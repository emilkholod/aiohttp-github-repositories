from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from datetime import date, datetime
from itertools import batched

from aiochclient import ChClient
from aiohttp import ClientSession

import config


class ClickhouseManager(ABC):
    client: ChClient

    @property
    @abstractmethod
    def tablename(self):
        pass

    class ClickhouseDTO(ABC):
        pass

    @classmethod
    def new_object(cls, **data):
        return cls.ClickhouseDTO(**data)

    @classmethod
    def get_client(cls, session=None):
        return ChClient(
            session=session,
            url=f"http://{config.CLICKHOUSE_HOST}:{config.CLICKHOUSE_PORT}/",
            user=config.CLICKHOUSE_USER,
            password=config.CLICKHOUSE_PASSWORD,
            database=config.CLICKHOUSE_DB,
        )

    @classmethod
    async def write(cls, rows):
        if not rows:
            return  # Нечего вставлять

        async with ClientSession() as session:
            client = cls.get_client(session)
            column_names = ", ".join(f.name for f in fields(cls.ClickhouseDTO))
            query = f"INSERT INTO {cls.tablename} ({column_names}) VALUES"

            try:
                for sub_rows in batched(rows, 100):
                    if sub_rows:  # batched может вернуть None
                        await client.execute(query, *sub_rows)
            except Exception as e:
                raise RuntimeError(f"Ошибка при записи в ClickHouse: {e}")


class RepositoryManager(ClickhouseManager):
    tablename = "test.repositories"

    @dataclass
    class ClickhouseDTO:
        name: str
        owner: str
        stars: int
        watchers: int
        forks: int
        language: str
        updated: datetime


class RepositoriesAuthorsCommitsManager(ClickhouseManager):
    tablename = "test.repositories_authors_commits"

    @dataclass
    class ClickhouseDTO:
        date: date
        repo: str
        author: str
        commits_num: int


class RepositoriesPositionsManager(ClickhouseManager):
    tablename = "test.repositories_positions"

    @dataclass
    class ClickhouseDTO:
        date: date
        repo: str
        position: int
