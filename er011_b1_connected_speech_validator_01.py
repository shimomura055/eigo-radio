# ============================================================
# er011_b1_connected_speech_validator_01.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# ============================================================
# ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07 Track Aで
# VALIDATEDと判定された、B1 Connected Speech Validatorの
# Production版(ロジックはTrial07から無変更で移植)。
#
# ASRとcanonicalの文字列差分を、即座に「TTS誤発音」とは扱わない。
# まず、語境界で自然に起こるconnected speech(音の弱化・融合・
# 再分節)として説明可能かどうかを、ユーザーが正式承認した3パターンに
# 限定して判定する。
#
#   Pattern A: 歯擦音どうしの連続による前語末音の脱落
#              (例: studies /z/ + suggest /s/ -> "study suggests")
#              -> PASS(警告なし)
#   Pattern B: 同一・近接調音位置の破裂音連続による前語末音の脱落
#              (例: opened /d/ + to /t/ -> "open to")
#              -> PASS(警告なし)
#   Pattern C: 次語頭の子音が前語末へ再分節されたように見える追加型
#              (例: survey + suggest /s/ -> "surveys suggest")
#              -> PASS_WITH_WARNING(blockingしないが警告を残す)
#
# ユーザー正式決定により、この3パターン以外への一般化は行わない
# (新しい音韻パターンをこのmoduleの外で勝手に追加しないこと)。

from __future__ import annotations

import re

_VOICED_CONSONANT_LETTERS = set("bdgvzlmnr")


def final_s_sound(word: str) -> str | None:
    w = word.lower().rstrip(".,!?;:\"'")
    if w.endswith("es") and len(w) >= 3:
        stem = w[:-2]
    elif w.endswith("s") and len(w) >= 2:
        stem = w[:-1]
    else:
        return None
    if not stem:
        return None
    voiceless_endings = ("p", "t", "k", "f")
    if stem.endswith(voiceless_endings):
        return "/s/"
    return "/z/"


def final_ed_sound(word: str) -> str | None:
    w = word.lower().rstrip(".,!?;:\"'")
    if not w.endswith("ed") or len(w) < 3:
        return None
    stem = w[:-2]
    voiceless_endings = ("p", "k", "f", "s", "sh", "ch", "x")
    if stem.endswith(voiceless_endings):
        return "/t/"
    return "/d/"


_NON_TARGET_DIGRAPHS = ("sh", "ch", "th", "ph")


def initial_sound(word: str) -> str | None:
    """語頭の音を概算判定する。sh/ch/th/phは別音素のため対象外
    (false accept防止、ER-011-CONNECTED-SPEECH-TRIAL-07で発見・修正済み)。"""
    w = word.lower().lstrip(".,!?;:\"'")
    if not w:
        return None
    if w.startswith(_NON_TARGET_DIGRAPHS):
        return None
    if w.startswith("s"):
        return "/s/"
    if w.startswith("z"):
        return "/z/"
    if w.startswith("t"):
        return "/t/"
    if w.startswith("d"):
        return "/d/"
    return None


SIBILANTS = {"/s/", "/z/"}
STOPS_ALVEOLAR = {"/t/", "/d/"}


def s_suffix_label_if_match(long_word: str, short_word: str) -> str | None:
    """long_wordがshort_wordに-s/-es系接尾辞を付けた形(city->citiesの
    ような子音+y->ies綴り変化を含む)と一致する場合、どの接尾辞パターン
    だったかのラベルを返す。一致しなければNone。"""
    long_l, short_l = long_word.lower(), short_word.lower()
    if long_l == short_l + "s":
        return "s"
    if long_l == short_l + "es":
        return "es"
    if len(short_l) >= 2 and short_l[-1] == "y" and short_l[-2] not in "aeiou":
        if long_l == short_l[:-1] + "ies":
            return "ies(y->i+es spelling change)"
    return None


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text)


def word_diff(canonical: str, asr: str):
    c_words = tokenize(canonical)
    a_words = tokenize(asr)
    n = min(len(c_words), len(a_words))
    for i in range(n):
        if c_words[i].lower() != a_words[i].lower():
            prev_word = c_words[i - 1] if i > 0 else None
            next_word = c_words[i + 1] if i + 1 < len(c_words) else None
            return {
                "index": i, "canonical_word": c_words[i], "asr_word": a_words[i],
                "prev_word": prev_word, "next_word": next_word,
            }
    if len(c_words) != len(a_words):
        return {"index": n, "canonical_word": None, "asr_word": None,
                "prev_word": c_words[n - 1] if n > 0 else None,
                "next_word": None, "length_mismatch": True}
    return None


def classify_connected_speech(canonical: str, asr: str) -> dict:
    """canonicalとasrの最初の食い違いが、承認済み3パターンのいずれかで
    説明できるかを判定する。戻り値の new_judgment:
      CONNECTED_SPEECH_ACCEPT          -> PASS(警告なし)候補
      CONNECTED_SPEECH_RESEGMENTATION  -> PASS_WITH_WARNING候補
      UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING -> 既存判定を維持(非該当)
    """
    diff = word_diff(canonical, asr)
    if diff is None:
        return {"diff": None, "new_judgment": "NO_DIFF", "rule": None, "false_accept_risk": "N/A"}

    c_word = diff["canonical_word"]
    a_word = diff["asr_word"]
    next_word = diff["next_word"]

    result = {
        "diff": diff, "expected_phoneme_boundary": None, "rule": None,
        "new_judgment": "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING", "false_accept_risk": None,
    }

    if c_word is None or a_word is None or next_word is None:
        return result

    c_low = c_word.lower().rstrip(".,!?;:\"'")
    a_low = a_word.lower().rstrip(".,!?;:\"'")

    # --- Pattern A: 歯擦音どうしの連続 (studies suggest型) ---
    dropped = s_suffix_label_if_match(c_word, a_word)
    if dropped is not None:
        c_sound = final_s_sound(c_word)
        if c_sound in SIBILANTS:
            next_sound = initial_sound(next_word)
            if next_sound in SIBILANTS:
                result["rule"] = "Pattern_A_sibilant_sequence"
                result["expected_phoneme_boundary"] = f"{c_word}{c_sound} + {next_word}{next_sound}"
                result["new_judgment"] = "CONNECTED_SPEECH_ACCEPT"
                result["false_accept_risk"] = (
                    "低: canonical語からdropped接尾辞(-s/-es)を除いた残り全体がASR語と完全一致しており、"
                    "語幹自体の置き換わりではない。さらに次語頭が歯擦音である場合のみ発火する。")
                return result

    # --- Pattern B: 破裂音連続 (opened to型) ---
    if a_low and c_low.startswith(a_low) and c_low != a_low:
        dropped_b = c_low[len(a_low):]
        c_sound = final_ed_sound(c_word)
        if c_sound in STOPS_ALVEOLAR and dropped_b == "ed":
            next_sound = initial_sound(next_word)
            if next_sound in STOPS_ALVEOLAR:
                result["rule"] = "Pattern_B_stop_consonant_sequence"
                result["expected_phoneme_boundary"] = f"{c_word}{c_sound} + {next_word}{next_sound}"
                result["new_judgment"] = "CONNECTED_SPEECH_ACCEPT"
                result["false_accept_risk"] = (
                    "低: canonical語からdropped接尾辞(-ed)を除いた残り全体がASR語と完全一致しており、"
                    "語幹自体の置き換わりではない。さらに次語頭が同系列の破裂音である場合のみ発火する。")
                return result

    # --- Pattern C: 再分節(語末子音の追加型, survey suggest型) ---
    added = s_suffix_label_if_match(a_word, c_word)
    if added is not None:
        next_sound = initial_sound(next_word)
        if next_sound in SIBILANTS:
            result["rule"] = "Pattern_C_resegmentation_added_consonant"
            result["expected_phoneme_boundary"] = f"{c_word}(+{added}) + {next_word}{next_sound}"
            result["new_judgment"] = "CONNECTED_SPEECH_RESEGMENTATION"
            result["false_accept_risk"] = (
                "中: canonical語自体に追加された子音が、次語頭の歯擦音と同一種であることのみを根拠にしている。"
                "ASR語がcanonical語と無関係な別単語である可能性を完全には排除できないため、"
                "PASS_WITH_WARNING(blockingしないが警告は残す)とする。")
            return result

    result["false_accept_risk"] = "N/A(パターン非該当のため既存判定を維持)"
    return result
