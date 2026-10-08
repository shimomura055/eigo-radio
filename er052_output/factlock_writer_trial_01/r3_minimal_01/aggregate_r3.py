# -*- coding: utf-8 -*-
"""R3-MINIMAL-01 集計 -> SUMMARY_R3.md / METRICS_R3.json (APIなし)。"""
import json, os, re, sys, collections, statistics
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_r3_minimal as m
import er003_audio_tts_asr_safety as safety
BASE = m.BASE
ARMS = ["fresh", "chain"]
FLAGS = ["changed_fact", "changed_scope", "changed_causality", "changed_certainty", "changed_number", "changed_actor",
         "changed_negation", "changed_comparison", "changed_time", "unsupported_new_claim"]
METAPHORS = "舞台 幕 探偵 衣装 主役 配役 ドラマ 映画 ショー 劇 手がかり 犯人 謎 ゲーム カード 小道具 せりふ 代役 お色直し 着替え 衣替え 箱 札 登場 退場 筋書き".split()


def rd(p):
    return open(p, encoding="utf-8").read()


def rj(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def metrics(text, ledger):
    t = text.strip()
    body = re.sub(r"\s+", "", t)
    sents = [s for s in re.split(r"[。！？!?\n]", t) if s.strip()]
    pol = sum(1 for s in sents if re.search(r"(です|ます|ました|でした|ません|でしょう|ください|ましょう)[」』]?$", s.strip()))
    n = len(body) or 1

    def g(pat):
        return len(re.findall(pat, t))

    def norm(s):
        return re.sub(r"[\s、。，．,.「」『』！？!?・\-—#*]", "", s)

    a, l = norm(t), norm(ledger)
    grams = [a[i:i + 6] for i in range(max(0, len(a) - 5))]
    hit = sum(1 for x in grams if x in l)
    return {"chars": n, "polite_rate": round(pol / max(1, len(sents)), 3), "digits_per_1000": round(g(r"[0-9]+") * 1000 / n, 2),
            "hypo": g(r"かもしれません|でしょう|もし|たら"), "questions": g(r"[？?]"),
            "metaphor_kinds": sum(1 for w in METAPHORS if w in t), "dewa_arimasen": g(r"ではありません|ではない"),
            "ngram6": round(hit / max(1, len(grams)), 3)}


def fc_summary(p):
    d = rj(p)
    if not d:
        return None
    devs = d["parsed"].get("deviations", [])
    return {"status": d["parsed"].get("overall_status"), "major": sum(1 for x in devs if x.get("severity") == "MAJOR"),
            "minor": sum(1 for x in devs if x.get("severity") == "MINOR"),
            "flags": {f: sum(1 for x in devs if x.get(f)) for f in FLAGS}, "devs": devs}


items = m.select_sources()
M = {"items": {}}
for it in items:
    r = {"slug": it["slug"], "b": it["b"], "rep": it["rep"]}
    led = rd(it["ledger_path"])
    r["orig_r2_metrics"] = metrics(rd(it["r2_path"]), led)
    r["orig_r2_fc"] = fc_summary(f"{it['out']}/fc_orig_r2.json")
    for a in ARMS:
        p = f"{it['out']}/r3_{a}.md"
        if not os.path.exists(p):
            continue
        t = rd(p)
        r[a] = {"metrics": metrics(t, led), "fc": fc_summary(f"{it['out']}/fc_{a}.json"),
                "symbols": [str(x) for x in safety.detect_prohibited_symbols(t, language="ja")],
                "meta": rj(f"{it['out']}/r3_{a}_meta.json")}
        sc = []
        for o in (0, 1):
            pw = rj(f"{it['out']}/pairwise_{a}_o{o}.json")
            sc.append(pw["winner"] if pw else None)
        r[a]["pw"] = sc
        if None not in sc:
            w = sum(1 for x in sc if x == "r3")
            lo = sum(1 for x in sc if x == "r2")
            r[a]["score"] = 1.0 if w == 2 else (0.0 if lo == 2 else 0.5)
            r[a]["split"] = not (w == 2 or lo == 2)
    M["items"][f"{it['slug']}/b{it['b']}"] = r
json.dump(M, open(f"{BASE}/METRICS_R3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

log = [json.loads(x) for x in open(f"{BASE}/usage_log.jsonl", encoding="utf-8") if x.strip()]
cost = collections.defaultdict(float)
for x in log:
    cost[x["stage"]] += x["cost_jpy"]
total = sum(cost.values())

L = []
L.append("# SUMMARY_R3: R3-MINIMAL-01 (FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_06)\n")
L.append("Status=MEASURED。Trial。しきい値・推奨なし。N=12(3テーマ x 4brief)、judge=gpt-6-luna(LLM判定のみ、人手確認なし)。\n")
L.append(f"R3指示(逐語): 「{m.R3_SENTENCE}」+現行の記号禁止ブロック。比較相手=元R2(6x現行 all6)。実費合計 ¥{total:.2f}(段階別: "
         + ", ".join(f"{k} ¥{v:.2f}" for k, v in sorted(cost.items())) + ")。\n")


def arm_rows(a):
    return [(k, v) for k, v in M["items"].items() if a in v]


def tot(a):
    return [v[a].get("score") for _, v in arm_rows(a) if v[a].get("score") is not None]


def row(name, f):
    L.append(f"| {name} | " + " | ".join(f(a) for a in ARMS) + " |")


def fcs(a, key):
    return sum((v[a]["fc"] or {}).get(key, 0) for _, v in arm_rows(a) if v[a].get("fc"))


L.append("## 1. 結果表\n")
L.append("| 指標 | R3-fresh | R3-chain |\n|---|---|---|")
row("pairwise: R3の得点(/12)", lambda a: f"{sum(tot(a)):.1f} / {len(tot(a))}")
row("割れ率(2順序で勝敗が割れた本)", lambda a: f"{sum(1 for _, v in arm_rows(a) if v[a].get('split'))}/{len(tot(a))}")
row("2順序とも勝ち/割れ/2順序とも負け", lambda a: f"{sum(1 for s in tot(a) if s == 1.0)}/{sum(1 for s in tot(a) if s == 0.5)}/{sum(1 for s in tot(a) if s == 0.0)}")
row("JA FC MAJOR件数(LEDGER_DEVIATION本数)", lambda a: f"{fcs(a, 'major')}件({sum(1 for _, v in arm_rows(a) if v[a].get('fc') and v[a]['fc']['status'] == 'LEDGER_DEVIATION')}本)")
row("JA FC MINOR件数", lambda a: f"{fcs(a, 'minor')}件")
orig_major = sum((v["orig_r2_fc"] or {}).get("major", 0) for v in M["items"].values())
orig_minor = sum((v["orig_r2_fc"] or {}).get("minor", 0) for v in M["items"].values())
orig_dev = sum(1 for v in M["items"].values() if v["orig_r2_fc"] and v["orig_r2_fc"]["status"] == "LEDGER_DEVIATION")
L.append(f"| (参考)元R2 JA FC 同条件再判定 | MAJOR {orig_major}件({orig_dev}本) / MINOR {orig_minor}件 | 同左 |")
row("記号Gate発火(本数/件数)", lambda a: f"{sum(1 for _, v in arm_rows(a) if v[a]['symbols'])}本/{sum(len(v[a]['symbols']) for _, v in arm_rows(a))}件")
row("費用/本(R3生成のみ)", lambda a: f"¥{cost.get('r3_' + a, 0) / max(1, len(arm_rows(a))):.2f}")
row("生成所要秒(平均)", lambda a: f"{statistics.mean([v[a]['meta']['sec'] for _, v in arm_rows(a) if v[a].get('meta')] or [0]):.0f}s")
row("R3生成method", lambda a: ", ".join(f"{k}x{n}" for k, n in collections.Counter((v[a].get('meta') or {}).get('method') for _, v in arm_rows(a)).items()))


def avg(a, k):
    xs = [v[a]["metrics"][k] for _, v in arm_rows(a)]
    return statistics.mean(xs) if xs else float("nan")


L.append("\n文体指標(12本平均。元R2 / R3 / 差):\n")
L.append("| 指標 | 元R2 | R3-fresh | 差 | R3-chain | 差 |\n|---|---|---|---|---|---|")
for k, nm in [("chars", "字数"), ("polite_rate", "です・ます率(文末)"), ("digits_per_1000", "アラビア数字(連続1塊)/1000字"), ("hypo", "仮定語/本"),
              ("questions", "問い(？)/本"), ("metaphor_kinds", "比喩種数(語彙表)/本"), ("dewa_arimasen", "「ではありません」型/本"), ("ngram6", "台帳との6-gram一致率")]:
    o = statistics.mean([v["orig_r2_metrics"][k] for v in M["items"].values()])
    cells = []
    for a in ARMS:
        x = avg(a, k)
        cells += [f"{x:.2f}", f"{x - o:+.2f}"]
    L.append(f"| {nm} | {o:.2f} | " + " | ".join(cells) + " |")
L.append("\n## 2. テーマ別・brief別 (pw列=2順序の勝者r3/r2/tie。score: 1=2順序ともR3勝/0.5=割れ/0=2順序ともR3負。FC列=MAJOR/MINOR件数)\n")
L.append("| theme/brief | rep | fresh pw | fresh score | fresh FC | chain pw | chain score | chain FC | 元R2 FC |\n|---|---|---|---|---|---|---|---|---|")


def fcell(f):
    return "-" if not f else f"{f['major']}/{f['minor']}"


for k, v in M["items"].items():
    cs = []
    for a in ARMS:
        x = v.get(a)
        cs += [("-" if not x else "/".join(str(s) for s in x["pw"])), ("-" if not x or x.get("score") is None else str(x["score"])), "-" if not x else fcell(x["fc"])]
    L.append(f"| {k} | r{v['rep']} | " + " | ".join(cs) + f" | {fcell(v['orig_r2_fc'])} |")
L.append("\nテーマ別合計(R3得点 / 本数):\n")
for a in ARMS:
    for s in m.SLUGS:
        sc = [v[a].get("score") for k, v in arm_rows(a) if k.startswith(s + "/") and v[a].get("score") is not None]
        L.append(f"- {a} {s}: {sum(sc):.1f} / {len(sc)}")
L.append("\nbrief別合計(b1..b4):\n")
for a in ARMS:
    for b in (1, 2, 3, 4):
        sc = [v[a].get("score") for k, v in arm_rows(a) if k.endswith(f"/b{b}") and v[a].get("score") is not None]
        L.append(f"- {a} b{b}: {sum(sc):.1f} / {len(sc)}")
L.append("\n## 3. meta b2 全文(ユーザーのChatGPT版との読み比べ用)\n")
it = [i for i in items if i["slug"] == "meta" and i["b"] == 2][0]
L.append("### 元R2\n\n" + rd(it["r2_path"]).strip() + "\n")
L.append("### R3-fresh\n\n" + rd(f"{it['out']}/r3_fresh.md").strip() + "\n")
if os.path.exists(f"{it['out']}/r3_chain.md"):
    L.append("### (参考)R3-chain\n\n" + rd(f"{it['out']}/r3_chain.md").strip() + "\n")
L.append("## 4. 事実逸脱の中身(MAJOR優先、各アーム最大3件)\n")
for a in ARMS:
    L.append(f"### {a}\n")
    allv = [(k, d) for k, v in arm_rows(a) if v[a].get("fc") for d in v[a]["fc"]["devs"]]
    allv.sort(key=lambda kd: kd[1].get("severity") != "MAJOR")
    for k, d in allv[:3]:
        L.append(f"- {k} [{d.get('severity')}] 「{d.get('claim_in_article')}」: {d.get('issue')} (flags: {[f for f in FLAGS if d.get(f)]})")
    if not allv:
        L.append("- 逸脱なし")
    L.append("\nflag内訳(全件): " + ", ".join(f"{f}={sum((v[a]['fc'] or {}).get('flags', {}).get(f, 0) for _, v in arm_rows(a) if v[a].get('fc'))}" for f in FLAGS) + "\n")
L.append("元R2のflag内訳(全件): " + ", ".join(f"{f}={sum((v['orig_r2_fc'] or {}).get('flags', {}).get(f, 0) for v in M['items'].values())}" for f in FLAGS) + "\n")
open(f"{BASE}/SUMMARY_R3.md", "w", encoding="utf-8").write("\n".join(L))
print("total", round(total, 2))
print("\n".join(L[:30]))
