# ============================================================
# er091_asr_three_way_trial_01_dataset.py  (ASR-THREE-WAY-COMPARISON-TRIAL-01 S1: 評価データ台帳builder)
# 既存音声のみ読み取り・コピー(API 0、TTS 0)。ASR結果は正解ラベルにしない。
# 正常ラベル=ユーザー試聴PASS済み記事(Std/Adv両方)の音声、またはHuman Review承認済みsegment。
# 問題ラベルは別script(er091_asr_three_way_trial_01_problem_audio.py)で追加(既知NG[take part]・構成ラベル)。
# ============================================================
from __future__ import annotations
import collections
import hashlib
import json
import os
import re
import shutil
import wave

OUT = "er091_output/asr_three_way_trial_01"
AUD = os.path.join(OUT, "audio", "orig")
os.makedirs(AUD, exist_ok=True)

ART = {
    "boredom": ("er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01", "X",
                "OPEN-408 USER_ACCEPTED 2026-10-17 Std/Adv試聴PASS",
                "docs/pm/delegation_log/2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_LISTENING-PASS_USER.md"),
    "yemen": ("er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02", "X",
              "OPEN-416 USER_ACCEPTED_FINAL 2026-10-21 Std/Adv試聴PASS",
              "docs/pm/delegation_log/2026-10-21_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_ACCEPTANCE_USER.md"),
    "melos": ("er026_output/family_z_production_e2e_01/melos/run_e2e_06", "Z",
              "OPEN-422 USER_ACCEPTED_FINAL 2026-10-21 Std/Adv試聴PASS",
              "docs/pm/delegation_log/2026-10-21_FAMILY-Z-MELOS-FINAL-CLOSEOUT-01_USER.md"),
}
LV = {"a2": "Standard", "b1b": "Advanced"}

# 本文normal選定 (art, level, seg)。短め区間優先+長文/数字/固有名詞/連結。
BODY_ARTICLE = [
    ("melos", "a2", "topic_intro_en"), ("melos", "a2", "full_story_part1_c2"), ("melos", "a2", "full_story_part1_c4"),
    ("melos", "a2", "full_story_part1_c5"), ("melos", "a2", "full_story_part1_c6"), ("melos", "a2", "full_story_part1_c8"),
    ("melos", "a2", "full_story_part3_c2"),
    ("melos", "a2", "full_story_part3_c6"), ("melos", "a2", "full_story_part3_c8"), ("melos", "a2", "full_story_part2_c1"),
    ("melos", "b1b", "full_story_part1_c2"), ("melos", "b1b", "full_story_part1_c9"), ("melos", "b1b", "full_story_part3_c4"),
    ("melos", "b1b", "comment_1"), ("melos", "b1b", "preview"),
    ("boredom", "a2", "topic_intro"), ("boredom", "a2", "in_one_line"), ("boredom", "b1b", "comment_1"),
    ("boredom", "b1b", "full_story_part1"),
    ("yemen", "a2", "topic_intro"), ("yemen", "a2", "in_one_line"), ("yemen", "b1b", "comment_1"), ("yemen", "b1b", "comment_2"),
    ("yemen", "b1b", "full_story_part3"),
]
# HR/ユーザー承認済み(ASRがUNCERTAIN/不一致でも人間が正読と確認した難例)。(base, level, seg, family, evidence)
HR_EXTRA = [
    ("er026_output/family_z_production_e2e_01/melos/run_e2e_04", "a2", "full_story_part3_c1", "Z",
     "human_approved_segments.json: user 2026-10-20 HR承認(attempt2 'Melos drank'を自然と試聴確認)"),
    ("er026_output/family_z_production_e2e_01/melos/run_e2e_02", "a2", "full_story_part1_c5", "Z",
     "human_approved_segments.json: user 2026-10-13 承認('Melos said.' Primary=Mello/Azure=Mellowだが人間は正読と確認)"),
    ("er014_output/user_test_news_2ep_01/space_weapons", "a2", "full_story_part1", "X",
     "human_approved_segments.json: user判断2026-09-17(/mɪŋk/採用、Troy Meink)"),
    ("er014_output/user_test_news_light_01/tiny_bags", "a2", "full_story_part2", "X",
     "human_approved_segments.json: user正式判断2026-09-17(Toteme/Kallmeyer実読確認、ASR5系統で綴り不一致のまま承認)"),
    ("er014_output/user_test_news_convenience_ai_01/convenience_ai", "a2", "point_two", "X",
     "human_approved_segments.json: user_via_fable_sandwich_pm 2026-09-17(Oimo no Cane等)"),
    ("er006_output/pool_pilot_01/pool_n9_tip_screens", "a2", "kp2_english", "X",
     "human_approved_segments.json: user 2026-09-01 ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25(KP)"),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def dur(p):
    with wave.open(p, "rb") as w:
        return round(w.getnframes() / float(w.getframerate()), 3)


def tags_for(text, kind):
    t = (text or "").strip()
    words = re.findall(r"[A-Za-z0-9'’\-]+", t)
    tg = []
    if kind == "kp":
        tg.append("kp_single_word" if len(words) == 1 else ("kp_short_2w" if len(words) == 2 else "kp_phrase_3w+"))
    else:
        tg.append("body_short" if len(words) <= 12 else ("body_mid" if len(words) <= 40 else "body_long"))
    if re.search(r"\d", t) or re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|hundred|thousand)\b", t, re.I):
        tg.append("number")
    if re.search(r"\b(not|no|never|won't|don't|can't|cannot|isn't|doesn't|didn't)\b", t, re.I):
        tg.append("negation")
    caps = [w for i, w in enumerate(words) if w[0].isupper() and (i > 0 or kind == "kp") and w.lower() not in ("i", "the", "a", "today's")]
    if caps:
        tg.append("proper_noun")
    if "-" in t or "'" in t or "’" in t:
        tg.append("hyphen_or_contraction")
    return tg


def load_seg(base, lv, seg):
    d = json.load(open(f"{base}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
    if seg.startswith("kp") and seg.endswith("_english"):
        v = d["key_phrases"][seg[2]]["english"]
    else:
        v = d["segments"][seg]
    return d, v


def kp_canon(base, lv, idx, v):
    t = v.get("text")
    if t:
        return t
    kj = json.load(open(f"{base}/{lv}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    it = kj["items"][idx - 1]
    return it.get("used_form") or it.get("key_phrase")


def pick_wav(v):
    p = v["path"]
    orig = p[:-4] + "_original.wav"
    return (orig if os.path.exists(orig) else p), p


def add(rows, rid, src, **meta):
    dst = os.path.join(AUD, rid + ".wav")
    shutil.copyfile(src, dst)
    row = {"id": rid, "wav": dst.replace("\\", "/"), "wav_sha256": sha(dst), "duration_s": dur(dst),
           "src_wav": src.replace("\\", "/")}
    row.update(meta)
    rows.append(row)


def main():
    rows = []
    for art, (base, fam, accept, orig) in ART.items():
        for lv in ("a2", "b1b"):
            d = json.load(open(f"{base}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
            for i in range(1, 6):
                v = d["key_phrases"][str(i)]["english"]
                canon = kp_canon(base, lv, i, v)
                src, final = pick_wav(v)
                rid = f"kp_{art}_{lv}_{i}"
                add(rows, rid, src, kind="kp", canonical=canon, family=fam, level=LV[lv], article=art, segment=f"kp{i}_en",
                    label="normal", label_class="normal", label_strength="human_listened_article",
                    label_basis=f"{accept}。原文={orig}(記事全体の試聴PASS。KP単位の個別聴取記録は無い[記事Bの take part 事例のとおり個別見逃しは起こりうる])",
                    production_time_asr_text=v.get("asr_text"), production_reused_from_store=bool(v.get("reused")),
                    final_path_user_heard=final, tags=tags_for(canon, "kp"))
    for art, lv, seg in BODY_ARTICLE:
        base, fam, accept, orig = ART[art]
        d, v = load_seg(base, lv, seg)
        canon = v.get("canonical_text") or v["text"]
        src, final = pick_wav(v)
        rid = f"body_{art}_{lv}_{seg}"
        add(rows, rid, src, kind="body", canonical=canon, family=fam, level=LV[lv], article=art, segment=seg,
            label="normal", label_class="normal", label_strength="human_listened_article",
            label_basis=f"{accept}。原文={orig}(記事全体の試聴PASS)", production_time_asr_text=v.get("asr_text"),
            final_path_user_heard=final, tags=tags_for(canon, "body"))
    for base, lv, seg, fam, ev in HR_EXTRA:
        d, v = load_seg(base, lv, seg)
        if seg.endswith("_english"):
            idx = int(seg[2])
            kind = "kp"
            canon = kp_canon(base, lv, idx, v)
        else:
            kind = "body"
            canon = v.get("canonical_text") or v["text"]
        src, final = pick_wav(v)
        rid = "hr_" + re.sub(r"[^A-Za-z0-9]+", "_", base.split("/")[-1]) + f"_{lv}_{seg}"
        add(rows, rid, src, kind=kind, canonical=canon, family=fam, level=LV[lv], article=base.split("/")[-1], segment=seg,
            label="normal", label_class="normal_hr_approved_hard", label_strength="human_approved_segment",
            label_basis=ev + "。注意: 承認時のwavと現存wavの同一性は未照合(承認hashはcanonical_text hash)",
            production_time_asr_text=v.get("asr_text"), final_path_user_heard=final,
            tags=tags_for(canon, kind) + ["hr_approved_hard"])
    with open(os.path.join(OUT, "dataset_manifest_normal.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), collections.Counter((r["kind"], r["label_class"]) for r in rows))
    print("total sec", round(sum(r["duration_s"] for r in rows), 1))
    for r in rows:
        print(r["id"], r["duration_s"], "|", r["canonical"][:60], "|", r["tags"])


if __name__ == "__main__":
    main()
