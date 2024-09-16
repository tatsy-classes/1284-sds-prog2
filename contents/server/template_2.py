import os
import socket
from datetime import datetime
from zoneinfo import ZoneInfo

# サーバのパラメータ
SERVER_HOST = "localhost"
SERVER_PORT = 8080
SERVER_NAME = "Awesome HTTP Server/v1.0.0"
SERVER_ROOT = "public_html"
BUFSIZE = 4096


def main():
    # ソケットを作成
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.settimeout(1)
    srv_sock.bind((SERVER_HOST, SERVER_PORT))
    srv_sock.listen(5)
    print(f"Listening on {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        try:
            # クライアントからの接続を待ち受ける
            clt_sock, clt_addr = srv_sock.accept()
            print(f"Connection from {clt_addr}")

            # データを受信して表示
            msg_bytes = clt_sock.recv(4096)
            msg = msg_bytes.decode("utf-8")
            print(f"Received:\r\n{msg}")

            if msg == "exit":
                break

            # レスポンスを返す
            file_path = os.path.join(SERVER_ROOT, "index.html")
            response = "HTTP/1.0 200 OK\r\n"

            now = datetime.now(ZoneInfo("Asia/Tokyo"))
            date = now.strftime("%a, %d %b %Y %H:%M:%S JST")
            response += f"Date: {date}\r\n"
            response += f"Server: {SERVER_NAME:s}\r\n"

            with open(file_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()

            response += "Content-type: text/html\r\n"
            response += f"Content-Length: {file_size}\r\n"
            response += "Connection: close\r\n"

            response += "\r\n"
            response = response.encode("utf-8")

            with open(file_path, "rb") as f:
                response += f.read()

            clt_sock.send(response)

        except socket.timeout:
            # 接続がタイムアウトしたら、再度接続を待ち受ける
            continue

        except KeyboardInterrupt:
            # Ctrl+Cなどが押されたらループを抜ける
            break

    # ソケットを閉じる
    srv_sock.close()


if __name__ == "__main__":
    main()
