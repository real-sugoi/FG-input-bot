# referenced from
# https://realpython.com/how-to-make-a-discord-bot-python/

# bot.py
import os
from unicodedata import name
import discord
import json
import re

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
        
# All glossary items obtained from https://glossary.infil.net/json/glossary.json once a day
# might move this to it's own .py cuz it's getting kinda large :sweat:

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if '!glossary' in message.content:
        # key_words = scraper.key_words_search_words(message.content)
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
                
                embed_kwargs = {}

                

                # replace embedded with underline to indicate more terms
                #result_text = ""
                #result_text += (term["term"] + "\n")
                if(hasImage):
                    embed = discord.Embed(title=term["term"], color=0x00ff00)
                    embed.set_image(url=("https://glossary.infil.net/images/terms/" + term["term"].replace(" ", "%20") + "." + term["image"][0]))
                    embed.set_footer(text=term["image"][1])
                    #result_text += ("https://glossary.infil.net/images/terms/" + term["term"].replace(" ", "%20") + "." + term["image"][0])
                    #footer_text = term["image"][1]         
                elif(hasVideo):
                   # embed = discord.Embed(
                   #     title=embed.title, 
                   #     fields={
                   #         for field in embed.fields:
                   #             name=field.name
                   #             }
                   #          )
                    embed = discord.Embed(title=term["term"], video=("https://gfycat.com/" + term["video"][0]), color=0x00ff00)
                    embed.add_field(name="video link:", value=("https://gfycat.com/" + term["video"][0]))
                    #embed.set_image(url=("https://gfycat.com/" + term["video"][0]))
                    embed.set_footer(text=term["video"][1])
                    #result_text += ("https://gfycat.com/" + term["video"][0])
                    #footer_text = term["video"][1]
                else:
                    embed = discord.Embed(title=term["term"], color=0x00ff00)
                if(hasAlt):
                    embed.add_field(name="Alternate Name(s): ", value=", ".join(str(alt) for alt in term["altterm"]))
                    #result_text += ", ".join(str(alt) for alt in term["altterm"]) + "\n"
                if(hasJP):
                    embed.add_field(name="JP name(s): ", value=term["jp"])
                    #result_text += (term["jp"] + "\n")
                #result_text += ("\n" + term["def"] + "\n")
                embed.description = term["def"]
                if(hasGameSpecific):
                    embed.add_field(name="Specific to: ", value=", ".join(str(alt) for alt in term["games"]))
                    #result_text += ("This game is specific to: \n")
                    #result_text += ", ".join(str(game) for game in term["games"]) + "\n"

                # send the embedded message
                await message.channel.send(embed=embed)
            else: 
                await message.channel.send("No results found")

client.run(TOKEN)
