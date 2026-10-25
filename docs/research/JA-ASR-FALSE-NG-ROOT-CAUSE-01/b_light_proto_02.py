# JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08 ②B-light prototype v2 (research/DEV only; NOT imported by Production; API 0; LLM 0).
# v1 (b_light_proto_01.py, sha256 5b715f8e…, 凍結・変更なし) からの差分 = Opus条件Aレビュー(OPUS_REVIEW_01_BLIGHT.md)の反映:
#   V2-1 (M-1 明示化): 読み規則は v2 (proto_reading_compare_02: pron_hira 助詞は→わ/へ→えのみ + c2_blocked) を import して使う。
#        これは『βの採用は v2 の読み規則の採用を含む』ことを意味するため、READING_RULE_V2 定数・audit['reading_rule']・設計文書に明記する。
#        参考として reading_rule="strict"(normalize_ja 完全一致のみ=v2読み規則に依存しない)を用意し、評価で並記する。
#   V2-2 (M-2 隔離): composite の寄与印 `composite_contributed(aj)` と再利用判定 `composite_reuse_decision(entry, flag_on, scope)` を追加。
#        scope外/flag OFFは先にblock、scope内は保存S転写で composite_judge を再実行、S転写・engine・wav sha が無ければ fail-closed。
#        composite_judge は secondary_meta(engine, wav_sha256) が無ければ fail-closed(保存を配線前提にする)。
#   V2-3 (M-3 複数atom): 原稿とSecondaryの値atom列を『位置・個数・順序』で照合(value_guardの結果に加えて二重化)。atomごとのPrimary照合は従来どおり。
#   V2-4 (R-1): Secondaryの『値atomを除いた残り』の読みがPrimary(=原稿)の読みと食い違う場合(a3『杉野氏』型)は警告 + 試聴必須
#        (secondary_reading_conflict="warn" 既定。"veto" でNG)。R-2: 断片説明(GARBLE_EXPLAINED)も試聴必須(TTSの不自然な間の可能性)。
#   V2-5 (R-3): 断片説明は『観測形』に限定: F-A=数字のみrunの**2断片**で前断片が `[1-9]0+`(d×10^k, k>=1)。3断片は実例が出るまで無効。
#        F-B=前断片(数字)が同じく `[1-9]0+`、後断片は漢数字(万億兆なし)。
#   V2-6 (R-4): 原稿・Secondaryの値atomは『数字・漢数字表記』に限る(かな数詞・あいまい語[amb]が含まれればNG)。OPEN-523/524(Secondary値ガード既知不具合)を継承しない。
#   V2-7 (R-7): audit に reading_source='primary' / value_source='secondary' / secondary_engine / secondary_wav_sha256 / 保存S転写 / reading_rule を残す。
#   V2-8 (R-8): フック①の事前判定は `precheck_composite`(戻り型 PrecheckResult。`.equal` を持たない=最終判定に流用できない)。
#        composite_judge は precheck 由来のmetaを拒否する。
# Production関数は import して使い、複製しない。最終ANDゲートは呼出側が常に通す(本関数はPASS候補を返すだけ)。
from __future__ import annotations
import json, os, re, sys, unicodedata
from dataclasses import dataclass, field
from fractions import Fraction

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_value_guard_01 as vg
from er078_asr_unified_judge_01 import negation_diff
import proto_reading_compare_02 as P2

COMPOSITE_LABEL = "JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE"
W_FROM_SECONDARY = "JA_COMPOSITE_VALUE_FROM_SECONDARY"
W_GARBLE_EXPLAINED = "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED"
W_SECONDARY_READING_CONFLICT = "JA_COMPOSITE_SECONDARY_READING_CONFLICT"      # R-1
W_LISTEN_REQUIRED = "JA_COMPOSITE_LISTEN_REQUIRED"                           # R-1/R-2: 試聴必須(事後試聴リストの必須扱い)
TOKEN = "【値】"
READING_RULE_V2 = "v2:normalize_ja_exact_or_particle_pron(proto_reading_compare_02.pron_hira)+c2_blocked+A7"
READING_RULE_STRICT = "strict:normalize_ja_exact_only+A7"
SCOPE_ALLOWED = ("X", "Y", "Z")      # A/B/C は対象外(27-7)

_NUM_CHARS = "0-9,.〇零一二三四五六七八九十百千万億兆"
_RUN_CHARS = "0-9,〇零一二三四五六七八九十百千万億兆"


@dataclass
class AtomStatus:
    surface: str
    value: int
    unit_surface: str
    primary_run: str | None
    status: str            # EQUAL | EXPLAINED | CONTRADICTION | MISSING
    detail: str = ""
    span: tuple | None = None


@dataclass
class BResult:
    equal: bool
    why: str
    blocked_by: str | None = None
    label: str | None = None
    warnings: tuple = ()
    atoms: list = field(default_factory=list)
    protected: bool = False
    listen_required: bool = False
    listen_reasons: tuple = ()
    audit: dict = field(default_factory=dict)


@dataclass
class PrecheckResult:
    """R-8: フック①の事前判定(S:=原稿)専用の戻り型。`.equal`/`.label`/`.warnings` を持たない=最終判定として流用できない。"""
    may_call_secondary: bool
    why: str
    blocked_by: str | None = None


def _nfkc(t: str) -> str:
    return unicodedata.normalize("NFKC", t or "")


def _unit_surface(atom_surface: str) -> str:
    return re.sub(r"^[0-9,.〇零一二三四五六七八九十百千万億兆]+", "", atom_surface)


def _numeric_notation_ok(a) -> bool:
    """R-4: 値atomが『数字・漢数字表記 + 助数詞』であること(かな数詞・あいまい語・分数は不可)。"""
    if a.kind != "num":
        return False
    us = _unit_surface(a.surface)
    pre = a.surface[: len(a.surface) - len(us)] if us else a.surface
    return bool(us) and bool(pre) and re.fullmatch("[" + _NUM_CHARS + "]+", pre) is not None


def _segments(run: str):
    if "," in run:
        return None
    segs, cur, kind = [], "", None
    for ch in run:
        k = "digit" if ch.isdigit() and ch.isascii() else "kanji"
        if k != kind and cur:
            segs.append((kind, cur)); cur = ""
        kind = k
        cur += ch
    if cur:
        segs.append((kind, cur))
    return segs


def _place_ok(frags: list[int]) -> bool:
    for i, fi in enumerate(frags):
        for fj in frags[i + 1:]:
            if fj <= 0 or fi % (10 ** len(str(fj))) != 0:
                return False
    return True


_FRONT_RE = re.compile(r"[1-9]0+")      # R-3: 前断片は『1桁 + 0の並び』(d x 10^k, k>=1)。観測形=8000


def explain_garble(run: str, target: int) -> str | None:
    """R-3(観測形に限定)。F-A=数字のみrunの2断片のみ(前断片 d*10^k)。3断片は無効。F-B=数字(d*10^k)+漢数字(万億兆なし)。
    いずれも 断片の総和==target ∧ 位取りが重ならない ∧ 先頭0の断片なし。カンマ付きrunは対象外。"""
    segs = _segments(run)
    if not segs:
        return None
    if len(segs) == 1 and segs[0][0] == "digit":
        d = segs[0][1]
        for i in range(1, len(d)):
            a, b = d[:i], d[i:]
            if not _FRONT_RE.fullmatch(a) or b.startswith("0"):
                continue
            vals = [int(a), int(b)]
            if sum(vals) == target and _place_ok(vals):
                return f"digit_split:{a}+{b}"
        return None
    if len(segs) == 2 and segs[0][0] == "digit" and segs[1][0] == "kanji":
        if not _FRONT_RE.fullmatch(segs[0][1]):
            return None
        k = segs[1][1]
        if any(c in k for c in "万億兆"):
            return None
        kv = vg.parse_ja_number(k)
        if kv is None or Fraction(kv).denominator != 1:
            return None
        vals = [int(segs[0][1]), int(kv)]
        if sum(vals) == target and _place_ok(vals):
            return f"digit+kanji:{segs[0][1]}+{k}"
    return None


def analyze_primary_values(canonical_n: str, primary_n: str, allow_explained: bool):
    c_atoms = [a for a in vg.extract_atoms_ja(canonical_n) if a.kind in ("num", "frac")]
    out, cursor = [], 0
    for a in c_atoms:
        us = _unit_surface(a.surface)
        val = int(a.value) if (a.kind == "num" and Fraction(a.value).denominator == 1) else None
        if a.kind != "num" or val is None or not us:
            out.append(AtomStatus(a.surface, -1, us, None, "CONTRADICTION", "unsupported_atom(kind/unit/non-integer)"))
            continue
        pat = re.compile(r"(?<![A-Za-z0-9,.])([" + _RUN_CHARS + r"]+)" + re.escape(us))
        found = None
        for m in pat.finditer(primary_n, cursor):
            found = m
            break
        if found is None:
            out.append(AtomStatus(a.surface, val, us, None, "MISSING", "no_numeric_run_before_unit_in_primary"))
            continue
        run = found.group(1)
        span = (found.start(), found.end())
        cursor = found.end()
        pv = vg.parse_ja_number(run)
        if pv is not None and Fraction(pv).denominator == 1 and int(pv) == val:
            out.append(AtomStatus(a.surface, val, us, run, "EQUAL", "primary_run_value_equals_canonical", span))
            continue
        why = explain_garble(run, val) if allow_explained else None
        if why:
            out.append(AtomStatus(a.surface, val, us, run, "EXPLAINED", why, span))
        else:
            out.append(AtomStatus(a.surface, val, us, run, "CONTRADICTION",
                                  f"primary_run_value={pv}" + ("" if allow_explained else "(explain disabled)"), span))
    return out, c_atoms


def _mask(text: str, spans: list[tuple]) -> str:
    out, pos = [], 0
    for s, e in sorted(spans):
        out.append(text[pos:s]); out.append(TOKEN); pos = e
    out.append(text[pos:])
    return "".join(out)


def _atom_seq(atoms):
    return [(int(a.value), a.unit) for a in atoms if a.kind == "num" and Fraction(a.value).denominator == 1]


def _core(canonical_text, primary_text, secondary_text, expected_readings, allow_explained_garble, reading_rule, secondary_reading_conflict) -> BResult:
    if primary_text is None or not str(primary_text).strip():
        return BResult(False, "primary_none", "primary_unavailable")
    if secondary_text is None or not str(secondary_text).strip():
        return BResult(False, "secondary_none_or_empty", "secondary_unavailable")
    if reading_rule not in ("v2", "strict") or secondary_reading_conflict not in ("warn", "veto"):
        return BResult(False, "bad_option", "bad_option")
    Cn, Pn, Sn = _nfkc(canonical_text), _nfkc(primary_text), _nfkc(secondary_text)
    for tag, t in (("primary", primary_text), ("secondary", secondary_text)):
        if negation_diff(canonical_text, t, "ja") or sec._scg_negation_marker_diff(canonical_text, t):
            return BResult(False, f"negation_diff:{tag}", "negation", protected=True)
    c_all = vg.extract_atoms_ja(Cn)
    c_atoms = [a for a in c_all if a.kind in ("num", "frac")]
    if not c_atoms:
        return BResult(False, "no_value_atoms_in_canonical", "not_applicable")
    if any(a.kind == "amb" for a in c_all):
        return BResult(False, "canonical_has_ambiguous_atom", "R4_atom_notation")
    if not all(_numeric_notation_ok(a) for a in c_atoms):
        return BResult(False, "canonical_atom_notation_unsupported", "R4_atom_notation")
    irr = [a.surface for a in c_atoms if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]
    if irr:
        return BResult(False, f"irregular_reading_value:{','.join(irr)}", "A4a_irregular_reading")
    s_all = vg.extract_atoms_ja(Sn)
    if any(a.kind != "num" for a in s_all) or not all(_numeric_notation_ok(a) for a in s_all):     # R-4
        return BResult(False, "secondary_atom_notation_unsupported", "R4_atom_notation", protected=True)
    # M-3: 値atom列を位置・個数・順序で照合(value_guardの二重化)
    if _atom_seq(c_atoms) != _atom_seq(s_all):
        return BResult(False, "secondary_atom_sequence_mismatch", "secondary_value", protected=True)
    gs = vg.value_guard(canonical_text, secondary_text, "ja")
    if gs.kind != vg.EQUAL:
        return BResult(False, f"secondary_value_guard={gs.kind}", "secondary_value", protected=(gs.kind == vg.DIFF))
    st, _ = analyze_primary_values(Cn, Pn, allow_explained_garble)
    bad = [s for s in st if s.status in ("CONTRADICTION", "MISSING")]
    if bad:
        contra = any(s.status == "CONTRADICTION" for s in bad)
        return BResult(False, "primary_value:" + ";".join(f"{s.surface}:{s.status}:{s.detail}" for s in bad),
                       "primary_secondary_value_contradiction" if contra else "primary_value_missing", atoms=st, protected=contra)
    cls = javal.classify_ja_asr_match(canonical_text, primary_text, expected_readings=expected_readings, allow_reading_resolver=False)
    rd = sec._scg_reading_dict_reason(cls)
    if rd:
        return BResult(False, rd, "A7_reading_dictionary", atoms=st)
    c_m = _mask(Cn, [(a.start, a.end) for a in c_atoms])
    p_m = _mask(Pn, [s.span for s in st])
    s_m = _mask(Sn, [(a.start, a.end) for a in s_all])
    c, p, s = javal.normalize_ja(c_m), javal.normalize_ja(p_m), javal.normalize_ja(s_m)
    warnings = [W_FROM_SECONDARY]
    listen: list[str] = []
    if any(x.status == "EXPLAINED" for x in st):
        warnings.append(W_GARBLE_EXPLAINED); listen.append("garble_explained(TTS不自然な間の可能性)")      # R-2
    if c != p:
        if reading_rule == "strict":
            return BResult(False, "primary_reading_differs(strict)", "primary_reading", atoms=st)
        if P2.pron_hira(c) != P2.pron_hira(p):
            return BResult(False, "primary_reading_differs", "primary_reading", atoms=st)
        blk = P2.c2_blocked(cls, c, p)
        if blk:
            return BResult(False, blk, "C2_heterophone", atoms=st)
        warnings.append(P2.W_PRON); listen.append("pron_equivalent(v2読み規則)")
    if sec._has_negation_ja_text(c_m) != sec._has_negation_ja_text(p_m):
        return BResult(False, "negation_after_mask", "negation", atoms=st, protected=True)
    # R-1: Secondaryの残りの読みが原稿(=Primaryが保証した読み)と食い違う
    conflict = False
    if s != c and P2.pron_hira(s) != P2.pron_hira(c):
        conflict = True
        if secondary_reading_conflict == "veto":
            return BResult(False, "secondary_reading_conflict(veto)", "secondary_reading_conflict", atoms=st)
        warnings.append(W_SECONDARY_READING_CONFLICT); listen.append("secondary_reading_conflict(Primary読みを正とする)")
    if listen:
        warnings.append(W_LISTEN_REQUIRED)
    audit = {"composite_contributed": True, "reading_source": "primary", "value_source": "secondary",
             "reading_rule": READING_RULE_V2 if reading_rule == "v2" else READING_RULE_STRICT,
             "explained_spans": [{"canon": x.surface, "primary_run": x.primary_run, "detail": x.detail} for x in st if x.status == "EXPLAINED"],
             "secondary_reading_conflict": conflict, "allow_explained_garble": allow_explained_garble, "atom_count": len(c_atoms)}
    return BResult(True, "composite_value_secondary_reading_primary", None, COMPOSITE_LABEL, tuple(warnings), st,
                   listen_required=bool(listen), listen_reasons=tuple(listen), audit=audit)


def composite_judge(canonical_text: str, primary_text: str | None, secondary_text: str | None, secondary_meta: dict | None = None,
                    expected_readings: dict | None = None, allow_explained_garble: bool = True, reading_rule: str = "v2",
                    secondary_reading_conflict: str = "warn") -> BResult:
    """純関数。呼出側がPrimary NGかつSecondary取得成功のときだけ呼ぶ。最終ANDゲートは呼出側が常に通す。
    secondary_meta = {'engine': 'azure', 'wav_sha256': ..., 'model_id': ...(任意)} が無ければ fail-closed(M-2: 保存を配線前提)。"""
    meta = secondary_meta or {}
    if meta.get("precheck"):
        return BResult(False, "precheck_meta_not_final", "precheck_not_final")          # R-8
    if not (meta.get("engine") and meta.get("wav_sha256")):
        return BResult(False, "secondary_provenance_missing", "secondary_provenance_missing")
    r = _core(canonical_text, primary_text, secondary_text, expected_readings, allow_explained_garble, reading_rule, secondary_reading_conflict)
    if r.equal:
        r.audit.update(secondary_engine=meta["engine"], secondary_wav_sha256=meta["wav_sha256"], secondary_model_id=meta.get("model_id"),
                       secondary_transcript=secondary_text, primary_transcript=primary_text, canonical_text=canonical_text)
    return r


def precheck_composite(canonical_text: str, primary_text: str | None, **kw) -> PrecheckResult:
    """フック①(P1緩和)の事前判定。S:=原稿として『Secondaryが台本通りの値を返したら composite が成立し得るか』だけを返す。
    戻り型は PrecheckResult(`.equal`/`.label`/`.warnings` を持たない)。この結果を最終判定へ流用してはならない(R-8)。"""
    r = _core(canonical_text, primary_text, canonical_text, kw.get("expected_readings"), kw.get("allow_explained_garble", True),
              kw.get("reading_rule", "v2"), kw.get("secondary_reading_conflict", "warn"))
    return PrecheckResult(bool(r.equal), r.why, r.blocked_by)


# ---------------- M-2: 寄与印と再利用判定 (er109/RET/UKUS前例の形。Production配線は別委任) ----------------
def composite_contributed(aj) -> bool:
    """fail-closed: asr_judgement内にcomposite印(ラベル・警告・auditキー)が1つでもあれば寄与あり。"""
    if not isinstance(aj, dict):
        return False
    s = json.dumps(aj, ensure_ascii=False, default=str)
    return ("JA_COMPOSITE" in s) or (COMPOSITE_LABEL in s) or bool(aj.get("composite_contributed"))


@dataclass
class ReuseDecision:
    blocked: bool
    reason: str
    rejudged: bool = False


def composite_reuse_decision(entry: dict, flag_on: bool, scope: str | None, **judge_kw) -> ReuseDecision:
    """Master Audio Store(A/B/C共有)の再利用時。composite寄与のあるentryだけが対象(印のないentryには作用しない)。
    1) scope外 or flag OFF → 先にblock(composite受理音声がA/B/CやflagOFFへ漏れない) 2) 保存S転写/engine/wav shaが無ければfail-closed
    3) 保存S転写で composite_judge を再実行し、NGならblock。"""
    ajs = [a for a in (entry.get("asr_judgement"), entry.get("asr_judgement_inherited")) if composite_contributed(a)]
    if not ajs:
        return ReuseDecision(False, "NOT_COMPOSITE")
    if (not flag_on) or scope not in SCOPE_ALLOWED:
        return ReuseDecision(True, "COMPOSITE_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF")
    for aj in ajs:
        au = aj.get("composite") if isinstance(aj.get("composite"), dict) else {}
        need = ("secondary_transcript", "secondary_engine", "secondary_wav_sha256", "primary_transcript", "canonical_text")
        if any(not au.get(k) for k in need):
            return ReuseDecision(True, "COMPOSITE_PROVENANCE_MISSING")
        r = composite_judge(au["canonical_text"], au["primary_transcript"], au["secondary_transcript"],
                            {"engine": au["secondary_engine"], "wav_sha256": au["secondary_wav_sha256"], "model_id": au.get("secondary_model_id")}, **judge_kw)
        if not r.equal:
            return ReuseDecision(True, f"COMPOSITE_REJUDGE_NG:{r.blocked_by}", True)
    return ReuseDecision(False, "COMPOSITE_REJUDGE_OK", True)
