import time

import pandas as pd
import requests
import psutil
from threading import Thread


class USDTrAcKeR:

    def __get_usd_price(self):
        return requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    def __init__(self):
        self.curr_usd = self.__get_usd_price()['Valute']['USD']['Value']
        self.collect = True
        self.data_list = []
        self.time_list = []

    def start_collect(self):
        while self.collect:
            usd = self.__get_usd_price()['Valute']['USD']['Value']
            self.time_list.append(f"{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}")
            self.data_list.append(usd)
            print("get usd")
            if usd != self.curr_usd:
                self.curr_usd = usd
            time.sleep(10)

    def get_current_state(self):
        return self.curr_usd

    def clean_up(self):
        self.curr_usd = None

    def stop_collect(self, table: pd.DataFrame, column_name: str):
        self.collect = False
        table['Time'] = self.time_list
        table[column_name] = self.data_list


class CPUTrAcKeR:

    def __init__(self):
        self.curr_percent = psutil.cpu_percent(interval=None, percpu=False)
        self.collect = True
        self.data_list = []

    def start_collect(self):
        while self.collect:
            percent = psutil.cpu_percent(interval=None, percpu=False)
            self.data_list.append(percent)
            print("get cpu")
            if percent != self.curr_percent:
                self.curr_percent = percent
            time.sleep(10)

    def get_current_state(self):
        return self.curr_percent

    def clean_up(self):
        self.curr_percent = None

    def stop_collect(self, table: pd.DataFrame, column_name: str):
        self.collect = False
        table[column_name] = self.data_list


class BiTcOiNTrAcKeR:

    def __get_bit_price(self):
        response = requests.get('https://blockchain.info/ru/ticker').json()
        return float(response["USD"]["last"])

    def __init__(self):
        self.curr_price = self.__get_bit_price()
        self.collect = True
        self.data_list = []

    def start_collect(self):
        while self.collect:
            price = self.__get_bit_price()
            self.data_list.append(price)
            print("get bit")
            if price != self.curr_price:
                self.curr_price = price
            time.sleep(10)

    def get_current_state(self):
        return self.curr_price

    def clean_up(self):
        self.curr_price = None

    def stop_collect(self, table: pd.DataFrame, column_name: str):
        self.collect = False
        table[column_name] = self.data_list


def main():
    df = pd.DataFrame()
    #df.columns = ['time', 'usd, rub', 'cpu, %', 'bitcoin, usd']
    usd = USDTrAcKeR()
    cpu = CPUTrAcKeR()
    bit = BiTcOiNTrAcKeR()

    thread_usd = Thread(target=usd.start_collect, args=(), daemon=True)
    thread_cpu = Thread(target=cpu.start_collect, args=(), daemon=True)
    thread_bit = Thread(target=bit.start_collect, args=(), daemon=True)

    thread_stop_usd = Thread(target=usd.stop_collect, args=(df, 'usd, rub'), daemon=True)
    thread_stop_cpu = Thread(target=cpu.stop_collect, args=(df, 'cpu, %'), daemon=True)
    thread_stop_bit = Thread(target=cpu.stop_collect, args=(df, 'bitcoin, usd'), daemon=True)

    thread_usd.start()
    thread_cpu.start()
    thread_bit.start()

    work_time_sec = 180
    time_count = time.time()
    while True:
        print(thread_usd.run())
        print(thread_cpu.run())
        print(thread_bit.run())
        if not (thread_bit.run() or thread_cpu.run() or thread_usd.run()):
            print("Один из потоков умер")
            break
        if time.time() - time_count > work_time_sec:
            break

    thread_stop_usd.start()
    thread_stop_cpu.start()
    thread_stop_bit.start()

    thread_stop_usd.join()
    thread_stop_cpu.join()
    thread_stop_bit.join()

    thread_usd.join()
    thread_cpu.join()
    thread_bit.join()

    print(df)


if __name__ == "__main__":
    main()
