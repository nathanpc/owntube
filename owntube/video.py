#!/usr/bin/env python3

from datetime import datetime

class Video:
    """Representation of an YouTube video."""

    def __init__(self, channel, video_id, title, description, published_date,
                 duration):
        self.video_id = video_id
        self.channel = channel
        self.title = title
        self.description = description
        self.published_date = published_date
        self.duration = duration

    @staticmethod
    def import_from_dump(channel, video):
        """Imports data from a JSON object inside of a dump made with ytdump."""
        self = Video(channel, video['resourceId']['videoId'],
                     video['title'], video['description'],
                     datetime.fromisoformat(video['publishedAt']), None)
        # TODO: Save the video to the database.

        # TODO: Download thumbnail.

        return self