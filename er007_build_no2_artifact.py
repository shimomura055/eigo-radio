# -*- coding: utf-8 -*-
import json

with open("C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/"
          "daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad/er007/no2_audio_uris.json") as f:
    uris = json.load(f)

HTML_TEMPLATE = """<title>Yamenikuku Fix</title>
<style>
:root {
  --bg: #faf7f2; --surface: #ffffff; --ink: #24211d; --ink-soft: #6b6558;
  --accent: #b5502f; --accent-soft: #f0ddd2; --line: #e6e0d4;
  --good: #3f7a52; --bad: #b5502f;
  --font-display: 'Zen Kaku Gothic New', 'Hiragino Sans', sans-serif;
  --font-body: 'Zen Kaku Gothic New', 'Hiragino Sans', sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1c1a17; --surface: #262320; --ink: #f1ece3; --ink-soft: #b3aa9a;
    --accent: #e08a63; --accent-soft: #3a2a22; --line: #3a352c;
    --good: #7fc496; --bad: #e08a63;
  }
}
:root[data-theme="dark"] {
  --bg: #1c1a17; --surface: #262320; --ink: #f1ece3; --ink-soft: #b3aa9a;
  --accent: #e08a63; --accent-soft: #3a2a22; --line: #3a352c;
  --good: #7fc496; --bad: #e08a63;
}
* { box-sizing: border-box; }
body {
  background: var(--bg); color: var(--ink); font-family: var(--font-body);
  margin: 0; padding: 2.5rem 1.5rem 4rem; line-height: 1.7;
}
.wrap { max-width: 760px; margin: 0 auto; }
h1 {
  font-family: var(--font-display); font-size: 1.9rem; font-weight: 700;
  margin: 0 0 0.3rem; text-wrap: balance;
}
.subtitle { color: var(--ink-soft); font-size: 0.95rem; margin: 0 0 2.2rem; }
.eyebrow {
  font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: 0.4rem;
}
.card {
  background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
  padding: 1.6rem 1.7rem; margin-bottom: 1.5rem;
}
.audio-row {
  display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
  padding: 1rem 0; border-bottom: 1px solid var(--line);
}
.audio-row:last-child { border-bottom: none; }
.tag {
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
  padding: 0.25rem 0.6rem; border-radius: 999px; white-space: nowrap;
}
.tag.a { background: var(--accent-soft); color: var(--bad); }
.tag.fixed { background: color-mix(in srgb, var(--good) 18%, transparent); color: var(--good); }
audio { flex: 1; min-width: 220px; height: 36px; }
.transcript {
  font-size: 0.98rem; margin-top: 1.2rem; padding: 1rem 1.1rem;
  background: var(--bg); border-radius: 10px; border: 1px solid var(--line);
}
.highlight-bad { color: var(--bad); font-weight: 700; text-decoration: underline wavy var(--bad); }
.highlight-good { color: var(--good); font-weight: 700; text-decoration: underline wavy var(--good); }
h2 {
  font-family: var(--font-display); font-size: 1.15rem; margin: 0 0 0.9rem;
}
.rca-item { margin-bottom: 1rem; }
.rca-item .label { font-weight: 700; font-size: 0.85rem; color: var(--ink-soft); margin-bottom: 0.2rem; }
table { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin-top: 0.5rem; }
th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--line); }
th { color: var(--ink-soft); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; }
td.ok { color: var(--good); font-weight: 700; }
.footer-note { color: var(--ink-soft); font-size: 0.85rem; margin-top: 2rem; }
</style>

<div class="wrap">
  <div class="eyebrow">No.2 サブスク解約 — 発音修正</div>
  <h1>「やめにくくする」聞き比べ</h1>
  <p class="subtitle">A2 comment_3 のASR書き起こしが「やめにくかする」となっていた問題のRCAと修正候補です。</p>

  <div class="card">
    <h2>音声を聞き比べる</h2>
    <div class="audio-row">
      <span class="tag a">A(元の音声)</span>
      <audio controls preload="none" src="__ORIG_URI__"></audio>
    </div>
    <div class="audio-row">
      <span class="tag fixed">Fixed(再生成)</span>
      <audio controls preload="none" src="__FIXED_URI__"></audio>
    </div>
    <div class="transcript">
      <strong>Canonical text:</strong><br>
      このニュースは、定期サービスをやめ<span class="highlight-good">にくく</span>する仕組みと、それを変えようとしたルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう調べたのかを聞きます。
      <br><br>
      <strong>A(元の音声)のASR書き起こし:</strong><br>
      このニュースは、定期サービスをやめ<span class="highlight-bad">にくか</span>する仕組みと、それを変えようとしたルールが裁判で取り消された流れを伝えています。……
    </div>
  </div>

  <div class="card">
    <h2>原因調査(RCA)</h2>
    <div class="rca-item">
      <div class="label">何が起きていたか</div>
      canonical text・TTS入力テキストとも「やめにくくする」で正しく、reading-safety処理による変更もありませんでした(<code>reading_safety_changed_text: false</code>)。しかし実際に生成された音声をAzure ASRで書き起こすと「やめにく<b>か</b>する」となっており、これは単なる主観的な聞き取り誤りではなく、ASRという第三者の認識でも同じ「くか」寄りの音として捉えられていたことを意味します。
    </div>
    <div class="rca-item">
      <div class="label">既存Validatorがなぜ検出できなかったか</div>
      この文はA2の長いComment segment(118文字)で、短いsegment向けの厳密な発音一致チェック(<code>PHONETIC_MATCH</code>等、30文字以下が対象)の対象外でした。長いsegmentの検証は「先頭2文字の一致+文字数が許容範囲内か」だけを見ており、文中の一部が別の音へ変わっても検出できない設計になっています。
    </div>
    <div class="rca-item">
      <div class="label">再現性テスト</div>
      同じcanonical textで、本番と全く同じ生成関数を使って新たに4回音声を作り直しました。
      <table>
        <tr><th>試行</th><th>ASR書き起こし(「にくく」周辺)</th><th>判定</th></tr>
        <tr><td>1</td><td>やめにくくする</td><td class="ok">正常</td></tr>
        <tr><td>2</td><td>やめにくくする</td><td class="ok">正常</td></tr>
        <tr><td>3</td><td>やめにくくする</td><td class="ok">正常</td></tr>
        <tr><td>4</td><td>やめにくくする</td><td class="ok">正常</td></tr>
      </table>
      4回中4回とも正しく「やめにくくする」と発音・認識されました。「くく」という連続音節自体が構造的に誤りやすいわけではなく、今回の1回だけがGemini TTSの偶発的な生成ゆれだったと判断しています。
    </div>
    <div class="rca-item">
      <div class="label">結論・修正方針</div>
      再現性テストの結果、これは特定の音韻パターンに起因する一般化可能な問題ではなく、TTS固有の偶発的な発音ゆれと判断しました。したがって、文章自体の書き換えや「くく」の表記変更、No.2専用のwhitelistは行わず、<strong>音声を再生成するだけ</strong>で解決するとの判断です。上記4回の再生成のうち1件(試行2)を修正候補として採用します。
    </div>
  </div>

  <p class="footer-note">
    主観的な発音の自然さの最終判断はユーザー試聴によります。上の「Fixed」を実際に聞いて、採用可否をご判断ください。
  </p>
</div>
"""

html = HTML_TEMPLATE.replace("__ORIG_URI__", uris["orig"]).replace("__FIXED_URI__", uris["fixed"])
out_path = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad/er007/no2_pronunciation_fix.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print("written", out_path, len(html))
