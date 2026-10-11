# OPEN-258 Phase 0 Trial専用(Production未変更)。判定は既存classify_ja_asr_matchを
# Resolver LLM=OFFで呼ぶだけ(課金なし)。追加除外(助詞/日付)は設計書上Phase1候補の新規小ルールで、
# ここでは集計用の「追加ルール」として別列に判定するのみ。
import sys, os, re, json, glob, wave, hashlib
sys.path.insert(0, os.getcwd())
import er007_ja_asr_validator_01 as javal
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False  # LLM課金を避ける(Trial専用)

OUT = "er053_output/open258_phase0_trial_01"
EVID = "er053_output/family_x_tts_asr_rootcause_01/OPEN258_OFFLINE_EVIDENCE_01.json"
USD_PER_HOUR = 1.0
JPY_PER_USD = 160.0
JPY_PER_SEC = USD_PER_HOUR / 3600.0 * JPY_PER_USD
BUDGET_JPY = 5.0

PARTICLES = set("がをにへともはでのやかだ")  # 設計書の例(証拠だと->証拠がと)に合わせ「だ」を含める
KANJI_NUM_RE = re.compile(r"[一二三四五六七八九十百千万〇]|[年月日]")


def dur(path):
    w = wave.open(path)
    return w.getnframes() / w.getframerate()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def diff_ops(c_norm, a_norm):
    import difflib
    sm = difflib.SequenceMatcher(None, c_norm, a_norm, autojunk=False)
    return [(t, c_norm[i1:i2], a_norm[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]


def extra_exclusion(c_norm, a_norm):
    """設計書4節の追加除外(新規小ルール案)。該当理由を返す(なければNone)。"""
    ops = diff_ops(c_norm, a_norm)
    reasons = []
    for t, c, a in ops:
        if t == "replace" and len(c) == 1 and len(a) == 1 and c in PARTICLES and a in PARTICLES:
            reasons.append(f"particle_diff:{c}->{a}")
        if KANJI_NUM_RE.search(c) or KANJI_NUM_RE.search(a):
            reasons.append(f"date_or_kanji_numeral_diff:{c}->{a}")
    return reasons or None


def exclusion_check(canonical, primary):
    """既存ルールによる除外判定+追加ルール判定。"""
    cls = javal.classify_ja_asr_match(canonical, primary)
    c_norm = javal.normalize_ja(canonical); a_norm = javal.normalize_ja(primary or "")
    out = {"primary_cls": cls.classification, "ratio": round(cls.similarity_ratio, 3)}
    existing = []
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        existing.append(f"not_TCM_now:{cls.classification}")
    if cls.protected.number_mismatches:
        existing.append(f"number_mismatch:{cls.protected.number_mismatches}")
    if cls.protected.negation_mismatches:
        existing.append(f"negation_mismatch:{cls.protected.negation_mismatches}")
    if cls.similarity_ratio < 0.4:
        existing.append("ratio<0.4")
    if "次の文章" in (primary or "") or "読み上げてください" in (primary or "") or "The message below" in (primary or ""):
        existing.append("instruction_echo")
    out["existing_exclusions"] = existing
    out["extra_exclusions"] = extra_exclusion(c_norm, a_norm)
    out["diff_ops"] = diff_ops(c_norm, a_norm)
    return out


def secondary_judge(canonical, sec_text):
    cls = javal.classify_ja_asr_match(canonical, sec_text)
    pass_ok = cls.classification in ("EXACT_MATCH", "NORMALIZED_MATCH")
    basis = {"EXACT_MATCH": "strip後の完全一致", "NORMALIZED_MATCH": "normalize_ja(NFKC・句読点除去等)後に一致"}.get(
        cls.classification, f"不一致({cls.classification}): " + cls.reason[:120])
    return {"sec_cls": cls.classification, "sec_pass": pass_ok, "basis": basis,
            "sec_diff_ops": diff_ops(javal.normalize_ja(canonical), javal.normalize_ja(sec_text or ""))}
