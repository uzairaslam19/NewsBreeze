#--------------------Import Necessary Packages------------#
import hydra
import json
from scrapy.crawler import CrawlerRunner
from Scrapy_Project.scrapenews.spiders.new_spider import News_Spider
import dearpygui.dearpygui as dpg
from twisted.internet import reactor
from Clean_News.clean import CleanNews
from summarize.summarize import Summarize
import warnings
import logging
import sys
from pyfiglet import Figlet
import webbrowser
# Set the logging level for openai, urlib, and scrapy spider
#---------------------Logging Settings--------------------#
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("news").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR) 
logging.getLogger("urllib3").setLevel(logging.ERROR)
#Store the logs to a file called app.log
logging.basicConfig(filename = 'app.log', filemode = 'w', format = '%(name)s - %(levelname)s - %(message)s')

#----------------Global Variables-------------------------#
# Global variable to store scraped news
scraped_news = []
f = Figlet(font = 'fender')

#---------------------------Main Function-----------------#
@hydra.main(version_base=None, config_path="conf/", config_name="config")
def main(cfg, keyword = None, max_news = None, summ_option = None):
    """
    The main function of the News Breeze application.
    
    Args:
        cfg: Hydra configuration object.
        keyword: Optional keyword for news search.
        max_news: Optional maximum number of news articles to scrape.
        summ_option: Optional option to summarize the scraped news.
    """
    print(f.renderText('!!Welcome to News Breeze!!'))
    try:
        guisetup(cfg)
        dpg.create_viewport(title = 'CS50P Final Project', width = 900, height = 600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.create_context()  
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        print("Code Finished")
        dpg.destroy_context()
    except Exception as e:
        logging.error(f"An error occurec, {str(e)}")
    
#---------------------DeapyGui Setup--------------------------#
def guisetup(cfg):
    dpg.create_context()
    dpg.set_global_font_scale(1.35)
    width, height, channels, data = dpg.load_image(cfg.images.logo)
    width2, height2, channels2, data2 = dpg.load_image(cfg.images.dalle)
    width3, height3, channels3, data3 = dpg.load_image(cfg.images.dalle2)
    with dpg.texture_registry(show = False):
        dpg.add_static_texture(width = width,
                                height = height, 
                                default_value = data,
                                tag = "texture_tag")
    with dpg.texture_registry(show = False):
        dpg.add_static_texture(width = width2,
                                height = height2, 
                                default_value = data2,
                                tag = "texture_tag2")
    with dpg.texture_registry(show = False):
        dpg.add_static_texture(width = width3,
                                height = height3, 
                                default_value = data3,
                                tag = "texture_tag3")    
    with dpg.window(label = "News Breeze", height = 800, width = 800, id = 1):
        # Set as primary window
        #dpg.set_primary_window(1, True)
        dpg.add_image("texture_tag", width = 800, height = 300, pos = (0,0))
        dpg.add_image("texture_tag2", width = 100, height = 100, pos = (660,435))
        dpg.add_image("texture_tag3", width = 100, height = 100, pos = (10,330))
        dpg.add_separator()
        dpg.add_spacing(count = 5)
        dpg.add_text("Welcome to News Breeze\n", pos = (280, 250), color = [115, 147, 179])
        dpg.add_text("""Your very own News Scraper and Summarizer.""",
                    color=[115, 147, 179], pos = (180, 270))
        dpg.add_spacing(count = 14)
        dpg.add_input_text(tag = 'Keyword_Input', pos = (120, 340), width = 540, hint = "Please Specify a keyword e.g. Covid 19 ", use_internal_label = False)
        dpg.add_slider_int(tag = 'Max_News', label = ' Max_News', pos = (120, 380), width = 540, default_value = 3, max_value = 5, clamped = True, min_value = 1)         
        dpg.add_checkbox(tag='Summary_Input',pos=(620,533),use_internal_label=False,enabled=True)
        with dpg.group(horizontal=True):
            dpg.add_loading_indicator(label="Please Wait",circle_count=4,pos=(70,230))
            dpg.add_button(label="Get News",pos=(670,340),use_internal_label=True,callback=lambda sender:get_news_callback(cfg,sender,False))
            dpg.add_button(tag="Summarise",label="Summarise",pos=(660,533),use_internal_label=True,callback=lambda sender:get_summaries_callback(cfg,sender,True)) 
            dpg.add_text(tag="news_text",pos=(120,430),wrap=500,color=[34,139,34])        
            dpg.add_button(label="Refresh", pos=(720, 35), use_internal_label=True, callback=lambda sender: get_news_callback(cfg,sender, False))


#------------------Second call back function to get Summaries-------------------#
def get_summaries_callback(cfg,sender,sum=True):
    summar=""
    check=dpg.get_value("Summary_Input")
    try:
        if check:
            dpg.set_value("news_text",f"Now Summarizing your news, Please Wait!!")
            clean_text(cfg)
            for summary in summarise(cfg):
                id, su =summary.split(':')
                summar += f"\n{id}:\n{su}\n"
            dpg.set_value("news_text",summar)
        else:
            dpg.set_value("news_text","If you want to summarise the news, please check the box")
    except Exception as e:
        logging.error(f"An error occurred {e}")
    
#--------------------------Call back function---------------------------#
def get_news_callback(cfg,sender,sum=False):
        keyword = dpg.get_value("Keyword_Input")
        print(f"Keyword is: {keyword}")
        max_news = dpg.get_value("Max_News")
        print(f"Max_news is: {max_news}")
        try:
            if keyword:
                if not sum: 
                    scraped_news.clear()
                    dpg.set_value("news_text",f"Scraping the news for keyword {keyword}")
                    scrape(cfg, keyword, max_news)
                    print(f"News Scraped...{scraped_news}")
                    news_text_value =""
                    for idx, article in enumerate(scraped_news):
                        title = article.get("title", "N/A")
                        link = article.get("link", "#") # Use "#" as a placeholder link if no link is provided
                        author = article.get('author', 'N/A') 
                        published_date = article.get('publishedAt', 'N/A')
                        news_article_text = f"\n{idx + 1}.  Title: {title}\n"
                        news_article_text += f"    Author: {author}\n"
                        news_article_text += f"    Published Date: {published_date}\n"
                    # Append the formatted news article text to 'news_text_value'
                        news_text_value += news_article_text
                    dpg.set_value("news_text", news_text_value)
                    
                else:
                    sys.exit("Thanks you have a nice day")
            else:
                dpg.set_value("news_text","No Keyword provided")
        except Exception as e:
            logging.error(f"An error occurred, {str(e)}")
            


#-----------------------Call the Scrapy Spider to scrape news---------------#
def scrape(cfg, keyword, max_news):
    """
    Function to scrape news articles using BeautifulSoup.

    Args:
        cfg: Hydra configuration object.
        keyword (str): The keyword for news search.
        max_news (str): The maximum number of news articles to scrape.
    """
    api_key =cfg.api
    json_output_path = cfg.path.json_output
    #Surpress the Scrapy log
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            process = CrawlerRunner()
            process.crawl(
                News_Spider,
                keyword = keyword,
                api_key = api_key,
                json_output_path= json_output_path,
                max_news=max_news
                )
            #process.start()
            d=process.join()
            d.addBoth(lambda _: reactor.stop())
            reactor.run(0)
        # Load scraped data
        scraped_data = load_scraped_news(json_output_path)
        scraped_news.extend(scraped_data)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


#--------------------Load the scraped news from json-----------------#
def load_scraped_news(json_file_path):
    """
    Function to load scraped news data from a JSON file.

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        list: A list of scraped news articles.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            scraped_data = json.load(json_file)
            print(f"Loaded {len(scraped_data)} news articles from {json_file_path}")
            return scraped_data
    except Exception as e:
        print(f"Error loading scraped news: {str(e)}")
    

#-------------Function to call the clean module to clean the news----------#
def clean_text(cfg):
    """
    Function to preprocess and clean scraped news articles.

    Args:
        cfg: Hydra configuration object.
    """
    cleaner = CleanNews()
    #Take the input/output file path from hydra config
    json_file_path = cfg.path.json_output
    output_json_path = cfg.path.cleaned_json_output
    #Pass in the paths to the news_list function
    cleaner.news_list(json_file_path, output_json_path)


#------------Function to call the summarizer module to summarise the news-----#
def summarise(cfg):
    """
    Function to summarize cleaned news articles.

    Args:
        cfg: Hydra configuration object.

    Returns:
        list: A list of summaries for news articles.
    """
    api_key =cfg.api.open_api_key
    json_path= cfg.path.cleaned_json_output
    output_path= cfg.path.summary_output
    summariser= Summarize(api_key=api_key , json_path = json_path)
    return summariser.summa(output_path)
    


if __name__ == "__main__":
    main()
    







