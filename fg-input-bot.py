# referenced from
# https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from unicodedata import name
import discord
import json # read glossary in
import re # cleaning text ewwww
import asyncio

# web scraping
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from discord.ext import commands

import glossary_functions
import g_search

scrape_mode = False
debug = True
if scrape_mode:
    from infil_scraper import infilScraper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# print("discord key: ", TOKEN)
client = discord.Client()
bot = commands.Bot(command_prefix='!')

# Open and store json file data

with open("glossary.json", encoding='utf-8') as jsonFile:

    glossary = json.load(jsonFile)
    jsonFile.close()

g_index = []
for dict in glossary:
    g_index.append(dict["term"])
g_index.sort()

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

g_index_pages = list(chunks(g_index, 30))


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    if debug:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
        
# All glossary items obtained from https://glossary.infil.net/json/glossary.json
# TODO: implement once a day/month update on glossary. 
# might move this to it's own .py cuz it's getting kinda large :sweat:
# moved :sunglasses:

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "!gindex" in message.content.lower() or "!glossaryindex" in message.content.lower():
        await glossary_functions.glossary_index(message, g_index_pages, client)
    # glossary search

    elif '!g' in message.content or "!glossary" in message.content:
        await g_search.g_search(message, glossary, debug)
  
client.run(TOKEN)
