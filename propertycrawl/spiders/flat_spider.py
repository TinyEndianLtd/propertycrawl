"""
This module contains spiders for crawling property data
"""

import scrapy


class FlatListSpider(scrapy.Spider):
    """
    Spider for crawling property ad site
    """
    name = "flats"

    def start_requests(self):
        url_template = 'https://otodom.pl/{0}/mieszkanie/{1}/' \
            + '?search%5Bdescription%5D=1' \
            + '&search%5Bcreated_since%5D=14' \
            + '&search%5Bdist%5D=0' \
            + '&nrAdsPerPage=72'
        url = url_template.format(self.kind, self.city)  ## pylint: disable=no-member
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """
        Parses a page containing property listings
        :param response:
        :return:
        """
        for article in response.css(
                'article.offer-item::attr(data-url)').extract():
            yield scrapy.Request(article, callback=parse_detail)
        next_page = response.css(
            'a[data-dir="next"]::attr(href)').extract_first()
        yield scrapy.Request(next_page, callback=self.parse)


def parse_detail(response):
    """
    Parses a page containing listing details
    :param response:
    :return:
    """
    uuid = response.url.split("/")[-1].split("#")[0]
    lat = response.css('#adDetailInlineMap::attr(data-lat)').extract_first()
    lon = response.css('#adDetailInlineMap::attr(data-lon)').extract_first()
    price, area = response.css('ul.main-list span strong::text').extract()[:2]
    added_at, updated_at = response.css(
        '.section-offer-text.updated .right p::text').extract()
    address_details = response.css('.address-links')[0].css(
        'a::text').extract()[1:-1]
    yield {
        'uuid': uuid,
        'address_details': address_details,
        'lat': float(lat),
        'lon': float(lon),
        'price': sanitize_number(float, price),
        'area': sanitize_number(float, area),
        'added_at': sanitize_date(added_at),
        'updated_at': sanitize_date(updated_at)
    }


def sanitize_number(constructor, number):
    """
    Safely attempts to parse number using constructor (float or int) disregarding
    difference between commas and dots in price format
    :param constructor:
    :param number:
    :return:
    """
    return constructor("".join(number.split(" ")[:-1]).replace(",", "."))


def sanitize_date(s):
    """
    Safely attempts to parse date, omitting unnecessary date info
    :param s:
    :return:
    """
    return s.split(" ")[-1]
