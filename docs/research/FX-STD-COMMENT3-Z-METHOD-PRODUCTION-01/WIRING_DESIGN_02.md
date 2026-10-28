# WIRING_DESIGN_02: Opus条件A反映(M-1〜M-5/R-1〜R-7)+Production配線(委任_02)

管理ID: FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01。基準設計: `WIRING_DESIGN_01.md`。Opus全文: `OPUS_REVIEW_01.md`(逐語)。

## 1. 配線点(変更ファイル)
| 変更 | 場所 | 内容 |
|---|---|---|
| 新module | `er019_family_x_std_comment3_z_method_01.py` | M-1(否定短縮形・助動詞not・cannot)/R-2(結果語+文頭So/Thus/Therefore/Still)/R-1(疑問文では結論語を違反としない)/M-5(attempt別text・response_id・model・prompt_sha256・J2有無、parts sha)/R-5(`compute_c2_c3_overlap_notes`)/M-3(`merge_regenerated_comment3`=他4キーsha assert) |
| runner | `er019_family_x_audio_production_runner_01.py` | `_a2_comment3_z`(唯一のhelper。J2+`_a2_support_model()`束縛)、`run_family_x_a2_scaffold`のC3を同helperへ置換、C3非OK時はC4/Preview不実行+`a2_support_texts.json`不書込、`run_theme_scaffold`の`support_stage_failed.json`marker+`support_stage_status`+break、`main()`のrc=3、TTS入口(`support`読込直後)の5キー検査+marker検査、`--regenerate-support comment_3`(`run_regenerate_support_comment3`)、`_comment3_method_of`(summaryへ`comment3_method`、再利用時はWARN) |
| 旧規則撤去(R-4) | `er019_family_x_audio_plan_01.py` | `FAMILY_X_A2_COMMENT_3_ROLE`を撤去(コメントのみ残置)。参照test 3か所を更新(runner test/style_profile test/新test pin) |
| 変更しないもの | C1/C2/C4/Preview呼出、X Advanced(`run_family_x_b1_scaffold`/b1b)、Y、Z、`a2gen.COMMENT_2_ROLE`(無改変) | 既存sha pinが全PASS |

## 2. M-1/R-2: 7記事の切り出し表(API 0。`table7_01.py`、結果json=`table7_before_01.json`/`table7_after_m1_01.json`/`table7_after_r2_01.json`)
| 記事 | 変更前(委任_01) | M-1適用後 | M-1+R-2適用後 | 打切り直前の文 |
|---|---|---|---|---|
| ai_island run_form_prod_01 | 1文 | 1文 | 1文 | 「After that, the average number of towers it could build went down.」 |
| coffee run_m2p0_n01_01 | fallback | fallback | fallback | 「However, "about nine months" is an estimate…」 |
| moon run_ms_03 | fallback | fallback | fallback | 「The team thinks a thick layer of rock … may have worked like insulation.」 |
| small_bag run_kpq_02 | fallback | fallback | fallback | 「Large bags had not disappeared.」 |
| uk_train run_nws_02 | 1文 | 1文 | 1文 | 「Just because we're in the same carriage doesn't mean…」 |
| tesla_spacex run_nws_01 | 3文 | 3文 | 3文 | MAX_SENTENCES |
| paycheck run_pp_02 | 3文 | 3文 | 3文 | MAX_SENTENCES(次は「This cannot prove…」=M-1でcannot単独でも打切り) |
**fallback件数: 3/7 → 3/7(M-1後) → 3/7(R-2後)**。4/7超ではないため語は絞らず全採用(worked/failed/succeeded/won/lost/approved/rejected/ruled/decided/agreed/chose/most/none、文頭So/Thus/Therefore/Still)。ユーザー進言事項なし(Opus「4/7超の場合に限り進言」に該当しない)。全記事で変化なし=M-1/R-2は偽陰性防止(将来記事・変種の漏れ封じ)で、現7記事の範囲ではfallback率を悪化させない。

## 3. M-2: fail-closedの停止配線(a)〜(e)
(a) C3非OK→その時点でreturn(C4/Preview未呼出、LLM計5回→2+最大3回)。(b) 非OK時`a2_support_texts.json`を書かない(`audit/a2_support_generation.json`にC1/C2/C3[却下文含む]のみ)。(c) `{level}/support_stage_failed.json`+`result[level]["support_stage_status"]`+KP/Part 1/2を実行せずbreak、`main()`はentry_pointへ記録してrc=3。成功時にmarker削除。(d) TTS入口で5キーの非空文字列+marker不在を検査し、満たさなければ有料TTS前に`RuntimeError`(b1bは対象外=記録のみ。OutOfScope)。(e) 次の一手を標準出力に表示(`--stage scaffold`再実行)。

## 4. M-3: `--regenerate-support comment_3`
`--stage scaffold --level a2`専用(`--dry-run`/`--scaffold-only`併用はparser.error)。既存`a2_support_texts.json`を読み、**初回経路と同一の`_a2_comment3_z`**で生成、`merge_regenerated_comment3`で他4キーsha不変をassert(書込前後)。`audit/a2_support_generation.json`はC1/C2/C4/Previewの元記録を保持してcomment_3のみ差替え(旧はcomment_3_history)。旧版は`a2_support_texts.before_c3_regen.json`/`audit/a2_support_generation.before_c3_regen.json`へ一度だけ退避。KP・Part 2・study_text・parts.jsonには触れない(testでdir内容を固定)。非OKならtexts/auditは不変、`audit/a2_comment3_regeneration_failed.json`+markerを残す。続いて`--stage tts --level a2 --only-segments comment_3`、他音声は`validation_inheritance`で引継ぎ。

## 5. R-6: parts入力の確定
再生成のpartsはsource記事(`er019_output/<slug>/<run>/a2/article.md`)の分割にLR台帳overlay(`er132_lr_overlay_pages_01.overlay_level_dir_units`、表示本文=公開本文と同じ規則)を適用したもの。AI島ではpart1の`AIs sent`→`AI agents sent`(1語)。overlay有無と、base/inputのpart別shaを`comment3_z_audit.input_parts_source`へ記録。初回scaffoldはoverlay前の素のparts(LR台帳が無い時点)。

## 6. R-3: 未公開のX Std run(support生成済み・未assemble)の方式混在
`er019_output/family_x_audio_production_wiring_01/*/a2/a2_support_texts.json`があり`assembled/*.wav`が無いrunを列挙(Fable判断用、hard STOPにしない)。多くは`tru_ev_*`・`*_ev_*`・`aborted`・`superseded`の証跡run(公開対象ではない)。support再利用時は`scaffold_run_summary.json`の`comment3_method`が`null`(旧仕様)でWARNを出し、必要なら`--regenerate-support comment_3`でC3だけZ方式へ作り直せる。一覧: `unpublished_std_runs_01.txt`。

## 7. R-7: test(`er019_family_x_std_comment3_z_method_01_test_01.py`、45件。旧25→45)
旧「未配線pin」を反転(`test_wired_comment3_uses_z_role_and_fallback_context`)、旧C3役割文pin撤去、`test_legacy_c3_role_removed_from_repo_source`。追加: M-1否定形、R-2語彙、7記事fallback≤4、R-1疑問文、M-5 audit、excerpt有りZ_EXCERPT(LONG_P3)、J2適用(`6〜8`→`6から8`)、通常時LLM5回、C3失敗でC4/Preview不呼出+null texts不書込、marker+KP不呼出、main rc=3、TTS入口検査、再生成経路(他4キーsha/audit保持/失敗時不変)、2経路helper共有、b1bは既存pin(runner test 53件・`X_B1`役割sha pin)でPASS。
