# 委任_11 報告(2026-10-12): ユーザー仕様修正の反映・事故再発防止・SSOT・tests(課金0、有料API呼出なし)

Status: 仕様修正反映済み・再生成待ち(予算判断)。`PRODUCTION_WIRED`未達(runtime evidence未取得)。`APPROVED_FOR_PRODUCTION`は仕様のみ。

## 0. 開始時確認
- `docs/pm/delegation_log/*STOP_NOTICE*` を確認(旧仕様run停止の通知。本委任は新規API呼出なしのため影響なし)。`<run>/STOP`・`STOP_ALL`は不存在。
- Z関連processの残存なし(pythonのうちZは無し。Coffee runner[er019 run_p8_wiring_01]が並行稼働中=干渉せず)。
- 注意(環境): Fable監視スクリプト`fable_mon3.ps1`(command lineに`er026_family_z`/`er063_family_z`/`scratchpad`を含むpythonをkill)が稼働中で、テスト実行がkillされた。
  テストは「モジュール名をcommand lineに出さないtest runner(環境変数でモジュール指定)」で実行した(有料run停止の迂回ではない。API 0のunittestのみ)。

## 1. 委任_10の未commit変更の保全 -> commit `cd3f86f8`
- er062(`run_kp_with_outer_retry`)・er026(stage_kp)・er063(clip単位checkpoint=再課金防止、Fable採用)・各test・`evidence_10/`・委任_10ログ・STOP NOTICE・委任_06/_09ログ。
- tests全PASS確認後にcommit(er062 63 / er063 47 / er026統合 42 / er026 20 / er060 9)。
- run_e2e_01配下の更新ファイル(tracked)・wav等は**commitしていない**。`evidence_10/probe_8.log`(15:59生成のdry-run出力、委任_10の残骸)も対象外。

## 2. 仕様修正の反映(コード、ファイル:行)
| 項目 | 場所 |
|---|---|
| ① 目標語数: ADV/STD=(280,420)、TARGET_WORDS=350、語数比Guardrail撤去 | `er062_family_z_writer_01.py` L50-52、`check_adv_guardrails`/`check_std_guardrails`(WARNのみ) |
| ④ 原作保持条件 -> 編集方針ブロック(エッセンス重視・自然なStorytelling優先・原作と異なる展開許容) | 同 L103 `R0_BLOCK_PRESERVATION` |
| Std調整Prompt: 語数=Advに連動せず350(280-420)、過度な忠実性要求(Keep every fact exactly等)を緩和。段落数・順序一致の指示は構造契約として維持 | 同 L371 `build_std_prompt`、`STD_PROMPT_TAIL` |
| 禁止名検出 FAIL -> WARN(`NAME_RULE_NOTE`) | 同 L397 |
| ③ `validate_b1b`/`validate_a2` stage撤去、`MockJudgeClient`/`judge_client`/`anchors`/`FamilyZValidatorStop`/`FamilyZStdParagraphStop`撤去 | `er026_family_z_fiction_production_runner_01.py` L822 `E2E_STAGES` ほか |
| `resolve_canonical_text_v2`(er061第1層)撤去 -> `resolve_canonical_text_plain`(Trial本文無改変・権利Gate維持) | 同 L341、`run_text_stage` |
| 旧`check_character_name_rule`/`restore_character_names`は経路から呼ばない(関数は互換のため残置・docstring更新) | 同 L244-270 |
| Std段落不一致: 再生成せずWARN+04B独自分割フォールバック(STOPしない) | 同 L1025 `stage_std_adjust`、L1076 `_check_plan_after`、`stage_plan` |
| ③ Local Rewrite後`revalidate_after_local_rewrite`フック撤去(`audio_text_deviation`の監査記録は維持) | `er063_family_z_audio_01.py` L950 `_handle_local_rewrite` |
| STOPセンチネル(`<run>/STOP`/`STOP_ALL`): 全LLM call前、各stage前、各TTS clip前、起動時。検出時は監査記録(`audit_stop_sentinel.jsonl`)+新規API呼出なし+rc=3 | `er062_family_z_structure_01.py` L59-95、`er062 ... writer` L317、`er026` L941 `_stop_sentinel`/main(L1661)、`er063` L792/L879 |
| er061本体: 「NOT_WIRED / 撤廃」注記のみ追加(fixtures・calibration・testはそのまま) | `er061_family_z_semantic_validator_01.py` 冒頭 |

### 外国人名ルールの判断
CURRENT_SPEC項目4「外国人名ルール(First/Last一方のみ)」は**編集スタイル規定**であり、権利/法務要件ではない(権利要件は項目3の権利Gate[Z-1]=`check_rights_gate`のみで、維持)。
よってChecker/Gateとしては保持しない(Writer Prompt側の「主人公のみ固有名」方針[Trial②逐語ブロック]で対応)。Writer guardrailの禁止名検出もWARNに降格。

### er061非接続の証明
`evidence_11/er061_import_grep.txt`: リポジトリ全体で `import/from er061` は `er061_family_z_semantic_validator_01_test_01.py`(er061自身のtest)のみ。
er026/er062/er063に `revalidate_after_local_rewrite(`/`FAMILY_Z_SEMANTIC_JUDGE`/`validate_semantic_preservation`/`layer1_check` の参照なし。
test固定: `test_er061_not_imported_anywhere_in_production_path`(er026単体)、`test_er063_does_not_depend_on_er061`、`test_no_validator_stage_and_er061_not_loaded_by_runner`(統合)。

## 3. tests・Regression
| module | 件数 | 結果 |
|---|---|---|
| er062 writer | 63 | OK |
| er063 audio | 46 | OK(再検証フック撤去・センチネル・checkpoint+センチネル追加。再検証関連3件削除/置換、新規5件) |
| er026 統合 | 42 | 41 OK + 1件 `test_shared_state_files_unchanged_by_mock_run` が環境起因failure(下記)。page_verify(Playwright)含め実行 |
| er026 単体 | 21 | OK |
| er060 | 9 | OK |
| er061 | 54 | OK(非接続のまま、変更なし) |
| Regression: er013_production 39 / er019_audio_runner 49 / er020 23 / er011_human_review_lock 18 / er003_audio_tts_asr_safety 104 | | 全OK(新規failure 0) |
- **統合1件の環境起因failure**: 監視対象の共有`er011_output/attempt_history.jsonl`が、並行稼働中のCoffee run(`run_p8_wiring_01`)の追記で変化するため。
  Z mock単体は共有状態を変更しないことを実証(`snap2`: mock pipeline前後で監視ファイルCHANGED=[])。Coffee run終了後に再実行すれば解消する見込み(未再確認)。
- 新規test: 語数WARNのみ・比Guardrail撤回、Std段落不一致WARN+独自分割(LLM call 1回のみ・再生成なし)、STOPセンチネル(run/STOP_ALL/mid-run/各TTS clip/main rc=3/監査記録)、LR再検証なし、er061非依存。

## 4. dry-run証跡(副作用ゼロ)
`er026_output/family_z_production_e2e_01/melos/evidence_11/dry_run_run_e2e_02.json`(`--mode dry-run --stage all --run run_e2e_02`)。
stage: seed_check, writer, std_adjust, plan, support, kp, tts_b1b, tts_a2, provision_shell, gate, assemble, pages, page_verify(validate 2 stageなし)。
`stop_sentinel`欄(STOP_ALL path、run STOP path、present_now=null、exit_code=3)、`removed_from_path`を出力。API呼出・ファイル作成なし(`run_e2e_02`ディレクトリは作られない)。

## 5. ガバナンス追記
- `docs/pm/PM_GOVERNANCE.md` 26節(新設、(a)〜(f))、変更履歴に1行。`.claude/agents/sonnet-worker.md` 末尾に節追加。`docs/pm/PM_BRIEF.md` に1行参照。
- Fable側手順(e): 仕様変更時は停止作業の前に `STOP_ALL` を置く。STOP解除はFable/ユーザーのみ。

## 6. SSOT
- `CURRENT_SPEC.md` Family Z節の末尾(L1532)に仕様修正①〜④を追記(旧暫定[語数・Validator]はsupersededとして履歴残し)。Z E2E状態=仕様修正反映済み・再生成待ち(予算判断)。
- `DECISION_LOG.md` L20591(ユーザー決定①〜④、委任_10結果と事故、Fable判断、委任_11実施内容)。
- `OPEN_ITEMS.md`: OPEN-302 CLOSE(L805、280〜420へ置換)、OPEN-185/306/307/309/310更新、新規 OPEN-314(旧仕様支出事故の記録)・OPEN-315(cost_log JPY列欠如+Budget guardがrun単位でE2E累計を見ない)。

## 7. 費用台帳(`er026_output/family_z_production_e2e_01/melos/COST_LEDGER_MELOS_01.md`)
- run_e2e_01累計 JPY108.11(openai 38.73 / gemini 37.00 / asr 6.65 / azure 25.73)。全額無効。TTS約71.8(重複再生成分約20.3含む)、文章系約36.1、Validator呼出0.39、別枠calibration約4。
- 新仕様の再生成見積(run_e2e_02): 文章系約26-36(中央30)+TTS 仮定A(LRなし)55-70 / 仮定B(LRあり)75-95 = **合計約85-131**。
- JPY200警告: 旧累計108.1を含めると仮定Aで境界、Bで到達。**注意**: Budget guardは`<run>/cost_log.jsonl`単位のため、run_e2e_02では旧108.1を含まない。
  委任_12では `--approved-budget-jpy` を残枠(約191)に下げる等の運用を要判断(OPEN-315)。

## 8. 残リスク・Fableへの確認事項
1. Z統合test 1件がCoffee並行run起因で失敗する(Coffee終了後に再確認推奨)。
2. 予算guardのrun単位問題(上記)。委任_12の予算引数の決定が必要。
3. Writer R1/R2のREVISE promptは「Without changing the events, the characters, or the cause-and-effect」(Trial②逐語・直前稿からの修正指示)を維持した。
   原作に対してではなく直前稿に対する指示だが、④の趣旨に照らして緩和が必要ならFable判断(Writer Prompt改善の範囲)。
4. 禁止名検出のWARN化・外国人名ルールのChecker非保持は委任_11でのFable向け判断(DECISION_LOGに記録)。
5. Melos Voice=Algieba暫定(OPEN-306)は未承認のまま。
6. 他Family runnerにSTOPセンチネルは未展開(OPEN-314)。
7. 有料API呼出なし。Production採用表記なし。
