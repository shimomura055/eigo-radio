# -*- coding: utf-8 -*-
"""ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 D: 『新たにPASSになる保存segment』の試聴リスト(ユーザー採用判断の材料)。
入力: bfix_before_after_01.json(B修正でNG->PASSになった保存行) + stored_onoff_compare_02.json(er109をONにしたときNG->PASSになる保存行、whisper再転写つき)。
保存wavは変更せずmp3へ変換コピー(既存ページ体裁 er107_fx_kp_audio_ng3_listen_page_01.py に合わせる)。API 0 / TTS 0。
使い方: python er109_new_pass_listen_page_01.py"""
from __future__ import annotations
import hashlib, html, json, os, subprocess, sys
sys.path.insert(0, ".")
import imageio_ffmpeg
import er104_kp_three_asr_vote_01 as vote
import er109_stored_onoff_compare_01 as onoff

D = "docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/"
OUT = "user_test/aho_new_pass_listen_01"
FF = imageio_ffmpeg.get_ffmpeg_exe()


def mp3(src, dst):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-codec:a", "libmp3lame", "-b:a", "96k", dst], check=True)


def main():
    os.makedirs(OUT + "/audio", exist_ok=True)
    on = json.load(open(D + "stored_onoff_compare_02.json", encoding="utf-8"))
    bf = json.load(open(D + "bfix_before_after_01.json", encoding="utf-8"))
    wh = {(r["wav"], r["canonical"]): r for r in on.get("whisper_recheck", []) if "whisper" in r}
    rows = []
    for x in bf["NG_to_PASS_items"]:
        if not x["set"].startswith("stored_"):
            continue
        rows.append(dict(by="B修正(承認済み規則の不具合是正)", family=onoff.family_of(x["src"]), seg=x["seg"], attempt=x.get("attempt"), canonical=x["c"], asr=x["a"],
                         kind=x["set"].replace("stored_", ""), rule=f'{x["result"]["label"]} -> {x["after"]["label"]}', warn="", src=x["src"], wav=onoff.find_wav(x["src"], x["seg"], x.get("attempt"))))
    for x in on["NG_to_PASS"]:
        rows.append(dict(by="er109(未配線・採用判断待ち)", family=x["family"], seg=x["seg"], attempt=x.get("attempt"), canonical=x["c"], asr=x["a"], kind=x["kind"],
                         rule=",".join(x["on"].get("rules") or []), warn=",".join(x["on"].get("warnings") or []), src=x["src"], wav=x.get("wav")))
    seen, uniq = set(), []
    for r in rows:
        k = (r["by"], r["canonical"], r["asr"], r["seg"], r["src"], r["attempt"], r["kind"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    data = []
    for i, r in enumerate(uniq, 1):
        r["id"] = f"R{i:02d}"
        if r["wav"] and os.path.isfile(r["wav"]):
            r["wav_sha256"] = hashlib.sha256(open(r["wav"], "rb").read()).hexdigest()
            r["page_audio"] = f"audio/{r['id']}.mp3"
            mp3(r["wav"], f"{OUT}/{r['page_audio']}")
            w = wh.get((r["wav"], r["canonical"]))
            if w is None:
                try:
                    r["whisper"] = vote.whisper_transcribe(r["wav"])
                except Exception as e:     # noqa: BLE001
                    r["whisper"] = f"(Whisper失敗: {type(e).__name__})"
            else:
                r["whisper"] = w["whisper"]
        data.append(r)
    json.dump({"generated_by": "er109_new_pass_listen_page_01.py", "api_calls": 0, "cost_jpy": 0, "rows": data}, open(D + "new_pass_listen_list_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    H = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>新たにPASSになる保存音声の試聴リスト(同音・表記違い対策)</title><style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 .6em}',
         'table{border-collapse:collapse;width:100%;font-size:.88em}td,th{border:1px solid #bbb;padding:5px;vertical-align:top}th{background:#eee}',
         'audio{width:220px;max-width:100%}.tbl{overflow-x:auto}.note{background:#f4f4f4;padding:.5em;border-radius:6px;font-size:.9em}.warn{color:#b60}</style></head><body>',
         '<h2>新たにPASSになる保存音声の試聴リスト(運営者向け)</h2>',
         '<p>これは「発音が同じなのに表記が違うだけ」(例: <code>one\'s</code> と <code>1\'s</code>)で不合格になっていた保存音声のうち、(1) 承認済み規則の不具合を直す修正(B修正)で新たに合格になるもの、(2) 提案中の共通層(er109、<b>未配線・採用判断待ち</b>)を有効にした場合に新たに合格になるもの、の一覧です。'
         '<b>実際に聴いて、期待文どおりに読まれているかを確認してください。</b></p>',
         '<p class="note">ASRの転写は事実の並記で、発音の正否の断定ではありません。「Whisper(参考)」は保存wavをローカルのfaster-whisper(small/int8、費用0)で再転写した参考値です。'
         'wavが無い行(古い実行で音声が残っていない)は転写のみの表示です。合計 %d 行(重複除く)。</p>' % len(data),
         '<div class="tbl"><table><tr><th>#</th><th>区分/Family</th><th>期待文(canonical)</th><th>ASR転写(保存)</th><th>Whisper(参考)</th><th>適用された規則</th><th>再生</th></tr>']
    for r in data:
        aud = f'<audio controls preload="none" src="{r["page_audio"]}"></audio>' if r.get("page_audio") else "<small>(wav無し)</small>"
        warn = f' <span class="warn">警告: {html.escape(r["warn"])}</span>' if r["warn"] else ""
        H.append(f'<tr><td>{r["id"]}</td><td>{html.escape(r["by"])}<br><small>{html.escape(r["family"])} / {html.escape(str(r["seg"]))} #{r["attempt"]} ({r["kind"]})</small></td>'
                 f'<td><code>{html.escape(r["canonical"][:400])}</code></td><td><code>{html.escape(r["asr"][:400])}</code></td>'
                 f'<td><code>{html.escape((r.get("whisper") or "-")[:400])}</code></td><td><small>{html.escape(r["rule"])}</small>{warn}</td><td>{aud}</td></tr>')
    H.append('</table></div><hr><p><small>出典: bfix_before_after_01.json / stored_onoff_compare_02.json(docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/)。'
             'VALIDATED/採用の判断はFable・ユーザー。本ページは採用判断の材料です。</small></p></body></html>')
    open(OUT + "/index.html", "w", encoding="utf-8").write("\n".join(H))
    print("rows", len(data), "with_wav", sum(1 for r in data if r.get("page_audio")))


if __name__ == "__main__":
    main()
