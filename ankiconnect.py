import json
import urllib.request
import subprocess
from time import sleep

from constants import ANKI_USER, DECK_NAME

NOTE_TYPE = 'vomBuchInAnki Note'
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


def createnotetype():  # Creates the note type of the generated notes
    if NOTE_TYPE in invoke('modelNames'):
        return

    p = {'modelName': NOTE_TYPE, 'inOrderFields': ['DE', 'DE Info', 'Sense', 'EN', 'Examples', 'Marking']}
    p['css'] = '.card{\nfont-family:arial;\nfont-size:20px;\ntext-align:center;\ncolor:black;\nbackground-color:white;}'
    p['css'] += '\n\n.case{\nvertical-align:super;\nfont-style:italic;\nfont-size:80%;}\n\n'
    for cl in ['topic', 'genus', 'info', 'style', 'rhetoric', 'region']:
        p['css'] += '\n.' + cl + '{font-style: italic;}'

    p['cardTemplates'] = [{}, {}]
    p['cardTemplates'][0]['Front'] = '{{DE}}<i>{{DE Info}}</i>'
    p['cardTemplates'][0]['Back'] = '{{FrontSide}}'
    p['cardTemplates'][0]['Back'] += '\n<hr id=answer>'
    p['cardTemplates'][0]['Back'] += '\n{{Sense}}<br>'
    p['cardTemplates'][0]['Back'] += '\n{{EN}}'
    p['cardTemplates'][0]['Back'] += '\n<br><br>'
    p['cardTemplates'][0]['Back'] += '\n<small>{{Examples}}</small>'
    p['cardTemplates'][1]['Front'] = '{{Sense}}<br>{{EN}}'
    p['cardTemplates'][1]['Back'] = '{{FrontSide}}'
    p['cardTemplates'][1]['Back'] += '\n<hr id=answer>'
    p['cardTemplates'][1]['Back'] += '\n{{DE}}<i>{{DE Info}}</i>'
    p['cardTemplates'][1]['Back'] += '\n<br><br>'
    p['cardTemplates'][1]['Back'] += '\n<small>{{Examples}}</small>'

    invoke('createModel', **p)


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
    createnotetype()
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
