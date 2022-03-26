# referenced from
# https://medium.com/codex/learn-web-scraping-the-fun-way-with-a-discord-bot-704d3422a6a2

import requests
import json

class infilScraper:
    def __init__(self):
        self.url = 'https://glossary.infil.net/json/glossary.json'
    
    # Create search workds and url keywords part 
    # returns a list of words
    # ex: !command term1 term2 term3
    # rt: ["term1", "term2", "term3"]
    def key_words_search_words(self, user_message):
        words = user_message.split()[1:]
        return words

    def search(self, keywords): 
        r = requests.get(self.url)
        results = json.loads(r.content)
        for i in results:
            if i["term"] in keywords:
                print(i["term"] + ": " + i["def"])
        return "lol"


    def send_link(self, result_text, search_words): 
### todo
        return 
