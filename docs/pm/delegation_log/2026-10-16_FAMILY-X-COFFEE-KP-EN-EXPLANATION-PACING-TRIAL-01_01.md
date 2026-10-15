## 管理ID

`FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01` 委任_01(ユーザー指示原文の保存+現行原稿/Prompt/TTS経路の確認+費用見積+8 Prompt×5本=40音声のTrial生成+QA/ASR+指標計測+試聴ページ[GitHub Pages]+SSOT記録+commit/push)。並行: AUW 委任_10(er078/er007系)、FCJ 委任_03(er079/er013系)が同時に進行しcommit/pushを行う。**本委任の編集・新規ファイルはそれらと重ならない**(新規`er080_*`・`user_test/coffee_kp_pacing_trial_01/`・SSOT末尾追記・delegation_log)。Git競合回避: commit時`.git/index.lock`があれば60秒待ち再試行(最大10回)。mainへの反映は`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`(ff不可なら`--no-ff`、競合は中止報告)→`git push origin main`(rejectedなら`pull --ff-only`→再push、最大3回)。SSOT追記直前に`git fetch origin; git merge --ff-only origin/main`で最新化し、追記は節末尾/ファイル末尾へ。他委任の未追跡file・本番state fileはaddしない。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Offline・Trial専用ディレクトリ)。到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`のいずれか(**Production反映禁止。8案の試聴ページと比較結果を提示したところでSTOP**。ユーザー採用判断待ち)。
- 禁止: Coffeeの現行Production Prompt・style profile・原稿・Key Phrase・解説文の変更、他記事・他Familyへの展開、8案以外の候補追加・改変、予定40音声以外の追加Take・派生案・再Trial(ユーザー承認なし)、生成条件を変えた不合格音声の救済、既存完成音声の上書き、Production Master Store/Production出力dirへの書込、`git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、STOPセンチネル削除・回避、HR Lock迂回、新TTSモデル探索・不要なResearch、有料runの再起動(26節)、「試聴合格」等の未試聴評価語の記載。
- **STOP条件(本委任内)**: (t1)費用見積が上限JPY40を超える見込み→生成前にSTOP報告。(t2)ASR失敗・TTS障害等で予定外のAPI呼出(40音声の規定attempt[Production同一のretry回数]を超える呼出)が必要になった→原因と影響を記録しSTOP。(t3)STOP_NOTICE/STOP/STOP_ALL該当(stop_scope_check rc≠0)。
- Opus独立技術レビューGate(11-3): 非該当(Trial、Production変更なし、新構造なし)。
- 開発・評価用途の最新モデル原則(25節): TTSは**ユーザー固定条件により現行Production同一`gemini-3.8-flash-lite-tts`**(例外理由=ユーザー指示§2固定条件)。ASRは現行Production経路の既定(Primary OpenAI/Secondary Azure)。報告に使用モデル名・最新か・理由を記載。
- 時間見込み: 全体2.5〜3.5時間(確認・見積30・生成40音声 30〜45・QA/指標30・ページ30・SSOT/Git/Pages確認30)。並列化: 指標集計script・ページ雛形は生成待ち中に先行作成(並列可)。生成は直列(同一TTS経路・rate limit・費用meter)。
- 費用/日次: 当日(2026-10-16 JST)既使用=AUW 約JPY1.3確認済み+進行中(AUW 委任_10 見積6・FCJ 委任_03 見積8)/本委任見積 **事前に作成して記録**(目安: 40 clip×TTS JPY0.062+Primary ASR+NG時Secondary、出典`er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md:113,320`、および現行KP解説TTS経路の既存費用記録があればそれを優先)/改善見込み 中〜高/承認区分: C(ユーザー2026-10-16指示によりTrial承認済み、Production採用は別)。
- T-3定型文: 「上限¥40(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」ただし本件はユーザー指示§7「ASR失敗・TTS障害などで予定外のAPI呼出が必要になった場合は、原因と影響を確認してSTOPする」が優先(t2)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。(定型文は「性質」欄)

T-0保存先: `docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_01.md`(本委任文**全文**。要旨化禁止)。加えて下記「ユーザー指示(原文)」本文を一字一句そのまま `docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_USER.md` へ保存(冒頭1行「2026-10-16 ユーザー指示原文(Fable受領)」を付す)。

## ユーザー指示(原文)

# Claude Code／Fableへの指示
## Coffee Advanced 英語解説TTS・速度／ポーズ改善Trial

**管理ID：FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01**

**現在Status：TRIAL（未検証）**

**今回の到達上限：VALIDATED**

**Production反映：禁止。ユーザー採用判断待ちでSTOP。**

## 1. 目的

Coffee記事のAdvanced向けKey Phrase英語解説について、現在の音声は全体的にやや遅く、意味の塊ごとのポーズが長いため、不自然に聞こえる。

英英解説であることから、**ややゆっくり・明瞭で理解しやすい読み方を維持しつつ、過剰な減速と不自然なポーズを改善する。**

通常のニュース朗読の速さを目指すTrialではない。速度変更は控えめとする。

## 2. 対象・固定条件

- 記事：Coffee
- レベル：Advancedのみ
- Section：Key Phraseの英語解説（explanation_en）
- 対象原稿：現在のCoffee記事で実際に使用している英語解説5本
- 比較：8 Prompt × 5本＝40音声
- Voice：現行Productionと同じAoede
- TTSモデル：現行Productionと同じ `gemini-3.8-flash-lite-tts`
- 音声生成・trim・その他条件：原則現行Productionと同一
- 原稿・Key Phrase・解説文の変更：禁止
- Standard日本語解説、英語Phrase音声、その他Section：対象外

最初に現行Coffee記事の解説原稿5本、採用Prompt、TTS経路を確認する。

現行Promptは、Coffee用style profileのP3を正本とし、Productionで実際に送信されるStyleと照合する。

**既存完成音声は比較用として保存し、上書きしない。**

## 3. 比較する8 Prompt

### P0：現行Production

```text
clear, precise, at a measured pace, without dragging Let the sentence flow from its first word to its last, without stopping partway through.
```

### P1：最小変更・ポーズ調整

```text
clear, precise, at a measured pace, without dragging Keep pauses between phrases brief and natural, letting the explanation flow smoothly.
```

### P2：ややゆっくりを明示

```text
Clear and precise, at a slightly slower than conversational pace. Keep the explanation flowing naturally, with brief pauses.
```

### P3：語句の連結重視

```text
Clear, precise, at a measured pace, without dragging. Connect the words and phrases naturally, with no unnecessary breaks.
```

### P4：自然な英語教師の説明

```text
Explain clearly and naturally, like a patient English teacher speaking to a learner. Use a slightly relaxed pace and smooth phrasing.
```

### P5：理解に必要な短い間だけを許容

```text
Clear and easy to follow, at a gently measured pace. Use only short, natural pauses where they help understanding.
```

### P6：一文としての滑らかさ

```text
Clear, precise, and gently paced. Deliver the explanation as one smooth, connected thought, without stretching the spaces between phrases.
```

### P7：速度・リズムのバランス型

```text
Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm, with brief transitions between phrases and no drawn-out pauses.
```

上記8案は比較対象として固定する。Claude/Fableの判断で候補を追加・改変しない。

## 4. Trial実施方法

1. Coffee記事の解説5本を、現行Productionの正本から取得する。
2. 8案のStyle文字列をそのまま使って、各5本のTTSを生成する。
3. モデル・Voice・原稿・パラメータを統一する。
4. Trial用の独立ディレクトリへ保存する。
5. 既存の安全QA／ASR検証を行う。
6. 5本を候補別・原稿別に比較できる試聴ページを作成する。

P0は現行Production Promptで新規生成した音声を原則使用する。既存Production音声も参照として表示してよいが、同条件の比較結果と混同しない。

生成条件を変更して不合格音声を都合よく救済しない。

**予定40音声以外の追加Take・派生案・再Trialはユーザー承認なしに実施しない。**

## 5. 評価項目

| 評価 | 内容 |
|---|---|
| 音声速度 | 過度に遅くなく、Advanced英英解説として適度にゆっくりか |
| 文中ポーズ | 意味の塊ごとの長い無音が減っているか |
| リズム | 一文として自然につながっているか |
| 明瞭性 | 英語学習者にとって単語が聞き取りやすいか |
| 自然さ | 機械的・ぶつ切り・過剰な教師口調にならないか |
| 安定性 | 5本で同じ傾向が得られるか |
| ASR／QA | 原稿と音声の内容が一致し、品質に問題がないか |

可能な範囲で、実測WPM、音声全長、発話時間、無音の長さと回数を比較する。

特に**文中ポーズと文末無音を分けて記録**する。

ただし、数値だけで優劣を決めず、最終的には自然さ・聞き取りやすさを重視する。

実際に試聴・評価していないものを「試聴合格」と記載しない。

## 6. 試聴ページ

ユーザーが比較しやすいシンプルなページを作成する。

- 各Key Phraseの英語解説原稿を表示
- 同じ解説文についてP0〜P7を横並び、または切替で比較
- 個別再生ボタン
- Prompt一覧・狙いの表示
- 必要に応じた音声長・WPM・ポーズ指標
- 既存Production完成音声との比較

可能なら、**5本の解説ごとに8候補を聞き比べる構成**とし、速度・間の違いが直感的に分かるようにする。

最終報告には、必ずユーザーがアクセス可能な試聴URLを添付する。ローカルパスだけで報告を終えない。

## 7. QDCと費用

- 既存の原稿・モデル・音声生成資産を再利用する。
- 新しいTTSモデル探索や不要なResearchを行わない。
- 事前に40音声の費用見積もりを作成する。
- 既存のTrial予算・STOP条件を守る。
- 実費・呼出回数・失敗件数を記録する。
- ASR失敗・TTS障害などで予定外のAPI呼出が必要になった場合は、原因と影響を確認してSTOPする。
- 独立した分析・ページ構築等は並列化してよいが、無駄な生成は避ける。

## 8. Trial終了時のGate

Trial結果を以下のいずれかに分類する。

- **VALIDATED**：改善候補として評価可能。
- **REJECTED**：改善効果不足、品質問題、または安定性不足。
- **USER_DECISION_REQUIRED**：候補の採否や追加検証についてユーザー判断が必要。

**Trial成功はProduction採用ではない。**

Coffeeの現行Production Prompt・style profileは変更しない。

他記事・他Familyへの展開も禁止する。

ユーザーが正式採用する場合のみ、別途APPROVED_FOR_PRODUCTIONとしてProduction Wiringへ進む。

## 9. 最終報告

以下を簡潔に報告する。

1. 実際に使用したCoffee英語解説5本。
2. 8候補×5本の生成成否。
3. 試聴ページURL。
4. 速度・ポーズ・自然さの比較結果。
5. 改善効果が見込める上位候補。
6. ASR／音声QAの結果。
7. 実費・TTS呼出数。
8. 各候補のTrial Status。
9. ユーザー判断が必要な事項。

**8案の試聴ページと比較結果を提示したところでSTOPすること。**

ユーザー承認なしに候補PromptをProductionへ反映しない。

(ユーザー指示原文ここまで)

## KPI provenance欄

- 40音声の生成成否・ASR/QA結果: `fresh`(Trial専用dir、Production同一経路のleaf関数を同一パラメータで呼ぶ)。
- 既存Production完成音声(参照表示): `reuse`(read-only、上書きしない)。
- WPM/全長/発話時間/無音(文中ポーズ・文末無音分離): `fresh`(生成wavからの計測。手法=既存の無音検出があれば流用、無ければRMS閾値ベースを新設し閾値を記録)。
- E2E自己確認「fresh Production初回pathを含むE2E値か」: No(Trial専用経路。Production Wiringは未)。
- 主観評価(速度・リズム・自然さ)は**ユーザー試聴待ち**。Sonnet/Fableは数値と、ASR/QA結果と、「数値上の傾向」までを記載し「試聴合格」とは書かない。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grep `style profile`/`P3`/`measured pace` → Coffee用style profileの正本節(Advanced KP英語解説のStyle定義。該当行±30)。Grep `Coffee`/`coffee_prices` → 現行Coffee記事のProduction出力dirとKP解説(explanation_en)の所在。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `Coffee`/`#69` → Coffee関連の既決・未決(監査(a)〜(d)が未決であることを把握。本Trialはそれと独立)。
- 現行Coffee記事のKP解説原稿5本: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/`配下(Grep `explanation_en`で`parts.json`/`key_phrases*.json`等を特定→該当5本を逐語で取得。**変更禁止**)。既存完成音声(KP解説wav)のパスも特定(read-only)。
- KP英語解説のProduction TTS経路: Grep全repo `*.py` `measured pace` / `without dragging` / `style_profile` / `explanation_en` → 実際にStyleを組み立てて送信する関数(ファイル:行)と、Productionで送信される最終Style文字列(P3プロファイル+前後に付加される文言があればそれも)。`er071_*`/`er019_*`/`er003_*`のKP leaf(`_kp_en_two_stage`等、`KP_EXPLANATION_MAX_ATTEMPTS=3`)を確認。
- 先行Trialの雛形(構成・ページ・隔離方法の参考、流用可): `docs/pm/delegation_log/2026-10-15_STANDARD-KP-JA-TTS-STYLE-TRIAL-02_01.md`(SKJT-02: Style比較Trialの隔離dir・ページ構成)、`user_test/fixed_shell_champion_trial_02/index.html`(候補×原稿の試聴ページ構成)。該当harness script(Grep `STANDARD-KP-JA-TTS-STYLE-TRIAL-02`で`er0XX_*.py`を特定)の主要部分。
- 費用単価: `er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md` L110-115、L315-325。KP解説の既存費用記録があればそれを優先(Grep `kp`/`explanation` in `audit/raw_usage_log.jsonl`の該当run)。
- 無音計測の既存実装: Grep全repo `*.py` `silence`/`rms`/`trim` → 既存の無音検出・trim関数(Production同一のtrim条件を適用するため)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Trial dir: 新規 `er080_output/coffee_kp_en_explanation_pacing_trial_01/`(`er080`が使用済みなら次の空き番号、記録)。配下: `audio/<p0..p7>/<kp01..kp05>.wav`、`audit/`(usage_log・asr結果・QA結果・費用meter・STOP)、`metrics.json`、`TRIAL_REPORT_01.md`。
- 試聴ページ: 新規 `user_test/coffee_kp_pacing_trial_01/index.html`(+音声は同dir配下`audio/`へ複製またはPagesから到達可能な相対パス)。正式配布経路=GitHub Pages `https://shimomura055.github.io/eigo-radio/user_test/coffee_kp_pacing_trial_01/`(PM_GOVERNANCE 9-5/`PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01`。blob/raw URLは標準経路として使わない)。
- SSOT: `DECISION_LOG.md`末尾に新節「FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01(2026-10-16)」(ユーザー承認原文位置・固定条件・8案・結果・Status・費用。Production不変を明記)+索引1行。`OPEN_ITEMS.md`末尾に新規OPEN 1行(「Coffee KP英語解説Pacing Trial: ユーザー試聴・採否待ち(USER_LISTENING_PENDING)。候補採用はAPPROVED_FOR_PRODUCTION別判断」、番号は起票直前に再Grepして空き番号)。`docs/pm/REPORT_LEDGER.md`に行追加(初回報告未)。`CURRENT_SPEC.md`は**変更しない**(Production仕様不変)。`docs/pm/ACTIVE_TASK.md`(gitignore)に本管理IDの行を追加。

## 実行コマンド全文

手順0: `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main; git branch --show-current`(`work/post-merge-01`上で作業)。`New-Item -ItemType Directory -Force er080_output\coffee_kp_en_explanation_pacing_trial_01\audit`。`.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 --run-dir er080_output\coffee_kp_en_explanation_pacing_trial_01` rc=0確認。
手順1(確認・見積、API 0): 原稿5本・採用Prompt(Productionで実送信される最終Style文字列とP0の文字列が一致するか照合。不一致なら差分を記録し**P0はユーザー指定文字列をそのまま使う**)・TTS経路・trim条件・ASR/QA経路・既存完成音声パスを `TRIAL_REPORT_01.md` §1に記録。見積を§2に記録(40 clip×attempt見込み×単価、出典)。見積>JPY40なら(t1)STOP。
手順2(harness作成): 新規 `er080_coffee_kp_pacing_trial_01.py`: 引数 `--prompt-set all|p0..p7 --out <dir> --budget-jpy 40 --execute`; Production同一のleaf TTS関数をStyle文字列だけ差し替えて呼ぶ(モデル`gemini-3.8-flash-lite-tts`・Voice Aoede・trim・その他パラメータ同一)、Production同一の安全QA/ASR検証(統一judge経由ならそのまま。NG時のretryはProduction同一回数まで。超える場合は(t2)STOP)、費用meter・呼出回数・失敗件数の記録、STOPセンチネル監視(`er080_output\...\STOP`)、**書込先は全てTrial dir**(Production Master Store/HR queue/attempt_historyへ書く経路なら、隔離できる引数を使うか、書込差分を実行前後で記録し報告)。
手順3(生成、有料): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er080_coffee_kp_pacing_trial_01.py --prompt-set all --out er080_output\coffee_kp_en_explanation_pacing_trial_01 --budget-jpy 40 --execute`(実行前にT-2追記(1)〜(4)を確認・記録)。
手順4(指標、API 0): `.venv\Scripts\python.exe er080_coffee_kp_pacing_metrics_01.py --in er080_output\coffee_kp_en_explanation_pacing_trial_01 --out er080_output\coffee_kp_en_explanation_pacing_trial_01\metrics.json`(全長・発話時間・WPM[語数/発話時間]・無音回数/長さを**文中ポーズと文末無音に分離**、閾値・手法を記録。既存Production完成音声5本も同指標で計測して参照列に)。
手順5(ページ): `user_test/coffee_kp_pacing_trial_01/index.html`(5本の解説ごとにP0〜P7を横並び/切替、個別再生、原稿表示、Prompt一覧と狙い、指標表、既存Production音声列[参照と明示]、ASR/QA結果列。シンプルなHTML、外部JS不要)。音声は`user_test/coffee_kp_pacing_trial_01/audio/`へ複製(mp3化は既存Trialの方式に合わせる。wavのままでも可)。
手順6(SSOT・Git): Grep手順どおり追記。secret scan(`--paths`)hits=0 → `git add er080_coffee_kp_pacing_trial_01.py er080_coffee_kp_pacing_metrics_01.py er080_output/coffee_kp_en_explanation_pacing_trial_01/TRIAL_REPORT_01.md er080_output/coffee_kp_en_explanation_pacing_trial_01/metrics.json er080_output/coffee_kp_en_explanation_pacing_trial_01/audit user_test/coffee_kp_pacing_trial_01 DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_01.md docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_01.md_check.json docs/pm/delegation_log/2026-10-16_FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01_USER.md`(Trial dirのwavが`.gitignore`対象なら`user_test`側の音声のみ追跡されることを確認。Pagesから再生できることが必須) → `git commit -m "FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 委任_01: Coffee Advanced KP英語解説 8 Prompt×5本 Pacing Trial(Trial専用dir、Production不変、JPY <実費>)+試聴ページ"` → crbnでmainへff→push → main dirでff。
手順7(Gate 7 URL確認): push後、GitHub Pagesの反映を待ち(最大10分、60秒間隔)`Invoke-WebRequest -UseBasicParsing https://shimomura055.github.io/eigo-radio/user_test/coffee_kp_pacing_trial_01/index.html`が200、および音声1本のURLが200であることを確認して記録(未反映なら「Pages反映待ち、次回確認」と明記)。

## SSOT追記文

上記Grep手順の文面(実値置換)。DECISION_LOG節の末尾に必ず「Trial結果はProduction採用ではない。Coffee現行Prompt/style profile不変。採用はユーザーのAPPROVED_FOR_PRODUCTION判断。」を含める。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: あり(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`、追記のみ)。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない。AUW/FCJのfile・本番state file・他委任の未追跡fileはaddしない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_CKP1.md`に、ユーザー指示§9の9項目(1 使用した解説5本[逐語] / 2 8×5生成成否表 / 3 試聴ページURL[Pages、200確認結果] / 4 速度・ポーズ指標比較表[文中ポーズと文末無音を分離、数値上の傾向。主観評価は試聴待ちと明記] / 5 数値上の上位候補[「試聴合格」とは書かない] / 6 ASR/QA結果[clipごとのstate、Secondary呼出、HR該当] / 7 実費・TTS呼出数・失敗件数・使用モデル名[最新か/理由] / 8 各候補のTrial Status案[VALIDATED候補/REJECTED候補/判断待ち、根拠] / 9 ユーザー判断事項)+T-0結果+P0とProduction実送信Styleの照合結果+shared_state差分+STOP該当有無+逸脱+所要時間+受入記録5項目(当初目的=§1・§2原文逐語/最終成果物/証拠/一致・不一致/判定)。
