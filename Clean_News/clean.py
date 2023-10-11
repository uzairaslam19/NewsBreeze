import json
import re
import spacy

class CleanNews:
    """Cleaning module made with spacy to preprocess and clean news"""
    def __init__(self, model_name="en_core_web_sm"):
        self.nlp = spacy.load(model_name)
        self.stopwords =set(spacy.lang.en.stop_words.STOP_WORDS)
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self.non_alphanumeric_pattern = r'[^a-zA-Z0-9\s]'

    def preprocessing(self,text):
        """ Function to clean the contents of a news article"""
        doc= self.nlp(text)
        cleaned_tokens =[]
        for token in doc:
            if not token.is_stop and not token.is_punct:
                cleaned_tokens.append(token.lemma_.lower())
        cleaned_text =" ".join(cleaned_tokens)
        # Use re.sub to replace URLs with an empty string
        text_without_links = re.sub(self.url_pattern, '', cleaned_text)
        # Use regular expression to keep only alphanumeric characters and spaces
        cleaned = re.sub(self.non_alphanumeric_pattern, '', text_without_links)
        return cleaned


    def news_list(self, input_path, output_path):
        """Function that takes the contents of news articles from a
        json passed it to preprocessing function and saves it in an output json"""
        cleaned_news_list = []
        with open(input_path, 'r', encoding ='utf-8') as f:
            news_data=json.load(f)

        for news in news_data:
            content =news.get('content','')
            cleaned_content = self.preprocessing(content)
            cleaned_news_list.append({'content':cleaned_content})
        with open(output_path,'w', encoding='utf-8') as o:
            json.dump(cleaned_news_list, o, ensure_ascii= False, indent=4)
            
