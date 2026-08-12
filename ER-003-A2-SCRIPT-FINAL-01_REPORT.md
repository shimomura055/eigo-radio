# ER-003-A2-SCRIPT-FINAL-01 実行報告(OPEN-31解消・A2最終台本確定)

**管理ID: ER-003-A2-SCRIPT-FINAL-01**
**実施日: 2026-08-12**
**ステータス: `SCRIPT FINALIZED`(台本確定のみ。音声生成・再assembleは実施していない)**

## A. 5件の最終結果

| # | 記事 | Before | After | 採用状態 | 理由 |
|---|---|---|---|---|---|
| 1 | A01 | `Rogers sent the ball across the front of goal.` | `Rogers crossed the ball into the box.` | **採用** | 放送英語として自然な"cross the ball into the box"へ改善。事実(誰が・どこへ)は不変 |
| 2 | A01 | `Messi sent the ball across goal from the right.` | `Messi crossed the ball from the right.` | **採用** | 同上。Point One「a good ball from the right」との整合を維持 |
| 3 | A01 | `The referee then added more time.` | `The game went into added time.` | **採用**(方針は既にDECIDED、今回台本へ反映) | サッカー放送の標準用語"added time"を使用 |
| 4 | A02 | `During that time, apps under the plan would not open at first.` | `During that time, apps under the plan would be switched off by default.` | **採用**(Source確認済み、詳細はB節) | 誤読リスク("起動できない"と誤解される)を解消 |
| 5 | ADD03 | 下記C節参照(段落全体) | 下記C節参照(段落全体) | **採用**(7/13→7/14の実時系列順へ再構成) | flashback構造による理解負荷を解消。新規事実の追加なし |

いずれも最終台本ソース(`er003_output/a2_p1_r3/{article}/a2_article_raw.md`)と、対応する
[ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)、
[ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)、
[ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md)
の両方へ反映済み。

## B. A02 Source確認

修正候補 `would be switched off by default` が元ニュースのどの意味に対応するかを、
Natural English Source(`er003_output/a2_p1_r3/A02/master_en_natural_source_approved.md`)
と照合した。

> "During those hours, covered apps would be **unavailable by default**, and
> notifications would be paused."

原文は「対象アプリはdefaultで利用不可(オフ)になる」という意味であり、修正候補
"would be switched off by default" はこれと**意味が一致**する。現行台本の
"would not open at first" が持つ「起動できない」という誤読可能性を、原意に即した
形で解消するものと判定し、**無条件停止することなく採用した**。

## C. ADD03

### 修正前(flashback構造)

```
Oil prices fell after Trump dropped the plan. But oil traders still worried about the strait.

The day before, Brent crude oil rose by about 10 percent. People worried about more fighting
between the United States and Iran. The planned fee also helped push the price up.

Brent then fell from its highest price that day. That price was above $87 a barrel. On July 14,
Brent still ended the day higher. It closed at $84.73 a barrel. The price was about 2 percent
higher than the day before. It was also Brent's highest price in a month.
```

### 修正後(7/13→7/14の実時系列順)

```
Brent crude oil rose by about 10 percent on July 13. People worried about more fighting between
the United States and Iran. The planned fee also helped push the price up. Brent reached its
highest price that day, above $87 a barrel.

After the fee was dropped, Brent fell back from that high. But oil traders still worried about
the strait. Even so, Brent still ended July 14 higher. It closed at $84.73 a barrel. The price
was about 2 percent higher than the day before. It was also Brent's highest price in a month.
```

### 説明

- 元の文章は「7/14(fee撤回で価格下落)→7/13への回想(急騰・$87超のピーク)→7/14(終値)」という
  順序で、日付が前後する構成だった。
- 修正後は「7/13(急騰・ピーク到達)→7/14(fee撤回・反落・それでも終値は前日比+2%高)」という
  実時系列順に並べ替えた。
- Natural English Source(`master_en_natural_source_approved.md`)の該当箇所
  ("Brent crude had surged roughly 10 percent the previous day... After the plan was
  scrapped, prices retreated from an intraday high above 87 dollars a barrel. Even so,
  Brent closed on July 14 at 84 dollars and 73 cents...")と照合し、事実関係(7/13に急騰・
  $87超のintraday高値／fee撤回後に高値から反落／7/14終値$84.73・前日比+2%・月間最高値)は
  すべて維持されていることを確認した。
- 旧文中で「価格が下落した」という同一の出来事が2回に分けて述べられていた箇所
  (冒頭の"Oil prices fell after Trump dropped the plan."と、後段の"Brent then fell from
  its highest price that day.")を、時系列順に並べ替えた結果、1箇所("After the fee was
  dropped, Brent fell back from that high.")へ統合した。事実の追加・削除ではなく、
  同一事実の重複記述を解消したものである。
- 文数は41→40(この段落のみで4文→3文)に変化したが、総語数は372語→368語で、内容の
  欠落はない。

## D. QA(6観点Naturalness QA)

生成担当(本タスク実施者)とは独立した観点で、Grammar / Idiomaticity / News narration
naturalness / Meaning preservation / A2 suitability / Spoken-first の6項目を確認した。

| 記事 | Grammar | Idiomaticity | News narration | Meaning preservation | A2 suitability | Spoken-first | 総合判定 |
|---|---|---|---|---|---|---|---|
| A01 | 問題なし | 実況英語として自然な"cross the ball into the box"等へ改善 | 改善 | Point One等との整合を含め維持を確認 | 全文18語以下、平易語のみ | 全文主語先頭のSVO | **PASS** |
| A02 | 問題なし。"would be switched off"は単純な一節の受動態(A2で回避対象の「複雑な受動態」には該当せず、同段落内の既存"is called a default"と同水準) | 自然 | 改善(誤読リスク解消) | B節でSource照合済み | 全文18語以下 | 主語("apps under the plan")は維持 | **PASS** |
| ADD03 | 問題なし | 自然な市況表現("fell back from that high"等) | 明確に改善(時系列の明確化) | C節でSource照合済み、新規事実なし | 全文15語以下(区間平均9.2語) | ほぼ良好。"After the fee was dropped, Brent fell back from that high."のみ4語の従属節が先行するが、元記事側にも同型の文頭従属節("The day before, Brent crude oil rose...")が既にあり、新規パターンではない | **PASS** |

3記事とも**PASS**。REVISE・HUMAN_REVIEW相当の問題は検出されなかった。

## E. 文長検査

`er003_a2_article.compute_a2_sentence_metrics()`(既存の実装済み関数、B1/B2と同型のロジック)
を使い、各記事の確定後の全文(Full Story + Points + In One Line)に対して計測した。

| 記事 | 平均文長 | 最長文長 | 18語超の文 | 文数 | 総語数(本文) | 修正前との差分 |
|---|---|---|---|---|---|---|
| A01 | 8.00語 | 13語 | 0件 | 41文 | 328語 | 平均8.1→8.0、総語数332→328(-4) |
| A02 | 8.84語 | 15語 | 0件 | 38文 | 336語 | 平均8.82→8.84、総語数335→336(+1) |
| ADD03 | 9.20語 | 15語 | 0件 | 40文 | 368語 | 平均9.07→9.20、総語数372→368(-4)、文数41→40(-1、C節参照) |

3記事とも平均文長≤11語・最長文長≤18語(CURRENT_SPEC.mdのA2仕様)を満たす。18語超の文は0件。

## F. 影響確認

Preview / Comments / Key Phrases / Points / In One Lineへの追加修正要否を確認した。

- **A01**: Point One「He helped Lautaro with a good ball from the right.」は修正後の
  Full Story("crossed the ball from the right")と矛盾しない。Preview・Comment1〜4・
  Key Phrases(shot on target / go ahead / come on / go out / turn the game around)は
  いずれも変更対象の文と無関係。**追加修正不要**。
- **A02**: Key Phrase 5「digital switch-off period」は変更対象と別の文
  ("The government calls it a digital switch-off period.")にあり無関係。他の4件
  (opt out / covered apps / urge to watch / personalized feed)も無関係。Preview・
  Comment1〜4も無関係。**追加修正不要**(なお"switched off"と既存Key Phrase内の
  "switch-off"は語幹が重なるが、同一概念の自然な反復であり問題ではない)。
- **ADD03**: Key Phrase 4「Brent crude oil」の`source_evidence`は元は
  `"The day before, Brent crude oil rose by about 10 percent."`だったが、今回の
  修正でこの一文自体は`"Brent crude oil rose by about 10 percent on July 13."`へ
  変わった。**"Brent crude oil"というフレーズ自体は語順を変えずそのまま残っており、
  Key Phrase選定自体は無効化されない**。ただし`keywords_selected.json`の
  `source_evidence`欄(選定時の引用文記録)は旧文言のままであり、これは選定プロセスの
  監査証跡(過去の記録)として意図的に変更していない。次回Key Phrase関連作業時に
  参照する場合は、この差分を踏まえること。Comment1〜4・Preview・Point One/Twoは
  いずれも無関係。**台本自体への追加修正は不要**。

## G. Source of Truth

- **OPEN-31の最終状態**: `DECIDED / CLOSED`(2026-08-12)。5件すべてを最終台本へ反映し、
  6観点Naturalness QAで3記事ともPASSしたため。
- **ARTIFACT_REGISTRY更新内容**: A01/A02/ADD03のCEFR-A2行のScript列を、OPEN-31解消を
  反映した`PASS`表記へ更新。あわせてPodcast組立列に「script確定により既存音声と
  内容が不一致(要再assemble)」を明記し、新規OPEN-35への参照を追加。A02の
  User Quality列には、ER-003-A2-AUDIO-AB-01時点の試聴承認が**script確定前の旧音声**
  に対するものである旨を追記。
- **DECISION_LOG更新内容**: 5件それぞれについて、既存の1件(added time)を`DECIDED / APPLIED`
  へ更新し、残り4件(Rogers/Messi/apps/Brent)を新規`DECIDED / APPLIED`として追加。
- **新規OPEN-35**: 「script確定済みだが3記事とも音声は未再生成」を追跡するため新設
  (`TBD`)。既存のOPEN-34(Cross-level仕様未反映)とあわせて、次回A01/A02/ADD03の
  A2音声assemble時に両方を反映する。

## 対象ファイルと変更概要

| ファイル | 変更内容 |
|---|---|
| `er003_output/a2_p1_r3/A01/a2_article_raw.md` | 最終台本ソース。項目1・2・3を反映 |
| `er003_output/a2_p1_r3/A02/a2_article_raw.md` | 最終台本ソース。項目4を反映 |
| `er003_output/a2_p1_r3/ADD03/a2_article_raw.md` | 最終台本ソース。項目5(段落再構成)を反映 |
| [ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md) | 統合台本ドキュメントを同期。付録表の記述も更新 |
| [ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md) | 同上 |
| [ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md) | 同上 |
| [DECISION_LOG.md](DECISION_LOG.md) | 5件の決定を`DECIDED / APPLIED`として記録(1件は既存決定の状態更新、4件は新規追加) |
| [OPEN_ITEMS.md](OPEN_ITEMS.md) | OPEN-31を`DECIDED / CLOSED`へ。新規OPEN-35(再assemble待ち)を追加 |
| [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) | A01/A02/ADD03のCEFR-A2行を更新(Script列のPASS化、Podcast組立列・User Quality列への注記追加)。凡例パラグラフも更新 |

意図的に変更していないもの(過去の実行時点の監査証跡として保持): 各記事の
`a2_vocab_qa_prompt.txt`・ASR文字起こしファイル・`keywords_selector_prompt.txt`等の
過去実行ログ、`a2_metrics.json`(A2-03生成時点のQA記録)、`keywords_selected.json`の
`source_evidence`欄(選定時点の引用記録)。

## 非対象範囲(今回実施していないこと)

- TTS生成・音声再assemble
- WPM調整・Pause変更・Outro変更
- B1/B2変更
- 新しいA2仕様検討
- Key Phrase発音生成
- ユーザー試聴済み音声の上書き

## 受入条件15項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | A01の3修正が最終scriptへ正しく反映されている | PASS |
| 2 | A02の修正について元Sourceとの意味一致を確認している | PASS(B節) |
| 3 | A02の意味一致が確認できない場合は勝手に確定せず停止・報告している | PASS(意味一致が確認できたため確定。停止は発生せず) |
| 4 | ADD03が7/13→7/14の実時系列順へ再構成されている | PASS(C節) |
| 5 | ADD03の再構成で新しい事実が追加・削除されていない | PASS(C節で照合済み) |
| 6 | 修正後全文がA2文長制約を満たす | PASS(E節、18語超0件) |
| 7 | 6観点Naturalness QAを実施している | PASS(D節) |
| 8 | Preview / Comments / Key Phrases / Points / In One Lineとの整合性を確認している | PASS(F節) |
| 9 | OPEN-31の5件それぞれについて最終状態を報告できる | PASS(A節) |
| 10 | 条件を満たした場合のみOPEN-31をCLOSEDにしている | PASS(G節) |
| 11 | ARTIFACT_REGISTRYに音声再生成・再assemble必要性が反映されている | PASS(G節、OPEN-35新設) |
| 12 | 音声生成・再assembleは行っていない | PASS |
| 13 | 仕様そのものを変更していない | PASS(CURRENT_SPEC.mdは無変更) |
| 14 | 変更ファイル一覧を提示する | PASS(上表) |
| 15 | テスト・QAの実施証拠を提示する | PASS(D節・E節、`compute_a2_sentence_metrics`の実行結果) |

**15項目全PASS。**

## Git / push

コード変更なし、ドキュメント・台本テキストのみ変更。commit・push結果は
チャット上の完了報告を参照。
