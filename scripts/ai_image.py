#!/usr/bin/env python3
"""OpenAI Images API で背景アート画像を生成する共通スクリプト（全部門で共用）。

**方針**: この画像に日本語のタイトル・数値・表を焼き込ませない（生成AIは長文・和文・数値の
描画を誤りやすいため）。ここで作るのはあくまで「背景の絵」で、タイトルや日付・ランキング表は
これまで通り各部の `make_eyecatch.py` / `make_ranking_table.py`（matplotlib）で上から重ねる
（=ハイブリッド方式。データの正確性はプログラム側で担保する）。

**費用に注意**: 1回の呼び出しごとに数円〜数十円の実費がかかる（従量課金）。デザインを
決めるまでの試行錯誤で複数回叩くことになるので、無闇に連打しない。

前提:
  - https://platform.openai.com で組織の支払い方法を登録済み（ChatGPT Plusとは別課金）
  - https://platform.openai.com/api-keys で発行したキーを、リポジトリ直下の `.env`
    （コミットされない）に `OPENAI_API_KEY=...` として保存済み

使い方:
  python scripts/ai_image.py \
      --prompt "北海道の温泉と紅葉をイメージした、明るいクリーム地にテラコッタのアクセント..." \
      --orientation landscape \
      --out dev/4-onsen/omiyage/assets/2026-10/bg.png

  orientation: landscape（note用サムネ想定・生成1536x1024→1280x670にトリミング）
             / portrait（Instagram用想定・生成1024x1536→1080x1350にトリミング）
             / square（1024x1024のまま）
"""
from __future__ import annotations

import argparse
import base64
import sys
from io import BytesIO
from pathlib import Path

import requests

try:  # Windows コンソールの文字化け対策
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

DEFAULT_MODEL = "gpt-image-1"
API_URL = "https://api.openai.com/v1/images/generations"

# orientation -> (APIに渡すsize, 最終的にトリミングする目標サイズ)
ORIENTATIONS = {
    "landscape": ("1536x1024", (1280, 670)),   # note eyecatch/cover想定（1.91:1相当）
    "portrait": ("1024x1536", (1080, 1350)),   # Instagram想定（4:5）
    "square": ("1024x1024", (1024, 1024)),
}

NO_TEXT_HINT = (
    " Do not include any text, letters, numbers, or tables in the image. "
    "Purely a background illustration/pattern."
)


def _load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _crop_to_size(img_bytes: bytes, target: tuple[int, int]) -> bytes:
    from PIL import Image

    im = Image.open(BytesIO(img_bytes)).convert("RGB")
    tw, th = target
    sw, sh = im.size
    src_ratio = sw / sh
    tgt_ratio = tw / th
    if src_ratio > tgt_ratio:
        # 元画像の方が横長 → 左右をトリミング
        new_w = int(sh * tgt_ratio)
        x0 = (sw - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, sh))
    else:
        # 元画像の方が縦長 → 上下をトリミング
        new_h = int(sw / tgt_ratio)
        y0 = (sh - new_h) // 2
        im = im.crop((0, y0, sw, y0 + new_h))
    im = im.resize(target, Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def generate(prompt: str, orientation: str, out_path: Path, no_text: bool = True) -> bool:
    if orientation not in ORIENTATIONS:
        print(f"orientation は {list(ORIENTATIONS)} のいずれかにしてください")
        return False
    api_size, target = ORIENTATIONS[orientation]

    env = _load_env(ENV_PATH)
    api_key = env.get("OPENAI_API_KEY") or ""
    if not api_key:
        print(f"OPENAI_API_KEY が {ENV_PATH} から読めませんでした。"
              ".env.example を参考に .env を作成してください（このリポジトリではコミットされません）。")
        return False
    model = env.get("OPENAI_IMAGE_MODEL") or DEFAULT_MODEL

    full_prompt = prompt + (NO_TEXT_HINT if no_text else "")
    print(f"[ai_image] model={model} size={api_size} で生成中…（数円〜数十円の課金が発生します）")
    res = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "prompt": full_prompt, "size": api_size, "n": 1},
        timeout=120,
    )
    if res.status_code >= 400:
        print(f"[ai_image] 生成失敗 {res.status_code}: {res.text}")
        return False

    payload = res.json()["data"][0]
    if payload.get("b64_json"):
        raw = base64.b64decode(payload["b64_json"])
    elif payload.get("url"):
        raw = requests.get(payload["url"], timeout=60).content
    else:
        print(f"[ai_image] 想定外のレスポンス形式: {payload.keys()}")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cropped = _crop_to_size(raw, target)
    out_path.write_bytes(cropped)
    print(f"[ai_image] 保存: {out_path}（{target[0]}x{target[1]}）")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", required=True, help="背景アートの説明（英語推奨・文字/数字/表は入れない前提）")
    ap.add_argument("--orientation", default="landscape", choices=list(ORIENTATIONS))
    ap.add_argument("--out", required=True, type=Path, help="保存先パス（例: dev/6-markets/assets/2026-09/bg.png）")
    ap.add_argument("--allow-text", action="store_true", help="文字を含めてよい場合のみ指定（非推奨）")
    args = ap.parse_args()

    ok = generate(args.prompt, args.orientation, args.out, no_text=not args.allow_text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
