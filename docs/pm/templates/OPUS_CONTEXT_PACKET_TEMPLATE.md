# Opus Context Packet テンプレート(雛形、SSOTではない)

作成: `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01`(2026-09-12、準備段階)。
根拠: `OPEN_ITEMS.md` OPEN-142行(ユーザー原案A「context packet」+B「読むべき/
読まなくてよいファイル明示」+progressive disclosure)、
`docs/pm/PM_GOVERNANCE.md` 11節「Opus L2入力限定の運用」、
`.claude/agents/opus-consultant.md`「入力範囲」節。

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

---

## (c) 必要なProduction code/spec sectionの該当行範囲のみ

ファイル名と行範囲だけを列挙し、**本文は必要最小限**(数行の抜粋のみ、
ファイル全文の貼り付け禁止)。Opusが行範囲を自分でReadする場合はこの一覧を
そのまま使わせる。

| ファイル | 行範囲 | この範囲が必要な理由 |
|---|---|---|
| `er003_v1_n3_01_articles_generate.py` | 例: 794-1138行 | Fact Checker→Ledger Deviation→Local Rewriteの実行順を確認するため |
| … | … | … |

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

- (a)論点セクション: ____字
- (b)主要数値表・要点セクション: ____字
- (c)Production code/spec抜粋セクション: ____字
- (d)Sonnet要約セクション: ____字
- (e)Progressive Disclosure指示文: ____字
- packet合計文字数: ____字
- (参考)雛形自体の文字数(見出し・記入例・説明文を含む未記入状態、
  Python `len()`実測): 2,637字

Opus側は、診断完了後に以下を追記する(opus-consultant最終メッセージへの
自己申告、`.claude/agents/opus-consultant.md`の既存指示と整合させる)。

- Progressive Disclosureで追加に読んだファイル一覧
- 追加読込の概算文字数
- (a)の論点のうち、今回のcontextで十分に答えられなかった項目の有無
