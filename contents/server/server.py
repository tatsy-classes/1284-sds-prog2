import os
import socket
import datetime

SERVER_HOST = "localhost"
SERVER_PORT = 8080
SERVER_NAME = "My first server"
SERVER_ROOT = "public_html"


def main():
    # ソケットを作成
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.settimeout(1)
    srv_sock.bind(("localhost", 8080))
    srv_sock.listen(1)
    print(f"Listening on {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        try:
            # クライアントからの接続を待ち受ける
            clt_sock, clt_addr = srv_sock.accept()
            print(f"Connection from {clt_addr}")

            # データを受信して表示
            data = clt_sock.recv(4096)
            data = data.decode("utf-8")
            print(f"Received:\r\n{data}")

            # リクエストのファイル名を取得
            req_file = data.split("\r\n")[0].split(" ")[1]
            if req_file == "/":
                req_file = "/index.html"

            # レスポンスを作成
            date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            name = SERVER_ROOT + req_file

            _, extension = os.path.splitext(name)
            if extension == ".html":
                content_type = "text/html"
            elif extension == ".css":
                content_type = "text/css"
            elif extension == ".js":
                content_type = "application/javascript"
            elif extension == ".jpg":
                content_type = "image/jpeg"
            elif extension == ".png":
                content_type = "image/png"
            else:
                content_type = "text/plain"

            if os.path.exists(name):
                with open(name, "rb") as f:
                    body = f.read()
            else:
                with open(SERVER_ROOT + "/404.html", "rb") as f:
                    body = f.read()

                response = f"HTTP/1.1 404 Not Found\r\n"
                response += f"Date: {date:s}\r\n"
                response += f"Server: {SERVER_NAME:s}\r\n"
                response += f"Content-Length: len(body)\r\n"
                response += "Content-Type: text/html\r\n"
                response += "\r\n"
                response = response.encode("utf-8")
                response += body

                clt_sock.send(response)
                continue

            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Date: {date:s}\r\n"
            response += f"Server: {SERVER_NAME:s}\r\n"
            response += f"Content-Length: {len(body):d}\r\n"
            response += f"Content-Type: {content_type}\r\n"
            response += f"Keep-Alive: timeout=5, max=100\r\n"
            response += "\r\n"

            response = response.encode("utf-8")
            response += body

            # レスポンスを送信
            clt_sock.send(response)

        except socket.timeout:
            continue

    # ソケットを閉じる
    clt_sock.close()
    srv_sock.close()


if __name__ == "__main__":
    main()
