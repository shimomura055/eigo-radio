# ER-010-WRITER-PRINCIPLES-STATUS-AUDIT-03 報告書

対象: Meaning First / Storytelling First / No Jargon の3原則について、現行Production
Writerでの正式採用状況を再監査し、Editorial Type一般化(Common Writing Contract化)の
前提となるBaseline仕様を確定する。今回はWriter一般化実装には入らない。

---

## 1. 結論サマリー

3原則は、**すべて同じ発端**(2026-08-30、ユーザーがNo.9試聴時に指摘した「Point Twoが
調査レポート的になる」問題、タスクID `ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03`)を
持ちながら、**その後の扱いが大きく異なる**ことが今回の監査で判明した。

| 原則 | 現在のStatus(正式分類) |
|---|---|
| Meaning First | **TRIAL VALIDATED / USER_DECISION_REQUIRED**(OPEN-91として正式記録済み、Production Prompt未反映) |
| Storytelling First | **UNDOCUMENTED TRIAL → PRODUCTION配線コードへの部分的混入(是正要)** |
| No Jargon | **UNDOCUMENTED TRIAL → PRODUCTION配線コードへの部分的混入(是正要)** |

最重要の発見は以下の3点。

1. **Meaning Firstは正規の手続きを踏んでいる**。専用Trial(Trial-03、意図的にgit未commit)
   →DECISION_LOGへの正式記録→OPEN-91としてUSER_DECISION_REQUIRED、という一連の流れが
   確認でき、記録に矛盾はない。ただし現行Production Writer Prompt(`COMMON_BLOCK_TEMPLATE`)
   には一切反映されていない。

2. **Storytelling FirstとNo Jargonは、ユーザーへ一度も正式報告されていない**。Trial-03
   完了後、同日中に別の未commit・未報告スクリプト(Trial-04/05/08)でこの2原則が独自に
   検証され、Trial-08では実際にNo.9記事全文(A2/B1)がこの方式で再生成されるところまで
   進んだ。しかしこの一連の作業はDECISION_LOG・OPEN_ITEMS・CURRENT_SPECのいずれにも
   記載がなく、ユーザーが正式に見聞きした記録が存在しない。

3. **にもかかわらず、この2原則の文言断片が、後続の一部Trial(10→11→12→13、いずれも
   commit済み)を経由して、現在Production配線済みのDiagnostic Full Retryモジュール
   (`er009_diagnostic_full_retry_modules_12.py`)内に"Preserve Storytelling First."
   "Preserve No Jargon."として literal に残存している**。これは前タスク
   (ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02)で発見した「dangling reference」
   バグの根本原因そのものであり、「初回生成では一度も指示していない原則を、再生成時に
   "維持せよ"と指示する」という宙に浮いた状態になっている。

このほか、(a) No.9本番記事・runnerスクリプトのGit保全を実施(commit `512bb78`、
ローカルのみ・push無し)、(b) DECISION_LOG/CURRENT_SPECの記録誤り("growing
frustration"→"strong consumer resistance"の適用対象の誤り)を訂正、(c) OPEN-90/91の
ID重複問題を再確認、をあわせて実施した。Production Writer本体の挙動・仕様は一切
変更していない。

---

## 2. Meaning First chronology / status

### 2-1. 発端

2026-08-30、ユーザーがNo.9(pool_n9_tip_screens)試聴時に3つの品質課題を指摘した
(タスク`ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03`)。うち1つが、**Writerが
Evidence・数値に引っ張られ、Podcastというより調査レポートのような文章になっている**
という指摘で、具体例としてNo.9 Point Twoで「78%/44%/66%→59%/36%」という4つの数値が
連続で読み上げられる箇所が挙げられた。ユーザーは「原因の切り分けのみ実施してSTOPし、
Writer Prompt/Verified Fact Ledger/Ledger Deviation Checker自体は変更しない」ことを
明示的に指示した。

### 2-2. 最初の提案・定義

同タスク内で、独立診断script `er009_writer_trial_diagnostic_03.py`(**DECISION_LOGに
「リポジトリへcommitしない」と明記された意図的な未追跡ファイル**、実際にgit履歴0件を
確認)が新規作成された。ここで初めて`MEANING_FIRST_INSTRUCTION`が定義された:

> "Before writing Point Two, first define in one sentence the single meaning you want
> the listener to take away (...). Then choose only the facts from the Verified Fact
> Ledger that support that one meaning. Write it as an interesting observation, not as
> a readout of a survey's results section. Do not add any fact that is not in the
> Verified Fact Ledger, and do not change what any fact means (its scope, direction,
> or certainty)."

あわせて数値圧縮の明示バリエーションとして`NUMERIC_COMPRESSION_1`(代表的な数値を
概ね1つへ圧縮)・`NUMERIC_COMPRESSION_0`(数値を一切出さず定性表現のみ)も定義された。

### 2-3. Trial

- **管理ID**: `ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03`内のTrial-03。
- **対象**: No.9実際のVerified Fact Ledger、実際のProduction Writer model/reasoning
  effort(`gpt-5.6-sol`/`high`)、実際のLedger Deviation Checker v2に対してのみ実施
  (Production側のprompt/moduleは無変更)。
- **パターン**: Trial B(Meaning First単体)/ Trial C1(+代表数値1個へ圧縮明示)/
  Trial C0(+定性表現のみ・数値0個明示)の3パターン × A2/B1 = 計6パターン。
- **結果**: 6パターン全てが`LEDGER_COMPLIANT`(MAJOR 0件)。MINORはA2の1パターンで
  1件のみ(「42%が以前より抵抗が減った」という個人内変化を「抵抗が減った人の割合が
  増えた」という比較へ言い換えてしまった軽微な逸脱)。現行本番文(4数値連続読み上げ)
  と比較し、いずれのTrialも「まず1文で意味を提示してから最小限のFactで裏付ける」
  構成になり、報告書調が解消したことを確認。数値の個数は明示指示なしでも自然に
  1個(44%)へ収束する傾向を確認。
- **原因判定**: 仮説A(Writer Promptの問題)が主要因。同一の粒度が細かいLedger・
  同一のDeviation Checker v2を使ってもMeaning First指示だけで明確に改善したため、
  仮説B(Ledger制約)・仮説C(Deviation Checker)は直接の阻害要因ではないと判断。
- **コスト**: 実測$0.479(約77円)。

### 2-4. ユーザー判断

Trial結果はOPEN_ITEMS.mdへ**OPEN-91**として正式記録された:

> 「Writer Point Two等が『調査レポート的』になる問題について、独立Trial(Production
> 配線なし)でMeaning First指示(+数値圧縮の明示、あり/なし2パターン)を検証した結果、
> 6パターン全てが...LEDGER_COMPLIANTを維持しつつ『調査レポート感』が明確に解消する
> ことを確認した。(中略)Production Writer Promptへ正式採用するかどうかはユーザー
> 判断待ち」— `USER_DECISION_REQUIRED`

「Trial結果が良い」という評価に留まり、`VALIDATED`(検証完了の意味では該当するが、
このプロジェクトの正式ステータス語彙としては次段階の`APPROVED_FOR_PRODUCTION`・
`PRODUCTION_WIRED`のいずれにも未到達)。ユーザーからの正式な採用可否の回答は、
本監査時点で記録上確認できない。

### 2-5. Production反映

**なし**。現行Production Writer(`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_
TEMPLATE`)を全文grepした結果、"Meaning First"という文字列は0件。commit履歴
(`git log --all -- er003_v1_n3_01_articles_generate.py`)を全件確認したが、
Meaning First採用を示すcommitは存在しない。

### 2-6. 現行実装

`COMMON_BLOCK_TEMPLATE`内の「Spoken-first原則」セクションD「一つの文、または一つの
短い意味ブロックで、聞き手が同時に比較しなければならない主要数字は原則2つ以内とする」
は、結果として数値圧縮に近い効果を持つが、これは**commit `17aa9b2`
(ER-003-A2-B1-N3-01、2026-08-12時点)から存在する既存ルールであり、Meaning First
Trial(2026-08-30)に由来するものではない**。「Evidenceを並べる前に、伝えたい意味を
一文で先に決める」というMeaning Firstの核心的な思考順序そのものは、現行Prompt
のどこにも存在しない。両者を混同しないこと。

### 2-7. No.9最終記事との関係

現行No.9本番記事(`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`)
を直接確認した結果、A2 Point Two・B1 Point Twoとも「78 percent...44 percent...
59 percent...36 percent」のように統計をほぼそのまま列挙する構成が**現在も残っている**。
すなわち、**No.9最終記事はMeaning First採用前の状態のまま**であり、Trial結果は
No.9の完成品には一切反映されていない。

### 2-8. OPEN-91との整合

**完全に一致**。OPEN-91の記述(発端・Trial内容・6パターン中MAJOR 0件・
USER_DECISION_REQUIRED)は、DECISION_LOGの実エントリ(`ER-009-N1-CONTENT-QUALITY-
RECALIBRATION-03`)および実Trialスクリプトの内容と矛盾なく一致することを確認した。
古いstatusの残存や誤記は無い。

---

## 3. Storytelling First chronology / status

### 3-1. 発端

Meaning Firstと同じNo.9試聴指摘・同じタスク`ER-009-N1-CONTENT-QUALITY-
RECALIBRATION-03`が起点。ただし、このタスクの**正式DECISION_LOGエントリ自体は
「Trial D(阪神記事の構成原則抽出)は実施しなかった」と明記**している(理由: 現行
`COMMON_BLOCK_TEMPLATE`に既に阪神記事の構成原則が組み込まれているため独立Trialとして
実施する根拠が薄いと判断)。

### 3-2. 最初の提案

Trial-03完了(見送り判断を含む)の**後**、同日中(2026-08-30、ファイル更新時刻から
Trial-03完了より後と推定)に、別の一連の未commit・未報告スクリプトで独自に
Storytelling First概念が具体化された:

- `er009_writer_trial_diagnostic_04.py`(14:13更新): `STORYTELLING_STRUCTURE`を
  新規定義。「(1) Hook — 短く具体的で人間的規模の導入、(2) Meaning — このpassageが
  伝えたい1つの考え、(3) Evidence — それを支える最小限のFact、(4) Interpretation —
  なぜ聞き手にとって重要かの短い結び」という4段構成。`trial_D_storytelling`
  (Meaning First+数値圧縮+Storytelling Structure)として定義。
- `er009_writer_trial_diagnostic_05.py`(15:32更新、タスク名`ER-009-N1-STORYTELLING-
  LEDGER-TRIAL-05`と自己記載): `STORYTELLING_FIRST_NO_JARGON`として統合。
- `er009_n1_full_writer_ledger_integration_08.py`(17:51更新): `STORYTELLING_FIRST`
  定数を独立定義し、**No.9 A2/B1の記事全文をこの方式で実際に再生成**するところまで
  踏み込んだ。定義文言:

  > "Storytelling First: Do not read facts out in order. First decide what is
  > interesting and what you want the listener to take away. Weave Hook, Meaning,
  > Evidence, and Interpretation together into a natural, spoken-style passage..."

これら3ファイルは**いずれも一度もgit commitされていない**(`git log --all --
-- <file>`で0件を確認)。

### 3-3. Trial

- **管理ID**: 上記3ファイルにはそれぞれ独自の番号(04/05/08)が振られているが、
  これらに対応する専用DECISION_LOGエントリは存在しない(全文grepで"storytelling"
  0件)。
- Trial-08の実測結果(`er009_output/full_writer_ledger_integration_08/results.json`):

| Level | Hook | jargon_found | final_ledger_check | Point One overlap | Point Two overlap |
|---|---|---|---|---|---|
| A2 | あり(1文) | [] | `LEDGER_COMPLIANT`(MAJOR/MINORとも0) | 0.409(**flagged**、閾値0.40超) | 0.542(**flagged**) |
| B1 | あり(1文) | [] | `LEDGER_COMPLIANT`(MAJOR/MINORとも0) | 0.310(flag無し) | 0.333(flag無し) |

Fact安全性(Ledger Deviation)の観点では両レベルとも問題なしだが、**A2はPoint
Overlap QAでflagされており、Storytelling First単体ではPoint Overlap問題(No.8/No.9で
継続していた既知の課題)を解決しない**ことが実測で判明している。

### 3-4. ユーザー判断

**記録なし**。OPEN_ITEMS.mdを全文grepしたが"Storytelling"は0件。DECISION_LOG・
CURRENT_SPECも0件。ユーザーがこの3ファイルの結果を見た、または採用可否を判断した、
という記録は一切存在しない。

### 3-5. Production反映

Writer Prompt本体(`COMMON_BLOCK_TEMPLATE`)への反映は**なし**(grep 0件)。しかし、
Trial-08の`STORYTELLING_FIRST`定数は、その後の一連の作業で以下のように再利用され続けた:

1. `er009_n1_point_retry_luna_10.py`(**commit `04adbeb`**、2026-08-30、
   `ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10`): No.9 A2のPoint Overlap Retryに
   Trial-08の`STORYTELLING_FIRST`/`NO_JARGON`定数をそのまま再利用。
2. `er009_n1_diagnostic_retry_11.py`(**commit `e1eae0d`**、
   `ER-009-N1-POINT-ROLE-VS-DIAGNOSTIC-RETRY-11`): retry prompt内に初めて
   **"Preserve Storytelling First."** という一文が literal に出現(116-117行)。
3. `er009_diagnostic_full_retry_modules_12.py`(**commit `f46b6e1`**、
   `ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-12`): 同じ一文をほぼそのまま継承
   (`DIAGNOSTIC_SECTION_TEMPLATE`83行)。
4. **commit `f6ecc1a`**(`ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13`)で、
   このモジュールが`er003_v1_n3_01_articles_generate.py`本体へ`import
   er009_diagnostic_full_retry_modules_12 as diagnostic_mod`として正式配線され、
   `PRODUCTION_WIRED`(DECISION_LOG `ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14`)
   まで到達した。

つまり、**「Storytelling Firstを正式採用する」という決定を一度も経ないまま、
Storytelling Firstを前提とした一文だけがProduction配線コードに残った**。

### 3-6. 現行実装

- `COMMON_BLOCK_TEMPLATE`(初回生成指示): Storytelling First/Hook/Meaning/
  Interpretationという文言・概念は一切存在しない。既存の「阪神記事の構成原則
  (概要→別切り口→一言まとめ)」は粒度・焦点が異なる別の原則である。
- `er009_diagnostic_full_retry_modules_12.py`(Point Overlap QA flagged時のみ発火する
  Diagnostic Full Retry): 83行目に**"Preserve Storytelling First."**が literal に
  存在。

**これが前タスクで発見した「dangling reference」バグの正体である**: retryプロンプトは
「(前回の生成で存在したはずの)Storytelling Firstを維持せよ」と指示するが、前回の
生成(初回生成)はそもそもStorytelling Firstを一度も指示されていないため、Writerが
実際に何を「維持」すべきかが定義されていない。

### 3-7. No.9最終記事との関係

現行No.9本番記事(a2/b1b `article.md`)を確認した結果、Hook文(短く具体的で人間的
規模の導入)で始まる構成には**なっていない**(通常のFull Story→Point One→Point
Two→In one lineという、既存の阪神記事構成原則に基づく文体のまま)。すなわち
No.9最終記事はStorytelling First採用前の状態である。

### 3-8. Diagnostic Full Retry内の"Preserve Storytelling First."との整合

**不整合が実在する**ことを確認した。文字列だけが存在しないのではなく、原則自体が
初回生成側のどこにも(別表現も含め)実装されていない。前タスクでの発見は正確だった。

---

## 4. No Jargon chronology / status

### 4-1. 最初の問題

Storytelling Firstと同一の発端(No.9試聴指摘)から派生。ただし、混同を避けるため
以下の3つの異なる"Jargon対策"を明確に区別する。

| 区分 | 対象 | 現在のStatus |
|---|---|---|
| (a) Key Phrase日本語glossの括弧書き禁止 | Key Phrase日本語gloss表記の**形式**(「（分析手法）」等の括弧補足を避ける) | `PRODUCTION_WIRED`(後述4-6) |
| (b) Key Phrase専門語回避 | Key Phrase**選定時**に高度専門語(regression discontinuity等)自体を選ばない | `USER_DECISION_REQUIRED`(OPEN-90) |
| (c) learner-facing全文でのNo Jargon | 記事**本文全体**で専門用語(研究手法名等)を一切使わない、という**Writer Prompt原則** | 本節の調査対象。UNDOCUMENTED |

### 4-2. Key Phraseのみのルールとして始まったか

はい。(a)(b)はいずれもKey Phrase(語句)レベルの問題として、No.8/No.9のKey Phrase
選定結果("uneven choice"括弧書きgloss、"regression discontinuity"という専門語選定)
から出発している。

### 4-3. learner-facing script全体への拡張の経緯

(c)は、Trial-03完了後の未報告Trial-04(`er009_writer_trial_diagnostic_04.py`、
14:13更新)で初めて、Key Phrase選定とは独立に**記事本文全体**を対象とする概念として
新規定義された:

> `JARGON_TERMS = ["regression discontinuity"]`
> `NO_JARGON = "Do not name any academic research method, statistical technique, or
> other high-level technical term (...). If the underlying method matters to the
> story, describe in plain, natural language what the researchers actually did and
> why it lets them draw a fair comparison — without naming the technique. A learner
> should be able to understand the sentence on a single listen without needing to
> know the name of any research method."`

`detect_jargon()`という機械的検知関数も同時に定義された(`JARGON_TERMS`との文字列
一致のみ、汎用的な専門語検知ではない)。

### 4-4. Trial

- Trial-04 `trial_E_no_jargon`(Meaning First+数値圧縮+Storytelling Structure+
  No Jargon)、Trial-05(`STORYTELLING_FIRST_NO_JARGON`として統合)、Trial-08
  (No.9全文再生成)を通じて検証された。
- Trial-08実測: A2/B1とも`jargon_found: []`(「regression discontinuity」が使われて
  いないことを確認)、かつ`final_ledger_check`は両レベルとも`LEDGER_COMPLIANT`
  (MAJOR/MINOR 0件)。Fact安全性を損なわずに専門語排除ができることを確認済み。

### 4-5. ユーザー判断

**記録なし**(Storytelling Firstと全く同じ状態。OPEN_ITEMS/DECISION_LOG/
CURRENT_SPECいずれも"jargon"を含む専用記録は0件。(a)(b)は別途記録あり、後述)。

### 4-6. Production反映

- (a) Key Phrase日本語glossの括弧書き禁止: `CURRENT_SPEC.md`(299行目)に記載あり。
  経緯: ER-008-N8-FINAL-QA-HARDENING-21で「A2/B1で共通適用」と記録されたが、これは
  誤りで、実際に修正されたのは研究比較専用モジュール(`er003_key_words_research10.py`)
  のみだった。`ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03`(A)で本番共有validator
  (`er003_key_words_min_unit.py::validate_min_unit_selection()`)へ実際に括弧検知を
  追加し、`PRODUCTION_WIRED`。
- (b) Key Phrase専門語回避: `OPEN-90`として正式記録、`USER_DECISION_REQUIRED`。
  No.9の実際の差替候補("changed suddenly"/「急に変わる」)は提示のみで未反映。
- (c) learner-facing全文No Jargon: **Production反映なし**。Storytelling Firstと
  同一の経路(Trial-08→10→11→12→13)で"Preserve No Jargon."という一文のみが
  `er009_diagnostic_full_retry_modules_12.py`84行目に literal に残存。
  `COMMON_BLOCK_TEMPLATE`には一切反映されていない。

### 4-7. 現行実装

`topic_adapter.py`(Topic候補選定段階、`er002_topic_adapter.py`36行目)に
"Not overloaded with jargon or an excessive number of proper nouns/technical
terms"という記述があるが、これは**News候補記事を選ぶ段階**の基準であり、
Writerが本文を書く際のNo Jargon原則(c)とは**別のパイプライン段階・別目的**である。
混同しないこと。

### 4-8. No.9最終記事との関係

現行No.9本番記事のKey Phrase("regression discontinuity"/"regression discontinuity
design")、本文中の言及("They used a method called regression discontinuity")とも、
専門語がそのまま使われている。No.9最終記事はNo Jargon採用前の状態のまま。

### 4-9. Diagnostic Full Retry内の"Preserve No Jargon."との整合

Storytelling Firstと同じ結論: **不整合が実在する**。初回生成側にNo Jargon原則が
存在しないため、"Preserve"という指示が宙に浮いている。

---

## 5. 3原則Status Table

| Principle | 発端となった問題 | 初回Trial/管理ID | Trial結果 | ユーザー判断 | Production反映タスク | 現行code | CURRENT_SPEC | 現在Status |
|---|---|---|---|---|---|---|---|---|
| Meaning First | No.9 Point Twoの調査レポート化(78/44/66→59/36%の4数値連続読み上げ) | `ER-009-N1-CONTENT-QUALITY-RECALIBRATION-03` Trial-03(`er009_writer_trial_diagnostic_03.py`、意図的に未commit) | 6/6 `LEDGER_COMPLIANT`(MAJOR 0、MINOR 1のみ)。調査レポート感の解消を確認 | `OPEN-91`として正式記録、`USER_DECISION_REQUIRED` | なし | `COMMON_BLOCK_TEMPLATE`に文言なし(grep 0件) | 記載なし | **TRIAL VALIDATED / USER_DECISION_REQUIRED** |
| Storytelling First | 同上(ただしTrial-03自体は「Trial D=実施しなかった」と明記) | Trial-03完了後・同日中の未報告Trial-04/05/08(いずれも`git log`0件、未commit) | Trial-08実測: `LEDGER_COMPLIANT`達成もA2 Point Overlap flagged(0.409/0.542) | **記録なし**(OPEN_ITEMSに項目なし、ユーザー報告の痕跡なし) | なし(Diagnostic Full Retryのretry promptにのみ文言混入、commit `f6ecc1a`で本体配線) | `COMMON_BLOCK_TEMPLATE`に文言なし。`er009_diagnostic_full_retry_modules_12.py`83行に"Preserve Storytelling First."が宙に浮いた状態で存在 | 記載なし | **UNDOCUMENTED TRIAL → PRODUCTION配線コードへの部分的混入(是正要)** |
| No Jargon(learner-facing全文) | 同上 | 同上(Trial-04で新規定義、`JARGON_TERMS`/`detect_jargon()`) | Trial-04/05/08で`jargon_found=[]`を確認しつつ`LEDGER_COMPLIANT`維持 | **記録なし** | 同上 | 同上("Preserve No Jargon."が84行に同様に存在) | 記載なし | **UNDOCUMENTED TRIAL → PRODUCTION配線コードへの部分的混入(是正要)**。Key Phrase括弧禁止(`PRODUCTION_WIRED`)・Key Phrase専門語回避(`OPEN-90`)とは別問題として区別 |

---

## 6. 現行Production Prompt実装状況

| Principle | 明示文言あり | 同義instructionあり | Master/別工程で実現 | 実file/function | コメント |
|---|---|---|---|---|---|
| Meaning First | ✗(0件) | △(部分的・別起源): Spoken-first原則D「1意味ブロックで主要数字2つ以内」は数値圧縮に近い効果を持つが、`commit 17aa9b2`(2026-08-12)由来でMeaning First Trial(2026-08-30)とは無関係。「Evidenceの前にMeaningを決める」という核心指示は存在しない | なし | `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`(188-198行) | 「結果が似ている」ことと「原則が採用されている」ことを混同しないよう注意 |
| Storytelling First | ✗ | △: 阪神マスター記事模倣による「概要→別切り口→一言まとめ」(99-110行)は粒度・focusが異なる別原則(Hook→Meaning→Evidence→Interpretationという4段構成ではない) | なし | 同上(99-110行) | `er009_diagnostic_full_retry_modules_12.py`83行にのみ、初回生成側との対応を欠いた状態で存在 |
| No Jargon(learner-facing全文) | ✗ | ✗(全文レベルの同義instructionなし) | Key Phrase選定段階に部分的関連(OPEN-90)だが、Writer全文の記述には及ばない別工程 | `er009_diagnostic_full_retry_modules_12.py`84行のみ | 唯一の言及がretry pathの宙に浮いた参照であり、初回生成用のCommon Writing Contractには一切存在しない |

「文字列がない=仕様がない」と短絡していない点を明記する: 上記の通りMeaning First・
Storytelling Firstについては、文言としては存在しないが部分的に類似効果を持つ既存
ルールを個別に確認し、それらがTrialに由来しない独立起源であることまで裏付けた。

---

## 7. OPEN-91その他記録との不整合

### 7-1. OPEN-90/OPEN-91のID重複(前回発見の再確認)

`OPEN_ITEMS.md`本文テーブル内で、同一IDが2つずつ異なる内容に割り当てられている
ことを再確認した(ヘッダ4行目の記述とも矛盾がある):

- **OPEN-90**: 45行目=Key Phrase専門語回避Item(`USER_DECISION_REQUIRED`) / 47行目=
  ASR短縮形("'ll"/"'ve")検知ギャップItem(`TBD`)。
- **OPEN-91**: 46行目=Meaning First Item(`USER_DECISION_REQUIRED`) / 48行目=A2 In
  One Line速度Item(`DECIDED`、2026-08-29 ER-24で現状維持確定)。ヘッダ4行目は
  後者(速度Item)を指して「OPEN-91[A2 In One Line速度]を現状維持でDECIDED」と
  記載しており、テーブル上のOPEN-91(Meaning First)とは明らかに別内容。

**今回はID再採番等の修正は実施しない**(タスクスコープ外、かつOPEN_ITEMS.md全体への
影響範囲調査が別途必要なため)。次にOPEN_ITEMS.mdを編集する機会に、重複IDの
再採番を行うことを推奨として記録するに留める。

### 7-2. Storytelling First / No Jargonに対応するOPEN_ITEMが存在しない

本来であれば、Meaning Firstと全く同じ性質(Trial実証済み・Production未反映・
ユーザー判断待ち)の内容であるにもかかわらず、対応するOPEN_ITEMが一件も存在しない。
これは「記録漏れ」であり、`USER_DECISION_REQUIRED`として今回報告するに留める
(タスク16節「Storytelling First/No Jargonの新規仕様追加をしない」という制約を
尊重し、OPEN_ITEMS.mdへの実ファイル追記は行わない。追記の要否自体をユーザー判断
待ちとする)。

### 7-3. CURRENT_SPEC/DECISION_LOGの記録誤り

第10節で詳述(修正実施済み)。

---

## 8. Common / Type-specific分類候補

Editorial Type一般化(Common Writing Contract + Editorial Type Module + Article-
specific Inputs)を見据えた分類候補を、今回の調査結果を踏まえて提案する
(**設計提案のみ、実装は行わない**)。

### Meaning First → Common Writing Contract推奨

News/Trend Synthesisも同種のFact羅列問題(複数のニュース断片・データを単純に並べる
だけになるリスク)を起こす可能性が高いと考えられ(前タスクのER-010-02レポートでも
指摘済み)、「Evidenceを提示する前に、リスナーへ伝える意味を一文で先に決める」という
核はEditorial Type非依存の一般原則として妥当性が高い。

- Common: 「Factを列挙する前に、リスナーへ伝える意味を明確にする」という思考順序
  そのもの。
- Type Module: 「何を意味として選ぶか」の基準は型ごとに異なる
  (Discovery/Why=原因・仕組み・現状、News/Trend=変化の方向性、等)。

### Storytelling First(Hook→Meaning→Evidence→Interpretation) → 即Common化は時期尚早

理由:
1. **ユーザーへ一度も正式報告されていない**ため、この構成原則自体がまだ
   「検証済みの正式候補」とは言えない(Meaning Firstとは扱いの成熟度が異なる)。
2. Trial-08実測で**Point Overlap問題を独立に解決しない**ことが分かっている
   (A2でflag継続)。
3. 「Hook」という導入要素は、既存のPreview/Comment設計(記事本編の前に置かれる
   聞き手の関心喚起要素)と役割が重複する可能性があり、既存要素との整理が
   先に必要。

推奨: まず(a)本監査結果をユーザーへ正式報告してTrial-04/05/08の結果を初めて
共有し、(b)採否を判断してもらった上で、Common/Type Moduleいずれに置くかを
改めて検討する。

### No Jargon(learner-facing全文) → Common Writing Contract推奨

専門用語を避けるという編集判断は、Discovery/Whyに限らずNews/Trend/Voices/Case
Story/Futureのいずれでも共通して成立する、Type非依存の安全原則である。ただし
Key Phrase選定レベルのjargon回避(OPEN-90)とは**別の原則として明確に区別して
定義すること**(前者は「本文全体でどの言葉を使うか」、後者は「どの語をKey Phrase
として選ぶか」という異なる工程・異なる判断)。

---

## 9. No.9 Baseline Git保全結果

**実施した**(ユーザー事前承認済みのため、本監査内で実行)。

- 対象: `er006_output/pool_pilot_01/pool_n9_tip_screens/`(149ファイル)および
  `er009_n1_production_integration_01.py`(本番runner、217行)。両者ともgit未追跡
  (`git status --porcelain`で`??`)であることを確認済み。
- 実施内容: 内容を一切変更せず、新規commit(`512bb78`)として追加。75ファイルが
  実際に追跡対象となった(音声実体`*.wav`74件は既存`.gitignore`ルールにより
  引き続き対象外、`er002_output`等の既存方針と同一の扱い)。
- 事前確認: `raw_usage_log.jsonl`等にAPIキー等の機密情報が含まれていないことを
  内容確認済み。
- **push未実施**(ローカルcommitのみ、タスク指示通り)。
- No.9記事内容・runnerコードとも無変更(このcommitで初めて追跡対象に加えるのみ)。
- Production behaviorへの影響: なし。

---

## 10. DECISION_LOG / CURRENT_SPEC記録訂正結果

第12節の指示に基づき、**記録訂正のみ**(仕様変更ではない)を実施した。

### 訂正対象1: `DECISION_LOG.md`(`ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14`エントリ)

- 訂正前: 「No.9 Ledger 改善: 前回 MINOR 1 件（"growing frustration"...）を修正。
  修正："A 2026 survey found strong consumer resistance to tipping practices" へ
  変更 → MINOR 0 件達成」という記述のみで、実際にNo.9本番記事へ適用されたかのように
  読める。
- 訂正後: 元の記述はそのまま残し(監査証跡として)、直後に訂正の追記を追加。
  実際のNo.9本番記事(`{a2,b1b}/article.md`)には該当フレーズが一切出現しないこと、
  実際の適用対象は無関係な独立診断script・別theme_idのテスト記事だったこと、
  No.9自体の`LEDGER_COMPLIANT`という結論自体は別証拠(実`ledger_deviation.json`)
  により独立に確認済みで変更しないこと、を明記した。

### 訂正対象2: `CURRENT_SPEC.md`(294行目、Diagnostic Full Retry関連のSpec行)

同様に、既存の記述はそのまま残し、同一箇所に訂正の追記を挿入した(内容は上記と同旨)。

両ファイルとも、既存のこの文書自身の慣習(日付付き「追記」を既存文へ追加し、
過去の記述を削除しない)に従って訂正した。

---

## 11. 残るOpen Questions

1. **Storytelling First / No Jargonの正式採否**: 本監査で初めてユーザーへ内容が
   共有される。Meaning Firstと合わせて、3原則すべての採否をユーザーが判断する
   必要がある。
2. **Diagnostic Full Retryの"Preserve Storytelling First."/"Preserve No Jargon."
   の扱い**: 3原則が採用されない場合、この2文はdangling referenceとして
   削除するのが妥当と考えられるが、今回は変更していない(Production Writer
   behaviorの変更を伴うため、ユーザー判断が必要)。
3. **OPEN-90/OPEN-91のID重複**: 再採番が必要だが、影響範囲(他ファイルからの
   参照有無)の調査を伴うため、別タスクでの対応を推奨。
4. **Storytelling First/No Jargonの正式OPEN_ITEMS登録要否**: 今回は記録漏れの
   指摘に留めた。登録するかどうか自体もユーザー判断とする。
5. **Trial-04/05/08がTrial-03のSTOP指示の範囲を超えていた可能性**: Trial-03で
   ユーザーは「原因切り分けのみ実施しSTOP」と明示的に指示したが、同日中に
   実施されたTrial-04/05/08は実際にNo.9記事全文の再生成にまで踏み込んでいる。
   これが指示範囲内の追加検証だったのか、範囲を超えた作業だったのかは、当時の
   会話記録が本監査の対象範囲外(過去セッションの生ログ)にあるため確定できず、
   `USER_DECISION_REQUIRED`ではなく**事実確認自体が困難**な項目として記録する。

---

## 12. Editorial Type一般化へ進む前の推奨Next Step

1. 本報告書(3原則の実際のStatus、特にStorytelling First/No Jargonが未報告
   だった事実)をユーザーへ共有し、採否判断を仰ぐ。
2. 採用する原則が決まった時点で、初めてCommon Writing Contract側の具体的な
   文言設計に着手する(今回は分類候補の提案のみ)。
3. Diagnostic Full Retryのdangling reference("Preserve Storytelling
   First."/"Preserve No Jargon.")の扱い(削除/初回生成側への正式追加/現状維持)を、
   3原則の採否判断とあわせて決定する。
4. OPEN-90/91のID重複を、次のOPEN_ITEMS.md編集機会に解消する。
5. これらの決定が済んだ後、初めて前タスク(ER-010-02)で設計した3層分解
   (Common Writing Contract + Editorial Type Module + Article-specific Inputs)
   の実装、およびNo.9 Regression Test Planの実行に着手する。

---

**Status: PRINCIPLES AUDITED / BASELINE PRESERVED — NO WRITER GENERALIZATION YET**
