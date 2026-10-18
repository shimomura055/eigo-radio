# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_03(Fable CP2判定=USER_DECISION_REQUIRED の記録のみ。JPY0、有料実行0)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: SSOT記録のみ。コード・Prompt・成果物の変更0。音声工程は起動しない。
- 到達上限Status: `USER_DECISION_REQUIRED(#112: 中東記事の扱い)`。
- 禁止: 有料実行/再生成/Prompt変更/音声plan以外の音声工程/`er082_*`・`er026_output`・`user_test/family_z_*`・`er063_*`への接触。
- 固定ブロック: E-1(OPEN-416・E2E_PLAN §14に整合)/D-1(不適用)/G-1(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentあり: SSOTは自分の変更行のみstaged blobでcommit(委任_02と同じ方法)、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行)/F-1(JPY0)/T-0(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_03.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/T-2・T-3(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY3.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。

## Fable CP2判定(2026-10-18、記録する内容)
- 再生成後の記事(タイトル "Airport Attacks: Another Crisis the Damage Figures Alone Cannot Show"): Ledger外の創作描写0件、Risk Flagger候補0件、帰属・数字の時点分離は良好、因果誇張なし=**事実性・中立性はPASS**。
- しかしB3は2回連続でF11(国連特使発言)のみを選定(F01〜F10はexcluded)。記事は「ニュースの読み方」型のメタ・エッセイで、ユーザーの狙い「なぜイエメン周辺の紛争がサウジ・地域全体に影響するのか」を一連の事実(10/6〜16の空港・アラムコ・マリブ・アデン)で語れていない=**狙い適合はNG**。
- 同じ問題が2回再現(原則5)。改善にはB3選定基準(Prompt)の変更=Production挙動変更が必要で、Fable権限外。Ledger自体も攻撃主体が公的発表で未特定・独立報道0件・1Fact1URLという限界があり、Research再実行でも狙い達成の保証はない。
- よってユーザー§6「既存Production経路では解決できない品質問題」に該当と判定し、**音声工程へ進めずSTOP、USER_DECISION_REQUIRED**。
- 選択肢(ユーザー提示): (a)この記事のまま音声工程へ(見込み約JPY25〜30、E2E累計約105〜110/180) (b)本記事を見送り(text実費JPY79.9で終了、成果物は保全) (c)Research再実行1回(見込み約JPY36+下流約25=約61、E2E累計約141、さらに音声で180に接近。狙い達成の保証なし) (d)B3選定基準の改善を別Trialとして起票(Prompt変更=Production Gate対象、本記事とは切り離す)。Fable推奨=(b)+(d)。(a)はユーザーが本文を読んで許容できる場合のみ。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY2.md`
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01\E2E_PLAN_01.md` §14

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `OPEN-416`→Status `USER_DECISION_REQUIRED(#112)`、CP2判定要旨・選択肢(a)〜(d)・推奨を追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#111`→直後に `#112(UDR-blocking 2026-10-18) 中東記事の扱い(a)〜(d)、推奨(b)+(d)` を追加。
- `DECISION_LOG.md`: 末尾に委任_03エントリ(CP2判定・STOP理由・選択肢)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `E2E_PLAN_01.md`: 「## §15 Fable CP2判定(USER_DECISION_REQUIRED)」追記。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01_委任_03.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在script名に置換)

## SSOT追記文(要点)
- OPEN-416: 「2026-10-18 Fable CP2: 事実性PASS/狙い適合NG(B3単一Fact選定が2回再現)。音声工程STOP。USER_DECISION_REQUIRED #112(a〜d、推奨b+d)」。
- DECISION_LOG: 同旨。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_03+_check.json、OPEN_ITEMS.md(自分の行のみ)、USER_DECISION_REGISTER_01.md、DECISION_LOG.md、REPORT_LEDGER.md、E2E_PLAN_01.md。msg: `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_03: Fable CP2判定(事実性PASS/狙い適合NG、B3単一Fact選定2回再現)→音声工程STOP・USER_DECISION_REQUIRED #112(選択肢a〜d)をSSOT記録(JPY0)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_MEY3.md`)
4行: (1)整合(編集行番号)(2)Production到達経路=変更なし(3)commit sha(4)撤去/残置なし。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/#112登録/音声未起動)。
