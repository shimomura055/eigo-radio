# OPEN-233 Evidence開示: neg1 / neg3 / hormuz_run03_standard(委任_26)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_26、既存Evidenceの実文開示。
新規API課金・Trial実行・コード変更・SSOT変更なし、¥0)。
読み取りのみ。json本文に無い情報は「記録なし」と明記し、推測で埋めない。

---

## 1. neg1(`neg1_meta_b3prod_a2`、iter7で不要Rewriteとして残った run)

対象記事: Meta Muse human-concierge記事(MUSE-HC-006/012)。`expected_
group_label`は`ACCEPTABLE(Normal群、§7-5)`=本来Rewrite 0件が正解の
負例群。iter7ではsample1(`instances_s1`)とsample2(`instances_s2`)が
**同一fixtureで正反対の結果**になった(n=2の非決定性の直接証拠)。

| | sample1(s1、不要Rewrite発生) | sample2(s2、正しく無Rewrite) |
|---|---|---|
| `final_state` | `STAGE4_ESCALATION` | `RESOLVED_STAGE2_DOWNGRADE` |
| `stage4_reason` | `ja_deviation_unresolved` | (該当なし) |
| cycle1 hook claim 2巡目判定 | BLOCKING(両者一致) | ACCEPTABLE(1巡目BLOCKING→2巡目降格) |
| 費用/call数 | ¥3.8708 / 20 call | ¥0.1875 / 2 call |

### 対応するLedger確認済みFact(逐語)

- **MUSE-HC-006**(`er019_output/family_x_refresh_e2e_01/meta/run_03/
  ledger/verified_fact_ledger.txt` L31-35): 「MetaはMuse経由の電話の
  一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、
  相手とのやり取りを完了させる「human concierge」「human agent
  calls」のテストを実施した。」scope:「Muse経由で発信された電話の
  一部」。conditions:「Museから人間の訓練済みエージェントへ依頼が
  引き渡されるテスト条件」。notes_for_writer:「全ての電話を人間が
  担当したとは書かない。「一部の電話」「テスト」と限定する。」
- **MUSE-HC-012**(同L74-78): 「MetaのSuperintelligence Labs部門の
  副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始
  したことを「ミス」だったと認め、機能を当面ロールバックしたと社内
  投稿で説明した。」scope:「Meta社内テストの人間コンシェルジュ機能」。
  conditions:「適切な開示なしで契約スタッフが電話を担当していた
  テスト」。notes_for_writer:「「サービス全体を停止した」とは書かない。
  ロールバック対象は人間コンシェルジュ機能として扱う。」

### Rewrite前の実際の英文(該当文と前後1文、cycle1 hook)

> Ring, ring. **A call seemed to come from an AI agent. But as the
> conversation went on, the voice was not AI at all. It was a
> person.** Meta had run a test that caused exactly this surprise.

### Stage 1(Checker)が問題と判定した表現とissue文(逐語)

- `claim_in_article`: “A call seemed to come from an AI agent. But
  as the conversation went on, the voice was not AI at all. It was
  a person. Meta had run a test that caused exactly this surprise.”
- `issue`: “The article presents a recipient discovering during a
  call that a person, not AI, was speaking, and says the test caused
  this surprise. The Ledger verifies that trained contract workers
  made some Muse calls, but does not establish that recipients
  experienced this reveal.”

### Stage 2の判定(materiality・basis逐語、Hook専用Stage2経由の有無)

- `section_type`: `hook` / `stage2_route`: `hook`(Hook専用Stage2
  rubricを経由。対象範囲外だったための誤判定ではない)。
- s1: 1回目`materiality: BLOCKING`(`basis: unsupported_relationship`)、
  2回目(`stage2_two_of_two_log`)も`"first_materiality": "BLOCKING"`
  `"second_materiality": "BLOCKING"` `"two_of_two_result":
  "BLOCKING(both agree)"` → Rewriteへ進行。
- s2: 1回目`materiality: ACCEPTABLE`(記録上`llm_materiality:
  BLOCKING`だが1巡目判定自体は`materiality: ACCEPTABLE`)、
  `two_of_two_downgraded: true`、`two_of_two_second_materiality:
  ACCEPTABLE`、`"two_of_two_result": "DOWNGRADED(1/2 non-blocking)"`
  → Rewrite不要のままRESOLVED。
- `floor_reason: null`(既存floor[changed_actor/number/negation/
  comparison/time]のいずれにも該当しない、floorが強制したBLOCKING
  ではない)。

### Rewriteへ送った理由(発火条件)

s1では2-of-2判定が両者ともBLOCKINGで一致したため(floor不介在、
純粋にStage2 LLM判定が2回ともBLOCKING)、`rewrite_kind: narrow_scope`
でStage3 Rewriteへ進んだ。s2では2回目の判定が非BLOCKINGへ振れた
ため、同一rubric・同一fixtureのままRewrite自体が発火しなかった。

### Rewrite後の実際の英文(cycle1、s1)

> Ring, ring. **Some Muse calls were handled not by AI, but by
> trained contract workers.** Meta had run a test that caused exactly
> this surprise.

`rewrite_hint`(逐語): 「対象文: “A call seemed to come from an AI
agent. But as the conversation went on, the voice was not AI at all.
It was a person.” ユーザーがAIだと思い、会話の途中で人間だと気づいた
という具体的な体験は示さず、「Muse経由の電話の一部を訓練を受けた
人間の契約スタッフが担当したテスト」と確認済みの範囲に狭めてください。
参照: MUSE-HC-006」

`ladder_level_used: "3_sentence"`(mechanism `single_text_local
(E-2/delete-generic)`, method `e2_generic_rewrite`)。

### cycle2(MUSE-HC-012、origin=ja_source、s1のみ)

- 検出された2 claim(いずれも`floor_reason: "deterministic_floor:
  changed_actor"`でLLM単独判定[QUALITY/ACCEPTABLE]をfloorが
  BLOCKINGへ強制):
  - `claim_in_article`: “The test began without clearly telling
    users that contract workers would make the calls.”
    `issue`: “The article says users were not clearly told, whereas
    the Ledger describes an internal test involving Meta employees
    and does not establish that Muse users generally were the
    audience that lacked disclosure.”
  - `claim_in_article`: “A Meta executive admitted the mistake. The
    test had begun without clearly telling users.”(同issue)
- Rewrite後(J-1、`ladder_level_used: "1_word_connective"`、method
  `j1_e1_minimal_word`、3レコード):
  - EN Before: “Here was the reveal. The test began without clearly
    telling **users** that contract workers would make the calls.
    A **user** might think the exchange was with AI, even though a
    person was involved.”
    EN After: “Here was the reveal. The test began without clearly
    telling **employees** that contract workers would make the
    calls. A person was involved.”
  - EN Before2: “A Meta executive admitted the mistake. The test had
    begun without clearly telling **users**.”
    EN After2: “A Meta executive admitted the mistake. The test had
    begun without clearly telling **employees**.”
  - JA Before: 「しかも今回は、契約スタッフが電話をかけることに
    ついて、適切な説明が十分にないまま**テスト**が始まりました。
    **利用者にはAIとのやり取りに見えても、実際には人間が関わって
    いる場合があったのです。**」
    JA After: 「しかも今回は、契約スタッフが電話をかけることに
    ついて、適切な説明が十分にないまま**社内テスト**が始まりました。
    **人間が関わっている場合があったのです。**」
  - JA Before2: 「Metaの幹部は、適切な開示なしに**この**テストを
    始めたことを「ミス」と認めました。」
    JA After2: 「Metaの幹部は、適切な開示なしに**社内の**テストを
    始めたことを「ミス」と認めました。」
- `ja_en_equivalence_verdict: "REVIEW_REQUIRED"`、
  `full_recheck_required_reasons`: `multiple_claims_rewritten_
  same_cycle` / `deterministic_floor_claim` / `ja_en_equivalence_
  not_pass`。`recheck_overall_status`(EN): `LEDGER_DEVIATION`、
  `ja_recheck_overall_status`: `LEDGER_DEVIATION`。

### cycle3(title claim、非blocking)

`claim_text: "We Thought It Was AI"`、`materiality: QUALITY`、
`blocking_count: 0`、`non_blocking_count: 1`。新規Rewriteは発火せず、
それでも最終的に`STAGE4_ESCALATION(ja_deviation_unresolved)`へ
到達した(cycle2のJA等価判定`REVIEW_REQUIRED`によりja_okが確定
解消されないまま持ち越されたため。§3Dで解説する
`resolve_ja_ok_after_equivalence_gating`と同一機構)。

### iter7のもう1 run・rep11・rep12の同claim判定比較

| Run | MUSE-HC-006 hook claim判定 | Rewrite発火 |
|---|---|---|
| rep11(委任_20、2/2 sample) | 2/2ともBLOCKING | 2/2ともRewrite |
| rep12(コード変更なし再実行、2/2 sample) | 2/2とも`RESOLVED_STAGE2_DOWNGRADE`(非BLOCKING) | 0/2 |
| iter7 s1 | 2-of-2両者BLOCKING一致 | Rewrite発生 |
| iter7 s2 | 1巡目BLOCKING→2巡目ACCEPTABLEへ降格 | Rewrite発生せず |

同一rubric・同一fixtureでBLOCKING/非BLOCKING双方が複数回実測されて
おり、コードのバグではなくLLM判定の閾値付近にある真の境界事例である
ことを裏付ける。

### 委任_21 A-3の「disputed」判定根拠(`design_open233_self_recovery_
flow_01.md` L1160-1228より逐語引用)

> **(b)許容線の判定**: Ledger factは「一部のMuse経由電話を人間スタッフ
> が担当するテストを実施した」という構造的事実のみを確認しており、
> 「ある特定の通話で、会話の途中にAIだと思っていた相手が実は人間
> だったと気づく驚きの瞬間」という受け手視点の具体的な体験・出来事
> までは確認していない。Hook専用Stage2 rubric(§4-14)のBLOCKING条件
> (a)「新しい具体的な人物・数字・出来事・行動・仕組みの発明」に文字
> どおり当てはめれば、「会話中に気づく」という具体的な展開の発明と
> 読める。一方、記事タイトル自体が「We Thought It Was AI—But There
> Was a Person Inside Meta's Muse」であり、この一文はHookの核となる
> 同一主題の劇的表現(情景描写に近い演出)とも読め、rubricのtie-break
> 規定「迷う場合は発明の有無で判定し、発明がなければQUALITYとする」
> の境界上にある。本claimは委任文基準(a)〜(d)のいずれにも機械的に
> 該当するが、rubric自体が想定する「演出として許容すべき誇張のない
> 強調」との境界が曖昧な、真にdisputedな事例と判定する。
>
> **結論**: 本claimはコードのバグや既存条件の誤適用ではなく、Hook専用
> Stage2 rubric自体が抱える「物語的な劇的表現」と「具体的な出来事の
> 発明」の境界上のdisputed事例と判定する(既存の`neg3_hormuz_
> prodrunner_b1b`と同種の扱い)。コード変更は行わない(rubric・floor
> 条件のいずれも変更しない)。

### 現在の再発防止策候補と、防げる理由・防げない範囲

候補として設計書が挙げているのは「rubric tie-break文言の明確化
(『会話中の気づき』のような物語的展開を演出側へ明示的に含めるか)」
のみで、これは**Fable/ユーザー判断待ちのOPEN_ITEMS事項**(本委任では
コード変更禁止のため未実装)。

- **防げる範囲**: 本claim(Hook区分・「AIだと思ったら人だった」という
  肯定形の劇的展開)と同型の、Hook専用Stage2 rubric境界上のdisputed
  claimに限る。
- **防げない範囲**: neg3/hormuz型(スコープ拡張=`changed_scope`
  floor起因のBLOCKING)には無関係(rubric tie-break文言とは別の
  決定論floor機構で判定されており、Hook rubric側の文言修正では
  影響を受けない)。また、rubric文言を緩めればneg1は改善する可能性が
  ある一方、Opus指摘(design doc記載)のとおり`bgroup_B3`のような
  Safety-critical回帰への波及リスクがあり、一般化は推奨されていない。

---

## 2. neg3(`neg3_hormuz_prodrunner_b1b`、iter7で2 runとも Rewrite)

対象記事: ホルムズ海峡20%手数料案撤回後の原油価格記事(HF-009)。
`expected_group_label`は同じく`ACCEPTABLE(Normal群、§7-5)`。iter7は
sample1・sample2とも同一claimで`RESOLVED_REWRITE`(2/2 Rewrite発生・
2/2解消)。

### Rewrite前の実際の英文(In one line全文+本文中の対応箇所)

- `section_type: in_one_line`、`claim_text`(In one line全文):
  > The fee plan left the stage, but the events driving oil prices
  > —and the prices themselves—quickly returned.
- 本文中の対応箇所(整合していた記述、同記事本文):
  > During that period, attacks between the United States and Iran,
  > a sea blockade, and concerns about tanker safety **continued**.

### 対応するLedger HF-009(逐語)

`er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/
verified_fact_ledger.txt` L58-64:

> [VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への
> 置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく
> 発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は
> 約2.6％高で、1バレル85ドルを上回っていた。
> scope: 国際指標Brent原油先物の短時間の値動き
> conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、
> タンカー安全上の懸念が**継続していた**。
> causal_strength: CAUSAL_STATED_BY_SOURCE
> notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。
> 観測されたのは一時的な上げ幅縮小と、その後の回復。

### Stage1のissue逐語(flags)

- `issue`: “The sentence describes the events as having quickly
  returned and as driving oil prices, whereas HF-009 reports that
  relevant attacks, blockade and tanker-safety concerns continued
  during the price movement. It changes continued events into
  returning events and asserts a causal role not established by the
  Ledger.”
- flags: `changed_fact: true` / `changed_causality: true` /
  `changed_time: true` / `unsupported_new_claim: true`(他flagは
  false)。`severity_final: BLOCKING`、`basis: ledger_conditions`
  (s1)/`ledger_scope`(s2、run間でbasisフィールドがぶれるが両方とも
  BLOCKING判定は一致)。
- `floor_reason: "deterministic_floor:changed_time"`(決定論floor
  起因、s1・s2とも)。

### Stage2のmateriality・basis逐語

`materiality: BLOCKING`、`llm_materiality: BLOCKING`(LLM自身も
floorと独立に一致)。`rewrite_hint`(s1逐語):「「The fee plan left
the stage, but the events driving oil prices—and the prices
themselves—quickly returned.」から、出来事が「returned」とする部分を
外し、価格の一時的な上げ幅縮小後の回復だけを述べてください。HF-009
では、攻撃・海上封鎖・タンカー安全上の懸念は継続していたとされて
います。」

### floorの種類

`deterministic_floor:changed_time`(ユーザーNG5項目の1つ、時制/
status[継続 vs 終息]の直接反転)。

### 2 runそれぞれのRewrite後の英文とラダー段・費用

両runとも`ladder_level_used: "1_word_connective"`(method
`e1_minimal_word_edit`)。

- s1 After(In one line): “The fee plan left the stage, but the
  prices themselves quickly returned.”(¥0.8075、5 call)
- s2 After(In one line): **同一文字列**“The fee plan left the
  stage, but the prices themselves quickly returned.”(¥0.6289、5 call)

JA側: `origin: translation`(JA sourceではなくEN翻訳由来のclaim)の
ため、対応する`ja_text_before/after_rewrite`はこのcycleでは記録上
本文全体のJA/EN対比フィールドとしては変化なし(In one line文自体は
記事内でEN版のみ独立管理、rewrite自体は`single_text_local`ではなく
`rewrite_kind: narrow_scope`のE-1最小編集)。

### 2 runが同じ入力文の再実行であることの明示

s1・s2とも`claim_text`・`related_fact_id`(HF-009)・`local_context`
(In one lineセクション全体)が完全一致し、`rewrite_hint`の文言のみ
run間で言い換えが異なる(s1「対象範囲」重視、s2「narrow the price
movement to Brent futures」）。Rewrite後の英文は**文字列として完全
一致**しており、同一入力に対する独立再実行(n=2)であることが確認
できる。`recheck_confirm_all_prior_issues_resolved: true`
(s1、`cite_or_release_released_count: 0`)。

### Opus #4 Q2の判定理由(`opus_l2_review_open233_self_recovery_04.md`
L133-143より逐語引用)

> **判定: BLOCKINGが妥当。ユーザー許容線を根拠にQUALITYへ落とすこと
> はできない。**
>
> - 因果部分(「the events driving oil prices」)→ 許容範囲。ユーザー
>   の例示「市場が海上リスクを重視したから価格が戻った」とほぼ同型で、
>   確認済みFact(海上リスク事象の継続/価格の回復)を人間が自然に
>   つなぐ解釈です。ここだけならQUALITY。
> - 時制・状態部分(「the events ... quickly returned」)→ NG側。
>   Ledger `conditions`は「継続していた(continued)」と明記して
>   います。「returned」は「いったん去った後に戻ってきた」を含意し、
>   確認済み条件と逆方向です。これは解釈差ではなく状態の反転で、
>   ユーザーNGリストの「timeの重大変更」「Factと逆方向」に当たります。
> - 統語的な逃げ道は弱い。「the events ... —and the prices
>   themselves— quickly returned」は2つの主語が同一VPを共有する
>   並置で、最も自然な読みでは両方が「returned」します。
> - 記事内整合からも裏付け。同記事本文は「けれど、海峡をめぐる緊張に
>   関するニュースは、舞台に残ったままです」(= stayed)と書いており、
>   in_one_lineだけが「returned」に反転しています。記事自身が
>   「継続」と言っているので、これは表現差ではなく要約時の事実変形
>   です。
> - 判定の安定性。rep10で2/2とも`llm_materiality: BLOCKING`かつ
>   `floor_reason: deterministic_floor:changed_time`、委任_19のn=3
>   でも3/3 BLOCKING。iter4/5のQUALITYは少数派で、floorを外しても
>   LLM単独でBLOCKINGになります。
>
> **Safetyを緩めない範囲での結論**: floorの`changed_time`もStage2
> rubricも、このケースのために緩める必要はありません。何も変更しない
> ことを推奨します。

### 元々「正常記事」とラベルした根拠

`design_open233_self_recovery_flow_01.md` L2674(§7-0表)より逐語:

> | negative候補7記事(全claim) | ACCEPTABLE(正解、Stage1のみで
> 完結が期待) | **ACCEPTABLE(変更なし、不要Rewrite0件が正解)** |
> 正常記事であり、いずれのclaimもNG(a)〜(e)に該当しない。§8追加測定
> 「正常記事の不要Rewrite件数・率」の分母(NORMAL_GROUP_INSTANCE_
> IDS)としても使用する |

「negative候補7件」はStage1チェッカー較正Trial(V4A変種、
`er052_output/open233_self_recovery_phase1_step3_stage1_compare_
01/c_negative/neg3_hormuz_prodrunner_b1b/V4A/run_1.json`)でBLOCK判定
された実在記事群であり、当時の較正Trialでは「Stage1のみで完結する
はずの正常記事」というラベルが付与された。Opus #4 Q2は、この前提
自体がneg3については成立しない(HF-009 conditionsを実際に反転して
いる)と判定した(`design_open233_self_recovery_flow_01.md` L149:
「claimはHF-009のconditionsを実際に反転しており、『クリーンな記事
(Rewrite不要)』というnegative群の前提を満たしていません」)。

### 本文中の「舞台に残ったままです/stayed」との整合

Opus Q2が引用した本文文言(逐語): 「けれど、海峡をめぐる緊張に関する
ニュースは、舞台に残ったままです。」(EN: “But news about tensions
around the strait stayed on stage.”) — 記事本文自体は継続(stayed)
と記述しており、In one lineだけが「returned」と逆方向に要約していた
ことが、Opusの「要約時の事実変形」判定の直接的な根拠になっている。

---

## 3. hormuz_run03_standard(rep15 sample1、STAGE4_ESCALATION)

`final_state: STAGE4_ESCALATION`、`stage4_reason:
"ja_deviation_unresolved"`。費用¥4.0578、19 call、3 cycle。

### A. 元記事(HF-009の全出現箇所、Before、cycle1時点=原文そのまま)

Ledger HF-009は§2と同一(再掲略)。

記事内の全出現箇所(cycle1 `en_text_before_rewrite`/
`ja_text_before_rewrite`より逐語、英日対応):

| 箇所 | 英文(Before) | 日本語文(Before) |
|---|---|---|
| Title | “The Fee Plan Leaves, But High Oil Prices Stay” | 「料金案は退場、原油高は居残り」 |
| 本文冒頭(Brent) | “After the fee plan was withdrawn and replaced, Brent crude oil futures briefly lost some of their gains. Prices seemed ready to fall. But they soon returned to a high level near their earlier level. At the time of reporting, they were up about 2.6 percent, above 85 dollars a barrel.” | 「料金案の撤回と置き換えが発表されたあと、ブレント原油先物は上げ幅を一時的に縮めました。これで値下がりの幕が開くのかと思ったところ、ほどなくして、発表前に近い高い水準へ戻りました。報道時点では約二点六パーセント高で、一バレル八十五ドルを超えていました。」 |
| 本文(市場全体への一般化、①) | “Oil prices did not fall across the whole market after the plan was withdrawn. At the same time, attacks by the United States and Iran continued. So did a sea blockade and worries about tanker safety.” | 「このとき確認できるのは、撤回の直後に原油価格が全面的に下落したわけではない、ということです。同じ時間帯には、アメリカとイランの攻撃、海上封鎖、タンカーの安全への懸念が続いていました。」 |
| 本文結び(市場全体への一般化、②) | “The fee plan disappeared. But news about tensions around the strait stayed on stage. Political statements changed greatly. Oil prices moved briefly, then returned to a high level. The interesting point this time was simple. One headline alone could not decide how the story would end.” | 「料金案は消えました。けれど、海峡をめぐる緊張に関するニュースは、舞台に残ったままです。政治の発言が大きく変わっても、原油価格は一度揺れたあと、高い水準へ戻った。今回の面白さは、まるで一つの見出しだけでは、物語の結末まで決められなかったように見えるところです。」 |
| In one line(市場全体への一般化、③) | “The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.” | (In one lineは本文JA末尾と同一文を参照、独立フィールドなし) |

### B. 最初の判定(cycle1、①本文冒頭近くの一般化claim)

Stage1が最初に問題としたclaim(section_type=`body`、origin=
`ja_source`):

> `claim_in_article`: “Oil prices did not fall across the whole
> market after the plan was withdrawn.”
> `issue`(逐語、日本語): 「Brent先物についての観測を、石油市場全体の
> 値動きに広げている。」
> `explanation`: 「HF-009が確認するのはBrent先物の一時的な上げ幅
> 縮小と回復であり、市場全体で原油価格が下落しなかったという主張
> までは保証しない。具体的事実の追加（changed_fact、unsupported_
> new_claim）と対象範囲の拡張（changed_scope）に該当する。」

Stage2 basis(逐語): `basis: "ledger_scope"`、`materiality:
BLOCKING`、`llm_materiality: BLOCKING`(floorを介さずLLM単独でも
BLOCKING)。

worker評価: 許容線に照らして妥当。「Brent先物」という限定された
Ledger観測範囲を「石油市場全体」へ広げる表現は、ユーザーNGリストの
「scope拡張」に明確に該当し、争いの余地は小さい(neg3のような
統語的な曖昧さがない、単純な主語の置き換え忘れに近い)。

### C. 各Rewrite段階(rep15 sample1主、rep14で補助比較)

**cycle1**(rewrite_records 2件):

1. claim「Oil prices did not fall across the whole market after
   the plan was withdrawn.」→ `ladder_level_used: "1_word_
   connective"`(method `j1_e1_minimal_word`)。
   - EN After: “Brent futures briefly went down, then went back up
     after the plan was withdrawn.”
   - JA After: 「このとき確認できるのは、撤回の直後にBrent先物が
     一時的に上げ幅を縮小し、その後回復した、ということです。」
   - `rewrite_hint`: 「「このとき確認できるのは、撤回の直後に原油
     価格が全面的に下落したわけではない、ということです。」の対象を
     市場全体ではなくBrent先物に限定し、撤回後に一時上げ幅を縮小
     したものの、その後回復したと記述してください。参照: HF-009」
2. claim「The fee plan vanished, but oil prices stayed high as
   tensions around the Strait of Hormuz continued.」(In one line)
   → `ladder_level_used: "3_sentence"`(method `j1_paired_rewrite`)。
   - EN After(In one line): “After the news, Brent prices briefly
     dipped, then returned close to their earlier high level.”
   - `escalate_to_paragraph`フラグなし(まだ初回検出)。
   - 局所QA fastpath: `local_qa_fastpath_attempted: false`(両claim
     とも未試行)。
   - `recheck_overall_status: LEDGER_DEVIATION`(全文Recheckはまだ
     未解消と判定)。`ja_fail_open_guard.ok: false`、violations 3件
     (`unexplained_ja_sentence_deletion`×2、
     `flagged_ja_sentence_unchanged`×1、いずれもHF-009関連JA文が
     cycle1のJA Rewrite後も未修正/説明なく削除されたと検出)。
   - `ja_en_equivalence_verdict: "REVIEW_REQUIRED"`。
   - 次cycleへ進んだ理由: `full_recheck_required_reasons`に
     `ja_en_equivalence_not_pass` / `ja_fail_open_guard_violation`
     が含まれ、EN/JAとも`LEDGER_DEVIATION`のまま。

**cycle2**(rewrite_records 1件、`escalate_to_paragraph: true`が
付与された新規claimに対する段落Rewrite):

- 新規blocking claim: “Oil prices moved briefly, then returned to
  a high level.”(cycle1では未検出だった本文末尾の別の一般化文、
  `escalate_to_paragraph: true`が明示的に付与)。
- `ladder_level_used: "4_paragraph"`(method
  `j1_paired_rewrite_paragraph`)。①③(word/sentence)は**この
  claimに対しては一度も試行されていない**(下記F参照)。
- EN After(段落末尾): “The fee plan disappeared. But news about
  tensions around the strait stayed on stage. Political statements
  changed greatly. **After the announcement, Brent prices briefly
  dipped, then soon returned close to their earlier high.** The
  interesting point this time was simple. One headline alone could
  not decide how the story would end.”
- JA After(段落末尾): 「料金案は消えました。けれど、海峡をめぐる
  緊張に関するニュースは、舞台に残ったままです。**発表後、Brent先物
  は一時上げ幅を縮めましたが、ほどなく発表前に近い高い水準へ戻り
  ました。**」(「政治の発言が大きく変わっても、原油価格は一度揺れた
  あと、高い水準へ戻った。」という1文がJA側から**丸ごと削除**されて
  いる。対応するEN側の「Political statements changed greatly.」は
  **削除されず残存**しており、EN/JAの文数・内容が非対称)。
- `rewrite_hint`: 「記事本文の該当箇所：「政治の発言が大きく変わっても、
  原油価格は一度揺れたあと、高い水準へ戻った。」対象を原油価格全般
  ではなく、Ledgerが観測したBrent先物の値動きに限定してください。
  参照: HF-009」
- `ja_fail_open_guard.ok: true`、`violations: []`(決定論ガードは
  cycle2では通過=逐語削除/残存の機械検出には引っかからなかった)。
- `ja_en_equivalence_verdict: "FAIL"`(LLMベースの意味等価チェックは
  不合格と判定)。
- 次cycleへ進んだ理由: `full_recheck_required_reasons`に
  `paragraph_or_full_or_delete_rewrite` / `both_ja_en_changed
  (paired_j1)` / `ja_en_equivalence_not_pass` /
  `same_fact_id_reappeared_across_cycles`。`recheck_overall_status
  (EN): LEDGER_DEVIATION`だが`recheck_all_prior_issues_resolved:
  true`、`ja_recheck_overall_status: LEDGER_COMPLIANT`
  (`"ja_ok_blocked_by_equivalence": true`=JA全文Recheck自体は
  合格だが、等価チェックFAILによりja_okが強制的にFalseへ倒された)。

**cycle3**(新規blocking claimなし):

- 全7claimが`materiality: ACCEPTABLE`(title「The Fee Plan Leaves,
  But High Oil Prices Stay」を含む、`blocking_count: 0`,
  `non_blocking_count: 7`)。Rewriteは発火しない。
- それでも`final_state: STAGE4_ESCALATION`、`stage4_reason:
  "ja_deviation_unresolved"`。

### D. 最終的に人間確認へ回った直接原因

**コード機構**(`er052_open233_self_recovery_flow_runner_01.py`
L3538-3544, L3608-3620、逐語コメント引用):

> 委任_20 W1(i)(Opus L2レビュー#4 §0): JA recheckが未解消
> (ja_ok=False)のまま次cycleへ進んだ事実を保持する。この状態のまま
> loopが「not blocking_claims」downgrade経路(RESOLVED_STAGE2_
> DOWNGRADE/RESOLVED_REWRITE_THEN_DOWNGRADE)へ抜けた場合は、JA側の
> 未解消を握り潰さずSTAGE4_ESCALATION(ja_deviation_unresolved)を
> 強制する(rep10 hormuz_run03_standard sample1 cycle2のfalse PASS
> 再発防止)。

すなわち、cycle2の`ja_en_equivalence_verdict: "FAIL"`により
`ja_pending_deviation`が`True`へセットされ、cycle3でEN側の
blocking claimsが0件(=表面上「解消」に見える)になっても、JA側の
未解消フラグが握り潰されずSTAGE4_ESCALATIONへ回された。これは
委任_20/23で意図的に維持しているfail-closed安全装置であり、
本委任範囲のバグではない。

**等価QAの入力(EN/JA、cycle2のAfter逐語、再掲)**:

- EN: “...Political statements changed greatly. After the
  announcement, Brent prices briefly dipped, then soon returned
  close to their earlier high. The interesting point this time was
  simple...”
- JA: 「...けれど、海峡をめぐる緊張に関するニュースは、舞台に
  残ったままです。発表後、Brent先物は一時上げ幅を縮めましたが、
  ほどなく発表前に近い高い水準へ戻りました。」

**等価QAの出力**: `verdict: "FAIL"`(call_log記録、逐語)。**ただし
判定理由テキスト自体(borrowed `er003_ja_to_en_translation.py`の
fidelity QA出力が持つexplanation相当フィールド)はcall_log/cycle_
recordのいずれにも保存されておらず、本委任のjson Evidenceからは
「記録なし」**(`run_ja_en_equivalence_check`関数はverdict enumの
みを`call_log`へ記録し、理由文は保存しない設計。再実行すれば理由
文を取得できるが、追加API課金が必要なため本委任[¥0縛り]では
実施しない)。

**worker自身の平文分析(推測ではなく、実際の逐語テキスト差分に基づく
観察であり、LLM判定の文言そのものではないことを明記)**: EN Afterは
「Political statements changed greatly.」という1文を維持したまま
「After the announcement, Brent prices briefly dipped...」を続けて
いるのに対し、JA Afterでは対応する「政治の発言が大きく変わっても」
に相当する文が丸ごと削除されている。EN側は文構成上「政治声明は
大きく変わった」ことと「その後Brent価格は一時下落後に回復した」の
2つの事実が並んでいるのに対し、JA側は「政治声明」への言及自体が
消え、「発表後にBrent先物が動いた」という1文だけが残る。**英語は
（政治の発言の変化と価格の動き、2つの事実）を言い、日本語は（価格の
動きのみ）を言っている**状態であり、語数・情報量の非対称という
形で意味のズレが生じている可能性がある。決定論ガード
(`ja_fail_open_guard`)はこの種の「情報量の非対称」を検出する設計に
なっておらず(逐語残存/無説明削除のみ検出)、`ok: true`のまま素通り
した。

### E. 現在の生成順序(J-1、JA/EN同時生成)

`er052_open233_self_recovery_flow_runner_01.py` L2241-2260
(paragraph level、逐語プロンプト抜粋):

```
[JA paragraph block (may include a heading/title/hook line)]
{ja_block}

[EN paragraph block (translation of the same paragraph)]
{en_block}
...
Revise BOTH paragraph blocks (paired, minimal edits). ...
Return strict JSON: {{"ja_revised": "<full revised JA paragraph
block>", "en_revised": "<full revised EN paragraph block>"}}
```

**確認した事実**: J-1は「JAを先に生成してからENを生成する」
逐次生成ではなく、**同一の1 LLM callにJA原文・EN原文の両方を入力
として渡し、同一callの中でja_revised/en_revisedを同時に出力させる
設計**(word/sentence/paragraph、全ladder水準で共通)。したがって
委任文が想定する「別々に生成するとズレる」という前提そのものは、
現行コードには当てはまらない(既に同時生成)。

**それでもズレが生じた理由(cycle2の実例から)**: 同時生成であっても、
1回のLLM呼び出しが生成する2言語の出力が意味的に完全に対応する保証は
ない(生成モデル側の非決定性)。本件では`ja_fail_open_guard`
(逐語照合の決定論ガード)がcycle2では素通りし(`ok: true`)、意味
レベルの等価性はLLMベースの`ja_en_equivalence`チェック(FAIL)だけが
捉えた。つまり「同時生成」自体は既に実装済みで、今回の不一致は
生成順序の問題ではなく、**段落単位という比較的大きな編集単位で2言語
を同時生成した際の、モデル出力の意味的不整合**が根本原因である
可能性が高い(§Fで検証)。

**Production仕様との整合**: J-1のpaired local rewriteはOPEN-233
Trial専用機構であり、Production正式経路には無断混入していない
(`design_open233_self_recovery_flow_01.md` L1272-1299)。Production
の既存JA側フォールバック(「案B」、`er012_e_family_entertainment_
two_level_runner_01.py::run_writer_stage()`のJARecheckRequiredError
捕捉→`jaw.run_ja_writer_o_r1_r2()`のmust_fix付き全文再生成
[Original→R1→R2→JA Fact Check])は、JA側を丸ごと再生成してから
別途EN翻訳を通すため、構造的に「JA/EN不整合」は起きにくい一方、
「該当claimと無関係な箇所まで変わり得る」「¥3.5〜4.0/回」という
既知のコストとリスクを持つ(同L1280-1298)。J-1(¥1.0〜1.5/cycle
想定)はこのコストを下げるためのTrial新設計であり、今回のJA/EN
不整合は、J-1という新方式が案Bより安いコストで導入した**新規リスク**
と位置づけられる(段落単位の同時生成が、文単位の同時生成より
このリスクを増幅させている可能性、§F)。追加コスト概算は、案Bの
全文再生成1回(¥3.5〜4.0、既存7 call相当)に対し、J-1段落Rewrite
1回は本件で¥0.1501+¥0.0806+¥0.1156×2+¥0.0844=概算0.5 call分
(数call、¥0.5前後)であり、J-1が案Bより明確に安いことは今回も
再確認できる。ただし今回のように等価FAILでSTAGE4へ回った場合、
後続の全文Recheck・JA Recheck・equivalence call(合計¥1.2前後)が
追加で発生し、案Bとの差は縮む。

### F. 段落Rewriteが本当に必要かの再評価

HF-009の各出現箇所(A節の表を参照)を、実際に解決した2箇所
(①本文冒頭近く、③In one line)と、段落Rewriteに至った1箇所
(②本文結び)で比較する。

| 箇所 | 実際の解決方法 | 解決したか |
|---|---|---|
| ①本文冒頭近く “Oil prices did not fall across the whole market...” | `1_word_connective`(語レベル置換、J-1) | 解決(cycle1) |
| ③In one line “...oil prices stayed high as tensions...continued.” | `3_sentence`(1文レベル、J-1) | 解決(cycle1) |
| ②本文結び “Oil prices moved briefly, then returned to a high level.” | `4_paragraph`(段落レベル、J-1、`escalate_to_paragraph`強制) | 未解決のままSTAGE4(等価FAIL) |

**worker案(局所修正のみでの解決案、未検証・提案のみ)**: ②の問題文
「Oil prices moved briefly, then returned to a high level.」は、
①・③と全く同型の「Oil prices」→「Brent futures」という主語の
scope限定だけで解決できる可能性が高い。

- EN案: “**Brent futures** moved briefly, then returned to a high
  level.”(1語置換)
- JA案: 「**Brent**先物は一度揺れたあと、高い水準へ戻った。」
  (「原油価格」→「Brent先物」の1語置換、元文「政治の発言が大きく
  変わっても、原油価格は一度揺れたあと、高い水準へ戻った。」の
  後半のみ変更し前半「政治の発言が大きく変わっても」は保持)

この案は①・③で実際に成功した編集パターン(主語のみをBrent限定へ
置換、前後の文構造・情報は保持)と完全に同型であり、局所修正のみで
解決できない特段の理由は本文中に見当たらない。**ただし、この案が
実際にguard/Recheck/等価QAを通過するかは未実測であり、新規Trial
実行が必要(本委任[¥0縛り]では検証不可)**。

**段落Rewriteに至った実際のトリガの確定(rep15ログより)**:
コード(L3648-3677、L3728-3734)を確認した結果、②の`escalate_to_
paragraph: true`は「①③で局所QA/Recheckが実際に試行され、かつ
不十分と判定されたから」ではなく、**「同一fact_id(HF-009)が
過去cycle(cycle1)で一度でもBLOCKINGと判定されていたから」という
決定論ルール(`repeat_fact_ids_for_recheck`、委任_19 A-2)が機械的に
発火したから**である。②の具体的な文言「Oil prices moved briefly,
then returned to a high level.」に対して①③相当の語レベル/1文
レベルRewriteが**一度も試行されていない**ことをコードコメント
(L2386-2387「`escalate_to_paragraph`が立っている場合、levelsから
1_word_connective/3_sentenceを除外する」)およびrewrite_records
(cycle2は`4_paragraph`の1レコードのみ)から確認した。`local_qa_
fastpath_attempted: false`(cycle1・cycle2とも)であることから、
局所QA自体も一度も発火していない。

---

## 4. 結論(worker見解、Fableが最終判断)

- **真に不要Rewriteと確認できる件数**: **0件**。neg3(HF-009
  scope反転)はOpus #4 Q2により「BLOCKINGが妥当、negative群ラベル
  側が誤っている可能性が高い」と判定済みであり、Rewrite自体は不要
  ではなく正当だった可能性が高い(§2)。neg1(MUSE-HC-006 hook
  claim)は真にdisputed(rubric境界事例、rep11/rep12/iter7 s1/s2で
  BLOCKING・非BLOCKING双方が実測)であり、「不要」と断定も「必要」
  と断定もできない。
- **まだ判断が必要な件数**: **1件**(neg1のHook rubric tie-break
  文言の明確化要否。Fable/ユーザー判断待ちのOPEN_ITEMS事項、コード
  変更を伴うため本委任スコープ外)。
- **人間確認1件(`hormuz_run03_standard`)を解消する最小改善案**:
  局所修正の連鎖で済む可能性は**ある**(§3F、①③と同型の1語置換
  案)が、**未検証**(新規Trial実行が必要、本委任では実施不可)。
  もし①③と同様に語レベルで解決すれば、段落単位の同時生成に伴う
  EN/JA非対称(§3D)自体が発生せず、STAGE4を回避できた可能性が
  ある。ただし`escalate_to_paragraph`ルール自体を緩める(同一
  fact_id再出現時に常に④へ直行させず、まず①③を試させる)ことは
  コード変更であり、本委任では実装していない。
- **段落Rewriteの要否**: 今回のケースについては、evidenceからは
  「必要だった」という実測根拠は見当たらない(①③既に同型claimが
  段落Rewriteなしで解決済み)。段落Rewrite自体を廃止すべきという
  結論ではなく、「同一fact_id再出現」という条件だけで①③を無条件に
  スキップする現行ルールが、本件のような『新しい文言だが同型の
  scope限定で直る』ケースを過剰に段落レベルへ送っている可能性が
  ある、という所見に留める(コード変更の要否はFable/ユーザー判断)。

## 参照したEvidence(パス)

- `er052_output/open233_self_recovery_flow_runner_01_iter7/
  instances_s1/neg1_meta_b3prod_a2.json`
- `er052_output/open233_self_recovery_flow_runner_01_iter7/
  instances_s2/neg1_meta_b3prod_a2.json`
- `er052_output/open233_self_recovery_flow_runner_01_iter7/
  instances_s1/neg3_hormuz_prodrunner_b1b.json`
- `er052_output/open233_self_recovery_flow_runner_01_iter7/
  instances_s2/neg3_hormuz_prodrunner_b1b.json`
- `er052_output/open233_self_recovery_flow_runner_01_rep15/
  instances_s1/hormuz_run03_standard.json`
- `er052_output/open233_self_recovery_flow_runner_01_rep14/
  instances_s1/hormuz_run03_standard.json`
- `er019_output/family_x_refresh_e2e_01/meta/run_03/ledger/
  verified_fact_ledger.txt`(MUSE-HC-006/012)
- `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/
  verified_fact_ledger.txt`(HF-009)
- `docs/pm/design_open233_self_recovery_flow_01.md`
  (§5-8 L1746-1781、§6-13 L2608-、L1160-1228、L2214-2263、
  L2664-2674)
- `docs/pm/opus_l2_review_open233_self_recovery_04.md`(Q2、
  L120-207)
- `er052_open233_self_recovery_flow_runner_01.py`(L796-841、
  L2195-2300、L2472-2620、L3538-3544、L3608-3620、L3648-3677、
  L3728-3734)
