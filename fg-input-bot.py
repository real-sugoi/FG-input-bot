# referenced from
# https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from infil_scraper import infilScraper

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# print("discord key: ", TOKEN)
client = discord.Client()
bot =  commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    
# https://glossary.infil.net/?t=

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    scraper = infilScraper()
    if '!glossary' in message.content:
        key_words, search_words = scraper.key_words_search_words(message.content)
        result_text = scraper.search(key_words)


    if len(result_text) > 0:
        await message.channel.send(result_text)
    else:
        await message.channel.send("no results found :(")

client.run(TOKEN)
