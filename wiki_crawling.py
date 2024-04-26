import re
import time
import argparse
import http.client
import urllib.parse
from queue import SimpleQueue


def get_pages(conn, title):
    """
    指定されたタイトルのページからリンクされているページのタイトルを取得
    """

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ja",
        "Accept-Charset": "utf-8",
    }
    uri = "/wiki/" + urllib.parse.quote(title)

    # リクエスト送信
    conn.request("GET", uri, headers=headers)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    resp.close()

    # リンクされた記事のタイトルを取得
    p_link = re.compile(r"href=\"/wiki/([^\#:\"]*?)\"")
    titles = p_link.findall(body)
    titles = list(set(titles))
    titles = [urllib.parse.unquote(t) for t in titles]

    return titles


def main():
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=str, metavar="START")
    parser.add_argument("goal", type=str, metavar="GOAL")
    parser.add_argument("--n_max", type=int, default=4)
    args = parser.parse_args()
    start = args.start
    goal = args.goal
    print("Start:", start)
    print("Goal:", goal)

    # クローリング開始
    que = SimpleQueue()
    que.put((start, None, 0))
    checked = {}
    conn = http.client.HTTPSConnection("ja.wikipedia.org")
    while not que.empty():
        # Throttle
        time.sleep(0.1)

        # 新しいページを処理
        title, prev, dist = que.get()
        if title in checked:
            continue
        checked[title] = prev

        pages = get_pages(conn, title)
        print(f"{dist:d}: {title:s} ({len(pages):d} links)")
        if goal in pages:
            checked[goal] = title
            break

        if dist == args.n_max - 1:
            ok = False
            for p in pages:
                if p not in checked:
                    checked[p] = title
                    goal = p
                    ok = True
                    break
            if ok:
                break

        for p in pages:
            if p not in checked:
                que.put((p, title, dist + 1))

    conn.close()

    # 経路の取り出し
    path = [goal]
    while True:
        prev = checked[path[-1]]
        if prev is None:
            break
        path.append(prev)
    path = reversed(path)

    # 結果の表示
    print("")
    print("Answer:")
    print(" -> ".join(path))


if __name__ == "__main__":
    main()
