# -*- coding: utf-8 -*-
"""Sonnet実読判定の記録先(委任_02以降で記入)と、新評価軸(2軸分離)のコード定義。最終の独立受入はFable。
形式: MAN[arm][case][表示形] = (code, 理由)。記載なし=『修正せずそのまま選べる(○)』。JUDGED={(arm,case)}=実読済み(未実読はOK扱いにしない)。
arm='PROD'は現行Production(保存済み候補doc)。表示形=Productionでは used_form。

【2軸分離(ユーザー原文§5「本文と同じ意味・用法を保持しているか」と「一般形として自然か」を分けて評価)】
 軸S(意味・用法の保持) : 一般形が本文と同じ語義・同じ構文・同じ項タイプの見出しか
   SENSE_SHIFT  : 別の語義の見出しになった(take points away from[減点する] -> take away from[損なう])
   ARG_TYPE     : someone/something(one's/someone's)が見出しの標準用法に合わない(hear it out -> hear something out。見出しの標準は人)
   FRAME_SHIFT  : 構文の枠が変わった(目的語・前置詞/粒子の脱落で語義が不定になる: take up space -> take up)
   MOD_SHIFT    : 修飾語の除去で語義が変わった(break new ground -> break ground)。**意味を損なわない修飾語除去はNGにしない**(set a lower limit -> set a limit等)
   GLOSS_MISMATCH: 日本語の意味が一般形と合わない(除いた修飾語・目的語の意味を含む、または別見出しの訳)
 軸N(一般形としての自然さ・汎用性) :
   NAT          : 英語として不自然(語形崩れ can't help think、冠詞欠落等) / OVER_GEN: 過度の一般化で学習価値が消える / UNDER_GEN: 本文固有語が残る
 軸F(選定): FREE=自由な組合せ(塊でない)。 OTHER。
 コードは優先順位 S(SENSE_SHIFT>ARG_TYPE>FRAME_SHIFT>MOD_SHIFT>GLOSS_MISMATCH) > FREE > N > OTHER で最も主要な1つを付ける(重大NG=S軸)。
 判定が割れる境界例(擬人化・慣用の固定it・語義が複数ある句動詞)は、辞書(学習者用英英辞書)の見出し・用例を根拠に理由欄へ書く。"""
CODES_S = ["SENSE_SHIFT", "ARG_TYPE", "FRAME_SHIFT", "MOD_SHIFT", "GLOSS_MISMATCH"]
CODES_N = ["NAT", "OVER_GEN", "UNDER_GEN"]
CODES = CODES_S + ["FREE"] + CODES_N + ["OTHER"]
LABEL_JA = {"SENSE_SHIFT": "本文と別の語義になっている", "ARG_TYPE": "人/物(someone/something)の選択が見出しの標準用法と合わない", "FRAME_SHIFT": "構文の枠(目的語・前置詞)が変わり語義が不定",
            "MOD_SHIFT": "修飾語の除去で語義が変わった", "GLOSS_MISMATCH": "日本語の意味が一般形と合わない", "FREE": "自由な組合せ(塊として覚える価値が薄い)",
            "NAT": "英語として不自然", "OVER_GEN": "一般化しすぎて学習価値が消えた", "UNDER_GEN": "本文固有の語が残っている", "OTHER": "その他"}

MAN = {}        # 委任_02以降で記入
JUDGED = set()  # 同上

# ---- P0再監査の種(API 0): TRIAL-02 kpg03_manual.pyのSonnet実読ラベルを新定義へ読み替えた結果。
# 新定義での読み替え: 旧GEN『人称取違え』(hear something out)=ARG_TYPE、旧GEN『別句動詞に変質』(take away from)=SENSE_SHIFT。
# 旧MEAN『unexpected/lowerを落とし語義変質』(take a turn / set a limit)は、原文§2-Cにより『意味を損なわない修飾語除去』として許容(日本語の意味が一般形の語義であることのみ確認)。
RECODE_02 = {
    "hear something out": "ARG_TYPE",
    "take away from": "SENSE_SHIFT",
    "take a turn": None, "set a limit": None,      # 許容へ変更(gloss検査のみ)
}
# 旧基準でのNG件数(kpg03_work/stats_14.txt)と新定義での意味・用法NG件数(S軸)。旧→新: 件数はTRIAL-02 MANからの手集計。
BASELINE_S_AXIS_02 = {   # (S軸NG件数, 提示数)。出典=kpg03_manual.py MAN[...]とkpg03_work/stats_14.txt
    "D": (1, 71), "E1L": (3, 81), "E2": (1, 77), "E3": (1, 77), "E4": (2, 70)}
