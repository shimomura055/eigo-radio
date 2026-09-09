# FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08 報告書

管理ID: FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08(Lane A News再改善、
段階2、A3-UDR-3再改善、Sonnet委任)。**Trial harness内の検証**
(Production/Prompt/共有module/SSOT編集・Git操作は一切行っていない)。並列
稼働中のDiscovery段階2(`er011_output/discovery_stage2_*`)・Lane B 3V
Audio/Household修正(`er012_*`、`er003_output/`)・SSOT統合タスクの成果物・
作業対象は参照・編集していない。`docs/pm/ACTIVE_TASK.md`/
`docs/pm/RESULT_PACKET.md`は編集していない。

---

## 0. Reconciliation再確認(作業1)

`FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md`(c)を再確認:
ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14の原設計は「lexical overlap
flagのみをトリガー」であり、ER-011-NO18導入時の記録には「value QA NGの
理由を既存の診断section直後に追加する」という**加算的設計**が明記されて
いる。Reconciliation判定は「基本構造は仕様どおり」、ただし**value単独NG
時の断定文の事実精度は『不明(未検討)』**。本Trialはこの「不明(未検討)」
部分だけを対象とし、`still_flagged = lexical_flagged or value_qa_flagged`
のOR判定・閾値0.40・Loop Budget 2・Point Role Planningの毎回再計画・
Prompt原則(Storytelling First等)は一切変更していない(下記Gate 4 diffで
機械確認済み、`conclusion=PASS`)。

---

## 1. Part A: N-1 Trial(条件分岐診断)

### 1-1. 方法

Focus Module+hint(Trial-06 focus_hint、現行最良)を固定し、診断構築方式
のみ2水準で比較。
- **current_diagnostic**(無条件構築、現行Production挙動): 新規生成せず、
  既存`er011_output/news_focus_hint_comparison_trial_06/{A2,B1B}/
  focus_hint/run{1,2,3}/`を再利用(同一Hanshin Ledger・同一harness・同一
  focus_hint条件、G1修正済みProduction関数を直呼び、Gate 4 diff確認済み)。
- **branch_diagnostic**(条件分岐、本Trial新規実装): `lexical_flagged`が
  Trueの時だけ`prod_gen.build_diagnostic_retry_prompt()`(overlap断定文+
  shared_words+前回Point本文を含む既存テンプレート)を呼ぶ。Falseの場合
  (value単独NG)はoverlap診断section自体を構築せず`diagnostic_prompt =
  prompt`。`value_qa_flagged`による診断メモ追加は無条件分岐のまま不変。
  新規6本(A2×3, B1B×3)を実生成(スクリプト:
  `er011_news_stage2_diagnostic_branch_trial_08.py`、関数
  `run_one_pattern_diagnostic_branch`)。

Gate 4: `run_one_pattern_diagnostic_branch`と`t3.run_one_pattern_
connected`のunified diffを機械確認(`er011_output/
news_stage2_diagnostic_branch_trial_08/gate4_diff_check.json` =
`conclusion: PASS`)。差分はコメント/docstring削除、診断section構築部分
の条件分岐、監査ログ追加(`audit/diagnostic_prompt_retry{N}.txt`保存)、
`t3.`修飾の4種のみで、`still_flagged`のOR判定・Loop Budget参照・Point
Role Planning二重呼び出しは不変であることを確認済み。

**runtime動作確認**(a2/run1): attempt0でlexical_flagged=True →
`diagnostic_prompt_retry1.txt`に断定文含む(grep一致1件)。attempt1で
lexical_flagged=False, value_qa_flagged=True(value単独NG) →
`diagnostic_prompt_retry2.txt`には断定文が**含まれない**(grep一致0件)、
Value QA診断メモのみ含まれる(grep一致1件)。設計どおりの分岐が実際に
動作したことをファイルで直接確認。

### 1-2. 結果表(N=6/条件)

| 指標 | current_diagnostic | branch_diagnostic |
|---|---|---|
| NG率 | 3/6 (50.0%) | 5/6 (83.3%) |
| 平均attempt数 | 1.50 | 1.83 |
| P1 overlap平均 | 0.390 | 0.302 |
| P2 overlap平均 | 0.287 | 0.383 |
| value単独NG発生数 | 1 | 5 |
| value単独NG→次attempt新規lexical flag率 | 1/1 (100%) | 5/5 (100%) |
| Fact Checker FAIL件数 | 0 | 1(a2 run3、既存blocking gateが正常動作、ロジック変更なし) |
| Ledger Deviation平均 | 0 | 0(OK到達run1本のみ) |

出典: `er011_output/news_stage2_diagnostic_branch_trial_08/parta/`
(analysis.json / point_overlap_article_retry_log.json 各run)、
`er011_output/news_focus_hint_comparison_trial_06/{A2,B1B}/focus_hint/`。

### 1-3. 判定

「value単独NG→次attemptで新規lexical flag」という連鎖は、条件分岐後も
**5/5(100%)で解消しなかった**(current_diagnosticの1/1=100%と同水準、
改善なし)。さらにNG率(50%→83.3%)・平均attempt数(1.50→1.83)は悪化方向、
新規にFact Checker FAILが1件発生(既存blocking gateが正常に機能した結果
であり新failure modeではないが、副作用として記録)。N=6/条件と小標本
(段階1報告書の全Trial合計N=9より更に少ない)のため統計的な確定はできない
が、**改善方向の兆候は一切観測されず、全指標が悪化方向で一致**しており、
偶然のノイズだけでは説明しにくいパターン。

**Gate 1分類: REJECTED**(連鎖率の低下なし、かつ副作用[NG率悪化・
attempt数増加]あり。VALIDATEDの条件[連鎖減少かつ副作用なし]を満たさない。
ただしN=6は小標本のため「効果なしと断定」ではなく「本Trialの証拠では
効果を支持できない」という限定的な結論)。

**解釈の仮説(未検証)**: overlap診断section除去により、Writerが「前回の
Point本文を読んで何を避けるべきか」という具体的な反面教師を失い、
Value QA診断メモ(理由は述べるが前回本文の引用がない)だけでは十分な
ガイドにならず、結果として空いた自由度でむしろ新規lexical overlapを
誘発した可能性がある。これは仮説であり本Trialのスコープでは追加検証
していない。

**Production修正案(実装しない、UDR)**: `build_diagnostic_retry_prompt()`
呼び出し部分への`lexical_flagged`条件分岐(変更箇所は本Trialの
`run_one_pattern_diagnostic_branch`と同一パターン、`er003_v1_n3_01_
articles_generate.py`の該当呼び出し1箇所)。**本Trialの結果は当該変更を
支持しない**(現状のまま維持を推奨、ただしN=6小標本のため最終判断は
ユーザー)。回帰テスト案: 本Trialと同型のA/B(N=6以上)を既存Focus/hint
以外の条件でも再現するかの追試が必要。既定挙動の変更自体はUDR(Production
採用は人間ユーザーのみ)。

---

## 2. Part B: N-2 分析(¥0、既存240件のoverlap分布)

出典: `er011_point_quality_stage1_recomputation_01.RUNS`(Trial-04/05/06/07
全50 run・240 Point観測、既存JSON読み取りのみ、新規API呼び出しなし)を
再利用。集計script:
`er011_news_stage2_diagnostic_branch_trial_08_partb_denominator_
threshold_01.py`。結果:
`er011_output/news_stage2_diagnostic_branch_trial_08/partb/
partb_results.json`。

### 2-1. 閾値0.40の分布上の位置

- 閾値0.40は観測分布の**57.92パーセンタイル**(中央よりわずかに上、
  Opus「分布の中央付近」との評価と整合)。平均0.378、中央値0.375、
  Q1/Q2/Q3 = 0.297/0.375/0.454。
- 境界帯(±0.037=1語分、[0.363, 0.437])内の観測: **60/240件(25.0%)**。
  4件に1件が「あと1語shared word数が変われば判定が反転する」僅差観測。

### 2-2. 分母の語数正規化案(数式提示、採用しない)

`ratio_norm = shared_word_count / D_fixed`(D_fixed=30、観測分布の中央値
point_word_count、stage1(a)と同一値)。現行`ratio = shared_word_count /
point_word_count`から、固定分母への変更を閾値0.40据え置きで試算:
- 現行flag率(Point観測単位): 105/240 (43.75%) → 固定分母30なら
  118/240 (49.17%)(+5.4pt)。
- attempt単位のlexical flag相当率(粗い試算、still_flaggedのOR判定は
  再現せず孤立試算): 65.0% → 70.83%(+5.8pt)。
- 新たにflagされる観測29件(平均36.97語、元々長いPoint)、flag解除される
  観測16件(平均23.06語、元々短いPoint)。**分母正規化は短いPointに有利
  ・長いPointに不利な方向へ判定を動かす**(現行方式とは逆方向の交絡)。

### 2-3. Focus系改善の境界効果依存度

| 条件 | flag率低下(pt) | treatment非flag中の境界隣接割合 |
|---|---|---|
| trial_06:focus_hint | 17.22 | 12.5%(2/16) |
| trial_06:hint_only | 23.89 | 16.67%(1/6) |
| trial_04:focus | 10.00 | 27.78%(5/18) |
| trial_05:gapfix | -22.50(悪化) | 23.53%(4/17) |
| trial_07:discovery_focus | 1.36 | 10.53%(2/19) |

Focus/hint系の改善は境界隣接観測が10〜28%に留まり、**改善の大部分は
境界効果(僅差の閾値越え)だけでは説明できない**(閾値のはるか下まで
overlapが下がっている観測が主体)。trial_04:focusのみ境界依存度がやや
高い(27.78%)。

### 2-4. 結論(判断材料、採用はUDR)

- 閾値0.40は分布中央付近に位置し、境界帯(±1語)に全観測の1/4が集中する
  ため、**個別観測レベルでは1語の増減で判定が反転しやすい「際どい」
  閾値**である。ただしFocus系施策の平均的な改善効果自体は境界効果への
  依存度が低く(10〜28%)、施策効果の実質性(段階1(a)の判定)とは矛盾しない。
- 分母を固定語数化すると、現行より**やや厳しい方向**(flag率+5〜6pt)に
  動き、長いPointが新たに不利になる(短いPointが有利になる)という**現行
  とは逆方向の交絡**が生じる。現行の「長いPointほど分母が大きく相対的に
  flagされにくい」という設計上の性質は、stage1(a)の実測(長いPointほど
  ratioがわずかに低い、Pearson -0.19)と整合しており、固定分母化が
  「より公平」になる保証はない(単に交絡の方向が変わるだけ)。
- **数値上、閾値・分母の変更を積極的に支持する根拠は弱い**(境界帯が
  1/4存在する点は再校正の検討材料だが、Focus系改善の実質性は境界効果に
  大きく依存していないため、緊急の再校正の必要性は低いと考えられる)。
  最終判断・採用はユーザー(UDR、A-UDR-7・OPEN-134整合確認要)。

---

## 3. 費用・成果物

- **Part A実測費用**: ¥42.5(branch_diagnostic新規6本のみ課金、
  current_diagnostic 6本は既存Trial-06成果物を再利用のため追加課金なし)。
  上限¥120以内。`er005_cost_logger`(`cl.install()`)で全呼び出しを実測。
- **Part B**: ¥0(既存JSON読み取りのみ)。
- **新規ファイル**:
  - `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08_REPORT.md`(本ファイル、
    root)
  - `er011_news_stage2_diagnostic_branch_trial_08.py`(Part A trial
    harness、root)
  - `er011_news_stage2_diagnostic_branch_trial_08_partb_denominator_
    threshold_01.py`(Part B分析script、root)
  - `er011_output/news_stage2_diagnostic_branch_trial_08/`
    (gate4_diff_check.json、gate4_diff_from_t3.txt、run_metadata.json、
    cost_summary.json、raw_usage_log.jsonl、
    parta/{a2,b1b}/branch_diagnostic/run{1,2,3}/*、
    partb/partb_results.json)
- **Production/Prompt/共有module/SSOT**: 無変更(編集していない)。
- **Git操作**: なし(本タスクの禁止事項どおり)。

## 4. STOP条件該当の有無

該当なし(条件分岐に判定ロジック変更は不要だった、新failure modeなし
[Fact FAIL 1件は既存blocking gateの正常動作]、費用超過なし、Production・
共有module変更は行っていない)。ただしPart Aの結果自体は**現状維持を
支持する**内容であり、Production採用は行わない(そもそも当初からUDR)。
