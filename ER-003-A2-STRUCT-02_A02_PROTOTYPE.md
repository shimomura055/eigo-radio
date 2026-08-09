# ER-003-A2-STRUCT-02 A02構造支援プロトタイプ(Full Storyブロック分割+日本語signpost)

**管理ID: ER-003-A2-STRUCT-02**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE_BUILT / UNDER_EVALUATION`(テキストのみ、音声未生成、ユーザー評価待ち)**

## 1. 目的

ER-003-A2-STRUCT-01 Candidate A(Full Story 2〜3ブロック化+日本語
signpost)のプロトタイプを、A02(SNS規制記事)で実際に作成する。目的は
英文自体をこれ以上易しくすることではなく、**構造側からリスニング理解を
支える**ことの効果を検証すること。

## 2. 英文のベース

ご指示のとおり、英文は**再生成していない**。A2超一般語5語制限・
抽象→具体変換・固有名詞密度低減は再適用せず、ER-003-A2-03で生成した
A02のFull Story英文をそのまま使用した(spoken-firstは維持済みの状態)。

- ベースファイル: [er003_output/a2_p1_r3/A02/a2_article_raw.md](er003_output/a2_p1_r3/A02/a2_article_raw.md)
- sha256: `9f15928a80b2afa59018441d386bdf181b1bf0d3eea68f724bc477d2c738bf13`
- 英文本体への変更: **なし**(単語・文の追加・削除・言い換えは一切行っていない)

## 3. ブロック分割の設計

Full Story(タイトルを除く本文170語、7段落)を、内容のまとまりで3
ブロックへ分割した。

| ブロック | 内容のまとまり | 元の段落 | 語数 |
|---|---|---|---|
| Block 1 | 何が起きるか(発表・対象・時間帯) | 段落1-2 | 42語 |
| Block 2 | 具体的に何が変わるか(アプリ停止・フィード停止・開始時期) | 段落3-5 | 65語 |
| Block 3 | 実は完全禁止ではない・狙い | 段落6-7 | 63語 |

分割の判断基準は、話題の転換点(「何が発表されたか」→「具体的な変化」→
「実は抜け道がある、その意図」)であり、機械的に均等分割したものでは
ない。Block 2が最も長い(65語)のは、規制の具体的な内容(アプリ停止・
通知停止・自動再生停止・フィード停止・開始時期)が集中しているため。

## 4. 日本語signpostの設計

各ブロックの間に、短い日本語の一文を挿入する。既存の番組で使われている
「ポイント解説」等の案内文と同じトーンとし、内容を先取りしすぎない
(ネタバレしすぎない)ことを意識した。

- **Block 1 → Block 2の間**: 「では、具体的に何が変わるのか見ていきましょう。」
- **Block 2 → Block 3の間**: 「ただし、これは完全な禁止ではありません。」

Block 1の前(Full Story冒頭)には追加していない。既存の番組構成では
Full Story本編の前に"Full Story intro"ナレーション(案内文)が既に
存在するため、二重の導入にならないようにした。

## 5. プロトタイプ全文(ユーザー確認用)

> **[Block 1 — 英語、42語]**
> Social media in the UK may soon say "goodnight" at midnight.
>
> The British government shared a new plan on July 15. It is for people aged 16 and 17. The government calls it a digital switch-off period. It would run from midnight to 6 a.m.
>
> **[日本語signpost]**
> では、具体的に何が変わるのか見ていきましょう。
>
> **[Block 2 — 英語、65語]**
> During that time, apps under the plan would not open at first. This first setting is called a default. Notifications would stop. Autoplay would stop too. This tool starts the next video on its own.
>
> The apps would also stop feeds that pick posts for each person. These feeds can keep people scrolling for a long time.
>
> The government plans to start it in spring 2027.
>
> **[日本語signpost]**
> ただし、これは完全な禁止ではありません。
>
> **[Block 3 — 英語、63語]**
> But it would not be a full ban. Teenagers could change the setting. Then they could use the apps late at night.
>
> The government wants this first setting to slow teenagers down. They would need to stop and make a clear choice. This small step may break the "just one more" habit. It may help more teenagers put down their phones and sleep.

## 6. 期待している効果(仮説、検証はしていない)

音声化した場合、現状(ブロック分割なし)は英語が**170語連続**で流れる
構成になる。今回のプロトタイプでは、英語が**42語→(日本語1文)→65語
→(日本語1文)→63語**という形に分かれ、最大の連続英語量が170語から
65語まで下がる計算になる。日本語signpostが「一度立ち止まって次の
話題を予告する」役割を果たすことで、聞き手が長時間連続で英語情報を
保持し続ける負荷が下がるのではないか、という仮説である。**この効果は
今回は検証していない(音声化していないため)。**

## 7. 構造(番組全体構成)について

この変更はFull Story内部の分割であり、番組全体の構造
(Preview/Key Phrases/Full Story/Point One/Point Two/In One Line)には
影響しない。ご指示どおり構造そのものは変更していない。

## 8. 非対象範囲(今回行っていないこと)

- 音声生成(TTS)
- A02英文の再生成・修正
- Listening Questions(Candidate B)の実装
- A01・ADD03への同様のプロトタイプ適用(今回はA02のみ)
- Key Phrase最終選定
- push

## 9. Source of Truth更新

[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-13を`PROTOTYPE_BUILT /
UNDER_EVALUATION`へ更新した。Candidate Aの採否(ADOPTED/REJECTED)は
ユーザーがこのプロトタイプを確認した後に判断する。

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)
