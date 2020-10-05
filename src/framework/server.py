from http.server import SimpleHTTPRequestHandler


class MyHttp(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(
            b"<!DOCTYPE html>"
            b"<html>"
            b"<head>"
            b"<title>Z37</title>"
            b'<meta charset="utf-8">'
            b"</head>"
            b"<body>"
            b"<h1>Z37 study project</h1>"
            b"<hr>"
            b"<p>This is a study project.</p>"
            b"</body>"
            b"</html>"
        )
