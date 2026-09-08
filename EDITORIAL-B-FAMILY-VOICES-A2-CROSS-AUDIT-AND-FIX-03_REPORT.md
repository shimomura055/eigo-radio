# EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03(Lane B)

管理ID: `EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03`
対象: `er012_output/editorial_b_voices_a2_free_address_02/`(TRIAL-02、VALIDATED、保持)
出力: `er012_output/editorial_b_voices_a2_free_address_03/`(新規)

## 0. 結論サマリ

- B-2(Japanese title欠落)のみ「既存A2標準の単純な配線漏れ」と判定し修正・再生成した。
- B-1(Voice A/Bのslowdown)・B-4(Key Phrase「stay put」)は、いずれも既存の
  正式決定・既存Production経路を確認した結果、**新しい仕様判断/新failure mode
  の可能性**にあたるためSTOP(個別patchは実施していない)。
- B-3(Charon/Aoede役割)・B-5横断項目は、既存B-Family(Phase 1 B1、
  PRODUCTION_WIRED)自身の既承認規約と一致しており、修正不要と判定した。
- 費用: 追加TTS実費 **¥0.65**(japanese_title 1segmentのみ、上限¥150以内)。
- Status: **VALIDATED**(APPROVED_FOR_PRODUCTIONは宣言していない)。

## B-1. A2 slowdown(Hookは適用、Voices以降は速い、というユーザー所感)

| 項目 | 既存A2標準 | B-Family A2実適用 | 判定 |
|---|---|---|---|
| 仕様/管理ID | A2 6% slowdown必須post-process(`ER-008-A2-TIMESTRETCH-ABC-10`、Audio Validation Gate `MISSING_MANDATORY_A2_SLOWDOWN`) | 同左を意図的に非適用 | 一致(意図的差異) |
| 対象segment(実装) | `generate_a2_segment_with_slowdown`+`A2_ENGLISH_STYLE_PREFIX_SLOWER`: full_story_part1/2・point_one・point_two・in_one_line(`er003_v1_n3_01_tts_generate.py:842-873`) | Hook Part1/2・Tension・Closing(in_one_line相当)は同関数・同prefixで適用。**Voice A/B本文(point_one/point_two相当)は`b1prod.generate_voice_body_wide_margin`(slowdown非対象)** | **不一致(既知)** |
| 実データ | n3_01 hanshin/health/household a2で point_one/point_two ともslowdown適用済み(`_original.wav`比較用ファイル実在) | `er012_output/.../02/a2/narration/`にpoint_one/two_original.wavが**存在しない**(slowdown post-process未実行の証跡) | 確認済み |
| 判定 | — | **既に`B-A2-9`(Voice A・Bのslowdown要否)としてUSER_DECISION_REQUIRED登録済み**(`DECISION_LOG.md` PM-CLOSEOUT-CONSOLIDATION-18、未回答)。runner.py自身のコメントも「Gate 3の残作業として明示」と記載済み | **STOP**(新A2 slowdown仕様=Voice A/Bへの適用可否そのものがユーザー判断待ちであり、Lane Bが独自に音速を変更することは範囲外) |

対応: 変更なし。既存B-A2-9の再掲としてPM/ユーザー判断待ち。

## B-2. 英語タイトル→日本語タイトル(修正実施)

| 既存A2標準(実データ) | B-Family A2(TRIAL-02) |
|---|---|
| Topic intro(英語, Aoede)→pause 0.65s→**Japanese title(Aoede, 日本語)**→pause 0.5s→Notification 1(hanshin/health/household `timeline.json`実測) | Topic intro(英語, Charon)→pause 0.65s→**Notification 1**(Japanese title欠落) |

対応: `er012_editorial_b_voices_a2_trial02_runner.py`へ`JAPANESE_TITLE_TEXT`(原文タイトルの直訳、新規主張・数字を追加しない。前例
`er011_open112_trend_theme2_b_full_audio_trial_13.py`の手法を踏襲)と、標準A2と同一関数
`n3_tts.generate_a2_japanese_with_reading_safety`によるjapanese_title segment生成・
`load_a2_sources_for_b_family`/`build_a2_voices_timeline`/`_row_info`への配線を追加した(標準A2と同じpause秒数)。

## B-3. Charon / Aoedeの役割・配置

既存A2(単発episode、n3_01/iran01系)ではTopic intro=Aoede、Welcome/Preview
intro/Key phrases intro/Full story intro=Charon(`shared_narration.py`)。一方
B-Family(Phase 1 B1、`er012_b_family_production_runner_01.py`、
`PRODUCTION_WIRED`)は元々Topic intro=Charonで統一(「B-Family Navigator規約」)
しており、B-Family A2(TRIAL-02)はこの**既存B-Family自身の規約**をそのまま
踏襲している(単発A2との差異は意図的・既承認、TRIAL-02固有の新規逸脱ではない)。
Comment 1-4・Preview・Key Phrase日本語gloss=Aoede、Key Phrase英語=Aoedeは
単発A2・B-Familyとも一致。**判定: 一致(B-Family独自の既承認規約どおり)。修正不要。**

## B-4. Key Phrase "stay put"(語末/t/が聞こえない)

- 経路確認: TRIAL-02のkp4英語Componentは`shared_narration.ensure_key_phrase_
  english_component`→標準Production関数`repro01.generate_key_phrase_component_
  verified`→Master Audio Store経由(`master_audio_id=a3a843488c2fc839d8e25f64`、
  `style_instruction_version=v2_margin030`=現行trim margin 0.30秒、
  `created_at=2026-09-07`=最新)。B-Family専用の別経路・改造は一切なく、
  他の全A2/B1と完全に同一のProduction経路を通っている。
- QA証跡: `status=OK, asr_verified=true, asr_text="Stay put.", disfluency_
  checked=true, disfluency_evidence.flagged=false`(2語とも正しく認識、繰り返し
  検知なし)。
- 判定: **既存の配線漏れは無し**(KEYPHRASE-EN-TTS-ROOTCAUSE・ASR false-rejection
  cascade・trim marginいずれも現行版が適用済み)。既存対策を正しく通過した状態で
  なお知覚上/t/が弱いとすれば、それは既存の自動QA(ASRベース)では捉えられない
  **新failure modeの可能性**であり、個別patch禁止の指示に従い**STOP**。
  再生成・別経路への差し替えは実施していない。

## B-5. 横断監査一覧(他A2で正式採用済み・B-Family A2だけ未適用だったもの)

| 項目 | 状態 | 管理ID |
|---|---|---|
| Japanese title segment | **未適用→本タスクで追加** | 既存A2標準(前例`OPEN-112`系Theme2 rerun) |
| Connected speech equivalence layer/repetition QA(4segment: full_story_part1/2・point_one/two) | 適用済み(既存どおり) | OPEN-121/OPEN-122 |
| Repetition QA誤検知是正(em dash・方式D local ASR confirm) | 共有module修正のため自動適用済み(runner側配線不要) | OPEN-127/OPEN-128 |
| Disfluency QA(point_one/two_heading, in_one_line) | 実データはdisfluency_checked=true(生成呼び出しで直接指定)。ただしAudio Validation Gateの`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`辞書に`"B_FAMILY_A2"`キーが未登録のため、Gate側の強制チェックのみ形式的に素通り(実データ自体は基準を満たす、共有module`er003_v1_n3_01_assemble.py`の変更が必要なため本タスクではSTOP・報告のみ) | 参考: `ER-008-N8-FINAL-QA-HARDENING-21` |
| Asset hash staleness check / VALIDATED・HUMAN_APPROVED状態チェック | level非依存のため適用済み | 既存Gate |
| Audio Validation Gate(`B_FAMILY_A2`文字列) | A2 slowdown必須チェックのみ意図的に回避、他は無変更(コード確認済み) | 既存判断(TRIAL-02) |
| Assembly(gain/headroom safety valve) | 無変更のまま適用、_03でも同一挙動を確認(peak 0.98、同一cause_piece) | 既存Gate |
| Fact QA/Naturalness QA(記事レベル) | Step1に属し本タスクでは再実行せず(B-A2-10として既にUSER_DECISION_REQUIRED登録済み) | B-A2-10 |

## B-6. 修正・再生成

### 変更ファイル
- `er012_editorial_b_voices_a2_trial02_runner.py`(既存関数は無変更、新規追加・引数修正のみ):
  `JAPANESE_TITLE_TEXT`定数、`OUT_DIR`/`EPISODE_OUTPUT_BASENAME`の環境変数
  override機構(未指定時は`_02`と完全に同一挙動)、`run_tts`へjapanese_title
  生成追加、`load_a2_sources_for_b_family`/`build_a2_voices_timeline`/
  `_row_info`へのjapanese_title配線、`build_player_html`のnote文言に
  fix-03専用の説明を追加(`is_fix03`分岐、`_02`側は無変更)。

### 新規ファイル
- `er012_b_voices_a2_cross_audit_fix_03_runner.py`: `_02`成果物を`_03`へ
  コピーしてTTS/Key Phrase/scaffold等を再生成せず再利用し(コスト・ドリフト
  防止)、japanese_title 1segmentのみ新規TTS生成→Assembly→player.html生成
  を行う専用driver。

### runtime evidence
- japanese_title: `status=OK`, `asr_text="一つのオフィスに、働く場所についての二つの考え方。"`(canonical textと一致)。
- Assembly: `status=OK`, `duration_seconds`: 335.12→**340.80**(+5.68s、新segment分)、
  `peak`: 0.98→0.98(不変、同一cause_piece=Voice B body、headroom safety valve同様に発火)、
  `clipping_detected: false`(不変)。
- 他segment: 全てMaster Audio Store/既存wav再利用(sha256照合で不変を確認、Audio
  Validation Gate PASS)。
- 費用: ¥0.65(gemini ¥0.62 + openai_asr ¥0.03、japanese_title 1segmentのみ、`_03`
  独自コストログ)。上限¥150以内。
- Attempt回数: japanese_title 1回でOK(retry無し)。
- `run_project_regression.py`: `collected=2195 passed=2192 failed=3 errors=0`
  (既知の無関係failure 3件のみ、新規failure/error無し)。

### 変更前後差分(segment表、抜粋)
| Segment | _02 | _03 |
|---|---|---|
| Japanese title | (無し) | 新規追加(Aoede, 日本語) |
| その他14 segment + Key Phrase 5件 | 既存音声 | 同一音声を再利用(バイト同一、sha256照合PASS) |
| Voice A/B・Hook・Tension・Closing・Comment音声 | 変更なし | 変更なし(B-1/B-4はSTOPのため無改変) |

## player.html

`file:///C:/Users/tensh/eigo-radio/er012_output/editorial_b_voices_a2_free_address_03/player.html`

Gate 7 (a)〜(l): 標準player形式(`player_common`共通関数を無変更で使用、`_02`と
同じ実装)を踏襲。各行にSeek・Segment名+voice・実際に読み上げられたscript・
個別音声を同一行に配置。Episode audio 1本化wavを先頭に配置。Trial出力
(APPROVED_FOR_PRODUCTIONではない)旨・STOP項目(B-1/B-4)をnoteへ明記。

## Gate 1分類

**VALIDATED**(Production採用は別途`APPROVED_FOR_PRODUCTION`が必要、Sonnetは宣言しない)。

## STOPした項目と論点

1. **B-1(Voice A/Bのslowdown)**: 既存A2標準ではVoice本文相当(point_one/two)は
   slowdown対象だが、B-FamilyのVoice A/B(Algieba/Erinome、2声構成)へ同じ
   slowdownを適用すべきかは既に`B-A2-9`としてUSER_DECISION_REQUIRED登録済み・
   未回答。Lane Bが独自に速度を変更する権限は無いため据え置き。
2. **B-4(Key Phrase「stay put」)**: 標準Production経路(Master Audio Store・
   最新trim margin・ASR false-rejection cascade)を正しく通過したにもかかわらず
   知覚上/t/が弱いという指摘であり、既存の自動QA(ASR based)の死角=新failure
   modeの可能性。個別patch(このKey Phraseだけ手動で音を足す等)は禁止事項に
   該当するためSTOP。対応方針(新QA設計要否等)はユーザー/PM判断待ち。
3. B-5で挙げた「Audio Validation Gateの`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_
   LEVEL`に`B_FAMILY_A2`が未登録」は共有module(`er003_v1_n3_01_assemble.py`)
   の変更が必要なため本タスクでは実施していない(実データ自体は基準を満たして
   おり緊急性は無いが、防御多重化の観点でFable/ユーザーへ情報共有)。

## 変更/新規ファイル一覧

- 変更: `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_a2_trial02_runner.py`
- 新規: `C:\Users\tensh\eigo-radio\er012_b_voices_a2_cross_audit_fix_03_runner.py`
- 新規: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_a2_free_address_03\`
  (a2/narration/japanese_title.wav含む全成果物、audit一式、player.html)
- 新規: `C:\Users\tensh\eigo-radio\EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03_REPORT.md`(本ファイル)
