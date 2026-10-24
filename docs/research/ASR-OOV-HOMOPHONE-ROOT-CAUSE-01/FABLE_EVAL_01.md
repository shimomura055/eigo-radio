# FABLE_EVAL_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_04、2026-10-24) Fable独立評価の記録

記録のみ(API 0・コード変更0・Production変更0)。Fable判定をそのまま保存する。

## 1. Fable判定
**Trial Closeout Status: VALIDATED_LIMITED(E2W形)**。限定理由:
1. 救済効果は本run長segment(Adv part3 3/3受理、-22.19円、約33分短縮)と合成正例(Phase2 6/6、Phase3 5/6)で再現した。
2. 1音素違いの意図的に厳しい負例で誤受理3/17(skool→scold/spool、kewl→cull。Primary・ローカルWhisper・Azureの3エンジンが全て同音語側に転写=ASR証拠の原理的限界)。E2WがE2単独より多く防いだ件数はPhase3で0(Phase2では1)。
3. 各語の同一run内最初の発生は救えない(Ledgerはreactive)。

## 2. Trial実測の要約(引用元: TRIAL_02_RESULT_01.md / TRIAL_03_RESULT_01.md)
| 項目 | Phase2 (TRIAL_02) | Phase3 (TRIAL_03、Opus条件C反映後E2W) |
|---|---|---|
| 正例(救済が必要だった件) | 11件中、条件(medium以上・差分1件)を満たす6件は6/6受理(11件全体6/11、取りこぼし5=low3+複数出現2) | 10件中、救済必要6件のうち5/6受理(BASE_PASS 4、不受理1=thicc_erinome[Primaryがsick、別語聞き違い]) |
| 負例 | 有効9件でE2単独の誤受理1(coal→cool)、E2Wは0。無効3件はASR3エンジンが同音語側 | 20件: 正しく不受理14、既存判定BASE_PASS(E2到達前)3、E2/E2W誤受理3(skool→scold、skool→spool、kewl→cull。3エンジン全て同音語) |
| 本run長segment | - | 20 attempt中Primary非PASS 12。E2受理3 attemptはE2Wも3/3受理(救済保持)。実績38.58円→16.38円=-22.19円 |
| M1単独 | 0/11 | - |
| 費用(Trial実費) | 約11.7円 | 約3.2円 |
| 頻度 | 保存188 run中1件(0.53%、X/Z 62 runで1.6%)。期待値0.12〜0.35円/記事 | 同左 |
| Family適用 | X(Aoede/Charon)・Z(Aoede/Erinome/Charon)で動作確認、Yは配線時に再判定、A/B/C対象外 | 同左 |
| テスト | - | E2W 15件+既存18件=33件PASS |

## 3. ユーザー目標5点との照合
- 誤NG削減=達成。
- Azure呼出削減=小(期待0.12〜0.35円/記事、頻度1/188 run)。
- 誤PASSを増やさない=**近似同音の誤発音では増える可能性あり**(ただし辞書語の既存判定と同じ限界。Ledger登録済みOOV語を辞書語と同じ扱いにする、という位置づけ)。
- X・Z・Y共通=X/Z範囲判定を再利用、Yは配線時に再判定。
- 70円整合=達成。

## 4. Fable判断とProduction採用
Production採用は**ユーザー判断(USER_DECISION_REQUIRED)**。新仕様採用+OF-184保留方式の再導入+D-2'(Tier3二次情報を自動PASS根拠に使う範囲)の拡張+統一判定フローへの層追加を含むため。登録=UDR #186(非blocking)。
- **Fable推奨=(A)条件付き採用**: X/Z限定、独立確認=ローカルWhisper位置1語一致必須・失敗時不受理、E2W受理にWarningラベル+最初N件(10件案)の事後試聴、rollback flag(er109同形)、Store再利用制限(DESIGN_03)、OF-OOV-09の訂正を含む申請文(ADOPTION_NOTE_01)。推奨理由=辞書語に既に許容している限界以上の新リスクを加えず、HR Lock/人間承認の連鎖(今回104.73円・8テイク)を同一run内2回目以降で回避できる。
- (B)=現状維持+telemetry再検討トリガー(E2_ACCEPTABLE_PAIRS増加/gacha型が複数runで出現)。
- (C)=不採用。

## 5. Opus条件Cレビュー(OPUS_REVIEW_02)
必須修正OF-OOV-07〜11は委任_03で反映済み(Fable照合: 07 fail-closed test15件/08 位置1語+本run再評価/09 ADOPTION_NOTE_01/10 DESIGN_03/11 負例20+正例10)。配線実装時はWIRING設計を作り、内容が変われば再レビュー。

## 6. 付随判定
- F1 ’修正(OPEN-500)=FIXED受入(Opus問題なし、should_pass変化0)。
- 別件(新規OPEN、DECISION_LOG/OPEN_ITEMS参照): `er109_wiring_golden_test_01` 3件失敗(HEADで再現、本案件起因でない、分類=修正へ進む・帰属調査が先)、Azure全文判定の崩れ(Opus指摘、NG_BOTH 31/68行、分類=調査候補)。

## 7. 証跡
docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/{TRIAL_02_RESULT_01,TRIAL_03_RESULT_01,OPUS_REVIEW_02,ADOPTION_NOTE_01,DESIGN_03,E2_ACCEPTABLE_PAIRS_01,BUDGET_LOG_01}.md
