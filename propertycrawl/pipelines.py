# -*- coding: utf-8 -*-
"""
Contains scrapy pipelines related to crawling properties
"""

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class PropertycrawlPipeline(object):
    """
    Pipeline for crawling property items
    """

    def process_item(self, item, _):  # pylint: disable=no-self-use
        """
        Return item as is without modifying.
        :param item:
        :param _:
        :return:
        """
        return item
