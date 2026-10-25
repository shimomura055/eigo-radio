管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02C(text coreの残り=`produce_article`[Voice生成+Voice Gate+Lead+人物紹介]の実装・test、Fable判断の転記。**有料API 0・Production run 0**)。02B(runner/audio/routing、別agent)が並行中=§4ファイル所有厳守。

## 0. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ・直前再Read)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_02,SPEC_LEDGER_02,BUDGET_PLAN_02,OPEN_TRACKING_02,GATE_CALIBRATION_01,REWRITE_EVIDENCE_01,OPUS_REVIEW_01}.md`、`er121_family_y_text_core_01.py`(+test 56)、ユーザー原文 `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`(§2-1, §7)、Y承認済みVoice生成設計の正本(`docs/research/FAMILY-Y-VOICES-DESIGN-01/`配下のDESIGN・USER原文、`er110_family_y_persona_pipeline_01.py`の`_pl`系: Theme Package→人物像→Voice生成→Voice Gate(`run_gate_pl`)→書換え`build_voice_rewrite_prompt_pl`、`er110_family_y_redelivery_revision_01.py`の Lead再生成・人物紹介生成+検査[主張先取り語の禁止・本人語りとの10字連続一致なし]、In One Line廃止、注意書き)、Round 1/2で使ったSNS `run_03` Theme Package/voices_final、宅配のR0(`load_r0`)。

## 1. Fable判断(転記: `DESIGN_02.md`に「Fable判断(委任_02C)」節、`OPEN_TRACKING_02.md`該当OT、OPEN-520)
- OT-27(案B固定ClosingがM-1後判定で2/7 FAIL): **案Iを採用**=進める。E-1実走時に案Bは1回判定し、FAILならSTOPして「ユーザー承認済み本文とGateの衝突」としてユーザー判断(既存のHuman個別承認記録機構[`record_human_approval`型]でGate FAILをユーザー承認で上書きする案を推奨案として提示予定)。書換え禁止・判定再試行禁止(I-4)は維持。
- OT-28(Lead/人物紹介への補助適用): Lead/人物紹介はナレーター文であり、Voice用の`leak_evidence_memorable`(人物の経験・感情の具体性)は性質上適合しないため**非適用**。適用するのは出所・創作・一人称・Tension専用2項目を除く「ナレーター文に意味を持つ項目」のみ。これは承認済みGate定義の変更ではなく、Y固有の新パート(Lead/紹介)への適用範囲の確定(Fable権限)。委任_28で用いた決定論検査(主張先取り語禁止・10字連続一致なし・字数)は必須のまま。
- 個別Cap: 150→**170円**へ引上げ(300円以下の自律範囲、7-7)。`BUDGET_PLAN_03.md`に反映(既支出14.347円)。
- E-3 voices段: Opus M-6どおり**SNS Theme Packageから実生成**(R0再利用ではProduction runtime evidenceにならない)。
- 範囲保全guard(`rewrite_scope_check`): 維持。緩和は運用実績後。
- G-2(`leak_discovery_syntax`がPrompt 02の「見えてくる」を3/3 FAIL): Gate文言の補足はユーザー判断事項として提示(台帳YL-E02)。本委任では変更しない。

## 2. 実装Scope(`er121_family_y_text_core_01.py`に追加。02Bのrunnerから`produce_article(client, theme_package, out_dir, guard=...)`で呼べるI/F。`FAMILY_Y_TEXT_CORE_NOT_CONNECTED`を解消)
- Theme Package読込・sha(案B registryのTheme Package shaと同じ算出法)。
- 人物像→Voice 1〜3生成(`FAMILY_Y_VOICE_GENERATE`)、Voice Gate(`run_gate(kind="voices")`、判定≤3・局所書換え`FAMILY_Y_VOICE_REWRITE`・`_pl`系の題材非依存prompt・範囲保全guard・残存FAILは`VOICE_RESIDUAL_STOP`・gate_history全保存)、Voice決定論検査(既存Y設計の字数・一人称・記号等をDEVから逐語移植、DEV不変・差分testで固定)。
- Lead生成(`FAMILY_Y_LEAD_GENERATE`、AI編集説明なし・委任_28の規則)、人物紹介3本(`FAMILY_Y_PERSONA_INTRO`、1文・主張先取り語禁止・本人語りとの10字連続一致なし・字数)、Lead/紹介へのGate補助適用(OT-28の範囲)。
- 記事組立(5パート: Lead/[紹介+Voice]×3/Closing、In One Lineなし)、`article_record`(各段のmodel_id・routing key・prompt sha・gate履歴・sha)。宅配の既存R0(Voice本文・改訂Lead・人物紹介)を**再利用入力として受け取る経路**(E-1用: Voice生成をskipし、byte一致検証のうえ採用。再利用も`article_record`に明記)。
- routing照合は既存`chat`(require_model+startswith)を使う。`guard`を各API呼出前に呼ぶ。
- test(socket遮断・mock・API 0): 生成call数、Gate経路、STOP各種、DEV差分=移植のみ、R0再利用のbyte一致、記事組立の5パート・In One Line不在・注意書き文言、Lead/紹介検査、OT-28適用範囲、Prompt/定義文のsha固定。既存56件回帰。
- `BUDGET_PLAN_03.md`(Cap 170、E-1〜E-5の最新見積、E-3 voices実生成込み)。

## 3. SSOT・Git・逐語保存
OPEN-520最小追記(Cap 170・OT-27/28判断)。OPEN_ITEMS直前再Read・最小Edit・バックアップ。CURRENT_SPEC変更なし。Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告。他agentの未commit差分を巻き込まない)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02C.md`(Nは588前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02C」を582〜615で走査)。

## 4. ファイル所有
- 02C(本委任)が編集: `er121_family_y_text_core_01.py`(+test)、`er121_prompts/`配下の新規prompt file、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_02(追記節のみ),BUDGET_PLAN_03,OPEN_TRACKING_02}.md`、OPEN-520、delegation_log 02C。
- 02Bが編集中(読むだけ): `er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`、`er006`、scope/segment/注意書き関連、`OPERATIONS_01.md`、構造一致test。runner側に必要なI/F変更があれば報告に「02Bへの要求」として書く(自分で編集しない)。
- 禁止: DEV(`er110_*`)変更、Prompt 02・Gate基準文言・案B本文の変更、有料API、公開ページ・`er0XX_output/`変更。

## 5. 報告(RESULT_PACKET_YPL2C.md+口頭要約)
実装関数・I/F、test件数(新規/回帰、遮断下接続0)、DEVからの移植一覧とsha、OT-27/28転記、Cap 170反映、02Bへの要求、E-1〜E-3の実行に必要な残作業、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。