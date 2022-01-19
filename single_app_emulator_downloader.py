from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException, \
    StaleElementReferenceException
import mysql.connector
from selenium.webdriver.chrome.webdriver import Options
import time
import os


class SingleAppEmulatorDownloader:
    def __init__(self, device_id, device_name, app_id, driver, base_app_ids):
        self.device_id = device_id
        self.device_name = device_name
        self.app_id = app_id
        self.MAX_WAIT = 50
        self.conn = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
        self.driver = driver
        self.base_app_ids = base_app_ids
        self.flag = True
        self.download()

    def download(self):
        self.check_emulator()
        self.uninstall_app()
        app_name = self.get_app_name(self.app_id)
        if self.flag:
            self.start_download(app_name)

            if self.flag:
                self.download_analysis()
            else:
                print("not find app skip")

    def check_emulator(self):
        # 如果模拟器未响应就重启模拟器
        if len(self.driver.find_elements(By.ID, "android:id/parentPanel")) > 0:
            os.popen("adb -s {} emu kill".format(self.device_id))

            os.popen("source ~/.bash_profile && emulator -avd {} -no-snapshot-load".format(self.device_name))

            while True:
                res = os.popen("adb -s {} shell getprop dev.bootcomplete".format(self.device_id)).readlines()
                if "1\n" in res:
                    break
                else:
                    time.sleep(1)

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
        # 根据app名字搜索
        self.search(app_name)

        if not self.flag:
            # 如果搜索失败返回
            return
        # 根据搜索结果下载匹配的app
        search_targets = self.get_search_result()

        if self.flag:
            find_result = self.get_matched_result(search_targets, app_name)
            if self.flag:
                if find_result:
                    # 如果找到了匹配的app
                    self.download_matched()
                else:
                    # 如果没有找到，若有推荐就下载推荐的app
                    self.download_recommend()
                # 如果有请求权限的按钮就点击
                self.click_accept_button()

    def download_analysis(self):
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

    def search(self, app_name):
        try:
            self.start_activity()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//android.widget.FrameLayout[@content-desc=\"Show navigation drawer\"]/.."))).click()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "android.widget.EditText"))).send_keys(app_name)

            self.driver.press_keycode(66)
        except Exception:
            self.update_status(4)
            self.flag = False

    def click_accept_button(self):
        try:
            time.sleep(2)
            if len(self.driver.find_elements(By.CLASS_NAME, "android.widget.Button")) == 1 and len(
                    self.driver.find_elements(
                        By.XPATH, "*//android.view.ViewGroup/android.widget.Button")) < 1:
                self.driver.find_element(By.CLASS_NAME, "android.widget.Button").click()
        except Exception:
            self.flag = False

    def get_search_result(self):
        try:
            search_targets = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
                (By.ID, "com.android.vending:id/nested_parent_recycler_view")))
            return search_targets
        except Exception:
            self.update_status(4)
            self.flag = False

    def download_matched(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "android.widget.Button"))).click()
            self.update_status(1)
        except Exception:
            self.flag = False
            self.update_status(4)

    def download_recommend(self):
        try:
            download_button = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "android.widget.Button")))
            download_button.click()
            self.update_status(1)
            self.flag = True
        except Exception:
            self.update_status(3)
            self.flag = False

    def get_matched_result(self, search_targets, app_name):
        for search_target in search_targets.find_elements(By.XPATH, "//*"):
            try:
                search_detail = search_target.find_element(By.XPATH, "//*[@content-desc]")
                for _ in str(search_detail.get_attribute("content-desc")).split("\n"):
                    print(_)
                    if app_name.lower() == _.replace("App: ", "").strip().lower():
                        search_detail.click()
                        return True
            except NoSuchElementException or StaleElementReferenceException:
                print("", end="")
            except Exception:
                self.flag = False
                self.update_status(5)
        return False

    def analysis(self):
        res = os.popen("adb -s {} shell pm list packages".format(self.device_id)).readlines()

        if len(res) > len(self.base_app_ids):
            if "package:" + self.app_id + "\n" in res:
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
        else:
            return False
        print("-------")
        return True

    def uninstall_app(self):
        res = os.popen("adb -s {} shell pm list packages".format(self.device_id)).readlines()
        for app_id in res:
            app_id = app_id.strip().replace("package:", "")
            if app_id not in self.base_app_ids:
                os.popen("adb -s {} uninstall {}".format(self.device_id, app_id)).readlines()

    def is_extract_finish(self, size):
        count = len(os.listdir("/Volumes/Data/apk_pure/play_xapk/" + self.app_id))
        if count != size:
            return False
        return True

    def update_status(self, status):
        cur = self.conn.cursor()
        cur.execute("UPDATE xapk.play_download SET status=%s WHERE app_id=%s", (status, self.app_id,))
        self.conn.commit()
        cur.close()

    def update_bundle(self, is_bundle):
        cur = self.conn.cursor()
        cur.execute("UPDATE xapk.play_download SET bundle=%s WHERE app_id=%s", (is_bundle, self.app_id,))
        self.conn.commit()
        cur.close()

    def get_app_name(self, app_id):
        # 根据app_id寻找app的名字
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get("https://play.google.com/store/apps/details?id={}".format(app_id))
        except Exception:
            self.update_status(4)
            self.flag = False

        try:
            return driver.find_element(By.CSS_SELECTOR, "h1 > span").text.strip()
        except NoSuchElementException:
            self.update_status(5)
            self.flag = False
            return ""
