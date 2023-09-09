#!/usr/bin/env python3
"""A collection of loggers to use with YoutubeDL."""

from sty import fg

class ConsoleLogger:
    """A regular console logger."""

    def debug(self, msg):
        if not msg.startswith('[debug] '):
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        print(f'{fg.yellow}Error: {msg}{fg.rs}')

    def error(self, msg):
        print(f'{fg.red}Error: {msg}{fg.rs}')
