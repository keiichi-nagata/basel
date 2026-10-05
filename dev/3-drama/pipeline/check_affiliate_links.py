#!/usr/bin/env python3
"""data/<週>.json と drafts/<週>.md を突き合わせ、affiliateが"linked"のサービスが
本文で[PR]リンク化されているかを確認する。

2026-W39・W40で、`providers_jp[].affiliate`が"linked"（提携済み）になっている
サービスが、存在しない「今号は広告表記なしの方針」を理由に本文からプレーンテキストに
戻されてしまう事故が2週連続で発生した。この確認を自動化し、ranking-writerが
ドラフト作成の最後に必ず実行するための軽量チェックスクリプト。

使い方:
  python dev/3-drama/pipeline/check_affiliate_links.py 2026-W40

問題があれば非ゼロ終了する（そのままCIやチェックリストの合否判定に使える）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:  # Windows コンソールの文字化け対策
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


def main() -> int:
    if len(sys.argv) != 2:
        print("使い方: python check_affiliate_links.py <週番号（例: 2026-W40）>")
        return 1

    week = sys.argv[1]
    base = Path(__file__).resolve().parent.parent
    data_path = base / "data" / f"{week}.json"
    draft_path = base / "drafts" / f"{week}.md"

    if not data_path.exists():
        print(f"データファイルが見つかりません: {data_path}")
        return 1
    if not draft_path.exists():
        print(f"ドラフトが見つかりません: {draft_path}")
        return 1

    data = json.loads(data_path.read_text(encoding="utf-8"))
    draft = draft_path.read_text(encoding="utf-8")

    linked: set[str] = set()
    for item in data.get("items", []):
        for p in item.get("providers_jp", []):
            if p.get("affiliate") == "linked":
                linked.add(p["name"])

    if not linked:
        print("提携済み(linked)のサービスはありません。広告表記なしで問題ありません。")
        return 0

    problems: list[str] = []
    if "プロモーション" not in draft and "広告表記" not in draft:
        problems.append("冒頭に広告表記（sop/disclosure.mdの定型文）が見つかりません。")
    for name in sorted(linked):
        if f"[{name}" not in draft or "[PR]" not in draft:
            problems.append(
                f"「{name}」が提携済み(linked)ですが、本文に[{name}...] [PR] 形式のリンクが見つかりません。"
            )

    if problems:
        print("❌ 提携済みアフィリンクの反映漏れの可能性があります:")
        for p in problems:
            print(f"  - {p}")
        print(f"\n提携済みサービス: {', '.join(sorted(linked))}")
        print(
            "\n「今号は広告表記なしの方針」という判断は、社長から明示的な指示があった"
            "場合のみ行ってよい。自分で方針を作り出して外さないこと。"
        )
        return 1

    print(f"✅ 提携済みサービス（{', '.join(sorted(linked))}）はすべて本文でリンク化されています。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
