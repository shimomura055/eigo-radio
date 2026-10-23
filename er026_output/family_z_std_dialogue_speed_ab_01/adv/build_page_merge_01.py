# -*- coding: utf-8 -*-
"""委任_03: 既存index.html(Standard、HEAD版)にAdvanced節と比較条件表を追加(API 0)。Standard節・Standard mp3は不変。"""
import json, os, html, shutil, subprocess, sys
os.chdir("C:/Users/tensh/eigo-radio")
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"; PAGE = "user_test/family_z_std_dialogue_speed_ab_01"
esc = html.escape; TITLE = {"melos": "走れメロス", "open_window": "開いた窓"}
base = subprocess.run(["git", "show", f"HEAD:{PAGE}/index.html"], capture_output=True, check=True).stdout.decode("utf-8")
if "_adv'" in base: sys.exit("HEAD page already has Advanced")
A = json.load(open(f"{OUT}/adv/analysis_adv.json", encoding="utf-8")); ASR = json.load(open(f"{OUT}/adv/asr_qa_adv_B.json", encoding="utf-8"))
secs = {}
for story in ("melos", "open_window"):
    d = f"{PAGE}/audio_{story}/adv"; os.makedirs(d, exist_ok=True)
    for f in os.listdir(f"{OUT}/adv/{story}/mp3"): shutil.copyfile(f"{OUT}/adv/{story}/mp3/{f}", f"{d}/{f}")
    S = A[story]["summary"]; asr = {r["id"]: r for r in ASR[story]}; rows = []; n = 0
    for r in A[story]["rows"]:
        if r["kind"] != "dialogue": continue
        n += 1; a = asr[r["id"]]; k = f"{story}adv{n}"
        note = "一致" if a["exact_norm_match"] else f"差あり(類似度{a['similarity']}。A版の事後ASR記録と同一テキスト=B固有の新規欠陥ではない)"
        rows.append(f"<tr><td class='id'><b>会話 {n}</b><br>{esc(str(r['speaker']))}<br><span class='sec'>Voice: {esc(str(r['voice']))}</span><br><span class='sec'>{esc(r['id'])}</span></td>"
            f"<td class='txt'><div class='script'>{esc(r['text'])}</div><div class='sec'>{r['words']}語 / Production ASR(B): {note}</div></td>"
            f"<td class='play'><b>A 現行(速度変更なし)</b> {r['A_sec']:.2f}秒 / {r['A_wpm']:.0f} WPM<audio id='a{k}A' controls preload='none' src='audio_{story}/adv/d{n:02d}_A.mp3'></audio>"
            f"<b>B Trial(機械処理で約6%高速化)</b> {r['B_sec']:.2f}秒 / {r['B_wpm']:.0f} WPM<audio id='a{k}B' controls preload='none' src='audio_{story}/adv/d{n:02d}_B.mp3'></audio>"
            f"<button class='seq' data-a='a{k}A' data-b='a{k}B'>A→B 連続再生</button></td>"
            f"<td>{r['A_wpm']:.0f} → {r['B_wpm']:.0f}<br>(+{r['B_wpm']-r['A_wpm']:.0f} WPM / 長さ比 {r['ratio_B_over_A']:.3f})</td></tr>")
    def row(l, a, b): return f"<tr><td>{l}</td><td>{a}</td><td>{b}</td><td>{b-a:+.1f}</td></tr>"
    wpm = ("<table><thead><tr><th>指標(語/分)</th><th>A 現行</th><th>B Trial</th><th>差</th></tr></thead><tbody>"
        + row(f"会話clip 中央値(全{S['n_dialogue']}clip)", S["dlg_A_wpm_median"], S["dlg_B_wpm_median"])
        + row(f"会話clip 中央値(8語以上 {S['n_ge8']}clip)", S["dlg_A_wpm_ge8"], S["dlg_B_wpm_ge8"])
        + row("会話clip 総語数÷総時間(加重)", S["dlg_A_wpm_weighted"], S["dlg_B_wpm_weighted"])
        + row(f"参考: Narrator clip 中央値(全{S['n_narrator']}clip、A=B不変)", S["narr_wpm_median"], S["narr_wpm_median"])
        + row(f"参考: Narrator clip 中央値(8語以上 {S['narr_n_ge8']}clip、A=B不変)", S["narr_wpm_ge8_median"], S["narr_wpm_ge8_median"])
        + row("参考: Narrator clip 加重(A=B不変)", S["narr_wpm_weighted"], S["narr_wpm_weighted"])
        + f"</tbody></table><p class='sec'>通し全体 {S['A_dur']:.1f}秒 → {S['B_dur']:.1f}秒(差 {S['A_dur']-S['B_dur']:.1f}秒)。会話clipの長さ比(B/A) {S['ratio_min']:.4f}〜{S['ratio_max']:.4f}。</p>")
    ident = ("<table><thead><tr><th>同一性の確認(A/B)</th><th>結果</th></tr></thead><tbody>"
        f"<tr><td>会話以外のclip(Narrator・コメント・導入等)のファイル同一(sha256)</td><td>{S['nondialogue_clip_sha_equal']} / {S['nondialogue_clip_total']} 一致(速度変更なし)</td></tr>"
        f"<tr><td>会話clipのファイル</td><td>{S['n_dialogue']} clip が別ファイル(Bはatempo 1.06適用)</td></tr>"
        "<tr><td>台詞テキスト・Voice(話者)</td><td>同一(同じTTS take・同じ台本)</td></tr>"
        f"<tr><td>再生順</td><td>{'同一' if S['order_equal'] else '相違'}</td></tr>"
        f"<tr><td>A版の再組立とProduction公開音声の一致</td><td>{'sha256完全一致' if S['A_rebuild_equals_production'] else '不一致'}</td></tr>"
        f"<tr><td>Production ASR(en-US)でB会話clipを検査</td><td>{sum(r['exact_norm_match'] for r in ASR[story])} / {len(ASR[story])} 正規化完全一致(残りはA版の事後ASR記録と同一テキスト)</td></tr></tbody></table>")
    secs[story] = (f"<h2 id='{story}_adv'>{TITLE[story]} Advanced</h2>"
        "<div class='note'><b>変更内容(Advanced)</b>: 登場人物の会話clipだけ、生成済み原音を機械処理(ffmpeg atempo 1.06、音程保持)で約6%高速化したのがB。Narrator・コメント・導入・効果音・Voice・本文・順序は不変。</div>"
        f"<div class='combo'><b>A 現行版 通し再生</b>({S['A_dur']:.0f}秒)<audio controls preload='none' src='audio_{story}/adv/full_A.mp3'></audio><br>"
        f"<b>B Trial版(会話のみ約6%高速化) 通し再生</b>({S['B_dur']:.0f}秒)<audio controls preload='none' src='audio_{story}/adv/full_B.mp3'></audio></div>"
        f"<h3>会話の実測速度</h3>{wpm}<h3>同一性</h3>{ident}<h3>会話ごとのA/B比較(同じ台詞を並べて再生)</h3>"
        "<table><thead><tr><th>話者</th><th>台詞</th><th>A / B 再生</th><th>WPM A→B</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")
html_ = base
html_ = html_.replace("Family Z Standard 会話速度 A/B比較試聴(Trial)", "Family Z 会話速度 A/B比較試聴(Standard/Advanced、Trial)")
nav = ("<nav><a href='#melos'>走れメロス Standard</a><a href='#melos_adv'>走れメロス Advanced</a>"
       "<a href='#open_window'>開いた窓 Standard</a><a href='#open_window_adv'>開いた窓 Advanced</a></nav>")
i0 = html_.index("<nav>"); i1 = html_.index("</nav>") + 6
cond = ("<div class='note'>Trial(比較試聴用)です。Production仕様・既存完成音声は変更していません。会話(登場人物の台詞)だけを比較します。採用・不採用はこの比較試聴の後にご判断ください(作品×レベルの4組それぞれA/Bをお選びいただけます)。</div>"
  "<h3>比較条件(何が変わるか)</h3><table><thead><tr><th>項目</th><th>A:現行版</th><th>B:Trial版</th></tr></thead><tbody>"
  "<tr><td>Standard Narrator</td><td>6%減速</td><td>変更なし(A=B)</td></tr>"
  "<tr><td>Standard 会話</td><td>6%減速</td><td><b>減速処理を撤去</b></td></tr>"
  "<tr><td>Advanced Narrator</td><td>速度変更なし</td><td>変更なし(A=B)</td></tr>"
  "<tr><td>Advanced 会話</td><td>速度変更なし</td><td><b>機械処理で約6%高速化</b>(音程保持)</td></tr>"
  "<tr><td>Voice・Prompt・本文・順序・効果音</td><td>現行版</td><td>変更なし</td></tr></tbody></table>")
# remove old intro note
j0 = html_.index("<div class='note'>", i1); j1 = html_.index("</div>", j0) + 6
html_ = html_[:i0] + nav + cond + html_[j1:]
for story in ("melos", "open_window"):
    h = html_.index(f"<h2 id='{story}'>")
    nxt = html_.find("<h2 id=", h + 5); nxt = nxt if nxt > 0 else html_.index("<script>")
    html_ = html_[:nxt] + secs[story] + html_[nxt:]
open(f"{PAGE}/index.html", "w", encoding="utf-8").write(html_)
print(len(html_), sum(len(os.listdir(f"{PAGE}/audio_{s}/adv")) for s in secs))
