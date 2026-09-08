# ============================================================
# er012_editorial_b_voices_comment1_contract_finalize_11.py
# EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11
# ============================================================
# Lane: Lane B / Voices-Perspective。種別: Comment 1 Contract確定版検証
# (2026-09-08、ユーザー決定反映)。
#
# 背景: ユーザーがVoices Comment Contract全体(Comment 1〜4)を採用
# (APPROVED_FOR_PRODUCTION、Comment 1はTRIAL-10修正版がベース)。あわせて
# "the question"漏出対策として、Comment 1 Contractの禁止事項リストへ
# 1行追加することをユーザー決定(このファイルでは追加せず、追加自体は
# er012_editorial_b_voices_trial_10_comment1.py::VOICES_COMMENT_1_ROLE_TRIAL10
# 側で実施済み。本ファイルはimportして読むのみ)。
#
# ただしB-Family(Voices)のProduction正式経路は未設計のため、本ファイルは
# Production wiringを一切行わない(Lane B側Trial定義ファイルの中で確定版
# Contractを保持・検証するだけ)。
#
# 設計方針: Trial-09/10と同じ記事(Trial-07由来、読み取り専用)・同じ
# Writer primitive(er003_v1_b1_scaffold_01_generate.run_support_text)・
# 同じTTS primitive(er003_v1_sing01_voice01_generate.generate_charon_english、
# 同一style_prefix・disfluency_qa=True)を使う。Trial-09/10の既存出力
# ファイル(er012_output/editorial_b_voices_trial_09_audio/、
# er012_output/editorial_b_voices_trial_10_comment1/配下)は一切書き換え
# ない(読み取りのみ)。出力は新規ディレクトリ
# er012_output/editorial_b_voices_comment1_contract_finalize_11/ のみへ。
#
# 触れないもの: Production Prompt本体、SSOT(CURRENT_SPEC.md/DECISION_LOG.md/
# OPEN_ITEMS.md)、docs/pm/ACTIVE_TASK.md/RESULT_PACKET.md、er011_output/、
# Trial-09/10の既存出力ファイル。Git操作はこのタスクでは行わない。
#
# n=3のComment 1テキスト生成(TTSなし、機械チェック付き) + 最良1本のみ
# Standard同期TTS + ASR Gate(費用上限¥50、全体上限¥100)。
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_editorial_b_voices_trial_09_audio as t9  # 読み取り専用(article/sections/定数の再利用のみ)
import er012_editorial_b_voices_trial_10_comment1 as t10  # 読み取り専用(確定版Contract定義の再利用のみ、無変更)
import er012_editorial_b_voices_trial_10_comment1_reproducibility as t10_repro  # 読み取り専用(check_text機械チェックの再利用のみ)

TRIAL07_ARTICLE_PATH = t9.TRIAL07_ARTICLE_PATH  # Trial-07/09/10と同一記事(再生成しない)

OUT_DIR = "er012_output/editorial_b_voices_comment1_contract_finalize_11"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP_TOTAL = 100.0  # 全体上限(委任範囲全体の安全装置)
TTS_STEP_BUDGET_JPY_CAP = 50.0  # 作業指示3項: TTS+ASR Gate単体の費用上限

N_RUNS = 3


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# コスト計測(Trial-09/10と同一ロジック、finalize-11専用ログへ適用)
# ============================================================
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far() -> tuple:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note: str = "") -> float:
    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[FINALIZE11][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP_TOTAL:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP_TOTAL} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 2: 確定版Contract(禁止句1行追加済み)でn=3生成 + 機械チェック
# ============================================================
def run_n3_generation() -> list:
    with open(TRIAL07_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    sections = t9.split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(Trial-07/09/10と同じ記事のはずが解析できません)")

    client = b1s.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"

    runs = []
    for i in range(N_RUNS):
        run_label = f"run{i + 1}"
        print(f"[FINALIZE11] Comment 1(確定版Contract)生成 {run_label}...")
        c1 = b1s.run_support_text(client, t10.VOICES_COMMENT_1_ROLE_TRIAL10, c1_context, model=model)
        text = c1.get("text")
        check = t10_repro.check_text(text) if text else {
            "text": text, "i_listening_focus_marker_present": False,
            "ii_looks_like_summary_or_verdict": True, "iii_structure_label_leak": ["<empty_generation>"],
        }
        check["run_label"] = run_label
        record = {
            "run_label": run_label,
            "generation": c1,
            "text": text,
            "context": c1_context,
            "role_prompt_source": "er012_editorial_b_voices_trial_10_comment1.VOICES_COMMENT_1_ROLE_TRIAL10 "
                                   "(確定版、禁止事項1行追加済み、本ファイルではimportして読むのみ・無変更)",
            "model": model,
            "check": check,
        }
        runs.append(record)
        assert_budget_ok(f"after {run_label} scaffold generation")

    save_json(f"{OUT_DIR}/audit/n3_generation.json", {
        "role_prompt_full_text": t10.VOICES_COMMENT_1_ROLE_TRIAL10,
        "context": c1_context,
        "runs": runs,
    })
    return runs


def select_best_run(runs: list) -> dict:
    """3本のうち(i)聞き方案内型かつ(ii)要約/評価なしかつ(iii)構造ラベル
    漏出なしを全て満たす最初のrunを選ぶ(全て満たすものが複数ある場合は
    run1優先)。全て満たすものがなければ、iii(構造ラベル漏出)がない中で
    iを満たすものを優先する。最終選定理由はaudit JSONへ記録し、Fable/
    ユーザーが別の1本を選び直せるよう3本ともreportへ列挙する。"""
    def score(r):
        c = r["check"]
        ok_i = c["i_listening_focus_marker_present"]
        ok_ii = not c["ii_looks_like_summary_or_verdict"]
        ok_iii = not c["iii_structure_label_leak"]
        return (ok_i and ok_ii and ok_iii, ok_i, ok_iii)

    best = max(runs, key=score)
    return best


# ============================================================
# Step 3: 最良1本のみStandard同期TTS + ASR Gate(費用上限¥50)
# ============================================================
def run_best_tts(best_run: dict) -> dict:
    new_text = best_run["text"]
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    out_path = f"{narration_dir}/comment_1_{best_run['run_label']}.wav"

    jpy_before, _ = compute_cost_jpy_so_far()
    print(f"[FINALIZE11] 最良1本({best_run['run_label']})のみTTS(Charon、"
          f"Trial-09/10と同一Production primitive)...")
    with cl.segment_context(f"comment_1_finalize11_{best_run['run_label']}"):
        r = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(new_text)), out_path,
            style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
    r["canonical_text"] = new_text
    r["selected_run_label"] = best_run["run_label"]
    save_json(f"{OUT_DIR}/audit/comment1_tts_result.json", r)

    jpy_after, by_provider_after = compute_cost_jpy_so_far()
    tts_step_cost = jpy_after - jpy_before
    print(f"[FINALIZE11] TTS+ASR step cost = {tts_step_cost:.2f} JPY (cap {TTS_STEP_BUDGET_JPY_CAP} JPY)")
    if tts_step_cost > TTS_STEP_BUDGET_JPY_CAP:
        print(f"[FINALIZE11][WARNING] TTS step cost {tts_step_cost:.2f} JPY exceeded step cap "
              f"{TTS_STEP_BUDGET_JPY_CAP} JPY (already executed; reporting as-is, no further TTS calls will run).")
    assert_budget_ok("after best-run TTS + ASR Gate")
    print(f"[FINALIZE11] TTS status={r.get('status')} asr_verified={r.get('asr_verified')} "
          f"asr_text={r.get('asr_text')!r}")
    return r, tts_step_cost


def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(COST_LOG_PATH)

    runs = run_n3_generation()
    best_run = select_best_run(runs)
    print(f"[FINALIZE11] 選定: {best_run['run_label']} "
          f"(全条件i/ii/iii充足={all([best_run['check']['i_listening_focus_marker_present'], not best_run['check']['ii_looks_like_summary_or_verdict'], not best_run['check']['iii_structure_label_leak']])})")

    tts_result, tts_step_cost = run_best_tts(best_run)

    jpy, by_provider = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/audit/run_summary.json", {
        "runs": [{"run_label": r["run_label"], "text": r["text"], "check": r["check"]} for r in runs],
        "selected_run_label": best_run["run_label"],
        "tts_status": tts_result.get("status"),
        "asr_verified": tts_result.get("asr_verified"),
        "asr_text": tts_result.get("asr_text"),
        "tts_step_cost_jpy": round(tts_step_cost, 4),
        "total_cost_jpy": round(jpy, 4),
        "by_provider": by_provider,
    })
    print(f"[FINALIZE11] 完了。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
