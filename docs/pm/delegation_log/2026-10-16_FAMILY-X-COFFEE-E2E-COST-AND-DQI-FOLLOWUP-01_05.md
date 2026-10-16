## 管理ID

`FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01`(略称CEC)委任_05(通番は親`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`から継続: ユーザー指示保存+K2代替音声Open Item登録+06c test独立Open Item登録+DQI前向き観察台帳の準備+**Coffee正式E2E stage(a) text工程の実走**[Research→Verified Fact Ledger→B3(Sol)→W-1 R0→R1→R2(Sol)→Adv英語化→Std調整→(構造的Mandatory STOPに到達したらそこで停止)]+工程別費用実測)。並行委任: なし。Git: `.git/index.lock`は60秒待ち再試行。mainへは`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`→`git push origin main`→main dirで`git merge --ff-only origin/main`。

## 前委任の受入記録(Gate 7)
委任_04(commit `4a7ee50d7`): `PHASE2_WIRED_CODE_COMMITTED_RUNTIME_EVIDENCE_PENDING`。当初目的=原文§4・§9。成果物=結合(audio runnerにIOL scope)・回帰956 PASS(FAIL6は非起因)・CLI未指定dry-runで`fx_20261016`確認・SSOT・commit/push。一致: 受入条件6・11充足。不一致: 4・5・7・8・9・12はCoffee実走待ち。判定: ACCEPTED。判定整合: 重大NG=なし。**ユーザーは本日、Coffee E2Eを最大JPY205で承認**(下記原文§1・§3)。

## 性質/到達上限Status/禁止事項
- 性質: Production正式経路の有料実走(text工程)+SSOT。到達上限Status: `COFFEE_E2E_TEXT_STAGE_DONE_OR_MANDATORY_STOP`(PRODUCTION_WIRED判定はしない)。
- 禁止: 承認上限JPY205(E2E全体)の超過見込みでの続行、**本委任のtext工程capはJPY100**(見積期待68/最悪95。超過見込みでSTOP)、Mandatory Human Review/品質Gate/U-1/assert_budget_ok/review_lock/HRの迂回・解除、旧Coffee成果(`run_l3_01`/`run_v5_ms_01`/MAQ_TRIAL等)のResearch結果・Fact Ledger・B3・Writer原稿・KP・音声の流用(新out_dir必須、`verified_fact_ledger.txt`の既存再利用禁止=`ER:98`の挙動を事前確認)、Trial用Writer/旧Luna・Astra経路の使用、同一原因の再試行(1回失敗したら原因を見てから。同じ原因で2回目失敗ならSTOP)、有料runの再起動(PM_GOVERNANCE 26節)、Family A/B/C/Zへの変更、K2 fallbackの改修、コスト削減目的の変更、Production code/Prompt変更(不具合でも変更せずSTOP報告)、TTS実行(本委任はtextまで。TTSは次委任)、Open Item close。
- Opus Gate: 不要(承認済み計画の実走)。
- 時間見込み: 90〜150分(API待ち含む)。
- 費用/日次: Cap JPY100(text工程)。本日累計約JPY79(REPORT_LEDGER L325/327/328/329/330/331合算)。日次1,000円内。承認区分: ユーザー承認済み(JPY205、2026-10-16)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなしだが、環境変数`TTS_EXECUTION_MODE=STANDARD`は全コマンドに明示)
T-3: 費用上限[Cap]=JPY100(本委任text工程)。E2E全体の承認上限JPY205。

T-0保存先(2本・**全文・固定ブロック短縮禁止**):
(1) 本委任文 → `docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01_05.md`
(2) `<<<USER>>>`〜`<<<END USER>>>`間を一字も変えずに → `docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01_USER.md`(先頭1行「# ユーザー指示原文(2026-10-16受領、Fable転記)」のみ付加可)。文字数記録。

## ユーザー指示(原文)
<<<USER>>>
# Claude Code／Fableへの指示
## Coffee正式E2E実走・原価実測・DQI効果観察

**管理ID：FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01**

### 1. 現在の状態・目的

- AUW：`PRODUCTION_WIRED`。ユーザー正式承認済み。
- DQIパッケージP：PM運用へのProduction実装完了。効果評価は未完了。
- Family X：承認済み最新仕様のProduction配線・テスト完了。Coffee正式実走によるruntime evidence待ち。
- Coffee E2E：**最大205円までユーザー承認済み**。
- Family X・Zが現在の開発対象。Family Yは将来対象。
- Family A・B・Cは開発停止。

今回の目的は、新しい仕様を探索することではなく、**既に承認・実装された仕組みを正式経路で動かし、品質と原価を実測すること**。

### 2. Coffee全面新規制作

既存管理ID：

`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`

既存の`SPEC_WIRING_MATRIX_01.md`および`COFFEE_E2E_PLAN_01.md`に従う。

- Coffeeはテーマだけを維持。
- Research、Fact Ledger、B3、Writer R0→R1→R2、英語化、Standard調整、KP、TTS、Assemblyを新規実行する。
- Standard／Advancedの試聴ページを完成させる。
- 工程ごとに正式仕様反映マトリクスと照合する。
- 必須Human Review／品質Gateを迂回しない。
- B3／R0／R1／R2のactual model_idと実送信Prompt SHAを記録する。
- retry／fallback／regenerationにおける承認済み仕様との整合を確認する。
- AUWは既存Production配線を利用し、再実装しない。

**Coffeeが完成しただけでFamily Xを`PRODUCTION_WIRED`としない。** 正式初回経路・後続経路・runtime evidence・test・SSOT・Git反映まで確認して判定する。

### 3. 費用管理・量産原価

**今回のユーザー承認上限：205円。**

この金額はCoffee E2Eに限定し、追加Trialや他案件へ流用しない。

費用について、以下を必ず計測する。

1. Research
2. Verified Fact Ledger
3. B3
4. Writer R0／R1／R2
5. Advanced英語化・Standard調整
6. KP生成・選定・解説
7. TTS・ASR
8. retry／fallback等の追加費用
9. 記事セット全体の実費

併せて、正式リリース後のBatch TTS適用を想定した**量産1記事セット（Standard＋Advanced）の原価**を算出する。

既存目標は**70円／記事セット**。

報告では以下を区別する。

- 今回の実測開発・検証費
- 通常の新規Production生成で反復する費用
- 今回だけの検証・異常対応費
- Batch適用による推定削減額
- 量産想定原価と70円目標との差額

Batch単価は正式な既存価格記録に基づいて計算し、未測定部分を実測値として扱わない。

70円超過の場合は、主因と改善余地を説明する。ただし、**今回は原価削減の追加Trial・モデル変更・品質仕様変更を行わない。**

日次開発費の原則1,000円／日（JST）も継続適用する。

205円を超える見込みが生じた場合は既存費用Gateに従いSTOPする。上限を超えないよう品質Gateを省略してはならない。

### 4. K2代替音声：Open Item登録のみ

K2はFamily XのStandard／AdvancedのKey Phrase英語フレーズ用正式TTS Style。

現行実装ではK2が不合格の場合、別Styleによる代替音声が使用される可能性がある。

今回のユーザー判断：

**この問題はCoffee制作から切り分け、Open Itemとして管理する。**

実施事項：

- 既存Open Itemとの重複を確認し、重複させず登録・更新する。
- K2代替音声の利用時、内部警告だけではユーザー報告が保証されない点を記録する。
- Coffee実走では代替音声の有無、件数、対象フレーズを記録する。
- 代替使用があれば完成報告に明示し、正式K2との不一致として扱う。

**今回、K2 fallbackの改修や追加Trialは行わない。**

Open Itemを登録したことだけを理由にCoffee制作を止めない。ただし、既存の必須品質Gateや受入条件を緩和しない。

### 5. DQI：今後10件の前向き効果観察

DQIパッケージPは既にPM運用へ実装済みである。

実装のやり直しは不要。

**今後の実際の受入案件10件について、DQIの効果を測定する。**

評価指標：

| 指標 | 目標 |
|---|---|
| 重大NGの被覆漏れ | 0件 |
| 承認済み事項の再質問 | 0件 |
| 機械Validatorの誤警告率 | 10%以下 |

各案件で以下を記録する。

- P1：受入判定と重大NGの整合
- P2：ユーザー判断前の4区分仕分け
- P3：不要なユーザー判断の提示抑制
- P4：機械Validatorの所見と妥当性

**10件分を集計し、まとめてPM向けに報告する。**

ユーザーの主観評価だけに依存せず、判定記録とValidator結果を用いて評価する。

一方、通常運用の観察では未知の重大NGを確実に発見できるとは限らないため、測定できなかった項目は「未検証」と明示する。

追加の有料盲検Trialは実施しない。

既知正解による机上評価と、今後の未知ケース観察を混同しない。

観察のためだけに不要な受入案件や追加タスクを作成しない。通常業務の進行に合わせて測定する。

### 6. Day 5・6

**PM自律運営モデルのDay 5・6は保留を維持する。**

DQIの10件観察をDay 5・6の代わりに完了扱いしない。

Day 5・6の詳細な実施項目を推測で補完したり、今回勝手に開始したりしない。

### 7. 作業範囲と禁止事項

実施対象：

- Family X Coffee正式E2E
- 工程別費用実測と量産想定原価計算
- K2代替音声Open Item登録
- DQI実運用10件の観察

禁止事項：

- Family A／B／Cの調査・Trial・改修
- Family Zの予防的追加改修
- Family Yの先行開発
- 新規の音声Style探索
- コスト削減を目的とした追加Trial
- 依頼されていないOpen Itemの全件棚卸し
- 不要なユーザー判断の発行
- Day 5・6の無断再開

新しい問題を発見しても、今回の依頼を逸脱して独立開発を始めない。

### 8. PM Gate・STOP条件

次の場合はSTOPし、事実・影響・必要な判断だけを報告する。

- Coffee費用205円の超過見込み
- Mandatory Human Review／品質Gate到達
- 承認済み仕様との重大な不一致
- 正式Production経路を使えない
- 新たな仕様採用・追加Trialが不可欠
- 既存の安全・品質・費用STOP条件に抵触

ただし、ユーザーが明示的に後回しにした非Blocking Open Itemを理由に、勝手に作業を止めない。

### 9. 報告事項

Coffee実走後、以下を報告する。

1. Standard／Advanced試聴ページ
2. 全工程の仕様照合結果
3. B3→R2のactual model_id・Prompt SHA
4. K2代替音声の有無と件数
5. 工程別の実測費用
6. Batch適用時の量産想定原価・70円目標との差
7. Production Wiring受入条件の達成状況
8. 未解決のBlocking事項のみ

DQIについては、**通常の受入10件が蓄積した時点で効果評価をまとめて報告**する。

FableはClaude Codeの完了報告をそのまま採用せず、CURRENT_SPEC・承認済み仕様・runtime evidence・テスト結果・QCDと照合して受入判定すること。

**ユーザーに不要な判断を求めないこと自体が、今回のDQIの重要な評価対象である。**
<<<END USER>>>

## 事前指定Read一覧(D-1厳守)
- `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/COFFEE_E2E_PLAN_01.md`(全文: stage分割・CP-A〜F・実行コマンド・前提条件・費用出典・§実行直前チェック)、`SPEC_WIRING_MATRIX_01.md`(text工程に関わる行: Research/Ledger/Risk Flagger/Review Queue/B3/W-1/英語化/Std/IOL/KP供給・選定・P8・P7文面 の「Coffee E2Eで確認する受入条件」列)。
- `er019_family_x_entertainment_production_runner_01.py`: stage定義・`--stage`の選択肢・構造的Mandatory STOP(`ER:24-27,456,468`付近)・`ER:98-103`(`verified_fact_ledger.txt`再利用)・`assert_budget_ok`・U-1・cost記録(`cost.json`の書き出し箇所、stage別に分かれているか)。`er012_e_family_entertainment_two_level_runner_01.py`: `writer_run_summary.json`(model_id_actual・prompt_sha256・chain_method・R1→R2契約の記録箇所)、IOL STOP。
- `er019_output/coffee_prices/run_l3_01/entry_point.json`(theme文字列の出典のみ。他は読まない)。
- `docs/pm/REPORT_LEDGER.md` 当日行(L325-335付近、本日累計の再計算)。
- `OPEN_ITEMS.md` Grep `K2`/`KEY_PHRASE_ENGLISH`/`ENGLISH_LOCK`/`OPEN-298 `/`OPEN-350 `(K2関連の既存Open Item重複確認)。空き番号Grep `^- OPEN-39[0-9] |^- OPEN-4[0-9][0-9] `。

## 手順
(手順0〜9・報告(RESULT_PACKET項目)は委任文本体のとおり。詳細: 0 sync / 1 T-0 / 2 Open Item2件登録(K2-FALLBACK-AUDIO-USER-REPORT-NOT-GUARANTEED-01、ER078-06C-TEST-DIRTY-TREE-DEPENDENCY-AND-LIVE-RESEARCH-CALL-01) / 3 DQI_PROSPECTIVE_OBS_01.md新規(#1-#3記入・Validator実走) / 4 実走前チェック(i)-(vii) / 5 stage(a)実走(Mandatory STOPで終了) / 6 evidence収集 / 7 費用実測表 / 8 SSOT(DECISION_LOG・REPORT_LEDGER・USER_DECISION_REGISTER) / 9 secret scan→明示add→commit→crbn経由push。報告=docs/pm/RESULT_PACKET_CEC5.md 1〜13項。)
注: 本ファイルの「手順」「報告」節は保存時に要約した(原委任文は会話ログに全文あり)。固定ブロック・ユーザー原文は全文。
