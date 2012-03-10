import re
import time
import urllib
import urllib2
import logging
import mechanize
import json
from flexget.plugin import register_plugin, PluginWarning, PluginError
import mimetypes

log = logging.getLogger('spool')

class PluginSpool(object):
    def validator(self):
        from flexget import validator
        root = validator.factory('dict')
        root.accept('text', key='userid')
        root.accept('text', key='password')
        return root

    def on_process_start(self, feed, config):
        self.browser = mechanize.Browser()
        self.auth = False

    def on_feed_download(self, feed, config):
        if not self.auth and not feed.manager.options.test:
            data = { 'userid': config.get('userid'), 'password': config.get('password') }
            resp = self.browser.open('https://getspool.com/api/authenticate', urllib.urlencode(data))
            auth_resp = json.loads(resp.read())
            self.enqueue_key = auth_resp[u'enqueue_key'].encode('ascii', 'ignore')
            self.auth = True
        for entry in feed.accepted:
            if entry.get('urls'):
                urls = entry.get('urls')
            else:
                urls = [entry['url']]
            errors = []
            for url in urls:
                if feed.manager.options.test:
                    log.info('Would spool: %s' % entry['title'])
                else:
                    resp = self.browser.open('https://getspool.com/bookmark/' + self.enqueue_key + '?url=' + urllib.quote_plus(url))
                    js = resp.read()
                    key = re.search("var key = '([^']+)';", js).group(1)
                    cver = re.search("var cver = '([^']+)';", js).group(1)
                    recording = { "type": "record", "url": url, "title": entry['title'] }
                    data = { "cver": cver, "tk": self.enqueue_key, "k": key.encode('ascii', 'ignore'), "recording": json.dumps(recording) }
                    resp = self.browser.open('https://getspool.com/bookmark/enqueue', urllib.urlencode(data))
                    log.info('Spooled: %s' % entry['title'])


register_plugin(PluginSpool, 'spool', api_ver=2)
