import sys
from typing import List
from colorama import Fore, Style, Back
from peewee import DoesNotExist
from models import Config, CF, Point, Status


settings = [i for i in dir(CF) if not i.startswith('__')]


def print_success(data):
    print(f'{Fore.GREEN}✔{Fore.RESET}', data)


def print_failure(data):
    print(f'{Fore.RED}✖{Fore.RESET}', data)


def set_param(key, value):
    try:
        param = Config.get(Config.key == key)
    except DoesNotExist:
        print_failure(
            f'Parameter {Back.BLACK}{Style.BRIGHT}{key}{Style.RESET_ALL} does not exist')
        return
    param.value = value
    param.save()
    print_success(f"Set {key} to {value}")


def help_handler(xs):
    for i in settings:
        val = Config.get(Config.key == i).value
        comment = ''
        if i == CF.QUIT:
            comment = '1 - stop boss'
        elif i == CF.delay:
            comment = 'delay between iterations in seconds'
        elif i == CF.free_amd:
            comment = 'not use this amount of nodes of amd'
        elif i == CF.free_intel:
            comment = 'not use this amount of nodes of intel'
        elif i == CF.nodes_per_calc:
            comment = 'nodes for one job'
        elif i == CF.query_amd:
            comment = 'jobs in query on amd'
        elif i == CF.query_intel:
            comment = 'jobs in query on intel'

        print(f"{Fore.CYAN}{i:<15}{Fore.GREEN}{val:5}{Fore.WHITE} {comment}{Style.RESET_ALL}")


def set_handler(xs: List[str]):
    assert len(xs) == 2
    key, value = xs
    assert value.isnumeric()
    set_param(key, int(value))


def mode_handler(xs):
    assert len(xs) == 1
    mode = xs[0]
    if mode == 'kind':
        cfg = {
            CF.free_amd: 4,
            CF.free_intel: 4,
            CF.query_amd: 0,
            CF.query_intel: 0
        }
    elif mode == 'angry':
        cfg = {
            CF.free_amd: 0,
            CF.free_intel: 0,
            CF.query_amd: 4,
            CF.query_intel: 4
        }
    elif mode == 'normal':
        cfg = {
            CF.free_amd: 2,
            CF.free_intel: 2,
            CF.query_amd: 0,
            CF.query_intel: 0
        }
    else:
        print_failure(
            f'Mode {Back.BLACK}{Style.BRIGHT}{mode}{Style.RESET_ALL} does not exist')
        return
    print_success(f"Set mode to {Style.BRIGHT}{Back.BLACK}{mode}{Style.RESET_ALL}")
    for k, v in cfg.items():
        set_param(k, v)

def process_status(status: int) -> str:
    if status == Status.PENDING:
        return "PENDING"
    if status == Status.CALCULATING:
        return f"{Fore.YELLOW}CALCULATING{Fore.RESET}"
    if status == Status.SUCCESS:
        return f"{Fore.GREEN}SUCCESS{Fore.RESET}"
    return ""

def points_handler(xs):
    assert len(xs) == 1
    mode = xs[0]
    if mode == 'all':
        points = Point.select()
    elif mode == 'pending':
        points = Point.select().where(
            Point.status == Status.PENDING)
    elif mode == 'calculating':
        points = Point.select().where(
            Point.status == Status.CALCULATING)
    elif mode == 'success':
        points = Point.select().where(
            Point.status == Status.SUCCESS)
    else:
        print_failure(f'Incorrect mode: {Back.BLACK}{Style.BRIGHT}{mode}{Style.RESET_ALL}')
        return
    print(f'{"LEFT":10}| {"RIGHT":10}| {"STATUS":15}')
    print('-'*30)
    if not points:
        print('No points')
    for i in points:
        print(f'{i.l:<10}| {i.r:<10}| {process_status(i.status):<15}')


def command_handler():
    argv = sys.argv[1:]
    if len(argv) == 0:
        return help_handler([])
    comm = argv[0]
    if comm == 'help':
        return help_handler(argv[1:])
    if comm == 'set':
        return set_handler(argv[1:])
    if comm == 'mode':
        return mode_handler(argv[1:])
    if comm == 'points':
        return points_handler(argv[1:])
    return help_handler([])


if __name__ == '__main__':
    command_handler()
