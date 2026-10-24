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

import difflib
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
    # ASRが出す ’(U+2019) を ' に正規化して語構成文字として扱う(他層 er006:497,1022 / er006_m1:60,331 と同じ。
    # OPEN-500: 未対応だと you’ve が you,ve に割れてF1 residualが偽残差になる)。
    return re.findall(r"[A-Za-z']+", (text or "").replace("’", "'").replace("‘", "'"))


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


def _classify_first_diff(canonical: str, asr: str) -> dict:
    """(F1以前の classify_connected_speech 本体。Pattern A/B/C判定は無変更。)
    canonicalとasrの最初の食い違いが、承認済み3パターンのいずれかで
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


# ============================================================
# F1(ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03、2026-10-13)
# 「最初の食い違い1か所だけでACCEPT」欠陥の是正。新しい許容ルールは作らない。
#   - 全差分を列挙し、各差分を既存Pattern A/B/C(_classify_first_diff、無変更)で個別判定
#   - 許容(benign)は冠詞(a/an/the)のみの差と、規則的単複(_is_benign_plural_pair)の1:1差のみ(OF-160)
#   - 説明できない差分=残差。残差0のときのみ従来ACCEPT/RESEGMENTATION。残差ありはUNCLASSIFIED
#   - 限定方向のみ: 従来のUNCLASSIFIED/NO_DIFFは判定不変、従来のACCEPT/RESEGは残差0のときのみ維持
# ============================================================
F1_VERSION = "F1-2026-10-13"
_ARTICLES = {"a", "an", "the"}
_OK_JUDGMENTS = ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")
_UNCL = "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING"
_DIGIT_RE = re.compile(r"\d+(?:[.,]\d+)*")


def _plural_pair_ok(a: str, b: str) -> bool:
    try:
        import er006_preprod_hardening_01_validation as _val  # 遅延import(循環回避)
        return bool(_val._is_benign_plural_pair(a, b))
    except Exception:
        return False  # 判定不能は残差側(厳格側)


def _benign_span(cspan: list[str], aspan: list[str]) -> bool:
    """benign=冠詞のみの差、または冠詞を除いた残りが規則単複の1:1差。他の機能語差(are/were, in/on, and/or等)は残差。"""
    c = [w for w in cspan if w not in _ARTICLES]
    a = [w for w in aspan if w not in _ARTICLES]
    if not c and not a:
        return True
    return len(c) == 1 and len(a) == 1 and _plural_pair_ok(c[0], a[0])


def _pair_classify(c_word: str, a_word: str, next_word: str | None) -> dict:
    """1語対を既存Pattern A/B/C(_classify_first_diff)で判定する(next_wordはcanonical側の次語)。"""
    if next_word is None:
        return {"new_judgment": _UNCL, "rule": None}
    return _classify_first_diff(f"{c_word} {next_word}", f"{a_word} {next_word}")


def classify_connected_speech(canonical: str, asr: str) -> dict:
    """F1版: 全差分を点検する。戻り値 new_judgment:
      CONNECTED_SPEECH_ACCEPT / CONNECTED_SPEECH_RESEGMENTATION -> 全差分が説明できる(残差0)ときのみ
      UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING -> 既存判定を維持(非該当、または残差あり)
    追加キー(後方互換、キー追加のみ): f1_version / f1_all_diffs / f1_explained / f1_residual / f1_residual_kind。
    残差ありで元が最初の1か所でACCEPTだったケースは、diffに「最初の残差」を入れる(説明済み差分ではない)。"""
    base = _classify_first_diff(canonical, asr)
    out = dict(base)
    out["f1_version"] = F1_VERSION
    out["f1_all_diffs"] = []
    out["f1_explained"] = []
    out["f1_residual"] = []
    out["f1_residual_kind"] = "none"
    if base.get("new_judgment") == "NO_DIFF":
        return out

    cw, aw = tokenize(canonical), tokenize(asr)
    cl, al = [w.lower() for w in cw], [w.lower() for w in aw]
    sm = difflib.SequenceMatcher(a=cl, b=al, autojunk=False)
    all_diffs, explained, residual = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        all_diffs.append({"op": tag, "index": i1, "canonical": cw[i1:i2], "asr": aw[j1:j2]})
        c_pos = [i for i in range(i1, i2) if cl[i] not in _ARTICLES]
        a_pos = [j for j in range(j1, j2) if al[j] not in _ARTICLES]
        # replaceブロックは冠詞(benign)を除いた語数が同数なら、位置ごとに個別判定する
        if tag == "replace" and c_pos and len(c_pos) == len(a_pos):
            for ci, aj in zip(c_pos, a_pos):
                if cl[ci] == al[aj]:
                    continue
                nxt = cw[ci + 1] if ci + 1 < len(cw) else None
                r = _pair_classify(cw[ci], aw[aj], nxt)
                if r.get("new_judgment") in _OK_JUDGMENTS:
                    explained.append({"index": ci, "canonical": cw[ci], "asr": aw[aj], "rule": r.get("rule"),
                                      "judgment": r["new_judgment"],
                                      "expected_phoneme_boundary": r.get("expected_phoneme_boundary")})
                elif not _benign_span([cl[ci]], [al[aj]]):
                    residual.append({"op": "replace", "index": ci, "canonical": [cw[ci]], "asr": [aw[aj]]})
        elif not _benign_span(cl[i1:i2], al[j1:j2]):
            residual.append({"op": tag, "index": i1, "canonical": cw[i1:i2], "asr": aw[j1:j2]})
    # 数字: csv3.tokenizeは数字を落とすため、数字列の不一致は別途残差にする(安全側)
    if _DIGIT_RE.findall(canonical) != _DIGIT_RE.findall(asr):
        residual.append({"op": "number", "index": None, "canonical": _DIGIT_RE.findall(canonical),
                         "asr": _DIGIT_RE.findall(asr)})
    residual.sort(key=lambda d: (d["index"] is None, d["index"] or 0))

    out["f1_all_diffs"] = all_diffs
    out["f1_explained"] = explained
    out["f1_residual"] = residual
    out["f1_residual_kind"] = "content" if residual else "none"

    if base.get("new_judgment") in _OK_JUDGMENTS:
        if residual or not explained:
            out["new_judgment"] = _UNCL
            out["rule"] = None
            out["expected_phoneme_boundary"] = None
            out["false_accept_risk"] = "F1: 説明できない残差差分があるため連結発音ACCEPTしない(既存判定へ戻す)"
            if residual:
                r0 = residual[0]
                idx = r0["index"]
                out["diff"] = {
                    "index": idx,
                    "canonical_word": r0["canonical"][0] if r0["canonical"] and idx is not None else None,
                    "asr_word": r0["asr"][0] if r0["asr"] and idx is not None else None,
                    "prev_word": cw[idx - 1] if idx else None,
                    "next_word": cw[idx + 1] if idx is not None and idx + 1 < len(cw) else None,
                    "f1_residual_first": True,
                }
        else:
            kinds = {e["judgment"] for e in explained}
            out["new_judgment"] = ("CONNECTED_SPEECH_RESEGMENTATION" if "CONNECTED_SPEECH_RESEGMENTATION" in kinds
                                   else "CONNECTED_SPEECH_ACCEPT")
            out["rule"] = "+".join(sorted({e["rule"] for e in explained}))
            out["expected_phoneme_boundary"] = " | ".join(e["expected_phoneme_boundary"] for e in explained)
    return out
