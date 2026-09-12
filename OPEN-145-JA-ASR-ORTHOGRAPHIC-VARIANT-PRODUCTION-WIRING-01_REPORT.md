# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01

## 要点(5行)
1. ユーザー正式決定(2026-09-12、`APPROVED_FOR_PRODUCTION`)に基づき、
   JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01(`VALIDATED`)の
   Candidate B/C/D-1/D-2を新規Production module
   [er011_ja_asr_variant_layer_01.py](er011_ja_asr_variant_layer_01.py)へ
   移設し、`er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`へ
   追加型(additive)で配線した。既存のpykakasi判定・Cascade・数字/否定
   保護・entity_like判定は無変更。feature flag
   `FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`(既定True)。
2. Trial fixture(自作82件+実データ161件)をProduction関数経由で再評価し、
   Trialの結果(82/82、実データ過去MISMATCH5/7解消、過去PASS72件で真の
   regression0件)と完全に一致することを実測確認した(flag OFFは配線前と
   完全一致)。既存er007/er011 fixture・project-wide regression
   (collected=2346、failed=3=既知の無関係failureのみ)も全PASS。
3. タオルTrial-11 A2 `comment_2`(Human Review Lock中)の既存6 take(既存
   ASR書き起こしのoffline再判定、新規ASR/TTS呼び出しなし)を配線後の
   Validatorで再判定し、既に採用済みの音声がPHONETIC_MATCHでPASS。
   `review_lock_state.json`をRESOLVED、`tts_generation_results.json`を
   同期した(バックアップ保存済み)。あわせて別件のpre-existing同期漏れ
   (`meaning_4`)も是正した。
4. comment_2解決後、A2 Assembly(Audio Validation Gate込み)を実行し
   **PASS**(duration=325.109秒、peak=0.95、clipping無し)。新規NGは0件。
   B1B側は別タスクが処理中のため一切触れていない(read-onlyでも確認済み)。
5. `PRODUCTION_WIRED`は宣言しない(Gate 3のうちDECISION_LOG.md/
   OPEN_ITEMS.md反映・Git commitはFable統合工程で完了予定)。本作業の
   API支出は¥0(offline再判定・CPU計算のみ)。

---

## 1. 差分

| ファイル | 種別 | 内容 |
|---|---|---|
| `er011_ja_asr_variant_layer_01.py` | 新規(Production module) | Candidate B(形態素解析ベース読み一致、fugashi+unidic-lite)/C(カタカナ語末長音符・助数詞ヶ月表記正規化)/D-1(漢数字位取り一般正規化)/D-2(voicing許容Cascade厳密一致引き上げ)を統合。Trial専用ファイルからは一切import しない(ロジックは移設・統合済み)。`FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`(既定True)、fugashi/unidic-lite import失敗時は自動的にFalseへ落としwarnings.warn |
| `er007_ja_asr_validator_01.py` | 追加(36行) | `classify_ja_asr_match()`内2箇所へ`try_rescue_before_resolver()`呼び出しを追加: (a)既存Resolver呼び出し直前、(b)数字のみの不一致(否定不一致を伴わない)による`protected.passed=False`早期returnの直前(Candidate D-1の漢数字位取りケースがここで早期returnされるため追加が必要と判明、詳細は§3参照) |
| `er007_ja_secondary_asr_01.py` | 追加(26行) | A2 Cascade呼び出し元(`evaluate_attempt_ja_with_cascade_detail`)のPrimary#1/#2・Secondary#1/#2の4箇所全てで、`classify_ja_asr_match()`直後に`_apply_variant_layer_voicing_upgrade()`(内部で`ja_variant_layer.try_upgrade_voicing_cascade()`を呼ぶ)を適用(Candidate D-2) |
| `CURRENT_SPEC.md` | 追記1行(表1行) | 「JA ASR表記ゆれ一般化Variant Layer(OPEN-145)」行を「A2 Reading Resolver(OPEN-111)」行の直後へ追加。他節は無変更 |
| `er011_open145_ja_asr_variant_production_wiring_01_run.py` | 新規(evidence) | Trial fixture(82件+161件)をProduction関数経由でflag ON/OFF両方評価する回帰スクリプト |
| `er011_open145_ja_asr_variant_production_wiring_01_regression_run.py` | 新規(evidence) | 既存er007/er011 fixtureをProduction関数経由で再確認する回帰スクリプト(call_resolverをブロックしAPI支出0を保証) |
| `er011_open145_towels_trial11_comment2_meaning4_resync_01.py` | 新規(runtime evidence) | タオルTrial-11 A2 `comment_2`/`meaning_4`のreview_lock_state.json/tts_generation_results.json同期スクリプト(バックアップ付き) |
| `er011_open145_towels_trial11_a2_player_01.py` | 新規(runtime evidence) | A2完成episodeの試聴player.html生成(標準フォーマット、read-only) |
| `er011_output/discovery_generalization_towels_trial_11/a2/**` | 実行結果(新規/更新) | `review_lock_state.json`(comment_2→RESOLVED)、`tts_generation_results.json`(comment_2→OK、meaning_4→OK同期)、`assembled/`(最終wav+player.html)、`audit/{gain_report,timeline,headroom_report}.json`、`run_summary_assemble.json`、`assembly_and_gate_summary_audio_01.json`(PASSへ更新) |
| Trial-onlyファイル(`er011_ja_asr_variant_trial_01*.py`) | 無変更 | 過去の証跡・再現用としてそのまま残す |
| `er011_output/discovery_generalization_towels_trial_11/b1b/**` | **本タスクでは一切変更していない** | 別タスク(B1B側)が並行して処理中のため、read-onlyでも書き込みを行っていない。git statusにこの配下の変更が見えるのは別タスクによるもの |

## 2. 配線図(呼び出し順序)

```
A2 TTS生成(generate_a2_japanese_with_reading_safety)
  -> ja_secondary.evaluate_attempt_ja_with_cascade()
       -> evaluate_attempt_ja_with_cascade_detail()
            [Primary#1] cls = javal.classify_ja_asr_match(canonical, primary_asr_text)
                 |  内部: 数字/否定保護 -> (数字のみ不一致ならCandidate B/C/D-1試行) -> entity_like/
                 |         phonetic_uncertain判定 -> whole_text読み一致 ->
                 |         (Resolver呼び出し直前でCandidate B/C/D-1試行、ここが主insertion point)
                 |         -> Reading Resolver(LLM) -> TRUE_CONTENT_MISMATCH
                 v
            cls = _apply_variant_layer_voicing_upgrade(canonical, primary_asr_text, cls)  [Candidate D-2]
                 (cls.classification=="ASR_VALIDATION_UNCERTAIN"かつphonetic_uncertainのみの場合に限り、
                  形態素解析ベース厳密一致でPHONETIC_MATCHへ引き上げ。それ以外は無変更)
            should_pass=True なら即return(Cascade不要)
            それ以外は既存どおりPrimary#2/Secondary#1/Secondary#2へ進む(各ステップも同じ
            classify_ja_asr_match() -> _apply_variant_layer_voicing_upgrade()の順)
            4 step全て不一致 -> 既存どおりHuman Review Lock(無変更)
```

既存のpykakasiベース判定・数字/否定保護・entity_like判定・Cascade
(Primary#2/Secondary#1/#2の順序・予算)・Human Review Lockへの遷移条件は
一切変更していない。この層が介入するのは「既存判定がまだ確定していない
(TRUE_CONTENT_MISMATCHのうち数字のみ不一致のケース、またはResolver呼び
出し直前で非cascade diffが残っているケース)」、または「既存の
voicing許容Cascade(ASR_VALIDATION_UNCERTAIN、根拠がphonetic_uncertainの
みでentity_likeを含まない)」の場合のみ。

## 3. 実装中に発見した設計上の補正(Trial REPORT配線案からの差分、報告)

Trial REPORT修正2回目の配線案は「Resolver呼び出し直前の1箇所」への
挿入のみを想定していたが、実装・テストの過程で以下を発見し、承認された
設計思想(追加型、既存判定への非干渉)の範囲内で補正した:

- **発見**: Candidate D-1(漢数字の位取り一般正規化、「十件/10件」等)が
  対象とするケースは、`protected_check_ja()`の数字不一致チェックにより
  `classify_ja_asr_match()`の**Resolver呼び出しよりずっと手前**
  (`if not protected.passed:`)で早期TRUE_CONTENT_MISMATCH returnされて
  しまい、Resolver直前のinsertion pointへ到達しないことが実測で判明した
  (「十」等の位取り漢数字は既存の単独1桁変換[一〜九]の対象外で、ASR側の
  算用数字と数字個数が食い違うため)。
- **対応**: 同じ`try_rescue_before_resolver()`関数を、この早期return
  直前にも追加で呼ぶようにした。**否定の不一致が同時に発生していない、
  かつ数字の不一致がある場合に限定**(`protected.number_mismatches and
  not protected.negation_mismatches`)。安全性の論拠:
  Candidate B/C/D-1のいずれの判定も「正規化後の文字列完全一致」または
  「形態素解析ベースの読み完全一致」という厳密な等価性判定であり、
  数量そのものが異なる場合(例:「十五件」と「50件」)は構造的に一致
  しない(Trial実測でも誤PASS0件、本タスクでも161件全件で再確認)。
- 本タスクのテスト(§4)は、この2箇所構成での実装を対象に実施した
  (「1箇所」という初期の配線案の字面ではなく、Trial REPORTが実測で
  検証した「Candidate B/C/D-1が既存判定のTRUE_CONTENT_MISMATCH全経路に
  対して働く」という設計意図・安全性根拠に忠実な実装)。

## 4. テスト結果

### 4-1. Trial fixture再評価(Production関数経由、`er011_open145_ja_asr_variant_production_wiring_01_run.py`)

| 観点 | flag OFF(旧挙動) | flag ON(配線後) | Trial rev2実測値 |
|---|---|---|---|
| 自作82件 correct | 69/82 | **82/82** | 82/82 |
| 自作82件 false_pass(誤PASS) | 0 | **0** | 0 |
| 実データ過去MISMATCH(7件)解消 | 0/7 | **5/7** | 5/7 |
| 実データ過去PASS(72件)維持 | 68/72 | **70/72**(0件が真のregression、改善のみ) | 72/72(定義補正後) |

flag OFFの結果は配線前の挙動そのもの(独立に検証済み)と一致する。
flag ONへ切り替えた際の全13件の変化(82件セット)はいずれも
`should_pass: False -> True`の一方向のみ(逆方向の変化=0件、regression
無し)を実測確認した。証跡:
`er011_output/open145_ja_asr_variant_production_wiring_01/production_wiring_synthetic_historical_result.json`

### 4-2. 既存回帰(`er011_open145_ja_asr_variant_production_wiring_01_regression_run.py`)

- `er007_ja_asr_validator_01_test.py`: POSITIVE 10/10、NEGATIVE 15/15、
  ENTITY_LIKE 1/1、PHONETIC_UNCERTAIN 2/2、WHOLE_TEXT_SCRIPT_MISMATCH
  3/3、WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE 2/2、KNOWN_TRADEOFF 1/1、全PASS
  (`READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES`[月/つき]1件は実際の
  LLM呼び出しが必須なためAPI支出禁止の本タスクではskip、Trial時と同じ扱い)。
- `er011_no18_connected_speech_reading_resolver_wiring_08_test.py`関連
  (#10完全一致、#14真の内容誤り、#15/#15b importチェック): 全PASS。
- `call_resolver`はテスト全体を通じて0回呼び出し(呼ばれたら即
  RuntimeErrorになるブロック用stubで検知、実測0回)。
- 証跡:
  `er011_output/open145_ja_asr_variant_production_wiring_01/existing_er007_er011_offline_regression_after_wiring.json`

### 4-3. project-wide regression(`run_project_regression.py`)

- 配線前(baseline): collected=2322, passed=2319, failed=3, errors=0
  (`er011_output/open145_ja_asr_variant_production_wiring_01_baseline_summary.json`)。
- 配線後: collected=2346, passed=2343, failed=3, errors=0
  (`er011_output/open145_ja_asr_variant_production_wiring_01/post_wiring_project_regression_summary.json`、
  collected数の差分[2322→2346]は本タスクと無関係な他タスクの並行作業に
  よるテスト追加、本タスクの新規failureは0)。
- failした3件を実名で確認(前後とも同一): `er003_test_bad.FixtureTests.
  test_case_0`(意図的な既知fixture)、
  `er003_test_p2j_investigate.CollectionCountTests.
  test_combined_equals_sum_of_er002_and_er003`、
  `er003_test_p2j_investigate.ReconciliationArithmeticTests.
  test_p2h_reported_count_matches_er002_plus_er003_at_that_time`。
  いずれもテスト件数の歴史的整合性に関する既知の無関係failureで、
  JA ASR/日本語segmentとは無関係(過去のCURRENT_SPEC記載の「既知3件
  failure」と同一カテゴリ)。
- **A2/B1/2V/3V既存テスト(日本語segmentを含む`er003_test_v1_n3_01_tts_
  generate.py`、`er012_editorial_b_family_voices_3v_production_wiring_
  phase1_test_01.py`等)を含め、本タスク起因の新規failureは0件**。

### 4-4. flag OFF時の旧挙動同一性 / import失敗時fail-safe

- flag OFF: §4-1のとおり配線前と完全一致(82件セット・historical
  セット双方で実測)。
- fugashi importを`builtins.__import__`差し替えで意図的に失敗させ、
  `er011_ja_asr_variant_layer_01`をimportし直したところ、
  `FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`が自動的に`False`へ変わり
  `RuntimeWarning`が発火すること、その状態で`classify_ja_asr_match()`が
  旧挙動どおり動作すること(「経つ/たつ」がrescueされずTRUE_CONTENT_
  MISMATCHのまま)を実測確認した。

## 5. Runtime evidence

### 5-1. タオルTrial-11 A2 `comment_2`のoffline再判定(Production経路)

`er011_open145_towels_trial11_comment2_meaning4_resync_01.py`で、既存6
take(canonical: 「洗濯して乾かしても、においが残ることがあります。では、
タオルの中には、時間がたつと何が残るのでしょうか。」)の既存ASR書き起こし
(新規ASR呼び出しなし)を、配線後の`javal.classify_ja_asr_match()`で
再判定した。

| take | 由来 | 再判定結果 | 現在の`comment_2.wav`と同一か |
|---|---|---|---|
| attempt1(standard) | tts_generation_results.json | PHONETIC_MATCH(Candidate B) | No |
| attempt2(standard) | tts_generation_results.json | PHONETIC_MATCH(Candidate B) | No |
| attempt3(minimal fallback) | tts_generation_results.json | **EXACT_MATCH** | No |
| attempt4(standard、resume) | review_lock_state.json | PHONETIC_MATCH(Candidate B) | No |
| attempt5(standard、resume) | review_lock_state.json | PHONETIC_MATCH(Candidate B) | No |
| attempt6(minimal fallback、resume) | narration/attempts(未反映分) | **PHONETIC_MATCH(Candidate B)** | **Yes(sha256一致)** |

既存採用規則(現在narration/comment_2.wavとして実在するファイル=
attempt6)がPASSしたため、**このファイルをそのまま採用**した(TTS再生成
なし、新しいtakeへの差し替えなし)。`review_lock_state.json`の
`comment_2`を`HUMAN_REVIEW_REQUIRED`→`RESOLVED`(`final_status: OK`)、
`tts_generation_results.json`の`segments.comment_2`を`STOPPED`→`OK`へ
更新し、6 take全ての再判定結果を`open145_reclassification`フィールドへ
記録した(透明性のため、単一attemptのOK schemaへ丸めず再判定という事実を
明示)。

**別件の発見(pre-existing sync gap、本タスクのVariant Layerとは無関係)**:
`meaning_4`(Key Phrase 4 japanese_meaning)は`review_lock_state.json`では
既に`RESOLVED`/`OK`(attempt4、`EXACT_MATCH`、旧pykakasi判定のみで解決
済み)だったが、`tts_generation_results.json`側の
`key_phrases["4"].japanese_meaning`だけが古い`STOPPED`のまま未同期
だった。ユーザー指示「meaning_4分も同時」に従い、
`review_lock_state.json`の実際の解決済みattemptを正として同期した
(TTS再生成・新規ASR呼び出しなし)。

両JSONファイルは変更前に`*.backup_before_open145_resync_20260912_113837.json`
としてバックアップ済み。証跡:
`er011_output/open145_ja_asr_variant_production_wiring_01/comment2_meaning4_resync_evidence.json`

**この再判定はoffline(既存ASR書き起こしの再利用)である点を明記する。
実TTS/実ASR run(新規生成)での本層の実発火は、次回このtheme(または
他theme)でA2音声を新規生成した際に確認されることになる。**

### 5-2. A2 Assembly(comment_2解決後)

`er011_discovery_generalization_towels_trial_11_audio_run.py`の既存関数
`assembly_stage("a2")`(無変更、A2のみ呼び出し、B1Bには一切触れない)を
実行した。

- Gate OFF経路(`asm.stage_assemble_a2`): **PASS**
  (status=OK、duration=325.109秒、peak=0.95、clipping無し、headroom
  safety valve未発動)。
- Gate opt-in ON経路(`asm.verify_episode_audio_validation_gate`、
  structural completeness含む): **PASS**。
- 新規NGは0件(retryは発生していない、既存音声の再判定のみで完結)。
- 出力: `er011_output/discovery_generalization_towels_trial_11/a2/assembled/
  English_Your_Way_A2_DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11.wav`
- player.html:
  `er011_output/discovery_generalization_towels_trial_11/a2/assembled/player.html`
  (`file:///C:/Users/tensh/eigo-radio/er011_output/discovery_generalization_towels_trial_11/a2/assembled/player.html`)
- B1B側(`er011_output/.../b1b/**`)は本タスクでは一切変更していない
  (別タスクが並行処理中のため)。

## 6. コスト影響評価

`er011_output/ja_asr_variant_trial_01/`の161件データセット全体を、
Reading Resolverをdry-run stub(呼び出し回数のみ計測、実API呼び出し
無し)にしてflag OFF/ON双方で実行した。

| 指標 | flag OFF(旧挙動) | flag ON(配線後) |
|---|---|---|
| Resolver呼び出し(would-be LLM call)回数、161件中 | 24回 | **14回(-42%)** |
| 平均処理時間/件 | 約3.18ms | 約3.96ms(+約0.8ms、CPU計算のみ、追加API呼び出しなし) |

Reading Resolver到達件数の削減は、その分のLLM API呼び出し(¥/回)と
待ち時間を恒常的に削減する方向に働く(本タスクでは実際のLLM呼び出しを
一切行っていないため、¥での節約額はここでは算出せず「到達件数」の
削減率のみを実測値として報告する)。追加処理時間(+0.8ms/件)は
CPU上のオフライン形態素解析のみであり、ネットワーク呼び出し・追加API
課金は発生しない。

## 7. Gate 3チェックリスト個別判定(PM_GOVERNANCE.md L146-152)

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Production正式初回経路 | **済** | `er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`(A2 TTS生成が実際に使うProduction正式関数)へ直接配線。並行のDEV/Trial経路は作っていない |
| 2 | retry・fallback・regenerationとの整合 | **済** | 既存のCascade予算(Primary#1/#2・Secondary#1/#2、`CASCADE_CONFIG_JA`)・TTS retry予算(`PRODUCTION_MAX_TTS_ATTEMPTS`等)は無変更。新規retryループ・新規上限は追加していない(§2配線図参照) |
| 3 | DEV・Trial-onlyでないこと | **済** | 新規moduleはProduction module。Trial専用ファイル(`er011_ja_asr_variant_trial_01*.py`)からのimportが無いことをgrepで確認済み |
| 4 | Production runtimeでの実発火 | **部分済(初回証跡)** | §5-1のとおり実データ(過去の実TTS/実ASR出力)をoffline再判定し、実際に`review_lock_state.json`/`tts_generation_results.json`の状態を変更、A2 Assembly実行までPASSさせた。ただし新規TTS/ASR呼び出しを伴う「今回初めて発火した」ケースではない。実TTS run経由の発火は次回A2生成時に確認予定 |
| 5 | 必要testのPASS | **済** | §4のTrial fixture再評価・既存er007/er011回帰・project-wide regression、全PASS(新規failure0件) |
| 6 | runtime evidence | **済(初回証跡)** | §5-1/5-2(#4と同じ証跡) |
| 7 | 実際のmodel_id・routing確認 | **該当なし(N/A)** | 本層はLLM呼び出しを増やさない(むしろReading Resolver到達件数を削減する)。新規model routingの追加は無い |
| 8 | コスト影響評価 | **済** | §6(Resolver到達件数-42%、処理時間+0.8ms/件、追加API課金無し) |
| 9 | `CURRENT_SPEC.md` | **済** | §1のとおり該当節へ追記済み |
| 10 | `DECISION_LOG.md` | **未(Fable統合で完了予定)** | 本タスクの禁止事項によりSonnetでは編集していない |
| 11 | `OPEN_ITEMS.md` | **未(Fable統合で完了予定)** | 同上 |
| 12 | 必要なGit反映 | **未(Fable統合で完了予定)** | 本タスクではGit操作を行っていない(禁止事項) |
| 13 | approved specとProduction挙動の一致 | **済** | Trial REPORT「修正2回目」の候補B+C+D-1+D-2構成と実装が一致し、テスト結果(82/82、5/7、72件中regression0)がTrial実測値と一致することを確認(§4-1)。§3の2箇所配線への補正は、承認済み設計思想[追加型・既存判定への非干渉]の範囲内での実装上の補正であり、報告済み |

(PM_GOVERNANCE.md L146-152の記載を「/」区切りで数えると本表は13項目
となった。タスク指示の「14項目」との差異は数え方の違いと考えられるが、
記載されている評価軸は全て網羅している)

## 8. Trial-11の1記事総コスト更新(5区分)

本タスク(offline再判定・記録同期・A2 Assembly・player生成)による新規
API呼び出しは0件(ASR/TTS/LLM呼び出しいずれも無し)。**本作業費用: ¥0**。

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| ①今回実測(訂正後、実際の実行経路=Batch API) | **180.55**(不変) | text-gen 117.72 + audio(訂正後)62.83 + 本作業¥0 |
| ②今回実測(未訂正、公式script報告値) | 130.48(不変) | 参照時は過小 |
| ③量産想定(Batch適用時の1記事見込み) | 180.55(不変) | ①と同値 |
| ④retry/Human Review由来の上振れ分(内数) | 16.00(不変) | 本作業はoffline再判定+Assembly+player生成のみでTTS/ASR/LLM呼び出しが無いため上振れなし |
| ⑤(参考、机上換算)Standard同期TTSで実行した場合 | 約230.6(不変) | 未実行の理論値 |

参考(別タスクの既支出、本表には含まれず開示のみ):
`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01`
のAzure Secondary ASR診断呼び出し実費用約¥1.81を含めた真の累計は
約¥182.36(前回`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01_REPORT.md`
と同じ開示、本タスクでの変更なし)。

## 9. 禁止事項の遵守確認

- `docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`: 触れていない。
- `OPEN_ITEMS.md`/`DECISION_LOG.md`: 編集していない。
- Git操作: 行っていない(`CURRENT_SPEC.md`の仕様追記のみ実施、指示どおり)。
- 閾値・判定意味の変更、個別語テーブル、Production retry仕様変更:
  行っていない(既存の閉じた助数詞リスト・既存Cascade設計をそのまま
  読み取り専用で再利用)。
- TTS再生成: 行っていない(既存音声の再判定のみ)。
- B1B側ファイルの編集: 行っていない。
- `PRODUCTION_WIRED`宣言: していない。
- API支出(LLM/TTS): 発生していない(全てdry-run stub/offline再判定/
  CPU計算のみ)。
- `git stash`/`git clean`: 使用していない。

## 参照

- Trial: `JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01_REPORT.md`
- Production module: `er011_ja_asr_variant_layer_01.py`
- 配線差分: `er007_ja_asr_validator_01.py`, `er007_ja_secondary_asr_01.py`
- 評価スクリプト: `er011_open145_ja_asr_variant_production_wiring_01_run.py`,
  `er011_open145_ja_asr_variant_production_wiring_01_regression_run.py`
- Runtime evidence スクリプト:
  `er011_open145_towels_trial11_comment2_meaning4_resync_01.py`,
  `er011_open145_towels_trial11_a2_player_01.py`
- 証跡ディレクトリ: `er011_output/open145_ja_asr_variant_production_wiring_01/`
- CURRENT_SPEC.md: 「JA ASR表記ゆれ一般化Variant Layer(OPEN-145)」行
