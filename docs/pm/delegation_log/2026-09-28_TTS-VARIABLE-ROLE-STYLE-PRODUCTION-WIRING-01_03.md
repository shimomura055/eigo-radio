## 管理ID

TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Opus L2 所見の逐語保存のみ、委任 _03)。一時ファイル `docs/pm/RESULT_PACKET_VW1C.md`(commitしない)。並行: 別Sonnet 1件(Task 1 修正 `er045_*`/`user_test/no_heading_trial_01/`)→ 触れない。本タスクの所有: `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md`(§追記)、`docs/pm/REPORT_LEDGER.md`(当該行の Opus 列更新のみ)、delegation_log。**コード・Prompt・CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS は変更しない(所見の実装・反映はユーザー判断待ち)。API 支出 ¥0。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。**

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_03.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_03.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_03.md_check.json` を実行し結果1行記録。T-2: TTSなし。T-3: API支出なし。SSOT編集権: `docs/pm/REPORT_LEDGER.md` の当該行 Opus 列のみ(差分所有者確認: 開始時・commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` で他差分ゼロを確認)。

## 手順

1. REPORT 末尾に「## §Opus L2 レビュー所見(2026-09-28、逐語、commit `9edfdc5f` 対象)」を新設し、下記の Opus 所見を **一字一句改変せず**転記(要約・省略禁止)。冒頭に「Fable 判定: BLOCKER 0/MAJOR 3/MINOR 3。所見の反映はユーザー判断待ち(USER_DECISION_REQUIRED)。`PRODUCTION_WIRED` 未判定」と付す。
2. `docs/pm/REPORT_LEDGER.md` の `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01` 行の Opus 列を「L2 実施(BLOCKER 0/MAJOR 3/MINOR 3、所見反映はユーザー判断待ち)」に更新。Status は `APPROVED_FOR_PRODUCTION(配線完了、所見反映・Gate 3 判定待ち)` のまま。
3. commit(path指定: REPORT、REPORT_LEDGER、delegation_log+`_check.json`)、メッセージ `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01: Opus L2 レビュー所見を逐語保存(BLOCKER 0/MAJOR 3/MINOR 3、反映はユーザー判断待ち)`、trailer `Management-ID: TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`。`git push origin main`。

## Opus 所見(逐語転記対象、ここから)

# Opus L2 レビュー結果: TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(commit 9edfdc5f)

## 総合判定

**BLOCKER: 0件**。配線そのもの(後方互換・backendゲート・置換方式・shell/Master Store非影響・テスト系譜)は設計どおり実装されており、技術的な欠陥は見つからなかった。

ただし **MAJOR 3件 / MINOR 3件** があり、うち MAJOR-1(JA記事内でのstyle混在が未試聴)と MAJOR-2(変更した3 EN roleのうち2つに実文字列のruntime証拠が無い)は、Gate 3 の「actual style metadata」「安全≠成功」の観点で `PRODUCTION_WIRED` 判定の前に埋めるのが妥当。いずれも数円〜¥数円規模の追加実行か、小さなコード追加で解消できる。MAJOR-3(再利用キャッシュ)は運用ルールの明文化だけでも回避可能。

判定の可否自体はFable/ユーザーの領域であり、ここでは材料のみ提示する。

---

## 論点別の所見

### 論点1: J3による長文 `JAPANESE_STYLE_PREFIX` 置換の安全性

**(1-a) reading-safety機構のPREFIX依存 → 問題なし**
`generate_a2_japanese_with_reading_safety`(`er003_v1_n3_01_tts_generate.py:589-668`)の安全機構は**すべてtext側**の処理であり、style prefixに一切依存しない: `tts_safe_ja` / `detect_gloss_placeholder_notation` / `detect_prohibited_symbols` / `pron_resolver_core.resolve_unknown_ja_tokens` / `classify_foreign_tokens_in_japanese_text` / `to_tts_safe_japanese_fraction_reading`、および `expected_readings`(L654-657)によるASR照合。読み(かな)・記号・数字の安全性はJ3置換の影響を受けない。なお英語側だけは `resolve_and_augment_en_style_prefix`(`er003_v1_repro01_main_generate.py:291-296`)でstyle prefixへ発音ヒントを追記するが、これは「渡されたbaseに追記」する構造なのでE2でも機能する(実測 `hints_applied=false`)。

**(1-b) [MINOR] 長文PREFIXに含まれる「表情指示以外」の機能的指示が3つ失われている**
根拠(実体は `er003_b1_p3y_audio.py:66-91` + `er002_common.py:94-124`):
- `"次の文章を、翻訳・言い換えせず、日本語のまま読み上げてください。"`(言語固定+翻訳/言い換え禁止)
- `"Read every title, section heading... Never skip, paraphrase, shorten, or silently absorb..."`(原文忠実性)
- `"Treat the narration as one continuous program, even when it is generated in separate sections."`(segment横断の連続性)

J3(`er033_tts_flash_lite_family_x_styles_01.py:94-97`)にはこれらに相当する文言が無い。さらに Flash-Lite 経路では `speech_config` の `language_code` が **`common.LANGUAGE_CODE = "en-us"` 固定**(`er033_tts_flash_lite_backend_wiring_01.py:199` / `er002_common.py:55`)であり、言語固定の手掛かりが減る方向。

ただし影響は限定的と判断する。緩和要因: (i) J3自体が日本語文であること、(ii) JA全文Validator(`evaluate_attempt_ja_with_cascade`)が翻訳・言い換えを `TRUE_CONTENT_MISMATCH` として検出し retry させること、(iii) fallback(minimal instruction)経路は `"次の文章だけを、翻訳・言い換え・追加をせず…そのまま読み上げてください"`(`er003_v1_n3_01_tts_generate.py:394-397`)を保持しており安全網になっていること、(iv) 実測はTrial-02の5 segment+Phase B確認再生成の5 segmentで計10回、言語ドリフト0・`call_count=1`。

最小是正案: コード変更は不要。CURRENT_SPEC(またはOPEN-229追記)に「J3置換で失われる指示は言語固定/翻訳・言い換え禁止/忠実読み/segment連続性の3点であり、検出はJA全文Validator+minimal fallbackに依存する」と1〜2行残す(将来JA音声で言い換え事故が出たときの最初の被疑箇所になるため)。

**(1-c) [MAJOR] japanese_title だけが長文PREFIXのまま残り、同一A2記事内でstyleが混在。その状態は誰も通しで聴いていない**
根拠: `er019_family_x_audio_production_runner_01.py:764-770`(japanese_titleはoverrideを渡さない)対 `:772-780`(preview/comment_1〜4はJ3)。A2の再生順では japanese_title の直後に preview 群が来る。japanese_title は `JAPANESE_STYLE_PREFIX`(= `LEVEL2_INSTRUCTION` の「noticeably animated, emotionally present, expressive」を含む)、preview/comment は J3(「演技がかった話し方は避けてください」)。方向が逆の指示が隣接する。
加えて、Flash-Lite では style が speech_metadata へそのまま入るため、**短い日本語タイトル1文に約1,700字のinstructionを与える**構図が japanese_title にだけ残る。これは `er006_audio_cost_pilot_02_shared_narration.py:80-91` が num_two 失敗(ASR="Ту")の最有力原因として記録した「長prefix × 短文」パターンと同型である。
影響: 記事単位の聴感一貫性(= ユーザーが実際に判断する対象)が未検証。Trial-02 は segment 単体比較ページであり、組み立て音声の試聴は行われていない。
最小是正案(いずれか): (a) 既存の J3 音声(確認再生成の5件)+既存 japanese_title 音声で **A2の該当区間だけを組み立ててユーザー試聴**(新規TTS不要、¥0に近い)。(b) japanese_title へJ3を適用するか否かを USER_DECISION として明示的に挙げる(Trial範囲外なのでAgentが決めない、という今回の判断自体は正しい)。

### 論点2: 共有関数の後方互換 → 問題なし(ただし副作用1件、下記MINOR-A)

- `p9a.generate_narration_snippet`(`er003_b1_p9a_audio.py:199-234`): 引数の増減・順序変更なし。ja分岐が `style_prefix_override or JAPANESE_STYLE_PREFIX` になっただけで、既定 `None` では従来と同一文字列 → `p4c.build_tts_prompt` も同一 → byte-identical。
- `generate_a2_japanese_with_fallback`(`:473-491`)/`with_reading_safety`(`:589-600`): 新引数は**末尾にキーワード引数として追加**、既定 `None`。全呼び出し元をGrepで確認したが、`expected_substring` より後ろを位置引数で渡している呼び出し元は存在しない(er008/er009/er011/er012/er019/er022/er025 系すべてキーワード指定)。`@review_lock.guarded_generate("ja")`(`er011_human_review_lock_01.py:569-597`)は `(text, out_path, *args, **kwargs)` の透過ラッパで影響なし。
- 戻り値dictへの `"style_prefix"` 追加(`er003_b1_p9a_audio.py:293`): 戻り値dictのキー集合を厳密比較・スキーマ検証している呼び出し元・テストは見つからなかった(`assertEqual(result, {...})` 形式の該当0件)。`_generate_or_reuse` の再利用判定も `status`/`canonical_text` のみ参照(`er019...:380-387`)で無影響。

### 論点3: E2 と `A2_SLOWER_PACE_INSTRUCTION` の重畳 → 問題なし(実測1件で確認済み)

`_role_style_slower()`(`er019...:701-717`)は `f"{base}\n{A2_SLOWER_PACE_INSTRUCTION.strip()}"`。`A2_SLOWER_PACE_INSTRUCTION`(`er003_v1_n3_01_tts_generate.py:74-78`)は前後に `\n` を持つため `.strip()` で余分な改行が除去され、区切りは `\n` 1つ。文言も矛盾しない(E2「not dramatic」/ slower「smooth, conversational, and natural」)。実測でも `confirmation_regen_results.json:876` に連結後文字列が逐語で記録されている(IN_ONE_LINE)。`assert_no_wpm_specification` も連結後にかかっている。
残る未確認は Standard の **FULL_STORY×slower** のみ(下記MAJOR-2で一緒に解消可能)。

### 論点4: backendゲート → 問題なし

`_role_style_ja()`(`er019...:728-731`)のゲート条件は EN `_role_style()`(`:696-699`、B1B側は `:491-497`)と**完全に同一**(`tts_backend != "speech_metadata_flash_lite"` → `None`)。既定backendでは明示的に `style_prefix_override=None` が渡り、既定値と同一。テスト `RunnerBackendGateTests`(`er019_family_x_variable_role_style_wiring_01_test_01.py:115-155`)が両方向を固定している(japanese_titleにはNone、preview/comment_1〜4にはJ3、呼び出し回数6の固定も含む)。

### 論点5: 固定Master phrase(shell)・Key Phrase・Master Audio Store → 問題なし

- shellのstyleは `_resolve_shell_english_style_prefix_override`(`er006_audio_cost_pilot_02_shared_narration.py:95-99`)が `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` のみを参照。本タスクは **FALLBACK定数を変更していない**(`er033...:61`、テストでも固定)ため、shell の style も `SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION`(`:92`)も不変。
- Master Audio Key は shell 専用(`_make_english_key`/`_make_japanese_key`、`:102-136`)で、可変segmentはそもそも `MasterAudioKey` を生成しない(`er006_master_audio_store_01.py` 冒頭コメント)。manifest の sha256 が前後不変という実測とも整合。
- Key Phrase JA(`er019...:873`)も override 非指定。テスト `KeyPhraseRoleUnchangedTests` で固定済み。

### 論点6: [MAJOR-2] B1B EN経路の runtime evidence 欠落 — BLOCKERではないが、変更した3 roleのうち2つに実文字列証拠が無い

事実確認: `voice01.generate_charon_english` は `standard_style_prefix = style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`(`er003_v1_sing01_voice01_generate.py:152`)を `flw.resolve_tts_call_and_prompt` へ渡しており、**override は確実に効いている**。`instruction_type`(`:158` `"english_style_prefix"` / `:198` `"minimal_fallback"`)は「fallback未発火」を示すので間接証拠としては有効。したがって「E2が使われていない」リスクは低く、単独ではBLOCKERにしない。

ただし本件で本当に問題なのは、**今回の確認再生成で E2 の実文字列が JSON に残ったのは IN_ONE_LINE(A2)だけ**である点:
- JA J3: 5件で逐語一致(`confirmation_regen_results.json:24, 94, 187, 257, 327`)→ OK
- EN IN_ONE_LINE: A2で連結値が逐語一致(`:876`)→ OK
- EN **FULL_STORY**: B1Bはフィールド無し、A2の `a2_en_full_story_part1` は **STOPPED**(`:765-767`)で `style_prefix` は記録されず(p9aは `status=="OK"` の枝でしか返さない)→ **実文字列証拠ゼロ**
- EN **TOPIC_INTRO**: B1Bはフィールド無し、A2 topic_intro は今回未実行 → **実文字列証拠ゼロ**

最小是正案(推奨は(a)、¥2前後):
(a) A2 の `topic_intro` と `full_story_part2`(本文、FULL_STORY+slower)の2 segmentだけを同じ確認スクリプト方式で追加生成する。この2つは `crosslevel → repro01 → p9a` を通るので `style_prefix` が自動で記録され、TOPIC_INTRO と FULL_STORY(+slower重畳)の両方を一度に埋められる(論点3の未確認も同時に解消)。
(b) B1B側3ファイル(`er003_v1_sing01_voice01_generate.py` / `er003_v1_sing01_news_tail_fix.py` / `er003_v1_sing01_point_headings_aoede.py`)の戻り値へ同フィールドを追加。ただし共有TTS層の追加変更となり評価コストが上がるので、今回スコープ外にした判断自体は妥当。やるなら別管理IDを推奨。
なお SSOT(`CURRENT_SPEC.md:1597-1599`)は「戻り値dictへ `style_prefix` を追加、既存auditへ記録される」とだけ書いており、B1B経路が対象外である旨が落ちている。1行の限定を足すのが望ましい(MINOR)。

### 論点7: 確認再生成の1件 STOPPED → 問題なし(本配線起因ではない、runner本体Regressionは必須でない)

`confirmation_regen_results.json:773/796/820` の ASR 全文を確認した。音声は原文を忠実に読んでおり、不一致は `canonical: "Act One was “20%.”"` に対し `ASR: "Act 1 was 20%."`(fallbackでは `"Act One was 20 percent"`)という**数詞・記号の表記差**に起因する `TRUE_CONTENT_MISMATCH` で、style指示とは独立の既知事象(OPEN-201)。Sonnetの判断は妥当。
runner本体(Local Rewrite Recovery込み)でのRegressionは、本配線の妥当性検証としては必須ではないと判断する。理由: Local Rewrite は canonical text の言い換えのみで style 引数に触れず、再生成は同じ呼び出し地点(同じ `style_prefix_override`)を再実行するため、styleの観点で新情報が出ない。ただし上記(a)の追加実行は論点6のために推奨する。

### 論点8: テスト更新の正当性 → 問題なし(系譜が固定されている)

単なる期待値書き換えではない:
- `er033_tts_flash_lite_family_x_styles_01_test_01.py:48-62` … 不変3roleは **Stage3(E0)ソース**と、更新3roleは **Trial-02のE2ソース**と、それぞれ別テストで逐語照合(どちらも出所に固定)。
- `er044_..._test_01.py:38-40` … Production値 == Trial-02 E2。
- `er038_..._test_01.py:152-157` … 不変3roleは一致、更新3roleは `assertNotEqual` で「意図的な差分」を明示。
- 新規 `er019_family_x_variable_role_style_wiring_01_test_01.py:48-53` … J3/E2を er044 定数と逐語照合。
「Trial-02 → Production」の系譜が機械的に壊れないようになっている。

---

## 論点外で発見した追加所見

### [MAJOR-3] style変更が segment 再利用キャッシュを無効化しない(同一out-dir再実行でJ3/E2が効かない)

根拠: `er019_family_x_audio_production_runner_01.py:370-387` の `_generate_or_reuse` は `status=="OK"` + wav存在 + `canonical_text` 一致だけで前回runの音声を再利用する。styleは判定に含まれない。
影響: 既存out-dir(例: `hormuz__run_06_flashlite_full_kp`)に対して `--stage tts` を再実行すると、E0/長文PREFIXで生成済みのsegmentが**黙って再利用され、J3/E2は適用されない**。一部segmentだけ再生成された場合、1記事内でE0音声とE2音声が混在しうるが、audit上その区別が付かない(古いentryには `style_prefix` フィールド自体が無い)。
これは本プロジェクトが既に踏んだ罠と同型で、`er006_audio_cost_pilot_02_shared_narration.py:103-110`(Opus所見BL-1)が「style変更時は `style_instruction_version` を bump しないと古いmasterが黙ってcache hitし続ける」として明文化している。可変segmentはMaster Store対象外だが、runner自前のキャッシュが同じ性質を持つ。
最小是正案(er019内で閉じる、共有層に触れない):
```
FAMILY_X_VARIABLE_ROLE_STYLE_VERSION = "v2_j3_e2"   # 新設
```
を `tts_generation_results.json` のトップレベルへ保存し、`_load_cached_tts_results` で読んだcacheのversionが不一致/欠落なら可変segment(topic_intro/preview/comment/full_story/in_one_line)の再利用を行わない。
コードを変えない場合の代替: 「J3/E2は新規out-dirでのみ有効。既存out-dirを再利用した場合はstyleが混在しうる」という運用制約をCURRENT_SPECへ明記する。
(補足: Review Lock の `check_before_generation` も out_path+text キーでstyle非依存のため、旧styleでLockされたsegmentは新styleでも試行されない。こちらは安全側なので是正不要。)

### [MINOR-A] `style_prefix` 全文記録により、全Familyのaudit JSONが1 segmentあたり約2KB肥大する

根拠: `er003_b1_p9a_audio.py:293` は `style_prefix` を**無加工で**返し、`er003_v1_repro01_main_generate.py:425` の `return {**r, ...}` 経由で各runnerの `tts_generation_results.json` にそのまま保存される。既定backendでは `ENGLISH_STYLE_PREFIX` / `JAPANESE_STYLE_PREFIX`(約1,700〜2,000字)が入るため、Family A/B/C を含む**全記事・全segment**のauditに長文instructionが複製される(A2 1レベルで概算40KB強)。同じ懸念に対し同一サブシステムは既に `er033_tts_flash_lite_backend_wiring_01.py:281-288`(N-4是正)で「telemetryへは先頭200文字にtruncate」という前例を作っており、今回の無加工記録はその方針と非対称。
最小是正案: override指定時のみ実値を記録し、既定時は短いラベルにする。
```python
"style_prefix": style_prefix if style_prefix_override else "<default:ENGLISH_STYLE_PREFIX>",  # ja分岐は JAPANESE_STYLE_PREFIX
```
これでFamily X role style(J3=72字、E2≤95字、A2連結≈280字)の証拠価値は完全に保たれ、legacy経路の肥大はゼロになる。単純な200字truncateだとA2連結値(280字)が切れるので非推奨。

### [MINOR-B] 確認再生成はrunnerの配線を通っていない(styleを手書きした複製経路)

`er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py:120-207` は `_role_style_ja()`/`_role_style_slower()` を呼ばず、`fl_styles.FAMILY_X_ROLE_STYLE_JA` 等を直接渡している。したがって「下位関数がstyleを尊重すること」の実測証拠ではあるが、「runnerがそのstyleを選ぶこと」の実測証拠ではない(後者はmockテストのみ)。runnerのCLIがsegment単位実行を持たない以上この代替は妥当だが、REPORT/SSOTには「runner配線=単体テスト、style反映=実測」の2段構成であることを1行明記するのが正確。

### [MINOR-C] SSOTのruntime evidence記述が実態より広い

`CURRENT_SPEC.md:1597-1599` は `style_prefix` が「既存auditへ記録される」とだけ書いており、B1B(Advanced)EN経路が対象外であること・確認再生成13件中1件がSTOPPEDであることが落ちている。REPORT §7-1/§4には書かれているので、SSOT側に1行の限定を足せば足りる。

## Opus 所見(ここまで)

## 報告(handback、目安10行)

転記先の行範囲/REPORT_LEDGER 更新内容/T-0 結果/差分所有者確認/commit hash・push・raw URL/禁止操作未実施。
