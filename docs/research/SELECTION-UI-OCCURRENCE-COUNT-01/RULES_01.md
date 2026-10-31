# RULES_01 — 出現回数の数え方(occ-v1)最終規則表(ユーザー確認用・1ページ)

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632 / 委任_02。実装=`er140_selection_occurrence_count_01.py`(AI API 0円・決定論)。根拠=`DESIGN_01.md` §2 + Opus条件Aレビュー必須6件の反映。
**ユーザー確認が要るのは、この表の「何を同じと数えるか」です(受入4)。** 確認後に正式採用(PRODUCTION_WIRED)とします。実装・公開URLでの動作確認は完了しています(`EVIDENCE_01.md`)。

## 何を数えるか
学習項目(Phrase/Word)ごとに、記事の **本文・Comment・Preview・In One Line** の英語文の中で、その表現が何回出てくるかを数えます(0の区分は表示しない)。
タイトルは別枠(合計に入れず、本文等が0回のときだけ「タイトルのみ1回」と表示)。日本語訳・説明文・KP解説・コメント欄(入力)は数えません。

## 規則表

| 区分 | 何を同じと数えるか | 例(見出し語 ← 本文) | 回数に |
|---|---|---|---|
| **確定** 完全一致 | 同じ語の並び(大文字小文字は無視、語の途中は不可) | `put away` ← `Put away` | 入れる |
| **確定** 活用形 | 動詞の -s/-ed/-ing・不規則変化、名詞の複数形(承認済みer105の活用表) | `leave out` ← `left out` / `supplement` ← `supplements` | 入れる |
| **確定** 先頭の be/have/do | `be`/`have`/`do` が先頭の表現は活用形も同じ | `be in the way` ← `was in the way` | 入れる |
| **確定** 人称・目的語の穴 | `someone/something/one's/oneself`(`sb/sth`も同じ)が代名詞1語で埋まる | `pull someone under` ← `pulled him under` | 入れる |
| **確定** 句動詞の分離 | 動詞と不変化詞の間に代名詞1語。ただし `in/on/over/up/down…` のように前置詞にもなる語は、直後が句読点・文末のときだけ | `put away` ← `put it away` / `put it in.` | 入れる |
| **確定** a/an ↔ this/that | 冠詞の言い換え(`the` は別物なので数えない) | `draw a line` ← `draw that line` | 入れる |
| **保留** 名詞句・人名の穴 | 穴や分離の間が名詞句/人名 | `hold someone back` ← `hold the whole team back` / `pull someone under` ← `pulled Tom under` / `put away` ← `put the books away` | 入れない |
| **保留** 前置詞かもしれない分離 | 直後に語が続く | `put in` ← `put it in boxes` | 入れない |
| **保留** 別の語にもなる活用形(1語の項目) | `build→building`、`lie→lay`、`good→goods`、`see→saw` など承認済みer105の除外表に載る形 | `build` ← `building` | 入れない |
| **保留** 活用済み語の他の活用形 | `bothered` に対する `bother/bothers` | | 入れない |
| **数えない** | 語の途中(`insight`≠`in sight`)・ハイフン語・句読点/改行/文をまたぐ一致・縮約 `'s`(let's/it's)・派生語(persuade≠persuasion)・語の挿入(`make daily life work`)・4語以上離れた分離・`the` への置換・意味の違い(下記) | | 入れない |

保留は **加算せず**、画面に「＋似た形N（未計上）」と小さく併記します(「回数が少ないのは数え漏れかも」を見える化)。
本文の取得できない区分は0にせず「※Comment・Preview未集計」と表示。数えられない候補(本文等0回かつタイトル0回)は「出現回数を確認できません」(0回とは書かない)。

## 画面表示(各候補の日本語訳の下に1行)
```
出現 6回｜本文4・Comment1・In One Line1  （put it away、put that away含む）
出現 5回｜本文3・Comment1・Preview1  （left out含む） ＋似た形1（未計上）
出現 本文等0回・タイトルのみ1回          ← タイトルだけに出る項目
出現回数を確認できません                  ← 数えられない項目(0回と断定しない)
出現 1回｜本文1  ※Comment・Preview未集計  ← 区分の本文が取得できなかったとき
```
「数えた形」は括弧の中に直接出ます(スマホでも見える。PCでは行にマウスを載せると全形の内訳も出ます)。回数は参考情報で、選択条件・並び順・Done・コピー内容には一切影響しません。

## 限界(正直な注記)
- **多義(同じ綴りで意味が違う)は判別しません。** 例: `in the way` の「邪魔」と別の意味が同じ綴りなら、どちらも数えます。判別の仕組みを作ると過剰になるため(ユーザー原文)。実データ253項目の全件確認では誤カウント0でした。
- 保留は「数えない側」に倒しています。真の出現を数えそびれる可能性があり(実測: `bother me` 等2件)、その分は「＋似た形N」で見えます。
- 不規則な活用・be/have/doの縮約(`I'm`/`he's`)は表にあるものだけです。評価用の緩い基準(oracle)も同じ限界を持つため、「取りこぼし0」は「oracleが見つけた範囲で0」という意味です(`PRECISION_01.md` §7)。
- 選定後に本文が変わった記事(Local Rewrite等)は、回数が選定時の候補docの値(`occurrence_count`)とずれることがあります。export時の自己検査が警告します(実例: `surname_choice` の `adopted` 4→3)。

## 確認したいこと(ユーザー判断候補)
上の表の「確定」と「保留」の境界(特に: ①`put it away`のような代名詞1語の分離を確定にしてよいか ②1語の項目で `building`/`lay`/`goods`/`saw` などを保留にしてよいか ③名詞句・人名の穴を保留にしてよいか)が、ユーザーの意図に合っているかをご確認ください。ずれがある場合は表の行を変えるだけで対応できます(実装は表と1対1)。
