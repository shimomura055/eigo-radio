# ============================================================
# er008_point_regenerate_19.py
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 3: Point-only
# regeneration(記事全体を再生成せず、NGになったPoint 1件だけを、
# 確定済みFull Story・Verified Fact Ledgerと整合させたまま差し替える)
# ============================================================
# 背景: er008_point_overlap_qa_18.py(第1段階の安価なlexical overlap
# 検知)がPoint One/TwoとFull Storyの意味重複を検知できるようになったが、
# flag時に「記事全体を書き直す」しか手段が無かった(既存のregenerate系
# script[er003_v1_n3_01_articles_regenerate.py等]は全て、Full Story+
# 両Point+In One Lineをまとめて1回のWriter呼び出しで再生成する設計しか
# 持たない)。記事全体の再生成は、Full Story/他方のPoint/In One Line/
# 既に生成済みのFact Checker・Ledger Deviation Check結果まで無駄に
# 揺らしてしまい、コスト・処理時間の両面で過剰(ユーザー指示: 「記事全体の
# 再生成は避ける」)。
#
# 設計: NGになったPoint 1件だけをLLMに再生成させ、Full Story・他方の
# Point・Verified Fact Ledgerは一切変更せずそのまま渡す(コンテキストとして
# 固定)。既存のfact-check系呼び出しパターン(client.responses.create、
# developer message + user message)を踏襲する新規呼び出しを追加する
# (新しいProviderは増やさない)。
#
# 既知の限界(正直に記録): 以下の検証は自動化していない、または弱い
# ヒューリスティックに留まる(将来のOpen Item):
#   - 「Pointとして新しい切り口がある」の判定は自動化していない
#     (er008_point_overlap_qa_18の閾値未満=paraphraseではない、以上の
#     ことは示せない。「本当に別の意味付けか」は人間またはLLM境界判定
#     [第2段階、今回は未実装]が必要)。
#   - 「Fact整合」チェックは、新規テキストの内容語のうちFull Story・
#     Verified Fact Ledgerのいずれにも出現しない語を機械的に列挙する
#     だけの弱いヒューリスティックであり(新語彙の言い換えを大量に
#     誤検知しうる)、「新しい数値・固有名詞・因果関係の主張が追加され
#     ていないか」を意味的に判定するものではない。
#   - 「文体/レベル整合」(A2/B1の難易度・語彙レベルに合っているか)は
#     自動チェックしていない(人間の主観判断が必要)。

from __future__ import annotations

import re

import er008_point_overlap_qa_18 as overlap_qa

POINT_REGENERATE_DEVELOPER_MESSAGE = (
    "You rewrite a single paragraph of an English-language news podcast script. "
    "Always respond in English only, with just the rewritten paragraph text "
    "(no headings, no labels, no explanation)."
)

PROHIBITIONS_EN = """Do not do any of the following:
- Do not restate or lightly reword the same logic/argument already made in the Full Story.
- Do not introduce any new fact, number, date, or named entity that is not present in the
  Verified Fact Ledger or the Full Story below.
- Do not drift the causal claim (do not imply a stronger or weaker cause-and-effect
  relationship than what the Full Story/Ledger actually supports).
- Do not drift the certainty level (do not state something as confirmed if the Ledger
  marks it as ambiguous/uncertain, or vice versa).
- Do not drift the scope (do not generalize beyond what the specific facts cover, and do
  not narrow a general finding into a false specific claim)."""


def build_point_regenerate_prompt(point_label: str, existing_point_text: str, full_story_text: str,
                                    other_point_text: str, verified_fact_ledger_text: str,
                                    ng_reason: str, role_spec_text: str) -> str:
    return f"""You are rewriting {point_label} for a news podcast episode because it failed a
duplication check: it was found to be too close to a paraphrase of the Full Story
instead of adding real depth.

[ROLE OF {point_label.upper()}]
{role_spec_text}

[WHY THE PREVIOUS VERSION WAS REJECTED]
{ng_reason}

[VERIFIED FACT LEDGER — the only facts you may reference]
{verified_fact_ledger_text}

[FULL STORY — already fixed, do not change, do not restate its logic]
{full_story_text}

[THE OTHER POINT IN THIS EPISODE — your new version must cover a different angle from this]
{other_point_text}

[PREVIOUS (REJECTED) VERSION OF {point_label}]
{existing_point_text}

[PROHIBITIONS]
{PROHIBITIONS_EN}

Write a new version of {point_label} that gives the listener a genuinely different angle
(for example: psychological/social reasoning behind the behavior, a broader real-world
implication, a comparison, or a "why does this matter to the listener" framing) —
something the Full Story does not already say. Keep a similar length to the previous
version."""


def _extract_content_words_not_in_sources(new_text: str, *source_texts: str) -> list:
    """新規テキストの内容語のうち、渡されたsource_texts(Full Story・
    Verified Fact Ledger等)のいずれにも出現しない語を列挙する弱い
    ヒューリスティック(新Fact混入の可能性がある語の一覧、機械的な
    確定判定ではない、人間の目視確認を前提とする)。"""
    new_words = overlap_qa._content_words(new_text)
    source_words = set()
    for t in source_texts:
        source_words |= overlap_qa._content_words(t)
    return sorted(new_words - source_words)


def regenerate_point_only(client, point_label: str, existing_point_text: str, full_story_text: str,
                            other_point_text: str, verified_fact_ledger_text: str, ng_reason: str,
                            role_spec_text: str, model: str, overlap_threshold: float = overlap_qa.OVERLAP_FLAG_THRESHOLD,
                            max_attempts: int = 2, reasoning_effort: str = None) -> dict:
    """NGになったPoint 1件をLLMで再生成し、再生成後の必須検証(Full Story
    との意味重複再チェック・他Pointとの役割重複チェック・弱いFact整合
    ヒューリスティック)を行う。記事の他の部分(Full Story/他方のPoint/
    Fact Checker/Ledger Deviation Check結果)は一切変更しない。"""
    prompt = build_point_regenerate_prompt(
        point_label, existing_point_text, full_story_text, other_point_text,
        verified_fact_ledger_text, ng_reason, role_spec_text)

    attempts = []
    create_kwargs = {"model": model, "input": [
        {"role": "developer", "content": POINT_REGENERATE_DEVELOPER_MESSAGE},
        {"role": "user", "content": prompt},
    ]}
    if reasoning_effort:
        create_kwargs["reasoning"] = {"effort": reasoning_effort}
    for attempt in range(1, max_attempts + 1):
        response = client.responses.create(**create_kwargs)
        new_text = (response.output_text or "").strip()
        if not new_text:
            attempts.append({"attempt": attempt, "status": "EMPTY_RESPONSE"})
            continue

        overlap_vs_story = overlap_qa.flag_possible_paraphrase(new_text, full_story_text, threshold=overlap_threshold)
        overlap_vs_other_point = overlap_qa.flag_possible_paraphrase(
            new_text, other_point_text, threshold=overlap_threshold)
        possible_new_facts = _extract_content_words_not_in_sources(
            new_text, full_story_text, verified_fact_ledger_text)

        validation = {
            "overlap_vs_full_story": overlap_vs_story,
            "overlap_vs_other_point": overlap_vs_other_point,
            "possible_new_fact_words": possible_new_facts,
            "fact_check_note": ("これはヒューリスティックであり、Fact整合の確定判定ではない"
                                 "(既知の限界、モジュールdocstring参照)。"),
        }
        passed = (not overlap_vs_story["flagged"]) and (not overlap_vs_other_point["flagged"])

        attempts.append({
            "attempt": attempt, "status": "OK", "new_text": new_text,
            "model": response.model, "response_id": response.id, "validation": validation, "passed": passed,
        })
        if passed:
            return {
                "status": "OK", "new_text": new_text, "attempts": attempts, "validation": validation,
                "point_label": point_label,
            }

    return {
        "status": "STOPPED",
        "reason": f"{max_attempts}回再生成してもFull Story/他Pointとの重複検証に合格しませんでした",
        "attempts": attempts, "point_label": point_label,
    }
