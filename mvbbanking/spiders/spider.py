import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import MvbbankingItem
from itemloaders.processors import TakeFirst


class MvbbankingSpider(scrapy.Spider):
	name = 'mvbbanking'
	start_urls = ['https://mvbbanking.com/wp-admin/admin-ajax.php?id=&post_id=0&slug=home&canonical_url=https%3A%2F%2Fmvbbanking.com%2Farticle-center%2F&posts_per_page=999999&page=0&offset=0&post_type=post&repeater=default&seo_start_page=1&preloaded=false&preloaded_amount=0&order=DESC&orderby=date&action=alm_get_posts&query_type=standard']

	def parse(self, response):
		data = json.loads(response.text)
		raw_html = scrapy.Selector(text=data['html'])
		post_links = raw_html.xpath('//a[@class="permalink"]/@href').getall()
		print(post_links)
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="post-content"]//text()[normalize-space() and not(ancestor::noscript | ancestor::h1 | ancestor::p[@class="post-date"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//p[@class="post-date"]/text()').get()

		item = ItemLoader(item=MvbbankingItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
