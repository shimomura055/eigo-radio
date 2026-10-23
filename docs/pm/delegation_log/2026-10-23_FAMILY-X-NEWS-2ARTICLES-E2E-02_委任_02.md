FABLE-DELEGATION-MARKER: FAMILY-X-NEWS-2ARTICLES-E2E-02-委任_02-ER053-FIX-RESUME-20261023

# 委任_02: er053 never-core不変条件の不具合修正(Fable承認・承認済み仕様内の是正)→記事A「イグ・ノーベル賞2026」再開→完成候補+試聴ページ、記事Bのページ検査誤検知対応、SSOT反映、7項目最終報告

前提: 委任_01の報告(`docs/pm/RESULT_PACKET_FXN2.md`、`docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-02/RESULT_01.md`)とユーザー原文(`docs/pm/delegation_log/2026-10-23_FAMILY-X-NEWS-2ARTICLES-E2E-02_USER.md`)を読んでから開始。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-X-NEWS-2ARTICLES-E2E-02_委任_02.md`(N≈342〜352、先頭MARKER一致確認)。
2. ACTIVE_TASK.md(並行agent: FAMILY-Z-SOURCE-FIDELITY 委任_06=『開いた窓』TTSあり、FAMILY-Y 委任_04=DEV)。編集直前に再読込、本管理ID行のみ更新。**TTS段の直前に他行の「有料run(TTS)進行中」を確認し、あれば5分間隔・最大30分待機**。自分のTTS開始/終了を行に記す。

## 1. Fable判定(修正の承認)
- er053_b3_deterministic_producer_01.py の `:544`(結合概念のcore役割継承)と `:798`(year/ordinal/name_embedded は never-core)の矛盾は、承認済み仕様内の不具合(11-8、区分B)と判定。**:798の不変条件を正とし、:544側を是正する修正(委任_01提案の1行: never-core kindのitemはroleをperipheralにする)を承認**する。Prompt/閾値/flag/他ファイルの変更は不可。
- 実施前確認(報告に記載): (a)er053系がFamily X専用でA/B/C・Zの経路から参照されていないこと(Grepで示す。A/B/C Legacy凍結§27-3)。(b)修正前後で、既存の全記事のB3入力(ledgerが残る過去runで `produce_annotated_b3` を再実行できるもの。例: 記事A/B旧2記事・coffee_prices・manga等、見つかる範囲で最大5件、API 0)の出力差分を比較し、「year/ordinal/name_embeddedがcoreだった箇所がperipheralになる」以外の差分が無いことを示す(差分0件なら「既存記事への影響0」)。(c)er053系・er019系の既存test(`er053*test*`/`er019*test*`)をPASS。
- (b)で「他の差分」や既存記事の本文に影響する可能性(coreが減ってB3のcore facts数が仕様下限を割る等)が見つかった場合は修正を適用せず報告して終了。

## 2. 記事A再開(正式経路)
- 修正commit後、`ig_nobel_2026/run_nws_02` を既存B3 brief(2回目)から再開(annotation producerはLLMなしなら再呼出不要。再開方法は runner の resume/regenerate-stage の正規オプションで、Ledger/Researchの再実行なし)。**有料run起動は1回のみ許可**(run内の既存retry/fallbackは仕様どおり)。rc≠0・HR Lock・STOPは迂回せず、原因・証跡・選択肢を報告して終了。
- 条件は委任_01と同一(`--mode real`、STANDARD、`--approved-budget-jpy 300`は案件合計。残見込み約70円、超過見込みなら開始前に停止報告)。
- 試聴ページ `user_test/ig_nobel_2026_e2e_02/`(記事Bと同形式)、HTTP 200+Playwright全audio実再生+ページ標準検査、評価json(記事Bと同じ `er019_nws2_eval_01.py`)。
- 内容確認(Fable受入資料): 受賞年(2026)と研究年(2016/1977)の区別が本文で混同されていないか、撤回済み研究が確立知見として書かれていないか、AMBIGUOUS IG2026-03 が本文に採用されていないか、KP 3件、PNAP(人名・大学名)の発火/供給、PASS_WITH_WARNING箇所。

## 3. 記事B 残件
- ページ標準検査 `no_internal_info_in_script` の「音楽」誤検知: `_INTERNAL_RE`(er_user_listening_page_common_01.py:125-127)は試聴ページ検査ツール(Production生成経路外)なので、**誤検知を減らす最小の絞り込み(例: ラベル行/効果音注記形式の「音楽」のみ検出)を承認**。条件: 既存公開ページ(user_test配下の全index.html)に対し修正前後で検査結果を比較し、新たに見逃すようになる真陽性が0件であることを示す。満たせなければ修正せず「既知の誤検知(本文中の正当な語)」としてRESULTに記録。
- Std comment_2 の PASS_WITH_WARNING(SECONDARY_CONFIRMED)1件: 該当clipのASR転写と台本を並記し、機械的に差異箇所を示す(耳確認はFable/ユーザー)。

## 4. SSOT・Git
- OPEN_ITEMS: 本案件の管理行(新規OPEN-xxx、記事A/B別Status: B=`USER_LISTENING_PENDING`、A=完了なら同じ、未完なら実Status)。er053不具合はOPEN-xxx(FIXED、修正commit、影響範囲評価)として別行。UDR: 2記事試聴PASS/NG判断を1件登録(URL 2件)。DECISION_LOG(er053修正判断=Fable、承認済み仕様内の是正)。REPORT_LEDGER。CURRENT_SPEC: er053の不変条件記述があれば整合確認(無ければ追加しない)。
- 共有SSOTは編集直前`git status`→自分の行のみ→即commit。明示add、mp3のみ、secret_scan `--staged` hits=0、`git push origin HEAD:main`。
- 全回帰 `run_project_regression.py` 最後に単独実行(他agentのTTS/commit中は避ける)。failedがあれば自分起因かを分類(Family Y DEVファイルのimportによる隔離test 2件は既知)。

## 5. 禁止
- Prompt/閾値/flag変更、Pro系TTS、追加Trial、A/B/C・Zファイル変更、本文手修正、有料run再起動(1回超)、HR/STOP迂回、記事Bの再生成。

## 6. 報告(docs/pm/RESULT_PACKET_FXN2.md に追記、同内容を最終報告)
ユーザー指定7項目(委任_01原文の報告項目に従う)を2記事分まとめる: (1)完成状況・URL(記事A/B)・JAタイトル(ユーザーのテーマ文言との関係) (2)音声・QA(segment/HR/retry/fallback/KP3V/PNAP/er109/PASS_WITH_WARNING/同値承認) (3)事実性(Ledger、B3採用、規則/事実の区別、年の区別、撤回研究) (4)費用(記事別text/audio内訳、出典、70円目標との差と支配要因) (5)所要時間 (6)不具合と修正(er053: 原因・修正・影響範囲評価・test、ページ検査誤検知の処置) (7)残リスク・残件・SSOT・commit・raw URL。+RESULT_PACKET 4行+「判定整合: 重大NG=あり/なし」。