# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04B: Family Z 構造処理(LLM呼出なし、純粋関数)。

担当: 段落整形・Story 3分割の候補列挙・Dialogue話者の決定論判定と突合・clip計画(Family C
plan_story_segmentsの全文1回呼出+id改名)・Preview/Comment/KPの決定論lint。
LLM呼出・Writer鎖・CLIは er062_family_z_writer_01.py。本moduleは課金0でtestできる。

Family C(er013)は import のみ(編集しない)。Production正式path(Z)用であり、Trial/他Familyからは使わない。
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import time

import er013_family_c_production_01 as fam_c

# ------------------------------------------------------------
# story別の話者roster / 決定論話者判定keyword / Voice表 / alias(FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01b、
# Fable判定=11-8是正[Family Z仕様は一般仕様なのに実装がMelos固定だった乖離])。
# 値の出所はこのdict一箇所。er026 STORY_REGISTRY[story]の"speaker_config"はここを参照し(二重定義しない)、
# er062 writer(ATTR prompt/schema enum)・er063(Voice表/alias)はstory_keyで解決する。引数省略=Melos(従来値とバイト同一、
# testで逐語固定)。new Gate/閾値/Prompt構造の追加ではなく、roster名列挙と{main_character}等の値差替えのみ。
# dialogue_voice_tts_namesは上記の正式Voice表+決定的割当規則から導出する(値None=未割当はer063 resolveでfail-closedの保険として残す)。
# ------------------------------------------------------------
_MELOS_ATTR_ROSTER = (
    "- \"melos\": the main character, Melos (including when he speaks to the king or to his friend)\n"
    "- \"king\": the ruler / tyrant / king\n"
    "- \"friend\": Melos's friend\n"
    "- \"other\": any other speaker (a guard, bandits, a sister, a crowd, etc.)\n"
    "- \"narrator\": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)")
_MELOS_ATTR_CAUTION = (
    "Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in "
    "'\"I will return,\" Melos told the king.' the speaker is melos, not king; in '\"I am here,\" he said to his friend.' "
    "decide who \"he\" is from the story).")

# ------------------------------------------------------------
# Family Z 登場人物Voice 正式表と決定的割当規則(FAMILY-Z-VOICE-PRODUCTION-WIRING-01 委任_01、
# ユーザー最終決定2026-10-23 APPROVED_FOR_PRODUCTION、原文=docs/pm/delegation_log/2026-10-23_FAMILY-Z-VOICE-PRODUCTION-WIRING-01_USER.md。
# 割当方針=2026-10-21ユーザー指示§4: 男女独立・登場順・6人目以降は循環・同一人物は作品全体で同一Voice)。
# Narrator=Aoede、Advanced補助=Charonは別枠で登場人物用プールに含めない。性別・登場順はrosterの明示データ
# (名前からの推測・LLM判定はしない)。割当は純粋関数で、resume時に再計算しても同一になる。
# ------------------------------------------------------------
FAMILY_Z_NARRATOR_VOICE = "Aoede"
FAMILY_Z_ADVANCED_AUX_VOICE = "Charon"
FAMILY_Z_DIALOGUE_VOICE_POOL = {
    "male": ("Algieba", "Schedar", "Fenrir", "Orus", "Puck"),
    "female": ("Zephyr", "Kore", "Leda", "Sulafat", "Erinome"),
}
FAMILY_Z_VOICE_STATUS = "APPROVED_FOR_PRODUCTION(2026-10-23ユーザー最終決定)"

# story別roster: speaker=話者key(STORY_SPEAKER_CONFIG speakers/dialogue_voice_tts_namesのkey)、gender=male|female、
# order=作品内の初出順(1始まり、story内一意)、first_appearance=根拠(本文上の初出箇所)。
STORY_VOICE_ROSTER = {
    "melos": (
        {"speaker": "melos", "gender": "male", "order": 1, "first_appearance": "Adv q0_1(王への最初の発話)"},
        {"speaker": "dionysius", "gender": "male", "order": 2, "first_appearance": "Adv q3_1(王=king、友を人質に置く発話)"},
        {"speaker": "selinuntius", "gender": "male", "order": 3, "first_appearance": "Adv q5_1(友=friend、'Go.')"},
    ),
    "the_open_window": (
        {"speaker": "vera", "gender": "female", "order": 1, "first_appearance": "冒頭の最初の引用('My aunt will come downstairs...'を言う15歳の少女)"},
        {"speaker": "framton", "gender": "male", "order": 2, "first_appearance": "2番目の引用('I don't really know anything about her.')"},
        {"speaker": "mrs_sappleton", "gender": "female", "order": 3, "first_appearance": "叔母の登場後の引用('I hope you've enjoyed talking to my niece...')"},
        {"speaker": "men", "gender": "male", "order": 4, "first_appearance": "狩りから戻る男たち(歌声'Oh, brother...'・夫の'Who's the man...')"},
    ),
    "after_twenty_years": (
        {"speaker": "bob", "gender": "male", "order": 1, "first_appearance": "冒頭の最初の引用(店の戸口で待つ男Bob『It's all right, officer.』)"},
        {"speaker": "patrolman", "gender": "male", "order": 2, "first_appearance": "2番目の引用(巡回中の警官『Until five years ago.』。正体はJimmyで、最後の手紙の書き手と同一人物=同一Voice)"},
        {"speaker": "detective", "gender": "male", "order": 3, "first_appearance": "3番目の話者(長いオーバーコートの背の高い男=私服刑事『Is that you, Bob?』)"},
    ),    "the_gift_of_the_magi": (
        {"speaker": "della", "gender": "female", "order": 1, "first_appearance": "主人公の妻Della(Madameに『Will you buy my hair?』と尋ねる、またはJimへの呼びかけ。作品の中心人物)"},
        {"speaker": "madame", "gender": "female", "order": 2, "first_appearance": "髪を買うMadame Sofronie(髪飾り店の女主人。『I buy hair.』『Twenty dollars.』)"},
        {"speaker": "jim", "gender": "male", "order": 3, "first_appearance": "夫Jim(部屋に入りDellaの髪を見て『You've cut off your hair?』と言う。唯一の男性話者で男性Poolの1番目)"},
    ),
    "the_monkeys_paw": (
        {"speaker": "morris", "gender": "male", "order": 1, "first_appearance": "Adv/Std冒頭の最初の引用(猿の手を持参した退役軍曹[the sergeant-major]『It grants three wishes』。警告者)"},
        {"speaker": "mr_white", "gender": "male", "order": 2, "first_appearance": "2番目の引用(父Mr. White、『Have you used it?』。三つの願いを唱える主人公)"},
        {"speaker": "herbert", "gender": "male", "order": 3, "first_appearance": "3番目の話者(息子Herbert、『Ask for two hundred pounds, Father!』)"},
        {"speaker": "visitor", "gender": "male", "order": 4, "first_appearance": "翌日訪れる会社の使者(Herbertの事故と200ポンドを告げる男)"},
        {"speaker": "mrs_white", "gender": "female", "order": 5, "first_appearance": "唯一の女性話者・母Mrs. White(『The paw! We have two wishes left.』。女性Poolの1番目)"},
    ),
    # 『告げ口心臓』: 一人称語り。語り手(名なし)自身の台詞はnarrator(Aoede)。会話話者は老人と警官のみ(男性2名)。
    "the_tell_tale_heart": (
        {"speaker": "old_man", "gender": "male", "order": 1, "first_appearance": "8夜目に目を覚まし『Who's there?』と叫ぶ老人(唯一の最初の他者発話。Writer出力の初出順確認後にplan前に訂正し得る)"},
        {"speaker": "officer", "gender": "male", "order": 2, "first_appearance": "夜明け前に訪れる3人の警官(原作では会話をほぼ直接話法で書かない。Writerが台詞化した場合の話者)"},
    ),
    # 『藪の中』(芥川龍之介、FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01、data表の値追加のみ)。語り手不在の7証言集。narrator枠=証言者の紹介のみ(Aoede)。
    # 証言者7名=男5(木樵り・旅法師・放免・多襄丸・武弘)+女2(媼・真砂)。男性Pool5名ちょうど(循環なし)。巫女は口寄せの媒体であり話者は武弘(死霊)。
    # 初出順は原作の証言順(Writer出力の初出順確認後にplan前に訂正し得る。Writerが一部証言者を省略した場合も同様)。
    "in_a_grove": (
        {"speaker": "woodcutter", "gender": "male", "order": 1, "first_appearance": "最初の証言者(死骸を見つけた木樵り、『I found the body this morning』)"},
        {"speaker": "monk", "gender": "male", "order": 2, "first_appearance": "2番目の証言者(前日に夫婦と出会った旅法師)"},
        {"speaker": "constable", "gender": "male", "order": 3, "first_appearance": "3番目の証言者(多襄丸を捕えた放免=constable)"},
        {"speaker": "old_woman", "gender": "female", "order": 4, "first_appearance": "4番目の証言者(真砂の母=媼)。女性Poolの1番目"},
        {"speaker": "tajomaru", "gender": "male", "order": 5, "first_appearance": "5番目の証言者(盗人多襄丸の白状)"},
        {"speaker": "masago", "gender": "female", "order": 6, "first_appearance": "6番目の証言者(清水寺に来れる女=真砂の懺悔)。女性Poolの2番目"},
        {"speaker": "takehiro", "gender": "male", "order": 7, "first_appearance": "最後の証言者(巫女の口を借りて語る夫・武弘の死霊)"},
    ),
}
# 作品単位のpin(既存確定値の固定)。メロスは2026-10-21 U:§7「メロス完成版は変更しない」により受入済み成果物のVoiceを
# 変更しない(pin値=受入済みfamily_z_melos_02の実使用値。規則適用値との差分は仕様差分として報告済み・変更はユーザー承認事項)。
STORY_VOICE_PINS = {
    "melos": {
        "melos": "Algieba",
        "selinuntius": "Erinome",
        "dionysius": "Charon",
    },
}
# 作品限定のNarrator(本文を語る声)Voice pin(FZ-TELL-TALE-HEART-NARRATOR-VOICE-01、2026-10-28ユーザー正式決定APPROVED_FOR_PRODUCTION。Schedar→Fenrirへ修正[警官役Schedarと重複回避。USER_02]、
# 原文=docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER_02.md §2 + 2026-10-28_FZ-TELL-TALE-HEART-NARRATOR-VOICE-01_USER_02.md)。Family Z共通Voiceルール化しない(他storyは従来のAoede)。
# 対象=本文narration clip(speaker=narrator、full_story_*)のみ。intro/preview/comment/KP/JA/Shellの割当(er063 role表)は変更しない。
STORY_NARRATOR_VOICE_PINS = {
    "the_tell_tale_heart": "Fenrir",
}


def narrator_voice_for(story_key: str) -> str:
    return STORY_NARRATOR_VOICE_PINS.get(story_key, FAMILY_Z_NARRATOR_VOICE)


STORY_VOICE_PIN_REASON = {
    "melos": "2026-10-21 U:§7 メロス完成版(受入済みpage family_z_melos_02)のVoiceは変更しない",
}


def assign_dialogue_voices(roster, pool=None) -> dict:
    """決定的割当(純粋関数)。男女独立に、order昇順で pool[gender][(n-1) % len] を割り当てる(6人目以降は循環)。
    入力=rosterの明示データ(speaker/gender/order)。出力={speaker: voice}(Narrator/Charonは含めない)。"""
    pool = pool or FAMILY_Z_DIALOGUE_VOICE_POOL
    seen_speakers, seen_orders = set(), set()
    for r in roster:
        if r["gender"] not in pool:
            raise ValueError(f"UNKNOWN_GENDER: {r['speaker']!r} gender={r['gender']!r}(male|femaleの明示データが必要)")
        if r["speaker"] in seen_speakers or r["order"] in seen_orders:
            raise ValueError(f"ROSTER_DUPLICATE: speaker/orderが重複 {r!r}")
        seen_speakers.add(r["speaker"])
        seen_orders.add(r["order"])
    out = {}
    for gender in pool:
        members = sorted((r for r in roster if r["gender"] == gender), key=lambda r: r["order"])
        for i, r in enumerate(members):
            out[r["speaker"]] = pool[gender][i % len(pool[gender])]
    return out


def derive_voice_assignment(story_key: str) -> dict:
    """story別のVoice割当記録(run metadata `voice_assignment.json` の中身)。規則適用値→pin上書き→最終値。"""
    roster = STORY_VOICE_ROSTER[story_key]
    rule = assign_dialogue_voices(roster)
    pins = STORY_VOICE_PINS.get(story_key, {})
    unknown = set(pins) - set(rule)
    if unknown:
        raise ValueError(f"PIN_SPEAKER_NOT_IN_ROSTER: {sorted(unknown)}")
    rows = []
    for r in sorted(roster, key=lambda r: r["order"]):
        sp = r["speaker"]
        final = pins.get(sp, rule[sp])
        rows.append({"speaker": sp, "gender": r["gender"], "order": r["order"], "first_appearance": r["first_appearance"],
                     "rule_voice": rule[sp], "pinned": sp in pins, "voice": final})
    rec = {"story_key": story_key, "status": FAMILY_Z_VOICE_STATUS, "narrator_voice": narrator_voice_for(story_key),
           "pool": {k: list(v) for k, v in FAMILY_Z_DIALOGUE_VOICE_POOL.items()},
           "pin_reason": STORY_VOICE_PIN_REASON.get(story_key) if pins else None, "speakers": rows}
    if story_key in STORY_NARRATOR_VOICE_PINS:   # 作品限定pinの作品だけ追記(他storyの記録はバイト不変)
        rec["narrator_voice_pin"] = {"voice": STORY_NARRATOR_VOICE_PINS[story_key], "default_narrator_voice": FAMILY_Z_NARRATOR_VOICE,
                                     "status": "APPROVED_FOR_PRODUCTION(2026-10-28ユーザー正式決定、本作品限定、Family Z共通ルール化しない)",
                                     "source": "docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER_02.md §2",
                                     "scope": "本文narration clip(speaker=narrator、full_story_*)のみ。intro/preview/comment/KP/JA/ShellのVoiceは変更しない"}
    return rec


def derive_dialogue_voice_tts_names(story_key: str) -> dict:
    """STORY_SPEAKER_CONFIG[story]["dialogue_voice_tts_names"] の導出(narrator + roster全員。値None=未割当は残さない)。"""
    names = {"narrator": narrator_voice_for(story_key)}
    for row in derive_voice_assignment(story_key)["speakers"]:
        names[row["speaker"]] = row["voice"]
    return names


STORY_SPEAKER_CONFIG = {
    "melos": {
        "speakers": ("melos", "king", "friend", "other", "narrator"),
        # Family C keyword窓判定用(挿入順に判定、最初に一致したvoice)。keywordに無い語(he/she等)は
        # default=narrator(=「決定論は判定不能」)になり、LLM判定のみで確定する(llm_only)。
        "z_voice_keywords": {
            "melos": ["melos"],
            "king": ["ruler", "king", "tyrant"],
            "friend": ["friend"],
        },
        "attr_roster_text": _MELOS_ATTR_ROSTER,
        "attr_caution_text": _MELOS_ATTR_CAUTION,
        # er063 Voice表(挿入順=判定優先順。Melos台詞を王/友への言及より優先する)。
        "dialogue_voice_keywords": {
            "melos": ["melos"],
            "selinuntius": ["selinuntius", "friend"],
            "dionysius": ["dionysius", "ruler", "king", "tyrant"],
        },
        # 規則適用+作品単位pin(メロスは既存確定値固定)から導出。値の出所=STORY_VOICE_ROSTER/STORY_VOICE_PINS。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("melos"),
        "speaker_aliases": {"king": "dionysius", "friend": "selinuntius", "melos": "melos", "narrator": "narrator",
                            "dionysius": "dionysius", "selinuntius": "selinuntius"},
    },
    # 『開いた窓』(Saki)。主人公Framton Nuttel(男)、姪Vera(女)、叔母Mrs. Sappleton(女)、男性端役[叔母の夫・弟Ronnie等、歌声含む](men、男性グループ1話者)。Voiceは導出(roster/規則参照)。"other"は想定外話者(Melos同様STOP)。
    "the_open_window": {
        "speakers": ("framton", "vera", "mrs_sappleton", "men", "other", "narrator"),
        "z_voice_keywords": {
            "framton": ["framton", "nuttel", "visitor"],
            "vera": ["vera", "niece", "girl"],
            "mrs_sappleton": ["sappleton", "aunt"],
            "men": ["ronnie", "brother", "husband"],
        },
        "attr_roster_text": (
            "- \"framton\": the main character, Framton Nuttel, the nervous visitor\n"
            "- \"vera\": Vera, the fifteen-year-old niece of Mrs. Sappleton (\"the girl\", \"the niece\")\n"
            "- \"mrs_sappleton\": Mrs. Sappleton, Vera's aunt, the lady of the house\n"
            "- \"men\": the men of the house: Mrs. Sappleton's husband and her brothers (including Ronnie), including the song one of them sings\n"
            "- \"other\": any other speaker (a servant, a stranger, a crowd, etc.)\n"
            "- \"narrator\": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)"),
        "attr_caution_text": (
            "Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"My aunt will be down presently,\" said Vera to Framton.' the speaker is vera, not framton; in "
            "'\"I hope Vera has been amusing you,\" she said to the visitor.' decide who \"she\" is from the story)."),
        "dialogue_voice_keywords": {
            "framton": ["framton", "nuttel", "visitor"],
            "vera": ["vera", "niece", "girl"],
            "mrs_sappleton": ["sappleton", "aunt"],
            "men": ["ronnie", "brother", "husband"],
        },
        # 正式Voice表+決定的割当規則から導出(Mrs. Sappletonを含む。未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("the_open_window"),
        "speaker_aliases": {"framton": "framton", "vera": "vera", "mrs_sappleton": "mrs_sappleton", "men": "men",
                            "narrator": "narrator"},
    },
    # 『二十年後』(O. Henry、FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_02、data表の値追加のみ)。待つ男Bob(男)、巡回中の警官=Jimmy Wells(男。最後の手紙の書き手と同一人物で同一Voice)、私服刑事(男)。
    # Voiceは導出(roster/規則参照)。"other"は想定外話者(Melos同様STOP)。
    "after_twenty_years": {
        "speakers": ("bob", "patrolman", "detective", "other", "narrator"),
        # 挿入順=判定優先順。detectiveを先頭にする(『Bob』宛の呼びかけを含む同一段落で'the tall man replied'の台詞がBobと誤判定される
        # addressee_keyword型の誤りを避ける。2026-10-23 plan実行で観測)。
        "z_voice_keywords": {
            "detective": ["detective", "tall man", "plain clothes", "plain-clothes"],
            "bob": ["bob"],
            "patrolman": ["patrolman", "policeman", "officer", "jimmy"],
        },
        "attr_roster_text": (
            "- \"bob\": Bob, the man from the West who waits in the doorway for his old friend\n"
            "- \"patrolman\": the patrolman on the beat who talks with Bob and walks on; also the writer of the final note signed Jimmy (the note is spoken in this voice)\n"
            "- \"detective\": the tall man in the long overcoat, a plain clothes officer who pretends to be Jimmy and arrests Bob\n"
            "- \"other\": any other speaker (a stranger, a crowd, etc.)\n"
            "- \"narrator\": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)"),
        "attr_caution_text": (
            "Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"Is that you, Jimmy Wells?\" cried the man in the door.' the speaker is bob, and the tall man who answers him is the detective; "
            "the text of the note that ends the story is written by the patrolman, signed Jimmy)."),
        "dialogue_voice_keywords": {
            "detective": ["detective", "tall man", "plain clothes", "plain-clothes"],
            "bob": ["bob"],
            "patrolman": ["patrolman", "policeman", "officer", "jimmy"],
        },
        # 正式Voice表+決定的割当規則から導出(未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("after_twenty_years"),
        "speaker_aliases": {"bob": "bob", "patrolman": "patrolman", "detective": "detective", "narrator": "narrator",
                            "jimmy": "patrolman"},
    },    # 『賢者の贈り物』(O. Henry、FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01、data表の値追加のみ)。妻Della(女)、夫Jim(男)、髪を買うMadame Sofronie(女)。
    # Voiceは導出(roster/規則参照)。"other"は想定外話者(Melos同様STOP)。
    "the_gift_of_the_magi": {
        "speakers": ("della", "madame", "jim", "other", "narrator"),
        # 挿入順=判定優先順(madame->della->jim)。
        "z_voice_keywords": {
            "madame": ["madame", "sofronie"],
            "della": ["della"],
            "jim": ["jim"],
        },
        "attr_roster_text": (
            "- \"della\": Della, the young wife who sells her hair on Christmas Eve to buy a gift for her husband\n"
            "- \"madame\": Madame Sofronie, the owner of the hair-goods shop who buys Della's hair\n"
            "- \"jim\": Jim, Della's husband (also when Della calls him 'Jim' or 'boy')\n"
            "- \"other\": any other speaker (a stranger, a crowd, etc.)\n"
            "- \"narrator\": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)"),
        "attr_caution_text": (
            "Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"Jim, darling,\" she cried.' the speaker is della, who is speaking TO Jim; in '\"Dell,\" said he, \"let's put our "
            "Christmas presents away.\"' the speaker is jim, who is speaking TO Della; in '\"Will you buy my hair?\" asked Della.' "
            "the speaker is della and the answer '\"I buy hair,\" said Madame.' is madame)."),
        "dialogue_voice_keywords": {
            "madame": ["madame", "sofronie"],
            "della": ["della"],
            "jim": ["jim"],
        },
        # 正式Voice表+決定的割当規則から導出(未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("the_gift_of_the_magi"),
        "speaker_aliases": {"della": "della", "madame": "madame", "jim": "jim", "narrator": "narrator"},
    },
    # 『猿の手』(W. W. Jacobs、FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01、data表の値追加のみ)。父Mr. White(男)、息子Herbert(男)、母Mrs. White(女)、
    # 退役軍曹Morris(男、猿の手の持ち主)、Maw and Megginsの使者(男)。Voiceは導出(roster/規則参照)。"other"は想定外話者(Melos同様STOP)。
    "the_monkeys_paw": {
        "speakers": ("mr_white", "herbert", "mrs_white", "morris", "visitor", "other", "narrator"),
        # 挿入順=判定優先順(mrs_white->mr_white->herbert->morris->visitor)。決定論は明示的な呼称のみ。
        "z_voice_keywords": {
            "mrs_white": ["mrs. white said", "said mrs. white", "mrs. white asked", "asked mrs. white", "mrs. white cried", "cried mrs. white", "mrs. white replied", "replied mrs. white", "mrs. white warned", "warned mrs. white", "mrs. white joked", "joked mrs. white", "mrs. white whispered", "whispered mrs. white", "mrs. white shouted", "shouted mrs. white", "mrs. white added", "added mrs. white"],
            "mr_white": ["mr. white said", "said mr. white", "mr. white asked", "asked mr. white", "mr. white cried", "cried mr. white", "mr. white replied", "replied mr. white", "mr. white warned", "warned mr. white", "mr. white joked", "joked mr. white", "mr. white whispered", "whispered mr. white", "mr. white shouted", "shouted mr. white", "mr. white added", "added mr. white"],
            "herbert": ["herbert said", "said herbert", "herbert asked", "asked herbert", "herbert cried", "cried herbert", "herbert replied", "replied herbert", "herbert warned", "warned herbert", "herbert joked", "joked herbert", "herbert whispered", "whispered herbert", "herbert shouted", "shouted herbert", "herbert added", "added herbert"],
            "morris": ["the sergeant-major said", "said the sergeant-major", "the sergeant-major asked", "asked the sergeant-major", "the sergeant-major cried", "cried the sergeant-major", "the sergeant-major replied", "replied the sergeant-major", "the sergeant-major warned", "warned the sergeant-major", "the sergeant-major joked", "joked the sergeant-major", "the sergeant-major whispered", "whispered the sergeant-major", "the sergeant-major shouted", "shouted the sergeant-major", "the sergeant-major added", "added the sergeant-major", "the soldier said", "said the soldier", "the soldier asked", "asked the soldier", "the soldier cried", "cried the soldier", "the soldier replied", "replied the soldier", "the soldier warned", "warned the soldier", "the soldier joked", "joked the soldier", "the soldier whispered", "whispered the soldier", "the soldier shouted", "shouted the soldier", "the soldier added", "added the soldier"],
            "visitor": ["the man said", "said the man", "the man asked", "asked the man", "the man cried", "cried the man", "the man replied", "replied the man", "the man warned", "warned the man", "the man joked", "joked the man", "the man whispered", "whispered the man", "the man shouted", "shouted the man", "the man added", "added the man", "the stranger said", "said the stranger", "the stranger asked", "asked the stranger", "the stranger cried", "cried the stranger", "the stranger replied", "replied the stranger", "the stranger warned", "warned the stranger", "the stranger joked", "joked the stranger", "the stranger whispered", "whispered the stranger", "the stranger shouted", "shouted the stranger", "the stranger added", "added the stranger", "the visitor said", "said the visitor", "the visitor asked", "asked the visitor", "the visitor cried", "cried the visitor", "the visitor replied", "replied the visitor", "the visitor warned", "warned the visitor", "the visitor joked", "joked the visitor", "the visitor whispered", "whispered the visitor", "the visitor shouted", "shouted the visitor", "the visitor added", "added the visitor"],
        },
        "attr_roster_text": (
            "- \"mr_white\": Mr. White, the father of the family who owns the monkey's paw and makes the wishes (also 'father', 'the old man', 'her husband')\n"
            "- \"herbert\": Herbert, the Whites' grown son (also 'the son')\n"
            "- \"mrs_white\": Mrs. White, Herbert's mother and Mr. White's wife (also 'mother', 'the old woman', 'the old lady', 'his wife')\n"
            "- \"morris\": Sergeant-Major Morris, the old soldier who brings the monkey's paw and warns the family (also 'the sergeant-major', 'the soldier', 'the old friend')\n"
            "- \"visitor\": the stranger from the firm Maw and Meggins who brings the news about Herbert\n"
            "- \"other\": any other speaker (a crowd, etc.)\n"
            "- \"narrator\": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)"),
        "attr_caution_text": (
            "Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"Herbert will have some more of his funny remarks,\" she said.' the speaker is mrs_white, who is speaking ABOUT Herbert; in "
            "'\"Better where you are,\" said the sergeant-major, shaking his head.' the speaker is morris; in "
            "'\"I wish my son alive again,\" he said.' the speaker is mr_white; decide who \"he\" and \"she\" are from the story)."),
        "dialogue_voice_keywords": {
            "mrs_white": ["mrs. white said", "said mrs. white", "mrs. white asked", "asked mrs. white", "mrs. white cried", "cried mrs. white", "mrs. white replied", "replied mrs. white", "mrs. white warned", "warned mrs. white", "mrs. white joked", "joked mrs. white", "mrs. white whispered", "whispered mrs. white", "mrs. white shouted", "shouted mrs. white", "mrs. white added", "added mrs. white"],
            "mr_white": ["mr. white said", "said mr. white", "mr. white asked", "asked mr. white", "mr. white cried", "cried mr. white", "mr. white replied", "replied mr. white", "mr. white warned", "warned mr. white", "mr. white joked", "joked mr. white", "mr. white whispered", "whispered mr. white", "mr. white shouted", "shouted mr. white", "mr. white added", "added mr. white"],
            "herbert": ["herbert said", "said herbert", "herbert asked", "asked herbert", "herbert cried", "cried herbert", "herbert replied", "replied herbert", "herbert warned", "warned herbert", "herbert joked", "joked herbert", "herbert whispered", "whispered herbert", "herbert shouted", "shouted herbert", "herbert added", "added herbert"],
            "morris": ["the sergeant-major said", "said the sergeant-major", "the sergeant-major asked", "asked the sergeant-major", "the sergeant-major cried", "cried the sergeant-major", "the sergeant-major replied", "replied the sergeant-major", "the sergeant-major warned", "warned the sergeant-major", "the sergeant-major joked", "joked the sergeant-major", "the sergeant-major whispered", "whispered the sergeant-major", "the sergeant-major shouted", "shouted the sergeant-major", "the sergeant-major added", "added the sergeant-major", "the soldier said", "said the soldier", "the soldier asked", "asked the soldier", "the soldier cried", "cried the soldier", "the soldier replied", "replied the soldier", "the soldier warned", "warned the soldier", "the soldier joked", "joked the soldier", "the soldier whispered", "whispered the soldier", "the soldier shouted", "shouted the soldier", "the soldier added", "added the soldier"],
            "visitor": ["the man said", "said the man", "the man asked", "asked the man", "the man cried", "cried the man", "the man replied", "replied the man", "the man warned", "warned the man", "the man joked", "joked the man", "the man whispered", "whispered the man", "the man shouted", "shouted the man", "the man added", "added the man", "the stranger said", "said the stranger", "the stranger asked", "asked the stranger", "the stranger cried", "cried the stranger", "the stranger replied", "replied the stranger", "the stranger warned", "warned the stranger", "the stranger joked", "joked the stranger", "the stranger whispered", "whispered the stranger", "the stranger shouted", "shouted the stranger", "the stranger added", "added the stranger", "the visitor said", "said the visitor", "the visitor asked", "asked the visitor", "the visitor cried", "cried the visitor", "the visitor replied", "replied the visitor", "the visitor warned", "warned the visitor", "the visitor joked", "joked the visitor", "the visitor whispered", "whispered the visitor", "the visitor shouted", "shouted the visitor", "the visitor added", "added the visitor"],
        },
        # 正式Voice表+決定的割当規則から導出(未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("the_monkeys_paw"),
        "speaker_aliases": {"mr_white": "mr_white", "herbert": "herbert", "mrs_white": "mrs_white", "morris": "morris",
                            "visitor": "visitor", "narrator": "narrator"},
    },
    # 『告げ口心臓』(E. A. Poe、FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_01、data表の値追加のみ)。一人称の語り手(名なし)・老人(男)・警官(男、3人まとめて1話者)。
    # 語り手自身の引用台詞(Villains!...等)はnarrator(Aoede)が読む(一人称語りの地の文と同一人物のため)。Voiceは導出(roster/規則参照)。"other"は想定外話者(Melos同様STOP)。
    "the_tell_tale_heart": {
        "speakers": ("old_man", "officer", "other", "narrator"),
        # 挿入順=判定優先順(old_man->officer)。決定論は明示的な呼称のみ。語り手本人(I)は決定論の対象外(narrator)。
        "z_voice_keywords": {
            "old_man": ["the old man said", "said the old man", "the old man asked", "asked the old man", "the old man cried", "cried the old man", "the old man replied", "replied the old man", "the old man whispered", "whispered the old man", "the old man shouted", "shouted the old man", "the old man added", "added the old man", "the old man called", "called the old man", "the old man answered", "answered the old man"],
            "officer": ["the officer said", "said the officer", "the officer asked", "asked the officer", "the officer cried", "cried the officer", "the officer replied", "replied the officer", "the officer whispered", "whispered the officer", "the officer shouted", "shouted the officer", "the officer added", "added the officer", "the officer called", "called the officer", "the officer answered", "answered the officer", "one of the officers said", "said one of the officers", "one of the officers asked", "asked one of the officers", "one of the officers cried", "cried one of the officers", "one of the officers replied", "replied one of the officers", "one of the officers whispered", "whispered one of the officers", "one of the officers shouted", "shouted one of the officers", "one of the officers added", "added one of the officers", "one of the officers called", "called one of the officers", "one of the officers answered", "answered one of the officers", "the policeman said", "said the policeman", "the policeman asked", "asked the policeman", "the policeman cried", "cried the policeman", "the policeman replied", "replied the policeman", "the policeman whispered", "whispered the policeman", "the policeman shouted", "shouted the policeman", "the policeman added", "added the policeman", "the policeman called", "called the policeman", "the policeman answered", "answered the policeman", "the police officer said", "said the police officer", "the police officer asked", "asked the police officer", "the police officer cried", "cried the police officer", "the police officer replied", "replied the police officer", "the police officer whispered", "whispered the police officer", "the police officer shouted", "shouted the police officer", "the police officer added", "added the police officer", "the police officer called", "called the police officer", "the police officer answered", "answered the police officer", "the detective said", "said the detective", "the detective asked", "asked the detective", "the detective cried", "cried the detective", "the detective replied", "replied the detective", "the detective whispered", "whispered the detective", "the detective shouted", "shouted the detective", "the detective added", "added the detective", "the detective called", "called the detective", "the detective answered", "answered the detective"],
        },
        "attr_roster_text": (
            "- \"old_man\": the old man whom the narrator watches at night and kills (also 'the old fellow'; he speaks, for example, 'Who's there?')\n"
            "- \"officer\": one of the police officers who come in the early morning to search the house (also 'the officers', 'the policemen', 'the men')\n"
            "- \"other\": any other speaker (a neighbour, a crowd, etc.)\n"
            "- \"narrator\": the first-person narrator himself, the 'I' of the story, whose own spoken words are read in the narrator voice (for example, 'Villains!' I shrieked); also a line not spoken by a character"),
        "attr_caution_text": (
            "Be careful: this story is told by the narrator in the first person, so '\"Villains!\" I shrieked' and '\"Who's there?\"' differ: the first is the narrator himself (narrator), the second is the old man (old_man) "
            "even if a nearby sentence says 'I'; a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"Who's there?\" cried the old man.' the speaker is old_man; in 'The officers asked, \"Who lives here?\"' the speaker is officer; in "
            "'I said, \"It was a dream.\"' the speaker is the narrator)."),
        "dialogue_voice_keywords": {
            "old_man": ["the old man said", "said the old man", "the old man asked", "asked the old man", "the old man cried", "cried the old man", "the old man replied", "replied the old man", "the old man whispered", "whispered the old man", "the old man shouted", "shouted the old man", "the old man added", "added the old man", "the old man called", "called the old man", "the old man answered", "answered the old man"],
            "officer": ["the officer said", "said the officer", "the officer asked", "asked the officer", "the officer cried", "cried the officer", "the officer replied", "replied the officer", "the officer whispered", "whispered the officer", "the officer shouted", "shouted the officer", "the officer added", "added the officer", "the officer called", "called the officer", "the officer answered", "answered the officer", "one of the officers said", "said one of the officers", "one of the officers asked", "asked one of the officers", "one of the officers cried", "cried one of the officers", "one of the officers replied", "replied one of the officers", "one of the officers whispered", "whispered one of the officers", "one of the officers shouted", "shouted one of the officers", "one of the officers added", "added one of the officers", "one of the officers called", "called one of the officers", "one of the officers answered", "answered one of the officers", "the policeman said", "said the policeman", "the policeman asked", "asked the policeman", "the policeman cried", "cried the policeman", "the policeman replied", "replied the policeman", "the policeman whispered", "whispered the policeman", "the policeman shouted", "shouted the policeman", "the policeman added", "added the policeman", "the policeman called", "called the policeman", "the policeman answered", "answered the policeman", "the police officer said", "said the police officer", "the police officer asked", "asked the police officer", "the police officer cried", "cried the police officer", "the police officer replied", "replied the police officer", "the police officer whispered", "whispered the police officer", "the police officer shouted", "shouted the police officer", "the police officer added", "added the police officer", "the police officer called", "called the police officer", "the police officer answered", "answered the police officer", "the detective said", "said the detective", "the detective asked", "asked the detective", "the detective cried", "cried the detective", "the detective replied", "replied the detective", "the detective whispered", "whispered the detective", "the detective shouted", "shouted the detective", "the detective added", "added the detective", "the detective called", "called the detective", "the detective answered", "answered the detective"],
        },
        # 正式Voice表+決定的割当規則から導出(未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("the_tell_tale_heart"),
        "speaker_aliases": {"old_man": "old_man", "officer": "officer", "narrator": "narrator"},
    },
    # 『藪の中』(芥川龍之介、FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01、data表の値追加のみ)。7証言者(木樵り・旅法師・放免・媼・多襄丸・真砂・武弘の死霊)+narrator(証言者紹介のみ)。
    # 決定論は明示的な呼称のみ(挿入順=判定優先順: old_woman->masago->woodcutter->monk->constable->tajomaru->takehiro)。証言者本人の「I」はspeech tagの呼称で決まる。
    "in_a_grove": {
        "speakers": ("woodcutter", "monk", "constable", "old_woman", "tajomaru", "masago", "takehiro", "other", "narrator"),
        "z_voice_keywords": {
            "old_woman": ["the old woman said", "said the old woman", "the old woman asked", "asked the old woman", "the old woman replied", "replied the old woman", "the old woman answered", "answered the old woman", "the old woman cried", "cried the old woman", "the old woman whispered", "whispered the old woman", "the old woman added", "added the old woman", "the old woman testified", "testified the old woman", "the old woman declared", "declared the old woman", "the old woman began", "began the old woman", "the old woman continued", "continued the old woman", "the old mother said", "said the old mother", "the old mother asked", "asked the old mother", "the old mother replied", "replied the old mother", "the old mother answered", "answered the old mother", "the old mother cried", "cried the old mother", "the old mother whispered", "whispered the old mother", "the old mother added", "added the old mother", "the old mother testified", "testified the old mother", "the old mother declared", "declared the old mother", "the old mother began", "began the old mother", "the old mother continued", "continued the old mother", "the mother said", "said the mother", "the mother asked", "asked the mother", "the mother replied", "replied the mother", "the mother answered", "answered the mother", "the mother cried", "cried the mother", "the mother whispered", "whispered the mother", "the mother added", "added the mother", "the mother testified", "testified the mother", "the mother declared", "declared the mother", "the mother began", "began the mother", "the mother continued", "continued the mother", "the wife's mother said", "said the wife's mother", "the wife's mother asked", "asked the wife's mother", "the wife's mother replied", "replied the wife's mother", "the wife's mother answered", "answered the wife's mother", "the wife's mother cried", "cried the wife's mother", "the wife's mother whispered", "whispered the wife's mother", "the wife's mother added", "added the wife's mother", "the wife's mother testified", "testified the wife's mother", "the wife's mother declared", "declared the wife's mother", "the wife's mother began", "began the wife's mother", "the wife's mother continued", "continued the wife's mother", "masago's mother said", "said masago's mother", "masago's mother asked", "asked masago's mother", "masago's mother replied", "replied masago's mother", "masago's mother answered", "answered masago's mother", "masago's mother cried", "cried masago's mother", "masago's mother whispered", "whispered masago's mother", "masago's mother added", "added masago's mother", "masago's mother testified", "testified masago's mother", "masago's mother declared", "declared masago's mother", "masago's mother began", "began masago's mother", "masago's mother continued", "continued masago's mother"],
            "masago": ["masago said", "said masago", "masago asked", "asked masago", "masago replied", "replied masago", "masago answered", "answered masago", "masago cried", "cried masago", "masago whispered", "whispered masago", "masago added", "added masago", "masago testified", "testified masago", "masago declared", "declared masago", "masago began", "began masago", "masago continued", "continued masago", "the wife said", "said the wife", "the wife asked", "asked the wife", "the wife replied", "replied the wife", "the wife answered", "answered the wife", "the wife cried", "cried the wife", "the wife whispered", "whispered the wife", "the wife added", "added the wife", "the wife testified", "testified the wife", "the wife declared", "declared the wife", "the wife began", "began the wife", "the wife continued", "continued the wife", "the woman said", "said the woman", "the woman asked", "asked the woman", "the woman replied", "replied the woman", "the woman answered", "answered the woman", "the woman cried", "cried the woman", "the woman whispered", "whispered the woman", "the woman added", "added the woman", "the woman testified", "testified the woman", "the woman declared", "declared the woman", "the woman began", "began the woman", "the woman continued", "continued the woman", "the young woman said", "said the young woman", "the young woman asked", "asked the young woman", "the young woman replied", "replied the young woman", "the young woman answered", "answered the young woman", "the young woman cried", "cried the young woman", "the young woman whispered", "whispered the young woman", "the young woman added", "added the young woman", "the young woman testified", "testified the young woman", "the young woman declared", "declared the young woman", "the young woman began", "began the young woman", "the young woman continued", "continued the young woman"],
            "woodcutter": ["the woodcutter said", "said the woodcutter", "the woodcutter asked", "asked the woodcutter", "the woodcutter replied", "replied the woodcutter", "the woodcutter answered", "answered the woodcutter", "the woodcutter cried", "cried the woodcutter", "the woodcutter whispered", "whispered the woodcutter", "the woodcutter added", "added the woodcutter", "the woodcutter testified", "testified the woodcutter", "the woodcutter declared", "declared the woodcutter", "the woodcutter began", "began the woodcutter", "the woodcutter continued", "continued the woodcutter", "the woodsman said", "said the woodsman", "the woodsman asked", "asked the woodsman", "the woodsman replied", "replied the woodsman", "the woodsman answered", "answered the woodsman", "the woodsman cried", "cried the woodsman", "the woodsman whispered", "whispered the woodsman", "the woodsman added", "added the woodsman", "the woodsman testified", "testified the woodsman", "the woodsman declared", "declared the woodsman", "the woodsman began", "began the woodsman", "the woodsman continued", "continued the woodsman"],
            "monk": ["the monk said", "said the monk", "the monk asked", "asked the monk", "the monk replied", "replied the monk", "the monk answered", "answered the monk", "the monk cried", "cried the monk", "the monk whispered", "whispered the monk", "the monk added", "added the monk", "the monk testified", "testified the monk", "the monk declared", "declared the monk", "the monk began", "began the monk", "the monk continued", "continued the monk", "the priest said", "said the priest", "the priest asked", "asked the priest", "the priest replied", "replied the priest", "the priest answered", "answered the priest", "the priest cried", "cried the priest", "the priest whispered", "whispered the priest", "the priest added", "added the priest", "the priest testified", "testified the priest", "the priest declared", "declared the priest", "the priest began", "began the priest", "the priest continued", "continued the priest", "the traveling monk said", "said the traveling monk", "the traveling monk asked", "asked the traveling monk", "the traveling monk replied", "replied the traveling monk", "the traveling monk answered", "answered the traveling monk", "the traveling monk cried", "cried the traveling monk", "the traveling monk whispered", "whispered the traveling monk", "the traveling monk added", "added the traveling monk", "the traveling monk testified", "testified the traveling monk", "the traveling monk declared", "declared the traveling monk", "the traveling monk began", "began the traveling monk", "the traveling monk continued", "continued the traveling monk", "the travelling monk said", "said the travelling monk", "the travelling monk asked", "asked the travelling monk", "the travelling monk replied", "replied the travelling monk", "the travelling monk answered", "answered the travelling monk", "the travelling monk cried", "cried the travelling monk", "the travelling monk whispered", "whispered the travelling monk", "the travelling monk added", "added the travelling monk", "the travelling monk testified", "testified the travelling monk", "the travelling monk declared", "declared the travelling monk", "the travelling monk began", "began the travelling monk", "the travelling monk continued", "continued the travelling monk", "the traveling priest said", "said the traveling priest", "the traveling priest asked", "asked the traveling priest", "the traveling priest replied", "replied the traveling priest", "the traveling priest answered", "answered the traveling priest", "the traveling priest cried", "cried the traveling priest", "the traveling priest whispered", "whispered the traveling priest", "the traveling priest added", "added the traveling priest", "the traveling priest testified", "testified the traveling priest", "the traveling priest declared", "declared the traveling priest", "the traveling priest began", "began the traveling priest", "the traveling priest continued", "continued the traveling priest", "the travelling priest said", "said the travelling priest", "the travelling priest asked", "asked the travelling priest", "the travelling priest replied", "replied the travelling priest", "the travelling priest answered", "answered the travelling priest", "the travelling priest cried", "cried the travelling priest", "the travelling priest whispered", "whispered the travelling priest", "the travelling priest added", "added the travelling priest", "the travelling priest testified", "testified the travelling priest", "the travelling priest declared", "declared the travelling priest", "the travelling priest began", "began the travelling priest", "the travelling priest continued", "continued the travelling priest"],
            "constable": ["the constable said", "said the constable", "the constable asked", "asked the constable", "the constable replied", "replied the constable", "the constable answered", "answered the constable", "the constable cried", "cried the constable", "the constable whispered", "whispered the constable", "the constable added", "added the constable", "the constable testified", "testified the constable", "the constable declared", "declared the constable", "the constable began", "began the constable", "the constable continued", "continued the constable", "the policeman said", "said the policeman", "the policeman asked", "asked the policeman", "the policeman replied", "replied the policeman", "the policeman answered", "answered the policeman", "the policeman cried", "cried the policeman", "the policeman whispered", "whispered the policeman", "the policeman added", "added the policeman", "the policeman testified", "testified the policeman", "the policeman declared", "declared the policeman", "the policeman began", "began the policeman", "the policeman continued", "continued the policeman", "the police officer said", "said the police officer", "the police officer asked", "asked the police officer", "the police officer replied", "replied the police officer", "the police officer answered", "answered the police officer", "the police officer cried", "cried the police officer", "the police officer whispered", "whispered the police officer", "the police officer added", "added the police officer", "the police officer testified", "testified the police officer", "the police officer declared", "declared the police officer", "the police officer began", "began the police officer", "the police officer continued", "continued the police officer"],
            "tajomaru": ["tajomaru said", "said tajomaru", "tajomaru asked", "asked tajomaru", "tajomaru replied", "replied tajomaru", "tajomaru answered", "answered tajomaru", "tajomaru cried", "cried tajomaru", "tajomaru whispered", "whispered tajomaru", "tajomaru added", "added tajomaru", "tajomaru testified", "testified tajomaru", "tajomaru declared", "declared tajomaru", "tajomaru began", "began tajomaru", "tajomaru continued", "continued tajomaru", "the bandit said", "said the bandit", "the bandit asked", "asked the bandit", "the bandit replied", "replied the bandit", "the bandit answered", "answered the bandit", "the bandit cried", "cried the bandit", "the bandit whispered", "whispered the bandit", "the bandit added", "added the bandit", "the bandit testified", "testified the bandit", "the bandit declared", "declared the bandit", "the bandit began", "began the bandit", "the bandit continued", "continued the bandit", "the thief said", "said the thief", "the thief asked", "asked the thief", "the thief replied", "replied the thief", "the thief answered", "answered the thief", "the thief cried", "cried the thief", "the thief whispered", "whispered the thief", "the thief added", "added the thief", "the thief testified", "testified the thief", "the thief declared", "declared the thief", "the thief began", "began the thief", "the thief continued", "continued the thief", "the robber said", "said the robber", "the robber asked", "asked the robber", "the robber replied", "replied the robber", "the robber answered", "answered the robber", "the robber cried", "cried the robber", "the robber whispered", "whispered the robber", "the robber added", "added the robber", "the robber testified", "testified the robber", "the robber declared", "declared the robber", "the robber began", "began the robber", "the robber continued", "continued the robber"],
            "takehiro": ["takehiro said", "said takehiro", "takehiro asked", "asked takehiro", "takehiro replied", "replied takehiro", "takehiro answered", "answered takehiro", "takehiro cried", "cried takehiro", "takehiro whispered", "whispered takehiro", "takehiro added", "added takehiro", "takehiro testified", "testified takehiro", "takehiro declared", "declared takehiro", "takehiro began", "began takehiro", "takehiro continued", "continued takehiro", "the dead man said", "said the dead man", "the dead man asked", "asked the dead man", "the dead man replied", "replied the dead man", "the dead man answered", "answered the dead man", "the dead man cried", "cried the dead man", "the dead man whispered", "whispered the dead man", "the dead man added", "added the dead man", "the dead man testified", "testified the dead man", "the dead man declared", "declared the dead man", "the dead man began", "began the dead man", "the dead man continued", "continued the dead man", "the dead husband said", "said the dead husband", "the dead husband asked", "asked the dead husband", "the dead husband replied", "replied the dead husband", "the dead husband answered", "answered the dead husband", "the dead husband cried", "cried the dead husband", "the dead husband whispered", "whispered the dead husband", "the dead husband added", "added the dead husband", "the dead husband testified", "testified the dead husband", "the dead husband declared", "declared the dead husband", "the dead husband began", "began the dead husband", "the dead husband continued", "continued the dead husband", "the husband said", "said the husband", "the husband asked", "asked the husband", "the husband replied", "replied the husband", "the husband answered", "answered the husband", "the husband cried", "cried the husband", "the husband whispered", "whispered the husband", "the husband added", "added the husband", "the husband testified", "testified the husband", "the husband declared", "declared the husband", "the husband began", "began the husband", "the husband continued", "continued the husband", "the samurai said", "said the samurai", "the samurai asked", "asked the samurai", "the samurai replied", "replied the samurai", "the samurai answered", "answered the samurai", "the samurai cried", "cried the samurai", "the samurai whispered", "whispered the samurai", "the samurai added", "added the samurai", "the samurai testified", "testified the samurai", "the samurai declared", "declared the samurai", "the samurai began", "began the samurai", "the samurai continued", "continued the samurai", "the spirit said", "said the spirit", "the spirit asked", "asked the spirit", "the spirit replied", "replied the spirit", "the spirit answered", "answered the spirit", "the spirit cried", "cried the spirit", "the spirit whispered", "whispered the spirit", "the spirit added", "added the spirit", "the spirit testified", "testified the spirit", "the spirit declared", "declared the spirit", "the spirit began", "began the spirit", "the spirit continued", "continued the spirit", "the ghost said", "said the ghost", "the ghost asked", "asked the ghost", "the ghost replied", "replied the ghost", "the ghost answered", "answered the ghost", "the ghost cried", "cried the ghost", "the ghost whispered", "whispered the ghost", "the ghost added", "added the ghost", "the ghost testified", "testified the ghost", "the ghost declared", "declared the ghost", "the ghost began", "began the ghost", "the ghost continued", "continued the ghost"],
        },
        "attr_roster_text": (
            "- \"woodcutter\": the woodcutter who found the body (also 'the woodsman')\n"
            "- \"monk\": the traveling monk who met the couple the day before (also 'the priest')\n"
            "- \"constable\": the constable (the police runner) who caught the bandit Tajomaru (also 'the policeman')\n"
            "- \"old_woman\": the old woman, Masago's mother and Takehiro's mother-in-law (also 'the mother')\n"
            "- \"tajomaru\": the bandit Tajomaru, who confesses (also 'the bandit', 'the thief')\n"
            "- \"masago\": Masago, the wife, who tells her account at the temple (also 'the wife', 'the woman')\n"
            "- \"takehiro\": Takehiro, the dead husband, a samurai, whose spirit speaks through a medium (also 'the dead man', 'the spirit', 'the husband')\n"
            "- \"other\": any other speaker (a stranger, a crowd, etc.)\n"
            "- \"narrator\": the outside narrator who only introduces who is speaking; also the police magistrate's questions if the text quotes them (the magistrate has no voice of his own), and any line not spoken by a witness"),
        "attr_caution_text": (
            "Be careful: every witness tells his or her own story in the first person, so the 'I' in a quote is the witness named in the speech tag or in the introduction before it, not the narrator; "
            "Takehiro speaks through a medium, but the speaker is takehiro, not the medium; a name or role that appears NEAR a quote is not always the speaker (for example, in "
            "'\"The bandit tied me up,\" said Takehiro.' the speaker is takehiro, not tajomaru; in 'The constable pointed at the bandit and said, \"This man did it.\"' the speaker is constable)."),
        "dialogue_voice_keywords": {
            "old_woman": ["the old woman said", "said the old woman", "the old woman asked", "asked the old woman", "the old woman replied", "replied the old woman", "the old woman answered", "answered the old woman", "the old woman cried", "cried the old woman", "the old woman whispered", "whispered the old woman", "the old woman added", "added the old woman", "the old woman testified", "testified the old woman", "the old woman declared", "declared the old woman", "the old woman began", "began the old woman", "the old woman continued", "continued the old woman", "the old mother said", "said the old mother", "the old mother asked", "asked the old mother", "the old mother replied", "replied the old mother", "the old mother answered", "answered the old mother", "the old mother cried", "cried the old mother", "the old mother whispered", "whispered the old mother", "the old mother added", "added the old mother", "the old mother testified", "testified the old mother", "the old mother declared", "declared the old mother", "the old mother began", "began the old mother", "the old mother continued", "continued the old mother", "the mother said", "said the mother", "the mother asked", "asked the mother", "the mother replied", "replied the mother", "the mother answered", "answered the mother", "the mother cried", "cried the mother", "the mother whispered", "whispered the mother", "the mother added", "added the mother", "the mother testified", "testified the mother", "the mother declared", "declared the mother", "the mother began", "began the mother", "the mother continued", "continued the mother", "the wife's mother said", "said the wife's mother", "the wife's mother asked", "asked the wife's mother", "the wife's mother replied", "replied the wife's mother", "the wife's mother answered", "answered the wife's mother", "the wife's mother cried", "cried the wife's mother", "the wife's mother whispered", "whispered the wife's mother", "the wife's mother added", "added the wife's mother", "the wife's mother testified", "testified the wife's mother", "the wife's mother declared", "declared the wife's mother", "the wife's mother began", "began the wife's mother", "the wife's mother continued", "continued the wife's mother", "masago's mother said", "said masago's mother", "masago's mother asked", "asked masago's mother", "masago's mother replied", "replied masago's mother", "masago's mother answered", "answered masago's mother", "masago's mother cried", "cried masago's mother", "masago's mother whispered", "whispered masago's mother", "masago's mother added", "added masago's mother", "masago's mother testified", "testified masago's mother", "masago's mother declared", "declared masago's mother", "masago's mother began", "began masago's mother", "masago's mother continued", "continued masago's mother"],
            "masago": ["masago said", "said masago", "masago asked", "asked masago", "masago replied", "replied masago", "masago answered", "answered masago", "masago cried", "cried masago", "masago whispered", "whispered masago", "masago added", "added masago", "masago testified", "testified masago", "masago declared", "declared masago", "masago began", "began masago", "masago continued", "continued masago", "the wife said", "said the wife", "the wife asked", "asked the wife", "the wife replied", "replied the wife", "the wife answered", "answered the wife", "the wife cried", "cried the wife", "the wife whispered", "whispered the wife", "the wife added", "added the wife", "the wife testified", "testified the wife", "the wife declared", "declared the wife", "the wife began", "began the wife", "the wife continued", "continued the wife", "the woman said", "said the woman", "the woman asked", "asked the woman", "the woman replied", "replied the woman", "the woman answered", "answered the woman", "the woman cried", "cried the woman", "the woman whispered", "whispered the woman", "the woman added", "added the woman", "the woman testified", "testified the woman", "the woman declared", "declared the woman", "the woman began", "began the woman", "the woman continued", "continued the woman", "the young woman said", "said the young woman", "the young woman asked", "asked the young woman", "the young woman replied", "replied the young woman", "the young woman answered", "answered the young woman", "the young woman cried", "cried the young woman", "the young woman whispered", "whispered the young woman", "the young woman added", "added the young woman", "the young woman testified", "testified the young woman", "the young woman declared", "declared the young woman", "the young woman began", "began the young woman", "the young woman continued", "continued the young woman"],
            "woodcutter": ["the woodcutter said", "said the woodcutter", "the woodcutter asked", "asked the woodcutter", "the woodcutter replied", "replied the woodcutter", "the woodcutter answered", "answered the woodcutter", "the woodcutter cried", "cried the woodcutter", "the woodcutter whispered", "whispered the woodcutter", "the woodcutter added", "added the woodcutter", "the woodcutter testified", "testified the woodcutter", "the woodcutter declared", "declared the woodcutter", "the woodcutter began", "began the woodcutter", "the woodcutter continued", "continued the woodcutter", "the woodsman said", "said the woodsman", "the woodsman asked", "asked the woodsman", "the woodsman replied", "replied the woodsman", "the woodsman answered", "answered the woodsman", "the woodsman cried", "cried the woodsman", "the woodsman whispered", "whispered the woodsman", "the woodsman added", "added the woodsman", "the woodsman testified", "testified the woodsman", "the woodsman declared", "declared the woodsman", "the woodsman began", "began the woodsman", "the woodsman continued", "continued the woodsman"],
            "monk": ["the monk said", "said the monk", "the monk asked", "asked the monk", "the monk replied", "replied the monk", "the monk answered", "answered the monk", "the monk cried", "cried the monk", "the monk whispered", "whispered the monk", "the monk added", "added the monk", "the monk testified", "testified the monk", "the monk declared", "declared the monk", "the monk began", "began the monk", "the monk continued", "continued the monk", "the priest said", "said the priest", "the priest asked", "asked the priest", "the priest replied", "replied the priest", "the priest answered", "answered the priest", "the priest cried", "cried the priest", "the priest whispered", "whispered the priest", "the priest added", "added the priest", "the priest testified", "testified the priest", "the priest declared", "declared the priest", "the priest began", "began the priest", "the priest continued", "continued the priest", "the traveling monk said", "said the traveling monk", "the traveling monk asked", "asked the traveling monk", "the traveling monk replied", "replied the traveling monk", "the traveling monk answered", "answered the traveling monk", "the traveling monk cried", "cried the traveling monk", "the traveling monk whispered", "whispered the traveling monk", "the traveling monk added", "added the traveling monk", "the traveling monk testified", "testified the traveling monk", "the traveling monk declared", "declared the traveling monk", "the traveling monk began", "began the traveling monk", "the traveling monk continued", "continued the traveling monk", "the travelling monk said", "said the travelling monk", "the travelling monk asked", "asked the travelling monk", "the travelling monk replied", "replied the travelling monk", "the travelling monk answered", "answered the travelling monk", "the travelling monk cried", "cried the travelling monk", "the travelling monk whispered", "whispered the travelling monk", "the travelling monk added", "added the travelling monk", "the travelling monk testified", "testified the travelling monk", "the travelling monk declared", "declared the travelling monk", "the travelling monk began", "began the travelling monk", "the travelling monk continued", "continued the travelling monk", "the traveling priest said", "said the traveling priest", "the traveling priest asked", "asked the traveling priest", "the traveling priest replied", "replied the traveling priest", "the traveling priest answered", "answered the traveling priest", "the traveling priest cried", "cried the traveling priest", "the traveling priest whispered", "whispered the traveling priest", "the traveling priest added", "added the traveling priest", "the traveling priest testified", "testified the traveling priest", "the traveling priest declared", "declared the traveling priest", "the traveling priest began", "began the traveling priest", "the traveling priest continued", "continued the traveling priest", "the travelling priest said", "said the travelling priest", "the travelling priest asked", "asked the travelling priest", "the travelling priest replied", "replied the travelling priest", "the travelling priest answered", "answered the travelling priest", "the travelling priest cried", "cried the travelling priest", "the travelling priest whispered", "whispered the travelling priest", "the travelling priest added", "added the travelling priest", "the travelling priest testified", "testified the travelling priest", "the travelling priest declared", "declared the travelling priest", "the travelling priest began", "began the travelling priest", "the travelling priest continued", "continued the travelling priest"],
            "constable": ["the constable said", "said the constable", "the constable asked", "asked the constable", "the constable replied", "replied the constable", "the constable answered", "answered the constable", "the constable cried", "cried the constable", "the constable whispered", "whispered the constable", "the constable added", "added the constable", "the constable testified", "testified the constable", "the constable declared", "declared the constable", "the constable began", "began the constable", "the constable continued", "continued the constable", "the policeman said", "said the policeman", "the policeman asked", "asked the policeman", "the policeman replied", "replied the policeman", "the policeman answered", "answered the policeman", "the policeman cried", "cried the policeman", "the policeman whispered", "whispered the policeman", "the policeman added", "added the policeman", "the policeman testified", "testified the policeman", "the policeman declared", "declared the policeman", "the policeman began", "began the policeman", "the policeman continued", "continued the policeman", "the police officer said", "said the police officer", "the police officer asked", "asked the police officer", "the police officer replied", "replied the police officer", "the police officer answered", "answered the police officer", "the police officer cried", "cried the police officer", "the police officer whispered", "whispered the police officer", "the police officer added", "added the police officer", "the police officer testified", "testified the police officer", "the police officer declared", "declared the police officer", "the police officer began", "began the police officer", "the police officer continued", "continued the police officer"],
            "tajomaru": ["tajomaru said", "said tajomaru", "tajomaru asked", "asked tajomaru", "tajomaru replied", "replied tajomaru", "tajomaru answered", "answered tajomaru", "tajomaru cried", "cried tajomaru", "tajomaru whispered", "whispered tajomaru", "tajomaru added", "added tajomaru", "tajomaru testified", "testified tajomaru", "tajomaru declared", "declared tajomaru", "tajomaru began", "began tajomaru", "tajomaru continued", "continued tajomaru", "the bandit said", "said the bandit", "the bandit asked", "asked the bandit", "the bandit replied", "replied the bandit", "the bandit answered", "answered the bandit", "the bandit cried", "cried the bandit", "the bandit whispered", "whispered the bandit", "the bandit added", "added the bandit", "the bandit testified", "testified the bandit", "the bandit declared", "declared the bandit", "the bandit began", "began the bandit", "the bandit continued", "continued the bandit", "the thief said", "said the thief", "the thief asked", "asked the thief", "the thief replied", "replied the thief", "the thief answered", "answered the thief", "the thief cried", "cried the thief", "the thief whispered", "whispered the thief", "the thief added", "added the thief", "the thief testified", "testified the thief", "the thief declared", "declared the thief", "the thief began", "began the thief", "the thief continued", "continued the thief", "the robber said", "said the robber", "the robber asked", "asked the robber", "the robber replied", "replied the robber", "the robber answered", "answered the robber", "the robber cried", "cried the robber", "the robber whispered", "whispered the robber", "the robber added", "added the robber", "the robber testified", "testified the robber", "the robber declared", "declared the robber", "the robber began", "began the robber", "the robber continued", "continued the robber"],
            "takehiro": ["takehiro said", "said takehiro", "takehiro asked", "asked takehiro", "takehiro replied", "replied takehiro", "takehiro answered", "answered takehiro", "takehiro cried", "cried takehiro", "takehiro whispered", "whispered takehiro", "takehiro added", "added takehiro", "takehiro testified", "testified takehiro", "takehiro declared", "declared takehiro", "takehiro began", "began takehiro", "takehiro continued", "continued takehiro", "the dead man said", "said the dead man", "the dead man asked", "asked the dead man", "the dead man replied", "replied the dead man", "the dead man answered", "answered the dead man", "the dead man cried", "cried the dead man", "the dead man whispered", "whispered the dead man", "the dead man added", "added the dead man", "the dead man testified", "testified the dead man", "the dead man declared", "declared the dead man", "the dead man began", "began the dead man", "the dead man continued", "continued the dead man", "the dead husband said", "said the dead husband", "the dead husband asked", "asked the dead husband", "the dead husband replied", "replied the dead husband", "the dead husband answered", "answered the dead husband", "the dead husband cried", "cried the dead husband", "the dead husband whispered", "whispered the dead husband", "the dead husband added", "added the dead husband", "the dead husband testified", "testified the dead husband", "the dead husband declared", "declared the dead husband", "the dead husband began", "began the dead husband", "the dead husband continued", "continued the dead husband", "the husband said", "said the husband", "the husband asked", "asked the husband", "the husband replied", "replied the husband", "the husband answered", "answered the husband", "the husband cried", "cried the husband", "the husband whispered", "whispered the husband", "the husband added", "added the husband", "the husband testified", "testified the husband", "the husband declared", "declared the husband", "the husband began", "began the husband", "the husband continued", "continued the husband", "the samurai said", "said the samurai", "the samurai asked", "asked the samurai", "the samurai replied", "replied the samurai", "the samurai answered", "answered the samurai", "the samurai cried", "cried the samurai", "the samurai whispered", "whispered the samurai", "the samurai added", "added the samurai", "the samurai testified", "testified the samurai", "the samurai declared", "declared the samurai", "the samurai began", "began the samurai", "the samurai continued", "continued the samurai", "the spirit said", "said the spirit", "the spirit asked", "asked the spirit", "the spirit replied", "replied the spirit", "the spirit answered", "answered the spirit", "the spirit cried", "cried the spirit", "the spirit whispered", "whispered the spirit", "the spirit added", "added the spirit", "the spirit testified", "testified the spirit", "the spirit declared", "declared the spirit", "the spirit began", "began the spirit", "the spirit continued", "continued the spirit", "the ghost said", "said the ghost", "the ghost asked", "asked the ghost", "the ghost replied", "replied the ghost", "the ghost answered", "answered the ghost", "the ghost cried", "cried the ghost", "the ghost whispered", "whispered the ghost", "the ghost added", "added the ghost", "the ghost testified", "testified the ghost", "the ghost declared", "declared the ghost", "the ghost began", "began the ghost", "the ghost continued", "continued the ghost"],
        },
        # 正式Voice表+決定的割当規則から導出(未割当/fail-closedの値Noneは残さない)。
        "dialogue_voice_tts_names": derive_dialogue_voice_tts_names("in_a_grove"),
        "speaker_aliases": {"woodcutter": "woodcutter", "monk": "monk", "constable": "constable", "old_woman": "old_woman", "tajomaru": "tajomaru",
                            "masago": "masago", "takehiro": "takehiro", "narrator": "narrator"},
    },
}


def speaker_config(story_key: str = "melos") -> dict:
    """story別roster設定(未登録story_keyはKeyError=fail-closed)。"""
    return STORY_SPEAKER_CONFIG[story_key]


def speakers_for(story_key: str = "melos") -> tuple:
    return STORY_SPEAKER_CONFIG[story_key]["speakers"]


# 互換alias(Melos値。二重定義ではなくSTORY_SPEAKER_CONFIG["melos"]の同一オブジェクトを参照)
SPEAKERS = STORY_SPEAKER_CONFIG["melos"]["speakers"]
Z_VOICE_KEYWORDS = STORY_SPEAKER_CONFIG["melos"]["z_voice_keywords"]
PART_RATIO_RANGE = (0.20, 0.45)
QUOTE_RE = fam_c.DEFAULT_QUOTE_RE
_EPS = 1e-9


class FamilyZStop(RuntimeError):
    """Family Z工程のSTOP(自動継続しない)基底。"""


class FamilyZSplitStop(FamilyZStop):
    pass


class FamilyZDialogueMismatchStop(FamilyZStop):
    pass


class FamilyZLintStop(FamilyZStop):
    pass


class FamilyZProvenanceMismatchStop(FamilyZStop):
    pass


class FamilyZPlanStop(FamilyZStop):
    pass


# ------------------------------------------------------------
# STOPセンチネル(委任_11 再発防止 / 委任_12A 機械的阻止の追加)
# Fable/ユーザーが仕様変更等で実行を止めたいときの合図ファイル。
#  - <run>/STOP, <run>/RESTART_STORM_LOCK.json, STOP_ALL(絶対path。cwdに依存しない)
#  - 各API呼出の直前・各stage前・各clip前・起動時・client生成時に確認し、存在すれば新規API呼出をせず
#    監査記録(<run>/audit_stop_sentinel.jsonl)を書いて停止(runnerはrc=3)。
#  - 共有moduleのretry/fallback/cool-down内部の呼出も、SDK入口(install_api_stop_guard)で止める。
#  - 二重起動(RUN_LOCK.json)・監視ループ的再起動(RESTART_STORM)も機械的に阻止する。
# ------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
STOP_ALL_PATH = os.path.join(_REPO_ROOT, "er026_output", "family_z_production_e2e_01", "STOP_ALL")
STOP_EXIT_CODE = 3
LOCK_EXIT_CODE = 4
CLEAR_REFUSED_EXIT_CODE = 5
RESTART_STORM_MARKER = "RESTART_STORM_LOCK.json"
RUN_LOCK_NAME = "RUN_LOCK.json"
LAUNCH_LOG_NAME = "run_launch_log.jsonl"
AUDIT_NAME = "audit_stop_sentinel.jsonl"
STORM_WINDOW_SEC = 300.0
STORM_THRESHOLD = 3
_STOP_RUN_DIR = None


class FamilyZStopSentinel(FamilyZStop):
    """STOPセンチネル検出。自動再開・再試行しない。"""


class FamilyZRunLockHeld(FamilyZStop):
    """同一runで別processが稼働中(RUN_LOCK.json有効)。二重起動拒否。"""


class FamilyZStopSentinelAbort(BaseException):
    """API入口(SDK class method / mock API)で送出するSTOP。BaseExceptionなので、共有moduleの
    `except Exception:` によるretry/fallbackで握り潰されない(握り潰されても次のAPI入口で再度止まる)。"""


def set_stop_run_dir(run_dir) -> None:
    global _STOP_RUN_DIR
    _STOP_RUN_DIR = run_dir


def _sentinel_candidates(run_dir):
    rd = run_dir or _STOP_RUN_DIR
    cands = []
    if rd:
        rd = str(rd).replace("\\", "/")
        dirs = [rd]
        if rd.endswith("_mock"):
            dirs.append(rd[: -len("_mock")])           # mockは `<run>_mock` で動くが `<run>/STOP` でも止める
        for d in dirs:
            cands += [f"{d}/STOP", f"{d}/{RESTART_STORM_MARKER}"]
    cands.append(STOP_ALL_PATH)
    return cands


def stop_sentinel_hit(run_dir=None):
    """存在するセンチネルのpathを返す(なければNone)。API 0・書込 0。"""
    for pth in _sentinel_candidates(run_dir):
        if os.path.exists(pth):
            return pth
    return None


def _audit(run_dir, rec: dict) -> None:
    import datetime
    if run_dir and os.path.isdir(run_dir):
        rec = {"at": datetime.datetime.now().isoformat(), "pid": os.getpid(), **rec}
        with open(f"{run_dir}/{AUDIT_NAME}", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def check_stop_sentinel(where: str, run_dir=None) -> None:
    """センチネルがあれば監査記録(<run>/audit_stop_sentinel.jsonl)を書いて FamilyZStopSentinel を送出する。"""
    hit = stop_sentinel_hit(run_dir)
    if hit is None:
        return
    rd = run_dir or _STOP_RUN_DIR
    _audit(rd, {"where": where, "sentinel": hit})
    raise FamilyZStopSentinel(f"FAMILY_Z_STOP_SENTINEL: {hit} が存在するため {where} の前で停止(新規API呼出なし)。"
                              "自動再開/再試行はしない。Fable/ユーザーの指示を待つこと。")


def api_guard(where: str, run_dir=None) -> None:
    """全API入口で呼ぶ。センチネルがあれば BaseException系 FamilyZStopSentinelAbort を送出する。"""
    try:
        check_stop_sentinel(where, run_dir)
    except FamilyZStopSentinel as e:
        raise FamilyZStopSentinelAbort(str(e)) from e


# ---- SDK入口へのguard(real時のみinstall。共有moduleは不変、classレベルのruntime wrap) ----
_GUARD_TARGETS = (
    ("openai.resources.responses.responses", "Responses", "create", "openai.responses.create"),
    ("openai.resources.audio.transcriptions", "Transcriptions", "create", "openai.audio.transcriptions.create"),
    ("google.genai.models", "Models", "generate_content", "gemini.models.generate_content"),
    ("google.genai.batches", "Batches", "create", "gemini.batches.create"),
)
_GUARD_AZURE = (("er003_b1_p3u_audio", "get_word_timestamps_via_azure_stt"),
                ("er003_b1_p4_audio", "get_full_text_via_azure_stt_continuous"))
_WRAPPED = []   # [(owner, name, original)]


def _wrap_attr(owner, name: str, where: str) -> bool:
    orig = getattr(owner, name, None)
    if orig is None or getattr(orig, "_family_z_stop_guard", False):
        return False

    @functools.wraps(orig)
    def guarded(*a, **k):
        api_guard(where)                     # 新規API(課金)の直前。retry/fallback/cool-down後でも必ず通る
        return orig(*a, **k)

    guarded._family_z_stop_guard = True
    setattr(owner, name, guarded)
    _WRAPPED.append((owner, name, orig))
    return True


def install_api_stop_guard() -> list:
    """OpenAI Responses/Transcriptions・Gemini generate_content/batches・Azure STTの入口にSTOP確認を差し込む。
    er005_cost_logger.install の後に呼ぶ(guardが最外殻になり、STOP時はcost logにも記録されない)。"""
    import importlib
    done = []
    for mod, cls, meth, where in _GUARD_TARGETS:
        try:
            owner = getattr(importlib.import_module(mod), cls)
        except Exception:  # noqa: BLE001  (SDK未導入等。guardできない入口は報告に残す)
            continue
        if _wrap_attr(owner, meth, where):
            done.append(where)
    for mod, fn in _GUARD_AZURE:
        try:
            m = importlib.import_module(mod)
        except Exception:  # noqa: BLE001
            continue
        if _wrap_attr(m, fn, f"azure.{fn}"):
            done.append(f"azure.{fn}")
    return done


def uninstall_api_stop_guard() -> None:
    while _WRAPPED:
        owner, name, orig = _WRAPPED.pop()
        setattr(owner, name, orig)


# ---- 二重起動阻止(RUN_LOCK.json) ----
def pid_alive(pid) -> bool:
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x1000, False, pid)         # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            if not k32.GetExitCodeProcess(h, ctypes.byref(code)):
                return True
            return code.value == 259                    # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_json_safe(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def acquire_run_lock(run_dir: str, argv=None) -> dict:
    """<run>/RUN_LOCK.json を排他作成する。有効(PID生存)なlockが既にあれば FamilyZRunLockHeld。stale(PID死亡)は置換。"""
    import datetime
    os.makedirs(run_dir, exist_ok=True)
    path = f"{run_dir}/{RUN_LOCK_NAME}"
    rec = {"pid": os.getpid(), "parent_pid": os.getppid(), "started_at": datetime.datetime.now().isoformat(),
           "started_ts": time.time(), "argv": list(argv) if argv is not None else None}
    for _ in range(3):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            cur = _read_json_safe(path)
            if cur is None:
                time.sleep(0.3)                           # 作成途中の可能性
                cur = _read_json_safe(path)
            if cur is not None and cur.get("pid") != os.getpid() and pid_alive(cur.get("pid")):
                _audit(run_dir, {"event": "RUN_LOCK_REFUSED", "held_by": cur})
                raise FamilyZRunLockHeld(
                    f"FAMILY_Z_RUN_LOCK_HELD: {path} が有効(PID {cur.get('pid')} 稼働中)。二重起動を拒否。"
                    "既存processの終了を待つこと(自動再試行しない)。")
            _audit(run_dir, {"event": "RUN_LOCK_STALE_REPLACED", "stale": cur})
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False)
        return rec
    raise FamilyZRunLockHeld(f"FAMILY_Z_RUN_LOCK_HELD: {path} を確保できない(競合)。")


def release_run_lock(run_dir: str) -> bool:
    path = f"{run_dir}/{RUN_LOCK_NAME}"
    cur = _read_json_safe(path)
    if cur is not None and cur.get("pid") == os.getpid():
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            pass
    return False


# ---- 監視ループ的再起動の検出(RESTART_STORM) ----
def _last_clear_ts(rows) -> float:
    return max([r.get("ts", 0) for r in rows if r.get("event") == "CLEARED"] or [0.0])


def record_launch_and_check_storm(run_dir: str, argv=None, *, now: float | None = None) -> dict:
    """起動1回を run_launch_log.jsonl に記録し、5分間に3回以上なら <run>/STOP と RESTART_STORM_LOCK.json を作って停止する。"""
    import datetime
    os.makedirs(run_dir, exist_ok=True)
    now = time.time() if now is None else now
    path = f"{run_dir}/{LAUNCH_LOG_NAME}"
    rec = {"event": "LAUNCH", "ts": now, "at": datetime.datetime.fromtimestamp(now).isoformat(), "pid": os.getpid(),
           "parent_pid": os.getppid(), "argv": list(argv) if argv is not None else None}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:  # noqa: BLE001
                pass
    since = max(_last_clear_ts(rows), now - STORM_WINDOW_SEC)
    n = sum(1 for r in rows if r.get("event") == "LAUNCH" and r.get("ts", 0) > since)
    if n >= STORM_THRESHOLD:
        body = {"reason": "RESTART_STORM", "created_at": rec["at"], "launches_in_window": n,
                "window_sec": STORM_WINDOW_SEC, "note": "監視ループ/自動再起動の疑い。--clear-stop --reason でのみ解除可。"}
        for name in ("STOP", RESTART_STORM_MARKER):
            with open(f"{run_dir}/{name}", "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False)
        _audit(run_dir, {"event": "RESTART_STORM", **body})
        raise FamilyZStopSentinel(
            f"FAMILY_Z_RESTART_STORM: 同一runが{STORM_WINDOW_SEC:.0f}秒間に{n}回起動された。{run_dir}/STOP を自動作成して停止。"
            "解除は `--clear-stop --reason \"...\"` のみ(手動削除では解除されない)。")
    return {"launches_in_window": n}


# ---- 明示的な解除(正規操作) ----
def clear_stop(run_dir: str, reason: str) -> dict:
    """<run>/STOP(と RESTART_STORM_LOCK.json)を解除し、理由を audit_stop_sentinel.jsonl に記録する。
    STOP_ALL は解除しない(Fable/ユーザー専用: tools/stop_all_family_z.py --release)。
    RUN_CLOSED(run閉鎖)は解除不可。"""
    import datetime
    if not (reason or "").strip():
        raise ValueError("--clear-stop には --reason が必須")
    stop_p, storm_p = f"{run_dir}/STOP", f"{run_dir}/{RESTART_STORM_MARKER}"
    cur = _read_json_safe(stop_p) or {}
    if cur.get("reason") == "RUN_CLOSED":
        raise FamilyZStop(f"FAMILY_Z_RUN_CLOSED: {run_dir} は閉鎖済みで解除できない(新しいrun名を使うこと)")
    removed = []
    for p in (stop_p, storm_p):
        if os.path.exists(p):
            os.remove(p)
            removed.append(p)
    now = time.time()
    if os.path.isdir(run_dir):
        with open(f"{run_dir}/{LAUNCH_LOG_NAME}", "a", encoding="utf-8") as f:     # storm カウントをここで区切る
            f.write(json.dumps({"event": "CLEARED", "ts": now, "at": datetime.datetime.fromtimestamp(now).isoformat(),
                                "reason": reason}, ensure_ascii=False) + "\n")
    _audit(run_dir, {"event": "CLEARED", "reason": reason, "removed": removed, "previous": cur or None,
                     "stop_all_still_present": os.path.exists(STOP_ALL_PATH)})
    return {"removed": removed, "stop_all_still_present": os.path.exists(STOP_ALL_PATH)}


def sha(s) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s or b"").hexdigest()


# ------------------------------------------------------------
# 1. 段落整形
# ------------------------------------------------------------
_TITLE_RE = re.compile(r"^\s*#\s+(.+?)\s*$")


def split_title_body(text: str) -> tuple:
    """先頭の非空行が `# Title` ならtitleとして分離する。(title|None, body)。"""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines):
        m = _TITLE_RE.match(lines[i])
        if m:
            return m.group(1).strip(), "\n".join(lines[i + 1:]).strip("\n")
    return None, "\n".join(lines).strip("\n")


def clean_body_paragraphs(body: str) -> list:
    """本文を空行区切りの段落listにする。強調記号(*)は音声化に不要なので除去する。
    段落内の改行は空白へ。空段落は捨てる(=全paragraph indexが非空段落を指す)。"""
    body = (body or "").replace("\r\n", "\n").replace("*", "")
    paras = []
    for p in re.split(r"\n\s*\n", body):
        q = " ".join(p.split())
        if q:
            paras.append(q)
    return paras


def para_word_counts(paragraphs) -> list:
    return [len(fam_c.normalize_for_tts(p).split()) for p in paragraphs]


def body_word_count(text: str) -> int:
    """見出し(# 行)を除いた語数。"""
    _t, body = split_title_body(text)
    return sum(para_word_counts(clean_body_paragraphs(body)))


# ------------------------------------------------------------
# 2. Story 3分割: 決定論の候補列挙
# ------------------------------------------------------------
def enumerate_split_candidates(wcs, lo: float = PART_RATIO_RANGE[0], hi: float = PART_RATIO_RANGE[1]) -> list:
    """段落境界ペア(b1<b2)を全列挙。b1=Part2の先頭段落index、b2=Part3の先頭段落index。
    Part1=[0,b1), Part2=[b1,b2), Part3=[b2,n)の各語数比が [lo,hi] (両端含む)。候補が空なら空list。"""
    n = len(wcs)
    total = sum(wcs)
    if n < 3 or total <= 0:
        return []
    pre = [0]
    for w in wcs:
        pre.append(pre[-1] + w)
    out = []
    for b1 in range(1, n - 1):
        r1 = pre[b1] / total
        if r1 < lo - _EPS or r1 > hi + _EPS:
            continue
        for b2 in range(b1 + 1, n):
            r2 = (pre[b2] - pre[b1]) / total
            r3 = (total - pre[b2]) / total
            if lo - _EPS <= r2 <= hi + _EPS and lo - _EPS <= r3 <= hi + _EPS:
                out.append((b1, b2))
    return out


def candidates_as_ranges(cands) -> dict:
    """{b1: [(b2_lo, b2_hi), ...]} 連続区間へ圧縮(LLM Prompt用)。"""
    by = {}
    for b1, b2 in cands:
        by.setdefault(b1, []).append(b2)
    out = {}
    for b1, vals in by.items():
        vals.sort()
        runs = []
        s = p = vals[0]
        for v in vals[1:]:
            if v == p + 1:
                p = v
            else:
                runs.append((s, p))
                s = p = v
        runs.append((s, p))
        out[b1] = runs
    return out


def part_stats(wcs, b1: int, b2: int) -> list:
    total = sum(wcs) or 1
    segs = [(0, b1), (b1, b2), (b2, len(wcs))]
    out = []
    for i, (a, b) in enumerate(segs, start=1):
        w = sum(wcs[a:b])
        out.append({"part": i, "paragraph_range": [a, b - 1], "word_count": w, "ratio": round(w / total, 4)})
    return out


def part_of_paragraph(p_idx: int, b1: int, b2: int) -> int:
    return 1 + (1 if p_idx >= b1 else 0) + (1 if p_idx >= b2 else 0)


def part_texts(paragraphs, b1: int, b2: int) -> dict:
    return {1: "\n\n".join(paragraphs[:b1]), 2: "\n\n".join(paragraphs[b1:b2]), 3: "\n\n".join(paragraphs[b2:])}


def validate_split_choice(choice, cands) -> tuple:
    """(ok, reason)。candsに無いペア(候補外)は拒否する。"""
    try:
        pair = (int(choice[0]), int(choice[1]))
    except Exception:  # noqa: BLE001
        return False, "NOT_A_PAIR"
    if pair not in set(cands):
        return False, f"OUT_OF_CANDIDATES:{pair}"
    return True, "OK"


# ------------------------------------------------------------
# 3. Dialogue話者判定(決定論 + LLM突合)
# ------------------------------------------------------------
_OPEN_CURLY_QUOTE = "“"


def quote_spans(para: str) -> list:
    """段落内の引用区間 [(start, end)] を出現順に返す。閉じ引用符で閉じた引用(QUOTE_RE)に加え、段落末尾の『閉じ引用符の無い開き引用』
    (英語の複数段落にわたる発言の慣習: 段落末は閉じず次段落を再び“で始める)を、開き“から段落末までの1引用として含める(FZIG 委任_13、
    OPEN-596)。これが無いと、閉じていない引用の本文が地の文(narrator)へ倒れ、発言者Voiceでなくナレーターで読まれる。
    閉じ括りが無いのは末尾の1区間だけ(それ以前はQUOTE_REが対で拾う)。引用符を含まない段落・全て閉じた段落の結果は従来と同一。"""
    spans = [(m.start(), m.end()) for m in QUOTE_RE.finditer(para)]
    tail_from = spans[-1][1] if spans else 0
    j = para.find(_OPEN_CURLY_QUOTE, tail_from)
    if j != -1:
        end = len(para.rstrip())
        if end > j + 1 and para[j + 1:end].strip():
            spans.append((j, end))
    return spans


def extract_quotes(paragraphs) -> list:
    quotes = []
    for p_idx, para in enumerate(paragraphs):
        for k, (s_, e_) in enumerate(quote_spans(para), start=1):
            quotes.append({"quote_id": f"q{p_idx}_{k}", "paragraph_index": p_idx, "ordinal": k,
                           "start": s_, "end": e_, "text": para[s_:e_]})
    return quotes


def deterministic_attribution(paragraphs, quotes, voice_keywords=None, story_key: str = "melos") -> dict:
    """Family C keyword窓判定。{quote_id: speaker or None}。None=キーワード該当なし(判定不能)。"""
    kw = voice_keywords or STORY_SPEAKER_CONFIG[story_key]["z_voice_keywords"]
    out = {}
    for q in quotes:
        v = fam_c.classify_quote_voice_window(paragraphs[q["paragraph_index"]], q["start"], q["end"], kw,
                                              default_voice="narrator")
        out[q["quote_id"]] = None if v == "narrator" else v
    return out


def reconcile_attribution(paragraphs, quotes, det: dict, llm: dict, story_key: str = "melos") -> dict:
    """全引用の突合。LLM結果が全quote_idを過不足なく含むこと、speakerがSPEAKERSであること。
    status: agree / llm_only(決定論=判定不能) / mismatch(決定論とLLMが異なる)。
    mismatchが1件でもあれば呼出側でSTOP(自動採用しない)。"""
    ids = [q["quote_id"] for q in quotes]
    problems = []
    if set(llm) != set(ids):
        problems.append({"missing": sorted(set(ids) - set(llm)), "extra": sorted(set(llm) - set(ids))})
    for k, v in llm.items():
        if v not in STORY_SPEAKER_CONFIG[story_key]["speakers"]:
            problems.append({"invalid_speaker": {k: v}})
    rows, final, mismatches = [], {}, []
    for q in quotes:
        qid = q["quote_id"]
        d, l = det.get(qid), llm.get(qid)
        para = paragraphs[q["paragraph_index"]]
        ctx = para[max(0, q["start"] - 60):q["end"] + 60]
        if l is None:
            status = "missing_llm"
        elif d is None:
            status = "llm_only"
        elif d == l:
            status = "agree"
        else:
            status = "mismatch"
        row = {"quote_id": qid, "paragraph_index": q["paragraph_index"], "text": q["text"],
               "context": ctx, "deterministic": d, "llm": l, "status": status}
        rows.append(row)
        if status == "mismatch":
            mismatches.append(row)
        elif status in ("agree", "llm_only"):
            final[qid] = l
    return {"rows": rows, "final": final, "mismatches": mismatches, "problems": problems,
            "ok": not mismatches and not problems and len(final) == len(ids)}


# ------------------------------------------------------------
# 4. clip計画(Family C plan_story_segments 全文1回 + id改名)
# ------------------------------------------------------------
def build_flat_chunks(paragraphs, speakers: dict) -> list:
    """(paragraph_index, voice, raw_text)のflat列。引用はspeakers[quote_id]のvoice、地の文はnarrator。
    空白のみのchunk(引用間の空白)は捨てる(単独clip化を防ぐ)。"""
    flat = []
    for p_idx, para in enumerate(paragraphs):
        pos, k = 0, 0
        for s_, e_ in quote_spans(para):
            k += 1
            if s_ > pos and para[pos:s_].strip():
                flat.append((p_idx, "narrator", para[pos:s_]))
            flat.append((p_idx, speakers[f"q{p_idx}_{k}"], para[s_:e_]))
            pos = e_
        if pos < len(para) and para[pos:].strip():
            flat.append((p_idx, "narrator", para[pos:]))
    return flat


def plan_clips(paragraphs, speakers: dict, b1: int, b2: int, level: str, narration_dir: str) -> list:
    """plan_story_segmentsを全文1回で呼び(force_split_before_paragraphs={b1,b2})、ids を
    full_story_part{n}_c{k} へ改名。Part境界を跨ぐclipがあればSTOP。"""
    flat = build_flat_chunks(paragraphs, speakers)
    segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={b1, b2})
    counters = {1: 0, 2: 0, 3: 0}
    clips = []
    for s in segs:
        parts = {part_of_paragraph(i, b1, b2) for i in s["source_paragraph_indices"]}
        if len(parts) != 1:
            raise FamilyZPlanStop(f"CLIP_CROSSES_PART_BOUNDARY: {s['id']} paragraphs={s['source_paragraph_indices']} "
                                  f"boundaries=({b1},{b2})")
        part = parts.pop()
        counters[part] += 1
        cid = f"full_story_part{part}_c{counters[part]}"
        speaker = s["voice"]
        clips.append({
            "id": cid, "part": part, "voice": speaker, "speaker": speaker,
            "voice_role": "narrator" if speaker == "narrator" else f"dialogue:{speaker}",
            "paragraph_index": s["source_paragraph_indices"][0],
            "source_paragraph_indices": s["source_paragraph_indices"],
            "text": s["tts_text"], "text_sha256": sha(s["tts_text"]), "word_count": s["word_count"],
            "split_reason": s["split_reason"], "warnings": s.get("warnings", []),
            "narration_path": f"{narration_dir.rstrip('/')}/{cid}.wav",
        })
    return clips


def comment_after_segment_ids(clips) -> dict:
    """Comment2=Part1-2間(Part1最後のclipの後)、Comment3=Part2-3間(Part2最後のclipの後)。
    Comment1はStory前(既存Z)なのでここには含めない。"""
    last = {}
    for c in clips:
        last[c["part"]] = c["id"]
    return {"2": last[1], "3": last[2]}


# ------------------------------------------------------------
# 5. Std/Adv 整列・同一本文
# ------------------------------------------------------------
def split_sentences(paragraphs) -> list:
    out = []
    for p in paragraphs:
        for s in re.split(r"(?<=[.!?])[\"”’']?\s+", fam_c.normalize_for_tts(p)):
            if s.strip():
                out.append(s.strip())
    return out


def avg_sentence_len(paragraphs) -> float:
    ss = split_sentences(paragraphs)
    return (sum(len(s.split()) for s in ss) / len(ss)) if ss else 0.0


def _norm_sentence(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def identical_sentence_ratio(std_paragraphs, adv_paragraphs) -> float:
    """Std文のうちAdvの正規化済み文と完全一致する割合(M8「同一本文」判定の式)。"""
    adv = {_norm_sentence(s) for s in split_sentences(adv_paragraphs)}
    ss = [_norm_sentence(s) for s in split_sentences(std_paragraphs)]
    ss = [s for s in ss if s]
    return (sum(1 for s in ss if s in adv) / len(ss)) if ss else 0.0


# ------------------------------------------------------------
# 6. Preview/Comment 決定論lint
# ------------------------------------------------------------
STORY_LINT_CONFIG = {
    "melos": {
        "forbidden_names": ["Selinuntius", "Dionysius", "Dionys", "Phidias",
                            "セリヌンティウス", "ディオニス", "ディオニュシオス", "フィロストラトス"],
        # 過剰ネタバレ語(結末の出来事)。Preview/Comment全てで禁止。
        "spoiler_ja": ["間に合", "救われ", "救い出", "解放され", "解き放", "改心", "心を改め", "処刑を免", "助かる",
                       "助かっ", "結末", "最後には", "最後に"],
        "spoiler_en": ["in the end", "just in time", "is freed", "set free", "set them free", "changes his mind",
                       "saves his friend", "let them both go", "is spared", "turns out", "finally reaches",
                       "arrives just"],
    },
    # 委任_01(FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01): 『開いた窓』用の同一機構(story_key別config)の値。新しい検査方式ではない。
    # forbidden_names=主人公(Framton)・keep_name人物(Vera、Seed source_essentials.key_roles)以外の人名(Preview/Commentに出さない、Melosと同方針)。
    # 2026-10-23(修正版B全体の正式採用): keep_name=trueのVera(カナ「ヴェラ」)はforbidden_namesから外した
    # (Std日本語Preview/Commentで「ヴェラ」が出てもblockingにしない)。短い名前は'several'等への部分一致誤検出を避けるため含めない。
    # spoiler_*=結末(少女の作り話・種明かし)を先回りする語。ユーザー2026-10-21指示「結末の意外性を損なう先回りの説明を入れない」に対応。
    "the_open_window": {
        "forbidden_names": ["Sappleton", "Ronnie", "サプルトン", "サップルトン", "ロニー"],
        # 結末(少女の作り話・種明かし・叔母の夫と弟の帰還後の展開)の先回りに必要な最小限の語のみ(Fable判定2026-10-21、一般語は入れない)。
        "spoiler_ja": ["作り話", "でっち上げ", "嘘", "うそ", "偽り", "種明かし", "ハッタリ"],
        "spoiler_en": ["made up", "made-up", "invented", "a lie", "was lying", "lied", "tall tale", "the truth is",
                       "romance at short notice", "a hoax"],
    },
    # 『二十年後』(FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_02): 同一機構(story_key別config)の値。
    # forbidden_names=主人公Bob・Jimmy(Seed source_essentials.key_roles)以外の人名(店主のBrady)。
    # spoiler_*=結末(警官の正体=Jimmy、Bobが指名手配犯で逮捕される、私服刑事の登場)を先回りする語(一般語は入れない)。
    "after_twenty_years": {
        "forbidden_names": ["Brady", "ブレイディ", "ブレイディー", "ブラディ"],
        "spoiler_ja": ["指名手配", "逮捕", "私服刑事", "警官の正体", "巡査の正体", "警官こそ", "巡査こそ", "警官が親友",
                       "親友が警官", "友人が警官", "ジミー本人"],
        "spoiler_en": ["wanted man", "wanted in chicago", "under arrest", "arrested", "plain clothes", "plain-clothes",
                       "was the policeman", "was the patrolman", "the policeman was jimmy", "the patrolman was jimmy",
                       "turns out", "the twist"],
    },    # 『賢者の贈り物』(FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01): 同一機構(story_key別config)の値。
    # forbidden_names=主人公Della・Jim(Seed source_essentials.key_roles)以外の人名(髪飾り店のSofronie、Jimの正式名Dillingham等)。
    # spoiler_*=結末(Jimが時計を売ったこと・贈り物の櫛・互いの贈り物が使えなくなること)を先回りする語(一般語は入れない)。
    "the_gift_of_the_magi": {
        "forbidden_names": ["Sofronie", "Dillingham", "ソフロニー", "ソフローニー", "ディリンガム", "ディリンハム"],
        "spoiler_ja": ["時計を売", "時計を手放", "時計を質", "櫛", "くしを", "コーム", "贈り物は使えな", "使えなくなる",
                       "無駄になる", "皮肉な結末"],
        "spoiler_en": ["sold his watch", "sold the watch", "sold his gold watch", "combs", "no watch", "useless gift",
                       "useless gifts", "turns out", "the twist", "the irony"],
    },
    # 『猿の手』(FAMILY-Z-MONKEYS-PAW-PRODUCTION-01 委任_01): 同一機構(story_key別config)の値。
    # forbidden_names=主人公Mr. White・Mrs. White・Herbert(Seed source_essentials.key_roles)以外の人名(Morris、会社名Maw and Meggins、Laburnam Villa等)。
    # spoiler_*=結末(第三の最後の願い・戻ってきたもの・無人の道)を先回りする語(一般語は入れない)。
    "the_monkeys_paw": {
        "forbidden_names": ["Morris", "Meggins", "Laburnam", "モリス", "メギンズ", "ラバーナム"],
        # Comment2/3は『すでに聞いた部分』を踏まえる設計(run_support_*)のため、Herbertの死・200ポンド・第二の願い自体は後半Commentに現れ得る。
        # よって先回りを禁じるのは結末(第三の最後の願い・戻ってきたもの・無人の道・種明かし語)に限る(一般語は入れない)。
        "spoiler_ja": ["三つ目の願い", "3つ目の願い", "三番目の願い", "最後の願い", "最後の三つ目", "墓から", "誰もいな",
                       "皮肉な結末", "種明かし"],
        "spoiler_en": ["third wish", "third and last", "last wish", "final wish", "back from the dead", "from the grave",
                       "nobody there", "no one there", "deserted road", "empty road", "turns out", "the twist", "the irony"],
    },
    # 『告げ口心臓』(FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_01): 同一機構(story_key別config)の値。
    # forbidden_names=原作に人名なし(語り手・老人・警官はすべて無名)。Preview/Commentに固有名詞を出さないよう、空listとし、Writer側の無名ルールで担保する。
    # spoiler_*=結末(語り手の自白・床板を剥がせ・心臓の音が実は老人のものである/幻聴であること・警官は聞こえていない)を先回りする語(一般語は入れない)。
    # Comment2/3は『すでに聞いた部分』を踏まえる設計(run_support_*)のため、老人の殺害・床下の隠蔽自体は後半Commentに現れ得る。
    "the_tell_tale_heart": {
        "forbidden_names": [],
        "spoiler_ja": ["自白", "告白する", "罪を認め", "罪を告白", "床板を剥が", "床板をはが", "床を剥が", "自分の心臓", "幻聴", "空耳",
                       "聞こえていたのは", "老人の心臓の音ではな", "皮肉な結末", "種明かし"],
        "spoiler_en": ["confess", "confession", "admits the deed", "admit the deed", "tear up the planks", "his own heart",
                       "own heartbeat", "imagined the sound", "only in his mind", "hallucinat", "turns out", "the twist", "the irony"],
    },
    # 『藪の中』(FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01): 同一機構(story_key別config)の値。
    # forbidden_names=主人公格3名(Tajomaru・Takehiro・Masago、Seed source_essentials.key_roles keep_name)以外の人名。原作の証言者は無名(役割名)。Takehiroの姓風の呼称(金沢の武弘=Kanazawa)は
    # 「First/Lastの一方のみ」方針(固有名詞ルール(d))により出さない。
    # spoiler_*=最後の証言(夫の死霊の語り: 自分で小刀を胸に刺した・見えない手が小刀を抜いた)と、真相の断定(真犯人・どれが本当)を先回りする語(一般語は入れない)。
    # Comment2/3は『すでに聞いた部分』を踏まえる設計(run_support_*)のため、多襄丸・真砂の語りの内容自体は後半Commentに現れ得る。
    "in_a_grove": {
        "forbidden_names": ["Kanazawa", "カナザワ", "金沢"],
        "spoiler_ja": ["自殺", "自害", "自ら胸", "自分で胸", "自分の胸を", "見えない手", "小刀を抜", "真犯人", "本当の犯人", "犯人は", "種明かし", "皮肉な結末"],
        "spoiler_en": ["killed himself", "kills himself", "stabbed himself", "stabs himself", "suicide", "took his own life", "unseen hand", "invisible hand",
                       "pulled the dagger", "drew the dagger", "the real killer", "the true killer", "the real murderer", "the true murderer",
                       "the truth is", "turns out", "the twist", "the irony"],
    },
}

_LINT_COMMON = [
    ("NEWS_WORD", re.compile(r"\bnews\b|ニュース|報道|記事", re.I)),
    ("IN_ONE_LINE", re.compile(r"in\s*one\s*line|イン\s*ワン\s*ライン", re.I)),
    ("POINT_LABEL", re.compile(r"\bpoint\s*(one|two|1|2)\b|ポイント", re.I)),
    ("STRUCTURE_LABEL", re.compile(r"\bpart\s*[0-9]|パート\s*[0-9０-９一二三]|full\s*story|key\s*phrases?|"
                                   r"キーフレーズ|\bcomment\s*[0-9]|\bpreview\b|プレビュー", re.I)),
    ("LITERATURE_INTRO_LABEL", re.compile(r"true\s+(crime\s+)?story|real\s+story|実話", re.I)),
]
_LINT_LISTEN_JA = re.compile(r"聞いてみ|聞いてください|お聞き|聞き取|聴いて|耳を|注目して|注意して聞")


def is_japanese_text(text: str) -> bool:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return False
    jp = sum(1 for c in chars if "぀" <= c <= "ヿ" or "一" <= c <= "鿿")
    return jp / len(chars) >= 0.3


def is_english_text(text: str) -> bool:
    chars = [c for c in text if not c.isspace()]
    return bool(chars) and sum(c.isascii() for c in chars) / len(chars) > 0.9


def lint_support_text(text: str, lang: str, story_key: str = "melos", *,
                      allow_listen_instruction_as_warn: bool = False, warn_out: list = None) -> list:
    """Preview/Comment出力の決定論lint。違反コードのlist(空=OK)。
    lang='ja'(Std)は聴取指示(Family C banned phrases + 聞いてみ等)も検査。
    lang='en'(Adv)はX B1のListening Focus役割が注目点を示す設計のため聴取指示は検査しない
    (news/In One Line/Point/構造ラベル/ネタバレ/名前/言語のみ)。
    allow_listen_instruction_as_warn(既定False=従来どおりblocking。FZQI委任_06/Opus_E R-E4 L-1): Z Stdの呼出側が
    明示したときのみ、lang='ja'のLISTEN_INSTRUCTIONをblockingにせずwarn_out(list)へ"LISTEN_INSTRUCTION"を追記する。
    他の違反コード(NEWS/IOL/Point/構造ラベル/ネタバレ/禁止名/言語)は常にblocking。"""
    if lang not in ("ja", "en"):
        raise ValueError(lang)
    v = []
    t = (text or "").strip()
    if not t:
        return ["EMPTY"]
    if lang == "ja" and not is_japanese_text(t):
        v.append("LANG_NOT_JA")
    if lang == "en" and not is_english_text(t):
        v.append("LANG_NOT_EN")
    for code, rx in _LINT_COMMON:
        if rx.search(t):
            v.append(code)
    if lang == "ja":
        if fam_c.FAMILY_C_A2_COMMENT_BANNED_PATTERNS_RE.search(t) or _LINT_LISTEN_JA.search(t):
            if allow_listen_instruction_as_warn:
                if warn_out is not None:
                    warn_out.append("LISTEN_INSTRUCTION")
            else:
                v.append("LISTEN_INSTRUCTION")
    cfg = STORY_LINT_CONFIG.get(story_key, {})
    low = t.lower()
    for nm in cfg.get("forbidden_names", []):
        if nm.lower() in low:
            v.append(f"FORBIDDEN_NAME:{nm}")
    for term in cfg.get("spoiler_" + lang, []):
        if term.lower() in low:
            v.append(f"SPOILER:{term}")
    return v


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
