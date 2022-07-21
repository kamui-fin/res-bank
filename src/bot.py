"""
TODO
- Search command
    - By author, date ranges, text query, filter
- Import from bookmarks?
- Docs
"""

import discord
import os
import re
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
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
async def search(ctx, query: str, user: typing.Optional[discord.Member], limit: typing.Optional[int]):
    user_id = user.id if user else None
    records = db.get_submissions_by_query(query, user_id, limit)
    await send_paginated_submissions(ctx, records)

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
        # no success msg to avoid clogging up channel
        keywords, description, link = parse_submission(msg)
        seo_title, seo_desc = fetch_metadesc(link)
        db.insert_submission(','.join(keywords), link, message.author.id, description, seo_title, seo_desc)
    except (ValueError, SyntaxError) as e:
        await discord_send_error(message.channel, "Invalid format", "Invalid submission format. Must contain keyword(s) and URL OR attachment. Example: ```Python https://docs.python.org/3/tutorial/venv.html```", ERROR_COLOR)

# on ready
@bot.event
async def on_ready():
    print(f'\nlogged in as {bot.user} @{str(datetime.datetime.now())}')
    print(f'prefix: {PREFIX}\n')

bot.run(os.getenv('TOKEN'))

schedule.every().monday.do(backup)
