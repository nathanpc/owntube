#!/usr/bin/env python3

import mariadb
from abc import ABC, abstractmethod

from commonutils import db_connect

class DatabaseItem(ABC):
    """Abstracts the relationship between objects and database items."""

    def __init__(self, table, is_new = True):
        self.conn = db_connect()
        self.table = table

    @abstractmethod
    def save(self):
        """Commits changes made to the object to the database."""

    def _commit(self, params):
        """Inserts or updates a database item parameters automagically."""
        # Prepare the SQL statement.
        statement = f'INSERT INTO {self.table}({", ".join(params)}) VALUES ' \
                    f'({"?, " * (len(params) - 1)}?) ON DUPLICATE KEY UPDATE '
        for col in list(params)[:-1]:
            statement += f'{col} = ?, '
        statement += f'{list(params)[-1]} = ?'

        # Commit the changes to the database.
        with self.conn.cursor() as cur:
            values = list(params.values()) + list(params.values())
            cur.execute(statement, values)

    @abstractmethod
    def exists(self):
        """Checks in the database if the item already exists via its ID."""

    def _check_exists(self, column, value):
        """Checks if an item exists based on a column and its value."""
        with self.conn.cursor() as cur:
            cur.execute(f'SELECT EXISTS(SELECT {column} FROM {self.table} '
                        f'WHERE {column} = ?)', value)
            return cur.fetchone()[0] == 0