# referenced from
# https://medium.com/codex/learn-web-scraping-the-fun-way-with-a-discord-bot-704d3422a6a2
# not necessary anymore :)

import requests
import json

class infilScraper:
    def __init__(self):
            self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
            self.url = 'https://glossary.infil.net/json/glossary.json'
    
    # Create search workds and url keywords part 
    def key_words_search_words(self, user_message):
        words = user_message.split()[1:]
        return words

    def search(self, keywords): 
        print("searching @: ", self.url+keywords)
        request = requests.get(self.url)
        results = json.loads(request.content)
        for term in results:
            if term["term"] in keywords:
                print(term["term"] + ": " + term["def"])
        return term["def"]
        