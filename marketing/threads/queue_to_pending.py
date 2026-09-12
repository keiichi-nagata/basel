#!/usr/bin/env python3
"""Basel の告知ドラフトを threads-app の承認待ちキューに登録する。

開発部（2/3/4/5/6部）で記事を公開したら、告知文をこのスクリプトで
threads-app（別リポジトリ）の Supabase: manual_posts テーブルに送る。
threads-app 側の Streamlit 画面「承認待ち」に表示され、社長が承認すると
既存の Threads 投稿の仕組み（公式API）でそのまま投稿される。

Supabase の接続情報は Basel リポジトリには置かず、threads-app の .env を
そのまま読む（同じシークレットを2つのリポジトリで二重管理しない）。
threads-app の場所が変わったら THREADS_APP_ENV を書き換える。

## UTM計測（2026-09-12〜）
noteのダッシュボードだけでは、Threads/Instagramアプリ内ブラウザ経由の流入が
「note.com」（記事間の回遊後）や「no referrer」（リファラーを送らないアプリ内WebView）に
紛れて過小評価される。これを避けるため、--link に渡したURLへ自動で
utm_source=threads&utm_medium=social&utm_campaign=<--sourceから生成> を付与し、
--content 中の同じURL文字列も置換してから送信する（--no-utm で無効化できる）。

使い方:
  python marketing/threads/queue_to_pending.py \
      --source "basel:5-finance-manga:02" \
      --content "本文（500字以内）... https://note.com/basel5/n/xxxx" \
      --link "https://note.com/basel5/n/xxxx"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

try:  # Windows コンソールの文字化け対策
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

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


def _slugify_campaign(source: str) -> str:
    """"basel:6-markets:2026-08" -> "6-markets-2026-08" """
    slug = source.split(":", 1)[1] if ":" in source else source
    slug = re.sub(r"[^0-9A-Za-z._-]+", "-", slug).strip("-")
    return slug or "basel"


def _add_utm(link: str, source: str, medium: str, campaign: str) -> str:
    parts = urlsplit(link)
    query = dict(parse_qsl(parts.query))
    query.update({"utm_source": source, "utm_medium": medium, "utm_campaign": campaign})
    return urlunsplit(parts._replace(query=urlencode(query)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True,
                     help='由来。例: "basel:5-finance-manga:02" "basel:2-cars:2026-08"')
    ap.add_argument("--content", required=True, help="投稿本文")
    ap.add_argument("--link", default=None, help="参照URL（note記事など・任意）")
    ap.add_argument("--utm-campaign", default=None, help="utm_campaignを明示指定（省略時は--sourceから自動生成）")
    ap.add_argument("--no-utm", action="store_true", help="UTM自動付与を無効化する")
    args = ap.parse_args()

    content = args.content
    link = args.link
    if link and not args.no_utm:
        campaign = args.utm_campaign or _slugify_campaign(args.source)
        tagged = _add_utm(link, source="threads", medium="social", campaign=campaign)
        if link in content:
            content = content.replace(link, tagged)
        else:
            print(f"[queue_to_pending] 注意: --content 内に --link のURLが見つからず、"
                  "本文へのUTM付与はスキップしました（link_urlメタデータのみ付与）。", file=sys.stderr)
        link = tagged
        print(f"[queue_to_pending] UTM付与: {link}")

    if len(content) > THREADS_CHAR_LIMIT:
        print(f"⚠️ 本文が{THREADS_CHAR_LIMIT}字を超えています（{len(content)}字）。"
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
        json={"source": args.source, "content": content, "link_url": link},
        timeout=30,
    )
    if res.status_code >= 400:
        print(res.status_code, res.text, file=sys.stderr)
        res.raise_for_status()

    print("[queue_to_pending] 登録しました。threads-app の「承認待ち」画面に表示されます。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
