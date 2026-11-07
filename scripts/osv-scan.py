"""osv-scanner の JSON 出力（--all-packages 付き）を集計し、判定基準に該当するものがあれば失敗する。

使い方: osv-scanner ... --format json --all-packages ... | python3 osv-scan.py [--policy <判定基準>] <名前>
出力: 1 行で完結する形式（grep や awk で扱いやすい形）。人間向けの表示は osv-format.py で整形する
  <名前>: SUMMARY: packages=<数>, Critical=<数>, High=<数>, Medium=<数>, Low=<数>, Unknown=<数>
  <名前>: <種別>: <内容>（種別: CRITICAL / HIGH / FIXABLE / UNDETERMINED / WARNING / NOTE）
判定基準:
  critical      Critical（CVSS 9.0 以上）があれば失敗する（既定）
                High（CVSS 7.0 以上）は表示のみで、失敗にはしない（Medium 以下は件数のみ）
  fixable-high  High 以上（CVSS 7.0 以上）または深刻度不明で、修正版があるものがあれば失敗する
                修正版がないものは警告とし、修正版の有無を判定できないものは失敗とする
                修正版の有無は、OSV のレコードに fixed が記録されているかで判定する（版の大小は比べない）
終了コード: 0 = 該当なし、1 = 該当あり
"""

import argparse
import json
import sys

CRITICAL = 9.0
HIGH = 7.0
MEDIUM = 4.0
LEVELS = ["Critical", "High", "Medium", "Low", "Unknown"]

FIXABLE_MESSAGE = (
    "修正版のある脆弱性があります。docker/mcp/gateway/Dockerfile の版を上げて"
    "（nginx は apk add、それ以外は FROM の digest）、make scan-mcp-nginx で再検査してください。"
)
UNDETERMINED_MESSAGE = "修正版の有無を判定できない脆弱性があります。osv-scanner の出力を確認してください。"


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


def fixed_versions(pkg: dict, ids: list[str]) -> list[str] | None:
    """パッケージ名と ecosystem が一致する OSV のレコードに記録された fixed を返す。

    版の大小は比べない（入っている版が影響を受けることは osv-scanner が判定済み）。
    fixed がなければ空のリストを返す。該当するレコードがなければ None を返す。
    """
    info = pkg["package"]
    found = False
    fixed = []
    for vuln in pkg.get("vulnerabilities") or []:
        if vuln.get("id") not in ids:
            continue
        for affected in vuln.get("affected") or []:
            target = affected.get("package") or {}
            if target.get("name") != info.get("name") or target.get("ecosystem") != info.get("ecosystem"):
                continue
            found = True
            for r in affected.get("ranges") or []:
                for event in r.get("events") or []:
                    if event.get("fixed") and event["fixed"] not in fixed:
                        fixed.append(event["fixed"])
    return fixed if found else None


def fixed_note(fixed: list[str] | None) -> str:
    """fixed_versions() の結果を、表示用の文言にする。"""
    if fixed is None:
        return "修正版の有無は判定できない"
    if fixed:
        return f"修正版: {','.join(fixed)}"
    return "修正版なし"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=["critical", "fixable-high"], default="critical")
    parser.add_argument("name")
    args = parser.parse_args()
    name = args.name
    data = json.load(sys.stdin)
    counts = dict.fromkeys(LEVELS, 0)
    criticals = []
    highs = []
    warnings = []
    fixables = []
    undetermined = []
    packages = 0
    for result in data.get("results") or []:
        for pkg in result.get("packages") or []:
            packages += 1
            info = pkg["package"]
            for group in pkg.get("groups") or []:
                lv = level(group.get("max_severity", ""))
                counts[lv] += 1
                ids = ",".join(group["ids"])
                target = f'{info["name"]}@{info["version"]} {ids}'
                if args.policy == "critical":
                    if lv == "Critical":
                        criticals.append(f"CRITICAL: {target}")
                    elif lv == "High":
                        highs.append(f"HIGH: {target} {fixed_note(fixed_versions(pkg, group['ids']))}")
                    continue
                if lv not in ("Critical", "High", "Unknown"):
                    continue
                fixed = fixed_versions(pkg, group["ids"])
                line = f"{target} {lv} {fixed_note(fixed)}"
                if fixed is None:
                    undetermined.append(f"UNDETERMINED: {line}")
                elif fixed:
                    fixables.append(f"FIXABLE: {line}")
                else:
                    warnings.append(f"WARNING: {line}")
    summary = ", ".join(f"{lv}={counts[lv]}" for lv in LEVELS)
    print(f"{name}: SUMMARY: packages={packages}, {summary}")
    if packages == 0:
        print(f"{name}: WARNING: パッケージを抽出できなかった（スキャン対象外）")
    for line in criticals + highs + warnings + undetermined + fixables:
        print(f"{name}: {line}")
    if undetermined:
        print(f"{name}: NOTE: {UNDETERMINED_MESSAGE}")
    if fixables:
        print(f"{name}: NOTE: {FIXABLE_MESSAGE}")
    return 1 if criticals or fixables or undetermined else 0


if __name__ == "__main__":
    sys.exit(main())
