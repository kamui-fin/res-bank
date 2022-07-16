"""
TODO
- Description for better filtering
- Use SEO metadata from URLs for search
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

load_dotenv()

LINK_RE = "(.*)\s+(https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))"
CSV_HEADERS = ['ID', 'Keyword', 'URL', 'Author', 'Created On']
JSON_HEADERS = ["id", "keyword", "url", "author", "created_on"]

PREFIX=">"
LINKS_CHANNEL_ID = 997609565334020156
BACKUPS_DIR = pathlib.Path("backups")

APP_COLOR=0x4287f5
ERROR_COLOR=0xf54e42
SUCCESS_COLOR=0x63c771

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

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()
    
    def insert_submission(self, keyword, url, author):
        self.cur.execute("INSERT INTO submissions (keyword, url, author) VALUES (?, ?, ?)", (keyword, url, author))
        self.conn.commit()
    
    def remove_submission(self, url):
        self.cur.execute("DELETE FROM submissions WHERE url = ?", (url))
        self.conn.commit()

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
    embed = discord.Embed(title="Export Config", description="What format would you like?", color=APP_COLOR)
    await ctx.send(embed=embed, view=ExportEmbedView())

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
        embed = discord.Embed(title="Invalid format", 
                    description='''Invalid submission format. Must contain keyword(s) and URL OR attachment. Example: ```Python https://docs.python.org/3/tutorial/venv.html```''', 
                    color=ERROR_COLOR)
         
        await message.channel.send(embed=embed)
    else:
        keywords, link = results.groups()
        
        embed = discord.Embed(title="Success", 
                    description=(f'Successfully added <{link}> to the resource database.'), 
                    color=SUCCESS_COLOR)
        
        await message.channel.send(embed=embed)
        db.insert_submission(keywords, link, message.author.id)

# on ready
@bot.event
async def on_ready():
    print(f'\nlogged in as {bot.user} @{str(datetime.datetime.now())}')
    print(f'prefix: {PREFIX}\n')

bot.run(os.getenv('TOKEN'))

# setup automatic weekly backups
def job():
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    full_path = BACKUPS_DIR / pathlib.Path(f"{datetime.datetime.now():%Y-%m-%d}.json")
    subs_to_json(full_path)

schedule.every().monday.do(job)
