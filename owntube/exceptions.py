#!/usr/bin/env python3
"""A collection of the exceptions found throughout the project."""

class OwnTubeBaseException(Exception):
    def __dict__(self):
        return {
            'type': self.__class__.__name__,
            'message': str(self),
            'args': self.args
        }

class ChannelNotFound(OwnTubeBaseException):
    def __init__(self, message = "Channel wasn't found in the database"):
        super().__init__(message)

class VideoNotFound(OwnTubeBaseException):
    def __init__(self, message = "Video wasn't found in the database"):
        super().__init__(message)

class SubscriptionFeedFetchError(OwnTubeBaseException):
    def __init__(self, message = "An error occurred while fetching the subscriptions"):
        super().__init__(message)

class VideoDownloadError(OwnTubeBaseException):
    def __init__(self, message = "An error occurred while downloading the video", data = None):
        super().__init__(message)
        self.data = data
