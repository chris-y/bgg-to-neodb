#!/usr/bin/python3
# NeoDB API, part of BGG to NeoDB by Chris Young 2024

import time
import requests
import json
import sys

def call_api_get(app, auth, endpoint, data):
  if auth is True:
    headers = {"Authorization": f'Bearer {app["access_token"]}'}
  else:
    headers = None
  r = requests.get(f'https://{app["instance"]}/api/{endpoint}', headers = headers, params=data)

  #print(data)
  #print(r.status_code)
  if(r.status_code == 202):
    print('  Waiting 15s for response...')
    time.sleep(15)
    r = call_api_get(app, auth, endpoint, data)
    return(r)

  return(r.json())

def call_api_post(app, auth, endpoint, data):
  if auth is True:
    headers = {"Authorization": f'Bearer {app["access_token"]}'}
  else:
    headers = None

  r = requests.post(f'https://{app["instance"]}/api/{endpoint}', headers = headers, json = data, allow_redirects = False)

  return(r.json())


def register_app(instance, cfgfile):
  try:
    with open(cfgfile) as f:
      app = json.load(f)
      if(app['instance'] != instance):
        print(f'Instance specified on command line ({instance}) does not match that where app is registered ({app["instance"]}).\nIf you want to change your instance please delete {cfgfile} or specify a different config with -c')
        sys.exit(1)
      return(app)
  except Exception as e:
    print(f'error reading app data: {e}')

  data = {"client_name": "BGG to NeoDB",
        "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
        "website": "https://github.com/chris-y/bgg-to-neodb"}

  r = requests.post(f'https://{instance}/api/v1/apps', json = data)

  app = r.json()
  app['instance'] = instance

  with open(cfgfile, 'w') as outfile:
    json.dump(app, outfile)

  return(app)

def auth(app, cfgfile):
  if 'access_token' in app:
    return

  print('Please visit the following URL and enter the code:')
  print(f'https://{app["instance"]}/oauth/authorize?response_type=code&client_id={app["client_id"]}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=read+write')
  app['code'] = input("Code:")

  data = {"client_id": app['client_id'],
          "client_secret": app['client_secret'],
          "code": app['code'],
          "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
          "grant_type": "authorization_code"}

  r = requests.post(f'https://{app["instance"]}/oauth/token', json = data)
  j = r.json()

  app['access_token'] = j['access_token']

  with open(cfgfile, 'w') as outfile:
    json.dump(app, outfile)


def me(app):
  return call_api_get(app, True, 'me', None)

def collection_create(app, title, brief, visibility):

  data = {"title": title,
          "brief": brief,
          "visibility": visibility}

  return call_api_post(app, True, 'me/collection/', data)

def collection_get(app):
  return call_api_get(app, True, 'me/collection/', None)

def collection_add_item(app, collection, item):
  data = {"item_uuid": item,
          "note": "Imported from BGG"}

  return call_api_post(app, True, f'me/collection/{collection}/item/', data)

def catalog_fetch(app, url):
  data = {"url": url}

  return call_api_get(app, False, 'catalog/fetch', data)

def mark_item(app, item, shelf, date):
  data = {"shelf_type": shelf,
          "visibility": 0,
          "created_time": f'{date}T00:00:00Z',
          "post_to_fediverse": 'false',
          "tags": ["boardgames"]}

  return call_api_post(app, True, f'me/shelf/item/{item}', data)
