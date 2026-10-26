# DATA_MODEL_02 データJSON schema拡張と送信データschema v2(委任_02、2026-10-27)
並行委任(KP-CONFIRMED-CONTENT-PROTECTION-01)が参照する正本。DATA_MODEL_01からの差分のみ。

## A. 候補データ `eigo_radio_selection_article_v1`(後方互換の追加項目。`export_form_data_01.py`/`build_data_01.py`が出力)
各 `phrases[]`/`words[]` entry に追加:
- `ja_gloss`: string。`japanese_gloss`の逐語(= 既存`meaning_ja`と同値)。
- `ja_gloss_status`: `official|provisional|missing`。official=Production正式経路+gloss整合Gate通過(ALIGNED/HUMAN_RESOLVED)+gloss HR待ちなし。provisional=gloss HR待ち/DEV Trial/replay由来。missing=空。
- `ja_gloss_source`: 出所の説明文字列。
- `reason_ja`: AIが実際に出した選定理由のみ(placeholder・call1は空文字)。
- `reason_source`: `ai_call2|ai_backfill|ai_call1|none_call1_has_no_reason|none_placeholder_not_real|none_not_generated`。
- (Trial-02データは `origin` も追加)。状態無しの旧データをフォームが読んだ場合は「provisional」扱い(正式扱いしない)。

## B. 送信データ `eigo_radio_selection_result_v2`(`schema_version: 2`。`form_logic.js buildStructured`)
```
{ schema, schema_version:2, generated_at,
  article{slug,level,level_label,name,text_sha256}, candidate_source, limits{...},
  user_confirmed_note_ja,                      // selection/comment=ユーザー確定内容。後続で変更しない
  selection{
    key_phrase[], extra_explanation[], meaning_display[]   // item={term, category(1|2|3), category_label, ja_gloss, ja_gloss_status[, selection_phrase]}
    grammar[]                                              // {id, title, explanation_full, explanation_status: provided|missing, example}
  },
  grammar_status: candidates_available | no_candidates_ungenerated,
  comment,
  ai_reference{ for_reference_only:true, note_ja, items[{term, reason_ja, reason_source}] },   // 確認用。確定内容と分離(selectionのitemにreason_jaを入れない)
  counts{...}, production_connected:false,
  candidates_all[]  // コピー時のみ: 未選択を含む全候補 {term, category(0=未選択), ja_gloss, ja_gloss_status, reason_ja, reason_source, reason_for_reference_only:true}
}
```
- v1からの変更: `selection.key_phrase/extra_explanation/meaning_display` は文字列配列→item配列、`selection.grammar`は`{id,title}`→`{id,title,explanation_full,...}`。schema名`..._v1`→`..._v2`。
- 人間可読テキスト: 先頭5ブロック(記事/①/②/③/文法/自由コメント)は参照HTMLと同一書式のまま維持し、続けて【ユーザー確定内容の詳細】(区分|英語|日本語訳【正式訳/仮訳・未確定/日本語訳未生成】)、【文法解説(選択分の解説全文)】、【AI選定理由(確認用情報。確定内容ではない)】の3節を追加。仮訳/未生成が含まれる場合は「黙って確定・変更しないこと」の注記を付す。
- 送信経路: ①ChatGPT URL(`?q=`、<=6000字)はテキスト+JSON(収まる場合のみ)→テキストのみ→URL不可(null)の順。URL不可なら全項目入りの選定結果(テキスト+JSON全候補)をコピーして誘導(黙って切り詰めない)。②コピー=テキスト+JSON(`candidates_all`付き)。

## C. 並行委任(確定内容保護)が使う前提
- 確定内容の最小単位: item `{term, category, ja_gloss}` と grammar `{id, title, explanation_full}`、`comment`。`ja_gloss_status!=official`の訳は未確定=後工程で修正案提示→再確認の対象。
- 後工程への保存(Production側の確定内容store)は本委任の範囲外(フォームは静的HTML+localStorageで、Production未接続)。
