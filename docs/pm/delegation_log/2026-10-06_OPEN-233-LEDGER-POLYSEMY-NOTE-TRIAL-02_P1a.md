# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 P1a (STOP at pre-call check, JPY0)
- meta: draft/verif Y, topic取得済, Control再構築=元txt一致(sha ea0ce587...)。
- sewer: draft/verif Y, topic取得済, Control一致(sha 42faae06...)。
- hormuz: draft/verif無し->--ledger-txt fallback。topic未取得(researcher record無し)。Control不一致(元txtのnumeric_value行10件が欠落、fallbackはnumeric_value/scope復元不可)。
- space_weapons: topic取得済(run_pipeline.py TOPIC_EN)。draft/verifはparsed抽出が必要(input_draft/verif.json)。Control不一致: 元txtはVERIFIED22件のみ、再構築はAMBIGUOUS F-022/F-023を追加(+2件)。
- ai_control: topic取得済。Control不一致: 元txtはVERIFIED16件のみ、再構築はAMBIGUOUS SPEC-001を追加(+1件)(EVID-003はREJECTED除外)。
- 有料call未実行(実費JPY0)。配置・diff・FREEZE未実施。STOP=固定台帳比較不成立。
