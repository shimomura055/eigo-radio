# scratchpad generator: builds the Trial-20 HTML report/Artifact from
# trial_summary.json + per-run diff html files. Not part of production code.
from __future__ import annotations

import html
import json
import os

BASE = "er011_output/no18_a2_evidence_compression_abc_precision_extension_trial_20"
OUT_HTML = r"C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\6d74e7a4-95be-49c2-afaf-d47cf0461e2a\scratchpad\trial20_report.html"

with open(f"{BASE}/trial_summary.json", encoding="utf-8") as f:
    S = json.load(f)
RUNS = S["runs"]

PATTERN_LABELS = {
    "A": "Pattern A — Representative Metric + Supporting Trend",
    "B": "Pattern B — Conclusion-First / Numeric Necessity Test",
    "C": "Pattern C — Listener-Friendly Numeric Re-expression",
}
PATTERN_ORDER = ["A", "B", "C"]
PATTERN_ACCENT = {"A": "a", "B": "b", "C": "c"}

RUN_IDS_BY_PATTERN = {k: [] for k in PATTERN_ORDER}
for rid, r in RUNS.items():
    RUN_IDS_BY_PATTERN[r["pattern"]].append(rid)
for k in RUN_IDS_BY_PATTERN:
    RUN_IDS_BY_PATTERN[k].sort()


def esc(x):
    return html.escape(str(x))


def sev_badge(sev):
    cls = {"MINOR": "sev-minor", "MAJOR": "sev-major", "CRITICAL": "sev-major"}.get(sev, "sev-minor")
    return f'<span class="badge {cls}">{esc(sev)}</span>'


def verdict_badge(v):
    cls = {"PASS": "sev-ok", "REVIEW_REQUIRED": "sev-review", "FAIL": "sev-major"}.get(v, "sev-review")
    return f'<span class="badge {cls}">{esc(v)}</span>'


def ledger_badge(v):
    cls = "sev-ok" if v == "LEDGER_COMPLIANT" else "sev-major"
    return f'<span class="badge {cls}">{esc(v)}</span>'


def bool_badge(b, yes_label="Yes", no_label="No"):
    return f'<span class="badge sev-ok">{yes_label}</span>' if b else f'<span class="badge sev-review">{no_label}</span>'


# ---------------------------------------------------------------
# Precision Decision Table (18 rows = 9 runs x F-005/F-006).
# Values confirmed by direct reading of area_text / precision_numbers /
# fact_separation_check in trial_summary.json for each run.
# pattern_c_precision_02's automated "possible_fact_merge_risk": true is a
# false positive of the crude sentence-overlap heuristic (the single
# combined sentence mentions both metric keywords, so both numbers "9"
# and "10" got attributed to both metrics' number-sets even though the
# text itself keeps them clearly separate and correctly attributed:
# "attention ... about 9 points lower, and processing speed ... about 10
# points lower". Fact Checker independently confirmed both deltas as
# accurate. Manually verified safe, not a real Fact merge.
# ---------------------------------------------------------------
PRECISION_ROWS = [
    # run_id, fact_id, metric, original, output_expr, rounded, decimal_kept, reason, safe, note
    ("pattern_a_precision_01", "F-005", "attention score", "99.71 / 108.95", "about 100 / about 109", True, False, "代表指標として保持、Precisionルールにより小数省略", True, ""),
    ("pattern_a_precision_01", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern A自身のルールでtrend化(数値省略はPrecision起因ではない)", True, ""),
    ("pattern_a_precision_02", "F-005", "attention score", "99.71 / 108.95", "about 100 / 109", True, False, "代表指標として保持、Precisionルールにより小数省略(2つ目の数字は\"about\"表現なし)", True, "表現がやや非対称(片方のみ\"about\")"),
    ("pattern_a_precision_02", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern A自身のルールでtrend化", True, ""),
    ("pattern_a_precision_03", "F-005", "attention score", "99.71 / 108.95", "about 100 / about 109", True, False, "代表指標として保持、Precisionルールにより小数省略", True, ""),
    ("pattern_a_precision_03", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern A自身のルールでtrend化", True, ""),
    ("pattern_b_precision_01", "F-005", "attention score", "99.71 / 108.95", "99.71 / 108.95", False, True, "このrunはPrecisionルール下でも小数保持を選択(保守的判断)", True, "3run中唯一、小数を落とさなかった"),
    ("pattern_b_precision_01", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern B自身のNecessity Testでtrend化", True, ""),
    ("pattern_b_precision_02", "F-005", "attention score", "99.71 / 108.95", "about 100 / about 109", True, False, "Precisionルールにより小数省略", True, ""),
    ("pattern_b_precision_02", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern B自身のNecessity Testでtrend化", True, ""),
    ("pattern_b_precision_03", "F-005", "attention score", "99.71 / 108.95", "about 100 / about 109", True, False, "Precisionルールにより小数省略", True, ""),
    ("pattern_b_precision_03", "F-006", "processing speed", "98.48 / 108.57", "(数値なし・trend文)", None, None, "Pattern B自身のNecessity Testでtrend化", True, ""),
    ("pattern_c_precision_01", "F-005", "attention score", "99.71 / 108.95 (差9.24)", "about 9 points lower", True, False, "差分再表現+Precisionにより整数化。数値精度は正確(誤差1.0以内)", True, ""),
    ("pattern_c_precision_01", "F-006", "processing speed", "98.48 / 108.57 (差10.09)", "about 10 points lower", True, False, "差分再表現+Precisionにより整数化。数値精度は正確", True, ""),
    ("pattern_c_precision_02", "F-005", "attention score", "99.71 / 108.95 (差9.24)", "about 9 points lower", True, False, "差分再表現+Precisionにより整数化。1文にF-005/F-006を併記", True, "自動heuristicが\"文共有\"を誤検知(下記コールアウト参照)。数値は区別維持・正確"),
    ("pattern_c_precision_02", "F-006", "processing speed", "98.48 / 108.57 (差10.09)", "about 10 points lower", True, False, "差分再表現+Precisionにより整数化", True, "同上"),
    ("pattern_c_precision_03", "F-005", "attention score", "99.71 / 108.95 (差9.24)", "about 9 points lower", True, False, "差分再表現+Precisionにより整数化。数値精度は正確", True, ""),
    ("pattern_c_precision_03", "F-006", "processing speed", "98.48 / 108.57 (差10.09)", "about 10 points lower", True, False, "差分再表現+Precisionにより整数化。数値精度は正確", True, ""),
]


def build_precision_table():
    rows = []
    for rid, fact_id, metric, orig, out, rounded, dec_kept, reason, safe, note in PRECISION_ROWS:
        key = RUNS[rid]["pattern"]
        rounded_html = "—" if rounded is None else bool_badge(rounded, "Rounded", "As-is")
        dec_html = "—" if dec_kept is None else bool_badge(dec_kept, "Kept", "Dropped")
        safe_html = bool_badge(safe, "Safe", "要確認")
        rows.append(f"""
        <tr class="pat-{PATTERN_ACCENT[key]}">
          <td class="mono small">{esc(rid)}</td>
          <td class="mono small">{esc(fact_id)}<br><span class="small" style="color:var(--text-muted)">{esc(metric)}</span></td>
          <td class="small">{esc(orig)}</td>
          <td class="small">{esc(out)}</td>
          <td>{rounded_html}</td>
          <td>{dec_html}</td>
          <td class="small">{esc(reason)}</td>
          <td>{safe_html}</td>
          <td class="small">{esc(note)}</td>
        </tr>""")
    return "\n".join(rows)


# =================================================================
# per-pattern aggregate stat cards
# =================================================================
def build_stat_cards():
    cards = []
    for key in PATTERN_ORDER:
        rids = RUN_IDS_BY_PATTERN[key]
        rs = [RUNS[r] for r in rids]
        n = len(rs)
        wc = [x["metrics"]["word_count"] for x in rs]
        total_nums = [x["number_count_total"] for x in rs]
        decimals = [x["precision_numbers"]["decimal_count"] for x in rs]
        ledger_ok = sum(1 for x in rs if x["ledger_overall_status"] == "LEDGER_COMPLIANT")
        major_ct = sum(1 for x in rs for d in x["ledger_deviations"] if d["severity"] in ("MAJOR", "CRITICAL"))
        minor_ct = sum(1 for x in rs for d in x["ledger_deviations"] if d["severity"] == "MINOR")
        fact_pass = sum(1 for x in rs if x["fact_checker_verdict"] == "PASS")
        fact_fail = sum(1 for x in rs if x["fact_checker_verdict"] == "FAIL")
        causal = sum(len(x["new_causal_markers_vs_baseline_input"]) for x in rs)
        both_facts = sum(1 for x in rs if x["f005_f006_area"]["mentions_attention"] and x["f005_f006_area"]["mentions_processing_speed"])
        cards.append(f"""
        <div class="stat-card pat-{PATTERN_ACCENT[key]}">
          <h3>{esc(PATTERN_LABELS[key])}</h3>
          <div class="stat-row"><span>平均語数</span><strong>{round(sum(wc)/n,1)}</strong></div>
          <div class="stat-row"><span>記事全体の数字数(平均/範囲)</span><strong>{round(sum(total_nums)/n,1)} ({min(total_nums)}–{max(total_nums)})</strong></div>
          <div class="stat-row"><span>対象箇所の小数付き数字数(合計/{n}run)</span><strong>{sum(decimals)}</strong></div>
          <div class="stat-row"><span>両Fact保持</span><strong>{both_facts} / {n}</strong></div>
          <div class="stat-row"><span>Ledger COMPLIANT</span><strong>{ledger_ok} / {n}</strong></div>
          <div class="stat-row"><span>Ledger MAJOR / MINOR件数</span><strong>{major_ct} / {minor_ct}</strong></div>
          <div class="stat-row"><span>Fact Checker PASS / FAIL</span><strong>{fact_pass} / {fact_fail}</strong></div>
          <div class="stat-row"><span>新規causal drift検出</span><strong>{causal}</strong></div>
        </div>""")
    return "\n".join(cards)


def build_ledger_table():
    rows = []
    for key in PATTERN_ORDER:
        for rid in RUN_IDS_BY_PATTERN[key]:
            r = RUNS[rid]
            devs = r["ledger_deviations"]
            status = r["ledger_overall_status"]
            if not devs:
                rows.append(f"""
                <tr class="pat-{PATTERN_ACCENT[key]}">
                  <td class="mono small">{esc(rid)}</td>
                  <td>{ledger_badge(status)}</td>
                  <td class="small" colspan="2">検出なし</td>
                </tr>""")
            else:
                for i, d in enumerate(devs):
                    rows.append(f"""
                    <tr class="pat-{PATTERN_ACCENT[key]}">
                      <td class="mono small">{esc(rid) if i == 0 else ""}</td>
                      <td>{ledger_badge(status) if i == 0 else ""}</td>
                      <td>{sev_badge(d["severity"])}</td>
                      <td class="small">{esc(d["claim_in_article"][:110])}{"…" if len(d["claim_in_article"]) > 110 else ""}</td>
                    </tr>""")
    return "\n".join(rows)


def build_fact_table():
    rows = []
    for key in PATTERN_ORDER:
        for rid in RUN_IDS_BY_PATTERN[key]:
            r = RUNS[rid]
            rows.append(f"""
            <tr class="pat-{PATTERN_ACCENT[key]}">
              <td class="mono small">{esc(rid)}</td>
              <td>{verdict_badge(r["fact_checker_verdict"])}</td>
              <td class="num">{r.get("fact_checker_unsupported_claim_count") if r.get("fact_checker_unsupported_claim_count") is not None else "–"}</td>
            </tr>""")
    return "\n".join(rows)


def build_change_volume_table():
    rows = []
    for key in PATTERN_ORDER:
        for rid in RUN_IDS_BY_PATTERN[key]:
            r = RUNS[rid]
            sd = r["sentence_diff_stats"]
            rows.append(f"""
            <tr class="pat-{PATTERN_ACCENT[key]}">
              <td class="mono small">{esc(rid)}</td>
              <td class="num">{sd["baseline_sentence_count"]}</td>
              <td class="num">{sd["variant_sentence_count"]}</td>
              <td class="num">{sd["unchanged_sentences"]}</td>
              <td class="num">{sd["replaced_sentences"]}</td>
            </tr>""")
    return "\n".join(rows)


# =================================================================
# Trial-19 (no precision rule) vs Trial-20 (with precision rule)
# comparison, per pattern, for the F-005/F-006 attention value.
# Trial-19 numbers below are taken directly from
# no18_a2_evidence_compression_abc_reproducibility_trial_19/trial_summary.json
# (read and cross-checked in this session; Trial-19 itself is unmodified).
# =================================================================
COMPARISON_ROWS = [
    ("A", "Trial-19 (Precisionなし)", "5/5", "99.71 / 108.95(小数保持のまま)を100%維持"),
    ("A", "Trial-20 (Precisionあり)", "3/3", "about 100 / about 109 へ100%丸め(初めて小数を落とした)"),
    ("B", "Trial-19 (Precisionなし)", "5/5", "99.71 / 108.95(小数保持のまま)を100%維持"),
    ("B", "Trial-20 (Precisionあり)", "1/3 保持・2/3 丸め", "run間でPrecision適用の強度が割れた(唯一の非一貫パターン)"),
    ("C", "Trial-19 (Precisionなし)", "5/5", "about 9 / about 10 (差分再表現の時点で既に整数化)"),
    ("C", "Trial-20 (Precisionあり)", "3/3", "about 9 / about 10 (変化なし、Precisionルールは実質no-op)"),
]


def build_comparison_table():
    rows = []
    for key, label, ratio, note in COMPARISON_ROWS:
        rows.append(f"""
        <tr class="pat-{PATTERN_ACCENT[key]}">
          <td class="mono small">{esc(PATTERN_LABELS[key].split(" — ")[0])}</td>
          <td class="small">{esc(label)}</td>
          <td class="mono small">{esc(ratio)}</td>
          <td class="small">{esc(note)}</td>
        </tr>""")
    return "\n".join(rows)


def build_diff_viewer():
    panels = []
    for key in PATTERN_ORDER:
        run_cards = []
        for i, rid in enumerate(RUN_IDS_BY_PATTERN[key]):
            with open(f"{BASE}/audit/diff_{rid}.html", encoding="utf-8") as f:
                diff_html = f.read()
            open_attr = " open" if i == 0 else ""
            run_cards.append(f"""
            <details class="run-diff pat-{PATTERN_ACCENT[key]}"{open_attr}>
              <summary>{esc(rid)}</summary>
              <div class="diff-body">{diff_html}</div>
            </details>""")
        panels.append(f"""
        <section class="diff-panel" id="diffpanel-{key}" role="tabpanel" aria-labelledby="difftab-{key}"{' hidden' if key != 'A' else ''}>
          {''.join(run_cards)}
        </section>""")
    tabs = "\n".join(
        f'<button class="tab-btn{" active" if key == "A" else ""}" id="difftab-{key}" '
        f'onclick="showDiffTab(\'{key}\')">{esc(PATTERN_LABELS[key].split(" — ")[0])}</button>'
        for key in PATTERN_ORDER
    )
    return f'<div class="tab-bar" role="tablist">{tabs}</div>' + "\n".join(panels)


PRECISION_TABLE = build_precision_table()
STAT_CARDS = build_stat_cards()
LEDGER_TABLE = build_ledger_table()
FACT_TABLE = build_fact_table()
CHANGE_VOLUME_TABLE = build_change_volume_table()
COMPARISON_TABLE = build_comparison_table()
DIFF_VIEWER = build_diff_viewer()

HTML_PAGE = f"""<title>Precision Extension Trial</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root {{
  --bg: #eef1f4;
  --surface: #ffffff;
  --surface-2: #f5f7f9;
  --text: #1a2130;
  --text-muted: #5b6472;
  --border: #dbe0e6;
  --accent: #34586b;
  --accent-soft: #dce8ec;
  --ok: #2f7a4f;
  --ok-soft: #dcefe2;
  --warn: #96631a;
  --warn-soft: #f5e8cf;
  --bad: #a23b3b;
  --bad-soft: #f6dede;
  --pat-a: #4d6f8a;
  --pat-b: #7a5a9c;
  --pat-c: #2f8073;
  --font-display: "Fraunces", Georgia, serif;
  --font-body: "IBM Plex Sans", -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #12161c; --surface: #191f27; --surface-2: #1f2732;
    --text: #e7ebf0; --text-muted: #98a2b0; --border: #2c3644;
    --accent: #7fa6bd; --accent-soft: #24333b;
    --ok: #6fbf8e; --ok-soft: #1c3226;
    --warn: #d8ab5c; --warn-soft: #3a2f18;
    --bad: #e18787; --bad-soft: #3a2222;
    --pat-a: #8fb3cc; --pat-b: #b79fd6; --pat-c: #6fc0ac;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #12161c; --surface: #191f27; --surface-2: #1f2732;
  --text: #e7ebf0; --text-muted: #98a2b0; --border: #2c3644;
  --accent: #7fa6bd; --accent-soft: #24333b;
  --ok: #6fbf8e; --ok-soft: #1c3226;
  --warn: #d8ab5c; --warn-soft: #3a2f18;
  --bad: #e18787; --bad-soft: #3a2222;
  --pat-a: #8fb3cc; --pat-b: #b79fd6; --pat-c: #6fc0ac;
}}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--font-body); line-height: 1.6; margin: 0; padding: 0 0 4rem; }}
h1, h2, h3 {{ font-family: var(--font-display); font-weight: 600; text-wrap: balance; }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding: 0 1.5rem; }}
header.hero {{ background: linear-gradient(180deg, var(--accent-soft), var(--bg)); border-bottom: 1px solid var(--border); padding: 2.6rem 0 1.8rem; }}
header.hero .eyebrow {{ font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); }}
header.hero h1 {{ font-size: 2.1rem; margin: 0.35rem 0 0.5rem; }}
header.hero p {{ color: var(--text-muted); max-width: 62ch; margin: 0 0 1rem; }}
.status-banner {{ display: inline-flex; align-items: center; gap: 0.5rem; background: var(--warn-soft); color: var(--warn); border: 1px solid var(--warn); border-radius: 999px; padding: 0.35rem 0.9rem; font-family: var(--font-mono); font-size: 0.82rem; font-weight: 600; }}
section {{ padding: 2.4rem 0; border-bottom: 1px solid var(--border); }}
section:last-of-type {{ border-bottom: none; }}
h2 {{ font-size: 1.5rem; margin: 0 0 0.3rem; }}
.section-sub {{ color: var(--text-muted); margin: 0 0 1.4rem; max-width: 72ch; }}
.callout {{ background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 8px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; }}
.callout.warn {{ border-left-color: var(--warn); }}
.callout h4 {{ margin: 0 0 0.4rem; font-family: var(--font-body); font-size: 0.95rem; font-weight: 700; }}
.callout p {{ margin: 0.3rem 0; color: var(--text); font-size: 0.92rem; }}
.callout code {{ font-family: var(--font-mono); background: var(--surface-2); padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.85em; }}
.stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }}
.stat-card {{ background: var(--surface); border: 1px solid var(--border); border-top: 4px solid var(--text-muted); border-radius: 10px; padding: 1.1rem 1.2rem; }}
.stat-card.pat-a {{ border-top-color: var(--pat-a); }}
.stat-card.pat-b {{ border-top-color: var(--pat-b); }}
.stat-card.pat-c {{ border-top-color: var(--pat-c); }}
.stat-card h3 {{ font-size: 1rem; margin: 0 0 0.7rem; font-family: var(--font-body); font-weight: 700; }}
.stat-row {{ display: flex; justify-content: space-between; gap: 1rem; font-size: 0.86rem; padding: 0.28rem 0; border-bottom: 1px dashed var(--border); }}
.stat-row:last-child {{ border-bottom: none; }}
.stat-row span {{ color: var(--text-muted); }}
.stat-row strong {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.86rem; background: var(--surface); }}
.table-scroll {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; }}
th, td {{ padding: 0.55rem 0.7rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
th {{ background: var(--surface-2); font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); position: sticky; top: 0; }}
td.mono, .mono {{ font-family: var(--font-mono); }}
td.num, .num {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; text-align: right; }}
td.small, .small {{ font-size: 0.82rem; }}
tr.pat-a td:first-child {{ border-left: 3px solid var(--pat-a); }}
tr.pat-b td:first-child {{ border-left: 3px solid var(--pat-b); }}
tr.pat-c td:first-child {{ border-left: 3px solid var(--pat-c); }}
.badge {{ display: inline-block; font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; padding: 0.12rem 0.5rem; border-radius: 999px; white-space: nowrap; }}
.sev-ok {{ background: var(--ok-soft); color: var(--ok); }}
.sev-minor {{ background: var(--warn-soft); color: var(--warn); }}
.sev-major {{ background: var(--bad-soft); color: var(--bad); }}
.sev-review {{ background: var(--surface-2); color: var(--text-muted); border: 1px solid var(--border); }}
.tab-bar {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1rem; }}
.tab-btn {{ font-family: var(--font-mono); font-size: 0.82rem; background: var(--surface); color: var(--text-muted); border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem 0.9rem; cursor: pointer; }}
.tab-btn.active {{ background: var(--accent); color: var(--surface); border-color: var(--accent); }}
.run-diff {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.7rem; overflow: hidden; }}
.run-diff.pat-a {{ border-left: 4px solid var(--pat-a); }}
.run-diff.pat-b {{ border-left: 4px solid var(--pat-b); }}
.run-diff.pat-c {{ border-left: 4px solid var(--pat-c); }}
.run-diff summary {{ font-family: var(--font-mono); font-size: 0.85rem; padding: 0.65rem 1rem; cursor: pointer; background: var(--surface-2); }}
.diff-body {{ padding: 1rem 1.2rem; font-size: 0.92rem; line-height: 1.75; white-space: pre-wrap; }}
.diff-del {{ color: var(--bad); text-decoration: line-through; background: var(--bad-soft); border-radius: 3px; padding: 0 2px; }}
.diff-add {{ color: var(--ok); text-decoration: none; background: var(--ok-soft); border-radius: 3px; padding: 0 2px; font-weight: 600; }}
.legend {{ display: flex; gap: 1.2rem; font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1rem; }}
.legend .diff-del, .legend .diff-add {{ padding: 0.1rem 0.4rem; }}
.rank-list {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 0.6rem; }}
.rank-list li {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.8rem 1rem; display: flex; gap: 0.9rem; align-items: baseline; }}
.rank-list .rank-num {{ font-family: var(--font-display); font-size: 1.3rem; color: var(--accent); }}
.rule-box {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.2rem; font-size: 0.86rem; white-space: pre-wrap; font-family: var(--font-mono); line-height: 1.6; max-height: 420px; overflow-y: auto; }}
footer {{ padding: 2rem 0 0; color: var(--text-muted); font-size: 0.82rem; }}
footer a {{ color: var(--accent); }}
</style>

<header class="hero">
  <div class="wrap">
    <div class="eyebrow">ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-PRECISION-EXTENSION-TRIAL-20</div>
    <h1>Listener-Friendly Numeric Precision 追加Trial</h1>
    <p>Trial-19で再現性を確認したPattern A/B/Cに、共通の追加ルール「Listener-Friendly Numeric Precision」を
    重ね、不要な小数精度を安全に落とせるか・Factを保持したまま聴取負荷をさらに下げられるか・丸めによる
    意味変化やFact統合を起こさないかを、各Pattern3回ずつ(計9 run)で比較しました。すべてTrialであり、
    Production Prompt変更・記事上書き・TTSは一切行っていません。</p>
    <span class="status-banner">● USER_DECISION_REQUIRED — Production未採用</span>
  </div>
</header>

<div class="wrap">

<section id="rule">
  <h2>今回追加した共通ルール全文</h2>
  <p class="section-sub">3 Pattern共通・Pattern固有のカスタマイズなし。A/B/C既存のルール文(Trial-18/19と同一)の後ろに、
  この英語ブロックだけを追加しました。</p>
  <div class="rule-box">{esc(S["precision_rule_text"])}</div>
</section>

<section id="findings">
  <h2>最重要の発見</h2>
  <p class="section-sub">n=3のため統計的有意差は主張しません。傾向観測として記載します。</p>

  <div class="callout">
    <h4>① Pattern Aは3/3 runで初めて小数を落とした(Trial-19では5/5とも小数を保持していた)</h4>
    <p>Trial-19(Precisionルールなし)ではPattern Aは5 run全てで <code>99.71 / 108.95</code> を小数のまま保持していました。
    今回Precisionルールを加えたところ、Pattern Aは3 run全てで <code>about 100 / about 109</code> へ丸め、
    かつ丸め後もF-005・F-006両方のFactを区別したまま保持し、数値もPew研究の実測値から見て妥当な誤差内でした。
    最も一貫してPrecisionルールの狙い通りに動いたPatternです。</p>
  </div>

  <div class="callout warn">
    <h4>② Pattern Bは3 run中1 runだけ小数を保持し、2 runは丸めた(一貫性が最も低い)</h4>
    <p><code>pattern_b_precision_01</code>は<code>99.71 / 108.95</code>を小数のまま残しましたが、
    <code>pattern_b_precision_02・03</code>は<code>about 100 / about 109</code>へ丸めました。
    「結論優先+数値必要性判定」というPattern B自体の中核挙動(両Fact保持・安全性)は3/3 runとも安定していましたが、
    Precisionルールの適用強度そのものは3 run中で割れており、A/Cに比べて再現性が低いという新しい知見です。</p>
  </div>

  <div class="callout">
    <h4>③ Pattern Cへの効果は実質ゼロ(Precisionルールを追加しても出力が変わらなかった)</h4>
    <p>Pattern Cは元々「差・概数への再表現」自体がPrecision的な判断を内包しており、Trial-19の時点で
    既に<code>about 9 points lower / about 10 points lower</code>という整数表現を使っていました。
    Precisionルールを追加したTrial-20でも3/3 runとも同じ表現で、数値の正確性(誤差1.0以内)も変わらず維持されました。
    Pattern Cにとって今回の追加ルールは安全ではあるものの、実質的な追加効果を確認できませんでした。</p>
  </div>

  <div class="callout">
    <h4>④ Fact統合(Fact merge)は9 run中0件。ただし自動判定に1件の誤検知あり(手動確認済み)</h4>
    <p><code>pattern_c_precision_02</code>は「attention...about 9 points lower, and processing speed...
    about 10 points lower」と1文にまとめましたが、2つのFactの数値(9と10)はそれぞれ正しく区別されたまま
    保持されており、Fact Checkerも両方の差分を「概ね正確」と確認しています。自動スクリプトの粗いheuristic
    (文単位での重複チェック)が誤って「統合リスクあり」と表示しましたが、手動確認の結果、
    Trial-19の<code>baseline_03</code>(2つの異なるFactを同じ概数ペアへ実際に混同した事例)とは異なり、
    実際のFact混同は起きていません。</p>
  </div>
</section>

<section id="stats">
  <h2>Pattern別 統計サマリー(各n=3)</h2>
  <div class="stat-grid">
    {STAT_CARDS}
  </div>
</section>

<section id="precision">
  <h2>Precision Decision Table — No.18対象4数字の扱い(9 run × F-005/F-006)</h2>
  <p class="section-sub">元のFact Ledger数値(99.71 / 108.95 / 98.48 / 108.57)が、各runでどう扱われたかの一覧です。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Run ID</th><th>Fact</th><th>Original</th><th>Output</th><th>Rounded?</th><th>Decimal kept?</th><th>理由</th><th>Safe?</th><th>備考</th></tr></thead>
      <tbody>
        {PRECISION_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="comparison">
  <h2>Trial-19(Precisionなし) vs Trial-20(Precisionあり)比較</h2>
  <p class="section-sub">代表指標(attention score)の小数の扱いを、Pattern別にPrecisionルール追加前後で比較しています。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Pattern</th><th>条件</th><th>丸め比率</th><th>備考</th></tr></thead>
      <tbody>
        {COMPARISON_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="ledger">
  <h2>Ledger Deviation Check 詳細(全9 run)</h2>
  <p class="section-sub">hook_aware=Trueで実行。指摘は全て、記事末尾の既存Hook文など、F-005/F-006の数値表現とは無関係な
  箇所に集中しており、OPEN-98(Ledger Deviation Checkのrun間非決定性、2026-08-31に既知の特性として追跡終了済み)
  と同種の現象がTrial-19に続き再確認されました。数値の丸め・差分再表現そのものへの指摘は9 run中0件です。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Run ID</th><th>Overall</th><th>Severity</th><th>指摘内容(抜粋)</th></tr></thead>
      <tbody>
        {LEDGER_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="factcheck">
  <h2>Fact Checker 判定(全9 run)</h2>
  <p class="section-sub">独立webサーチによる外部Fact検証。REVIEW_REQUIREDは既存Production運用でも非ブロッキングの通常判定です。
  指摘内容は「silent phone」という既存記事の表現や研究解釈に関するもので、いずれもpre-editor記事の時点で
  既に存在していた表現であり、今回のPrecisionルールや数値の丸めが原因で新たに生じたものではありません。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Run ID</th><th>Verdict</th><th>Unsupported claim件数</th></tr></thead>
      <tbody>
        {FACT_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="changevol">
  <h2>記事全体の変更量(文単位)</h2>
  <p class="section-sub">pre-editor記事(34文)を基準にした文単位diff。全9 runで削除0/追加0、置換のみで、
  記事構造そのものを壊す大規模な書き換えは9 run中0件でした。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Run ID</th><th>元文数</th><th>出力文数</th><th>不変</th><th>置換</th></tr></thead>
      <tbody>
        {CHANGE_VOLUME_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="diffviewer">
  <h2>ハイライト付き全文比較(全9 run)</h2>
  <p class="section-sub">pre-editor記事を基準に、Editorが変更した箇所を可視化しています。各runをクリックして展開してください。</p>
  <div class="legend">
    <span><del class="diff-del">削除された箇所</del></span>
    <span><ins class="diff-add">追加・言い換えられた箇所</ins></span>
  </div>
  {DIFF_VIEWER}
</section>

<section id="no9">
  <h2>No.9 OPEN-100への静的汎用性評価(更新)</h2>
  <p class="section-sub">No.9は再生成していません。Trial-19時点の評価に、今回のPrecisionルールの知見を追加します。</p>
  <div class="callout">
    <h4>Pattern C — Trial-19時点の結論を維持</h4>
    <p>No.9のPoint Twoは3つの異なる調査質問であり、No.18のような自然な2条件差分が存在しないため、
    構造的に適用困難という評価はPrecisionルール追加後も変わりません。</p>
  </div>
  <div class="callout">
    <h4>Pattern A — Precisionルールにより丸めが積極化した分、survey型では要注意度がやや上がる</h4>
    <p>No.18では「代表指標のみ絶対値・他はtrend化」という構造により、丸めても異なるFact同士が数値衝突しない
    ことを確認できました。ただしNo.9のように3つの質問が並ぶ場合、どれを「代表」として丸め対象にするかという
    編集判断が追加で必要になり、Trial-19時点の「概念的に適用可能、ただし要注意」という評価を維持します。</p>
  </div>
  <div class="callout warn">
    <h4>Pattern B — 精度適用の一貫性が低いため、survey型ではさらに慎重な検証が必要</h4>
    <p>No.18単体でも3 run中1 runが小数を保持・2 runが丸めるという揺れが見られたため、survey型記事へ
    転用する場合はPrecisionルールの効果自体がrunごとに変わりうる点を踏まえ、Trial-19時点より一段階
    慎重な評価とします。</p>
  </div>
</section>

<section id="rank">
  <h2>Claude推奨順位(採用判断ではありません)</h2>
  <ol class="rank-list">
    <li><span class="rank-num">1</span><div><strong>Pattern C</strong> — Precisionルール追加後も3/3 runで完全に安定・数値正確。Precisionルールとの相性が良く(実質no-op)、副作用もなし。</div></li>
    <li><span class="rank-num">2</span><div><strong>Pattern A</strong> — Precisionルールの狙い通り、3/3 runで一貫して小数を安全に丸めた。Fact混同も起きていない。</div></li>
    <li><span class="rank-num">3</span><div><strong>Pattern B</strong> — 核となる挙動(両Fact保持・安全性)は3/3 runで安定しているが、Precisionルールの適用強度が3 run中で割れ、再現性はA/Cより低い。</div></li>
  </ol>
  <p class="section-sub">最終的な採用判断はユーザーに委ねます。Status: <strong>USER_DECISION_REQUIRED</strong>。</p>
</section>

<footer>
  <p>ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-PRECISION-EXTENSION-TRIAL-20 / 生成日: 2026-09-04 /
  Production Prompt・CURRENT_SPEC・No.18 article.md・TTSへの変更は一切なし。</p>
</footer>

</div>

<script>
function showDiffTab(key) {{
  document.querySelectorAll('.diff-panel').forEach(function(p) {{ p.hidden = (p.id !== 'diffpanel-' + key); }});
  document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.toggle('active', b.id === 'difftab-' + key); }});
}}
</script>
"""

os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(HTML_PAGE)
print("wrote", OUT_HTML, len(HTML_PAGE), "chars")
