# ============================================================
# er011_no18_b1_connected_speech_trial_07.py
# ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07 Track A
# ============================================================
# ASRとcanonicalの文字列差分を、即座に「TTS誤発音」とは扱わない。
# まず、語境界で自然に起こるconnected speech(音の弱化・融合・
# 再分節)として説明可能かどうかを、今回タスクで明示的に与えられた
# 3パターンに限定して判定する。
#
#   Pattern A: 歯擦音どうしの連続による前語末音の脱落
#              (例: studies /z/ + suggest /s/ → "study suggests")
#   Pattern B: 同一・近接調音位置の破裂音連続による前語末音の脱落
#              (例: opened /d/ + to /t/ → "open to")
#   Pattern C: 次語頭の子音が前語末へ再分節されたように見える追加型
#              (例: survey + suggest /s/ → "surveys suggest")
#
# 新しい音韻パターンをこのTrialの中で勝手に追加することはしない
# (§2禁止事項)。判定はすべて既存の実データ(既存audio・既存ASR結果)
# に対して行い、新規TTS/ASR呼び出しは行わない。
#
# Production配線は一切行わない。OPEN-107のProduction仕様(Ending-Clarity
# fallback)も変更しない。本Trialの結果だけではProduction採用を決定しない。

from __future__ import annotations

import re

# ----------------------------------------------------------------
# 最小限の語末/語頭 音素推定(このTrialで扱う3パターンの検証に
# 必要な範�囲のみ。一般的な英語発音規則エンジンではない)
# ----------------------------------------------------------------

_VOICED_CONSONANT_LETTERS = set("bdgvzlmnr")  # 有声子音字(概算)


def final_s_sound(word: str) -> str | None:
    """語末が -s / -es の場合、その音が /s/ か /z/ かを概算判定する。
    直前の音が無声子音なら/s/、それ以外(有声子音・母音)なら/z/。
    (英語の一般的な規則の簡略版。本Trialの3ケース検証に十分な範囲。)"""
    w = word.lower().rstrip(".,!?;:\"'")
    if w.endswith("es") and len(w) >= 3:
        stem = w[:-2]
    elif w.endswith("s") and len(w) >= 2:
        stem = w[:-1]
    else:
        return None
    if not stem:
        return None
    prev = stem[-1]
    voiceless_endings = ("p", "t", "k", "f")
    if stem.endswith(voiceless_endings):
        return "/s/"
    return "/z/"


def final_ed_sound(word: str) -> str | None:
    """語末が -ed の場合、その音が /d/ か /t/ かを概算判定する。"""
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
    """語頭の音を概算判定する。sh/ch/th/phのような、綴り上はs/tで
    始まって見えても実際には別の音素(esh, tesh, theta等)になる
    digraphは、歯擦音/破裂音のどちらとも判定しない(false accept防止)。"""
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


def s_suffix_variants(short_word: str) -> list[str]:
    """short_wordに英語の-s/-es接尾辞を付けた場合にあり得る綴りの
    バリエーションを返す(city→cities のような子音+y→iesの綴り変化を含む)。
    音としては、どの形でも語末に歯擦音(/s/または/z/)が1つ追加される
    だけであり、綴り変化そのものは別の音素を表すものではない。"""
    w = short_word
    variants = {w + "s", w + "es"}
    if len(w) >= 2 and w[-1].lower() == "y" and w[-2].lower() not in "aeiou":
        variants.add(w[:-1] + "ies")
    return list(variants)


def s_suffix_label_if_match(long_word: str, short_word: str) -> str | None:
    """long_wordがshort_wordに-s/-es系接尾辞を付けた形(city→citiesのような
    子音+y→ies綴り変化を含む)と一致する場合、どの接尾辞パターンだったかの
    ラベルを返す。一致しなければNone。"""
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
    """canonicalとasrの単語列を単純アライメントし、最初に食い違う
    (canonical_word, asr_word, index, prev_word, next_word_canonical)を返す。
    完全一致ならNoneを返す。"""
    c_words = tokenize(canonical)
    a_words = tokenize(asr)
    n = min(len(c_words), len(a_words))
    for i in range(n):
        if c_words[i].lower() != a_words[i].lower():
            prev_word = c_words[i - 1] if i > 0 else None
            next_word = c_words[i + 1] if i + 1 < len(c_words) else None
            return {
                "index": i,
                "canonical_word": c_words[i],
                "asr_word": a_words[i],
                "prev_word": prev_word,
                "next_word": next_word,
            }
    if len(c_words) != len(a_words):
        return {"index": n, "canonical_word": None, "asr_word": None,
                "prev_word": c_words[n - 1] if n > 0 else None,
                "next_word": None, "length_mismatch": True}
    return None


def classify_connected_speech(canonical: str, asr: str) -> dict:
    diff = word_diff(canonical, asr)
    if diff is None:
        return {"diff": None, "new_judgment": "NO_DIFF", "old_judgment": "PASS",
                "false_accept_risk": "N/A", "rule": None}

    c_word = diff["canonical_word"]
    a_word = diff["asr_word"]
    next_word = diff["next_word"]

    result = {
        "diff": diff,
        "expected_phoneme_boundary": None,
        "rule": None,
        "new_judgment": "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING",
        "old_judgment": "TRUE_CONTENT_MISMATCH",
        "false_accept_risk": None,
    }

    if c_word is None or a_word is None or next_word is None:
        return result

    c_low = c_word.lower().rstrip(".,!?;:\"'")
    a_low = a_word.lower().rstrip(".,!?;:\"'")

    # --- Pattern A: 歯擦音どうしの連続 (studies suggest 型) ---
    # canonical語尾が -s/-es(歯擦音、city→citiesのような綴り変化も含む)、
    # ASR語がその歯擦音を欠いた形と一致、かつ次語頭が歯擦音。
    dropped = s_suffix_label_if_match(c_word, a_word)
    if dropped is not None:
        c_sound = final_s_sound(c_word)
        if c_sound in SIBILANTS:
            next_sound = initial_sound(next_word)
            if next_sound in SIBILANTS:
                result["rule"] = "Pattern_A_sibilant_sequence"
                result["expected_phoneme_boundary"] = f"{c_word}{c_sound} + {next_word}{next_sound}"
                result["new_judgment"] = "CONNECTED_SPEECH_ACCEPT"
                result["old_judgment"] = "TRUE_CONTENT_MISMATCH"
                result["false_accept_risk"] = (
                    "低: canonical語からdropped接尾辞(-s/-es)を除いた残り全体が"
                    "ASR語と完全一致しており、語幹自体の置き換わりではない。"
                    "さらに次語頭が歯擦音である場合のみ発火する。"
                )
                return result

    # --- Pattern B: 破裂音連続 (opened to 型) ---
    if a_low and c_low.startswith(a_low) and c_low != a_low:
        dropped = c_low[len(a_low):]
        c_sound = final_ed_sound(c_word)
        if c_sound in STOPS_ALVEOLAR and dropped == "ed":
            next_sound = initial_sound(next_word)
            if next_sound in STOPS_ALVEOLAR:
                result["rule"] = "Pattern_B_stop_consonant_sequence"
                result["expected_phoneme_boundary"] = f"{c_word}{c_sound} + {next_word}{next_sound}"
                result["new_judgment"] = "CONNECTED_SPEECH_ACCEPT"
                result["old_judgment"] = "TRUE_CONTENT_MISMATCH"
                result["false_accept_risk"] = (
                    "低: canonical語からdropped接尾辞(-ed)を除いた残り全体が"
                    "ASR語と完全一致しており、語幹自体の置き換わりではない。"
                    "さらに次語頭が同系列の破裂音である場合のみ発火する。"
                )
                return result

    # --- Pattern C: 再分節(語末子音の追加型, survey suggest 型) ---
    added = s_suffix_label_if_match(a_word, c_word)
    if added is not None:
            next_sound = initial_sound(next_word)
            if next_sound in SIBILANTS:
                result["rule"] = "Pattern_C_resegmentation_added_consonant"
                result["expected_phoneme_boundary"] = f"{c_word}(+{added}) + {next_word}{next_sound}"
                result["new_judgment"] = "CONNECTED_SPEECH_RESEGMENTATION"
                result["old_judgment"] = "TRUE_CONTENT_MISMATCH"
                result["false_accept_risk"] = (
                    "中: canonical語自体に追加された子音が、次語頭の歯擦音と"
                    "同一種であることのみを根拠にしている。ASR語がcanonical語と"
                    "無関係な別単語である可能性を完全には排除できないため、"
                    "PASS_WITH_WARNING(blockingしないが警告は残す)候補とする。"
                )
                return result

    # どのパターンにも該当しない場合は、既存の判定(TRUE_CONTENT_MISMATCH等)
    # をそのまま維持する。
    result["false_accept_risk"] = "N/A(パターン非該当のため新判定を適用しない)"
    return result


# ----------------------------------------------------------------
# Trial対象ケース(すべて既存音声・既存ASR結果の再利用)
# ----------------------------------------------------------------

CASES = {
    "case1_studies_suggest": {
        "canonical": "The studies suggest that a phone can affect attention even when you do not check it. How does this pull appear in everyday life, especially for teenagers?",
        "asr": "The study suggests that a phone can affect attention even when you do not check it. How does this pull appear in everyday life, especially for teenagers?",
        "source": "B1 comment_2 (open110_comment2_ending_clarity_runtime_evidence_04.json, attempt1-3全て同一)",
    },
    "case2_opened_to": {
        "canonical": "Your phone does not have to be opened to become part of the task. In these studies, attention was pulled by the sound and affected by the silent device, which helps explain why ignoring a notification can feel harder than it looks.",
        "asr": "Your phone does not have to be open to become part of the task. In these studies, attention was pulled by the sound and affected by the silent device, which helps explain why ignoring a notification can feel harder than it looks.",
        "source": "OPEN-107 opened_tts_diagnostic_trial_01 cond7 attempt3(3回中1回)",
    },
    "case3_survey_suggest": {
        "canonical": "This story is not only about choosing to check a phone. The studies and the survey suggest that a phone can affect people even when they do not check it. Now, let's look more closely at what may be happening in these situations.",
        "asr": "This story is not only about choosing to check a phone. The studies and the surveys suggest that a phone can affect people even when they do not check it. Now let's look more closely at what may be happening in these situations.",
        "source": "OPEN-110 survey_diagnostic_04 cond1 attempt3(3回中1回)",
    },
}

# --- false accept riskの検証用: 本当のcontent mismatchの陰性対照ケース ---
NEGATIVE_CONTROL_CASES = {
    "control1_unrelated_word_swap": {
        "canonical": "The report shows clear evidence about the trend.",
        "asr": "The report shows clear evidence about the trend today.",
        "note": "文末に無関係な語が追加されただけ(歯擦音関連なし)。Pattern Cの条件(追加子音がs/esのみ、次語頭が歯擦音)を満たさないため非該当となるべき。",
    },
    "control2_real_mispronunciation_same_length": {
        "canonical": "The studies suggest a strong link between sleep and memory.",
        "asr": "The stories suggest a strong link between sleep and memory.",
        "note": "studies→storiesは語幹自体が別単語に変わっている(studie→storie)。dropped/added接尾辞ルールに該当せず、Pattern A/Cどちらにも該当しないべき(真のcontent mismatchとして従来通り扱われるべき)。",
    },
    "control3_survey_to_unrelated_plural": {
        "canonical": "The survey shows useful results for parents.",
        "asr": "The surveys show useful results for parents.",
        "note": "「survey」→「surveys」だが次語が showsではなくshow(動詞も複数呼応で変化)であり、次語頭は歯擦音でない(sh-)。Pattern Cの'次語頭が歯擦音'条件を満たさないため非該当となるべき。",
    },
}


def main():
    print("=== Track A: 3ケースの判定 ===")
    case_results = {}
    for case_id, c in CASES.items():
        r = classify_connected_speech(c["canonical"], c["asr"])
        case_results[case_id] = {**c, "classification": r}
        print(case_id, "->", r["rule"], "|", r["new_judgment"])

    print()
    print("=== false accept risk検証: 陰性対照ケース ===")
    control_results = {}
    for case_id, c in NEGATIVE_CONTROL_CASES.items():
        r = classify_connected_speech(c["canonical"], c["asr"])
        control_results[case_id] = {**c, "classification": r}
        print(case_id, "->", r["rule"], "|", r["new_judgment"])

    import json
    import os
    out_dir = "er011_output/b1_connected_speech_trial_07"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/connected_speech_trial_results.json", "w", encoding="utf-8") as f:
        json.dump({"cases": case_results, "negative_controls": control_results}, f, ensure_ascii=False, indent=2)
    print("\nwrote", f"{out_dir}/connected_speech_trial_results.json")


if __name__ == "__main__":
    main()
