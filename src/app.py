import socketserver

from framework import settings
from framework.server import MyHttp

if __name__ == "__main__":
    with socketserver.TCPServer(("", settings.PORT), MyHttp) as server:
        banner = f"server works! go to http://localhost:{settings.PORT}"
        print(banner)
        server.serve_forever(poll_interval=1)
