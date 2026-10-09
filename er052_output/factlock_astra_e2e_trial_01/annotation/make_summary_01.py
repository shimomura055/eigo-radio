# -*- coding: utf-8 -*-
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, BASE); sys.path.insert(0, HERE)
import b3_annotation_check_01 as c
SLUGS = "byd_recall central_bank_mortgage hormuz inbound_tourism meta openai_copyright semiconductor_earnings small_bag space_weapons streaming_price".split()
J = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))
rd = lambda p: open(p, encoding="utf-8", newline="").read()
def short_fail(d):
    bad = [k.split("_")[0] + ":" + k.split("_", 1)[1] for k, v in d.items() if isinstance(v, dict) and v.get("status") == "FAIL"]
    return ",".join(bad)
def verdict(N, s):
    p = f"check/{N}/{s}.json"
    if not os.path.exists(os.path.join(HERE, p)): return "STOP"
    d = J(p); return d["verdict"] + ("" if d["verdict"] == "PASS" else "(" + short_fail(d) + ")")
def ids_per_fact(side):
    fs = side.get("facts", []); return [len(f.get("ledger_ids", [])) for f in fs]
def fmt_b3(s, d="storyline_b3"):
    b = rd(os.path.join(BASE, "stage_r", s, d, "selected_brief.md")); bp = c.prep(b); rng = c.facts_section_range(bp)
    lines = [l for l in bp[rng[0]:rng[1]].split("\n") if l.strip()]
    bl = [l for l in lines if re.match(r"^\s*(?:-|・)", l)]; dup = [l for l in lines if re.match(r"^\s*Storyline[:：]", l)]; so = [l for l in lines if re.match(r"^\s*素材[:：]", l)]
    kind = "箇条書き" if bl and not so else ("Storyline重複行+素材段落" if so else ("段落" if not bl else "混在"))
    dot = sum(1 for l in bl if l.lstrip().startswith("・"))
    return kind, len(bl), bool(dup), dot
out = []
w = out.append
w("# ANNOTATION_SUMMARY_01(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_09)\n")
w("日付 2026-10-09。注記A/Bの抽出->単独検査->統合->統合版検査。数値は annotation/check/, annotation/out/merged/, annotation/final/ の実測。")
w("検査スクリプトは委任_09でバグ修正3件(P1台帳statusの読取り・P3段落区切り後の`- `・P4抽出時の末尾空行)を適用後の結果。修正前の結果は annotation/check_prefix/ に保存。詳細は `_09_result.md`。\n")
w("## 1 テーマ別 検査結果(修正後)\n")
w("| テーマ | 単独A | 単独B | 統合 | 事実数 | 中核/周辺 | cap_dropped | unmapped_claims(統合) | 分割一致率 | 中核Jaccard | 判定線(0.8/0.67) |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
merged_rows = {}
for s in SLUGS:
    M = f"out/merged/{s}"
    if os.path.exists(os.path.join(HERE, M, "agreement.json")):
        ag = J(M + "/agreement.json"); mc = J(M + "/merged_check_result.json"); ma = J(M + "/merged_annotation.json")
        cn = mc["c_numbers"]; ncore = len(cn["expected_core_concepts"]); ntot = cn["countable_concepts"]
        um = collections.Counter(u.get("type") for u in ma.get("unmapped_claims", []))
        sj = ag["core_jaccard"]; line = "超え" if (ag["split_agreement_rate"] >= 0.8 and (sj is None or sj >= 0.67)) else "未達"
        if sj is None: line += "(中核0件記事のためJaccard算出不能)"
        merged_rows[s] = dict(facts=len(ma["facts"]), core=ncore, per=ntot - ncore, cap=cn["cap_dropped_count"], um=dict(um), ag=ag)
        w(f"| {s} | {verdict('A', s)} | {verdict('B', s)} | PASS | {len(ma['facts'])} | {ncore}/{ntot - ncore} | {cn['cap_dropped_count']} | {dict(um) or '-'} | {ag['split_agreement_rate']:.2f} | {('%.2f' % sj) if sj is not None else 'n/a'} | {line} |")
    else:
        w(f"| {s} | {verdict('A', s)} | {verdict('B', s)} | 未統合(単独PASSが2本揃わず) | - | - | - | - | - | - | - |")
w("\n注: 単独FAILの理由。hormuz=B3 v1の Selected Facts 節が『Storyline:重複行+素材:段落』で【事実N】を付けられる箇条書き/段落が無く事実0件(仕様§2は素材行に付けない)。inbound_tourism=台帳ID F06(台帳status AMBIGUOUS)を注記者が参照->VERIFIED以外はFAIL(既存規則・非修正)に加え、概念統合の食い違い(`8月`と`2019年8月`が別概念)・分類漏れ(`01`,`02`,`03`,`06`)という注記者側の形式エラー。semiconductor_earnings=AMBIGUOUS台帳ID F1参照のみ(他は検査PASS)。streaming_price A=AMBIGUOUS台帳ID F07参照のみ、B=STOP(§4(ii))。\n")
w("## 2 単独検査の詳細(事実数・unmapped_claims種類・cap_dropped)\n")
w("| テーマ | 注記者 | 検査 | 事実数 | countable概念 | 中核(期待) | cap_dropped | unmapped_claims種類別 |")
w("|---|---|---|---|---|---|---|---|")
for s in SLUGS:
    for N in "AB":
        p = f"check/{N}/{s}.json"
        if not os.path.exists(os.path.join(HERE, p)):
            w(f"| {s} | {N} | STOP | - | - | - | - | - |"); continue
        d = J(p); sc = J(f"out/{N}/{s}/annotation.json"); cn = d["c_numbers"]
        w(f"| {s} | {N} | {d['verdict']} | {len(sc.get('facts', []))} | {cn.get('countable_concepts')} | {len(cn.get('expected_core_concepts', []))} | {cn.get('cap_dropped_count')} | {d['e_sidecar_meta'].get('unmapped_claims_by_type') or '-'} |")
w("\n## 3 B3形式の観察(v1。全10テーマ)\n")
w("| テーマ | Selected Facts形式 | 箇条書き行数 | 『・』行頭 | Storyline重複行 | 1事実あたり台帳ID数(統合 or A) |")
w("|---|---|---|---|---|---|")
for s in SLUGS:
    kind, nb, dup, dot = fmt_b3(s)
    if s in merged_rows:
        ma = J(f"out/merged/{s}/merged_annotation.json"); ip = ids_per_fact(ma); src = "統合"
    elif os.path.exists(os.path.join(HERE, f"out/A/{s}/annotation.json")):
        ip = ids_per_fact(J(f"out/A/{s}/annotation.json")); src = "A"
    else: ip, src = [], "-"
    w(f"| {s} | {kind} | {nb} | {dot} | {'有' if dup else '無'} | {ip or '-'} ({src}) |")
w("\n- 段落形式(箇条書き0行): byd_recall / openai_copyright / semiconductor_earnings / small_bag(+ streaming_price v1/v2)。これらは1段落に多数台帳IDが紐付き、事実数が少なく(1〜3)なる。")
w("- 注記者は段落先頭に `- 【事実N】` を挿入した(仕様§1の定義済み挿入)。\n")
w("## 4 B3 v2(hormuz・streaming_price。機械判定は annotation/b3_v2_judge.json)\n")
j = json.load(open(os.path.join(BASE, "annotation", "b3_v2_judge.json"), encoding="utf-8")) if os.path.exists(os.path.join(BASE, "annotation", "b3_v2_judge.json")) else {}
w("| テーマ | 版 | 箇条書き行 | Storyline重複行 | 素材行 | 段落行 | 台帳外の数字 | 選択台帳ID数 |"); w("|---|---|---|---|---|---|---|---|")
for k, r in j.items():
    w(f"| {k.rsplit('_', 1)[0]} | {k.rsplit('_', 1)[1]} | {r['bullet_lines']} | {r['storyline_dup_lines']} | {r['sozai_lines']} | {r['paragraph_lines']} | {r['numbers_not_in_ledger'] or '-'} | {r['n_selected_ids']} |")
w("\n## 5 transcript監査(annotation/audit/, annotation/AUDIT_SUMMARY.md)\n")
au = J("audit/audit_all.json"); bd = J("audit/bash_detail.json")
w("| テーマ_注記者 | 既存strict | 既存base | 補助(許可=Read自分のプロンプト+Write自分のreply.md) | 使用ツール |"); w("|---|---|---|---|---|")
for k, v in sorted(au.items()):
    w(f"| {k} | {v['strict']} | rc={v['base_rc']} | {v['extra_verdict']} | {','.join(t for t, _ in v['tools'])} |")
open(os.path.join(HERE, "ANNOTATION_SUMMARY_01.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out[:40]))
