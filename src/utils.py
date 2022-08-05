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

def subs_to_csv(db, filename = "temp.csv"):
    rows = [list(row) for row in db.get_submissions()]
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)

def subs_to_json(db, filename = "temp.json"):
    rows = db.get_submissions()
    records = []
    for row in rows:
        record = {}
        for idx, val in enumerate(list(row)):
            record[JSON_HEADERS[idx]] = val
        records.append(record)
    
    with open(filename, "w") as f:
        json.dump(records, f)

def backup(db):
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    full_path = BACKUPS_DIR / pathlib.Path(f"{datetime.datetime.now():%Y-%m-%d}.json")
    subs_to_json(db, full_path)

def parse_submission(text):
    res_full = re.search(SUB_DESC_RE, text)
    res_min = re.search(SUB_KEY_RE, text)
    try:
        # with description
        if res_full and len(res_full.groups()) == 3:
            keywords, description, link = res_full.groups()
            return keywords, description, link
        # without
        elif res_min and len(res_min.groups()) == 2:
            keywords, link = res_min.groups()
            return keywords, None, link
        else:
            raise SyntaxError
    except: # propagate split() and syntax errors
        raise

def fetch_meta(link):
    response = requests.get(link)
    soup = BS(response.text, features="html.parser")

    page_title = soup.find("title")
    page_title = page_title.string if page_title else None

    page_desc = soup.find("meta", attrs={'name': 'description'})
    page_desc = page_desc.content if page_desc else None

    page_keywords = soup.find("meta", attrs={'name': 'keywords'})
    page_keywords = page_keywords.content if page_keywords else None

    og_title = soup.find("meta",  property="og:title")
    og_title = og_title.content if og_title else None

    og_desc = soup.find("meta",  property="og:description")
    og_desc = og_desc.content if og_desc else None

    return {
        "title": og_title or page_title,
        "description": og_desc or page_desc,
        "keywords": page_keywords
    }

async def discord_send_error(ctx, title, desc):
    embed = discord.Embed(title=title, description=desc, color=ERROR_COLOR)
    await ctx.send(embed=embed)

def create_submissions_embed(records, author, title="Search Results"):
    # len(records) <= 12
    embed = discord.Embed(title=title, color=APP_COLOR)
    for record in records:
        embed.add_field(name=record.url, value=get_priority(record, ["description", "meta_description", "meta_title", "keywords"]), inline=False)
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

async def post_submissions_update(channel, db, ids, author):
    records = db.get_submissions_from_ids(ids)
    embeds = [create_submissions_embed(records[i:i+12], author, "Bulk Inserts") for i in range(0, len(records), 12)]
    if embeds:
        await Paginator.Simple().start(channel, pages=embeds)
