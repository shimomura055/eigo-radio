# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_rewrite_compare_page_iter5_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, iteration5、委任_13 作業E)
# ============================================================
# 目的: 委任_13作業E「読み比べページをiteration5の結果で更新する(同じ3記事+
# 可能ならneg2を追加)。iteration4版はindex_iter4.htmlとして残す(移動・削除
# 禁止、新規保存)」に基づき、er052_output/open233_self_recovery_flow_runner_01_
# iter5/instances_s1/*.json (sample1)から4 instance
# (neg1_meta_b3prod_a2/hormuz_run02_advanced/bgroup_B3/neg2_meta_refresh_a2)
# を選び、修正前後を段落対応で並べたページを生成する。
#
# 既存er052_open233_self_recovery_rewrite_compare_page_01.py(iter4版)は
# 変更しない(そちらはINSTANCES_DIR=iter4/instancesを参照したまま)。
# API呼び出しなし(¥0、既存iter5証跡jsonの読み直しのみ)。
from __future__ import annotations

import difflib
import html
import json
import os
import re

INSTANCES_DIR = "er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1"
OUT_PATH = "user_test/open233_rewrite_compare_01/index.html"

SELECTED = [
    {
        "instance_id": "neg1_meta_b3prod_a2", "group_label": "negative候補7(正常記事、Standardレベル)",
        "level": "Standard",
        "note": "本来はACCEPTABLEが期待される正常記事(§7-5 Normal群)。iteration4ではhook/タイトルが"
                "消え、cycle2で重複段落まで発生した実例。iteration5はR3''+品質劣化検出v2+Rewrite品質"
                "制約(hook保持・削除優先・重複禁止)を反映した後の同一instanceの結果。",
    },
    {
        "instance_id": "hormuz_run02_advanced", "group_label": "実run(現行Production STOP実例、Advancedレベル)",
        "level": "Advanced",
        "note": "現行Productionで実際にJA_RECHECK_REQUIRED STOPとなった記事そのもの。"
                "iteration4でRewrite解消に成功し、iteration5(n=2のsample1)でも再現するかを確認する。",
    },
    {
        "instance_id": "bgroup_B3", "group_label": "B群(claim単位に正解ラベルが混在するfixture、政策決定理由の取り違え)",
        "level": "B3 fixture",
        "note": "Ledger conditionsが「中東指導者との協議に基づく決定」と明記するのに、記事が「懸念継続"
                "so撤回」と逆方向の因果を述べていた、genuine BLOCKING(§7-0-iter5でも変更なしを維持)。",
    },
    {
        "instance_id": "neg2_meta_refresh_a2", "group_label": "negative候補7(正常記事、Standardレベル、iteration5追加)",
        "level": "Standard",
        "note": "iteration4ではRewrite後もSTAGE4(unconfirmed_after_reverify)に至った実例(neg2)。"
                "iteration5のR3''(内心の断定を開示・認識の有無へ限定)+cite-or-release"
                "(remaining_sentence必須化)でどう変わったかを確認する。",
    },
]

_HEDGE_WORD_RE = re.compile(r"\b(may|might|possibly|perhaps|could|seem(?:s|ed)?|appear(?:s|ed)?)\b", re.IGNORECASE)


def load_instance(instance_id: str) -> dict:
    with open(f"{INSTANCES_DIR}/{instance_id}.json", encoding="utf-8") as f:
        return json.load(f)


def collect_blocking_claims(inst: dict) -> list:
    out = []
    for ci, c in enumerate(inst["cycles"], start=1):
        for sr in c.get("stage2_results", []):
            if sr["materiality"] == "BLOCKING":
                out.append({
                    "cycle": ci, "claim_text": sr["claim_text"], "basis": sr.get("basis"),
                    "rewrite_kind": sr.get("rewrite_kind"), "rewrite_hint": sr.get("rewrite_hint", ""),
                    "floor_reason": sr.get("floor_reason"),
                })
    return out


def before_after_text(inst: dict) -> tuple:
    cycles = inst["cycles"]
    before = None
    after = None
    for c in cycles:
        if "en_text_before_rewrite" in c and before is None:
            before = c["en_text_before_rewrite"]
        if "en_text_after_rewrite" in c:
            after = c["en_text_after_rewrite"]
    return before, after


def paragraph_diff_html(before: str, after: str) -> str:
    before_paras = [p for p in before.split("\n\n") if p.strip()]
    after_paras = [p for p in after.split("\n\n") if p.strip()]
    sm = difflib.SequenceMatcher(a=before_paras, b=after_paras)
    rows = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for bp, ap in zip(before_paras[i1:i2], after_paras[j1:j2]):
                rows.append(("equal", bp, ap))
        elif tag == "replace":
            b_block = "\n\n".join(before_paras[i1:i2])
            a_block = "\n\n".join(after_paras[j1:j2])
            rows.append(("replace", b_block, a_block))
        elif tag == "delete":
            rows.append(("delete", "\n\n".join(before_paras[i1:i2]), ""))
        elif tag == "insert":
            rows.append(("insert", "", "\n\n".join(after_paras[j1:j2])))

    out = ['<table class="diff-table"><thead><tr><th>Before(Rewrite前)</th>'
           '<th>After(Rewrite後)</th></tr></thead><tbody>']
    for tag, b, a in rows:
        cls = {"equal": "diff-equal", "replace": "diff-replace",
               "delete": "diff-delete", "insert": "diff-insert"}[tag]
        out.append(
            f'<tr class="{cls}"><td>{html.escape(b).replace(chr(10), "<br>")}</td>'
            f'<td>{html.escape(a).replace(chr(10), "<br>")}</td></tr>'
        )
    out.append("</tbody></table>")
    return "\n".join(out)


def quality_metrics(before: str, after: str) -> dict:
    def sc(t):
        return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s.strip()])

    def pc(t):
        return len([p for p in t.split("\n\n") if p.strip()])

    hedge_b = len(_HEDGE_WORD_RE.findall(before))
    hedge_a = len(_HEDGE_WORD_RE.findall(after))
    return {
        "sentence_before": sc(before), "sentence_after": sc(after),
        "paragraph_before": pc(before), "paragraph_after": pc(after),
        "hedge_before": hedge_b, "hedge_after": hedge_a,
    }


CHECKLIST_ITEMS = [
    "読みやすさ(Before比でAfterが読みにくくなっていないか)",
    "面白さ(ストーリーの面白さが損なわれていないか)",
    "ストーリー性(前後の文脈・流れが不自然に途切れていないか)",
    "不自然な弱め表現(may/might/possibly等が不自然に増えていないか)",
    "Rewriteによる品質劣化(文が唐突に短く/曖昧になっていないか、重複段落・孤立逆接語がないか)",
    "Fact上の問題解消(BLOCKINGと判定された問題が実際に解消されているか)",
]

PAGE_HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-233 Self-Recovery Flow iteration5 - Rewrite 修正前後比較</title>
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
<h1>OPEN-233 Self-Recovery Flow iteration5 - Rewrite 修正前後比較</h1>
<div class="iter-link"><a href="index_iter4.html">iteration4版のページはこちら(旧版、保存のまま残しています)</a></div>
<div class="top-note">
<p><strong>これは何か</strong>: Eigo Radioの記事生成パイプラインで、AIチェッカー
(Deviation Check)がLedger(検証済み事実台帳)と矛盾する・根拠のない具体的事実を
発明していると判定した文章を、AIが自動的に書き直した(Rewrite)実例です。
書き直し前(Before)と書き直し後(After)を並べて表示しています。</p>
<p>このページは、OPEN-233-SELF-RECOVERY-TRIAL-01(Self-Recovery Flow Trial)
iteration5(委任_13、n=2実行のsample1)の実測結果からの抜粋です。Production
(本番)記事の生成経路には未接続のTrial実装であり、この結果を見てユーザーが
「この自動修正の品質は妥当か」を確認するためのページです。iteration4からの
変更点: Stage2 rubric R3''(較正で改善確認)・Stage2の2-of-2安定化・
確認callのcite-or-release・品質劣化検出v2(重複段落・孤立逆接語・語彙難化を
新規検出)・Rewrite品質制約(hook保持・削除優先・重複禁止をprompt側へ追加)。</p>
</div>
"""

PAGE_FOOTER = """
<footer>
生成元: er052_open233_self_recovery_rewrite_compare_page_iter5_01.py (API呼び出し
なし、既存iteration5証跡json[er052_output/open233_self_recovery_flow_runner_01_
iter5/instances_s1/]の読み直しのみ)。管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
(委任_13)。
</footer>
</body>
</html>
"""


def render_instance_section(sel: dict) -> str:
    inst = load_instance(sel["instance_id"])
    claims = collect_blocking_claims(inst)
    before, after = before_after_text(inst)
    parts = [f'<h2>{html.escape(sel["instance_id"])} &mdash; {html.escape(sel["group_label"])}</h2>']
    parts.append(f'<div class="meta">レベル: {html.escape(sel["level"])} / '
                  f'最終状態: {html.escape(inst["final_state"])} / '
                  f'総コスト: ¥{inst["total_cost_jpy"]} / 総call数: {inst["total_calls"]}</div>')
    parts.append(f'<div class="note">{html.escape(sel["note"])}</div>')

    parts.append('<div class="claims-box"><div class="label">BLOCKINGと判定されたclaim '
                  f'({len(claims)}件)と修正方針</div>')
    for c in claims:
        parts.append(
            '<div class="claim">'
            f'<div>cycle{c["cycle"]} / basis={html.escape(str(c["basis"]))} / '
            f'rewrite_kind={html.escape(str(c["rewrite_kind"]))}'
            f'{" / floor=" + html.escape(str(c["floor_reason"])) if c["floor_reason"] else ""}</div>'
            f'<div>対象claim: 「{html.escape(c["claim_text"])}」</div>'
            f'<div>修正方針(rewrite_hint): {html.escape(c["rewrite_hint"])}</div>'
            '</div>'
        )
    parts.append('</div>')

    # 委任_13(iteration5): 品質劣化検出v2の結果があれば併記する。
    qd_v2_notes = []
    for ci, c in enumerate(inst["cycles"], start=1):
        qd = c.get("quality_degradation_v2")
        if qd and (qd.get("duplicate_paragraph_detected") or qd.get("orphan_contrastive_detected")
                   or qd.get("vocab_difficulty_increased")):
            qd_v2_notes.append(f'cycle{ci}: {qd.get("reasons")} '
                                f'(再生成実施={c.get("quality_degradation_v2_regenerated")})')
    if qd_v2_notes:
        parts.append('<div class="note"><strong>品質劣化検出v2の所見</strong>: '
                      + html.escape(" / ".join(qd_v2_notes)) + '</div>')

    if before and after:
        m = quality_metrics(before, after)
        parts.append('<table class="metrics-table"><tr><th></th><th>Before</th><th>After</th></tr>'
                      f'<tr><td>文数</td><td>{m["sentence_before"]}</td><td>{m["sentence_after"]}</td></tr>'
                      f'<tr><td>段落数</td><td>{m["paragraph_before"]}</td><td>{m["paragraph_after"]}</td></tr>'
                      f'<tr><td>弱め表現(may/might/possibly等)数</td>'
                      f'<td>{m["hedge_before"]}</td><td>{m["hedge_after"]}</td></tr></table>')
        parts.append(paragraph_diff_html(before, after))
    else:
        parts.append('<p>(この instance には保存済みのRewrite前後全文が無い、または'
                      '前後で変化がなかったため、差分表示を省略します。)</p>')

    parts.append('<div class="checklist"><div class="label">観点チェックリスト(確認用)</div>')
    for i, item in enumerate(CHECKLIST_ITEMS):
        parts.append(f'<label><input type="checkbox" disabled> {html.escape(item)}</label>')
    parts.append('</div>')
    return "\n".join(parts)


def main():
    sections = [render_instance_section(sel) for sel in SELECTED]
    page = PAGE_HEADER + "\n".join(sections) + PAGE_FOOTER
    os.makedirs("user_test/open233_rewrite_compare_01", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT_PATH}, {len(page)} chars")


if __name__ == "__main__":
    main()
