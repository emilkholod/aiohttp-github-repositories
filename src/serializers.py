from copy import deepcopy
from dataclasses import fields
from typing import Any

from dto import Repository


class RepositorySerialzer:
    dataclass_fields = {f.name for f in fields(Repository)}

    def __init__(self, response_data: dict[str, Any]):
        self.response_data = response_data

    @property
    def dto(self):
        repository_data = deepcopy(self.response_data)
        repository_data["owner"] = repository_data["owner"]["login"]
        return Repository(
            **{k: v for k, v in repository_data.items() if k in self.dataclass_fields}
        )
