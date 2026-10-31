# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B: Prompt・schema定義(Trial専用。Production Promptではない)。
特定の語・訳語・記事固有の例を一切書かない(M-8、機械照合は jaq02b_run.m8_check)。"""
import hashlib

PRINCIPLES = (
    "あなたは英語学習教材の日本語訳レビュアーです。学習対象の英語表現(expression)について、現在の日本語訳(current_ja)が、"
    "本文のこの箇所での意味を学習者に適切に伝えているかを、記事全文と該当箇所の文脈に基づいて判定します。特定の語についての決まりごとはありません。"
    "毎回、本文の文脈から判断してください。各項目は互いに独立に判定し、前の項目の判定に引きずられないでください。"
    "訳が妥当なら warn=false にします。疑わしいだけで根拠が弱い場合や、好みの言い換えにすぎない場合も warn=false にします。"
    "warn=true にするのは、次のいずれかを具体的に説明できるときだけです。"
    "(1)本文の文脈での意味と合っていない (2)文脈上の意味でなく、一般的・辞書の第一義的な意味になっている "
    "(3)比喩やたとえの意味が変わってしまっている (4)確立した定訳・専門用語があるのに、定義文や別の語に不適切に置き換えている "
    "(5)日本語として不自然・冗長・分かりにくく、学習項目の訳として不適切。"
    "severity は、意味が変わる・定訳が消える場合は major、意味は概ね取れるが不自然・冗長などの場合は minor、問題なしは none。"
    "confidence は、その判定への確信度です。"
    "reason_ja は60字以内で具体的に書き、断定しすぎない表現にします。"
    "suggestion は、より適切な訳が明確にあるときだけ書き、なければ空文字にします。warn=false の項目は reason_ja と suggestion を空文字にします。"
)
BATCH_NOTE = "次の複数項目を、同じ記事の文脈で一括して検査してください。出力の results には、入力した全ての id を1件ずつ、漏れなく含めてください。"
SINGLE_NOTE = "次の1項目を、記事の文脈で検査してください。"
REF_NOTE = (
    "項目に other_level_ja がある場合、それは同じ記事の別レベルで同じ表現に付けられている訳です。"
    "同じ表現なのに意味が食い違う訳が付いているときは category=inconsistent としますが、言い回しが違うだけで意味が同じなら問題にしません。"
)
M3_NOTE = (
    "各項目で、(A)意味の忠実度 fidelity(faithful=文脈の意味を適切に表す / partial=一部ずれる・弱い / wrong=意味が合わない)と、"
    "(B)日本語の自然さ naturalness(natural / awkward / unclear)を、別々に評価してから、総合の warn・severity を決めてください。"
    "(B)だけの問題(意味は合っている)は severity=minor とし、category=unnatural_ja にします。"
)
R6_NOTE = (
    "各項目で、判定の前に次の分析欄を先に書いてください。"
    "context_sense_en=本文のこの箇所でこの表現が実際に表している意味(英語1文以内)、"
    "figurative=この箇所で比喩・たとえ・慣用として使われているか、"
    "established_term=この意味に対して確立した日本語の定訳・専門用語があればその語、なければ空文字。"
    "その分析に基づいて current_ja を判定してください。"
)
M6S1 = (
    "あなたは英語学習教材の翻訳者です。以下の各項目について、記事全文と該当箇所の文脈に基づき、本文のこの箇所での意味を学習者に伝えるのに最も適した日本語訳を、"
    "1語または短い句で best_ja に書いてください(学習項目の訳として、本文の該当表現に置き換えて読める形)。"
    "文脈上の意味が比喩・慣用なら、その意味が伝わる訳にします。確立した定訳・専門用語があればそれを使います。"
    "acceptable_alternatives には、同じ意味として許容できる別の訳があれば最大2件書きます(なければ空配列)。出力の results には全ての id を1件ずつ含めてください。"
)
M6S2 = (
    "あなたは英語学習教材の日本語訳レビュアーです。各項目には、現在の訳(current_ja)と、現在の訳を見せずに独立に作った推奨訳(best_ja)・許容別訳があります。"
    "current_ja が、本文の文脈での意味を適切に伝えているかを判定します。推奨訳と文字が違うだけで意味が同等なら問題にしません(equivalent=true, warn=false)。"
    "意味が合わない、一般的すぎる、比喩の意味が変わる、定訳を不適切に言い換えている、日本語として不自然・冗長で学習項目の訳として不適切、のいずれかが具体的に説明できる場合だけ warn=true にします。"
    "severity は、意味が変わる・定訳が消える場合は major、意味は概ね取れるが不自然・冗長などの場合は minor、問題なしは none。confidence は判定への確信度。"
    "reason_ja は60字以内で具体的に、suggestion は明確な代案があるときだけ書きます(warn=false では両方とも空文字)。出力の results には全ての id を1件ずつ含めてください。"
)
M5S2 = (
    "あなたは英語学習教材の日本語訳レビュアーです。各項目について、本文のこの箇所での意味を、より正確かつ自然に表しているのは訳Aと訳Bのどちらかを、記事の文脈に基づいて選んでください。"
    "どちらも同程度に適切、または差が小さい(好みの違い程度)場合は equal を選びます。差がはっきりしている場合だけ A か B を選びます。reason_ja は60字以内。"
    "出力の results には全ての id を1件ずつ含めてください。"
)

CATS = ["none", "meaning_mismatch", "too_generic", "lost_nuance", "established_term_replaced", "unnatural_ja", "inconsistent"]


def _props(extra_before=None, extra_after=None):
    p = {"id": {"type": "string"}}
    for k, v in (extra_before or []): p[k] = v
    p.update({
        "warn": {"type": "boolean"},
        "severity": {"type": "string", "enum": ["none", "minor", "major"]},
        "confidence": {"type": "string", "enum": ["low", "mid", "high"]},
        "category": {"type": "string", "enum": CATS},
        "reason_ja": {"type": "string"},
        "suggestion": {"type": "string"},
    })
    for k, v in (extra_after or []): p[k] = v
    return p


def _wrap(name, props):
    return {"name": name, "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["results"], "properties": {
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": list(props.keys()), "properties": props}}}}}


SCHEMAS = {
    "base": _wrap("gloss_quality_check", _props()),
    "m3": _wrap("gloss_quality_check_m3", _props(extra_before=[("fidelity", {"type": "string", "enum": ["faithful", "partial", "wrong"]}), ("naturalness", {"type": "string", "enum": ["natural", "awkward", "unclear"]})])),
    "r6": _wrap("gloss_quality_check_r6", _props(extra_before=[("context_sense_en", {"type": "string"}), ("figurative", {"type": "boolean"}), ("established_term", {"type": "string"})])),
    "m6s1": _wrap("blind_best_translation", {"id": {"type": "string"}, "best_ja": {"type": "string"}, "acceptable_alternatives": {"type": "array", "items": {"type": "string"}}}),
    "m6s2": _wrap("blind_compare", _props(extra_before=[("equivalent", {"type": "boolean"})])),
    "m5s2": _wrap("ab_choice", {"id": {"type": "string"}, "choice": {"type": "string", "enum": ["A", "B", "equal"]}, "reason_ja": {"type": "string"}}),
}


def developer_text(method, ref=False, batch=True):
    t = PRINCIPLES + (BATCH_NOTE if batch else SINGLE_NOTE)
    if method == "M3": t += M3_NOTE
    if method == "R6": t += R6_NOTE
    if ref: t += REF_NOTE
    return t


def all_prompt_texts():
    """M-8照合の対象(Prompt本文+schema名/キー)。"""
    out = {"PRINCIPLES": PRINCIPLES, "BATCH_NOTE": BATCH_NOTE, "SINGLE_NOTE": SINGLE_NOTE, "REF_NOTE": REF_NOTE, "M3_NOTE": M3_NOTE, "R6_NOTE": R6_NOTE,
           "M6S1": M6S1, "M6S2": M6S2, "M5S2": M5S2}
    return out


def prompt_sha():
    h = hashlib.sha256()
    for k, v in sorted(all_prompt_texts().items()): h.update((k + "\n" + v + "\n").encode("utf-8"))
    return h.hexdigest()
