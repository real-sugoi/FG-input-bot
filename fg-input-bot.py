# referenced from
# https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from unicodedata import name
import discord
import json # read glossary in
import re # cleaning text ewwww

# web scraping
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from discord.ext import commands

scrape_mode = False
debug = True
if scrape_mode:
    from infil_scraper import infilScraper

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
        
# All glossary items obtained from https://glossary.infil.net/json/glossary.json
# TODO: implement once a day/month update on glossary. 
# might move this to it's own .py cuz it's getting kinda large :sweat:

def clean_text(text):
    #text = text.replace("'>", "__**")
    text = re.sub(r"(!<')([a-zA-Z0-9\/\ \.\-]+)'>", r"**__\2__**", text)
    text = re.sub("(!<')([a-zA-Z0-9\/\ \.\-]+)','([a-zA-Z0-9\/\ \.\-]+)'>", r" \3 (**__\2__**)", text)
    print(text)
    text = text.replace("'>", "__**")
    text = re.sub("(?:<br>|</br>)", "\n", text)
    text = re.sub("(?:<[^\s]+>)", "", text)
    return text 

def clean_feet(text):
    text = re.sub(r"(!<')([a-zA-Z0-9\/\ \.\-]+)'>", r"\2}", text)
    text = re.sub("(!<')([a-zA-Z0-9\/\ \.\-]+)','([a-zA-Z0-9\/\ \.\-]+)'>", r"\3 (\2)", text)
    return text
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if '!glossary' in message.content:
        search_words = message.content[10::]

        if scrape_mode:
            scraper = infilScraper()
            result_text = scraper.search(message.content)
        else:
            result_found = False
            term = list(filter(lambda item: item['term'].lower() == search_words.lower(), glossary))
            #print(term)
            if term:
                term = term[0]
                result_found = True
            elif not term:
                for dict in glossary:
                    if "altterm" in dict:
                        if search_words.lower() in (alt.lower() for alt in dict["altterm"]):                    
                            term = dict
                            result_found = True

            # really bad way of checking if dict has these keys
            if result_found:
                hasAlt = "altterm" in term
                hasVideo = "video" in term
                hasImage = "image" in term
                hasJP = "jp" in term
                hasGameSpecific = "games" in term

                if debug:   
                    print(message.content)
                    print(search_words)
                    print("type: ", type(term))
                    print(hasAlt)
                    print(hasVideo)
                    print(hasImage)
                    print(hasJP)
                    print(hasGameSpecific)
                #TODO: make this readable
                
                # replace embedded with underline to indicate more terms
                embed = discord.Embed(title=term["term"], color=0x00ff00)

                if(hasImage):
                    embed.set_image(url=("https://glossary.infil.net/images/terms/" + term["term"].replace(" ", "%20") + "." + term["image"][0]))
                    embed.set_footer(text=clean_feet(term["image"][1]))
                elif(hasVideo):
                    # get the gif version cuz video embed doesn't work :(
                    # this gif looks really bad thouuuuuughhhh T_T
                    link = requests.get("https://gfycat.com/" + term["video"][0])
                    soup = BeautifulSoup(link.content, 'html.parser')
                    soup = soup.find(property="og:image")
                    video = soup.get('content')

                    embed.set_image(url=(video))
                    embed.set_footer(text=clean_feet(term["video"][1]))

                if(hasAlt):
                    embed.add_field(name="Alternate Name(s): ", value=", ".join(str(alt) for alt in term["altterm"]))

                if(hasJP):
                    embed.add_field(name="JP name(s): ", value=clean_text(term["jp"].replace("Lit.", "\n")))
                embed.description = clean_text(term["def"])

                if(hasGameSpecific):
                    embed.add_field(name="Specific to: ", value=", ".join(str(alt) for alt in term["games"]))

                # send the embedded message
                await message.channel.send(embed=embed)
            else: 
                await message.channel.send("No results found")

client.run(TOKEN)
