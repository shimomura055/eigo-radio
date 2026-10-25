管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_06(A: Part 1/Part 2/文法HRのY runner接続[API 0]、B: E-1(宅配)のHR Lock解消→完走→限定公開[有料小額]、C: 原価要因の分析[API 0])。Cap 170円(既支出129.14円、残40.86円)、日次1,500円(本日累計約1,247円+他案件進行分。各起動前に`py docs/pm/tools/daily_dev_cost_01.py`+94.28円で確認)。

## 前提・競合回避
- 委任_05(別agent)が`er121_family_y_text_core_01.py`(案B個別Human承認・`leak_discovery_syntax`補足)・`er020`・`er117 test`・CURRENT_SPEC(Y Gate節)を編集中。**text coreは読むだけ**。E-1再走の前に`git log origin/main --oneline -30`で「FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05」のcommitが着いていればpullして使い、着いていなければE-1はtext stage再利用(text変更の影響なし)で進めてよいが、**text coreのimportが壊れていないこと(`py -c "import er121_family_y_text_core_01"`)を起動直前に確認**。
- KP HR evidence(X/Z)・JA ASR 07A(er078/er007のProduction適用)が並行中。07Aのcommit(「JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A」)が着いていれば、E-1のASR再判定はその版で動く(evidenceに版を記録)。
- 本委任所有: `er121_family_y_runner_01.py`(+runner test)、`er121_family_y_audio_01.py`(必要最小)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{EVIDENCE_02,BUDGET_LOG_02,COST_ANALYSIS_01,OPEN_TRACKING_05}.md`、OPEN-520/484(最小追記)、`user_test/family_y_production_redelivery_fee_01/`(限定公開)、delegation_log。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{EVIDENCE_01,BUDGET_LOG_01,DESIGN_02,OPERATIONS_01,SPEC_LEDGER_03,OPEN_TRACKING_04(あれば)}.md`、`er121_family_y_runner_01.py`(`study_text_slots.json`の未接続スロット、stage列)、X/Zの接続実装 `er120_part2_wiring_01.py`・`er119_grammar_review_01.py`・`er019`の`--stage study_text`/scaffold先頭の候補抽出・`er026`の`part2_cand_b1b`/`part2_b1b`・`er003_kp_general_explanation_01.py`(Part 1 5件化=`vocab_confirmed.json`/`part1_items`)・`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_02,OPERATIONS_01,EVIDENCE_PLAN_01}.md`・`docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md`、ER-011 HR Lock仕様(`er011_human_review_lock_01.py`、`approve_regenerate`の権限・手順。Fable権限で`approve_regenerate`[追加再生成の許可]は可、個別音声のNG承認[`approved_by="user"`の最終採用]は不可)、E-1 run `er121_output/family_y_production_01/redelivery_fee/run_01/a2/audit/review_lock_state.json`と各attemptのASR/QA記録。

## A. Part 1/Part 2/文法HRのY接続(API 0)
- X/Zと**同形**でY runnerへ: 候補抽出(Step A'')はKP候補生成と同じ待機点の前(Y `stage_text`後・`kp`前)、KPと文法のpendingを1つの`review_request.md`/rc=4に統合(er119共通核のkind="grammar")、確定後にStep B(`part2_b1b`相当、input_sha=本文sha|label|文法確定署名)、Part 1は`part1_items`/`vocab_confirmed.json`(5件、Advのみ)、`require_fresh_part2`をtts/assemble/pages/page_verify入口で、`verify_selection_matches_outputs(kind="grammar")`をpage_verifyで、公開ページはPart 1直後・Advancedのみ・0件固定文面(共通builder `compose_study_html`/`public_study_html`相当)。`study_text_slots.json`の「未接続」を解消。routing(`STUDY_TEXT_GRAMMAR_*`)はer006登録済み。構造一致testの許可リストを更新(Part 1/Part 2の共通呼出しがX/Zと一致)。
- test(`.venv`・遮断harness): 待機1回、確定前Step B 0 call、再開API 0、Advのみ表示、0件文面、fail-closed入口、HRあり/なし(mock)。回帰: runner/structure/audio/text core(読むだけ)全PASS。
- 注: E-1/E-3の既存runはPart 1/2未接続で生成済み。E-1再走ではtext/kp再利用のうえ、Part 2候補抽出〜確定(HRなし宣言は既存の宣言を再利用せず、**新しい候補shaに紐づく新宣言**が必要=仕様どおり)→Step B→study_text→page。費用: Step A''+Step B 約0.5円+Part 1(5件)約0.2円。

## B. E-1(宅配)完走
1. Lock原因の確認(記録ベース): a2 `preview`(JA: ASR「思い通りに」vs正本「思いどおりに」=表記差・読み正)、a2 `y_voice_1`(EN: attempt1 Repetition QA短ラグ0.68s/閾値0.6s、attempt2 "re-deliveries"↔"redeliveries"ハイフン差でASR_VALIDATION_UNCERTAIN)。既存仕様(同音・異表記救済、ハイフン正規化、Repetition QA閾値)で本来PASSすべきものかを照合し、**実装不具合(仕様上は救済対象なのに動いていない)なら原因を特定**(修正はProduction共通moduleに及ぶ場合は別OPEN登録し本委任では変更しない。Y固有部分なら修正)。
2. **Fable権限で`approve_regenerate`(追加再生成の許可。NG音声の最終採用承認ではない)**を2 segmentに適用し、`--regenerate-stage tts_a2`で再生成(既定の追加attempt数、各attemptは既存ASR/QAで判定)。PASSすれば→gate→assemble→pages→page_verify→限定公開(`user_test/family_y_production_redelivery_fee_01/`、Pages反映確認)。それでもNGが残る場合は**再度のapprove_regenerateは行わず**、当該wavのローカルパス・ASR/QA記録を添えてユーザー試聴判断へ(STOP)。費用見込み: TTS数call+ASR 約3〜8円。
3. E-1の受入証跡(EVIDENCE_02.md): 案B固定(1回判定PASS・sha一致・書換えなし)、HRなし(宣言→`UNREVIEWED_AUTO_ADOPTED`・ng=[]・verdicts null)、Part 1/Part 2(接続後)、Chunk決定記録(分割0=1段落契約)、注意書き、segment網羅、model_id/routing/Prompt sha(案B経路はPrompt 02不使用を明記)、Lock経緯と解消手順、実費、受入条件13項目(USER_02 §6)対応表(未達は未達)。
4. `final_manifest.stage_entries`のtext/kp/supportのmodel欄null(`article_record`には記録あり)を修正(runner側の転記漏れ)。

## C. 原価要因分析(API 0、`COST_ANALYSIS_01.md`)
- E-3実測82.72円の内訳をstage別・call別に分解。特に(1)Voice UNMAPPED再生成3/3発火(14.92円): `map_voice`(luna)が全VoiceでUNMAPPEDになった原因(prompt/入力形式/判定閾値/Theme Package側の出典ID形式)を記録ベースで特定=**不具合なら修正候補(品質非影響)**として提示、(2)Closing 1 call 21.99円(reasoning token数、cached_tokens命中率)、(3)その他。品質を下げない低減策(重複call排除・cache・不具合修正)と、品質判断を伴う策(effort等=ユーザー判断)を分けて列挙。70円目標との差(+12.7円)の内訳。

## SSOT・Git・逐語保存
OPEN-520(接続完了・E-1結果)/OPEN-484(Y Part 1/2接続のStatus)最小追記、直前再Read・最小Edit・バックアップ。CURRENT_SPEC変更なし(PRODUCTION_WIRED判定はFable)。Git: 対象pathのみ(wav/raw_usage_log/lock不追跡、公開mp3は`user_test/`配下のみ)→`git commit --only`または一時index→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_06.md`(Nは605前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_06」を598〜655で走査)。

## 禁止
NG音声の最終採用承認(`approved_by="user"`)の代行、Gate/閾値/Repetition QA/ハイフン正規化等の共通Production規則の変更(不具合は別OPEN)、Prompt 02・案B本文の変更、Cap/日次超過、同一run dirへの起動間隔150秒未満・5分3回、E-3の再生成。

## 報告(RESULT_PACKET_YPL6.md+口頭要約)
A接続の変更点・test、E-1の結果(Lock原因の仕様照合結果、approve_regenerate後の各attempt結果、完走/STOP、公開URL)、受入13項目対応表、原価分析(内訳・不具合候補・低減策の分類)、実費(本委任・累計/170・日次)、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。