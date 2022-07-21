"""
TODO
- Docs
"""

import sys
import discord
import os
import schedule
import typing
from discord.ext import commands
from dotenv import load_dotenv

from config import *
from utils import *
from db import Database

load_dotenv(BASE_DIR / '.env')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

class ExportEmbedView(discord.ui.View):
    @discord.ui.button(label='CSV', style=discord.ButtonStyle.green)
    async def export_csv(self, interaction: discord.Interaction, button: discord.ui.Button):
        subs_to_csv()
        await interaction.response.send_message(file=discord.File("temp.csv"))

    @discord.ui.button(label='JSON', style=discord.ButtonStyle.red)
    async def export_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        subs_to_json()
        await interaction.response.send_message(file=discord.File("temp.json"))

db = Database("data.db")

# commands

# export db to csv or json format
@bot.command()
async def export(ctx):
    embed = discord.Embed(title="Export Config", description="What format would you like?", color=APP_COLOR)
    await ctx.send(embed=embed, view=ExportEmbedView())

@bot.command()
async def search(ctx, query: str, user: typing.Optional[discord.Member], limit: typing.Optional[int] = 0):
    user_id = user.id if user else None
    records = db.get_submissions_by_query(query, user_id, limit)
    await send_paginated_submissions(ctx, records, user)

@bot.command()
async def importlinks(ctx, keywords: typing.Optional[str]):
    files = ctx.message.attachments
    if not files:
        await discord_send_error(ctx, "No file supplied", "Must supply a file containing a link on each line to import")
    else:
        file = files[0]

        file_request = requests.get(file.url)
        links = file_request.content.splitlines()
        author = ctx.message.author

        # TODO: optimize to batch insert
        count = 0
        for link in links:
            link = link.decode("utf-8")
            if not re.search(LINK_RE, link):
                continue

            try:
                seo_data = fetch_meta(link)
                seo_keywords, seo_title, seo_desc = seo_data["keywords"], seo_data["title"], seo_data["description"]
                
                id = db.insert_submission(keywords or seo_keywords or seo_title, link, author.id, "", seo_title, seo_desc)
                await post_submission_update(bot.get_channel(UPDATES_CHANNEL_ID), db, id, author)
                count += 1
            except:
                continue

        if count:
            embed = discord.Embed(title="Success", description=f"Successfully imported {count} entries", color=SUCCESS_COLOR)
            await ctx.send(embed=embed)
        else:
            await discord_send_error(ctx, "Error", "Could not import any entries from file")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Documentation", description=f"https://github.com/kamui-fin/res-bank/blob/main/README.md", color=APP_COLOR)
    await ctx.send(embed=embed)

# events

# on submit to #links, add to db
@bot.listen()
async def on_message(message):
    if message.author == bot.user or message.channel.id != LINKS_CHANNEL_ID or message.content.startswith(PREFIX):
        return

    msg = message.content.strip()
    if message.attachments:
        msg += f" {message.attachments[0].url}"

    try:
        keywords, description, link = parse_submission(msg)
        seo_data = fetch_meta(link)
        seo_keywords, seo_title, seo_desc = seo_data["keywords"], seo_data["title"], seo_data["description"]
        
        id = db.insert_submission(keywords or seo_keywords or seo_title, link, message.author.id, description, seo_title, seo_desc)
        await post_submission_update(bot.get_channel(UPDATES_CHANNEL_ID), db, id, message.author)
        embed = discord.Embed(title="Success", description=f"Successfully added entry", color=SUCCESS_COLOR)
        await message.channel.send(embed=embed)
    except (ValueError, SyntaxError):
        await discord_send_error(message.channel, "Invalid format", "Invalid submission format. Must contain keyword(s), an optional description, and URL OR attachment. Example: ```'Python Documentation' 'Useful resource for learning about venv'  https://docs.python.org/3/tutorial/venv.html```")
    except Exception as e:
        await discord_send_error(message.channel, "Internal Server Error", "Unable to register submission. Please report this to the admin")

# on ready
@bot.event
async def on_ready():
    print(f'\nlogged in as {bot.user} @{str(datetime.datetime.now())}')
    print(f'prefix: {PREFIX}\n')

token = os.getenv('TOKEN')
if not token:
    sys.exit("Must set a token in .env to run bot")

bot.run(token)

schedule.every().monday.do(backup)
