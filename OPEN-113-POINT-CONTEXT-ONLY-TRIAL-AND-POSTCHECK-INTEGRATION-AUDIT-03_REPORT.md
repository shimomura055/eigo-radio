# OPEN-113-POINT-CONTEXT-ONLY-TRIAL-AND-POSTCHECK-INTEGRATION-AUDIT-03

管理ID: OPEN-113-POINT-CONTEXT-ONLY-TRIAL-AND-POSTCHECK-INTEGRATION-AUDIT-03
実施日: 2026-09-05
関連: OPEN-113(Local Rewrite Post-Rewrite Intra-Point Redundancy Check)、
Trial-01(`OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01_REPORT.md`)、
Trial-02(`OPEN-113-LOCAL-REWRITE-HIERARCHICAL-CONTRACT-TRIAL-02_REPORT.md`)

到達Status: **VALIDATED**(主Trial)。Production採用・wiringはこのTrial自身のスコープ外
(このTrialで到達してよいStatusの上限もVALIDATEDまで)。

---

## 1. 最終Status

**VALIDATED**

現行Production Local Rewrite契約(`er010_ledger_local_rewrite_09.py`)の
System Prompt・attempt template文言・出力形式・Retry回数・Ledger再チェック
呼び出し方法を一切変更せず、Rewriteモデルへの入力に「対象文が属するPoint
全体」をcontextとして追加しただけで、Trial-01/02が対象とした4ケース全件で
意味重複・過剰修正のいずれも発生しなかった。Trial-01(Prompt契約変更+DELETE追加
を同時実施)・Trial-02(階層Prompt契約を追加)がいずれも解決できなかった問題が、
「Point全体を見せるだけ」という最小限の変更で解決した。

ただし、Production wiringの可否・OPEN-113自体のcloseはこのTrialのスコープ外
であり、ユーザー判断が必要な項目が残る(18節参照)。

---

## 2. Point-context-only Trial結果(サマリ)

| Fixture | 対象文数 | 解決 | 使用Step | Ledger compliant | Word count変化 | API calls | 所要時間 |
|---|---|---|---|---|---|---|---|
| No.18 B1既知重複ケース | 1 | 1/1 | REWRITE(attempt1) | ○(major=0) | 75→87語 | 3 | 44.2s |
| No.9 regression(2件) | 2 | 2/2 | REWRITE(attempt1) | ○(major=0) | 94→107語 | 5 | 70.2s |
| No.18 A2 regression | 1 | 1/1 | REWRITE(attempt1) | ○(major=0) | 39→39語 | 3 | 117.2s |
| **合計** | **4** | **4/4** | 全てREWRITE、DELETE不使用(現行Productionに機能自体なし) | **4/4 major=0** | — | **11** | 231.6s |

4件全てが**初回attemptで解決**した(Retryへ進んだケースはゼロ)。現行
Productionには`DELETE_SENTENCE`という機能自体が存在しないため、削除は
起こり得ない構造になっている(Trial-01/02はDELETEをTrial専用契約として
新規追加していたため今回とは前提が異なる、後述11節)。

---

## 3. No.18 B1(既知重複ケース)

対象文: `"Clear response windows could ease it."`
(Ledger: 10代の多数派が即時返信の必要を感じると回答しているだけで、
明確な返信時間帯を設けることで圧力が軽減されるとは検証していない)

- **今回の出力**: `"Setting clear response windows might help ease that pressure, although the survey did not test whether it does."`
- 同じPoint内の既出文 `"A majority felt a need to reply quickly."` とは意味が
  異なる(前者は「対策が効くかは未検証」という限定を明示、後者は「即時返信の
  必要性を感じる」という調査結果そのもの)。**言い換え重複は発生しなかった**。
- Ledger compliant(1回目のattemptでLEDGER_COMPLIANT)。
- 全文再判定(full recheck): `LEDGER_COMPLIANT`、MAJOR=0。
- 追加の安定性確認として、同じ`new_article`に対しもう一度独立に全文判定を
  実行(judgment揺れの切り分け、7節で許可された追加1回)。結果は同じく
  `LEDGER_COMPLIANT`、MAJOR=0で**再現した**(詳細は17節)。

Trial-01はこの同じケースでDELETEを選び解決、Trial-02は3回試行しても解決
できず「未解決」のまま終了した。今回はREWRITEで、かつ重複なしで解決した。

---

## 4. No.9 #2("tired of being guided by the screen")

対象文: `"But they show that many customers are becoming tired of being guided by the screen."`
(Ledgerは調査結果[不合理という認識・チップ減少の自己申告・カスタム額選択]
を保証するのみで、「画面に導かれることに疲れている」という心理状態の直接
測定はない)

- **今回の出力**: `"But they suggest that many customers may be pushing back against suggested tip rates and digital prompts."`
- 直前の文 `"These are survey answers, not proof that the screen caused the change."` との整合を保ちつつ、因果ではなく「示唆」「かもしれない」という
  確実性レベルへ調整。同じPoint内の他文(78%が不合理と回答、44%がチップを
  減らした、36%がカスタム額を選択)とも意味が重ならない。
- Trial-01・Trial-02は共にこの文をDELETEしていた(過剰削除)。今回は
  安全なREWRITEで解決し、**過剰削除が発生しなかった**。

---

## 5. No.18 A2("always"→certainty softening)

対象文: `"“I did not check it” does not always mean “it had no effect.”"`

- **今回の出力**: `"“I did not check it” does not necessarily mean “it had no effect.”"`
- 「always」→「necessarily」という**最小1語修正**。word count前後とも39語で
  完全一致(内容の水増し・縮退が発生していないことの直接的な裏付け)。
- これはOPEN-113着手前の履歴ベースライン(過去の正常Production実行結果)と
  ほぼ同じ最小修正であり、Trial-01・Trial-02が共に到達できなかった結果。

---

## 6. No.9 #1(scope条件の明記)

対象文: `"The feeling of “I must leave a tip” also fell, from 66 percent in September 2025 to 59 percent in 2026."`

- **今回の出力**: `"The share of respondents who said they felt they had to leave a tip when a digital screen prompted one fell from 66 percent in September 2025 to 59 percent in 2026."`
- Ledgerが保証する「デジタル画面がチップを促すとき」という条件を明記し、
  数値・比較方向は変更なし。Trial-01/02と同様、このケースは非診断的な
  コントロールケース(3Trialとも一貫してREWRITEで解決)。

---

## 7. 重複解消

4件中、意味重複が懸念されていたのは主にNo.18 B1(3節)。今回のRewrite文は
同一Point内のどの既出文とも意味が重ならないことを目視確認した。また
`duplication_notes`(報告用の参考指標、新Validatorではない)で各Rewrite後文と
同一Point内の他文数を記録したが、これは正式な自動判定ではなく、あくまで
目視確認の補助である(15節)。

**結論: 4件全てで重複は発生しなかった。**

---

## 8. 正常Rewrite維持

No.9 #1・#2、No.18 A2の3件はいずれも「過去に成立していた正常なREWRITE」を
壊さずに再現(または同等の安全な代替)できた。DELETE・大幅な意味変化・
別Factへの置換はいずれも発生していない。

**結論: 正常ケースの退行はゼロ。**

---

## 9. Ledger compliance

4件の対象文は全てattempt1でLEDGER_COMPLIANT。3fixtureの全文再判定も
全て`LEDGER_COMPLIANT`・MAJOR=0(MINORのみ残存、いずれもRewrite対象と
無関係な既存の軽微な逸脱で、Trial-01/02でも同様に検出されていたものと
同種)。

**結論: Ledger compliance 3/3 fixture、4/4 item。**

---

## 10. API call増減

| Fixture | api_call_count |
|---|---|
| No.18 B1 | 3 |
| No.9 regression | 5 |
| No.18 A2 | 3 |
| 合計(主Trial) | 11 |
| 追加(disambiguation recheck 1回) | 1 |
| **セッション合計** | **12** |

呼び出し回数の計算式は現行Production(`rewrite_ng_item`のescalation構造:
1attempt=generate 1回+check 1回、最大3attempt+全文再判定1回)と完全に同一
であり、新たな呼び出し経路は追加していない。全item が attempt1 で解決した
ため、この計算式が許容する**理論上の最小回数**で完了した。

**結論: API call増加なし。**(現行Productionの計算式のまま、追加なし)

---

## 11. 「Point全体を見せるだけ」で十分か

**十分だった、というのが今回の4件における結論。**

Trial-01は「Point context追加」と「Prompt契約変更(DELETE追加等)」を同時に
行っていたため、Point context単独の効果を評価できていなかった
(背景1節)。今回、Prompt契約(Rule文言)を一切変えず、Point context追加
のみを変数として切り出した結果、Trial-01/02が抱えていた2つの問題
(過剰DELETE、既知重複ケースの重複再発/未解決)がどちらも発生しなかった。

考えられる理由(推測、確定的な因果証明ではない):
- Trial-01/02はDELETEという新しい選択肢自体を導入しており、モデルが
  「安全側に倒す」ならDELETEへ流れやすい構造だった。今回はDELETE機能が
  現行Productionに存在しないため、モデルは必然的にREWRITEで解決する
  しかなく、その際にPoint全体という情報があることで、既出文と重ならない
  安全な言い換えを見つけやすくなった可能性がある。
- 現行ProductionのRule文言(1〜9)は既に「元の意図を保て」「central pointを
  保て」「他の文を変えるな」等、REWRITE指向の明確な指示を持っており、
  そこにPoint全体という「見える情報」が加わったことで、モデルが実際に
  その指示を実行しやすくなった可能性がある。

ただし4件のみのTrialであり、対象文4件・fixture3件という小規模サンプルで
ある点はサンプルサイズの限界として明記する(19節・20節)。

---

## 12. 既存Ledger recheck構造

調査対象: `er003_v1_en_direct_vfl_01_generate.py`の`run_deviation_check()`
(603〜626行目)。

- 入力: `verified_ledger_text` + `article_text`(呼び出し元が渡すテキストの
  範囲は呼び出し箇所ごとに異なる、後述)+ `hook_aware`フラグ。
- 出力スキーマ: OpenAI Responses APIの`json_schema`(`strict: True`,
  `additionalProperties: False`)。`deviations`配列のみを返す構造で、各要素は
  `claim_in_article` / `issue` / `severity`(MINOR・MAJOR) / 10種類のboolean
  flag(`changed_fact`等) / `explanation`(+ hook-aware版は`treated_as_hook`)。
- `overall_status`はモデルの自己申告ではなく、`_apply_deviation_post_hoc_
  validation()`がPython側でMAJORの有無から計算する(513〜530行目)。
- **呼び出し箇所が2種類あり、渡している`article_text`の範囲が異なる**:
  1. Local Rewriteのescalation loop内の`run_check_window_fn`
     (`er010_ledger_local_rewrite_09.py`経由): 対象文の前後1文だけの
     小さな窓(3文程度)。**Point全体は渡っていない。**
  2. Rewrite cycle後の「全文再判定」: 記事全体(`article_text`)を渡す。
- developer message(`DEVIATION_DEVELOPER_MESSAGE`)は明示的に「記事の
  面白さやスタイルは評価せず、意味上のFactがLedgerの範囲内に収まっている
  かだけを判定してください」と指示しており、Fact Safety以外の評価軸を
  意図的に排除する設計になっている(ER-009-N1-LEDGER-DEVIATION-
  RECALIBRATION-02: paraphrase・簡略化・bridge sentenceの誤検知を無くす
  ために意図的にこの範囲へ絞り込んだ経緯がコード内コメントに記録されている)。
- 呼び出し元(`er003_v1_n3_01_articles_generate.py`)は`overall_status`と
  `deviations[].severity` / `claim_in_article`のみを参照しており、スキーマの
  他フィールドには依存していない。

---

## 13. 品質判定統合の実現可能性

**判定: B. FEASIBLE_BUT_RISKY**

技術的に可能な部分と、リスクが残る部分を分けて報告する。

**可能な部分**:
- 「全文再判定」の呼び出し箇所(12節の2)は既に記事全体を受け取っている
  ため、そこにquality判定を追加すること自体はAPI呼び出し回数を増やさずに
  実現できる可能性がある。

**リスク・制約**:
- `strict: True` + `additionalProperties: False`のJSON Schemaのため、
  新しいフィールド(例: `semantic_duplication`)を追加するには**必ず
  スキーマ定義の変更が必要**(=Production code変更。今回禁止事項に該当し、
  今回は実装していない)。「call数を増やさない」ことと「Production変更なし」
  は別軸であり、両立させるには次のTrialでの正式な変更提案が必要。
- Local Rewrite escalation loop内の窓チェック(12節の1)はPoint全体を
  見ていないため、**そのチェック箇所で意味重複を検知することはできない**。
  重複を実際に防ぐ役割は担えず、全文再判定の段階で「後から気づく」ことしか
  できない(手遅れ、もう一度cycleを回す以外の是正手段がない)。
- developer messageが意図的にFact Safetyのみへ判定を絞り込んだ経緯
  (12節)があり、意味重複・flow・情報欠落という異なる種類の判定を同じ
  callへ混在させることは、この意図的な絞り込みに反する。今回のTrialで
  再確認したLedger判定揺れ(17節)を悪化させるリスクは否定できないが、
  今回はread-only調査のみのため、実際に悪化するかどうかは未検証
  (D. UNKNOWNの要素も残る)。

---

## 14. 推奨する最小品質判定

**今回時点での推奨: 新たな品質判定は追加しない。**

主Trial(2〜11節)の結果、OPEN-113の本質的な問題(意味重複)は、Ledger
recheckへ新しい判定軸を追加しなくても、Local Rewrite生成側にPoint context
を渡すだけで4/4件が解決した。この結果を踏まえると、複雑さとリスクを伴う
「Ledger recheckへの品質判定統合」を今の時点で急いで導入する必然性は低いと
判断する。

もし将来、Point context追加をProductionへ正式採用した後にOPEN-113相当の
問題が別のケースで再発した場合に限り、候補として
**SEMANTIC_DUPLICATION単体**(POINT_FLOW_BROKEN・INFORMATION_LOSSは含めない)
を、既存Ledger recheckとは**別の**軽量チェックとして検討する余地がある
(ただしその場合はAPI call追加を伴う新Trialとしての提案が必要)。

---

## 15. 追加API callなしで可能か

**部分的にのみ可能、全体としてはUNKNOWN。**

- 全文再判定の箇所だけであれば、call追加なしでの統合は技術的に可能
  (13節)。
- しかしLocal Rewrite escalation loop内での重複「予防」(発生後の検知
  ではなく)を実現するには、そのチェック窓へPoint全体を渡す入力変更が
  別途必要になる(これ自体はcall追加ではないが、今回の主Trialとは別の
  設計変更であり、read-only調査の範囲を超える)。
- 結論として、「品質判定を追加API callなしで完全に統合できるか」は
  現時点でUNKNOWN。全文再判定への追加だけならcall増加なしで可能という
  限定的な答えに留まる。

---

## 16. 既存QAとの責務重複

- **Point Overlap QA**(`er008_point_overlap_qa_18.py`): Pointの内容語と
  **Full Story(記事の別セクション)** とのJaccard係数による字面ベースの
  重複検知。LLM不使用。**比較対象がPoint間(Point vs Full Story)**であり、
  今回の問題(同一Point内の文同士の重複)とはスコープが異なる。
- **Point Value QA**(`er011_point_role_value_planning_01.py`):
  記事執筆**前**の計画段階で、Point One/TwoとFull Storyの役割・価値を
  比較するQA。実行タイミングがLocal Rewrite後ではなく執筆前であり、
  今回の問題とはタイミング・目的の両方が異なる。

**結論**: 「Rewrite後、同一Point内の文同士が意味的に重複していないか」を
チェックする機構は現状どこにも存在しない。品質判定統合を検討する場合でも、
既存QAとの機能重複は発生しない(新しい責務の追加になる)。

---

## 17. Ledger判定揺れへの影響

Trial-01・Trial-02で見つかっていたLedger Deviation Checkerの判定揺れ
(同一記事に対する判定結果が実行ごとに異なりうる、未登録のOPEN-114候補)
について、今回も以下の観察を追加で得た(修正は行っていない、9節の
規定どおり):

- No.18 B1の`new_article`(3節)に対する全文再判定を、独立した2回目の
  API呼び出しとして実行(disambiguation目的、Loop Budgetで許可された
  追加1回)。**結果は1回目と同じ`LEDGER_COMPLIANT`・MAJOR=0で再現した。**
  今回のTrial-03自身の結論(VALIDATED)は、この点で単発の偶然ではなく
  安定した結果であると確認できた。
- 一方、Trial-02では同じPointを含む記事(ただし未解決のまま=元文が残った
  状態)に対する全文再判定で、`"Everyday expectations can make ignoring
  it feel difficult."`という、今回のRewrite対象とは無関係な一文が
  MAJORとして検出されていた。今回のTrial-03では同じ趣旨の一文(Rewrite後
  記事内に`"while everyday expectations can make ignoring it feel
  difficult"`という節として存在)が2回ともMAJORとして検出されなかった。
  記事の状態(Rewrite対象文が解決済みか否か)が異なるため厳密な同一
  条件比較ではないが、**同じ論点について3回目(Trial-01・02・03)の
  観察が集まったことになり、判定揺れが実在する可能性を引き続き示唆
  している**。
- この論点はOPEN_ITEMS.mdに独立した行としてまだ登録されていない
  (確認済み)。今回もユーザー承認なしに新規登録・実装は行っていない。
  仮ID OPEN-114として、報告のみ据え置く。

13節で述べたとおり、Ledger recheckへ品質判定を統合する場合はこの判定揺れが
リスク要因になりうる。

---

## 18. USER_DECISION_REQUIRED(次に進む前にユーザー判断が必要な項目)

主Trial自体はVALIDATEDだが、以下はこのTrialのスコープ外(Production
wiring禁止、新Validator禁止)のため、ユーザーの判断を仰ぐ。

**(a) Point-context-only方式のProduction採用検討へ進むか**
今回4/4件で成功したが、対象は依然としてTrial-01/02と同じ4ケース(3
fixture)のみ。Production wiring(`er010_ledger_local_rewrite_09.py`・
`er003_v1_n3_01_articles_generate.py`への実装)を正式に検討するには、
別途「Production変更を伴う提案・実装Trial」を新規に依頼いただく必要がある。

**(b) OPEN-114候補(Ledger判定揺れ)を正式登録・調査するか**
今回で3セッション連続の観察となった。正式なOpen Item登録・原因調査を
別タスクとして依頼するか、このまま非公式の観察に留めるか。

**(c) Ledger recheckへの品質判定統合(9〜17節)を追加Trialとして依頼するか**
今回の推奨(14節)は「今は不要」だが、将来的にPoint context方式単独では
防ぎきれないケースが見つかった場合に備え、SEMANTIC_DUPLICATION単体の
軽量チェックを別途検討する選択肢を残すか。

**(d) 何もせず、今回の結果を記録のみに留めるか**
OPEN-113をこのままOpenのまま維持し、次のアクションは行わない。

---

## 19. Production変更なし確認

- `er010_ledger_local_rewrite_09.py`: 未変更(importして参照のみ、
  `REWRITE_SYSTEM_PROMPT`の同一性を機械的に検証済み)。
- `er003_v1_n3_01_articles_generate.py`: 未変更。
- `er003_v1_en_direct_vfl_01_generate.py`(Ledger recheck): 未変更
  (read-only調査のみ、コード変更なし)。
- 新規作成したのはTrial専用ファイル`er011_open113_point_context_only_
  trial_03.py`と、その出力(`er011_output/open113_point_context_only_
  trial_03/`)、および本報告書のみ。
- `CURRENT_SPEC.md`: 変更なし。
- `OPEN_ITEMS.md`: OPEN-113の既存行へ今回の結果を追記のみ(close・新規
  行追加はしていない)。

**結論: Production code・Prompt・schemaのいずれも変更していない。**

---

## 20. 次アクション

このTrial自身としての次アクションはない(「Trial結果報告後STOP」の
指示どおり、本報告後は追加のTrial・実装・Production変更提案のいずれも
自発的には行わない)。18節の(a)〜(d)のうち、ユーザーがどれを次に進めるか
判断されるのを待つ。

---

## まとめ

今回Status: VALIDATED(Point-context-onlyのTrial自体は成功、Production採用可否は別判断)
OPEN-113: Open継続(closeせず、Trial-01・02・03の結果をOPEN_ITEMS.mdへ追記済み)
Point-context-only: 4/4件で成功(重複解消・正常Rewrite維持・Ledger compliant、全てVALIDATED)
Rewrite Prompt変更: なし(現行ProductionのSystem Prompt・Rule文言を一字一句変更せず、Point context追加のみ)
追加QA実装: なし(read-only調査のみ、実装は行っていない)
Ledger recheck品質統合: 実現可能性はFEASIBLE_BUT_RISKY(13節)。今回は実装せず、推奨は「今は追加しない」(14節)
追加API call: なし(現行Productionと同一の呼び出し回数計算式のまま、disambiguation用に主Trial外で1回のみ追加実行)
Production変更: なし
次に進めてよい工程: なし(18節のユーザー判断待ち)
