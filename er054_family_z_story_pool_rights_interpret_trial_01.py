# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_02: 権利情報の解釈・整理工程(Trial専用driver、gpt-6-luna固定)。

【位置づけ】Phase B(決定論の権利スクリーニング: screening/<ID>.json)の結果を、LLMが「整理・要約・未確認事項の明確化」する補助工程。
【最重要原則】LLM出力はPhase Bの決定論判定を上書きしない。
  - LLMの出力schemaには「判定(PASS/NG)」欄が無い(llm_concern_levelは懸念の度合いのみ)。
  - 最終PASSはPython判定+ユーザー確定。LLMが「PASS相当」と言っても決定論がREVIEW_REQUIRED/NGなら据え置き(pass_equivalentは記録のみ)。
  - LLMがreview/ng_concernの懸念を出した場合、決定論PASSを REVIEW_REQUIRED へ「降格のみ」可。REVIEW/NGの昇格は不可。
  - 一次資料が未取得(primary_source.fetch_ok != True)の作品は、決定論PASSでもREVIEW_REQUIREDへ降格(原作未確認の自動PASS禁止)。
  - 常に final_pass_confirmed=False(ユーザーが確定するまで最終PASSにしない)。
【状態】乾式(--mode dry-run、モックclient、API呼出なし)のみ実行可。--mode real は --approved-budget-jpy>0 が無いと起動しない。
【範囲】Trial専用(到達上限VALIDATED)。Production(er026等)・Production Routing keyは変更しない。Blind: 封印ファイル(過去評価結果)は読まない。
【モデル】既存Routing経由のTrial専用key FAMILY_Z_TRIAL_RIGHTS_INTERPRET(値=gpt-6-luna)。actual model_id(応答のmodel)を呼出ごとに記録。
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import er054_family_z_story_pool_trial_common_01 as common

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01")
SCREEN = os.path.join(BASE, "screening")
PRICING_SNAPSHOT = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0
INTERP_VERSION = "family_z_rights_interpret_v2_work_edition"
ROUTING_KEY = common.KEY_RIGHTS
PRIMARY_MODEL = common.resolve_trial_model(ROUTING_KEY)  # gpt-6-luna
ALLOWED_MODELS = (PRIMARY_MODEL,)
REASONING_EFFORT = "medium"
OVERHEAD_PROMPT_TOKENS = 1500
OUT_TOKENS_POINT = 5000
JA_TOKENS_PER_CHAR = 1.0
WORKS = [f"L{i:02d}" for i in range(1, 11)]
DROP_KEYS = {"primary_source": ("text_sha256_raw", "text_sha256_plain", "saved_dir", "card_parse")}  # ノイズ(ハッシュ等)除去

DEVELOPER_MESSAGE = (
    "あなたは英語学習マガジンのFiction編集部の権利確認補助者である。与えられた『Phase B決定論判定JSON』(Pythonが日本の著作権法ルールで計算した結果)と"
    "書誌メタ・未確認事項だけを根拠に、権利状態を整理・要約し、未確認情報を明確化し、REVIEW_REQUIREDの解消に必要な確認事項を挙げる。"
    "あなたは最終判定者ではない。PASS/NGを決める欄は無く、決定論判定を変更・上書きすることはできない。"
    "入力に無い事実(没年・出版事情・翻訳者・出典)を記憶から補ってはならない。入力に無い情報は『未確認』と明記する。"
    "米国のPD状態を日本の利用条件の根拠にしてはならない。原語原作の権利(work_rights)と、利用した版・翻訳の権利(edition_rights)は必ず分けて述べ、混同しない。"
    "判定の根拠は work_rights(原語原作の著者の日本国内保護期間と一次資料の取得状況)だけであり、edition_rights は参考情報で作品の権利判断・記事化の前提条件にしてはならない。"
    "既存翻訳に権利上の懸念があっても、原語原作に問題が無ければ作品を懸念扱いにしない(翻訳側の懸念は concerns に文章で書くだけにし、llm_concern_level には反映しない)。"
    "懸念(llm_concern_level)は、入力から読み取れる「原語原作(work_rights)」に関する権利上の疑義の度合いだけを答える(none=疑義なし / review=確認が必要 / ng_concern=権利NGの疑い)。"
)

USER_TEMPLATE = """[入力: Phase B決定論判定JSON(作品ID {work_id})]
{payload}

[手順]
1. rights_state_summary: 権利状態の整理(日本国内の原語原作の保護状態を先に、次に版・翻訳(edition_rights、参考情報)の扱いを分けて、2〜4文、日本語)。
2. basis_summary: 判断根拠の要約(入力のどのフィールドに基づくか、決定論判定 decision={decision} をどう読んだか)。
3. subjects: 権利者(rights_subjects)ごとの状態の読み取り(subject, status_as_given(入力のstatusをそのまま), note)。
4. unconfirmed_clarified: 未確認事項(unconfirmed)ごとに、なぜ重要か(why_matters)と、最終PASSに対してブロッキングか(blocking_for_final_pass)。入力に無い未確認事項を足す場合はadded_by_llm=trueにする。
5. confirmations_needed_to_resolve_review: REVIEW_REQUIRED/最終PASSに必要な追加確認事項(誰が/何を確認するか、日本語の短文の配列、0個可)。
6. llm_concern_level(none/review/ng_concern)と concerns(懸念の具体、0個可)。pass_equivalent: あなたの印象で『PASS相当』か(記録用。判定には使われない)。
7. confidence(high/medium/low)。
8. 出力はJSONのみ。"""

JSON_SCHEMA = {
    "name": "family_z_rights_interpret",
    "schema": {
        "type": "object",
        "properties": {
            "rights_state_summary": {"type": "string"},
            "basis_summary": {"type": "string"},
            "subjects": {"type": "array", "items": {"type": "object", "properties": {
                "subject": {"type": "string"}, "status_as_given": {"type": "string"}, "note": {"type": "string"}},
                "required": ["subject", "status_as_given", "note"], "additionalProperties": False}},
            "unconfirmed_clarified": {"type": "array", "items": {"type": "object", "properties": {
                "item": {"type": "string"}, "why_matters": {"type": "string"},
                "blocking_for_final_pass": {"type": "boolean"}, "added_by_llm": {"type": "boolean"}},
                "required": ["item", "why_matters", "blocking_for_final_pass", "added_by_llm"], "additionalProperties": False}},
            "confirmations_needed_to_resolve_review": {"type": "array", "items": {"type": "string"}},
            "llm_concern_level": {"type": "string", "enum": ["none", "review", "ng_concern"]},
            "concerns": {"type": "array", "items": {"type": "string"}},
            "pass_equivalent": {"type": "boolean"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        },
        "required": ["rights_state_summary", "basis_summary", "subjects", "unconfirmed_clarified",
                     "confirmations_needed_to_resolve_review", "llm_concern_level", "concerns", "pass_equivalent", "confidence"],
        "additionalProperties": False,
    },
    "strict": True,
}


def load_screening(wid: str) -> dict:
    with open(common.assert_not_sealed(os.path.join(SCREEN, f"{wid}.json")), encoding="utf-8") as f:
        return json.load(f)


def build_payload(scr: dict) -> str:
    d = copy.deepcopy(scr)
    for k, drops in DROP_KEYS.items():
        for x in drops:
            d.get(k, {}).pop(x, None)
    return json.dumps(d, ensure_ascii=False, indent=1)


def build_messages(scr: dict) -> list:
    user = USER_TEMPLATE.format(work_id=scr["work_id"], payload=build_payload(scr), decision=scr["decision"])
    return [{"role": "developer", "content": DEVELOPER_MESSAGE}, {"role": "user", "content": user}]


def validate_schema_min(parsed: dict) -> None:
    for k in JSON_SCHEMA["schema"]["required"]:
        if k not in parsed:
            raise ValueError(f"missing key: {k}")
    if parsed["llm_concern_level"] not in ("none", "review", "ng_concern"):
        raise ValueError("bad llm_concern_level")


def reconcile(scr: dict, parsed: dict) -> dict:
    """決定論判定とLLM整理の統合(決定論)。降格のみ可・昇格不可・最終PASS未確定。"""
    det = scr["decision"]
    final, notes = det, []
    if det == "PASS":
        if parsed["llm_concern_level"] in ("review", "ng_concern"):
            final = "REVIEW_REQUIRED"
            notes.append(f"LLM懸念({parsed['llm_concern_level']})により決定論PASSをREVIEW_REQUIREDへ降格")
        if scr.get("primary_source", {}).get("fetch_ok") is not True:
            final = "REVIEW_REQUIRED"
            notes.append("一次資料未取得のためREVIEW_REQUIREDへ降格(原作未確認の自動PASS禁止)")
        if any(u.get("blocking") for u in scr.get("unconfirmed", [])):
            final = "REVIEW_REQUIRED"
            notes.append("blocking未確認事項があるためREVIEW_REQUIREDへ降格")
    elif parsed["pass_equivalent"] or parsed["llm_concern_level"] == "none":
        notes.append(f"LLMがPASS相当/懸念なしと述べたが、決定論判定{det}を据え置き(LLMは昇格不可)")
    return {"deterministic_decision": det, "final_status_after_interpret": final,
            "demoted": final != det, "pass_equivalent_llm_ignored": parsed["pass_equivalent"],
            "final_pass_confirmed": False,
            "final_pass_note": "最終PASSはPython判定+ユーザー確定。本工程は確定しない。", "notes": notes}


class MockClient:
    """OpenAI Responses API互換モック(API呼出なし)。mode: neutral/concern/upgrade。"""
    def __init__(self, mode: str = "neutral"):
        self.calls, self.mode = 0, mode
        self.responses = self

    def create(self, **kw):
        self.calls += 1
        concern = {"neutral": "none", "concern": "review", "upgrade": "none"}[self.mode]
        out = {"rights_state_summary": "mock", "basis_summary": "mock", "subjects": [], "unconfirmed_clarified": [],
               "confirmations_needed_to_resolve_review": [], "llm_concern_level": concern,
               "concerns": [] if concern == "none" else ["mock concern"],
               "pass_equivalent": self.mode in ("upgrade", "neutral"), "confidence": "low"}

        class R:
            model = kw["model"]
            id = "mock-response"
            output_text = json.dumps(out, ensure_ascii=False)
        return R()


def interpret_one(wid: str, model: str, client, out_dir: str, mock: bool) -> dict:
    model = common.check_model(ROUTING_KEY, model)
    scr = load_screening(wid)
    msgs = build_messages(scr)
    _t0 = __import__("time").time()
    resp = client.responses.create(model=model, reasoning={"effort": REASONING_EFFORT}, input=msgs,
                                   text={"format": {"type": "json_schema", **JSON_SCHEMA}})
    elapsed = round(__import__("time").time() - _t0, 2)
    actual = getattr(resp, "model", None)
    if not mock and not (actual and str(actual).startswith(model)):
        raise RuntimeError(f"STOP: actual model_idが要求と異なる requested={model} actual={actual}")
    parsed = json.loads(resp.output_text)
    validate_schema_min(parsed)
    rec_ = reconcile(scr, parsed)
    usage = getattr(resp, "usage", None)
    rec = {"work_id": wid, "interp_version": INTERP_VERSION, "requested_model": model, "actual_model_id": actual,
           "routing_key": ROUTING_KEY, "mock": mock, "reasoning_effort": REASONING_EFFORT,
           "interpreted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "usage": ({"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)} if usage else None),
           "prompt_sha256": hashlib.sha256(json.dumps(msgs, ensure_ascii=False).encode("utf-8")).hexdigest(),
           "usage_full": (usage.model_dump() if usage is not None and hasattr(usage, "model_dump") else None), "elapsed_sec": elapsed, "response_id": getattr(resp, "id", None),
           "developer_message": DEVELOPER_MESSAGE, "user_prompt_full": msgs[1]["content"], "llm_output": parsed, "reconcile": rec_}
    d = os.path.join(out_dir, model)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{wid}.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec


def load_prices(model: str) -> dict:
    with open(PRICING_SNAPSHOT, encoding="utf-8", errors="replace") as f:
        snap = json.load(f)
    pr = {p["meter"]: p["price"] for p in snap["prices"]
          if p["model"] == model and p.get("tier") == "Standard" and p["meter"] in ("input_tokens", "cached_input_tokens", "output_tokens")}
    if len(pr) < 3:
        raise RuntimeError(f"STOP: {model} の単価が未登録。他modelの流用は禁止。")
    return pr


def estimate_cost(works: list, model: str = PRIMARY_MODEL, out_tokens: int = OUT_TOKENS_POINT) -> dict:
    pr = load_prices(model)
    rows, tot = {}, 0.0
    for w in works:
        scr = load_screening(w)
        tin = int(len(build_payload(scr)) * JA_TOKENS_PER_CHAR) + OVERHEAD_PROMPT_TOKENS
        usd = tin / 1e6 * pr["input_tokens"] + out_tokens / 1e6 * pr["output_tokens"]
        rows[w] = {"input_tokens": tin, "output_tokens": out_tokens, "usd": round(usd, 5), "jpy_point": round(usd * USD_JPY, 3)}
        tot += usd * USD_JPY
    return {"model": model, "prices_usd_per_1m": pr, "per_work": rows, "total_jpy_point": round(tot, 3),
            "total_jpy_cap_x1_5": round(tot * 1.5, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dry-run", "real", "estimate"], default="dry-run")
    ap.add_argument("--models", nargs="+", default=[PRIMARY_MODEL])
    ap.add_argument("--works", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out-dir", default=os.path.join(BASE, "phase_b2_rights_interpret"))
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    args = ap.parse_args()
    for m in args.models:
        if m not in ALLOWED_MODELS:
            sys.exit(f"STOP: {m} は許可モデル外(Trial固定=gpt-6-luna。変更はユーザー承認が必要)。許可: {ALLOWED_MODELS}")
    works = args.works or WORKS

    if args.mode == "estimate":
        print(json.dumps(estimate_cost(works), ensure_ascii=False)[:2000])
        return
    if args.mode == "dry-run":
        out = os.path.join(BASE, "phase_b2_dry_run")
        client = MockClient()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            recs = list(ex.map(lambda w: interpret_one(w, args.models[0], client, out, True), works))
        up = interpret_one("L04", args.models[0], MockClient("upgrade"), os.path.join(out, "_upgrade_check"), True)
        dn = interpret_one("L01", args.models[0], MockClient("concern"), os.path.join(out, "_demote_check"), True)
        summary = {"mock_calls": client.calls, "works": works,
                   "final_status": {r["work_id"]: r["reconcile"]["final_status_after_interpret"] for r in recs},
                   "deterministic": {r["work_id"]: r["reconcile"]["deterministic_decision"] for r in recs},
                   "any_upgraded": any(r["reconcile"]["final_status_after_interpret"] != r["reconcile"]["deterministic_decision"]
                                       and r["reconcile"]["deterministic_decision"] != "PASS" for r in recs),
                   "any_final_pass_confirmed": any(r["reconcile"]["final_pass_confirmed"] for r in recs),
                   "upgrade_check_L04_stays": up["reconcile"]["final_status_after_interpret"] == "REVIEW_REQUIRED",
                   "demote_check_L01_demoted": dn["reconcile"]["final_status_after_interpret"] == "REVIEW_REQUIRED",
                   "actual_model_id_recorded": all(r["actual_model_id"] == PRIMARY_MODEL for r in recs)}
        with open(os.path.join(out, "DRY_RUN_SUMMARY.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=False))
        return
    if args.approved_budget_jpy <= 0:
        sys.exit("STOP: 有料API(real)はユーザーの課金上限承認(--approved-budget-jpy > 0)が無いと起動しない。")
    est = estimate_cost(works)
    if est["total_jpy_cap_x1_5"] > args.approved_budget_jpy:
        sys.exit(f"STOP: 保守見積{est['total_jpy_cap_x1_5']:.1f}円が承認上限{args.approved_budget_jpy:.1f}円を超える。")
    from dotenv import load_dotenv
    load_dotenv()
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(os.path.join(args.out_dir, "raw_usage_log.jsonl"))
    client = vfl01.get_client()

    def one(w):
        with cl.logging_context("FAMILY_Z_STORY_POOL_SCREENING_TRIAL_01", f"rights_{w}"):
            return interpret_one(w, args.models[0], client, args.out_dir, False)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one, works))


if __name__ == "__main__":
    main()
