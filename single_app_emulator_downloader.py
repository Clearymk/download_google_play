from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import Options
import time
import os


class SingleAppEmulatorDownloader:
    def __init__(self, device_id, app_id, conn, cursor, driver):
        self.device_id = device_id
        self.app_id = app_id
        self.MAX_WAIT = 50
        self.conn = conn
        self.driver = driver
        self.cursor = cursor
        self.download()

    def download(self):
        app_name = self.get_app_name(self.app_id)
        if app_name:
            if self.start_download(app_name):
                count = 0

                while count < self.MAX_WAIT:
                    res = self.analysis()
                    if res:
                        break
                    else:
                        time.sleep(5)
                    count += 1
                    print("wait count", count)

                try:
                    self.driver.start_activity("com.android.vending",
                                               "com.google.android.finsky.activities.MainActivity")
                except InvalidSessionIdException:
                    self.driver.refresh()
            else:
                print("not find app skip")

    def start_activity(self):
        flag = True

        while flag:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.FrameLayout[@content-desc=\"Show navigation drawer\"]/..")))
                flag = False
            except TimeoutException:
                self.driver.start_activity("com.android.vending", "com.google.android.finsky.activities.MainActivity")

    def start_download(self, app_name):
        print("download app name " + app_name)

        self.start_activity()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//android.widget.FrameLayout[@content-desc=\"Show navigation drawer\"]/.."))).click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "android.widget.EditText"))).send_keys(app_name)

        self.driver.press_keycode(66)

        flag = False

        try:
            search_targets = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
                (By.ID, "com.android.vending:id/nested_parent_recycler_view")))
        except TimeoutException:
            self.update_status(4)
            return False
        for search_target in search_targets.find_elements(By.XPATH, "//*"):
            try:
                try:
                    search_detail = search_target.find_element(By.CLASS_NAME, "android.view.View")
                    for _ in str(search_detail.get_attribute("content-desc")).split("\n"):
                        if app_name.lower() == _.replace("App: ", "").strip().lower():
                            search_detail.click()
                            flag = True
                            break
                except StaleElementReferenceException:
                    flag = False
            except NoSuchElementException:
                print()

            if flag:
                break

        if flag:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "android.widget.Button"))).click()
            self.update_status(1)
        else:
            try:
                download_button = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "android.widget.Button")))
                download_button.click()
                self.update_status(1)
            except TimeoutException or NoSuchElementException:
                self.update_status(3)
                return False

        return True

    def analysis(self):
        res = os.popen("adb -s {} shell pm list packages".format(self.device_id))
        flag = False

        if "package:" + self.app_id + "\n" in res:
            flag = True

        if flag:
            res = os.popen("adb -s {} shell pm path {}".format(self.device_id, self.app_id)).readlines()
            if len(res) == 1:
                print(res)
                self.update_bundle(2)
                print("one apk find uninstall it")
                os.popen("adb -s {} uninstall {}".format(self.device_id, self.app_id)).readlines()
            elif len(res) > 1:
                print(res)
                self.update_bundle(2)
                os.popen("mkdir /Volumes/Data/apk_pure/play_xapk/" + self.app_id).readlines()
                print("muti apk find extract it")
                for path in res:
                    path = path.split('package:')[1].strip()
                    print(os.popen("adb -s {} pull ".format(self.device_id)
                                   + path + " /Volumes/Data/apk_pure/play_xapk/" +
                                   self.app_id).readlines())

                os.popen("adb -s {} uninstall {}".format(self.device_id, self.app_id)).readlines()

        else:
            print("-------")
            return False

        print("-------")
        return True

    def is_extract_finish(self, size):
        count = len(os.listdir("/Volumes/Data/apk_pure/play_xapk/" + self.app_id))
        if count != size:
            return False
        return True

    def update_status(self, status):
        self.cursor.execute("UPDATE xapk.play_download SET status=%s WHERE app_id=%s", (status, self.app_id,))
        self.conn.commit()

    def update_bundle(self, is_bundle):
        self.cursor.execute("UPDATE xapk.play_download SET bundle=%s WHERE app_id=%s", (is_bundle, self.app_id,))
        self.conn.commit()

    def get_app_name(self, app_id):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://play.google.com/store/apps/details?id={}".format(app_id))
        try:
            return driver.find_element(By.CSS_SELECTOR, "h1 > span").text.strip()
        except NoSuchElementException:
            return False
