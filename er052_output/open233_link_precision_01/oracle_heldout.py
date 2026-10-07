# -*- coding: utf-8 -*-
"""T3 oracle(held-out): dev確定(dev_summary.json)後に開いた。既知NG項目 -> EN unit の人手マッピング(r3出力を見る前に確定)。"""
MAIN = [
 ("ai_control-s9dk-n1", "control_checker_polysemy_trial_01/runs/ai_control/control/rep2", ["S5.4"]),
 ("meta-jdmu-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep6", ["S4.2"]),
 ("meta-jdmu-n2", "control_checker_polysemy_trial_01/runs/meta/nb/rep6", ["S6.1"]),
 ("meta-qvqc-n1", "control_checker_polysemy_trial_01/runs/meta/nb/rep2", ["S8.2"]),
 ("meta-qvqc-n2", "control_checker_polysemy_trial_01/runs/meta/nb/rep2", ["S7.2"]),
 ("meta-qvqc-n3", "control_checker_polysemy_trial_01/runs/meta/nb/rep2", ["T"]),
 ("meta-ua6f-n2", "control_checker_polysemy_trial_01/runs/meta/nb/rep7", ["S7.2"]),
 ("space_weapons-4mjq-n1", "control_checker_polysemy_trial_01/runs/space_weapons/control/rep1", ["S5.4"]),
 ("ai_control-b3ux-n1", "allfact_note_e2e_02/runs/ai_control/nb/p2/rep1", ["S5.5"]),
 ("ai_control-b3ux-p1", "allfact_note_e2e_02/runs/ai_control/nb/p2/rep1", ["S3.1"]),
 ("hormuz-h3rq-n1", "allfact_note_e2e_02/runs/hormuz/nb/p2/rep1", ["S5.2", "S7.2"]),
 ("hormuz-h3rq-p1", "allfact_note_e2e_02/runs/hormuz/nb/p2/rep1", ["S3.3"]),
 ("meta-475j-n1", "allfact_note_e2e_02/runs/meta/nb/p2/rep2", ["S9.3"]),
 ("space_weapons-89wf-n1", "allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2", ["S6.2"]),
 ("space_weapons-89wf-n2", "allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2", ["L1"]),
 ("space_weapons-89wf-n3", "allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2", ["S7.2"]),
]
UNLOCATED = {"meta-ua6f-n1": "EN特定不可", "meta-475j-p1": "EN特定不可", "sewer-87tc-p1": "R0のみ(R2/ENは『can be』で解消)"}
STEP3_TARGETS = [
 ("meta-475j-n1", "allfact_note_e2e_02/runs/meta/nb/p2/rep2", "S9.3"),
 ("space_weapons-89wf-n2", "allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2", "L1"),
]
