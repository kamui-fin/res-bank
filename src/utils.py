import datetime
import csv
import json

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
