# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_03 報告(2026-10-12)

範囲: Opus必須修正M1〜M8の設計書v02反映+課金0の先行実装。有料API 0、追加費用JPY0。`PRODUCTION_WIRED`未達。

## 1. 何が問題だったか
Opus独立レビュー(条件A)で、v01設計にM1〜M8(Gate穴・fail-open・配置規約・reuse判定・話者誤割当・Local Rewrite差分・routing key不足・閾値/calibration)が指摘された。また後続実装(04A/04B/04C)が共有する前提(routing key、er020のID認識、Seed、データ契約)が未整備だった。

## 2. 何を変更したか
- 設計書: `er060_output/melos_production_e2e_01/IMPLEMENTATION_DESIGN_02.md`(v01は残置)。M1〜M8・推奨・Fable判断、データ契約4種(seed/segment_plan/provenance/tts_generation_results entry、JSON schema相当)、ファイル配置規約と Family C asset名対応表、04A/04B/04C分担(入出力・禁止領域)。
- routing key 7件追加(`er006_model_routing_contract_01.py`、既存key不変): FAMILY_Z_WRITER_ADV_R0/R1/R2・FAMILY_Z_STD_ADJUST=gpt-6.1-sol、FAMILY_Z_SEMANTIC_JUDGE/STORY_SPLIT/DIALOGUE_ATTRIBUTION=gpt-6-luna。
- `er006_model_routing_gpt6_wiring_test_01.py`: luna固定判定の許可リストにSol 4キーを明示追加(判定自体は緩和せず)。
- `er020_tts_retry_local_rewrite_01.py::resolve_narrative_role`: `full_story_part[1-3]_c[0-9]+`をfullmatchでFULL_STORYと認識(1箇所、既存ID不変、`_original`/`_heading`は不一致)。`CONNECTED_SPEECH_SEGMENT_IDS`に注記。
- Seed複製: `er026_output/family_z_production_e2e_01/melos/seed/`(seed.json sha f4a85f5c...、primary_text_excerpt.md sha cdf8b3dd...、`SEED_PROVENANCE.json`)。Trial成果物は不変。`validator_anchors`は04A担当(仕様のみ)。
- tests: `er060_family_z_foundation_test_01.py` 9件(routing key存在/値/既存key不変、er020 positive/negative/既存ID不変、Seed sha=provenance=Trial元)。
- SSOT: `DECISION_LOG.md`(Opus結果・Fable判断・OPEN-297のZ範囲解除)、`OPEN_ITEMS.md`(OPEN-302更新、新規OPEN-304 X Std part3減速Gate穴、OPEN-305 Family C B1 assembly未実行)、`docs/pm/REPORT_LEDGER.md`。

## 3. 検証(runtime evidence)
- 新test 9件PASS。
- 関連suite(er020/er006/er026/er019/er003/er060の全test file、計1577 test)を変更前(HEADのer006/er020で実行)と変更後で比較: 新規failure/error **0**(既存の失敗は67件[環境起因のImportError等]のうち変更前後とも同集合。変更後64件、差分は新testがHEADでは失敗するため)。
- 途中で`er006_model_routing_gpt6_wiring_test_01::test_process_map_openai_models_all_gpt6_luna`が新規failureとなった(Sol keyがluna固定判定に該当)。許可リストへ明示追加して解消(判定は緩和していない)。

## 4. 改善されること / リスク
- 後続04A/04B/04Cが同一の契約・routing・ID認識を前提に並列実装できる。
- リスク: er020は共有層。Z以外では`_cN`付きIDは生成されず影響なし(negative test固定)。Z narrator clipはconnected speech=Trueとなりcool-down(最大10分/clip)とLocal Rewriteが発火しうる(M6で記録義務化)。語数Guardrail(OPEN-302)は未承認。

## 5. 発見事項(実装せず報告)
- X Stdのpart3の減速Gate穴(OPEN-304、共有層変更を伴うためZ範囲外)。
- `python`コマンドはWindowsストアのスタブでは動かず`py`を使用(環境メモ)。
- Melos台詞に別Voiceを割り当てる既存機構の有無は未確認(`voice_tts_names_plan`にMelos用キー無し)。04C着手時に確認し、無ければSTOP報告(設計書M5に明記)。
