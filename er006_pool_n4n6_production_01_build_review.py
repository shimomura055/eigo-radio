# -*- coding: utf-8 -*-
import base64, html, json, os

data = json.load(open("er006_output/pool_pilot_01/adoption_audit_01/review_data_n4n6.json", encoding="utf-8"))
MP3_MAP = {
    ("n4_supermarket", "b1"): "er006_output/pool_pilot_01/human_review_mp3_n4n6/n4_supermarket_b1b.mp3",
    ("n4_supermarket", "a2"): "er006_output/pool_pilot_01/human_review_mp3_n4n6/n4_supermarket_a2.mp3",
}


def esc(t):
    return html.escape(t or "")


def para(t):
    if not t:
        return ""
    return "".join(f"<p>{esc(p)}</p>" for p in t.split("\n\n"))


def kp_html(kps):
    items = "".join(
        f'<li><span class="kp-rank">{i["rank"]}</span><span class="kp-en">{esc(i["en"])}</span>'
        f'<span class="kp-ja">{esc(i["ja"])}</span></li>' for i in kps)
    return f'<ol class="kp-list">{items}</ol>'


def seg(name, label, text, stopped_set, lang_class="en"):
    warn = ""
    if name in stopped_set:
        warn = ('<div class="stopped-warn">⚠ この区間はASR自動検証が未合格のまま採用されています'
                '(理由は差分記録を参照)。実際に聞いて内容に問題がないか確認してください。</div>')
    return f'''<div class="seg seg-{name}">
      <div class="seg-label">{esc(label)}</div>
      {warn}
      <div class="seg-text {lang_class}">{para(text)}</div>
    </div>'''


def level_block(topic_key, level, ld):
    mp3_path = MP3_MAP[(topic_key, level)]
    with open(mp3_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    stopped = set(ld["stopped_segments"])
    level_label = "B1" if level == "b1" else "A2"
    lang_class = "en" if level == "b1" else "ja"

    segs = []
    segs.append(seg("preview", "Preview", ld["preview"], stopped, "ja" if level == "a2" else "en"))
    segs.append(f'<div class="seg seg-key_phrases"><div class="seg-label">Key Phrases</div>{kp_html(ld["key_phrases"])}</div>')
    segs.append(seg("comment_1", "Comment 1", ld["comment_1"], stopped, lang_class if level == "b1" else "ja"))
    segs.append(seg("full_story_part1", "Full Story — Part 1", ld["full_story_part1"], stopped, "en"))
    segs.append(seg("comment_2", "Comment 2", ld["comment_2"], stopped, lang_class if level == "b1" else "ja"))
    segs.append(seg("full_story_part2", "Full Story — Part 2", ld["full_story_part2"], stopped, "en"))
    segs.append(seg("comment_3", "Comment 3", ld["comment_3"], stopped, lang_class if level == "b1" else "ja"))
    segs.append(seg("point_one", "Point One — " + (ld["point_one_heading"] or ""), ld["point_one_body"], stopped, "en"))
    segs.append(seg("point_two", "Point Two — " + (ld["point_two_heading"] or ""), ld["point_two_body"], stopped, "en"))
    segs.append(seg("comment_4", "Comment 4", ld["comment_4"], stopped, lang_class if level == "b1" else "ja"))
    segs.append(seg("in_one_line", "In One Line", ld["in_one_line"], stopped, "en"))

    n_stopped = len(stopped)
    status_chip = (f'<span class="chip chip-warn">{n_stopped}区間 要確認</span>' if n_stopped
                    else '<span class="chip chip-ok">全区間 機械検証PASS</span>')

    return f'''
    <section class="level-block">
      <div class="level-head">
        <h2>{level_label} <span class="level-title">{esc(ld["title"])}</span></h2>
        {status_chip}
      </div>
      <div class="player-sticky">
        <audio controls preload="none" src="data:audio/mpeg;base64,{b64}"></audio>
      </div>
      <div class="segs">{"".join(segs)}</div>
    </section>
    '''


def build_page(topic_key, td, title_tag):
    b1 = level_block(topic_key, "b1", td["levels"]["b1"])
    a2 = level_block(topic_key, "a2", td["levels"]["a2"])
    return f'''<title>{title_tag}</title>
<style>
:root {{
  --paper:#f6f3ec; --ink:#232019; --ink-soft:#6f6a5c; --rule:#ddd7c6;
  --card:#fffdf8; --accent:#3d6b66; --accent-soft:#e2ece9;
  --ok:#2f6b4f; --ok-bg:#e2eee5; --warn:#a8560f; --warn-bg:#faeadb;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#191712; --ink:#eae6da; --ink-soft:#a49d8a; --rule:#3a352a;
    --card:#211e18; --accent:#7fbdb5; --accent-soft:#1f2f2c;
    --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#e0a25c; --warn-bg:#33240f;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#191712; --ink:#eae6da; --ink-soft:#a49d8a; --rule:#3a352a;
  --card:#211e18; --accent:#7fbdb5; --accent-soft:#1f2f2c;
  --ok:#7fcf9e; --ok-bg:#1b3025; --warn:#e0a25c; --warn-bg:#33240f;
}}
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;600;700&display=swap');
* {{ box-sizing:border-box; }}
body {{ background:var(--paper); color:var(--ink); font-family:'Inter',-apple-system,"Segoe UI",sans-serif; line-height:1.7; margin:0; }}
.wrap {{ max-width:760px; margin:0 auto; padding:2.5rem 1.5rem 6rem; }}
.eyebrow {{ font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent); font-weight:700; margin:0 0 0.6rem; }}
h1 {{ font-family:'Source Serif 4',Georgia,serif; font-size:1.7rem; margin:0 0 0.3rem; text-wrap:balance; }}
.sub-ja {{ color:var(--ink-soft); font-size:1rem; margin:0 0 2.2rem; }}
.level-block {{ margin-bottom:3.5rem; }}
.level-head {{ display:flex; align-items:baseline; gap:0.8rem; flex-wrap:wrap; margin-bottom:1rem; }}
.level-head h2 {{ font-size:1.05rem; margin:0; font-weight:700; }}
.level-title {{ font-weight:400; color:var(--ink-soft); font-size:0.9rem; }}
.chip {{ font-size:0.68rem; font-weight:700; letter-spacing:0.02em; padding:0.2rem 0.6rem; border-radius:99px; }}
.chip-ok {{ background:var(--ok-bg); color:var(--ok); }}
.chip-warn {{ background:var(--warn-bg); color:var(--warn); }}
.player-sticky {{ position:sticky; top:0; z-index:5; background:var(--paper); padding:0.6rem 0; margin-bottom:1.2rem; border-bottom:1px solid var(--rule); }}
.player-sticky audio {{ width:100%; }}
.segs {{ display:flex; flex-direction:column; gap:0; }}
.seg {{ padding:1.1rem 0; border-top:1px solid var(--rule); }}
.seg:first-child {{ border-top:none; }}
.seg-label {{ font-size:0.72rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:var(--accent); margin-bottom:0.5rem; }}
.seg-text {{ font-size:0.98rem; }}
.seg-text.en {{ font-family:'Source Serif 4',Georgia,serif; }}
.seg-text.ja {{ font-family:'Inter',sans-serif; }}
.seg-text p {{ margin:0 0 0.7rem; }}
.seg-text p:last-child {{ margin-bottom:0; }}
.stopped-warn {{ background:var(--warn-bg); color:var(--warn); font-size:0.8rem; padding:0.55rem 0.8rem; border-radius:8px; margin-bottom:0.7rem; }}
.kp-list {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:0.5rem; }}
.kp-list li {{ display:flex; align-items:baseline; gap:0.7rem; font-size:0.92rem; }}
.kp-rank {{ color:var(--ink-soft); font-variant-numeric:tabular-nums; font-size:0.78rem; width:1.2em; }}
.kp-en {{ font-family:'Source Serif 4',Georgia,serif; font-weight:600; }}
.kp-ja {{ color:var(--ink-soft); }}
footer {{ margin-top:2.5rem; font-size:0.72rem; color:var(--ink-soft); text-align:center; }}
</style>
<div class="wrap">
  <p class="eyebrow">Pool Topic No.{td["no"]} · PRODUCTION_GENERATED_PENDING_USER_REVIEW</p>
  <h1>{esc(td["title_en"])}</h1>
  <p class="sub-ja">{esc(td["title_ja"])}</p>
  {b1}
  {a2}
  <footer>ER-006-POOL-N4-N6-PRODUCTION-01 · 現行Production仕様で新規生成。⚠マークの区間は機械ASR検証未合格のまま採用されています。Fact Checker/Ledger Deviationの詳細は完了報告を参照。</footer>
</div>
'''


os.makedirs("er006_output/pool_pilot_01/adoption_audit_01/review_html_n4n6", exist_ok=True)
titles = {"n4_supermarket": "Supermarket Shuffle"}
for topic_key, td in data.items():
    page = build_page(topic_key, td, titles[topic_key])
    path = f"er006_output/pool_pilot_01/adoption_audit_01/review_html_n4n6/{topic_key}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(topic_key, len(page.encode('utf-8')), "bytes ->", path)
