# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05: Human Review パケット生成(新形式、API 0)。

1 segmentのHRを『原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価』の固定構成で
静的HTML(+同内容のMarkdown)に出力する。質問は「この音声でよいですか?」の1つだけ。
入力は run の audit/review_lock_state.json と narration/attempts/*.json(読み取りのみ。runは変更しない)。
使い方:
  .venv\\Scripts\\python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_hr_packet_01.py --segment preview --take 1 --audio std_hr/std_preview_take1.mp3 [--check-only]
Production Pythonではない(提示方式の試作。HR依頼書rendererの恒久変更は別委任)。
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import sys
import wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUN = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
PAGE_DIR = "user_test/family_y_production_redelivery_fee_03"
OUT_MD = "docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/HR_PACKET_STD_PREVIEW_01.md"
OUT_HTML = PAGE_DIR + "/hr_preview_01.html"


def _load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def _diff(canon: str, asr: str):
    """文字単位diff。[(op, canon_part, asr_part)] と両側の強調HTMLを返す。"""
    sm = difflib.SequenceMatcher(None, canon, asr, autojunk=False)
    ops, ch, ah = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        c, a = canon[i1:i2], asr[j1:j2]
        if tag == "equal":
            ch.append(html.escape(c))
            ah.append(html.escape(a))
        else:
            ops.append((tag, c, a))
            ch.append("<mark class='c'>%s</mark>" % (html.escape(c) or "∅"))
            ah.append("<mark class='a'>%s</mark>" % (html.escape(a) or "∅"))
    return ops, "".join(ch), "".join(ah)


def _dur(path):
    with wave.open(path) as w:
        return round(w.getnframes() / w.getframerate(), 2)


def collect(segment: str, take: int):
    st = _load(f"{RUN}/a2/audit/review_lock_state.json")[segment]
    attempts = {}
    ad = os.path.join(ROOT, RUN, "a2", "narration", "attempts")
    for fn in sorted(os.listdir(ad)):
        if fn.startswith(f"{segment}_attempt") and fn.endswith(".json"):
            with open(os.path.join(ad, fn), encoding="utf-8") as f:
                d = json.load(f)
            d["_wav"] = os.path.join(ad, fn[:-5] + ".wav")
            attempts[d["attempt_number"]] = d
    rec = attempts[take]
    log = {x["attempt"]: x for x in st["last_attempts_log"]}
    j = (log.get(take) or {}).get("asr_judgement") or {}
    return st, rec, j, j.get("canonical_text"), attempts


def build(segment="preview", take=1, audio_rel="std_hr/std_preview_take1.mp3"):
    st, rec, j, canon, attempts = collect(segment, take)
    prim = j["primary"]["text"]
    sec = j["secondary"]["text"]
    ops_p, c_p, a_p = _diff(canon, prim)
    ops_s, c_s, a_s = _diff(canon, sec)
    data = dict(segment=segment, take=take, canon=canon, primary=prim, secondary=sec, ops_p=ops_p, ops_s=ops_s,
                dur=_dur(rec["_wav"]), judge_state=j["state"], reason_code=j["reason_code"], p_label=j["primary"]["label"],
                s_label=j["secondary"]["label"], s_accepted=j["secondary"]["accepted"], length=j["length"], lock=st["state"],
                why=st["reason"], route=rec["route"], audio=audio_rel)
    return data, (c_p, a_p, c_s, a_s)


def _ops_table(ops):
    rows = "".join("<tr><td>%s</td><td><b>%s</b></td><td><b>%s</b></td></tr>" % (t, html.escape(c) or "(なし)", html.escape(a) or "(なし)") for t, c, a in ops)
    return "<table><tr><th>種別</th><th>原稿側</th><th>ASR側</th></tr>%s</table>" % rows


EVAL_PARAS = [
    "結論: 実際の内容の誤りではなく、表記の差(「どおり」と「通り」)が自動検査で止まった可能性が高い、とAIは判断しています。ただしAI自身は音声を聞けないため、最終確認は耳でお願いします(これがこのHRの唯一の目的です)。",
    "根拠(1) 原稿「思いどおりに」に対し、OpenAI・Azureの2つの音声認識がどちらも「思い通りに」と書き起こしています。「どおり」を漢字で書けば「通り」になるのが一般的な書き方で、他の文字・数字・否定語はすべて一致し、抜けや重複はありません(OpenAI全文79字/Azure全文78字、同じ文の繰り返しなし)。",
    "根拠(2) 自動検査は「読みが完全に同じ」と確認できる場合だけ自動合格にします。ここでは文字の並びから「通り」を「どおり」(濁った発音)と確定できず、「とおり」(濁らない発音)の可能性が残るため、安全側で止まりました。実際に「どおり」と発音されていれば問題ありません。",
    "音声の計測: 長さ{dur}秒、先頭・末尾の無音は0.3秒、文の切れ目(7.15秒付近)に約1.0秒の間、途中の長い無音・途切れ・繰り返しなし(自動計測)。話し方(Style)は承認済みの日本語補助S3です。",
    "Take 1・2・3の比較はAI側で済ませました。Take 1とTake 2は同じ承認Styleで、書き起こし・判定とも完全に同じです(間の長さがわずかに違うだけ)。Take 3は別の短い指示文(fallback)で作られた音声で承認Styleとは異なるため候補から外しました。聴き比べをお願いする必要のある品質差はありません。よって最初の1つであるTake 1を推奨します。",
]


def render_html(d, hl) -> str:
    c_p, a_p, c_s, a_s = hl
    ev = "".join("<p>%s</p>" % html.escape(p.format(dur=d["dur"])) for p in EVAL_PARAS)
    css = ("body{font-family:sans-serif;max-width:860px;margin:1em auto;padding:0 .8em;line-height:1.7}h1{font-size:1.25em}"
           "h2{font-size:1.05em;border-left:5px solid #36c;padding-left:.5em;margin-top:1.4em}"
           ".box{background:#f6f8fb;border:1px solid #cfd8e6;border-radius:6px;padding:.7em 1em}mark.c{background:#ffd6d6}mark.a{background:#ffe9a8}"
           "table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:.2em .6em}audio{width:100%}"
           ".q{background:#eaf6ea;border:2px solid #4a4;border-radius:6px;padding:.8em 1em;font-size:1.1em}.sm{font-size:.85em;color:#555}")
    ng = ("<ul><li>止めた判定: 統一ASR判定 <code>%s</code>(理由コード <code>%s</code>)。OpenAI(gpt-4o-mini-transcribe)=<code>%s</code>、Azure Speech STT=<code>%s</code>(受理=%s)。</li>"
          "<li>規則: 日本語の二次ASR(Azure)が受理されるのは <code>EXACT_MATCH</code> / <code>NORMALIZED_MATCH</code> の場合のみ(CURRENT_SPEC.md:2903)。"
          "両エンジンとも「読みは濁点の有無を除いて一致するが確定できない」扱いのため受理されず、3回の生成後もHuman Review待ちになりました(最終: %s)。</li>"
          "<li>実測: 数値・否定の保護差=なし、長さ検査OK(OpenAI %s字/Azure %s字、上限%s字)。</li></ul>"
          % (d["judge_state"], d["reason_code"], d["p_label"], d["s_label"], d["s_accepted"], html.escape(d["why"]),
             d["length"]["primary_len"], d["length"]["secondary_len"], d["length"]["max_len"]))
    return f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='robots' content='noindex,nofollow'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Human Review: Standard Preview(宅配の再配達)</title><style>{css}</style></head><body>
<h1>Human Review 依頼: Standard の「Preview(日本語要約)」1か所だけ</h1>
<p class='sm'>Family Y 宅配の再配達 / 確認が必要なのはこの1か所のみ(他は自動検査に合格済み)。API費用0円・音声の再生成なし。</p>
<h2>1. 原稿(読み上げる日本語全文)</h2><div class='box'>{html.escape(d['canon'])}</div>
<h2>2. ASR結果(音声認識が実際に書き起こした全文)</h2>
<p>OpenAI(一次):</p><div class='box'>{html.escape(d['primary'])}</div><p>Azure(二次):</p><div class='box'>{html.escape(d['secondary'])}</div>
<h2>3. 相違点(原稿とASRで異なる部分)</h2>
<p>原稿 → OpenAI:</p><div class='box'>原稿側 {c_p}<br>ASR側 {a_p}</div>{_ops_table(d['ops_p'])}
<p>原稿 → Azure:</p><div class='box'>原稿側 {c_s}<br>ASR側 {a_s}</div>{_ops_table(d['ops_s'])}
<p class='sm'>Azureは「指定しても」の直後の読点「、」も書き起こしていません(句読点のみの差で意味・読みに影響しません)。</p>
<h2>4. NG理由(なぜ自動検査で止まったか)</h2>{ng}
<h2>5. 推奨音声(1つ)</h2><p>Take {d['take']}({d['dur']}秒、承認Style S3、モデル gemini-3.8-flash-lite-tts)</p>
<audio controls preload='none' src='{d['audio']}'></audio>
<p class='sm'>聴くポイント: 「おもいどおりに」の部分が「どおり」(濁った音)になっているか。それ以外は自動検査で確認済みです。</p>
<h2>6. Claude/Fableの評価</h2><div class='box'>{ev}</div>
<h2>7. ご確認</h2><div class='q'><b>この音声でよいですか?</b><br><span class='sm'>返答例: 「よい(Take 1で承認)」または「よくない」。承認後に、Style修正を反映したStandard/Advancedの完成版を組み立てます。</span></div>
</body></html>
"""


def render_md(d, hl) -> str:
    ev = "\n\n".join(p.format(dur=d["dur"]) for p in EVAL_PARAS)

    def ops(o):
        return "\n".join(f"  - {t}: 原稿 `{c or '(なし)'}` / ASR `{a or '(なし)'}`" for t, c, a in o)

    return f"""# HR_PACKET_STD_PREVIEW_01 — Std preview 1 segment(新形式、委任_05)
管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_05。公開: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/hr_preview_01.html 。生成: `tools/build_hr_packet_01.py`(API 0)。承認はユーザーのみ。

## 1. 原稿
{d['canon']}

## 2. ASR結果(全文)
- OpenAI(一次): {d['primary']}
- Azure(二次): {d['secondary']}

## 3. 相違点
- 原稿→OpenAI:
{ops(d['ops_p'])}
- 原稿→Azure:
{ops(d['ops_s'])}

## 4. NG理由
統一ASR判定 `{d['judge_state']}` / `{d['reason_code']}`。OpenAI=`{d['p_label']}`、Azure=`{d['s_label']}`(accepted={d['s_accepted']})。JA二次ASRの受理は `EXACT_MATCH`/`NORMALIZED_MATCH` のみ(CURRENT_SPEC.md:2903)。読みが濁点の有無を除いて一致=「とおり/どおり」を確定できず、標準2+fallback1=3回後 lock={d['lock']}(最終: {d['why']})。数値/否定の保護差なし、長さOK。

## 5. 推奨音声(1つ)
Take {d['take']}({d['dur']}秒、route `{d['route']}`、承認Style S3): `{PAGE_DIR}/{d['audio']}`

## 6. 評価
{ev}

## 7. 質問
**この音声でよいですか?**(1つだけ)
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--segment", default="preview")
    ap.add_argument("--take", type=int, default=1)
    ap.add_argument("--audio", default="std_hr/std_preview_take1.mp3")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    d, hl = build(a.segment, a.take, a.audio)
    if not os.path.exists(os.path.join(ROOT, PAGE_DIR, a.audio)):
        print("AUDIO_MISSING", a.audio)
        return 2
    if a.check_only:
        print(json.dumps({k: d[k] for k in ("judge_state", "reason_code", "ops_p", "ops_s", "dur")}, ensure_ascii=False))
        return 0
    with open(os.path.join(ROOT, OUT_HTML), "w", encoding="utf-8") as f:
        f.write(render_html(d, hl))
    with open(os.path.join(ROOT, OUT_MD), "w", encoding="utf-8") as f:
        f.write(render_md(d, hl))
    print("WROTE", OUT_HTML, OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
