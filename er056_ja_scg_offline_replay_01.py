# ============================================================
# er056_ja_scg_offline_replay_01.py
# 管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01 (日本語側、2026-10-11)
# 完全オフライン再計算(課金0・API呼び出しなし・Productionコード無変更・read-only)。
#  - Phase 0 Trial(OPEN-258)の保存済みAzure転写25行 + 既存Primary転写を、現行コード
#    (er007_ja_asr_validator_01 / er007_ja_secondary_asr_01)で再判定する。
#  - 除外ポリシー(現行 / C1解除 / 数字・否定のみ除外 / 除外なし)ごとに、
#    誤PASS件数・救済件数・再生成削減回数・SCG呼出数を集計する。
#  - 代表ケース(合成入力)について、現行コードの経路(除外理由 or Azure呼出)を確認する。
#    合成ケースのSecondary転写は実測ではなく仮定であり、経路確認のみ(ASR性能の証拠ではない)。
# 出力: er056_output/asr_tts_cross_language_reconciliation_01/ja_offline_replay_01.json
# 実行: .venv\Scripts\python.exe er056_ja_scg_offline_replay_01.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")
sys.path.insert(0, ".")

import er007_ja_asr_validator_01 as javal  # noqa: E402
import er007_ja_secondary_asr_01 as scg  # noqa: E402

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False  # LLM(有料)を呼ばない。Phase 0もResolver OFFで再判定している

P0 = "er053_output/open258_phase0_trial_01"
EVID = "er053_output/family_x_tts_asr_rootcause_01/OPEN258_OFFLINE_EVIDENCE_01.json"
OUT = "er056_output/asr_tts_cross_language_reconciliation_01/ja_offline_replay_01.json"

PASS_CLS = ("EXACT_MATCH", "NORMALIZED_MATCH")

# ground truth(RESULT_01の記述に基づく分類。ground truthは試聴のみ=標本ラベルは代理)
#  error_proxy: C群(whisper small/medium(原稿非提示)とPrimaryが原稿と不一致=TTS誤りの代理)
#  correct_user: ユーザー試聴で正(META出演)
#  correct_strong: Azure+whisper small+whisper mediumが原稿と一致、または表記差のみ(Primaryだけが誤認)
#  correct_probable: whisperの少なくとも一方が原稿と一致(Azure NGでも)
#  needs_listen: RESULT_01(4)で「要試聴」とされた音声(Azure PASSだがwhisper/Primaryと不一致)
GT = {
    "g35_japanese_title_a1": "correct_user", "g35_japanese_title_a2": "correct_user", "g35_japanese_title_a3": "correct_user",
    "g12_kp1_ja_aoede_a2": "error_proxy", "g3_kp4_ja_charon_a1": "error_proxy", "g4_kp2_ja_charon_a1": "error_proxy",
    "g5_kp4_ja_charon_a1": "error_proxy", "g6_kp5_ja_charon_a1": "error_proxy",
    "g2_kp2_ja_charon_a1": "correct_strong", "g8_kp4_ja_charon_a1": "correct_strong",
    "g11_kp5_ja_aoede_a1": "needs_listen", "g11_kp5_ja_aoede_a2": "correct_strong",
    "g17_kp5_ja_charon_a1": "correct_strong", "g20_kp2_ja_charon_a1": "correct_strong",
    "g21_comment_3_a1": "correct_strong", "g23_meaning_2_a1": "correct_probable",
    "g27_kp1_ja_charon_a1": "needs_listen", "g31_meaning_2_a1": "correct_strong",
    "g33_meaning_5_a1": "correct_strong", "g33_meaning_5_a2": "correct_strong",
    "g36_comment_1_a1": "correct_strong", "g18_meaning_2_a2": "needs_listen", "g18_meaning_2_a3": "needs_listen",
    "g1_meaning_4_a1": "needs_listen", "g7_meaning_4_a1": "correct_strong",
}


def exclusion_under(policy: str, cls, canonical: str, primary: str, length_ok: bool = True):
    """policy別のSCG除外理由。None=Secondary(Azure)を呼ぶ。現行コードの_scg_exclusion_reasonを部品として再利用。"""
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        return "not_true_content_mismatch"
    if policy == "ALL":  # 除外なし(Primary NGなら必ずSecondary)
        return None
    if cls.protected.number_mismatches:
        return "number_mismatch"
    if cls.protected.negation_mismatches:
        return "negation_mismatch"
    if policy == "HARD_ONLY":  # 数字・否定(保護チェック+否定マーカー)のみ除外
        if scg._scg_negation_marker_diff(canonical, primary):
            return "negation_marker_diff"
        return None
    # 以下は CURRENT / NO_C1 / NO_SIM
    if policy in ("CURRENT", "NO_C1") and cls.similarity_ratio < scg.SCG_MIN_SIMILARITY:
        return "similarity_lt_0.4"
    for d in (cls.protected.content_diffs or []):
        if policy == "CURRENT":
            if d.get("reading_dictionary_mismatch"):
                return "reading_dictionary_mismatch"
            if d.get("entity_like"):
                return "entity_like_diff"
            if scg._has_latin(d.get("canonical", "")):
                return "latin_in_canonical_diff"
        else:  # NO_C1: C1(entity_like/辞書読み/ラテン)だけ解除、C2は残す
            pass
        if scg._scg_heterophone_candidate(d):
            return "heterophone_reading_candidate"
    if scg._scg_negation_marker_diff(canonical, primary):
        return "negation_marker_diff"
    return None


POLICIES = ["CURRENT", "NO_C1", "HARD_ONLY", "ALL"]


def main():
    res = [json.loads(l) for l in open(f"{P0}/results_01.jsonl", encoding="utf-8")]
    wh = json.load(open(f"{P0}/whisper_aux_01.json", encoding="utf-8"))
    ev = json.load(open(EVID, encoding="utf-8"))["impact_estimate_from_logs"]["groups"]
    rows = []
    for r in res:
        c, p = r["canonical"], r["primary_asr"]
        cls = javal.classify_ja_asr_match(c, p)
        sec = javal.classify_ja_asr_match(c, r["secondary_text"], allow_reading_resolver=False) if r["secondary_text"] else None
        sec_pass = bool(sec and sec.classification in PASS_CLS)
        row = {
            "key": r["key"], "group": r["group"], "attempt": r["attempt"], "role": r["role"], "gt": GT[r["key"]],
            "canonical": c, "primary": p, "secondary": r["secondary_text"], "duration_s": r["duration_s"],
            "wall_s": r["wall_seconds"], "est_cost_jpy": r["est_cost_jpy"],
            "primary_cls_now": cls.classification, "similarity": round(cls.similarity_ratio, 3),
            "content_diffs": [(d["canonical"], d["asr"], d["entity_like"], d["phonetic_uncertain"]) for d in cls.protected.content_diffs],
            "number_mm": cls.protected.number_mismatches, "neg_mm": cls.protected.negation_mismatches,
            "secondary_cls_now": sec.classification if sec else None, "secondary_pass": sec_pass,
            "whisper_small": wh[r["key"]]["small"]["agrees_with_canonical"], "whisper_medium": wh[r["key"]]["medium"]["agrees_with_canonical"],
        }
        for pol in POLICIES:
            ex = exclusion_under(pol, cls, c, p)
            row[f"excl_{pol}"] = ex
            row[f"call_{pol}"] = ex is None
            row[f"pass_{pol}"] = (ex is None) and sec_pass
            # 参考: Secondary PHONETIC_MATCH(読み一致の表記差)もPASSに含める仮定(現行は含めない=ユーザー決定済み安全条件)
            row[f"pass_phon_{pol}"] = (ex is None) and bool(sec and sec.classification in PASS_CLS + ("PHONETIC_MATCH",))
        rows.append(row)

    # ---- 集計(音声単位) ----
    summ = {}
    for pol in POLICIES:
        calls = [x for x in rows if x[f"call_{pol}"]]
        passed = [x for x in rows if x[f"pass_{pol}"]]
        fp = [x["key"] for x in passed if x["gt"] == "error_proxy"]
        correct = [x for x in rows if x["gt"].startswith("correct")]
        rescued_correct = [x["key"] for x in passed if x["gt"].startswith("correct")]
        need = [x["key"] for x in passed if x["gt"] == "needs_listen"]
        summ[pol] = {
            "azure_calls": len(calls), "azure_audio_seconds": round(sum(x["duration_s"] for x in calls), 1),
            "azure_est_cost_jpy": round(sum(x["est_cost_jpy"] for x in calls), 3),
            "azure_wall_s": round(sum(x["wall_s"] for x in calls), 1),
            "scg_pass_total": len(passed), "false_pass_error_proxy": fp,
            "rescued_correct_audio": len(rescued_correct), "correct_audio_total": len(correct),
            "scg_pass_needs_listen": need,
            "pass_if_phonetic_allowed": len([x for x in rows if x[f"pass_phon_{pol}"]]),
            "false_pass_if_phonetic_allowed": [x["key"] for x in rows if x[f"pass_phon_{pol}"] and x["gt"] == "error_proxy"],
            "false_NG_remaining_correct_audio": [x["key"] for x in correct if not x[f"pass_{pol}"]],
        }

    # ---- group単位(再生成削減) ----
    by_g = {}
    for x in rows:
        by_g.setdefault(x["group"], []).append(x)
    group_rows = []
    for g, xs in sorted(by_g.items()):
        e = ev[g]
        rec = {"group": g, "seg": e["seg"], "n_attempts_hist": e["n_attempts"], "final_verified_hist": e["final_verified"],
               "tested": [(x["attempt"], x["gt"]) for x in xs]}
        for pol in POLICIES:
            ks = [x["attempt"] for x in xs if x[f"pass_{pol}"]]
            k = min(ks) if ks else None
            rec[f"rescue_attempt_{pol}"] = k
            rec[f"regen_avoided_{pol}"] = max(e["n_attempts"] - k, 0) if k else 0
            rec[f"completes_{pol}"] = bool(k) or bool(e["final_verified"])
        group_rows.append(rec)
    # g24=g21, g26=g23(同一音声) は24/26は実行していないため参考として付記しない(重複防止)


    # ---- 3回上限(現行Production=PRODUCTION_MAX_TTS_ATTEMPTS)を適用した標本内の再生成/完成の再計算 ----
    cap = 3
    cap3 = {}
    base_att = sum(min(g["n_attempts_hist"], cap) for g in group_rows)
    base_complete = sum(1 for g in group_rows if g["final_verified_hist"] and g["n_attempts_hist"] <= cap)
    cap3["groups_in_sample"] = len(group_rows)
    cap3["PRE_SCG"] = {"tts_attempts": base_att, "completed_within_cap": base_complete,
                       "human_review_or_stopped": len(group_rows) - base_complete}
    for pol in POLICIES:
        att = comp = 0
        for g in group_rows:
            k = g[f"rescue_attempt_{pol}"]
            if k and k <= cap:
                att += k
                comp += 1
            else:
                att += min(g["n_attempts_hist"], cap)
                comp += 1 if (g["final_verified_hist"] and g["n_attempts_hist"] <= cap) else 0
        cap3[pol] = {"tts_attempts": att, "completed_within_cap": comp, "human_review_or_stopped": len(group_rows) - comp,
                     "tts_attempts_saved_vs_pre": base_att - att}

    # ---- 合成代表ケース(経路確認のみ) ----
    synth = [
        ("通常語(助詞)", "世界市場の価格は下がりました", "世界市場の価格が下がりました"),
        ("通常語(漢字近音)", "AIの電話に人間が出演", "AIの電話に人間が出現"),
        ("カナ・濁点のみ(単独)", "出るガス", "出るカス"),
        ("カナ・濁点+他の差分(g8型)", "熟すと出るガス", "じくすと出るカス"),
        ("カナ固有名詞(挿入: メタ->メタン)", "メタに投資する", "メタンに投資する"),
        ("カナ固有名詞(置換: ダ/タ)", "メダに投資する", "メタに投資する"),
        ("漢字固有名詞(同読み)", "李さんが発表した", "里さんが発表した"),
        ("漢字固有名詞(別読み)", "鈴木さんが発表した", "薄木さんが発表した"),
        ("数値", "理由は3つ", "理由は4つ"),
        ("否定(ず)", "縛られず自由になれる", "縛られる自由になれる"),
        ("否定(ない/なかった)", "彼は来なかった", "彼は来た"),
        ("否定(ない)", "行かない予定", "行く予定"),
        ("時制(た/る)", "会議は終わった", "会議は終わる"),
        ("同音異義(市場 いち/し)", "市場で野菜を買う", "資場で野菜を買う"),
        ("同形異音(行った)", "試合に行った", "試合を行った"),
        ("同形異音(行った 差分が行)", "調査を行った", "調査を言った"),
    ]
    syn_rows = []
    for name, c, p in synth:
        cls = javal.classify_ja_asr_match(c, p)
        item = {"case": name, "canonical": c, "primary": p, "primary_cls": cls.classification,
                "content_diffs": [(d["canonical"], d["asr"], d["entity_like"], d["phonetic_uncertain"]) for d in cls.protected.content_diffs]}
        if cls.classification == "TRUE_CONTENT_MISMATCH":
            item["route_current"] = scg._scg_exclusion_reason(cls, c, p) or "SCG: Azure 1回を呼ぶ"
        elif cls.classification == "ASR_VALIDATION_UNCERTAIN":
            item["route_current"] = "legacy Cascade(Primary#2->Azure#1->Azure#2、PHONETIC_MATCH含むshould_passでPASS、全不一致=Human Review)"
        else:
            item["route_current"] = "Primary PASS(Secondaryなし)"
        syn_rows.append(item)

    out = {"rows": rows, "summary": summ, "groups": group_rows, "cap3_sample": cap3, "synthetic_route_check": syn_rows,
           "note": "API未使用。Resolver LLM OFF。ground truthは代理ラベル(GT定数、RESULT_01(4)準拠)。"}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(cap3, ensure_ascii=False, indent=1))
    for s in syn_rows:
        print(s["case"], "|", s["primary_cls"], "|", s["route_current"], "|", s["content_diffs"])


if __name__ == "__main__":
    main()
