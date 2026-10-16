## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` / `DECISION-QUALITY-IMPROVEMENT-01` 委任_01(**read-only棚卸し**: C-1の5問題に対する既存規則・実例・選択肢の整理。Fableの推奨案作成とOpusレビューの材料)。並行: AUW 委任_08(Git・SSOT・ACTIVE_TASK担当)、AUW 委任_09(read-only)、FCJ 委任_01(read-only)。**本委任はコード・SSOT・既存ファイルを一切編集せず、Git操作もしない。** 新規作成は棚卸し書とRESULT_PACKET_DQI1.mdと委任文保存のみ。衝突なし。

## 性質/到達上限Status/禁止事項

- 性質: PM運用の改善方式検討(材料整理)。到達上限Status: `INVENTORY_READY`。**新しい運用仕様の採用・`sandwich-pm.md`/`PM_GOVERNANCE.md`の編集・追加盲検・Day5〜6の開始は禁止**(ユーザー指示C-4)。
- 禁止: ファイル編集(新規2ファイルと委任文保存を除く)、Git操作、有料API、推測で「原文」を創作すること(引用は必ずファイル:行)、Opusレビュー結果の本文を創作・転記すること。
- Opus独立技術レビューGate(11-3): 本委任は非該当。Fableが本棚卸しと自身の推奨案を元にOpusへ依頼する予定(ユーザー指示C-2「必要に応じてOpus独立レビュー」)。
- 時間見込み: 60〜90分。並列化: 他3委任と並列。
- 費用/日次: JPY0。承認区分: C(承認済みscope内=「改善方式の検討・既存規則との整合確認・具体案の提示」)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 費用上限[Cap]なし。

T-0保存先: `docs/pm/delegation_log/2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_01.md`(全文)。

## ユーザー指示(原文)

2026-10-16ユーザー指示(全文は委任_08が`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`へ保存中。存在すればそれを正とする)。本件該当箇所を逐語引用:

「# C. Fable PM判断品質の改善
**管理ID：PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DECISION-QUALITY-IMPROVEMENT-01**
**現在Status：既存改善は実装済みだが、目的達成は未検証・未達**
**今回の到達範囲：改善方式の検討・既存規則との整合確認・具体案の提示**
**Day 5〜6：引き続き保留**
## C-1. 解決すべき問題
Fableはこれまでの改善で、ユーザー原文・最終成果物・受入条件の照合を行うようになった。
しかし、次の問題が残る。
1. 承認済み仕様を再びユーザー判断へ戻す。
2. 自己解決可能な技術的不具合をユーザーへ転送する。
3. 発見済みの重大品質NGを最終判定へ正しく反映できない。
4. 本来のタスクと、新規発見した独立問題を混在させる。
5. 検出した不適合に対する是正・STOP・ユーザー提示制限が不適切。
単なる報告形式の問題ではなく、PMの意思決定品質の問題として扱う。
## C-2. 改善案の検討
以下はChatGPTからの参考提案であり、実装方式の指定ではない。
Fable自身が検討し、必要に応じてOpus独立レビューを受けること。
### 提案①：重大品質NGと最終受入の整合強制
成果物に重大な意味反転、Fact欠落、学習内容の不一致等がある場合、別のテストPASSや形式的問題による差戻しで相殺できない仕組みを検討する。
### 提案②：不適合成果物の提示制限
目的を満たしていない成果物を、完成品としてユーザーへ試聴・選定依頼することを防ぐ。
ただし、不完全な候補を比較すること自体が正式目的のTrialは区別する。
### 提案③：最終判定の矛盾検出
受入記録の詳細では重大NGなのに、総合判定ではACCEPTEDとなるなどの矛盾を、Validator・構造化判定・独立レビュー等で防ぐ方式を比較する。
### 提案④：ユーザー判断Gateの適正化
必ず以下を区別する。
- ユーザー承認済みで実施すべき事項
- 承認範囲内で技術的に自己解決可能な事項
- 新たに発見された独立問題
- 本当にユーザー判断が必要な事項
承認済み事項を再びUSER_DECISION_REQUIREDに戻さない。
独立問題はOpen Itemに分離し、重大な依存・阻害関係がない限り、本タスクを不要に停止させない。
## C-3. Fable／Opusに求める検討
以下を比較評価する。
- 現行Prompt／運用規則の改善だけで足りるか
- 構造化した受入判定が必要か
- Validator等の機械的な矛盾チェックが必要か
- Fable自身による独立判断とOpusレビューの適切な役割分担
- 誤STOP・過剰なUSER_DECISION_REQUIREDのリスク
- 実装・運用コスト
- 他Family／案件への再利用性
- 既存Governanceとの重複・競合
- 再発防止効果
Fableは単にOpusの提案を転記するのではなく、自分自身の推奨案・理由・代替案・QDC評価を示す。
## C-4. 今回のSTOP条件
本指示では、新規の大規模改修・追加盲検・Day 5〜6開始は承認していない。
改善案の比較と推奨がまとまった段階でSTOPし、ユーザーへ提示する。
新しい運用仕様を独自にProduction採用してはならない。」

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし(状態遷移なし)。OAR-02採点のOpus指摘が台帳にあればIDのみ列挙。

## 事前指定Read一覧

- `.claude/agents/sandwich-pm.md` L60-110(手順4-2 受入記録5項目+是正A/B)、およびGrep `USER_DECISION_REQUIRED`/`Open Item`/`独立問題` → 該当行±10。
- `docs/pm/PM_GOVERNANCE.md`: Grep見出しで位置特定→該当節のみRead: `9-0`(固定5節報告)、`10-1`、`10-2`(8分類)、`11-1`、`11-3`(Opus Gate・STOP条件)、`11-4`、`11-6`(問題解決運用)、`11-7`(既定OFF例外)、`12-13`(REGISTER照合)、`14`(7段階、Human Reviewは最後の手段)、`21`(Existing Spec/Prior Trial Check A/B/C)、`23`(重大誤解原則7観点)、Gate 7(`2-0`付近または`Gate 7`Grep)。
- `CLAUDE.md` L1-40(共通Charter: 8原則・判断を求める主な事項・判断を求める前の確認4点)。
- `docs/pm/USER_DECISION_REGISTER_01.md` L1-30(4区分の定義)、L150-170(#73 決定③、#76、#80〜#87)。
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REBLIND_SCORING_01.md` §3〜§4(v2欠陥提案(A)〜(D))。
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/OAR2_SCORING_01.md` §0・§2・§3(v3欠陥提案①〜⑥)・§4。
- `docs/pm/delegation_log/2026-10-15_DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02_USER.md`(是正A/B/Cの原文、全文可・約200行想定)。
- `docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`(全文)。
- `docs/pm/tools/check_delegation_prompt.py` 冒頭〜60行(既存の機械的チェッカーの構造。Validator案の再利用性評価用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/PM_GOVERNANCE.md`: `ACCEPTED`/`NOT ACCEPTED`/`条件付き受入`/`受入記録` → 受入判定語彙の定義有無。
- `docs/pm/PM_GOVERNANCE.md`・`sandwich-pm.md`: `試聴`/`選定`/`提示` → 不適合成果物のユーザー提示に関する既存規定の有無(提案②との重複確認)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: `判断済み` → 「判断済みを再質問しない」規則の既存文言。
- 追記位置: 既存ファイルへ追記しない。新規 `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_INVENTORY_01.md` を作成。

## 実行コマンド全文

- `cd C:\Users\tensh\eigo-radio; Get-ChildItem docs\research\PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 -Recurse -Filter *.md | Select-Object -ExpandProperty FullName`(既存成果物一覧の把握のみ)
- それ以外の実行なし(Read/Grepのみ)。

## SSOT追記文

なし(本委任ではSSOTもsandwich-pm.mdも編集しない)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **なし**。Git操作: **なし**。新規ファイルは未追跡のまま残す。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DQI1.md`に記載。棚卸し書 `DQI_INVENTORY_01.md` の構成:
1. **問題1〜5それぞれの実例**(2026-10-15〜16の実記録から、ファイル:行で): 例として、問題1=REGISTER #83/#84/#86がUSER_DECISION_REQUIREDとして起票された経緯(AUW 委任_07の判断根拠 vs 統一仕様承認原文)、問題2=OPEN-372(Family C JA en固定)がAUW内で「Production変更を伴うため未実施」とされた判断、問題3=OAR-02 c3(意味反転MAJORを(4)で検出しながら(5)で形式的理由に置換)・CRB初回0/2、問題4=AUW内でFamily C不具合・U1〜U4が同一報告に混在した点、問題5=c2(Champion選定をそのまま提示)。各実例について「当時どの既存規則が適用可能で、なぜ効かなかったか(規則不在/規則はあるが判断時に参照されない/規則が曖昧/規則が競合)」を1行で。推測は「推測」と明記。
2. **既存規則マップ**: 問題1〜5 × 既存規則(Charter 8原則・判断前確認4点・決定③#73・10-2 8分類・11-3 STOP条件・11-6・14節・21節A/B/C・23節・4-2+是正A/B・v2/v3提案)の対応表。重複・競合・空白を明示。
3. **選択肢の比較表**(C-3の9観点で各案を◯△×+1行理由): (i)現行Prompt/規則の文言改善のみ、(ii)構造化受入判定(受入記録を固定スキーマ化し、重大NGフィールドが真なら総合判定ACCEPTED不可を規則化)、(iii)機械的Validator(RESULT_PACKET/受入記録をscriptで検査、`check_delegation_prompt.py`と同系統)、(iv)USER_DECISION_REQUIRED発行前の4区分トリアージ表の必須化(承認済み/自己解決可/独立問題/真のユーザー判断)+REGISTER照合、(v)Opusレビュー役割の再定義(設計レビューに加え「最終判定の矛盾検出」を限定的に担当)、(vi)組合せ案(ii)+(iv)+軽量(iii)。各案について、実装規模(編集対象ファイル・行数見込み)、運用コスト(1委任あたりの追加token/時間)、誤STOP・過剰UDRのリスク、再利用性、再発防止効果(問題1〜5のどれに効くか)。
4. **「不完全候補の比較自体が目的のTrial」の判別基準案**(提案②の例外): 既存のTrial設計書で該当するもの(例: Champion Trialは完成セットの比較が目的=例外に該当しない、など)を2〜3例で検証。
5. **Validator案の実現性**: 受入記録の機械検査に必要な固定見出し・フィールド(例: `重大NG:` あり/なし、`総合判定:`、`ユーザー提示可否:`)、既存`check_delegation_prompt.py`の拡張で足りるか、新規scriptか。見込み行数。
6. 未確認事項・Sonnetの所見(Sonnet自身の推奨は「参考」として1段落。Fableの推奨とは区別)。
7. 費用JPY0、所要時間、受入記録5項目(当初目的=C-1〜C-4原文逐語/最終成果物=棚卸し書/証拠/一致・不一致/判定)。
