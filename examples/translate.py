import json
import urllib
import urllib.parse
import urllib.request


def main():
    # tl: タガログ語, pt: ポルトガル語, sl: スロベニア語
    text = "O Monte Fuji é a montanha mais alta do Japão a glavni grad Japana je Tokio Mont Blanc je najvišja gora v Evropi ano ang kabiserang lungsod ng bansa kung saan matatagpuan ang pinakamataas na bundok sa mundo?"

    words = text.split()
    langs = []
    for i in range(0, len(words), 5):
        url = "http://127.0.0.1:5000/detect"
        data = {"q": " ".join(words[i : i + 5])}
        data = urllib.parse.urlencode(data).encode("utf-8")
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Charset": "utf-8",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        req = urllib.request.Request(url, data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                b = resp.read().decode("utf-8")
                j = json.loads(b)
                langs.append(j[0]["language"])
        except urllib.error.HTTPError as e:
            print(e)
            print(e.headers)
            print(e.read().decode("utf-8"))

    langs = list(set(langs))
    print(langs)

    for la in langs:
        url = "http://127.0.0.1:5000/translate"
        d2 = {
            "q": text,
            "source": la,
            "target": "en",
            "format": "text",
        }
        d2 = urllib.parse.urlencode(d2).encode("utf-8")
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Charset": "utf-8",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        req = urllib.request.Request(url, d2, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                b = resp.read().decode("utf-8")
                js = json.loads(b)
                print(la, js["translatedText"])
                # print(json.dumps(j, indent=2))
        except urllib.error.HTTPError as e:
            print(e)
            print(e.headers)
            print(e.read().decode("utf-8"))


if __name__ == "__main__":
    main()
