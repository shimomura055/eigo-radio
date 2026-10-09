# -*- coding: utf-8 -*-
"""casebank_01.json -> CASEBANK_01.md (表示用)。API呼び出しなし。"""
import json, collections, os, sys
sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(D, "casebank_01.json"), encoding="utf-8"))
C = d["cases"]
cnt = collections.Counter


def t(s, n=70):
    s = (s or "").replace("\n", " ").replace("|", "/")
    return s if len(s) <= n else s[:n] + "…"


pos = [c for c in C if c["label"] == "重大"]
neg = [c for c in C if c["label"] == "非重大"]
n_hum = sum(1 for c in pos if c["label_basis"] == "ユーザー確認")
o = []
o.append("# CASEBANK_01: Risk Flagger評価用ケースバンク(WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01A、API¥0)\n")
o.append("全ての文・台帳・ラベルは過去成果物からの逐語抽出で、新規生成はない。ラベルは過去成果物の記録に従い、本書では再判定していない。機械可読の正本は `casebank_01.json`(生成: `build_casebank_01.py` → `render_casebank_md_01.py`)。\n")
o.append("## 1. 件数\n")
o.append(f"- 実記事由来ケース: {len(C)}件(重大 {len(pos)} / 非重大 {len(neg)})。別枠で合成参考セット {len(d['synthetic_reference'])}件(人工反転、KPI本体には入れない)。")
o.append("- 重大のラベル根拠区分: " + ", ".join(f"{k} {v}" for k, v in cnt(c['label_basis'] for c in pos).items()))
o.append("- 非重大のラベル根拠区分: " + ", ".join(f"{k} {v}" for k, v in cnt(c['label_basis'] for c in neg).items()))
o.append(f"- **人間確認済み重大: {n_hum}件**(ユーザー確認C: K01・K02・K03の3件 + ユーザー判断『C寄り、Bの余地あり』: K11の1件)。目標≥5件に**1件不足**(§7参照)。")
o.append("")
o.append("### 事故タイプ別(重大)\n")
o.append("| 事故タイプ | 件数 | 開発 | 保留 |\n|---|---|---|---|")
types = ["rollback方向反転", "主体対象入替", "否定反転", "数量時系列", "不在断定", "その他"]
for ty in types:
    l = [c for c in pos if c["accident_type"] == ty]
    o.append(f"| {ty} | {len(l)} | {sum(c['split']=='dev' for c in l)} | {sum(c['split']=='holdout' for c in l)} |")
o.append(f"| 合計 | {len(pos)} | {sum(c['split']=='dev' for c in pos)} | {sum(c['split']=='holdout' for c in pos)} |")
o.append("\n注: 『否定反転』は実記事由来の確定重大が0件(K02は不在断定を主、否定反転を副に分類)。否定反転・数量時系列・Rollbackの**タイプ別能力**は合成参考セット(14件、`synthetic_reference`)で別途測る。\n")
o.append("### 非重大\n")
o.append("| 区分 | 件数 |\n|---|---|")
for k, v in cnt(c['label_basis'] for c in neg).items():
    o.append(f"| {k} | {v} |")
o.append(f"| 合計 | {len(neg)}(開発 {sum(c['split']=='dev' for c in neg)} / 保留 {sum(c['split']=='holdout' for c in neg)}) |")
o.append("")
o.append("## 2. 開発セット / 保留セットの事前分割\n")
o.append(f"- 乱数seed: case_id生成 {d['split_info']['seed_case_id']} / 分割 {d['split_info']['seed_split']} / 機械抽出 {d['split_info']['seed_mech']}。")
o.append("- 規則: " + d["split_info"]["rule"])
o.append("- 分割は検出器開発の前に確定し、`casebank_01.json` の `split` に固定した(以後変更しない。変更が必要な場合は理由つきで新版を作り、保留セットのscoreを再利用しない)。")
o.append("- 保留セットは最終評価1回のみに使う。開発セットで検出器を調整し、保留セットでKPI 1〜4を確定する。\n")
o.append("## 3. 重大ケース一覧\n")
o.append("| case_id | 旧ID | 区分 | タイプ | 分割 | Fact | 対象文(先頭) | 文の所在 |\n|---|---|---|---|---|---|---|---|")
for c in sorted(pos, key=lambda c: (c["label_basis"] != "ユーザー確認", c["accident_type"])):
    o.append(f"| {c['case_id']} | {t(','.join(c['legacy_ids']),30)} | {c['label_basis']} | {c['accident_type']} | {c['split']} | {c['fact']['id']} | {t(c['sentence'],60)} | {t(c['sentence_locator'],70)} |")
o.append("\n## 4. 非重大ケース一覧\n")
o.append("| case_id | 旧ID | 区分 | 分割 | Fact | 対象文(先頭) | 文の所在 |\n|---|---|---|---|---|---|---|")
for c in sorted(neg, key=lambda c: (c["label_basis"], c["legacy_ids"][0])):
    o.append(f"| {c['case_id']} | {t(','.join(c['legacy_ids']),30)} | {c['label_basis']} | {c['split']} | {t(c['fact']['id'],20)} | {t(c['sentence'],60)} | {t(c['sentence_locator'],70)} |")
o.append("\n(全フィールド: 台帳Fact逐語・対象文・前後文・ラベル根拠・出典は `casebank_01.json` を参照。)\n")
o.append("## 5. 記事単位セット(1記事あたりFlag数・未知ケース有用性測定用)\n")
o.append("FACTLOCK-ASTRA-E2E-TRIAL-01 の新腕・旧腕。JA=`ja_writer/revision2.md`(R2最終)、EN Adv=`b1b/article.md`、EN Std=`a2/article.md`。ファイル無し=その腕でSTOP(未出荷)。sha256・文数・台帳Fact数・labels_merged所見は `casebank_01.json` の `articles`。\n")
o.append("| テーマ | 腕 | 台帳Fact数 | JA R2文数 | EN Adv文数 | EN Std文数 | labels_merged件数(重大/軽微/問題なし/所見なし/判断不能) |\n|---|---|---|---|---|---|---|")
for a in d["articles"]:
    f = a["files"]
    sv = a["label_sev_counts"]

    def g(k):
        return str(f[k]["n_sentences"]) if f[k] else "-"
    o.append(f"| {a['theme']} | {a['arm']} | {a['n_facts']} | {g('JA_R2')} | {g('EN_Adv_b1b')} | {g('EN_Std_a2')} | {sv.get('重大',0)}/{sv.get('軽微',0)}/{sv.get('問題なし',0)}/{sv.get('所見なし',0)}/{sv.get('判断不能',0)} |")
nj = sum(1 for a in d["articles"] if a["arm"] == "new" and a["files"]["JA_R2"])
ne = sum(1 for a in d["articles"] if a["arm"] == "new" and (a["files"]["EN_Adv_b1b"] or a["files"]["EN_Std_a2"]))
oj = sum(1 for a in d["articles"] if a["arm"] == "old" and a["files"]["JA_R2"])
oe = sum(1 for a in d["articles"] if a["arm"] == "old" and (a["files"]["EN_Adv_b1b"] or a["files"]["EN_Std_a2"]))
o.append(f"\n- 新腕: JA最終稿あり {nj}/9、EN最終あり {ne}/9(central_bank_mortgage はR0 STOPで記事なし、openai_copyright・semiconductor_earnings はEN STOP)。旧腕: JA {oj}/9、EN {oe}/9(hormuz・meta旧はSTOPで記事なし)。")
o.append("- 注: labels_merged に新腕の重大ラベルは0件、旧腕は2件(meta旧 w1-11・w1-14、同一箇所)。新腕記事でFlagが出ても『既知の重大ラベル』と照合できない箇所は、**未知ケース有用性の人間裁定**(DESIGN §4 KPI5)に回す。")
o.append("- 台帳Fact数の注: 各腕の `research_ledger/verified_fact_ledger.txt` の `[VERIFIED]` ブロック数。")
o.append("\n## 6. 合成参考セット(人工反転14件、KPI本体外)\n")
o.append("出典 `er052_output/open233_directional_misread_trial_01/testset_01.json`(決定論置換、Trial専用、Fable代理gold)。実記事に存在しない人工文であり、**実記事KPI(Recall・Flag精度)には含めない**。事故タイプ別の能力確認(特にRollback・否定反転・方向反転)と、検出器の最低限の動作確認にのみ使う。\n")
o.append("| syn_id | タイプ | 分割 | Fact | 文 |\n|---|---|---|---|---|")
for s in d["synthetic_reference"]:
    o.append(f"| {s['syn_id']} | {s['accident_type']} | {s['split']} | {s['fact_id']} | {t(s['sentence'],90)} |")
o.append("\n## 7. 未確認・不足・注意\n")
o.append("1. **人間確認済み重大が4件(目標5件に1件不足)**。K11は『C寄り、Bの余地あり』のため、確定重大としては3件(K01・K02・K03)。K01とK03は同一Fact・同型(Rollback)で独立性が低い(near_dup_group)。人間確認済みの独立サンプルは実質3系統(Rollback・不在断定・発表内容取り違え)。追加の人間確認候補: meta-p2r2-02(開示対象)、sw-p2r2-02(『初めて』の拡張)、hormuz-T0M0r2-01(20%の対象)、RC-K16(時期)、RC-K18/Safety-A2A3-0(支払義務者)。ユーザー確認が取れれば人間確認区分へ格上げできる。")
o.append("2. 重大の大半(10/17)はSonnet判定、3件はFable確定(Safety-critical gold、ユーザー承認の線引き基準の机上適用)で、ユーザー個別確認ではない。KPI1は『人間確認済みのみのRecall』と『全重大のRecall』を分けて出す。")
o.append("3. 『否定反転』の実記事由来の確定重大は0件。K02の『Nor has anyone reported…』は不在断定を主、否定反転を副としたが、分類は評価者によって割れうる。")
o.append("4. 非重大の『境界・軽微』は『重大/非重大』の2値指示により非重大側に置いた。K04/K06/K10(Sonnet暫定)・S0_USER_CHECK 3件(ユーザー回答待ち)・B-xx(Sonnet暫定、B-05は人間確認候補)は、ユーザーが重大と裁定した場合にラベルが反転する。")
o.append("5. 機械抽出の非重大は弱ラベル(文単位の人間確認なし。『記事内の数値が台帳の同一Factに含まれる』という条件のみ)。誤Flag率の分母としては使うが、確定ラベルとしては扱わない。Fact選択は数値トークン一致による機械選択で、別Factを選んでいる可能性がある。")
o.append("6. 文の所在を特定できなかった軽微項目: " + ", ".join(f"{u['tag']}({u['row_id']})" for u in d['unlocated_minor_items']) + "(R0 attempt等の途中稿の引用で、最終記事ファイルに存在しないため除外)。")
o.append("7. 前後文なし(`context`のbefore/after両方null)のケースがある。記事ファイルに当該文が単独で残っていない、または途中稿・要約単体のみ。Flagger入力の評価では『文単体+台帳』でも判定できる形にしておく。")
o.append("8. WRITER-EVAL由来(K01等)の旧case_idは `legacy_case_id`。本バンクの `case_id` は `rf_` 接頭辞。")
open(os.path.join(D, "CASEBANK_01.md"), "w", encoding="utf-8").write("\n".join(o) + "\n")
print("ok", len(o))
