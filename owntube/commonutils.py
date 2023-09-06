#!/usr/bin/env python3
"""A collection of common utility functions to help us out."""

import requests

def download_image(url, path):
    """Downloads an image from an URL to the specified path."""
    req = requests.get(url, stream=True)
    req.raise_for_status()

    # Write the image out.
    with open(path, 'wb') as fh:
        for chunk in req.iter_content(1024):
            fh.write(chunk)
