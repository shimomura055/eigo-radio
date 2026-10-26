# -*- coding: utf-8 -*-
"""試聴ページ生成(Trial、Production未採用): user_test/family_y_voice_pause_trial_01/index.html + audio/*.mp3。API 0。
mp3は既存経路(er121_family_y_audio_01.build_v1_candidates系)と同じ設定: soundfile→imageio_ffmpeg libmp3lame 96k。
各音声は「最終音声」(Std=6%減速後=Productionでユーザーが聴く音)。停止統計は同じ最終音声の実測(表のraw attempt値とは別)。"""
import glob, html, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yvp_measure_lib_01 as lib

T = "docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01"
OUT = "user_test/family_y_voice_pause_trial_01"
R = lib.RUN01
TR = "er121_output/family_y_voice_pause_trial_01"
VN = {1: "Voice 1 (Algieba)", 2: "Voice 2 (Zephyr)", 3: "Voice 3 (Schedar)"}
LVN = {"a2": "Standard", "b1b": "Advanced"}


def items(lv):
    """{(b,v): [(label, kind[reuse|fresh], wav, status)]}"""
    d = {}
    def add(b, v, label, kind, wav, status):
        if wav and os.path.exists(wav):
            d.setdefault((b, v), []).append((label, kind, wav, status))
    add(1, 1, "現行(採用済み)", "reuse", f"{R}/{lv}/narration/y_voice_1.wav", "採用済み")
    for k in (1, 2, 3):
        rp = f"{R}/{lv}/hr_adopt_prep/voice1_candidates/take{k}/result.json"
        if os.path.exists(rp):
            r = json.load(open(rp, encoding="utf-8"))
            w = r.get("wav")
            if lv == "a2" and r.get("status") != "OK":
                w2 = os.path.join(os.path.dirname(w), "y_voice_1_slowed6pct.wav")
                w = w2 if os.path.exists(w2) else w
            add(1, 1, f"候補take{k}", "reuse", w, r.get("status"))
    for i in (2, 3):
        add(i, i, "現行(採用済み)", "reuse", f"{R}/{lv}/narration/y_voice_{i}.wav", "採用済み")
    for rp in sorted(glob.glob(f"{TR}/{lv}/body*_voice*/take*/result.json")):
        m = re.search(r"body(\d)_voice(\d)[\\/]take(\d+)", rp)
        b, v, k = int(m.group(1)), int(m.group(2)), int(m.group(3))
        r = json.load(open(rp, encoding="utf-8"))
        add(b, v, f"新規take{k}", "fresh", r.get("wav"), r.get("status"))
    return d


def mp3(wav, out):
    import imageio_ffmpeg, soundfile as sf
    x, sr = sf.read(wav, dtype="float32")
    tmp = out + ".tmp.wav"
    sf.write(tmp, x, sr)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "96k", out], check=True)
    os.remove(tmp)


def main():
    os.makedirs(f"{OUT}/audio", exist_ok=True)
    S = json.load(open(f"{T}/measure/summary.json", encoding="utf-8"))
    parts = ["<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             "<title>Voice 1 ポーズ原因切り分けTrial(Production未採用)</title><style>body{font-family:sans-serif;max-width:1180px;margin:auto;padding:8px}"
             "table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:4px;vertical-align:top;font-size:13px}.sec{color:#555;font-size:12px}"
             ".b{display:inline-block;background:#eef;border-radius:3px;padding:1px 4px;margin:1px;font-size:12px}.w{background:#fdd}.t{background:#ffe;border:2px solid #c90;padding:6px}"
             "audio{width:100%;height:30px}</style></head><body>",
             "<h1>『宅配の再配達は有料にすべきか?』 Voice 1 長ポーズ原因切り分けTrial</h1>",
             "<p class='t'><b>Trial(検証用)。Production未採用</b>: 正式音声・公開ページ(宅配 本編)は変更していません。Voice・Style・選別方式の変更は、ユーザー判断までは何も行いません。"
             "数値は無音検出(-40 dBFS・150ms以上、120ms未満の有音は結合)の実測で、品質の合否ではありません。聴き比べて自然さを判断してください。</p>",
             "<p class='sec'>各表は 行=<b>誰の本文か</b>(本文1=Voice 1担当 / 本文2=Voice 2担当 / 本文3=Voice 3担当)、列=<b>どのVoiceで読んだか</b>。"
             "同じ本文・同じ設定でVoiceだけを入れ替えています(新規=今回生成、再利用=既存の採用/候補音声)。Standardの音は6%減速後(本番で聴く音)。"
             "バッジ: <span class='b'>1秒以上の停止の回数</span><span class='b'>停止占有率</span><span class='b'>最長停止</span><span class='b'>尺</span>。赤=1秒以上の停止あり。</p>"]
    n = 0
    for lv in ("a2", "b1b"):
        it = items(lv)
        parts.append(f"<h2>{LVN[lv]}</h2><table><tr><th>本文＼読んだVoice</th>" + "".join(f"<th>{VN[v]}</th>" for v in (1, 2, 3)) + "</tr>")
        for b in (1, 2, 3):
            parts.append(f"<tr><th>本文{b}<br><span class='sec'>({VN[b]}担当)</span></th>")
            for v in (1, 2, 3):
                cell = []
                for label, kind, wav, status in it.get((b, v), []):
                    m = lib.measure_wav(wav, lib.body_text(lv, b))
                    fn = f"{lv}_b{b}v{v}_{re.sub('[^0-9a-zA-Z]+', '', label) or 'x'}_{abs(hash(wav)) % 10**6}.mp3"
                    # hash()はprocessごとに変わるため、決定的な名前にする
                    fn = f"{lv}_b{b}v{v}_{'cur' if label.startswith('現行') else ('cand' + label[-1] if label.startswith('候補') else 't' + label[-1])}.mp3"
                    mp3(wav, f"{OUT}/audio/{fn}")
                    n += 1
                    cls = "b w" if m["ge1000"] >= 1 else "b"
                    cell.append(f"<div><b>{html.escape(label)}</b> <span class='sec'>{'新規' if kind == 'fresh' else '再利用'}・{html.escape(str(status))}</span><br>"
                                f"<audio controls preload='none' src='audio/{fn}'></audio>"
                                f"<span class='{cls}'>1秒以上 {m['ge1000']}回</span><span class='b'>占有率 {m['occ_pct']}%</span><span class='b'>最長 {m['max_ms'] / 1000:.2f}秒</span><span class='b'>{m['dur_s']:.1f}秒</span></div>")
                parts.append("<td>" + ("".join(cell) if cell else "<span class='sec'>(なし)</span>") + "</td>")
            parts.append("</tr>")
        parts.append("</table>")
    L = S["levels"]
    parts.append("<h2>判定(自動集計・生成前に固定した基準)</h2><ul>")
    for lv in ("a2", "b1b"):
        for h in ("H1", "H2", "H3", "H5"):
            parts.append(f"<li>{LVN[lv]} {h}: {html.escape(L[lv][h]['verdict'])}</li>")
    rows = json.load(open(f"{T}/measure/samples_measured.json", encoding="utf-8"))
    parts.append("</ul><p class='sec'>「否定」=事前に決めた数値基準(停止占有率の差など)を満たさなかった、の意味で、「問題がない」ではありません。"
                 "Voice別の1秒以上の停止(生成した全sampleの平均回数 / 1回以上出たsampleの割合):</p><table><tr><th>レベル</th>" + "".join(f"<th>{VN[v]}</th>" for v in (1, 2, 3)) + "</tr>")
    for lv in ("a2", "b1b"):
        cells = []
        for v in (1, 2, 3):
            rs = [r for r in rows if r["level"] == lv and r["kind"] == "main" and r["voice"] == v]
            cells.append(f"{sum(r['ge1000'] for r in rs) / len(rs):.2f}回 / {100 * sum(1 for r in rs if r['ge1000'] >= 1) / len(rs):.0f}% (n={len(rs)})")
        parts.append(f"<tr><th>{LVN[lv]}</th>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    parts.append("</table><ul>")
    parts.append(f"<li>減速(H4a): {html.escape(S.get('H4a', {}).get('verdict', '-'))} / レベル差(H4b): {html.escape(S['H4b']['verdict'])}</li></ul>"
                 "<p class='sec'>H1=Voice固有 / H2=本文固有 / H3=生成ばらつき / H5=相互作用。詳細は RESULT_MATRIX_01.md(リポジトリ docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/)。</p></body></html>")
    open(f"{OUT}/index.html", "w", encoding="utf-8").write("\n".join(parts))
    print("mp3", n, "->", OUT)


if __name__ == "__main__":
    main()
