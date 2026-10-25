# EVIDENCE_01: Family Y 正式E2E evidence(E-3 SNS年齢制限 / E-1 宅配・案B)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_03 / 2026-10-25(JST)。**PRODUCTION_WIRED判定はFable。本書は事実の記録であり判定ではない。ユーザーの最終試聴PASSは別Status(未実施)。**

## 0. 結論
- **E-3(SNS年齢制限、一般化Closing Prompt 02+Sol high、Voice実生成、HRあり経路)= 完走**(rc=0。text→translate→support→kp[rc=4待機→HR操作→再開]→tts_b1b→tts_a2→gate→assemble→pages→page_verify 全PASS)。実費82.72円、機械時間約27分。限定公開済み。
- **E-1(宅配・案B固定・R0再利用・HRなし経路)= 未完走**。案Bは**1回判定でPASS**(OT-27のSTOPには当たらない)、HRなし経路(不在宣言→自動確定)は確認、Advanced音声(b1b)は完成。**Standard(a2)でTTS 3回上限に達した2 segment(`preview`[日本語]・`y_voice_1`[英語])がHuman Review Lock(ER-011)に入り、Gate BLOCK→組立・ページ・公開なし**(Lockは回避していない)。実費32.07円。
- 累計実費(Y立上げ): 14.347(02A)+82.718(E-3)+32.072(E-1)=**129.14円/Cap 170円**(残40.86円)。本日(JST)の開発費累計は`daily_dev_cost_01.py`で1,153.29円+未捕捉94.28円=1,247.57円(日次1,500円内)。

## 1. 実行条件・並行事故の記録(事実)
- 開始条件: (i) `origin/main`に「KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03」commit(daf0fdb8a)あり=充足。(ii) 日次累計1,014.06(開始時)+94.28+見積≤160=1,268円≤1,500=充足。
- 起動: E-3とE-1を**並列**(別run dir・別process)。`stop_scope_check_01.py`を各起動前に実行(全てrc=0、`<run>/stop_check_*.json`)。起動間隔: E-3 launch1 20:52→launch2 21:13、E-1 launch1 20:52→launch2 20:58→launch3 21:30(5分3回なし)。
- **共有working treeの並行編集**: run中に別agent(委任_04、commit 89b630bd1[21:23])が`er121_family_y_audio_01.py`(21:07:46)・`er121_family_y_structure_01.py`(21:05)を変更(X方式Chunk TTSのY適用=ユーザー追加決定USER_02①)、`er121_family_y_text_core_01.py`も未commitで編集中。影響:
  - **text stage(E-3/E-1とも20:52〜21:05)は変更前のtext core(module_sha `e0a6bf10…`)で実行**。案Bは当時の仕様=1回判定(委任_03指示どおり)。
  - **E-3 launch2(21:13)のTTSは変更後のaudio codeで実行**。`audit/chunk_tts_decision.json`は`applied_X_method`だが、**Y 8 segmentは全て1段落のため分割0**(`paragraphs=1<2`)=音声は従来の1 call生成と同等。委任文の「Chunk非適用」はUSER_02①(APPROVED_FOR_PRODUCTION)で上書きされた後の状態で記録された。
  - E-1 launch2のb1b TTSは変更前のaudio code(21:01にimport済み)、a2/launch3は変更後codeだが対象segmentはChunk無関係(各1段落)。
- Part A(結線)は`4437e98cf`でpush済み。run中のcodeは**Part A+他agent変更**の混合であることを上記のとおり明記する。

## 2. E-3(SNS年齢制限)結果
成果物: `er121_output/family_y_production_01/sns_age_limit/run_01/`(final_manifest.json、cost_log.jsonl、cost_by_stage.json、e2e_stage_log.jsonl、segment_coverage.json、verify_selection.json、text/、key_phrases/)。公開(限定共有): `user_test/family_y_production_sns_age_limit_01/index.html`(+`audio/`)。
- コマンド: `--mode real --slug sns_age_limit --run run_01 --theme-package docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/sns_age_limit_package_01.json --approved-budget-jpy 170 --stage all`(rc=4待機後、**同一コマンド**を再実行)。
- **stage順序**(e2e_stage_log.jsonl): seed_check→text(808.5秒)→translate(67.2)→support(33.5)→kp(候補生成→rc=4)→[HR操作]→seed_check→…→kp(37.7)→tts_b1b(246.3)→tts_a2(263.7)→gate→assemble(8.7)→pages(28.3)→page_verify。
- **Closing実使用**(`text/article_record.json` closing、cost_log): routing_key=`FAMILY_Y_CLOSING_GENERATE`、model_id=`gpt-6.1-sol`、effort=high、**Prompt 02 sha `4713ceff2dd00a2f67eb9313ae9e206a4a3236c5b158e624c10ccf6fc20e5f07`**(closing_general_02.txt)、source=`general_prompt_02`(`general_method_used=true`)、gen_calls=1、selected_id=C、書換え0、Gate(判定gpt-6-luna=`FAMILY_Y_LEAK_JUDGE`)=PASS・判定1回。Theme Package sha `aa37a1e1…`、判定履歴=`text/closing/gate/`。
- **Voice**: Sol high×3+UNMAPPED再生成×3(3/3発火。下記コスト所見)、出典付番(luna)・構造タグ(luna、発火なし)、Voice Gate(luna)=PASS・判定1回・書換え0(`text/voices/gate_voices/`)。routing key: `FAMILY_Y_VOICE_GENERATE`/`FAMILY_Y_VOICE_PROVENANCE_MAP`/`FAMILY_Y_VOICE_STRUCTURE_TAG`/`FAMILY_Y_LEAK_JUDGE`。Prompt sha: voice `48645f1d…`、lead `76282235…`、intro `787794d6…`。Lead生成(Sol)1回、人物紹介(Sol)2回(再生成1)、Lead+紹介の補助Gate(luna)=適用項目の指摘0(`applicable_flagged=[]`。対象外項目`leak_tension_reverts_to_research`は記録のみ=OT-28どおり)。最終付番でvoice_3にUNMAPPED 2文が残る(記録のみ・非blocking)。
- **逐語検査**: 204出典ファイルに対し連続一致0(`verbatim.n_hits=0`)。
- **Chunk記録**: §1(`chunk_tts_decision.json`、分割0)。中核数値v4/J2: Y非適用(final_manifestに記録)。
- **注意書き(AI編集告知)**: ページ本文外のみ。`tools/y_page_notice_check_01.py --expect y`=rc=0、`tools/user_test_page_standard_check_01.py`=PASS(公開dirの`index.html`)。text/support stageのAI_ANNOUNCE検査を通過。
- **segment ID網羅**: Y 8 segment(y_lead/y_intro_1/y_voice_1/y_intro_2/y_voice_2/y_intro_3/y_voice_3/y_closing)が両level(b1b/a2)に存在し全てOK(`segment_coverage.json`)。voice割当: Voice1=Algieba/Voice2=Zephyr/Voice3=Schedar/ナレーター=Aoede。a2は全Y segmentで減速適用。
- **Master store**: 共有ナレーション等は再利用(`er006_output/master_audio_store_01/reuse_telemetry.jsonl`の本run宛: b1b reused9/generated3、a2 reused10/generated3。keyはlanguage/speaker_voice/tts_model_id/style_instruction_id・version/canonical_text_hash/audio_processing_version等)。Y本文segmentは記事固有のため新規生成。
- **Gate**: `gate_summary.json` b1b=PASS・a2=PASS(`y_body_blocked=[]`)。page_verify `violations=[]`。assemble: B1 337.2秒、A2 349.8秒。
- **retry/HR Lock**: TTS再試行・HR Lockは発生せず。
- **実費(stage別、`cost_by_stage.json`)**: text 59.08(Voice生成12.97+UNMAPPED再生成14.92、Closing生成21.99、人物紹介4.79、Lead2.61、付番1.53、他<1)、translate 0.64、support 0.34、kp 3.35、tts_b1b 8.60、tts_a2 10.70。**合計82.7182円**(BUDGET_PLAN_03のE-3テキスト見積44〜62に対しtext 59.08=範囲内上限付近。通常Y記事1本の実測原価=82.7円)。
- **HRあり経路の証跡**(Fable代行の評価操作。実際の人間レビューではない旨を明記):
  - rc=4待機(`[KP_REVIEW_PENDING]`、`review_request.md`、候補sha b1b `208f5fd0764db2d9`/a2 `3f79580a85869463`)。
  - b1b: AI推奨 KP=1,2,3 に対し **KP=1,3,4**(AI順位外の候補4[AI推奨では『単語』枠]を採用し候補2を外す)、vocab=1,3,4,2,5、**NG 1件**(候補6「thrown into it」、理由「比喩的でQA FAIL旗付き、学習価値が低いため以後も出さない」)。a2: KP=1,2,4(AI推奨3→4に差替え)。操作者名`Fable代行(Sonnet実行/evidence操作)`。status=REVIEWED。
  - **`verify_selection_matches_outputs`(er119)=b1b/a2とも ok=true**(確定KP=TTS結果のKP英語text=公開ページHTML。b1b KP: draw the line / fit neatly together / raise the question of、a2 KP: draw a line / bring up another question / turn to adults)。`verify_selection.json`。Part 1(単語解説)・Part 2(文法)はY未接続のため検証対象外。
  - 文法(Part 2)HR: **Y未接続のため操作できず(未達)**。

## 3. E-1(宅配・案B固定・HRなし)結果
成果物: `er121_output/family_y_production_01/redelivery_fee/run_01/`。公開なし。
- コマンド: `--mode real --slug redelivery_fee --run run_01 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 170 --stage all`。Theme Package=THEME_DATA_02.json(sha `f0d0af36…`=registry一致)。
- **案B判定結果(1回): PASS**(`closing_record.gate`: n_judgements=1、rewritten=false、source=`judged_this_run`)。closing_final sha=案B登録shaと一致(`26745165…`)、source=`fixed_user_approved`、`general_method_used=false`。Voice R0 sha `566ebd97…`(byte一致)、Lead/紹介=revision_01再利用(決定論検査を再度通過)。**注意**: 02A較正では同系prompt(M-1後)で2/7 FAILだった案Bが、本番の1回判定ではPASSした(判定の確率的ばらつき。再判定・書換えによる救済は行っていない)。
- text API: Lead+紹介の補助判定1+案B判定1(luna、計0.117円)。Voice生成0(R0再利用、Voice Gateは来歴検査付き既存PASS記録を再利用)。
- **HRなし経路**: rc=4待機後、`declare-absent --runs <run_dir> --by "Fable代行(Sonnet実行)" --user-ref "…_USER.md §10-5" --reason "E-1 evidence…"`(宣言は`<run>/kp_review_mode.json`、rounds=[1])→同一コマンド再実行→KP自動確定。`kp_human_review.json`: **status=`UNREVIEWED_AUTO_ADOPTED`(b1b/a2とも)、`ng=[]`、`verdicts`全null、`last_human_op_at=null`、`mode_used`に宣言ID・declared_by・user_ref**=「未レビュー」と「NG」が区別して記録されている。`verify_selection_matches_outputs`(ページ検査なし)=b1b/a2とも ok=true(`verify_selection.json`)。
- Advanced(b1b): TTS完了。
- **Standard(a2)でHR Lock**: `preview`(日本語)と`y_voice_1`(英語)が「標準経路2回+fallback経路1回(合計上限3回)とも不合格」→ER-011 HUMAN_REVIEW_REQUIRED。
  - `preview`: ASR転写は「思い通りに」(正本『思いどおりに』)=かな/漢字の表記差のみで読みは正しい。**JA-ASR false-NG(OPEN-517と同型)の疑いが強い**(未検証)。attempts: ASR_VALIDATION_UNCERTAIN×2。
  - `y_voice_1`: attempt1=NORMALIZED_MATCHだがRepetition QAの短ラグspectral検査(0.68秒≥閾値0.6秒)でflagged、attempt2=ASR_VALIDATION_UNCERTAIN(ASR『re-deliveries』と正本『redeliveries』のハイフン差)。
  - Gate BLOCK(`y_voice_1`: STD_FALLBACK_USED_OR_UNKNOWN/Y_MISSING_MANDATORY_A2_SLOWDOWN)で組立・ページ・公開なし。**再起動(launch3、`--stages tts_a2,gate,assemble,pages,page_verify --regenerate-stage tts_a2`)でもLockは維持**(TTS/ASR 0 call。ER-011のとおり`approve_regenerate()`が無い限り再生成しない)。Lock解除は`er011_human_review_lock_01.approve_regenerate(approved_by="user")`=ユーザー承認の操作であり、本委任では行っていない。2回目のrc≠0は同一原因(Gate BLOCK)で新規API呼出0。以後は再起動していない。
- **実費**: 32.0715円(text 0.12、translate 0.47、support 0.42、kp 2.81、tts_b1b 10.88、tts_a2 17.37)。所要: tts_b1b 925秒、tts_a2 939秒(再試行・cooldown)。

## 4. 受入条件12項目との対応(`USER.md §10`、未達は未達と明記)

| # | 条件 | 本委任でのevidence | 判定 |
|---|---|---|---|
| 1 | 正式初回Production経路に実装 | runner→`produce_article`結線(4437e98cf)。E-3が正式runner経路で完走 | E-3で達成。E-1は途中(a2 HR Lock) |
| 2 | Y固有の承認済み構成維持 | 5パート+Voice割当+Aoedeナレーター+Std減速+IOL無しをE-3で確認(`segment_coverage.json`、`check_y_article`) | 達成(E-3) |
| 3 | Closing Prompt 02+Sol highが正式経路で実使用 | E-3: sol/high/sha 4713ceff…/Gate PASS(§2) | **達成(E-3)** |
| 4 | model_id/routing/Prompt hash記録 | `text/article_record.json`、`closing_record`、`cost_log.jsonl`(response_id付)。**残課題**: `final_manifest.stage_entries`のtext/kp/supportのmodel/routing欄がnull(translateは記録あり) | article_record側は達成/final_manifest側は不足=OPEN |
| 5 | HRあり/なし両経路 | HRあり=E-3(AI外選択+NG1+verify ok)。HRなし=E-1(不在宣言→UNREVIEWED_AUTO_ADOPTED、NGと区別)。**文法(Part 2)のHR経路はY未接続で未達** | KP: 達成(両経路)。文法: **未達** |
| 6 | 承認済み適用対象共通仕様が実装 | KP HR=実装済。Part 1/Part 2=Yへ**未接続**(`study_text_slots.json`)。Chunk=別委任(委任_04)で実装・本runでは分割0 | **一部未達**(Part 1/2) |
| 7 | Retry/fallback/regeneration/resume | resume(rc=4→同一コマンド、API 0再利用)=E-1/E-3で確認。TTS再試行上限→HR Lock→再起動後もLock維持(回避なし)=E-1。UNMAPPED再生成=E-3 | 達成(E-1のLock解除後の再開は未確認) |
| 8 | 必須Regression/Validator/integration test | Part A: Y関連187+新規結線7=194 PASS(socket遮断)。X/Z回帰(er006/er109/er103/er020)787 PASS/16 FAIL(02Bで報告済みの既知分類と同一、本変更起因でない) | 達成(既知失敗を除く) |
| 9 | 正式Production E2Eで実動作 | E-3完走。E-1はa2でHR Lock | E-3のみ達成。**E-1未達** |
| 10 | SSOT・Git更新 | OPEN-520更新、Part A commit、本文書commit | 本委任分は達成 |
| 11 | 未完了事項がOPEN追跡 | OPEN-520(残課題)、OPEN-517(JA-ASR false-NG)関連 | 達成 |
| 12 | ユーザー承認内容と実出力の一致 | E-3: 一般化Prompt02・Sol high・Gate・構成が承認原文どおり。E-1: closing本文=案B登録sha一致、Voice=R0 byte一致。**最終試聴PASSは別Status(未実施)** | 機械的照合は一致。人手の確認はFable/ユーザー |

## 5. 所見・残課題
1. **E-1のa2 HR Lock(最優先)**: 原因仮説=JA ASR false-NG(`preview`)と英語ASR/Repetition QAの表記差・近接検出(`y_voice_1`)。反証材料: ASR転写は正本と語順・内容一致(表記差のみ)。再現は未実施(有料・Lock維持のため)。次の一手候補=①ユーザーが2 segmentのwavを試聴して`approve_regenerate`/承認、②OPEN-517のProduction適用(別委任)後に再走、③`y_voice_1`のRepetition QA/英語ハイフン差は別所見としてFable判断。E-3(同一コード)では発生しなかったためY固有の欠陥とは断定できない。
2. **Voice生成のUNMAPPED再生成が3/3発火**(14.92円=E-3原価の18%)。通常Y記事の実測原価82.7円は量産単価70円を約12.7円超過。削減余地=初回draftでUNMAPPEDが出ない条件の調査(品質判断を伴うため独断変更せず、Fable/ユーザー判断)。Closing生成1 callが21.99円(reasoning約10,876トークン、268秒)で最大費目。
3. 記録の集約不足: `final_manifest.stage_entries`のtext/support/kpのmodel欄がnull(個別recordにはあり)。
4. Part 1(単語解説)・Part 2(文法)のY配線は別案件。KP HRのみ。
5. 案B判定の確率的ばらつき(02A: 2/7 FAIL、本番1回: PASS)。委任_04で案Bは再判定≤3回(書換えなし)へ変更済み=本run(1回判定)より後のcode。
6. 他agentの共有working tree並行編集により、run中にcodeが変わった(§1)。再走時はcommit済みの版で固定すること。
