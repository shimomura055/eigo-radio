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

---
# 追補 委任_03a(2026-10-27): v2契約にcandidate_id / kind / candidates_sha256を追加(additive、`schema_version`は2のまま)
理由: canonicalization後は同じ`term`(英語表示)が複数候補に存在し得るため、termでの対応付けは曖昧。確定内容保護(KP-CONFIRMED-CONTENT-PROTECTION-01、Opus条件Aレビュー)は`candidate_id`で候補docと逐語照合する。UI・既存項目の意味は変えない。

## A'. 候補データ(`data/<slug>__<level>.json`)への追加
各 `phrases[]`/`words[]`(と`overflow[]`)entryに:
- `candidate_id`: 候補doc(`kp_candidates.json` candidates[])の`candidate_id`の**逐語**(既存`id`と同値。`id`は互換のため残す)。
- `kind`: `phrase`|`word`。候補docの`kind`を逐語。候補docに`kind`が無い場合のみ「`used_form`の語数==1→`word`、それ以外→`phrase`」で導出。
- `kind_source`: `candidate_doc`|`derived_from_word_count`(導出時のみ後者。捏造しない)。

データJSON最上位(記事×レベル単位)に:
- `candidates_sha256`: 候補docの自己sha(`kp_candidates.json`最上位フィールド`candidates_sha256`。算出は`er119_kp_human_review_01.candidates_sha256(doc)`=docから`candidates_sha256`キーを除いたjsha)。**docに無い場合は`null`**(算出・推測しない)。
- `candidates_sha256_source`: `candidate_doc_field`(docの値を逐語。出力時に再算出と一致を検証)|`unavailable_replay_doc`|`unavailable_dev_trial_doc`(取れない理由)。
- `source_kp_candidates_path`: 入力した候補docのリポジトリ相対path(取れない場合`null`)。
- `candidate_id_uniqueness`: データ内で`candidate_id`は一意(testで検証)。`term`の重複はこれまで通りフォームが拒否(dup)。

## B'. 送信データ(JSON・人間可読テキストの両方)への追加(`schema: eigo_radio_selection_result_v2`、`schema_version: 2`、新設`schema_minor: 1`)
- `article{...}`に`candidates_sha256`(null可)・`candidates_sha256_source`・`source_kp_candidates_path`を追加。
- `selection.key_phrase/extra_explanation/meaning_display`の各item: `{term, category, category_label, ja_gloss, ja_gloss_status, candidate_id, kind[, selection_phrase]}`。**対応付けの正はcandidate_id**(termは表示用)。
- `ai_reference.items[]`: `{candidate_id, term, reason_ja, reason_source}`。
- `candidates_all[]`(コピー時): `{candidate_id, kind, term, category, ...}`。
- `selection.grammar[]`は変更なし(`id`が識別子)。
- 人間可読テキスト: 先頭5ブロックは不変。【ユーザー確定内容の詳細】の見出し直下に`候補集合sha256: <値|なし(取得不可: 理由)>`行を追加し、各行末へ`｜candidate_id: <id>｜種類: phrase|word`を付加。AI理由節の各行は`・term(candidate_id): 理由`。
- 旧データ(`candidate_id`/`kind`無し)をフォームが読んだ場合は、`id`を`candidate_id`に流用し、それも無ければ`null`(捏造しない)。

## C'. 受け側(確定内容保護er128)が前提にできること / 注意
- 照合キー=`candidate_id`(+`candidates_sha256`で候補集合の同一性)。`candidates_sha256==null`(replay/Trial-02由来)の記事は、保護Gateで「候補集合照合不可」として扱うこと(通過扱いにしない)。
- `ja_gloss_status`の意味は変更なし。`official`以外の訳をユーザーが確定した場合、受け側(er128)はISSUE(要確認)として扱う。
- 本追補で確定内容の最小単位は `{candidate_id, kind, term, category, ja_gloss}` と grammar `{id, title, explanation_full}`、`comment`。

---
# 追補 委任_04(2026-10-27): P7/W5'(KP_CANDIDATE_MAX 12・kind別cap 7/5)配線への追従(additive、UI不変、API 0)
## A''. 候補データ最上位への追加
- `cap`: 候補上限(整数)。候補docの`shortfall_detail.cap`を正とし、記録が無いdocのみ既定12(`export_form_data_01.cap_info`)。旧8 doc(`data/legacy/`)は`shortfall_detail.cap=8`のまま。
- `cap_by_kind`: `{phrase:7, word:5}`。候補docの`shortfall_detail.cap_by_kind`を正、無ければ既定。`phrases[]`/`words[]`の上限スライスと`overflow[]`の境界もこの値を使う。
- `cap_source`: `candidate_doc`|`candidate_doc_cap_only`|`default_12_7_5`。
- `shortfall_detail`(docがあれば): `cap`/`cap_by_kind`が欠落している場合のみ補完(docの値は書き換えない)。`shortfall_note_ja`は`候補N件/上限12件(フレーズ最大7・単語最大5)…`。
- `reason_ja`: P7/W5'では全候補(call1含む)に`reason_ja`があり逐語。旧Prompt 2 doc(legacy)のcall1は空(`none_call1_has_no_reason`)。`kind`はP7/W5' docでは必須で、`kind_source=candidate_doc`。
## B''. フォーム表示(UI仕様は不変。表示のみ追加)
- 候補グループ見出し: `フレーズ（N件／上限7件）`/`単語（N件／上限5件）`(`cap_by_kind`がある場合のみ。無い旧データは従来表示)。
- 出所注記(`#srcnote`)に`［候補数: <shortfall_note_ja>］`を追記(shortfall時のみ)。
- 選択上限(①<=3/①+②<=5/①+②+③<=12)・文法独立2・コメントは不変。
## C''. データ差し替え一覧(`data/` ← 候補doc)
| データ | 候補doc(run_kp75_ev_01) | 候補数(phrase+word) | 旧3+5版 |
|---|---|---|---|
| ai_island_temple__a2__prod | er019.../ai_island_temple__run_kp75_ev_01/a2 | 5+5 | legacy/へ退避 |
| ai_island_temple__b1b__prod | 同 b1b | 5+5 | legacy/へ退避 |
| uk_train_speaker_playback__a2__prod(新規) | er019.../uk_train_speaker_playback__run_kp75_ev_01/a2 | 3+5 | なし(新規枠) |
| uk_train_speaker_playback__b1b__prod(新規) | 同 b1b | 7+5(12件満載) | なし(新規枠) |
| redelivery_fee__a2__prod | er121.../redelivery_fee/run_kp75_ev_01/key_phrases/a2 | 5+3(補完1) | legacy/へ退避 |
| redelivery_fee__b1b__prod | 同 b1b | 6+4(補完1) | legacy/へ退避 |
| melos__a2__prod | er026.../melos/run_kp75_ev_01/key_phrases/a2 | 4+4 | legacy/へ退避 |
| melos__b1b__prod(新規) | 同 b1b | 4+5 | なし(新規枠) |
- 記事枠: 9記事枠(参照HTML順)は不変。7+5 evidenceは`_prod`スラッグ枠(9枠に数えない)に置く。`articles.json`は`melos_prod`にb1b、`uk_train_speaker_playback_prod`にa2/b1bを追加(計+3枠)。9枠を超えて退避した7+5版は無い。
- 旧3+5版5件は`data/legacy/`へ移動(articles.jsonから参照しない。testで保持を確認)。猿の手(`monkeys_paw__b1b`/`__prod`)は7+5 evidence docが無いため不変(前者DEV Trial-02、後者replay=いずれも`provisional`)。
- 日本語訳(`ja_gloss`)・AI理由(`reason_ja`)は候補docの値を逐語(AI再生成なし)。8件とも`ja_gloss_status=official`、全候補に`reason_ja`あり。

## 委任_05追補(2026-10-27、ユーザー正式決定【全面修正版】§4への追従。UI仕様変更ではない)

- 理由欄の表示規則: 候補の`reason_ja`が空(未設定・空白のみ)の場合、フォームは理由欄(折りたたみ「AI理由・確認用」)自体を描画しない。「AI理由なし」「(なし)」等の文言は一切表示・送信しない。理由がある候補は従来どおり表示。
- 送信payload: `ai_reference.items[]`は理由がある候補のみ。`candidates_all[]`の`reason_ja`/`reason_source`/`reason_for_reference_only`も理由がある候補のみ付与。テキスト版「AI選定理由」節は理由がある候補の行のみ(節見出しは維持)。
- `reason_source`の`none_*`値はデータ側の内部区分として残る(旧doc互換)が、フォームは表示に使わない。
- `data_warnings[]`(article docの任意項目): `{code, count, candidate_ids[], message_ja}`。エクスポータは候補doc(`prompt_ids`のcall1/call2が`kp_prompt_p7`/`kp_prompt_w5p`、または候補単位`prompt_id`がP7/W5')を7+5世代と判定し、`reason_ja`欠落候補があれば`code=reason_missing_in_p7w5`を記録する(正常扱いしない)。フォームは出所注記(`#srcnote`)に「【データ警告】…」を表示する。旧Prompt 2 doc(`prompt_ids`なし等)は警告なし(理由欄非表示のみ)。
- 実データ確認: 配線済み7+5 evidence 8 docは全候補に理由があり`data_warnings`なし。`data/legacy/`・DEV Trial・ダミーは旧世代/非Production扱いで警告なし。
