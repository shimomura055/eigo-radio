# -*- coding: utf-8 -*-
"""KP候補doc(`kp_candidates.json`、Production正式経路またはreplayの`generate_candidates`出力)を学習項目選定フォームv3のデータJSON
(`eigo_radio_selection_article_v1`)へ変換するtool。API 0・read-only(入力docは変更しない)。DATA_CONTRACT_01.mdに従う。

出力: phrases[](kind=phrase)/words[](kind=word)。各entryは既存4項目(id/term/meaning_ja/excerpt)+flag/flag_note_ja(フォームUIが表示)+契約項目
(kind/origin/ai_rank/auto_eligible/human_selectable/flags/rescue要約/reason_ja)。doc単位でbackfill要約・shortfall・shortfall_detailを持つ。
grammar[]は正式Part 2候補が無い限り空(仮データを入れない)。

実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\export_form_data_01.py
        --cand <kp_candidates.json> --slug <slug> --level <a2|b1b> --name <表示名> --family <X|Y|Z> --out <out.json>
        [--grammar <grammar_candidates.json>] [--source-kind PRODUCTION_FORMAL_PATH|REPLAY_FROZEN_INITIAL_REAL_BACKFILL] [--run <run名>] [--note-ja <注記>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

LEVEL_LABEL = {"a2": "Standard", "b1b": "Advanced"}


def kind_of(c: dict) -> str:
    k = c.get("kind")
    if k in ("phrase", "word"):
        return k
    return "word" if len((c.get("used_form") or "").split()) == 1 else "phrase"      # 古いdoc(kind欠落)を許容


def flag_notes(c: dict) -> list:
    fl = c.get("flags") or {}
    notes = []
    if c.get("origin") == "backfill":
        notes.append("補完候補(Gate除外の代替)")
    if fl.get("rescued"):
        notes.append("KP救済済み(" + "/".join(fl.get("rescue_codes") or (c.get("rescue") or {}).get("codes") or []) + ")")
    if fl.get("qa_fail"):
        notes.append("QA不合格(人間のみ採用可)")
    if fl.get("gloss_hr_pending"):
        notes.append("意味確認待ち(人間のみ採用可)")
    if fl.get("similar_to_ng"):
        notes.append("不適切(NG)指定に類似(人間のみ採用可)")
    if fl.get("redundant_with"):
        notes.append("他候補と重複の可能性")
    if not c.get("auto_eligible", True) and not any(n.startswith(("QA", "意味", "不適切")) for n in notes):
        notes.append("AUTO採用不可(人間のみ採用可)")
    return notes


def entry(c: dict) -> dict:
    fl = c.get("flags") or {}
    e = {
        "id": c["candidate_id"], "term": c.get("used_form") or c.get("selection_phrase"),
        "meaning_ja": c.get("japanese_gloss") or "", "excerpt": c.get("source_sentence") or "",
        "kind": kind_of(c), "origin": c.get("origin"), "ai_rank": c.get("ai_rank"),
        "auto_eligible": bool(c.get("auto_eligible")), "human_selectable": bool(c.get("human_selectable", True)),
        "reason_ja": c.get("reason_ja") or "",
        "flags": {k: fl[k] for k in ("qa_fail", "gloss_hr_pending", "similar_to_ng", "redundant_with", "rescued", "rescue_codes") if k in fl},
    }
    if c.get("selection_phrase") and c.get("selection_phrase") != e["term"]:
        e["selection_phrase"] = c["selection_phrase"]
    if c.get("rescue"):
        e["rescue"] = {"codes": c["rescue"].get("codes"), "note": c.get("rescue_note")}
    notes = flag_notes(c)
    if notes:
        e["flag"] = "候補の注記"
        e["flag_note_ja"] = " / ".join(notes)
    return e


def shortfall_note_ja(doc: dict) -> str:
    sd = doc.get("shortfall_detail") or {}
    bf = doc.get("backfill") or {}
    n = len(doc.get("candidates") or [])
    if not doc.get("shortfall"):
        return ""
    parts = [f"候補{n}件/上限{sd.get('cap', 8)}件"]
    E = (bf.get("E") or {}).get("total")
    if E:
        parts.append(f"Gate除外{E}件")
    if bf.get("status") == "OK" and bf.get("triggered"):
        parts.append(f"補完{len(bf.get('added') or [])}件を追加")
    elif bf.get("status") == "NOT_TRIGGERED":
        parts.append({"E=0": "Gate除外が無いため補完なし(AIの返答が上限未満。数合わせはしません)", "no_candidate": "候補0件のため補完なし", "no_room": "上限到達のため補完なし"}.get(bf.get("reason"), "補完なし"))
    elif bf.get("status") == "FAILED":
        parts.append("補完は失敗(初回候補のみ)")
    ub = sd.get("unfilled_by_kind") or {}
    miss = [f"{lab}{ub[k]}件" for k, lab in (("phrase", "フレーズ"), ("word", "単語")) if ub.get(k)]
    if miss:
        parts.append("補えなかった種類: " + "・".join(miss))
    return "、".join(parts)


def convert(doc: dict, *, slug: str, level: str, name: str, family: str, run: str, source_kind: str, note_ja: str, text_sha256: str | None = None,
            grammar: list | None = None) -> dict:
    cands = sorted(doc.get("candidates") or [], key=lambda c: c.get("ai_rank") or 99)
    es = [entry(c) for c in cands]
    bf = doc.get("backfill") or {}
    out = {
        "schema": "eigo_radio_selection_article_v1", "slug": slug, "level": level, "level_label": LEVEL_LABEL.get(level, level), "name": name, "family": family,
        "source": {"kind": source_kind, "trial": "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "run": run, "text_sha256": text_sha256 or doc.get("text_sha256"),
                   "model_id": {"kp": doc.get("model_id")}, "prompt_sha256": doc.get("prompt_sha256"), "note_ja": note_ja},
        "phrases": [e for e in es if e["kind"] == "phrase"][:7], "words": [e for e in es if e["kind"] == "word"][:5],
        "backfill": {"enabled": bf.get("enabled"), "triggered": bf.get("triggered"), "status": bf.get("status"), "reason": bf.get("reason"),
                     "E_total": (bf.get("E") or {}).get("total"), "N_total": (bf.get("N") or {}).get("total"), "added": bf.get("added") or [],
                     "dropped_by_stage": bf.get("dropped_by_stage") or {}},
        "shortfall": bool(doc.get("shortfall")), "shortfall_detail": doc.get("shortfall_detail"), "shortfall_note_ja": shortfall_note_ja(doc),
        "grammar": grammar or [],
    }
    over = [e for e in es if e["kind"] == "phrase"][7:] + [e for e in es if e["kind"] == "word"][5:]
    if over:                                   # フォームの枠(フレーズ7/単語5)を超える候補は表示せず別枠に保持(情報は失わない)
        out["overflow"] = over
        out["shortfall_note_ja"] = (out["shortfall_note_ja"] + "、" if out["shortfall_note_ja"] else "") + "枠超過で未表示の候補" + str(len(over)) + "件(overflow)"
    if not grammar:
        out["grammar_note_ja"] = "候補なし・要生成(この記事のPart 2文法解説候補は未生成です。仮データは入れていません)"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--name", required=True)
    ap.add_argument("--family", required=True, choices=("X", "Y", "Z"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", default="")
    ap.add_argument("--source-kind", default="PRODUCTION_FORMAL_PATH", choices=("PRODUCTION_FORMAL_PATH", "REPLAY_FROZEN_INITIAL_REAL_BACKFILL"))
    ap.add_argument("--note-ja", default="")
    ap.add_argument("--text-sha256", default=None)
    a = ap.parse_args(argv)
    with open(a.cand, encoding="utf-8") as f:
        doc = json.load(f)
    out = convert(doc, slug=a.slug, level=a.level, name=a.name, family=a.family, run=a.run or os.path.dirname(a.cand), source_kind=a.source_kind,
                  note_ja=a.note_ja, text_sha256=a.text_sha256)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"out": a.out, "phrases": len(out["phrases"]), "words": len(out["words"]), "shortfall_note_ja": out["shortfall_note_ja"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
