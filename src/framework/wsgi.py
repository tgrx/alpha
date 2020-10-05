def application(environ, start_response):
    status = "200 OK"
    headers = {
        "Content-type": "text/html",
    }
    payload = (
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

    start_response(status, list(headers.items()))

    yield payload
