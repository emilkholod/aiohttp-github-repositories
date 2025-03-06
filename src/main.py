import asyncio
from collections import Counter
from datetime import datetime, timedelta
from types import TracebackType
from typing import Any, Final, Optional, Self, Type

from aiohttp import ClientSession
from aiolimiter import AsyncLimiter

import config
from dto import Repository, RepositoryAuthorCommitsNum
from serializers import RepositorySerialzer

GITHUB_API_BASE_URL: Final[str] = "https://api.github.com"


class GithubReposScrapper:
    semaphore = asyncio.Semaphore(config.MCR)
    limiter = AsyncLimiter(config.RPS)

    def __init__(self, access_token: str):
        self._session = ClientSession(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
            }
        )

    async def _make_request(
        self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None
    ) -> Any:
        async with self._session.request(
            method, f"{GITHUB_API_BASE_URL}/{endpoint}", params=params
        ) as response:
            return await response.json()

    async def _get_top_repositories(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        GitHub REST API:
        https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
        """
        data = await self._make_request(
            endpoint="search/repositories",
            params={
                "q": "stars:>1",
                "sort": "stars",
                "order": "desc",
                "per_page": limit,
            },
        )
        return data["items"]

    async def _get_repository_commits(
        self,
        owner: str,
        repo: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        GitHub REST API:
        https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
        """
        async with self.semaphore, self.limiter:
            # TODO: Iterate over all commits (use link header)
            return await self._make_request(
                endpoint=f"repos/{owner}/{repo}/commits",
                params=params,
            )

    async def get_repositories(self) -> list[Repository]:
        repositories = [
            RepositorySerialzer(r).dto for r in await self._get_top_repositories()
        ]
        params = {"since": (datetime.now() - timedelta(days=1)).isoformat()}
        tasks = [
            self._get_repository_commits(r.owner, r.name, params=params)
            for r in repositories
        ]
        results = await asyncio.gather(*tasks)
        for repo, author_commits_num in zip(repositories, results):
            commits_per_author = Counter(
                c["commit"]["author"]["name"] for c in author_commits_num
            )
            repo.authors_commits_num_today = [
                RepositoryAuthorCommitsNum(author=author, commits_num=commits_num)
                for author, commits_num in commits_per_author.items()
            ]
        return repositories

    async def close(self):
        await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()
