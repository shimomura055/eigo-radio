# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03 統合proto v3(research/DEV専用。Productionからimportされない。API 0。LLM 0)。
# proto_unified_02 からの差分 = Opus条件Aレビュー(OPUS_REVIEW_01.md)の反映。規則は PREREGISTERED_03.md(有料draw前に凍結)。
#   M-1: 原稿に不規則読み数詞があれば両側・PRON/VALUE_ONLY両経路でv2不適用(Production判定を返す=L1⊇L0を構造で保証)。
#   M-2: 新層の救済は専用warning codeを必ず持ち(NEW_WARN)、APPROVED_EQUIVALENCE_BASES に登録しない。最終区分 PASS / PASS_W_PROD / PASS_W_NEW。
#        Productionの`_numeric_value_equivalence`が受理しないVALUE_ONLY救済(v2由来)にも警告を付ける。
#   M-3: ASR再試行は best-of-N でなく「矛盾なし合意」(consensus)。force_secondary・PASS_W必須・N≤3・発火理由ホワイトリスト・Azure再試行なし。
#   M-4: 再試行セグメントではβの Secondary読み食い違い=veto。 M-5: 『超→こえ』は汎用辞書を触らず新層内の別表(送り仮名省略形の訓読み、残差0文字、PASS_W_NEW)。
#   M-6: E3(candidate_e_rejections)/E4(candidate_e_cascade_diffs)が非空なら全新層を不適用。 M-7: βは phrase_list_hash が空であることを確認、無ければfail-closed。
#   R-1: C2逆方向を差分span内の漢字1字ごとに検査。 R-2: v2のENGINE_reading_difference経路を除外。 R-7: 全draw・規則版・層版を保存、保存drawのみから再現。
# Flags()全OFFはL0同一(Production adapterを呼ぶだけ)。Production関数は呼ぶだけで編集しない。判定の間だけ in-process 差替し、finallyで必ず元へ戻す。
from __future__ import annotations
import hashlib, itertools, re, sys, unicodedata
from dataclasses import dataclass

sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01"); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02")
import eval_common_02 as E     # javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False(LLM 0)・socket guard・dummy wav
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er008_asr_variant_hardening_15_ja_kanji_readings as kr
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import proto_reading_compare_02 as P
import b_light_proto_02 as B
import proto_unified_02 as U2

PASSING = uj.PASSING_STATES
ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")
RETRY_WHITELIST = ("p1_value_diff", "secondary_not_accepted")          # M-3(e)
_ORIG = sec._numeric_value_equivalence
LAYER_VERSION = "proto_unified_03"
RULE_VERSION = "consensus_v1(PREREGISTERED_03)"
SCOPE_ALLOWED = B.SCOPE_ALLOWED

# M-2: 新層専用warning code。どれも APPROVED_EQUIVALENCE_BASES(最終ANDゲートを素通りする根拠)に入れない。
NEW_WARN = {
    "L1_PRON": "JA_NEWLAYER_PRON_EQUIVALENT",
    "L1_VALUE": "JA_NEWLAYER_VALUE_ONLY_BEYOND_PROD",
    "L2": "JA_NEWLAYER_BETA_COMPOSITE",
    "L3": "JA_NEWLAYER_KUNYOMI_OKURIGANA",
    "RETRY": "JA_NEWLAYER_ASR_CONSENSUS_RETRY",
}
assert not (set(NEW_WARN.values()) & set(uj.APPROVED_EQUIVALENCE_BASES))

# M-5: 送り仮名省略形の訓読み別表(新層内のみ参照。汎用辞書は不変)。「<数量>超」の『超』を ASR が 超え/越え/こえ と書く型。活用語尾が続くものは対象外。
KUNYOMI_OKURIGANA = {"超": ("超え", "越え", "こえ")}
_KOE_RE = re.compile(r"^(超え|越え|こえ)(?![るたてなばずよ])")


@dataclass(frozen=True)
class Flags:
    l1: bool = False
    l2: bool = False
    l3: bool = False
    r1: bool = True          # R-1(差分span内の漢字1字ごとのC2逆方向検査)。ablation用に切替可

    def name(self) -> str:
        n = "+".join(x for x, f in (("L1", self.l1), ("L2", self.l2), ("L3", self.l3)) if f) or "L0"
        return n if self.r1 or not self.l1 else n + "(R1off)"


FINAL = Flags(True, True, True)


def irregular_atoms(canon: str) -> list:
    return U2.irregular_atoms(canon)


def _kanji(ch: str) -> bool:
    return "一" <= ch <= "鿿"


def r1_block(canon: str, asr: str):
    """R-1: ASR側の差分span内の漢字1字ごとに読み候補を引き、2つ以上ある字が1字でもあれば発音救済しない。戻り=理由 or None。"""
    cf, af = sec._ja_value_form(canon), sec._ja_value_form(asr)
    if cf is None or af is None:
        cf, af = canon, asr
    c, a = javal.normalize_ja(cf), javal.normalize_ja(af)
    for c_span, a_span in P._diff_spans(c, a):
        for ch in a_span:
            if not _kanji(ch):
                continue
            try:
                cands = kr.reading_candidates_for_span(ch)
            except Exception:
                continue
            if cands and len(set(cands)) >= 2:
                return f"r1_char_multi_reading:{ch}({c_span}->{a_span})"
    return None


def e34_state(canon: str, prim: str | None) -> tuple:
    """M-6: Primary分類のE3(rejections)/E4(cascade_diffs)の読取専用取得(Production adapterと同一手順)。"""
    if not prim:
        return [], []
    cls = javal.classify_ja_asr_match(canon, prim, expected_readings=None)
    cls = sec._apply_variant_layer_voicing_upgrade(canon, prim, cls)
    return (list(getattr(getattr(cls, "protected", None), "candidate_e_rejections", None) or []),
            list(getattr(getattr(cls, "protected", None), "candidate_e_cascade_diffs", None) or []))


def make_layer(flags: Flags, audit: list):
    """Production _numeric_value_equivalence 位置の差替関数(L1有効時のみ)。"""
    def layer(canon, asr, cls):
        side = "secondary" if sys._getframe(1).f_code.co_name == "_secondary_accept" else "primary"
        irr = irregular_atoms(canon)
        if irr:                                           # M-1: side・kindに関わらずProduction判定へ戻す
            audit.append({"layer": "M1_irregular_guard", "side": side, "atoms": irr})
            return _ORIG(canon, asr, cls)
        r = P.pron_value_equivalence(canon, asr, cls=cls, expected_readings=None, side=side)
        if not r.equal:
            return _ORIG(canon, asr, cls)                 # フォールバック=Production層(L1 ⊇ L0)
        if r.kind == "PRON":
            if r.cause == "ENGINE_reading_difference":    # R-2: 助詞も値も要らない読み一致=エンジン差。Production化の範囲外
                audit.append({"layer": "R2_engine_reading_excluded", "side": side})
                return _ORIG(canon, asr, cls)
            if flags.r1:
                blk = r1_block(canon, asr)
                if blk:
                    audit.append({"layer": "R1_blocked", "side": side, "why": blk})
                    return _ORIG(canon, asr, cls)
            audit.append({"layer": "L1_v2_pron", "side": side, "cause": r.cause})
            return P.to_classification(r, cls)
        o = _ORIG(canon, asr, cls)                        # VALUE_ONLY: Production既存の値等価層が受理するなら同一(新層の寄与なし)
        if getattr(o, "should_pass", False):
            return o
        audit.append({"layer": "L1_v2_value_only", "side": side, "cause": r.cause})   # M-2: 受理範囲を超える救済 → 警告対象
        return P.to_classification(r, cls)
    return layer


def _adapter(canon, prim, sec_text, wav, flags: Flags, audit: list):
    orig_az = sec._azure_stt_strict
    if sec_text is not None:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (sec_text, None)
    else:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary")
    sec._numeric_value_equivalence = make_layer(flags, audit) if flags.l1 else _ORIG
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, wav, cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig_az
        sec._numeric_value_equivalence = _ORIG
    return r


# ---------------- M-5: L3 別表 ----------------
def _num_atoms(text: str) -> list:
    return [a for a in vg.extract_atoms_ja(text) if a.kind == "num"]


def l3_rewrite_one(canon: str, text: str):
    """1転写へ別表を適用。戻り=(置換後text, [置換記録]) 置換が起きなければ (text, [])。位置ずれ/atom列不一致はfail-closed (text, None)。"""
    cn = unicodedata.normalize("NFKC", canon or "")
    if len(unicodedata.normalize("NFKC", text)) != len(text):
        return text, None
    if vg.value_guard(canon, text, "ja").kind != vg.EQUAL:
        return text, None
    c_atoms, t_atoms = _num_atoms(cn), _num_atoms(text)
    if len(c_atoms) != len(t_atoms) or [(a.value, a.unit) for a in c_atoms] != [(a.value, a.unit) for a in t_atoms]:
        return text, None
    out, shift, fired = text, 0, []
    for ca, ta in zip(c_atoms, t_atoms):
        key = cn[ca.end:ca.end + 1]
        if key not in KUNYOMI_OKURIGANA:
            continue
        m = _KOE_RE.match(text[ta.end:])
        if not m or m.group(1) not in KUNYOMI_OKURIGANA[key]:
            continue
        if sec._scg_heterophone_candidate({"canonical": key, "asr": m.group(1)}):   # C2候補spanは除外
            return text, None
        s = ta.end + shift
        out = out[:s] + key + out[s + len(m.group(1)):]
        shift += len(key) - len(m.group(1))
        fired.append(f"{ca.surface}{key}<-{m.group(1)}")
    return out, fired


def l3_judge(canon: str, prim: str | None, sec_text: str | None):
    """両engine転写が揃い、各々を別表で置換した後に原稿と残差0文字(値形式+normalize_ja一致)、かつ置換が少なくとも片方で起きた場合だけ発火。"""
    if not prim or not sec_text:
        return None
    if irregular_atoms(canon):
        return None
    texts, fired_all = [], []
    for t in (prim, sec_text):
        if uj.negation_diff(canon, t, "ja") or sec._scg_negation_marker_diff(canon, t):
            return None
        t2, fired = l3_rewrite_one(canon, t)
        if fired is None:
            return None
        cf, tf = sec._ja_value_form(canon), sec._ja_value_form(t2)
        if cf is None or tf is None or javal.normalize_ja(cf) != javal.normalize_ja(tf):      # 置換後の残差が0文字でなければ不発
            return None
        texts.append(t2); fired_all.append(fired)
    if not any(fired_all):
        return None
    return {"layer": "L3_kunyomi_okurigana", "rewrites": {"primary": fired_all[0], "secondary": fired_all[1]}}


# ---------------- β wrapper(M-4/M-7) ----------------
def beta_guarded(canon, prim, sec_text, wav_sha, phrase_list_hash, retry_mode: bool, r1: bool = True):
    if phrase_list_hash is None or phrase_list_hash != "":       # M-7: 原稿テキストをAzureへ渡していないことを確認できなければfail-closed
        return B.BResult(False, "phrase_list_hash_not_empty_or_unknown", "M7_witness_independence")
    b = B.composite_judge(canon, prim, sec_text, {"engine": "azure", "wav_sha256": wav_sha, "model_id": "azure-speech-stt", "phrase_list_hash": phrase_list_hash},
                          secondary_reading_conflict=("veto" if retry_mode else "warn"))
    if b.equal and r1 and P.W_PRON in b.warnings:                # R-1をβの発音同一経路にも適用(βは凍結ファイルのため結果に対する事後検査)
        blk = r1_block(canon, prim)
        if blk:
            return B.BResult(False, "beta_" + blk, "R1_blocked_in_beta")
    return b


def judge(canon: str, prim: str | None, sec_text: str | None, wav: str, flags: Flags = Flags(), *, retry_mode: bool = False,
          phrase_list_hash: str | None = "") -> dict:
    """1対(Primary転写, Secondary転写)の最終Gate判定。cat = PASS / PASS_W_PROD / PASS_W_NEW / NG。
    戻り: cat/state/reason/route/layers(監査)/warning_labels(新層)/sec_called/needs_new_azure_call/blocked(M-6)。"""
    rej, casc = e34_state(canon, prim) if (flags.l1 or flags.l2 or flags.l3) else ([], [])
    blocked = bool(rej or casc)
    eff = Flags(r1=flags.r1) if blocked else flags             # M-6: E3/E4があれば全新層を不適用(L0結果)
    audit: list = []
    if blocked:
        audit.append({"layer": "M6_new_layers_disabled", "e3_rejections": len(rej), "e4_cascade_diffs": len(casc)})
    r = _adapter(canon, prim, sec_text, wav, eff, audit)
    j = r["asr_judgement"]
    st, rc = j.get("state"), j.get("reason_code")
    sec_called = bool((j.get("secondary") or {}).get("called"))
    fired = [a for a in audit if a.get("layer") in ("L1_v2_pron", "L1_v2_value_only")]
    base = {"state": st, "reason": rc, "sec_called": sec_called, "layers": audit, "blocked": blocked, "needs_new_azure_call": False}
    if st in PASSING:
        labels = [NEW_WARN["L1_PRON"] if a["layer"] == "L1_v2_pron" else NEW_WARN["L1_VALUE"] for a in fired]
        prod_w = list(j.get("warnings") or [])
        assert not (set(labels) & set(prod_w))
        if fired:
            return dict(base, cat="PASS_W_NEW", route="|".join(sorted({a["layer"] + ":" + a.get("side", "") + ":" + str(a.get("cause", "")) for a in fired})),
                        warning_labels=sorted(set(labels)), prod_warnings=prod_w)
        if st == "PASS_WITH_WARNING":
            return dict(base, cat="PASS_W_PROD", route="prod_warning:" + ",".join(prod_w), warning_labels=[], prod_warnings=prod_w)
        return dict(base, cat="PASS", route="prod:" + str(rc), warning_labels=[], prod_warnings=prod_w)
    out = dict(base, cat="NG", route=str(rc), warning_labels=[], prod_warnings=[])
    if eff.l3 and sec_text and prim and any(str(rc).startswith(e) for e in ELIG):
        a = l3_judge(canon, prim, sec_text)
        if a:
            return dict(out, cat="PASS_W_NEW", state="PASS_WITH_WARNING", reason="l3_kunyomi_okurigana", route="L3_kunyomi_okurigana", layers=audit + [a],
                        warning_labels=[NEW_WARN["L3"]], needs_new_azure_call=(not sec_called))
    if eff.l2 and sec_text and any(str(rc).startswith(e) for e in ELIG):
        sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
        b = beta_guarded(canon, prim, sec_text, sha, phrase_list_hash, retry_mode, eff.r1)
        if b.equal:
            return dict(out, cat="PASS_W_NEW", state="PASS_WITH_WARNING", reason="composite", route="L2_beta_composite" + (":listen" if b.listen_required else ""),
                        layers=audit + [{"layer": "L2_beta", "listen": b.listen_required, "reasons": list(b.listen_reasons)}],
                        warning_labels=[NEW_WARN["L2"]], needs_new_azure_call=(not sec_called))
        out["beta_blocked_by"] = b.blocked_by
    return out


# ---------------- M-3: 矛盾なし合意(consensus) ----------------
def contradicts(canon: str, draw: str, flags: Flags = FINAL) -> tuple:
    """NGdrawの矛盾判定。戻り=(矛盾か, 理由)。矛盾=否定差/値以外の内容span食い違い/対応する数字runの欠落/解釈できる別の値(説明不能)。
    例外=explain_garbleで説明できる数値garble、M-1/C2/R-1を通る発音同一。"""
    if uj.negation_diff(canon, draw, "ja") or sec._scg_negation_marker_diff(canon, draw):
        return True, "negation"
    Cn, Dn = unicodedata.normalize("NFKC", canon), unicodedata.normalize("NFKC", draw)
    c_all = vg.extract_atoms_ja(Cn)
    c_atoms = [a for a in c_all if a.kind in ("num", "frac")]
    spans_c, spans_d = [], []
    if c_atoms and not any(a.kind == "amb" for a in c_all):
        st, _ = B.analyze_primary_values(Cn, Dn, True)
        if any(s.detail.startswith("unsupported_atom") for s in st):
            st = None
        else:
            for s in st:
                if s.status == "MISSING":
                    return True, "value_missing:" + s.surface
                if s.status == "CONTRADICTION":
                    return True, f"value_diff:{s.surface}<-{s.primary_run}"
            spans_c, spans_d = [(a.start, a.end) for a in c_atoms], [s.span for s in st]
    cm, dm = (B._mask(Cn, spans_c), B._mask(Dn, spans_d)) if spans_c else (Cn, Dn)
    c, d = javal.normalize_ja(cm), javal.normalize_ja(dm)
    if c == d:
        return False, "same_after_mask"
    if P.pron_hira(c) != P.pron_hira(d):
        return True, "content_span_differs"
    if irregular_atoms(canon):
        return True, "pron_same_but_irregular_reading_atom"
    cls = javal.classify_ja_asr_match(canon, draw, expected_readings=None, allow_reading_resolver=False)
    blk = P.c2_blocked(cls, c, d)
    if blk:
        return True, "pron_same_but_c2:" + blk
    if flags.r1:
        blk = r1_block(canon, draw)
        if blk:
            return True, "pron_same_but_" + blk
    return False, "pron_same_homophone"


def retry_eligible(canon: str, d1: str, r1: dict, sec_text: str | None) -> tuple:
    """M-3(e)+(a): d1がNGのとき再試行を発火してよいか。ホワイトリスト理由かつ否定差・A7・length以外、かつ保存Secondaryあり(force_secondary)。"""
    if r1.get("blocked"):
        return False, "m6_e3_e4_block"
    if not sec_text:
        return False, "no_stored_secondary(force_secondary不可)"
    rc = str(r1.get("reason"))
    if not any(rc.startswith(w) for w in RETRY_WHITELIST):
        return False, "reason_not_whitelisted:" + rc
    if uj.negation_diff(canon, d1, "ja") or sec._scg_negation_marker_diff(canon, d1):
        return False, "negation"
    cls = javal.classify_ja_asr_match(canon, d1, expected_readings=None, allow_reading_resolver=False)
    if sec._scg_reading_dict_reason(cls):
        return False, "A7_reading_dictionary"
    lc, ld = len(javal.normalize_ja(canon)), len(javal.normalize_ja(d1))
    if lc == 0 or not (0.8 <= ld / lc <= 1.25):
        return False, "length"
    return True, "eligible"


def consensus(canon: str, draws: list, sec_text: str | None, wav: str, flags: Flags = FINAL, first: int = 0, extras: tuple = (), n_max: int = 3,
              phrase_list_hash: str | None = "") -> dict:
    """draws=OpenAI転写(同一wavのdraw集合)。first=最初に採るdrawの添字、extras=再試行で追加するdrawの添字(最大n_max-1本)。Azureは保存転写固定(再試行しない)。
    戻り: cat(PASS/PASS_W_PROD/PASS_W_NEW/HR/NG)・retry_fired・extra_openai_draws・全draw判定・矛盾判定・規則版/層版(R-7: 再現用)。"""
    assert len(extras) <= n_max - 1 and first not in extras
    d1 = draws[first]
    r1 = judge(canon, d1, sec_text, wav, flags, phrase_list_hash=phrase_list_hash)
    meta = {"rule_version": RULE_VERSION, "layer_version": LAYER_VERSION, "flags": flags.name(), "n_max": n_max, "canonical": canon, "secondary": sec_text,
            "draws": list(draws), "first": first, "extras": list(extras), "wav": wav}
    if r1["cat"] != "NG":
        return dict(meta, cat=r1["cat"], retry_fired=False, extra_openai_draws=0, reason=r1["reason"], route=r1["route"], warning_labels=r1["warning_labels"], per_draw=[r1])
    if not extras:
        return dict(meta, cat="NG", retry_fired=False, extra_openai_draws=0, reason=r1["reason"], route=r1["route"], warning_labels=[], per_draw=[r1], retry_block="n1")
    ok, why = retry_eligible(canon, d1, r1, sec_text)
    if not ok:
        return dict(meta, cat="NG", retry_fired=False, extra_openai_draws=0, reason=r1["reason"], route=r1["route"], warning_labels=[], per_draw=[r1], retry_block=why)
    idx = [first] + list(extras)
    rs = [judge(canon, draws[i], sec_text, wav, flags, retry_mode=True, phrase_list_hash=phrase_list_hash) for i in idx]
    cons = [(False, "judged_non_ng") if r["cat"] != "NG" else contradicts(canon, draws[i], flags) for i, r in zip(idx, rs)]
    passing = [k for k, r in enumerate(rs) if r["cat"] != "NG"]
    contra = [k for k, c in enumerate(cons) if c[0]]
    base = dict(meta, retry_fired=True, extra_openai_draws=len(extras), per_draw=rs, contradictions=cons, passing_idx=[idx[k] for k in passing], contra_idx=[idx[k] for k in contra])
    if passing and not contra:
        return dict(base, cat="PASS_W_NEW", reason="consensus", route="consensus_retry", warning_labels=[NEW_WARN["RETRY"]] + sorted({w for k in passing for w in rs[k]["warning_labels"]}))
    if passing and contra:
        return dict(base, cat="HR", reason="mixed_evidence_content_contradiction", route="early_hr", warning_labels=[])
    return dict(base, cat="NG", reason=r1["reason"], route=r1["route"], warning_labels=[])


def best_of_n_ref(canon: str, draws: list, sec_text, wav, flags: Flags = FINAL, first: int = 0, extras: tuple = ()) -> str:
    """参考(Phase 2の規則): d1がNGなら追加drawの中に非NGが1本でもあれば合格(矛盾無視)。"""
    for i in [first] + list(extras):
        r = judge(canon, draws[i], sec_text, wav, flags)
        if r["cat"] != "NG":
            return r["cat"] if i == first else "PASS_W_NEW"
    return "NG"


def combos(k: int, n: int):
    """全(first, extras部分集合)。N=1は first のみ。順序に依存させない(各組合せ等重み)。"""
    for f in range(k):
        rest = [i for i in range(k) if i != f]
        for ex in itertools.combinations(rest, n - 1):
            yield f, ex


def rejudge_from_audit(entry: dict, phrase_list_hash: str | None = "") -> dict:
    """R-7: 保存したdraw集合・Secondary・規則/層版だけから再現(API 0)。版が異なれば fail-closed。"""
    if entry.get("rule_version") != RULE_VERSION or entry.get("layer_version") != LAYER_VERSION:
        return {"cat": "NG", "reason": "version_mismatch_fail_closed", "retry_fired": False}
    f = entry["flags"]
    flags = Flags(True, True, True, r1=("R1off" not in f)) if f.startswith("L1+L2+L3") else Flags()
    return consensus(entry["canonical"], entry["draws"], entry["secondary"], entry["wav"], flags, entry["first"], tuple(entry["extras"]), entry["n_max"], phrase_list_hash)


def consensus_reuse_decision(entry: dict, flag_on: bool, scope: str | None) -> dict:
    """R-7: Store再利用。flag OFF・scope外を先にblock(B.composite_reuse_decision と同形)、scope内は保存drawで再現し、結果が違えばblock。"""
    if "rule_version" not in entry:
        return {"blocked": False, "reason": "NOT_CONSENSUS_ENTRY"}
    if (not flag_on) or scope not in SCOPE_ALLOWED:
        return {"blocked": True, "reason": "CONSENSUS_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF"}
    for k in ("draws", "secondary", "canonical", "wav", "first", "extras", "n_max", "flags"):
        if entry.get(k) in (None, ""):
            return {"blocked": True, "reason": "CONSENSUS_PROVENANCE_MISSING:" + k}
    r = rejudge_from_audit(entry)
    return {"blocked": r["cat"] != entry.get("cat"), "reason": "CONSENSUS_REJUDGE_" + ("SAME" if r["cat"] == entry.get("cat") else "DIFF:" + r["cat"])}
