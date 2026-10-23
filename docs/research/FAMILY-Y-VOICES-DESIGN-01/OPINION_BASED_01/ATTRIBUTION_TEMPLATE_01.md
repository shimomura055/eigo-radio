# ATTRIBUTION_TEMPLATE_01 (委任_18 H / OF-Y6-10: 公開に向けた表示の雛形。**公開はPhase 2の対象外=雛形のみ**)

根拠: みらい議会データ利用規約(`/developers/interview-data-terms`、2026-07-29改定)第2条(CC BY 4.0)・第3条(再識別・誹謗中傷等の禁止)・第4条(出典表示)。CC BY 4.0は、(1)クレジット(出典) (2)ライセンスへのリンク (3)**改変したことの表示** (4)提供元が推薦・関与しているように示さないこと、を求める。

## 1. 記事ページ/概要欄に置く表示(日本語)
```
このVoicesは、実在の人物の発言ではありません。ネット上で公開されている複数の意見をもとに、編集・要約・再構成して作った声です(改変あり)。
データ出典:「みらい議会AIインタビュー(チームみらい)」(https://gikai.team-mir.ai/)
データ利用規約:https://gikai.team-mir.ai/developers/interview-data-terms
ライセンス:CC BY 4.0(https://creativecommons.org/licenses/by/4.0/deed.ja)
上記データを、要約・統合・言い換えなどの改変を加えて利用しています。チームみらいが本コンテンツを推薦・関与しているものではありません。
(TBS NEWS DIGの発言を根拠にした場合のみ) 一部は、TBS NEWS DIGの記事(https://newsdig.tbs.co.jp/articles/-/2618789)で紹介された街頭の声を、自分の言葉で要約して参考にしています。
```
## 2. 英語版(同じ内容。リスナー向け一文を含む)
```
These voices are not real individuals. They were composed by editing, summarizing, and recombining multiple publicly shared opinions (modified).
Data source: "Mirai Gikai AI Interview (Team Mirai)" (https://gikai.team-mir.ai/)
Terms of use: https://gikai.team-mir.ai/developers/interview-data-terms
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
The data was adapted (summarized, merged, and rephrased). This content is not endorsed by or affiliated with Team Mirai.
```
## 3. リスナー向けの一文(音声/本文の冒頭。OF-Y6-10。日英)
- 日本語(`er110_family_y_opinion_based_01.py`のINTRO_JA): 「これから聞くのは、実在の特定の人の話ではない。ネットなどで公開されている複数の意見をもとに、組み立てた声だ。」
- 英語(案): "The voices you are about to hear are not real, specific people. They are composed from several opinions shared publicly online."
- Voiceごとの出典説明は入れない(Phase 2の方針)。「みらい議会」「チームみらい」の名前は、リスナー向け一文には出さず、ページ・概要欄の表示(上記1・2)で出す(政党名が音声の中立感に影響するため。公開時の最終判断はユーザー)。

## 4. 公開前のGate(未実施。Phase 2では公開しない)
| Gate | 内容 | 状態 |
|---|---|---|
| G1 | 上記1・2の表示がページ/概要欄に実装されている | 未(雛形のみ) |
| G2 | **TBSのみが根拠の文**(`PROVENANCE_01.md` §3。現状4文)について、TBS NEWS DIGの許諾要否を確認するか、MR由来の内容に置換 | 未 |
| G3 | 再識別行為の禁止(第3条): Voiceに属性ラベル以上の個人特定情報を入れない・回答者の特定を試みない | 本稿は満たす(PROVENANCE §2で確認)が、公開時に再確認 |
| G4 | 誹謗中傷等への利用でないこと(第3条) | 本稿は満たす |
| G5 | 偏り(回答者は政党のAIインタビュー参加者の自己選択サンプル)をリスナーに誤認させない。『世論の代表』と見せない | 未(表示文に追記するか判断が必要) |
| G6 | 利用停止要請(第5条)・同意撤回データの除外(第2条末)に備え、取得日・取得データのスナップショットを保管 | `sources/`(git管理外)に保管済み |
