# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_rewrite_compare_page_rep17_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, 委任_31 Part3)
# ============================================================
# 目的: 委任_31「読み比べページにneg1の『Rewriteなし』例を追加(既存版
# 保存)」に基づき、rep16版の既存3 instance(hormuz_run03_standard/
# neg1_meta_b3prod_a2[最小置換実例]/bgroup_B3)はそのまま維持しつつ、
# 新規セクションとして`neg1_meta_b3prod_a2`のrep17再実行結果
# (Hookセクション境界拡張[委任_31 Part1(b)]後の確認、Rewrite 0件)を
# 追加する。
#
# 正直な開示(捏造禁止): rep17のStage1(fresh、非決定性)は今回、Hook
# 導入文・Hook締め文("Meta had run a test that caused exactly this
# surprise.")・usersクレームのいずれもBLOCKING-candidateとして検出せず、
# 別のbody claim("A human can handle situations that AI alone finds
# difficult.")を検出してStage2 body rubric(V5)でQUALITYへdowngradeした
# (Rewrite 0件という結果自体はrep16時点から変わらない「no-rewrite」実例
# だが、Hook境界拡張の効果をこの特定のfull flow実行が直接再現したわけ
# ではない)。そのため、本ページには(1)rep17の実際のfull flow結果
# (Rewrite 0件)に加え、(2)実fixtureのarticle_text(捏造なし)に対し
# `detect_claim_section_type`/`_hook_paragraph_block`を直接呼んだ¥0
# 確認結果(Hook導入文・Hook締め文がともにsection_type="hook"へ分類され
# ることを実データで確認)を並べて正直に記載する。
#
# API呼び出しなし(¥0、既存rep17証跡json読み直し+ランタイムでの決定論
# 関数呼び出しのみ)。既存er052_open233_self_recovery_rewrite_compare_
# page_{01,iter5,iter6,iter7,rep16}_01.pyは変更しない。
from __future__ import annotations

import html as html_mod
import json
import os

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_rewrite_compare_page_iter7_01 as prev

OUT_PATH = "user_test/open233_rewrite_compare_01/index.html"
PREV_OUT_PATH = "user_test/open233_rewrite_compare_01/index_rep16.html"
REP16_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep16"
REP17_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep17"

# rep16版の既存3 instance(変更しない、そのまま再掲)
SELECTED_REP16 = list(
    __import__("er052_open233_self_recovery_rewrite_compare_page_rep16_01").SELECTED
)
for sel in SELECTED_REP16:
    sel["_dir"] = REP16_DIR

CHECKLIST_ITEMS = prev.CHECKLIST_ITEMS


def load_instance(dir_path: str, instance_id: str, sample: str) -> dict:
    path = f"{dir_path}/{sample}/{instance_id}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def render_instance_section(sel: dict) -> str:
    inst = load_instance(sel["_dir"], sel["instance_id"], sel["sample"])
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


def render_hook_boundary_section() -> str:
    """委任_31 Part1(b)是正の構造的な効果を、実fixtureのarticle_text
    (捏造なし)への¥0の決定論関数呼び出しで示す新規セクション。"""
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    full_text = insts["neg1_meta_b3prod_a2"]["fixture"]["article_text"]
    hook_intro = ("Ring, ring. A call seemed to come from an AI agent. But as the "
                  "conversation went on, the voice was not AI at all. It was a person.")
    hook_closing = "Meta had run a test that caused exactly this surprise."
    users_claim = ("The test began without clearly telling users that contract "
                   "workers would make the calls.")
    rows = [
        (hook_intro, runner.detect_claim_section_type(hook_intro, full_text)),
        (hook_closing, runner.detect_claim_section_type(hook_closing, full_text)),
        (users_claim, runner.detect_claim_section_type(users_claim, full_text)),
    ]
    parts = ['<h2>neg1_meta_b3prod_a2 &mdash; Hookセクション境界拡張の確認(委任_31 Part1(b)、実データ・¥0)</h2>']
    parts.append(
        '<div class="note">rep17のStage1(fresh、非決定性)は今回たまたまHook導入文・Hook締め文・'
        'usersクレームのいずれもBLOCKING-candidateとして検出しなかったため(下のセクションの'
        'rep17実行結果は別のclaimの結果)、Hook境界拡張の効果はfull flow上では直接再現しなかった。'
        'そこで、実fixtureのarticle_text(捏造なし)に対し<code>detect_claim_section_type</code>/'
        '<code>_hook_paragraph_block</code>を直接呼ぶ¥0の確認を別途行った。その結果、Hook導入文・'
        'Hook締め文の双方がsection_type=&quot;hook&quot;(Hook専用rubric、演出を許容)へ分類され、'
        'usersクレームはsection_type=&quot;body&quot;のまま(変化なし)であることを確認した。'
        '以前(委任_30以前)は、Hook締め文は段落①(Hook導入文)のみをHook候補とする旧実装により'
        '&quot;body&quot;に誤分類され、本文の厳格なrubricで判定されていた。</div>'
    )
    parts.append('<table class="metrics-table"><tr><th>claim</th><th>section_type(新実装)</th></tr>')
    for claim_text, section_type in rows:
        parts.append(f'<tr><td>{html_mod.escape(claim_text)}</td><td>{html_mod.escape(section_type)}</td></tr>')
    parts.append('</table>')
    return "\n".join(parts)


PAGE_HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-233 Self-Recovery Flow rep17 - Rewrite 修正前後比較</title>
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
<h1>OPEN-233 Self-Recovery Flow rep17 - Rewrite 修正前後比較</h1>
<div class="iter-link"><a href="index_rep16.html">rep16版のページはこちら(旧版、保存のまま残しています)</a>
/ <a href="index_iter7.html">iteration7版のページはこちら(旧版)</a></div>
<div class="top-note">
<p><strong>これは何か</strong>: Eigo Radioの記事生成パイプラインで、AIチェッカー
(Deviation Check)がLedger(検証済み事実台帳)と矛盾する・根拠のない具体的事実を
発明していると判定した文章を、AIが自動的に書き直した(Rewrite)実例です。
書き直し前(Before)と書き直し後(After)を並べて表示しています。</p>
<p>このページは、OPEN-233-SELF-RECOVERY-TRIAL-01(Self-Recovery Flow Trial)
委任_31(rep16の残3点の是正+rep17再確認)の実測結果からの抜粋です。
Production(本番)記事の生成経路には未接続のTrial実装であり、この結果を見て
ユーザーが「この自動修正の品質は妥当か」を確認するためのページです。rep16からの
変更点: (1)主体置換ガードをproblem_kindに関係なく常に評価するよう是正、(2)Hook
セクションの範囲を「冒頭段落全体(Hook導入文+締め文)」へ拡張、(3)body rubricへ
「受け手側の驚き・反応は新規Factではない」の防御層(V5)を追加。最後に新設した
セクションで、Hookセクション境界拡張の効果を実データで確認した結果を示す
(「Rewriteなし」例)。</p>
</div>
"""

PAGE_FOOTER = """
<footer>
生成元: er052_open233_self_recovery_rewrite_compare_page_rep17_01.py (API呼び出し
なし、既存rep16/rep17証跡json[er052_output/open233_self_recovery_flow_runner_01_
rep16(rep17)/]の読み直し+決定論関数の直接呼び出しのみ)。管理ID:
OPEN-233-SELF-RECOVERY-TRIAL-01(委任_31)。
</footer>
</body>
</html>
"""


def main():
    sections = [render_instance_section(sel) for sel in SELECTED_REP16]
    # rep17の実行結果(neg1、Rewrite 0件)を新規セクションとして追加する。
    sections.append(render_instance_section({
        "instance_id": "neg1_meta_b3prod_a2", "sample": "instances_s1",
        "group_label": "negative候補7(Meta Muse記事、rep17再実行、Rewrite 0件)",
        "level": "Standard", "_dir": REP17_DIR,
        "note": "委任_31の3点の是正(actorガード常時評価・Hook境界拡張・body rubric V5)"
                "反映後のStage1 fresh再実行。今回はStage1が別のbody claim"
                "(“A human can handle situations that AI alone finds difficult.”、"
                "related_fact_id=MUSE-HC-008)を検出し、body rubric(V5)でQUALITYへ"
                "downgradeした(Rewrite 0件、final_state=RESOLVED_STAGE2_DOWNGRADE、"
                "sample1・sample2とも同一結果)。Hook導入文・Hook締め文・usersクレームは"
                "今回Stage1が検出しなかったため、この特定の実行はHook境界拡張の効果を"
                "直接は再現していない(下のセクションで実データによる直接確認を別途示す)。",
    }))
    sections.append(render_hook_boundary_section())
    page = PAGE_HEADER + "\n".join(sections) + PAGE_FOOTER
    os.makedirs("user_test/open233_rewrite_compare_01", exist_ok=True)
    # rep16版を保存してからrep17版で上書きする(移動・削除禁止の既存運用どおり)。
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
