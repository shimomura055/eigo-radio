# -*- coding: utf-8 -*-
"""KP候補doc(`kp_candidates.json`、Production正式経路またはreplayの`generate_candidates`出力)を学習項目選定フォームv3のデータJSON
(`eigo_radio_selection_article_v1`)へ変換するtool。API 0・read-only(入力docは変更しない)。DATA_CONTRACT_01.mdに従う。

出力: phrases[](kind=phrase)/words[](kind=word)。各entryは既存4項目(id/term/meaning_ja/excerpt)+flag/flag_note_ja(フォームUIが表示)+契約項目
(kind/origin/ai_rank/auto_eligible/human_selectable/flags/rescue要約/reason_ja)。doc単位でbackfill要約・shortfall・shortfall_detailを持つ。
grammar[]は正式Part 2候補が無い限り空(仮データを入れない)。

実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\export_form_data_01.py
        --cand <kp_candidates.json> --slug <slug> --level <a2|b1b> --name <表示名> --family <X|Y|Z> --out <out.json>
        [--grammar <grammar_candidates.json>] [--source-kind PRODUCTION_FORMAL_PATH|REPLAY_FROZEN_INITIAL_REAL_BACKFILL] [--run <run名>] [--note-ja <注記>]
        [--grammar-study-dir <study_dir>]   (Production: 文法のstudy dirから form_grammar_bundle(level) を直接読む。提示=AI評価Top1/Top2の最大2件(rank順)・
                                             grammar_max_select=1・grammar_presented_ids・grammar_candidates_sha256/grammar_text_sha256を出力する。事前生成が不完全/失敗/sha不整合ならデータを出さずエラー[rc=4]。
                                             --grammar-bundle[保存済みbundle json]とは同時に指定できない)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
LEVEL_LABEL = {"a2": "Standard", "b1b": "Advanced"}
DEFAULT_CAP = 12                                   # 2026-10-27 P7/W5'配線(KP_CANDIDATE_MAX 8->12)。docに記録が無い場合の既定
DEFAULT_CAP_BY_KIND = {"phrase": 7, "word": 5}
GRAMMAR_PRESENT_MAX = 2        # 文法選定仕様(2026-10-27ユーザー正式決定): AI評価Top1/Top2の最大2件のみ提示(rank順)
GRAMMAR_MAX_SELECT = 1         # ユーザーは原則1件選択・0件可・2件同時選択禁止(フォームUI/Validatorはこの値を読む)


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


def _rv():
    """提示集合の唯一の定義(er119_kp_human_review_01.presentable_candidates)。exporter専用の定義を持たない(HR-SELECTION-FLOW-QA-FIRST、2026-10-29)。"""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    import er119_kp_human_review_01 as rv
    return rv


def flag_notes(c: dict) -> list:
    fl = c.get("flags") or {}
    notes = []
    if c.get("origin") == "backfill":
        notes.append("補完候補(Gate除外の代替)")
    if fl.get("rescued"):
        notes.append("KP救済済み(" + "/".join(fl.get("rescue_codes") or (c.get("rescue") or {}).get("codes") or []) + ")")
    if fl.get("similar_to_ng"):
        notes.append("不適切(NG)指定に類似(人間のみ採用可)")
    if fl.get("redundant_with"):
        notes.append("他候補と重複の可能性")
    if not c.get("auto_eligible", True) and not any(n.startswith("不適切") for n in notes):
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


P7W5_PROMPT_IDS = ("kp_prompt_p7", "kp_prompt_w5p")


def is_p7w5_doc(doc: dict) -> bool:
    """候補docが正式7+5(P7/W5')世代か。doc.prompt_ids(call1/call2)または候補単位のprompt_idがP7/W5'を示す場合のみTrue。
    旧Prompt 2 doc(prompt_idsなし/kp_prompt_2等)はFalse(理由欠落を警告しない。フォームは理由欄を出さないだけ)。"""
    ids = list((doc.get("prompt_ids") or {}).values()) + [c.get("prompt_id") for c in (doc.get("candidates") or [])]
    return any(i in P7W5_PROMPT_IDS for i in ids if i)


def reason_missing_warning(doc: dict, entries: list):
    """7+5 docで`reason_ja`が欠落する候補があれば`data_warnings`用dictを返す。正常扱いしない(2026-10-27ユーザー決定§4)。該当なしはNone。"""
    if not is_p7w5_doc(doc):
        return None
    miss = [e["candidate_id"] for e in entries if not e.get("reason_ja")]
    if not miss:
        return None
    return {"code": "reason_missing_in_p7w5", "count": len(miss), "candidate_ids": miss,
            "message_ja": "正式7+5方式の候補にAI理由の欠落が" + str(len(miss)) + "件あります(欠落は正常状態ではありません。該当候補は理由欄を非表示にしています)"}


DIFFICULTY_LEVELS = ("easy", "medium", "hard", "rare")
DIFFICULTY_LABEL_JA = {"easy": "易", "medium": "中", "hard": "難", "rare": "激難(レア)", "unknown": "未判定"}


def difficulty_info(c: dict) -> dict:
    """KP-DIFFICULTY-4LEVEL-DISPLAY-01: 候補の難易度(参考情報。Gateではない)をフォームdataへ透過する。候補docに無い/不正な旧docは`unknown`(未判定)・source=not_graded
    (fail-open: 候補は除外しない)。readable/AIF1コードには含めない(照合コード互換維持)=フォーム表示側だけが使う。"""
    d = c.get("difficulty")
    if isinstance(d, dict) and d.get("level") in DIFFICULTY_LEVELS:
        return {"level": d["level"], "label_ja": DIFFICULTY_LABEL_JA[d["level"]], "reason_ja": (d.get("reason_ja") or "").strip(),
                "source": d.get("source") or "llm"}
    return {"level": "unknown", "label_ja": DIFFICULTY_LABEL_JA["unknown"],
            "reason_ja": (d.get("reason_ja") if isinstance(d, dict) else "") or "", "source": "fail_open" if isinstance(d, dict) else "not_graded"}


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
        "difficulty": difficulty_info(c),
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


def grammar_from_bundle(bundle: dict | None) -> tuple:
    """文法bundle(`er120_part2_wiring_01.form_grammar_bundle`の出力。SCHEMA_CONTRACT_01 §5)を、フォームUIの文法entry(id/title/body/example)へ。
    契約キー(candidate_id/explanation_full/explanation_status/explanation_sha256/level/rank/ai_recommended/para/feature_class)も逐語で併記する。
    戻り値: (entries, grammar_status|None)。bundle無しは([], None)=従来どおり『要生成』扱い。解説本文が空のitemは捏造せず例外(fail-closed)。"""
    if not bundle:
        return [], None
    if len(bundle.get("items") or []) > GRAMMAR_PRESENT_MAX:
        raise ValueError(f"grammar bundle has {len(bundle['items'])} items (> Top1/Top2 present max {GRAMMAR_PRESENT_MAX}); 3rd+ candidates must not be presented")
    ranks = [it.get("rank") for it in bundle.get("items") or []]
    if ranks != sorted(ranks):
        raise ValueError(f"grammar bundle items are not in rank order: {ranks}")
    out = []
    for it in bundle.get("items") or []:
        full = (it.get("explanation_full") or "").strip()
        if not full or it.get("explanation_status") != "provided":
            raise ValueError("grammar bundle item without provided explanation_full: " + str(it.get("id")))
        out.append({"id": it["id"], "candidate_id": it.get("candidate_id") or it["id"], "title": it["title"], "body": it["explanation_full"], "example": it.get("example") or "",
                    "explanation_full": it["explanation_full"], "explanation_status": "provided", "explanation_sha256": it.get("explanation_sha256"),
                    "level": it.get("level"), "rank": it.get("rank"), "ai_recommended": bool(it.get("ai_recommended")), "para": it.get("para"),
                    "feature_class": it.get("feature_class")})
    return out, bundle.get("grammar_status")


def grammar_meta_from_study_dir(study_dir: str, level: str) -> dict:
    """文法候補doc(grammar_candidates.json)の candidates_sha256 / text_sha256(読むだけ。levelはdocのlevel欄と一致を確認)。"""
    with open(os.path.join(study_dir, "grammar_candidates.json"), encoding="utf-8") as f:
        d = json.load(f)
    if d.get("level") != LEVEL_LABEL.get(level):
        raise ValueError(f"grammar_candidates.json level {d.get('level')!r} != {LEVEL_LABEL.get(level)!r}")
    return {"candidates_sha256": d.get("candidates_sha256"), "text_sha256": d.get("text_sha256")}


def grammar_bundle_from_study_dir(study_dir: str, level: str) -> dict:
    """Production経路: 文法study dirから `er120_part2_wiring_01.form_grammar_bundle(study_dir, level=)`(SCHEMA_CONTRACT_01 §5)を直接読む。
    事前生成が不完全・part2_failed.jsonあり・explanations/sha不整合・level不一致は、データを出さずに例外(Part2Error)。呼出側は出力ファイルを作らずエラー終了する
    (grammar_status=candidates_availableにもno_candidates_foundにもしない=『要生成』と区別できない仮データを作らない)。"""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    import er120_part2_wiring_01 as p2w
    return p2w.form_grammar_bundle(study_dir, level=level)


def convert(doc: dict, *, slug: str, level: str, name: str, family: str, run: str, source_kind: str, note_ja: str, text_sha256: str | None = None,
            grammar: list | None = None, cand_path: str | None = None, grammar_status: str | None = None, grammar_source: dict | None = None,
            grammar_meta: dict | None = None) -> dict:
    rv = _rv()
    cands = sorted(rv.presentable_candidates(doc), key=lambda c: c.get("ai_rank") or 99)      # 仕様①: 品質検査を通った候補だけを選択可能に提示する
    excluded_pres = rv.excluded_from_presentation(doc)                                       # 旧doc(旗付きで保存済み)の提示除外。新docは生成時にdropped済み=通常0件
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
        "difficulty_grading": {k: (doc.get("difficulty_grading") or {}).get(k) for k in ("version", "prompt_id", "prompt_sha256", "status", "model_id", "n_graded", "n_unknown")}
        if doc.get("difficulty_grading") else None,
        "shortfall": bool(doc.get("shortfall")), "shortfall_detail": sd_out, "shortfall_note_ja": shortfall_note_ja(doc),
        "grammar": grammar or [],
        "grammar_max_select": GRAMMAR_MAX_SELECT, "grammar_present_max": GRAMMAR_PRESENT_MAX,
        "grammar_presented_ids": [g["id"] for g in (grammar or [])],
    }
    if grammar_meta:                              # 文法候補docのsha(KCPの照合・AI島Std/Advの確認に使う。文法側のsha=KP候補docのcandidates_sha256とは別)
        out["grammar_candidates_sha256"] = grammar_meta.get("candidates_sha256")
        out["grammar_text_sha256"] = grammar_meta.get("text_sha256")
    w = reason_missing_warning(doc, es)
    if w:
        out["data_warnings"] = [w]
    if excluded_pres:                          # 提示から外した候補を隠さず記録(0件のdocはキー自体を出さない=従来とバイト同一)
        out.setdefault("data_warnings", []).append({"code": "presentation_excluded", "count": len(excluded_pres), "candidates": excluded_pres,
                                                    "filter_version": rv.PRESENTABLE_FILTER_VERSION,
                                                    "message_ja": "品質検査で不適合のため選択肢に出していない候補が" + str(len(excluded_pres)) + "件あります(旧候補doc由来)"})
    over = [e for e in es if e["kind"] == "phrase"][cbk.get("phrase", 7):] + [e for e in es if e["kind"] == "word"][cbk.get("word", 5):]
    if over:                                   # フォームの枠(フレーズ7/単語5)を超える候補は表示せず別枠に保持(情報は失わない)
        out["overflow"] = over
        out["shortfall_note_ja"] = (out["shortfall_note_ja"] + "、" if out["shortfall_note_ja"] else "") + "枠超過で未表示の候補" + str(len(over)) + "件(overflow)"
    if grammar_status:
        out["grammar_status"] = grammar_status
    if grammar_source:
        out["grammar_source"] = grammar_source
    if grammar_status == "no_candidates_found":
        out["grammar_note_ja"] = "文法候補なし(この本文から文法解説の候補が抽出されませんでした。事前生成は実施済み)"
    elif not grammar:
        out["grammar_note_ja"] = "候補なし・要生成(この記事のPart 2文法解説候補は未生成です。仮データは入れていません)"
    return out


def write_batch_key(articles_json: str, members: list, batch_id: str = None, generated: str = None) -> dict:
    """articles.json に任意キー `batch`={id, generated, members:[slug__lvl...]} を出力する(SELECTION-UI-BATCH 委任_02B)。
    既存の `articles[]` ほか他キーは一切変更しない(読み込み->batchのみ差替え->temp+renameで原子的に書戻し)。API 0。
    members: 当日の一括選定対象 stem(slug__level)。重複/空/対応dataなしは拒否(何も書かない)。batch_idの既定=日付+members shaの先頭8桁。"""
    import datetime
    import tempfile
    mem = [m.strip() for m in members if m and m.strip()]
    if not mem or len(set(mem)) != len(mem):
        raise ValueError(f"batch.members が空または重複しています: {members!r}")
    base = os.path.dirname(os.path.abspath(articles_json))
    for m in mem:
        if not os.path.exists(os.path.join(base, m + ".json")):
            raise ValueError(f"batch.members の {m!r} に対応するデータ {m}.json が {base} にありません")
    with open(articles_json, "rb") as f:
        raw = f.read()
    doc = json.loads(raw.decode("utf-8-sig"))
    gen = generated or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")
    bid = batch_id or (gen[:10] + "-" + hashlib.sha256("\n".join(mem).encode("utf-8")).hexdigest()[:8])
    doc["batch"] = {"id": bid, "generated": gen, "members": mem}
    fd, tmp = tempfile.mkstemp(dir=base, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            txt = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
            if b"\r\n" in raw:   # 既存の改行コード(CRLF)を保つ(無関係な全行diffを出さない)
                txt = txt.replace("\n", "\r\n")
            f.write(txt.encode("utf-8"))
        os.replace(tmp, articles_json)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return doc["batch"]


def main(argv=None) -> int:
    _av = sys.argv[1:] if argv is None else list(argv)
    if "--set-batch" in _av:   # 既存呼出(--set-batchなし)は完全に従来どおり。articles.jsonのbatchキーだけを更新する別モード
        bp = argparse.ArgumentParser()
        bp.add_argument("--set-batch", action="store_true")
        bp.add_argument("--articles-json", required=True)
        bp.add_argument("--members", required=True, help="カンマ区切りの slug__level")
        bp.add_argument("--batch-id", default=None)
        bp.add_argument("--generated", default=None)
        ba = bp.parse_args(_av)
        try:
            res = write_batch_key(ba.articles_json, ba.members.split(","), ba.batch_id, ba.generated)
        except ValueError as e:
            print(f"[BATCH_KEY][REFUSED] {e}", file=sys.stderr)
            return 2
        print(json.dumps({"articles_json": ba.articles_json, "batch": res}, ensure_ascii=False))
        return 0
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
    ap.add_argument("--grammar-bundle", default=None, help="form_grammar_bundle.json(SCHEMA_CONTRACT_01 §5)。文法候補+解説全文をフォームデータへ取り込む")
    ap.add_argument("--grammar-study-dir", default=None, help="文法のstudy dir(Production経路)。form_grammar_bundleを直接読む。不完全/失敗/不整合はデータを出さずrc=4で終了")
    ap.add_argument("--grammar-source-json", default=None, help="文法の出所(summary_<level>.json等)から grammar_source に入れるJSON")
    a = ap.parse_args(argv)
    with open(a.cand, encoding="utf-8") as f:
        doc = json.load(f)
    gram, gstatus, gsrc, gmeta = [], None, None, None
    if a.grammar_study_dir and a.grammar_bundle:
        raise SystemExit("--grammar-study-dir と --grammar-bundle は同時に指定できません(出所を1つにしてください)")
    if a.grammar_study_dir:
        try:
            bundle = grammar_bundle_from_study_dir(a.grammar_study_dir, a.level)
        except (RuntimeError, ValueError, OSError) as e:   # Part2Error(Part2Stale等)/KpReviewError系。出力ファイルは作らない
            print(json.dumps({"status": "GRAMMAR_NOT_READY", "out": None, "data_warnings": [{"kind": "grammar_pregen_incomplete_or_inconsistent", "error": f"{type(e).__name__}: {e}"}],
                              "next": f"py er119_kp_human_review_cli_01.py grammar-pregen --run <run_dir> --level {a.level} (未生成分だけ事前生成。制作コマンドを同じまま再実行でも可)"},
                             ensure_ascii=False), file=sys.stderr)
            return 4
        gram, gstatus = grammar_from_bundle(bundle)
        gmeta = grammar_meta_from_study_dir(a.grammar_study_dir, a.level)
        if a.grammar_source_json:
            with open(a.grammar_source_json, encoding="utf-8") as f:
                gsrc = json.load(f)
    elif a.grammar_bundle:
        with open(a.grammar_bundle, encoding="utf-8") as f:
            bundle = json.load(f)
        if bundle.get("level") != a.level:
            raise SystemExit(f"grammar bundle level {bundle.get('level')} != --level {a.level}")
        gram, gstatus = grammar_from_bundle(bundle)
        if a.grammar_source_json:
            with open(a.grammar_source_json, encoding="utf-8") as f:
                gsrc = json.load(f)
    out = convert(doc, slug=a.slug, level=a.level, name=a.name, family=a.family, run=a.run or os.path.dirname(a.cand), source_kind=a.source_kind,
                  note_ja=a.note_ja, text_sha256=a.text_sha256, cand_path=a.cand, grammar=gram, grammar_status=gstatus, grammar_source=gsrc, grammar_meta=gmeta)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"out": a.out, "phrases": len(out["phrases"]), "words": len(out["words"]), "grammar": len(out["grammar"]), "shortfall_note_ja": out["shortfall_note_ja"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
