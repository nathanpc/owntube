#!/usr/bin/env python3

import json

import requests
from requests.exceptions import HTTPError

from os.path import abspath, dirname
from lxml import etree
from sty import fg, ef

from commonutils import download_image
from video import Video

class YouTubeRSS:
    """YouTube channel RSS feed utility."""

    # Important URLs.
    CHANNEL_RSS_BASE_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='

    # XML namespaces.
    NS_ATOM = '{http://www.w3.org/2005/Atom}'
    NS_MEDIA = '{http://search.yahoo.com/mrss/}'
    NS_YOUTUBE = '{http://www.youtube.com/xml/schemas/2015}'

    def __init__(self, channel_id):
        self.channel_id = channel_id

    def fetch(self):
        """Fetches the RSS feed of the channel."""
        req = requests.get(self.CHANNEL_RSS_BASE_URL + self.channel_id)
        if req.status_code != 200:
            raise Exception('Failed to fetch channel\'s RSS feed')

        return etree.fromstring(bytes(req.text, encoding='utf-8'))

class Channel:
    """Representation of an YouTube channel."""

    def __init__(self, channel_id, name, description):
        self.channel_id = channel_id
        self.name = name
        self.description = description

        self._avatar_dir = dirname(abspath(__file__)) + '/static/avatars'

    @staticmethod
    def import_from_dump(fname):
        """Imports data from a JSON dump and saves it to the database."""
        # Load the JSON dump.
        channel = None
        with open(fname, 'r') as fh:
            channel = json.load(fh)

        # Build up the new class and save it to the database.
        self = Channel(channel['resourceId']['channelId'], channel['title'],
                       channel['description'])
        print(f'Importing channel {fg.yellow}{self.name}{fg.rs}...')
        # TODO: Save the channel to the database.

        # Download the thumbnail.
        self._fetch_avatar(channel['thumbnails'])

        # Go through the videos and import them.
        total = len(channel['videos'])
        index = 1
        for video_dump in channel['videos']:
            print(f'[{fg.blue}{index}/{total}{fg.rs}] Importing video '
                  f'{ef.italic}{video_dump["title"]}{ef.rs}')
            Video.import_from_dump(self, video_dump)
            index += 1

        return self

    def _fetch_avatar(self, thumbs):
        """Downloads the channel's avatar from the thumbnails list."""
        url = thumbs['high']['url']

        try:
            download_image(url, f'{self._avatar_dir}/{self.channel_id}.jpg')
        except HTTPError as err:
            print(f'{fg.red}Error: Failed to fetch avatar from {url}\n'
                  f'{err}{fg.rs}')

if __name__ == '__main__':
    channel = Channel.import_from_dump(
        'dump/NCommander_UCWyrVfwRL-2DOkzsqrbjo5Q.json')
