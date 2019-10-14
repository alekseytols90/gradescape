# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders.init import InitSpider


class GradebookSpider(InitSpider):
    name = "gradebook"
    allowed_domains = ["dreambox.com"]
    start_urls = [
        "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=7d&by=day"
    ]
    login_url = "https://play.dreambox.com/login/n352/3kaw"
    login_email_input_xpath = "//*[@id='txtEmailAddress']"
    login_password_input_xpath = "//*[@id='txtPassword']"
    login_submit_xpath = (
        "/html/body/div[1]/div/div[3]/div[1]/form/div[4]/div/input"
    )
    login_email_address = "charlotte.wood@epiccharterschools.org"
    login_password = "Teacher1"

    def parse(self, response):
        for row in response.xpath(
            "//tbody[contains(@ng-hide, 'loadingPage')]/tr"
        ):
            yield {
                "First Name": row.xpath(
                    "normalize-space(./td[@class='first_name']/span/text())"
                ).extract_first(),
                "Last Name": row.xpath(
                    "normalize-space(./td[@class='last_name']/span/text())"
                ).extract_first(),
                "Total Time": row.xpath(
                    "normalize-space(./td/span[contains(@ng-class, 'total_session_time')]/text())"
                ).extract()[0],
                "Lessons Completed": row.xpath(
                    "normalize-space(./td/span[contains(@ng-class, 'count_lessons_completed')]/text())"
                ).extract()[0],
            }
