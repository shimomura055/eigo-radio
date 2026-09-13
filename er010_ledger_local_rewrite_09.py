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


# OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01 Phase B
# (B3、Fable判断2026-09-13「本Trialの前提修正としてスコープに含める」):
# 従来はMarkdown見出し行(`#`/`##`/`###`...)も他の行と区別せず1つのスペース
# で連結してから文分割していたため、見出し(`.!?`で終わらない)が前後の文へ
# 結合され、「1つの対象文」が実際には複数文+見出しの塊になる既知の不具合が
# あった(Phase A A2で全163ファイル実データscan、3/63件[4.8%]で確認)。
# 実データ確認(`er011_output/daily_news_focus_layer_comparison_trial_04/
# b1b/focus/run2`)では、この不具合により`apply_rewrites()`の文字列置換
# (改行を含む実際の記事本文に対し、見出し混入で改行がスペースへ変わった
# `original_ng_sentence`を探索)が一致せず、Local Rewriteが`resolved=True`
# を記録したにもかかわらず、実際に出荷された記事本文はMAJOR判定された
# 元の文のまま変わっていなかった(サイレント無変更、OPEN-141 Phase B
# REPORT参照)。見出し行(`#`で始まる行)・空行を文候補の連結対象から除外する
# ことで、対象文の単位を見出しをまたがない実際の1文に正しく限定する。
# 見出しを含まない入力に対する挙動は従来と完全に同一(見出し除外の
# has-no-effect回帰テストで保証、`er010_open141_target_sentence_matching_
# diff_qa_b_test_01.py`)。
def split_sentences(text: str) -> list:
    flat = " ".join(
        line.strip() for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
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


# ============================================================
# OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01 Phase B
# (B1、Fable判断2026-09-13「案I採用、run_check_window_fnインターフェースに
# opt-in[既定OFF]でtarget-sentence-matching受理ロジックを追加」)
# ============================================================
# 背景: 従来の受理判定は「対象文+前後各1文」というwindow全体の
# overall_status(Ledger Deviation Checkerが返す10種フラグのいずれかが
# MAJORか)のみで決まり、前後の文にだけ存在する逸脱に対象文自身の書き換え
# が巻き込まれ、false rejectを起こす盲点があった
# (`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`
# Stage 1b-1、OPEN-141 Phase A A3で保存済み実データ8件中6件を¥0で再確認)。
# 本ロジックは、window全体のdeviations配列を対象文/前後文へ対応付け
# (exact_substring→word-overlap fallback、Phase A A2のlocate_target_
# sentenceと同一方式)し、対象文自身に紐づくdeviationのみでoverall_status
# を再計算する。対応付けが曖昧(not_found・複数一致・僅差のtie)な
# deviationが1件でもあれば、安全側としてwindow全体のoverall_statusへ
# フォールバックする(危険な変更を誤って通さないための保守的な既定動作)。
# Judgeの基準・prompt自体は一切変更しない(Ledger Deviation Checkerの
# 呼び出しはそのまま、事後の集計ロジックのみを変える)。
_ROLE_MATCH_THRESHOLD = 0.25  # locate_target_sentenceと同一閾値
_ROLE_TIE_MARGIN = 0.05  # 上位2候補の差がこの値未満なら「僅差=曖昧」とする


def _role_content_words(text: str) -> set:
    return set(re.findall(r"[a-z']+", (text or "").lower()))


def _role_word_overlap(a: str, b: str) -> float:
    wa, wb = _role_content_words(a), _role_content_words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def classify_deviation_role(claim_in_article: str, target_sentence: str, before_ctx: str,
                             after_ctx: str) -> dict:
    """claim_in_article(Ledger Deviation Checkerが引用した逸脱箇所)が、
    window内のtarget_sentence(対象文=rewrite候補)/before_ctx/after_ctxの
    どれに属するかを判定する。role in {'target','before','after','ambiguous'}。
    ambiguousの場合、呼び出し側(evaluate_target_sentence_status)は安全側
    フォールバックする。"""
    claim = (claim_in_article or "").strip()
    candidates = {"target": target_sentence or "", "before": before_ctx or "", "after": after_ctx or ""}
    if not claim:
        return {"role": "ambiguous", "method": "empty_claim"}
    exact_hits = [role for role, text in candidates.items() if text and claim in text]
    if len(exact_hits) == 1:
        return {"role": exact_hits[0], "method": "exact_substring"}
    if len(exact_hits) > 1:
        return {"role": "ambiguous", "method": "exact_substring_multi_match", "candidates": exact_hits}
    scores = {role: _role_word_overlap(claim, text) for role, text in candidates.items()}
    best_role = max(scores, key=scores.get)
    best_score = scores[best_role]
    if best_score < _ROLE_MATCH_THRESHOLD:
        return {"role": "ambiguous", "method": "not_found", "scores": scores}
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) > 1 and (sorted_scores[0] - sorted_scores[1]) < _ROLE_TIE_MARGIN:
        return {"role": "ambiguous", "method": "tie", "scores": scores}
    return {"role": best_role, "method": f"word_overlap({round(best_score, 2)})", "scores": scores}


def evaluate_target_sentence_status(check_result: dict, target_sentence: str, before_ctx: str,
                                     after_ctx: str) -> dict:
    """window全体のcheck_result(dict、'deviations'+'overall_status'を含む、
    vfl01.run_deviation_check()['parsed']と同一形式)から、対象文
    (target_sentence)に対応するdeviationのみを抽出し、対象文単位の
    overall_statusを算出する(Phase A A3で保存済み実データにより検証済みの
    再分類方式)。deviationsが空ならCOMPLIANT。対応付けがambiguousな
    deviationが1件でもあれば、window全体のoverall_statusへフォールバック
    する(match_fallback=Trueとして記録)。"""
    window_status = check_result.get("overall_status", "LEDGER_DEVIATION")
    deviations = check_result.get("deviations", [])
    if not deviations:
        return {"overall_status": "LEDGER_COMPLIANT", "window_overall_status": window_status,
                "target_deviations": [], "adjacent_deviations": [], "ambiguous_deviations": [],
                "match_fallback": False}
    target_devs, adjacent_devs, ambiguous_devs = [], [], []
    for d in deviations:
        classification = classify_deviation_role(
            d.get("claim_in_article", ""), target_sentence, before_ctx, after_ctx)
        entry = {**d, "_role_classification": classification}
        role = classification["role"]
        if role == "target":
            target_devs.append(entry)
        elif role == "ambiguous":
            ambiguous_devs.append(entry)
        else:
            adjacent_devs.append(entry)
    if ambiguous_devs:
        return {"overall_status": window_status, "window_overall_status": window_status,
                "target_deviations": target_devs, "adjacent_deviations": adjacent_devs,
                "ambiguous_deviations": ambiguous_devs, "match_fallback": True}
    status = "LEDGER_DEVIATION" if any(d.get("severity") == "MAJOR" for d in target_devs) \
        else "LEDGER_COMPLIANT"
    return {"overall_status": status, "window_overall_status": window_status,
            "target_deviations": target_devs, "adjacent_deviations": adjacent_devs,
            "ambiguous_deviations": [], "match_fallback": False}


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
                     after_ctx: str, run_check_window_fn,
                     use_target_sentence_matching: bool = False) -> dict:
    """run_check_window_fn(window_text: str) -> dictで、少なくとも
    'overall_status'キー('LEDGER_COMPLIANT'/'LEDGER_DEVIATION')を返す
    呼び出し可能オブジェクトを渡す(呼び出し元がHook-aware判定を使うか
    どうかを制御できるよう、判定ロジック自体はこの関数に埋め込まない)。

    point_context: 対象文が属するPoint(またはsection)全文。
    extract_point_context()で取得する(OPEN-113-POINT-CONTEXT-PRODUCTION-
    WIRING-04)。見つからない場合、呼び出し側でbefore_ctx+ng_sentence+
    after_ctx等へのfallback文字列を渡すことを想定し、この関数自身は
    contextの取得方法に関与しない。

    use_target_sentence_matching: OPEN-141 Phase B(B1)で追加したopt-in
    パラメータ、既定False。Falseの間はrun_check_window_fnが返す
    'overall_status'(window全体判定)のみで受理判定する既存の挙動と
    完全に同一(戻り値のattemptsエントリも従来通り{'attempt','text',
    'ledger_status'}の3キーのみ、他の呼び出し元[A/B-Family]は本引数を
    渡さないため無変更)。Trueの場合のみ、run_check_window_fnの戻り値の
    'deviations'配列をevaluate_target_sentence_status()で対象文/前後文へ
    対応付け、対象文自身に紐づくdeviationのみでoverall_statusを再計算
    する(対応付けambiguous時はwindow全体判定へ安全側フォールバック)。
    Trueの場合のみ、attemptsエントリに診断用キー
    ('ledger_status_window'/'target_sentence_eval')を追加する。"""
    flags_true = [k for k in vfl01.DEVIATION_FLAG_KEYS if deviation.get(k)]
    attempts = []
    accepted_text, accepted, human_review = None, False, False

    def _check_and_record(attempt_no: int, candidate_text: str, check_result: dict) -> str:
        if not use_target_sentence_matching:
            status = check_result["overall_status"]
            attempts.append({"attempt": attempt_no, "text": candidate_text, "ledger_status": status})
            return status
        target_eval = evaluate_target_sentence_status(check_result, candidate_text, before_ctx, after_ctx)
        status = target_eval["overall_status"]
        attempts.append({
            "attempt": attempt_no, "text": candidate_text, "ledger_status": status,
            "ledger_status_window": check_result["overall_status"],
            "target_sentence_eval": target_eval,
        })
        return status

    prompt1 = REWRITE_ATTEMPT1_TEMPLATE.format(
        ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=ng_sentence,
        issue=deviation["issue"])
    text1 = generate_rewrite(client, model, reasoning_effort, prompt1)
    check1 = run_check_window_fn(f"{before_ctx} {text1} {after_ctx}".strip())
    status1 = _check_and_record(1, text1, check1)
    if status1 == "LEDGER_COMPLIANT":
        accepted_text, accepted = text1, True
    else:
        prompt2 = REWRITE_ATTEMPT2_TEMPLATE.format(
            ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text1,
            issue=deviation["issue"], explanation=deviation["explanation"],
            flags=", ".join(flags_true) or "(none)")
        text2 = generate_rewrite(client, model, reasoning_effort, prompt2)
        check2 = run_check_window_fn(f"{before_ctx} {text2} {after_ctx}".strip())
        status2 = _check_and_record(2, text2, check2)
        if status2 == "LEDGER_COMPLIANT":
            accepted_text, accepted = text2, True
        else:
            prompt3 = REWRITE_ATTEMPT3_TEMPLATE.format(
                ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text2,
                issue=deviation["issue"])
            text3 = generate_rewrite(client, model, reasoning_effort, prompt3)
            check3 = run_check_window_fn(f"{before_ctx} {text3} {after_ctx}".strip())
            status3 = _check_and_record(3, text3, check3)
            if status3 == "LEDGER_COMPLIANT":
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
