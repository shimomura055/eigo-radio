# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 (DEV/Trial専用、Family Z『賢者の贈り物』Advanced=b1bのセリフ8件)。

目的: 現行方式(セリフ本文+既存汎用Dialogue Style)と、改善方式(同一本文・同一Voice・同一model・同一設定で、Styleに
      「話者の感情・心理状態 / 場面 / 直前直後の会話 / 地の文の演出語 / 相手の発言への反応」を追加)を比較する。
      Production採用・実装は対象外(到達上限VALIDATED)。Production file / Prompt / flag / 再利用仕様は一切変更しない。

設計正本: docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/DESIGN_01.md
Phase 0(本ファイルの無料部分・API 0): 対象選定・文脈抽出(決定論)・Style構成・費用見積・試聴ページ骨格・計測/leakage検出。
Phase 1(有料、Opusレビュー後のFable Goまで開始禁止): `llm` / `gen` サブコマンド。`PHASE1_GO.json`が無ければ起動拒否。

再利用(全て既存Production関数のimport。編集しない):
  - er012_b_family_voices_production_01.generate_voice_body_wide_margin(style_prefix_override=...) = Z会話の既存生成関数
    (ASR検査・Cascade・Repetition QA・attempt保存まで同一。『style_prefix_override』は既存の公開引数で、Zのdialogueは従来Noneで呼ぶ)
  - er003_b1_p4c_audio.build_tts_prompt (Structured Separation。STYLE区画にCONTEXTを置き、TEXT TO SPEAKは当該セリフのみ)
  - er063_family_z_audio_01._norm_for_tts (本文の整形。Production Zと同一)
  - er113_fx_paragraph_chunk_trial_01 の DEV専用helper (sink隔離・protected snapshot・measure_wav・mp3書出し)
再利用分離: ①はProduction保存済み音声(読み取りのみ)、②は本Trial専用dirへ新規生成。Production reuse関数(run_tts_stage/cached entry)は
  呼ばず、Master Audio StoreにはZ会話が元々登録されない。DEV出力は _trial_reuse_key(style hash含む)で区別する。
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import html as H
import json
import os
import re
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

MANAGED_ID = "FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01"
OUT_DIR = "er118_output/fz_dialogue_context_tts_trial_01"
PAGE_DIR = "user_test/fz_dialogue_context_trial_01"
PHASE1_GO_FILE = f"{OUT_DIR}/PHASE1_GO.json"
SRC_RUN = "er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01"
LEVEL = "b1b"
PLAN_PATH = f"{SRC_RUN}/segment_plan_{LEVEL}.json"
TTS_RESULTS_PATH = f"{SRC_RUN}/{LEVEL}/audit/tts_generation_results.json"
NARR_DIR = f"{SRC_RUN}/{LEVEL}/narration"
SR24 = 24000
EXPECTED_BASE_STYLE_SHA = "add26d27a79c2cbee982eb5ddc32616b8294494a316b973215c94cccc76ede26"
TRIAL_CAP_JPY = 30.0   # ユーザー指定の追加API費用上限(Trial固有、他案件流用不可)
TTS_MODEL = "gemini-2.5-pro-preview-tts"
LLM_MODEL = "gpt-6-luna"

SPEAKER_DISPLAY = {"della": "Della", "jim": "Jim", "madame": "the hair-shop owner"}

# ---- 対象セリフ(Adv=b1bの全dialogue 8件。8件は下限で、全カテゴリを網羅できるためStdから補わない) ----
# scene_ja/why_ja/category は試聴ページ・選定記録用の表示データ(TTSには渡さない)。
TARGETS = [
    {"id": "full_story_part2_c2", "categories": ["悲しみ・不安", "ためらい・戸惑い"],
     "scene_ja": "クリスマス前日。夫Jimへの贈り物を買うお金がなく、自慢の長い髪を売ろうと髪飾り店の前で息を整え、店の女主人に切り出す場面。",
     "why_ja": "不安とためらいを抱えた切り出し。前後に会話が無く、直前の地の文(息を整える)だけが手掛かり。"},
    {"id": "full_story_part2_c4", "categories": ["相手の発言を受けた返答", "感情を抑えた事務的な発言(対照)"],
     "scene_ja": "女主人がDellaの豊かな髪を持ち上げ、買い取り額を告げる場面。",
     "why_ja": "Madame(別Voice)。感情の明記が無い台詞が、文脈追加で『過剰に感情的』にならないかの対照。直前のDellaの問いへの返答。"},
    {"id": "full_story_part2_c5", "categories": ["ためらい・戸惑い", "感情が変化する場面", "相手の発言を受けた返答"],
     "scene_ja": "金額を聞いたDellaが、迷う前に決めてしまおうと、すぐ切ってほしいと頼む場面。",
     "why_ja": "ためらいを振り切る決意。直前の金額提示への返答。"},
    {"id": "full_story_part2_c7", "categories": ["ささやき・静かな発言", "悲しみ・不安"],
     "scene_ja": "髪を売って贈り物の鎖を買い、帰宅。短くなった髪を気にして鏡に戻りながら、Jimが帰る前に小さく祈る場面(直後の地の文に『ささやいた』)。",
     "why_ja": "先行調査(INVESTIGATION_01)で、ささやきの演出が地の文(別clip・別Voice)にあるため反映されない可能性が指摘された代表例。"},
    {"id": "full_story_part3_c2", "categories": ["感情が変化する場面", "悲しみ・不安", "喜び・驚き"],
     "scene_ja": "帰ってきたJimが短い髪を見て立ち尽くす。Dellaは駆け寄り、髪を売った理由を打ち明ける場面。",
     "why_ja": "1セリフ内で動揺→必死の説明→前向きな一言(It'll grow again!)と感情が動く最長のセリフ。"},
    {"id": "full_story_part3_c4", "categories": ["悲しみ・不安", "喜び・驚き", "感情が変化する場面"],
     "scene_ja": "Jimから贈られたのは、ずっと欲しかった櫛。髪を売った今は使えない櫛を胸に抱き、涙ながらに微笑んで言う場面(直前の地の文に『smiling through tears』)。",
     "why_ja": "セリフ本文に感情語が無い短文(事実陳述)。涙ながらの笑顔という感情が地の文にしか無い、文脈の効果が最も出やすい例。"},
    {"id": "full_story_part3_c6", "categories": ["喜び・驚き"],
     "scene_ja": "気を取り直したDellaが、Jimのために買った時計の鎖を見せ、時計を貸してほしいと言う場面。",
     "why_ja": "喜び・高揚。『Look!』『Isn't it perfect?』と感情語が本文にもあり、文脈追加が過剰にならないかの確認にもなる。"},
    {"id": "full_story_part3_c8", "categories": ["ささやき・静かな発言", "ためらい・戸惑い", "相手の発言を受けた返答"],
     "scene_ja": "Jimが腰を下ろして穏やかに微笑み、Dellaの『時計を貸して』に応えて、櫛を買うために時計を売ったと静かに告げる場面。",
     "why_ja": "Jim(男声・別Voice)の静かな告白。直前のDellaの発言への返答で、穏やかな微笑みという演出が地の文にある。"},
]
TARGET_IDS = [t["id"] for t in TARGETS]

# 決定論の演出語抽出に使う語彙(話し方・表情・動作の手掛かり。原文の逐語を抜く目印であって、感情語を創作するものではない)
STAGE_LEXICON = re.compile(
    r"(whisper\w*|softly|gently|quietly|loudly|smil\w+|tears?|cried|cry|laugh\w*|shout\w*|tremb\w*|nervous\w*|sigh\w*|"
    r"rushed|hurried|breath|shut her eyes|stopped|stared|eyes stayed|kept returning|paused|suddenly)", re.I)
NEIGHBOR_MAX_CLIP_DISTANCE = 4     # この距離(clip数)を超えるセリフは文脈に入れない(場面が離れている)
TIMESKIP_NARRATION_WORDS = 40      # 間の地の文がこれを超える語数なら時間経過とみなし、そのセリフは文脈に入れない
PREV_DIALOGUE_MAX = 2
NEXT_DIALOGUE_MAX = 1
NARRATION_SENTENCES = 2


# ============================================================
# 共通
# ============================================================
def load_json(path: str):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    ap = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha_file(path: str):
    ap = os.path.join(ROOT, path)
    if not os.path.isfile(ap):
        return None
    h = hashlib.sha256()
    with open(ap, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def now_jst() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def load_plan() -> dict:
    return load_json(PLAN_PATH)


def voice_map() -> dict:
    """speaker key -> TTS Voice名。正本=Production Zの voice_assignment.json(2026-10-23 APPROVED_FOR_PRODUCTION)。segment_planのclip['voice']は話者keyでVoice名ではない。"""
    va = load_json(f"{SRC_RUN}/voice_assignment.json")
    return {sp["speaker"]: sp["voice"] for sp in va["speakers"]}


def tts_voice(clip: dict) -> str:
    return voice_map()[clip["speaker"]]


def clip_index(plan: dict) -> dict:
    return {c["id"]: i for i, c in enumerate(plan["clips"])}


def split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def n_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'’\-]+", text))


def norm_for_match(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def norm_tokens(s: str) -> list:
    return re.findall(r"[a-z0-9']+", norm_for_match(s))


# ============================================================
# 文脈の決定論抽出(LLM不使用。segment_planのみから作る)
# ============================================================
def extract_context(plan: dict, clip_id: str) -> dict:
    clips = plan["clips"]
    idx = clip_index(plan)[clip_id]
    c = clips[idx]
    is_dialogue = lambda x: str(x.get("voice_role", "")).startswith("dialogue:")  # noqa: E731

    def between_narration_words(i, j):
        lo, hi = sorted((i, j))
        return sum(n_words(clips[k]["text"]) for k in range(lo + 1, hi) if not is_dialogue(clips[k]))

    prev_d, k = [], idx - 1
    while k >= 0 and len(prev_d) < PREV_DIALOGUE_MAX and idx - k <= NEIGHBOR_MAX_CLIP_DISTANCE:
        if is_dialogue(clips[k]) and between_narration_words(k, idx) <= TIMESKIP_NARRATION_WORDS:
            prev_d.append(k)
        k -= 1
    prev_d.reverse()
    next_d, k = [], idx + 1
    while k < len(clips) and len(next_d) < NEXT_DIALOGUE_MAX and k - idx <= NEIGHBOR_MAX_CLIP_DISTANCE:
        if is_dialogue(clips[k]) and between_narration_words(idx, k) <= TIMESKIP_NARRATION_WORDS:
            next_d.append(k)
        k += 1

    def d_item(i):
        x = clips[i]
        return {"clip_id": x["id"], "speaker": x["speaker"], "speaker_display": SPEAKER_DISPLAY.get(x["speaker"], x["speaker"]), "text": x["text"]}

    narr_before = narr_after = ""
    if idx - 1 >= 0 and not is_dialogue(clips[idx - 1]):
        narr_before = " ".join(split_sentences(clips[idx - 1]["text"])[-NARRATION_SENTENCES:])
    if idx + 1 < len(clips) and not is_dialogue(clips[idx + 1]):
        narr_after = " ".join(split_sentences(clips[idx + 1]["text"])[:NARRATION_SENTENCES])
    stage = []
    for piece in (narr_before, narr_after):
        for s in split_sentences(piece):
            if STAGE_LEXICON.search(s) and s not in stage:
                stage.append(s)
    manner = sorted({m.group(0).lower() for s in stage for m in STAGE_LEXICON.finditer(s)})
    return {
        "clip_id": clip_id, "speaker": c["speaker"], "speaker_display": SPEAKER_DISPLAY.get(c["speaker"], c["speaker"]),
        "voice": tts_voice(c), "text": c["text"], "part": c.get("part"),
        "prev_dialogue": [d_item(i) for i in prev_d], "next_dialogue": [d_item(i) for i in next_d],
        "narration_before": narr_before, "narration_after": narr_after,
        "stage_direction_sentences": stage, "manner_words": manner,
    }


def allowed_source_text(ctx: dict) -> str:
    """感情情報の『根拠引用』が逐語一致すべき範囲(この文脈に含まれる原文のみ)。"""
    parts = [ctx["text"]] + [d["text"] for d in ctx["prev_dialogue"] + ctx["next_dialogue"]]
    parts += [ctx["narration_before"], ctx["narration_after"]] + list(ctx["stage_direction_sentences"])
    return "\n".join(p for p in parts if p)


# ============================================================
# 感情・心理状態の作成(LLM 1 call、全対象一括)と創作防止検査
# ============================================================
EMOTION_FALLBACK_STATE = "No strong emotion is stated for this line in the story, so deliver it plainly and naturally."

EMOTION_DEVELOPER = (
    "You prepare short, faithful delivery notes for an audiobook reader performing one spoken line of a classic story (The Gift of the Magi). "
    "For each line you receive: the line, the speaker, nearby spoken lines, and the narration right before or after it.\n"
    "Rules:\n"
    "1. Use ONLY what the provided text states or clearly implies. Do not invent backstory, emotions, gestures, or acting that the text does not support.\n"
    "2. speaker_state: 1-2 short sentences (max 30 words) in English describing the speaker's feeling or state of mind at the moment of this line, "
    "written in plain, restrained words (no theatrical adjectives).\n"
    "3. scene: ONE sentence (max 25 words) saying where/when the line is spoken and what is happening, from the provided text only.\n"
    "4. reaction_to_previous: ONE sentence (max 25 words) saying how the line responds to the previous spoken line, or an empty string if it does not respond to one.\n"
    "5. evidence: 1-3 quotes copied EXACTLY (character for character) from the provided text that support your speaker_state. "
    "Quote only text that appears in that line's own fields (the line, nearby lines, narration). No paraphrase.\n"
    "6. If the text states no emotion or manner for a line, set has_explicit_cue=false and write a plain neutral speaker_state; do not guess an emotion.\n"
    "7. Do not add person names or places that are not in the provided text. Return JSON only.")

EMOTION_SCHEMA = {
    "name": "dialogue_delivery_notes", "strict": True,
    "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["clip_id", "speaker_state", "scene", "reaction_to_previous", "evidence", "has_explicit_cue"],
        "properties": {"clip_id": {"type": "string"}, "speaker_state": {"type": "string"}, "scene": {"type": "string"},
                       "reaction_to_previous": {"type": "string"}, "evidence": {"type": "array", "items": {"type": "string"}},
                       "has_explicit_cue": {"type": "boolean"}}}}}}}


def emotion_user_message(contexts: list) -> str:
    rows = []
    for c in contexts:
        rows.append({"clip_id": c["clip_id"], "speaker": c["speaker_display"], "line": c["text"],
                     "previous_spoken_lines": [{"speaker": d["speaker_display"], "text": d["text"]} for d in c["prev_dialogue"]],
                     "next_spoken_line": [{"speaker": d["speaker_display"], "text": d["text"]} for d in c["next_dialogue"]],
                     "narration_before": c["narration_before"], "narration_after": c["narration_after"]})
    return "Prepare delivery notes for each line below.\n" + json.dumps(rows, ensure_ascii=False, indent=1)


def emotion_prompt_sha() -> str:
    return sha_text(EMOTION_DEVELOPER + "\n" + json.dumps(EMOTION_SCHEMA, sort_keys=True))


def validate_emotion_items(raw_items: list, contexts: list) -> dict:
    """LLM出力の創作防止検査(決定論)。根拠引用が当該文脈の原文に逐語一致しない/語数超過/新規固有名詞を含む項目は破棄し、
    中立のfallbackへ置換する。戻り値 {clip_id: {"state","scene","reaction","evidence","status","discard_reasons"}}。"""
    by_id = {it.get("clip_id"): it for it in (raw_items or []) if isinstance(it, dict)}
    out = {}
    for ctx in contexts:
        cid = ctx["clip_id"]
        it = by_id.get(cid)
        src = allowed_source_text(ctx)
        src_n = norm_for_match(src)
        src_tokens = set(norm_tokens(src)) | {"della", "jim", "christmas"}
        reasons = []
        if it is None:
            reasons.append("missing_item")
            it = {}
        state, scene, reaction = str(it.get("speaker_state", "")).strip(), str(it.get("scene", "")).strip(), str(it.get("reaction_to_previous", "")).strip()
        ev = [str(e).strip() for e in (it.get("evidence") or []) if str(e).strip()]
        cue = bool(it.get("has_explicit_cue"))
        if cue:
            if not ev:
                reasons.append("no_evidence")
            for e in ev:
                if norm_for_match(e).strip(" .,!?\"'") not in src_n:
                    reasons.append(f"evidence_not_verbatim:{e[:40]}")
        if n_words(state) > 32:
            reasons.append("state_too_long")
        if n_words(scene) > 27:
            reasons.append("scene_too_long")
        if n_words(reaction) > 27:
            reasons.append("reaction_too_long")
        # 創作防止: 新規の固有名詞(文頭以外の大文字語で、文脈原文に無いもの)を含めない
        for field_name, val in (("state", state), ("scene", scene), ("reaction", reaction)):
            for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z]+)", val):
                if m.group(1).lower() not in src_tokens:
                    reasons.append(f"new_proper_noun:{field_name}:{m.group(1)}")
        if reasons or not cue:
            # 根拠なし・不正 -> 感情は中立fallback。scene/reactionは根拠検査を通らなかった場合のみ破棄(has_explicit_cue=falseだけなら場面は保持)
            if reasons:
                out[cid] = {"state": EMOTION_FALLBACK_STATE, "scene": "", "reaction": "", "evidence": [], "status": "DISCARDED", "discard_reasons": reasons}
            else:
                out[cid] = {"state": EMOTION_FALLBACK_STATE, "scene": scene, "reaction": reaction, "evidence": ev, "status": "NO_EXPLICIT_CUE", "discard_reasons": []}
        else:
            out[cid] = {"state": state, "scene": scene, "reaction": reaction, "evidence": ev, "status": "ACCEPTED", "discard_reasons": []}
    return out


# ============================================================
# Style構成(①=既存汎用style無変更 / ②=①と同一文字列 + CONTEXTブロック追記のみ)
# ============================================================
CONTEXT_HEAD = ("CONTEXT FOR THIS ONE LINE (delivery reference only. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. "
                "Only the TEXT TO SPEAK section is spoken.)")
CONTEXT_TAIL = ("Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. "
                "Keep the delivery natural and believable: let the feeling described above come through in the voice, "
                "without theatrical over-acting and without adding any emotion beyond what is described. "
                "Do not read any word of this CONTEXT block.")


def base_style() -> str:
    import er003_b1_p9a_audio as p9a
    return p9a.ENGLISH_STYLE_PREFIX


def build_context_block(ctx: dict, note: dict | None) -> str:
    """CONTEXTブロック本文。noteは validate_emotion_items の1件(None=感情情報なし=決定論の項目のみ)。"""
    lines = [CONTEXT_HEAD, f"Speaker of this line: {ctx['speaker_display']}."]
    if note and note.get("state"):
        lines.append(f"Speaker's state of mind: {note['state']}")
    if note and note.get("scene"):
        lines.append(f"Scene: {note['scene']}")
    for d in ctx["prev_dialogue"]:
        lines.append(f'Spoken line before: {d["speaker_display"]}: "{_unq(d["text"])}"')
    if ctx["narration_before"]:
        lines.append(f'Narration just before: "{ctx["narration_before"]}"')
    for d in ctx["next_dialogue"]:
        lines.append(f'Spoken line after: {d["speaker_display"]}: "{_unq(d["text"])}"')
    if ctx["narration_after"]:
        lines.append(f'Narration just after: "{ctx["narration_after"]}"')
    if ctx["stage_direction_sentences"]:
        lines.append("Stage direction in the story (manner of speaking or acting): " + " / ".join(f'"{s}"' for s in ctx["stage_direction_sentences"]))
    if note and note.get("reaction"):
        lines.append(f"How this line answers the previous one: {note['reaction']}")
    lines.append(CONTEXT_TAIL)
    return "\n".join(lines)


def _unq(t: str) -> str:
    return t.strip().strip('"“”')


def style_for_arm(arm: str, ctx: dict | None, note: dict | None) -> str:
    """arm='base'(①と同一のProduction既定style) / 'ctx'(②)。①②の差は CONTEXTブロックの追記のみ。"""
    b = base_style()
    if arm == "base":
        return b
    if arm == "ctx":
        return b.rstrip() + "\n\n" + build_context_block(ctx, note)
    raise ValueError(arm)


def build_prompt(text: str, style: str) -> str:
    import er003_b1_p4c_audio as p4c
    return p4c.build_tts_prompt(text, style)


def tts_text_for(clip: dict) -> str:
    """Production Zと同一の本文整形(_norm_for_tts)。"""
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec(clip_id=clip["id"], level=LEVEL, kind="dialogue", text=clip["text"], voice=tts_voice(clip), speaker=clip["speaker"],
                      role_key="DIALOGUE_ADV", part=clip.get("part"))
    return z._norm_for_tts(spec)


# ============================================================
# 再利用分離
# ============================================================
def trial_reuse_key(clip: dict, arm: str, style: str, take: int) -> dict:
    """本Trial専用の出力識別key。Production build_reuse_key(er063:798)はdialogueでstyle hashを含まない(style_text_for=None)ため、
    本Trialでは style_sha256 / arm / take / Trial IDを必ず含める。Production reuse関数には渡さない。"""
    return {"managed_id": MANAGED_ID, "arm": arm, "take": take, "canonical_text_sha256": sha_text(clip["text"]), "voice": tts_voice(clip),
            "model": TTS_MODEL, "style_sha256": sha_text(style), "tts_backend_note": "gemini_standard_sync(Production Z実行と同じSTANDARD)"}


def production_reuse_key_for(clip: dict) -> dict:
    """Productionのreuse_key(読み取り再構成。呼び出すだけでI/Oなし)。②と①で同一になる=分離不能であることの証明用。"""
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec(clip_id=clip["id"], level=LEVEL, kind="dialogue", text=clip["text"], voice=tts_voice(clip), speaker=clip["speaker"], role_key="DIALOGUE_ADV")
    return z.build_reuse_key(spec)


# ============================================================
# ①既存音声(読み取りのみ)
# ============================================================
def existing_audio_record(clip_id: str) -> dict:
    res = load_json(TTS_RESULTS_PATH)["segments"][clip_id]
    orig = f"{NARR_DIR}/{clip_id}_original.wav"
    att = load_json(f"{NARR_DIR}/attempts/{clip_id}_attempt1_englishstyleprefixwidemargin.json")
    return {"clip_id": clip_id, "original_wav": orig, "original_sha256": sha_file(orig), "attempt_json_sha256_field": att.get("sha256"),
            "original_matches_attempt_sha": sha_file(orig) == att.get("sha256"),
            "final_wav": res.get("path"), "final_sha256": res.get("sha256"), "voice": res.get("voice"),
            "asr_text": res.get("asr_text"), "audio_classification": (res.get("attempts") or [{}])[-1].get("audio_classification"),
            "asr_state": (res.get("asr_judgement") or {}).get("state"), "asr_primary_label": ((res.get("asr_judgement") or {}).get("primary") or {}).get("label"), "speed_profile": (res.get("speed_profile") or {}).get("profile"),
            "tempo": (res.get("speed_profile") or {}).get("tempo"), "tts_model_id": (res.get("attempts") or [{}])[-1].get("tts_model_id"),
            "tts_execution_mode": att.get("tts_execution_mode"), "attempts": len(res.get("attempts") or []),
            "style_effective_sha256": (res.get("style") or {}).get("effective_style_prefix_sha256"),
            "reuse_key_style_prefix_sha256": (res.get("reuse_key") or {}).get("style_prefix_sha256")}


# ============================================================
# 計測(API 0、ローカル)
# ============================================================
def read_mono(path: str):
    import soundfile as sf
    x, sr = sf.read(os.path.join(ROOT, path), dtype="float64")
    return (x if x.ndim == 1 else x[:, 0]), sr


def rms_dbfs(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    return round(20 * np.log10(max(r, 1e-9)), 2)


def f0_stats(x: np.ndarray, sr: int, fmin: float = 70.0, fmax: float = 400.0) -> dict:
    """簡易自己相関F0(有声フレームのみ)。粗い指標で、感情の自然さの代替ではない(聴感はユーザー試聴)。"""
    fl, hop = int(0.040 * sr), int(0.010 * sr)
    gate = 0.1 * float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    lo, hi = int(sr / fmax), int(sr / fmin)
    f0s = []
    for s in range(0, max(0, len(x) - fl), hop):
        fr = x[s:s + fl] - np.mean(x[s:s + fl])
        if float(np.sqrt(np.mean(fr ** 2))) < max(gate, 1e-4):
            continue
        ac = np.correlate(fr, fr, mode="full")[fl - 1:]
        if ac[0] <= 0:
            continue
        seg = ac[lo:hi]
        if len(seg) == 0:
            continue
        k = int(np.argmax(seg)) + lo
        if ac[k] / ac[0] > 0.45:
            f0s.append(sr / k)
    if len(f0s) < 5:
        return {"n_voiced": len(f0s), "median_hz": None, "range_semitones_p10_p90": None}
    a = np.array(f0s)
    p10, p90 = np.percentile(a, [10, 90])
    return {"n_voiced": len(f0s), "median_hz": round(float(np.median(a)), 1), "range_semitones_p10_p90": round(float(12 * np.log2(p90 / p10)), 2)}


def analyze_wav(path: str, words: int) -> dict:
    import er113_fx_paragraph_chunk_trial_01 as t113
    x, sr = read_mono(path)
    m = t113.measure_wav(x, sr, words)
    return {"duration_s": m["duration_s"], "words": words, "total_wpm": m["total_wpm"], "articulation_wpm_300": m["articulation_wpm_300"],
            "mid_pause_300": m["pause_300"]["n_mid"], "max_mid_pause_s": m["pause_300"]["max_mid_s"],
            "rms_dbfs": rms_dbfs(x), "peak": round(float(np.max(np.abs(x))), 4), "f0": f0_stats(x, sr)}


def leakage_check(asr_text: str, ctx: dict, note: dict | None) -> dict:
    """CONTEXT内の文言が音声に混入していないかの検査(ASR転写に対する決定論検査)。Production ASR検査(長さ<=本文+15字)は小さな混入を通すため別途行う。
    1) 本文語数+許容を超える語 2) CONTEXT専用語(本文に無い)の出現 3) CONTEXT文字列との3語連続一致(本文内の連続一致は除く)。"""
    target_tokens = norm_tokens(ctx["text"])
    asr_tokens = norm_tokens(asr_text or "")
    ctx_block = build_context_block(ctx, note)
    # CONTEXT専用語 = CONTEXT文に出現し、本文に出現しない語のうち、手順語・見出し語に限定した集合(一般語の偶然一致を避ける)
    marker_words = {"context", "stage", "direction", "narration", "speaker", "scene", "state", "spoken", "reference", "block", "delivery", "audiobook", "theatrical"}
    extra_markers = sorted(w for w in set(asr_tokens) if w in marker_words and w not in set(target_tokens))
    ngram = []
    ctx_tokens = norm_tokens(ctx_block.split("\n", 1)[1] if "\n" in ctx_block else ctx_block)
    tgt_str = " ".join(target_tokens)
    for n in (3, 4, 5):
        for i in range(len(asr_tokens) - n + 1):
            g = " ".join(asr_tokens[i:i + n])
            if g in tgt_str:
                continue
            if g in " ".join(ctx_tokens):
                ngram.append(g)
    surplus = max(0, len(asr_tokens) - len(target_tokens))
    flagged = bool(extra_markers or ngram or surplus > 3)
    return {"flagged": flagged, "extra_marker_words": extra_markers, "context_ngrams": sorted(set(ngram))[:8], "surplus_words": surplus,
            "asr_words": len(asr_tokens), "target_words": len(target_tokens)}


def verbatim_check(asr_text: str, canonical_text: str) -> dict:
    a, b = norm_tokens(asr_text or ""), norm_tokens(canonical_text)
    import difflib
    r = difflib.SequenceMatcher(None, a, b).ratio()
    return {"token_equal": a == b, "token_similarity": round(r, 4)}


# ============================================================
# 費用見積(API 0)
# ============================================================
USD_JPY = 160.0                 # er113/既存runnerと同一
TTS_PRO_IN_USD_PER_M = 1.0      # gemini-2.5-pro-preview-tts Standard input (pricing_snapshot.json)
TTS_PRO_OUT_USD_PER_M = 20.0    # 同 output (audio 25 tokens/sec)
ASR_IN_USD_PER_M = 1.25
ASR_OUT_USD_PER_M = 5.0


def est_tts_jpy(prompt_chars: int, audio_s: float) -> float:
    in_tok = prompt_chars / 4.5
    return (in_tok * TTS_PRO_IN_USD_PER_M + audio_s * 25 * TTS_PRO_OUT_USD_PER_M) / 1e6 * USD_JPY


def est_asr_jpy(n: int) -> float:
    return n * (530 * ASR_IN_USD_PER_M + 180 * ASR_OUT_USD_PER_M) / 1e6 * USD_JPY


# ============================================================
# Phase 0: plan(API 0)
# ============================================================
def build_phase0_artifacts() -> dict:
    plan = load_plan()
    cl = {c["id"]: c for c in plan["clips"]}
    contexts = [extract_context(plan, t["id"]) for t in TARGETS]
    sel = []
    est_rows = []
    for t, ctx in zip(TARGETS, contexts):
        rec = existing_audio_record(t["id"])
        clip = cl[t["id"]]
        x, sr = read_mono(rec["original_wav"])
        dur = len(x) / sr
        meas = analyze_wav(rec["original_wav"], n_words(clip["text"]))
        base_prompt = build_prompt(tts_text_for(clip), style_for_arm("base", ctx, None))
        ctx_prompt = build_prompt(tts_text_for(clip), style_for_arm("ctx", ctx, None))  # noteなし=決定論部のみ(感情欄はPhase 1のLLM後に入る)
        est_rows.append({"clip_id": t["id"], "audio_s": round(dur, 2), "base_prompt_chars": len(base_prompt), "ctx_prompt_chars_deterministic_only": len(ctx_prompt),
                         "tts_ctx_est_jpy": round(est_tts_jpy(len(ctx_prompt) + 350, dur * 1.05), 3),
                         "tts_base_est_jpy": round(est_tts_jpy(len(base_prompt), dur), 3)})
        sel.append({**t, "speaker": clip["speaker"], "voice": tts_voice(clip), "text": clip["text"], "context": ctx, "existing_audio": rec, "existing_measure": meas,
                    "production_reuse_key": production_reuse_key_for(clip)})
    save_json(f"{OUT_DIR}/phase0/selection.json", sel)
    ctx_ex = contexts[3]
    save_json(f"{OUT_DIR}/phase0/style_example_part2_c7.json", {
        "note": "Phase 0 例示。speaker_state/scene/reactionはPhase 1のLLM(gpt-6-luna 1 call)出力が入る欄で、ここでは『<LLM>』のプレースホルダ。",
        "context_block_with_placeholders": build_context_block(ctx_ex, {"state": "<LLM: speaker_state>", "scene": "<LLM: scene>", "reaction": ""}),
        "base_style_sha256": sha_text(base_style())})
    return {"selection": sel, "estimates": est_rows}


# ============================================================
# TTSリクエスト捕捉(Productionが保存しない実送信prompt・config・modeを残す)
# ============================================================
@contextlib.contextmanager
def capture_tts_requests(log: list, label_fn=lambda: None):
    import er006_batch_tts_wiring_01 as bw
    import er002_gemini_client as gclient
    orig = bw.make_batch_tts_call_fn
    prev_env = os.environ.get(bw.TTS_EXECUTION_MODE_ENV_VAR)
    os.environ[bw.TTS_EXECUTION_MODE_ENV_VAR] = "STANDARD"   # Z既存実行(tts_execution_mode=STANDARD)と同一。Trial processのみ・終了時に復元

    def factory(model_name, voice_name, *a, **kw):
        inner = orig(model_name, voice_name, *a, **kw)
        sc = gclient.build_speech_config(voice_name)

        def call(prompt):
            log.append({"label": label_fn(), "ts": now_jst(), "model": model_name, "voice": voice_name, "tts_execution_mode": bw.resolve_tts_execution_mode(),
                        "speech_config": sc.model_dump() if hasattr(sc, "model_dump") else str(sc), "response_modalities": ["AUDIO"],
                        "temperature": None, "temperature_note": "未指定(SDK/モデル既定)。Production Z実行と同一コード経路 er003_b1_p7a_audio.make_tts_call_fn_for_model",
                        "http_timeout_ms": gclient.TTS_TIMEOUT_MS, "prompt_sha256": sha_text(prompt), "prompt_chars": len(prompt), "prompt": prompt})
            return inner(prompt)
        return call
    bw.make_batch_tts_call_fn = factory
    try:
        yield
    finally:
        bw.make_batch_tts_call_fn = orig
        if prev_env is None:
            os.environ.pop(bw.TTS_EXECUTION_MODE_ENV_VAR, None)
        else:
            os.environ[bw.TTS_EXECUTION_MODE_ENV_VAR] = prev_env


# ============================================================
# Phase 1: 実行ガード
# ============================================================
def _require_go() -> dict:
    ap = os.path.join(ROOT, PHASE1_GO_FILE)
    if not os.path.exists(ap):
        raise SystemExit(f"[STOP] {PHASE1_GO_FILE} が無い。Phase 1(有料)はOpusレビュー後のFable Goまで開始禁止。")
    go = load_json(PHASE1_GO_FILE)
    if go.get("managed_id") != MANAGED_ID or not go.get("cap_jpy") or float(go["cap_jpy"]) > TRIAL_CAP_JPY:
        raise SystemExit(f"[STOP] PHASE1_GO.json の managed_id / cap_jpy 不正(cap上限{TRIAL_CAP_JPY}円)")
    return go


def _stop_check() -> None:
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", OUT_DIR,
                        "--out", f"{OUT_DIR}/stop_check.json"], cwd=ROOT)
    if r.returncode == 3:
        raise SystemExit("[STOP] stop_scope_check rc=3")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check 異常 rc={r.returncode}")


def protected_paths() -> list:
    ps = [TTS_RESULTS_PATH, PLAN_PATH]
    for cid in TARGET_IDS:
        ps += [f"{NARR_DIR}/{cid}_original.wav", f"{NARR_DIR}/{cid}.wav"]
    return ps


def snapshot_protected() -> dict:
    import er113_fx_paragraph_chunk_trial_01 as t113
    snap = {p: sha_file(p) for p in protected_paths()}
    snap.update(t113.snapshot_protected())
    return snap


def run_emotion_llm(client=None, *, out_dir: str = f"{OUT_DIR}/llm") -> dict:
    """Phase 1専用。全対象を1 callで。結果と生応答・検査結果を保存。GO無しでは起動しない。"""
    go = _require_go()
    _stop_check()
    plan = load_plan()
    contexts = [extract_context(plan, t["id"]) for t in TARGETS]
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        import er005_cost_logger as cl
        cl.install(os.path.join(ROOT, f"{OUT_DIR}/raw_usage_log.jsonl"))
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
    import er062_family_z_writer_01 as zw
    msgs = [{"role": "developer", "content": EMOTION_DEVELOPER}, {"role": "user", "content": emotion_user_message(contexts)}]
    kw = {"model": LLM_MODEL, "reasoning": {"effort": "low"}, "input": msgs, "text": {"format": {"type": "json_schema", **EMOTION_SCHEMA}}}
    r = client.responses.create(**kw)
    cost = zw.cost_jpy(LLM_MODEL, r.usage)
    if not str(r.model).startswith(LLM_MODEL):
        raise SystemExit(f"[STOP] 返却modelが{LLM_MODEL}で始まらない: {r.model}")
    raw = json.loads(r.output_text)
    checked = validate_emotion_items(raw.get("items"), contexts)
    rec = {"managed_id": MANAGED_ID, "model_requested": LLM_MODEL, "model_returned": str(r.model), "cost_jpy": round(cost, 4),
           "prompt_sha256": emotion_prompt_sha(), "user_message_sha256": sha_text(msgs[1]["content"]), "raw_output": raw, "validated": checked,
           "n_accepted": sum(1 for v in checked.values() if v["status"] == "ACCEPTED"),
           "n_discarded": sum(1 for v in checked.values() if v["status"] == "DISCARDED"),
           "n_no_explicit_cue": sum(1 for v in checked.values() if v["status"] == "NO_EXPLICIT_CUE"), "saved_at": now_jst()}
    save_json(f"{out_dir}/emotion_notes.json", rec)
    return rec


def generate_arm(arm: str, take: int, *, gen_fn=None, only: list | None = None, go: dict | None = None) -> dict:
    """arm='ctx'(②) / 'base'(対照: ①と同一styleの新規take。take間のばらつきの切り分け用)。1セリフ=1 TTS call(retryはProduction既定の通算3回まで)。
    gen_fn: test用injection(本番はNone=Production bvoices.generate_voice_body_wide_margin。このときだけ GO・STOP確認・sink隔離・Zscopeを適用)。"""
    live = gen_fn is None
    if live:
        go = _require_go()
        if arm not in go.get("arms", []):
            raise SystemExit(f"[STOP] arm={arm} はPHASE1_GO.jsonで許可されていない(許可={go.get('arms')})")
        _stop_check()
    cap = float(go["cap_jpy"]) if go else 1e9
    plan = load_plan()
    cl_map = {c["id"]: c for c in plan["clips"]}
    notes = {}
    if arm == "ctx":
        npath = f"{OUT_DIR}/llm/emotion_notes.json"
        if not os.path.exists(os.path.join(ROOT, npath)):
            raise SystemExit("[STOP] ctx armには emotion_notes.json(Phase 1のLLM出力)が必要")
        notes = load_json(npath)["validated"]
    arm_dir = f"{OUT_DIR}/gen/{arm}_t{take}"
    results, reqs, current = {}, [], {"label": None}
    before = None

    def _run(_dir=None):
        runner = None
        if live:
            import er019_family_x_audio_production_runner_01 as runner
        for t in TARGETS:
            cid = t["id"]
            if only and cid not in only:
                continue
            if runner is not None:
                spent, _ = runner.compute_cost_jpy_so_far(os.path.join(ROOT, f"{OUT_DIR}/raw_usage_log.jsonl"))
                if spent >= cap:
                    raise SystemExit(f"[STOP] 個別Cap {cap}円到達(実績{spent:.2f}円)")
            clip = cl_map[cid]
            ctx = extract_context(plan, cid)
            style = style_for_arm(arm, ctx, notes.get(cid) if arm == "ctx" else None)
            text = tts_text_for(clip)
            prompt_expected = build_prompt(text, style)
            wav = f"{arm_dir}/{cid}/{LEVEL}/narration/{cid}.wav"
            os.makedirs(os.path.dirname(os.path.join(ROOT, wav)), exist_ok=True)
            current["label"] = f"{arm}_t{take}:{cid}"
            n_before = len(reqs)
            t0 = time.time()
            res = gen_fn(text, os.path.join(ROOT, wav), tts_voice(clip), style_prefix_override=(None if arm == "base" else style)) or {}
            sent = reqs[n_before:]
            rec = {"clip_id": cid, "arm": arm, "take": take, "status": res.get("status"), "wav": wav, "wav_sha256": sha_file(wav),
                   "voice": tts_voice(clip), "tts_text": text, "style_sha256": sha_text(style), "prompt_expected_sha256": sha_text(prompt_expected),
                   "requests_sent": [{k: v for k, v in q.items() if k != "prompt"} for q in sent],
                   "request_prompt_matches_expected": [q["prompt_sha256"] == sha_text(prompt_expected) for q in sent],
                   "n_tts_calls": len(sent), "asr_text": res.get("asr_text"), "audio_classification": res.get("audio_classification"),
                   "asr_judgement": res.get("asr_judgement"), "attempts_log_n": len(res.get("attempts_log") or []),
                   "instruction_type": res.get("instruction_type"), "repetition_qa_checked": res.get("repetition_qa_checked"),
                   "trim_info": res.get("trim_info"), "reuse_key_trial": trial_reuse_key(clip, arm, style, take),
                   "elapsed_s": round(time.time() - t0, 2), "saved_at": now_jst()}
            save_json(f"{arm_dir}/{cid}/request_full.json", {"clip_id": cid, "arm": arm, "take": take, "requests": sent})
            if res.get("status") != "OK":
                rec["fail_reason"] = res.get("reason")
            save_json(f"{arm_dir}/{cid}/result.json", rec)
            results[cid] = rec
            if res.get("status") != "OK":
                break   # 自動再実行しない。Fableへ報告

    with contextlib.ExitStack() as stack:
        if live:
            import er012_b_family_voices_production_01 as bvoices
            import er005_cost_logger as cl_mod
            import er078_secondary_run_scope_01 as secondary_run_scope
            import er109_xz_scope_01 as er109_scope
            import er113_fx_paragraph_chunk_trial_01 as t113
            from dotenv import load_dotenv
            load_dotenv()
            cl_mod.install(os.path.join(ROOT, f"{OUT_DIR}/raw_usage_log.jsonl"))
            gen_fn = bvoices.generate_voice_body_wide_margin
            before = snapshot_protected()
            stack.enter_context(t113.redirect_production_sinks(f"{OUT_DIR}/sinks"))
            stack.enter_context(capture_tts_requests(reqs, lambda: current["label"]))
            secondary_run_scope.with_secondary_run(er109_scope.family_scope("Z")(_run))(arm_dir)
        else:
            _run()
    summary = {"arm": arm, "take": take, "results": {k: {"status": v["status"], "n_tts_calls": v["n_tts_calls"]} for k, v in results.items()}}
    if live:
        after = snapshot_protected()
        diff = [k for k in before if before[k] != after.get(k)]
        summary["protected_diff"] = diff
        if diff:
            summary["STOP"] = "protected store/Production音声が変化した"
    save_json(f"{arm_dir}/summary.json", summary)
    return results


# ============================================================
# 解析(API 0) と 試聴ページ
# ============================================================
def target_rms_for_listening() -> float:
    """試聴用の統一RMS = Magi Advの実組立が使ったtarget_rms(timeline.json gain_report)。①②とも同一方式(p9a.compute_gain_for_target_rms, max_peak=0.95)で個別gain。"""
    return float(load_json(f"{SRC_RUN}/{LEVEL}/assembly/timeline.json")["gain_report"]["target_rms"])


def export_mp3(wav_rel: str, mp3_rel: str, target_rms: float) -> dict:
    import er003_b1_p9a_audio as p9a
    import imageio_ffmpeg
    import soundfile as sf
    x, sr = read_mono(wav_rel)
    g = p9a.compute_gain_for_target_rms(x, target_rms)
    y = x * g
    ap = os.path.join(ROOT, mp3_rel)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    tmp = ap + ".tmp.wav"
    sf.write(tmp, y.astype("float32"), sr)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "96k", ap], check=True)
    os.remove(tmp)
    return {"gain": round(float(g), 4), "rms_after_dbfs": rms_dbfs(y), "peak_after": round(float(np.max(np.abs(y))), 4)}


_PAGE_CSS = """body{font-family:sans-serif;max-width:980px;margin:16px auto;padding:0 12px;color:#222}
h1{font-size:1.25rem}.note{background:#fff8e1;border:1px solid #e6c200;padding:8px 12px;border-radius:6px;font-size:.9rem}
.card{border:1px solid #ccc;border-radius:8px;padding:10px 14px;margin:14px 0}.card h2{font-size:1rem;margin:0 0 4px}
.scene{color:#444;font-size:.92rem;margin:4px 0}.en{font-size:1.05rem;font-weight:bold;margin:6px 0}
.row{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px}.col{flex:1;min-width:260px}.lab{font-size:.85rem;color:#555}
.na{color:#a00;font-size:.85rem}details{margin:6px 0;font-size:.88rem}audio{width:100%}"""


def build_page(sel: list, arms: dict, out_dir: str = PAGE_DIR, extra: dict | None = None) -> str:
    """arms: {"base": {clip_id: mp3_relpath_from_page}, "ctx": {...}}。ctx欠落は『Phase 1で生成』表示(ダミー音声は置かない)。
    ①②の並び順は固定(A=現行 / B=改善)。開発者向け詳細は dev_details.html に分離。"""
    def cell(src):
        return f"<audio controls preload='none' src='{H.escape(src)}'></audio>" if src else "<span class='na'>未生成(Phase 1で生成)</span>"
    cards = []
    for i, s in enumerate(sel, 1):
        ctx = s["context"]
        prev = "".join(f"<div>{H.escape(d['speaker_display'])}: {H.escape(d['text'])}</div>" for d in ctx["prev_dialogue"])
        nxt = "".join(f"<div>{H.escape(d['speaker_display'])}: {H.escape(d['text'])}</div>" for d in ctx["next_dialogue"])
        narr = "".join(f"<div class='lab'>地の文: {H.escape(x)}</div>" for x in (ctx["narration_before"], ctx["narration_after"]) if x)
        cards.append(
            f"<div class='card'><h2>{i}. {H.escape(s['speaker'].capitalize())}（{' / '.join(H.escape(c) for c in s['categories'])}）</h2>"
            f"<div class='scene'>{H.escape(s['scene_ja'])}</div><div class='en'>{H.escape(s['text'])}</div>"
            f"<details><summary>前後の会話・地の文（英語）</summary>{narr}<div class='lab'>直前のセリフ</div>{prev or '<div>なし</div>'}"
            f"<div class='lab'>直後のセリフ</div>{nxt or '<div>なし</div>'}</details>"
            f"<div class='row'><div class='col'><div class='lab'>A 現行方式</div>{cell(arms.get('base', {}).get(s['id']))}</div>"
            f"<div class='col'><div class='lab'>B 文脈・感情を追加</div>{cell(arms.get('ctx', {}).get(s['id']))}</div></div>"
            + (("<details><summary>参考: 別のtake（同じ方式を別に生成した音声）</summary>" + "".join(
                f"<div class='lab'>{H.escape(lbl)}</div>{cell(m.get(s['id']))}" for lbl, m in extra.items() if m.get(s['id'])) + "</details>") if extra else "")
            + "</div>")
    doc = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='robots' content='noindex,nofollow'>"
           f"<meta name='viewport' content='width=device-width, initial-scale=1'><title>セリフ音声 文脈・感情 比較試聴（Trial）</title><style>{_PAGE_CSS}</style></head><body>"
           "<h1>『賢者の贈り物』セリフ音声 現行方式 vs 文脈・感情を追加（Trial）</h1>"
           "<div class='note'><b>状態: Trial（Production採用ではありません）</b>。同じ英文・同じ声・同じAIモデル・同じ生成設定で、A=現行方式、"
           "B=Style（話し方の指示）に「話者の気持ち／場面／前後の会話／地の文の演出」を足した方式を聞き比べます。音量は両方そろえてあります。"
           "<br>聴いていただきたい観点: 感情が伝わるか / 抑揚の自然さ / 会話としての自然さ / 場面に合った演出 / 聞き取りやすさ / 大げさすぎないか。</div>"
           f"{''.join(cards)}<p class='lab'>開発者向けの詳細は <a href='dev_details.html'>dev_details.html</a></p></body></html>")
    ap = os.path.join(ROOT, out_dir, "index.html")
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return ap


def build_dev_details(analysis: dict | None, out_dir: str = PAGE_DIR) -> str:
    body = "<p>Phase 1実行後に生成条件・Style全文・ASR・leakage・機械指標を出力します。</p>" if not analysis else \
        "<pre>" + H.escape(json.dumps(analysis, ensure_ascii=False, indent=1)) + "</pre>"
    doc = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='robots' content='noindex,nofollow'><title>dev details</title>"
           f"<style>{_PAGE_CSS}pre{{white-space:pre-wrap;font-size:.8rem}}</style></head><body><h1>開発者向け詳細（Trial）</h1>{body}</body></html>")
    ap = os.path.join(ROOT, out_dir, "dev_details.html")
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return ap


def analyze_all(*, out_dir: str = OUT_DIR, page_dir: str = PAGE_DIR) -> dict:
    """Phase 1生成後(API 0): 生成済みarm/takeを解析し、mp3(target_rms統一)・analysis.json・試聴ページ・dev_details.htmlを書く。
    ページのA=Production既存①(過去take)、B=ctx_t1。ctx_t2/base_t*(対照take)は『参考take』として折りたたみに載せる。"""
    plan = load_plan()
    cl_map = {c["id"]: c for c in plan["clips"]}
    sel = load_json(f"{OUT_DIR}/phase0/selection.json")
    tr = target_rms_for_listening()
    gen_root = os.path.join(ROOT, out_dir, "gen")
    arm_dirs = sorted(d for d in os.listdir(gen_root) if os.path.isdir(os.path.join(gen_root, d))) if os.path.isdir(gen_root) else []
    notes = {}
    npath = f"{out_dir}/llm/emotion_notes.json"
    if os.path.exists(os.path.join(ROOT, npath)):
        notes = load_json(npath)["validated"]
    analysis = {"managed_id": MANAGED_ID, "target_rms": tr, "arms": arm_dirs, "clips": {}}
    pages = {"base": {}, "ctx": {}}
    extra = {}
    for s_ in sel:
        cid = s_["id"]
        clip = cl_map[cid]
        ctx = extract_context(plan, cid)
        words = n_words(clip["text"])
        row = {"text": clip["text"], "voice": s_["voice"], "existing_A": {**s_["existing_measure"], "asr_text": s_["existing_audio"]["asr_text"]}}
        orig = s_["existing_audio"]["original_wav"]
        row["existing_A"]["mp3"] = export_mp3(orig, f"{page_dir}/audio/A_{cid}.mp3", tr)
        pages["base"][cid] = f"audio/A_{cid}.mp3"
        for ad in arm_dirs:
            rpath = f"{out_dir}/gen/{ad}/{cid}/result.json"
            if not os.path.exists(os.path.join(ROOT, rpath)):
                continue
            r = load_json(rpath)
            if r.get("status") != "OK":
                row[ad] = {"status": r.get("status"), "fail_reason": r.get("fail_reason")}
                continue
            m = analyze_wav(r["wav"], words)
            note = notes.get(cid) if r["arm"] == "ctx" else None
            m.update({"asr_text": r["asr_text"], "n_tts_calls": r["n_tts_calls"], "request_prompt_matches_expected": r["request_prompt_matches_expected"],
                      "verbatim": verbatim_check(r["asr_text"], clip["text"]), "leakage": leakage_check(r["asr_text"], ctx, note),
                      "wav_sha256": r["wav_sha256"], "style_sha256": r["style_sha256"]})
            m["mp3"] = export_mp3(r["wav"], f"{page_dir}/audio/{ad}_{cid}.mp3", tr)
            row[ad] = m
            rel = f"audio/{ad}_{cid}.mp3"
            if ad == "ctx_t1":
                pages["ctx"][cid] = rel
            else:
                extra.setdefault(ad, {})[cid] = rel
        analysis["clips"][cid] = row
    save_json(f"{out_dir}/analysis.json", analysis)
    build_page(sel, pages, out_dir=page_dir, extra={f"参考take: {k}": v for k, v in extra.items()} or None)
    build_dev_details(analysis, out_dir=page_dir)
    return analysis


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=MANAGED_ID)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan", help="Phase 0: 選定・文脈・費用見積(API 0)")
    p_page = sub.add_parser("page", help="試聴ページ骨格(API 0)。生成済みarmがあれば反映")
    p_page.add_argument("--no-existing-mp3", action="store_true")
    sub.add_parser("analyze", help="生成済みarmの解析・mp3・試聴ページ(API 0)")
    sub.add_parser("llm", help="Phase 1(有料): 感情情報LLM 1 call")
    p_gen = sub.add_parser("gen", help="Phase 1(有料): arm生成")
    p_gen.add_argument("--arm", choices=("ctx", "base"), required=True)
    p_gen.add_argument("--take", type=int, default=1)
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        r = build_phase0_artifacts()
        tot = sum(e["tts_ctx_est_jpy"] for e in r["estimates"])
        print(json.dumps({"n": len(r["selection"]), "tts_ctx_est_jpy_per_take": round(tot, 3)}, ensure_ascii=False))
        return 0
    if a.cmd == "page":
        sel = load_json(f"{OUT_DIR}/phase0/selection.json")
        tr = target_rms_for_listening()
        arms = {"base": {}, "ctx": {}}
        if not a.no_existing_mp3:
            for s in sel:
                export_mp3(s["existing_audio"]["original_wav"], f"{PAGE_DIR}/audio/A_{s['id']}.mp3", tr)
                arms["base"][s["id"]] = f"audio/A_{s['id']}.mp3"
        print(build_page(sel, arms))
        print(build_dev_details(None))
        return 0
    if a.cmd == "analyze":
        r = analyze_all()
        print(json.dumps({"arms": r["arms"], "n_clips": len(r["clips"])}, ensure_ascii=False))
        return 0
    if a.cmd == "llm":
        r = run_emotion_llm()
        print(json.dumps({k: r[k] for k in ("cost_jpy", "n_accepted", "n_discarded", "n_no_explicit_cue")}, ensure_ascii=False))
        return 0
    if a.cmd == "gen":
        generate_arm(a.arm, a.take)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
