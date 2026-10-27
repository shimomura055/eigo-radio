# RESTORE_TOOL_SPEC_01 Claude側 復元・照合tool 仕様(委任_06、read-only設計。実装は別委任)

目的: ユーザーが貼り付けた**人間可読テキスト(+照合コード)**から、`er128 confirm --from-form`が受け付けるpayload v2(`schema_version:2, schema_minor:1`)を**欠落・改変なく**復元する。ユーザーにJSON編集を求めない。照合できなければfail-closed(確定しない)。試作で挙動を実証済み: `proto06_copy_restore_01.py`(`proto06_output_01.txt`: 往復66/66一致、改変9種検出、data更新2経路)。

## 1. 置き場・CLI
- 新規ファイル(推奨): リポジトリrootの`er128_form_readable_restore_01.py`(関数`restore(text, data_dir, git_lookup)`→`(payload, notes)`、`RestoreError`)。既存`er128_kp_confirmed_content_01.py`の関数は**変更しない**。
- CLI(薄い追加。GPG委任のer128編集権の下で): `py er128_kp_confirmed_content_01.py confirm --from-readable <貼付テキストfile> --run <run> --level a2|b1b --by <名> --user-ref <参照>`(既存`confirm --from-form`と同じ引数群)。処理: 貼付テキストを`<kp_dir>/source/rev{N}_readable.txt`へ**そのまま保存**(監査用、sha記録)→`restore()`→payloadを一時JSONへ→**既存`cmd_from_form(run, level, payload_path, by, user_ref)`を呼ぶ**(er128の検査・保存は無変更)。`origin`へ`readable_sha256`を追記する場合は`cmd_from_form`の`origin`拡張が要るため、GPGのer128編集権の範囲で最小追加(任意)。
- 単体利用: `py er128_form_readable_restore_01.py --text <file> [--data-dir user_test/selection_form_v3/data] [--out payload.json]`(payload出力のみ。確定はしない)。

## 2. 入力と前処理
- 入力: ユーザーが貼ったテキスト(ChatGPTの返信全体でも可)。改行はLFへ正規化。コードブロック囲み(```)・前置き文があっても、**末尾の照合コード行を探して**その前の本文を解析する。
- 照合コード行: 正規表現`AIF1-(stem)-(d6)-(c8)-(t8)-(s10)-(g10|0)-(m8|0)-(k4)`(最後の一致を採用)。`k4`不一致=破損として拒否。`AIF1`以外=未知版として拒否。

## 3. 復元手順(各段で不一致=`RestoreError`、何も書かない)
1. **データ特定**: `user_test/selection_form_v3/data/<stem>.json`を読む。`sha256(ファイル)[:6]==d6`でなければ、`git_lookup(stem, d6)`で履歴(`git log --format=%H -- <path>`→`git show <h>:<path>`のshaが一致する版)から選定時の版を取得。無ければ「選び直し」を案内して拒否。公開Pages版との同一性確認(任意`--verify-public`): `GET .../data/<stem>.json`のshaが`d6`と一致(無料・read-only)。
2. **束縛**: `candidates_sha256[:8]==c8`かつ`source.text_sha256[:8]==t8`(`null`は`00000000`扱い→最終的にer128が拒否)。
3. **字句解析**: 行頭`記事`/`①②③`/`文法`/`自由コメント`で節に分割。項目行`^\s*(-|・|•|\*|\d+[.)])\s*英語[：:]日本語訳`(最初の`：`/`:`で分割)。文法ブロックは`【解説全文】`〜`【解説ここまで】`の間を解説全文として取得(終端記号欠落=途中切れとして拒否)。自由コメント=`自由コメント：`以降〜照合コード行の前(複数行可、`なし`は空)。
4. **候補への解決**(termは記事内で一意=`form_logic.js validateArticle`のdup検査。**term→`candidate_id`はデータJSON由来**で、貼付テキスト側のidは使わない):
   - term逐語一致 → なければ`NFKC+空白正規化+casefold`で**一意に**一致する場合のみ採用(`notes`に記録)。0件/複数件=拒否。
   - 同一termが複数候補にある(旧データ等)場合は`s10`を満たす組合せを列挙(上限64通り)して一意に決まるときのみ採用、決まらなければ拒否。
   - 日本語訳: 貼付の訳(末尾の`（仮訳・未確定）`等を除く)とデータ`ja_gloss`が`NFKC+空白正規化`で一致すること。不一致=拒否(**黙って置換しない**。ChatGPTによる意訳の検出)。
   - 区分の重複(同じ項目が複数区分)=拒否。
5. **選択集合の照合**: データ順へ並べ替えて`s10`を再計算し一致を要求(項目の欠落・追加・区分の入替えを検出)。
6. **文法**: 文法名が一致する候補のうち、**解説全文が(`\r\n`→`\n`、行末空白除去、末尾`=====`除去後に)一致するものが唯一**であること(同名候補が複数あるデータに対応: 実データ`ai_island_temple__a2__prod`は同名3件)。0件=省略/改変の疑いで拒否、2件以上=同名同文で一意不可として拒否。`g10`再計算が一致すること。**解説全文はデータ側の`body`をpayloadに入れる**(貼付側の文字列は照合にのみ使用)。
7. **コメント**: `m8`が`sha256(trim(コメント))[:8]`と一致(0=空)。

## 4. 出力payload(`cmd_from_form`が読むフィールドのみ必須。既存`buildStructured`と一致)
`schema:"eigo_radio_selection_result_v2", schema_version:2, schema_minor:1, article{slug,level,level_label,name,text_sha256,candidates_sha256(全文),candidates_sha256_source,source_kp_candidates_path}, selection{key_phrase[],extra_explanation[],meaning_display[],grammar[]}, comment`。
- 各itemは`{term,category,category_label,ja_gloss,ja_gloss_status,candidate_id,kind[,selection_phrase]}`(データJSON由来)。`grammar[]`は`{id,title,explanation_full,explanation_status:"provided",example[,candidate_id,explanation_sha256,level]}`(データ由来)。
- 省略するフィールド(コピーから除外したもの): `ai_reference`、`candidates_all`、`limits`、`user_confirmed_note_ja`、`counts`、`generated_at`(復元時刻を入れる場合は`restored_at`として別名)、`production_connected`。**根拠**: `er128 cmd_from_form`(origin/main `er128_kp_confirmed_content_01.py:1297-1382`)が参照するのは`schema_version`・`article.{level,candidates_sha256,text_sha256}`・`selection.{key_phrase,extra_explanation,meaning_display,grammar}`・`comment`のみ。
- 試作での一致検証: 復元payloadの`article/selection/comment`が、同じ選択に対する**既存`FormLogic.buildStructured`(node)の出力と全11データ×6乱択=66件で完全一致**。

## 5. 曖昧・揺れの扱い
| ケース | 扱い |
|---|---|
| 同名の英語表現が複数候補 | 現データでは発生しない(dup検査)。発生時は`s10`で組合せ解決、不能なら拒否 |
| 日本語訳の揺れ(句点・空白・全角半角) | NFKC+空白正規化で吸収。語句が変わったら拒否 |
| 全角/半角コロン、箇条書き記号(-/・/•/数字) | 吸収(試作で確認) |
| termの大文字小文字(`Make a difference`) | casefoldで一意なら採用し`notes`に記録。payloadはデータの表記へ正規化 |
| 文法名重複 | 文法名+解説全文で一意化(§3-6) |
| CRLF、行末空白、ChatGPTのコードブロック/前置き | 吸収 |
| 解説の省略・要約・追記 | 拒否(「再コピー」を案内) |
| 照合コード欠落/破損 | 拒否 |
| 選定後にdata JSON更新 | `d6`から履歴版を取得。不能なら拒否 |
| 候補集合shaが`null`のデータ(replay/DEV Trial) | 復元は可能だがer128 `cmd_from_form`が「候補集合shaなし」ISSUEで拒否(現行仕様維持) |
| `ja_gloss_status!=official`の項目 | 復元自体は成功。er128が従来どおりISSUE(要確認) |

## 6. 失敗時の出力(ユーザー向け)
JSON編集を求めない。「フォームの『選定結果をコピー』をもう一度押し、全文を貼り付けてください」+不一致箇所(項目名・区分・文法名)を1〜3行で。ISSUE記録は`cmd_from_form`側の既存方式(rc=4)。

## 7. 安全
- read-only(データJSONとgit履歴の読取のみ)。API 0。外部HTTPは任意`--verify-public`のGETのみ。
- 既存retry/fallback/Gateを触らない。確定後のレコード変更は従来どおり`confirm-revise`/`revoke`経由のみ。
- 貼付原文は`source/rev{N}_readable.txt`に保存し、既存の`rev{N}_payload.json`と対にして監査できる。
- DefaultOff性: 新CLIオプション追加のみで、フォーム/Productionの既定動作を変えない。復元toolは明示実行時のみ動く。
