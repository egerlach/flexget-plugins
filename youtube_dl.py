import re
import time
import urllib
import urllib2
import logging
import mechanize
from flexget.plugin import register_plugin, PluginWarning, PluginError
import mimetypes
import youtube_dl
import cookielib

log = logging.getLogger('youtube_dl')

class PluginYoutubeDL(object):

    def validator(self):
        from flexget import validator
        root = validator.factory('dict')
        root.accept('text', key='directory')
        return root

    def on_process_start(self, feed, config):
        self.browser = mechanize.Browser()

    def on_feed_output(self, feed, config):
        jar = cookielib.CookieJar()
        cookie_processor = urllib2.HTTPCookieProcessor(jar)
        proxy_handler = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy_handler, cookie_processor, youtube_dl.YoutubeDLHandler())
        urllib2.install_opener(opener)
        for entry in feed.accepted:
            if entry.get('urls'):
                urls = entry.get('urls')
            else:
                urls = [entry['url']]
            pubdate = entry.get('rss_pubdate')
            errors = []
            if not feed.manager.options.test:
                fd = youtube_dl.FileDownloader({
                    'usenetrc': None,
                    'username': None,
                    'password': None,
                    'quiet': False,
                    'forceurl': False,
                    'forcetitle': False,
                    'forcethumbnail': False,
                    'forcedescription': False,
                    'forcefilename': False,
                    'forceformat': False,
                    'simulate': False,
                    'skip_download': False,
                    'format': None,
                    'format_limit': None,
                    'listformats': None,
                    'outtmpl': u'%(directory)s/%(year)04d-%(month)02d-%(day)02d-%%(id)s.%%(ext)s' % {'directory': config.get('directory'), 'year': pubdate.year, 'month': pubdate.month, 'day': pubdate.day},
                    'ignoreerrors': False,
                    'ratelimit': None,
                    'nooverwrites': False,
                    'retries': 10,
                    'continuedl': True,
                    'noprogress': False,
                    'playliststart': 1,
                    'playlistend': -1,
                    'logtostderr': False,
                    'consoletitle': False,
                    'nopart': False,
                    'updatetime': True,
                    'writedescription': False,
                    'writeinfojson': False,
                    'writesubtitles': False,
                    'subtitleslang': None,
                    'matchtitle': None,
                    'rejecttitle': None,
                    'max_downloads': None,
                    'prefer_free_formats': False,
                    'verbose': False,
                    })
                
                for extractor in youtube_dl.gen_extractors():
                    fd.add_info_extractor(extractor)
                
                urls = map(lambda url: url.strip(), urls)
                fd.download(urls)
        urllib2.install_opener(urllib2.build_opener())


register_plugin(PluginYoutubeDL, 'youtube_dl', api_ver=2)
