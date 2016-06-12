#!/usr/bin/python
# vim: set ts=4:
# vim: set shiftwidth=4:
# vim: set expandtab:

import os
import json
import time
import random
import codecs
import logging
import requests

import js2json

_USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'

_FAILCODE_MSG = 'Request for {0} failed with code {1}'
_FAILDATA_MSG = 'Request for {0} did not return json data, instead {1}'

class Crawler(object):
    def __init__(self, election_str, seconds_per_request):
        self.data_dir = os.path.abspath(election_str)
        self.scrapped_dir = os.path.join(self.data_dir, 'scrapped')
        if not os.path.exists(self.scrapped_dir):
            os.makedirs(self.scrapped_dir)
            os.makedirs(os.join.path(self.scrapped_dir, 'static'))
            os.makedirs(os.join.path(self.scrapped_dir, 'dyn'))
        self.limit = seconds_per_request
        self.next_request = 0.0

    def get(self, url):
        fname = url.rpartition('/')[2]
        if 'dyn' in url:
            fname = os.path.join('dyn', fname)
        else:
            fname = os.path.join('static', fname)
        fname = os.path.join(self.scrapped_dir, fname)

        if not os.path.exists(fname):
            self.wait()
            logging.info('Sending request for {0}'.format(url))
            r = requests.get(url, headers={'user-agent': _USERAGENT})

            if r.status_code != requests.codes.ok:
                logging.warning(_FAILCODE_MSG.format(url, r.status_code))
                return None
            header = r.headers['Content-Type']
            if header != 'application/json' and header != 'application/x-javascript':
                logging.warning(_FAILDATA_MSG.format(url, header))
                return None

            txt = self.transform(r.text)
            #txt = js2json.transform(r.text)

            with codecs.open(fname, 'w', encoding='utf-8') as f:
                f.write(txt)

            logging.info('Successful request for {0}'.format(url))

        with codecs.open(fname, 'r', encoding='utf-8') as f:
            return json.load(f)

    def wait(self):
        while True:
            now = time.time()
            if self.next_request > now:
                time.sleep(self.next_request - now)
            else:
                break
        self.next_request = now + random.uniform(0.33 * self.limit, 1.66 * self.limit)

    def transform(self, txt):
        try:
            json.loads(txt)
        except:
            idx1 = txt.find('[')
            idx2 = txt.find('{')
            if idx1 < idx2 and idx1 > 0:
                txt = txt[idx1:txt.rfind(']')+1]
            elif idx2 < idx1 and idx2 > 0:
                txt = txt[idx2:txt.rfind('}')+1]
            txt = txt.replace(u'epik:', u'\"epik\":')
            txt = txt.replace(u'snom:', u'\"snom\":')
            txt = txt.replace(u'ep:', u'\"ep\":')
            txt = txt.replace(u'dhm:', u'\"dhm\":')
            txt = txt.replace(u'den:', u'\"den\":')
            txt = txt.replace(u'party:', u'\"party\":')
        return txt
    
