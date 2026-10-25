## 管理ID
FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01(2026-10-26 JST、Family X新規記事『AIを仮想の島に放置したら、勝手に神殿を建て始めた？』Standard/Advancedの通常Production制作。テーマはユーザー選定済み)。並行タスク: FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_04が稼働中(所有=`docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/`・`er118_*`・`er118_output/`・`user_test/fz_dialogue_context_trial_02/`・`docs/pm/RESULT_PACKET_FZDC4.md`。共有SSOTは編集しない取り決め)。本委任はそれらに触れない。共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)の編集権は本委任が持つ。X runnerの出力dir・`user_test/family_x_ai_island_temple_01/`は本委任が所有。

## 性質/到達上限Status/禁止事項
- 性質: Production(承認済みFamily X Production仕様による通常の新規記事制作、Trialではない)。到達上限: 公開試聴ページ完成=`USER_LISTENING_PENDING`。ユーザー最終試聴PASS・記事採用の代行禁止。`APPROVED_FOR_PRODUCTION`の新規宣言なし。
- 禁止: 未承認仕様・DEV専用経路・新flagの使用、既存Prompt/閾値/Gate/retry/fallbackの変更、STOP/HR Lock/Gateの迂回、Human Reviewの独断確定(KP HR・文法HRの「HRなし宣言」(`--kp-review auto`等、`declared_by`+`user_ref`必須)は**ユーザーが宣言していないため使わない**。既定どおり待機(rc=4)で止めてFableへ報告)、NG音声の最終採用(`approved_by="user"`はユーザーのみ)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用上限: 上限¥150(Guardrail、案件Cap。Fable 7-7: 承認済みScope内・300円以下は自律)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- Opus独立技術レビューGate: 非該当(承認済み正式経路の通常制作。設計変更なし)。
- 時間見込み: 全体2〜3時間(Research/本文/英訳 30〜45分、TTS/ASR/Gate 45〜60分、組立/ページ/検査 15分、SSOT/Git 15分)。並列化: Std/Advは正式runnerの既定(同一runner内の並列/直列)に従う。別記事runとの並列はしない(X runnerプロセスが他に稼働していないことを起動前に確認)。起動間隔150秒以上・同一run 5分3回禁止(RESTART_STORM、OPEN-480)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約0.2(出典: RESULT_PACKET_YPL9/10=0円、FZ委任_04感情LLM見込み0.2円。起動前に`py docs/pm/tools/daily_dev_cost_01.py`で実測)/残JPY約999/本委任見積JPY50〜70(根拠: 直近X記事セット実績46.82円・63.78円[USER_DECISION_REGISTER_01.md:374,388]、上限=Guardrail 150円)/改善見込み高/承認区分: C:承認済みscope内(ユーザー本日指示、300円以下、日次1,000円以内)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

## ユーザー指示(原文)
次の原文を**一字も変えず** `docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER.md` に保存する(先頭に「ユーザー指示原文(2026-10-26、Fable経由で逐語保存)」の1行を付けてよい):

```
# Family X｜新規記事制作指示

## 1. 制作対象

**タイトル案：AIを仮想の島に放置したら、勝手に神殿を建て始めた？**

Family Xの新規記事として、Standard／Advancedの2レベルを制作してください。

今回はユーザーによるテーマ選定済みです。Trialではなく、承認済みFamily X Production仕様による通常の記事制作です。

**到達目標：** 記事本文、英訳、音声、Key Phrase、文法解説、正式組立、品質検査、ユーザー最終試聴ページの完成。

制作・公開試聴ページの提出は承認しますが、ユーザー最終試聴PASSを代行してはいけません。

## 2. 参考情報・Research

以下の一次資料を優先してください。

- MIT研究論文「Is this machine playing?」
  https://machineplaying.org/paper/
- MITによる研究紹介
  https://news.mit.edu/news-clip/fast-company-259
- TechCrunchによる報道
  https://techcrunch.com/2026/10/22/left-alone-with-nothing-to-do-ai-agents-started-playing/

これらは参考資料であり、本文や結論を無批判に採用するものではありません。通常のResearch／Fact管理工程で裏取りしてください。

特に以下を確認してください。

- 13体のAIエージェント「Eko」を、仮想の島でそれぞれ30時間稼働させた実験。
- 具体的な目標を与えなかったところ、塔の建設、遊びの発明、模様の制作などが発生したこと。
- 神殿・記念碑・儀式に相当する行動について、研究記録上の具体的事実と研究者の解釈を区別すること。
- 島での経験後に課題成績が向上したという研究結果と、その限界。
- 論文がプレプリント段階であること。

**重要：AIが本当に祈った、宗教を持った、感情や意識を獲得した、と断定しないでください。**

また、前回の候補提示時には直近24時間の記事として紹介されましたが、研究・報道自体はそれ以前に公開されています。今回はユーザーが題材を明示選定しているため、24時間条件の例外として扱います。

## 3. 記事の方向性

Family Xの既存仕様に沿って、意外性とストーリー性を重視してください。

今回の魅力は、目標を与えられなかったAIが、何もしないどころか自分で活動を始め、神殿のようなものまで作ったという展開です。

一方、研究の本質は単なる奇妙なAIの行動ではなく、**自発的な探索や遊びが、その後の学習・課題遂行につながる可能性**にあります。

この2つを自然なストーリーとして結び付けてください。

ただし、この構成案を固定せず、既存B3／Writer／Entertainment Revisionの役割と正式仕様に従い、最も面白く正確な記事にしてください。

## 4. Production仕様・品質

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMSを確認し、現在の承認済みFamily X Production仕様を適用してください。

特に、直近で正式採用された以下の機能のProduction反映状況に注意してください。

- B3と中核数値保持方式
- Standard／Advancedの英訳・表現品質仕様
- Key Phrase選定、Human Review
- Part 1英語解説、Part 2文法・構文解説
- TTS速度・Chunk分割・ポーズ
- Primary／Secondary ASR、発音同等性、音声品質検査
- retry／fallback／resume

未承認仕様を暗黙に採用せず、既存の正式初回Production経路を使用してください。

Human Reviewが必要な場合は既存仕様どおり進め、ユーザーによる承認が必要な音声・本文は独断で確定しないこと。

## 5. 実行・QCD

- 品質 ＞ 完成速度 ＞ 量産単価の優先順位を遵守。
- 独立工程は並列化し、不要な待機・日付分割を避ける。
- 既存の成果物・キャッシュを活用し、不要なAPI呼び出しを避ける。
- 量産単価70円／記事セットの目標に対する実績を記録。
- 承認済み開発予算・個別上限の範囲で自律的に対応。
- 不具合は既存仕様・承認範囲内で原因究明、修正、検証まで実施。
- 重大な品質問題、明示STOP、未承認仕様の採用が必要な場合は停止・報告。

## 6. 完成報告・受入条件

Standard／Advancedについて、以下を報告してください。

1. 正式な記事タイトルと本文品質評価
2. Fact管理・出典確認の結果
3. Key Phrase・Human Reviewの結果
4. 音声・ASR・組立・公開検査の結果
5. 実際のProduction経路・モデル・Prompt等のruntime evidence
6. Fable独立受入結果
7. 実費と記事セットあたりの量産単価
8. SSOT・Git反映状況と残るOpen Item
9. **Standard／Advancedの全文・通し再生・パート別再生ができるユーザー試聴URL**

ユーザー試聴ページ完成後は、最終試聴・記事採用の判断をユーザーに求めてください。

制作途中の技術的な問題については自律的に対処し、重要な判断事項以外で不要に作業を止めないでください。
```

## KPI provenance欄
全Gate・ASR・page_verify値は production_formal_path(fresh、本run)で取得する。E2E自己確認: Yes(fresh Production初回path)。再利用cacheを使った場合は件数内訳を記録。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
- 直近X新規記事の委任文・結果(正式経路コマンド・runner名・stage名・既知の落とし穴の正本として読む): `docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_01.md`(全文)、`docs/pm/delegation_log/2026-10-25_FAMILY-X-MOON-SHRINKING-PRODUCTION-01_DELEGATION_03.md`(全文)、対応するRESULT_PACKET(Grep `WORD-GACHA|MOON-SHRINKING` で `docs/pm/RESULT_PACKET_*.md` を特定し該当のみ)。
- `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPERATIONS_01.md`(X経路のKP HR・文法HR待機点、rc=4時のレビュー資料の所在、`grammar-select`/`reselect` CLI)§全体(短い)。
- `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/EVIDENCE_01.md` §2(受入表)・§11(R3)。
- `CURRENT_SPEC.md`: Grep `Family別Status|Family別到達Status` → 該当節のX行。Grep `B3|中核数値` → Family X B3節の見出し±40行。Grep `OPEN-517` → X行(L2855-2857付近)。
- `docs/pm/USER_DECISION_REGISTER_01.md:370-395`(直近X記事の受入・費用実績)。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 起動前: `git status --short | head -40`、他agentのX runnerプロセス(`Get-Process python*`)の有無、`py docs/pm/tools/daily_dev_cost_01.py`、`py tools/stop_scope_check_01.py --managed-id FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 --run-dir <X runnerの出力dir(DELEGATION_01で確定)> --out <同dir>/stop_check_委任_01.json`(rc=3なら起動しない)。
2. 既存仕様確認(API 0、短表): ユーザー原文§4の7項目について、X Production経路での反映状況(PRODUCTION_WIRED/未配線/該当なし)をSSOT行(ファイル:行)付きで表にし、`docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/SPEC_CHECK_01.md`(新規)へ。未承認仕様を使わないことを確認。
3. Research/Fact: 正式X経路のResearch工程に、ユーザー提示の3 URLを一次資料として与える(runnerの既存入力方法に従う。URL直指定の入力がなければ既存のtheme/source指定の仕組みで渡し、方法を記録)。24時間条件はユーザー原文どおり例外(原文path引用)。Fact管理で「13体・30時間・目標なし・塔/遊び/模様・神殿等は研究者の解釈と区別・課題成績向上とその限界・プレプリント」を確認し、断定禁止事項(祈った/宗教/感情・意識の獲得)が本文に無いことを英日両方でGrep検査して記録。
4. 制作: 直近X委任と同じ正式初回Production経路・同じrunner・同じ既定stage順で、Standard/Advancedを生成(`TTS_EXECUTION_MODE=STANDARD`、budget引数があればCap 150に合わせる)。slug案=`ai_island_temple`。KP HR/文法HRの待機点(rc=4)に達したら**そこで停止**し、レビュー用資料(KP候補一覧・文法候補一覧・レビューページ/依頼書のpath、Fableがユーザーへ提示できる公開URLがあればそれ)をRESULT_PACKETに記載して報告(宣言代行・top1自動採用はしない。ただし待機点より前に完了できる独立stageは全て完了させておく)。音声NGのHR Lockが出た場合はapprove_regenerateを1 segment 1回まで(Fable権限)、残れば採用せず報告。
5. runtime evidence: 使用runner・stage・model名(LLM/TTS/ASR Primary/Secondary)・Prompt sha・OPEN-517 r5(`open517_first_run_tally_01.py`・`open333_first_run_tally_01.py`を初回JA判定に対して実行、alert基準: DEMOTE>3/run、E3 reject>3/run、E4 fired>3/run またはE4発火行がHR到達=即報告)を `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/EVIDENCE_01.md`(新規)へ。費用は`BUDGET_LOG_01.md`(cost_log実測のみ、未記録は「未確認」、推定値を費用表に使わない。記事セット原価=PM_GOVERNANCE 15-8の『Production 1生成セット総原価』主指標)。
6. 完走できた場合: ページ(全文・通し再生・パート別再生)を `user_test/family_x_ai_island_temple_01/` へ配置、`py -I tools\user_test_page_standard_check_01.py --page user_test\family_x_ai_island_temple_01\index.html` rc=0、公開URL=`https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_temple_01/index.html`。
7. SSOT: `OPEN_ITEMS.md`に新規行(ID=次番号、種別=Production記事、Status=USER_LISTENING_PENDING または HR待機、11-8分類必須)。`DECISION_LOG.md`に委任_01エントリ(ユーザー原文pathを出典)。`CURRENT_SPEC.md`は変更不要(仕様変更なし。Family別Status節の記事一覧があれば1行追記のみ)。`docs/pm/ACTIVE_TASK.md`冒頭を固定ヘッダ(PM_BRIEF書式)で上書き+委任_01節。`docs/pm/REPORT_LEDGER.md`に1行。他agent差分(DECISION_LOG.mdのCRLF全行差分)はHEAD blob+自分hunkで回避。
8. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_01.md`(Nは615前後、`--index -1`不可、「FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01」を含むものを探す)。

## 実行コマンド全文
- `py docs/pm/tools/daily_dev_cost_01.py`
- `py tools/stop_scope_check_01.py --managed-id FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 --run-dir <出力dir> --out <出力dir>/stop_check_委任_01.json`
- X正式runner: 直近X委任(`2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_01.md`・`2026-10-25_FAMILY-X-MOON-SHRINKING-PRODUCTION-01_DELEGATION_03.md`)に記載の正式コマンドを、slug=`ai_island_temple`・本記事のtheme/source入力・`TTS_EXECUTION_MODE=STANDARD`・budget=150に置き換えて実行する(`.venv\Scripts\python.exe`)。**実際に実行した全コマンドを引数実値でRESULT_PACKETに記録**(Fableが本欄で確定コマンドを示せないため、ここは参照指定。check_delegation_promptでFAILになり得るが記録用)。
- `py -I tools\user_test_page_standard_check_01.py --page user_test\family_x_ai_island_temple_01\index.html`
- `py docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py --run-dir <出力dir>` / `py docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_first_run_tally_01.py --run-dir <出力dir>`(引数名はscriptの`--help`で確認)
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_01.md --json-out docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_DELEGATION_01.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- <commit対象path>`

## SSOT追記文
- DECISION_LOG(案): 「2026-10-26 FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01: ユーザー選定テーマ(原文=docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER.md、24時間条件はユーザー明示の例外)によるFamily X新規記事Std/Advを承認済み正式初回Production経路で制作。<到達点: HR待機(rc=4)/完走・限定公開>。実費<cost_log実測>円。未承認仕様の使用なし。ユーザー最終試聴PASSは未(USER_LISTENING_PENDING)。」
- OPEN_ITEMS新規行(案): 「| OPEN-<次番号> | FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 [種別=Production記事、Status=<HR待機|USER_LISTENING_PENDING>、分類=<11-8>] AIを仮想の島に放置…(Std/Adv)。<要点・URL・費用・残作業>。証跡=docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/{SPEC_CHECK_01,EVIDENCE_01,BUDGET_LOG_01}.md、報告=docs/pm/RESULT_PACKET_XAIT1.md |」

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/*.md`、`docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_{USER,DELEGATION_01}.md`(+_check.json)、`user_test/family_x_ai_island_temple_01/`(index.html・mp3のみ。wav/raw_usage_log/STOP/lock/RUN_LOCK不追跡)、X runner出力のうち既存X記事で追跡対象としているもの(直近X委任のadd対象に倣う)、`OPEN_ITEMS.md`、`DECISION_LOG.md`(HEAD blob+自分hunk)、`docs/pm/REPORT_LEDGER.md`(同)。ACTIVE_TASK/RESULT_PACKETは不追跡。
- メッセージ案: 「FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01: X新規記事『AIを仮想の島に放置…』Std/Advを正式経路で制作(<到達点>、実費<x>円)」
- `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。
- SSOT編集権: あり(本委任のみ。FZ委任_04は編集しない取り決め)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_XAIT1.md`(新規)。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+ RESULT_PACKET 4行(既存仕様整合・未承認機能の既定値・最終成果物・撤去/残置)+判定整合行。必ず含める: ユーザー原文§6の1〜9に対応する事実(6はFable記入欄として空欄、9は公開URL。HR待機で止まった場合は到達点とレビュー資料の所在・Fableがユーザーへ提示するKP/文法候補の一覧)、§2の確認事項5点+断定禁止Grep結果、実行コマンド全文、起動時刻一覧(Get-Date)、cost_log実測費用と記事セット原価(15-8)・70円目標比、日次累計、commit hash・push結果・raw.githubusercontent.com URL、check_delegation結果。