# FIX_02 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02、2026-10-15)

Status: **Trial実装済み(mode=corrected)**。Production既定は`legacy`(現行挙動そのまま)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。Opus条件Aレビュー全文は`OPUS_REVIEW_01_VERBATIM.md`。

## 1. 何が問題だったか(根本原因)
- 欠陥①: gloss再整合の合否を「KPにスロット語が無いのにglossに『～』が残るか」という**記号の有無**で判定していた(`gloss_has_unjustified_slot`)。承認済み規則(辞書的に自然なら『～』可)と矛盾し、意味欠落の検出手段にもなっていなかった(旧gloss不整合6件中3件のみ捕捉)。
- 欠陥②: 再整合が2回失敗しても`gloss_alignment_status=FAILED`をartifactに書き通知ファイルを出すだけで、TTS・Gate・assemble・page/runnerのいずれもその状態を**参照しなかった**(INVESTIGATION_01 5節)。不整合itemが正常TTS入力・正常完成として素通りした。
- Opus条件Aレビュー(BLOCKER 2件): 草案のHuman Review Lock流用は、A2のwavが`narration/meaning_{i}.wav`・canonical textが`ja_gloss_tts`でkey/text hashが一致せず**fail-open**になる(OF-KGDC-01)。B1ではglossが解説LLM入力・page表示に流れ、TTSだけ止めても止まらない(OF-KGDC-02)。

## 2. 何を変更したか(構造=案A')
| 領域 | 変更 |
|---|---|
| `er003_key_words_gloss_alignment.py` | `mode`切替(`GLOSS_ALIGNMENT_MODE`既定`legacy`、`align_glosses(..., mode=)`、envでは切替えない)。correctedを追加: 追加内容語の算出(`added_content_words`、機能語除外)、課題指示文(DESIGN_DRAFT_01 3.3+OF-KGDC (b)、承認規則本文は実行時抽出・sha256 447e07cb…不変)、strict schema(`added_word_mappings`)、item単位検証(`validate_item_corrected`: 「～」条件なし、真⇔不変の矛盾検出[空白・～/〜のみ正規化、採用値はcurrent原文])、追加語→span対応の機械検査(`check_added_word_mappings`: 多対一・重複可・句可・NFKC+空白除去の部分文字列一致、**record-only既定+gate判定を並記**)、item単位retry(`run_alignment_gate_corrected`: 2回目は未解決itemのみ、各itemは最初の有効出力を採用)、適用(`apply_alignment_corrected`: 未解決は`FAILED_HUMAN_REVIEW_REQUIRED`・KPを候補へ戻さない)、`collect_unresolved`、HR報告書(`emit_human_review_notice`: json+md、**書込後に再読してスキーマ検証、失敗は例外=fail-closed**)、`resolve_gloss`。`make_alignment_fn`に`schema`引数(既定None=従来)。`kp_adds_words_beyond_display`は関数抽出のみ(挙動不変)。 |
| `er003_v1_n3_01_scaffold_generate.py` | `run_key_phrase_canonicalization(..., gloss_alignment_mode=None)`(None=legacy)。`run_key_phrases(..., gloss_alignment_mode=None)`: corrected時のみ、外側retry確定後の**最終artifact**に対して1回HR報告(OF-KGDC-04)、`gloss_alignment_human_review_events`をresultへ、HR待ちがあれば`status=STOPPED_GLOSS_ALIGNMENT_FAILED`、専用stdout1行。legacyでは従来のcall形のまま(`_run_key_phrases_impl`/canonicalizationへmode引数を渡さない)。 |
| `er019_family_x_audio_production_runner_01.py` | 関所: `_generate_key_phrase_segments_a2/b1`がHR待ちartifactで当該level KP segment全体(A2: en/ja、B1: en/解説/phrase_repeat)を`STOPPED_GLOSS_ALIGNMENT_FAILED`(reason付き)で返す(0 API call、B1解説LLMも呼ばない)。assemble前チェック`_assert_no_gloss_alignment_hr`(`tts_generation_results.json`欠落でも拒否)。`_build_level_table`にpage多重防御。`run_theme_scaffold(*, gloss_alignment_mode="legacy")`(keyword-only=`__defaults__[-1]`のkp_backend契約を維持)、最終stdout`print_gloss_hr_final_line`(HRなし/legacyは無出力)。 |
| `er026_family_z_fiction_production_runner_01.py` | `E2EContext.gloss_alignment_mode`(既定legacy)。corrected時のみ: `stage_kp`でHR待ちなら報告書+run-level event(`gloss_alignment_human_review_events.json`)+snapshot保存後に既存`FamilyZE2EStop`。HR解消後の再開は**選定を再実行せずsnapshot復元**(`--regenerate-stage kp_<lv>`時は使わない)。`kp_expl_b1b`のsigにglossを含める(corrected時のみ=legacyのsigは不変でMelos完成物のprovenance互換を維持)。`load_level_inputs`(TTS/Gate/Assembly共有入力)にもHR待ち関所。 |
| 使わなかったもの | Human Review Lock(`er011_human_review_lock_01.py`)、`human_review_queue.jsonl`、`attempt_history.jsonl`、Audio Validation Gate(`er003_v1_n3_01_assemble.py`は無変更。新statusは非許可statusとしてUNVALIDATED扱い=`record_human_approval`の承認対象外)。 |

## 3. 撤去一覧(OF-KGDC (g))の扱い: 「correctedで不使用、legacyで残す」
撤去はcorrected側(=新経路は呼ばない)で行い、legacyの挙動は本委任では変更していない(ユーザー/Fable決定)。再列挙(`rg`、2026-10-15):

| 対象 | 場所 | correctedでの扱い | legacy |
|---|---|---|---|
| `SLOT_TOKENS` / `kp_has_slot_word` / `gloss_has_unjustified_slot` | gloss module 50, 227-235, 266 | 不使用(「～」条件なし) | 残す(`validate_alignment_response`が使用) |
| fallback(i) `revert_to_candidate_allowed` / `FALLBACK_REVERT_IF_SAFE` | 312, 44 | 不使用(KPは短い候補へ戻さない) | 残す(config選択時のみ) |
| `GLOSS_ALIGNMENT_FALLBACK_MODE`と`FALLBACK_KEEP_KP`、`apply_alignment`の`fallback_mode`引数/docstring | 42-48, 339 | 不使用 | 残す |
| 冒頭コメント20-22・46行 | 19-23, 45-46 | 末尾の「corrected節」コメントで「correctedでは不使用」を明記(旧文は変更せず) | 残す |
| `build_gloss_alignment_fallback_record`のnote / `write_failed_notice`(出力先`<run>/GLOSS_ALIGNMENT_FAILED_NOTICE.md`) / `format_failed_stdout` | 400, 455, scaffold 840 | 不使用(HR報告書`GLOSS_ALIGNMENT_HUMAN_REVIEW_01.*`と専用stdout行に置換) | 残す |
| 不整合出力をassertするtest(`test_failed_alignment_keeps_kp_flags_failed_not_human_review`等)・「～」禁止固定test(11件) | `er003_test_key_words_gloss_alignment.py` | legacy testとして**無変更で残す**。corrected用の新testを追加(36件) | 残す |
| 証跡スクリプト(`er071_gloss_alignment_01_replay.py`/`_census.py`/`er071_gloss_alignment_correction_01_offline_audit.py`) | 上記legacy記号を参照 | 改修しない。参照記号がすべて残っていることをtest(`test_evidence_scripts_still_resolve_legacy_symbols`)で確認(import破綻なし=shim不要) | 無変更 |

Grep全数(撤去対象7記号): gloss module内定義/使用、test 11行、scaffold 840行(write_failed_notice、legacy分岐のみ)、証跡スクリプト3ファイルのみ。Production runner(er019/er026)はいずれも参照しない。

## 4. OF-KGDC-01〜12 対応(詳細はOPUS_FINDINGS_LEDGERの該当行)
01 Lock不使用→関所status / 02 B1解説LLM・page停止 / 03 `resolve_gloss`+Z再開実証 / 04 最終artifactに対して1回 / 05 queue不使用+「届いた」4条件 / 06 機械検査の最小形(record-only+gate並記) / 07 P3から`put solo travel at`除外+census relabel / 08 P7追加 / 09 item単位retry / 10 真なら不変の正規化比較 / 11 実装せず別OPEN / 12 mode切替(Production既定legacy)。

## 5. 調査で確定した事実(Opus未確認事項への回答)
- (1) gloss消費元の全数: VALIDATION_02 §0。Production Family X/Zの経路に関所を経由しない呼出元は無い(page表示は`_build_level_table`が多重防御を追加、Zのpagesはassemble後=load_level_inputsの関所の先)。Legacy A/B/C(`er003_v1_n3_01_tts_generate`)はcorrected modeを受け取らない=HR statusのartifactが生成されない(対象外・一覧のみ)。
- (2) `w62.ensure_stage`: 出力ファイル+provenance entryが無ければ`runner()`を再実行する。runner内で例外(`FamilyZE2EStop`)になるとentryも出力も保存されないため、再開時は**選定から再実行**される(Opus推定どおり)。→ snapshot復元で選定を再実行しないようにした(T3 l-Z)。`run_kp_stage`は`fn(text,kp_dir,article_id,src_level,process=)`を呼ぶだけ(Zの既定kp_fnは`run_kp_with_outer_retry`でcanon_fnを差替可能)。
- (3) page/player: Xは`build_player_html`(stage player)がassemble summary=OKのlevelのtableのみ生成、assemble前にGate(+新チェック)が拒否。Zは`stage_pages`がassemble後。
- (4) `tts_generation_results.json`欠落: 既存Gate(`verify_episode_audio_validation_gate`)は即return(既存fail-open、無変更)。corrected artifactについてはX assemble前チェックが同じ理由で拒否(T3 o)。
- (5) 既存test群の位置: `er003_test_key_words_gloss_alignment.py`のみ(gloss_alignmentを参照するtest)。Production runnerのtestはRegression(er019/er026/er030/er063)で確認。

## 6. リスクと注意点
- corrected modeはTrial専用。Production既定をcorrectedにする/機械検査をgate化する/Human Review例外対応を正式採用するのはユーザー判断(未承認)。
- 停止粒度の使い分け(X=level内KP segment全体、Z=stage単位。Zでb1bが止まるとa2のKPも未実行)は設計どおり。
- 本変更はX runnerの関所コードをProduction runnerファイルに追加しているが、legacy artifactでは`collect_unresolved`が常に`[]`で何も起きない(T3 k-X/k-Z、Regression)。
- Family X `NG_REVIEW_REQUIRED`素通り(OF-KGDC-11)は実装していない(別OPEN)。
