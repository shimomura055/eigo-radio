# DATA_MODEL_03 記事データ/送信payload(委任_02差分。DATA_MODEL_02への追加)
## 記事データ(eigo_radio_selection_article_v1への追加項目、任意)
- `kp_confirmed`: {status:"USER_CONFIRMED", locked:true, confirmed_at, user_ref, payload_path, payload_sha256, text_sha256, candidates_sha256, selection:[{term,category,category_label,ja_gloss,ja_gloss_status:"official",candidate_id,kind,selection_phrase?}×10(3/2/5)]}。`validateArticle`が候補データと逐語照合(candidate_id存在/term/ja_gloss/件数3-2-5/sha一致)し、不一致はデータ形式エラー(fail-closed)。
- `grammar_spec`: {version:"top2_select1_v1", presented_max:2, max_select:1, allow_zero:true, presented_ids[], hidden_ids[], source_*_sha256}。`validateArticle`: grammar<=2件・rank=1,2・presented_ids一致・max_select=1。
- `grammar[]`: 提示分のみ(Top1/Top2)。各item: id/candidate_id/title/body/explanation_full/example/explanation_sha256/rank。
## 状態(localStorage `eigo-kp-form-v3`)
`grammar`(id→bool、最大1)・`grammar_zero`(true=「適切な候補なし」明示)。決定状態: selected|none|undecided|n/a。旧状態は正規化(2件選択→未決定)。`kp_confirmed`記事では`choices`を無視。
## payload(eigo_radio_selection_result_v2, schema_minor 1のまま追加項目)
`limits.grammar=1,grammar_presented_max=2`、`selection.grammar[]`(0/1件、rank/rank_label付き)、`grammar_status`、`grammar_decision`、`kp_confirmed`(locked)。er128 `from-form`が読む既存項目(selection.{key_phrase,extra_explanation,meaning_display}.{term,candidate_id,kind,ja_gloss,ja_gloss_status}、selection.grammar[].{id,title,explanation_full,...}、article.{candidates_sha256,text_sha256})は不変。

## 委任_07追補: 送信形式v3(人間可読+照合コード)(2026-10-27。DATA_MODEL_02/本書上部の送信payload記述を拡張。データJSON自体は無変更)

正本の形式定義=`COPY_FORMAT_01.md`、復元側仕様=`RESTORE_TOOL_SPEC_01.md`。本書はフォーム実装(`user_test/selection_form_v3/form_logic.js`)の確定事項のみ記す。

## 1. 送信・コピー文(人間可読、`FormLogic.buildReadable(d, st, {stem, file_sha256})`)
- 構成: `記事：<名>｜<レベル>` / `① Key Phrase`・`② 追加解説`・`③ 本文意味表示`の各`- 英語：日本語訳`(0件は`（選択なし）`) / `文法：選定なし` または `文法：<名>`+`【解説全文】…【解説ここまで】` / `自由コメント：<本文|なし>` / `照合コード(変更しないでください)：AIF1-…`。
- 日本語訳の状態: `official`以外は`（仮訳・未確定）`/`（日本語訳未生成）`を訳の後ろに付与(未生成は訳欄`(未生成)`)。
- 確定済み記事(`kp_confirmed`)は保存状態でなく確定内容(`choicesOf`)から同一形式で出力。UI上限(3/5/12・文法1件/0件)は不変。
- 解説全文は`grammar[].body`をそのまま。末尾の内部終端記号は**直前が改行の`=====`(改行+=====)のみ除外**(データ側に直前改行なしの`。=====`終端が1件ある=`ai_island_temple__b1b__prod` Top1。この場合は終端記号を残して逐語出力する。復元側`norm_body`も同じ規則のため往復は一致。データ側終端の統一は別途)。
- 「ChatGPTへ送信」は先頭に`FormLogic.PREFACE`(コードブロックで逐語返却を依頼、`▼選定結果`で本文を区切る)を付ける。「選定結果をコピー」・「技術情報付きでコピー」は前置きなし。

## 2. 照合コード(フォーム側の算出、`FormLogic.makeCode`)
`AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>`。`stem`=データファイル名(拡張子なし)、`d6`=フォームが`fetch`した**生バイト列(`arrayBuffer`)**のSHA-256先頭6桁、以降は`COPY_FORMAT_01.md` §3どおり。SHA-256は同期の純JS実装(`FormLogic.sha256Hex`、外部ライブラリなし)で、node標準crypto・Python hashlib・ブラウザWebCryptoとバイト一致をtestで確認。
- フォームは`d.__stem`・`d.__file_sha256`(読込時に付与する実行時プロパティ。データJSONには書かない)から`buildReadable`へ渡す。
- Windows作業ツリーのCRLFとリポジトリblob(LF)で`d6`が変わり得る。公開Pagesはblob(LF)を配信するため、**公開URLで生成した照合コードの`d6`はblob基準**(復元tool側`d6_of_bytes`はCRLFをLFへ正規化して比較)。

## 3. 廃止・残置
- 廃止: 送信URLへのJSON同梱(旧`buildChatGptUrl`のwith_json)、旧PREFACE(「Claude Code向け指示案を作成」)、送信文中の`candidate_id`/種類/SHA行・AI選定理由(`buildText`の内容)。
- 残置(既定非表示の補助): `buildText`/`buildStructured`/`buildCopyText`は技術情報付きコピー(`<details>`内)で使用。`er128 confirm --from-form`へ直接渡せる逃げ道。
- 返値: `buildChatGptUrl(d, st, now, opts)` → `{text, url|null, url_length, mode:'url'|'paste'}`。
