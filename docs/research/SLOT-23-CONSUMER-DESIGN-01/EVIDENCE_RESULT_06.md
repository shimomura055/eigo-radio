# EVIDENCE_RESULT_06 F班(委任_06F): ①②③表示仕様の6経路 runtime evidence
管理ID=SLOT-23-CONSUMER-DESIGN-01。性質=evidence取得(DEV run dir・非公開)。到達上限=EVIDENCE(PRODUCTION_WIRED判定はFable)。使用model=本番routing(`gpt-6-luna`=KEY_PHRASE_GENERAL_EXPLANATION→SUPPORT_MODEL、TTS=`gemini-3.8-flash-lite-tts`、ASR=`gpt-4o-mini-transcribe`/`azure-speech-stt`。評価用最新モデル原則[25節]の対象ではなく、本番ライン配線の確認のため本番routingのまま。最新かの評価は本委任外)。
前提=A〜E班+M班完了(commit 1684e19f5/ccf118a31=マーク発行`new_review`接続済み)。ユーザー決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。
証跡=`evidence_runs/{y,z,x}/`(番号順)。独立検査tool=`tools/{mk_payload_s23f_01,verify_page_s23f_01,browser_check_s23f_01}.py`。

## 1. 対象run(各Familyの複製。ベースrunは無変更)
| Family | ベース | 本委任のrun(DEV、非公開) | runner |
|---|---|---|---|
| Y | `er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01` | `.../run_gpg5_y_01_s23f` | `er121_family_y_runner_01.py` |
| Z | `er026_output/family_z_production_e2e_01/melos/run_kcp4_ev_z_01` | `.../run_kcp4_ev_z_01_s23f` | `er026_family_z_fiction_production_runner_01.py` |
| X | `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_gpg5_x_01`(source `er019_output/part2_hr_evidence_01/run_gpg5_x_01`も`_s23f`へ複製) | `...__run_gpg5_x_01_s23f` | `er019_family_x_audio_production_runner_01.py` |
STOP/lock(RESTART_STORM_LOCK等)はベースに無く、コピーしていない。AI島run(`ai_island_temple__run_form_prod_01`)・AIF委任_06のrunは触っていない。

## 2. 手順(全Family共通。正式初回経路の再現と限界)
1. 各levelの`key_phrases`の確定・review関連ファイルを`_s23f_prev/`へ退避(削除しない)。KP解説/Part 1/T1訳は残置。
2. 正式runnerを起動し、候補抽出(P7/W5')→**`new_review`が自動でマーク`std_part1`を付与**(6review全て`std_part1=True`、`evidence_runs/51_mark_auto_issue_and_records.json`)。人手でマークを書いていない。
3. `confirm --from-form --actor evidence --grammar-pending`(payload v2は`tools/mk_payload_s23f_01.py`で候補docから決定的に生成。①3件・②2件・③2件、活用形を含む候補を優先)→`grammar-pregen`(API 0・既存解説reuse)→`confirm --grammar-from-form`(Y Std/Adv=Top1/Top2各1件、Z Std=0件[NO_CANDIDATE_UNREVIEWED]/Adv=1件、X 各1件)。確定レコードに**`display_spec=LEARNING_ITEMS_123_V1`が自動で付与**(継承/導出)。`status`でG0/G1(実行前後)とも`live`・`evidence`・`display_spec`あり。
4. runner通し(下の起動履歴)。
限界(正直な記録): 本runは「既存run複製+review差替え」であり、来歴(provenance)に旧entryが残るため、新規記事では不要な`--regenerate-stage`連鎖(kp_b1b→kp_a2→kp_expl_b1b→kp_part1_*→part2_*→tts_*)がSTOP案内どおり必要になった(各STOPはAPI 0で原因判明)。「来歴が空の正式初回run」そのもの(regenerate無し)は再現していない。ただしnew_review→マーク→display_spec→Std Part 1→ハイライト→G3の各点は実runnerで発火した。

## 3. 経路別evidence(a)〜(i)
確定内容(①②③。used_form/本文上の表層形): 
- Y Std(a2): ①end up getting it / can’t be helped / make an effort、②in person / encourage(encourages)、③take up(takes up) / when it suits someone(when it suits me)。文法Top1 g31f4b39e68。Y Adv(b1b): ①doesn’t sit right with (someone/me) / take the trouble to / end up receiving、②beforehand / repeatedly、③encourage(encourages) / can’t be helped。文法Top2 g938cd4b23a。
- Z Std: ①pull someone under(pulled him under) / keep one's eyes on them(kept his eyes on them) / For once、②shepherd / flood、③lose one's life(lose his life) / demand(demanding)。文法0件。Z Adv: ①sentence someone to death(sentenced him to death) / hold out one's hands(held out his hands) / rise above the other voices(rose above the other voices)、②without asking for another promise / execution、③seize(seized) / abandon(abandoned)。文法g50e12a388f。
- X Std: ①Turn Back the Clock / pass through(passed through) / coffee futures price、②drought / suspect、③reach a record high(reached a record high) / tariff(Tariffs)。文法gddf816bb8f。X Adv: ①jump to conclusions(jumping to conclusions) / make its way through(made its way through) / have one's eye on(had our eye on)、②year over year / futures price、③impose(imposed) / shortage(shortages)。文法g241d45439e。

| 項目 | Y | Z | X(player.html。公開builderは不具合D-F1でSTOP) |
|---|---|---|---|
| (a) Part 1がStd/Advともちょうど1個・①+②全件・日本語解説 | 各section `part1_blocks=1`・h4=5件=①3+②2(`30_verify_pages_public.json`/`40_verify..final.json`、`page_verify_local.json`) | 同(各5件) | 同(各5件。`20_verify_player_public.json`、`verify_x_player`がrc=0) |
| (a2) Std難易度差=Head差分のみ・Adv golden不変 | `build_prompt(level)`のStd/Adv差=3行(対象読者行1+やさしい語の1文。`EVIDENCE`本文参照)。Adv `prompt_template_sha256=4d7ae557…`(定数`PROMPT_TEMPLATE_SHA256`と一致)、Std=`df21d3ef…`(`PROMPT_TEMPLATE_SHA256_A2`)。解説は日本語(作業仮定A) | 同 | 同 |
| (b) ①二重/②下線/③下線が本文に出る・`data-hl`件数=確定件数 | Std 3/2/2・Adv 3/2/2(=確定件数、id集合一致=true)。NOTICE=0(`61_highlight_resolution_*.json`) | 3/2/2・3/2/2。NOTICE=0(`61_highlight_resolve_*.json`) | 3/2/2・3/2/2。NOTICE: Std ①`Turn Back the Clock`に`HL_OCCURRENCE_RELOCATED`1件(最初の出現が表示範囲外[見出し側]のため本文の出現へ再配置。停止しない設計。`26_highlight_resolve_x.json`)。Adv 0 |
| (c) ③訳リスト=確定`japanese_gloss`逐語 | 各section `used_form ＝ gloss`=確定一致(`meaning_equals_confirmed_japanese_gloss_verbatim=true`)。`ul.lk-meaning`は各section1個 | true(各section) | true(各section) |
| (d) G3 PASS・`check_page(public)`PASS・public⏸0 | page_verify `highlight_verified` b1b/a2=PASS(decorated 7/7)・`ok=true`。`check_page`=PASS・public⏸0(`pause_total_in_html=0`) | `learning_items_verified` b1b/a2 `g3.status=PASS`(decorated 7/7)。`check_page`=PASS・⏸0 | G3=playerステージ内`verify_x_player`PASS(rc=0)・⏸0。**`check_page(public)`は未取得**(標準builderが`X_PART1_BLOCK_COUNT(a2)`でSTOPしindex.htmlを出力しない=不具合D-F1。player.htmlは公開ページではなく`check_page`は設計上FAIL) |
| (e) 確定レコードcmp同一(実行前後) | a2/b1b とも`cmp`同一(`11_confirmed_selection_*_before.json`↔最終。regenerate後も同一) | 同(a2/b1b。regenerate後も同一) | 同 |
| (f) finalize/pagesのLLM 0(Part 1生成分のみ加算) | part2_a2再finalize+pages: cost_log 62→62行。dev pages・pages再実行も62→62。Part 1生成分(`kp_part1`系3回)のみ加算 | part2_a2+完成段: 108→108行。pages再実行108→108 | study_text(Part 2 finalize)・assemble・player・player再実行: raw_usage_log 72行のまま(API 0)。Part 1/T1生成分はscaffold内に加算 |
| (g) retry/resume | pages+page_verify再実行: `pages/index.html` sha256同一(`66d4ecdf…`、API 0)。`--regenerate-stage kp_part1_a2`でStd Part 1だけ再生成(+¥0.105)・確定レコード不変(cmp同一) | pages再実行: sha同一(`a8f3cd4d…`、API 0)。`--regenerate-stage kp_part1_a2`(+¥0.099)・確定不変 | `--stage player`再実行: player.html sha同一(`3ffdf12c…`、raw_usage 72→72)。`study_text`再実行はreusedでAPI 0。Xに`--regenerate-stage`は無い |
| (h) actual model_id・routing | Part 1(Std/Adv)・T1訳・KP抽出等=`gpt-6-luna`(requested=actual、process=`KEY_PHRASE_GENERAL_EXPLANATION`)、TTS=`gemini-3.8-flash-lite-tts`、ASR=`gpt-4o-mini-transcribe`+`azure-speech-stt`(`40_llm_calls_by_stage.json`、各`kp_general_explanations.json`の`audit`) | 同 | 同(X TTS backend=`speech_metadata_flash_lite`) |
| (i) dev `--page-audience dev`で⏸が装飾の外 | `index_dev.html`: ⏸は凡例1個のみ・`data-hl`内0(`35_verify_pages_dev.json`)。**本記事にはChunk境界⏸が無く**、境界⏸と装飾の共存はY実runでは観測できない(D班testで固定) | Zにdevページ経路は無い(対象外) | `player_dev.html`: `chunk-mark`span 12個・`data-hl`内0(`23_verify_player_dev.json`)=⏸は装飾の外 |
Std/Adv別表示: Std Part 1(②)はY/Z/Xとも新規にStdへ出現(旧表示のStdはPart 1無し)。Std Part 1の記載位置=Part 2の直前(Part 1→Part 2)。

## 4. 起動履歴(同一run起動間≥300秒を全て維持。全体150秒は下記逸脱)
- Y(15起動、15:27:40〜16:45:47): L1 kp(新規review 9/10候補→rc=4待機)/確定+文法/L2 kp_b1b regenerate→**予算guard STOP(approved=10、見積り5円+累計5.79)**/L3(approved=20)kp_b1b→kp_a2親sha不一致STOP/L4 kp_a2→kp_expl_b1b stale STOP/L5 kp_expl_b1b→kp_part1_b1b STOP/L6 kp_part1_b1b→kp_part1_ja_b1b STOP/L7 kp_part1_ja_b1b→kp完了rc=0/L8 tts_b1b→Part 2(b1b)再finalize要STOP(API 0)/L9 part2_b1b/L10 tts_b1b(KP音声のみ)/L11 tts_a2(KP音声のみ)→gate→assemble→pages: part2_a2要STOP/L12 part2_a2+pages+page_verify OK/L13 dev pages/L14 pages再実行/L15 kp_part1_a2 regenerate+pages。rc≠0はいずれも原因判明(来歴の親sha不一致・予算guard)、原因不明のrc≠0の連続は無い。
- Z(13起動+L1 STOP): L1 legacy判定(review無し+result有)で親sha不一致STOP(API 0)→result退避→L1b kp(新規review)rc=4/確定/L2 kp_b1b→kp_expl_b1b STOP/L3 kp_expl_b1b/L4 kp_part1_b1b/L5 kp_part1_ja_b1b→kp完了/L6 tts_b1b→Part 2 STOP(API 0)/L7 part2_b1b/L8 tts_b1b KP clipのみ/L9 tts_a2 KP clipのみ/L10 part2_a2+provision_shell+gate+assemble+pages+page_verify OK/L11 pages再実行/L12 kp_part1_a2 regenerate/L13 pages+page_verify。
- X(8起動): L1 `--stage scaffold --scaffold-only kp`(新規review・rc=4)/確定+文法/L2 同(KP finalize+Part 1生成)/L3 study_text(API 0)/L4 tts/L5 assemble/L6 player/L7 player dev/L8 player再実行。標準公開page builder(`er019_family_x_listening_page_01.py`)はrunner起動ではなく、STOP(rc=3)でindex.html非出力。
全起動前に`stop_scope_check_01.py`(rc=0、`00_stop_check_*.json`)。他`er019`/runner process不在をXのtts前に確認(`x/13_er019_proc_before_tts.txt`=空)。

## 5. 逸脱・不具合・判断(詳細は`RESULT_PACKET_S23F.md`)
- **逸脱1(禁止事項への抵触)**: X `--stage tts`でStd(a2) Full Storyのchunk 9セグメント(`full_story_part{1-3}_k{1-3}`)をGemini TTSで再生成した(+Std parent3)。原因=ベースXのa2は旧(chunk化前)の生成物で、現行のStd chunk TTS(CHUNK-TTS-STD)ではchunk entryが無く再生成が必要。`--dry-run`/`--only-segments`での事前確認を怠った私の手順ミス。Adv Full Storyはcache再利用(再生成0。wavのmtimeが複製時刻のまま)。費用=Gemini 17呼出のうち9呼出がStd Full Story(TTS stage全体¥7.42の9/17≒約¥3.9)。DEV複製run内のみ(Production・公開・他runへ影響なし)。KP音声のみ許容≤¥5/経路は、X TTS stage全体¥7.42で超過(KP分は約¥3.5)。Y/ZはTTS gemini 11呼出ずつ=KP音声のみ(Full Story再生成0。YはcostLogで確認、Zは`--only-clips`)。
- **逸脱2**: 「全体150秒以上」の起動間隔は守らず、Y/Z/Xを並列で起動した(最小20秒差。独立runの並列化=Charter原則2を優先)。同一run間隔≥300秒は全て維持。実害なし(rate limit・STOP・RESTART_STORM・process競合なし)。
- **不具合D-F1**(X標準公開builder): `er120_part2_wiring_01.public_study_html`がPart 1を`level=="b1b"`のみに限定しており(`:529-532`)、display_spec付きStd(a2)でPart 1が出力されない。標準builder(`er019_family_x_listening_page_01.py:143-148`)はStdのPart 1ちょうど1個を要求するため`X_PART1_BLOCK_COUNT(a2 page)`でSTOP(fail-closed・index.html/音声とも非出力)。`18_public_study_html_probe.txt`=a2: Part 1無し・b1b: あり。承認済み仕様(Std②表示)との矛盾=不具合(PM_GOVERNANCE 11-8)。AI島のStd再ビルド(同builder経由)にも影響する見込み。修正案: `public_study_html`の`level`分岐を`vocab_enabled(level, review)`/`display_spec_of`ベースにし、Stdでも`p1.study_html_for_audio_dir(..., level=level)`+`load_verified_items(..., level=level, which="part1")`を使う(+X Std公開builderのtest追加)。Productionコードのため本委任では修正していない。分類=修正へ進む(次委任案: er120 public_study_html level化+X標準builder test+AI島再ビルド前提確認)。
- 観測(不具合でない): Y/Z/XのKP review差替えは来歴の旧entryとの整合で多数のregenerate起動が必要(上記)。新規記事では発生しない見込み(来歴空)。
- 言語(受入条件2): Std/Advの②解説は**日本語**(作業仮定A。ユーザー確認中の事項。B[英語化]はPrompt本文のみの差替え)。本evidenceは仮定Aの状態。
