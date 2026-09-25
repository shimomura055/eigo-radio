# NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01_REPORT.md

管理ID: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01`
実行者: Sonnet(サンドイッチ委任、初回)
日付: 2026-09-25

## §1 正式採用仕様(逐語)

Standard A2では、頻出上位約6,000語以内=原則そのまま使用可、必要に応じてKey
Words/Phrases側で学習補助/6,000語を超える語=より簡単で自然な表現がある場合は
置換を強く優先、ただし置換によって英文の自然さや意味を損なわない/固有名詞は
別扱い/不可欠な専門語は、簡単な代替で意味が失われる場合は残してよい/難語の
説明を本文へ追加してStoryを膨らませない。v5 Promptを正式Standard A2として
採用。**「6000語超を必ず置換」ではない**(septic tank/wastewater/artery等は
必要語として残り得る。municipalitiesのように自然な簡単語へ置換できる難語は
優先的に平易化)。

分離事項: Metaのscope曖昧性(some parts of the calls ↔ parts of some calls)
は本仕様と分離。個別Prompt対応を追加せず、OPEN-177の既存サブ項目(7)として
保持する。

## §2 偵察結果(初回経路・Advanced経路・contract・retry・Key Words)

詳細: `er003_output/standard_a2_wiring_01/recon.md`。要点:

- (a) 日本語Entertainment R2(Original→R1→R2)のProduction正式初回入口は
  **存在しない**(`CURRENT_SPEC.md` L828「配線先Production経路: 未確定」)。
- (b) Advanced(Natural English Adaptation)のProduction実装も**存在しない**
  (`er015_*` Trialスクリプトのみ、OPEN-177(1))。
- (c) 既存News Writer経路のProduction contract(`# Title`+`### `×2+
  `## In one line`)と、Standard A2 v5 Promptの単純contract(Title行+本文
  のみ)は**異なる**。
- (d) retry primitiveは`er003_v1_en_direct_vfl_01_generate.py`(vfl01)の
  `run_writer_no_search`/`run_writer_with_technical_retry`にWriter系全体で
  一元化されている。fallbackモデル定義なし(`routing.PROCESS_MODEL_MAP`)。
- (e) Key Words/Phrasesは記事本文からの抽出(`er003_v1_n3_01_scaffold_
  generate.py`の`run_key_phrases`)で、Standard A2生成とは独立工程。

(a)(b)がともに存在しないため、delegation記載のSTOP条件(「Advanced Natural→
Standard A2の正式初回経路が存在せず、経路の設計に仕様判断が必要」)に該当する。
経路設計自体はFable/ユーザー判断待ちとし、本タスクでは行っていない。

## §3 実装(モジュール・関数・Prompt sha256・呼び出し経路)

新規Productionモジュール: `er003_v1_n3_01_standard_a2_generate.py`

- 定数: `STANDARD_A2_DEVELOPER`/`STANDARD_A2_PROMPT_V5`(v5逐語)、
  `STANDARD_A2_PROMPT_SHA256`(LF正規化sha256、import時にfail-closedで
  assert、`_assert_prompt_sha256()`)。
- 関数: `generate_standard_a2(advanced_text, *, client=None, model=None,
  effort="high", max_retries=1) -> StandardA2Result`。
- 機械チェック: `strip_title`/`extract_fact_tokens`/`run_checks`
  (Ledger不要の簡易diff、Trial importなしの独立実装)。
- cost計算: `_load_pricing`/`_compute_cost_jpy`(`er012_b_family_
  production_runner_01._load_pricing()`と同一ロジックの独立実装、
  `er005_output/cost_baseline_01/pricing_snapshot.json`、USD_JPY=160.0)。
- CLI: `--advanced-file <path> --out-dir <dir> [--max-retries N]`。

Prompt sha256: `cbb72357449dea9bcf0912c55aaf7e5b8ea52f6e157c37ae71180768dc13c589`
(DEVELOPER/USER TEMPLATE定数からTrial file形式[LF正規化後]を再構成した
テキストのsha256。Trial file自体はCRLF保存のため生バイトのsha256は
`597e0d3f669b7d76ce8c651ba2f96d355cd7f706ad927336b49e1d8a2711aac4`だが、
改行コードの違いのみでPrompt内容は完全一致。UTF-8テキストモード
[newline=None]で読み込みLF正規化した場合の一致は
`er003_v1_n3_01_standard_a2_generate_test_01.py::test_prompt_sha256_matches_
trial_file`で確認済み)。

呼び出し経路: **未接続**(§2参照)。CLI直接実行のみで、どのrunnerからも
importされていない。

### 既存Production依存モジュールへの変更(diff、逐語)

STOP条件確認前の設計検証で、`vfl01.run_writer_no_search()`が developer
メッセージをモジュール定数`WRITER_DEVELOPER_MESSAGE`("英語の記事を作成して
ください。")にハードコードしており、v5 Prompt(`STANDARD_A2_DEVELOPER`)を
そのまま送れないことが判明した。重複実装を避けるため、既存関数へ完全後方
互換の拡張を行った(`git diff --stat`: `er003_v1_en_direct_vfl_01_generate.py`
+33/-4行、`er006_model_routing_contract_01.py` +5行)。

1. `er003_v1_en_direct_vfl_01_generate.py::run_writer_no_search()`:
   - 新規オプション引数`developer: str = WRITER_DEVELOPER_MESSAGE`を追加
     (既定値=既存モジュール定数。developerを渡さない既存呼び出し箇所21箇所
     [`er003_discovery_focus_staged_production_01.py`/
     `er011_discovery_focus_s2_full_trial_01.py`/
     `er012_b_family_voices_writer_generic_01.py`等]は挙動が一切変わらない)。
   - 戻り値dictへ`"usage"`キー(input_tokens/cached_input_tokens/
     output_tokens/reasoning_tokens)を追加(既存キー`raw_text`/`model`/
     `response_id`は無変更、辞書アクセスのみの既存呼び出し元には影響しない)。
2. `er006_model_routing_contract_01.py::PROCESS_MODEL_MAP`へ
   `"STANDARD_A2_ADAPTATION": WRITER_MODEL`を新規追加(値はWRITER_MODELと
   同一、新規モデル追加ではない。既存キー・既存値は無変更)。

いずれも追加のみで既存キー/既存デフォルト値を変更していないため、
既存Production挙動への影響はないと判断した(§6のregression結果で確認)。

## §4 retry・fallback・regeneration整合

`generate_standard_a2()`は`vfl01.run_writer_no_search()`(developer引数付き)
を呼び出し、空出力でRuntimeErrorが送出された場合のみ同一Promptで
`max_retries`回(既定1回)まで再試行する(既存Trial`_call_and_record`と同じ
「空出力→1回再試行」方針を、Trial importなしで独立実装)。fallbackモデルは
`routing.PROCESS_MODEL_MAP`に定義が無いため実装していない(News A2/B1
Writerと同じ「fallbackなし」方針)。

ただし、この関数を呼び出す上位のオーケストレーター(既存News Writerの
`MAX_WRITER_ATTEMPTS`のような記事全体retryループ)自体が本Familyには存在
しないため、「既存retry/fallback/regeneration経路との統合」は実地確認できて
いない(Gate 3項目2=△、詳細`gate3_checklist.md`)。

## §5 runtime evidence(Sewer/Meta、model_id実値、cost)

| | Sewer | Meta |
|---|---|---|
| 入力 | `a1_advanced_sewer.md` | `arms/arm3/output.md` |
| response_id | resp_0b7ae0a1ec33f9e9006ab5f3a3aa0c87d0b3df742d870d73e6 | resp_00296e5e7aa628bc006ab5f3c89afc87d0b4f05123e9f7ac1e |
| model_id_actual | gpt-5.6-luna | gpt-5.6-luna |
| fallback_detected | false | false |
| attempts / retried | 1 / false | 1 / false |
| cost_jpy | 0.5045 | 0.2979 |
| checks_failed | [] | [] |

合計cost_jpy = 0.8024(予算¥20の約4%)。保存先:
`er003_output/standard_a2_wiring_01/sewer/{standard_a2.md,runtime_evidence.json}`、
`er003_output/standard_a2_wiring_01/meta/{standard_a2.md,runtime_evidence.json}`。

## §6 テスト結果(単体・regression)

- 単体テスト`er003_v1_n3_01_standard_a2_generate_test_01.py`: **14件PASS**
  (unittest、`python -m unittest ... -v`。pytest未導入のため委任文記載の
  `pytest -q`コマンドは実行できず、リポジトリ標準の`unittest`形式へ変更した)。
  Prompt sha256一致/mismatch検知、build_prompt置換、generate_standard_a2の
  正常系・1回retry成功・2回失敗でraise・fallback検知・effort不一致検知、
  run_checks(タイトル欠落/数字追加/数字欠落)、strip_title/extract_fact_
  tokensをカバー。
- 影響範囲regression(`vfl01.run_writer_no_search`変更の影響を受ける
  既存モジュールを個別実行、全件PASS):
  - `er006_model_routing_contract_01_test.py` — PASS(vfl01関数シグネチャ
    契約含む)。
  - `er003_discovery_focus_staged_production_01_test_01.py` — 24 tests PASS。
  - `er011_discovery_focus_s2_full_trial_01_test_01.py` — 22 tests PASS。
  - `er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py` — 6/6 PASS。
  - 本リポジトリにはpytestも統一test runnerも存在しないため、全`_test*.py`
    一括実行はしていない(事実として記録。委任文の`pytest -q`は不可能
    だったため未実施)。

## §7 Sewer/Meta Production実行結果(全文+6,000超残存語)

全文は§5記載のパスに保存(`standard_a2.md`)。要旨:

- Sewer(下水道): 18語が6,000語超/表外(septic, sewers, invisible,
  surprisingly, repairs, treats, cleaned, pipes, handles, connects, flush,
  baths, artery, sewer, inspections, collects, kitchens, wastewater)。
  中心比喩(main artery/washing machine)は保持。
- Meta(AI Call): 9語が6,000語超/表外(understudy, concierges, leak,
  belonged, curtain, performer, trusting, backstage, paused)。劇場比喩
  (stage/backstage/curtain/performer/understudy)は許容語として保持。

計測はwordfreq(`top_n_list("en", 20000)`)を直接使用(Trial scriptから
importせず、独立スクリプトで実行)。不自然置換・v4で問題視された
「難語→難語」置換の再発は目視観察で確認されなかった。

## §8 CURRENT_SPEC更新(逐語)

`CURRENT_SPEC.md` L829直後へ新規行を追加(既存Advanced行は変更していない)。
追加行の内容(要旨、全文はファイル参照): Standard(A2) = v5「6,000語ライン+
自然さ優先」Prompt(正式仕様逐語をそのまま記載)、Production module
`er003_v1_n3_01_standard_a2_generate.py`(`generate_standard_a2()`、Prompt
定数・sha256 assert)、v1〜v5の到達履歴、Status=`APPROVED_FOR_PRODUCTION /
WIRING INCOMPLETE`(未接続の理由を明記)、根拠管理ID列。

## §9 DECISION_LOG更新(逐語)

`DECISION_LOG.md`末尾へ新規セクション「## NEWS-STANDARD-A2-VOCAB-6000-
CUTOFF-PRODUCTION-WIRING-01: User formally approved Standard A2 v5
(6,000-cutoff)、Production module実装・Gate 3判定」を追加。ユーザー指示
逐語・偵察結果・実装詳細・runtime evidence・regression結果・Gate 3
チェックリスト14項目・最終Status・未完了事項・関連管理IDを記録(全文は
ファイル参照)。

## §10 OPEN_ITEMS更新(逐語)

OPEN-177を更新。サブ項目(2)retry・fallback consistency[Standard A2部分]・
(5)runtime evidence[Standard A2部分]・(9)Standard A2 v5 Production module
実装[新規]を**CLOSED**、(1)Production official initial path wiring・
(3)Production contract付与・(4)Audio path・(6)Fact・Ledger consistency・
(7)Meta scope曖昧性一次情報確認・(8)final regression・integration tests
[Production pipeline全体]は**OPEN継続**として明記。新規Open Itemは起票
していない(既存OPEN-177の更新のみ)。

## §11 Git

対象ファイル(明示add、`git add -A`不使用):
- `er003_v1_n3_01_standard_a2_generate.py`(新規)
- `er003_v1_n3_01_standard_a2_generate_test_01.py`(新規)
- `er003_v1_en_direct_vfl_01_generate.py`(既存、developer引数+usage戻り値
  追加)
- `er006_model_routing_contract_01.py`(既存、PROCESS_MODEL_MAPへ1行追加)
- `er003_output/standard_a2_wiring_01/`配下(sewer/meta の standard_a2.md・
  runtime_evidence.json、recon.md、gate3_checklist.md)
- `CURRENT_SPEC.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md`
- `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01_REPORT.md`
- `docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-
  WIRING-01.md` / `.md_check.json`

commit SHA・push結果は本REPORT作成後にRESULT_PACKETへ記載する。

## §12 Dangling Reference Check

`Grep "er015_" glob="er003_*.py,er012_*.py"`: 一致は本タスクの新規ファイル
自体(`er003_v1_n3_01_standard_a2_generate.py`のコメント3箇所、
`er003_v1_n3_01_standard_a2_generate_test_01.py`のパス文字列1箇所)のみで、
いずれも`import er015_...`文ではない(コメント内のTrial file言及、および
テストがsha256照合のために読み込むファイルパス文字列)。実行時import(`import
er015`)は0件。

`Grep "STANDARD_A2_PROMPT_V5"`: 定義1箇所(`er003_v1_n3_01_standard_a2_
generate.py`)+参照2箇所(同ファイル内`reconstruct_prompt_file_text()`/
`build_prompt()`)のみ。他ファイルからの参照なし(未接続のため)。

## §13 Gate 3チェックリスト

詳細: `er003_output/standard_a2_wiring_01/gate3_checklist.md`。要約:

○: 3(Trial-onlyでない)、7(test PASS)、8(runtime evidence)、9(model_id・
routing確認)、10(コスト影響評価)、11(CURRENT_SPEC)、12(DECISION_LOG)、
13(OPEN_ITEMS)、14(Git、本コミットで実施)、approved specとProduction挙動
の一致、Dangling Reference Check。
△: 2(retry/fallback整合、関数単体は方針一致だがオーケストレーター不在で
実地確認不能)、5(Key Words/Phrases役割分担、設計上矛盾なしだが未接続)。
×: 1(Production正式初回経路への接続)、4(Advanced経路との整合、Advanced
自体が未実装)、6(Production正式pathでのruntime発火、CLI直接実行のみ)、
9系(Sewer/MetaでProduction経路から期待挙動、経路自体が無い)。

## §14 未完了事項

1. 日本語Entertainment R2のProduction正式初回経路の確定
   (`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`の既存宿題、本タスクでは
   未着手)。
2. Advanced(Natural English Adaptation)のProduction module化(本タスクでは
   未着手。Standard A2はAdvancedの出力を入力として要求するため、Advancedが
   無いとend-to-end経路が成立しない)。
3. (1)(2)確定後の、Standard A2 runner接続位置・呼び出し順序・Audio path・
   Key Phrase抽出元(Advanced/Standardどちらの本文を使うか)の設計判断。
4. Meta「通話の一部」scope曖昧性の一次情報確認(OPEN-177(7)、本タスクの
   対象外、分離事項として維持)。
5. Production contract(News Writer経路の`### `×2+In One Line構造)への
   適合要否の判断(Standard A2 v5 Promptの単純contractのままでよいか)。

一覧外Read理由: 委任文の事前指定Read一覧に加え、以下を追加で参照した
(いずれも指定Read項目の範囲内での深掘り、または実装に必須だったため):
`er003_v1_en_direct_vfl_01_generate.py`のWRITER_DEVELOPER_MESSAGE定義
(指定Grep `def run_deviation_check|def `の結果から発見、v5 developer
メッセージをそのまま送れない問題を検出するために必須)、
`er006_model_routing_contract_01.py`のPROCESS_MODEL_MAP全体・require_model
実装(指定Read一覧の「Production経路の偵察」延長として、routing.require_
model呼び出しに必要な工程名登録の要否確認のため)、`er012_b_family_
production_runner_01.py`の`_load_pricing`/`compute_cost_jpy_so_far`
(指定Grepパターン`retry|fallback`一致から発見、cost計算ロジック再利用の
ため)、`er003_v1_n3_01_articles_generate.py`のMODEL/REASONING_EFFORT定義
箇所(指定Grep結果、既存Production呼び出し規約の確認のため)。

## §15 最終Status

`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`

Standard A2 v5仕様はユーザー正式採用済み。Productionモジュール
(`er003_v1_n3_01_standard_a2_generate.py`)・単体テスト14件・Sewer/Meta
runtime evidence(実API、合計¥0.8024)は完了したが、Gate 3の14項目中
複数項目(特に1・4・6: Production正式初回経路が存在しないための未接続)が
未充足のため`PRODUCTION_WIRED`とはしない。STOP条件(経路設計に仕様判断が
必要)に該当するため、経路設計自体は実施せずFable/ユーザー判断待ちとして
報告する。

## §16 Fable記入欄

`[Fable記入]`
