from dataclasses import asdict, astuple
from datetime import datetime

import clickhouse
from dto import Repository


async def save_repositories(repositories: list[Repository]):
    await clickhouse.RepositoryManager.write(
        _get_transformed_repositories(repositories)
    )
    await clickhouse.RepositoriesAuthorsCommitsManager.write(
        _get_transformed_repositories_author_commits(repositories),
    )
    await clickhouse.RepositoriesPositionsManager.write(
        _get_transformed_repositories_positions(repositories),
    )


def _get_transformed_repositories(repositories: list[Repository]):
    result = []
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for repository in repositories:
        repository_data = asdict(repository)

        repository_data.pop("position", None)
        repository_data.pop("authors_commits_num_today", None)

        result.append(
            astuple(
                clickhouse.RepositoryManager.new_object(
                    **repository_data,
                    updated=updated,
                )
            )
        )
    return result


def _get_transformed_repositories_author_commits(repositories: list[Repository]):
    result = []
    today = datetime.today().strftime("%Y-%m-%d")
    for repository in repositories:
        for authors_commits_num_today in repository.authors_commits_num_today:
            authors_commits_num_today_data = asdict(authors_commits_num_today)

            result.append(
                astuple(
                    clickhouse.RepositoriesAuthorsCommitsManager.new_object(
                        **authors_commits_num_today_data,
                        repo=repository.name,
                        date=today,
                    )
                )
            )
    return result


def _get_transformed_repositories_positions(repositories: list[Repository]):
    result = []
    today = datetime.today().strftime("%Y-%m-%d")
    for repository in repositories:
        result.append(
            astuple(
                clickhouse.RepositoriesPositionsManager.new_object(
                    position=repository.position,
                    repo=repository.name,
                    date=today,
                )
            )
        )
    return result
