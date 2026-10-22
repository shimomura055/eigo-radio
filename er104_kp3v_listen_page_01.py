# ============================================================
# er104_kp3v_listen_page_01.py  (API 0 / TTS 0 / Production経路外)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02 (Opus P-10): 3-ASR多数決で「旧方式NG→新方式PASS」に変わった4本
# (think up / blurt / cause a stir #3 / #4) の**運営者向け任意試聴ページ**を生成する(ユーザーの承認依頼ではない)。
# 既存音声は読み取りのみ(mp3へ変換コピー)。判定内容は stored_audio_reeval_02.json(本番adapter経路の再評価結果)から読む。
# 使い方: python er104_kp3v_listen_page_01.py --reeval docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_02.json --out user_test/kp3v_vote_evidence_01
# ============================================================
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, ".")
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PICK = [("byus_survey7", "think up"), ("byus_survey7", "blurt"), ("er096_stats24_attempts", "kp22#3"), ("er096_stats24_attempts", "kp22#4")]
NOTES = {
    "think up": "ユーザー試聴(2026-10-22): PASS(正しく聞こえる)。旧方式=NG(Azureが『Think.』)・多数決=PASS(OpenAI+Whisper)。",
    "blurt": "ユーザー試聴(2026-10-22): 語末のt音が聞こえず発音に懸念。ASR 2/3 PASS(Azure+Whisper)でも人間は聞こえなかった事例=多数決方式の限界(品質知見、仕様変更なし)。行4=SECONDARY_CONFIRMED警告で事後試聴リスト対象。",
    "kp22#3": "人間聴取ラベルなし(Production生成物)。OpenAIのみ『Causeister』、Azure・Whisperは『Cause a stir』。PASSの妥当性は未聴取。",
    "kp22#4": "人間聴取ラベルなし(Production生成物)。OpenAIのみ『Cause of stir.』、Azure・Whisperは『Cause a stir』。PASSの妥当性は未聴取。",
}


def mp3(src, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src, "-codec:a", "libmp3lame", "-b:a", "128k", dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reeval", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(a.reeval, encoding="utf-8"))
    rows = {(r["corpus"], r["id"].split("(")[0]): r for r in d["rows"]}
    os.makedirs(f"{a.out}/audio", exist_ok=True)
    cards = []
    for corpus, rid in PICK:
        r = rows[(corpus, rid)]
        key = r["canonical"].replace(" ", "_")
        dst = "audio/" + re.sub(r"[^A-Za-z0-9]+", "_", f"{key}_{rid}").strip("_") + ".mp3"
        mp3(r["wav"], f"{a.out}/{dst}")
        ad = r["adapter"]
        cards.append(f"""<section><h2>{html.escape(r['canonical'])} <small>({html.escape(rid)})</small></h2>
<audio controls preload="none" src="{dst}"></audio>
<table><tr><th>系統</th><th>転写</th></tr>
<tr><td>OpenAI(Primary)</td><td>{html.escape(str(r['primary']['text']))} <b>[{'PASS' if ad['primary_pass'] else 'NG'}]</b></td></tr>
<tr><td>Azure(Secondary)</td><td>{html.escape(str(r['secondary']['text']))} <b>[{'PASS' if ad['secondary_pass'] else 'NG'}]</b></td></tr>
<tr><td>Whisper small(local)</td><td>{html.escape(str(ad['whisper_text']))} <b>[{'PASS' if ad['whisper_pass'] else 'NG'}]</b></td></tr></table>
<p>旧方式(両方PASS必須)={'PASS' if r['prior_script_old_dual_pass'] else 'NG'} / 新方式(3-ASR多数決, 本番adapter経路)=<b>{'PASS' if ad['verified'] else 'NG'}</b> (行={html.escape(str(ad['row']))}, state={html.escape(str(ad['vote_state']))}, warnings={html.escape(str(ad['warnings']))})</p>
<p class="note">{html.escape(NOTES[rid])}</p></section>""")
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>KP 3-ASR多数決 判定変化4本の試聴(運営者向け・任意)</title>
<style>body{{font-family:sans-serif;max-width:860px;margin:2em auto;padding:0 1em}}section{{border:1px solid #ccc;border-radius:8px;padding:1em;margin:1.2em 0}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:4px 10px}}.note{{background:#fff8dc;padding:.5em;border-radius:6px}}</style></head><body>
<h1>KP 3-ASR多数決: 旧方式NG→新方式PASSに変わった4本(運営者向け・任意試聴)</h1>
<p>これはユーザーの承認依頼ではありません。多数決(OpenAI・Azure・Whisper 2/3)で旧「両方PASS必須」から判定が変わった音声を、運営者が任意で聴いて確認するためのページです。
判定は本番adapter経路(<code>stored_audio_reeval_02.json</code>)の再評価結果です(API 0)。</p>
{''.join(cards)}
</body></html>"""
    open(f"{a.out}/index.html", "w", encoding="utf-8").write(page)
    print("wrote", f"{a.out}/index.html", len(cards), "cards")


if __name__ == "__main__":
    main()
