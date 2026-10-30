# 委任_02C 証跡: 実TTS済みコピーrunのvocab_audio.json -> 公開済みarticle.jsonのコピーへ `levels[lv].vocab[i].audio` を付与し、
# 全掲載項目に音声があること/mp3実在・sha一致を検査する(API 0)。公開済みdirは変更しない(コピー先=証跡dir)。fail-closed経路(1件欠落)も同時に実演。
# 使い方: python sub02c_article_evidence.py <WT> <label> <published_enduser_dir> <out_dir> <a2_level_dir|-> <b1b_level_dir>
import copy
import json
import os
import shutil
import sys

WT, LABEL, PUB, OUT, A2, B1B = sys.argv[1:7]
sys.path.insert(0, WT)
import er137_vocab_extra_audio_01 as vx  # noqa: E402

art0 = json.load(open(f"{PUB}/data/article.json", encoding="utf-8"))
docs = {}
for lv, d in (("a2", A2), ("b1b", B1B)):
    if d != "-" and os.path.exists(f"{d}/vocab_audio/vocab_audio.json"):
        docs[lv] = json.load(open(f"{d}/vocab_audio/vocab_audio.json", encoding="utf-8"))
art = vx.apply_to_article(copy.deepcopy(art0), docs)
os.makedirs(f"{OUT}/data", exist_ok=True)
os.makedirs(f"{OUT}/audio", exist_ok=True)
for lv, d in (("a2", A2), ("b1b", B1B)):
    if lv in docs:
        for it in docs[lv]["items"]:
            shutil.copy(f"{d}/vocab_audio/{it['mp3']}", f"{OUT}/audio/{it['mp3']}")
json.dump(art, open(f"{OUT}/data/article.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
rep = {"label": LABEL, "levels": {}}
for akey, L in art["levels"].items():
    rep["levels"][akey] = [{"heading": v["heading"], "audio": v.get("audio")} for v in L.get("vocab") or []]
rep["validate_article(public_dir)"] = vx.validate_article(art, public_dir=OUT)
# 公開済み(音声なし)articleのまま検査すると全件違反=旧articleは音声なしで掲載されている事実の確認
rep["validate_original_article_without_audio"] = vx.validate_article(art0)
# fail-closed実演: 1件のvocab_audioを欠落させるとapply_to_articleが止まる
if docs:
    lv0 = sorted(docs)[-1]
    bad = copy.deepcopy(docs)
    bad[lv0]["items"] = bad[lv0]["items"][:-1]
    try:
        vx.apply_to_article(copy.deepcopy(art0), bad)
        rep["fail_closed_demo"] = "NOT_STOPPED(NG)"
    except vx.VocabAudioIncomplete as e:
        rep["fail_closed_demo"] = f"STOPPED: {str(e)[:160]}"
json.dump(rep, open(f"{OUT}/article_audio_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1)[:3500])
