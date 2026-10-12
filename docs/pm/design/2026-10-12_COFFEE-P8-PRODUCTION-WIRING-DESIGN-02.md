# COFFEE-P8-PRODUCTION-WIRING-DESIGN-02(OPEN-300、Opus条件Aレビュー反映版・実装済み)

管理ID: FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02。日付2026-10-12。状態: **実装済み(コード+テスト)・runtime evidence未実行・Production未配線(`PRODUCTION_WIRED`ではない)**。課金0。

v01(`2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-01.md`)の1節(現状)・2節(3案比較)・案2推奨は維持し、Opus条件Aレビュー(M1〜M6/S1〜S5)で訂正・追加された点を本書で上書きする。v01と本書が食い違う場合は本書が優先。

前提(ユーザー決定2026-10-12): Coffee Full StoryのStyleをP8(`er057_output/aoede_style_trial_03/prompts/prompts_aoede_style_03.md`、402文字、sha256 `3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595`、`assert_no_wpm_specification`通過)へ置換、`APPROVED_FOR_PRODUCTION`(Coffee限定)。OPEN-298(全記事共通Style展開)・OPEN-299(In One Line 2文方針)は範囲外。共通定数・他Family・他記事・共有module(er003/er006/er011/er033定数/Master Store)は変更しない。

## 1. 採用した実装(案2、Phase 1=Full Storyのみ)
- 新module `er019_family_x_style_profile_01.py`: profile定義(`default`/`coffee_p8`)、P8定数(逐語、import時にsha256/長さ/WPM無し検証)、単一解決関数 `resolve_role_style(profile, role, level, base_getter)`、固定記録 read/write/verify、M2/M5 STOP判定、M3 Gate、M4 evidence判定、S2 Ledger hit計算。
- runner変更は最小: CLI `--style-profile`(既定=未指定、choices=default/coffee_p8)、`generate_family_x_b1/a2_segments(style_profile="default")`、各 `_role_style`/`_role_style_slower` の中身のみを `resolve_role_style` 経由へ、P8対象segmentにだけ `style_profile`(`style_base_sha256`=hint追記前)を記録、`stage_assemble_family_x_b1/a2` 内の `_style_profile_gate_blocked_summary`(M3)、`main` のM5/M2判定、`run_plan_stage` のS2記録。
- 固定記録: `<out_dir>/audit/style_profile.json`(profile_id・`overridden_roles=["FULL_STORY"]`・roleごとsha256・設計ID)。**defaultでは新key/fileを一切書かない**(S3)。

## 2. Opusレビュー反映(M1〜M6)
### M1 Local Rewrite回復の再TTSはP8が落ちる(v01 3節の経路表を訂正)
- Adv: `er003_v1_sing01_news_tail_fix.py:360-366` の `_retts_fn` は `style_prefix_override` を渡さない。Std: `er003_v1_crosslevel_audio_02_common.py:392-397` はminimal fallback系。**共有moduleは改変しない**。
- 訂正後の経路表:

| 経路 | P8適用 | 備考 |
|---|---|---|
| 初回生成 | 適用(Adv=wide_margin、Std=slowdown、Stdは逐語) | resolver経由 |
| 標準retry(attempt) | 適用 | 同一 `style_prefix_override` が内側へ渡る |
| A2外側減速ループ(最大3、総生成3回上限) | 適用 | 回数上限不変 |
| segment regeneration(同一out_dir内) | 適用(ただしM2: coffee_p8は新out_dir前提) | |
| **Local Rewrite回復の再TTS** | **適用されない**(Adv/Std両方) | fallback同様「非P8」。M3 Gateで捕捉(`local_rewrite_recovery`あり=BLOCK) |
| **minimal_fallback** | **適用されない** | `instruction_type=minimal_fallback`/Std `fallback_used=True`。M3 Gateで捕捉 |
| resume(同一out_dir) | 固定記録から同profile | CLI食い違い=STOP |
| 発音hint追記 | 既存挙動(P8末尾へ追記) | M4で判定 |

- **Family X全体の既存の穴**(Adv Local Rewrite回復でrole styleが落ちる)は、P8導入と無関係に存在する。新規OPENとして起票(OPEN_ITEMS.md)。本設計では是正しない(共有module改変が必要で他記事影響が出るため)。

### M2 Review Lock/人間承認はStyleを区別しない → coffee_p8は新しいout_dirでのみ実行可
- Review Lock/人間承認の照合キーはtext shaのみ(`er011:179-190, 318-339`、`assemble:127-132`)で、Style/profileを区別しない。旧Style音声の承認が黙ってP8に引き継がれるのを防ぐ。
- `coffee_p8` 指定時、`<out_dir>`・`<out_dir>/a2`・`<out_dir>/b1b` の `audit/` に `tts_generation_results.json` / `review_lock_state.json` / `human_approved_segments.json` のいずれかが存在すれば、`style_profile.json` を作らずSTOP。
- 記録欠落の扱い: CLI default(または未指定)+記録なし -> default / CLI coffee_p8+既存run記録なし(新規out_dir) -> 記録作成 / CLI coffee_p8+既存run記録あり(固定記録なし) -> STOP。
- v3と同一原稿を使う場合は、scaffold成果物(parts/support/KP)だけを**出所記録付きで明示コピー**する(scaffold再実行禁止、Review Lock/承認/attempt系は一切コピーしない)。runtime evidence run時の手順であり本委任では実行しない。

### M3 Assembly前Gate(Family X runnerの `stage_assemble_family_x_*` 内のみ、共有assembleは不変)
- P8対象role各segment(full_story_part1〜3)ごとに: `style_profile.style_base_sha256 == P8` / Advは `style_prefix` がP8で始まる / `instruction_type != minimal_fallback` / `local_rewrite_recovery` なし / Stdは `fallback_used` が False / M4のFinal Style判定。
- 満たさない場合、`asm.record_human_approval` による人間承認(canonical text sha一致)が無ければ `BLOCKED_STYLE_PROFILE_GATE`(`run_summary_assemble.json`+`audit/style_profile_gate.json`)。defaultでは何もしない。

### M4 runtime evidence判定(hint追記を考慮)
- runnerがsegmentごとに `style_base_sha256`(hint追記前にrunnerが渡したStyleのsha256)を記録。判定: base sha==P8 かつ hintなし(`en_pronunciation_resolver_info.hints_applied` 偽)なら最終style sha==P8 / hintありなら最終styleの先頭200字==P8[:200]かつ長さ>=402、加えて `cache_hits` を列挙。最終styleは、Adv=`style_prefix`(文字列)、Std=`attempts_log`末尾の `style_prefix`(sha256+head200+len)から取得。

### M5 backend STOP
- `profile != default` かつ `tts_backend != speech_metadata_flash_lite` ならSTOP(`--allow-legacy-backend` を付けても同じ)。main(全stage、plan/dry-runを含む)と `generate_family_x_*_segments` の両方で課金前に判定。STOP時は記録・ファイルを作らない。

### M6 PRODUCTION_WIRED表記の限定
- 配線完了が将来判定される場合の表記は**「Coffee Full StoryのStyle解決のみ」**に限定。`style_profile.json` に `overridden_roles=["FULL_STORY"]`。他Role(A5/B5/E1/R2/K2/M2等)・他記事は未配線。
- runtime evidence episodeは配線証跡であり、01A成果物(Coffee v4)を**置き換えない**(SSOT明記)。

## 3. Sonnet申し送り反映(S1〜S6)
- **S1** Std「P8逐語+6%減速、減速指示非連結」はCoffee限定例外(決定ID `COFFEE-P8-STD-VERBATIM-EXCEPTION-01`)。`er019_family_x_style_profile_01.py` のヘッダに注記(`er003_v1_n3_01_tts_generate.py` の説明文「A2_ENGLISH_STYLE_PREFIX_SLOWERを渡しinstruction+6%を正確に再現」および現行 `_role_style_slower` 連結との差異)。共有moduleは不変。テストで固定(coffee_p8のStd Full Storyはinstruction非連結、defaultのStd/coffee_p8のStd IN_ONE_LINEは従来どおり連結)。
- **S2** plan段階でCoffee part1〜3のLedger hitを計算・記録(web lookup無効、課金0、`run_plan_stage` の `style_profile_plan`)。結果: 現行Ledger(37 entries)では**Coffee a2/b1bとも part1〜3 のhit 0件**(hint追記なし)。証跡は `er019_output/coffee_prices/run_p8_wiring_01/plan_run_result.json`。runtime時にreactive lookupでLedgerが増えた場合はM4でhintあり判定になる。
- **S3** profile記録はP8対象roleのsegmentにだけ付与。defaultでは新key/fileを書かない。mock TTSでb1/a2全segmentの `style_prefix_override` を捕捉し、baseline commit(`776c6b92`、runner変更前)のrunnerと比較するtestで同一性を確認。
- **S4** rollback手順: `--style-profile` 未指定でdefault(現行動作)。新module削除+runner差分revertで完全復帰。**coffee_p8のout_dirは再利用禁止**(defaultとの混在・旧承認の引き継ぎを防ぐ。やり直しは新しいout_dirで)。
- **S5** Phase 2申し送り(K2/M2/A5/B5/E1/R2): (a) KP系(`_generate_or_reuse_kp`)にprofile照合を追加(現行のreuse判定は `style_version` のみでprofileを見ない)、(b) Master Store(shell固定phrase・KP英語)を使う役は `style_instruction_id` を `coffee_*` として既存defaultと分離、(c) E1/R2はrunnerのrole style定数(PREVIEW/COMMENT/JA)をprofile経由で上書き。OPEN_ITEMS.mdに記録。
- **S6** runtime evidence run(新out_dir、両level全segment+KP)の費用見積は `er057_output/coffee_final_audio_assembly_01/RUNTIME_EVIDENCE_COST_ESTIMATE_01.md`。実行はユーザー判断待ち。

## 4. Wiring Checklist(全て満たすまで `PRODUCTION_WIRED` としない)
| # | 項目 | 状態 |
|---|---|---|
| 1 | Opus条件Aレビュー反映(M1〜M6/S1〜S5) | 済(本書) |
| 2 | 実装(案2) | 済(新module+runner最小差分+test、共有module/共通定数diff=0) |
| 3 | 初回経路適用(mock) | 済(test: b1b/a2 Full Story 3 segmentがP8) |
| 4 | retry/regen適用 | mock級まで(標準retryは同一prefix)。**実segmentでのsha一致=runtime evidence未実行** |
| 5 | fallback/Local Rewrite扱い | 済(M1/M3: 非P8を検知しBLOCK、独自無効化なし) |
| 6 | resume適用 | 済(固定記録読込、CLI不一致STOP、test) |
| 7 | Std逐語+6%減速 | 済(test、S1)。実音声は未生成 |
| 8 | 他記事非影響 | 済(default同一性HEAD比較test、regression新規failure 0) |
| 9 | Gate/ASR/duration(P8で既存閾値) | **未実行**(runtime evidence) |
| 10 | runtime evidence(実TTS、新out_dir、両level) | **未実行**(ユーザー判断待ち) |
| 11 | SSOT/Git | 済(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC注記、commit/push) |
| 12 | 人間承認(Production採用) | 人間のみ。配線完了判定後 |

## 5. 範囲外・禁止の確認
OPEN-298・OPEN-299は含めない。共通定数・他Family・共有module・Master Storeは変更しない。`PRODUCTION_WIRED` とは表記しない(runtime evidence未実行)。
