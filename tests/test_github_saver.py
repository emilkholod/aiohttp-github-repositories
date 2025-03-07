import pytest
from tests.factories import RepositoryFactory

from github_repos_saver import save_repositories


@pytest.mark.asyncio
async def test_save_repositories():
    repositories = RepositoryFactory.create_batch(10)
    await save_repositories(repositories)
