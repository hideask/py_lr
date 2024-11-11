# RPA自动化组件默认引用
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests, json
def getRestFulResult(restFulURL,paramObject):
	r = requests.post(restFulURL, paramObject)
	return r.json()


# 判断selenium可控的chrome浏览器访问端口是否打开 如果没有则自动打开
if not webdriver.common.utils.is_connectable(9222):
    # 自动打开需设置 chrome浏览器启动路径到Path环境变量
	# os.popen("chrome --remote-debugging-port=9222 --disable-background-networking --start-maximized")
	print("请启动自动化模式的Chrome浏览器")
	quit()
# time.sleep(2)
s = Service(r"${driverPath}")
chrome_options = Options()
# 需在桌面浏览器快捷方式 属性 目标种的chrome.exe 后追加参数信息   --remote-debugging-port=9222
# 即可支持在已打开的页面中抓取元素
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_options.add_argument("--disable-infobars");
chrome_options.add_argument("--start-maximized");
chrome_options.add_argument("--disable-extensions");

#初始化浏览器对象
# browser = webdriver.Chrome(service=s, options=chrome_options)
browser=None

xPath = '/html/body/div[3]/div[1]/div/div/div[1]'
compareLabel = '【新】就业失业管理系统'
element_v = None
elementArray = browser.find_elements(by=By.XPATH,value=_xPath)
for _element in elementArray:
    for _child in _element.find_elements(by=By.XPATH,value="./*"):
        if _child.text == compareLabel:
            element_v = _element
            break
print(element_v)


