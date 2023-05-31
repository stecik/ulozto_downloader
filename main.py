from selenium import webdriver

PATH = "chromedriver.exe"

driver = webdriver.Chrome(PATH)

URL = "https://uloz.to/file/DzHJfMFnPVRt/harry-potter-5-cz-xvid-avi#!ZGOxBQR2AQWuBJAzMGqwLzZkZzD3MUEFIyNksv5ZAHWuI2H4MN=="

driver.get(URL)