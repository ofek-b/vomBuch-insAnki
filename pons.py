import requests
import urllib
import json
import os
from os.path import isfile, join
from bs4 import BeautifulSoup as BS

from constants import PONS_KEY, NOTCODE_DIR

BASE_URL = 'https://api.pons.com/v1/dictionary?'
HISTORY_PATH = join(NOTCODE_DIR, 'pons_responses_history.json')


def generateankinotes(maindict):
    allterms = []
    for marking in maindict:
        maindict[marking]['termposes'] = maindict[marking]['lemmaposes'].copy()
        if len(maindict[marking]['clean'].split()) > 1 or not maindict[marking]['termposes']:
            maindict[marking]['termposes'].append((maindict[marking]['clean'], ''))
        allterms.extend([termpos[0] for termpos in maindict[marking]['termposes']])

    responses = query(allterms)

    for marking in maindict:
        maindict[marking]['ankinotes'] = []
        for term, pos in maindict[marking]['termposes']:
            ankinote = makenote(responses[term], term, pos)
            if ankinote['DE'] and ankinote not in maindict[marking]['ankinotes']:
                maindict[marking]['ankinotes'].append(ankinote)


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


def makenote(data, term, pos):
    if not data: return {'DE': ''}

    # extract the roms and lonely translations out of the raw json received:
    roms = []
    lonely_translations = []
    for hit in data[0]['hits']:
        if hit['type'] == 'entry':
            roms.extend(hit['roms'])
        elif hit['type'] == 'translation':
            lonely_translations.append({'source': hit['source'], 'target': hit['target']})
        else:
            raise Exception('error, check that ref=false')

    # parse every translation into a dictionary containing all relevant infos:
    notenominees = []
    for rom in roms:
        for arab in rom['arabs']:
            for trans in arab['translations']:
                notenominees.append(parse(rom, arab, trans, term, pos))

    if not roms and len(term.split()) > 1:  # idiom
        for trans in lonely_translations:
            notenominees.append(parse(None, None, trans, term, pos))

    # pick the right nominee and make the ankinote:
    egs = [nn for nn in notenominees if 'example' == nn['transtype'] or 'full_collocation' == nn['transtype']]
    srtd = []
    if pos == 'Verb':
        srtd = [nn for nn in notenominees if 'grammatical_construction' == nn['transtype']]
    srtd += [nn for nn in notenominees if nn not in srtd and nn not in egs]
    srtd = [nn for nn in srtd if nn['fit']]

    examples = ''
    if srtd:
        nn = srtd[0]
        egs = [eg for eg in egs if nn['arab'] == eg['arab']] + [eg for eg in egs if nn['rom'] == eg['rom']]
        if egs and not nn['lonely']:
            examples = egs[0]['source'] + '<br>' + egs[0]['target']
    else:
        nn = egs[0]

    return {'DE': nn['source'], 'DE Info': nn['info'], 'Sense': nn['sense'], 'EN': nn['target'], 'Examples': examples}


def parse(rom, arab, trans, term, pos):
    lonely = rom is None
    nn = {'headwords': [], 'wordclass': None, 'info': '', 'sense': '', 'source': '', 'source_text': '',
          'target': '', 'transtype': '', 'ankinote': {}, 'fit': None, 'lonely': lonely, 'rom': rom, 'arab': arab}

    trans_soup = BS(trans['source'], features="html.parser")
    if not lonely:
        rom_soup = BS(rom['headword_full'], features="html.parser")
        arab_soup = BS(arab['header'], features="html.parser")

    # headwords:
    if not lonely:
        nn['headwords'].append(''.join(filter(lambda x: x.isalpha() or x in ['-', ' ', ','], rom['headword'])))

        arab_headword = ''
        if arab_soup.find_all(text=True):
            arab_headword = str(arab_soup.find_all(text=True)[0])
        if len(arab_headword) >= 3 and arab_headword[0].isdigit() and arab_headword[1] == '.' \
                and arab_headword[2].isspace():
            arab_headword = arab_headword[3::]
        nn['headwords'].append(arab_headword.strip())

    # wordclass:
    if not lonely:
        nn['wordclass'] = rom['wordclass']

    # info:
    info = []
    if not lonely:
        for cl in ['genus', 'info' 'topic', 'rhetoric', 'style']:
            info += rom_soup.find_all('span', {'class': cl})
            info += arab_soup.find_all('span', {'class': cl})
        nn['info'] = ', '.join([str(x) for x in removedups(info)])
        if nn['info']:
            nn['info'] = '&nbsp;&nbsp;&nbsp;' + nn['info']

    # sense:
    sense = trans_soup.find_all('span', {'class': 'sense'})
    if not lonely:
        sense += rom_soup.find_all('span', {'class': 'sense'})
        sense += arab_soup.find_all('span', {'class': 'sense'})
    nn['sense'] = ', '.join([str(x) for x in removedups(sense)])

    # source:
    nn['source'] = trans['source']
    for s in trans_soup.find_all('span', {'class': 'sense'}):
        nn['source'] = nn['source'].replace(str(s), '')

    # source_text:
    nn['source_text'] = BS(nn['source'], features="html.parser").text

    # target:
    nn['target'] = trans['target']

    # transtype:
    for transtype in ['example', 'full_collocation', 'grammatical_construction']:
        if trans_soup.find_all('span', {'class': transtype}):
            nn['transtype'] = transtype

    # fit:
    if not lonely:
        posmatches = not pos or (nn['wordclass'] is not None and pos in nn['wordclass'])
        lemmamatches = term and term in nn['headwords']
        nn['fit'] = posmatches and lemmamatches
    else:
        nn['fit'] = term in nn['source_text']

    return nn


def removedups(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
