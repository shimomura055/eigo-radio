# WIRING_DESIGN_01 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07、2026-10-25)

中核数値保持方式v4 + J2(範囲値の波ダッシュ正規化)の**Production配線設計**。ユーザー承認: 中核数値保持方式v4=APPROVED_FOR_PRODUCTION(`docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_04.md`)、J2=APPROVED_FOR_PRODUCTION(`..._USER_05.md`)。対象=Family X(Std/Adv)のみ。Y/Z対象外。承認済みTrial方式(`ADOPTION_NOTE_01.md`)を基本とし、品質基準・仕様は変えない。
配線実装の正本=`er116_fx_core_numeric_retention_01.py`(新Production module)+ 3 fileの最小編集。Trial(`er115_*`)は変更しない(残置)。

## 1. 変更ファイルと役割(Production)
| file | 変更 | 既定(新仕様を使わない呼出) |
|---|---|---|
| `er116_fx_core_numeric_retention_01.py`(新) | v4指示文(V2+欄指示)・`with_field_schema`(deepcopyへ欄)・M1構造検査(`derive_E`/`derive_E_from_field`)・較正済み照合(`match_core`)・O-2'(`plan_o2prime`/`swap_marks`/`filter_overlay`)・M2(`new_numbers`)・J2/R4(`normalize_ranges`)・`NumericRetention`文脈・EN観察(`observe_en`)。Trialの検証済み関数は**ソース同一**(testで1文字単位照合) | - |
| `er019_family_x_storyline_b3_fact_selection_01.py` | `_call_once`/`_technical_attempts`/`run_storyline_b3_selection`に`variant=None`引数を追加(user message末尾へ追記+schemaのdeepcopy変換)。`STORYLINE_B3_JSON_SCHEMA`定数・Prompt定数は**不変**(Y Trialのimport契約を保持) | `variant=None`=従来とバイト同一(test) |
| `er053_family_x_factlock_ja_writer_01.py` | `run_w1_writer(..., numeric=None)`と`JANumericRetentionStopError`(`JASymbolCheckStopError`のサブクラス)。規則5の文言・R0 Prompt・`USER_TMPL`は**不変** | `numeric=None`=従来とバイト同一(Trial/Y/Z) |
| `er019_family_x_entertainment_production_runner_01.py` | `run_storyline_b3(..., numeric_variant=None)`・`run_numeric_field_step`(M1+B3再実行1回)・`run_ja_writer`で`numeric=`を渡す・`main()`にv4 variant指定とEN観察 | `run_storyline_b3`既定`numeric_variant=None`(Y Trial `er110`が呼ぶ経路は不変) |

## 2. 委任文§2の1〜12 → 実装箇所
1. **欄の追加**: `numret.variant()`→`b3._call_once`が`variant["addendum"]`をuser末尾へ、`variant["text_transform"]`(=`with_field_schema`)でschema deepcopyへ`reader_must_hear_numbers`(array of string)を足す。送信バイト列はTrial `_AddendumClient`と同一(testで`D.B3_ADDENDUM_V4`/再実行文言と一致を確認)。reeval callにも同variantを付与(Trialのclientラッパが全createに付けたのと同じ)。
2. **E=欄**: `run_storyline_b3`が採用B3出力の欄を`storyline_b3/reader_must_hear_numbers.json`へ保存(`numret.save_field`)。`run_numeric_field_step`(注記producer直後・丸め判断の前)が`derive_E_from_field`でM1構造検査。違反かつ今回新規B3なら**B3を1回だけ再実行**(1回目artifactは`storyline_b3_attempt1`へ退避、修正指示=Trialと同じ`M1_RETRY_NOTE_V3_TEMPLATE`)。再実行後も違反→`mode=m1_final_violation_E_empty`(E=∅で続行、`[WARN][numeric_retention]`+`numeric_retention_b3.json`+W-1 evidence)。欄が空/欄ファイルなし=E=∅(Gate/O-2'/M2なし=現行動作)。
3. **保持Gate**: `run_w1_writer`のR0直後・R1直後・R2直後に`numeric.missing()`(較正済み照合)。不足時は既存の再生成枠(R0=記号QA再生成枠、R2=記号QA再実行枠、R1=新規1枠)を**共有で1回**使い、なお不足なら`JANumericRetentionStopError`(`rejected_w1_<stage>_numeric_{first,rerun}.md`+`runtime_evidence_stopped.json`)。**STOP先=既存のJA STOP枠**(`JASymbolCheckStopError`サブクラス→`runner.run_ja_writer`が`RuntimeError`化→EN/KP/TTS以降へ進まない)。*既存のText段にHuman Review専用キューは存在しない*(HRキュー`human_review_queue.jsonl`は音声ASR cascade用)。STOPは既存の技術QA STOP(`JA_SYMBOL_CHECK_STOP`)と同じ扱いで、人間が確認する。→ 0円testで「STOPがrunnerの既存STOP経路に入り、a2/b1b/TTSが生成されない」ことを確認(`test_stop_reaches_runner_stop_path_and_no_downstream`)。
4. **O-2'**: `NumericRetention.apply_o2prime`が契約検証済みnews欄/Factsの**メモリ上コピー**の`【中核数値】`印だけを`【周辺数値】`へ付け替え(年系・別単位系・単位不明は残す)。`overlay`から該当【概数表記】行を除く。注記済みB3ファイル(契約sha)・規則5文言・R0 Promptは不変(testでファイルshaを前後比較)。`gate_E`が空ならno-op。
5. **M2**: `numeric.missing(..., m2=True)`をR1/R2に適用(R0本文+ニュース欄に無い数値表記)。再生成枠は保持Gateと共有。
6. **J2**: Writer入力(R4=`normalize_inputs`、Prompt本体の固定部は不変)と出力R0/R1/R2(`normalize_output`、記号QA・Gateより前の決定論後処理=`run_w1_writer`内1か所)。`numeric`が渡れば常に有効=**R5/欄/E=∅に依存しない**(E=∅記事にも適用)。件数と変換前shaをevidenceへ。TTS Normalizer(`er003.normalize_tilde_placeholder_ja`)は残置(使い捨てコピー・役割別)。J2が先に「から」へ変換するため、範囲値ではNormalizerの「なになに」欠陥が表に出ない(OPEN-509に記録)。数字以外の波ダッシュは触れず、記号QAが従来どおり検出(test)。
7. **retry/resume/再生成**: (a)B3再実行1回はM1違反時のみ・新規B3のみ。(b)`--regenerate-stage writer`や途中段再開はB3を呼ばず、`NumericRetention.from_out_dir`が保存済み`reader_must_hear_numbers.json`+注記済みB3からEを**決定論で再構成**(API 0)。(c)欄ファイルが無い旧記事=E=∅。(d)`--regenerate-stage storyline_b3`は新B3(欄つき)。(e)U-1来歴検査(`load_reused_ja_text`)は不変。
   **記事あたり費用上限**: runner既定`--budget-jpy 150`(`efam.assert_budget_ok`をB3後・M1再実行後・W-1各段前後で呼ぶ)。最悪ケース(追加): B3再実行≈12 + R0再生成≈7.8 + R1再実行≈3.6 + R2再実行≈2.5 = **約26円**(基準: `FXMS RUNTIME_EVIDENCE_01`のR0 7.79/R1 3.63/R2 2.51/B3 12.07)。基準text 約50円(research/ledger込み)+26 ≒ 約76円 < 150円。収まる。超過見込み時の挙動は既存どおり`assert_budget_ok`がSTOP(迂回しない)。
8. **runtime evidence**: `storyline_b3/numeric_retention_b3.json`(b3_rerun・attempts[違反理由・欄の1回目/最終値]・mode・E)、`storyline_b3/runtime_evidence.json`の`numeric_retention_b3`(variant sha・欄)、`ja_writer/numeric_retention.json`(mode・E・gate_E・O-2'付替え・J2適用箇所/件数・段別retention/new_numbers・R4入力変更・WARN)、`ja_writer/runtime_evidence.json`の`numeric_retention`+各call(model・response_id・prompt sha)、`ja_writer/numeric_retention_en_observation.json`(EN Std/Adv)。routingはW-1既存(`FAMILY_X_FACTLOCK_R0`/`_REVISE`、B3は`FAMILY_X_STORYLINE_B3`)をそのまま使い、実際のmodel_idを記録。
9. **Gate経路の担保**: `er116_fx_core_numeric_retention_01_test_01.py`(45 test)。Gate発火→再生成→STOP、E=∅(欄なし/空/M1最終違反+WARN)、J2正規化、resume再構成(B3 API無し)、旧記事E=∅、M1→B3再実行1回、Trial保存済み14標本のE/O-2'再適用(Trialとの完全一致)と保存済み最終本文へのProduction Gate適用(不足0・新規数値0)。
10. **撤去・残置**: Productionへ移したのはv4・M1構造検査・E=欄・Gate・O-2'・M2・J2(+R4)のみ。v1〜v3指示文・Storyline由来E(`derive_E`のsurfaces=None経路)・RULE9・`resume_w1_dev_from_r2`・C-1(`field_priority_*`)はer115に残置し、er116はer115をimportしない(AST test)。旧処理で不要になったもの: なし(旧Production W-1の記号QA再生成/再実行枠は共有して維持。重複検査は作っていない)。
11. **C-1**(欄をderive_ranks優先に加える最適化)は配線しない(検証済みv4からの挙動変更)。後続改善候補としてOPEN-507に記録。
12. **半導体型の初回選定傾向**: 指示文追加なし。`numeric_retention_b3.json`の`first_pass.field_items`に欄の1回目値を記録し、最初の数記事をFableが確認(受入観察事項)。

## 3. O-2'の単位系の穴(`ADOPTION_NOTE_01 §2-3`、分類=修正へ進む)
`dimension_of`が桁付き通貨(億ドル等)を通貨系へ写像しないため、E=167億ドル+217億ドル型でO-2'は休眠(非E中核は従来どおり残る=現行Production同等で悪化なし)。検証済みv4からの挙動変更になるため今回は配線せず(11と同判断)、DEVで写像を足して9標本に再適用する後続委任を推奨。

## 4. 既定動作の整理(確認はtest)
| 状態 | mode | Gate/O-2'/M2 | J2/R4 | 備考 |
|---|---|---|---|---|
| 新規B3・欄に数値・M1合格 | field_ok | あり(gate_Eがあれば) | あり | v4標準経路 |
| 欄が空 | field_empty | なし | あり | 現行Production+J2 |
| 欄の数値が時間前提のみ | field_observe_only | なし | あり | 観察のみ |
| M1最終違反(再実行後) | m1_final_violation_E_empty | なし | あり | WARN+evidence |
| 旧記事(欄ファイルなし) | legacy_no_field | なし | あり | 現行Production+J2 |
| `numeric=None`(Trial/Y/Z) | - | なし | なし | 従来とバイト同一 |
flag・環境変数でON/OFFする経路は無い(承認済みのため)。Y/Zはer116/`numeric=`/`variant=`に到達しない(test_isolation)。
