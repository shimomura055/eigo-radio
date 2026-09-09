#!/usr/bin/env python3
"""
FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10
comparison.html生成(Before/After[current_focus vs cautionary_constrained]を
A2/B1B・run1〜3で並置し、代表記事全文と保険文(独立した注意喚起・取扱説明書的
一文)のハイライトを表示する)。標準規則によりSource列は設けない。

Production/Prompt/共有module編集ではない(閲覧用HTML生成のみ、$0)。
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "er011_output" / "discovery_stage4_cautionary_language_trial_10"

CONDITIONS = [("current_focus", "Before(現行Discovery Focus Module、未変更)"),
              ("cautionary_constrained", "After(Part B案1、最小制約文言を追加、未承認候補)")]
LEVEL_DIRS = {"A2": "a2", "B1B": "b1b"}

VERB = r"(?:check|consult|ask|see|refer to|look at|read|follow)"
SOURCE = r"(?:instructions?|manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|experts?|labels?|packagings?|packages?)"
INSURANCE_RE = re.compile(VERB + r"[^.!?]{0,80}" + SOURCE, re.IGNORECASE)


def esc(s):
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight(text: str) -> str:
    """保険文検出regex(Part A、$0静的走査、all_results_so_far集計と同一定義)に
    一致した文をハイライトする。文単位ではなくescape後の生テキストに対して
    正規表現を直接当てるため、文境界をまたぐ誤爆を避けるよう欲張らない量指定子
    ([^.!?]{0,80})を使っている(part_a_insurance_sentence_summary.jsonの検出
    ロジックと同一)。"""
    escaped = esc(text)

    def repl(m):
        return f"<mark>{m.group(0)}</mark>"

    return INSURANCE_RE.sub(repl, escaped)


def read_text(p: Path):
    return p.read_text(encoding="utf-8") if p.exists() else None


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def metrics_row(condition, level, run_idx):
    run_dir = OUT_DIR / LEVEL_DIRS[level] / condition / f"run{run_idx}"
    analysis = read_json(run_dir / "analysis.json")
    if not analysis:
        return "<tr><td colspan='7'>(結果なし)</td></tr>"
    verdict = analysis.get("fact_verdict")
    run_status = None
    summary = read_json(run_dir / "run_summary.json")
    if summary:
        run_status = summary.get("status")
    verdict_display = verdict if verdict is not None else f"(未到達: {esc(run_status)})"
    cls = "status-ok" if verdict == "PASS" else ("status-review" if verdict else "status-na")
    ledger = analysis.get("ledger_status") or "-"
    wc = analysis.get("word_count")
    article_path = run_dir / "article.md"
    article_text = read_text(article_path) or ""
    ins_hits = INSURANCE_RE.findall(article_text)
    ins_count = len(ins_hits)
    return (f"<tr><td>{esc(condition)}</td><td>{esc(level)}</td><td>run{run_idx}</td>"
            f"<td><span class='{cls}'>{esc(verdict_display)}</span></td>"
            f"<td>{esc(ledger)}</td><td>{wc}</td>"
            f"<td class='{'status-review' if ins_count else 'status-ok'}'>{ins_count}</td></tr>")


def article_cell(condition, level, run_idx):
    run_dir = OUT_DIR / LEVEL_DIRS[level] / condition / f"run{run_idx}"
    text = read_text(run_dir / "article.md")
    if not text:
        return "<td><em>(本文なし)</em></td>"
    return f"<td><pre>{highlight(text)}</pre></td>"


def build_level_section(level: str):
    rows = []
    for run_idx in (1, 2, 3):
        rows.append(
            f"<tr><td><strong>run{run_idx}</strong></td>"
            f"{article_cell('current_focus', level, run_idx)}"
            f"{article_cell('cautionary_constrained', level, run_idx)}</tr>")
    return f"""
    <div class="section-title">{level} — 記事全文 Before / After 並置(<mark>ハイライト</mark>=保険文検出regex一致)</div>
    <table class="article-table">
        <tr><th style="width:6%">run</th>
        <th style="width:47%">Before(current_focus)</th>
        <th style="width:47%">After(cautionary_constrained)</th></tr>
        {''.join(rows)}
    </table>
    """


def build_metrics_table():
    rows = []
    for level in ("A2", "B1B"):
        for condition, _ in CONDITIONS:
            for run_idx in (1, 2, 3):
                rows.append(metrics_row(condition, level, run_idx))
    return f"""
    <div class="section-title">12本 結果一覧(fact_verdict / ledger_status / word_count / 保険文検出数)</div>
    <table>
        <tr><th>条件</th><th>Lv</th><th>run</th><th>fact_verdict</th><th>ledger_status</th>
        <th>word_count</th><th>保険文検出数(BROAD)</th></tr>
        {''.join(rows)}
    </table>
    """


def main():
    metrics = build_metrics_table()
    sections = "".join(build_level_section(level) for level in ("A2", "B1B"))
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10 Comparison</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 12px; margin-bottom: 30px; table-layout: fixed; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; word-wrap: break-word; }}
th {{ background-color: #f2f2f2; font-weight: bold; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
pre {{ white-space: pre-wrap; font-family: inherit; margin: 0; font-size: 0.88em; }}
mark {{ background-color: #ffe08a; font-weight: bold; }}
.status-ok {{ color: green; font-weight: bold; }}
.status-review {{ color: #b8860b; font-weight: bold; }}
.status-na {{ color: #888; font-weight: bold; }}
.section-title {{ font-size: 1.3em; font-weight: bold; margin-top: 30px; border-bottom: 2px solid #333; padding-bottom: 6px; }}
.note {{ background: #fff8e1; border: 1px solid #f0d060; padding: 10px; margin-bottom: 20px; }}
.article-table pre {{ font-size: 0.85em; }}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10 — Before/After比較(記事全文)</h1>
<p>Output: <code>{OUT_DIR}</code></p>
<div class="note">
Before=current_focus(現行Discovery Focus Module本体、Trial-05/07/08/09と一字一句同一)。
After=cautionary_constrained(Part B案1、既存の断定回避段落の末尾へ「PointやIn One Lineの
締めくくりとして、聞き手に取扱説明書・メーカーの案内・専門家など記事の外にある情報源を
確認するよう呼びかける、独立した注意喚起・保険的な一文を書かない」旨の1文のみ追加、
Verified Fact Ledgerがその注意喚起自体を発見として示す場合は例外、未承認候補)。両条件
とも記事全文はそのまま掲載(Role文字列のヒューリスティック分類は行っていない、D-2=(a)を
踏襲)。保険文ハイライトは静的regex(check/consult/ask/see/refer to/look at/read/follow
+ instructions/manual/guide/manufacturer/maker/professional/expert/label/packaging の
共起、Part A集計と同一定義、$0)による機械的検出であり、目視の最終判断はFable/ユーザーに
委ねる。標準規則によりSource列は設けていない。全12本ともHousehold Verified Fact Ledger v5
(無変更)を使用、Fact Checker側の変更は行っていない(緩和なし)。
</div>
{metrics}
{sections}
</body>
</html>
"""
    out_path = OUT_DIR / "comparison.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
