# ============================================================
# er012_editorial_b_voices_trial_10_comment1_reproducibility.py
# EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10
# (Fable修正指示1回目: EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10
#  への追加委任、管理ID同一)
# ============================================================
# 目的: TRIAL-10で定義済みのComment 1 Contract
# (er012_editorial_b_voices_trial_10_comment1.VOICES_COMMENT_1_ROLE_TRIAL10)を
# 一切変更せず、同一入力(Trial-07記事のThe Question本文、Trial-09/10と同一)に
# 対してテキスト生成のみをさらに2回実行し(TRIAL-10本体のn=1と合わせて合計n=3)、
# Contractの再現性を確認する。
#
# TTSは実行しない(LLMコストのみ、テキスト生成2回分)。
# TRIAL-10本体のスクリプト・出力(audit/comment1_regeneration.json 等)・
# narration/は一切書き換えない。出力は新規サブディレクトリ
# er012_output/editorial_b_voices_trial_10_comment1/reproducibility/ のみへ。
#
# 触れないもの: Contract本体(VOICES_COMMENT_1_ROLE_TRIAL10の定義箇所)、
# Production コード、SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md)、
# Trial-09出力、TRIAL-10本体の既存出力ファイル。Git操作はこのタスクでは
# 行わない。
#
# cost > 100円でSTOP。
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_b1_scaffold_01_generate as b1s
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_editorial_b_voices_trial_09_audio as t9  # 読み取り専用(article/sections再利用のみ)
import er012_editorial_b_voices_trial_10_comment1 as t10  # 読み取り専用(Contract定義の再利用のみ、無変更)

OUT_DIR = "er012_output/editorial_b_voices_trial_10_comment1/reproducibility"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 100.0

N_ADDITIONAL_RUNS = 2  # TRIAL-10本体のn=1と合わせて合計n=3


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


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
    print(f"[TRIAL10-COMMENT1-REPRO][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# 機械的チェック(Fable指示の(i)(ii)(iii))
# ============================================================
LISTENING_FOCUS_MARKERS = ["listen for", "as you listen", "notice how", "notice what", "notice ", "pay attention"]
STRUCTURE_LABELS = ["the question", "part 1", "part 2", "hook", "voice a", "voice b", "one voice", "another voice",
                    "comment 1", "comment 2", "comment 3", "comment 4", "tension", "preview", "key phrase"]


def check_text(text: str) -> dict:
    lower = text.lower()
    has_listening_marker = any(m in lower for m in LISTENING_FOCUS_MARKERS)
    leaked_labels = [lbl for lbl in STRUCTURE_LABELS if lbl in lower]
    return {
        "text": text,
        "i_listening_focus_marker_present": has_listening_marker,
        "ii_looks_like_summary_or_verdict": not has_listening_marker,  # 機械的proxy(注記: 人手確認を推奨)
        "iii_structure_label_leak": leaked_labels,
    }


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    with open(t10.TRIAL07_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    sections = t9.split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(Trial-09/10と同じ記事のはずが解析できません)")

    client = b1s.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"

    runs = []
    for i in range(N_ADDITIONAL_RUNS):
        run_label = f"run{i + 2}"  # TRIAL-10本体の生成をrun1とみなし、run2/run3として記録
        print(f"[TRIAL10-COMMENT1-REPRO] Comment 1 再生成({run_label})...")
        c1 = b1s.run_support_text(client, t10.VOICES_COMMENT_1_ROLE_TRIAL10, c1_context, model=model)
        record = {
            "run_label": run_label,
            "generation": c1,
            "text": c1.get("text"),
            "context": c1_context,
            "role_prompt_source": "er012_editorial_b_voices_trial_10_comment1.VOICES_COMMENT_1_ROLE_TRIAL10 (unchanged, imported only)",
            "model": model,
        }
        runs.append(record)
        assert_budget_ok(f"after {run_label} scaffold regen")

    run1_text = load_json(
        "er012_output/editorial_b_voices_trial_10_comment1/audit/comment1_regeneration.json"
    )["new_text"]
    run1_check = check_text(run1_text)
    run1_check["run_label"] = "run1 (TRIAL-10本体、TTS+ASR PASS済み)"
    checks = [run1_check] + [
        {**check_text(r["text"]), "run_label": r["run_label"]} for r in runs if r.get("text")
    ]

    save_json(f"{OUT_DIR}/reproducibility_runs.json", {
        "note": "TRIAL-10本体run1 (n=1, VALIDATED, TTS+ASR PASS済み)に加え、"
                "同一Contract・同一入力でrun2/run3をテキストのみ追加生成(TTSなし)。"
                "合計n=3で再現性確認。",
        "run1_trial10_body_text": run1_text,
        "additional_runs": runs,
        "checks": checks,
    })

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL10-COMMENT1-REPRO] 完了(テキストのみ、TTS未実行)。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
