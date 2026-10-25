# JA-ASR-FALSE-NG-ROOT-CAUSE-01 Phase 2 prototype (research only; NOT imported by Production; API 0).
# Design-A candidate comparator = existing mechanism's missing pieces:
#   A1 digit-group comma strip ("8,900" == "8900"; 3-digit groups only)
#   A2 particle reading (助詞 は->わ / へ->え) in the morph reading (unidic 'kana' gives ハ, 'pron' gives ワ)
#   A3 numeric atoms replaced by value tokens on BOTH sides (value-guard must be EQUAL), remainder compared by *reading*
# Strict: no voicing leniency, no kanji candidate enumeration, ANY remaining reading difference => not equal.
from __future__ import annotations
import re, sys, unicodedata
sys.path.insert(0, ".")
import jaconv
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as vl
import er078_asr_value_guard_01 as vg

_COMMA = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")
_PARTICLE_PRON = {"は": "ワ", "へ": "エ"}


def strip_digit_commas(t: str) -> str:
    return _COMMA.sub("", unicodedata.normalize("NFKC", t or ""))


def value_form(t: str) -> str | None:
    t = strip_digit_commas(t)
    atoms = [a for a in vg.extract_atoms_ja(t) if a.kind in ("num", "frac")]
    if not atoms:
        return t
    out, pos = [], 0
    for a in atoms:
        if a.start < pos:
            return None
        out.append(t[pos:a.start]); out.append(f"【値{a.kind}:{a.value}:{a.unit}】"); pos = a.end
    out.append(t[pos:])
    return "".join(out)


def pron_hira(t: str) -> str:
    out = []
    for w in vl._get_tagger()(t):
        f = w.feature
        if getattr(f, "pos1", "") == "助詞" and w.surface in _PARTICLE_PRON:
            out.append(_PARTICLE_PRON[w.surface]); continue
        k = getattr(f, "kana", None) or getattr(f, "pron", None) or w.surface
        out.append(k)
    return jaconv.kata2hira("".join(out))


def design_a(canon: str, asr: str) -> tuple[bool, str]:
    """(equal, why). Value guard must be EQUAL/NO_VALUES, negation equal, remainder *pronunciation* equal."""
    g = vg.value_guard(canon, asr, "ja")
    if g.kind not in (vg.EQUAL, vg.NO_VALUES):
        return False, f"value_guard={g.kind}"
    from er078_asr_unified_judge_01 import negation_diff
    if negation_diff(canon, asr, "ja"):
        return False, "negation_diff"
    cf, af = value_form(canon), value_form(asr)
    if cf is None or af is None:
        return False, "value_form_none"
    c, a = javal.normalize_ja(cf), javal.normalize_ja(af)
    if c == a:
        return True, "surface_equal_after_value_form"
    if pron_hira(c) == pron_hira(a):
        return True, "pron_equal_after_value_form"
    return False, "pron_differs"
