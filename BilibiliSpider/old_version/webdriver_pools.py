# -*- coding:utf-8 -*-
from multiprocessing import Process
from queue import Queue
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions


class WebdriverPool(object):
    def __init__(self, concurrent_requests, browser, options):
        self.options = options
        maxsize = concurrent_requests if concurrent_requests <= 4 else 4
        self.queue = Queue(maxsize=concurrent_requests)
        for q in range(concurrent_requests):
            if browser == "chrome":
                self.queue.put(Chrome(executable_path="F:\ChromeDriver\chromedriver.exe", chrome_options=options))
            elif browser == "firefox":
                self.queue.put(Firefox(firefox_options=options))


if __name__ == '__main__':
    w = WebdriverPool(concurrent_requests=2, browser="chrome", options=ChromeOptions())