# COVERAGE_MATRIX_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_01A、実装前・API 0・Production編集0)
目的: Family X/Y/Z × Level(Std=a2 / Adv=b1b) × Section で「日本語音声あり → ASR judge経路あり/なし(file:line)」「対象外の理由」を確定する。一部Familyだけで完了としない(USER §3-3)。
根拠: 全て読取(Grep/Read)。行番号は2026-10-29時点のHEAD(f215c3537)。ユーザー原文=`docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md`。

## 0. 結論(先に)
1. **日本語音声が存在するのは Std(a2) のみ**。Adv(b1b)の Preview/Comment/KP解説/Dialogue/本文は全て英語(下表)。X/Y/Z とも Std の「日本語題・Preview・Comment・KP日本語意味」の4 Section が対象。
2. 上記4 Section はX/Y/Zとも**同一の入口** `n3_tts.generate_a2_japanese_with_reading_safety`(`er003_v1_n3_01_tts_generate.py:901`)→ `generate_a2_japanese_with_fallback`(`:763`。標準経路=`c.generate_narration_snippet_verified_strict(..."ja"...)`、fallback=`_generate_a2_japanese_minimal_instruction` `:689`)→ **`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade`(JA adapter、唯一のJA判定入口)** → `er078_asr_unified_judge_01.unified_judge` に到達する。よって配線点は **JA adapter 1関数**(`evaluate_attempt_ja_with_cascade_detail`、er007:556)で、X/Y/Z全Sectionを同時にカバーできる。
3. 新方式の有効範囲は **TTS段関数の既存run scope(`er109_xz_scope_01.family_scope("X"|"Y"|"Z")`)内だけ**に限定できる(§3)。scope外(Family A/B/C・単体呼出)は従来コードパスのまま=A/B/Cの挙動は変わらない(27-7)。
4. 要補完の抜け1件: **Yの試聴ページ(`er121_family_y_runner_01.py:1282`)に「事後試聴リスト(PASS_WITH_WARNING)」節が無い**(X: `er019_family_x_listening_page_01.py:179-186`・`er019_family_x_audio_production_runner_01.py:3432`、Z: `er063_family_z_audio_01.py:2716-2774` は有る)。Yは`audit/pass_with_warning_listening_list.json`までは書く(`er121_family_y_audio_01.py:762`)。最終制作報告に載せるため02で補う(WIRING_DESIGN_01 (e))。

## 1. 判定経路(共通。全Family・全Section)
| 段 | file:line | 内容 |
|---|---|---|
| 入口(Std JA 共通) | `er003_v1_n3_01_tts_generate.py:901`(`generate_a2_japanese_with_reading_safety`)→`:763`(`generate_a2_japanese_with_fallback`) | 標準経路 `c.generate_narration_snippet_verified_strict(...,"ja",...)`(`:805`)→ fallback `_generate_a2_japanese_minimal_instruction`(`:689`) |
| 標準経路のJA判定 | `er003_v1_repro01_main_generate.py:407-413` | `ja_secondary.evaluate_attempt_ja_with_cascade(... detail_out=cascade_detail)`。`asr_judgement`は `attempts_log`・最終entryに保存 |
| fallback経路のJA判定 | `er003_v1_n3_01_tts_generate.py:842-848` | 同 adapter。通算slot=標準消費分+周(`build_attempt_ctx`)、最終slotのNGのみHR対象 |
| (参考)Charon JA | `er003_v1_sing01_voice01_generate.py:616,677` | `generate_charon_japanese`(`:527`、標準+fallback)。**X/Y/Z Std JA Sectionは呼ばない**(A/B/C legacy)。同じ adapter を通るが scope外=従来のまま |
| JA adapter | `er007_ja_secondary_asr_01.py:556`(`evaluate_attempt_ja_with_cascade_detail`)/`:793`(wrapper。`:809-810`でHR queueへ) | Primary=OpenAI(`routing.transcribe`)→ Primary側値等価層(`:595`)→ `unified_judge`(`:691`)→ Secondary=Azure(`_azure_stt_strict`、`phrase_list_hash=""` `:644`) |
| 統一judge | `er078_asr_unified_judge_01.py:509` | Primary PASS→最終ANDゲート(`:633`)/ P1(`p1_value_diff` `:642`、Secondary不呼出NG)/ P2除外 / P3 Secondary 1回(`:676`、SecondaryCache)/ `secondary_not_accepted`(`:828`)/ `secondary_confirmed`=PASS_WITH_WARNING(`:840-841`) |
| 継承(J11) | `er019_family_x_validation_inheritance_01.py:256`(`rejudge_with_current_judge`)・`:234`(`_j11_adopted_judgement`) | JAは保存転写に最終ANDゲートだけ再適用。元の`asr_judgement`(警告)を`asr_judgement_inherited`へ継承 |
| Store再利用 | `er006_master_audio_store_01.py:130-137`(guard)/`:197`(`asr_judgement_inherited`復元)/`:234`(`manifest[...]["asr_judgement"]`保存) → `er078_reuse_value_guard_01.py:46`(`guard_entry`) | 保存された`asr_judgement`ごと再利用。scope外ブロックは`guard_entry`内(ortho/UKUS/PNAP前例: `:70-100`) |
| 事後試聴リスト | `er078_pass_with_warning_registry_01.py:93`(`derive_listening_list`)/`:153`(`load_listening_list`)/`:169`(`write_listening_list_safe`)/`:198`(`render_html_section`) | `tts_generation_results.json`から再導出。**非ブロッキング**(同ファイル冒頭コメント) |
| 組立Gate | `er003_v1_n3_01_assemble.py:89,487`(`AUDIO_GATE_ALLOWED_STATUSES=("VALIDATED","HUMAN_APPROVED")`) | statusがOKなら`VALIDATED`。PASS_WITH_WARNINGでもstatus OK→通過(TEST_PLAN T-H) |
| HR | `er007_ja_secondary_asr_01.py:42`(`_log_human_review`)/`:763`(最終slot NGのみ`human_review_required`)/`er127_tts_block_policy_01.py:726-740`(`register_ja_terminal_hr`) | PASS系(verified)はどちらにも到達しない |
| 採用take分類 | `er130_adopted_take_classifier_01.py:41`(`_ASR_PASS_STATES={"PASS","PASS_WITH_WARNING"}`) | JA PASS_WITH_WARNINGはASR PASS系として扱われる(BLOCK対象は異常Style/記録欠落等。TEST_PLAN T-H) |

## 2. Family × Level × Section マトリクス
凡例: 「ASR judge経路」=§1の共通経路。「scope」=その段関数に付いた `er109_xz_scope_01.family_scope(...)`(`er109_xz_scope_01.py:64`)。

### 2-1. Family X
| Level | Section | 日本語音声 | 生成点(file:line) | ASR judge経路 | scope |
|---|---|---|---|---|---|
| Std(a2) | 日本語題 | あり | `er019_family_x_audio_production_runner_01.py:2180-2194`(`japanese_title`) | あり(§1) | `:2025`(`@family_scope("X")`、`generate_family_x_a2_segments` `:2026`) |
| Std(a2) | Preview | あり | 同`:2196-2205`(loop `preview`) | あり | 同上 |
| Std(a2) | Comment 1-4 | あり | 同`:2196-2205`(loop `comment_1..4`) | あり | 同上 |
| Std(a2) | KP日本語意味 | あり | 同`:2327-2334`(`_generate_key_phrase_segments_a2` `:2281`、呼出`:2246`。`kp{rank}_japanese_meaning`) | あり | 同上 |
| Std(a2) | その他(Topic intro / Full Story / In One Line / KP英語 / 固定Shell) | なし(英語) | `:2166-2178`ほか | 英語adapter(`er006_secondary_asr_01.py:1215`)。**本ID対象外** | - |
| Adv(b1b) | 全Section | **なし**(Preview/Comment/KP解説/本文とも英語。KPの日本語は画面表示`display_gloss`のみ=`:2009`、音声化されない) | `generate_family_x_b1_segments` `:1659`(`@family_scope("X")` `:1658`) | 日本語音声が無いため対象なし | `:1658` |

### 2-2. Family Y
| Level | Section | 日本語音声 | 生成点 | ASR judge経路 | scope |
|---|---|---|---|---|---|
| Std(a2) | 日本語題 | あり | `er121_family_y_audio_01.py:692-698` | あり(§1) | `:639`(`@er109_scope.family_scope("Y")`、`generate_y_a2_segments` `:640`) |
| Std(a2) | Preview/Comment(1-3。Comment 4なし) | あり | 同`:700-710`(`ys.support_names("a2")`) | あり | 同上 |
| Std(a2) | KP日本語意味 | あり | 同`:744`(`xr._generate_key_phrase_segments_a2`、X共通部品) | あり | 同上 |
| Std(a2) | その他(Topic intro / Y本文chunk / In One Line / KP英語) | なし(英語) | `:682-691`,`:716-740` | 英語adapter。対象外 | - |
| Adv(b1b) | 全Section | **なし**(`:128`のコメント「Std(a2)のpreview/commentは日本語のため除外」=Advのpreview/commentは英語。KPは英語解説`:627`) | `generate_y_b1_segments` `:551`(`@family_scope("Y")` `:550`) | 対象なし | `:550` |

### 2-3. Family Z
| Level | Section | 日本語音声 | 生成点 | ASR judge経路 | scope |
|---|---|---|---|---|---|
| Std(a2) | 日本語題 | あり | `er063_family_z_audio_01.py:579`(ClipSpec `japanese_title`)/`:1138`(`ja_simple` `:1070`→`n3_tts.generate_a2_japanese_with_reading_safety`) | あり(§1) | `:1518`(`@er109_scope.family_scope("Z")`、`run_tts_stage` `:1519`) |
| Std(a2) | Preview/Comment | あり | `:581-582`(`language="en" if adv else "ja"`)/`:1075-1077`(`preview` closure=`comment`) | あり | 同上 |
| Std(a2) | KP日本語意味 | あり | `:1131`(`kp_ja`)/ClipSpec `KP_JA` | あり | 同上 |
| Std(a2) | その他(Topic intro EN / Narrator / Dialogue / KP英語・英語解説 / 固定Shell) | なし(英語) | `:1085-1130` | 英語adapter。対象外 | - |
| Adv(b1b) | 全Section | **なし**(`:581-582` `language="en" if adv`、`:1076` `charon_en`、`has_japanese_title=(level=="a2")` `:2340`、KPは英語+英語解説) | 同`run_tts_stage` | 対象なし | `:1518` |

## 3. scope外ツール・別入口の扱い(取りこぼし確認)
| 入口 | file:line | scope | 扱い |
|---|---|---|---|
| X b1b段 | `er019_family_x_audio_production_runner_01.py:1658` | X | 日本語なし(上記) |
| X 継承再構築 | `er019_family_x_validation_inheritance_01.py:429,520`(`@family_scope("X")`)/`er019_family_x_clobber_restore_03.py:41` | X | J11再判定。新層は**再判定の判定核に含めない**(保存採用転写に最終ANDゲートのみ。WIRING_DESIGN (d)) |
| X support再生成 | `er019_coffee_s3_support_regen_01.py:138`(`evaluate_attempt_ja_with_cascade_detail`直接呼出) | **scope未設定**(`:187`はrunnerをimportするだけでdecorator無し) | scope外=従来挙動。X/Y/Z「正式Production経路」ではない補助tool。変更しない(fail-safe)。使う場合は`run_scope("X")`で包む運用(02で注記) |
| Xの個別承認tool | `er019_fx_moon_title_individual_approval_01.py` | - | HUMAN_APPROVED記録のみ(判定を変えない) |
| Z E2E | `er026_family_z_fiction_production_runner_01.py`(`run_tts_stage`を呼ぶ) | Z | `er063:1518`のdecoratorで覆われる |
| HR Lock再判定 | `er109_hr_lock_rejudge_01.py:206`(`xz.run_scope("X"/"Z")`) | X/Z | 既存ツール。保存転写+現行judgeの再判定は現行どおり(新層で結果が変わるのは「現行judgeが新層込みになる」ため。02Aで挙動確認) |
| legacy A/B/C | `er012_b_family_production_runner_01.py`/`er013_family_c_production_runner_01.py`/`er003_v1_*` | **scope None** | 共有adapterは通るが新層は**非活性**(`current_scope()`がX/Y/Zでない)。出力byte同一をTEST_PLAN T-Aで固定 |

## 4. 対象外の理由(記録)
- Adv(b1b)×{Preview, Comment, KP, 本文, In One Line, Dialogue}: 英語音声のみ。日本語音声が存在しないためJA ASR judgeに到達しない(§2の生成点で確認)。
- Std(a2)の英語Section(Topic intro, 本文, In One Line, KP英語, 固定Shell, Dialogue): 英語adapter(`er006_secondary_asr_01.py`)。本ID(日本語ASR)の範囲外。
- Charon JA(`generate_charon_japanese`、`voice01:527`): X/Y/Z Std JA Sectionは使わない。A/B/C legacy経路のため、scope Noneで従来のまま。
- 画面表示専用の日本語(KPの`display_gloss` `er019:2009,2343`、`er063:2545-2676`のページ表示): 音声化されない=ASR対象外。

## 5. 集計(02Aで確認する項目つき)
- 対象Section数: X 4 / Y 4 / Z 4(Std各: 日本語題・Preview・Comment・KP日本語意味)=12 Section。Advは0(理由は§4)。
- 配線点: JA adapter 1関数(+ Store再利用ガード/継承/最終制作報告の付随3点)。Section/Familyごとの追加配線は不要(scope decoratorが既存、全て静的確認済み)。
- 未確認(02Aのruntimeで確認): (a) Z Stdの`comment`が実際に`ja_simple`を通ること(`:1138`の`"comment": preview`+`:581-582`から静的には確認済み)。(b) Yの`xr._generate_key_phrase_segments_a2`がY scope内で呼ばれること(`:744`が`:639`のdecorator内=静的確認済み)。(c) X/Y/Z各stage entryで`current_scope()`が実際にX/Y/Zになること(`run_scope`のfinally復元を含む)。
