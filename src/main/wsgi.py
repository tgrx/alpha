def application(environ, start_response):
    if environ["PATH_INFO"] == "/e/":
        division = 1 / 0

    status = "200 OK"

    headers = {
        "Content-type": "text/html",
    }

    payload = (
        b"<!DOCTYPE html>"
        b"<html>"
        b"<head>"
        b"<title>Alpha</title>"
        b'<meta charset="utf-8">'
        b"</head>"
        b"<body>"
        b"<h1>Project Alpha</h1>"
        b"<hr>"
        b"<p>This is a template project.</p>"
        b"</body>"
        b"</html>"
    )

    start_response(status, list(headers.items()))

    yield payload
