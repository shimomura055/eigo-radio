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
