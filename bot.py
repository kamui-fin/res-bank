"""
TODO
- Description for better filtering
- Use SEO metadata from URLs for search
- Embeds instead of regular plain-text
- Search command
    - By author, date ranges, text query, filter
- Docs
- Import from bookmarks?
"""

import discord
import os
import re
import csv
import json
import sqlite3
import schedule
import pathlib
import datetime
from discord.ext import commands
from dotenv import load_dotenv

LINK_RE = "(.*)\s+(https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))"
CSV_HEADERS = ['ID', 'Keyword', 'URL', 'Author', 'Created On']
JSON_HEADERS = ["id", "keyword", "url", "author", "created_on"]
PREFIX=">"
LINKS_CHANNEL_ID = 997609565334020156
BACKUPS_DIR = pathlib.Path("backups")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()
        self.initialize_tables()
    
    def initialize_tables(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                author INTEGER NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        ''')

    def insert_submission(self, keyword, url, author):
        self.cur.execute("INSERT INTO submissions (keyword, url, author) VALUES (?, ?, ?)", (keyword, url, author))
        self.conn.commit()

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()

def subs_to_csv(filename = "temp.csv"):
    rows = db.get_submissions()
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)

def subs_to_json(filename = "temp.json"):
    rows = db.get_submissions()
    records = []
    for row in rows:
        record = {}
        for idx, val in enumerate(row):
            record[JSON_HEADERS[idx]] = val
        records.append(record)
    
    with open(filename, "w") as f:
        json.dump(records, f)

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
@bot.command()
async def export(ctx):
    await ctx.send("What format would you like?", view=ExportEmbedView())

# events
@bot.listen()
async def on_message(message):
    if message.author == bot.user or message.channel.id != LINKS_CHANNEL_ID or message.content.startswith(PREFIX):
        return

    msg = message.content
    if message.attachments:
        msg += f" {message.attachments[0].url}"

    results = re.search(LINK_RE, msg)
    if not results or len(results.groups()) != 2:
        await message.channel.send("Invalid submission format. Must contain keyword(s) and URL OR attachment. Example: Python <https://realpython.com/how-to-make-a-discord-bot-python/>")
    else:
        keywords, link = results.groups()
        db.insert_submission(keywords, link, message.author.id)

@bot.event
async def on_ready():
    print(f"Bot has logged in")

bot.run(os.getenv('TOKEN'))

# setup automatic weekly backups
def job():
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    full_path = BACKUPS_DIR / pathlib.Path(f"{datetime.datetime.now():%Y-%m-%d}.json")
    subs_to_json(full_path)

schedule.every().monday.do(job)
