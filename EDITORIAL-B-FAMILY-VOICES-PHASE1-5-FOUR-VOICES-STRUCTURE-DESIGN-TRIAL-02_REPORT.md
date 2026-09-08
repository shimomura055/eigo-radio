# EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02

Lane: B(Lane A[Family A事実確認]と並列稼働、相互独立、Lane A成果物・
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`には触れていない)。
種別: 構造設計Trial(記事本文生成・音声生成・Production実装・Phase 2
Writer配線・Contract/コード編集は禁止、すべて計画・設計のみ)。
LLM API呼び出し: なし(¥0)。バックグラウンド待機なし。

## 前提
- ユーザー決定(2026-09-08): 4 Voicesへ拡張YES、選定軸=案A
  (Applicant / Recruiter-Hiring Manager統合 / Business-Efficiency /
  Fairness-Legal-HR Governance、テーマ"Should companies use AI to
  screen job applicants?")、出典
  `EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01_REPORT.md`。
- 今回の目的: 4 Voices対応への**構造拡張**(見出しブロック数・
  five_section骨格・TTS voice設計・Comment Contract・Tension・QA・
  語数尺・Audio Validation Gate・2/3 Voicesとの関係)を設計・比較し、
  推奨案を1つ提示するまで。本文生成なし。構造案の採用はUSER_DECISION_
  REQUIREDでSTOP。

## 実施内容
- 現行Phase 1構造の事実確認(読み取り専用、Grep+該当箇所抜粋読込):
  `er012_b_family_editorial_type_registry_01.py`(Voice A/B/Narrator
  割当・5区切りSECTION_LABELS・Comment 1〜4確定文言)、
  `er012_b_family_voices_production_01.py`(`split_five_voice_sections()`
  厳密5見出しガード、`build_b1_voices_timeline()`実際のAssembly順序)、
  `EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md`
  (完成episode実測`duration=305.135s`)。
- 構造案3案(S1: 4見出し直列/S2: 2ペア構造+統合Tension/S3: Hook→軸提示
  →4 Voice)を設計し、タスク指定10影響点+実装影響(Lane B内で閉じるか/
  Contract変更要否)の比較表を作成。
- 語数・尺設計: 単純倍増(見積り約500〜610秒)を避ける設計条件を提示し、
  目標尺レンジ約380〜430秒(305秒起点+25%〜+40%、未検証の設計目標)を
  提案。
- 推奨案S1の「Phase 1構造からの差分一覧」(ファイル・関数・設定キー名
  レベル、実装なし)と「未承認仕様として承認が必要な項目一覧」(8項目)を
  作成。
- 3 Voicesとの関係(比較論点、実装なし)を整理。

## 成果物
- `er012_output/editorial_b_voices_phase1_5_four_voices_structure_trial_02/design.md`
  (新規、本Trialの唯一の出力)。

## Gate 1分類
- 構造設計としての妥当性: **VALIDATED**(Trial範囲内、2〜3案比較・
  既存SSOTとの整合確認済み、案S3の新規failure mode[Voice視聴前の軸
  説明がComment 3/Tensionの役割と機能重複]を特定しSTOP扱いとして記録)。
- 採用判断(構造案・Comment Contract変更・TTS voice選定・目標尺の採否):
  **USER_DECISION_REQUIRED**。

## 禁止事項の遵守
記事本文・音声生成なし、Production/Prompt/Contract/コード編集なし、SSOT
編集なし、Git操作なし(本Reportとdesign.mdの追加のみで、user側のcommit/
push判断に委ねる)、Lane A参照なし、Phase 2配線なし、LLM API呼び出しなし。
