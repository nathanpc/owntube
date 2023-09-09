#!/usr/bin/env python3
"""A collection of the exceptions found throughout the project."""

class ChannelNotFound(Exception):
    def __init__(self, message = "Channel wasn't found in the database"):
        super().__init__(message)

class VideoNotFound(Exception):
    def __init__(self, message = "Video wasn't found in the database"):
        super().__init__(message)

class SubscriptionFeedFetchError(Exception):
    def __init__(self, message = "An error occurred while fetching the subscriptions"):
        super().__init__(message)

class VideoDownloadError(Exception):
    def __init__(self, message = "An error occurred while downloading the video", data = None):
        super().__init__(message)
        self.data = data
