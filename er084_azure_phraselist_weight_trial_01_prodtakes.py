# -*- coding: utf-8 -*-
"""[v02] 本番既存take(Primary NG系)の選定(S-1)。API 0。TRIAL_DESIGN_01.md §2-D-2の選定規則をそのまま実装する。

母集団: er026_output/family_z_production_e2e_01/melos/run_e2e_0[1-5]/{a2,b1b}/narration/attempts/*.json
 (i)確定canonical(同run・同levelのaudit/tts_generation_results.json canonical_text)にMelosを含む
 (ii)記録された本番Primary転写(asr_text)のMelos出現数がcanonicalと異なる(Primary NG系)
 (iii)wavが実在しsha256がattempt jsonと一致
選定(結果非依存): sha256重複除外 -> canonical同一を1「文」とし代表=sha256昇順最小 -> 文の順序=
 [各segment_id(名前昇順)につき(NG take数最多, canonical文字数最長, canonical sha昇順)の1文] + [残り: 代表の秒数昇順, canonical sha昇順]
 -> 20本/500秒に達したら打切り。PhraseListは現行Ledgerから本番と同一の取得で再現。
"""
import argparse
import collections
import glob
import hashlib
import json
import os
import re
import sys
import wave

import er084_azure_phraselist_weight_trial_01_lib as L

MELOS_ROOT = os.path.join("er026_output", "family_z_production_e2e_01", "melos")
RE_MELOS = L.RE_MELOS
MAX_TAKES, MAX_SECONDS = 20, 500.0


def _walk_canon(o, out):
    if isinstance(o, dict):
        for _k, v in o.items():
            if isinstance(v, dict) and v.get("canonical_text") and "segment_id" in v:
                out[v["segment_id"]] = v
            _walk_canon(v, out)


def collect_candidates(root: str = None) -> list:
    root = root or L.ROOT
    cands = []
    for run in sorted(glob.glob(os.path.join(root, MELOS_ROOT, "run_e2e_0[1-5]"))):
        for lvl in ("a2", "b1b"):
            res_p = os.path.join(run, lvl, "audit", "tts_generation_results.json")
            if not os.path.exists(res_p):
                continue
            canon = {}
            _walk_canon(json.load(open(res_p, encoding="utf-8")), canon)
            for p in sorted(glob.glob(os.path.join(run, lvl, "narration", "attempts", "*.json"))):
                a = json.load(open(p, encoding="utf-8"))
                seg, at = a.get("segment_id"), a.get("asr_text")
                c = (canon.get(seg) or {}).get("canonical_text")
                if not c or at is None or not RE_MELOS.search(c):
                    continue
                if len(RE_MELOS.findall(at)) == len(RE_MELOS.findall(c)):
                    continue
                w = p[:-5] + ".wav"
                if not os.path.exists(w):
                    continue
                sha = hashlib.sha256(open(w, "rb").read()).hexdigest()
                if a.get("sha256") and sha != a["sha256"]:
                    continue
                with wave.open(w) as f:
                    dur = f.getnframes() / float(f.getframerate())
                cands.append({"json": os.path.relpath(p, root).replace("\\", "/"), "wav": os.path.relpath(w, root).replace("\\", "/"),
                              "run": os.path.basename(run), "level": lvl, "segment_id": seg, "attempt": a.get("attempt_number"),
                              "route": a.get("route"), "voice": a.get("voice"), "model": a.get("model"),
                              "sha256": sha, "duration_s": round(dur, 3), "primary_text": at, "canonical_text": c,
                              "canon_sha12": hashlib.sha256(c.encode("utf-8")).hexdigest()[:12],
                              "clip_kind": (canon.get(seg) or {}).get("clip_kind")})
    return cands


def select(cands: list, max_takes: int = MAX_TAKES, max_seconds: float = MAX_SECONDS) -> list:
    seen, uniq = set(), []
    for c in cands:  # (1) sha256重複除外
        if c["sha256"] in seen:
            continue
        seen.add(c["sha256"])
        uniq.append(c)
    groups = collections.defaultdict(list)
    for c in uniq:  # (2) canonical同一=1「文」
        groups[c["canon_sha12"]].append(c)
    rep = {k: sorted(v, key=lambda x: x["sha256"])[0] for k, v in groups.items()}
    by_seg = collections.defaultdict(list)
    for k, v in groups.items():
        by_seg[v[0]["segment_id"]].append(k)
    first_round = []
    for seg in sorted(by_seg):  # (3) 各segmentの最多NG文
        best = sorted(by_seg[seg], key=lambda k: (-len(groups[k]), -len(groups[k][0]["canonical_text"]), k))[0]
        first_round.append(best)
    rest = sorted([k for k in groups if k not in first_round], key=lambda k: (rep[k]["duration_s"], k))
    sel, tot = [], 0.0
    for rank, k in enumerate(first_round + rest, 1):
        r = rep[k]
        if len(sel) >= max_takes or tot + r["duration_s"] > max_seconds:
            break
        tot += r["duration_s"]
        sel.append({**r, "selection": {"order": rank, "round": 1 if k in first_round else 2,
                                        "n_ng_takes_in_group": len(groups[k]), "rule": "TRIAL_DESIGN_01.md §2-D-2"}})
    return sel


def ledger_phrases_for(canonical: str) -> list:
    import er006_pronunciation_ledger_01 as pl
    return [h["canonical_spelling"] for h in pl.get_hint_for_text(canonical, min_confidence="low")]


def build_manifest(sel: list, n_candidates: int) -> dict:
    audio = []
    for s in sel:
        audio.append({
            "id": f"PT_{s['run'][-2:]}_{s['level']}_{s['segment_id']}_a{s['attempt']}", "path": s["wav"], "sha256": s["sha256"],
            "duration_s": s["duration_s"], "voice": s["voice"], "model": s["model"], "segment_id": s["segment_id"],
            "run": s["run"], "level": s["level"], "attempt": s["attempt"], "route": s["route"], "source_json": s["json"],
            "label": "positive", "set": "POS_PROD", "sentence_id": s["canon_sha12"], "text": s["canonical_text"],
            "canonical_text": s["canonical_text"], "expected_melos": len(RE_MELOS.findall(s["canonical_text"])),
            "primary_text": s["primary_text"], "primary_source": "attempt json asr_text(Production記録のOpenAI Primary転写。再転写しない)",
            "ledger_phrases": ledger_phrases_for(s["canonical_text"]), "slow6": False, "clip_kind": s["clip_kind"],
            "selection": s["selection"]})
    return {"trial_id": L.TRIAL_ID, "manifest_version": "01(本番take再利用集合。固定)", "n_candidates_primary_ng": n_candidates,
            "n_audio": len(audio), "total_seconds": round(sum(a["duration_s"] for a in audio), 2),
            "note": "wavは本番run dirの既存ファイルを参照(複製・変更しない)。TTS 0。Primary転写は記録値。", "audio": audio}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cands = collect_candidates()
    sel = select(cands)
    m = build_manifest(sel, len(cands))
    json.dump(m, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    segs = collections.Counter(x["segment_id"] for x in m["audio"])
    print(json.dumps({"n_candidates": len(cands), "n_selected": m["n_audio"], "total_seconds": m["total_seconds"],
                      "n_segments": len(segs), "voices": dict(collections.Counter(x["voice"] for x in m["audio"])),
                      "ledger_phrases": sorted({tuple(x["ledger_phrases"]) for x in m["audio"]})}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
