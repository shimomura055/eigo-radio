# IMPL_E_01 委任_04E(E班): Family Z の本文ハイライト・③訳リスト・Standard Part 1 stage level化・Validator・page_verify G3
API 0 / JPY0。設計=`DESIGN_03.md`(§A-3/A-4/B/C/D/E)・`CONTRACT_03.md`。A班実装(commit 22f3a09ef)の署名・class `lk-meaning`・原因コード(`HL_*`のA実装名)に合わせた(CONTRACT_03との相違はRESULT_PACKET_S23E(4))。B班APIはcommit 374cfc941で着地済みのものを使用(待機0分)。
**マーク発行(`new_review`接続)はしない(M14)・実run/再ビルド/公開はしない。** 表示有効化は確定レコードの`display_spec`(`er128.display_spec_of`)のみ。マーク無しの旧run=従来とバイト同一。

## 1. 変更点(file:line)
| ファイル:行 | 変更 |
|---|---|
| `er063_family_z_audio_01.py:2487` `full_story_display_units(run_dir, level)` | ページに表示されるFull Storyクリップ台本をPart別・公開順のDisplayUnit列にして返す(timeline+`tts_generation_results.json`の`canonical_text`のみ読む。mp3/wav不要=API 0・副作用0)。 |
| `er063…:2507` `highlight_block_html(result)` | 台本表の外に置く付随ブロック(`<style>HIGHLIGHT_CSS</style>`+凡例1行+`ul.lk-meaning`の③訳リスト)。装飾も③訳も無ければ`""`。 |
| `er063…:2520` `_user_page_rows(…, highlights=None)` | Full Story各クリップの`script_block(g["script"], chunk_texts, audience, highlights=…)`。クリップをまたぐ語句は片ごとに同一`data-hl`(A班`highlights_for_text(result, unit_key, text_index)`)。**解決に使った表示台本と描画する台本が1文字でも違えば`FamilyZAudioStop(HL_DISPLAY_UNIT_MISMATCH)`**、ハイライト対象のunitがページに無ければ`HL_DISPLAY_UNIT_MISSING`。`⏸`(dev)は`script_block`内でハイライトの外。 |
| `er063…:2611` `build_pages(…, highlights_by_level=None)` | 指定levelのindex節だけ装飾し、台本表の直後(`study_html`の先頭)に付随ブロックを置く。standard.html/advanced.html(開発確認用)は対象外。None/未指定=従来とバイト同一。 |
| `er026_family_z_fiction_production_runner_01.py:1135-1138` | `ADV_LEVEL`/`ADV_EXPL_STAGE`新設、`E2E_KP_EXTRA_REGEN_NAMES`に`kp_part1_a2`/`kp_part1_ja_a2`を追加(`argparse --regenerate-stage`で明示再生成可。`DEPENDENTS`へは追加しない=既存方針、`er062`は無変更)。 |
| `er026…:1540-1620` | `_part1_items(ctx, level)`(旧`_part1_items_b1b`を撤去)、`_display_spec`(`display_spec_of`、未知値=`FAMILY_Z_DISPLAY_SPEC_UNKNOWN`)、`_part1_on`(Advは常に/Stdはdisplay_spec付きのみ)、`_part1_levels`、`_highlight_items`、`_resolve_level_highlights`(アダプタ。本文=`canonical_article_text(level本文)`、表示単位=`full_story_display_units`、候補docのcandidates_sha256を確定レコードoriginと照合、ISSUE=原因コード付き`FAMILY_Z_HIGHLIGHT_ISSUE`でページ生成前STOP、NOTICE/ISSUEは`<level>/audit/highlight_resolve.json`へ記録)。 |
| `er026…:1762` `_part2_pool` | Part 1が載るlevelのみ参考訳pool(Std旧run=空のまま)。 |
| `er026…:2137-2270` `stage_kp` | Part 1生成を`_part1_levels(ctx)`のloop(Adv常に+display_spec付きStd)。`_stage_kp_part1`/`_stage_kp_part1_ja`/`_assemble_study_rows`/`_require_part1_fresh`/`_require_part1_ja_fresh`/`_part1_path`/`_part1_ja_path`を`level`引数化(既定=`ADV_LEVEL`)。stage名`kp_part1_<lv>`/`kp_part1_ja_<lv>`、保存先`key_phrases/<lv>/`、study_textはAdv=`<out>/study_text`(従来どおり)・Std=`<out>/a2/study_text`(Advを上書きしない)。 |
| `er026…:2418` `load_level_inputs` | `_part1_on(ctx, level)`のlevelでPart 1(解説+T1訳)の存在とsignature一致をfail-closed確認(Stdも同型)。Part 2確定確認はAdvのみのまま(Std文法はページ専用)。 |
| `er026…:2553` `stage_pages` | display_spec付きlevelのハイライトをページ生成前に解決(ISSUE=STOP)。Part 1をlevel別に描画し、**判断記録が無く空になるdisplay_spec付きlevelはSTOP**(黙って欠落させない、M11)。Std節=付随ブロック→Part 1→Part 2。マーク無し=`highlights_by_level`キー自体を渡さない。 |
| `er026…:2614` `_verify_learning_items` / `:2660` `stage_page_verify` | level節ごとにPart 1ブロックがちょうど1個(vocab対象level=Advで描画有効・display_spec付き)/それ以外は0個、display_spec付きlevelは`verify_highlights`(G3)。kill switch(`EIGO_KP_CONFIRMED_PROTECTION=0`)時はG3のみスキップしてdisabled markerを`page_verify_local.json`の`learning_items_verified`へ記録。`has_vocab_on_page`をlevel節単位に(旧: b1bのみ・index全体)。 |

## 2. 検査結果(runtime evidence、API 0)
- 新規test `er026_z_highlight_wiring_test_01.py` 47件PASS(合成run: 描画・クリップ跨ぎ・`⏸`共存・unit不一致STOP・付随ブロック/禁止語0・解決アダプタ(OK/ISSUE/sha不一致/候補doc差替え)・`stage_pages`配線(マーク無し/付き/判断記録なしSTOP/ISSUE先行STOP)・`_verify_learning_items`(1/0/2個・G3 FAIL・kill switch)・mock `stage_kp`(マーク接続を模擬: Std Part 1がlevel=a2で生成、Advは従来、provenance、再実行API 0、`--regenerate-stage kp_part1_a2`はa2の1 callのみ、`load_level_inputs(a2)`のfail-closed)・Part 1系関数の`"b1b"`リテラル0のAST検査・実Z run `run_kcp4_ev_z_01`(確定レコードあり、wav要)でのend-to-end)。
- 実run `er026_output/family_z_production_e2e_01/melos/run_kcp4_ev_z_01`(a2/b1b、display_spec付き相当を与え、runファイルは変更せず): 解決ISSUE 0・NOTICE 0。a2=7要素(①3/②2…区分1×3,2×2,3×2)+③訳2、b1b=①3。`build_pages`→`check_page` PASS・lint 3項目False・public `⏸`0・`title=`0・禁止語(英語:/日本語:/EN:/JA:)0・G3 PASS(a2 decorated_elements=7、b1b=3)。
- golden: 旧run `melos/run_p2_evidence_r3`の`build_pages`出力sha256が変更前後で一致(advanced=9fcd3783…、index=c7a80677…、standard=82a43fd3…)。
- 回帰: `er026_family_z_fiction_production_runner_01_test` 21 OK、`er026_family_z_src_posthoc` 12 OK、`er062_*`(source_essentials/speaker_roster/voice_assignment) OK、`er063_*pd06/common_style` OK、E2E統合(`ER026_SKIP_PAGE_VERIFY=1`)30件中29 OK+1 error(`MockFullPipelineTest.setUpClass`)。残りの失敗は変更前(commit 374cfc941のworktree)と同一または包含される環境要因(`google.genai`/`faster_whisper`/`pronouncing`未導入)で、変更前後の失敗集合の差分に新規失敗なし。`er026_family_z_stop_sentinel_test_01`の並列干渉dry-run系は単体再実行で変更後=失敗3(genai/whisper環境要因)、変更前worktree=失敗6。

## 3. 旧経路撤去・残置(Grep)
- 撤去: `_part1_items_b1b`(関数名)。Part 1系関数(`_part1_items/_part1_path/_part1_ja_path/_require_part1_fresh/_require_part1_ja_fresh/_assemble_study_rows/_stage_kp_part1/_stage_kp_part1_ja/_part1_stage/_part1_ja_stage/_part1_on/_part1_levels/_part2_pool`)内の`"b1b"`文字列定数=**0件**(既定引数も`ADV_LEVEL`参照。AST testで固定)。`"Standardに載せるのはPart 2だけ"`コメント・`study_html_std = compose_page_html("", …)`を撤去。`SPEC_CONFLICT_02.md`のZ分: S21(`:1135,1537-1542,2196-2201,2206-2217`)・S22(`_part2_pool`)・S23(`stage_pages`)・S24(`has_vocab_on_page`)は解消、`er063:2592`コメント(Part 1[Advancedのみ])を更新。
- 残置(意図): `kp_expl_b1b`(Advanced専用の英語解説stage、Std無し)・`_kp_items_b1b`(Adv KP解説の入力、Part 1系ではない)・`_part2_final_step(…, "b1b", …)`/`PART2_STAGES`(Part 2)。
- S29(`CURRENT_SPEC.md:2086`「Advanced=b1bのみ。Standard・A/B/C・Yへは拡張しない」)の更新は本委任の編集権外(Fable/別委任、SPEC_CONFLICT_02のとおり)。

## 4. 未対応・留意(判断区分つき)
1. **`load_verified_items(which="highlight")`はB班commit 374cfc941に無い**(CONTRACT_03 §2/§9のB行)。Zアダプタは`er128.load_record`+`items_from_record`で代用(`_highlight_items` 1関数に局所化。G1整合は`stage_pages`冒頭の`_assert_kp_review_consistent`が先に通す)。B班が追加した場合は`_highlight_items`の1関数だけ差し替える。分類B(承認範囲内・修正へ進む=同一契約の局所差し替え)。
2. **`er128.verify_outputs`(G3)のa2 Part 1行検査は`level=="b1b"`ガードのまま**(B班IMPL_B_01 §5「§D別班」)。Zは`_verify_learning_items`でPart 1の個数とハイライトを検査し、`verify_selection_matches_outputs`にa2の`study_text_json`/`vocab_page_paths`を渡している(B班の`vocab_enabled`で有効)が、ページ上のa2 Part 1行と確定gloss照合(§D-5)は未実装。分類B(別班の所有範囲、修正へ進む=次委任)。
3. 環境: `google.genai`・`faster_whisper`・`pronouncing`未導入のため、mock全stage通し(TTS stage以降)と`test_zz_page_verify_local_playwright`は本環境で実行不可(変更前から同一)。`stage_pages`/`stage_page_verify`の配線は、mock/合成と実Z runのend-to-end(pages+G3)で代替検証した。`wordfreq`は本環境にpip導入(pre-existing testの前提)。
4. 凡例・訳リストの文言はA班共通部品のまま(`英語:`/`日本語:`/`EN:`/`JA:`/`(A2)`なし)。
5. **B班所有testの許可リスト**: `er128_kp_confirmed_content_test_01.py::TestIsolation::test_abc_and_shared_functions_do_not_import_er128`(`^\s*(import|from)\s+er128_`をA/B/C共有側のimport禁止として検査)は、X/Y/Zの配線(本E班の`er026…:2619` `import er128_kp_highlight_01 as g3`、C班の`er019…`/`er019_family_x_listening_page_01.py`、D班の`er121_family_y_runner_01.py`)で失敗する(許可リストは`er128_kp_highlight_01.py`自身までしか含まない)。E班は`er128_kp_confirmed_content_01`のimportを`_khr()._cc()`経由(既存の入口)にして接点を最小化し、`test_default_is_on_and_single_reader`(runnerにflag名を書かない)は満たした。許可リストへのX/Y/Z runner・builderの追加はB班所有testの1行変更で、C/D/E共通の事項=Fableが一括で依頼する(分類B・修正へ進む)。E班はB所有ファイルを編集していない。
