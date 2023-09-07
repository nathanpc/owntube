#!/usr/bin/env python3
"""A collection of common utility functions to help us out."""

from os.path import abspath, dirname

import requests
import yaml

def read_config(path = None):
    """Reads the default configuration file or a specific one."""
    # Use the default path if one wasn't provided.
    if path is None:
        path = dirname(dirname(abspath(__file__))) + '/config.yml'

    # Check if we have already cached the configuration file.
    if not hasattr(read_config, 'config'):
        with open(path, 'r') as fh:
            read_config.config = yaml.safe_load(fh)

    return read_config.config

def download_image(url, path):
    """Downloads an image from an URL to the specified path."""
    req = requests.get(url, stream=True)
    req.raise_for_status()

    # Write the image out.
    with open(path, 'wb') as fh:
        for chunk in req.iter_content(1024):
            fh.write(chunk)
