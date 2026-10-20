# -*- coding: utf-8 -*-
"""FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 harness lib (Trial専用/DEV path)。

目的: 「同一出典・Web検索なし」で、Family X Researcher(Fact抽出・構造化)と検証の方式を比較する。
Production(vfl01 Prompt/schema、run_researcher_for_topic、run_verification_for_topic、B3、Writer)は
**変更しない**。Production Prompt本文は`er003_v1_en_direct_vfl_01_generate`から**importして**使い、
Trial固有差分は下記の明示的な置換/挿入だけにする(差分はtestで固定)。

Production同等性の限界(設計書 §1-4):
 (1) Production Researcherは`web_search` toolを持つ1回のResponses呼出で検索+抽出を同時に行う。
     本harnessは検索toolを渡さず、取得済み出典本文をuser入力へ同梱する(検索由来の行動差は測れない)。
 (2) Production検証もweb_searchで再照合するが、本harnessでは同梱出典だけを根拠にする。
 (3) 出典本文はHTMLからのテキスト化+本文切出し済み(ナビ等除去)。Productionモデルが検索で見る断片とは異なる。
 (4) 1 Trial runのPrompt変更が検索回数へ与える影響は本harnessでは測れない(設計書 S-check)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "docs", "pm", "tools"))

TRIAL_ID = "FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01"
THEME_TAG = "XRFR_TRIAL_01"
DOC_DIR = os.path.join(ROOT, "docs", "research", "FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01")
OUT_ROOT = os.path.join(ROOT, "er085_output", "research_fact_retention_trial_01")
USD_JPY = 160.0
PRICING_REL = "er005_output/cost_baseline_01/pricing_snapshot.json"

# ---------------------------------------------------------------------------
# 基本ユーティリティ
# ---------------------------------------------------------------------------


def read_text(p: str) -> str:
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def write_text(p: str, s: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def write_json(p: str, o) -> None:
    write_text(p, json.dumps(o, ensure_ascii=False, indent=2))


def read_json(p: str):
    return json.loads(read_text(p))


def append_jsonl(p: str, o) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def norm_q(s: str) -> str:
    """引用符の揺れ(“”‘’と"')を正規化した上で空白を畳む。gold引用と出典本文の照合用。"""
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'")):
        s = s.replace(a, b)
    return norm_ws(s)


def assert_under_out_root(path: str, out_root: str = OUT_ROOT) -> None:
    ap = os.path.abspath(path)
    if not (ap == os.path.abspath(out_root) or ap.startswith(os.path.abspath(out_root) + os.sep)):
        raise RuntimeError(f"[STOP] out_root外への書込み禁止: {ap}")


# ---------------------------------------------------------------------------
# 出典(本文切出し)
# ---------------------------------------------------------------------------


def extract_body(raw_text: str, rule: dict) -> str:
    """rule: start(marker、含む) / end(marker、含まない) / drop([[from,to],...] を本文から除去)。
    各行をstripし空行を除いて返す。marker未検出は例外(黙って全文を返さない)。"""
    i = raw_text.find(rule["start"])
    if i < 0:
        raise ValueError(f"start marker not found: {rule['start']!r}")
    j = raw_text.find(rule["end"], i + len(rule["start"]))
    if j < 0:
        raise ValueError(f"end marker not found: {rule['end']!r}")
    body = raw_text[i:j]
    for a, b in rule.get("drop", []):
        x = body.find(a)
        if x >= 0:
            y = body.find(b, x)
            if y >= 0:
                body = body[:x] + body[y + len(b):]
    lines = [ln.strip() for ln in body.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def load_sources_spec(path: str | None = None) -> dict:
    return read_json(path or os.path.join(DOC_DIR, "sources_spec_01.json"))


def prepare_sources(spec: dict, out_root: str = OUT_ROOT) -> dict:
    """sources_raw/ -> sources/<topic>/<id>.txt と manifest(sha・文字数)を作る。無料・API 0。"""
    manifest = {"trial_id": TRIAL_ID, "topics": {}}
    for topic, tdef in spec["topics"].items():
        entries = []
        for s in tdef["sources"]:
            raw = read_text(os.path.join(out_root, "sources_raw", s["raw"]))
            body = extract_body(raw, s)
            outp = os.path.join(out_root, "sources", topic, f"{s['id']}.txt")
            write_text(outp, body)
            entries.append({"id": s["id"], "url": s["url"], "title": s["title"], "date": s["date"], "http": s["http"],
                            "fetched_at": s["fetched_at"], "raw_sha256": sha256_text(raw), "body_sha256": sha256_text(body),
                            "body_chars": len(body)})
        manifest["topics"][topic] = {"topic_text": tdef["topic_text"], "sources": entries}
    write_json(os.path.join(out_root, "sources_manifest_01.json"), manifest)
    return manifest


def load_packet(topic: str, spec: dict, out_root: str = OUT_ROOT) -> list:
    packet = []
    for s in spec["topics"][topic]["sources"]:
        body = read_text(os.path.join(out_root, "sources", topic, f"{s['id']}.txt"))
        packet.append({"id": s["id"], "url": s["url"], "title": s["title"], "date": s["date"], "body": body})
    return packet


def render_packet(packet: list) -> str:
    parts = []
    for s in packet:
        parts.append(f"--- 出典{s['id']} ---\nsource_title: {s['title']}\nsource_url: {s['url']}\n公開日: {s['date']}\n本文:\n{s['body']}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Prompt(Production本文はvfl01からimportし、Trial差分は下記のみ)
# ---------------------------------------------------------------------------
# E0(現行再現)の差分は2点のみ(No-search化。全方式共通):
#  (r1) 先頭文の「Webで調査し」を、同梱出典だけを根拠とする文へ置換する
#  (r2) 末尾に【取得済み出典】ブロックを追加する
# 検証(V0)の差分も同様に2点: (v1)「独立してWeb検索により再照合」を同梱出典のみの再照合へ置換 (v2)末尾に【取得済み出典】
R1_OLD = "今回のテーマについて、Webで調査し、Verified Fact Ledgerの下書きを作成してください。"
R1_NEW = ("今回のテーマについて、末尾の【取得済み出典】に同梱されたテキストだけを根拠に、"
          "Verified Fact Ledgerの下書きを作成してください。Web検索は行えません。")
V1_OLD = "独立してWeb検索により再照合してください。"
V1_NEW = "末尾の【取得済み出典】に同梱されたテキストだけを根拠に再照合してください。Web検索は行えません。"
SOURCE_HEADER = "\n\n【取得済み出典】(この出典テキストだけを根拠とする。出典に書かれていない事実を補わない)\n"

# 方式A: Researcher Promptへ第5/第6観点を追加(RESEARCH_GAP_ROOT_CAUSE_01 §5-3の案を逐語)
A_INSERT = """
5. 帰属・行為主体: 出典が事象の責任主体・行為主体(例: 誰が攻撃した/発表した/決定した)を明示している場合に限り、claimに「誰がそう述べているか/誰の行為と述べているか」を省かず帰属表現で記す。出典が主体に触れない、または出典間で異なる場合は、その差をambiguityに記す。出典が明示していない主体・動機は書かない
6. 直接の文脈(任意): 同一出典が明示する当該Factの直接の背景(例: 当該声明が併記する戦況・対立)は、conditionsまたはnotes_for_writerに最大2文で保持する。因果は出典が述べている場合のみCAUSAL_STATED_BY_SOURCEとし、出典が述べていない因果・動機は書かない
"""
A_ANCHOR = "\n\n【出力形式】"

# 方式B: Trial専用schema(actor/contextを任意欄として追加)と、その出力形式の説明
B_PROMPT_ADD = """各Factには、次の2欄も任意で記入できます(該当しなければnull)。
- actor: 出典が当該Factの行為主体・責任主体・発言主体を明示している場合に限り、その名称と役割を出典の表現どおりに記す。出典が明示していない主体・動機は書かない。
- context: 同一出典が明示する当該Factの直接の背景・文脈を最大2文で記す。出典が述べていない因果・動機は書かない。
"""
B_ANCHOR = "数字・期間・対象範囲があるFactについては、該当項目を必ず明示してください。"

# 方式C/D: 検証に1行追加(省略検知)
VC_LINE = ("- claimが、出典内で明示された重要な帰属(行為主体・責任主体・発言主体)や直接の文脈を省いていないか"
           "(省略があればAMBIGUOUSとし、verification_notesに省かれた内容を出典の表現で記す。出典に書かれていない主体・文脈は要求しない)")
VC_ANCHOR = "\n\n各fact_idについて"

# 方式E: 保持監査(追加LLM呼出)
AUDIT_DEV = "あなたはFact Ledger下書きの『保持監査』担当です。出典に明示された情報の脱落だけを点検し、新しい解釈や推測は加えません。"
AUDIT_TEMPLATE = """以下は、取得済み出典から作成されたFact Ledger下書きです。出典に**明示されている**次の情報が、下書きのFactから脱落していないか点検してください。

- 主体: 誰が行ったか(行為主体・責任主体・発言主体)
- 行為・対象: 何を、誰に対して行ったか
- 背景・文脈: 出来事の理解に必要な、同一出典が明示する直接の関連情報
- 理由・動機は、出典が明示している場合のみ

【対象テーマ】
{topic}

【Fact Ledger下書き】
{ledger_json}

【ルール】
- 脱落している情報があれば、追加Factとして出力する(fact_idは AU01, AU02, ... )。出力形式は下書きと同じ項目。
- 既に下書きのFactに含まれている情報は追加しない。出典が明示していない主体・動機・因果は絶対に追加しない。
- 脱落が無ければ facts を空配列で返す。
{packet_block}"""


def _vfl01():
    import er003_v1_en_direct_vfl_01_generate as vfl01
    return vfl01


def build_researcher_prompt(rvar: str, topic_text: str, packet: list) -> tuple:
    """(developer, user, schema) を返す。rvar in R0/RA/RB。"""
    v = _vfl01()
    base = v.build_researcher_prompt(topic=topic_text)
    if R1_OLD not in base:
        raise RuntimeError("Production researcher prompt changed: R1_OLD not found")
    p = base.replace(R1_OLD, R1_NEW)
    schema = v.FACT_LEDGER_JSON_SCHEMA
    if rvar == "RA":
        if A_ANCHOR not in p:
            raise RuntimeError("A_ANCHOR not found")
        p = p.replace(A_ANCHOR, A_INSERT.rstrip("\n") + A_ANCHOR, 1)
    elif rvar == "RB":
        if B_ANCHOR not in p:
            raise RuntimeError("B_ANCHOR not found")
        p = p.replace(B_ANCHOR, B_PROMPT_ADD + B_ANCHOR, 1)
        schema = trial_schema_b()
    elif rvar != "R0":
        raise ValueError(rvar)
    p = p + SOURCE_HEADER + render_packet(packet)
    return v.RESEARCHER_DEVELOPER_MESSAGE, p, schema


def build_verification_prompt(vvar: str, topic_text: str, ledger_parsed: dict, packet: list) -> tuple:
    """vvar in V0/VC。(developer, user, schema)"""
    v = _vfl01()
    base = v.build_verification_prompt(topic_text, ledger_parsed)
    if V1_OLD not in base:
        raise RuntimeError("Production verification prompt changed: V1_OLD not found")
    p = base.replace(V1_OLD, V1_NEW)
    if vvar == "VC":
        if VC_ANCHOR not in p:
            raise RuntimeError("VC_ANCHOR not found")
        p = p.replace(VC_ANCHOR, "\n" + VC_LINE + VC_ANCHOR, 1)
    elif vvar != "V0":
        raise ValueError(vvar)
    p = p + SOURCE_HEADER + render_packet(packet)
    return v.VERIFICATION_DEVELOPER_MESSAGE, p, v.VERIFICATION_JSON_SCHEMA


def build_audit_prompt(topic_text: str, draft_parsed: dict, packet: list) -> tuple:
    v = _vfl01()
    p = AUDIT_TEMPLATE.format(topic=topic_text, ledger_json=json.dumps(draft_parsed, ensure_ascii=False, indent=2),
                              packet_block=SOURCE_HEADER + render_packet(packet))
    return AUDIT_DEV, p, v.FACT_LEDGER_JSON_SCHEMA


def trial_schema_b() -> dict:
    """Production FACT_LEDGER_JSON_SCHEMAのdeep copy + actor/context(nullable string、required)。Ledger本体schemaは不変。"""
    import copy
    s = copy.deepcopy(_vfl01().FACT_LEDGER_JSON_SCHEMA)
    s["name"] = "verified_fact_ledger_draft_trial_b"
    item = s["schema"]["properties"]["facts"]["items"]
    item["properties"]["actor"] = {"type": ["string", "null"]}
    item["properties"]["context"] = {"type": ["string", "null"]}
    item["required"] = list(item["required"]) + ["actor", "context"]
    return s


def fold_b_to_ledger(parsed_b: dict) -> dict:
    """Bのactor/contextを、Ledger本体schemaの既存欄(conditions/notes_for_writer)へ決定論で畳み込む(LLM 0)。
    conditions/notes_for_writerは`build_verified_ledger_text`が出力する欄。"""
    facts = []
    for f in parsed_b["facts"]:
        g = {k: v for k, v in f.items() if k not in ("actor", "context")}
        if f.get("actor"):
            g["conditions"] = _join(g.get("conditions"), f"【主体】{f['actor']}")
        if f.get("context"):
            g["notes_for_writer"] = _join(g.get("notes_for_writer"), f"【背景】{f['context']}")
        facts.append(g)
    return {"facts": facts}


def merge_audit(draft: dict, audit: dict) -> dict:
    """E: 下書き+保持監査の追加Factを統合(fact_idはAU..のまま、重複idは付番し直す)。"""
    seen = {f["fact_id"] for f in draft["facts"]}
    facts = list(draft["facts"])
    n = 0
    for f in audit.get("facts", []):
        fid = f["fact_id"]
        if fid in seen:
            n += 1
            fid = f"AU{900 + n}"
        seen.add(fid)
        facts.append({**f, "fact_id": fid})
    return {"facts": facts}


def _join(a, b) -> str:
    return f"{a} {b}".strip() if a else b


# ---------------------------------------------------------------------------
# mini schema validator(Ledger本体schemaへの適合確認。jsonschema非依存)
# ---------------------------------------------------------------------------


def validate_schema(obj, schema, path="$") -> list:
    errs = []
    t = schema.get("type")
    types = t if isinstance(t, list) else ([t] if t else [])
    pymap = {"string": str, "object": dict, "array": list, "null": type(None), "number": (int, float), "integer": int, "boolean": bool}
    if types and not any(isinstance(obj, pymap[x]) for x in types):
        return [f"{path}: type {type(obj).__name__} not in {types}"]
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} not in enum")
    if isinstance(obj, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}: missing {k}")
        if schema.get("additionalProperties") is False:
            for k in obj:
                if k not in props:
                    errs.append(f"{path}: extra {k}")
        for k, sub in props.items():
            if k in obj:
                errs += validate_schema(obj[k], sub, f"{path}.{k}")
    elif isinstance(obj, list) and "items" in schema:
        for i, x in enumerate(obj):
            errs += validate_schema(x, schema["items"], f"{path}[{i}]")
    return errs


def validate_ledger_draft(parsed: dict) -> list:
    return validate_schema(parsed, _vfl01().FACT_LEDGER_JSON_SCHEMA["schema"])


# ---------------------------------------------------------------------------
# 費用・LLM呼出
# ---------------------------------------------------------------------------


def _price(model: str, meter: str) -> float:
    import daily_dev_cost_01 as dd
    prices = dd.load_prices(ROOT)
    p = dd.find_price(prices, "openai", model, meter)
    if p is None:
        raise RuntimeError(f"pricing not found: openai/{model}/{meter} (fail-closed)")
    return p


def cost_jpy(model: str, in_tok: int, out_tok: int, web_search_calls: int = 0) -> float:
    usd = (in_tok or 0) * _price(model, "input_tokens") / 1e6 + (out_tok or 0) * _price(model, "output_tokens") / 1e6
    if web_search_calls:
        usd += web_search_calls * 10.0 / 1000
    return usd * USD_JPY


def usage_dict(resp) -> dict:
    u = getattr(resp, "usage", None)
    d = {"input_tokens": getattr(u, "input_tokens", 0) or 0, "output_tokens": getattr(u, "output_tokens", 0) or 0}
    od = getattr(u, "output_tokens_details", None)
    d["reasoning_tokens"] = getattr(od, "reasoning_tokens", 0) if od is not None else 0
    idt = getattr(u, "input_tokens_details", None)
    d["cached_input_tokens"] = getattr(idt, "cached_tokens", 0) if idt is not None else 0
    return d


class BudgetGuard:
    def __init__(self, calls_log: str, cap_jpy: float):
        self.calls_log = calls_log
        self.cap = cap_jpy

    def spent(self) -> float:
        if not os.path.exists(self.calls_log):
            return 0.0
        tot = 0.0
        for ln in read_text(self.calls_log).splitlines():
            if ln.strip():
                tot += json.loads(ln).get("cost_jpy", 0.0)
        return tot

    def check(self, est_next: float = 1.5) -> None:
        s = self.spent()
        if s + est_next > self.cap:
            raise RuntimeError(f"[BUDGET_GUARD] spent={s:.2f} + next~{est_next} > cap {self.cap} JPY. STOP")


def llm_call(client, stage: str, dev: str, user: str, schema: dict, *, model: str, effort: str, guard: BudgetGuard | None,
             dry_run: bool, meta: dict) -> dict:
    """検索toolなしの1回呼出(web_search_call_count=0を明示記録)。"""
    if guard is not None:
        guard.check()
    t0 = time.time()
    resp = client.responses.create(
        model=model, reasoning={"effort": effort},
        text={"format": {"type": "json_schema", **schema}},
        input=[{"role": "developer", "content": dev}, {"role": "user", "content": user}],
    )
    latency = time.time() - t0
    ws = sum(1 for it in (getattr(resp, "output", None) or []) if getattr(it, "type", None) == "web_search_call")
    usage = usage_dict(resp)
    rec = {
        "stage": stage, "model_requested": model, "model_returned": getattr(resp, "model", None), "response_id": getattr(resp, "id", None),
        "latency_seconds": round(latency, 3), "usage": usage, "web_search_call_count": ws,
        "cost_jpy": round(cost_jpy(model, usage["input_tokens"], usage["output_tokens"], ws), 4), "dry_run": dry_run,
        "prompt_sha256": sha256_text(dev + "\n" + user), "parsed": json.loads(resp.output_text), **meta,
    }
    return rec


# ---------------------------------------------------------------------------
# Stub(dry-run用。API 0。**合成応答であり実LLM結果ではない**)
# ---------------------------------------------------------------------------


class StubClient:
    def __init__(self):
        self.responses = SimpleNamespace(create=self._create)
        self.calls = 0

    def _create(self, **kw):
        self.calls += 1
        schema_name = kw["text"]["format"]["name"]
        user = kw["input"][1]["content"]
        if schema_name.startswith("verified_fact_ledger_draft"):
            facts = []
            for i, m in enumerate(re.finditer(r"source_url: (\S+)", user)):
                f = {"fact_id": f"F{i + 1:02d}", "claim": f"(stub) 出典{i + 1}の要点", "subject": "stub", "date_or_period": None, "scope": None,
                     "conditions": None, "numeric_value": None, "numeric_scope": None, "causal_strength": "OBSERVED_REPORTED",
                     "source_title": "stub", "source_url": m.group(1), "source_type": "OTHER", "support_level": "DIRECTLY_STATED",
                     "ambiguity": None, "notes_for_writer": None}
                if schema_name.endswith("_b"):
                    f["actor"] = "(stub actor)"
                    f["context"] = None
                facts.append(f)
            if "保持監査" in kw["input"][0]["content"]:
                facts = []
            out = {"facts": facts}
        else:
            ids = re.findall(r'"fact_id": "([^"]+)"', user)
            out = {"verifications": [{"fact_id": i, "verdict": "VERIFIED", "verification_notes": "(stub)"} for i in dict.fromkeys(ids)]}
        text = json.dumps(out, ensure_ascii=False)
        usage = SimpleNamespace(input_tokens=max(1, len(user) // 3), output_tokens=max(1, len(text) // 2),
                                input_tokens_details=SimpleNamespace(cached_tokens=0),
                                output_tokens_details=SimpleNamespace(reasoning_tokens=0))
        return SimpleNamespace(output_text=text, model=kw["model"], id=f"stub-{self.calls}", usage=usage, output=[])


# ---------------------------------------------------------------------------
# Pipeline: stage定義と方式
# ---------------------------------------------------------------------------
# 方式 -> 必要stage列。stage名: R0/RA/RB (Researcher), V0@R0 等 (検証), AU@R0 (保持監査)
VARIANTS = {
    "E0": {"research": "R0", "audit": False, "verify": "V0"},
    "A": {"research": "RA", "audit": False, "verify": "V0"},
    "B": {"research": "RB", "audit": False, "verify": "V0"},
    "C": {"research": "R0", "audit": False, "verify": "VC"},
    "D": {"research": "RA", "audit": False, "verify": "VC"},
    "E": {"research": "R0", "audit": True, "verify": "V0"},
}
# 追加LLM呼出数(現行E0=Researcher1+検証1=2回に対する増分): A/B/C/D=0, E=+1(保持監査)


def stage_path(cell_dir: str, name: str) -> str:
    return os.path.join(cell_dir, "stages", name.replace("@", "__") + ".json")


def run_stage(client, cell_dir: str, name: str, builder, *, model, effort, guard, dry_run, meta) -> dict:
    p = stage_path(cell_dir, name)
    if os.path.exists(p):
        return read_json(p)
    dev, user, schema = builder()
    write_text(p.replace(".json", ".prompt.txt"), f"[developer]\n{dev}\n\n[user]\n{user}")
    rec = llm_call(client, name, dev, user, schema, model=model, effort=effort, guard=guard, dry_run=dry_run, meta=meta)
    write_json(p, rec)
    append_jsonl(os.path.join(os.path.dirname(os.path.dirname(cell_dir)), "calls_dryrun.jsonl" if dry_run else "calls_real.jsonl"),
                 {k: v for k, v in rec.items() if k != "parsed"})
    return rec


def run_variant(client, variant: str, topic: str, sample: int, spec: dict, out_root: str, *, guard, dry_run: bool) -> dict:
    """1 (variant, topic, sample)を実行。stageは (topic,sample) 内でcacheし、方式間でR0等を共有する(同一出典・paired比較)。"""
    vd = VARIANTS[variant]
    v = _vfl01()
    model, effort = v.MODEL, v.REASONING_EFFORT
    cell_dir = os.path.join(out_root, "_dryrun" if dry_run else "", topic, f"s{sample}")
    cell_dir = os.path.normpath(cell_dir)
    assert_under_out_root(cell_dir, out_root)
    topic_text = spec["topics"][topic]["topic_text"]
    packet = load_packet(topic, spec, out_root)
    meta = {"topic": topic, "sample": sample, "trial_id": TRIAL_ID}
    kw = dict(model=model, effort=effort, guard=guard, dry_run=dry_run, meta=meta)

    r = run_stage(client, cell_dir, vd["research"], lambda: build_researcher_prompt(vd["research"], topic_text, packet), **kw)
    stages = [r]
    draft = fold_b_to_ledger(r["parsed"]) if vd["research"] == "RB" else r["parsed"]
    verify_in_name = vd["research"]
    if vd["audit"]:
        au = run_stage(client, cell_dir, f"AU@{vd['research']}", lambda: build_audit_prompt(topic_text, draft, packet), **kw)
        stages.append(au)
        draft = merge_audit(draft, au["parsed"])
        verify_in_name = f"E({vd['research']})"
    vstage = f"{vd['verify']}@{verify_in_name}"
    ver = run_stage(client, cell_dir, vstage, lambda: build_verification_prompt(vd["verify"], topic_text, draft, packet), **kw)
    stages.append(ver)
    ledger_text, counts, kept = v.build_verified_ledger_text(draft, ver["parsed"])
    vdir = os.path.join(cell_dir, variant)
    write_json(os.path.join(vdir, "draft.json"), draft)
    write_json(os.path.join(vdir, "verification.json"), ver["parsed"])
    write_text(os.path.join(vdir, "verified_fact_ledger.txt"), ledger_text)
    schema_errs = validate_ledger_draft(draft)
    summary = {
        "variant": variant, "topic": topic, "sample": sample, "dry_run": dry_run, "n_facts_draft": len(draft["facts"]),
        "verdict_counts": counts, "n_kept": len(kept), "schema_errors": schema_errs,
        "stage_names": [s["stage"] for s in stages], "n_llm_calls": len(stages), "web_search_calls": sum(s["web_search_call_count"] for s in stages),
        "cost_jpy": round(sum(s["cost_jpy"] for s in stages), 4), "latency_seconds": round(sum(s["latency_seconds"] for s in stages), 2),
        "input_tokens": sum(s["usage"]["input_tokens"] for s in stages), "output_tokens": sum(s["usage"]["output_tokens"] for s in stages),
        "model_returned": sorted({s["model_returned"] for s in stages if s["model_returned"]}),
    }
    write_json(os.path.join(vdir, "summary.json"), summary)
    return summary


# ---------------------------------------------------------------------------
# 評価(gold一致・創作候補フラグ)
# ---------------------------------------------------------------------------


def split_blocks(ledger_text: str) -> list:
    """rendered Ledgerを Fact単位ブロックに分割: [{'fact_id','tag','text'}]"""
    blocks = []
    for chunk in re.split(r"\n\s*\n", ledger_text.strip()):
        m = re.match(r"\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+):", chunk.strip())
        if m:
            blocks.append({"fact_id": m.group(2), "tag": m.group(1).split(" ")[0], "text": chunk.strip()})
    return blocks


def fact_text(f: dict) -> str:
    """下書きFactの全文(rendered Ledgerと違いambiguity等も含む=draft段階の保持判定用)"""
    keys = ("claim", "scope", "conditions", "ambiguity", "notes_for_writer", "numeric_scope", "actor", "context")
    return "\n".join(str(f.get(k)) for k in keys if f.get(k))


def item_matches(item: dict, text: str) -> bool:
    return all(re.search(g, text, re.I) for g in item["groups"])


def match_gold(items: list, texts: list) -> dict:
    """texts: ブロック文字列のlist。item_id -> 一致したindex(最初)またはNone"""
    out = {}
    for it in items:
        out[it["id"]] = next((i for i, t in enumerate(texts) if item_matches(it, t)), None)
    return out


MOTIVE_CAUSAL_RE = re.compile(r"(動機|狙い|報復|対抗|意図|目的で|目的は|が原因|を引き起こ|によって引き起こ|の結果として|ことを理由に|理由は|背景には)")


def fabrication_flags(blocks: list, watch: list) -> list:
    """創作候補フラグ(機械)。ブロックごとに [{'fact_id','reasons':[...]}]。最終判定は出典逐語照合のadjudication。"""
    flags = []
    for b in blocks:
        reasons = []
        t = b["text"]
        if MOTIVE_CAUSAL_RE.search(t):
            reasons.append("motive_causal_marker")
        if "CAUSAL_STATED_BY_SOURCE" in t:
            reasons.append("causal_stated_by_source")
        for w in watch:
            if re.search(w["pattern"], t, re.I):
                reasons.append("watch:" + w["id"])
        if reasons:
            flags.append({"fact_id": b["fact_id"], "reasons": reasons})
    return flags
