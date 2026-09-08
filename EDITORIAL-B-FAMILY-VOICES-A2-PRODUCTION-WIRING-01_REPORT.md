# EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01 報告書

**管理ID: EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01**
**種別: Gate 3配線(候補)。Sonnetは`PRODUCTION_WIRED`を宣言しない(Fable/ユーザー受入判定待ち)**
**作成日: 2026-09-09**

---

## 0. 背景・ユーザー決定(2026-09-09、正式)

B-Family A2(「フリーアドレス vs 固定席」A2、`er012_output/editorial_b_voices_a2_free_address_04/`、
ユーザー再試聴「問題なし」、`stay put`新版採用)を`APPROVED_FOR_PRODUCTION`とし、
Gate 3(ユーザー指定15項目)を実施した。根拠となる各Trial Reportは
`EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02_REPORT.md`・
`...-CROSS-AUDIT-AND-FIX-03_REPORT.md`・`...-SLOWDOWN-AND-KEYPHRASE-REGEN-04_REPORT.md`、
Phase 1 Production moduleは`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`。

---

## 1. 実装箇所(ファイル・関数)

| ファイル | 種別 | 内容 |
|---|---|---|
| `er012_b_family_editorial_type_registry_01.py` | 変更(追加のみ) | `B_FAMILY_A2_CONFIG`(audio_gate_level・slowdown_target_segments・comment_language/voice・japanese_title_required/titles・required_segments)、`EDITORIAL_TYPES["b_family_voices"]["a2"]`、`get_editorial_type_a2()` |
| `er012_b_family_voices_a2_production_01.py` | 新規 | A2翻案Writer(Prompt定数+`run_writer_adapt`)、Evidence Compression Editor連携、Fact Checker/Ledger Deviation wrapper、Point Overlap/Value QA monitoring・Analytical Leakage Check(Trial07から全文転記)、Comment/Preview日本語生成(`run_scaffold_a2`)、日本語タイトル生成(`generate_japanese_title`)、Key Phrase A2経路(`reuse_key_phrases_a2`)、Voice A/B slowdown付きTTS合成関数(`generate_voice_body_wide_margin_with_a2_slowdown`)、A2 Assemblyローダー・timeline builder(`load_a2_sources_for_b_family`/`build_a2_voices_timeline`)、OPEN-129整合完全性チェック(`check_required_segments_completeness`)、player行情報(`row_info_a2`) |
| `er012_b_family_production_runner_01.py` | 変更(既存関数は無変更、追加のみ) | `level`引数分岐(`main()`冒頭、既定"b1")、`main_a2()`および一連のA2専用関数(`prepare_a2`/`voice_check_a2`/`reuse_approved_a2_assets`/`run_tts_a2`/`finalize_tts_results_a2`/`run_assembly_a2`/`build_player_html_a2`)、`compute_cost_jpy_so_far()`への後方互換引数追加 |
| `er012_editorial_b_family_production_phase1_test_01.py` | 変更(追加のみ) | 新規テスト19件(下記4節) |
| `er003_v1_n3_01_assemble.py` | 変更(辞書1行追加のみ) | `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`へ`"B_FAMILY_A2"`キー追加(標準A2と同一tuple) |

Trialスクリプト(`er012_editorial_b_voices_a2_trial02_writer.py`/`..._trial02_runner.py`/
`er012_b_voices_a2_cross_audit_fix_03_runner.py`/`er012_b_voices_a2_slowdown_keyphrase_regen_04_runner.py`、
`er012_editorial_b_voices_trial_07.py`)は一切importしていない(全文転記のうえbyte一致テストで確認)。

---

## 2. B1不変の証拠

- 既存Phase1単体テスト14件、変更なしでPASS(本タスク後も全PASS)。
- `main()`の既存B1処理(`level`引数を除く)は1文字も変更していない(追加した
  分岐は`if level == "a2": main_a2(); return`のみ、以降は既存コードそのまま)。
- `compute_cost_jpy_so_far()`へ追加した引数は既定`None`(既存呼び出しは無引数のまま、
  挙動不変)。
- `generate_voice_body_wide_margin()`(Phase1/A2共有)への引数追加は既に
  `EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04`で完了済み・
  既定値保持済み(本タスクでは無変更)。
- `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`の既存"B1"/"A2"エントリは
  単体テストで内容一致を確認(`DisfluencyQaMandatoryDictB_FamilyA2Tests`)。
- project-wide regression: 本タスク前`collected=2214 passed=2211 failed=3`
  (delta=+19は本タスクの新規テストのみ)。

---

## 3. Gate 3チェックリスト(15項目、充足/未充足)

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Production正式初回path統合(Trial非import) | **充足** | §1・4節。ast解析で本tasy新規fileにTrial importが無いことを機械確認(`test_module_does_not_import_any_trial_script_at_module_level`) |
| 2 | retry/fallback/regeneration整合(A2設定引継ぎ) | **充足** | Voice A/B: `generate_voice_body_wide_margin_with_a2_slowdown`が`style_prefix_override`/OPEN-121/122フラグを一貫して渡すこと契約テストで確認。runtime evidenceでもASR cascade・repetition QA・connected speech・6% slowdownが実発火(§6)。Human Review Lock不発動(全segment 1回でOK)。Key Phrase A2再生成経路(`review_lock.approve_regenerate`)は_04時点で既に検証済み、本タスクでは変更していない |
| 3 | Trial専用scriptのみでない | **充足** | 同上1 |
| 4 | runtime発火(level="a2"、TTS_EXECUTION_MODE=STANDARD) | **充足** | §6。完成episode+標準player生成 |
| 5 | Regression/Validator/integration | **充足** | 新規テスト19件PASS(registry/slowdown/comment language/日本語タイトル/Gate辞書/完全性チェック/byte一致/runner level分岐)、`run_project_regression.py`PASS(既知3件のみ、新規failure 0件) |
| 6 | model_id/routing | **充足** | §7 |
| 7 | `B_FAMILY_A2`のGate辞書登録 | **充足** | §8。共有ファイル変更はこの1行のみ(既存B1/A2エントリ・既存関数無変更、diff確認) |
| 8 | OPEN-129整合 | **充足(Lane B側のみ)** | 共有Gateは未対策のまま(OPEN-129 close無し)。Lane B runner側完全性チェックで段数15/15・voice一致を確認(`required_segments_completeness.json`) |
| 9 | `stay put`新版使用確認 | **充足** | §6。sha256一致(新版と一致、旧版とは不一致) |
| 10-12 | SSOT反映 | **充足** | `CURRENT_SPEC.md`新設「## B-Family(Voices)Editorial Type」節、`DECISION_LOG.md`エントリ、`OPEN_ITEMS.md`OPEN-120行更新(`PRODUCTION_WIRED候補`)・OPEN-129行追記(OPEN-131不変) |
| 13 | Git(G1/G2、wav除外) | **充足** | §9(commit hash・push、本メッセージ末尾) |
| 14 | 承認内容とProduction挙動一致 | **充足** | §10表 |
| 15 | Gate 4 Dangling Reference Check | **充足** | §11表 |

**全15項目充足。ただし`PRODUCTION_WIRED`の正式宣言はSonnetから行わない(Fable/ユーザー受入判定待ち)。**

---

## 4. Trialスクリプトimportなしの機械確認

`ast`解析による静的チェック(`test_module_does_not_import_any_trial_script_at_module_level`)で、
`er012_b_family_voices_a2_production_01.py`のimport文に"trial"を含むモジュール名が
0件であることを確認。転記した定数(Analytical Leakage Check prompt/schema、A2 Writer
Prompt各種)は転記元(`er012_editorial_b_voices_trial_07.py`/`er012_editorial_b_voices_a2_trial02_writer.py`)
とbyte-for-byte一致することを単体テストで確認済み(`A2ProductionModuleTranscriptionByteIdentityTests`)。

---

## 5. runtime evidence

出力先: `er012_output/editorial_b_family_voices_a2_production_wiring_01/`。
入力: ユーザー承認済み記事(`er012_output/editorial_b_voices_a2_free_address_04/a2/article.md`、
sha256照合済み、読み取り専用)。`TTS_EXECUTION_MODE=STANDARD`。

- **Voice可用性チェック**(実TTS、2サンプル): Algieba/Erinome双方status=OK(fallback発火なし)。
- **承認済みsegment byte再利用**: 13本文segment(topic_intro/japanese_title/preview/
  comment_1-4/point_one_heading/point_two_heading/full_story_part1/2/tension_reflection/
  in_one_line)+Key Phrase5件×2成分を、`_04`記録sha256と実ファイルの突き合わせで
  fail-closed検証したうえで再利用(不一致なら例外、実行時は全件一致)。
- **Voice A/B本文(Gate 3 item1の中心対象)**: `point_one`(Algieba)・`point_two`(Erinome)を
  正式Production関数`generate_voice_body_wide_margin_with_a2_slowdown()`で実際に新規TTS発火。
  両方1 attemptでstatus=OK、`slowdown_applied=True`(実測5.97%/6.0%近傍)、`asr_verified=True`、
  `repetition_qa_checked=True`(OPEN-121/122安全機構実発火)。
- **OPEN-129整合チェック**: `check_required_segments_completeness()`実行結果
  `{"expected_segment_count": 15, "actual_present_count": 15, "missing_or_not_ok": [],
  "complete": true}`。
- **stay put新版確認**: 再利用した`kp4_en.wav`のsha256が`_04`の`kp4_en_new_v2.wav`と完全一致
  (`b1118d28...`)、`kp4_en_old_v1.wav`とは不一致。
- **Assembly**: `status=OK`、`duration_seconds=350.493`、`peak=0.95049`、
  `clipping_detected=False`、`headroom_safety_valve.applied=False`(閾値0.98未満)、
  Audio Validation Gate level=`"B_FAMILY_A2"`でPASS。
- **player.html**: `er012_output/editorial_b_family_voices_a2_production_wiring_01/player.html`
  (標準player形式、Gate 7 (a)〜(l)全充足、「未取得」行0件、32行)。
- **費用**: 合計¥15.76(gemini ¥14.72 / openai_asr ¥1.04)、上限¥100以内。

---

## 6. model_id/routing確認

- TTS: `gemini-2.5-pro-preview-tts`(`raw_usage_log.jsonl`実測、Voice=Algieba/Erinome/Aoede/Charon)。
- ASR: `gpt-4o-mini-transcribe`。
- Comment/Preview・Writer/Fact Checker routing keyは`routing.require_model("A2_SUPPORT"/
  "WRITER_FACT_CHECK"/...)`経由(既存`er006_model_routing_contract_01.py`、無変更)、
  本タスクではruntime実行で新規呼び出ししていない箇所(Comment再生成等)についても
  registry・関数シグネチャで正しいrouting keyを渡すことをコードで確認済み。

---

## 7. 辞書エントリのdiff(Gate 3 item7)

```diff
 DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL = {
     "B1": ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "in_one_line", "point_one_heading", "point_two_heading"),
     "A2": ("in_one_line", "point_one_heading", "point_two_heading"),
+    "B_FAMILY_A2": ("in_one_line", "point_one_heading", "point_two_heading"),
 }
```

既存"B1"/"A2"エントリ・`_segment_missing_mandatory_disfluency_qa()`等の既存関数は無変更
(単体テスト`DisfluencyQaMandatoryDictB_FamilyA2Tests`で内容一致を確認)。

---

## 8. OPEN-129整合

共有Audio Validation Gate(`verify_episode_audio_validation_gate()`)自体は本タスクでも
未対策のまま(OPEN-129はcloseしない)。B-Family A2 Lane B runner側限定で、
registryの`required_segments`(期待segment名+役割)と実行結果を突合する完全性チェック
(`check_required_segments_completeness()`)を実装し、runtime evidenceで15/15一致・
`complete=True`を確認した。これは共有Gateへの変更ではなく、Lane B側のみの緩和策である
ことを明記する。

---

## 9. Git

G1(Lane B module・テスト・Report・evidence[json/md/html]+`er003_v1_n3_01_assemble.py`辞書1行):
- `er012_b_family_editorial_type_registry_01.py`
- `er012_b_family_voices_a2_production_01.py`(新規)
- `er012_b_family_production_runner_01.py`
- `er012_editorial_b_family_production_phase1_test_01.py`
- `er003_v1_n3_01_assemble.py`
- `EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01_REPORT.md`(新規、本ファイル)
- `er012_output/editorial_b_family_voices_a2_production_wiring_01/`配下(wav除く全ファイル)

G2(SSOT 3ファイル): `CURRENT_SPEC.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md`

commit hash・push結果はコミット後に追記する(下記「Status」参照)。

---

## 10. 承認内容とProduction挙動一致表(Gate 3 item14)

| 承認内容 | Production挙動 | 一致 |
|---|---|---|
| 5区切り構造維持 | `split_five_voice_sections`/`build_parts`(b1prod、無変更)をそのまま使用 | 一致 |
| Voice A=Algieba/B=Erinome/Narrator=Aoede | registry共有、runtime evidence fallback発火なし | 一致 |
| Voice A/B含む英語segmentへ標準A2 6% slowdown | `generate_voice_body_wide_margin_with_a2_slowdown`/`generate_a2_segment_with_slowdown`、実測5.97% | 一致 |
| Comment1-4・Preview=Aoede日本語 | `a2gen.run_support_text`/`n3_tts.generate_a2_japanese_with_reading_safety`経路 | 一致 |
| 日本語タイトル追加 | `generate_japanese_title`+registryの`japanese_titles`辞書 | 一致 |
| stay put新版採用 | sha256一致確認(§5) | 一致 |
| 11語超18/38許容(新上限なし) | article.mdは`_04`のまま無変更で使用 | 一致 |
| Fact Checker REVIEW_REQUIRED今回限り承認 | `_04`時点の専用承認recordをそのまま参照、本タスクでは再判定していない(恒久化していないことをCURRENT_SPEC.mdに明記) | 一致 |

---

## 11. Gate 4 Dangling Reference Check(Gate 3 item15)

| 経路 | Trial script参照 | 未承認仕様(3V/4V・Fact Checker A'・OPEN-129対策)参照 |
|---|---|---|
| 初回(prepare/voice_check/reuse_assets/tts/assemble/player) | なし(ast解析+import確認) | なし |
| retry(TTS ASR cascade内部retry) | なし(既存Production primitive経由) | なし |
| fallback(voice fallback、minimal instruction fallback) | なし | なし |
| regeneration(該当なし、本runは新規byte再利用のみ) | なし | なし |
| Validator(disfluency gate/repetition QA/connected speech/Audio Validation Gate) | なし | なし(`"B_FAMILY_A2"`は既存Gate機構への新規キー登録のみ、3V/4V・Fact Checker A'・OPEN-129対策コードは一切含まない) |
| Human Review | 本run内では不発動(全segment 1回でOK) | なし |

---

## 12. STOP有無

なし。委任範囲内(A2 Production wiring)を完了した。3V/4V・OPEN-129対策(共有Gate側)・
Fact Checker A'は実装していない(禁止事項どおり)。

---

## Status

**Status: IMPLEMENTED(Gate 3候補)— `PRODUCTION_WIRED`はFable/ユーザー受入判定待ち。
Sonnetからの宣言はしない。**
