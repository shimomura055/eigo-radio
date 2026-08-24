# -*- coding: utf-8 -*-
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A-9: Topic×Level単位の
# A/B聴き比べArtifact HTML生成(base64埋め込み、12kHzダウンサンプル版)。
import json
import sys

sys.path.insert(0, ".")
from er007_artifact_audio_prep_01 import wav_to_data_uri
from er007_evidence_density_ab_01_scripts import B_SCRIPTS

TOPIC_CONFIG = {
    "n4_supermarket": {"out_dir": "er006_output/pool_pilot_01/pool_n4_supermarket",
                        "title_ja": "スーパーマーケット棚替え", "title_en_key": "n4"},
    "n5_cafes": {"out_dir": "er006_output/pool_pilot_01/pool_n5_cafes",
                 "title_ja": "カフェのラップトップ問題", "title_en_key": "n5"},
    "n6_delivery": {"out_dir": "er006_output/pool_pilot_01/pool_n6_delivery",
                    "title_ja": "配送追跡ページの心理", "title_en_key": "n6"},
}

SEGMENT_LABELS = {
    "part1": "Full Story Part 1", "part2": "Full Story Part 2",
    "point_one_body": "Point One", "point_two_body": "Point Two",
}
SEGMENT_TO_AUDIO_NAME = {
    "part1": "full_story_part1", "part2": "full_story_part2",
    "point_one_body": "point_one", "point_two_body": "point_two",
}

B_AUDIO_ROOT = "er006_output/pool_pilot_01/evidence_density_ab_01/b_audio"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_segment_block(short_key, level_dir, seg_key, original_text, override_text):
    label = SEGMENT_LABELS[seg_key]
    audio_name = SEGMENT_TO_AUDIO_NAME[seg_key]
    out_dir = TOPIC_CONFIG[short_key]["out_dir"]
    orig_wav = f"{out_dir}/{level_dir}/narration/{audio_name}.wav"

    if override_text is None:
        return f"""
    <div class="card unchanged">
      <div class="seg-head"><span class="seg-label">{label}</span><span class="tag unchanged-tag">変更なし</span></div>
      <p class="unchanged-note">この区間はEvidence Density的に既に軽量で、圧縮対象にしていません。</p>
    </div>"""

    orig_uri = wav_to_data_uri(orig_wav)
    b_wav = f"{B_AUDIO_ROOT}/{short_key}/{level_dir}/{audio_name}.wav"
    b_uri = wav_to_data_uri(b_wav)

    a_html = esc(original_text).replace("\n\n", "</p><p>")
    b_html = esc(override_text).replace("\n\n", "</p><p>")

    return f"""
    <div class="card">
      <div class="seg-head"><span class="seg-label">{label}</span></div>
      <div class="audio-row">
        <span class="tag a">A(現行)</span>
        <audio controls preload="none" src="{orig_uri}"></audio>
      </div>
      <div class="audio-row">
        <span class="tag b">B(Evidence Compression)</span>
        <audio controls preload="none" src="{b_uri}"></audio>
      </div>
      <div class="script-compare">
        <div class="script-col">
          <div class="script-label a-label">A(現行)</div>
          <p>{a_html}</p>
        </div>
        <div class="script-col">
          <div class="script-label b-label">B(圧縮版)</div>
          <p>{b_html}</p>
        </div>
      </div>
    </div>"""


CSS = """
<style>
:root {
  --bg: #f7f5f0; --surface: #ffffff; --ink: #221f1a; --ink-soft: #746c5c;
  --accent: #2f6f6b; --accent-soft: #dcebe9; --line: #e3ddcf;
  --a-color: #a8632f; --b-color: #2f6f6b;
  --font-display: 'Zen Kaku Gothic New', 'Hiragino Sans', sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1a1d1b; --surface: #232722; --ink: #eef0e9; --ink-soft: #a8ab9d;
    --accent: #6ec2bb; --accent-soft: #253632; --line: #34382f;
    --a-color: #dd935b; --b-color: #6ec2bb;
  }
}
:root[data-theme="dark"] {
  --bg: #1a1d1b; --surface: #232722; --ink: #eef0e9; --ink-soft: #a8ab9d;
  --accent: #6ec2bb; --accent-soft: #253632; --line: #34382f;
  --a-color: #dd935b; --b-color: #6ec2bb;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-display); margin: 0; padding: 2.5rem 1.5rem 4rem; line-height: 1.7; }
.wrap { max-width: 820px; margin: 0 auto; }
h1 { font-size: 1.85rem; font-weight: 700; margin: 0 0 0.3rem; text-wrap: balance; }
.subtitle { color: var(--ink-soft); font-size: 0.95rem; margin: 0 0 2rem; }
.eyebrow { font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin-bottom: 0.4rem; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 1.5rem 1.6rem; margin-bottom: 1.4rem; }
.card.unchanged { opacity: 0.7; }
.seg-head { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.9rem; }
.seg-label { font-weight: 700; font-size: 1.05rem; }
.tag { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 0.22rem 0.55rem; border-radius: 999px; white-space: nowrap; }
.tag.a { background: color-mix(in srgb, var(--a-color) 18%, transparent); color: var(--a-color); }
.tag.b { background: color-mix(in srgb, var(--b-color) 18%, transparent); color: var(--b-color); }
.tag.unchanged-tag { background: var(--line); color: var(--ink-soft); }
.unchanged-note { color: var(--ink-soft); font-size: 0.9rem; margin: 0; }
.audio-row { display: flex; align-items: center; gap: 0.8rem; padding: 0.5rem 0; flex-wrap: wrap; }
audio { flex: 1; min-width: 220px; height: 34px; }
.script-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
@media (max-width: 640px) { .script-compare { grid-template-columns: 1fr; } }
.script-col { background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 0.9rem 1rem; font-size: 0.88rem; }
.script-col p { margin: 0 0 0.7rem; }
.script-col p:last-child { margin-bottom: 0; }
.script-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.5rem; }
.a-label { color: var(--a-color); }
.b-label { color: var(--b-color); }
.footer-note { color: var(--ink-soft); font-size: 0.85rem; margin-top: 2rem; }
.legend { display: flex; gap: 1.2rem; margin-bottom: 1.6rem; font-size: 0.85rem; color: var(--ink-soft); }
</style>
"""


def build_page(short_key, level_dir):
    cfg = TOPIC_CONFIG[short_key]
    out_dir = cfg["out_dir"]
    parts = load_json(f"{out_dir}/{level_dir}/parts.json")
    overrides = B_SCRIPTS[short_key][level_dir]
    level_label = "B1" if level_dir == "b1b" else "A2"

    blocks = []
    for seg_key in ("part1", "part2", "point_one_body", "point_two_body"):
        blocks.append(build_segment_block(short_key, level_dir, seg_key, parts[seg_key], overrides.get(seg_key)))

    title = parts["title"]
    html = f"""<title>{esc(cfg['title_ja'])} {level_label} AB</title>
{CSS}
<div class="wrap">
  <div class="eyebrow">Evidence Density A/B — {esc(cfg['title_ja'])} / {level_label}</div>
  <h1>{esc(title)}</h1>
  <p class="subtitle">A(現行完成候補)とB(Evidence Compression版)を聞き比べてください。裏側のResearch/Evidence Pack/VFL/Fact Checkは両方とも同じ既存Ledgerを使用しています。</p>
  <div class="legend">
    <span><span class="tag a">A</span> 現行(数字・年号・研究者名・機関名を維持)</span>
    <span><span class="tag b">B</span> 圧縮版(意味のある数字以外を削減)</span>
  </div>
  {''.join(blocks)}
  <p class="footer-note">
    最終判断はA/Bの音声試聴を優先してください。定量比較・Fact Check結果は完了報告を参照。
  </p>
</div>
"""
    return html, title


if __name__ == "__main__":
    short_key, level_dir = sys.argv[1], sys.argv[2]
    html, title = build_page(short_key, level_dir)
    out_path = (f"C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/"
                f"daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad/er007/{short_key}_{level_dir}_ab.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"written {out_path} ({len(html)} chars, {len(html)/1024/1024:.2f} MB)")
