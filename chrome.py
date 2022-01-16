import undetected_chromedriver as uc
import ssl
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
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
    input()
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.webdriver import Options
#
# app_id = "com.capistudio.evapp"
# chrome_options = Options()
#
# chrome_options.add_argument("--headless")
#
# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://play.google.com/store/apps/details?id={}".format(app_id))
# print(driver.find_element(By.CSS_SELECTOR, "h1 > span").text.strip())
# input()
# driver.quit()
