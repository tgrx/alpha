import json
from contextlib import closing

import psycopg2

from framework import config


def main():
    if not config.DATABASE_URL:
        return {}

    with closing(psycopg2.connect(config.DATABASE_URL)) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pg_config;")
        result = dict(cursor.fetchall())
        js = json.dumps(result, indent=2, sort_keys=True)
        return js


if __name__ == "__main__":
    print(main())
