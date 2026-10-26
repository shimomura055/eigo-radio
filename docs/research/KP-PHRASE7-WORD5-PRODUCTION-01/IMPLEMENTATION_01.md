# IMPLEMENTATION_01: Key Phrase最大7件 + Key Word最大5件 分離抽出のProduction配線(実装記録)
KP-PHRASE7-WORD5-PRODUCTION-01 委任_02 / 2026-10-27。到達Status=**IMPLEMENTED**(API 0。実API evidenceは`EVIDENCE_01.md`)。PRODUCTION_WIRED判定はFable。設計=`DESIGN_02.md`(Opus条件A M-1〜M-9・R-2〜R-6反映、D1〜D6)、撤去/残置=`REMOVAL_RESULT_01.md`。
実装commit: `Delegation: KP-PHRASE7-WORD5-PRODUCTION-01/02`(hashは`RESULT_PACKET_KP75B.md`)。

## 1. 変更ファイルと主な差分(ファイル:行は実装後)
| ファイル | 変更 |
|---|---|
| `er119_kp_p7w5_prompts_01.py`(新) | `P7_TEXT`(`ft.PROMPT_2_TEXT`から冒頭の件数文と条件6だけ置換=Trial-02と同一の生成式、sha`2e930193…`をassert)、`W5P_TEXT`(Trial W5の補足行1つをユーザー原文逐語へ、sha`12d33708…`をassert)、`KP_PHRASE_MAX=7/KP_WORD_MAX=5`、message builder、`make_p7_selector_fn`/`make_w5_selector_fn`(先頭一致を満たさないmessageは`FulltextSelectionError`=fail-closed)、`PromptSpec`/`SPEC_P7`/`SPEC_W5P`。**er124非import**(testで固定) |
| `er105_kp_fulltext_selector_01.py` | keyword-only・既定=従来: `build_user_message/prompt_prefix_intact(prompt_text)`(:109)、`validate_and_resolve(max_items)`(:226)、`apply_exclusions(max_items)`(:402)、`build_exclusion_note/build_machine_note(limit)`(:392,:368)、`run_selection_gate(prompt_text,max_items,parse_fn)`(:464)、`run_fulltext_selection(…,prompt_id,prompt_sha256)`(:551)。`reason_ja`はキーがある時だけ通す(:269,:306)。**Prompt 2経路はバイト同一**(testで固定) |
| `er119_kp_candidates_01.py` | `select_p7`(:291、M-9 telemetry)、`_enforce_kind_caps`(:316)、既定`select_fn or select_p7`(:350)、call2=`run_vocab_selection(spec=SPEC_W5P)`(:387)、`run_vocab_selection`一般化(:49、`not_single_word`:108)、call1の`reason_ja`を候補へ(:`meta`)、`gate_dropped`を`bf.GATE_DROP_EXEMPT_STAGES`参照(:429)、doc`prompt_ids/prompt_sha256`=P7/W5'、`_shortfall_detail`に`cap_by_kind/missing_by_kind`(:498)、`_run_backfill`全面改訂(:529: 種類別・直列・各1回、`backfill_duplicate`=M-4) |
| `er119_kp_backfill_01.py` | `PHRASE_CAP/WORD_CAP`、`NOT_COUNTED_STAGES`に`overflow_kind`、`GATE_DROP_EXEMPT_STAGES`、`count_exclusions`の`not_single_word`=word固定(:123)、`plan_quota(counts,n_phrase,n_word)`(:131)、`pick_backfill`=quota(:144)、`rejected_entries(for_kind)`(:171)。`BACKFILL_MAX_CALL_ITEMS`撤去 |
| `er119_kp_human_review_01.py` | `KP_CANDIDATE_MAX = 8 → 12`(:52、**1行のみ**。KCP 02A(`246093175`)のcommit後に変更) |
| `er106_joint_runtime_evidence_01.py` | `kpft_expected(prompt_id)`・KPFT-3/4を`prompt_id`別(M-6)、`collect_kp_selection`に`prompt_id`追加 |
| test | `er119_kp_p7w5_test_01.py`(新31件)、`er119_kp_p7w5_e2e_test_01.py`(新8件)、`er119_kp_backfill_test_01.py`(改訂65件)、`er119_test_support_01.py`(harness M-5)、golden_03、`er119_kp_human_review_01_test_01.py`/`_cli_`/`er119_kp_rescue_wiring_test_01.py`/`er105_*_test`(許可リスト)/`er106_*_test`(改訂) |
| 触っていない | `er003_v1_n3_01_scaffold_generate.py`(telemetryは`select_p7`内で記録)、`er125`、`er108`、canonicalization/gloss template、runner(`er019/er121/er026`)、`_gate_chain`(**無変更**: `git diff`で関数本体差分なし)、`user_test/selection_form_v3/**`、`export_form_data_01.py`(`cap`既定8→12はフォーム側へ引継ぎ) |

## 2. 方式差の記録(Opus O-1)
Trial-02のP7はループなし・不適合itemだけ落とす方式(`er124:221-267`)。Production化では承認済みcall1仕様の**attempt loop(MAX_ATTEMPTS=2、1件でも不適合なら全件再選定)を維持**(`select_p7`→`er105.run_fulltext_selection`)。K1(item単位化)は導入しない。件数不足は不適合でなく再選定は起きない(`test_four_items_are_not_a_nonconformance_no_retry`)。

## 3. test結果(実行ログから)
| 範囲 | コマンド | 結果 |
|---|---|---|
| er119全体 | `run_project_regression.py --pattern "er119_*_test_*.py"` | collected=252 passed=250 failed=2。失敗2件は**着手前から同一**(baseline: 203件中2件失敗=`er119_grammar_review_test_01.test_grammar_files_not_tracked_dirs`・`er119_isolation_test_01.test_only_x_z_runners_import_er119`[Y runner/Trial moduleがer119をimport]。本件起因でない) |
| er105 | `--pattern "er105_*_test_*.py"` | 52/52 PASS(Prompt 2経路のバイト同一test含む) |
| er106 | `--pattern "er106_*_test_*.py"` | 38/38 PASS(prompt_id別KPFT-3/4追加) |
| er125 | 同 | 58/58 PASS |
| er030(X production wiring含む) | `--pattern "er030_*test*.py"`(`_test`を含む名のみ) | 92/92 PASS |
| er121(Y) | `--pattern "er121_*_test_*.py"` | 369件 368 PASS・skipped 1・失敗0 |
| er019(X) | `--pattern "er019_*_test_*.py"` | 552件 551 PASS・失敗1(`er019_x_std_chunk_opus_test_01.R4HunkClassifierTest`=er019 runnerのgit diff分類test。本件でer019は無編集=無関係) |
| er026(Z) | `--pattern "er026_*_test_*.py"` | 224件 220 PASS・skipped 2・失敗2(`DryRunAndCliTest.test_dry_run_*`=実リポジトリ出力dirのsnapshot比較。並行Agentの出力書込みでずれる環境依存。本件の変更ファイルを含まない) |
| er108 | 同 | 37件 36 PASS・失敗1(`Importers.test_cmu_gate_is_imported_only_by_x_z_shared_kp_path`=Trial `er123/er124`がer108をimport。baseline既存) |
| 参考(KCP並行Agent) | er128 | 並行Agent(a)の作業中(`er128`等が未commit)。本件起因ではない |

## 4. R-3 予算見積の確認(Y/Z `STAGE_EST_JPY["kp"]/2`)
`er121_family_y_runner_01.py:575`・`er026:1995`の`guard_fn`は**候補生成roundごとの予算残の事前guard**(¥5)であり実費の上限ではない。7+5の1 level実費はTrial-02実測で約¥1.9〜2.2(現行3+5比+約¥0.24)。最悪(外側retry 3周×attempt再選定+補完2 call)でも約¥8で、次round・final redundancyのguardが`ctx.budget`で止める構造は不変 → **更新不要**(runner非編集)。実測は`COST_01.md`。

## 5. 残存Grep・既定値確認(RESULT_PACKETの(2)(4))
- 新flag無し: `grep -rn "EIGO_KP_P7\|EIGO_KP_WORD5\|EIGO_KP_3PLUS5\|EIGO_KP_LEGACY"` → 0件(testで固定)。`er119_kp_p7w5_prompts_01.py`・`er119_kp_candidates_01.py`に`os.environ/getenv`なし(test固定)。
- 既定ON: `select_fn or select_p7`(`er119_kp_candidates_01.py:350`)・`spec=p7w5.SPEC_W5P`(:387)。`EIGO_KP_BACKFILL`(既存kill switch、補完のみ)は種類別補完でも従来どおり。
- 撤去: `REMOVAL_RESULT_01.md`。

## 6. 既知の限界・観測事項
- **R-1(既知の限界)**: 基本形化後の`used_form`同士の含有は確認しない。語形違い(price/prices、push/pushed、所有格、ハイフン語)でKey WordがKey Phraseの語を含む場合は、選定表層形でのGate`duplicate_of_top3`とW5'本文の除外指示だけが防御。evidenceで実測(`EVIDENCE_01.md`)。
- 補完phrase/wordは**直列**(M-7、並列化は未実施)。
- Opusが推奨したE_wordに`duplicate_of_top3`を数える挙動(R-6)は承認仕様どおり。W5'の含有語漏れは単語補完callになる(頻度はevidenceで監視)。
- runner内の古いコメント「候補(最大8)」(`er019:800`、`er026:2018`)・mock候補生成`n_max=8`(`er026:2792`)は表記のみ(runner非編集)。
