# DESIGN_01: Family Y 正式Production runner 設計(Phase 0、設計のみ。API 0・Production変更0)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01 / 2026-10-25。Opus条件A独立レビュー依頼=`OPUS_REVIEW_REQUEST_01.md`。本書は**未実装の設計案**で、実装は条件Aレビュー反映後の委任_02以降。

## 0. 設計の前提・目標

- 目標: Family Y PRODUCTION_WIRED(Family別・仕様別に判定。ユーザー最終試聴PASSは別Status)。受入条件12項目(委任文§0)を満たす経路を作る。
- 制約: Prompt 02・Gate基準・案B本文は変更しない。DEV Trial(`er110_family_y_*`)は無変更で残す(既存Trial成果物の再現性)。Y専用の新Validatorを増やさない(既存Gateの移植のみ)。`er019/er026/er062/er006/er119/er120`は別agentが編集中=**新規fileを中心**にし、共有fileの編集は最小・限定列挙(§2)。
- Y基本構成・Voice原則・Closing一般化・案B個別採用は変更しない(EXISTING_SPEC_CHECK_01 §1)。

## 1. 構成判断: 新規file群 vs 既存runner拡張

| 案 | 内容 | 判断 |
|---|---|---|
| (a) X runnerを拡張 | `er019_family_x_audio_production_runner_01.py`(3,358行)にY分岐を足す | **不採用**。Xは3分割・In One Line・Comment4・segment順がコード固定(INVENTORY T3/T5/T9/T11)で、並行agentが編集中(Chunk/Part1/numeric配線)。X/Z Production変更リスクと競合が大きい |
| (b) **新規Y runner(Zと同じstage framework)** | 新規file `er121_*` を作り、X/Zの共通部品をimportして呼ぶ(Zが`er026`でX部品を再利用した先例) | **採用**。X/Z無変更。Y固有構造(5パート・Voice別TTS Voice・紹介・Closing)だけを新規に持つ |
| (c) DEV runner(`er110_*`)をそのまま昇格 | — | **不採用**。DEVは`patched_*`のモジュール差替え・alias segment ID・DEV専用の予算skip(Gate SKIPPED_BUDGET)を含み、Production化すると隔離と安全装置が崩れる。Production moduleは**DEVをimportしない**(委任文) |

新規file(命名`er121_*`。`er121`は未使用を`ls er12*`で確認):

| file | 責務 |
|---|---|
| `er121_family_y_production_01.py` | テキスト側core: Theme Package検査、Voice生成+Voice Gate、Lead/紹介、Closing(一般化/固定注入)、Closing Gate運用、5パート契約、英訳(Adv/Std)呼出、`Y_SEGMENT_IDS`、Prompt/schema/sha定数 |
| `er121_family_y_audio_01.py` | 音声側: segment計画、Voice別TTS Voice割当(決定論)、Y timeline builder(Adv/Std)、Y style gate、Std減速適用確認、ページ入力 |
| `er121_family_y_production_runner_01.py` | stage runner(Zの`E2E_STAGES`/`run_stage`/`stage_context`形式)。STOP/RUN_LOCK/費用guard/resume/`--regenerate-stage` |
| `er121_*_test_01.py`(複数) | test(§8) |
| `er121_prompts/closing_general_02.txt` | Production用Prompt 02(byte一致コピー。sha4713ceff…) |
| `er121_fixed_closing_registry_01.py`(定数module) | 案B固定注入の承認記録(§5) |

DEV `er110_family_y_*`は無変更。`production_reachable`の意味: DEVは`False`のまま、Production runnerの`entry_point.json`は`production_reachable=True`を記録(誤認防止のため両者のstatus文言を区別: DEV=`DEV_TRIAL_ONLY`、Production=`FAMILY_Y_PRODUCTION`)。

## 2. 共有fileの最小編集(列挙。各々DefaultOff/不変testを付ける。Opus条件Aの対象)

| 共有file | 編集内容 | 不変条件 |
|---|---|---|
| `er006_model_routing_contract_01.py`(+`er005_output/cost_baseline_01/pricing_snapshot.json`) | Y process key追加: `FAMILY_Y_VOICE_WRITER`(gpt-6.1-sol)/`FAMILY_Y_CLOSING_GENERAL`(gpt-6.1-sol, effort high)/`FAMILY_Y_LEAKAGE_JUDGE`(gpt-6-luna, effort high)/`FAMILY_Y_LEAD_INTRO`(gpt-6.1-sol)/`FAMILY_Y_CLOSING_REWRITE`(gpt-6.1-sol, medium)/`FAMILY_Y_TRANSLATE`系は既存X keyを共用 | 既存keyのmodel値不変(snapshot test)。未登録modelはfail-closed |
| `er103_proper_noun_alarm_policy_01.py:42`・`er109_xz_scope_01.py:25` | `APPROVED_SCOPES`に`"Y"`追加(28-1運用7。開示事項) | A/B/Cは従来経路でバイト一致(既存署名43,033件テスト再実行) |
| `er020_tts_retry_local_rewrite_01.py` `resolve_narrative_role` ほか | Y segment ID(§4-3)のrole解決を追加、import時自己検査に追加 | 既存ID(full_story_part*, ..._c{k}, ..._k{j}, comment_n)の解決不変(既存testを全通し) |
| `er_user_listening_page_common_01.py`・`tools/user_test_page_standard_check_01.py` | 注意書き枠(Y専用引数、既定None=出力不変)。検査のY見出し誤検知(`One Voice:`型)対応 | X/Z既存ページ出力のバイト一致 |
| `er019/er026`(runner本体) | **編集しない** | — |
| `CURRENT_SPEC.md`「共通仕様のFamily別配線Status表」 | Y列を台帳に合わせ更新(実装後のSSOT反映) | — |

## 3. stage列・I/O・routing・resume

Zの`E2E_STAGES`形式。`--mode dry-run|mock|real`、各stage開始前に`<run>/STOP`・`STOP_ALL`確認(rc=3)+`RUN_LOCK.json`(Z方式)。stage別推定費用guard(`E2E_STAGE_EST_JPY`相当)と`--approved-budget-jpy`(超過見込みで課金前STOP)。

| # | stage | 入力 | 出力 | model/routing | 備考(resume key) |
|---|---|---|---|---|---|
| 0 | `package_check` | Theme Package(`THEME_DATA`形式: world_frame/sheets/出典付き意見/権利メモ) | `package_verdict.json` | LLM 0 | schema・出典逐語照合・Persona3名・立場3・R2+のみ根拠の警告。sha記録 |
| 1 | `voices` | Package | `voices.json`+`voice_gate/` | `FAMILY_Y_VOICE_WRITER`=gpt-6.1-sol / Gate=`FAMILY_Y_LEAKAGE_JUDGE`=gpt-6-luna | DEV opinion_based_03/02の生成+UNMAPPED再生成+Voice Leakage Gate(7項目、判定≤3・局所書換え)。**Gate予算skip禁止**。`--reuse-voices <manifest>`で既存R0を来歴検査付きで採用(§7) |
| 2 | `lead_intro` | Package+Voices | `lead.txt`,`intros.json`+gate | `FAMILY_Y_LEAD_INTRO` | 決定論検査(Lead 115〜160字、紹介32〜62字)。Tension専用2項目は適用外の既存扱い |
| 3 | `closing` | Package+Voices(+registry) | `closing.txt`,`closing_analysis.json`,`closing_gate/`,`closing_record.json` | `FAMILY_Y_CLOSING_GENERAL`=gpt-6.1-sol/high、Gate=luna | §4。一般化 or 固定注入。`closing_record.json`に`source`/`prompt_sha256`/`model_id`/`effort`/`routing_key`/`selected_id`/Gate履歴 |
| 4 | `ja_assemble` | 2〜3の出力 | `article_ja.md`(5パート)+`mapping`検査 | LLM 0 | 5パート契約・In One Line/AI告知混入検出・Voice本文byte一致(R0再利用時) |
| 5 | `english` | `article_ja.md` | Adv/Std `parts.json` | 既存X英訳routing(Adv忠実英訳、Std簡易化) | 段落数=5、Voice個性保持検査、連続一致(日20字/英8語)による出典コピー検出、In One Line生成なし |
| 6 | `plan` | parts | segment計画 | 0 | Y segment ID(§4-3) |
| 7 | `support` | parts | Preview/Comment1〜3/日本語タイトル(Std) | 既存`SUPPORT_MODEL` | Y版role文 |
| 8 | `kp` | parts(全文) | KP・gloss・解説+`part1_items` | 共通`sc.run_key_phrases`→`run_key_phrase_canonicalization`(hook付き, OPEN-484 a〜f) | **接続点**: er119のHR(wait/auto)、er120 Part 2、Part 1(study_text)はこのstage直後に差込(§9) |
| 9 | `tts_b1b` / `tts_a2` | 各level text+plan | segment wav+`tts_generation_results.json` | TTS=gemini-3.8-flash-lite-tts(`FAMILY_X_FLASH_LITE_TTS`)、ASR=AUW共通 | Voice 1〜3=Algieba/Zephyr/Schedar、ナレーター=level別Full Story設定。retry/fallback/Local Rewrite/HR Lockは共通。Chunkは非適用 |
| 10 | `provision_shell` | — | shell固定segment | 共通 | Welcome/Intro/Outro/Notification。**Z運用注意(OPEN-480): 再実行は`provision_shell,gate,assemble,pages,page_verify`を1起動で指定** |
| 11 | `gate` | results | `gate_summary.json` | — | style_profile gate(+Y body拡張)・key_phrase_source_gate・shared narration gate・Audio Validation Gate・Std減速確認 |
| 12 | `assemble` | — | 最終mp3×2level | — | Y timeline builder(§4-4) |
| 13 | `pages` / `page_verify` | — | 限定共有ページ+検査 | 共通page builder | 注意書き表示、内部情報非表示、実再生検査 |

resume/regeneration: 全stageが出力sha・入力shaを`stage_state.json`に記録し、一致すればAPI 0でスキップ。`--regenerate-stage voices|lead_intro|closing|english|support|kp|tts_*`(下流を`DEPENDENTS`で自動無効化。Zの`DEPENDENTS`方式)。`--only-segments`はtts専用(X仕様)。**Closingの再生成は`--regenerate-stage closing`の明示のみ**(Gate FAIL後の自動全文再生成はしない=既存retry上限に従う)。

## 4. 主要設計項目

### 4-1. Voice生成(stage 1)
- DEV `er110_family_y_opinion_based_01/02/03`のVoice Prompt・Persona描画・UNMAPPED再生成・出典照合を**Production moduleへ関数として展開移植**(DEVの`patched_ob_03()`等のモジュール差替えは使わない=import時副作用の排除)。Promptの文面は一字も変えず、sha固定testを付ける。
- 歯止め: 出典との連続一致(日20字/英8語)0件、創作確定0、数字不使用、反復検出。Voice Leakage Gate(7項目)は判定≤3・局所書換え・`LEAKAGE_RESIDUAL_STOP`。DEV専用の「累計22円超でGate SKIPPED_BUDGET」は**移植しない**(Gate省略禁止、費用は事前見積と`--approved-budget-jpy`で管理)。

### 4-2. Closing一般化(stage 3、通常経路)
- Prompt: `er121_prompts/closing_general_02.txt`(Prompt 02のbyte一致コピー。**sha4713ceff…をtestとruntimeで照合**、不一致はSTOP)。入力ブロック(THEME/PERSONA/VOICE)・選定処理・schema(`family_y_closing_general`)・決定論検査(`check_structure`+`check_closing`+記号gate)・再生成1回・`CLOSING_GENERAL_CONTRACT_STOP`は、EXISTING_SPEC_CHECK_01 §3のとおり**そのまま移植**(意味変更・Prompt 03化なし)。
- 生成: `gpt-6.1-sol` effort high。**応答modelが期待と不一致ならSTOP**(`response.model`照合)。`closing_record.json`にactual model_id・routing key・prompt sha・user prompt sha・effort・gen回数・`selected_id`を記録。
- Gate: Tension 6項目(定義無変更)を`run_gate`(判定≤3・局所書換え・`LEAKAGE_RESIDUAL_STOP`)で運用。局所書換えpromptに選定済み切り口(`selected_id`のnew_view+evidence_quotes)を付加(PROMPT_GATE_ALIGNMENT_01 I-1)。判定回数・理由・引用を`gate_history`に全保存(I-2)。残存STOP時は暫定版を公開せず、JA稿+FAIL記録を保存(I-3)。**Gate FAILの自動全文再生成はしない**(再生成は明示`--regenerate-stage closing`のみ)。

### 4-3. Y segment ID(DEVのalias廃止)
DEVは本文5segmentを`full_story_part1/2/3/3_c2/3_c3`に載せて共有QAに乗せた暫定(Zの`_c{k}`はDialogue clipの意味)。Productionは意味が衝突しないY専用IDを導入する: `y_lead`, `y_intro_1..3`, `y_voice_1..3`, `y_closing`(命名は条件Aレビューで確定)。`resolve_narrative_role`・Connected Speech/Local Rewrite/Repetition/disfluency QA・`--only-segments`の対象に追加(共有fileの最小編集)。role割当: lead/intro/closing→FULL_STORY(ナレーター)、y_voice_n→FULL_STORY(人物TTS Voice)。**追加漏れ防止**: 全Y segment IDが各QA対象表に含まれることを固定するtest(T8対策)。

### 4-4. 音声・timeline
- Voice割当: Z正式表の`assign_dialogue_voices`を呼び、Algieba/Zephyr/Schedar(固定、期待値test)。ナレーターはlevel別既存Full Story設定から導出(`Y_BODY`の`Aoede`直書きを廃止)。Adv補助(Welcome/Topic/Preview/Comment等)=Charon(X仕様)。
- 順序(Adv/Std共通骨格): Intro→Welcome→Topic→(Std:日本語タイトル)→N1→Preview intro→Preview→N2→KP intro→KP×3→N3→Full story intro→**Comment1→Lead→Comment2→[紹介1→Voice1]→[紹介2→Voice2]→[紹介3→Voice3]→Comment3→Closing**→Outro。In One Lineなし。Voice間gapは既存値(`CHARON_TO_AOEDE_PAUSE_SECONDS`相当)を再利用(Y固有の新値なし)。
- Std減速: X準拠既定(Y Std本文全segmentで`slowdown_applied=True`確認)。Chunk分割は**非適用**(YL-B08判断待ち)。
- Style: profile `fx_20261017`を継承(OPEN-415はZ方式[定数参照+drift test]を採用)。

### 4-5. 英訳
Adv=日本語の忠実英訳(段落数5、追加削除なし)、Std=Advからの簡易化(A2語彙・段落維持)。In One Lineは生成しない。紹介行/Voice行の2行構成をパート内契約として検査。**Voiceの個性保持**(一人称・口調・迷い)をStdでも削らない(USER_09 §3)ことを、Y Trial既存の英語監視(`en_monitors`)の移植で記録。

### 4-6. 公開ページ
共通builder+注意書き枠。注意書き文言=`PAGE_NOTICE_JA`(逐語)。内部ID・Voice名/Style等の内部情報は載せない。PASS_WITH_WARNINGは折りたたみ。限定共有(unlisted・noindex・転載不可注記)。

## 5. 案B固定Closing注入(例外の監査可能化)

- 手段: コード定数`FIXED_CLOSING_REGISTRY = {slug: {text_sha256, text, approval_ref, approved_on, scope}}`(`er121_fixed_closing_registry_01.py`)。slug=`redelivery_fee`のみ、text_sha256=`26745165e33be3ea5cf4548f365c6d145862d94ad0201cc69695c0a954800e71`、approval_ref=`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`§2-3。**環境変数・CLI flag・設定dictで他記事へ流用不可**(registryに無いslugは必ず一般化方式)。
- 動作: stage `closing`はslugがregistryにあれば生成API 0で注入し、`closing_record.json`に`source="fixed_user_approved"`・`approval_ref`・`text_sha256`・registry版sha・「一般化方式(Prompt 02)を使っていない」旨を記録。run summaryと完了報告に**固定注入であることを必ず表示**。
- Gate: 注入本文も**Leakage Gateを1判定通す**(迂回なし)。ただし**局所書換えは禁止**(ユーザー承認本文を改変しない)。FAILなら`STOP`してFableへ報告(同一本文の判定再試行で通さない)。
- 決定論検査: 一般化方式用`check_closing`は適用しない(案Bは問い2つ等で一般化規則と異なる承認本文)。代わりに本文sha一致・段落1・数字なし・AI告知なし・5パート契約のみ検査。
- 受入との関係: **受入条件3『Prompt 02+sol highの実使用』は宅配(案B固定)では満たされない**。別記事(SNSの年齢制限、Voice既存)の**一般化経路runtime evidence**を別途取る(§10 E-3)。

## 6. HRあり/なし・retry/fallback/regeneration/resume

- HR(KP/文法): er119/er120の確定I/Fに依存。Yは接続点でmode宣言(`wait`/明示auto dict)を受け取り、HRなしは「Human不在時TOP1〜3/TOP1〜5を自動採用、NGと未レビューを区別、NG自動採用なし」(OPEN-518)。HR待ちはrc=4で中断し、再開は同runの`--stage kp`以降のみ(再抽出なし)。
- retry/fallback: TTS/ASR=共通(通算3回、KP英語4回、Local Rewrite、fallback、HR Lock)。テキスト側=技術retryのみ(API失敗・JSON不正)+Closing決定論再生成1回+Gate判定≤3。**内容を理由にした全文反復再生成はしない**(OPEN-217/X設計思想)。
- 失敗終了時の最終成果物: 各stageは`stage_state.json`と部分成果物を残し、STOP理由を`run_status.json`に記録。Closing残存FAIL=未公開JA稿+FAIL記録、TTS HR Lock=該当segmentのHR Lock+その手前までの成果物(ユーザー向け完成物は出さない)。目的要件(完成音声+限定試聴ページ)に対しては「未完成と明示」して報告。

## 7. 既存成果物の再利用(来歴契約)

宅配の既存成果(Voice R0 Gate PASS・改訂Lead/紹介・案B本文・英訳一部)は、**手動コピーではなく来歴検査付きの再利用**として取り込む: `--reuse-voices <manifest>`(manifest={source_path, sha256, gate_status, produced_by})。Voice R0はGate PASS済み・sha一致を必須、Lead/紹介はREVISION_01のgate PASS・sha一致を必須。不一致は再生成せずSTOP(Zの`U-1`来歴契約と同思想)。再利用したことを`reuse_record.json`に残す。

## 8. test計画(API 0)

1. Prompt/schema: Prompt 02 sha一致、DEVとのbyte一致、schema・入力ブロック描画の一致(DEV関数との出力一致をfixtureで固定)、Prompt変更検出。
2. 隔離: `er121_*`が`er110_*`をimportしない/DEVがProductionをimportしない、import時API 0・副作用0、Y機能がX/Z runnerから到達しない(AST)。
3. routing: Y keyのmodel値・actual model_id照合・未登録fail-closed・pricing。
4. Gate: 判定器入力・Tension 6項目定義の不変、`run_gate`の判定≤3、`LEAKAGE_RESIDUAL_STOP`、Gate予算skip不在(Grep)。
5. 固定注入: slug限定、sha一致、registry外slug拒否、Gate FAILで書換えず`STOP`、表示記録。
6. 5パート: splitter、mapping検査、In One Line/AI告知混入検出、Voice別TTS Voice期待値。
7. segment ID: 全Y IDがQA対象表に含まれる網羅test、既存ID解決不変。
8. resume/regeneration/STOP/RUN_LOCK/費用guard。
9. 共有file編集の不変test(A/B/C・X/Zのバイト一致、43,033署名)。
10. 全回帰(`run_project_regression.py`)。自分起因failed 0。
11. **API遮断の担保**: 新規testは全てmock/ネットワーク遮断harnessで実行し、`api.openai.com`等への接続試行0を確認する(隣接案件OPEN-518で、既存testのmock漏れから推定6〜15円の実LLM呼出が発生した教訓。Y testはProduction関数(`generate_*`)呼出箇所を全てfake clientへ差替え、client未注入ならtest内で例外)。

## 9. 進行中仕様の接続点(確定I/Fに依存)

| 接続点 | 依存先 | 現状 | Yでの扱い |
|---|---|---|---|
| KP HR(wait/auto) | `er119_kp_human_review_01.py`/`er119_kp_wiring_01.py`(別agent。commit d7a5713d4で`IMPLEMENTED_PENDING_EVIDENCE`、単体test 104件PASS、Production run 0) | KP側X/Z共通核は実装済み・実API evidenceは10/26以降。Yは明示的に「入口なし」 | stage 8の後にhook。I/F確定後に結線。HRあり/なし両evidence |
| 文法HR・Part 2 | er119 kind=grammar、`er120_part2_grammar_production_01.py` | module完成・runner未接続 | Adv限定。0件許容 |
| Part 1 | `er003_kp_general_explanation_01.py`+`er003_kp_source_sentence_ja_01.py` | X/Z PRODUCTION_WIRED | stage 8直後(Adv)。`part1_items`をHRと共有 |

## 10. evidence計画(正式E2E)

| ID | 内容 | 目的 |
|---|---|---|
| E-1 | **宅配(案B固定)を正式経路で1記事完成**(Std+Adv、再利用manifest使用、限定共有ページ、実再生検査) | 受入1,2,5,6,7,8,12。E2E evidence兼用(ユーザー最終試聴待ち) |
| E-2 | **HRなし**(auto)と**HRあり**(wait→選択→再開)の両経路をKP段で取得(本文・body TTSはMaster store再利用、KP差分のみ) | 受入5(HRあり/なし) |
| E-3 | **一般化Closing経路のruntime evidence**: SNSの年齢制限(Voice既存)で`closing`stageを実行し、Prompt 02+gpt-6.1-sol high・model_id・routing・sha・Gate履歴を記録。英訳まで(音声は宅配で検証済みの共通経路) | 受入3,4 |
| E-4 | 全回帰・隔離・Dangling Reference 0 | 受入9,10 |
| E-5 | SSOT/Git(OPEN・DECISION_LOG・CURRENT_SPEC配線表・台帳) | 受入11 |

受入条件12項目との対応は`BUDGET_PLAN_01.md`末尾の表と同一(各E-xが担当)。

## 11. Dangling Reference防止
- 削除・置換するもの: Productionでは`Y_BODY`のAoede直書き/alias segment ID/`in_one_line`参照/DEV予算skipを移植しない。DEVは残置(参照されない)。
- 新規参照を追加する際: ledger行(`spec_ledger_01.json`)・OPEN-520・CURRENT_SPEC配線表のY列を同時更新し、grepで`er121_`の被参照・docs内のpathが実在することを確認(Closeout)。
- 台帳に`YL-*`の行がある仕様名は、実装後に`PRODUCTION_WIRED`/`WIRED_PENDING_FABLE`を記入。

## 12. 作業分解・並列案・クリティカルパス・所要見込み

| レーン | 作業 | 依存 | 並列 |
|---|---|---|---|
| L1 テキストcore | Voice/Lead/紹介/Closing/Gate/固定注入/英訳呼出(+test) | routing key(L3) | L2,L3と並列 |
| L2 音声/ページ | segment計画・timeline・Y style gate・ページ(+test) | segment ID方式(L3) | L1,L3と並列 |
| L3 共有file最小編集 | routing・scope・resolve_narrative_role・page共通・検査tool | Opus条件Aレビュー反映 | **先行(クリティカルパス)** |
| L4 runner | stage framework・STOP/RUN_LOCK・費用guard・resume | L1/L2の関数I/F | L1/L2の後半と重ねる |
| L5 接続点 | er119/er120/Part 1の結線 | 別agentのI/F確定 | 別委任(独立) |
| L6 evidence | E-1〜E-5 | L1〜L4 | E-2/E-3はE-1と並列可(Master store・Package別) |
| L7 SSOT/台帳 | OPEN-520更新・CURRENT_SPEC配線表 | 随時 | 並列 |

クリティカルパス: Opus条件Aレビュー反映(L3)→L1/L2→L4→E-1。所要見込み(Sonnet実装+test、**見込み・未実測**): L3 約0.5日、L1 約1日、L2 約1日、L4 約0.5〜1日、E-1〜E-3 約0.5日、SSOT/Git 約0.25日。L1〜L3並列で**約2〜3日**(実装2日+evidence1日)。L5(HR/Part 2接続)は別agentの完了に依存し、接続は+0.5日。直列化は(a)Opus条件Aレビュー(必須Gate)→実装、(b)有料runは日次予算・STOP確認後、(c)共有file編集は並行agentとのcommit競合回避(一時index方式)に限る。

## 13. 開示・リスク
- DEV Trialの暫定実装(alias ID・DEV skip等)をProductionへ持ち込まない方針のため、移植量は大きい(DEV約5,100行のうち必要部分)。
- 固定注入は例外機構であり、記事を増やす際は誤用防止のため登録時に毎回ユーザー承認refを要する。
- 一般化Closingの品質は2テーマ・10生成でVALIDATED(限定)。量産時の分布は未測定。
