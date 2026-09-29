## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Opus L2 所見の逐語保存、F-1、委任 _07)。**保存のみ。是正実装・コード変更・SSOT 編集は禁止**(ユーザー判断待ち)。一時ファイル `docs/pm/ACTIVE_TASK_RF7.md` / `docs/pm/RESULT_PACKET_RF7.md`(commitしない)。並行 Agent なし。`git pull --ff-only origin main` で最新化。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物。push 競合時は `git merge origin/main` のみ。費用 ¥0。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_07.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_07.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_07.md_check.json` を実行し結果1行記録。T-2/T-3: API 支出なし。

## 作業

1. `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` の末尾に新節 `## Opus L2 設計レビュー所見(2026-09-29、逐語保存、反映はユーザー判断待ち)` を追加し、以下の「=== OPUS 所見 ここから ===」〜「=== ここまで ===」の間を**一字一句変更せず**(見出しレベルは節内に収めるため `#` を 2 段下げてよい。それ以外の改変禁止)貼り付ける。冒頭に「Status: 所見受領・未反映。BLOCKER 1 / MAJOR 4 / MINOR 9。E2E 発火可否・是正の実施はユーザー判断(PM_GOVERNANCE 11 節、Opus 後の Sonnet 自動再実行禁止)」の 1 行を付す。
2. `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §9 末尾に「Opus L2 実施済み(1 回、所見は REPORT 参照)、Status: USER_DECISION_REQUIRED(E2E 発火前是正の要否)」を 3 行以内で追記。
3. path 指定 add(REPORT・設計書・delegation_log+`_check.json` のみ)、メッセージ `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: Opus L2 レビュー所見を逐語保存(BLOCKER 1/MAJOR 4/MINOR 9、是正実施はユーザー判断待ち)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、push。
4. 報告(10 行以内): 保存位置(行範囲)、逐語性確認(貼付前後の文字数一致)、commit hash・raw URL。

=== OPUS 所見 ここから ===
# Opus L2 設計レビュー: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W1〜W4)

read-only。コード・SSOT・一時ファイルの編集なし、テスト/TTS/ASR実行なし、¥0。

## 1. 総括

**推奨: 是正後発火(BLOCKER 1件 + MAJOR 4件。いずれも小さくmock検証可能、追加費用¥0)**

W1〜W4の中核主張は実機コードで裏が取れました。特に以下は「問題なし」と確認済みです。

- **KP 先頭=末尾の同一性(W4の最重要論点)は構造的に保証されている**。共有 `er003_b1_p9a_audio.py:440-445 build_key_phrase_block()` が `english_component_samples` という同一in-memory配列を先頭と末尾の両方へ連結しており、`er003_v1_n3_01_assemble.py:665-674 build_b1_key_phrase_blocks()` / `:863-874 build_a2_key_phrase_blocks()` の両方がこれを呼ぶ。Assembly段で wav を1回読んで2回使うだけなので、retry / fallback / cache hit / Master reuse / 解説STOPPED のどの経路でも先頭と末尾が食い違う余地がない。W4が追加した `phrase_repeat`(`er019_family_x_audio_production_runner_01.py:744-746`、`dict(en_r)` の複製)は監査記録上の明示であり、TTS call を増やさない。Standard 無変更も妥当。
- **v2 split の二重実装drift(W1論点2)は無い**。`er019_family_x_audio_plan_01.py:147-153` は `sc.split_family_x_article_text_v2()` への薄いwrapperで、実装は `er003_v1_n3_01_scaffold_generate.py:185-243` の1箇所のみ。Writer段(`er012_e_..._runner_01.py:302,308,398,492`)とAudio段(runner `:210,322`)は同一関数を同一text(article.md)に適用する決定論処理なので一致する。
- **A2 Prompt の差分は機械置換のみ(W1論点1)**。`er003_v1_n3_01_standard_a2_generate.py:510-532` を `:147-169` (V5) と逐語比較した結果、差分は (a) 構造保持行の `the two "### " sections,` 削除、(b) `STANDARD_A2_SECTION_PRESERVE_SENTENCE` → `FAMILY_X_STANDARD_A2_NO_HEADING_PRESERVE_SENTENCE` の2箇所のみ。`STANDARD_A2_NEW_VOCAB_BLOCK` を含むA2簡略化ルール本文は1文字も変わっていない。ARM3(「may reorder, merge, or reshape paragraphs」)との矛盾も**無い**——新経路のStandard入力は `generate_advanced_adaptation()` ではなく忠実英訳(`:526-553` で「same number of paragraphs / Do not merge, split, or reorder」を明示)であり、旧Advanced adaptationは呼ばれない(`er012_e_..._runner_01.py:351,451`)。
- **段落数retryのStandard/Advanced対称性**は単一ヘルパー `_family_x_ensure_split_or_paragraph_retry()`(`er012_e_..._runner_01.py:293-315`)を2箇所(`:365-366`, `:461-462`)から同一に呼んでおり対称。Deviation must-fix後の再チェックも両側対称(`:398-404` / `:492-498`)。
- **W2の他Family波及は実質的に無い**(ただし報告の根拠は誤り。下記 MINOR N-8b)。`_make_english_key`/`_make_japanese_key` は `tts_backend != "speech_metadata_flash_lite"` なら version を `"v1"` に固定する(`er006_audio_cost_pilot_02_shared_narration.py:181-186, 210-211`)。flash_lite を渡す呼び出し元は Family X runner のみ(grep確認)なので、Family A/B/Cの固定shell音声は不変。
- **Model Routing Contract追加は additive かつ fail-closed**(`er006_model_routing_contract_01.py:109`、`require_model` は未知processを例外化 `:124-126`)。共有Contractへの1行追加として妥当。

## 2. 所見一覧

### BLOCKER-1: KP英語解説の QA NG が Gate も STOP も Human Review も通らず音声化・episode採用される(W4論点3)

- **根拠**: `er019_family_x_kp_explanation_01.py:283-298` — QA NG は retry 1回後 `NG_ACCEPTED_AFTER_RETRY` として**そのまま採用**。さらに (a) 初回で parse 失敗して retry を使い切った場合は QA retry が一切行われず status は `"NG"` のまま(`:287` の `and not retried_for_parse`)、(b) `NG_PHRASE_MISMATCH` 時は `english_explanation=None`(`:275-276`)。runner 側は `er019_family_x_audio_production_runner_01.py:726` で `explanation_text = explanation_row.get("english_explanation") or ""` として**空文字のままTTSへ渡し**、`:734-736` で status を記録するだけで分岐しない。
- **影響**: QA NG の内容は「語数15超」または「**phrase/source_sentence に無い固有名詞・数値の混入(=新規Fact)**」(`:143-158`)。この解説音声は Verified Fact Ledger の deviation check を一度も通らない新規英語コンテンツであり、NGを無視するのは他工程の扱い(deviation MAJOR→retry1回→なおMAJORならSTOP、`er012_e_..._runner_01.py:413-422`)および「安全≠成功」原則と非整合。空文字TTSは最終的に STOPPED→Audio Validation Gate で落ちる見込みだが、fail-closed の位置が遅く、無駄な課金と不明瞭な失敗になる。
- **最小是正案**(どちらか): (1) コード修正=text-gate status が OK 以外の rank は TTS を呼ばず、`kp_results[rank]["explanation"]` に `status="STOPPED"` + reason を記録する(既存 `verify_episode_audio_validation_gate` が `kp{rank}_explanation=STOPPED` で assembly をblockし、既存 `record_human_approval()` 経路で人間承認も可能)。(2) コードを触らないなら、E2E手順に**必須Gate**として「assembly実行前に `audit/tts_generation_results.json` の全 rank で `explanation_status_from_text_gate == "OK"` を確認、1件でも違えばSTOPしてユーザー判断」を明文化する。
- **E2E前に必要**: **はい**(1か2のいずれか)。

### MAJOR-1: KP解説音声の cache が text guard も style_version guard も持たず、再runで text と音声が食い違う

- **根拠**: `er019_family_x_audio_production_runner_01.py:421-428 _generate_or_reuse_kp()` は status=="OK" + ファイル存在のみで reuse し、`expected_text` 相当の比較をしない(W3で可変segmentに入れた `:409-414` のガードが KP には意図的に非適用)。解説textは LLM 生成なので**phrase が1件変わると5件まとめて再生成**(`:684-696`)され、変わっていない rank の解説文も文面が変わり得る。その一方で音声は旧wavが reuse され、`:734` で `expl_r["explanation_text"] = explanation_text`(新text)に上書きされる。`_segment_asset_hash_stale()`(`er003_v1_n3_01_assemble.py:207-217`)は「記録sha256 vs 実ファイル」しか見ないため検知不能で、player 表示(`runner:1531-1536`)も新textを表示する。
- 併せて W3論点4の答え: `style_version` 不一致時に explanation は**再生成されない**(`_generate_or_reuse_kp` はこの値を見ない)。KEY_PHRASE_EXPLANATION_EN は Family X 固有の可変role styleなので、将来 style を変えても旧音声が黙って残る。
- **影響**: retry / Local Rewrite / `--stage tts` 再実行時に「audit・player上のtextと実音声が異なる」episode が Gate を通過する。OPEN-226 の冪等性ガード未実装(設計書§5-2 Guardrail 4)と同じ穴。
- **最小是正案**: `_generate_or_reuse_kp()` に `expected_text` 引数を追加し、role="explanation" では cached の `text`/`canonical_text` と `explanation_text` の一致を要求、加えて `cached.get("style_version") != FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` なら reuse しない(可変segmentと同一の判定に揃える)。既存テスト `er019_family_x_kp_structure_wiring_01_test_01.py:391-427` が現挙動を固定しているため同時更新が必要。english role(used_form変化)も同様に guard すると望ましい(既存の限界の解消)。
- **E2E前に必要**: **はい**(修正しない場合は「tts stage 再実行時に b1b の `kp*_explanation_en.wav` と `key_phrase_explanations_text` を必ず破棄する」を必須運用として明記)。

### MAJOR-2: Standard(A2) の構造Gateが Advanced より弱く、`# ` 欠落時に title が空のまま通過する

- **根拠**: Advanced は `_FAMILY_X_TITLE_BODY_RE = ^#\s+(.+?)\s*\n\n(.+)$`(`er003_v1_n3_01_advanced_adaptation_generate.py:579,600-603`)で `# ` を必須にしているが、Standard は `strip_title()`(先頭行が非空か)だけ(`er003_v1_n3_01_standard_a2_generate.py:573-574, 315-319`)。`split_family_x_article_text_v2()` は `^#\s+` に一致しなければ `title=""`・`body_start=0` とし、**title行を本文第1段落に含めたまま status OK を返す**(`er003_v1_n3_01_scaffold_generate.py:191-213`)。その結果 topic_intro が `"Today's topic is ."`(runner `:850`)、ASR期待部分文字列も空(`first_words("",3)`)になり、機械Gateに引っかからないまま音声化される。
- 併せて: (a) `## In one line` 欠落時は `split_v2` が RuntimeError を投げるが `_family_x_ensure_split_or_paragraph_retry()` は捕まえないので、retryせず課金後にクラッシュ停止する。(b) **本文中の markdown 見出しを検査する機械チェックがどこにも無い**。`detect_prohibited_symbols()`(`er003_audio_tts_asr_safety.py:1026-1076`)は `#` を対象にしておらず、`tts_safe_en/news_en` も除去しない(`er003_v1_n3_01_tts_generate.py:702-714, 778-779`)ため、混入した `### ...` は ASR不一致→3 attempt消費→STOPPED という高コストな失敗になる(ユーザー決定「途中Heading廃止」に対する機械的保証がゼロ)。
- **最小是正案**: `generate_family_x_standard_a2_no_heading()` のparse gateを Advanced と対称化する——`^#\s+` の title行、`## In one line` の存在、本文中に見出し行が無いこと、の3点を満たさなければ 1回retry。可能なら同じ3点を `split_family_x_article_text_v2()` に status として持たせ、両レベルで共通化するのが最小かつ効果的。
- **E2E前に必要**: **はい**(少なくとも Standard 側の `^#\s+` 必須化。残りは plan stage 出力の目視Gateで代替可)。

### MAJOR-3: E2E は `--tts-backend speech_metadata_flash_lite` 必須だが CLI既定は legacy。しかも解説styleだけ backend gate が無い

- **根拠**: `er019_family_x_audio_production_runner_01.py:1707-1713` の既定は `structured_separation`。既定のままだと (a) 固定shell は version `"v1"` の旧キー=Champion未使用、(b) `_role_style()` / `_role_style_ja()` / `_role_style_slower()` は全て None を返し J3/E2/A2連結が無効(`:551-553, 796-798, 805-816, 827-830`)、(c) しかし **KP解説だけは `style_prefix_override=fl_styles.KEY_PHRASE_EXPLANATION_EN` を無条件に渡す**(`:733`)ため Variant B が legacy モデルへ適用される(er046 未検証の組み合わせ)。結果として「どの承認仕様にも一致しない半新規episode」が全Gateを通過する。
- **影響**: CLIフラグ1個の抜けで¥150〜250を無駄にし、かつ間違ったepisodeを試聴・承認しかねない。
- **最小是正案**: 解説styleも `_role_style` と同じ backend gate に揃える(対称化)か、runnerで tts stage 開始前に backend を明示チェックして記録/停止する。加えてE2E手順書に実行コマンド全文(`--tts-backend speech_metadata_flash_lite`、`--stage` 個別、`--budget-jpy` 段階値)を固定記載し、Gate項目として `entry_point.json.tts_backend` と audit の `style_prefix` 実値を突き合わせる。
- **E2E前に必要**: **はい**(コード修正 or 手順+Gate明文化のいずれか)。

### MAJOR-4: OPEN-228 gate は `er012_e` runner の非writer stage経由で今も到達可能(到達不能証明はwriter段限定)

- **根拠**: `er012_e_family_entertainment_two_level_runner_01.py:556-557 run_scaffold_stage()` → `sc.run_theme_scaffold()` → `er003_v1_n3_01_scaffold_generate.py:886 split_article_text(article_text)`(旧h3見出し2つ必須gate、無変更で残置)。同runner の `main()` は `--stage scaffold/tts/assemble/player/all` でこの legacy A-Family 経路(`run_tts_stage` → `tts_gen.run_theme`)を呼ぶ(`:880-893`)。新構造(見出しなし)のarticle.mdでは確実に RuntimeError になり、しかも `--stage all` では **writer段の課金後**に落ちる。
- **影響**: W1報告の「OPEN-228到達不能」は `run_writer_stage` に限った話で、同じrunnerの他stageは新構造と非互換のまま残っている。運用トラップであり、OPEN-228 を CLOSED にする根拠としても不十分。
- **最小是正案**: `er012_e` の scaffold/tts/assemble/player stage を fail-fast にする(「Family Xは `er019_family_x_audio_production_runner_01.py` を使う」旨のRuntimeError)か `--stage` の choices を `ledger/writer` に限定する。あわせて2runnerの実行順をE2E手順書に明記し、OPEN-228のclose文面に「旧gateは残置、Family X新経路からは到達しない(er012_eの非writer stageは封鎖済み)」と書けるようにする。
- **E2E前に必要**: **はい**(最低でも実行手順の明文化。コード封鎖が望ましい)。

### MINOR(E2E実測/後追いで可)

- **N-1(W1論点1の残り)**: 置換文言自体の出力品質はTrial未検証。E2Eで段落数保持・見出し不在・In one line保持・平均文長を実測確認すれば足りる。設計上の不整合は検出されず。
- **N-2**: 段落retryのmust-fixは `build_must_fix_block()`(`er003_v1_n3_01_standard_a2_generate.py:243-258`)を流用するため、ヘッダが「Verified Fact Ledger 照合で見つかったFact Safety問題」と宣言され、explanation が Standard 側でも「the Japanese article と同じ段落構造を保て」と指示する(`er012_e_..._runner_01.py:318-327`)。Standardモデルは日本語記事を見ないので指示が不整合。発生頻度は低く、文言修正のみ。
- **N-3**: Standard の KP 中間(japanese_meaning)は `style_prefix_override` を渡していない(`runner:951-956`)ため既定の長文 JAPANESE_STYLE_PREFIX のまま。W3 が japanese_title を J3 へ統一した理由(同一記事内のJA style混在)がそのまま残っている。ユーザー決定のJ3適用範囲外の可能性があるため仕様確認事項として提示し、E2Eの通し試聴で違和感を確認。
- **N-4(横断論点: runtime evidence)**: 可変segment・KP解説は `style_prefix`(override時は実文字列)・`model`・`voice`・`sha256`・`canonical_text` が揃う(`er003_b1_p9a_audio.py:286-301`)。一方 **Master Store reuse 経路(固定shell10件・KP english 5件)の返り値は status/path/reused/master_audio_id/qa_evidence のみ**で model/voice/style/canonical_text を含まない(`er006_master_audio_store_01.py:115-133`)。追跡は `master_audio_id` → `manifest.json` の join が必要で、manifest も style_instruction_id/version までで style 全文は持たない。Gate 13 の「全segmentで追跡可能」は**joinを前提に限り充足**。改善するなら reuse 返り値に `key.as_dict()` を1行追加。
- **N-5**: `_segment_missing_mandatory_disfluency_qa()`(`er003_v1_n3_01_assemble.py:192-196`)は `kp{rank}_explanation` を必須対象に含まない(`*_english` とレベル別listのみ)。実際には `disfluency_qa=True` で生成されるので証跡自体はある。また Family X は `required_structure=None` で gate を呼ぶ(`runner:1006`)ため構造完全性(rankごとsub-entry 3件)は未強制。後追い強化候補。
- **N-6**: point_explanation(JA)のChampion styleがcache hit経路のみ有効、という W2 の既知限界は Store削除禁止の前提で許容可。E2Eでは `reused=True` の実測確認で足りる。
- **N-7**: `EXPLANATION_JSON_SCHEMA` が minItems/maxItems=5 固定(`er019_family_x_kp_explanation_01.py:99-101`)で、`attempt()` は `len(parsed["explanations"]) != len(items)` を parse失敗扱いにする(`:255-256`)。KP件数が5以外になった場合、retry消費後 `ExplanationGenerationError` で tts stage 中断。`len(items)` から導出するか事前assertを推奨。
- **N-8a**: er040/er043 の凍結Trialスクリプトは旧シグネチャ `_make_english_key(text, tts_backend=...)` のまま動かなくなる(W2で意図的に無修正)。完了済み一回限りscriptなので許容だが、「再実行不能になった」ことをREPORT/SSOTに事実として残すこと(TODOとして残さない)。
- **N-8b**: W2報告の「shared_narration を参照するのはFamily Xのみ」は不正確(47ファイルがimportし、`er003_v1_n3_01_tts_generate.py`・`er012_b_family_production_runner_01.py` 等のProduction runnerも `ensure_all_shared_narration_*` を呼ぶ)。実際の隔離要因は `tts_backend` gate による version 固定。結論(他Family無影響)は正しいので、**根拠の記述だけ訂正**すべき(将来この誤った前提に依拠するリスクを避けるため)。
- **N-9**: player の `voice` 表示が level で一律(b1b=Charon)で、本文Aoede segmentも "Charon" と表示される(`runner:1503`)。既存からの表示上の不正確さ、音声には影響なし。

## 3. E2E で実測確認すべき項目(Gate追加推奨)

1. `entry_point.json.tts_backend == "speech_metadata_flash_lite"`、かつ audit の `style_prefix` が J3/E2/A2連結/Variant B の**実文字列**であること(可変segment全件+KP explanation全rank)。
2. 各level `parts.json`: `title` 非空 / part1 が title文を含まない / `paragraph_count>=3` / 本文に `#` 始まり行が無い / `in_one_line` 非空。Standardのtitleが空でないことは特に必須(MAJOR-2)。
3. b1b 全rank: `key_phrases[rank].phrase_repeat.path/sha256 == key_phrases[rank].english.path/sha256`、narration に末尾Phrase用の別wavが存在しないこと、`ensure_key_phrase_english_component` 呼び出しが rank数と一致(TTS 2倍化なし)。
4. b1b 全rank: `explanation_status_from_text_gate == "OK"`、語数<=15、`new_fact_tokens` 0件。1件でも違えば **STOP してユーザー判断**(BLOCKER-1の運用代替)。
5. 固定shell 10件: `reused=True`、`master_audio_id` が W2表の9件(+welcomeは既存 `aa130472d437ac80b7cdd474`)と一致、TTS call 0。
6. `tts_generation_results.json` の `style_version == "v2_j3_e2_title"`、全segmentに model/voice/style_prefix/sha256/canonical_text。reuse経路は `master_audio_id` → manifest join で model/voice/version を確認(N-4)。
7. 通し試聴: A2 の JA style混在(title/preview/comment=J3 vs KP meaning=既定, N-3)、Advanced KP の phrase→英語解説→phrase の間(内部pause)が自然か、In One Line の長さ・一文性、Comment1〜4 が新3分割の内容と整合しているか(設計書§5-1項7の未解決点)。
8. 費用: 段階別 `--budget-jpy` 実測、KP解説 LLM call=**1/記事**、explanation TTS=rank数、Phrase再掲TTS=**0**、Heading Readout撤去による -2 segment/記事。
9. 実行規律: `--stage all` 禁止・段階個別実行(設計書§5-2)。MAJOR-1未修正で tts stage を再実行する場合は b1b の `kp*_explanation_en.wav` と `key_phrase_explanations_text` を事前破棄。MAJOR-4未修正なら `er012_e` は `--stage writer` のみで実行。

## 4. 追加探索で見つけた論点(上記に含めた新規分)

- MAJOR-3(backend既定と解説styleの非対称)、MAJOR-4(OPEN-228の残存到達経路)、MAJOR-2(Standard構造Gateの弱さ・in-body heading無検査)、N-4(reuse経路のruntime evidence欠落)、N-7(schema 5件固定)、N-8b(W2根拠の事実誤り)は、委任された6論点には含まれていなかった追加発見です。
- W4論点1(`key_phrase_meanings` の意味的乖離)・論点2(run単位text cacheの粒度)・論点4(Contract 1行追加)は、単体では実害なしと判断します。ただし論点1は MAJOR-1(text/audio drift)と組み合わさると「keyの名前も中身も追跡しづらい」状態になるため、MAJOR-1の是正時に `explanation_text` を canonical text として明示記録することを併せて推奨します。論点2(1件変化で5件再生成、+1 call)はコスト影響が小さく許容可ですが、MAJOR-1の guard が無いと「textだけ更新・音声は旧」という形で害になるため、guard追加が前提です。

Production採用可否(`APPROVED_FOR_PRODUCTION`)および有料E2Eの発火判断は人間ユーザーのみが行うものであり、本レビューは判断材料の提示までです。実装・修正には着手していません。
=== ここまで ===
