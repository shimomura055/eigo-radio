管理ID: JA-ASR-FALSE-NG-ROOT-FIX-02(新規。前身=JA-ASR-FALSE-NG-ROOT-CAUSE-01[OPEN-515/517/333]、FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03/04[R4/R3是正済み commit 930c31ff2])。本委任=委任_01B「課題B Phase 1: 既存方式の統一再評価+残NG原因分析+改善方式の設計案」。並行して別worker(委任_01A、PM管理不備調査、PM_AUDIT_*/RESULT_PACKET_JAFIX2A.mdのみ編集)が稼働中。ファイル範囲: docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/配下(PM_AUDIT_*を除く)、docs/pm/RESULT_PACKET_JAFIX2B.md、docs/pm/ACTIVE_TASK.md(新管理IDの行追加のみ)、delegation_log の _USER.md と本ファイル。Production code・SSOT編集禁止。Family A/B/Cには触れない。

(要旨。委任文全文はFableの起動プロンプトに存在。以下は主要規定の保存)
- 範囲: Phase 1=既存方式の統一再評価+残NG原因分析+改善方式の設計案まで。新方式のproto実装・新Trialは行わない(設計案をOpus条件Aレビュー後、委任_02)。既存protoの組合せ評価は可。
- 1. eval_unified_01.py(API 0、socket guard、2回実行でsha一致)。正例=6音声(run_ms_03 a1-a3, run_reselect_01 a1-a3)の保存済み全転写をwav sha256で紐付け。負例=N-1 150/N-3 30/合成55+17+19/OPEN333 sweep 8クラス・P-1負例/OPEN517負例/R4R3追加18/履歴43対/§4-3の6分類各最低3件(無い分類は合成追加・事前登録明記)。方式M0=現行Production HEAD最終判定、M1=v2、M2=β、M3=P-1(⊂v2注記)、M4=M1+M2、M5=他。PASS_WITH_WARNINGはPASSと別集計。出力EVAL_UNIFIED_01.md、事前にPREREGISTERED_01.md。
- 2. 残NG原因分析(reselect#3 スギノ、ms_03#1/#3 OpenAI数詞崩れ、詩は/氏は/市は/死は)。TTS発音ゆれ/ASR誤認識/判定規則不足に分類、再ASR12転写の分散を数値化。
- 3. DESIGN_PROPOSAL_01.md(候補i-v、推奨1案)、OPUS_REVIEW_REQUEST_01.md下書き。
- 4. RESULT_PACKET_JAFIX2B.md(20行以内)、ACTIVE_TASK行F追加、BUDGET_LOG_01.md、commit(自分のファイルのみadd、PM_AUDIT_*/RESULT_PACKET_JAFIX2A.md不可)、push origin HEAD:main。
- 費用: API 0原則、不足転写の補完はASR再実行のみ上限30円、事前にBUDGET_PLAN_01.md。
