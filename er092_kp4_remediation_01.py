# FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01 委任_01 (2026-10-21)
# 問題音声(Std KP4 "take part", sha 675cd6b1...)の無効化。Productionコード無変更。既存の`reuse_blocked` mark機構
# (er078_reuse_value_guard_01.guard_entry / er006_master_audio_store_01.get_or_generate)を該当Master Store entry 1件にだけ付与し、
# 旧音声は削除せず改名保存する(Task Bの問題音声として再利用)。
from __future__ import annotations
import hashlib, json, os, shutil, sys, time

MID = "0714639d351b47c34b4d4103"
OLD_SHA = "675cd6b1aec9865acbdb411b588672d9cc963b936bb4a35bb2d8158cb4172186"
MANIFEST = "er006_output/master_audio_store_01/manifest.json"
NARR = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/narration"
STAMP = "invalid_20261021"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def invalidate():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    before = json.dumps(man, ensure_ascii=False, sort_keys=True)
    e = man[MID]
    assert e["qa_evidence"]["sha256"] == OLD_SHA, "entry sha mismatch"
    assert sha(f"{NARR}/kp4_en.wav") == OLD_SHA
    # 旧音声を改名保存(上書きしない)
    dst = f"{NARR}/kp4_en.{STAMP}.wav"
    assert not os.path.exists(dst)
    shutil.move(f"{NARR}/kp4_en.wav", dst)
    for ext in ("wav", "json"):
        s = f"{NARR}/attempts/kp4_en_attempt1_custom60ebc452.{ext}"
        if os.path.exists(s):
            shutil.move(s, f"{NARR}/attempts/kp4_en_attempt1_custom60ebc452.{STAMP}.{ext}")
    os.makedirs("er006_output/master_audio_store_01/audio/_reuse_blocked", exist_ok=True)
    shutil.copyfile(e["audio_path"], f"er006_output/master_audio_store_01/audio/_reuse_blocked/{MID}_{STAMP}_preserved.wav")
    e["reuse_blocked"] = {"reason": "KP4 take part mispronunciation (user report 2026-10-21: tart); local whisper 'Tarte', Azure 'Take Tart' (FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01)",
                          "marked_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "by": "FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01",
                          "old_sha256": OLD_SHA}
    json.dump(man, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after = json.load(open(MANIFEST, encoding="utf-8"))
    b = json.loads(before)
    changed = [k for k in set(b) | set(after) if b.get(k) != after.get(k)]
    print("changed entries:", changed, "(expected only", MID + ")")
    assert changed == [MID]
    print("old kept:", dst, sha(dst))


if __name__ == "__main__":
    {"invalidate": invalidate}[sys.argv[1]]()
