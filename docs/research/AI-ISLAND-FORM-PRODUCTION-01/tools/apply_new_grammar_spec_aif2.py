# -*- coding: utf-8 -*-
"""AI-ISLAND-FORM-PRODUCTION-01 委任_02: AI島Std/Advのフォームデータへ(1)ユーザー確定KP/KW 10件(kp_confirmed)と(2)文法新仕様(Top1/Top2のみ提示)を適用する。API 0。
入力: payloads/ai_island_temple__{lv}__user_confirmed_01.json(ユーザー確定の逐語保存)・grammar_prep_out/{lv}/study_text/{grammar_candidates,grammar_explanations}.json(既存暫定事前生成物。再生成しない)
出力: user_test/selection_form_v3/data/ai_island_temple__{lv}__prod.json(同名置換。冪等)
検証(fail-closed): Top2=候補docの top_ids=rank1,2 / 解説全文=explanations.items[].explanation_md と逐語一致+sha256再計算一致 / 確定payloadのsha・件数が元データと一致"""
import hashlib, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
D = os.path.join(ROOT, "docs", "research", "AI-ISLAND-FORM-PRODUCTION-01")
FORM = os.path.join(ROOT, "user_test", "selection_form_v3", "data")
CAT_ORDER = ("key_phrase", "extra_explanation", "meaning_display")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    for lv in ("a2", "b1b"):
        pf = os.path.join(D, "payloads", f"ai_island_temple__{lv}__user_confirmed_01.json")
        payload_bytes = open(pf, "rb").read()
        pay = json.loads(payload_bytes.decode("utf-8"))
        fp = os.path.join(FORM, f"ai_island_temple__{lv}__prod.json")
        d = json.load(open(fp, encoding="utf-8"))
        st = os.path.join(D, "grammar_prep_out", lv, "study_text")
        gc = json.load(open(os.path.join(st, "grammar_candidates.json"), encoding="utf-8"))
        ex = json.load(open(os.path.join(st, "grammar_explanations.json"), encoding="utf-8"))
        # ---- 確定KP/KW ----
        assert pay["article"]["text_sha256"] == d["source"]["text_sha256"], "text_sha256不一致"
        assert pay["article"]["candidates_sha256"] == d["candidates_sha256"], "candidates_sha256不一致"
        recs = []
        for k in CAT_ORDER:
            recs += pay["selection"][k]
        assert len(recs) == 10
        byid = {x["candidate_id"]: x for x in d["phrases"] + d["words"]}
        for r in recs:
            it = byid[r["candidate_id"]]
            assert it["term"] == r["term"] and it["ja_gloss"] == r["ja_gloss"] and it["ja_gloss_status"] == "official" == r["ja_gloss_status"], r
        d["kp_confirmed"] = {"status": "USER_CONFIRMED", "locked": True, "confirmed_at": pay["confirmed_at"], "user_ref": pay["user_ref"],
                             "payload_path": f"docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/ai_island_temple__{lv}__user_confirmed_01.json",
                             "payload_sha256": sha(payload_bytes), "text_sha256": pay["article"]["text_sha256"], "candidates_sha256": pay["article"]["candidates_sha256"],
                             "selection": recs,
                             "note_ja": "Key Phrase／Key Word各10件はユーザー確定済み(2026-10-27)。フォームでは表示のみで再選定できない。送信payloadには確定内容を逐語で含める。"}
        # ---- 文法: Top1/Top2のみ ----
        cands = sorted(gc["candidates"], key=lambda c: c["rank"])
        top_ids = [c["candidate_id"] for c in cands[:2]]
        assert top_ids == gc["top_ids"], ("候補docのtop_idsとrank順Top2が不一致", top_ids, gc["top_ids"])
        items = {i["candidate_id"]: i for i in ex["items"]}
        full = {g["candidate_id"]: g for g in d["grammar"]}      # 既存の全候補データ(冪等のため、既に絞り込み済みなら不足する)
        if set(top_ids) - set(full):
            raise SystemExit(f"{lv}: Top2がフォームデータに存在しない(既に絞り込み済み・別データ?)")
        hidden = [g["candidate_id"] for g in d["grammar"] if g["candidate_id"] not in top_ids] or (d.get("grammar_spec") or {}).get("hidden_ids", [])
        out = []
        for k, cid in enumerate(top_ids, 1):
            g = full[cid]
            e = items[cid]
            assert g["explanation_full"] == e["explanation_md"] == g["body"], f"{cid} 解説全文が事前生成物と不一致"
            assert hashlib.sha256(e["explanation_md"].encode("utf-8")).hexdigest() == g["explanation_sha256"], f"{cid} sha不一致"
            assert g["rank"] == k and g.get("explanation_status") == "provided"
            out.append(g)
        d["grammar"] = out
        d["grammar_spec"] = {"version": "top2_select1_v1", "decided": "2026-10-27(ユーザー正式決定、USER_02 §5)", "presented_max": 2, "max_select": 1, "allow_zero": True,
                             "presented_ids": top_ids, "hidden_ids": hidden, "order": "AI評価順位(grammar_candidates.json candidates[].rank / top_ids)",
                             "source_candidates_sha256": gc["candidates_sha256"], "source_explanations_sha256": ex.get("explanations_sha256"),
                             "note_ja": "AI評価Top 1・Top 2のみ提示。1件選ぶか『適切な候補なし(0件)』を選ぶ。2件同時は不可。旧フォームの文法0件は引き継がない(新フォームで明示選択が必要)。3位以降は表示しない(解説は既存暫定事前生成物を再利用・再生成なし)。"}
        d["grammar_status"] = "candidates_available"
        with open(fp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(lv, "ok top2=", top_ids, "hidden=", hidden, "kp_confirmed payload sha", sha(payload_bytes)[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
