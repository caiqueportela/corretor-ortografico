from datetime import datetime
from pytz import timezone


class LogModel:

    @staticmethod
    def log(msg):
        now = datetime.now().astimezone(timezone('America/Sao_Paulo'))
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        print(f'[{dt_string}] {msg}')