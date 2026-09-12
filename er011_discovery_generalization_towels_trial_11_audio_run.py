# ============================================================
# er011_discovery_generalization_towels_trial_11_audio_run.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01
# ============================================================
# 目的(ユーザー決定 2026-09-10): 既に記事生成+QA一式が完了している
# FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11(タオル臭テーマ、A2/B1B、
# Discovery Focus Module Part A単独、保険文制約なし)の記事(`er011_output/
# discovery_generalization_towels_trial_11/{a2,b1b}/article.md`、本タスクでは
# **変更しない**)に対して、Support(Preview/Comment/Key Phrase)→Audio(TTS+
# ASR検証→Assembly+SFX)→試聴artifact(player.html)までを、既存Production
# 関数のみ(無変更で直接呼ぶ)で作る。**Trial(Production実装ではない)**。
# Focus ModuleのProduction採用判断は本タスクでは行わない(ユーザー試聴待ち)。
# Production/Prompt/共有module/registry/SSOT編集・Git操作は一切行わない。
#
# 再利用(import・無変更、read-onlyでの参照のみ):
#   - er011_household_unified_final_candidate_01_run.py(手本、Support/Audio
#     段階のオーケストレーション構造・費用実測ロジックを踏襲。コード自体は
#     importせず、同一のProduction関数呼び出しパターンを本scriptへ再実装)。
#   - er003_v1_n3_01_scaffold_generate(sc): split_article_text/get_client/
#     run_a2_scaffold/run_b1_scaffold/run_key_phrases。無変更。
#   - er003_v1_n3_01_tts_generate(tts_gen): generate_a2_segments/
#     generate_b1_segments/JAPANESE_TITLES。無変更(JAPANESE_TITLESへの
#     .update()はA2のtheme_id gap用の人手供給、OPEN-137既知gapの継続)。
#   - er003_v1_n3_01_assemble(asm): stage_assemble_a2/stage_assemble_b1/
#     derive_a_family_required_structure/verify_episode_audio_validation_gate。
#     無変更。
#   - audio_review_player(arp): 標準player部品(Source列なし、min-width
#     360px、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)。無変更。
#   - er003_b1_p9a_audio(p9a): PODCAST_NAME_TEXT_V2/PREVIEW_INTRO_TEXT/
#     KEY_PHRASES_INTRO_TEXT/FULL_STORY_INTRO_TEXT(固定文言)。無変更。
#   - er005_cost_logger(cl): install/logging_context。無変更。
#
# 既知gap是正(前回Trial-11記事生成段階の既知gap、REPORT記載): 前回は
# cl.logging_context(theme=THEME_ID, stage=...)のtheme引数にlevelを含めな
# かったため、レベル別費用集計が容易でなかった。本scriptでは
# theme=f"{THEME_ID}_{level}"としてlevelをtheme_tagへ含め、費用集計を
# レベル別に分離できるようにする(Household一本化最終候補と同様の方式)。
#
# 費用: 前段(記事生成、raw_usage_log.jsonl、実測¥117.72、既存・別タスク)
# とは別に、本タスク(Support+Audio)専用のusage logを新規に使う
# (`audit/raw_usage_log_audio_01.jsonl`)。本タスクの費用上限は合計¥120
# (Household最終候補のSupport+Audio実績は約¥68)。同期実行のみ。
# バックグラウンド待機・二重起動禁止。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_audio_run.py [stage ...]
#   stage: a2 | b1b | player | cost | all(省略時)
# ============================================================
from __future__ import annotations

import html
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# TTS-DEV-PROD-MODE-SEPARATION-01是正: 本scriptのコメント(42行目「同期実行
# のみ」)が示す本来の意図に反し、実際には`er006_batch_tts_wiring_01.py`の
# `DEFAULT_TTS_EXECUTION_MODE`(Production量産向け既定=BATCH)がそのまま
# 適用され、Gemini Batch API経由で実行されていた(OPEN-144の副産物として
# 発見)。Trial/開発runはスピード優先でStandard同期へ戻す(Production量産の
# 既定=BATCHはer006_batch_tts_wiring_01.py側では変更しない)。呼び出し元
# (このTrial harness)が明示的に環境変数を指定していない場合のみSTANDARDを
# 既定にする(os.environ.setdefault、呼び出し元が別途明示指定していれば
# それを尊重する)。
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import audio_review_player as arp
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
AUDIO_COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log_audio_01.jsonl"
BUDGET_JPY_CAP = 120.0

# ユーザー提示の日本語タイトル(2026-09-10、OPEN-137継続の既知gap:
# JAPANESE_TITLES辞書に本Trialのtheme_id未登録のため、A2のjapanese_title
# segmentへ人手で供給する。新しい主張・数字は追加していない)。
TOWELS_JAPANESE_TITLE = "洗濯したのに、なぜタオルは臭うことがあるのか?"

LEVELS = {
    "a2": {"label": "A2", "gate_level": "A2"},
    "b1b": {"label": "B1B", "gate_level": "B1"},
}

# ------------------------------------------------------------
# 保険文検出regex(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10/
# Household最終候補scriptと同一定義、read-onlyで転記して再利用)。Support文
# (Preview/Comment)に対して計数のみ行い、本文修正はしない。
# ------------------------------------------------------------
_VERB = r"(?:check|consult|ask|see|refer to|look at|read|follow)"
_SOURCE = r"(?:instructions?|manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|experts?|labels?|packagings?|packages?)"
INSURANCE_RE = re.compile(_VERB + r"[^.!?]{0,80}" + _SOURCE, re.IGNORECASE)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def detect_insurance_sentences(text: str) -> list:
    return [m.group(0) for m in INSURANCE_RE.finditer(text or "")]


# ============================================================
# 費用実測(Household最終候補scriptと同一ロジック、log_pathのみ本タスク
# 専用のAUDIO_COST_LOG_PATHへ差し替え。単価は既存OFFICIAL_SOURCEをそのまま
# 参照、独自の単価は一切定義しない)。
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    """(cost_usd, unpriced: bool)を返す。既存OFFICIAL_SOURCE
    (pricing_snapshot.json)に無い組み合わせはunpriced=Trueとして0円計上し、
    cost_summary.jsonのunpriced_recordsへ記録する(黙って無視しない)。"""
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        if provider == "gemini":
            return (it / 1e6) * _price("gemini", model, "input_tokens") \
                + (ot / 1e6) * _price("gemini", model, "output_tokens"), False
        if provider == "gemini_batch":
            # OPEN-144是正: Gemini Batch API(batches.create)経由の呼び出しは
            # provider="gemini_batch"で記録されるが、pricing_snapshot.json側は
            # provider="gemini"のtier="Batch"として単価定義されている。従来は
            # このプロバイダ名不一致によりKeyErrorで0円(unpriced)計上していた。
            return (it / 1e6) * _price("gemini", model, "input_tokens", tier="Batch") \
                + (ot / 1e6) * _price("gemini", model, "output_tokens", tier="Batch"), False
        if provider == "openai_asr":
            return (it / 1e6) * _price("openai_asr", model, "input_tokens") \
                + (ot / 1e6) * _price("openai_asr", model, "output_tokens"), False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    """本タスク専用log(AUDIO_COST_LOG_PATH)のみを集計する(前段の記事生成
    費用[raw_usage_log.jsonl、実測¥117.72、既存・別タスク]は含めない)。
    theme_tagにlevel(a2/b1b)を含めているため、by_level_jpyでレベル別
    分離ができる(前回Trial-11記事生成段階の既知gap是正)。"""
    log_path = AUDIO_COST_LOG_PATH
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "by_level_jpy": {},
                 "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, by_level, unpriced = 0.0, {}, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            theme_tag = rec.get("theme") or ""
            level = theme_tag[len(THEME_ID) + 1:] if theme_tag.startswith(THEME_ID + "_") else "other"
            by_level[level] = by_level.get(level, 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "by_level_jpy": {k: round(v * USD_JPY, 2) for k, v in by_level.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/audit/cost_summary_audio_01.json", result)
    print(f"[{THEME_ID}][cost][AUDIO-01] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_level={result['by_level_jpy']} by_provider={result['by_provider_jpy']} "
          f"unpriced_records={result['unpriced_records']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Step 1: Support(Preview/Comment、Production関数を無変更で直接呼ぶ)
# ============================================================
def support_stage(level: str) -> dict:
    out_dir = f"{OUT_DIR}/{level}"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    parts = sc.split_article_text(article_text)
    save_json(f"{out_dir}/parts.json", parts)
    client = sc.get_client()
    run_fn = sc.run_a2_scaffold if level == "a2" else sc.run_b1_scaffold
    with cl.logging_context(f"{THEME_ID}_{level}", "scaffold"):
        support = run_fn(client, parts, out_dir, article_text)
    status = {k: v.get("status") for k, v in support.items()}

    support_texts = {k: v.get("text") for k, v in support.items()}
    insurance_hits = {k: detect_insurance_sentences(t) for k, t in support_texts.items()}
    insurance_hits = {k: v for k, v in insurance_hits.items() if v}
    total_insurance_hits = sum(len(v) for v in insurance_hits.values())
    save_json(f"{out_dir}/audit/support_insurance_sentence_check.json",
              {"insurance_sentence_hits_broad_regex_by_field": insurance_hits,
               "total_insurance_sentence_hit_count": total_insurance_hits})
    print(f"[{THEME_ID}][{level}] scaffold(Preview/Comment)完了。status={status} "
          f"insurance_hits={total_insurance_hits}")
    return {"support_status": status, "insurance_hits": insurance_hits,
            "total_insurance_hits": total_insurance_hits}


# ============================================================
# Step 2: Key Phrase(Selection→Canonicalization→Redundancy QA、
# Production関数sc.run_key_phrasesを無変更で直接呼ぶ)
# ============================================================
def keyphrase_stage(level: str) -> dict:
    meta = LEVELS[level]
    out_dir = f"{OUT_DIR}/{level}"
    kp_dir = f"{out_dir}/key_phrases"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    article_id = f"DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11_{meta['label']}"
    source_level = "B1-B(N3-01, direct generation)" if level == "b1b" else "A2(V2改1, N3-01)"
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    with cl.logging_context(f"{THEME_ID}_{level}", "keyphrase"):
        kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level, process=process)
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    summary = {"selection_status": sel_status, "canonicalization_status": canon_status,
               "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log")}
    save_json(f"{out_dir}/audit/run_key_phrases_result_summary.json", summary)
    print(f"[{THEME_ID}][{level}] key phrase: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"[{level}] Key Phraseパイプライン失敗、STOP。selection={sel_status} "
                            f"canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError(f"[{level}] Key Phrase Redundancy QAがretry上限到達後もNG_REVIEW_REQUIRED、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return summary


# ============================================================
# Step 3: 日本語タイトルgap fill(A2のみ、ユーザー提示のタイトルを供給)
# ============================================================
def japanese_title_stage() -> dict:
    tts_gen.JAPANESE_TITLES.update({THEME_ID: TOWELS_JAPANESE_TITLE})
    note = {
        "gap": "JAPANESE_TITLES辞書にtheme_id(discovery_generalization_towels_trial_11)未登録のため"
               "KeyErrorが発生する(OPEN-137継続の既知gap)。",
        "resolution": "ユーザー提示の日本語タイトルをTrial内で供給(新しい主張・数字は追加しない)。",
        "supplied_title": TOWELS_JAPANESE_TITLE,
        "supplied_by": "user (2026-09-10 Fable委任文)",
    }
    save_json(f"{OUT_DIR}/audit/a2_japanese_title_gap_note.json", note)
    print(f"[{THEME_ID}][a2] JAPANESE_TITLES登録(gap fill・ユーザー提示タイトル): {TOWELS_JAPANESE_TITLE!r}")
    return note


# ============================================================
# Step 4: TTS(Production関数を無変更で直接呼ぶ)
# ============================================================
def tts_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(f"{THEME_ID}_{level}", "tts"):
        result = tts_gen.generate_a2_segments(theme) if level == "a2" else tts_gen.generate_b1_segments(theme)
    print(f"[{THEME_ID}][{level}] TTS完了。segment_status/key_phrase_statusを確認してください。")
    return result


# ============================================================
# Step 5: Human Review Lock状態の確認(既存Production機構、review_lock_
# state.json、3回NGでHUMAN_REVIEW_REQUIRED。本scriptは回避・再生成を行わず
# 状態を読み取って報告するだけ)。
# ============================================================
def lock_summary_stage(level: str) -> dict:
    path = f"{OUT_DIR}/{level}/audit/review_lock_state.json"
    if not os.path.exists(path):
        return {"lock_state_file_present": False}
    store = load_json(path)
    per_segment = {seg_id: {"state": v.get("state"), "final_status": v.get("final_status"),
                             "cumulative_tts_attempts": v.get("cumulative_tts_attempts"),
                             "cumulative_asr_calls": v.get("cumulative_asr_calls"),
                             "budget_guard_triggered": v.get("budget_guard_triggered")}
                   for seg_id, v in store.items()}
    locked_segments = [seg_id for seg_id, v in per_segment.items()
                        if v.get("final_status") not in ("OK", None) or v.get("budget_guard_triggered")]
    max_attempts = max((v.get("cumulative_tts_attempts") or 0) for v in per_segment.values()) if per_segment else 0
    summary = {"lock_state_file_present": True, "segment_count": len(per_segment),
               "max_cumulative_tts_attempts_any_segment": max_attempts,
               "locked_or_review_required_segments": locked_segments}
    save_json(f"{OUT_DIR}/{level}/audit/review_lock_summary_audio_01.json", summary)
    print(f"[{THEME_ID}][{level}] Human Review Lock状態: segment_count={len(per_segment)} "
          f"max_attempts={max_attempts} locked_or_review_required={locked_segments}")
    return summary


# ============================================================
# Step 6: Assembly(Gate OFF経路[内部で自動実行]) + Gate opt-in ON経路
# (OPEN-129、read-only)
# ============================================================
def assembly_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    out_dir = f"{OUT_DIR}/{level}"
    assemble_fn = asm.stage_assemble_a2 if level == "a2" else asm.stage_assemble_b1
    with cl.logging_context(f"{THEME_ID}_{level}", "assemble"):
        try:
            result = assemble_fn(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    print(f"[{THEME_ID}][{level}] Assembly(Gate OFF経路)結果: {result.get('gate_off_result')}")

    gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    if result.get("gate_off_result") == "PASS":
        rs = asm.derive_a_family_required_structure(LEVELS[level]["gate_level"])
        try:
            asm.verify_episode_audio_validation_gate(out_dir, LEVELS[level]["gate_level"], required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:1200]}
    print(f"[{THEME_ID}][{level}] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")
    result["gate_opt_in_result"] = gate_on
    save_json(f"{out_dir}/audit/assembly_and_gate_summary_audio_01.json", result)
    return result


# ============================================================
# Level単位オーケストレーション
# ============================================================
def run_level(level: str) -> dict:
    print(f"===== [{THEME_ID}][AUDIO-01] level={level} 開始 =====")
    support_summary = support_stage(level)
    kp_summary = keyphrase_stage(level)
    if level == "a2":
        japanese_title_stage()
    tts_result = tts_stage(level)
    lock_summary = lock_summary_stage(level)
    assembly_result = assembly_stage(level)

    return {
        "level": level, "support": support_summary, "key_phrase": kp_summary,
        "tts": tts_result, "review_lock": lock_summary, "assembly": assembly_result,
    }


# ============================================================
# Step 7: 試聴player.html(A2/B1B切替、標準player部品arp使用、
# 絶対パスfile:// URL方式、Household最終候補build_player.pyと同一ロジック)
# ============================================================
def esc(text) -> str:
    if text is None:
        return ""
    return html.escape(str(text)).replace("\n\n", "<br><br>").replace("\n", "<br>")


def au(path: str) -> str:
    return arp.abs_file_url(path)


def build_b1b_rows() -> tuple:
    b1_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{b1_dir}/narration"
    parts = load_json(f"{b1_dir}/parts.json")
    support = load_json(f"{b1_dir}/b1_support_texts.json")
    timeline = load_json(f"{b1_dir}/audit/timeline.json")
    kp = load_json(f"{b1_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = {item["rank"]: item for item in kp["items"]}

    def audio_url(name: str) -> str:
        return au(f"{narration_dir}/{name}.wav")

    fixed_text = {
        "welcome_charon": p9a.PODCAST_NAME_TEXT_V2,
        "preview_intro_charon": p9a.PREVIEW_INTRO_TEXT,
        "key_phrases_intro_charon": p9a.KEY_PHRASES_INTRO_TEXT,
        "full_story_intro_charon": p9a.FULL_STORY_INTRO_TEXT,
    }
    sfx_labels = {"Intro", "Notification 1", "Notification 2", "Notification 3", "Outro (Charon)",
                  "Point Notification (Point One cue)", "Point Notification (Point Two cue)"}

    def resolve_row(label: str):
        if label in sfx_labels:
            return "SFX", "効果音・音楽ジングル(読み上げなし、固定音源)。", "—"
        if label.startswith("pause_"):
            return None, None, None
        if label == "Welcome (Charon)":
            return "Charon", esc(fixed_text["welcome_charon"]), arp.render_single_audio_html(audio_url("welcome_charon"))
        if label == "Preview intro (Charon)":
            return "Charon", esc(fixed_text["preview_intro_charon"]), arp.render_single_audio_html(audio_url("preview_intro_charon"))
        if label == "Key phrases intro (Charon)":
            return "Charon", esc(fixed_text["key_phrases_intro_charon"]), arp.render_single_audio_html(audio_url("key_phrases_intro_charon"))
        if label == "Full story intro (Charon)":
            return "Charon", esc(fixed_text["full_story_intro_charon"]), arp.render_single_audio_html(audio_url("full_story_intro_charon"))
        if label == "Topic intro (Charon)":
            text = f"Today's topic is {parts['title']}."
            return "Charon", esc(text), arp.render_single_audio_html(audio_url("topic_intro"))
        if label == "Preview (Charon)":
            return "Charon", esc(support.get("preview")), arp.render_single_audio_html(audio_url("preview"))
        comment_map = {"Comment 1 (Charon)": 1, "Comment 2 (Charon)": 2,
                       "Comment 3 (Charon, Bridge)": 3, "Comment 4 (Charon)": 4}
        if label in comment_map:
            i = comment_map[label]
            return "Charon", esc(support.get(f"comment_{i}")), arp.render_single_audio_html(audio_url(f"comment_{i}"))
        if label.startswith("Key Phrase "):
            rank = int(label.split(" ")[-1])
            item = kp_items.get(rank)
            if item is None:
                return "Aoede/Charon", "未取得", "—"
            text = f"EN: {esc(item['used_form'])}<br>JA(表示/TTS共通): {esc(item['japanese_gloss'])}"
            audio_html = arp.render_single_audio_html((audio_url(f"kp{rank}_en"), audio_url(f"kp{rank}_ja_charon")))
            return "Aoede(EN)/Charon(JA)", text, audio_html
        if label == "Full Story Part 1 (Aoede)":
            return "Aoede", esc(parts.get("part1")), arp.render_single_audio_html(audio_url("full_story_part1"))
        if label == "Full Story Part 2 (Aoede)":
            return "Aoede", esc(parts.get("part2")), arp.render_single_audio_html(audio_url("full_story_part2"))
        if label == "Point One semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_one_heading")), arp.render_single_audio_html(audio_url("point_one_heading"))
        if label == "Point One (Aoede)":
            return "Aoede", esc(parts.get("point_one_body")), arp.render_single_audio_html(audio_url("point_one"))
        if label == "Point Two semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_two_heading")), arp.render_single_audio_html(audio_url("point_two_heading"))
        if label == "Point Two (Aoede)":
            return "Aoede", esc(parts.get("point_two_body")), arp.render_single_audio_html(audio_url("point_two"))
        if label == "In One Line (Aoede)":
            return "Aoede", esc(parts.get("in_one_line")), arp.render_single_audio_html(audio_url("in_one_line"))
        return "未取得", "未取得", "—"

    rows = []
    for entry in timeline:
        voice, script_html, audio_html = resolve_row(entry["part"])
        if voice is None:
            continue
        rows.append(arp.render_timeline_row(entry["start_seconds"], entry["part"], voice, script_html, audio_html,
                                             missing=False))

    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items.keys()):
        item = kp_items[rank]
        kp_rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td><td>{esc(item['japanese_gloss'])}</td>"
                        f"<td>{esc(item.get('japanese_gloss_tts') or item['japanese_gloss'])}</td></tr>")
    kp_table_html = f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'

    return rows, kp_table_html, parts, support


def build_a2_rows() -> tuple:
    a2_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{a2_dir}/narration"
    parts = load_json(f"{a2_dir}/parts.json")
    support = load_json(f"{a2_dir}/a2_support_texts.json")
    timeline = load_json(f"{a2_dir}/audit/timeline.json")
    tts = load_json(f"{a2_dir}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{a2_dir}/key_phrases/keywords_canonicalized.json")
    seg = tts["segments"]
    kp = tts["key_phrases"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_audio(name: str) -> str:
        return au(f"{narration_dir}/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_paths):
        sec = start_by_part[part_name]
        audio_html = arp.render_single_audio_html(audio_paths) if audio_paths else "—"
        rows.append(arp.render_timeline_row(sec, label, voice, script_html, audio_html, missing=(audio_paths is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)
    add("Welcome", "Welcome", "Charon(固定文言)", esc(p9a.PODCAST_NAME_TEXT_V2), None)
    add("Topic intro", "Topic intro", "Aoede(英語)", esc(seg["topic_intro"].get("text")), seg_audio("topic_intro"))
    ja_title = seg.get("japanese_title", {}).get("text", "")
    add("Japanese title", "Japanese title", "Aoede(日本語、ユーザー提示タイトル)",
        esc(ja_title), seg_audio("japanese_title"))
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Preview intro", "Preview intro", "Charon(固定文言)", esc(p9a.PREVIEW_INTRO_TEXT), None)
    add("Point explanation", "Point explanation", "Charon(固定文言・日本語)", "ポイント解説", None)
    add("Preview", "Preview", "Aoede(日本語)", esc(support.get("preview")), seg_audio("preview"))
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Key phrases intro", "Key phrases intro", "Charon(固定文言)", esc(p9a.KEY_PHRASES_INTRO_TEXT), None)

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
        gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {esc(ja_gloss_tts)})"
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
            f"英語: {esc(used_form)}<br>日本語gloss(表示用): {esc(ja_gloss)}{gloss_note}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"meaning_{rank}")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro", "Full story intro", "Charon(固定文言)", esc(p9a.FULL_STORY_INTRO_TEXT), None)
    add("Comment 1", "Comment 1", "Aoede(日本語)", esc(support.get("comment_1")), seg_audio("comment_1"))
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part1"].get("text")), seg_audio("full_story_part1"))
    add("Comment 2", "Comment 2", "Aoede(日本語)", esc(support.get("comment_2")), seg_audio("comment_2"))
    add("Full Story Part 2", "Full Story Part 2", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part2"].get("text")), seg_audio("full_story_part2"))
    add("Comment 3", "Comment 3", "Aoede(日本語)", esc(support.get("comment_3")), seg_audio("comment_3"))
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point One semantic heading", "Point One heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_one_heading"].get("text")), seg_audio("point_one_heading"))
    add("Point One", "Point One", "Aoede(英語・A2 6%減速)", esc(seg["point_one"].get("text")), seg_audio("point_one"))
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point Two semantic heading", "Point Two heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_two_heading"].get("text")), seg_audio("point_two_heading"))
    add("Point Two", "Point Two", "Aoede(英語・A2 6%減速)", esc(seg["point_two"].get("text")), seg_audio("point_two"))
    add("Comment 4", "Comment 4", "Aoede(日本語)", esc(support.get("comment_4")), seg_audio("comment_4"))
    add("In One Line", "In One Line", "Aoede(英語・A2 6%減速)", esc(seg["in_one_line"].get("text")), seg_audio("in_one_line"))
    add("Outro", "Outro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)

    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items_by_rank.keys()):
        item = kp_items_by_rank[rank]
        kp_rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td><td>{esc(item['japanese_gloss'])}</td>"
                        f"<td>{esc(item.get('japanese_gloss_tts') or item['japanese_gloss'])}</td></tr>")
    kp_table_html = f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'

    return rows, kp_table_html, parts, support


def player_stage() -> dict:
    a2_rows, a2_kp_table, a2_parts, a2_support = build_a2_rows()
    b1b_rows, b1b_kp_table, b1b_parts, b1b_support = build_b1b_rows()

    a2_assemble = load_json(f"{OUT_DIR}/a2/run_summary_assemble.json")
    b1b_assemble = load_json(f"{OUT_DIR}/b1b/run_summary_assemble.json")
    a2_audio_url = au(a2_assemble["out_path"])
    b1b_audio_url = au(b1b_assemble["out_path"])

    with open(f"{OUT_DIR}/a2/article.md", encoding="utf-8") as f:
        a2_article_md = f.read()
    with open(f"{OUT_DIR}/b1b/article.md", encoding="utf-8") as f:
        b1b_article_md = f.read()

    note = """
<p class="note">
このページはFAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01
(Trial扱い、Production配線なし)の試聴用ページです。A2/B1Bとも、既に完了して
いる記事(Discovery Focus Module Part A単独、保険文制約なし)に対して、
既存Production関数(Preview/Comment/Key Phrase選定[Redundancy QA込み]/TTS
[ASR検証]/Assembly[SFX込み]/Audio Validation Gate)を無変更で直接呼び、
Support生成からAudio完成まで実行しました。標準フォーマット
(audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-
FORMAT-11、Source列なし)準拠。<b>Focus ModuleのProduction採用判断はこの
Trialでは行っていません。ユーザー試聴待ちです。</b>
</p>
<p class="note">
A2: duration={a2_dur}s / peak={a2_peak} / clipping={a2_clip}。日本語タイトルは
ユーザー提示テキストを供給(JAPANESE_TITLES辞書に本Trial theme_id未登録の
ためのgap fill、OPEN-137継続既知gap、新しい主張・数字は追加していない)。<br>
B1B: duration={b1b_dur}s / peak={b1b_peak} / clipping={b1b_clip}。
</p>
""".format(a2_dur=a2_assemble["duration_seconds"], a2_peak=a2_assemble["peak"], a2_clip=a2_assemble["clipping_detected"],
           b1b_dur=b1b_assemble["duration_seconds"], b1b_peak=b1b_assemble["peak"], b1b_clip=b1b_assemble["clipping_detected"])

    # 標準arp.SEEK_SCRIPTは単一id="episode_audio"を前提とする(1ページ1完成
    # episode音声の既存前例のみ)。本ページはA2/B1Bの2つの完成episode音声を
    # 1ページに並置するため、標準CSS/render_timeline_row/render_timeline_table
    # は無変更のまま使い、Seek対象の解決だけをdata-audio-target属性でscopeする
    # 独自スクリプトに置き換える(audio_review_player.py自体は無変更、
    # Household最終候補build_player.pyと同一パターン)。
    scoped_seek_script = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-audio-target]").forEach(function (container) {
    var audioId = container.getAttribute("data-audio-target");
    container.querySelectorAll("button.seek").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var a = document.getElementById(audioId);
        a.currentTime = parseFloat(btn.getAttribute("data-sec"));
        a.play();
      });
    });
  });
});
""".strip("\n")

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01 — タオル臭テーマ(A2/B1B、Discovery Focus Module Part A単独)</h1>
{note}

<div data-audio-target="episode_audio_a2">
<h2>A2 — 「{esc(a2_parts.get('title'))}」</h2>
<audio id="episode_audio_a2" class="main" controls src="{a2_audio_url}"></audio>
<h3>A2 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(a2_rows)}
<h3>A2 Key Phrase表</h3>
{a2_kp_table}
<h3>A2 記事全文(article.md)</h3>
<pre class="article">{esc(a2_article_md)}</pre>
</div>

<hr>

<div data-audio-target="episode_audio_b1b">
<h2>B1B — 「{esc(b1b_parts.get('title'))}」</h2>
<audio id="episode_audio_b1b" class="main" controls src="{b1b_audio_url}"></audio>
<h3>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(b1b_rows)}
<h3>B1B Key Phrase表</h3>
{b1b_kp_table}
<h3>B1B 記事全文(article.md)</h3>
<pre class="article">{esc(b1b_article_md)}</pre>
</div>

<script>
{scoped_seek_script}
</script>
</body>
</html>
"""

    player_out_path = f"{OUT_DIR}/player.html"
    with open(player_out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    abs_path = os.path.abspath(player_out_path).replace("\\", "/")
    print(f"player.html 出力: {player_out_path}")
    print(f"file:///{abs_path}")
    return {"player_html_path": player_out_path, "player_html_file_url": f"file:///{abs_path}",
            "a2_wav_file_url": a2_audio_url, "b1b_wav_file_url": b1b_audio_url}


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(AUDIO_COST_LOG_PATH)

    if stages == ["all"]:
        results = {}
        for level in ("a2", "b1b"):
            try:
                results[level] = run_level(level)
            except (RuntimeError, AssertionError) as e:
                results[level] = {"level": level, "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{level}] STOP: {e}")
            cost_stage()
        if results.get("a2", {}).get("status") != "STOP" and results.get("b1b", {}).get("status") != "STOP":
            results["player"] = player_stage()
        save_json(f"{OUT_DIR}/audit/e2e_run_summary_audio_01.json", results)
        print(f"[{THEME_ID}][AUDIO-01] 完了。")
        return results

    result = {}
    for s in stages:
        if s in ("a2", "b1b"):
            result[s] = run_level(s)
        elif s == "player":
            result["player"] = player_stage()
        elif s == "cost":
            result["cost"] = cost_stage()
        else:
            print(f"unknown stage: {s}")
    save_json(f"{OUT_DIR}/audit/e2e_run_summary_audio_01_partial_{'_'.join(stages)}.json", result)
    return result


if __name__ == "__main__":
    main()
