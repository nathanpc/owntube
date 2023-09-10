#!/usr/bin/env python3
"""View abstraction for a channel on the platform."""

from flask import Blueprint

from owntube.channel import Channel
from owntube.exceptions import ChannelNotFound, OwnTubeBaseException

# Create the view blueprint.
bp = Blueprint('channel', __name__, url_prefix='/channel')

@bp.route('/<id>')
def show(id):
    channel = Channel().from_id(id)
    return channel.__dict__(expand=True)

@bp.errorhandler(ChannelNotFound)
def handle_channel_not_found(err):
    return { 'error': err.__dict__() }, 404

@bp.errorhandler(OwnTubeBaseException)
def handle_base_exception(err):
    return { 'error': err.__dict__() }, 500
