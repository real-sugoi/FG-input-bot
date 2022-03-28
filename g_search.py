# bot.py

from unicodedata import name
import discord
import re

# web scraping
import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from discord.ext import commands


def clean_text(text):
    #text = text.replace("'>", "__**")
    text = re.sub(r"(!<')([a-zA-Z0-9\/\ \.\-]+)'>", r"**__\2__**", text)
    text = re.sub("(!<')([a-zA-Z0-9()\/\ \.\-]+)','([a-zA-Z0-9()\/\ \.\-]+)'>", r" \3 (**__\2__**)", text)
    text = text.replace("'>", "__**")
    text = re.sub("(?:<br>|</br>)", "\n", text)
    text = re.sub("(?:<[^\s]+>)", "", text)
    return text 

def clean_feet(text):
    text = re.sub(r"(!<')([a-zA-Z0-9\/\ \.\-]+)'>", r"\2}", text)
    text = re.sub("(!<')([a-zA-Z0-9()\/\ \.\-]+)','([a-zA-Z0-9()\/\ \.\-]+)'>", r"\3 (\2)", text)
    text = re.sub('(?:<a href="([^\s]+)">([^.]+)</a>)', r"\2 (\1)", text)
    return text


async def g_search(message, glossary, debug):
    if '!glossary' in message.content:
        search_words = message.content.lower()[10::]
    else: 
        search_words = message.content.lower()[3::]

    result_found = False
    term = list(filter(lambda item: item['term'].lower().replace(" ", "") == search_words.replace(" ", "") , glossary))
    #print(term)
    if term:
        term = term[0]
        result_found = True
    elif not term:
        for dict in glossary:
            if "altterm" in dict:
                if search_words.replace(" ", "") in (alt.lower().replace(" ", "")  for alt in dict["altterm"]):                    
                    term = dict
                    result_found = True
        if not result_found:
            for dict in glossary:
                if "def" in dict:
                    if search_words.replace(" ", "") in dict["def"].lower().replace(" ", ""):
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
        
        # replace embedded with underline to indicate more terms
        embed = discord.Embed(title=term["term"], color=0x00adef)
        footer = ""
        if(hasImage):
            embed.set_image(url=("https://glossary.infil.net/images/terms/" + term["term"].replace(" ", "%20") + "." + term["image"][0]))
            footer = clean_feet(term["image"][1])
        elif(hasVideo):
            # get the gif version cuz video embed doesn't work :(
            # this gif looks really bad thouuuuuughhhh T_T
            link = requests.get("https://gfycat.com/" + term["video"][0])
            soup = BeautifulSoup(link.content, 'html.parser')
            soup = soup.find(property="og:image")
            video = soup.get('content')
            embed.set_image(url=(video))
            footer = clean_feet(term["video"][1])

        if(hasAlt):
            embed.add_field(name="Alternate Name(s): ", value=", ".join(str(alt) for alt in term["altterm"]), inline=False)

        if(hasJP):
            embed.add_field(name="JP name(s): ", value=clean_text(term["jp"]), inline=False)
        embed.description = clean_text(term["def"])

        if(hasGameSpecific):
            embed.add_field(name="Specific to: ", value=", ".join(str(alt) for alt in term["games"]), inline=True)
        footer += "\n\n Data obtained from glossary.infil.net"
        embed.set_footer(text=footer)
        # send the embedded message
        await message.channel.send(embed=embed)
    else: 
        await message.channel.send("No results found")