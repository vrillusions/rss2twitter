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


__version__ = open('VERSION', 'r').read()


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
    parser = OptionParser(version='%prog v' + __version__)
    parser.add_option('-c', '--config', default='config.ini',
                      help='Location of config file (default: %default)',
                      metavar='FILE')
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
    rss = {}
    rss['id'] = feed['entries'][0]['id']
    rss['link'] = feed['entries'][0]['link']
    rss['title'] = feed['entries'][0]['title']
    rss['summary'] = feed['entries'][0]['summary']
    # compare with cache
    if cache['id'] != rss['id']:
        #print 'new post'
        post_update('%s %s' % (rss['title'], rss['link']))
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


