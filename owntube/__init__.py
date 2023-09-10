#!/usr/bin/env python3

from owntube.video import Video, DownloadedVideo
from owntube.channel import Channel

def create_app():
    """Creates the Flask application."""
    # Create flask application.
    from flask import Flask
    app = Flask(__name__)

    # Import views.
    from owntube.views import channel, video

    # Register blueprints.
    app.register_blueprint(channel.bp)
    app.register_blueprint(video.bp)

    return app

if __name__ == '__main__':
    create_app()
