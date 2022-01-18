import queue
import threading
from appium import webdriver
from single_app_emulator_downloader import SingleAppEmulatorDownloader
import mysql.connector

MAX_THREAD = 3
download_queue = queue.Queue()
device_ids = ["emulator-5554", "emulator-5558", "emulator-5556"]
appium_ports = ["4723", "4724", "4725"]


class DownloadBatchDownloader:

    def __init__(self):
        self.threads = []
        self.base_app_ids = []
        self.conn = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
        self.prepare()

    def worker(self, device_id, appium_port):
        global download_queue
        driver = webdriver.Remote("http://localhost:{}/wd/hub".format(appium_port),
                                  self.init_appium(device_id, appium_port))
        while not download_queue.empty():
            app_id = download_queue.get()
            SingleAppEmulatorDownloader(device_id, app_id, driver, self.base_app_ids)
            # driver.find_element().
            download_queue.task_done()

    def init_appium(self, device_id, appium_port):
        desired_caps = {}
        desired_caps['platformName'] = "Android"
        desired_caps['platformVersion'] = "11.0"
        desired_caps['deviceName'] = device_id
        desired_caps['udid'] = device_id
        desired_caps['systemPort'] = int(appium_port) + 4 * MAX_THREAD - 1
        desired_caps['autoGrantPermissions'] = True
        desired_caps['automationName'] = "UiAutomator2"
        desired_caps['appPackage'] = "com.android.vending"
        desired_caps['appActivity'] = "com.google.android.finsky.activities.MainActivity"
        desired_caps['noReset'] = False
        desired_caps['unicodeKeyboard'] = True
        desired_caps['resetKeyboard'] = True
        desired_caps['newCommandTimeout'] = 400000
        return desired_caps

    def prepare(self):
        cur = self.conn.cursor()
        cur.execute("SELECT app_id FROM xapk.play_download WHERE status = 0 ORDER BY id")
        targets = cur.fetchall()
        for app_id in targets:
            download_queue.put(app_id[0])
        cur.close()
        with open("base_app_id", "r") as f:
            for app_id in f.readlines():
                self.base_app_ids.append(app_id.strip().replace("package:", ""))

        # set max thread and start each thread
        for i in range(MAX_THREAD):
            thread = threading.Thread(target=self.worker, args=(device_ids[i], appium_ports[i],))
            thread.start()
            self.threads.append(thread)

        for thread in self.threads:
            thread.join()


if __name__ == '__main__':
    DownloadBatchDownloader()
