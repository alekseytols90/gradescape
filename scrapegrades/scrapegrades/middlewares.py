# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from scrapy.utils.project import get_project_settings


class ScrapegradesSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapegradesDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        options = webdriver.ChromeOptions()
        # Set no interface
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        if get_project_settings().get("CHROME_PATH"):
            options.binary_location = get_project_settings()["CHROME_PATH"]
        # Initialize the Chrome driver
        if get_project_settings().get("CHROME_DRIVER_PATH"):
            self.driver = webdriver.Chrome(
                chrome_options=options,
                executable_path=get_project_settings()["CHROME_DRIVER_PATH"],
            )
        else:
            self.driver = webdriver.Chrome(chrome_options=options)

    def __del__(self):
        self.driver.close()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        try:
            print("Chrome driver begin...")
            login_url = getattr(spider, "login_url", None)
            login_email_input_xpath = getattr(
                spider, "login_email_input_xpath", None
            )
            login_password_input_xpath = getattr(
                spider, "login_password_input_xpath", None
            )
            login_submit_xpath = getattr(spider, "login_submit_xpath", None)
            login_email_address = getattr(spider, "login_email_address", None)
            login_password = getattr(spider, "login_password", None)
            if (
                login_url
                and login_email_input_xpath
                and login_password_input_xpath
                and login_submit_xpath
                and login_email_address
                and login_password
            ):
                self.driver.get(spider.login_url)
                self.driver.find_element_by_xpath(
                    spider.login_email_input_xpath
                ).send_keys(spider.login_email_address)
                time.sleep(3)
                self.driver.find_element_by_xpath(
                    spider.login_password_input_xpath
                ).send_keys(spider.login_password)
                time.sleep(1)
                self.driver.find_element_by_xpath(
                    spider.login_submit_xpath
                ).click()
                time.sleep(2)
            self.driver.get(request.url)
            time.sleep(10)
            return HtmlResponse(
                url=request.url,
                body=self.driver.page_source,
                request=request,
                encoding="utf-8",
                status=200,
            )
        except TimeoutException:
            return HtmlResponse(
                url=request.url, request=request, encoding="utf-8", status=500
            )
        finally:
            print("Chrome driver end...")

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
