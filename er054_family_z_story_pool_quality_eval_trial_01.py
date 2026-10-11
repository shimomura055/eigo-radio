# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 Phase C(Story品質一次評価)Trial専用driver。

【委任_02(2026-10-11ユーザー指示)】使用モデルを gpt-6-luna に固定。既存Routing経由のTrial専用key
        `FAMILY_Z_TRIAL_STORY_QUALITY_EVAL`(er006 PROCESS_MODEL_MAP、値=gpt-6-luna)で解決し、
        Astra/Sol等は選べない(driverで拒否。提案候補としてPHASE_C_EVAL_DESIGN_01.mdに記載のみ)。
        呼出ごとに応答のmodelフィールド(actual model_id)を記録。Trial限定でProduction採用を意味しない。
【状態】委任_01では乾式(--mode dry-run、モックclient、API呼出ゼロ)のみ実行。
        --mode real は有料API(LLM)を使うため、ユーザーの課金上限承認(--approved-budget-jpy)が
        無い限り起動しない(委任_01では未実行)。
【範囲】Trial専用(到達上限VALIDATED)。Family Z Production(er026等)・Prompt・Routingは変更しない。
        Production runnerからimportされない(ファイル名にtrialを含む)。
【設計】PHASE_C_EVAL_DESIGN_01.md参照。1作品=1 API call(原作の全文または評価単位の全文を原文のまま渡す。要約しない)。
        作品別に別ファイルへ書くため並列実行可(同一ファイル書込みなし)。
        根拠引用はscriptが原文との一致を決定論で検証する(LLMの引用を信用しない)。
        総合判定は決定論(LLMにさせない)。過去Trial結果(SEALED_PAST_RESULTS_L01_L06.json)はこのdriverから読まない(Blind)。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import er054_family_z_story_pool_trial_common_01 as common

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01")
SRC = os.path.join(BASE, "sources")
SCREEN = os.path.join(BASE, "screening")
PRICING_SNAPSHOT = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0  # 既存換算(er009 USD_TO_JPY)に合わせる
EVAL_VERSION = "family_z_story_quality_eval_v2_original_language"  # 委任_03: L04はロシア語原作入力、従来/新基準の両判定

# ---- 評価用モデル(委任_02: ユーザー指示でgpt-6-lunaに固定。PM_GOVERNANCE 25節の例外=ユーザー明示指定)
ROUTING_KEY = common.KEY_QUALITY
PRIMARY_MODEL = common.resolve_trial_model(ROUTING_KEY)  # = "gpt-6-luna"(既存Routing経由)
ALLOWED_MODELS = (PRIMARY_MODEL,)  # これ以外(Astra/Sol等)は起動拒否。変更はユーザー承認が必要
MODEL_REASON = {PRIMARY_MODEL: "ユーザー指示(2026-10-11)によるTrial基本モデル固定。25節最新モデル原則の例外(ユーザー明示指定)。"}
REASONING_EFFORT = "medium"

# ---- 評価単位(原作の全文を原文のまま渡す。長編は章単位に固定し、要約はしない)
UNIT_RULES = {
    # L04: 委任_03で原語原作(ロシア語、ru.wikisource Пари)全文を入力する。英訳(Gutenberg)は渡さない。UNIT_RULESには置かない(全文モード)。
    "L06": {"kind": "gutenberg_chapter_slice", "start_heading": "CHAPTER IV", "end_heading": "CHAPTER V",
            "note": "自伝全体(約74万字)は短編化評価の単位にならないため第IV章を評価単位に仮設定。これは設計仮定でありユーザー確認事項。"},
}
EN_WORKS = {"L06"}
RU_WORKS = {"L04"}  # ロシア語原作(原語原作の品質評価。英訳は入力しない)
SRC_DIR = {"L04": "L04_ru"}
OVERHEAD_PROMPT_TOKENS = 1800  # developer + user template + JSON schema
OUT_TOKENS_POINT = 5000        # JSON(約1,500) + reasoning(effort=medium)の点見積
JA_TOKENS_PER_CHAR = 1.0       # 日本語: tokenizer未取得のため保守的な代理値(実測で要補正)
EN_TOKENS_PER_WORD = 1.4

CRITERIA = ("A", "B", "C", "D")
CRITERIA_DEF = {
    "A": "中心となる出来事・変化: 追える中心事件・行動・関係変化・選択があるか。",
    "B": "読者の関心を維持する要素: Hook・緊張・意外性・疑問・人間関係・共感・皮肉・強い状況設定のいずれかで読者を引っ張れるか(派手なHookは必須ではない)。",
    "C": "意味のある展開・変化・余韻: 明確なオチは必須ではないが、展開による変化または余韻が残るか。",
    "D": "短編化適性: 英語の短編(280〜420語)へ圧縮しても魅力が残るか(文体や長い心理描写・描写そのものが魅力の中心で削ると消える作品は不向き)。",
}

DEVELOPER_MESSAGE = (
    "あなたは英語学習マガジンのFiction編集部の評価者である。与えられた『原作本文』だけを根拠に、"
    "その作品を『英語の短編(280〜420語、A2〜B1向け)へ再話するための素材』として評価する。"
    "作品の知名度・評判・過去の評価・あなたの記憶に頼らず、本文に書かれていることだけで判断すること。"
    "評価は4項目(A〜D)それぞれについてPASSまたはFAILのどちらかで答え、本文からの根拠引用と理由を必ず付ける。"
    "引用(evidence_quotes)は本文中の連続した文字列をそのままコピーしたものに限る(言い換え・要約・結合・省略記号は禁止。ロシア語本文の引用はロシア語のままコピーし、日本語に訳さない)。"
    "1項目あたり1〜3個、各60文字(英語は25語)以内。迷った場合は無理にPASSにせず、理由欄に迷いの内容を書いてFAILまたはPASSを選ぶ。"
)

USER_TEMPLATE = """[評価対象]
作品ID: {work_id}
タイトル: {title}
言語: {lang}
評価単位: {unit_note}
本文の長さ: {size_note}

[評価基準(4項目、正本: FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md §2)]
A. {A}
B. {B}
C. {C}
D. {D}

[手順]
1. まず key_facts に、本文から抜き出した重要情報を書く(中心事件、主要人物と関係、転換点、結末、本文中の印象的な表現の引用)。要約は自分の言葉でよいが、引用は本文の連続した文字列のままにする。
2. 次に A〜D を判定する。各項目: verdict(PASS/FAIL)、evidence_quotes(本文からの連続した引用1〜3個)、reason(日本語、2〜4文)、confidence(high/medium/low)。
3. appeal: 英語短編化したときに残すべき魅力を日本語で1〜2文。
4. compression_risk: level(low/medium/high)と、圧縮で失われやすいもの(notes)、削ってよい要素(cut_candidates)。
5. diversity: 多様性属性(theme, mood, era, region, narrator)を短い日本語で。
6. 出力はJSONのみ。

[原作本文(原文のまま、要約・省略なし)]
<<<BEGIN_SOURCE_TEXT
{text}
END_SOURCE_TEXT>>>"""

_VERDICT = {"type": "string", "enum": ["PASS", "FAIL"]}
_CRIT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": _VERDICT,
        "evidence_quotes": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "string"}},
        "reason": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["verdict", "evidence_quotes", "reason", "confidence"],
    "additionalProperties": False,
}
JSON_SCHEMA = {
    "name": "family_z_story_quality_eval",
    "schema": {
        "type": "object",
        "properties": {
            "key_facts": {
                "type": "object",
                "properties": {
                    "central_event": {"type": "string"},
                    "main_characters": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"type": "string"}},
                    "turning_point": {"type": "string"},
                    "ending": {"type": "string"},
                    "notable_quotes": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "string"}},
                },
                "required": ["central_event", "main_characters", "turning_point", "ending", "notable_quotes"],
                "additionalProperties": False,
            },
            "A": _CRIT_SCHEMA, "B": _CRIT_SCHEMA, "C": _CRIT_SCHEMA, "D": _CRIT_SCHEMA,
            "appeal": {"type": "string"},
            "compression_risk": {
                "type": "object",
                "properties": {"level": {"type": "string", "enum": ["low", "medium", "high"]},
                               "notes": {"type": "string"},
                               "cut_candidates": {"type": "array", "minItems": 0, "maxItems": 5, "items": {"type": "string"}}},
                "required": ["level", "notes", "cut_candidates"], "additionalProperties": False,
            },
            "diversity": {
                "type": "object",
                "properties": {k: {"type": "string"} for k in ("theme", "mood", "era", "region", "narrator")},
                "required": ["theme", "mood", "era", "region", "narrator"], "additionalProperties": False,
            },
        },
        "required": ["key_facts", "A", "B", "C", "D", "appeal", "compression_risk", "diversity"],
        "additionalProperties": False,
    },
    "strict": True,
}


# ------------------------------------------------------------ 評価単位の構築(決定論)
def load_screening(wid: str) -> dict:
    with open(common.assert_not_sealed(os.path.join(SCREEN, f"{wid}.json")), encoding="utf-8") as f:
        return json.load(f)


def build_unit(wid: str) -> dict:
    p = os.path.join(SRC, SRC_DIR.get(wid, wid), "text_plain.txt")
    if not os.path.exists(p):
        raise RuntimeError(f"STOP: {wid} 一次資料(text_plain.txt)が未取得。評価に進まない。")
    with open(common.assert_not_sealed(p), encoding="utf-8") as f:
        full = f.read()
    rule = UNIT_RULES.get(wid)
    if rule:
        lines = full.split("\n")
        hs = [i for i, l in enumerate(lines) if l.strip() == rule["start_heading"]]
        he = [i for i, l in enumerate(lines) if l.strip() == rule["end_heading"]]
        if wid == "L04":      # 目次(1回目)ではなく本文見出し(2回目)を使う
            e = he[1]                       # 本文側の次作見出し(目次の1回目を除く)
            s = max(i for i in hs if i < e)  # その直前の『THE BET』見出し(目次行ではなく本文見出し)
        else:                  # L06: 章見出しの最初の出現
            s = hs[0]; e = [i for i in he if i > s][0]
        text = "\n".join(lines[s:e]).strip()
        note = rule["note"]
    else:
        text = full.strip()
        note = "作品の全文(ru.wikisource、ロシア語原作『Пари』。英訳ではない)。" if wid in RU_WORKS else "作品の全文(青空文庫の本文領域、日本語原作)。"
    is_en = wid in EN_WORKS
    is_ru = wid in RU_WORKS
    chars = len(re.sub(r"\s", "", text))
    words = len(text.split()) if is_en else None
    tok = int(words * EN_TOKENS_PER_WORD) if is_en else (int(chars * 0.7) if is_ru else int(chars * JA_TOKENS_PER_CHAR))
    return {"work_id": wid, "text": text, "lang": "English" if is_en else ("ロシア語(原語原作)" if is_ru else "日本語"), "unit_note": note,
            "chars_no_ws": chars, "words_en": words, "est_input_tokens_text": tok,
            "size_note": (f"約{words}語" if is_en else f"約{chars}文字")}


def build_messages(unit: dict, title: str) -> list:
    user = USER_TEMPLATE.format(work_id=unit["work_id"], title=title, lang=unit["lang"], unit_note=unit["unit_note"],
                                size_note=unit["size_note"], text=unit["text"], **CRITERIA_DEF)
    return [{"role": "developer", "content": DEVELOPER_MESSAGE}, {"role": "user", "content": user}]


# ------------------------------------------------------------ 決定論の後処理
def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", "", s)


def verify_quotes(parsed: dict, source_text: str) -> dict:
    src = normalize_ws(source_text)
    res, bad = {}, 0
    for c in CRITERIA:
        flags = [normalize_ws(q) in src for q in parsed[c]["evidence_quotes"]]
        res[c] = flags
        bad += flags.count(False)
    kq = [normalize_ws(q) in src for q in parsed["key_facts"]["notable_quotes"]]
    res["key_facts.notable_quotes"] = kq
    bad += kq.count(False)
    return {"per_item": res, "unverified_quote_count": bad, "all_verified": bad == 0}


def aggregate(parsed: dict, qv: dict) -> dict:
    """総合判定は決定論。委任_03: 従来基準(4項目中3項目以上PASS)と比較用新基準(3項目以上かつD PASS、D必須は仮説で正式仕様変更ではない)の両方を記録。
    引用が原文と不一致ならPASS相当はREVIEW_REQUIREDへ降格(両基準とも)。"""
    passes = [c for c in CRITERIA if parsed[c]["verdict"] == "PASS"]
    legacy = "PASS" if len(passes) >= 3 else "FAIL"
    new = "PASS" if (len(passes) >= 3 and parsed["D"]["verdict"] == "PASS") else "FAIL"
    note = []
    if not qv["all_verified"]:
        note.append("引用の一部が原文と一致しない(根拠の信頼性要確認)")
        legacy_f = "REVIEW_REQUIRED" if legacy == "PASS" else legacy
        new_f = "REVIEW_REQUIRED" if new == "PASS" else new
    else:
        legacy_f, new_f = legacy, new
    return {"pass_count": len(passes), "passed": passes,
            "legacy_rule": "pass_count>=3", "legacy_overall": legacy_f,
            "new_rule_hypothesis": "pass_count>=3 and D==PASS(比較用仮説。正式仕様変更ではない)", "new_overall": new_f,
            "criteria_disagree": legacy_f != new_f,
            "rule": "new(比較用仮説)", "overall": new_f, "notes": note}


def validate_schema_min(parsed: dict) -> None:
    for k in JSON_SCHEMA["schema"]["required"]:
        if k not in parsed:
            raise ValueError(f"missing key: {k}")
    for c in CRITERIA:
        if parsed[c]["verdict"] not in ("PASS", "FAIL"):
            raise ValueError(f"bad verdict {c}")
        if not 1 <= len(parsed[c]["evidence_quotes"]) <= 3:
            raise ValueError(f"bad quote count {c}")


# ------------------------------------------------------------ モックclient(乾式。API呼出なし)
class MockClient:
    """OpenAI Responses API互換の最小モック。本文の先頭付近から連続文字列を切り出して引用に使う(決定論)。
    wid='FORCE_BAD_QUOTE'のときは原文に無い引用を返し、検証ロジックが検出するか確認する。"""
    def __init__(self, bad_quote: bool = False):
        self.calls = 0
        self.bad_quote = bad_quote
        self.responses = self

    def create(self, **kw):
        self.calls += 1
        user = kw["input"][1]["content"]
        body = user.split("<<<BEGIN_SOURCE_TEXT\n", 1)[1].split("\nEND_SOURCE_TEXT>>>", 1)[0]
        flat = body.replace("\n", "")
        q = lambda i: flat[i * 80: i * 80 + 20] if not self.bad_quote else "this quote is not in the source"
        crit = lambda i: {"verdict": "PASS", "evidence_quotes": [q(i)], "reason": "mock", "confidence": "low"}
        out = {"key_facts": {"central_event": "mock", "main_characters": ["mock"], "turning_point": "mock", "ending": "mock",
                              "notable_quotes": [q(1)]},
               "A": crit(0), "B": crit(1), "C": crit(2), "D": crit(3), "appeal": "mock",
               "compression_risk": {"level": "low", "notes": "mock", "cut_candidates": []},
               "diversity": {k: "mock" for k in ("theme", "mood", "era", "region", "narrator")}}

        class R:
            model = kw["model"]
            id = "mock-response"
            output_text = json.dumps(out, ensure_ascii=False)
        return R()


# ------------------------------------------------------------ 1作品の評価(作品別ファイルへ書く)
def eval_one(wid: str, model: str, client, out_dir: str, title: str, mock: bool) -> dict:
    model = common.check_model(ROUTING_KEY, model)  # 許可外モデルはAPI前にfail-closed
    unit = build_unit(wid)
    kwargs = dict(model=model, reasoning={"effort": REASONING_EFFORT}, input=build_messages(unit, title),
                  text={"format": {"type": "json_schema", **JSON_SCHEMA}})
    _t0 = __import__("time").time()
    resp = client.responses.create(**kwargs)
    elapsed = round(__import__("time").time() - _t0, 2)
    actual_model_id = getattr(resp, "model", None)
    if not mock and not (actual_model_id and str(actual_model_id).startswith(model)):
        raise RuntimeError(f"STOP: actual model_idが要求と異なる requested={model} actual={actual_model_id}")
    usage = getattr(resp, "usage", None)
    parsed = json.loads(resp.output_text)
    validate_schema_min(parsed)
    qv = verify_quotes(parsed, unit["text"])
    agg = aggregate(parsed, qv)
    rec = {"work_id": wid, "title": title, "eval_version": EVAL_VERSION, "model": model, "requested_model": model,
           "actual_model_id": actual_model_id, "routing_key": ROUTING_KEY, "mock": mock,
           "usage": ({"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)} if usage else None),
           "usage_full": (usage.model_dump() if usage is not None and hasattr(usage, "model_dump") else None), "elapsed_sec": elapsed, "response_id": getattr(resp, "id", None),
           "prompt_sha256": __import__("hashlib").sha256(json.dumps(kwargs["input"], ensure_ascii=False).encode("utf-8")).hexdigest(),
           "developer_message": DEVELOPER_MESSAGE, "user_prompt_full": kwargs["input"][1]["content"], "eval_unit_id": wid,
           "reasoning_effort": REASONING_EFFORT, "evaluated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "unit": {k: unit[k] for k in ("lang", "unit_note", "chars_no_ws", "words_en", "est_input_tokens_text")},
           "result": parsed, "quote_verification": qv, "aggregate": agg}
    d = os.path.join(out_dir, model.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{wid}.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec


# ------------------------------------------------------------ 費用見積(無料・計算のみ)
def load_prices(model: str) -> dict:
    with open(PRICING_SNAPSHOT, encoding="utf-8", errors="replace") as f:
        snap = json.load(f)
    pr = {}
    for p in snap["prices"]:
        if p["model"] == model and p.get("tier") == "Standard" and p["meter"] in ("input_tokens", "cached_input_tokens", "output_tokens"):
            pr[p["meter"]] = p["price"]
    if len(pr) < 3:
        raise RuntimeError(f"STOP: {model} の単価が未登録(pricing_snapshot.json)。他modelの流用は禁止。")
    return pr


def estimate_cost(works: list, models: list, out_tokens: int = OUT_TOKENS_POINT) -> dict:
    units = {w: build_unit(w) for w in works}
    table = {}
    for m in models:
        pr = load_prices(m)
        rows, tot_pt = {}, 0.0
        for w in works:
            tin = units[w]["est_input_tokens_text"] + OVERHEAD_PROMPT_TOKENS
            usd = tin / 1e6 * pr["input_tokens"] + out_tokens / 1e6 * pr["output_tokens"]
            rows[w] = {"input_tokens": tin, "output_tokens": out_tokens, "usd": round(usd, 5), "jpy_point": round(usd * USD_JPY, 2)}
            tot_pt += usd * USD_JPY
        table[m] = {"prices_usd_per_1m": pr, "per_work": rows, "total_jpy_point": round(tot_pt, 2), "total_jpy_cap_x1_5": round(tot_pt * 1.5, 2)}
    return {"usd_jpy": USD_JPY, "assumptions": {"ja_tokens_per_char": JA_TOKENS_PER_CHAR, "en_tokens_per_word": EN_TOKENS_PER_WORD,
            "overhead_prompt_tokens": OVERHEAD_PROMPT_TOKENS, "output_tokens_point_per_call": OUT_TOKENS_POINT,
            "cache": "キャッシュ割引なし(保守)"}, "models": table}


def titles() -> dict:
    return {w: load_screening(w)["title_ja"] for w in [f"L{i:02d}" for i in range(1, 11)]}


def select_works(args) -> list:
    ids = args.works or [f"L{i:02d}" for i in range(1, 11)]
    ok = []
    for w in ids:
        dec = load_screening(w)["decision"]
        if dec == "PASS" or (dec == "REVIEW_REQUIRED" and args.include_review) or (dec == "NG" and args.include_control):
            ok.append(w)
        else:
            print(f"[skip] {w}: 権利判定={dec}(評価対象外。--include-review/--include-controlで明示した場合のみ)")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dry-run", "real", "estimate"], default="dry-run")
    ap.add_argument("--models", nargs="+", default=[PRIMARY_MODEL])  # 許可はgpt-6-lunaのみ
    ap.add_argument("--works", nargs="*")
    ap.add_argument("--include-review", action="store_true")
    ap.add_argument("--include-control", action="store_true", help="権利NG(L06)を意図的負例として品質評価する")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out-dir", default=os.path.join(BASE, "phase_c_eval"))
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0, help="ユーザーが承認した課金上限(円)。0ならrealは起動しない")
    args = ap.parse_args()
    for m in args.models:
        if m not in ALLOWED_MODELS:
            sys.exit(f"STOP: {m} は許可モデル外(Trial固定=gpt-6-luna。変更はユーザー承認が必要)。許可: {ALLOWED_MODELS}")
    works = select_works(args)
    T = titles()

    if args.mode == "estimate":
        est = estimate_cost([f"L{i:02d}" for i in range(1, 11)], list(ALLOWED_MODELS))  # 10作品分の単価表(ケース別集計はPHASE_C_COST_ESTIMATE_02_luna.md)
        os.makedirs(BASE, exist_ok=True)
        with open(os.path.join(BASE, "PHASE_C_COST_ESTIMATE_02_luna.json"), "w", encoding="utf-8") as f:
            json.dump(est, f, ensure_ascii=False, indent=2)
        print(json.dumps({m: (v["total_jpy_point"], v["total_jpy_cap_x1_5"]) for m, v in est["models"].items()}, ensure_ascii=False))
        return

    if args.mode == "dry-run":
        out = os.path.join(BASE, "phase_c_dry_run")
        client = MockClient()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            recs = list(ex.map(lambda w: eval_one(w, args.models[0], client, out, T[w], mock=True), works))
        # 悪い引用の検出確認
        bad = eval_one(works[0], args.models[0], MockClient(bad_quote=True), os.path.join(out, "_bad_quote_check"), T[works[0]], mock=True)
        summary = {"mock_calls": client.calls, "works": works,
                   "aggregates": {r["work_id"]: r["aggregate"]["overall"] for r in recs},
                   "all_quotes_verified": all(r["quote_verification"]["all_verified"] for r in recs),
                   "bad_quote_detected": (not bad["quote_verification"]["all_verified"]) and bad["aggregate"]["overall"] == "REVIEW_REQUIRED",
                   "est_input_tokens": {r["work_id"]: r["unit"]["est_input_tokens_text"] + OVERHEAD_PROMPT_TOKENS for r in recs}}
        with open(os.path.join(out, "DRY_RUN_SUMMARY.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=False))
        return

    # ---- real: 有料API。ユーザー承認の課金上限が必須。委任_01では実行しない。
    if args.approved_budget_jpy <= 0:
        sys.exit("STOP: 有料API(real)はユーザーの課金上限承認(--approved-budget-jpy > 0)が無いと起動しない。")
    est = estimate_cost(works, args.models)
    cap = sum(v["total_jpy_cap_x1_5"] for v in est["models"].values())
    if cap > args.approved_budget_jpy:
        sys.exit(f"STOP: 保守見積{cap:.1f}円が承認上限{args.approved_budget_jpy:.1f}円を超える。")
    from dotenv import load_dotenv  # lazy import: dry-run/estimateでは使わない
    load_dotenv()
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(os.path.join(args.out_dir, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    for m in args.models:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            list(ex.map(lambda w: _real_one(cl, w, m, client, args.out_dir, T[w]), works))


def _real_one(cl, w, m, client, out_dir, title):
    with cl.logging_context("FAMILY_Z_STORY_POOL_SCREENING_TRIAL_01", f"eval_{w}"):
        return eval_one(w, m, client, out_dir, title, mock=False)


if __name__ == "__main__":
    main()
