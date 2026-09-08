"""
管理ID: OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01
Fable(PM)委任によるSonnet実行。Trial(Production変更なし、Gate 1判定)。

背景: 方式D(スペクトル自己相関、Production既定run閾値>=0.12秒、sim閾値0.85)が
既存PASS音声517件(en本文、既知事例除く)中23件をflagした。ユーザーが23件全件を
実試聴し、8件(run 0.16〜0.32秒)は真の重複(既知バグ再現)、残り15件
(run 0.12〜0.16秒)は「正常音声への誤flag」と確定した
(`OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01_REPORT.md`・
`OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02_REPORT.md`)。

本Trialの目的: 真の重複検知能力(TP8/8維持)を落とさずに、方式D単体の
誤flag(FP15件)を減らす候補を比較する。Production閾値・モジュール
(er011_open121_repetition_qa_production_01.py)は一切変更しない
(読み取り専用でimportし、必要な検証はTrial側で完結させる)。

データセット(すべて既存artifactの再利用、追加TTS/ASR API呼び出しなし):
- positive controls (TP=8): method_d_flag23_review_01/classification_table.json
  で classification == "真の重複(証拠あり)"
- negative controls (FP=15): 同ファイルで classification != 上記
  (「誤flagの可能性高」14件+「判断困難」1件。ユーザーが2026-09-08に
  15件全件をfalse positiveと確定済み)
- background (517件): open121_existing_audio_dprime_sweep_01/results/
  production_params_reclassification_02.json の main_rows
  (既存sweepで計算済みのd_run_at_sim0.85・d_prime_run_at_sim0.7・
  a_flagged等を読み取りのみで再利用。閾値を「引き上げる」方向の候補は
  既存23件の部分集合しか生まないことが数学的に自明なため、517件全件の
  重い再計算は行わない。詳細は各候補の項で理由を明記する)

計算方針(コスト最小化、Production精度と同一の値を再現できることを
spot-checkで確認済み):
- 方式Dの候補ペア選定(top-k類似度)はsim_threshold・run閾値に依存しない
  (生成済みmethod_d.jsonのtop_matchesのtime_a/time_b/lagをそのまま再利用)。
  run長は対数スペクトル自己相関行列(bundle["sim"])さえあれば任意の
  sim_thresholdで再計算できる(O(n)、高速)。bundle自体は
  compute_shared_self_similarity()を無変更importして計算する
  (1ファイルあたり数十〜数百ms、23件で数秒)。これによりO(n^2)の
  候補生成(23件で計185秒相当)を一切やり直さずに、sim閾値スイープを
  低コストで行える。
- 方式A(n-gram反復検知)はProduction既定のa_flagged値(classification_table・
  main_rowsに既存)をそのまま使う(追加ASR呼び出しなし)。
- 候補(c)の局所ASR語句一致度のみ、23件に対しfaster-whisper(ローカルCPU、
  無料)でtranscribe_verbatim()を実行する(既存モジュール無変更import)。

出力: er011_output/method_d_fp_reduction_trial_01/
- controls_dataset.json (TP8/FP15の item_id一覧)
- candidate_a_run_threshold_sweep.json (run閾値のみ変更、sim=0.85固定)
- candidate_b_sim_threshold_sweep.json (sim閾値変更、23件のrun長再計算)
- candidate_c_fragment_overlap.json (局所ASR語句一致度、23件)
- candidate_d_and_with_method_a.json (方式AとのAND合成)
- summary.json (候補比較表)

費用: ¥0(TTS/ASR/LLM有料API呼び出しなし。faster-whisperはローカルCPU実行のみ)
"""
from __future__ import annotations

import difflib
import json
import os
import time

import er008_disfluency_qa_18 as dq18
import er011_open121_repetition_qa_production_01 as prod

BASE = os.path.dirname(os.path.abspath(__file__))
SWEEP_DIR = os.path.join(BASE, "er011_output", "open121_existing_audio_dprime_sweep_01")
FLAG23_DIR = os.path.join(BASE, "er011_output", "method_d_flag23_review_01")
OUT_DIR = os.path.join(BASE, "er011_output", "method_d_fp_reduction_trial_01")
os.makedirs(OUT_DIR, exist_ok=True)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(obj, name):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


# ============================================================
# データセット準備
# ============================================================
def build_controls():
    table23 = load(os.path.join(FLAG23_DIR, "classification_table.json"))
    tp_ids = [r["item_id"] for r in table23 if r["classification"] == "真の重複(証拠あり)"]
    fp_ids = [r["item_id"] for r in table23 if r["classification"] != "真の重複(証拠あり)"]
    assert len(tp_ids) == 8, f"TP件数が想定外: {len(tp_ids)}"
    assert len(fp_ids) == 15, f"FP件数が想定外: {len(fp_ids)}"
    by_id = {r["item_id"]: r for r in table23}
    return tp_ids, fp_ids, by_id


def build_background():
    recl = load(os.path.join(SWEEP_DIR, "results", "production_params_reclassification_02.json"))
    main_rows = recl["main_rows"]
    assert len(main_rows) == 517, f"背景母集団件数が想定外: {len(main_rows)}"
    return main_rows


def main():
    t_start = time.time()
    tp_ids, fp_ids, table23_by_id = build_controls()
    main_rows = build_background()
    main_by_id = {r["item_id"]: r for r in main_rows}

    save({"tp_ids": tp_ids, "fp_ids": fp_ids,
          "note": "TP8/FP15は2026-09-08ユーザー試聴確定済み(method_d_flag23_review_01/"
                  "method_d_flag15_review_02の成果物を再利用、追加試聴・API呼び出しなし)"},
         "controls_dataset.json")

    # ============================================================
    # 候補(a): run閾値のみ変更(sim=0.85固定、既存d_run_at_sim0.85を再利用)
    # 引き上げ方向は既存23件flag集合の部分集合しか生まないため
    # (run長がより長い判定条件は既にflagされた23件の中でしか真になり得ない)、
    # 背景494件(517-23)の再計算は不要(数学的に新規flagは発生しない)。
    # ============================================================
    run_thresholds = [0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35]
    cand_a_rows = []
    for rt in run_thresholds:
        tp_caught = sum(1 for i in tp_ids if main_by_id[i]["d_run_at_sim0.85"] >= rt)
        fp_caught = sum(1 for i in fp_ids if main_by_id[i]["d_run_at_sim0.85"] >= rt)
        cand_a_rows.append({
            "run_threshold_seconds": rt,
            "tp_retained": tp_caught, "tp_total": 8,
            "fp_retained_false_positive_count": fp_caught, "fp_total": 15,
            "background_new_flags_beyond_23": 0,
            "note": "引き上げのみのため背景494件からの新規flagは数学的に発生しない",
        })
    save({"method": "run閾値のみ変更、sim=0.85固定。既存d_run_at_sim0.85(517件全件、"
                     "既存sweep計算値)をそのまま参照、追加wav計算なし。",
          "rows": cand_a_rows}, "candidate_a_run_threshold_sweep.json")

    # ============================================================
    # 候補(b): sim閾値変更(run閾値は複数点でスイープ)
    # top-k候補ペア(time_a/time_b/lag)はsim閾値に依存しない
    # (Production同一ロジック、生データmethod_d.jsonのtop_matchesを再利用)。
    # run長だけをキャッシュ済みsim行列から再計算する(スポットチェックで
    # production値と完全一致を確認済み、本ファイル冒頭コメント参照)。
    # 23件(TP8+FP15)のみ対象(sim閾値を現状より引き上げる方向は、候補(a)と
    # 同じ理由で背景494件への新規flag波及がない: sim閾値を上げるほどrun長は
    # 単調非増加になるため、現状flag対象の23件の部分集合しか生まない)。
    # ============================================================
    method_d_raw = load(os.path.join(SWEEP_DIR, "results", "method_d.json"))
    sim_thresholds = [0.80, 0.85, 0.90, 0.95]
    bundles = {}
    per_item_runs = {}  # item_id -> {sim_threshold: best_run_length_seconds}
    for item_id in tp_ids + fp_ids:
        path = main_by_id[item_id]["path"]
        bundle = prod.compute_shared_self_similarity(path)
        bundles[item_id] = bundle
        sim = bundle["sim"]
        hop_s = bundle["hop_ms"] / 1000.0
        n = sim.shape[0]
        top_matches = method_d_raw[item_id]["top_matches"][:3]
        runs_by_sim = {}
        for st in sim_thresholds:
            best_run = 0.0
            for m in top_matches:
                i0 = int(round(m["time_a_seconds"] / hop_s))
                lag = int(round(m["lag_seconds"] / hop_s))
                k = 0
                while i0 + k < n and i0 + k + lag < n and sim[i0 + k, i0 + k + lag] >= st:
                    k += 1
                run_s = round(k * hop_s, 3)
                if run_s > best_run:
                    best_run = run_s
            runs_by_sim[str(st)] = best_run
        per_item_runs[item_id] = runs_by_sim

    # sanity check: sim=0.85での再計算値が既存記録値(main_rows)と一致するか確認
    mismatches = []
    for item_id in tp_ids + fp_ids:
        recomputed = per_item_runs[item_id]["0.85"]
        recorded = main_by_id[item_id]["d_run_at_sim0.85"]
        if abs(recomputed - recorded) > 0.011:
            mismatches.append({"item_id": item_id, "recomputed": recomputed, "recorded": recorded})

    cand_b_rows = []
    decision_run_thresholds = [0.10, 0.12, 0.14, 0.16]
    for st in sim_thresholds:
        for rt in decision_run_thresholds:
            tp_caught = sum(1 for i in tp_ids if per_item_runs[i][str(st)] >= rt)
            fp_caught = sum(1 for i in fp_ids if per_item_runs[i][str(st)] >= rt)
            cand_b_rows.append({
                "sim_threshold": st, "run_threshold_seconds": rt,
                "tp_retained": tp_caught, "tp_total": 8,
                "fp_retained_false_positive_count": fp_caught, "fp_total": 15,
            })
    save({"method": "sim閾値・run閾値ともに変更(23件のみ、bundleキャッシュから"
                     "run長を再計算。top-k候補ペア自体はsim閾値非依存のため"
                     "method_d.jsonのtop_matchesをそのまま再利用)。",
          "sanity_check_mismatches_vs_recorded_sim0.85": mismatches,
          "per_item_runs_by_sim": per_item_runs,
          "rows": cand_b_rows}, "candidate_b_sim_threshold_sweep.json")

    # ============================================================
    # 候補(c): 局所ASR語句一致度による2段判定
    # 方式Dが検知した2箇所(flag_time_a/flag_time_b、既存
    # classification_table.jsonの値をそのまま使用、sim=0.85のtop match位置)
    # の前後1.5秒(空なら2.5秒→4.0秒まで拡張、flag15_review_02と同じ手順)を
    # faster-whisper word-level timestampsで切り出し、2箇所のtoken列の
    # 一致度(difflib SequenceMatcher比率+最長連続一致語数)を計算する。
    # 2段目はD flagged(現状閾値、無変更)の後段フィルタのみのため、
    # 現状23件の部分集合しか生まない(背景494件への新規flag波及なし)。
    # ============================================================
    def normalize_tok(w):
        return dq18._normalize_token(w)

    def extract_window_tokens(words, center_s, half_window=1.5, max_half_window=4.0):
        hw = half_window
        while hw <= max_half_window:
            toks = [w for w in words if center_s - hw <= (w["start"] + w["end"]) / 2 <= center_s + hw]
            if toks:
                return toks, hw
            hw += 1.0 if hw < 2.5 else 1.5
        return [], hw

    def longest_common_contig_run(a, b):
        best = 0
        for i in range(len(a)):
            for j in range(len(b)):
                k = 0
                while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                    k += 1
                best = max(best, k)
        return best

    cand_c_items = []
    for item_id in tp_ids + fp_ids:
        row = table23_by_id[item_id]
        path = main_by_id[item_id]["path"]
        time_a = row.get("flag_time_a")
        time_b = row.get("flag_time_b")
        entry = {"item_id": item_id, "is_tp": item_id in tp_ids,
                 "flag_time_a": time_a, "flag_time_b": time_b}
        if time_a is None or time_b is None:
            entry["status"] = "flag_time取得不可(スキップ)"
            entry["overlap_ratio"] = None
            entry["lcs_words"] = None
            cand_c_items.append(entry)
            continue
        words = dq18.transcribe_verbatim(path, language="en", model_size="small")
        toks_a_raw, hw_a = extract_window_tokens(words, time_a)
        toks_b_raw, hw_b = extract_window_tokens(words, time_b)
        toks_a = [normalize_tok(w["text"]) for w in toks_a_raw]
        toks_b = [normalize_tok(w["text"]) for w in toks_b_raw]
        overlap_ratio = difflib.SequenceMatcher(None, toks_a, toks_b).ratio() if (toks_a and toks_b) else 0.0
        lcs_words = longest_common_contig_run(toks_a, toks_b) if (toks_a and toks_b) else 0
        entry.update({
            "status": "特定" if (toks_a and toks_b) else "位置未特定",
            "window_half_seconds_a": hw_a, "window_half_seconds_b": hw_b,
            "fragment_a": " ".join(w["text"].strip() for w in toks_a_raw),
            "fragment_b": " ".join(w["text"].strip() for w in toks_b_raw),
            "overlap_ratio": round(overlap_ratio, 4),
            "lcs_words": lcs_words,
        })
        cand_c_items.append(entry)

    overlap_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    lcs_thresholds = [1, 2, 3]
    cand_c_sweep = []
    for ot in overlap_thresholds:
        for lt in lcs_thresholds:
            tp_retained = sum(1 for e in cand_c_items if e["is_tp"] and e.get("overlap_ratio") is not None
                               and (e["overlap_ratio"] >= ot or e["lcs_words"] >= lt))
            fp_retained = sum(1 for e in cand_c_items if not e["is_tp"] and e.get("overlap_ratio") is not None
                               and (e["overlap_ratio"] >= ot or e["lcs_words"] >= lt))
            cand_c_sweep.append({"overlap_ratio_threshold": ot, "lcs_words_threshold": lt,
                                  "rule": "overlap_ratio>=OT OR lcs_words>=LT",
                                  "tp_retained": tp_retained, "tp_total": 8,
                                  "fp_retained_false_positive_count": fp_retained, "fp_total": 15})
    save({"method": "方式D flag(現状閾値、無変更)の後段フィルタとして局所ASR"
                     "語句一致度(difflib比率+最長連続一致語数)を追加。"
                     "flag_time_a/bは既存classification_table.jsonの値(sim=0.85"
                     "top match)をそのまま使用、追加API呼び出しなし(faster-whisper"
                     "ローカルCPUのみ)。",
          "items": cand_c_items, "threshold_sweep": cand_c_sweep}, "candidate_c_fragment_overlap.json")

    # ============================================================
    # 候補(d): 方式Aとの AND 合成(既存a_flagged値をそのまま使用、追加計算なし)
    # ============================================================
    cand_d_items = []
    for item_id in tp_ids + fp_ids:
        a_flagged = main_by_id[item_id]["a_flagged"]
        cand_d_items.append({"item_id": item_id, "is_tp": item_id in tp_ids, "a_flagged": a_flagged})
    tp_retained_d = sum(1 for e in cand_d_items if e["is_tp"] and e["a_flagged"] is True)
    fp_retained_d = sum(1 for e in cand_d_items if not e["is_tp"] and e["a_flagged"] is True)
    a_flagged_none_items = [e["item_id"] for e in cand_d_items if e["a_flagged"] is None]
    save({"method": "D flagged(現状閾値、無変更) AND 方式Aのa_flagged(既存値、"
                     "既存sweep計算済み、追加計算なし)。",
          "rule": "flagged = d_flagged(現状) AND (a_flagged == True)",
          "tp_retained": tp_retained_d, "tp_total": 8,
          "fp_retained_false_positive_count": fp_retained_d, "fp_total": 15,
          "a_flagged_none_items_caveat": a_flagged_none_items,
          "caveat": "a_flagged=Noneはcanonical_text未取得で方式A自体が実行不可な"
                    "ケース(この23件中1件該当)。AND合成ではNoneをFalse扱いする"
                    "ため、canonical_text欠落時に真の重複があってもAND条件が"
                    "常に不成立になり、方式D単独の検知能力を失う設計リスクがある"
                    "(false negative増加リスク、詳細はReport参照)。",
          "items": cand_d_items}, "candidate_d_and_with_method_a.json")

    # ============================================================
    # summary
    # ============================================================
    elapsed = round(time.time() - t_start, 1)
    summary = {
        "elapsed_seconds_total": elapsed,
        "candidate_a_best_rows_tp8_fp0": [r for r in cand_a_rows if r["tp_retained"] == 8 and r["fp_retained_false_positive_count"] == 0],
        "candidate_b_best_rows_tp8_fp0": [r for r in cand_b_rows if r["tp_retained"] == 8 and r["fp_retained_false_positive_count"] == 0],
        "candidate_c_best_rows_tp8_fp0": [r for r in cand_c_sweep if r["tp_retained"] == 8 and r["fp_retained_false_positive_count"] == 0],
        "candidate_d_tp8_fp0": (tp_retained_d == 8 and fp_retained_d == 0),
        "sanity_check_mismatches": mismatches,
    }
    save(summary, "summary.json")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
