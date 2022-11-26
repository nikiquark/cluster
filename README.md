# Cluster package

Пакет для упрощения работы с кластерами

Сейчас доступна работа только с Иркутским Кластером (Матросов). В будущем, возможно, добавлю ещё НГУ кластер.

Пакет может работать, как локально на кластере, так и удалённо на машине, имеющей ssh доступ к кластеру.
## Установка 

Todo

## Настройка SSH
Если вы не хотите копировать код на кластер, а работать запускать скрипт, использующий данный пакет, удалённо (у себя или на Уме). Если не хотите и будете запускать на кластере, то пропустите этот шаг. Необходимо настроить ssh config, чтобы можно было получить доступ к кластеру без пароля. 

Для этого необходими сгенерировать связку ssh ключей, добавить открытую часть на кластере в `~/.ssh/authorized_keys` и на локальной машине настроить `~/.ssh/config`. Если хотите запускать скрипт на компьютере, у которого нет доступа к кластеру, то нужно ещё `ProxyJump` добавить через сервер, у которого доступ есть.

Пример моего конфига (`~/.ssh/config`)
```
Host uma
  HostName <ip>
  User <username on uma>

Host matrosov
  HostName <ip>
  User <username on matrosov>
  ProxyJump uma
```
Имя указанное для кластера (у меня это `matrosov`) позже понадобиться.

После настройки можно проверить, что всё работает 
```
ssh matrosov 
```

## Использование

### Общая информация
Todo



### Старт
Так как сейчас доступен только матросов, то на его примере и покажу.

Для начала импортируем обёртку и создадим экземпляр. По умолчанию `ssh=True, ssh_name='matrosov'`. Можете поменять имя, которое указано в ssh конфиге или выключить ssh.
```python
from cluster import Matrosov

m = Matrosov()
```
Если хотите получить последнюю информацию о своих задачах и загруженности сегментов необходимо вызвать `update`. `__init__` сам вызывает `update`. Поэтому после создания дополнительно можно не вызывать.
```
m.update()
```
После создания или обновления `m` можем посмотреть на сегменты кластера `m.segments`. Для удобства доступ к сегментом можно делать по их имени.
```python
print(m.segments)
# [amd - 13/59, intel - 37/59]
print(m.intel)
# intel - 37/59
print(m.amd)
# amd - 13/59
m.amd.nodes_info
# dataclass SegmentStatus in cluster/matrosov/models.py
m.amd.cores_per_node
m.amd.jobs
# list of dataclasses JobStatus in cluster/matrosov/models.py
```

### Запуск задачи
Пример запуска lcode без аргументов  
`create_job` создаёт скрипт запуска в нужной папке  
`submit_job` вызывает `qsub.intel` или `qsub.amd`
```python
new_dir = 'gh_test'
m.execute(f'mkdir {new_dir}')

home_dir = m.run('pwd')

m.intel.create_job(f'{home_dir}/{new_dir}', 'without-argv', 2, '', '~/lcode2d')

m.intel.submit_job(f'{home_dir}/{new_dir}')
```

Пример `create_job` с аргументами
```python

m.intel.create_job(f'{home_dir}/{new_dir}', 'test', 4, './lcode.cfg ./plasma-zshape-profile.txt', '~/lcode2d')

m.intel.submit_job(f'{home_dir}/{new_dir}')
```

