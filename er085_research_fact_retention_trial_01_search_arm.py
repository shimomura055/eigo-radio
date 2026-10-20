# -*- coding: utf-8 -*-
"""FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_02 検索込み腕(Trial専用wrapper、設計v02 §9-2)。

目的: Production経路と同一の `er012_e_family_entertainment_two_level_runner_01.run_researcher_for_topic`
(web_search tool固定・同一引数 client, topic)を、E0(Prompt不変)/A(Prompt第5・6観点のみ差分)/D(A+検証1行)で
各 sample 回呼び、(1)検索回数・token・費用・時間 (2)Ledger draftへの主体・文脈の保持(出典逐語照合)を測る。

安全:
 - Productionファイルは変更しない。Prompt差分は **このprocess内だけ** の context manager で
   `vfl01.build_researcher_prompt` / `vfl01.build_verification_prompt` を差し替え、終了時に必ず復元する。
   E0はPrompt不変(差し替えなし)で、Production関数の出力 Prompt と一致することをrun前に assert する。
 - 出力先は <OUT_ROOT>/search_arm/ のみ(Production run dir・Ledgerへ書かない)。harness側から別途Web検索しない。
 - 追加の無料HTTP取得(`--fetch-sources`)は、各runが **実際に引用した出典URL** の本文取得のみ(検索ではない)。
 - 異常STOP: 1 runの web_search_call_count が STOP_WS (=40、Production実績20の2倍) を超えたら即中断。
 - 起動はflagなし(Trial専用CLI)。Production起動経路・.env等からは呼ばれない。

使い方:
  --variants E0 A D --topic mey --samples 2 --out <dir under OUT_ROOT> --budget-jpy N [--dry-run]
  --fetch-sources --out <dir>        (各runの引用URLを無料HTTP取得 -> <out>/_sources/)
  --score --out <dir> --report <md>  (主体・文脈の保持採点。API 0)
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import hashlib
import html as htmllib
import json
import os
import re
import subprocess
import sys
import time
from types import SimpleNamespace

import er085_research_fact_retention_trial_01_lib as lib

STOP_WS = 40                      # 1 runの検索回数がこれを超えたら異常STOP(Production実績20の2倍)
SEARCH_ARM_VARIANTS = ("E0", "A", "D")
EST_RUN_JPY = {"E0": 30.0, "A": 30.0, "D": 40.0}   # BudgetGuard用の次呼出見込み(Researcher ~27、D=+検証~9)

# ---------------------------------------------------------------------------
# Prompt差分(context manager。Production moduleのprocess内差し替え→復元)
# ---------------------------------------------------------------------------


def a_prompt(base_prompt: str) -> str:
    """方式A: Researcher Promptへ第5・6観点を挿入(libのA_INSERT/A_ANCHORを再利用。検索なしharnessと同一文言)。"""
    if lib.A_ANCHOR not in base_prompt:
        raise RuntimeError("A_ANCHOR not found in Production researcher prompt")
    return base_prompt.replace(lib.A_ANCHOR, lib.A_INSERT.rstrip("\n") + lib.A_ANCHOR, 1)


def vc_prompt(base_prompt: str) -> str:
    """方式C/D: 検証Promptへ1行追加(libのVC_LINE/VC_ANCHOR)。"""
    if lib.VC_ANCHOR not in base_prompt:
        raise RuntimeError("VC_ANCHOR not found in Production verification prompt")
    return base_prompt.replace(lib.VC_ANCHOR, "\n" + lib.VC_LINE + lib.VC_ANCHOR, 1)


@contextlib.contextmanager
def patched_prompts(variant: str):
    """E0: 差し替えなし。A: researcher promptのみ。D: researcher(A)+verification(VC)。終了時に必ず復元。"""
    v = lib._vfl01()
    orig_r, orig_v = v.build_researcher_prompt, v.build_verification_prompt
    try:
        if variant in ("A", "D"):
            v.build_researcher_prompt = lambda topic=v.TOPIC: a_prompt(orig_r(topic=topic))
        if variant == "D":
            v.build_verification_prompt = lambda topic, ledger_parsed: vc_prompt(orig_v(topic, ledger_parsed))
        yield v
    finally:
        v.build_researcher_prompt, v.build_verification_prompt = orig_r, orig_v


# ---------------------------------------------------------------------------
# 記録用client proxy(呼出内容は変えない。usage・検索回数・引用を記録するだけ)
# ---------------------------------------------------------------------------


class RecordingClient:
    def __init__(self, inner):
        self.inner = inner
        self.responses = SimpleNamespace(create=self._create)
        self.records = []

    def _create(self, **kw):
        t0 = time.time()
        resp = self.inner.responses.create(**kw)
        latency = time.time() - t0
        ws = [it for it in (getattr(resp, "output", None) or []) if getattr(it, "type", None) == "web_search_call"]
        usage = lib.usage_dict(resp)
        cites, seen = [], set()
        for it in (getattr(resp, "output", None) or []):
            if getattr(it, "type", None) != "message":
                continue
            for c in getattr(it, "content", None) or []:
                for ann in getattr(c, "annotations", None) or []:
                    if getattr(ann, "type", None) == "url_citation" and getattr(ann, "url", None) not in seen:
                        seen.add(ann.url)
                        cites.append({"title": getattr(ann, "title", None), "url": ann.url})
        self.records.append({
            "model_returned": getattr(resp, "model", None), "response_id": getattr(resp, "id", None),
            "latency_seconds": round(latency, 2), "usage": usage, "web_search_call_count": len(ws),
            "cost_jpy": round(lib.cost_jpy(kw["model"], usage["input_tokens"], usage["output_tokens"], len(ws)), 4),
            "url_citations": cites, "tools": [t.get("type") for t in (kw.get("tools") or [])],
            "schema_name": kw["text"]["format"].get("name"),
        })
        return resp


class StubSearchClient:
    """dry-run用(API 0、合成応答)。web_search_callを3回含む合成outputを返す。"""

    def __init__(self):
        self.responses = SimpleNamespace(create=self._create)
        self.calls = 0

    def _create(self, **kw):
        self.calls += 1
        name = kw["text"]["format"]["name"]
        user = kw["input"][1]["content"]
        if name.startswith("verified_fact_ledger_draft"):
            out = {"facts": [{"fact_id": "F01", "claim": "(stub) Ansar Allah attack on Riyadh airport", "subject": "stub", "date_or_period": None,
                              "scope": None, "conditions": None, "numeric_value": None, "numeric_scope": None,
                              "causal_strength": "OBSERVED_REPORTED", "source_title": "stub", "source_url": "https://example.invalid/stub",
                              "source_type": "OTHER", "support_level": "DIRECTLY_STATED", "ambiguity": None, "notes_for_writer": None}]}
        else:
            ids = re.findall(r'"fact_id": "([^"]+)"', user)
            out = {"verifications": [{"fact_id": i, "verdict": "VERIFIED", "verification_notes": "(stub)"} for i in dict.fromkeys(ids)]}
        text = json.dumps(out, ensure_ascii=False)
        wsc = [SimpleNamespace(type="web_search_call", action=SimpleNamespace(queries=[f"stub query {i}"], query=None)) for i in range(3)]
        msg = SimpleNamespace(type="message", content=[SimpleNamespace(annotations=[
            SimpleNamespace(type="url_citation", url="https://example.invalid/stub", title="stub")])])
        usage = SimpleNamespace(input_tokens=1000, output_tokens=500, input_tokens_details=SimpleNamespace(cached_tokens=0),
                                output_tokens_details=SimpleNamespace(reasoning_tokens=0))
        return SimpleNamespace(output_text=text, model=kw["model"], id=f"stubS-{self.calls}", usage=usage, output=wsc + [msg])


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------


def run_one(client_raw, efam, variant: str, topic_text: str, topic: str, sample: int, out: str, guard, dry_run: bool) -> dict:
    cell = os.path.join(out, variant, topic, f"s{sample}")
    lib.assert_under_out_root(cell)
    sp = os.path.join(cell, "summary.json")
    if os.path.exists(sp):                       # 完了済みcellは再実行しない(費用重複防止)
        return lib.read_json(sp)
    v = lib._vfl01()
    rc = RecordingClient(client_raw)
    with patched_prompts(variant):
        if variant == "E0":                      # Prompt不変の保証: Production関数の出力そのもの
            assert v.build_researcher_prompt(topic=topic_text) == v.RESEARCHER_PROMPT_TEMPLATE.format(topic=topic_text)
        if guard is not None:
            guard.check(EST_RUN_JPY[variant])
        t0 = time.time()
        research = efam.run_researcher_for_topic(rc, topic_text)
        lib.write_json(os.path.join(cell, "research_record.json"), {k: val for k, val in research.items() if k != "parsed"} | {"variant": variant})
        lib.write_json(os.path.join(cell, "draft.json"), research["parsed"])
        stage_rec = [dict(rc.records[-1], stage="research")]
        ws_r = rc.records[-1]["web_search_call_count"]
        if ws_r > STOP_WS:
            lib.write_json(sp.replace("summary.json", "ANOMALY_STOP.json"), {"web_search_call_count": ws_r, "limit": STOP_WS})
            raise SystemExit(f"[ANOMALY_STOP] web_search_call_count={ws_r} > {STOP_WS} ({variant}/{topic}/s{sample})")
        verification = None
        if variant == "D":
            if guard is not None:
                guard.check(EST_RUN_JPY["D"] - EST_RUN_JPY["A"])
            verification = efam.run_verification_for_topic(rc, topic_text, research["parsed"])
            stage_rec.append(dict(rc.records[-1], stage="verification"))
            lib.write_json(os.path.join(cell, "verification_record.json"), {k: val for k, val in verification.items() if k != "parsed"})
            lib.write_json(os.path.join(cell, "verification.json"), verification["parsed"])
            if rc.records[-1]["web_search_call_count"] > STOP_WS:
                raise SystemExit(f"[ANOMALY_STOP] verification web_search_call_count={rc.records[-1]['web_search_call_count']}")
        wall = time.time() - t0
    # 描画: Dは検証後のLedger(Production関数build_verified_ledger_text)。E0/Aは検証を走らせないため
    # draft全Factを仮に全VERIFIEDとみなした『draft view』(採点・比較用。Production Ledgerではない)
    draft = research["parsed"]
    ver_parsed = verification["parsed"] if verification else {"verifications": [
        {"fact_id": f["fact_id"], "verdict": "VERIFIED", "verification_notes": "(draft view)"} for f in draft["facts"]]}
    ledger_text, counts, kept = v.build_verified_ledger_text(draft, ver_parsed)
    lib.write_text(os.path.join(cell, "verified_fact_ledger.txt"), ledger_text)
    summary = {
        "variant": variant, "topic": topic, "sample": sample, "dry_run": dry_run, "n_facts_draft": len(draft["facts"]),
        "ledger_is_post_verification": verification is not None, "verdict_counts": counts, "n_kept": len(kept),
        "schema_errors": lib.validate_ledger_draft(draft),
        "stages": stage_rec,
        "research_web_search_calls": stage_rec[0]["web_search_call_count"],
        "verification_web_search_calls": stage_rec[1]["web_search_call_count"] if len(stage_rec) > 1 else None,
        "research_cost_jpy": stage_rec[0]["cost_jpy"], "total_cost_jpy": round(sum(s["cost_jpy"] for s in stage_rec), 4),
        "research_latency_s": stage_rec[0]["latency_seconds"], "total_latency_s": round(sum(s["latency_seconds"] for s in stage_rec), 2),
        "research_input_tokens": stage_rec[0]["usage"]["input_tokens"], "research_output_tokens": stage_rec[0]["usage"]["output_tokens"],
        "research_search_queries": research["search_usage"].get("queries", []),
        "cited_urls_draft": sorted({f.get("source_url") for f in draft["facts"] if f.get("source_url")}),
        "cited_urls_annotations": [c["url"] for c in stage_rec[0]["url_citations"]],
        "model_returned": research["model"], "wall_s": round(wall, 1),
    }
    lib.write_json(sp, summary)
    lib.append_jsonl(os.path.join(out, "calls_dryrun.jsonl" if dry_run else "calls_real.jsonl"),
                     {"variant": variant, "topic": topic, "sample": sample, "cost_jpy": summary["total_cost_jpy"],
                      "ws": [s["web_search_call_count"] for s in stage_rec]})
    return summary


def cmd_run(a) -> int:
    out = os.path.abspath(a.out)
    lib.assert_under_out_root(out)
    spec = lib.load_sources_spec()
    topic_text = spec["topics"][a.topic]["topic_text"]
    if a.dry_run:
        out = os.path.join(out, "_dryrun")
        lib.assert_under_out_root(out)
        raw_client, guard = StubSearchClient(), None
    else:
        import er005_cost_logger as cl
        from dotenv import load_dotenv
        load_dotenv()
        cl.install(os.path.join(out, "raw_usage_log.jsonl"))
        raw_client = lib._vfl01().get_client()
        guard = lib.BudgetGuard(os.path.join(out, "calls_real.jsonl"), a.budget_jpy)
    import er012_e_family_entertainment_two_level_runner_01 as efam
    res = []
    for variant in a.variants:
        if variant not in SEARCH_ARM_VARIANTS:
            raise SystemExit(f"unknown search-arm variant {variant}")
        for s in range(1, a.samples + 1):
            if a.dry_run:
                summ = run_one(raw_client, efam, variant, topic_text, a.topic, s, out, None, True)
            else:
                import er005_cost_logger as cl
                with cl.logging_context("XRFR_TRIAL_01_SEARCH", f"{variant}_{a.topic}_s{s}"):
                    summ = run_one(raw_client, efam, variant, topic_text, a.topic, s, out, guard, False)
            res.append(summ)
            print(f"[XRFR-SEARCH][{'DRY' if a.dry_run else 'REAL'}] {variant}/{a.topic}/s{s}: facts={summ['n_facts_draft']} "
                  f"ws_research={summ['research_web_search_calls']} ws_verif={summ['verification_web_search_calls']} "
                  f"jpy={summ['total_cost_jpy']} lat={summ['total_latency_s']}s cited={len(summ['cited_urls_draft'])}", flush=True)
    print(f"[XRFR-SEARCH] done runs={len(res)}")
    return 0


# ---------------------------------------------------------------------------
# 引用出典の無料HTTP取得
# ---------------------------------------------------------------------------

_TAG = re.compile(r"<(script|style|noscript|svg|head)[\s\S]*?</\1>", re.I)


def html_to_text(raw: str) -> str:
    t = _TAG.sub(" ", raw)
    t = re.sub(r"<(br|/p|/div|/li|/h\d|/tr)[^>]*>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmllib.unescape(t)
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in t.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def url_key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def collect_cited_urls(out: str) -> dict:
    """{url: [cell,...]} 各runの引用URL(draft fact source_url ∪ url_citation annotation)"""
    urls = {}
    for sp in sorted(glob.glob(os.path.join(out, "*", "*", "s*", "summary.json"))):
        summ = lib.read_json(sp)
        cell = f"{summ['variant']}|{summ['topic']}|s{summ['sample']}"
        for u in list(summ["cited_urls_draft"]) + list(summ["cited_urls_annotations"]):
            urls.setdefault(u, [])
            if cell not in urls[u]:
                urls[u].append(cell)
    return urls


BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def nextdata_text(raw: str) -> str:
    """JS描画ページ(SPA等)用: og:description + __NEXT_DATA__ JSON内の長い文字列を本文代わりに連結(無料HTTP取得済みHTMLからの抽出のみ)。"""
    parts = []
    m = re.search(r'og:description" content="([^"]{20,})"', raw)
    if m:
        parts.append(htmllib.unescape(m.group(1)))
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>', raw)
    if m:
        try:
            obj = json.loads(m.group(1))
            # サイト全体のデータ(他記事・ナビ)を避け、記事本体(pageProps.newsDetails)のみを使う。無ければ使わない
            nd = ((obj.get("props") or {}).get("pageProps") or {}).get("newsDetails")
            stack = [nd] if nd else []
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    stack.extend(x.values())
                elif isinstance(x, list):
                    stack.extend(x)
                elif isinstance(x, str) and len(x) > 60 and not x.startswith(("http", "/_next")):
                    parts.append(html_to_text(x) if "<" in x else x)
        except ValueError:
            pass
    return "\n".join(parts)


def ap_body(raw: str) -> str:
    """AP記事: RichTextStoryBody以降を本文とみなす(関連記事・ナビを避ける。見つからなければ空)。"""
    i = raw.find("RichTextStoryBody")
    if i < 0:
        return ""
    j = raw.find("Page-actions-bottom", i)
    seg = raw[i:j] if j > 0 else raw[i:i + 40000]
    return html_to_text(seg)


def fetch_one(u: str, sdir: str) -> dict:
    k = url_key(u)
    rawp = os.path.join(sdir, k + ".raw")
    r = subprocess.run(["curl.exe", "-L", "-s", "-m", "30", "-A", BROWSER_UA, "-H", "Accept-Language: en-US,en;q=0.9",
                        "-w", "%{http_code}", "-o", rawp, u], capture_output=True, text=True)
    code = r.stdout.strip()
    text, method = "", "none"
    if os.path.exists(rawp):
        with open(rawp, "rb") as f:
            raw = f.read().decode("utf-8", errors="replace")
        if "RichTextStoryBody" in raw and "apnews.com" in u:
            text, method = ap_body(raw), "ap_body"
        if len(text) < 500 and ("<" in raw[:5000] or "<html" in raw.lower()):
            text, method = html_to_text(raw), "html_to_text"
        if len(text) < 500 and "__NEXT_DATA__" in raw:
            text, method = nextdata_text(raw), "nextdata"
        if "<" not in raw[:5000] and "<html" not in raw.lower():
            text, method = raw, "plain"
    lib.write_text(os.path.join(sdir, k + ".txt"), text)
    return {"key": k, "http": code, "chars": len(text), "method": method, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "available": code.startswith("2") and len(text) >= 500, "sha256": lib.sha256_text(text)}


def cmd_fetch(a) -> int:
    out = os.path.abspath(a.out)
    lib.assert_under_out_root(out)
    sdir = os.path.join(out, "_sources")
    os.makedirs(sdir, exist_ok=True)
    urls = collect_cited_urls(out)
    manifest_p = os.path.join(sdir, "fetch_manifest.json")
    manifest = lib.read_json(manifest_p) if os.path.exists(manifest_p) else {}
    for u in urls:
        if u in manifest and (manifest[u]["available"] or not a.refetch_unavailable):
            manifest[u]["cells"] = urls[u]
            continue
        m = fetch_one(u, sdir)
        m["cells"] = urls[u]
        manifest[u] = m
        print(f"[fetch] {m['http']} chars={m['chars']} {m['method']} avail={m['available']} {u[:110]}", flush=True)
    lib.write_json(manifest_p, manifest)
    return 0


# ---------------------------------------------------------------------------
# 採点(API 0。決定論)
# ---------------------------------------------------------------------------
ACTOR = r"(Ansar\s*Allah|アンサール|アンサル|フーシ|Houthi|ホーシ)"
# 検索込み腕の汎用項目(事前登録 v02 §9-2): source側の明示判定(windows) と Ledger側の保持判定(単一Factブロック)
SA_SRC = [ACTOR, r"(Saudi|サウジ|Riyadh|リヤド|airport|空港|Abha|Jeddah|Dhahran)", r"(attack|strike|drone|missile|攻撃|空爆|ミサイル)"]
SA_LED = [ACTOR, r"(サウジ|Saudi|リヤド|Riyadh|空港|airport|アブハ|ジッダ|ジェッダ|Abha|Jeddah|ダ[ーハフ]*ラン|Dhahran)",
          r"(攻撃|空爆|ミサイル|ドローン|無人機|attack|strike|missile|drone)"]
SC_SRC = [r"(Red Sea|Bab al-Mandab|Bab el-Mandeb|Mandab|maritime|shipping|sea lane|trade route)", r"(Houthi|Ansar\s*Allah|Yemen)"]
SC_LED = [r"(紅海|Red Sea|バブ|マンデブ|Mandab|海上|航路|海運|船舶|商船|maritime|shipping|sea lane)", r"(フーシ|アンサール|アンサル|Houthi|Ansar|イエメン|Yemen)"]
GENERIC_ITEMS = [
    {"id": "SA", "label": "空港攻撃等の主体(Ansar Allah/Houthi)", "src": SA_SRC, "led": SA_LED},
    {"id": "SC", "label": "紅海・海上交易路とイエメン戦況の文脈", "src": SC_SRC, "led": SC_LED},
]


def windows(text: str, size: int = 700, step: int = 350) -> list:
    t = lib.norm_ws(text)
    if len(t) <= size:
        return [t]
    return [t[i:i + size] for i in range(0, len(t) - size + step, step)]


def window_match(groups: list, text: str) -> bool:
    return any(all(re.search(g, w, re.I) for g in groups) for w in windows(text))


def score_cell(summ: dict, ledger_text: str, draft: dict, src_texts: dict, gold_items: list) -> dict:
    """src_texts: {url: text}(取得できたもの)。item(generic+gold KEY)ごとに expected(引用出典が明示) と retained(Ledger/draft)を返す。"""
    blocks = [b["text"] for b in lib.split_blocks(ledger_text)]
    dtexts = [lib.fact_text(f) for f in draft["facts"]]
    cited = list(dict.fromkeys(list(summ["cited_urls_draft"]) + list(summ["cited_urls_annotations"])))
    avail = {u: src_texts[u] for u in cited if u in src_texts}
    res = {"n_cited": len(cited), "n_cited_available": len(avail), "items": {}}
    for it in GENERIC_ITEMS:
        exp_srcs = [u for u, t in avail.items() if window_match(it["src"], t)]
        led = any(all(re.search(g, b, re.I) for g in it["led"]) for b in blocks)
        drf = any(all(re.search(g, b, re.I) for g in it["led"]) for b in dtexts)
        res["items"][it["id"]] = {"kind": "generic", "expected": bool(exp_srcs), "expected_in": exp_srcs, "retained_ledger": led, "retained_draft": drf}
    for gi in gold_items:
        if gi["tier"] != "KEY":
            continue
        exp_srcs = [u for u, t in avail.items() if window_match(gi["groups"], t)]
        led = any(lib.item_matches(gi, b) for b in blocks)
        drf = any(lib.item_matches(gi, b) for b in dtexts)
        res["items"][gi["id"]] = {"kind": "gold", "expected": bool(exp_srcs), "expected_in": exp_srcs, "retained_ledger": led, "retained_draft": drf}
    return res


def cmd_score(a) -> int:
    out = os.path.abspath(a.out)
    gold = lib.read_json(os.path.join(lib.DOC_DIR, "gold_02.json"))["topics"]["mey"]
    mp = os.path.join(out, "_sources", "fetch_manifest.json")
    manifest = lib.read_json(mp)
    src_texts = {u: lib.read_text(os.path.join(out, "_sources", m["key"] + ".txt")) for u, m in manifest.items() if m["available"]}
    adj_p = os.path.join(lib.DOC_DIR, "adjudication_02.json")
    adjud = lib.read_json(adj_p) if os.path.exists(adj_p) else {}
    cells = []
    for sp in sorted(glob.glob(os.path.join(out, "*", "*", "s*", "summary.json"))):
        summ = lib.read_json(sp)
        cd = os.path.dirname(sp)
        led = lib.read_text(os.path.join(cd, "verified_fact_ledger.txt"))
        draft = lib.read_json(os.path.join(cd, "draft.json"))
        sc = score_cell(summ, led, draft, src_texts, gold["items"])
        blocks = lib.split_blocks(led)
        flags = lib.fabrication_flags(blocks, gold["watch"])
        for fl in flags:
            key = f"S|{summ['variant']}|{summ['topic']}|s{summ['sample']}|{fl['fact_id']}"
            fl["adjudication"] = adjud[key]["verdict"] if key in adjud else "UNADJUDICATED"
        cells.append({"variant": summ["variant"], "sample": summ["sample"], "summary": summ, "score": sc, "flags": flags})
    agg = aggregate_search(cells)
    lib.write_json(os.path.join(out, "search_arm_eval.json"), {"cells": cells, "aggregate": agg})
    md = search_md(cells, agg, manifest)
    if a.report:
        lib.write_text(a.report, md)
    print(md)
    return 0


def aggregate_search(cells: list) -> dict:
    out = {}
    for var in SEARCH_ARM_VARIANTS:
        cs = [c for c in cells if c["variant"] == var]
        if not cs:
            continue
        exp = ret = exp_d = ret_d = 0
        exp_g = ret_g = 0
        for c in cs:
            for iid, r in c["score"]["items"].items():
                if r["expected"]:
                    exp += 1
                    ret += 1 if r["retained_ledger"] else 0
                    if r["kind"] == "gold":
                        exp_g += 1
                        ret_g += 1 if r["retained_ledger"] else 0
        ws = [c["summary"]["research_web_search_calls"] for c in cs]
        out[var] = {
            "n_runs": len(cs), "expected_obs": exp, "retained_obs": ret, "retention": round(ret / exp, 3) if exp else None,
            "gold_expected_obs": exp_g, "gold_retained_obs": ret_g,
            "research_ws_calls": ws, "mean_research_ws": round(sum(ws) / len(ws), 2),
            "verification_ws_calls": [c["summary"]["verification_web_search_calls"] for c in cs],
            "mean_research_cost_jpy": round(sum(c["summary"]["research_cost_jpy"] for c in cs) / len(cs), 3),
            "mean_total_cost_jpy": round(sum(c["summary"]["total_cost_jpy"] for c in cs) / len(cs), 3),
            "mean_research_latency_s": round(sum(c["summary"]["research_latency_s"] for c in cs) / len(cs), 1),
            "mean_input_tokens": round(sum(c["summary"]["research_input_tokens"] for c in cs) / len(cs)),
            "mean_output_tokens": round(sum(c["summary"]["research_output_tokens"] for c in cs) / len(cs)),
            "mean_facts": round(sum(c["summary"]["n_facts_draft"] for c in cs) / len(cs), 2),
            "flags_unadjudicated": sum(1 for c in cs for f in c["flags"] if f["adjudication"] == "UNADJUDICATED"),
            "fabrication_unsupported": sum(1 for c in cs for f in c["flags"] if f["adjudication"] == "UNSUPPORTED"),
        }
    return out


def search_md(cells: list, agg: dict, manifest: dict) -> str:
    L = ["# XRFR 検索込み腕 採点(機械)", "", "## 方式別集計(retention=出典が明示している項目のうちLedger(Dは検証後/E0・Aはdraft view)に保持された割合)", "",
         "| 方式 | runs | expected観測 | 保持 | retention | gold(KEY)expected/保持 | 検索回数(Researcher) | 平均検索 | 検証検索 | Researcher費用JPY | 総費用JPY | 時間s | in tok | out tok | Fact数 | 未判定フラグ | UNSUPPORTED |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v, a in agg.items():
        L.append(f"| {v} | {a['n_runs']} | {a['expected_obs']} | {a['retained_obs']} | {a['retention']} | {a['gold_expected_obs']}/{a['gold_retained_obs']} | "
                 f"{a['research_ws_calls']} | {a['mean_research_ws']} | {a['verification_ws_calls']} | {a['mean_research_cost_jpy']} | {a['mean_total_cost_jpy']} | "
                 f"{a['mean_research_latency_s']} | {a['mean_input_tokens']} | {a['mean_output_tokens']} | {a['mean_facts']} | {a['flags_unadjudicated']} | {a['fabrication_unsupported']} |")
    L += ["", "## run別 項目(expected=引用出典が明示 / retained=Ledger)", ""]
    for c in sorted(cells, key=lambda x: (x["variant"], x["sample"])):
        rows = []
        for iid, r in c["score"]["items"].items():
            if r["expected"]:
                rows.append(f"{iid}:{'OK' if r['retained_ledger'] else 'MISS' + ('(draftにはあり)' if r['retained_draft'] else '(draftに無し)')}")
        s = c["summary"]
        L.append(f"- {c['variant']}/s{c['sample']} (facts={s['n_facts_draft']}, 検索{s['research_web_search_calls']}, 引用{c['score']['n_cited']}件/取得可{c['score']['n_cited_available']}件): " + (" ".join(rows) or "(expected項目なし)"))
    L += ["", "## 引用出典の取得状況", ""]
    for u, m in manifest.items():
        L.append(f"- [{m['http']}] chars={m['chars']} avail={m['available']} {u} <- {', '.join(m['cells'])}")
    L += ["", "## 創作候補フラグ", ""]
    n = 0
    for c in cells:
        for f in c["flags"]:
            n += 1
            L.append(f"- S|{c['variant']}|mey|s{c['sample']}|{f['fact_id']}: {','.join(f['reasons'])} -> {f['adjudication']}")
    if not n:
        L.append("(フラグ0件)")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="*", default=list(SEARCH_ARM_VARIANTS))
    ap.add_argument("--topic", default="mey")
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(lib.OUT_ROOT, "search_arm"))
    ap.add_argument("--budget-jpy", type=float, default=60.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fetch-sources", action="store_true")
    ap.add_argument("--refetch-unavailable", action="store_true", help="取得不能(本文500字未満)の出典を、ブラウザUA・本文抽出規則(AP本文/SPA __NEXT_DATA__)で再取得")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--report", default=None)
    a = ap.parse_args(argv)
    a.variants = [x for v in a.variants for x in v.split(",") if x]
    if a.fetch_sources:
        return cmd_fetch(a)
    if a.score:
        return cmd_score(a)
    return cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
