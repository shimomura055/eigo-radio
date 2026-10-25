# -*- coding: utf-8 -*-
"""FZ-NARRATION-CHUNK-TTS-TRIAL-01 (DEV/Trial専用、Phase 0 = 分割規則の決定論planner。API 0・TTS 0・Production変更0)。

目的: Family Z正式経路のnarrator story clipのうち『長い地の文clip』だけを、段落境界>文境界の優先で追加分割するchunk planを決定論的に作る。
既存のDialogue/話者切替境界(= 既存plan_clips / plan_story_segments が作るclip境界)は一切変更しない(入力clipをそのまま受け、narrator clipの内部だけを分割)。
Production module(er062/er063/er026/er013)は編集しない。本ファイルはimportも不要(純粋関数のみ)。出力はDEV dirのみ。
設計正本: docs/research/FZ-NARRATION-CHUNK-TTS-TRIAL-01/DESIGN_01.md
"""
from __future__ import annotations

import json
import math
import os
import re

# 分割閾値: Family C/Z story clip語数目安の target_words=100 (er013_family_c_production_01.py:plan_story_segments の target_words)。
# 根拠は DESIGN_01 §2 (現行Adv narrator clipの語数別WPM分布: <30語136 / 30-59語157 / 60-99語159 / >=100語163 WPM)。
SPLIT_THRESHOLD_WORDS = 100
MIN_CHUNK_WORDS = 25   # これ未満の断片chunkは作らない(Xの最短14語chunkで文脈なし短文の品質が論点だったため、それより大きく取る)
EXTRA_PAUSE_SECONDS = 0.2   # ユーザー指定(2026-10-25)。新しい独自秒数ではない

_SENT_END = re.compile(r"(?<=[.!?])[\"']?\s+")


def normalize_for_tts(raw: str) -> str:
    """er013_family_c_production_01.normalize_for_tts と同一(スマートクォート→ASCII、空白圧縮)。planの語数定義と一致させるための転記。"""
    t = raw.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    return re.sub(r"\s+", " ", t).strip()


def _wc(text: str) -> int:
    return len(normalize_for_tts(text).split())


def _sentence_units(para: str) -> list:
    """段落を文単位に分ける。引用符の途中(未閉じの二重引用符)で切れる位置は候補にしない。"""
    t = normalize_for_tts(para)
    units, start = [], 0
    for m in _SENT_END.finditer(t):
        cut = m.end()
        left = t[start:cut]
        if left.count('"') % 2 == 1:
            continue  # 引用の途中
        units.append(t[start:cut].strip())
        start = cut
    if t[start:].strip():
        units.append(t[start:].strip())
    return units


def _candidates(paragraph_texts: list) -> list:
    """分割候補 = [(priority, left_units_text_list, right..)] ではなく、(priority, 累積語数, 位置ラベル)の列。
    priority 0 = 段落境界(最優先)、1 = 段落内の文境界(引用の途中は除く)。"""
    cands, cum = [], 0
    for pi, para in enumerate(paragraph_texts):
        units = _sentence_units(para)
        for ui, u in enumerate(units):
            cum += _wc(u)
            last_unit = ui == len(units) - 1
            if pi == len(paragraph_texts) - 1 and last_unit:
                continue  # clip末尾は候補外
            cands.append({"priority": 0 if last_unit else 1, "cum_words": cum, "after_paragraph": pi, "after_sentence": ui})
    return cands


def plan_clip_chunks(clip: dict, paragraph_texts: list) -> dict:
    """1 clipの追加分割計画。narrator以外/閾値以下は分割しない(unchanged)。
    clip: {id, voice, word_count, source_paragraph_indices, text}。paragraph_texts: そのclipに含まれる段落の生テキスト(順)。
    戻り値: {clip_id, split: bool, reason, chunks:[{chunk_id, words, text, first_para, last_para}], cuts:[...]}"""
    cid, wc = clip["id"], clip["word_count"]
    if clip.get("voice") != "narrator":
        return {"clip_id": cid, "split": False, "reason": "not_narrator(話者切替/セリフclipは不変)", "chunks": [], "cuts": []}
    if wc <= SPLIT_THRESHOLD_WORDS:
        return {"clip_id": cid, "split": False, "reason": f"words={wc}<=閾値{SPLIT_THRESHOLD_WORDS}", "chunks": [], "cuts": []}
    # 文単位テキスト列(結合 = 現行clip.textと同一になることを検証する)
    joined = normalize_for_tts(" ".join(paragraph_texts))
    assert joined == normalize_for_tts(clip["text"]), "clip.textと段落テキストが一致しない(planとの不整合)"
    k = math.ceil(wc / SPLIT_THRESHOLD_WORDS)
    cands = _candidates(paragraph_texts)
    cuts, prev, used = [], 0, set()
    for i in range(1, k):
        target = prev + (wc - prev) / (k - i + 1)
        ok = [c for c in cands if c["cum_words"] - prev >= MIN_CHUNK_WORDS and wc - c["cum_words"] >= MIN_CHUNK_WORDS * (k - i)
              and c["cum_words"] not in used]
        if not ok:
            return {"clip_id": cid, "split": False, "reason": "no_valid_cut(最小chunk語数を満たす境界なし→不変)", "chunks": [], "cuts": []}
        # 段落境界(priority 0)があればそれを優先。優先順 = 段落境界 > 文境界、同優先内は目標語数との差が最小
        p0 = [c for c in ok if c["priority"] == 0]
        pool = p0 if p0 else ok
        best = min(pool, key=lambda c: (abs(c["cum_words"] - target), c["cum_words"]))
        cuts.append(best)
        used.add(best["cum_words"])
        prev = best["cum_words"]
    # chunk化
    sentences = []
    for pi, para in enumerate(paragraph_texts):
        for ui, u in enumerate(_sentence_units(para)):
            sentences.append((pi, ui, u))
    chunks, start_idx, cum = [], 0, 0
    bounds = [(c["after_paragraph"], c["after_sentence"]) for c in cuts] + [(None, None)]
    cur = []
    bi = 0
    for pi, ui, u in sentences:
        cur.append((pi, ui, u))
        if bounds[bi] != (None, None) and (pi, ui) == bounds[bi]:
            chunks.append(cur)
            cur = []
            bi += 1
    if cur:
        chunks.append(cur)
    out = []
    for j, ch in enumerate(chunks):
        text = " ".join(u for _, _, u in ch)
        out.append({"chunk_id": f"{cid}_k{j + 1}", "words": _wc(text), "text": text, "first_para": ch[0][0], "last_para": ch[-1][0]})
    assert normalize_for_tts(" ".join(c["text"] for c in out)) == joined, "chunk結合が元clipと一致しない(欠落/重複)"
    return {"clip_id": cid, "split": True, "reason": f"narrator words={wc}>{SPLIT_THRESHOLD_WORDS}: {k} chunks, "
            + "/".join("段落境界" if c["priority"] == 0 else "文境界" for c in cuts),
            "chunks": out, "cuts": [{"after_paragraph": c["after_paragraph"], "after_sentence": c["after_sentence"],
                                     "cum_words": c["cum_words"], "priority": c["priority"]} for c in cuts],
            "extra_pause_seconds": EXTRA_PAUSE_SECONDS}


def plan_run(run_dir: str, level: str, article_md_relpath: str) -> dict:
    """読取専用: run_dirのsegment_plan_<level>.json と 記事md(writer/r2.md等)から、全clipの追加分割planを作る。"""
    import sys
    root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root)
    import er062_family_z_structure_01 as st   # 読取のみ(split_title_body/clean_body_paragraphs)
    plan = json.load(open(os.path.join(root, run_dir, f"segment_plan_{level}.json"), encoding="utf-8"))
    txt = open(os.path.join(root, run_dir, article_md_relpath), encoding="utf-8").read()
    _, body = st.split_title_body(txt)
    paras = st.clean_body_paragraphs(body)
    res = []
    for c in plan["clips"]:
        ptexts = [paras[i] for i in c["source_paragraph_indices"]]
        # 段落が複数clipに跨る(セリフ混在)場合は narrator のみ対象で、段落の一部だけがnarrator clipに入る。
        # その場合は clip.text を唯一の正として段落代わりに扱う(段落境界情報は失うため文境界のみ)
        joined = normalize_for_tts(" ".join(ptexts))
        if joined != normalize_for_tts(c["text"]):
            ptexts = [c["text"]]
        res.append(plan_clip_chunks(c, ptexts))
    return {"run_dir": run_dir, "level": level, "threshold_words": SPLIT_THRESHOLD_WORDS, "min_chunk_words": MIN_CHUNK_WORDS,
            "extra_pause_seconds": EXTRA_PAUSE_SECONDS, "clips": res}


if __name__ == "__main__":
    import sys
    out_dir = "er026_output/family_z_dev_trials/fz_narration_chunk_01"
    os.makedirs(out_dir, exist_ok=True)
    targets = {
        "tth_1b_s1_adv": ("er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1", "b1b", "writer/r2.md"),
        "tth_run_sf_prod_01_adv": ("er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01", "b1b", "writer/r2.md"),
        "magi_run_sf_prod_01_adv": ("er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01", "b1b", "writer/r2.md"),
    }
    for name, (rd, lv, md) in targets.items():
        if not os.path.exists(os.path.join(rd, md)):
            print("skip", name, "(記事mdなし)")
            continue
        r = plan_run(rd, lv, md)
        with open(f"{out_dir}/chunk_plan_{name}_01.json", "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        print(name, [(c["clip_id"], [x["words"] for x in c["chunks"]] if c["split"] else "-") for c in r["clips"] if c["split"]])
