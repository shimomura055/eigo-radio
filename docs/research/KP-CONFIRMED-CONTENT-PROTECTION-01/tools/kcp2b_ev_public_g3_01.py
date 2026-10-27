# -*- coding: utf-8 -*-
"""公開URLの実ページ(取得済みHTML。read-only)に対する G3 の実行。確定レコード(コピーdir・actor=evidence)の日本語訳が、公開ページに表示されているかを er128.verify_outputs で検査する。"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er119_kp_human_review_01 as rv  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402

kp, lv, kind, *pages = sys.argv[1:]
rec = cc.load_record(kp)
out = {"kp_dir": kp, "level": lv, "record_actor": rec["confirmed_by"]["actor"], "gloss_expected": [i["japanese_gloss"] for i in rec["items"] if i["slot"] == "kp"], "pages": pages}
for label, extra in (("PASS期待(実ページ)", {}),):
    try:
        if kind == "a2":
            cc.verify_outputs(kp, lv, page_paths=pages)
        else:
            cc.verify_outputs(kp, lv, vocab_page_paths=pages)
        out["result"] = "PASS(公開ページに確定訳が表示されている)"
    except Exception as e:  # noqa: BLE001
        out["result"] = "BLOCK " + type(e).__name__ + ": " + str(e)[:400]
print(json.dumps(out, ensure_ascii=False, indent=1))
