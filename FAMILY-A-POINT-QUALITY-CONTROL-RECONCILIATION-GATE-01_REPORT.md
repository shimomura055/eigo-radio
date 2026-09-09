# FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01 報告書

管理ID: FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01。
**読み取り専用の横断整理**。編集・Trial実行・API呼び出し・Git操作は一切
行っていない。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。
並列稼働中のLane B 3V Trial-03(`er012_*`)・FACT-03再検証
(`er003_output/n3_01/household/`)・SSOT統合タスクの成果物・作業対象は
参照・編集していない。

News(A3-UDR-3)/Discovery(D2-UDR-1)のProduction採用案は不承認のまま
(Focus Module/Point Role自体はREJECTEDではない)。本タスクは新規Prompt・
新規QAを一切追加せず、既存の仕組みを整理する。

---

## 1. 一枚の構造図(Point品質に関与する仕組み一覧)

発火タイミング列の凡例: 初=初回生成前/生成直後、Retry=Diagnostic Full
Retry attempt内、最終=retryループ終了後に一度だけ。

| # | 仕組み | 目的 | 担当する品質軸 | 発火タイミング | 入力 | 出力/判定 | 承認Status | 導入管理ID | 重複・競合・依存 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Writer Prompt「言い換えによる重複の禁止」(`COMMON_BLOCK_TEMPLATE` 196-217行) | Point がMain Story核心の言い換えにならないよう事前に指示 | 重複回避(語彙・意味) | 初(唯一のWriter呼び出し前) | Verified Fact Ledger, Master記事 | Writerへの自然文指示(機械判定なし) | `PRODUCTION_WIRED`(ER-008-N8-FINAL-CLOSEOUT-24) | ER-008-N8-FINAL-CLOSEOUT-24 | lexical Overlap QA(#6)・Diagnostic feedback(#8)と同じ「語彙重複」を別レイヤーで扱う(§2-1) |
| 2 | Writer Prompt「Pointが実際に新しい価値を持つこと」(`COMMON_BLOCK_TEMPLATE` 221-232行) | 留保・免責事項だけのPointを禁止 | 価値 | 初 | 同上 | 同上(機械判定なし) | `PRODUCTION_WIRED`(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01) | 同上 | Point Value QA(#5)と同じ判定基準6項目を事前指示として重複配置(意図的、prompt→QAの対応関係) |
| 3 | Point Role Planning(`er011_point_role_value_planning_01.py::run_point_role_planning`) | Point One/Twoの役割・根拠・重複禁止事項を生成前に計画 | 役割分担・価値・重複回避(事前計画) | 初+Retry毎回再計画(`er003_v1_n3_01_articles_generate.py` 841-845行/932-938行) | topic, verified_ledger_text のみ(**article_text・editorial_type_module_block は渡らない**) | `role`/`new_listener_takeaway`/`evidence_anchor`/`why_it_matters`/重複禁止2項目 | `PRODUCTION_WIRED`(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01) | 同上 | Focus Module(#4)と役割決定を二重に行う可能性(§2-2)。過去A/B比較で単独では0/3 PASS(`er009_n1_point_role_planning_11.py`、DECISION_LOG.md:2629/5984) |
| 4 | Focus Module(`editorial_type_module_block`、`EDITORIAL_TYPE_MODULE_BLOCKS`辞書) | Editorial Type固有の題材焦点・役割候補をWriter promptへ注入 | 役割分担・題材焦点 | 初(Writer prompt構築時、`build_common_block` 471-495行) | editorial_mode文字列(人間が明示指定) | Writer promptへの文字列挿入 | Trend=`PRODUCTION_WIRED`(辞書に`"trend_synthesis"`のみ登録)。News/Discovery=**未登録**(`major_daily_news`/`discovery_why`いずれもTrial限定、辞書に不在、grep確認済み) | OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01(Trend) / FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01・FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07(News/Discovery、いずれもTrial) | #3と役割決定が二重(§2-2)。Point Role Planningへは届かない(Gap Audit確認済み) |
| 5 | Point Role hint(`point_role_hint_block`、Trial-03) | Focus Module語彙をPoint Role Planning promptへ短文で直接注入する接続候補 | 役割分担(#3⇔#4の接続) | 初+Retry(実装すれば#3と同時) | Focus Module語彙の要約 | Role Planning promptへの短文挿入 | `VALIDATED`(Trial-03推奨案(b))、**未配線**(Production関数に`point_role_hint_block`引数なし、grep確認) | FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03 | #3の役割決定を#4寄りに誘導する設計(§3-B/C参照)。役割固定・多様性喪失のリスク(§3-I) |
| 6 | lexical Point Overlap QA(Full Story対Point、`er008_point_overlap_qa_18.py`) | PointがFull Storyの言い換えでないかを機械判定 | 重複回避(語彙、Full Story対Point) | 初+Retry毎回(`run_point_overlap_qa_and_regenerate`) | Point本文, Full Story本文 | overlap_ratio(閾値0.40)、`flagged` | `PRODUCTION_WIRED`(ER-22/23、閾値0.40はER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19で暫定調整) | ER-008-N8-QA-CONTENT-SPEED-HARDENING-18 | #1・#8と同じ「語彙重複」を三重に扱う(§2-1) |
| 7 | cross_point_overlap(Point One対Point Two、同一関数を双方向適用) | Point同士の重複を検知 | 重複回避(Point間) | 初+Retry毎回で**計算のみ**(`run_point_overlap_qa_and_regenerate` 710行) | Point One本文, Point Two本文 | overlap_ratio、`flagged`(計算されるが未使用) | `DECIDED`(統合方針)/**`DEFERRED`(retry判定[`still_flagged`]への統合は未実装、OPEN-133、A-UDR-21でSSOT記載を実態へ訂正済み)** | ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 | #6と同一関数だが`lexical_flagged`(863-873行)に含まれず、retry判定へ寄与しない(不足、§2-4) |
| 8 | Diagnostic Full Retry診断section(`er009_diagnostic_full_retry_modules_12.py::build_diagnostic_section`) | Retry時にWriterへ前回失敗の具体的な語彙・分類を提示 | 重複回避(語彙、フィードバック) | Retry構築時のみ | 前回Full Story全文, #6のoverlap_ratio/shared_words, 前回Point One/Two本文(G1修正後) | 診断テキスト(shared_words最大12語+evidence/implication/cause/genericの粗い分類) | `PRODUCTION_WIRED`(G1修正含む、OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01、commit 8596f34) | ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14 | #1・#6と同じ「語彙重複」を三重に扱う(§2-1)。cross_point_overlap(#7)の値は診断本文に含まれない(G2、実装しない判定済み) |
| 9 | Value QA診断メモ(`build_value_qa_diagnostic_note`) | Retry時にWriterへPoint Value QA NG理由を提示 | 価値(フィードバック) | Retry構築時、`value_qa_flagged`時のみ(916-918行) | #10のfail_fields/reasoning | 診断section直後へ追加するテキスト | `PRODUCTION_WIRED`(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01) | 同上 | **既にProductionへ配線済み**(Fableブリーフの「拡張案」5は既存仕様であることを確認、§5参照) |
| 10 | Point Value QA(`run_point_value_qa`) | Point本文が実際に新しい価値を持つかを独立LLM判定 | 価値 | 初+Retry毎回(`sections_for_value_qa`が解析できた場合のみ、881-892行) | Full Story, Point One/Two本文 | 6項目PASS/FAIL(`qa_not_caveat_only`等) | `PRODUCTION_WIRED`(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01) | 同上 | #6(lexical)とOR条件で`still_flagged`を構成、互いに独立判定のため相互作用が発生しうる(§2-3、Trial-06実データで実証) |
| 11 | Loop Budget(`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`) | #6/#7/#10のretry回数上限 | 安全装置(無限retry防止) | Retry全体を統括 | #6・#10の`still_flagged` | 2回retryでもNGなら`status="NG_REVIEW_REQUIRED"` | `PRODUCTION_WIRED`(ER-22) | ER-22 | Local Rewrite(`MAX_REWRITE_CYCLES`)・Human Review Lockの`PRODUCTION_MAX_TTS_ATTEMPTS`とは別の独立した上限(混同なし、769行コメント確認) |
| 12 | Fact Checker(独立Web検索) | 記事(Point含む)と外部情報源の整合性 | 事実性(外部照合) | 最終(retryループ終了後、一度だけ) | 確定article_text | verdict PASS/REVIEW_REQUIRED(non-blocking)/FAIL(blocking) | `PRODUCTION_WIRED` | ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 | Point Role Planning/Value QAの「価値」判定とは無関係、Point文言がPoint品質QAをPASSした後で初めて評価対象になる(順序依存、§2-5) |
| 13 | Ledger Deviation Checker + Local Rewrite | 記事(Point含む)とVerified Fact Ledgerの整合性 | 事実性(Ledger内整合) | 最終(Fact Checker通過後)、MAJOR時はLocal Rewrite cycle(`MAX_REWRITE_CYCLES`まで) | 確定article_text, Ledger | MAJOR/MINOR、Local Rewriteは局所文修正のみ(Point Role Planning再計画なし) | `PRODUCTION_WIRED` | ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02 / ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10 | Local RewriteはPoint Role Planningを再実行しない(#3と非対称、Trial-03確認済み) |
| 14 | Human Review(NG_REVIEW_REQUIRED後の人間判断) | 機械QA全上限到達後の最終判断 | 総合(最終セーフティネット) | 最終 | #6/#7/#10/#12/#13のいずれかの終端結果 | 人間による採否判断(記事レベル) | `PRODUCTION_WIRED` | ER-22ほか | Point品質そのものは判定せず、機械QAが尽きた後の受け皿 |

**仕組みの数**: Point品質へ直接関与するのは#1〜#10(10種、うち#7は計算のみで
retry判定へ未接続)。#11(Loop Budget)は共有の安全装置。#12〜#14(Fact
Checker/Ledger Deviation・Local Rewrite/Human Review)はPoint固有ではない
隣接安全装置だがPoint文言もその対象に含む。**担当軸は5つ**(重複回避
[Full Story対Point/Point対Point]・価値・役割分担・多様性・事実性)。

---

## 2. 重複・競合・不足の判定

### 2-1. 語彙重複の三重扱い(実証)

「Full Storyとの語彙重複」という同一の品質軸を、(a) Writer Prompt原則
(#1、事前・自然文指示)、(b) lexical Overlap QA(#6、事後・機械閾値0.40)、
(c) Diagnostic Full Retry診断section(#8、retry時・shared_words提示)の
**3層で扱っている**。これ自体は「予防(#1)→検知(#6)→是正フィードバック
(#8)」という役割分担として合理的に見えるが、(#8)が(#6)の出力をそのまま
再利用する設計(`shared_words`/`overlap_ratio`を直接埋め込む)であるため、
実質的に(#6)の判定基準がWriterへの説明としても機能しており、独立した
3層というより「1つの判定基準(lexical overlap閾値0.40)を prompt/QA/
feedbackの3箇所で反復提示している」構造に近い。**重複というより多重の
念押し**であり、危険な重複ではないが、閾値0.40自体の妥当性(暫定値のまま
CURRENT_SPEC記載、OPEN-134観測対象)を1点でしか検証できていない点が
構造上の限界。

### 2-2. Point Role PlanningとFocus Module hintの役割決定二重化

Focus Module(#4)はWriter本文生成promptへ挿入され、Point Role Planning
(#3)はFocus Moduleを一切知らない独立LLM呼び出しとして役割を決める
(`FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03`§1が
呼び出しチェーンで実証)。現状は「Focus Moduleが本文生成に効く」
「Point Role Planningが独自に役割を決める」という**分離**であり二重
決定ではないが、Point Role hint(#5)を配線すると、Focus Module語彙が
Point Role Planningへも流入し、**同じ役割語彙(mechanism/beyond-the-
headline等)が(a)Writer本文promptへのFocus Module注入と(b)Point Role
Planningへのhint注入の2経路から二重に届く**設計になる(Trial-03推奨案
(b)自体はhint経由の直接注入でありFocus Module全文の重複注入ではないため
設計上は軽量だが、「役割を決める主体」が実質的に2つ[Focus Module文言＋
Point Role Planning]になる点は変わらない)。

### 2-3. Value QAとOverlap QAの相互排他性の欠如(retry logで実証)

Trial-06の`focus_hint`条件3 NG runの attempt別ログを直接確認した:

- `a2/focus_hint/run2`: attempt0(lexical=True,value_qa=True)→attempt1
  (lexical=True,value_qa=**False**)→attempt2(lexical=**False**,
  value_qa=True)
- `a2/focus_hint/run3`: attempt0(True,True)→attempt1(False,True)→
  attempt2(True,False)
- `b1b/focus_hint/run1`: attempt0(True,False)→attempt1(True,True)→
  attempt2(True,True)

(出典: `er011_output/news_focus_hint_comparison_trial_06/{a2,b1b}/
focus_hint/run{2,3,1}/point_overlap_article_retry_log.json`)

いずれも**片方の軸が解消すると別の軸が新たに(または継続して)flagされる**
「もぐらたたき」パターンが実データで確認できた。retryは記事全体を
Ledgerから再生成する設計(Point-onlyではない)であり、diagnostic
section(#8)はlexical overlap軸の情報しか持たず、value QA診断メモ(#9)は
value_qa_flagged時のみ追加される。両方が同時にflagされた場合は両方の
フィードバックが渡るが、Writerの新規生成は非決定的なLLM呼び出しであり、
「lexicalを直すために語彙を変える」ことが「valueの新規性」を損なう
(または逆)という**構造的なトレードオフが存在する可能性**を示唆する
(2試行では統計的に確定できないが、3例中3例で軸の入れ替わりが観測された
ことは偶然とは考えにくい)。

### 2-4. cross_point_overlap統合の不足(実装漏れ、既にOPEN-133として記録済み)

Point One対Point Two自体の重複(#7)はCURRENT_SPEC.md記載上は
`still_flagged`判定へ統合済みとされていたが、`FAMILY-A-POINT-OVERLAP-
GAP-FIX-TRIAL-05`のGate 4監査で未実装と判明し、A-UDR-21でSSOT記載を
「統合済み」から「未実装・`DEFERRED`」へ訂正済み(OPEN-133)。本タスクでも
`er003_v1_n3_01_articles_generate.py` 871-873行の`lexical_flagged`計算
(`before_overlap`のみ参照、`cross_point_overlap`不使用)を直接確認し、
既存記録と一致することを再確認した。**「多様性を保証する仕組み」自体は
存在しない**(§3-Iで詳述、Discovery Layer3 TrialでPoint Role分類が
mechanism/myth_correctionへ100%収束しbroader_dimensionが消滅した実例が
唯一の直接証拠)。

### 2-5. 発火順序の非対称(Fact Checker/Ledger Deviationは最終確定後)

Point品質QA(#1・#3・#6・#7・#10)はretryループ内で完結し、Fact Checker
(#12)・Ledger Deviation(#13)はretryループが終わった**確定後の記事**に
対して一度だけ実行される(769行コメント「Fact Checker・Ledger Deviation
Check・Directional Fact Precheckは、retryループが終わり最終的に採用が
確定した記事に対して一度だけ実行する」)。この順序自体は費用最適化
(TTS前完結)として合理的だが、Point Role Planning/Value QAが「価値」を
追求する過程で生まれた解釈的表現(mechanism/myth_correction dwelling等)
が、後段のFact Checkerで初めてunsupported claim扱いされる(Discovery
Layer3 TrialのREVIEW_REQUIRED急増、§4)という**構造上の遅延フィードバック**
が生じている。Point Role PlanningはFact Checkerの判定基準(evidence_
anchorがLedgerのどのFactに基づくか)を事前に問うてはいるが、Fact
Checkerの実際の外部照合結果を学習・反映する経路は存在しない。

---

## 3. Trial-06 NG 3/6の原因分解(A〜I)

A. **Focus Module効果**: baseline(Focus Moduleなし・hint無し)はA2/B1B
   両レベルとも6/6 NG(100%)。focus_hint条件は3/6 NG(50%)で、両レベル
   一貫して改善(baselineに対し系統的に良好)。Focus Module文言自体は
   一定の改善効果を示した。

B. **Point Role hint効果**: hint_only(Focus Moduleなし・hintのみ)は
   N=2(bonus)と極小標本だが1/2 NG。focus_hintとhint_onlyを分離した
   直接比較はN不足で断定不可(Trial-06自身がN数不足を明記、§6項目6)。

C. **既存Point Role Planning効果**: baseline条件でもPoint Role Planning
   自体は毎回実行されている(#3はhintの有無に関わらず常時稼働)。
   baseline 100% NGという結果は、Point Role Planning単独では今回の
   overlap/value問題を解消できていないことを示す(既存機構としての
   限界が改めて確認された)。

D. **Value QAとの相互作用**: §2-3の通り、focus_hint 3 NG中3例全てで
   lexical/value_qaの少なくとも一方が全attemptを通じてflagされ続けるか、
   両者が入れ替わりながらflagされ続けた。3例ともfinal attemptで
   いずれか一方(またはbothが解消できないまま)Loop Budget上限(2)に
   到達した。

E. **Diagnostic Full Retryとの相互作用**: 診断sectionはlexicalのみを
   詳細に説明し、value QA理由は別メモ(#9)として追加されるが、両方の
   フィードバックが同時に渡っても、非決定的な全文再生成という設計上、
   両方を同時に解消する保証がない(§2-3のretry log自体がこれを示す)。

F. **lexical Overlapとの相互作用**: `a2/focus_hint/run3`はattempt2で
   lexicalが再flag(0.400ちょうど、閾値到達)。attempt1でvalue QA対応の
   ため文言を変えた結果、Full Storyとの語彙重複が再発した可能性が
   考えられる(individual attemptの本文比較は本タスクのスコープ外、
   仮説として記録)。

G. **retryごとにfailure modeが移る理由(実データで機序を示す)**:
   §2-3の3例で共通するパターンは「あるattemptで一方の軸(lexical/value)
   を解消する新しい記事全体が生成されると、別の軸で新たにflagされる」
   というものである。原因として構造的に指摘できるのは: (1)retryが
   Point単位ではなく記事全体の再生成であるため、一方の問題を避けようと
   語彙・構成を変えると、もう一方の判定基準への適合が保証されない。
   (2)lexical Overlap QAは機械的・決定的(同じ入力なら同じ判定)だが、
   Value QAはLLM判定であり、生成のたびに評価軸(caveat only/paraphrase/
   specific/new value)の重み付けが変わりうる。(3)Point Role Planningが
   毎回再計画される(#3、Retry時も含む)ため、retry間で「役割」自体が
   変わり、新しい役割設計が新しい語彙重複または新しい価値不足を生む
   可能性がある(役割の再計画自体は前回の失敗を踏まえた診断section
   [#8/#9]を見て行われるが、診断は主にlexical軸の情報であり、value軸の
   情報は別メモとしてのみ渡る)。

H. **ER-009-N1のPoint Role Planning 0/3失敗と今回方式(hint注入)の本質的
   差**: 過去のA/B比較(`er009_n1_point_role_planning_11.py`、DECISION_
   LOG.md:2629/5984)は、**Point Role Planning単独**(診断feedbackなし、
   全文retryなし)とDiagnostic Full Retry(診断feedbackあり)を比較する
   ものであり、「Point Role Planningという事前計画だけでは実際の
   overlap/valueを解消できない」ことを示した(0/3)。今回のTrial-06は
   Point Role Planningを**Diagnostic Full Retryと組み合わせた状態**
   (現行Production仕様そのもの)にFocus Module hintを追加注入した
   もので、比較対象が異なる(単独計画 vs 計画+検知+フィードバックの
   複合機構)。したがって「hint注入がPoint Role Planning単独実験の失敗を
   克服した」とは言えず、**今回のbaseline自体が既にDiagnostic Full
   Retry込みでも100% NGだった**という点が、旧実験(0/3)よりもむしろ
   悪化して見える(§2-3・OPEN-134の観測記載どおり、G1修正後baselineの
   悪化がG1由来かサンプリング変動かは未切り分け)。

I. **Point Role固定・誘導による多様性の毀損**: Trial-06自体では役割
   分類(mechanism/beyond_the_headline/other)がbaseline/focus_hint両条件
   でほぼ同水準(P1 33.3%、P2 16.7%)であり、hint注入によるrole文言への
   明示的収束はキーワード機械分類では検出できなかった(限界: キーワード
   語彙が実際のWriter出力と一致しにくい)。一方、**Discovery Layer3
   Trial-07では明確な多様性喪失が実証された**: baseline(12枠)は
   mechanism4/myth_correction3/broader_dimension4/other1と分散していた
   のに対し、discovery_focus(12枠)はmechanism6/myth_correction6/
   broader_dimension0/other0へ**完全収束**した(Trial-07§7)。Focus
   Moduleが提示する役割候補が狭いと、Point Role Planningがその候補内へ
   収束し、Focus Moduleが提示しない役割方向(日常生活での意味づけ等)が
   選ばれなくなるという構造的リスクが、Discovery側で直接確認された。
   News側(Trial-06)でも同じ設計原理を採用しているため、同種のリスクは
   理論上残る(News側での役割分布は本タスクの再集計では確定できず、
   `hanshin/gapfix`系列の実データにはrole分類集計自体が実施されていない
   ため「不明」)。

**追加Trialが必要な項目とその最小Trial設計案**(実行しない、提案のみ):
- **項目D/G(相互作用の再現性検証)**: 現行baseline条件(Focus Module
  なし・hint無し)でN=10程度のretry attempt別ログを集計し、lexical⇔
  value_qaの入れ替わり率が統計的に有意な傾向かを確認する(条件1つ、
  N=10、既存Production経路のみ使用、追加Prompt変更なし、費用目安
  Trial-06の1条件相当[¥30〜40])。
- **項目I(News側のrole多様性)**: Trial-06の既存生成物(14本)へ、
  Discovery Layer3 Trial-07と同じrole分類ヒューリスティックを事後適用し
  再集計する(新規API呼び出し不要、既存JSON解析のみ、費用¥0)。

---

## 4. Discovery REVIEW_REQUIRED増加の原因分解

Trial-07(Household Ledger再利用、N=3×2条件×2レベル)のclaim→evidence
対応表を再利用する。

- **blocking(FAIL)自体はFocus Module起因ではない**: baseline/
  discovery_focusとも1/6ずつで同率発生し、原因は両条件共通の
  Household Ledger FACT-03(柑橘類の高湿度記載)に対するFact Checkerの
  非決定的な指摘であり、Focus Moduleが原因ではない(Trial-07§4、
  現行Production承認済み記事[2026-08-17]にも同一文言が存在し当時は
  問題視されていなかった事実で裏付け)。
- **REVIEW_REQUIRED増加(17%→67%、unsupported claims 0.33→1.67件/本)
  はFocus Moduleが解釈を押している結果**: discovery_focus条件の10件の
  unsupported claimsのうち8件はキーワード一致でLedger evidence id
  (FACT-01/02/03)へ機械的に紐付き、残り2件も人間読解ではLedgerの
  解釈・敷衍として説明可能だった(Trial-07§5、Ledger外の事実創作は
  0件)。すなわちWriterはLedgerの範囲を実際には超えていないが、
  Fact Checker(独立Web検索)が「Ledgerには書かれているがWeb上の
  一次資料では明確に裏付けられない敷衍」を積極的に拾っている。
- **Ledgerがinterpretation可能範囲を曖昧にしているか**: Household
  Ledgerの各Factは「confirmed fact」であることは明示されているが、
  「この事実からどこまで一般化・機構説明してよいか」という許容範囲は
  明示的なフィールドを持たない(#3のevidence_anchorはLedger内のどの
  Factに基づくかを問うのみで、敷衍の許容度は問わない設計)。Focus
  Moduleがmechanism/myth-correctionという役割をPoint Role Planningへ
  push すると、evidence_anchorはLedger内Factを指しているにもかかわらず、
  実際の本文が生成する「なぜ」の説明が、Ledgerが直接検証していない
  機構的細部まで踏み込みやすくなる。
- **Fact Checkerが妥当なTPを拾っているか / review labelのfalse
  positive**: 本タスクの再分析範囲では、Trial-07の10件は「Ledgerの
  解釈として妥当」という人間判断であり、Fact Checker側の指摘が
  「誤検知」とは言い切れない(Fact Checkerは独立Web照合という別の
  正当な安全基準で動いており、Ledger内包=Web照合済み、ではない)。
  したがって「WriterとFact Checker間のLedger-bounded interpretation
  許容範囲の不一致」が根本原因であり、どちらか片方が誤っているという
  単純な構図ではない。
- **Point Role収束とReview増の因果**: §3-Iで確認した通り、discovery_
  focus条件はPoint Roleがmechanism/myth_correctionへ100%収束した。
  この2方向はいずれも「なぜ」「訂正」という解釈色の強い役割であり、
  baselineが持っていたbroader_dimension(日常生活での意味づけ、解釈色が
  相対的に薄い)が失われたことが、unsupported claims増加と役割収束を
  結ぶ蓋然性の高い経路として読み取れる(Trial-07自身も同様の考察を
  記載、§7)。

---

## 5. 整理・統合・廃止の候補(実装しない、提案のみ)

### 候補1: 役割決定をPoint Role Planning一本に集約し、Focus Moduleは
題材焦点(語彙・トピック限定)のみに限定する

- **Reconciliation(2-2への対応)**: 現状Focus Module(#4)はWriter本文
  promptへ直接挿入され、Point Role Planning(#3)は独立に役割を決める
  ため、hint(#5)を追加配線すると役割語彙の入力経路が2つになる。候補1は
  Focus Moduleから「役割候補の明示」を削り、Point Role Planning(#3)
  へのhint(#5)だけを役割決定の単一入口とする案。Trial-03の推奨案(b)
  (役割候補のみの短文をRole Planningへ渡す)と設計思想は同じだが、
  Focus Module本文側から役割語彙を除去する点が新規要素。
- **コスト影響**: Focus Module文言の再編集が必要(Trend Synthesis
  PRODUCTION_WIREDへの影響評価必須、既存TREND_SYNTHESIS_FOCUS_MODULE_
  BLOCKの書き換えを伴うため`APPROVED_FOR_PRODUCTION`済み仕様への変更に
  該当し、慎重な回帰確認が必要)。API呼び出し回数は無変更(Point Role
  Planningは既に毎回呼ばれている)。

### 候補2: Value QA診断をDiagnostic feedbackへ拡張する(**注記: 既に
実装済み**)

- Fableブリーフが挙げた「Diagnostic feedbackへValue QA理由も渡す」は、
  `build_value_qa_diagnostic_note()`(#9)として**既にProductionへ配線
  済み**であることを確認した(`er003_v1_n3_01_articles_generate.py`
  916-918行)。したがってこれは新規候補ではなく、既存仕様の再確認事項
  として報告する。ただし§2-3で示した通り、配線済みであっても
  「もぐらたたき」現象は実データで観測されており、**フィードバックの
  存在自体は相互作用問題を解決していない**。

### 候補3: Overlap QAをValue QAより前に評価する順序変更

- 現状は両者を同一attempt内で並行計算し(871-892行)、OR条件で
  `still_flagged`を構成しているため、明確な「順序」自体が存在しない
  (順序変更というより、判定を逐次化しattemptごとに1軸だけを対象に
  retryする設計変更に近い)。**Reconciliation**: 逐次化はLoop Budget
  (2回)を「lexical用1回+value用1回」に事実上分割してしまい、両方が
  同時にflagされるケースでの解消可能性を下げるリスクがある(§2-3の
  3例はいずれも両方またはいずれかが繰り返しflagされ、2回では収束
  しきらない例が複数あった)。**コスト影響**: 実装は小さいが、Loop
  Budget自体の再設計(例えば上限を分離するか、共有のまま維持するか)
  はユーザー判断が必要な仕様変更。

### 候補4: 多様性を「役割候補の複数提示+選択」で担保する

- 現状Point Role Planning(#3)はLedgerから自由に1つの役割を選ぶ設計
  であり、Focus Module hint(#5)を追加すると選択肢がFocus Module語彙へ
  収束するリスクがある(§3-I実証)。候補4は、Focus Module hintを
  「必須の役割」ではなく「候補の一部」として複数提示し、Point Role
  Planning自身に選択・多様性確保の責任を残す設計(Trial-03の設計案
  (b)「Mode別Point Role候補リスト」がこれに近いが、Trial-03自体は
  単一hintのみを検証しており「複数候補提示+選択」は未検証)。
  **コスト影響**: 新規Prompt文言(候補リストの文言)が必要になるため
  「新Prompt文言の追加は最小限に」という制約に抵触しうる。実施する
  場合はhint文言を「候補の一部」と明記する程度の最小変更に留めるべき。

### 候補5(参考、実装しない): cross_point_overlapのretry統合(OPEN-133)

- 既にOPEN-133として`USER_DECISION_REQUIRED`登録済みであり、本タスクの
  新規候補ではない。§2-4で構造的位置づけを再確認したのみ。

---

## 6. Dangling Reference Check

Production Writer正式path(`er003_v1_n3_01_articles_generate.py`・
`er006_pool_pilot_01_writer.py`)を対象にgrep監査した。

- `major_daily_news`/`discovery_why`/`NEWS_FOCUS_MODULE`/`DISCOVERY.*
  FOCUS_MODULE`/`point_role_hint`のいずれも、上記2ファイルに**出現しない**
  (0件)。`EDITORIAL_TYPE_MODULE_BLOCKS`辞書は`"trend_synthesis"`の
  1キーのみを持つ(451-453行)。**News/Discovery Focus Module・Point
  Role hintはProduction pathへ混入していない**。
- `resolve_editorial_type_module_block()`は未知のmode文字列に対し
  fail-closedで`ValueError`を送出する設計(456-468行)であり、仮に
  誤って`"major_daily_news"`等が渡されても無音のno-op化やdangling
  fallbackにはならない。
- cross_point_overlap(OPEN-133、未実装のretry統合)は、CURRENT_SPEC.md
  側の記載が既にA-UDR-21で実態(未実装・`DEFERRED`)へ訂正済みであり、
  本タスクで新たなdangling reference は確認されなかった。

**結論: Dangling Reference なし**(News/Discovery Focus Module・Point
Role hintいずれも、Trial限定のまま Production path へは配線されて
いない)。

---

## 7. Fableへの提案

### 7-1. News/Discovery再改善Trialの推奨順序と最小構成

1. **原因切り分け(最小・追加API費用ほぼ0)**: 3-A/G/Iで提案した
   「既存生成物の事後再集計」(Trial-06 14本のrole分布、baseline
   N=10のretry log集計)を先に実施し、追加生成なしで得られる情報を
   使い切る。
2. **整理案の検証(小規模)**: §5候補1(役割決定の一本化)または候補4
   (役割候補の複数提示)のいずれかをユーザーが選択したうえで、
   Hanshin Ledger固定・N=3〜5・baseline対整理案の2条件比較Trial
   (Trial-06と同型ハーネス流用、追加費用目安¥50〜100)。
3. **比較Artifact作成**: 整理案がbaselineに対しNG率・役割多様性
   (Discovery Layer3 Trial-07と同じ機械分類ヒューリスティックを共通
   適用)の両方で改善するかを、News/Discovery両方で同一基準により
   比較する。

### 7-2. Opusレビューで確認すべき論点

- §2-3で実証した「もぐらたたき」パターンが、Loop Budget=2という
  既存の安全装置の設計思想(「2回で収束しなければ人間へ」)と整合的か、
  それとも構造的に2回では不十分な設計になっているか。
- §3-I・§4で確認したPoint Role収束→多様性喪失→REVIEW_REQUIRED増加
  という連鎖が、Focus Module設計(役割候補を狭く提示する設計原理)
  そのものに内在する構造的トレードオフか、Household固有(Ledger
  FACT-03の脆弱性)の偶然の重なりか。
- §5候補1(役割決定の一本化)がTrend Synthesis(既にPRODUCTION_WIRED)
  へ与える回帰リスクの評価方法。

---

## 参照した一次資料

CURRENT_SPEC.md(938-940行ほか)、OPEN_ITEMS.md(OPEN-132/133/134/135行)、
DECISION_LOG.md(2554-2802行[ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01]、
5925-5989行[ER-009-N1系列])、`er003_v1_n3_01_articles_generate.py`
(101-495行、611-960行、1000-1070行)、`er008_point_overlap_qa_18.py`、
`er009_diagnostic_full_retry_modules_12.py`、
`er011_point_role_value_planning_01.py`、`er006_pool_pilot_01_writer.py`、
`FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01_REPORT.md`、
`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md`、
`FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03_REPORT.md`、
`FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06_REPORT.md`
(及び`er011_output/news_focus_hint_comparison_trial_06/`実retry log
JSON)、`FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07_REPORT.md`、
`FAMILY-A-COMPLETION-GAP-AUDIT-A1-01_REPORT.md`。
