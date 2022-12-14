from sys import argv

from models import Config, CF, Point, Status

commands = [i for i in dir(CF) if not i.startswith('__')]


def help():
    for i in commands:
        val = Config.get(Config.key == i).value
        comment = ''
        if i == CF.QUIT:
            comment = f'({val}); 1 - stop boss'
        elif i == CF.delay:
            comment = f'({val}); delay between iterations in seconds'
        elif i == CF.free_amd:
            comment = f'({val}); not use this amount of nodes of amd'
        elif i == CF.free_intel:
            comment = f'({val}); not use this amount of nodes of intel'
        elif i == CF.nodes_per_calc:
            comment = f'({val}); nodes for one job'

        print('\033[96m', f"{i:>15}", '\033[94m', comment, '\033[0m')


if __name__ == '__main__':
    if len(argv) > 1:
        comm = argv[1]
        if comm == 'set':
            key = argv[2]
            value = int(argv[3])
            if key in commands:
                cf = Config.get(Config.key == key)
                cf.value = value
                cf.save()
                print('set '
                      f'\033[1m\033[92m{key}\033[0m'
                      ' to '
                      f'\033[1m\033[95m{value}\033[0m', sep='')
        if comm == 'help':
            help()
        if comm == 'points':
            spec = argv[2]
            if spec == 'all':
                points = Point.select()
            if spec == 'pending':
                points = Point.select().where(
                    Point.status == Status.PENDING)
            if spec == 'calculating':
                points = Point.select().where(
                    Point.status == Status.CALCULATING)
            if spec == 'success':
                points = Point.select().where(
                    Point.status == Status.SUCCESS)
            print("LEFT", "RIGHT", "STATUS", sep='\t|\t', end='\n\n')
            for i in points:
                print(i.l, i.r, "\033[96mPENDING\033[0m" if i.status == Status.PENDING else
                      "\033[93mCALCULATING\033[0m" if i.status == Status.CALCULATING else
                      "\033[92mSUCCESS\033[0m" if i.status == Status.SUCCESS else "", sep='\t|\t')

    else:
        help()
