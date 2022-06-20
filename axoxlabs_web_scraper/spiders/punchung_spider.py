"""
https://punchng.com/ scraper.
"""

import scrapy

from axoxlabs_web_scraper.spiders.util import get_random_agent


class PunchungScraper(scrapy.Spider):
    """
    Spider for scraping https://punchng.com/ articles.
    """

    name = "punchung_scraper"
    user_agent =  get_random_agent()

    def start_requests(self):
        """
        Yields list of categories URLs to scrape.
        """

        list_categories = [
            "politics", "news", "sports", "metro-plus", "entertainment", "business", "editorial",
            "podcast", "video", "spice", "special-features", "education", "sex-relationship",
            "interview", "columns", "opinion"]
        # HealthWise needs a special spider
        list_categories = list_categories[:3]  # Temporarily test 3 categories
        lists_urls = [
            "https://punchng.com/topics/{}".format(item) for item in list_categories]
        for url, category in zip(lists_urls, list_categories):
            yield scrapy.Request(
                url=url, meta={"category": category}, callback=self.scrape_items,  headers={
            'User-Agent': self.user_agent
        })


    def set_user_agent(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return request

    def scrape_items(self, response):

        # Extract number results pages
        number_pages = response.css(".page-link").extract()[-2].strip().replace(",", "")
        number_pages = 2  # Temporarily test 2 PAGES
        response.meta["category"]

        for page_num in range(number_pages):
            yield scrapy.Request(
                url="{}/page/{}".format(response.url, str(page_num+1)),
                meta={"category": response.meta["category"]}, callback=self.scrape_page_items,
                dont_filter=True)

    def scrape_page_items(self, response):

        article_blocks = response.css("article")
        for article in article_blocks:
            article_url = article.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                url=article_url, meta={"category": response.meta["category"]}, callback=self.scrape_item)

    @staticmethod
    def scrape_item(response):

        yield {
            'headline': response.xpath("////h1[@class='post-title']/text()").get(),
            'image_url': response.xpath("//div[@class='post-image-wrapper']/figure/img/@src").get(),
            'authour': response.xpath(
                "(//span[@class='post-author']/strong)[1]/text()[normalize-space()]").get().strip(),
            'posted_date': response.xpath("//span[@class='post-date']/text()[normalize-space()]").get().strip(),
            'description': response.xpath("(//div[@class='post-content']/p)[1]/text()").get(),
            'newspaper_name': "Punch Newspaper",
            'category':  response.meta["category"],
            'url': response.url
        }