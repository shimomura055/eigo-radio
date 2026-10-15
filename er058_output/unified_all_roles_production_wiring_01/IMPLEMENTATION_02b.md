# IMPLEMENTATION_02b: 共通判定・値ガード・registry・Unit test・静的監査(branch上、Production未配線)

管理ID `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_02b。branch `feat/auw-unified-asr-01`。有料API 0・JPY0(mock engineのみ)。
前提: DESIGN_01(3953de4ff)+DESIGN_02_ADDENDUM_01(9ed5754e2。食い違いは追補優先)+Fable補正(EN "one"の脱落/挿入=UNKNOWN)。
到達=`UNIT_READY_ON_BRANCH`。既存Production関数(er006_*/er007_*/runner群)は無変更。mainは無変更。

## 1. 実装概要(新規ファイルのみ)
| file | 内容 |
|---|---|
| `er078_asr_value_guard_01.py` | `value_guard(src,hyp,lang)->ValueGuardResult(kind,pairs,reasons,warnings)`。5値、優先順位 DIFF>UNKNOWN>AMBIGUOUS>EQUAL>NO_VALUES。JA=算用/漢数字(位取り〇・混在「1万2000」)/かな数詞辞書/助数詞/割合/分数「N分の」/概数(数十・十数)/曖昧語(十分等)+閉集合マーカー。EN=Tier1 atom(number/time)+単位語+同音語(for/to/won/ate)+soft-one |
| `er078_asr_unified_judge_01.py` | `unified_judge(ctx, primary_result, secondary_fn, *, lang, role, final_and_gate=True, secondary_accept_fn=None)->JudgeResult`。7状態、`SecondaryCache`(成功のみ)、`RunState`(circuit breaker・技術STOP記録)、`SCG_EXCLUSIONS`(データ化)、`est_jpy`(秒数ベース) |
| `er078_pass_with_warning_registry_01.py` | `derive_listening_list`/`write_listening_list`/`render_html_section`/`render_standalone_html`。`asr_judgement`(・`asr_judgement_inherited`)付きsegmentを再帰走査、sha256+ラベルで重複排除、STOPPED除外、途中STOPでも呼べる純関数 |
| `er078_asr_value_guard_01_test_01.py` | 58件(9例14ケース+追補パターン26+"one"6+閉集合マーカー・集約・警告・Production前処理後原稿・er066 parity) |
| `er078_asr_unified_judge_01_test_01.py` | 45件(全状態遷移・Secondary呼出0/1回・cache・障害4種+circuit breaker・承認済みequivalence非否定・否定差・est_jpy・SCG定数parity) |
| `er078_pass_with_warning_registry_01_test_01.py` | 9件 |
| `er078_asr_unified_wiring_static_audit_01.py` + `er078_asr_unified_wiring_allowlist_01.json` | 8件。import graph方式。allowlist 33 entry(呼出合計42)=pre_wiring snapshot |

## 2. 状態機械の実装上の判断(追補との対応)
- Primary PASS: 最終ANDゲート(値DIFF/否定差→NG_PROTECTED)。承認済みequivalence根拠(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`/`TIER1_DIFF_ANCHORED`/`TIER1_NUMERIC_EQUIVALENCE`/`READING_MATCH`)は再否定しない(ゲートskipを監査recordに記録)。
- **判断(追補が明記していない箇所)**: Primary PASSだが根拠なしで値AMBIGUOUS(10分/十分)の場合は、追補§1-3「ASR転写`10分`のままではPASSしない」に従いP3へ降格(Secondary 1回)。
- Primary NG: P1=値DIFF/否定差、P2=`SCG_EXCLUSIONS`(A3 length/A4 C2、U1待ちA5 類似度<0.4・A6 C1)、P3=Secondary。AMBIGUOUSはP3(追補§1-3)。
- Secondary障害(None/空/例外/error/circuit open)=PASS不可・`NG_SECONDARY_UNAVAILABLE`・非キャッシュ・技術STOP記録(restartable, approval_required=False)。連続3回でrun単位circuit breaker。Lock状態は未追加。
- Secondary許容集合は本module内に再実装せず、`SecondaryOutcome.accepted`または`secondary_accept_fn`で注入。注入が無い場合のみ同一表層(EXACT)。
- LR後v1: PASS時は必ず`LR_REWRITTEN`警告(PASS_WITH_WARNING)。`ctx.force_secondary`でPrimary PASSでもSecondary必須(U2暫定=呼出側が指定)。
- COST_GUARD($0.05/segment)は本judgeでは未適用(`COST_GUARD_IN_UNIFIED_JUDGE="NOT_APPLIED_02B"`)。既存adapter側に残置。再校正/無効の確定は委任_03/04。

## 3. 再利用元対応表
| 機能 | 再利用元 | 方式 |
|---|---|---|
| EN atom抽出 | `er021..._tier1_atoms` | 関数import(number/time atomのみ。private関数) |
| EN normalize_numeric | `er006_preprod_hardening_01_validation.normalize_numeric` | 値ガード内では再実装せず、Tier1の同等契約に委ね(Tier1が%/percent/通貨/序数/数詞語を吸収)。`_is_number`の拡張は委任_03の配線commitで行う(追補§2) |
| EN否定語 | `er006..._NEGATION_WORDS` | import(judge) |
| JA漢数字位取り | `er011_ja_asr_variant_layer_01.kanji_numeral_run_to_int` | 関数import |
| JA Stage 1(find_spans/_to_value/COUNTERS/AMBIGUOUS_RE/is_irregular_sig) | `er066_..._trial.py` | **移設(拡張込み)**。er066はTrial専用でヘッダ・DESIGN §5-4が「Production→Trial import禁止」のためimportしない。移設分の一致はtest(parity)でer066をimportして突合(test側のみ) |
| JA否定 | `er003_audio_tts_asr_safety._has_negation_ja` | import(judge) |
| 費用式 | `er007_ja_secondary_asr_01.py:309-311` | 定数・式を同値で保持(循環import回避。parity test) |

移設時の拡張: 位取り〇、混在数字(1万2000)、割、分数、概数(数十/十数)、かな数詞辞書、助数詞なし裸数字、閉集合マーカー化。**fail-safe**: 解釈不能なspanは黙って無視せず`unparsed`=UNKNOWN。

## 4. 9例+追加パターンの判定結果(実測)
| id | lang | 原稿 | 転写 | 期待 | 実測 | 一致 |
|---|---|---|---|---|---|---|
| 1_三人_3人 | ja | 三人で行きました。 | 3人で行きました。 | EQUAL | EQUAL | OK |
| 2_三人_四人 | ja | 三人で行きました。 | 四人で行きました。 | DIFF | DIFF | OK |
| 3_三十人_30人 | ja | 三十人が来ました。 | 30人が来ました。 | EQUAL | EQUAL | OK |
| 4_三十人_40人 | ja | 三十人が来ました。 | 40人が来ました。 | DIFF | DIFF | OK |
| 5a_十分_10分_マーカーなし | ja | 十分待ちました。 | 10分待ちました。 | AMBIGUOUS | AMBIGUOUS | OK |
| 5b_十分間_10分間_マーカーあり | ja | 十分間待ちました。 | 10分間待ちました。 | EQUAL | EQUAL | OK |
| 5c_三十分_30分 | ja | 三十分待ちました。 | 30分待ちました。 | EQUAL | EQUAL | OK |
| 6_100円_百円 | ja | 100円でした。 | 百円でした。 | EQUAL | EQUAL | OK |
| 7a_EN_20%_20percent | en | The rate is 20% today. | The rate is 20 percent today. | EQUAL | EQUAL | OK |
| 7b_JA_20%_20パーセント | ja | 20％の人が来ました。 | 20パーセントの人が来ました。 | EQUAL | EQUAL | OK |
| 8_EN_20%_30% | en | The rate is 20% today. | The rate is 30% today. | DIFF | DIFF | OK |
| 8_JA_20%_30% | ja | 20％の人が来ました。 | 30％の人が来ました。 | DIFF | DIFF | OK |
| 9_EN_25%_26% | en | The rate is 25% today. | The rate is 26% today. | DIFF | DIFF | OK |
| 9_JA_25%_26% | ja | 25％の人が来ました。 | 26％の人が来ました。 | DIFF | DIFF | OK |
| 一人で/ひとりで | ja | 一人で行きます。 | ひとりで行きます。 | EQUAL | EQUAL | OK |
| 一つ/ひとつ | ja | 一つ選びます。 | ひとつ選びます。 | EQUAL | EQUAL | OK |
| 二十歳/はたち | ja | 二十歳になりました。 | はたちになりました。 | EQUAL | EQUAL | OK |
| 二〇二六年/2026年 | ja | 二〇二六年に始まりました。 | 2026年に始まりました。 | EQUAL | EQUAL | OK |
| 1万2000人/一万二千人 | ja | 1万2000人が来ました。 | 一万二千人が来ました。 | EQUAL | EQUAL | OK |
| 数十人/十数人 | ja | 数十人が来ました。 | 十数人が来ました。 | DIFF | DIFF | OK |
| 十分な/充分な(単独) | ja | 十分な量です。 | 充分な量です。 | AMBIGUOUS | AMBIGUOUS | OK |
| 3分の1/3分の1(同表層) | ja | 3分の1になりました。 | 3分の1になりました。 | EQUAL | EQUAL | OK |
| 3分の1/1/3(構文不一致) | ja | 3分の1になりました。 | 1/3になりました。 | UNKNOWN | UNKNOWN | OK |
| EN for->4 | en | He waited for the bus. | He waited 4 the bus. | AMBIGUOUS | AMBIGUOUS | OK |
| EN 4->for | en | He bought 4 books. | He bought for books. | AMBIGUOUS | AMBIGUOUS | OK |
| 3〜5日/35日(OPEN-334) | ja | 3〜5日かかります。 | 35日かかります。 | DIFF | DIFF | OK |
| 3人/3日(助数詞違い) | ja | 3人来ました。 | 3日来ました。 | DIFF | DIFF | OK |
| 2026年/二千二十六年 | ja | 2026年です。 | 二千二十六年です。 | EQUAL | EQUAL | OK |
| 3,000円/三千円 | ja | 3,000円です。 | 三千円です。 | EQUAL | EQUAL | OK |
| EN 5/$5 | en | It costs 5 today. | It costs $5 today. | DIFF | DIFF | OK |
| EN 5/5% | en | It grew 5 today. | It grew 5% today. | DIFF | DIFF | OK |
| EN 28/28th | en | On 28 people left. | On 28th people left. | DIFF | DIFF | OK |
| 1.5倍/1.6倍 | ja | 1.5倍になりました。 | 1.6倍になりました。 | DIFF | DIFF | OK |
| JA 欠落 三人/数字なし | ja | 三人で行きました。 | で行きました。 | DIFF | DIFF | OK |
| JA 追加 数字なし/三人 | ja | で行きました。 | 三人で行きました。 | DIFF | DIFF | OK |
| JA 値なし | ja | これは本です。 | これは本です。 | NO_VALUES | NO_VALUES | OK |
| EN 値なし | en | This is a book. | This is a book. | NO_VALUES | NO_VALUES | OK |
| EN 4 vs 5 | en | There are four people here. | There are five people here. | DIFF | DIFF | OK |
| EN twenty-five/25 | en | There were twenty-five people. | There were 25 people. | EQUAL | EQUAL | OK |
| EN 単位違い 3 hours/3 days | en | It took 3 hours. | It took 3 days. | DIFF | DIFF | OK |
| one脱落(代名詞的) | en | One of the students left. | Of the students left. | UNKNOWN | UNKNOWN | OK |
| one挿入 | en | The students left. | One of the students left. | UNKNOWN | UNKNOWN | OK |
| one脱落(冠詞的) | en | I have one apple. | I have apple. | UNKNOWN | UNKNOWN | OK |
| one vs two(明確な数量: 相手側に別の数詞) | en | I have one apple. | I have two apple. | DIFF | DIFF | OK |
| one vs 2 | en | I have one apple. | I have 2 apple. | DIFF | DIFF | OK |
| one vs 1(同値) | en | I have one apple. | I have 1 apple. | EQUAL | EQUAL | OK |

追加の設計判断(testで固定): 助数詞辞書外の裸数字と辞書内助数詞(3メートル/3キロ)は値同一・単位が片側のみ判定可能のためUNKNOWN。「なのか/ようか/とお」は一般語と衝突するため辞書に入れず脱落判定の保守側(UNKNOWN)にのみ使用。「いつか」は曖昧語atom。

## 5. test結果
- 新規4ファイル(`pytest ... -q`): **120 passed**(value_guard 58 / unified_judge 45 / registry 9 / static_audit 8)。
- 既存影響確認(`er021*test*.py er007*test*.py er006*test*.py`、31ファイル): **428 passed / 14 failed(既存)**。14件は`er078`を一切importせず、新規ファイル追加のみの本commitと無関係。代表: `er006_asr_provider_routing_01_test.py::test_japanese_routes_to_azure`(現行ルーティングはopenai_asr=gpt-4o-mini-transcribeでtest期待のazureと不一致)。HEAD clean worktreeでの突合はパス長(Filename too long)で作成できず未実施。詳細は RESULT_PACKET_AUW2b.md (8)。

## 6. 静的監査snapshot(entrypoint 8本から到達するmoduleのASR呼出、pre_wiring)
33 entry(呼出42)。DESIGN J1〜J11との突合:
| J | module:function | snapshot内 |
|---|---|---|
| J1 | er003_v1_sing01_voice01_generate:generate_charon_english | transcribe+evaluate_attempt_with_cascade |
| J2 | er003_v1_sing01_news_tail_fix:generate_news_narration_wide_margin | 同上 |
| J3 | er003_v1_crosslevel_audio_02_common:_run_a2_minimal_fallback_attempt | 同上 |
| J4 | er012_b_family_voices_production_01:generate_voice_body_wide_margin | 同上 |
| J5 | er003_v1_repro01_main_generate:generate_narration_snippet_verified_strict | transcribe+cascade(EN)+ja cascade |
| J6 | er003_v1_sing01_point_headings_aoede:generate | transcribe+cascade |
| J7 | er003_v1_n3_01_tts_generate:apply_a2_slowdown_postprocess(+_post_slowdown_cascade_rescue) | transcribe+classify_asr_match+cascade_detail |
| J8 | er003_v1_n3_01_tts_generate:generate_a2_japanese_with_fallback | transcribe+ja cascade |
| J9/J10 | er003_v1_sing01_voice01_generate:generate_charon_japanese | transcribe x2 + ja cascade x2 |
| J11 | er019_family_x_validation_inheritance_01:rejudge_with_current_judge | `classify_asr_match`(保存転写に対するAPI 0再判定)。配線後に統一判定の入口へ置換 |
**J1〜J11に無い呼出(Fableへ報告)**: (a) `er013_family_c_production_runner_01.get_or_run_asr`(Family C診断用ASR。判定に使われるか未確認)、(b) `er008_disfluency_qa_18.transcribe_verbatim`/`er011_open121_repetition_qa_production_01.run_method_c_v2_window_check`(Safety QA用転写=内容判定点ではない)、(c) `er006_preprod_hardening_01_validation`内部の`classify_asr_match`/`evaluate_attempt`(既存P-chain本体)、(d) `er006_secondary_asr_01`/`er007_ja_secondary_asr_01`本体(adapter化の対象)。
test: 配線前は統一judgeがentrypointから**到達しない**ことをassert(未承認配線の検知)。配線後(委任_03/04)にallowlistのphaseを`post_wiring`へ切替えると「judge/adapter内部以外のASR呼出0」のassertに変わる(test内コメントに手順記載)。

## 7. 未実装(次委任)
- 既存2関数のadapter化・runner/leaf配線(委任_03 EN / _04 JA+J11)。`_is_number`のマーカー付きtoken認識拡張(配線と同一commit、追補§2)。
- 試聴リストのX/Zページ節組込み(委任_03)。COST_GUARD再校正/無効の確定。HR queue/attempt_history/tts_generation_resultsへの`asr_judgement`書込み(配線時)。

## 8. U1/U2待ちの箇所
| 項目 | flag名 | 現状値 | 場所 |
|---|---|---|---|
| U1(JA C1固有名詞差・類似度<0.4の除外を解放するか) | `er078_asr_unified_judge_01.U1_KEEP_C1_SIMILARITY_EXCLUSIONS` | `True`(現行維持)。承認後は1行で`False`。testで解放時の挙動も固定済み | judge:`SCG_EXCLUSIONS`のu1_gated 2件(A5/A6) |
| U2(LR後v1のSecondary必須化) | `er078_asr_unified_judge_01.U2_FORCE_SECONDARY_SCOPE` / `AttemptCtx.force_secondary` | `"A2_ONLY"`(暫定=呼出側が指定) | judge |
