# -*- coding: utf-8 -*-
"""raw/azure_calls.jsonlの**全行**(除外なし)から条件別集計表(md+json)とProduction判定offline注入の結果表を作る。"""
import argparse
import collections
import json
import os
import re
import sys

import er084_azure_phraselist_weight_trial_01_lib as L

COND_ORDER = list(L.COND_NAMES)


def melos_hits(text) -> int:
    return len(L.RE_MELOS.findall(text or ""))


def name_window(text, n=34):
    m = re.search(r"rock\.\s*(.{0,%d})" % n, text or "")
    return m.group(1) if m else None


def aggregate(rows: list, audio_meta: dict) -> dict:
    """audio_meta: audio_id -> {label: positive|negative, expected_melos: int, ...}。除外なし。"""
    by = collections.OrderedDict()
    for r in rows:
        key = (r["audio_id"], r["cond"])
        by.setdefault(key, []).append(r)
    cells = []
    for (aid, cond), rs in by.items():
        meta = audio_meta.get(aid, {})
        label = meta.get("label", "positive")
        exp = meta.get("expected_melos", 1 if label == "positive" else 0)
        texts = [r["text"] for r in rs]
        n_err = sum(1 for r in rs if r.get("err"))
        ok = [r for r in rs if not r.get("err")]
        hits = [melos_hits(r["text"]) for r in ok]
        if label == "positive":
            correct = sum(1 for h in hits if h == exp and exp > 0)
        else:
            correct = sum(1 for h in hits if h == 0)  # 負例の「正しい」=Melosと出さない
        false_melos = sum(1 for h in hits if h > 0) if label == "negative" else 0
        wrong = collections.Counter(w for r in ok for w in r["cls"]["wrong"])
        wires = sorted(set(w for r in rs for w in r.get("wire_evidence", {}).get("wire_bias", [])))
        cells.append({
            "audio_id": aid, "cond": cond, "label": label, "n_calls": len(rs), "n_err": n_err, "n_ok": len(ok),
            "expected_melos": exp, "correct": correct, "false_melos": false_melos,
            "distinct_transcripts": len(set(t for t in texts if t is not None)),
            "wrong_variants": dict(wrong), "wire_bias": wires,
            "wire_has_dgi": sorted(set(bool(r.get("wire_evidence", {}).get("wire_has_dgi")) for r in rs)),
            "name_windows": sorted(set(name_window(r["text"]) or "" for r in ok)),
        })
    return {"cells": cells, "n_rows": len(rows)}


def rates_by_condition(agg: dict) -> dict:
    out = {}
    for c in COND_ORDER:
        pos = [x for x in agg["cells"] if x["cond"] == c and x["label"] == "positive"]
        neg = [x for x in agg["cells"] if x["cond"] == c and x["label"] == "negative"]
        pn = sum(x["n_ok"] for x in pos)
        nn = sum(x["n_ok"] for x in neg)
        out[c] = {
            "positive_n": pn, "positive_correct": sum(x["correct"] for x in pos),
            "positive_rate": (sum(x["correct"] for x in pos) / pn) if pn else None,
            "negative_n": nn, "negative_false_melos": sum(x["false_melos"] for x in neg),
            "negative_false_rate": (sum(x["false_melos"] for x in neg) / nn) if nn else None,
        }
    return out


def judge_table(rows: list, audio_meta: dict) -> list:
    """各行のAzure転写を注入し、Production判定(offline)の結果を得る。重複(同一audio+cond+text)は1回だけ計算。"""
    import er084_azure_phraselist_weight_trial_01_judge as J
    cache, out = {}, []
    for r in rows:
        meta = audio_meta.get(r["audio_id"], {})
        if not meta.get("canonical_text") or meta.get("primary_text") is None:
            continue
        k = (r["audio_id"], r["text"])
        if k not in cache:
            cache[k] = J.judge_offline(meta["canonical_text"], meta["primary_text"], r["text"],
                                       os.path.join(L.ROOT, r["wav_path"]))
        j = cache[k]
        out.append({"audio_id": r["audio_id"], "cond": r["cond"], "rep": r["rep"], "state": j["state"],
                    "reason_code": j["reason_code"], "verified": j["verified"], "classification": j["classification"],
                    "human_review_required": j["human_review_required"]})
    return out


def load_audio_meta(design: dict, manifest: dict | None) -> dict:
    meta = {}
    for a in design["phases"]["A"]["audio"]:
        pt = None
        jp = os.path.join(L.ROOT, a["path"][:-4] + ".json")
        if os.path.exists(jp):
            pt = json.load(open(jp, encoding="utf-8")).get("asr_text")
        meta[a["id"]] = {"label": a.get("label", "positive"), "canonical_text": a.get("canonical_text"),
                         "expected_melos": len(L.RE_MELOS.findall(a.get("canonical_text", ""))), "primary_text": pt}
    if manifest:
        for a in manifest["audio"]:
            meta[a["id"]] = {k: a.get(k) for k in ("label", "canonical_text", "expected_melos", "primary_text")}
    return meta


def render_md(agg, rates, judges, rows) -> str:
    lines = ["# Phase結果(自動生成: er084_azure_phraselist_weight_trial_01_eval.py、raw全行を対象・除外なし)", "",
             f"raw行数: {agg['n_rows']}", "", "## 条件別集計(audio x 条件)", "",
             "| audio | 条件 | n | err | Melos正認識/期待 | 誤Melos(負例) | 異なり転写数 | 誤認識variant | 送信bias(wire) | dgi有 | name直後窓 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(agg["cells"], key=lambda z: (z["audio_id"], COND_ORDER.index(z["cond"]))):
        lines.append(f"| {x['audio_id']} | {x['cond']} | {x['n_calls']} | {x['n_err']} | {x['correct']}/{x['n_ok']} | "
                     f"{x['false_melos']} | {x['distinct_transcripts']} | {x['wrong_variants']} | {x['wire_bias']} | "
                     f"{x['wire_has_dgi']} | {' / '.join(x['name_windows'])} |")
    lines += ["", "## 条件別率(正例=Melos正認識率、負例=誤Melos率)", "",
              "| 条件 | 正例 正認識 | 正例率 | 負例 誤Melos | 負例率 |", "|---|---|---|---|---|"]
    for c, v in rates.items():
        pr = "-" if v["positive_rate"] is None else f"{v['positive_rate']:.2f}"
        nr = "-" if v["negative_false_rate"] is None else f"{v['negative_false_rate']:.2f}"
        lines.append(f"| {c} | {v['positive_correct']}/{v['positive_n']} | {pr} | {v['negative_false_melos']}/{v['negative_n']} | {nr} |")
    if judges:
        lines += ["", "## Production判定offline注入(Primary=既存OpenAI転写、Secondary=各条件のAzure転写。判定ロジック無変更)", "",
                  "| audio | 条件 | rep | 状態 | reason_code | verified | classification | HR要 |", "|---|---|---|---|---|---|---|---|"]
        for j in judges:
            lines.append(f"| {j['audio_id']} | {j['cond']} | {j['rep']} | {j['state']} | {j['reason_code']} | {j['verified']} | "
                         f"{j['classification']} | {j['human_review_required']} |")
    lines += ["", "## 転写全文(raw、除外なし)", ""]
    for r in rows:
        lines.append(f"- {r['audio_id']} / {r['cond']} / r{r['rep']}: name窓=`{name_window(r['text'])}` err={r['err']}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True, help="結果md。同名.jsonも出力")
    ap.add_argument("--design", default=os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01", "design_matrix_01.json"))
    ap.add_argument("--wav-manifest", default=None)
    ap.add_argument("--no-judge", action="store_true")
    a = ap.parse_args(argv)
    rows = L.read_raw(a.raw)
    design = json.load(open(a.design, encoding="utf-8"))
    manifest = json.load(open(a.wav_manifest, encoding="utf-8")) if a.wav_manifest else None
    meta = load_audio_meta(design, manifest)
    agg = aggregate(rows, meta)
    rates = rates_by_condition(agg)
    judges = [] if a.no_judge else judge_table(rows, meta)
    open(a.out, "w", encoding="utf-8").write(render_md(agg, rates, judges, rows))
    json.dump({"agg": agg, "rates": rates, "judges": judges}, open(os.path.splitext(a.out)[0] + ".json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"rows={len(rows)} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
