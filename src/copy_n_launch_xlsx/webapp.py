#!/usr/bin/env python3
"""
copy-n-launch-xlsx web frontend

A tiny HTTP frontend for copy-n-launch-xlsx.

Intended primarily for:

- localhost
- Termux
- LAN testing

This is intentionally minimal.

Business logic belongs in core.py.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import signal
import sys
import threading
import urllib.parse
import time
import webbrowser
import socket
import socketserver
import base64
import pyhabitat

from .core import copy_then_launch
from .paths import (
            APP_NAME, 
            get_target_copy_dir,
            get_icon_path, 
            LOGO_FILENAME_PNG
            )


HOST = "127.0.0.1"
PORT = 8000

SHUTDOWN_EVENT = threading.Event()


# ----------------------------------------------------------------------
# HTML helpers
# ----------------------------------------------------------------------

def page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="en">

<head>

<meta charset="utf-8">

<title>{html.escape(title)}</title>

<style>

body {{
    font-family: system-ui, sans-serif;
    max-width: 700px;
    margin: 40px auto;
    line-height: 1.5;
    background: #f5f5f5;
}}

.card {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,.15);
}}

button {{
    font-size: 1.25rem;
    padding: 1rem 2rem;
    cursor: pointer;
}}

code {{
    background: #efefef;
    padding: .2rem .4rem;
}}

.success {{
    color: green;
}}

.error {{
    color: darkred;
}}

</style>

</head>

<body>

<div class="card">

{body}

</div>

</body>

</html>
""".encode("utf-8")


def home_page() -> bytes:

    destination = html.escape(str(get_target_copy_dir()))

    body = f"""
<h1>{APP_NAME}</h1>

<p>
Launch today's wastewater spreadsheet.
</p>

<form action="/launch" method="post">

<button type="submit">

📄 Copy and Launch Today's Spreadsheet

</button>

</form>

<hr>

<p>

Destination folder:

</p>

<p>

<code>{destination}</code>

</p>

<p>

<a href="/folder">Open Folder</a>

</p>
"""

    return page(APP_NAME, body)


def success_page(destination) -> bytes:

    body = f"""
<h1 class="success">

Success

</h1>

<p>

Created:

</p>

<pre>

{html.escape(str(destination))}

</pre>

<p>

<a href="/">Return Home</a>

</p>
"""

    return page("Success", body)


def already_exists_page(exc: Exception) -> bytes:

    body = f"""
<h1 class="error">

Spreadsheet Already Exists

</h1>

<p>

Today's spreadsheet has already been created.

</p>

<pre>

{html.escape(str(exc))}

</pre>

<p>

<a href="/">Return Home</a>

</p>
"""

    return page("Already Exists", body)


def error_page(exc: Exception) -> bytes:

    body = f"""
<h1 class="error">

Error

</h1>

<pre>

{html.escape(str(exc))}

</pre>

<p>

<a href="/">Return Home</a>

</p>
"""

    return page("Error", body)


# ----------------------------------------------------------------------
# HTTP Handler
# ----------------------------------------------------------------------

class WebHandler(BaseHTTPRequestHandler):

    server_version = "copy-n-launch-xlsx"

    def log_message(self, fmt, *args):
        print(
            f"[{self.log_date_time_string()}] "
            f"{self.client_address[0]} "
            f"{fmt % args}"
        )

    def send_html(self, body: bytes, status: int = 200):

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    # ----------------------------------------------------------

    def do_GET(self):

        path = urllib.parse.urlparse(self.path).path

        if path == "/":
            self.send_html(home_page())
            return

        if path == "/health":

            body = b"OK"

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()

            self.wfile.write(body)
            return

        if path == "/folder":

            try:
                target_dir = get_target_copy_dir()
                pyhabitat.show_system_explorer(target_dir)
            except Exception as e:
                logger.debug(f"Folder {target_dir} failed to be opened: {e}")

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

            return

        if path == "/favicon.ico":
            try:
                ico = get_icon_path(LOGO_FILENAME_ICO)
                data = ico.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception:
                self.send_error(404)
            return

        self.send_error(404)

    # ----------------------------------------------------------

    def do_POST(self):

        path = urllib.parse.urlparse(self.path).path

        if path != "/launch":
            self.send_error(404)
            return

        try:
            result = copy_then_launch()
            destination = result.destination

            self.send_html(success_page(destination))

        except FileExistsError as e:

            self.send_html(
                already_exists_page(e),
                status=409,
            )

        except Exception as e:

            self.send_html(
                error_page(e),
                status=500,
            )

def find_open_port(start: int = 8000) -> int:
    port = start
    while True:
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", port))
            return port
        except OSError:
            port += 1


def launch_browser(url: str) -> None:
    """
    Open the user's default browser.

    Using a tiny delay avoids a race where the browser opens before
    serve_forever() is actually listening.
    """
    threading.Timer(
        0.4,
        lambda: webbrowser.open(url),
    ).start()

# ----------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------

def run_webapp():

    global PORT

    PORT = find_open_port(PORT)

    with ThreadingHTTPServer((HOST, PORT), WebHandler) as httpd:

        def handle_exit():
            if not SHUTDOWN_EVENT.is_set():
                SHUTDOWN_EVENT.set()
                threading.Thread(
                    target=httpd.shutdown,
                    daemon=True,
                ).start()

        signal.signal(signal.SIGINT, lambda *_: handle_exit())
        signal.signal(signal.SIGTERM, lambda *_: handle_exit())

        url = f"http://{HOST}:{PORT}/"

        print(f"Serving {url}")

        launch_browser(url)

        try:
            httpd.serve_forever()

        except KeyboardInterrupt:
            handle_exit()

        finally:
            httpd.server_close()

def run_webapp_defunct(
    host: str = HOST,
    port: int = PORT,
):

    httpd = ThreadingHTTPServer(
        (host, port),
        WebHandler,
    )

    def shutdown():

        if SHUTDOWN_EVENT.is_set():
            return

        SHUTDOWN_EVENT.set()

        print("\nStopping server...")

        threading.Thread(
            target=httpd.shutdown,
            daemon=True,
        ).start()

    signal.signal(signal.SIGINT, lambda *_: shutdown())
    signal.signal(signal.SIGTERM, lambda *_: shutdown())

    print(f"Serving http://{host}:{port}")

    try:
        httpd.serve_forever()

    except KeyboardInterrupt:
        shutdown()

    finally:
        httpd.server_close()
        print("Goodbye.")


if __name__ == "__main__":
    run_webapp()
