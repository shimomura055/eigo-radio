# COPY_FORMAT_01 人間可読コピー形式(委任_06、2026-10-27。契約: フォーム(JS)と復元tool(Python)の両実装がこれに従う)

## 1. 形式(ユーザー例示どおり。見出しは固定文字列)
```
記事：<記事名>｜<Standard|Advanced>

① Key Phrase
- <英語>：<日本語訳>
（選択なし）                       ← 0件の区分はこの1行

② 追加解説
- ...

③ 本文意味表示
- ...

文法：選定なし                       ← 0件
文法：<文法名>                       ← 1件ごとに以下のブロック(N件なら繰返し)
【解説全文】
<解説全文をそのまま。末尾の内部終端記号「=====」だけ除く>
【解説ここまで】

自由コメント：<本文(複数行可)|なし>

照合コード(変更しないでください)：AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>
```
- 区切り文字は全角`：`。項目は`- 英語：日本語訳`1行。順序=フォーム表示順(データ順)。
- 日本語訳が`official`以外の項目は訳の後ろに`（仮訳・未確定）`/`（日本語訳未生成）`を付ける(現行の【仮訳・未確定】注記の人間可読版。復元時にdataの`ja_gloss_status`と一致を検査し、`official`以外は従来どおり確定ISSUE)。
- 「ChatGPTへ送信」のみ、先頭に`PREFACE_NEW`(`HANDOFF_DESIGN_01.md` §3)を付ける。「選定結果をコピー」は前置きなし。
- 表示しないもの: JSON、SHA全文、`candidate_id`一覧、`kind`、`candidates_all`、`ai_reference`(AI選定理由)、`user_confirmed_note_ja`。**消失はしない**=§3の照合コード+公開データJSONから復元できる。

## 2. 実例(AI島 Standard、ユーザー例示の10語。実データ`ai_island_temple__a2__prod.json`の語・訳と完全一致を確認[10語すべて実在])
```
記事：AIの仮想の島｜Standard

① Key Phrase
- carry over：持ち越す
- take a detour：寄り道をする
- card to play：使える手

② 追加解説
- worth paying attention to：注目する価値がある
- obstacle：障害物

③ 本文意味表示
- make a difference：影響を与える
- separately：個別に
- feature：性質
- Strategy：作戦
- setup：設定

文法：選定なし

自由コメント：なし

照合コード(変更しないでください)：AIF1-ai_island_temple__a2__prod-915481-25a7bce9-76f80f62-ccce40d25f-0-0-9cd3
```
(文法0件・コメントなし。AI島はユーザー正式決定により両レベル文法0件。照合コードの`g10`=`0`は「文法選定なし」を表し、`s10`は上記10項目の選択集合のhash)

### 文法1件ありの実例(AI島 Advanced、動作確認用の例。実際の確定内容ではない)
```
記事：AIの仮想の島｜Advanced

① Key Phrase
- carry over：次に持ち越す
- call on：頼む

② 追加解説
- look at separately：別々に検討する

③ 本文意味表示
（選択なし）

文法：関係節を含む長い主語
【解説全文】
【日本語訳】
その後、そのAIが建てられる塔の平均数は減少した。

【文法・構文の仕組み】
主語は **the average number of towers it could build** 全体です。中の **it could build** は **towers** を説明する関係節で、「そのAIが建てられる塔」という意味です。ここでは **towers** が **build** の目的語にあたるため、関係代名詞は省略されています。

文の中心となる主語は **the average number ...** で、主節の動詞は **fell**（減少した）です。つまり、「そのAIが建てられる塔の平均数」が減少した、と述べています。

【意味・ニュアンス・表現効果】
関係節 **it could build** によって、どの塔の数を指しているのかが「そのAIが建てられる塔」と限定されています。前の文では、AIの記憶から「岩を投げてブロックを得る」技法の説明が取り除かれたと述べられており、この文はその後に建てられる塔の平均数が下がったことを伝えています。焦点は、個々の塔ではなく、建てられる数の平均がどう変化したかにあります。
【解説ここまで】

自由コメント：文法の例文をもう少し短く

照合コード(変更しないでください)：AIF1-ai_island_temple__b1b__prod-78503a-5d8c1b12-00f14092-7bfb3e32aa-f9ccac25c2-89851cb6-437b```
解説全文は事前生成物と同一の文字列(データ`grammar[].body`)で、省略しない。`**`等のMarkdown記号も原文のまま保持する(ChatGPTには「コードブロックで逐語返却」を求める理由)。

## 3. 照合コード(1行・約75字)
`AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>`(区切りは半角`-`。`stem`は英数字と`_`のみ)

| 要素 | 内容 |
|---|---|
| `AIF1` | 形式バージョン(将来変更時は`AIF2`。復元toolは未知バージョンをfail-closed) |
| `stem` | データJSONのファイル名(拡張子なし)`<slug>__<level>[__prod]`。例`ai_island_temple__a2__prod` |
| `d6` | そのデータJSONファイル全体の`sha256`先頭6桁(選定時の版。公開Pages=リポジトリの同一ファイル) |
| `c8` | `candidates_sha256`先頭8桁(候補集合。`null`なら`00000000`=er128が拒否) |
| `t8` | `source.text_sha256`先頭8桁(本文) |
| `s10` | `sha256("v1\n" + 選択項目を"<区分1-3>:<candidate_id>"で形式順に改行連結)`先頭10桁(区分と項目の集合・順序) |
| `g10` | 文法0件=`0`。ありは`sha256("v1\n" + "<candidate_id>:<explanation_sha256>"改行連結)`先頭10桁 |
| `m8` | コメントなし=`0`。ありは`sha256(trim(コメント))`先頭8桁 |
| `k4` | 直前までの文字列の`sha256`先頭4桁(人手の誤編集・欠落の検出) |

- JS側の実装では`Web Crypto`の`crypto.subtle.digest('SHA-256')`(非同期)を使うか、同期が必要なら小さな純JS SHA-256を同梱(外部ライブラリなし)。委任_07で選択。ファイル全体のshaは、フォームがデータをfetchした生バイト列(`arrayBuffer`)から計算する。
- 行は1行のまま折り返さない。ChatGPTがコードブロックで返せば逐語維持される。

## 4. ユーザーが見ない/触らない情報の保持(原文§4の両立)
| 情報 | 保持先 |
|---|---|
| `candidate_id`、`kind`、`ja_gloss_status` | 公開データJSON(`phrases[]/words[]`)。復元時にterm→候補へ一意解決(termは記事内で一意=`validateArticle`のdup検査) |
| 本文sha・候補集合sha全文 | 公開データJSON最上位+照合コード(`t8`/`c8`)。復元payloadへ全文を再付与し、er128が現行候補docと全文照合 |
| 文法の`id`/`explanation_sha256` | 公開データJSON(`grammar[]`)。同名文法は**文法名+解説全文**で一意解決(AI島Stdは同名3件。prototypeで確認) |
| 選定順序 | データ順に正規化し`s10`で照合 |

## 5. 設計判断の記録
- 文法ブロックに`candidate_id`/shaを出さない理由: 解説全文が文法候補の識別子として十分(同名でも本文は異なる)で、`g10`が補強する。画面・コピーに内部IDを出さない原文§4に従う。
- 「AI選定理由」節はコピーから外す(原文例示に含まれない。`reason_ja`は確認用情報で、確定内容ではない=DATA_MODEL_02 B。公開データJSONに残る)。
- 区分見出しの件数表記(例`(3/3)`)は例示に無いため付けない。上限は引き続きフォームが担保。

## 6. 改訂(委任_08、2026-10-27。JS `form_logic.js` と Python `er128_form_readable_restore_01.py` に同時適用・バイト一致)
- **コメント既定語**: 自由コメントは、trim後が空、またはtrim後を`NFKC`+小文字化した値が次の既定語のいずれか**のみ**なら「コメントなし」として扱う(コピー本文は`自由コメント：なし`、`m8`=`0`、`payload.comment`=`""`)。
  `COMMENT_NONE_WORDS = なし / 特になし / 無し / 特に無し / ありません / 特にありません / - / ー / ― / — / n/a / none`(JS `COMMENT_NONE_WORDS`・Python `COMMENT_NONE_WORDS`は同一定数、正規化関数=JS `normalizeComment`/Python `normalize_comment`)。
  既定語を含むだけの実コメント(`なし。`、`- 例文を短く`等)は実コメントとして保持。復元側は同じ関数で正規化するため「コメント欄が『なし』」の復元拒否は廃止(実コメントのコードに対する『なし』への書換えは`m8`不一致で従来どおり拒否=fail-closed維持)。
- **解説全文の終端記号**: 表示・照合用の正規化は末尾の`\s*=+\s*$`(Pythonは`\s*=+\s*\Z`)を除去する(直前に改行が無い`。=====`も含む)。本文中の`=====`は触らない。対象=JS `bodyView`、Python `body_view`・`norm_body`。
- 既存fixtureのうち`ai_island_temple__b1b__prod__r1`(Top1が`。=====`終わり)の期待コピーは新規則に更新。追加fixture=`comment08_{nashi,tokuninashi,empty_ws,real}`・`b1b_top1_trailing_term08`。
- 照合コード構造(`AIF1-…-k4`)・UI上限・fail-closedは不変。
