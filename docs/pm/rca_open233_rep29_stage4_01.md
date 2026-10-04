# RCA: rep29 Human Review 3件の構造的根本原因分析(OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_10)

管理ID: `OPEN-233-KPI-RECOVERY-REDESIGN-02`(親`OPEN-233-SELF-RECOVERY-TRIAL-01`)。費用: ¥0(既存instance JSONの走査・span解決関数のオフライン呼び出しのみ。LLM・API呼び出しなし)。性質: 診断。Production未変更。`APPROVED_FOR_PRODUCTION`ではない。
再現スクリプト: `er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.py`(出力`agg_rep29_stage4_rca_01.json`・`agg_rep29_stage4_rca_01_stdout.txt`)。
一次証跡(逐語の元): `er052_output/open233_self_recovery_flow_runner_01_rep29/instances_s1/meta_run03_advanced.json`、`instances_s2/meta_run03_advanced.json`、`instances_s1/safety_A4.json`(cycles[].stage2_results/rewrite_records/recheck_*/en_text_before_rewrite/en_text_after_rewrite、call_log)。
凡例: 「確認」=実データ・コードから直接確認、「推測」=データから導いた仮説。runnerの行番号は`er052_open233_self_recovery_flow_runner_01.py`(本委任時点、編集なし)。

## 0. 結論(先に要点)

| # | instance | STAGE4理由 | 直接原因(確認) | 後段だけで決定論的に解けたか |
|---|---|---|---|---|
| (1) | s1 `meta_run03_advanced` | `same_claim_fact_id_reblocked` | **記録バグ**: `escalated_to_paragraph`を「flagが付いたか」で記録(L8264)するが、ladderはflagを無視する(`ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP=False`、L311/5952)。実際は毎cycle ①語句のみ試行なのに「④段落まで昇段済み」と記録され、cycle 3の再発で「ladder枯渇」とみなされた。加えて cycle 3のclaimは**古い文言**(複数範囲のRewrite後文を`\n`連結したためL2221が現行文への差替えを行わない) | **解けた**。(i)記録を実際の試行level基準にし(ii)同一箇所の再発は前levelの上位から試す(③1文→④段落)。cycle 3のRewrite案は未生成のためLLM call 1〜2回(推測)が必要 |
| (2) | s2 `meta_run03_advanced` | `violation_span_unverified` | Recheckが返した`claim_in_article`が「“引用A” and, in the one-line summary, … “引用B”」という**地の文混じりの合成文**。`resolve_violation_spans`が`explanatory_mixed`(L4804)で未確定。cycle 1の①語句置換(users→businesses)→cycle 2の①語句置換(businesses→users)で本文が**原文に戻って**いたため、claimの引用は本文に逐語で存在していた | **解けた(replay確認)**。引用ごとに分割して解決すると2片とも一意に確定(L3・L0)。`related_fact_id`(MUSE-HC-006)は存在したが不要 |
| (3) | s1 `safety_A4` | `cycle_limit_exhausted_after_recheck` | cycleごとの新規MAJOR 6件は**全て原文に最初から在った文**(Rewriteが生んだものは0件)。Stage 1(fixture指定)が拾わなかった箇所をRecheckが1cycleに1〜2件ずつ見つけ、cycle 3(`HARD_MAX_CYCLES`)で打ち切り。最終Recheckで残った`MUSE-HC-012`は**同じ文がcycle 1・2で Stage 2+S1により非BLOCKINGと確認済み**だが、上限到達後はStage 2を通らずSTAGE4へ | **一部解けた**。上限到達後に残ったRecheck MAJORを既存のmateriality funnel(Stage 2+S1)に1回通すだけで済む(新ゲートなし)。ただし結果(非BLOCKINGか)は有料callなしでは確定不能 |

共通構造(確認+解釈): 3件とも**個別の穴**ではあるが、背後に3つの共通構造がある。
1. **Rewrite「成功」とissue「解消」が別物**: ladderの成功判定は「文字列が変わった∧書き戻せた∧新主体語がLedger内」だけ(L6011〜6031)。issueの焦点が残っているか・直前の状態に戻っていないかは見ない。解消判定は1cycle後のRecheck(¥0.4〜0.8)に任されており、(1)(2)(3)の全てがこの乖離を通っている。
2. **履歴のキーが「claim(fact_id・claim本文)」で、「記事内の箇所(location)」ではない**: (1)は別文言・合成文のclaimで一致判定が崩れ、(2)はfact_idの兄弟(HC-006↔HC-012)が同じ文を行き来しても「別claim」になり、(3)は同じ文が3 cycleにわたり別claimとして再検出されている。
3. **Human Reviewへ倒す出口が「処理の計数・形式条件」で、materiality判定(Stage 2+S1)を現行本文に対して呼ぶ前に発火する**: `same_claim_fact_id_reblocked`(L8178〜8184)、`violation_span_unverified`(L8342〜8347)、`cycle_limit_exhausted_after_recheck`(L8724〜8726)の3つは全て「重大かどうか」を見ずに倒す出口である。

→ 判断: rep27〜29の9件(下記§4)は全て別原因の実装不整合で、**「Rewriteが本当に直せない重大誤り」であった例は0件**(確認)。個別修正の連鎖であると同時に、上の3構造が毎回形を変えて出口に到達している。次は個別3件の修正ではなく、構造(location単位の履歴・ladder成功判定・出口のfunnel経由)を一括で設計し、Opusに批判させるべきと判断する(§5、設計書§17)。

## 1. (1) s1 `meta_run03_advanced` MUSE-HC-006(final_state `STAGE4_ESCALATION` / `same_claim_fact_id_reblocked`、費用¥2.48、10 calls)

Ledger MUSE-HC-006(確認): 「MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる…テストを実施した。」→ 電話する側=契約スタッフ、相手=企業・店舗。原文の `users had no way to know whether they were talking to AI or a person`は「ユーザー=通話の当事者」に読めるため`changed_actor`。

### cycle 1
- Stage 1(Recheck経由で記録されたStage 2入力)3 claim(全て`MUSE-HC-006`、`origin=ja_source`、同一issue): ① `And if this was not properly explained, users had no way to know whether they were talking to AI or a person.` ② `People who asked Muse to make a call might think that AI was making it. But in some cases, a human was speaking.` ③ `Some calls made through Meta’s AI assistant were actually handled by humans, without users being properly told.`
- Checker issue(逐語): `This wording makes users sound like the people speaking on the phone. The Ledger describes calls placed to businesses or stores, with human contract workers handling some calls on users’ behalf.` flags: changed_fact/changed_actor/unsupported_new_claim。
- Stage 2: 3件BLOCKING(`existing_major_v2`)。S1(降格確認、2件batch): ②③は`ACCEPTABLE→ACCEPTABLE`で**降格確定**。BLOCKINGは①のみ。
- Rewrite: `problem_kind=actor`、`levels_planned=[1_word_connective, 3_sentence, 4_paragraph]`、span解決L0→`[870,979]`。level 1(1_word_connective)の結果`success`:
  - before: `And if this was not properly explained, users had no way to know whether they were talking to AI or a person.`
  - after: `And if this was not properly explained, users had no way to know whether AI or a person was making the call.`
  - `actor_guard_decision=[{"mode":"ag1_strict","ok":true,"new_classes":[]}]`(新主体語なし=無条件OK)。**主体語`users`は残存**(`agg_rep29_stage4_rca_01.json` `actor_focus_check_rep29`: `actor_noun_retained=true`)。
- Recheck: `LEDGER_DEVIATION`、`prior_issues_resolved=[{"index":0,"resolved":false,"explanation":"The article retains the cited claim that users had no way to know whether AI or a person was making the call; the prior concern about shifting the actors in the reported interaction is therefore not resolved."}]`。次cycleへ(`NEXT_CYCLE`)。merged claim: `“Users had no way to know whether AI or a person was making the call” and “a human on the other end of the call.”`(label `recheck_major`、MUSE-HC-006、**2つの引用を含む合成claim**)。
→ 判定の経路: Stage 2は問題を見つけ、ladderは「文字列変更成功」と判定し、実際のissue(「users had no way to know」という未確認の主張自体)はRecheckで未解消。

### cycle 2
- Stage 2 claim(1件): 上記の合成claim。issue: `The wording relocates the human from the contract worker placing/handling the call to “the other end” of the call, and says users had no way to know, beyond the Ledger’s account that the test began without proper disclosure.` → BLOCKING。
- Rewrite: `problem_kind=actor`、`levels_planned=[1,3,4]`(**level 1から再開**。cycle 1の履歴は引き継がれない)。span解決`P:2`(explain_split、2範囲)。level 1 `success`:
  - `users had no way to know whether AI or a person was making the call` → `users had little way to know whether AI or a person was making the call`
  - `a human on the other end of the call` → `a human on the call`
  - `actor_guard_decision`=2件`ok:true,new_classes:[]`。
- Recheck: `index 0 resolved=false`、explanation: `The role-relocation concern is resolved: the article describes a human speaking and making the call, not a human at the receiving end. However, it retains the unsupported assertion that users had little way to know who was making the call, so the prior issue is not fully resolved.`。merge: `recheck_major`(`MUSE-HC-012`: `“If this was not properly explained, users had little way to know whether AI or a person was making the call.”`)+`normal_gap`(`MUSE-HC-006`、cycle 1と同一の**古い合成claim**)。`n_merged=2`。
  - `normal_gap`のclaimが古いまま残った直接原因(確認): `normalize_recheck_outcome`は未解消priorの`claim_in_article`を現行本文の置換後の文へ差し替えるが、`if cur and "\n" not in cur:`(L2221)で**複数行(複数範囲のRewrite後文を`\n`連結したもの)は差し替えない**。cycle 2のRewriteは2範囲だったため(`prior_issue_text_sources=["current_text"]`だが、結合後は複数行)、HC-006のclaimは**本文に既に無い文言**のまま次cycleへ渡った。

### cycle 3(最終)
- Stage 2 claim 2件: ① `MUSE-HC-012` `“If this was not properly explained, users had little way to know …”`(issue: `The Ledger reports that the test began without proper disclosure, but does not establish how much ability users had to determine who was making a particular call.`)→ Stage 2 BLOCKING、**S1でACCEPTABLE→ACCEPTABLE、降格確定**(`confirmed_downgrade=true`)。② `MUSE-HC-006`の**古い合成claim**(`Users had no way to know whether AI or a person was making the call” and “a human on the other end of the call.”`)→ BLOCKING(issueはcycle 2と同一の逐語、現行本文はこの文言をもう含まない: `had no way to know`=本文に無し、`had little way to know`=有り)。
- `repeat_claim_ids=["fact:MUSE-HC-006"]`、`ladder_exhausted_before_reblock=true` → `final_state=STAGE4_ESCALATION`、`stage4_reason=same_claim_fact_id_reblocked`(L8178〜8184)。**cycle 3でRewrite(LLM call)は実行されていない**。

### 問い(a) level 1が「成功」とされた判定基準(確認)
`rewrite_ranges_ladder`(L5798〜):各levelで`candidate, bad_idx = vs_apply_replacements(...)`(書き戻し)→ **`if not (candidate != full_text and all(changed)): guard_failed`(L6011)**→ actor guard(新主体クラス=after−before、L6023)→ `attempt["result"]="success"`(L6031)。成功条件は「①文字列が変わった ②書き戻せた ③新しい主体クラスが無い/許容された」のみ。**issueの焦点(`users`の残存・入替、数値・否定・時期)がRewrite後spanから消えたかは見ない**。

### 問い(b) 次cycleのlevel(確認)
**level 1から再開**。cycle 2の`levels_planned=[1_word_connective,3_sentence,4_paragraph]`は cycle 1と同一。`ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP=False`(L311、委任_27、§0-4「各箇所は独立に初期単位から判断する」)のため、`escalate_to_paragraph`flagはladderに無効(L5952/6164/6436)。

### 問い(c) `same_claim_fact_id_reblocked`の条件と、昇段した場合の追跡(確認+推測)
条件(L8178〜8184、引用): `exhausted_matched_records = [m for m in matched_records if m.get("escalated_to_paragraph")]` → 非空なら `final_state="STAGE4_ESCALATION"; stage4_reason="same_claim_fact_id_reblocked"`。`matched_records`=`find_matching_prior_record`(L1319〜、fact_id一致∧正規化claim文のSequenceMatcher比率≥0.75、近い直前cycle優先)。`escalated_to_paragraph`は`prior_blocking_records`へ`bool(c.get("escalate_to_paragraph"))`で記録(**L8264**)。このflagは(i)前回claimが再発したとき(L8193)(ii)同一fact_idが過去cycleに存在するとき(L8250)に付くが、(i)(ii)どちらも「ladderがparagraphを試した」ことを意味しない(ladderはflagを無視、L5952)。

→ **確認した不整合**: cycle 2のHC-006 claimは(ii)でflag=Trueが付き、`escalated_to_paragraph=True`として記録されたが、実際のladderは level 1のみ(`rewrite_records[0].ladder_level_used="1_word_connective"`、`levels_planned`に③④が残っていた)。cycle 3で再発し、「④まで昇段済みの再発」と誤認してSTAGE4。`agg_rep29_stage4_rca_01.json`の`same_claim_reblocked_vs_actual_ladder`: `max_ladder_level_actually_used=1`、`ladder_actually_exhausted_to_level4=false`。(rep27〜29で`same_claim_fact_id_reblocked`は本件のみ。)

「前cycleのlevelの上位へ昇段」した場合の追跡(推測+オフライン確認可能部分): cycle 3相当の入力(古い合成claim)を cycle 3開始時点の記事(=cycle 2のRewrite後)で解決すると **`status=unverified, reason=mismatch`**(`span_replay.s1_c3_HC006_claim_vs_cycle3_start_article`、確認)。つまり単に昇段させても、次は`violation_span_unverified`で別の出口に倒れる。**(1)は「記録バグ」と「古いclaim(L2221)」の二重**で、片方だけ直しても別の出口で止まる。古いclaimを現行本文へ差し替えれば(cycle 2のRewrite後文2つ=`users had little way to know whether AI or a person was making the call` / `a human on the call`)、span解決・昇段(③1文)に進める。③のRewrite案は既存ログに無い(未生成)。必要なLLM call: ③1文 1回(≈¥0.1〜0.2)+Recheck 1回(≈¥0.4〜0.5)。

### 構造的な含意
本件の本質は「①語句の最小編集が、"users had no way to know…"という**文全体の主張**(Ledgerにない)を直せない」にある。cycle 2のRecheckの`explanation`が自ら示している(`it retains the unsupported assertion that users had little way to know`)。語句置換(`no`→`little`、`other end`→`on the call`)は文の主張を保ったまま表層だけを変えた。levelの昇段(③1文)か、Rewrite文が「Ledgerの確認済みの形(`the test began without properly telling users`、MUSE-HC-012)」へ変わったか、のどちらかが決定論的に判定できれば、cycle 1の時点で止められた。

## 2. (2) s2 `meta_run03_advanced`(final_state `STAGE4_ESCALATION` / `violation_span_unverified`、費用¥1.73、8 calls)

### cycle 1
- Stage 2 3 claim(s1と同一)。S1: ②③が降格確定、①のみBLOCKING。
- Rewrite level 1 `success`(`problem_kind=actor`、span L0 `[870,979]`):
  - before: `And if this was not properly explained, users had no way to know whether they were talking to AI or a person.`
  - after: `And if this was not properly explained, businesses had no way to know whether they were talking to AI or a person.`
  - `actor_guard_decision`: `ag1_strict ok:true new_classes:[]`(`businesses`は`ACTOR_SYNONYM_CLASSES`にクラスが無く、新主体クラス検出の対象外=guard素通り。**guardは「主体の入替」を見るが、「正しい主体への入替」かは見ない**)。
- Recheck: `index 0 resolved=false`、`The article still says businesses had no way to know whether they were talking to AI or a person, retaining the actor shift and unsupported claim identified previously.`。merge 2件: `MUSE-HC-012`(`recheck_major`)+`MUSE-HC-006`(`normal_gap`)、**両方とも同一の文**(`And if this was not properly explained, businesses had no way…`)。

### cycle 2
- Stage 2 2 claim(同一文、fact_id違い): `MUSE-HC-012`(issue: `The claim shifts the affected party from users in the Japanese source to businesses, and asserts that businesses had no way to know who they were speaking with. The Ledger does not establish that.`)、`MUSE-HC-006`(cycle 1と同じissue)。両方BLOCKING。
- Rewrite: HC-012: level 1 `success`(`problem_kind=term_scope`): `businesses had no way to know whether they were talking to AI or a person` → `users had no way to know whether they were talking to AI or a person`。**cycle 1の編集前の文(原文)に完全に戻る**。`actor_guard_decision`: 新主体クラス`user`、`basis=ledger_and_issue`で許容。HC-006: `covered_by_earlier_rewrite_in_cycle`(carry-forward、同文を先行Rewrite済みとして skip。`carry_forward_comparison`: `issue_string_equal=false`、`same_related_fact_id=false`、`true_flags_equal=false`)。
- `same_claim_reblocked_escalated_to_paragraph`(cycle 2の記録キー): 付与あり。ただし ladder は level 1のまま(上記(1)と同じ不整合)。
- Recheck: `index 0 resolved=true`(businessesの置換は解消)、`index 1 resolved=false`(`The article still says users were talking to AI or a person, framing users as call participants. The ledger describes calls made to businesses or stores by human contractors on users’ behalf.`)。merged claim(`recheck_major`、MUSE-HC-006、**地の文混じりの合成文**): `“Users had no way to know whether they were talking to AI or a person” and, in the one-line summary, calls were handled by humans “without users being properly told.”`。`en_text_before_rewrite`(cycle 1前)==cycle 2後の本文(`article_equals_original_before_cycle1=true`、確認)。

### cycle 3(最終)
- Stage 2 1 claim(上記合成claim)。BLOCKING。
- `resolve_violation_spans`: `status=unverified, reason=explanatory_mixed`(L4804、`per_lang.EN.status=explanatory`)。L6/sentence_restore: `not_fired`、`reason=explanatory_mixed_left_to_P`。carry-forward: cycle 3は1 claimのため対象外(cycle内の先行Rewriteが無い)。→ `rewrite_records`: `method=violation_span_unverified, target_not_locatable=true, span_unverified=true` → L8342〜8347で`violation_span_unverified`。LLM callは`stage2`のみ(cycle 3のRewrite call 0)。

### 問い(d) spanが特定できなかった直接原因(確認)
- Checkerの`claim_in_article`が前cycleの文を指していたのではない。cycle 3開始時点の本文(=原文に戻った本文)に、claimの2つの引用は**逐語で存在する**。原因はclaimの**形式**: 「“引用A” and, in the one-line summary, calls were handled by humans “引用B”」。引用の間に地の文があるため、引用ごとの照合の`explain_split`(`and`等の接続詞のみ許容)が通らず、`explanatory_mixed`になる。
- L6(sentence_restore)が効かなかったのは、`explanatory_mixed`を「P(段落水準)に任せる」とskipしたため(`not_fired/explanatory_mixed_left_to_P`)。carry-forwardは同一cycle内の先行Rewriteの存在が前提で、cycle 3は単独claimのため無関係。
- **replay(確認、`agg_rep29_stage4_rca_01.json`)**: claimから引用(`“…”`)だけを取り出して個別に`resolve_violation_spans`すると、`Users had no way to know whether they were talking to AI or a person`→`resolved L3, ranges=["users had no way to know whether they were talking to AI or a person"]`、`without users being properly told.`→`resolved L0`。**引用単位の分割で2片とも一意に確定**した。`related_fact_id`(MUSE-HC-006)からのfact→本文の特定は不要だった。

### 構造的な含意
(2)は(1)と**同じ根**を共有する: cycle 1の level 1が`users`→`businesses`(別の不正確な主体)にすり替え、cycle 2の level 1がその編集をそのまま元に戻した(2 cycleで本文が原文に戻り、Recheck 2回+Stage 2 2回+S1 1回=約¥1.5を使って何も変わらない)。①履歴(同じ箇所を以前の状態に戻す案は、その箇所の過去の状態と一致する=**振動**)を決定論で検知できれば、cycle 2のRewrite案を却下して上位levelへ進める。

## 3. (3) s1 `safety_A4`(final_state `STAGE4_ESCALATION` / `cycle_limit_exhausted_after_recheck`、費用¥4.3435、20 calls、3 cycle、`extra_cycle_granted=true`)

(fixture: `stage1_call_used=false`=Stage 1 deviationはfixture指定。Recheckが全文をStage 1相当で見る。)

### cycleごとの時系列(逐語の要点)
| cycle | Stage 2のBLOCKING claim(fact) | S1 | Rewrite(level) | Recheck結果 → 次cycleのclaim |
|---|---|---|---|---|
| 1 | HC-006 `Through Muse, trained human contract workers made some calls and completed the exchanges with users.`(translation、changed_actor)、HC-010 `One helper meant one more person handling private data.`(changed_scope/causality/certainty)ほか計8記録。HC-012(`That was what people thought as they spoke.`/`So people who thought they were speaking with AI were actually speaking with human staff.`)はS1で**降格確定**(`QUALITY→ACCEPTABLE`・`ACCEPTABLE→ACCEPTABLE`) | 4件 | HC-006: `users`→`businesses`(level 1)、HC-010: `meant`→`risked`(level 1)。品質regen 2回(`vocab_difficulty_increased_fragment(sentence_len+3.0,difficult_ratio+0.0083)`) | prior 4件**全て解消**。**新規MAJOR2件**: HC-006 `The idea was practical: when AI struggled, a person could help.`、HC-012 `AI called. That was what people thought as they spoke. ... people who thought they were speaking with AI were actually speaking with human staff.` |
| 2 | HC-006 `The idea was practical: when AI struggled, a person could help.`(ja_source、issue: `The Ledger confirms that trained human contractors handled some Muse calls, but does not say their role was to step in when AI struggled. The article adds that specific operating rationale.`)、HC-012(合成)=BLOCKING | HC-012を降格確定(`ACCEPTABLE→ACCEPTABLE`)。HC-006は残る | HC-006: ④段落(`problem_kind=multi_sentence`、見出し`### The human backup plan`→`### The human calls`+2文削除) | prior 1件**未解消**(`The explicit claim that humans helped when AI struggled has been removed, but “backup plan” still characterizes the contractors as a fallback role`)。新規MAJOR: HC-006 `But that backup plan changed the meaning of the call.`、HC-012 `The test began without properly telling people what was happening. So people who thought they were speaking with AI were actually speaking with human staff.` |
| 3(`extra_cycle_granted`) | HC-006 `But that backup plan changed the meaning of the call.`(issue: `…adds an operational rationale—that the humans served as a fallback for Muse—not established by the Ledger. The Japanese source already included the unsupported backup framing.`)、HC-012 `The test began… So people who thought…`(changed_causality、BLOCKING) | HC-006のS1は`ACCEPTABLE→BLOCKING`(降格**不成立**)。HC-012はS1なし(Stage 2が直接BLOCKING) | HC-006: ④段落で`But that backup plan changed the meaning of the call.`→`Human contract workers handled some calls.`、HC-012: level 1 `So people who thought they were speaking with AI were actually speaking with human staff.`→`And people were actually speaking with human staff.`。品質regen 2回(`orphan_contrastive_opener(...)`+`vocab_difficulty_increased_fragment(+0.0905)`) | prior 2件のうち HC-006**解消**、HC-012**未解消**(`The opening still asserts that people thought an AI was calling…`)。**新規MAJOR1件**: HC-012 `“An AI called. That was what people thought as they spoke.”` |
| (上限) | cycle=4>`HARD_MAX_CYCLES=3`(L8724〜8726)→STAGE4 `cycle_limit_exhausted_after_recheck`。cycle 3 Recheckで残った`MUSE-HC-012`の1 claimは**Stage 2/S1を通っていない** | — | — | — |

### 問い(a) 新規MAJORの分類(確認)
cycle 1→2の2件、2→3の2件、3→最終の1件=**計5件のRecheck新規MAJOR全て、原文に最初から在った文**(Rewrite後の文ではない。cycle間の`en_text_before_rewrite`の差分はいずれも当該Rewriteの置換箇所のみで、新規MAJORの文は差分に含まれない)。分類:
- **前cycleで未検出(Stage 1 recall)**: HC-006 `The idea was practical…`(cycle 1→2)、HC-006 `But that backup plan changed the meaning of the call.`(2→3)。fixtureのStage 1 deviationに無く、Recheckが全文走査の結果として1cycle1〜2件ずつ見つけた。
- **同一判定の再浮上/判定ゆれ(S1で降格確定済みの文を、Recheckが再度MAJOR化)**: HC-012 `That was what people thought as they spoke.`(cycle 1 S1で降格確定→cycle 1 Recheckが再度`recheck_major`)、HC-012 `So people who thought they were speaking with AI were actually speaking with human staff.`(cycle 1 S1で`ACCEPTABLE→ACCEPTABLE`降格確定→cycle 3 Stage 2が`BLOCKING`、changed_causality付き。直前の文を足した形のclaim)、最終HC-012 `An AI called. That was what people thought…`(cycle 1・2のS1で降格確定済みの文を、cycle 3 Recheckが`recheck_major`)。
- Rewriteが新たに生んだ問題: **0件**。

→ 1 Rewriteで直るのは1箇所。しかし`MUSE-HC-012`の「人々がAIと話していると思っていた」という認識の主張は記事内に**少なくとも3箇所**(冒頭`An AI called…`、本文`So people who thought…`、`That was what people thought as they spoke.`)に分散しており、cycleごとに1箇所ずつ見つかった(コードのコメントL8230付近が「多箇所分散Rewriteの根本解決ではない(Phase2課題item8)」と既に認めている構造)。

### 問い(b) 同一cycle内の複数fact(確認)
`_run_stage3_cycle`(L8286〜)は**claimごとに**`run_stage3_for_claim`を順に呼ぶ(claim数=Rewrite call数)。同じ文を指す後続claimは`covered_by_earlier_rewrite_in_cycle`でskip(cycle 1: HC-006/HC-010の重複2件)。まとめて1回のRewriteにはしない。cycle 1はHC-006・HC-010の2 Rewrite+品質regen 2、cycle 3はHC-006・HC-012の2 Rewrite+regen 2。

### 問い(c) `HARD_MAX_CYCLES`到達後の扱い(確認)
`MAX_CYCLES=2`、`HARD_MAX_CYCLES=MAX_CYCLES+1=3`(L279〜283)。cycle 3は`extra_cycle_granted`(L8195〜8225。`cycle==MAX_CYCLES+1`でblocking件数が減った/同一fact_idの新しい箇所が現れたとき1回だけ)。cycle 3のRewrite→Recheck後、`cycle += 1`→`cycle > HARD_MAX_CYCLES`(L8724)でループ終了、`stage4_reason="cycle_limit_exhausted_after_recheck"`(L8726)。**到達時点の未解消claim(確認)**: `MUSE-HC-012` `“An AI called. That was what people thought as they spoke.”`(`recheck_major`)の**1件のみ**。Stage 2のmaterialityは**未判定**(上限到達後はStage 2を通らない)。過去の判定: cycle 1のS1で`That was what people thought as they spoke.`が`QUALITY→ACCEPTABLE`(降格確定)、cycle 2のS1で`AI called. That was what people thought as they spoke. ... people who thought they were speaking with AI…`が`ACCEPTABLE→ACCEPTABLE`(降格確定)。

### 問い(d) 費用内訳(確認、`agg_rep29_stage4_rca_01.json` `a4_cost`、call_log合計=¥4.3435・20 calls)
| cycle | Stage 2 | S1 | Rewrite | 品質regen | Recheck | cycle計 |
|---|---|---|---|---|---|---|
| 1 | 0.5071(2) | 0.2445(2) | 0.1510(2) | 0.1664(2) | 0.8057(1) | 1.8747 |
| 2 | 0.2728(1) | 0.1585(1) | 0.1036(1) | — | 0.5657(1) | 1.1006 |
| 3 | 0.1768(1) | 0.2339(1) | 0.1732(2) | 0.2326(2) | 0.5517(1) | 1.3682 |
| 計 | 0.9567 | 0.6369 | 0.4278 | 0.3990 | 1.9231 | 4.3435 |
Recheckが44%、Stage 2+S1が37%、Rewrite(regen含む)が19%。品質regen(¥0.399、9%)は`vocab_difficulty_increased_fragment`の僅かな増加(+0.0083)でも発火している。worst +¥3.34(rep24比)=Cap(+¥3)超過は、この instance 1件が3 cycle(各¥1.1〜1.9)を消費したことが全て。

### 後段だけで決定論的に解けたか
- 上限到達後の残claim(HC-012 `An AI called…`)は、同じ文が**既にStage 2+S1の2段で非BLOCKINGと確認された文**。既存のmateriality funnelを1回通すだけで(新ゲートなし)、非BLOCKINGなら`RESOLVED_REWRITE_THEN_DOWNGRADE`、BLOCKINGなら本当に残った重大(そのときだけ最終手段)と区別できる。ただし有料call(Stage 2+S1、約¥0.2〜0.4)なしに結果は確定できない(推測: 過去の2判定が非BLOCKINGなので非BLOCKINGの可能性が高いが、cycle 3のStage 2は隣接文で`BLOCKING`を出したため確定ではない)。
- 費用: cycle数を減らさない限りCap内に収まらない(1 cycle≈¥1.1〜1.9)。

## 4. rep27/28/29のHuman Review原因の推移(確認、設計書§12・§14・§16と本RCA)

| run | Human Review件数 | 内訳(STAGE4理由) | 根本原因(RCAで確認済み) |
|---|---|---|---|
| rep27 | 3 | A4 s1・A5 s1: `ladder_exhausted_without_full_rewrite`、neg3 s1: `unconfirmed_after_reverify` | L6とcarry-forwardの順序不整合、Recheck自己矛盾(件数一致バグ) |
| rep28 | 3 | changed_scope s1・meta s2: `ladder_exhausted_without_full_rewrite`、unsupported_new_claim s1: `degenerate_rewrite_output` | actor_guardの日英言語不一致による過剰拒否、1文記事のtitle delete |
| rep29 | 3 | meta s1: `same_claim_fact_id_reblocked`、meta s2: `violation_span_unverified`、A4 s1: `cycle_limit_exhausted_after_recheck` | 本RCA(記録バグ+古いclaim、合成claim、cycle上限後にfunnelを通らない) |

**9件全て「Rewriteが本当に直せない重大」ではなく実装・形式上の不整合**(確認。rep29aの1件=related_fact_id空のfail-closedも同様)。`agg_rep29_stage4_rca_01.json`の`stage4_reason_by_run`で理由コードの内訳を再確認(rep27: ladder_exhausted 2・unconfirmed 1、rep28: degenerate 1・ladder_exhausted 2、rep29: 3件)。

## 5. 構造的な見立て(個別穴埋めか構造問題か)

- **個別穴の連鎖である側面(確認)**: 毎回、原因は別の実装不整合。個別に直すたびに次の出口に到達している。本RCAの(1)は特に、`escalated_to_paragraph`記録の不整合を直しても古いclaimで`violation_span_unverified`へ倒れるため、**出口が連鎖しており、1つずつ直しても次の出口で止まる**ことを確認した(replay: 古い合成claim→`mismatch`)。
- **構造問題である側面(確認+解釈)**: §0の共通3構造(Rewrite成功≠解消、履歴のキーがclaim、出口が計数・形式条件でfunnelを通らない)が、rep27〜29の9件のうち少なくとも本RCAの3件と、rep27〜28の`ladder_exhausted`4件(guard失敗後に別の出口がない)に共通する。
- 判断: **構造的な見直しが必要**。個別の穴を3つ塞ぐ委任_11を直ちに実装するのではなく、(a)location単位の履歴、(b)Rewrite成功判定の強化、(c)出口のfunnel経由化、(d)最終手段(決定論)を一体で設計し、Opus#14(条件B・必須)で批判させる(設計書§17、packet `docs/pm/opus_packet_open233_kpi_recovery_02_04.md`)。

## 6. 確認できなかったこと(推測の区別)

- ③1文・④段落のRewrite案が実際にissueを解消するか(未生成のため推測。LLM依存)。rep27〜29の単独Rewrite cycle 29件では、level 1が22中18解消(`causality` 12/12、`actor` 2/5、`term_scope` 2/3、`time` 2/2)、③1文が2/2、④段落が4/5(`agg_rep29_stage4_rca_01.json` `single_rewrite_cycles`、確認)。actorの2/5は小標本で、うち3件の失敗は同一instance(meta_run03_advanced)の別cycle・sampleであり、「actorはlevel 1で直らない」と一般化できる根拠ではない(推測)。
- 上限到達後のFunnelの結果(Stage 2+S1が非BLOCKINGになるか)。
- rep29の他35 instanceへの副作用(今回は読まず)。
