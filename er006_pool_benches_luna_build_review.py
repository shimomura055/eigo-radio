# ============================================================
# er006_pool_benches_luna_build_review.py
# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Human Review Artifact生成
# ============================================================
from __future__ import annotations

import base64
import html
import json
import re

SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"
MP3_DIR = "er006_output/pool_pilot_01/human_review_mp3"

cost = json.load(open("er006_output/pool_pilot_01/pool_benches_sol_vs_luna_cost.json", encoding="utf-8"))


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def md_to_html(text):
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
        elif ln.startswith("### "):
            out.append(f"<h5>{html.escape(ln[4:])}</h5>")
        else:
            t = html.escape(ln)
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
            out.append(f"<p>{t}</p>")
    return "\n".join(out)


BASE_CSS = """
<style>
:root {
  --paper:#f5f4f0; --ink:#22201c; --ink-soft:#6b675e; --rule:#ddd8cd;
  --card:#fffefb; --accent:#7a5c3e; --accent-soft:#efe6d8;
  --sol:#a5342a; --sol-bg:#f6e2df; --luna:#2f6b8f; --luna-bg:#e2edf4;
  --ok:#2f6b4f; --ok-bg:#e2eee5; --warn:#a8710f; --warn-bg:#f5ead2;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:#1b1a17; --ink:#ece8e0; --ink-soft:#a8a296; --rule:#3a362e;
    --card:#242220; --accent:#c9a877; --accent-soft:#332c1f;
    --sol:#e18579; --sol-bg:#3a221f; --luna:#7fb8de; --luna-bg:#1c2c38;
    --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#d9a94c; --warn-bg:#332a15;
  }
}
:root[data-theme="dark"] {
  --paper:#1b1a17; --ink:#ece8e0; --ink-soft:#a8a296; --rule:#3a362e;
  --card:#242220; --accent:#c9a877; --accent-soft:#332c1f;
  --sol:#e18579; --sol-bg:#3a221f; --luna:#7fb8de; --luna-bg:#1c2c38;
  --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#d9a94c; --warn-bg:#332a15;
}
* { box-sizing:border-box; }
body { background:var(--paper); color:var(--ink); font-family:-apple-system,"Segoe UI",sans-serif; line-height:1.65; margin:0; }
.wrap { max-width:960px; margin:0 auto; padding:2.5rem 1.5rem 5rem; }
.eyebrow { font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent); font-weight:700; margin:0 0 0.5rem; }
h1 { font-size:1.5rem; margin:0 0 1.5rem; text-wrap:balance; }
.cols { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
@media (max-width:760px) { .cols { grid-template-columns:1fr; } }
.card { background:var(--card); border:1px solid var(--rule); border-radius:12px; padding:1.4rem 1.5rem; }
.card.sol { border-top:4px solid var(--sol); }
.card.luna { border-top:4px solid var(--luna); }
.card h2 { font-size:1.05rem; margin:0 0 1rem; display:flex; align-items:center; gap:0.5rem; }
.tag { font-size:0.65rem; font-weight:700; letter-spacing:0.03em; text-transform:uppercase; padding:0.15rem 0.5rem; border-radius:99px; }
.tag.sol { background:var(--sol-bg); color:var(--sol); }
.tag.luna { background:var(--luna-bg); color:var(--luna); }
audio { width:100%; margin-bottom:0.8rem; }
.metrics-row { display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin:0.8rem 0; font-size:0.76rem; }
.metric { background:var(--accent-soft); border-radius:8px; padding:0.5rem 0.6rem; }
.metric-label { display:block; color:var(--ink-soft); font-size:0.65rem; text-transform:uppercase; letter-spacing:0.03em; }
.metric-value { font-variant-numeric:tabular-nums; font-weight:700; }
details { border-top:1px solid var(--rule); padding:0.6rem 0; margin-top:0.6rem; }
summary { cursor:pointer; font-size:0.8rem; font-weight:700; color:var(--accent); }
.ok-note { color:var(--ok); font-size:0.8rem; }
.warn-note { color:var(--warn); font-size:0.8rem; }
.stopped-chip { display:inline-block; font-size:0.68rem; background:var(--warn-bg); color:var(--warn); padding:0.15rem 0.45rem; border-radius:6px; font-family:monospace; margin:0.15rem 0.2rem 0 0; }
.dev-item { font-size:0.78rem; margin:0.5rem 0; padding-left:0.6rem; border-left:2px solid var(--warn); }
.article-text { font-size:0.84rem; }
.article-text h3 { font-size:0.98rem; }
.article-text h4, .article-text h5 { font-size:0.88rem; color:var(--accent); }
footer { margin-top:2.5rem; font-size:0.72rem; color:var(--ink-soft); text-align:center; }
table.cost { width:100%; border-collapse:collapse; font-size:0.8rem; margin-top:0.6rem; }
table.cost th, table.cost td { text-align:right; padding:0.3rem 0.4rem; border-bottom:1px solid var(--rule); font-variant-numeric:tabular-nums; }
table.cost th:first-child, table.cost td:first-child { text-align:left; }
.clip-card { background:var(--card); border:1px solid var(--rule); border-radius:10px; padding:1rem 1.2rem; margin-bottom:1rem; }
.clip-card h3 { font-size:0.9rem; margin:0 0 0.5rem; }
.clip-meta { font-size:0.76rem; color:var(--ink-soft); margin-top:0.4rem; }
</style>
"""


def build_level_page(level_key, level_label, out_dir):
    sol_dir = "b1b" if level_key == "b1" else "a2"
    sol_article = open(f"er006_output/pool_pilot_01/pool_benches/{sol_dir}/article.md", encoding="utf-8").read()
    luna_article = open(f"er006_output/pool_pilot_01/pool_benches_luna/{sol_dir}/article.md", encoding="utf-8").read()

    sol_ld = json.load(open(f"er006_output/pool_pilot_01/pool_benches/{sol_dir}/ledger_deviation.json", encoding="utf-8"))
    luna_ld = json.load(open(f"er006_output/pool_pilot_01/pool_benches_luna/{sol_dir}/ledger_deviation.json", encoding="utf-8"))
    sol_fq = json.load(open(f"er006_output/pool_pilot_01/pool_benches/{sol_dir}/fact_qa.json", encoding="utf-8"))
    luna_fq = json.load(open(f"er006_output/pool_pilot_01/pool_benches_luna/{sol_dir}/fact_qa.json", encoding="utf-8"))

    sol_audio = b64(f"{MP3_DIR}/pool_benches_{level_key if level_key=='a2' else 'b1b'}.mp3")
    luna_audio = b64(f"{MP3_DIR}/pool_benches_luna_{sol_dir}.mp3")

    sol_cost = cost["sol"]["by_level"][level_key]
    luna_cost = cost["luna"]["by_level"][level_key]
    sol_stopped = cost["sol"]["stopped_and_uncertain"][level_key]
    luna_stopped = cost["luna"]["stopped_and_uncertain"][level_key]

    def dev_html(ld):
        devs = ld.get("deviations", [])
        if not devs:
            return '<p class="ok-note">Ledger逸脱なし(LEDGER_COMPLIANT)</p>'
        rows = []
        for d in devs:
            rows.append(f'<div class="dev-item"><strong>{html.escape(d.get("severity",""))}</strong> '
                        f'{html.escape(str(d.get("issue",""))[:200])}</div>')
        return "".join(rows)

    def stopped_html(s):
        chips = "".join(f'<span class="stopped-chip">{html.escape(x)}</span>' for x in s["stopped"])
        uchips = "".join(f'<span class="stopped-chip" style="background:var(--luna-bg);color:var(--luna)">{html.escape(x)}(UNCERTAIN)</span>' for x in s["uncertain"])
        if not chips and not uchips:
            return '<p class="ok-note">STOPPED/UNCERTAINなし</p>'
        return f'<div>{chips}{uchips}</div>'

    def cost_table(sol_c, luna_c):
        rows = []
        for label, key in [("Writer(+FC/Deviation)", "writer_jpy"), ("Support(+KP/FC)", "support_jpy"),
                            ("Audio TTS", "audio_tts_jpy"), ("Audio ASR", "audio_asr_jpy")]:
            rows.append(f"<tr><th>{label}</th><td>¥{sol_c.get(key,0):.1f}</td><td>¥{luna_c.get(key,0):.1f}</td></tr>")
        sol_total = sum(sol_c.values())
        luna_total = sum(luna_c.values())
        rows.append(f"<tr><th>合計</th><td><strong>¥{sol_total:.1f}</strong></td><td><strong>¥{luna_total:.1f}</strong></td></tr>")
        return (f'<table class="cost"><tr><th></th><th>Sol(実費)</th><th>Luna(実費)</th></tr>{"".join(rows)}</table>')

    page = f'''<title>Public Benches {level_label} Sol vs Luna</title>
{BASE_CSS}
<div class="wrap">
  <p class="eyebrow">ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 · Human Review</p>
  <h1>Public Benches — {level_label}: Sol版 vs Luna版</h1>

  <div class="cols">
    <div class="card sol">
      <h2>Sol版(旧、履歴実費) <span class="tag sol">gpt-5.6-sol</span></h2>
      <audio controls preload="none" src="data:audio/mpeg;base64,{sol_audio}"></audio>
      <details open><summary>Audio QA(STOPPED/UNCERTAIN)</summary>{stopped_html(sol_stopped)}</details>
      <details><summary>Writer Fact Check</summary><p>verdict: {html.escape(str((sol_fq.get("result") or {}).get("verdict")))}</p></details>
      <details><summary>Ledger Deviation</summary>{dev_html(sol_ld)}</details>
      <details><summary>Script</summary><div class="article-text">{md_to_html(sol_article)}</div></details>
    </div>
    <div class="card luna">
      <h2>Luna版(新) <span class="tag luna">gpt-5.6-luna</span></h2>
      <audio controls preload="none" src="data:audio/mpeg;base64,{luna_audio}"></audio>
      <details open><summary>Audio QA(STOPPED/UNCERTAIN)</summary>{stopped_html(luna_stopped)}</details>
      <details><summary>Writer Fact Check</summary><p>verdict: {html.escape(str((luna_fq.get("result") or {}).get("verdict")))}</p></details>
      <details><summary>Ledger Deviation</summary>{dev_html(luna_ld)}</details>
      <details><summary>Script</summary><div class="article-text">{md_to_html(luna_article)}</div></details>
    </div>
  </div>

  <div class="card" style="margin-top:1.5rem;">
    <h2>Cost比較(実測、按分なし)</h2>
    {cost_table(sol_cost, luna_cost)}
    <p style="font-size:0.72rem;color:var(--ink-soft);margin-top:0.6rem;">Sol版のWriter Costには過去のRewrite(出典修正による再実行)分を含む。
    Luna版はResearchを再利用しており新規Research費用は発生していない(別途0円)。</p>
  </div>

  <footer>ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 · Claude Code生成 · 主観的な自然さ・品質の最終判断はユーザーが行う</footer>
</div>
'''
    path = f"{out_dir}/pool_benches_{level_key}_sol_vs_luna.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(level_key, len(page), "chars ->", path)


def build_hostile_page(out_dir):
    clips = [
        ("sol_b1_kp1", "Sol B1 — hostile architecture", "旧Sol版B1のKey Phrase 1(元々ユーザーが/h/→/p/を指摘した音声)"),
        ("sol_a2_kp1", "Sol A2 — hostile architecture", "旧Sol版A2のKey Phrase 1(独立した別生成)"),
        ("luna_b1_kp1", "Luna B1 — hostile architecture", "新Luna版B1のKey Phrase 1(独立した別生成、5サンプル中で最も立ち上がりが滑らか)"),
        ("hostile_repeat1", "診断: hostile architecture (再生成1)", "本番同一条件での追加生成。ASRが先頭に\u201cA\u201d(幻聴的な語)を追加した実例"),
        ("hostile_repeat2", "診断: hostile architecture (再生成2)", "本番同一条件での追加生成、クリーンな例"),
        ("hidden_cost", "診断: hidden cost(比較用/h/開始語)", "hostile固有ではなく/h/開始語全般の傾向かを確認するための比較サンプル"),
        ("happy_ending", "診断: happy ending(比較用/h/開始語)", "同上。5サンプル中で最も急峻な立ち上がり(4.69倍)を示した"),
    ]
    clip_html = []
    for name, title, desc in clips:
        audio = b64(f"{MP3_DIR}/hostile_diag/{name}.mp3")
        clip_html.append(f'''<div class="clip-card">
          <h3>{html.escape(title)}</h3>
          <audio controls preload="none" src="data:audio/mpeg;base64,{audio}"></audio>
          <div class="clip-meta">{html.escape(desc)}</div>
        </div>''')

    page = f'''<title>Hostile Architecture Pronunciation Diagnostic</title>
{BASE_CSS}
<div class="wrap">
  <p class="eyebrow">ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 · Human Review</p>
  <h1>Key Phrase "hostile architecture" 発音問題の診断音声</h1>
  <p style="color:var(--ink-soft);font-size:0.85rem;">ユーザーHuman Reviewで報告された「語頭/h/が/p/のように聞こえる」問題について、
  Sol版・Luna版・追加診断生成(比較用の別/h/語含む)を独立生成ごとに聴き比べられるようにした。
  ASRは全サンプルで"Hostile architecture."と正しく書き起こしており、ASR一致だけでは
  この問題を検出できないことを示す実例でもある。主観的な発音品質の最終判定はユーザーが行う。</p>

  {"".join(clip_html)}

  <footer>ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 · Claude Code生成</footer>
</div>
'''
    path = f"{out_dir}/hostile_architecture_diagnostic.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print("hostile", len(page), "chars ->", path)


if __name__ == "__main__":
    import os
    out_dir = f"{SCRATCH}/luna_review"
    os.makedirs(out_dir, exist_ok=True)
    build_level_page("b1", "B1", out_dir)
    build_level_page("a2", "A2", out_dir)
    build_hostile_page(out_dir)
