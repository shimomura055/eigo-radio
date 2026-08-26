# ============================================================
# er008_evidence_compression_ab_04_build_artifact.py
# ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04 Part I
# ============================================================
# No.7のBaseline / Compression-aware Writer(B) / Lossless Editor(C)を
# section単位で3列比較するtext-onlyページ。音声は含めない。
import html
import json
import re

OUT_DIR = "er006_output/pool_pilot_01/pool_n7_assigned_desks"
SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"

PROPER_NOUNS = ["Scotiabank", "iCapital Network", "iCapital", "Bisnow", "Gensler", "Korn Ferry", "CBRE"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return html.escape(s).replace("\n\n", "<br><br>")


def en_words(text):
    return len(re.findall(r"[A-Za-z][A-Za-z'\u2019-]*", text))


def count_proper_nouns(text):
    return sum(text.count(name) for name in PROPER_NOUNS)


def count_numeric(text):
    pct = len(re.findall(r"\d+(\.\d+)?\s*%|\d+(\.\d+)?\s*percent", text))
    years = len(re.findall(r"\b(19|20)\d{2}\b", text))
    all_nums = len(re.findall(r"\b\d+\b", text))
    return {"percent": pct, "year": years, "total_numeric_tokens": all_nums}


SECTIONS = [
    ("part1", "Full Story Part 1", None),
    ("part2", "Full Story Part 2", None),
    ("point_one_body", "Point One", "point_one_heading"),
    ("point_two_body", "Point Two", "point_two_heading"),
    ("in_one_line", "In One Line", None),
]

CSS = """
:root{
  --paper:#f4f2ea; --paper-2:#ffffff; --ink:#20241f; --ink-soft:#4b524a;
  --line:rgba(32,36,31,0.14);
  --base:#6b6458; --base-soft:#efece3; --base-ink:#4a453b;
  --writer:#a8631f; --writer-soft:#f6e9d8; --writer-ink:#6b3f10;
  --editor:#1f7a68; --editor-soft:#e4f2ee; --editor-ink:#0f4a3f;
  --flag:#b0392f; --flag-soft:#fbe6e3; --flag-ink:#7a241c;
  --radius:14px;
  --serif:"Fraunces",Georgia,"Hiragino Mincho ProN",serif;
  --sans:"IBM Plex Sans","Hiragino Sans",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
    --line:rgba(241,239,230,0.16);
    --base:#a39c8e; --base-soft:#2a2822; --base-ink:#cdc7ba;
    --writer:#e0a862; --writer-soft:#2e2011; --writer-ink:#f3cd9a;
    --editor:#5fcbb1; --editor-soft:#0f2b26; --editor-ink:#a9ecdc;
    --flag:#e17d70; --flag-soft:#3a1512; --flag-ink:#f6c3bb;
  }
}
:root[data-theme="dark"]{
  --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
  --line:rgba(241,239,230,0.16);
  --base:#a39c8e; --base-soft:#2a2822; --base-ink:#cdc7ba;
  --writer:#e0a862; --writer-soft:#2e2011; --writer-ink:#f3cd9a;
  --editor:#5fcbb1; --editor-soft:#0f2b26; --editor-ink:#a9ecdc;
  --flag:#e17d70; --flag-soft:#3a1512; --flag-ink:#f6c3bb;
}
*{box-sizing:border-box;}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  margin:0;padding:2.5rem 1.5rem 4rem;line-height:1.6;}
.wrap{max-width:1280px;margin:0 auto;}
header.page{margin-bottom:2rem;}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 .6rem;}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.7rem,3.2vw,2.4rem);
  margin:0 0 .6rem;text-wrap:balance;}
.sub{color:var(--ink-soft);font-size:1rem;max-width:78ch;margin:0 0 .8rem;}
.status-pill{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--mono);
  font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;padding:.25rem .7rem;
  border-radius:999px;background:var(--writer-soft);color:var(--writer-ink);border:1px solid var(--line);}
.legend{display:flex;gap:1.1rem;flex-wrap:wrap;margin-top:1rem;font-size:.85rem;}
.legend span{display:inline-flex;align-items:center;gap:.4rem;}
.dot{width:.6rem;height:.6rem;border-radius:50%;display:inline-block;}
.dot.base{background:var(--base);} .dot.writer{background:var(--writer);} .dot.editor{background:var(--editor);}

.level-header{font-family:var(--serif);font-size:1.6rem;margin:2.6rem 0 .4rem;
  padding-bottom:.5rem;border-bottom:2px solid var(--line);}
.level-summary{font-size:.85rem;color:var(--ink-soft);margin:0 0 1.4rem;}
.level-summary b{color:var(--ink);}

.section-block{margin-bottom:1.8rem;background:var(--paper-2);border:1px solid var(--line);
  border-radius:var(--radius);padding:1.2rem 1.3rem 1.4rem;}
.section-block h3{font-family:var(--serif);font-size:1.15rem;margin:0 0 .2rem;}
.section-heading-line{font-size:.8rem;color:var(--ink-soft);margin:0 0 .8rem;font-style:italic;}
.triple{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.9rem;}
@media (max-width:920px){.triple{grid-template-columns:1fr;}}
.card{border-radius:10px;padding:.8rem .9rem;font-size:.85rem;border:1px solid var(--line);}
.card.base{background:var(--base-soft);}
.card.writer{background:var(--writer-soft);}
.card.editor{background:var(--editor-soft);}
.card .tag{font-family:var(--mono);font-size:.65rem;letter-spacing:.06em;text-transform:uppercase;
  display:inline-block;padding:.1rem .45rem;border-radius:999px;margin-bottom:.5rem;}
.card.base .tag{background:var(--paper-2);color:var(--base-ink);}
.card.writer .tag{background:var(--paper-2);color:var(--writer-ink);}
.card.editor .tag{background:var(--paper-2);color:var(--editor-ink);}
.card p{margin:0 0 .5rem;white-space:pre-line;color:var(--ink);}
.metrics{font-family:var(--mono);font-size:.68rem;color:var(--ink-soft);
  display:flex;gap:.6rem;flex-wrap:wrap;font-variant-numeric:tabular-nums;
  border-top:1px dashed var(--line);padding-top:.4rem;margin-top:.3rem;}

table.compact{border-collapse:collapse;width:100%;font-size:.82rem;margin:.6rem 0 0;}
table.compact th,table.compact td{border:1px solid var(--line);padding:.35rem .55rem;text-align:left;
  font-variant-numeric:tabular-nums;}
table.compact th{background:var(--paper-2);font-family:var(--mono);font-size:.68rem;
  text-transform:uppercase;letter-spacing:.04em;color:var(--ink-soft);}

.flag-note{font-size:.78rem;background:var(--flag-soft);color:var(--flag-ink);
  border-radius:8px;padding:.5rem .7rem;margin:1.1rem 0;line-height:1.5;}

footer.page{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--ink-soft);}
"""


def metric_line(text):
    wc = en_words(text)
    pn = count_proper_nouns(text)
    num = count_numeric(text)
    return (f'<div class="metrics"><span>words: {wc}</span>'
            f'<span>proper nouns: {pn}</span>'
            f'<span>%: {num["percent"]}</span>'
            f'<span>years: {num["year"]}</span>'
            f'<span>numeric: {num["total_numeric_tokens"]}</span></div>')


def section_html(key, title, heading_key, baseline_parts, writer_parts, editor_parts):
    b_text, w_text, e_text = baseline_parts[key], writer_parts[key], editor_parts[key]
    heading_line = ""
    if heading_key:
        heading_line = (f'<p class="section-heading-line">Heading &mdash; Baseline: '
                         f'"{esc(baseline_parts[heading_key])}" / Writer: '
                         f'"{esc(writer_parts[heading_key])}" / Editor: '
                         f'"{esc(editor_parts[heading_key])}"</p>')
    return f"""<div class="section-block">
  <h3>{title}</h3>
  {heading_line}
  <div class="triple">
    <div class="card base">
      <span class="tag">Baseline</span>
      <p>{esc(b_text)}</p>
      {metric_line(b_text)}
    </div>
    <div class="card writer">
      <span class="tag">B: Compression-aware Writer</span>
      <p>{esc(w_text)}</p>
      {metric_line(w_text)}
    </div>
    <div class="card editor">
      <span class="tag">C: Lossless Editor</span>
      <p>{esc(e_text)}</p>
      {metric_line(e_text)}
    </div>
  </div>
</div>"""


def level_section(level_label, base_dir, writer_dir, editor_dir, fact_note):
    baseline_parts = load_json(f"{OUT_DIR}/{base_dir}/parts.json")
    writer_parts = load_json(f"{OUT_DIR}/evidence_compression_candidate/{writer_dir}/parts.json")
    editor_parts = load_json(f"{OUT_DIR}/evidence_compression_editor/{editor_dir}/parts.json")
    body = "".join(
        section_html(key, title, heading_key, baseline_parts, writer_parts, editor_parts)
        for key, title, heading_key in SECTIONS
    )
    return f"""<h2 class="level-header">{level_label}</h2>
<p class="level-summary">{fact_note}</p>
{body}"""


def build():
    a2_html = level_section(
        "A2", "a2", "a2", "a2",
        "Fact Check (Baseline / Writer / Editor): REVIEW_REQUIRED / REVIEW_REQUIRED / <b>PASS</b> &middot; "
        "Ledger Deviation: 5 (MAJOR 4) / 6 (MAJOR 3) / 5 (MAJOR 4) &middot; "
        "causal-strengthening words (because/causes/leads to/makes/results in) found in article body: "
        "0 / 0 / 0 (all clean)")
    b1_html = level_section(
        "B1", "b1b", "b1b", "b1b",
        "Fact Check (Baseline / Writer / Editor): REVIEW_REQUIRED / REVIEW_REQUIRED / REVIEW_REQUIRED &middot; "
        "Ledger Deviation: 1 (MAJOR 1) / 6 (MAJOR 4) / 4 (MAJOR 2) &middot; "
        "causal-strengthening words found in article body: 0 / 0 / 0 (all clean &mdash; "
        "the earlier drift from the first Writer attempt does not recur after the Fact-safety "
        "invariants were added to the prompt)")

    body = f"""<title>Evidence Compression 3-Way</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">English Your Way &middot; ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04</p>
    <h1>No.7: Baseline vs Two Evidence Compression Methods</h1>
    <p class="sub">Script-only comparison (no audio). Research / Evidence Pack / VFL / Fact Check keep every
    Fact unchanged in all three versions. <b>Method B (Compression-aware Writer)</b> writes the article fresh
    from the Fact Ledger with Evidence Density guidance built in from the start. <b>Method C (Lossless Editor)</b>
    takes the existing Baseline script and only removes/generalizes what it can without touching anything else.
    This run used a strengthened prompt that explicitly forbids causal/scope/certainty drift, added after the
    first Evidence Compression trial (ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03) produced a stronger-than-
    supported causal claim in one B1 candidate.</p>
    <span class="status-pill">VALIDATED_CANDIDATE / USER_REVIEW_REQUIRED</span>
    <div class="legend">
      <span><i class="dot base"></i>Baseline &mdash; current Production script (unchanged)</span>
      <span><i class="dot writer"></i>Method B &mdash; Compression-aware Writer (fresh from Fact Ledger)</span>
      <span><i class="dot editor"></i>Method C &mdash; Lossless Editor (light edit of Baseline)</span>
    </div>
    <div class="flag-note">
      <b>Observed difference between the two methods:</b> Method C consistently drove proper-noun mentions to
      zero across every section in this run and left unrelated sentences byte-for-byte identical to Baseline
      (including a pre-existing causal phrase in A2's In One Line that was already in Baseline before any
      compression). Method B is a full rewrite, so its wording varies more between runs &mdash; in this run
      it happened to keep "Scotiabank" / "iCapital Network" in A2's Full Story Part 2. Neither introduced a
      new causal-strengthening claim this time. See the completion report for the recommended method.
    </div>
  </header>

  {a2_html}
  {b1_html}

  <footer class="page">
    Generated 2026-08-26 (ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04 Part E&ndash;J)
    &middot; script-only, no TTS/ASR generated &middot; Production Writer default behavior unchanged
    (evidence_compression=False remains the default).
  </footer>
</div>
"""
    with open(f"{SCRATCH}/n7_evidence_compression_3way.html", "w", encoding="utf-8") as f:
        f.write(body)
    print("written", f"{SCRATCH}/n7_evidence_compression_3way.html")


if __name__ == "__main__":
    build()
