# Envs

Envs may be set using these mechanisms:

1. Env var syntax - consider reading the docs of your OS.
2. Secrets files in secrets dir. 
3. `.env` file.

Secrets are kept in `config/.secrets/` dir. Usage: create a file, name it as a variable, and post the value into it.

Secrets dir may be different in case of using Docker secrets.

## 1. Server

1. `HOST` is used to mark the hostname which server is running on. Typically, `"localhost"` or `"0.0.0.0"` is ok.
1. `PORT` is a port number server will be listening to.
1. `REQUEST_TIMEOUT` is used by Gunicorn to disconnect requests which consume time over this value.
1. `WEB_CONCURRENCY` is used by Gunicorn to know how many workers to spawn. Typical value is `(Number of CPUs) * 2 + 1`.

## 2. Maintenance

1. `MODE_DEBUG` is a flag, name says its all. Also it influences the logging level.
1. `TEST_SERVICE_URL` is used for tests because operating host:port may differ from test one.
1. `SENTRY_DSN` is used in non-debug mode. If not set, you will not be able to track errors without pain.
1. `HEROKU_APP_NAME` and `HEROKU_API_TOKEN` are required if you want to manage the Heroku app from AMT.

## 3. Database

In order to follow the [12 Factor](https://12factor.net) way,
database should be configured only using `DATABASE_URL` env var.

However, if you want to control components, here they are:

1. `DB_DRIVER`
2. `DB_HOST`
3. `DB_NAME`
4. `DB_PASSWORD`
5. `DB_PORT`
6. `DB_USER`

These two ways are completely independent, no interleaving is between them.
However, if you want to convert one to another, use:

1. `Settings().db_components_from_database_url() -> DatabaseSettings`.
    It splits `DATABASE_URL` value into components and forms a new `DatabaseSettings` object. 
1. `Settings().database_url_from_db_components() -> str`.
    It composes db components into the new url value, which is returned. Existing attributes are not changed.

