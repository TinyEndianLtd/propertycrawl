import scrapy


class FlatListSpider(scrapy.Spider):
    name = "flats"

    def start_requests(self):
        url_template = 'https://otodom.pl/{0}/mieszkanie/{1}/?search%5Bdescription%5D=1&search%5Bcreated_since%5D=14&search%5Bdist%5D=0&nrAdsPerPage=72'
        url = url_template.format(self.kind, self.city)
        yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        for article in response.css('article.offer-item::attr(data-url)').extract():
            yield scrapy.Request(article, callback=self.parse_detail)
        next_page = response.css('a[data-dir="next"]::attr(href)').extract_first()
        yield scrapy.Request(next_page, callback=self.parse_list)

    def parse_detail(self, response):
        uuid = response.url.split("/")[-1].split("#")[0]
        lat = response.css('#adDetailInlineMap::attr(data-lat)').extract_first()
        lon = response.css('#adDetailInlineMap::attr(data-lon)').extract_first()
        price, area = response.css('ul.main-list span strong::text').extract()[:2]
        added_at, updated_at = response.css('.section-offer-text.updated .right p::text').extract()
        address_details = response.css('.address-links')[0].css('a::text').extract()[1:-1]
        yield {
            'uuid': uuid,
            'address_details': address_details,
            'lat': float(lat),
            'lon': float(lon),
            'price': self.sanitize_number(float, price),
            'area': self.sanitize_number(float, area),
            'added_at': self.sanitize_date(added_at),
            'updated_at': self.sanitize_date(updated_at)
        }

    def sanitize_number(self, constructor, number):
        return constructor("".join(number.split(" ")[:-1]).replace(",", "."))

    def sanitize_date(self, s):
        return s.split(" ")[-1]
