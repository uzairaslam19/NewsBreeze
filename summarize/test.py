import openai
import json
import tiktoken
import requests
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

    def summa(self):

        if not self.api_key:
            raise ValueError("API key is required for ChatGPT API.")
        prompt="Summarise this news for me in 3-4 lines"
        model = self.model
        news_article= [
    {
        "content": "hindustan aeronautics limited hal hand light combat aircraft lca twin seater trainer version aircraft indian air force iaf bengaluru october 4 minister state defence ajay bhatt air chief marshal vivek ram chaudhari arrive lca tejas division plant historic event today mark achievement key milestone produce lca twin seater design strategic intent graduate bud pilot twin seater variant fighter pilots hal order 18 twin seater iaf plan deliver twin seater fy 2023 24 10 twin seater deliver progressively 2026 27 order expect iaf lca tejas large r d program undertake india maiden flight 2001 achieve milestone go backbone iaf fleet year come slate produce high number hindustan aeronautics limited bengaluru hal receive order 123 aircraft 32 fighter supply iaf squadron operational indian air force sulur af base series production lca tejas go swing hal balance aircraft plan deliver 2027 28 progressively hal successfully produce twin seater variant lca tejas capability support training requirement iaf augment role fighter case necessity lca tejas twin seater lightweight weather multi role 45 generation aircraft amalgamation contemporary concept technology relaxed static stability quadruplex fly wire flight control carefree manoeuvring advanced glass cockpit integrate digital avionic system advanced composite material airframe add india list elite country create capability operational defence forces feather cap atmanirbhar bharat initiative government minister state defence chief guest function unveiling lca twin seater hand release service rsd hand signal certificate soc conduct presence chief air staff iaf chairman managing director hal director general ada chief executive centre military airworthiness certification ce cemilac echelon iaf mod hal ada dgaqa cemilac drdo production partner present hal discussion foreign friendly country export lca tejas platform submit customize proposal export lca tejas fighter twin seater aircraft foreign friendly country world lca tejas good platform india flag bearer achieve export target set government input ani"
    }]
        openai.api_key =self.api_key
        summaries = []  # To store the summaries
        for news in news_article:
            content = news.get('content','')
            content= self.limit_tokens(content)
            messages= [{"role": "system", "content":f"{prompt}, {content}"}]
            response = openai.ChatCompletion.create(model=model,messages=messages,temperature=0.7)
            summary= response.choices[0].message["content"]
            summaries.append(summary)
        return summaries

def main():

    api_key= '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'
    summary= Summarize(api_key=api_key)
    print(summary.summa())

if __name__=="__main__":
    main()