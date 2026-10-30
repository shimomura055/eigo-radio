# -*- coding: utf-8 -*-
"""Sonnet(実行層)の実読判定の記録先(委任_02で記入)。最終の独立受入はFable。
形式: MAN[arm][case][display_form] = (code, 理由)。記載のない候補は『修正せずにそのまま選べる(OK)』。
JUDGED = {(arm, case)}: 実読済みのケース(未実読は集計に『未判定』と明記し、OK扱いにしない)。
コード(主評価と対応):
  FREE : 自由な組合せ(塊でない。形容詞+名詞・専門名詞句・一回限りの比喩を含む)
  GEN  : 一般化の失敗(未一般化/過一般化/時制・語形/受動形残り/somethingとsomeoneの取違え/修飾語の過不足)
  MEAN : 意味・用法の不正確(語義が変わる/gloss不整合)
  NAT  : 英語として不自然(見出し形として不自然)
  OTHER: その他
注: 易しい表現(rely on等)は本Trialでは不可の理由にしない(ユーザー方針)。難易度は参考分布として別集計。"""
CODES = ["FREE", "GEN", "MEAN", "NAT", "OTHER"]

MAN = {}        # 委任_02で記入
JUDGED = set()  # 委任_02で記入

# ---- 前回(方式D=Before基準)の判定を新基準のコードへ再分類(TRIAL-01 kpg01_manual.NG['D_luna']の理由に基づく)。
# 易しいだけの理由(rely on)は不可としない(OK扱い)。明示override: (case, 表示形) -> コード or None(=OK)
D_OVERRIDE = {
    ("untidi_a2", "hear something out"): "GEN",               # 人称(someone)の取違え
    ("untidi_a2", "rely on"): None,                           # 易しいだけ=本Trialでは不可としない
    ("ai_cha_b1b", "need an instruction manual"): "FREE",
    ("jwst_m_b1b", "set a limit"): "MEAN",                    # lower(下限)を落とし語義喪失
    ("jwst_m_b1b", "take a turn"): "MEAN",                    # unexpectedを落とし語義が変わる
    ("jwst_m_b1b", "point-like object"): "FREE",
    ("jwst_m_b1b", "deep image"): "FREE",
    ("jwst_m_b1b", "have yet to be spoken"): "GEN",           # 受動形が残る
    ("ignobel_a2", "protein crystal"): "FREE",
    ("tesla_b1b", "hurdle to clear"): "NAT",                  # 単数化で不自然・塊として弱い
}

# ---- 委任_02 P1: Sonnet実読(E1L/E2/E3 ×14ケース、2026-10-30)。記載なし=OK。
ALL14_ = ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b", "ai_cha_a2", "meta_w_a2", "aiisland_b1b", "surname_b1b",
          "melos_a2", "ignobel_a2", "ignobel_b1b", "tesla_b1b"]
_E2NG = {
    "untidi_b1b": {"hear something out": ("GEN", "人称: itは話し手(人)=hear someone out")},
    "jwst_m_a2": {"lower limit": ("FREE", "形容詞+名詞の描写的組合せ"), "absence from": ("FREE", "名詞+前置詞の自由な組合せ")},
    "jwst_m_b1b": {"drop something": ("FREE", "動詞+目的語の字面どおり"), "absence from": ("FREE", "名詞+前置詞の自由な組合せ")},
    "meta_w_a2": {"storage space": ("FREE", "名詞+名詞の描写的組合せ")},
}
MAN["E1L"] = {
    "untidi_a2": {"hear something out": ("GEN", "人称取違え"), "take away from": ("GEN", "take points away fromの一般化失敗(別句動詞に変質)")},
    "untidi_b1b": {"hear something out": ("GEN", "人称取違え")},
    "jwst_m_a2": {"take a turn": ("MEAN", "unexpectedを落とし語義変質"), "lower limit": ("FREE", "形容詞+名詞")},
    "jwst_m_b1b": {"set a limit": ("MEAN", "lowerを落とし語義喪失"), "take a turn": ("MEAN", "unexpectedを落とし語義変質")},
    "meta_w_a2": {"storage space": ("FREE", "名詞+名詞")},
    "surname_b1b": {"can't help think": ("GEN", "can't help thinkingが正。語形崩れ")},
}
MAN["E2"] = {k: dict(v) for k, v in _E2NG.items()}
MAN["E3"] = {k: dict(v) for k, v in _E2NG.items()}
JUDGED |= {(a, c) for a in ("E1L", "E2", "E3") for c in ALL14_}

# 委任_02: E側でlower limit/absence fromを専門的・描写的組合せとしてFREEと判定したため、Dにも同一基準を適用(基準の非対称を除去)。
D_OVERRIDE[("jwst_m_a2", "equivalent width")] = "FREE"   # 専門分野の記述的名詞句(deep image型)
D_OVERRIDE[("jwst_m_b1b", "equivalent width")] = "FREE"

# ---- 委任_02 P2: E4(難所6ケース)/E1S(4ケース)実読
HARD6_ = ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b"]
MAN["E4"] = {"untidi_a2": {"hear something out": ("GEN", "人称取違え")}, "untidi_b1b": {"hear something out": ("GEN", "人称取違え")}}
MAN["E1S"] = {"untidi_a2": {"hear something out": ("GEN", "人称取違え")},
              "jwst_m_a2": {"take a turn": ("MEAN", "unexpectedを落とし語義変質")},
              "jwst_m_b1b": {"set a lower limit": ("FREE", "未一般化の描写的組合せ"), "take a turn": ("MEAN", "unexpectedを落とし語義変質")}}
JUDGED |= {("E4", c) for c in HARD6_}
JUDGED |= {("E1S", c) for c in ("untidi_a2", "jwst_m_b1b", "ai_cha_b1b", "jwst_m_a2")}

# ---- 委任_02 P3: E4 残り8ケース実読(NG0件)
JUDGED |= {("E4", c) for c in ("ai_cha_a2", "meta_w_a2", "aiisland_b1b", "surname_b1b", "melos_a2", "ignobel_a2", "ignobel_b1b", "tesla_b1b")}
