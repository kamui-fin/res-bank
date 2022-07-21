# Resource management Discord bot

This is a Discord bot for our server which is meant for centralized resource aggregation, management, and search. Saving useful and unique resources together as a group for various topics is now significantly easier with this bot. No more keeping track of arbitrary links buried across DMs.

## Features Overview

- Weekly backups of resource database
- On-demand export to CSV or JSON
- Submit links or attachments with keywords and an optional description
  - SEO data pulled for improved search results
- Batch import from a file of links
- Search using author and query filters
  - Custom limit option
  - Paginated 12 records per page using new interactions library
- Immutable records with a constant log of newly added submissions

## Installation

Pull the repository and install dependencies:

```
git clone https://github.com/kamui-fin/res-bank.git
cd res-bank
pip install -r requirements.txt
```

Add a `.env` file with the discord token for the bot. Make sure to replace `{token}` with your actual token.

```
echo "TOKEN={token}" >> .env
```

Run the bot:

```
python src/bot.py
```

## Commands

### Add submission

Adds a single submission to the resource database.

#### Format

```
"[keyword(s)]" "[description]" [link]
```

Keywords can be separated with any delimiter. Description and keywords must be wrapped within quotes, but the link should not be.
There is no specific command for this functionality, you can simply send a message with this format to the designated channel, like #submissions.

#### Example

```
"Programming" "Ask and view programming questions" https://stackoverflow.com/
```

### Import links

Batch imports resources to the database using a file of links.

#### Format

`>importlinks` with an attached text file. The file must include _only_ links on separate lines.

#### Example

![Example use case of importlinks](./screenshots/importlinks.png)

### Search

Sends a search query to the database given a set of parameters and returns the result. Limit must be a valid integer greater than 0.
Optional: `[user]` and `[limit]`. An empty query "" means no text filtering.

#### Format

```
>search "[query]" [user] [limit]
```

#### Example

![Example use case of search](./screenshots/search.png)

### Export

Exports a list of saved resources into a given filetype parameter (either json or csv).

#### Format

```
>export
```

#### Example

![Example use case of export](./screenshots/export.png)
