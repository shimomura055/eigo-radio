# ============================================================
# er008_n7_baseline_reset_01_build_artifact.py
# ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01
# ============================================================
# No.7の正式Baseline(B1/A2のみ、Middleなし)比較試聴ページを、実際に
# 再生成されたarticle.md/parts.json/support_texts.json/key_phrasesから
# 動的に読み込んで組み立てる(旧Pilot版の固定辞書は使わない)。
import html
import json

OUT_DIR = "er006_output/pool_pilot_01/pool_n7_assigned_desks"
SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_b64(label):
    with open(f"{SCRATCH}/n7_baseline_{label}_b64.txt", encoding="ascii") as f:
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
        "title": parts["title"],
    }
    return data, key_phrases


CSS = """
:root{
  --paper:#f4f2ea; --paper-2:#ffffff; --ink:#20241f; --ink-soft:#4b524a;
  --line:rgba(32,36,31,0.14);
  --a2:#1f7a68; --a2-soft:#e4f2ee; --a2-ink:#0f4a3f;
  --b1:#4c3f8a; --b1-soft:#eae6f7; --b1-ink:#2f2560;
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
  }
}
:root[data-theme="dark"]{
  --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
  --line:rgba(241,239,230,0.16);
  --a2:#5fcbb1; --a2-soft:#0f2b26; --a2-ink:#a9ecdc;
  --b1:#a99bec; --b1-soft:#241f3d; --b1-ink:#d6cdf7;
}
*{box-sizing:border-box;}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  margin:0;padding:2.5rem 1.5rem 4rem;line-height:1.6;}
.wrap{max-width:920px;margin:0 auto;}
header.page{margin-bottom:2.2rem;}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 .6rem;}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.8rem,3.4vw,2.6rem);
  margin:0 0 .5rem;text-wrap:balance;}
.sub{color:var(--ink-soft);font-size:1.02rem;max-width:66ch;margin:0;}
.legend{display:flex;gap:1.1rem;flex-wrap:wrap;margin-top:1.3rem;font-size:.85rem;}
.legend span{display:inline-flex;align-items:center;gap:.4rem;}
.dot{width:.6rem;height:.6rem;border-radius:50%;display:inline-block;}
.dot.a2{background:var(--a2);} .dot.b1{background:var(--b1);}
.deferred{margin-top:1rem;padding:.8rem 1rem;background:var(--paper-2);border:1px dashed var(--line);
  border-radius:10px;font-size:.85rem;color:var(--ink-soft);}

.cols{display:grid;grid-template-columns:repeat(2,1fr);gap:1.1rem;}
@media (max-width:760px){.cols{grid-template-columns:1fr;}}
.col{background:var(--paper-2);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.3rem 1.3rem 1.5rem;display:flex;flex-direction:column;}
.col.a2{border-top:4px solid var(--a2);} .col.b1{border-top:4px solid var(--b1);}
.col h2{font-family:var(--serif);font-size:1.3rem;margin:.1rem 0 .15rem;}
.col .tag{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;
  padding:.15rem .5rem;border-radius:999px;display:inline-block;margin-bottom:.7rem;}
.col.a2 .tag{background:var(--a2-soft);color:var(--a2-ink);}
.col.b1 .tag{background:var(--b1-soft);color:var(--b1-ink);}
.col p.desc{font-size:.88rem;color:var(--ink-soft);margin:0 0 1rem;}
audio{width:100%;margin-bottom:.3rem;}
.dur{font-family:var(--mono);font-size:.75rem;color:var(--ink-soft);margin:0 0 1.1rem;
  font-variant-numeric:tabular-nums;}

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


def key_phrase_section(a2_kp, b1_kp):
    return f"""<div class="script-section">
  <h3 class="section-title">Key Words / Key Phrases</h3>
  <div class="script-row">{key_phrase_list_html("a2", a2_kp, "A2")}{key_phrase_list_html("b1", b1_kp, "B1")}</div>
</div>"""


def build():
    a2_data, a2_kp = load_level("a2")
    b1_data, b1_kp = load_level("b1b")
    a2_b64 = load_b64("a2")
    b1_b64 = load_b64("b1")
    with open(f"{SCRATCH}/n7_qa02_point_one_orig_b64.txt", encoding="ascii") as f:
        point_one_orig_b64 = f.read()
    with open(f"{SCRATCH}/n7_qa02_point_one_candidate_b64.txt", encoding="ascii") as f:
        point_one_candidate_b64 = f.read()

    # 実際の再生順(build_a2_timeline/build_b1_timelineと同じ順序):
    # Preview -> Key Phrases -> Comment 1 -> Full Story Part 1 -> Comment 2 ->
    # Full Story Part 2 -> Comment 3 -> Point One -> Point Two -> Comment 4 -> In One Line
    sections_html = "".join([
        section(a2_data, b1_data, "Preview / Intro", None, "preview"),
        key_phrase_section(a2_kp, b1_kp),
        section(a2_data, b1_data, "Comment 1", None, "comment_1"),
        section(a2_data, b1_data, "Full Story Part 1", None, "full_story_part1"),
        section(a2_data, b1_data, "Comment 2", None, "comment_2"),
        section(a2_data, b1_data, "Full Story Part 2", None, "full_story_part2"),
        section(a2_data, b1_data, "Comment 3", None, "comment_3"),
        section(a2_data, b1_data, "Point One", "point_one_heading", "point_one_body"),
        section(a2_data, b1_data, "Point Two", "point_two_heading", "point_two_body"),
        section(a2_data, b1_data, "Comment 4", None, "comment_4"),
    ])

    body = f"""<title>No.7 Baseline Reset</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">English Your Way &middot; ER-008-N7 Baseline Reset</p>
    <h1>Assigned Desks Are Back in Some Offices</h1>
    <p class="sub">No.7 regenerated from the official, Fixed A2/B1 Production spec &mdash;
    no Shared Point Blueprint, no cross-level comment anchoring, no Full Story length
    adjustment. B1 Key Phrase 2 was corrected (see below) and A2's Key Phrase pause was
    widened by 0.1s per user decision; everything else matches official Production.</p>
    <div class="legend">
      <span><i class="dot a2"></i>A2 &mdash; plain English + Japanese</span>
      <span><i class="dot b1"></i>B1 &mdash; natural adult English</span>
    </div>
    <p class="deferred">Middle/Bridge is not shown here. It is <strong>DEFERRED /
    FUTURE_CANDIDATE</strong> &mdash; not part of this Baseline comparison. See
    DECISION_LOG.md / OPEN_ITEMS.md for the recorded design and re-opening checklist.</p>
  </header>

  <section class="cols">
    <div class="col a2">
      <span class="tag">A2</span>
      <h2>{esc(a2_data["title"])}</h2>
      <p class="desc">Full story, Points, and In One Line in English; Preview and Comments in
      Japanese. Official A2 Production spec. Key Phrase numbering&rarr;phrase pause widened
      by 0.1s (ER-008-N7-CONTENT-AUDIO-QA-02 Part B).</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{a2_b64}"></audio>
      <p class="dur">5:30 &middot; official A2 pipeline (+0.1s Key Phrase pause)</p>
    </div>
    <div class="col b1">
      <span class="tag">B1</span>
      <h2>{esc(b1_data["title"])}</h2>
      <p class="desc">Full episode in natural adult English, Preview and Comments included.
      Official B1 Production spec. Key Phrase 2 ("compare poorly with") audio/gloss corrected
      (ER-008-N7-CONTENT-AUDIO-QA-02 Part A).</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{b1_b64}"></audio>
      <p class="dur">5:17 &middot; official B1 pipeline (Key Phrase 2 fixed)</p>
    </div>
  </section>

  <section class="script-section">
    <h3 class="section-title">A2 Point One Heading &mdash; Pronunciation Candidate</h3>
    <p class="desc" style="margin-bottom:1rem;">User feedback: "feel" onward sounded unnatural
    in the original. RCA: the original audio was generated via the minimal-instruction fallback
    path (the standard path failed 6 times on transient Gemini server errors) and OpenAI's
    Primary ASR transcribed it as correct text despite the actual audio being garbled &mdash;
    confirmed by re-transcribing with Azure Secondary ASR, which heard "A desk can feel LITHA."
    A freshly regenerated candidate (standard path succeeded this time) transcribes cleanly on
    both Primary and Secondary ASR. Not yet swapped into the B1/A2 episodes above &mdash; your
    call on whether the candidate sounds better.</p>
    <div class="script-row">
      <div class="script-card a2">
        <span class="src">Original (currently in A2 episode)</span>
        <div class="heading">"A desk can feel like a place"</div>
        <audio controls preload="none" src="data:audio/mpeg;base64,{point_one_orig_b64}"></audio>
        <p style="margin:.5rem 0 0;font-size:.8rem;color:var(--ink-soft);">Azure Secondary ASR heard: "A desk can feel LITHA."</p>
      </div>
      <div class="script-card a2">
        <span class="src">Regenerated candidate</span>
        <div class="heading">"A desk can feel like a place"</div>
        <audio controls preload="none" src="data:audio/mpeg;base64,{point_one_candidate_b64}"></audio>
        <p style="margin:.5rem 0 0;font-size:.8rem;color:var(--ink-soft);">Azure Secondary ASR heard: "A desk can feel like a place." (exact match)</p>
      </div>
    </div>
  </section>

  {sections_html}

  <footer class="page">
    Updated 2026-08-26 (ER-008-N7-CONTENT-AUDIO-QA-02) &middot;
    DEV/VALIDATION run using synchronous TTS (not the Gemini Batch API used in Production)
    &middot; No Shared Point Blueprint, no comment anchor, no Story length adjustment, no
    Key Phrase pause adjustment &mdash; this reflects official Production behavior as-is,
    including any open issues under investigation.
  </footer>
</div>
"""
    with open(f"{SCRATCH}/n7_baseline_artifact.html", "w", encoding="utf-8") as f:
        f.write(body)
    print("written", f"{SCRATCH}/n7_baseline_artifact.html")


if __name__ == "__main__":
    build()
