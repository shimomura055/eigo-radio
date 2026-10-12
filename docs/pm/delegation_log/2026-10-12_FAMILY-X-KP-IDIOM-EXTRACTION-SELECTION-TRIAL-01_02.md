# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / 委任_02 (Phase B+C) 2026-10-12

- 範囲: Phase B(Trial実装、JPY0)+Phase C(Coffee v4 Std/Adv、有料、上限JPY20)。Phase Dは準備のみ(正解表案)。SSOT未編集、Production code/Prompt/DB/共有Template/共有canonicalization無変更(git diff空)。
- STOP確認: 作業開始時と各有料段(C1/C2/C3/C3R)の直前に `docs/pm/delegation_log/*STOP_NOTICE*`・`er064_output/.../STOP`・`er026_output/family_z_production_e2e_01/STOP_ALL` を確認。Melos案件(FAMILY-Z-MELOS-...)のSTOP_NOTICEが1件存在するが、該当管理IDは別案件であり本件対象外(本文に別案件の仕様変更停止と明記)。STOP/STOP_ALLは存在せず。外部停止・rc≠0の連続なし(rc≠0は構文エラーのimport失敗1回のみ、API呼出前、原因修正後に同一コマンドを再実行=有料runの再起動ではない)。
- 有料run: C1/C2/C3/C3R 各1回ずつのみ起動(自動再試行・監督ループ・別名ラッパなし)。C3R(重複NG3件へのProduction方式retry 1回確認)は委任のC1-C4に明記のない追加確認で、既存retry機構との整合確認(委任「厳守/安全性」)のため実施、JPY3.79。費用の累計はJPY14.44で上限20内。
- 使用モデル: gpt-6-luna(Production同一。PM_GOVERNANCE 25節の例外「Production比較可能性」を事前に採用)。
- 詳細は `er064_output/kp_idiom_trial_01/PHASE_BC_REPORT_01.md`。RESULT: `docs/pm/RESULT_PACKET_KP_IDIOM_01.md`。
- 発見事項(実装せず報告): (1) 抽出の枠埋め偏り(6/6で上限5件)。(2) LLM由来比率が最終5件で高く、ラベル誘導とガイダンスの効果が未分離。(3) 主語込みスパン。(4) Rule7表の制約(`pump someone's fist`/`pull my leg`->`someone's`でINVALID)=OPEN-310。(5) b1は設計原則「本文全文をLLMへ送らない」と衝突(Trial限定)。いずれも勝手に仕様化していない。
