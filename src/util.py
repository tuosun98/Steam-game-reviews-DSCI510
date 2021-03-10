#2020.11.20 Tuo Sun
#####################
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time


class Tree_spider:
    """
    Tree_spider will automatically get html from a given url. If the website is dynamic, argument static should be
    False. Then Tree_spider will use selenium to simulate browser (Firefox) to get html from dynamic website.

    """
    def __init__(self, url, static=True, time_step=0.2, scroll_time=300):
        """
        :param url: the url of website that going to be crawled
        :param static: If website is dynamic website like IGN, static should be False
        :param time_step: scroll the page every 0.2 second in order to load the whole dynamic website
        :param scroll_time: total scroll time. For example, scroll_time is 300 time_step is 0.2, so the page will be
                            scrolled by 1500 times. However, not every scrolling is effective.
        """
        self.url = url
        self.content = []
        self.spider_path = []
        if static:
            self.static_web_spider()
        else:
            self.time_step = time_step
            self.scroll_time = scroll_time
            self.dynamic_web_spider()

    def dynamic_web_spider(self):
        """
        This method is for loading dynamic website by using selenium.
        self.content will get html through beautiful soup
        """
        driver = webdriver.Firefox(executable_path='src/geckodriver')
        driver.get(self.url)
        for i in range(int(self.scroll_time/self.time_step)):
            time.sleep(self.time_step)
            js = "var q=document.documentElement.scrollTop=document.body.scrollHeight"
            driver.execute_script(js)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        self.content = soup.html

    def static_web_spider(self):
        """
        This method is for loading static website by using requests.
        self.content will get html through beautiful soup
        """
        response = requests.get(self.url).content
        soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')
        self.content = soup.html

    def set_spider_path(self, path_list):
        """
        Tree_spider can crawl a website and load specific part of html through a list. This method will set and check
        the path.
        :param path_list: the path to load the html. The item in the list can be string or integer. Integers will be
                          filled into '.content[]' method and the string will be treated as a tag in soup.
        """
        #is items in path_list all integer or string?
        if all(map(lambda x: type(x) is int or type(x) is str, path_list)):
            self.spider_path = path_list
        else:
            raise ValueError('items in path_list should be integer or string')

    def get_info(self, info):
        """
        get the the specific part of input argument info whose type should be 'bs4.element.tag'.
        :param info: the whole or a part of html content
        :return: will return residue html content (type is bs4.element.tag) after loading on given path

        for example:
        s = Tree_spider(example_url)
        s.content                                   # will show html information of example_url
        s.set_spider_path([4, div, h3])             # set the path to `4, div, h3`
        s.get_info(s.content)                       # this will return `s.content.contents[4].div.h3`
        """
        for tag in self.spider_path:
            if type(tag) == str:
                info = eval('info.' + tag)
            else:
                str_tag = str(tag)
                info = eval('info.' + 'contents[' + str_tag + ']')
        return info

