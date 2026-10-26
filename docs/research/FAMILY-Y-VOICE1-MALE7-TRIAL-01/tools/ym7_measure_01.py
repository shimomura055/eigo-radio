# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: 男性7Voiceのsample計測(read-only、API 0)。
 - fresh: --in 配下の全 raw attempt wav(1 attempt = 1 独立TTS draw)を既存tool(yvp_measure_lib_01経由 yfb_*)で計測
 - reuse: 前回Trial(PAUSE-CAUSE-01)の samples_measured.json から Algieba(voice=1)/Schedar(voice=3) のみ(女性Zephyr=voice 2は除外)
 追加指標(DESIGN_01 §4): sent_end(文末境界直後: after語が . ? ! … で終わる)かどうか → mid_long1000 = 文境界に対応しない>=1000ms停止の数(primary)
 使い方: py ym7_measure_01.py --in <fresh_dir> --reuse <samples_measured.json> --out <samples.json>"""
import argparse, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01", "tools"))
import yvp_measure_lib_01 as lib  # noqa: E402

SENT_END = re.compile(r"[.?!…][\"'”’)\]]*$")
REUSE_VOICE = {1: "Algieba", 3: "Schedar"}


def is_sent_end(after_word: str) -> bool:
    return bool(SENT_END.search(after_word or ""))


def add_metrics(r: dict) -> dict:
    pl = r.get("pause_list", [])
    long_ = [p for p in pl if p["ms"] >= 1000]
    r["long1000_n"] = len(long_)
    r["sent_long1000"] = sum(1 for p in long_ if is_sent_end(p["after"]))
    r["mid_long1000"] = sum(1 for p in long_ if not is_sent_end(p["after"]))       # primary(comma含む=文境界以外)
    r["clause_long1000"] = sum(1 for p in long_ if (not p["punct"]))                # 句読点にも対応しない純文中(補助)
    r["bad_mid"] = 1 if r["mid_long1000"] >= 1 else 0
    r["bad_any"] = 1 if r["long1000_n"] >= 1 else 0
    return r


def attach_attempt_meta(r: dict) -> dict:
    j = r["wav"][:-4] + ".json"
    if os.path.exists(j):
        d = json.load(open(j, encoding="utf-8"))
        ev = d.get("repetition_qa_evidence") or {}
        r["asr_verified"] = d.get("verified")
        r["audio_classification"] = d.get("audio_classification")
        r["rep_flag"] = (ev.get("flagged") if isinstance(ev, dict) else None)
        r["route"] = d.get("route")
        r["model"] = d.get("model")
        r["voice_name_attempt"] = d.get("voice")
        it = d.get("instruction_text") or ""
        r["instr_sha"] = hashlib.sha256(it.encode("utf-8")).hexdigest()[:12] if it else None
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--reuse", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    prev = {}
    if os.path.exists(a.out):
        for r in json.load(open(a.out, encoding="utf-8")):
            prev[(r["wav"], r["sha256"])] = r
    texts = {(lv, b): lib.body_text(lv, b) for lv in ("a2", "b1b") for b in (1, 2, 3)}
    rows = []
    # reuse(前回Trial。Voice名=Algieba/Schedarのみ)
    for r in json.load(open(a.reuse, encoding="utf-8")):
        if r["voice"] in REUSE_VOICE:
            r = dict(r)
            r["voice"] = REUSE_VOICE[r["voice"]]
            r["origin"] = "reuse"
            rows.append(add_metrics(r))
    # fresh
    n_new = 0
    for f in sorted(glob.glob(f"{a.inp}/*/body*_*/take*/narration/attempts/*_attempt*.wav")):
        f = f.replace("\\", "/")
        m = re.search(r"/(a2|b1b)/body(\d)_([A-Za-z]+)/take(\d+)/narration/attempts/.*_attempt(\d+)_(.*)\.wav$", f)
        if not m:
            continue
        lv, b, voice, k, att, tag = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5)), m.group(6)
        sha = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if (f, sha) in prev:
            rows.append(prev[(f, sha)])
            continue
        meas = lib.measure_wav(f, texts[(lv, b)])
        r = {"level": lv, "body": b, "voice": voice, "src": "trial", "take": k, "attempt": att, "kind": lib.route_kind(f), "wav": f, "sha256": sha, **meas, "origin": "fresh"}
        rows.append(add_metrics(attach_attempt_meta(r)))
        n_new += 1
    # fresh take 単位(result.json)をtake_resultsとして別出力
    takes = []
    for rp in sorted(glob.glob(f"{a.inp}/*/body*_*/take*/result.json")):
        d = json.load(open(rp, encoding="utf-8"))
        takes.append({k: d.get(k) for k in ("level", "body", "voice", "take", "status", "asr_verified", "asr_judgement_state", "asr_reason_code", "post_slowdown_final_classification",
                                           "tts_generations_used", "duration_seconds", "started_at", "finished_at", "batch", "plan_seq", "wav")})
    json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(takes, open(a.out.replace(".json", "_takes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"samples={len(rows)} (fresh={sum(1 for r in rows if r['origin']=='fresh')}, reuse={sum(1 for r in rows if r['origin']=='reuse')}, newly measured={n_new}), takes={len(takes)} -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
