# ER-005: 4本のFull Audio候補をテーマごとに2つのArtifact HTMLへ組み立てる
import json

SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"


def load_b64(name):
    with open(f"{SCRATCH}/{name}_b64.txt", encoding="ascii") as f:
        return f.read()


def load_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


CSS = """
:root {
  --paper: #f3f1e9;
  --paper-2: #ffffff;
  --ink: #26302a;
  --ink-soft: #5b6660;
  --line: #d9d4c4;
  --accent: #3d6b5c;
  --accent-warm: #b6572e;
  --mono-bg: #eee9da;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #1b201c;
    --paper-2: #232921;
    --ink: #ece7db;
    --ink-soft: #a9b3ab;
    --line: #3a4038;
    --accent: #7fbfa8;
    --accent-warm: #e08a5c;
    --mono-bg: #2a3128;
  }
}
:root[data-theme="dark"] {
  --paper: #1b201c;
  --paper-2: #232921;
  --ink: #ece7db;
  --ink-soft: #a9b3ab;
  --line: #3a4038;
  --accent: #7fbfa8;
  --accent-warm: #e08a5c;
  --mono-bg: #2a3128;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: Georgia, "Iowan Old Style", ui-serif, serif;
  line-height: 1.55;
}
.wrap { max-width: 880px; margin: 0 auto; padding: 48px 24px 80px; }
header.page { margin-bottom: 40px; }
.eyebrow {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 10px;
}
h1 { font-size: clamp(28px, 4vw, 40px); margin: 0 0 8px; text-wrap: balance; }
.sub { font-family: ui-sans-serif, system-ui, sans-serif; color: var(--ink-soft); font-size: 15px; max-width: 60ch; }
.card {
  background: var(--paper-2);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px 28px 24px;
  margin-bottom: 28px;
}
.card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 6px; }
.level-badge {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.06em;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--accent);
  color: var(--accent);
  white-space: nowrap;
}
.card h2 { font-size: 22px; margin: 0; }
audio { width: 100%; margin: 16px 0 14px; }
.meta {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 13px;
  color: var(--ink-soft);
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}
.meta strong { color: var(--ink); font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-weight: 600; }
details { margin-top: 14px; }
summary {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 13px;
  color: var(--accent);
  cursor: pointer;
  user-select: none;
}
.transcript {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 14.5px;
  color: var(--ink);
  white-space: pre-wrap;
  background: var(--mono-bg);
  border-radius: 10px;
  padding: 16px 18px;
  margin-top: 10px;
  max-height: 360px;
  overflow-y: auto;
}
footer.page {
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 12.5px;
  color: var(--ink-soft);
  border-top: 1px solid var(--line);
  padding-top: 18px;
  margin-top: 8px;
}
"""


def card(level_label, title, b64, duration, word_count, transcript):
    return f"""<div class="card">
  <div class="card-head">
    <h2>{title}</h2>
    <span class="level-badge">{level_label}</span>
  </div>
  <audio controls preload="none" src="data:audio/mpeg;base64,{b64}"></audio>
  <div class="meta">
    <span>Duration <strong>{duration}</strong></span>
    <span>Word count <strong>{word_count}</strong></span>
  </div>
  <details>
    <summary>Show full transcript</summary>
    <div class="transcript">{transcript}</div>
  </details>
</div>"""


def build_page(theme_title, theme_sub, b1_card_html, a2_card_html):
    return f"""<title>{theme_title}</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">ER-005-COST-BASELINE-01 &middot; Listening Candidate</p>
    <h1>{theme_title}</h1>
    <p class="sub">{theme_sub}</p>
  </header>
  {b1_card_html}
  {a2_card_html}
  <footer class="page">
    Generated as part of a Production-pipeline cost measurement run. Quality QA (Fact Checker, Ledger Deviation Check) was not skipped for cost-measurement purposes. user_quality_status remains NOT_REVIEWED pending project-owner listening.
  </footer>
</div>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---- AKB48 ----
akb_b1_parts = json.load(open("er005_output/cost_baseline_01/akb48/b1b/parts.json", encoding="utf-8"))
akb_a2_parts = json.load(open("er005_output/cost_baseline_01/akb48/a2/parts.json", encoding="utf-8"))
akb_b1_text = load_text("er005_output/cost_baseline_01/akb48/b1b/article.md")
akb_a2_text = load_text("er005_output/cost_baseline_01/akb48/a2/article.md")
akb_b1_metrics = json.load(open("er005_output/cost_baseline_01/akb48/b1b/metrics.json", encoding="utf-8"))
akb_a2_metrics = json.load(open("er005_output/cost_baseline_01/akb48/a2/metrics.json", encoding="utf-8"))

akb_page = build_page(
    "AKB48 \u2014 Listening Candidates",
    "COST-ARTICLE-01: AKB48's 68th single \u201cSuki-ish,\u201d Momoka Ito's back-to-back center run, and Saki Kondo's first selection at 14.",
    card("CEFR B1", akb_b1_parts["title"], load_b64("akb48_b1"), "4:46", akb_b1_metrics["word_count"], esc(akb_b1_text)),
    card("CEFR A2", akb_a2_parts["title"], load_b64("akb48_a2"), "5:16", akb_a2_metrics["word_count"], esc(akb_a2_text)),
)
with open("er005_output/cost_baseline_01/akb48_listening_candidates.html", "w", encoding="utf-8") as f:
    f.write(akb_page)

# ---- Parenting ----
par_b1_parts = json.load(open("er005_output/cost_baseline_01/parenting/b1b/parts.json", encoding="utf-8"))
par_a2_parts = json.load(open("er005_output/cost_baseline_01/parenting/a2/parts.json", encoding="utf-8"))
par_b1_text = load_text("er005_output/cost_baseline_01/parenting/b1b/article.md")
par_a2_text = load_text("er005_output/cost_baseline_01/parenting/a2/article.md")
par_b1_metrics = json.load(open("er005_output/cost_baseline_01/parenting/b1b/metrics.json", encoding="utf-8"))
par_a2_metrics = json.load(open("er005_output/cost_baseline_01/parenting/a2/metrics.json", encoding="utf-8"))

par_page = build_page(
    "Parenting Research \u2014 Listening Candidates",
    "COST-ARTICLE-02: A Dunedin Study finding on how parents' own upward social mobility relates to the quality of care they give their children.",
    card("CEFR B1", par_b1_parts["title"], load_b64("parenting_b1"), "5:52", par_b1_metrics["word_count"], esc(par_b1_text)),
    card("CEFR A2", par_a2_parts["title"], load_b64("parenting_a2"), "6:04", par_a2_metrics["word_count"], esc(par_a2_text)),
)
with open("er005_output/cost_baseline_01/parenting_listening_candidates.html", "w", encoding="utf-8") as f:
    f.write(par_page)

print("done")
