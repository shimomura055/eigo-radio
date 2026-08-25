# ============================================================
# er007_ja_tts_retry_path_fix_cost_01.py
# ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part E:
# 経路A(stop_retrying無視bug)・経路B(漢字読み揺れ誤分類)それぞれが
# 引き起こしていた可能性のある不要TTS retry回数・cost をcounterfactual
# 算出する。No.1-6の既存96 Japanese segment(er007_ja_cost_latency_
# projection_01.pyと同一データソース)を再利用し、新規TTS/ASRは呼ばない。
# ============================================================
import json

import er007_ja_asr_validator_01 as javal

TOPIC_DIRS = {
    "No.1": "pool_benches_luna", "No.2": "pool_subscriptions", "No.3": "pool_startups",
    "No.4": "pool_n4_supermarket", "No.5": "pool_n5_cafes", "No.6": "pool_n6_delivery",
}

# er007_ja_cost_latency_projection_01.pyと同一の実測公式価格・latency前提。
OPENAI_COST_PER_SECOND = 0.003 / 60
AZURE_COST_PER_SECOND = 1.0 / 3600
GEMINI_TTS_COST_PER_CHAR = 0.6 / 1_000_000  # gemini-3.1-flash-tts-preview概算(既存報告のBatch実費と同オーダー)
A2_JA_STATIC = {"japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4"}


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def collect_ja_segments_with_duration(topic_dir):
    found = []
    for level_dir, level_label in (("b1b", "B1"), ("a2", "A2")):
        path = f"er006_output/pool_pilot_01/{topic_dir}/{level_dir}/audit/tts_generation_results.json"
        data = load_json(path)
        if data is None:
            continue
        segs = data.get("segments", {})
        kps = data.get("key_phrases", {})
        if level_label == "B1":
            for rank, kp in kps.items():
                ja = kp.get("japanese")
                if ja and ja.get("canonical_text"):
                    found.append((level_label, f"kp{rank}_ja_charon", ja["canonical_text"],
                                  ja.get("asr_text"), ja.get("trim_info", {}).get("trimmed_duration_seconds")
                                  or ja.get("duration_seconds") or 5.0))
        else:
            for name, seg in segs.items():
                if name in A2_JA_STATIC:
                    c = seg.get("canonical_text")
                    if c:
                        found.append((level_label, name, c, seg.get("asr_text"), seg.get("duration_seconds") or 10.0))
            for rank, kp in kps.items():
                jm = kp.get("japanese_meaning")
                if jm and jm.get("canonical_text"):
                    found.append((level_label, f"meaning_{rank}", jm["canonical_text"],
                                  jm.get("asr_text"), jm.get("duration_seconds") or 5.0))
    return found


def old_classify_would_be_true_mismatch(canonical, asr_text):
    """ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B適用前の分類を再現する
    (entity_likeのみをCascade対象とし、phonetic_uncertainは存在しな
    かった)。javal.classify_ja_asr_matchの現在の出力から、Part B変更を
    revertした場合の分類を、content_diffsのentity_like/phonetic_uncertain
    フラグを見て逆算する(コード自体は変更しない、静的な逆算のみ)。"""
    cls = javal.classify_ja_asr_match(canonical, asr_text)
    if cls.classification != "ASR_VALIDATION_UNCERTAIN":
        return cls.classification == "TRUE_CONTENT_MISMATCH", cls
    diffs = cls.protected.content_diffs
    # Part B前は、phonetic_uncertainのみで構成されるcascade_eligibleは
    # 全てnon_entity_diffs(TRUE_CONTENT_MISMATCH)側に落ちていた。
    was_entity_like_only = bool(diffs) and all(d["entity_like"] for d in diffs)
    return (not was_entity_like_only), cls


def run():
    all_segments = []
    for topic_label, topic_dir in TOPIC_DIRS.items():
        segs = collect_ja_segments_with_duration(topic_dir)
        for level, name, canonical, asr_text, duration in segs:
            all_segments.append((topic_label, level, name, canonical, asr_text, duration))

    print(f"Total JA segments (実測ログ、既存asr_textを再利用): {len(all_segments)}")

    # --- 経路B: 漢字読み揺れ誤分類によるTTS retry対象segment数 ---
    part_b_affected = []
    for topic_label, level, name, canonical, asr_text, duration in all_segments:
        if asr_text is None or canonical == asr_text:
            continue
        was_true_mismatch_before, cls_now = old_classify_would_be_true_mismatch(canonical, asr_text)
        is_phonetic_uncertain_now = (cls_now.classification == "ASR_VALIDATION_UNCERTAIN"
                                      and any(d["phonetic_uncertain"] for d in cls_now.protected.content_diffs))
        if was_true_mismatch_before and is_phonetic_uncertain_now:
            part_b_affected.append((topic_label, level, name, cls_now, duration))

    print(f"\n=== 経路B(漢字読み揺れ誤分類)の影響 ===")
    print(f"旧分類ではTRUE_CONTENT_MISMATCH(即TTS retry対象)だったが、新分類では"
          f"ASR_VALIDATION_UNCERTAIN(Cascade対象、TTS retry対象外)になったsegment: "
          f"{len(part_b_affected)}/{len(all_segments)}")
    for topic_label, level, name, cls_now, duration in part_b_affected:
        print(f"  - {topic_label}/{level}/{name}: {cls_now.protected.content_diffs}")

    # --- avoidable TTS retry cost(経路B分のみ、実測ベース) ---
    # 1回のTTS retry = Gemini TTS 1回(文字数×単価)+ 検証ASR 1回(OpenAI,
    # duration×単価)。保守的に「誤分類1件につき平均1回分の無駄なTTS
    # retryが発生していた」と仮定する(実際は複数回attemptが同一誤分類を
    # 繰り返し得点でmax_attempts回に達するまで再試行されうるため、これは
    # 下限見積り)。
    b_avoidable_tts_calls = len(part_b_affected)
    b_avoidable_cost = 0.0
    b_avoidable_asr_cost = 0.0
    for topic_label, level, name, canonical, asr_text, duration in all_segments:
        matched = any(name == n and topic_label == t and level == l for t, l, n, *_ in part_b_affected)
        if not matched:
            continue
        b_avoidable_cost += len(canonical) * GEMINI_TTS_COST_PER_CHAR
        b_avoidable_asr_cost += duration * OPENAI_COST_PER_SECOND
    print(f"\n下限見積り(誤分類1件あたり平均1回の無駄なTTS+検証ASRが発生していたと仮定):")
    print(f"  回避可能だったTTS再生成回数: {b_avoidable_tts_calls}回")
    print(f"  回避可能だったTTS cost: ${b_avoidable_cost:.6f} (¥{b_avoidable_cost*160:.3f} @160円/$)")
    print(f"  回避可能だった検証ASR cost: ${b_avoidable_asr_cost:.6f} (¥{b_avoidable_asr_cost*160:.3f})")

    # --- 経路A: stop_retrying無視bugのworst-case見積り ---
    # 経路Aは「Cascadeがstop_retrying=Trueを返した後、voice01.py/n3_01.pyの
    # 自前ループがmax_attempts回まで無駄にTTS再生成を続ける」bugである。
    # このbugは今Sessionで新規配線されたCascade呼び出し自体に内在していた
    # ため、実運用ログにはまだ現れていない(Production配線直後に本タスクで
    # 発見・修正したため)。したがって実測ではなく、
    # 「Cascadeを尽くしてもHRに到達するsegmentがvoice01.py/n3_01.pyの
    # フォールバック経路を通った場合、bug由来で最大(max_attempts-1)回分の
    # 無駄なTTS+Cascade再試行が発生していた」というworst-case上限を示す。
    cascade_to_hr_count = 0
    for topic_label, level, name, canonical, asr_text, duration in all_segments:
        if asr_text is None or canonical == asr_text:
            continue
        cls = javal.classify_ja_asr_match(canonical, asr_text)
        is_cascade_eligible = (cls.classification == "ASR_VALIDATION_UNCERTAIN")
        if is_cascade_eligible:
            cascade_to_hr_count += 1

    max_attempts_default = 6
    a_worst_case_extra_tts = cascade_to_hr_count * (max_attempts_default - 1)
    a_worst_case_tts_cost = sum(
        len(canonical) * GEMINI_TTS_COST_PER_CHAR * (max_attempts_default - 1)
        for topic_label, level, name, canonical, asr_text, duration in all_segments
        if asr_text is not None and canonical != asr_text
        and javal.classify_ja_asr_match(canonical, asr_text).classification == "ASR_VALIDATION_UNCERTAIN"
    )
    a_worst_case_asr_cost = sum(
        duration * (OPENAI_COST_PER_SECOND * 2 + AZURE_COST_PER_SECOND * 2) * (max_attempts_default - 1)
        for topic_label, level, name, canonical, asr_text, duration in all_segments
        if asr_text is not None and canonical != asr_text
        and javal.classify_ja_asr_match(canonical, asr_text).classification == "ASR_VALIDATION_UNCERTAIN"
    )
    print(f"\n=== 経路A(stop_retrying無視bug)のworst-case見積り ===")
    print(f"(このbugは今Session中に新規配線されたCascade呼び出しに内在しており、"
          f"実運用ログにはまだ現れていない。Cascade対象[ASR_VALIDATION_UNCERTAIN]に"
          f"分類されるsegment数を土台に、max_attempts={max_attempts_default}回全てを"
          f"無駄に消費していたと仮定する上限見積り)")
    print(f"  Cascade対象(ASR_VALIDATION_UNCERTAIN)segment数: {cascade_to_hr_count}/{len(all_segments)}")
    print(f"  bug由来で無駄になり得た追加TTS再生成回数(上限): {a_worst_case_extra_tts}回")
    print(f"  bug由来で無駄になり得たTTS cost(上限): ${a_worst_case_tts_cost:.6f} "
          f"(¥{a_worst_case_tts_cost*160:.3f})")
    print(f"  bug由来で無駄になり得た追加検証ASR cost(上限): ${a_worst_case_asr_cost:.6f} "
          f"(¥{a_worst_case_asr_cost*160:.3f})")

    # --- 比較: 新規追加されたASRコスト(経路Bで新たにCascadeへ回る分) ---
    new_cascade_asr_cost = 0.0
    for topic_label, level, name, canonical, asr_text, duration in all_segments:
        matched = any(name == n and topic_label == t and level == l for t, l, n, *_ in part_b_affected)
        if matched:
            # worst-case: Primary#2 + Secondary#1 + Secondary#2の3回追加ASR
            new_cascade_asr_cost += duration * (OPENAI_COST_PER_SECOND + AZURE_COST_PER_SECOND * 2)

    print(f"\n=== 経路B修正による新規追加ASRコスト(Cascade起動分、worst-case) ===")
    print(f"  新たにCascadeへ回るsegment{len(part_b_affected)}件分の追加ASR cost(上限): "
          f"${new_cascade_asr_cost:.6f} (¥{new_cascade_asr_cost*160:.3f})")
    print(f"  → 回避したTTS+検証ASR cost(¥{(b_avoidable_cost+b_avoidable_asr_cost)*160:.3f})との比較: "
          f"{'節約(新規ASRコストより回避コストの方が大きい)' if (b_avoidable_cost+b_avoidable_asr_cost) > new_cascade_asr_cost else '純増(新規ASRコストの方が大きい)'}")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/ja_tts_retry_path_fix_cost.json", "w",
              encoding="utf-8") as f:
        json.dump({
            "n_segments": len(all_segments),
            "part_b_affected_count": len(part_b_affected),
            "part_b_affected_segments": [f"{t}/{l}/{n}" for t, l, n, *_ in part_b_affected],
            "part_b_avoidable_tts_cost_usd": b_avoidable_cost,
            "part_b_avoidable_asr_cost_usd": b_avoidable_asr_cost,
            "part_a_cascade_eligible_count": cascade_to_hr_count,
            "part_a_worst_case_extra_tts_calls": a_worst_case_extra_tts,
            "part_a_worst_case_tts_cost_usd": a_worst_case_tts_cost,
            "part_a_worst_case_asr_cost_usd": a_worst_case_asr_cost,
            "new_cascade_asr_cost_usd_worst_case": new_cascade_asr_cost,
        }, f, ensure_ascii=False, indent=2)
    print("\nJA_TTS_RETRY_PATH_FIX_COST_DONE")


if __name__ == "__main__":
    run()
