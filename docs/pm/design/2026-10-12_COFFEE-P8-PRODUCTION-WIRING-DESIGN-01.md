# COFFEE-P8-PRODUCTION-WIRING-DESIGN-01(OPEN-300、Opus条件Aレビュー用)

管理ID: FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_01B。日付2026-10-12。状態: 設計のみ(実装・API呼出・課金0)。Production未配線(`PRODUCTION_WIRED`ではない)。

前提(ユーザー決定2026-10-12): Coffee Full StoryのStyleをP8(`er057_output/aoede_style_trial_03/prompts/prompts_aoede_style_03.md`、402文字、sha256 `3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595`、本設計時に原典から再計算して一致を確認、`assert_no_wpm_specification`通過を確認)へ置換、`APPROVED_FOR_PRODUCTION`(Coffee限定)。共通定数・他Family・他記事は変更しない。OPEN-298(全記事共通Style展開)とOPEN-299(In One Line 2文方針)は未解決のまま**本設計の範囲外**。

## 1. 現状(コード確認結果)

### 1-1. Style解決の現行経路(`er019_family_x_audio_production_runner_01.py`)
- Style定数は `er033_tts_flash_lite_family_x_styles_01.py` L41 `FAMILY_X_ROLE_STYLE_EN`(TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/IN_ONE_LINE)、L94 `FAMILY_X_ROLE_STYLE_JA`(Standard日本語)、L114 `KEY_PHRASE_EXPLANATION_EN`、L61 `FAMILY_X_ROLE_STYLE_EN_FALLBACK`。**現行FULL_STORYは「calm, steady news narration…」でありPD8/P8ではない**(Coffee v3のPD8はTrial隔離経路でのみ適用)。
- runnerは `generate_family_x_b1_segments`(L560)と `generate_family_x_a2_segments`(L827)内に**各々ローカル関数 `_role_style(role)`**(L583/L872)を持ち、`tts_backend == "speech_metadata_flash_lite"` のときだけ定数を返す。記事別の分岐は無い。
- Advanced Full Story: L655-673 `news_tail_fix.generate_news_narration_wide_margin(..., style_prefix_override=_role_style("FULL_STORY"|"IN_ONE_LINE"))`(`er003_v1_sing01_news_tail_fix.py` L96/L128で `standard_style_prefix = style_prefix_override or ENGLISH_STYLE_PREFIX`、発音hintがある場合はprefix末尾へ追記)。
- Standard Full Story: L970-990 `n3_tts.generate_a2_segment_with_slowdown(..., style_prefix_override=_role_style_slower(...))`。`_role_style_slower`(L877)は **基本Style + `A2_SLOWER_PACE_INSTRUCTION`(「slightly slower, relaxed pace…」)を連結**し、その後に6%time-stretch(`apply_a2_slowdown_postprocess`)。**Coffee v3 StdのPD8は逐語(減速指示を連結せず)+生成後6%減速**であり、現行Standard経路とは構造が異なる(論点2)。
- retry(標準経路attempt)・Local Rewrite・A2外側ループ(最大3回、`max_slowdown_attempts`)はいずれも同一の `style_prefix_override` を内側へ渡す。**minimal_fallback**経路は `repro01.generate_english_component_minimal_instruction` 内部の別文字列を使い、style_prefix_overrideは効かない(news_tail_fix L123-128/L282コメント)。

### 1-2. Reuse/resume/Master Store
- Full Story等の可変segment: 再利用は `_generate_or_reuse`(L406)。判定は (a) `out_dir/audit/tts_generation_results.json` のトップレベル `style_version` == グローバル定数 `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`(L385)、(b) status=OK、(c) wav実在、(d) canonical_text一致。**Style内容そのもの・記事別profileはキーに入らない**。cacheは `out_dir`(slug/run単位)に閉じる。
- Master Audio Store(`er006_master_audio_store_01.py`、`MasterAudioKey`にstyle_instruction_id/version含む)は **shell固定phrase・Key Phrase英語(shared_narration)のみ**が対象で、Full Storyは対象外。よってFull Story P8化はMaster Storeキーに影響しない。ただしA5/B5(shell)・K2等をCoffeeへ入れる場合は `style_instruction_id` を分けないと既存の共通masterを再利用/汚染する(4節)。
- 人間確認: `er011_human_review_lock_01.py` が `attempt_history.jsonl`(append-only)/`human_review_queue` を管理。Gate: `er003_v1_n3_01_assemble.py`(Audio Validation Gate)はStyle文字列に依存しない(音声指標のみ)。P8は発話が明るく速度が変わり得るため、既存閾値で判定する(閾値は不変)。

### 1-3. Style差異表(Coffee v3/v4適用 vs 現行Production、`PRODUCTION_DIFF_V3_01.md`/`STYLE_APPLICATION_EVIDENCE_V3_01.md`参照)
| Role | Coffee適用Style(承認) | 現行Production(共通) | 差異/配線要否 |
|---|---|---|---|
| Full Story Adv/Std | **P8**(旧PD8)。Stdは逐語P8+生成後6%減速 | FULL_STORY「calm, steady news narration…」(Stdは+減速指示+6%減速) | **本設計の主対象**。Std連結仕様に差異 |
| In One Line | 既存承認Style(新2文原稿はOPEN-299) | IN_ONE_LINE既存 | Style差異なし(原稿はOPEN-299) |
| Intro welcome/preview_intro | A5 / B5 | shell固定(Master Store) | 差異あり(shell=Master Store、styleキー分離要) |
| Adv Preview | E1 | PREVIEW「calm, conversational」 | 差異あり |
| Std日本語Preview/Comment | R2(P2表記ゆれ、OPEN-303で原典sha確認) | `FAMILY_X_ROLE_STYLE_JA`(J3) | 差異あり |
| KP英語 | K2 | Master Store経由の既存KP style | 差異あり(Master Storeキー要) |
| KP日本語意味 | M2 | J3系/既存 | 差異あり |
| 発音hint | Trial省略(PD8逐語) | Style末尾にhint追記 | 差異あり(論点4) |

注: A5/B5/E1/R2/K2/M2はユーザー決定済みだが、本委任のP8決定が直接要求するのはFull Story。**Phase 1=Full Storyのみ配線、他Roleは同じprofile機構へ後続Phaseで追加**とする案を推奨(論点1)。Phase 1だけではCoffee全Style配線完了とは言えない点を明記する。

## 2. 設計案(最小構成、3案比較)

共通部品(全案共通): 新規小モジュール `er019_family_x_style_profile_01.py`(副作用なし、定数+純関数)。
- `STYLE_PROFILES = {"default": {}, "coffee_p8": {"FULL_STORY": {"text": <P8逐語>, "sha256": "3eadf4...", "std_append_slower_instruction": False}}}`
- `resolve_role_style(profile_id, level, role, base_getter)` は該当override無しなら `base_getter(role)`(現行`fl_styles`の値)をそのまま返す。`default`/未指定は**現行とバイト同一**。
- resolverはP8テキストのsha256を実行時に検証(不一致でRuntimeError=STOP)。

### 案1: 記事slug->profile表(自動解決)
runnerが `--slug` から表(`{"<coffee slug>": "coffee_p8"}`)を引く。CLI追加なし。
- 長所: 実行者の指定漏れが無い。短所: slug命名に依存(再生成・別run名・rename・別slug再取込で黙って`default`に落ち、**P8適用漏れがsilent**)。記事ID=slugとは限らず対応表のメンテが必要。

### 案2(推奨): 明示CLI `--style-profile coffee_p8` + out_dirへの固定記録
- 変更: `build_arg_parser`へ `--style-profile`(既定`default`、choices=STYLE_PROFILES)を追加。`generate_family_x_b1_segments`/`generate_family_x_a2_segments`へ引数 `style_profile="default"` を追加し、両関数ローカルの`_role_style`/`_role_style_slower`の**中身だけ**を `resolve_role_style` 経由へ差し替え(呼出し箇所L662/L981は無変更)。
- **固定記録**: 初回tts stageで `out_dir/audit/style_profile.json`(profile_id・各roleのtext sha256・設計版)を書き、以後の全stage(retry/regen/resume/Local Rewrite/再実行)は**CLI値ではなくこのファイルを読む**。CLI値と記録が食い違えばSTOP(`USER_DECISION_REQUIRED`)。「resumeで黙ってdefaultに戻る」「途中でprofileが混在する」を防ぐ。
- cache整合: `tts_generation_results.json` に `style_profile`(id+sha)を追加。`_generate_or_reuse`は `cached.get("style_profile")` と現行profile(欠落は`default`扱い)を比較し、**不一致なら再利用せず再生成**(P8と旧default/PD8の混在reuseを防ぐ)。`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`(グローバル)は**bumpしない**(bumpすると他記事の既存cacheまで無効化するため。default記事の再利用挙動は不変)。
- evidence: 各segment結果に `style_profile`、実際に使ったstyle_prefixのsha、`instruction_type`(standard/minimal_fallback)を記録(news_tail_fixは既に`style_prefix`/`instruction_type`を記録)。

### 案3: 記事ソースsidecar(`<source_dir>/style_profile.json`)
article.md隣のsidecarをrunnerが読む。長所: 記事単位の宣言が記事側に残る。短所: 記事ソースがTrial/queueから複製される経路が複数あり(`_queue_shas`等)、sidecarの欠落・コピー漏れが案1同様silent。新たな入力契約が増え最小構成ではない。不採用候補。

比較要約:
| 観点 | 案1 slug表 | 案2 CLI+固定記録 | 案3 sidecar |
|---|---|---|---|
| 変更ファイル | runner+新module | runner+新module(+test) | runner+新module+入力契約 |
| 他記事非影響 | slug一致のみ | 既定default、profile指定時のみ | sidecar有のみ |
| silent適用漏れ | あり | 固定記録+不一致STOPで防止 | あり |
| resume/regen一貫 | slug依存 | 固定記録で保証 | sidecar依存 |
| 最小性 | 小 | 小〜中 | 中 |

### 他記事・他Familyへの非影響の保証(案2)
1. `default`は現行とバイト同一(resolverは`base_getter`素通し)。テスト: 全role x A2/B1bで`default`のstyle_prefixが現行定数と一致。
2. `fl_styles.FAMILY_X_ROLE_STYLE_EN`等の共通定数は**一切編集しない**(git diffで対象外を確認)。
3. 新moduleはer019 runnerからのみimport(Dangling Reference Check)。Family Y/Z/A/B/C、共有module(er003/er006/er011/er012/er013/er020)は無改変。
4. グローバル`style_version`非bump、Master Storeキー非変更(Phase 1)。

## 3. 経路別の適用(案2)
| 経路 | P8適用 | 備考 |
|---|---|---|
| 初回生成 | resolver経由で`style_prefix_override`=P8 | Adv=wide_margin、Std=slowdown(Std逐語、減速指示連結なし=profileフラグ) |
| 標準retry(attempt) | 同一`style_prefix_override`が内側へ渡る | 変更なし |
| A2外側減速ループ(最大3) | 同上 | 回数上限不変 |
| Local Rewrite / segment regeneration | テキストのみ変更、generate_fn同一 | resolver経由のため自動でP8 |
| **minimal_fallback** | **P8は適用されない**(既存安全装置が内部の別文字列を使う設計) | 独自判断で無効化・変更しない。fallback発動時は`instruction_type=minimal_fallback`をevidenceに記録しreview対象(論点3) |
| resume(同一out_dir再実行) | 固定記録から同profile、cache不一致なら再生成 | CLI不一致はSTOP |
| 発音hint追記 | 既存挙動(hintありならprefix末尾へ追記) | Trialでは省略していた。論点4 |

## 4. Master Store/既存Coffee音声の再利用可否
- Full Story: Master Store対象外。Coffee v3/v4のPD8 wavは**P8とStyleが異なるため再利用しない**(cacheはcanonical_text+style_profileで不一致=再生成)。
- 他Role(Intro/Preview/KP/日本語等)のv3 wav再利用: Production out_dirへ取り込む場合は、cache entryに`style_profile`・由来(Trial wav sha・provenance)を明記した**明示import**が必要(黙った流用は不可)。取り込むかProductionで再生成するか(追加課金)は別判断。Master Store対象(shell/KP英語)を後続Phaseで入れる場合は `style_instruction_id` を`coffee_*`として既存defaultと分離。
- Coffee以外の記事のcache/Master Storeは非影響(default)。

## 5. Gate/evidence/test/Regression/rollback
- **test(新規)**: resolverのdefault同一性、`coffee_p8`のFULL_STORY=P8逐語sha一致・他role素通し、`assert_no_wpm_specification`通過、Std逐語(減速指示非連結)+6%減速呼出し、固定記録(初回書込・CLI不一致STOP・欠落した既存run=default扱い)、cache不一致で再生成、`_role_style`系の全参照が単一resolver経由であること(grep型test)。mock TTSで経路別style_prefix検証(標準/retry/regen/fallback)。API課金0。
- **Regression**: 既存er019関連test(style・style_version・tts_backend gate関連)を全件実行し結果同一。`--dry-run`でprofile未指定のplan・prefixが現行とバイト同一。
- **runtime evidence(実装・承認後の別委任、予算上限は別途確認)**: Coffee実記事Part1〜3のAdv/Std、`style_profile.json`、各segment結果のstyle_prefix sha・instruction_type・attempt履歴、Audio Validation Gate、attempt_history、Master Store非書込(Phase 1)。
- **rollback**: `--style-profile`を指定しなければ`default`で現行動作。新module削除+runner差分revert(単一commit)で完全復帰。生成済みwavはP8由来と記録されるため区別可能。
- **Gate**: 既存Gate・retry上限・Human Review Lockは無改変。fallback発動・ASR UNCERTAIN増加(OPEN-272型)はHuman Reviewへ(独自に回避しない)。

## 6. Wiring Checklist(全て満たすまで`PRODUCTION_WIRED`としない)
| # | 項目 | 判定基準 |
|---|---|---|
| 1 | Opus条件Aレビュー反映 | 指摘に対する設計反映済み |
| 2 | 実装(案2) | 変更がrunner+新module+testのみ、共通定数diff=0 |
| 3 | 初回経路適用 | evidenceのstyle_prefix sha==P8、Adv/Std全Part |
| 4 | retry/regen/Local Rewrite適用 | mock+実segmentでstyle_prefix sha一致 |
| 5 | fallback扱い | instruction_type記録・review対象、独自無効化なし |
| 6 | resume適用 | 固定記録読込、CLI不一致STOP、cache不一致で再生成 |
| 7 | Std逐語+6%減速 | 減速指示非連結、減速後検証は既存どおり |
| 8 | 他記事非影響 | default同一性test、既存全test PASS、dry-runバイト同一 |
| 9 | Gate/ASR/duration | 既存閾値でPASS(P8でGate落ちなら停止して報告) |
| 10 | SSOT/Git | DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC更新、commit/push |
| 11 | 人間承認 | 配線完了判定の報告後、Production採用承認は人間のみ |

## 7. 推奨と理由
**案2(明示CLI+out_dir固定記録、Phase 1=Full Storyのみ)** を推奨。理由: (1)default素通しで他記事・他Familyへの非影響を機械的にtestできる、(2)silent適用漏れを固定記録+不一致STOPで防げる(案1/3は漏れがsilent)、(3)retry/regen/resumeが単一resolver経由になり、b1/a2二重のローカルclosureの拡張点が一箇所にまとまる、(4)グローバル`style_version`を触らないためcache影響が局所化、(5)rollbackが容易(flag不指定+revert)。

## 8. Opusへの論点
1. **Scope**: Phase 1をFull Storyのみとし、A5/B5(shell=Master Store)・E1・R2・K2・M2を同じprofile機構で後続とする分割は妥当か。全Coffee Roleを一括配線すべきか(Master Storeキー分離を含む設計が必要)。
2. **Std構造差**: 現行`_role_style_slower`は基本Style+減速指示連結だが、Coffee v3のStdはP8逐語+生成後6%減速。profileフラグ`std_append_slower_instruction=False`で再現する方針は、既存Gate(A2 Core Logic Preservation等)・OPEN-270(外側ループ未実装)と整合するか。
3. **fallback**: minimal_fallbackが内部の別文字列を使う既存安全装置を変更せず、P8非適用でevidence記録+review対象とする扱いは「fallbackへの適用」要求に対し妥当か(P8をfallbackにも使うには共有module `er003_v1_repro01_main_generate`の改変が必要で、他記事影響が出る)。
4. **発音hint**: Trial(PD8/P8)はhint省略だが、Productionは発音hintをprefix末尾へ追記する。hint付与で音声が変わるリスクと、Pronunciation Ledger(OPEN-272型偽NG対策含む)を省略できない点の整理。
5. **固定記録の責務**: `style_profile.json`のSTOP挙動(CLI不一致・欠落した既存run)と、Coffee v3/v4 Trial音声を明示importで取り込む場合のprovenance要件。cache比較をグローバル`style_version`ではなく別フィールド(`style_profile`)にした設計は、既存の`require_style_version`系(KP guard)と矛盾しないか。

## 9. 範囲外・禁止の確認
OPEN-298(共通Style展開)・OPEN-299(In One Line)は本設計に含めない。共通定数・他Family変更を前提にしない。本書は設計のみでコード・API呼出・課金はなし。`PRODUCTION_WIRED`とは表記しない。
