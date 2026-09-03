# scratchpad generator: builds the Trial-19 HTML report/Artifact from
# trial_summary.json + per-run diff html files. Not part of production code.
from __future__ import annotations

import html
import json
import os

BASE = "er011_output/no18_a2_evidence_compression_abc_reproducibility_trial_19"
OUT_HTML = r"C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\6d74e7a4-95be-49c2-afaf-d47cf0461e2a\scratchpad\trial19_report.html"

with open(f"{BASE}/trial_summary.json", encoding="utf-8") as f:
    S = json.load(f)
RUNS = S["runs"]

PATTERN_LABELS = {
    "baseline": "Baseline",
    "A": "Pattern A — Representative Metric + Supporting Trend",
    "B": "Pattern B — Conclusion-First / Numeric Necessity Test",
    "C": "Pattern C — Listener-Friendly Numeric Re-expression",
}
PATTERN_ORDER = ["baseline", "A", "B", "C"]
PATTERN_ACCENT = {"baseline": "neutral", "A": "a", "B": "b", "C": "c"}

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


# ---------------------------------------------------------------
# F-005/F-006 corrected target-sentence text (regex-based extraction
# missed phrasing variants like "Attention averaged ..."; the values
# below were confirmed by direct reading of each article_<run_id>.md).
# ---------------------------------------------------------------
TARGET_SENTENCE = {
    "baseline_01": ("Both the attention and processing-speed scores were lower on the desk than when the phone was in another room.", 0, "0nums(trend文のみ)"),
    "baseline_02": ("Both attention and processing-speed scores were lower with the phone on the desk than when it was in another room.", 0, "0nums(trend文のみ)"),
    "baseline_03": ("Both attention and processing speed scores averaged about 100 with the phone on the desk, compared with about 109 when it was in another room.", 2, "2nums・ただし2つの異なるFact(attention/processing speed)を単一の概数ペアへ統合(要注意)"),
    "baseline_04": ("Attention averaged about 100 on the desk, compared with about 109 when the phone was away. Processing speed was about 98 on the desk and 109 in another room.", 4, "4nums(概数化・両Fact別々に保持)"),
    "baseline_05": ("Both attention and processing-speed scores were lower with the phone on the desk than when it was in another room.", 0, "0nums(trend文のみ)"),
    "pattern_a_01": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed showed the same pattern: it was lower with the phone on the desk.", 2, "代表指標(attention)絶対値保持+trend文"),
    "pattern_a_02": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed showed the same pattern: it was lower when the phone was on the desk.", 2, "代表指標(attention)絶対値保持+trend文"),
    "pattern_a_03": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed showed the same pattern: it was lower when the phone stayed on the desk.", 2, "代表指標(attention)絶対値保持+trend文"),
    "pattern_a_04": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed showed the same pattern.", 2, "代表指標(attention)絶対値保持+trend文"),
    "pattern_a_05": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower on the desk.", 2, "代表指標(attention)絶対値保持+trend文"),
    "pattern_b_01": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower on the desk than in another room.", 2, "結論優先+attention数値保持、processing speedは方向のみ"),
    "pattern_b_02": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower when the phone stayed on the desk.", 2, "結論優先+attention数値保持、processing speedは方向のみ"),
    "pattern_b_03": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower on the desk.", 2, "結論優先+attention数値保持、processing speedは方向のみ"),
    "pattern_b_04": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower on the desk.", 2, "結論優先+attention数値保持、processing speedは方向のみ"),
    "pattern_b_05": ("The attention score averaged 99.71 on the desk, compared with 108.95 when the phone was away. Processing speed was also lower on the desk than in another room.", 2, "結論優先+attention数値保持、processing speedは方向のみ"),
    "pattern_c_01": ("The attention score was about 9 points lower, and processing speed was about 10 points lower, when the phone was on the desk.", 2, "差分再表現(9/10)・両Fact保持・数値正確"),
    "pattern_c_02": ("The attention score was about 9 points lower, and processing speed was about 10 points lower, when the phone was on the desk.", 2, "差分再表現(9/10)・両Fact保持・数値正確"),
    "pattern_c_03": ("The attention score was about 9 points lower on the desk, and processing speed was about 10 points lower.", 2, "差分再表現(9/10)・両Fact保持・数値正確"),
    "pattern_c_04": ("The attention score was about 9 points lower, and processing speed was about 10 points lower, than when the phone was in another room.", 2, "差分再表現(9/10)・両Fact保持・数値正確"),
    "pattern_c_05": ("The attention score was about 9 points lower on the desk, and processing speed was about 10 points lower.", 2, "差分再表現(9/10)・両Fact保持・数値正確"),
}

# ---------------------------------------------------------------
# manually-reviewed "core target behaved as intended" verdict, taking
# into account that 3 of Pattern C's LEDGER_DEVIATION MAJOR flags were
# on an unrelated, byte-identical pre-existing hook sentence untouched
# by any pattern -- not on the F-005/F-006 re-expression itself.
# ---------------------------------------------------------------
CORE_INTENDED = {
    "pattern_a_01": True, "pattern_a_02": True, "pattern_a_03": True, "pattern_a_04": True, "pattern_a_05": True,
    "pattern_b_01": True, "pattern_b_02": True, "pattern_b_03": True, "pattern_b_04": True, "pattern_b_05": True,
    "pattern_c_01": True, "pattern_c_02": True, "pattern_c_03": True, "pattern_c_04": True, "pattern_c_05": True,
}


# =================================================================
# F-005/F-006 comparison table (20 rows)
# =================================================================
def build_target_table():
    rows = []
    for key in PATTERN_ORDER:
        for rid in RUN_IDS_BY_PATTERN[key]:
            r = RUNS[rid]
            text, n, note = TARGET_SENTENCE[rid]
            core_ok = CORE_INTENDED.get(rid)
            core_html = "—" if core_ok is None else ('<span class="badge sev-ok">core OK</span>' if core_ok else '<span class="badge sev-major">要確認</span>')
            rows.append(f"""
            <tr class="pat-{PATTERN_ACCENT[key]}">
              <td class="mono small">{esc(rid)}</td>
              <td>{esc(text)}</td>
              <td class="num">{n}</td>
              <td class="small">{esc(note)}</td>
              <td>{core_html}</td>
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
        wc = [x["metrics"]["word_count"] for x in rs]
        total_nums = [x["number_count_total"] for x in rs]
        ledger_ok = sum(1 for x in rs if x["ledger_overall_status"] == "LEDGER_COMPLIANT")
        major_ct = sum(1 for x in rs for d in x["ledger_deviations"] if d["severity"] in ("MAJOR", "CRITICAL"))
        minor_ct = sum(1 for x in rs for d in x["ledger_deviations"] if d["severity"] == "MINOR")
        fact_pass = sum(1 for x in rs if x["fact_checker_verdict"] == "PASS")
        fact_fail = sum(1 for x in rs if x["fact_checker_verdict"] == "FAIL")
        causal = sum(len(x["new_causal_markers_vs_baseline_input"]) for x in rs)
        core_ok = sum(1 for r in rids if CORE_INTENDED.get(r) is True) if key != "baseline" else None
        core_line = f'<div class="stat-row"><span>Core目標達成(手動確認込み)</span><strong>{core_ok} / 5</strong></div>' if core_ok is not None else ""
        cards.append(f"""
        <div class="stat-card pat-{PATTERN_ACCENT[key]}">
          <h3>{esc(PATTERN_LABELS[key])}</h3>
          <div class="stat-row"><span>平均語数</span><strong>{round(sum(wc)/len(wc),1)}</strong></div>
          <div class="stat-row"><span>記事全体の数字数(平均/範囲)</span><strong>{round(sum(total_nums)/len(total_nums),1)} ({min(total_nums)}–{max(total_nums)})</strong></div>
          <div class="stat-row"><span>Ledger COMPLIANT</span><strong>{ledger_ok} / 5</strong></div>
          <div class="stat-row"><span>Ledger MAJOR / MINOR件数</span><strong>{major_ct} / {minor_ct}</strong></div>
          <div class="stat-row"><span>Fact Checker PASS / FAIL</span><strong>{fact_pass} / {fact_fail}</strong></div>
          <div class="stat-row"><span>新規causal drift検出</span><strong>{causal}</strong></div>
          {core_line}
        </div>""")
    return "\n".join(cards)


# =================================================================
# Ledger Deviation Check detail table (20 rows, only non-empty highlighted)
# =================================================================
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


# =================================================================
# Fact Checker verdict table
# =================================================================
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


# =================================================================
# sentence-level change-volume table
# =================================================================
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
# full diff-highlighted article viewer, grouped by pattern
# =================================================================
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
        <section class="diff-panel" id="diffpanel-{key}" role="tabpanel" aria-labelledby="difftab-{key}"{' hidden' if key != 'baseline' else ''}>
          {''.join(run_cards)}
        </section>""")
    tabs = "\n".join(
        f'<button class="tab-btn{" active" if key == "baseline" else ""}" id="difftab-{key}" '
        f'onclick="showDiffTab(\'{key}\')">{esc(PATTERN_LABELS[key].split(" — ")[0])}</button>'
        for key in PATTERN_ORDER
    )
    return f'<div class="tab-bar" role="tablist">{tabs}</div>' + "\n".join(panels)


TARGET_TABLE = build_target_table()
STAT_CARDS = build_stat_cards()
LEDGER_TABLE = build_ledger_table()
FACT_TABLE = build_fact_table()
CHANGE_VOLUME_TABLE = build_change_volume_table()
DIFF_VIEWER = build_diff_viewer()

HTML_PAGE = f"""<title>Evidence Compression Reproducibility Trial</title>
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
.stat-card.pat-neutral {{ border-top-color: var(--text-muted); }}
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
tr.pat-neutral td:first-child {{ border-left: 3px solid var(--text-muted); }}
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
.run-diff.pat-neutral {{ border-left: 4px solid var(--text-muted); }}
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
footer {{ padding: 2rem 0 0; color: var(--text-muted); font-size: 0.82rem; }}
footer a {{ color: var(--accent); }}
</style>

<header class="hero">
  <div class="wrap">
    <div class="eyebrow">ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-REPRODUCIBILITY-TRIAL-19</div>
    <h1>Evidence Compression 拡張ルール A/B/C 再現性Trial</h1>
    <p>No.18 A2の既存Writer出力(pre-editor、Fact-safe)を共通入力として、Baseline・Pattern A・B・Cを各5回、
    同一条件(model / reasoning effort / input / Prompt)で実行した20 runの比較。すべてTrialであり、
    Production Prompt変更・記事上書き・TTSは一切行っていません。</p>
    <span class="status-banner">● USER_DECISION_REQUIRED — Production未採用</span>
  </div>
</header>

<div class="wrap">

<section id="findings">
  <h2>最重要の発見</h2>
  <p class="section-sub">20 runを比較した結果、Pattern自体の設計よりも大きな影響を持つ2つの現象が見つかりました。</p>

  <div class="callout warn">
    <h4>① 安全チェック自体(Ledger Deviation Check)にrun間のばらつきがある</h4>
    <p>全20 runで一字一句同一・未変更のHook文
    <code>"...a phone that never rings."</code> が、runによって「検出なし」「MINOR」「MAJOR」と
    異なる重大度で判定されました。Pattern Cで3/5 runが<code>LEDGER_DEVIATION</code>となった主因は、
    この既存文への判定ゆらぎであり、F-005/F-006の数値再表現そのものへの指摘は20 run中0件でした。</p>
  </div>

  <div class="callout">
    <h4>② 追加ルールなしのBaselineも、単独で数値の丸め・統合を行うことがある</h4>
    <p><code>baseline_03</code>は、attention(99.71/108.95)とprocessing speed(98.48/108.57)という
    異なる2つのFactを、"about 100 / about 109" という単一の概数ペアへ統合して表現しました。
    Ledger Deviation Checkはこれを検出していません。Pattern Cが要求する「Fact別・検証済みの丸め」は、
    この種の暗黙的な数値統合を防ぐ具体的な効果を持つことが示唆されます。</p>
  </div>
</section>

<section id="stats">
  <h2>Pattern別 統計サマリー(各n=5)</h2>
  <p class="section-sub">n=5のため統計的有意差は主張しません。「小規模再現性Trial」としての傾向観測です。</p>
  <div class="stat-grid">
    {STAT_CARDS}
  </div>
</section>

<section id="target">
  <h2>F-005 / F-006 対象箇所 — 20 run比較</h2>
  <p class="section-sub">問題箇所(attention score / processing speed)の出力を全run分並べています。「Core目標達成」は、
  各Patternのルールが意図した変換(代表指標保持・結論優先・差分再表現など)が機能したかどうかの判定で、
  記事内の無関係な箇所のLedger指摘とは独立に評価しています。</p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Run ID</th><th>出力</th><th>数字数</th><th>備考</th><th>判定</th></tr></thead>
      <tbody>
        {TARGET_TABLE}
      </tbody>
    </table>
  </div>
</section>

<section id="ledger">
  <h2>Ledger Deviation Check 詳細(全20 run)</h2>
  <p class="section-sub">hook_aware=Trueで実行。「検出なし」の行はLEDGER_COMPLIANTかつ指摘0件を示します。</p>
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
  <h2>Fact Checker 判定(全20 run)</h2>
  <p class="section-sub">独立webサーチによる外部Fact検証。REVIEW_REQUIREDは既存Production運用でも非ブロッキングの通常判定です。</p>
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
  <p class="section-sub">pre-editor記事(34文)を基準にした文単位diff。全run・全Patternで削除0/追加0、置換のみで、
  記事構造そのものを壊す大規模な書き換えは20 run中0件でした。</p>
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
  <h2>ハイライト付き全文比較(全20 run)</h2>
  <p class="section-sub">pre-editor記事を基準に、Evidence Compression Editorが変更した箇所を可視化しています。
  各runをクリックして展開してください。</p>
  <div class="legend">
    <span><del class="diff-del">削除された箇所</del></span>
    <span><ins class="diff-add">追加・言い換えられた箇所</ins></span>
  </div>
  {DIFF_VIEWER}
</section>

<section id="no9">
  <h2>No.9 OPEN-100への静的汎用性評価</h2>
  <p class="section-sub">No.9は再生成していません。既存のNo.9 A2記事(Point Two: 78% / 44% / 36%という3つの異なる調査質問への回答率)と、今回の再現性Trialで得た知見を突き合わせた評価です。</p>
  <div class="callout">
    <h4>Pattern C — 構造的に適用困難</h4>
    <p>No.9のPoint Twoは3つの異なる調査質問(3つの独立したFact)であり、No.18のような「同一指標の2条件間の差」という
    自然な差分が存在しません。加えて、今回発見した「baseline単独でも異なるFactを1つの概数へ統合してしまう」という
    リスクは、survey型記事でこそ深刻化しやすく、Pattern Cを機械的に適用するとFact混同を助長する危険があります。</p>
  </div>
  <div class="callout">
    <h4>Pattern A / B — 概念的に適用可能、ただし要注意</h4>
    <p>「代表指標を1つ選ぶ」(A)や「結論を先に述べ、数字の必要性を判定する」(B)という考え方自体はsurvey型にも
    転用できますが、3つの質問のうちどれを「代表」または「必要」と判定するかという追加の編集判断が発生し、
    No.18の2条件比較よりも恣意性のリスクが高くなります。</p>
  </div>
</section>

<section id="rank">
  <h2>Claude推奨順位(採用判断ではありません)</h2>
  <ol class="rank-list">
    <li><span class="rank-num">1</span><div><strong>Pattern C</strong> — 5/5 runでcore変換(差分約9/約10)が完全に安定・数値正確。記事全体への副作用も他Patternと同水準。</div></li>
    <li><span class="rank-num">2</span><div><strong>Pattern A</strong> — 5/5 runで代表指標保持+trend文が安定。Ledger MINOR指摘はF-005/F-006と無関係な既存Hook文のみ。</div></li>
    <li><span class="rank-num">3</span><div><strong>Pattern B</strong> — 5/5 runで安定・Ledger指摘0件と最もクリーンだが、「結論優先」の効果はA/Cほど明確に数値化しにくい。</div></li>
  </ol>
  <p class="section-sub">最終的な採用判断はユーザーに委ねます。Status: <strong>USER_DECISION_REQUIRED</strong>。</p>
</section>

<footer>
  <p>ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-REPRODUCIBILITY-TRIAL-19 / 生成日: 2026-09-03 / Production Prompt・CURRENT_SPEC・No.18 article.md・TTSへの変更は一切なし。</p>
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
