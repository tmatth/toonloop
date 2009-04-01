#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ToonLoop for Python
#
# Copyright 2008 Tristan Matthews & Alexandre Quessy
# <le.businessman@gmail.com> & <alexandre@quessy.net>
#
# Original idea by Alexandre Quessy
# http://alexandre.quessy.net
# 
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# ToonLoop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ToonLoop.  If not, see <http://www.gnu.org/licenses/>.
"""
Twisted RSS Parser.

This code was found with no license, so I assume it is public domain.
Modified in 2008 by Alexandre Quessy and licensed under GPL 2.
Source : 
Recipe 277099: Rss aggregator with twisted 
http://code.activestate.com/recipes/277099/
"""

from twisted.internet import reactor, protocol, defer
from twisted.web import client
import feedparser
import time
import sys
import pprint

try:
    import cStringIO as _StringIO
except ImportError:
    import StringIO as _StringIO

#rss_feeds = out.rss_feed # This is the HUGE feed list  (730 feeds)

DEFERRED_GROUPS = 60  # Number of simultaneous connections
INTER_QUERY_TIME = 300 # Max Age (in seconds) of each feed in the cache
TIMEOUT = 30 # Timeout in seconds for the web request

# This dict structure will be the following:
# { 'URL': (TIMESTAMP, value) }
cache = {}

class FeederProtocol(object):
    def __init__(self):
        self.parsed = 1
        self.with_errors = 0
        self.error_list = []
        
    def isCached(self, site):
        # Try to get the tuple (TIMESTAMP, FEED_STRUCT) from the dict if it has
        # already been downloaded. Otherwise assign None to already_got
        already_got = cache.get(site[0], None)

        # Ok guys, we got it cached, let's see what we will do
        if already_got:
            # Well, it's cached, but will it be recent enough?
            elapsed_time = time.time() - already_got[0]
            
            # Woooohooo it is, elapsed_time is less than INTER_QUERY_TIME so I
            # can get the page from the memory, recent enough
            if elapsed_time < INTER_QUERY_TIME:
                return True
            
            else:    
                # Uhmmm... actually it's a bit old, I'm going to get it from the
                # Net then, then I'll parse it and then I'll try to memoize it
                # again
                return False
            
        else: 
            # Well... We hadn't it cached in, so we need to get it from the Net
            # now, It's useless to check if it's recent enough, it's not there.
            return False

    def gotError(self, traceback, extra_args):
        # An Error as occurred, print traceback infos and go on
        print traceback, extra_args
        self.with_errors += 1
        self.error_list.append(extra_args)
        print "="*20
        print "Trying to go on..."
        
    def getPageFromMemory(self, data, key=None):
        # Getting the second element of the tuple which is the parsed structure
        # of the feed at address key, the first element of the tuple is the
        # timestamp
        print "Getting from memory..."
        return defer.succeed(cache.get(key,key)[1])

    def parseFeed(self, feed):
        # This is self explaining :)
        print "parsing..."
        try:
            feed+''
            parsed = feedparser.parse(_StringIO.StringIO(feed))
        except TypeError:
            parsed = feedparser.parse(_StringIO.StringIO(str(feed)))
        print "parsed feed"
        pprint.pprint(parsed)
        return parsed
   
    def memoize(self, feed, addr):
        # feed is the raw structure, just as returned from feedparser.parse()
        # while addr is the address from which the feed was got.
        print "Memoizing",addr,"..."
        if cache.get(addr, None):
            cache[addr] = (time.time(), feed)
        else:
            cache.setdefault(addr, (time.time(),feed))
        return feed
    
    def workOnPage(self, parsed_feed, addr):
        # As usual, addr is the feed address and file is the file in
        # which you can eventually save the structure.
        print "-"*20
        print "finished retrieving"
        print "Feed Version:",parsed_feed.get('version','Unknown')
        
        #
        #  Uncomment the following if you want to print the feeds
        #
        chan = parsed_feed.get('channel', None)
        if chan:
            print chan.get('title', '')
            #print chan.get('link', '')
            #print chan.get('tagline', '')
            #print chan.get('description','')
        print "-"*20
        #items = parsed_feed.get('items', None)
        #if items:
        #    for item in items:
        #        print '\tTitle: ', item.get('title','')
        #        print '\tDate: ', item.get('date', '')
        #        print '\tLink: ', item.get('link', '')
        #        print '\tDescription: ', item.get('description', '')
        #        print '\tSummary: ', item.get('summary','')
        #        print "-"*20
        #print "got",addr
        #print "="*40
        return parsed_feed
        
    def stopWorking(self, data=None):
        print "Closing connection number %d..."%(self.parsed,)
        print "=-"*20
        
        # This is here only for testing. When a protocol/interface will be
        # created to communicate with this rss-aggregator server, we won't need
        # to die after we parsed some feeds just one time.
        self.parsed += 1
        print self.parsed,  self.END_VALUE
        if self.parsed > self.END_VALUE:   #
            print "Closing all..."         #
            for i in self.error_list:      #  Just for testing sake
                print i                    #
            print len(self.error_list)     #
            reactor.stop()                 #

    def getPage(self, data, args):
        return client.getPage(args,timeout=TIMEOUT)

    def printStatus(self, data=None):
        print "Starting feed group..."
            
    def start(self, data=None, std_alone=True):
        d = defer.succeed(self.printStatus())
        for feed in data:
        
            # Now we start telling the reactor that it has
            # to get all the feeds one by one...
            cached = self.isCached(feed)
            if not cached: 
                # When the feed is not cached, it's time to
                # go and get it from the web directly
                d.addCallback(self.getPage, feed[0])
                d.addErrback(self.gotError, (feed[0], 'getting'))
                
                # Parse the feed and if there's some errors call self.gotError
                d.addCallback(self.parseFeed)
                d.addErrback(self.gotError, (feed[0], 'parsing'))
                
                # Now memoize it, if there's some error call self.getError
                d.addCallback(self.memoize, feed[0])
                d.addErrback(self.gotError, (feed[0], 'memoizing'))
                
            else: # If it's cached
                d.addCallback(self.getPageFromMemory, feed[0])
                d.addErrback(self.gotError, (feed[0], 'getting from memory'))
            
            # When you get the raw structure you can work on it
            # to format in the best way you can think of.
            # For any error call self.gotError.
            d.addCallback(self.workOnPage, feed[0])
            d.addErrback(self.gotError, (feed[0], 'working on page'))
            
            # And when the for loop is ended we put 
            # stopWorking on the callback for the last 
            # feed gathered
            # This is only for testing purposes
            if std_alone:
                d.addCallback(self.stopWorking)
                d.addErrback(self.gotError, (feed[0], 'while stopping'))
        if not std_alone:
            return d

class FeederFactory(protocol.ClientFactory):
    protocol = FeederProtocol()
    def __init__(self, feeds, std_alone=False):
        self.feeds = feeds # self.getFeeds()
        self.std_alone = std_alone
        
        self.protocol.factory = self
        self.protocol.END_VALUE = len(self.feeds) # this is just for testing

        if std_alone:
            self.start(self.feeds)

    def start(self, addresses):
        # Divide into groups all the feeds to download
        if len(addresses) > DEFERRED_GROUPS:
            url_groups = [[] for x in xrange(DEFERRED_GROUPS)]
            for i, addr in enumerate(addresses):
                url_groups[i%DEFERRED_GROUPS].append(addr)
        else:
            url_groups = [[addr] for addr in addresses]
            
        for group in url_groups:
            if not self.std_alone:
                return self.protocol.start(group, self.std_alone)
            else:
                self.protocol.start(group, self.std_alone)

#     def getFeeds(self, where=None):
#         # This is used when you call a COMPLETE refresh of the feeds,
#         # or for testing purposes
#         #print "getting feeds"
#         # This is to get the feeds we want
#         if not where: # We don't have a database, then we use the local
#                       # variabile rss_feeds
#             return rss_feeds
#         else: return None

if __name__=="__main__":
    tpl = """
    <?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
    <channel>
      <title>Sample Feed</title>
      <description>For documentation &lt;em&gt;only&lt;/em&gt;</description>
      <link>http://example.org/</link>
      <language>en</language>
      <copyright>Copyright 2004, Mark Pilgrim</copyright>
      <managingEditor>editor@example.org</managingEditor>
      <webMaster>webmaster@example.org</webMaster>
      <pubDate>Sat, 07 Sep 2002 00:00:01 GMT</pubDate>
      <category domain="Syndic8">1024</category>
      <category domain="dmoz">Top/Society/People/Personal_Homepages/P/</category>
      <generator>Sample Toolkit</generator>
      <docs>http://feedvalidator.org/docs/rss2.html</docs>
      <cloud domain="rpc.example.com" port="80" path="/RPC2" registerProcedure="pingMe" protocol="soap"/>
      <ttl>60</ttl>
      <image>
        <url>http://example.org/banner.png</url>
        <title>Example banner</title>
        <link>http://example.org/</link>
        <width>80</width>
        <height>15</height>
      </image>
      <textInput>
        <title>Search</title>
        <description>Search this site:</description>
        <name>q</name>
        <link>http://example.org/mt/mt-search.cgi</link>
      </textInput>
      <item>
        <title>First item title</title>
        <link>http://example.org/item/1</link>
        <description>Watch out for &lt;span style="background: url(javascript:window.location='http://example.org/')"&gt;nasty tricks&lt;/span&gt;</description>
        <author>mark@example.org</author>
        <category>Miscellaneous</category>
        <comments>http://example.org/comments/1</comments>
        <enclosure url="http://example.org/audio/demo.mp3" length="1069871" type="audio/mpeg"/>
        <guid>http://example.org/guid/1</guid>
        <pubDate>Thu, 05 Sep 2002 00:00:01 GMT</pubDate>
      </item>
    </channel>
    </rss>
    """
# out = [  ( 'URL', 'EXTRA_INFOS'),
#          ( 'URL', 'EXTRA_INFOS')
#          ...
#        ]
    # global rss_feeds
    if 1:
        print "TEST 1: local string"
        feedparser.parse(tpl)

        parsed = feedparser.parse(_StringIO.StringIO(tpl))
        pprint.pprint(parsed)
    if 1:
        url = 'http://toonloop.com/?q=rss.xml'
        print "TEST 2: remote file"
        rss_feeds = [(url, 'toonloop web site')]
        f = FeederFactory(rss_feeds, std_alone=True)
        reactor.run()

    if 1:
        super_dict = {'bozo': 0,
 'encoding': 'utf-8',
 'entries': [{'author': u'admin',
              'comments': u'http://toonloop.com/?q=node/8#comments',
              'enclosures': [{'href': u'http://toonloop.com/sites/default/files/output_0.flv',
                              'length': u'386010',
                              'type': u'application/octet-stream'}],
              'guidislink': False,
              'id': u'http://toonloop.com/8 at http://toonloop.com',
              'link': u'http://toonloop.com/?q=node/8',
              'links': [{'href': u'http://toonloop.com/?q=node/8',
                         'rel': 'alternate',
                         'type': 'text/html'}],
              'summary': u'<p>Test number 2</p>',
              'summary_detail': {'base': u'http://toonloop.com',
                                 'language': None,
                                 'type': 'text/html',
                                 'value': u'<p>Test number 2</p>'},
              'title': u'noisy green',
              'title_detail': {'base': u'http://toonloop.com',
                               'language': None,
                               'type': 'text/plain',
                               'value': u'noisy green'},
              'updated': u'Tue, 24 Mar 2009 07:38:35 +0000',
              'updated_parsed': (2009, 3, 24, 7, 38, 35, 1, 83, 0)},
             {'author': u'admin',
              'comments': u'http://toonloop.com/?q=node/5#comments',
              'enclosures': [{'href': u'http://toonloop.com/sites/default/files/output.flv',
                              'length': u'386010',
                              'type': u'application/octet-stream'}],
              'guidislink': False,
              'id': u'http://toonloop.com/5 at http://toonloop.com',
              'link': u'http://toonloop.com/?q=node/5',
              'links': [{'href': u'http://toonloop.com/?q=node/5',
                         'rel': 'alternate',
                         'type': 'text/html'}],
              'summary': u'<p>This is some green and some noise. Test for the video uploder.</p>',
              'summary_detail': {'base': u'http://toonloop.com',
                                 'language': None,
                                 'type': 'text/html',
                                 'value': u'<p>This is some green and some noise. Test for the video uploder.</p>'},
              'title': u'green and noise',
              'title_detail': {'base': u'http://toonloop.com',
                               'language': None,
                               'type': 'text/plain',
                               'value': u'green and noise'},
              'updated': u'Tue, 24 Mar 2009 06:57:19 +0000',
              'updated_parsed': (2009, 3, 24, 6, 57, 19, 1, 83, 0)},
             {'author': u'admin',
              'guidislink': False,
              'id': u'http://toonloop.com/1 at http://toonloop.com',
              'link': u'http://toonloop.com/?q=home',
              'links': [{'href': u'http://toonloop.com/?q=home',
                         'rel': 'alternate',
                         'type': 'text/html'}],
              'summary': u'<p>(english below)<br />\nToonLoop (dessin tr\xe8s anim\xe9) est un dispositif pour la performance vid\xe9o de dessin anim\xe9 en direct. Les images sont ajout\xe9es une par une au moyen d\'une p\xe9dale qui, lorsque l\'on appuie dessus, prend une photo et la rajoute \xe0 la boucle d\'images. Ces images forment ensemble un film d\'animation. Au cours d\'une m\xeame soir\xe9e, on peut faire plusieurs petits films de la sorte. Cela peut \xeatre du dessin anim\xe9, ou encore du stop motion. (frame by frame) </p>\n<p>ToonLoop is a <strong>realtime stop motion performance tool</strong>. You can download it here for free. </p>\n<p><a href="http://toonloop.com/?q=home" target="_blank">read more</a></p>',
              'summary_detail': {'base': u'http://toonloop.com',
                                 'language': None,
                                 'type': 'text/html',
                                 'value': u'<p>(english below)<br />\nToonLoop (dessin tr\xe8s anim\xe9) est un dispositif pour la performance vid\xe9o de dessin anim\xe9 en direct. Les images sont ajout\xe9es une par une au moyen d\'une p\xe9dale qui, lorsque l\'on appuie dessus, prend une photo et la rajoute \xe0 la boucle d\'images. Ces images forment ensemble un film d\'animation. Au cours d\'une m\xeame soir\xe9e, on peut faire plusieurs petits films de la sorte. Cela peut \xeatre du dessin anim\xe9, ou encore du stop motion. (frame by frame) </p>\n<p>ToonLoop is a <strong>realtime stop motion performance tool</strong>. You can download it here for free. </p>\n<p><a href="http://toonloop.com/?q=home" target="_blank">read more</a></p>'},
              'title': u'Home',
              'title_detail': {'base': u'http://toonloop.com',
                               'language': None,
                               'type': 'text/plain',
                               'value': u'Home'},
              'updated': u'Tue, 24 Mar 2009 03:13:50 +0000',
              'updated_parsed': (2009, 3, 24, 3, 13, 50, 1, 83, 0)}],
 'feed': {'language': u'en',
          'link': u'http://toonloop.com',
          'links': [{'href': u'http://toonloop.com',
                     'rel': 'alternate',
                     'type': 'text/html'}],
          'subtitle': u'ToonLoop is a set of software tools from creating stop motion animation. It is intended to help teaching new medias to children and to give a professional tool for movie creators.',
          'subtitle_detail': {'base': u'http://toonloop.com',
                              'language': None,
                              'type': 'text/html',
                              'value': u'ToonLoop is a set of software tools from creating stop motion animation. It is intended to help teaching new medias to children and to give a professional tool for movie creators.'},
          'title': u'ToonLoop',
          'title_detail': {'base': u'http://toonloop.com',
                           'language': None,
                           'type': 'text/plain',
                           'value': u'ToonLoop'}},
 'namespaces': {'dc': u'http://purl.org/dc/elements/1.1/'},
 'version': 'rss20'}
 