from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyautogui
import pyperclip
import os
import traceback
import requests, json
import suds.client
import math

s = Service(r"${driverPath}")
chrome_options = Options()
# 需在桌面浏览器快捷方式 属性 目标种的chrome.exe 后追加参数信息   --remote-debugging-port=9222
# 即可支持在已打开的页面中抓取元素
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_options.add_argument("--disable-infobars");
chrome_options.add_argument("--start-maximized");
chrome_options.add_argument("--disable-extensions");
browser = webdriver.Chrome(service=s, options=chrome_options)

listElement = browser.find_element(by=By.XPATH, value='//*[@id="task_list"]')

viewItem = listElement.find_element(by=By.XPATH, value='.//div[@class="slick-viewport"]')

gridItems = viewItem.find_element(by=By.XPATH, value='.//div[@class="slick-grid-canvas"]/div')

perList = []

for item in gridItems:
    dataItem = item.find_element(by=By.XPATH, value='.//div[@class="slick-cell lr l4 r4""]')
    if (dataItem is None) :
        dataItem = item.find_element(by=By.XPATH, value='.//div[@class="slick-cell lr l4 r4 selected"]')

    perList.append(dataItem.text)