# WIRING_DESIGN_01: Family X Standard Comment 3 Z方式のProduction設計(委任_01、未配線、API 0)

基準: Trial `docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01/`(METHOD_DIFF_01.md / generate_after_01.py / after_generation_log_01.json)。実装: `er019_family_x_std_comment3_z_method_01.py`(新規module)。test: `er019_family_x_std_comment3_z_method_01_test_01.py`(25件)。

## (a) Comment 3役割文
`COMMENT3_Z_ROLE = a2gen.COMMENT_2_ROLE`(`er003_v1_iran01_a2_generate.py:137`の既存定数を無改変で参照。新Prompt文は作らない)。sha256=`COMMENT3_Z_ROLE_SHA256`(= `sha256(a2gen.COMMENT_2_ROLE)`、testで固定)。Trial `generate_after_01.py:ROLE[3]`も同一定数。testで「Trial `after_generation_log_01.json` comment_3.full_prompt == `a2gen.build_support_prompt(COMMENT3_Z_ROLE, context_block)`」を確認(Prompt枠も同一=SUPPORT_JA_PRINCIPLE/PROHIBITIONS/出力形式を共通)。ユーザー仕様(回収1点+後半への問い+原則1〜2文)はこの定数の文面で満たされる(`:137-146`)。旧`plan.FAMILY_X_A2_COMMENT_3_ROLE`(`er019_family_x_audio_plan_01.py:209`)は定数として残置(配線後は不使用。既存test `er019_family_x_style_profile_01_test_01.py:593`・`er019_family_x_audio_production_runner_01_test_01.py:274,281`が参照するため削除せず、委任_02で使用箇所Grepを再確認)。

## (b) ニュース向け参照範囲制御(決定論、LLM不使用)
`build_part3_excerpt(part3)`。Part 3を文に分割し先頭から順に走査、次のいずれかの文の手前で打ち切る(その文は渡さない):
1. `CONCLUSION_MARKER_RE`(even so / still, / in short / overall / in conclusion / in other words / in the end / after all / too soon / do(es) not show / proof / however / as a result / this means / that means / for now / in fact)を含む文
2. `RESULT_SENTENCE_RE`(数字・%・数詞、found/showed/turned out/rose/fell/dropped/increased/went up/down/did better 等の結果動詞、比較[more/less than, higher, lower, fewer]、因果・結論動詞[because/led to/caused/suggests/thinks]、否定的結果[had not/no longer/never]を含む文)
3. 上限: 2段落目まで(`MAX_EXCERPT_PARAGRAPHS=2`)・3文(`MAX_EXCERPT_SENTENCES`)・70語(`MAX_EXCERPT_WORDS`)
渡す語数が`MIN_EXCERPT_WORDS=8`未満なら0文扱い=Part1+Part2のみ(`fallback_no_excerpt=True`)。Part 3の割合は一切使わない。Trialの段落単位規則(先頭25%・最低2段落・段落marker)は、(i)割合が無条件(ユーザー指示違反)(ii)Part 3第1段落の結果文を含んでしまう、ため採用せず文単位に変更。AI島ではTrial実績と同じ出力(第1文のみ)になることをtestで固定。
context: Trialと同一ラベル `【すでに聞いた本文(前半)】Part1\n\nPart2` + (excerptあれば)`\n\n【これから聞く本文(後半)】excerpt`(`build_comment3_context_x_std`)。物語向け注記(`NOT_NEWS_NOTE`)は付けない。

### 境界例(机上確認、`build_part3_excerpt`の実出力)
| 記事(parts.json) | 渡る範囲 | 打切り理由・直前の文 | 判定 |
|---|---|---|---|
| ai_island_temple__run_form_prod_01 | 1文: 「The researchers also erased a way to “throw rocks…” from one AI’s memory.」 | RESULT_SENTENCE「After that, the average number of towers it could build went down.」 | Trialと同範囲。結果(went down)・Even so(第2段落)を除外 |
| coffee_prices__run_m2p0_n01_01 | 0文(fallback) | CONCLUSION_MARKER「However, “about nine months” is an estimate…」 | Part1+Part2のみ |
| moon_shrinking__run_ms_03 | 0文(fallback) | RESULT_SENTENCE「The team thinks a thick layer of rock … insulation.」(答えそのもの) | Part1+Part2のみ(答え先取り防止) |
| small_bag__run_kpq_02 | 0文(fallback) | 「This list matters.」(3語)のみ→MIN未満。次文「Large bags had not disappeared.」はRESULT | Part1+Part2のみ |
| uk_train_speaker_playback__run_nws_02 | 1文 | RESULT_SENTENCE「Just because … doesn’t mean we’ve joined the fan club…」 | 1文のみ |
| tesla_spacex_merger_talks__run_nws_01 | 3文(株主承認の手続き説明) | MAX_SENTENCES | 結果文なし、上限で停止 |
| paycheck_personality__run_pp_02 | 3文(問い+「The team studied data…」) | MAX_SENTENCES(次は「This cannot prove…」=RESULT) | 上限で停止 |
所見: 7本中3本がfallback(Part1+Part2のみ)、4本で1〜3文を渡す。fallbackの割合が高いのは「結果の先取りを防ぐ」安全側設計の帰結で、fallback時も役割文はZ(回収1点+後半への問い)でありPart1+Part2から問いを作れる(AI島Beforeはこの方式相当)。割合が品質上問題なら閾値調整(MIN語数・結果語彙)は委任_02のregression/E2Eで評価。

## (c) 先取り検査(事後lint、決定論)
`comment3_spoiler_lint(comment, part1, part2, excerpt, withheld_text)`。withheld_text=渡さなかった文。blocking違反:
- `WITHHELD_NUMBER`: 渡さなかった文にだけある数値(数字・数詞twoなど。全角/カンマ正規化)がCommentにある(「二つ」等の漢数字は二〜九+助数詞のみ検出)
- `WITHHELD_TERM`: 渡さなかった文にだけある英単語(4字以上)がCommentにある
- `CONCLUSION_WORD`: 結論/結局/最終的/答えは/判明/証明/突き止め/正体は/明らかになり
- `STRUCT_LABEL`: Part N/Full Story/第N部/本文N(Zのlintと同種)
Zの物語語彙(「記事」「ニュース」禁止等)は適用しない(Xの正規文言と矛盾。test `test_story_vocab_not_applied`)。流れ(`run_comment3_z_method`): 生成→lint→違反なら同一入力で1回retry→なお違反ならPart1+Part2のみで生成(excerptが元から空なら省略=最大2回)→なお違反なら`status=COMMENT3_SPOILER_LINT_FAILED`・`text=None`・`rejected_text`保持(fail-closed、下流は既存のsupport失敗扱い=停止/HR。偽のOKを残さない)。技術失敗(`run_support_text`が内部で2回retry済み)はそのまま返す。最大LLM呼出=3回/記事(通常1回)。

## (d) 配線点(委任_02で実施。本委任では未変更)
- 正式初回生成: `er019_family_x_audio_production_runner_01.py:342-344`(`run_family_x_a2_scaffold`のComment 3 3行)のみを`run_comment3_z_method(lambda role, ctx: _a2_run_support_text_j2(client, role, ctx, model=_a2_support_model()), parts)`に置換。Comment 1(:334-336)・2(:338-340)・4(:346-348)・Preview(:350-355)は触らない。J2(範囲値正規化)は`_a2_run_support_text_j2`内(:317-328)で従来どおり適用。生成順C1→C2→C3→C4→Previewは不変。呼出元は`:867`のみ(Standard=a2のみ。b1b=Advancedは`:865` `run_family_x_b1_scaffold`=変更なし)。
- retry/再実行(regeneration): `--stage scaffold`の再実行は同じ`:867`→同関数を通る。support文面の再生成経路は他になし(`er020`系Local Rewriteはsegment音声のTTSテキスト修正でCommentのLLM再生成を持たない=Grep `run_support_text|FAMILY_X_A2_COMMENT` er020*.py で該当0)。run_support_text内部の技術retry(2回, `er003_v1_iran01_a2_generate.py:198-`)は`run_support`の中で従来どおり。
- resume: 保存済み`a2_support_texts.json`を再利用する経路(`:843-858` `_resume_review`/`scaffold_only=="kp"`)は`support = {}`でscaffoldを呼ばず再利用=新規LLM呼出なし・仕様は保存時のまま一貫。読込側は`:246-247`(plan構築)、`:2011`、`:3197`(`a2_support_texts.json`)で、いずれも文面のみ消費。
- DEV/Trial scriptは配線に使わない: `docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01/generate_after_01.py`は参照せず、新moduleは独立実装(Trial scriptのimport無し)。`er057_coffee_final_v5_comment4_01.py`/`er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py`等のDEV scriptは対象外。
- 失敗時: `COMMENT3_SPOILER_LINT_FAILED`は`text=None`。現行`run_family_x_a2_scaffold`は`results`にそのまま入れ`save_json`するため、`a2_support_texts.json`にcomment_3=nullが残る。下流が`support[name]`をそのまま使う(:1625,:2064等)点とKP stageの前でのfail-closed停止を、委任_02で専用の停止(rc/marker)として設計する(要Opus論点)。

## (e) 監査記録
`run_comment3_z_method`の戻り値に`comment3_z_audit`(method_version=`FX-STD-COMMENT3-Z-V1`、role_sha256、mode[Z_EXCERPT/PART12_ONLY_NO_SAFE_EXCERPT/PART12_ONLY_LINT_FALLBACK]、excerpt{cut_reason, paragraph_count, sentence_count, passed_sentence_count, passed_paragraph_indices, passed_word_count, passed_excerpt_sha256, withheld_sentence_count, part3_sha256}、attempts[{attempt, mode, context_sha256, status, lint_violations}]、lint_retry_count、final_status)。runnerは`results`全体を`audit/a2_support_generation.json`へ保存する(`:359-360`既存)ため、追加ファイルなしで監査に残る(`a2_support_texts.json`のスキーマ{key:text}は変更しない=下流不変)。

## (f) Regression test計画(実装済み)
- 役割文sha固定: Comment1/2/Preview/X A2 Comment4/X A2 Comment3(旧)/X B1 Comment3・4(Advanced)。
- `run_family_x_a2_scaffold`をfake clientで実行し、Comment1/2/4/Previewの(役割+context)全文sha・呼出順(5回)・各ラベルを固定。Comment 3は「従来のまま(旧X役割・Part1+Part2)」を未配線ピンとして固定(委任_02で意図的に反転)。
- 他moduleが新moduleをimportしていないこと(Y/Z/Advancedへの波及なし)をGlob全`*.py`で確認。
- 既存関連test: runner 53件・style_profile 50件・kp_stage_fail_closed 8件・er119_x_wiring 12件・er053_c3_audio_guard 33件 全PASS。

## (g) 委任_02(配線)の予定
Opus条件Aレビュー→runner 3行置換→未配線ピンtestの反転→DefaultOffIsolationは不要(承認済み仕様の配線でflagなし)→実Prod経路でAI島Standardのsupport再生成(Comment 3のみLLM 1回、約0.1円)→TTS(comment_3のみ)→ASR→組立→公開検査。
