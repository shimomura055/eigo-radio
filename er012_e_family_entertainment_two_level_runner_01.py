# ============================================================
# er012_e_family_entertainment_two_level_runner_01.py
# NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01
# ============================================================
# Production正式runner(delegation D1)。入力=日本語完成Entertainment R2
# 記事ファイル(path+sha256を記録、由来管理IDは呼び出し側が--source-idで
# 明示)。日本語記事の自動生成(Original→R1→R2)自体の配線は本タスク範囲外
# (CURRENT_SPEC.md行828 WIRING INCOMPLETE)。本runnerは「完成JA記事を
# 受け取る」入口として、以下を実行する:
#   1. Verified Fact Ledger(既存reuse、または既存Researcher/Verification
#      [web_search]による新規構築、delegation D5)
#   2. Advanced(Natural English Adaptation、CEFR B1、delegation D2、
#      `er003_v1_n3_01_advanced_adaptation_generate.py`)
#   3. Standard(CEFR A2、v5 6,000語ライン、delegation D3、
#      `er003_v1_n3_01_standard_a2_generate.py`)
#   4. 各段でVerified Fact Ledgerに対するdeviation check(既存
#      `vfl01.run_deviation_check`、delegation D5。MAJORの場合は1回だけ
#      再生成しても解消しない場合はSTOP、本文を手で直さない)
#   5. downstream(delegation D7): 既存`er003_v1_n3_01_scaffold_
#      generate.py`(Preview/Comment 1-4、Key Phrase選定)・
#      `er003_v1_n3_01_tts_generate.py`(TTS)・`er003_v1_n3_01_assemble.py`
#      (Assembly、Audio Validation Gate)を関数importで再利用(無改変)。
#      Advanced=B1製品、Standard=A2製品として、既存のA2/B1レベル別出力
#      規約(`{out_dir}/b1b/`・`{out_dir}/a2/`)にそのまま載せる。
#   6. player.html生成(既存`audio_review_player`共有ヘルパーを再利用、
#      本runner専用の新規レイアウト関数)。
#
# 実行方法:
#   .venv/Scripts/python.exe er012_e_family_entertainment_two_level_runner_01.py \
#       --ja-article <path> --slug <sewer|meta> --out-dir <dir> \
#       [--ledger-file <既存Ledger再利用path>] [--source-id <管理ID>] \
#       [--budget-jpy 300] [--stage ledger|writer|scaffold|tts|assemble|player|all] \
#       [--regenerate-stage advanced|standard] \
#       [--tts-mode STANDARD|BATCH(既定STANDARD)] [--batch-reason "<PM_GOVERNANCE 7-2の理由>"]
#
# TTS実行方式(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01、2026-09-25):
# 既定は--tts-mode STANDARD(TTS_EXECUTION_MODE=STANDARD、PM_GOVERNANCE.md
# 7-1「正式リリース前は原則Standard同期」)。--tts-mode BATCHを使う場合は
# --batch-reasonでPM_GOVERNANCE.md 7-2の例外条件(1〜4)に該当する理由を
# 明示すること(未指定時はエラーで停止)。低レベル実装
# `er006_batch_tts_wiring_01.DEFAULT_TTS_EXECUTION_MODE`(=BATCH、量産
# Production既定)には依存しない。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time

import audio_review_player as player_common
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_standard_a2_generate as std_gen
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    return sha256_text(load_text(path))


# ------------------------------------------------------------
# コスト計測(er012_b_family_production_runner_01.pyと同一ロジック、
# 本runner専用ログへ適用する独立実装)
# ------------------------------------------------------------
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far(cost_log_path: str) -> tuple:
    if not os.path.exists(cost_log_path):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(cost_log_path, encoding="utf-8") as f:
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


def assert_budget_ok(out_dir: str, budget_jpy: float, note: str = "") -> float:
    cost_log_path = f"{out_dir}/raw_usage_log.jsonl"
    jpy, by_provider = compute_cost_jpy_so_far(cost_log_path)
    print(f"[E-FAMILY-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > budget_jpy:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {budget_jpy} JPY. Stopping ({note}).")
    return jpy


# ------------------------------------------------------------
# Verified Fact Ledger構築(delegation D5、既存Researcher/Verification
# [web_search]を、topic引数を明示できる形で再現する。
# NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase Bの
# run_researcher_for_topic/run_verification_for_topicと同一の呼び出し
# 構造[model/reasoning/tools/text.format/developer+user message]を、
# Trial scriptをimportせず本runner内に独立実装する)
# ------------------------------------------------------------
def run_researcher_for_topic(client, topic: str) -> dict:
    import er002_ja_web_research_r3 as r3

    prompt = vfl01.build_researcher_prompt(topic=topic)
    t0 = time.time()
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    latency = time.time() - t0
    search_usage = r3.extract_web_search_usage(response)
    parsed = json.loads(response.output_text)
    return {"prompt": prompt, "raw_text": response.output_text, "parsed": parsed,
            "model": response.model, "response_id": response.id,
            "search_usage": search_usage, "latency_seconds": latency}


def run_verification_for_topic(client, topic: str, ledger_parsed: dict) -> dict:
    import er002_ja_web_research_r3 as r3

    prompt = vfl01.build_verification_prompt(topic, ledger_parsed)
    t0 = time.time()
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    latency = time.time() - t0
    search_usage = r3.extract_web_search_usage(response)
    parsed = json.loads(response.output_text)
    return {"prompt": prompt, "raw_text": response.output_text, "parsed": parsed,
            "model": response.model, "response_id": response.id,
            "search_usage": search_usage, "latency_seconds": latency}


def build_ledger_for_topic(client, topic: str, ledger_dir: str) -> str:
    os.makedirs(f"{ledger_dir}/audit", exist_ok=True)
    print(f"[E-FAMILY-RUNNER][ledger] Researcher呼び出し開始(topic={topic[:40]!r}...)...")
    research = run_researcher_for_topic(client, topic)
    print(f"[E-FAMILY-RUNNER][ledger] facts={len(research['parsed']['facts'])} "
          f"web_search_calls={research['search_usage']['web_search_call_count']}")
    save_json(f"{ledger_dir}/fact_ledger_draft.json", research["parsed"])
    save_json(f"{ledger_dir}/audit/researcher_full_record.json",
              {k: v for k, v in research.items() if k != "parsed"})

    print("[E-FAMILY-RUNNER][ledger] Verification呼び出し開始...")
    verification = run_verification_for_topic(client, topic, research["parsed"])
    save_json(f"{ledger_dir}/fact_ledger_verification.json", verification["parsed"])
    save_json(f"{ledger_dir}/audit/verification_full_record.json",
              {k: v for k, v in verification.items() if k != "parsed"})

    ledger_text, verdict_counts, kept_facts = vfl01.build_verified_ledger_text(
        research["parsed"], verification["parsed"])
    save_text(f"{ledger_dir}/verified_fact_ledger.txt", ledger_text)
    save_json(f"{ledger_dir}/verdict_counts.json", verdict_counts)
    print(f"[E-FAMILY-RUNNER][ledger] Ledger確定。verdict_counts={verdict_counts} "
          f"kept_facts={len(kept_facts)}")
    return ledger_text


def load_or_build_ledger(client, out_dir: str, topic: str, reuse_ledger_file: str | None) -> str:
    ledger_dir = f"{out_dir}/ledger"
    dest_path = f"{ledger_dir}/verified_fact_ledger.txt"
    if os.path.exists(dest_path):
        print(f"[E-FAMILY-RUNNER][ledger] 既存Ledgerを再利用(既生成済み): {dest_path}")
        return load_text(dest_path)
    if reuse_ledger_file:
        os.makedirs(ledger_dir, exist_ok=True)
        text = load_text(reuse_ledger_file)
        shutil.copyfile(reuse_ledger_file, dest_path)
        save_json(f"{ledger_dir}/reuse_source.json",
                  {"reused_from": reuse_ledger_file, "sha256": sha256_text(text)})
        print(f"[E-FAMILY-RUNNER][ledger] 既存Ledgerを再利用(コピー): {reuse_ledger_file}")
        return text
    return build_ledger_for_topic(client, topic, ledger_dir)


# ------------------------------------------------------------
# Writer stage(delegation D2/D3/D4/D5/D6)
# ------------------------------------------------------------
def _extract_title(article_text: str) -> str:
    for line in article_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def run_writer_stage(client, theme: dict, ja_text: str, ledger_text: str,
                      budget_jpy: float, only: str | None = None) -> dict:
    """only: None(両方)/"advanced"/"standard"(delegation D4の
    --regenerate-stage相当。同じ生成関数をそのまま再呼び出しする)。"""
    out_dir = theme["out_dir"]
    b1b_dir = f"{out_dir}/b1b"
    a2_dir = f"{out_dir}/a2"
    os.makedirs(f"{b1b_dir}/audit", exist_ok=True)
    os.makedirs(f"{a2_dir}/audit", exist_ok=True)
    evidence = {}

    if only in (None, "advanced"):
        print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Advanced(Natural English Adaptation)生成開始...")
        adv_result = adv_gen.generate_advanced_adaptation(ja_text, client=client)
        advanced_text = adv_result.text
        print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Advanced deviation check開始...")
        deviation = vfl01.run_deviation_check(client, ledger_text, advanced_text, hook_aware=False)
        dev_status = deviation["parsed"].get("overall_status")
        retried_for_deviation = False
        if dev_status == "LEDGER_DEVIATION":
            print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Advanced deviation MAJOR。1回だけ再生成します...")
            adv_result = adv_gen.generate_advanced_adaptation(ja_text, client=client)
            advanced_text = adv_result.text
            deviation = vfl01.run_deviation_check(client, ledger_text, advanced_text, hook_aware=False)
            dev_status = deviation["parsed"].get("overall_status")
            retried_for_deviation = True
            if dev_status == "LEDGER_DEVIATION":
                save_json(f"{b1b_dir}/audit/deviation_check.json", deviation["parsed"])
                # STOPでも未採用の生成text自体は監査証跡として保存する(本文としては
                # 採用しない、article.mdとは別名で保存)。
                save_text(f"{b1b_dir}/audit/rejected_advanced_attempt2.md", advanced_text)
                raise RuntimeError(
                    f"[STOP] Advanced deviation check: 再生成後もMAJOR"
                    f"(retry_for_deviation={retried_for_deviation})。本文を手で直さずSTOPします。"
                )
        save_text(f"{b1b_dir}/article.md", advanced_text)
        save_json(f"{b1b_dir}/parts.json", sc.split_article_text(advanced_text))
        save_json(f"{b1b_dir}/audit/deviation_check.json", deviation["parsed"])
        evidence["advanced"] = {
            "process_label": adv_gen.PROCESS_LABEL,
            "model_id_requested": adv_result.model_id_requested,
            "model_id_actual": adv_result.model_id_actual,
            "fallback_detected": adv_result.fallback_detected,
            "response_id": adv_result.response_id,
            "structure_status": adv_result.structure_status,
            "attempts": adv_result.attempts,
            "retried": adv_result.retried,
            "retried_for_deviation": retried_for_deviation,
            "deviation_overall_status": dev_status,
            "usage": adv_result.usage,
            "cost_usd": adv_result.cost_usd,
            "cost_jpy": adv_result.cost_jpy,
            "elapsed_seconds": adv_result.elapsed_seconds,
            "title": _extract_title(advanced_text),
        }
        assert_budget_ok(out_dir, budget_jpy, "after advanced writer+deviation")

    if only in (None, "standard"):
        if only == "standard":
            advanced_text = load_text(f"{b1b_dir}/article.md")
        print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Standard(A2 v5)生成開始...")
        std_result = std_gen.generate_standard_a2(advanced_text, client=client)
        standard_text = std_result.text
        print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Standard deviation check開始...")
        deviation = vfl01.run_deviation_check(client, ledger_text, standard_text, hook_aware=False)
        dev_status = deviation["parsed"].get("overall_status")
        retried_for_deviation = False
        if dev_status == "LEDGER_DEVIATION":
            print(f"[E-FAMILY-RUNNER][writer/{theme['theme_id']}] Standard deviation MAJOR。1回だけ再生成します...")
            std_result = std_gen.generate_standard_a2(advanced_text, client=client)
            standard_text = std_result.text
            deviation = vfl01.run_deviation_check(client, ledger_text, standard_text, hook_aware=False)
            dev_status = deviation["parsed"].get("overall_status")
            retried_for_deviation = True
            if dev_status == "LEDGER_DEVIATION":
                save_json(f"{a2_dir}/audit/deviation_check.json", deviation["parsed"])
                raise RuntimeError(
                    f"[STOP] Standard deviation check: 再生成後もMAJOR"
                    f"(retry_for_deviation={retried_for_deviation})。本文を手で直さずSTOPします。"
                )
        save_text(f"{a2_dir}/article.md", standard_text)
        save_json(f"{a2_dir}/parts.json", sc.split_article_text(standard_text))
        save_json(f"{a2_dir}/audit/deviation_check.json", deviation["parsed"])
        evidence["standard"] = {
            "process_label": std_gen.PROCESS_LABEL,
            "model_id_requested": std_result.model_id_requested,
            "model_id_actual": std_result.model_id_actual,
            "fallback_detected": std_result.fallback_detected,
            "response_id": std_result.response_id,
            "structure_status": std_result.structure_status,
            "attempts": std_result.attempts,
            "retried": std_result.retried,
            "retried_for_deviation": retried_for_deviation,
            "deviation_overall_status": dev_status,
            "usage": std_result.usage,
            "cost_usd": std_result.cost_usd,
            "cost_jpy": std_result.cost_jpy,
            "elapsed_seconds": std_result.elapsed_seconds,
            "checks": std_result.checks,
            "title": _extract_title(standard_text),
        }
        assert_budget_ok(out_dir, budget_jpy, "after standard writer+deviation")

    save_json(f"{out_dir}/writer_run_summary.json", evidence)
    return evidence


# ------------------------------------------------------------
# downstream(delegation D7): 既存A-Family(n3)関数の再利用のみ
# ------------------------------------------------------------
def run_scaffold_stage(client, theme: dict) -> dict:
    return sc.run_theme_scaffold(client, theme)


def run_tts_stage(theme: dict, japanese_title: str) -> dict:
    # generate_a2_segments()はJAPANESE_TITLES[theme_id]を必須で参照する
    # (既存Production仕様、モジュール自体は無変更)。記事固有のJapanese
    # titleを、既存の拡張ポイントであるこのdictへ実行時に登録する
    # (article本文はJA記事のtitleそのまま、新しい命名/翻訳ロジックは
    # 追加しない)。
    tts_gen.JAPANESE_TITLES[theme["theme_id"]] = japanese_title
    return tts_gen.run_theme(theme)


def run_assemble_stage(theme: dict) -> dict:
    """b1b/a2を個別にtry/exceptする(delegation D7: Audio Validation Gate/
    Human Review LockでblockされたらSTOP、上書き禁止。GATE_BLOCKED状態も
    run_summary_assemble.jsonへ永続化し、player.html生成やevidence
    確認で毎回re-runしなくても状態を読めるようにする)。"""
    out_dir = theme["out_dir"]
    results = {}
    for label, stage_fn in (("b1b", asm.stage_assemble_b1), ("a2", asm.stage_assemble_a2)):
        try:
            results[label] = stage_fn(theme)
        except RuntimeError as e:
            print(f"[E-FAMILY-RUNNER][assemble/{label}] GATE_BLOCKED(override無し、報告のみ): {e}")
            summary = {"status": "GATE_BLOCKED", "error": str(e)}
            save_json(f"{out_dir}/{label}/run_summary_assemble.json", summary)
            results[label] = summary
    return results


# ------------------------------------------------------------
# player.html(delegation D7、既存audio_review_player共有ヘルパーを再利用)
# ------------------------------------------------------------
def _row_info_b1b(label: str, parts: dict, support: dict, narration_dir: str, kp_by_rank: dict) -> dict:
    charon, aoede = "Charon", "Aoede"
    if label in ("Intro", "Outro (Charon)"):
        return {"text": "音楽ジングル/固定音源(読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": "(共有固定Welcome、Master Audio Store)", "voice": charon,
                "audio": f"{narration_dir}/welcome_charon.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": "(共有固定Preview intro)", "voice": charon,
                "audio": f"{narration_dir}/preview_intro_charon.wav", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support["preview"], "voice": charon, "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": "(共有固定Key phrases intro)", "voice": charon,
                "audio": f"{narration_dir}/key_phrases_intro_charon.wav", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        text = f"EN: {kp['used_form']}<br>JA: {kp['japanese_gloss']}"
        return {"text": text, "voice": "Aoede(EN)/Charon(JA)",
                "audio": (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/kp{rank}_ja_charon.wav"),
                "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": "(共有固定Full story intro)", "voice": charon,
                "audio": f"{narration_dir}/full_story_intro_charon.wav", "sfx": False}
    if label.startswith("Comment 1"):
        return {"text": support["comment_1"], "voice": charon, "audio": f"{narration_dir}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2"):
        return {"text": support["comment_2"], "voice": charon, "audio": f"{narration_dir}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3"):
        return {"text": support["comment_3"], "voice": charon, "audio": f"{narration_dir}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4"):
        return {"text": support["comment_4"], "voice": charon, "audio": f"{narration_dir}/comment_4.wav", "sfx": False}
    if label.startswith("Full Story Part 1"):
        return {"text": parts["part1"], "voice": aoede, "audio": f"{narration_dir}/full_story_part1.wav", "sfx": False}
    if label.startswith("Full Story Part 2"):
        return {"text": parts["part2"], "voice": aoede, "audio": f"{narration_dir}/full_story_part2.wav", "sfx": False}
    if label.startswith("Point One semantic heading"):
        return {"text": parts["point_one_heading"], "voice": aoede,
                "audio": f"{narration_dir}/point_one_heading.wav", "sfx": False}
    if label.startswith("Point One"):
        return {"text": parts["point_one_body"], "voice": aoede, "audio": f"{narration_dir}/point_one.wav", "sfx": False}
    if label.startswith("Point Two semantic heading"):
        return {"text": parts["point_two_heading"], "voice": aoede,
                "audio": f"{narration_dir}/point_two_heading.wav", "sfx": False}
    if label.startswith("Point Two"):
        return {"text": parts["point_two_body"], "voice": aoede, "audio": f"{narration_dir}/point_two.wav", "sfx": False}
    if label.startswith("In One Line"):
        return {"text": parts["in_one_line"], "voice": aoede, "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "(共有固定segment、記事固有scriptなし)", "voice": None, "audio": None, "sfx": False}


def _row_info_a2(label: str, parts: dict, support: dict, narration_dir: str, kp_by_rank: dict,
                  japanese_title: str) -> dict:
    aoede = "Aoede"
    if label in ("Intro", "Outro"):
        return {"text": "音楽ジングル/固定音源(読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome":
        return {"text": "(共有固定Welcome)", "voice": aoede, "audio": None, "sfx": False}
    if label == "Topic intro":
        return {"text": f"Today's topic is {parts['title']}.", "voice": aoede,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label == "Japanese title":
        return {"text": japanese_title, "voice": aoede, "audio": f"{narration_dir}/japanese_title.wav", "sfx": False}
    if label == "Preview intro":
        return {"text": "(共有固定Preview intro)", "voice": aoede, "audio": None, "sfx": False}
    if label == "Point explanation":
        return {"text": "(共有固定Point explanation)", "voice": aoede, "audio": None, "sfx": False}
    if label == "Preview":
        return {"text": support["preview"], "voice": aoede, "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label == "Key phrases intro":
        return {"text": "(共有固定Key phrases intro)", "voice": aoede, "audio": None, "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        idx = sorted(kp_by_rank).index(rank) + 1
        text = f"EN: {kp['used_form']}<br>JA: {kp['japanese_gloss']}"
        return {"text": text, "voice": "Aoede",
                "audio": (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/meaning_{idx}.wav"), "sfx": False}
    if label == "Full story intro":
        return {"text": "(共有固定Full story intro)", "voice": aoede, "audio": None, "sfx": False}
    if label.startswith("Comment 1"):
        return {"text": support["comment_1"], "voice": aoede, "audio": f"{narration_dir}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2"):
        return {"text": support["comment_2"], "voice": aoede, "audio": f"{narration_dir}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3"):
        return {"text": support["comment_3"], "voice": aoede, "audio": f"{narration_dir}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4"):
        return {"text": support["comment_4"], "voice": aoede, "audio": f"{narration_dir}/comment_4.wav", "sfx": False}
    if label.startswith("Full Story Part 1"):
        return {"text": parts["part1"], "voice": aoede, "audio": f"{narration_dir}/full_story_part1.wav", "sfx": False}
    if label.startswith("Full Story Part 2"):
        return {"text": parts["part2"], "voice": aoede, "audio": f"{narration_dir}/full_story_part2.wav", "sfx": False}
    if label.startswith("Point One semantic heading"):
        return {"text": parts["point_one_heading"], "voice": aoede,
                "audio": f"{narration_dir}/point_one_heading.wav", "sfx": False}
    if label.startswith("Point One"):
        return {"text": parts["point_one_body"], "voice": aoede, "audio": f"{narration_dir}/point_one.wav", "sfx": False}
    if label.startswith("Point Two semantic heading"):
        return {"text": parts["point_two_heading"], "voice": aoede,
                "audio": f"{narration_dir}/point_two_heading.wav", "sfx": False}
    if label.startswith("Point Two"):
        return {"text": parts["point_two_body"], "voice": aoede, "audio": f"{narration_dir}/point_two.wav", "sfx": False}
    if label.startswith("In One Line"):
        return {"text": parts["in_one_line"], "voice": aoede, "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "(共有固定segment、記事固有scriptなし)", "voice": None, "audio": None, "sfx": False}


def _build_level_table(level_dir: str, level: str, japanese_title: str = "") -> str:
    assemble_summary = load_json(f"{level_dir}/run_summary_assemble.json")
    if assemble_summary.get("status") != "OK":
        return f"<p style='color:#b00'>Assembly未完了(status={assemble_summary.get('status')})。table省略。</p>"
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    parts = load_json(f"{level_dir}/parts.json")
    narration_dir = f"{level_dir}/narration"
    kp = load_json(f"{level_dir}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp["items"]}
    abs_url = player_common.abs_file_url

    if level == "b1b":
        support = load_json(f"{level_dir}/b1_support_texts.json")
    else:
        support = load_json(f"{level_dir}/a2_support_texts.json")

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        if level == "b1b":
            info = _row_info_b1b(label, parts, support, narration_dir, kp_by_rank)
        else:
            info = _row_info_a2(label, parts, support, narration_dir, kp_by_rank, japanese_title)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"] or not info["audio"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        else:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        rows.append(player_common.render_timeline_row(sec, label, voice_disp, info["text"], audio_html, missing=False))
    return player_common.render_timeline_table(rows)


def _load_assemble_summary(path: str) -> dict:
    if not os.path.exists(path):
        return {"status": "NOT_ATTEMPTED_OR_GATE_BLOCKED_BEFORE_SUMMARY_WRITE"}
    return load_json(path)


def build_player_html(theme: dict, japanese_title: str) -> str:
    out_dir = theme["out_dir"]
    abs_url = player_common.abs_file_url
    b1b_summary = _load_assemble_summary(f"{out_dir}/b1b/run_summary_assemble.json")
    a2_summary = _load_assemble_summary(f"{out_dir}/a2/run_summary_assemble.json")

    b1b_audio_html = ""
    if b1b_summary.get("status") == "OK":
        b1b_audio_html = (f'<h2>Advanced(B1、Natural English Adaptation)</h2>'
                           f'<audio class="main" controls preload="none" '
                           f'src="{abs_url(b1b_summary["out_path"])}"></audio>'
                           f'<p class="note">duration={b1b_summary["duration_seconds"]}s '
                           f'peak={b1b_summary["peak"]} clipping={b1b_summary["clipping_detected"]}</p>'
                           f'{_build_level_table(f"{out_dir}/b1b", "b1b")}')
    else:
        b1b_audio_html = f'<h2>Advanced(B1)</h2><p style="color:#b00">status={b1b_summary.get("status")}</p>'

    a2_audio_html = ""
    if a2_summary.get("status") == "OK":
        a2_audio_html = (f'<h2>Standard(A2、v5 6,000語ライン)</h2>'
                          f'<audio class="main" controls preload="none" '
                          f'src="{abs_url(a2_summary["out_path"])}"></audio>'
                          f'<p class="note">duration={a2_summary["duration_seconds"]}s '
                          f'peak={a2_summary["peak"]} clipping={a2_summary["clipping_detected"]}</p>'
                          f'{_build_level_table(f"{out_dir}/a2", "a2", japanese_title)}')
    else:
        a2_audio_html = f'<h2>Standard(A2)</h2><p style="color:#b00">status={a2_summary.get("status")}</p>'

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01 player({theme['theme_id']})</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01({theme['theme_id']})</h1>
<p class="note">Production正式runner(er012_e_family_entertainment_two_level_runner_01.py、
Trialスクリプト非経由)による生成。Advanced=Natural English Adaptation(B1)、
Standard=A2 v5(6,000語ライン+自然さ優先)。</p>
{b1b_audio_html}
{a2_audio_html}
</body></html>
"""
    out_path = f"{out_dir}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ja-article", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--ledger-file", default=None, help="既存Ledgerを再利用する場合のpath")
    parser.add_argument("--source-id", default="",
                         help="日本語記事の由来管理ID(evidenceとして記録のみ)")
    parser.add_argument("--topic", default=None,
                         help="Ledger新規構築時のResearcher/Verification用topic文字列"
                              "(--ledger-file指定時は不要)")
    parser.add_argument("--budget-jpy", type=float, default=300.0)
    parser.add_argument("--stage", default="all",
                         choices=("ledger", "writer", "scaffold", "tts", "assemble", "player", "all"))
    parser.add_argument("--regenerate-stage", default=None, choices=("advanced", "standard"))
    parser.add_argument("--tts-mode", default="STANDARD", choices=("STANDARD", "BATCH"),
                         help="TTS実行方式(既定STANDARD、PM_GOVERNANCE.md 7-1: 正式リリース前は"
                              "原則Standard同期)。BATCH指定時は--batch-reason必須(7-2の例外条件)。")
    parser.add_argument("--batch-reason", default=None,
                         help="--tts-mode BATCH指定時に必須。PM_GOVERNANCE.md 7-2の例外条件"
                              "(1〜4のいずれか)に該当する理由を明記する。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.tts_mode == "BATCH" and not args.batch_reason:
        parser.error("--tts-mode BATCH を指定する場合は --batch-reason で"
                      "PM_GOVERNANCE.md 7-2の例外条件に該当する理由を明示すること。")

    os.environ["TTS_EXECUTION_MODE"] = args.tts_mode

    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")

    ja_text = load_text(args.ja_article)
    ja_sha256 = sha256_text(ja_text)
    japanese_title = _extract_title(ja_text) or ja_text.splitlines()[0].strip()

    save_json(f"{args.out_dir}/entry_point.json", {
        "runner": "er012_e_family_entertainment_two_level_runner_01.py",
        "ja_article_path": args.ja_article,
        "ja_article_sha256": ja_sha256,
        "source_management_id": args.source_id,
        "slug": args.slug,
        "japanese_title": japanese_title,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tts_execution_mode": args.tts_mode,
        "tts_batch_reason": args.batch_reason,
    })

    theme = {
        "theme_id": args.slug,
        "topic": args.topic or japanese_title,
        "out_dir": args.out_dir,
        "ledger_path": f"{args.out_dir}/ledger/verified_fact_ledger.txt",
    }

    client = vfl01.get_client()

    if args.stage in ("ledger", "writer", "all") or args.regenerate_stage:
        ledger_text = load_or_build_ledger(client, args.out_dir, theme["topic"], args.ledger_file)
        assert_budget_ok(args.out_dir, args.budget_jpy, "after ledger")
    else:
        ledger_text = load_text(theme["ledger_path"]) if os.path.exists(theme["ledger_path"]) else ""

    if args.regenerate_stage:
        run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only=args.regenerate_stage)
        print(f"[E-FAMILY-RUNNER] regenerate-stage={args.regenerate_stage} 完了。")
        return

    if args.stage in ("writer", "all"):
        run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only=None)

    if args.stage in ("scaffold", "all"):
        run_scaffold_stage(client, theme)
        assert_budget_ok(args.out_dir, args.budget_jpy, "after scaffold")

    if args.stage in ("tts", "all"):
        run_tts_stage(theme, japanese_title)
        assert_budget_ok(args.out_dir, args.budget_jpy, "after tts")

    if args.stage in ("assemble", "all"):
        run_assemble_stage(theme)

    if args.stage in ("player", "all"):
        player_path = build_player_html(theme, japanese_title)
        print(f"[E-FAMILY-RUNNER] player.html: {os.path.abspath(player_path)}")

    final_jpy, by_provider = compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[E-FAMILY-RUNNER] 完了。stage={args.stage} 累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")


if __name__ == "__main__":
    main()
