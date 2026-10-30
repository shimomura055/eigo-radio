# -*- coding: utf-8 -*-
"""Sonnet(実行層)による方式D'の全候補の実読判定(『修正せずにそのまま選べるか』)。基準はkpg01_manual.pyと同一
(一般化適切・意味保持・gloss整合・塊価値・難易度優先・英語として自然)。NGに載っていない候補は『選択可』。
最終の独立受入はFable。Before/A/Dの判定はkpg01_manual.pyを参照。"""
NG = {
    "untidi_a2": {"need another look": "自由な組合せ・易しい", "rely on": "易しい(基本の前置詞付き動詞)", "turn something into": "易しい・塊価値が弱い",
                  "take up": "易しい・語義が不明確(alt)"},
    "untidi_b1b": {"hear something out": "somethingは不自然(someone)", "rely on": "易しい", "take points away": "from欠落・pointsが残り未一般化",
                   "turn into": "易しい(alt)", "help with": "易しい(alt)"},
    "ai_cha_a2": {"need an instruction manual": "自由な組合せ(比喩だが辞書的な塊でない)"},
    "ai_cha_b1b": {"or so it seemed": "時制が未原型化(or so it seems)"},
    "jwst_m_a2": {"deep image": "自由な組合せ", "lower limit": "自由な組合せ寄り・易しめ"},
    "jwst_m_b1b": {"set a lower limit": "lowerが残り未一般化(語義保持とのトレードオフ)", "rely on": "易しい", "pick up": "易しい・日本語意味(拾い上げる)が不整合"},
    "meta_w_a2": {"early step toward": "earlyが残る自由な組合せ"},
    "meta_w_b1b": {"early step toward": "earlyが残る自由な組合せ"},
}
LOW = {"meta_w_a2": ["make time for"], "untidi_b1b": ["take something seriously"]}
# 必須9例のD'判定: id -> (結果の表示, OK?, コメント)
REQUIRED2 = {
    "G1": ("take something away from(untidi_a2のmain、gloss『〜から差し引く』)", True, "達成(a2)。b1bは選定されたが『take points away』でfrom欠落・未一般化(alt生成なし)。1/2"),
    "G2": ("make something work(untidi_a2 main)", True, "達成。塊判定2回和集合で一方のpassがC判定→一般化段で達成"),
    "G3": ("at the time of", True, "達成"),
    "G4": ("narrow down(a2/b1b)", True, "達成"),
    "G5": ("turn something around / 何かを逆の順序にする", True, "達成・語義保持"),
    "V1": ("提示されない", True, "除外(F判定、2回とも)"),
    "V2": ("make room for(meta_w a2/b1b)", True, "提示"),
    "V3": ("blow a whistle / 警戒の合図を出す", True, "提示(2passのうち1passがF→和集合で維持。D'初回のeasy veto方針では脱落、veto条件をC判定のeasyに限定して回復)"),
    "V4": ("sales pitch(a2/b1b)", True, "提示。b1bは複数形lemma補正(sale/sales)で脱落を解消"),
}
