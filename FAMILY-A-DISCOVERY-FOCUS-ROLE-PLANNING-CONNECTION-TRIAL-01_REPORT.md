# FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01_REPORT

管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
性質: Trial(Article-only)。**Gate 4静的確認でSTOPし、記事生成・API呼び出しは
一切実施していない(実費¥0)**。Production採用・配線の承認ではない
(そもそも実装フェーズへ進んでいない)。

## ユーザー確定判断(原文、再確認不要)

> Discovery: 接続は短いPoint役割hintの案2のみ。案2'は今回試しません。前回の
> 「目覚ましが鳴る直前に起きる理由」のLedgerとFocus単独A2・B1記事を再利用し、
> 接続ありのA2・B1を新規生成して、計4記事を比較してください。Trialの費用
> 上限は300円です。Production経路は変更しないでください。記事全文とPoint
> 計画を並べ、書き分け、Pointの価値・多様性、面白さ、Fact Safety、retryを
> 評価してください。0〜2点の主観評価には本文上の根拠を添え、ユーザーが4記事
> を直接読めるようにしてください。

## 1. Gate 4静的確認の結果: FAIL(意味的変更あり) → STOP

手順1の指示通り、`er003_v1_n3_01_articles_generate.py`をTrial-03実施時点
(commit `d79a9f9a`)からの変更を確認した。

```
git diff --stat d79a9f9a..HEAD -- er003_v1_n3_01_articles_generate.py \
    er011_point_role_value_planning_01.py er006_pool_pilot_01_writer.py
```
→ `er003_v1_n3_01_articles_generate.py`のみ変更(47行、他2ファイルは無変更)。

変更元コミット: `ce39de7b`「PM-CLOSEOUT-CONSOLIDATION-105: OPEN-141差分QA
Production配線+3V Fact Safetyゲート有効化+方式C-v2 Close(ユーザー判断
2026-09-13反映)」(**本タスクと同日**)。

### 検出した3件の差分(`run_one_pattern`本体、および周辺)

1. **Fact Checker prompt (軽微、本Ledgerには非該当)**: `canonical_en_spelling`
   行がLedgerにある場合のみFact Checkerへ照合項目を追加する仕組みが追加。
   Wake-before-alarm Ledger(`er011_output/discovery_generalization_wake_
   before_alarm_trial_12/research/verified_fact_ledger.txt`)を確認したが
   `canonical_en_spelling`行は0件のため、この差分は今回no-op。
2. **Diagnostic Full Retry prompt (自動的に反映される、問題なし)**:
   `build_diagnostic_retry_prompt`が前回Point One/Two実本文を診断promptへ
   渡すよう修正済み(OPEN-112回帰修正)。`run_one_pattern_connected`は
   `prod_gen.build_diagnostic_retry_prompt(...)`を**import経由でそのまま
   呼ぶ**(コピーしていない)ため、この修正は自動的に反映される。問題なし。
3. **新規安全ゲート(重大、コピー側に欠落)**: Local Rewrite Loop内の
   個別文修正呼び出しが、
   - `local_rewrite.rewrite_ng_item(..., use_target_sentence_matching=True)`
     (既定ONへ切替)
   - 直後の`local_rewrite.apply_diff_qa_to_resolved_rewrite(...)`
     (Fact Checker A'再実行+Ledger Deviation Checker再確認、FAIL相当は
     resolvedをFalseへ反転)
   - `overlap_qa.recompute_point_overlap_for_target_sentence(...)`
     (Point Overlap rule-based再計算、記録のみ)
   の3点を新規に含むようになった(OPEN-141、ユーザー正式判断2026-09-13)。
   `er011_point_role_planning_focus_connection_trial_03.py`の
   `run_one_pattern_connected`(Trial-03時点のコピー、406行)は、この3点を
   **一切含んでいない**(該当箇所は旧来の1行呼び出しのまま)。

### なぜ実行不能と判断したか(単なる差分ではなく実害がある根拠)

再利用予定のfocus単独baseline記事(`er011_output/discovery_focus_module_
revalidation_01/a2_focus/`)は、現行Production `run_one_pattern`(コピーで
はなく本物)で生成されており、実際にLedger MAJOR逸脱1件でLocal Rewriteが
1 cycle発火し、この新ゲートを実際に通過している(`run_summary.json`内の
`local_rewrite_results[0].diff_qa.applied=true`
`diff_qa_point_overlap.applicable=true`で確認済み)。

これに対し、新規生成する「focus+接続」記事(A2/B1)は`run_one_pattern_
connected`(コピー)を使う設計のため、**もし同様にLocal Rewriteが発火した
場合、新ゲートを経由せずに合格してしまう**。これは:
- 4記事比較が「Fact Safety」評価軸で不公平になる(baseline側だけ厳格な
  ゲートを通過)。
- 本タスクの遵守事項「既存の安全装置(Gate等)を独自判断で回避・無効化
  しない」に抵触するリスクがある(発火するかどうかは非決定的で、実行前に
  否定できない)。
- 本タスクの制約「接続関数はimportして再利用、コピー・改変しない」があり、
  Sonnet側で`run_one_pattern_connected`へOPEN-141差分QAを追記することは
  (a)Production安全装置の複製を自己判断で行うことになり、(b)接続関数の
  改変禁止に反するため、いずれも独自判断で実施できない。

以上により、手順1の指示「変更があり接続関数が動かない場合はSTOP報告」に
該当すると判断し、**手順2以降(費用見積の確定、driver作成、記事生成)を
実施せずSTOPした**。API呼び出し・記事生成は一切行っていない(実費¥0)。

## 2. 実費

¥0(Gate 4でSTOP、API呼び出しなし)。参考として、直前Trial実測
(focus単独 A2 ¥30.54 / B1 ¥23.81、両方共既存流用のため今回追加費用なし)
のみ既存記録として存在する。

## 3. 選択肢(推奨は付けず、判断材料のみ提示)

- (a) `run_one_pattern_connected`へOPEN-141差分QA相当(3点)を追記した
  更新版コピーを作る。ただし本タスクの「コピー・改変しない」制約に反する
  ため、新規に管理IDを立てて再度Gate 4/実装審査を通す必要がある
  (Sonnet単独では実施しない)。
- (b) 新ゲートが発火しない蓋然性に賭けて、現状の`run_one_pattern_
  connected`のままfocus+接続記事を生成する。ただし比較の公平性と安全性の
  観点から非推奨(発火有無は生成後にしか分からない)。
- (c) Discovery接続Trial自体をPending(保留)にし、まずOPEN-141差分QAを
  反映した接続関数の更新(News Trial-03相当の再検証込み)を先に行う。
- (d) 4記事比較をやめ、focus単独2記事(baseline)のみで「Point Role
  Planning接続なし」の現状を再確認するだけに縮小する(接続効果は評価
  できなくなる)。

## 4. 残る問題

- Discovery向け「focus+接続」runtimeの実証はまだゼロ(News Trial-03の
  Gate1=VALIDATEDのみ、Discoveryへの転用は未検証のまま)。
- 接続関数(Trial-03コピー)は、Production側の継続的な安全機構追加
  (今回のOPEN-141に限らず今後も起こりうる)に対して自動追従しない構造的
  な弱点がある。今後同種のTrialを行う場合、毎回Gate 4静的確認で
  差分の有無だけでなく「安全ゲートの欠落」を明示的に確認する必要がある。

## 5. 比較記事への直接リンク

なし(記事生成を実施していないため、新規4記事比較artifactは存在しない)。
既存参考(今回変更なし、再掲のみ):
`er011_output/discovery_focus_module_revalidation_01/index.html`
(focus単独A2/B1・baseline A2/B1の4記事比較、直前Trialの成果物)。

## 6. Git

本REPORTと`docs/pm/ACTIVE_TASK.md`更新のみ。Production/SSOT/driverコード・
API呼び出しなし。

---

# 追記: Fable修正指示1回目(STOP解除)の結果

上記1〜6節は前回(初回委任)のSTOP記録であり、無変更のまま保全する。以下は
Fable修正指示1回目(選択肢(a)採用: 接続関数を現行Production `run_one_pattern`
[OPEN-141差分QA込み]と同等の新コピーとして作り直し、Trialを実行)の結果。

## 7. Gate 4機械検証(¥0、API呼び出しなし)

新規Trial専用ファイル`er011_point_role_planning_focus_connection_trial_04.py`を
作成した。旧`er011_point_role_planning_focus_connection_trial_03.py`は無改変の
まま保全(News向けGate 1=VALIDATED実績を維持、履歴保全)。

- `run_one_pattern_connected`: `er003_v1_n3_01_articles_generate.run_one_pattern`
  (818-1248行、431行、OPEN-141差分QA込みの現行版)のコピー+改変。
- `run_point_role_planning_connected`/`ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED`:
  `er011_point_role_value_planning_01.run_point_role_planning`のコピー(Trial-03
  から変更なし、同ファイルがTrial-03以降無変更のため)。

**機械証明**: `er011_point_role_planning_focus_connection_trial_04_test_01.py`の
`Gate4SourceReconstructionTests`が、`inspect.getsource(prod_gen.run_one_pattern)`へ
既知の置換規則(下表)を機械的に適用した結果を、`t4.run_one_pattern_connected`の
ソースと文字列比較し、**完全一致することを実行毎に自動確認する**(目視diffでは
なく、再現可能な機械証明)。

| # | 差分項目 | 内容 |
|---|---|---|
| 1 | 関数名 | `run_one_pattern` → `run_one_pattern_connected` |
| 2 | 新規引数 | `point_role_hint_block: str = ""`を追加 |
| 3 | 呼び出し置換(初回・retry計2箇所) | `point_planning.run_point_role_planning(...)` → `run_point_role_planning_connected(..., point_role_hint_block=point_role_hint_block)` |
| 4 | bareヘルパー参照14件の修飾(ロジック不変) | `_writer_process`, `_generate_and_compress_article`, `run_point_overlap_qa_and_regenerate`, `split_common_sections_for_point_qa`, `build_diagnostic_retry_prompt`, `compute_metrics`, `normalize_article_formatting`, `POINT_OVERLAP_ARTICLE_RETRY_MAX`, `POINT_TARGET_LOWER/UPPER`, `POINT_TOLERANCE_LOWER/UPPER`, `TOTAL_SOFT_LOWER/UPPER`, `REASONING_EFFORT`へ`prod_gen.`を付与 |

上記4点以外の差分はゼロ(OPEN-141差分QA[Local Rewrite受理直後のFact Checker
A'再実行+Ledger再確認+Point Overlap再計算]・target-sentence-matching既定ON・
retry上限・print文・出力ファイル名は現行Productionのまま完全に維持)。

**LLMモック統合テスト**(`RunOnePatternConnectedIntegrationTests`、Writer/Fact
Checker/Ledger Deviation/Directional Fact Precheck/Point Overlap QAを決定論的
Fakeへ`mock.patch.object`で差し替え、Point Role PlanningのみFakeClient経由で
実呼び出し): `point_role_hint_block=""`時、Production版`run_one_pattern`と
trial_04版`run_one_pattern_connected`のPoint Role Planning request(model/
reasoning/input全体)と結果dictがbyte一致することを確認。hint指定時は、hintが
Role Planning requestにのみ出現し、Writerへ渡すprompt(role plan込み)はFakeClientが
決定論的な計画JSONを返す限りhint有無で不変であることも確認(6 test全PASS)。

回帰テスト: `run_project_regression.py --pattern "er011_point_role*"`
→ collected=6 passed=6 failed=0。default全件1回
→ collected=2490 passed=2487 failed=3(全て`er003_test_p2j_investigate.py`の
既存自己参照的テスト件数カウント検証、新規テストファイル追加のたびに既知の形で
失敗する既存事象であり本タスクの機能変更とは無関係、過去のOPEN-146等でも同型の
3件失敗が記録されている)。

## 8. Runtime実行結果(実費¥46.47、上限¥300)

新規driver`er011_discovery_focus_role_planning_connection_trial_01_run.py`で、
Gate 4静的確認(git diff再確認+trial_04のhint引数存在確認)PASS後、「focus+接続
(案2 hintのみ、案2'は対象外)」A2/B1を各1本生成した(wake-before-alarm Ledger
再利用、Focus Module Part A有効、現行QA・retry上限無変更)。focus単独(接続なし)
A2/B1は`discovery_focus_module_revalidation_01`の成果物を再利用(再生成なし)。

- A2/Focus+接続: status=OK、fact_verdict=PASS、ledger_status=LEDGER_COMPLIANT
  (MINOR逸脱1件、non-blocking)、Point Overlap flagなし、article retry 0回。
- B1/Focus+接続: status=OK、fact_verdict=PASS、ledger_status=LEDGER_COMPLIANT
  (逸脱0件)、Point Overlap flagなし、article retry 0回。
- 実費: ¥46.47(A2 ¥22.09 + B1 ¥24.38、上限¥300に対し十分な余裕)。

4記事比較artifact(本文全文・role plan JSON・Main Story/Point対応表・0〜2点
主観評価[根拠引用付き])を`er011_output/discovery_focus_role_planning_connection_trial_01/
comparison.md`+`index.html`に作成した。詳細な評価結果(Fact Safety・hintの
反映確認・A2/B1角度収束というリスク観察・面白さ評価)は同ファイル参照。

## 9. 結論・Gate判定

Gate 1判定材料(comparison.md 8節): Fact Safety上は4記事ともOK/LEDGER_COMPLIANT
(A2/接続のMINOR逸脱1件は既存安全装置の範囲内で記録・非ブロッキング)。接続は
Point Role Planningのrole出力にhintの語彙を実際に反映させ、Main Story/Point間の
役割分離を計画通り実装させることを確認した。一方、(i) 接続によりA2・B1の役割選択が
収束し記事間の角度多様性が低下するリスク、(ii) 「Main Storyが解決しない機序」役割の
割り当てが証拠の射程をわずかに超える表現を誘発するリスク、の2点を観察した(いずれも
既存安全装置の範囲内)。**Production採用の判断ではない**(Trial結果の提示のみ)。
サンプルは単一テーマ・各条件1本ずつであり、上記2リスクの一般化可能性は本Trialの
範囲では確定できない(9節「残る問題」参照)。

## 10. Git

本追記・`er011_point_role_planning_focus_connection_trial_04.py`・
`er011_point_role_planning_focus_connection_trial_04_test_01.py`・
`er011_discovery_focus_role_planning_connection_trial_01_run.py`・
`er011_output/discovery_focus_role_planning_connection_trial_01/`(新規出力)・
`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET_DFT.md`を対象にcommit・push。
Production 3ファイル(`er003_v1_n3_01_articles_generate.py`、
`er011_point_role_value_planning_01.py`、`er006_pool_pilot_01_writer.py`)・
旧`trial_03`ファイル・SSOTは無編集。
