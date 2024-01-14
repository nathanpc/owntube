#!/usr/bin/env python3

from flask import Flask

from owntube.views import channel, video

# Define the global flask application object.
app = Flask(__name__)

# Set up the Flask paths.
app.static_url_path = ''
app.static_folder = app.root_path + '/owntube/static'
app.template_folder = app.root_path + '/owntube/templates'

# Register blueprints.
app.register_blueprint(channel.bp)
app.register_blueprint(video.bp)

if __name__ == '__main__':
    app.run()
