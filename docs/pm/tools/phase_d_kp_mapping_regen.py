"""phase_d_kp_mapping_regen.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D専用。新canonical
keywords_canonicalized.json(source_span基準)と新article.mdを突き合わせ、
Phase Aと同じschema(phrase/phrase_ja/matched_text/mapping_type/occurrences/
rationale/candidates + summary)でkp_mapping.jsonを再作成する。

判定ルール(Phase Aと同一): source_spanが本文中に(大文字小文字を無視して)
1箇所以上見つかればexact、0箇所ならUNRESOLVED。
"""
from __future__ import annotations

import json
import re
import sys


def build_mapping(article_id: str, level: str, article_text: str, kp_items: list) -> dict:
    key_phrases = []
    mapped = 0
    exact = 0
    unresolved = 0
    for item in kp_items:
        span = item["source_span"]
        pattern = re.compile(re.escape(span), re.IGNORECASE)
        matches = list(pattern.finditer(article_text))
        if matches:
            matched_text = article_text[matches[0].start():matches[0].end()]
            entry = {
                "phrase": item["key_phrase"],
                "phrase_ja": item["japanese_gloss"],
                "matched_text": matched_text,
                "mapping_type": "exact",
                "occurrences": len(matches),
                "rationale": None,
                "candidates": None,
            }
            mapped += 1
            exact += 1
        else:
            entry = {
                "phrase": item["key_phrase"],
                "phrase_ja": item["japanese_gloss"],
                "matched_text": None,
                "mapping_type": "UNRESOLVED",
                "occurrences": 0,
                "rationale": f"本文にsource_span('{span}')が見つかりません。",
                "candidates": [span],
            }
            unresolved += 1
        key_phrases.append(entry)
    return {
        "article_id": article_id, "level": level, "key_phrases": key_phrases,
        "summary": {"total": len(kp_items), "mapped": mapped, "exact": exact,
                     "non_exact": 0, "unresolved": unresolved},
    }


def main() -> int:
    article_id, level, article_md_path, kp_json_path, out_path = sys.argv[1:6]
    with open(article_md_path, encoding="utf-8") as f:
        article_text = f.read()
    with open(kp_json_path, encoding="utf-8") as f:
        kp = json.load(f)
    mapping = build_mapping(article_id, level, article_text, kp["items"])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(json.dumps(mapping["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
