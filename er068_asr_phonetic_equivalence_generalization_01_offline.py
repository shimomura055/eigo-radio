# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01: 一般化判定方式の Trial 隔離プロトタイプ + 既存データ read-only 検証。

位置づけ(重要):
  * 本ファイルは DEV/Trial 専用。Production 経路(er006/er011/er003/er020/er021/er025/er026/er062/er063)へは
    一切接続しない。Production モジュールは import して「呼ぶだけ」(変更しない)。
  * 有料 API(TTS/ASR/LLM)は一切呼ばない。入力は既存データ(er065 実データ・合成反例、Melos run_e2e_02 の
    attempt_history / reeval、既存 wav のローカル DSP)のみ。費用 JPY0。
  * 共有 telemetry(er021)への追記は append_telemetry_log を no-op 化して防ぐ。
  * 採用判断は書かない。到達上限 Status = DESIGN_DRAFT(設計) / VALIDATED|REJECTED|USER_DECISION_REQUIRED(検証)。

設計(DESIGN_DRAFT_01.md の方式 M1 + M2):
  M1 = ASR 側の「CMU 確認済み同音綴り」正規化フロントエンド。ASR トークンを、同じ音素列(CMU 全変種で確認)を持つ
       別綴りのうち「承認済み Pattern A/B/C や厳密一致が canonical 側で期待する綴り」へ置換し、置換後の文を
       Production の既存判定(val.classify_asr_match = protected_check + entity gate + Pattern A/B/C)へそのまま流す。
       新しい受理基準は作らない(同じ音素列なら同じ判定、という一貫性公理のみ追加)。
  M2 = M1 で受理できないが音素水準で連結発音と説明できる差分を、自動受理せず「説明付き HR 候補」に分類する
       (Trial 音韻判定 P.explain_diff + P.risk_flags を再利用)。
  V2 = M1 に「clip 末尾完全性の独立確認(ローカル DSP)」を AND した変種(末尾切詰の誤 PASS 対策の検討用)。
"""
from __future__ import annotations

import argparse
import collections
import difflib
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pronouncing

import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er021_en_asr_semantic_equivalence_production_01 as _se
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er068_asr_phonetic_equivalence_generalization_01_stateguard as guard

# 共有 telemetry への追記を無効化(Production state 保護)。import 直後に必ず実行する。
_se.append_telemetry_log = lambda *a, **k: None

SEG = "full_story_part1"  # Production と同じ role gating(FULL_STORY)で判定する
OUT_DEFAULT = "er068_output/asr_phonetic_equivalence_generalization_01"
ER065 = "er065_output/short_clip_asr_context_trial_01"
P2 = ER065 + "/phase2"
PASS_CLASSES_PATTERN = {"CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_PASS_WITH_WARNING"}
TAIL_THRESHOLD_DB = -30.0  # 末尾 50ms の最大フレーム RMS が p95 フレーム RMS 比で -30dB 以下(Production 実 wav 97 本の全数が満たす値)
TAIL_MS = 50

# ---------------------------------------------------------------------------
# Production 現行判定(V0)と既存 Pattern A/B/C 単独(VA)
# ---------------------------------------------------------------------------
_secondary_asr = None


def _alt_pass_fn():
    """Production の _step_alternate_pass(CMU Case A 固有名詞/同音語)。import 失敗時は None。"""
    global _secondary_asr
    if _secondary_asr is None:
        try:
            import er006_secondary_asr_01 as s
            _secondary_asr = s
        except Exception:  # pragma: no cover
            _secondary_asr = False
    return getattr(_secondary_asr, "_step_alternate_pass", None) if _secondary_asr else None


def prod_judge(canonical: str, asr: str) -> dict:
    """V0: Production 現行(Primary 1 回分 + cascade 内 _step_alternate_pass[CMU 同音 Case A])。
    Tier3(Azure corroboration)は ASR 呼出が要るため含めない(read-only のため)。"""
    c = val.classify_asr_match(canonical, asr, segment_id=SEG)
    alt = None
    fn = _alt_pass_fn()
    if (not c.should_pass) and fn is not None:
        try:
            alt = fn(c)
        except Exception:
            alt = None
    return {"cls": c, "classification": c.classification, "pass": bool(c.should_pass) or bool(alt),
            "pass_basis": ("should_pass" if c.should_pass else (alt or None))}


def pattern_abc_only(canonical: str, asr: str) -> bool:
    """VA: 既存 Pattern A/B/C 単独(csv3.classify_connected_speech)が ACCEPT/RESEGMENTATION か。"""
    j = csv3.classify_connected_speech(canonical, asr)["new_judgment"]
    return j in ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")


# ---------------------------------------------------------------------------
# M1: CMU 確認済み同音綴り正規化フロントエンド
# ---------------------------------------------------------------------------
_REV = None
_REV_PRIMARY = None


def _build_rev():
    global _REV, _REV_PRIMARY
    if _REV is None:
        pronouncing.init_cmu()
        rev = collections.defaultdict(set)
        revp = collections.defaultdict(set)
        seen_first = {}
        for w, ph in pronouncing.pronunciations:
            if not re.fullmatch(r"[a-z]{2,}", w):
                continue
            key = tuple(P._strip(x) for x in ph.split())
            rev[key].add(w)
            if w not in seen_first:  # CMU の先頭エントリ = 代表発音
                seen_first[w] = key
                revp[key].add(w)
        _REV, _REV_PRIMARY = rev, revp


def _rev(primary: bool = False) -> dict:
    _build_rev()
    return _REV_PRIMARY if primary else _REV


def _cmu_variants(word: str) -> list:
    return [tuple(P._strip(x) for x in e.split()) for e in pronouncing.phones_for_word(word.lower())]


def homophone_class(token: str, primary_only: bool = False) -> tuple:
    """token と同じ音素列を持つ別綴りの集合と、その根拠(確認済み発音のみ。推定音素は使わない)。
    primary_only=False(一般語): Production の homophone_arpabet_equivalent と同じ『いずれかの変種が一致』基準。
    primary_only=True(固有名詞らしき語): Production の entity_word_arpabet_primary_match と同じ
      『CMU 代表(先頭)発音同士の一致』のみ(CMU 登録が偶然・不正確な場合がある Tse の実例に基づく保守基準)。
    根拠: 'cmu'(token 自体が CMU 収録) / 'cmu_stem+regular_s'(token が CMU 未収録で、CMU 収録 stem + 規則的 -s)/ 'none'。
    OOV の stem には音素を推定しない(G2P 未導入)。"""
    t = token.lower().strip("'")
    vs = _cmu_variants(t)
    if primary_only:
        vs = vs[:1]
    rev = _rev(primary_only)
    if vs:
        words = set()
        for v in vs:
            words |= rev.get(v, set())
        words.discard(t)
        return sorted(words), "cmu"
    if t.endswith("s") and len(t) > 3:
        stem = t[:-1]
        svs = _cmu_variants(stem)
        if primary_only:
            svs = svs[:1]
        if svs:
            words = set()
            for v in svs:
                words |= rev.get(v, set())
            words.add(stem)
            out = {w + "s" for w in words}
            out.discard(t)
            return sorted(out), "cmu_stem+regular_s"
    return [], "none"


def expected_spellings(c: str) -> set:
    """canonical 語 c に対し、承認済み Pattern A/B/C や厳密一致が『受理する側』として期待する ASR 綴りの集合。
    (Pattern A: c から -s/-es/-ies を除いた形、Pattern B: -ed を除いた形、Pattern C: c に -s/-es を足した形、厳密一致: c)"""
    c = c.lower().strip("'")
    e = {c}
    if c.endswith("ies") and len(c) > 4:
        e.add(c[:-3] + "y")
    if c.endswith("es") and len(c) > 3:
        e.add(c[:-2])
    if c.endswith("s") and len(c) > 2:
        e.add(c[:-1])
    if c.endswith("ed") and len(c) > 3:
        e.add(c[:-2])
    e.add(c + "s")
    e.add(c + "es")
    if c.endswith("y") and len(c) > 2:
        e.add(c[:-1] + "ies")
    return e


_WORD = re.compile(r"[A-Za-z0-9']+")


def _norm_text(t: str) -> str:
    return (t or "").replace("’", "'")


def m1_candidates(canonical: str, asr: str, cls) -> list:
    """Production が『フラグした差分』(cls.protected.content_word_diffs)に含まれる ASR トークンだけを対象に、
    (token_index, 元綴り, 置換綴り, 根拠, 対応 canonical 語) を列挙する。無関係な語への副作用を避けるため、
    フラグされていない差分語(機能語・句読点由来など)には置換を適用しない。"""
    flagged = {}  # asr token -> entity_like
    for d in cls.protected.content_word_diffs:
        for t in P.tokens(d.get("asr", "")):
            flagged[t] = flagged.get(t, False) or bool(d.get("entity_like"))
    if not flagged:
        return []
    cw = P.tokens(canonical)
    aw = P.tokens(asr)
    sm = difflib.SequenceMatcher(a=cw, b=aw, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or j1 == j2 or i1 == i2:
            continue
        exp = set()
        for c in cw[i1:i2]:
            exp |= expected_spellings(c)
        for j in range(j1, j2):
            if aw[j] not in flagged:
                continue
            cls_words, prov = homophone_class(aw[j], primary_only=flagged[aw[j]])
            for cand in cls_words:
                if cand in exp:
                    cc = next((c for c in cw[i1:i2] if cand in expected_spellings(c)), cw[i1])
                    out.append({"asr_index": j, "from": aw[j], "to": cand, "provenance": prov, "canonical_word": cc,
                                "entity_like": flagged[aw[j]]})
    return out


def _replace_tokens(asr: str, repl: dict) -> str:
    """asr 文中の j 番目(P.tokens と同じ分割)のトークンを repl[j] へ置換した文を返す(大文字小文字は元を保つ)。"""
    text = _norm_text(asr)
    pieces, last, j = [], 0, 0
    for m in _WORD.finditer(text):
        tok = m.group(0)
        if tok.lower() == "'":
            continue
        pieces.append(text[last:m.start()])
        new = repl.get(j)
        if new is None:
            pieces.append(tok)
        else:
            pieces.append(new.capitalize() if tok[:1].isupper() else new)
        last = m.end()
        j += 1
    pieces.append(text[last:])
    return "".join(pieces)


def m1_try(canonical: str, asr: str, cls, max_combo: int = 64) -> dict | None:
    """M1 本体。置換候補(複数の差分トークンは直積、上限 max_combo)を Production 既存判定へ流し、
    既存判定が PASS にする組合せが 1 つでもあれば返す。置換後も Production が通さなければ None(新基準は作らない)。"""
    cands = m1_candidates(canonical, asr, cls)
    if not cands:
        return None
    by_idx = collections.defaultdict(list)
    for c in cands:
        by_idx[c["asr_index"]].append(c)
    idxs = sorted(by_idx)
    import itertools
    combos = list(itertools.islice(itertools.product(*[by_idx[i] for i in idxs]), max_combo))
    for combo in combos:
        repl = {c["asr_index"]: c["to"] for c in combo}
        asr2 = _replace_tokens(asr, repl)
        pj = prod_judge(canonical, asr2)
        # 保守基準の維持: 変種文の PASS 根拠が『固有名詞らしき差分に対する HOMOPHONE_EQUIVALENT(CMU いずれかの変種一致)』
        # の場合は M1 の受理にしない(Production は固有名詞に代表発音一致のみを要求する設計[Tse の実例]。
        # M1 経由で緩い経路を通さない)。説明付き HR 候補(M2)へ落ちる。
        if pj["pass"] and pj["pass_basis"] == "HOMOPHONE_EQUIVALENT" and any(
                d.get("entity_like") for d in pj["cls"].protected.content_word_diffs):
            continue
        if pj["pass"]:
            return {"normalized_asr": asr2, "subs": [{k: c[k] for k in ("from", "to", "provenance", "canonical_word", "entity_like")} for c in combo],
                    "variant_classification": pj["classification"], "variant_pass_basis": pj["pass_basis"],
                    "cs_rule": (pj["cls"].connected_speech_info or {}).get("rule") if getattr(pj["cls"], "connected_speech_info", None) else None}
    return None


# ---------------------------------------------------------------------------
# 末尾完全性の独立確認(ローカル DSP、API なし)
# ---------------------------------------------------------------------------
_TAIL_CACHE: dict = {}


def tail_integrity(wav_path: str) -> dict | None:
    """clip 末尾 TAIL_MS の最大フレーム RMS が、clip の p95 フレーム RMS 比 TAIL_THRESHOLD_DB 以下なら tail_ok=True
    (=発話が自然に終わっている)。wav 不在/読込失敗は None(=確認不能)。"""
    if not wav_path:
        return None
    if wav_path in _TAIL_CACHE:
        return _TAIL_CACHE[wav_path]
    res = None
    try:
        import numpy as np
        import soundfile as sf
        if os.path.exists(wav_path):
            x, sr = sf.read(wav_path)
            if getattr(x, "ndim", 1) > 1:
                x = x.mean(axis=1)
            fr = int(sr * 0.01)
            n = len(x) // fr
            if n >= 10:
                r = np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(axis=1) + 1e-12)
                db = 20 * np.log10(r)
                ref = float(np.percentile(db, 95))
                k = max(1, TAIL_MS // 10)
                rel = float(db[-k:].max() - ref)
                res = {"rel_tail_db": round(rel, 2), "tail_ok": rel <= TAIL_THRESHOLD_DB, "duration_s": round(len(x) / sr, 3)}
    except Exception:
        res = None
    _TAIL_CACHE[wav_path] = res
    return res


# ---------------------------------------------------------------------------
# 設計判定(7 段構造の実装。Trial 隔離)
# ---------------------------------------------------------------------------
def _subtype_from_expl(expl: dict) -> str:
    regs = expl.get("regions", [])
    tags = []
    for r in regs:
        v = r.get("verdict")
        if v == "PHON_EXPLAINED_FUSION":
            tags.append("fusion:" + str(r.get("boundary")))
        elif v == "PHON_EXPLAINED_VOICING":
            tags.append("voicing_weak:" + str(r.get("boundary")))
        elif v == "PHON_HOMOPHONE_ONLY":
            tags.append("homophone_spelling_only")
        if any("split:" in s for s in r.get("asr_srcs", []) or []):
            tags.append("resegmentation")
    return "+".join(sorted(set(tags))) or expl.get("verdict", "?")


def design_judge(canonical: str, asr: str) -> dict:
    """設計判定 V1(ASR テキストのみ)。verdict:
       EXACT                    綴り一致(本機構の対象外)
       PROD_PASS_UNCHANGED      Production が既に PASS(判定は変えない)
       DEFER_PROTECTED_FAIL     protected_check 不通過(数字/否定の不一致): 本機構は適用しない(既存判定へ)
       ACCEPT_M1                M1(同音綴り正規化 → 既存判定が PASS): 新規受理
       HR_CANDIDATE_EXPLAINED   音素水準で連結発音と説明できるが自動受理しない(M2、説明付き HR 候補)
       HR_CANDIDATE_RISK_FLAGGED  同上だが risk_flags あり(警告併記)
       DEFER_NOT_EXPLAINED      説明不能 / 音素証拠なし: 既存判定へ委譲(判定を変えない)"""
    if P.tokens(canonical) == P.tokens(asr):
        return {"verdict": "EXACT"}
    pj = prod_judge(canonical, asr)
    base = {"prod_classification": pj["classification"], "prod_pass": pj["pass"]}
    if pj["pass"]:
        return dict(base, verdict="PROD_PASS_UNCHANGED")
    if not pj["cls"].protected.passed:
        return dict(base, verdict="DEFER_PROTECTED_FAIL")
    # M1 は Production が『固有名詞/同音語のみの差で UNCERTAIN』とした場合に限る(TRUE_CONTENT_MISMATCH=内容語の差は対象外。
    # それは Eq Layer の入口条件[OPEN-122(4)]の別問題であり、M1 で覆い隠さない)。
    m1 = m1_try(canonical, asr, pj["cls"]) if pj["classification"] == "ASR_VALIDATION_UNCERTAIN" else None
    if m1:
        return dict(base, verdict="ACCEPT_M1", m1=m1)
    expl = P.explain_diff(canonical, asr)
    flags = P.risk_flags(canonical, asr)
    if expl["verdict"] in ("PHON_EXPLAINED_FUSION", "PHON_EXPLAINED_VOICING", "PHON_HOMOPHONE_ONLY"):
        return dict(base, verdict=("HR_CANDIDATE_RISK_FLAGGED" if flags else "HR_CANDIDATE_EXPLAINED"),
                    phon_verdict=expl["verdict"], subtype=_subtype_from_expl(expl), risk_flags=flags)
    return dict(base, verdict="DEFER_NOT_EXPLAINED", phon_verdict=expl["verdict"])


def v2_verdict(d: dict, tail: dict | None) -> str:
    """V2: ACCEPT_M1 に末尾完全性の独立確認を AND。確認不能/NG は HR 候補へ降格。"""
    if d["verdict"] == "ACCEPT_M1":
        if tail is not None and tail.get("tail_ok") is True:
            return "ACCEPT_M1"
        return "HR_CANDIDATE_TAIL_UNCONFIRMED" if tail is None else "HR_CANDIDATE_TAIL_SUSPECT"
    return d["verdict"]


def accept_like(v: str) -> bool:
    return v == "ACCEPT_M1"


def hr_like(v: str) -> bool:
    return v.startswith("HR_CANDIDATE")


# ---------------------------------------------------------------------------
# データ読み込み(既存データのみ)
# ---------------------------------------------------------------------------
def _load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def target_wav_map() -> dict:
    """er065 manifests から target_id -> 当該 target 単体の wav パス(role==target)。"""
    m = {}
    for p in glob.glob(ER065 + "/conditions_manifest_*.json"):
        d = _load_json(p)
        for c in d.get("conditions", []):
            for part in c.get("parts", []):
                if part.get("role") == "target":
                    m.setdefault(c["target_id"], part["path"])
    return m


def ds_real_diff_instances() -> list:
    out = []
    for i, x in enumerate(_load_json(P2 + "/d_instances_02.json")):
        out.append({"ds": "real_diff_instances", "id": f"rdi{i}", "canonical": x["canonical_window"], "asr": x["asr_window"],
                    "truth": "normal", "slow": None, "src": x.get("src")})
    return out


def ds_real_pairs_612() -> list:
    """HR queue + er021 telemetry 先頭 7155 行(CS 監査と同一範囲)。読み取りのみ。"""
    pairs = {}
    for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        c = d.get("canonical_text")
        for s in d.get("steps", []):
            if s.get("text") and c:
                pairs[(c, s["text"])] = "HRqueue"
    for n, l in enumerate(open("er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl", encoding="utf-8")):
        if n >= 7155:
            break
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get("canonical") and d.get("asr"):
            pairs.setdefault((d["canonical"], d["asr"]), "er021_telemetry")
    out = []
    for i, ((c, a), src) in enumerate(pairs.items()):
        if c.strip() != a.strip():
            out.append({"ds": "real_pairs_612", "id": f"rp{i}", "canonical": c, "asr": a, "truth": "unknown", "slow": None, "src": src})
    return out


def ds_general_windows() -> list:
    out = []
    for i, x in enumerate(_load_json(P2 + "/b_records_02.json")):
        if x["group"] != "p2_general" or not (x.get("region") or "").strip():
            continue
        out.append({"ds": "general_2word_" + ("control" if x["cat"] == "CTRL" else "fusion"), "id": f"gw{i}", "canonical": x["canon"],
                    "asr": x["region"], "truth": "normal", "slow": None, "engine": x["engine"], "cat": x["cat"]})
    return out


def ds_melos_c_records(twm: dict) -> list:
    out = []
    for i, x in enumerate(_load_json(P2 + "/c_records_02.json")):
        if not (x.get("region") or "").strip():
            continue
        g, cat = x["group"], x.get("category")
        base = {"id": f"cr{i}", "canonical": x["canon"], "asr": x["region"], "slow": None, "engine": x["engine"], "target": x["target"],
                "wav": twm.get(x["target"])}
        if g == "main" and x["variant"] == "base" and x["recipe"] == "R00_alone":
            out.append(dict(base, ds="melos_takes_alone", truth="unknown"))
        elif g == "synthetic":
            if cat == "synthetic_final_consonant_loss":
                out.append(dict(base, ds="defect_synth_tail_trunc", truth="defect"))
            elif cat == "synthetic_missing_word":
                out.append(dict(base, ds="defect_synth_missing_word", truth="defect"))
            elif cat == "synthetic_wrong_name":
                out.append(dict(base, ds="defect_synth_wrong_name", truth="defect"))
            elif cat == "intact_control":
                out.append(dict(base, ds="control_synth_intact", truth="normal"))
        elif g == "natural_ng" and x["variant"] == "base":
            out.append(dict(base, ds="defect_natural_ng_proxy_" + str(cat), truth="defect"))
    return out


def _sha_of(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ds_slowdown_pairs() -> list:
    """attempt_history の A2_SLOWDOWN_REVERIFY(減速後 ASR)と、直前の同 segment の PROCEED(減速前 Primary ASR)を対にする。
    canonical は wav と同じ run の tts_generation_results から取り、canonical_text_sha256 が一致する場合のみ採用。"""
    rows = [json.loads(l) for l in open("er011_output/attempt_history.jsonl", encoding="utf-8") if l.strip()]
    canon_cache = {}

    def canon_for(wav_path, seg):
        d = os.path.dirname(os.path.dirname(wav_path)) + "/audit/tts_generation_results.json"
        if d not in canon_cache:
            try:
                canon_cache[d] = _load_json(d).get("segments", {})
            except Exception:
                canon_cache[d] = {}
        s = canon_cache[d].get(seg) or {}
        return s.get("canonical_text") or s.get("text")

    out = []
    for idx, ev in enumerate(rows):
        if ev.get("action") != "A2_SLOWDOWN_REVERIFY":
            continue
        seg, theme = ev.get("segment_id"), ev.get("theme_id")
        canon = canon_for(ev["wav_path"], seg)
        pre = None
        for j in range(idx - 1, max(-1, idx - 40), -1):
            r = rows[j]
            if r.get("action") == "PROCEED" and r.get("segment_id") == seg and r.get("theme_id") == theme and r.get("attempts_detail"):
                pre = r
                break
        if not canon or pre is None:
            continue
        if pre.get("canonical_text_sha256") and _sha_of(canon) != pre["canonical_text_sha256"]:
            continue
        ok = [a for a in pre["attempts_detail"] if a.get("verified")] or pre["attempts_detail"]
        pre_txt = ok[-1].get("primary_asr_text")
        post_txt = ev.get("post_slowdown_asr_text")
        if not pre_txt or not post_txt:
            continue
        pid = f"{theme}:{seg}:{ev.get('attempt')}:{idx}"
        out.append({"ds": "slowdown_pair", "id": pid + ":pre", "pair": pid, "canonical": canon, "asr": pre_txt, "truth": "unknown", "slow": "pre"})
        out.append({"ds": "slowdown_pair", "id": pid + ":post", "pair": pid, "canonical": canon, "asr": post_txt, "truth": "unknown", "slow": "post"})
    return out


def ds_reeval_post() -> list:
    p = "er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/reeval_post_slowdown_01.json"
    d = _load_json(p)
    out = []
    for i, r in enumerate(d.get("rows", [])):
        if r.get("canonical") and r.get("primary_asr"):
            out.append({"ds": "reeval_post_slowdown_primary", "id": f"rp{i}:{r.get('case')}:{r.get('trial')}", "canonical": r["canonical"],
                        "asr": r["primary_asr"], "truth": "normal" if r.get("kind") == "positive" else "unknown", "slow": "post", "wav": r.get("wav")})
    return out


def ds_cs_audit_sweeps() -> list:
    """CS 監査の合成スイープ(18 固有名詞 x 次語6)と 25 件の合成対照を、既存 json から読む(再計算なし)。
    sweep: kind=exact_stem_drop / stem_variant_spelling は『構成上の正常想定』(真値は構成由来で確定ではない)。
    synthetic: label が COUNTER_ で始まるものを欠陥、それ以外を正常想定とする。"""
    d = _load_json("er026_output/family_z_production_e2e_01/melos/cs_audit_01/cs_offline_reeval_01.json")
    out = []
    for i, r in enumerate(d.get("sweep_rows", [])):
        out.append({"ds": "cs_sweep_" + r.get("kind", "?"), "id": f"sw{i}", "canonical": r["canonical"], "asr": r["asr"],
                    "truth": "normal_by_construction", "slow": None})
    for i, r in enumerate(d.get("synthetic", [])):
        lab = r.get("label", "")
        out.append({"ds": "cs_synthetic_" + ("counter" if lab.startswith("COUNTER_") else "normal"), "id": f"cs{i}", "canonical": r["canonical"],
                    "asr": r["asr"], "truth": "defect" if lab.startswith("COUNTER_") else "normal_by_construction", "slow": None, "label": lab})
    return out


# テキスト反例(真値=欠陥、構成により既知)。連結発音が起きやすい境界を意図的に含め、安全条件を突く。
TEXT_COUNTER = [
    # (canonical, asr, category)
    ("He can't talk to them.", "He can talk to them.", "negation"),
    ("They did not stop soon.", "They did stop soon.", "negation"),
    ("She never said sorry.", "She ever said sorry.", "negation"),
    ("It cannot start soon.", "It can start soon.", "negation"),
    ("There is no sign soon.", "There is a sign soon.", "negation"),
    ("She walked to school.", "She walk to school.", "tense"),
    ("He asked to leave.", "He ask to leave.", "tense"),
    ("They stopped to think.", "They stop to think.", "tense"),
    ("Sales rose by three percent.", "Sales rose by tree percent.", "number"),
    ("There are six sets.", "There are sick sets.", "number"),
    ("About ten sales were made.", "About tin sales were made.", "number"),
    ("The first set was fine.", "The fast set was fine.", "number"),
    ("Melos said hello.", "Melon said hello.", "wrong_name"),
    ("Melos said hello.", "Marcus said hello.", "wrong_name"),
    ("Melos said hello.", "Melody said hello.", "wrong_name"),
    ("Melos said hello.", "Mellis said hello.", "wrong_name"),
    ("Melos said hello.", "Milo said hello.", "wrong_name"),
    ("Melos said hello.", "Mel said hello.", "wrong_name"),
    ("Marcus smiled at him.", "Marker smiled at him.", "wrong_name"),
    ("Carlos stood still.", "Carla stood still.", "wrong_name"),
    ("Chris saw the ship.", "Cris saw the ship.", "wrong_name_or_spelling"),
    ("Melos said hello.", "Melos hello.", "word_dropped"),
    ("The studies suggest a link.", "The studies a link.", "word_dropped"),
    ("The bosses said so.", "The said so.", "word_dropped"),
    ("The class started late.", "The class late.", "word_dropped"),
    ("The studies suggest a link.", "The studio suggests a link.", "wrong_word"),
    ("The bosses said so.", "The bonus said so.", "wrong_word"),
    ("The bus stops here.", "The bu stops here.", "wrong_word"),
    ("This school starts soon.", "This schoo starts soon.", "wrong_word"),
    ("A nice sign.", "A nigh sign.", "wrong_word"),
    ("The guards seized him.", "The garden seized him.", "wrong_word"),
    ("He looked to the sea.", "He lock to the sea.", "wrong_word"),
    ("Prices fell sharply.", "Prices fall sharply.", "tense"),
    ("Sales increased slowly.", "Sales decreased slowly.", "meaning_flip"),
    ("The test passed soon.", "The test failed soon.", "meaning_flip"),
    ("The studies suggest cats today.", "The study suggests dogs today.", "multi_diff_masking_existing_hole"),
    ("Melos said hello to Marcus.", "Mello said hello to Marcos.", "multi_name_one_homophone"),
    ("Melos said hello to Marcus.", "Mello said hello to Mark.", "multi_name_one_homophone"),
    ("Melos said that he would return.", "Melos said that he would return home.", "context_extra_word"),
    ("Melos said.", "Melos said it.", "context_extra_word"),
    ("Ross said it.", "Rose said it.", "wrong_name"),
    ("Melos said.", "Mellow said.", "wrong_name"),  # 参考: 同音異綴り(下で除外=欠陥扱いにしない)
]
# 上の最終行は「同音異綴り」であり欠陥ではないので、下で normal_text へ移す
NORMAL_TEXT = [
    # 正常音声だが ASR が別綴り/語境界で揺れる典型(真値=正常)。固有名詞・一般語の同音異綴り+連結発音。
    ("Melos said.", "Melo said.", "proper_noun_pattern_a_native"),
    ("Melos said.", "Mello said.", "proper_noun_homophone_spelling"),
    ("Melos said.", "Mellow said.", "proper_noun_homophone_spelling"),
    ("Melos said.", "Mellos said.", "proper_noun_homophone_spelling_s_present"),
    ("Melos said hello.", "Mello said hello.", "proper_noun_homophone_spelling"),
    ("Marcus smiled.", "Marcu smiled.", "proper_noun_pattern_a_native"),
    ("Thomas sat down.", "Thoma sat down.", "proper_noun_pattern_a_native"),
    ("Thomas sat down.", "Tomma sat down.", "proper_noun_other_spelling"),
    ("Carlos saw him.", "Carlo saw him.", "proper_noun_pattern_a_native"),
    ("Carlos saw him.", "Karlo saw him.", "proper_noun_homophone_spelling"),
    ("The studies suggest a link.", "The study suggests a link.", "general_pattern_a_native"),
    ("The bosses said so.", "The boss said so.", "general_pattern_a_native"),
    ("The classes started late.", "The class started late.", "general_pattern_a_native"),
    ("The cities seem calm.", "The city seem calm.", "general_pattern_a_native"),
    ("The glasses sit there.", "The glass sit there.", "general_pattern_a_native"),
    ("The bosses said so.", "The bosse said so.", "general_homophone_spelling"),
    ("The prices spiked.", "The price spiked.", "general_pattern_a_native"),
    ("He opened to them.", "He open to them.", "pattern_b_native"),
    ("The wheels spun.", "The wheel spun.", "general_pattern_a_native"),
    ("The cross sign was clear.", "The cros sign was clear.", "general_nonword_spelling"),
]


def ds_text_sets() -> list:
    out = []
    for i, (c, a, cat) in enumerate(TEXT_COUNTER):
        if a == "Mellow said.":
            continue
        out.append({"ds": "defect_text_" + cat, "id": f"tc{i}", "canonical": c, "asr": a, "truth": "defect", "slow": None})
    for i, (c, a, cat) in enumerate(NORMAL_TEXT):
        out.append({"ds": "normal_text_" + cat, "id": f"nt{i}", "canonical": c, "asr": a, "truth": "normal", "slow": None})
    return out


# ---------------------------------------------------------------------------
# 評価
# ---------------------------------------------------------------------------
def evaluate_record(r: dict) -> dict:
    c, a = r["canonical"], r["asr"]
    d = design_judge(c, a)
    v0 = True if d["verdict"] == "EXACT" else bool(d.get("prod_pass"))
    tail = tail_integrity(r.get("wav")) if r.get("wav") else None
    v1 = d["verdict"]
    v2 = v2_verdict(d, tail)
    return {
        "ds": r["ds"], "id": r["id"], "truth": r.get("truth"), "slow": r.get("slow"), "pair": r.get("pair"), "engine": r.get("engine"),
        "target": r.get("target"), "canonical": c if len(c) <= 140 else c[:140] + "...", "asr": a if len(a) <= 140 else a[:140] + "...",
        "v0_prod_pass": v0, "v0_class": d.get("prod_classification", "EXACT"), "va_pattern_abc": pattern_abc_only(c, a),
        "v1": v1, "v2": v2, "tail": tail, "wav": r.get("wav"),
        "asr_full": a if r.get("ds") == "slowdown_pair" else None,
        "m1": d.get("m1"), "subtype": d.get("subtype"), "risk_flags": d.get("risk_flags"), "phon_verdict": d.get("phon_verdict"),
    }


def _subtype_of_accept(e: dict) -> str:
    """ACCEPT_M1 の内訳: 固有名詞(canonical 語が CMU 未収録、または文中で大文字始まり) / 一般語、と受理に使われた既存規則。"""
    m1 = e["m1"] or {}
    sub = (m1.get("subs") or [{}])[0]
    cw = (sub.get("canonical_word") or "").lower()
    toks = re.findall(r"[A-Za-z']+", e["canonical"])
    cap_mid = any(t.lower() == cw and t[:1].isupper() and i > 0 for i, t in enumerate(toks))
    kind = "proper_noun" if sub.get("entity_like") or cap_mid or not _cmu_variants(cw) else "general_word"
    rule = m1.get("cs_rule") or m1.get("variant_classification")
    return f"{kind}|{rule}"


def summarize(evals: list) -> dict:
    S = {"n": len(evals)}
    by_ds = collections.defaultdict(list)
    for e in evals:
        by_ds[e["ds"]].append(e)
    S["by_ds"] = {}
    for ds, xs in sorted(by_ds.items()):
        s = {"n": len(xs),
             "v0_pass": sum(1 for e in xs if e["v0_prod_pass"]),
             "va_pass": sum(1 for e in xs if e["va_pattern_abc"] or e["v1"] == "EXACT"),
             "v1_accept_new": sum(1 for e in xs if accept_like(e["v1"]) and not e["v0_prod_pass"]),
             "v1_hr_candidate": sum(1 for e in xs if hr_like(e["v1"]) and not e["v0_prod_pass"]),
             "v2_accept_new": sum(1 for e in xs if accept_like(e["v2"]) and not e["v0_prod_pass"]),
             "v2_hr_candidate": sum(1 for e in xs if hr_like(e["v2"]) and not e["v0_prod_pass"]),
             "v1_verdicts": dict(collections.Counter(e["v1"] for e in xs)),
             "with_wav": sum(1 for e in xs if e.get("tail") is not None)}
        S["by_ds"][ds] = s
    return S


def slowdown_consistency(evals: list) -> dict:
    pairs = collections.defaultdict(dict)
    for e in evals:
        if e["ds"] == "slowdown_pair":
            pairs[e["pair"]][e["slow"]] = e

    def grp(v):
        if v in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1"):
            return "PASS"
        if v.startswith("HR_CANDIDATE"):
            return "HR"
        return "DEFER"
    n = len(pairs)
    same_v0 = sum(1 for p in pairs.values() if p["pre"]["v0_prod_pass"] == p["post"]["v0_prod_pass"])
    same_v1 = sum(1 for p in pairs.values() if grp(p["pre"]["v1"]) == grp(p["post"]["v1"]))
    # 音素列が同一(同じ ASR 正規化後)なら判定も同一であることの確認: 同一文字列対
    same_text = [p for p in pairs.values() if p["pre"]["asr_full"] == p["post"]["asr_full"]]
    same_text_same_v1 = sum(1 for p in same_text if p["pre"]["v1"] == p["post"]["v1"])
    diff_rows = [{"pair": k, "canonical": p["pre"]["canonical"], "pre_asr": p["pre"]["asr"], "post_asr": p["post"]["asr"],
                  "pre_v1": p["pre"]["v1"], "post_v1": p["post"]["v1"], "pre_v0": p["pre"]["v0_prod_pass"], "post_v0": p["post"]["v0_prod_pass"]}
                 for k, p in pairs.items() if grp(p["pre"]["v1"]) != grp(p["post"]["v1"])]
    return {"n_pairs": n, "v0_same_pass_state": same_v0, "v1_same_group": same_v1, "same_text_pairs": len(same_text),
            "same_text_same_verdict": same_text_same_v1, "v1_group_mismatch_rows": diff_rows}



PROBE_NAMES = ("Carlos Marcus Thomas James Lewis Louis Charles Agnes Alexis Dennis Francis Hermes Atlas Paris Silas Elias Lucas "
               "Nicholas Venus Pegasus Jones Hughes Bess Moses Cyrus Julius Theseus Orpheus Hades Ares Helios Sophocles Socrates "
               "Diogenes Archimedes Aeneas Achilles Hercules Ulysses Zeus Chris Giles Wells Mills Hayes Reyes Gomes Torres Ramos "
               "Santos Silvas Rojas Haynes Melos").split()
PROBE_NEXT = ("said", "saw", "sat", "spoke", "stood", "smiled")


def surface_expansion_probe() -> dict:
    """受理面の拡張プローブ(真値なし・構成のみ): s終わり固有名詞 x 歯擦音始まり動詞で、
    Pattern A が綴りとして受理する ASR 形(stem 綴り)に対し、M1 が新たに受理する同音綴りの数と実例を数える。
    『同音異綴りの正規化で受理面がどれだけ広がるか(=誤PASS露出の増分の上限)』の見積りであり、誤PASS率ではない。"""
    rows, total_extra, names_with_extra = [], 0, 0
    for n in PROBE_NAMES:
        native = set()
        for st in (n[:-1].lower(), n[:-2].lower() if n.lower().endswith("es") else None):
            if st:
                native.add(st)
        extras = set()
        for nx in PROBE_NEXT:
            canon = f"{n} {nx}."
            for st in list(native):
                cls_words, _ = homophone_class(st, primary_only=True)
                for v in cls_words:
                    if v in native:
                        continue
                    d = design_judge(canon, f"{v.capitalize()} {nx}.")
                    if d["verdict"] == "ACCEPT_M1":
                        extras.add(v)
        if extras:
            names_with_extra += 1
            total_extra += len(extras)
        rows.append({"name": n, "native_stems": sorted(native), "m1_extra_spellings": sorted(extras)})
    return {"n_names": len(PROBE_NAMES), "names_with_extra": names_with_extra, "total_extra_spellings": total_extra, "rows": rows}


def tail_calibration() -> dict:
    """末尾完全性チェックの較正/検出率(ローカル DSP のみ)。閾値は Production の健全な wav のみから決めた(切詰 wav では調整していない)。"""
    out = {}
    for label, pat in (("production_a2_narration", "er026_output/family_z_production_e2e_01/melos/run_e2e_02/a2/narration/*.wav"),
                       ("production_b1b_narration", "er026_output/family_z_production_e2e_01/melos/run_e2e_02/b1b/narration/*.wav")):
        xs = [tail_integrity(p) for p in sorted(glob.glob(pat)) if "_original" not in p]
        xs = [x for x in xs if x]
        out[label] = {"n": len(xs), "tail_ok": sum(1 for x in xs if x["tail_ok"]),
                      "max_rel_tail_db": max((x["rel_tail_db"] for x in xs), default=None)}
    return out


def tail_detection_by_target(evals: list) -> dict:
    by = collections.defaultdict(lambda: {"n_wav": set(), "tail_ng": set()})
    for e in evals:
        if e["ds"] in ("defect_synth_tail_trunc", "control_synth_intact") or e["ds"].startswith("defect_natural_ng"):
            if e.get("tail") is not None and e.get("target"):
                key = (e["ds"], e["target"])
                by[key]["n_wav"].add(e["wav"])
                if not e["tail"]["tail_ok"]:
                    by[key]["tail_ng"].add(e["wav"])
    res = {}
    for (ds, t), v in sorted(by.items()):
        res[f"{ds}|{t}"] = {"wavs": len(v["n_wav"]), "tail_flagged_wavs": len(v["tail_ng"])}
    return res


def write_report(out_dir: str, S: dict, evals: list) -> str:
    L = []
    A = L.append
    A("# OFFLINE_EVAL_01: 発音同等性に基づく一般化ASR判定(Trial隔離プロトタイプ)の既存データ read-only 評価\n")
    A("管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01 / 費用 JPY0 / 新規API呼出 0 / 使用モデル: なし(CMU辞書・ローカルDSPのみ) / Production無変更\n")
    A("KPI provenance: 本表の数値はすべて `reuse`(既存転写・既存wavの再評価)+`synthetic`(er065合成反例・CS監査合成sweep・本script内の構成テキスト反例)。fresh Production初回path E2E値: No。\n")
    A("## 0. 比較する判定(定義)\n")
    A("- **V0** Production現行: `val.classify_asr_match`(segment_id=FULL_STORY)+ `_step_alternate_pass`(CMU同音Case A)。Tier3(Azure)等ASR呼出を要する救済は含まない(read-only)。")
    A("- **VA** 既存Pattern A/B/C単独(`csv3.classify_connected_speech`)。")
    A("- **V1** 設計判定(ASR転写テキストのみ): V0がPASSならそのまま(判定を変えない)/ V0 UNCERTAIN(固有名詞・同音語のみの差)でM1(CMU確認済み同音綴り正規化→既存判定)が通れば ACCEPT_M1 / 音素水準で連結発音と説明できれば説明付きHR候補(M2)/ 説明不能は既存判定へ委譲。")
    A("- **V2** V1のACCEPT_M1に『clip末尾完全性の独立確認(ローカルDSP)』をAND。確認不能(wavなし)・NGはHR候補へ降格。")
    A(f"  末尾確認: 末尾{TAIL_MS}msの最大フレームRMSが、clipのp95フレームRMS比{TAIL_THRESHOLD_DB:.0f}dB以下。閾値はProduction健全wavのみから決定(切詰wavでは調整していない)。\n")
    by = S["by_ds"]
    normal_like = ("normal", "unknown", "normal_by_construction")
    A("## 1. 評価A: 正常音声の誤NG削減(V0が通さないもののうち、V1/V2が救済する件数)\n")
    A("真値列: normal=Production採用済み正常音声由来/unknown=真値未確定(HR待ちを含む)/normal_by_construction=構成上正常想定(循環の恐れあり、参考値)。\n")
    A("| データセット | 真値 | n | V0 PASS | V0非PASS | V1 新規ACCEPT | V1 HR候補 | V2 新規ACCEPT | V2 HR候補 | wav有 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    tot = collections.Counter()
    for ds, v in by.items():
        truths = {e["truth"] for e in evals if e["ds"] == ds}
        if not (truths & set(normal_like)):
            continue
        nonpass = v["n"] - v["v0_pass"]
        A(f"| {ds} | {','.join(sorted(t for t in truths if t))} | {v['n']} | {v['v0_pass']} | {nonpass} | {v['v1_accept_new']} | {v['v1_hr_candidate']} | {v['v2_accept_new']} | {v['v2_hr_candidate']} | {v['with_wav']} |")
        if ds in ("real_pairs_612", "general_2word_fusion", "general_2word_control", "melos_takes_alone", "control_synth_intact",
                  "reeval_post_slowdown_primary"):
            tot["nonpass"] += nonpass
            tot["acc"] += v["v1_accept_new"]
            tot["hr"] += v["v1_hr_candidate"]
    A(f"\n実データ系の合計(real_pairs_612 / general_2word_fusion / general_2word_control / melos_takes_alone / control_synth_intact / reeval_post_slowdown_primary。"
      f"real_diff_instances は real_pairs_612 と同一ログ由来のため重複除外): V0非PASS {tot['nonpass']}件中、V1新規ACCEPT {tot['acc']}件、V1説明付きHR候補 {tot['hr']}件。")
    A("(slowdown_pair・cs_sweep・normal_text・cs_synthetic は構成/重複のため別掲の参考値で合計に含めない。)\n")
    acc = [e for e in evals if e["v1"] == "ACCEPT_M1" and not e["v0_prod_pass"] and e["truth"] in normal_like]
    cnt = collections.Counter(_subtype_of_accept(e) for e in acc)
    A("### 1-1. V1新規ACCEPTの内訳(真値normal/unknown/構成想定の全データセット、重複を含む)\n")
    A("| 種別 | 受理に使われた既存規則 | 件数 |")
    A("|---|---|---|")
    for k, n in sorted(cnt.items(), key=lambda x: -x[1]):
        kind, rule = k.split("|")
        A(f"| {kind} | {rule} | {n} |")
    A("\n新規ACCEPTの正規化(元綴り→置換綴り→対応canonical語):\n")
    uniq = collections.Counter()
    for e in acc:
        for sb in e["m1"]["subs"]:
            uniq[(sb["from"], sb["to"], sb["canonical_word"], sb["provenance"], bool(sb.get("entity_like")))] += 1
    A("| ASR綴り | 置換(同音綴り) | canonical語 | 根拠 | 固有名詞扱い | 件数 |")
    A("|---|---|---|---|---|---|")
    for (f, t, c, pv, en), n in sorted(uniq.items(), key=lambda x: -x[1]):
        A(f"| {f} | {t} | {c} | {pv} | {en} | {n} |")
    non_melos = [e for e in acc if not any(sb["canonical_word"] == "melos" for sb in e["m1"]["subs"])]
    A(f"\n**Melos以外の新規ACCEPT件数: {len(non_melos)}件**(実データ・sweepとも、新規救済はMelosの `Mello/Mellow/Mellos/Mellows` に限られた。一般化の実効は『ASR綴りがCMU収録語の同音綴りで、かつ承認済みPattern/厳密一致が期待する綴りと同音』の場合に限られ、実データではMelosのみ。)")
    for e in non_melos[:10]:
        A(f"  - {e['ds']}: `{e['canonical']}` / `{e['asr']}` / {e['m1']['subs']}")
    hr = [e for e in evals if e["v1"].startswith("HR_CANDIDATE") and not e["v0_prod_pass"] and e["truth"] in normal_like]
    hc = collections.Counter((e["v1"], e.get("subtype")) for e in hr)
    A("\n### 1-2. V1 説明付きHR候補の内訳(自動受理ではない。HR件数は減らさず確認時間の短縮のみ)\n")
    A("| 区分 | 音韻診断(境界型等) | 件数 |")
    A("|---|---|---|")
    for (v, st), n in sorted(hc.items(), key=lambda x: -x[1]):
        A(f"| {v} | {st} | {n} |")
    A("\n## 2. 評価B: 異常音声の誤PASS防止(真値=欠陥のデータセット)\n")
    A("既存誤PASS(V0 PASS)は『テキストだけでは検出できない既存の限界』(例: 末尾切詰でASRが全文を正しく書いた、Pattern Aの first-diff-only 受理)を含む。本設計の評価指標は **増分** = V0がPASSにしないのにV1/V2がACCEPTにした件数(目標0)。\n")
    A("| データセット(欠陥の種類) | n | V0 PASS(既存誤PASS) | VA PASS | V1 新規ACCEPT=増分 | V2 新規ACCEPT=増分 | V1→V2でHRへ降格 |")
    A("|---|---|---|---|---|---|---|")
    tinc1 = tinc2 = tv0 = ttot = 0
    for ds, v in by.items():
        truths = {e["truth"] for e in evals if e["ds"] == ds}
        if "defect" not in truths:
            continue
        A(f"| {ds} | {v['n']} | {v['v0_pass']} | {v['va_pass']} | {v['v1_accept_new']} | {v['v2_accept_new']} | {v['v1_accept_new'] - v['v2_accept_new']} |")
        tinc1 += v["v1_accept_new"]
        tinc2 += v["v2_accept_new"]
        tv0 += v["v0_pass"]
        ttot += v["n"]
    A(f"\n**合計: 欠陥観測 {ttot}件、既存誤PASS(V0) {tv0}件、V1増分 {tinc1}件、V2増分 {tinc2}件。**\n")
    inc1 = [e for e in evals if e["truth"] == "defect" and e["v1"] == "ACCEPT_M1" and not e["v0_prod_pass"]]
    A("V1増分の全内訳(ds / target / ASR転写 / 末尾チェック):")
    cc = collections.Counter((e["ds"], e.get("target"), e["asr"], (e.get("tail") or {}).get("tail_ok")) for e in inc1)
    for (ds, t, a, tk), n in sorted(cc.items(), key=lambda x: str(x)):
        A(f"  - {ds} / {t} / `{a}` / tail_ok={tk} : {n}件")
    A("\n**判定規則(委任文)**: Pattern A比の誤PASS増分>0の方式は採用候補から外す(REJECTED候補)。V1(テキストのみ)の増分は " + str(tinc1) + "件 → " + ("**REJECTED候補**" if tinc1 > 0 else "増分なし") + "。V2(+末尾確認)の増分は " + str(tinc2) + "件(ただし下記のとおり検出網羅性は未検証)。\n")
    A("## 3. 末尾完全性チェックの較正と検出率\n")
    cal = tail_calibration()
    A("| 健全wav群(Production run_e2e_02、_original除く) | n | tail_ok | 最大rel_tail_db |")
    A("|---|---|---|---|")
    for k, v in cal.items():
        A(f"| {k} | {v['n']} | {v['tail_ok']} | {v['max_rel_tail_db']} |")
    A("\n切詰・欠陥wav側(target単位、wav数/末尾チェックで検出された数):\n")
    A("| ds target | wav数 | tail_flagged |")
    A("|---|---|---|")
    for k, v in tail_detection_by_target(evals).items():
        A(f"| {k} | {v['wavs']} | {v['tail_flagged_wavs']} |")
    A("\n注意(未検証/限界): (1) 合成切詰wav(syn_B*_trunc)は『発話末をN ms削除+8ms fade』で作られ、**元wavの末尾無音も同時に失われる**ため、末尾エネルギー検出が実際のTTS切詰より容易な可能性がある。(2) B2/B4の70-220ms切詰の一部は末尾チェックを通過する(検出されない)。(3) 自然に発生したTTS末尾欠損の真値付きwavは本データに無い(natural_ng は proxy)。→ V2の増分0は『この小さな合成セットで』であり一般的な保証ではない。\n")
    sd = S["slowdown"]
    A("## 4. 減速前後(Std 6%減速)の判定一致\n")
    A(f"attempt_history の A2_SLOWDOWN_REVERIFY 由来の(減速前Primary転写, 減速後Primary転写)対: {sd['n_pairs']}対(canonicalはtts_generation_resultsから復元、sha256一致のみ採用)。")
    A(f"- 同一転写文字列の対 {sd['same_text_pairs']}対で、V1の判定が同一: **{sd['same_text_same_verdict']}/{sd['same_text_pairs']}**(判定はcanonicalと転写テキストの純関数であり、減速の有無を入力に持たない=判定思想は減速前後で同一)。")
    A(f"- 転写が異なる対を含む全{sd['n_pairs']}対での PASS/HR/DEFER 群の一致: V0={sd['v0_same_pass_state']}/{sd['n_pairs']}、V1={sd['v1_same_group']}/{sd['n_pairs']}。不一致はASR転写自体が減速で変わったこと(例 Mellows→mellowes)による。")
    A("- 注意: 減速前後は別音声(6%伸長)のため『同一wav対』ではなく『同一take対』。ASR転写が揺れる限り判定も揺れる(判定器でなくASR揺れの問題)。\n")
    A("| pair | canonical | 減速前ASR | 減速後ASR | 前V1 | 後V1 |")
    A("|---|---|---|---|---|---|")
    for r in sd["v1_group_mismatch_rows"]:
        A(f"| {r['pair']} | {r['canonical'][:40]} | {r['pre_asr'][:40]} | {r['post_asr'][:40]} | {r['pre_v1']} | {r['post_v1']} |")
    pr = S.get("surface_probe") or {}
    A("\n## 5. 受理面の拡張プローブ(構成のみ・真値なし): 同音綴り正規化で『Pattern Aが受理する綴り』に何が加わるか\n")
    A(f"s終わり固有名詞 {pr.get('n_names')}語 x 歯擦音始まり動詞6語。Pattern A が受理する ASR 形(stem 綴り)の CMU 代表発音同音綴りのうち、M1 が新たに ACCEPT にした綴りの数: "
      f"**{pr.get('names_with_extra')}語で追加あり、追加綴り延べ {pr.get('total_extra_spellings')}個**。")
    A("これは『ASRが語末sを落とした音声の別綴り』だけでなく、**語末sが元から無い別の実在語・別の名前**(例 Jones→Joan、Hayes→Hey、Torres→Tore)も、s脱落の仮定の下で同じ基準で受理されることを意味する。"
      "Pattern A 自体が `Hayes said ← Hay said` を綴りで受理する既存の性質(OPEN-330)の自然な延長だが、**受理面が広がる**事実は誤PASS露出の増分として Opus/ユーザーの判断対象(音響の独立証拠なしには区別不能)。\n")
    A("| 名前 | Pattern A が受理する stem 綴り | M1 が追加で受理する同音綴り |")
    A("|---|---|---|")
    for r in pr.get("rows", []):
        if r["m1_extra_spellings"]:
            A(f"| {r['name']} | {', '.join(r['native_stems'])} | {', '.join(r['m1_extra_spellings'])} |")
    A("\n## 6. State guard\n")
    A("`state_guard_01.json` 参照: 実行前後で Production state 9ファイル(Melos run_e2e_02 a2/b1b の review_lock_state・tts_generation_results、Master Store manifest、er021 telemetry、HR queue、attempt_history、Pronunciation ledger)の sha256/行数が不変: " + str(all(S["state_guard"]["unchanged"].values())))
    path = os.path.join(out_dir, "OFFLINE_EVAL_01.md")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return path


def run(out_dir: str, no_telemetry: bool = True) -> dict:
    assert no_telemetry, "telemetry 追記は許可されない"
    os.makedirs(out_dir, exist_ok=True)
    before = guard.snapshot()
    t0 = time.time()
    twm = target_wav_map()
    recs = []
    recs += ds_real_diff_instances()
    recs += ds_real_pairs_612()
    recs += ds_general_windows()
    recs += ds_melos_c_records(twm)
    recs += ds_slowdown_pairs()
    recs += ds_reeval_post()
    recs += ds_text_sets()
    recs += ds_cs_audit_sweeps()
    evals = [evaluate_record(r) for r in recs]
    S = summarize(evals)
    S["slowdown"] = slowdown_consistency(evals)
    after = guard.snapshot()
    S["state_guard"] = {"unchanged": guard.diff(before, after), "before": before, "after": after}
    S["elapsed_s"] = round(time.time() - t0, 1)
    S["surface_probe"] = surface_expansion_probe()
    S["tail_calibration"] = tail_calibration()
    S["tail_detection_by_target"] = tail_detection_by_target(evals)
    S["tail_params"] = {"threshold_db": TAIL_THRESHOLD_DB, "tail_ms": TAIL_MS}
    json.dump({"summary": S, "records": evals}, open(os.path.join(out_dir, "offline_eval_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    write_report(out_dir, S, evals)
    json.dump(S["state_guard"], open(os.path.join(out_dir, "state_guard_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return {"summary": S, "records": evals}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=OUT_DEFAULT)
    ap.add_argument("--no-telemetry", action="store_true", required=True)
    args = ap.parse_args()
    res = run(args.out_dir, no_telemetry=True)
    print(json.dumps({k: v for k, v in res["summary"].items() if k != "state_guard"}, ensure_ascii=False, indent=1)[:6000])
    print("state_guard unchanged:", res["summary"]["state_guard"]["unchanged"])
