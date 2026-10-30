# 委任_02C 証跡: 公開用の単体mp3そのもの(wav->mp3変換後)を、生成時のASR(KP3V多数決)とは独立にローカルfaster-whisper(medium int8・API 0)で転写し、
# 掲載項目の英語表現と一致するか確認する(er135.kp_asr_matches=End Userが既にKP区間照合に使う判定をそのまま利用)。
# 使い方: python sub02c_asr_check.py <WT> <out_json> <enduser_dir>...
import json
import os
import sys

WT, OUT = sys.argv[1:3]
sys.path.insert(0, WT)
import er135_enduser_page_01 as eu  # noqa: E402
import er137_vocab_extra_audio_01 as vx  # noqa: E402

rows = []
for d in sys.argv[3:]:
    art = json.load(open(f"{d}/data/article.json", encoding="utf-8"))
    for akey, L in art["levels"].items():
        for v in L["vocab"]:
            a = v["audio"]
            p = f"{d}/{a['file']}"
            dur = eu._mp3_duration(p)
            heard = eu._default_asr(p, 0.0, dur + 0.05)
            rows.append({"dir": d.split("/ev02c/")[-1], "level": akey, "heading": v["heading"], "file": a["file"], "dur": dur, "heard": heard,
                         "match": eu.kp_asr_matches(vx._norm(v["heading"]), heard)})
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(sum(r["match"] for r in rows), "/", len(rows))
for r in rows:
    if not r["match"]:
        print("NG", r)
