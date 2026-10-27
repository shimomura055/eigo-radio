# 委任_08(Phase B / B4): 採用take分類核 `classify_adopted_take`(未配線の純module+test)+旧Gate/新Gate差分監査(保存X/Y/Z run全件、API 0)

共通事項=`…_委任_00_COMMON.md`。設計=`INTEGRATION_01.md`(F-4/F-5/F-6/F-16)+`OPUS_REVIEW_01.md`((b)-1/(b)-5、M-5/M-8/M-9/M-10、R-3、Fable照合)+`W3_UD3_GATE_DESIGN_01.md`(分類表・正常定義・allowlist・撤去・test計画)。前提module=`er129_lr_display_reflection_01.py`(委任_07、commit済み。`resolve_adopted_take`/`build_lr_ledger`/`check_text_parity`/`check_confirmed_overlap`の実際のAPIを読んで使う)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B4_CLASSIFY_CORE_AND_DIFF_AUDIT_01.md`。**実装委任**(新module+test+成果物のみ。X M3/Y gate/Z gateの**呼出切替は本委任では行わない**=統合配線commitで行う)。

## 契約
`er130_adopted_take_classifier_01.py`(純関数・LLMなし):
- `classify_adopted_take(ledger_clip, policy, allowlist, ctx) -> Classification{verdict: PASS|PASS_WITH_WARNING|BLOCK, reasons[], warnings[]}`。
- **通過(警告記録)**=採用takeのStyle実測が承認済みStyle allowlist(leaf側既存定数をimportして導出: role Style群、`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、JA短文、ENGLISH_LOCK、Z従来Dialogue、Z ctx。drift testで固定)に含まれ、slotがpolicyの許可範囲(①②③/①'②'③')で、記録完全(`resolve_adopted_take`がUNKNOWN/RECORD_MISMATCHでない)で、ASR PASS系で、`text_parity.verdict==PASS`(三者一致Gateの結果を受け取る。本moduleは検査を再実装しない=Opus (b)-5)で、`overlap` T1/T2/T3非干渉。正常Fallback=`FALLBACK_APPLIED`警告、正常LR=`LR_APPLIED`警告(ともにHR非要求)。
- **BLOCK(従来どおり)**=未承認・不明Style/許可されないFallback方式(policy外slot)/記録欠落・不一致(UNKNOWN, RECORD_MISMATCH, Style記録欠落)/ASR NG・品質NG/overlap干渉/parity不一致/例外(fail-closed)。
- 旧記録(OPEN-564以前のStd `fallback_used=True`等): `resolve_adopted_take`④で導出でき記録完全なら警告、不完全ならBLOCK(F-6)。
- `profile`非依存(全profile適用、F-4)。X M3の`PROFILE_DEFAULT`無条件PASS挙動との関係は成果物に明記(parityは assemble Gate側)。

## 作業
1. module+test(`er130_adopted_take_classifier_01_test_01.py`): W3 §7の新規15ケース+Opus M-5(HR採用後・Store再利用・旧cache・Z build_entry・wav sha変化で偽BLOCKしない)+allowlist drift test+例外時BLOCK。
2. **差分監査(M-9、配線前受入条件)**: 保存済みX/Y/Z run(`er019_output/`・`er121_output/`相当・`er026_output/`配下の`tts_generation_results`を持つ全run。件数を記録)について、現行Gate(X `m3_assembly_gate`/Y gate/Z `run_audio_gate`のStyle・Fallback・LR項)の判定と、新分類核の判定を**読み取り専用**で並べ、「旧BLOCK→新PASS(解除、正常LR/Fallbackのみ)」「旧PASS→新BLOCK(厳格化)」「不変」をsegment単位で集計。**旧PASS→新BLOCK**は全件、原因(記録欠落/旧記録/parity未配線=常にBLOCK想定なので除外して集計/overlap)を列挙し、正当(品質異常)か偽BLOCKかを判定。偽BLOCKがあれば規則修正(allowlist・導出④の範囲内)して再集計。AI島hr_02(k2 BLOCK)・告げ口心臓Adv kp2_en(ENGLISH_LOCK、M-10)・Y E-1・Word Gacha Adv part3の結果を個別に記載。
3. 撤去予定(W3 §5)の一覧を成果物へ(本委任では撤去しない)。
4. Git: 新規ファイル+成果物のみ`git add`、commit「LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_08(B4): 採用take分類核(未配線)+旧/新Gate差分監査(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。
5. 最終応答: 成果物パス+要約10行(test件数/差分監査: run数・segment数・解除数・厳格化数とその正当性/偽BLOCK 0か/告げ口心臓Adv kp2_en判定)。
