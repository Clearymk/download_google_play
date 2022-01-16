import csv
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import ssl
import mysql.connector
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from mysql.connector.errors import IntegrityError
from listener import Listener

con = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
cur = con.cursor()
ssl._create_default_https_context = ssl._create_unverified_context


class DownloadApp:
    def __init__(self):
        self.listener = Listener()

    def download(self):
        driver = uc.Chrome()

        GOOGLE_LOGIN_PATH = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow"
        GOOGLE_ID = "holpokarwdhholikarec466@gmail.com"
        GOOGLE_PW = "downloadPlay123"

        driver.get(GOOGLE_LOGIN_PATH)
        login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'identifierId')))
        login.send_keys(GOOGLE_ID)

        time.sleep(1)
        driver.find_element(By.ID, 'identifierNext').click()

        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password')))
        password = password.find_element_by_tag_name('input')
        time.sleep(1)
        password.send_keys(GOOGLE_PW)

        driver.find_element(By.ID, 'passwordNext').click()
        flag = True

        count = 0
        with open("../apk_pure_info.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                count += 1
                print("当前处理到第" + str(count) + "行")
                self.row = count

                if count < 0:
                    continue

                if row[4].strip() == 1:
                    break

                driver.switch_to.default_content()
                driver.get("https://play.google.com/store/apps/details?id={}".format(row[0].strip()))

                if flag:
                    driver.refresh()
                    flag = False

                try:
                    download_button = driver.find_element(By.CSS_SELECTOR,
                                                          "button[class=\" LkLjZd ScJHi HPiPcc IfEcue  \"]")
                    # download_button = driver.find_element(By.CSS_SELECTOR,
                    #     "button[class=\"VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc MjT6xe sOCCfd brKGGd BhQfub  zwjsl\"]")
                except NoSuchElementException:
                    print(row[0] + "app not find skip")
                    print("---------")
                    continue

                download_button.click()

                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[width=\"100%\"]")))

                try:
                    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe[width=\"100%\"]"))
                except TimeoutException:
                    print()

                try:
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable(
                            driver.find_elements(By.CSS_SELECTOR,
                                                 "button[class=\"LkLjZd ScJHi IfEcue HPiPcc KXT7c  \"")[1]))
                    driver.find_elements(By.CSS_SELECTOR, "button[class=\"LkLjZd ScJHi IfEcue HPiPcc KXT7c  \"")[
                        1].click()
                    driver.switch_to.default_content()
                    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password')))
                    password = password.find_element(By.TAG_NAME, 'input')
                    time.sleep(1)
                    password.send_keys(GOOGLE_PW)

                    driver.find_element(By.ID, 'passwordNext').click()

                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[width=\"100%\"]")))
                    except TimeoutException:
                        continue

                    try:
                        cur.execute("INSERT INTO app(app_id) VALUES (%s)", (row[0],))
                        con.commit()
                    except IntegrityError:
                        print()

                    print("install", row[0])
                except IndexError:
                    continue
                print("-----")
        driver.quit()
