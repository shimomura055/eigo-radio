# ============================================================
# er008_evidence_compression_03_build_artifact.py
# ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03 Part E
# ============================================================
# No.7のBaseline vs Evidence Compression candidate(B1/A2)をsection単位で
# 並べて比較するtext-onlyページ。音声は含めない。
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

# Part C: 各sectionで削除/圧縮/維持されたEvidenceの短い注記(手動監査結果)。
EVIDENCE_NOTES = {
    ("a2", "part2"): "REMOVED: Scotiabank / iCapital Network(社名を「some companies」へ一般化)",
    ("b1b", "part1"): "REMOVED: Bisnow / Bisnow's New York Office Conference(出典名・イベント名を削除)",
    ("b1b", "part2"): "REMOVED: Scotiabank / iCapital Network、Korn Ferry citing Gensler dataの出典名、"
                        "「20%(パンデミック前比2倍)」の具体数値(トレンドの言及自体は維持)",
    ("a2", "point_one_body"): "REMOVED: Gensler(調査主体名)、87%/74%・80%/67%の4つの数値。"
                                "COMPRESSED: 2組の比較数値 → 「were more likely to say they felt they "
                                "belonged at work and could focus well」という1文の傾向表現へ",
    ("b1b", "point_one_body"): "REMOVED: Gensler(調査主体名)、87%/74%・80%/67%の4つの数値。"
                                 "COMPRESSED: 同上、causal overclaim防止の「connection, not proof」の"
                                 "hedgingは維持",
    ("a2", "point_two_body"): "REMOVED: CBRE(調査主体名)。KEPT: 56%/40%・2023/2024・2026(トレンドの"
                                "核心的な比較数値、変更なし)",
    ("b1b", "point_two_body"): "REMOVED: CBRE(調査主体名)。KEPT: 56%/40%・2023/2024・2026(同上)",
}


def load_level_parts(path):
    return load_json(f"{OUT_DIR}/{path}/parts.json")


CSS = """
:root{
  --paper:#f4f2ea; --paper-2:#ffffff; --ink:#20241f; --ink-soft:#4b524a;
  --line:rgba(32,36,31,0.14);
  --base:#6b6458; --base-soft:#efece3; --base-ink:#4a453b;
  --cand:#1f7a68; --cand-soft:#e4f2ee; --cand-ink:#0f4a3f;
  --warn:#a8631f; --warn-soft:#f6e9d8; --warn-ink:#6b3f10;
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
    --cand:#5fcbb1; --cand-soft:#0f2b26; --cand-ink:#a9ecdc;
    --warn:#e0a862; --warn-soft:#2e2011; --warn-ink:#f3cd9a;
  }
}
:root[data-theme="dark"]{
  --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
  --line:rgba(241,239,230,0.16);
  --base:#a39c8e; --base-soft:#2a2822; --base-ink:#cdc7ba;
  --cand:#5fcbb1; --cand-soft:#0f2b26; --cand-ink:#a9ecdc;
  --warn:#e0a862; --warn-soft:#2e2011; --warn-ink:#f3cd9a;
}
*{box-sizing:border-box;}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  margin:0;padding:2.5rem 1.5rem 4rem;line-height:1.62;}
.wrap{max-width:1080px;margin:0 auto;}
header.page{margin-bottom:2rem;}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 .6rem;}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.7rem,3.2vw,2.4rem);
  margin:0 0 .6rem;text-wrap:balance;}
.sub{color:var(--ink-soft);font-size:1rem;max-width:70ch;margin:0 0 .8rem;}
.status-pill{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--mono);
  font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;padding:.25rem .7rem;
  border-radius:999px;background:var(--warn-soft);color:var(--warn-ink);border:1px solid var(--line);}
.legend{display:flex;gap:1.1rem;flex-wrap:wrap;margin-top:1rem;font-size:.85rem;}
.legend span{display:inline-flex;align-items:center;gap:.4rem;}
.dot{width:.6rem;height:.6rem;border-radius:50%;display:inline-block;}
.dot.base{background:var(--base);} .dot.cand{background:var(--cand);}

.level-header{font-family:var(--serif);font-size:1.6rem;margin:2.6rem 0 .4rem;
  padding-bottom:.5rem;border-bottom:2px solid var(--line);}
.level-summary{font-size:.88rem;color:var(--ink-soft);margin:0 0 1.4rem;}
.level-summary b{color:var(--ink);}

.section-block{margin-bottom:1.8rem;background:var(--paper-2);border:1px solid var(--line);
  border-radius:var(--radius);padding:1.2rem 1.3rem 1.4rem;}
.section-block h3{font-family:var(--serif);font-size:1.15rem;margin:0 0 .2rem;}
.section-heading-line{font-size:.85rem;color:var(--ink-soft);margin:0 0 .8rem;font-style:italic;}
.evidence-note{font-size:.78rem;background:var(--warn-soft);color:var(--warn-ink);
  border-radius:8px;padding:.5rem .7rem;margin-bottom:.9rem;line-height:1.5;}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem;}
@media (max-width:760px){.pair{grid-template-columns:1fr;}}
.card{border-radius:10px;padding:.85rem .95rem;font-size:.87rem;border:1px solid var(--line);}
.card.base{background:var(--base-soft);}
.card.cand{background:var(--cand-soft);}
.card .tag{font-family:var(--mono);font-size:.65rem;letter-spacing:.06em;text-transform:uppercase;
  display:inline-block;padding:.1rem .45rem;border-radius:999px;margin-bottom:.5rem;}
.card.base .tag{background:var(--paper-2);color:var(--base-ink);}
.card.cand .tag{background:var(--paper-2);color:var(--cand-ink);}
.card p{margin:0 0 .6rem;white-space:pre-line;color:var(--ink);}
.metrics{font-family:var(--mono);font-size:.72rem;color:var(--ink-soft);
  display:flex;gap:.8rem;flex-wrap:wrap;font-variant-numeric:tabular-nums;
  border-top:1px dashed var(--line);padding-top:.5rem;margin-top:.3rem;}

table.compact{border-collapse:collapse;width:100%;font-size:.85rem;margin:.6rem 0 0;}
table.compact th,table.compact td{border:1px solid var(--line);padding:.4rem .6rem;text-align:left;
  font-variant-numeric:tabular-nums;}
table.compact th{background:var(--paper-2);font-family:var(--mono);font-size:.7rem;
  text-transform:uppercase;letter-spacing:.04em;color:var(--ink-soft);}

footer.page{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);
  font-size:.78rem;color:var(--ink-soft);}
footer.page a{color:var(--ink-soft);}
"""


def metric_line(text):
    wc = en_words(text)
    pn = count_proper_nouns(text)
    num = count_numeric(text)
    return (f'<div class="metrics"><span>words: {wc}</span>'
            f'<span>proper nouns: {pn}</span>'
            f'<span>%: {num["percent"]}</span>'
            f'<span>years: {num["year"]}</span>'
            f'<span>numeric tokens: {num["total_numeric_tokens"]}</span></div>')


def section_html(level_key, key, title, heading_key, baseline_parts, candidate_parts):
    b_text = baseline_parts[key]
    c_text = candidate_parts[key]
    heading_line = ""
    if heading_key:
        heading_line = (f'<p class="section-heading-line">Heading &mdash; baseline: '
                         f'"{esc(baseline_parts[heading_key])}" / candidate: '
                         f'"{esc(candidate_parts[heading_key])}"</p>')
    note = EVIDENCE_NOTES.get((level_key, key))
    note_html = f'<div class="evidence-note">{esc(note)}</div>' if note else ""
    return f"""<div class="section-block">
  <h3>{title}</h3>
  {heading_line}
  {note_html}
  <div class="pair">
    <div class="card base">
      <span class="tag">Baseline</span>
      <p>{esc(b_text)}</p>
      {metric_line(b_text)}
    </div>
    <div class="card cand">
      <span class="tag">Evidence Compression Candidate</span>
      <p>{esc(c_text)}</p>
      {metric_line(c_text)}
    </div>
  </div>
</div>"""


def level_section(level_key, level_label, level_path, candidate_path, fact_note):
    baseline_parts = load_level_parts(level_path)
    candidate_parts = load_level_parts(f"evidence_compression_candidate/{candidate_path}")
    body = "".join(
        section_html(level_key, key, title, heading_key, baseline_parts, candidate_parts)
        for key, title, heading_key in SECTIONS
    )
    return f"""<h2 class="level-header">{level_label}</h2>
<p class="level-summary">{fact_note}</p>
{body}"""


def build():
    a2_html = level_section(
        "a2", "A2", "a2", "a2",
        "Fact Check: baseline REVIEW_REQUIRED &rarr; candidate REVIEW_REQUIRED (unchanged) &middot; "
        "Ledger Deviation: baseline 5 (MAJOR 3) &rarr; candidate 3 (MAJOR 3)")
    b1_html = level_section(
        "b1b", "B1", "b1b", "b1b",
        "Fact Check: baseline REVIEW_REQUIRED &rarr; candidate <b>PASS</b> &middot; "
        "Ledger Deviation: baseline 1 (MAJOR 1) &rarr; candidate <b>6 (MINOR 3, MAJOR 3)</b> "
        "&mdash; see caution note below")

    body = f"""<title>Evidence Compression Candidate</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">English Your Way &middot; ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03</p>
    <h1>No.7: Baseline vs Evidence Compression Candidate</h1>
    <p class="sub">Script-only comparison (no audio). Research / Evidence Pack / VFL / Fact Check keep
    every Fact unchanged; only the spoken-layer wording was regenerated with an opt-in instruction
    telling the Writer to drop company/institution names and near-duplicate numbers that don't change
    listener understanding, while keeping the core comparisons, trend direction, and causal-caution
    hedging ("a connection, not proof").</p>
    <span class="status-pill">VALIDATED_CANDIDATE / USER_REVIEW_REQUIRED</span>
    <div class="legend">
      <span><i class="dot base"></i>Baseline &mdash; current Production script (unchanged)</span>
      <span><i class="dot cand"></i>Candidate &mdash; Evidence Compression opt-in (script-only)</span>
    </div>
    <div class="evidence-note" style="margin-top:1.1rem;">
      <b>Caution before adopting:</b> B1's candidate Ledger Deviation count rose from 1 to 6 (3 new
      MAJOR items), including a more direct causal phrase ("Assigned desks are returning because some
      offices are questioning the human cost of desk sharing" / A2: "...because some workers want a
      stable place to belong and focus") that reads more confidently than the underlying correlational
      evidence supports. This looks like a real side effect of compression, not just removed citation
      names &mdash; see Part D in the completion report before approving for Production.
    </div>
  </header>

  {a2_html}
  {b1_html}

  <footer class="page">
    Generated 2026-08-26 (ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03 Part B&ndash;E) &middot;
    script-only, no TTS/ASR generated &middot; Production Writer default behavior unchanged
    (evidence_compression=False remains the default in er003_v1_n3_01_articles_generate.py).
  </footer>
</div>
"""
    with open(f"{SCRATCH}/n7_evidence_compression_candidate.html", "w", encoding="utf-8") as f:
        f.write(body)
    print("written", f"{SCRATCH}/n7_evidence_compression_candidate.html")


if __name__ == "__main__":
    build()
