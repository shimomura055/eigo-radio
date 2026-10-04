# OPEN-233 span切断の自動復元(L6「完結文復元」)設計と¥0検証(委任_65、2026-10-04)

管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_65)。性質: 設計+既存ログの決定論replay(¥0、API課金なし)。**コード(runner・Prompt・Production path)は未変更**。L6はreplayスクリプト内の試作実装(`er052_output/open233_span_restore_offline_01/replay_01.py`)であり、runnerへは未配線、Production未接続、`PRODUCTION_WIRED`なし。
Status(Sonnet側の事実報告であり、分類・Production採用判断はFable/ユーザー): 設計案+¥0検証結果。次Trial(10本)は開始しない。

根拠となるユーザー指示: `DECISION_LOG.md`末尾「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、ユーザー指示[6回目]…)」に原文を逐語記録(Primary KPI=Checker起因のUSER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均+¥2/記事以内)。

## 0. 結論(先に)

1. rep24で残ったHuman Review 2件(A2A3 s2 cycle2・B3 s2 cycle2)は、L6で**いずれも記事内の1つの完結文に一意に復元**できた(§5-2、復元文を逐語で記載)。したがって今回の29件横断セットは、replay上はHuman Review 2→0件。
2. 2件の正体は、ユーザー指示の「途中切断」ではなく、(A2A3 s2)Checkerが記事にない語「the」を先頭に足した、(B3 s2)Checkerが末尾`...`省略に加えて記事の`while`を`so`へ言い換えた、という**「逐語でない語の混入+省略」**だった。そのため単純な切断・省略の処理だけでは解けず、L6に「逐語で記事に1箇所しかない最長の連続語列(アンカー)から文を決める」処理を含めた(§4)。
3. 「`6 percent, because …`」型2件(A2A3 s1/s2 cycle1)は現行の照合では**確定扱い**だが、確定範囲が`2.6 percent`の`6`から始まる(小数点を単語境界と誤認する既存の穴、§2-3)。数値境界の判定を直すとL6の対象になり、完結文へ復元される(replayで確認)。
4. 決定論replay(runner既存関数+L6試作、¥0): 過去全ログ(instance JSON 475本・BLOCKING claim 591件・一意182件)で、現行照合で未確定になる一意17件のうち、日本語claim(旧Checker言語、現行運用外)5件・precheck由来の説明文(非Checker出力)2件を除く**英語のChecker出力10件中5件がL6で復元**、残り5件はすべて「説明文混入型(d)」(L6の対象外、P-strict-closedの領域)。
5. **誤復元0**: (i)実例の復元全6件(未確定5+数値境界1)は`issue`と対応(§5-4)、(ii)確定済み127件を決定論的に壊した合成ストレス(切断・省略・語の置換・余分な語、889通り中、L6が呼ばれた721試行)で、復元は712件すべて正解の文と完全一致、**正解と無関係の文への復元0件**、残りは安全側(復元せず)に倒れた。
6. 追加API callなし(決定論のみ)。Rewrite対象が語句→文になる増分も、復元発生率(rep24実測0.053件/instance-run)×1件あたり最大約¥0.5=平均約¥0.03/記事。仮に全記事で1回発生しても約¥0.5/記事で、+¥2以内(§4-8)。
7. **残るHuman Review要因**(§7): (d)説明文混入型(P-strict-closedが4ガードで棄却するもの。過去ログ5 runs/591、rep24は0件)。L6は説明文混入型に触れない。Checker出力が記事に逐語アンカーを持たない完全な言い換え(候補0)も原理的に存在する。これらを0に近づける追加案(deterministicな位置語→構造要素の範囲追加、Checker span再取得1回)は§7に**USER_DECISION候補**として記載(本委任では実装・推奨しない)。
8. Opus独立技術レビュー(条件A)向けpacket作成済み: `docs/pm/opus_packet_open233_span_restore_01.md`。Opusへの依頼はFable。

## 1. 現状の照合経路(runner `er052_open233_self_recovery_flow_runner_01.py`、Grep確認済み行番号)

| # | 処理 | 行 | 要点 |
|---|---|---|---|
| 1 | 切替(Trial専用、既定OFF) | `VS_MATCH_EXT=False` 335、`VS_EXPLAIN_SPLIT=False` 358、`VS_STRUCTURAL_LABELS` 343、`VS_EDGE_PUNCT=".,;:!?"` 344 | rep24は`VS_MATCH_EXT=True`・`VS_EXPLAIN_SPLIT=True`・`HANDOFF_MODE=violation_span`・`JA_MODE=english_only` |
| 2 | 入口 | `resolve_violation_spans` 3632(violation_spans配列ならL3645`_resolve_spans_array`、それ以外は`_resolve_claim_string`) | 配列要素は要素ごとに確定、1要素でも不能なら全体不能 |
| 3 | 照合の入口(1箇所) | `_resolve_claim_string` 3894 | base→(`VS_EXPLAIN_SPLIT`ON かつ reason∈{explanatory_mixed,mismatch,label_only}のとき)`vs_explain_split_resolve` |
| 4 | base | `_resolve_claim_string_base` 3686。EN・JA各本文に`vs_resolve_in_text` 3577。確定=ちょうど1箇所(3710-3719、EN優先)。label_onlyは3722-3727。不能時reasonは`multi_match`/`explanatory_mixed`/`mismatch`(3729-3739) | 類似度・単語重なり・位置比は使わない |
| 5 | L0〜L3 | `vs_match_levels` 3508。L0=原文そのまま、L1=外側の引用符1組を外す、L2=空白・curly引用符の正規化、L3=L2+大小無視。`VS_MATCH_EXT`かつEN(`ext`、3514)のとき、1箇所一致に**単語境界**条件(`vs_word_boundary_ok` 3494、`_vs_wordch` 3482)を課し、満たさなければ次段へ | 単語境界は英数字・`_`・英数字に挟まれたアポストロフィだけを語構成文字とみなす(**`.`は語構成文字でない**、§2-3) |
| 6 | L4 | `_vs_resolve_in_text_core` 3591。曲線引用符の断片が2つ以上で残りが接続語・句読点だけなら各断片を別範囲に | 断片1つ+説明文は`explanatory`(3611) |
| 7 | L5(`VS_MATCH_EXT`) | `vs_edge_punct_match` 3544(`vs_resolve_in_text` 3582-3587がL0〜L4で確定しない場合のみ呼ぶ)。両端の`.,;:!?`を除いた文字列が1箇所(単語境界込み)なら確定 | 語は足さない・落とさない・置換しない |
| 8 | label_only | `vs_is_structural_label_range` 3919(確定範囲が`## In one line`行そのものなら確定不能) | |
| 9 | P-strict-closed | `vs_explain_split_resolve` 3795(Opus#7の4ガード=位置語/対比・参照語/残りの長さ/残りの逐語・隣接) | 説明文を**外す**処理。L6とは目的が違う |
| 10 | 不能の後 | `rewrite_ranges_ladder` 4129、4160-4167: `status!="resolved"`なら`method="violation_span_unverified"`(`target_not_locatable=True`、`span_unverified=True`)。cycle側6430-6444でSTAGE4、`stage4_reason="violation_span_unverified"` | Human Reviewへの唯一の道 |
| 11 | 確定後 | `rewrite_ranges_ladder`: 水準①`1_word_connective`(対象=確定範囲そのもの、`E1_RANGES_PROMPT_TEMPLATE` 4020-4048)→③`3_sentence`(`sentence_units=vs_expand_to_sentences(spans)` 4171)→④`4_paragraph`(4225-4250) | E1のPromptは既に「範囲の内側の最小編集だけ、不能なら空配列」と指示 |
| 12 | 文分割(拡張専用) | `vs_sentence_segments` 3934、`vs_expand_to_sentences` 3953、`_VS_SENT_END_RE` 3431(改行も区切り) | L6はこれを使う(新規の文分割を作らない) |
| 13 | 書き戻し | `vs_replace_once` 3971(対象が本文にちょうど1箇所の場合のみ置換) | 復元文が本文に2回以上あれば復元しない(§4) |
| 14 | 周回間の識別・Recheck | `claim_span_text` 3980(確定範囲を改行連結)、`annotate_claim_span_identity` 3989 | 復元文を渡す配線は追加不要(`ranges`が復元文になるため) |

Production(正式path)側の対応はer010 `locate_target_sentence` 68-90(exact_substring→**単語重なり0.25以上のfallback**、再推測)と、その呼び出し元(`er003_v1_n3_01_articles_generate.py:1178`、`er003_discovery_focus_staged_production_01.py:219・252`)。runnerのTrial経路とは別物(§6)。

## 2. 失敗2件+「6 percent」型2件の逐語(rep24、`er052_output/open233_self_recovery_flow_runner_01_rep24/`、`instances_s1|s2/<instance>.json`)

### 2-1. A2A3 s2 cycle2(`safety_A2A3`、`STAGE4_ESCALATION`、`violation_span_unverified`)

- Checker `claim_in_article`(逐語): `“the trade and investment deals that the Gulf states were working on with the United States”`
- Checker `issue`(逐語): `The article adds that the deals were already being worked on; HF-007 verifies the replacement with trade and investment deals but does not establish that status.`
- cycle2開始時点の記事の該当完結文(cycle1 Rewrite後の本文): `On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States.`
- 各レベルの失敗: L0/L1(外側引用符を外した`the trade and ...`)=記事に無し(記事は`by trade and investment deals`で`the`が無い)→L2/L3=同じく無し→L4=断片1つで残りなし(`explanatory`ではなく`none`)→L5=端の句読点なし→`none`。結果`status=unverified, reason=mismatch`、`per_lang={"EN":{"status":"none"}}`。P-strict-closed: `explain_split_rejected:fragment_not_in_article`。
- 型: Checkerが記事にない語`the`を先頭に足した(e: Checkerの言い換え)。切断でも省略でもない。

### 2-2. B3 s2 cycle2(`bgroup_B3`、`STAGE4_ESCALATION`、`violation_span_unverified`)

- Checker `claim_in_article`(逐語): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage...`
- Checker `issue`(逐語): `The word “so” presents the continuing concerns as a cause of the plan’s withdrawal. The Ledger says Trump cited productive discussions with Middle Eastern leaders, but does not establish that the continuing concerns caused the withdrawal.`
- cycle2開始時点の記事の該当完結文(1文、`## In one line`直下): `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.`
- 各レベルの失敗: 全体(`stage...`)は記事に無い(記事は`while`、claimは`so`)。L5で末尾`...`(3つの`.`)を除いても同じ`so`が残るため不一致。`status=unverified, reason=mismatch`。
- 型: 末尾`...`省略+Checkerが記事の`while`を`so`に言い換え(Checker自身のissueが「so」を問題にしているため、Checkerは「cycle1の本文にあった`so`」を引用した可能性。cycle2本文は既に`while`へ修正済み)。

### 2-3. A2A3 s1/s2 cycle1の「`6 percent, because …`」型2件(いずれも`covered_by_earlier_rewrite_in_cycle`)

- claim(逐語、s1・s2同一): `6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.`
- `issue`(逐語): `The article asserts that the danger around the strait affects gasoline prices and the cost of moving goods through crude oil; the Ledger does not verify these downstream effects.`
- 記事の該当完結文: `After the announcement, the rise in Brent crude futures briefly narrowed, but prices soon returned to nearly the high level seen before it; at the time of reporting, they were above $85 a barrel, up about 2.6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea remained, and people still did not know whether tankers could pass safely—showing that the charge had left the stage, but the dangerous route remained the real lead actor, with its distant danger reaching gasoline prices and the cost of moving goods through crude oil.`
- 現行照合の結果: **resolved(L0)、確定範囲の先頭=`6 percent, because ...`(`2.6`の`6`から)**。理由: claimは`2.6 percent`の先頭`2.`が欠けている(途中切断)が、`vs_word_boundary_ok`は`.`を語構成文字とみなさないため、`6`の前の`.`を単語境界と判定して確定してしまう(`_vs_wordch` 3482-3491)。これが「数値の途中から始まる確定範囲」という既存の穴。
- 影響: このままでは範囲が`6 percent, ...`で始まるため、水準①E1が範囲内を書き換えて書き戻すと`2.`+書き換え後、のように数値が壊れうる(今回のs1/s2は同じcycleの別claim[HF-003]の段落Rewriteで本文が先に変わり、`covered_by_earlier_rewrite_in_cycle`で処理されたため顕在化しなかった)。

## 3. 過去ログの未確定claim全件の型分類(現行設定`VS_MATCH_EXT=True`・`VS_EXPLAIN_SPLIT=True`でreplay)

収集: `er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json`(28ディレクトリ、instance JSON 475本、cycleごとのStage2 BLOCKING claim 591件=一意(claim,記事)182件)。各claimを、そのcycle開始時点の本文(cycle1=`en_text_before_rewrite`、以降=前cycleの`en_text_after_rewrite`)に対して`_resolve_claim_string`で再判定(rep24は記録済みhandoffと35/35一致)。`claims_detail_01.csv`・`unverified35_classification_01.csv`は同じinstance JSONの集計であり、unverified35のうち31件は現行の照合(L5・P-strict-closed)で既に確定、4件が未確定(下表d×3・c×1に含まれる)。

| 型 | 一意 | runs | L6の結果 | 代表例 |
|---|---:|---:|---|---|
| (a) 途中切断(先頭・末尾が語/数値の途中) | 0(*) | 0 | (*)未確定側には無し。確定側に1(数値境界、§2-3、7 runs) | `6 percent, because …`(確定扱いだが先頭が小数の途中) |
| (b) 末尾`...`/`…`省略 | 1 | 1 | 復元1(B3 s2) | `…so the flashy 20% plan left the stage...` |
| (c) 中間`...`省略 | 2 | 2 | 復元2 | `attacks by the United States and Iran ... continued` |
| (d) 説明文混入(Checkerの説明文+引用断片) | 5 | 5 | L6対象外(P-strict-closedの領域)。残る | `“Oil prices moved briefly…” The headline and one-line summary also state this…`(P: `dangling_position:headline,one_line`) |
| (e) 記事にない語の混入(Checkerの言い換え) | 2 | 2 | 復元2(A2A3 s2含む) | `the trade and investment deals that…`、`Users could not know … they’d asked AI to do.`(`they’d`) |
| (f) 複数出現(同じ断片が2か所以上) | 0 | 0 | 候補複数(例外)になる設計、実例なし | - |
| (g) その他: 日本語claim(旧Checker言語) | 5 | 7 | 対象外(現行はEN) | 日本語の説明文 |
| (h) precheck由来の数値差分説明文(Checker出力ではない) | 2 | 24 | 対象外(Checker起因でない) | `percent values found in article not matching any ledger fact: [2.0, 3.0]`(iter初期のみ、rep系は確定扱い) |
| 計 | 17 | 41 | | |

- 英語のChecker出力に限ると未確定は10件(b1+c2+d5+e2)。うちL6で復元できるのは5件(50%)、残る5件はすべて(d)。(a)(f)の実例は未確定側に無く、設計の網羅性は合成テスト(§5-5)と合成ストレス(§5-6)で確認した。
- 確定済み165件のうち、確定範囲の端が数値の途中なものは1件(一意)=§2-3の`6 percent`(7 runs: iter8・rep18・rep24 s1/s2ほか)。

## 4. L6「完結文復元」の設計

### 4-1. 位置づけと既存の基本線との関係

- Opus#5・#6の受け渡し基本線(`docs/pm/design_open233_violation_span_handoff_01.md`§2-4「再推測(不許可)=類似度・単語重なり・位置比・別のLLMの引用など、文字列の同一性でなく似ていることを根拠に範囲を選ぶ処理」、`opus_l2_review_open233_self_recovery_06.md`「Checkerが示した違反範囲を後段で再推測しない/縮小しない」)は、L6でも維持する。
- ユーザー指示(6回目)は「断片を含む意味の通る完結文が記事内で一意に特定できるなら、その文を対象範囲として復元する」ことを認めた。L6は**縮小ではなく、断片を含む完結文への決定論的な拡張**であり、(1)類似度・単語重なり・SequenceMatcherを使わない、(2)記事の部分文字列としての逐語照合だけで文を決める、(3)一意でなければ復元しない、(4)Checkerが挙げた語句を落とさない(範囲は拡張のみ)。ここで「語の置換を含むclaim」にも逐語の連続語列(アンカー)で対応するのは、基本線の字義(完全一致)を超えるため、**Opusレビュー論点**とし、ユーザー判断が必要になりうる点は§7に記載する。

### 4-2. 発火条件(L0〜L5と、`VS_EXPLAIN_SPLIT`ONならP-strict-closedでも確定しなかったclaimに限る)

claimが日本語(CJK文字を含む)なら対象外。説明文混入型は対象外(次のルール)。次のいずれかに該当した場合のみ発火:

1. (i)切断: 断片全体(端の句読点・外側引用符・空白を除き正規化後)が記事にちょうど1箇所あり、先頭側または末尾側が語・数値の途中(単語境界を満たさない。単語境界は`.`/`,`が数字に挟まれる場合を語構成とみなす拡張を含む)。
2. (ii)省略記号: 外側以外に`...`/`…`/`・・・`を含む。末尾のみ(`ellipsis_tail`)・先頭のみ・中間(`ellipsis_mid`、各部分を別々に探す)。
3. (iii)中間省略で、各部分は記事に一致するが全体は一致しない。
4. (iv)アンカー: 断片全体は記事に一致しないが、先頭側と/または末尾側に、記事に逐語でちょうど1箇所ある連続語列(アンカー)がある(Checkerが記事にない語を混入した型、A2A3 s2・B3 s2)。

**説明文混入型の除外**: 断片全体が記事に出現せず、かつ引用符の外側に「3語以上かつ記事に逐語で存在しない語句」があるclaimは、Checkerの説明文が混じっているとみなし、L6は触らない(P-strict-closedの領域。Opus#7の4ガードを迂回しない)。引用符を含む記事の文そのもの(外側が記事に逐語で存在、または2語以下)は説明文とみなさない。

**適用順序(P→L6)**: P-strict-closedは「説明文を外す」、L6は「断片を文へ広げる」ため、目的が逆。Pが確定したclaimはそのまま(L6は呼ばない)、Pが棄却した残りにL6を適用する。L6→Pの順にすると、説明文付きの断片をL6が先に文へ広げ、Pの4ガード(位置語・対比語・残りの長さ)が回避される恐れがあるため採用しない。L6はlabel_only(`In one line`行そのもの)には適用しない(label_onlyが優先、人間確認のまま)。multi_match(断片が2か所以上)も、L6では解消しない(例外、§4-6)。

### 4-3. 復元手順(決定論、擬似コード)

```
l6(claim, article):
  1. claimの外側の引用符1組を外す。末尾/先頭/中間の省略記号で分割し、部分に分ける(省略記号なしなら1部分)。
  2. 各部分を正規化(空白・curly引用符・大小。既存L2/L3と同じ)し、端の句読点・引用符を除く。
  3. 各部分について記事(正規化済み)を探索:
     - 全体一致が2箇所以上 → 候補複数。ちょうど1箇所 → その位置(単語境界を満たさなければ「切断」)。
     - 一致なし → アンカー探索: 先頭側の「最長の逐語連続語列」と末尾側のそれ。いずれも
       「記事にちょうど1箇所」「4語以上かつ20文字以上」「アンカー外(記事に無い語)の連続は6語以内」
       「アンカーがclaim文字数の50%以上」を全て満たす場合のみ位置を得る。先頭側・末尾側が両方あるなら順序が正しいこと。
  4. 各部分の位置の和集合を含む文群(`vs_sentence_segments`、改行・段落でまたがない)を求める。
     文数が2を超える/復元文が700字超/引用符が閉じない(隣接文で閉じても2文以内に収まらない)/構造ラベル行のみ → 復元しない。
  5. 省略記号が複数部分を持つ場合は、後ろの部分が前の部分より後にある組合せのうち、文群がちょうど1つに定まる場合のみ。
  6. 復元文群が記事にちょうど1箇所(`vs_replace_once`の条件)で、候補がちょうど1組 → 復元。
  結果: level="L6:sentence_restore"、restore_reason、元の断片、復元文、文数をhandoffに記録。
        候補0・複数、またはガード不通過 → 従来どおりunresolvable(例外=唯一のHuman Review経路)。
```

### 4-4. ガードとしきい値(根拠は§5の実測)

| ガード | 値 | 根拠(既存ログ・replay) |
|---|---|---|
| 断片の最小長(切断型・省略各部分) | EN 3語かつ12文字(中間省略の短い側の部分だけは1語から可。長い側が基準を満たすことが条件) | fixture 28本の3語連続の一意率95.5%・4語98.3%・5語99.2%・6語99.5%(replay §集計)。中間省略は組合せの位置順序と文群の一意性が追加の絞り込みになる |
| アンカーの最小長 | 4語かつ20文字 | アンカー型は逐語でない語が混じるので、断片型より厳しく4語(一意率98.3%)。合成ストレスで誤復元0 |
| アンカー外の連続語数 | 6語以内 | B3 s2=1語、A2A3 s2=1語、U04(`they’d`)=5語。7語置換は合成テストでcand0(安全側)。外れ値を許す上限として実例の最大5を超える6とした |
| アンカーのカバー率 | claim文字数の50%以上 | 実例は9割以上。類似度ではなく「逐語で連続する範囲の長さ」のみ |
| 連続文の最大数 | 2文 | fixtureの隣接2文は中央値123字・p95 218字・最大289字。3文以上は段落に近づき「最小」から離れる。3文に及ぶ合成ケースは候補0 |
| 復元文の最大長 | 700字 | fixtureの単文は中央値60字・p95 140字・p99 185字・**最大575字**(`6 percent`の文は約460字)。最大を超える余裕を持たせた上限 |
| 引用符(“ ”)を含む文 | 文群の引用符が閉じていること。閉じなければ隣接1文で閉じる場合のみ(2文以内)、それ以外は復元しない | 文分割が引用符内の`. `でも切るため |
| 数値境界 | `2.6`の`.`・`1,000`の`,`は語構成とみなす | §2-3の実例 |
| label_only | 構造ラベル行のみなら復元しない | 既存label_only(人間確認)を優先 |

### 4-5. 最小Rewrite原則の維持(仕組みと記録)

- 復元文はRewriteの**対象範囲**(`resolution["ranges"]`)になるだけで、ラダーの段は進めない。既存の水準①`1_word_connective`は対象=確定範囲(=復元文)のまま、**既存のE1 Prompt**が「範囲の内側の最小編集(単語・接続語・短い修飾の削除)だけを許し、不能なら空配列を返す」と明示している(runner 4020-4048)。Checkerの`issue`もそのままPromptに渡る(4211-4216)。新しいPromptは足さない。
- 水準①で直らない場合のみ③(`sentence_units`=復元文を含む文)へ進む。L6の復元文は既に文なので③の対象は同一文になる(段を飛ばさない、重複試行の費用は§4-8)。
- Recheckの`prior_issues`は`claim_span_text`(確定範囲を連結)を使うため、復元文が自動的に渡る(追加配線なし、3980-3998)。
- 記録: `handoff.level`に`L6:sentence_restore`、`restore_reason`(truncated_head/truncated_tail/ellipsis_tail/ellipsis_mid/anchor_with_substituted_words)、`restore_fragments`(元の断片)、`restored_sentence`、`n_sentences`を残す(委任_66でrunnerへ実装する場合の記録項目案)。評価では「復元されたclaimのうち、Rewriteが復元文の外側を変えなかったか」(最小Rewrite違反率)を件数で出す。
- 不要Rewriteの観点: L6は、現状Human Reviewで止まるclaimを自動で直しに進めるため、Rewrite件数は増える。ただしそれは「Checkerが実際にMAJOR/BLOCKINGとして指摘した問題」であり、Human Reviewに送る代わりに直す件数。正常記事の不要Rewrite率(既存の注意項目)はL6では悪化しない(L6はBLOCKING確定のclaimにしか作用せず、BLOCKINGにするか否かの判定は変えない)。

### 4-6. Safetyと例外(復元が失敗側に倒れる条件)

- 復元しない(従来のunresolvable=Human Review。唯一の例外経路)条件: 日本語claim/説明文混入型/断片が短すぎる(§4-4)/断片全体が2か所以上(候補複数)/アンカー無し(候補0)/アンカー外が7語以上/カバー率不足/先頭側と末尾側のアンカーが逆順/文が2文を超える/復元文が700字超/引用符が閉じない/label_only/復元文が記事に2回以上出現。
- 重大Factの見逃しは、復元が「より広い範囲を対象にすること」の副作用としては増えない。Checkerが指摘したclaimの文を含む範囲を対象にするだけで、BLOCKINGの判定・Safety-critical floor・Recheck・Stage 2の`materiality`には触れない。復元文がSafety-critical登録文と一致する場合も通常どおりBLOCKINGとして扱う(L6は材料の不足で止まっていたclaimを進めるだけ)。
- 「別の文」を選ぶリスク: ①断片全体が記事に逐語で1箇所(Checkerが記事からコピーした以上、その箇所が出典)、②アンカー型は4語・20文字以上かつ1箇所(fixture 4語連続の一意率98.3%)、③アンカーがclaimの半分以上、④アンカー外6語以内、⑤文群が2文以内、で封じる。それでも別文を選びうる残存リスクは、claimの語がその文で偶然にも長く連続して一致しつつ、実際は別の箇所の指摘という極端に稀な場合で、Recheck(prior_issuesに復元文を渡す)が「その文に問題がない」と判定して未解消=ladder次段/Stage 4で拾う。
- Failure時は安全側: 復元の判定ロジックで例外が出た場合・文分割に失敗した場合は復元せずunresolvable扱い(未確定のまま従来経路)。

### 4-7. 数値境界の補正(L6-N)

`vs_word_boundary_ok`(3494)を、数字に挟まれた`.`/`,`(`2.6`・`1,000`)を語構成文字とみなすよう拡張する。これにより`6 percent, because …`は(単語境界を満たさず)現行の確定から外れ、L6(i)切断として完結文へ復元される。**既存の確定結果が変わる唯一の箇所**であり、全ログで該当は一意1件(7 runs、rep24のA2A3 s1/s2 cycle1を含む)。変更後の結果は、範囲=数値の途中から始まる断片、から、範囲=その完結文、に変わる(§5-3)。実装範囲の判断(単語境界の関数自体を直すか、L6側だけの補正にするか)は委任_66とOpus論点。

### 4-8. Cost(追加API call 0)

- L6は決定論のみ(追加のLLM callなし)。変化は、Human Reviewで止まっていたclaimが「Rewrite(水準①)+Recheck」に進むこと。rep24実測の単価: Rewrite(`stage3_rewrite`)1call平均¥0.1093(28 calls)、Recheck(`stage1_recheck`)平均¥0.2753(21 calls)、Stage 2判定(`stage2_second_judge`)平均¥0.1402(45 calls)、instance-run平均¥0.4401(38 run)。
- 1件のL6復元で増える費用の上限見積り=Rewrite 1+Recheck 1+Stage 2 1回分≒¥0.11+¥0.28+¥0.14≒**¥0.5**。
- 復元の発生率: rep24では未確定2件(復元対象)/38 instance-run=0.053件/run。過去全ログ(英語のChecker出力、現行設定)では未確定10件/475 instance JSON=0.021件/run。平均追加費用=0.053×¥0.5≒¥0.03/記事。最悪ケースとして**全記事で1回復元が発生**しても約¥0.5/記事で、Cost KPI(平均+¥2/記事以内)に対して約4倍の余裕。
- 「1記事」は本Trialではinstance(1記事の自己修復1回)に相当する。Production(`er003`)の1記事あたりの追加はこれと同程度(L6は決定論の位置決め)と推定するが、実測ではない。

## 5. ¥0検証(決定論replay)の結果

実行: `.venv\Scripts\python.exe er052_output\open233_span_restore_offline_01\replay_01.py`(runner既存関数をimportするだけ、runner本体は未変更、API呼び出しなし)。出力: `er052_output/open233_span_restore_offline_01/results_01.json`・`results_01.md`(全claim・全復元文・全合成テスト・全ストレス結果)。

### 5-1. 母集団と集計

| 項目 | 値 |
|---|---:|
| BLOCKING claim(cycle単位、全28ディレクトリ・475 instance JSON) | 591 runs / 一意182 |
| 現行照合で確定 | 165一意 |
| 未確定 | 17一意(41 runs) |
| うち日本語claim(旧Checker言語・現行運用外) | 5一意 |
| うちprecheck由来の説明文(非Checker出力) | 2一意(24 runs、iter初期のみ) |
| **英語のChecker出力の未確定** | **10一意** |
| L6で復元 | **5/10(50%)**(b1・c2・e2) |
| L6対象外で残る | 5/10(すべて(d)説明文混入型、P-strict-closedが棄却) |
| 復元文の長さ(chars) | 116・116・134・161・275 |
| rep24の記録済みhandoffとreplay(base)の確定/未確定の一致 | 35/35 |
| L6の呼び出しで結果が変わった確定済みclaim | **0**(L6は未確定claimにだけ作用する構造) |
| 確定済みだが範囲の端が数値の途中(L6-Nで変わるもの) | 1一意(7 runs) |

### 5-2. 必須確認(1): rep24の失敗2件は一意に復元

| 件 | 復元文(逐語、1文) | Checker issueとの対応 |
|---|---|---|
| A2A3 s2 cycle2 | `On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the Gulf states were working on with the United States.` | issueは「deals were already being worked on」という状態の追加=この文の`that the Gulf states were working on`そのものを指す。**対応(OK)** |
| B3 s2 cycle2 | `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.` | issueは接続語「so」が因果を示すという指摘。復元文の接続は`while`(cycle1のRewrite済み)で、同じ文の同じ位置の接続語を指す。Recheckが「既に解消済み」と判定しうる。**対応(OK)** |

L6の`restore_reason`: A2A3 s2=`anchor_with_substituted_words`(アンカー外1語)、B3 s2=`ellipsis_tail`+`anchor_with_substituted_words`(アンカー外1語)。いずれも候補は1文のみ。

### 5-3. 必須確認(2): `6 percent, because …`型2件

L6-N適用後(§4-7)、2件とも`truncated_head`で、記事の完結文(§2-3、`After the announcement, … up about 2.6 percent, because attacks …`)へ一意に復元された(約460字、1文)。issue(ガソリン価格・輸送費への波及)はこの文の末尾`with its distant danger reaching gasoline prices and the cost of moving goods through crude oil`を指す。**対応(OK)**。

### 5-4. 必須確認(4): 誤復元0(実例の復元全6件を列挙、issueとの対応を仮判定)

| # | 出典 | claim | 復元文(要旨) | issue | 仮判定 |
|---|---|---|---|---|---|
| 1 | rep24 A2A3 s2 c2 | `the trade and investment deals that…` | July 14の文 | 上記 | 対応 |
| 2 | rep24 B3 s2 c2 | `…so the flashy 20% plan…` | In one lineの1文 | 上記 | 対応 |
| 3 | rep24 A2A3 s1 c1(同一claimは計7 runs) | `6 percent, because…` | After the announcementの1文 | 上記 | 対応 |
| 4 | iter2 neg7 c1(U04) | `Users could not know who was really doing the work they’d asked AI to do.` | `But users could not know who was really doing the work they had asked AI to do—and their personal information might reach that person.` | 記録なし(古い設定) | claimは復元文の前半の言い換え(`they’d`↔`they had`)。復元文の後半(個人情報の件)がRewrite範囲に入る点に注意(最小Rewrite原則のPromptで抑える)。**対応** |
| 5 | iter3 hormuz_run03_advanced c1(U05) | `At the same time, attacks by the United States and Iran ... continued.` | `At the same time, attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued.` | 記録なし | claimはこの文の前後(中間`...`)。**対応** |
| 6 | iter5 hormuz_run03_advanced c1(U07) | `“attacks by the United States and Iran ... continued”` | 同上(同じ文) | 記録なし | **対応** |

**誤復元(issueと無関係の文への復元)は実例で0件**。issueが記録されていない3件(4〜6)は、claimの語が復元文の逐語部分と一致していることで対応を仮判定した(目視相当)。

### 5-5. 合成テスト(rep24 B3・A2A3の記事本文で作成、全13件が期待どおり)

途中切断(先頭)=復元/途中切断(末尾)=復元/末尾`...`・`…`=復元/中間`...`=復元/短すぎる断片(語の途中で切断+2語)=`guard_rejected`/同じ断片が2か所に出現=`cand_multi`/引用符内の発話を含む文(`“not over yet”`)=復元/2文またがり=2文を復元/3文以上=候補0/記事に逐語アンカー無し(言い換え)=候補0/語の置換1語(B3型)=復元/先頭に余分な語1つ(A2A3型)=復元/置換10語=候補0(安全側)。全件の詳細は`results_01.md`「合成テスト」。

### 5-6. 誤復元ストレステスト(正解付き)

確定済みの一意127(記事,範囲)を、**決定論的に**壊す(乱数なし): V1先頭を1文字切断/V2末尾を1文字切断/V3末尾`...`/V4中間`...`/V5中間の1語を`so`へ置換/V6先頭に`the`/`also`を追加/V7末尾に`also`を追加。正解=元の確定範囲を含む文群。

- 889通り(127件×7種)のうち、変形不能41・現行照合で確定(V3全件)127を除いたL6が呼ばれた721試行で、**復元712件はすべて正解の文群と完全一致(exact)**。正解と無関係(disjoint)・部分的重なり・上位集合・部分集合の復元は**0件**。
- 安全側に倒れた(復元せず)9件: 説明文混入とみなして対象外4、候補複数1、アンカー外が長すぎる3(うち1件は31語置換)、逐語アンカー無し1。
- V3(末尾`...`)は127件すべて現行のL5で確定(prefixの断片範囲)し、L6は呼ばれない。末尾`...`で、接頭部分が逐語なら現行どおり「断片」が範囲になる(完結文への拡張はしない。Rewriteのラダーが水準③で文へ広げる)。この挙動は変えない。

### 5-7. 必須確認(5): 残る型(技術的に復元できない/しない残り)

- (d)説明文混入5件(rep9・rep23・iter5・iter7ほか。P-strict-closedの棄却理由: `dangling_position:headline,one_line`×2、`remainder_too_long`×2、`fragment_not_in_article`×1)。rep24は0件、過去ログ全体で5 runs/591(0.85%)。
- 逐語アンカー無し(候補0)、候補複数(同じ断片が2か所): 実例0件。設計上の例外として残る。
- (日本語claim・precheck説明文は、Checker起因ではない/現行運用外であり集計から除外。)

## 6. Production配線時の対応箇所(本委任では未実装、配線は`APPROVED_FOR_PRODUCTION`後)

- Trial runner: `_resolve_claim_string`(3894)内の、P-strict-closedの直後に`VS_SENTENCE_RESTORE`(既定OFF、Trial専用)でL6を呼ぶ。`vs_word_boundary_ok`の数値境界補正(L6-N)は単語境界関数側か、`vs_resolve_in_text`の確定直後の検査(切断検知)で入れる。委任_66の範囲。
- Production(正式path): Deviation→Local Rewriteの`locate_target_sentence`(`er010_ledger_local_rewrite_09.py:68-90`、呼び出し元`er003_v1_n3_01_articles_generate.py:1178`・`er003_discovery_focus_staged_production_01.py:219/252`)は、現状「exact_substring→**単語重なり0.25以上のfallback**(再推測)→not_found」で、本Trialの照合(L0〜L5・P・L6)とは別実装である。Production配線は、このfallback(類似度による文選び)を、決定論の照合(L0〜L6)に**置き換える**形になる(置き換えなしにL6を足すと再推測が残る)。この置き換えは、既存の「Safety-critical floor・retry・fallback・regeneration」と配線順序が絡むため、`OPEN-233-A1-PROD`の構成要素の一つとして追加し、`CURRENT_SPEC.md`へは`APPROVED_FOR_PRODUCTION`後に反映する(本委任ではSSOT未編集)。
- 既存retry/fallback/regenerationとの整合: L6はunresolvableを減らすだけで、上限回数・Gate・Safety-critical floor・Stage 4(最終cycle)の機構は変更しない。L6が復元しなかった場合は従来どおり`violation_span_unverified`→Stage 4。

## 7. KPI見通しと残る課題、USER_DECISION候補

### 7-1. KPI見通し(replay根拠、実flow未実証)

| KPI | 見通し | 根拠 |
|---|---|---|
| Primary: Human Review 0件 | 今回の29件横断セット: replay上は2→0件。過去全ログの英語Checker出力: 未確定10→5件(残りは(d)説明文混入型のみ)。Production全体で0件とは**まだ言えない**(§7-2) | §5-1・§5-7 |
| Safety: 重大Fact見逃し0件 | 悪化の要因なし(BLOCKING判定・floor・Recheckに触れない)。誤復元0(実例6+ストレス712、安全側9) | §4-6、§5 |
| Cost: 平均+¥2/記事以内 | 平均約+¥0.03/記事、全記事で1回発生しても約¥0.5/記事 | §4-8 |

実flowでの実証は、委任_66(実装+単体テスト+影響instance再実行)の後の29件再確認で行う(Human Review 0件、重大見逃し0件、費用)。

### 7-2. Human Reviewを0にするための残課題(本委任の実装範囲外、USER_DECISION候補として記載)

**U-1(要ユーザー判断の可能性あり): アンカー型(逐語でない語を含むclaim)を「再推測」でなく「決定論の逐語照合」として扱ってよいか。** 基本線は「完全一致のみ」だが、実際の失敗2件はどちらも逐語でない語の混入(`the`の追加、`so`↔`while`)だった。L6はこれを「記事に逐語でちょうど1箇所ある連続語列(4語・20文字以上、アンカー外6語以内、カバー率50%以上)」で位置決めする。類似度ではなく連続部分文字列であり、ストレス712件で誤復元0だが、「完全一致のみ」という既存基本線の拡張に当たる。Opusレビュー論点に含め、Opus後のFable判断で、基本線の解釈に関するユーザー判断が要るかを決める(Sonnetは決めない)。

**U-2(新規設計、本委任では未設計・未実装): 説明文混入型(d)の残り。** P-strict-closedの棄却理由は2種類。(1)`dangling_position`(`headline`/`one_line`): 説明文が「見出しにも同じ記述がある」と別の場所を指す。決定論の候補=記事の構造要素(見出し行・`## In one line`直下の1行、`_vs_explain_structure_elements` 3778)を追加の範囲に加える(位置語→構造要素の機械的対応)。(2)`remainder_too_long`: 引用断片は逐語で確定できるが、残りが長い説明文。候補=断片を範囲とし、残りの説明文は捨ててissueへ回す(P-strict-closedのガードを緩める案、Opus#7の判断を再検討する必要がある)。どちらも、新しい仕様=Opus独立レビュー(条件A)とユーザー判断が必要。**本委任の範囲外**であり、Sonnetは推奨しない(Fableが判断)。

**U-3(新規設計、本委任では未設計・未実装): 逐語アンカー無し(候補0)・候補複数の例外を0にする最後の網。** 決定論では原理的に解けない(Checkerが記事に無い文を言い換えて返した場合)。候補=Checkerのspan再取得1回(LLM call追加、失敗claim 1件につき約¥0.14〜0.28、発生率は§5の未確定率から約1〜3%で平均<¥0.02/記事程度の見積り)。再取得でも逐語にならなければHuman Review。非決定性が増える・LLM callが増えるため、Opus条件A+ユーザー判断が必要。**本委任では推奨しない**(実例が0件で、必要性の根拠がまだ無い)。

## 8. Opusに答えてほしい論点(`docs/pm/opus_packet_open233_span_restore_01.md`(a)と同一)

1. L6の発火条件・一意性・最小長ガードは「別の文を誤って選ぶ」Failureを封じているか。
2. 受け渡し基本線(再推測しない・縮小しない)との整合(特にアンカー型)。
3. P-strict-closedとL6の順序(P→L6)。
4. 最小Rewrite原則が実際に守られる仕組み(Promptと記録)。
5. Human Reviewに残る例外(候補0・複数、(d)説明文混入型)を更に減らす決定論的な手段はあるか。
6. Production配線時の矛盾(er003/er010/retry/fallback/regeneration)。
7. KPI(Human Review 0・重大見逃し0・+¥2以内)を同時に満たすか。

## 付録: 記録・ファイル

- replayスクリプト: `er052_output/open233_span_restore_offline_01/replay_01.py`(L6試作=`l6_restore`、ストレス=`stress_test`、合成=`run_synthetic`)
- 結果: 同ディレクトリ`results_01.json`・`results_01.md`
- 使用したrunner既存関数(変更なし): `_resolve_claim_string`・`_resolve_claim_string_base`・`vs_match_levels`・`vs_norm_with_map`・`vs_sentence_segments`・`vs_is_structural_label_range`・`vs_strip_one_pair`・`_vs_explain_extract_fragments`・`build_target_instances`
- L6の試作は`num_word_boundary_ok`(数値境界補正、§4-7)をreplay内に独自実装(runnerの`vs_word_boundary_ok`は未変更)
