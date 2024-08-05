#!/usr/bin/python3
# Bgg to NeoDB by Chris Young 2024

import os
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
  parser.add_argument("-c", "--configfile", help="Config filename", default="~/.config/bgg-to-neodb.json")
  parser.add_argument("-b", "--boardgames", help="Import boardgames to NeoDB collection", action="store_true")
  parser.add_argument("-p", "--plays", help="Import plays to NeoDB", action="store_true")
  args = parser.parse_args()
  a = vars(args)

  return(a)

def get_bgg_coll(user):
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

  return r

def get_bgg_collection(user):
  r = get_bgg_coll(user)
  return xmltodict.parse(r.text)

def get_plays(user):
  data = { "username": user } # mindate=2024-MM-DD
  r = requests.get(f'https://boardgamegeek.com/xmlapi2/plays', params = data)
  # gets 1 page, check total
  return xmltodict.parse(r.text)

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

def neodb_lookup_bgg_item(app, id):
    url = f'https://boardgamegeek.com/boardgame/{id}'
    print(f'Lookup for {url}')

    return neodb.catalog_fetch(app, url)

def bgg_to_neodb_collection(user, app):
  bgg_coll = get_bgg_collection(user)
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

  i = 0
  t = len(bgg_coll['items']['item'])

  for bg in bgg_coll['items']['item']:
    i += 1
    print(f'importing {i} of {t}')
    r = neodb_lookup_bgg_item(app, bg['@objectid'])
    neodb.collection_add_item(app, uuid, r['uuid'])

def bgg_to_neodb_plays(user, app):
  bgg_plays = get_plays(a['bgguser'])['plays']
  print(f'{bgg_plays["@page"]}/{bgg_plays["@total"]}')

  for play in bgg_plays['play']:
    r = neodb_lookup_bgg_item(app, play['item']['@objectid'])
    item = r['uuid']
    neodb.mark_item(app, item, 'progress', play['@date'])
    neodb.mark_item(app, item, 'complete', play['@date'])

### start ###
a = get_args()

cfgfile = os.path.expanduser(a['configfile'])
app = neodb.register_app(a['instance'], cfgfile)
neodb.auth(app, cfgfile)

if a['boardgames'] is True:
  print('Importing boardgames collection')
  print('-------------------------------')
  bgg_to_neodb_collection(a['bgguser'], app)

if a['plays'] is True:
  print('Importing plays')
  print('---------------')
  bgg_to_neodb_plays(a['bgguser'], app)
