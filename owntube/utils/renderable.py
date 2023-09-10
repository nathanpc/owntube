#!/usr/bin/env python3

import json
from abc import ABC, abstractmethod

class Renderable(ABC):
    """Abstracts an object that can be rendered by the server."""

    def to_json(self, expand=None):
        """JSON representation of the object."""
        return json.dumps(self.__dict__(expand=expand))
