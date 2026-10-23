# PRODUCTION_PLAN_01 Production反映計画(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01で設計、実施は委任_02。API 0を維持できる計画)

## 1. 適用経路(X/Z双方に1箇所で効くことの確認)
- 修正箇所: `er021_en_asr_semantic_equivalence_production_01.py`(`_tier1_atoms` + 新関数 `_try_clock_pair`)の1ファイルのみ。`er078_asr_value_guard_01._en_sequence`(:352-355)・`er006 classify_asr_match`(Tier1 early-exit :1376)は同関数を参照するだけで無変更。
- X・Z・A/B/C は同じ adapter(`er006_secondary_asr_01.py`)→ `unified_judge` を通る(STRUCTURE_01 §4)。再利用(`er078_reuse_value_guard_01.guard_entry`、Master Store `er006_master_audio_store_01.py:126`)・X引継ぎ(`er019_family_x_validation_inheritance_01.py:256 rejudge_with_current_judge`)・retry/fallback/regeneration/resume も保存転写を同じ判定で再実行するため、コード反映=全経路の配線完了(runnerごとの配線は不要)。
- flag: **不要**(方針: 既存承認仕様の不具合修正[PM_GOVERNANCE 11-8]、既定ON)。`er109_xz_scope_01` は『同音救済(er109)をX/Zだけ有効にする』scopeで、er021/er078のatom化はscope対象外=A/B/Cにも同じく効く(元からerシリーズ共有moduleで、第1層er006 b5138e452・第2層er078 e0eb13ab4も同様にscope外で適用済み)。A/B/Cへの波及は27-7に照らし『時刻形の語列を含む文のみ・方向は誤NG解消と桁連結誤PASS解消のみ』(Opus論点7)。
- 未承認機能の既定値: 新規flag・新規仕様を追加しない。ユーザー指示(OPEN-482の2件を根本原因解消、`ten thirty`と`1030`を一致扱いしない)の実装であり、新仕様候補ではない。ただし年号境界(`twelve fifteen`型)はOpus論点2で確認してから実装する。

## 2. 実装手順(委任_02、Opus条件付き承認後)
1. `proto_C` の差分(`CANDIDATE_C_01.diff`)を実ファイルへ反映(Opusの修正点を織込み)。
2. test: `TEST_MATRIX_01.md` の期待値あり77件を新test(`er021_clock_pair_test_01.py`等)に固定(正常/異常/境界)。既存 `er006_time_numeral_test_01.py`・`er078_time_atom_test_01.py`・`er021` Trial test・er109 test を回帰。
3. replay: `replay_judge_01.py --out after_replay_01.json` → `replay_compare_01.py baseline_replay_01.json after_replay_01.json pairs_01.jsonl`(基準: judge PASS→NG 0、分類層PASS→NG 0、NG→PASSは時刻パターン起因のみ)。pairsは委任_02で再抽出して新規対(委任_01以降の追加分)も含める。
4. 全回帰 `run_project_regression.py`(依存のある環境。委任_01の環境ではgoogle.genai等が無く実行不可)。

## 3. runtime evidence(API 0優先、正式経路の関数で既存音声・ASR結果を再判定)
- 第一: 既存X・Z記事の保存entry(`tts_generation_results.json`等、canon+ASR転写を持つ)から時刻/桁連結パターンを含むものを抽出し、**`rejudge_with_current_judge`(X引継ぎ正式経路)と `er078_reuse_value_guard_01.guard_entry`(再利用の正式経路)**を修正前後で呼ぶ。対象にZ c8(`er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/a2/audit/tts_generation_results.json`、canon『At ten thirty』/ASR『At 10:30』、`run_sf_prod_01`)を必ず含める。X側は `er019_output/` の実記事entryから該当を抽出(無ければ『Xに該当パターン無し=合成entryの正式経路関数による判定』と開示)。
- 第二(必要時のみ): 合成entry(canon=数字化後/語形、ASR=`10:30`/`10 30`/`ten-thirty`/`1030`)を `guard_entry`/`rejudge_with_current_judge` に通し、audit(`asr_judgement.value_guard`・`final_gate`)を保存。
- 新規TTS/ASRが不可欠な場合のみ、X 1clip・Z 1clip(各≤3円。時刻語を含む短文1文)。既存音声再判定で足りるため原則0円の見込み。
- 保存先: 既存 `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/RUNTIME_EVIDENCE_01.md`(新置き場は作らない)。

## 4. 委任_02でのSSOT更新(委任_01では編集しない)
CURRENT_SPEC(値ガード節の `_clock_pair` 記述に『隣接数詞語の時刻形統一[er021]』を追記)、DECISION_LOG(根本原因・案C採用・Opusレビュー結果)、OPEN_ITEMS(OPEN-482を解消、F-1/X-2を新規候補として登録)、`docs/pm/delegation_log/` 逐語保存。

## 5. 費用・リスク
- 委任_01: API 0円。委任_02見込み: API 0円(再判定のみ。新規TTSは不要の見込み、必要でも≤約6円で個別Cap・日次内)。
- リスク: (a)中世年号の語形↔桁連結がNGへ(意図)、(b)過去にPASSした保存entryが再利用時の再判定でNGとなる可能性(`ten thirty`↔`1030`型のみ。replay 5,330対で0件)、(c)Primary誤聴のP1化によるSecondary救済機会の喪失(論点4)。
