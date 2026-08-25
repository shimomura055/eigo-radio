# ============================================================
# er008_n7_pilot_run_01_build_artifact.py
# No.7 Pilot: B1/A2/Middle比較試聴ページの組み立て(Artifact公開用HTML)
# ============================================================
import html

SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"


def load_b64(label):
    with open(f"{SCRATCH}/n7_{label}_b64.txt", encoding="ascii") as f:
        return f.read()


def esc(s):
    return html.escape(s).replace("\n\n", "<br><br>")


B1 = {
    "preview": "This episode is about the way offices arrange desks. The issue is not only where people sit. It is also about how a workday feels and how people use the workplace. As you listen, consider what offices are trying to achieve when they change their desk system.",
    "comment_1": "Listen for what is changing in some offices now and the question that change raises.",
    "comment_2": "Some workplaces are bringing back assigned desks after years of shared seating. As you listen, ask: is this a full return to personal desks, or are shared desks still part of office life?",
    "comment_3": "For some workers, a regular desk can make the workday feel different. Shared desks can also feel hard to predict and less consistent. Next, we will look at two sides of this change.",
    "comment_4": "Across companies, the share with enough desks for all employees has gone down, and shared seating is still used in some workplaces. So the return of assigned desks is a change seen in some workplaces, not a broad shift across the whole market. Now, let\u2019s bring these points together in the final summary.",
    "point_one_heading": "Why a personal desk feels different",
    "point_one_body": "Workers\u2019 daily experience may be part of the story. Korn Ferry points to complaints about hot-desking: less appeal than working from home, unwanted closeness to unfamiliar colleagues, and less predictable workspaces.\n\nIn Gensler data, assigned-seat workers reported belonging more often than workers without assigned seating: 87%, compared with 74%. They also reported effective focus more often: 80%, compared with 67%. These are associations, not proof that desks caused the difference. Against this background, some offices are bringing assigned desks back.",
    "point_two_heading": "A limited return, not a market reversal",
    "point_two_body": "The wider market tells a different story. In CBRE\u2019s 2024 survey, the share of companies with at least one desk per employee fell from 56% in 2023 to 40% in 2024.\n\nRespondents expected it to fall to about one-third by 2026. So assigned desks are returning in some places, but shared seating remains part of the wider office model.",
    "full_story_part1": "After the pandemic, hot-desking became more common. In this system, workers are not given one personal desk. They choose an empty desk when they arrive.\n\nNow, in some offices, the desk map is changing again. Assigned desks are returning, and some workplaces are reducing their reliance on hot-desking.\n\nIt raises a simple question: after years of sharing, why are some workplaces choosing personal desks again?",
    "full_story_part2": "A worker may once again have a regular place to sit each day. But this is not a full return across the office world. Some offices still use shared desks and flexible office space.\n\nThe result is a mixed picture. The personal desk is back in some places, while the shared desk remains part of the wider office model.",
}

B1_KEY_PHRASES = [
    ("hot-desking", "\u5171\u6709\u30c7\u30b9\u30af\u5236\u3001\u30d5\u30ea\u30fc\u30a2\u30c9\u30ec\u30b9"),
    ("market reversal", "\u5e02\u5834\u5168\u4f53\u306e\u53cd\u8ee2"),
    ("unwanted closeness", "\u671b\u307e\u306a\u3044\u8fd1\u3055\u30fb\u8ddd\u96e2\u306e\u8fd1\u3055"),
    ("mixed picture", "\u4e00\u69d8\u3067\u306f\u306a\u3044\u72b6\u6cc1\u3001\u8907\u96d1\u306a\u5168\u4f53\u50cf"),
    ("quiet comeback", "\u9759\u304b\u306a\u5fa9\u6d3b\u3001\u76ee\u7acb\u305f\u306a\u3044\u518d\u767b\u5834"),
]

A2 = {
    "preview": "\u4eca\u56de\u306e\u30cb\u30e5\u30fc\u30b9\u306f\u3001\u4f1a\u793e\u306e\u6a5f\u306e\u4f7f\u3044\u65b9\u304c\u6539\u3081\u3066\u898b\u76f4\u3055\u308c\u3066\u3044\u308b\u3053\u3068\u306b\u3064\u3044\u3066\u3067\u3059\u3002\u673a\u306e\u6c7a\u3081\u65b9\u306f\u3001\u8077\u5834\u3067\u306e\u5c45\u5834\u6240\u3084\u3001\u4ed5\u4e8b\u3078\u306e\u96c6\u4e2d\u306e\u3057\u3084\u3059\u3055\u306b\u3082\u95a2\u308f\u308a\u307e\u3059\u3002\u4e00\u65b9\u3067\u3001\u30aa\u30d5\u30a3\u30b9\u306e\u4f7f\u3044\u65b9\u306b\u306f\u3001\u5225\u306e\u8003\u3048\u65b9\u3082\u3042\u308a\u307e\u3059\u3002\u306a\u305c\u673a\u306e\u4f7f\u3044\u65b9\u304c\u898b\u76f4\u3055\u308c\u3001\u4f1a\u793e\u3054\u3068\u306b\u8003\u3048\u65b9\u304c\u5206\u304b\u308c\u3066\u3044\u308b\u306e\u3067\u3057\u3087\u3046\u304b\u3002\u805e\u304d\u7d42\u3048\u308b\u3053\u308d\u306b\u306f\u3001\u3053\u306e\u52d5\u304d\u306e\u80cc\u666f\u3068\u3001\u4eca\u306e\u30aa\u30d5\u30a3\u30b9\u304c\u62b1\u3048\u308b\u8ad6\u70b9\u304c\u5206\u304b\u308a\u307e\u3059\u3002",
    "comment_1": "\u307e\u305a\u3001\u30d1\u30f3\u30c7\u30df\u30c3\u30af\u306e\u3042\u3068\u3001\u30aa\u30d5\u30a3\u30b9\u3067\u673a\u3092\u4f7f\u3046\u65b9\u6cd5\u304c\u3069\u3046\u5909\u308f\u3063\u305f\u304b\u306b\u6ce8\u76ee\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
    "comment_2": "\u30d1\u30f3\u30c7\u30df\u30c3\u30af\u306e\u5f8c\u3001\u591a\u304f\u306e\u4f1a\u793e\u3067\u306f\u3001\u6c7a\u307e\u3063\u305f\u673a\u3092\u6301\u305f\u305a\u3001\u6765\u305f\u4eba\u304c\u7a7a\u3044\u3066\u3044\u308b\u673a\u3092\u4f7f\u3046\u5f62\u304c\u5e83\u304c\u308a\u307e\u3057\u305f\u3002\u3067\u306f\u3001\u4f1a\u793e\u306f\u3053\u306e\u65b9\u6cd5\u3092\u5909\u3048\u3066\u3001\u673a\u3092\u6c7a\u3081\u308b\u306e\u3067\u3057\u3087\u3046\u304b\u3002",
    "comment_3": "\u3053\u306e\u30cb\u30e5\u30fc\u30b9\u306f\u3001\u4f1a\u793e\u306e\u673a\u306e\u4f7f\u3044\u65b9\u304c\u5c11\u3057\u5909\u308f\u3063\u3066\u3044\u308b\u3068\u3044\u3046\u8a71\u3067\u3059\u3002\u3059\u3079\u3066\u306e\u5834\u6240\u304c\u5143\u306b\u623b\u308b\u308f\u3051\u3067\u306f\u3042\u308a\u307e\u305b\u3093\u304c\u3001\u673a\u3092\u4e00\u4eba\u306e\u5c45\u5834\u6240\u306e\u3088\u3046\u306b\u8003\u3048\u308b\u898b\u65b9\u3082\u3042\u308a\u307e\u3059\u3002\u3053\u308c\u304b\u3089\u3001\u673a\u306e\u610f\u5473\u3068\u3001\u4eca\u56de\u306e\u5909\u5316\u306e\u5927\u304d\u3055\u306b\u3064\u3044\u3066\u898b\u3066\u3044\u304d\u307e\u3059\u3002",
    "comment_4": "\u3053\u3053\u307e\u3067\u3001\u56fa\u5b9a\u5e2d\u306e\u3042\u308b\u50cd\u304d\u65b9\u304c\u3001\u8077\u5834\u3067\u306e\u5c45\u5834\u6240\u3084\u96c6\u4e2d\u3057\u3084\u3059\u3055\u3068\u7d50\u3073\u3064\u304f\u9762\u3092\u898b\u3066\u304d\u307e\u3057\u305f\u3002\u305d\u306e\u4e00\u65b9\u3067\u3001\u67d4\u8edf\u306b\u4f7f\u3048\u308b\u30b9\u30da\u30fc\u30b9\u3082\u6b8b\u3063\u3066\u304a\u308a\u3001\u30aa\u30d5\u30a3\u30b9\u306e\u5e2d\u306e\u5f62\u306f\u4e00\u3064\u306b\u6c7a\u307e\u3063\u3066\u3044\u307e\u305b\u3093\u3002\u3067\u306f\u3001\u3053\u306e\u4e8c\u3064\u306e\u52d5\u304d\u3092\u82f1\u8a9e\u306e\u307e\u3068\u3081\u3067\u78ba\u8a8d\u3057\u307e\u3057\u3087\u3046\u3002",
    "point_one_heading": "A desk can feel like a place to belong",
    "point_one_body": "Gensler data shows why the change may matter. Among workers with assigned desks, 87% said they felt they belonged at work, compared with 74% without assigned desks. Also, 80% said they could focus well, compared with 67% in hot-desking settings. Korn Ferry says changing desks and nearby coworkers can make work less predictable. These findings help explain the return in some offices.",
    "point_two_heading": "A small change, not a full reversal",
    "point_two_body": "But the desk story is not moving in only one direction. CBRE found that companies with one desk or less for each worker fell from 56% in 2023 to 40% in 2024. In the same survey, 42% of organizations had more than 10% of their office space in flexible areas, up from 36%. Assigned desks are returning in some places, but flexible workspaces remain common overall.",
    "full_story_part1": "After the pandemic, many offices changed the way people used desks. Instead of keeping one desk for each worker, they began using hot-desking. In this system, a worker does not have a personal desk. They choose an empty desk when they arrive at the office. The desk may be different each day, depending on which seats are free. This means that workers may use different desks on different days. A worker’s desk is simply a place to sit during the day. The desk is not necessarily a personal space, and it may change from one day to the next.",
    "full_story_part2": "Now, some companies are changing that plan. Scotiabank and iCapital Network are among the companies bringing back assigned desks in some offices. This does not mean that hot-desking has ended everywhere. The change is quiet and limited. Assigned desks are returning in some offices, while companies are also reducing their dependence on empty desks. The old personal desk is returning in some places, but the shared desk has not disappeared.",
}

A2_KEY_PHRASES = [
    ("hot-desking", "共有デスク制"),
    ("assigned desk", "割り当てられた専用デスク"),
    ("full reversal", "全面的な方針転換"),
    ("belong at work", "職場に居場所があると感じる"),
    ("flexible workspace", "柔軟な共有型ワークスペース"),
]

CSS = """
:root{
  --paper:#f4f2ea; --paper-2:#ffffff; --ink:#20241f; --ink-soft:#4b524a;
  --line:rgba(32,36,31,0.14);
  --a2:#1f7a68; --a2-soft:#e4f2ee; --a2-ink:#0f4a3f;
  --mid:#a8631f; --mid-soft:#f6e9d8; --mid-ink:#6b3f10;
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
    --mid:#e0a862; --mid-soft:#2e2011; --mid-ink:#f3cd9a;
    --b1:#a99bec; --b1-soft:#241f3d; --b1-ink:#d6cdf7;
  }
}
:root[data-theme="dark"]{
  --paper:#1a1c18; --paper-2:#232620; --ink:#f1efe6; --ink-soft:#b9bcb2;
  --line:rgba(241,239,230,0.16);
  --a2:#5fcbb1; --a2-soft:#0f2b26; --a2-ink:#a9ecdc;
  --mid:#e0a862; --mid-soft:#2e2011; --mid-ink:#f3cd9a;
  --b1:#a99bec; --b1-soft:#241f3d; --b1-ink:#d6cdf7;
}
*{box-sizing:border-box;}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);
  margin:0;padding:2.5rem 1.5rem 4rem;line-height:1.6;}
.wrap{max-width:1180px;margin:0 auto;}
header.page{margin-bottom:2.2rem;}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 .6rem;}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(1.8rem,3.4vw,2.6rem);
  margin:0 0 .5rem;text-wrap:balance;}
.sub{color:var(--ink-soft);font-size:1.02rem;max-width:62ch;margin:0;}
.legend{display:flex;gap:1.1rem;flex-wrap:wrap;margin-top:1.3rem;font-size:.85rem;}
.legend span{display:inline-flex;align-items:center;gap:.4rem;}
.dot{width:.6rem;height:.6rem;border-radius:50%;display:inline-block;}
.dot.a2{background:var(--a2);} .dot.mid{background:var(--mid);} .dot.b1{background:var(--b1);}

.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;}
@media (max-width:920px){.cols{grid-template-columns:1fr;}}
.col{background:var(--paper-2);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.3rem 1.3rem 1.5rem;display:flex;flex-direction:column;}
.col.a2{border-top:4px solid var(--a2);} .col.mid{border-top:4px solid var(--mid);}
.col.b1{border-top:4px solid var(--b1);}
.col h2{font-family:var(--serif);font-size:1.3rem;margin:.1rem 0 .15rem;}
.col .tag{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;
  padding:.15rem .5rem;border-radius:999px;display:inline-block;margin-bottom:.7rem;}
.col.a2 .tag{background:var(--a2-soft);color:var(--a2-ink);}
.col.mid .tag{background:var(--mid-soft);color:var(--mid-ink);}
.col.b1 .tag{background:var(--b1-soft);color:var(--b1-ink);}
.col p.desc{font-size:.88rem;color:var(--ink-soft);margin:0 0 1rem;}
audio{width:100%;margin-bottom:.3rem;}
.dur{font-family:var(--mono);font-size:.75rem;color:var(--ink-soft);margin:0 0 1.1rem;
  font-variant-numeric:tabular-nums;}

.script-section{margin-top:1.9rem;}
.script-section > h3.section-title{font-family:var(--serif);font-size:1.3rem;margin:0 0 1rem;
  padding-bottom:.5rem;border-bottom:1px solid var(--line);}
.script-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin-bottom:1.4rem;}
@media (max-width:920px){.script-row{grid-template-columns:1fr;}}
.script-card{background:var(--paper-2);border:1px solid var(--line);border-radius:10px;
  padding:.85rem .95rem;font-size:.86rem;}
.script-card .src{font-family:var(--mono);font-size:.65rem;letter-spacing:.06em;text-transform:uppercase;
  display:inline-block;padding:.1rem .45rem;border-radius:999px;margin-bottom:.5rem;}
.script-card.a2 .src{background:var(--a2-soft);color:var(--a2-ink);}
.script-card.mid .src{background:var(--mid-soft);color:var(--mid-ink);}
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

MID_SEGMENT_SRC = {
    "Intro": "a2", "Preview": "b1", "Comment 1": "b1", "Comment 2": "b1",
    "Full Story Part 1": "a2", "Full Story Part 2": "a2",
    "Comment 3": "b1", "Point One": "a2", "Comment 4": "b1", "Point Two": "a2",
}


def script_card(cls, label_html, body_html, tag_text):
    return f"""<div class="script-card {cls}">
  <span class="src">{tag_text}</span>
  {label_html}
  <p>{body_html}</p>
</div>"""


def section(title, key_heading, key_body, mid_from_a2=False):
    """mid_from_a2=True: Middle列がA2側の文章を使うsegment(Full Story/
    Point、本文はA2のまま採用)。False: Middle列がB1側を使うsegment
    (Preview/Comment、B1 Supportをそのまま採用)。"""
    def cell(level_cls, data, tag_text, is_mid=False, src=None):
        heading_html = ""
        if key_heading:
            heading_html = f'<div class="heading">{esc(data[key_heading])}</div>'
        body = esc(data[key_body])
        actual_tag = tag_text
        if is_mid and src:
            actual_tag = f"from {src.upper()}"
        return script_card(level_cls, heading_html, body, actual_tag)

    a2_cell = cell("a2", A2, "A2")
    b1_cell = cell("b1", B1, "B1")
    mid_data, mid_tag_src = (A2, "a2") if mid_from_a2 else (B1, "b1")
    mid_cell = cell("mid", mid_data, "MIDDLE", is_mid=True, src=mid_tag_src)
    return f"""<div class="script-section">
  <h3 class="section-title">{title}</h3>
  <div class="script-row">{a2_cell}{mid_cell}{b1_cell}</div>
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


def key_phrase_section():
    # ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01 Part A:
    # MiddleはKey PhraseもB1の構造・英語phraseをそのまま使う(本文系
    # [Full Story/Point/In One Line]のみA2)。
    a2_cell = key_phrase_list_html("a2", A2_KEY_PHRASES, "A2")
    mid_cell = key_phrase_list_html("mid", B1_KEY_PHRASES, "from B1")
    b1_cell = key_phrase_list_html("b1", B1_KEY_PHRASES, "B1")
    return f"""<div class="script-section">
  <h3 class="section-title">Key Words / Key Phrases</h3>
  <div class="script-row">{a2_cell}{mid_cell}{b1_cell}</div>
</div>"""


def build():
    b1_b64 = load_b64("b1")
    a2_b64 = load_b64("a2")
    mid_b64 = load_b64("middle")

    # 実際の再生順(build_b1_timeline/build_middle_timeline_and_assembleと同じ順序):
    # Preview -> Key Phrases -> Comment 1 -> Full Story Part 1 -> Comment 2 ->
    # Full Story Part 2 -> Comment 3 -> Point One -> Point Two -> Comment 4
    sections_html = "".join([
        section("Preview / Intro", None, "preview"),
        key_phrase_section(),
        section("Comment 1", None, "comment_1"),
        section("Full Story Part 1", None, "full_story_part1", mid_from_a2=True),
        section("Comment 2", None, "comment_2"),
        section("Full Story Part 2", None, "full_story_part2", mid_from_a2=True),
        section("Comment 3", None, "comment_3"),
        section("Point One", "point_one_heading", "point_one_body", mid_from_a2=True),
        section("Point Two", "point_two_heading", "point_two_body", mid_from_a2=True),
        section("Comment 4", None, "comment_4"),
    ])

    body = f"""<title>No.7 Desk Pilot</title>
<style>{CSS}</style>
<div class="wrap">
  <header class="page">
    <p class="eyebrow">English Your Way &middot; ER-008-N7 Shared Point Blueprint Pilot</p>
    <h1>Assigned Desks Are Back in Some Offices</h1>
    <p class="sub">Three finished versions of the same No.7 episode, generated from one Shared
    Point Blueprint: the existing A2 level, the existing B1 level, and a new Middle/Bridge
    version built on the B1 episode, with only the English news-story segments (Full Story,
    Points, In One Line) swapped in from A2 &mdash; with zero new text-to-speech calls for
    Middle.</p>
    <div class="legend">
      <span><i class="dot a2"></i>A2 &mdash; plain English + Japanese</span>
      <span><i class="dot mid"></i>Middle &mdash; B1 base, A2 story</span>
      <span><i class="dot b1"></i>B1 &mdash; natural adult English</span>
    </div>
  </header>

  <section class="cols">
    <div class="col a2">
      <span class="tag">A2</span>
      <h2>The Desk Is Back&mdash;but Not Everywhere</h2>
      <p class="desc">Full story, Points, and In One Line in English; Preview and Comments in
      Japanese. Existing A2 production spec, unchanged.</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{a2_b64}"></audio>
      <p class="dur">~5:28 &middot; existing A2 pipeline</p>
    </div>
    <div class="col mid">
      <span class="tag">Middle / Bridge</span>
      <h2>The Desk Is Back&mdash;but Not Everywhere</h2>
      <p class="desc">Based on the full B1 episode (Title, Preview, Comments 1&ndash;4, Key
      Phrases all from B1). Only Full Story Part 1/2, Point One/Two, and In One Line are
      swapped in from A2. No new audio was generated for this version; Japanese only appears
      in the Key Phrase glosses.</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{mid_b64}"></audio>
      <p class="dur">~5:09 &middot; 0 new TTS/ASR calls</p>
    </div>
    <div class="col b1">
      <span class="tag">B1</span>
      <h2>Assigned Desks Are Quietly Returning to Some Offices</h2>
      <p class="desc">Full episode in natural adult English, Preview and Comments included.
      Existing B1 production spec, unchanged.</p>
      <audio controls preload="none" src="data:audio/mpeg;base64,{b1_b64}"></audio>
      <p class="dur">~5:00 &middot; existing B1 pipeline</p>
    </div>
  </section>

  {sections_html}

  <footer class="page">
    Updated 2026-08-25 (ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01) &middot;
    DEV/VALIDATION run using synchronous TTS (not the Gemini Batch API used in Production)
    &middot; Shared Point Blueprint: F-001/F-004/F-005/F-007 (Point One), F-008 (Point Two,
    required in both levels) &middot; A2 Full Story was expanded (102&rarr;169 words) after
    user feedback that Part 1 felt too short &middot; B1's Key Phrase pauses were tightened to
    match A2's (a trimming step was missing for B1) &middot; Middle column tags show which
    finished level's audio each segment is taken from.
  </footer>
</div>
"""
    with open(f"{SCRATCH}/n7_pilot_artifact.html", "w", encoding="utf-8") as f:
        f.write(body)
    print("written", f"{SCRATCH}/n7_pilot_artifact.html")


if __name__ == "__main__":
    build()
