from bs4 import BeautifulSoup as BS


def parserom(rom):  # rom has: headword, info, sense, wordclass, arabs
    soup = BS(rom['headword_full'], features="lxml")

    rom['headword'] = ''.join(filter(lambda x: x.isalpha() or x in ['-', ' ', ','], rom['headword']))

    info = []
    for cl in ['genus', 'info' 'topic', 'rhetoric', 'style']:
        info += soup.find_all('span', {'class': cl})
    rom['info'] = info

    sense = []
    for cl in ['sense']:
        sense += soup.find_all('span', {'class': cl})
    rom['sense'] = sense

    if 'wordclass' not in rom:
        rom['wordclass'] = None
    if 'arabs' not in rom:
        rom['arabs'] = []
    return rom


def parsearab(arab):  # arab has: headword, info, sense, translations
    soup = BS(arab['header'], features="lxml")

    arab['headword'] = ''
    if soup.find_all(text=True):
        arab['headword'] = str(soup.find_all(text=True)[0])
    if len(arab['headword']) >= 3 and arab['headword'][0].isdigit() and arab['headword'][1] == '.' \
            and arab['headword'][2].isspace():
        arab['headword'] = arab['headword'][3::]
    arab['headword'] = arab['headword'].strip()

    info = []
    for cl in ['genus', 'info' 'topic', 'rhetoric', 'style']:
        info += soup.find_all('span', {'class': cl})
    arab['info'] = info

    sense = []
    for cl in ['sense']:
        sense += soup.find_all('span', {'class': cl})
    arab['sense'] = sense

    if 'translations' not in arab:
        arab['translations'] = []
    return arab


def parsetrans(trans):  # trans has: source, source_text, target, transtype
    soup = BS(trans['source'], features="lxml")
    trans['transtype'] = ''
    for transtype in ['example', 'full_collocation', 'grammatical_construction']:
        if soup.find_all('span', {'class': transtype}):
            trans['transtype'] = transtype
    trans['source_text'] = soup.text
    return trans
