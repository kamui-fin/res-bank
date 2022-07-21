import pathlib

CSV_HEADERS = ['ID', 'Keywords', 'Description', 'SEO Title', 'SEO Description', 'URL', 'Author', 'Created On']
JSON_HEADERS = ["id", "keywords", 'description', 'meta_title', 'meta_description',  "url", "author", "created_on"]

PREFIX=">"

LINKS_CHANNEL_ID = 997609565334020156

APP_COLOR=0x4287f5
ERROR_COLOR=0xf54e42
SUCCESS_COLOR=0x63c771

BASE_DIR = pathlib.Path(__file__).parent.parent
BACKUPS_DIR = pathlib.Path("backups")

LINK_RE = "https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
SUB_DESC_RE = f"^['\"](.*)['\"]\s+['\"](.*)['\"]\s+{LINK_RE}"
SUB_KEY_RE = f"^['\"](.*)['\"]\s+{LINK_RE}"
