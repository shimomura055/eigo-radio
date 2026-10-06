# -*- coding: utf-8 -*-
"""OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_04: Checker再分類(4観点)の正式実装module(APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED未)。

正本(逐語移植元)=`er052_output/open233_reclassify_02/reclassify_candidates_02.py`(RECLASSIFY-02、VALIDATED)。
`DEVELOPER_MESSAGE`/`PROMPT_TEMPLATE`/`SCHEMA`は逐語(sha256一致をテストで検証)。model=gpt-6-luna、effort=medium固定(M3)。

構造(Opus M1/M2): coverage moduleの`candidate_filter`として、r3/r5候補を`union_candidates`で合流する**前**に適用する。
- 対象=model由来候補(sources[0]が`model_*`)のみ。決定論・coverage_gapは不変(Trialと同一)。
- 前回指摘と同文の候補(`protected_claims`)は対象外=候補のまま残す(Stage 2が再判定、fail-closed)。
- 判定がCANDIDATE以外(SUPPORTED/NO_FACT_CLAIM)のclaimだけ候補から除く。未返却・schema不一致・call失敗は全件CANDIDATE維持(fail-closed)。
本moduleはfilter関数を作るだけで、runner globalを変更しない(承認構成の適用は`runner.apply_open233_approved_flow_switches`)。
"""
from __future__ import annotations

import hashlib

import er052_open233_stage1_coverage_checker_01 as cov

MODEL_LABEL = "gpt-6-luna"   # 実modelはrunner.MODEL(call_fn側で使う)。ここは記録用
EFFORT = "medium"            # Trial(RECLASSIFY-02)と同一。call_fnへ明示固定する(label依存にしない)
RECLASSIFY_LABEL = "reclassify"
RECOVERY_STAGE = "stage1_reclassify"

DEVELOPER_MESSAGE = (
    "あなたはニュース記事のFact Safety分類担当です。旧Checkerが『候補』として挙げた記事中の主張を、Verified Fact Ledgerと照らして3択に再分類します。"
    "重大度の判定はしません。数値・日付・固有名・因果・否定・比較を含む主張は厳しく見て、Ledgerと一致しない限りCANDIDATEにしてください。"
)

PROMPT_TEMPLATE = """【Verified Fact Ledger】
{ledger_text}

【記事全文(文脈)】
{article_text}

【再分類の対象(旧Checkerが候補にした主張。IDつき。これらのIDだけを使う)】
{claims_block}

【問い】
各主張について、次の3択のどれかを選んでください。
- SUPPORTED: Ledgerに裏付けがある(Ledgerのfactと一致、または言い換え・平易化の範囲)。
- NO_FACT_CLAIM: 比喩・つなぎ・一般論・読者への問いかけ・導入や締めの修辞など、Ledgerにない具体的なFactを追加していない。
- CANDIDATE: Ledgerとの食い違いがある、または、Ledgerにない具体的な新事実(数値・日付・固有名・因果・仕組みなど)の追加がある。

【規則】
1. 「Ledgerに明示されていない」だけでは CANDIDATE にしない。具体的Factの食い違い、または具体的な新事実の追加がある場合だけ CANDIDATE にする。
2. ただし、数値・日付・固有名・因果・否定・比較のいずれかを含む主張は、Ledgerと一致しない限り CANDIDATE とする(厳しく見る)。特に否定の有無・極性(あった/なかった、増えた/増えていない等)、因果の結び付け(so/because/therefore等)、比較・方向(上昇/下落、より大きい/小さい)、主体(誰が何をしたか)、範囲(一部/全部、一時的/恒久)、確信度(断定/推測)をLedgerと照合する。
3. 迷った場合、その主張が上記6種類のFactのどれかに関わるなら CANDIDATE、関わらない修辞・つなぎ・一般論なら NO_FACT_CLAIM とする。
4. SUPPORTED と判定する前に、主張が述べる具体的Factごとに、次の4点がLedgerと一致しているかを必ず照合する。1つでも mismatch(Ledgerと食い違う、または広げている・落としている)なら、SUPPORTED にせず CANDIDATE とする。
   (i) 主体: 誰が行ったか(actor_match)。
   (ii) 相手先・対象: 誰/何に対して行ったか(counterpart_match)。例: Ledgerが「AがBに対して行った」とするのを、記事が「AがCに対して行った」と書いていれば mismatch。
   (iii) 対象範囲: 範囲が広がっていないか(scope_match)。
   (iv) 限定条件: 一部・テスト・時期などの限定が落ちたり変わったりしていないか(qualifier_match)。
   各点は match / mismatch / n_a(その主張にその点が関わらない)のいずれかで出す。mismatch は、Ledgerの記述と食い違う、範囲を広げる、限定を落とす・変える場合に限る。Ledgerが単にその点へ触れていないだけでは mismatch にしない(規則1と同じ)。NO_FACT_CLAIM の主張は4点とも n_a とする。
5. 判定ごとに reason(1行。4点のうち mismatch があればどの点かを含める)と fact_tags(その主張に含まれるFact種別: number/date/proper_noun/causality/negation/comparison のうち該当するもの。なければ none)を出す。
6. 対象の全IDを1件ずつ出力する。
"""

SCHEMA = {
    "name": "open233_reclassify_verdicts_v2", "strict": True,
    "schema": {"type": "object", "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "cid": {"type": "string"},
            "verdict": {"type": "string", "enum": ["SUPPORTED", "NO_FACT_CLAIM", "CANDIDATE"]},
            "fact_tags": {"type": "array", "items": {"type": "string", "enum": ["number", "date", "proper_noun", "causality", "negation", "comparison", "none"]}},
            "actor_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "counterpart_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "scope_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "qualifier_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]},
            "reason": {"type": "string"}},
        "required": ["cid", "verdict", "fact_tags", "actor_match", "counterpart_match", "scope_match", "qualifier_match", "reason"], "additionalProperties": False}}},
        "required": ["results"], "additionalProperties": False}}

VERDICTS = ("SUPPORTED", "NO_FACT_CLAIM", "CANDIDATE")


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def src_of(c: dict) -> str:
    s = c.get("sources")
    if s:
        return s[0]
    return cov.source_of((c.get("routes") or ["r3"])[0], (c.get("sub_reasons") or [""])[0])


def is_model(c: dict) -> bool:
    return src_of(c).startswith("model_")


def ckey(c: dict) -> str:
    return "|".join(c.get("unit_ids") or []) or ("TXT:" + (c.get("claim_text") or ""))


def is_protected(claim_text: str, protected_claims) -> bool:
    """前回指摘と同文(`cov.prior_issue_resolution`の`same_text`条件と同一)なら再分類の対象外(M2)。"""
    ct = cov.norm_sentence(claim_text or "")
    for p in protected_claims or ():
        nc = cov.norm_sentence(p or "")
        if nc and ct and len(nc) >= 8 and (nc in ct or ct in nc):
            return True
    return False


def claims_for_candidates(cands: list, protected_claims=()) -> tuple:
    """(再分類対象items, 保護されたkey集合)。対象=model由来の一意claim(keyは単位ID列、Trialと同一)。cidはC1..。"""
    d, prot = {}, set()
    for c in cands:
        if not is_model(c):
            continue
        k = ckey(c)
        if is_protected(c.get("claim_text"), protected_claims):
            prot.add(k)
            continue
        x = d.setdefault(k, {"key": k, "claim_text": c.get("claim_text") or "", "routes": [], "related": []})
        for r in (c.get("routes") or [])[:1]:
            if r not in x["routes"]:
                x["routes"].append(r)
        for r in c.get("related_fact_ids") or []:
            if r not in x["related"]:
                x["related"].append(r)
    items = [x for k, x in d.items() if k not in prot]
    for i, x in enumerate(items, 1):
        x["cid"] = f"C{i}"
    return items, prot


def build_prompt(fixture: dict, items: list) -> str:
    lines = []
    for x in items:
        dirs = "/".join({"r3": "記事→Ledger", "r5": "Ledger→記事"}[r] for r in x["routes"])
        ref = ",".join(x["related"]) or "-"
        lines.append(f'[{x["cid"]}] (旧Checkerの方向: {dirs}; 旧Checkerが照合したfactID: {ref}) {x["claim_text"]}')
    return PROMPT_TEMPLATE.format(ledger_text=fixture["ledger_text"], article_text=fixture["article_text"], claims_block="\n".join(lines))


def reclassify_candidates(fixture: dict, cands: list, call_fn, protected_claims=()) -> tuple:
    """(kept_cands, info)。合流前の経路別候補listを受け、model由来でCANDIDATE以外と判定されたclaimのentryを除く。
    fail-closed: call失敗・未返却・schema不一致(enum外)・call例外は全件CANDIDATE維持(除外0)。
    info.status: `no_target`(対象0件、callなし) / `ok`(callが返った。未返却claimは`n_failclosed`) / `failed`(call失敗、全件維持)。"""
    items, prot = claims_for_candidates(cands, protected_claims)
    info = {"status": "no_target", "n_entries_in": len(cands), "n_model_entries": sum(1 for c in cands if is_model(c)),
            "n_targets": len(items), "n_protected_keys": len(prot), "n_excluded_claims": 0, "n_excluded_entries": 0,
            "n_excluded_with_changed_number": 0, "n_failclosed": 0, "calls": [], "cost_jpy": 0.0, "verdicts": [],
            "effort": EFFORT, "prompt_sha256": None}
    if not items:
        return list(cands), info
    prompt = build_prompt(fixture, items)
    info["prompt_sha256"] = sha256_text(prompt)
    calls: list = []
    try:
        parsed = cov._call_with_one_retry(call_fn, RECLASSIFY_LABEL, DEVELOPER_MESSAGE, prompt, SCHEMA, calls)
    except Exception as e:  # noqa: BLE001  TrialAbort(予算・連続エラー停止)は握りつぶさず再送出する
        if type(e).__name__ == "TrialAbort":
            raise
        parsed = None
        calls.append({"label": RECLASSIFY_LABEL, "error": f"{type(e).__name__}: {e}", "ok": False})
    info["calls"] = calls
    info["cost_jpy"] = round(sum((c.get("cost_jpy") or 0.0) for c in calls), 4)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("results"), list):
        info["status"] = "failed"
        info["n_failclosed"] = len(items)
        return list(cands), info
    info["status"] = "ok"
    res = {}
    for r in parsed["results"]:
        if isinstance(r, dict) and isinstance(r.get("cid"), str) and r.get("verdict") in VERDICTS:
            res.setdefault(r["cid"], r)
    drop_keys = set()
    for x in items:
        r = res.get(x["cid"])
        if r is None:
            info["n_failclosed"] += 1  # 未返却/enum外=CANDIDATE維持
            info["verdicts"].append({"cid": x["cid"], "key": x["key"], "claim": x["claim_text"], "verdict": "CANDIDATE",
                                     "failclosed": True, "excluded": False})
            continue
        excluded = r["verdict"] != "CANDIDATE"
        if excluded:
            drop_keys.add(x["key"])
        info["verdicts"].append({
            "cid": x["cid"], "key": x["key"], "claim": x["claim_text"], "verdict": r["verdict"], "failclosed": False,
            "excluded": excluded, "reason": r.get("reason"), "fact_tags": r.get("fact_tags"),
            **{k: r.get(k) for k in ("actor_match", "counterpart_match", "scope_match", "qualifier_match")}})
    kept = []
    for c in cands:
        if is_model(c) and ckey(c) in drop_keys:
            info["n_excluded_entries"] += 1
            if c.get("flags", {}).get("changed_number"):
                info["n_excluded_with_changed_number"] += 1
            continue
        kept.append(c)
    info["n_excluded_claims"] = len(drop_keys)
    return kept, info


def make_candidate_filter(fixture: dict, call_fn, protected_claims=()):
    """`cov.run_*`の`candidate_filter`引数へ渡すcallable(cands)->(kept, info)。`protected_claims`は呼び出し時に評価
    (listを渡せば後からの追記も反映される)。"""
    def _filter(cands: list) -> tuple:
        return reclassify_candidates(fixture, cands, call_fn, protected_claims)
    return _filter
