import scrapy
from hydra.core.config_store import ConfigStore
import logging
import json
logging.getLogger('scrapy').propagate = False

#Define a new Spider object that will scrape the news for any given word
class News_Spider(scrapy.Spider):
    name ='news'
    article_count =0
    def __init__(self, keyword = None, api_key = None, language='en',json_output_path =None, max_news=4,*args, **kwargs):
        super(News_Spider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.api_key = api_key
        self.language = language
        self.json_output_path = json_output_path
        self.max_news = int(max_news)

    def start_requests(self):
        if self.keyword:
            start_url =f"https://newsdata.io/api/1/news?apikey={self.api_key}&q={self.keyword}&language={self.language}"
            yield scrapy.Request(f'{start_url}', callback=self.parse)

    def parse(self,response):
        articles =[]
        try:
            json_data=json.loads(response.text)
            for article_data in json_data.get('results' ,[]):
                content =article_data.get('content')
                #Only take articles that have content
                if content:

                    article ={
                        "title" :article_data.get('title'),
                        "content": content,
                        "link": article_data.get('link'),
                        "publishedAt" :article_data.get("pubDate"),
                        "author": article_data.get("creator"),
                    }
                    article['publishedAt'] =article['publishedAt'][:10]
                    article['author']= article['author'][0] if article['author'] and isinstance(article['author'], list) and len(article['author']) > 0 else "Unknown Author"
                    articles.append(article)

                #Stop parsing if 5 news articles have been collected
                self.article_count +=1
                #Limit the number of News to 5 only
                if self.article_count >= self.max_news:
                    break

            # Save data to a JSON file
            filename = f'{self.json_output_path}'
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(articles, json_file, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            self.logger.error(f'Error parsing JSON data: {e}')

        self.log(f'Saved data to {filename}')
