# ============================================================
# er008_n7_completion_candidate_06_build_artifact.py
# ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 Part M
# ============================================================
# No.7の音声完成候補(A2/B1、Method C反映後・Key Phrase pause変更・
# Point One heading修正・A2わずかに遅く)を試聴できるページ。
import html
import json

OUT_DIR = "er006_output/pool_pilot_01/pool_n7_assigned_desks"
SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_b64(label):
    with open(f"{SCRATCH}/n7_final_{label}_b64.txt", encoding="ascii") as f:
        return f.read()


def esc(s):
    return html.escape(s).replace("\n\n", "<br><br>")


def load_level(level_dir):
    parts = load_json(f"{OUT_DIR}/{level_dir}/parts.json")
    support = load_json(f"{OUT_DIR}/{level_dir}/{'a2_support_texts.json' if level_dir == 'a2' else 'b1_support_texts.json'}")
    kp = load_json(f"{OUT_DIR}/{level_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrases = [(it["used_form"], it["japanese_gloss"]) for it in kp_items]
    data = {
        "preview": support["preview"], "comment_1": support["comment_1"], "comment_2": support["comment_2"],
        "comment_3": support["comment_3"], "comment_4": support["comment_4"],
        "point_one_heading": parts["point_one_heading"], "point_one_body": parts["point_one_body"],
        "point_two_heading": parts["point_two_heading"], "point_two_body": parts["point_two_body"],
        "full_story_part1": parts["part1"], "full_story_part2": parts["part2"],
        "in_one_line": parts["in_one_line"], "title": parts["title"],
    }
    return data, key_phrases


CSS = """
:root{
  --paper:#f4f2ea; --paper-2:#ffffff; --ink:#20241f; --ink-soft:#4b524a;
  --line:rgba(32,36,31,0.14);
  --a2:#1f7a68; --a2-soft:#e4f2ee; --a2-ink:#0f4a3f;
  --b1:#4c3f8a; --b1-soft:#eae6f7; --b1-ink:#2f2560;
  --highlight:#a8631f; --highlight-soft:#f6e9d8; --highlight-ink:#6b3f10;
  --good:#1f7a4a; --good-soft:#e2f2e7;
  --radius:14px;
  --serif:"Fraunces",Georgia,"Hiragino Mincho ProN",serif;
  --sans:"IBM Plex Sans","Hiragino Sans",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
    --line:rgba(241,239,230,0.16);
    --a2:#5fcbb1; --a2-soft:#0f2b26; --a2-ink:#a9ecdc;
    --b1:#a99bec; --b1-soft:#241f3d; --b1-ink:#d6cdf7;
    --highlight:#e0a862; --highlight-soft:#2e2011; --highlight-ink:#f3cd9a;
    --good:#6fd39a; --good-soft:#12291c;
  }
}
:root[data-theme="dark"]{
  --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
  --line:rgba(241,239,230,0.16);
  --a2:#5fcbb1; --a2-soft:#0f2b26; --a2-ink:#a9ecdc;
  --b1:#a99bec; --b1-soft:#241f3d; --b1-ink:#d6cdf7;
  --highlight:#e0a862; --highlight-soft:#2e2011; --highlight-ink:#f3cd9a;
  --good:#6fd39a; --good-soft:#12291c;
}
*{box-sizing:border-box;}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  margin:0;padding:2.5rem 1.5rem 4rem;line-height:1.6;}
.wrap{max-width:1080px;margin:0 auto;}
header.page{margin-bottom:2rem;}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 .6rem;}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.8rem,3.4vw,2.6rem);
  margin:0 0 .6rem;text-wrap:balance;}
.sub{color:var(--ink-soft);font-size:1.02rem;max-width:72ch;margin:0 0 .8rem;}
.status-row{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:1rem;}
.status-pill{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--mono);
  font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;padding:.25rem .65rem;
  border-radius:999px;background:var(--good-soft);color:var(--good);border:1px solid var(--line);}

.cols{display:grid;grid-template-columns:repeat(2,1fr);gap:1.1rem;margin-top:1.6rem;}
@media (max-width:760px){.cols{grid-template-columns:1fr;}}
.col{background:var(--paper-2);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.3rem 1.3rem 1.5rem;display:flex;flex-direction:column;}
.col.a2{border-top:4px solid var(--a2);} .col.b1{border-top:4px solid var(--b1);}
.col h2{font-family:var(--serif);font-size:1.3rem;margin:.1rem 0 .15rem;}
.col .tag{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;
  padding:.15rem .5rem;border-radius:999px;display:inline-block;margin-bottom:.7rem;}
.col.a2 .tag{background:var(--a2-soft);color:var(--a2-ink);}
.col.b1 .tag{background:var(--b1-soft);color:var(--b1-ink);}
.col p.desc{font-size:.86rem;color:var(--ink-soft);margin:0 0 1rem;}
audio{width:100%;margin-bottom:.3rem;}
.dur{font-family:var(--mono);font-size:.75rem;color:var(--ink-soft);margin:0 0 1.1rem;
  font-variant-numeric:tabular-nums;}

.highlight-block{margin:2rem 0;background:var(--highlight-soft);border:1px solid var(--line);
  border-radius:var(--radius);padding:1.2rem 1.3rem 1.4rem;}
.highlight-block h3{font-family:var(--serif);font-size:1.2rem;margin:0 0 .6rem;color:var(--highlight-ink);}
.highlight-block p{font-size:.88rem;margin:.4rem 0;}

table.compact{border-collapse:collapse;width:100%;font-size:.84rem;margin:.7rem 0 0;}
table.compact th,table.compact td{border:1px solid var(--line);padding:.4rem .6rem;text-align:left;
  font-variant-numeric:tabular-nums;}
table.compact th{background:var(--paper-2);font-family:var(--mono);font-size:.68rem;
  text-transform:uppercase;letter-spacing:.04em;color:var(--ink-soft);}

.script-section{margin-top:1.9rem;}
.script-section > h3.section-title{font-family:var(--serif);font-size:1.3rem;margin:0 0 1rem;
  padding-bottom:.5rem;border-bottom:1px solid var(--line);}
.script-row{display:grid;grid-template-columns:repeat(2,1fr);gap:1.1rem;margin-bottom:1.4rem;}
@media (max-width:760px){.script-row{grid-template-columns:1fr;}}
.script-card{background:var(--paper-2);border:1px solid var(--line);border-radius:10px;
  padding:.85rem .95rem;font-size:.86rem;}
.script-card .src{font-family:var(--mono);font-size:.65rem;letter-spacing:.06em;text-transform:uppercase;
  display:inline-block;padding:.1rem .45rem;border-radius:999px;margin-bottom:.5rem;}
.script-card.a2 .src{background:var(--a2-soft);color:var(--a2-ink);}
.script-card.b1 .src{background:var(--b1-soft);color:var(--b1-ink);}
.script-card .heading{font-weight:600;margin:0 0 .3rem;}
.script-card p{margin:0;color:var(--ink);white-space:pre-line;}
.kp-list{list-style:decimal;margin:0;padding:0 0 0 1.3rem;}
.kp-list li{display:flex;justify-content:space-between;align-items:baseline;gap:.6rem;
  padding:.4rem 0;border-bottom:1px dashed var(--line);}
.kp-list li:last-child{border-bottom:none;}
.kp-en{font-weight:600;}
.kp-ja{color:var(--ink-soft);font-size:.82rem;text-align:right;white-space:nowrap;}

footer.page{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--ink-soft);}
"""


def script_card(cls, label_html, body_html, tag_text):
    return f"""<div class="script-card {cls}">
  <span class="src">{tag_text}</span>
  {label_html}
  <p>{body_html}</p>
</div>"""


def section(a2_data, b1_data, title, key_heading, key_body):
    def cell(level_cls, data, tag_text):
        heading_html = ""
        if key_heading:
            heading_html = f'<div class="heading">{esc(data[key_heading])}</div>'
        body = esc(data[key_body])
        return script_card(level_cls, heading_html, body, tag_text)

    return f"""<div class="script-section">
  <h3 class="section-title">{title}</h3>
  <div class="script-row">{cell("a2", a2_data, "A2")}{cell("b1", b1_data, "B1")}</div>
</div>"""


def key_phrase_list_html(cls, phrases, tag_text):
    items = "".join(
        f'<li><span class="kp-en">{esc(en)}</span><span class="kp-ja">{esc(ja)}</span></li>'
        for en, ja in phrases
    )
    return f"""<div class="script-card {cls} kp-card">
  <span class="src">{tag_text}</span>
  <ol class="kp-list">{items}</ol>
</div>"""


def build():
    a2_data, a2_kp = load_level("a2")
    b1_data, b1_kp = load_level("b1b")
    a2_b64 = load_b64("a2")
    b1_b64 = load_b64("b1")

    sections_html = "".join([
        section(a2_data, b1_data, "Preview / Intro", None, "preview"),
        f"""<div class="script-section">
  <h3 class="section-title">Key Words / Key Phrases</h3>
  <div class="script-row">{key_phrase_list_html("a2", a2_kp, "A2")}{key_phrase_list_html("b1", b1_kp, "B1")}</div>
</div>""",
        section(a2_data, b1_data, "Comment 1", None, "comment_1"),
        section(a2_data, b1_data, "Full Story Part 1", None, "full_story_part1"),
        section(a2_data, b1_data, "Comment 2", None, "comment_2"),
        section(a2_data, b1_data, "Full Story Part 2", None, "full_story_part2"),
        section(a2_data, b1_data, "Comment 3", None, "comment_3"),
        section(a2_data, b1_data, "Point One", "point_one_heading", "point_one_body"),
        section(a2_data, b1_data, "Point Two", "point_two_heading", "point_two_body"),
        section(a2_data, b1_data, "Comment 4", None, "comment_4"),
        section(a2_data, b1_data, "In One Line", None, "in_one_line"),
    ])

    body = f"""<title>No.7 Completion Candidate</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">English Your Way &middot; ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06</p>
    <h1>{esc(a2_data["title"])}</h1>
    <p class="sub">No.7 completion candidate &mdash; ready for your listening review. Evidence
    Compression (Method C, Lossless Editor) is now the Production default and was applied to
    both scripts below. Every required audio segment passed the Audio Validation Gate
    automatically (no forced approvals).</p>
    <div class="status-row">
      <span class="status-pill">Evidence Compression: PRODUCTION_WIRED</span>
      <span class="status-pill">Audio Validation Gate: PASSED (all segments)</span>
      <span class="status-pill">USER LISTENING READY</span>
    </div>
  </header>

  <section class="cols">
    <div class="col a2">
      <span class="tag">A2</span>
      <h2>{esc(a2_data["title"])}</h2>
      <p class="desc">Evidence Compression applied. Key Phrase pause +0.2s vs original Baseline.
      Point One heading re-recorded (old mispronounced take retired). Slightly slower, relaxed
      pacing instruction applied to all English narration.</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{a2_b64}"></audio>
      <p class="dur">5:18 &middot; Production pipeline (Method C + pause + speed + heading fix)</p>
    </div>
    <div class="col b1">
      <span class="tag">B1</span>
      <h2>{esc(b1_data["title"])}</h2>
      <p class="desc">Evidence Compression applied (same Production default as A2). Key Phrase
      pause and narration pace unchanged from official B1 spec.</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{b1_b64}"></audio>
      <p class="dur">5:22 &middot; Production pipeline (Method C only, no pause/speed change)</p>
    </div>
  </section>

  <div class="highlight-block">
    <h3>A2 Key Phrase pause &mdash; measured</h3>
    <p>Numbering &rarr; phrase gap, measured on the actual generated audio (silence in the
    numbering file + the fixed internal pause + any residual silence in the phrase clip):</p>
    <table class="compact">
      <tr><th>Key Phrase</th><th>Effective pause</th></tr>
      <tr><td>hot-desking</td><td>0.668s</td></tr>
      <tr><td>assigned desk</td><td>0.663s</td></tr>
      <tr><td>sense of belonging</td><td>0.668s</td></tr>
      <tr><td>full reversal</td><td>0.615s</td></tr>
      <tr><td>bring back</td><td>0.610s</td></tr>
    </table>
    <p>For reference: the original Baseline (before any of the ER-008 pause work) measured
    about 0.41&ndash;0.47s. This run averages about 0.65s &mdash; roughly +0.2s over the
    original Baseline, as decided. B1 is unchanged.</p>
  </div>

  <div class="highlight-block">
    <h3>A2 Point One heading &mdash; fixed</h3>
    <p>Old text ("A desk can feel like a place") had a real pronunciation defect: OpenAI
    Primary ASR transcribed it as correct, but Azure Secondary ASR heard "A desk can feel
    LITHA." That old take has been retired &mdash; it is not part of this audio.</p>
    <p>The new heading text is <b>"{esc(a2_data['point_one_heading'])}"</b> (Method C produced
    different wording this round). It was generated fresh through the standard path (not
    fallback) and verified as an <b>exact match on both Primary and Azure Secondary ASR</b>.</p>
  </div>

  <div class="highlight-block">
    <h3>A2 speed &mdash; WPM measured</h3>
    <p>A natural-language instruction ("slightly slower, relaxed pace... smooth, conversational,
    natural") was added to A2's English narration only (no numeric WPM/speed-factor value).
    B1 received no instruction change.</p>
    <table class="compact">
      <tr><th>Section</th><th>Previous baseline (old text)</th><th>This candidate (new text)</th></tr>
      <tr><td>Full Story Part 1</td><td>142.3 WPM</td><td>147.7 WPM</td></tr>
      <tr><td>Full Story Part 2</td><td>162.8 WPM</td><td>151.4 WPM</td></tr>
      <tr><td>Point One</td><td>113.1 WPM</td><td>123.0 WPM</td></tr>
      <tr><td>Point Two</td><td>124.0 WPM</td><td>118.2 WPM</td></tr>
      <tr><td>In One Line</td><td>151.9 WPM</td><td>167.0 WPM</td></tr>
      <tr><td><b>Average</b></td><td><b>138.8 WPM</b></td><td><b>141.5 WPM</b></td></tr>
    </table>
    <p><b>Honest finding:</b> the average did not go down &mdash; the wording itself changed
    completely between the two runs (fresh Writer + Evidence Compression), so this is not a
    clean same-text A/B. Taken at face value, the pacing instruction did not produce a
    measurably slower narration this time. Reported as-is per the task's instruction, without
    further re-tuning.</p>
  </div>

  {sections_html}

  <footer class="page">
    Generated 2026-08-26 (ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06) &middot;
    DEV/VALIDATION run using synchronous TTS (not the Gemini Batch API used in Production)
    &middot; Every segment above passed the Audio Validation Gate automatically on this run
    (no STOPPED/UNVALIDATED segments, no forced Human Approval).
  </footer>
</div>
"""
    with open(f"{SCRATCH}/n7_completion_candidate.html", "w", encoding="utf-8") as f:
        f.write(body)
    print("written", f"{SCRATCH}/n7_completion_candidate.html")


if __name__ == "__main__":
    build()
