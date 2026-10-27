# B3_OVERLAY_AND_PARITY_GATE_01: 表示本文overlay・三者一致Gate・Z注記撤去・X事後試聴LR行非表示・混入検知の実装(未配線)+配線patch(委任_10 / Phase B B3準備、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。委任文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_委任_10.md`(+Fable補足: 既存moduleへの関数追加もしない)。ユーザー原文=`…_USER.md`(§2 表示は最終Human報告のみ・注記の公開混入禁止 / §3 UD-1)。設計=`INTEGRATION_01.md` F-1/F-5/F-9、`OPUS_REVIEW_01.md` (b)-5・M-7・M-8・R-6、`W2_UD1_BODY_REFLECTION_DESIGN_01.md` §3・§5・§9。前提=`er129_lr_display_reflection_01.py`(委任_07、commit e56c9a04f)。

## 0. 結論
1. 新module `er132_lr_overlay_pages_01.py`(新規1ファイル。**既存moduleへの追加0**)に、overlay・三者一致Gate・公開物混入検知を実装。どの既存コードからもimportされない(未配線)。stdlibのみをtop importし、er129/er020/er128は遅延import。
2. 既存4module+共通ページ+Z runnerへの変更は**patchのみ**: `docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/patches/B3_wiring_01.patch`(`git diff`形式、7ファイル(既存module6+旧仕様test1)・+67/-18、現HEAD(e56c9a04f)に対し`git apply --check`/`git apply --cached --check`とも通る)。適用は統合配線commit(別委任)。**適用手順**: このrepoは`core.autocrlf=true`のため、checkout後のpatchファイルがCRLFになると素の`git apply`は失敗する(実測)。`git show <commit>:docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/patches/B3_wiring_01.patch | git apply`(blobのLFをそのまま適用)または`git apply --ignore-whitespace <patchファイル>`を使う(両方とも`--check`確認済み)。
3. test `er132_lr_overlay_pages_01_test_01.py` 52件PASS(約19秒、合成+実データ。実データ不在時はskip)。patchは一時dirのHEADコピーに適用して内容・compile・check_page挙動をtestで固定(作業ツリーの既存moduleは無編集)。
4. 既定動作不変: er132は未import(ASTで全`*.py`を走査するtestで固定)。patchを適用しても、LR 0のrunではoverlayが入力と**同一object**を返し(byte同一)、Gateは未配線呼出でも通る(新たな停止を作らない)。

## 1. 追加した関数(`er132_lr_overlay_pages_01.py`)
| 区分 | 関数 | 要点 |
|---|---|---|
| 台帳 | `level_ledger(run_dir, level, results_path=, level_dir=)` | `er129.build_lr_ledger`のwrapper。X/Y/Z共通(`<run>/<level>/audit/tts_generation_results.json`)。results無し=空台帳 |
| overlay | `overlay_text(ledger, text, source=|clip_id=)` | 変更箇所前後k語のanchor(`er129.locate_op`)で位置特定→`er129.apply_overlay`で派生適用。台帳空/該当なし=同一object。反映済み(AFTER)なら不変(冪等)。位置不能・曖昧・STOP判定clip=`LROverlayError`(黙って原文表示にしない) |
| overlay | `overlay_level_units(ledger, parts, support)` / `overlay_level_dir_units(level_dir, parts, support)` | X/Yの`parts.json`(`part1`/`in_one_line`/`segments.<sid>`)と`*support_texts.json`のoverlay済み**コピー**(入力dict不変、変更キーのみ差替え)。LR 0=同一object |
| overlay | `display_text_of_clip(ledger, clip_id, text)` | Z・Y topic_intro等`entry.canonical_text`出典の共通入口 |
| overlay | `overlay_highlight_units(ledger, units)` / `unit_sources(key)` | ハイライトのDisplayUnit列(X `full_story_partN`・Y segment id)を同じoverlayで揃える(SLOT-23 `data-hl`が書換え後文で確定候補IDに紐付く条件) |
| Gate | `rendered_display_units(run, level)` | 「配線後にページが描く表示unit」={unit_key: overlay後本文}。ページ描画と同じoverlay関数を通す |
| Gate | `evaluate_text_parity(run, level, rendered_display=…)` / `assert_text_parity(…, stop_cls=)` | 三者一致(表示=TTS入力=ASR正解)。**`rendered_display=None`(overlay未配線の呼出)はLR採用clipがあれば常に`DISPLAY_NOT_OVERLAID`=異常側**(配線後に初めて通る、INTEGRATION F-5)。不一致・位置不能=`BLOCKED_LR_DISPLAY_CONSISTENCY`、T1/T2/T3=`BLOCKED_LR_CONFIRMED_CONTENT_INTERFERENCE`(ユーザー判断)。HR採用で音声=原文のclipは原文表示でPASS_SUPERSEDED |
| Gate | `assemble_gate_summary(run, level)`(X/Y)/`z_assemble_gate(run, level, stop_cls)`(Z)/`blocked_summary(exc)` | X/Yは`run_summary_assemble.json`へ保存するBLOCKED summary(`hr_queue: False`=HRキューへ流さない)。Zは`FamilyZLRDisplayConsistencyStop`(patchでFamilyZAudioStop系列に追加)を上げる |
| 混入検知 | `public_leak_hits(text)` / `assert_no_public_leak` / `PUBLIC_FORBIDDEN_PATTERNS` | `fhr-` class/CSS・`LR_REWRITTEN`・`LR_APPLIED`・`FALLBACK_APPLIED`・`FALLBACK_MINIMAL_EN/JA`・`ENGLISH_LOCK`・`LEGACY_DIALOGUE`・`minimal_fallback`/`english_lock_fallback`・「Local Rewrite採用」・「Fallback発動/採用・音声は原稿から変更」 |

## 2. 配線patch(`patches/B3_wiring_01.patch`)の内容
| ファイル | 変更 |
|---|---|
| `er019_family_x_audio_production_runner_01.py` | (a)`stage_assemble_family_x_b1/a2`: 三者一致Gate(`assemble_gate_summary`)を**M3/Style Gateより前**に挿入(BLOCKED時は既存summary保存形式で返す) (b)`_build_level_table`: parts/supportをoverlay (c)`resolve_x_highlights`: overlay後のpartsでハイライト解決(LRありのときだけ`lr_rebound=True`) |
| `er019_family_x_listening_page_01.py` | (a)`level_data`: overlay (b)`build_page(audience="public")`引数追加、publicでは事後試聴リストのLR行(`LR_REWRITTEN`ラベル・期待文・ASR文)を非表示(M-7。HR audienceは従来どおり) (c)`check_page`へaudienceを渡す |
| `er121_family_y_audio_01.py` | (a)`assemble_level`: Gateを`y_style_gate`より前に挿入 (b)`y_highlight_display_units`をoverlay済み化(`overlay=False`で従来値)・`resolve_y_highlights`はLRありのときだけ`lr_rebound=True` (c)`build_page_rows`: parts/support/topic_introをoverlay(原文同士の`FAMILY_Y_HIGHLIGHT_TEXT_MISMATCH`比較はoverlay済み同士に揃う) |
| `er063_family_z_audio_01.py` | (a)`FamilyZLRDisplayConsistencyStop`追加 (b)`build_page_rows`/`full_story_display_units`の2式を同じ`display_text_of_clip`へ (c)**旧`Local Rewrite採用(…)`注記2か所(:2464-2468)を撤去**。`Voice:`/`Style:`/`TTS方式`表示・減速注記は維持 |
| `er026_family_z_fiction_production_runner_01.py` | `stage_assemble`: `run_assembly`の前にZ Gate(`z_assemble_gate`) |
| `er_user_listening_page_common_01.py` | `check_page(public)`に`no_lr_fallback_note_in_public`検査を追加(dev/HR audienceは検査しない。既存検査キーは不変) |
| `er117_z_chunk_wiring_test_01.py` | 旧仕様(I7: chunkのLR注記を親行へ表示)を固定していたassert1件を「注記なし」へ更新(撤去した旧規則のtest) |

## 3. mock integration結果(API 0、`er132`の関数を直接呼ぶ。patchは作業ツリーに適用していない)
| 対象 | 結果 |
|---|---|
| X AI島Std/Adv(`ai_island_temple__run_form_prod_01` a2/b1b) | part1の該当1語のみ `AIs`→`AI agents`/`AI systems`(逆置換で原文と一致、part2/3不変)。三者一致PASS。parts/results/confirmed_selectionのshaは前後で同一。**ハイライト解決(`resolve_highlights`、実確定レコード)がoverlay後のDisplayUnitでstatus=OK** |
| X Word Gacha Adv(`word_gacha__run_wg_01` b1b) | part3 `you've`→`you have`(1語)、三者一致PASS |
| Z 猿の手Std(`run_sf_prod_01` a2) | `full_story_part1_c10` `guest`→`visitor`、三者一致PASS。採用takeはB2既報どおりUNKNOWN(記録欠落、別項目) |
| Y LR採用(`run_tru_ev_y_adv_4b` b1b、保存evidence run) | `y_voice_1` `notice`→`note`のoverlay、三者一致PASS(公開Yに実LR採用なし=未観測のため evidence run で代替) |
| LR 0(X BAPE a2/b1b・Z メロスrun_e2e_06・Z 告げ口心臓run_reselect_01) | overlayは同一object(byte同一)、`rendered_display_units`={}、**overlay未配線の呼出でも**Gate通過(新たな停止なし) |
| 未配線Gate(AI島) | `rendered_display=None`→`BLOCKED_LR_DISPLAY_CONSISTENCY`(`DISPLAY_NOT_OVERLAID`)。原文のまま描画した場合も`MISMATCH_V1/V2`で停止 |

## 4. 混入検知の実測
- 保存run(AI島・Word Gacha・BAPE・猿の手・メロス・告げ口心臓・Y evidence)のTTS入力(`text`/`canonical_text`)・ASR期待文・Style Prompt(`instruction`/`style_prefix`)・KP表示・parts/support・study_textに禁止語**0件**(testで固定)。overlay出力にも0件。
- 公開ページ実測(`user_test/*/{index,standard,advanced}.html`、HR用`hr_*`除外): 検出は **Z `family_z_melos_01/advanced.html`・`family_z_monkeys_paw_01/standard.html` の2件のみ**(旧`Local Rewrite採用(音声は原稿から変更…)`注記=既公開不一致の一部。B7の差替え是正対象)。他の公開ページは0件。検出器が実在の混入を捕捉できることの確認を兼ねる。HR audience用ページ(`hr_*`、`minimal_fallback`を含む)は対象外(最終確認資料側の語を使うのはHRページの正当な機能)。

## 5. Fable補足(既存module無編集)への対応・設計上の注意
- 委任文§7の「既存module内への未呼出関数追加は可」は、Fable補足に従い**使わなかった**(委任_06の編集対象と衝突しないため)。patchは現HEADに対して作成(別worktreeのHEAD上で編集→`git diff`)。委任_06のcommit後は、patchが同箇所に当たる場合のrebase要否を統合配線commit担当が`git apply --check`で確認する。
- patchで既存moduleに入る`import er132_lr_overlay_pages_01`は各関数内の遅延import(module top-importを増やさない)。`er_user_listening_page_common_01.check_page`の追加検査はpublicだけ。
- `z_assemble_gate`はZ `stage_assemble`直前(gate stageの後)。Zの`run_audio_gate`/`audio_text_deviation`の既存挙動は不変。

## 6. 既存regressionテスト(patch適用後・隔離worktree、API 0)
patchを隔離worktree(HEAD e56c9a04f、作業ツリーとは別)へ適用し、関連17テストファイル(Z audio/E2E・Y runner/highlight/chunk・X highlight/runner/chunk・ページ共通・LR highlight等)を実行(API 0)。
- **patch無しの同worktreeを基準線**とし、失敗集合を比較: 基準線 38 failed/66 errors(worktreeに未commitのrun出力・`*.wav`(.gitignore)が無い環境差=`FileNotFoundError: …welcome_charon.wav`/`REAL API PATH CALLED`/`FAMILY_Z_SEED_SHA_MISMATCH`。patchと無関係)、patch適用後 39 failed → **差分は1件のみ**: `er117_z_chunk_wiring_test_01.py::ZGateAndAssemblyTests::test_assembly_chunk_gain_gap_timeline_and_pages`(旧仕様I7「chunkのLR注記を親行に出す」を固定していたassert)。
- これは撤去対象の旧規則(F-9/M-7、原文§2)そのもののtestなので、**patchに同testの更新を含めた**(`assertTrue(any("Local Rewrite" in n …))`→`assertFalse(…)`、コメントも更新。撤去した旧規則の識別子=`row["notes"]`のLR注記2か所と同test assert 1か所)。更新後、同ファイルを含む `er117_z_chunk_wiring/er117_x_chunk_wiring/er063_z_std_chunk` 60 passed・1 skipped。
- 追加で`er003_output/b1redesign_audio_01`のwavを隔離worktreeへ複写して再実行: `er063_family_z_audio_01_test_01.py`・`er078_asr_unified_en_wiring_test_01.py`は**全PASS**(patch適用後、ページ構築・assemble・注記撤去を含む)。残る失敗はseed sha(CRLF/LF checkout差)・実API経路ガード(`REAL API PATH CALLED`、未複写の他asset依存)=基準線と同一の環境差。
- main作業ツリー: 新規4ファイル以外に差分なし(patchは未適用。`git apply --check`と`git apply --cached --check`はともにOK)。

## 7. 未観測・限界・判断候補
- **(区分B、軽微・fail-closedで対処済み)X `topic_intro`/`japanese_title`のLR**: Xの表示はテンプレート(`Today's topic is {title}.`)で`entry.canonical_text`を描画しない(`er019 runner:_row_info_family_x`)ため、overlayを届ける経路が無い。保存evidence run(coffee `x_std_2` topic→subject)にLR記録あり(公開物ではない)。Gateは`rendered_display_units`をer132自身が組むので、描画されない箇所のLRは通常のGateでは検知できない→X呼出に`not_rendered_clip_ids=("topic_intro","japanese_title")`を渡し、当該LR採用があれば`DISPLAY_SOURCE_NOT_RENDERED`で技術STOP(見逃さない。testで固定)。是正(Xのtopic_intro表示をclip overlayへ接続するか、当該LRをT系列で扱うか)は統合配線時にFableが判断。
- **(区分B、設計上の限界)Gateが見る「描画本文」はer132のoverlay関数の出力**(ページ描画側も同じ関数を通す=構成上一致)であり、描画後HTMLの本文を再取得して照合してはいない。patch適用後のページHTMLと台帳overlayの一致は、統合配線後のruntime evidence(B8、AI島assemble→pages→公開HTMLの該当文確認)で実測する。
- Y: 公開Yに実LR採用なし(evidence runで代替=未観測)。Yの`topic_intro`表示のoverlayはpatchに入れた(`display_text_of_clip`)が実LR例は未観測。
- X chunkの親part写像(W2 §4-2-3: chunk plan再分割一致の検証)は未実装(`er129`既記のとおり。`parts.json:partN`出典のchunk clipはanchor特定で扱え、AI島実データで確認済み)。
- patch適用後の既存testのうちworktreeで失敗するものは、patch無しの同worktreeでも同じ失敗(隔離worktreeにはmain作業ツリーの未commit run出力が無いため)。上記§6に差分を明記。
- 新規OPEN登録: なし。
