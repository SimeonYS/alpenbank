import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import AlpenbankItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class AlpenbankSpider(scrapy.Spider):
	name = 'alpenbank'
	start_urls = ['https://www.alpenbank.com/bozen/aktuelles.html',
				  'https://www.alpenbank.com/innsbruck/aktuelles.html',
				  'https://www.alpenbank.com/no_cache/salzburg/aktuelles.html',
				  ]

	def parse(self, response):
		post_links = response.xpath('//div[@class="col-xs-12 col-sm-8 col-sm-pull-2 newstitle"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		pages = response.xpath('//ul[@class="pagination"]/li/a/@href').getall()
		yield from response.follow_all(pages, self.parse)


	def parse_post(self, response):

		date = response.xpath('//time//text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="news-text-wrap col-xs-12 col-sm-8"]//text() | //div[@class="csc-textpic-text"]//text() | //div[@class="teaser-text"]//text() | //div[@class="news-text-wrap col-xs-12 col-sm-12"]//text() | //div[@class="row clearfix"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=AlpenbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
