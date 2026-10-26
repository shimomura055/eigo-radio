# -*- coding: utf-8 -*-
# ============================================================
# er121_family_y_structure_01.py
# FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B: Family Y 正式Production の「構造」層(純関数・API 0・import時副作用 0)
# ============================================================
# 位置づけ: Family Y Production(runner=er121_family_y_runner_01 / 音声=er121_family_y_audio_01 / テキストcore=er121_family_y_text_core_01[02A])が
#   共有する、Y固有の構造定義だけを置く(M-3: Y固有として新規に書くのは segment計画・timeline順・role文 のみ。共通工程は共通moduleを直接呼ぶ)。
#   - Y segment ID(YL-C11): y_lead / y_intro_1..3 / y_voice_1..3 / y_closing。DEV Trialのalias(full_story_part3_c2/c3)は使わない。
#     er020_tts_retry_local_rewrite_01.resolve_narrative_role がこれらをFULL_STORYへ解決する(test固定)。
#   - 5パート記事契約(YL-C01): 段落1=リード / 段落2〜4=[人物紹介行(ナレーター)\nVoice本文(本人)] / 段落5=Tension+Closing。In One Lineなし(YL-C08)。
#   - Voice固定割当(YL-C10): Algieba/Zephyr/Schedar(Z正式表 assign_dialogue_voices の結果と一致をtestで固定)。ナレーターのVoiceは
#     コードに固定せず、Xの既存Full Story設定(er003_b1_p9a_audio.VOICE_NAME)を実行時に読む(audio module)。
#   - 公開ページ注意書き(YL-C07): PAGE_NOTICE_JA(本文外・音声にアナウンスなし)。
#   - Comment 2/3のY版role文(YL-C09): DEV Trial(er110_family_y_text_trial_01.Y_COMMENT_2/3_ROLE)と逐語一致(testで固定。Productionはer110をimportしない)。
#   - Chunk TTS: Y=適用(X方式=段落単位chunk+0.2秒。ユーザー正式決定2026-10-25 USER_02 ①、APPROVED_FOR_PRODUCTION。YL-B08)。ZのB_r1方式は不採用。
#     適用可否表 CHUNK_TTS_SCOPE・Y chunk ID規則・決定記録のみここに置き、分割/生成/組立はaudit moduleが共通er117を直接importして行う。
# DEV Trial(er110_*)はimportしない(隔離: test固定)。
# ============================================================
from __future__ import annotations

import re

MANAGEMENT_ID = "FAMILY-Y-PRODUCTION-LAUNCH-01"
FAMILY = "Y"
ENTRY_STATUS = "FAMILY_Y_PRODUCTION"       # DEV Trialは DEV_TRIAL_ONLY。誤認防止のため文言を区別する

# ------------------------------------------------------------
# Y segment ID(再生順)
# ------------------------------------------------------------
Y_LEAD = "y_lead"
Y_INTRO_IDS = ("y_intro_1", "y_intro_2", "y_intro_3")
Y_VOICE_IDS = ("y_voice_1", "y_voice_2", "y_voice_3")
Y_CLOSING = "y_closing"
Y_SEGMENT_IDS = (Y_LEAD, "y_intro_1", "y_voice_1", "y_intro_2", "y_voice_2", "y_intro_3", "y_voice_3", Y_CLOSING)
Y_NARRATOR_IDS = (Y_LEAD, *Y_INTRO_IDS, Y_CLOSING)
SLOTS = ("voice_1", "voice_2", "voice_3")
SLOT_OF_ID = {"y_intro_1": "voice_1", "y_voice_1": "voice_1", "y_intro_2": "voice_2", "y_voice_2": "voice_2",
              "y_intro_3": "voice_3", "y_voice_3": "voice_3"}
Y_SEGMENT_ID_RE = re.compile(r"y_(?:lead|closing|intro_[1-3]|voice_[1-3])")

# 試聴ページの行ラベル(内部IDを出さない: er_user_listening_page_common_01._RAW_ID_RE を避ける)。「Full Story」始まりで標準適合checkの本文行判定に合う。
PAGE_LABEL = {
    "y_lead": "Full Story: Lead (Narrator)",
    "y_intro_1": "Full Story: Voice 1 Introduction (Narrator)", "y_voice_1": "Full Story: Voice 1",
    "y_intro_2": "Full Story: Voice 2 Introduction (Narrator)", "y_voice_2": "Full Story: Voice 2",
    "y_intro_3": "Full Story: Voice 3 Introduction (Narrator)", "y_voice_3": "Full Story: Voice 3",
    "y_closing": "Full Story: Closing (Narrator)",
}

# ------------------------------------------------------------
# Voice固定割当(YL-C10、ユーザー決定): Z正式表 assign_dialogue_voices の結果と一致(男女独立・登場順)
# ------------------------------------------------------------
FIXED_VOICE_SLOTS = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
ROSTER = (
    {"speaker": "voice_1", "gender": "male", "order": 1, "first_appearance": "Voice 1"},
    {"speaker": "voice_2", "gender": "female", "order": 2, "first_appearance": "Voice 2"},
    {"speaker": "voice_3", "gender": "male", "order": 3, "first_appearance": "Voice 3"},
)


class FamilyYStop(RuntimeError):
    """Family Y Productionの契約違反STOP(自動で通さない・自動再生成しない)。"""


class FamilyYStructureError(FamilyYStop):
    pass


def verify_voice_assignment() -> dict:
    """Z正式表(er062 assign_dialogue_voices)の結果が固定割当と一致することを確認する(API 0)。不一致は方式を変えずSTOP。"""
    import er062_family_z_structure_01 as z
    got = z.assign_dialogue_voices(ROSTER)
    if got != FIXED_VOICE_SLOTS:
        raise FamilyYStop(f"FAMILY_Y_VOICE_ASSIGNMENT_MISMATCH: Z正式表の割当 {got} が固定割当 {FIXED_VOICE_SLOTS} と一致しません")
    return {"z_rule_assignment": got, "y_fixed_slots": dict(FIXED_VOICE_SLOTS), "match": True}


def voice_of_segment(segment_id: str, narrator_voice: str) -> str:
    """segmentのTTS Voice。voice_n=固定割当、それ以外=ナレーター(呼出側が既存Full Story設定から読んだ値)。"""
    if segment_id in Y_VOICE_IDS:
        return FIXED_VOICE_SLOTS[SLOT_OF_ID[segment_id]]
    if segment_id in Y_NARRATOR_IDS:
        if not narrator_voice:
            raise FamilyYStop("FAMILY_Y_NARRATOR_VOICE_MISSING: ナレーターVoiceが未解決(既存Full Story設定を読めていません)")
        return narrator_voice
    raise FamilyYStop(f"FAMILY_Y_UNKNOWN_SEGMENT_ID: {segment_id!r}")


# ------------------------------------------------------------
# 公開ページ注意書き(YL-C07、本文外。音声にはアナウンスを入れない)
# ------------------------------------------------------------
PAGE_NOTICE_JA = "本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり、特定の実在人物の発言を再現したものではありません。"
PAGE_NOTICE_CLASS = "y-ai-notice"
# 音声(ナレーション)へ混入してはならない語(AI編集アナウンス廃止。単純削除でなくLead再生成で対処する=text core)
AI_ANNOUNCE_RE = re.compile(r"(実在|公開されている|公開された|ネットなど|組み立てた|組み立て|AI|人工知能|複数の意見をもと|特定の人の話)")
AI_ANNOUNCE_EN_RE = re.compile(r"\b(AI|artificial intelligence|real people|publicly available opinions|assembled from)\b", re.I)
IOL_RE = re.compile(r"(^|\n)\s*#{1,6}\s*(in one line|ひとこと)|\bIn one line\b", re.I)


def notice_html() -> str:
    """試聴ページ冒頭(本文外)の注意書き1ブロック。共通builder(render_standard_page)のintro_htmlへ渡す。X/Zページには出さない。"""
    import html
    return f"<div class='note {PAGE_NOTICE_CLASS}'>{html.escape(PAGE_NOTICE_JA)}</div>"


# ------------------------------------------------------------
# Chunk TTS適用範囲(YL-B08: ユーザー正式決定2026-10-25 USER_02 ①=Family X方式[段落分割+0.2秒]をYへ正式採用。APPROVED_FOR_PRODUCTION)
# ------------------------------------------------------------
CHUNK_TTS_SCOPE = {"X": True, "Z": True, "Y": True}
CHUNK_TTS_Y_METHOD = "X_paragraph_0.2s"          # ZのB_r1(narrator>100語分割)は採用しない(USER_02 ①)
CHUNK_TTS_Y_LEVELS = ("b1b",)                    # X同様Advanced(b1b)本文のみ。Std(a2)本文はchunk化しない
CHUNK_TTS_Y_APPROVAL_REF = "docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md §1-① (Family X方式のY正式採用、APPROVED_FOR_PRODUCTION)"
CHUNK_TTS_Y_NOTE = ("Family Y: Chunk TTSはX方式(段落単位chunk+0.2秒ポーズ)を正式採用(USER_02 ①)。分割は各Y segment(lead/intro/voice/closing)の"
                    "段落単位に限り、segment境界(話者切替=intro→voice、voice→次のintro)は結合しない。段落が1つのsegmentは分割しない(X規則どおり=従来の1 call)。")
Y_CHUNK_ID_RE = re.compile(r"(y_(?:lead|closing|intro_[1-3]|voice_[1-3]))_k([1-9][0-9]*)")


def parse_y_chunk_id(segment_id: str):
    """Y chunk id(`y_voice_1_k2`等)なら (親segment_id, index)。chunkでなければNone。"""
    m = Y_CHUNK_ID_RE.fullmatch(segment_id or "")
    return (m.group(1), int(m.group(2))) if m else None


def chunk_tts_applicable(family: str) -> bool:
    """Chunk TTS共通hookの適用判定。X/Z/Y=True(Yは2026-10-25 USER_02 ①で承認)。未知のFamilyはFalse(fail-closed)。"""
    return bool(CHUNK_TTS_SCOPE.get(family, False))


def chunk_decision_record(level: str) -> dict:
    applies = chunk_tts_applicable(FAMILY) and level in CHUNK_TTS_Y_LEVELS
    return {"family": FAMILY, "level": level, "chunk_tts_applicable": chunk_tts_applicable(FAMILY), "chunk_tts_applied_at_this_level": applies,
            "method": CHUNK_TTS_Y_METHOD, "decision": "applied_X_method", "approval": "APPROVED_FOR_PRODUCTION",
            "approval_ref": CHUNK_TTS_Y_APPROVAL_REF, "z_b_r1_adopted": False, "note": CHUNK_TTS_Y_NOTE, "ledger_ids": ["YL-B08"]}


# 中核数値保持v4/J2(YL-B05)はY対象外(承認でY/Z対象外と明記)。runnerはJ2/中核数値の入口を呼ばない(testで固定)。
CORE_NUMERIC_APPLICABLE = False


# ------------------------------------------------------------
# 5パート記事契約
# ------------------------------------------------------------
def _paragraphs(body: str) -> list:
    return [b.strip("\n") for b in re.split(r"\n\s*\n", (body or "").strip()) if b.strip()]


def split_y_article(text: str) -> dict:
    """`# タイトル`+空行区切りの5段落。段落2〜4は『紹介行\nVoice本文』の2行。違反はFamilyYStructureError(violations付き)。
    戻り値: {title, lead, voices:[{intro, body}]*3, closing, paragraphs:[5], segments:{segment_id: text}}"""
    t = (text or "").replace("\r\n", "\n").strip()
    v = []
    m = re.match(r"^#\s+(.+?)[ \t]*\n+(.*)$", t, re.S)
    if not m:
        raise FamilyYStructureError("Y_ARTICLE_TITLE_MISSING: 先頭に `# タイトル` 行がありません")
    title, rest = m.group(1).strip(), m.group(2)
    if IOL_RE.search(rest):
        v.append("IN_ONE_LINE_PRESENT(Yは廃止)")
    paras = _paragraphs(rest)
    if len(paras) != 5:
        raise FamilyYStructureError(f"Y_ARTICLE_PARAGRAPH_COUNT: 段落が5でありません(={len(paras)})")
    voices = []
    for i in (1, 2, 3):
        lines = [x.strip() for x in paras[i].split("\n") if x.strip()]
        if len(lines) != 2:
            v.append(f"VOICE_PART_{i}_NOT_2_LINES(紹介行+Voice本文の2行でありません: {len(lines)}行)")
            voices.append({"intro": lines[0] if lines else "", "body": " ".join(lines[1:])})
        else:
            voices.append({"intro": lines[0], "body": lines[1]})
    for name, txt in (("lead", paras[0]), ("closing", paras[4])):
        if "\n" in txt.strip():
            v.append(f"{name.upper()}_MULTI_LINE")
    if v:
        raise FamilyYStructureError("Y_ARTICLE_CONTRACT: " + " / ".join(v))
    seg = {Y_LEAD: paras[0].strip(), Y_CLOSING: paras[4].strip()}
    for i, vo in enumerate(voices, start=1):
        seg[f"y_intro_{i}"], seg[f"y_voice_{i}"] = vo["intro"], vo["body"]
    if any(not s.strip() for s in seg.values()):
        raise FamilyYStructureError("Y_ARTICLE_EMPTY_SEGMENT")
    return {"title": title, "lead": seg[Y_LEAD], "voices": voices, "closing": seg[Y_CLOSING], "paragraphs": paras, "segments": seg}


def check_y_article(text: str, *, lang: str) -> dict:
    """契約検査(決定論)。ok/violations。langは'ja'|'en'。音声へ混入してはならないAI告知をナレーター4種+紹介3本で検出する。"""
    try:
        p = split_y_article(text)
    except FamilyYStructureError as e:
        return {"ok": False, "violations": [str(e)]}
    v = []
    pat = AI_ANNOUNCE_RE if lang == "ja" else AI_ANNOUNCE_EN_RE
    for sid in Y_NARRATOR_IDS:
        if pat.search(p["segments"][sid]):
            v.append(f"AI_ANNOUNCE_IN_NARRATION:{sid}")
    return {"ok": not v, "violations": v}


def render_y_article(title: str, lead: str, intros: dict, voices: dict, closing: str) -> str:
    """JA組立(LLM 0)。intros/voices={slot: text}。契約を満たさなければFamilyYStructureError。"""
    paras = [lead.strip()] + [f"{intros[s].strip()}\n{voices[s].strip()}" for s in SLOTS] + [closing.strip()]
    text = f"# {title.strip()}\n\n" + "\n\n".join(paras) + "\n"
    split_y_article(text)
    return text


def canonical_body(text: str) -> str:
    """KP/Part 1等の共通入力(段落を空行で連結。タイトル行を除く)。Voice段落の紹介行+本文は1行へ結合される(clean_body_paragraphsと同じ規則)。"""
    t = (text or "").replace("\r\n", "\n").strip()
    m = re.match(r"^#\s+.+?[ \t]*\n+(.*)$", t, re.S)
    body = m.group(1) if m else t
    return "\n\n".join(" ".join(p.split()) for p in _paragraphs(body))


# ------------------------------------------------------------
# role文(YL-C09): Y版 Comment 2 / Comment 3。DEV Trial(er110_family_y_text_trial_01.Y_COMMENT_2/3_ROLE)と逐語一致(test固定)
# ------------------------------------------------------------
_LABEL_BAN = ("【重要・出力への制約】出力する文章自体に\"Part 1\"・\"Part 2\"・\"Full Story\"のような\n"
              "制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。")
_C2_COMMON = ("役割: 導入で聞いた問いの核心を1点だけ短く回収し、これから3人の違う人物が語ることを予告します。"
              "3人の立場や結論を先に言ってはいけません。新しいFactを追加しないでください。")
_C3_COMMON = ("役割: 3人の語りを聞いたうえで、「なぜ同じ問題が、それぞれにこんなに違って見えるのか」へ聞き手の視点を移します。"
              "誰が正しいかを言わず、結論を先に言ってはいけません。3人の発言を再要約しないでください。新しいFactを追加しないでください。")
# Comment 2: ユーザー正式承認(2026-10-26、USER.md §1-③)によりAdvanced(b1b)は削除。Standard(a2、日本語側)は現状維持。
# 旧b1b用role文は撤去(DEV Trial er110のY_COMMENT_2_ROLE['b1b']は旧run解析用に残るが、Productionは参照しない)。
Y_COMMENT_2_ROLE = {
    "a2": ("あなたはPodcastのナビゲーターです。リスナーは導入部分(リード)をすでに聞き終わり、これから3人の人物が順番に自分の言葉で語るのを聞きます。"
           "その間に流す、Comment 2(役割: Lead Recovery + Bridge to the Three Voices)を日本語で書いてください。\n\n"
           + _C2_COMMON + "易しい日本語で1〜2文にしてください。\n\n" + _LABEL_BAN),
}
Y_COMMENT_3_ROLE = {
    "b1b": ("あなたはPodcastのナビゲーターです。リスナーは3人の人物の語りをすべて聞き終わり、これから語り手のまとめの段落を聞きます。"
            "その間に流す、Comment 3(役割: Shift to Why They Differ)を書いてください。\n\n"
            + _C3_COMMON + "易しい英語で2〜3文にしてください。\n\n" + _LABEL_BAN),
    "a2": ("あなたはPodcastのナビゲーターです。リスナーは3人の人物の語りをすべて聞き終わり、これから語り手のまとめの段落を聞きます。"
           "その間に流す、Comment 3(役割: Shift to Why They Differ)を日本語で書いてください。\n\n"
           + _C3_COMMON + "易しい日本語で2〜3文にしてください。\n\n" + _LABEL_BAN),
}


# ------------------------------------------------------------
# support segment構成(level別)。Advanced(b1b)はComment 2なし(2026-10-26ユーザー承認)。Standard(a2)は現状維持。
# 生成・検査・TTS・組立・ページはこの1か所の定義から導出する(各所でlevel別のcomment名を直書きしない)。
# ------------------------------------------------------------
COMMENT2_REMOVED_SPEC = "2026-10-26 FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01(ユーザー正式承認: Family Y Advanced Comment 2削除)"
Y_SUPPORT_NAMES = {
    "b1b": ("preview", "comment_1", "comment_3"),
    "a2": ("preview", "comment_1", "comment_2", "comment_3"),
}
Y_REMOVED_SUPPORT_NAMES = {"b1b": ("comment_2",), "a2": ()}


def support_names(level: str) -> tuple:
    if level not in Y_SUPPORT_NAMES:
        raise KeyError(f"unknown Family Y level: {level}")
    return Y_SUPPORT_NAMES[level]


def body_comment_names(level: str) -> tuple:
    """再生順に並ぶ本文中のComment(Preview除く)。"""
    return tuple(n for n in support_names(level) if n.startswith("comment_"))


def advanced_preview_role(base_role: str) -> str:
    """Advanced(b1b)用Preview role。共有のX用PREVIEW_ROLEから、Comment 2への言及(重複回避の参照)だけを機械的に除く。
    ほかの文は1文字も変えない。置換対象が共有側から消えた/変わった場合はValueErrorで止める(黙って旧文のまま出さない)。"""
    reps = (("- 後で流れるComment 1・Comment 2と内容が重複する", "- 後で流れるComment 1と内容が重複する"),
            ("Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。", "Comment 1は以下の通りです。これと重複する内容にしないでください。"),
            ("\n\n【Comment 2】\n{comment_2}", ""))
    out = base_role
    for a, b in reps:
        if out.count(a) != 1:
            raise ValueError(f"ADVANCED_PREVIEW_ROLE_BASE_CHANGED: 置換対象が1か所ではありません: {a[:30]}")
        out = out.replace(a, b)
    if "Comment 2" in out or "comment_2" in out:
        raise ValueError("ADVANCED_PREVIEW_ROLE_COMMENT2_LEFT")
    return out


def comment_contexts(parsed_en: dict) -> dict:
    """support生成の入力文脈(LLM 0)。Comment 1=導入、Comment 2(Standardのみ。Advancedは削除済みで未使用)=導入+3人の冒頭1文、Comment 3=導入+3人の語り。Previewは全文。"""
    paras = parsed_en["paragraphs"]
    first_sentences = "\n".join("- " + re.split(r"(?<=[.!?])\s", vo["body"])[0] for vo in parsed_en["voices"])
    return {
        "comment_1": "【これから聞く本文(導入)】\n" + parsed_en["lead"],
        "comment_2": "【すでに聞いた導入】\n" + parsed_en["lead"] + "\n\n【これから聞く3人の語り(それぞれの冒頭の1文のみ)】\n" + first_sentences,
        "comment_3": "【導入】\n" + parsed_en["lead"] + "\n\n" + "\n\n".join(f"【人物{i}の語り】\n{vo['body']}" for i, vo in enumerate(parsed_en["voices"], start=1)),
        "preview": "【エピソード全文(参考、新しいFactの追加禁止)】\n# " + parsed_en["title"] + "\n\n" + "\n\n".join(paras),
    }


def y_contrast_must_fix() -> list:
    """英訳(X承認済み関数)へ渡すmust_fix欄(Prompt本体は無変更)。DEV(persona版 y5_contrast_must_fix)の5パート版から、テーマ固有の具体物の例示だけを除いた汎用版
    (テーマ固有語を共通moduleへ固定しない)。各話者の文の長さ・ためらい・問い返し・直接性・誰が話しているかを保つ。"""
    return [{"fact_id": "", "claim_in_article": "", "issue": "KEEP_SPEAKER_CONTRAST",
             "explanation": ("Paragraph 1 and paragraph 5 are spoken by a narrator. Paragraphs 2, 3 and 4 each have two lines: the first line is a short introduction "
                             "by the narrator (no first person), and the second line is spoken by one of three different people in the first person. "
                             "Keep these two lines as two separate lines within each of paragraphs 2, 3 and 4. "
                             "Keep each speaker's sentence-length contrast, hesitations, questions-back and directness, and keep who is speaking, "
                             "even when you simplify the English. Do not even out the rhythm across the paragraphs or turn them into a neutral explanation. "
                             "Keep each speaker's concrete objects and everyday words rather than abstract wording. "
                             "Do not add any new fact, event or claim.")}]


# ------------------------------------------------------------
# 実model照合(snapshot付きIDの誤STOP防止)。w62.LLM と同じ規則(返却model IDが要求モデル名で始まれば一致)
# ------------------------------------------------------------
def model_id_matches(requested: str, actual) -> bool:
    return bool(requested) and str(actual).startswith(requested)


def y_no_iol_must_fix() -> list:
    """Std(A2)生成関数のPrompt本体は『In one lineセクションを保つ』文を含むため(X承認済み、無変更)、Yの入力(IOLなし)で
    In one lineを足されないよう、既存のmust_fix欄で1文だけ明示する(Prompt本体は変更しない)。"""
    return [{"fact_id": "", "claim_in_article": "", "issue": "NO_IN_ONE_LINE_SECTION",
             "explanation": ("The source article has no 'In one line' section. Do not add an 'In one line' section or any other extra section "
                             "or heading; output only the title line and the five paragraphs.")}]


# ------------------------------------------------------------
# 公開ページ注意書きの検査(API 0)。Yページ=本文外の冒頭に1回・noindex、X/Zページ=出ない
# ------------------------------------------------------------
def page_has_notice(html_text: str) -> bool:
    return PAGE_NOTICE_CLASS in (html_text or "") or PAGE_NOTICE_JA in (html_text or "")


def check_y_page_notice(html_text: str) -> dict:
    """Yページ: 注意書きが1回だけ・最初のレベル表(table)より前(=本文外)・noindex。違反はviolationsに列挙。"""
    t = html_text or ""
    v = []
    n = t.count(PAGE_NOTICE_CLASS)
    if n != 1:
        v.append(f"NOTICE_COUNT_NOT_1(={n})")
    i_notice, i_table = t.find(PAGE_NOTICE_CLASS), t.find("<table")
    if i_notice < 0 or (i_table >= 0 and i_notice > i_table):
        v.append("NOTICE_NOT_BEFORE_BODY")
    if 'name="robots" content="noindex' not in t:
        v.append("NOINDEX_MISSING")
    return {"ok": not v, "violations": v}
