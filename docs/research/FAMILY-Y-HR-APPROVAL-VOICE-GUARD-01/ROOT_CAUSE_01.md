# ROOT_CAUSE_01 (FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01 / OPEN-535)

## 結論
承認記録(`human_approved_segments.json`)のscope=「this single segment / this attempt only」(`ypl7_user_approval_record_y_voice_1.json` scope欄)に対し、
承認を**消費する3箇所すべて**がsegment ID + canonical text sha256 だけで照合しており、Voice(・Style)を見ていなかった。仕様文と実装の乖離(PM_GOVERNANCE 11-8の不具合)。

## 一次情報
| # | 箇所 | 照合キー | 結果 |
|---|---|---|---|
| 1 | `er011_human_review_lock_01.py:179-190 _human_approved` / `:299-` `check_before_generation`(`:315`) | text sha のみ | 旧承認が残ると `proceed=False, HUMAN_APPROVED` → TTS/ASR 0 callで再生成をスキップ(`_blocked_result` `:504-527`) |
| 2 | `er003_v1_n3_01_assemble.py:116-137 _segment_gate_status`、`er019_family_x_style_profile_01.py:629-634 _approved`(`er121…:name_not_approved`) | text sha のみ | 非OK entryでも承認で「HUMAN_APPROVED」→ 組立Gateを通過 |
| 3 | `er121_family_y_audio_01.py`(修正前 :492/:606 ほか4箇所)`results[name]["y_tts_voice_requested"] = voice` | 無条件刻印 | 承認スキップ結果(`_blocked_result`は`voice`欄なし)にも「要求Voice」を刻印 → 旧Voice wavが新Voiceのラベルで通る。`voice_guard_cached`(Voice照合)も刻印を信じるため以後のresumeでも露見しない |

`record_human_approval`(`er003…:96-113`)は`canonical_text_sha256/approved_at/approved_by`のみ記録し、Voice/Style/modelを持たない。
再現(修正前): run_01 a2/b1bの`y_voice_1`は旧Algieba attempt限定の承認(`ypl7_user_approval_record_y_voice_1.json`、`adopted_attempt=5`、entry `voice=Algieba`)。
Voice 1=Puck化(2026-10-26)後も承認が残り、`check_before_generation`が`HUMAN_APPROVED`を返す(scratch実測: test `test_old_approval_with_voice_mismatch...`冒頭・EVIDENCE_01)。
なお、実TTSが記録する`entry["voice"]`(例 `Algieba`)は承認時Voiceの一次証拠として使える。

## X/Z経路
同じ構造(承認=text shaのみ): Zは`er063_family_z_audio_01.py:919`(`generate_dialogue_ctx`)で同じ`check_before_generation`、`:1715`の承認読込でGate。
Xは`er019`のdecorator(`guarded_generate`)と`:1333-1343`/`:2365-2367`。**ただしXはナレーターVoice固定、Z/Yのように本文Voiceを後から変更する運用が現状ない**ため実害は未観測。
Zは対話Voiceの割当変更時に同型の問題が起こり得る。本委任ではX/Z無変更(報告のみ)。判定: 修正へ進む/ユーザー判断要/実害なし = **実害なし(現時点)・Z Voice変更時に要対応(次委任案: 同guardのZ適用)**。
