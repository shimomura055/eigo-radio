# ============================================================
# er008_n8_final_artifact_24_build.py
# ER-008-N8-FINAL-CLOSEOUT-24: No.8最終試聴用Artifact HTMLをビルドする
# (音声をbase64 data URIとして埋め込む、一回限りのビルドスクリプト)
# ============================================================
import base64
import html as html_lib
import json
import re

import er003_v1_n3_01_articles_generate as gen

BASE = "er006_output/pool_pilot_01/pool_n8_airport_line"
OUT_HTML = ("C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/"
            "4559ebbb-f749-4719-a4c4-1a5c91891e44/scratchpad/n8_final_listening_24.html")


def b64_audio(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def inline_md_to_html(text: str) -> str:
    escaped = html_lib.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def paragraphs_html(text: str) -> str:
    paras = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "\n".join(f"<p>{inline_md_to_html(p)}</p>" for p in paras)


def build_script_html(article_path: str) -> str:
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    title_match = re.match(r"^#\s+(.+?)\s*\n", article_text)
    title = title_match.group(1) if title_match else ""
    sections = gen.split_common_sections_for_point_qa(article_text)
    in_one_line_match = re.search(r"^##\s+In one line[^\n]*\n+(.+)", article_text,
                                   flags=re.MULTILINE | re.DOTALL)
    in_one_line_text = in_one_line_match.group(1).strip() if in_one_line_match else ""
    return f"""<details class="script">
      <summary>スクリプトを表示</summary>
      <div class="script-body">
        <h4 class="script-title">{inline_md_to_html(title)}</h4>
        {paragraphs_html(sections["full_story"])}
        <div class="script-point">
          <span class="point-label">Point One</span>
          <p class="script-point-heading">{inline_md_to_html(sections["point_one_heading"])}</p>
          {paragraphs_html(sections["point_one_body"])}
        </div>
        <div class="script-point">
          <span class="point-label">Point Two</span>
          <p class="script-point-heading">{inline_md_to_html(sections["point_two_heading"])}</p>
          {paragraphs_html(sections["point_two_body"])}
        </div>
        <p class="script-in-one-line">{inline_md_to_html(in_one_line_text)}</p>
      </div>
    </details>"""


a2_audio = b64_audio(f"{BASE}/a2/assembled/English_Your_Way_A2_POOL_N8_AIRPORT_LINE.mp3")
b1_audio = b64_audio(f"{BASE}/b1b/assembled/English_Your_Way_B1B_POOL_N8_AIRPORT_LINE.mp3")
a2_script_html = build_script_html(f"{BASE}/a2/article.md")
b1_script_html = build_script_html(f"{BASE}/b1b/article.md")

with open("er008_output/n8_location_compression_24_summary.json", encoding="utf-8") as f:
    loc_summary = json.load(f)

a2_dur = loc_summary["assemble"]["a2"]["duration_seconds"]
b1_dur = loc_summary["assemble"]["b1"]["duration_seconds"]
a2_peak = loc_summary["assemble"]["a2"]["peak"]
b1_peak = loc_summary["assemble"]["b1"]["peak"]


def fmt_mmss(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return f"{m}:{s:02d}"


HTML_TEMPLATE = """<title>No.8 Airport Line — Final Check</title>
<style>
:root {{
  --bg: #f6f5f1;
  --surface: #ffffff;
  --surface-alt: #edeae2;
  --text: #1d2024;
  --text-muted: #5b6169;
  --border: #e1ddd2;
  --accent: #2b5f8a;
  --accent-soft: #e4eef5;
  --good: #2e7d5b;
  --good-soft: #e3f2ea;
  --warn: #a8721f;
  --warn-soft: #f6ecd9;
  --font-display: "Source Serif 4", Georgia, "Hiragino Mincho ProN", serif;
  --font-body: "IBM Plex Sans", "Hiragino Sans", "Yu Gothic", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #15181b;
    --surface: #1c2024;
    --surface-alt: #22262b;
    --text: #e8e6e1;
    --text-muted: #9aa0a6;
    --border: #2c3238;
    --accent: #7fb0da;
    --accent-soft: #1f3141;
    --good: #6cc39b;
    --good-soft: #1c3129;
    --warn: #e0b15c;
    --warn-soft: #3a3020;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #15181b;
  --surface: #1c2024;
  --surface-alt: #22262b;
  --text: #e8e6e1;
  --text-muted: #9aa0a6;
  --border: #2c3238;
  --accent: #7fb0da;
  --accent-soft: #1f3141;
  --good: #6cc39b;
  --good-soft: #1c3129;
  --warn: #e0b15c;
  --warn-soft: #3a3020;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{
  max-width: 760px;
  margin: 0 auto;
  padding: 48px 24px 96px;
}}
header.page {{
  margin-bottom: 40px;
}}
.eyebrow {{
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 10px;
}}
h1 {{
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 38px);
  margin: 0 0 12px;
  text-wrap: balance;
  font-weight: 600;
}}
.lede {{
  color: var(--text-muted);
  font-size: 15.5px;
  max-width: 60ch;
}}
section {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px 28px 30px;
  margin-bottom: 22px;
}}
section h2 {{
  font-family: var(--font-display);
  font-size: 20px;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
section h2 .num {{
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 9px;
}}
p {{ margin: 0 0 12px; }}
.pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--good-soft);
  color: var(--good);
  font-weight: 600;
  white-space: nowrap;
}}
.pill.warn {{ background: var(--warn-soft); color: var(--warn); }}
.pill.accent {{ background: var(--accent-soft); color: var(--accent); }}
.player-block {{
  background: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 14px;
}}
.player-block:last-child {{ margin-bottom: 0; }}
.player-head {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}}
.player-head h3 {{
  font-family: var(--font-display);
  font-size: 17px;
  margin: 0;
}}
.player-stats {{
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}}
audio {{ width: 100%; height: 40px; display: block; }}
details.script {{ margin-top: 14px; }}
details.script summary {{
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--accent);
  user-select: none;
  list-style: none;
}}
details.script summary::-webkit-details-marker {{ display: none; }}
details.script summary::before {{ content: "▸ "; }}
details.script[open] summary::before {{ content: "▾ "; }}
.script-body {{
  margin-top: 14px;
  padding: 18px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
}}
.script-body p {{ margin: 0 0 12px; }}
.script-title {{
  font-family: var(--font-display);
  font-size: 16px;
  margin: 0 0 14px;
}}
.script-point {{
  margin: 16px 0;
  padding-left: 14px;
  border-left: 3px solid var(--accent-soft);
}}
.point-label {{
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  background: var(--accent-soft);
  border-radius: 999px;
  padding: 2px 9px;
  margin-bottom: 6px;
}}
.script-point-heading {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 14.5px;
  margin: 4px 0 8px !important;
}}
.script-in-one-line {{
  font-style: italic;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
  padding-top: 12px;
  margin-top: 4px !important;
}}
.changed-list {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.changed-list li {{
  border-left: 3px solid var(--accent);
  padding: 6px 0 6px 14px;
  font-size: 14px;
}}
.diff {{
  font-family: var(--font-mono);
  font-size: 12.5px;
  line-height: 1.7;
  overflow-x: auto;
}}
.diff .old {{ color: var(--warn); text-decoration: line-through; opacity: 0.75; }}
.diff .new {{ color: var(--good); font-weight: 600; }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}}
th, td {{
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
}}
th {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
}}
td.num, th.num {{ font-family: var(--font-mono); text-align: right; font-variant-numeric: tabular-nums; }}
.table-wrap {{ overflow-x: auto; margin-bottom: 10px; }}
.note {{
  background: var(--accent-soft);
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 13.5px;
  color: var(--text);
}}
.note.warn {{ background: var(--warn-soft); }}
.status-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}}
@media (max-width: 560px) {{ .status-grid {{ grid-template-columns: 1fr; }} }}
.status-item {{
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
}}
.status-item .label {{ color: var(--text-muted); font-size: 11.5px; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 4px; }}
footer.page {{
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 36px;
  font-family: var(--font-mono);
}}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">

<div class="wrap">
  <header class="page">
    <div class="eyebrow">ER-008-N8-FINAL-CLOSEOUT-24 &middot; 最終試聴チェック</div>
    <h1>No.8 — The Airport Line That Starts Before It Needs To</h1>
    <p class="lede">地名・施設名Compression("Dallas Fort Worth International Airport" &rarr; "Dallas Fort Worth")を反映し、影響segmentのみ再TTS・再Assembleした完成版です。他の内容(発音・話速・disfluency QA等)はNo.8のこれまでの承認済み仕様のまま変更していません。</p>
  </header>

  <section>
    <h2><span class="num">1</span>今回変更した箇所</h2>
    <ul class="changed-list">
      <li>A2 Full Story Part2、B1 Full Story Part2、B1 In One Line の3segmentのみ再TTS・再ASR検証(いずれも <span class="pill">asr_verified</span>)。Point One/Two・Title・Comment等、他のsegmentは無変更のため再生成していません。</li>
    </ul>
    <div class="diff" style="margin-top:16px">
      <span class="old">Dallas Fort Worth International Airport</span> &rarr; <span class="new">Dallas Fort Worth</span>
    </div>
  </section>

  <section>
    <h2><span class="num">2</span>試聴</h2>
    <div class="player-block">
      <div class="player-head">
        <h3>A2</h3>
        <span class="player-stats">{a2_dur_fmt} &middot; peak {a2_peak:.2f} &middot; clipping なし</span>
      </div>
      <audio controls preload="none" src="data:audio/mpeg;base64,{a2_audio}"></audio>
      {a2_script_html}
    </div>
    <div class="player-block">
      <div class="player-head">
        <h3>B1</h3>
        <span class="player-stats">{b1_dur_fmt} &middot; peak {b1_peak:.2f} &middot; clipping なし</span>
      </div>
      <audio controls preload="none" src="data:audio/mpeg;base64,{b1_audio}"></audio>
      {b1_script_html}
    </div>
  </section>

  <section>
    <h2><span class="num">3</span>Writer Point Prompt強化(実API A/B比較、各n=4)</h2>
    <p>No.8の実Topic・実Verified Fact Ledgerを使い、強化前/後のprompt each 4回、実Writer APIで生成し、Point-Full Story lexical overlap率を比較しました。</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>条件</th><th class="num">平均overlap</th><th class="num">最大overlap</th><th class="num">要retry率(&ge;0.40)</th></tr></thead>
        <tbody>
          <tr><td>強化前(OLD)</td><td class="num">0.293</td><td class="num">0.538</td><td class="num">25%(4件中1件)</td></tr>
          <tr><td>強化後(NEW)</td><td class="num">0.244</td><td class="num">0.320</td><td class="num">0%(4件中0件)</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">サンプル数が小さいため(各4件)傾向の確認に留まりますが、方向は狙い通りでした。強化前の高overlap事例(0.538)はFull Storyの電子ゲート機能説明をほぼ再掲していたのに対し、強化後の一例は同じFactに対し「これは航空会社自身の自己申告であり、独立した効果検証は示されていない」という一段深めた視点を新Fact追加なしで加えていました。</p>
  </section>

  <section>
    <h2><span class="num">4</span>Point overlap retryコストの訂正</h2>
    <p>共有のcost計算モジュール(<code>er005_stage7_cost_compute.py</code>)に、実際のmodel(<code>gpt-5.6-luna</code>)ではなく常に<code>gpt-5.6-sol</code>単価(約25倍高い)で計算するバグを発見し、修正しました。</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>項目</th><th class="num">訂正前(誤)</th><th class="num">訂正後(正)</th></tr></thead>
        <tbody>
          <tr><td>Point overlap retry 1回の<strong>純増分</strong>コスト</td><td class="num">$0.7861 <span class="pill warn">誤</span></td><td class="num">約$0.005</td></tr>
          <tr><td>記事1本の基本コスト(Writer+EC Editor+Fact Check+Deviation)</td><td class="num">&mdash;</td><td class="num">約$0.111</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note warn">Fact Checker・Ledger Deviation Checkは記事1本につき必ず1回発生する固定costであり、retryの有無に関わらず変わりません。旧$0.7861は「retryを含む記事1本の総コスト」に近い数字で、「retry自体の増分コスト」ではありませんでした。</p>
  </section>

  <section>
    <h2><span class="num">5</span>Stephen Reicher発音</h2>
    <p>ユーザーが再試聴し、現在の音声は <span class="pill accent">/aɪ/寄り(RY-ker)</span> に聞こえると判断。既存音声をPASSとし、再生成していません。Pronunciation Ledgerのconfidenceは根拠の性質(音声ではなくテキスト書き起こし由来)を反映し"medium"のまま維持し、今回のユーザー確認内容を追記しました。</p>
  </section>

  <section>
    <h2><span class="num">6</span>Status</h2>
    <div class="status-grid">
      <div class="status-item"><div class="label">Production Wired</div>地名/施設名Compressionロジック・No.8適用・Writer Point Prompt強化・Point overlap Writer retry</div>
      <div class="status-item"><div class="label">Decided(現状維持)</div>A2 In One Line速度(OPEN-91、追加TTSなし)</div>
      <div class="status-item"><div class="label">Open(TBD)</div>Fact Checkerのライブ検索非決定性(OPEN-92)</div>
      <div class="status-item"><div class="label">Reicher</div>ユーザー確認済み・PASS確定</div>
    </div>
  </section>

  <footer class="page">eigo-radio &middot; ER-008-N8-FINAL-CLOSEOUT-24 &middot; {generated_at}</footer>
</div>
"""

import datetime

html = HTML_TEMPLATE.format(
    a2_dur_fmt=fmt_mmss(a2_dur), b1_dur_fmt=fmt_mmss(b1_dur),
    a2_peak=a2_peak, b1_peak=b1_peak,
    a2_audio=a2_audio, b1_audio=b1_audio,
    a2_script_html=a2_script_html, b1_script_html=b1_script_html,
    generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
)

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("wrote", OUT_HTML, len(html), "bytes")
