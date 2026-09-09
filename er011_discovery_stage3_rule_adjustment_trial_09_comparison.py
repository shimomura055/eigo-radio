#!/usr/bin/env python3
"""
FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09
D-2目視artifact生成(Role文字列のヒューリスティック分類は行わず、
Point本文をそのまま並置する。Trial-08の比較artifact形式
[er011_output/discovery_stage2_interpretation_rule_trial_08/comparison.html]に
倣ったテーブル形式)。

Production/Prompt/共有module編集ではない(閲覧用HTML生成のみ)。
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TRIAL09_DIR = BASE_DIR / "er011_output" / "discovery_stage3_rule_adjustment_trial_09"
OUT_DIR = TRIAL09_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)

ORIGINAL_ARTICLES = {
    "A2": BASE_DIR / "er003_output/n3_01/household/a2/article.md",
    "B1B": BASE_DIR / "er003_output/n3_01/household/b1b/article.md",
}

CONDITIONS = ["current_focus", "adjusted_focus"]
LEVEL_DIRS = {"A2": "a2", "B1B": "b1b"}


def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def read_text(p: Path):
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def read_json(p: Path):
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def find_runs(condition: str, level_dir: str):
    cond_dir = TRIAL09_DIR / level_dir / condition
    if not cond_dir.exists():
        return []
    runs = []
    for run_dir in sorted(cond_dir.iterdir()):
        if run_dir.is_dir() and run_dir.name.startswith("run"):
            analysis = read_json(run_dir / "analysis.json")
            if analysis:
                runs.append((run_dir.name, analysis))
    return runs


def point_cell(text, cross_overlap_key, analysis):
    if not text:
        return "<td><em>(本文なし)</em></td>"
    overlap_info = ""
    cpo = analysis.get("cross_point_overlap") if analysis else None
    if cpo:
        ratio = cpo.get(cross_overlap_key + "_ratio")
        flagged = cpo.get(cross_overlap_key + "_flagged")
        if ratio is not None:
            overlap_info = f"<div class='overlap'>cross_point_overlap={ratio} (flagged={flagged})</div>"
    return f"<td><pre>{esc(text)}</pre>{overlap_info}</td>"


def fact_cell(analysis):
    if not analysis:
        return "<td>-</td>"
    verdict = analysis.get("fact_verdict")
    status = analysis.get("status")
    if verdict is None and status and status != "OK":
        # Fact Checkerへ未到達(例: 既存Point Overlap QAでNGとなり記事全体retryが
        # 上限に達した場合)。Fact Checker由来のREVIEW_REQUIREDと混同しないよう
        # 明示的に区別して表示する。
        return (f"<td><span class='status-review'>{esc(status)}</span>"
                f"<div class='overlap'>(Fact Checker未到達。既存Point Overlap QA機構による、"
                f"本Trial非依存の判定)</div>"
                f"word_count={analysis.get('word_count')}</td>")
    cls = "status-ok" if verdict == "PASS" else ("status-ng" if verdict == "FAIL" else "status-review")
    n = analysis.get("fact_unsupported_specific_claims_count")
    wc = analysis.get("word_count")
    dprecheck = analysis.get("directional_fact_precheck_status")
    dprecheck_html = ""
    if dprecheck and dprecheck != "PASS":
        dprecheck_html = f"<div class='overlap'>directional_precheck={esc(dprecheck)}</div>"
    return (f"<td><span class='{cls}'>{esc(verdict)}</span><br>"
            f"unsupported_claims={n}<br>word_count={wc}{dprecheck_html}</td>")


def build_level_section(level: str):
    level_dir = LEVEL_DIRS[level]
    rows_html = []

    # Household original (2026-08-17承認記事)
    orig_text = read_text(ORIGINAL_ARTICLES[level])
    if orig_text:
        # 簡易分割(### 見出し2つ)
        import re
        h3 = list(re.finditer(r"^###\s+(.+?)\s*$", orig_text, flags=re.MULTILINE))
        if len(h3) == 2:
            p1 = orig_text[h3[0].end():h3[1].start()].strip()
            p2_end_match = re.search(r"^##\s+In one line", orig_text, flags=re.MULTILINE)
            p2_end = p2_end_match.start() if p2_end_match else len(orig_text)
            p2 = orig_text[h3[1].end():p2_end].strip()
            p1_full = h3[0].group(1).strip() + "\n" + p1
            p2_full = h3[1].group(1).strip() + "\n" + p2
        else:
            p1_full = p2_full = None
        rows_html.append(
            f"<tr><td><strong>Household原本(2026-08-17承認)</strong></td>"
            f"<td><pre>{esc(p1_full)}</pre></td><td><pre>{esc(p2_full)}</pre></td>"
            f"<td>Production採用済み(参考、本Trial対象外、Ledger v5適用前)</td></tr>")

    for condition in CONDITIONS:
        for run_name, analysis in find_runs(condition, level_dir):
            label = f"{condition} / {run_name}"
            rows_html.append(
                f"<tr><td><strong>{esc(label)}</strong></td>"
                f"{point_cell(analysis.get('point_one_text'), 'point_one_vs_point_two', analysis)}"
                f"{point_cell(analysis.get('point_two_text'), 'point_two_vs_point_one', analysis)}"
                f"{fact_cell(analysis)}</tr>")

    return f"""
    <div class="section-title">{level} — Point One / Point Two 本文比較</div>
    <table>
        <tr><th style="width:14%">条件/run</th><th style="width:38%">Point One</th>
        <th style="width:38%">Point Two</th><th style="width:10%">Fact結果</th></tr>
        {''.join(rows_html)}
    </table>
    """


def main():
    sections = "".join(build_level_section(level) for level in ("A2", "B1B"))
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09 Comparison</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 12px; margin-bottom: 30px; table-layout: fixed; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; word-wrap: break-word; }}
th {{ background-color: #f2f2f2; font-weight: bold; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
pre {{ white-space: pre-wrap; font-family: inherit; margin: 0; font-size: 0.92em; }}
.overlap {{ margin-top: 6px; font-size: 0.8em; color: #555; }}
.status-ok {{ color: green; font-weight: bold; }}
.status-ng {{ color: red; font-weight: bold; }}
.status-review {{ color: #b8860b; font-weight: bold; }}
.section-title {{ font-size: 1.3em; font-weight: bold; margin-top: 30px; border-bottom: 2px solid #333; padding-bottom: 6px; }}
.note {{ background: #fff8e1; border: 1px solid #f0d060; padding: 10px; margin-bottom: 20px; }}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09 — Point本文比較(D-2目視artifact)</h1>
<p>Output: <code>{OUT_DIR}</code></p>
<div class="note">
Role文字列のヒューリスティック分類は行っていない(D-2=(a)を踏襲、Point本文そのものと
cross_point_overlap[既存Point Overlap Countermeasure機構の出力、新規指標ではない]で
Fable/ユーザーが目視判定する)。current_focus=現行Focus Module(Trial-05/07/08 current_focusと
一字一句同一本体、見出しのみTrial-09向けに改稿)、adjusted_focus=Trial-08 Part A案1(既存断定回避
段落末尾へscope-generalization禁止の1文のみ追加、Trial-08で使用したadjusted版と完全同一文言、
未承認候補)。全runでHousehold Verified Fact Ledger v5(FACT-03/04整合修正版、
HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03)を使用。N=3(A2/B1B各条件3本、計12本)。
Fact Checker側の変更は行っていない(緩和なし)。
</div>
{sections}
</body>
</html>
"""
    out_path = OUT_DIR / "comparison.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
