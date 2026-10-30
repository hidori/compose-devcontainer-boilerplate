"""osv-scanner の JSON 出力（--all-packages 付き）を集計し、Critical があれば失敗する。

使い方: osv-scanner scan source --format json --all-packages ... | python3 osv-summary.py <名前>
終了コード: 0 = Critical なし、1 = Critical あり
"""

import json
import sys

CRITICAL = 9.0
HIGH = 7.0
MEDIUM = 4.0
LEVELS = ["Critical", "High", "Medium", "Low", "Unknown"]


def level(max_severity: str) -> str:
    try:
        score = float(max_severity)
    except ValueError:
        return "Unknown"
    if score >= CRITICAL:
        return "Critical"
    if score >= HIGH:
        return "High"
    if score >= MEDIUM:
        return "Medium"
    return "Low"


def main() -> int:
    name = sys.argv[1]
    data = json.load(sys.stdin)
    counts = dict.fromkeys(LEVELS, 0)
    criticals = []
    packages = 0
    for result in data.get("results") or []:
        for pkg in result.get("packages") or []:
            packages += 1
            for group in pkg.get("groups") or []:
                lv = level(group.get("max_severity", ""))
                counts[lv] += 1
                if lv == "Critical":
                    info = pkg["package"]
                    criticals.append(f'{info["name"]}@{info["version"]} {",".join(group["ids"])}')
    summary = " ".join(f"{lv}={counts[lv]}" for lv in LEVELS)
    print(f"{name}: packages={packages} {summary}")
    if packages == 0:
        print(f"WARNING: {name}: パッケージを抽出できなかった（スキャン対象外）")
    for c in criticals:
        print(f"CRITICAL: {name}: {c}")
    return 1 if criticals else 0


if __name__ == "__main__":
    sys.exit(main())
