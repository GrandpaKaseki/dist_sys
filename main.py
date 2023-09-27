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


def main() -> None:
    data_table = pd.DataFrame()
    usd = USDTrAcKeR()
    cpu = CPUTrAcKeR()
    bit = BiTcOiNTrAcKeR()

    # create collecting cycle threads.
    thread_usd = Thread(target=usd.start_collect, args=(), daemon=True)
    thread_cpu = Thread(target=cpu.start_collect, args=(), daemon=True)
    thread_bit = Thread(target=bit.start_collect, args=(), daemon=True)

    # create stop collecting threads.
    thread_stop_usd = Thread(target=usd.stop_collect, args=(data_table, 'usd, rub'), daemon=True)
    thread_stop_cpu = Thread(target=cpu.stop_collect, args=(data_table, 'cpu, %'), daemon=True)
    thread_stop_bit = Thread(target=bit.stop_collect, args=(data_table, 'bitcoin, usd'), daemon=True)

    # start collecting.
    print("start collecting")
    thread_usd.start()
    thread_cpu.start()
    thread_bit.start()

    work_time_sec = 20 * 60  # how long will we collect (in seconds).
    time_count = time.time()  # timer.
    while True:
        # checking if every thread is alive.
        if not (thread_bit.is_alive() and thread_cpu.is_alive() and thread_usd.is_alive()):
            print("Error: one of the thread died")
            break
        # check time to stop.
        if time.time() - time_count > work_time_sec:
            break
    # stopping our collecting cycles and saving result.
    thread_stop_usd.start()
    thread_stop_cpu.start()
    thread_stop_bit.start()

    thread_stop_usd.join()
    thread_stop_cpu.join()
    thread_stop_bit.join()

    thread_usd.join()
    thread_cpu.join()
    thread_bit.join()

    print("stop collecting")
    # print(data_table)
    # save result into csv-file.
    data_table.to_csv("thread_table.csv", sep=';', index=False)


if __name__ == "__main__":
    main()
