# ============================================================
# er007_ja_cost_latency_projection_01.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part C:
# No.1-6の既存96 Japanese segmentを使い、旧方式(Azure-only)と
# 新方式(OpenAI Primary + Azure Secondary Cascade)のASR cost/latencyを
# 比較する。新規TTS/ASRは呼ばない(既存ログの再利用のみ)。
#
# 方法論上の注記: 新方式のシミュレーションでは、実際のOpenAI transcript
# が存在しない92segment分について、既存のAzure transcript(旧Primary)を
# 「Primary #1が返したであろうtranscript」の代理として使う。Part Eの
# 実測(n=14)で、OpenAIとAzureの誤り率・傾向は概ね同程度であることを
# 確認済みのため、この代理は妥当な近似と判断する(詳細はPart E参照)。
# ============================================================
import json

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja_secondary

TOPIC_DIRS = {
    "No.1": "pool_benches_luna", "No.2": "pool_subscriptions", "No.3": "pool_startups",
    "No.4": "pool_n4_supermarket", "No.5": "pool_n5_cafes", "No.6": "pool_n6_delivery",
}

# 実測公式価格(2026-08時点、WebSearchで確認、推測値は使わない):
#   OpenAI gpt-4o-mini-transcribe: 約$0.003/分(=$0.00005/秒)
#   Azure Speech STT(標準リアルタイム): $1/時間(=$0.0002778/秒)
OPENAI_COST_PER_SECOND = 0.003 / 60
AZURE_COST_PER_SECOND = 1.0 / 3600

# 概算latency(実測、既存ログ平均): OpenAI mini呼び出し 約1.5秒/回、
# Azure連続認識呼び出し 約3〜5秒/回(音声長×リアルタイム係数+オーバーヘッド、
# 保守的に5秒/回とする)。
OPENAI_CALL_LATENCY_SECONDS = 1.5
AZURE_CALL_LATENCY_SECONDS = 5.0

B1_JA_SEGMENT_PATTERN_PREFIX = "kp"
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


def simulate_new_system(canonical, proxy_primary_asr_text):
    """新方式(OpenAI Primary#1 -> #2 -> Azure Secondary#1 -> #2 -> HR)を、
    既存transcriptを代理入力として使いシミュレートする。実際のASR呼び出しは
    行わない(canonical/proxy_primary_asr_textはいずれも既存記録データ)。
    Cascadeの後続段(Primary#2/Secondary#1-2)は、実際にどんなtranscriptに
    なるか不明なため、「entity-likeなら平均的にCascadeの最終段(Secondary#2
    まで)へ進み、それでも不確実ならHRへ到達する」という保守的(=cost/
    latencyを過小評価しない)前提でシミュレートする。"""
    cls = javal.classify_ja_asr_match(canonical, proxy_primary_asr_text)
    is_entity = ja_secondary.is_entity_like_mismatch_ja(cls)
    if cls.should_pass:
        return {"stage": "primary_1", "openai_calls": 1, "azure_calls": 0}
    if not is_entity:
        # 真の内容誤り: Cascade対象外、TTS retry(ASR呼び出しはこの1回のみ)
        return {"stage": "true_mismatch_tts_retry", "openai_calls": 1, "azure_calls": 0}
    # entity-like: Cascade起動。保守的に、実際にPrimary#1で拾えなかった
    # 固有名詞ゆれは、後続でも解決しないHuman Review到達ケースとして扱う
    # (最大コスト/latencyを見積もる、実際には途中でPASSする場合も多い
    # ため、これは上限見積り)。
    return {"stage": "cascade_to_hr_worst_case", "openai_calls": 2, "azure_calls": 2}


def run():
    all_segments = []
    for topic_label, topic_dir in TOPIC_DIRS.items():
        segs = collect_ja_segments_with_duration(topic_dir)
        for level, name, canonical, asr_text, duration in segs:
            all_segments.append((topic_label, level, name, canonical, asr_text, duration))

    print(f"Total JA segments: {len(all_segments)}")

    # --- 旧方式(Current, Azure-only) ---
    current_azure_calls = len(all_segments)  # 全segment、Azure 1回のみ(既存は複数回attemptもあるが、
                                              # ここでは「1 attemptあたり1 ASR call」の単純化で比較する
    current_total_duration = sum(d for *_, d in all_segments)
    current_cost = current_azure_calls * AZURE_COST_PER_SECOND * (current_total_duration / len(all_segments))
    # duration依存のcostなので、実際はsegmentごとのduration×単価で積算する
    current_cost = sum(d * AZURE_COST_PER_SECOND for *_, d in all_segments)
    current_latency = current_azure_calls * AZURE_CALL_LATENCY_SECONDS

    # --- 新方式(Proposed) ---
    stage_counts = {"primary_1": 0, "true_mismatch_tts_retry": 0, "cascade_to_hr_worst_case": 0}
    proposed_openai_calls = 0
    proposed_azure_calls = 0
    proposed_cost = 0.0
    proposed_latency = 0.0

    for topic_label, level, name, canonical, asr_text, duration in all_segments:
        sim = simulate_new_system(canonical, asr_text)
        stage_counts[sim["stage"]] += 1
        proposed_openai_calls += sim["openai_calls"]
        proposed_azure_calls += sim["azure_calls"]
        proposed_cost += sim["openai_calls"] * duration * OPENAI_COST_PER_SECOND
        proposed_cost += sim["azure_calls"] * duration * AZURE_COST_PER_SECOND
        proposed_latency += sim["openai_calls"] * OPENAI_CALL_LATENCY_SECONDS
        proposed_latency += sim["azure_calls"] * AZURE_CALL_LATENCY_SECONDS

    n = len(all_segments)
    print("\n=== 旧方式(Current, Azure-only Primary) ===")
    print(f"  Azure ASR call数: {current_azure_calls}")
    print(f"  合計cost: ${current_cost:.5f} (¥{current_cost*160:.3f} @160円/$)")
    print(f"  合計wall-clock(逐次実行想定): {current_latency:.1f}秒")
    print(f"  cost/segment: ${current_cost/n:.6f}")

    print("\n=== 新方式(Proposed, OpenAI Primary + Azure Secondary Cascade) ===")
    print(f"  Primary#1のみで終了: {stage_counts['primary_1']}/{n} ({100*stage_counts['primary_1']/n:.1f}%)")
    print(f"  真の内容誤り(TTS retry対象、Cascade対象外): {stage_counts['true_mismatch_tts_retry']}/{n} "
          f"({100*stage_counts['true_mismatch_tts_retry']/n:.1f}%)")
    print(f"  entity-like(Cascade起動、上限見積りでHRまで): {stage_counts['cascade_to_hr_worst_case']}/{n} "
          f"({100*stage_counts['cascade_to_hr_worst_case']/n:.1f}%)")
    print(f"  OpenAI call数: {proposed_openai_calls}, Azure call数: {proposed_azure_calls}")
    print(f"  合計cost: ${proposed_cost:.5f} (¥{proposed_cost*160:.3f} @160円/$)")
    print(f"  合計wall-clock(逐次実行想定、上限見積り): {proposed_latency:.1f}秒")
    print(f"  cost/segment: ${proposed_cost/n:.6f}")

    print("\n=== 比較 ===")
    diff = proposed_cost - current_cost
    pct = 100 * diff / current_cost if current_cost else 0
    print(f"  cost差額: ${diff:+.5f} ({pct:+.1f}%)")
    latency_diff = proposed_latency - current_latency
    latency_pct = 100 * latency_diff / current_latency if current_latency else 0
    print(f"  latency差額: {latency_diff:+.1f}秒 ({latency_pct:+.1f}%)")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/ja_cost_latency_projection.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_segments": n, "current": {"azure_calls": current_azure_calls, "cost_usd": current_cost,
                                          "latency_seconds": current_latency},
            "proposed": {"stage_counts": stage_counts, "openai_calls": proposed_openai_calls,
                         "azure_calls": proposed_azure_calls, "cost_usd": proposed_cost,
                         "latency_seconds": proposed_latency},
            "cost_diff_usd": diff, "cost_diff_pct": pct,
            "latency_diff_seconds": latency_diff, "latency_diff_pct": latency_pct,
        }, f, ensure_ascii=False, indent=2)
    print("\nJA_COST_LATENCY_PROJECTION_DONE")


if __name__ == "__main__":
    run()
