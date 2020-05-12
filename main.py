from tools import readlog, writetolog, getmarkings
from zmorge import lemmatize
from pons.ponssuche import cardsfrompons
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
    cardsfrompons(maindict)  # maindict[marking] is added: termposes, ankinotes
    print('Uploading to Anki...')
    print()
    addnotes(maindict)  # maindict[marking]['ankinotes'] is added: Marking, couldadd
    print()
    print('Done:')
    writetolog(maindict)  # Print results and write them to log


if __name__ == "__main__":
    markings2cards()
