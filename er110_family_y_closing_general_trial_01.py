# -*- coding: utf-8 -*-
"""er110_family_y_closing_general_trial_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_29: Family Y Closing生成方式の一般化Trial(DEV/Trial専用)。

目的: テーマ情報+Persona 3+Voice本文 3 だけを入力し、AIが自ら切り口を発見して Tension+Closing(最終パート)を書く
      共通方式を検証する。記事ごとの切り口の手動設計・Prompt修正は行わない(テーマ間でPromptは同一、入力データの差替えのみ)。

位置づけ(重要):
  - Family YのDEV/Trial経路。Production runner・.env・起動scriptから参照されない(testでGrep固定)。import時にAPI呼出0・ファイル副作用0。
    環境変数・flagでProduction挙動が変わる経路はない。ProductionのPrompt・正規表現・閾値・Gate定義は無変更(読取りのみ)。
  - Prompt本体は docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/prompt_closing_general_01.txt(sha256をtestで固定)。
    記事固有語(宅配・再配達・SNS・年齢など)はPrompt本文に含めない(testで固定)。テーマ固有情報は入力データブロックにだけ入る。
  - Leakage Gateは既存 p.run_leak(kind='tension') を **判定のみ1回**実行して記録する。FAILでも書き換えない(切り口を失わせないため。
    書き換え付きの p.run_gate は使わない)。FAIL理由の分類(Gate側の課題か本文の課題か)は EVAL で行う。
  - **有料runは --paid と er110_output/family_y_closing_general_01/BUDGET_APPROVED.json が無い限り起動しない**。
    費用guardは予約方式(各callの前に『実費累計+そのcallの見積』>Cap なら停止)。テーマごとに別processで並列実行し、Capはテーマ別に等分する。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_persona_text_trial_01 as p
import er110_family_y_redelivery_audio_01 as rr
import er110_family_y_redelivery_revision_01 as rev
import er110_family_y_text_trial_01 as y0

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_CLOSING_GENERAL_01"
ROOT = "er110_output/family_y_closing_general_01"
APPROVAL_FILE = f"{ROOT}/BUDGET_APPROVED.json"
PROMPT_FILE = "docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/prompt_closing_general_01.txt"
PROMPT_SHA256 = "fd3dc62e67ce661e675b648d5b9207d41e2f9bb20425bbe4c6cbcd597af479b8"
SLOTS = ("voice_1", "voice_2", "voice_3")
THEMES = ("redelivery_fee", "sns_age_limit")
GEN_EST_JPY = 12.0       # 1生成(sol, high, 構造化出力)の予約見積(委任_28実績 1callあたり4〜5.4円[出力2.2〜3k token]から、分析出力を加えた保守値)
GATE_EST_JPY = 0.8       # Leakage判定(luna, high)1回の予約見積(委任_28実績 0.05〜0.6円)
THEME_DATA_REDELIVERY = rev.THEME_DATA
SNS_VOICES = "er110_output/family_y_opinion_based_02/sns_age_limit/run_03/voices_final.json"
SNS_GATE = "er110_output/family_y_opinion_based_02/sns_age_limit/run_03/gate_voices/gate_result.json"

# ============================================================
# 出力スキーマ(strict JSON)。分析→候補→選定→本文。最終採用はclosing_jaのみ(他は評価・監査用)
# ============================================================
_QUOTES = {"type": "array", "items": {"type": "string"}}
SCHEMA = {"name": "family_y_closing_general", "strict": True, "schema": {
    "type": "object", "additionalProperties": False,
    "required": ["observations", "candidates", "selected_id", "selection_reason", "closing_ja"],
    "properties": {
        "observations": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["kind", "note", "evidence_quotes"],
            "properties": {"kind": {"type": "string", "enum": ["共通点", "相違点", "矛盾", "意外性"]}, "note": {"type": "string"}, "evidence_quotes": _QUOTES}}},
        "candidates": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "new_view", "evidence_quotes", "deepens", "listener_question", "pitfall"],
            "properties": {"id": {"type": "string"}, "new_view": {"type": "string"}, "evidence_quotes": _QUOTES, "deepens": {"type": "string"},
                           "listener_question": {"type": "string"}, "pitfall": {"type": "string"}}}},
        "selected_id": {"type": "string"},
        "selection_reason": {"type": "string"},
        "closing_ja": {"type": "string"},
    }}}


# ============================================================
# Prompt(ファイルから読み、sha固定)
# ============================================================
def load_prompt_parts(path: str = PROMPT_FILE) -> dict:
    raw = open(path, "rb").read().replace(bytes([13, 10]), bytes([10]))      # 改行コード差(CRLF変換)でshaが変わらないようLFへ正規化
    text = raw.decode("utf-8")
    m = re.match(r"=====DEVELOPER=====\n(.*?)\n=====USER=====\n(.*)\Z", text, re.S)
    if not m:
        raise RuntimeError("prompt fileの形式が想定と違います")
    return {"developer": m.group(1).strip(), "user_template": m.group(2).rstrip("\n"), "sha256": hashlib.sha256(raw).hexdigest()}


def check_prompt_sha(parts: dict):
    if parts["sha256"] != PROMPT_SHA256:
        raise RuntimeError(f"[PROMPT_SHA_MISMATCH] {parts['sha256']} != {PROMPT_SHA256}(Promptを変更した場合は版を改めて記録すること)")


# ============================================================
# 入力データ(テーマ情報+Persona 3+Voice本文 3。どのテーマも同じ形に正規化する。切り口・結論・既存Closingは入れない)
# ============================================================
def normalize_input(question: str, premise: str, distinctions: list, personas: list, voices: dict) -> dict:
    return {"question": question, "premise": premise, "distinctions": distinctions,
            "personas": [{"role": x["role"], "sketch": x["sketch"], "stake": x["stake"]} for x in personas],
            "voices": {s: voices[s].strip() for s in SLOTS}}


def load_input(theme: str) -> dict:
    if theme == "redelivery_fee":
        d = json.load(open(THEME_DATA_REDELIVERY, encoding="utf-8"))
        wf, sh = d["world_frame"], d["sheets"]
        r0 = rr.load_r0()          # Gate PASS・byte一致を検査して読む(委任_28と同一のVoice本文)
        return normalize_input(wf["question_ja"], wf["shared_premise_ja"], wf["distinctions"],
                               [{"role": sh[s]["role_ja"], "sketch": sh[s]["persona_sketch_ja"], "stake": sh[s]["stake_ja"]} for s in SLOTS],
                               {s: r0[s] for s in SLOTS})
    if theme == "sns_age_limit":
        import er110_family_y_opinion_based_02 as ob2     # 既存テーマ定義・Persona Sheet(読取りのみ)
        gate = json.load(open(SNS_GATE, encoding="utf-8"))
        if gate.get("status") != "PASS":
            raise RuntimeError("SNS Voice Leakage Gateが PASS ではありません")
        voices = json.load(open(SNS_VOICES, encoding="utf-8"))
        wf, sh = ob2.WORLD_FRAME_02, ob2.SHEETS_02
        return normalize_input(wf["question_ja"], wf["shared_premise_ja"], wf["distinctions"],
                               [{"role": sh[s]["role_ja"], "sketch": sh[s]["persona_sketch_ja"], "stake": sh[s]["stake_ja"]} for s in SLOTS],
                               {s: voices[s] for s in SLOTS})
    raise ValueError(theme)


def render_blocks(inp: dict) -> dict:
    ds = "\n".join(f"- {x['term_ja']}: {x['definition_ja']}" for x in inp["distinctions"])
    theme = (f"【テーマ・論点】{inp['question']}\n【前提と範囲】{inp['premise']}\n【用語の意味】\n{ds}")
    persona = "【3人の人物像】\n" + "\n".join(
        f"- 人物{i + 1}: {x['role']}。{x['sketch']} 大事にしていること: {x['stake']}" for i, x in enumerate(inp["personas"]))
    voice = "\n\n".join(f"【人物{i + 1}の語り】\n{inp['voices'][s]}" for i, s in enumerate(SLOTS))
    return {"@@THEME_BLOCK@@": theme, "@@PERSONA_BLOCK@@": persona, "@@VOICE_BLOCK@@": voice}


def build_prompt(inp: dict, parts: dict = None) -> dict:
    parts = parts or load_prompt_parts()
    check_prompt_sha(parts)
    user = parts["user_template"]
    for k, v in render_blocks(inp).items():
        user = user.replace(k, v)
    if "@@" in user:
        raise RuntimeError("未置換のplaceholderが残っています")
    return {"developer": parts["developer"], "user": user, "prompt_sha256": parts["sha256"], "user_sha256": w1.sha_text(user)}


# ============================================================
# 検査(決定論)
# ============================================================
_PROBLEM_JA = {
    "EMPTY": "closing_ja が空でした。最終パートの本文を書いてください。",
    "MULTI_PARAGRAPH": "改行が入っていました。最終パートは改行なしの1段落にしてください。",
    "HAS_FIRST_PERSON": "一人称(私・俺・僕・わたし)が入っていました。語り手の声で、一人称を使わずに書いてください。",
    "LABEL_AT_START": "冒頭にラベルのような言葉が入っていました。ラベルや見出しは書かず、本文から始めてください。",
    "HAS_INTERVIEWER_EXPRESSION": "取材者がいるような言い方(取材した、話を聞いた等)が入っていました。使わないでください。",
    "HAS_DIGIT": "算用数字が入っていました。数字は使わず、言葉で書いてください。",
    "DESU_MASU": "です・ます調が入っていました。話し言葉の常体で書いてください。",
    "HAS_AI_EDIT_ANNOUNCEMENT": "編集やAIについて断る文言が入っていました。本文だけを書いてください。",
    "OBVIOUS_CONCLUSION_PHRASE": "「人によって違う」のような当然の結論で終える言い方が入っていました。避けてください。",
    "NOT_ENDING_WITH_QUESTION": "文末が「？」で終わっていませんでした。最後は聞き手への問い1つで、文末を「？」にしてください。",
    "SENTENCE_TOO_LONG": "1文が長すぎる箇所がありました。1文は45字以内に区切ってください。",
}


def explain_problem(code: str) -> str:
    """決定論検査の違反コードを、再生成時に渡す日本語の説明へ変える(コード名のまま渡さない)。"""
    if code in _PROBLEM_JA:
        return _PROBLEM_JA[code]
    if code.startswith("LENGTH="):
        return f"本文の長さが{code[7:]}字でした。約190〜230字の範囲に収めてください。"
    if code.startswith("CANDIDATES_COUNT="):
        return "候補の切り口の数が3〜5個の範囲ではありませんでした。3〜5個にしてください。"
    if code == "CANDIDATE_ID_DUP":
        return "候補の id が重複していました。候補ごとに別の id を付けてください。"
    if code == "SELECTED_ID_NOT_IN_CANDIDATES":
        return "selected_id が候補の id にありませんでした。候補の id から選んでください。"
    if code == "NO_OBSERVATIONS":
        return "観察の欄が空でした。語りの中から見つかった観察を書いてください。"
    if code.startswith("TAG_LEAK:"):
        return "本文に内部用のタグのような表記が入っていました。本文だけを書いてください。"
    if code.startswith("SYMBOL:"):
        return "使えない記号(括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字など)が入っていました。使わずに書いてください。"
    return f"本文に問題がありました({code})。ルールを見直して書き直してください。"


def _squash(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def check_structure(obj: dict) -> list:
    v = []
    cands = obj.get("candidates") or []
    ids = [c.get("id") for c in cands]
    if not (3 <= len(cands) <= 5):
        v.append(f"CANDIDATES_COUNT={len(cands)}")
    if len(set(ids)) != len(ids):
        v.append("CANDIDATE_ID_DUP")
    if obj.get("selected_id") not in ids:
        v.append("SELECTED_ID_NOT_IN_CANDIDATES")
    if not (obj.get("observations") or []):
        v.append("NO_OBSERVATIONS")
    return v


def grounding_report(obj: dict, voices: dict) -> dict:
    """根拠引用が語りの本文に実在するか(記録専用。合否に使わない)。"""
    body = _squash("".join(voices[s] for s in SLOTS))
    qs = [q for o in obj.get("observations", []) for q in o["evidence_quotes"]] + [q for c in obj.get("candidates", []) for q in c["evidence_quotes"]]
    found = [q for q in qs if _squash(q) and _squash(q) in body]
    return {"n_quotes": len(qs), "n_verbatim": len(found), "missing": [q for q in qs if q not in found][:12]}


# ============================================================
# 有料run(予約方式の費用guard)
# ============================================================
def read_cap(path: str = None) -> dict:
    return rr.read_cap(path or APPROVAL_FILE)


def require_paid(paid_flag: bool, approval_path: str = None) -> dict:
    if not paid_flag:
        raise RuntimeError("[NO_PAID_FLAG] --paid が無いため有料runを起動しません")
    return read_cap(approval_path)


def spent_jpy(theme_dir: str) -> float:
    import glob
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{theme_dir}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def reserve(theme_dir: str, est_jpy: float, theme_cap: float, note: str, spent_fn=spent_jpy) -> float:
    """callの前に『実費累計+このcallの見積』がCapを超えるなら停止(実費はcallごとのraw usage logで確定)。"""
    s = spent_fn(theme_dir)
    if s + est_jpy > theme_cap:
        raise RuntimeError(f"[BUDGET_RESERVE_STOP] spent {s} + est {est_jpy} > theme cap {theme_cap} JPY ({note})")
    print(f"[Y-CLOSING-GENERAL] reserve ok: spent {s} + est {est_jpy} <= {theme_cap} ({note})")
    return s


def generate_one(client, *, theme: str, gen_idx: int, inp: dict, theme_cap: float, out_dir: str, chat=None, spent_fn=spent_jpy, leak=None) -> dict:
    """1生成(+決定論検査違反時のみ再生成1回)→ Leakage判定(1回・書き換えなし)。"""
    import er003_audio_tts_asr_safety as safety
    chat = chat or y0.chat
    leak = leak or p.run_leak
    theme_dir = os.path.dirname(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    pr = build_prompt(inp)
    w1.wt(os.path.join(out_dir, "prompt_developer.txt"), pr["developer"])
    w1.wt(os.path.join(out_dir, "prompt_user.txt"), pr["user"])
    hist, calls, cur = [], [], pr["user"]
    for k in (1, 2):
        reserve(theme_dir, GEN_EST_JPY, theme_cap, f"{theme} gen{gen_idx} try{k}", spent_fn)
        resp = chat(client, model=y0.MODEL_TOP, effort="high", user=cur, developer=pr["developer"], schema=SCHEMA,
                    stage=f"ycg_{theme}_g{gen_idx}" + ("" if k == 1 else "_regen"))
        calls.append({**y0.resp_meta(resp), "user_sha256": w1.sha_text(cur)})
        obj = json.loads(resp.output_text)
        w1.wj(os.path.join(out_dir, f"analysis_try{k}.json"), obj)
        probs = check_structure(obj)
        final = ""
        try:
            final, sym = p._fin(obj.get("closing_ja", ""))
            probs += rev.check_closing(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            probs.append(f"TAG_LEAK:{e}")
        hist.append(probs)
        if not probs:
            break
        if k == 1:
            cur = pr["user"] + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {explain_problem(x)}" for x in probs)
    else:
        w1.wj(os.path.join(out_dir, "gen_meta.json"), {"calls": calls, "problems_per_try": hist, "status": "CONTRACT_STOP"})
        raise y0.YStop("CLOSING_GENERAL_CONTRACT_STOP", f"{theme} gen{gen_idx}: 再生成後も契約違反 {hist[-1]}", hist)
    w1.wt(os.path.join(out_dir, "closing_final.txt"), final + "\n")
    w1.wj(os.path.join(out_dir, "analysis_final.json"), obj)
    w1.wj(os.path.join(out_dir, "grounding_report.json"), grounding_report(obj, inp["voices"]))
    reserve(theme_dir, GATE_EST_JPY, theme_cap, f"{theme} gen{gen_idx} gate", spent_fn)
    chk = leak(client, "tension", {"tension": final}, model=y0.MODEL_CHEAP, effort="high", stage=f"ycg_{theme}_g{gen_idx}_gate_leak")
    w1.wj(os.path.join(out_dir, "gate_leak_check.json"), {**chk, "note": "既存Tension項目セットを1回判定のみ(書き換えなし)。FAILの分類はEVALで行う"})
    meta = {"calls": calls, "problems_per_try": hist, "status": "DONE", "chars": len(final), "prompt_sha256": pr["prompt_sha256"],
            "gate_any_flagged": chk["any_flagged"], "gate_flagged": [{"fields": f["fail_fields"], "reasoning": f["reasoning"]} for f in chk["flagged_items"]],
            "selected_id": obj["selected_id"]}
    w1.wj(os.path.join(out_dir, "gen_meta.json"), meta)
    return {"text": final, "meta": meta}


# ============================================================
# CLI
# ============================================================
def cmd_dryrun(a):
    """API 0・副作用0: Prompt sha・両テーマの組立Promptの差分(入力ブロックのみ)・見積を表示。"""
    parts = load_prompt_parts()
    check_prompt_sha(parts)
    for t in THEMES:
        pr = build_prompt(load_input(t), parts)
        print(t, "user_chars=", len(pr["user"]), "user_sha256=", pr["user_sha256"][:16])
    print("prompt_sha256", parts["sha256"])
    print("est per theme (gens=%d): %.1f JPY" % (a.gens, a.gens * (GEN_EST_JPY + GATE_EST_JPY)))


def cmd_gen(a):
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cap = require_paid(a.paid)["cap_jpy"]
    theme_cap = cap / len(THEMES)
    theme_dir = f"{ROOT}/{a.theme}"
    os.makedirs(theme_dir, exist_ok=True)
    cl.install(f"{theme_dir}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    inp = load_input(a.theme)
    w1.wj(f"{theme_dir}/entry_point.json", {"runner": "er110_family_y_closing_general_trial_01.py", "management_id": MANAGEMENT_ID, "theme": a.theme,
                                            "production_reachable": False, "writer_model": y0.MODEL_TOP, "judge_model": y0.MODEL_CHEAP, "cap_jpy_total": cap,
                                            "theme_cap_jpy": theme_cap, "gens": a.gens, "prompt_sha256": PROMPT_SHA256,
                                            "module_sha256": hashlib.sha256(open("er110_family_y_closing_general_trial_01.py", "rb").read()).hexdigest()})
    prev = y0.THEME_TAG
    y0.THEME_TAG = THEME_TAG
    try:
        for g in range(1, a.gens + 1):
            od = f"{theme_dir}/gen_{g}"
            if os.path.exists(f"{od}/gen_meta.json") and json.load(open(f"{od}/gen_meta.json", encoding="utf-8")).get("status") == "DONE":
                print("skip(done)", a.theme, g)
                continue
            r = generate_one(client, theme=a.theme, gen_idx=g, inp=inp, theme_cap=theme_cap, out_dir=od)
            print(f"[Y-CLOSING-GENERAL] {a.theme} gen{g} chars={r['meta']['chars']} gate_flagged={r['meta']['gate_any_flagged']}")
    finally:
        y0.THEME_TAG = prev


def main():
    ap = argparse.ArgumentParser(description="Family Y Closing生成方式の一般化Trial(DEV/Trial専用)")
    ap.add_argument("cmd", choices=("dryrun", "gen"))
    ap.add_argument("--theme", choices=THEMES)
    ap.add_argument("--gens", type=int, default=2)
    ap.add_argument("--paid", action="store_true", help="有料run。予算承認ファイルも必要")
    a = ap.parse_args()
    if a.cmd == "gen" and not a.theme:
        ap.error("gen には --theme が必要")
    {"dryrun": cmd_dryrun, "gen": cmd_gen}[a.cmd](a)


if __name__ == "__main__":
    main()
