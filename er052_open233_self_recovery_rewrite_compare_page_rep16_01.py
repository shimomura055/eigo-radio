# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_rewrite_compare_page_rep16_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, 委任_30 Part4)
# ============================================================
# 目的: 委任_30 Part4「読み比べページをrep16の結果で更新する」に基づき、
# er052_output/open233_self_recovery_flow_runner_01_rep16/instances_s1(s2)/*.json
# から3 instance(hormuz_run03_standard[Rewriteなし実例]/
# neg1_meta_b3prod_a2[最小置換実例]/bgroup_B3[接続詞修正実例])を選び、
# 修正前後を段落対応で並べたページを生成する。重大誤解原則(Stage1 V4A・
# Stage2 body V4・Hook V4)をrunner既定経路へ実配線した後の実記事代表
# ケースの実例として提示する。
#
# 既存er052_open233_self_recovery_rewrite_compare_page_01.py(iter4版)/
# _iter5_01.py(iter5版)/_iter6_01.py(iter6版)/_iter7_01.py(iter7版)は
# 変更しない。API呼び出しなし(¥0、既存rep16証跡jsonの読み直しのみ)。
from __future__ import annotations

import os

import er052_open233_self_recovery_rewrite_compare_page_iter7_01 as prev

OUT_PATH = "user_test/open233_rewrite_compare_01/index.html"
PREV_OUT_PATH = "user_test/open233_rewrite_compare_01/index_iter7.html"
REP16_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep16"

SELECTED = [
    {
        "instance_id": "hormuz_run03_standard", "sample": "instances_s1",
        "group_label": "Hormuz実記事(Standard、重大誤解原則V4によるRewriteなし実例)",
        "level": "Standard",
        "note": "重大誤解原則(Stage1 V4A・Stage2 body V4)をrunner既定経路へ実配線した後の"
                "再実行(委任_30)。「Brent futures→oil prices」「Brent crude futures→crude "
                "prices」のような、同じ対象をより一般的な言い方へ置き換えるだけの表現は"
                "許容候補として明記されており(design書§0-2)、本instanceではStage2自体が"
                "全claimを非BLOCKING(QUALITY/ACCEPTABLE)と判定し、Rewrite自体が一度も"
                "発生しなかった(final_state=RESOLVED_STAGE2_DOWNGRADE、ladder使用0件)。"
                "sample1・sample2とも同一結果で再現性を確認した。",
    },
    {
        "instance_id": "neg1_meta_b3prod_a2", "sample": "instances_s1",
        "group_label": "negative候補7(Meta Muse記事、最小置換実例)",
        "level": "Standard",
        "note": "Hook claim(“Ring, ring...”)・users claim(“The test began without clearly "
                "telling users...”)はいずれも非BLOCKING(委任_30 Part1のHook V4・委任_29の"
                "重大誤解原則配線により、境界群・社内テスト誤読の双方が解消済み)のまま"
                "Rewrite対象にならなかった。一方、別の1 body claim(“Meta had run a test that "
                "caused exactly this surprise.”)がBLOCKING判定され、①単語・接続詞水準のみ"
                "(ladder_level_used=1_word_connective)の最小置換(「that caused exactly this "
                "surprise」を削除)で解消した。段落・全文Rewriteは発生していない。",
    },
    {
        "instance_id": "bgroup_B3", "sample": "instances_s1",
        "group_label": "B群(Safety-critical、因果の接続詞修正実例)",
        "level": "B3 fixture",
        "note": "Safety-critical claim(因果の“so”、Ledgerでは単なる時期の一致であり因果関係は"
                "確認されていない)が、重大誤解原則V4配線後も引き続きBLOCKINGとして正しく"
                "検出され(誤降格なし、final_state=RESOLVED_REWRITE)、①単語・接続詞水準のみ"
                "(ladder_level_used=1_word_connective)で\"so\"→\"while\"への1語修正により"
                "解消した。段落・全文Rewriteは発生していない。sample1・sample2とも同一結果。",
    },
]

CHECKLIST_ITEMS = prev.CHECKLIST_ITEMS


def load_instance(instance_id: str, sample: str) -> dict:
    path = f"{REP16_DIR}/{sample}/{instance_id}.json"
    import json
    with open(path, encoding="utf-8") as f:
        return json.load(f)


PAGE_HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-233 Self-Recovery Flow rep16 - Rewrite 修正前後比較</title>
<style>
body { font-family: -apple-system, "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
       max-width: 1100px; margin: 0 auto; padding: 24px; line-height: 1.6; color: #222; }
h1 { font-size: 1.5em; }
h2 { margin-top: 2.5em; border-bottom: 3px solid #444; padding-bottom: 4px; }
.meta { color: #555; font-size: 0.92em; margin-bottom: 1em; }
.note { background: #f4f4f4; border-left: 4px solid #888; padding: 8px 12px; margin: 12px 0; }
table.diff-table { width: 100%; border-collapse: collapse; margin: 12px 0 24px 0; font-size: 0.92em; }
table.diff-table th, table.diff-table td { border: 1px solid #ccc; padding: 8px; vertical-align: top; width: 50%; }
table.diff-table th { background: #333; color: #fff; }
tr.diff-equal td { background: #fff; color: #666; }
tr.diff-replace td { background: #fff3cd; }
tr.diff-delete td { background: #f8d7da; }
tr.diff-insert td { background: #d4edda; }
.claims-box { background: #eef3fb; border: 1px solid #b6c9e3; padding: 10px 14px; margin: 10px 0; border-radius: 4px; }
.claims-box .claim { margin-bottom: 10px; }
.claims-box .label { font-weight: bold; }
.metrics-table { border-collapse: collapse; margin: 8px 0 16px 0; font-size: 0.9em; }
.metrics-table td, .metrics-table th { border: 1px solid #ccc; padding: 4px 10px; }
.checklist label { display: block; margin: 4px 0; }
.checklist input { margin-right: 8px; }
.top-note { background: #fff8e1; border: 1px solid #e0c46c; padding: 12px 16px; margin-bottom: 24px; }
.iter-link { background: #eef; border: 1px solid #99c; padding: 8px 12px; margin-bottom: 12px; }
footer { margin-top: 3em; color: #888; font-size: 0.85em; }
</style>
</head>
<body>
<h1>OPEN-233 Self-Recovery Flow rep16 - Rewrite 修正前後比較</h1>
<div class="iter-link"><a href="index_iter7.html">iteration7版のページはこちら(旧版、保存のまま残しています)</a>
/ <a href="index_iter6.html">iteration6版のページはこちら(旧版)</a>
/ <a href="index_iter5.html">iteration5版のページはこちら(旧版)</a>
/ <a href="index_iter4.html">iteration4版のページはこちら(旧版)</a></div>
<div class="top-note">
<p><strong>これは何か</strong>: Eigo Radioの記事生成パイプラインで、AIチェッカー
(Deviation Check)がLedger(検証済み事実台帳)と矛盾する・根拠のない具体的事実を
発明していると判定した文章を、AIが自動的に書き直した(Rewrite)実例です。
書き直し前(Before)と書き直し後(After)を並べて表示しています。</p>
<p>このページは、OPEN-233-SELF-RECOVERY-TRIAL-01(Self-Recovery Flow Trial)
委任_30(rep16、実記事代表5ケースのうち3ケースを抜粋)の実測結果からの抜粋です。
Production(本番)記事の生成経路には未接続のTrial実装であり、この結果を見て
ユーザーが「この自動修正の品質は妥当か」を確認するためのページです。iteration7
からの変更点: 重大誤解原則(Stage1 V4A・Stage2 body V4・Hook V4、確認済みの
Factから自然に導ける一般化・演出は許容し、主要な意味・主体・方向・規模・時間軸を
誤認させる場合のみBLOCKINGとする原則)をrunner既定経路へ実配線した後の再測定
であり、(1)Hormuz記事はRewrite自体が発生しない(許容)実例、(2)(3)はいずれも
①単語・接続詞水準のみの最小置換で解消し、段落・全文Rewriteは発生していないことを
示す。</p>
</div>
"""

PAGE_FOOTER = """
<footer>
生成元: er052_open233_self_recovery_rewrite_compare_page_rep16_01.py (API呼び出し
なし、既存rep16証跡json[er052_output/open233_self_recovery_flow_runner_01_
rep16/]の読み直しのみ)。管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_30)。
</footer>
</body>
</html>
"""


def render_instance_section(sel: dict) -> str:
    inst = load_instance(sel["instance_id"], sel["sample"])
    claims = prev.collect_blocking_claims(inst)
    ladder = prev.collect_rewrite_ladder(inst)
    before, after = prev.before_after_text(inst)
    import html as html_mod
    parts = [f'<h2>{html_mod.escape(sel["instance_id"])} ({html_mod.escape(sel["sample"])}) '
             f'&mdash; {html_mod.escape(sel["group_label"])}</h2>']
    parts.append(f'<div class="meta">レベル: {html_mod.escape(sel["level"])} / '
                  f'最終状態: {html_mod.escape(inst["final_state"])} / '
                  f'総コスト: ¥{inst["total_cost_jpy"]} / 総call数: {inst["total_calls"]}</div>')
    parts.append(f'<div class="note">{html_mod.escape(sel["note"])}</div>')

    parts.append('<div class="claims-box"><div class="label">BLOCKINGと判定されたclaim '
                  f'({len(claims)}件)と修正方針</div>')
    for c in claims:
        parts.append(
            '<div class="claim">'
            f'<div>cycle{c["cycle"]} / basis={html_mod.escape(str(c["basis"]))} / '
            f'rewrite_kind={html_mod.escape(str(c["rewrite_kind"]))} / '
            f'section_type={html_mod.escape(str(c.get("section_type")))}'
            f'{" / floor=" + html_mod.escape(str(c["floor_reason"])) if c["floor_reason"] else ""}'
            f'{" / floor_cited=" + html_mod.escape(str(c["floor_cited_reason"])) if c.get("floor_cited_reason") else " / floor_cited=なし"}'
            '</div>'
            f'<div>対象claim: 「{html_mod.escape(c["claim_text"])}」</div>'
            f'<div>修正方針(rewrite_hint): {html_mod.escape(c["rewrite_hint"])}</div>'
            '</div>'
        )
    if not claims:
        parts.append('<div class="claim">(このcycleでBLOCKING claimは検出されませんでした。'
                      'Rewriteは発生していません。)</div>')
    parts.append('</div>')

    if ladder:
        parts.append('<div class="note"><strong>最小変更ラダーの停止水準</strong>: '
                      + html_mod.escape(" / ".join(
                          f'cycle{l["cycle"]}:{l["ladder_level_used"]}({l["mechanism"]})' for l in ladder))
                      + '</div>')

    if before and after:
        m = prev.quality_metrics(before, after)
        parts.append('<table class="metrics-table"><tr><th></th><th>Before</th><th>After</th></tr>'
                      f'<tr><td>文数</td><td>{m["sentence_before"]}</td><td>{m["sentence_after"]}</td></tr>'
                      f'<tr><td>段落数</td><td>{m["paragraph_before"]}</td><td>{m["paragraph_after"]}</td></tr>'
                      f'<tr><td>弱め表現(may/might/possibly等)数</td>'
                      f'<td>{m["hedge_before"]}</td><td>{m["hedge_after"]}</td></tr></table>')
        parts.append(prev.paragraph_diff_html(before, after))
    else:
        parts.append('<p>(この instance には保存済みのRewrite前後全文が無い、または'
                      '前後で変化がなかったため、差分表示を省略します。Rewrite自体が'
                      '発生しなかった[Rewriteなし]ことを示す実例です。)</p>')

    parts.append('<div class="checklist"><div class="label">観点チェックリスト(確認用)</div>')
    for item in CHECKLIST_ITEMS:
        parts.append(f'<label><input type="checkbox" disabled> {html_mod.escape(item)}</label>')
    parts.append('</div>')
    return "\n".join(parts)


def main():
    sections = [render_instance_section(sel) for sel in SELECTED]
    page = PAGE_HEADER + "\n".join(sections) + PAGE_FOOTER
    os.makedirs("user_test/open233_rewrite_compare_01", exist_ok=True)
    # iteration7版を保存してからrep16版で上書きする(移動・削除禁止の既存運用どおり、
    # iter4〜7版と同じパターン)。
    if os.path.exists(OUT_PATH) and not os.path.exists(PREV_OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as f:
            prev_content = f.read()
        with open(PREV_OUT_PATH, "w", encoding="utf-8") as f:
            f.write(prev_content)
        print(f"saved previous version to {PREV_OUT_PATH}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT_PATH}, {len(page)} chars")


if __name__ == "__main__":
    main()
