import regex


def main():
    lines = []
    with open("wagahai.txt", "r") as fp:
        lines = fp.readlines()

    p_yoji = regex.compile(r"\P{Han}{0,1}?(\p{Han}{4})\P{Han}{0,1}")
    yoji = []
    for ln in lines:
        matches = p_yoji.findall(ln)
        yoji.extend(matches)
    print(f"四字熟語は{len(yoji):d}個見つかりました(重複なしで{len(set(yoji))}個)。")
    print(yoji)

    p_juku = regex.compile(r"\P{Han}{0,1}?(\p{Han}+)\P{Han}{0,1}")
    juku = []
    for ln in lines:
        matches = p_juku.findall(ln)
        juku.extend(matches)

    longest = max(juku, key=lambda x: len(x))
    print(f"最も長い熟語は{len(longest):d}文字で「{longest:s}」です。")


if __name__ == "__main__":
    main()
