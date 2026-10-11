# -*- coding: utf-8 -*-
"""aux_metrics_01.py  補助指標(人間判断の代替ではない。ユーザー評価前には提示しない)。無課金・決定論。
出力: AUX_METRICS_01.json / AUX_METRICS_01.md(案名つき=Blind対応表と同じ扱いのFable内部資料)"""
import json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maq_driver_01 as D

ARMS = ["A", "C", "D", "E"]
CONSTRAINT_PHRASES = ["事実1", "事実2", "事実3", "について：", "【事実", "Writerへの注意", "事実ではありません", "【中核数値】", "【周辺数値】"]
nfkc = lambda s: unicodedata.normalize("NFKC", s)

def main():
    ledger = nfkc(open(os.path.join(D.A_RUN, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read())
    out = {}
    for a in ARMS:
        rd = os.path.join(D.RUNS, a)
        r2 = open(os.path.join(rd, "export", "r2.md"), encoding="utf-8").read()
        lines = [l for l in r2.split("\n") if l.strip()]
        title, body = lines[0], "\n".join(lines[1:])
        ids = open(os.path.join(rd, "export", "selected_fact_ids"), encoding="utf-8").read().split()
        cons = open(os.path.join(rd, "export", "writer_constraints.txt"), encoding="utf-8").read()
        usage = json.load(open(os.path.join(rd, "usage.json"), encoding="utf-8"))
        nb = nfkc(body + title)
        nums = sorted(set(re.findall(r"\d+(?:[.,]\d+)*", nb)))
        nums_not_in_ledger = [n for n in nums if n not in ledger]
        lat = sorted(set(re.findall(r"[A-Za-z][A-Za-z0-9\.\-]{1,}", nb)))
        lat_not = [t for t in lat if t.lower() not in ledger.lower()]
        kata = sorted(set(re.findall(r"[゠-ヿー]{3,}", nb)))
        kata_not = [t for t in kata if t not in ledger]
        leak = [p for p in CONSTRAINT_PHRASES if p in r2]
        for ln in cons.split("\n"):
            m = re.sub(r"^- ", "", ln.strip())
            if len(m) > 12 and m in r2:
                leak.append("verbatim:" + m[:20])
        sym = D.safety.detect_prohibited_symbols(r2, language="ja")
        tag_leak = bool(D.w1.TAG_LEAK_RE.search(r2))
        echo = D.w1.detect_r0_echo(r2)
        stage_jpy = {}
        for s in usage["stages"]:
            stage_jpy[s["stage"]] = round(stage_jpy.get(s["stage"], 0) + s["jpy"], 3)
        sentences = [s for s in re.split(r"[。！？!?]", body) if s.strip()]
        out[a] = {"body_chars": len(re.sub(r"\s", "", body)), "title": title, "title_chars": len(title), "n_sentences": len(sentences),
                  "selected_fact_ids": ids, "n_selected_facts": len(ids), "numbers_in_text": nums, "numbers_not_in_ledger": nums_not_in_ledger,
                  "latin_not_in_ledger": lat_not, "katakana_not_in_ledger_literal(翻字ゆれ含む要目視)": kata_not,
                  "constraint_leak_hits": leak, "symbol_qa_findings": sym, "tag_leak": tag_leak, "r0_echo": echo,
                  "generation_sec_total": usage["total"]["sec"], "stage_jpy": stage_jpy, "total_jpy": usage["total"]["jpy"],
                  "model_returned": sorted({s.get("model_returned") for s in usage["stages"]})}
    json.dump(out, open(os.path.join(HERE, "AUX_METRICS_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    L = ["# AUX_METRICS_01(補助指標。人間判断の代替ではない。ユーザーBlind評価前に提示しない。案名つきのFable内部資料)", "",
         "| 指標 | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    rows = [("本文字数(空白除く、タイトル除く)", "body_chars"), ("タイトル字数", "title_chars"), ("文数", "n_sentences"), ("選択Fact数", "n_selected_facts"),
            ("選択Fact ID", "selected_fact_ids"), ("数値(本文中)", "numbers_in_text"), ("Ledger外の数値", "numbers_not_in_ledger"),
            ("Ledger外の英字固有名詞", "latin_not_in_ledger"), ("Ledger非逐語のカタカナ語(翻字ゆれ含む要目視)", "katakana_not_in_ledger_literal(翻字ゆれ含む要目視)"),
            ("制約文混入(grep)", "constraint_leak_hits"), ("記号QA findings", "symbol_qa_findings"), ("タグ残存", "tag_leak"),
            ("生成秒合計(並列実行の影響あり、参考)", "generation_sec_total"), ("実測円合計", "total_jpy"), ("返却model", "model_returned")]
    for lab, k in rows:
        L.append(f"| {lab} | " + " | ".join(str(out[a][k]) for a in ARMS) + " |")
    L += ["", "## stage別実測円", "| stage | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    stages = ["storyline_b3", "w1_r0", "w1_astra_r1", "w1_astra_r2"]
    for s in stages:
        L.append(f"| {s} | " + " | ".join(str(out[a]["stage_jpy"].get(s, "-")) for a in ARMS) + " |")
    L += ["", "注: A/CのB3は既存実測(C=Aの再利用で新規0円、表のC列B3は未発生のため'-')。タイトル末尾の「、」等はProduction postprocess(`normalize_ellipsis_pause_ja`)の決定論変換の結果で、モデル出力の差ではない場合がある。"]
    open(os.path.join(HERE, "AUX_METRICS_01.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))

main()
