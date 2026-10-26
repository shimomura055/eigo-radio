# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: 男性7Voice比較試聴ページ(Trial、Production未採用)。API 0。
使い方: py ym7_page_01.py --summary measure/summary_01.json --out user_test/family_y_voice1_male7_trial_01/index.html [--focus Fenrir]
 音声=各takeの「最終音声」(Stdは6%減速後=本番でユーザーが聴く音)。Voice×本文×レベルごとに 典型(長停止数が中央値に最も近い)/長停止最多/最良 を提示(focus VoiceとAlgiebaは上位5件)。
 mp3は64kbps mono(試聴用圧縮。リポジトリ容量のため)。"""
import argparse, glob, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ym7_measure_01 as m7          # noqa: E402  (lib経由で既存計測toolを使用)
lib = m7.lib

R = lib.RUN01
FRESH = "er121_output/family_y_voice1_male7_trial_01"
PREV = "er121_output/family_y_voice_pause_trial_01"
VOICES = ["Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager"]
VINFO = {"Algieba": "現行Voice 1・Smooth", "Schedar": "現行Voice 3・Even", "Fenrir": "Excitable", "Orus": "Firm", "Puck": "Upbeat", "Iapetus": "追加・Clear", "Sadaltager": "追加・Knowledgeable"}
LVN = {"a2": "Standard", "b1b": "Advanced"}
SLOT = {"Algieba": 1, "Schedar": 3}


def take_items(lv, b, voice):
    """[(label, kind, wav, status)] final wav。"""
    out = []
    def add(label, kind, wav, status):
        if wav and os.path.exists(wav):
            out.append((label, kind, wav.replace("\\", "/"), status))
    for rp in sorted(glob.glob(f"{FRESH}/{lv}/body{b}_{voice}/take*/result.json")):
        r = json.load(open(rp, encoding="utf-8"))
        add(f"新規take{r['take']}", "fresh", r.get("wav"), r.get("status"))
    if voice in SLOT:
        v = SLOT[voice]
        for rp in sorted(glob.glob(f"{PREV}/{lv}/body{b}_voice{v}/take*/result.json")):
            r = json.load(open(rp, encoding="utf-8"))
            add(f"前回take{r['take']}", "reuse", r.get("wav"), r.get("status"))
        if v == b:
            add("現行(採用済み)", "reuse", f"{R}/{lv}/narration/y_voice_{b}.wav", "採用済み")
        if voice == "Algieba" and b == 1:
            for k in (1, 2, 3):
                rp = f"{R}/{lv}/hr_adopt_prep/voice1_candidates/take{k}/result.json"
                if os.path.exists(rp):
                    r = json.load(open(rp, encoding="utf-8"))
                    w = r.get("wav")
                    if lv == "a2" and r.get("status") != "OK" and w:
                        w2 = os.path.join(os.path.dirname(w), "y_voice_1_slowed6pct.wav")
                        w = w2 if os.path.exists(w2) else w
                    add(f"候補take{k}(過去日)", "reuse", w, r.get("status"))
    return out


def mp3(wav, out):
    if os.path.exists(out):
        return
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "64k", out], check=True)


def pick(measured, focus):
    """measured: [(item, metrics)]。典型/長停止最多/最良(focusは上位5件)を返す。"""
    if not measured:
        return []
    ms = sorted(measured, key=lambda x: (x[1]["mid_long1000"], x[1]["occ_pct"]))
    med = ms[len(ms) // 2]
    worst = sorted(measured, key=lambda x: (-x[1]["mid_long1000"], -x[1]["max_ms"]))
    chosen, tags = [], []
    def take(x, tag):
        if all(x[0][2] != c[0][2] for c in chosen):
            chosen.append(x)
            tags.append(tag)
    take(med, "典型(中央値)")
    take(worst[0], "長停止が最多")
    take(ms[0], "最良")
    if focus:
        for x in worst[1:3]:
            take(x, "長停止が多い")
        for x in ms[1:3]:
            take(x, "良い")
    return list(zip(chosen, tags))[:5 if focus else 2]


def fmt_iv(d, nd=2):
    return f"{d['mean']:.{nd}f} [{d['lo']:.{nd}f}-{d['hi']:.{nd}f}]"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--focus", default="")
    a = ap.parse_args(argv)
    S = json.load(open(a.summary, encoding="utf-8"))
    outdir = os.path.dirname(a.out)
    os.makedirs(f"{outdir}/audio", exist_ok=True)
    cand = S["recommendation_check"].get("candidate_top") or a.focus or S["phase2_decision"]["best_by_mean"]
    focus_set = {"Algieba", cand} | set(S["recommendation_check"].get("recommend_candidates", []))
    texts = {(lv, b): lib.body_text(lv, b) for lv in ("a2", "b1b") for b in (1, 2, 3)}
    P = S["pooled"]
    h = ["<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Family Y Voice 1 男性7Voice比較(Trial・Production未採用)</title>"
         "<style>body{font-family:sans-serif;max-width:1200px;margin:auto;padding:8px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:4px;font-size:13px;vertical-align:top}"
         ".t{background:#ffe;border:2px solid #c90;padding:6px}.sec{color:#555;font-size:12px}.b{display:inline-block;background:#eef;border-radius:3px;padding:1px 5px;margin:1px;font-size:12px}.w{background:#fdd}"
         ".card{border:1px solid #aac;border-radius:6px;padding:6px;margin:6px 0}.foc{border:2px solid #36c;background:#f4f8ff}audio{width:100%;height:30px}.tab button{font-size:15px;padding:6px 12px;margin:2px}"
         ".sel{background:#36c;color:#fff}.hid{display:none}.txt{background:#f7f7f7;padding:6px;font-size:13px;line-height:1.5}</style></head><body>",
         "<h1>『宅配の再配達は有料にすべきか?』 Family Y Voice 1 男性7Voice比較</h1>",
         "<p class='t'><b>Trial(検証用)。Production未採用</b>: 正式音声・公開ページ・Voice割当は変更していません。数値は無音検出(-40 dBFS・150ms以上、120ms未満の有音は結合)による機械計測で、"
         "声質・人物像への適合は耳で判断してください。同じ本文・同じ設定(Style・モデル・減速)でVoice名だけを変えています。女性Voiceは含みません。</p>"]
    h.append("<h2>7名の統計(全本文・Standard+Advanced、6cell等重み。[ ]=95%区間)</h2><table><tr><th>Voice</th><th>声質</th><th>n(新規/再利用)</th><th>文中≥1秒の停止 回/sample</th><th>全≥1秒 回/sample</th><th>悪いtake率<br>(文中≥1秒が1回以上)</th>"
             "<th>占有率%</th><th>最長停止(平均/最悪)</th><th>ASR合格率</th><th>Repetition旗率</th></tr>")
    for v in VOICES:
        s = P.get(v)
        if not s:
            continue
        mark = " <b>(推奨候補1位)</b>" if v == S["recommendation_check"].get("candidate_top") else (" (推奨条件も満たす)" if v in S["recommendation_check"].get("recommend_candidates", []) else (" (現行)" if v == "Algieba" else ""))
        h.append(f"<tr><th>{v}{mark}</th><td>{VINFO[v]}</td><td>{s['n']} ({s['n_fresh']}/{s['n_reuse']})</td><td>{fmt_iv(s['mid_long1000'])}</td><td>{fmt_iv(s['long1000_n'])}</td><td>{fmt_iv(s['bad_mid'])}</td>"
                 f"<td>{s['occ_pct']['mean']:.1f}</td><td>{s['max_ms']['mean'] / 1000:.2f}s / {s['worst_max_ms'] / 1000:.2f}s</td><td>{100 * s['asr_pass']:.0f}%</td><td>{100 * s['rep_flag_i']['mean']:.0f}%</td></tr>")
    h.append("</table><p class='sec'>unit=生成の1回ごと(raw attempt)。ASR合格=自動文字起こしが本文と一致した割合、Repetition旗=繰り返し/言い直しの自動検出。数字が小さいほど長い不自然な停止が少ない(自然な文末の間は数えない)。"
             "Standard/Advancedの別・本文別の数値は各カードに表示。詳細・判定規則は docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/ (DESIGN_01.md / RESULT_01.md)。</p>")
    h.append("<div class='tab'><b>レベル:</b> " + "".join(f"<button id='lv_{lv}' onclick=\"setLv('{lv}')\">{LVN[lv]}</button>" for lv in ("a2", "b1b")) +
             " &nbsp; <b>本文:</b> " + "".join(f"<button id='bd_{b}' onclick=\"setBd({b})\">本文{b}</button>" for b in (1, 2, 3)) + "</div>")
    n_mp3 = 0
    for lv in ("a2", "b1b"):
        for b in (1, 2, 3):
            h.append(f"<div class='sect hid' id='s_{lv}_{b}'><h3>{LVN[lv]} / 本文{b}({len(texts[(lv, b)].split())}語、元の担当 Voice {b})</h3><div class='txt'>{html.escape(texts[(lv, b)])}</div>")
            cells = S["by_cell"][f"{lv}_b{b}"]
            for v in VOICES:
                foc = v in focus_set
                cs = cells.get(v)
                measured = []
                for item in take_items(lv, b, v):
                    m = lib.measure_wav(item[2], texts[(lv, b)])
                    m7.add_metrics(m)
                    measured.append((item, m))
                head = f"<b>{v}</b>{' ★推奨候補' if v == S['recommendation_check'].get('candidate_top') else (' (現行)' if v == 'Algieba' else '')} <span class='sec'>{VINFO[v]}</span> "
                if cs:
                    head += (f"<br><span class='b'>この本文×レベル: n={cs['n']}(新規{cs['n_fresh']}) 文中≥1秒 {cs['mid_long1000']['mean']:.2f}回/sample</span>"
                             f"<span class='b'>悪いtake率 {100 * cs['bad_mid']['mean']:.0f}%</span><span class='b'>ASR合格 {100 * cs['asr_pass']:.0f}%</span><span class='b'>旗 {100 * cs['rep_flag_i']['mean']:.0f}%</span>")
                h.append(f"<div class='card{' foc' if foc else ''}'>{head}")
                if not measured:
                    h.append("<br><span class='sec'>(音声なし)</span>")
                for (item, m), tag in pick(measured, foc):
                    label, kind, wav, status = item
                    fn = f"{lv}_b{b}_{v}_{re.sub(r'[^0-9A-Za-z]+', '', label.replace('新規take', 't').replace('前回take', 'p').replace('候補take', 'c').replace('現行', 'cur')) or 'x'}.mp3"
                    mp3(wav, f"{outdir}/audio/{fn}")
                    n_mp3 += 1
                    cls = "b w" if m["mid_long1000"] >= 1 else "b"
                    h.append(f"<div><span class='sec'>{html.escape(tag)}: {html.escape(label)}・{'新規' if kind == 'fresh' else '再利用'}・{html.escape(str(status))}</span><br><audio controls preload='none' src='audio/{fn}'></audio>"
                             f"<span class='{cls}'>文中≥1秒 {m['mid_long1000']}回</span><span class='b'>全≥1秒 {m['long1000_n']}回</span><span class='b'>占有率 {m['occ_pct']}%</span><span class='b'>最長 {m['max_ms'] / 1000:.2f}秒</span><span class='b'>{m['dur_s']:.1f}秒</span></div>")
                h.append("</div>")
            h.append("</div>")
    h.append("<h2>聞き分けの参考: 現行の Voice 2 / Voice 3(同じ記事の既存音声)</h2><p class='sec'>Voice 1の候補が、Voice 2(Zephyr・女性)・Voice 3(Schedar・男性30代)と聞き分けやすいかの確認用(各レベルの現行音声)。</p><table><tr><th>レベル</th><th>Voice 2 (Zephyr)</th><th>Voice 3 (Schedar)</th></tr>")
    for lv in ("a2", "b1b"):
        row = f"<tr><th>{LVN[lv]}</th>"
        for i in (2, 3):
            w = f"{R}/{lv}/narration/y_voice_{i}.wav"
            fn = f"ref_{lv}_v{i}.mp3"
            if os.path.exists(w):
                mp3(w, f"{outdir}/audio/{fn}")
                n_mp3 += 1
                row += f"<td><audio controls preload='none' src='audio/{fn}'></audio></td>"
            else:
                row += "<td>(なし)</td>"
        h.append(row + "</tr>")
    h.append("</table>")
    ph2 = S["phase2_decision"]
    rc = S["recommendation_check"]
    h.append("<h2>機械判定(事前固定した基準)</h2><ul>"
             f"<li>主要指標が最小のVoice: {html.escape(ph2['best_by_mean'])}。Phase 2対象: {html.escape(', '.join(ph2['phase2_voices']) or 'なし(差が明確)')}</li>"
             f"<li>推奨条件を全て満たすVoice: {html.escape(', '.join(rc['recommend_candidates']) or 'なし(現行維持)')}。最終推奨はFable/ユーザー判断で、このページは判断材料です。</li></ul>"
             "<script>var LV='a2',BD=1;function show(){document.querySelectorAll('.sect').forEach(e=>e.classList.add('hid'));document.getElementById('s_'+LV+'_'+BD).classList.remove('hid');"
             "['a2','b1b'].forEach(x=>document.getElementById('lv_'+x).classList.toggle('sel',x==LV));[1,2,3].forEach(x=>document.getElementById('bd_'+x).classList.toggle('sel',x==BD));}"
             "function setLv(x){LV=x;show();}function setBd(x){BD=x;show();}show();</script></body></html>")
    open(a.out, "w", encoding="utf-8").write("\n".join(h))
    print("mp3", n_mp3, "->", a.out, "focus", sorted(focus_set))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
