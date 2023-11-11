import time
import pandas as pd
import requests  # needs to get ethernet info
import psutil  # needs to get cpu info
from threading import Thread
from datetime import datetime

USD_LINK = 'https://www.cbr-xml-daily.ru/daily_json.js'
BITCOIN_LINK = 'https://blockchain.info/ru/ticker'


class USDTrAcKeR:
    """This class collect info about usd→rub course from https://www.cbr-xml-daily.ru/daily_json.js."""

    @staticmethod
    def __get_usd_price() -> dict | None:
        """requests info from url."""
        response = requests.get(USD_LINK)
        if response.status_code == 200:
            return response.json()

    def __init__(self) -> None:
        # this parameter needs to create the column with this name in csv file.
        self.column_name = 'usd, rub'

        self.curr_usd = None
        # needs to stop collecting.
        self.collect = False
        # contains usd val.
        self.data_list = []
        # contains time val.
        self.time_list = []

    def start_collect(self) -> None:
        """Star a cycle, which sends requests to url then parse data, finally save it into list."""
        self.collect = True
        while self.collect:
            usd = self.__get_usd_price()
            if usd is not None:
                usd = usd['Valute']['USD']['Value']
            now = datetime.now()
            self.time_list.append(now.strftime("%H:%M:%S"))
            self.data_list.append(usd)
            print("get usd")
            # set new value if it changes.
            if usd != self.curr_usd:
                self.curr_usd = usd
            time.sleep(60)  # sleep shouldn't be less, then 25 seconds.

    def get_current_state(self) -> float | None:
        return self.curr_usd

    def clean_up(self) -> None:
        self.curr_usd = None

    def stop_collect(self) -> None:
        """stops cycle from start_collect method."""
        self.collect = False

    def save_data(self, table: pd.DataFrame, column_name: str) -> None:
        """saves lists into pandas dataframe."""
        table['Time'] = self.time_list
        table[column_name] = self.data_list


class CPUTrAcKeR:
    """This class collect info about cpu percentage course with psutil framework."""

    def __init__(self) -> None:
        # this parameter needs to create the column with this name in csv file.
        self.column_name = 'cpu, %'

        self.curr_percent = None
        # needs to stop collecting.
        self.collect = False
        # contains cpu percentage val.
        self.data_list = []

    def start_collect(self) -> None:
        """Star a cycle, which get cpu percentage, finally save it into list."""
        self.collect = True
        while self.collect:
            percent = psutil.cpu_percent(interval=None, percpu=False)
            self.data_list.append(percent)
            print("get cpu")
            # set new value if it changes.
            if percent != self.curr_percent:
                self.curr_percent = percent
            time.sleep(60)  # sleep shouldn't be less, then 25 seconds.

    def get_current_state(self) -> float:
        return self.curr_percent

    def clean_up(self) -> None:
        self.curr_percent = None

    def stop_collect(self) -> None:
        """stops cycle from start_collect method"""
        self.collect = False

    def save_data(self, table: pd.DataFrame, column_name: str) -> None:
        """saves list into pandas dataframe."""
        table[column_name] = self.data_list


class BiTcOiNTrAcKeR:
    """This class collect info about bitcoin→usd course from https://blockchain.info/ru/ticker."""

    @staticmethod
    def __get_bit_price() -> dict | None:
        """requests info from url."""
        response = requests.get(BITCOIN_LINK)
        if response.status_code == 200:
            return response.json()

    def __init__(self) -> None:
        # this parameter needs to create the column with this name in csv file.
        self.column_name = 'bitcoin, usd'

        self.curr_price = self.__get_bit_price()
        # needs to stop collecting.
        self.collect = False
        # contains bitcoin val.
        self.data_list = []

    def start_collect(self) -> None:
        """Star a cycle, which sends requests to url then parse data, finally save it into list."""
        self.collect = True
        while self.collect:
            price = self.__get_bit_price()
            if price is not None:
                price = float(price["USD"]["last"])
            self.data_list.append(price)
            print("get bit")
            # set new value if it changes.
            if price != self.curr_price:
                self.curr_price = price
            time.sleep(60)  # sleep shouldn't be less, then 25 seconds.

    def get_current_state(self) -> float | None:
        return self.curr_price

    def clean_up(self) -> None:
        self.curr_price = None

    def stop_collect(self) -> None:
        """stops cycle from start_collect method"""
        self.collect = False

    def save_data(self, table: pd.DataFrame, column_name: str) -> None:
        """saves list into pandas dataframe."""
        table[column_name] = self.data_list


def start_or_join_thread(start: bool, thread_arr: list):
    if start:
        for thread in thread_arr:
            thread.start()
    else:
        for thread in thread_arr:
            thread.join()


def main(work_time_minutes: float = 10) -> None:
    data_table = pd.DataFrame()
    usd = USDTrAcKeR()
    cpu = CPUTrAcKeR()
    bit = BiTcOiNTrAcKeR()
    class_arr = [usd, cpu, bit]
    thread_start = []
    thread_save = []
    thread_stop = []

    for class_ in class_arr:
        thread_start.append(Thread(target=class_.start_collect, args=(), daemon=True))
        thread_stop.append(Thread(target=class_.stop_collect(), args=(), daemon=True))
        thread_save.append(Thread(target=class_.save_data, args=(data_table, class_.column_name), daemon=True))

    # start collecting.
    print("start collecting")
    start_or_join_thread(start=True, thread_arr=thread_start)

    work_time_sec = work_time_minutes * 60  # how long will we collect (in seconds).
    time_count = time.time()  # timer.
    while True:
        # checking if every thread is alive.
        for collect_thread in thread_start:
            if not collect_thread.is_alive():
                print("Error: one of the thread died")
                break
        # check time to stop.
        if time.time() - time_count > work_time_sec:
            break
    # stopping our collecting cycles.
    start_or_join_thread(start=True, thread_arr=thread_stop)

    start_or_join_thread(start=False, thread_arr=thread_stop)

    start_or_join_thread(start=False, thread_arr=thread_start)

    # saving result.
    start_or_join_thread(start=True, thread_arr=thread_save)
    start_or_join_thread(start=False, thread_arr=thread_save)

    print("stop collecting")
    # print(data_table)
    # save result into csv-file.
    data_table.to_csv("thread_table.csv", sep=';', index=False)


if __name__ == "__main__":
    main(5)
