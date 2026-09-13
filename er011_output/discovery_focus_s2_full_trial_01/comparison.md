# comparison.md — FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01

対象: `er011_discovery_focus_s2_full_trial_01.py` 実行結果(A2/B1B、各1本、実API実行)。
Ledger/Topic: `er011_output/discovery_generalization_wake_before_alarm_trial_12/research/`
(read-only再利用)。Stage 1(Main Story)は本Trialで新規生成(前回trialの既存Main Story
再利用とは異なる)。

## 1. 実費(実測)

| 項目 | A2 | B1B | 合計 |
|---|---|---|---|
| 実測費用(円) | 概算内訳はraw_usage_log.jsonl参照 | 同左 | **84.62円**(上限90円) |

`cost_summary.json`: total_jpy=84.62, by_provider_jpy={"openai": 84.62}。retry不発火のため、
見積(¥60〜90)の上限付近で収まった(Stage 1新規生成+Stage 1/最終の二重QAにより、前回
Stage2-3のみのTrial[¥33.94]より高い)。

## 2. Stage別QA結果(実発火/モック証明の区別)

| Stage/QA | A2(実測) | B1B(実測) | 実発火 or モック証明 |
|---|---|---|---|
| Stage 1 Writer(Focus付きMain Story) | 1回で構造OK | 1回で構造OK | 実発火(実API) |
| Stage 1 Fact Checker A' | REVIEW_REQUIRED(non-blocking、advisory) | PASS | 実発火 |
| Stage 1 Ledger Deviation | LEDGER_COMPLIANT(逸脱0) | LEDGER_COMPLIANT(逸脱0) | 実発火(Local Rewriteは未発火、MAJOR無し) |
| Stage 1 Directional Precheck | DIRECTION_REVIEW_REQUIRED(non-blocking) | DIRECTION_REVIEW_REQUIRED(non-blocking) | 実発火 |
| Stage 2 Point Role Planning | 1回(replan無し) | 1回(replan無し) | 実発火 |
| Stage 3 Point生成 | 1回で構造OK | 1回で構造OK | 実発火 |
| Evidence Compression(Points対象) | applied=true | applied=true | 実発火(新規適用範囲、###見出し2件維持を確認) |
| Point Overlap QA | flagged=false(retry不要) | flagged=false(retry不要) | 実発火。**retryは未発火**→分岐はモック統合テストで証明(`Stage23RetryTests.test_success_after_one_retry`/`test_exhausts_retries_still_ng`) |
| Point Value QA | PASS | PASS | 実発火。retry未発火は上記と同じテストで証明 |
| 最終Fact Checker A'(記事全体) | PASS | PASS | 実発火 |
| 最終Ledger Deviation+Local Rewrite | **MAJOR 1件検出→cycle 1で解決**(locus=main_story、diff QA PASS) | LEDGER_COMPLIANT(逸脱0、cycle無し) | **A2で実発火**(Local Rewrite本体・diff QA・locus分類の全てが実データで動作したことを確認) |
| Stage 1再生成分岐(不適格→再生成) | 未発火(0回) | 未発火(0回) | モック証明(`GenerateArticleStageBranchTests.test_stage1_blocking_then_regen_succeeds`/`test_stage1_blocking_exhausted_returns_ng`) |
| Stage 2-3 exhaustion→Stage1 fallback分岐 | 未発火 | 未発火 | モック証明(`test_stage23_exhaustion_falls_back_to_stage1_and_succeeds`) |
| 最終Ledger MAJORのmain_story locus→Stage1 escalation分岐 | **locus="main_story"は実際に観測されたが、Local Rewrite cycle 1で解決したためStage1 escalationは不要だった(未発火)** | 該当なし | モック証明(`test_final_ledger_main_story_locus_escalates_and_succeeds`/`test_final_ledger_points_locus_does_not_escalate_stays_ng`) |
| 最終Directional Precheck | DIRECTION_REVIEW_REQUIRED(non-blocking、Ledger内部のvfl_internal層由来、A2/B1Bとも同一Ledgerのため同一結果) | DIRECTION_REVIEW_REQUIRED(non-blocking) | 実発火 |

**重要な実データ(A2)**: 最終Ledger Deviation Checkが記事全体に対して実行された際、
Stage 1で既に個別にPASSしていたMain Story文中の1文
("However, the researchers did not find clear evidence of a sudden change in the
rate of rise during the hour before waking.")が新たにMAJORとして検出された
(比較対象が「覚醒前後の比較」から「覚醒前1時間内の変化」へ変わっていた、という
意味変化)。`locate_target_sentence`によるlocus判定は`main_story`(Stage 1で確定した
範囲内)。既存Local Rewrite機構(`er010_ledger_local_rewrite_09.rewrite_ng_item`+
`apply_diff_qa_to_resolved_rewrite`、無変更)がcycle 1で解決し
("However, the researchers did not find clear evidence that the rate of rise
differed between the hour before waking and the hour after waking."へ書き換え、
diff QA Fact Checker A' PASS・Ledger再確認LEDGER_COMPLIANT)、Stage 1
escalationには至らなかった。これは「Main Story固定後も、Points追加後の文脈で
新たなMAJORが見つかりうる」という設計上の懸念が実データで確認された一方、
Local Rewriteという既存の安全装置がその懸念に対して有効に機能した実例である。

## 3. retry単位の検証結果

ユーザー確定判断の第一候補(「通常はStage 1を固定しStage 2-3のみ再実行、Main Story
自体が不適格な場合のみStage 1から再生成」)を実装し、分岐条件を以下のように明文化した:

- (a) 最終Ledger Deviation CheckでMAJORのclaim_in_articleがMain Story側に位置し、
  Local Rewrite cycle上限(3、既存値)を尽くしても解決しない場合→Stage 1再生成。
- (b) Stage 2-3再実行がPOINT_OVERLAP_ARTICLE_RETRY_MAX(2、既存値)回を尽くしても
  Overlap/Value QAまたはFact CheckerがNG/FAILのままの場合→最終フォールバックとして
  Stage 1を1回だけ再生成(新規Trialしきい値`STAGE1_MAX_REGENERATIONS=1`)。

実行結果: A2/B1Bとも、Stage 2-3のretryは1回も発火せず(Point Overlap/Value QAは
初回で共にPASS)、Stage 1再生成も1回も発火しなかった(Stage 1自体は初回生成で
Fact Checker/Ledger/Directionalすべて許容範囲だった)。したがって、上記(a)(b)の
分岐ロジックは実行では検証されず、`er011_discovery_focus_s2_full_trial_01_test_01.py`
のLLMモック統合テスト(22件全PASS)で分岐の正しさを機械的に証明した(詳細は
本ファイル冒頭のテスト一覧、およびREPORT参照)。

## 4. 角度多様性(Main Story/Point対応表)

| | A2 Point One | A2 Point Two | B1B Point One | B1B Point Two |
|---|---|---|---|---|
| 見出し | A Clock with Limits | Timing Can Become a Habit | Why the Same Alarm Feels Different | A Habit Some People Develop |
| Role Planning `role`(抜粋) | "circadian entrainment is a bounded alignment process, not a precision time-reading system" | "recurring self-awakening may involve learned expectation and chronotype" | "sleep stage at that moment affects how easily awakening breaks through" | "reframe the experience as an individual and potentially trainable sleep habit" |
| 系統 | 生理メカニズムの限界 | 行動・個人差(習慣) | 睡眠段階(生理メカニズム、A2 P1とは別軸) | 行動・個人差(習慣、A2 P2と同系統) |

**評価**: A2 Point One(概日リズムの同調限界)とB1B Point One(睡眠段階による
覚醒しやすさ)は明確に異なる軸。一方、A2 Point Two・B1B Point Twoは共に
「学習された習慣・練習による強化」という同系統のテーマを扱っており、
前回S2 Trial(4役割すべてが異なっていた)と比べると**部分的な収束が見られる**
(ただし文面・具体的根拠[chronotype vs practice/morningness]は異なり、
案2で観察された「A2・B1が完全に同一の役割ペアに収束する」という重い収束
ではない)。原因の一つとして、Stage 1で生成したMain Story自体がA2/B1Bとも
「習慣化(self-awakening habit)」のEvidenceを本文内で既に短く触れており、
Point Role PlanningがMain Story本文を読んだ結果、同じ available な
"habit"関連evidenceに収束しやすかった可能性がある(Focus Module Part Aは
角度を指定していないため、hint注入によるものではない)。

過去Trialとの比較:
| Trial | Point役割の多様性 |
|---|---|
| 案2(hint注入、Trial-04系) | A2/B1とも Point One=睡眠段階、Point Two=学習された期待 に**完全収束** |
| 前回S2(Main Story再利用、Stage1固定) | 4役割すべて異なる(収束なし) |
| 本Trial(S2完全版、Stage1新規生成) | Point Oneは異なる、**Point Twoのみ同系統(部分収束)** |

## 5. Main Story固定性の確認

`main_story_reproduced_exactly=true`(A2/B1Bとも、Stage 2-3のEvidence Compression・
結合を経てもMain Story本文が最終的に完全一致)。ただしA2は最終Ledger Deviation
Checkの後にLocal Rewriteが1文だけ書き換えており、**この時点でMain Storyは
「完全固定」ではなくなっている**(Local Rewriteは安全装置として正しく機能したが、
「Main Storyは一切変更しない」という前提が、Local Rewrite発火時には破られる
という設計上の事実を正直に記録する)。

## 6. 主観採点(0〜2、引用必須)

- **A2: 2点**。理由: Main Storyの主張(「体内時計はストップウォッチではない」)を
  受けて、Point One "In a time-isolation experiment, very dim light plus a fixed
  sleep–wake schedule usually synchronized healthy adults to a 24-hour day. But the
  same system generally failed to adjust to imposed 23.5- or 24.6-hour days." は
  Main Storyの主張を具体的なEvidenceで補強しており言い換えになっていない。
  Point Two "A university survey found that about 10% of students reported a
  self-awakening habit." も新しい axis(習慣)を提示できている。
- **B1B: 2点**。理由: Point One "If an alarm—or a natural awakening—catches deep
  N3 sleep, waking may be harder and groggier." はMain Storyが triggeredしていない
  「睡眠段階」という新しい説明軸を追加できており、単なる要約ではない。

## 7. News/Trend/Discovery競合確認(静的確認)

`run_one_pattern`(Production、mode非依存の共通関数)は本Trialで一切importされて
いない(`er011_discovery_focus_s2_full_trial_01.py`内でのgrep結果、import文に
`run_one_pattern`なし)。Trend Synthesis(`editorial_mode="trend_synthesis"`)・
News既定経路は無変更・無影響。
