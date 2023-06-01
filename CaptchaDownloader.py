from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import re
import requests
import shutil
import os
from uuid import uuid4


class CaptchaDownloader:

    def __init__(self, driver):
        self._driver = driver


    def _get_web_element_attribute_names(self, web_element):
        """Get all attribute names of a web element"""
        # get element html
        html = web_element.get_attribute("outerHTML")
        # find all with regex
        pattern = """([a-z]+-?[a-z]+_?)='?"?"""
        return re.findall(pattern, html)


    def _get_captcha_src(self, url):
        self._driver.get(url)
        download_btns = self._driver.find_elements(By.CSS_SELECTOR, ".c-button")
        slow_download_btn = download_btns[3]
        slow_download_btn.click()
        captcha_img = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "xapca-image"))
        )
        src = captcha_img.get_attribute('src')
        return src


    def _download_image(self, image_url, filename):
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)


    def download_captcha(self, url, count):
        src = self._get_captcha_src(url)
        dir_uuid = str(uuid4())
        path = f"downloads/{dir_uuid}"
        os.mkdir(path)
        for i in range(count):
            filename = f"downloads/{dir_uuid}/{uuid4()}.png"
            self._download_image(src, filename)
        return path
