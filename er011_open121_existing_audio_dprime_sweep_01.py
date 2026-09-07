# ============================================================
# er011_open121_existing_audio_dprime_sweep_01.py
# OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01
# ============================================================
# 読み取り専用の一括点検(ユーザー承認2026-09-07: 検知したものを自動
# 再生成せず、一覧化・分類して報告するだけのLane A作業)。Production
# 変更・音声変更・TTS/ASR課金なし(ローカル計算のみ)。Git操作なし
# (Fableが統合)。
#
# OPEN-121-TTS-REPETITION-GENERAL-QA-TRIAL-02
# (er011_open121_tts_repetition_general_qa_trial_02.py)の方式D'
# (short_run_priority_autocorrelation、full-file、閾値0.6、run長判定)・
# 方式D(spectral_self_similarity、min_lag=1.0秒、参考)・方式A
# (detect_ngram_repetition、n-gram3語+canonical照合、faster-whisper
# local)をTrial-02モジュールからimportして無変更のまま適用する
# (Production関数は呼ばない、Trial-02自体・その出力も変更しない)。
#
# 書き込み範囲: 本ファイル(root)、er011_output/
# open121_existing_audio_dprime_sweep_01/ 配下のみ。Git操作なし。
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er011_open121_tts_repetition_general_qa_trial_02 as t2  # noqa: E402 (方式D'/D/A本体、無変更import)
import er008_disfluency_qa_18 as dq18  # noqa: E402 (方式A用faster-whisper local verbatim、無変更)

OUT_DIR = "er011_output/open121_existing_audio_dprime_sweep_01"
INVENTORY_PATH = f"{OUT_DIR}/inventory.json"
RESULTS_DIR = f"{OUT_DIR}/results"
CLIPS_DIR = f"{OUT_DIR}/clips"
PLAYER_PATH = f"{OUT_DIR}/player.html"
CLASSIFIED_PATH = f"{RESULTS_DIR}/classified_table.json"
SUMMARY_STATS_PATH = f"{RESULTS_DIR}/summary_stats.json"


def log(msg):
    print(msg, flush=True)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _load_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception as e:
        log(f"  [warn] failed to parse {path}: {e}")
        return None


# ============================================================
# 対象ディレクトリ一覧(事前調査で確認済み、docs/pm/ACTIVE_TASK.md参照)
# ============================================================
ER003_INCLUDE_DIRS = [
    "a2_audio_01", "a2_audio_02", "a2_audio_ab_01", "b1redesign_audio_01",
    "b1_p9a", "b1_scaffold_audio_01", "b1_scaffold_audio_03",
    "crosslevel_audio_02", "jp_reading_safety_01", "n3_01",
    "novel_audio_01", "novel_audio_02",
]


def collect_target_roots():
    roots = [
        ("open112_rerun02", "er011_output/open112_trend_theme2_b_final_audio_rerun_02"),
        ("open112_trial13", "er011_output/open112_trend_theme2_b_full_audio_trial_13"),
        ("open117_trial02_kp", "er011_output/open117_keyphrase_display_tts_separation_trial_02"),
    ]
    for d in sorted(glob.glob("er006_output/pool_pilot_01/*")):
        if os.path.isdir(d):
            roots.append((f"pool_pilot_01/{os.path.basename(d)}", d.replace("\\", "/")))
    roots.append(("er012_laneb_trial08", "er012_output/editorial_b_voices_trial_08_audio"))
    roots.append(("er012_laneb_trial09", "er012_output/editorial_b_voices_trial_09_audio"))
    for d in ER003_INCLUDE_DIRS:
        roots.append((f"er003_output/{d}", f"er003_output/{d}"))
    return roots


# ============================================================
# segment分類(EN body / Key Phrase EN / Key Phrase JA / JA other / EN other)
# ============================================================
EN_BODY_BASENAMES = {
    "full_story_intro", "full_story_intro_charon", "full_story_part1", "full_story_part2",
    "point_one", "point_one_heading", "point_two", "point_two_heading", "point_explanation",
    "in_one_line", "topic_intro", "tension_reflection",
}

JA_CHAR_RANGES = [(0x3040, 0x30FF), (0x4E00, 0x9FFF), (0x3000, 0x303F), (0xFF00, 0xFFEF)]


def _has_japanese(text):
    if not text:
        return False
    for ch in text:
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in JA_CHAR_RANGES):
            return True
    return False


def strip_original_suffix(segment_id):
    return segment_id[: -len("_original")] if segment_id.endswith("_original") else segment_id


def classify_segment(segment_id, language):
    base = strip_original_suffix(segment_id)
    if re.match(r"^kp\d+_en$", segment_id):
        return "keyphrase_en"
    if re.match(r"^kp\d+_ja", segment_id):
        return "keyphrase_ja"
    if base in EN_BODY_BASENAMES:
        return "en_body"
    if language == "ja":
        return "ja_other"
    if language == "en":
        return "en_other_non_body"
    return "unknown"


# ============================================================
# canonical text解決(audit/tts_generation_results.json優先、
# parts.jsonフォールバック。無ければNone=canonical未取得)
# ============================================================
PARTS_MAP = {
    "full_story_part1": "part1", "full_story_part2": "part2",
    "point_one": "point_one_body", "point_one_heading": "point_one_heading",
    "point_two": "point_two_body", "point_two_heading": "point_two_heading",
    "in_one_line": "in_one_line",
}


def resolve_segment_info(segment_id, parts, tts, lock, wav_path):
    segments = (tts or {}).get("segments", {}) or {}
    key_phrases = (tts or {}).get("key_phrases", {}) or {}
    base_id = strip_original_suffix(segment_id)

    text, source, tts_status = None, None, None
    for cid in (segment_id, base_id):
        entry = segments.get(cid)
        if entry and entry.get("text"):
            text = entry["text"]
            source = f"tts_generation_results.segments.{cid}"
            tts_status = entry.get("status")
            break
        if entry and tts_status is None:
            tts_status = entry.get("status")

    if text is None and key_phrases:
        m = re.match(r"^kp(\d+)_(en|ja)", segment_id)
        if m:
            idx, lang = m.group(1), m.group(2)
            kp_entry = (key_phrases.get(idx) or {}).get({"en": "english", "ja": "japanese"}[lang])
            if kp_entry and kp_entry.get("text"):
                text = kp_entry["text"]
                source = f"tts_generation_results.key_phrases.{idx}.{lang}"
                tts_status = kp_entry.get("status")

    if text is None and parts:
        if base_id in PARTS_MAP and parts.get(PARTS_MAP[base_id]):
            text = parts[PARTS_MAP[base_id]]
            source = f"parts.json.{PARTS_MAP[base_id]}"

    language = "ja" if _has_japanese(text) else ("en" if text else None)
    if language is None:
        # canonical不明時のfallback heuristic(ファイル名のみで判定、参考程度)
        if re.search(r"(comment_|meaning_|japanese_title|^num_|_ja(_|$))", segment_id):
            language = "ja"
        else:
            language = "en"

    review_entry = None
    if lock:
        review_entry = lock.get(segment_id) or lock.get(base_id)
    review_state = review_entry.get("state") if review_entry else None
    review_final_status = review_entry.get("final_status") if review_entry else None
    review_wav_path = review_entry.get("wav_path") if review_entry else None
    review_lock_available = lock is not None

    return {
        "canonical_text": text, "canonical_source": source or "canonical未取得",
        "language": language, "tts_status": tts_status,
        "review_lock_available": review_lock_available,
        "review_lock_state": review_state, "review_lock_final_status": review_final_status,
        "review_lock_wav_path": review_wav_path,
    }


# ============================================================
# Phase 0: inventory構築
# ============================================================
def find_narration_dirs(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        if os.path.basename(dirpath) == "narration":
            found.append(dirpath.replace("\\", "/"))
    return sorted(found)


def build_inventory():
    os.makedirs(OUT_DIR, exist_ok=True)
    items = []
    roots = collect_target_roots()
    log(f"build_inventory: scanning {len(roots)} target roots")
    for group, root in roots:
        if not os.path.isdir(root):
            log(f"  [skip, missing root] {group}: {root}")
            continue
        narration_dirs = find_narration_dirs(root)
        for narration_dir in narration_dirs:
            level_dir = os.path.dirname(narration_dir)
            level = os.path.basename(level_dir)
            article_dir = os.path.dirname(level_dir)
            parts = _load_json(f"{level_dir}/parts.json")
            tts = _load_json(f"{level_dir}/audit/tts_generation_results.json")
            lock = _load_json(f"{level_dir}/audit/review_lock_state.json")
            wav_files = sorted(f for f in os.listdir(narration_dir) if f.lower().endswith(".wav"))
            for fn in wav_files:
                segment_id = fn[:-4]
                wav_path = f"{narration_dir}/{fn}"
                info = resolve_segment_info(segment_id, parts, tts, lock, wav_path)
                category = classify_segment(segment_id, info["language"])
                # item_idにarticle_dirを含める(2026-09-07 completion-fix: 同一
                # group+levelに複数article(例: n3_01のhanshin/health/household、
                # laneb_trial08のp1/p3)が存在するとgroup::level::segment_idだけ
                # では衝突し、run_d_primeのresumeロジックが異なる実ファイルを
                # 「処理済み」と誤認して読み飛ばしていた。article_dirを含めて
                # 一意化し、全1654件を実際にカバーする)。
                items.append(dict(
                    item_id=f"{group}::{article_dir}::{level}::{segment_id}",
                    group=group, article_dir=article_dir, level=level,
                    segment_id=segment_id, path=wav_path,
                    category=category, in_active_narration_dir=True,
                    **info,
                ))
        log(f"  [{group}] {len(narration_dirs)} narration dirs -> "
            f"{sum(1 for it in items if it['group'] == group)} wav items")

    # ---- 既知事例確認用の追加item(narration/外の履歴backup、audit/読み取りのみ) ----
    known_extra = []
    rerun02_a2_parts = _load_json(
        "er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2/parts.json")
    known_specs = [
        dict(item_id="known_case::point_two_BUGGY_UNFIXED_backup",
             group="known_case_validation", level="a2", segment_id="point_two_BUGGY_UNFIXED",
             path="er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
                  "duplication_diagnosis_review_fix_02/"
                  "2_a2_point_two_narration_BUGGY_UNFIXED_pending_human_review.wav",
             canonical_text=(rerun02_a2_parts or {}).get("point_two_body"),
             note="OPEN-121行既知事例: Trial-13時点TTS生成そのもののhallucination"
                  "(冒頭2文がまるごと1回逐語反復)。現在のnarration/point_two.wav"
                  "とは別ファイル(2026-09-07サブタスクEで別attemptが正式accept・"
                  "再Assembly済み、このBUGGYバックアップはaudit/配下の履歴のみ)。"),
        dict(item_id="known_case::in_one_line_BEFORE_FIX_buggy_backup",
             group="known_case_validation", level="a2", segment_id="in_one_line_BEFORE_FIX_buggy",
             path="er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
                  "duplication_diagnosis_review_fix_02/"
                  "3_a2_in_one_line_narration_BEFORE_FIX_buggy.wav",
             canonical_text=(rerun02_a2_parts or {}).get("in_one_line"),
             note="OPEN-121行既知事例: 主節全体が1回逐語反復。現在のnarration/"
                  "in_one_line.wavは既存Production関数による再生成で修正済み"
                  "(このBUGGYバックアップはaudit/配下の履歴のみ)。"),
        dict(item_id="known_case::b1_fsp1_falsestart_clip_0-3s",
             group="known_case_validation", level="b1b", segment_id="b1_fsp1_falsestart_clip",
             path="er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/"
                  "duplication_diagnosis_review_fix_02/b1_fsp1_recheck/"
                  "falsestart_opening_0-3s.wav",
             canonical_text="As of September 2026, travel surveys in Japan tell a story "
                             "with two different speeds.",
             note="OPEN-121行既知事例: B1 Full Story Part 1冒頭のpartial-word false start"
                  "(\"As of Septem, As of September 2026...\")を切り出した0-3秒clip。"
                  "本体はrerun_02/trial_13/open117_trial02_kpの各b1b/narration/"
                  "full_story_part1.wav(全て同一sha256、メインinventoryで別途スキャン)。"),
    ]
    for spec in known_specs:
        if not os.path.exists(spec["path"]):
            log(f"  [skip known_case, missing] {spec['item_id']}")
            continue
        text = spec.pop("canonical_text")
        known_extra.append(dict(
            article_dir=os.path.dirname(spec["path"]), category="en_body",
            in_active_narration_dir=False, canonical_text=text,
            canonical_source="known_case_hardcoded_from_parts_json_or_falsestart_report",
            language="en", tts_status=None, review_lock_available=False,
            review_lock_state=None, review_lock_final_status=None, review_lock_wav_path=None,
            **spec,
        ))
    items.extend(known_extra)
    log(f"build_inventory: {len(known_extra)} known_case_validation items added")

    for it in items:
        it["sha256"] = sha256_of(it["path"])
        it["duration_seconds"] = round(t2.duration_seconds(it["path"]), 3)

    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    by_cat = {}
    for it in items:
        by_cat[it["category"]] = by_cat.get(it["category"], 0) + 1
    log(f"build_inventory: {len(items)} total items -> {INVENTORY_PATH}")
    log(f"  by category: {by_cat}")
    return items


# ============================================================
# Phase 1: 方式D'(全item、full-file、閾値0.6)
# ============================================================
def run_d_prime(limit=None, resume=True):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    items = json.load(open(INVENTORY_PATH, encoding="utf-8"))
    out_path = f"{RESULTS_DIR}/method_d_prime.json"
    results = _load_json(out_path) or {} if resume else {}
    t_start = time.time()
    n_done = 0
    for it in items:
        if limit and n_done >= limit:
            break
        if resume and it["item_id"] in results:
            continue
        t0 = time.time()
        r = t2.short_run_priority_autocorrelation(it["path"])
        r["elapsed_seconds"] = round(time.time() - t0, 2)
        results[it["item_id"]] = r
        n_done += 1
        best06 = r["best_by_threshold"].get("0.6", {})
        if n_done % 25 == 0:
            log(f"  [D'] {n_done} done, last={it['item_id']} run@0.6={best06.get('run_length_seconds')}s "
                f"elapsed_total={round(time.time()-t_start,1)}s")
        if n_done % 50 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"run_d_prime: {n_done} newly processed, {len(results)} total in {out_path} "
        f"(elapsed {round(time.time()-t_start,1)}s)")
    return results


# ============================================================
# Phase 2: 方式D(参考、min_lag=1.0秒、en_body + known_case のみ)
# ============================================================
def run_d(limit=None, resume=True):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    items = [it for it in json.load(open(INVENTORY_PATH, encoding="utf-8"))
             if it["category"] == "en_body"]
    out_path = f"{RESULTS_DIR}/method_d.json"
    results = _load_json(out_path) or {} if resume else {}
    t_start = time.time()
    n_done = 0
    for it in items:
        if limit and n_done >= limit:
            break
        if resume and it["item_id"] in results:
            continue
        t0 = time.time()
        sim = t2.spectral_self_similarity(it["path"])
        best_run = max((m.get("run_length_seconds_at_thresh_0.85", 0.0) for m in sim["top_matches"]),
                       default=0.0)
        results[it["item_id"]] = {
            "duration_seconds": sim["duration_seconds"], "best_run_length_seconds": best_run,
            "top_matches": sim["top_matches"], "elapsed_seconds": round(time.time() - t0, 2),
        }
        n_done += 1
        if n_done % 10 == 0:
            log(f"  [D] {n_done}/{len(items)} done, last={it['item_id']} best_run={best_run} "
                f"elapsed_total={round(time.time()-t_start,1)}s")
        if n_done % 20 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"run_d: {n_done} newly processed, {len(results)} total in {out_path} "
        f"(elapsed {round(time.time()-t_start,1)}s)")
    return results


# ============================================================
# Phase 3: 方式A(n-gram min_words=3 + canonical crosscheck、
# en_body + canonical_text既知のみ、faster-whisper local)
# ============================================================
def run_method_a(limit=None, resume=True):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    items = [it for it in json.load(open(INVENTORY_PATH, encoding="utf-8"))
             if it["category"] == "en_body" and it.get("canonical_text")]
    skipped = [it for it in json.load(open(INVENTORY_PATH, encoding="utf-8"))
               if it["category"] == "en_body" and not it.get("canonical_text")]
    out_path = f"{RESULTS_DIR}/method_a.json"
    results = _load_json(out_path) or {} if resume else {}
    t_start = time.time()
    n_done = 0
    for it in items:
        if limit and n_done >= limit:
            break
        if resume and it["item_id"] in results:
            continue
        t0 = time.time()
        words = dq18.transcribe_verbatim(it["path"], language="en", model_size="small")
        proposed = t2.detect_ngram_repetition(words, canonical_text=it.get("canonical_text"), min_words=3)
        results[it["item_id"]] = {
            "word_count": len(words), "proposed_ngram_min3_canonical_crosscheck": proposed,
            "elapsed_seconds": round(time.time() - t0, 2),
        }
        n_done += 1
        if n_done % 10 == 0:
            log(f"  [A] {n_done}/{len(items)} done, last={it['item_id']} "
                f"flagged={proposed['flagged']} elapsed_total={round(time.time()-t_start,1)}s")
        if n_done % 20 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"run_method_a: {n_done} newly processed, {len(results)} total in {out_path} "
        f"({len(skipped)} en_body items skipped: canonical未取得) (elapsed {round(time.time()-t_start,1)}s)")
    with open(f"{RESULTS_DIR}/method_a_skipped_no_canonical.json", "w", encoding="utf-8") as f:
        json.dump([it["item_id"] for it in skipped], f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# Phase 4: 分類・集計
# ============================================================
FLAG_D_PRIME_THRESH = 0.7
BOUNDARY_D_PRIME_LOW = 0.5
BOUNDARY_D_PRIME_HIGH = 0.7
FLAG_D_THRESH = 0.6


def classify():
    items = json.load(open(INVENTORY_PATH, encoding="utf-8"))
    d_prime = _load_json(f"{RESULTS_DIR}/method_d_prime.json") or {}
    d_res = _load_json(f"{RESULTS_DIR}/method_d.json") or {}
    a_res = _load_json(f"{RESULTS_DIR}/method_a.json") or {}

    rows = []
    for it in items:
        dp = d_prime.get(it["item_id"])
        dp_run = (dp or {}).get("best_by_threshold", {}).get("0.6", {}).get("run_length_seconds")
        dp_lag = (dp or {}).get("best_by_threshold", {}).get("0.6", {}).get("lag")
        d = d_res.get(it["item_id"])
        d_run = (d or {}).get("best_run_length_seconds")
        a = a_res.get(it["item_id"])
        a_flagged = None
        a_spans = None
        if a:
            proposed = a["proposed_ngram_min3_canonical_crosscheck"]
            a_flagged = proposed["flagged"]
            a_spans = proposed["flagged_matches"]

        flags = []
        boundary = False
        if dp_run is not None:
            if dp_run >= FLAG_D_PRIME_THRESH:
                flags.append("FLAG_D_PRIME")
            elif BOUNDARY_D_PRIME_LOW <= dp_run < BOUNDARY_D_PRIME_HIGH:
                boundary = True
        if d_run is not None and d_run >= FLAG_D_THRESH:
            flags.append("FLAG_D")
        if a_flagged:
            flags.append("FLAG_A")

        if flags:
            judgement = "+".join(flags) + ("+BOUNDARY_WATCH" if boundary else "")
        elif boundary:
            judgement = "BOUNDARY_WATCH"
        else:
            judgement = "CLEAN"

        rows.append({
            "item_id": it["item_id"], "group": it["group"], "level": it["level"],
            "segment_id": it["segment_id"], "path": it["path"], "category": it["category"],
            "language": it["language"], "duration_seconds": it["duration_seconds"],
            "canonical_source": it.get("canonical_source"),
            "review_lock_state": it.get("review_lock_state"),
            "review_lock_final_status": it.get("review_lock_final_status"),
            "tts_status": it.get("tts_status"),
            "in_active_narration_dir": it.get("in_active_narration_dir"),
            "d_prime_run_at_0.6": dp_run, "d_prime_lag": dp_lag,
            "d_best_run_length_seconds": d_run,
            "a_flagged": a_flagged, "a_flagged_spans": a_spans,
            "flags": flags, "boundary_watch": boundary, "judgement": judgement,
        })

    with open(CLASSIFIED_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # ---- 集計 ----
    def count_where(pred):
        return sum(1 for r in rows if pred(r))

    main_pop = [r for r in rows if r["category"] == "en_body" and r["group"] != "known_case_validation"]
    stats = {
        "total_items": len(rows),
        "by_category": {},
        "main_population_en_body": len(main_pop),
        "main_flag_d_prime": count_where(lambda r: "FLAG_D_PRIME" in r["flags"] and r in main_pop),
        "main_flag_d": count_where(lambda r: "FLAG_D" in r["flags"] and r in main_pop),
        "main_flag_a": count_where(lambda r: "FLAG_A" in r["flags"] and r in main_pop),
        "main_boundary_watch": count_where(lambda r: r["boundary_watch"] and r in main_pop),
        "main_clean": count_where(lambda r: r["judgement"] == "CLEAN" and r in main_pop),
        "known_case_validation": [r for r in rows if r["group"] == "known_case_validation"],
    }
    for cat in set(r["category"] for r in rows):
        stats["by_category"][cat] = len(ize_ := [r for r in rows if r["category"] == cat])
    with open(SUMMARY_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    log(f"classify: {len(rows)} rows classified. main_population(en_body, excl. known_case)={len(main_pop)}")
    log(f"  FLAG_D_PRIME={stats['main_flag_d_prime']} FLAG_D={stats['main_flag_d']} "
        f"FLAG_A={stats['main_flag_a']} BOUNDARY_WATCH={stats['main_boundary_watch']} "
        f"CLEAN={stats['main_clean']}")
    log("  known_case_validation judgements:")
    for r in stats["known_case_validation"]:
        log(f"    {r['item_id']}: judgement={r['judgement']} d_prime_run={r['d_prime_run_at_0.6']} "
            f"a_flagged={r['a_flagged']}")
    return rows, stats


# ============================================================
# Phase 5: 疑いのある件のclip切り出し + player.html
# ============================================================
def build_clips_and_player():
    import soundfile as sf
    os.makedirs(CLIPS_DIR, exist_ok=True)
    rows = json.load(open(CLASSIFIED_PATH, encoding="utf-8"))
    suspicious = [r for r in rows if r["judgement"] != "CLEAN"]
    log(f"build_clips_and_player: {len(suspicious)} suspicious/boundary items")

    for r in suspicious:
        try:
            data, sr = sf.read(r["path"], always_2d=False)
        except Exception as e:
            log(f"  [warn] failed to read {r['path']}: {e}")
            continue
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", r["item_id"])
        # 先頭10秒
        head = data[: int(10.0 * sr)]
        head_path = f"{CLIPS_DIR}/{safe_id}__head10s.wav"
        sf.write(head_path, head, sr, subtype="PCM_16")
        r["clip_head10s"] = head_path
        # D'該当区間(time_a〜time_a+lag+run+1秒、あれば)
        if r.get("d_prime_run_at_0.6") and r.get("d_prime_lag"):
            d_prime = _load_json(f"{RESULTS_DIR}/method_d_prime.json") or {}
            best06 = (d_prime.get(r["item_id"]) or {}).get("best_by_threshold", {}).get("0.6", {})
            time_a = best06.get("time_a")
            lag = best06.get("lag")
            run_len = best06.get("run_length_seconds", 0.0)
            if time_a is not None and lag is not None:
                start_s = max(0.0, time_a - 0.5)
                end_s = min(len(data) / sr, time_a + lag + run_len + 1.0)
                region = data[int(start_s * sr): int(end_s * sr)]
                region_path = f"{CLIPS_DIR}/{safe_id}__region_{start_s:.1f}s-{end_s:.1f}s.wav"
                sf.write(region_path, region, sr, subtype="PCM_16")
                r["clip_region"] = region_path
                r["clip_region_start_s"] = round(start_s, 2)
                r["clip_region_end_s"] = round(end_s, 2)

    with open(CLASSIFIED_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def row_html(r):
        rel_full = os.path.relpath(r["path"], OUT_DIR).replace("\\", "/")
        head_rel = os.path.relpath(r["clip_head10s"], OUT_DIR).replace("\\", "/") if r.get("clip_head10s") else None
        region_rel = os.path.relpath(r["clip_region"], OUT_DIR).replace("\\", "/") if r.get("clip_region") else None
        canon = ""
        return ("<tr>"
                f"<td>{esc(r['item_id'])}</td>"
                f"<td>{esc(r['judgement'])}</td>"
                f"<td>{r['duration_seconds']}</td>"
                f"<td>d'={r.get('d_prime_run_at_0.6')} lag={r.get('d_prime_lag')} / "
                f"d={r.get('d_best_run_length_seconds')} / a_flagged={r.get('a_flagged')}</td>"
                f"<td>full: <audio controls src='{rel_full}'></audio></td>"
                f"<td>{'head10s: <audio controls src=' + chr(39) + head_rel + chr(39) + '></audio>' if head_rel else ''}</td>"
                f"<td>{('region(' + str(r.get('clip_region_start_s')) + '-' + str(r.get('clip_region_end_s')) + 's): <audio controls src=' + chr(39) + region_rel + chr(39) + '></audio>') if region_rel else ''}</td>"
                f"<td style='max-width:300px;font-size:11px'>{esc(r.get('canonical_source'))}</td>"
                "</tr>")

    html = ["<html><head><meta charset='utf-8'>"
            "<title>OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01 player</title></head><body>",
            "<h1>OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01: 疑い・境界付近一覧</h1>",
            "<p>読み取り専用スイープ。自動再生成なし。判定はFLAG_D_PRIME(run@0.6&gt;=0.7秒)/"
            "FLAG_D(参考、run&gt;=0.6秒)/FLAG_A(n-gram句・文反復)/BOUNDARY_WATCH"
            "(D' run 0.5〜0.7秒)。</p>",
            "<table border=1 cellpadding=4 style='border-collapse:collapse'>",
            "<tr><th>item_id</th><th>判定</th><th>dur(s)</th><th>signals</th>"
            "<th>full audio</th><th>head10s</th><th>region</th><th>canonical source</th></tr>"]
    for r in suspicious:
        html.append(row_html(r))
    html.append("</table></body></html>")
    with open(PLAYER_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    log(f"player.html -> {PLAYER_PATH} ({len(suspicious)} rows)")
    return PLAYER_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=[
        "build_inventory", "run_d_prime", "run_d", "run_method_a",
        "classify", "build_clips_and_player",
    ])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.phase == "build_inventory":
        build_inventory()
    elif args.phase == "run_d_prime":
        run_d_prime(limit=args.limit, resume=not args.no_resume)
    elif args.phase == "run_d":
        run_d(limit=args.limit, resume=not args.no_resume)
    elif args.phase == "run_method_a":
        run_method_a(limit=args.limit, resume=not args.no_resume)
    elif args.phase == "classify":
        classify()
    elif args.phase == "build_clips_and_player":
        build_clips_and_player()
