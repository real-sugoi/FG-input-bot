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

def clean_text(text):
    #text = text.replace("'>", "__**")
    text = re.sub(r"(!<')([a-zA-Z0-9\/\ \.\-]+)'>", r"**__\2__**", text)
    text = re.sub("(!<')([a-zA-Z0-9\/\ \.\-]+)','([a-zA-Z0-9\/\ \.\-]+)'>", r" \3 (**__\2__**)", text)
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
    
    # glossary index
    # reference from https://stackoverflow.com/questions/61787520/i-want-to-make-a-multi-page-help-command-using-discord-py
    if "!gindex" in message.content.lower().replace(" ", "") or "!glossaryindex" in message.content.lower().replace(" ", ""):
        pages = len(g_index_pages)
        if '!glossaryindex' in message.content.lower().replace(" ", ""):
            msg_int = int("".join([str(page_num) for page_num in message.content[14::] if page_num.isdigit()]))
            print(msg_int)
            if msg_int > 0 and msg_int <= pages:
                cur_page = msg_int
        elif '!gindex' in message.content.lower().replace(" ", ""):
            msg_int = int("".join([str(page_num) for page_num in message.content[7::] if page_num.isdigit()]))
            if msg_int > 0 and msg_int <= pages:
                cur_page = int(msg_int)
        else: 
            cur_page = 1
        embed = discord.Embed(title="Page %i of %i" % (cur_page, pages), description=("\n".join(str(term) for term in g_index_pages[cur_page-1])), color=0x00adef)
        page = await message.channel.send(embed=embed)

        # getting the message object for editing and reacting

        await page.add_reaction("◀️")
        await page.add_reaction("▶️")

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    next_page = discord.Embed(title="Page %i of %i" % (cur_page, pages), description=("\n".join(str(term) for term in g_index_pages[cur_page-1])), color=0x00adef)
                    await page.edit(embed=next_page)
                    await page.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    next_page = discord.Embed(title="Page %i of %i" % (cur_page, pages), description=("\n".join(str(term) for term in g_index_pages[cur_page-1])), color=0x00adef)
                    await page.edit(embed=next_page)
                    await page.remove_reaction(reaction, user)

                else:
                    await page.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                break
                # ending the loop if user doesn't react after x seconds
        return

    # glossary search

    if '!g' in message.content or "!glossary" in message.content:
        if '!glossary' in message.content:
            search_words = message.content.lower().replace(" ", "")[9::]
        else: 
            search_words = message.content.lower().replace(" ", "")[2::]
        
        if scrape_mode:
            # non-functional atm
            scraper = infilScraper()
            result_text = scraper.search(message.content)
        else:
            result_found = False
            term = list(filter(lambda item: item['term'].lower().replace(" ", "") == search_words , glossary))
            #print(term)
            if term:
                term = term[0]
                result_found = True
            elif not term:
                for dict in glossary:
                    if "altterm" in dict:
                        if search_words  in (alt.lower().replace(" ", "")  for alt in dict["altterm"]):                    
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
                embed = discord.Embed(title=term["term"], color=0x00adef)

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
                    embed.add_field(name="Alternate Name(s): ", value=", ".join(str(alt) for alt in term["altterm"]), inline=False)

                if(hasJP):
                    embed.add_field(name="JP name(s): ", value=clean_text(term["jp"]), inline=False)
                embed.description = clean_text(term["def"])

                if(hasGameSpecific):
                    embed.add_field(name="Specific to: ", value=", ".join(str(alt) for alt in term["games"]), inline=True)

                # send the embedded message
                await message.channel.send(embed=embed)
            else: 
                await message.channel.send("No results found")

client.run(TOKEN)
