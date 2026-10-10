# -*- coding: utf-8 -*-
"""Separate-call腕(Trial専用・Production不変更)。数値ランクだけを別callで出す。
入力=Storyline+採用Fact(ID・Fact本文・numeric_value・date_or_period のみ。制約欄は渡さない)。出力=number_ranks。
手順6の定義はD-plus-single-callと逐語同一(比較条件を揃えるため)。"""
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3r2_rank_01 as RK
B1 = RK.B1

DEVELOPER_MESSAGE = (
    "あなたはNews記事の数値整理を行うEditorです。採用済みFactの本文に書かれている数字・日付の表記を洗い出し、"
    "中核(core)か周辺(peripheral)かを規則に従って分類してください。記事本文は書きません。Factの採否やStorylineは変更しません。"
)

# 手順6本文(D-plus-single-callと逐語同一。b3r2_make_dplus_01.py がこの定数を取り込む=単一ソース。driverがsha一致をassert)
# 委任_02 A3: 仕様3-5-2の代替規則(欄が台帳に1件も無い場合のみFact本文で比べる)と概念(仕様3-3: 同じFactの中で主数字と単位が同じ表記)を反映
STEP6_RULES = (
    "- surface: 数字・単位・「約」「超」などのヘッジ語まで含めた形で、Fact本文に書かれている通りに写してください(例: 約3.4％、2,300件超、7月13日)。Fact本文に無い数字、Ledgerの他の欄にしかない数字、別のFactの数字は書かないでください。数字を含まない表記は不要です。\n"
    "- kind: magnitude(量・割合・金額・件数など)/date_time(月を含む日付・時刻・四半期)/range(範囲)/year(年だけ)/ordinal(第12回など識別子の序数)/name_embedded(名称の一部の番号)のどれか。\n"
    "- role: 次の順で決めてください。(a)year・ordinal・name_embeddedは常にperipheral。"
    "(b)量とrangeは、そのFactのnumeric_value欄の数字(numeric_scopeの括弧内を除く)に含まれるものだけがcore候補(Ledger全体にnumeric_value欄が1件も無い場合に限り、Fact本文の数字で比べる)。"
    "日付は、表記に月があり、そのFactのdate_or_period欄の先頭の日付と、表記にある年・月・日が全て一致するものだけがcore候補(Ledger全体にdate_or_period欄が1件も無い場合に限り、Fact本文の最初の日付で比べる。年だけ・日だけ・時刻だけ・四半期の表記は候補になりません)。"
    "(c)core候補を、Storylineに出る量、それ以外の量、日付の順に並べ(同じ順位ではFactの採用順・本文の出現順)、先頭から最大 max(3, min(6, floor(n/2))) 個をcore、残りと候補でないものをperipheralとする"
    "(nは量・range・日付の概念の総数。概念=同じFactの中で主数字と単位が同じ表記のまとまり。同じ概念の表記は全て同じroleにする)。迷ったらperipheral。\n"
)

USER_TEMPLATE = """以下は、あるテーマについて、中心Storylineと、そのStorylineのために採用済みのFactです。

【テーマ】
{topic}

【Storyline】
{storyline}

【採用Fact】
{facts_block}

あなたの仕事は次の1つです。
採用したFactそれぞれについて、そのFact本文(ID行の文)に書かれている数字・日付の表記を1つずつ洗い出し、number_ranksへ中核(core)か周辺(peripheral)の別とともに記載してください。
""" + STEP6_RULES + """
【出力】
JSON schemaの指示に従い、number_ranks(採用Factの数字・日付の表記ごとに fact_id・surface・kind・role)を出力してください。数字が1つも無い場合は空配列。

【重要】fact_idは、上記の採用Factに実在するもののみを使用してください。surfaceは当該Factのfact本文に実在する表記のみとしてください。"""

SCHEMA = {
    "name": "number_ranks_only",
    "schema": {
        "type": "object",
        "properties": {
            "number_ranks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fact_id": {"type": "string"},
                        "surface": {"type": "string"},
                        "kind": {"type": "string", "enum": ["magnitude", "date_time", "range", "year", "ordinal", "name_embedded"]},
                        "role": {"type": "string", "enum": ["core", "peripheral"]},
                    },
                    "required": ["fact_id", "surface", "kind", "role"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["number_ranks"],
        "additionalProperties": False,
    },
    "strict": True,
}


def facts_block(ledger_text, selected_ids):
    """採用Factの抜粋。ID行(claim)+numeric_value+date_or_period のみ(scope/conditions/制約は渡さない=役割分離と入力最小化)。"""
    facts, order = B1.parse_ledger(ledger_text)
    lines = []
    for fid in selected_ids:
        f = facts[fid]
        lines.append(f"{fid}: {B1.clean(f['claim'])}")
        if f.get("numeric_value"):
            lines.append(f"  numeric_value: {f['numeric_value']}")
        if f.get("date_or_period"):
            lines.append(f"  date_or_period: {f['date_or_period']}")
    return "\n".join(lines)


def build_payload(topic, storyline, ledger_text, selected_ids, model, effort):
    user = USER_TEMPLATE.format(topic=topic, storyline=storyline, facts_block=facts_block(ledger_text, selected_ids))
    return {"model": model, "reasoning": {"effort": effort}, "text": {"format": {"type": "json_schema", **SCHEMA}},
            "input": [{"role": "developer", "content": DEVELOPER_MESSAGE}, {"role": "user", "content": user}]}


def validate(parsed, ledger_text, selected_ids, storyline):
    """技術検証。D-plusと同一関数(validate_number_ranks)。"""
    return RK.validate_number_ranks(parsed.get("number_ranks"), ledger_text, selected_ids, storyline)
