# -*- coding: utf-8 -*-
"""KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01: Key Phrase候補要求を「フレーズ7件」+「単語単体3件」に分けて要求するDEV Trial。

位置づけ: **DEV/Trial専用**。Production(er119_kp_candidates_01 / er105 / er003_key_words_* / er119_kp_human_review_*)は
read/importのみで1字も変更しない。Production経路へは入らない(このmoduleはProductionから一切importされない)。
Gate(本文連続一致・1〜5語・有限助動詞・数値placeholder・CMU・Human NG・既存候補との同一/包含・canonicalization[LLM]・gloss再整合・
CMU post-canon・記号・[Z]人称整合/SRC D1・Redundancy QA)は **Production関数をそのままimportして同一引数**で適用する。
新設したのは「要求区分(フレーズ7/単語3)と要求数のPrompt」だけ(P7/W3。条件文はProduction Prompt 2/2-Vから条件を変えず、件数・区分の文言だけ置換)。
- 現行方式(current): er119_kp_candidates_01.generate_candidates をProduction既定のまま実行(call1=Prompt 2で3件 + call2=Prompt 2-Vで最大5件)。
- Trial方式(p7w3): call1=P7(フレーズ最大7件) → call2=W3(単語最大3件。P7のGate通過句を「すでに選ばれた表現」として入力)。
  call1相当をselect_fn、call2相当をvocab_call_fn(make_call_fn)としてgenerate_candidatesへ注入し、以降(Gate・canonicalization・RQA)はProductionのまま。
副作用の隔離: ネットワークtelemetry(sc.KP_BACKEND_TELEMETRY_PATH)を出力dirへ向け、cost loggerも出力dirへ向ける。既存run dirには書かない。
サブコマンド: baseline / run-one / run / judge / report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
from typing import Any, Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "docs", "research", "KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01")
MGMT_ID = "KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01"

LEVELS = {"a2": "Standard", "b1b": "Advanced"}
FORMAL_X = "er019_output/family_x_audio_production_wiring_01"
Z_RUN = "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01"
ARTICLES = {
    "ai_island_temple": {"family": "X", "ja": "AIの仮想の島", "src": "er019_output/ai_island_temple/run_ai_01/{lv}/article.md",
                         "formal_run": f"{FORMAL_X}/ai_island_temple__run_ai_01"},
    "uk_train_speaker_playback": {"family": "X", "ja": "英国の電車マナー", "src": "er019_output/uk_train_speaker_playback/run_nws_02/{lv}/article.md",
                                  "formal_run": f"{FORMAL_X}/uk_train_speaker_playback__run_nws_02"},
    "monkeys_paw": {"family": "Z", "ja": "猿の手", "src": Z_RUN + "/writer/{zf}", "formal_run": Z_RUN},
}
Z_LEVEL_FILE = {"a2": "std.md", "b1b": "r2.md"}   # er062_family_z_writer_01.level_text_path

JUDGE_MODEL = "gpt-6.1-sol"
P7_MAX = 7
W3_MAX = 3


# ============================================================
# Prompt(P7 / W3)。条件文はProduction Prompt 2(er105.PROMPT_2_TEXT)から、区分・件数の文言だけを置換して作る。
# ============================================================
def _build_prompts():
    import er105_kp_fulltext_selector_01 as ft
    base = ft.PROMPT_2_TEXT
    head2 = "以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。\n"
    cond6 = "6. **3件選定**：条件を満たす候補から3件選ぶ。適切な候補が不足する場合のみ3件未満とし、数合わせはしない。\n"
    assert head2 in base and cond6 in base
    p7_head = ("以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム(2語以上の連続した語句)を、"
               "学習価値の高い順に**最大7つ**選んでください(単語単体は別の枠で選ぶため、ここでは選びません)。\n")
    p7_cond6 = ("6. **最大7件・順位付け**：条件を満たす候補から、学習価値の高い順に最大7件を選び、1位から順に並べる。"
                "互いに同一、または一方がもう一方を含む類似の表現を重ねて選ばない。"
                "適切な候補が不足する場合のみ7件未満とし、数合わせはしない。"
                "各候補に、選んだ理由を日本語で1文(40字以内)添える。\n")
    p7 = base.replace(head2, p7_head, 1).replace(cond6, p7_cond6, 1)
    w3 = (
        "以下の記事から、英語上級者が学ぶ価値のある**単語単体(1語)**を、学習価値の高い順に**最大3つ**選んでください"
        "(すでに選ばれたフレーズ・表現は、記事本文の後ろに示します)。\n"
        "\n"
        "以下の順序で処理し、上位条件を優先してください。\n"
        "\n"
        "1. **本文一致（絶対条件）**：本文中に実在する単語だけを、本文に現れる形のまま抜き出す。変更・言い換え・追加・創作は禁止。\n"
        "2. **1語（絶対条件）**：スペースを含まない1語だけを出力する。2語以上は出力禁止。\n"
        "3. **単語単体の学習価値（必須）**：その単語そのものを学ぶ価値があること。意味の明確さ・他の文脈での汎用性・難易度を評価して選ぶ。"
        "固有名詞・数字・この記事だけでしか使えない語は避ける。\n"
        "4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙を優先する。\n"
        "5. **易しい語の除外**：基本語や、上級者なら知っている易しい語は除外する。\n"
        "6. **重複の回避**：すでに選ばれたフレーズ・表現に含まれる語は、フレーズ側で学べるため選ばない。\n"
        "7. **最大3件・順位付け**：条件を満たす候補から、学習価値の高い順に最大3件を選び、1位から順に並べる。"
        "適切な候補が不足する場合のみ3件未満とし、数合わせはしない(簡単すぎる語や不自然な語で3件に揃えない)。"
        "各候補に、選んだ理由を日本語で1文(40字以内)添える。\n"
        "\n"
        "**出力直前に各候補を本文と照合し、改変がないこと、1語であることを再確認してください。語数も併記してください。**")
    return p7, w3


P7_TEXT, W3_TEXT = _build_prompts()
P7_SHA = hashlib.sha256(P7_TEXT.encode("utf-8")).hexdigest()
W3_SHA = hashlib.sha256(W3_TEXT.encode("utf-8")).hexdigest()


def build_p7_message(text: str) -> str:
    import er105_kp_fulltext_selector_01 as ft
    return P7_TEXT + ft.BODY_DELIMITER + text


def build_w3_message(text: str, already: list) -> str:
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_prompt_2v_01 as p2v
    return W3_TEXT + ft.BODY_DELIMITER + text + p2v.ALREADY_DELIMITER + "\n".join(f"- {p}" for p in already)


def parse_already(msg: str) -> list:
    """Production(run_vocab_selection)が組んだ2-V messageから『すでに選ばれた表現』を取り出す(W3 messageの入力に使う)。"""
    import er119_kp_prompt_2v_01 as p2v
    tail = msg.split(p2v.ALREADY_DELIMITER, 1)[1]
    return [ln[2:] for ln in tail.split("\n") if ln.startswith("- ")]


# ============================================================
# 単語/フレーズの判定基準(事前固定)
# ============================================================
def classify_kind(used_form: str) -> str:
    """空白を含まない1トークン(ハイフン複合語を含む)=word。空白で区切られる2語以上(句動詞・コロケーション・複合語[空白区切り])=phrase。"""
    return "word" if len((used_form or "").split()) == 1 else "phrase"


# ============================================================
# 本文の取得(Production候補生成が受け取るのと同じ本文)
# ============================================================
def load_text(article: str, lv: str) -> str:
    a = ARTICLES[article]
    if a["family"] == "X":
        with open(os.path.join(ROOT, a["src"].format(lv=lv)), encoding="utf-8") as f:
            return f.read()
    import er026_family_z_fiction_production_runner_01 as z
    m = z._m()
    return z.canonical_article_text(m.w62.rd(os.path.join(ROOT, a["src"].format(zf=Z_LEVEL_FILE[lv]))))


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# Gate(選定段): Production primitivesのみ使用。run_vocab_selection(er119)の選定gateと同一ロジックで、上限件数だけを引数化
# ============================================================
def selection_gate(selected: list, units: list, already_keys: list, ex_keys: dict, cap: int, origin: str) -> dict:
    import er105_kp_fulltext_selector_01 as ft
    import er108_kp_cmu_lexicon_gate_01 as cmu
    import er119_kp_candidates_01 as kcand
    v = ft.validate_and_resolve([{"phrase": s["phrase"], "declared_word_count": s["declared_word_count"]} for s in selected], units)
    item_reasons = {ir["index"]: ir["reasons"] for ir in v["item_reasons"]}
    kept, dropped = [], []
    for rec in v["resolved"]:
        idx, phrase = rec["index"], rec["phrase"]
        pk = ft.phrase_key(phrase)
        reasons = list(item_reasons.get(idx) or [])
        stage = "validate" if reasons else None
        if not reasons and any(pk == k or kcand._containment(pk, k) for k in already_keys):
            reasons, stage = ["前記の選定済み表現と同一または包含関係(重複)"], "duplicate_of_top3"
        if not reasons and pk in ex_keys:
            e = ex_keys[pk]
            reasons, stage = ["除外指定の語句(" + (" / ".join(e.get("reasons") or ["不適合"])) + ")"], e.get("source") or "excluded"
        if not reasons:
            cr = cmu.reasons_for_phrase(phrase)
            if cr:
                reasons, stage = cr, "cmu"
        if reasons:
            dropped.append({"raw_rank": idx + 1, "phrase": phrase, "stage": stage, "reasons": reasons, "origin": origin})
        else:
            kept.append({"resolved": rec, "reason_ja": selected[idx]["reason_ja"], "raw_rank": idx + 1})
    if len(kept) > cap:
        for k in kept[cap:]:
            dropped.append({"raw_rank": k["raw_rank"], "phrase": k["resolved"]["phrase"], "stage": "overflow",
                            "reasons": [f"最大{cap}件を超過(下位のため除外)"], "origin": origin})
        kept = kept[:cap]
    return {"kept": kept, "dropped": dropped}


class TrialState:
    """P7/W3のraw応答・件数・p7段のGate除外を保持(generate_candidatesのdoc外の記録)。"""

    def __init__(self):
        self.p7_raw, self.p7_model, self.p7_calls, self.p7_returned = None, None, 0, None
        self.p7_dropped, self.p7_reason = [], {}
        self.w3_raw, self.w3_model, self.w3_calls, self.w3_returned, self.w3_over_request = None, None, 0, None, 0
        self.messages = {}


def make_p7_select_fn(text: str, state: TrialState, units: list, call_factory=None):
    """generate_candidatesのselect_fn(call1相当)。P7(最大7件)を呼び、Production gate primitivesを適用して original_items を返す。"""
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_prompt_2v_01 as p2v

    def select_fn(text_, work, article_id, source_level, process=None, diagnostic_note=None, kp_backend=None, **kw):
        os.makedirs(work, exist_ok=True)
        model = ft.resolve_model(process)
        ex_keys = {ft.phrase_key(e["phrase"]): e for e in (kw.get("excluded_phrases") or [])}
        msg = build_p7_message(text)
        state.messages["p7"] = {"sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(), "prompt_sha256": P7_SHA}
        with open(f"{work}/p7_prompt.txt", "w", encoding="utf-8") as f:
            f.write(msg)
        attempts = []
        for attempt in range(1, ft.MAX_ATTEMPTS + 1):
            fn = call_factory(msg, model) if call_factory else p2v.make_vocab_selector_fn(msg, model=model)
            state.p7_calls += 1
            try:
                raw, model_id, response_id = fn()
            except ft.FulltextSelectionError as e:
                if isinstance(e, ft.ModelMismatchError):
                    attempts.append({"attempt": attempt, "error": str(e)})
                    continue
                raise
            except Exception as e:   # noqa: BLE001
                attempts.append({"attempt": attempt, "error": f"{type(e).__name__}: {e}"})
                time.sleep(2)
                continue
            try:
                selected = p2v.parse_selection(raw)
            except ft.ParseError as e:
                attempts.append({"attempt": attempt, "error": str(e), "raw": raw})
                continue
            state.p7_raw, state.p7_model, state.p7_returned = raw, model_id, len(selected)
            g = selection_gate(selected, units, [], ex_keys, P7_MAX, "p7")
            state.p7_dropped = g["dropped"]
            if not g["kept"]:
                attempts.append({"attempt": attempt, "error": "P7: Gate通過0件"})
                continue
            items = ft.build_original_items([k["resolved"] for k in g["kept"]])
            for k, it in zip(g["kept"], items):
                state.p7_reason[it["display_phrase"]] = {"reason_ja": k["reason_ja"], "raw_rank": k["raw_rank"]}
            with open(f"{work}/p7_raw.json", "w", encoding="utf-8") as f:
                json.dump({"raw": json.loads(raw), "model": model_id, "response_id": response_id, "dropped": g["dropped"]}, f, ensure_ascii=False, indent=2)
            return {"status": ft.STATUS_PASS, "original_items": items, "model_id": model_id, "response_id": response_id,
                    "parsed": {"items": items}, "kp_backend_used": "dev_p7", "kp_attempts": attempt}
        return {"status": ft.STATUS_INVALID, "original_items": None, "model_id": None, "attempts": attempts}
    return select_fn


def make_w3_call_fn(text: str, state: TrialState, process: str, call_factory=None):
    """generate_candidatesのvocab_call_fn(make_call_fn)。run_vocab_selection(Production)が組んだ2-V messageから『すでに選ばれた表現』を取り、
    W3 messageで単語単体を最大3件要求する。以降のitem単位gate(validate/重複包含/Human NG/CMU)はrun_vocab_selection(Production)がそのまま適用。"""
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_prompt_2v_01 as p2v

    def make_call_fn(prod_msg: str):
        already = parse_already(prod_msg)
        msg = build_w3_message(text, already)
        state.messages["w3"] = {"sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(), "prompt_sha256": W3_SHA, "already": already}
        model = ft.resolve_model(process)
        inner = call_factory(msg, model) if call_factory else p2v.make_vocab_selector_fn(msg, model=model)

        def fn():
            state.w3_calls += 1
            raw, model_id, response_id = inner()
            doc = json.loads(raw)
            n = len(doc.get("items") or [])
            state.w3_returned = n
            state.w3_model = model_id
            if n > W3_MAX:   # 要求は最大3件。超過分は下位から切って記録(Production gateの上限5を3へ揃える)
                state.w3_over_request = n - W3_MAX
                doc["items"] = doc["items"][:W3_MAX]
                raw = json.dumps(doc, ensure_ascii=False)
            state.w3_raw = raw
            return raw, model_id, response_id
        return fn
    return make_call_fn


# ============================================================
# run-one(1 level × 1 method × 1 rep)。子processで実行(cost loggerはprocess単位)
# ============================================================
def run_one(args) -> int:
    import er005_cost_logger as cl
    import er003_v1_n3_01_scaffold_generate as sc
    import er003_key_words_gloss_alignment as ga
    import er119_kp_candidates_01 as kcand
    import er105_kp_fulltext_selector_01 as ft

    article, lv, method, rep = args.article, args.level, args.method, args.rep
    tag = f"{article}__{lv}__{method}__r{rep}"
    run_dir = os.path.join(OUT, "runs", tag)
    os.makedirs(run_dir, exist_ok=True)
    usage_path = os.path.join(run_dir, "usage_log.jsonl")
    cl.install(usage_path)
    sc.KP_BACKEND_TELEMETRY_PATH = os.path.join(run_dir, "kp_backend_telemetry.jsonl")   # 共有telemetry(er030_output)へ書かない
    ga.preflight()
    text = load_text(article, lv)
    process = "A2_SUPPORT" if lv == "a2" else "B1_SUPPORT"
    source_level = "A2" if lv == "a2" else "B1"
    family = ARTICLES[article]["family"]
    src_fn = kcand.make_z_src_fn(text, lv) if family == "Z" else None
    person_fn = None
    if family == "Z" and ga.flag_enabled():
        import er006_model_routing_contract_01 as routing
        model = routing.require_model(process, routing.SUPPORT_MODEL)
        person_fn = kcand.make_person_repair_fn(text, (lambda msg: ga.make_alignment_fn(msg, model=model)),
                                                f"{run_dir}/gloss_person_repair_candidates", tag)
    import er030_key_phrase_db_hybrid_core_01 as core
    units = core.build_sentence_units(text)
    state = TrialState()
    kw: dict[str, Any] = dict(process=process, src_fn=src_fn, person_repair_fn=person_fn)
    t0 = time.time()
    if method == "p7w3":
        kw.update(max_outer=1, select_fn=make_p7_select_fn(text, state, units), vocab_call_fn=make_w3_call_fn(text, state, process))
    elif method != "current":
        raise SystemExit("method must be current|p7w3")
    article_id = f"kptrial_{tag}"
    with cl.logging_context(article_id, f"kp_trial_{method}"):
        res = kcand.generate_candidates(text, run_dir, article_id, source_level, lv, 1, [], **kw)
    elapsed = round(time.time() - t0, 1)
    out = {"tag": tag, "article": article, "level": lv, "method": method, "rep": rep, "text_sha256": text_sha(text), "elapsed_sec": elapsed,
           "ok": res.get("ok"), "status": res.get("status"),
           "p7_prompt_sha256": P7_SHA, "w3_prompt_sha256": W3_SHA, "ft_prompt2_sha256": ft.PROMPT_2_SHA256}
    if method == "p7w3":
        out["state"] = {"p7_calls": state.p7_calls, "p7_returned": state.p7_returned, "p7_model": state.p7_model,
                        "p7_dropped": state.p7_dropped, "p7_reason": state.p7_reason, "p7_raw": state.p7_raw,
                        "w3_calls": state.w3_calls, "w3_returned": state.w3_returned, "w3_model": state.w3_model,
                        "w3_over_request": state.w3_over_request, "w3_raw": state.w3_raw, "messages": state.messages}
    if res.get("ok"):
        out["doc"] = res["doc"]
    else:
        out["outer_retry_log"] = res.get("outer_retry_log")
    with open(os.path.join(run_dir, "trial_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({"tag": tag, "ok": out["ok"], "status": out["status"], "elapsed": elapsed}, ensure_ascii=False))
    return 0 if out["ok"] else 3


# ============================================================
# cost集計(raw usage log → JPY。pricing_snapshot × USD_JPY=160、daily_dev_cost_01と同一換算)
# ============================================================
def cost_of_log(path: str) -> dict:
    sys.path.insert(0, os.path.join(ROOT, "docs", "pm", "tools"))
    import daily_dev_cost_01 as d
    prices = d.load_prices(ROOT)
    n, usd, unpriced, tin, tout = 0, 0.0, [], 0, 0
    models = {}
    if not os.path.exists(path):
        return {"calls": 0, "usd": 0.0, "jpy": 0.0}
    for ln in open(path, encoding="utf-8"):
        if not ln.strip():
            continue
        r = json.loads(ln)
        n += 1
        u, why = d.price_record(r, prices)
        if u is None:
            unpriced.append(why)
        else:
            usd += u
        tin += r.get("input_tokens") or 0
        tout += r.get("output_tokens") or 0
        models[r.get("model_id")] = models.get(r.get("model_id"), 0) + 1
    return {"calls": n, "usd": round(usd, 6), "jpy": round(usd * d.USD_JPY, 3), "input_tokens": tin, "output_tokens": tout,
            "models": models, "unpriced": unpriced}


# ============================================================
# 現行方式baseline(API 0): 既存成果物の棚卸し
# ============================================================
def summarize_doc(doc: dict) -> dict:
    cands = doc.get("candidates") or []
    dropped = doc.get("dropped") or []
    kinds = [classify_kind(c.get("used_form") or "") for c in cands]
    return {"n_final": len(cands), "n_phrase": kinds.count("phrase"), "n_word": kinds.count("word"), "n_dropped": len(dropped),
            "n_returned_total": len(cands) + len([d for d in dropped if d.get("stage") not in ("canonicalization", "cmu_post_canon", "symbol", "src_d1")]) +
            len([d for d in dropped if d.get("stage") in ("canonicalization", "cmu_post_canon", "symbol", "src_d1")])}


def cand_rows(doc: dict) -> list:
    rows = []
    for c in doc.get("candidates") or []:
        rows.append({"ai_rank": c.get("ai_rank"), "origin": c.get("origin"), "raw_rank": c.get("raw_rank"), "selection_phrase": c.get("selection_phrase"),
                     "used_form": c.get("used_form"), "kind": classify_kind(c.get("used_form") or ""), "japanese_gloss": c.get("japanese_gloss"),
                     "source_sentence": c.get("source_sentence"), "reason_ja": c.get("reason_ja"), "word_count": c.get("word_count"),
                     "auto_eligible": c.get("auto_eligible"), "flags": c.get("flags")})
    return rows


def cmd_baseline(args) -> int:
    out = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind_rule": classify_kind.__doc__, "levels": {}}
    import er105_kp_fulltext_selector_01 as ft
    for article, a in ARTICLES.items():
        for lv in LEVELS:
            key = f"{article}:{lv}"
            text = load_text(article, lv)
            rec = {"article": article, "ja": a["ja"], "family": a["family"], "level": lv, "level_name": LEVELS[lv], "text_sha256": text_sha(text),
                   "text_words": len(text.split()), "formal_run": a["formal_run"]}
            kd = os.path.join(ROOT, a["formal_run"], lv, "key_phrases") if a["family"] == "X" else os.path.join(ROOT, a["formal_run"], "key_phrases", lv)
            cj = os.path.join(kd, "kp_candidates.json")
            if os.path.exists(cj):   # 8候補方式(現行)の既存成果物
                doc = json.load(open(cj, encoding="utf-8"))
                sp = os.path.join(kd, "kp_candidates", "round_1", "work", "keywords_selector_prompt.txt")
                if os.path.exists(sp):
                    body = open(sp, encoding="utf-8").read().split(ft.BODY_DELIMITER, 1)[1].split(ft.NOTE_DELIMITER, 1)[0]
                    rec["prompt_body_equals_text"] = body == text
                rec["current_source"] = "reuse(既存kp_candidates.json)"
                rec["current"] = {"summary": summarize_doc(doc), "candidates": cand_rows(doc), "dropped": doc.get("dropped"),
                                  "model_id": doc.get("model_id"), "outer_attempts": doc.get("outer_attempts"), "shortfall": doc.get("shortfall"),
                                  "redundancy_qa": doc.get("redundancy_qa")}
                rec["current"]["requested"] = 8
            else:
                rec["current_source"] = "NO_EXISTING_8CAND_RUN(現行方式のfresh再実行が必要)"
            # 参考: 正式run(3KP時代)の確定KP
            kc = os.path.join(kd, "keywords_canonicalized.json")
            if os.path.exists(kc):
                d = json.load(open(kc, encoding="utf-8"))
                rec["formal_3kp_reference"] = [{"display_phrase": i.get("display_phrase"), "used_form": i.get("used_form") or i.get("key_phrase"),
                                                "japanese_gloss": i.get("japanese_gloss")} for i in d.get("items", [])]
            sp2 = os.path.join(kd, "keywords_selector_prompt.txt")
            if os.path.exists(sp2) and "prompt_body_equals_text" not in rec:
                body = open(sp2, encoding="utf-8").read().split(ft.BODY_DELIMITER, 1)[1].split(ft.NOTE_DELIMITER, 1)[0]
                rec["formal_3kp_prompt_body_equals_text"] = body == text
            out["levels"][key] = rec
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    for k, v in out["levels"].items():
        print(k, v["current_source"][:30], v.get("current", {}).get("summary"), v.get("prompt_body_equals_text"), v.get("formal_3kp_prompt_body_equals_text"))
    return 0


# ============================================================
# run: 子processを並列起動(自動retryなし。失敗はそのまま記録)
# ============================================================
def cmd_run(args) -> int:
    jobs = []
    for spec in args.levels.split(","):
        article, lv = spec.split(":")
        for method in args.methods.split(","):
            reps = args.repeats if method == "p7w3" else args.current_repeats
            for rep in range(1, reps + 1):
                tag = f"{article}__{lv}__{method}__r{rep}"
                if os.path.exists(os.path.join(OUT, "runs", tag, "trial_result.json")):
                    print("skip(既に結果あり。再実行しない):", tag)
                    continue
                jobs.append((article, lv, method, rep, tag))
    print(f"{len(jobs)} jobs, parallel={args.parallel}")
    procs, results = [], {}
    pending = list(jobs)
    running = []
    while pending or running:
        while pending and len(running) < args.parallel:
            article, lv, method, rep, tag = pending.pop(0)
            logp = os.path.join(OUT, "runs", f"{tag}.console.txt")
            os.makedirs(os.path.dirname(logp), exist_ok=True)
            fh = open(logp, "w", encoding="utf-8")
            p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "run-one", "--article", article, "--level", lv, "--method", method,
                                  "--rep", str(rep)], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONUTF8="1"))
            running.append((p, tag, fh))
        time.sleep(2)
        for item in list(running):
            p, tag, fh = item
            if p.poll() is not None:
                fh.close()
                results[tag] = p.returncode
                running.remove(item)
                print("done", tag, "rc=", p.returncode, flush=True)
    json.dump(results, open(args.out, "w", encoding="utf-8"), indent=2)
    return 0 if all(v == 0 for v in results.values()) else 3


# ============================================================
# collect: 全runの結果を trial_runs_01.json / gate_results_01.json に集約(件数・call数・費用はusage log出典)
# ============================================================
def _stage_counts(dropped: list) -> dict:
    c: dict = {}
    for d in dropped:
        c[d.get("stage")] = c.get(d.get("stage"), 0) + 1
    return c


def collect_runs() -> dict:
    rd = os.path.join(OUT, "runs")
    runs = {}
    for tag in sorted(os.listdir(rd)):
        rp = os.path.join(rd, tag, "trial_result.json")
        if not os.path.exists(rp):
            continue
        r = json.load(open(rp, encoding="utf-8"))
        cost = cost_of_log(os.path.join(rd, tag, "usage_log.jsonl"))
        doc = r.get("doc") or {}
        cands = doc.get("candidates") or []
        dropped_doc = doc.get("dropped") or []
        st = r.get("state") or {}
        p7_dropped = st.get("p7_dropped") or []
        all_dropped = list(p7_dropped) + list(dropped_doc)
        if r["method"] == "p7w3":
            requested = {"phrase": P7_MAX, "word": W3_MAX, "total": P7_MAX + W3_MAX}
            returned = {"p7": st.get("p7_returned"), "w3": st.get("w3_returned"), "total": (st.get("p7_returned") or 0) + (st.get("w3_returned") or 0)}
            calls = {"p7": st.get("p7_calls"), "w3": st.get("w3_calls")}
        else:
            requested = {"call1": 3, "call2": 5, "total": 8}
            returned = {"total": len(cands) + len(dropped_doc)}
            calls = {}
        kinds = [classify_kind(c.get("used_form") or "") for c in cands]
        n_auto = sum(1 for c in cands if c.get("auto_eligible"))
        gate_dropped = [d for d in all_dropped if d.get("stage") not in ("human_ng", "overflow", "duplicate_of_top3", "excluded")]
        runs[tag] = {
            "tag": tag, "article": r["article"], "level": r["level"], "method": r["method"], "rep": r["rep"], "ok": r["ok"],
            "text_sha256": r["text_sha256"], "requested": requested, "returned": returned, "calls_p7w3": calls,
            "n_gate_dropped_total": len(all_dropped), "drop_stage_counts": _stage_counts(all_dropped),
            "n_final": len(cands), "n_phrase": kinds.count("phrase"), "n_word": kinds.count("word"), "n_auto_eligible": n_auto,
            "prod_outer_retry_would_fire": bool(n_auto < 3 and gate_dropped), "over_8": len(cands) > 8,
            "w3_over_request": st.get("w3_over_request"), "p7_single_words_returned": None,
            "cost": cost, "elapsed_sec": r["elapsed_sec"], "outer_attempts": doc.get("outer_attempts"),
            "redundancy_qa": doc.get("redundancy_qa"), "model_id": doc.get("model_id"),
            "candidates": cand_rows(doc), "dropped": all_dropped,
        }
        if r["method"] == "p7w3" and st.get("p7_raw"):
            try:
                items = json.loads(st["p7_raw"])["items"]
                runs[tag]["p7_single_words_returned"] = sum(1 for i in items if len(i["phrase"].split()) == 1)
            except Exception:   # noqa: BLE001
                pass
    return runs


def cmd_collect(args) -> int:
    runs = collect_runs()
    total = {"calls": 0, "jpy": 0.0}
    for r in runs.values():
        total["calls"] += r["cost"]["calls"]
        total["jpy"] += r["cost"]["jpy"]
    total["jpy"] = round(total["jpy"], 3)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "n_runs": len(runs), "total_run_cost": total, "runs": runs}, f, ensure_ascii=False, indent=1)
    gate = {tag: {"drop_stage_counts": r["drop_stage_counts"], "dropped": r["dropped"]} for tag, r in runs.items()}
    with open(args.gate_out, "w", encoding="utf-8") as f:
        json.dump(gate, f, ensure_ascii=False, indent=1)
    print(json.dumps({"n_runs": len(runs), "total": total}, ensure_ascii=False))
    return 0


# ============================================================
# judge: level単位で 現行候補 + Trial候補(rep1/rep2の和集合) を匿名化・順序シャッフルし、同一ルーブリックで1 call判定
# ============================================================
JUDGE_SCHEMA = {
    "name": "kp_candidate_judge", "strict": True,
    "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "natural", "general", "level_fit", "value", "verdict", "overlap_with", "note_ja"],
        "properties": {"id": {"type": "string"}, "natural": {"type": "boolean"}, "general": {"type": "boolean"},
                       "level_fit": {"type": "string", "enum": ["good", "too_easy", "too_hard"]}, "value": {"type": "integer"},
                       "verdict": {"type": "string", "enum": ["Y", "B", "N"]}, "overlap_with": {"type": "array", "items": {"type": "string"}},
                       "note_ja": {"type": "string"}}}}}},
}

JUDGE_INSTRUCTION = (
    "あなたは英語学習コンテンツの編集者です。下の記事(英語)から選ばれた『Key Phrase候補』を、同一ルーブリックで独立に評価してください。\n"
    "対象の学習者: {level_desc}。\n\n"
    "各候補について次を判定します。\n"
    "- natural: 単独で自然に成立する語句で、切り出しが不自然・文脈依存でない\n"
    "- general: 他の文脈でも再利用でき、記事固有の固有名詞・数値・物名でない\n"
    "- level_fit: 学ぶ価値がある(少し上の語彙)なら good、易しすぎる基本語なら too_easy、極端に難しい/特殊なら too_hard\n"
    "- value: 学習価値 1(低)〜5(高)\n"
    "- overlap_with: 学習ポイントが実質同じ(語幹・包含・同概念)の別候補のid(なければ空配列)\n"
    "- verdict: natural・general・level_fitが全て満たされるなら Y、1項目だけ境界なら B、明確に不満足なら N\n"
    "候補の出所や順序は無関係です。数合わせのために入れられた候補(易しすぎる語・不自然な語・重複)は N にしてください。note_jaは日本語で30字以内。\n")


def _level_desc(lv: str) -> str:
    return ("Standard(A2〜B1相当の英語学習者向け。本文は平易に書かれている)" if lv == "a2"
            else "Advanced(B1〜B2相当の英語学習者向け)")


def cmd_judge(args) -> int:
    import er005_cost_logger as cl
    runs = collect_runs()
    base = json.load(open(os.path.join(OUT, "current_baseline_01.json"), encoding="utf-8"))
    usage_path = os.path.join(OUT, "judge", "usage_log.jsonl")
    os.makedirs(os.path.dirname(usage_path), exist_ok=True)
    cl.install(usage_path)
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    client = OpenAI()
    results = {}
    for article in ARTICLES:
        for lv in LEVELS:
            key = f"{article}:{lv}"
            outp = os.path.join(OUT, "judge", f"judge_{article}__{lv}.json")
            if os.path.exists(outp):
                print("skip(既存)", key)
                continue
            pool: dict = {}   # used_form.lower() -> {"used_form","gloss","sentence","sources":set}

            def add(row, src):
                k = (row["used_form"] or "").lower()
                e = pool.setdefault(k, {"used_form": row["used_form"], "gloss": row.get("japanese_gloss"), "sentence": row.get("source_sentence"), "sources": set()})
                e["sources"].add(src)
            b = base["levels"][key]
            if b.get("current"):
                cur_rows = b["current"]["candidates"]
            else:
                rr = runs.get(f"{article}__{lv}__current__r1")
                cur_rows = rr["candidates"] if rr else []
            for r in cur_rows:
                add(r, "current")
            for rep in (1, 2):
                rr = runs.get(f"{article}__{lv}__p7w3__r{rep}")
                for r in (rr["candidates"] if rr else []):
                    add(r, f"p7w3_r{rep}")
            items = list(pool.values())
            rnd = random.Random(f"{MGMT_ID}:{key}")
            rnd.shuffle(items)
            ids = {}
            lines = []
            for n, it in enumerate(items, start=1):
                cid = f"C{n:02d}"
                ids[cid] = it
                lines.append(f"- {cid}: {it['used_form']} / 意味: {it['gloss']} / 出典文: {it['sentence']}")
            text = load_text(article, lv)
            msg = (JUDGE_INSTRUCTION.format(level_desc=_level_desc(lv)) + "\n【記事本文】\n" + text + "\n\n【候補一覧(" + str(len(items)) + "件)】\n" + "\n".join(lines))
            with cl.logging_context(f"kpjudge_{article}_{lv}", "kp_judge"):
                resp = client.responses.create(model=JUDGE_MODEL, reasoning={"effort": "low"},
                                               text={"format": {"type": "json_schema", **JUDGE_SCHEMA}}, input=[{"role": "user", "content": msg}])
            judged = json.loads(resp.output_text)["items"]
            rec = {"key": key, "model_requested": JUDGE_MODEL, "model_id": resp.model, "response_id": resp.id, "n_candidates": len(items),
                   "message_sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(), "message": msg,
                   "candidates": {cid: {"used_form": it["used_form"], "sources": sorted(it["sources"])} for cid, it in ids.items()}, "judged": judged}
            with open(outp, "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            results[key] = len(judged)
            print("judged", key, len(items), len(judged), flush=True)
    print(json.dumps(results))
    return 0


# ============================================================
# report: RESULT_01.md(比較表+候補全文)/ 集計json を生成(判断文章は含まない。COMPARISON/STATUSは別途記述)
# ============================================================
def _load_judge(article: str, lv: str) -> dict:
    p = os.path.join(OUT, "judge", f"judge_{article}__{lv}.json")
    if not os.path.exists(p):
        return {}
    rec = json.load(open(p, encoding="utf-8"))
    by_form = {}
    for j in rec["judged"]:
        form = rec["candidates"][j["id"]]["used_form"]
        by_form[form.lower()] = dict(j, used_form=form, sources=rec["candidates"][j["id"]]["sources"])
    return by_form


def _verdict_counts(rows: list, own: dict, judge: dict) -> dict:
    c = {"own": {"Y": 0, "B": 0, "N": 0}, "judge": {"Y": 0, "B": 0, "N": 0}, "both_Y": 0, "own_Y_phrase": 0, "own_Y_word": 0}
    for r in rows:
        k = (r["used_form"] or "").lower()
        ov = (own.get(k) or {}).get("verdict")
        jv = (judge.get(k) or {}).get("verdict")
        if ov:
            c["own"][ov] += 1
            if ov == "Y":
                c["own_Y_phrase" if r["kind"] == "phrase" else "own_Y_word"] += 1
        if jv:
            c["judge"][jv] += 1
        if ov == "Y" and jv == "Y":
            c["both_Y"] += 1
    return c


def cmd_report(args) -> int:
    runs = collect_runs()
    base = json.load(open(os.path.join(OUT, "current_baseline_01.json"), encoding="utf-8"))
    own_all = json.load(open(os.path.join(OUT, "own_rubric_01.json"), encoding="utf-8"))
    fresh_cur = [r for r in runs.values() if r["method"] == "current"]
    mean_cur_cost = round(sum(r["cost"]["jpy"] for r in fresh_cur) / max(1, len(fresh_cur)), 2)
    L = ["# RESULT_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26)", "",
         "自動生成(`er124_kp_phrase_word_trial_01.py report`)。現行=Production既定(call1 Prompt 2=3件+call2 Prompt 2-V=最大5件)、"
         "Trial=P7(フレーズ最大7)→W3(単語最大3)。Gate=Production関数同一適用(DESIGN_01 §6)。判定: own=自ルーブリック Y/B/N、judge=gpt-6.1-sol(匿名・シャッフル)。", ""]
    summary = {}
    for article, a in ARTICLES.items():
        for lv in LEVELS:
            key = f"{article}:{lv}"
            own = {k.lower(): v for k, v in own_all.get(key, {}).items()}
            judge = _load_judge(article, lv)
            b = base["levels"][key]
            if b.get("current"):
                cur = {"source": "reuse(既存kp_candidates.json、run_ai_01)", "rows": b["current"]["candidates"], "dropped": b["current"]["dropped"] or [],
                       "cost": None, "returned": b["current"]["summary"]["n_final"] + len(b["current"]["dropped"] or [])}
            else:
                rr = runs[f"{article}__{lv}__current__r1"]
                cur = {"source": "fresh(DEV実行、Production既定のgenerate_candidates)", "rows": rr["candidates"], "dropped": rr["dropped"],
                       "cost": rr["cost"], "returned": rr["returned"]["total"]}
            tr = [runs.get(f"{article}__{lv}__p7w3__r{rep}") for rep in (1, 2)]
            cc = _verdict_counts(cur["rows"], own, judge)
            L += [f"## {a['ja']} ({a['family']}) / {LEVELS[lv]} ({lv})  本文sha256={b['text_sha256'][:12]} 語数={b['text_words']}", "",
                  f"現行の出所: {cur['source']}", "",
                  "| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |", "|---|---|---|---|"]
            def cell(f):
                return [f(t) if t else "-" for t in tr]
            rows = [
                ("要求件数", "最大8(3+5)", *cell(lambda t: "フレーズ7＋単語3(計10)")),
                ("AI返答件数", str(cur["returned"]), *cell(lambda t: f"P7 {t['returned']['p7']}＋W3 {t['returned']['w3']}＝{t['returned']['total']}")),
                ("Gate除外件数", str(len(cur["dropped"])), *cell(lambda t: f"{t['n_gate_dropped_total']} {t['drop_stage_counts'] or ''}")),
                ("最終候補件数", str(len(cur["rows"])), *cell(lambda t: str(t["n_final"]))),
                ("フレーズ件数", str(sum(1 for r in cur["rows"] if r["kind"] == "phrase")), *cell(lambda t: str(t["n_phrase"]))),
                ("単語件数", str(sum(1 for r in cur["rows"] if r["kind"] == "word")), *cell(lambda t: str(t["n_word"]))),
            ]
            tc = [(_verdict_counts(t["candidates"], own, judge) if t else None) for t in tr]
            def vtxt(c):
                return f"自Y{c['own']['Y']}/B{c['own']['B']}/N{c['own']['N']}・judge Y{c['judge']['Y']}/B{c['judge']['B']}/N{c['judge']['N']}・両者Y{c['both_Y']}"
            rows.append(("学習価値・多様性(Y/B/N)", vtxt(cc), *[vtxt(c) if c else "-" for c in tc]))
            rows.append(("生成コスト", (f"実績 ¥{cur['cost']['jpy']}({cur['cost']['calls']} call)" if cur["cost"] else f"推計 約¥{mean_cur_cost}(他4 levelのfresh現行平均)"),
                         *cell(lambda t: f"実績 ¥{t['cost']['jpy']}({t['cost']['calls']} call)")))
            for r in rows:
                L.append("| " + " | ".join(str(x) for x in r) + " |")
            L.append("")
            def listing(title, cand_rows, dropped, extra=""):
                out = [f"### {title}", "", "| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |", "|---|---|---|---|---|---|---|---|---|"]
                for r in cand_rows:
                    k = (r["used_form"] or "").lower()
                    ov = (own.get(k) or {}).get("verdict", "-")
                    on = (own.get(k) or {}).get("note", "")
                    jv = (judge.get(k) or {}).get("verdict", "-")
                    gate = "PASS(auto)" if r.get("auto_eligible") else "PASS(flag)"
                    out.append(f"| {r.get('ai_rank')} | {'単語' if r['kind'] == 'word' else 'フレーズ'}({r.get('origin')}#{r.get('raw_rank')}) | {r['used_form']} | {r.get('japanese_gloss')} | "
                               f"{(r.get('source_sentence') or '')} | {r.get('reason_ja') or ''} | {gate} | {ov} {on} | {jv} |")
                for d in dropped:
                    out.append(f"| (除外) | - | {d['phrase']} | - | - | - | **{d['stage']}**: {d['reasons'][0][:100]} | - | - |")
                out.append("")
                return out
            L += listing(f"現行方式 候補全文", cur["rows"], cur["dropped"])
            for rep, t in enumerate(tr, start=1):
                if t:
                    L += listing(f"Trial方式 r{rep} 候補全文(P7返答{t['returned']['p7']}・W3返答{t['returned']['w3']}、call {t['cost']['calls']}、¥{t['cost']['jpy']})", t["candidates"], t["dropped"])
            summary[key] = {"current": {"n_final": len(cur["rows"]), "counts": cc},
                            "trial": [{"rep": i + 1, "n_final": t["n_final"], "n_phrase": t["n_phrase"], "n_word": t["n_word"], "counts": c, "cost_jpy": t["cost"]["jpy"]}
                                      for i, (t, c) in enumerate(zip(tr, tc)) if t]}
    with open(os.path.join(OUT, "RESULT_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # 安定性集計
    def dist(vals):
        v = sorted(vals)
        n = len(v)
        med = (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2) if n else None
        return {"min": v[0] if v else None, "median": med, "max": v[-1] if v else None, "values": v}
    tr_all = [x for k in summary.values() for x in k["trial"]]
    cur_all = [k["current"] for k in summary.values()]
    stab = {
        "trial_n_final": dist([x["n_final"] for x in tr_all]),
        "trial_own_Y": dist([x["counts"]["own"]["Y"] for x in tr_all]),
        "trial_own_Y_plus_B": dist([x["counts"]["own"]["Y"] + x["counts"]["own"]["B"] for x in tr_all]),
        "trial_both_Y": dist([x["counts"]["both_Y"] for x in tr_all]),
        "trial_judge_Y": dist([x["counts"]["judge"]["Y"] for x in tr_all]),
        "trial_own_Y_word": dist([x["counts"]["own_Y_word"] for x in tr_all]),
        "trial_own_Y_phrase": dist([x["counts"]["own_Y_phrase"] for x in tr_all]),
        "current_n_final": dist([x["n_final"] for x in cur_all]),
        "current_own_Y": dist([x["counts"]["own"]["Y"] for x in cur_all]),
        "current_own_Y_plus_B": dist([x["counts"]["own"]["Y"] + x["counts"]["own"]["B"] for x in cur_all]),
        "current_both_Y": dist([x["counts"]["both_Y"] for x in cur_all]),
        "current_judge_Y": dist([x["counts"]["judge"]["Y"] for x in cur_all]),
        "current_own_Y_phrase": dist([x["counts"]["own_Y_phrase"] for x in cur_all]),
        "trial_runs_with_own_Y_ge6": sum(1 for x in tr_all if x["counts"]["own"]["Y"] >= 6),
        "trial_runs_with_Y_plus_B_ge6": sum(1 for x in tr_all if x["counts"]["own"]["Y"] + x["counts"]["own"]["B"] >= 6),
        "trial_runs_with_both_Y_ge6": sum(1 for x in tr_all if x["counts"]["both_Y"] >= 6),
        "levels_with_word_Y_ge1": sum(1 for k in summary.values() if any(x["counts"]["own_Y_word"] >= 1 for x in k["trial"])),
        "n_trial_runs": len(tr_all),
    }
    sums = lambda lst, f: sum(f(x) for x in lst)   # noqa: E731
    def rate(lst, n_key, y_key):
        n = sums(lst, n_key)
        return round(sums(lst, y_key) / n, 3) if n else None
    # フレーズ品質: フレーズ候補のうち own Y の割合
    def phrase_rate(rows_list):
        return None
    out = {"summary": summary, "stability": stab, "mean_current_fresh_cost_jpy": mean_cur_cost}
    with open(os.path.join(OUT, "summary_01.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(stab, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline")
    b.add_argument("--out", required=True)
    r1 = sub.add_parser("run-one")
    r1.add_argument("--article", required=True)
    r1.add_argument("--level", required=True)
    r1.add_argument("--method", required=True)
    r1.add_argument("--rep", type=int, default=1)
    r = sub.add_parser("run")
    r.add_argument("--levels", required=True)
    r.add_argument("--methods", default="p7w3")
    r.add_argument("--repeats", type=int, default=2)
    r.add_argument("--current-repeats", type=int, default=1)
    r.add_argument("--parallel", type=int, default=4)
    r.add_argument("--out", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--out", required=True)
    c.add_argument("--gate-out", required=True)
    sub.add_parser("judge")
    sub.add_parser("report")
    a = ap.parse_args(argv)
    if a.cmd == "report":
        return cmd_report(a)
    if a.cmd == "collect":
        return cmd_collect(a)
    if a.cmd == "judge":
        return cmd_judge(a)
    if a.cmd == "baseline":
        return cmd_baseline(a)
    if a.cmd == "run-one":
        return run_one(a)
    if a.cmd == "run":
        return cmd_run(a)
    return 2


if __name__ == "__main__":
    sys.exit(main())
