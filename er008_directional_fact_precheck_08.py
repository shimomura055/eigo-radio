# ============================================================
# er008_directional_fact_precheck_08.py
# ER-008-DIRECTIONAL-FACT-PRECHECK-08:
# 比較方向(more/fewer, at least/at most, increase/decrease等)の
# 反転によるFact逆転を、Production完成前に軽量・決定的(rule-based)に
# 検知する暫定チェック。
# ============================================================
# 位置付け(OPEN-72との違い):
#   OPEN-72が指摘した「script対Source Factの比較方向を機械的に検知する
#   汎用Validator」の本格実装(構造化comparator、任意の自然文への一般化、
#   quantifier protection等)は今回行わない。あくまで
#     (1) 今回発見した具体的な反転パターン(more/fewer等)に絞った
#     (2) 新規LLM callを増やさない、rule-based中心の
#     (3) 実ユーザー検証対象(当面No.7のみ)向けの
#   暫定対策(interim directional fact precheck)である。既存22テーマへの
#   横断監査・VFL/Fact Ledger構造の改修は今回のスコープ外(Part A/J)。
#
# 重要な設計原則(Part D): 同じLLMに「もう一度Fact Checkさせる」だけには
# しない。今回のB1 Point Two誤りは「VFLで逆転→Writerがその逆転を採用→
# Fact Checkも同じ方向で誤認」という連鎖で発生した(ER-008-B1-POINT2-
# FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07で判明)。同じ誤りを繰り返す
# LLM検証に依存せず、最終的なdirection token比較は正規表現による
# 機械的な一致判定で行う(LLMは使わない、追加API callゼロ)。
#
# 2軸設計: 個別の12カテゴリ(more/fewer, higher/lower...)をそれぞれ
# 独立対比するのではなく、「同じ意味の方向」を束ねた2つの軸で判定する。
#   - magnitude軸(high/low): 量・程度が「大きい方向」か「小さい方向」か
#     (more/fewer, higher/lower, increase/decrease, rise/fall, up/down,
#      at least/at most, above/below, more than/less than, doubled/
#      halved, growth/declineは全てこの1軸に統合)
#   - temporal軸(earlier/later): 時間的な前後関係
#     (before/earlier, after/later)
# こうすることで、「increase」(Ledger側)と「rise」(script側)のような
# 正しい同義表現(Part H項目7)を、カテゴリの違いを理由に誤って
# 「比較不能」とせず、同じmagnitude軸のhighとして正しくMATCH判定できる。
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

VALID_VERDICTS = (
    "MATCH", "POTENTIAL_DIRECTION_REVERSAL", "DIRECTION_REVIEW_REQUIRED", "NOT_APPLICABLE",
)

# ------------------------------------------------------------
# Direction term辞書(Part B必須12カテゴリを2軸へ統合)。
# 各エントリ: (正規表現パターン, confidence, category)。
#   confidence="high"は曖昧性が低く単独でFAILへ寄与してよい表現
#     (2語以上のphraseや、他の意味を持ちにくい語)、confidence="low"は
#     単独語で他の用法もあり得る表現(bare "up"/"down"等、Part F
#     「表現が婉曲でdirectionを機械判定しづらい」に該当)。low
#     confidenceの衝突はWARN止まりとし、即FAILにはしない。
#   category="trend"は「同じ名前の量(シェア・割合等)が時間とともに
#     増えたか減ったか」を表す語(increase/decrease、rise/fall等)。
#     Ledger/VFL/scriptのどれも同じ量(例:「その割合」)を指している
#     ため、対象がすり替わるリスクが低く、cross-artifact比較でも
#     安全にFAILへ使える。
#   category="threshold"は「ある基準値に対して以上か以下か」を表す語
#     (at least/at most、more than/less than、above/below等)。
#     ER-008-DIRECTIONAL-FACT-PRECHECK-08で実データ検証した結果、
#     この種の語は「比率」と「その逆数に近い量(例:従業員1人あたりの
#     デスク数)」のように、対象(主語)が実は逆数関係にある場合に、
#     同じ語("以下"等)が両側に現れても実際には逆方向を意味する
#     ケースがあることが判明した(VFL F-008: claim欄は「比率が1.0
#     以下」、conditions欄は「デスク数が1台以下」で、いずれも表記上は
#     「以下」だが対象が逆数関係にあるため実際には逆方向)。この
#     ため、thresholdカテゴリの衝突は、Fact Ledger/VFLとscriptを
#     自動対応付けするcross-artifact比較(audit_article_directional_
#     facts()のLayer 1/2)では、対象一致が保証できないとしてFAILへ
#     格上げしない(DIRECTION_REVIEW_REQUIRED止まり)。ただし
#     compare_direction()単体(対象が明確な2文を直接比較する用途、
#     Part G/HのFixtureが要求する動作)では、そのままFAILへ使う。
# ------------------------------------------------------------
_MAGNITUDE_HIGH = [
    (r"\bat least\b", "high", "threshold"), (r"\bor more\b", "high", "threshold"),
    (r"\bmore than\b", "high", "threshold"), (r"\bgreater than\b", "high", "threshold"),
    (r"\bhigher\b", "high", "threshold"), (r"\bincrease[sd]?\b", "high", "trend"),
    (r"\bincreasing\b", "high", "trend"), (r"\brose\b", "high", "trend"),
    (r"\brising\b", "high", "trend"), (r"\brises?\b", "high", "trend"),
    (r"\babove\b", "high", "threshold"), (r"\bover\b", "low", "threshold"),
    (r"\bdoubled\b", "high", "threshold"), (r"\bgrowth\b", "high", "trend"),
    (r"\bgrowing\b", "high", "trend"), (r"\bexpand(?:ed|ing|s)?\b", "high", "trend"),
    (r"\bmore\b", "high", "threshold"), (r"\bup\b", "low", "trend"),
    (r"以上", "high", "threshold"), (r"より多い", "high", "threshold"),
    (r"より高い", "high", "threshold"), (r"多い", "low", "threshold"),
    (r"多く", "low", "threshold"), (r"高い", "low", "threshold"), (r"高く", "low", "threshold"),
    (r"増加", "high", "trend"), (r"増える", "high", "trend"), (r"増えた", "high", "trend"),
    (r"上昇", "high", "trend"), (r"上がる", "high", "trend"), (r"上がった", "high", "trend"),
    (r"拡大", "high", "trend"), (r"倍増", "high", "threshold"), (r"を上回る", "high", "threshold"),
    (r"超(?:え|る|えた)", "high", "threshold"),
]
_MAGNITUDE_LOW = [
    (r"\bat most\b", "high", "threshold"), (r"\bor fewer\b", "high", "threshold"),
    (r"\bor less\b", "high", "threshold"), (r"\bless than\b", "high", "threshold"),
    (r"\bfewer than\b", "high", "threshold"), (r"\blower\b", "high", "threshold"),
    (r"\bdecrease[sd]?\b", "high", "trend"), (r"\bdecreasing\b", "high", "trend"),
    (r"\bfell\b", "high", "trend"), (r"\bfalling\b", "high", "trend"),
    (r"\bfalls?\b", "high", "trend"), (r"\bbelow\b", "high", "threshold"),
    (r"\bunder\b", "low", "threshold"), (r"\bhalved\b", "high", "threshold"),
    (r"\bdecline[sd]?\b", "high", "trend"), (r"\bdeclining\b", "high", "trend"),
    (r"\bshrink(?:ing|s)?\b", "high", "trend"), (r"\bfewer\b", "high", "threshold"),
    (r"\bdown\b", "low", "trend"),
    (r"以下", "high", "threshold"), (r"より少ない", "high", "threshold"),
    (r"より低い", "high", "threshold"), (r"少ない", "low", "threshold"),
    (r"少なく", "low", "threshold"), (r"低い", "low", "threshold"), (r"低く", "low", "threshold"),
    (r"減少", "high", "trend"), (r"減る", "high", "trend"), (r"減った", "high", "trend"),
    (r"下落", "high", "trend"), (r"下がる", "high", "trend"), (r"下がった", "high", "trend"),
    (r"低下", "high", "trend"), (r"縮小", "high", "trend"), (r"半減", "high", "threshold"),
    (r"を下回る", "high", "threshold"), (r"未満", "high", "threshold"),
]
_TEMPORAL_EARLIER = [
    (r"\bbefore\b", "high", "temporal"), (r"\bearlier\b", "high", "temporal"),
    (r"\bprior to\b", "high", "temporal"), (r"以前", "high", "temporal"),
    (r"より早く", "high", "temporal"),
]
_TEMPORAL_LATER = [
    (r"\bafter\b", "high", "temporal"), (r"\blater\b", "high", "temporal"),
    (r"\bfollowing\b", "low", "temporal"), (r"以後", "high", "temporal"),
    (r"より遅く", "high", "temporal"),
]

_TERM_TABLE = {
    ("magnitude", "high"): _MAGNITUDE_HIGH,
    ("magnitude", "low"): _MAGNITUDE_LOW,
    ("temporal", "earlier"): _TEMPORAL_EARLIER,
    ("temporal", "later"): _TEMPORAL_LATER,
}
_OPPOSITE_BUCKET = {
    ("magnitude", "high"): "low", ("magnitude", "low"): "high",
    ("temporal", "earlier"): "later", ("temporal", "later"): "earlier",
}

_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?%?")


@dataclass
class DirectionSignal:
    axis: str
    bucket: str
    term: str
    confidence: str
    category: str


def extract_direction_signals(text: str) -> list[DirectionSignal]:
    """テキストから方向を持つ表現を抽出する(rule-based、個別カテゴリ
    ごとにマッチさせることで、どの語が実際にヒットしたかを監査可能な
    形で残す)。英字の大文字/小文字は無視する(`.lower()`は日本語文字
    には影響しないため、EN/JA混在テキストでも安全に共通処理できる)。"""
    if not text:
        return []
    signals: list[DirectionSignal] = []
    lowered = text.lower()
    for (axis, bucket), patterns in _TERM_TABLE.items():
        for pattern, confidence, category in patterns:
            for m in re.finditer(pattern, lowered):
                signals.append(DirectionSignal(axis=axis, bucket=bucket, term=m.group(0),
                                                 confidence=confidence, category=category))
    return signals


def compare_direction(reference_text: str, candidate_text: str) -> dict:
    """referenceとcandidateの方向表現を比較する。Part C/E/Fの判定区分:
      MATCH: 両者に方向表現があり、共有する軸で衝突がない
      POTENTIAL_DIRECTION_REVERSAL: high confidence表現同士が逆bucket
      DIRECTION_REVIEW_REQUIRED: low confidence表現の衝突、または
        片方にのみ方向表現がある(比較できない=人間確認が必要)
      NOT_APPLICABLE: 両者とも方向表現が見つからない
    """
    ref_signals = extract_direction_signals(reference_text)
    cand_signals = extract_direction_signals(candidate_text)

    if not ref_signals and not cand_signals:
        return {"verdict": "NOT_APPLICABLE", "reference_signals": [], "candidate_signals": [],
                "conflicts": [], "reason": "両テキストとも方向表現が見つからない"}

    if bool(ref_signals) != bool(cand_signals):
        return {
            "verdict": "DIRECTION_REVIEW_REQUIRED",
            "reference_signals": [s.__dict__ for s in ref_signals],
            "candidate_signals": [s.__dict__ for s in cand_signals],
            "conflicts": [],
            "reason": "片方にのみ方向表現があり、機械的に一致/不一致を判定できない",
        }

    high_conflicts = []
    low_conflicts = []
    shared_axis_found = False
    for axis in ("magnitude", "temporal"):
        ref_axis_signals = [s for s in ref_signals if s.axis == axis]
        cand_axis_signals = [s for s in cand_signals if s.axis == axis]
        if not ref_axis_signals or not cand_axis_signals:
            continue
        shared_axis_found = True
        # trend/threshold(temporalは単一category)を独立に評価する。同じ
        # bucket内にtrendとthresholdが混在する場合、trend側は一致して
        # いてもthreshold側だけが逆、というケースを区別できないと、
        # 逆に「trendも一致していない」という誤った衝突報告になる
        # (実データ検証で判明: "at least"[threshold,high]と"fell"
        # [trend,low]が両方low bucketの"以下"/"低下"と比較される際、
        # trendは一致[fell/低下とも declining]なのにthresholdだけが
        # 逆[at least vs 以下]という構造をcategory別に見ないと分離
        # できない)。
        categories_present = {s.category for s in ref_axis_signals} | {s.category for s in cand_axis_signals}
        for category in categories_present:
            ref_cat_signals = [s for s in ref_axis_signals if s.category == category]
            cand_cat_signals = [s for s in cand_axis_signals if s.category == category]
            if not ref_cat_signals or not cand_cat_signals:
                continue
            ref_buckets = {s.bucket for s in ref_cat_signals}
            cand_buckets = {s.bucket for s in cand_cat_signals}
            for rb in ref_buckets:
                opp = _OPPOSITE_BUCKET[(axis, rb)]
                if opp not in cand_buckets:
                    continue
                ref_high_signals = [s for s in ref_cat_signals if s.bucket == rb and s.confidence == "high"]
                cand_high_signals = [s for s in cand_cat_signals if s.bucket == opp and s.confidence == "high"]
                entry = {"axis": axis, "category": category, "reference_bucket": rb,
                         "candidate_bucket": opp, "threshold_only": category == "threshold"}
                if ref_high_signals and cand_high_signals:
                    high_conflicts.append(entry)
                else:
                    low_conflicts.append(entry)

    result_common = {
        "reference_signals": [s.__dict__ for s in ref_signals],
        "candidate_signals": [s.__dict__ for s in cand_signals],
    }
    if high_conflicts:
        return {"verdict": "POTENTIAL_DIRECTION_REVERSAL", "conflicts": high_conflicts,
                "reason": f"高確度の方向表現が逆になっている: {high_conflicts}", **result_common}
    if low_conflicts:
        return {"verdict": "DIRECTION_REVIEW_REQUIRED", "conflicts": low_conflicts,
                "reason": f"曖昧な表現同士で方向が逆に見えるが確度が低い: {low_conflicts}", **result_common}
    if shared_axis_found:
        return {"verdict": "MATCH", "conflicts": [], "reason": "共有する軸で方向の衝突なし", **result_common}
    return {"verdict": "DIRECTION_REVIEW_REQUIRED", "conflicts": [],
            "reason": "両者に方向表現はあるが共有する軸がない(比較不能)", **result_common}


def _downgrade_threshold_only_reversal(result: dict) -> dict:
    """POTENTIAL_DIRECTION_REVERSALのうち、衝突が全てthresholdカテゴリ
    のみ(trend/temporalの衝突を伴わない)場合はDIRECTION_REVIEW_
    REQUIREDへ格下げする。cross-artifact比較(VFLのclaim対conditions、
    Fact Ledger対script)では、比較している2つの表現が実は逆数関係に
    ある異なる主語を指している可能性を機械的に排除できないため
    (実データ検証: VFL F-008の`claim`「比率が1.0以下」と`conditions`
    「デスク数が1台以下」は、いずれも表記上「以下」で一致するが、
    主語[比率とその逆数に近い量]が異なるため実際には逆方向。同じ
    「以下」という表記が両側にあってもMATCH扱いになるだけでなく、
    正しい"at least"と誤った"or fewer"を比較すると実際には正しい方を
    REVERSAL扱いにしてしまう逆転が起きることも確認した)。thresholdの
    衝突のみでは安全にFAILと断定できないため、Human Reviewへ回す。"""
    if result["verdict"] != "POTENTIAL_DIRECTION_REVERSAL":
        return result
    conflicts = result.get("conflicts") or []
    if conflicts and all(c.get("threshold_only") for c in conflicts):
        result = dict(result)
        result["verdict"] = "DIRECTION_REVIEW_REQUIRED"
        result["reason"] = (
            "thresholdカテゴリ(at least/at most等)のみの衝突であり、主語が逆数関係にある"
            "可能性を排除できないためHuman Reviewへ回す(FAILへは格上げしない): "
            f"{conflicts}")
        result["downgraded_from_reversal"] = True
    return result


def audit_vfl_fact_internal_consistency(vfl_fact: dict) -> dict:
    """VFLの1つのFactオブジェクト内で、`claim`欄と`conditions`/
    `numeric_scope`欄の方向表現が矛盾していないか確認する(同一言語
    内の比較のため、cross-languageの問題は回避できるが、主語が逆数
    関係にある場合の限界は_downgrade_threshold_only_reversal()を参照。
    ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07で実際に
    発見した根本原因[VFL F-008の`conditions`欄が`claim`欄と逆方向
    だった]は、trend/temporalカテゴリの衝突であれば直接検知できる
    設計)。"""
    fact_id = vfl_fact.get("fact_id", "?")
    claim = vfl_fact.get("claim") or ""
    conditions = vfl_fact.get("conditions") or ""
    numeric_scope = vfl_fact.get("numeric_scope") or ""
    other = " ".join(x for x in (conditions, numeric_scope) if x)
    result = _downgrade_threshold_only_reversal(compare_direction(claim, other))
    result["fact_id"] = fact_id
    result["layer"] = "vfl_internal_claim_vs_conditions"
    return result


def find_matching_script_sentences(numbers: set[str], script_text: str) -> list[str]:
    """script_text内から、指定した数字集合を(全て)含む文を探す
    (number-anchored Fact alignment、Fact Ledger/VFLとscriptの文を
    言語をまたいで対応付けるための軽量なヒューリスティック)。"""
    if not numbers:
        return []
    sentences = re.split(r"(?<=[.!?])\s+|\n+", script_text)
    matches = []
    for sent in sentences:
        sent_numbers = set(_NUMBER_RE.findall(sent))
        sent_numbers_norm = {n.rstrip("%").replace(",", "") for n in sent_numbers}
        if numbers.issubset(sent_numbers_norm):
            matches.append(sent.strip())
    return matches


def _extract_normalized_numbers(text: str) -> set[str]:
    return {n.rstrip("%").replace(",", "") for n in _NUMBER_RE.findall(text or "")}


def audit_article_directional_facts(article_text: str, ledger_text: str,
                                      vfl_path: str | None = None) -> dict:
    """Production記事1本分の暫定比較方向チェック(Part C/I)。
      Layer 1(vfl_internal): vfl_pathが与えられ、ファイルが存在する
        場合のみ実行。各VFL Factの`claim`と`conditions`/`numeric_scope`
        の内部矛盾を検知する。
      Layer 2(ledger_vs_script): Fact Ledgerのテキスト(`verified_
        ledger_text`、文単位に分割)ごとに、共有する数字を手がかりに
        article_text内の対応する文を探し、方向表現を比較する。
    どちらのLayerも新規LLM callを発生させない(rule-based、regexのみ)。
    overall_status: 1件でもPOTENTIAL_DIRECTION_REVERSALがあればそれ、
    なければ1件でもDIRECTION_REVIEW_REQUIREDがあればそれ、それ以外は
    PASS。"""
    facts_results = []

    if vfl_path and os.path.exists(vfl_path):
        with open(vfl_path, encoding="utf-8") as f:
            vfl_data = json.load(f)
        vfl_facts = (vfl_data.get("parsed") or {}).get("facts") or []
        for vfl_fact in vfl_facts:
            r = audit_vfl_fact_internal_consistency(vfl_fact)
            if r["verdict"] != "NOT_APPLICABLE":
                facts_results.append(r)

    ledger_sentences = [s.strip() for s in re.split(r"(?<=[.!?。])\s+|\n+", ledger_text or "") if s.strip()]
    for ledger_sentence in ledger_sentences:
        numbers = _extract_normalized_numbers(ledger_sentence)
        if not numbers:
            continue
        matched = find_matching_script_sentences(numbers, article_text)
        for script_sentence in matched:
            r = _downgrade_threshold_only_reversal(compare_direction(ledger_sentence, script_sentence))
            if r["verdict"] == "NOT_APPLICABLE":
                continue
            r["layer"] = "ledger_vs_script"
            r["ledger_sentence"] = ledger_sentence
            r["script_sentence"] = script_sentence
            r["shared_numbers"] = sorted(numbers)
            facts_results.append(r)

    verdicts = [r["verdict"] for r in facts_results]
    if "POTENTIAL_DIRECTION_REVERSAL" in verdicts:
        overall = "POTENTIAL_DIRECTION_REVERSAL"
    elif "DIRECTION_REVIEW_REQUIRED" in verdicts:
        overall = "DIRECTION_REVIEW_REQUIRED"
    else:
        overall = "PASS"
    return {"overall_status": overall, "results": facts_results}


class DirectionalFactReversalError(RuntimeError):
    pass


def assert_no_directional_reversal(audit_result: dict) -> None:
    """Part E: POTENTIAL_DIRECTION_REVERSALがあれば明示的にSTOPする
    ためのgate関数。article生成自体は自動でblockしない(Part K:
    「Production完成を頻繁に誤ブロックする」ことをSTOP条件として
    警戒しているため)。episodeを`USER LISTENING READY`と宣言する
    完成判定の直前で、この関数を明示的に呼び出す運用とする。"""
    if audit_result["overall_status"] == "POTENTIAL_DIRECTION_REVERSAL":
        reversed_facts = [r for r in audit_result["results"] if r["verdict"] == "POTENTIAL_DIRECTION_REVERSAL"]
        raise DirectionalFactReversalError(
            f"POTENTIAL_DIRECTION_REVERSAL: {len(reversed_facts)}件の比較方向反転の疑いがあります。"
            f"詳細: {reversed_facts}")
