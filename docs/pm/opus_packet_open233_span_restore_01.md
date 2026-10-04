# Opus Context Packet: OPEN-233 L6「完結文復元」設計(条件A独立レビュー)

作成: 委任_65(2026-10-04、Sonnet)。雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`(a)〜(g)。Opusへの依頼はFable。
本packetはSSOTではない。Production未接続・未実装(replayのみ)・`PRODUCTION_WIRED`なし。

---

## (a) 論点(限定)

管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_65)。対象: Checker返却spanの途中切断・`...`省略・語の混入を、Human Reviewなしで自動解決する後段照合の新レベル「L6 完結文復元」の設計(未実装、replayのみ、Production未接続)。

KPI(ユーザー指示[6回目]、`DECISION_LOG.md`末尾に原文記録): Primary=Checker起因のUSER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均+¥2/記事以内。**「Human Review維持」を推奨にする案は不可**(前回の「現状維持」推奨は撤回済み)。

1. L6の発火条件・一意性・最小長ガードは、「断片を含む別の文を誤って選ぶ」Failureを封じているか(特にアンカー型=逐語でない語が混じるclaimを、記事に逐語で1箇所ある連続語列で位置決めする部分)。
2. 受け渡し基本線(Opus#5・#6: Checkerの範囲を後段で再推測しない・類似度で縮小しない)との整合。ユーザー指示は「断片を含む完結文への決定論的拡張」を認めたが、アンカー型は「完全一致のみ」という基本線の字義を超える。許容範囲か、別の決定論的手段があるか。
3. P-strict-closed(説明文を外す)とL6(断片を文へ広げる)の順序(P→L6案)。
4. 最小Rewrite原則が実際に守られる仕組み(既存のE1 Prompt+ラダー+`issue`のみで足りるか、復元文が長い場合の逸脱をどう検知するか)。
5. Human Reviewに残る例外(候補0・候補複数・説明文混入型(d))を更に減らす決定論的手段はあるか(U-2/U-3が妥当か、より単純な案はあるか)。
6. Production配線時の矛盾(er003・er010 `locate_target_sentence`の単語重なりfallback、retry/fallback/regeneration)。
7. KPI3つを同時に満たすか。replay根拠は十分か(母数・ストレステストの妥当性)。

### 論点と材料の対応チェック

| 論点番号 | 必要な材料 | (b)/(c)のどこにあるか | 不足時の扱い |
|---|---|---|---|
| 1 | 失敗2件逐語・ガード値・replay・合成ストレス結果 | (b)失敗2件、ガード表、replay結果表、ストレス | 不足なし |
| 2 | 基本線の原文引用 | (b)「基本線との関係」 | 不足なし |
| 3 | P-strict-closedのガードと棄却理由 | (b)P棄却理由、(c)runner 3795-3891 | 不足なし |
| 4 | E1 Prompt原文・ラダー | (b)Prompt抜粋、(c)runner 4020-4048・4211-4250 | 不足なし |
| 5 | (d)型5件の実例 | (b)残る型の表 | 不足なし |
| 6 | er010 `locate_target_sentence`・呼び出し元 | (b)抜粋、(c) | 不足なし |
| 7 | 費用単価・発生率 | (b)費用見積り | 不足なし |

---

## (b) 主要数値表・要点

詳細(全文・全claim・全復元文): `docs/pm/design_open233_span_sentence_restore_01.md`、`er052_output/open233_span_restore_offline_01/results_01.md`・`results_01.json`、スクリプト`replay_01.py`(Opusは本packetで足りない場合のみ参照)。

### 要点(5行)

1. rep24のHuman Review 2件は、**Checkerが記事にない語を混ぜた**型(A2A3 s2: 先頭に`the`、B3 s2: 末尾`...`+記事の`while`を`so`へ言い換え)で、単純な切断・省略ではなかった。L6は、記事に逐語で1箇所ある最長の連続語列(アンカー)から1文を決め、2件とも一意に復元した(replay)。
2. 「`6 percent, because …`」型2件は現行照合では確定扱いだが、確定範囲が`2.6 percent`の`6`から始まる(`.`を単語境界と誤認する既存の穴)。数値境界を補正すると完結文へ復元される。
3. 過去ログ(instance JSON 475本・BLOCKING 591件・一意182件)の英語Checker出力の未確定10件中5件をL6で復元、残り5件はすべて(d)説明文混入型。確定済みの結果をL6が変えた件数0。
4. 誤復元0: 実例6件はissueと対応、確定済み127件を決定論で壊した889通り(L6呼び出し721)で復元712件は全て正解の文と完全一致、安全側9件。
5. 追加API callなし。1件の復元で増える費用は最大約¥0.5、発生率0.053件/run(rep24)で平均約+¥0.03/記事、全記事で発生しても約¥0.5/記事。

### 基本線との関係(原文引用)

- `design_open233_violation_span_handoff_01.md`§2-4: 「**再推測(不許可、新設計で原則なくす)**: 類似度(SequenceMatcher等)・単語重なり・位置比・Ledger語彙・別のLLM(判定役)の引用など、**文字列の同一性ではなく「似ている」ことを根拠に範囲を選ぶ処理**。判定基準: 「変換後の文字列が記事中の部分文字列として**完全一致**し、一致が1箇所に定まるか」。定まらなければ再推測に進まず、…」
- `opus_l2_review_open233_self_recovery_06.md`: 「Checkerが示した違反範囲を後段で再推測しない/複数文なら複数文のままRewriteへ渡す/離れた複数箇所なら複数範囲として…」「成功条件: …Checkerが示した違反範囲を勝手に縮小しない」
- ユーザー指示[6回目]: 「spanが途中切断・...省略でも、断片を含む意味の通る完結文が記事内で一意に特定できるなら、その文を対象範囲として復元する。複数候補、本当に一意に決められない場合のみ例外扱い。範囲拡張で不要Rewriteが入らないよう、最小Rewrite原則は維持する。」
- L6の立場: **縮小ではなく拡張**(断片→それを含む完結文)。類似度・単語重なりを使わず、記事の部分文字列(逐語)照合のみ。アンカー型(記事にない語が混じるclaim)は、逐語の連続語列(4語・20文字以上、記事に1箇所)で位置決めし、アンカー外は6語以内・claimの文字数の50%以上がアンカー。基本線の字義(完全一致のみ)を超えるため、論点2として問う。

### 失敗2件の逐語(rep24、`er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s2/`)

**A2A3 s2 cycle2**(`safety_A2A3`、`STAGE4_ESCALATION`、`violation_span_unverified`、reason=`mismatch`、P-strict-closed棄却=`fragment_not_in_article`)
- `claim_in_article`: `“the trade and investment deals that the Gulf states were working on with the United States”`
- `issue`: `The article adds that the deals were already being worked on; HF-007 verifies the replacement with trade and investment deals but does not establish that status.`
- 記事の該当完結文: `On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States.`
- 失敗理由: 記事は`by trade and …`で`the`が無い。L0〜L5すべて不一致。

**B3 s2 cycle2**(`bgroup_B3`、同上、reason=`mismatch`)
- `claim_in_article`: `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage...`
- `issue`: `The word “so” presents the continuing concerns as a cause of the plan’s withdrawal. The Ledger says Trump cited productive discussions with Middle Eastern leaders, but does not establish that the continuing concerns caused the withdrawal.`
- 記事の該当完結文(1文、`## In one line`直下): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- 失敗理由: claimは`so`、記事は`while`(cycle1で修正済み)。末尾`...`を除いても不一致。

**A2A3 s1/s2 cycle1の「6 percent」型**(現行は確定=L0、`covered_by_earlier_rewrite_in_cycle`)
- claim: `6 percent, because attacks between the United States and Iran continued, … the cost of moving goods through crude oil.`(全文は設計書§2-3)。記事側は`…up about 2.6 percent, because attacks …`。確定範囲が`6`から始まる(`_vs_wordch` 3482-3491が`.`を語構成としないため単語境界OK扱い)。
- `issue`: `The article asserts that the danger around the strait affects gasoline prices and the cost of moving goods through crude oil; the Ledger does not verify these downstream effects.`

### 記事本文(必須転記、該当cycleの本文)

B3 s2 cycle2開始時点の記事(`## In one line`の1文が上記):

```
# 20% Withdrawn—but the Oil Chart Was Not Finished Yet

This news feels like a short play in three acts. Act One was “20%.” Act Two brought an unexpected turn. Act Three was an unexpected move in oil prices.

The curtain rose on July 13. Trump posted that the United States would seek a 20% charge on all cargo passing through the Strait of Hormuz. The aim was to recover the cost of US efforts to keep the strait safe.

But “20%” was not a finished system. The post did not say who would pay, how the money would be collected, or what legal basis would support it. For the moment, only a large number stood at center stage.

The number stayed at center stage for about a day. Then the story took a sharp turn.

### The 20% plan changes overnight

The next day, Trump said the 20% plan would be replaced by trade and investment projects between Gulf states and the US. He cited “very productive discussions” with Middle Eastern leaders. He also said no one should charge ships in the strait, and that he disliked fees.

The change was sudden. But to read the oil move, the dates must be kept separate. On July 13, Brent rose about 10% and settled at about $83 a barrel. The rise was linked to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz.

### The chart refuses to stay down

On July 14, after the withdrawal and replacement announcement, Brent crude futures briefly gave back some of their gains. Soon, they returned close to the high level before the announcement. At the time of reporting, Brent was up about 3%, above $85 a barrel. Its final settlement price was about $85, up about 2% from the day before.

## In one line

Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.
```

A2A3 s2 cycle2開始時点の記事(`On July 14 …`の文が上記):

```
# The 20 Percent Charge Left the Stage. Oil Worries Remained.

In the oil market, the lead role changed in a single day. First came a proposed 20 percent charge on all cargo passing through the Strait of Hormuz. The next day, the proposal disappeared from the stage. Normally, that might have brought some relief to crude oil prices.

But the market reacted differently. Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level. It was as if the market were saying, “The talk about the charge is over, but the story of the strait is not.” The fee was gone, yet the worry remained. To understand the turn, we need to look at what the charge was meant to do.

### A fee meant to protect the strait

On July 13, Trump proposed a 20 percent charge on all cargo passing through the Strait of Hormuz. The proposal was to repay the money the United States spends to keep the strait safe. Crude oil also passes through it, so trouble with transport could push its price higher.

The stage was ready for a quick change, but the market still had another question.

### The charge leaves, but the danger stays

On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States. He said the change came after “very productive discussions” with Middle Eastern leaders. The charge had left the stage, but that did not settle the market’s concern.



## In one line

The fee disappeared in a day, but the danger around the Strait of Hormuz remained.
```

A2A3 cycle1(fixture)の記事(`2.6 percent, because …`の文を含む):

```
# The 20 Percent Charge Left the Stage. Oil Worries Remained.

In the oil market, the lead role changed in a single day. First came a proposed 20 percent charge on all cargo passing through the Strait of Hormuz. The next day, the proposal disappeared from the stage. Normally, that might have brought some relief to crude oil prices.

But the market reacted differently. Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level. It was as if the market were saying, “The talk about the charge is over, but the story of the strait is not.” The fee was gone, yet the worry remained. To understand the turn, we need to look at what the charge was meant to do.

### A fee meant to protect the strait

On July 13, Trump proposed a 20 percent charge on all cargo passing through the Strait of Hormuz. The idea was that those carrying the cargo would repay the money the United States spends to keep the strait safe. Crude oil also passes through it, so trouble with transport could push its price higher.

The stage was ready for a quick change, but the market still had another question.

### The charge leaves, but the danger stays

On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States. He said the change came after “very productive discussions” with Middle Eastern leaders. The charge had left the stage, but that did not settle the market’s concern.

After the announcement, the rise in Brent crude futures briefly narrowed, but prices soon returned to nearly the high level seen before it; at the time of reporting, they were above $85 a barrel, up about 2.6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.

## In one line

The fee disappeared in a day, but the danger around the Strait of Hormuz remained.
```

### L6設計の要点(設計書§4)

- 発火: L0〜L5・(ONなら)P-strict-closedで未確定、かつ(i)切断(単語境界を満たさない、数値内の`.`/`,`は語構成)/(ii)`...``…``・・・`/(iii)中間省略の各部分が記事に一致/(iv)アンカー(逐語連続語列)が1箇所。日本語・説明文混入型(引用符の外側が「3語以上かつ記事に逐語で無い」)は対象外。label_only・multi_matchは対象外。
- 手順: 省略記号で分割→各部分を正規化(L2/L3と同じ)→記事に部分文字列として探索(全体一致/アンカー)→位置の和集合を含む文群(runner既存の`vs_sentence_segments`)を求める→2文以内・700字以内・引用符が閉じる・構造ラベルでない・記事に1箇所、を満たし候補がちょうど1組なら復元(`level="L6:sentence_restore"`、`restore_reason`、元断片、復元文を記録)。0/複数なら従来のunresolvable(唯一のHuman Review経路)。
- 順序: P→L6(Pが確定したclaimはそのまま、Pが棄却した残りにL6)。L6→Pだと、Pの4ガードを迂回して断片を文へ広げる恐れ。
- 最小Rewrite: 復元文は`resolution["ranges"]`(=水準①の対象)になるだけで、ラダーの段は進めない。既存の水準①E1のPrompt(runner 4020-4048)は既に「範囲の内側の最小編集のみ、不能なら空配列」で、Checkerの`issue`がそのまま渡る。`prior_issues`は`claim_span_text`(確定範囲の連結)なので復元文が渡る。

| ガード | 値 | 根拠(replay) |
|---|---|---|
| 断片の最小長 | 3語かつ12文字(中間省略の短い側は1語から可) | fixture 28本の3語連続一意率95.5%・4語98.3%・5語99.2% |
| アンカーの最小長 | 4語かつ20文字 | 4語一意率98.3%、ストレステスト誤復元0 |
| アンカー外の連続語数 | 6語以内 | 実例の最大5(`they’d`)、7語置換は候補0 |
| アンカーのカバー率 | claim文字数の50%以上 | 実例は9割以上 |
| 連続文の最大数 | 2文 | 隣接2文は中央値123字・p95 218字・最大289字 |
| 復元文の最大長 | 700字 | 単文は中央値60字・p95 140字・最大575字 |

### replay結果表(`results_01.md`、runner未変更・¥0)

| 項目 | 値 |
|---|---:|
| BLOCKING claim(全28ディレクトリ・instance JSON 475本) | 591 runs / 一意182 |
| 現行照合で確定 | 165一意 |
| 未確定 | 17一意(41 runs) |
| うち日本語claim(旧Checker言語) | 5一意(対象外) |
| うちprecheck由来(非Checker出力) | 2一意(24 runs、iter初期のみ) |
| 英語Checker出力の未確定 | 10一意 |
| **L6で復元** | **5/10**(末尾省略1・中間省略2・語の混入2[A2A3 s2含む])。B3 s2はこのうち末尾省略1(語の混入も併発) |
| L6対象外で残る | 5/10(すべて(d)説明文混入型) |
| L6が呼ばれて結果が変わった確定済みclaim | 0 |
| 確定済みだが数値の途中から始まる範囲(L6-Nで変わる) | 1一意(7 runs。A2A3 s1/s2 cycle1を含む) |
| rep24の記録済みhandoffとreplay(base)の一致 | 35/35 |
| 復元文の長さ | 116・116・134・161・275字 |

復元の仮判定(全6件=未確定5+数値境界1): すべてclaim/issueと対応、無関係の文への復元0(設計書§5-4)。

合成ストレス(確定済み127件を決定論で壊す、889通り): 変形不能41・現行で確定(V3末尾`...`は現行L5が断片範囲として確定)127を除くL6呼び出し721のうち、復元712は**すべて正解の文群と完全一致**、無関係・部分重なり・上位/下位集合は0、安全側(復元せず)9(説明文4・候補複数1・置換が長すぎ3・アンカー無し1)。合成13ケース(切断・省略・短すぎ・複数出現・引用符・2文・3文・言い換え・置換1語/10語)は全件期待どおり。

### 残る型(技術的に復元できない/しないもの)

| 型 | 一意 | P-strict-closedの棄却理由 | 例 |
|---|---:|---|---|
| (d)説明文混入 | 5(5 runs/591) | `dangling_position:headline,one_line`×2、`remainder_too_long`×2、`fragment_not_in_article`×1 | `“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly …` / `“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.` |
| 逐語アンカー無し(候補0)・同じ断片が2か所(候補複数) | 0(実例なし) | - | 合成のみ |

(d)はrep24で0件、rep23で1件(safety_A4 c3)。L6は触らない(P-strict-closedの4ガードを迂回しない)。追加案U-2(位置語→構造要素の機械的な範囲追加/残りが長い説明文のガード再検討)・U-3(Checker span再取得1回、LLM call追加)は未設計・未実装で、設計書§7に候補としてのみ記載。

### 費用見積り(rep24実測の単価)

| 項目 | 値 |
|---|---|
| Rewrite 1call平均 | ¥0.1093(28 calls、最大¥0.3528) |
| Recheck 1call平均 | ¥0.2753(21 calls) |
| Stage 2判定 1call平均 | ¥0.1402(45 calls) |
| instance-run平均 | ¥0.4401(38 run) |
| 1件の復元で増える最大費用 | Rewrite+Recheck+Stage 2各1回≒¥0.5 |
| 復元発生率 | 0.053件/run(rep24 2件/38run)、過去全ログ0.021件/run |
| 平均追加費用 | 約¥0.03/記事(最悪、全記事で1回発生でも約¥0.5/記事) |

按分単位: instance(1記事の自己修復1回)。

### E1 Prompt抜粋(最小Rewrite、runner 4020-4048)

`You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the SMALLEST possible edit: swap a single word or connective, remove a short qualifier, or split one sentence into two at a connective.` / `Try to resolve the issue using ONLY a minimal edit inside the range(s): …(without adding any new fact and without changing any other word). Do NOT rewrite the content or structure beyond this.` / `If this issue genuinely CANNOT be resolved by such a minimal edit, return {"revised_ranges": []} (do not attempt a larger rewrite).`

### Production側の現状(er010 `locate_target_sentence` 68-90、再推測)

`claim_in_articleが記事本文中に厳密一致する箇所を探す。見つからない場合、文単位に分割しword-overlap比率が最も高い文をfallbackとして採用する(overlap>=0.25)`。呼び出し元: `er003_v1_n3_01_articles_generate.py:1178`、`er003_discovery_focus_staged_production_01.py:219・252`。Production配線はこのfallbackを決定論の照合(L0〜L6)へ**置き換える**形になる(置き換えなしにL6を足すと再推測が残る)。

### comparison artifact・語数表・near-duplicate・比較対象定型句

該当なし(本件は照合設計であり、記事生成Trialではない)。comparison.html: 生成していない。failure modeの条件差: Checkerの言い換え・省略・切断の出方はClaim生成のたびに変わる(非決定性)。同じ記事でrep24 s1は発生せず、s2のみ発生(A2A3・B3とも)。

---

## (c) 必要なProduction code/spec sectionの該当行範囲のみ

| ファイル | 行範囲 | この範囲が必要な理由 | Grep確認 |
|---|---|---|---|
| `er052_open233_self_recovery_flow_runner_01.py` | 335・343・344・358 | 切替(`VS_MATCH_EXT`・`VS_STRUCTURAL_LABELS`・`VS_EDGE_PUNCT`・`VS_EXPLAIN_SPLIT`) | 済(Grep `VS_MATCH_EXT\|VS_EXPLAIN_SPLIT`、行確認) |
| 同 | 3482-3505 | 単語境界(`_vs_wordch`・`vs_word_boundary_ok`、`.`が語構成でない=§2-3の穴) | 済(Read) |
| 同 | 3508-3541 | `vs_match_levels`(L0〜L3、ENで単語境界) | 済(Read) |
| 同 | 3544-3567 | `vs_edge_punct_match`(L5) | 済(Read) |
| 同 | 3577-3613 | `vs_resolve_in_text`・L4(断片分割)・explanatory判定 | 済(Read) |
| 同 | 3686-3739 | `_resolve_claim_string_base`(確定=ちょうど1箇所、label_only、reason) | 済(Read) |
| 同 | 3795-3891 | `vs_explain_split_resolve`(P-strict-closed) | 済(Read) |
| 同 | 3894-3916 | `_resolve_claim_string`(照合の入口。L6の挿入候補位置) | 済(Read) |
| 同 | 3919-3968 | `vs_is_structural_label_range`・`vs_sentence_segments`・`vs_expand_to_sentences` | 済(Read) |
| 同 | 3971-3998 | `vs_replace_once`・`claim_span_text`・`annotate_claim_span_identity` | 済(Read) |
| 同 | 4020-4048・4160-4260 | E1 Prompt(最小編集)、`rewrite_ranges_ladder`の未確定時`violation_span_unverified`と水準①③④ | 済(Read) |
| 同 | 6430-6450 | cycle側: `violation_span_unverified`→STAGE4 | 済(Read) |
| `er010_ledger_local_rewrite_09.py` | 60-90 | Production側`locate_target_sentence`(単語重なりfallback) | 済(Read) |
| `er003_v1_n3_01_articles_generate.py` | 1178 | `locate_target_sentence`の呼び出し元 | 済(Grep) |
| `er003_discovery_focus_staged_production_01.py` | 219・252 | 同上 | 済(Grep) |
| `er052_output/open233_span_restore_offline_01/replay_01.py` | `l6_restore`・`anchor_scan`・`locate_part`・`stress_test` | L6試作(replay内) | 済(実行済み、結果は`results_01.md`) |

---

## (d) Sonnet要約

rep24の残Human Review 2件はユーザー指示の「途中切断・省略」ではなく、Checkerが記事にない語を混入した型(先頭に`the`、`while`→`so`)だったため、単純な切断・省略処理では解けず、L6に「記事に逐語で1箇所ある連続語列(アンカー)から文を決める」処理を入れた。これは基本線(完全一致のみ・再推測しない)の字義を超えるため、論点2で独立評価を求める。replay(¥0、475 instance JSON)では、2件が一意に復元され、誤復元は実例6件・ストレス712件で0。確定済みの結果は変えない(例外: 小数点を単語境界とみなす既存の穴=`2.6 percent`の`6`から始まる確定範囲1件)。残るHuman Review要因は(d)説明文混入型(過去ログ5 runs/591、rep24は0)で、L6は触らない。U-2・U-3(説明文混入の追加対策・Checker span再取得)は未設計の候補として論点5で問う。実flowでの検証は未実施(Opus後の委任_66で実装・再実行)。懸念: (1)ストレステストは確定済み127件の機械的変形であり、実際のChecker言い換えの分布は代表しない。(2)アンカー型の閾値(4語・20文字・6語・50%)は実例10件+合成が根拠で、母数が小さい。(3)Production(er003/er010)は現在、単語重なりfallbackで別文を選びうる別実装であり、L6の配線は置き換えを伴う。

---

## (e) Progressive Disclosure手順(Opus向け指示文)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。
> ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、
> 診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告する
> こと。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、
> 必要な事実を省いてまで読込量を減らしてはならない。

---

## (f) 入力文字数の自己計測欄(Python `len()`実測)

- (a)論点セクション(論点と材料の対応チェック含む): 1436字
- (b)主要数値表・要点セクション: 13813字
  - うち記事本文小節(3記事: B3 cycle2 1975字・A2A3 cycle2 1579字・A2A3 cycle1 2183字): 5737字
- (c)Production code/spec抜粋セクション(Grep確認欄含む): 1657字
- (d)Sonnet要約セクション: 660字
- (e)Progressive Disclosure指示文: 221字
- (g)発火条件+独立レビューブロック: 1727字
- packet合計文字数: 20253字(目安2〜3万字以内。範囲内)
- 前回packetとの差分: 該当なし(新規packet)。記事本文3記事の転記(約5737字)により、Opusが失敗2件の記事該当文を確認するための追加ファイル読込(instance JSON)を不要にした想定。

---

## (g) 発火条件の記入欄と独立レビューブロック

管理ID: PM-OPUS-INDEPENDENT-TECH-REVIEW-GATE-2026-10-02(`docs/pm/PM_GOVERNANCE.md` 11-3節)。

- 発火条件: **11-3節 条件A**(新しい構造・処理フローの設計)。根拠: 後段照合に新しい処理レベル(L6 完結文復元、アンカー型の位置決め、数値境界の補正)を追加する設計で、既存の受け渡し基本線(再推測しない・縮小しない)の解釈にも関わる。条件B〜Dには該当しない(同じ問題への2回修正ではない、Production採用提案前ではない、QCDの悪化ではない)。
- 重複レビューの確認: 同じ内容の既存Opusレビュー=`docs/pm/opus_l2_review_open233_self_recovery_05.md`(受け渡し再設計=Opus#5)・`opus_l2_review_open233_self_recovery_06.md`(後段対策=Opus#6)。**再レビューする**。理由: 設計変更。#5・#6の基本線は「Checkerの範囲を後段で再推測しない/縮小しない」だったが、今回はユーザー指示[6回目]により「断片を含む完結文への決定論的な拡張」を認める設計であり、レビュー時の前提が変わった(11-3節「重複レビューの回避」のうち、設計変更・レビュー時の前提が崩れたに該当)。#7(説明文混入のP-strict-closed)は、L6が触らない領域として位置づける。

以下は`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`の`---`で囲まれた本文を、改変せず貼ったもの(条件Aのため追加観点は無し、12観点は全件)。

---【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか
12. 個別パッチではなく再発防止になっているか

【追加観点(発火条件別)】
- 条件B(同じ問題へ2回修正しても再発): 「個別バグの連続なのか、根本設計に問題があるのか」を
  必ず明示的に判定すること。
- 条件C(Production採用候補の最終レビュー): 次の6点も必ず確認すること。
  Trial専用実装になっていないか / Production全体で矛盾しないか /
  初回・retry・fallback間で仕様が一致しているか / Dangling Referenceがないか /
  Failure時に安全側へ倒れるか / QCD上の新しい問題を生まないか。
  これはユーザーのProduction採用判断を代替するものではない(採用可否は
  人間ユーザーのみが決める。あなたは採用可否を宣言しない)。

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。---
