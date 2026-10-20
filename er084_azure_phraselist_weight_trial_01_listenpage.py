# -*- coding: utf-8 -*-
"""[v02] 簡易試聴ページ生成(API 0、ユーザー指示§5)。user_test/plw_trial_01/{index.html,audio/*.mp3}。

収載: (1)NG→PASS系にflipしたwav全件 (2)PASS→NGにflipしたwav全件 (3)負例の誤PASS・Azure誤Melos全件(あれば)
(4)境界例(N2/N4)全件。各行に原稿・実際に話した文(TTS原稿)・Primary転写・条件別Azure転写と本番判定(2 role)を併記。
音声は元wav(不変)を再エンコードしたmp3(precedent=er058_05b_listen_page_01.pyのto_mp3と同じ正規化)。
"""
import argparse
import html
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

import er002_common as common
import er003_b1_p9a_audio as p9a
import er084_azure_phraselist_weight_trial_01_eval_v02 as E
import er084_azure_phraselist_weight_trial_01_judge as J
import er084_azure_phraselist_weight_trial_01_lib as L

TARGET = 0.09932  # 既存試聴ページ(er058_05b_listen_page_01)と同じtarget_rms
CONDS = ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0")


def to_mp3(wav, out_path):
    mono = common.read_wav_float(wav)[0]
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    st = p9a.mono_24k_to_stereo_target(mono * gain)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sf.write(out_path, np.clip(st, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")


def pick_rows(ev: "E.Evaluator", ov: dict) -> list:
    secs = []
    up, down = {}, {}
    for w, we in ov["weights"].items():
        for role in E.ROLES:
            for a in we["roles"][role]["up_ids"]:
                up.setdefault(a, []).append(f"{w}/{role}")
            for a in we["roles"][role]["down_ids"]:
                down.setdefault(a, []).append(f"{w}/{role}")
    secs.append(("1. 本番判定がNG→PASS系にflipしたwav(誤発音の見逃しでないか確認)", [(a, ", ".join(t)) for a, t in sorted(up.items())]))
    secs.append(("2. 本番判定がPASS→NGに悪化したwav", [(a, ", ".join(t)) for a, t in sorted(down.items())]))
    fp = {}
    for w, we in ov["weights"].items():
        for k, v in we["negatives_detail"].items():
            for a in v["false_pass_ids"]:
                fp.setdefault(a, set()).add(f"誤PASS:{k}")
        for c, v in we["false_melos_detail"].items():
            for a in v["false_melos_ids"]:
                fp.setdefault(a, set()).add(f"Azure誤Melos:{c}")
    new = {}
    for w in ("pl_w1.5", "pl_w2.0"):
        for r in E.new_false_pass(ev, w, "full_story"):
            new.setdefault(r["audio_id"], []).append(w)
    rows3 = []
    for a, t in sorted(fp.items()):
        lab = ("★重みが新たに作った誤PASS(" + ",".join(new[a]) + ") / " if a in new else "ベースライン(現行)から既に誤PASS / ") + ", ".join(sorted(t))
        rows3.append((a, lab))
    secs.append(("3. 負例の誤PASS・Azure誤Melos(minimal pair/N1/N3。★=重みで新たに生じたもの)", rows3))
    secs.append(("4. 境界例(N2 mellows / N4 Milos。判定には使っていない別枠)", [(a, "境界例") for a in ev.ids(("NEG_BOUNDARY",))]))
    return secs


def row_html(ev, aid, tag, rid, audio_rel):
    m = ev.meta[aid]
    trs = []
    for c in CONDS:
        r = ev.cells.get((aid, c), {}).get(1)
        if not r:
            continue
        s_full = ev.judge(aid, r["text"], "full_story")["state"]
        s_no = ev.judge(aid, r["text"], "no_tier3")["state"]
        trs.append(f"<tr><td>{c}</td><td>{html.escape(r['text'])}</td><td>{s_full}</td><td>{s_no}</td></tr>")
    spoken = ""
    if m["text"] != m["canonical_text"]:
        spoken = f'<div class="s mis">TTSに渡した文(意図した読み): {html.escape(m["text"])}</div>'
    return (f'<div class="row" data-id="{html.escape(aid)}"><div class="hd"><span class="id">{html.escape(aid)}</span>'
            f'<audio controls preload="none" src="{audio_rel}"></audio><span class="v">{html.escape(str(m["voice"]))}{" 減速6%" if m["slow6"] else ""} / {m["set"]}</span>'
            f'<span class="tag">{html.escape(tag)}</span></div>'
            f'<div class="s"><b>判定用の原稿:</b> {html.escape(m["canonical_text"])}</div>{spoken}'
            f'<div class="s"><b>Primary(OpenAI)転写:</b> {html.escape(m["primary_text"] or "")}</div>'
            f'<table class="asr"><tr><th>Azure条件</th><th>Azure転写</th><th>本番判定(FULL_STORY role)</th><th>本番判定(Tier3なしrole)</th></tr>{"".join(trs)}</table>'
            f'<div class="j"><label><input type="radio" name="{rid}" value="Melosと正しく読んでいる">Melosと正しく読んでいる</label>'
            f'<label><input type="radio" name="{rid}" value="Melosと読んでいない(誤読)">誤読</label>'
            f'<label><input type="radio" name="{rid}" value="不明">不明</label></div></div>')


HEAD = """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Azure PhraseList重み比較Trial 試聴ページ(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 / Trial・未承認)</title>
<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:1.8em}
.row{border:1px solid #ccc;border-radius:6px;padding:.5em .9em;margin:.7em 0}.hd{display:flex;gap:.8em;align-items:center;flex-wrap:wrap}.hd .id{font-weight:bold}.hd .v{color:#06c;font-size:.85em}.tag{background:#eef;border-radius:4px;padding:0 .4em;font-size:.8em}
audio{height:32px;min-width:360px}.s{margin:.2em 0}table.asr{border-collapse:collapse;font-size:.85em;margin:.3em 0}table.asr td,table.asr th{border:1px solid #ddd;padding:.15em .5em;text-align:left}
.j label{margin-right:1em}.note{color:#555;font-size:.9em}#out{width:100%;height:9em;font-family:monospace}.mis{color:#b00}</style></head><body>
<h1>Azure PhraseList重み比較Trial 試聴ページ(Trial・Production未採用)</h1>
<p class="note">Azure Secondary ASRのPhraseList重み(未指定=現行/1.5/2.0)で「Melos」の認識と本番判定がどう変わったかのTrialです。重みを上げて判定が<b>NG→PASSに変わったwav</b>が、本当に「Melos」と読まれているか(誤発音の見逃しになっていないか)を耳で確認するための一覧です。Blindではありません。
各行に判定用の原稿・TTSに渡した文・OpenAI(Primary)転写・条件別のAzure転写と本番判定を併記しています。聞いたあと各行で選び、末尾の「結果をテキスト化」で出る文章をそのまま返信に貼ってください(このページはサーバーに送信しません)。
音声は短いclip(合成短文または本番clip)で、完成episodeではありません。Production判定は変更していません。</p>"""
TAIL = """<h2>結果をテキスト化</h2><button id="mk">結果をテキスト化</button><br><textarea id="out" readonly></textarea>
<script>document.getElementById('mk').onclick=function(){var o=[];document.querySelectorAll('.row').forEach(function(r){var c=r.querySelector('input:checked');o.push(r.dataset.id+': '+(c?c.value:'未回答'));});document.getElementById('out').value=o.join('\\n');};</script></body></html>"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--primary", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--manifest2", required=True)
    ap.add_argument("--production-takes", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--page-dir", required=True)
    a = ap.parse_args(argv)
    crit = json.load(open(a.thresholds, encoding="utf-8"))
    meta = E.load_meta(json.load(open(a.manifest, encoding="utf-8")), json.load(open(a.manifest2, encoding="utf-8")),
                       json.load(open(a.production_takes, encoding="utf-8")), L.read_raw(a.primary), J.ROLE_FULL_STORY_SEGMENT)
    ev, ov, _extra = E.run_eval(L.read_raw(a.raw), meta, crit)
    secs = pick_rows(ev, ov)
    H, n, total = [HEAD], 0, 0
    for title, items in secs:
        H.append(f"<h2>{html.escape(title)}({len(items)}件)</h2>")
        if not items:
            H.append('<p class="note">該当なし。</p>')
        for aid, tag in items:
            n += 1
            name = re.sub(r"[^A-Za-z0-9_]+", "_", aid).strip("_") + ".mp3"
            out_mp3 = os.path.join(a.page_dir, "audio", name)
            if not os.path.exists(out_mp3):
                to_mp3(os.path.join(L.ROOT, ev.meta[aid]["path"]), out_mp3)
                total += 1
            H.append(row_html(ev, aid, tag, f"r{n}", "audio/" + name))
    H.append(TAIL)
    os.makedirs(a.page_dir, exist_ok=True)
    open(os.path.join(a.page_dir, "index.html"), "w", encoding="utf-8").write("\n".join(H))
    print(json.dumps({"rows": n, "mp3_new": total, "sections": {t: len(i) for t, i in secs}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
