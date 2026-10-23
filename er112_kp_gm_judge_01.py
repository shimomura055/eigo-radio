# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_02: Judge(評価側、DEV専用)。Production不触。
Judge 2系統: claude-sonnet-5-5(Anthropic) / gpt-6.1-sol(OpenAI)。いずれも2026-10-22時点で各社の最新世代(前回Trial-02と同系統)。
行(row)は内容hashで重複排除し、判定はキャッシュ(judge/<judge>/cache.jsonl)。armラベルは評価者に見せない(blind)。
使い方: python er112_kp_gm_judge_01.py build [--arms prod,a1,...] / run --judges sonnet,sol --cap N / report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import er098_kp_six_model_trial_01_common as C   # noqa: E402  (評価呼出の共通部。Production外のTrial専用module)
import er112_kp_gm_eval_01 as ev   # noqa: E402
import er112_kp_gm_trial_01 as tr   # noqa: E402

OUT = ROOT / "er112_output" / "kp_gm_trial_01"
JDIR = OUT / "judge"
JUDGES = {"sonnet": dict(provider="anthropic", model_id="claude-sonnet-5-5"), "sol": dict(provider="openai", model_id="gpt-6.1-sol")}
BATCH = 24

COMMON = ("あなたは英語学習コンテンツの独立評価者です。英語学習者(日本人成人)向けの『Key Phrase』(本文から選んだ表現)とその意味説明を評価します。"
          "各行は独立に評価し、行の並びや番号から推測しないでください。思考過程や前置きは出力せず、結果だけを出力します。"
          "出力形式: 対象行ごとに1行、`<行番号> <判定文字列> <note>`。判定文字列は下記の項目を指定の順に並べた0/1の連結(区切り無し)。"
          "noteは、問題(0または1の悪い側)があるときだけ20字以内で理由を書き、問題が無ければ省略してください。\n\n")
INSTR = {
    "G": COMMON + ("【行の種類G: 日本語の意味(gloss)】key_phrase(英語)、source_sentence(本文の1文)、gloss(日本語の意味)があります。\n"
                   "- sense_ok(1/0): glossが『その本文の文での』この表現の意味を、日本語学習者に正しく伝えているか。\n"
                   "- literal(1/0): 慣用句・比喩・定型表現なのに語ごとの直訳になっていて、本来の意味が伝わらない場合に1。日本語でも同じ比喩が同じ意味で自然に通じる表現"
                   "(例: 光を当てる、一線を引く)は逐語に数えず0。本文で字義どおりに使われている場合も0。\n"
                   "- deictic(1/0): 英語側が一般形(a/someone/one's等)なのに、glossが『その』『あの』『彼』『あなた』など具体的な指示語・人称を逐語的に訳出している場合に1。\n"
                   "- specific(1/0): 記事固有の状況・固有名詞・条件がglossに入り、別の場面では通用しにくい場合に1。\n"
                   "- multi(1/0): 複数の訳語を並べている場合に1。\n"
                   "判定文字列の項目順: sense_ok,literal,deictic,specific,multi(良い例 `10000`)。\n"),
    "E": COMMON + ("【行の種類E: 英語の説明(Advanced向けexplanation)】key_phrase、source_sentence、explanation(英語1文)があります。\n"
                   "- sense_ok(1/0): explanationが『その本文の文での』この表現の意味を正しく表しているか。\n"
                   "- specific(1/0): 記事固有の状況・条件・詳細が説明に入り、別の場面では通用しにくい場合に1。\n"
                   "- narrow(1/0): 一般的な中心義ではなく、狭い下位語義や条件付きの意味だけを説明している場合に1。\n"
                   "- multi(1/0): 複数の意味を並べている場合に1。\n"
                   "判定文字列の項目順: sense_ok,specific,narrow,multi(良い例 `1000`)。\n"),
    "E2": COMMON + ("【行の種類E2: 英語の説明(Advanced向けexplanation)の汎用性】key_phrase、source_sentence、explanation(英語1文)があります。\n"
                    "- sense_ok(1/0): explanationが『その本文の文での』この表現の意味を正しく表しているか。\n"
                    "- core(1/0): 説明が、どの場面でも成り立つ中心的な意味だけを書いている場合に1。本文の話題に由来する条件・目的・対象(何が許容されるか、誰が何のためか、など、表現自体に含まれない限定)を含む場合は0。\n"
                    "- single(1/0): 意味が1つに絞られている場合に1。『AまたはB』のように2つの意味を併記している場合は0。\n"
                    "判定文字列の項目順: sense_ok,core,single(良い例 `111`)。\n"),
    "P": COMMON + ("【行の種類P: Std/Adv整合】同じ表現について、Standard向けの日本語の意味(gloss_ja)とAdvanced向けの英語説明(explanation_en)があります。\n"
                   "- consistent(1/0): 2つが同じ語義(同じ中心義)を指しているか。片方が字義どおり、もう片方が比喩的意味など、語義が食い違う場合は0。\n"
                   "判定文字列の項目順: consistent(良い例 `1`)。\n"),
    "K": COMMON + ("【行の種類K: Key Phrase形】display(本文中の表層形)から学習用に整えたkey(提示形)があります。source_sentenceは参考です。\n"
                   "- ok(1/0): keyは英語として自然で文法的に正しく、displayの意味・用法を保った、別の場面でも再利用できる形か。\n"
                   "- under(1/0): 本文固有の指示語(this/that)や目的格代名詞(him/her/me/us)、活用形など、一般化すべき要素がkeyに残っている場合に1(固定表現で必要なものは0)。\n"
                   "- over(1/0): 不要な変更・意味の変化・非文法(例: someone job)がある場合に1。\n"
                   "判定文字列の項目順: ok,under,over(良い例 `100`)。\n"),
}
FIELDS = {"E2": ("sense_ok", "core", "single"), "G": ("sense_ok", "literal", "deictic", "specific", "multi"), "E": ("sense_ok", "specific", "narrow", "multi"),
          "P": ("consistent",), "K": ("ok", "under", "over")}
_LOCK = threading.Lock()


def rid(kind, *parts):
    return kind + "_" + hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:12]


def build_rows(arms, hard_only=False):
    """judge対象行(重複排除)。戻り値: rows(dict id->row)、ref(id->[(arm,rep,unit,rank)...])。"""
    res = ev.load_results(include_v1=any(x.startswith("v1_") for x in arms))
    rows, ref = {}, defaultdict(list)

    def add(row, key):
        rows.setdefault(row["id"], row)
        ref[row["id"]].append(key)

    for (arm, rep, uid), r in res.items():
        if arm not in arms:
            continue
        u = ev.UBY[uid]
        items = r.get("items") or []
        by_rank = {it["rank"]: it for it in items}
        for it in items:
            key = it["key_phrase"]
            sent = it.get("source_sentence") or ""
            hard = it["display_phrase"].lower() in ev.HARD
            if it.get("gloss") and (hard or (arm.replace("v1_", "") in ("prod", "a12", "a123s") and not hard_only)):
                add(dict(id=rid("G", key, sent, it["gloss"]), kind="G", key_phrase=key, source_sentence=sent, gloss=it["gloss"]), (arm, rep, uid, it["rank"], "G"))
            e = (r.get("expl") or {}).get(str(it["rank"])) or {}
            if e.get("text") and (hard or (arm.replace("v1_", "") in ("prod", "a12", "a123s") and not hard_only)):
                add(dict(id=rid("E", key, sent, e["text"]), kind="E", key_phrase=key, source_sentence=sent, explanation=e["text"]), (arm, rep, uid, it["rank"], "E"))
            if e.get("text") and hard:
                add(dict(id=rid("E2", key, sent, e["text"]), kind="E2", key_phrase=key, source_sentence=sent, explanation=e["text"]), (arm, rep, uid, it["rank"], "E2"))
            if it["display_phrase"].lower() != key.lower() or hard:
                add(dict(id=rid("K", it["display_phrase"], key, sent), kind="K", display=it["display_phrase"], key=key, source_sentence=sent), (arm, rep, uid, it["rank"], "K"))
    # P: 同一arm・rep・runでa2のused_form == b1bのused_form
    byrun = defaultdict(dict)
    for (arm, rep, uid), r in res.items():
        if arm in arms and not ev.UBY[uid]["synthetic"]:
            byrun[(arm, rep, ev.UBY[uid]["run"])][ev.UBY[uid]["level"]] = r
    for (arm, rep, run), lv in byrun.items():
        if "a2" in lv and "b1b" in lv:
            a2 = {it["used_form"].lower(): it for it in (lv["a2"].get("items") or []) if it.get("gloss")}
            for it in lv["b1b"].get("items") or []:
                s = a2.get(it["used_form"].lower())
                e = ((lv["b1b"].get("expl") or {}).get(str(it["rank"])) or {}).get("text")
                if s and e:
                    add(dict(id=rid("P", it["used_form"], s["gloss"], e), kind="P", key_phrase=it["used_form"], source_sentence=it.get("source_sentence") or "",
                             gloss_ja=s["gloss"], explanation_en=e), (arm, rep, run, it["rank"], "P"))
    return rows, ref


def render_batch(kind, rows):
    lines = [INSTR[kind], "\n【対象行】\n"]
    for i, r in enumerate(rows, 1):
        d = {k: v for k, v in r.items() if k not in ("kind", "id")}
        lines.append(f"{i}. " + json.dumps(d, ensure_ascii=False))
    return "\n".join(lines)


_LINE = re.compile(r"^\s*(\d+)[.:)]?\s+([01]+)\s*(.*)$")


def parse_lines(text, kind, batch):
    out = {}
    for ln in text.splitlines():
        m = _LINE.match(ln)
        if not m:
            continue
        n = int(m.group(1))
        bits = m.group(2)
        if not (1 <= n <= len(batch)) or len(bits) != len(FIELDS[kind]):
            continue
        v = {k: int(c) for k, c in zip(FIELDS[kind], bits)}
        v["note"] = m.group(3).strip()
        out[batch[n - 1]["id"]] = v
    return out


def cache_path(judge):
    return JDIR / judge / "cache.jsonl"


def load_cache(judge):
    p = cache_path(judge)
    c = {}
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                r = json.loads(ln)
                c[r["id"]] = r
    return c


def extract_json(text):
    s = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    a, b = s.find("["), s.rfind("]")
    return json.loads(s[a:b + 1])


def run_batch(judge, kind, batch, cap):
    j = JUDGES[judge]
    user = render_batch(kind, batch)
    if tr.stop_present():
        return dict(judge=judge, skipped="STOP")
    if tr.ledger_total_jpy() >= cap:
        return dict(judge=judge, skipped="CAP")
    extra = {"reasoning": {"effort": "low"}} if j["provider"] == "openai" else {"thinking": {"type": "between_tools"}}
    body = C.build_body(j["provider"], j["model_id"], user, extra=extra)
    r = C.call_with_retry(j["provider"], j["model_id"], body)
    if not r["ok"]:
        return dict(judge=judge, error=str(r["attempts"])[:300])
    cost = C.cost_usd(j["model_id"], r["usage"]) * C.USD_JPY
    tr.ledger_add(dict(kind="judge", judge=judge, model=r["model_returned"], batch_kind=kind, n=len(batch), usage=r["usage"], cost_jpy=round(cost, 5),
                       ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
    got = parse_lines(r["text"], kind, batch)
    if not got:
        return dict(judge=judge, error="parse", raw=r["text"][:300])
    with _LOCK:
        (JDIR / judge).mkdir(parents=True, exist_ok=True)
        with open(cache_path(judge), "a", encoding="utf-8") as f:
            for row in batch:
                v = got.get(row["id"])
                if v:
                    f.write(json.dumps(dict(id=row["id"], kind=kind, model=r["model_returned"], verdict=v), ensure_ascii=False) + "\n")
    return dict(judge=judge, ok=len(got), n=len(batch), cost=round(cost, 4))


def cmd_run(a):
    rows, ref = build_rows(set(a.arms.split(",")), hard_only=a.hard_only)
    only = set(a.kinds.split(",")) if a.kinds else None
    todo = defaultdict(list)
    caches = {j: load_cache(j) for j in a.judges.split(",")}
    for rw in rows.values():
        if only and rw["kind"] not in only:
            continue
        for j in caches:
            if rw["id"] not in caches[j]:
                todo[(j, rw["kind"])].append(rw)
    jobs = []
    for (j, kind), rs in todo.items():
        rs.sort(key=lambda x: x["id"])
        for i in range(0, len(rs), BATCH):
            jobs.append((j, kind, rs[i:i + BATCH]))
    print("rows", len(rows), "jobs", len(jobs), {f"{k[0]}:{k[1]}": len(v) for k, v in todo.items()}, flush=True)
    if a.max_jobs:
        jobs = jobs[:a.max_jobs]
    if a.dry_run:
        return 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for f in as_completed([ex.submit(run_batch, j, k, b, a.cap) for j, k, b in jobs]):
            print(f.result(), f"cum={tr.ledger_total_jpy():.3f}", flush=True)
    return 0


def cmd_count(a):
    rows, ref = build_rows(set(a.arms.split(",")))
    print(Counter(r["kind"] for r in rows.values()))
    return 0


GOOD = {"core": 1, "single": 1, "sense_ok": 1, "literal": 0, "deictic": 0, "specific": 0, "multi": 0, "narrow": 0, "consistent": 1, "ok": 1, "under": 0, "over": 0}


def verdict_ok(kind, v):
    """項目ごとに『良い側』か。kind別の総合: G=sense_ok&!literal&!deictic、E=sense_ok&!narrow&!specific、P=consistent、K=ok&!under&!over。"""
    if kind == "G":
        return bool(v["sense_ok"] == 1 and v["literal"] == 0 and v["deictic"] == 0)
    if kind == "E":
        return bool(v["sense_ok"] == 1 and v["narrow"] == 0 and v["specific"] == 0)
    if kind == "E2":
        return bool(v["sense_ok"] == 1 and v["core"] == 1 and v["single"] == 1)
    if kind == "P":
        return bool(v["consistent"] == 1)
    if kind == "K":
        return bool(v["ok"] == 1 and v["under"] == 0 and v["over"] == 0)
    return False


def cmd_report(a):
    rows, ref = build_rows(set(a.arms.split(",")), hard_only=a.hard_only)
    judges = a.judges.split(",")
    caches = {j: load_cache(j) for j in judges}
    agg = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # (kind,arm) -> field -> [good,n]
    overall = defaultdict(lambda: [0, 0])
    for rid_, refs in ref.items():
        row = rows[rid_]
        vs = [caches[j].get(rid_) for j in judges]
        if any(v is None for v in vs):
            continue
        kind = row["kind"]
        for (arm, rep, uid, rank, k) in refs:
            both = all(verdict_ok(kind, v["verdict"]) for v in vs)
            overall[(kind, arm)][0] += 1 if both else 0
            overall[(kind, arm)][1] += 1
            for f in FIELDS[kind]:
                agg[(kind, arm)][f][0] += 1 if all(v["verdict"][f] == GOOD[f] for v in vs) else 0
                agg[(kind, arm)][f][1] += 1
    for (kind, arm), (g, n) in sorted(overall.items()):
        det = " ".join(f"{f}={x[0]}/{x[1]}" for f, x in agg[(kind, arm)].items())
        print(f"{kind} {arm:6s} PASS={g}/{n} ({100*g/max(n,1):.0f}%) | {det}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count")
    c.add_argument("--arms", default="prod,a1,a12,a123s")
    rp = sub.add_parser("report")
    rp.add_argument("--arms", default="prod,a1,a12,a123s")
    rp.add_argument("--judges", default="sonnet")
    rp.add_argument("--hard-only", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--arms", default="prod,a1,a12,a123s")
    r.add_argument("--judges", default="sonnet,sol")
    r.add_argument("--kinds", default="")
    r.add_argument("--cap", type=float, default=80.0)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--max-jobs", type=int, default=0)
    r.add_argument("--hard-only", action="store_true")
    a = ap.parse_args()
    sys.exit(cmd_count(a) if a.cmd == "count" else cmd_report(a) if a.cmd == "report" else cmd_run(a))
