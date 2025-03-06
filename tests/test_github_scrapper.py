import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from aiolimiter import AsyncLimiter

from main import GithubReposScrapper


@pytest.mark.asyncio
async def test_get_repositories(mock_aiohttp_session):
    # Создаем экземпляр скраппера с фиктивным токеном доступа
    async with GithubReposScrapper(access_token="fake_token") as scrapper:
        # Настраиваем mock для метода _make_request
        mock_response_repos = {
            "items": [
                {
                    "name": "repo1",
                    "owner": {"login": "owner1"},
                    "position": 500,
                    "stars": 100,
                    "watchers": 50,
                    "forks": 20,
                    "language": "Python",
                    "some_extra_field": "some_extra_value",
                },
                {
                    "name": "repo2",
                    "owner": {"login": "owner2"},
                    "position": 400,
                    "stars": 200,
                    "watchers": 80,
                    "forks": 30,
                    "language": "JavaScript",
                    "some_extra_field": "some_extra_value",
                },
            ]
        }

        mock_response_commits_repo1 = [
            {"commit": {"author": {"name": "author1", "date": "2025-03-05T10:00:00Z"}}},
            {"commit": {"author": {"name": "author2", "date": "2025-03-05T09:00:00Z"}}},
            {"commit": {"author": {"name": "author1", "date": "2025-03-05T08:00:00Z"}}},
        ]

        mock_response_commits_repo2 = [
            {"commit": {"author": {"name": "author3", "date": "2025-03-05T08:00:00Z"}}}
        ]

        async def mock_make_request(endpoint, method="GET", params=None):
            if endpoint == "search/repositories":
                return mock_response_repos
            elif endpoint == "repos/owner1/repo1/commits":
                return mock_response_commits_repo1
            elif endpoint == "repos/owner2/repo2/commits":
                return mock_response_commits_repo2
            return []

        scrapper._make_request = AsyncMock(side_effect=mock_make_request)

        # Выполняем тестируемый метод
        repositories = await scrapper.get_repositories()

        # Проверяем результаты
        assert len(repositories) == 2

        repo1 = repositories[0]
        assert repo1.name == "repo1"
        assert repo1.owner == "owner1"
        assert repo1.stars == 100
        assert repo1.watchers == 50
        assert repo1.forks == 20
        assert repo1.language == "Python"
        assert len(repo1.authors_commits_num_today) == 2
        assert repo1.authors_commits_num_today[0].author == "author1"
        assert repo1.authors_commits_num_today[0].commits_num == 2
        assert repo1.authors_commits_num_today[1].author == "author2"
        assert repo1.authors_commits_num_today[1].commits_num == 1

        repo2 = repositories[1]
        assert repo2.name == "repo2"
        assert repo2.owner == "owner2"
        assert repo2.stars == 200
        assert repo2.watchers == 80
        assert repo2.forks == 30
        assert repo2.language == "JavaScript"
        assert len(repo2.authors_commits_num_today) == 1
        assert repo2.authors_commits_num_today[0].author == "author3"
        assert repo2.authors_commits_num_today[0].commits_num == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_counter, semaphore_value, limiter_max_rate, limiter_time_period",
    [
        (4, 4, 1, 1 / 4),
        (4, 1, 4, 1),
    ],
)
async def test_requests(
    mock_aiohttp_session,
    task_counter: int,
    semaphore_value: int,
    limiter_max_rate: int,
    limiter_time_period: float,
):
    # Создаем экземпляр скраппера с фиктивным токеном доступа
    async with GithubReposScrapper(access_token="fake_token") as scrapper:

        async def mock_make_request(endpoint, method="GET", params=None):
            await asyncio.sleep(1 / task_counter)
            return []

        scrapper._make_request = AsyncMock(side_effect=mock_make_request)

        tasks = [
            scrapper._get_repository_commits("test", "test")
            for _i in range(task_counter)
        ]
        with (
            patch.object(scrapper, "semaphore", asyncio.Semaphore(semaphore_value)),
            patch.object(
                scrapper,
                "limiter",
                AsyncLimiter(limiter_max_rate, time_period=limiter_time_period),
            ),
        ):
            elapsed = time.monotonic()
            await asyncio.gather(*tasks)
            delta = time.monotonic() - elapsed
            assert 1 <= delta < 1.1
