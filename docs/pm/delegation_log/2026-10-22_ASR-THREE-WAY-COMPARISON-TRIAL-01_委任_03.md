FABLE-DELEGATION-MARKER: ASR3W-CLOSEOUT-委任_03-20261022

# 委任(ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_03: ユーザー正式決定(#136)のCloseout記録のみ。API 0・有料run禁止・Productionコード/モデル構成/Prompt/flag無変更)

## 0. 運用ルール
`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。対象ファイルのみ明示add。commit前 `.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`(localブランチ`work/post-merge-01`)。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は一時ファイル(gitignore、force-add禁止)。SSOT全文読込禁止(Grepで該当行のみ)。作業treeの他人の未commit差分(`er0XX_output/*`等)を混ぜない。現在、他のagentは動いていない。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_ASR-THREE-WAY-COMPARISON-TRIAL-01_DECISION_USER.md` へ本文を改変せず保存し、文字数とsha256[本文のみ]を記録)
---
## Claude Codeへの回答・指示：ASR 3方式比較Trialの採用判断

ASR-THREE-WAY-COMPARISON-TRIAL-01（#136）について、ユーザー判断を以下のとおり確定する。

### 1. 正式決定

1. **Primary：OpenAI `gpt-4o-mini-transcribe` を維持。**
2. **Secondary：Azure Speech STTを維持。**
3. **ローカルWhisperのProduction導入は不採用。** 運用複雑化を避ける。
4. Primary／Secondaryの入替は行わない。
5. 今回の比較Trialに基づく追加精度検証（Store 333件へのAzure追加検証等）は実施しない。

### 2. Key Phraseの両方PASS仕様

Key PhraseはPrimary／Secondaryの両方PASSを必須とする方針。

ただし、この仕様の実装状況・Production整合性については**別指示系統で確認中**。

今回の指示では調査・実装・追加Trialを行わない。重複作業を禁止する。

### 3. Closeout

- 今回のモデル比較Trialの採否を、上記ユーザー判断に従って整理する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／USER_DECISION_REGISTERに必要な記録を反映する。
- Gitへ反映する。
- **既存Productionコード・モデル構成は変更しない。**

記録更新後、変更ファイル・commit・残存Open Itemのみ簡潔に報告すること。

今回の指示による新規Trial・API呼出は不要。
---

## 2. Fableの整理(記録に使う。原文の範囲を広げない)
- §1の1〜5=正式決定(判断済み)。Trialの最終Status: Trial自体は`VALIDATED`(検出方向の有効性)のまま、**採用判断=現行構成維持(Primary OpenAI gpt-4o-mini-transcribe/Secondary Azure STT)、ローカルWhisper不採用、入替なし、追加精度検証(①″ Azure 333件等)は実施しない**。C1dK/C5K(KP限定Azure拒否権)の採否そのものは§2により別系統(下記)へ。
- §2=「Key PhraseはPrimary/Secondary両方PASSを必須とする**方針**」。実装・Production整合は別系統=`FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01`(OPEN-440)。Fableの同日報告(ケース1: 承認済み仕様はPrimaryのみ、KP両方PASSの承認記録なし、採用は新仕様)へのユーザー回答待ち。**本委任ではKP仕様の採用・実装・配線を記録しない**(「方針表明あり、正式採用・実装指示は未」とだけ書く)。重複作業禁止。
- PNMH(OPEN-439、`PLAN_FIXED_WAITING_ASR_SELECTION`)のTrialトリガー「新Primary/Secondary確定」は本決定で**充足**。ただしTrial開始はFable判断でOPEN-440(KPのPASS条件)の決着後に順序付ける(理由=Trial Phase3のKP判定構成を確定させてから走らせ、再実行を避ける)。OPEN-439へこの旨を1行追記(Statusラベルは`PLAN_FIXED_ASR_CONFIRMED_WAITING_OPEN440`へ)。

## 3. 作業
1. `docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_RESULT_01.md`へ「§9 ユーザー正式決定(2026-10-22)」を追記(逐語+採否整理+Status)。
2. `CURRENT_SPEC.md`: ASR Primary/Secondaryエンジン構成を定義している行(Grep: `gpt-4o-mini-transcribe`、`Secondary ASR(Azure)`、統一ASR判定仕様 L2813-2838付近)に、2026-10-22ユーザー再確認(維持・Whisper不採用・入替なし・追加検証なし、出典=USERファイル名)を**追記のみ**(既存行の書換え禁止)。KP両方PASSについては「方針表明(2026-10-22)、実装・採用はOPEN-440で確認中。承認済み仕様はL2818のまま」と追記。
3. `DECISION_LOG.md`: 決定エントリ1件(管理ID、逐語引用§1・§2、決定内容、Production無変更、出典)。
4. `OPEN_ITEMS.md`: OPEN-438(ASR 3方式比較、USER_DECISION_REQUIRED)→`DECIDED_CLOSED`相当へ(履歴は3,000字超なら`OPEN_ITEMS_HISTORY.md`へ切出し)。OPEN-440へ「ユーザー方針表明(KP両方PASS)あり、Fable報告(ケース1)への回答待ち」を追記。OPEN-439へ上記2.の追記。OPEN-433(Secondary費用見込み)やOPEN-426等に本決定で状態が変わる行があるか確認し、変わる行だけ最小追記。
5. `docs/pm/USER_DECISION_REGISTER_01.md`: #136を判断済み(内容要約・日付・出典)へ。#137は触らない(A側で更新済み)。KP両方PASSは#136の判断済み欄に「方針表明。採用判断はOPEN-440報告への回答で確定」と注記し、新しい番号は振らない。
6. `docs/pm/REPORT_LEDGER.md`に1行追加。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_ASR-THREE-WAY-COMPARISON-TRIAL-01_委任_03.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: ASR3W-CLOSEOUT-委任_03-20261022` を含むAgent tool_useの0始まり通番。直前2件はindex 234/235だったので236前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
7. commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ追記。`docs/pm/RESULT_PACKET_ASR3W3.md`へ報告。

## 4. 禁止
コード・モデル構成・Prompt・flag・Ledger・Phrase Listの変更禁止。有料API 0。KP両方PASSの実装・設計着手禁止。PNMH Trialの実行禁止。ユーザー決定の範囲を広げない(「採用」と書けるのは§1の1〜5のみ)。

## 5. 報告(簡潔。ユーザー§3「変更ファイル・commit・残存Open Itemのみ」に合わせる)
1) 変更ファイル一覧(各1行で何を追記したか) 2) commit hash・raw URL(TRIAL_RESULT_01.md) 3) 残存Open Item(OPEN-440=KP PASS条件[ユーザー回答待ち]、OPEN-439=PNMH Trial[トリガー充足・OPEN-440後に開始]、その他本決定に関係して残るもの) 4) RESULT_PACKET 4行+費用JPY0+使用モデル名。