# ============================================================
# er013_family_c_production_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01
#         (委任A: Family C 2仕様のProduction wiring)
# ============================================================
# 目的: ユーザー正式決定(2026-09-16)によりAPPROVED_FOR_PRODUCTIONとなった
# Family C(Future Story)の2仕様を、正式Production module として集約する。
#
#   仕様A: Story TTS segmentation原則
#     同一Voiceの自然な連続性を優先する/不要な短segmentを避ける/Voice変更点
#     では分割する/Comment挿入位置・scene・semantic boundaryを考慮する/
#     word countだけで機械的に細分化しない/概ね100語以内を運用目安とし120語を
#     大きく超えない/150〜200語級の長segmentは避ける/Voice境界による不可避な
#     短segmentは許容する。
#     (根拠: Trial-11/12 `er013_family_c_episode_trial_11_memory_run.py`/
#      `..._trial_12_memory_b1_run.py`/`..._trial_12_twins_run.py`/
#      `..._trial_12_twins_b1_run.py`で`VALIDATED`、2026-09-16ユーザー
#      正式決定で`APPROVED_FOR_PRODUCTION`)
#
#   仕様B: Family C A2 Comment理解ガイド型Contract
#     「聞いてみましょう」等のメタナレーションを避け、次の英語理解に必要な
#     具体的context(場所・状況/人物関係/場面転換/次の行動/選択・対立点)を
#     簡潔な日本語で提供する。B1 Commentには適用しない(既存B1 Support経路を
#     維持し、本moduleはB1 Comment Promptを一切提供しない構造上のガードで
#     誤適用を防ぐ)。
#
# 本moduleはTrial script(`er013_family_c_episode_trial_1[012]_*.py`)を
# import・参照しない(Trial script側が本moduleを参照することもない、履歴
# として残置のみ)。記事固有のVoice/scene boundary・登場人物キーワードは
# すべて呼び出し側が引数・設定で渡し、本moduleが固定値で上書きすることはない。
#
# 語数目安(target_words/soft_max_words/hard_avoid_words)は運用目安であり、
# 生成をブロックしない。hard_avoid_words超過はsegmentへ`warnings`として
# 記録するのみで、可能なら最も近い段落境界で自動分割する
# (`_apply_word_guideline_splits`)。
# ============================================================
from __future__ import annotations

import re
from typing import Callable, Iterable, Sequence


# ============================================================
# 1. Story TTS segmentation原則(仕様A)
# ============================================================

DEFAULT_QUOTE_RE = re.compile("[“\"][^”\"]*[”\"]")
_CLOSE_QUOTE_CHARS = "”\""


def normalize_for_tts(raw_text: str) -> str:
    """Trial-11/12と同一の正規化(スマートクォート→ストレート、太字記号除去、
    空白圧縮)。新しい語・語順の変更は行わない。"""
    t = raw_text
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def split_into_paragraphs(text: str) -> list:
    return text.split("\n\n")


def classify_quote_voice_window(
    paragraph_text: str,
    start: int,
    end: int,
    voice_keywords: "dict[str, Sequence[str]]",
    *,
    window: int = 80,
    default_voice: str = "narrator",
    close_quote_chars: str = _CLOSE_QUOTE_CHARS,
) -> str:
    """引用符の前後window文字を見てVoiceを判定する(OPEN-156修正版を汎用化)。
    同一段落内に直前の引用符区間がある場合、before windowがその内容まで
    拾ってしまい誤判定する可能性があるため、直近の閉じ引用符より後ろだけを
    before windowに使う。voice_keywordsは{voice_name: [keyword, ...]}の
    dictで、記事側が渡す(挿入順に判定、最初に一致したvoiceを採用)。"""
    before_raw = paragraph_text[max(0, start - window):start]
    last_close = -1
    for ch in close_quote_chars:
        idx = before_raw.rfind(ch)
        if idx > last_close:
            last_close = idx
    if last_close != -1:
        before_raw = before_raw[last_close + 1:]
    before = before_raw.lower()
    after = paragraph_text[end:end + window].lower()
    window_text = before + " " + after
    for voice, keywords in voice_keywords.items():
        if any(kw.lower() in window_text for kw in keywords):
            return voice
    return default_voice


def split_paragraph_by_quotes(
    paragraph_text: str,
    voice_keywords: "dict[str, Sequence[str]]",
    *,
    quote_re: "re.Pattern | None" = None,
    default_voice: str = "narrator",
) -> list:
    """段落内の引用符区間を境に(voice, raw_text, is_quote)へ分割する。
    raw_textを順に連結するとparagraph_textへ完全一致で復元できる。"""
    quote_re = quote_re or DEFAULT_QUOTE_RE
    chunks = []
    pos = 0
    for m in quote_re.finditer(paragraph_text):
        if m.start() > pos:
            chunks.append((default_voice, paragraph_text[pos:m.start()], False))
        voice = classify_quote_voice_window(
            paragraph_text, m.start(), m.end(), voice_keywords, default_voice=default_voice)
        chunks.append((voice, m.group(0), True))
        pos = m.end()
    if pos < len(paragraph_text):
        chunks.append((default_voice, paragraph_text[pos:], False))
    return chunks


def build_flat_voice_chunks(
    paragraphs: Sequence[str],
    voice_keywords: "dict[str, Sequence[str]]",
    *,
    quote_re: "re.Pattern | None" = None,
    default_voice: str = "narrator",
    display_paragraph_voice: "dict[int, str] | None" = None,
    quote_voice_override_paragraphs: "dict[int, str] | None" = None,
    restrict_quote_splitting_to_paragraphs: "Iterable[int] | None" = None,
) -> list:
    """段落列を(paragraph_index, voice, raw_text)のflatな列へ変換する。

    display_paragraph_voice(記事固有、任意)は「段落全体を1つのvoiceとして
    扱い引用符分割しない」段落(Twins episodeのdisplay文等)を
    {paragraph_index: voice}で指定する。

    quote_voice_override_paragraphs(記事固有、任意)は「この段落内の引用符
    区間は前後windowのkeyword判定を使わず常に指定voiceとする」段落を
    {paragraph_index: voice}で指定する(Twins A2 episodeのように、記事側で
    話者が引用符段落単位で確定している場合に使う。地の文はdefault_voiceの
    まま)。

    restrict_quote_splitting_to_paragraphs(記事固有、任意)を指定すると、
    その集合に含まれない段落は引用符の有無に関わらず分割せずdefault_voiceの
    1chunkとして扱う(Twins A2 episodeのように、対話段落があらかじめ列挙
    されている記事で、他の地の文段落を誤って引用符分割しないためのガード)。"""
    display_paragraph_voice = display_paragraph_voice or {}
    quote_voice_override_paragraphs = quote_voice_override_paragraphs or {}
    restrict_set = None if restrict_quote_splitting_to_paragraphs is None else set(
        restrict_quote_splitting_to_paragraphs)
    flat = []
    for p_idx, para in enumerate(paragraphs):
        if para.strip() == "":
            continue
        if p_idx in display_paragraph_voice:
            flat.append((p_idx, display_paragraph_voice[p_idx], para))
            continue
        if p_idx in quote_voice_override_paragraphs:
            override_voice = quote_voice_override_paragraphs[p_idx]
            qre = quote_re or DEFAULT_QUOTE_RE
            pos = 0
            for m in qre.finditer(para):
                if m.start() > pos:
                    flat.append((p_idx, default_voice, para[pos:m.start()]))
                flat.append((p_idx, override_voice, m.group(0)))
                pos = m.end()
            if pos < len(para):
                flat.append((p_idx, default_voice, para[pos:]))
            continue
        if restrict_set is not None and p_idx not in restrict_set:
            flat.append((p_idx, default_voice, para))
            continue
        for voice, raw, _is_quote in split_paragraph_by_quotes(
                para, voice_keywords, quote_re=quote_re, default_voice=default_voice):
            flat.append((p_idx, voice, raw))
    return flat


def _flush_segment(current_voice: str, current_chunks: list, reason: str) -> dict:
    parts = []
    prev_p = None
    for p, r in current_chunks:
        if prev_p is not None and p != prev_p:
            parts.append(" ")
        parts.append(r)
        prev_p = p
    raw_text = "".join(parts)
    p_indices = sorted({p for p, _ in current_chunks})
    tts_text = normalize_for_tts(raw_text)
    return {
        "voice": current_voice,
        "source_paragraph_indices": p_indices,
        "raw_text": raw_text,
        "tts_text": tts_text,
        "word_count": len(tts_text.split()),
        "split_reason": reason,
        "paragraph_contributions": list(current_chunks),
    }


def _build_base_segments(flat_chunks: list, force_split_before_paragraphs: "Iterable[int]") -> list:
    force_set = set(force_split_before_paragraphs)
    segments = []
    current_voice = None
    current_chunks: list = []
    pending_reason = "article_start"
    for p_idx, voice, raw in flat_chunks:
        starts_new_paragraph = (not current_chunks) or (p_idx != current_chunks[-1][0])
        force_break = starts_new_paragraph and p_idx in force_set
        if current_voice is not None and (voice != current_voice or force_break):
            reason = "voice_boundary(分割不可避)" if voice != current_voice else (
                "comment_or_scene_boundary(呼び出し側指定のforce_split_before_paragraphs)")
            segments.append(_flush_segment(current_voice, current_chunks, reason))
            current_chunks = []
        current_voice = voice
        current_chunks.append((p_idx, raw))
    if current_chunks:
        # 最終segmentの理由: 直前の一つ前のsegmentがあれば連続の帰結、無ければ記事全体が1segment
        reason = "article_end(直前の分割点から続く同一Voice区間)" if segments else "single_segment_article"
        segments.append(_flush_segment(current_voice, current_chunks, reason))
    return segments


def _regroup_contributions_by_paragraph(contributions: list) -> list:
    """[(p_idx, raw), ...] を段落単位でグループ化する([(p_idx, [raw, ...]), ...])。"""
    groups = []
    cur_p = None
    cur_texts: list = []
    for p, r in contributions:
        if cur_p is None or p == cur_p:
            cur_texts.append(r)
            cur_p = p
        else:
            groups.append((cur_p, cur_texts))
            cur_texts = [r]
            cur_p = p
    if cur_texts:
        groups.append((cur_p, cur_texts))
    return groups


def _build_segment_from_groups(voice: str, groups: list, reason: str) -> dict:
    contribs = []
    for p, texts in groups:
        for t in texts:
            contribs.append((p, t))
    return _flush_segment(voice, contribs, reason)


def _apply_word_guideline_splits(
    segments: list, *, target_words: int, soft_max_words: int, hard_avoid_words: int,
) -> list:
    """語数目安は運用目安でありブロックしない。hard_avoid_words超過segmentは
    複数段落にまたがる場合のみ、語数の中間点に最も近い段落境界で自動分割する
    (呼び出し側が指定したVoice/scene boundaryを上書きすることはない。あくまで
    同一Voice内・force_split指定がない区間内での追加分割)。分割できない
    (単一段落)場合はwarningのみ記録し生成はブロックしない。"""
    result = []
    for seg in segments:
        wc = seg["word_count"]
        warnings = []
        if wc > hard_avoid_words and len(seg["source_paragraph_indices"]) > 1:
            groups = _regroup_contributions_by_paragraph(seg["paragraph_contributions"])
            if len(groups) > 1:
                target_half = wc / 2.0
                best_i, best_diff = None, None
                joined_so_far = ""
                for i, (_p, texts) in enumerate(groups[:-1]):
                    piece = "".join(texts)
                    joined_so_far = (joined_so_far + " " + piece) if joined_so_far else piece
                    cum_words = len(normalize_for_tts(joined_so_far).split())
                    diff = abs(cum_words - target_half)
                    if best_diff is None or diff < best_diff:
                        best_diff, best_i = diff, i
                if best_i is not None:
                    left = _build_segment_from_groups(
                        seg["voice"], groups[:best_i + 1],
                        seg["split_reason"] + "; word_count_guideline_auto_split(前半、"
                        f"元{wc}語がhard_avoid_words={hard_avoid_words}語を超過したため"
                        "最も近い段落境界で自動分割)")
                    right = _build_segment_from_groups(
                        seg["voice"], groups[best_i + 1:],
                        seg["split_reason"] + "; word_count_guideline_auto_split(後半、"
                        f"元{wc}語がhard_avoid_words={hard_avoid_words}語を超過したため"
                        "最も近い段落境界で自動分割)")
                    for s in (left, right):
                        s["warnings"] = [f"auto_split_hard_avoid_exceeded(original_word_count={wc})"]
                    result.append(left)
                    result.append(right)
                    continue
            warnings.append(f"hard_avoid_exceeded_unsplittable(word_count={wc}, "
                             f"hard_avoid_words={hard_avoid_words})")
        elif wc > hard_avoid_words:
            warnings.append(f"hard_avoid_exceeded_unsplittable(word_count={wc}, "
                             f"hard_avoid_words={hard_avoid_words}, single_paragraph)")
        elif wc > soft_max_words:
            warnings.append(f"soft_max_exceeded(word_count={wc}, soft_max_words={soft_max_words})")
        seg["warnings"] = warnings
        result.append(seg)
    for i, s in enumerate(result, start=1):
        s["id"] = f"story_{i:03d}"
    return result


def plan_story_segments(
    flat_chunks: list,
    *,
    force_split_before_paragraphs: "Iterable[int]" = frozenset(),
    target_words: int = 100,
    soft_max_words: int = 120,
    hard_avoid_words: int = 150,
) -> list:
    """Family C Story TTS segmentation原則(仕様A、APPROVED_FOR_PRODUCTION、
    2026-09-16)の正式実装。

    flat_chunks: `build_flat_voice_chunks()`等で作った
        (paragraph_index, voice, raw_text)のflatな列。
    force_split_before_paragraphs: Comment挿入位置・scene/semantic boundaryなど、
        記事固有の理由でVoiceが同じでも分割が必要な段落index集合
        (呼び出し側が決定して渡す。本関数が固定値で上書きすることはない)。
    target_words/soft_max_words/hard_avoid_words: 運用目安(hard capではない)。

    戻り値: 各segment dict(id/voice/source_paragraph_indices/raw_text/
    tts_text/word_count/split_reason/warnings/paragraph_contributions)。
    """
    base = _build_base_segments(flat_chunks, force_split_before_paragraphs)
    return _apply_word_guideline_splits(
        base, target_words=target_words, soft_max_words=soft_max_words,
        hard_avoid_words=hard_avoid_words)


def reconstruct_article_from_segments(segments: list, paragraphs: Sequence[str]) -> str:
    """segmentsからraw段落を再構成し元記事と一致するか検証するためのヘルパ
    (Trial script群のassertと同じ目的)。空段落はそのまま維持する。"""
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = []
    for i, orig in enumerate(paragraphs):
        if orig.strip() == "":
            paras.append(orig)
        else:
            paras.append("".join(per_para.get(i, [])))
    return "\n\n".join(paras)


def build_segmentation_plan_report(segments: list) -> list:
    rows = []
    for seg in segments:
        idxs = seg["source_paragraph_indices"]
        rows.append({
            "id": seg["id"],
            "voice": seg["voice"],
            "paragraph_range": [min(idxs), max(idxs)],
            "word_count": seg["word_count"],
            "split_reason": seg["split_reason"],
            "warnings": seg.get("warnings", []),
        })
    return rows


# ============================================================
# 2. A2 Comment理解ガイド型Contract(仕様B、A2限定、B1へは適用しない)
# ============================================================

FAMILY_C_A2_COMMENT_BANNED_PATTERNS = [
    "聞いてみましょう",
    "耳を傾け",
    "耳を澄ま",
    "注目して",
    "どうなるでしょう",
]

FAMILY_C_A2_COMMENT_BANNED_PATTERNS_RE = re.compile(
    "|".join(re.escape(p) for p in FAMILY_C_A2_COMMENT_BANNED_PATTERNS))

_BANNED_PHRASES_INSTRUCTION = (
    "「聞いてみましょう」「耳を傾けて」「耳を澄ませて」「注目してみましょう」"
    "「これからどうなるでしょう」のような、聞く行為だけを促す言い回しは"
    "使わないでください。雰囲気だけの抽象的な誘導や、本文を聞けば分かる"
    "だけの無内容な予告、結末の先出し、Storyにない事実の追加、不要な長文化も"
    "避けてください。"
)

# Trial-11(`COMMENT_1_ROLE_JA_TRIAL11`)/Trial-12 Memory B1/Twinsの3記事分の
# 役割文を正本化した共通Contract。記事固有の内容(誰が・何が起きているか等)は
# `content_facts`、場面転換の説明は`scene_transition`、記事固有の表記注意
# (例: 片仮名指定)は`extra_instructions`として呼び出し側が注入する。
FAMILY_C_A2_COMMENT_ROLE_JA_1 = (
    "あなたは英語学習者向け音声番組で、物語の直前に置く短い日本語コメントを"
    "書く担当です。これから始まる物語の理解を助けるため、雰囲気作りの声かけ"
    "ではなく状況説明に徹してください。本文に書かれている事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度で簡潔にまとめて"
    "ください: {content_facts} 結末や主人公の最終的な選択には触れないで"
    "ください。新しい設定・登場人物を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION
)

FAMILY_C_A2_COMMENT_ROLE_JA_2 = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。{scene_transition}英文の理解を助けるため、"
    "雰囲気作りではなく状況整理に徹してください。本文の事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度でまとめてください: "
    "{content_facts} 結末や主人公の選択には触れないでください。新しい設定・"
    "事実を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION
)

FAMILY_C_A2_COMMENT_ROLE_JA_3 = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。{scene_transition}英文の理解を助けるため、"
    "雰囲気作りではなく状況整理に徹してください。本文の事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度でまとめてください: "
    "{content_facts} 結末(実際にどうなったか)には触れないでください。新しい"
    "設定・事実を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION
)

FAMILY_C_A2_COMMENT_ROLE_JA = {
    1: FAMILY_C_A2_COMMENT_ROLE_JA_1,
    2: FAMILY_C_A2_COMMENT_ROLE_JA_2,
    3: FAMILY_C_A2_COMMENT_ROLE_JA_3,
}


def build_family_c_a2_comment_prompt(
    comment_num: int, content_facts: str, *, scene_transition: str = "",
    extra_instructions: str = "",
) -> str:
    """comment_numは1〜3のみ(Family C既定、Comment 4なしはTrial-10から無変更)。
    B1側からこの関数を呼ぶことは想定していない(B1 Commentは既存B1 Support
    経路[`er003_v1_b1_scaffold_01_generate`]のみを使用する)。"""
    if comment_num not in FAMILY_C_A2_COMMENT_ROLE_JA:
        raise ValueError(f"FAMILY_C_A2_COMMENT_INVALID_NUMBER: comment_num={comment_num}")
    template = FAMILY_C_A2_COMMENT_ROLE_JA[comment_num]
    prompt = template.format(content_facts=content_facts, scene_transition=scene_transition)
    if extra_instructions:
        prompt = prompt + extra_instructions
    return prompt


def check_a2_comment_quality(text: "str | None", *, min_chars: int = 40, max_chars: int = 170) -> tuple:
    """禁止語句0件・空でない・文字数目安、をbool+理由listで返す。retry/
    regeneration時も本関数で判定する(初回とretryで別基準を使わない)。"""
    reasons = []
    if not text or not text.strip():
        return False, ["empty_text"]
    if FAMILY_C_A2_COMMENT_BANNED_PATTERNS_RE.search(text):
        reasons.append("banned_phrase_found")
    length = len(text.strip())
    if length < min_chars:
        reasons.append(f"too_short(chars={length}, min_chars={min_chars})")
    if length > max_chars:
        reasons.append(f"too_long(chars={length}, max_chars={max_chars})")
    return (len(reasons) == 0, reasons)


def generate_family_c_a2_comment(
    client,
    comment_num: int,
    article_text: str,
    content_facts: str,
    *,
    scene_transition: str = "",
    extra_instructions: str = "",
    budget=None,
    label_prefix: str = "family_c_a2_comment",
    max_retries: int = 1,
    llm_call_cost_jpy: float = 3.0,
    model: "str | None" = None,
    run_support_text_fn: "Callable | None" = None,
):
    """Family C A2 Comment理解ガイド型Contractの唯一の生成入口。初回生成・
    retry・regeneration・fallbackのいずれの呼び出しコード(runner側)からも
    本関数を経由する(本関数自体が禁止語句検出時の再生成ループを内包する
    ため、呼び出し側で別ロジックの「retry専用path」を持つ必要がない=
    経路によって挙動が分岐しない設計)。

    run_support_text_fn: 既定は`er003_v1_iran01_a2_generate.run_support_text`
    (Production標準A2/B1 Support生成関数)。テスト用のモック差し替えに使う。
    """
    if run_support_text_fn is None:
        import er003_v1_iran01_a2_generate as a2gen
        run_support_text_fn = a2gen.run_support_text
        if model is None:
            model = a2gen.MODEL

    prompt = build_family_c_a2_comment_prompt(
        comment_num, content_facts, scene_transition=scene_transition,
        extra_instructions=extra_instructions)
    context = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{article_text}"

    attempts = []
    for attempt in range(max_retries + 1):
        label = f"{label_prefix}_{comment_num}_llm_attempt{attempt + 1}"
        if budget is not None:
            budget.check_before(llm_call_cost_jpy, label)
        result = run_support_text_fn(client, prompt, context, model=model)
        if budget is not None:
            budget.add(label, "llm", 1, llm_call_cost_jpy, {"status": result.get("status")})
        if result.get("status") != "OK":
            attempts.append({"attempt": attempt + 1, "ok": False, "status": result.get("status")})
            continue
        text = result["text"].strip()
        ok, reasons = check_a2_comment_quality(text)
        attempts.append({"attempt": attempt + 1, "ok": ok, "reasons": reasons, "text": text})
        if ok:
            return {
                "comment_num": comment_num, "text": text, "ok": True,
                "attempts": attempts, "model": model, "prompt": prompt,
                "contract": f"FAMILY_C_A2_COMMENT_ROLE_JA_{comment_num}",
            }
    raise RuntimeError(
        f"FAMILY_C_A2_COMMENT_QUALITY_FAILED(comment_{comment_num}): "
        f"max_retries={max_retries}回のretryを尽くしても品質基準を満たせません。"
        f"attempts={attempts}")


def guard_a2_only(level: str) -> None:
    """A2 Comment理解ガイド型ContractがB1へ誤適用されないための構造的ガード。
    B1経路はこの関数を一切import・呼び出ししない設計だが、万一level="b1"で
    本Contract系関数が呼ばれた場合に備え明示的にRuntimeErrorとする。"""
    if level != "a2":
        raise RuntimeError(
            f"FAMILY_C_A2_COMMENT_CONTRACT_MISUSE: level={level!r}に対して"
            "A2 Comment理解ガイド型Contractは使用できません(B1 Commentは"
            "既存B1 Support経路[er003_v1_b1_scaffold_01_generate]のみを"
            "使用してください)。")
