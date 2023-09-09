#!/usr/bin/env python3

from os.path import abspath, dirname
from datetime import datetime

import requests
from requests.exceptions import HTTPError

from sty import fg

from commonutils import download_image
from database import DatabaseItem
import channel

class Video(DatabaseItem):
    """Representation of an YouTube video."""

    def __init__(self, channel = None, video_id = None, title = None,
                 description = None, published_date = None, duration = None,
                 width = None, height = None, fps = None):
        super().__init__('videos')

        self.video_id = video_id
        self.channel = channel
        self.title = title
        self.description = description
        self.published_date = published_date
        self.duration = duration
        self.width = width
        self.height = height
        self.fps = fps

        self._thumbs_dir = dirname(abspath(__file__)) + '/static/thumbnails'

    def save(self):
        self._commit({
            'vid': self.video_id,
            'channel_cid': self.channel.channel_id,
            'title': self.title,
            'description': self.description,
            'published_date': self.published_date.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'fps': self.fps
        })

    def exists(self):
        return self._check_exists('vid', self.video_id)

    @staticmethod
    def import_from_dump(channel, video):
        """Imports data from a JSON object inside of a dump made with ytdump."""
        self = Video(channel, video['resourceId']['videoId'],
                     video['title'], video['description'],
                     datetime.fromisoformat(video['publishedAt']), None)

        # Save the video to the database.
        self.save()

        # Download the thumbnail.
        self._fetch_thumbnail(video['thumbnails'])

        return self

    def _fetch_thumbnail(self, thumbs):
        """Downloads the video's thumbnail from the thumbnails list."""
        url = None

        # Get the highest resolution thumbnail possible.
        resolution = 0
        for name, thumbnail in thumbs.items():
            tbres = thumbnail['width'] * thumbnail['height']
            if tbres > resolution:
                resolution = tbres
                url = thumbnail["url"]

        # Actually download the thumbnail.
        try:
            download_image(url, f'{self._thumbs_dir}/{self.video_id}.jpg')
        except HTTPError as err:
            print(f'{fg.red}Error: Failed to fetch video thumbnail from {url}\n'
                  f'{err}{fg.rs}')
