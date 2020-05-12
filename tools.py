from os.path import isfile
from bs4 import BeautifulSoup as BS
from importlib import import_module

profile = input('Profile: ')
params = import_module('profiles.' + profile)

ANKI_USER = params.ANKI_USER
DECK_NAME = params.DECK_NAME
NOTE_TYPE = params.NOTE_TYPE
NOT_FOUND_PATH = params.NOT_FOUND_PATH
PONS_KEY = params.PONS_KEY
getmarkings = params.getmarkings


DONE_PATH = '.donemarkings_' + ANKI_USER + '.txt'


def dispreport(marking, entry, show):
    msg = None
    if show == 'notfound' and not entry['ankinotes']:
        lemmaposes = []
        if entry['lemmaposes']:
            for lemma, pos in entry['lemmaposes']:
                lemmaposes.append('(' + lemma + ', ' + pos + ')')
        else:
            lemmaposes = ['(No lemma found in ZMORGE)']
        msg = marking + ' ' + ', '.join(lemmaposes)
        print('Nothing found for:', msg)

    else:
        for n in entry['ankinotes']:
            de = BS(n['DE'], features="lxml").text
            de = de.replace('\n', '').strip()
            en = BS(n['EN'], features="lxml").text
            en = en.replace('\n', '').strip()
            if show == 'added' and n['couldadd']:
                print(marking, '==>', de, ':', en)
            if show == 'couldntadd' and not n['couldadd']:
                print('Could not add note: ', marking, '==>', de, ':', en)

    return msg


def writetolog(maindict):
    with open(DONE_PATH, mode='a', encoding='utf8') as donefile:
        for marking in maindict:
            donefile.write(marking + '\n')  # add all markings to log
            dispreport(marking, maindict[marking], 'added')  # display added notes

    with open(NOT_FOUND_PATH, mode='a', encoding='utf8') as notfoundfile:
        for marking in maindict:
            if not maindict[marking]['ankinotes']:
                msg = dispreport(marking, maindict[marking], 'notfound')  # dsiplay not found markings
                notfoundfile.write(msg + '\n')  # add not found markings to notfound log

    for marking in maindict:
        dispreport(marking, maindict[marking], 'couldntadd')  # display couldntadd markings


def readlog():
    if isfile(DONE_PATH):
        with open(DONE_PATH, mode='r', encoding='utf8') as logfile:
            return [row.rstrip('\n') for row in logfile if row.rstrip('\n')]
    return []


def basiccleanup(st):
    # remove non-text characters:
    original_st = st
    st = ''
    for c in original_st:
        if c.isalpha() or c == '-':
            st = st + c
        if c.isspace():
            st = st + ' '
    # remove non-letters/lonely letters from edges:
    while not st[0:2].isalpha():
        st = st[1::]
    while not st[-2::].isalpha():
        st = st[:-1:]
    # make space series to single space
    while ' ' + ' ' in st:
        st = st.replace(' ' + ' ', ' ')
    return st


def removedups(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
