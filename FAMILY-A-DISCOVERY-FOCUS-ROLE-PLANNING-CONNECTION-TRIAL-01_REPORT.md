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
