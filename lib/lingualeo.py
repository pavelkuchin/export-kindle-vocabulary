import urllib2
import urllib
import cookielib
import time
import re
import json
import unicodedata

class LinguaLeoAPI():
    BASEURL = "http://lingualeo.com"

    URLs = {
        'login': BASEURL + '/ru/login',
        'translations': BASEURL + '/userdict3/getTranslations',
        'addWordWithContext': BASEURL + '/userdict3/addContext',
        'getDictionary': BASEURL + '/userdict/json'
    }

    BASIC_HEADER = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    DICT_HEADER = {'X-Requested-With': 'XMLHttpRequest'}

    def __init__(self, login, password):
        jar = cookielib.FileCookieJar("cookies")
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        urllib2.install_opener(opener)

        data = urllib.urlencode({'email': login, 'password': password})
        req = urllib2.Request(self.URLs['login'], data, self.BASIC_HEADER)
        r = urllib2.urlopen(req)
        result = r.read()
        r.close()

        # Are we in?
        if '"isAuth":true' not in result:
            raise Exception("Login error. Please check your login and password!")

        # Looking for server hash. Example: "serverHash":"20140429150031"
        hashPattern = re.compile(r'"serverHash":"(\d+)"')
        self.lhash = hashPattern.search(result).groups()[0]

    def get_translations(self, word):
        r = urllib2.urlopen(self.URLs['translations'] + urllib.quote("?word_value=%s&groupId=&_hash=%s&_=%d" \
                            % (word, self.lhash, time.time() * 1000)))
        result = json.load(r)
        r.close()
        return result

    def get_user_dictionary(self, page = 0):
        result = []

        data = urllib.urlencode({'sortBy': 'date', 'wordType': 0, 'filter': 'all', 'page': page, '_hash': self.lhash})
        req = urllib2.Request(self.URLs['getDictionary'], data, dict(self.BASIC_HEADER.items() + self.DICT_HEADER.items()))
        r = urllib2.urlopen(req)
        resp = json.loads(r.read())
        for i in resp["userdict3"]:
            result.extend(i["words"])
        if resp["show_more"] == True:
            page += 1
            result.extend(self.get_user_dictionary(page))
            return result
        else:
            return result
        r.close()

    def add_word_with_context(self, word, context, translation_id):
        ncontext = unicodedata.normalize('NFKD', context).encode('ascii','ignore')
        nword = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
        data = urllib.urlencode({'groupId': 'dictionary',
            'content_id': '',
            'word_value': nword,
            'translate_id': translation_id,
            'context_text': ncontext,
            'context_id': 0,
            '_hash': self.lhash})
        req = urllib2.Request(self.URLs['addWordWithContext'], data, dict(self.BASIC_HEADER.items() + self.DICT_HEADER.items()))
        r = urllib2.urlopen(req)
        resp = json.loads(r.read())
        r.close()
        if resp['error_msg']:
            print "Can't add word: %s. Error occurred: %s" % (nword, resp['error_msg'])
        else:
            print "Word '%s' has been added." % nword
