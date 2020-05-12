import json
import urllib.request
import subprocess
from time import sleep

from tools import *


NOTE_TYPE = "DE-EN"
ANKI_APP = None


def request(action, **params):  # from AnkiConnect's page
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):  # from AnkiConnect's page
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def runanki():
    global ANKI_APP
    if ANKI_APP is None or ANKI_APP.poll() is not None:
        ANKI_APP = subprocess.Popen(['anki', '-p', ANKI_USER])
        sleep(5)
        invoke('sync')


def closeanki():
    global ANKI_APP
    if ANKI_APP is not None and ANKI_APP.poll() is None:
        ANKI_APP.terminate()


def formatnote(n):
    return {'deckName': DECK_NAME, "modelName": NOTE_TYPE, 'fields': n,
            "options": {"allowDuplicate": False, "duplicateScope": "collection"}, 'tags': []}


def addnotes(maindict):
    runanki()
    notesarray = []
    invoke('createDeck', deck=DECK_NAME)
    for marking in maindict:
        for n in maindict[marking]['ankinotes']:
            n.update({'Marking': marking})
            notesarray.append(formatnote(n))

    canaddnote = invoke('canAddNotes', notes=notesarray)
    added = [item for i, item in enumerate(notesarray) if canaddnote[i]]
    resadded = invoke('addNotes', notes=added)
    invoke('sync')
    added = [item for i, item in enumerate(added) if resadded[i] is not None]
    sleep(5)

    for marking in maindict:
        for n in maindict[marking]['ankinotes']:
            n.update({'couldadd': formatnote(n) in added})

    closeanki()

    return maindict

