import socket

# サーバのパラメータ
SERVER_HOST = "localhost"
SERVER_PORT = 8080
SERVER_NAME = "Awesome HTTP Server/v1.0.0"
SERVER_ROOT = "public_html"
BUFSIZE = 4096

dummy_msg = """
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.11.9
Date: Wed, 12 Jun 2024 00:23:34 GMT
Content-type: text/html
Content-Length: 497
Last-Modified: Tue, 11 Jun 2024 23:59:41 GMT

<html>
<head>
<meta charset="utf-8" />
<title>テスト</title>
</head>
<body>
<h1>テスト</h1>
</body>
</html>
"""


def main():
    # ソケットを作成
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.settimeout(1)
    srv_sock.bind((SERVER_HOST, SERVER_PORT))
    srv_sock.listen(10)
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
            clt_sock.send(dummy_msg.encode("utf-8"))

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
