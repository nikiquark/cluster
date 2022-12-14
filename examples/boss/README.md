# Boss Example
Пример босса с использованием новой библиотеки  
Состоит из четырёх файлов:
- **models.py** - создаёт Базу Данных (БД) и загружает в неё стандартный конфиг
- **populate.py** - заполняет БД точками, которые нужно посчитать
- **controller.py** - контролирует config и выводит текущий прогресс
- **main.py** - основной цикл босса

## Запуск
Для первичного запуска необходимо сначала запустить models.py, чтобы создать БД. Затем можно запускать босса.  
Заполнить БД точками и настраивать конфиг можно в любой момент

```
python models.py 
python populate.py
python controller.py set delay 1200
python main.py
```

## Controller
Умеет выводить текущий статус и текущий конфиг

Для вывода текущего конфига
```
python controller.py
```
или
```
python controller.py help
```

Для изменения конфига необходимо вызвать ***set \<name> \<value>***, где *\<name>* любой параметр из конфига, а *\<value>* целое значение 
```
python controller.py set <name> <value>
```
Также можно посмотреть статус расчёта всех точек или выбранную группу (Это можно сделать и через бд, если умеете)
```
python controller.py points all
python controller.py points pending
python controller.py points calculating
python controller.py points success
```