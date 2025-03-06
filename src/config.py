from environs import env

env.read_env()

MCR = env.int("MCR", 5)
RPS = env.int("RPS", 10)
