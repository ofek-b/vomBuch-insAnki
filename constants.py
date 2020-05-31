from os.path import join, isdir
from os import listdir, mkdir
from importlib import import_module

NOTCODE_DIR = 'notcode'
if not isdir(NOTCODE_DIR):
    mkdir(NOTCODE_DIR)

# read profile:
profiles = [x.rstrip('.py') for x in listdir('profiles') if x.endswith('.py')]
profile = None
if not profiles:
    raise Exception('No profile found.')
elif len(profiles) == 1:
    profile = profiles[0]
while profile not in profiles:
    profile = input('Profile: ')

# import constants:
profmodule = import_module('profiles.' + profile)
ANKI_USER = profmodule.ANKI_USER
DECK_NAME = profmodule.DECK_NAME
NOT_FOUND_PATH = profmodule.NOT_FOUND_PATH
PONS_KEYS = profmodule.PONS_KEYS
getmarkings = profmodule.getmarkings

DONE_PATH = join(NOTCODE_DIR, 'donemarkings_' + profile + '.txt')
