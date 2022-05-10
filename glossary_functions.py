import discord
import asyncio

# glossary index
# reference from https://stackoverflow.com/questions/61787520/i-want-to-make-a-multi-page-help-command-using-discord-py

async def glossary_index(message, g_index_pages, client):
    pages = len(g_index_pages)
    if '!glossaryindex' in message.content.lower().replace(" ", "") and len(message.content.lower().replace(" ", "")) > 14:
        msg_int = int("".join([str(page_num) for page_num in message.content[14::] if page_num.isdigit()]))
        print(msg_int)
        if msg_int > 0 and msg_int <= pages:
            cur_page = msg_int
        else:
            cur_page = 1
    elif '!gindex' in message.content.lower().replace(" ", "") and len(message.content.lower().replace(" ", "")) > 7:
        msg_int = int("".join([str(page_num) for page_num in message.content[7::] if page_num.isdigit()]))
        if msg_int > 0 and msg_int <= pages:
            cur_page = int(msg_int)
        else:
            cur_page = 1
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