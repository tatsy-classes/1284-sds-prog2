import os
import re
import socket
from datetime import datetime
from zoneinfo import ZoneInfo
from threading import Thread

# サーバのパラメータ
SERVER_HOST = "localhost"
SERVER_PORT = 8080
SERVER_NAME = "Awesome HTTP Server/v1.0.0"
SERVER_ROOT = "public_html"
BUFSIZE = 4096


def handle_error(clt_sock, msg):
    content = ""
    with open(SERVER_ROOT + "/error.html", "r") as f:
        content = f.read()
        content = content.replace("{{ error }}", msg)

    response = f"HTTP/1.0 {msg:s}\r\n"

    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    date = now.strftime("%a, %d %b %Y %H:%M:%S JST")
    response += f"Date: {date}\r\n"

    response += f"Server: {SERVER_NAME:s}\r\n"
    response += "Content-Type: text/html\r\n"
    response += f"Content-Length: {len(content):d}\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
    response += content

    clt_sock.send(response.encode("utf-8"))
    clt_sock.close()


class ClientHandler(Thread):
    def __init__(self, clt_sock, clt_addr):
        super(ClientHandler, self).__init__(daemon=True)
        self.clt_sock = clt_sock
        self.clt_addr = clt_addr

    def run(self):
        # データを受信して表示
        req_bytes = self.clt_sock.recv(4096)
        request = req_bytes.decode("utf-8")
        print(f"Received:\r\n{request}", flush=True)

        # レスポンスを返す
        lines = re.split("[\r\n]{1,2}", request)
        pattern = re.compile("(GET|POST)\s+(\S+?)\s+HTTP/([0-9\.]+)")
        matches = pattern.match(lines[0])
        if not matches:
            handle_error(self.clt_sock, "400 Bad Request")
            return

        # サブグループの取得
        file_path = matches.group(2)
        if file_path == "/":
            file_path = "/index.html"

        file_path = SERVER_ROOT + file_path
        response = "HTTP/1.0 200 OK\r\n"

        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date = now.strftime("%a, %d %b %Y %H:%M:%S JST")
        response += f"Date: {date}\r\n"
        response += f"Server: {SERVER_NAME:s}\r\n"

        content_type = "text/html"
        file_size = 0

        try:
            with open(file_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()

        except FileNotFoundError:
            handle_error(self.clt_sock, "404 File not found")
            return
        except PermissionError:
            handle_error(self.clt_sock, "403 Forbidden")
            return

        _, extension = os.path.splitext(file_path)
        if extension == ".html" or extension == ".htm":
            content_type = "text/html"
        elif extension == ".css":
            content_type = "text/css"
        elif extension == ".jpg" or extension == ".jpeg":
            content_type = "image/jpeg"
        elif extension == ".png":
            content_type = "image/png"
        else:
            raise Exception("Unknown file type!!")

        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {file_size}\r\n"
        response += "Connection: close\r\n"

        ts = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(ts, ZoneInfo("Asia/Tokyo"))
        last_modified = dt.strftime("%a, %d %b %Y %H:%M:%S JST")
        response += f"Last-Modified: {last_modified}\r\n"

        response += "\r\n"
        response = response.encode("utf-8")

        with open(file_path, "rb") as f:
            response += f.read()

        self.clt_sock.send(response)
        self.clt_sock.close()


def main():
    # ソケットを作成
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.settimeout(1)
    srv_sock.bind((SERVER_HOST, SERVER_PORT))
    srv_sock.listen(10)
    print(f"Listening on {SERVER_HOST}:{SERVER_PORT}...", flush=True)

    clt_sock = None
    while True:
        try:
            # クライアントからの接続を待ち受ける
            clt_sock, clt_addr = srv_sock.accept()
            print(f"Connection from {clt_addr}", flush=True)
            handler = ClientHandler(clt_sock, clt_addr)
            handler.start()
        except socket.timeout:
            # 接続がタイムアウトしたら、再度接続を待ち受ける
            continue

        except KeyboardInterrupt:
            # Ctrl+Cなどが押されたらループを抜ける
            break

    # ソケットを閉じる
    if clt_sock:
        clt_sock.close()

    if srv_sock:
        srv_sock.close()


if __name__ == "__main__":
    main()
