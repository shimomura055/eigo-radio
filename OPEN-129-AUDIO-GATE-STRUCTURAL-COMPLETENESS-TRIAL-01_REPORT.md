# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01

Trial(Production変更なし、¥0、TTS/LLM呼び出し無し)。Lane B。
管理ID: OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01

## 1. 現状分析: 現行Gateの検証/非検証表

対象: `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`
(A-Family A2/B1・B-Family A2/B1が共有するProduction唯一のGate)。

| 検証している | 検証していない |
|---|---|
| `tts_generation_results.json`に実在するsegments/key_phrasesの各entryのstatus(OK/ASR_VALIDATION_UNCERTAIN/HUMAN_REVIEW_LOCKED/STOPPED) | **entry自体が丸ごと欠落**しているsegment(=生成が例外終了しentryが書かれなかった場合)の検知。存在するentryしか走査しないため無条件でスキップされる |
| Human Review承認(`human_approved_segments.json`のsha256突合) | segmentの**voice割当**(entry内の`voice`フィールドは記録されているが一度も参照されない) |
| narration_dir実ファイルsha256と記録sha256の突合(ASSET_HASH_MISMATCH、ファイルが存在する場合のみ) | **余分な(想定外)segment**の混入検知 |
| A2の6% slowdown必須post-process証跡 | segment**総数**が期待値(15件/14件/13件等)と一致するかの直接カウント |
| disfluency QA必須post-process証跡(level別mandatory segment) | `level`文字列がA-Family/B-Familyのどちらの構造を指すか。**B-Family B1とA-Family B1は同一`level="B1"`を共有**(`er012_b_family_production_runner_01.py`が`asm.load_b1_sources()`をそのまま呼ぶ)が、実際の構造は異なる(B-Familyのみ`tension_reflection`を持ち、point_one/twoがvoice_a/voice_bの2役) |

既知failure mode(Grep結果、DECISION_LOG/OPEN_ITEMS): ER-008-N7-CONTENT-AUDIO-QA-02(disk上の旧音声を検知できず誤採用、Gate導入の直接動機)、ER-008-N8-FINAL-QA-HARDENING-21(disfluency_checked証跡欠落)、OPEN-112-THEME2-AUDIO-REVIEW-FIX-02(slowdown_applied=Falseの見逃し)。いずれも「entryの状態」検証であり、「entry集合の完全性」は共通して未対策(OPEN-129)。

## 2. 失敗再現(read-only import、既存wav/JSON無変更)

4経路(A_FAMILY_A2/A_FAMILY_B1/B_FAMILY_B1/B_FAMILY_A2)×5ケース(baseline/delete_segment/voice_swap/reorder/extra_segment)。既存archival dataには本Trial対象外の別metadata gap(旧データのdisfluency_checked未記録等)が混在していたため、current_gate比較専用にstatus/disfluency_checked/slowdown_appliedを正規化した複製で比較(実ファイル無変更、コード内`normalize_baseline_for_gate_reproduction()`参照)。

| ケース | 期待検知 | current_gate(4経路とも) | trial_check(4経路とも) |
|---|---|---|---|
| baseline | しない | しない(一致) | しない(一致) |
| delete_segment | する | **しない(OPEN-129再現)** | する |
| voice_swap | する | **しない(OPEN-129再現)** | する |
| reorder | しない(negative control、JSON dict順序は現アーキテクチャで無意味) | しない(一致) | しない(一致) |
| extra_segment | する | **しない(OPEN-129再現)** | する |

現行Gateは4経路全てで delete/voice_swap/extra を検知できず(20ケース中、期待通り検知12/20はGate側でしない=OPEN-129を明確に再現、trial_check側は20/20全て期待通り)。詳細: `er011_output/open129_structural_completeness_trial_01/reproduction_results.json`

## 3. 設計案比較

- **案(a) level別REQUIRED_SEGMENTSをGate側に持ち突合**: 実装量小、既存levelは現行timelineから導出可能。ただし「level文字列」だけではB-Family B1/A-Family B1を区別できない実データ確認済み(§1)。family+level複合キーが必須。
- **案(b) registry/timeline builderが期待構造をrun summaryへ書き出しGateが突合**: 構造定義を生成側に一元化でき、3V/4V(voice可変)にも自然に拡張できる。実装量大(生成側の複数script改修が必要)。
- **案(c) Lane B runner側`check_required_segments_completeness()`を共有Gateへ昇格**: 既存実績(B-Family A2で15/15確認済み)を再利用でき実装量最小だが、voice_a/voice_bのroleのみでkey phraseは未網羅、B1系は未定義。

**推奨: (a)をベースに(c)の既存パターン(role文字列+voice_a/voice_b解決)を踏襲し、family+level複合キーで定義**(本Trialの`REQUIRED_STRUCTURE_BY_PATH`がこの形の実証実装)。既定はopt-in(新規引数、未指定なら現行動作のまま)とし、後方互換を保ったまま段階的にmandatory化する。

## 4. Trial実装・検知率・false reject

新規: `er011_open129_structural_completeness_trial_01.py`(root、Production無変更)。`check_structural_completeness()`が4経路の必須segment集合・voice role・key phrase(rank×sub-entry件数、名称は生成eraでschema drift実在のため件数ベース)を突合。

- 検知率: 4経路×4検知対象ケース(delete/voice_swap/extra、reorder除く) = 12/12 検知。baseline/reorderの8/8は不検知(期待通り)。
- false reject: 既存完成episode13件(n3_01 3テーマ×2level、rerun_04×2、B-Family Phase1 B1、B-Family A2 4件)に適用 → 12/12の「最終・完成」episodeで0 false reject。残り1件(`editorial_b_voices_a2_free_address_02`)はjapanese_title欠落を検知したが、これは`_03`で追加される**前**の中間iteration(既知の真の未完成状態)であり、false rejectではなくtrue positive(確認済み: `_03`以降は同segmentが存在)。詳細: `er011_output/open129_structural_completeness_trial_01/false_reject_sweep.json`

## 5. Production配線案(実装しない、案のみ)

- 変更候補ファイル: `er003_v1_n3_01_assemble.py`(`verify_episode_audio_validation_gate()`に`required_structure: dict | None = None`引数追加、未指定時は現行動作)、`er012_b_family_editorial_type_registry_01.py`(B1用required_segments追加、A2側にkey phrase網羅を追加)。
- 回帰テスト案: `er012_editorial_b_family_production_phase1_test_01.py`と同型のunit test(15/15・14/14・13/13カウント確認)をA-Family側にも追加。
- 段階導入: (1) opt-inで新規runへ追加しwarningのみ記録 → (2) 既存全経路でfalse reject 0を一定期間確認 → (3) mandatory化。

## Gate分類・USER_DECISION_REQUIRED候補

- Gate 1分類: Trial(`VALIDATED`止まり)、Production実装は未承認。
- Gate 4観点: 既存retry/fallback/Human Review再生成機構と非干渉(read-only、Gate自体は無変更)。
- USER_DECISION_REQUIRED候補: (1) mandatory化のタイミング、(2) 構造定義の正本置き場(registry統合 vs Gate内蔵)、(3) key phrase sub-key命名のschema drift(`english/japanese_meaning` vs `english/japanese` vs `en/ja_charon`)を統一するか。

## 新規ファイル

- `er011_open129_structural_completeness_trial_01.py`(root)
- `er011_output/open129_structural_completeness_trial_01/`(gate_capability_matrix.json、reproduction_results.json、false_reject_sweep.json、reproduction_cases/)
- `OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01_REPORT.md`(本ファイル)
