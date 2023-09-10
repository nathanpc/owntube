#!/usr/bin/env python3

import json
from abc import ABC, abstractmethod

class Renderable(ABC):
    """Abstracts an object that can be rendered by the server."""

    @abstractmethod
    def as_dict(self, expand=None):
        """Python dictionary representation of the object."""

    def as_json(self, expand=None):
        """JSON representation of the object."""
        return json.dumps(self.as_dict(expand=expand))
