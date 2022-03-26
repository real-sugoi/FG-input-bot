# referenced from
# https://medium.com/codex/learn-web-scraping-the-fun-way-with-a-discord-bot-704d3422a6a2

import requests
from bs4 import BeautifulSoup
import urllib
import json

class infilScraper:
    def __init__(self):
            self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
            self.url = 'https://glossary.infil.net/?t='
    
    # Create search workds and url keywords part 
    def key_words_search_words(self, user_message):
        words = user_message.split()[1:]
        keywords = '+'.join(words)
        search_words = ' '.join(words)
        return keywords, search_words

    def search(self, keywords): 
        print("searching @: ", self.url+keywords)
        soup = BeautifulSoup(urllib.request.urlopen(self.url+keywords).read())
        script = soup.findAll('script')[1].string
        data = json.loads(script)
        print(data)
        #print(terms)
        return soup
        
    def send_link(self, result_text, search_words): 
### todo
        return 