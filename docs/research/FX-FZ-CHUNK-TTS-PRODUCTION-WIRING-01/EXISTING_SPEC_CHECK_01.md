# EXISTING_SPEC_CHECK_01 (FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01 Phase 0、API 0・Production file編集0)

原文: `docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md`(APPROVED_FOR_PRODUCTION: X=段落分割+0.2秒 / Z=B_r1)。調査日2026-10-25。**行番号は調査時点(並行agentが同一fileを編集中のため数行ずれうる)。実装時は関数名で再特定すること。**
前提Trial正本: `docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/{EXISTING_SPEC_CHECK_01,DESIGN_01,OPUS_REVIEW_01,TRIAL_RESULT_01,TRIAL_RESULT_02}.md`、`docs/research/FZ-NARRATION-CHUNK-TTS-TRIAL-01/{EXISTING_SPEC_CHECK_01,DESIGN_01,OPUS_REVIEW_01,TRIAL_RESULT_01,ISOLATION_EVIDENCE_01}.md`。本書はそれらの再掲を避け、**Production正式経路側**の確認(file:line)と、Trialとの差分に絞る。
分類(PM_GOVERNANCE 21節): **A+B**(承認済みの連結先例あり、過去不採用P6Bとは条件が異なりユーザーが2026-10-25に正式採用)。新規仕様の追加ではなく、承認済みTrial方式のProduction配線。

## 0. 重要な発見(設計を左右する順)

1. **gateは全segmentエントリを列挙する**(`er003_v1_n3_01_assemble.py:485-506` `for name, entry in data["segments"]`)。chunkを別entryにすると、既存のGate(`status==OK`・`sha256`一致・HR承認)がchunkごとに自動で効く。親(part/clip)の集約entryはGateにも通るため、**集約entryのstatusはchunk entryとHR承認から導出する必要がある**(WIRING_DESIGN §共通3)。共有Gate(Family A/B/C/X/Z共通)は変更しない。
2. **ロール解決はsegment_idの完全一致/`fullmatch`**(`er020_tts_retry_local_rewrite_01.py:125-150`)。X=`full_story_part{1,2,3}`のみ、Z=`full_story_part[1-3]_c[0-9]+`のみ。chunk wavのファイル名(=`derive_segment_key`でsegment_id、`er011_human_review_lock_01.py:139-152`)が`full_story_part1_k1`/`full_story_part1_c1_k1`になると**roleがNoneになり、Connected Speech層が外れる**(`connected_speech_enabled_for`、:163-168)。→ `resolve_narrative_role`に**追加のみ**で`(_c[0-9]+)?_k[0-9]+`を許可する(既存IDの結果は不変)。これを入れないとGateが静かに弱まる(最重要の落とし穴)。
3. **Z `target_rms`は`story_clips[0]`のwavから計算**(`er063_family_z_audio_01.py:1761`)、**X `target_rms`は`full_story_part1`のwavから計算**(`er019…:1767`)。chunk化しても**親wav(`narration/<parent>.wav`)を生chunkの0.2秒連結として書き出す**設計にすれば、この2行は無変更で動く(基準RMSは「単一callでのpart」に最も近い値)。
4. **Zのclip ID正規表現が複数箇所にある**(`er063…:82 _CLIP_ID_RE`、使用:580/1534/1570/1658/1660/1717/1851)。chunk IDを許可しないと`verify_z_speed_profile`(Adv Narrator後処理なしの検査)・`verify_std_english_slowdown`等がchunkを**スキップ**し検査が静かに抜ける。
5. **`prune_cached_to_plan`はplan内のClipSpecだけをcachedから残す**(`er063…:1161-1175`)。親集約entryはplanに無いため、TTS stage末尾で毎回再構築する必要がある(cachedから持ち越せない)。
6. **Xの本文reuseは`results["full_story_partN"]`単位**(`er019…:808-850 _generate_or_reuse`: status OK+wav実在+`canonical_text==expected_text`+`style_version`一致)。Master Audio Storeは**KP/shell専用**(`shared_narration`、`er019…:1043-1058`)で本文は通らない。Zの本文(narrator)もMaster Store非経由(`er063…`にmaster参照はshell用`existing_master`のみ、:1700)。→ 「Master Audio Store/reuse_keyへのchunk方式の組込み」は、Xは**part単位cache entry**、Zは**`build_reuse_key`**に対して行う(Master Store本体は無関係)。
7. **150語ルールはclip境界ルールで、Advでも残る**(`er013_family_c_production_01.py:251-326`、Std/Adv共通のplan stage)。新ルールはその**後段**でAdv narrator clip(>100語)の**内部**を分けるだけで衝突しない(WIRING_DESIGN §Z-h)。
8. **実run `run_sf_prod_02` Advの該当は2 clip**(`full_story_part2_c1`=120語→58/62、`full_story_part3_c1`=126語→65/61。他は82/79語[150語ルールで分割済み]・2語・12語等で対象外。Trial plannerをそのまま実run planへ適用して確認、`tests_draft_01.py::test_equals_adopted_trial_planner_on_real_run`)。

## 1. Family X 正式TTS経路図(Advanced b1b)と配線点

```
run_family_x(runner main, tts stage)
 └ generate_family_x_b1_segments(theme_out_dir, tts_backend, style_profile)      er019:1031   [decorators: secondary_run_scope / fx_iol / pnap family_scope X / er109 scope X]
    ├ _cached = _load_cached_tts_results(out_dir)                                 er019:661   (audit/tts_generation_results.json)
    ├ topic_intro/preview/comment_1-4 …                                           (不変)
    ├ for name in (full_story_part1..3, in_one_line):                             er019:1143-1160  ← ★配線点X1(本文3 partのみ)
    │    _generate_or_reuse(_cached, name, narration/<name>.wav,
    │        lambda: news_tail_fix.generate_news_narration_wide_margin(
    │            _pnap_supply(text, tts_safe_news_en(text)), wav, enable_connected_speech_equivalence_layer=cs(name),
    │            enable_repetition_qa=(name in _BODY_SEGMENT_NAMES), enable_pronunciation_resolver=True,
    │            style_prefix_override=_role_style("FULL_STORY"), tts_backend), expected_text=text)
    │    results[name]["canonical_text"]=text ; attach_segment_profile_record(...)
    ├ KP (Master Audio Store経由)                                                  (不変)
    └ save tts_generation_results.json / run_summary_tts.json                      er019:1189-1207
 news_tail_fix.generate_news_narration_wide_margin  [@review_lock.guarded_generate("en")]   news_tail_fix:62
    └ 内部: symbol Gate → 発音resolver → TTS(≤PRODUCTION_MAX_TTS_ATTEMPTS=3) → trim → ASR cascade(primary OpenAI→Azure) → Repetition QA → Connected Speech層 → Local Rewrite → HR Lock記録
       segment_idは out_path の basename (er011_human_review_lock_01.py:139 derive_segment_key)  ← ★role/HR/telemetryの単位
 stage_assemble_family_x_b1(theme_out_dir)                                       er019:1938
    ├ load_family_x_b1_sources → asm.verify_episode_audio_validation_gate(out_dir,"B1")   er019:1715 / assemble:474  (全segment entry)
    │   └ narration/<name>.wav を読む (full_story_part1..3 含む)                              er019:1731-1736   ← ★配線点X2(読込)
    ├ apply_family_x_b1_gain: target_rms=(rms(preview)+rms(full_story_part1))/2 ; 各segmentへscalar gain  er019:1764-1824  ← ★配線点X3(chunk別gain+0.2秒pad)
    ├ build_family_x_b1_timeline(parts)                                          er019:1827  ← ★配線点X4(chunk境界記録)
    └ assemble_with_timeline → apply_headroom_safety_valve → wav + run_summary_assemble.json
```
retry/fallback/regeneration/resume(既存):
- 生成内retry = `news_tail_fix`内(≤3 attempt、minimal_fallback、Local Rewrite、cool-down)。**chunkごとに呼ぶので、chunkごとに同じ上限が効く**(上限を緩めない/回避しない)。
- 失敗終了時 = `status!=OK`はHR Lock(`review_lock`)+`human_review_queue`に**chunk単位**で記録(segment_id=chunk id)。Gate(assemble)で`STOPPED/HUMAN_REVIEW_LOCKED`はブロック、人間承認(`approvals[chunk_id]`+canonical_text sha一致)でのみ通る(`assemble:116-139`)。
- resume = 同一out_dirで再実行 → `_generate_or_reuse`が前回results(`status OK`+wav実在+canonical_text一致+style_version一致)を再利用(`er019:808-850`)。`--only-segments`で当該segmentのみ(`er019:680-700 _VALID_ONLY_SEGMENT_RE`)。
- Local Rewrite後の再生成 = `news_tail_fix`内の`_local_rewrite_recovery_for_news_narration`(:346)。chunk text単位で動く(`m1_anchor_text`=元chunk text)。

## 2. Family Z 正式TTS経路図(Advanced b1b)と配線点

```
er026 stage_tts(ctx, level)                                                     er026:1843
 ├ load_level_inputs(ctx, level) → spec_plan = a63.build_level_plan(level, story_clips, …)   er026:1904 / er063:546  ← ★配線点Z1(plan展開: chunk ClipSpec)
 ├ run_tts_stage(out_dir, level, plan, generators, only_clips, article_text)    er063:1305-1396 (_run_tts_stage_impl)
 │    cached = load_results + _merge_checkpoint + migrate_legacy_dialogue_speed + prune_cached_to_plan(plan)
 │    for spec in plan:  generate_or_reuse_z(cached_entry, spec, out_path, gen)  er063:760   (reuse_key全一致のみ再利用)  ← ★配線点Z2(reuse_key)
 │         gen = real_generators()["narrator"] → news_tail_fix.generate_news_narration_wide_margin (b1b)  er063:835-841
 │         build_entry → _handle_local_rewrite → normalize_technical_stop_entry → _store → save_checkpoint
 │    → save tts_generation_results.json / runtime_evidence_<SUB_TASK_ID>.json / PWW listening list            ← ★配線点Z3(親集約entry+親wav生成)
 stage_gate → run_audio_gate(plan, shell_names): required_clip_ids(plan)=plan clip_id ; assert_tts_results_complete ;
      verify_z_speed_profile(_CLIP_ID_RE.fullmatch) ; check_clip_audio_quality ; asm.verify_episode_audio_validation_gate   er063:1647-1674  ← ★配線点Z4(chunk IDを検査対象へ)
 stage_assemble → run_assembly(run_dir, level, story_clips, …)                  er063:1743
      target_rms=(rms(preview)+rms(story_clips[0].wav))/2 ; build_z_sequence → runner_c.build_family_c_episode_sequence   ← ★配線点Z5(chunk別gain+0.2秒/0.5秒)
         narrator後=0.5秒 / voice≠narrator後=0.2秒 / Comment挿入前後1.0・0.8秒                       er013_family_c_production_runner_01.py:665-680
 stage_pages → build_pages → build_page_rows(timeline.json + results)           er063:1859 / 1985   (timeline labelがpart_to_clip_id(:1848)で親clip idへ)
```
- retry = `news_tail_fix`内(chunkごと)。clip単位の外側retry(`--only-clips`)= `er063:1353 only_clips`(Z E2Eの「当該clipのみ再実行、全体の自動再生成はしない」方針)。
- resume = `_merge_checkpoint`(process中断でもOK clip再利用、`er063:1347`)+ reuse_key。`RUN_LOCK`/`STOP`は`er026`側(chunkでも各生成の直前に`_check_stop_sentinel`:1361、`er026:1914 wrap_generators_with_budget` が各spec=各chunkの新規API呼出前にguard)。
- 失敗終了 = `FamilyZTtsClipFailedStop`(`er026:1950`)で当該clipのみ再実行を案内。

## 3. 既存の組立規則(Production、Trialと一致する点)

| 規則 | X | Z | 出典 |
|---|---|---|---|
| 音量 | `target_rms=(preview+part1)/2`、各独立TTS出力へscalar gain(peak≤0.95) | `target_rms=(preview+story_clips[0])/2`、clip別 | X `er019:1767-1778` / Z `er063:1761-1776`、`er003_b1_p9a_audio.py:459` |
| 結合 | `np.concatenate`のみ(crossfade・Dynamics無し) | 同 | `er003_v1_n3_01_assemble.assemble_with_timeline`、CURRENT_SPEC:2079 |
| gap | segment間0.4/0.5/0.65秒(本文part間は`build_family_x_b1_timeline`定義) | narrator後0.5/voice変更後0.2/Comment前1.0・後0.8 | `er019:1827-1876` / `er013_family_c_production_runner_01.py:665-680` |
| ヘッドルーム弁 | peak>0.98で全体一律 | 同 | `assemble:982-985`、CURRENT_SPEC:2100 |
| Comment位置 | (Xは本文part間に挿入しない) | `comment_after_segment_ids`=Part1最終clipの後=Comment2、Part2最終clipの後=Comment3 | `er063:1713-1719` |
| trim | 生成関数内部 | 同 | `er003_b1_p3u_audio`(0.35秒マージン) |

**chunk方式の規則(Trialで承認済み、Productionで再現する)**: chunk別scalar gain → chunk間に固定無音0.2秒(mono24kで`int(round(0.2*24000))`個のゼロ、Trial `er113_…trial_01.py:315-345 join_chunks`/`er114_…trial_02.py` と同一)→ 親全体をstereo48k化。既存gap(Z narrator後0.5秒・Comment前後)は**最後のchunkの後に1回**。ヘッドルーム弁は組立全体に1回(既存のまま)。

## 4. ASR Gate / 発音Ledger / HR / telemetry の適用単位(clip→chunk)

| 機構 | 現在の単位 | chunk方式での単位 | 変化 | 根拠 |
|---|---|---|---|---|
| ASR Gate(primary OpenAI→Azure secondary、統一judge) | 生成1 call(=part/clip) | chunk 1 call | 判定対象が短くなる(誤判定時の再生成が安い)。比較語数は同じ。Trial 23 chunk全OK、retry1件はB_r2のみ | `news_tail_fix:63-345`、X TRIAL_RESULT_01 §1 |
| Repetition QA | 本文part/clip | chunk(`enable_repetition_qa=True`をそのまま渡す) | 変化なし(各chunk内) | `er019:1151` |
| Connected Speech層 | role FULL_STORY | chunk(★role解決の拡張が必須) | 拡張しないと**外れる**(§0-2) | `er020:125-168` |
| 発音resolver / Ledger | call単位(style_prefixにhint) | chunk text単位 | hint(medium+)は該当語を含むchunkにだけ付く。Ledger書込みは従来どおりProduction store(Trial DEVではsink隔離したが**Productionでは正式sinkへ書く**) | `er025…resolve_and_augment_en_style_prefix` |
| HR Lock / human_review_queue / attempt_history | segment_id(`derive_segment_key`) | chunk id | 承認は**chunk単位**で`approvals[chunk_id]`+canonical_text sha | `er011_human_review_lock_01.py:139,179`、`assemble:116-139` |
| `audio_text_deviation`(Local Rewrite) | clip | chunk | 親集約に`deviation_chunks`として列挙 | `er063:1664` |
| sha256 stale検知 | 各entry | 各chunk entry + 親集約entry(親wavのsha) | 親wav=生chunk連結なので決定論 | `assemble:212-222` |
| ASR telemetry / 費用ログ | `cl.segment_context(name)` | `cl.segment_context(chunk_id)` | chunk別に費用・時間が出る | `er019:1149`、`er063:1387` |

## 5. Trial方式 vs Production の差分表

| 項目 | Trial(DEV) | Production | 備考 |
|---|---|---|---|
| 書込み先sink | `redirect_production_sinks`でattempt_history/HR queue/ASR telemetry/entity telemetry/Ledger(コピー)/Local Rewrite出力をDEV dirへ付替え(`er113…:660-712`) | **正式sinkへそのまま書く(付替え不要)** | 隔離・audit hook・保護store比較・mtime走査は**移植しない** |
| 出力dir/segment_id | `gen/<chunk_id>/b1b/narration/full_story_part<n>.wav`(chunkごとに別dirで`full_story_part<n>`を維持) | 同一`narration/`直下に`<parent>_k<j>.wav`(★role解決の拡張で対応) | Trialの回避策(dir分離)はProductionでは使えない(HR/telemetryが衝突) |
| target_rms | A側`gain_report`の固定値(X 0.09149 / Z 0.07332) | 通常式`(preview+親wav)/2`。親wav=生chunkの0.2秒連結 | 値は同一式の延長。差は§WIRING_DESIGN共通2 で定量見積 |
| 組立 | DEV assembler(本文のみ差替え) | 通常のassemble stage(`stage_assemble_family_x_b1`/`run_assembly`)の内部で展開 | |
| arm構成 | A/A_r2/B_r1/B_fine/B_alt | **B0.2(X)/B_r1(Z)のみ**(Fable注: B_alt/B_fine変更不要) | |
| 計測 | WPM・M4分解・境界dB・整列(ローカルWhisper) | **実行時の必須検査にしない**(承認済み品質水準を超える追加基準を作らない)。evidenceとして記録のみ | 境界音量差は採否の理由にしない(ユーザー決定) |
| 費用上限 | Trial Cap | 通常の記事案件Cap(X 150円/記事等、Z作品Cap)内 | |
| 版管理 | なし | `CHUNK_PLANNER_VERSION`をreuse_key/results/timelineへ | 旧clip音声の誤再利用防止 |

## 6. 適用範囲と既存仕様の照合(未承認の対象拡大なし)

| 対象 | 判定 | 根拠 |
|---|---|---|
| X Advanced(b1b)本文1・2・3 | **対象**(Trial条件と一致: Production同一関数`generate_news_narration_wide_margin`、model `gemini-3.8-flash-lite-tts`/Aoede、style_profile `fx_20261017` FULL_STORY、段落単位、chunk別RMS、0.2秒) | X EXISTING_SPEC_CHECK_01 §2 |
| X Standard(a2)本文 | **対象外**(生成後6%減速post-process[`generate_a2_segment_with_slowdown`]との相互作用が未Trial。`generate_family_x_a2_segments`は不変) | CURRENT_SPEC:2083,2133 |
| X in_one_line / topic_intro / comment / preview / KP | 対象外(Trial未検証、短文) | |
| Z Advanced(b1b) narrator clipのうち語数>100 | **対象**(B_r1: k=ceil(語数/100)、段落>文、最小25語、引用途中禁止、0.2秒) | Z TRIAL_RESULT_01 |
| Z Dialogue / 話者切替clip / 100語以下のnarrator | 不変 | ユーザー決定「会話文や短い地の文への無断拡張はしない」 |
| Z Standard(a2) narrator | **対象外**(6%減速[`generate_a2_segment_with_slowdown`]・`verify_std_english_slowdown`との相互作用が未Trial) | Z EXISTING_SPEC_CHECK_01 §4 |
| Z KP / Comment / Preview | 不変 | |
| Y(`er110`) | **対象外**(ユーザー決定はX/Zのみ) | |
| Family A/B/C | **不変**(`resolve_narrative_role`追加は新しいID形にのみ反応) | |

## 7. 速度仕様v2(Z)との整合
`Z_SPEED_PROFILE_VERSION=z_speed_v2`(`er063:49-64`): (Adv,Narrator)=後処理なし。chunkはAdv narratorなので**後処理なしのまま**。`verify_z_speed_profile`の「Adv Narratorに速度後処理が掛かっていたらSTOP」(:1608-1610)をchunk IDにも効かせる(§0-4、WIRING_DESIGN §Z-g)。極短clip速度Gate(`adv_dialogue_ratio_range`)はdialogue専用で非干渉。X: Adv本文に速度Gate無し(X EXISTING_SPEC_CHECK_01 §1 #10)。

## 8. 過去不採用(P6B)との関係
`CURRENT_SPEC.md:2052,2065,2074`: 日本語P6B(2-Macrochunk)はユーザー試聴で不合格・単一call凍結。本件は**英語・Flash-Lite・段落/文単位・chunk別RMS+0.2秒・Voice固定**で条件が異なり、**ユーザーが試聴のうえ2026-10-25に正式採用**(USER原文§1)。無断再導入ではない。CURRENT_SPECの「単一TTS call凍結」記述にはX/Z Advanced本文への**例外**を明記する(WIRING_DESIGN §l)。
