"""osv-scan.py の出力（1 行で完結する形式）を、人間向けの表示に整形する。

使い方: python3 osv-scan.py ... | python3 osv-format.py
入力: <名前>: <種別>: <内容>（osv-scan.py の出力形式）
出力: 名前ごとに見出しの行を出し、その下に内容を 1 文字字下げして並べる（SUMMARY は種別を省く）
  <名前>:
   packages=<数>, Critical=<数>, ...
   HIGH: <内容>
終了コード: 0 = 整形できた、1 = 入力の形式が不正
"""

import sys


def flush(name: str | None, lines: list[str]) -> None:
    if name is None:
        return
    print(f"{name}:")
    for line in lines:
        print(f" {line}")
    sys.stdout.flush()


def main() -> int:
    name = None
    lines: list[str] = []
    for raw in sys.stdin:
        raw = raw.rstrip("\n")
        if not raw:
            continue
        # 名前（イメージ名の "xxx:latest" など）は ": " を含まない前提で、最初の ": " で区切る
        current, sep, rest = raw.partition(": ")
        kind, sep2, body = rest.partition(": ")
        if not sep or not sep2 or not kind.isupper():
            print(f"ERROR: osv-format.py: 入力の形式が不正: {raw}", file=sys.stderr)
            return 1
        if current != name:
            flush(name, lines)
            name, lines = current, []
        lines.append(body if kind == "SUMMARY" else f"{kind}: {body}")
    flush(name, lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
