#!/usr/bin/env python
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Checks rss feed and posts to twitter.

Check an rss feed and if the latest entry is different than post it to twitter.

"""


import sys
import os
import traceback
import cPickle
from ConfigParser import SafeConfigParser
from optparse import OptionParser

import feedparser
import tweepy


__version__ = '0.0.3'

config = None

def post_update(status):
    global config
    consumer_key = config.get('twitter', 'consumer_key')
    consumer_secret = config.get('twitter', 'consumer_secret')
    access_token = config.get('twitter', 'access_token')
    access_token_secret = config.get('twitter', 'access_token_secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    try:
        api.update_status(status)
    except tweepy.error.TweepError, e:
        print "Error occurred while updating status:", e
        sys.exit(1)
    else:
        return True


def main():
    """The main function."""
    global config
    parser = OptionParser(version='%prog v' + __version__)
    parser.add_option('-c', '--config', default='config.ini',
                      help='Location of config file (default: %default)',
                      metavar='FILE')
    parser.add_option('-a', '--all', action='store_true', default=False,
                      dest='all',
                      help='Send all RSS items as tweet')
    parser.add_option('-l', '--limit', dest='limit',
                      default=10,
                      help='Use with all parameters, send the first 10 feeds as a tweet')
    (options, args) = parser.parse_args()
    config = SafeConfigParser()
    if not config.read(options.config):
        print 'Could not read config file'
        sys.exit(1)
    rss_uri = config.get('rss', 'uri')
    feed = feedparser.parse(rss_uri)
    # lots of scary warnings about possible security risk using this method
    # but for local use I'd rather do this than a try-catch with open()
    if not os.path.isfile('cache.dat'):
        # make a blank cache file
        cPickle.dump({'id': None}, open('cache.dat', 'wb'), -1)

    cache = cPickle.load(open('cache.dat'))
    if options.all:
        tweet_count = 0
        for entry in feed['entries']:
            rss = {
                'id': entry['id'],
                'link': entry['link'],
                'title': entry['title'],
                'summary': entry['summary'],
                'hashtag': ' '.join(['#%s' % i for i in entry['tags'][0]['term'].split()[:2]]),
            }
            post_update('%s %s %s' % (rss['title'], rss['link'], rss['hashtag']))

            # We keep the first feed in the cache, to use rss2twitter in normal mode the next time
            if tweet_count == 0:
                cPickle.dump(rss, open('cache.dat', 'wb'), -1)

            tweet_count += 1
            if tweet_count >= options.limit:
                break
    else:
        rss = {
            'id': feed['entries'][0]['id'],
            'link': feed['entries'][0]['link'],
            'title': feed['entries'][0]['title'],
            'summary': feed['entries'][0]['summary'],
            'hashtag': ' '.join(['#%s' % i for i in feed['entries'][0]['tags'][0]['term'].split()[:2]]),
        }
        # compare with cache
        if cache['id'] != rss['id']:
            #print 'new post'
            post_update('%s %s %s' % (rss['title'], rss['link'], rss['hashtag']))
            cPickle.dump(rss, open('cache.dat', 'wb'), -1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt, e:
        # Ctrl-c
        raise e
    except SystemExit, e:
        # sys.exit()
        raise e
    except Exception, e:
        print "ERROR, UNEXPECTED EXCEPTION"
        print str(e)
        traceback.print_exc()
        sys.exit(1)
    else:
        # Main function is done, exit cleanly
        sys.exit(0)


