# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Family Z dialogue 文脈・感情情報(CONTEXT block)の正式Production経路。

ユーザー正式決定(APPROVED_FOR_PRODUCTION 2026-10-26): Trial(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01)で使用した文脈・感情情報生成方式を
**Prompt/モデル/決定論検査/CONTEXT書式とも逐語**で正式Productionへ移植する。本moduleは `er118_*` をimportしない(Trial一時機構を持ち込まない。
Trialのmodule globals差替え[use_case/configure_case]ではなく、作品別dataを引数で明示する純関数にした)。

- Trialと逐語同一(testでTrial moduleとsha/出力完全一致を固定): extract_context / allowed_source_text / EMOTION_DEVELOPER(rule 1-10) / EMOTION_SCHEMA /
  emotion_user_message / emotion_prompt_sha / validate_emotion_items / CONTEXT_HEAD / CONTEXT_TAIL / build_context_block / leakage_check。
- 引数化した点(Opus M-6): `validate_emotion_items` の許可語(Trialではmodule global ALLOWED_NAMES)、`extract_context` の話者表示名(同SPEAKER_DISPLAY)、
  EMOTION_DEVELOPERの作品名。いずれも story別dataとして明示的に渡す。
- Fable目視レビューの撤去: 決定論検査の3値(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)をそのまま消費する(Trial決定済み77件でvalidatorとFableの判断が100%一致、
  覆し0件。判定結果が同等の工程置換であって品質基準の緩和ではない。新しい品質基準・警告種別・blocking条件は作らない)。
- LLM失敗(1回再試行後も失敗)=技術STOP(再開可・承認不要)。全clip中立での続行はしない(Opus M-7)。
- Adv narratorのchunk展開は親clip列へ畳み戻す(Opus M-6)。Productionのplanは chunk spec(`<親>_k<j>`)を持つが、文脈抽出はTrialの segment_plan と同じ親clip列で行う。
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re

MANAGEMENT_ID = "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
SCHEMA = "fz_dialogue_ctx_notes_v1"
NOTES_RELPATH = "audit/dialogue_ctx_notes.json"
LLM_MODEL = "gpt-6-luna"     # Trial採用(本番ラインのモデル選定は別判断、PM_GOVERNANCE 25節)。reasoning effort=low
EXPECTED_BASE_STYLE_SHA = "add26d27a79c2cbee982eb5ddc32616b8294494a316b973215c94cccc76ede26"   # = p9a.ENGLISH_STYLE_PREFIX(Trial EXPECTED_BASE_STYLE_SHA)
LLM_MAX_ATTEMPTS = 2         # 初回+1回再試行(Opus M-7)

# 決定論の演出語抽出に使う語彙(Trial逐語)
STAGE_LEXICON = re.compile(
    r"(whisper\w*|softly|gently|quietly|loudly|smil\w+|tears?|cried|cry|laugh\w*|shout\w*|tremb\w*|nervous\w*|sigh\w*|"
    r"rushed|hurried|breath|shut her eyes|stopped|stared|eyes stayed|kept returning|paused|suddenly)", re.I)
NEIGHBOR_MAX_CLIP_DISTANCE = 4     # この距離(clip数)を超えるセリフは文脈に入れない(場面が離れている)
TIMESKIP_NARRATION_WORDS = 40      # 間の地の文がこれを超える語数なら時間経過とみなし、そのセリフは文脈に入れない
PREV_DIALOGUE_MAX = 2
NEXT_DIALOGUE_MAX = 1
NARRATION_SENTENCES = 2


class FzCtxNotesStop(RuntimeError):
    """感情notes生成の技術STOP(再開可)。er063側で FamilyZAudioStop 系へ載せ替えて送出する(`stop_type()`)。"""


def stop_type():
    """既存STOP系(FamilyZAudioStop)に揃えた例外型(Opus R-2)。遅延import(er063が本moduleを遅延importするため循環を避ける)。"""
    import er063_family_z_audio_01 as z
    return z.FamilyZDialogueCtxStop


# ============================================================
# 共通
# ============================================================
def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


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
# story別data(Trial検証済み作品はTrialのdataを逐語。それ以外は決定論fallback)
# ============================================================
TRIAL_STORY_DATA = {
    # Trial全編(er118_fz_full_episode_trial_01.py:49-61 WORK_CFG)。猿の手の許可語に whites を含む(Trial初回に12件が誤DISCARDされ許可名追加で解消)。
    "the_monkeys_paw": {
        "title": "The Monkey's Paw",
        "speaker_display": {"morris": "the retired sergeant-major", "mr_white": "Mr. White", "mrs_white": "Mrs. White", "herbert": "Herbert",
                            "visitor": "the stranger from the firm"},
        "allowed_names": {"herbert", "mr", "mrs", "white", "whites"}},
    # メロス: Production planの話者keyは正規化後(dionysius/selinuntius)。Trial plan側のalias(king/friend)と同じ表示名に揃える。
    "melos": {
        "title": "Before the Last Light (Melos)",
        "speaker_display": {"melos": "Melos", "king": "the ruler", "friend": "Melos's friend",
                            "dionysius": "the ruler", "selinuntius": "Melos's friend"},
        "allowed_names": {"melos"}},
    # Round 2(er118_fz_dialogue_context_tts_trial_01.py:1364-1383 WORKS)
    "the_open_window": {
        "title": "The Open Window",
        "speaker_display": {"vera": "Vera", "framton": "Framton", "mrs_sappleton": "Vera's aunt", "men": "one of the returning men"},
        "allowed_names": {"vera", "framton", "bertie", "india"}},
    # Round 1(同 :66 SPEAKER_DISPLAY, :53 ALLOWED_NAMES)
    "the_gift_of_the_magi": {
        "title": "The Gift of the Magi",
        "speaker_display": {"della": "Della", "jim": "Jim", "madame": "the hair-shop owner"},
        "allowed_names": {"della", "jim", "christmas"}},
}


def resolve_story_key(slug: str) -> str:
    """runnerが渡す`story_key`は実際には`--slug`(既定=story key)。slugが既知storyの接頭辞/接尾辞を持つ場合(例 melos_chunk01)は既知story keyへ解決し、
    Trial検証済みdataが黙ってfallbackに落ちるのを防ぐ。どれにも当たらなければslugのまま(story_data側で決定論fallback+source記録)。"""
    known = set(TRIAL_STORY_DATA)
    try:
        import er062_family_z_structure_01 as st
        known |= set(st.STORY_SPEAKER_CONFIG)
    except Exception:
        pass
    if slug in known:
        return slug
    for k in sorted(known, key=len, reverse=True):
        if slug.startswith(k) or slug.endswith(k):
            return k
    return slug


def _roster_display_from_attr_text(story_key: str) -> dict:
    """Trial未検証storyの表示名fallback(Opus R-2): 既存の話者表(er062 STORY_SPEAKER_CONFIG[story]["attr_roster_text"]の`- "key": Name, ...`行)から先頭の名称句を取る。"""
    try:
        import er062_family_z_structure_01 as st
        txt = st.STORY_SPEAKER_CONFIG[story_key].get("attr_roster_text") or ""
    except Exception:
        return {}
    out = {}
    for line in txt.splitlines():
        m = re.match(r'\s*-\s*"([a-z_0-9]+)"\s*:\s*(.+)$', line)
        if not m:
            continue
        head = re.split(r"[,(;]", m.group(2), maxsplit=1)[0].strip().rstrip(".")
        if head and head.lower() not in ("any other speaker", "the line is not spoken by a character"):
            out[m.group(1)] = head
    return out


def story_data(story_key: str, speakers: list) -> dict:
    """作品別の {title, speaker_display, allowed_names, sources}。Trial検証済み作品=Trial dataを逐語。それ以外=決定論fallback
    (表示名=既存話者表の名称句 > roster key のTitle化。許可語=表示名tokenと話者key token。失敗モードは誤DISCARD=中立化=安全側)。"""
    td = TRIAL_STORY_DATA.get(story_key)
    if td is not None:
        disp = dict(td["speaker_display"])
        src = {s: ("trial_verified" if s in disp else "fallback_key_title") for s in speakers}
        for s in speakers:
            disp.setdefault(s, s.replace("_", " ").title())
        return {"title": td["title"], "title_source": "trial_verified", "speaker_display": disp, "allowed_names": set(td["allowed_names"]),
                "speaker_display_source": src}
    roster = _roster_display_from_attr_text(story_key)
    disp, src = {}, {}
    for s in speakers:
        if s in roster:
            disp[s], src[s] = roster[s], "attr_roster_text"
        else:
            disp[s], src[s] = s.replace("_", " ").title(), "fallback_key_title"
    allowed = set()
    for s, d in disp.items():
        allowed |= set(norm_tokens(d)) | set(norm_tokens(s.replace("_", " ")))
    title = story_key.replace("_", " ").title()
    return {"title": title, "title_source": "fallback_key_title", "speaker_display": disp, "allowed_names": allowed, "speaker_display_source": src}


# ============================================================
# Productionのplan(ClipSpec列) -> Trialの segment_plan clips 相当(Opus M-6: chunk展開の畳み戻しadapter)
# ============================================================
def story_clips_from_plan(plan: list) -> list:
    """plan(er063 ClipSpec列)のstory clip(kind=narrator|dialogue)を、Trial `segment_plan_{level}.json` の `clips` と同形の親clip列へ戻す。
    chunk spec(`<親>_k<j>`、extra.chunk)は親clip(id=parent_id、text=parent_text)1件へ畳み戻す(最初のchunkの位置)。順序はplan順のまま。"""
    out, seen_parent = [], set()
    for s in plan:
        if s.kind not in ("narrator", "dialogue"):
            continue
        ch = (s.extra or {}).get("chunk")
        if ch:
            pid = ch["parent_id"]
            if pid in seen_parent:
                continue
            seen_parent.add(pid)
            out.append({"id": pid, "speaker": s.speaker, "voice_role": "narrator" if s.kind == "narrator" else f"dialogue:{s.speaker}",
                        "text": ch["parent_text"], "part": s.part, "voice": s.voice})
            continue
        out.append({"id": s.clip_id, "speaker": s.speaker, "voice_role": "narrator" if s.kind == "narrator" else f"dialogue:{s.speaker}",
                    "text": s.text, "part": s.part, "voice": s.voice})
    return out


# ============================================================
# 文脈の決定論抽出(LLM不使用。Trial extract_context と逐語同一、話者表示名のみ引数化)
# ============================================================
def extract_context(clips: list, clip_id: str, speaker_display: dict) -> dict:
    idx = {c["id"]: i for i, c in enumerate(clips)}[clip_id]
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
        return {"clip_id": x["id"], "speaker": x["speaker"], "speaker_display": speaker_display.get(x["speaker"], x["speaker"]), "text": x["text"]}

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
        "clip_id": clip_id, "speaker": c["speaker"], "speaker_display": speaker_display.get(c["speaker"], c["speaker"]),
        "voice": c.get("voice"), "text": c["text"], "part": c.get("part"),
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
# 感情・心理状態の作成(LLM 1 call、level内の全dialogue一括)と創作防止検査(Trial逐語)
# ============================================================
INTENSITY_STEMS = ("despair", "devastat", "terrif", "heartbr", "ecstat", "overjoy", "overwhelm", "hysteric", "desperat")   # 強度語deny(語幹一致)

_EMOTION_DEVELOPER_TEMPLATE = (
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
    "7. Do not add person names or places that are not in the provided text.\n"
    "8. Use mild, plain wording for feelings (for example \"a little nervous\", \"quietly hopeful\"). Never use intensity words such as despair, devastated, terrified, "
    "heartbroken, ecstatic, overjoyed, overwhelmed, hysterical, desperate.\n"
    "9. Describe the feeling, not acting instructions: do not write sob, cry, tremble, gasp, sigh, laugh, or similar sound or gesture directions.\n"
    "10. At least one evidence quote must come from the narration or another speaker's line, unless the line itself contains an exclamation or question that shows the feeling.\n"
    "Return JSON only.")


def emotion_developer(title: str) -> str:
    """EMOTION_DEVELOPER(Trialと同一。作品名のみ置換 = Trial configure_case と同じ replace)。"""
    return _EMOTION_DEVELOPER_TEMPLATE.replace("The Gift of the Magi", title)


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


def emotion_prompt_sha(title: str) -> str:
    return sha_text(emotion_developer(title) + "\n" + json.dumps(EMOTION_SCHEMA, sort_keys=True))


def validate_emotion_items(raw_items: list, contexts: list, allowed_names) -> dict:
    """LLM出力の創作防止検査(決定論、Trialと逐語同一。許可語のみ引数化)。根拠引用が当該文脈の原文に逐語一致しない/語数超過/新規固有名詞/強度語を含む項目は破棄し、
    中立のfallbackへ置換する。戻り値 {clip_id: {"state","scene","reaction","evidence","status","discard_reasons","llm_raw"}}。"""
    by_id = {it.get("clip_id"): it for it in (raw_items or []) if isinstance(it, dict)}
    out = {}
    allowed_names = set(allowed_names)
    for ctx in contexts:
        cid = ctx["clip_id"]
        it = by_id.get(cid)
        src = allowed_source_text(ctx)
        src_n = norm_for_match(src)
        src_tokens = set(norm_tokens(src)) | allowed_names
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
        # 強度語deny(語幹一致。state/scene/reactionのみ。根拠引用は原文なので対象外)
        for field_name, val in (("state", state), ("scene", scene), ("reaction", reaction)):
            for w in norm_tokens(val):
                if any(w.startswith(st) for st in INTENSITY_STEMS):
                    reasons.append(f"intensity_word:{field_name}:{w}")
        if reasons or not cue:
            if reasons:
                out[cid] = {"state": "", "scene": "", "reaction": "", "evidence": [], "status": "DISCARDED", "discard_reasons": reasons,
                            "llm_raw": {"state": state, "scene": scene, "reaction": reaction, "evidence": ev}}
            else:
                out[cid] = {"state": "", "scene": scene, "reaction": reaction, "evidence": ev, "status": "NO_EXPLICIT_CUE", "discard_reasons": [],
                            "llm_raw": {"state": state, "scene": scene, "reaction": reaction, "evidence": ev}}
        else:
            out[cid] = {"state": state, "scene": scene, "reaction": reaction, "evidence": ev, "status": "ACCEPTED", "discard_reasons": [],
                        "llm_raw": {"state": state, "scene": scene, "reaction": reaction, "evidence": ev}}
    return out


# ============================================================
# CONTEXT block / Style構成(Trial逐語)
# ============================================================
CONTEXT_HEAD = ("CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. "
                "Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)")
CONTEXT_TAIL = ("Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. "
                "The story's own narration above is what supports the feeling of this line. "
                "Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. "
                "Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds "
                "(no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. "
                "If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. "
                "Do not read any word of this CONTEXT block.")


def is_dialogue_tag(sentence: str) -> bool:
    """会話タグ = 小文字で始まる5語以下の文(例 `she whispered.`)。逐語でCONTEXTへ入れると読み上げ混入の主因になる。"""
    t = sentence.strip()
    return bool(t) and t[0].islower() and n_words(t) <= 5


def _narration_without_tags(narr: str) -> str:
    return " ".join(x for x in split_sentences(narr) if not is_dialogue_tag(x))


def _unq(t: str) -> str:
    return t.strip().strip('"“”')


def build_context_block(ctx: dict, note) -> str:
    """CONTEXTブロック本文。noteは validate_emotion_items の1件(None=感情情報なし)。noteのstateが空(NO_EXPLICIT_CUE/DISCARDED/None)なら状態行を出さない。"""
    lines = [CONTEXT_HEAD, f"Speaker of this line: {ctx['speaker_display']}."]
    if note and note.get("state"):
        lines.append(f"Speaker's state of mind: {note['state']}")
    if note and note.get("scene"):
        lines.append(f"Scene: {note['scene']}")
    for d in ctx["prev_dialogue"]:
        lines.append(f'Spoken line before (said by {d["speaker_display"]}; not part of this line): {_unq(d["text"])}')
    nb = _narration_without_tags(ctx["narration_before"])
    if nb:
        lines.append(f'Narration just before: "{nb}"')
    for d in ctx["next_dialogue"]:
        lines.append(f'Spoken line after (said by {d["speaker_display"]}; not part of this line): {_unq(d["text"])}')
    na = _narration_without_tags(ctx["narration_after"])
    if na:
        lines.append(f'Narration just after: "{na}"')
    if ctx["manner_words"]:
        lines.append("Manner words from the narration: " + ", ".join(ctx["manner_words"]))
    if note and note.get("reaction"):
        lines.append(f"How this line answers the previous one: {note['reaction']}")
    lines.append(CONTEXT_TAIL)
    return "\n".join(lines)


def base_style() -> str:
    """従来方式のStyle(承認済みの既定Dialogue Style = p9a.ENGLISH_STYLE_PREFIX)。shaが期待値と異なれば fail-closed。"""
    import er003_b1_p9a_audio as p9a
    s = p9a.ENGLISH_STYLE_PREFIX
    if sha_text(s) != EXPECTED_BASE_STYLE_SHA:
        raise stop_type()(f"[STOP][Z-DIALOGUE-CTX] 従来Dialogue Style(p9a.ENGLISH_STYLE_PREFIX)のshaが承認済み値と異なります: {sha_text(s)[:12]}。"
                          "Trial方式の移植はこのStyleを土台にしているため課金前にSTOPしました。")
    return s


def build_ctx_style(ctx: dict, note) -> str:
    """文脈・感情付きStyle = 従来Style + 空行 + CONTEXT block(Trial style_for_arm('ctx') と逐語同一)。"""
    return base_style().rstrip() + "\n\n" + build_context_block(ctx, note)


# ============================================================
# leakage検査(観測のみ。NG理由にしない=ASRの表記違いだけで再生成しない。Trial逐語)
# ============================================================
LEAK_MIN_RUN = 2


def context_only_words(ctx: dict, note) -> set:
    blk = build_context_block(ctx, note)
    body = blk.split("\n", 1)[1] if "\n" in blk else blk
    return set(norm_tokens(body)) - set(norm_tokens(ctx["text"]))


def leakage_check(asr_text, ctx: dict, note) -> dict:
    target = norm_tokens(ctx["text"])
    asr = norm_tokens(asr_text or "")
    only = context_only_words(ctx, note)
    runs, extra = [], []
    sm = difflib.SequenceMatcher(None, target, asr, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            seg = asr[j1:j2]
        elif tag == "replace" and (j2 - j1) > (i2 - i1):
            seg = asr[j1 + (i2 - i1):j2]
        else:
            continue
        runs.append(seg)
        extra += seg
    hit_words = sorted({w for w in extra if w in only})
    max_run = max((len(r) for r in runs), default=0)
    return {"flagged": bool(max_run >= LEAK_MIN_RUN or hit_words), "needs_listen": bool(extra), "extra_tokens": extra, "extra_runs": runs,
            "max_extra_run": max_run, "context_only_hits": hit_words, "asr_words": len(asr), "target_words": len(target)}


def leakage_all_attempts(attempt_asr_texts: list, final_asr_text, ctx: dict, note) -> dict:
    per = [leakage_check(t, ctx, note) for t in attempt_asr_texts if t is not None]
    fin = leakage_check(final_asr_text, ctx, note)
    return {"observation_only": True, "leakage_any_attempt": any(x["flagged"] for x in per) or fin["flagged"], "leakage_final": fin["flagged"],
            "needs_listen_any_attempt": any(x["needs_listen"] for x in per) or fin["needs_listen"],
            "per_attempt": per, "final": fin}


# ============================================================
# level単位の notes 生成(1 call + 1回再試行)・保存・再利用
# ============================================================
def default_llm_fn(developer: str, user: str) -> dict:
    """Trial run_llm_case と同一のcall形(model=gpt-6-luna, reasoning effort=low, structured output)。
    戻り値 {"raw": dict, "model_returned": str, "cost_jpy": float}。cost loggerはrunnerが cl.install 済み(OpenAIクライアント全体に掛かる)。"""
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er062_family_z_writer_01 as zw
    client = vfl01.get_client()
    msgs = [{"role": "developer", "content": developer}, {"role": "user", "content": user}]
    kw = {"model": LLM_MODEL, "reasoning": {"effort": "low"}, "input": msgs, "text": {"format": {"type": "json_schema", **EMOTION_SCHEMA}}}
    r = client.responses.create(**kw)
    cost = zw.cost_jpy(LLM_MODEL, r.usage)
    if not str(r.model).startswith(LLM_MODEL):
        raise RuntimeError(f"返却modelが{LLM_MODEL}で始まらない: {r.model}")
    return {"raw": json.loads(r.output_text), "model_returned": str(r.model), "cost_jpy": float(cost)}


def _cost_segment(name: str):
    import contextlib
    try:
        import er005_cost_logger as cl
        return cl.segment_context(name)
    except Exception:
        return contextlib.nullcontext()


LLM_FN = None   # test/driverが差し替える注入点(Noneなら default_llm_fn)。env/flagではない。


def body_sha256(clips: list) -> str:
    """level内の全story clip(地の文を含む)の (id, speaker, text, voice_role) を束ねたsha(本文・並びが変われば変わる。文脈抽出は地の文にも依存するため全clip)。"""
    rows = [(c["id"], c["speaker"], c["text"], c["voice_role"]) for c in clips]
    return sha_text(json.dumps(rows, ensure_ascii=False))


def _atomic_write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


class NotesProvider:
    """level単位。`ensure()` で保存済みnotesを再利用、無ければ(または本文が変わっていれば)LLM 1 call(+1回再試行)で作る。
    LLM失敗(再試行後も)=FzCtxNotesStop(技術STOP・再開可)。結果は run dir `audit/` に不変保存(run内で再callしない)。"""

    def __init__(self, level_dir: str, story_key: str, clips: list, now_fn=None):
        self.level_dir = level_dir
        self.story_key = story_key
        self.clips = clips
        self.speakers = sorted({c["speaker"] for c in clips if c["voice_role"].startswith("dialogue:")} | {c["speaker"] for c in clips})
        self.data = story_data(story_key, self.speakers)
        self.path = f"{level_dir}/{NOTES_RELPATH}"
        self._rec = None
        self.llm_calls = 0
        self.dialogue_ids = [c["id"] for c in clips if c["voice_role"].startswith("dialogue:")]

    # ---- deterministic ----
    def contexts(self) -> dict:
        return {cid: extract_context(self.clips, cid, self.data["speaker_display"]) for cid in self.dialogue_ids}

    def context_input_sha(self, clip_id: str) -> str:
        return sha_text(json.dumps(self.contexts_cache()[clip_id], ensure_ascii=False, sort_keys=True))

    def contexts_cache(self) -> dict:
        if not hasattr(self, "_ctxs"):
            self._ctxs = self.contexts()
        return self._ctxs

    # ---- notes ----
    def _fresh_ok(self, rec: dict) -> bool:
        return (rec.get("schema") == SCHEMA and rec.get("body_sha256") == body_sha256(self.clips)
                and rec.get("prompt_sha256") == emotion_prompt_sha(self.data["title"]) and rec.get("model_requested") == LLM_MODEL)

    def ensure(self) -> dict:
        if self._rec is not None:
            return self._rec
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    rec = json.load(f)
            except Exception:
                rec = None
            if rec and self._fresh_ok(rec):
                self._rec = rec
                return rec
            if rec:   # 本文が変わった(Opus R-2: level単位でLLM再call)。旧notesは .prev として残す
                try:
                    os.replace(self.path, self.path + ".prev")
                except OSError:
                    pass
        self._rec = self._generate()
        return self._rec

    def _generate(self) -> dict:
        ctxs = [self.contexts_cache()[cid] for cid in self.dialogue_ids]
        if not ctxs:
            rec = self._record([], {}, {"raw": {"items": []}, "model_returned": None, "cost_jpy": 0.0}, 0)
            return rec
        title = self.data["title"]
        developer, user = emotion_developer(title), emotion_user_message(ctxs)
        fn = LLM_FN or default_llm_fn
        last = None
        for k in range(1, LLM_MAX_ATTEMPTS + 1):
            try:
                self.llm_calls += 1
                with _cost_segment(f"dialogue_ctx_notes:{os.path.basename(self.level_dir)}"):   # 費用はdialogue clipではなくnotes生成として計上
                    out = fn(developer, user)
                raw = out["raw"]
                if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
                    raise ValueError("schema違反: items(list)がありません")
                checked = validate_emotion_items(raw.get("items"), ctxs, self.data["allowed_names"])
                rec = self._record(ctxs, checked, out, k)
                return rec
            except Exception as e:   # transport/schema/JSON/model不一致。1回だけ再試行
                last = e
        raise stop_type()(f"[STOP][Z-DIALOGUE-CTX-NOTES] 感情・文脈notesのLLM生成が{LLM_MAX_ATTEMPTS}回失敗しました(level_dir={self.level_dir}): {last}。"
                          "文脈・感情付きTTSの前提情報が無いため、このlevelのdialogue TTS前に技術STOPしました(全clip中立での続行はしません)。"
                          "承認不要・再開可(同じ引数で再実行)。")

    def _record(self, ctxs: list, checked: dict, out: dict, attempt_no: int) -> dict:
        title = self.data["title"]
        counts = {k: sum(1 for v in checked.values() if v["status"] == k) for k in ("ACCEPTED", "NO_EXPLICIT_CUE", "DISCARDED")}
        rec = {"schema": SCHEMA, "management_id": MANAGEMENT_ID, "story_key": self.story_key, "level_dir": self.level_dir,
               "model_requested": LLM_MODEL, "model_returned": out.get("model_returned"), "cost_jpy": round(out.get("cost_jpy") or 0.0, 4),
               "llm_attempt_no": attempt_no, "llm_calls_this_process": self.llm_calls,
               "n_clips": len(ctxs), "prompt_sha256": emotion_prompt_sha(title), "title": title, "title_source": self.data["title_source"],
               "speaker_display": self.data["speaker_display"], "speaker_display_source": self.data["speaker_display_source"],
               "allowed_names": sorted(self.data["allowed_names"]),
               "body_sha256": body_sha256(self.clips),
               "user_message_sha256": sha_text(emotion_user_message(ctxs)) if ctxs else None,
               "raw_output": out.get("raw"), "validated": checked,
               "n_accepted": counts["ACCEPTED"], "n_no_explicit_cue": counts["NO_EXPLICIT_CUE"], "n_discarded": counts["DISCARDED"],
               "acceptance": "deterministic_validator(Fable目視レビューは撤去。Trial決定済み77件でvalidatorとFableの判断が100%一致=工程置換)"}
        _atomic_write_json(self.path, rec)
        return rec

    def note_for(self, clip_id: str):
        rec = self.ensure()
        return (rec.get("validated") or {}).get(clip_id)

    def style_for(self, clip_id: str) -> dict:
        """clipの文脈・感情付きStyleと記録(note状態・context sha・speaker_display_source)。notes未生成ならここでLLMを呼ぶ(level単位1回、保存済みなら0)。"""
        ctx = self.contexts_cache()[clip_id]
        note = self.note_for(clip_id)
        style = build_ctx_style(ctx, note)
        return {"style": style, "style_sha256": sha_text(style), "context_input_sha256": self.context_input_sha(clip_id),
                "note_status": (note or {}).get("status"), "speaker_display_source": self.data["speaker_display_source"].get(ctx["speaker"]),
                "emotion_prompt_sha256": emotion_prompt_sha(self.data["title"]), "ctx": ctx, "note": note}


_PROVIDERS: dict = {}


def get_provider(level_dir: str, story_key: str, clips: list) -> NotesProvider:
    """(level_dir, story_key, 本文sha) ごとに1つ(プロセス内メモ化。保存済みnotesの再利用はNotesProvider.ensure)。"""
    k = (os.path.abspath(level_dir), story_key, body_sha256(clips))
    p = _PROVIDERS.get(k)
    if p is None:
        p = NotesProvider(level_dir, story_key, clips)
        _PROVIDERS[k] = p
    _BY_LEVEL[os.path.abspath(level_dir)] = p
    return p


_BY_LEVEL: dict = {}


def provider_for_level(level_dir: str) -> NotesProvider:
    """prepare_dialogue_ctx が登録した、このlevel_dirのNotesProvider(同一プロセス内)。"""
    p = _BY_LEVEL.get(os.path.abspath(level_dir))
    if p is None:
        raise stop_type()(f"[STOP][Z-DIALOGUE-CTX] level_dir={level_dir} のNotesProviderが未登録です(prepare_dialogue_ctxを経由していません)。")
    return p


def reset_providers_for_test() -> None:
    _PROVIDERS.clear()
    _BY_LEVEL.clear()
