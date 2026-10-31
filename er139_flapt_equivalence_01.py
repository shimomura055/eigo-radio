# ============================================================
# er139_flapt_equivalence_01.py
# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02 (2026-10-31)
# Flap-T(米音の弾音化)発音同等性救済の Production 層。Status: APPROVED_FOR_PRODUCTION(ユーザー原文 2026-10-31)。既定ON。
# 方式 = Trial M1(`ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_equivalence_proto_01.py`)の再実装 + Opus M1〜M6 確定仕様。
#   Trial protoは数字tokenを落とす(`The latter 13 option`<->`The ladder 30 option`をRESCUEにする)ため移植ではなく再実装。
# 構造: 本moduleは純関数 + Voice適用ゲート `decide()` のみ。呼べるのは `er109_xz_scope_01.decision()` だけ(AST test)。
#   新規call siteなし。er109(表記違い同音)が `equivalent=False` のときだけ評価される第3層(既存の勝敗・ラベルは不変)。
# 不変条件 I-1〜I-10 (Trial DESIGN_01 2節):
#   I-1 文字列t<->d置換禁止(CMU音素列+flap環境のみ) / I-2 母音完全一致 / I-3 差位置は全てflap環境(強勢母音_無強勢母音)
#   I-4 canonical強勢読み単一 / I-5 AY・AW核は自動救済しない / I-6 1:1語置換のみ・CMU未登録は同値でない / I-7 ASR収束を根拠にしない
#   I-8 Voice適用境界(出自台帳+静的Voice表で confirmed な (voice,model) のみ) / I-9 既存閾値・Gate・retry上限・最終ANDゲート不変
#   I-10 救済は必ず警告ラベル `FLAP_T_EQUIVALENT` 付き+根拠ログ(根拠は FlapEq.audit())
# flag: `FLAP_T_EQUIVALENCE_ENABLED`(module定数・rollbackスイッチ。env/引数/設定dictから変更不可)。単一読取 `is_enabled()`。
#   親flag = er109 `is_active_for_run()`(ORTHOGRAPHIC_EQUIVALENCE_ENABLED ∧ scope∈{X,Y,Z})。親をrollbackするとFlap-Tも停止する(仕様)。
# ============================================================
from __future__ import annotations

import difflib
import functools
import hashlib
import json
import os
import re
import threading
import unicodedata
import warnings as _warnings
from dataclasses import dataclass, field
from typing import Optional

try:
    import pronouncing
except ImportError:      # 判定不能=非救済(fail-closed)
    pronouncing = None

FLAP_T_EQUIVALENCE_ENABLED = True          # 既定ON(ユーザー正式採用)。rollback時のみFalseへ(コード変更+Fable報告)
RULES_VERSION = "er139_flapt_equivalence_v1"
WARNING_LABEL = "FLAP_T_EQUIVALENT"
RULE_NAME = "flap_t_equivalence"
# 固定したCMU辞書(cmudict 1.1.3 の cmudict.dict)。不一致=救済せず run警告(記録のみは不可)
EXPECTED_CMU_DICT_SHA256 = "81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22"
VOICE_TABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er139_flapt_voice_table_01.json")
FAST106_PCT = -5.66          # Z Adv dialogue 高速化(er063 Z_ADV_DIALOGUE_SLOWDOWN_PCT = -5.6603...)
CONFIRMED_PLAIN_PCTS = (6.0,)  # Std 6%減速(減速なし=変換履歴なしも確認済み)
PCT_TOL = 0.02

VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
RAISING_SENSITIVE = {"AY", "AW"}
# 多重防御: 数詞語・否定語を含む対は非救済(数値/否定の意味差をFlapで説明しない)
_NUMBER_WORDS = frozenset("""zero oh one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen
eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion first second third fourth fifth
sixth seventh eighth ninth tenth half quarter dozen""".split())
_NEGATION_FALLBACK = frozenset({"no", "not", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "without"})

RUN_WARNINGS: list = []       # run単位の警告(CMU sha不一致等)。sidecarが参照
_RW_LOCK = threading.Lock()


def is_enabled() -> bool:
    """単一読取関数。module定数のみ(env/引数/設定dictから変更不可)。"""
    return FLAP_T_EQUIVALENCE_ENABLED is True


def _run_warning(kind: str, detail: str) -> None:
    with _RW_LOCK:
        item = {"kind": kind, "detail": detail}
        if item not in RUN_WARNINGS:
            RUN_WARNINGS.append(item)
            _warnings.warn(f"[FLAP_T] {kind}: {detail}", RuntimeWarning, stacklevel=3)


# ---------------------------------------------------------------- CMU辞書の同一性(M6)
@functools.lru_cache(maxsize=1)
def cmu_info() -> dict:
    out = {"cmudict_dict_sha256": None, "cmudict_version": None, "pronouncing_version": None}
    try:
        import cmudict as _cm
        import importlib.metadata as _md
        p = os.path.join(os.path.dirname(_cm.__file__), "data", "cmudict.dict")
        with open(p, "rb") as f:
            out["cmudict_dict_sha256"] = hashlib.sha256(f.read()).hexdigest()
        out["cmudict_version"] = _md.version("cmudict")
        out["pronouncing_version"] = _md.version("pronouncing")
    except Exception as exc:  # noqa: BLE001 fail-closed
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def cmu_matches() -> bool:
    ok = cmu_info().get("cmudict_dict_sha256") == EXPECTED_CMU_DICT_SHA256
    if not ok:
        _run_warning("CMU_DICT_SHA_MISMATCH",
                     f"expected={EXPECTED_CMU_DICT_SHA256[:12]} actual={str(cmu_info().get('cmudict_dict_sha256'))[:12]} "
                     f"err={cmu_info().get('error')}: Flap-T救済を停止(従来NG)")
    return ok


def engine_version() -> str:
    return f"{RULES_VERSION}+cmu{(cmu_info().get('cmudict_dict_sha256') or 'none')[:8]}"


# ---------------------------------------------------------------- Voice表(M4)
@functools.lru_cache(maxsize=1)
def voice_table() -> dict:
    with open(VOICE_TABLE_PATH, "rb") as f:
        raw = f.read()
    d = json.loads(raw.decode("utf-8"))
    rows = {}
    for r in d.get("rows", []):
        rows[(r["Voice"], r["model_id"])] = r        # 表キー完全一致のみ(あいまい一致・別名・prefix一致なし)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "rows": rows, "n_rows": len(rows)}


def table_row(voice, model_id) -> Optional[dict]:
    try:
        return voice_table()["rows"].get((voice, model_id))
    except Exception:  # noqa: BLE001
        return None


def table_status(voice, model_id) -> str:
    r = table_row(voice, model_id)
    if r is None:
        return "not_in_table"
    return "confirmed" if r.get("confirmed") is True else "unconfirmed"


def speed_ok(row: dict, transforms, transforms_known: bool) -> tuple:
    """速度後処理の条件(pct条件つき)。減速なし/6.0=確認済み、-5.66(Z Adv高速化)はfast106_confirmed、未知pct・変換履歴不明は
    最も厳しい条件(fast106_confirmed)を要求。"""
    if not transforms_known:
        return (row.get("fast106_confirmed") is True), "transforms_unknown_requires_fast106_confirmed"
    for t in transforms or []:
        pct = t.get("slowdown_pct")
        if pct is None or any(abs(float(pct) - c) <= PCT_TOL for c in CONFIRMED_PLAIN_PCTS):
            continue
        if abs(float(pct) - FAST106_PCT) <= PCT_TOL:
            if row.get("fast106_confirmed") is True:
                continue
            return False, "fast106_unconfirmed"
        return False, "speed_pct_unknown"
    return True, "ok"


# ---------------------------------------------------------------- tokenizer(M1: er109 `_TOKEN_RE` と同一。数字・通貨・時刻・記号もtoken)
def tokenize(text: str) -> list:
    import er109_xz_scope_01 as xz          # er109純関数はscope module経由でのみ参照(Productionのimport隔離を維持)
    out = []
    for m in xz.token_regex().finditer(unicodedata.normalize("NFKC", text or "")):
        g, s = m.lastgroup, m.group(0)
        if g == "word":
            s = s.lower().replace("’", "'").rstrip(".").rstrip("'")
        else:
            s = re.sub(r"\s+", "", s.lower())
        if s:
            out.append((g, s))
    return out


# ---------------------------------------------------------------- CMU音素判定(純関数)
def _readings(word: str):
    if pronouncing is None:
        return None
    vs = pronouncing.phones_for_word(word.lower())
    return [tuple(v.split()) for v in vs] if vs else None


def _s2(ph: tuple) -> tuple:
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
    decision: str          # RESCUE / NO_RESCUE / REQUIRES_EXTRA_EVIDENCE
    reason: str
    detail: dict = field(default_factory=dict)


@dataclass
class FlapResult:
    decision: str          # RESCUE / NO_RESCUE / REQUIRES_EXTRA_EVIDENCE / NOT_APPLICABLE
    reason: str
    pairs: list = field(default_factory=list)


def flap_env(ph: tuple, i: int) -> tuple:
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


def _negation_words(w: str) -> bool:
    try:
        import er078_asr_unified_judge_01 as uj
        return bool(uj.negation_counter(w))
    except Exception:  # noqa: BLE001
        return w in _NEGATION_FALLBACK


def judge_pair(canonical: str, asr: str) -> PairResult:
    c, a = canonical.lower(), asr.lower()
    if c in _NUMBER_WORDS or a in _NUMBER_WORDS:
        return PairResult(c, a, "NO_RESCUE", "number_word_pair")
    if _negation_words(c) or _negation_words(a):
        return PairResult(c, a, "NO_RESCUE", "negation_word_pair")
    rc, ra = _readings(c), _readings(a)
    if rc is None or ra is None:
        return PairResult(c, a, "NO_RESCUE", "cmu_unresolved")
    sc = {_s2(r) for r in rc}
    if len(sc) != 1:
        return PairResult(c, a, "NO_RESCUE", "canonical_multiple_readings")
    pc = next(iter(sc))
    pa = _s2(ra[0])
    if len(pc) != len(pa):
        return PairResult(c, a, "NO_RESCUE", "phoneme_length_differs")
    diff = [i for i, (x, y) in enumerate(zip(pc, pa)) if x != y]
    if not diff:
        return PairResult(c, a, "NO_RESCUE", "phonemes_identical_not_flap_case")
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
    det = {"canonical_phones": " ".join(pc), "asr_phones": " ".join(pa), "positions": diff}
    if sens:
        return PairResult(c, a, "REQUIRES_EXTRA_EVIDENCE", f"raising_sensitive_nucleus:{sens}", det)
    return PairResult(c, a, "RESCUE", "flap_t_equivalent", det)


def evaluate(canonical_text: str, asr_text: str) -> FlapResult:
    """文単位。差分は『word tokenの1:1置換』のみ。数字・記号・通貨・時刻tokenの差が1つでもあれば NOT_APPLICABLE(非救済)。"""
    ct, at = tokenize(canonical_text), tokenize(asr_text)
    ops = [o for o in difflib.SequenceMatcher(a=[s for _g, s in ct], b=[s for _g, s in at], autojunk=False).get_opcodes() if o[0] != "equal"]
    if not ops:
        return FlapResult("NOT_APPLICABLE", "no_token_difference")
    pairs = []
    for tag, i1, i2, j1, j2 in ops:
        if tag != "replace" or (i2 - i1) != (j2 - j1):
            return FlapResult("NOT_APPLICABLE", f"non_1to1_difference:{tag}")
        for k in range(i2 - i1):
            (gc, sc_), (ga, sa) = ct[i1 + k], at[j1 + k]
            if gc != "word" or ga != "word":
                return FlapResult("NOT_APPLICABLE", f"non_word_token_difference:{gc}/{ga}")      # M1: 数字・記号tokenの差
            pairs.append(judge_pair(sc_, sa))
    ds = {p.decision for p in pairs}
    if ds == {"RESCUE"}:
        return FlapResult("RESCUE", "all_differences_flap_t_equivalent", pairs)
    if "NO_RESCUE" in ds:
        return FlapResult("NO_RESCUE", next(p.reason for p in pairs if p.decision == "NO_RESCUE"), pairs)
    return FlapResult("REQUIRES_EXTRA_EVIDENCE", next(p.reason for p in pairs if p.decision == "REQUIRES_EXTRA_EVIDENCE"), pairs)


@functools.lru_cache(maxsize=8192)
def evaluate_cached(canonical: str, text: str) -> FlapResult:
    """純規則判定のみのメモ。keyは(canonical,text)だけ=voice非依存(M2)。Voice判定はこのcacheの外。"""
    return evaluate(canonical, text)


# ---------------------------------------------------------------- 判定object(er109 EquivalenceResult 互換の最小面)
@dataclass
class FlapEq:
    equivalent: bool
    reason: str
    pairs: list
    provenance: dict
    version: str = ""
    warnings: list = field(default_factory=lambda: [WARNING_LABEL])
    rules: list = field(default_factory=lambda: [RULE_NAME])
    spans: list = field(default_factory=list)       # 互換のため空(er109 explain_protected は version 不一致で先にFalse=値DIFF/否定差を解除しない)

    @property
    def verdict(self) -> str:
        return "PASS_WITH_WARNING"

    def audit(self) -> dict:
        info = cmu_info()
        return {"version": self.version, "flag_enabled": is_enabled(), "equivalent": self.equivalent, "verdict": self.verdict,
                "reason": self.reason, "rules": list(self.rules), "warnings": list(self.warnings),
                "spans": [{"canon": [p.canonical], "asr": [p.asr], "equivalent": True, "rule": RULE_NAME, "why": p.reason,
                           "canonical_phones": p.detail.get("canonical_phones"), "asr_phones": p.detail.get("asr_phones"),
                           "warnings": [WARNING_LABEL]} for p in self.pairs],
                "flapt": {"rules_version": RULES_VERSION, "cmudict_dict_sha256": info.get("cmudict_dict_sha256"),
                          "cmudict_version": info.get("cmudict_version"), "pronouncing_version": info.get("pronouncing_version"),
                          "voice_table_sha256": voice_table()["sha256"], **self.provenance}}


# ---------------------------------------------------------------- Voice適用ゲート
def _decline(notes: list, reason: str, **kw) -> None:
    notes.append({"reason": reason, **kw})


def _decide_uncached(canonical: str, text: str, ctx: Optional[dict]) -> tuple:
    """戻り値: (FlapEq|None, notes[list], candidate_record|None)。例外は呼出側が捕捉。"""
    notes: list = []
    res = evaluate_cached(canonical, text)
    rescue_pairs = [p for p in res.pairs if p.decision == "RESCUE"]
    if res.decision != "RESCUE":
        if rescue_pairs:     # flap対はあるが他の差分で全体が非救済(監査に残す)
            _decline(notes, "non_flap_token_diff", canonical=canonical[:120], text=str(text)[:120], detail=res.reason)
            return None, notes, {"outcome": "declined", "reason": "non_flap_token_diff", "pairs": [[p.canonical, p.asr] for p in rescue_pairs]}
        return None, notes, None
    pair_ids = [[p.canonical, p.asr] for p in res.pairs]
    if not cmu_matches():
        _decline(notes, "cmu_sha_mismatch", pairs=pair_ids)
        return None, notes, {"outcome": "declined", "reason": "cmu_sha_mismatch", "pairs": pair_ids}
    import er139_flapt_provenance_01 as prov
    sha = ctx.get("sha") if ctx else None
    if not sha:
        _decline(notes, "provenance_missing", why="no_wav_context", pairs=pair_ids)
        return None, notes, {"outcome": "declined", "reason": "provenance_missing", "why": "no_wav_context", "pairs": pair_ids}
    ent = prov.resolve(sha)
    if ent is None:
        _decline(notes, "provenance_missing", why="wav_sha_not_in_ledger", wav_sha256=sha, pairs=pair_ids)
        return None, notes, {"outcome": "declined", "reason": "provenance_missing", "why": "wav_sha_not_in_ledger", "pairs": pair_ids}
    row = table_row(ent.get("voice"), ent.get("model_id"))
    base_prov = {"voice": ent.get("voice"), "model_id": ent.get("model_id"), "wav_sha256": sha, "provenance_source": ent.get("source"),
                 "transforms": list(ent.get("transforms") or []), "transforms_known": bool(ent.get("transforms_known", True))}
    if row is None or row.get("confirmed") is not True:
        _decline(notes, "voice_unconfirmed", voice=ent.get("voice"), model_id=ent.get("model_id"),
                 table_status=table_status(ent.get("voice"), ent.get("model_id")), pairs=pair_ids)
        return None, notes, {"outcome": "declined", "reason": "voice_unconfirmed", "voice": ent.get("voice"),
                             "model_id": ent.get("model_id"), "pairs": pair_ids}
    ok, why = speed_ok(row, ent.get("transforms"), bool(ent.get("transforms_known", True)))
    if not ok:
        _decline(notes, "voice_unconfirmed", why=why, voice=ent.get("voice"), model_id=ent.get("model_id"),
                 transforms=base_prov["transforms"], pairs=pair_ids)
        return None, notes, {"outcome": "declined", "reason": why, "voice": ent.get("voice"), "model_id": ent.get("model_id"), "pairs": pair_ids}
    base_prov.update(path=row.get("path"), table_evidence_ref=row.get("evidence_ref"), table_evidence_sha256=row.get("sha"))
    eq = FlapEq(True, res.reason, list(res.pairs), base_prov, version=engine_version())
    return eq, notes, {"outcome": "rescued", "pairs": pair_ids, "voice": ent.get("voice"), "model_id": ent.get("model_id")}


def decide(canonical, text, sink: Optional[dict] = None) -> Optional[FlapEq]:
    """`er109_xz_scope_01.decision()` からのみ呼ぶ。er109が『同値でない』と判定したときの第3層。
    条件: 親(er109 is_active_for_run: flag∧X/Y/Z scope)∧子flag ∧ 1:1のword置換でflap対 ∧ 数字/記号token差0 ∧ CMU辞書sha一致 ∧
    出自台帳でwav shaのVoice/modelが表で confirmed(速度条件つき)。例外は『同値でない』+sink記録(runを止めない)。
    (sha,canonical,text)ごとのmemoは judging_wav 範囲内(I-10: 二重呼出でも同一結果・警告が消えない)。"""
    if not is_enabled():
        return None
    import er109_xz_scope_01 as xz
    if not xz.is_active_for_run() or not canonical or text is None or not str(text).strip():
        return None
    import er139_flapt_provenance_01 as prov
    ctx = prov.current_ctx()
    key = (canonical, text)
    try:
        if ctx is not None and key in ctx["memo"]:
            eq, notes, _cand = ctx["memo"][key]
        else:
            eq, notes, cand = _decide_uncached(canonical, text, ctx)
            if ctx is not None:
                ctx["memo"][key] = (eq, notes, cand)
                if cand is not None:
                    ctx["cands"].append({"canonical": canonical[:160], "text": str(text)[:160], **cand})
    except Exception as exc:  # noqa: BLE001  fail-closed
        if sink is not None:
            sink.setdefault("orthographic_equivalence_errors", []).append(f"flapt:{type(exc).__name__}: {exc}")
        return None
    if sink is not None and notes:
        lst = sink.setdefault("flapt_declined", [])
        for n in notes:
            if n not in lst:
                lst.append(n)
    return eq


# ---------------------------------------------------------------- Master Audio Store再利用ガード用(er078_reuse_value_guard_01 から)
REUSE_BLOCK_REASON = "FLAP_T_EQUIVALENT_AUDIO_OUT_OF_SCOPE_OR_VOICE_UNCONFIRMED"


def reuse_still_valid(aj) -> tuple:
    """Flap-T寄与recordが、現在の(flag・Voice表sha・CMU辞書sha・Voice/model確認状態)でも成立するか。成立しない/読めない場合は (False, reason)=fail-closed。"""
    try:
        if not is_enabled():
            return False, "flag_off"
        oe = (aj or {}).get("orthographic_equivalence") or {}
        audits = [st.get("er109") for st in (oe.get("sites") or []) if isinstance(st, dict) and isinstance(st.get("er109"), dict)
                  and RULE_NAME in (st["er109"].get("rules") or [])]
        if not audits:
            return False, "flapt_audit_missing"
        cur_table = voice_table()["sha256"]
        for a in audits:
            fl = a.get("flapt") or {}
            if fl.get("voice_table_sha256") != cur_table:
                return False, "voice_table_sha_changed"
            if fl.get("cmudict_dict_sha256") != EXPECTED_CMU_DICT_SHA256 or fl.get("rules_version") != RULES_VERSION:
                return False, "cmu_or_rules_changed"
            row = table_row(fl.get("voice"), fl.get("model_id"))
            if row is None or row.get("confirmed") is not True:
                return False, "voice_unconfirmed_now"
            ok, why = speed_ok(row, fl.get("transforms"), bool(fl.get("transforms_known", True)))
            if not ok:
                return False, why
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
