# -*- coding: utf-8 -*-
"""AI-ISLAND-FORM-PRODUCTION-01 委任_02: ユーザー確定20件(2026-10-27)の元データ照合(fail-closed)+payload v2保存+照合表出力。API 0。
使い方: py verify_user_confirm_aif2.py [--write]   (--writeでpayloadとCONFIRMATION_CHECK_01.mdを書く。不一致が1件でもあれば何も書かず rc=1)"""
import hashlib, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
D = os.path.join(ROOT, "docs", "research", "AI-ISLAND-FORM-PRODUCTION-01")
KP = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "ai_island_temple__run_kp75_ev_01")
ART = os.path.join(ROOT, "er019_output", "ai_island_temple", "run_ai_01")
FORM = os.path.join(ROOT, "user_test", "selection_form_v3", "data")
USER_REF = "docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md"
# ---- ユーザー原文(USER_02.md §2/§3)の逐語転記: (区分, 英語=used_form, 確定日本語訳, candidate_id) ----
USER = {
    "a2": {"text_sha256": "76f80f62120b57835150b1fc35d590c0b848926ce219ecb27105f2414d376599",
           "candidates_sha256": "25a7bce9357cdaaaf58207e179fd187e97f77e0c5f30c4b511ec933bd51d028a",
           "rows": [(1, "carry over", "持ち越す", "p_1a2370a6af"), (1, "take a detour", "寄り道をする", "p_1473453d19"), (1, "card to play", "使える手", "p_289a665236"),
                    (2, "worth paying attention to", "注目する価値がある", "p_1cf1329364"), (2, "obstacle", "障害物", "p_d17f8079e3"),
                    (3, "make a difference", "影響を与える", "p_801113c17d"), (3, "separately", "個別に", "p_dc8803926c"), (3, "feature", "性質", "p_4b7615dce5"),
                    (3, "Strategy", "作戦", "p_31e10e6357"), (3, "setup", "設定", "p_80437a44a6")],
           "surface": {"carry over": "carried over", "take a detour": "taken a detour", "make a difference": "made a difference"}},
    "b1b": {"text_sha256": "00f14092c072d9aa208778dbc1aa1b5d715262cc77b4e5420acae6c0bffca324",
            "candidates_sha256": "5d8c1b12f01b0de9265721152da508e7f8f7afb1f7f126d5d461a835457d87f9",
            "rows": [(1, "carry over", "次に持ち越す", "p_1a2370a6af"), (1, "call on", "頼む", "p_ad091fb295"), (1, "take a detour", "遠回りをする", "p_1473453d19"),
                     (2, "card to play", "打てる手", "p_289a665236"), (2, "obstacle", "障害物", "p_d17f8079e3"),
                     (3, "look at separately", "別々に検討する", "p_8f3df24cb8"), (3, "exploration", "いろいろ探ること", "p_0d5feb1964"), (3, "technique", "やり方", "p_b41c6aff6d"),
                     (3, "overlook", "見過ごす", "p_1b8ee344f0"), (3, "erase", "消し去る", "p_4513a423ab")],
            "surface": {"carry over": "carried over", "call on": "called on", "take a detour": "taken a detour", "look at separately": "looked at separately", "erase": "erased"}},
}
CAT_KEY = {1: "key_phrase", 2: "extra_explanation", 3: "meaning_display"}
CAT_LABEL = {1: "①Key Phrase", 2: "②追加解説", 3: "③本文意味表示"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def article_norm(lv):
    raw = open(os.path.join(ART, lv, "article.md"), "rb").read()
    t = raw.decode("utf-8").replace("\r\n", "\n")
    paras = [x.strip() for x in re.split(r"\n\s*\n", t.strip()) if x.strip()]
    return raw, "\n\n".join(paras)


def main():
    write = "--write" in sys.argv
    bad, out, payloads = [], [], {}

    def chk(ok, msg):
        if not ok:
            bad.append(msg)
        return "OK" if ok else "NG"
    out.append("# CONFIRMATION_CHECK_01 ユーザー確定20件の元データ照合(AI-ISLAND-FORM-PRODUCTION-01 委任_02、fail-closed)\n")
    out.append("機械生成: `docs/research/AI-ISLAND-FORM-PRODUCTION-01/tools/verify_user_confirm_aif2.py`(API 0)。ユーザー確定値=`" + USER_REF + "` §2/§3の逐語転記。\n")
    for lv, u in USER.items():
        doc = json.load(open(os.path.join(KP, lv, "key_phrases", "kp_candidates.json"), encoding="utf-8"))
        fd = json.load(open(os.path.join(FORM, f"ai_island_temple__{lv}__prod.json"), encoding="utf-8"))
        raw, norm = article_norm(lv)
        out.append(f"\n## {lv} ({'Standard' if lv == 'a2' else 'Advanced'})\n")
        out.append("### SHA照合\n\n| 項目 | ユーザー値 | 照合先 | 照合先の値 | 結果 |\n|---|---|---|---|---|")
        rows = [("本文SHA256", u["text_sha256"], "候補doc `text_sha256`", doc["text_sha256"]),
                ("本文SHA256", u["text_sha256"], "フォームデータ `source.text_sha256`", fd["source"]["text_sha256"]),
                ("本文SHA256", u["text_sha256"], "article.mdをLF正規化→空行区切り段落をstrip→`\\n\\n`連結(タイトル行・In one line節を含む全10段落)のSHA256", sha(norm.encode("utf-8"))),
                ("候補集合SHA256", u["candidates_sha256"], "候補doc `candidates_sha256`", doc["candidates_sha256"]),
                ("候補集合SHA256", u["candidates_sha256"], "フォームデータ `candidates_sha256`", fd["candidates_sha256"])]
        for name, uv, src, v in rows:
            out.append(f"| {name} | `{uv[:12]}…` | {src} | `{v[:12]}…` | {chk(uv == v, lv + ' ' + name + ' != ' + src)} |")
        out.append(f"\n参考(別基準・一致しなくてよい): article.md 生bytes SHA256=`{sha(raw)[:12]}…`(委任_01報告の値)。ユーザー値は生bytesではなく上記『正規化本文』基準のSHA(候補doc `text_sha256`と同一基準)。文法事前生成docの`text_sha256`は本文8段落(タイトル・In one line節を除く)基準で別値のため混同しない。\n")
        out.append("### 10件の逐語照合(区分・英語・日本語訳・candidate_id)\n\n| 区分 | 英語(used_form) | ユーザー確定日本語訳 | candidate_id | 候補doc used_form | 候補doc japanese_gloss | form data term / ja_gloss / status | 本文の表層形 | 結果 |\n|---|---|---|---|---|---|---|---|---|")
        cm = {c["candidate_id"]: c for c in doc["candidates"]}
        fm = {x["candidate_id"]: x for x in fd["phrases"] + fd["words"]}
        low = norm.lower()
        sel = {k: [] for k in CAT_KEY.values()}
        for cat, en, ja, cid in u["rows"]:
            c, f = cm.get(cid), fm.get(cid)
            ok = c is not None and f is not None
            it = (c or {}).get("item") or {}
            ufm = it.get("used_form")
            gl = it.get("japanese_gloss") or (c or {}).get("japanese_gloss")
            ok = ok and ufm == en and gl == ja and (f or {}).get("term") == en and (f or {}).get("ja_gloss") == ja and (f or {}).get("ja_gloss_status") == "official"
            surf = (c or {}).get("selection_phrase") or en
            if u["surface"].get(en):
                ok = ok and surf == u["surface"][en]
            present = surf.lower() in low
            ok = ok and present
            out.append(f"| {CAT_LABEL[cat]} | {en} | {ja} | {cid} | {ufm} | {gl} | {(f or {}).get('term')} / {(f or {}).get('ja_gloss')} / {(f or {}).get('ja_gloss_status')} | {surf}{'(在)' if present else '(不在)'} | {chk(ok, lv + ' ' + cid + ' ' + en)} |")
            rec = {"term": en, "category": cat, "category_label": CAT_LABEL[cat], "ja_gloss": ja, "ja_gloss_status": "official", "candidate_id": cid, "kind": (c or {}).get("kind") or "phrase"}
            if surf != en:
                rec["selection_phrase"] = surf
            sel[CAT_KEY[cat]].append(rec)
        ids = [r[3] for r in u["rows"]]
        a = chk(len(set(ids)) == 10, lv + " 件数/重複")
        b = chk([sum(1 for r in u["rows"] if r[0] == k) for k in (1, 2, 3)] == [3, 2, 5], lv + " 区分内訳")
        out.append(f"\n件数10(①3/②2/③5)・candidate_id重複なし: {a}/{b}。候補doc全体={len(doc['candidates'])}件(ユーザー確定10件が全候補)。\n")
        payloads[lv] = {
            "schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1, "generated_at": "2026-10-27",
            "article": {"slug": "ai_island_temple", "level": lv, "level_label": fd.get("level_label", ""), "name": fd["name"], "text_sha256": u["text_sha256"],
                        "candidates_sha256": u["candidates_sha256"], "candidates_sha256_source": fd.get("candidates_sha256_source"),
                        "source_kp_candidates_path": fd.get("source_kp_candidates_path")},
            "candidate_source": "PRODUCTION_FORMAL_PATH",
            "user_confirmed_note_ja": "ユーザー正式決定(2026-10-27)の確定内容を逐語保存したもの。英語表現・日本語訳・区分・candidate_idは変更しない。文法は新仕様で再選定待ち(0件確定ではない)。",
            "user_ref": USER_REF, "confirmed_at": "2026-10-27",
            "selection": dict(sel, grammar=[]),
            "grammar_status": "pending_reselection",
            "comment": "",
            "counts": {"key_phrase": 3, "key_phrase_plus_extra": 5, "total_highlight": 10, "grammar": 0},
            "production_connected": False,
        }
    if bad:
        print("FAIL (fail-closed):", *bad, sep="\n  ")
        return 1
    print("ALL MATCH: SHA 10/10, items 20/20")
    out.append("\n## 判定\n\n不一致 0件。ユーザー確定20件は、候補doc・フォームデータ・承認済み本文と逐語一致(英語・訳・区分・candidate_id・kind・official・SHA)。ユーザー確定の日本語訳と候補docの`japanese_gloss`は全件一致のため、ユーザー値を上書き・不採用にした項目は0件。\n")
    if write:
        os.makedirs(os.path.join(D, "payloads"), exist_ok=True)
        for lv, p in payloads.items():
            path = os.path.join(D, "payloads", f"ai_island_temple__{lv}__user_confirmed_01.json")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(p, f, ensure_ascii=False, indent=1)
                f.write("\n")
            print("wrote", path, sha(open(path, "rb").read())[:16])
        with open(os.path.join(D, "CONFIRMATION_CHECK_01.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
