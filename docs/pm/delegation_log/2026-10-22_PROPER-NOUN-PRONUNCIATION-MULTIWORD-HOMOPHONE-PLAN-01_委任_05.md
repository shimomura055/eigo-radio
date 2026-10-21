FABLE-DELEGATION-MARKER: PNMH-FABLE-VERDICT-委任_05-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_05: Fable独立評価・最終分類の記録のみ。API 0・JPY0・コード無変更)

## 0. 運用ルール・並列注意
別agent(B3丸めTrial 委任_03)が実行中で、`OPEN_ITEMS.md`(OPEN-437)・`docs/pm/REPORT_LEDGER.md`・`docs/pm/ACTIVE_TASK.md`・`er090_*`へ書く。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分を混ぜない。

## 1. 記録するFable判定(逐語で`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/TRIAL_RESULT_01.md` §7「Fable独立評価」へ記入。内容の改変・補強はしない。事実関係で明らかな誤りがあれば記入せず報告)

---
**最終分類: `VALIDATED`**(Trialとしての有効性確認。`APPROVED_FOR_PRODUCTION`ではない。Production採用・配線はユーザー正式承認が必須)

**合格基準の照合(Fable)**
- 既知正例の救済100%: 充足(保存転写`byus→buy us` 4/4、構成正例M1/M2/M4/M7/RS1)。
- 新規誤PASS 0: 充足(ケース表41件・保存転写4,032ペア・実音声13本×2エンジン)。
- 実音声負例のPASS 0: 充足(bios×2/buys/buy/B Y U S)。**A9(`Bi-us`型)の1件は「負例の構成失敗」と判定**: 両エンジンが`Bias`と転写しており、TTSが`bias`と読んだ疑いが強い。PASSは現行の1語同音規則によるもので提案の寄与は0。したがって提案の欠陥ではないが、「`Bi-us`型の実音声負例をNGにできる」ことは本Trialでは**実音声で未検証**であり、保証はケース表BI1/BI2(NOT_PASS)とV8ガードのコードレベルに留まる。採用時の実装testで実音声負例を1本取り直すことを条件とする。
- Regression PASS→NG 0: 充足。層A/B/C分離報告: 充足。

**サンプルの偏り(Fable)**
- 実音声での救済実績は1記事(run_byus_01)の4ペアのみ。新規13本ではASRが`Bias`/`Byus`/`by US`と出力し、`buy us`型の転写は0件。提案が必要になる頻度は低く(0.10%)、効果は主に予防的。有意性は主張しない。
- 一方、副作用の面は広く計測済み(4,032ペア再適用、機能語経由一致の全列挙407組→代表発音限定89組、保存データでの発生0)。安全側の評価としては十分。

**挙動変化4点の審査(Fable)**
- NX1(`two→to`が多語同音と共存して新規PASS): `two→to`は現行Productionが既に許容している1語同音の数値例外であり、新規に数値差を解放するものではない。各差分が独立に真の同音である以上、組合せでNGにすべき理由はない→**許容**(ただし採用提案時にユーザーへ明示)。
- BI3(`bias⇔by us`): ユーザー判断「発音が同じなら単語数・綴り・ストレスの違いでNGにしない」の範囲内→許容。区切り読みとの区別不能は既知の限界として記録。
- CS3の分類変化(最終NG不変)、RS1 PASS: 許容。
- 機能語経由の一致(`businesses→business is`等、代表発音限定89組): いずれも連続音声では同音であり、TTSが正しく読んだ場合にASRがそう綴る可能性のある組。保存データで発生0。採用時はこの89組を目視リストとして添付する。

**Family X/Z整合**: 判定入口は共通関数で、Z由来の保存転写も同一関数で再判定済み。Z runner呼出行の個別確認は採用実装時のtestで行う(未確認事項として残す)。

**QCD**: 実行時API追加0、判定時間+0.02ms、Trial費用JPY6.32(Cap 50)。量産原価への影響なし。

**Production採用に向けたFable推奨**: 採用を推奨する(品質ライン「同音の正しい読みをNGにしない」に適合し、誤PASS増0・原価0)。ただし効果が小さいため単独で急がず、**OPEN-440(Key Phrase両方PASS)の実装と同じ判定関数群を触るので、同一の実装・Opus独立レビュー(条件C)・Regression・runtime evidenceに束ねて実施する**ことを推奨。供給層L2は範囲外のまま(#133判断待ち)。
---

## 2. SSOT
- `OPEN_ITEMS.md` OPEN-439: Status=`VALIDATED`(Trial)・`PRODUCTION採用未承認`。履歴追記(Fable判定日2026-10-22、費用JPY6.32、残=採用判断/U5/J7/L2)。3,000字超なら`OPEN_ITEMS_HISTORY.md`へ切出し。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 新番号(#138)で「多語同音救済(L1)のProduction採用可否」をUDR(非blocking)として登録。選択肢=(ア)採用(OPEN-440実装と束ねて実施、Opus条件Cレビュー付き)/(イ)保留。Fable推奨=(ア)。付随審査事項=NX1許容・BI3許容・機能語経由89組の目視リスト・`Bi-us`実音声負例の採用時再取得。#137には「Trial完了→#138へ」と1行追記。
- `docs/pm/REPORT_LEDGER.md`に行追加。DECISION_LOGは書かない。
- T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_05.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-FABLE-VERDICT-委任_05-20261022` を含むAgent tool_useの0始まり通番、239前後)。
- commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNMH5.md`へ短い報告(変更ファイル・commit・raw URL[TRIAL_RESULT_01.md]・RESULT_PACKET 4行・JPY0)。