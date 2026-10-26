# REMOVAL_01 — 撤去・書換え・残置の一覧(旧条件が正式経路・Validatorに残らないための台帳)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(設計・read-only。本書の撤去は委任_02で実施)。行番号は本委任時点のworking tree(HEAD d2269a26b)の実測。
前提: 撤去は**X/Y/Z run scope内(`er109_xz_scope_01.current_scope() in {X,Y,Z}`)の正式経路**が対象。Family A/B/C(Legacy凍結=PM_GOVERNANCE 27-3/27-7)は旧コードを温存し、出力をbyte同一に保つ(DESIGN_01 D1)。残置は必ず理由とGrep期待値を付ける。
実装時の再Grep必須: CURRENT_SPECの行番号は更新で動く(棚卸し時点の`2873/2954/2963`は現在`2873`=ASR値ガード記述等、別内容)。**行番号ではなく節の見出しとキーワードで特定する**。

## 1. 撤去する(scope内正式経路)

| ID | 対象 | 場所(ファイル:行) | 処置 | 置換先 |
|---|---|---|---|---|
| R-01 | 600秒cooldown定数の正式使用 | `er020_tts_retry_local_rewrite_01.py:57` `COOLDOWN_SECONDS = 600.0`、`:64-93 maybe_cooldown_before_attempt`の既定引数 | 正式定義を`er127.COOLDOWN_SECONDS=180.0`へ。`er020`は`LEGACY_COOLDOWN_SECONDS=600.0`(scope外専用)に改名。`maybe_cooldown_before_attempt`は旧シグネチャを温存(A/B/C golden互換) | D2 |
| R-02 | cooldown呼出の個別実装(4箇所) | `voice01:156`、`news_tail_fix:149`、`crosslevel:200`、`repro01:339` | scope内は`policy.before_attempt`/`between_stages`→`cooldown_core`へ。scope外は旧呼出を温存 | D2 |
| R-03 | Z ctx独自cooldown | `er122_fz_ctx_policy_01.py:41-44 cooldown_seconds()`、`:298-338 _cooldown_before_fallback`、doc `:2,:8,:299` | `cooldown_core`委譲(外形・イベント名`CTX_COOLDOWN_BEFORE_FALLBACK`維持)。docの「600秒」→「180秒」 | D10 |
| R-04 | LR再TTS=1回(`max_attempts=1`) | `voice01:365`、`news_tail_fix:372`、`crosslevel:425`(`_run_a2_minimal_fallback_attempt`直呼び) | scope内は3回構成のLR block(`BlockCtx(depth=1)`)。scope外は温存 | D4 |
| R-05 | LR再入経路(`cs`でLR分岐、深さカウンタなし) | `voice01:304/:323`、`news_tail_fix:294-300/:325`(`if enable_connected_speech_equivalence_layer:`) | scope内はdepth guardでLR分岐に入れない。`cs`はjudge層(CS Equivalence)の切替に純化 | D4 |
| R-06 | LR再TTSのStyle脱落/部位差 | `news_tail_fix:370-377`(`style_prefix_override`未転送)、`crosslevel:425-427`(minimal固定) | 元の引数一式を転送(①②=元Style/③=Fallback Style) | D4 |
| R-07 | Adv英語「品質NGではStyle不変、技術エラー時のみ切替」 | `voice01:179-216`、`news_tail_fix:171-181`(F-Techのみの分岐) | ③(ordinal==3)で`_run_a2_minimal_fallback_attempt`へ分岐。F-Techは別枠として残す(撤去しない) | D3 |
| R-08 | LR回復helperの3複製 | `voice01:337`、`news_tail_fix:346`、`crosslevel:402` | scope内は`er127.lr_recover`へ統合。scope外は旧helper温存 | D4 |
| R-09 | KP二段の3複製 | `repro01:797-880`、`er019_family_x_kp_en_k2_store_01.py:55-95`、`er063_family_z_audio_01.py:1069-1100` | `er127.kp_two_stage`へ統合(cooldownはENGLISH_LOCK段の実TTS直前) | D8 |
| R-10 | KP解説の単一段3回 | `er019:1202 KP_EXPLANATION_MAX_ATTEMPTS=3`、`:1205-1220`、コメント`:1212-1213`(「統一フロー『TTS①②③、3回NGでLR/HR』に揃える」=LR配線なしの誤記) | 二段化(2→180秒→短文1)。定数は`BLOCK_PROFILES["KP_EXPL"]`へ移し、コメントを新仕様の記述に訂正 | D9 |
| R-11 | Std本文の外側ループ(案A採用時のみ) | `n3_tts:331-431`(`generate_a2_segment_with_slowdown`の周回・`generations_used`)、`:434-495 generate_with_a2_slowdown_outer_loop`、`:309 finalize_a2_slowdown_final_ng`、`prior_generations`/`cooldown_total_budget`引数(`crosslevel:93-95付近`、`repro01:336-343`)、OPEN-270 M3コメント | Std/chunk本文は減速+再検証をattempt内へ。Z Adv dialogue用の`generate_with_a2_slowdown_outer_loop`は**据置**(D10: U-07据置)。案C縮退時は全て残置 | D6 |
| R-12 | 旧回数文言(「総4」「総3」「4回目以降は絶対にTTS生成しない」) | `CURRENT_SPEC.md`の「TTS生成の同一segment総試行回数上限」行(:1857)、`er011_human_review_lock_01.py:60-104`のコメント、`er122_fz_ctx_policy_01.py:2,:11`、`final_reason`文言(`er122:`)、`er063:885,1023`コメント | 「1ブロック3回(LRあり部位は元+LR blockで最大6、KPは4)、待機はブロックごと1回180秒」へ書換え。`PRODUCTION_MAX_TTS_ATTEMPTS=3`は**1ブロックの上限**として残す(値は不変、assert 2+1==3も有効) | 全般 |
| R-13 | 旧10分記述(正式仕様・コメント・docstring) | `CURRENT_SPEC.md:1531`(「10分cool-down→attempt3→NGならLocal Rewrite」)、`:1647`(Z試行列「固定600秒」)、`:1649`、`:2185`(2026-09-26承認の「固定600秒cool-down」を含む表)、`:1652`(runtime evidence記述は過去事実=書換えず追記)。コード側: `er020:7,10,55,69-70`、`voice01:65,153`、`news_tail_fix:146`、`crosslevel:189-199`、`repro01:258`、`er122_fz_ctx_policy_01.py:2,8,42,299`、`er122_fzcw_runtime_evidence_01.py:5,43`、`er063:885,1023` | 現行仕様欄は180秒へ更新(承認履歴の過去記述は「2026-09-26=600秒→2026-10-26=180秒」と履歴化)。コメントは新仕様へ | 文書 |
| R-14 | 旧testが固定している条件 | §3 | §3の表のとおり更新/新規 | — |
| R-15 | 旧文書の誤記(Grep再確認) | `er121_family_y_audio_01.py:17`(「Std本文はchunk化しない」=既に是正済みの仕様に反する古記述、U-11)、`CURRENT_SPEC.md`の「対象外にStandard(a2)・Family Yを含めていた」旧記述の残存確認 | U-11としてコメント訂正(本件でコード編集するファイルのみ同時に直す。er121_audioは本件で触るため同時) | 文書 |

## 2. 撤去しない(残置)と理由

| ID | 対象 | 場所 | 残置理由 | Grep期待値(scope内正式経路) |
|---|---|---|---|---|
| K-01 | `LEGACY_COOLDOWN_SECONDS=600`・`maybe_cooldown_before_attempt`旧シグネチャ・旧LR helper・`max_attempts=1`旧LR retts | er020・voice01・news_tail_fix・crosslevel | Family A/B/C(Legacy凍結、27-3)のbyte同一を保つ。X/Y/Z scopeからは到達不能(testで固定) | X/Y/Z scope専用module(er019/er121/er063/er122/er026/er127)に`600`のcooldown用途0件 |
| K-02 | Trial/観測用定数 | `er020_tts_cooldown_local_rewrite_trial_01.py:64`(`COOLDOWN_SECONDS=600`、Trial)、`er011_tts_cooldown_observation_01.py:107`(1200秒観測) | 過去Trialの再現性(VALIDATED成果物の根拠)。Production経路から参照されない | Production runner/leafからのimport 0件(Grep) |
| K-03 | `stop_retrying`分岐(cascade OFF専用) | voice01:302/559/611、news_tail_fix:294、crosslevel:273/395、n3_tts:798、er012_b:624、repro01:482 | rollback互換。到達不能だが撤去対象を増やさない(棚卸しU-14=Fable判断どおり) | 変更なし |
| K-04 | `min(max_attempts, 3)`クランプ | voice01:487、n3_tts:732、crosslevel:149 | `max_attempts=6`を渡す旧caller(A/B/C・shell JA[er006_audio_cost_pilot_02:243]・B1 scaffold等)のため。意味を「1ブロックの上限」に再定義 | 変更なし |
| K-05 | F-Tech(attempt内の技術エラー即時minimal再TTS)・`_call_tts_with_retry(max_retry=1)` | voice01:179-216、news_tail_fix:171-181、er012_b:508-527 ほか | 原文§2「技術エラー再試行は別枠で維持」 | 変更なし |
| K-06 | shell固定英語(X-A09/Y-S-01/Y-B-01)の「同一Style3回・LRなし・待機なし」 | `shared_narration`経由のvoice01 L1(policy=None) | 表外(A-1)。生成0が通常・失敗0。拡張する場合は③のStore汚染対策が要る | 確認事項A-1 |
| K-07 | Z dialogueのAdv外側ループ(`generate_with_a2_slowdown_outer_loop`)・U-07(M-3(ii)) | n3_tts:434-495、er063:1033-1038、er122 | 原文は「Zセリフ=LR追加なし・従来方式」のみ。外側ループの行会計(OPEN-528 Deferred(2))は別判断 | 変更なし |
| K-08 | Y Gate/X M3の規則(`STD_FALLBACK_USED_OR_UNKNOWN`/`LOCAL_REWRITE_RECOVERY`/`ADV_MINIMAL_FALLBACK`/`JA_FALLBACK_USED_OR_UNKNOWN`) | er121_audio:700-715、er019_style_profile:685-743 | Gate方針は品質Gate(ユーザー判断事項)。DESIGN_01 D13 | 変更なし |
| K-09 | ER-011の安全上限 | er011:68-69(累積TTS15/ASR60)、RESTART_STORM、RUN_LOCK、`BUDGET_GUARD`、Review Lock | 原文§2「安全上限・STOP条件も維持」。LRあり部位の6 attemptは15以内(再生成を重ねる3周目でBUDGET_GUARD=既存仕様) | 変更なし |

## 3. 旧testの更新・新規(固定されている旧条件)

| test | 固定している旧条件(ファイル:行) | 処置 |
|---|---|---|
| `er122_fz_ctx_policy_test_01.py` | `:117-131` `test_case3_*_cooldown_600_*`/`test_case3b_cooldown_constant_is_the_existing_600_not_shortened`(`cooldown_seconds()==er020.COOLDOWN_SECONDS==600.0`)、`:122,124,126` sleep合計600/`>=600`、`:208-210` resume=600、`:219` | 180へ更新(定数は`er127.cooldown_seconds()`参照に変更し、`==180.0`をexplicitに固定)。5秒刻み(`SLICE_SECONDS`)・resume残り時間の論理は不変 |
| `er122_fzcw_runtime_evidence_test_01.py` | `:207`(コメント600秒)・`:213` `sum(sleeps)==1200.0`(2 clip×600) | 2 clip×180=360へ |
| `er063_fz_ctx_wiring_test_01.py` | `:248` `sum(sleeps)-600`・`e3[...]["total_elapsed_since_ref_seconds"]>=600`、`:396` | 180へ |
| `er007_ja_tts_retry_path_fix_test_01.py` | `:465` `mock_sleep.assert_called_once_with(600.0)`、`:469` `cooldown_requested_seconds==600.0`(crosslevel fallback経路のcooldown+LR回帰。docstring:380-392) | scope外=600(旧)をgoldenとして維持するtestと、scope内=180を検証するtestの2本に分離 |
| `er020_tts_retry_local_rewrite_01_test_01.py` | `:68-88`(`m.COOLDOWN_SECONDS`参照。既定引数の旧挙動) | 旧シグネチャ維持のため**変更なし**(legacy golden)。`LEGACY_COOLDOWN_SECONDS`名の追加testを足す |
| `er026_family_z_stop_sentinel_test_01.py` | `:352-353` `slept==[er020.COOLDOWN_SECONDS]`(共有module本体のcooldown) | legacy golden(変更なし)+scope内STOP確認付き分割sleepのtest追加 |
| `er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py` | `:52-61` LR→`retts_fn`1回→外側ループ、`:91-117`(Std path/outer loop/LR非採用/LR後最終NG) | scope内: 3回構成のLR block・減速後再検証をattempt内(案A)で再表現。scope外: 現行のまま(golden) |
| `er020_lr_post_rewrite_expected_text_fzaq2_test_01.py` | `:241`(cooldown stub)・LR後の正解原稿 | 期待text規則は不変。LR blockの複数attempt(書換え後textを全attemptで正解とする)を追加検証 |
| `er078_asr_unified_wiring_05_test_01.py`、`er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py:432,478`、`er058_asr_tts_prodfix_01_test_01.py:381-397`(M3: 2周目でも600秒cooldownが通算3回目直前) | `maybe_cooldown_before_attempt`のmock/spy、LR retts、OPEN-270 M3 | scope内は`policy`経由の呼出に差替え。M3(通算3回目直前)は案Aで「attempt==3直前」へ単純化(外側ループ撤去) |
| `er063_family_z_audio_01_test_01.py:64` | fake `cooldown_actual_seconds: 600.0`(fixture値) | 180へ(整合) |
| `er019_*kp*_test`、`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`、`er019_family_x_kp_structure_wiring_01_test_01.py` | KP二段の分岐順序 | `kp_two_stage`へ移しても挙動同一(待機以外)をregressionとして維持 |
| `er019_family_x_pointless_01_test_01.py:75-97 FamilyAUnchangedTest` | 共有TTS層(`er003_v1_n3_01_tts_generate.py`/`voice01`/`news_tail_fix`)のworking tree diff=0 | **commit後に実行**(`git status --porcelain`判定)。編集中は失敗する仕様 |

## 4. 残す安全上限(変更しない。原文§2・§5)

ER-011 3回上限(1ブロック=3、`PRODUCTION_MAX_TTS_ATTEMPTS`)・累積TTS15回/ASR60回(`MAX_CUMULATIVE_*`)・同一canonical_textのReview Lock(0 API block)・`approve_regenerate`/`record_human_approval`・RESTART_STORM_LOCK/RUN_LOCK/STOP・STOP_ALL/STOP_NOTICE・予算guard(`--budget-jpy`/clip前guard)・`SharedNarrationBlockedError`・Assemble前Audio Validation Gate・`CHUNKS_NOT_ALL_VALIDATED`。

## 5. Dangling Reference検査(委任_02の受入時に実行する具体的Grep)

| # | Grep(.pyは`_output/`・`.venv`除外) | 期待 |
|---|---|---|
| G-1 | `COOLDOWN_SECONDS` | 正式定義は`er127`のみ180。`er020`は`LEGACY_COOLDOWN_SECONDS`。X/Y/Z専用module(er019*/er121*/er063*/er122*/er026*)から`er020.COOLDOWN_SECONDS`参照0 |
| G-2 | `maybe_cooldown_before_attempt` | 呼出はscope外分岐内のみ。scope内leafからは`policy`経由 |
| G-3 | `max_attempts=1`(LR retts文脈) | scope内のLR経路から0件(旧helperのlegacy分岐のみ) |
| G-4 | `_local_rewrite_recovery_for_` | scope内から呼ばれない(旧3定義はlegacy分岐のみ) |
| G-5 | `600秒`・`固定600`・`10分` | コメント/docstringで正式仕様として残るものが0(履歴・Trial・A/B/C legacyの明示注記のみ許容) |
| G-6 | `KP_EXPLANATION_MAX_ATTEMPTS` | 0件(定数は`BLOCK_PROFILES`へ)または新仕様の注記つき |
| G-7 | `prior_generations`/`cooldown_total_budget`/`generations_used`(案A採用時) | 0件(案C縮退時は残置を記録) |
| G-8 | `minimal_fallback`のAdv gate記述 | Gate規則は不変のまま、③採用時にevidence(`block_evidence`)が付く |
| G-9 | CURRENT_SPEC/er011のコメントの「4回目以降は絶対にTTS生成しない」 | 「1ブロック3回。LRあり部位は最大6、KPは4」へ訂正済み |
| G-10 | scope外golden | A/B/C leaf出力のbyte同一(T-SCOPE) |
| G-11 | OPEN-376/312/536/538の状態 | 解消根拠(commit・test・evidence)を紐付けてFableが更新 |

## 6. 旧シグネチャに依存する既存ツール(残置で無影響であることの確認。Grep実測)

| ファイル:行 | 依存内容 | 扱い |
|---|---|---|
| `er094_pnmh_runtime_evidence_01.py:78-79` | `rp.maybe_cooldown_before_attempt.__defaults__`を差替えてcooldownを即時化(API 0のruntime evidence) | 旧シグネチャを温存するため無影響。scope内の新flowを即時化するevidence/test用途は`cooldown_core(clock=,sleep=)`の注入点を使う |
| `er053_family_x_open256_runtime_01.py`(`_local_rewrite_recovery_for_*`参照2件) | 旧LR helper | scope外helperを温存するため無影響。X scope内で呼ぶ場合は`lr_recover`に置換されるため、委任_02でこのtoolの再実行可否を確認 |
| `er011_tts_cooldown_observation_01.py`(7件)・`er020_tts_cooldown_local_rewrite_trial_01.py`(3件) | Trial/観測の独自`COOLDOWN_SECONDS` | Production経路から参照されない(K-02)。残置 |
| 現状baseline(委任_02開始前のGrep件数、`er*.py`直下・`_output`/`.venv`除外): `COOLDOWN_SECONDS` 26件(10ファイル)、`_local_rewrite_recovery_for_` 38件(12ファイル、うちtest 8) | — | 委任_02完了時に同じGrepで減少(正式経路の参照0)を確認 |
