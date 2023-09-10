#!/usr/bin/env python3

import os
from os.path import abspath, dirname
from datetime import datetime

from yt_dlp import YoutubeDL

import json
import requests
from requests.exceptions import HTTPError

from sty import fg

from owntube.utils.commonutils import download_image
from owntube.utils.database import DatabaseItem
from owntube.utils.loggers import ConsoleLogger
from owntube.utils.renderable import Renderable
from owntube.exceptions import VideoNotFound, VideoDownloadError
import owntube.channel as channel

class Video(DatabaseItem, Renderable):
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

    def __dict__(self, expand=None):
        # Build up the base structure.
        d = {
            'id': self.video_id,
            'title': self.title,
            'description': self.description,
            'published_date': self.published_date,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'chapters': self.chapters
        }

        # Expand the channel?
        if expand is not None:
            d['channel'] = self.channel.__dict__()

        return d

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
        self.chapters = None if (row[9] is None) else json.loads(row[9])

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
            'chapters': None if (self.chapters is None) else
                json.dumps(self.chapters)
        })

    def exists(self):
        return self._check_exists('vid', self.video_id)

    def download(self, height, logger = ConsoleLogger()):
        """Downloads a video in a specific resolution."""
        # Setup the options for the download.
        opts = {
            'outtmpl': {
                'default': f'{self.video_dir}/{self.video_id}_{height}.mp4'
            },
            'format': f'bestvideo[ext=mp4][height<=?{height}]+'
                       'bestaudio[ext=m4a]/best',
            'format_sort': ['vcodec:h264'],
            'extract_flat': 'discard_in_playlist',
            'fragment_retries': 10,
            'ignoreerrors': 'only_download',
            'retries': 10,
            'logger': logger,
            'progress_hooks': [self._download_hook]
        }

        # Perform the download.
        with YoutubeDL(opts) as ydl:
            ydl.download(self.url)

    @property
    def url(self):
        """Original YouTube URL to this video."""
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    @staticmethod
    def thumbs_dir():
        """Location of the thumbnails directory."""
        return dirname(dirname(abspath(__file__))) + '/static/thumbnails'

    @property
    @staticmethod
    def video_dir():
        """Location of the video files directory."""
        return dirname(dirname(abspath(__file__))) + '/static/videos'

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
            download_image(url, f'{self.thumbs_dir}/{self.video_id}.jpg')
        except HTTPError as err:
            print(f'{fg.red}Error: Failed to fetch video thumbnail from {url}\n'
                  f'{err}{fg.rs}')

    def _fetch_metadata(self):
        """Fetches extra metadata and saves it to the database."""
        with YoutubeDL({}) as ydl:
            info = ydl.sanitize_info(ydl.extract_info(self.url, download=False))

            # Populate ourselves with the extra metadata.
            self.duration = info['duration']
            self.width = info['width']
            self.height = info['height']
            self.fps = info['fps']
            self.chapters = info['chapters']

            # Commit the changes.
            self.save()

    def _download_hook(self, data):
        """Responds to events fired by a YoutubeDL download."""
        if data['status'] == 'finished':
            info = data['info_dict']

            print(f'{fg.green}Downloaded {data["filename"]}{fg.rs}')
            if info['ext'] == 'mp4':
                # Save information about the downloaded video to the database.
                download = DownloadedVideo(
                    None, self, info['width'], info['height'], info['fps'],
                    data['total_bytes'], info['ext'])
                download.save()
        elif data['status'] == 'error':
            raise VideoDownloadError(data = data)

class DownloadedVideo(DatabaseItem):
    """Representation of a local video."""

    def __init__(self, id = None, video = None, width = None, height = None,
                 fps = None, filesize = None, extension = None):
        super().__init__('downloaded_videos')

        self.id = id
        self.video = video
        self.width = width
        self.height = height
        self.fps = fps
        self.filesize = filesize
        self.extension = extension

    def from_id(self, id, video = None):
        # Fetch database row.
        row = self._fetch_by_id('id', id)
        if row is None:
            raise VideoNotFound("Downloaded video wasn't found")

        # Get the video if needed.
        if video is None:
            self.video = Video().from_id(row[1])

        # Populate ourselves.
        self.id = row[0]
        self.width = row[2]
        self.height = row[3]
        self.fps = row[4]
        self.filesize = row[5]
        self.extension = row[6]

        return self

    def save(self):
        self._commit({
            'id': self.id,
            'vid': self.video.video_id,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'filesize': self.filesize,
            'extension': self.extension
        })

    def exists(self):
        return self._check_exists('id', self.id)

    @property
    def path(self):
        """Path to where the video is located at."""
        return f'{Video.video_dir}/{self.video.video_id}_{self.height}.mp4'
