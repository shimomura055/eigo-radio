# -*- coding: utf-8 -*-
"""A/B比較試聴ページ生成(API 0)。mp3=lameenc 128kbps(assembled wavからtimelineで切り出し)。wavはpushしない。"""
import json, os, html, sys
import numpy as np, soundfile as sf, lameenc
sys.path.insert(0, "C:/Users/tensh/eigo-radio"); os.chdir("C:/Users/tensh/eigo-radio")
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"; PAGE = "user_test/family_z_std_dialogue_speed_ab_01"
TITLE = {"melos": "走れメロス", "open_window": "開いた窓"}
esc = html.escape


def mp3(path, x, sr):
    if x.ndim == 1:
        x = x[:, None]
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    e = lameenc.Encoder(); e.set_bit_rate(128); e.set_in_sample_rate(sr); e.set_channels(pcm.shape[1]); e.set_quality(2)
    open(path, "wb").write(e.encode(pcm.tobytes()) + e.flush())


A = json.load(open(f"{OUT}/analysis.json", encoding="utf-8"))
ASR = json.load(open(f"{OUT}/asr_qa_B.json", encoding="utf-8"))
os.makedirs(PAGE, exist_ok=True)
sections = []; nav = []
for story in ("melos", "open_window"):
    d = f"{PAGE}/audio_{story}"; os.makedirs(d, exist_ok=True)
    tl = {}; X = {}
    for v, sub in (("A", "A_rebuild"), ("B", "B")):
        t = json.load(open(f"{OUT}/{story}/{sub}/a2/assembly/timeline.json", encoding="utf-8"))
        x, sr = sf.read(t["wav"], dtype="float32"); X[v] = (x, sr); tl[v] = {e["part"]: e for e in t["timeline"]}
        mp3(f"{d}/{v}_full.mp3", x, sr)
    S = A[story]["summary"]; rows = A[story]["rows"]
    asr = {r["id"]: r for r in ASR[story]}
    drows = []; n = 0
    for r in rows:
        if r["kind"] != "dialogue":
            continue
        n += 1
        for v in ("A", "B"):
            e = tl[v][r["id"]]; x, sr = X[v]
            mp3(f"{d}/d{n:02d}_{v}.mp3", x[int(round(e["start_seconds"] * sr)): int(round((e["start_seconds"] + e["duration_seconds"]) * sr))], sr)
        a = asr[r["id"]]
        asr_note = "一致" if a["exact_norm_match"] else f"差あり(類似度{a['similarity']}。A版の事後ASR記録と同内容、または句読点差)"
        drows.append(
            f"<tr><td class='id'><b>会話 {n}</b><br>{esc(str(r['speaker']))}<br><span class='sec'>Voice: {esc(str(r['voice']))}</span><br><span class='sec'>{esc(r['id'])}</span></td>"
            f"<td class='txt'><div class='script'>{esc(r['text'])}</div><div class='sec'>{r['words']}語 / ASR(B): {asr_note}</div></td>"
            f"<td class='play'><b>A 現行(6%減速)</b> {r['A_sec']:.2f}秒 / {r['A_wpm']:.0f} WPM<audio id='a{story}{n}A' controls preload='none' src='audio_{story}/d{n:02d}_A.mp3'></audio>"
            f"<b>B Trial(減速なし)</b> {r['B_sec']:.2f}秒 / {r['B_wpm']:.0f} WPM<audio id='a{story}{n}B' controls preload='none' src='audio_{story}/d{n:02d}_B.mp3'></audio>"
            f"<button class='seq' data-a='a{story}{n}A' data-b='a{story}{n}B'>A→B 連続再生</button></td>"
            f"<td>{r['A_wpm']:.0f} → {r['B_wpm']:.0f}<br>(+{r['B_wpm'] - r['A_wpm']:.0f} WPM / 長さ比 {r['ratio']:.3f})</td></tr>")
    ge8 = S["A_wpm_ge8"]; ge8b = S["B_wpm_ge8"]

    def row(lbl, a, b):
        return f"<tr><td>{lbl}</td><td>{a}</td><td>{b}</td><td>{b - a:+.1f}</td></tr>"
    wpm = ("<table><thead><tr><th>指標(会話clip、語/分)</th><th>A 現行</th><th>B Trial</th><th>差</th></tr></thead><tbody>"
           + row(f"中央値(全{S['n_dialogue']}clip)", S["A_wpm_all"]["median"], S["B_wpm_all"]["median"])
           + row(f"平均(全{S['n_dialogue']}clip)", S["A_wpm_all"]["mean"], S["B_wpm_all"]["mean"])
           + row(f"中央値(8語以上 {S['n_ge8']}clip)", ge8["median"], ge8b["median"])
           + row("総語数÷総時間(加重)", S["weighted_A_wpm"], S["weighted_B_wpm"])
           + row("参考: Narrator clip中央値(A=B、6%減速維持)", S["narrator_A_wpm"]["median"], S["narrator_B_wpm"]["median"])
           + f"</tbody></table><p class='sec'>会話clip合計 {S['dialogue_A_sec']}秒 → {S['dialogue_B_sec']}秒。通し全体 {S['A_dur']:.1f}秒 → {S['B_dur']:.1f}秒(差 {S['A_dur'] - S['B_dur']:.1f}秒)。"
             f"会話clipの長さ比(A/B) {S['ratio_min']:.4f}〜{S['ratio_max']:.4f}。</p>")
    ident = ("<table><thead><tr><th>同一性の確認(A/B)</th><th>結果</th></tr></thead><tbody>"
             f"<tr><td>Narrator clip(Story内)のファイル同一(sha256)</td><td>{S['narrator_sha_equal']} / {S['n_narrator_story']} 一致(6%減速維持)</td></tr>"
             f"<tr><td>会話clipのファイル(減速あり/なし)</td><td>{S['dialogue_sha_differs']} / {S['n_dialogue']} が別ファイル(Bは減速前の原音)</td></tr>"
             f"<tr><td>減速前の原音に6%減速を再適用するとA版と完全一致</td><td>{S['atempo_reproduces_A']} / {S['n_dialogue']} clip(Bの原音=Aの元音声と確認)</td></tr>"
             "<tr><td>台詞テキスト・Voice(話者)</td><td>同一(同じTTS take・同じ台本。下表のText/Voiceは両版共通)</td></tr>"
             f"<tr><td>再生順(シーケンス)</td><td>{'同一' if S['order_equal'] else '相違'}</td></tr>"
             f"<tr><td>A版の再組立とProduction公開音声の一致</td><td>{'sha256完全一致' if S['A_rebuild_equals_production'] else '不一致'}</td></tr></tbody></table>")
    sec = (f"<h2 id='{story}'>{TITLE[story]} Standard</h2>"
           f"<div class='combo'><b>A 現行版 通し再生</b>({S['A_dur']:.0f}秒)<audio controls preload='none' src='audio_{story}/A_full.mp3'></audio><br>"
           f"<b>B Trial版(会話の6%減速なし) 通し再生</b>({S['B_dur']:.0f}秒)<audio controls preload='none' src='audio_{story}/B_full.mp3'></audio></div>"
           f"<h3>会話の実測速度</h3>{wpm}<h3>同一性</h3>{ident}<h3>会話ごとのA/B比較(同じ台詞を並べて再生)</h3>"
           "<table><thead><tr><th>話者</th><th>台詞</th><th>A / B 再生</th><th>WPM A→B</th></tr></thead><tbody>" + "".join(drows) + "</tbody></table>")
    sections.append(sec); nav.append(f"<a href='#{story}'>{TITLE[story]}</a>")
css = ("<style>body{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.2em}"
       "th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}audio{width:100%}.sec{color:#666;font-size:.85em}"
       ".script{background:#f6f6f6;padding:4px;white-space:pre-wrap}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}"
       ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}nav a{margin-right:1.2em;font-weight:bold}button.seq{margin-top:4px;cursor:pointer}</style>")
js = ("<script>document.querySelectorAll('button.seq').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.a),c=document.getElementById(b.dataset.b);"
      "a.currentTime=0;c.currentTime=0;a.onended=()=>c.play();a.play();});</script>")
intro = ("<div class='note'>Trial(比較試聴用)です。Production仕様は変更していません。Standardの会話(登場人物の台詞)だけ、生成後6%減速を外したB版を用意しました。"
         "Narrator、Voice、台詞本文、再生順、効果音はA/Bで同一です。Advancedは変更していません。採用・不採用はこの比較試聴の後にご判断ください。</div>")
page = (f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>Family Z Standard 会話速度 A/B比較試聴(Trial)</title>{css}</head><body>"
        f"<h1>Family Z Standard 会話速度 A/B比較試聴(Trial)</h1><nav>{''.join(nav)}</nav>{intro}{''.join(sections)}{js}</body></html>")
open(f"{PAGE}/index.html", "w", encoding="utf-8").write(page)
print(len(page), sorted(os.listdir(PAGE)))
