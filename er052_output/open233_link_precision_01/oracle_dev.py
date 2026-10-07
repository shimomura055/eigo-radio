# -*- coding: utf-8 -*-
"""T3 oracle(dev): 既知NG項目 -> EN unit の人手(Claude)マッピング。r3出力を見る前に確定(事前登録 3節)。
located=Trueの項目のみ(a)の分母。fact_id=None(評価JSONにfact無し)は(a)分母外、(c)の「リンクなし期待」側に使う。
src: 'main'=replay対象22 run、'b3x'=step3のためだけに追加したB3 trial 3記事(各1回、(a)主集計には入れず別掲)。"""
# (item_id, run suffix key, [unit ids], note)
MAIN = [
 ("ai_control-jb9k-n1", "control_checker_polysemy_trial_01/runs/ai_control/control/rep1", ["S7.2"]),
 ("ai_control-jb9k-n2", "control_checker_polysemy_trial_01/runs/ai_control/control/rep1", ["S7.3"]),
 ("ai_control-jb9k-n3", "control_checker_polysemy_trial_01/runs/ai_control/control/rep1", ["S7.4"]),
 ("ai_control-jb9k-n4", "control_checker_polysemy_trial_01/runs/ai_control/control/rep1", ["S8.1"]),
 ("ai_control-jb9k-n5", "control_checker_polysemy_trial_01/runs/ai_control/control/rep1", ["S5.1"]),
 ("hormuz-cv85-p1", "control_checker_polysemy_trial_01/runs/hormuz/control/rep1", ["S3.1"]),
 ("hormuz-cv85-p2", "control_checker_polysemy_trial_01/runs/hormuz/control/rep1", ["S10.2"]),
 ("hormuz-d5qr-p1", "control_checker_polysemy_trial_01/runs/hormuz/control/rep2", ["S9.3"]),
 ("hormuz-d5qr-p2", "control_checker_polysemy_trial_01/runs/hormuz/control/rep2", ["S2.2"]),
 ("meta-249j-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep10", ["S7.1"]),
 ("meta-249j-p1", "control_checker_polysemy_trial_01/runs/meta/nb/rep10", ["L1"]),
 ("meta-2xhw-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep8", ["S8.2"]),
 ("meta-2xhw-n2", "control_checker_polysemy_trial_01/runs/meta/nb/rep8", ["S6.1"]),
 ("meta-cz6g-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep4", ["S7.1"]),
 ("meta-daju-n2", "control_checker_polysemy_trial_01/runs/meta/nb/rep9", ["S5.2"]),
 ("meta-daju-p1", "control_checker_polysemy_trial_01/runs/meta/nb/rep9", ["S5.1"]),
 ("meta-ggp4-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep5", ["S6.2"]),
 ("meta-gj99-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep3", ["S6.2"]),
 ("meta-n6vy-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep1", ["S9.2"]),
 ("sewer-qrfc-n1", "control_checker_polysemy_trial_01/runs/sewer/control/rep1", ["S9.1", "S9.4"]),
 ("ai_control-cfqm-n1", "polysemy_trial_04/runs/ai_control/control/rep1", ["S4.4"]),
 ("ai_control-cupe-n1", "allfact_note_e2e_02/runs/ai_control/nb/p2/rep2", ["S9.3"]),
 ("hormuz-j7gv-n1", "allfact_note_e2e_02/runs/hormuz/nb/p2/rep2", ["S4.2"]),
 ("hormuz-j7gv-p2", "allfact_note_e2e_02/runs/hormuz/nb/p2/rep2", ["S9.3"]),
 ("meta-7aqr-n1", "polysemy_trial_04/runs/meta/control/rep1", ["S6.1"]),
 ("sewer-4hgy-p1", "polysemy_trial_04/runs/sewer/control/rep1", ["T"]),
 ("sewer-g8qg-n1", "allfact_note_e2e_02/runs/sewer/nb/p2/rep2", ["S4.1", "S8.4"]),
 ("space_weapons-bcgj-n1", "polysemy_trial_04/runs/space_weapons/control/rep1", ["S4.1"]),
 ("space_weapons-bcgj-n3", "polysemy_trial_04/runs/space_weapons/control/rep1", ["S5.5"]),
]
# 未特定(ENに該当文が無い/R0限定): 理由
UNLOCATED = {
 "ai_control-jb9k-p1": "EN該当文を特定できず", "ai_control-cupe-p1": "台帳曖昧・EN特定不可", "meta-daju-n1": "R0のみ(ENでは弱まる)",
 "sewer-cqsu-n1": "R0のみ", "sewer-cqsu-p1": "R0のみ", "sewer-qrfc-p1": "EN特定不可", "space_weapons-kfuf-p1": "EN特定不可",
 "space_weapons-bcgj-n2": "R0のみ(ENは緩和)", "hormuz-byz5-n1": "R0のみ", "hormuz-byz5-p1": "EN特定不可", "hormuz-byz5-p2": "EN特定不可",
 "hormuz-j7gv-p1": "EN特定不可", "hormuz-j7gv-p3": "EN特定不可", "meta-7aqr-p1": "EN特定不可", "meta-a5te-p1": "R0のみ",
 "meta-a5te-p2": "EN特定不可", "sewer-4hgy-n1": "R0のみ", "sewer-g8qg-p1": "EN特定不可",
}
# step3専用: B3 trial記事(Stage1ログ無し)。run_dir = er052_output/open233_b3_trial_01/runs/<key>
B3X = [
 ("hormuz-cdwb-n1", "hormuz/nb/V6/b1/w1", ["S4.1"]),
 ("hormuz-cdwb-n2", "hormuz/nb/V6/b1/w1", ["S10.2"]),
 ("hormuz-cf8v-n2", "hormuz/nb/V1/b1/w1", ["S4.3"]),
 ("space_weapons-637f-n1", "space_weapons/nb/V3/b2/w1", ["S4.3"]),
 ("space_weapons-637f-n2", "space_weapons/nb/V3/b2/w1", ["S9.1"]),
]
