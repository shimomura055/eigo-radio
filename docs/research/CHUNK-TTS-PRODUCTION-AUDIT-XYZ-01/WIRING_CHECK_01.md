# WIRING_CHECK_01 — Chunk TTS(分割+0.2秒): Family×レベル×経路の配線確認(コード・テスト読解、API 0、Production file編集0)

管理ID: CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01(2026-10-26)。判定語彙: 【配線済み・発火実績あり】/【配線済み・本文構造上不発火】/【配線なし(仕様上対象外)】。**「関数が存在する」「設定ON」だけでPRODUCTION_WIREDと判定していない**(判定はFable。runtime evidenceは`RUNTIME_EVIDENCE_01.md`)。
共通module: `er117_chunk_tts_production_01.py`(`CHUNK_PLANNER_VERSION=chunk_tts_v1_x_paragraph_z_r1_20261025` :23、`EXTRA_PAUSE_SECONDS=0.2` :24、flagなし=既定で有効)。numpy+標準libのみ。

## 1. 分割条件・位置決定・0.2秒(Family×レベル)
| Family | レベル | 分割条件(コード) | 分割位置の決定 | 0.2秒の挿入・組立 | 判定 |
|---|---|---|---|---|---|
| X | Adv(b1b) | 本文part1〜3(`full_story_part{n}`)が空行区切り段落2つ以上(`er117:29 X_MIN_PARAGRAPHS_FOR_CHUNKING=2`、`:94`)。1段落partは分割なし | 段落境界のみ(`split_x_paragraphs` :83-84、`plan_x_part` :87-101。非可逆検査あり) | chunk間のみ0.2秒=24kHzで4800 sample(`pad_samples`)。親wav=chunk raw PCM連結+無音(`compose_gained_parent`)。組立はchunk別gain→pad→48kHz(`er019:2098-2118`) | 配線済み・発火実績あり(uk_train、coffee_prices) |
| X | Std(a2) | **なし**。`generate_family_x_a2_segments`(`er019:1743`)・`stage_assemble_family_x_a2`(:2589)にchunk経路なし。`--level a2`で`_k`指定は拒否(`:959-961`) | — | — | 配線なし(仕様上対象外)。testで固定: `er117_x_chunk_wiring_test_01.py:194-213` |
| Z | Adv(b1b) | narrator story clipで語数>100(`er117:26 Z_SPLIT_THRESHOLD_WORDS`)。`k=ceil(語数/100)`(:152)、最小chunk 25語、引用の途中で切らない、分割点がなければ不変(:157-160) | 段落境界優先(priority 0)>文境界、各cutは残語数の等分に最も近い候補(:161-165)=B_r1。Dialogue/話者切替clipは対象外(:145-146)。既存150語超clip分割(er013)は先に走り不変 | chunk間0.2秒、clip間gapは従来(narrator後0.5秒等)。`er063:585-600`(ClipSpec展開)、`:1853-1872`(整合検査→chunk別gain→合成) | 配線済み・発火実績あり(tell_tale、melos) |
| Z | Std(a2) | **なし**。`er117:143-144` `level != "b1b"`→`chunked=False, reason="level!=b1b(Std対象外…)"`。`er063:592`も`level == "b1b"`条件 | — | — | 配線なし(仕様上対象外)。test: `er117_z_chunk_wiring_test_01.py:130-132`(Stdはchunk有無でClipSpec列が完全一致)、`:202`(`chunk_plans_from_specs(make_plan("a2"))=={}`) |
| Y | Adv(b1b) | `er121_family_y_audio_01.py:264-272 plan_y_chunks`が各Y segment(8個)へ`er117.plan_x_part`を適用。**各segmentが1段落のため`paragraphs=1<2`→chunked=False** | 段落境界(X規則)。話者切替(intro→voice等)は構造上結合も分割もされない | 配線コードあり(`:363-390`生成、`:347-360`親再構築、`:675-702`整合検査、`:805-826`組立summary)。実Y runでは0.2秒挿入0箇所 | 配線済み・**本文構造上不発火**(実音声での発火実績なし。合成testのみ) |
| Y | Std(a2) | **なし**。`er121_family_y_structure_01.py:111 CHUNK_TTS_Y_LEVELS=("b1b",)`。`audio:296`で`level in ys.CHUNK_TTS_Y_LEVELS`のときだけplan、a2は`not_applied_reason`を記録(:309) | — | — | 配線なし(X継承の対象外)。**仮にStdを対象に含めても1段落契約のため分割0** |

## 2. 経路別(初回/retry/fallback/regeneration/resume)
| 経路 | X Adv | Z Adv | Y Adv | 備考 |
|---|---|---|---|---|
| 正式初回Production | `er019`のb1b生成関数内(`:1443-1447` plan作成・`reconcile_saved_plan`・stale除去、`:1502-1504`でchunked partだけ`_generate_x_body_part_chunked`、`:1529-1530`親集約entry、`:1546-1549` evidence) | `er026_family_z_fiction_production_runner_01.py:2267-2317`(plan展開、`chunk_plans_from_specs`)→`er063:1402-1458` | `er121_family_y_audio_01.py:397`(b1b生成の入口で`_record_chunk_decision`、課金前にplan保存・Y適用表の逸脱は課金前STOP :288-290)→`:363-390` | いずれも別flagなしの正式経路 |
| retry | chunkは通常segment/clipと同じ関数・同じ3 attempt・同じfallback(chunkごと)。chunk失敗は後続chunkを止めない(R1) | 同 | 同(`:363-366`) | `er020_tts_retry_local_rewrite_01.py:123-126,130-132,168-170`: chunk IDの`resolve_narrative_role`=FULL_STORY(import時自己検査で外れると即RuntimeError) |
| fallback / Local Rewrite | 共有Gate・HR Lock・telemetry・sha stale検知がchunk単位に効く(`CURRENT_SPEC.md:2942`)。LR注記も親行に出す | 同(`er063:2019`) | 同(YのHR採用`er121_e1_hr_adopt_r0_01.py`はchunk idを扱わない=grep `chunk`0件。**E-1は非chunkで未発火のため実害なし、将来chunk化segmentをHR採用する場合は未対応**) | 実runでLR/fallbackがchunkで発火した証拠はない(attempt_count 1、LR None=`RUNTIME_EVIDENCE_01.md`) |
| regeneration / replan | 同一本文・同一版でplanが変わればSTOP(`reconcile_saved_plan`、replan禁止)。旧版chunk entryは破棄(`drop_stale_chunk_entries`) | 同(`er063:1406-1408`) | 同(`audio:298-300`) | `CHUNK_PLANNER_VERSION`で版管理 |
| resume | 既存OK chunkを再利用(再課金なし)。`--only-segments <親>`は全chunkへ展開(`er019:965-972`) | `--only-clips <親>`は全chunkへ展開(`er063:1403-1405`)。reuse_keyはchunk specにのみ`chunk_tts`追加(`:813`、非chunk keyはバイト不変) | `audio:311-336` | **実run観測あり**: X `part2_hr_evidence_01__run_r1/r2`のchunk entry `reused=true, attempt_count=0`(再課金なしでresume) |
| 親wav整合 | `verify_parent_integrity`(chunk集合・順序・語数・版・本文)をaudio読込前に、`verify_raw_parent`(整数sample一致)をtarget_rms算出前に(`CURRENT_SPEC.md:2943`)。`er019:2098-2118` | `er063:1853-1856` | `audio:675-702` | 欠落・重複・順序変更はfail-closed |
| Validator / Gate | X Style profile M3 Gateはchunk entryを列挙、親は対象外(M1) | 共有Gate(`verify_z_speed_profile`はAdv narrator chunkを対象) | `y_style_profile_gate.json`、chunk親の人間承認参照対象外 | — |

## 3. 回帰test(レベル条件を固定しているもの)
| test | 内容 | 本監査での実行 |
|---|---|---|
| `er117_chunk_tts_production_01_test_01.py` | planner/合成/整合/reuse(43件)。`level!=b1b`でZ不変 | 実行: 43 tests、29 OK/14 error(全て`ImportError: cannot import name 'genai' from 'google'`=本環境に`google.genai`未導入。HEAD/変更前後ともに同じ環境差。接続試行は`netblock_harness_01/sitecustomize.py`遮断下でゼロ) |
| `er117_x_chunk_wiring_test_01.py:194-213` | `test_std_a2_path_untouched_no_chunk_ids`、`_k`のa2拒否(I5) | `genai` ImportErrorでmodule import不可(環境差) |
| `er117_z_chunk_wiring_test_01.py:130-132,202` | Std: ClipSpec列がchunk有無で一致、`chunk_plans_from_specs(a2)=={}` | 同上 |
| `er121_family_y_audio_chunk_test_01.py:137,205-329` | `test_single_paragraph_segments_are_not_chunked`(1段落は分割しない=期待値固定)、複数段落fixtureでの生成・0.2秒組立・resume・失敗chunk・scope復帰fail-closed | 同上(`genai`) |
Std除外を『期待値』として固定しているtestは上3件(X:`:194-213`、Z:`:130-132,202`、Y:Std側のapplied=false検査)と`er117`のlevel条件。**本委任では是正しないため変更していない**(拡張する場合の更新対象)。

## 4. DEV/Trial専用経路との差異
- Trial: X=`er113_fx_paragraph_chunk_trial_01*`(`build_chunk_plan`、Advanced `uk_train`)、Z=`er114_fz_narration_chunk_trial_01*`(`plan_clip_chunks`、Adv `tth_*_adv`、`er026_output/family_z_dev_trials/fz_narration_chunk_01/chunk_plan_*.json`)。Production plannerとの一致は`planner_fixture_01.json`で凍結(Z 16 run/385 clip/15分割clip、X parts.json 421。`CURRENT_SPEC.md:2947`)。
- Trial→Production差分: chunk entryを通常segment entry化(共有Gate・HR Lock・stale検知・resumeが無変更で効く)、chunk失敗の後続継続(R1)、再計画禁止、版管理。方式(分割規則・0.2秒)は不変。
- Trial成果物は`user_test/`・`er026_output/family_z_dev_trials/`等の別dir。Productionのflagで切り替わる構造ではない(X/Zは常時有効)。

## 5. 気づき(配線)
1. **chunkは常時有効でflagがない**。レベル対象は`level == "b1b"`のハードコード(X:関数配置、Z:`er117:143`/`er063:592`、Y:`CHUNK_TTS_Y_LEVELS`)であり、Std拡張はflag切替ではなく3 Familyそれぞれのコード変更になる。
2. Std拡張に必要な新設計(許可条件(c)不成立の根拠): Stdは`generate_a2_segment_with_slowdown`でsegment wav全体にffmpeg atempo(6%減速)を後処理で掛ける。無音も同率で伸びる(Y E-1実測: 無音平均535→564ms=+5.4%、`CHUNK_WIRING_CHECK_01.md`§3-6)。chunk化すると『chunk別に減速してから0.2秒を挟む』か『chunk連結(0.2秒込み)後に減速』かで追加ポーズが0.2秒か約0.212秒かに分かれ、さらにZは`verify_std_english_slowdown`、X/ZのreuseキーとGateの再設計が要る。これは『既存の承認済み分割規則を同一条件で適用する』だけでは決まらない新規設計であり、Opus条件A該当の可能性がある。
