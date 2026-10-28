# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B 統合proto(research/DEV専用。Productionからimportされない。API 0。LLM 0)。
# 層: L0=現行Production HEAD / L1=v2読み層+不規則読みガード / L2=β composite / L3=読み候補辞書拡張(数量+超の接尾 超え/越え/こえ) / L4=best-of-N(別関数)
# 既定(Flags()全OFF)はL0と同一出力(=Production adapterをそのまま呼ぶだけ)。Production関数(er007_ja_secondary_asr_01/er078_*)は呼ぶだけで編集しない。
# Productionの _numeric_value_equivalence / _azure_stt_strict を判定の間だけ in-process 差替し、finallyで必ず元へ戻す。
# 参照元(複製しない): proto_reading_compare_02.py(v2)・b_light_proto_02.py(β)・eval_unified_01.py(M0〜M4のadapter/ELIG)。
from __future__ import annotations
import difflib, hashlib, re, sys, unicodedata
from dataclasses import dataclass
from math import comb
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E     # javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False(LLM 0)・socket guard・dummy wav
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import proto_reading_compare_02 as P
import b_light_proto_02 as B

PASSING = uj.PASSING_STATES
ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")
_ORIG = sec._numeric_value_equivalence
L3_LABEL = "L3_dict_koe"
# L3: 『超』の読み候補(ちょう/こえ)。ASR側の表記 超え/越え/こえ(直後が活用語尾でないとき)を『超』へ正規化する。数量atom直後の『超』にだけ適用。
_KOE_RE = re.compile(r"^(超え|越え|こえ)(?![るたてなばずよ])")


@dataclass(frozen=True)
class Flags:
    l1: bool = False
    l2: bool = False
    l3: bool = False

    def name(self) -> str:
        return "+".join(n for n, f in (("L1", self.l1), ("L2", self.l2), ("L3", self.l3)) if f) or "L0"


def irregular_atoms(canon: str) -> list:
    return [a.surface for a in vg.extract_atoms_ja(canon) if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]


def _num_atoms(text: str) -> list:
    return [a for a in vg.extract_atoms_ja(text) if a.kind == "num"]


def l3_rewrite(canon: str, text: str | None, other: str | None):
    """L3の発火判定+正規化。戻り=(新text, 監査dict|None)。発火しなければ (text, None)。fail-closed。
    条件: (1)text/other両方ある (2)両方とも原稿との値ガードEQUAL (3)原稿のnum atom直後が『超』 (4)textの同じ順位のnum atom直後が 超え/越え/こえ。"""
    if not text or not other:
        return text, None
    cn = unicodedata.normalize("NFKC", canon or "")
    if len(unicodedata.normalize("NFKC", text)) != len(text):
        return text, None                       # 位置ずれ回避(fail-closed)
    for t in (text, other):
        if vg.value_guard(canon, t, "ja").kind != vg.EQUAL:
            return text, None
    c_atoms, t_atoms = _num_atoms(cn), _num_atoms(text)
    if len(c_atoms) != len(t_atoms) or [(a.value, a.unit) for a in c_atoms] != [(a.value, a.unit) for a in t_atoms]:
        return text, None
    out, shift, fired = text, 0, []
    for ca, ta in zip(c_atoms, t_atoms):
        if cn[ca.end:ca.end + 1] != "超":
            continue
        m = _KOE_RE.match(text[ta.end:])
        if not m:
            continue
        s = ta.end + shift
        out = out[:s] + "超" + out[s + len(m.group(1)):]
        shift += 1 - len(m.group(1))
        fired.append(f"{ca.surface}超<-{m.group(1)}")
    if not fired:
        return text, None
    return out, {"layer": L3_LABEL, "rewrites": fired}


def make_layer(flags: Flags, ctx: dict, audit: list):
    """Production _numeric_value_equivalence 位置の差替関数(L1有効時のみ使う)。ctx={'prim','sec'}。auditへ発火根拠を追記。"""
    def layer(canon, asr, cls):
        side = "secondary" if sys._getframe(1).f_code.co_name == "_secondary_accept" else "primary"
        irr = irregular_atoms(canon)
        if irr:                                       # L1新規ガード: 不規則読み数詞は両側・両kindでv2対象外→Production判定へ戻す
            audit.append({"layer": "L1_irregular_guard", "side": side, "atoms": irr})
            return _ORIG(canon, asr, cls)
        asr2, aud3, cls2 = asr, None, cls
        if flags.l3:
            other = ctx.get("sec") if side == "primary" else ctx.get("prim")
            asr2, aud3 = l3_rewrite(canon, asr, other)
            if aud3:
                cls2 = javal.classify_ja_asr_match(canon, asr2, expected_readings=None, allow_reading_resolver=False)
        if aud3 and cls2.classification != "TRUE_CONTENT_MISMATCH":
            if cls2.should_pass:                      # 辞書正規化だけで原稿と一致/Production既存規則で受理
                audit.append(dict(aud3, side=side, via="surface"))
                return P.to_classification(P.V1Result(True, "DICT", "l3_dict_then_production_match", P.VALUE_LABEL, ("JA_DICT_KOE",), "L3"), cls)
            return _ORIG(canon, asr, cls)
        r = P.pron_value_equivalence(canon, asr2, cls=cls2, expected_readings=None, side=side)
        if r.equal:
            if aud3:
                audit.append(dict(aud3, side=side, via="v1:" + str(r.cause)))
            elif r.kind == "PRON":
                audit.append({"layer": "L1_v2_pron", "side": side, "cause": r.cause})
            return P.to_classification(r, cls)
        return _ORIG(canon, asr, cls)                 # フォールバック=Production層(L1 ⊇ L0)
    return layer


def _adapter(canon, prim, sec_text, wav, flags: Flags, audit: list):
    ctx = {"prim": prim, "sec": sec_text}
    orig_az = sec._azure_stt_strict
    if sec_text is not None:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (sec_text, None)
    else:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary")
    sec._numeric_value_equivalence = make_layer(flags, ctx, audit) if flags.l1 else _ORIG
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, wav, cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig_az
        sec._numeric_value_equivalence = _ORIG
    return r


def judge(canon: str, prim: str | None, sec_text: str | None, wav: str, flags: Flags = Flags()) -> dict:
    """1対(Primary転写, Secondary転写)の最終Gate判定。戻り: cat(PASS/PASS_W/NG)/state/reason/route/layers(監査)/sec_called/needs_new_azure_call。"""
    audit: list = []
    r = _adapter(canon, prim, sec_text, wav, flags, audit)
    j = r["asr_judgement"]
    st, rc = j.get("state"), j.get("reason_code")
    sec_called = bool((j.get("secondary") or {}).get("called"))
    fired = [a for a in audit if a.get("layer") in ("L1_v2_pron", L3_LABEL)]
    if st in PASSING:
        ftag = "|".join(sorted({a["layer"] + ":" + a.get("side", "") + ":" + str(a.get("cause", a.get("via", ""))) for a in fired}))
        if st == "PASS_WITH_WARNING":
            cat, route = "PASS_W", (ftag + "|" if ftag else "") + "prod_warning:" + ",".join(j.get("warnings") or [])
        elif fired:
            cat, route = "PASS_W", ftag
        else:
            cat, route = "PASS", "prod:" + str(rc)
        return {"cat": cat, "state": st, "reason": rc, "route": route, "sec_called": sec_called, "layers": audit,
                "needs_new_azure_call": bool(any(a.get("layer") == L3_LABEL for a in audit) and not sec_called)}
    out = {"cat": "NG", "state": st, "reason": rc, "route": str(rc), "sec_called": sec_called, "layers": audit, "needs_new_azure_call": False}
    if flags.l2 and sec_text and any(str(rc).startswith(e) for e in ELIG):
        p2, s2, a3 = prim, sec_text, None
        if flags.l3:
            p2, a3 = l3_rewrite(canon, prim, sec_text)
            s2 = l3_rewrite(canon, sec_text, prim)[0] if a3 else sec_text
        sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
        b = B.composite_judge(canon, p2, s2, {"engine": "azure", "wav_sha256": sha, "model_id": "azure-speech-stt"})
        if b.equal:
            out.update(cat="PASS_W", state="PASS_WITH_WARNING", reason="composite", route="L2_beta_composite" + (":listen" if b.listen_required else ""),
                       needs_new_azure_call=(not sec_called))
            out["layers"] = audit + [{"layer": "L2_beta", "listen": b.listen_required, "reasons": list(b.listen_reasons)}] + ([dict(a3, side="primary", via="beta_input")] if a3 else [])
        else:
            out["beta_blocked_by"] = b.blocked_by
    return out


# ---------------- L4: best-of-N(判定前のOpenAI再転写)のシミュレーション ----------------
def best_of_n(draw_results: list, n: int) -> dict:
    """draw_results: 保存順の判定結果列(各要素は judge() の戻り)。最初にPASS/PASS_Wになったdrawで停止。N個以内になければNG(draw1の理由)。"""
    for i, r in enumerate(draw_results[:n], 1):
        if r["cat"] != "NG":
            return {"cat": r["cat"], "stopped_at": i, "extra_openai_calls": i - 1, "reason": r["reason"], "route": r["route"]}
    first = draw_results[0] if draw_results else {"reason": None, "route": None}
    return {"cat": "NG", "stopped_at": None, "extra_openai_calls": min(n, len(draw_results)) - 1, "reason": first["reason"], "route": first.get("route")}


def hyper_reach(k: int, m: int, n: int) -> float:
    """k draw中m本が非NG。無作為にn個選んで少なくとも1本が非NGの確率(超幾何)。"""
    n = min(n, k)
    if m <= 0 or k <= 0:
        return 0.0
    return 1.0 - (comb(k - m, n) / comb(k, n) if k - m >= n else 0.0)


# ---------------- (iv) Human Review 候補条件(機械案。PASS/NGを変えない=人間の試聴キューへ付ける証拠だけ) ----------------
def hr_candidate(canon: str, pairs: list) -> dict:
    """pairs=[(primary, secondary|None), ...](同一wavの全draw)。全層NG後に呼ぶ。HR候補=次の3条件を満たす対が1つでもある:
    (a)少なくとも片方のengineの値ガードがEQUAL かつ全転写に否定差なし
    (b)値atomを除いた読み(助詞発音規則v2のモーラ列)の差分が原稿に対し連続1区間・3モーラ以内
    (c)原稿に不規則読み数詞なし(読みの正誤が表記から判別できない)
    この関数はPASS/NGを変えない(自動PASSパスなし)。"""
    if irregular_atoms(canon):
        return {"candidate": False, "why": "irregular_reading_atom_in_canon"}
    cn = unicodedata.normalize("NFKC", canon)
    cm = javal.normalize_ja(B._mask(cn, [(a.start, a.end) for a in vg.extract_atoms_ja(cn) if a.kind in ("num", "frac")]))
    for p, s in pairs:
        texts = [t for t in (p, s) if t]
        if any(uj.negation_diff(canon, t, "ja") or sec._scg_negation_marker_diff(canon, t) for t in texts):
            continue
        ok = [t for t in texts if vg.value_guard(canon, t, "ja").kind == vg.EQUAL]
        if not ok:
            continue
        tn = unicodedata.normalize("NFKC", ok[0])
        tm = javal.normalize_ja(B._mask(tn, [(a.start, a.end) for a in vg.extract_atoms_ja(tn) if a.kind in ("num", "frac")]))
        cp, tp = P.pron_hira(cm), P.pron_hira(tm)
        blocks = [o for o in difflib.SequenceMatcher(None, cp, tp, autojunk=False).get_opcodes() if o[0] != "equal"]
        if len(blocks) <= 1 and all((o[2] - o[1]) <= 3 and (o[4] - o[3]) <= 3 for o in blocks):
            return {"candidate": True, "evidence": {"engine_text": ok[0], "canon_pron": cp, "asr_pron": tp, "diff": [(cp[o[1]:o[2]], tp[o[3]:o[4]]) for o in blocks]}}
    return {"candidate": False, "why": "no_pair_meets_value_and_single_span_conditions"}
