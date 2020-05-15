from os.path import isfile
from bs4 import BeautifulSoup as BS

from constants import getmarkings, DONE_PATH, NOT_FOUND_PATH
from zmorge import lemmatize
from pons import generateankinotes
from ankiconnect import addnotes


def markings2cards():
    print('Fetching markings...')
    markings = getmarkings()
    current_notes = readlog()
    markings = [marking for marking in markings if marking not in current_notes]
    if not markings:
        print('All markings fetched have already been processed.')
        return

    print('Looking up lemmata in ZMORGE...')
    maindict = lemmatize(markings)  # maindict[marking] has: clean, terms, lemmaposes
    print('Querying translations from PONS...')
    generateankinotes(maindict)  # maindict[marking] is added: termposes, ankinotes
    print('Uploading to Anki...')
    print()
    addnotes(maindict)  # maindict[marking]['ankinotes'] is added: Marking, couldadd
    print()
    print('Done:')
    writetolog(maindict)  # Print results and write them to log


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
            de = BS(n['DE'], features="html.parser").text
            de = de.replace('\n', '').strip()
            en = BS(n['EN'], features="html.parser").text
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


if __name__ == "__main__":
    markings2cards()
