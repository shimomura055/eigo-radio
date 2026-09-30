# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_rewrite_compare_page_iter6_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, iteration6、委任_14 作業E)
# ============================================================
# 目的: 委任_14作業E「読み比べページをiteration6の結果で更新する(Meta hook
# [neg1_meta_b3prod_a2]とB3[bgroup_B3]を必ず収録)。iteration5版は
# index_iter5.htmlとして残す(移動・削除禁止、新規保存)」に基づき、
# er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s1/*.json
# (sample1)から4 instance
# (neg1_meta_b3prod_a2/bgroup_B3/hormuz_run02_advanced/neg2_meta_refresh_a2)
# を選び、修正前後を段落対応で並べたページを生成する。
#
# 既存er052_open233_self_recovery_rewrite_compare_page_01.py(iter4版)/
# er052_open233_self_recovery_rewrite_compare_page_iter5_01.py(iter5版)は
# 変更しない。API呼び出しなし(¥0、既存iter6証跡jsonの読み直しのみ)。
from __future__ import annotations

import difflib
import html
import json
import os
import re

INSTANCES_DIR = "er052_output/open233_self_recovery_flow_runner_01_iter6/instances_s1"
OUT_PATH = "user_test/open233_rewrite_compare_01/index.html"
PREV_OUT_PATH = "user_test/open233_rewrite_compare_01/index_iter5.html"

SELECTED = [
    {
        "instance_id": "neg1_meta_b3prod_a2", "group_label": "negative候補7(正常記事、Standardレベル、Meta hook実例)",
        "level": "Standard",
        "note": "2026-09-30ユーザー新方針item2で「Rewrite不要だった可能性が高い」と指摘されたMeta hook実例"
                "(\"Ring, ring. A call seemed to come from an AI agent...\")。監査"
                "(docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md §A-1-3)の結論どおり、実際のflag"
                "(changed_fact/changed_certainty/unsupported_new_claim)はHook-aware緩和対象"
                "(changed_scope単独)の範囲外であり、本委任の実装ではBLOCKING判定・Rewrite実施は変わらない"
                "(iteration6でも継続してRewriteされている)。",
    },
    {
        "instance_id": "bgroup_B3", "group_label": "B群(政策決定理由の取り違え、2026-09-30ユーザー新方針item4のB3因果実例)",
        "level": "B3 fixture",
        "note": "Ledger conditionsが「中東指導者との協議に基づく決定」と明記するのに、記事が「懸念継続"
                "so撤回」と逆方向の因果を述べていた、genuine BLOCKING(§7-0-iter5で変更なしを維持)。"
                "ユーザー指示item4は「まずso→while/meanwhile相当の最小変更で解消を試す」だったが、"
                "本claimはJA→EN対訳ペア(origin=ja_source)のためpaired J-1経路(最小変更ラダー未適用、"
                "既知の限界)でRewriteされており、段落単位の書き換えのままとなっている(達成できなかった"
                "点として正直に報告)。",
    },
    {
        "instance_id": "hormuz_run02_advanced", "group_label": "実run(現行Production STOP実例、Advancedレベル)",
        "level": "Advanced",
        "note": "現行Productionで実際にJA_RECHECK_REQUIRED STOPとなった記事そのもの。iteration6でも"
                "Rewrite解消するかを確認する。",
    },
    {
        "instance_id": "neg2_meta_refresh_a2", "group_label": "negative候補7(正常記事、Standardレベル)",
        "level": "Standard",
        "note": "iteration4/5でRewrite後もSTAGE4(unconfirmed_after_reverify)に至ったことがある実例。"
                "iteration6(丸め許容・floor-cited・最小変更ラダー・セクション役割維持・Hook-aware統合)"
                "でどう変わったかを確認する。",
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
                    "floor_reason": sr.get("floor_reason"), "section_type": sr.get("section_type"),
                    "floor_cited_reason": sr.get("floor_cited_reason"),
                })
    return out


def collect_rewrite_ladder(inst: dict) -> list:
    out = []
    for ci, c in enumerate(inst["cycles"], start=1):
        for rr in c.get("rewrite_records", []):
            out.append({"cycle": ci, "ladder_level_used": rr.get("ladder_level_used"),
                         "mechanism": rr.get("mechanism"), "method": rr.get("method")})
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
    "Title/Hook/In one lineの役割維持(引きつける/演出/短い締めが保たれているか)",
    "不自然な弱め表現(may/might/possibly等が不自然に増えていないか)",
    "Rewriteによる品質劣化(文が唐突に短く/曖昧になっていないか、重複段落・孤立逆接語がないか)",
    "Fact上の問題解消(BLOCKINGと判定された問題が実際に解消されているか)",
    "最小変更か(単語・接続詞・1文で済む話を段落・全文まで書き換えていないか)",
]

PAGE_HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-233 Self-Recovery Flow iteration6 - Rewrite 修正前後比較</title>
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
<h1>OPEN-233 Self-Recovery Flow iteration6 - Rewrite 修正前後比較</h1>
<div class="iter-link"><a href="index_iter5.html">iteration5版のページはこちら(旧版、保存のまま残しています)</a>
/ <a href="index_iter4.html">iteration4版のページはこちら(旧版、保存のまま残しています)</a></div>
<div class="top-note">
<p><strong>これは何か</strong>: Eigo Radioの記事生成パイプラインで、AIチェッカー
(Deviation Check)がLedger(検証済み事実台帳)と矛盾する・根拠のない具体的事実を
発明していると判定した文章を、AIが自動的に書き直した(Rewrite)実例です。
書き直し前(Before)と書き直し後(After)を並べて表示しています。</p>
<p>このページは、OPEN-233-SELF-RECOVERY-TRIAL-01(Self-Recovery Flow Trial)
iteration6(委任_14、n=2実行のsample1)の実測結果からの抜粋です。Production
(本番)記事の生成経路には未接続のTrial実装であり、この結果を見てユーザーが
「この自動修正の品質は妥当か」を確認するためのページです。iteration5からの
変更点: (1)数値の通常の四捨五入は別数値として扱わない(丸め許容)、
(2)floor-strict/floor-cited variantの並行測定、(3)最小変更ラダー
(単語・接続詞→1文→段落→全文の順に試し、前段で直れば後段へ進まない、
J-1[JA/EN対訳ペア]は既知の限界として未適用)、(4)Title/Hook/In one lineの
役割維持検出、(5)Hook-aware統合(changed_scope単独発火のみ緩和、
changed_comparisonはfloor安全装置のため対象外)、(6)記事単位コスト5分割
計測。</p>
</div>
"""

PAGE_FOOTER = """
<footer>
生成元: er052_open233_self_recovery_rewrite_compare_page_iter6_01.py (API呼び出し
なし、既存iteration6証跡json[er052_output/open233_self_recovery_flow_runner_01_
iter6/instances_s1/]の読み直しのみ)。管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
(委任_14)。
</footer>
</body>
</html>
"""


def render_instance_section(sel: dict) -> str:
    inst = load_instance(sel["instance_id"])
    claims = collect_blocking_claims(inst)
    ladder = collect_rewrite_ladder(inst)
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
            f'rewrite_kind={html.escape(str(c["rewrite_kind"]))} / '
            f'section_type={html.escape(str(c.get("section_type")))}'
            f'{" / floor=" + html.escape(str(c["floor_reason"])) if c["floor_reason"] else ""}'
            f'{" / floor_cited=" + html.escape(str(c["floor_cited_reason"])) if c.get("floor_cited_reason") else " / floor_cited=なし"}'
            '</div>'
            f'<div>対象claim: 「{html.escape(c["claim_text"])}」</div>'
            f'<div>修正方針(rewrite_hint): {html.escape(c["rewrite_hint"])}</div>'
            '</div>'
        )
    parts.append('</div>')

    if ladder:
        parts.append('<div class="note"><strong>最小変更ラダー(委任_14 B-3)の停止水準</strong>: '
                      + html.escape(" / ".join(
                          f'cycle{l["cycle"]}:{l["ladder_level_used"]}({l["mechanism"]})' for l in ladder))
                      + '</div>')

    # 委任_13/_14: 品質劣化検出v2+セクション役割違反の結果があれば併記する。
    qd_notes = []
    for ci, c in enumerate(inst["cycles"], start=1):
        qd = c.get("quality_degradation_v2")
        if qd and (qd.get("duplicate_paragraph_detected") or qd.get("orphan_contrastive_detected")
                   or qd.get("vocab_difficulty_increased")):
            qd_notes.append(f'cycle{ci}品質劣化v2: {qd.get("reasons")} '
                             f'(再生成実施={c.get("quality_degradation_v2_regenerated")})')
        sr = c.get("section_role_violation")
        if sr and sr.get("section_role_violated"):
            qd_notes.append(f'cycle{ci}セクション役割違反: {sr.get("reasons")}')
    if qd_notes:
        parts.append('<div class="note"><strong>品質劣化検出v2/セクション役割違反の所見</strong>: '
                      + html.escape(" / ".join(qd_notes)) + '</div>')

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
    # iteration5版を保存してからiteration6版で上書きする(移動・削除禁止の
    # 既存運用どおり、iter4版と同じパターン)。
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
