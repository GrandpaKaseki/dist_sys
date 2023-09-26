import time
import requests
import psutil
from threading import Thread


class USDTrAcKeR:

    def __get_usd_price(self):
        return requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    def __init__(self):
        self.curr_usd = self.__get_usd_price()['Valute']['USD']['Value']
        self.collect = True

    def start_collect(self):
        while self.collect:
            self.curr_usd = self.__get_usd_price()['Valute']['USD']['Value']
            # запись в табличку
            time.sleep(10)

    def get_current_state(self):
        return self.curr_usd

    def clean_up(self):
        self.curr_usd = None

    def stop_collect(self):
        self.collect = False


class CPUTrAcKeR:

    def __init__(self):
        self.curr_percent = psutil.cpu_percent(interval=None, percpu=False)
        self.collect = True

    def start_collect(self):
        while self.collect:
            self.curr_percent = psutil.cpu_percent(interval=None, percpu=False)
            # запись в табличку
            time.sleep(10)

    def get_current_state(self):
        return self.curr_percent

    def clean_up(self):
        self.curr_percent = None

    def stop_collect(self):
        self.collect = False


class BiTcOiNTrAcKeR:

    def __get_bit_price(self):
        response = requests.get('https://blockchain.info/ru/ticker').json()
        return float(response["USD"]["last"])

    def __init__(self):
        self.curr_price = self.__get_bit_price()
        self.collect = True

    def start_collect(self):
        while self.collect:
            self.curr_price = self.__get_bit_price()
            # запись в табличку
            time.sleep(10)

    def get_current_state(self):
        return self.curr_price

    def clean_up(self):
        self.curr_price = None

    def stop_collect(self):
        self.collect = False

def main():
    usd = USDTrAcKeR
    cpu = CPUTrAcKeR
    bit = BiTcOiNTrAcKeR
    thread_usd = Thread(target=usd.start_collect,args=(),daemon=True)
    thread_cpu = Thread(target=cpu.start_collect,args=(),daemon=True)
    thread_bit = Thread(target=bit.start_collect,args=(),daemon=True)
    thread_stop_usd = Thread(target=usd.stop_collect,args=(),daemon=True)
    thread_stop_cpu = Thread(target=cpu.stop_collect,args=(),daemon=True)
    thread_stop_bit = Thread(target=cpu.stop_collect,args=(),daemon=True)