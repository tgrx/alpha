import uvicorn

from framework import config
from main.asgi import application

SERVER_RUNNING_BANNER = """
+----------------------------------------+
|             SERVER WORKS!              |
+----------------------------------------+

Visit http://{host}:{port}

..........................................
"""


def run():
    banner = SERVER_RUNNING_BANNER.format(host=config.HOST, port=config.PORT)
    print(banner)
    try:
        uvicorn.run(application, host="0.0.0.0", port=config.PORT)
    except KeyboardInterrupt:
        print("\n! stopping server\n")
    finally:
        print("\n--- server has been shut down ---\n\n")


if __name__ == "__main__":
    run()
