# ============================================================
# er091_asr_three_way_trial_01_analyze.py (API 0)  Phase 1/2 集計。
# 単体verdict = Production分類器(val.classify_asr_match + sec._step_alternate_pass)をASR転写に適用した「単独でPASS相当か」。
# 同じ分類器を3方式に同一適用する(Primary用に調整された規則を他方式へ流用している点は報告で明記)。
# ============================================================
from __future__ import annotations
import collections
import csv
import json
import math
import os
import re
import statistics

OUT = "er091_output/asr_three_way_trial_01"
RES = os.path.join(OUT, "results")


def manifest():
    return [json.loads(l) for l in open(os.path.join(OUT, "dataset_manifest.jsonl"), encoding="utf-8") if l.strip()]


def raw():
    return [json.loads(l) for l in open(os.path.join(RES, "asr_raw.jsonl"), encoding="utf-8") if l.strip()]


def norm_tokens(t):
    t = (t or "").lower().replace("’", "'").replace("—", " ").replace("-", " ")
    t = re.sub(r"[^a-z0-9' ]+", " ", t)
    return t.split()


def edit(a, b):
    n, m = len(a), len(b)
    d = list(range(m + 1))
    for i in range(1, n + 1):
        p, d[0] = d[0], i
        for j in range(1, m + 1):
            c = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, p + (a[i - 1] != b[j - 1]))
            p = c
    return d[m]


def wer(ref, hyp):
    r, h = norm_tokens(ref), norm_tokens(hyp)
    return edit(r, h) / max(1, len(r))


def cer(ref, hyp):
    r, h = "".join(norm_tokens(ref)), "".join(norm_tokens(hyp))
    return edit(list(r), list(h)) / max(1, len(r))


def effective(rows):
    """(id, method) -> {'neutral':rec, 'prod':rec(なければneutral), 'reps':{rep:rec}}。Production条件でprodが同一呼出の場合はneutralを使う。"""
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["id"], r["method"])].setdefault(r["cond"], {})[r["rep"]] = r
    out = {}
    for k, cd in by.items():
        neutral = (cd.get("neutral") or {}).get(1)
        prod = (cd.get("prod") or {}).get(1) or neutral
        reps = {}
        for rep in (1, 2, 3):
            c = (cd.get("prod") or {}).get(rep) or (cd.get("neutral") or {}).get(rep)
            if c:
                reps[rep] = c
        out[k] = {"neutral": neutral or prod, "prod": prod, "reps": reps}
    return out


_val = None


def verdict(canon, text):
    """Production分類器による単独PASS相当判定。戻り値(passed, label, reason)。text=Noneは(False,'NO_TRANSCRIPT')."""
    global _val
    if _val is None:
        import er006_preprod_hardening_01_validation as v
        import er006_secondary_asr_01 as s
        _val = (v, s)
    v, s = _val
    text = " ".join(str(text).split()) if text is not None else None   # Whisper出力の二重空白を除去(長さ判定等の人工的NG防止)
    if text is None or not str(text).strip():
        return False, "NO_TRANSCRIPT", ""
    cls = v.classify_asr_match(canon, text)
    alt = s._step_alternate_pass(cls) if not cls.should_pass else None
    return bool(cls.should_pass or alt), (alt or getattr(cls, "classification", None)), getattr(cls, "reason", "")


def main():
    man = {r["id"]: r for r in manifest() if not r["duplicate_of"]}
    eff = effective(raw())
    rows = []
    for rid, m in man.items():
        for method in ("openai", "azure", "whisper", "whisper_medium"):
            e = eff.get((rid, method))
            if not e:
                continue
            for cond in ("neutral", "prod"):
                rec = e[cond]
                if rec is None:
                    continue
                text = rec.get("text")
                ok, label, reason = verdict(m["canonical"], text)
                rows.append({"id": rid, "kind": m["kind"], "label": m["label"], "label_class": m["label_class"], "family": m["family"],
                             "level": m["level"], "problem_type": m.get("problem_type"), "method": method, "cond": cond,
                             "canonical": m["canonical"], "transcript": text, "error": rec.get("error"),
                             "wer": round(wer(m["canonical"], text), 4) if text is not None else None,
                             "cer": round(cer(m["canonical"], text), 4) if text is not None else None,
                             "exact_norm_match": norm_tokens(text) == norm_tokens(m["canonical"]) if text is not None else False,
                             "verdict_pass": ok, "verdict_label": label, "wall_s": rec.get("wall_s"), "audio_s": rec.get("audio_s"),
                             "cpu_s": rec.get("cpu_s"), "jpy": rec.get("jpy", 0.0), "phrase_list": rec.get("phrase_list"),
                             "same_as_neutral": e["prod"] is e["neutral"]})
    json.dump(rows, open(os.path.join(RES, "phase12_item_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(RES, "phase12_item_results.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in r.items()})
    print("rows", len(rows))


if __name__ == "__main__":
    main()
