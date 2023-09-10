#!/usr/bin/env python3
"""View abstraction for videos on the platform."""

from datetime import datetime
from flask import Blueprint, request

from owntube.video import Video, DownloadedVideo
from owntube.exceptions import VideoNotFound, OwnTubeBaseException

# Create the view blueprint.
bp = Blueprint('video', __name__, url_prefix='/video')


@bp.route('/')
def list_videos():
    """Lists the videos from all channels."""
    # Get URL parameters.
    count = request.args.get('count', type=int)
    since = request.args.get('since', type=str)
    if since is not None:
        since = datetime.fromisoformat(since)

    # Append video list.
    resp = { 'videos': [] }
    for video in Video().list(count=count, since=since):
        resp['videos'].append(video.__dict__(expand=['channel']))

    return resp

@bp.route('/<id>')
def show(id):
    """Gets detailed information about a single video."""
    video = Video().from_id(id)
    # TODO: Get downloaded videos list.
    return video.__dict__(expand=True)

@bp.errorhandler(VideoNotFound)
def handle_video_not_found(err):
    return { 'error': err.__dict__() }, 404

@bp.errorhandler(OwnTubeBaseException)
def handle_base_exception(err):
    return { 'error': err.__dict__() }, 500
