# -*- coding: utf-8 -*-
"""Sonnet(実行層)による全候補の実読判定(『修正せずにそのまま選べるか』)。Fable実読用の一次判定であり、最終の独立受入はFable。
NG に載っていない候補は『選択可』。reasonは不可の主因。LOW は選択可だが難易度が低め(難易度優先の観点で注意)。
判定基準: ①一般化が適切(本文固有語が残らない/必要語が欠けない) ②本文での意味を保持 ③日本語意味と整合 ④塊としての学習価値(自由な組合せ=F・単語のみ=Wは不可)
⑤難易度(基本語のみで字面どおり=不可) ⑥英語として自然。
判定を行った時点で、本Trialの必須9例の評価も別途 REQUIRED 表に記録する。"""

NG = {
    "untidi_a2": {
        "Before": {"hear it out": "代名詞itが未一般化(hear someone out)", "take points away from": "未一般化(take something away from)",
                   "make life work": "未一般化(make something work)", "need another look": "自由な組合せ・易しい"},
        "A_luna": {"turn something into": "易しい・塊価値が弱い", "take up": "過一般化(spaceを落とし語義が不明)"},
        "D_luna": {"hear something out": "somethingは不自然(someone)", "rely on": "易しい(基本の前置詞付き動詞)"},
    },
    "untidi_b1b": {
        "Before": {"apply to every household": "本文固有語が残る", "turn into an interrogation": "自由な組合せ", "hear it out": "代名詞itが未一般化",
                   "the participant's own explanation": "自由な名詞句", "what it helps with": "節の断片", "demand its removal": "自由な組合せ・未一般化",
                   "Now in Session": "Nowが残る(本文固有)"},
        "A_luna": {}, "D_luna": {},
    },
    "ai_cha_a2": {
        "Before": {"confirm a clear fall": "自由な組合せ(ユーザー例)", "results suggest": "自由な組合せ", "favor one product": "未一般化・自由な組合せ",
                   "let the advice through": "未一般化(let something through)"},
        "A_luna": {"open for business": "字面どおり(看板文言)", "after all": "易しい"},
        "D_luna": {},
    },
    "ai_cha_b1b": {
        "Before": {"whose interests the conversation serves": "節の断片・未一般化", "confirm a clear drop": "自由な組合せ", "rate at which": "断片・塊でない",
                   "or so it seemed": "時制が未原型化(or so it seems)"},
        "A_luna": {}, "D_luna": {"need an instruction manual": "自由な組合せ(比喩だが辞書的な塊でない)"},
    },
    "jwst_m_a2": {
        "Before": {"a lower limit": "冠詞・自由な組合せ", "narrow down the source": "未一般化(narrow down)", "turn the usual steps around": "未一般化(turn something around)",
                   "line's absence from images": "本文固有の名詞句", "show up": "易しい"},
        "A_luna": {"set a lower limit": "lowerが残り未一般化"}, "D_luna": {},
    },
    "jwst_m_b1b": {
        "Before": {"narrow down the source": "未一般化(narrow down)", "set a lower limit": "lowerが残り未一般化", "point-like object": "自由な組合せ・汎用性なし"},
        "A_luna": {"set a lower limit on": "lowerが残り未一般化・末尾前置詞onは余計"},
        "D_luna": {"set a limit": "lowerを落とし語義(下限)が失われる", "take a turn": "unexpectedを落とし語義が変わる(take an unexpected turn → take a turn)",
                   "point-like object": "自由な組合せ・汎用性なし", "deep image": "自由な組合せ", "have yet to be spoken": "受動形が残り塊でない"},
    },
    "meta_w_a2": {
        "Before": {"At the time of writing": "未一般化(at the time of)・大文字残り", "side by side": "易しい(字面どおり)", "early step toward": "earlyが残る自由な組合せ",
                   "gaps in a busy day": "自由な名詞句"},
        "A_luna": {"at the time of writing": "未一般化(at the time of)", "turn into": "易しい"},
        "D_luna": {},
    },
    "meta_w_b1b": {
        "Before": {"by the time of reporting": "未一般化・本文固有語", "in the gaps": "断片・自由な組合せ"},
        "A_luna": {"by the time of": "不自然(固定表現として成立しない)"}, "D_luna": {},
    },
    "aiisland_b1b": {
        "Before": {"look at separately": "自由な組合せ"}, "A_luna": {}, "D_luna": {},
    },
    "surname_b1b": {
        "Before": {"way out in the country": "自由な組合せ"},
        "A_luna": {"let go of": "意味が具体的すぎ(人への執着)", "way out in the country": "自由な組合せ"},
        "D_luna": {},
    },
    "melos_a2": {
        "Before": {"without asking for another promise": "節の断片・未一般化", "lose one's trust in someone": "末尾のsomeoneが残る・意味説明が不自然",
                   "win such trust": "suchが未一般化"},
        "A_luna": {"lose one's life": "易しい・自由な組合せ寄り"}, "D_luna": {},
    },
    "ignobel_a2": {
        "Before": {"Take a number alone": "未一般化(thatが残る/不自然)", "packed with nutrition": "未一般化(packed with)"},
        "A_luna": {}, "D_luna": {"protein crystal": "専門の自由な組合せ"},
    },
    "ignobel_b1b": {
        "A_luna": {"on its own": "未一般化(on one's own)", "turn into": "易しい"}, "D_luna": {},
    },
    "tesla_b1b": {
        "A_luna": {}, "D_luna": {"hurdle to clear": "単数化で不自然(hurdles to clear)・塊として弱い"},
    },
}

# 選択可だが難易度が低め(難易度優先の観点で注意)。件数集計には影響しない
LOW = {
    "untidi_b1b": {"A_luna": ["take something seriously", "apply to", "on the job"], "D_luna": ["apply to", "on the job", "speak for"]},
    "ai_cha_a2": {"A_luna": ["after all"]},
    "jwst_m_a2": {"A_luna": ["pick something up"]},
    "meta_w_a2": {"A_luna": ["when it comes to"]},
    "meta_w_b1b": {"A_luna": ["when it comes to", "skip over"]},
    "surname_b1b": {"Before": ["overlap with"]},
    "ignobel_a2": {"Before": ["on hold"], "A_luna": ["on hold"]},
    "ignobel_b1b": {"A_luna": ["on hold"], "D_luna": ["serve as"]},
}

# 必須9例(ユーザー提示)の最終判定: (対象表現, 望ましい方向, 判定欄 dict[method]=(結果の表示 or None, OK?, コメント))
REQUIRED = [
    {"id": "G1", "kind": "一般化", "input": "take points away from", "target": "take something away from", "case": "untidi_a2/b1b",
     "Before": ("take points away from", False, "未一般化"),
     "A_luna": ("a2:選定なし / b1b: take something away from", True, "b1bで達成。a2では選定されず(1/2)"),
     "D_luna": ("選定なし(a2/b1bとも)。一般化段の単体test: take points away from", False, "選定段でFree combination判定。単体でも名詞をCOREに残す(モデルが比喩語義に必要と判断)")},
    {"id": "G2", "kind": "一般化", "input": "make life work", "target": "make something work", "case": "untidi_a2",
     "Before": ("make life work", False, "未一般化"),
     "A_luna": ("選定なし", False, "自由な組合せ判定で落ちた"),
     "D_luna": ("選定なし(F判定)。一般化段の単体test: make something work", True, "選定段ではFree combinationとして不採用。一般化単体では達成(改訂規則後)")},
    {"id": "G3", "kind": "一般化", "input": "at the time of writing", "target": "at the time of", "case": "meta_w_a2",
     "Before": ("At the time of writing", False, "未一般化"),
     "A_luna": ("at the time of writing", False, "未一般化(モデルがwritingを核に残す)"),
     "D_luna": ("at the time of", True, "達成(トークン分類+別系列検証でwritingを除去、glossも〜の時点でへ)")},
    {"id": "G4", "kind": "一般化", "input": "narrow down the source", "target": "narrow down", "case": "jwst_m_a2/b1b",
     "Before": ("narrow down the source", False, "未一般化"),
     "A_luna": ("narrow something down", True, "達成(somethingを足した標準形。目的語省略の核形ではないが辞書見出し)"),
     "D_luna": ("narrow down", True, "達成(a2/b1b)")},
    {"id": "G5", "kind": "一般化", "input": "turn the usual steps around", "target": "turn something around(語義: 順序を逆にする)", "case": "jwst_m_a2",
     "Before": ("turn the usual steps around", False, "未一般化"),
     "A_luna": ("turn something around / 手順などを逆にする", True, "達成・語義保持"),
     "D_luna": ("turn something around / 何かを逆の順序にする", True, "達成・語義保持")},
    {"id": "V1", "kind": "学習価値", "input": "confirm a clear fall(drop)", "target": "原則NG(自由な組合せ)", "case": "ai_cha_a2/b1b",
     "Before": ("提示されている", False, "自由な組合せがそのまま提示"),
     "A_luna": ("提示されない", True, "除外"), "D_luna": ("提示されない", True, "除外(F判定)")},
    {"id": "V2", "kind": "学習価値", "input": "make room for", "target": "良い候補(提示される)", "case": "meta_w_a2/b1b",
     "Before": ("make room for", True, "提示"), "A_luna": ("make room for", True, "提示"), "D_luna": ("make room for", True, "提示")},
    {"id": "V3", "kind": "学習価値", "input": "blow a whistle", "target": "良い候補(提示される・語義区別)", "case": "ai_cha_a2",
     "Before": ("blow a whistle / 警報を鳴らす", True, "提示"), "A_luna": ("提示されない", False, "選定されず(単一callでは脱落)"),
     "D_luna": ("blow a whistle / 危険を知らせる合図を出す", True, "提示。chunk_reasonに比喩(笛=警告)を明記")},
    {"id": "V4", "kind": "学習価値", "input": "sales pitch", "target": "良い候補(提示される)", "case": "ai_cha_a2/b1b",
     "Before": ("sales pitch", True, "提示"), "A_luna": ("sales pitch", True, "提示"), "D_luna": ("sales pitch", True, "提示")},
]
