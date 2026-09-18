"""translation_reprint_check.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-2.

10 Standard(A2) levelについて、`translation_ja.json`の`type=reprint`各section
の`text_ja`(=`source_ja`)が、現行canonical player DOM(`index.json`のsrcが
指すファイル)のComment原文(既存日本語Comment)と完全一致することを確認する。
10 Advanced(B1) levelについては、`type=translation`のうちComment
(`section_id`が`comment_`で始まるsection)の件数が、DOM上のComment件数と
一致することを確認する(Comment原文=英語、Standard/Advancedとも同一の
`<b>Comment N ...</b>`マーカーで機械抽出する)。

DOM抽出方式: player.html/index.htmlはtimeline tableが1行のHTMLとして出力
されており、`<b>Comment N ...</b>` の直後に現れる最初の
`<td class="txt">...</td>` をそのComment本文とみなす(既存出力フォーマット
に基づく機械的抽出。フォーマット変更があれば本スクリプトの正規表現を
更新する必要がある)。

使い方:
  python docs/pm/tools/translation_reprint_check.py \
      --index user_test/translations/index.json \
      --translations user_test/translations \
      --out docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/reprint_check.json
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

COMMENT_RE = re.compile(
    r"<b>Comment\s*(\d+)[^<]*</b>.*?<td class=\"txt\">(.*?)</td>",
    re.DOTALL,
)

# reprintの型名はPhase Aで"existing_comment_repost"、Phase B1/B2以降で"reprint"
# の2種類が既存Production資産として混在している(内容は同じ既存Comment再掲)。
REPRINT_TYPES = ("reprint", "existing_comment_repost")


def _segment_for_level(raw: str, level: str) -> str:
    """1ファイルに複数level分のtimeline tableが同居する既存canonical
    (例: wake_before_alarm player_std/index.html)の場合、対象levelの
    区間のみを切り出す。単一levelのみのファイルではrawをそのまま返す。"""
    table_starts = [m.start() for m in re.finditer(r'<table class="timeline">', raw)]
    if len(table_starts) <= 1:
        return raw
    pos_a2 = raw.find("episode_audio_a2")
    pos_b1 = raw.find("episode_audio_b1b")
    if level.upper() == "A2":
        start, other = pos_a2, pos_b1
    else:
        start, other = pos_b1, pos_a2
    if start == -1:
        return raw
    end = other if other > start else len(raw)
    return raw[start:end]


def extract_dom_comments(html_path: Path, level: str) -> dict[int, str]:
    raw = html_path.read_text(encoding="utf-8")
    segment = _segment_for_level(raw, level)
    out: dict[int, str] = {}
    for m in COMMENT_RE.finditer(segment):
        n = int(m.group(1))
        text = html.unescape(re.sub(r"<[^>]*>", "", m.group(2))).strip()
        out[n] = text
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--index", required=True)
    ap.add_argument("--translations", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    index_data = json.loads(Path(args.index).read_text(encoding="utf-8"))
    items = {(it["article_id"], it["level"]): it for it in index_data["items"]}
    tdir = Path(args.translations)

    results = {}
    all_pass = True

    for (article_id, level), item in sorted(items.items()):
        trans_path = tdir / article_id / level / "translation_ja.json"
        if not trans_path.is_file():
            continue
        trans = json.loads(trans_path.read_text(encoding="utf-8"))
        src_path = Path(item["src"])
        if not src_path.is_file():
            results[f"{article_id}_{level}"] = {
                "status": "FAIL", "reason": f"canonical src not found: {src_path}",
            }
            all_pass = False
            continue
        dom_comments = extract_dom_comments(src_path, level)

        comment_sections = [s for s in trans["sections"] if s["section_id"].startswith("comment_")]
        entry = {
            "article_id": article_id, "level": level, "src": item["src"],
            "dom_comment_count": len(dom_comments),
            "translation_comment_count": len(comment_sections),
            "mismatches": [],
        }

        if item.get("comment_lang") == "ja":
            # Standard: reprint本文がDOM原文と完全一致すること
            for s in comment_sections:
                if s.get("type") not in REPRINT_TYPES:
                    entry["mismatches"].append(
                        {"section_id": s["section_id"], "reason": f"type not in {REPRINT_TYPES} (got {s.get('type')})"}
                    )
                    continue
                n = int(re.sub(r"\D", "", s["section_id"]))
                dom_text = dom_comments.get(n)
                if dom_text is None:
                    entry["mismatches"].append({"section_id": s["section_id"], "reason": "DOM comment not found"})
                    continue
                text_ja = s.get("text_ja", "")
                source_ja = s.get("source_ja")
                if source_ja is not None and text_ja != source_ja:
                    entry["mismatches"].append({
                        "section_id": s["section_id"], "reason": "text_ja != source_ja (reprint self-consistency)",
                    })
                if dom_text != text_ja:
                    entry["mismatches"].append({
                        "section_id": s["section_id"], "reason": "DOM comment != translation_ja text_ja",
                        "dom_text": dom_text, "text_ja": text_ja,
                    })
        else:
            # Advanced: Comment件数のみ一致確認(内容は英語Comment原文の翻訳対象)
            if len(comment_sections) != len(dom_comments):
                entry["mismatches"].append({
                    "reason": "comment count mismatch",
                    "dom_count": len(dom_comments), "translation_count": len(comment_sections),
                })

        entry["status"] = "PASS" if not entry["mismatches"] else "FAIL"
        if entry["status"] == "FAIL":
            all_pass = False
        results[f"{article_id}_{level}"] = entry

    summary = {"overall": "PASS" if all_pass else "FAIL", "results": results}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v["status"] for k, v in results.items()}, ensure_ascii=False, indent=2))
    print(f"overall: {summary['overall']}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
