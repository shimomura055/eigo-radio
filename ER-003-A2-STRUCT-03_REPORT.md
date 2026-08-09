# ER-003-A2-STRUCT-03 実行報告(A02構造支援テキスト統合プロトタイプ)

**管理ID: ER-003-A2-STRUCT-03**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / UNDER_EVALUATION`**

## 1. 今回使用したA2言語仕様

[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)の「維持する項目」をそのまま
前提とした(Natural English Sourceから独立生成/総語数を意図的に削減
しない/Full Storyだけでニュースの核心が分かる/Point One・Twoは深掘り/
平均文長11語以下/最長18語以下/原則1文1メッセージ/構文単純化/平易な
一般語を優先/spoken-first継続/1文1数字継続)。「不採用済み」の4項目
(A2超一般語5語制限/抽象→具体一律変換/固有名詞密度低減/1文1新情報等)
は再適用していない。今回はこれらの言語仕様そのものを変更する作業では
なく、既存のA2-03本文に構造支援(Full Story分割+日本語Comment)を
かぶせる検証。

## 2. A02の11パート構造全文

[ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)
に、Preview〜In One Lineまでを指定順序で通した1本のMarkdownとして
まとめた(Intro/Outro/notification等の音声部品は対象外)。

## 3. Full Story分割位置

"The government plans to start it in spring 2027." の直後、
"But it would not be a full ban." の直前で分割した(段落境界: 元の7
段落のうち、Part 1=段落1〜5、Part 2=段落6〜7)。

## 4. 分割理由

Part 1のテーマは"What will the government do?"、Part 2のテーマは
"But can teenagers still use social media?"であり、"But it would not
be a full ban."から論点が「政府は何をするか」から「完全禁止ではない」
へ転換する。この意味上の転換点を境界とした(機械的な50:50分割ではない。
実際の語数もPart 1=107語、Part 2=63語と不均等)。

## 5〜8. 各Commentの役割

| Comment | 役割名 | 機能 |
|---|---|---|
| Comment 1 | Listening Focus | Full Story Part 1で何を聞けばよいかを1点だけ示す。答えは先に言わない |
| Comment 2 | Mid-story Recovery + Next Question | Part 1の最重要点を1点だけ日本語で回収し、Part 2で確認する問いを提示する |
| Comment 3 | Story Meaning + Bridge to Points | Full Story全体の意味・論点を整理し、Point One/Twoを聞く理由を作る |
| Comment 4 | Point Recovery + Bridge to In One Line | Point One/Twoの結論を短く回収し、In One Lineへつなぐ |

## 9. 各Commentが新規factを追加していない証拠

各Commentの内容を、隣接する英語パートの既出情報とのみ突き合わせた。

| Comment | 言及内容 | 出典(既出箇所) | 新規fact |
|---|---|---|---|
| Comment 1 | 「夜になるとSNSがどう変わるか」という話題提示のみ | Preview("深夜0時から午前6時までSNSを止める計画") | なし(話題の予告のみ、詳細は未言及) |
| Comment 2 | 「深夜にSNSの機能が自動で止まる計画」の回収 + 「設定を自分で変えられるか」という問い | Full Story Part 1("apps...would not open at first"、"This first setting is called a default"等) | なし。「自分で変えられるか」という問いはPart 2の内容を先取りして断定していない(疑問形のまま) |
| Comment 3 | 「設定は自分で変えられる」「完全な禁止ではない」の整理 + 「行動は変わるのか」という問い + 「2つの実験を見る」という予告 | Full Story Part 2("Teenagers could change the setting"、"it would not be a full ban") | なし。「2つの実験」はPoint One/Twoの存在を予告するのみで、実験の内容(309家族/Ofcom)には触れていない |
| Comment 4 | 「夜のルールだけでは解決しない」「最初の設定を変えるだけで行動が変わる可能性」の回収 | Point One(結論部)・Point Two(結論部) | なし。具体的な数値(309家族、7割/5割等)は再掲していない |

**結論: 4つのCommentとも、直前までに英語で語られた内容の要点整理・
予告のみで構成されており、英語パートより先に新しい事実を明かして
いない。**

## 10. 日本語全文翻訳になっていないことの確認

各Commentの文字数(日本語)と、対応する英語パートの語数を比較した。

| Comment | 日本語文字数(概算) | 対応する英語パート | 英語語数 |
|---|--:|---|--:|
| Comment 1 | 約28字・1文 | Full Story Part 1 | 107語 |
| Comment 2 | 約60字・2文 | Full Story Part 1(の要点1点) | 107語 |
| Comment 3 | 約70字・3文 | Full Story Part 2 | 63語 |
| Comment 4 | 約65字・3文 | Point One + Point Two | 約130語相当 |

いずれのCommentも、対応する英語パートの全内容を訳出するには明らかに
不十分な分量であり(要点1点への絞り込み、または問いかけの提示のみ)、
全文翻訳になっていないことを分量面からも確認した。

## 11. A2-03英語との差分

プログラムによる機械的な比較を実施した(`er003_a2_article.py`の
`split_article_sections`で実際のA2-03ファイルからFull Story/Points/
In One Lineを抽出し、文字列として突き合わせ)。

| 検証項目 | 結果 |
|---|---|
| Part 1(指定テキスト) == 元Full Story段落1〜5 | **完全一致**(`True`) |
| Part 1+Part 2の再結合 == 元Full Story本文全体 | **完全一致**(`True`) |
| Point One/Point Twoセクション | 元ファイルの該当箇所とテキスト完全一致(冒頭・末尾を確認) |
| In One Line | 元ファイルと完全一致: `"The UK hopes more teenagers will keep the night setting and simply go to sleep."` |

**結論: A2-03の英語本文は1文字も変更していない。** 分割は既存の段落境界
での切断のみであり、書き換え・言い換え・語順変更は一切行っていない。

## 12. 一般化可能な役割フレーム

[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)の「構造支援候補」節に
記載済み(Comment 1〜4の役割名・機能・長さ目安の表、Full Story分割
優先順位①意味上の転換点②時系列上の転換点③問題→例外④発表→反応
⑤What happened→What happened next/Why it matters)。原則2ブロック
とし、3ブロック化は将来候補として残すが今回のA02では使用していない。

## 13. 今回一般化しなかったもの

- 任意記事から自動で分割点を決定するコード(未実装)
- 日本語Commentを自動生成する汎用ロジック(未実装)
- A01への適用(未実施)
- ADD03への適用(未実施)

今回はA02の具体例を正確に作ることのみを目的とした。一般化の実装は
A02がユーザー承認された後に着手する。

## 14. Source of Truth更新内容

- [OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-13を、11パート構造の統合台本
  ([ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md))
  が完成した状態として更新した。ステータスは引き続き
  `PROTOTYPE_BUILT / UNDER_EVALUATION`のまま(CURRENT_SPECへは未反映)
- [A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)の構造支援候補節から
  本統合台本へのリンクを追加した

## 15. 作成・変更ファイル

- 新規: [ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)(11パート統合台本)
- 新規: 本レポート([ER-003-A2-STRUCT-03_REPORT.md](ER-003-A2-STRUCT-03_REPORT.md))
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)(OPEN-13の参照先更新)
- 更新: [A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)(統合台本へのリンク追加)
- コード変更: なし(検証用の一時スクリプトはスクラッチ領域のみで使用し、リポジトリには追加していない)

## 16. テスト結果

コード変更がないため、プロジェクト全体回帰テストの再実行は不要と判断した
(直近の実行結果1660件全合格が引き続き有効)。11節の差分検証は
`er003_a2_article.py`の既存関数(`split_article_sections`)のみを用いた
一時的な確認スクリプトで実施し、リポジトリへは追加していない。

## 17. Git status / 18. commit / 19. push未実行確認

commit済み(pushなし)。**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-STRUCT-02_A02_PROTOTYPE.md](ER-003-A2-STRUCT-02_A02_PROTOTYPE.md)、
[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)
