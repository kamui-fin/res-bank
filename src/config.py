import pathlib

CSV_HEADERS = ['ID', 'Keyword', 'URL', 'Author', 'Created On']
JSON_HEADERS = ["id", "keyword", "url", "author", "created_on"]

PREFIX=">"

LINKS_CHANNEL_ID = 997609565334020156

APP_COLOR=0x4287f5
ERROR_COLOR=0xf54e42
SUCCESS_COLOR=0x63c771

BASE_DIR = pathlib.Path(__file__).parent.parent
BACKUPS_DIR = pathlib.Path("backups")
