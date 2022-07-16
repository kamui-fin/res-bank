import discord
import os
import re
import csv
import json
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

link_re = "(.*)\s+(https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))"
csv_headers = ['ID', 'Keyword', 'URL', 'Author', 'Created On']
json_header = ["id", "keyword", "url", "author", "created_on"]

conn = sqlite3.connect("data.db")
cur = conn.cursor()
cur.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                author INTEGER NOT NULL,
                created_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
            ''')

class ExportEmbedView(discord.ui.View):
    def __init__(self, rows, ctx):
        super().__init__()
        self.rows = rows
        self.ctx = ctx

    @discord.ui.button(label='CSV', style=discord.ButtonStyle.green)
    async def export_csv(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("temp.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            writer.writerows(self.rows)

        await interaction.response.send_message(file=discord.File("temp.csv"))

    @discord.ui.button(label='JSON', style=discord.ButtonStyle.red)
    async def export_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        records = []
        for row in self.rows:
            record = {}
            for idx, val in enumerate(row):
                record[json_header[idx]] = val
            records.append(record)
        
        with open("temp.json", "w") as f:
            json.dump(records, f)

        await interaction.response.send_message(file=discord.File("temp.json"))

@bot.event
async def on_ready():
    print(f"Bot has logged in")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def export(ctx):
    cur.execute("SELECT * FROM submissions")
    rows = cur.fetchall()
    await ctx.send("What format would you like?", view=ExportEmbedView(rows, ctx))

@bot.listen()
async def on_message(message):
    if message.author == bot.user or message.channel.id != 997609565334020156 or message.content.startswith(">"):
        return

    results = re.search(link_re, message.content)
    if not results or len(results.groups()) != 2:
        await message.channel.send("Invalid submission format. Must contain keyword(s) and URL. Example: Python https://realpython.com/how-to-make-a-discord-bot-python/")
    else:
        keywords, link = results.groups()
        cur.execute("INSERT INTO submissions (keyword, url, author) VALUES (?, ?, ?)", (keywords, link, message.author.id))
        conn.commit()

bot.run(os.getenv('TOKEN'))
