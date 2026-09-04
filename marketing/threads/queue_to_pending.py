#!/usr/bin/env python3
"""Basel の告知ドラフトを threads-app の承認待ちキューに登録する。

開発部（2/3/5部）で記事を公開したら、告知文をこのスクリプトで
threads-app（別リポジトリ）の Supabase: manual_posts テーブルに送る。
threads-app 側の Streamlit 画面「承認待ち」に表示され、社長が承認すると
既存の Threads 投稿の仕組み（公式API）でそのまま投稿される。

Supabase の接続情報は Basel リポジトリには置かず、threads-app の .env を
そのまま読む（同じシークレットを2つのリポジトリで二重管理しない）。
threads-app の場所が変わったら THREADS_APP_ENV を書き換える。

使い方:
  python marketing/threads/queue_to_pending.py \
      --source "basel:5-finance-manga:02" \
      --content "本文（500字以内）..." \
      --link "https://note.com/basel5/n/xxxx"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

THREADS_APP_ENV = Path(r"C:\Claude\プライベート\投資\threads-app\.env")
THREADS_CHAR_LIMIT = 500


def _load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        raise SystemExit(
            f"threads-app の .env が見つかりません: {path}\n"
            "THREADS_APP_ENV のパスが合っているか確認してください。"
        )
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True,
                     help='由来。例: "basel:5-finance-manga:02" "basel:2-cars:2026-08"')
    ap.add_argument("--content", required=True, help="投稿本文")
    ap.add_argument("--link", default=None, help="参照URL（note記事など・任意）")
    args = ap.parse_args()

    if len(args.content) > THREADS_CHAR_LIMIT:
        print(f"⚠️ 本文が{THREADS_CHAR_LIMIT}字を超えています（{len(args.content)}字）。"
              "Threadsの文字数制限に注意してください。", file=sys.stderr)

    env = _load_env(THREADS_APP_ENV)
    url, key = env.get("SUPABASE_URL"), env.get("SUPABASE_KEY")
    if not url or not key:
        raise SystemExit("SUPABASE_URL / SUPABASE_KEY が threads-app の .env から読めませんでした")

    res = requests.post(
        f"{url}/rest/v1/manual_posts",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json={"source": args.source, "content": args.content, "link_url": args.link},
        timeout=30,
    )
    if res.status_code >= 400:
        print(res.status_code, res.text, file=sys.stderr)
        res.raise_for_status()

    print("[queue_to_pending] 登録しました。threads-app の「承認待ち」画面に表示されます。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
