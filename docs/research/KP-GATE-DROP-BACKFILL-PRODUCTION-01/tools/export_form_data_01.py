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
import hashlib
import json
import os
import sys

LEVEL_LABEL = {"a2": "Standard", "b1b": "Advanced"}
DEFAULT_CAP = 12                                   # 2026-10-27 P7/W5'配線(KP_CANDIDATE_MAX 8->12)。docに記録が無い場合の既定
DEFAULT_CAP_BY_KIND = {"phrase": 7, "word": 5}


def cap_info(doc: dict) -> tuple:
    """(cap, cap_by_kind, source)。docのshortfall_detailに記録があればそれを正とする(旧8 docは8のまま)。無ければ既定12 / 7+5。"""
    sd = doc.get("shortfall_detail") or {}
    cap = sd.get("cap")
    cbk = sd.get("cap_by_kind")
    src = "candidate_doc" if (cap and cbk) else ("candidate_doc_cap_only" if cap else "default_12_7_5")
    return (cap or DEFAULT_CAP), (dict(cbk) if cbk else dict(DEFAULT_CAP_BY_KIND)), src


def kind_of(c: dict) -> str:
    k = c.get("kind")
    if k in ("phrase", "word"):
        return k
    return "word" if len((c.get("used_form") or "").split()) == 1 else "phrase"      # 古いdoc(kind欠落)を許容


def kind_source_of(c: dict) -> str:
    """kindの出所(委任_03)。候補docのkindを逐語で使ったか、語数から導出したか。"""
    return "candidate_doc" if c.get("kind") in ("phrase", "word") else "derived_from_word_count"


def doc_sha256(doc: dict) -> str:
    """候補docの自己sha。er119_kp_human_review_01.candidates_sha256と同一算式(candidates_sha256キーを除いたjsha)。Production moduleに依存しないよう再掲。"""
    d = {k: v for k, v in doc.items() if k != "candidates_sha256"}
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def sha_info(doc: dict, source_kind: str) -> tuple:
    """(candidates_sha256, candidates_sha256_source)。docのフィールドが無い場合はnull(算出・捏造しない)。docの値と再算出が不一致なら例外。"""
    v = doc.get("candidates_sha256")
    if v:
        if v != doc_sha256(doc):
            raise ValueError("candidates_sha256 mismatch: doc field != recomputed")
        return v, "candidate_doc_field"
    return None, ("unavailable_replay_doc" if source_kind.startswith("REPLAY") else "unavailable_dev_trial_doc")


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


REASON_PLACEHOLDERS = ("replay", "mock", "fixture")      # replay/mock fixtureが埋めた非実在の理由(AI理由として表示しない)


def gloss_status(c: dict, source_kind: str) -> str:
    """日本語訳の正式性(委任_02 ①)。official=Production正式経路で生成されgloss整合Gate通過済み(ページ表示・P8-KP音声と同じ`japanese_gloss`)/
    provisional=意味確認待ち・試作(DEV Trial)・replay由来で正式扱いしない/missing=未生成。仮訳を正式訳として扱わない。"""
    if not (c.get("japanese_gloss") or "").strip():
        return "missing"
    fl = c.get("flags") or {}
    g = (c.get("gates") or {}).get("gloss")
    if fl.get("gloss_hr_pending") or g == "HR_PENDING":
        return "provisional"
    if source_kind == "PRODUCTION_FORMAL_PATH" and g in ("ALIGNED", "HUMAN_RESOLVED"):
        return "official"
    return "provisional"


def reason_info(c: dict) -> tuple:
    """(reason_ja, reason_source)。AIが実際に出した理由だけを返す。P7/W5'(2026-10-27配線、KP-PHRASE7-WORD5-PRODUCTION-01)では全候補(call1含む)に`reason_ja`があり逐語で返す。
    旧Prompt 2 doc(3+5以前)のcall1候補は理由が空で、その場合のみ`none_call1_has_no_reason`。fixture placeholderは理由として扱わない。"""
    r = (c.get("reason_ja") or "").strip()
    origin = c.get("origin")
    if r and r.lower() not in REASON_PLACEHOLDERS:
        return r, "ai_" + (origin or "unknown")
    if r:
        return "", "none_placeholder_not_real"
    if origin == "call1" or origin is None:
        return "", "none_call1_has_no_reason"
    return "", "none_not_generated"


def entry(c: dict, source_kind: str = "PRODUCTION_FORMAL_PATH") -> dict:
    fl = c.get("flags") or {}
    rj, rsrc = reason_info(c)
    e = {
        "id": c["candidate_id"], "candidate_id": c["candidate_id"], "kind_source": kind_source_of(c), "term": c.get("used_form") or c.get("selection_phrase"),
        "meaning_ja": c.get("japanese_gloss") or "", "excerpt": c.get("source_sentence") or "",
        "ja_gloss": c.get("japanese_gloss") or "", "ja_gloss_status": gloss_status(c, source_kind),
        "ja_gloss_source": "kp_candidates.japanese_gloss(ページ表示・P8-KP音声の元と同一項目。AI再生成なし)",
        "reason_source": rsrc,
        "kind": kind_of(c), "origin": c.get("origin"), "ai_rank": c.get("ai_rank"),
        "auto_eligible": bool(c.get("auto_eligible")), "human_selectable": bool(c.get("human_selectable", True)),
        "reason_ja": rj,
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
    cap, cbk, _ = cap_info(doc)
    parts = [f"候補{n}件/上限{cap}件(フレーズ最大{cbk.get('phrase')}・単語最大{cbk.get('word')})"]
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
            grammar: list | None = None, cand_path: str | None = None) -> dict:
    cands = sorted(doc.get("candidates") or [], key=lambda c: c.get("ai_rank") or 99)
    es = [entry(c, source_kind) for c in cands]
    bf = doc.get("backfill") or {}
    sha, sha_src = sha_info(doc, source_kind)
    cap, cbk, cap_src = cap_info(doc)
    sd_out = dict(doc.get("shortfall_detail") or {}) if doc.get("shortfall_detail") is not None else None
    if sd_out is not None:
        sd_out.setdefault("cap", cap)
        sd_out.setdefault("cap_by_kind", cbk)
    out = {
        "schema": "eigo_radio_selection_article_v1", "slug": slug, "level": level, "level_label": LEVEL_LABEL.get(level, level), "name": name, "family": family,
        "candidates_sha256": sha, "candidates_sha256_source": sha_src,
        "source_kp_candidates_path": (os.path.relpath(cand_path).replace(os.sep, "/") if cand_path else None),
        "source": {"kind": source_kind, "trial": "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "run": run, "text_sha256": text_sha256 or doc.get("text_sha256"),
                   "model_id": {"kp": doc.get("model_id")}, "prompt_sha256": doc.get("prompt_sha256"), "note_ja": note_ja},
        "cap": cap, "cap_by_kind": cbk, "cap_source": cap_src,
        "phrases": [e for e in es if e["kind"] == "phrase"][:cbk.get("phrase", 7)], "words": [e for e in es if e["kind"] == "word"][:cbk.get("word", 5)],
        "backfill": {"enabled": bf.get("enabled"), "triggered": bf.get("triggered"), "status": bf.get("status"), "reason": bf.get("reason"),
                     "E_total": (bf.get("E") or {}).get("total"), "N_total": (bf.get("N") or {}).get("total"), "added": bf.get("added") or [],
                     "dropped_by_stage": bf.get("dropped_by_stage") or {}},
        "shortfall": bool(doc.get("shortfall")), "shortfall_detail": sd_out, "shortfall_note_ja": shortfall_note_ja(doc),
        "grammar": grammar or [],
    }
    over = [e for e in es if e["kind"] == "phrase"][cbk.get("phrase", 7):] + [e for e in es if e["kind"] == "word"][cbk.get("word", 5):]
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
                  note_ja=a.note_ja, text_sha256=a.text_sha256, cand_path=a.cand)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"out": a.out, "phrases": len(out["phrases"]), "words": len(out["words"]), "shortfall_note_ja": out["shortfall_note_ja"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
