#!/usr/bin/env python
from setuptools import setup

setup(
    name = 'rss2twitter',
    version = '0.0.1',
    package_dir = {'': 'src'},
    data_files = [('etc/rss2twitter', ['src/config-sample.ini'])],
    scripts = ['src/rss2twitter.py'],
    install_requires = ['feedparser', 'tweepy>=1.8'],

    author = 'Todd Eddy',
    author_email = 'vr@vrillusions.com',
    description = 'Checks rss feed for new posts and adds them to twitter.',
    url = 'https://github.com/vrillusions/rss2twitter',
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        ],
)
