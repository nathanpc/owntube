#!/usr/bin/env python3

from abc import ABC, abstractmethod

from owntube.utils.commonutils import db_connect

class DatabaseItem(ABC):
    """Abstracts the relationship between objects and database items."""

    def __init__(self, table):
        self.conn = db_connect()
        self.table = table

    @abstractmethod
    def from_id(self, id):
        """Fetches an object from the database via its ID."""

    @abstractmethod
    def list(self):
        """Gets a list of our objects from the database."""

    @abstractmethod
    def _from_row(self, row):
        """Populates an object using a database row."""

    def _fetch_by_id(self, column, id):
        """Fetches an object from the database via its ID column."""
        with self.conn.cursor() as cur:
            cur.execute(f'SELECT * FROM {self.table} WHERE {column} = %s', [id])
            return cur.fetchone()

    @abstractmethod
    def save(self):
        """Commits changes made to the object to the database."""

    def _commit(self, params):
        """Inserts or updates a database item parameters automagically."""
        # Prepare the SQL statement.
        statement = f'INSERT INTO {self.table}({", ".join(params)}) VALUES ' \
                    f'({"%s, " * (len(params) - 1)}%s) ON DUPLICATE KEY UPDATE '
        for col in list(params)[:-1]:
            statement += f'{col} = %s, '
        statement += f'{list(params)[-1]} = %s'

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
                        f'WHERE {column} = %s)', [value])
            return cur.fetchone()[0] == 0
