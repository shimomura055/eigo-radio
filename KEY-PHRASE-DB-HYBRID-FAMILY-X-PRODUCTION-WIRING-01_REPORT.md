# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01

管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(新規、
ユーザー正式採用2026-09-27)。委任文全文は
`docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_01.md`。
Guardrail¥40(runtime evidenceのみ課金、コード・test¥0)。

Status: **Phase 1完了、Sonnet報告完了。Fable Gate 3判定・Mandatory
Opus L2レビュー待ち。`PRODUCTION_WIRED`未達**(§10・§11参照)。

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
| 必要testのPASS | **済** | §3(単体/統合15件PASS、project regression既知failureのみ) |
| runtime evidence | **済** | §4 |
| 実際のmodel_id・routing確認 | **済** | `gpt-5.6-luna`(routing contract経由、実測) |
| コスト影響評価 | **済** | §4(実測JPY 9.2517+概算、Guardrail¥40以内) |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`反映 | **済** | 「Key Phrase」節新規行、DECISION_LOGエントリ新設、OPEN-202新規登録 |
| 必要なGit反映 | **未**(本レポート後にcommit/push予定) | §7参照 |
| approved specとProduction挙動の一致 | **済** | Primary=DB Hybrid/Fallback=Strategy Lの責務分離どおりに動作(§1・§4) |
| Mandatory Opus L2所見の反映 | **未着手(次段階)** | §6参照、共有KP層変更のためFable発火が必要 |

**未完了項目(Git反映・Opus L2)が残るため、本タスク単独では
`PRODUCTION_WIRED`を宣言しない。**

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

## 7. Git

新規ファイル(`er030_key_phrase_db_hybrid_core_01.py`,
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
uncommitted diff)は一切addしない。commit message trailer:
`Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`。

---

## 8. 未解決事項・限界(再掲、OPEN-202参照)

Trial-04 REPORT §11の①〜④(rare word閾値の汎化性・会話タグFP・
モデル裁量の揺らぎ・rare word一般語彙候補化)は、`OPEN_ITEMS.md`
OPEN-202として継続監視化した。Family X(News/Entertainment)通常記事
の範囲では12本文実データで悪化なしを確認済みであり、現時点では
Non-blocking。

---

## 9. Status仮分類(Sonnet仮判定、確定はFable/ユーザー判断)

Phase 1(Production module昇格+opt-in配線+test+runtime evidence)は
完了し、既知の限界を除き悪化・regressionは確認されなかった。
`PRODUCTION_WIRED`化にはGate 3残項目(Git反映、本レポート後に実施)と
Mandatory Opus L2レビューの完了が必要であり、Sonnetはこの時点での
`PRODUCTION_WIRED`宣言を行わない。

Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
