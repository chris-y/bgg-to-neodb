#!/usr/bin/python3
# Bgg to NeoDB by Chris Young 2024

import sys
import time
import xmltodict
import requests
import neodb
import argparse

def get_args():
  parser = argparse.ArgumentParser(description="BGG to NeoDB",
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("bgguser", help="BGG Username")
  parser.add_argument("-i", "--instance", help="NeoDB Instance", default="neodb.social")
  args = parser.parse_args()
  a = vars(args)

  return(a)

def get_bgg_collection(user):
  data = {"username": user,
          "own": 1,
          "excludesubtype": "boardgameexpansion"}
  r = requests.get(f'https://api.geekdo.com/xmlapi2/collection', params=data)

  #https://api.geekdo.com/xmlapi2/collection?username=chrisy&excludesubtype=boardgameexpansion&own=1

  while r.status_code != 200:
    if r.status_code in (500,503,202):
      print('waiting 5s for response')
      time.sleep(5)
      r = get_bgg_collection(user)
    else:
      print(f'unknown status getting collection {r.status_code}: {r.text}')
      sys.exit(1)

  return(r)

def get_bg(id):
  r = requests.get(f'https://api.geekdo.com/xmlapi/boardgame/{id}')

  while r.status_code != 200:
    if r.status_code in (500,503,202):
      print('waiting 5s for response')
      time.sleep(5)
      r = get_bg(id)
    else:
      print(f'unknown status getting boardgame {r.status_code}: {r.text}')
      sys.exit(1)

  return(r)

### start ###
a = get_args()

r = get_bgg_collection(a['bgguser'])
bgg_coll = xmltodict.parse(r.text)

app = neodb.register_app(a['instance'])
neodb.auth(app)

collections = neodb.collection_get(app)
uuid = None

if collections['count'] > 0:
  for c in collections['data']:
    if c['title'] == 'Board Games':
      uuid = c['uuid']

if uuid is None:
  print('No board games collection found, creating...')
  collection = neodb.collection_create(app, "Board Games", "Board Games imported from BGG", 2)
  uuid = collection['uuid']

for bg in bgg_coll['items']['item']:
  url = f'https://boardgamegeek.com/boardgame/{bg["@objectid"]}'
  print(f'Importing {url}')

  r = neodb.catalog_fetch(app, url)

  neodb.collection_add_item(app, uuid, r['uuid'])
