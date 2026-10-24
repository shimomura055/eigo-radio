"""委任_35 X(記事B uk_train_speaker_playback)の正式KP段 re-run。API: gpt-6-luna(canonicalization + gloss alignment + redundancy QA)。TTS 0。

方式: 既存run(er019 Production run)に保存済みのKP段artifact(keywords_canonicalized.json)から、選定段の出力(original_items)を
`er105.build_original_items`と同形に**再構成**(選定LLMは再実行しない=KPの選び直しをしない)し、正式入口
`sc.run_key_phrase_canonicalization(article_text, original_items, kp_dir, article_id, process)`を呼ぶ
(=canonicalization[A-1/②のhook込み]→merge→`gloss_align.align_glosses`[X2p' 新規生成経路]。runnerの`run_theme_scaffold`と同じprocess/article_id)。
続けて`sc.run_key_phrase_redundancy_qa`(KP変更時の相互重複QA)。旧artifactはWIRING_35/x_backup/<level>/へ退避。
--dry-runはAPI 0で入力復元・article sha照合だけ行う。再起動・自動再試行ラッパなし。
"""
import argparse
import json
import os
import shutil
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er003_v1_n3_01_scaffold_generate as sc  # noqa: E402
import er003_key_words_gloss_alignment as ga  # noqa: E402
import er005_cost_logger as cl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG_DIR = "er019_output/uk_train_speaker_playback/run_nws_02"
RUN = "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02"
RESTORE_KEYS = ("rank", "display_phrase", "source_span", "source_sentence", "source_sentence_id", "ja_gloss", "japanese_gloss",
                "fulltext_source_ref", "selection_resolution_method", "occurrence_count", "occurrence_sentence_ids",
                "declared_word_count_mismatch")


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def restore_original_items(merged):
    out = []
    for it in sorted(merged["items"], key=lambda x: x["rank"]):
        o = {k: it.get(k) for k in RESTORE_KEYS if k in it}
        o["ja_gloss"] = None
        o["japanese_gloss"] = None
        out.append(o)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="a2,b1b")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    shas = json.load(open(f"{RUN}/audit/scaffold_article_sha256.json", encoding="utf-8"))
    summary = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "levels": {}}
    if not a.dry_run:
        cl.install(f"{HERE}/cost/usage_log_x.jsonl")
    for lv in a.levels.split(","):
        art_path = f"{SLUG_DIR}/{lv}/article.md"
        assert sha(art_path) == shas[lv]["article_sha256"], f"{lv}: article sha不一致(本文が変わっている)"
        article_text = open(art_path, encoding="utf-8").read()
        kp_dir = f"{RUN}/{lv}/key_phrases"
        old = json.load(open(f"{kp_dir}/keywords_canonicalized.json", encoding="utf-8"))
        orig = restore_original_items(old)
        article_id = f"FAMILY_X_AUDIO_{os.path.basename(RUN)}_{lv}"
        proc = "B1_SUPPORT" if lv == "b1b" else "A2_SUPPORT"
        rec = {"article_id": article_id, "process": proc, "n_original_items": len(orig),
               "old": [(i["rank"], i["key_phrase"], i["japanese_gloss"]) for i in old["items"]],
               "original_display": [o["display_phrase"] for o in orig],
               "is_fulltext": all(o.get("fulltext_source_ref") for o in orig)}
        summary["levels"][lv] = rec
        print(lv, json.dumps(rec, ensure_ascii=False))
        if a.dry_run:
            continue
        bk = f"{HERE}/x_backup/{lv}"
        os.makedirs(bk, exist_ok=True)
        for fn in ("keywords_canonicalized.json", "canonicalization_prompt.txt", "canonicalization_runtime_metadata.json",
                   "gloss_alignment_prompt.txt", "gloss_alignment_runtime_metadata.json", "keyphrase_redundancy_qa.json",
                   "keyphrase_redundancy_qa_prompt.txt"):
            if os.path.exists(f"{kp_dir}/{fn}") and not os.path.exists(f"{bk}/{fn}"):
                shutil.copy2(f"{kp_dir}/{fn}", f"{bk}/{fn}")
        t0 = time.monotonic()
        with cl.logging_context(article_id, "kp_x2pp_rerun_35"):
            res = sc.run_key_phrase_canonicalization(article_text, orig, kp_dir, article_id, process=proc)
        rec["canonicalization_status"] = res.get("status")
        rec["gloss_alignment_status"] = res.get("gloss_alignment_status")
        rec["gloss_alignment_cost_jpy"] = res.get("gloss_alignment_cost_jpy")
        rec["gloss_alignment_metrics"] = res.get("gloss_alignment_metrics")
        rec["elapsed_canon_plus_align_sec"] = round(time.monotonic() - t0, 2)
        if res.get("merged") is not None:
            merged = res["merged"]
            rec["new"] = [(i["rank"], i["key_phrase"], i["japanese_gloss"], (i.get("gloss_alignment") or {}).get("meaning_stage"),
                           i.get("gloss_alignment_status")) for i in merged["items"]]
            with cl.logging_context(article_id, "kp_x2pp_rerun_35_redundancy"):
                red = sc.run_key_phrase_redundancy_qa(article_text, merged["items"], kp_dir, article_id, process=proc)
            rec["redundancy_status"] = red.get("status")
            rec["redundancy_duplicate_pairs"] = red.get("duplicate_pairs")
        print(lv, json.dumps({k: v for k, v in rec.items() if k in ("canonicalization_status", "gloss_alignment_status", "new",
                                                                   "redundancy_status", "elapsed_canon_plus_align_sec")}, ensure_ascii=False))
    out = f"{HERE}/x_rerun_summary_35.json"
    json.dump(summary, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("summary ->", out)


if __name__ == "__main__":
    main()
