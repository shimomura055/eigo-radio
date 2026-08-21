# ============================================================
# er006_pool_pilot_01_build_review.py
# ER-006-POOL-PILOT-01: Human Review Artifact(トピック別HTML)生成
# ============================================================
from __future__ import annotations

import base64
import html
import json
import re

SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"

review_data = json.load(open(f"{SCRATCH}/review_data.json", encoding="utf-8"))
cost = json.load(open("er006_output/pool_pilot_01/cost_time_summary.json", encoding="utf-8"))
time_data = json.load(open("er006_output/pool_pilot_01/time_summary.json", encoding="utf-8"))

TOPIC_META = {
    "pool_benches": {
        "title_en": "Why Are More Cities Rethinking Public Benches?",
        "title_ja": "公共のベンチ、なぜ今見直されているのか",
        "category": "社会・暮らし", "code": "ER-006-POOL-001",
    },
    "pool_subscriptions": {
        "title_en": "Why Do Companies Make Subscriptions So Easy to Start—and Hard to Stop?",
        "title_ja": "なぜ契約は簡単で、解約は難しいのか",
        "category": "ビジネス", "code": "ER-006-POOL-002",
    },
    "pool_startups": {
        "title_en": "Why Do Some Startups Chase Growth Before Profit?",
        "title_ja": "なぜ一部のスタートアップは利益より成長を優先するのか",
        "category": "スタートアップ", "code": "ER-006-POOL-003",
    },
}

SEVERITY_LABEL = {"MAJOR": "MAJOR", "MINOR": "MINOR"}


def md_to_html(text: str) -> str:
    lines = text.strip().split("\n")
    out = []
    for ln in lines:
        ln = ln.rstrip()
        if not ln:
            out.append("")
            continue
        if ln.startswith("# "):
            out.append(f"<h3>{html.escape(ln[2:])}</h3>")
        elif ln.startswith("## "):
            out.append(f"<h4>{html.escape(ln[3:])}</h4>")
        else:
            t = html.escape(ln)
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
            out.append(f"<p>{t}</p>")
    return "\n".join(out)


def deviation_html(devs: list) -> str:
    if not devs:
        return '<p class="ok-note">Ledger逸脱なし(LEDGER_COMPLIANT)</p>'
    rows = []
    for d in devs:
        sev = d.get("severity", "?")
        claim = d.get("claim_in_article", "")
        issue = d.get("issue", "")
        rows.append(f'''<li class="dev-item sev-{sev.lower()}">
          <span class="sev-chip sev-{sev.lower()}">{html.escape(sev)}</span>
          <div class="dev-body">
            <div class="dev-claim">{html.escape(str(claim))}</div>
            <div class="dev-issue">{html.escape(str(issue))}</div>
          </div>
        </li>''')
    return f'<ul class="dev-list">{"".join(rows)}</ul>'


def support_fc_html(verdict: str, issues: list) -> str:
    if verdict == "PASS" and not issues:
        return '<p class="ok-note">Support Fact Check: PASS(問題なし)</p>'
    rows = []
    for iss in issues:
        rows.append(f'''<li class="dev-item sev-minor">
          <span class="sev-chip sev-minor">{html.escape(iss.get("severity","MINOR"))}</span>
          <div class="dev-body">
            <div class="dev-claim">{html.escape(iss.get("component",""))}: {html.escape(iss.get("quote",""))}</div>
            <div class="dev-issue">{html.escape(iss.get("description",""))}</div>
          </div>
        </li>''')
    return f'<p class="verdict-line">verdict: {html.escape(verdict or "?")}</p><ul class="dev-list">{"".join(rows)}</ul>'


def stopped_html(segs: list, n_total: int) -> str:
    if not segs:
        return f'<p class="ok-note">全{n_total}セグメントASR検証PASS(STOPPEDなし)</p>'
    chips = "".join(f'<span class="stopped-chip">{html.escape(s)}</span>' for s in segs)
    return (f'<p class="warn-note">{len(segs)}/{n_total}セグメントがSTOPPED'
            f'(最終試行の未検証音声を採用、Human Review対象):</p><div class="stopped-chips">{chips}</div>')


def fmt_jpy(v):
    return f"{v:,.1f}"


def build_level_block(theme, level_key, level_label):
    d = review_data[theme][level_key]
    b64 = base64.b64encode(
        open(f"er006_output/pool_pilot_01/human_review_mp3/{theme}_{'b1b' if level_key=='b1b' else 'a2'}.mp3", "rb").read()
    ).decode("ascii")
    tcost = cost["totals_by_theme"][theme]
    ttime = time_data[theme]
    lvl = "b1" if level_key == "b1b" else "a2"
    needs_review = bool(d["stopped_segments"]) or bool(d["ledger_deviations"]) or (d["support_fc_verdict"] not in (None, "PASS"))
    badge = '<span class="badge badge-review">Needs Review</span>' if needs_review else '<span class="badge badge-ok">Clean</span>'

    return f'''
    <section class="level-card level-{level_key}">
      <div class="level-head">
        <h2>{level_label} {badge}</h2>
      </div>
      <div class="player-box">
        <audio controls preload="none" src="data:audio/mpeg;base64,{b64}"></audio>
      </div>
      <div class="metrics-row">
        <div class="metric"><span class="metric-label">Cost (Level分)</span><span class="metric-value">¥{fmt_jpy(tcost[f"{lvl}_jpy"] if f"{lvl}_jpy" in tcost else tcost.get(f"{level_key}_jpy",0))}</span></div>
        <div class="metric"><span class="metric-label">按分Cost(Shared/2込)</span><span class="metric-value">¥{fmt_jpy(tcost[f"allocated_{lvl}_episode_jpy"])}</span></div>
        <div class="metric"><span class="metric-label">TTS時間</span><span class="metric-value">{ttime[f"tts_{lvl}_sec"]:.0f}秒</span></div>
        <div class="metric"><span class="metric-label">Writer+FC時間</span><span class="metric-value">{ttime[f"writer_{lvl}_sec"]:.0f}秒</span></div>
      </div>

      <details open><summary>Audio QA サマリー</summary>{stopped_html(d["stopped_segments"], d["n_segments"])}</details>
      <details><summary>Writer Fact Check / Ledger Deviation</summary>{deviation_html(d["ledger_deviations"])}</details>
      <details><summary>Support Fact Check</summary>{support_fc_html(d["support_fc_verdict"], d["support_fc_issues"])}</details>
      <details><summary>Script(記事本文)</summary><div class="article-text">{md_to_html(d["article"])}</div></details>
    </section>
    '''


def build_page(theme):
    meta = TOPIC_META[theme]
    tcost = cost["totals_by_theme"][theme]
    ttime = time_data[theme]
    b1_block = build_level_block(theme, "b1b", "B1")
    a2_block = build_level_block(theme, "a2", "A2")

    return f'''<title>{meta["code"]} Human Review</title>
<style>
:root {{
  --paper:#f5f4f0; --ink:#22201c; --ink-soft:#6b675e; --rule:#ddd8cd;
  --card:#fffefb; --accent:#7a5c3e; --accent-soft:#efe6d8;
  --ok:#2f6b4f; --ok-bg:#e2eee5; --warn:#a8710f; --warn-bg:#f5ead2;
  --major:#a5342a; --major-bg:#f6e2df; --minor:#a8710f; --minor-bg:#f5ead2;
  --review:#a5342a; --review-bg:#f6e2df;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#1b1a17; --ink:#ece8e0; --ink-soft:#a8a296; --rule:#3a362e;
    --card:#242220; --accent:#c9a877; --accent-soft:#332c1f;
    --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#d9a94c; --warn-bg:#332a15;
    --major:#e18579; --major-bg:#3a221f; --minor:#d9a94c; --minor-bg:#332a15;
    --review:#e18579; --review-bg:#3a221f;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#1b1a17; --ink:#ece8e0; --ink-soft:#a8a296; --rule:#3a362e;
  --card:#242220; --accent:#c9a877; --accent-soft:#332c1f;
  --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#d9a94c; --warn-bg:#332a15;
  --major:#e18579; --major-bg:#3a221f; --minor:#d9a94c; --minor-bg:#332a15;
  --review:#e18579; --review-bg:#3a221f;
}}
* {{ box-sizing:border-box; }}
body {{ background:var(--paper); color:var(--ink); font-family:-apple-system,"Segoe UI",sans-serif; line-height:1.65; margin:0; }}
.wrap {{ max-width:920px; margin:0 auto; padding:2.5rem 1.5rem 5rem; }}
.eyebrow {{ font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent); font-weight:700; margin:0 0 0.5rem; }}
h1 {{ font-size:1.5rem; margin:0 0 0.3rem; text-wrap:balance; }}
.sub-ja {{ color:var(--ink-soft); font-size:0.95rem; margin:0 0 1.8rem; }}
.shared-bar {{ display:flex; gap:1.2rem; flex-wrap:wrap; background:var(--card); border:1px solid var(--rule); border-radius:10px; padding:1rem 1.3rem; margin-bottom:2rem; font-size:0.82rem; }}
.shared-bar .metric-label {{ color:var(--ink-soft); display:block; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.04em; }}
.shared-bar .metric-value {{ font-variant-numeric:tabular-nums; font-weight:700; }}
.levels {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }}
@media (max-width:760px) {{ .levels {{ grid-template-columns:1fr; }} }}
.level-card {{ background:var(--card); border:1px solid var(--rule); border-radius:12px; padding:1.4rem 1.5rem; }}
.level-head h2 {{ font-size:1.1rem; margin:0 0 1rem; display:flex; align-items:center; gap:0.6rem; }}
.badge {{ font-size:0.68rem; font-weight:700; letter-spacing:0.03em; text-transform:uppercase; padding:0.2rem 0.55rem; border-radius:99px; }}
.badge-ok {{ background:var(--ok-bg); color:var(--ok); }}
.badge-review {{ background:var(--review-bg); color:var(--review); }}
.player-box audio {{ width:100%; }}
.metrics-row {{ display:grid; grid-template-columns:1fr 1fr; gap:0.7rem; margin:1rem 0; font-size:0.78rem; }}
.metric {{ background:var(--accent-soft); border-radius:8px; padding:0.55rem 0.7rem; }}
.metric-label {{ display:block; color:var(--ink-soft); font-size:0.68rem; text-transform:uppercase; letter-spacing:0.03em; }}
.metric-value {{ font-variant-numeric:tabular-nums; font-weight:700; }}
details {{ border-top:1px solid var(--rule); padding:0.7rem 0; }}
summary {{ cursor:pointer; font-size:0.82rem; font-weight:700; color:var(--accent); }}
.ok-note {{ color:var(--ok); font-size:0.82rem; margin:0.6rem 0 0; }}
.warn-note {{ color:var(--warn); font-size:0.82rem; margin:0.6rem 0 0.3rem; }}
.verdict-line {{ font-size:0.78rem; color:var(--ink-soft); margin:0.6rem 0 0.4rem; }}
.stopped-chips {{ display:flex; flex-wrap:wrap; gap:0.4rem; }}
.stopped-chip {{ font-size:0.72rem; background:var(--major-bg); color:var(--major); padding:0.2rem 0.5rem; border-radius:6px; font-family:monospace; }}
.dev-list {{ list-style:none; margin:0.6rem 0 0; padding:0; display:flex; flex-direction:column; gap:0.6rem; }}
.dev-item {{ display:flex; gap:0.6rem; font-size:0.8rem; }}
.sev-chip {{ flex-shrink:0; font-size:0.65rem; font-weight:700; padding:0.15rem 0.4rem; border-radius:5px; height:fit-content; }}
.sev-chip.sev-major {{ background:var(--major-bg); color:var(--major); }}
.sev-chip.sev-minor {{ background:var(--minor-bg); color:var(--minor); }}
.dev-claim {{ font-style:italic; color:var(--ink); }}
.dev-issue {{ color:var(--ink-soft); margin-top:0.2rem; }}
.article-text {{ font-size:0.85rem; }}
.article-text h3 {{ font-size:1rem; }}
.article-text h4 {{ font-size:0.9rem; color:var(--accent); }}
footer {{ margin-top:2.5rem; font-size:0.72rem; color:var(--ink-soft); text-align:center; }}
</style>
<div class="wrap">
  <p class="eyebrow">ER-006-POOL-PILOT-01 · Human Review · {meta["category"]} · {meta["code"]}</p>
  <h1>{html.escape(meta["title_en"])}</h1>
  <p class="sub-ja">{html.escape(meta["title_ja"])}</p>

  <div class="shared-bar">
    <div class="metric"><span class="metric-label">Actual Pair Production Cost</span><span class="metric-value">¥{fmt_jpy(tcost["actual_pair_production_jpy"])}</span></div>
    <div class="metric"><span class="metric-label">Shared Research Cost</span><span class="metric-value">¥{fmt_jpy(tcost["shared_jpy"])}</span></div>
    <div class="metric"><span class="metric-label">Article-specific Rewrite Waste</span><span class="metric-value">¥{fmt_jpy(tcost["rewrite_waste_jpy"])}</span></div>
    <div class="metric"><span class="metric-label">Research時間</span><span class="metric-value">{ttime["research_total_sec"]:.0f}秒</span></div>
    <div class="metric"><span class="metric-label">Stage合計時間(Clean run)</span><span class="metric-value">{ttime["stage_sum_min_CLEAN_RUN_ONLY"]:.1f}分</span></div>
  </div>

  <div class="levels">
    {b1_block}
    {a2_block}
  </div>

  <footer>ER-006-POOL-PILOT-01 · Claude Code生成 · Subjective PASS判定はユーザー確認待ち(Claudeは確定させない)</footer>
</div>
'''


import os
os.makedirs(f"{SCRATCH}/er006_review", exist_ok=True)
for theme in TOPIC_META:
    page = build_page(theme)
    path = f"{SCRATCH}/er006_review/{theme}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(theme, len(page), "chars ->", path)
