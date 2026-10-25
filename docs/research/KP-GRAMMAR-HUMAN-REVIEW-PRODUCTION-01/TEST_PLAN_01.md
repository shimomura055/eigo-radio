# TEST_PLAN_01(検証7点に対応するtest・runtime evidence計画)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_01 / 日付: 2026-10-25 / 本委任では計画のみ(test未作成・API 0)。実装委任(Opus条件Aレビュー後)で作成・実行。
新規test: `er119_kp_human_review_01_test_01.py`(核)、`er119_kp_human_review_cli_01_test_01.py`、`er119_x_wiring_test_01.py`、`er119_z_wiring_test_01.py`、`er119_isolation_test_01.py`(DefaultOffIsolation型)。証跡置き場: `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/`(新置き場を作らない)。

## 1. ユーザー検証7点 × test/evidence
| # | 検証 | 単体/統合test(mock、API 0) | runtime evidence(実API) |
|---|---|---|---|
| 1 | TOP 8/TOP 2が仕様どおり選定・保存 | (a)Prompt 2-Rの差分assert(`p2r.replace(差分)==p2`)・sha固定 (b)schema(`rank/phrase/word_count/reason_ja`)・件数1〜8 (c)候補ファイルのスキーマ検査(`ai_rank`連番・`raw_rank`・`dropped`理由・`candidates_sha256`再計算) (d)Gate順序(validate→CMU→canon→gloss→CMU post→記号→SRC)が各候補に適用され不合格は`dropped`、順位が詰まる (e)item単位除外とattempt成功閾値(目標数未満のみretry) (f)文法TOP 2は核の合成fixture(`kind="grammar"`)で保存・順位のみ | X 1記事・Z 1作品で`kp_candidates.json`が最大8件・順位・理由・旗付きで生成されること(実モデルID・prompt sha・actual model記録) |
| 2 | Human選定が最終出力へ反映 | selectコマンドの検証(kp⊂vocab、件数、NG交差、重複pair、qa_fail明示、gloss_hr)・finalize(`keywords_canonicalized.json`=選択KP、`vocab_confirmed.json`=5件、署名)・Part 1がvocab 5件を読む・KP音声segmentが3件のまま・公開ページのPart 1が5件 | HRあり run: 選んだ3+5が`kp_selection_final.json`→`keywords_canonicalized.json`→TTS結果→`study_text`→公開ページに現れる(一致検証`verify_selection_matches_outputs` PASS) |
| 3 | 未レビュー時 KP TOP3/解説TOP5/文法TOP1で継続 | 無宣言→`PENDING_REVIEW`・rc=4・下流API 0 / `auto`宣言→`UNREVIEWED_AUTO_ADOPTED`・`ai_rank`順採用・`auto_eligible`外とpair片方を飛ばす・shortfall(1〜2件)でも継続・0件はSTOP / **未レビュー≠NG**(NG集合が空、`verdict=null`)/ 文法: 合成fixtureでTOP1自動(Part 2配線後に本番test) | HRなし run(`--kp-review auto`宣言): 上位3/5で継続し最終成果物到達。`status=UNREVIEWED_AUTO_ADOPTED`が成果物に残る |
| 4 | NG候補は自動採用されない | NG付きreview→(a)select拒否 (b)reselect後にLLMがNG句を再返却→`dropped(human_ng)` (c)外側retry seed excluded (d)AUTO走査スキップ (e)`require_final_consistent`が手編集でNGを混入した確定を拒否 (f)3キー(candidate_id/phrase_key/used_form_key)で基本形化後も一致 | reselect runで、NG句が新候補にも最終にも現れないこと(NG句を意図的に含む記事で確認) |
| 5 | 再生成・再開時も選定結果保持 | resume(sha一致→候補再利用・API 0)/ `--regenerate-stage kp_*`確定済み→STOP(再抽選しない)/ 本文変更→`STALE`・NG保持 / 外側retryが確定後に動かない / 署名不一致STOP / 下流失効(Z `mark_stale_descendants`、X segment invalidate)/ 事後Review(AUTO→REVIEWED)で下流再生成が差分のみ | Z: 確定後に`--stage kp`再実行で選定結果不変・API 0(キャッシュ)を実測。X: `--scaffold-only kp`/`--stage study_text`再実行で不変 |
| 6 | 各Familyの正式経路で機能 | X: `run_theme_scaffold`→review→`study_text`/`tts`入口のfail-closed。Z: `stage_kp`→`load_level_inputs`/`stage_pages`のfail-closed。**Y: 経路なしを確認し未整備として記録(PRODUCTION_WIREDにしない)**。A/B/Cはgolden不変 | X(正式入口`er019_family_x_audio_production_runner_01.py`)・Z(`er026_family_z_fiction_production_runner_01.py`)の正式入口で発火(entry_point/summaryに`kp_review_status`記録) |
| 7 | 既存Gate・音声構成に意図しない変更なし | 全回帰(`docs/research/TEST-HYGIENE-02/REGRESSION_BASELINE_01.md`基準でfailed 0/errors 0)+下記§2の指定test+KP音声segment構成(Std: 英語→日本語意味→英語、Adv: 英語→解説→英語)のgolden不変+Gate判定基準の不変assert(CMU/Validator/canon template/gloss規則のsha) | 非KP音声はMaster Store再利用(新規TTS無し)、KP segmentのみ生成し構成を確認 |

## 2. 既存testの回帰対象(最低限)
`er105_kp_fulltext_selector_01_test_01.py` / `er003_test_kp_fulltext_wiring_01.py` / `er003_test_kp_outer_retry_exclusion_01.py` / `er003_test_kp_review_required_retry_01.py` / `er019_family_x_kp_structure_wiring_01_test_01.py` / `er019_family_x_kp_stage_fail_closed_01_test_01.py` / `er026_family_z_e2e_integration_test_01.py` / `er003_kp_general_explanation_01_test_01.py`(+`_runner_integration_test_01.py`) / `er003_kp_source_sentence_ja_01_test_01.py` / `er104_*`(KP vote、無変更確認) / `er108_kp_cmu_lexicon_gate_01_test_01.py` / `er109_wiring_golden_test_01.py` / `er109_xz_isolation_01_test_01.py` / `er106_joint_runtime_evidence_01_test_01.py`。`KP_COUNT_MAX==3`のassert(`er003_test_kp_fulltext_wiring_01.py:845-851`、`er105…test_01.py:68,267`)は「確定数」の意味で維持。

## 3. DefaultOffIsolation型test(`er119_isolation_test_01.py`)
- 宣言なしで起動 → 候補生成後に`PENDING_REVIEW`、`keywords_canonicalized.json`・`vocab_confirmed.json`・TTS呼出・Part 1 API が0。
- `auto`の入口は2つのみ(`--kp-review auto`、`declare-absent`)。環境変数(`EIGO_KP_REVIEW*`等任意名)・設定dict・関数既定値・`.env`・hook引数からは`auto`にならない(Grepと動作の両方でassert)。
- 共有`sc.run_key_phrases`・Y Trial scaffold・A/B/Cの出力と呼出(引数・戻り値)が不変(既存golden+新規)。
- 文法経路: Part 2採用確認前はProduction経路から到達不可(`er119`のgrammar層がimportされない/配線されないことのGrep assert)。

## 4. runtime evidence run(BUDGET_PLAN_01の4 run)
| run | Family | 経路 | 確認 |
|---|---|---|---|
| R1 | X(既存記事1本。coffee等の既存Adv/Std本文を再利用) | HRあり: 候補生成→`select`(Human選択)→再開→TTS差分(KP segmentのみ)→player/ページ | 検証1,2,4(NG付き1回reselect),5,6,7 |
| R2 | X(同記事) | HRなし: `--kp-review auto`→継続→完走 | 検証3,6,7、AUTO成果物の`UNREVIEWED_AUTO_ADOPTED`表示 |
| R3 | Z(既存作品1本。melos等) | HRあり: kp stage→pending→`select`→`--stages`再開(`provision_shell,gate,assemble,pages,page_verify`を1起動)→page_verify | 検証1,2,4,5,6,7 |
| R4 | Z(同作品の複製run) | HRなし: auto宣言→完走 | 検証3,6,7 |
- 実運用の観測: 実際の選定(TOP 8)・Human介入(select/reselect/NG)・自動継続(auto)の各証拠(ログ・JSON・ページ)を`KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/EVIDENCE_*.md`に保存。
- 公開ページ: 本番公開先へは書かない(複製runのpages_dirを分離。`CURRENT_SPEC.md:2052`注意)。既公開ページの差替えは本件で行わない。
- Family Y: runを行わない。`production_reachable=False`のままで、Y Trial scaffoldが従来どおり3件で動くこと(出力不変)だけをtestで確認し、OPEN-484で未整備追跡。

## 5. PRODUCTION_WIRED判定(Family別、Fable独立受入)に必要な証拠
正式初回経路実装 / retry・fallback・regeneration・resume整合(§1の#5) / 正式runtime発火証拠(R1〜R4) / Regression・Validator・integration PASS / 選定・Human介入・自動継続の実証拠 / SSOT更新(CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS) / Git / ユーザー承認仕様との一致(検証7点)。**文法**はPart 2採用確認後に別途(本計画の範囲外)。**Y**は未整備として追跡。
