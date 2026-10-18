# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_01(ユーザー2026-10-18指示原文保存+E2E計画書+正式Production E2E text工程S0〜S5(Research/Ledger/B3/Writer R0-R2/Adv/Std)+音声plan S6。有料、記事制作上限JPY180のうちtext工程)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 承認済みFamily X正式Production経路による新規記事制作(ユーザー選定テーマ)。有料(LLM+Web検索)。
- 到達上限Status: `TEXT_STAGES_COMPLETE_AUDIO_PLAN_READY_PENDING_FABLE_CP`。音声有料工程S7〜S11はFable CP後の委任_02(記事内容のFable確認=内部CP、ユーザー承認待ちではない)。
- 禁止: 未承認仕様・Prompt探索・追加Trial/RLCT(er082)の方式・成果の混入(Research/Ledgerは正式Production経路のみ)/Production runner・Prompt・Style・Gateの変更/review_lock・Fact Lock・Risk Flagger契約・Human Reviewの迂回/累計JPY180超過見込みでの続行/有料runの再起動(26節)/旧記事・他Trial成果物の流用/テーマの変更(ユーザー選定。仮題の最終見出しはResearch事実に基づき決定可)/Family Z配線への変更。
- 固定ブロック: **E-1**(BAPE E2E_PLAN_01の工程表・仕様照合表11行をそのまま転用。最新正式仕様はCURRENT_SPEC Status表・S3W/PD06/E1/K2/P7/P8-KP/M2P0+A/IOL/6%減速/AUW/Risk Flagger/Fact Lockの各行をGrepで確認)/**D-1**(不適用=承認済み仕様のみ)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`)/**F-1**(費用は`cost.json`/`raw_usage_log.jsonl`実測を出典に工程別・Web検索/LLM別・実測/推定/未取得区分。未確認の数字は出さない)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_01.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY1.md`、ACTIVE_TASK.md先頭へ新ヘッダをEdit/Writeで追記、旧ヘッダ保持、sed禁止)。
- **並行作業注意(重要)**: 同じ作業ツリーで別agentがRLCT(er082_*)とFamily Z試聴ページ(er063/user_test/family_z_melos_02)の作業・commitを並行中。(a)`docs/pm/ACTIVE_TASK.md`は編集直前に再読し、自分のヘッダ1ブロックの先頭追記のみ行う(他ブロックを触らない) (b)git: 自分のファイルだけを`git add <path>`し、`.git/index.lock`があれば最大5分待って再試行、commit直前に`git status --porcelain`で自分の対象以外がstagedでないことを確認、pushがnon-ffなら`git pull --ff-only`後に再試行(force禁止)、conflictはSTOP報告 (c)`er082_output/`・`er026_output/`・`user_test/family_z_*`・`er063_*`に触れない。
- 使用モデル: Production配線済みrouting(変更しない)。報告に実model_idを記載。

## ユーザー指示原文(2026-10-18、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_USER.md`へ原文のまま保存し、文字数とsha256を報告)
---
# Claude Code／Fableへの指示
## Family X 新記事「中東情勢が悪化、イエメン・サウジ周辺で攻撃続く」

### 1. 目的

Family Xの正式Production E2Eを使用して、新しいNews記事をStandard／Advancedの両レベルで制作し、音声・試聴ページまで完成させる。

**記事テーマ：**
「中東情勢が悪化、イエメン・サウジ周辺で攻撃続く」

タイトルは仮題。Researchで確認した事実に基づいて、内容・見出しを最終決定すること。

### 2. 制作方針

前回の「退屈と攻撃性」と同じ承認済みProduction仕様を使用する。

- Research → Verified Fact Ledger → B3 → Writer R0/R1/R2
- Advanced英語化 → Standard調整
- KP選定 → TTS → AUW → Assembly → 試聴ページ
- Family Xの正式Production初回経路を使用
- 既存のretry／fallback／Human Review／品質Gateを維持
- 承認済み音声Style（PD06／E1／K2／P7／S3／P8-KP）およびStandard 6%減速を適用
- Risk Flagger、Fact Lock、重大誤解防止の既存仕様を遵守
- In One Line等のFamily X構成仕様を維持

未承認の新仕様、Prompt探索、追加Trialを行わない。

### 3. 今回のResearchで特に注意すること

中東情勢は変化が速く、報道間で数字や主張が異なる可能性がある。

以下を徹底すること。

1. 攻撃の**日時・場所・実行主体・標的・被害状況**を確認する。
2. フーシ派、イエメン政府、サウジアラビア、イラン等の立場・関与を混同しない。
3. 当事者の発表と、独立して確認された事実を明確に区別する。
4. 死傷者数、攻撃回数、被害施設などは報道時点を明示し、数字を安易に混ぜない。
5. 過去の攻撃と今回の新しい攻撃を混同しない。
6. 攻撃の目的・責任・報復関係について、確認できない推測を事実として書かない。
7. 特に重要なFactは複数の信頼できる情報源で照合する。

Reuters／AP／公的発表などを適切に参照し、公開日だけでなく事件発生日も確認すること。

**記事の狙い：**

事件を単に列挙するのではなく、「なぜイエメン周辺の紛争がサウジアラビアや地域全体に影響するのか」を、英語学習者にも分かりやすく、興味深いストーリーとして伝える。

ただし、面白さのために事実を誇張したり、政治的に一方的な解釈へ誘導したりしないこと。

### 4. 既存Production仕様の維持

以下を徹底する。

- Family Xの最新正式仕様をSSOTで確認
- CLI指定なしの既定Style Profileが正しく適用されることを確認
- B3／Writer／KP／TTS／AUWの既存Production経路をそのまま使用
- Storytelling品質と重大誤解防止の両立
- Risk Flaggerによる指摘を既存契約に従って処理
- 各音声RoleのStyle、Voice、actual model_id、routingを検証
- ASR・Validator・Integration・Assemblyの必要な検査をPASS

RLCTでTrial中のResearch／Ledgerコスト削減案は、Production採用前なので今回の正式経路へ混入させない。

Cross-Family同時配線原則も遵守する。ただし、今回が既存承認仕様による新記事制作である以上、Family Zで並行作業中の配線を無用に重複・競合させないこと。

### 5. 費用・効率

前回と同水準の**記事制作費上限JPY180**を想定する。

- 前回実績：JPY89.90
- 今回も同程度を目標とするが、情勢調査の難度により変動し得る
- 上限超過見込みの場合はSTOP
- 工程別の実費を記録
- 検索・再生成・retryの無駄を避ける
- 独立工程は安全な範囲で並列化する

JPY180は今回の制作管理上限とし、承認済みの他案件予算とは混同しない。別途の費用承認が必須となる契約・運用上の制約が見つかった場合は、有料実行前にSTOPして報告すること。

### 6. STOP条件

以下の場合は、独断で仕様変更・追加Trialを進めず報告する。

- 重要な事実関係を十分に検証できない
- 重大誤解・Fact Lock・Human Review等の必須Gateが発火
- 既存Production経路では解決できない品質問題が発生
- 費用上限超過が見込まれる
- 未承認仕様への変更が必要
- Production実行・音声検証に重大な問題がある

### 7. 最終報告

制作完了時には、以下を簡潔に提示すること。

1. 正式Production E2Eの完走結果
2. Standard／Advancedの試聴URL
3. 記事の要約と主要Fact
4. Fact Ledger／Risk Flaggerの結果
5. KP選定結果
6. TTS・AUW・ASR・Assemblyの品質結果
7. Style／model_id等のruntime evidence
8. 工程別実測費用と総額
9. commit／push、SSOT更新状況
10. 未解決Open Itemおよびユーザー判断事項

**音声・試聴ページまで完成させたらSTOPし、ユーザーの試聴判断を待つこと。**

Fableの技術的PASSとユーザー試聴PASSは区別する。

既存Productionに問題がなければ、途中の不要な報告や追加承認待ちを挟まず、前回同様、完成音声まで進めること。
---

## Fable決定(本委任で確定)
- 費用: 本記事の制作管理上限JPY180はユーザー本指示で承認済み(7-7の100円超ユーザー判断は本原文で充足。別案件予算と混同しない)。text工程runner `--budget-jpy 110`、音声runner `--budget-jpy 70`(BAPEと同じ配分。合計上限180はE2E_PLANで管理し、text実績に応じて音声側へ残額を配分可、ただし総額180を超えない)。当日(10/18 JST)費用: RLCT 1bが並行中(上限493)+本件180 ≤ 1,000の範囲で管理。実行前に当日累計を`raw_usage_log`系から集計して記録。
- slug=`middle_east_yemen_saudi`、run=`run_mey_01`、run-label=`MEY-E2E-01`、out-dir=`er019_output/middle_east_yemen_saudi/run_mey_01`、計画書=`docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01/E2E_PLAN_01.md`(BAPEの`E2E_PLAN_01.md` §1〜§11を転用、THEME/slug/out-dir/run-label置換、§3テーマ選定=ユーザー選定2026-10-18と記録)。
- `--theme`はユーザー仮題「中東情勢が悪化、イエメン・サウジ周辺で攻撃続く」をそのまま渡す(BAPEでの`--theme`渡し方を踏襲。英語補助が必要な経路なら計画書に記載)。
- ユーザー§3のResearch注意7項目は、Production Prompt変更ではなく**Research成果の受入チェック**として適用する: Verified Fact Ledgerの各Factについて「日時/場所/主体/標的/被害」「発表元(当事者発表 vs 独立確認)」「報道時点」「出典2本以上(中心Fact)」を`E2E_PLAN_01.md §12`の表で確認し、不足があればSTOP(Prompt改変で補わない)。
- Fable CP(委任_02前): 記事本文の事実性・中立性(一方的解釈への誘導なし)・数字の時点明示・In One Lineの因果誇張なしをFableが読んで判定。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_委任_03.md`(手順の先例。コマンド・CP・費用集計の形式)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01\E2E_PLAN_01.md` §1〜§13(転用元)
- `C:\Users\tensh\eigo-radio\er019_bape_cost_03.py`(費用集計の雛形→`er019_mey_cost_01.py`)
- `C:\Users\tensh\eigo-radio\er019_output\boredom_aggression\run_bape_01\audit\cost_by_stage_text_03.json`(出力形式)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `共通仕様のFamily別配線Status表`(X列がPRODUCTION_WIREDであることを§5仕様照合表に転記)/Grep `fx_20261017`(既定profile)/Grep `Risk Flagger|Fact Lock`(契約の所在行を計画書に記載)。
- `OPEN_ITEMS.md`: 末尾の最大番号をGrep `OPEN-41[0-9]`で確認し、新規`OPEN-4xx FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 [TEXT_STAGES_COMPLETE…]`を起票。
- `DECISION_LOG.md`: 末尾に委任_01エントリ(ユーザー指示受領・テーマ選定=ユーザー・text工程結果・費用)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 本件の費用180承認を判断済みとして登録(次番号)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 作業(順序)
S0 T-0保存・原文保存・計画書作成・開始条件チェックリスト(§1、全PASSでなければ有料生成しない)。当日累計の集計記録。
S1 research(`--stage research`)→S2 storyline_b3→S3 writer→S4 advanced→S5 standard(BAPE §4の工程表とCLIをそのまま踏襲。各stage後に`cost.json`累計と110・180の残を記録。超過見込みでSTOP)。
Research受入チェック(ユーザー§3、§12表)→不足はSTOP報告(Prompt改変・手動Fact追加はしない)。
S6 音声plan(`er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_01 --level both --stage plan`、CLI指定なし→`audit/style_profile.json`でfx_20261017の6 role sha確認)。有料TTSは起動しない。
費用集計`er019_mey_cost_01.py`→`audit/cost_by_stage_text_01.json`(工程別・Web検索/LLM別・実測/推定/未取得)。
計画書§12に実走記録(記事タイトル最終案・In One Line・Fact Ledger件数V/A/R・B3選定Fact・Risk Flagger候補・HR/Lock発火有無・費用)。SSOT追記→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`、runnerは`-I`なし=BAPE先例どおり)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_01.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py --theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --slug middle_east_yemen_saudi --out-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --run-label MEY-E2E-01 --budget-jpy 110 --stage research 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\console_s1_research.txt`
- 同runnerで `--stage storyline_b3` / `--stage writer` / `--stage advanced` / `--stage standard` を順に(他引数同一、consoleは`console_s2_b3.txt`〜`console_s5_standard.txt`)。
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_01 --level both --stage plan 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\console_s6_plan.txt`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er019_mey_cost_01.py --run-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --out C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\audit\cost_by_stage_text_01.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在script名に置換)
(引数名がBAPE先例と異なる場合は先例のconsole/計画書の実コマンドに合わせて置換し、置換内容を報告)

## SSOT追記文(要点)
- OPEN-4xx(新規): 「FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01: ユーザー2026-10-18指示(テーマ選定=ユーザー、上限JPY180)。text工程S0〜S5完了(実測JPY x)、音声planS6確認、音声有料工程はFable CP後。Status=TEXT_STAGES_COMPLETE_AUDIO_PLAN_READY_PENDING_FABLE_CP」。
- DECISION_LOG: 「2026-10-18 委任_01: 受領・計画・text工程結果(タイトル最終案、Fact Ledger V/A/R、費用)。Production変更なし」。
- REGISTER: 「#111(判断済み 2026-10-18) 中東記事の制作費上限JPY180承認(原文sha)」(番号は既存最大+1に合わせる)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 2件(+_check.json)、E2E_PLAN_01.md、`er019_output/middle_east_yemen_saudi/run_mey_01/**`のうちBAPE先例と同じ追跡対象(article.md/parts.json/audit json/research_ledger/storyline/console。wav・巨大binary不可)、`er019_mey_cost_01.py`、OPEN_ITEMS.md、DECISION_LOG.md、USER_DECISION_REGISTER_01.md、REPORT_LEDGER.md。msg: `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_01: ユーザー2026-10-18指示(中東情勢記事、上限JPY180)原文保存+E2E計画+正式Production E2E text工程S0〜S5実走(Research/Ledger/B3/W-1/Adv/Std、実測JPY x)+音声plan S6(fx_20261017確認)+費用集計+SSOT(音声有料工程はFable CP後)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY1.md`)
4行: (1)整合(計画書§5仕様照合表の結果、開始条件§1)(2)Production到達経路=既存経路のみ(変更0)(3)成果物とcommit sha、記事タイトル最終案・In One Line全文・Fact Ledger V/A/R件数と中心Factの出典数・Research受入チェック表の結果・Risk Flagger候補件数・HR/Lock発火有無・工程別費用(text実測/110、E2E累計/180)・当日累計/1,000・S6 style_profile sha一致(4)撤去/残置。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check結果。自己チェック: RLCT方式の混入0/テーマ不変/Prompt・Gate不変/累計≤180/有料TTS未起動/並行作業ファイル不干渉。Fable CP用に`article.md`(a2/b1b)の絶対pathを明記。
