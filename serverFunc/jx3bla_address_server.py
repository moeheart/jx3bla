# coding: utf-8
# Lightweight address jump service for jx3blaaddress.moeheart.cn.

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = "127.0.0.1"
PORT = 8033

ADDRESS_DATA = {
    "api": {"host": "116.211.150.188", "port": 8009},
    "logs": {"host": "116.211.150.188", "port": 888},
}


class AddressHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(ADDRESS_DATA).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), AddressHandler)
    print("jx3bla address service listening on %s:%d" % (HOST, PORT))
    server.serve_forever()
