# er073_family_z_kp_db_hybrid_m2p0_migration_01_diff.py
# FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01 Phase 1 (JPY0、LLM呼出なし)
# Family Z原稿に対し、Production module(read-only import)でM2候補供給+選定メッセージ組立までをオフライン実行し、
# 構造差(shortlist・候補・Prompt長・title有無の影響・所要時間)の証跡を保存する。Production無変更・telemetry書込なし。
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, concurrent.futures as cf

import er003_b1_p2_keywords as bk
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_m2_supply_01 as m2
import er030_key_phrase_db_hybrid_selector_01 as sel
import er062_family_z_structure_01 as st

MELOS = "er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer"
TEXTS = {
    "melos_std": (f"{MELOS}/std.md", "A2_SUPPORT"),
    "melos_adv": (f"{MELOS}/r2.md", "B1_SUPPORT"),
    "lemon_l11": ("er055_output/family_z_d_predictive_validation_trial_01/L11/story_en.md", "A2_SUPPORT"),
}


def canonical_article_text(text: str) -> str:
    # er026_family_z_fiction_production_runner_01.canonical_article_text と同一実装(読み取り再現)
    _t, body = st.split_title_body(text)
    return "\n\n".join(st.clean_body_paragraphs(body))


def article_for(text_id: str, with_title: bool) -> tuple[str, str]:
    raw = open(TEXTS[text_id][0], encoding="utf-8").read()
    title, _ = st.split_title_body(raw)
    heading_in_body = not title
    if not title:  # er055系は`### 見出し`形式でsplit_title_bodyがNoneを返す -> 先頭の#見出し行を使う
        title = next((l.lstrip('#').strip() for l in raw.splitlines() if l.strip().startswith('#')), "")
    body = canonical_article_text(raw)
    return ((f"# {title}" + chr(10) + chr(10) + body if (with_title and not heading_in_body) else body), title)


def snapshot(text_id: str, with_title: bool, out_dir: str, dbs: dict) -> dict:
    art, title = article_for(text_id, with_title)
    t0 = time.time()
    s1r = m2.build_m2_stage1_and_shortlist(art, dbs, sel.extract_article_title(art))
    el = round(time.time() - t0, 1)
    si = s1r["shortlist_info"]
    built = sel.build_production_selection_message(
        sel.extract_article_title(art), si, sel.extract_static_instructions(bk.load_prompt_template()),
        "family_x", containment_pairs=s1r["containment_pairs"])
    msg = built["message"]
    cands = [{"id": c["candidate_id"], "surface": c["surface_form"], "type": sel._display_type(c),
              "important": bool(c.get("important_noun_phrase_candidate")), "sentence": c.get("context_sentence_id"),
              "evidence": sel._compact_evidence_string(c), "fragment_risk": bool(c.get("fragment_risk"))}
             for c in built["shortlist_with_ids"]]
    rec = {"text_id": text_id, "with_title": with_title, "title_passed": sel.extract_article_title(art),
           "article_sha256": hashlib.sha256(art.encode()).hexdigest(), "article_words": len(art.split()),
           "elapsed_sec": el, "shortlist_total": si["shortlist_total_count"],
           "phrase_included": si["phrase_included_count"], "important_noun_included": si["important_noun_included_count"],
           "word_included": si["word_included_count"], "m2_meta": s1r["m2_meta"],
           "message_chars": len(msg), "message_sha256": hashlib.sha256(msg.encode()).hexdigest(),
           "candidates": cands}
    tag = f"{text_id}_{'title' if with_title else 'notitle'}"
    json.dump(rec, open(f"{out_dir}/shortlist_{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(f"{out_dir}/selector_message_{tag}.txt", "w", encoding="utf-8").write(msg)
    return {k: rec[k] for k in ("text_id", "with_title", "title_passed", "elapsed_sec", "shortlist_total", "phrase_included",
                                "important_noun_included", "word_included", "message_chars")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--only", default=None, help="text_idを1つだけ再実行(lemon_l11のtitle補正用)")
    a = ap.parse_args()
    out = os.path.join(a.out_dir, "phase1")
    os.makedirs(out, exist_ok=True)
    dbs = core.load_group1_dbs()
    jobs = [("melos_std", True), ("melos_std", False), ("melos_adv", True), ("lemon_l11", True)]
    if a.only:
        jobs = [j for j in jobs if j[0] == a.only]
    summ = []
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(snapshot, t, w, out, dbs) for t, w in jobs]
        for f in futs:
            summ.append(f.result())
    if not a.only:
        json.dump(summ, open(f"{out}/phase1_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
