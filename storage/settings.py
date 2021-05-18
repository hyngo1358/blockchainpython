from environs import Env

env = Env()

DEBUG = env.bool('DEBUG', default=False)
DATABASE_PATH = env('DATABASE_PATH', default='/var/lib/chain/main')
