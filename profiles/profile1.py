import requests

"""
This is a profile file. You may rename it.
You may create several (e.g. for different decks and corresponding sources).
Every file must contain ANKI_USER, DECK_NAME, NOT_FOUND_PATH, PONS_KEY and getmarkings.
"""

# Anki profile username to use
ANKI_USER = "User 1"
# Anki deck to use (does not have to exist before first run)
DECK_NAME = "Deck 1"
# Path to a .txt file where unsuccessful searches are saved
NOT_FOUND_PATH = "/home/USERNAME/Documents/vomBuch-insAnki Notes Unfound - Deck 1.txt"
# Your PONS API-key(s), to be obtained in a two-minute process, free of charge and according to terms at:
# http://login.pons.com/login?return_to=https%3A%2F%2Fen.pons.com%2Fopen_dict%2Fpublic_api%3Flogged%3D1
PONS_KEYS = ["abc123456...", "xyz123456..."]


# A function returning a list of the markings you wish to input to vomBuch-insAnki, usually fetched from some cloud.
# The example here fetches the Google Play Books note list from Google Drive (see GPB's settings).
# To use just change the fileid below. If you wish to use a different cloud/list format, you should rewrite it.
def getmarkings():
    # File-ID of your auto-generated "Notizen aus..." Google Drive file. Must be "anyone with the link can view".
    fileid = 'xyz123...'
    baseurl = 'https://docs.google.com/document/export?format=txt&id=' + '%s' + '&includes_info_params=true'

    rows = requests.get(baseurl % fileid).text
    rows = rows.splitlines()
    startidx = 0
    while not ('Notizen' in rows[startidx] or 'notes' in rows[startidx]):
        startidx += 1
        if startidx == len(rows):
            raise Exception('Did not find declaraion regarding number of notes')
    numnotes = int(rows[startidx].split()[0])

    rows = [row.split('\t')[1] for row in rows[startidx:] if row.startswith('\t') and row.strip()]
    markings = [row for row in rows if not row.isdigit()]
    if len(markings) != numnotes:
        raise Exception('Error: Expected ' + str(numnotes) + ' notes, but found ' + str(len(markings)) + '.')

    return markings
