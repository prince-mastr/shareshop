from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import urllib.request
from PIL import Image ,ImageEnhance 
import pytesseract
import glob
import os
import pathlib


url = "http://127.0.0.1:8000/admin/core/item/add/"
driver = webdriver.Firefox()
driver.maximize_window()
driver.get(url)
time.sleep(5)
driver.find_element_by_name("username").send_keys("Prince")
driver.find_element_by_name("username").send_keys(Keys.RETURN)
time.sleep(5)
driver.find_element_by_name("password").send_keys("9653")
driver.find_element_by_name("password").send_keys(Keys.RETURN)
time.sleep(5)
path = pathlib.Path().absolute()
count = 0
for photo in glob.glob(str(path.parent)+"/apple/*"):
    count = count+1
    driver.get(url)
    driver.find_element_by_name("title").send_keys("Apple"+ str(count).zfill(3))
    driver.find_element_by_name("price").send_keys(350)
    driver.find_element_by_name("discount_price").send_keys(350)
    s1 = Select(driver.find_element_by_name('category'))
    s1.select_by_value("6")
    driver.find_element_by_name("slug").send_keys("Apple"+ str(count).zfill(3))
    driver.find_element_by_name("description").send_keys("Apple"+ str(count).zfill(3))
    driver.find_element_by_name("image").send_keys(photo)
    driver.find_element_by_name("slug").send_keys(Keys.RETURN)
    time.sleep(10)








