# RESULT_PACKET_KPG01(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_01、2026-10-30)

- 結論: Closeout案=USER_DECISION_REQUIRED(Status上限VALIDATED手前、Fable最終)。工程分離方式Dで『修正せず選べる候補』 現行26/66(39%)→A統合56/70(80%)→D 61/71(86%)(Std 27%→88%)。3件以上選べるケース 4/12→12/14。目的は概ね達成、完全ではない(D残NG10/71)。
- 比較ページ: https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/ (必須9例表・記事別Before/After・可否理由・内部評価は折畳)
- 必須9例(Before/A/D): G1 take points away from ×/△(b1b)/× | G2 make life work ×/×/△(単体○・選定段でF) | G3 at the time of ×/×/○ | G4 narrow down ×/○/○ | G5 turn something around ×/○/○ | V1 confirm a clear fall ×(提示)/○/○ | V2 make room for ○/○/○ | V3 blow a whistle ○/×/○ | V4 sales pitch ○/○/○
- 費用・時間: ¥79.1(Cap¥60→理由記録で¥80未満)。D 1レベル¥0.98(+約¥2/記事セット、既存段置換の相殺は未確認)・約55秒、A ¥0.31・約33秒。事故: deepseek-v4-pro判定1回¥7.4(thinking既定)→以降flash非thinking。
- 使用モデル: gpt-6-luna(Production比較基準=例外2)、gpt-6.1-sol(最新推奨系)、gemini-3.8-flash(最新Flash・別系列検証)、deepseek-v4-pro(最新最上位・判定1回)、deepseek-flash(下位=費用Cap上の実務制約)。gpt-6-astra未使用。
- 設計上の発見: 現行canonicalizationは規則1〜5外の変換を決定論検証で却下=目的語のsomething化・後続名詞句除去は仕様上不可。採用には学習表示用display_formの新許容ルールが必要(OPEN-349同系統、ユーザー判断)。
- 残NG(D): 自由な組合せ4(deep image等)・語義変化2(take a turn/set a limit)・不自然2・易しい1・受動形1。Before成功例26件中6件が脱落。
- 判断候補(分類D、UDR登録・未提示): 新許容ルール/7件未満の容認/G1型の扱い/費用/追加Trial約¥5(Cap追加)。
- commit: 本commit(hashは最終報告に記載)。成果=docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/{CURRENT_STATE_01,TRIAL_DESIGN_01,RESULT_01}.md
- (1)既存仕様整合: CURRENT_SPEC.md:2041-2048、er119_kp_p7w5_prompts_01.py:24-43、er119_kp_candidates_01.py:198-300、er119_kp_human_review_01.py:705,1241,1548、canonicalizationテンプレ:9-21(CURRENT_STATE_01.md)。矛盾は検出せず。
- (2)未承認機能の既定値: Production到達経路への未承認機能の混入0(Production code/Prompt/Validator/閾値の変更0、flag新設0)。確認=git diffでProduction fileの変更なし、Before再現は`select_p7`/`run_key_phrase_canonicalization`のread-only呼出でtelemetry書込をprocess内no-op化。
- (3)失敗終了時の最終成果物: Trialは完了終了。最終成果物=比較ページ(上記URL)とRESULT_01.md。目的要件との適合=『概ね達成・完全ではない』(86%、残NG明記、判断事項をUDR登録)。
- (4)撤去・残置: Production規則の撤去なし。Trial側の旧方式(B_luna/C1/C2/C3/A_sol/A2_sol/B_mix)は比較記録として`kpg01_work/results`に残置(最終設計はD)。Grep: Production moduleに`kpg01`参照0。
- 判定整合: 重大NG=なし / 主因=抽出ではなく塊判定のばらつきと一般化での修飾語DROP / 是正対象=意味破壊ガード・塊判定2回和集合 / STOP理由=なし / 提示=証拠のみ(Fable受入・独立評価後に提示)
