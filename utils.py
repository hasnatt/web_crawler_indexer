import datetime


def time_print(*args):
    print(str(datetime.datetime.now().strftime("[%I:%M:%S %p] -")), *args)


def command_print(*args):
    print(">", *args)
