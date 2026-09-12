# Opus Context Packet テンプレート(雛形、SSOTではない)

作成: `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01`(2026-09-12、準備段階)。
根拠: `OPEN_ITEMS.md` OPEN-142行(ユーザー原案A「context packet」+B「読むべき/
読まなくてよいファイル明示」+progressive disclosure)、
`docs/pm/PM_GOVERNANCE.md` 11節「Opus L2入力限定の運用」、
`.claude/agents/opus-consultant.md`「入力範囲」節。

改訂: `PM-TOKEN-EFFICIENCY-PHASE2-TEMPLATE-REVISION-01`(2026-09-12)。
Discovery Trial-12 Opus L2レビュー(`FAMILY-A-DISCOVERY-GENERALIZATION-
TRIAL-12-OPUS-L2-INTERPRETATION-01_REPORT.md`末尾「packet不足点(Phase 2
改善用)」9件、`PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01_REPORT.md`
7-5節に集約)を反映し、(b)へ7小節を追加・(c)へGrep確認欄を追加・(f)へ
計測項目を追加した。**packet総量の目安は2〜3万字以内**とする。本改訂で
記事本文等の転記分が増える一方、その転記によりOpusのProgressive
Disclosure(追加ファイル読込)が減るはずであり、**増えた転記分は
Progressive Disclosureの削減で相殺されるべき**(転記後もOpusが同じ
ファイルを追加で読む場合はpacket化の失敗であり、次回改訂で見直す)。

この雛形は**フォーマットの型のみ**を定めるものであり、正式ルール
(PM_GOVERNANCE.md・opus-consultant.md)を上書き・追加しない。既存ルール
「重要contextを省いて精度を落とすことは禁止」は本雛形にもそのまま適用される。
Sonnetが本雛形を埋めてpacketを作成し、Fableはpacketファイルのみを
opus-consultantへ渡す(元REPORT全文・巨大SSOT全文を追加で渡さない)。

---

## (a) 論点(限定)

このレビューで**Opusに答えてほしい問い**を、番号付きで具体的に列挙する。
「全体をレビューして」のような無制限依頼は禁止(論点を絞れていない証拠)。
各論点は1〜3行で「何を」「何と比較して」「何のために」を明記する。

例(Discovery Trial-12を想定した記入例、実データではない):
1. Trial-12のPart A適用結果は、Trial-11(タオル)と比較してREVIEW率・
   保険文発生がどう変化したか。対照アーム(baseline)は用意されているか。
2. Local Rewriteが発生した場合、rewrite前後で語数・near-duplicate文が
   Trial-11と同様のパターンを再現しているか。
3. (必須論点チェックリスト該当項目をここに転記。詳細は
   `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01_REPORT.md`
   「Opusレビュー品質rubric」節を参照し、対象Trialに合わせて具体化する)

### 論点と材料の対応チェック(必須)

上記で立てた論点それぞれについて、判定に必要な**材料(本文・成果物・
数値)が(b)/(c)に実際に含まれているか**を1行で確認する。材料を用意
できない論点は、ここで論点から外すか、(e)のProgressive Disclosureで
読ませる前提を明記する(「材料なしで論点だけ立てる」ことを禁止する)。

| 論点番号 | 必要な材料 | (b)/(c)のどこにあるか | 不足時の扱い |
|---|---|---|---|
| 1 | 例: Trial-12記事本文 | (b)「記事本文」節 | (不足なし) |
| … | … | … | … |

---

## (b) 主要数値表・要点(Sonnet REPORTからの転記、全文は渡さない)

Sonnet REPORTの「要点(5行)」に相当する要約と、比較に使う結果表のみを
ここに**転記**する(元REPORTファイルへのリンクは残すが、Opusに全文を
読ませる前提にしない)。

### 要点(5行以内)

1. …
2. …
3. …
4. …
5. …

### 結果表(例: Before/After比較、Trial間比較など)

| 項目 | Trial-11(タオル) | Trial-12(該当テーマ) | 差分 |
|---|---|---|---|
| REVIEW率 | | | |
| 保険文BROAD hit | | | |
| Local Rewrite件数 | | | |
| B1B語数 | | | |
| A2語数 | | | |

(表の行は対象Trialの必須論点チェックリストに合わせて増減してよい。
数値は実測値のみを記載し、推定値は「推定」と明記する。)

### 記事本文(必須転記)

対象記事(A2/B1B等)の`parts.json`相当の**全文**(通常約4,000〜5,000字)を
ここに転記する。本文読込なしでは①内容の具体的判定②語数超過の実感③
near-duplicate文脈④house phrase再出現、などが検証不能になり、
Progressive Disclosureで結局読ませることになる(Trial-12 packetでの
実測: 本文なしで4ファイル追加読込が発生。**最も費用対効果が高い改善点**)。
複数レベル・複数テーマを比較する場合はそれぞれ全文転記する。

```
(A2 parts.json相当 全文をここに貼る)
```

```
(B1B parts.json相当 全文をここに貼る)
```

### 語数target/tolerance実数値表

boolean(超過/非超過)だけでなく、**target語数・tolerance上限の実数値**
そのものを記載する。実数値がないと超過幅の逆算(推定)が必要になる
(Trial-12 packetでの実測不備)。

| セグメント | target語数 | tolerance上限 | 実測語数 | 超過幅 |
|---|---|---|---|---|
| A2 point_one | | | | |
| B1B point_two | | | | |

### near-duplicate実文

QAが検出したnear-duplicate pair(ratio値等)の**該当2文の実文**を転記する
(ratio数値のみでは、記事QAと音声QAの層間不整合のような論点に到達
できない、Trial-12 packetでの実測不備)。

| ペア | 文A | 文B | ratio |
|---|---|---|---|
| | | | |

### 比較対象Trialの定型句

前回Trial等、比較対象となる`in_one_line`/heading等の**定型句そのもの**
を転記する(型/house phraseの継続性判定には比較対象の実文が要る、
Trial-12 packetでの実測不備)。

| 対象Trial | in_one_line | heading | その他定型句 |
|---|---|---|---|
| | | | |

### comparison artifact生成有無

`comparison.html`等、目視比較用artifactが**今回生成されたか否か**を
明記する(未記載だと論点の充足判定が「不明」になる、Trial-12 packetでの
実測不備)。

- 生成有無: 生成した/生成していない
- 生成した場合のパス: 

### 費用按分単位

費用(¥換算)がある場合、その**按分単位**(テーマ単位/レベル単位/記事
単位など)を明記する(単位が曖昧だと規模見積りに推定を挟む必要がある、
Trial-12 packetでの実測不備)。

- 按分単位: 
- 単価(該当単位あたり): 

### failure modeの条件差

レベル間の表記差(例: A2 "twenty-four-hour" vs B1B "24-hour")など、
**同じ問題が条件によって現れ方・発生有無が変わる差分**があれば記載する
(この条件差がfailure modeの一般化可否の核心になることがある、
Trial-12 packetでの実測不備)。

- 条件差の内容: 
- どの条件で発生し、どの条件で発生しないか: 

---

## (c) 必要なProduction code/spec sectionの該当行範囲のみ

ファイル名と行範囲だけを列挙し、**本文は必要最小限**(数行の抜粋のみ、
ファイル全文の貼り付け禁止)。Opusが行範囲を自分でReadする場合はこの一覧を
そのまま使わせる。

**コード帰属(どの実装がどの振る舞いをするか)を記述する場合は、
`ファイル名:行番号`を必須とし、Sonnetが実際にGrepで実在確認したことを
「Grep確認」列に明記する**(未確認のまま記憶や推測で帰属を書くと誤記の
リスクがある。Trial-12 packetで`(?<!-)`の帰属先を誤記した実例があり、
Opus L2レビューが指摘するまで訂正されなかった)。

| ファイル | 行範囲 | この範囲が必要な理由 | Grep確認 |
|---|---|---|---|
| `er003_v1_n3_01_articles_generate.py` | 例: 794-1138行 | Fact Checker→Ledger Deviation→Local Rewriteの実行順を確認するため | 済(コマンド/結果概要を一言) |
| … | … | … | … |

---

## (d) Sonnet要約

Fableへ渡す前段としてSonnetが作成した所見・懸念・未解決点の要約
(300〜600字目安)。ここに書かれていない懸念をOpusが後から発見した場合は
下記(e)の手順で追加開示する。

---

## (e) Progressive Disclosure手順(Opus向け指示文、packetへそのまま含める)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。
> ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、
> 診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告する
> こと。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、
> 必要な事実を省いてまで読込量を減らしてはならない。

---

## (f) 入力文字数の自己計測欄

Sonnetが本packetを完成させた時点で、以下を記入する。

- (a)論点セクション(論点と材料の対応チェック含む): ____字
- (b)主要数値表・要点セクション(記事本文・語数実数値表・near-duplicate
  実文・比較対象定型句・comparison artifact有無・費用按分単位・
  failure mode条件差の7小節を含む): ____字
  - うち記事本文小節のみ: ____字(参考: target目安4,000〜5,000字)
- (c)Production code/spec抜粋セクション(Grep確認欄含む): ____字
- (d)Sonnet要約セクション: ____字
- (e)Progressive Disclosure指示文: ____字
- packet合計文字数: ____字(目安2〜3万字以内。超過する場合は理由を
  1行で記載する)
- 前回packet(改訂前)との差分: 増えた文字数の主因(例: 記事本文転記)
  と、それによって不要になったはずのProgressive Disclosure読込先を
  1行で対応付ける
- (参考)雛形自体の文字数(見出し・記入例・説明文を含む未記入状態、
  Python `len()`実測): 2,637字(2026-09-12改訂前の値。改訂後の値は
  次回packet作成時に実測して更新する)

Opus側は、診断完了後に以下を追記する(opus-consultant最終メッセージへの
自己申告、`.claude/agents/opus-consultant.md`の既存指示と整合させる)。

- Progressive Disclosureで追加に読んだファイル一覧
- 追加読込の概算文字数
- (a)の論点のうち、今回のcontextで十分に答えられなかった項目の有無
