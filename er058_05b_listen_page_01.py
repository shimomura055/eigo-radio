# -*- coding: utf-8 -*-
"""委任_05B 未確定音声の試聴ページ生成(ローカル処理のみ、費用0円、API呼出なし、Production書込なし)。
Blindにしない(原稿・意図した誤読・各ASR転写・判定を併記)。ユーザーが「正しく読んだ/誤読/不明」を選べる構成。
出力: user_test/asr_misread_listen_01/{index.html,audio/*.mp3} と er058_output/trial_abc/listen_items_05B.json"""
import os, sys, json, html, io, contextlib, re

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import numpy as np
import soundfile as sf
import er002_common as common
import er003_b1_p9a_audio as p9a
import er058_trial_b_intentional_misread_01  # noqa  (stdout再ラップを先に済ませる)
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    import er058_05b_two_label_rejudge_01 as R  # Trial B の clip/判定/ground を再利用(読み取りのみ)
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)

PAGE = os.path.join(ROOT, "user_test", "asr_misread_listen_01")
AUD = os.path.join(PAGE, "audio")
os.makedirs(AUD, exist_ok=True)
TARGET = 0.09932  # Trial D試聴ページと同じtarget_rms(tone worktreeのgain_report、読取のみ)


def to_mp3(wav, name):
    mono = common.read_wav_float(wav)[0]
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    st = p9a.mono_24k_to_stereo_target(mono * gain)
    sf.write(os.path.join(AUD, name), np.clip(st, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")
    return "audio/" + name


def absp(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def tbl(canon, word, dur):
    """原稿中の語の位置から、再生位置の目安(秒)を出す(文字数比の概算。目安のみ)。"""
    i = canon.lower().find(word.lower()) if word else -1
    if i < 0 or not dur:
        return ""
    return f"(該当語は原稿の約{int(100 * i / max(1, len(canon)))}%付近=再生の約{dur * i / max(1, len(canon)):.0f}秒付近の目安)"


items = []

# ---------------- 1-3. Trial B ----------------
cl = {c["clip_id"]: c for c in R.nb2["clips"]}
B_PRI = ["en_inf1_mis", "en_prn1_mis", "en_voi1_mis", "ja_voi3_mis", "ja_prn3_mis"]
B_REST = [c["clip_id"] for c in R.nb2["clips"] if str(c["ground"]).startswith(("unverified", "homophone")) and c["clip_id"] not in B_PRI]
LISTEN_B = {"inflection": "語末(-ed/-s/複数形の有無)", "voicing": "語頭・語中の子音(濁音/清音)", "proper_noun": "固有名詞の綴り・発音",
            "homograph": "同形異音語(read/lead)の読み", "minimal_pair": "同音異義語(原稿と区別できるか)"}


def b_item(cid, sec):
    c = cl[cid]
    asr = []
    for s, lab in (("primary", "OpenAI Primary"), ("azure", "Azure(Phrase Listなし)"), ("local_medium", "ローカルwhisper medium")):
        a = c["asr"].get(s)
        if a:
            j = c["judge"][s]
            asr.append((lab, a["text"], ("PASS" if j["pass"] else "NG") + ":" + j["cls"]))
    items.append(dict(section=sec, id=cid, wav=os.path.join(R.ROOT, "er058_output", "trial_abc", "audio", cid + ".wav"), voice=c["voice"],
                      script=c["canonical"], intended=c["spoken"], asr=asr,
                      note="型=%s / ASR結論=%s(3系統とも原稿の形で転写。TTSが正しく読んだのか、ASRが丸めたのか区別できません)" % (c["type"], c["ground"]),
                      listen=LISTEN_B.get(c["type"], "")))


for cid in B_PRI:
    b_item(cid, "1. Trial B 未確定(優先5件)")
for cid in B_REST:
    b_item(cid, "2. Trial B 未確定(残り9件)")
b_item("ja_voi5_mis", "3. ja_voi5(Secondary原稿寄せ疑い)")
items[-1]["note"] = "Primaryは「点灯をつけた」でNG、Azure・localは「電気をつけた」でPASS。Azureが原稿に寄せたのか、TTSが本当に『でんき』と読んだのかを確認します(Secondary自動採用の安全性に直結)。"
items[-1]["listen"] = "「てんき」と「でんき」のどちらに聞こえるか"

# ---------------- 4. needs_listen 5(既存公開mp3を再利用) ----------------
rep = json.load(open(os.path.join(ROOT, "er056_output", "asr_tts_cross_language_reconciliation_01", "ja_offline_replay_01.json"), encoding="utf-8"))
wh = json.load(open(os.path.join(ROOT, "er053_output", "open258_phase0_trial_01", "whisper_aux_01.json"), encoding="utf-8"))
NL = ["g11_kp5_ja_aoede_a1", "g27_kp1_ja_charon_a1", "g18_meaning_2_a2", "g18_meaning_2_a3", "g1_meaning_4_a1"]
for r in rep["rows"]:
    if r["key"] not in NL:
        continue
    voice = "Aoede" if ("aoede" in r["key"] or "meaning" in r["key"]) else "Charon"
    w = wh.get(r["key"], {})
    asr = [("OpenAI Primary", r["primary"], "NG:" + r["primary_cls_now"]), ("Azure(Phrase Listなし)", r["secondary"], "PASS:" + r["secondary_cls_now"]),
           ("ローカルwhisper small", w.get("small", {}).get("text"), w.get("small", {}).get("cls_vs_canonical")),
           ("ローカルwhisper medium", w.get("medium", {}).get("text"), w.get("medium", {}).get("cls_vs_canonical"))]
    items.append(dict(section="4. 日本語 Phase 0 needs_listen(5音声、既存公開mp3を再利用)", id=r["key"], audio_rel="../open258_phase0_listen_01/" + r["key"].replace("_", "-") + ".mp3",
                      voice=voice, script=r["canonical"], intended="(意図的誤読ではなく実際の生成音声)", asr=asr,
                      note="Primary NG・Azure PASS(統一フロー/現行SCGとも採用される)。TTSが原稿どおり読んだのか、Primaryの聞き取り通りか未確定。",
                      listen="差分語(" + ", ".join("%s→%s" % (d[0], d[1]) for d in r["content_diffs"]) + ")"))

# ---------------- 5. Coffee showed / raw bean ----------------
SN = os.path.join(ROOT, "er056_output", "en_asr_confirm_retry_redesign_01", "evidence_snapshot")
a2 = json.load(open(os.path.join(SN, "a2_attempts", "full_story_part2_attempt2_customf1837a73.json"), encoding="utf-8"))
coffee_note = "(原稿全文は保存attempt jsonに未保存=推測補完しない。該当文のみASR転写から引用)"
items.append(dict(section="5. Coffee part2 の2点", id="coffee_part2_#2(showed)", wav=os.path.join(SN, "a2_attempts", "full_story_part2_attempt2_customf1837a73.wav"), voice="Aoede",
                  script="…At the same time, U.S. data on what people pay showed coffee cost 6.1% more than in the same month a year earlier… " + coffee_note,
                  intended="(意図的誤読ではなく実際の生成音声)",
                  asr=[("OpenAI Primary", (a2.get("asr_text") or "")[:140], "NG:" + str(a2.get("audio_classification"))), ("ローカルwhisper small/medium", "showed coffee cost(両方原稿一致)", "NORMALIZED_MATCH")],
                  note="Primaryは「showed→show」と聞いてNG。ローカル2モデルは原稿どおり。TTSが『show』と読んだのか、Primaryの聞き間違いかを確認します。",
                  listen="冒頭付近の「people pay showed coffee cost」(文頭から約5〜8秒)"))
fin = os.path.join(SN, "a2_final", "full_story_part2.wav")
items.append(dict(section="5. Coffee part2 の2点", id="coffee_part2_#5(raw bean、LR後最終)", wav=fin, voice="Aoede",
                  script="…They estimate raw bean prices take at least about nine months to appear in U.S. shop prices… " + coffee_note,
                  intended="(意図的誤読ではなく実際の生成音声)",
                  asr=[("OpenAI Primary", "raw bean(原稿一致)", "PASS:NORMALIZED_MATCH"), ("Azure(forced)", "robbing prices / robbins", "NG:TRUE_CONTENT_MISMATCH"),
                       ("ローカルwhisper small", "robbing", "NG:TRUE_CONTENT_MISMATCH"), ("ローカルwhisper medium", "raw bean", "PASS:NORMALIZED_MATCH")],
                  note="4系統中2系統が「robbing」と転写。本物の発音のあいまいさか確認します(Primary単独PASSで採用される型の見逃し候補)。",
                  listen="「They estimate raw bean prices take at least about nine months」付近(文章の中盤、約20〜28秒)"))

# ---------------- 6. Trial C 合意誤読11・曖昧 ----------------
res = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "trial_c_results_01.json"), encoding="utf-8"))
sample = {x["id"]: x for x in json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "sample_C_01.json"), encoding="utf-8"))}
az = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "azure_nopl_C_01.json"), encoding="utf-8"))
cache = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "local_asr_cache_C_01.json"), encoding="utf-8"))
rows = {r["id"]: r for r in res["rows"]}
for lab, sec in (("TRUE_ERROR_SUSPECT", "6a. Trial C 合意誤読(3系統が同じ誤りを返した11件)"), ("AMBIGUOUS", "6b. Trial C 曖昧(要試聴、7件)")):
    for rid in sorted(rows, key=lambda k: int(k[1:])):
        r = rows[rid]
        if r["proxy_label"] != lab:
            continue
        it = sample[rid]
        wav = absp(it["wav"])
        sysd = r["systems"]
        agreed = r["proxy_label_agreed_error_signature"]
        diffs = "; ".join("原稿「%s」→ASR「%s」" % (x[1], x[2]) for x in agreed if len(x) >= 3 and x[0] == "d")
        if not diffs:
            diffs = "; ".join("原稿「%s」→ASR「%s」(%s)" % (a, b, s) for s in ("openai_primary", "azure_noPL", "local_medium") if sysd.get(s) for a, b in sysd[s]["diffs"][:2])
        asr = []
        for sname, lab2, text in (("openai_primary", "OpenAI Primary", it["primary_text"]), ("azure_noPL", "Azure(Phrase Listなし)", (az.get(rid) or {}).get("text")),
                                  ("local_medium", "ローカルwhisper medium", cache.get("medium|%s" % wav)), ("local_small", "ローカルwhisper small", cache.get("small|%s" % wav))):
            s = sysd.get(sname)
            asr.append((lab2, text, (("PASS" if s["should_pass"] else "NG") + ":" + s["class"]) if s else "-"))
        first_word = ""
        for x in agreed:
            if len(x) >= 3 and x[0] == "d":
                first_word = x[1]
                break
        if not first_word:
            for s in ("openai_primary", "azure_noPL", "local_medium"):
                if sysd.get(s) and sysd[s]["diffs"]:
                    first_word = sysd[s]["diffs"][0][0]
                    break
        voice = "Aoede"
        try:
            vj = json.load(open(wav[:-4] + ".json", encoding="utf-8"))
            voice = vj.get("voice") or voice
        except Exception:
            pass
        items.append(dict(section=sec, id="%s(%s)" % (rid, it["segment_id"]), wav=wav, voice=voice, script=it["canonical"], intended="(実際の生成音声。意図的誤読ではない)", asr=asr,
                          note="ラベル=%s。ASR側の合意差分: %s" % (lab, diffs or "なし(系統間で割れた)"), listen=("差分語の周辺 " + tbl(it["canonical"], first_word, it["dur"])).strip()))

# ---------------- mp3化・HTML ----------------
HEAD = """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ASR判定の未確定音声 試聴ページ(ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 / Trial・未承認)</title>
<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:1.8em}
.row{border:1px solid #ccc;border-radius:6px;padding:.5em .9em;margin:.7em 0}.hd{display:flex;gap:.8em;align-items:center;flex-wrap:wrap}.hd .id{font-weight:bold}.hd .v{color:#06c;font-size:.85em}
audio{height:32px;min-width:360px}.s{margin:.2em 0}.k{font-size:.8em;color:#555}.n{font-size:.85em;color:#444}table.asr{border-collapse:collapse;font-size:.85em;margin:.3em 0}table.asr td,table.asr th{border:1px solid #ddd;padding:.15em .5em;text-align:left}
.j label{margin-right:1em}.note{color:#555;font-size:.9em}#out{width:100%;height:9em;font-family:monospace}.mis{color:#b00}</style></head><body>
<h1>ASR判定の未確定音声 試聴ページ(Trial・Production未採用)</h1>
<p class="note">ASR(OpenAI Primary / Azure / ローカルwhisper)が原稿どおりに転写したため、「TTSが本当に正しく読んだのか」を耳で確認するための一覧です。Blindではありません。各行に原稿・意図した誤読(Trial Bのみ)・各ASRの転写と判定を併記しています。
聞いたあと、各行で「正しく読んだ / 誤読 / 不明」を選び、末尾の「結果をテキスト化」で出る文章をそのまま返信に貼ってください(このページはサーバーに送信しません)。
全音声は部品単位の短いclip(または1segment)で、完成episodeではありません。TTS方式はいずれもStandard同期(Trial B)または各Production生成時の方式です。固定文言・Intro/Outro・SFXは含みません。</p>"""
TAIL = """<h2>結果をテキスト化</h2><button id="mk">結果をテキスト化</button><br><textarea id="out" readonly></textarea>
<script>document.getElementById('mk').onclick=function(){var o=[];document.querySelectorAll('.row').forEach(function(r){var c=r.querySelector('input:checked');o.push(r.dataset.id+': '+(c?c.value:'未回答'));});document.getElementById('out').value=o.join('\\n');};</script></body></html>"""
H = [HEAD]
cur = None
n = 0
mp3_map = []
for it in items:
    if it["section"] != cur:
        cur = it["section"]
        H.append("<h2>%s</h2>" % html.escape(cur))
    n += 1
    if "audio_rel" in it:
        src = it["audio_rel"]
    else:
        name = re.sub(r"[^A-Za-z0-9_]+", "_", it["id"]).strip("_") + ".mp3"
        src = to_mp3(it["wav"], name)
    mp3_map.append({"id": it["id"], "src": src, "voice": it["voice"], "section": it["section"]})
    rid = "r%d" % n
    asr_rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (html.escape(a), html.escape(str(t)), html.escape(str(j))) for a, t, j in it["asr"])
    if it["intended"] and not it["intended"].startswith("("):
        intended = '<div class="s mis">意図した誤読(話した文): %s</div>' % html.escape(it["intended"])
    else:
        intended = '<div class="k">%s</div>' % html.escape(it["intended"])
    H.append('<div class="row" data-id="%s"><div class="hd"><span class="id">%s</span><audio controls preload="none" src="%s"></audio><span class="v">Voice: %s</span></div>'
             '<div class="s"><b>原稿:</b> %s</div>%s<div class="k">聞くところ: %s</div><div class="n">%s</div>'
             '<table class="asr"><tr><th>ASR</th><th>転写</th><th>判定</th></tr>%s</table>'
             '<div class="j"><label><input type="radio" name="%s" value="正しく読んだ">正しく読んだ</label><label><input type="radio" name="%s" value="誤読">誤読</label>'
             '<label><input type="radio" name="%s" value="不明">不明</label></div></div>'
             % (html.escape(it["id"]), html.escape(it["id"]), src, html.escape(it["voice"]), html.escape(it["script"]), intended, html.escape(it["listen"]), html.escape(it["note"]), asr_rows, rid, rid, rid))
H.append(TAIL)
open(os.path.join(PAGE, "index.html"), "w", encoding="utf-8").write("\n".join(H))
json.dump(mp3_map, open(os.path.join(ROOT, "er058_output", "trial_abc", "listen_items_05B.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows", len(items), "mp3 files", len(os.listdir(AUD)))
