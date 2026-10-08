# -*- coding: utf-8 -*-
"""ASTRA-REVISE-MATRIX-02: aggregate (no API). Writes eval/METRICS_MATRIX_02.json, SUMMARY_MATRIX_02.md, HUMAN_CHECK_MATRIX_02.md,
COST_MATRIX_02.md, USER_PACK_02.md."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_matrix2 as R
H, m, BASE, ART = R.H, R.m, R.BASE, R.ART
import er052_factlock_writer_trial_01_run as fl

ARTS = ["hormuz", "small_bag"]
LABEL = {"hormuz": "ホルムズ", "small_bag": "ミニバッグ"}
IDS = ["R0", "A_r1", "A_r2", "B_r1", "B_r2"]
LUNA = H.PRICE_LUNA
M1 = f"{R.FL}/astra_revise_matrix_01"


def jr(p):
    return json.load(open(p, encoding="utf-8"))


def p1_path(art, i):
    return ART[art]["r0"] if i == "R0" else f"{BASE}/runs/{art}/{i[0]}/r{i[-1]}.p1.md"


def raw_path(art, i):
    return ART[art]["r0"] if i == "R0" else f"{BASE}/runs/{art}/{i[0]}/r{i[-1]}.md"


def ledger_map(art):
    out, cur = {}, None
    for ln in m.read(ART[art]["ledger"]).split("\n"):
        mm = re.match(r"\[VERIFIED\]\s+([A-Z0-9\-]+):\s*(.*)", ln)
        if mm:
            cur = mm.group(1); out[cur] = mm.group(2)
    return out


def collect(art):
    M = {}
    for i in IDS:
        tid = f"{art}_{i}"
        p1 = m.read(p1_path(art, i)); raw = m.read(raw_path(art, i))
        det = H.det_metrics(p1, ART[art]["d_src"]); detraw = H.det_metrics(raw, ART[art]["d_src"])
        fc = jr(f"{BASE}/eval/fc/{tid}.json")["parsed"]
        devs = fc.get("deviations", [])
        ii = jr(f"{BASE}/eval/ii/{tid}.json")
        sents = fl.split_sentences(p1)
        smap = {s["idx"]: s["text"] for s in sents}
        newc = [{"sentence": smap.get(x["sentence_index"], "?"), "reason": x["reason"]} for x in ii["items"] if x["label"] == "new_specific_claim"]
        meta = None if i == "R0" else jr(f"{BASE}/runs/{art}/{i[0]}/r{i[-1]}.response.json")
        gate = []
        if detraw["symbol_gate_findings"] or det["symbol_gate_findings"]:
            import er003_audio_tts_asr_safety as safety
            gate = safety.detect_prohibited_symbols(p1, "ja")
        M[i] = {"det": det, "markdown_hash_raw": detraw["markdown_hash"], "markdown_bold_raw": detraw["markdown_bold"],
                "symbol_gate_raw": detraw["symbol_gate_findings"], "symbol_gate_p1": det["symbol_gate_findings"], "symbol_gate_p1_items": gate,
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


def row(i, x, lab=None):
    d = x["det"]; me = x["meta"]
    gate = f"{x['symbol_gate_raw']}/{x['symbol_gate_p1']}"
    return (f"| {lab or i} | {x['major']} | {x['minor']} | {x['new_claims']} | {d['chars']} | {d['paragraphs']} | {d['one_sentence_paragraphs']} | {d['questions']} | {d['dash_count']} | "
            f"{d.get('numbers_out_of_ledger_n')} | {x['markdown_hash_raw']}/{x['markdown_bold_raw']} | {gate} | {jp(me['cost_jpy_estimated']) if me else '-'} | {me['sec'] if me else '-'} |")


HEAD = ("| 本 | FC MAJOR | FC MINOR | 新規具体主張(ii) | 字数 | 段落 | 1文段落 | 問い(?/？) | ダッシュ | 台帳外数値 | Markdown残存(raw: #行/**) | 記号Gate(raw/P1) | 費用(推定円) | 秒 |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def meta01():
    d = jr(f"{M1}/eval/METRICS_MATRIX.json")
    return {i: d[i] for i in IDS}


def write_summary(MM):
    m01 = meta01()
    L = ["# SUMMARY_MATRIX_02: ASTRA-REVISE-MATRIX-02 (FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_16, 2026-10-08)", "",
         "性質: Trial/DEV。Status=MEASURED(人間確認待ち)、Production変更なし。モデル=gpt-6-astra(reasoning high)、R1/R2のみ(R3なし)。",
         "X=系列A(ユーザーPromptのみ、developer/systemなし) / Y=系列B(熟練編集者: developer文あり、Step 1 F2と同一)。逐次: R1入力=R0、R2入力=R1出力(本文テキスト渡し、previous_response_idなし)。",
         "字数等はタイトル行を除く(Step 1/sweepと同じ`det_metrics`)。FC・決定論指標はMarkdown除去後(P1)の本文。astra費用は**推定単価**(gpt-6-sol 2.00/0.20/10.00 USD/1M x2.5、USD/JPY=160)。",
         "meta行は委任_15(ASTRA-REVISE-MATRIX-01)の既存値の転記(再評価なし)。", ""]
    for art in ARTS:
        L += [f"## {LABEL[art]} ({art})", "", HEAD]
        for i in IDS:
            lab = {"R0": "R0", "A_r1": "X_R1", "A_r2": "X_R2", "B_r1": "Y_R1", "B_r2": "Y_R2"}[i]
            L.append(row(i, MM[art][i], lab))
        L.append("")
    L += ["## meta(委任_15、既存値の転記・再評価なし)", "", HEAD]
    for i in IDS:
        lab = {"R0": "R0", "A_r1": "X_R1", "A_r2": "X_R2", "B_r1": "Y_R1", "B_r2": "Y_R2"}[i]
        L.append(row(i, m01[i], lab))
    L += ["", "## 記事x段x系列(MAJOR/MINOR/新規主張/字数/段落/1文段落)", "", "| 記事 | 段 | X (ユーザーPromptのみ) | Y (熟練編集者) |", "|---|---|---|---|"]
    allm = [("meta(委任_15)", m01)] + [(LABEL[a], MM[a]) for a in ARTS]
    for nm, D in allm:
        x = D["R0"]; d = x["det"]
        s = f"{x['major']}/{x['minor']}/{x['new_claims']}/{d['chars']}/{d['paragraphs']}/{d['one_sentence_paragraphs']}"
        L.append(f"| {nm} | R0 | {s} (共通) | {s} (共通) |")
        for st in ("r1", "r2"):
            c = []
            for ser in "AB":
                x = D[f"{ser}_{st}"]; d = x["det"]
                c.append(f"{x['major']}/{x['minor']}/{x['new_claims']}/{d['chars']}/{d['paragraphs']}/{d['one_sentence_paragraphs']}")
            L.append(f"| {nm} | {st.upper()} | {c[0]} | {c[1]} |")
    L += ["", "## 重大(MAJOR)・軽微(MINOR)カウント(FC=gpt-6-luna全台帳、自己判定)", "",
          "| 記事 | X_R1 | X_R2 | Y_R1 | Y_R2 | 記事計(X/Y x R1/R2 の4本、MAJOR/MINOR) |", "|---|---|---|---|---|---|"]
    for nm, D in allm:
        cs = [f"{D[k]['major']}/{D[k]['minor']}" for k in ("A_r1", "A_r2", "B_r1", "B_r2")]
        tM = sum(D[k]["major"] for k in ("A_r1", "A_r2", "B_r1", "B_r2")); tm = sum(D[k]["minor"] for k in ("A_r1", "A_r2", "B_r1", "B_r2"))
        L.append(f"| {nm} | {cs[0]} | {cs[1]} | {cs[2]} | {cs[3]} | MAJOR {tM} / MINOR {tm} |")
    L += ["(表記は MAJOR/MINOR)", "", "## 記号Gate(計測のみ)の該当(P1本文)", ""]
    for art in ARTS:
        for i in IDS:
            x = MM[art][i]
            if x["symbol_gate_p1"]:
                L.append(f"- {art} {i}: {x['symbol_gate_p1']}件 {json.dumps(x['symbol_gate_p1_items'], ensure_ascii=False)[:600]}")
    L += ["", "## 新規具体主張(ii, R0比)", "", "(ii)は台帳・briefに無い具体主張をLLM(gpt-6-luna)が文単位で判定した件数(sweepと同一手法)。", ""]
    for art in ARTS:
        for i in IDS:
            x = MM[art][i]
            L.append(f"- {art} {i}: {x['new_claims']}件 (R0比 {x['new_claims'] - MM[art]['R0']['new_claims']:+d})")
            for c in x["new_claim_items"]:
                L.append(f"    - 「{c['sentence']}」 / 判定理由: {c['reason']}")
    L += ["", "## 注意", "",
          "- N=1 brief x 1回 x 系列あたり1本。FCはgpt-6-luna自己判定(全台帳)。差が1件以内は誤差内で、序列は付けない。",
          "- 面白さはここに載せない(人間読みは `USER_PACK_02.md`)。台帳外数値 = 本文中の数値のうちbrief/台帳の数値集合に無いもの(決定論)。",
          "- ミニバッグの台帳外数値は、E2E run_02のbrief/台帳にある年・日付の数値集合との比較。"]
    m.write(f"{BASE}/eval/SUMMARY_MATRIX_02.md", "\n".join(L) + "\n")


def write_human(MM):
    L = ["# HUMAN_CHECK_MATRIX_02: 重大候補(ユーザー確認用)", "",
         "対象 = JA Fact Check(gpt-6-luna、全台帳)のMAJOR(全件) + MINORのうち 主体(changed_actor)・因果(changed_causality)・否定(changed_negation)の型。3行形式(NG文・台帳・理由)。", ""]
    nM = sum(MM[a][i]["major"] for a in ARTS for i in IDS)
    key = []
    for art in ARTS:
        led = ledger_map(art)
        for i in IDS:
            for d in MM[art][i]["deviations"]:
                t = types(d)
                if d["severity"] == "MAJOR" or any(k in t for k in ("changed_actor", "changed_causality", "changed_negation")):
                    key.append((art, i, d, t, led))
    L.append(f"MAJOR合計(R0含む、記事共通R0は1回): {nM}件。主体/因果/否定型のMINOR: {sum(1 for k in key if k[2]['severity']=='MINOR')}件。")
    L.append("")
    if not key:
        L += ["**該当なし**(MAJOR 0件、主体・因果・否定型のMINORも0件)。", ""]
    lab = {"R0": "R0", "A_r1": "X_R1", "A_r2": "X_R2", "B_r1": "Y_R1", "B_r2": "Y_R2"}
    for art, i, d, t, led in key:
        fid = d.get("related_fact_id") or ""
        L += [f"## {LABEL[art]} {lab[i]} / {d['severity']} / 型: {', '.join(t) or '-'}", f"- NG文: {d['claim_in_article']}", f"- 台帳: {fid} {led.get(fid, '(該当行なし)')}", f"- 理由: {d['issue']} {d['explanation']}", ""]
    L += ["## 参考: 全指摘(MAJOR/MINOR)一覧(上記基準に該当しないもの含む)", ""]
    for art in ARTS:
        led = ledger_map(art)
        for i in IDS:
            for d in MM[art][i]["deviations"]:
                fid = d.get("related_fact_id") or ""
                L += [f"### {LABEL[art]} {lab[i]} / {d['severity']} / 型: {', '.join(types(d)) or '-'}", f"- NG文: {d['claim_in_article']}", f"- 台帳: {fid} {led.get(fid, '(該当行なし)')}", f"- 理由: {d['issue']} {d['explanation']}", ""]
    L += ["## 参考: (ii) new_specific_claim 文(FCとは別系統)", ""]
    for art in ARTS:
        for i in IDS:
            for c in MM[art][i]["new_claim_items"]:
                L += [f"### {LABEL[art]} {lab[i]}", f"- 文: {c['sentence']}", f"- 判定理由: {c['reason']}", ""]
    m.write(f"{BASE}/eval/HUMAN_CHECK_MATRIX_02.md", "\n".join(L))


def luna_old(art):
    if art == "hormuz":
        rows = [json.loads(l) for l in open(f"{R.HZ}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
        out = {}
        for r in rows:
            if r["stage"] in ("ja_r1", "ja_r2"):
                out[r["stage"]] = H.jpy(LUNA, r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0)
        return out, "同run raw_usage_logの実測トークンxluna登録単価(同runのcost.jsonは課金0記録のため)"
    c = jr(f"{R.E2E}/cost.json")["by_stage_jpy"]
    return {"ja_r1": c["ja_r1"], "ja_r2": c["ja_r2"]}, "E2E run_02 cost.json の ja_r1 + ja_r2"


def write_cost(MM):
    ev = [json.loads(l) for l in open(R.LOG, encoding="utf-8") if l.strip()]
    L = ["# COST_MATRIX_02 (ASTRA-REVISE-MATRIX-02)", "",
         "**注意: astraの単価はrouting contract未登録のため推定**(gpt-6-sol 2.00/0.20/10.00 USD per 1M x2.5 = 5.00/0.50/25.00、USD/JPY=160)。トークン数は実測、円は推定。lunaは登録単価(0.10/0.01/0.50)。", "",
         "## 1. 記事・系列別・段別の実測トークンと推定円", "",
         "| 記事 | 系列 | 段 | input | cached | output | (うちreasoning) | 推定円 | 秒 | 累積(推定円) |", "|---|---|---|---|---|---|---|---|---|---|"]
    cum = {}
    tok = {"in": 0, "cached": 0, "out": 0, "reasoning": 0}
    for art in ARTS:
        for s, sl in (("A", "X"), ("B", "Y")):
            c = 0.0; cum[(art, s)] = []
            for n in R.ROUNDS:
                me = MM[art][f"{s}_r{n}"]["meta"]; u = me["usage"]; c += me["cost_jpy_estimated"]; cum[(art, s)].append(c)
                L.append(f"| {LABEL[art]} | {sl} | R{n} | {u['input_tokens']} | {u['cached_input_tokens']} | {u['output_tokens']} | {u['reasoning_tokens']} | {jp(me['cost_jpy_estimated'])} | {me['sec']} | {jp(c)} |")
                tok["in"] += u["input_tokens"] or 0; tok["cached"] += u["cached_input_tokens"] or 0; tok["out"] += u["output_tokens"] or 0; tok["reasoning"] += u["reasoning_tokens"] or 0
    gen = sum(r["cost_jpy"] for r in ev if r["stage"] == "gen"); fc = sum(r["cost_jpy"] for r in ev if r["stage"] == "fc")
    ii = sum(r["cost_jpy"] for r in ev if r["stage"] == "ii"); r0c = R.r0_cost()
    L += ["", f"生成8本のトークン合計: input {tok['in']} / cached {tok['cached']} / output {tok['out']} (うちreasoning {tok['reasoning']})。",
          f"実験総額(推定): 生成(astra推定) ¥{gen:.2f} + ミニバッグR0生成(Luna、Writer+JA FC+タグ照合の実測xluna登録単価、R0ログ内のみ=タグ照合(i)(ii)のusageはcl.install経由で含む) ¥{r0c:.2f} + FC(luna) ¥{fc:.2f} + (ii) ¥{ii:.2f}(概算計上: 1本0.2円固定) = **¥{gen + r0c + fc + ii:.2f}**。", "",
         "## 2. 累積と旧Luna R1+R2実費との差", ""]
    L += ["| 記事 | 系列 | Astra R1のみ(推定円) | Astra R1+R2(推定円) | 旧Luna R1+R2実費 | 純増(R1+R2 - Luna R1+R2) | 旧Lunaの根拠 |", "|---|---|---|---|---|---|---|"]
    olds = {}
    for art in ARTS:
        o, why = luna_old(art); olds[art] = sum(o.values())
        for s, sl in (("A", "X"), ("B", "Y")):
            cc = cum[(art, s)]
            L.append(f"| {LABEL[art]} | {sl} | {jp(cc[0])} | {jp(cc[1])} | {olds[art]:.3f} | {jp(cc[1] - olds[art])} | {why} |")
    try:
        cs = jr(f"{M1}/eval/COST_SUMMARY.json")
        L += ["", f"参考(meta、委任_15の転記): X R1 {jp(cs['cum']['A'][0])} / R1+R2 {jp(cs['cum']['A'][1])}、Y R1 {jp(cs['cum']['B'][0])} / R1+R2 {jp(cs['cum']['B'][1])}、旧Luna R1+R2 {cs['luna12']:.3f}。"]
    except Exception:
        pass
    L += ["", "## 3. 1記事セット換算", "",
          "前提: 現行1セット約¥52(TTS Standard同期)/約¥43(Batch)に、本実験の1記事分(約1000字)のAstra Revise増分を足す。Astraにはbatch割引を仮定しない(未登録)。純増はLuna R1+R2を置換する場合、総増は置換せず追加する場合。", "",
          "| 記事 | 系列 | 段 | 総増(推定円) | 純増(推定円) | Standard ¥52基準(総増/純増) | Batch ¥43基準(総増/純増) |", "|---|---|---|---|---|---|---|"]
    for art in ARTS:
        for s, sl in (("A", "X"), ("B", "Y")):
            for k, nm in enumerate(("R1のみ", "R1+R2")):
                g = cum[(art, s)][k]; nt = g - olds[art]
                L.append(f"| {LABEL[art]} | {sl} | {nm} | {jp(g)} | {jp(nt)} | {jp(52 + g)} / {jp(52 + nt)} | {jp(43 + g)} / {jp(43 + nt)} |")
    allr2 = [cum[(a, s)][1] for a in ARTS for s in "AB"]
    L += ["", f"R1+R2の4系列平均(推定): ¥{sum(allr2) / len(allr2):.2f}(最小¥{min(allr2):.2f}-最大¥{max(allr2):.2f})。",
          "注記: astra単価は推定値(sol x2.5)。実単価が登録されたら再計算が必要。段あたり費用は出力長・reasoning量で変動する。"]
    m.write(f"{BASE}/eval/COST_MATRIX_02.md", "\n".join(L) + "\n")
    return {"gen": gen, "r0": r0c, "fc": fc, "ii": ii, "total": gen + r0c + fc + ii, "tok": tok, "cum": {f"{k[0]}_{k[1]}": v for k, v in cum.items()}, "olds": olds}


def write_pack(MM):
    L = ["# USER_PACK_02: 2記事 x (元記事 / X-R2 / Y-R2) 全6本", "",
         "- 各記事について、元記事(R0)から、2つの書き方で2回(R1 → R2)改稿した **R2** を載せています(R1は省略)。",
         "- **X = ユーザーPromptのみ**(「事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。」だけを渡したもの)。",
         "- **Y = 熟練編集者**(上記に加え、「あなたは熟練の編集者です。元記事の事実はそのままに、読者が思わず続きを聞きたくなる記事に書き直してください。構成の組み替え…」という指示を付けたもの)。",
         "- 見出し・太字記号(Markdown)は読みやすさのため除去してあります。字数はタイトル行を除いた本文の文字数(改行除く)です。",
         "- 事実確認(FC)の結果は先入観を避けるためここには載せていません(別表: `eval/HUMAN_CHECK_MATRIX_02.md`、`eval/SUMMARY_MATRIX_02.md`)。", "", "---", ""]
    for art in ARTS:
        L += [f"# 記事: {LABEL[art]}", ""]
        for lab, i in (("元記事(R0)", "R0"), ("X-R2(ユーザーPromptのみ)", "A_r2"), ("Y-R2(熟練編集者)", "B_r2")):
            L += [f"## {LABEL[art]} / {lab} 字数 {MM[art][i]['det']['chars']}", "", m.read(p1_path(art, i)).strip(), "", "---", ""]
    m.write(f"{BASE}/USER_PACK_02.md", "\n".join(L))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    MM = {a: collect(a) for a in ARTS}
    m.jwrite(f"{BASE}/eval/METRICS_MATRIX_02.json", MM)
    write_summary(MM); write_human(MM); c = write_cost(MM); write_pack(MM)
    m.jwrite(f"{BASE}/eval/COST_SUMMARY_02.json", c)
    print("report done")
    for a in ARTS:
        print(a, {i: (MM[a][i]["major"], MM[a][i]["minor"], MM[a][i]["new_claims"], MM[a][i]["det"]["chars"]) for i in IDS})
    print("total", round(c["total"], 2))


if __name__ == "__main__":
    main()
