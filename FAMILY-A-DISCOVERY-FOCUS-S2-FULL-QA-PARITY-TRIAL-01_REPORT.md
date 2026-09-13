# FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01_REPORT

管理ID: FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01
性質: Trial(Article-only)。到達: **VALIDATED**(判定語の最終確定はFableに委ねる)。
**Production配線・CURRENT_SPEC正式仕様化・APPROVED_FOR_PRODUCTIONへの変更は
一切行っていない**。Production関数(`er003_v1_n3_01_articles_generate.py`
`run_one_pattern`含む)は無編集(git status上、本Trialの新規ファイル以外に
差分なし)。

## ユーザー確定判断(原文、再確認不要)

> S2を軸に、完全版Trialまで進めてください。(中略)最低限、以下を含めてください。
> Local Rewrite/Point Overlap・Point Value retry/Directional Precheck/Evidence
> Compressionを含むStage 3/retry・fallback・regenerationの整合/Main Story固定時の
> Stage 2-3再実行/Main Story自体に重大問題がある場合のみStage 1からやり直す分岐/
> A2・B1間・複数記事間の角度収束確認/既存News・Trend・Discoveryとの競合確認。
> retry単位については、前回推奨の「通常はStage 1を固定しStage 2-3のみ再実行。
> Main Story自体がLedger MAJOR等で不適格な場合のみStage 1から再生成」を第一候補
> として検証してください。(中略)今回到達してよいStatusは最大VALIDATEDです。

## 1. 実装(新規Trialファイル)

- `er011_discovery_focus_s2_full_trial_01.py`(Trial専用パイプライン、約830行):
  Stage 1(Focus付きMain Story新規生成+Stage 1 QA)→ Stage 2(Point Role Planning、
  前回Trialの`run_stage2_role_planning`をそのままimport再利用)→ Stage 3(Point
  生成、前回Trialの`run_stage3_points_writer`を再利用)→ Evidence Compression
  (Points本文のみへ新規適用)→ 結合 → Point Overlap/Value QA retryループ
  (Stage 2-3単位、Main Story固定)→ 記事全体Fact Checker A'/Ledger Deviation+
  Local Rewrite → Directional Precheck。詳細設計・分岐条件はファイル冒頭
  コメント(約110行)に明文化。
- `er011_discovery_focus_s2_full_trial_01_test_01.py`: LLMモック統合テスト22件
  (全PASS、実費¥0)。Production関数(r3/vfl01/prod_gen/point_planning/
  local_rewrite/dfp/ec_editor)は無変更のままidentity確認(コピー・再実装で
  ないことの機械証明)。

## 2. 実費(5区分、PM_GOVERNANCE 15-5準拠)

1. **今回実測**: **¥84.62**(A2=¥39.15、B1B=¥45.46、上限¥90以内)。全てStandard
   同期(gpt-5.6-luna、Responses API)。openai以外のprovider課金なし。
2. **Trial特有の追加コスト**: ¥0(新規Verified Fact Ledger作成なし、既存
   wake-before-alarm Trial-12のLedger/Topicをread-only再利用。A/B比較用の
   追加runなし、A2/B1B各1本のみ)。
3. **異常retry・Human Review由来の上振れ**: ¥0相当(Point Overlap/Value QA
   retryは0回、Stage 1再生成は0回、いずれも発火せず追加費用なし)。ただし
   A2で最終Ledger Deviation Check後にLocal Rewrite cycleが1回発火した
   (診断+書き換え+diff QA fact checker 1回、既存Production安全装置の
   通常動作の範囲内であり「異常」ではないが、内訳として明記する)。
4. **Standard同期でのコスト(1記事あたり)**: A2=¥39.15、B1B=¥45.46
   (前回Trial[Stage2-3のみ、Main Story再利用]の¥16.51/¥17.43と比べ約2.3〜2.6倍。
   理由: (i)Stage 1 Main Storyを新規生成した分のWriterコストが追加、
   (ii)Fact Checker A'・Ledger Deviation・Directional Precheckを
   Stage 1単体と記事全体の**2回**実行する設計のため)。
5. **Batch量産換算時のコスト**: 該当なし。Writer/QAで使用する`gpt-5.6-luna`は
   `pricing_snapshot.json`上Standard tierのみが定義されており、Batch tier自体が
   存在しない(Batch換算は本Familyの音声[TTS]経路にのみ存在する概念で、
   Writer/QA経路には現状適用されない)。

## 3. 完全版QA結果(実発火/モック証明の区別)

詳細表は`er011_output/discovery_focus_s2_full_trial_01/comparison.md` 2節。要点:

- Stage 1(Main Story単体): Fact Checker A'(A2=REVIEW_REQUIRED[non-blocking]、
  B1B=PASS)、Ledger Deviation(両方LEDGER_COMPLIANT、逸脱0、Local Rewrite未発火)、
  Directional Precheck(両方DIRECTION_REVIEW_REQUIRED[non-blocking、同一Ledgerの
  vfl_internal層由来のためA2/B1Bで同一理由]) — **すべて実発火(実API)**。
- Stage 2-3: Point Role Planning・Point生成とも1回で構造PASS。Evidence
  Compression(Points本文のみへの新規適用範囲)はA2/B1Bとも`applied=true`
  (###見出し2件維持・Title混入なしの安全確認をパスした実データ) — **実発火**。
- Point Overlap QA・Point Value QA: A2/B1Bともflagged=false、**retryは0回
  (未発火)**。retry分岐(Stage 2のみ再計画+Stage 3 diagnostic再生成)は
  `Stage23RetryTests`(3ケース: retry無し成功/1回retryで成功/上限まで
  retryしてもNG)でモック証明。
- 記事全体Fact Checker A': A2/B1Bとも最終的にPASS。
- 記事全体Ledger Deviation+Local Rewrite: **A2で実際にMAJOR 1件を検出し、
  Local Rewrite cycle 1で解決した実例あり**(既存`er010_ledger_local_rewrite_09`
  の`rewrite_ng_item`+`apply_diff_qa_to_resolved_rewrite`を無変更で使用、
  diff QA Fact Checker A' PASS・Ledger再確認LEDGER_COMPLIANTを確認)。この
  MAJORの`locate_target_sentence`によるlocus判定は`main_story`(Stage 1で
  確定した範囲内)だったが、Local Rewriteで解決したためStage 1再生成
  (escalation)には至らなかった。B1Bは記事全体でも逸脱0件、Local Rewrite
  未発火。
- 記事全体Directional Precheck: 両方DIRECTION_REVIEW_REQUIRED(non-blocking)。
- Stage 1再生成分岐(不適格→再生成)・Stage 2-3 exhaustion後のStage 1
  fallback分岐・最終Ledger MAJORのmain_story locus→Stage 1 escalation分岐:
  **いずれも実行では未発火**(0回)。`er011_discovery_focus_s2_full_trial_01_test_01.py`
  の`GenerateArticleStageBranchTests`(happy path/Stage1 blocking→regen成功/
  Stage1 regen上限到達→NG/Stage2-3 exhaustion→Stage1 fallback成功/最終Ledger
  main_story locus→escalation成功/points locus→escalationせずNG、計6ケース)
  でモック証明。

## 4. retry単位の検証結果(ユーザー確定判断の第一候補)

実装した分岐ロジック(コード上明文化、`er011_discovery_focus_s2_full_trial_01.py`
冒頭コメント参照):
- 通常: Point Overlap/Value QA NGはStage 2-3のみ再実行(Main Story固定、
  `POINT_OVERLAP_ARTICLE_RETRY_MAX=2`回まで、既存Production値と同一)。
- 例外(a): 記事全体Ledger Deviation CheckのMAJORが`locate_target_sentence`で
  Main Story側に位置し、Local Rewrite cycle上限(`MAX_REWRITE_CYCLES=3`、
  既存値)を尽くしても解決しない場合→Stage 1再生成。
- 例外(b): Stage 2-3再実行が上限を尽くしてもNGのままの場合→最終フォール
  バックとしてStage 1を1回だけ再生成(**新規Trialしきい値
  `STAGE1_MAX_REGENERATIONS=1`、Production値の流用ではない**、Gate 1判定
  材料として明記)。
- 上記いずれも尽きた場合はNG_REVIEW_REQUIRED(fail-closed、無限ループなし)。

実行結果: A2/B1Bとも上記いずれの再生成分岐も発火せず(Stage 1個別QA・
Stage 2-3 QA・記事全体QAすべて許容範囲内)。したがって**retry単位の設計は
今回、モックテストによる分岐証明のみで検証**されており、実データによる
「実際にMain Story全体を1本作り直した」証拠はまだ無い(次点の検証事項、
7節参照)。ただし、A2で実際に発生したLocal Rewrite(Main Story側locus)が
「Stage 1 escalationの一歩手前で解決した」実例であり、分岐条件自体が
現実のQA結果と接続していることは実データで確認できた。

## 5. 角度多様性(A2・B1間、既存Trialとの比較)

| Trial | Point役割の多様性 |
|---|---|
| 案2(hint注入) | A2/B1とも Point One=睡眠段階、Point Two=学習された期待 に**完全収束** |
| 前回S2(Main Story再利用、Stage1固定) | 4役割すべて異なる(収束なし) |
| **本Trial(S2完全版、Stage1新規生成)** | Point Oneは異なる(A2=概日リズムの同調限界/B1B=睡眠段階)。**Point Twoは同系統(部分収束)**: A2="learned expectation and chronotype"、B1B="trainable sleep habit"(文面・根拠は異なるが、共に習慣・行動差の軸) |

詳細な役割文面・0〜2点の主観採点(引用付き)は`comparison.md` 4節・6節参照
(A2=2点、B1B=2点、いずれも本文引用でMain Storyの言い換えでないことを確認)。
**部分収束の示唆**: Stage 1で生成したMain Story自体がA2/B1Bとも
self-awakening habitのEvidenceに軽く触れており、Point Role PlanningがMain
Story本文を読んだ結果、同じ利用可能なevidenceに収束した可能性がある(Focus
Moduleは角度を指定していないため、hint注入によるものではない)。

## 6. News/Trend/Discovery競合・Dangling Reference確認

`run_one_pattern`は本Trialファイル内で一切import・呼び出しされていない
(grep確認、コメント内言及のみ)。Trend Synthesis・News既定経路は無影響。
本Trialの新規ファイル2件はどこからもimportされていない(Production側から
の依存なし、単方向importのみ)。

## 7. 残る問題・USER_DECISION_REQUIRED相当の未解決事項

1. **retry分岐の実データ検証は未達成**: 3節の通り、Stage 1再生成・
   Stage 2-3 exhaustion fallback・main_story locus escalationはいずれも
   実行で発火しなかった(モック証明のみ)。実データでの検証には、意図的に
   問題を含むLedgerやMain Storyでの追加Trialが必要(追加費用要、
   ユーザー判断)。
2. **STAGE1_MAX_REGENERATIONS=1は新規Trialしきい値**であり、Production値の
   流用ではない。Production化する場合はこの値自体をユーザー承認が必要
   (4節)。
3. **Main Story「完全固定」の前提が、Local Rewrite発火時には成立しない**:
   A2で実際にMain Story本文の1文がLocal Rewriteで書き換わった
   (5節の`main_story_reproduced_exactly=true`はEvidence Compression/結合
   の時点の話であり、その後のLocal Rewriteでは対象外)。「Main Storyは
   Stage 2-3を通じて一切変更しない」という設計原則は、Local Rewrite
   という既存安全装置とは両立しない場面があることを正直に記録する
   (安全性を優先しLocal Rewriteを機能させた結果であり、今回はこれを
   問題視せず許容した)。
4. **Fact Checker FAIL時のlocus分類は簡略化**: Ledger Deviation MAJORは
   `locate_target_sentence`で厳密にlocus判定するが、Fact Checker FAILは
   明確なlocus情報を持たないため、本Trialでは「Stage 2-3 exhaustion後の
   最終フォールバックとしてのみStage 1へ escalate」という簡略ルールを
   採用した(3節参照)。これはFAIL発火が無かったため未検証。
5. **cost_summary.jsonのby_provider_jpy計算に軽微なバグを発見・修正済み**
   (前回Trialから継承していたUSD→JPY変換漏れ、本Trialのコード上で修正
   済み。total_jpyの安全上限判定には影響なし、表示専用の軽微な不具合)。

## 8. SSOT追記文案(編集しない、ユーザー承認後にFableが反映)

- `OPEN_ITEMS.md`への追記候補: 「S2(Focus→Main Story確定→Point Role
  Planning→Point)の完全版QA同等性・retry単位(Stage2-3優先、Main Story
  locus限定でStage1再生成)をTrialで実装・部分検証(実データ:Local
  Rewrite実発火1件、retry分岐はモック証明)。Production化には
  STAGE1_MAX_REGENERATIONS等の新規しきい値のユーザー承認、および
  retry分岐の実データ検証が必要。」

## 9. 成果物

- `er011_discovery_focus_s2_full_trial_01.py`(新規、Trialパイプライン本体)
- `er011_discovery_focus_s2_full_trial_01_test_01.py`(新規、モックテスト22件)
- `er011_output/discovery_focus_s2_full_trial_01/`(新規、A2/B1B実行結果一式、
  `comparison.md`+`index.html`含む)
- 本REPORT、`docs/pm/RESULT_PACKET_S2F.md`
