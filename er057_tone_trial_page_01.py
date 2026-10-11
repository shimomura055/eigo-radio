# ============================================================
# er057_tone_trial_page_01.py (Trial専用、委任_01A) 試聴ページ生成
# ============================================================
from __future__ import annotations
import html, json, os
import er057_tone_trial_tts_gen_01 as G

WEB = os.path.join(G.ROOT, "user_test", "coffee_tone_trial_01", "intro_preview_fullstory")
man = json.load(open(os.path.join(G.OUT, "assembly_manifest_01A.json"), encoding="utf-8"))
cost = json.load(open(os.path.join(G.OUT, "cost_actual_01A.json"), encoding="utf-8"))
actual = {r["job"]: r for r in cost["records"] if r.get("success")}
sec = lambda k: man["items"][k]["seconds"]
esc = html.escape
TOPIC = "Today's topic is Coffee Bean Prices Fall. Are Price Tags Still on a Journey?."
JTITLE = "コーヒー豆は値下がり。値札は、まだ旅の途中？"
TTS_NOTE = "gemini-3.8-flash-lite-tts / speech_metadata_flash_lite相当 / Standard同期"


def audio(name, label=None):
    return f'<audio controls preload="none" src="audio/{name}.mp3" data-name="{name}"></audio>'


def row(id_, title, desc, voice, text, name, extra="", style=None, secs=None):
    st = f'<details><summary>Prompt(style)</summary><pre>{esc(style)}</pre></details>' if style else ""
    return (f'<tr id="r_{id_}"><td class="id"><b>{esc(id_)}</b><br>{esc(title)}<br><span class="sec">{secs if secs is not None else sec(name)}秒</span></td>'
            f'<td class="play">{audio(name)}</td>'
            f'<td class="txt"><div class="desc">{esc(desc)}</div><div class="voice">Voice: {esc(voice)} / {esc(extra) if extra else TTS_NOTE}</div>'
            f'<div class="script">{esc(text)}</div>{st}</td></tr>')


def table(rows):
    return '<table><thead><tr><th>仕様</th><th>音声</th><th>説明・Voice・Script</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"


def build():
    S = G.SPECS
    A_rows = [row("A0", "既存(Baseline)", "現行shell(Master Store、Charon、style=natural, clear, conversational)", "Charon", G.TEXT_A, "A0", "Master Store再利用(既存音声)")]
    B_rows = [row("B0", "既存(Baseline)", "現行shell(Master Store、Charon、style=natural, clear, conversational)", "Charon", G.TEXT_B, "B0", "Master Store再利用(既存音声)")]
    for g, rows_ in (("A", A_rows), ("B", B_rows)):
        for k, (nm, ds, st) in S[g]["items"].items():
            rows_.append(row(k, nm, ds, "Charon", S[g]["text"], k, style=st))
    pat_rows = []
    for n in range(6):
        a = "A0 既存" if n == 0 else f"A{n} {S['A']['items'][f'A{n}'][0]}"
        b = "B0 既存" if n == 0 else f"B{n} {S['B']['items'][f'B{n}'][0]}"
        flow = (f"Intro(音楽ジングル・読み上げなし) → Welcome[{a}] → pause → Topic intro(既存・Aoede)「{TOPIC}」 → pause → Japanese title(既存・Aoede)「{JTITLE}」 → "
                f"通知音(読み上げなし) → Preview intro[{b}] → 終端")
        pat_rows.append(row(f"通し{n}" if n else "通しBaseline", "既存A+既存B" if n == 0 else f"A{n}+B{n}",
                            flow, "Welcome/Preview intro=Charon, Topic intro/Japanese title=Aoede", f"A: {G.TEXT_A}  /  B: {G.TEXT_B}", f"pattern_{n}"))
    E_rows = [row("E0", "既存(Baseline)", "現行Advanced Preview(Style: E2_UPBEAT、既存run dirのb1b/preview.wav)", "Charon", G.TEXT_E, "E0", "既存音声", secs=sec("E0"))]
    for k, (nm, ds, st) in S["E"]["items"].items():
        E_rows.append(row(k, nm, ds, "Charon", G.TEXT_E, k, style=st))
    F_adv = [row("F_既存", "既存Advanced Part1(全文)", "現行Advanced Full Story Part1(F1.5)。既存音声は第1段落以降(ICO/USDA等)も続く全文。候補は冒頭段落のみ", "Aoede",
                 "(冒頭段落は下記F0と同一。以降に続く本文はこの試聴ページでは未取得=原稿テキスト省略)", "F_existing_adv", "既存音声")]
    F_adv.append(row("F0", "現行F1.5(同一原稿再生成)", "公平比較用: 現行Style F1.5で候補と同一原稿(冒頭段落のみ)を再生成", "Aoede", G.TEXT_F, "F0", style=G.EN_FULLSTORY_F1_5))
    for k, (nm, ds, st) in S["F"]["items"].items():
        F_adv.append(row(k, nm, ds, "Aoede", G.TEXT_F, k, style=st))
    F_std = [row("F_既存Std", "既存Standard Part1(全文・別原稿)", "現行Standard Full Story Part1(F1.5+減速指示+6%減速)。Standardの原稿は易しく書き換えられており本文が異なる(参考)", "Aoede",
                 "(Standard版Part1は別原稿。テキストはこの試聴ページでは未取得=省略)", "F_existing_std", "既存音声")]
    F_std.append(row("F0S", "現行Standard方式再現", "F1.5+既承認の減速指示で生成→6%減速(atempo)。Advanced原稿と同一原稿での現行Standard再現", "Aoede", G.TEXT_F, "F0S_std",
                     "生成+ローカル6%減速", style=G.F_BASELINE_EXTRA["F0S"][2]))
    F_std.append(row("F0+6%", "現行F1.5を6%減速", "F0に既存の6%減速のみ適用", "Aoede", G.TEXT_F, "F0_std", "生成+ローカル6%減速", style=G.EN_FULLSTORY_F1_5))
    for k, (nm, ds, st) in S["F"]["items"].items():
        F_std.append(row(f"{k}+6%", nm + "(6%減速版)", ds + " さらにStandard相当の既存6%減速を適用。", "Aoede", G.TEXT_F, f"{k}_std", "生成+ローカル6%減速", style=st))

    def sel(id_, label, opts):
        return f'<label>{label} <select id="{id_}">' + "".join(f'<option value="{v}">{esc(t)}</option>' for v, t in opts) + "</select></label>"
    aopts = [("0", "A0 既存")] + [(str(i), f"A{i} {S['A']['items'][f'A{i}'][0]}") for i in range(1, 6)]
    bopts = [("0", "B0 既存")] + [(str(i), f"B{i} {S['B']['items'][f'B{i}'][0]}") for i in range(1, 6)]
    page = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><title>Coffee Tone Trial 01A: 共通Intro / Advanced Preview / Full Story</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}}
table{{border-collapse:collapse;width:100%;margin-bottom:1.5em}}th,td{{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}}
td.id{{width:150px}}td.play{{min-width:380px}}td.play audio{{min-width:360px;width:100%}}
.sec{{color:#666;font-size:.85em}}.voice{{color:#555;font-size:.85em}}.script{{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}}
.desc{{font-size:.9em}}pre{{white-space:pre-wrap;font-size:.8em;background:#fafafa;margin:2px}}
.combo{{background:#eef6ff;padding:10px;border:1px solid #99c}}nav a{{margin-right:1em}}
</style></head><body>
<h1>Coffee Tone Trial 01A: 共通Intro / Advanced Preview / Full Story</h1>
<p>FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01A(Trial。Production未変更)。仕様名は中立(A1〜A5等)で、アプローチ説明を併記しています(Blindではありません)。
どれも採用候補ではなく比較用です。Model: {TTS_NOTE}。</p>
<nav><a href="#intro">1. 共通Intro(A/B)</a><a href="#e">2. Advanced Preview</a><a href="#f">3. Full Story(Aoede)</a></nav>

<h2 id="intro">1. 共通Intro(Welcome=A / Preview導入=B)</h2>
<p>実際のEpisode冒頭(Intro → Welcome → Topic intro → Japanese title → 通知音 → Preview intro)にAとBを組み込んだ通し音声です。Intro・Topic intro・Japanese title・通知音は既存音声(全パターン共通)。</p>
<div class="combo"><b>AとBを独立選択して通し再生</b><br>
{sel("selA", "A(Welcome)", aopts)} {sel("selB", "B(Preview導入)", bopts)}
<button id="comboPlay">通し再生</button> <button id="comboStop">停止</button> <span id="comboStatus">停止中</span></div>
<h3>通し(固定の組合せ: A_n+B_n と Baseline)</h3>
{table(pat_rows)}
<h3>A単独: "{esc(G.TEXT_A)}"(Charon)</h3>{table(A_rows)}
<h3>B単独: "{esc(G.TEXT_B)}"(Charon)</h3>{table(B_rows)}

<h2 id="e">2. Advanced Preview(英語・Charon)</h2>
<p>Advanced Previewの英語。現行(E0)に対し、少し遅め・落ち着き・自然なニュース調の聞きやすさを狙った5仕様。</p>
{table(E_rows)}

<h2 id="f">3. Full Story(Aoede、Standard/Advanced共通Style)</h2>
<p>Part1冒頭段落のみで比較(各約20秒)。Styleは両Level共通(新設なし)。Advanced相当=生成そのまま、Standard相当=同じ生成音声へ既存の6%機械減速(FFmpeg atempo、pitch保持)をローカル適用。</p>
<h3>Advanced相当(生成そのまま)</h3>{table(F_adv)}
<h3>Standard相当(6%減速適用)</h3>{table(F_std)}
<script>
const nm=(p)=>'audio/'+p+'.mp3';
let chain=[],idx=0,cur=null;
function stop(){{if(cur){{cur.pause();cur=null}}chain=[];document.getElementById('comboStatus').textContent='停止中'}}
function next(){{
  if(idx>=chain.length){{document.getElementById('comboStatus').textContent='再生完了';cur=null;return}}
  const a=new Audio(nm(chain[idx]));cur=a;document.getElementById('comboStatus').textContent='再生中: '+chain[idx]+' ('+(idx+1)+'/'+chain.length+')';
  a.onended=()=>{{idx++;next()}};a.onerror=()=>{{document.getElementById('comboStatus').textContent='エラー: '+chain[idx]}};a.play();
}}
document.getElementById('comboPlay').onclick=()=>{{stop();const A=document.getElementById('selA').value,B=document.getElementById('selB').value;
  chain=['part_head','A'+A,'part_mid','B'+B,'part_tail'];idx=0;next()}};
document.getElementById('comboStop').onclick=stop;
document.addEventListener('play',e=>{{document.querySelectorAll('audio').forEach(x=>{{if(x!==e.target)x.pause()}})}},true);
</script></body></html>"""
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(page)
    assert "file:///" not in page and "C:\\" not in page and "C:/" not in page
    print("page written", len(page))


if __name__ == "__main__":
    build()
