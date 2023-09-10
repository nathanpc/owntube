#!/usr/bin/env python3
"""View abstraction for videos on the platform."""

from flask import Blueprint

from owntube.video import Video, DownloadedVideo

# Create the view blueprint.
bp = Blueprint('auth', __name__, url_prefix='/video')

@bp.route('/<id>')
def show(id):
    video = Video().from_id(id)
    return video.as_dict(expand=True)
