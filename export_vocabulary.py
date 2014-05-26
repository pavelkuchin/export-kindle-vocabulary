#!/usr/bin/python

import argparse
import getpass
import os
import fileinput
from lib.helpers import *
from lib.whitepaper import Vocabulary
from lib.lingualeo import LinguaLeoAPI

"""
	Script to import vocabulary from Kindle Whitepaper to Lingualeo user dictionary.

	Get data from SQLLite and put to Lingualeo dictionary through RESTful API.
"""
parser = argparse.ArgumentParser(description = 'Import vocabulary from Kindle Whitepaper to Lingualeo user dictionary')
parser.add_argument('input', help = '.db file from Kindle')
parser.add_argument('login', help = 'Your Lingualeo login')
parser.add_argument('-p', '--password', help = "Optionally you can enter Lingualeo password here otherwise it will be requested later.")
parser.add_argument('-a', '--ask', action = "store_true", help = "Ask to select translation. Otherwise the most popular variant will be selected automatically. ")
args = parser.parse_args()

if not args.password:
	args.password = getpass.getpass('Lingualeo password:')

# Validate Input
if not os.path.isfile(args.input):
	raise Exception('File not found: %s' % args.input)

if not args.input.endswith(".db"):
	raise Exception('Unknown file type: %s' % args.input)

myprint('Getting vocabulary from kindle...')
voc = Vocabulary(args.input).read()
myprint('done\n')

kindle_words = get_uniques(voc)

myprint('Authorization on LinguaLeo...')
lla = LinguaLeoAPI(args.login, args.password)
myprint('done\n')
myprint('Getting dict...')
lldict = lla.get_user_dictionary()
myprint('done\n')
norm_lldict = [i["word_value"] for i in lldict]

myprint('Filtering new words...')
new_words = []
for w in kindle_words:
    if w[0] not in norm_lldict:
        new_words.append(w)
myprint('done\n')
print '%d total; %d new;' % (len(kindle_words), len(new_words))

print 'Getting translations and filling dictionary...'
for c, i in enumerate(new_words):
    print '[%d of %d]' % (c+1, len(new_words)),
    tr = lla.get_translations(i[0])
    if not tr['userdict3']['translations']:
        print "There are no translations for word '%s'" % i[0]
    elif args.ask:
        print "Translations for '%s'" % i[0]
        for e, t in enumerate(tr['userdict3']['translations']):
            print '%d - %s' % (e, t['translate_value'])
        user_input = raw_input('Translation variant (number): ')
        try:
            translation_variant = int(user_input)
            if not 0 <= translation_variant < len(tr['userdict3']['translations']):
                raise Exception()
        except:
            raise Exception('Invalid translation variant')
        lla.add_word_with_context(i[0], i[1], tr['userdict3']['translations'][translation_variant]['translate_id'])
    else:
        lla.add_word_with_context(i[0], i[1], tr['userdict3']['translations'][0]['translate_id'])

