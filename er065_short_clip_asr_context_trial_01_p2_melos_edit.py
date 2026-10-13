# -*- coding: utf-8 -*-
"""委任_03 C: Melos said 全7 takeの s+s 境界の摩擦区間長を測り、(1)実測値を較正分布と比べる、(2)『融合長の摩擦区間を単独sの長さまで短縮した編集音声』
(= 語末sが実際には融合しておらず1つ分しか無い音声の模擬。TTS生成なし、既存wavの編集のみ)を作る。ASR比較は別途(runner)。
usage: python ... <target_single_ms> [threshold=0.4]"""
import json, os, sys
import numpy as np
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er065_short_clip_asr_context_trial_01_p2_acoustic as A

OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
TARGET_MS = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0
TH = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
L.install_write_guard([OUT])
cfg = json.load(open("er065_output/short_clip_asr_context_trial_01/config_melos_01.json", encoding="utf-8"))
os.makedirs(OUT + "/edit_audio", exist_ok=True)
res, targets = [], []
for t in cfg["targets"]:
    p = t["path"]
    r = L.whisper_asr(p, "small")
    ws = [w for w in r["words"] if P.tokens(w["w"])]
    x, sr = A.load(p)
    fr, hop = A.frames(x, sr)
    mx = fr[:, 1].max()
    rec = {"target": t["id"], "words": [(w["w"], round(w["start"], 3), round(w["end"], 3)) for w in ws], "dur": round(len(x) / sr, 3)}
    if len(ws) >= 2:
        e, s = ws[0]["end"], ws[1]["start"]
        rec["runs"] = {str(th): round(A.run_across(fr, hop, e - 0.04, s + 0.04, mx, th)) for th in (0.3, 0.4, 0.5)}
        # 最長runの位置を th=TH で取得
        fric = (fr[:, 0] > TH) & (fr[:, 1] > 0.03 * mx)
        a, b = max(0, int((e - 0.04) / hop)), min(len(fric), int((s + 0.04) / hop))
        best = None; i = 0
        while i < len(fric):
            if fric[i]:
                j = i
                while j < len(fric) and fric[j]: j += 1
                if j > a and i < b and (best is None or j - i > best[1] - best[0]): best = (i, j)
                i = j
            else:
                i += 1
        if best:
            i0, i1 = best
            rec["run_at_TH_ms"] = round((i1 - i0) * hop * 1000); rec["run_span_s"] = (round(i0 * hop, 3), round(i1 * hop, 3))
            cut_ms = (i1 - i0) * hop * 1000 - TARGET_MS
            if cut_ms >= 15:
                # 摩擦区間の中央から cut_ms を除去(両端は20msクロスフェード)
                mid = (i0 + i1) // 2 * hop
                c0 = int((mid - cut_ms / 2000) * sr); c1 = int((mid + cut_ms / 2000) * sr)
                xf = int(0.02 * sr)
                y = np.concatenate([x[:c0], x[c1:]]).astype(np.float32)
                w_ = np.linspace(0, 1, xf)
                y[c0 - xf:c0] = x[c0 - xf:c0] * (1 - w_) + x[c1 - xf:c1] * w_ if c1 - xf >= 0 and c0 - xf >= 0 else y[c0 - xf:c0]
                outp = f"{OUT}/edit_audio/{t['id']}_shortS.wav"
                L.write_wav(outp, y * 32768.0 if np.abs(y).max() <= 1.5 else y, sr)
                rec["edited"] = {"path": outp, "cut_ms": round(cut_ms), "new_dur": round(len(y) / sr, 3)}
                targets.append({"id": t["id"] + "_shortS", "path": outp, "pool": "x", "canonical": "Melos said.", "focus_word": "Melos",
                                "voice": t.get("voice"), "model": t.get("model"), "note": f"edit of {t['id']}: s+s fricative run {rec['run_at_TH_ms']}ms -> {TARGET_MS:.0f}ms",
                                "category": "edit_single_s"})
    res.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)
json.dump(res, open(OUT + "/melos_take_acoustic_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cfg2 = {"work_id": "family_z_melos_run_e2e_02", "group": "p2_edit", "focus_word": "Melos", "target_canonical": "Melos said.", "gap_ms": 300,
        "pools": {"x": {"slots": {}, "clips": {}}}, "targets": targets,
        "recipes": [{"id": "R00_alone", "pre": [], "post": [], "kind": "alone"}], "targets_recipes": {}}
json.dump(cfg2, open(OUT + "/config_edit_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
