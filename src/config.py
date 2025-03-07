from environs import env

env.read_env()

MCR = env.int("MCR", 5)
RPS = env.int("RPS", 10)

GITHUB_ACCESS_TOKEN = env.str("GITHUB_ACCESS_TOKEN", "")

CLICKHOUSE_HOST: str = env.str("CLICKHOUSE_HOST", default="clickhouse")
CLICKHOUSE_PORT: int = env.int("CLICKHOUSE_PORT", default=8123)
CLICKHOUSE_DB: str = env.str("CLICKHOUSE_DB", default="test")
CLICKHOUSE_USER: str = env.str("CLICKHOUSE_USER", default="default")
CLICKHOUSE_PASSWORD: str = env.str("CLICKHOUSE_PASSWORD", default="default")
