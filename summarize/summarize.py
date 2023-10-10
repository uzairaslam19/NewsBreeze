import openai
import json
import tiktoken
import requests
import logging
openai.util.logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger().setLevel(logging.CRITICAL)
# Initiate a summary class that takes data from json, and api key for chatgpt, calls chatgpt and summarizes
class Summarize:
    def __init__(self, api_key=None, model="gpt-3.5-turbo",json_path=None, *args, **kwargs):
        self.api_key= api_key
        self.model = model
        self.json_path= json_path
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def limit_tokens(self, news_text, max_tokens=4000):

        if not isinstance(news_text, str):
            news_text = str(news_text)
        # Tokenize the text and count tokens
        tokenized_text=self.encoding.encode(news_text)
        tokens =len(tokenized_text)

        if tokens > max_tokens:
            # If the text exceeds the limit, truncate it
            truncated_text = ' '.join(tokenized_text[:max_tokens])
            return self.encoding.decode(truncated_text)
        else:
            # If the text is within the limit, return it as is
            return news_text

    def summa(self,output_path):

        if not self.api_key:
            raise ValueError("API key is required for ChatGPT API.")

        if not self.json_path:
            raise ValueError("JSON file path is required.")
        prompt="Summarise this news for me in 2-3 lines"
        model = self.model
        with open(self.json_path, 'r', encoding='utf-8') as news:
            news_article= json.load(news)
        openai.api_key =self.api_key
        summaries = []  # To store the summaries
        for idx, news in enumerate(news_article):
            content = news.get('content','')
            content= self.limit_tokens(content)
            messages= [{"role": "system", "content":f"{prompt}, {content}"}]
            response = openai.ChatCompletion.create(model=model,messages=messages,temperature=0.7)
            summary= response.choices[0].message["content"]
            summaries.append(f"Summary {idx +1}: {summary}")
        
        with open(output_path,'w', encoding='utf-8') as o:
            json.dump(summaries, o, ensure_ascii= False, indent=4)
        
        return summaries