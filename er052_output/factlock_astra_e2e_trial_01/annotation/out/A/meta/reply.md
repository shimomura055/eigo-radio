=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
MetaはMuse経由の一部電話を訓練済み契約スタッフに担わせる人間コンシェルジュを試したが、従業員から機微情報共有への懸念が出るなか、適切な開示なしに始めたことをミスと認め、同機能を当面ロールバックした。

## Selected Facts
- 【事実1】MetaはMuse経由の電話の一部で、訓練を受けた人間の契約スタッフに電話をかけさせ、相手とのやり取りを完了させるテストを実施した。
- 【事実2】従業員は、電話中にユーザーの機微情報が契約スタッフへ意図せず共有される可能性を懸念した。
- 【事実3】MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを始めたことを「ミス」だったと認め、人間コンシェルジュ機能を当面ロールバックした。これは機能の試験に関する話であり、Muse全体の停止ではない。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "meta",
  "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "83c29bc213a7c8bd22000e04446dded2dce4c047b9273ae6575e260339fa22e0",
  "facts": [
    {"n": 1, "ledger_ids": ["MUSE-HC-006"]},
    {"n": 2, "ledger_ids": ["MUSE-HC-010"]},
    {"n": 3, "ledger_ids": ["MUSE-HC-012"]}
  ],
  "numbers": [],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "Selected Facts 第4文「これは機能の試験に関する話であり、Muse全体の停止ではない。」", "question": "限定文を別事実にするか、直前の事実3に含めるか", "options": ["別事実にする", "事実3に含める"], "chosen": "事実3に含める(台帳 MUSE-HC-012 の notes_for_writer に由来、同一ID)", "rule": "§2"},
    {"where": "本文全体", "question": "算用数字を含む表記が存在しない(漢数字のみの数量も無い)", "options": ["numbers を空にする"], "chosen": "numbers は空配列", "rule": "§3"}
  ]
}
=== SIDECAR_JSON_END ===
