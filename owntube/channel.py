#!/usr/bin/env python3

import json

from os.path import abspath, dirname

import requests
from requests.exceptions import HTTPError

from lxml import etree
from sty import fg, ef

from commonutils import download_image
from database import DatabaseItem
from exceptions import ChannelNotFound, SubscriptionFeedFetchError
import video

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
            raise SubscriptionFeedFetchError()

        return etree.fromstring(bytes(req.text, encoding='utf-8'))

class Channel(DatabaseItem):
    """Representation of an YouTube channel."""

    def __init__(self, channel_id = None, name = None, description = None):
        super().__init__('channels')

        self.channel_id = channel_id
        self.name = name
        self.description = description

        self._avatar_dir = dirname(abspath(__file__)) + '/static/avatars'

    def from_id(self, id):
        # Fetch database row.
        row = self._fetch_by_id('cid', id)
        if row is None:
            raise ChannelNotFound()

        # Populate ourselves.
        self.channel_id = row[0]
        self.name = row[1]
        self.description = row[2]

        return self

    def save(self):
        self._commit({
            'cid': self.channel_id,
            'name': self.name,
            'description': self.description
        })

    def exists(self):
        return self._check_exists('cid', self.channel_id)

    @staticmethod
    def import_from_dump(fname):
        """Imports data from a JSON dump and saves it to the database."""
        # Load the JSON dump.
        with open(fname, 'r') as fh:
            channel = json.load(fh)

        # Build up the new class and save it to the database.
        self = Channel(channel['resourceId']['channelId'], channel['title'],
                       channel['description'])
        print(f'Importing channel {fg.yellow}{self.name}{fg.rs}...')

        # Save the channel to the database.
        self.save()

        # Download the thumbnail.
        self._fetch_avatar(channel['thumbnails'])

        # Go through the videos and import them.
        total = len(channel['videos'])
        index = 1
        for video_dump in channel['videos']:
            print(f'[{fg.blue}{index}/{total}{fg.rs}] Importing video '
                  f'{ef.italic}{video_dump["title"]}{ef.rs}')
            video.Video.import_from_dump(self, video_dump)
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
