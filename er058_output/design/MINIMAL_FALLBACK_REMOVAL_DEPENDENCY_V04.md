# MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_V04: minimal fallback撤去の依存マップと撤去手順案(委任_04D作成、委任_05Bで更新、2026-10-12。v01は`MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_01.md`として残す)

**v04での更新(委任_05B、0円追加確認)**: (1)LR再TTS関数の中身確認(2-1、8章の未確認を解消) (2)見出し経路がminimal系Promptを通常Styleとして使うこと・`force_secondary`の適用範囲(2-6、10章) (3)Master Storeにminimal由来の印が無いこと(11章) (4)日本語minimalの指示文読み上げ(leakage)のFlash-Lite期再発率(2-8) (5)400エラーの再試行実績(7章)。再現: `er058_05b_zero_yen_checks_01.py`。

状態: **設計案・read-only調査**(Production code変更なし、API 0円)。方法: main作業ツリー(root直下`*.py`)をgrep+該当箇所を実読。`er053_dangling_reference_check_01.py`は実装が無いため未実行(実装後に検査する前提、末尾9章)。行番号は2026-10-12時点のmain。
ユーザー方針: minimal fallbackは日英の対象Production経路から**撤去する設計方針**。**Key Phraseの初回から使う専用短文Prompt(`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`)は別物で削除しない**。

---

## 1. 撤去対象の定義(混同防止)

| 名称 | 何か | 撤去? |
|---|---|---|
| A2英語minimal fallback | `er003_v1_crosslevel_audio_02_common.py::_run_a2_minimal_fallback_attempt`(L292)が`repro01.generate_english_component_minimal_instruction`(repro01 L501)を呼ぶ1 attempt。標準2回後の最終attempt(L181)+**LR再TTS(L383)**で使用。`force_secondary=True`(L341) | **撤去対象** |
| 日本語minimal fallback | `er003_v1_n3_01_tts_generate.py::_generate_a2_japanese_minimal_instruction`(L400、呼出L532)、`er003_v1_sing01_voice01_generate.py::generate_charon_japanese_minimal_instruction`(L401、呼出L557) | **撤去対象** |
| B1/Charon英語の技術的fallback | `voice01.generate_charon_english`内(L170〜200、400系で`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`/`MINIMAL_INSTRUCTION_PREFIX`へ切替)、`er003_v1_sing01_news_tail_fix.py` L175 | **決定論的技術失敗専用**。撤去するか隔離経路として残すかは**ユーザー判断**(U-4(d))。本設計は一旦「撤去しない・対象外」として扱い、論点として分離(7章) |
| Point見出し | `er003_v1_sing01_point_headings_aoede.py` L97〜99 | 見出し(Heading readout)の生成Style。minimal「fallback」ではなく**通常Style選択**の一分岐。撤去対象外(要確認) |
| **Key Phrase専用Minimal Prompt** | `repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(L685、CORE+FUNCTION_WORD_REDUCTION)、English Lock(`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`) | **削除しない**(KPの初回Prompt。`generate_key_phrase_component_verified`は`generate_english_component_minimal_instruction`を呼ばず`generate_narration_snippet_verified_strict(style_prefix_override=...)`を直接呼ぶ=撤去対象と**独立**。コードで確認) |
| `repro01.MINIMAL_INSTRUCTION_PREFIX`(汎用Minimal文言) | repro01 L495。使用: `generate_english_component_minimal_instruction`、legacy scaffold(`b1_scaffold_audio_03_generate` L131)、point_headings L99、voice01 L189 | 撤去後も**legacy/技術的fallback/見出し**が参照しうるため、定数は削除しない(到達不能にするだけ) |

---

## 2. 依存マップ(撤去で壊れる/影響する箇所)

### 2-1. LR再TTSの依存(**最優先、D1**)
- `crosslevel` L383: `_local_rewrite_recovery_for_english_segment_with_fallback`の`_retts_fn`が`_run_a2_minimal_fallback_attempt`を呼ぶ。
- 影響(確定): (1)fallbackを撤去するとLR再TTSが消える。(2)現状でもLR再TTSは**minimal Prompt**(標準Promptではない)で行われる=「Style不変の再生成」ではない(ユーザー新方針「原稿以外不変」と衝突)。
- 対応: LR再TTSを、通常ループと**同じ関数・同じPrompt/model/voice/速度**を呼ぶ「同一Prompt TTS attempt(1回)」に置換。共通ループ(3回)に原稿v1で再入させる(`UNIFIED_FLOW_SPEC_V03.md` 4章)。**確認済み(v04)**: 他のLR再TTS`news_tail_fix` L368は`generate_news_narration_wide_margin.__wrapped__(max_attempts=1, …)`、`voice01` L359は`generate_charon_english.__wrapped__(max_attempts=1, style_prefix_override=…)`で、**どちらもminimal Promptを使わず標準Promptの1 attempt**(ただし`generate_charon_english`内にTTS 400/発話区間検出失敗時の技術的fallback L170-200はある)。**minimal依存のLR再TTSはA2経路(`crosslevel` L383)の1関数だけ**。また、voice01/news_tail_fixは`attempts_log`を連結して累積計数に反映する(voice01 L394、news_tail_fix L371-)が、**A2は`resolved`へretts分のlogを追記しない**=Coffee記録4回/実際5回の構造原因(置換時に同時に是正が必要)。

### 2-2. `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`の使用(D2)
- 定義: `er033_tts_flash_lite_family_x_styles_01.py` L61(`["natural, clear, conversational", "clear"]`)。
- 使用: `repro01` L543(`generate_english_component_minimal_instruction`のFlash-Lite分岐)、`sing01_point_headings_aoede` L97、`voice01` L187、**`er006_audio_cost_pilot_02_shared_narration.py` L166(`welcome`共有殻の通常style)**、`n3_01_tts_generate` L409(コメントのみ)。テスト・Trial: 13ファイル。
- 影響(確定): 名前は「FALLBACK」だが`welcome`共有殻では**通常経路**。**定数を削除・値変更すると`welcome`殻のStyleとMaster Store `style_version`整合が崩れる**(既存音声の再利用不可/再生成)。
- 対応: 「到達不能にするだけ」で**定数は残す**。名称と用途のズレは別整理(改名は`welcome`殻のstyle_instruction_versionに影響しない範囲で、別判断)。

### 2-3. `ATTEMPTS`既定引数の日英共有(D3)
- 定数: `er011_human_review_lock_01.py` L80/L102/L103: `PRODUCTION_MAX_TTS_ATTEMPTS=3`、`PRODUCTION_STANDARD_TTS_ATTEMPTS=2`、`PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS=1`、**`assert STANDARD+MINIMAL==MAX`(L104)**。
- 既定引数: `crosslevel` L82(`standard_attempts`)、`n3_tts` L476、`voice01` L436(日本語`generate_charon_japanese`)。他に`er022_..._stage1/2/3.py`、`er038_tts_all_spoken_role_style_trial_01.py`(Trial)が参照。
- 影響(確定): 英語だけ変更すると日本語の既定が崩れる/assertが落ちる。標準3+minimal0へ変えるなら**定数3つ+assert+既定引数3関数を日英同時に**変更。
- 副次: `standard_attempts`引数自体が不要になる(`max_attempts`のみ)。Trial参照(`er022`/`er038`)は再実行しなければ無害だが「定義だけ残る」Danglingになる(D12型)。

### 2-4. 静的監査・回帰テスト(D4、**意図的に失敗する**)
| ファイル | 内容 | 扱い |
|---|---|---|
| `er006_audio_cost_spec_fix_01_static_audit.py` L50 | `evaluate_attempt_with_cascade`の呼出文字列を数える | 仕様変更として期待値を更新(テストを緩めない) |
| `er006_pool_benches_luna_audio_wiring_test.py` L47 | 配線テスト | 同上 |
| `er007_ja_scg_phase0_regression_test_01.py` L239 | g8除外固定(C1) | C1廃止時に更新 |
| `er007_ja_tts_retry_path_fix_test_01.py`、`er007_ja_scg_test_01.py` | `PRODUCTION_STANDARD/MINIMAL`・`_generate_a2_japanese_minimal_instruction`・`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`を参照 | 2+1->3の期待値を更新 |
| `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`(`_run_a2_minimal_fallback_attempt`を参照)、`er025_pronunciation_resolution_phase4_a2_fallback_evidence_01_run.py`(同関数のruntime evidence run) | fallback経路のEN resolver配線を検証 | 関数撤去で失敗。EN resolver(OPEN-203是正)は**標準経路で既に無条件適用**(確定、repro01 L293付近の構造)なので、検証対象を標準経路へ移す |
| `er011_open121_repetition_qa_production_wiring_01_test_01.py` ほか`force_secondary`関連6ファイル(`er006_secondary_asr_01_test.py`、`er007_reading_validation_wiring_test_01.py`、`er008_audio_validation_gate_05_test.py`、`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`、`er011_tts_attempt_audio_retention_wiring_01_test.py`) | force_secondaryの挙動テスト | `force_secondary`引数を残すか(下)で更新量が決まる |
| `er033_..._family_x_wiring_phase1_regression_01_test_01.py`、`er019_family_x_variable_role_style_wiring_01_test_01.py`、`er006_audio_cost_pilot_02_shared_narration_test.py` | `FAMILY_X_ROLE_STYLE_EN_FALLBACK`/minimal関数を参照 | 同関数/定数を残すなら無変更で通る |

### 2-5. Review Lockの特例(D5)
- `er011_human_review_lock_01.py` L236〜258: 状態`RESOLVED`をブロックしない特例。理由は**6%減速retry**(`generate_a2_segment_with_slowdown`が内側関数を最大3回正当に再呼出)。案B'(外側ループ廃止)でこの根拠が消える=**孤立**(安全側の特例なので残しても害はないが「理由コメント」が嘘になる)。
- 追加: 現行TTS計数は**LR再TTS・外側ループを数えない**(Coffeeで記録4/実際5、確定)。新フローで「script版あたり3+LR後3」を数えるには`record_outcome`/`cumulative_tts_attempts`の集計元(`attempts_log`+`fallback_attempts_log`)を再設計要。`@guarded_generate`のreentrancy guard(OPEN-105)は維持。

### 2-6a. 見出し(Point heading)経路の実態(v04追加)
`er003_v1_sing01_point_headings_aoede.py` L77-100: `max_attempts=3`のとき`minimal_after=max(1,3//2)=1`で**attempt 1のみ標準Prompt、attempt 2・3が`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`/`MINIMAL_INSTRUCTION_PREFIX`(minimal系)**(標準1+minimal2)。ユーザー決定25/26の「標準2+minimal1」とは**別の内訳**で、v01はこの分岐を「通常Style選択の一分岐、撤去対象外(要確認)」としていた。確認結果: (1)内訳は標準1+minimal2(`PRODUCTION_STANDARD/MINIMAL`定数を参照しない独自分割)。(2)`evaluate_attempt_with_cascade`を**`force_secondary`なし**で呼ぶ(L126-128)=見出しのminimal attemptは元から`force_secondary`の保護下に無い。(3)共通フロー化では見出しも標準Prompt 3回へ変えるか、現行の分割を維持するかの判断が要る(`point_one_heading`誤PASS事故[ER-008]の対象経路)。

### 2-6. `force_secondary`
- 定義: `er006_secondary_asr_01.py` L346/L392/L463/L699。使用: minimal fallback(`crosslevel` L341)のみがTrue(確定)。
- **v04確認**: `force_secondary=True`を渡すのは`crosslevel` L341(`_run_a2_minimal_fallback_attempt`)のみ。見出し・B1/Charon・News経路は渡さない。したがって「force_secondary撤去で外れる保護」は**A2のminimal fallback経由(LR後の再TTSを含む)に限られる**。
- 撤去後: 呼出元ゼロ。**引数は残してよい**(既定False、テスト更新を最小化)。ただし「呼ばれない機能が残る」ことを記録(Dangling)。削除する場合は6テストファイルの更新が必要。**撤去の副作用**: ER-008 Part C(minimal経由はPrimary PASSでもAzure必須)で防いでいた「point_one_heading誤PASS」型の根本原因は未決(OPEN)。minimalが無くなれば同経路は存在しないが、**標準経路で同種の誤PASSが再現しうるか**は別途確認(推測)。

### 2-7. Tier3 / CS層とのAzure重複(D6)
- `evaluate_attempt_with_cascade_detail`内でTier3(`er021`)・CS層(Connected Speech)がAzureを別に呼ぶ(確定)。新フローのSecondaryも同じAzureを呼ぶ=**1音声に2回Azure**(費用増)。
- 対応: Secondary転写を共有する改修(新規。fallback撤去とは独立だが、同時期に設計する)。

### 2-8. 日本語固有
- `generate_a2_japanese_with_fallback`(n3)・`generate_charon_japanese`(voice01): 「標準2+minimal1」->「標準3」。minimal関数2つ(L400/L401)を呼ぶループ末尾(n3 L532、voice01 L557)を撤去し標準ループのmax_attemptsを3へ。
- `er011_final26_runtime_evidence_01.py` L78が文言を参照(過去のruntime evidence script。再実行しなければ無害、Dangling)。
- 注意: JA minimal Promptは`JAPANESE_STYLE_PREFIX`が長くてinstruction leakage(指示文を読み上げる)が起きた過去事例(ER-003-N3-ROOT-FIX-01)への対策として導入された(確定、n3 L385〜)。**v04実測(保存attempt json、0円)**: Flash-Lite+`speech_metadata`方式(Production現行)の日本語は**87 attempt(標準86+minimal 1)中leakage 0件**(Wilson95%上限約4%)。leakageは`tts_gemini_3_8_flash_lite_ab_trial_01/b`(指示文をpromptへ含める旧方式)でのみ発生(標準8中7件、minimal 5中3件)。**したがってFlash-Lite期のProduction方式では、日本語minimalを残す根拠となる再発は観測されていない**(U-4(c)の結論: 撤去に支障なし。ただし指示文同居経路が残るなら別)。

### 2-9. 他の呼出元(legacy・Production対象外と見られるもの)
`generate_english_component_minimal_instruction`の呼出元: `er003_v1_b1_scaffold_audio_01/03_generate.py`、`er003_v1_iran01_b1_audio_fix.py`、`er003_v1_sing01_audio_generate.py`、`er012_b_family_voices_production_01.py`(`generate_voice_body_minimal_fallback` L447)等=**Family A/B legacyの個別記事script**(Family X Production runner `er019`は`generate_english_segment_with_fallback`経由)。これらは**関数を残せば無変更**。関数を削除するならlegacy 7ファイルが壊れる(再実行しないなら無害)。推奨: 関数は**削除せず呼出元(`_run_a2_minimal_fallback_attempt`)だけ撤去**。

---

## 3. 撤去手順案(実装は別委任・ユーザー承認後。以下は設計)
順序は「壊れにくい順」。各ステップ後にテスト+runtime evidence。
1. **LR再TTSの独立化**(D1)。標準経路と同一Prompt/model/voice/速度の`_retts_same_prompt`を用意し、`_local_rewrite_recovery_for_english_segment_with_fallback`の`_retts_fn`を差替え。この時点ではfallbackは残る(並存)=安全。LR再TTSの上限は共通ループへ。
2. **共通ループ化**: `generate_english_segment_with_fallback`の標準2回+fallback1回を、標準3回(max_attempts=3)へ。`standard_attempts`引数は廃止or無視。cool-downの位置はU-6の決定に従う。
3. **日本語**: n3/voice01の同様の置換。
4. **定数・assert**: `PRODUCTION_STANDARD/MINIMAL`と`assert`(er011 L102-104)を日英同時に更新(`MINIMAL=0`または定数削除)。Trial参照(er022/er038)は読み取りのみなら影響を確認して注記。
5. **force_secondary**: 呼出元ゼロになるため引数は残置(既定False)。ドキュメント化。
6. **Review Lock特例**(L236-258)の理由コメント更新または撤去(B'採用と同時)。
7. **静的監査・回帰テストの期待値更新**(2-4。緩めずに仕様に合わせる)。
8. **`_run_a2_minimal_fallback_attempt`・`_generate_a2_japanese_minimal_instruction`・`generate_charon_japanese_minimal_instruction`の削除**: 呼出元ゼロを確認してから。`generate_english_component_minimal_instruction`・`MINIMAL_INSTRUCTION_PREFIX`・`FAMILY_X_ROLE_STYLE_EN_FALLBACK`は残す(2-2、2-9)。
9. **Dangling Reference Check**(9章)を実装後に実行。

## 4. 並存期間の設計(Fableが選択)
- 案(i): 1〜2のみ先行(LR再TTS独立化+共通ループ化)、fallback関数は到達不能のまま数週間残す(ロールバック容易)。
- 案(ii): 一括削除。ロールバックはcommit revert。
- 推奨: (i)。「到達不能にしてから削除」でDangling Checkが容易。

## 5. 影響とリスク
| リスク | 内容 | 軽減 |
|---|---|---|
| 救済機会の喪失 | minimalでしか通らなかった事例。英語160件中fallback合格2件、日本語19件中...(報告02 U-4、確定は元データ) | 影響小。決定論的400失敗は技術失敗経路(7章)で扱う |
| 指示文読み上げ(leakage)の再発 | JAで過去に発生。Flash-Liteでの再発率は未測定 | 撤去前に再発率を実データで確認(U-4(c)) |
| 総TTS回数が増える可能性 | LR後3回(最大6)。費用ガード上限の再計算 | 7章・UNIFIED C-6 |
| 既存音声のMaster Store再利用 | Promptを変えない限り影響なし(通常Promptは不変) | KP Prompt変更時のみversion更新 |

## 6. Review Lock特例・force_secondary・fallbackの連鎖(簡略図)
```
generate_english_segment_with_fallback
 ├ 標準経路(generate_narration_snippet_verified_strict) ×2
 ├ [cool-down 600s(enable_connected_speech_equivalence_layer時)]
 ├ _run_a2_minimal_fallback_attempt ×1 ── force_secondary=True ── generate_english_component_minimal_instruction ── FALLBACK[0](Flash-Lite)
 └ 全NG -> _local_rewrite_recovery_...(L383: _retts_fn が上記minimal関数を再利用)
```
撤去後: 標準3回(同一Prompt)->全NG->LR(同一Prompt再TTS、共通ループ3回)->HR。

## 7. 論点として分離(ユーザー判断)
1. 決定論的技術失敗(400 "Model tried to generate text"、指示文読み上げ)専用の隔離経路を残すか(U-4(d))。残さない場合、同一Prompt再試行は無意味なので「1回でHR_TECH」か「上限2回再試行」(UNIFIED 2-5)。
2. B1B技術的fallback(`news_tail_fix` L175、`voice01` L170〜200)を撤去対象に含めるか。
3. `FAMILY_X_ROLE_STYLE_EN_FALLBACK`の名称整理。

## 8. 追加確認が必要な点(未確認)
- (v04で解消)`news_tail_fix` L368、`voice01` L359のLR retts_fnの実体=標準Prompt 1 attempt(2-1)。
- `er019_family_x_audio_production_runner_01.py`が撤去対象関数を直接呼ぶか(grepでは直接参照なし=`generate_english_segment_with_fallback`経由)。実行系の完全な到達性は`er053_dangling_reference_check_01.py`で別途。

## 9. Dangling Reference Check結果(**撤去後の想定**、grepベース、本委任では撤去していないため「撤去した場合に残る参照」)
| 対象 | 撤去後の状態 | 結果 |
|---|---|---|
| `_run_a2_minimal_fallback_attempt`(定義1・呼出2[L181/L383]・テスト/evidence 2ファイル) | 呼出を撤去すると定義のみ残る->削除対象。`er025_..._test_01.py`/`..._run.py`が参照=更新または削除 | **要対応**(依存あり) |
| `_generate_a2_japanese_minimal_instruction`(定義n3 L400、呼出L532、テスト/Trial 9ファイル) | 同上 | 要対応 |
| `generate_charon_japanese_minimal_instruction`(voice01 L401、呼出L557) | 同上 | 要対応 |
| `PRODUCTION_STANDARD/MINIMAL_FALLBACK_TTS_ATTEMPTS`(定義+assert、使用: crosslevel/n3/voice01+Trial/テスト約10ファイル) | 定数変更=全参照の更新要 | **要対応(最重要、日英同時)** |
| `force_secondary`(呼出元=minimal fallbackのみ) | 呼出元ゼロ、引数は残置可 | 軽微(休眠機構) |
| `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`(13ファイル) | **削除しない**(welcome殻で通常使用) | OK(残す) |
| `generate_english_component_minimal_instruction`(legacy含む17ファイル) | **削除しない** | OK(残す、到達性のみ変化) |
| `repro01.MINIMAL_INSTRUCTION_PREFIX` | 残す | OK |
| `KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`/English Lock | KP初回Promptとして使用継続 | **削除しない**(確認済み) |
| `KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`等(repro01 L633-635、他5ファイル) | KP 3回化で定数構成が変わる(別設計、`UNIFIED_FLOW_SPEC_V03.md`3章)。**fallback撤去とは独立** | 別タスク |
| `evaluate_attempt_with_cascade`の呼出文字列を数える静的監査 | 期待値更新要 | **要対応** |
| `review_lock` RESOLVED特例 | 理由コメントが孤立 | 軽微 |
| `er011_final26_runtime_evidence_01.py` L78(文言参照) | 旧evidence script。再実行しなければ無害 | 低(許容か整理か判断) |
| Trial参照(`er022_..._stage1/2/3.py`、`er038_..._trial_01.py`が`PRODUCTION_STANDARD_TTS_ATTEMPTS`参照) | 定数を残す設計なら無変更。削除するとimportエラー | 注意 |

要約: **最初に壊れる**=LR再TTS(L383)、日英共有定数+assert、静的監査/回帰テスト。**残すべき**=`FAMILY_X_ROLE_STYLE_EN_FALLBACK`、`generate_english_component_minimal_instruction`、`MINIMAL_INSTRUCTION_PREFIX`、Key Phrase専用Prompt。

---

## 10. minimalが残る経路の一覧(v04追加、委任_05B 0円確認)
共通フロー化・minimal撤去後も**minimal系Promptが到達しうる箇所**と、その扱い(コードで確認。`UNIFIED_FLOW_SPEC_V04.md` 9-6と同内容)。
| 経路 | 場所 | 内容NG再試行か | 撤去後の扱い |
|---|---|---|---|
| A2英語(標準2+minimal1) | `crosslevel` L181/L292、LR再TTS L383 | はい | 撤去対象(1章) |
| 日本語(標準2+minimal1) | `n3` L532、`voice01` L557 | はい | 撤去対象(2-8) |
| B1/Charon英語の技術的fallback(`trimmed is None`=TTS 400/発話区間検出失敗時) | `voice01` L170-200、`news_tail_fix` L175 | いいえ(技術失敗専用) | 到達不能にするか隔離か(U-4(d))。400は確率的な拒否で同一Prompt再試行が有効(7章) |
| Point見出し(英語、attempt 2・3がminimal) | `point_headings_aoede` L77-100 | **はい**(標準1+minimal2) | **要判断**(2-6a) |
| legacy label(`voice01_labels_fix` L63-66、後半half=minimal) | Family A/B legacy個別script | はい | legacy。再実行しなければ無害 |
| Family A/B legacy個別script(`generate_english_component_minimal_instruction`直接呼出) | 7ファイル(2-9) | はい | 関数を残せば無変更 |
| Key Phrase専用Minimal | repro01 L685 | KP初回Prompt | 削除しない |
| 汎用定数`MINIMAL_INSTRUCTION_PREFIX`/`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` | repro01 L495、`er033` L61 | - | 残す(`welcome`殻で通常使用) |

## 11. Master Storeとminimal(v04追加)
- `er006_output/master_audio_store_01/manifest.json` 378件は全て`key.instruction_path='primary'`で、**fallback/minimal由来を示す記録は無い**(キーにstage情報が無い)。minimal由来が標準キーで保存されていないかは**manifestだけでは判定不能**。
- 混入しうる経路: (a)KP英語の2段目(English Lock、minimalではない): 救済率約1.4%(`UNIFIED_FLOW_SPEC_V04.md` 9-1)、(b)B1/Charon固定殻の技術的fallback(TTS 400/発話区間検出失敗時のみ、頻度不明)。A2 narrationのminimal fallback音声はMaster Storeに入らない(対象は固定殻・KP・数字)。
- 内訳: key_phrase_english_component 340件(v2_margin030 241[2.5-pro 210+Flash-Lite 31]+v1 99)、charon_english_fixed_shell 35件、charon_japanese_fixed_shell 3件。
- 撤去(A2/日本語minimal)はMaster Storeキー(通常Prompt)に影響しない。KP Promptを変更する(P-b/P-c)場合のみ`KEY_PHRASE_TRIM_POLICY_VERSION`更新=既存241件が再利用不可。
