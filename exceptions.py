import sys


class ConnectionError(Exception):
    def __init__(self):
        self.message = f'Ошибка в соединении к {self.result}: {self.status}!'

def CriticalException(Exception):
    return sys.exit()