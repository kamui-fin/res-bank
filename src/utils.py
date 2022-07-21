import datetime
import csv
import json
import requests
from bs4 import BeautifulSoup as BS

from config import *

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

def fetch_metadesc(link):
    response = requests.get(url)
    soup = BS(response.text)
    metas = soup.find_all('meta')
    return ' '.join([meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description'])

def discord_send_error(ctx, title, desc):
    embed = discord.Embed(title=title, description=desc, color=ERROR_COLOR)
    await ctx.send(embed=embed)
