管理ID: ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_04 — Fable独立評価のSSOT反映(記録のみ。API 0・コード変更0)。

## Fable判定(そのまま記録する)
- Trial Closeout Status: **VALIDATED_LIMITED(E2W形)**。限定理由: (i)救済効果は本run長segment(Adv part3 3/3受理、-22.19円、約33分短縮)と合成正例(Phase2 6/6、Phase3 5/6)で再現したが、(ii)1音素違いの意図的に厳しい負例で誤受理3/17(skool→scold/spool、kewl→cull。Primary・ローカルWhisper・Azureの3エンジンが全て同音語側に転写=ASR証拠の原理的限界)、E2WがE2単独より多く防いだ件数はPhase3で0(Phase2では1)。(iii)各語の同一run内最初の発生は救えない(Ledgerはreactive)。
- ユーザー目標5点との照合: 誤NG削減=達成/Azure呼出削減=小(期待0.12〜0.35円/記事、頻度1/188 run)/誤PASSを増やさない=**近似同音の誤発音では増える可能性あり**(ただし辞書語の既存判定と同じ限界=Ledger登録済みOOV語を辞書語と同じ扱いにする、という位置づけ)/X・Z・Y共通=X/Z範囲判定再利用、Yは配線時に再判定/70円整合=達成。
- Fable判断: Production採用は**ユーザー判断(USER_DECISION_REQUIRED)**。新仕様採用+OF-184保留方式の再導入+D-2'(Tier3二次情報を自動PASS根拠に使う範囲)の拡張+統一判定フローへの層追加を含むため。Fable推奨=**(A)条件付き採用**(X/Z限定、独立確認=ローカルWhisper位置1語一致必須・失敗時不受理、E2W受理にWarningラベル+最初N件(10件案)の事後試聴、rollback flag er109同形、Store再利用制限DESIGN_03、OF-OOV-09の訂正を含む申請文ADOPTION_NOTE_01)。推奨理由: 辞書語に既に許容している限界以上の新リスクを加えず、HR Lock/人間承認の連鎖(今回104.73円・8テイク)を同一run内2回目以降で回避できる。(B)=現状維持+telemetry再検討トリガー(E2_ACCEPTABLE_PAIRS増加/gacha型が複数runで出現)、(C)=不採用。
- Opus条件Cレビュー(OPUS_REVIEW_02)の必須修正OF-OOV-07〜11は委任_03で反映済み(Fable照合: 07 fail-closed test15件/08 位置1語+本run再評価/09 ADOPTION_NOTE_01/10 DESIGN_03/11 負例20+正例10)。配線実装時はWIRING設計を作り、内容が変われば再レビュー。
- F1 ’修正(OPEN-500)=FIXED受入(Opus問題なし、should_pass変化0)。
- 別件: `er109_wiring_golden_test_01` 3件失敗(HEADで再現、本案件起因でない)→新規OPEN登録(分類=修正へ進む、帰属調査が先。管理ID未定、TEST-HYGIENE系で別委任)。Azure全文判定の崩れ(Opus指摘、NG_BOTH 31/68行)→新規OPEN登録(分類=調査候補、別管理ID、着手はユーザー優先度判断)。

## 作業
1. `docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/FABLE_EVAL_01.md` に上記Fable判定を保存(Trial実測の要約表: Phase2/3の正例・負例・本run結果・費用・頻度・Family適用を `TRIAL_02_RESULT_01.md`/`TRIAL_03_RESULT_01.md` から引用)。
2. `docs/pm/USER_DECISION_REGISTER_01.md`: 新規UDR(次の空き番号、#186想定。既に使われていれば次番号)「E2W(Ledger読み直接音素一致+ローカルWhisper位置一致)のProduction採用可否 (A)条件付き採用/(B)保留+telemetry/(C)不採用、Fable推奨A、非blocking」。
3. `OPEN_ITEMS.md`: OPEN-498=VALIDATED_LIMITED(E2W)_PENDING_USER_ADOPTION(UDR番号、証跡パス)。OPEN-500=FIXED→受入済み表記。新規OPEN 2件(golden test 3件失敗/Azure全文判定の崩れ)を**分類付き**で登録(POST_USER_VALIDATION)。
4. `DECISION_LOG.md`: Fable評価エントリ1件(Status・推奨・UDR番号・Opus条件C実施・Production変更0)。
5. `docs/pm/ACTIVE_TASK.md`: 委任_03/04行を追加(Status=VALIDATED_LIMITED_PENDING_USER_ADOPTION、UDR番号)。
6. 本委任文を `docs/pm/delegation_log/2026-10-24_ASR-OOV-HOMOPHONE-ROOT-CAUSE-01_DELEGATION_04.md` に逐語保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新> --out <path>`、先頭行一致確認)。
7. Git: 自分の変更ファイルのみ。**別agentが並行して同じSSOT(DECISION_LOG/OPEN_ITEMS/USER_DECISION_REGISTER/ACTIVE_TASK/CURRENT_SPEC)を編集中**。各ファイルは編集直前に該当箇所を再Readして最小Edit、衝突時は再Readして再試行(他agent差分を上書き・巻き戻ししない)。commitは他agentの未commit差分を混ぜないため、前委任と同様に「HEAD内容+自分の編集」を `git update-index` でindexへ入れる方式か `git commit --only -- <path…>` のいずれか安全な方で行い、`git diff --cached --name-status` で意図しないD/Aなし確認後 `git push origin HEAD:main`。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret grep 0件。
8. 報告 `docs/pm/RESULT_PACKET_AOHR4.md`(UDR番号・新規OPEN番号・commit hash・反映箇所)。