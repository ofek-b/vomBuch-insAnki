from pons.parsing import *
from pons.querypons import *
from tools import removedups


def taketrans(rom, arab, lemma, pos):
    posmatches = not pos or (rom['wordclass'] is not None and pos in rom['wordclass'])
    lemmamatches = lemma and lemma in [arab['headword'], rom['headword']]
    return posmatches and lemmamatches


def lookupinjson(data, lemma, pos):
    roms, lonely_translations = getroms(data)
    if isinstance(roms, str):
        # print(roms)
        return []

    cardnominees = []
    cardnominees_b = []
    for rom in roms:
        rom = parserom(rom)
        # print('@'+rom['headword']+'@', rom['wordclass'])
        for arab in rom['arabs']:
            arab = parsearab(arab)
            # print('\t', '@'+arab['headword']+'@')
            for trans in arab['translations']:
                trans = parsetrans(trans)
                # print( '\t\t', trans['source'], trans['target'], trans['transtype'] )
                if taketrans(rom, arab, lemma, pos):
                    cardnominees.append((rom, arab, trans))

    if not roms and len(lemma.split()) > 1:  # idiom
        for trans in lonely_translations:
            trans = parsetrans(trans)
            if lemma in trans['source_text']:
                cardnominees.append((None, None, trans))

    return cardnominees


def picard(cardnominees, pos):
    egs = [cn for cn in cardnominees if 'example' == cn[2]['transtype'] or 'full_collocation' == cn[2]['transtype']]
    srtd = []
    if pos == 'Verb':
        srtd = [cn for cn in cardnominees if 'grammatical_construction' == cn[2]['transtype']]
    srtd += [cn for cn in cardnominees if cn not in srtd and cn not in egs]

    if srtd:
        rom, arab, trans = srtd[0]
        egs = [cn for cn in egs if arab == cn[1]] + [cn for cn in egs if rom == cn[0]]
        egtrans = None
        if egs and rom is not None:
            _, _, egtrans = egs[0]
        return rom, arab, trans, egtrans
    else:
        rom, arab, trans = egs[0]
        return rom, arab, trans, None


def createnote(rom, arab, trans, egtrans=None):
    examples = ''
    if egtrans is not None:
        examples = egtrans['source'] + '<br>' + egtrans['target']
    info = sense = ''
    if rom is not None:
        info = ', '.join([str(x) for x in removedups(arab['info'] + rom['info'])])
        if info:
            info = '&nbsp;&nbsp;&nbsp;' + info
        sense = ', '.join([str(x) for x in removedups(arab['sense'] + rom['sense'])])

    ankinote = {'DE': trans['source'],
                'DE Info': info,
                'Sense': sense,
                'EN': trans['target'],
                'Examples': examples}

    return ankinote


def cardsfrompons(maindict):
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
            cardnominees = lookupinjson(responses[term], term, pos)
            if not cardnominees: continue
            rom, arab, trans, egtrans = picard(cardnominees, pos)
            ankinote = createnote(rom, arab, trans, egtrans)
            if ankinote['DE']:
                maindict[marking]['ankinotes'].append(ankinote)
