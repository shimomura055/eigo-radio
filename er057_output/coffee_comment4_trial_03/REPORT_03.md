# REPORT_03 FAMILY-X-COFFEE-COMMENT4-MINIMAL-PROMPT-TRIAL-03
- 方針: Trial-01/02の大幅変更を置き換え、現行Comment 4 Promptへ2点のみ追加(In One Lineは番組最後の英語による要点整理/橋渡しは「続いて」より「最後に」)。差分は prompt_diff_03.md。
- 現行Prompt照合: `er019_family_x_audio_plan_01.FAMILY_X_A2_COMMENT_4_ROLE`(Production実定義)が Trial-02 prompt_baseline_current.md と一致することをscriptがassert済み。
- 実行: 同一入力(Coffee Std v4 parts)・同経路(trial_02流用、gpt-6-luna)で3 call。TTS/ASRなし。
- 実費: 3 call、JPY約0.168(cost_llm.json)。
- 結果: 3/3良好、VALIDATED。詳細 EVAL_03.md、全文 generations.jsonl、metrics.json。
- 状態: Production不変。採否はUSER_DECISION_REQUIRED(OPEN-316)。
