import discord
import os
import re
import csv
import json
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

LINK_RE = "(.*)\s+(https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))"
CSV_HEADERS = ['ID', 'Keyword', 'URL', 'Author', 'Created On']
JSON_HEADERS = ["id", "keyword", "url", "author", "created_on"]
PREFIX=">"
LINKS_CHANNEL_ID = 997609565334020156

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
        self.cur.execute("INSERT INTO submissions (keyword, url, author) VALUES (?, ?, ?)", (keywords, link, author))
        self.conn.commit()

    def get_submissions(self):
        self.cur.execute("SELECT * FROM submissions")
        return self.cur.fetchall()

    
class ExportEmbedView(discord.ui.View):
    def __init__(self, rows, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label='CSV', style=discord.ButtonStyle.green)
    async def export_csv(self, interaction: discord.Interaction, button: discord.ui.Button):
        rows = db.get_submissions()
        with open("temp.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            writer.writerows(rows)

        await interaction.response.send_message(file=discord.File("temp.csv"))

    @discord.ui.button(label='JSON', style=discord.ButtonStyle.red)
    async def export_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        rows = db.get_submissions()
        records = []
        for row in rows:
            record = {}
            for idx, val in enumerate(row):
                record[JSON_HEADERS[idx]] = val
            records.append(record)
        
        with open("temp.json", "w") as f:
            json.dump(records, f)

        await interaction.response.send_message(file=discord.File("temp.json"))

db = Database("data.db")

# commands
@bot.command()
async def export(ctx):
    await ctx.send("What format would you like?", view=ExportEmbedView(ctx))


# events
@bot.listen()
async def on_message(message):
    if message.author == bot.user or message.channel.id != LINKS_CHANNEL_ID or message.content.startswith(PREFIX):
        return

    results = re.search(LINK_RE, message.content)
    if not results or len(results.groups()) != 2:
        await message.channel.send("Invalid submission format. Must contain keyword(s) and URL. Example: Python https://realpython.com/how-to-make-a-discord-bot-python/")
    else:
        keywords, link = results.groups()
        db.insert_submission(keywords, link, message.author.id)

@bot.event
async def on_ready():
    print(f"Bot has logged in")

bot.run(os.getenv('TOKEN'))
