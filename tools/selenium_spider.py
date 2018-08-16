# -*- coding:utf-8 -*-
__author__ = 'KoiSato'

import time
# from selenium import webdriver
# from settings import USER, PASSWD
# from scrapy.selector import Selector

# browser = webdriver.Chrome(executable_path="F:\ChromeDriver\chromedriver.exe")
# browser.get("http://www.weibo.com")
# time.sleep(5)
# user_btn = browser.find_element_by_xpath("//div[contains(@class, 'username')]//input").send_keys(USER)
# passwd_btn = browser.find_element_by_xpath("//div[contains(@class, 'password')]//input").send_keys(PASSWD)
# submit_btn = browser.find_element_by_xpath("//div[contains(@class, 'login_btn')]/a").click()

# 模拟浏览器下滑操作
# browser.execute_script("""
#     window.scrollTo(0, document.body.scrollHeight);
#     var lenOfPage = document.body.scrollHeight;
#     return lenOfPage;
# """)

# # 设置selenium不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(executable_path="F:\ChromeDriver\chromedriver.exe", chrome_options=chrome_opt)
# browser.get("https://www.taobao.com")
# browser.close()

# 利用PhantomJS动态加载页面, 无界面浏览器, 但在多进程下性能下降严重
# browser = webdriver.PhantomJS(executable_path="F:\phantomjs-2.1.1-windows\\bin\phantomjs.exe")
# browser.get("https://www.imooc.com/")
# print(browser.page_source)
# browser.quit()