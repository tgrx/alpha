# Alpha Management Tool

Alpha Management Tool is a tool like Django manage.py.

It is a CLI tool with verbose help.

## Run it

`python -m alpha.management`

Python, venv, PYTHONPATH must be configured.

Example:

```
❯ PYTHONPATH=src poetry run python -m alpha.management --help
Usage: python -m alpha.management [OPTIONS] COMMAND [ARGS]...

  Alpha Management Tool

Options:
  -v, --verbose  Can be used many times to increase verbosity (spam).
  --help         Show this message and exit.

Commands:
  db      Database Management Tool
  heroku  Heroku Management Tool
```

## Tools

### The `db` tool

Can display various DB settings like name, password etc.

Used in various places where other code needs components from DATABASE_URL or vice versa.

### The `heroku` tool

Can display the app config in JSON format.

Can set up the config vars for your app. Current config vars:

1. PYTHONPATH
2. SENTRY_DSN

Need some secrets to be configured, check its help.
