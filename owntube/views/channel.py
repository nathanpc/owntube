#!/usr/bin/env python3
"""View abstraction for a channel on the platform."""

from datetime import datetime
from flask import Blueprint, request

from owntube.channel import Channel
from owntube.exceptions import ChannelNotFound, OwnTubeBaseException

# Create the view blueprint.
bp = Blueprint('channel', __name__, url_prefix='/channel')

@bp.route('/')
def list_channels():
    """Lists all of the channels."""
    # Generate channel list.
    resp = { 'channels': [] }
    for channel in Channel().list():
        resp['channels'].append(channel.__dict__(expand=None))

    return resp

@bp.route('/<id>')
def show(id):
    """Gets detailed information about the channel."""
    channel = Channel().from_id(id)
    return channel.__dict__(expand=True)

@bp.route('/<id>/videos')
def list_videos(id):
    """Lists the videos from the channel."""
    # Get the channel.
    channel = Channel().from_id(id)
    resp = channel.__dict__(expand=True)

    # Get URL parameters.
    count = request.args.get('count', type=int)
    since = request.args.get('since', type=str)
    if since is not None:
        since = datetime.fromisoformat(since)

    # Append video list.
    resp['videos'] = []
    for video in channel.videos(count=count, since=since):
        resp['videos'].append(video.__dict__(expand=None))

    return resp

@bp.errorhandler(ChannelNotFound)
def handle_channel_not_found(err):
    return { 'error': err.__dict__() }, 404

@bp.errorhandler(OwnTubeBaseException)
def handle_base_exception(err):
    return { 'error': err.__dict__() }, 500
