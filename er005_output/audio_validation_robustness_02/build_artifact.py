import base64
import json
import os

BASE = "er005_output/audio_validation_robustness_02"
with open(f"{BASE}/avr02_trial_results.json", encoding="utf-8") as f:
    RESULTS = json.load(f)

CATEGORY_LABEL = {
    "NORMAL_ASR_PASS": ("OK", "ok"),
    "NORMAL_ASR_MISMATCH": ("ASR不一致", "warn"),
    "INVALID_ARGUMENT": ("INVALID_ARGUMENT", "bad"),
    "500_INTERNAL": ("500 INTERNAL", "bad"),
    "OTHER_TTS_ERROR": ("応答が空(parts欠落)", "bad"),
    "TIMEOUT": ("タイムアウト", "bad"),
    "DURATION_ANOMALY": ("異常長音声(hallucination疑い)", "bad"),
    "NO_SPEECH_DETECTED": ("発話区間未検出", "bad"),
}

SEGMENT_META = {
    "a2_topic_intro": ("A2 topic_intro", "英語(Aoede)", "Today's topic is When Family Tension Meets Screen Time: A Study of Young Children."),
    "a2_point_one": ("A2 point_one", "英語(Aoede)", "A closer parent-child relationship was linked with fewer behavior problems…"),
    "a2_full_story_part1": ("A2 full_story_part1", "英語(Aoede)", "A quiet question at home may become an important research question…(727字)"),
    "kp5_en_association": ("B1 Key Phrase 5 英語(“association”)", "英語(Aoede)", "association"),
    "kp5_ja_association": ("B1 Key Phrase 5 日本語meaning(“関連・相関”)", "日本語(Charon)", "関連・相関"),
}


def audio_tag(path):
    if not path or not os.path.exists(path):
        return ""
    mp3_path = path.replace("/trials/", "/mp3/").replace(".wav", ".mp3")
    if not os.path.exists(mp3_path):
        return ""
    with open(mp3_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f'<audio controls preload="none" src="data:audio/mpeg;base64,{b64}"></audio>'


def trial_row(t, idx):
    cat = t.get("category")
    label, cls = CATEGORY_LABEL.get(cat, (cat, "warn"))
    parts = [f'<div class="trial"><span class="trial-num">#{idx}</span>'
             f'<span class="chip chip-{cls}">{label}</span>']
    if t.get("path"):
        parts.append(audio_tag(t["path"]))
    if t.get("asr_text"):
        parts.append(f'<span class="asr-text">ASR: {t["asr_text"]}</span>')
    err = t.get("error")
    if err:
        parts.append(f'<span class="err-text">{err[:120]}</span>')
    parts.append("</div>")
    return "".join(parts)


def method_summary(trials):
    from collections import Counter
    n = len(trials)
    ok = sum(1 for t in trials if t.get("category") == "NORMAL_ASR_PASS")
    cats = Counter(t.get("category") for t in trials)
    cat_str = " / ".join(f"{CATEGORY_LABEL.get(k, (k, ''))[0]}×{v}" for k, v in cats.items())
    return n, ok, cat_str


def build_segment_section(seg):
    name, lang, text = SEGMENT_META[seg["segment"]]
    cur_n, cur_ok, cur_summary = method_summary(seg["current"])
    struct_n, struct_ok, struct_summary = method_summary(seg["structured"])
    cur_rows = "".join(trial_row(t, i + 1) for i, t in enumerate(seg["current"]))
    struct_rows = "".join(trial_row(t, i + 1) for i, t in enumerate(seg["structured"]))
    return f"""
    <section class="segment">
      <h2>{name}</h2>
      <p class="meta">{lang} ・ 本文: <span class="src-text">{text}</span></p>
      <div class="compare">
        <div class="method method-current">
          <div class="method-head">
            <span class="method-label">Current</span>
            <span class="method-rate">{cur_ok}/{cur_n} 正常</span>
          </div>
          <p class="method-summary">{cur_summary}</p>
          {cur_rows}
        </div>
        <div class="method method-structured">
          <div class="method-head">
            <span class="method-label">Structured Separation</span>
            <span class="method-rate">{struct_ok}/{struct_n} 正常</span>
          </div>
          <p class="method-summary">{struct_summary}</p>
          {struct_rows}
        </div>
      </div>
    </section>
"""


sections_html = "".join(build_segment_section(seg) for seg in RESULTS)

HTML = f"""<!doctype html>
<title>Instruction Separation A/B</title>
<style>
  :root {{
    --bg: #f6f3ee; --surface: #ffffff; --surface-2: #efeae1;
    --ink: #241f1a; --ink-dim: #6b6255; --border: #ddd5c7;
    --accent: #a4432e; --accent-ink: #ffffff;
    --ok: #3f6b47; --ok-bg: #e6efe4;
    --warn: #9a6b1f; --warn-bg: #f6ecd8;
    --bad: #a4432e; --bad-bg: #f6e6e0;
    --current: #4a5568; --current-bg: #eceef0;
    --structured: #a4432e; --structured-bg: #f6e6e0;
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --serif: 'Source Serif 4', Georgia, serif;
    --sans: 'IBM Plex Sans', system-ui, sans-serif;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #1c1815; --surface: #262019; --surface-2: #2e271f;
      --ink: #ede6da; --ink-dim: #a89d8b; --border: #3c342a;
      --accent: #e08363; --accent-ink: #201007;
      --ok: #8fc79a; --ok-bg: #253429;
      --warn: #e0b563; --warn-bg: #3a3120;
      --bad: #e08363; --bad-bg: #3a2620;
      --current: #a9b4c0; --current-bg: #2a2e33;
      --structured: #e08363; --structured-bg: #3a2620;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #1c1815; --surface: #262019; --surface-2: #2e271f;
    --ink: #ede6da; --ink-dim: #a89d8b; --border: #3c342a;
    --accent: #e08363; --accent-ink: #201007;
    --ok: #8fc79a; --ok-bg: #253429;
    --warn: #e0b563; --warn-bg: #3a3120;
    --bad: #e08363; --bad-bg: #3a2620;
    --current: #a9b4c0; --current-bg: #2a2e33;
    --structured: #e08363; --structured-bg: #3a2620;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--sans);
         padding: 2.5rem 1.25rem 4rem; }}
  .wrap {{ max-width: 900px; margin: 0 auto; }}
  header {{ margin-bottom: 2rem; }}
  .eyebrow {{ font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.09em;
              text-transform: uppercase; color: var(--accent); margin: 0 0 0.5rem; }}
  h1 {{ font-family: var(--serif); font-size: 1.9rem; margin: 0 0 0.6rem; text-wrap: balance; }}
  .lede {{ font-family: var(--serif); font-size: 1.02rem; color: var(--ink-dim); line-height: 1.6;
           max-width: 65ch; margin: 0 0 0.5rem; }}
  .note {{ font-family: var(--sans); font-size: 0.86rem; color: var(--ink-dim); line-height: 1.6;
           background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
           padding: 0.9rem 1.1rem; margin-top: 1rem; }}
  .note strong {{ color: var(--ink); }}
  section.segment {{ border: 1px solid var(--border); border-radius: 12px; background: var(--surface);
                      padding: 1.4rem 1.5rem 1.6rem; margin-bottom: 1.5rem; }}
  h2 {{ font-family: var(--serif); font-size: 1.25rem; margin: 0 0 0.3rem; }}
  .meta {{ font-family: var(--sans); font-size: 0.82rem; color: var(--ink-dim); margin: 0 0 1rem; }}
  .src-text {{ font-family: var(--mono); font-size: 0.78rem; }}
  .compare {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.1rem; }}
  @media (max-width: 680px) {{ .compare {{ grid-template-columns: 1fr; }} }}
  .method {{ border: 1px solid var(--border); border-radius: 10px; padding: 0.9rem 1rem; }}
  .method-current {{ background: var(--current-bg); }}
  .method-structured {{ background: var(--structured-bg); }}
  .method-head {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.3rem; }}
  .method-label {{ font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.04em;
                    font-weight: 600; text-transform: uppercase; }}
  .method-current .method-label {{ color: var(--current); }}
  .method-structured .method-label {{ color: var(--structured); }}
  .method-rate {{ font-family: var(--mono); font-size: 0.82rem; font-variant-numeric: tabular-nums; }}
  .method-summary {{ font-size: 0.78rem; color: var(--ink-dim); margin: 0 0 0.7rem; }}
  .trial {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; padding: 0.4rem 0;
            border-top: 1px solid var(--border); }}
  .trial:first-of-type {{ border-top: none; }}
  .trial-num {{ font-family: var(--mono); font-size: 0.72rem; color: var(--ink-dim); min-width: 1.6rem; }}
  .chip {{ font-family: var(--mono); font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 999px;
           white-space: nowrap; }}
  .chip-ok {{ background: var(--ok-bg); color: var(--ok); }}
  .chip-warn {{ background: var(--warn-bg); color: var(--warn); }}
  .chip-bad {{ background: var(--bad-bg); color: var(--bad); }}
  audio {{ height: 30px; flex: 1 1 200px; min-width: 160px; }}
  .asr-text, .err-text {{ font-family: var(--sans); font-size: 0.74rem; color: var(--ink-dim);
                           flex-basis: 100%; }}
  .err-text {{ color: var(--bad); }}
</style>
<div class="wrap">
  <header>
    <p class="eyebrow">ER-005-AUDIO-VALIDATION-ROBUSTNESS-02</p>
    <h1>Instruction Separation A/B Test</h1>
    <p class="lede">既存のstyle instruction文面(内容は一切変更していません)を、「Current」(既存通りテキストへ単純連結)と「Structured Separation」(読み上げ対象外であることを明示するdelimiterで区切る)の2方式で比較しました。過去にINVALID_ARGUMENT・hallucination・応答欠落が確認されていたsegmentを優先して選んでいます。</p>
    <p class="note"><strong>試聴のお願い:</strong> 各segmentで両方式の音声を聞き比べ、自然さ・落ち着き・ニュースらしさ・話者の印象・テンポ・聞きやすさに、体感できる差があるかご確認ください。Structured Separationの音声を本番へ反映するかどうかは、この試聴結果を踏まえてご判断いただく方針です(自動反映はしていません)。</p>
  </header>
  {sections_html}
</div>
"""

out_path = f"{BASE}/instruction_separation_ab.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote", out_path, "size KB:", len(HTML.encode("utf-8")) / 1024)
