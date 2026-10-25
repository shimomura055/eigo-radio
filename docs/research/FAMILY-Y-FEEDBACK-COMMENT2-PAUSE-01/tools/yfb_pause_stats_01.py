"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02: yfb_silence_scan_01.py のmeasure/*.json から統計を作る(read-only)。
- 『瞬き分割』: 無音間の有音が blip_ms 未満(既定120ms)なら前後の無音を1つの停止として統合
- 台本の句読点数(境界候補)と統合後ポーズ数を比較し、句読点で説明できない過剰ポーズ(excess)を数える
使い方: py -I yfb_pause_stats_01.py --measure-dir <dir> --parts a2=<parts.json> ... は使わず、--text-map <json: tag->text> を渡す
"""
import argparse, glob, json, os, re


def merge(pauses, blip_ms=120):
    out = []
    for p in pauses:
        if out and (p["start_s"] - out[-1]["end_s"]) * 1000 < blip_ms:
            out[-1]["end_s"] = p["end_s"]
            out[-1]["dur_ms"] = round((out[-1]["end_s"] - out[-1]["start_s"]) * 1000)
            out[-1]["merged"] = out[-1].get("merged", 1) + 1
        else:
            out.append(dict(p))
    return out


def stats(d, text):
    tot = d["duration_s"]
    inner = [p for p in d["pauses"] if p["start_s"] >= 0.05 and p["end_s"] < tot - 0.05]
    m = merge(inner)
    punct = len(re.findall(r"[.?!,;:]", text)) - 1  # 末尾の句点は内部境界ではない
    long700 = [p for p in m if p["dur_ms"] >= 700]
    long1000 = [p for p in m if p["dur_ms"] >= 1000]
    return {"dur_s": tot, "words": d["words"], "raw_inner": len(inner), "merged_inner": len(m), "punct_boundaries": punct,
            "excess_vs_punct": len(m) - punct, "blip_split": len(inner) - len(m),
            "ge700": len(long700), "ge1000": len(long1000), "max_ms": max([p["dur_ms"] for p in m], default=0),
            "mean_ms": round(sum(p["dur_ms"] for p in m) / len(m)) if m else 0,
            "pause_ratio_pct": round(100 * sum(p["dur_ms"] for p in m) / 1000 / tot, 1),
            "lead_ms": d["leading_silence_ms"], "trail_ms": d["trailing_silence_ms"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure-dir", required=True)
    ap.add_argument("--text-map", required=True, help="json: measure json basename(no ext) -> text")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tm = json.load(open(a.text_map, encoding="utf8"))
    res = {}
    for f in sorted(glob.glob(os.path.join(a.measure_dir, "*.json"))):
        k = os.path.basename(f)[:-5]
        if k in tm:
            res[k] = stats(json.load(open(f, encoding="utf8")), tm[k])
    json.dump(res, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(len(res), "files ->", a.out)
