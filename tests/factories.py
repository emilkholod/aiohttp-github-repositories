import factory

from dto import Repository, RepositoryAuthorCommitsNum


class RepositoryAuthorCommitsNumFactory(factory.Factory):
    class Meta:
        model = RepositoryAuthorCommitsNum

    author = factory.Faker("name")
    commits_num = factory.Faker("pyint", min_value=0, max_value=1000)


class RepositoryFactory(factory.Factory):
    class Meta:
        model = Repository

    name = factory.Faker("uuid4")
    owner = factory.Faker("name")
    position = factory.Faker("pyint", min_value=0, max_value=1000)
    stars = factory.Faker("pyint", min_value=0, max_value=1000)
    watchers = factory.Faker("pyint", min_value=0, max_value=1000)
    forks = factory.Faker("pyint", min_value=0, max_value=1000)
    language = "some-language"
    authors_commits_num_today = factory.List(
        [factory.SubFactory(RepositoryAuthorCommitsNumFactory) for _ in range(5)]
    )
