from os import remove
from subprocess import run
import re
import requests
from zipfile import ZipFile
import io
from os.path import dirname, join

from tools import basiccleanup


cafileurl = 'https://pub.cl.uzh.ch/users/sennrich/zmorge/transducers/zmorge-20150315-smor_newlemma.ca.zip'

posdict = {'<+V>': 'Verb',
           '<+NN>': 'Nomen',
           '<+ADJ>': 'Adjektiv',
           '<+ADV>': 'Adverb', '<+PROADV>': 'Adverb'}


def lemmatize(markings):
    if isinstance(markings, str):
        markings = [markings]

    maindict = {}
    allterms = []
    for marking in markings:
        cleanmarking = basiccleanup(marking)
        if not cleanmarking: continue
        maindict[marking] = {'clean': cleanmarking, 'terms': [], 'lemmaposes': []}
        if len(marking.split()) == 1:  # case of single word
            maindict[marking]['terms'] = [maindict[marking]['clean']]
        else:  # case of a phrase: look for trennbares Verb
            one, two = maindict[marking]['clean'].split()[0].lower(), maindict[marking]['clean'].split()[-1].lower()
            maindict[marking]['terms'] = [one + two, two + one]

        allterms.extend(maindict[marking]['terms'])

    zmorgout = query(allterms)
    for marking in maindict:
        for term in maindict[marking]['terms']:
            maindict[marking]['lemmaposes'].extend(zmorgout[term])
        maindict[marking]['lemmaposes'] = list(set(maindict[marking]['lemmaposes']))
        if len(maindict[marking]['clean'].split()) > 1:  # keep only verbs if more than one word
            maindict[marking]['lemmaposes'] = [(lm, p) for lm, p in maindict[marking]['lemmaposes'] if p == 'Verb']

    simplerules(maindict)
    return maindict


def simplerules(maindict):
    ruleset = [(lambda l, p: l.endswith('nd') and p == 'Adjektiv', lambda l, p: (l.rstrip('d'), 'Verb'))]

    for marking in maindict:
        for lemma, pos in maindict[marking]['lemmaposes']:
            for ruleapplies, newlemmapos in ruleset:
                if ruleapplies(lemma, pos):
                    maindict[marking]['lemmaposes'].append(newlemmapos(lemma, pos))


def query(terms):
    r = requests.get(cafileurl)
    with ZipFile(io.BytesIO(r.content)) as archive:
        cafilepath = archive.extract(archive.namelist()[0], path=dirname(__file__))

    wordlistfilename = join(dirname(__file__), 'tmp_zmorgewordlist.txt')
    with open(wordlistfilename, mode='w', encoding='utf8') as f:
        for term in terms:
            f.write(term + '\n')

    prc = run(['fst-infl2', cafilepath, wordlistfilename], capture_output=True)
    remove(wordlistfilename)
    remove(cafilepath)
    outrows = prc.stdout.decode('utf-8').split('\n')
    # for row in outrows:
    #     print(row)
    zmorgout = out2lemmatags(outrows, terms)
    return zmorgout


def out2lemmatags(outrows, terms):
    outrows = [row for row in outrows if row]
    zmorgout = {}
    for term in terms:
        zmorgout[term] = []
        # print(term)
        outrowsiter = iter(outrows)
        for row in outrowsiter:
            if row == '> ' + term:
                row = next(outrowsiter)
                while not row.startswith('> '):
                    lemma, pos = row2lemma(row)
                    # print(lemma, pos)
                    if lemma is not None:
                        zmorgout[term].append((lemma, pos))
                    try:
                        row = next(outrowsiter)
                    except StopIteration:
                        break
                break
    return zmorgout


def row2lemma(row):
    if row.startswith('no result for '):
        return None, None

    tags = re.findall('<.*?>', row)
    try:
        pos = posdict[next(tag for tag in tags if tag in posdict)]
    except StopIteration:
        pos = ''

    lemma = row
    for tag in tags:
        lemma = lemma.replace(tag, '')
    lemma = ''.join(filter(lambda x: x.isalpha() or x in ['-', ' ', ','], lemma))

    return lemma, pos
