#!/usr/bin/env python3
"""View abstraction for videos on the platform."""

from flask import Blueprint

from owntube.video import Video, DownloadedVideo
from owntube.exceptions import VideoNotFound, OwnTubeBaseException

# Create the view blueprint.
bp = Blueprint('video', __name__, url_prefix='/video')

@bp.route('/<id>')
def show(id):
    video = Video().from_id(id)
    return video.__dict__(expand=True)

@bp.errorhandler(VideoNotFound)
def handle_video_not_found(err):
    return { 'error': err.__dict__() }, 404

@bp.errorhandler(OwnTubeBaseException)
def handle_base_exception(err):
    return { 'error': err.__dict__() }, 500
