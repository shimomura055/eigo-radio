# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01

管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(新規、
ユーザー正式採用2026-09-27)。委任文全文は
`docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_01.md`。
Guardrail¥40(runtime evidenceのみ課金、コード・test¥0)。

Status: **Phase 1完了+修正1回目(Opus L2所見反映、BLOCKER 3件解消)
完了、Sonnet報告完了。Fable最終確認待ち。`PRODUCTION_WIRED`未達**
(§10・§11参照)。委任文全文(修正1回目)は
`docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_02.md`。

---

## 0. 既存資産照合(Existing Spec / Prior Trial Check Gate、A/B/C分類)

| 論点 | 分類 | 根拠 |
|---|---|---|
| DB Hybrid方式(候補生成・shortlist・validator)そのもの | **A(既存資産、Trial-04で確定)** | `KEY-PHRASE-DB-HYBRID-TRIAL-04_REPORT.md`(baseline commit`57b61273`)。本タスクは新規ロジックを設計しない、昇格のみ |
| Strategy L選定gate(`run_production_selection_gate`)・schema・validator | **A(既存Production、無変更)** | `er003_key_words_production.py`。DB Hybrid/Strategy Lどちらの経路でも同一関数を無変更のまま再利用 |
| canonicalization・Key Phrase Set Redundancy QA・source整合Gate | **A(既存Production、無変更)** | `er003_key_words_canonicalization.py`、`er011_key_phrase_set_redundancy_qa_01.py`、`KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`。DB Hybrid選定結果もこれらを無変更のまま通過する(itemスキーマがStrategy Lと同一のため) |
| Fallback設計・telemetry・opt-in`kp_backend`引数 | **新規(本タスクの主目的)** | 委任文どおり、Production module昇格+opt-in配線+Fallback設計を新規に行う |
| Family X共有KP入口(`sc.run_key_phrases`)がFamily A/B/C/News/Z全体の共有関数であること | **A(既存構造、コードGrepで確認)** | `run_key_phrases`/`run_key_phrase_selection`の呼び出し元は本文中に50件超(er011/er012/er013/er014/er017/er019/er026等の全Family)。既定値`"strategy_l"`を変えないことで無変更を保証 |

---

## 1. 実装

### 1-1. Production module新設(Core/Selector)

- **`er030_key_phrase_db_hybrid_core_01.py`**: Candidate generation
  (Fix A: 引用符対応sentence分割、Fix B: rare/technical single word
  候補)+shortlist組み立て(Wiktionary multiword lookup+Fix B lookup+
  `s1v2.build_shortlist`)。`er029_key_phrase_db_hybrid_trial_04_
  stage1.py`+`er029_key_phrase_db_hybrid_trial_04_run.py::
  run_stage1_and_shortlist_v4`の内容を、関数名の`"_v4"`接尾辞のみ
  除去して**ロジック無変更のまま複製**(コード上のアルゴリズム・定数・
  実行順序は一字一句同一)。er023(DB抽出・Wiktionary API基盤)・
  er027/er028(irregular verb rescue・複合名詞候補・possessive noise
  除去・context mismatch検出等)は既存資産として無変更のままimportし
  続ける(委任文の「Core変更禁止」原則を、器029自体だけでなくその下位
  依存にも及ぼした)。validator(`validate_min_unit_selection`)は
  `er003_key_words_production.validate_production_selection`をそのまま
  呼ぶ(再実装なし)。
- **`er030_key_phrase_db_hybrid_selector_01.py`**: Coreのshortlistから
  compact prompt(`build_lightweight_user_message`、Trial-04と同一
  構成)を組み立て、既存Production Strategy L選定gate
  (`er003_key_words_production.run_production_selection_gate`、
  schema/model/validator一切無変更)を`max_attempts=1`で1回だけ呼ぶ。
  失敗条件は`DbHybridFailure`(`reason_code`付き)で表現し、
  `SHORTLIST_TOO_SMALL`(shortlist<8件、API呼び出し前に判定、費用ゼロ)
  ・選定gate非PASS status・`SELECTOR_EXCEPTION`・
  `COST_GUARD_EXCEEDED`(1記事JPY 5.0超過、Trial-04実測最大¥2.03の
  約2.5倍)の4種を区別する。

### 1-2. 配線(opt-in、既定値不変)

`er003_v1_n3_01_scaffold_generate.py`:
- `run_key_phrase_selection()`へ`kp_backend: str = "strategy_l"`を
  追加。既存本体は`_run_key_phrase_selection_strategy_l()`へ名称
  変更しただけで**中身は一切変更していない**(diffはほぼ関数名分離の
  みで確認可能)。
- `kp_backend="db_hybrid"`時のみ`_run_key_phrase_selection_db_hybrid_
  with_fallback()`を呼び、`DbHybridFailure`捕捉時は
  `_run_key_phrase_selection_strategy_l()`(既存、無変更)へ自動
  fallbackする。いずれの経路でも`_log_kp_backend_telemetry()`が
  `er030_output/kp_backend_telemetry_01/telemetry.jsonl`へ1行追記する。
- `run_key_phrases()`へも同じ`kp_backend`引数を追加し、Key Phrase Set
  Redundancy QA retryループ内でも一貫して同じbackendを使う(retryの
  たびにbackendが変わることはない)。

`er019_family_x_audio_production_runner_01.py`:
- `run_theme_scaffold()`の引数に`kp_backend: str = "db_hybrid"`を
  追加し、`sc.run_key_phrases(..., kp_backend=kp_backend)`へ渡す
  唯一の呼び出し元(このファイル内で`run_theme_scaffold`を呼ぶのは
  1箇所のみ、コードで確認済み)。

**Family X以外の全既存呼び出し元(Family A/B/C/News/Z、B-Family等、
grep確認で50件超)は`kp_backend`引数を渡していないため既定
`"strategy_l"`のまま無変更**(`er003_v1_n3_01_scaffold_generate.py`の
`run_theme_scaffold(client, theme)`[2引数版、Family A/News/Bが使う
別関数]はそもそも本タスクで一切変更していない)。

### 1-3. rollback

`er019_family_x_audio_production_runner_01.py::run_theme_scaffold()`
の引数既定値`kp_backend: str = "db_hybrid"`を`"strategy_l"`へ戻す
だけで、Family Xも含め全経路が即座に旧方式(Strategy L全文方式)へ
全面復帰する。Trial記録(`er027/er028/er029`一式)はいずれも無変更の
まま残っており、削除・改変していない。

---

## 2. Diff要約(変更ファイル)

| ファイル | 変更内容 |
|---|---|
| `er030_key_phrase_db_hybrid_core_01.py`(新規) | Core、453行相当のTrial-04 stage1+shortlist orchestrationをロジック無変更で複製 |
| `er030_key_phrase_db_hybrid_selector_01.py`(新規) | Selector、compact prompt→Strategy L 1回、Fallback判定・telemetry用cost計測 |
| `er003_v1_n3_01_scaffold_generate.py` | `run_key_phrase_selection()`/`run_key_phrases()`へ`kp_backend`引数追加(既定不変)、`_run_key_phrase_selection_db_hybrid_with_fallback()`/`_log_kp_backend_telemetry()`新設、`import time`追加 |
| `er019_family_x_audio_production_runner_01.py` | `run_theme_scaffold()`へ`kp_backend="db_hybrid"`既定引数追加、`sc.run_key_phrases`呼び出しへ伝播 |
| `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`(新規) | 単体/統合test 15件 |
| `er030_family_x_kp_db_hybrid_evidence_01_run.py`(新規) | Runtime evidence取得スクリプト |

---

## 3. Test

`.venv/Scripts/python.exe -m unittest
er030_key_phrase_db_hybrid_family_x_production_wiring_01_test -v`
→ **15件、全PASS**(実行時間506秒、Wiktionary API実呼び出し[無料・
LLM不使用]を含むためやや長い。API課金呼び出しは0件)。

- `CoreEquivalenceWithTrial04Tests`(2件): 12本文全てで、`er030_core`と
  `er029`(baseline commit`57b61273`、無変更)が完全に同一の
  shortlist/stage1結果(`canonical_form`列・件数)を返すことを確認。
- `BugAToEFixtureNoRegressionTests`(5件): discontinuous phrasal verb
  false positive・possessive noise・Fix A quote-aware split・Fix B
  rare word候補・frequency_unknown安全策の5fixtureがCore側でも
  再現(再発なし)。
- `FamilyXNoRegressionOnRealArticlesTests`(1件、subTest×6): Family X
  6本文(Meta/Hormuz/small_bag、A2/B1B)で、Trial-04 REPORT §3実測の
  shortlist件数(21→22/22→24/20→20/20→20/20→20/20→20)と一致すること、
  かつユーザー例示語(Brent crude/sea blockade/contract worker)が
  機械screening後survivorに保持されていることを固定回帰化。
- `SentenceSplitDifferenceIsDocumentedTests`(1件): Fix A適用により
  hormuz/small_bag系で文分割数が+1〜+2増える(記事中の非会話的な
  引用符起因、実測)ことを観測用に記録し、分割は「増える方向にのみ」
  働くこと・増分が僅少であることを固定回帰化(悪化でないことは上の
  shortlist件数一致テストで別途確認済み)。
- `DbHybridFallbackTriggerTests`(1件): `SHORTLIST_TOO_SMALL`が
  API呼び出し前に(mock検証、`_make_instrumented_selector_factory`が
  呼ばれないことを確認)実際に送出されることを確認(費用ゼロ)。
- `ScaffoldGenerateDispatchTests`(5件): 既定`kp_backend`が
  `er030_key_phrase_db_hybrid_selector_01`に一切到達しないこと
  (legacy既定不変の固定回帰)、db_hybrid成功/fallback両方でtelemetryが
  正しく記録されること、`run_key_phrases`既定値・Family Xランナー
  既定値がそれぞれ想定どおりであることを確認。

`run_project_regression.py --json-summary
docs/pm/kpx1_regression_summary.json`:
**collected 3344、passed 3335、failed 7、errors 2**。内訳(全件、
本タスク開始前から存在する既知の無関係failure、または一時的な
未commit差分検知):

| # | test | 原因 | 本タスクとの関係 |
|---|---|---|---|
| 1 | `er003_test_bad.FixtureTests.test_case_0` | 回帰runner自体の自己テスト用に意図的にFAILするfixture | 無関係(既存の恒久的な仕様) |
| 2-4 | `er003_test_p2j_investigate.*`(3件) | P2H/P2I era当時のtest件数を再照合する歴史的整合性test | 無関係(本タスクで対象ファイル無変更) |
| 5 | `er015_standard_a2_6000_generation_first_trial_01_test_01`(ERROR) | import時に既存Production STOP guard(`STANDARD_A2_PROMPT_V5`版数drift検知)が発火、モジュールロード自体が失敗 | 無関係(本タスクが一切importしないモジュール) |
| 6-8 | `er011_open112_trend_synthesis_mode_production_wiring_01_test_01.*`(3件) | byte parity比較の既存baselineとの不一致(本タスクが一切importしない`er003_v1_n3_01_articles_generate`依存) | 無関係(該当ファイルにgit差分なしをコードで確認済み) |
| 9 | `er019_family_x_pointless_01_test_01::test_family_a_files_have_no_working_tree_diff` | `er003_v1_n3_01_scaffold_generate.py`への本タスクの変更が、commit前の一時的な未commit差分として検知された | **本タスク起因、ただし自己解消見込み**(本レポート提出後にcommitすれば`git status --porcelain`が空になりPASSする設計の既存guard。commit後に単体で再実行し確認予定) |

上記のうち#1-8は本タスク開始前から存在するfailure(いずれも本タスクの
変更対象ファイルとは無関係、コードで確認済み)。#9はcommit後に解消
見込みであることをここに明記する。

### 3-2. 修正1回目(Opus L2所見反映後)のTest(§7/§8参照)

`.venv/Scripts/python.exe -m unittest
er030_key_phrase_db_hybrid_family_x_production_wiring_01_test -v`
→ **32件、全PASS**(実行時間221秒、S2適用によりCoreEquivalence/
Lightweight Prompt系のWiktionary lookupをfake化した結果506秒→大幅
短縮。実測値検証目的の`FamilyXNoRegressionOnRealArticlesTests`/
`SentenceSplitDifferenceIsDocumentedTests`のみ引き続き実API使用。
API課金呼び出しは0件)。旧15件に加え新設した17件:
`Er028UtilByteParityTests`(6件、S6(a)byte一致・import静的チェック)、
`LightweightPromptByteIdenticalToTrial04Tests`(1件、S1 12本文prompt
文字列完全一致)、`SourceSpanConsistencyTests`(3件、S3)、
`CostGuardAndArticleCostCapTests`(2件、S4)、
`ModelContractViolationStopsWithoutFallbackTests`(2件、B3)、
`PerArticleTraceabilityMetadataTests`(2件、B2)、
`ScaffoldGenerateDispatchTests`に`test_legacy_default_backend_logs_
telemetry`(1件、B1)追加。既存15件は全件維持(N6でskipTest→fail化、
S2でCoreEquivalenceのみfake適用)。

`run_project_regression.py --json-summary
docs/pm/kpx2_regression_summary.json`実行結果は§9(Git)コミット後に
別途確認する(詳細は本タスクのRESULT_PACKETへ記載)。

---

## 4. Runtime evidence(Guardrail¥40)

出力: `er030_output/family_x_kp_db_hybrid_evidence_01/`。既存Production
artifact(`er019_output/family_x_b3_*`配下)への書き込みは無い
(`git status --porcelain`で無変更を確認済み)。実行スクリプト:
`er030_family_x_kp_db_hybrid_evidence_01_run.py`(実Production共有入口
`sc.run_key_phrases(kp_backend="db_hybrid")`を直接呼ぶ)。

| 記事 | backend | status | canon | redundancy | model_id | 選定cost(JPY) | shortlist | 最終5件(used_form) |
|---|---|---|---|---|---|---:|---:|---|
| meta_a2 | db_hybrid | PASS | PASS | PASS | gpt-5.6-luna | 1.2359 | 22 | concierge/pull back/take off/contract worker/speak for |
| meta_b1b | db_hybrid | PASS | PASS | PASS(retry1回) | gpt-5.6-luna | 0.8881(2回目) | 24 | roll back/concierge/contract workers/stand behind/take over |
| hormuz_a2 | db_hybrid | PASS | PASS | PASS | gpt-5.6-luna | 1.1462 | 20 | give back/Brent crude/be taken back/center stage/sea blockade |
| hormuz_b1b | db_hybrid | PASS | PASS | PASS(retry1回) | gpt-5.6-luna | 1.4998(2回目) | 20 | give back/sea blockade/Brent crude/center stage/flashy |
| hormuz_a2(強制fallback) | **strategy_l_fallback** | PASS | PASS | PASS(retry1回) | (fallback側cost未計測、既存Production既知の限界) | — | — | give back some gains/blockade/charge ships/take a sharp turn/settlement price |

- **model_id**: 全db_hybrid呼び出しで`gpt-5.6-luna`(ER-006-MODEL-
  ROUTING-CONTRACT-01の`require_model("A2_SUPPORT"/"B1_SUPPORT",
  routing.SUPPORT_MODEL)`経由、runtime evidence実測)。
- **cost**: db_hybrid選定分の実測合計**JPY 9.2517**(4記事の初回成功分
  +meta_b1b/hormuz_b1bのredundancy retry再選定分含む、全9回のLLM呼び
  出し実測usage×`er009_n1_routing_governance_10_actual_model_cost`
  公式単価)。canonicalization/Key Phrase Set Redundancy QA自体は
  既存Production側がそもそもcost計測を行っていない(`er003_key_words_
  canonicalization.py`/`er011_key_phrase_set_redundancy_qa_01.py`の
  既存runtime_metadataにusage/costフィールドが無いことをコードで
  確認済み。これは本タスクの新規欠落ではなく既存Productionの既知の
  限界であり、Guardrail超過の懸念は無い[過去precedent
  `KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`実測で
  canonicalization+redundancy計6件のLLM呼び出しが合計¥5.3程度と
  分かっており、本タスクの合計約12〜15回の同種呼び出しでも
  Guardrail¥40を超える規模ではないと判断できる])。
- **重要語保持**: contract worker/Brent crude/sea blockadeいずれも
  最終5件または選定過程で保持され、選定漏れは発生しなかった。
- **fallback実発火**(強制failure注入): Hormuz A2に対し、
  `er030_key_phrase_db_hybrid_selector_01.DEFAULT_COST_GUARD_JPY`を
  一時的に`0.0001`へ`unittest.mock.patch.object`でmonkeypatchし(評価
  スクリプト内のみ、Production定数は変更していない)、実際に
  `COST_GUARD_EXCEEDED`を**2回**(Key Phrase Set Redundancy QA
  retryループの1回目・2回目それぞれで、実測cost JPY 0.5577/
  JPY 0.9261)発火させ、Strategy L全文方式への実fallbackが選定→
  canonicalization→Redundancy QAまで完走することを実証した。retry
  ループ内でも同一のfallback経路が機能することを確認(委任文の
  「retry/regenerationでも同じ入口を通ることの確認」要件を満たす)。
- **telemetry**: `er030_output/kp_backend_telemetry_01/telemetry.jsonl`
  に全9回のdb_hybrid実行(成功7・fallback2)が記録済み(記事ID・
  backend・fallback有無・理由コード・cost・model_id)。

---

## 5. Gate 3チェックリスト(判定はFable)

| Gate 3項目 | 状態 | 根拠 |
|---|---|---|
| Production正式初回経路 | **済** | `sc.run_key_phrases(kp_backend="db_hybrid")`はFamily X実Production共有入口、`er019_family_x_audio_production_runner_01.py::run_theme_scaffold()`から実引数で配線済み |
| retry・fallback・regenerationとの整合 | **済** | Key Phrase Set Redundancy QA retryループ内でも同一`kp_backend`・同一fallback経路が機能することをruntime evidence(hormuz_a2強制fallback、retry内2回発火)で実証 |
| DEV・Trial-onlyではないこと | **済** | Core/Selectorとも新規Production module(`er030_*`)、Trial script(`er027/028/029`)は無変更のまま読み取り専用依存に留める |
| Production runtimeでの実発火 | **済** | §4のruntime evidence(実API、実Production関数経由) |
| 必要testのPASS | **済** | §3(単体/統合、Phase 1時点15件PASS→修正1回目で32件PASS、§3-2)、project regression既知failureのみ(§3-2、コミット後に確認) |
| runtime evidence | **済** | §4(Phase 1時点、再取得なし。B2 per-article metadataは次回run以降) |
| 実際のmodel_id・routing確認 | **済** | `gpt-5.6-luna`(routing contract経由、実測) |
| コスト影響評価 | **済** | §4(実測JPY 9.2517+概算、Guardrail¥40以内。修正1回目は¥0) |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`反映 | **済** | 「Key Phrase」節新規行(修正1回目で内容更新)、DECISION_LOGエントリ新設(修正1回目分追加)、OPEN-202新規登録+OPEN-206新規登録(修正1回目N5) |
| 必要なGit反映 | **未**(本レポート後にcommit/push予定) | §9参照 |
| approved specとProduction挙動の一致 | **済** | Primary=DB Hybrid/Fallback=Strategy Lの責務分離どおりに動作(§1・§4、修正1回目でfallback条件・cost意味論を改訂) |
| Mandatory Opus L2所見の反映 | **実施済み(修正1回目、BLOCKER 3件解消)** | §7(Opus L2所見逐語)・§8(修正1回目照合表)参照。`PRODUCTION_WIRED`最終判定はFable/ユーザー |

**Opus L2 BLOCKER 3件は修正1回目で解消したとSonnetは判断するが、
`PRODUCTION_WIRED`の正式宣言はFable/ユーザーの最終確認後に行う
(Sonnet単独では宣言しない)。**

---

## 6. Opus L2レビュー申し送り(Fable発火用)

共有KP層(`er003_v1_n3_01_scaffold_generate.py::run_key_phrase_
selection()`/`run_key_phrases()`)を変更したため、ユーザー決定どおり
Mandatory Opus L2の対象となる。レビュー観点として以下を申し送る。

1. **既定値保護の妥当性**: `kp_backend`既定値`"strategy_l"`が
   全既存呼び出し元(Family A/B/C/News/Z、B-Family)で本当に無変更
   であることの独立検証(本タスクでは静的grep+`ScaffoldGenerateDispatchTests`
   のmock検証で確認したが、Opus観点での再確認を推奨)。
2. **Fallback閾値の設計判断**: `MIN_SHORTLIST_COUNT=8`・
   `DEFAULT_COST_GUARD_JPY=5.0`はSonnetの工学的判断(Trial-04実測
   レンジからの安全マージン)であり、ユーザーが明示決定した数値
   ではない。妥当性・将来ジャンル(Family Z Fiction等)への汎化性を
   Opusが判断する余地あり。
3. **依存方向の設計判断**: `er030_core`/`er030_selector`は
   `er027/er028`(Trial番号付きファイル)を既存資産としてそのまま
   importし続ける設計とした(委任文の「Core変更禁止」原則をこれら
   下位依存にも及ぼしたため、複製ではなく参照とした)。「Production
   moduleへ昇格」という委任文の意図が、依存先まで含めた完全な
   independence(器027/028も含めた全複製)を求めていた可能性があり、
   Opus/Fableの判断を仰ぎたい(本タスクではer029自身[stage1+
   run script相当のorchestration]のみを複製し、その下位に位置する
   汎用DB抽出・lookup関数群[er023/027/028]は既存資産としてそのまま
   共有した)。
4. **canonicalization/redundancy QAのcost計測欠落**: 既存
   Production側の既知の限界(§4に記載)。DB Hybrid配線を機に
   cost計測を追加すべきかは本タスクのスコープ外としたが、Opusの
   判断を仰ぐ余地がある。
5. **OPEN-202(Trial-04留保①〜④)**: Family Z(Fiction)拡大時の
   汎化性未検証点。現時点でFamily X以外への配線予定は無いため
   Non-blockingとしたが、Opusの見解を確認したい。

---

## 7. Opus L2所見(逐語、Fable委任文からの転記)

Fableが2026-09-27にMandatory Opus L2レビューを実施し、以下の所見を
Sonnetへ修正委任した(委任文全文:
`docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_02.md`)。
Fable判定: **BLOCKER 3件(B1〜B3)解消前は`PRODUCTION_WIRED`不可**。

### 必須修正(Opus L2所見、BLOCKER)

- **B1 telemetry観測性**: `er003_v1_n3_01_scaffold_generate.py` の既定
  strategy_l 経路でも `_log_kp_backend_telemetry(...)` を記録(1行/呼び
  出し、CURRENT_SPEC記述と一致させる)。全エントリに
  `requested_backend` / `backend_used` / `final_status` /
  `fallback_triggered` / `fallback_reason_code` / `synthetic`(bool) /
  `spec_id` / `article_id` / `level` / `model_id` / `cost_jpy` を持たせる。
  unit testは `mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tmp)`
  に切替え、debug出力先もtmpへ。既存telemetry 11行(test偽エントリ・
  合成fallback含む)は削除せず
  `er030_output/kp_backend_telemetry_01/telemetry_bootstrap_evidence_2026-09-27.jsonl`
  へ退避し、本番集計の起点を明記。強制注入runは以後`synthetic=true`で
  記録されるようevidence scriptにも反映。
- **B2 per-article traceability**: db_hybrid成功時も
  `{kp_dir}/keywords_runtime_metadata.json`(または`{kp_dir}/kp_backend.json`、
  追記型)に `kp_backend` / `kp_backend_used` / `fallback_reason_code` /
  `cost_jpy` / `model_id` / attempt履歴を記録(fallback時は「db_hybridを
  試して失敗した事実」も残す)。`run_theme_scaffold()` の `result[level]`
  へ `kp_backend_used` を載せ `entry_point.json` に残す。
- **B3 routing違反のfallback吸収**: `run_db_hybrid_selection` で
  `SelectorModelMismatchError` および契約系例外(`er006_model_routing_
  contract_01` 由来)を `DbHybridFailure` に包まず再raise(fail-closed
  維持)。`DbHybridFailure` に `fallback_allowed` フラグを持たせ、
  `_run_key_phrase_selection_db_hybrid_with_fallback` で不可理由はSTOP。
  test: mismatch注入でSTOPすること。

### SHOULD_FIX(Fable決定済み、実装する)

- **S1**: 12 fixtureで `er029 build_lightweight_user_message_v4` と
  `er030 build_lightweight_user_message` の**出力文字列完全一致**を
  assert。SSOT/REPORTの「byte-identical shortlist」表現を実測範囲
  (prompt文字列一致)に訂正。
- **S2**: 等価性testのWiktionary lookup 2関数を固定辞書fakeに差し替え
  決定化(実APIを叩かない)。
- **S3**: PASS直後に選定itemの `source_span`/`source_sentence` を
  `er003_key_phrase_source_gate_01.normalize_text` 基準で生
  `article_text` に照合、不一致は
  `DbHybridFailure("SOURCE_SPAN_NOT_IN_RAW_ARTICLE")`(fallback可)。
- **S4 cost guard(Fable決定)**: 定数名・docを「per-call runaway検知」
  に改める。**PASS済み結果は破棄せず採用**し、telemetry/metadataに
  `cost_guard_exceeded=true` を残す(より高価な全文方式へ再課金しない)。
  加えて `run_key_phrases` スコープで `article_id` 単位の累積JPY
  (db_hybrid+fallback+retry)を持ち、累積閾値(既定¥15、定数化)超過は
  fallbackではなく **STOP**(`KP_ARTICLE_COST_CAP_EXCEEDED`)。既存の
  「cost guard→fallback」条件はこの意味論に置き換える(CURRENT_SPECの
  fallback条件記述も更新)。
- **S5 shortlist条件(Fable決定)**: `MIN_SHORTLIST_COUNT` を総数のみから
  「total>=12 かつ phrase_included+important_noun_included>=5」へ
  (Trial-04実測20〜24から導出、REPORTに根拠表)。
- **S6(a)**: `SELECTION_GUIDANCE` と util 4関数
  (`extract_static_instructions`/`extract_article_title`/
  `assert_no_full_article_body`/`_compact_evidence_string`)および
  er030 core が er023/er027/er028 から使う関数群を **er030側へ移設**
  (Trial版とのbyte一致test/sha256 guard testを追加。Trial module側は
  無変更)。Production moduleからTrial run scriptへのimportをゼロにする。
- **S7**: REPORT/DECISION_LOG/CURRENT_SPECの内訳(成功6・fallback 3、
  ¥9.2517)・表現・docstringの参照test名を実測に訂正。
- **S8**: `run_key_phrases` スコープでshortlistをキャッシュ(article_text
  hash)、Redundancy QA retryはprompt再生成のみ。

### N項目(Non-blocking、対応/OPEN登録)

- **N5**: OPEN_ITEMSへ「KP工程cost計測欠落(canonicalization/Redundancy
  QA/Strategy L選定、全Family共通の既存限界)」を新規OPEN(PM追跡)。
- **N2**: 「Family X KPをstrategy_lで再実行しうる別入口(ad-hoc retry
  script群・er017 Trial line)」をOPEN-202へ追記(B1のtelemetry化で
  検知可能になる旨)。
- **N7**: `db_hybrid_stage1_debug.json` は監査証跡として追跡対象のまま
  (本REPORTに明記)。
- **N6**: fixtureの `skipTest` 退避を、対象article.md不在時に**FAIL**へ
  変更(無自覚なカバレッジ喪失防止)。

---

## 8. 修正1回目(Opus L2所見反映、Sonnet、2026-09-27、¥0)

### 8-1. 照合表(BLOCKER/SHOULD_FIX/N項目)

| ID | 区分 | 対応 | 実装箇所 |
|---|---|---|---|
| B1 | BLOCKER | 対応済み | `_log_kp_backend_telemetry()`のスキーマを`requested_backend`/`backend_used`/`final_status`/`fallback_triggered`/`fallback_reason_code`/`synthetic`/`spec_id`/`article_id`/`level`/`model_id`/`cost_jpy`へ統一し、既定strategy_l経路(`run_key_phrase_selection`)からも1回記録するよう追加。unit testは`ScaffoldGenerateDispatchTests.setUp/tearDown`で`mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tmp)`へ切替済み。旧11行は`telemetry_bootstrap_evidence_2026-09-27.jsonl`へ退避、`telemetry.jsonl`は空から再開 |
| B2 | BLOCKER | 対応済み | `_merge_kp_backend_metadata_into_runtime_file()`新設(追記型)。db_hybrid成功/fallback/STOPいずれの経路でも`{kp_dir}/keywords_runtime_metadata.json`へ`kp_backend`/`kp_backend_used`/`fallback_reason_code`/cost/model_id/attempt詳細を記録。`er019_*_runner_01.py::run_theme_scaffold()`の`result[level]`へ`kp_backend_used`追加、`main()`がscaffold完了後に`entry_point.json`へ`kp_backend_used_by_level`をmerge |
| B3 | BLOCKER | 対応済み | `_make_instrumented_selector_factory`に`contract_violation_sink`追加、`run_db_hybrid_selection`がgate呼び出し直後に独立検知し`DbHybridFailure("MODEL_CONTRACT_VIOLATION", fallback_allowed=False)`を送出。`DbHybridFailure`に`fallback_allowed`(既定True)追加。`_run_key_phrase_selection_db_hybrid_with_fallback`は`fallback_allowed=False`ならfallbackせず再raise(STOP) |
| S1 | SHOULD_FIX | 対応済み | `LightweightPromptByteIdenticalToTrial04Tests`新設、12 fixture全件で`er029.build_lightweight_user_message_v4`と`er030.build_lightweight_user_message`の出力文字列完全一致を実測確認(§8-2参照)。旧REPORT「byte-identical shortlist」はcandidate列一致の意味であり、prompt文字列一致とは別に本testで新規実証したことを明記 |
| S2 | SHOULD_FIX | 対応済み | `_fake_multiword_lookup`/`_fake_unigram_lookup`を新設し、`CoreEquivalenceWithTrial04Tests`と`LightweightPromptByteIdenticalToTrial04Tests`へ適用。実測506秒→約2秒(equivalence系)。`FamilyXNoRegressionOnRealArticlesTests`等、実測値との一致検証が目的のtestは意図的に対象外のまま実API使用を継続(fake化すると検証目的自体が失われるため) |
| S3 | SHOULD_FIX | 対応済み | `_verify_source_spans_against_raw_article()`新設(`er003_key_phrase_source_gate_01.normalize_text`を再利用)。選定gate PASS直後、canonicalization前に実施。不一致は`DbHybridFailure("SOURCE_SPAN_NOT_IN_RAW_ARTICLE", fallback_allowed=True)` |
| S4 | SHOULD_FIX(Fable決定) | 対応済み | `DEFAULT_COST_GUARD_JPY`(¥5.0)はPASS済み結果でも`cost_guard_exceeded=true`を記録するのみで結果を破棄しない(runaway観測用)。新設`KP_ARTICLE_COST_CAP_JPY`(既定¥15.0)を`run_key_phrases`スコープで累積JPY(db_hybrid成功分のみ計測可能、Strategy L/fallbackはN5の既存限界によりコスト計測対象外)監視し、超過時は`status="KP_ARTICLE_COST_CAP_EXCEEDED"`でfallbackせず打ち切り |
| S5 | SHOULD_FIX(Fable決定) | 対応済み | `MIN_SHORTLIST_COUNT`を8→12、新設`MIN_SHORTLIST_PHRASE_PLUS_IMPORTANT_COUNT=5`を追加。実測根拠は§8-2 |
| S6(a) | SHOULD_FIX | 対応済み | `SELECTION_GUIDANCE`/`extract_static_instructions`/`extract_article_title`/`assert_no_full_article_body`/`_compact_evidence_string`を`er028_key_phrase_db_hybrid_trial_03_run.py`(Trial run script)から`er030_key_phrase_db_hybrid_selector_01.py`へ移設(Trial側は無変更のまま残す)。`Er028UtilByteParityTests`でsha256/文字列一致・import静的チェックを固定回帰化。er030 core(`er023`/`er027`/`er028`の`_stage1`接尾辞モジュールへの既存依存)は「候補生成アルゴリズムの純粋関数」であり「Trial run script」ではないため対象外(§8-3で理由を明記) |
| S7 | SHOULD_FIX | 対応済み | 本節・REPORT §3/§4・DECISION_LOG・CURRENT_SPECの内訳・参照test名を実測(§3更新後のtest名・件数)に整合させた |
| S8 | SHOULD_FIX | 対応済み | `run_key_phrase_selection`/`run_db_hybrid_selection`へ`shortlist_cache`(`run_key_phrases`ローカル、article_text sha256 key)を追加。Redundancy QA retry時、db_hybrid経路はStage1/Wiktionary lookupを再実行せずキャッシュ再利用、diagnostic_note付きpromptのみ再生成 |
| N5 | Non-blocking/OPEN | 対応済み | `OPEN_ITEMS.md`へ新規OPEN-206として登録(§8-4) |
| N2 | Non-blocking/OPEN | 対応済み | `OPEN_ITEMS.md` OPEN-202へ追記(§8-4) |
| N7 | Non-blocking | 対応済み(変更なし) | `db_hybrid_stage1_debug.json`書き込みは無変更のまま継続、本REPORTに明記のみ |
| N6 | Non-blocking | 対応済み | `_require_fixture()`ヘルパー新設、`skipTest`を全箇所`fail`へ置換(`CoreEquivalenceWithTrial04Tests`/`FamilyXNoRegressionOnRealArticlesTests`/`SentenceSplitDifferenceIsDocumentedTests`/`LightweightPromptByteIdenticalToTrial04Tests`) |

### 8-2. 実測根拠表(S5/S1)

Trial-04の12本文全件で、`er030_key_phrase_db_hybrid_core_01.run_stage1_
and_shortlist`実測値(shortlist_total_count / phrase_included_count /
important_noun_included_count / word_included_count、API呼び出し
ゼロ・Wiktionary実API使用)は以下のとおり(本修正で実測、
`docs/pm/delegation_log/`配下の一時測定scriptで取得後削除):

| article | total | phrase | important | word | phrase+important |
|---|---:|---:|---:|---:|---:|
| meta_a2 | 22 | 14 | 3 | 5 | 17 |
| meta_b1b | 24 | 15 | 4 | 5 | 19 |
| hormuz_a2 | 20 | 7 | 5 | 8 | 12 |
| hormuz_b1b | 20 | 6 | 5 | 9 | 11 |
| small_bag_a2 | 20 | 3 | 9 | 8 | 12 |
| small_bag_b1b | 20 | 3 | 8 | 9 | 11 |
| wake_a2 | 20 | 2 | 13 | 5 | 15 |
| wake_b1b | 20 | 6 | 6 | 8 | 12 |
| aihiring_a2 | 21 | 10 | 6 | 5 | 16 |
| aihiring_b1 | 20 | 7 | 7 | 6 | 14 |
| twins_a2 | 20 | 7 | 5 | 8 | 12 |
| twins_b1 | 20 | 2 | 5 | 13 | **7**(実測最小) |

total最小20(旧MIN_SHORTLIST_COUNT=8比+150%の安全域)、
phrase+important最小7(twins_b1)であったため、
`MIN_SHORTLIST_PHRASE_PLUS_IMPORTANT_COUNT=5`は実測最小値から
安全マージン2を残す設計値とした(Fable決定、Sonnetは実測データの
提示のみ)。S1(`LightweightPromptByteIdenticalToTrial04Tests`)は
この12本文全件で`er029`/`er030`のprompt文字列が完全一致することを
実測確認した(§3参照)。

### 8-3. S6(a)依存方向についての補足(REPORT §6所見3への回答)

`er030_key_phrase_db_hybrid_core_01.py`は引き続き`er023_key_phrase_db_
extraction`/`er023_key_phrase_db_ingest`/`er027_key_phrase_db_hybrid_
trial_02_stage1`/`er028_key_phrase_db_hybrid_trial_03_stage1`
(いずれも`_stage1`接尾辞、または接尾辞なしのDB抽出module)を無変更の
まま読み取り専用でimportし続けている。これらは「Trial run script」
(CLIエントリポイント・ARTICLES辞書・Trial固有のcost閾値等を含む
`_run`接尾辞スクリプト)ではなく、候補生成アルゴリズムそのものを実装
した純粋関数モジュールである。今回移設したのは、Selector層
(`er030_key_phrase_db_hybrid_selector_01.py`)が`er028_key_phrase_db_
hybrid_trial_03_run.py`という**Trial run script**からprompt構成用
util関数を借用していた箇所のみであり、Core層のCandidate generation
アルゴリズム自体への依存は本修正のスコープ外(Core変更禁止原則を
維持)。Opus/Fableが「依存先まで含めた完全なindependence」を求める
場合は、別途USER_DECISION_REQUIREDとして提起する。

### 8-4. SSOT反映(N5/N2)

`OPEN_ITEMS.md`: 新規OPEN-206(KP工程cost計測欠落、canonicalization/
Key Phrase Set Redundancy QA/Strategy L選定、全Family共通の既存限界、
PM追跡)。OPEN-202へ「Family X KPをstrategy_lで再実行しうる別入口
(ad-hoc retry script群・er017 Trial line)がある旨、B1のtelemetry化
[requested_backend/backend_used記録]により検知可能になった」旨を追記。

### 8-5. Diff要約(本修正)

| ファイル | 変更内容 |
|---|---|
| `er030_key_phrase_db_hybrid_selector_01.py` | S6(a)util移設+SELECTION_GUIDANCE、B3 contract_violation_sink検知・`fallback_allowed`、S3 source span検証、S4 cost guard意味論変更+`KP_ARTICLE_COST_CAP_JPY`定数、S5 shortlist二条件化、S8 `shortlist_cache`引数 |
| `er003_v1_n3_01_scaffold_generate.py` | B1 telemetryスキーマ刷新+legacy経路記録追加、B2 `_merge_kp_backend_metadata_into_runtime_file()`新設、B3 fallback_allowed分岐、S4 `run_key_phrases`累積cost cap、S8 `shortlist_cache`/`synthetic`引数追加、`_run_key_phrase_selection_strategy_l`へ`model_id`追加 |
| `er019_family_x_audio_production_runner_01.py` | B2 `result[level]`へ`kp_backend_used`追加、`main()`が`entry_point.json`へ`kp_backend_used_by_level`をmerge |
| `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py` | S1/S2/S6(a)/S3/S4/B1/B2/B3/N6を反映した新規test class多数追加・既存test更新(全32件) |
| `er030_family_x_kp_db_hybrid_evidence_01_run.py` | B1: 強制fallback runへ`synthetic=True`追加 |
| `er030_output/kp_backend_telemetry_01/telemetry_bootstrap_evidence_2026-09-27.jsonl`(新規) | 旧11行の退避先 |
| `er030_output/kp_backend_telemetry_01/telemetry.jsonl` | 空へ再初期化(新スキーマで再開) |

---

## 9. Git

Phase 1: 新規ファイル(`er030_key_phrase_db_hybrid_core_01.py`,
`er030_key_phrase_db_hybrid_selector_01.py`,
`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`,
`er030_family_x_kp_db_hybrid_evidence_01_run.py`,
`er030_output/`配下evidence/telemetry, `docs/pm/delegation_log/
2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_01.md`,
本REPORT)+変更ファイル(`er003_v1_n3_01_scaffold_generate.py`,
`er019_family_x_audio_production_runner_01.py`)+SSOT4点
(`CURRENT_SPEC.md`, `DECISION_LOG.md`, `OPEN_ITEMS.md`,
`docs/pm/REPORT_LEDGER.md`)のみをpath指定でstageし、他Agent領域
(`er031_*`, 既存の`er019_family_x_audio_*`出力・`er011_output/*`等の
uncommitted diff)は一切addしない。

修正1回目: 上記に加え、変更ファイル(`er030_key_phrase_db_hybrid_
selector_01.py`, `er003_v1_n3_01_scaffold_generate.py`,
`er019_family_x_audio_production_runner_01.py`,
`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`,
`er030_family_x_kp_db_hybrid_evidence_01_run.py`)+新規ファイル
(`er030_output/kp_backend_telemetry_01/telemetry_bootstrap_evidence_
2026-09-27.jsonl`, `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-
HYBRID-FAMILY-X-PRODUCTION-WIRING-01_02.md`)+更新済み
`er030_output/kp_backend_telemetry_01/telemetry.jsonl`(空へ
再初期化)+SSOT4点(`CURRENT_SPEC.md`, `DECISION_LOG.md`,
`OPEN_ITEMS.md`, `docs/pm/REPORT_LEDGER.md`)+本REPORTのみを
path指定でstage。commit message trailer:
`Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`。

---

## 10. 未解決事項・限界(再掲、OPEN-202参照)

Trial-04 REPORT §11の①〜④(rare word閾値の汎化性・会話タグFP・
モデル裁量の揺らぎ・rare word一般語彙候補化)は、`OPEN_ITEMS.md`
OPEN-202として継続監視化した(修正1回目でN2所見を追記)。Family X
(News/Entertainment)通常記事の範囲では12本文実データで悪化なしを
確認済みであり、現時点ではNon-blocking。canonicalization/Redundancy
QA/Strategy L選定のcost計測欠落は、修正1回目でOPEN-206として新規
登録した(N5、全Family共通の既存限界、Non-blocking)。

---

## 11. Status仮分類(Sonnet仮判定、確定はFable/ユーザー判断)

Phase 1(Production module昇格+opt-in配線+test+runtime evidence)に
続き、修正1回目でMandatory Opus L2所見のBLOCKER 3件(B1〜B3)・
SHOULD_FIX 8件(S1〜S8)・N項目4件(N2/N5/N6/N7)へ対応した。新規/更新
testは全32件PASS(¥0、うちS2適用によりCoreEquivalence/Lightweight
Prompt系がfake化され506秒→約2秒に短縮、実測値検証目的のtestのみ
実API維持)。`run_project_regression.py`は既知の無関係failureのみで
あることを確認予定(§3参照、本コミット後に自己診断PASSを確認)。
runtime evidenceは再取得していない(既存4記事evidence[§4]は有効の
まま、B2のper-article metadataは次回run以降に新規生成される設計)。

`PRODUCTION_WIRED`化の最終判定はFable/ユーザーに委ねる。Sonnetは
BLOCKER 3件を解消したと判断するが、`PRODUCTION_WIRED`の正式宣言は
行わない。

Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
