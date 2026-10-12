# -*- coding: utf-8 -*-
"""反例セット(D)のconfig生成(オフライン無料・TTS生成なし)。

(1) natural_ng: 既存の本番NG take(verified=False)と、同dirの検証済みclipから選んだ前後文脈。
    正解テキストは同segmentの検証済みtakeのASR(または作品plan)を代理(proxy)とする。真の発音は人手試聴でのみ確定。
(2) synthetic: 既存のOK音声をオフライン編集して「既知の欠陥」を作る(語末子音の切り詰め・語の削除)。
    欠陥の真値が既知なので、文脈付きASRが正しい表記を返せば確定的な false accept になる。
"""
import glob
import json
import os
import re
import sys
import wave

import numpy as np

sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L

OUT = "er065_output/short_clip_asr_context_trial_01"
SRC = OUT + "/audio_src/"
L.install_write_guard([OUT])


def speech_end(a, sr=24000, thr_db=-38.0):
    fr = int(sr * 0.01)
    n = len(a) // fr
    rms = np.array([np.sqrt(np.mean(a[i * fr:(i + 1) * fr] ** 2) + 1e-9) for i in range(n)])
    peak = rms.max()
    on = np.where(rms > peak * 10 ** (thr_db / 20))[0]
    return (on[-1] + 1) * fr / sr


def fade_out(a, ms=8, sr=24000):
    k = int(sr * ms / 1000)
    a = a.copy()
    a[-k:] *= np.linspace(1, 0, k)
    return a


def meta_for(wavpath):
    j = wavpath[:-4] + ".json"
    d = json.load(open(j, encoding="utf-8")) if os.path.exists(j) else {}
    return d


# ------------------------------------------------------------------ synthetic
def make_synthetic():
    a2 = json.load(open(OUT + "/config_melos_01.json", encoding="utf-8"))["pools"]["a2"]
    bases = {
        "B1": {"path": SRC + "a2_narration/attempts/full_story_part1_c5_attempt1_customadfcf33f.wav", "canon": "Melos said.", "final": "said",
               "slots": {"SS": ["n_c1"], "SL": ["n_c9"], "SD": ["m_c4"], "SD2": ["m_c6"]}},
        "B2": {"path": a2["clips"]["n_c7"]["path"], "canon": "The ruler smiled and said,", "final": "said",
               "slots": {"SS": ["n_c1"], "SL": ["n_c9"], "SD": ["m_c4"], "SD2": ["m_c6"]}},
        "B4": {"path": a2["clips"]["n_c3"]["path"], "canon": "Silence came, and guards grabbed the young shepherd. The ruler ordered his death.",
               "final": "death", "slots": {"SS": ["n_c7"], "SL": ["n_c9"], "SD": ["m_c4"], "SD2": ["m_c6"]}},
    }
    targets = []
    adir = OUT + "/synthetic_audio/"
    os.makedirs(adir, exist_ok=True)
    for bid, b in bases.items():
        a = L.read_wav_mono(b["path"])
        end = speech_end(a)
        for ms in (70, 140, 220):
            cut = int((end - ms / 1000) * 24000)
            y = fade_out(a[:cut])
            p = adir + f"syn_{bid}_trunc{ms}.wav"
            L.write_wav(p, y)
            targets.append({"id": f"syn_{bid}_trunc{ms}", "path": p, "pool": f"p_{bid}", "voice": "Aoede", "canonical": b["canon"],
                            "focus_word": b["final"], "category": "synthetic_final_consonant_loss",
                            "defect": f"last {ms} ms of speech removed (speech_end={end:.2f}s), fade 8ms; base={b['path'].split('/')[-1]}",
                            "note": "known defect (offline edit)", "label_hint": "known_defect"})
    # 無改変の対照(intact control): 正解側(true accept)の代理。欠陥targetと同一base・同一focus語
    for bid, b in bases.items():
        targets.append({"id": f"ctl_{bid}_intact", "path": b["path"], "pool": f"p_{bid}", "voice": "Aoede", "canonical": b["canon"],
                        "focus_word": b["final"], "category": "intact_control", "defect": "none (unmodified base)",
                        "note": "control (offline edit なし)", "label_hint": "intact"})
    # drop-word: B1の語境界はAzure word timestamps(R00 rep1)から
    words = None
    for line in open(OUT + "/results_01_azure_melos.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["cond_id"] == "a2_att1__R00_alone" and r["variant"] == "base" and r["result"].get("words"):
            words = r["result"]["words"]
            break
    a = L.read_wav_mono(bases["B1"]["path"])
    w_melos, w_said = words[0], words[1]
    sr = 24000
    keep_melos = fade_out(a[:int(w_said["start"] * sr)])           # 'Melos' のみ残す(said削除)
    keep_said = a[int(max(0, w_said["start"] - 0.02) * sr):]        # 'said' のみ残す(Melos削除)
    for nm, y, foc, d in (("dropsaid", keep_melos, "said", "word 'said' removed"), ("dropmelos", keep_said, "Melos", "word 'Melos' removed")):
        p = adir + f"syn_B1_{nm}.wav"
        L.write_wav(p, y)
        targets.append({"id": f"syn_B1_{nm}", "path": p, "pool": "p_B1", "voice": "Aoede", "canonical": "Melos said.", "focus_word": foc,
                        "category": "synthetic_missing_word", "defect": d + f" (azure word ts: melos {w_melos['start']:.2f}-{w_melos['end']:.2f}, said {w_said['start']:.2f}-{w_said['end']:.2f})",
                        "note": "known defect (offline edit)", "label_hint": "known_defect"})
    pools = {}
    for bid, b in bases.items():
        clips = {k: {"path": v["path"], "text": v["text"], "voice": v["voice"], "model": v["model"]} for k, v in a2["clips"].items()}
        pools[f"p_{bid}"] = {"slots": b["slots"], "clips": clips}
    recipes = [
        {"id": "R00_alone", "pre": [], "post": [], "kind": "alone"},
        {"id": "SSpre", "pre": ["SS"], "post": [], "kind": "same_voice"},
        {"id": "SSpost", "pre": [], "post": ["SS"], "kind": "same_voice"},
        {"id": "SLpre", "pre": ["SL"], "post": [], "kind": "same_voice"},
        {"id": "SDpre", "pre": ["SD"], "post": [], "kind": "diff_voice"},
        {"id": "SDboth", "pre": ["SD"], "post": ["SD2"], "kind": "diff_voice"},
    ]
    cfg = {"work_id": "synthetic_known_defects", "group": "synthetic", "focus_word": "said", "target_canonical": "Melos said.", "gap_ms": 300,
           "pools": pools, "targets": targets, "recipes": recipes, "targets_recipes": {}}
    json.dump(cfg, open(OUT + "/config_synthetic_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("synthetic targets", len(targets))


# ------------------------------------------------------------------ natural NG
def ok_clips(dirpath, exclude_seg):
    out = []
    for j in sorted(glob.glob(dirpath + "/*.json")):
        d = json.load(open(j, encoding="utf-8"))
        w = j[:-5] + ".wav"
        if not d.get("verified") or not os.path.exists(w) or d.get("segment_id") == exclude_seg:
            continue
        t = d.get("asr_text") or ""
        if not re.fullmatch(r"[\x20-\x7e‘’]+", t.strip() or "x") or len(t.split()) < 3:
            continue
        with wave.open(w) as x:
            du = x.getnframes() / x.getframerate()
        out.append({"path": w.replace(chr(92), "/"), "text": t.strip(), "voice": d.get("voice"), "model": d.get("model"), "dur": du, "seg": d.get("segment_id")})
    return out


def pick(cl, voice, same, lo, hi, avoid=()):
    c = [x for x in cl if (x["voice"] == voice) == same and lo <= x["dur"] <= hi and x["seg"] not in avoid]
    c.sort(key=lambda x: abs(x["dur"] - (lo + hi) / 2))
    return c[0] if c else None


NATURAL = [
    # id, category, dir, seg, ng attempt, canonical(proxy), focus word, note
    ("nat_reduce", "final_consonant_drop", "er014_output/four_type_observation_01/discovery/audio/b1b/narration/attempts", "kp2_en", 1,
     "Reduced the feeling of connection.", "reduced", "NG ASR 'reduce the feeling of connection.' (-d dropped)"),
    ("nat_counts", "final_consonant_added", "er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/narration/attempts", "kp3_en", 1,
     "Count as success.", "count", "NG ASR 'Counts as success.' (+s)"),
    ("nat_paused", "final_consonant_added", "er012_output/e_family_two_level_wiring_01/meta/a2/narration/attempts", "kp4_en", 2,
     "Pause the feature.", "pause", "NG ASR 'Paused the feature.' (+d)"),
    ("nat_forced", "final_consonant_added", "er026_output/family_z_production_e2e_01/melos/run_e2e_01/b1b/narration/attempts", "kp4_en", 2,
     "Force one's way through.", "force", "NG ASR \"Forced one's way through.\" (+d)"),
    ("nat_milo", "proper_noun_mispronounced", "er026_output/family_z_production_e2e_01/melos/run_e2e_01/b1b/narration/attempts", "full_story_part1_c1", 1,
     "The guards went still when Melos spoke.", "Melos", "NG ASR 'Milo spoke'"),
    ("nat_milos_hand", "proper_noun_mispronounced", "er026_output/family_z_production_e2e_01/melos/run_e2e_01/a2/narration/attempts", "full_story_part1_c18", 1,
     "His friend's warm, steady fingers closed around Melos's hand.", "Melos's", "NG ASR \"Milos's hand\" (+friends')"),
    ("nat_melus_hand", "proper_noun_mispronounced", "er026_output/family_z_production_e2e_01/melos/run_e2e_01/b1b/narration/attempts", "full_story_part1_c18", 1,
     "His friend took Melos's hand. His fingers were warm and steady.", "Melos's", "NG ASR \"His friends took Melus's hand\""),
    ("nat_feet", "context_guessable_homophone", "er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/b1b/narration/attempts", "point_two_heading", 1,
     "Another voice, the reader who worries her feed is closing in.", "feed", "NG ASR '...her feet is closing in' (context 'feed')"),
    ("nat_bements", "context_guessable_homophone", "er014_output/user_test_news_2ep_01/space_weapons/a2/narration/attempts", "kp4_en", 1,
     "Be meant to protect.", "meant", "NG ASR 'Bements to protect.'"),
    ("nat_turnout", "content_mispronounced", "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_01/b1b/narration/attempts", "kp1_en", 1,
     "turn out not to be", "be", "NG ASR 'Turn out not today.'"),
    ("nat_design", "context_guessable_homophone", "er011_output/discovery_generalization_towels_trial_11/b1b/narration/attempts", "point_one_heading", 1,
     "When fabric and drying join forces.", "drying", "NG ASR '...fabric and design join forces'"),
]


def make_natural():
    targets, pools = [], {}
    for tid, cat, d, seg, n, canon, foc, note in NATURAL:
        cands = sorted(glob.glob(d.replace("family_x_b3_production_01", "*") + f"/{seg}_attempt{n}_*.json"))
        if not cands and "family_x" in d:
            cands = sorted(glob.glob("er019_output/family_x_audio_production_wiring_01/*/*/narration/attempts" + f"/{seg}_attempt{n}_*.json"))
        if not cands:
            print("NOT FOUND", tid, d, seg, n)
            continue
        j = cands[0]
        dd = json.load(open(j, encoding="utf-8"))
        wav = j[:-5] + ".wav"
        pdir = os.path.dirname(j)
        cl = ok_clips(pdir, seg)
        voice = dd.get("voice")
        ss = pick(cl, voice, True, 2.0, 5.5)
        sl = pick(cl, voice, True, 6.0, 12.0)
        sd = pick(cl, voice, False, 3.0, 9.0)
        clips, slots = {}, {}
        for nm, c in (("SS", ss), ("SL", sl), ("SD", sd)):
            if c:
                clips[nm] = {"path": c["path"], "text": c["text"], "voice": c["voice"], "model": c["model"]}
                slots[nm] = [nm]
        pools[f"p_{tid}"] = {"slots": slots, "clips": clips}
        targets.append({"id": tid, "path": wav.replace(chr(92), "/"), "pool": f"p_{tid}", "voice": voice, "model": dd.get("model"),
                        "canonical": canon, "focus_word": foc, "category": cat, "defect": note,
                        "note": f"{dd.get('audio_classification')} / ASR='{dd.get('asr_text')}' ({os.path.basename(j)})", "label_hint": "prod_ng_proxy"})
        print(tid, "voice", voice, "| SS", ss and (round(ss["dur"], 1), ss["text"][:40]), "| SL", sl and (round(sl["dur"], 1), sl["text"][:40]),
              "| SD", sd and (sd["voice"], round(sd["dur"], 1), sd["text"][:40]))
    recipes = [
        {"id": "R00_alone", "pre": [], "post": [], "kind": "alone"},
        {"id": "SSpre", "pre": ["SS"], "post": [], "kind": "same_voice"},
        {"id": "SSpost", "pre": [], "post": ["SS"], "kind": "same_voice"},
        {"id": "SLpre", "pre": ["SL"], "post": [], "kind": "same_voice"},
        {"id": "SDpre", "pre": ["SD"], "post": [], "kind": "diff_voice"},
    ]
    cfg = {"work_id": "natural_ng_counterexamples", "group": "natural_ng", "focus_word": "x", "target_canonical": "x", "gap_ms": 300,
           "pools": pools, "targets": targets, "recipes": recipes, "targets_recipes": {}}
    # recipeに必要なslotが無いtargetは除外
    tr = {}
    for t in targets:
        have = set(pools[t["pool"]]["slots"])
        tr[t["id"]] = [r["id"] for r in recipes if set(r["pre"] + r["post"]) <= have]
    cfg["targets_recipes"] = tr
    json.dump(cfg, open(OUT + "/config_natural_ng_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("natural targets", len(targets), {k: len(v) for k, v in tr.items()})


# ------------------------------------------------------------------ wrong-name (known defect, context contains the correct name)
def make_namedefect():
    mel = json.load(open(OUT + "/config_melos_01.json", encoding="utf-8"))["pools"]["a2"]
    a_ruler = L.read_wav_mono(mel["clips"]["n_c7"]["path"])
    a_said = L.read_wav_mono(SRC + "a2_narration/attempts/full_story_part1_c5_attempt1_customadfcf33f.wav")
    sr = 24000
    seg1 = a_ruler[int(0.45 * sr):int(0.93 * sr)]      # 'ruler' (Azure word ts in a2_att1__Npre3: 0.47-0.91)
    seg2 = a_said[int(0.77 * sr):int(1.56 * sr)]       # 'said'  (Azure word ts in a2_att1 alone: 0.79-1.55)
    y = np.concatenate([fade_out(seg1, 6), np.zeros(int(0.06 * sr), dtype=np.float32), seg2])
    p = OUT + "/synthetic_audio/syn_name_ruler.wav"
    L.write_wav(p, y)
    clips = {k: {"path": v["path"], "text": v["text"], "voice": v["voice"], "model": v["model"]} for k, v in mel["clips"].items()}
    pool = {"slots": {"SS": ["n_c1"], "SL": ["n_c11"], "SD": ["m_c4"], "SN": ["n_c3"]}, "clips": clips}
    targets = [{"id": "syn_name_ruler", "path": p, "pool": "p_name", "voice": "Aoede", "canonical": "Melos said.", "focus_word": "Melos",
                "category": "synthetic_wrong_name", "defect": "first word replaced by 'ruler' (spliced from another clip); contexts SS/SL contain the correct name 'Melos'",
                "note": "known defect (offline edit)", "label_hint": "known_defect"}]
    recipes = [
        {"id": "R00_alone", "pre": [], "post": [], "kind": "alone"},
        {"id": "NMpre_name3", "pre": ["SS"], "post": [], "kind": "same_voice"},
        {"id": "NMpre_name14", "pre": ["SL"], "post": [], "kind": "same_voice"},
        {"id": "NMpre_noname7", "pre": ["SN"], "post": [], "kind": "same_voice"},
        {"id": "NMpre_diffvoice", "pre": ["SD"], "post": [], "kind": "diff_voice"},
    ]
    cfg = {"work_id": "synthetic_wrong_name", "group": "synthetic", "focus_word": "Melos", "target_canonical": "Melos said.", "gap_ms": 300,
           "pools": {"p_name": pool}, "targets": targets, "recipes": recipes, "targets_recipes": {}}
    json.dump(cfg, open(OUT + "/config_namedefect_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("namedefect ok", round(len(y) / sr, 2), "s")


# ------------------------------------------------------------------ truncation sweep (どこまで切るとASRが語末欠落に気付くか)
def make_truncsweep():
    mel = json.load(open(OUT + "/config_melos_01.json", encoding="utf-8"))["pools"]["a2"]
    base = mel["clips"]["n_c7"]["path"]
    a = L.read_wav_mono(base)
    end = speech_end(a)
    targets = []
    for ms in (300, 380, 460):
        y = fade_out(a[:int((end - ms / 1000) * 24000)])
        p = OUT + f"/synthetic_audio/sweep_B2_trunc{ms}.wav"
        L.write_wav(p, y)
        targets.append({"id": f"sweep_B2_trunc{ms}", "path": p, "pool": "p_sweep", "voice": "Aoede", "canonical": "The ruler smiled and said,",
                        "focus_word": "said", "category": "synthetic_final_consonant_loss",
                        "defect": f"last {ms} ms of speech removed (speech_end={end:.2f}s), fade 8ms", "note": "known defect (offline edit)", "label_hint": "known_defect"})
    clips = {k: {"path": v["path"], "text": v["text"], "voice": v["voice"], "model": v["model"]} for k, v in mel["clips"].items()}
    pool = {"slots": {"SS": ["n_c1"], "SD": ["m_c4"]}, "clips": clips}
    recipes = [{"id": "R00_alone", "pre": [], "post": [], "kind": "alone"},
               {"id": "SSpre", "pre": ["SS"], "post": [], "kind": "same_voice"},
               {"id": "SDpre", "pre": ["SD"], "post": [], "kind": "diff_voice"}]
    cfg = {"work_id": "synthetic_truncation_sweep", "group": "synthetic", "focus_word": "said", "target_canonical": "The ruler smiled and said,",
           "gap_ms": 300, "pools": {"p_sweep": pool}, "targets": targets, "recipes": recipes, "targets_recipes": {}}
    json.dump(cfg, open(OUT + "/config_truncsweep_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("truncsweep ok")


if __name__ == "__main__":
    which = sys.argv[1]
    {"synthetic": make_synthetic, "natural": make_natural, "namedefect": make_namedefect, "truncsweep": make_truncsweep}[which]()
