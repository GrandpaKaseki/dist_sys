import time
import pandas as pd
import requests  # needs to get ethernet info
import psutil  # needs to get cpu info
from threading import Thread


class USDTrAcKeR:
    """This class collect info about usd→rub course from https://www.cbr-xml-daily.ru/daily_json.js."""

    @staticmethod
    def __get_usd_price() -> dict:
        """requests info from url."""
        return requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    def __init__(self) -> None:
        # this parameter needs to create column with this name in csv file.
        self.column_name = 'usd, rub'

        self.curr_usd = self.__get_usd_price()['Valute']['USD']['Value']
        # needs to stop collecting.
        self.collect = True
        # contains usd val.
        self.data_list = []
        # contains time val.
        self.time_list = []

    def start_collect(self) -> None:
        """Star a cycle, which sends requests to url then parse data, finally save it into list."""
        while self.collect:
            usd = self.__get_usd_price()['Valute']['USD']['Value']
            self.time_list.append(f"{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}")
            self.data_list.append(usd)
            print("get usd")
            # set new value if it changes.
            if usd != self.curr_usd:
                self.curr_usd = usd
            time.sleep(60)  # sleep shouldn't be less, then 25 seconds.

    def get_current_state(self) -> float:
        return self.curr_usd

    def clean_up(self) -> None:
        self.curr_usd = None

    def stop_collect(self, table: pd.DataFrame, column_name: str) -> None:
        """stops cycle from start_collect, then saves lists into pandas dataframe."""
        self.collect = False
        table['Time'] = self.time_list
        table[column_name] = self.data_list


class CPUTrAcKeR:
    """This class collect info about cpu percentage course with psutil framework."""

    def __init__(self) -> None:
        # this parameter needs to create column with this name in csv file.
        self.column_name = 'cpu, %'

        self.curr_percent = psutil.cpu_percent(interval=None, percpu=False)
        # needs to stop collecting.
        self.collect = True
        # contains cpu percentage val.
        self.data_list = []

    def start_collect(self) -> None:
        """Star a cycle, which get cpu percentage, finally save it into list."""
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

    def stop_collect(self, table: pd.DataFrame, column_name: str) -> None:
        """stops cycle from start_collect, then saves list into pandas dataframe."""
        self.collect = False
        table[column_name] = self.data_list


class BiTcOiNTrAcKeR:
    """This class collect info about bitcoin→usd course from https://blockchain.info/ru/ticker."""

    @staticmethod
    def __get_bit_price() -> float:
        """requests info from url."""
        response = requests.get('https://blockchain.info/ru/ticker').json()
        return float(response["USD"]["last"])

    def __init__(self) -> None:
        # this parameter needs to create column with this name in csv file.
        self.column_name = 'bitcoin, usd'

        self.curr_price = self.__get_bit_price()
        # needs to stop collecting.
        self.collect = True
        # contains bitcoin val.
        self.data_list = []

    def start_collect(self) -> None:
        """Star a cycle, which sends requests to url then parse data, finally save it into list."""
        while self.collect:
            price = self.__get_bit_price()
            self.data_list.append(price)
            print("get bit")
            # set new value if it changes.
            if price != self.curr_price:
                self.curr_price = price
            time.sleep(60)  # sleep shouldn't be less, then 25 seconds.

    def get_current_state(self) -> float:
        return self.curr_price

    def clean_up(self) -> None:
        self.curr_price = None

    def stop_collect(self, table: pd.DataFrame, column_name: str) -> None:
        """stops cycle from function start_collect, then saves lists into pandas dataframe."""
        self.collect = False
        table[column_name] = self.data_list


def start_or_join_thread(start: bool, thread_arr: list):
    if start:
        for thread in thread_arr:
            thread.start()
    else:
        for thread in thread_arr:
            thread.join()


def main() -> None:
    data_table = pd.DataFrame()
    usd = USDTrAcKeR()
    cpu = CPUTrAcKeR()
    bit = BiTcOiNTrAcKeR()
    class_arr = [usd, cpu, bit]
    thread_start = []
    thread_stop = []

    for class_ in class_arr:
        thread_start.append(Thread(target=class_.start_collect, args=(), daemon=True))
        thread_stop.append(Thread(target=class_.stop_collect, args=(data_table, class_.column_name), daemon=True))

    # start collecting.
    print("start collecting")
    start_or_join_thread(start=True, thread_arr=thread_start)

    work_time_sec = 20 * 60  # how long will we collect (in seconds).
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
    # stopping our collecting cycles and saving result.
    start_or_join_thread(start=True, thread_arr=thread_stop)

    start_or_join_thread(start=False, thread_arr=thread_stop)

    start_or_join_thread(start=False, thread_arr=thread_start)

    print("stop collecting")
    # print(data_table)
    # save result into csv-file.
    data_table.to_csv("thread_table.csv", sep=';', index=False)


if __name__ == "__main__":
    main()
