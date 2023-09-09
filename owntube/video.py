#!/usr/bin/env python3

from os.path import abspath, dirname
from datetime import datetime

from yt_dlp import YoutubeDL

import json
import requests
from requests.exceptions import HTTPError

from sty import fg

from commonutils import download_image
from database import DatabaseItem
from exceptions import VideoNotFound
import channel

class Video(DatabaseItem):
    """Representation of an YouTube video."""

    def __init__(self, channel = None, video_id = None, title = None,
                 description = None, published_date = None, duration = None,
                 width = None, height = None, fps = None, chapters = None):
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
        self.chapters = chapters

        self._thumbs_dir = dirname(abspath(__file__)) + '/static/thumbnails'

    def from_id(self, id, chan = None):
        # Fetch database row.
        row = self._fetch_by_id('vid', id)
        if row is None:
            raise VideoNotFound()

        # Get the channel if needed.
        if chan is None:
            self.channel = channel.Channel().from_id(row[1])

        # Populate ourselves.
        self.video_id = row[0]
        self.title = row[2]
        self.description = row[3]
        self.published_date = row[4]
        self.duration = row[5]
        self.width = row[6]
        self.height = row[7]
        self.fps = row[8]
        self.chapters = json.loads(row[9])

        # Fetch additional metadata if needed.
        if self.height is None:
            self._fetch_metadata()

        return self

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
            'fps': self.fps,
            'chapters': json.dumps(self.chapters)
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

    def _fetch_metadata(self):
        """Fetches extra metadata and saves it to the database."""
        url = f'https://www.youtube.com/watch?v={self.video_id}'
        with YoutubeDL({}) as ydl:
            info = ydl.sanitize_info(ydl.extract_info(url, download=False))

            # Populate ourselves with the extra metadata.
            self.duration = info['duration']
            self.width = info['width']
            self.height = info['height']
            self.fps = info['fps']
            self.chapters = info['chapters']

            # Commit the changes.
            self.save()
