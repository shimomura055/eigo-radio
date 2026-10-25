管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_04(ユーザー追加決定3件の反映。**API 0・有料run 0**)。委任_03(別agent)が`er121_family_y_runner_01.py`・`er006`・`.gitattributes`・OPEN-520を編集中=それらは**編集禁止**(読むだけ)。本委任の所有: `er121_family_y_audio_01.py`(+test)、`er121_family_y_text_core_01.py`(+test)、`er121_family_y_structure_01.py`、`docs/pm/PM_GOVERNANCE.md`(Closeout Mandatory Checkの1項目追加のみ)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{SPEC_LEDGER_03,spec_ledger_03.json,BUDGET_PLAN_04,OPEN_TRACKING_03,DESIGN_02(追記節)}.md`、delegation_log、DECISION_LOG(1件)。

## 0. ユーザー追加決定(2026-10-25。原文を最初に逐語保存: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl`の末尾付近user行で「Family Y Production正式立ち上げ｜追加仕様決定・実装継続」を含む行を`<pasted_content>`ごと`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md`へ無改変保存。文字化けしていれば`_RAW_JSONL`として退避し、以下の要旨版を`USER_02.md`に「Fable context由来の逐語」として保存)
要旨(逐語に近い形):
- ①**Family Y Chunk分割: Family X方式(段落分割+0.2秒ポーズ)をYに正式採用(APPROVED_FOR_PRODUCTION)**。正式Production経路に組込み、既存X方式を最大限再利用、Yの5パート・3 Voice・話者切替との整合、セリフや話者の切替を不自然に結合・分割しない、事前Trial・試聴承認は不要、正式実走時に音声品質・分割位置・ポーズを検証。ZのB_r1方式は採用しない。
- ②**Closing Prompt/Gate: 現行Prompt 02・既存Gateを変更せずに進める**。Prompt 02+gpt-6.1-sol high維持、承認済みGate基準維持、**既存の局所修正・再判定機構を利用**、Gate FAILが解消しない場合は公開しない、不整合は既存OPENで継続管理、Prompt 03化・Gate緩和は行わない。
- ③**Voice生成方式: 既存Y設計に基づく3 Voice生成方式を正式Production採用(APPROVED_FOR_PRODUCTION)**(実在意見を素材、明確な人物像、一人称・主観、立場・価値観・経験の違い、5パート維持、意見収集の自動化はScope外)。公開前の出典・利用許諾の既存課題は継続管理し公開条件を省略しない。
- Closing採用判断維持: 今後のY記事=Prompt 02/sol/high、『宅配』のみ案B(他記事へ拡張しない)。
- 配線漏れ防止【最重要】: 55項目台帳を正本として更新し3項目を反映。承認済み仕様はY立上げで組込み(KP・文法HR、英語解説、Part 1/2、ASR・TTS共通品質対策)、他案件で実装・検証中のものは接続仕様確定時点でYへ接続。未承認は先行採用しないが仕様ごとに Status/適用対象/Y要否/配線状況/残作業/完了条件/OPEN追跡先を追跡。**既存PM Closeout Mandatory Checkに、共通仕様のX/Y/Z配線状況を確認する項目を必要十分な形で追加する(承認済みのFamily間仕様乖離防止方針の実装として扱う)**。
- 費用: Phase 0概算を維持(宅配27〜35/通常69〜93/総額73〜113/案件枠提案150)。Chunk採用で見積・検証範囲が変わる場合は再計算。**150円は提案枠であり新規承認予算ではない**。既存承認予算・日次上限内で継続、有料実走前に充足確認、不足時は追加額と用途を提示。70円目標は継続、品質を下げて合わせない。
- 受入条件13項目(5パート・3 Voice/承認済みVoice生成/通常記事でPrompt 02+sol high発火/宅配のみ案B/**X方式Chunk+0.2秒ポーズがYで機能**/KP・文法HRあり・なし/共通仕様適用/retry・fallback・regeneration・resume/Gate・Regression・integration/runtime evidenceにmodel_id・routing・Prompt/Style/CURRENT_SPEC・DECISION_LOG・OPEN・台帳更新/Git/Fable独立受入)。
- STOP条件は従来どおり+「公開条件・権利関係の未解決によって公開できない」。
- 報告: まずOpusレビュー結果と追加決定を反映した実装計画・費用見積・未解決事項を簡潔に報告→実装・検証→最終報告。

## 1. Fable判断(転記)
- ①Chunk: 承認に伴い、台帳YL-B08を「除外+OPEN記録」→「適用(X方式)」へ。実装はX方式の共通module(`er117_chunk_tts_production_01.py`のX B0.2=段落chunk+0.2秒ポーズ)を**直接import**し、Yのsegment(lead/intro/voice/closing)ごとに段落単位で適用。話者切替境界(intro→voice、voice→次intro)はsegment境界なので結合しない。1 Voice(約300字/約200語)内の段落分割はX規則どおり。Chunk Gate(Style profile Gate on chunks、親集約`CHUNKS_NOT_ALL_VALIDATED`)もX同様。`chunk_tts_decision.json`は「適用(X方式)」を記録。
- ②案B(OT-27改訂): 「既存の局所修正・再判定機構を利用」の指示に従い、案Bは**既存の再判定機構(判定≤3回)は使う**が、ユーザー承認本文を変える局所書換えは行わない(承認本文の保護)。3回判定後もFAILなら公開せずSTOP→ユーザー判断。`FIXED_CLOSING_*`の経路をこの仕様に更新(判定回数・各判定結果をclosing_recordに記録)。一般Closing(Prompt 02)は既存どおり判定≤3+局所書換え+残存FAILは公開しない。G-2(Gate文言補足)は実施しない(OPEN継続管理)。
- ③Voice生成: 台帳YL-C03を「適用(APPROVED_FOR_PRODUCTION、USER_02 ①③)」へ。公開前条件(V1根拠の再利用許諾等)はOPEN追跡を維持。
- Closeout Mandatory Check: ユーザー指示により**PM_GOVERNANCEへ1項目追加**(正本参照先はCURRENT_SPEC「共通仕様のFamily別配線Status表」。文言案: 「全Family共通仕様の採用・配線・Closeout時に、X/Y/Zの配線Statusを配線Status表で確認し、未配線Familyがあれば理由・残作業・解消条件をOPEN_ITEMSに記録したか」。必要十分・過剰にしない)。前回の「取り下げ」をこの指示で上書き。
- 予算: 案件Cap 170円はFableの自律枠(承認済みScope・300円以下、7-7)として維持(ユーザーの新規承認ではないことを明記)。Chunk採用の費用影響≈0(chunk数増によるTTS call増はX実績で単価影響なし)を再計算して記載。

## 2. 作業
A. 原文保存(§0)。`SPEC_LEDGER_03.md`+json(①②③反映、YL-B08/C03/E02更新、承認根拠=USER_02の節引用)。`OPEN_TRACKING_03.md`(OT-27改訂、Chunk適用、公開前条件)。`BUDGET_PLAN_04.md`(Chunk影響再計算、Cap 170=Fable自律枠の明記、日次状況)。`DESIGN_02.md`へ「追加決定反映(委任_04)」節。
B. `er121_family_y_audio_01.py`: Chunk X方式の適用(er117の共通関数import、Y segment計画への組込み、chunk決定記録、Chunk Gate連携)。runner側で呼出変更が必要なら、変更内容を「委任_03/次委任への要求」として報告に書く(runnerは編集しない)。test: 段落分割がsegment境界をまたがない、0.2秒ポーズ、話者切替で結合なし、Chunk Gate親集約、X回帰(er117 x)PASS。
C. `er121_family_y_text_core_01.py`: 案B経路を「判定≤3・書換えなし・残存FAILはSTOP(`FIXED_CLOSING_RESIDUAL_FAIL`)」へ更新、closing_recordに各判定結果。test更新(128件回帰+新規)。
D. `docs/pm/PM_GOVERNANCE.md`: Closeout Mandatory Checkに1項目追加(節番号を確認し最小Edit。改訂履歴にユーザー決定2026-10-25 USER_02を記す)。DECISION_LOGに1件(①②③+Closeout項目追加)。
E. test実行は`.venv`のPython・ネットワーク遮断harness(実client生成block)。
F. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告。他agentの未commit差分を巻き込まない)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
G. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <上記jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_04.md`(Nは595前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_04」を590〜630で走査)。

## 禁止
有料API・Production run。runner/er006/.gitattributes/OPEN-520の編集(委任_03所有。OPEN_ITEMSへは本委任分の追記が必要なら直前再Read・最小Edit・バックアップで別行)。Prompt 02・Gate基準・案B本文の変更。ZのB_r1方式の適用。`er117`等の共通moduleの変更(importのみ)。

## 報告(RESULT_PACKET_YPL4.md+口頭要約)
反映内容(台帳差分・Chunk実装・案B判定仕様・PM_GOVERNANCE追加文言)、test件数、runnerへの要求(あれば)、費用再計算、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。