# ============================================================
# er013_family_c_future_eval_08.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
# ============================================================
# 目的: (A) 補助Story Spark評価(6軸: Future Leap/面白さ/わくわく・ドキドキ/
# 分かりやすさ/リスニング適性/読後の問い、各0-3+一言、LLM 1呼び出し)。
# er013_family_c_future_spark_gate_06.pyの5軸(future_leap/curiosity/
# emotional_pull/thought_provoking/core_provocation_clarity)には「分かり
# やすさ」「リスニング適性」が無いため、委任文どおり新規_08評価関数として
# 実装する(spark_gate_06.pyは無編集のまま)。
# (B) 登場人物数の決定的カウント(正規表現ヒューリスティック、LLM不使用)。
# 固有名候補(文頭語を除く大文字始まり語)と、関係性表現(his/her/their +
# mother/father/friend等)の出現をそれぞれ機械的に数える。あくまで推定値
# であり、RESULT_PACKETでは手動確認値も併記する(委任文の方針)。
#
# 既存er013_family_c_future_*_01〜07.pyは一切編集しない(新規ファイル)。
# PASS/FAILで記事を破棄する用途には使わない(委任文: 補助評価のみ、最終
# 判断はユーザー人間評価)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json
import re

AXES = ["future_leap", "interestingness", "excitement", "clarity", "listening_friendliness", "lingering_question"]

AXIS_LABEL_JA = {
    "future_leap": "Future Leap(未来を感じるか)",
    "interestingness": "面白さ",
    "excitement": "わくわく・ドキドキ",
    "clarity": "分かりやすさ",
    "listening_friendliness": "リスニング適性(耳で聞いて追えるか)",
    "lingering_question": "読後の問い(読後に何か残るか)",
}

EVAL_JSON_SCHEMA = {
    "name": "family_c_freeform_story_eval",
    "schema": {
        "type": "object",
        "properties": {
            **{axis: {"type": "integer", "minimum": 0, "maximum": 3} for axis in AXES},
            **{f"{axis}_note": {"type": "string", "description": "one short sentence"} for axis in AXES},
            "overall_comment": {"type": "string"},
        },
        "required": [*AXES, *[f"{a}_note" for a in AXES], "overall_comment"],
        "additionalProperties": False,
    },
    "strict": True,
}

EVAL_DEVELOPER_MESSAGE = (
    "You are an auxiliary evaluator for a short imagined-future story in an "
    "English-learning magazine. This is an AUXILIARY score only -- a human editor "
    "makes the final call, and this score never causes an article to be discarded. "
    "Score each axis 0-3 (0=not at all, 1=a little, 2=clearly, 3=strongly), with one "
    "short sentence of reasoning per axis."
)

EVAL_PROMPT_TEMPLATE = """[Core Provocation this article was meant to explore]
{core_provocation}

[Reader-facing article text]
{reader_text}

[Axes to score, each 0-3 with one short sentence]
- future_leap: does the reader genuinely feel this is a leap into the future (not just
  a mild extension of today)?
- interestingness: is this simply an interesting, enjoyable read?
- excitement: does it create some excitement and a little tension (わくわく・ドキドキ)?
- clarity: is the story easy to follow for an A2-level English learner (not confusing,
  not overloaded with abstract explanation)?
- listening_friendliness: would this be easy to follow as AUDIO for a listener (not
  too many named people, not too many time/place jumps, clear whose perspective it is
  at each point)?
- lingering_question: does the reader have something (a question, an image, a feeling)
  that stays with them after finishing?"""


def build_eval_prompt(core_provocation: str, reader_text: str) -> str:
    return EVAL_PROMPT_TEMPLATE.format(core_provocation=core_provocation, reader_text=reader_text)


def run_story_eval(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **EVAL_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": EVAL_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("補助Story Spark評価(_08)の応答が空です")
    parsed = json.loads(text)
    scores = {axis: int(parsed[axis]) for axis in AXES}
    return {
        "parsed": parsed, "scores": scores, "model": response.model, "response_id": response.id,
        "note": "補助評価のみ。PASS/FAILで採用・破棄は決定しない(委任文の方針、最終判断はユーザー人間評価)。",
    }


# ------------------------------------------------------------
# 登場人物数の決定的カウント(正規表現ヒューリスティック、LLM不使用)
# ------------------------------------------------------------
# 文頭(各文の1語目)にだけ現れても人名ではない一般語(代名詞・冠詞・接続詞等)。
# 文頭語を一律除外すると"Maya walked home."のような主人公名の文頭登場を
# 取りこぼすため、位置ではなく語そのもので判定する。
_SENTENCE_START_STOPWORDS = {
    "the", "a", "an", "this", "that", "these", "those", "he", "she", "it", "they",
    "we", "you", "i", "if", "when", "after", "before", "then", "but", "and", "so",
    "because", "one", "every", "some", "many", "most", "later", "now", "soon",
    "suddenly", "maybe", "perhaps", "still", "yet", "also", "even", "just", "only",
    "sometimes", "often", "always", "never", "no", "yes", "well", "here", "there",
    "for", "as", "while", "since", "until", "what", "who", "how", "why",
    # 前置詞・助動詞・所有格代名詞等(文頭に来ても人名ではない、1回目の実行結果
    # を見て追加。委任文の「決定的カウント+手動確認値も併記」を実質的に機能
    # させるための精度改善、既存ファイルの編集ではなく本ファイル内の修正)
    "at", "in", "on", "by", "to", "from", "with", "between", "behind", "inside",
    "did", "was", "were", "would", "could", "should", "will", "can", "may", "might",
    "has", "have", "had", "her", "his", "your", "my", "our", "their", "its", "or",
    "do", "does", "not", "let", "are", "am",
}

# 固有名候補から除外する、大文字始まりでも人名でない一般語(頻出のもの、位置を問わず除外)
_COMMON_NON_NAME_CAPITALIZED = {
    "I", "A2", "IMAGINED", "FACT", "English", "Future", "January", "February", "March",
    "April", "May", "June", "July", "August", "September", "October", "November",
    "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday", "AI", "VR", "AR", "BCI", "The", "If", "When", "One", "Every", "Someday",
}

_RELATIONSHIP_WORDS = [
    "mother", "father", "mom", "dad", "friend", "daughter", "son", "sister", "brother",
    "neighbor", "neighbour", "wife", "husband", "partner", "colleague", "teacher",
    "doctor", "grandmother", "grandfather", "grandson", "granddaughter", "boss",
    "classmate", "roommate", "boyfriend", "girlfriend", "child", "parent", "aunt",
    "uncle", "cousin",
]
_RELATIONSHIP_RE = re.compile(
    r"\b(his|her|their|its|my|your|our)\s+(" + "|".join(_RELATIONSHIP_WORDS) + r")\b", re.IGNORECASE)

_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def find_proper_noun_candidates(reader_text: str) -> list:
    """大文字始まり語を人名候補として抽出する(ヒューリスティック、決定的だが
    完全ではない)。文頭語(各文の1語目)は、代名詞・冠詞・接続詞等の一般語である
    場合のみ除外し、"Maya walked home."のような文頭の主人公名は候補に含める。
    手動確認を推奨、RESULT_PACKETに手動確認値も併記する。"""
    candidates = set()
    for sentence in _SENTENCE_SPLIT_RE.split(reader_text.strip()):
        words = _WORD_RE.findall(sentence)
        for i, w in enumerate(words):
            if not (w[0].isupper() and w.isalpha()):
                continue
            if len(w) > 1 and w.isupper():
                continue  # 全て大文字(ALL CAPS)は本文中の強調・UI表示テキストであり人名ではない
            if w.lower() in {c.lower() for c in _COMMON_NON_NAME_CAPITALIZED}:
                continue
            if i == 0 and w.lower() in _SENTENCE_START_STOPWORDS:
                continue
            candidates.add(w)
    return sorted(candidates)


def find_relationship_references(reader_text: str) -> list:
    return sorted({m.group(0).lower() for m in _RELATIONSHIP_RE.finditer(reader_text)})


def count_characters_heuristic(reader_text: str) -> dict:
    proper_nouns = find_proper_noun_candidates(reader_text)
    relationships = find_relationship_references(reader_text)
    return {
        "proper_noun_candidates": proper_nouns,
        "proper_noun_count": len(proper_nouns),
        "relationship_references": relationships,
        "relationship_reference_count": len(relationships),
        "estimated_total_characters": len(proper_nouns) + len(relationships),
        "note": "ヒューリスティック推定値。RESULT_PACKETで手動確認値も併記する(委任文の方針)。",
    }


# ------------------------------------------------------------
# リスニング適性の簡易決定的指標(一文平均語数・人物切替回数の粗い代理指標)
# ------------------------------------------------------------
def compute_listening_metrics(reader_text: str) -> dict:
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(reader_text.strip()) if s.strip()]
    word_counts = [len(_WORD_RE.findall(s)) for s in sentences]
    avg_sentence_len = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0.0
    max_sentence_len = max(word_counts) if word_counts else 0
    return {
        "sentence_count": len(sentences),
        "avg_sentence_word_count": avg_sentence_len,
        "max_sentence_word_count": max_sentence_len,
    }
