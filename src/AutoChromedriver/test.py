import os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


try:
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/')
except WebDriverException as e:
    print("This was encountered", e)
