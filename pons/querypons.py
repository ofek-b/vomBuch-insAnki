import requests
import urllib
import json
import os

from tools import *


BASE_URL = 'https://api.pons.com/v1/dictionary?'
HISTORY_PATH = join(dirname(__file__), 'responses_history.json')


def query(terms):
    history = {}
    if isfile(HISTORY_PATH) and os.stat(HISTORY_PATH).st_size:
        with open(HISTORY_PATH, 'r') as jsonfile:
            history = json.load(jsonfile)

    newterms = [term for term in terms if term not in history]
    for term in newterms:
        term_es = urllib.parse.quote_plus(term)
        url = BASE_URL + 'q=' + term_es + '&l=deen' + '&in=de' + '&ref=false&language=de'
        headers = {'X-Secret': PONS_KEY}
        r = requests.get(url, headers=headers)
        history[term] = []
        if r.text:
            history[term] = r.json()

    # save to history:
    if newterms:
        with open(HISTORY_PATH, 'w') as jsonfile:
            json.dump(history, jsonfile, sort_keys=True, indent=4)

    return {term: history[term] for term in terms}


def getroms(data):
    if isinstance(data, dict):
        if 'hits' in data:
            hits = data['hits']
        else:
            hits = 'Received dict without a key "hits"'
    if isinstance(data, list):
        if not data:
            hits = 'No Data Received'
        else:
            hits = data[0]['hits']

    if isinstance(hits, str):
        return hits, hits

    allroms = []
    lonely_translations = []
    for hit in hits:
        if hit['type'] == 'entry':
            allroms.extend(hit['roms'])
        elif hit['type'] == 'translation':
            lonely_translations.append({'source': hit['source'], 'target': hit['target']})
        else:
            print('error, check that ref=false')

    return allroms, lonely_translations
