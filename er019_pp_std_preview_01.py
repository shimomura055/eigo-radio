# -*- coding: utf-8 -*-
"""FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_05: Standard通し再生プレビュー音声(確認用・Production完成版ではない)。
API 0。Production assemble(M3 Gate)は呼ばない/迂回しない。run dirは読み取りのみ。
順序・pause秒数はer019_family_x_audio_production_runner_01.build_family_x_a2_timeline(L1853-)の写し(SFX[Intro/Notification/Outro]・gain正規化・headroom処理は省略)。
出力: user_test/paycheck_personality_e2e_01/std_preview/audio/*.mp3, docs/research/.../std_preview_manifest_01.json"""
from __future__ import annotations
import hashlib, json, os, subprocess
import numpy as np
import soundfile as sf
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
A2 = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "paycheck_personality__run_pp_01", "a2")
NAR = os.path.join(A2, "narration")
AUD = os.path.join(ROOT, "user_test", "paycheck_personality_e2e_01", "std_preview", "audio")
MAN = os.path.join(ROOT, "docs", "research", "FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01", "std_preview_manifest_01.json")
SR = 24000
KP_NUMBERING_PAUSE = 0.4 + 0.2   # er003_v1_n3_01_assemble.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS(p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDS 0.4 + 0.2)
KP_INTERNAL_PAUSE = 0.4          # p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDS
KP_BLOCK_END_PAUSE = 0.8         # p9a.KEY_PHRASE_BLOCK_END_PAUSE_SECONDS
EN2JA, JA2EN = 1.0, 0.8          # build_family_x_a2_timeline hard-coded pause_1.0_en_to_ja / pause_0.8_ja_to_en


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rd(name):
    p = os.path.join(NAR, name + ".wav")
    x, sr = sf.read(p, dtype="float32")
    assert sr == SR and x.ndim == 1, (name, sr, x.shape)
    return x


def sil(s):
    return np.zeros(int(round(s * SR)), dtype="float32")


def mp3(x, dst, br="128k"):
    tmp = dst + ".tmp.wav"
    sf.write(tmp, x, SR)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, dst], check=True)
    os.remove(tmp)


def main():
    os.makedirs(AUD, exist_ok=True)
    res = json.load(open(os.path.join(A2, "audit", "tts_generation_results.json"), encoding="utf-8"))
    seg_res = res["segments"]
    used, pieces, marks = {}, [], []   # used: name -> sha ; marks: label,start,end
    t = [0.0]

    def add(label, name=None, arr=None, mark=False):
        a = arr if arr is not None else rd(name)
        if name:
            used[name] = sha(os.path.join(NAR, name + ".wav"))
        if mark:
            marks.append({"label": label, "start": round(t[0], 2), "end": round(t[0] + len(a) / SR, 2)})
        pieces.append(a)
        t[0] += len(a) / SR

    def pause(s):
        add("pause", arr=sil(s))

    add("welcome", "welcome"); pause(0.5)
    add("topic_intro", "topic_intro"); pause(0.65)
    add("japanese_title", "japanese_title"); pause(0.5)
    add("preview_intro", "preview_intro"); pause(0.65)
    add("preview", "preview"); pause(0.5)
    add("key_phrases_intro", "key_phrases_intro"); pause(0.5)
    kp = json.load(open(os.path.join(A2, "key_phrases", "keywords_canonicalized.json"), encoding="utf-8"))
    nums = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    for i, it in enumerate(sorted(kp["items"], key=lambda z: z["rank"])):
        r = it["rank"]
        add("kp%d_num" % r, nums[i]); pause(KP_NUMBERING_PAUSE)
        add("kp%d_en" % r, "kp%d_en" % r); pause(KP_INTERNAL_PAUSE)
        add("kp%d_meaning" % r, "meaning_%d" % (i + 1)); pause(KP_INTERNAL_PAUSE)
        add("kp%d_en_2" % r, "kp%d_en" % r); pause(KP_BLOCK_END_PAUSE)
    pause(0.4)
    add("full_story_intro", "full_story_intro"); pause(EN2JA)
    for n in (1, 2, 3):
        add("comment_%d" % n, "comment_%d" % n, mark=True); pause(JA2EN)
        add("part%d" % n, "full_story_part%d" % n, mark=True)
        pause(EN2JA)
    add("comment_4", "comment_4", mark=True); pause(JA2EN)
    add("in_one_line", "in_one_line", mark=True)
    full = np.concatenate(pieces)
    pre = os.path.join(AUD, "Standard_PREVIEW_not_production.mp3")
    mp3(full, pre)
    # 単独再生用(第1/2/3部)
    singles = {}
    for n in (1, 2, 3):
        d = os.path.join(AUD, "part%d_only.mp3" % n)
        mp3(rd("full_story_part%d" % n), d)
        singles[n] = d
    # 取り違え防止: run dirの採用wav sha(tts_generation_results.json OK entry)と照合
    table = []
    for n in (1, 2, 3):
        k = "full_story_part%d" % n
        w = os.path.join(NAR, k + ".wav")
        table.append({"segment": k, "status": seg_res[k]["status"], "results_json_sha256": seg_res[k]["sha256"], "narration_wav_sha256": sha(w),
                      "match": seg_res[k]["sha256"] == sha(w), "preview_mp3": os.path.relpath(singles[n], ROOT).replace("\\", "/")})
    for k in ("topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4", "in_one_line"):
        w = os.path.join(NAR, k + ".wav")
        table.append({"segment": k, "status": seg_res[k]["status"], "results_json_sha256": seg_res[k]["sha256"], "narration_wav_sha256": sha(w), "match": seg_res[k]["sha256"] == sha(w)})
    man = {"purpose": "Standard通し再生プレビュー(確認用。Production完成版ではない。M3 Gate/assemble経路は使っていない)",
           "run_dir": os.path.relpath(A2, ROOT).replace("\\", "/"),
           "order_source": "er019_family_x_audio_production_runner_01.py build_family_x_a2_timeline(順序・pause秒数の写し。SFX[Intro/Notification/Outro]・RMS gain・headroom処理は省略)",
           "pauses": {"en_to_ja": EN2JA, "ja_to_en": JA2EN, "kp_numbering": KP_NUMBERING_PAUSE, "kp_internal": KP_INTERNAL_PAUSE, "kp_block_end": KP_BLOCK_END_PAUSE,
                      "source": "build_family_x_a2_timeline L1853-1905(1.0/0.8/0.5/0.65/0.4)、er003_v1_n3_01_assemble.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS L865、er003_b1_p9a_audio KEY_PHRASE_*_PAUSE_SECONDS"},
           "preview_mp3": os.path.relpath(pre, ROOT).replace("\\", "/"), "preview_duration_s": round(len(full) / SR, 2), "preview_mp3_sha256": sha(pre),
           "marks": marks, "segment_wav_sha256_used": used, "adoption_match_table": table, "all_match": all(r["match"] for r in table)}
    os.makedirs(os.path.dirname(MAN), exist_ok=True)
    json.dump(man, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("dur", man["preview_duration_s"], "all_match", man["all_match"])
    for m in marks:
        print(m)


if __name__ == "__main__":
    main()
