# referenced from
# https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from infil_scraper import infilScraper
import discord
import json

from dotenv import load_dotenv
from discord.ext import commands

scrape_mode = False
debug = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# print("discord key: ", TOKEN)
client = discord.Client()
bot =  commands.Bot(command_prefix='!')

# Open and store json file data

with open("glossary.json", encoding='utf-8') as jsonFile:
    glossary = json.load(jsonFile)
    jsonFile.close()


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
        
# All glossary items obtained from https://glossary.infil.net/json/glossary.json once a day

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    scraper = infilScraper()
    if '!glossary' in message.content:
        # key_words = scraper.key_words_search_words(message.content)
        search_words = message.content[10::]

        if scrape_mode:
            result_text = scraper.search(message.content)
        else:
            term = list(filter(lambda item: item['term'].lower() == search_words.lower(), glossary))
            #print(term)
            if not term:
                for altterm in glossary:
                    if "altterm" in altterm:
                        if search_words.lower() in (alt.lower() for alt in altterm["altterm"]):                    
                            term = altterm
            if debug:
                print(message.content)
                print(search_words)
            #TODO: make this readable
            result_text = term



    if len(result_text) > 0:
        await message.channel.send(result_text)
    else:
        await message.channel.send("no results found :(")

client.run(TOKEN)
