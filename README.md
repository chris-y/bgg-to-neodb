# BGG to NeoDB

This is a simple script which currently has one function: It imports a user's board game collection from BoardGameGeek, into a collection on NeoDB.

You can add the required modules to Python with `pip -r requirements.txt` before running.

Usage:
```
python3 bgg.py --instance=neodb.social -p -b bgguser
```

The instance can be specified using `--instance` (or `-i`).  The bgguser is required - this will be your username on BGG. 

## `-b` - this imports your collection
A collection on NeoDB called "Board Games" will be created if it does not exist.  If it does exist it will be updated.  **If you don't want your BGG collection imported into an existing Board Games collection on NeoDB, please rename it first before running this script!**

The Board Games collection will be set as private when it is created.  This can be changed in the NeoDB interface later.

Only board games set as "owned" will be imported.  Expansions are never imported.

This can take many hours to run if the games are not known to your NeoDB instance, as the API requires a minimum 15 second delay to fetch from BGG.

## `-p` - this imports your plays
Imported plays are set as "public"

Played games will be tagged with #boardgames - this shows as a personal tag but can be made public through the web interface.

Note that any existing comments and tags associated with marks get overwritten/wiped.

