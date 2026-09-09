# FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01 報告書

管理ID: FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01(Lane A、News/Discovery再改善の段階1、Sonnet委任)。Opus設計レビュー(`FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01_REPORT.md`参照、本タスクの作業1でFableの要旨を転記済み)を受けた事後再集計+読み取り専用検証。Production/Prompt/SSOT編集・Trial生成・Git操作は行っていない((e)のみFable許可により極小LLM呼び出し実施、実測¥3.34)。並列稼働中のLane B 3V Trial-03(`er012_*`)・SSOT統合タスクの成果物・作業対象は参照・編集していない。`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`は編集していない。

---

## 2. 段階1 再集計(作業2、(a)〜(g))

**方法**: 全て¥0の読み取り専用再集計(API呼び出しなし)。ただし(e)のみ
Fable許可により極小LLM呼び出し(N=10、Household Ledger/topic、Focus
Module無し、Writer呼び出し無し)を実施(実測¥3.34、上限¥15以内)。
対象: Trial-06(14 run)・Trial-04(12 run)・Trial-05(12 run)・Trial-07
(12 run)、計50 run(Haiku L0集計`er011_output/point_quality_retry_log_
aggregation_l0_01/`と同一母集団、件数を突合し一致を確認済み)。
再集計script: `er011_point_quality_stage1_recomputation_01.py`
(結果: `er011_output/point_quality_stage1_recomputation_01/
stage1_recomputation_results.json`)。

### 定義固定(Haiku L0集計との差異を明示)

- **「NG」**: `analysis.json`の`status`が`NG_REVIEW_REQUIRED`または`FAIL`系
  (=最終確定status)。Fact Checker verdict(`fact_verdict`)は別列として
  独立集計する(混同しない)。Haiku L0集計は`status`フィールドを読まず、
  retry_logの最終attemptの`lexical_flagged`/`value_qa_flagged`から
  `final_status`("OK"/"NG")を**独自に推測**していた(`extract_analysis_
  status()`はstatus取得を試みるが、集計本体の`final_status_str`計算は
  attempt由来)。本タスクは`analysis.json.status`を直接採用する点が異なる
  (今回の50 run全件で両者の値は一致することを確認済み、乖離なし)。
- **「入れ替わり(true swap)」**: attempt n→n+1で(lexical_flagged,
  value_qa_flagged)が`(True,False)→(False,True)`または`(False,True)→
  (True,False)`に変化した回数のみ。Haiku L0集計の`transitions`フィールド
  は「curr != next」という**any-change**定義(例: `(True,True)→(True,
  False)`のような片方のみ変化する非swapケースも含む)であり、本タスクの
  narrow定義とは異なる。両方を算出し併記した。

### (a) Point異なり内容語数 vs overlap_ratio

`er008_point_overlap_qa_18.py:44-58`(`lexical_overlap_ratio()`)を確認:
`point_words = _content_words(point_text)`は`set`(重複除去、stopword除去
後)であり、`point_word_count = len(point_words)`は「Point内の異なり内容
語数」そのもの。`overlap_ratio = len(shared) / len(point_words)`。

- 全240件のPoint観測(50 run×最大3 attempt×2 Point):
  word count範囲20〜47語(中央値30語)、overlap_ratio範囲0.115〜0.688。
- Pearson相関(word count vs ratio) = **-0.192**(弱い負の相関。長い
  PointほどわずかにOverlap比率が低い傾向で、Opusの懸念「長いPointほど
  overlap比率が高く出て不利」という交絡方向とは**逆符号**)。
- 1語あたりratio変化(全観測の1/word_countの平均) = **0.0333**
  (Opus引用値「1語≈0.037」と近似的に一致、Opus引用のword count範囲
  26〜36語に限定すると1/wc平均は0.030〜0.038でOpus値とほぼ一致)。
- 条件間比較(baseline vs 施策条件、5語binでword count層別一致):
  - Trial-06 focus_hint: 生値diff -0.043→層別後diff **-0.043**(不変、
    交絡なし、施策側優位は実質)。
  - Trial-06 hint_only: 生値diff -0.059→層別後 **-0.059**(不変)。
  - Trial-04 focus: 生値diff -0.042→層別後 **-0.042**(不変)。
  - Trial-05 gapfix: 生値diff **+0.040**(施策側が悪化)→層別後diff
    **+0.014**(交絡により生値の約2/3が説明された。gapfix条件のPointは
    平均32.6語、baseline平均36.7語と有意に短く、word count差が生値diffの
    主因の一部であることを直接確認)。
  - Trial-07 discovery_focus: 生値diff -0.004→層別後 **-0.011**(ほぼ
    ゼロ、施策効果は元々わずか)。
  - **判定**: Trial-06/04のFocus/hint系施策の優位性はword count交絡では
    説明されない(層別後も残る)。Trial-05のgapfix「悪化」の大部分は
    word count交絡で説明される(Opusの交絡懸念はTrial-05に関しては
    支持される)。

### (b) 全attemptのlexical/value flag遷移表

全4 Trial・全条件、120 attempt(50 runの全attempt合計)を再集計:
- lexical_flagged=True: 78/120(65.0%)
- value_qa_flagged=True: 58/120(48.3%)
- **Trial-06 baseline**(Opus引用対象): 18 attempt中lexical_flagged=True
  **17件**(94.4%)。**Opus引用「17/18」を完全再現・確認**。
- **真の入れ替わり(narrow定義)**: Trial-06内のみで**4件**(Opus引用
  「真の入れ替わりは4件」を完全再現・確認)。全4 Trial合計では**7件**
  (Trial-04で1件、Trial-05で2件が追加)。
- any-change定義(Haiku L0相当)での遷移数: 全50 runで**50件**
  (true swap 7件の約7倍。ほとんどの「変化」はswapではなく片方の軸のみの
  変化であり、Haiku L0集計の`transitions`フィールドをそのまま「もぐら
  たたき」の証拠として使うと過大評価になる)。

### (c) value単独NG起因retryの後続attempt結果

全4 Trial横断でvalue単独NG(lexical=False, value_qa=True)ケースを再抽出:
**全9件**(Trial-06内は2件のみ)。
- **Trial-06内の2件**: 次attemptで新規lexical flag発生2/2件。
  **Opus引用「2/2」を完全再現・確認**(Trial-06限定では正確)。
- **全4 Trial合計9件**では、次attemptで新規lexical flag発生は**4/9件
  (44.4%)**。Opusの2/2(100%)という数値はTrial-06限定の少数サンプルでは
  正確だが、他Trialへ一般化すると再現率は約44%まで下がる(母集団拡大で
  弱まる)。

**コード確認(誤診断メカニズム)**:
- `er003_v1_n3_01_articles_generate.py:915`付近の`build_diagnostic_
  retry_prompt()`(611-635行)は、`lexical_flagged`の値を一切参照せず
  `diagnostic_mod.build_diagnostic_section()`を**常に無条件に呼び出す**。
- `er009_diagnostic_full_retry_modules_12.py:60-65`の
  `DIAGNOSTIC_SECTION_TEMPLATE`冒頭文("It failed an automatic
  Point-overlap check: Point One and/or Point Two repeated meaning that
  was already in the Full Story...")は、`point_one_flagged`/
  `point_two_flagged`が両方Falseの場合(=value単独NGでlexicalは実際には
  flagされていない場合)でも**無条件に出力される断定文**であり、事実と
  異なる主張をWriterへ提示しうる。
- `run_one_pattern()`(883-919行)では`still_flagged = lexical_flagged or
  value_qa_flagged`のOR判定でretryへ入るが、diagnostic prompt構築自体は
  この分岐を経由しない(921-937行)。

**設計意図のReconciliation**: `ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-
14`の原設計は「lexical overlap flagのみをトリガー」としていた
(value QAは未存在)。その後`ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01`が
value QAを追加した際の記録(DECISION_LOG.md該当エントリ)には「上記3つを
`still_flagged = lexical_flagged or value_qa_flagged`として既存の
Diagnostic Full Retryループへ統合し、retry時はvalue QA NGの理由を**既存の
診断section直後に追加する**」と明記されている。すなわち設計意図は
「overlap診断sectionは基盤として維持し、value QA理由を追加する」という
**加算的設計**であり、コードの挙動(overlap診断section無条件構築+value
QA診断メモ条件付き追加)と一致する。**Reconciliation判定: 基本構造は
「仕様どおり」**(実装漏れではない)。ただし、value単独NG(lexical
flagged=Falseが2点とも)の場合に**テンプレート冒頭の断定文が事実と異なる
内容をWriterへ提示する**という具体的な文言精度の問題は、`ER-011-NO18`の
設計記録に明示的な検討の痕跡がない。**この文言精度の問題自体は「不明
(未検討)」**と判定する(実装漏れとも仕様どおりとも言い切れない)。

### (d) cross_point_overlap既存値

全240 Point観測(Point One対Point Two、双方向、`report.point_one_vs_
point_two`/`point_two_vs_point_one`)を再集計:
- 全体平均0.1311、中央値0.1265、標準偏差0.0653、範囲0.0〜0.346。
- 現行lexical overlap閾値0.40を適用した場合の該当件数: **0件(0.0%)**
  (全観測が閾値未満)。
- 条件別: Trial-07 discovery_focus平均0.134 > baseline平均0.094(discovery_
  focus側でPoint同士がわずかに近い、方向性としてはRole収束の主張と
  整合的だが差は小さい)。Trial-05 gapfix平均0.143 > baseline平均0.109。
  Trial-06/04では施策条件で微増または横ばい。
- **判定**: 全観測が既存閾値未満のため既存gateとしては機能しないが、
  連続指標としては条件間で緩やかな差(0.03〜0.05程度)があり、Point間
  分化度の補助指標として使える可能性がある(閾値運用ではなく分布比較
  用途)。

### (e) Trial-07 role分布の再現性(N=10、実測¥3.34)

**コード確認**: `run_point_role_planning(client, topic, verified_ledger_
text, model, reasoning_effort)`(`er011_point_role_value_planning_01.py:
124-145`)はtopic/verified_ledger_textのみを引数に取り、`article_text`
も`editorial_type_module_block`も一切受け取らない。Trial-07の`run_one_
pattern()`呼び出し(baseline/discovery_focus両条件)も同一の2引数のみを
渡しており、**Focus ModuleがRole Planningへ到達する経路はコード上
存在しない**(Opus指摘を確認)。

**新規サンプリング**: Household Ledger/topic(Trial-07と同一Source of
Truth、`prod_gen.THEMES`から直接取得)で`run_point_role_planning()`のみを
N=10回追加抽選(Writer呼び出しなし、model=gpt-5.6-luna、reasoning_
effort=high)。実測費用**¥3.34**(上限¥15以内)。役割分類はTrial-07と
同一のキーワード分類器(`er011_discovery_layer3_focus_trial_07.
classify_role_text()`)をそのまま再利用(改変なし)。

- 新規N=10(20 Point)の分布: mechanism 3、myth_correction 4、broader_
  dimension **8**、other **5**、certainty_limitation 0。
- Trial-07 baseline実績(N=6 run、12 Point、同一入力): mechanism 4、
  myth_correction 3、broader_dimension 4、other 1。
- Trial-07 discovery_focus実績(N=6 run、12 Point): myth_correction 6、
  mechanism 6、broader_dimension **0**、other **0**。
- 新規サンプルとbaseline実績を合算(N=16 run、32 Point、「Focus Module
  なし」相当の同一分布からの抽選とみなせる): mechanism 7、myth_
  correction 7、broader_dimension 12、other 6。**broader_dimension+other
  だけで18/32(56%)**。さらに、新規10 runのうち**10/10 run全てが
  broader_dimensionまたはotherを最低1件含む**。
- **判定**: Role PlanningはFocus Moduleの入力を一切受け取らないため
  (コード確認済み)、baseline/discovery_focusのRole Planning初回呼び出し
  は理論上**完全に同一の入力分布からの抽選**のはずである。しかし
  discovery_focus実績6 runでbroader_dimension/otherが0/12件だったのに
  対し、同一入力から新たに抽選した16 run(32 Point)ではbroader_
  dimension/otherが56%の頻度で出現し、全run(10/10)が最低1件を含んだ。
  これは「discovery_focus実績のRole収束(mechanism/myth_correctionのみ)
  が、Focus Module以外の原因では説明しにくい」という意味で、Opus指摘
  「Focus ModuleにはRole Planningへの因果経路が無い」を**コード面では
  完全に支持**しつつ、**実績データの収束自体は依然として未解明の異常
  (単なる小標本[N=6]の偶然か、当時のモデル応答分布の何らかの一時的
  偏りか、他の未特定要因かは本タスクの範囲では特定できない)として残る**。
  この異常の原因特定は段階1のスコープ外であり「不明」と判定する
  (段階2または追加Trialの検討対象候補)。

### (f) G1語彙プライミング仮説の予備確認(¥0)

- Trial-04(a2/b1b とも Trial-06と**同一のマスター記事**であることを
  `audit/prompt.txt`の先頭一致で確認済み、topic交絡は無い)とTrial-06の
  baseline P1/P2 ratio(全attempt込み):
  - P1: Trial-04 0.4273(n=16, 平均wc=26.7) → Trial-06 0.4151(n=18,
    平均wc=27.8)(**ほぼ横ばい、わずかに低下**)
  - P2: Trial-04 0.3869(n=16, 平均wc=31.6) → Trial-06 0.4207(n=18,
    平均wc=28.6)(**+0.034の上昇**、Opus引用「0.339→0.458」より小さい
    差だが同方向)
- attempt番号別に層別(G1はretry診断prompt[attempt≥1]のみに影響し、
  attempt=0はG1の影響を受けられない設計であることを`er009_diagnostic_
  full_retry_modules_12.py`のコードで確認済み):
  - attempt=0(G1の影響を受け得ない): Trial-04 P2=0.383(n=6) →
    Trial-06 P2=0.463(n=6)、**既にattempt=0時点で+0.079の差が存在**。
  - attempt=1: Trial-04 0.442 → Trial-06 0.341(**逆符号、-0.101**)。
  - attempt=2: Trial-04 0.336 → Trial-06 0.458(+0.122)。
- **判定**: attempt=0(G1が構造上影響し得ない初回生成)で既に有意な差が
  観測され、attempt=1では符号が反転する非単調なパターンであるため、
  「G1のretry診断prompt改善が語彙プライミングとして働いた」という
  Opusの仮説メカニズムは**この¥0再集計では確認できない**(支持されない)。
  マスター記事・Ledgerは同一であることを確認済みのため、観測された差は
  トピック交絡ではなく、別Trial実行間のLLMサンプリング分散である可能性
  が高い。ただしN=16〜18・attempt別ではN=5〜6と小さく、統計的に断定は
  できない。**残差は残っており(全attempt込みでP2+0.034)**、Opusの
  推奨通り「N=10のA/B Trial(¥60〜80)」が必要かどうかはUDR候補(iii)
  として提示する(本タスクでは追加生成を行わない)。

### (g) Role Planning再計画の入力構造(コード確認)

- `er003_v1_n3_01_articles_generate.py:932-933`: retry時の`role_plan_
  result = point_planning.run_point_role_planning(client, topic,
  verified_ledger_text, model=writer_model, reasoning_effort=
  REASONING_EFFORT)`は、初回呼び出し(835-838行付近)と**完全に同一の
  2引数(topic, verified_ledger_text)のみ**であり、診断結果
  (lexical/value NGの理由)・前回article_text・overlap_reportのいずれも
  渡していない(引数シグネチャに存在しない)。**Opus指摘「盲目の
  再抽選」をコードで確認**。
- `er003_v1_n3_01_articles_generate.py:937`: `diagnostic_prompt =
  diagnostic_prompt + "\n" + point_planning.build_role_planning_block(
  role_plan_result["parsed"])`により、Role Planningブロックは診断
  section(前回NG例の説明)の**後ろに追加連結**される。
- `er011_point_role_value_planning_01.py:154-157`: 連結される
  `build_role_planning_block()`の冒頭文言は「【Point One / Point Twoの
  計画(Point Role Planning、**必ず従うこと**)】...この設計に**厳密に
  従ってください**」という強い命令形。診断section側の文言(「読んで
  理解するためだけの失敗例」)より明確に強い拘束力を持つ文言構造である
  ことを確認。**Opus指摘「診断より強い命令形」をコードで確認**。

---

## 3. 判定(作業3)

### 3-1. Opus指摘の支持/不支持

| Opus指摘 | 判定 | 根拠 |
|---|---|---|
| baseline 17/18でlexical flag(もぐらたたきは主因でない) | **支持(完全再現)** | (b) |
| 真の入れ替わりは4件(Trial-06限定) | **支持(完全再現)**、全Trial合計7件 | (b) |
| overlap_ratio分母=Point異なり内容語数、1語≈0.037 | **支持(ほぼ完全再現、0.0333)** | (a) |
| Focus側改善はPoint長交絡の可能性 | **条件付き支持**(Trial-05のgapfixは交絡で大半説明、Trial-06/04のfocus/hintは交絡後も優位性残存=交絡ではない) | (a) |
| value単独NG時にoverlap診断を無条件構築(誤診断) | **支持(コード確認)**。Trial-06限定2/2は再現、全Trial合計は4/9(44%)に減衰 | (c) |
| 設計意図が実装漏れか仕様どおりか | **基本構造は仕様どおり**(加算的設計として明記済み)。文言精度問題は**不明(未検討)** | (c) |
| Role PlanningはFocus Moduleと因果経路なし | **支持(コード確認)** | (e)(g) |
| Trial-07のRole収束はFocus Module起因と説明できない | **支持**。ただし収束自体(discovery_focus実績6 run全て2categoryのみ)の真因は依然不明、新規サンプリングでは再現せず | (e) |
| Role Planning再計画は診断結果を受け取らない盲目の再抽選、診断より強い命令形 | **支持(コード確認)** | (g) |
| G1語彙プライミング仮説 | **不支持寄り**(attempt=0で既に差があり、G1は構造上attempt=0に影響し得ない。ただし残差自体は存在) | (f) |
| 整理候補1(Role Planning一本化)・候補4(複数提示)は保留 | **支持** | 観点3・4、Trend Synthesisとの競合を確認 |

### 3-2. UDR候補(実装しない、費用・効果・Fact Safetyリスク・実装規模を付記)

**(i) value単独NG時のoverlap診断構築を条件分岐する**
- 現状: 常に無条件でoverlap診断section(断定文含む)を構築、value QA
  診断メモは条件付きで追加。
- 判定根拠: 基本構造は仕様どおり(加算的設計)だが、value単独NG時の
  断定文の事実精度は未検討。
- 期待効果: 全Trial合計で value単独NG後の新規lexical flag発生率(44%)
  低下の可能性(Trial-06限定では2/2=100%だったが母数9では44%、効果の
  確度は中程度)。
- コスト: ¥0(追加API呼び出しなし、条件分岐のみ)。
- Fact Safetyリスク: 低(診断文言の精度向上はFact Safetyを緩和しない)。
- 実装規模: 小(`build_diagnostic_retry_prompt()`と`build_diagnostic_
  section()`呼び出し部分に`lexical_flagged`分岐を追加する程度)。

**(ii) overlap指標の分母正規化/閾値再校正**
- 現状: 閾値0.40固定、分母はPoint側の異なり内容語数のみ(Full Story側
  語数を考慮しない一方向指標)。
- 判定根拠: 閾値0.40は分布中央付近(全体平均overlap_ratioは概ね0.35〜
  0.42のレンジ、条件により変動)。
- 期待効果: 閾値精度向上によるretry回数最適化(効果は不明、追加検証
  必要)。
- コスト: 分母変更は既存記事群への再遡及評価が必要(¥数百〜規模)。
- Fact Safetyリスク: **中**(QA基準=Production安全装置の変更、A-UDR-7
  観測Exit条件・OPEN-134との整合確認が必須、Fact Safety緩和と誤認され
  ないよう慎重な検討が必要)。
- 実装規模: 中(既存閾値の履歴・多数記事への遡及影響評価を伴う)。

**(iii) G1語彙プライミングのA/B Trial要否**
- 現状: ¥0再集計では支持されず(attempt=0で既に差、非単調)。ただし
  残差(全attempt込みP2+0.034)は残る。
- 判定根拠: (f)。
- 期待効果: G1が実際に語彙プライミングとして機能しているかの確定
  (現状は「不明、確率低め」)。
- コスト: Opus見積りN=10、¥60〜80。
- Fact Safetyリスク: 低(観測のみ、Production変更を伴わない)。
- 実装規模: 小(既存Trial-06/04と同型のA/B再実行)。
- **本タスクの結論としては優先度低**(¥0再集計で仮説がむしろ弱まった
  ため、他のUDR候補より優先度は下げてよいと考えられる。最終判断は
  ユーザー)。

**(iv) Role Planning再計画へ診断結果を渡す(仕様変更候補)**
- 現状: 初回・retryとも同一2引数のみ、診断結果非依存の「盲目の再抽選」。
- 判定根拠: (g)。Trial-07のRole収束問題(discovery_focus 6/6 runが
  mechanism/myth_correctionのみ)の真因が依然不明であるため、この変更が
  収束問題を解決するかは不明。
- 期待効果: 不明(収束問題の真因未特定のため、効果を予測する根拠が無い)。
- コスト: 新規プロンプト設計・単体テストで小〜中規模(¥0〜数十円/検証)。
- Fact Safetyリスク: 低(Role Planning自体はFact Checkerより前段の
  計画工程、直接のFact Safety変更ではない)。ただし「必ず従うこと」の
  命令文言強度の見直しも合わせて検討する必要がある(観点3のTrend
  Synthesisとの競合に配慮)。
- 実装規模: 中(`run_point_role_planning()`のシグネチャ変更、呼び出し元
  2箇所[初回・retry]の整合、既存単体テスト`er011_test_point_role_value_
  planning_01.py`の更新を伴う)。

### 3-3. 段階2への申し送り

- discovery_focusのRole収束(6/6 run全てmechanism/myth_correctionのみ)
  という実績データ自体の異常性は、本タスクの新規サンプリング(N=10)でも
  再現せず、真因は不明のまま残る。段階2ではこの異常の原因調査
  (当時のモデル応答ログ・reasoning_effort設定・prompt完全一致確認等)を
  優先候補とすることを提案する(実装ではなく調査)。
- UDR候補(i)〜(iv)はいずれも人間ユーザーの承認(`APPROVED_FOR_
  PRODUCTION`または明示的UDR裁定)が無い限り実装しない。

---

## 4. 費用・成果物

- **実測費用合計**: ¥3.34((e)のみ、N=10、Household Ledger/topic、
  Point Role Planningのみ・Writer呼び出しなし)。上限¥15以内。
- (a)〜(d)、(f)、(g)は¥0(既存JSONの読み取り再計算・コード引用確認のみ)。
- **新規ファイル**:
  - `FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01_REPORT.md`(本
    ファイル、root)
  - `er011_point_quality_stage1_recomputation_01.py`(再集計script)
  - `er011_output/point_quality_stage1_recomputation_01/stage1_
    recomputation_results.json`((a)〜(d)、(f)の全数値結果)
  - `er011_point_role_planning_reproducibility_stage1_01.py`((e)の
    N=10抽選script)
  - `er011_output/point_role_planning_reproducibility_stage1_01/`
    (results.json、run0〜9_full.json、raw_usage_log.jsonl)
- **Production/Prompt/SSOT**: 無変更(編集していない)。
- **Git操作**: なし(本タスクの禁止事項どおり)。
