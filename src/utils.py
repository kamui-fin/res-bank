import discord
import datetime
import csv
import json
import re
import requests
import Paginator
from math import ceil
from bs4 import BeautifulSoup as BS

from config import *

def get_priority(entry, attributes):
    val = None
    for attr in attributes:
        val = getattr(entry, attr)
        if val:
            return val

def subs_to_csv(filename = "temp.csv"):
    rows = [list(row) for row in db.get_submissions()]
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)

def subs_to_json(filename = "temp.json"):
    rows = db.get_submissions()
    records = []
    for row in rows:
        record = {}
        for idx, val in enumerate(list(row)):
            record[JSON_HEADERS[idx]] = val
        records.append(record)
    
    with open(filename, "w") as f:
        json.dump(records, f)

def backup():
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    full_path = BACKUPS_DIR / pathlib.Path(f"{datetime.datetime.now():%Y-%m-%d}.json")
    subs_to_json(full_path)

def parse_submission(text):
    res_full = re.search(SUB_DESC_RE, text)
    res_min = re.search(SUB_KEY_RE, text)
    fetch_kw = lambda words: [kw.strip() for kw in words.split(",")]

    try:
        # with description
        if res_full and len(res_full.groups()) == 3:
            keywords, description, link = res_full.groups()
            keywords = fetch_kw(keywords)
            return keywords, description, link
        # without
        elif res_min and len(res_min.groups()) == 2:
            keywords, link = res_min.groups()
            keywords = fetch_kw(keywords)
            return keywords, None, link
        else:
            raise SyntaxError
    except: # propagate split() and syntax errors
        raise

def fetch_meta(link):
    response = requests.get(link)
    soup = BS(response.text, features="html.parser")
    title = soup.find("meta",  property="og:title")
    desc = soup.find("meta",  property="og:description")

    title = title["content"] if title else None
    desc = desc["content"] if desc else None
    return title, desc

async def discord_send_error(ctx, title, desc):
    embed = discord.Embed(title=title, description=desc, color=ERROR_COLOR)
    await ctx.send(embed=embed)

def create_submissions_embed(records, author):
    # len(records) <= 12
    embed = discord.Embed(title=f"Search Results", color=APP_COLOR)
    for record in records:
        embed.add_field(name=record.link, value=get_priority(record, ["description", "meta_description", "meta_title", "keywords"]), inline=False)
        if author:
            embed.set_author(name=author.name, icon_url=author.avatar.url)
    return embed

async def send_paginated_submissions(ctx, records, user):
    # 12 records / page
    # Priority: Custom desc > SEO description > SEO title > keywords
    embeds = [create_submissions_embed(records[i:i+12], user) for i in range(0, len(records), 12)]
    if not embeds:
        await discord_send_error(ctx, "No results", "Unable to find submissions matching criteria")
    else:
        await Paginator.Simple().start(ctx, pages=embeds)

async def post_submission_update(channel, db, id, author):
    submission = db.get_submission_by_id(id)
    if submission:
        embed = discord.Embed(title=submission.url, description=get_priority(submission, ["description", "meta_description", "meta_title", "keywords"]), color=APP_COLOR)
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await channel.send(embed=embed)
