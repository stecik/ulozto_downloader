from selenium import webdriver
from selenium.webdriver import ChromeOptions
from CaptchaDownloader import CaptchaDownloader
from CaptchaBreaker import CaptchaBreaker
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import re
import requests
import shutil
from uuid import uuid4


if __name__ == "__main__":
    options = ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    URL = "https://uloz.to/file/DzHJfMFnPVRt/harry-potter-5-cz-xvid-avi#!ZGOxBQR2AQWuBJAzMGqwLzZkZzD3MUEFIyNksv5ZAHWuI2H4MN=="
    captcha_downloader = CaptchaDownloader(driver)
    path = captcha_downloader.download_captcha(URL, 3)
    model_path = "models/model_v1/"
    captcha_breaker = CaptchaBreaker(model_path)
    captcha_breaker.predict(path)
    driver.close()