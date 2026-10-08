# -*- coding: utf-8 -*-
"""ASTRA-REVISE-MATRIX-01: aggregate (no API). Writes eval/METRICS_MATRIX.json, SUMMARY_MATRIX.md, HUMAN_CHECK_MATRIX.md,
COST_MATRIX.md, USER_PACK.md, _private/MAP.json."""
import json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_matrix as R
H, m, BASE = R.H, R.m, R.BASE
import er052_factlock_writer_trial_01_run as fl

IDS = ["R0", "A_r1", "A_r2", "A_r3", "B_r1", "B_r2", "B_r3"]
USD_JPY = 160.0
LUNA = H.PRICE_LUNA


def jr(p):
    return json.load(open(p, encoding="utf-8"))


def raw_path(i):
    return R.R0_PATH if i == "R0" else f"{BASE}/runs/{i[0]}/r{i[-1]}.md"


def p1_path(i):
    return R.R0_PATH if i == "R0" else f"{BASE}/runs/{i[0]}/r{i[-1]}.p1.md"


def ledger_map():
    out, cur = {}, None
    for ln in m.read(R.LEDGER).split("\n"):
        mm = re.match(r"\[VERIFIED\]\s+([A-Z0-9\-]+):\s*(.*)", ln)
        if mm:
            cur = mm.group(1); out[cur] = mm.group(2)
    return out


def collect():
    M = {}
    for i in IDS:
        p1 = m.read(p1_path(i)); raw = m.read(raw_path(i))
        det = H.det_metrics(p1, R.RUN_DIR)
        detraw = H.det_metrics(raw, R.RUN_DIR)
        fc = jr(f"{BASE}/eval/fc/{i}.json")["parsed"]
        devs = fc.get("deviations", [])
        ii = jr(f"{BASE}/eval/ii/{i}.json")
        sents = fl.split_sentences(p1)
        smap = {s["idx"]: s["text"] for s in sents}
        newc = [{"sentence": smap.get(x["sentence_index"], "?"), "reason": x["reason"]} for x in ii["items"] if x["label"] == "new_specific_claim"]
        meta = None if i == "R0" else jr(f"{BASE}/runs/{i[0]}/r{i[-1]}.response.json")
        M[i] = {"det": det, "markdown_hash_raw": detraw["markdown_hash"], "markdown_bold_raw": detraw["markdown_bold"],
                "symbol_gate_raw": detraw["symbol_gate_findings"], "symbol_gate_p1": det["symbol_gate_findings"],
                "fc_status": fc.get("overall_status"), "major": sum(1 for d in devs if d["severity"] == "MAJOR"),
                "minor": sum(1 for d in devs if d["severity"] == "MINOR"), "deviations": devs,
                "new_claims": len(newc), "new_claim_items": newc, "ii_counts": ii["counts"], "meta": meta}
    return M


def types(d):
    ks = ["changed_fact", "changed_scope", "changed_causality", "changed_certainty", "changed_number", "changed_actor",
          "changed_negation", "changed_comparison", "changed_time", "unsupported_new_claim"]
    return [k for k in ks if d.get(k)]


def jp(x):
    return f"{x:.2f}"


def write_summary(M):
    L = ["# SUMMARY_MATRIX: ASTRA-REVISE-MATRIX-01 (FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_15, 2026-10-08)", "",
         "性質: Trial/DEV。Status=MEASURED(人間確認待ち)、Production変更なし。起点R0 = Fact Lock v1 meta b2 r1 の `original.md`(Writer直後、タグ除去済み)。モデル=gpt-6-astra(reasoning high)。",
         "系列A=ユーザーPromptのみ(developer/systemなし) / 系列B=熟練編集者(developer文あり、Step 1 F2と同一)。逐次: R1入力=R0、R2入力=R1出力、R3入力=R2出力(本文テキスト渡し、previous_response_idなし)。",
         "字数等はタイトル行を除く(Step 1/sweepと同じ`det_metrics`)。FC・決定論指標はMarkdown除去後(P1)の本文。astra費用は**推定単価**(gpt-6-sol 2.00/0.20/10.00 USD/1M x2.5、USD/JPY=160)。", "",
         "| 本 | FC MAJOR | FC MINOR | 新規具体主張(ii) | 字数 | 段落 | 1文段落 | 問い(?/？) | ダッシュ | 台帳外数値 | Markdown残存(raw: #行/**) | 記号Gate(raw/P1) | 費用(推定円) | 秒 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in IDS:
        x = M[i]; d = x["det"]; me = x["meta"]
        L.append(f"| {i} | {x['major']} | {x['minor']} | {x['new_claims']} | {d['chars']} | {d['paragraphs']} | {d['one_sentence_paragraphs']} | {d['questions']} | {d['dash_count']} | "
                 f"{d.get('numbers_out_of_ledger_n')} | {x['markdown_hash_raw']}/{x['markdown_bold_raw']} | {x['symbol_gate_raw']}/{x['symbol_gate_p1']} | "
                 f"{jp(me['cost_jpy_estimated']) if me else '-'} | {me['sec'] if me else '-'} |")
    L += ["", "## 4段x2系列(同じ内容を段ごとに並べ直し)", "", "| 段 | 系列A (MAJOR/MINOR/新規主張/字数/段落/1文段落) | 系列B (同) |", "|---|---|---|"]
    for n, st in (("R0", None), ("R1", "r1"), ("R2", "r2"), ("R3", "r3")):
        if st is None:
            x = M["R0"]; d = x["det"]
            s = f"{x['major']}/{x['minor']}/{x['new_claims']}/{d['chars']}/{d['paragraphs']}/{d['one_sentence_paragraphs']}"
            L.append(f"| R0 | {s} (共通) | {s} (共通) |")
        else:
            cells = []
            for ser in "AB":
                x = M[f"{ser}_{st}"]; d = x["det"]
                cells.append(f"{x['major']}/{x['minor']}/{x['new_claims']}/{d['chars']}/{d['paragraphs']}/{d['one_sentence_paragraphs']}")
            L.append(f"| {n} | {cells[0]} | {cells[1]} |")
    L += ["", "## 新規具体主張(ii, R0比)", "", "R0のnew_specific_claim = 0件を基準。(ii)は台帳・briefに無い具体主張をLLM(gpt-6-luna)が文単位で判定した件数(sweepと同一手法・同一プロンプト)。", ""]
    for i in IDS:
        x = M[i]
        L.append(f"- {i}: {x['new_claims']}件 (R0比 {x['new_claims'] - M['R0']['new_claims']:+d})")
        for c in x["new_claim_items"]:
            L.append(f"    - 「{c['sentence']}」 / 判定理由: {c['reason']}")
    L += ["", "## 注意", "",
          "- N=1 brief x 1回 x 系列あたり1本。FCはgpt-6-luna自己判定(全台帳)。差が1件以内は誤差内で、序列は付けない。",
          "- 面白さはここに載せない(人間盲検 `USER_PACK.md` で判断)。",
          "- 台帳外数値 = 本文中の数値のうちbrief/台帳の数値集合に無いもの(決定論)。"]
    m.write(f"{BASE}/eval/SUMMARY_MATRIX.md", "\n".join(L) + "\n")


def write_human(M):
    led = ledger_map()
    L = ["# HUMAN_CHECK_MATRIX: 重大候補(ユーザー確認用)", "",
         "対象 = JA Fact Check(gpt-6-luna、全台帳)のMAJOR(全件) + MINORのうち 主体(changed_actor)・因果(changed_causality)・否定(changed_negation)の型。", ""]
    n_major = sum(M[i]["major"] for i in IDS)
    key = []
    for i in IDS:
        for d in M[i]["deviations"]:
            t = types(d)
            if d["severity"] == "MAJOR" or any(k in t for k in ("changed_actor", "changed_causality", "changed_negation")):
                key.append((i, d, t))
    L.append(f"MAJOR合計: {n_major}件。主体/因果/否定型のMINOR: {sum(1 for _, d, _ in key if d['severity']=='MINOR')}件。")
    L.append("")
    if not key:
        L += ["**該当なし**(MAJOR 0件、主体・因果・否定型のMINORも0件)。", ""]
    for i, d, t in key:
        fid = d.get("related_fact_id") or ""
        L += [f"## {i} / {d['severity']} / 型: {', '.join(t) or '-'}", f"- NG文: {d['claim_in_article']}", f"- 台帳: {fid} {led.get(fid, '(該当行なし)')}", f"- 理由: {d['issue']} {d['explanation']}", ""]
    L += ["## 参考: 全MINOR一覧(上記基準に該当しないもの含む)", ""]
    for i in IDS:
        for d in M[i]["deviations"]:
            fid = d.get("related_fact_id") or ""
            L += [f"### {i} / {d['severity']} / 型: {', '.join(types(d)) or '-'}", f"- NG文: {d['claim_in_article']}", f"- 台帳: {fid} {led.get(fid, '(該当行なし)')}", f"- 理由: {d['issue']} {d['explanation']}", ""]
    L += ["## 参考: (ii) new_specific_claim 文(台帳・briefに無い具体主張とLLMが判定。FCとは別系統)", ""]
    for i in IDS:
        for c in M[i]["new_claim_items"]:
            L += [f"### {i}", f"- 文: {c['sentence']}", f"- 判定理由: {c['reason']}", ""]
    m.write(f"{BASE}/eval/HUMAN_CHECK_MATRIX.md", "\n".join(L))


def luna_chain():
    rows = [json.loads(l) for l in open(f"{R.RUN_DIR}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
    out = {}
    for r in rows:
        if r["stage"] in ("ja_original", "ja_r1", "ja_r2", "ja_r2_check"):
            i, c, o = r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0
            out[r["stage"]] = {"in": i, "cached": c, "out": o, "reasoning": r.get("reasoning_tokens"),
                               "jpy": H.jpy(LUNA, i, c, o), "sec": r.get("elapsed_seconds")}
    return out


def write_cost(M):
    lc = luna_chain()
    luna12 = lc["ja_r1"]["jpy"] + lc["ja_r2"]["jpy"]
    L = ["# COST_MATRIX (ASTRA-REVISE-MATRIX-01)", "",
         "**注意: astraの単価はrouting contract未登録のため推定**(gpt-6-sol 2.00/0.20/10.00 USD per 1M x2.5 = 5.00/0.50/25.00、USD/JPY=160)。トークン数は実測、円は推定。lunaは登録単価(0.10/0.01/0.50)。", "",
         "## 1. 系列別・段別の実測トークンと推定円", "",
         "| 系列 | 段 | input | cached | output | (うちreasoning) | 推定円 | 秒 | 累積(推定円) |", "|---|---|---|---|---|---|---|---|---|"]
    cum = {}
    tot_tok = {"in": 0, "cached": 0, "out": 0, "reasoning": 0}
    for s in "AB":
        c = 0.0
        cum[s] = []
        for n in (1, 2, 3):
            me = M[f"{s}_r{n}"]["meta"]; u = me["usage"]; c += me["cost_jpy_estimated"]; cum[s].append(c)
            L.append(f"| {s} | R{n} | {u['input_tokens']} | {u['cached_input_tokens']} | {u['output_tokens']} | {u['reasoning_tokens']} | {jp(me['cost_jpy_estimated'])} | {me['sec']} | {jp(c)} |")
            tot_tok["in"] += u["input_tokens"] or 0; tot_tok["cached"] += u["cached_input_tokens"] or 0
            tot_tok["out"] += u["output_tokens"] or 0; tot_tok["reasoning"] += u["reasoning_tokens"] or 0
    ev = [json.loads(l) for l in open(R.LOG, encoding="utf-8") if l.strip()]
    gen_cost = sum(r["cost_jpy"] for r in ev if r["stage"] == "gen")
    fc_cost = sum(r["cost_jpy"] for r in ev if r["stage"] == "fc"); ii_cost = sum(r["cost_jpy"] for r in ev if r["stage"] == "ii")
    L += ["", f"生成6本のトークン合計: input {tot_tok['in']} / cached {tot_tok['cached']} / output {tot_tok['out']} (うちreasoning {tot_tok['reasoning']})。",
          f"実験総額(推定): 生成 ¥{gen_cost:.2f} + FC(luna, 実測トークンx登録単価) ¥{fc_cost:.2f} + (ii) ¥{ii_cost:.2f}(概算計上: 1本0.2円固定、usage非取得) = ¥{gen_cost + fc_cost + ii_cost:.2f}。", "",
         "## 2. 累積(Revise段をどこまで入れるか)", "",
         "| 系列 | R1のみ | R1+R2 | R1+R2+R3 |", "|---|---|---|---|",
         f"| A | {jp(cum['A'][0])} | {jp(cum['A'][1])} | {jp(cum['A'][2])} |", f"| B | {jp(cum['B'][0])} | {jp(cum['B'][1])} | {jp(cum['B'][2])} |", "",
         "## 3. 差し引き: Fact Lock v1 meta b2 r1 の同runのLuna R1+R2(実測トークンx登録単価)", "",
         "同runの`cost.json`は全項目0.0円(cost loggerが課金を記録していない)ため、`raw_usage_log.jsonl`の実測トークンにluna登録単価を掛けて算出した。",
         "", "| Luna段(同run) | input | cached | output | (うちreasoning) | 円 |", "|---|---|---|---|---|---|"]
    for k, nm in (("ja_original", "Writer(original)"), ("ja_r1", "R1"), ("ja_r2", "R2"), ("ja_r2_check", "R2 check")):
        v = lc[k]
        L.append(f"| {nm} | {v['in']} | {v['cached']} | {v['out']} | {v['reasoning']} | {v['jpy']:.3f} |")
    L += ["", f"Luna R1+R2 = ¥{luna12:.3f}(R1 ¥{lc['ja_r1']['jpy']:.3f} + R2 ¥{lc['ja_r2']['jpy']:.3f})。",
          "", "Astra Reviseを Luna R1+R2 の**置換**として入れる場合の純増(推定円) = Astra累積 − Luna R1+R2:", "",
          "| 系列 | R1のみ | R1+R2 | R1+R2+R3 |", "|---|---|---|---|",
          f"| A | {jp(cum['A'][0]-luna12)} | {jp(cum['A'][1]-luna12)} | {jp(cum['A'][2]-luna12)} |",
          f"| B | {jp(cum['B'][0]-luna12)} | {jp(cum['B'][1]-luna12)} | {jp(cum['B'][2]-luna12)} |", "",
          "## 4. 1記事セット換算(文字数一定の前提)", "",
          "前提: 現行1セット約¥52(TTS Standard同期)/約¥43(Batch)に本実験の1記事分(約1000字)のRevise増分を足す。Astraにはbatch割引を仮定しない(未登録)。Luna R1+R2を置換する場合は純増、置換せずに追加する場合は総増を使う。", "",
          "| 系列 | 段数 | 追加(総増,推定円) | 追加(純増,推定円) | 合計 Standard ¥52基準(総増/純増) | 合計 Batch ¥43基準(総増/純増) |", "|---|---|---|---|---|---|"]
    for s in "AB":
        for k, nm in enumerate(("R1のみ", "R1+R2", "R1+R2+R3")):
            g = cum[s][k]; nt = g - luna12
            L.append(f"| {s} | {nm} | {jp(g)} | {jp(nt)} | {jp(52 + g)} / {jp(52 + nt)} | {jp(43 + g)} / {jp(43 + nt)} |")
    L += ["", "注記: astra単価は推定値(sol x2.5)。実単価が登録されたら再計算が必要。1記事のみの測定で、段あたり費用は出力長・reasoning量で変動する(同じ段でも ±数十%)。"]
    m.write(f"{BASE}/eval/COST_MATRIX.md", "\n".join(L) + "\n")
    return {"luna12": luna12, "cum": cum, "gen": gen_cost, "fc": fc_cost, "ii": ii_cost, "tok": tot_tok}


def write_pack(M):
    rnd = random.Random(20261008)
    a_is_x = rnd.random() < 0.5
    mp = {"X": "A" if a_is_x else "B", "Y": "B" if a_is_x else "A", "seed": 20261008,
          "note": "X/Y -> series. A=ユーザーPromptのみ, B=熟練編集者"}
    m.jwrite(f"{BASE}/_private/MAP.json", mp)
    lab = {"A": "X" if a_is_x else "Y", "B": "Y" if a_is_x else "X"}
    L = ["# USER_PACK: 同じ元記事の改稿 7本(段は明示・系列は伏せています)", "",
         "- 元記事(R0)から、2つの書き方(X・Y)で、R1 → R2 → R3 と順に改稿しました(各段は前の段の本文を入力にしています)。",
         "- 見出し・太字記号(Markdown)は読みやすさのため除去してあります。字数はタイトル行を除いた本文の文字数(改行除く)です。",
         "- 事実確認の結果は、先入観を避けるためここには載せていません。", "", "---", ""]
    L += [f"## R0(元記事) 字数 {M['R0']['det']['chars']}", "", m.read(p1_path('R0')).strip(), "", "---", ""]
    for n in (1, 2, 3):
        for lb in ("X", "Y"):
            ser = mp[lb]; i = f"{ser}_r{n}"
            L += [f"## R{n} / {lb} 字数 {M[i]['det']['chars']}", "", m.read(p1_path(i)).strip(), "", "---", ""]
    m.write(f"{BASE}/USER_PACK.md", "\n".join(L))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    M = collect()
    m.jwrite(f"{BASE}/eval/METRICS_MATRIX.json", {i: {k: v for k, v in x.items()} for i, x in M.items()})
    write_summary(M); write_human(M); c = write_cost(M); write_pack(M)
    m.jwrite(f"{BASE}/eval/COST_SUMMARY.json", c)
    print("report done", {i: (M[i]["major"], M[i]["minor"], M[i]["new_claims"], M[i]["det"]["chars"]) for i in IDS})


if __name__ == "__main__":
    main()
