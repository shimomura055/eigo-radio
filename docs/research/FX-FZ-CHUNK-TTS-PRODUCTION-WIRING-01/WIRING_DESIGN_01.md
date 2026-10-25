# WIRING_DESIGN_01 (FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01 Phase 0、設計のみ。API 0・Production file編集0)

Status: APPROVED_FOR_PRODUCTION(ユーザー2026-10-25)・**実装中(委任_02)→WIRED_PENDING_FABLE止まり(PRODUCTION_WIRED判定はFable)**。Opus条件Aレビュー=条件付き(`OPUS_REVIEW_01.md`、M1〜M4必須・I1〜I11・R1〜R4)。**下の§R(改訂)が本文に優先する**。
照合: `EXISTING_SPEC_CHECK_01.md`(経路図・配線点X1〜X4/Z1〜Z5・差分表)。ドラフト実装+test=`chunk_tts_core_draft_01.py`・`tests_draft_01.py`(24 PASS、採用Trial plannerと実runで出力一致を確認済み)。

## §R. 改訂(委任_02、Opus条件A M1〜M4・I1〜I11・R1〜R4の反映。本節が下の旧本文と食い違う場合は本節を正とする)

実装: 共通module `er117_chunk_tts_production_01.py`(+`er117_chunk_tts_production_01_test_01.py` 41 test)、`er020`の`resolve_narrative_role`にchunk ID形+import時自己検査(I4)、期待値凍結 `planner_fixture_01.json`(生成=`freeze_planner_fixture_01.py`)。X/Z配線は§R-X/§R-Z。

| ID | 反映内容(実装の置き場) |
|---|---|
| M1 | X `er019_family_x_style_profile_01._gate_targets`/関連検査をchunk entryを列挙するよう拡張(親aggregateはM3の対象外。親には`style_profile`が無いのでコピーもしない)。`attach_segment_profile_record`は**chunkごと**に呼ぶ。C8の編集表に`er019_family_x_style_profile_01.py`を追加。test「chunk k2だけminimal_fallback→BLOCK」「親の値をchunk1からコピーしても素通りしない」 |
| M2(a) | `er117.refresh_parent_status`は**失敗・未生成でも親を常に書く**。statusは`derive_parent_status`がplanのchunk id一覧から導出(entry無し=`status_fn(None)`=UNVALIDATED)。非全合格は status=`CHUNKS_NOT_ALL_VALIDATED`(共有Gate `_segment_gate_status`の承認照会対象外の値。**親idへ人間承認を記録してもGateを迂回できない**=test固定) |
| M2(b) | 全chunk wavが揃っていれば親wavを(欠落・古い場合は)再合成しsha更新。一部欠けなら親wavに触れずsha=None(Gateはstatusで止める) |
| M2(c) | X: `stage_assemble_family_x_b1`の`_style_profile_gate_blocked_summary`より前。Z: `run_audio_gate`冒頭と`run_assembly`。いずれも`verify_parent_integrity`(+`verify_raw_parent`)を音声を読む前に実行 |
| M2(d) | 親`chunk_tts.human_approved_chunks`を記録(statusはOKに丸まるが事実は残る)。`chunk_gate_statuses`・`deviation_chunks`も記録 |
| M3 | Z evidenceは案A不可。`copy_reusable_run_assets`でテキスト系のみ複製した新runを作り`tts_a2,tts_b1b,provision_shell,gate,assemble,pages,page_verify`を**1起動**(両level)。費用見積 約30〜40円。他agentのer026 Part 1配線commit後に起動 |
| M4 | X evidenceは`theme_out_dir`全体を複製(entry_point.json・theme直下`audit/style_profile.json`を含む)。起動前に記録profile==現行Production profile、M3 `checked`にchunk idを含むことをevidenceへ |
| I1 | `er117.drop_stale_chunk_entries`(planner_versionが現行と異なる/無いchunk idの前回entryは再利用しない)をXの`_cached`読込直後に適用。Zはreuse_keyに`chunk_tts.planner_version`を含むので自動 |
| I2 | `er117.compose_gained_parent(..., gain_fn=p9a.compute_gain_for_target_rms, rms_fn=p9a.rms, peak_fn=p9a.peak)`。gain式は再実装しない(testでp9a直接呼出と一致) |
| I3 | `planner_fixture_01.json`: ディスク上の全Z run(16 run・385 clip・split 15 clip)と全X parts.json(421)のTrial planner出力(chunk本文sha・語数・boundary_kind・first/last段落・paragraph_info_lost)を凍結。Production testはDEVのer113/er114をimportしない(凍結スクリプトのみTrialをimport。`docs/research`配下) |
| I4 | `er020`のimport時自己検査(`full_story_part1_k1`・`full_story_part3_k10`・`full_story_part2_c1_k2`がFULL_STORYへ解決されなければimport失敗)。X runnerの既存import時検査(`_REQUIRED_FULL_STORY_SEGMENT_IDS`)にchunk IDを追加 |
| I5 | X `_VALID_ONLY_SEGMENT_RE`: `full_story_part[1-9]\d*(_k[1-9]\d*)?`(`_k`は本文partにのみ)。`--level a2`で`_k`指定は`validate_only_segments_args`で拒否。親名指定=当該partの全chunkに展開 |
| I6 | Z `run_assembly(..., chunk_plans=)`に`load_level_inputs`のplanを渡し、`verify_parent_integrity`を実行 |
| I7 | 親aggregateに`voice`/`style.instruction_label`/`canonical_text`(+`clip_kind`/`role`等)を持たせる(`display`引数)。ページ行は親entryを読んでも「-」にならない。chunkの`audio_text_deviation`は親`deviation_chunks`からページ注記へ。gain_report親keyには値を書かず`chunk_tts.<親>`にchunk別gainを記録 |
| I8 | 合成長は整数サンプル一致(`verify_composed_samples`)。親wavは**PCM16のバイト連結**で書く(float往復の1LSBずれを作らない)。組立時`verify_raw_parent`(親wav==ディスク上chunk wavの生連結)に合格してから親wavをtarget_rms基準に使う |
| I9 | Zのchunk本文は`normalize_for_tts`後(引用符の直線化・`**`除去)。clip.textが既に正規化済みかは全run実データで確認(§R-Z) |
| I10 | 回帰はclean worktree(HEAD+自変更のみ)で取る |
| I11 | `er019_family_x_validation_inheritance_01.derive_expected_texts`(手動CLI): chunk labelを導出できる拡張は行わず**既知の制限として記録**(§R-X。chunk idの`SKIPPED_NOT_SELECTED`継承は`try_inherit_from_cached`が汎用なので動くが、手動CLIの期待text導出はpart単位のまま) |
| R1 | **採用**: X/Zともchunk失敗後も後続chunkの生成を続ける(旧設計(b)の「失敗chunkでループ停止」は撤回)。OK chunkは再利用されるので無駄な再課金は無く、未生成entryという余計な状態を作らない |
| R2 | Zは`_CLIP_ID_RE`を広げず、Gate箇所(`verify_z_speed_profile`・`verify_std_english_slowdown`・`run_audio_gate`)専用の別正規表現`_CLIP_OR_CHUNK_ID_RE`を追加。入力検証(`build_level_plan`の story clip id)・`comment_after_segment_ids`・`part_to_clip_id`は厳密なまま |
| R3 | pww警告→ページ行の紐付け(`_warn_entry_to_clip_id`)で`_k\d+`を親clipへ対応 |
| R4 | role解決の不変testは手書き一覧でなく既存`*_output`の全results segment idで比較(`TRoleResolution`) |

### §R-共通の設計確定事項
- **親wav定義(仕様)**: 親wav=「生chunk(gain前)を0.2秒(4800 sample@24kHz)の無音で連結した24kHz mono PCM16」。X `apply_family_x_b1_gain`/Z `run_assembly`のtarget_rms基準に使われる(`(rms(preview)+rms(part1_または_c1))/2`の式は無変更)。**0.2秒の無音を含めて計算するためRMSが生chunk平均より約0.06dB小さい**(Opus論点2。仕様として記録)。peak cap(0.95)発動chunkは`compose_gained_parent`の`peak_capped`とevidenceに記録するのみ(新Gateは作らない)。
- **planner**: 単一の`CHUNK_PLANNER_VERSION="chunk_tts_v1_x_paragraph_z_r1_20261025"`。規則を変えたら必ず更新(reuse_key/chunk entry/親entry/保存plan/整合検査が版で旧chunkを拒否)。
- **resume**: planは純関数。`audit/chunk_plan_<level>.json`に保存し、同一本文sha・同一版で分割が食い違えばSTOP(`reconcile_saved_plan`)。
- **対象外**: X Std(a2)本文・in_one_line・他segment、Z Std全clip・Dialogue・100語以下narrator・KP・Comment・Preview・Topic intro。経路は`chunked=False`/対象外で分岐前に従来関数へ抜ける(バイト不変testで固定)。

## 0. 設計方針(要点)
1. **chunkは「既存のsegment/clip entryと同じ型の1 entry」にする**。これにより既存のGate・HR Lock・ASR telemetry・費用ログ・sha stale検知・checkpoint/resume・STOP/Budget guardが**共有コードを変更せず**chunk単位に効く。新しい安全装置は作らず、既存の上限(`PRODUCTION_MAX_TTS_ATTEMPTS`=3等)も回避しない。
2. **親(part/clip)の下流consumerは不変にする**: 親wav(`narration/<parent>.wav`)を「**生chunkを0.2秒無音で連結した24kHz mono**」として書き出す。target_rms計算・player行・hash検知・既存読込(`read_wav_float`)がそのまま動く。組立時のみ親を**chunk別gain**で再合成する。
3. **新規module 1つ**(`er117_chunk_tts_production_01.py`、仮称。着手時に番号の空きを再確認)+ 既存file内の**関数単位の限定的な追加**。planner・合成・整合検査・reuse_key部品・evidence recordを集約。承認済み仕様なのでflagは設けない(DefaultOffIsolationの対象外=APPROVED_FOR_PRODUCTION)。撤去はcommit revert。
4. 対象はX=Advanced本文3 part、Z=Advanced narrator>100語clipのみ。Std・Dialogue・短narrator・KP・Comment等は**コード経路が分岐前に抜ける**(`chunked=False`なら従来関数・従来entryのまま=出力バイト不変)。

## 共通

### C1. 新規module `er117_chunk_tts_production_01.py`(draftは`chunk_tts_core_draft_01.py`)
`CHUNK_PLANNER_VERSION`(規則を変えたら更新)/`plan_x_part`/`plan_z_clip`/`compose_raw_parent`/`compose_gained_parent`/`build_parent_aggregate`/`refresh_parent_status`/`verify_parent_integrity`/`verify_composed_duration`/`chunk_reuse_key_fields`/`evidence_record`。numpyのみ依存(重い`p9a`はimport連鎖にgoogle.genaiを含むため、合成関数はrms/peak関数を引数注入=testが軽量)。

### C2. target_rmsの基準 = 親wav(生chunkの0.2秒連結)
X `er019:1767`・Z `er063:1761`の式は**無変更**。Trial(固定値)との差を実データで定量した(uk_train Trial wav 20 chunk、読取のみ):
- X: 現行A: preview 0.1000、part1 0.0830 → target **0.09149**。B_r1の生chunk連結RMS 0.0932 → target **0.0966**(+0.47dB)、B_r2 0.0950 → **0.0975**(+0.56dB)。差はTTS出力レベルのtake間ばらつき(chunk RMS 0.070〜0.109)の範囲で、**現行方式でも`part1`の生RMSが変わればtargetは動く**(Aを再生成したA_r2でも動く)。Trialの固定0.09149は比較条件統制のためで、Productionの式ではない。
- peak頭打ち(`max_peak=0.95`): target 0.09149では20 chunk中0、**0.0966/0.0975では1 chunk(B_r2 part1の3番目)が頭打ち**(必要gainでpeak 0.964/0.973→0.95にcap、RMSがtarget未達)。既存`compute_gain_for_target_rms`の定義どおりの挙動で正常(新Gateは作らない)。**evidenceにchunk別 gain/post-RMS/peak_afterを記録**し、cap発動chunkを明示する。
- 全体への影響: targetが+0.5dB動くと同episode内の全segment(intro/comment/KP等)のgainも同量動く(従来もpart1 RMSで動く)。ヘッドルーム弁(peak>0.98)は既存のまま通す。
→ **推奨: 通常式を維持**(Production仕様の延長。Opus論点1)。代案=「第1chunkのRMSだけ」または固定は、いずれも独自基準になるため採らない。

### C3. 親集約entryのstatus導出(共有Gateを変更しない)
- chunk entry(`full_story_part1_k1`等)は**通常のsegment entry**として`results["segments"]`に入る(Gateが`status==OK`・sha・HR承認を直接評価)。
- 親entry(`full_story_part1`/`<clip>`)は`segments`に**集約entry**として残す(`chunk_tts.chunk_ids`、`words`、`boundary_kinds`、`extra_pause_seconds`、`raw_parent_sha256`、`canonical_text`=親原稿、`path`/`sha256`=親wav)。statusは `refresh_parent_status` が**共有Gateと同じ判定関数**(`asm._segment_gate_status(entry, name, approvals)`、approvals=`asm.human_approval_path`)でchunkを評価して導出: 全chunkが`VALIDATED`/`HUMAN_APPROVED`なら`OK`、それ以外は最悪chunkのstatus(`STOPPED`/`HUMAN_REVIEW_LOCKED`)。
- `refresh_parent_status`はTTS stage末尾(結果保存直前)と、**gate/assemble stageの入口**で冪等に実行(人間がchunkを承認した後の再gateで親も通る)。親に独自の承認を要求しない。
- 親のASR判定(`asr_judgement`)は**コピーしない**(PASS_WITH_WARNING listing=`pww`が二重表示しないため。警告はchunk entryのみに残り、`_warn_entry_to_clip_id`は未知IDを`None`=リンクなし表示で安全)。
- 代案(共有Gate `_segment_gate_status`に`aggregate_of_chunks`分岐を足す)は全Family共通コードへの変更になるため採らない(Opus論点2で確認)。

### C4. role解決の拡張(必須)
`er020_tts_retry_local_rewrite_01.py:125-150 resolve_narrative_role`へ**追加のみ**: X `full_story_part[1-3]_k[0-9]+`、Z `full_story_part[1-3]_c[0-9]+_k[0-9]+` → `FULL_STORY`。既存ID(`full_story_part1`・`…_c3`・`comment_*`等)の結果は不変、`fullmatch`のため`_original`/`_heading`等は引き続き不一致。`connected_speech_enabled_for`が自動でchunkにも効く。test: 既存ID全件の戻り値スナップショット一致+新ID解決+隣接誤一致(`full_story_part1_k`・`_k0x`等)が`None`。

### C5. 欠落・重複・順序変更の防止(多層)
1. **planner内**: `normalize(結合chunk text)==normalize(親text)`、`Σchunk語数==親語数`(違反は`ChunkIntegrityError`でplan自体が失敗。Trial plannerのassertと同一、draftで移植・test済)。
2. **生成時**: 各chunkのcanonical_text(=計画のchunk text)とtext shaをentryへ記録。`news_tail_fix`のASRが**chunk text全体を照合**する(既存Gate)ので、chunk内の欠落/重複は従来どおり検出。
3. **親集約/組立入口**: `verify_parent_integrity(plan再計算, 親text, chunk entries, 親entry)` — chunk集合==計画、順序(`chunk_ids`)==計画、語数列==計画、`planner_version`一致、canonical_text==計画。違反は`FamilyXZ…Stop`(fail-closed、組立に進まない)。
4. **合成後**: `verify_composed_duration`(親wav長==Σchunk長+0.2×(n−1))、親wav sha256を集約entryへ記録(Gateのstale検知が効く)。
5. **記録**: `timeline.json`/`run_summary_assemble.json`/`gain_report`に `chunk_tts.{parent_id: {chunk_ids, words, boundary_offsets_s, pad_s, gains, post_rms, peak_after}}`。
6. **resume時の再計画禁止**: planはcanonical text・paragraph構造・`CHUNK_PLANNER_VERSION`の純関数(決定論)。resume/regenerateは**同じ入力から同じplanを再構成**し、保存済みplan(`audit/chunk_plan_<level>.json`)と一致しなければ(同一text・同一versionで不一致)STOP。textが変わった場合のみ再計画し、旧chunk entryはreuse_key(text sha)不一致で再利用されない。

### C6. reuse / 旧音声の誤再利用防止
- X: chunk単位に`_generate_or_reuse(cached, chunk_id, chunk_wav, …, expected_text=chunk.text)`(既存関数のまま)。chunk idは旧cache(`full_story_partN`のみ)に存在しないため旧part音声は**構造的に再利用されない**。加えて親は`chunked`計画のとき旧entry(`chunk_tts`無し)を無視して再構築。`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`はbumpしない(topic_intro等の再生成を誘発して費用を増やさないため。chunk方式の識別はchunk entryの`chunk_tts.planner_version`で行う)。
- Z: `build_reuse_key(spec)`に`chunk_tts: {planner_version, parent_id, index, count, extra_pause_s}`を**chunk specにのみ追加**(`chunk_reuse_key_fields`)。非chunk specのkeyはバイト不変=既存の再利用を壊さない。旧親clip entryはplanに無いので`prune_cached_to_plan`が落とす。
- Master Audio Store: 本文/narratorは元々対象外(EXISTING_SPEC_CHECK §0-6)。KP/shellは不変。

### C7. runtime evidence項目(各chunk entry + 親集約 + `audit/chunk_tts_evidence_<level>.json`)
`tts_model_id`(actual)、`voice`、`style_prefix_sha256`(Aと同一か)、`tts_backend`、`planner_version`、分割位置(`boundary_kind`=paragraph/sentence、`first_para/last_para`、語数)、chunk数、`extra_pause_seconds`(0.2)と各境界の実測offset、gain/post-RMS/peak_after(cap発動chunk)、attempts/`instruction_type`(minimal_fallback)/`local_rewrite_recovery`/`en_pronunciation_resolver_info`、ASR判定(primary/secondary、`asr_judgement`)、費用(`cl.segment_context(chunk_id)`のraw_usage_log集計)、所要(生成+検査、cool-down分離)、`reused_from_previous_run`。これらはTrialの`gen_result`と同項目(`er113…:generate_chunks_phase2`)で、Trial 23 chunk×全項目が取得できることを確認済み。

### C8. 編集箇所と衝突回避(実装委任用)
並行agentがuncommittedで編集中のfile: `er019_family_x_audio_production_runner_01.py`・`er026_family_z_fiction_production_runner_01.py`・`er063_family_z_audio_01.py`(`git status`で`M`を確認済み、FAMILY-Z-STUDY Part 1配線/FX-CORE-NUMERIC配線)。→ **作業treeを共有したまま、関数単位の最小編集にし、commitは一時index方式**(`git read-tree`→`git apply --cached`で自分のhunkのみ→`git commit --only`相当、他agentのhunkをstageしない)。編集関数:

| file | 関数/箇所(追加のみ・既存挙動不変) | Family |
|---|---|---|
| `er117_chunk_tts_production_01.py`(新規)+test | 全体 | X/Z |
| `er020_tts_retry_local_rewrite_01.py` | `resolve_narrative_role`にchunk ID正規表現を追加(+定数1) | X/Z |
| `er019…` | `generate_family_x_b1_segments`内の本文3 partのループ(:1143-1160)を`_generate_body_part_chunked`呼出へ(`name in _BODY_SEGMENT_NAMES`かつplan.chunkedのときのみ)。新ヘルパ`_generate_body_part_chunked`、`_VALID_ONLY_SEGMENT_RE`の拡張 | X |
| `er019…` | `load_family_x_b1_sources`(chunk wav読込・`body_chunks`保持)、`apply_family_x_b1_gain`(chunk別gain合成)、`build_family_x_b1_timeline`/`stage_assemble_family_x_b1`(chunk境界記録、`verify_parent_integrity`呼出) | X |
| `er063…` | `build_level_plan`(chunk specへの展開、`_CLIP_ID_RE`の拡張)、`build_reuse_key`、`_run_tts_stage_impl`末尾(親集約+親wav+`only_clips`展開)、`run_audio_gate`/`verify_z_speed_profile`/`verify_std_english_slowdown`(chunk IDを対象に)、`build_z_sequence`/`run_assembly`(chunk別gain+0.2/0.5秒、`gs`ラッパ) | Z |
| `er026…` | `load_level_inputs`(paragraph構造の供給=`plan_z_level`呼出+plan保存)のみ | Z |

`build_pages`/`build_page_rows`/Part 1(study)/Writer系/B3系は**触らない**(timelineは親1エントリのまま=ページ行は不変)。

## Family X

### (a) 分割planner
`plan_x_part(parts["partN"], "full_story_partN")`: 空行区切りの段落=1 chunk(10段落→4/3/3 chunk、Trial `er113 build_chunk_plan`と一致をtest済)。**段落が1つのpartは分割しない**(従来の1 call)。可逆性は空白正規化後の一致で検証(`tts_safe_news_en`は改行を空白へ畳むので段落ごとに掛けて連結=全体適用と完全一致、Trial test済)。短段落の併合・最小語数は**設けない**(Trial条件=段落単位。最短14語chunkまで実証。chunk語数はevidenceに記録のみ)。
### (b) 生成
`_generate_body_part_chunked(name, text, cached, …)`: 各chunkで既存と**同じ呼出**(`_pnap_supply(chunk.text, tts_safe_news_en(chunk.text))`→`news_tail_fix.generate_news_narration_wide_margin(…, enable_connected_speech_equivalence_layer=cs(chunk_id), enable_repetition_qa=True, enable_pronunciation_resolver=True, style_prefix_override=_role_style("FULL_STORY"), tts_backend)`)。出力`narration/<name>_k<j>.wav`。Voice/Style/modelは不変(`_role_style`・`tts_backend`を共有)。**直列**(chunk順)。~~chunkのGate失敗でループを止める~~ → **§R R1: 失敗後も後続chunkの生成を続ける**(HR Lockはchunk単位)。retry/fallback/Local Rewrite/cool-downは関数内の既存規約をそのまま踏襲。親集約entryは失敗時も常に書く(§R M2。statusはplanから導出)。
### (c) 組立
`load_family_x_b1_sources`: チャンク化したpartは`narration/<name>_k*.wav`を計画順に読み`sources["body_chunks"][name]=[mono…]`、`b1_segments[name]`(target_rms用)=親wav(生連結)。`apply_family_x_b1_gain`: `name in body_chunks`なら `compose_gained_parent`(chunk別gain→0.2秒→連結)→`mono_24k_to_stereo_target`。それ以外のsegmentは従来関数のまま。本文part間の既存gap(`build_family_x_b1_timeline`)は不変(親=1 timelineエントリ)。ヘッドルーム弁は既存。gain_reportへ`b1_<name>_chunks`を追加(既存keyは不変)。
### (d) Store/reuse
§C6のとおり(part単位cache+chunk単位cache、Master Store非経由)。
### (e) retry/regeneration/resume
- 初回: 上記。中断(STOP/HR/プロセス死)後の同一out_dir再実行: OK済みchunkは`_generate_or_reuse`で再利用(API 0)、失敗chunkだけ再生成(従来はpart全体を再生成=むしろ節約)。
- `--only-segments full_story_part2`: `_VALID_ONLY_SEGMENT_RE`に`(_k[1-9]\d*)?`を追加し、親名指定は当該partの全chunkを対象に展開、`_k`指定は当該chunkのみ。`SKIPPED_NOT_SELECTED`の継承(`validation_inheritance`)はchunk単位で同様。
- 本文変更(Writer再生成等): parts.json変更→plan再計算→chunk textのshaが変わったchunkだけ`expected_text`不一致で再生成。
- Local Rewrite後: chunk entryに`audio_text_deviation`(既存形式)が残り、親集約が`deviation_chunks`で列挙。再生成は従来どおり`news_tail_fix`内。
### (f) evidence
§C7。X固有: Advanced本文3 part×chunk(10)、`tts_generation_results.json`のchunk entry、`run_summary_assemble.json`の`chunk_tts`。
### (g) 速度・Std
Advは速度後処理なし(chunk後も不変)。**Std(a2)本文は非適用**: `generate_family_x_a2_segments`・`apply_family_x_a2_gain`・`stage_assemble_family_x_a2`は不変。理由=生成後6%減速とchunk別生成の相互作用が未Trial(Fable委任文、ユーザー決定の「未承認の対象拡大を行わない」)。
### (h) 旧処理整理
Xに旧chunk規則なし(P-series `SECTION_JOIN_PAUSE_SECONDS=0.8`は凍結・未使用、`er002_common:58`)。撤去対象なし。旧`full_story_partN`単位の本文生成呼出はchunk化partでは使われなくなるが、**1段落のpart用の従来経路として残す**(撤去しない)。
### (i) test計画
`tests_draft_01.py`(planner/合成/整合/reuse/resume再構成、24 PASS済)+実装時追加: role解決(既存全ID不変スナップショット)、X配線(mockで各chunkが同一kwargsで呼ばれる/Std不変/chunk k失敗→後続未生成/resume再利用/親wav生連結+sha/組立でchunk別gain/旧cache非再利用)、`--only-segments`展開、既存回帰(`er019`系test一式、`er011`/`er020`系、共有assembleのGate test)。**既存testの期待値を新方式に合わせて書き換えない**(本文をchunk化していない既存fixtureが従来経路で通ることを維持)。
### (j) runtime evidence取得計画・費用
既存公開記事1本(第一候補=『英国の電車マナー』uk_train `run_nws_02`、本文10段落)の**Advanced TTS段を新out_dirで再実行**し、完成候補として置く(公開差替えなし)。b1b dirを新out_dirへコピーし(topic_intro/preview/comment/in_one_line/KPは同一out_dir前回results再利用=API 0、本文3 partは旧cacheにchunkが無いため新方式で生成)→assemble→Gate。費用: TTS 10 call+ASR 10 ≈ **4.3〜5円**(Trial B_r1実測4.27円)、retry発生時 +1〜2円。Trial実測のレンジ**5〜10円**(retry/Azure含む上限見込み)で起動前に日次1,000円内を確認(他Family・並行案件の当日使用額を`compute_cost_jpy_so_far`で合算確認)。再起動は委任文が明示した回数のみ。追加evidence(無料): 同out_dirで`--only-segments full_story_part2_k2`を再実行し、親再構築・OK chunk再利用・chunk別再生成を確認(resume/regeneration経路)。
### (k) 量産原価・時間
Trial実測: +約0.30円/Adv本文(+7.5%、10 call vs 3 call、1 callあたり+0.043円)、所要+約6秒。retryは1 chunk再生成で済むため従来(part全体再生成)より安くなる場合あり。70円/記事セット目標への影響は約0.4%。
### (l) CURRENT_SPEC記載案(本実装完了・Fable受入後に反映。今回は案のみ)
> **Family X Advanced本文のTTSは段落単位**(APPROVED_FOR_PRODUCTION 2026-10-25、Trial B0.2)。本文part(1〜3)を空行区切りの段落ごとに独立TTS(同一Voice/Style/model/Gate)で生成し、chunkごとに同一target_rmsへscalar gain(peak≤0.95)、chunk間に固定無音0.2秒を挟み`np.concatenate`のみで結合する(crossfade無し)。段落が1つのpartは単一call。Standard本文・in_one_line・他segmentは従来どおり(Std=6%減速との相互作用が未Trial)。chunkのsegment_idは`full_story_part{n}_k{j}`(role=FULL_STORY)。`CHUNK_PLANNER_VERSION`をresults/reuse判定に記録。「単一TTS call凍結」(ER-003-B1-P6B不採用)はX/Z Advanced本文に限り本方式が例外(英語・Flash-Lite・段落/文単位・chunk別RMS+0.2秒・ユーザー試聴で採用)。
### (m) SSOT更新案 → 末尾「SSOT更新案」節

## Family Z

### (a) 分割planner(er114 `plan_clip_chunks`の移植)
`plan_z_clip(clip, paragraph_texts, level)`: Adv(b1b)のnarratorで語数>100のみ。`k=ceil(語数/100)`、候補=段落境界(優先0)>文境界(優先1、未閉じ二重引用符の途中は除外)、各cutは「残語数の等分」に最も近い候補(優先0があればそれを優先)、最小chunk語数25、境界候補が満たせなければ**不変**(分割しない)。決定論・純関数。段落情報は`load_level_inputs`が持つ原稿(`_level_text_path`)+`segment_plan`の`source_paragraph_indices`から`er062.split_title_body/clean_body_paragraphs`で構成(Trial `plan_run`と同一手順)。**段落結合がclip.textと一致しない場合(段落途中でnarratorとdialogueが切り替わる)は文境界のみ**(`paragraph_info_lost=true`を記録、黙って落とさない)。実run `run_sf_prod_02`では`full_story_part2_c1`(120語→58/62)・`full_story_part3_c1`(126語→65/61)の2 clip・4 chunk、他clipは不変(Trial plannerとの一致をtest済)。
### (b) 生成
`build_level_plan`が対象clipを**chunk ClipSpec**(`clip_id=<parent>_k<j>`、`kind="narrator"`、`extra.chunk={parent_id,index,count,planner_version,words,boundary_kind}`)に展開(親ClipSpecは作らない)。以後は既存の`run_tts_stage`がそのまま回す(narrator generator=`news_tail_fix.generate_news_narration_wide_margin`、Style=`NARRATOR_FULL_STORY_ADV`、TTS_BACKEND、`enable_repetition_qa=True`、`cs(spec)`=chunk idでFULL_STORY)。budget guard・STOP sentinel・`secondary_run_scope`・checkpointは**各chunk=各spec**で自動的に効く。
### (c) 組立
`run_assembly`: `story_clips`(親clip列)は不変。`build_z_sequence`は親clipごとに`story_segments`を作るまま、**chunk化した親のgsだけラッパ**: 親wav(生連結)をtarget_rms基準として読み、`gs(label=親id)`が呼ばれたとき`compose_gained_parent`(chunk別gain→0.2秒→連結)→stereo48kを返す(共有`build_family_c_episode_sequence`[Family Cと共有]は**無変更**)。narrator後の既存0.5秒・Comment2/3の挿入規則は親の直後に1回(=最後のchunkの後)。timeline上は親1エントリ=ページ行不変、`timeline.json["chunk_tts"]`にchunk境界offset・gain・post-RMSを記録。
### (d) reuse_key / Store
§C6。chunk specに`chunk_tts`を追加、planner versionとindexを含む。spec.text=chunk text(=canonical_text_sha256がchunkごと)。Zの既知問題(dialogueのstyle_prefix_sha256=None)は本件対象外(narrator chunkのStyleはNARRATOR_FULL_STORY_ADVでsha有り)。
### (e) retry/regeneration/resume
- 同一run再実行/`_merge_checkpoint`: OK chunkはreuse_key一致で再利用。失敗chunkのみ再生成(`FamilyZTtsClipFailedStop`のメッセージにchunk idが出る)。
- `--only-clips <親id>`: `only_clips`を親id→全chunk idに展開(`_run_tts_stage_impl`冒頭)。`<chunk id>`直接指定も可。
- text変更(Writer再生成後の`tts_b1b`再実行): planを再計算(textの純関数)、sha不一致chunkは再生成。dialogue/他clipは従来のreuse_key判定。
- `--regenerate-stage`系はstage単位の既存挙動(plan/kp等)。planを再実行してsegment_planが変わった場合はchunk planも再計算される(入力が変わるため)。
### (f) evidence
§C7+`audit/chunk_plan_b1b.json`(plan保存)+`gate_result`に`chunk_tts`要約。
### (g) Z速度仕様v2 Gate整合
`_CLIP_ID_RE`(:82)を`full_story_part([1-3])_c([0-9]+)(?:_k([0-9]+))?`に拡張(group 1,2の位置は不変)し、`required_clip_entries`の絞込み(:1534/:1570/:1658/:1660)がchunk IDを含むようにする。`verify_z_speed_profile`はAdv narrator chunkに**`slowdown_applied is True`ならSTOP**(:1608-1610、後処理なしを維持)。`verify_std_english_slowdown`はStd専用でchunk化しない(Stdにchunkが無いので対象IDは増えない)。`assert_tts_results_complete`は`required_clip_ids(plan)`=chunk idsを検査(親は検査対象外)。`part_to_clip_id`(:1848)は親id(timeline label)のまま。
### (h) 旧処理整理(150語ルールとの関係) — **推奨: 共存(150語ルールは不変、新ルールはその後段)**
- 事実: 150語ルール(`er013_family_c_production_01.py:251-326`、`hard_avoid_words=150`超のみ段落境界/語数中点で**clip自体を2分割**、clip間gap=narrator後0.5秒)はplan stageのクリップ化規則でStd/Adv共通・Family Cも使用。新ルールはplan後の**Adv narrator clip内部**のTTS分割(gap 0.2秒、clip id不変)。
- 適用順: 150語ルール(clip化)→新planner(>100語のAdv narrator clipを内部分割)。例: 161語は150語ルールで82+79の2 clip(各100語以下=新ruleは不発動)、201語以上は150語ルール後もなお>100語なら新ruleが追加で内部分割。
- 「一本化」案(Advでは150語ルールを無効化し新plannerに任せる)を採らない理由: (1) 150語ルールの変更は`plan`stageの出力(clip数・`comment_after_segment_id`・Std/Advの段落数整合)を変え、承認済みの`run_sf_prod_02`構成と非互換になる (2) Family C共有コードを触る (3) 150語超clipのclip間gapが0.5秒→0.2秒に変わる=ユーザーが承認していない聴感変更 (4) ユーザー決定の対象は「100語超のnarrator clip」(既存planが作ったclip)であり、150語ルールを廃止する承認はない。→ **重複ルールは残らない**(役割が異なる: clip境界 vs clip内TTS分割)。CURRENT_SPECに2規則の適用順と範囲を明記する(案(l))。一本化は将来の別案件(新仕様候補)として`OPEN`に記載のみ。
### (i) test計画
`tests_draft_01.py`+実装時追加(skip雛形に識別子を固定済み): plan展開(Adv長narratorのみ)、reuse_key(chunkのみ追加・非chunk不変)、`run_assembly`列(`…_k1,_silence_0.2,_k2,_silence_0.5,Comment…`)、`only_clips`展開、speed Gate対象化、pagesの親clip id、既存回帰(`er063`系・`er026`系・Family C builder回帰)。実runのoffline回帰: `run_sf_prod_02` Advのplanをdry-runし、非対象clip(Std全clip・Adv dialogue・短narrator)の`reuse_key`が**変更前とバイト一致**することを確認(旧音声の再利用維持)。
### (j) runtime evidence取得計画・費用
『告げ口心臓』`run_sf_prod_02`の**新run id**(例`run_sf_prod_03`、公開差替えなし)で `--stages tts_b1b,provision_shell,gate,assemble,pages,page_verify`(Z完成段は1起動、provision_shell欠落禁止=OPEN-480)。注意: `stage_gate/assemble`は`LEVELS=("b1b","a2")`を回すためStd(a2)の成果物が新runに必要→ **(推奨A) run_sf_prod_02のrun dirを新run idへ複製**(`copy_reusable_run_assets`のALLOW範囲+results/narration)し`tts_b1b`のみ再実行: Adv narrator 2 clip→4 chunk(+dialogue/KP等はreuse_key一致で再利用)=TTS 4 call+ASR 4 ≈ **1.5〜3円**で正式経路(plan展開→生成→親集約→Gate→chunk別gain組立→pages)をフル通過できる。**(B) 完全新規`tts_b1b`**: Adv全clipの再生成≈15〜20円(Fable見積)。Aで足りない点=「初回で全clipを生成する経路」だが、chunk対象は上記2 clipのみで他clipは既存経路なので、Aで要件6(正式経路で実際に発火)を満たす。Bは初回経路の全体evidenceが必要とFableが判断した場合のみ。起動前: `tools/stop_scope_check_01.py`、日次1,000円内確認、再起動は委任文の回数のみ。公開差替えはユーザー判断(OPEN-503最終試聴待ちと別)。
### (k) 量産原価・時間
Trial実測: B_r1 6 chunk 4.78円(うちNER等)。実run想定は2 clip→4 chunk(+2 call)で増分は主にASR/プロンプト固定費=**+0.12〜0.2円/Adv**(X実測1 call+0.043円からの外挿、X/Z差=Z TTS入力が長め)。処理時間+数十秒(直列2 call分)。作品Cap 70円・70円/記事セット目標への影響は0.3%未満。
### (l) CURRENT_SPEC記載案
> **Family Z Advanced narrator clipのTTS chunk分割**(APPROVED_FOR_PRODUCTION 2026-10-25、Trial B_r1): Advancedのnarrator story clipのうち語数>100のものを、`k=ceil(語数/100)`のchunkへ決定論的に分割して独立TTS(同一Voice/Style/model/Gate)で生成する。分割は段落境界を優先し、なければ文境界(引用符の途中は不可)、最小chunk25語。chunk間は固定無音0.2秒、chunkごとにscalar RMS正規化、既存のnarrator後0.5秒・Comment挿入は最後のchunkの後に1回。Dialogue・話者切替clip・100語以下のnarrator・Standard・KP・Commentは不変。chunkのsegment_idは`full_story_part{n}_c{k}_k{j}`。既存の150語超2分割(clip境界規則、`er013`)は不変で、その後段にこの規則を適用する。
### (m) SSOT更新案 → 下記

## SSOT更新案(実装・Fable受入後)
- **OPEN-506(X)/OPEN-510(Z)**: 本委任で「APPROVED_FOR_PRODUCTION・配線設計中・未配線(PRODUCTION_WIREDではない)」を最小追記済み。実装委任完了時に「WIRED_PENDING_FABLE」、Fable受入で「PRODUCTION_WIRED(Family別)」。
- **UDR #191**: 採用決定(2026-10-25、X=B0.2/Z=B_r1)を追記済み。
- **新規OPEN起票案(11-8分類)**: (1)「chunk方式のtarget_rms基準(親生連結RMS)によるepisode音量の+0.5dB級変動とpeak cap」→ **実害なし**(現行方式も部品RMSで変動、cap発動はevidenceに記録、Gate不要)。(2)「`_CLIP_ID_RE`拡張・role解決拡張の取りこぼし」→ **修正へ進む**(実装委任内で完了、testで固定)。(3)「Std本文(X a2/Z a2)へのchunk適用可否」→ **ユーザー判断要の将来候補**(現時点でTrial未検証・対象外。起票は実装完了時、今回は設計記載のみ)。(4)「150語ルールとの一本化」→ **実害なし**(共存で重複ルールなし。将来の新仕様候補として記録のみ)。
- **DECISION_LOG**: 本委任1件(配線設計・対象範囲・共存方針・C3集約方式)。
