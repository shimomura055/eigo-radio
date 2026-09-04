# ============================================================
# er010_ledger_local_rewrite_09.py
# ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09
# ============================================================
# Ledger Deviation Checker(Hook-aware、er003_v1_en_direct_vfl_01_generate.py)
# がMAJORを検出した際の局所Rewrite、Production正式実装。
#
# 由来: er009_n1_full_writer_ledger_integration_08.py(Trial-08)の
# REWRITE_SYSTEM_PROMPT・3段階escalating attempt(Attempt1=issue提示、
# Attempt2=flags/explanation追加、Attempt3=scope-safe fallback)・
# locate_target_sentence(exact substring→word-overlap>=0.25 fallback)を
# そのまま踏襲する。最大3回という上限も、根拠のない新設ではなくTrial-08
# 自身の設計をそのまま引き継いだもの(このTrial自身のrewriteループは
# 実データで一度も発火しなかった=A2/B1とも初回LEDGER_COMPLIANTだったため、
# 本モジュールがこのロジックの初めてのProduction runtime適用になる)。
#
# 対象はMAJORのみ(MINORは対象外)。修正は当該文(前後の文をcontextとして
# 参照するのみ、書き換えるのは対象文だけ)に限定し、記事全体の再生成は
# 行わない。Ledgerにない新Factの追加・因果/確信度の強化・比較や時系列の
# 反転は、REWRITE_SYSTEM_PROMPT自体で明示的に禁止する。

from __future__ import annotations

import re

import er003_v1_en_direct_vfl_01_generate as vfl01

MAX_REWRITE_ATTEMPTS = 3

# ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10: 記事全体を再チェックし、新たな
# MAJORが見つかった場合に再度Local Rewriteを行う「cycle」次元の上限。
# 新しい上限値を独自に発明するのではなく、既存承認済みの文単位試行上限
# MAX_REWRITE_ATTEMPTS(Trial-08由来、3回)を、記事全体cycleの次元にも
# そのまま適用したもの(ユーザーがER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10で
# 明示的に許可: 「既存上限の適用範囲整理で済むなら、その根拠を明示した
# うえで進めてよい」)。文単位のRetry上限とは独立した別軸のカウンタ。
MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def split_sentences(text: str) -> list:
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(flat) if s.strip()]


def locate_target_sentence(claim_in_article: str, article_text: str):
    """claim_in_articleが記事本文中に厳密一致する箇所を探す。見つからない
    場合、文単位に分割しword-overlap比率が最も高い文をfallbackとして採用
    する(overlap>=0.25、Trial-08と同一の閾値)。"""
    if claim_in_article and claim_in_article.strip() in article_text:
        return claim_in_article.strip(), "exact_substring"
    sentences = split_sentences(article_text)
    claim_words = set(re.findall(r"[a-z']+", claim_in_article.lower()))
    best, best_score = None, 0.0
    for s in sentences:
        s_words = set(re.findall(r"[a-z']+", s.lower()))
        if not s_words or not claim_words:
            continue
        overlap = len(claim_words & s_words) / len(claim_words | s_words)
        if overlap > best_score:
            best, best_score = s, overlap
    if best is not None and best_score >= 0.25:
        return best, f"sentence_fallback(overlap={round(best_score, 2)})"
    return None, "not_found"


# OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-04: OPEN-113 Trial-03
# (er011_open113_point_context_only_trial_03.py)でVALIDATEDとなった
# 「対象文が属するPoint全体をRewriteモデルのcontextとして渡す」方式の
# Production実装。見出し(#で始まる行)ごとに記事をsectionへ区切る単純な
# 実装で、Point One/Twoに限定しない(Main Story/In One Line等、既存Local
# Rewrite適用範囲内のどのsectionでも同一ロジックで扱える汎用実装とし、
# 対象を勝手に拡張しない)。Trial-01のextract_section()と同一ロジックを
# Production側へ直接移植したもので、Trial専用モジュールへの依存は持たない。
def extract_point_context(article_text: str, target_sentence: str):
    """target_sentenceが属する見出し区切りsection全文を返す。見つからない
    場合はNone(呼び出し側でbefore/after contextへのfallbackを想定する)。"""
    lines = article_text.splitlines()
    sections, current = [], []
    for line in lines:
        if line.startswith("#"):
            if current:
                sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    for sec in sections:
        if target_sentence in sec:
            return sec
    return None


REWRITE_SYSTEM_PROMPT = """You are a professional Writer fixing a fact deviation flagged by a \
Ledger Deviation Checker, for a local, minimal rewrite (not a full regeneration).

Rules:
1. Do NOT create new generalizations.
2. Preserve the original intent and interest as much as possible.
3. Soften strong assertions like "always / everywhere / exactly / definitely" first.
4. Use "can / may / might / some / sometimes / in some cases" to adjust scope/certainty as needed.
5. Do NOT reverse the direction of meaning.
6. Even when you soften a strong assertion, keep its central point — do NOT retreat into a bland, \
generic fact statement.
7. Modify ONLY the flagged sentence or the minimum necessary range — do not change other text.
8. Do NOT introduce a new fact or a different Ledger fact to change the subject.
9. Do NOT add emoji (💳 or any other emoji) to the revised text. Do NOT add unnecessary Markdown \
bold (**...**) formatting. Keep formatting clean and plain.

Return ONLY the revised sentence(s), nothing else — no explanation, no quotation marks around it."""

# OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-04: 上記REWRITE_SYSTEM_PROMPT・
# 各attemptの指示文(下記テンプレート内の英文)は一字一句変更しない。追加
# するのは、対象文が属するPoint(またはsection)全文を「参考情報のみ」として
# 提示する1ブロックのみで、新しいRuleは追加しない(Trial-03で検証済みの
# POINT_CONTEXT_BLOCKをそのまま使用)。
POINT_CONTEXT_BLOCK = """[The full Point this sentence belongs to — shown for reference only]
{point_context}

"""

REWRITE_ATTEMPT1_TEMPLATE = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence flagged as a Ledger deviation]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "Rewrite this sentence following the rules above. Return only the revised sentence."
)

REWRITE_ATTEMPT2_TEMPLATE = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence still flagged after a first rewrite attempt]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "[Checker's explanation]\n{explanation}\n\n"
      "[Flags the checker marked true]\n{flags}\n\n"
      "Your previous rewrite still did not resolve this deviation. Rewrite it again, paying specific "
      "attention to the flags above. Return only the revised sentence."
)

REWRITE_ATTEMPT3_TEMPLATE = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence still flagged after two rewrite attempts]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "This is the final attempt: use a Scope-safe fallback. Make the evidence's scope naturally "
      "explicit in the sentence (choose whichever fits the sentence naturally, do not just "
      "mechanically prepend a fixed phrase): \"In this study...\", \"Among these passengers...\", "
      "\"In these taxi rides...\", \"The study suggests...\", \"In this case...\", or similar. Keep as "
      "much of the original meaning and interest as possible. Return only the revised sentence."
)


def generate_rewrite(client, model: str, reasoning_effort: str, prompt: str) -> str:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_text.strip()


def rewrite_ng_item(client, model: str, reasoning_effort: str, verified_ledger_text: str,
                     point_context: str, ng_sentence: str, deviation: dict, before_ctx: str,
                     after_ctx: str, run_check_window_fn) -> dict:
    """run_check_window_fn(window_text: str) -> dictで、少なくとも
    'overall_status'キー('LEDGER_COMPLIANT'/'LEDGER_DEVIATION')を返す
    呼び出し可能オブジェクトを渡す(呼び出し元がHook-aware判定を使うか
    どうかを制御できるよう、判定ロジック自体はこの関数に埋め込まない)。

    point_context: 対象文が属するPoint(またはsection)全文。
    extract_point_context()で取得する(OPEN-113-POINT-CONTEXT-PRODUCTION-
    WIRING-04)。見つからない場合、呼び出し側でbefore_ctx+ng_sentence+
    after_ctx等へのfallback文字列を渡すことを想定し、この関数自身は
    contextの取得方法に関与しない。"""
    flags_true = [k for k in vfl01.DEVIATION_FLAG_KEYS if deviation.get(k)]
    attempts = []
    accepted_text, accepted, human_review = None, False, False

    prompt1 = REWRITE_ATTEMPT1_TEMPLATE.format(
        ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=ng_sentence,
        issue=deviation["issue"])
    text1 = generate_rewrite(client, model, reasoning_effort, prompt1)
    check1 = run_check_window_fn(f"{before_ctx} {text1} {after_ctx}".strip())
    attempts.append({"attempt": 1, "text": text1, "ledger_status": check1["overall_status"]})
    if check1["overall_status"] == "LEDGER_COMPLIANT":
        accepted_text, accepted = text1, True
    else:
        prompt2 = REWRITE_ATTEMPT2_TEMPLATE.format(
            ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text1,
            issue=deviation["issue"], explanation=deviation["explanation"],
            flags=", ".join(flags_true) or "(none)")
        text2 = generate_rewrite(client, model, reasoning_effort, prompt2)
        check2 = run_check_window_fn(f"{before_ctx} {text2} {after_ctx}".strip())
        attempts.append({"attempt": 2, "text": text2, "ledger_status": check2["overall_status"]})
        if check2["overall_status"] == "LEDGER_COMPLIANT":
            accepted_text, accepted = text2, True
        else:
            prompt3 = REWRITE_ATTEMPT3_TEMPLATE.format(
                ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text2,
                issue=deviation["issue"])
            text3 = generate_rewrite(client, model, reasoning_effort, prompt3)
            check3 = run_check_window_fn(f"{before_ctx} {text3} {after_ctx}".strip())
            attempts.append({"attempt": 3, "text": text3, "ledger_status": check3["overall_status"]})
            if check3["overall_status"] == "LEDGER_COMPLIANT":
                accepted_text, accepted = text3, True
            else:
                accepted_text, accepted, human_review = text3, False, True

    return {
        "original_ng_sentence": ng_sentence, "issue": deviation["issue"],
        "explanation": deviation["explanation"], "flags": flags_true, "attempts": attempts,
        "final_text": accepted_text, "resolved": accepted, "human_review_required": human_review,
    }


def apply_rewrites(article_text: str, rewrite_results: list) -> str:
    updated = article_text
    for r in rewrite_results:
        if r["final_text"] and r["original_ng_sentence"] in updated:
            updated = updated.replace(r["original_ng_sentence"], r["final_text"], 1)
    return updated
