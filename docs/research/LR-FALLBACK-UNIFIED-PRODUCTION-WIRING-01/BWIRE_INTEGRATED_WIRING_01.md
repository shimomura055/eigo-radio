# 委任_11(B-wire) 統合配線 成果物(実装、API 0、1 commit)

## 1. 配線点(file:line)
| 項目 | 配線先 |
|---|---|
| 三者一致Gate(er132) | X `er019_family_x_audio_production_runner_01.py:2581,2841`(assemble入口 b1b/a2、`assemble_gate_summary`、`japanese_title`は`not_rendered`記録)/ Y `er121_family_y_audio_01.py:1206` / Z `er026_family_z_fiction_production_runner_01.py:2552`(`z_assemble_gate`) |
| X M3の分類核切替 | `er019_family_x_style_profile_01.py:750`(`m3_assembly_gate(level_dir=)`、`override_violations`。runnerのcallが`level_dir=out_dir`を渡す) |
| Y style gate切替 | `er121_family_y_audio_01.py:934`(FULL_STORY chunk)・`:979`(JA role)。`lr_fallback_warnings`を結果へ追加 |
| Z style gate切替 | `er063_family_z_audio_01.py:2192-2197`(`_z_row_for_clip(ledger_clips=)`、`style_actual`記録を持つentryのみ。旧runは遡及判定しない) |
| 分類核(新規追記) | `er130_adopted_take_classifier_01.py`末尾: `X_REPLACED`/`Z_REPLACED`/`event_ledger_clips`/`override_violations` |
| B6 Z style_actual | `er063_family_z_audio_01.py:2011-2051`(`_adopted_take_for_style_actual`、`build_style_actual_record`が`er129.resolve_adopted_take`で採用attempt同定。`adopted_identification`欄) |
| 共通表示部品(新規) | `er133_report_marks_01.py`(er129 ledger+er131 `_card`/`_op_spans`のみ。独自の採用判定なし)。描画`er_user_listening_page_common_01.py`(`render_marked_script`/`script_block(marks=)`/`kp_block(cell_marks=)`)|
| 部品の配線 | X `er019_family_x_listening_page_01.py:105-126` / Y `er121_family_y_audio_01.py:1530-1579` / Z `er063_family_z_audio_01.py:2531-2684` |
| overlay(patch) | X runner `_build_level_table`/`resolve_x_highlights`、Y/Z `display_text_of_clip`(topic_introはclip overlayへ接続) |
| X事後試聴LR行 | 非表示にせず赤(`color:#c00000`)で表示(改定5') |
| Z旧注記 | 旧「Local Rewrite採用」注記(`row["notes"]`)を撤去し共通部品の注記(赤/濃青+範囲)に置換(改定4') |
| allowlist | er129 test u8(`er130/er131/er132/er133`+配線先)を明示列挙 |
| er131最終報告CLI | E2E_STAGES非追加。運用: 完了後に `python er131_final_human_report_01.py <results_path> ...` をCLI1行で任意実行(本委任では配線しない) |

## 2. 撤去(Dangling Referenceなし)
- 旧公開ページ「⏸なし」規則(audience=public時に⏸を出さない)・`FAMILY_Y_PUBLIC_PAGE_HAS_CHUNK_MARKER` STOP・`check_page`の旧public marker/leak検査(新仕様=⏸/赤/青は全audienceで表示。audienceは出力ファイル選択のみ)。
- Z旧LR/Fallback注記2か所。旧Style由来違反(`X_REPLACED`/`Z_REPLACED`の各code)は「台帳で正常と分類された採用takeのみ」置換、異常/UNKNOWN/記録なしは旧違反を維持(fail-closed)。
- 旧ruleのtest(er_page_audience_marker/er_learning_highlight/er026・er121 highlight wiring/er132旧公開前提 等)は新規則へ書換え。残存Grep: `FAMILY_Y_PUBLIC_PAGE_HAS_CHUNK_MARKER`=配線対象に0件、`Local Rewrite採用`=er131(LEGACY検知用)・er132(旧注記検知regex+「出さない」assert)のみ。

## 3. 差分監査(配線後の実Gate呼出、読取専用、`BWIRE_audit_01/audit_wired_gate_01.py`、結果`diff_{X,Y,Z}.json`・`summary_01.txt`)
旧=台帳なし(UD-3前)、新=配線どおり。X 134run/1357行・Y 31run/574行・Z 128run/3628行、エラー0。
- 旧BLOCK→新PASS(LR_APPLIED警告): X ai_island_temple/run_form_prod_01 a2・b1b `full_story_part1_k2`(LOCAL_REWRITE_RECOVERY(+STD_FALLBACK)解除)、Y run_tru_ev_y_adv_4b `y_voice_1`(LOCAL_REWRITE_RECOVERY解除)。いずれも正常LR。
- 旧PASS→新BLOCK(厳格化): X 0 / Y 0 / Z 0。偽BLOCK 0。
- 旧BLOCK維持: 台帳なし旧run(aho4_h1b等)・STYLE_BASE_SHA_MISMATCH等の異常は新でもBLOCK(fail-closed)。Z run_reselect_01/voice_*のZ_STYLE_ACTUAL_UNRECORDED(`full_story_part2_c1`等)は旧新同一(今回導入でなく従来から。OPEN候補A)。
- 告げ口心臓 Adv kp2_en(ENGLISH_LOCK): run_reselect_01/voice_fenrir_01/voice_schedar_01 b1b とも新=PASS+FALLBACK_APPLIED警告(M-10)。a2はFallbackなし。旧run(style_actual記録なし)は旧新ともPASS。
- Word Gacha Adv/メロス_02/猿の手Std/他: 変化なし(PASSのまま、または台帳なしで旧判定維持)。

## 4. mock E2E(`er130_gate_wiring_mock_e2e_01_test_01.py` 8件PASS、API 0)
X: LR→PASS_WITH_WARNING(HR非要求)/異常Style(STYLE_BASE等)→BLOCK/台帳なし→従来どおり。Z: ENGLISH_LOCK kp_en Fallback→警告通過・異常mock→BLOCK・記録欠落→遡及判定しない・B6がresolve_adopted_takeで同定。Y: 証跡runでLR→警告通過。
parity不一致: `assemble_gate_summary`が不一致を技術STOP(HRなし)とすることをer132 test(49件PASS)で確認。X mockではledgerがentry.canonical_textへ退避するため配線mockではverdictをSTOP_PARITYへパッチして停止を確認(制約として記録)。

## 5. ページ実測(保存run読取、scratch出力、run dir不変・2回生成で同一hashを確認)
- Z 告げ口心臓 run_reselect_01: advanced.htmlの⏸=2(plan境界)・Fallback濃青注記あり、standard=⏸2、再生成で決定的。run dir・公開ページ`user_test/family_z_tell_tale_heart_reselect_01`はgit差分0(未再生成)。
- X part2_hr_evidence_01群: 実chunk plan境界⏸=6/12。ai_island run_form_prod_01は旧run由来でassemble=BLOCKED_STYLE_PROFILE_GATEのためページ生成不可(従来どおり、PageStop)。LR赤はer133 test(AI島ledger照合)で確認。
- Y: wav未保存のため保存runからのページ全体生成は**未確認**。FullMockRun(⏸=実plan境界)と共通部品testで確認。A/B/C Family: **未確認**(PRODUCTION_WIREDとは呼ばない)。

## 6. test
- 新規: er133 12件/er130 mock 8件。更新: er129/er130/er131/er132(49)/page_audience(14)/highlight系。変更関連: er026 highlight+er121 runner 101 PASS。
- 全回帰(458ファイル、6分割): 失敗は全てbaseline既知(OPEN-543系・git-clean系・Fenrir voice・er019_fx AbcGolden 等)。直列再実行で14ファイル中の失敗12件は全てbase既知と同一。並列実行起因の見かけ上の失敗(er063/er117/er121 gate系、er026 e2e `test_shared_state_files_unchanged`)は直列で解消。`er026 e2e DryRun`は別worker(voice_fenrir_01)の並行書込でer026_output mtimeが変わる環境要因。
- golden: er026 melos golden index.html/他html byte同一(⏸と凡例1行を除く)、er109 wiring golden等PASS。
- 混入: er133 testがTTS入力・ASR正解・Style Prompt・KP学習表示・study_textへの混入0を確認(試聴ページHTMLは対象外)。

## 7. 新規OPEN候補
- (a)Z run_reselect_01/voice_*の`full_story_part2_c1`等`Z_STYLE_ACTUAL_UNRECORDED`(旧新同一): 実害なし(完了済みrun、再Gate対象外)。
- (b)er019_fx AbcGolden readers allowlistにer129/er131未登録(B2/B5由来の既存失敗): 修正へ進む(allowlistへ追記、次委任で)。
- (c)Y保存run由来のページ全体E2Eとワ A/B/C Familyページ: 未確認→B7/B8で記事単位に確認(修正へ進む)。
