# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_rewrite_compare_page_iter8_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, 委任_32)
# ============================================================
# 目的: 委任_32(広いTrial iteration8)の実測結果から3 instanceを選び、
# 読み比べページを更新する。(1)hormuz_run03_standard[実記事、Rewiteなし
# 実例、既知のハードケースが今回解消]、(2)neg3_hormuz_prodrunner_b1b
# [最小修正実例、①水準のみ]、(3)safety_er009_changed_actor[Safety
# fixtureの正当BLOCK実例]。
#
# 正直な開示: 本委任ではbgroup_B3/safety_A2A3(A2A3-0)でSafety-critical
# claimの誤降格を検出したため(REPORT§30-3C)、bgroup_B3は「正当BLOCK
# 実例」としては使わず、safety_er009_changed_actor(誤降格が起きて
# いない、既存floor機構が正しく機能した実例)を代わりに採用する。
#
# API呼び出しなし(¥0、既存iter8証跡json読み直しのみ)。既存
# er052_open233_self_recovery_rewrite_compare_page_{01,iter5,iter6,
# iter7,rep16,rep17}_01.pyは変更しない。
from __future__ import annotations

import os

import er052_open233_self_recovery_rewrite_compare_page_iter7_01 as prev

OUT_PATH = "user_test/open233_rewrite_compare_01/index.html"
PREV_OUT_PATH = "user_test/open233_rewrite_compare_01/index_rep17.html"
ITER8_DIR = "er052_output/open233_self_recovery_flow_runner_01_iter8"

SELECTED = [
    {
        "instance_id": "hormuz_run03_standard", "sample": "instances_s1",
        "group_label": "Hormuz実記事(Standard、既知のハードケースが今回解消したRewriteなし実例)",
        "level": "Standard",
        "_dir": ITER8_DIR,
        "note": "広いTrial iteration8(委任_32)でStage1 freshにより再実行。過去(iteration7、"
                "委任_22)はこのinstanceがn=2の両方でSTAGE4(人間確認)に到達していたが、今回は"
                "n=2の両方でStage2自体が全claimを非BLOCKING(QUALITY/ACCEPTABLE)と判定し、"
                "Rewrite自体が一度も発生しなかった(final_state=RESOLVED_STAGE2_DOWNGRADE、"
                "ladder使用0件)。「Brent futures→oil prices」型の一般化を許容する上位原則"
                "(design書§0-2)の効果が、full flow上で初めて確認できた実例。",
    },
    {
        "instance_id": "neg3_hormuz_prodrunner_b1b", "sample": "instances_s2",
        "group_label": "negative候補7(Hormuz関連記事、最小修正実例)",
        "level": "Standard",
        "_dir": ITER8_DIR,
        "note": "`changed_time`floor該当claim(継続していた出来事が一度消えて戻ったかのような"
                "時間表現の変化)が3件検出されたが、いずれも①単語・接続詞水準のみ"
                "(ladder_level_used=1_word_connective)の最小編集で解消した。段落・全文"
                "Rewriteは発生していない(sample1も同様の結果)。",
    },
    {
        "instance_id": "safety_er009_changed_actor", "sample": "instances_s1",
        "group_label": "Safety群(er009フラグ、正当BLOCK実例)",
        "level": "Safety fixture",
        "_dir": ITER8_DIR,
        "note": "記事が「A team at Harvard Business School(具体的な研究機関名)」という、Ledgerに"
                "ない具体的な主体を追加していたclaimが、deterministic safety floor"
                "(`changed_actor`)により無条件にBLOCKINGへ確定し(LLM判定を待たず)、①単語・"
                "接続詞水準のみ(ladder_level_used=1_word_connective)の最小編集(具体的な"
                "研究機関名の削除)で解消した。本委任で検出したB3/A2A3-0の誤降格(REPORT"
                "§30-3C)とは異なり、`changed_actor`はFLOOR_FLAGSに含まれるためdeterministic"
                "floorが正しく機能した例として対比のために掲載する。",
    },
]

CHECKLIST_ITEMS = prev.CHECKLIST_ITEMS


def render_safety_finding_section() -> str:
    """委任_32で新規検出したSafety-critical誤降格(B3/A2A3-0)を、実データ
    (捏造なし)のまま正直に提示する新規セクション。"""
    import html as html_mod
    import json as json_mod

    with open(f"{ITER8_DIR}/instances_s1/bgroup_B3.json", encoding="utf-8") as f:
        b3_s1 = json_mod.load(f)
    with open(f"{ITER8_DIR}/instances_s2/bgroup_B3.json", encoding="utf-8") as f:
        b3_s2 = json_mod.load(f)
    with open(f"{ITER8_DIR}/instances_s1/safety_A2A3.json", encoding="utf-8") as f:
        a2a3_s1 = json_mod.load(f)
    with open(f"{ITER8_DIR}/instances_s2/safety_A2A3.json", encoding="utf-8") as f:
        a2a3_s2 = json_mod.load(f)

    def materiality_of(inst: dict, needle: str) -> str:
        for c in inst.get("cycles", []):
            for sr in c.get("stage2_results", []):
                if needle in (sr.get("claim_text") or ""):
                    return sr.get("materiality")
        return "(not found)"

    b3_claim = "Concerns about US-Iran attacks"
    a2a3_claim = "those carrying the cargo would repay"

    parts = ['<h2>委任_32で新規検出したSafety-critical claim誤降格(B3/A2A3-0、REPORT§30-3C)</h2>']
    parts.append(
        '<div class="note"><strong>重要な開示</strong>: 本ページの他の実例(左記3件)は「正しく'
        '機能した例」だが、本委任では以下2件のSafety-critical claim(design書§7-0-iter32で'
        '正解BLOCKING確定済み)がStage2により誤ってQUALITYへ降格する事例を検出した。既存の'
        'false PASS自動検知(<code>silent_pass_candidate</code>)は常に0を返す非稼働コードで'
        'あり、以下はSAFETY_CRITICAL_SUB_IDSとの手動照合で検出したものである。採用可否・'
        '対応要否はFable/ユーザー判断待ち。</div>'
    )
    parts.append('<table class="metrics-table"><tr><th>claim</th><th>sample1</th><th>sample2</th></tr>')
    parts.append(
        f'<tr><td>B3(HF-007、因果)</td>'
        f'<td>{html_mod.escape(materiality_of(b3_s1, b3_claim))}</td>'
        f'<td>{html_mod.escape(materiality_of(b3_s2, b3_claim))}</td></tr>'
    )
    parts.append(
        f'<tr><td>A2A3-0(HF-003、未確認の支払主体)</td>'
        f'<td>{html_mod.escape(materiality_of(a2a3_s1, a2a3_claim))}</td>'
        f'<td>{html_mod.escape(materiality_of(a2a3_s2, a2a3_claim))}</td></tr>'
    )
    parts.append('</table>')
    parts.append('<p>正解ラベル: いずれもBLOCKING(design書§7-1/§7-4参照)。</p>')
    return "\n".join(parts)


PAGE_HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-233 Self-Recovery Flow iteration8 - Rewrite 修正前後比較</title>
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
<h1>OPEN-233 Self-Recovery Flow iteration8 - Rewrite 修正前後比較</h1>
<div class="iter-link"><a href="index_rep17.html">rep17版のページはこちら(旧版、保存のまま残しています)</a>
/ <a href="index_iter7.html">iteration7版のページはこちら(旧版)</a></div>
<div class="top-note">
<p><strong>これは何か</strong>: Eigo Radioの記事生成パイプラインで、AIチェッカー
(Deviation Check)がLedger(検証済み事実台帳)と矛盾する・根拠のない具体的事実を
発明していると判定した文章を、AIが自動的に書き直した(Rewrite)実例です。
書き直し前(Before)と書き直し後(After)を並べて表示しています。</p>
<p>このページは、OPEN-233-SELF-RECOVERY-TRIAL-01(Self-Recovery Flow Trial)
委任_32(広いTrial iteration8、29 instance全量・9 instanceはn=2)の実測結果
からの抜粋です。Production(本番)記事の生成経路には未接続のTrial実装であり、
この結果を見てユーザーが「この自動修正の品質は妥当か」を確認するためのページ
です。<strong>重要な開示</strong>: 本委任では、Safety-critical claim(B3/
A2A3-0)がStage2により誤ってQUALITYへ降格する事例を新規に検出した(末尾の
専用セクション参照)。上の3件は「正しく機能した実例」、末尾は「現在未解決の
問題点」であり、あわせて見ることで現状を正確に把握できるようにしている。</p>
</div>
"""

PAGE_FOOTER = """
<footer>
生成元: er052_open233_self_recovery_rewrite_compare_page_iter8_01.py (API呼び出し
なし、既存iteration8証跡json[er052_output/open233_self_recovery_flow_runner_01_
iter8/]の読み直しのみ)。管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_32)。
</footer>
</body>
</html>
"""


def main():
    sections = [render_section(sel) for sel in SELECTED]
    sections.append(render_safety_finding_section())
    page = PAGE_HEADER + "\n".join(sections) + PAGE_FOOTER
    os.makedirs("user_test/open233_rewrite_compare_01", exist_ok=True)
    if os.path.exists(OUT_PATH) and not os.path.exists(PREV_OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as f:
            prev_content = f.read()
        with open(PREV_OUT_PATH, "w", encoding="utf-8") as f:
            f.write(prev_content)
        print(f"saved previous version to {PREV_OUT_PATH}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT_PATH}, {len(page)} chars")


def render_section(sel: dict) -> str:
    import html as html_mod
    import json as json_mod

    with open(f"{sel['_dir']}/{sel['sample']}/{sel['instance_id']}.json", encoding="utf-8") as f:
        inst = json_mod.load(f)
    claims = prev.collect_blocking_claims(inst)
    ladder = prev.collect_rewrite_ladder(inst)
    before, after = prev.before_after_text(inst)
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


if __name__ == "__main__":
    main()
