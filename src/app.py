from wsgiref.simple_server import make_server

from framework import settings
from framework import wsgi
from framework.consts import SERVER_RUNNING_BANNER


def run():
    banner = SERVER_RUNNING_BANNER.format(host=settings.HOST, port=settings.PORT)
    with make_server(settings.HOST, settings.PORT, wsgi.application) as httpd:
        print(banner)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n! stopping server\n")
        finally:
            httpd.shutdown()
            print("\n--- server has been shut down ---\n\n")


if __name__ == "__main__":
    run()
