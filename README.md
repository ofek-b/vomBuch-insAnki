# vomBuchInAnki
I wrote it to save me the effort of reading through the list of notes I made in Google Books, looking them up and manually typing every single note into Anki. Simply highlight something -> run vomBuchInAnki -> Anki note created.

<img src="/example.png" alt="Example" width="70%" height="70%">

## Installation
You need to have [Anki](https://apps.ankiweb.net/#download) installed<sup>1</sup>: `$ sudo apt install anki` plus the add-on [AnkiConnect](https://ankiweb.net/shared/info/2055492159) (and your account connected of course).
 
 1. Clone this repo.
 1. `$ bash installpreqs.sh` to install the prerequisites ([SFST](https://www.cis.uni-muenchen.de/~schmid/tools/SFST/) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)).
 1. Set your profile in the profiles folder.
 
 ## Usage
 1. Markings provided should either be a single word, an idiom or a phrase beginning and ending with the parts of a separable verb (e.g. _ging oft damit ein_).
 1. `$ python main.py`
 1. Specify a profile if several exist.

## What it does
1. Markings are cleaned with phrases are treated as trennbare Verben or idioms, and then [Zmorge](https://pub.cl.uzh.ch/users/sennrich/zmorge/) is used for lemmatization and part-of-speech determination.
1. Every lemma + POS pair found (one marking can lead to several pairs) is queried to [PONS](https://en.pons.com/p/online-dictionary/developers/api) using the API you provided in the profile and according to their terms.
1. The best translation to be used as an Anki note is picked from the results, alongside with an example. This happenns for every lemma + POS pair, so a single marking can lead to several Anki notes.
1. Notes are created using AnkiConnect.
1. Markings for which no translation/lemma was found (~5%) are written in the path specified in the profile (so you can add them manually when you're bored).

## Notes
* Only thing preventing this to  run on Windows is SFST (exists for Linux and Mac)

<sup>1</sup> For some reason, installing Anki this way rather than from the tar archive in their website saves problems when calling `anki` from python (It's a different version, as this one lacks dark mode).
