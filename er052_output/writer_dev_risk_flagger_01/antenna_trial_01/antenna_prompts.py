# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-ANTENNA-TRIAL-01 Antenna 1-6 system prompt。Trial/DEV専用(Production経路ではない)。
現行D2(prompts_flagger.d2_system())の構造を3区画に分け、(i)重大リスク定義 と (iii)出力形式 は6段階でバイト一致、
(ii)候補化条件のうち『最終段落(台帳どおりの文の扱い)』だけを段階化する。Antenna1 = 現行D2とバイト一致(assertで保証)。
detectors/ 配下は変更しない(importのみ)。件数指定・新しい事故タイプ・重大定義の変更・記事名/モデル名/既知例名の混入は禁止。
"""
import os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "detectors"))
import prompts_flagger as P

# --- (i)/(iii)/共通: 現行D2からそのまま取り出す(文言を一切変えない)
_ROLE = ("あなたの役割は、台帳Factと食い違って読者に誤った事実を伝えうる『重大』な箇所だけを列挙することです。")
_V1 = "軽微な言い換え・省略・表現の硬さ・文体の問題は出さないでください。"   # 重大/軽微の境界=重大定義の一部として固定
_DEF = ("重大候補の例: " + " / ".join(P.TYPES) + "(各タイプの定義: 動作の向きの反転、主体や対象や範囲の入替、肯定否定の反転、"
        "数値・日付・順序の変更、台帳にない不在の断定)。typeには上の5つのいずれか、当てはまらなければ『その他』。"
        "severityは常に『重大』。confidenceは正直に付けること: ")
_V2 = ("疑いが小さくても重大の可能性が少しでもあれば"
       "低めの確信度(0.1〜0.4)で出してよい(人間に見せるかどうかは後で確信度の閾値で決める)。")   # 確信度の方針も全段階で固定
_V3_A1 = "明らかに台帳どおりの文は出さない。"   # <- ここだけが段階ごとに変わる(最終段落S)

_CLOSING = ("\n出力件数に目標・下限・上限はありません。各文について『この文は人間に確認させる価値があるか』を自分で判断し、"
            "価値があると判断した文だけを出してください。該当する文が無ければ {\"flags\":[]} で構いません。")

_RANGE = {
    2: ("台帳どおりの文は出さない。候補にするのは、(a) 台帳と明確に食い違う文に加えて、(b) 台帳の言い換え・要約・一般化・範囲の広げ縮めによって、"
        "台帳が述べているより強い意味、または別の範囲・意味に読める文。"),
    3: ("(c) 台帳に対応するFactはあるが、数値・日付・固有名・主体・範囲・順序のどれかが台帳と一致しているか確認しきれない文。"
        "出すかどうか迷う場合は、出さない側ではなく出す側に倒し、確信度を低めに付ける。"),
    4: ("(d) 台帳のどのFactにも対応する記述が見つからない事実の主張(数値・日付・固有名・因果・理由・仕組み・不在・断定のいずれかを含む文)。"
        "食い違いまでは言えず台帳で確認できないだけの文は、確信度を低く付ける。対応するFactが無い場合、fact_idsは空配列でよい。"
        "(e) 注意書き(ambiguity_note、conditions、notes_for_writerなど)が付いたFactに関わる文で、その注意書きが落ちて断定的に読める文。"),
    5: ("(f) 事実を直接述べる文だけでなく、背景説明・仕組みの説明・一般論・まとめ・読者への呼びかけの文でも、台帳にない事実を前提または断定として含む文。"
        "一般常識として自然な説明でも、台帳にない事実を断定していれば候補にする。"),
    6: ("(g) 台帳から正誤を判断できない事実の主張を含む文は、重大度が低いと見込まれても、事実として誤りうるなら候補にする。"
        "文単独では問題がなくても、前後の文と合わせると台帳にない含意を読者に与える文も候補にする。"),
}

LEVEL_LABEL = {1: "Antenna 1(現行D2)", 2: "Antenna 2(少し広め)", 3: "Antenna 3(中程度)", 4: "Antenna 4(やや積極的)",
               5: "Antenna 5(高感度)", 6: "Antenna 6(非常に高感度)"}


def final_paragraph(level):
    """段階化される(ii)の最終段落。2以上は下位レベルの文を累積して含む(包含設計)。"""
    assert level in (1, 2, 3, 4, 5, 6)
    if level == 1:
        return _V3_A1
    return "".join(_RANGE[k] for k in range(2, level + 1)) + _CLOSING


def antenna_system(level):
    return (P.COMMON_HEAD + _ROLE + _V1 + _DEF + _V2 + final_paragraph(level) + P.COMMON_OUT)


def fixed_parts():
    """6段階でバイト一致すべき区画: (i)重大定義(+severity/type規定) と (iii)出力形式、COMMON_HEAD、_V1、_V2。"""
    return dict(head=P.COMMON_HEAD, role=_ROLE, v1=_V1, definition=_DEF, v2=_V2, out=P.COMMON_OUT)


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


assert antenna_system(1) == P.d2_system(), "Antenna1 must be byte-identical to current D2"

if __name__ == "__main__":
    import json
    out = {}
    for k in range(1, 7):
        s = antenna_system(k)
        out[k] = dict(sha256=sha(s), chars=len(s), final_paragraph_sha256=sha(final_paragraph(k)))
    out["d2_current_sha256"] = sha(P.d2_system())
    out["fixed_parts_sha256"] = {k: sha(v) for k, v in fixed_parts().items()}
    print(json.dumps(out, ensure_ascii=False, indent=2))
