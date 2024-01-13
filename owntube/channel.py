#!/usr/bin/env python3

import datetime
import json

from os.path import abspath, dirname

import requests
from requests.exceptions import HTTPError

from lxml import etree
from sty import fg, ef

from owntube.utils.commonutils import download_image, read_config
from owntube.utils.database import DatabaseItem
from owntube.utils.renderable import Renderable
from owntube.exceptions import ChannelNotFound, SubscriptionFeedFetchError
import owntube.video as video

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

class Channel(DatabaseItem, Renderable):
    """Representation of an YouTube channel."""

    def __init__(self, channel_id = None, name = None, description = None):
        super().__init__('channels')

        self.channel_id = channel_id
        self.name = name
        self.description = description

    def __dict__(self, expand=None):
        d = {
            'id': self.channel_id,
            'name': self.name,
            'description': self.description
        }

        return d

    def from_id(self, id):
        # Fetch database row.
        row = self._fetch_by_id('cid', id)
        if row is None:
            raise ChannelNotFound()

        return self._from_row(row)

    def save(self):
        self._commit({
            'cid': self.channel_id,
            'name': self.name,
            'description': self.description
        })

    def exists(self):
        return self._check_exists('cid', self.channel_id)

    def list(self):
        """Gets a list of the channels in the database."""
        channels = []

        # Get all the channels.
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM channels')
            for row in cur.fetchall():
                channels.append(Channel()._from_row(row))

        return channels

    def videos(self, count=None, since=None):
        """Gets the lastest videos or all the videos since a date."""
        videos = []

        # Ensure the user gets something.
        if count is None and since is None:
            count = read_config()['settings']['video_count']

        # Build up statement depending on our constraints.
        stmt = 'SELECT * FROM videos WHERE channel_cid = ? '
        if since is not None:
            stmt += 'AND published_date >= ? '
        stmt += 'ORDER BY published_date DESC '
        if count is not None:
            stmt += 'LIMIT ? '

        with self.conn.cursor() as cur:
            # Setup our statement parameters.
            params = [ self.channel_id ]
            if since is not None:
                params.append(since.strftime('%Y-%m-%d %H:%M:%S'))
            if count is not None:
                params.append(count)

            # Get our videos.
            cur.execute(stmt, params)
            for row in cur.fetchall():
                videos.append(video.Video()._from_row(row, chan=self))

        return videos

    @property
    def avatar_dir(self):
        """Location of the channel avatar directory."""
        return dirname(abspath(__file__)) + '/static/avatars'

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
        if channel['videos'] is None:
            return self
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
            download_image(url, f'{self.avatar_dir}/{self.channel_id}.jpg')
        except HTTPError as err:
            print(f'{fg.red}Error: Failed to fetch avatar from {url}\n'
                  f'{err}{fg.rs}')

    def _from_row(self, row):
        self.channel_id = row[0]
        self.name = row[1]
        self.description = row[2]

        return self
