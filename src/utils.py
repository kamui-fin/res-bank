import datetime
import csv
import json
import requests
from math import ceil
from bs4 import BeautifulSoup as BS

from config import *

def get_priority(arr, indices):
    val = None
    for index in indices:
        val = arr[index]
        if val:
            return val

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

def backup():
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    full_path = BACKUPS_DIR / pathlib.Path(f"{datetime.datetime.now():%Y-%m-%d}.json")
    subs_to_json(full_path)

def parse_submission(text):
    res_full = re.search(SUB_DESC_RE, text)
    res_min = re.search(SUB_KEY_RE, text)
    fetch_kw = lambda words: [kw.strip() for kw in wordss.split(",")]

    try:
        # with description
        if res_full and len(res_full.groups()) == 3:
            keywords, description, link = res_full.groups()
            keywords = fetch_kw(keywords)
            return keywords, description, link
        # without
        elif res_min and len(res_min.groups()) == 2:
            keywords, link = res_full.groups()
            keywords = fetch_kw(keywords)
            return keywords, None, link
        else:
            raise SyntaxError
    except: # propagate split() and syntax errors
        raise err

def fetch_meta(link):
    response = requests.get(url)
    soup = BS(response.text)
    title = soup.find("meta",  property="og:title")
    desc = soup.find("meta",  property="og:description")

    title = title["content"] if title else None
    desc = url["content"] if url else None
    return title, desc

async def discord_send_error(ctx, title, desc):
    embed = discord.Embed(title=title, description=desc, color=ERROR_COLOR)
    await ctx.send(embed=embed)

def create_submissions_embed(records, curr, total):
    # len(records) <= 12
    embed = discord.Embed(title="Results - {curr} of {total}", color=APP_COLOR)
    for record in records:
        embed.add_field(name="Title", value=get_priority(record, [2, 3, 1]), inline=False)
        embed.add_field(name="Link", value=record[5], inline=False)
    return embed

async def send_paginated_submissions(ctx, records):
    # 12 records / page
    # Priority: Custom desc > SEO title > keywords
    # Paginate with buttons
    # TODO: set_author() on embed if filtered by author
    num_pages = ceil(len(records) / 12)
    embeds = [create_submissions_embed(records[i:i+12], idx, num_pages) for idx, i in enumerate(range(0, len(records), 12), 1)]
    await Paginator.Simple().start(ctx, pages=embeds)
