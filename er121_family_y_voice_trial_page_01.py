# -*- coding: utf-8 -*-
"""FY-STD-V2-FEMALE-VOICE-TRIAL-01: 比較試聴ページ生成(DEV/Trial専用)。mp3化+機械計測(声量・明るさ)+index.html。"""
import json, os, sys, hashlib, html
import numpy as np, soundfile as sf, lameenc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SRC = "er121_output/family_y_voice_trial_01/surname_v2"
PAGE = "user_test/family_y_surname_v2_voice_trial_01"
CANDS = [("c1", "Zephyr"), ("c2", "Kore"), ("c3", "Leda"), ("c4", "Sulafat"), ("c5", "Erinome")]
PROD = "er121_output/family_y_production_01/surname_choice/run_02/a2/narration/y_voice_2.wav"


def measure(path):
    x, sr = sf.read(path, always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float64)
    peak = float(np.max(np.abs(x)))
    fl = int(sr * 0.05)
    n = len(x) // fl
    fr = x[: n * fl].reshape(n, fl)
    rms_f = np.sqrt((fr ** 2).mean(axis=1) + 1e-12)
    db_f = 20 * np.log10(rms_f)
    act = db_f > -45
    rms_all = 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
    rms_act = 20 * np.log10(np.sqrt((fr[act] ** 2).mean()) + 1e-12) if act.any() else float("nan")
    spec = np.abs(np.fft.rfft(fr[act] * np.hanning(fl), axis=1)) ** 2
    fq = np.fft.rfftfreq(fl, 1 / sr)
    cent = float(((spec * fq).sum(axis=1) / (spec.sum(axis=1) + 1e-12)).mean())
    hi = float(spec[:, fq >= 2000].sum() / (spec.sum() + 1e-12))
    return {"duration_s": round(len(x) / sr, 2), "sr": sr, "peak_dbfs": round(20 * np.log10(peak + 1e-12), 2), "rms_all_dbfs": round(float(rms_all), 2),
            "rms_active_dbfs": round(float(rms_act), 2), "spectral_centroid_hz": round(cent, 0), "energy_above_2khz_pct": round(hi * 100, 1), "active_frame_pct": round(float(act.mean()) * 100, 1)}


def to_mp3(wav, mp3):
    x, sr = sf.read(wav, dtype="int16", always_2d=True)
    e = lameenc.Encoder(); e.set_bit_rate(128); e.set_in_sample_rate(sr); e.set_channels(x.shape[1]); e.set_quality(2)
    data = e.encode(x.tobytes()) + e.flush()
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    open(mp3, "wb").write(bytes(data))


def main():
    cc = json.load(open(f"{SRC}/common_conditions.json", encoding="utf-8"))
    rows, meas = [], {}
    for cid, v in CANDS:
        d = f"{SRC}/{cid}_{v}"
        r = json.load(open(f"{d}/result.json", encoding="utf-8"))
        m = measure(f"{d}/y_voice_2.wav")
        to_mp3(f"{d}/y_voice_2.wav", f"{PAGE}/audio/{cid}_{v}.mp3")
        meas[cid] = {"voice": v, "measure": m, "status": r.get("status"), "model": r.get("model"), "voice_used": r.get("voice"), "call_count": r.get("call_count"),
                     "retry_count": r.get("retry_count"), "asr_verified": r.get("asr_verified"), "wav_sha256": hashlib.sha256(open(f"{d}/y_voice_2.wav", "rb").read()).hexdigest()}
        rows.append((cid, v, m, meas[cid]))
    pm = measure(PROD)
    json.dump({"candidates": meas, "production_run02_reference": pm, "common": {k: cc[k] for k in ("style_profile", "tts_backend", "script_sha256")}},
              open(f"{SRC}/measurements.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cards = []
    for cid, v, m, mm in rows:
        cur = "(現行Voice=候補1)" if cid == "c1" else ""
        cards.append(f"<div class='card'><h3>候補{cid[1]}: {v} {cur}</h3><audio controls preload='none' src='audio/{cid}_{v}.mp3'></audio>"
                     f"<div class='sec'>status={mm['status']} / ASR検証={mm['asr_verified']} / 再試行={mm['retry_count']} / 長さ {m['duration_s']}s</div></div>")
    th = "<tr><th>候補</th><th>Voice</th><th>長さ(s)</th><th>声量: 有音区間RMS(dBFS)</th><th>全体RMS(dBFS)</th><th>ピーク(dBFS)</th><th>明るさ: スペクトル重心(Hz)</th><th>2kHz以上のエネルギー比(%)</th></tr>"
    tr = "".join(f"<tr><td>{cid[1]}</td><td>{v}</td><td>{m['duration_s']}</td><td>{m['rms_active_dbfs']}</td><td>{m['rms_all_dbfs']}</td><td>{m['peak_dbfs']}</td><td>{m['spectral_centroid_hz']:.0f}</td><td>{m['energy_above_2khz_pct']}</td></tr>" for cid, v, m, _ in rows)
    body = f"""<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow'>
<title>Family Y Standard Voice 2 女性Voice 5候補比較(Trial・採用はユーザー判断)</title>
<style>body{{font-family:sans-serif;max-width:980px;margin:auto;padding:8px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:4px;font-size:13px}}.t{{background:#ffe;border:2px solid #c90;padding:8px}}.card{{border:1px solid #aac;border-radius:6px;padding:6px;margin:8px 0}}audio{{width:100%}}.sec{{color:#555;font-size:12px}}.txt{{background:#f7f7f7;padding:8px;line-height:1.6}}</style></head><body>
<h1>夫が妻の姓を選ぶとき、それぞれの声 / Standard Full Story Voice 2(母親)女性Voice 5候補比較</h1>
<p class='t'><b>Trial(検証用)。Production未採用</b>: 正式音声・Voice割当は変更していません。同じ本文・同じ設定(Style・TTSモデル・6%減速・ASR検証)で<b>Voice名だけ</b>を変えています。音量の後処理はしていません。<b>採用はユーザー判断</b>です。</p>
<h2>評価観点</h2><p>聞き取りやすさ / 声量 / 感情表現の自然さ / 過度に暗くならないこと / 人物像(息子の結婚で寂しさを抱える母親)との適合。</p>
<h2>試聴</h2>{''.join(cards)}
<h2>機械計測(参考。声質・人物像への適合は耳で判断)</h2><table>{th}{tr}</table>
<p class='sec'>有音区間RMS=50ms frameのRMSが-45dBFSを超える区間の平均レベル(大きいほど声量が大きい)。スペクトル重心・2kHz以上比=大きいほど明るい。参照: 現行Production run_02 のy_voice_2.wav(候補1と同条件の既存音声)=有音区間RMS {pm['rms_active_dbfs']} dBFS / 重心 {pm['spectral_centroid_hz']:.0f} Hz。</p>
<h2>生成条件(全候補共通)</h2><table><tr><th>TTS backend</th><td>{html.escape(cc['tts_backend'])}</td></tr><tr><th>model_id</th><td>{html.escape(rows[0][3]['model'] or '')}</td></tr>
<tr><th>Style profile</th><td>{html.escape(cc['style_profile'])}(FULL_STORY。Standardの6%減速は生成後のtime-stretch+減速後ASR再検証)</td></tr><tr><th>Style/Prompt全文</th><td>{html.escape(cc['style_prefix'])}</td></tr>
<tr><th>候補のvoice_id</th><td>{', '.join(f'{c[1]}={v}' for c, v in CANDS)}</td></tr><tr><th>候補選定</th><td>Family Y女性Voice候補表(er121_family_y_structure_01.py:58)=Z承認済み女性5名。候補1=現行Zephyr。</td></tr></table>
<h2>スクリプト(5候補共通・Standard y_voice_2 全文)</h2><div class='txt'>{html.escape(cc['script_text'])}</div>
</body></html>"""
    open(f"{PAGE}/index.html", "w", encoding="utf-8").write(body)
    print(json.dumps(meas, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
