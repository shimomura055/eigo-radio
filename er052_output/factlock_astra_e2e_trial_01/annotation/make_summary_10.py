# -*- coding: utf-8 -*-
"""委任_10: ANNOTATION_SUMMARY_01.md を10テーマ表(+(c)(d)(e)記録+Bash使用注記者一覧)で再生成。数値は check/ out/merged/ final/ audit/ の実測。"""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
SLUGS = "byd_recall central_bank_mortgage hormuz inbound_tourism meta openai_copyright semiconductor_earnings small_bag space_weapons streaming_price".split()
B3V = {"hormuz": "v2", "streaming_price": "v2"}
J = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
ex = lambda p: os.path.exists(os.path.join(HERE, p))
def single(N, s):
    d = J(f"check/{N}/{s}.json"); bad = [k for k, v in d.items() if isinstance(v, dict) and v.get("status") == "FAIL"]
    amb = d["b_ledger_mapping"].get("ambiguous_fact") or {}
    return d["verdict"] + (f"({','.join(bad)})" if bad else "") + (" +AMBIG" if amb else "")
o = []; w = o.append
w("# ANNOTATION_SUMMARY_01(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_10 更新、2026-10-09)\n")
w("委任_09版(旧表)は `ANNOTATION_SUMMARY_01_prev09.md` に保存。数値は annotation/check/, out/merged/, final/, audit/ の実測。AMBIG=AMBIGUOUS台帳IDへの紐付けあり(運用明確化(c)でWARN+`ambiguous_fact`フラグ。評価時は別集計)。\n")
w("## 1 10テーマ表\n")
w("| テーマ | B3版 | 単独A | 単独B | 統合 | final | inputs配線 | G0実照合 | 事実数 | 中核/周辺 | cap_dropped | ambiguous_fact(統合) | 分割一致率 | 中核Jaccard | 判定線(0.8/0.67) |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
g0 = json.load(open(os.path.join(BASE, "g0_real_annotation_01", "g0_summary.json"), encoding="utf-8"))
for s in SLUGS:
    a, b = single("A", s), single("B", s)
    if ex(f"out/merged/{s}/agreement.json"):
        ag = J(f"out/merged/{s}/agreement.json"); mc = J(f"out/merged/{s}/merged_check_result.json"); ma = J(f"out/merged/{s}/merged_annotation.json")
        cn = mc["c_numbers"]; nc = len(cn["expected_core_concepts"]); sj = ag["core_jaccard"]
        amb = mc["b_ledger_mapping"].get("ambiguous_fact") or {}
        line = "超え" if (ag["split_agreement_rate"] >= 0.8 and (sj is None or sj >= 0.67)) else "未達"
        if sj is None: line += "(中核0件でJaccard算出不能)"
        row = [mc["verdict"], "有" if ex(f"final/{s}/annotation.json") else "無", "済" if os.path.exists(os.path.join(BASE, "inputs", s, "annotation.json")) else "無",
               ("PASS" if g0.get(s, {}).get("pass") else "FAIL") if s in g0 else "-", len(ma["facts"]), f"{nc}/{cn['countable_concepts'] - nc}", cn["cap_dropped_count"],
               dict(amb) or "-", f"{ag['split_agreement_rate']:.2f}", ("%.2f" % sj) if sj is not None else "n/a", line]
    else:
        row = ["未統合(単独PASSが2本揃わず)", "無", "無", "-", "-", "-", "-", "-", "-", "-", "-"]
    w(f"| {s} | {B3V.get(s, 'v1')} | {a} | {b} | " + " | ".join(str(x) for x in row) + " |")
w("\n- G0実照合は `g0_real_annotation_01/g0_summary.json`(runner `run --g0-only`、実注記)。hormuz・streaming_priceは注記も統合もB3 v2(`stage_r/<slug>/storyline_b3_v2/`)が基準で、inputsには v2 の原B3/原JSON+`input_manifest.json`(凍結sha LF値)を置いた。")
w("- inbound_tourism: 再注記(v1-brief, 台帳ID `F01`形式)の単独検査はA・Bとも c_numbers FAIL。(c)でb_ledger_mappingはPASS(AMBIG)になったが、c_numbers FAILが残る。内訳はA=`8`(Storyline「8月単月」)の分類漏れ+台帳ID括弧`（F01）`内の数字誤検出、B=概念重複2件+`2026`分類漏れ+同ID誤検出。`ID_RE`が連字符なしID(F01)を除外できないため括弧内IDの数字(01,02,03,06)を分類漏れと誤検出(検査script側の欠陥候補。IDマスク修正だけではA・Bとも別の実FAILが残る=スクラッチ実測。要Fable判断)。統合しない。\n")
w("## 2 (c)(d)(e) 運用明確化の記録(Fable判断、2026-10-09)\n")
w("- (c) AMBIGUOUS台帳IDの紐付けは許容+`ambiguous_fact`フラグ(WARN)。NOT_VERIFIED/REJECTED等は従来どおりFAIL。事前登録(PREREGISTRATION v2.2 5-12)と整合。正本は `stage_r/SPEC_V2_CLARIFICATIONS.md` (c)。ユーザーが覆した場合は該当3テーマ(inbound_tourism / semiconductor_earnings / streaming_price)を除外。")
w("- (d) 注記者が許可Writeでなく Bash `cat >` で自分の reply.md を書いた件: 他パス接触0・隔離維持のため採用。既存監査scriptのVIOLATIONは許可済みWrite/返却ツールと自プロンプトパスの禁止語該当による誤判定で、補助監査(AUDIT_SUMMARY.md)の結果を正とする。")
w("- (e) 「・」行頭への【事実N】挿入は検査PASS・仕様§2に反しないため許容。")
w("- 仕様sha256はLF正規化後の値を正とし、CRLF生バイト値は併記(runner g0.json の spec_sha256 に raw / lf_normalized を併記)。\n")
w("## 3 (c)反映による検査結果の変化(単独検査)\n")
w("| テーマ | 注記者 | 旧(委任_09) | 新(委任_10) | 備考 |"); w("|---|---|---|---|---|")
old = {"semiconductor_earnings": "FAIL(b)", "streaming_price": "FAIL(b)/STOP", "inbound_tourism": "FAIL(b,c)"}
for s in ("semiconductor_earnings", "streaming_price", "inbound_tourism"):
    for N in "AB":
        note = {"semiconductor_earnings": "同一返答、(c)のみで変化", "streaming_price": "再注記(B3 v2)。旧はv1(B=STOP)", "inbound_tourism": "再注記。b解消、c残"}[s]
        w(f"| {s} | {N} | {old[s]} | {single(N, s)} | {note} |")
w("\n## 4 Bash使用注記者(委任_09監査 annotation/audit/audit_all.json の v1ラウンド分)\n")
au = J("audit/audit_all.json")
bash = sorted(k for k, v in au.items() if any(t == "Bash" for t, _ in v["tools"]))
w("- " + ", ".join(bash) + f"(計{len(bash)}本)。")
w("- 採用済み統合6テーマで該当: byd(B), central_bank_mortgage(B), meta(B), openai_copyright(A,B), small_bag(A), space_weapons(A,B)。(d)により採用。")
w("- 委任_10時点で再注記済みの hormuz / streaming_price / inbound_tourism のA/B(計6本)は transcript が未保存のため、本版では**未監査**(呼び出し側が transcript.jsonl 保存後に監査する。手順は RUN_ANNOTATION.md 末尾)。ディレクトリ上の transcript.jsonl は旧ラウンド(v1)のもの。")
open(os.path.join(HERE, "ANNOTATION_SUMMARY_01.md"), "w", encoding="utf-8", newline="\n").write("\n".join(o) + "\n")
print("\n".join(o[:22]))
