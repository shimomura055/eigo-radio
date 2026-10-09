# -*- coding: utf-8 -*-
"""D1(タイプ別専用Prompt)・D2(万能Flagger)のPrompt。DEV専用。
共通方針: 合否判定しない・修正案を出さない・書き換えない。『人間が確認した方がよい箇所』にFlagを立てるだけ。
出力はJSON1個のみ。Flagが無ければ flags=[]。
"""

TYPES = ["rollback反転", "主体対象入替", "否定反転", "数量時系列", "不在断定"]

COMMON_HEAD = (
    "あなたは記事の校閲補助です。記事の各文を、根拠である台帳Fact(事実の一覧)と照らし、"
    "人間が確認した方がよい箇所にFlagを立てます。合否判定・修正案の提示・書き換えはしません。\n"
    "入力はJSONで、facts(fact_id, text)と sentences(sid, text, before, after)です。"
    "before/afterは文脈で、判定対象ではありません。\n"
)

COMMON_OUT = (
    "\n出力はJSON1個のみ(前後に説明文を付けない):\n"
    '{"flags":[{"sentence_id":"<sid>","type":"<タイプ名>","fact_ids":["<fact_id>"],"confidence":0.0-1.0,'
    '"severity":"重大|非重大","question":"人間向けの確認質問を日本語1文"}]}\n'
    "Flagが無ければ {\"flags\":[]}。sentence_idとfact_idsは入力に存在するIDのみ使うこと。questionは1文で、"
    "断定せず『〜ではありませんか』の形で、どの語とどの語が食い違うかを示す。\n"
)

TYPE_DESC = {
    "rollback反転": (
        "【探す逸脱: rollback反転(動作の向きの反転)】台帳Factは停止・撤回・取り消し・ロールバック・無効化・中止など"
        "『元に戻す/やめる』側の出来事を述べているのに、文が復元・再導入・再開・復活・元に戻した(機能や制度が戻った、動いている)"
        "と読める場合。逆(台帳が再開・復元で、文が停止・撤回)も対象。"
        "『rollback』『以前の状態に戻した』のような、どちらの意味にも読める語を文が台帳の言葉を使わず言い換えている場合も、"
        "読者が逆向きに受け取りうるならFlag。台帳と同じ向きが明確な文(例: put on hold/取りやめた)はFlagしない。"),
    "主体対象入替": (
        "【探す逸脱: 主体対象入替】台帳Factの『誰が/何が』『誰に/何を』『どの範囲(定義と発表内容など)』が、文で入れ替わっている、"
        "または別の主体・対象・種類・定義に差し替わっている場合。例: 定義を発表内容として述べる、AがBにした→BがAにした、"
        "一部の事例→全体。語の言い換えだけで意味が同じならFlagしない。"),
    "否定反転": (
        "【探す逸脱: 否定反転】台帳Factが肯定(した・ある・認めた)なのに文が否定(しなかった・ない)、またはその逆。"
        "二重否定・『〜とは限らない』『〜しているわけではない』など否定の範囲が台帳と変わっている場合も対象。"
        "台帳が否定していることを文が同じく否定しているだけならFlagしない。"),
    "数量時系列": (
        "【探す逸脱: 数量時系列】台帳Factの数値・割合・件数・金額・日付・順序・期間・『初めて/以前/〜まで』が、文で変わっている・"
        "盛られている・丸められすぎている・台帳にない数値や時期が加わっている場合。"
        "単位換算や自然な丸め(約・およそ付き)で意味が変わらないならFlagしない。"),
    "不在断定": (
        "【探す逸脱: 不在断定】文が『〜はない/〜されていない/誰も〜していない/まだ公表されていない/一度もない』など"
        "『存在しない・未公表・起きていない』を断定しているが、台帳にその不在を明示する記述がない、または台帳に"
        "それと矛盾する記述(起きた事実)がある場合。台帳Factが不在を明示していて文がそれを写しているだけならFlagしない。"
        "台帳に載っていないだけでは不在の根拠にならない点に注意。"),
}


def d1_system(typ):
    assert typ in TYPE_DESC
    return (COMMON_HEAD + "あなたの役割は次の1タイプだけを探すことです。他のタイプの逸脱は無視してください。\n"
            + TYPE_DESC[typ] + "\n出力のtypeは必ず「" + typ + "」。severityは、読者に事実と逆・別の意味を与えるなら『重大』、"
            "ニュアンスの違いにとどまるなら『非重大』。確信が低くても重大の可能性があるものは出す。" + COMMON_OUT)


def d2_system():
    return (COMMON_HEAD + "あなたの役割は、台帳Factと食い違って読者に誤った事実を伝えうる『重大』な箇所だけを列挙することです。"
            "軽微な言い換え・省略・表現の硬さ・文体の問題は出さないでください。重大候補の例: "
            + " / ".join(TYPES) + "(各タイプの定義: 動作の向きの反転、主体や対象や範囲の入替、肯定否定の反転、"
            "数値・日付・順序の変更、台帳にない不在の断定)。typeには上の5つのいずれか、当てはまらなければ『その他』。"
            "severityは常に『重大』。" + COMMON_OUT)


def build_user(unit, facts_override=None, sentences_override=None):
    """LLMへ渡す入力。ラベル・Checker参考判定・context_source等は一切渡さない。"""
    import json
    facts = facts_override if facts_override is not None else unit["facts"]
    sents = sentences_override if sentences_override is not None else unit["sentences"]
    return json.dumps(dict(
        facts=[dict(fact_id=f["fact_id"], text=f["text"]) for f in facts],
        sentences=[dict(sid=s["sid"], text=s["text"], before=s.get("before", ""), after=s.get("after", "")) for s in sents],
    ), ensure_ascii=False)
