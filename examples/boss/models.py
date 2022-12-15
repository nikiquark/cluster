from peewee import SqliteDatabase, Model, DoubleField, IntegerField, CharField
DB_NAME = 'db.sqlite'

db = SqliteDatabase(DB_NAME)


class Point(Model):
    l = DoubleField()
    r = DoubleField()
    status = IntegerField()
    energy = DoubleField(null=True, default=None)

    class Meta:
        database = db


class Status:
    PENDING = 1
    CALCULATING = 2
    SUCCESS = 3


class Config(Model):
    key = CharField()
    value = IntegerField()

    class Meta:
        database = db


class CF:
    QUIT = 'QUIT'
    nodes_per_calc = 'nodes_per_calc'
    delay = 'delay'
    free_amd = 'free_amd'
    free_intel = 'free_intel'
    query_amd = 'query_amd'
    query_intel = 'query_intel'


if __name__ == "__main__":
    try:
        import os
        os.remove(f'{DB_NAME}')
    except FileNotFoundError:
        pass
    db.connect()
    db.create_tables([Point, Config])

    Config.create(key=CF.QUIT, value=0)
    Config.create(key=CF.nodes_per_calc, value=4)
    Config.create(key=CF.delay, value=300)
    Config.create(key=CF.free_amd, value=2)
    Config.create(key=CF.free_intel, value=2)
    Config.create(key=CF.query_intel, value=0)
    Config.create(key=CF.query_amd, value=0)



