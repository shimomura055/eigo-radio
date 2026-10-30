# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01: Flap-T発音同等性判定の Trial専用プロトタイプ(M1)。純関数・API 0・副作用なし。
# Status: Trial専用(Production未配線・未承認)。本fileはProduction経路(er006/er078/er104/er109)からimportされない。
# 方式M1: CMU辞書(pronouncing、既存er008 homophone_enと同一ライブラリ)の音素列を用い、
#   (1) 差分が「1:1の語置換」のみ (2) 両語の音素列が同長で、異なる位置が全てT<->Dの入替のみ
#   (3) 異なる各位置が両語ともflap環境 = 直前が強勢母音(強勢>=1)かつ直後が無強勢母音 かつ 直前がR/鼻音等でない
#   (4) 直後が AH0+N(音節的n: button/eaten型。声門閉鎖化しやすくflapにならない)でない
#   (5) canonicalのCMU強勢読みが1つ(strict, er008 P-01と同原則)かつASR語は代表(先頭)強勢読み
#   (6) 直前の強勢母音が AY/AW(Canadian raising系: writer/rider, title/tidal)なら自動救済せず REQUIRES_EXTRA_EVIDENCE
#   全て満たしたとき RESCUE。それ以外は NO_RESCUE / NOT_APPLICABLE / REQUIRES_EXTRA_EVIDENCE(いずれも従来どおりNG扱い)。
from __future__ import annotations
import difflib
import re
from dataclasses import dataclass, field

try:
    import pronouncing
except ImportError:      # 判定不能=非救済(fail-closed)
    pronouncing = None

VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
RAISING_SENSITIVE = {"AY", "AW"}     # 母音差が残りうる核(辞書では同一でも実音声で区別が出る)
_TOK = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOK.findall(text or "")]


def _readings(word: str):
    if pronouncing is None:
        return None
    vs = pronouncing.phones_for_word(word.lower())
    return [tuple(v.split()) for v in vs] if vs else None


def _s2(ph: tuple) -> tuple:           # 強勢2値化(1,2->1 / 0->0)
    return tuple(re.sub(r"([A-Z]+)[12]$", r"\g<1>1", p) for p in ph)


def _base(p: str) -> str:
    return re.sub(r"\d$", "", p)


def _is_vowel(p: str) -> bool:
    return _base(p) in VOWELS


def _stress(p: str) -> int:
    m = re.search(r"(\d)$", p)
    return int(m.group(1)) if m else -1


@dataclass
class PairResult:
    canonical: str
    asr: str
    decision: str              # RESCUE / NO_RESCUE / REQUIRES_EXTRA_EVIDENCE
    reason: str
    detail: dict = field(default_factory=dict)


@dataclass
class FlapResult:
    decision: str              # RESCUE / NO_RESCUE / REQUIRES_EXTRA_EVIDENCE / NOT_APPLICABLE
    reason: str
    pairs: list = field(default_factory=list)


def flap_env(ph: tuple, i: int) -> tuple[bool, str]:
    """ph[i]がT/Dで、flap環境(強勢母音 _ 無強勢母音)か。"""
    if i <= 0 or i >= len(ph) - 1:
        return False, "edge_of_word"
    prev, nxt = ph[i - 1], ph[i + 1]
    if not _is_vowel(prev) or _stress(prev) < 1:
        return False, "prev_not_stressed_vowel"
    if not _is_vowel(nxt) or _stress(nxt) != 0:
        return False, "next_not_unstressed_vowel"
    if _base(nxt) == "AH" and i + 2 < len(ph) and ph[i + 2] == "N":
        return False, "syllabic_n_glottalization"
    return True, "ok"


def judge_pair(canonical: str, asr: str) -> PairResult:
    c, a = canonical.lower(), asr.lower()
    rc, ra = _readings(c), _readings(a)
    if rc is None or ra is None:
        return PairResult(c, a, "NO_RESCUE", "cmu_unresolved")
    sc = {_s2(r) for r in rc}
    if len(sc) != 1:
        return PairResult(c, a, "NO_RESCUE", "canonical_multiple_readings")      # P-01相当(putting等)
    pc = next(iter(sc))
    pa = _s2(ra[0])                                                             # ASR語は代表読み
    if len(pc) != len(pa):
        return PairResult(c, a, "NO_RESCUE", "phoneme_length_differs")
    diff = [i for i, (x, y) in enumerate(zip(pc, pa)) if x != y]
    if not diff:
        return PairResult(c, a, "NO_RESCUE", "phonemes_identical_not_flap_case")   # 同音は既存homophone層の担当
    sens = None
    for i in diff:
        if {_base(pc[i]), _base(pa[i])} != {"T", "D"}:
            return PairResult(c, a, "NO_RESCUE", "non_td_phoneme_difference", {"pos": i, "c": pc[i], "a": pa[i]})
        e1, w1 = flap_env(pc, i)
        e2, w2 = flap_env(pa, i)
        if not (e1 and e2):
            return PairResult(c, a, "NO_RESCUE", f"not_flap_environment:{w1 if not e1 else w2}", {"pos": i})
        if _base(pc[i - 1]) in RAISING_SENSITIVE:
            sens = _base(pc[i - 1])
    if sens:
        return PairResult(c, a, "REQUIRES_EXTRA_EVIDENCE", f"raising_sensitive_nucleus:{sens}",
                          {"canonical_phones": " ".join(pc), "asr_phones": " ".join(pa)})
    return PairResult(c, a, "RESCUE", "flap_t_equivalent", {"canonical_phones": " ".join(pc), "asr_phones": " ".join(pa)})


def evaluate(canonical_text: str, asr_text: str) -> FlapResult:
    ct, at = tokens(canonical_text), tokens(asr_text)
    ops = [o for o in difflib.SequenceMatcher(a=ct, b=at, autojunk=False).get_opcodes() if o[0] != "equal"]
    if not ops:
        return FlapResult("NOT_APPLICABLE", "no_token_difference")
    pairs = []
    for tag, i1, i2, j1, j2 in ops:
        if tag != "replace" or (i2 - i1) != (j2 - j1):
            return FlapResult("NOT_APPLICABLE", f"non_1to1_difference:{tag}")
        for k in range(i2 - i1):
            pairs.append(judge_pair(ct[i1 + k], at[j1 + k]))
    decisions = {p.decision for p in pairs}
    if decisions == {"RESCUE"}:
        return FlapResult("RESCUE", "all_differences_flap_t_equivalent", pairs)
    if "NO_RESCUE" in decisions:
        return FlapResult("NO_RESCUE", next(p.reason for p in pairs if p.decision == "NO_RESCUE"), pairs)
    return FlapResult("REQUIRES_EXTRA_EVIDENCE", next(p.reason for p in pairs if p.decision == "REQUIRES_EXTRA_EVIDENCE"), pairs)


# ---- Voice適用範囲(fail-closed): 米音(flap実観測)が確認されたVoiceだけ許可。既定=空集合=どのVoiceにも不適用 ----
def voice_applicable(voice: str | None, confirmed_voices=frozenset()) -> bool:
    """confirmed_voices は Voice実音声のflap実証(保存ASR転写のd綴り実例 or Voice probe)で確認済みのVoice名集合。
    未指定・Voice不明(None/空)・未確認Voiceは False(未確認Voiceを米国英語と決めつけない)。"""
    return bool(voice) and voice in confirmed_voices
