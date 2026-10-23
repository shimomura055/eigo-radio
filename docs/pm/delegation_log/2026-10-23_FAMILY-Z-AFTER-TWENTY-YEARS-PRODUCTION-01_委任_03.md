FABLE-DELEGATION-MARKER: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01-委任_03-TIME-NUMERAL-NORMALIZATION-DEFECT-GATE-FIX-AND-FINALIZE-20261023

# FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_03: Std c8 HR Lockの真因=ASR保護検査が原稿の隣接数詞語「ten thirty」を合算して`40`に正規化する(X/Z共通の既存検査の不具合、OPEN-482)。**影響分析gate→(通過時のみ)最小修正→回帰→c8再生成(approve_regenerate、原稿不変)→完成段1起動→試聴ページ→SSOT→報告**。Production codeの変更は影響分析gate通過時の当該正規化1箇所のみ。費用上限20円(作品累計約45円→≤65円)。

## 0. 先に読むもの
`docs/pm/ACTIVE_TASK.md`(line 2、FAMILY-Z-AFTER-TWENTY-YEARS行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_FZ20Y1.md`、`docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/{RUNTIME_EVIDENCE_01,CP_CHECK_01,BUDGET_PLAN_01}.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_{USER,委任_01,委任_02}.md`(制約継承)、OPEN-479の前例 `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/OPEN_479_IMPACT_01.md`(影響分析gateの方式)、`run_sf_prod_01/a2/audit/review_lock_state.json`、数詞保護検査の実装(`er078_reuse_value_guard_01.py` の PROTECTED_DIFF/number正規化、`er006_secondary_asr_01.py`/`er109_*` の number_mismatches 生成箇所をGrep: `number_mismatches`, `_normalize_number`, `words_to_number`, `ten thirty`)。

## 1. Fable判断
- 案A(原稿を`half past ten`へ決定論パッチ)は、原稿変更による個別回避であり採らない(ユーザーは『開いた窓』で原稿改変による個別対応を否定)。案B(人間試聴承認)は最終手段。**X/Z共通検査の不具合を根本修正する(案C相当)**のが原則4・8に沿う。ただしProduction検査の変更のため、OPEN-479と同じ**影響分析gate**を課す。
- gate: (i)既存の保存済みX/Z判定(『開いた窓』run_sf_prod_01、melos、X記事群、pool backtest等)に対し、修正前後の決定論再計算でPASS→NG 0件、NG→PASSは「時刻/隣接数詞語の正規化誤り」に起因するものに限る、(ii)数値・否定の安全条件(数値差の検出力)が弱まらない(合成負例: `ten thirty`→`10:13`、`ten`→`10:30`、`two thirty`→`2:03`、`forty`→`10:30`は全てNGのまま)、(iii)修正が1箇所の正規化関数(または時刻パターン分岐)に閉じる。不通過なら修正せずSTOPしFableへ(案A/Bを提示)。
- gate通過なら修正はFable承認済みの仕様内不具合修正。c8は原稿不変のまま `approve_regenerate`(根拠=本委任・ユーザー原文§5「必要なretry/fallbackは既存仕様に従って自律実行」)で再生成してよい(最大2テイク)。

## 2. 作業
### T-0 記録・予算
委任文逐語保存 `..._委任_03.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致。`.venv/Scripts/python.exe`でも可)。ACTIVE_TASK自行: 委任_03 Status=`OPEN_482_IMPACT_ANALYSIS`、上限20円、報告=`docs/pm/RESULT_PACKET_FZ20Y3.md`。当日累計確認(JST日付と上限に注意)。
### T-1 影響分析(API 0)→`docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/OPEN_482_IMPACT_01.md`
正規化の現行仕様(どの関数が隣接数詞語を合算するか、時刻・年号・小数・分数・序数の扱い)、意図された設計(DECISION_LOG/CURRENT_SPECを管理ID・「数値」「number」でGrep)、修正案(例: 時刻パターン `hour(one..twelve) + minute(oh/o'clock/thirty/forty-five等)` を`HH:MM`へ正規化、ASR側`10:30`も同形へ。合算は「twenty one」型の合成数のみ)、replay結果(件数・変化一覧)、合成負例の結果、gate判定。
### T-2 修正(gate通過時のみ)
最小差分+test(時刻表現の正規化、合成負例NG維持、既存golden不変、X/Z共通)。関連suite+`run_project_regression.py`(`er0*`,`er1*`)。golden hash変化は内容列挙(時刻正規化以外の変化は不可)。
### T-3 c8再生成→完成
TTS直列化(他行flag待機、最大45分。自行flag)。保全→`approve_regenerate`(c8のみ、最大2テイク)→正式CLI `--only-clips full_story_part2_c8`(tts_a2)→受理確認→`provision_shell,gate,assemble,pages,page_verify` **1起動**(再起動禁止)→試聴ページ `user_test/family_z_after_twenty_years_01/`(『開いた窓』と同テンプレート: Std/Adv切替、通し、パート別、全スクリプト、KP、開発者情報なし)→page_verify(実再生・整合・console error 0)→`PAGE_VERIFY_01.md`。cool-downは正規の待機であり自PIDを終了しない(委任_02の事象3の再発防止)。
### T-4 SSOT・Git・報告
OPEN-482(原因・gate・修正・結果、CLOSED候補)、新規OPEN(本作品: 完成版提出・ユーザー試聴待ち)、OPEN-472(RET: 本作品でのNER 1call・weak判定の事実)、DECISION_LOG(Fable承認の仕様内不具合修正、approve_regenerate)、REPORT_LEDGER、UDR新規(ユーザー最終試聴待ち)。CURRENT_SPECは数値検査の記述があれば時刻の扱いを1行追記。Seed駆動化はOPEN候補として記録のみ。secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`(wav/raw_usage_log/STOP関連追跡禁止)→`git push origin HEAD:main`。raw URL添付。
報告=`docs/pm/RESULT_PACKET_FZ20Y3.md`(ユーザー§8の8項目+gate判定+登録負担の実態[45分・data追加のみ・test1行変更]+原作忠実性の軽微所見[到着時刻30分 vs 原作約20分、因果影響なし]を明記)。使用model名。

## 3. 禁止
gate不通過時のProduction変更、原稿の改変(案A)、Ledger手動登録、Gate/HR Lock/STOP迂回、再起動(完成段は1起動)、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index、他PIDの終了、上限20円無断超過。
## 4. handback
完了/gate不通過/新HR Lock/予算警告/blocker のいずれかで。