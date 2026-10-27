# CONTRACT_03 A/B/C/D/E/F班の境界契約(DESIGN_03の実装契約。班はこの契約に対して先行着手し、変更は契約改訂commitで行う)

## 1. 型(委任_04C更新: 委任_04Aの実装[`er_learning_highlight_01.py`]に合わせて改訂。実装が正)
```
DisplayUnit = {key: str, texts: list[str], joiner: str}   # 表示順の台本単位。Xはparts.jsonのPart(full_story_part1-3)+in_one_line、Yはsegment、Zはクリップ群をPart単位(texts=クリップ台本)
Highlight(resolve_highlights結果の1項目) = {candidate_id, kind: 1|2|3, used_form, gloss, surface(=pieces本文の連結), decorate: bool,
                                           pieces:[{unit_key, text_index, start, end, text}], sentence_id, relocated_from, stream_span}
   # start/endは「当該unit内のtexts[text_index]」の文字オフセット(joinerを含む連結テキストのoffsetではない)。pieces[i].text == texts[text_index][start:end]。
   # 跨ぎ(unitの複数texts/Zのクリップ分割)は piece ごとの surface(=pieces[i].text)。全pieceを連結したものが Highlight.surface。各pieceに同一 data-hl を付ける
render入力(highlights_for_text) = [{kind, start, end, candidate_id, surface}]   # surface=その片の本文。script_blockはtext[start:end]==surfaceをassert
Meaning = {candidate_id, used_form, japanese_gloss, unit_key(None=表示範囲外の③。節末に置く)}
Notice/Issue = {code, candidate_id, detail}
```

## 2. 関数(委任_04C更新)
```
er128.display_spec_of(run, level) -> str|None                 # 表示有効化(flag非経由)。X配線はこれ+load_record+items_from_record(record)で足りる
er128.load_verified_items(kp_dir, *, level, which="highlight")  # B班の予定(委任_04C時点では未着地)。C班は依存しない
er_learning_highlight_01.resolve_highlights(article_text, cands_doc, items, display_units, *, units=None, lr_rebound=False)
      -> {"status":"OK"|"ISSUE","highlights":[Highlight],"meanings":[Meaning],"notices":[...],"issues":[...],"stats":{...}}
      # 純関数。ISSUEは例外送出ではなく result["issues"]/status="ISSUE"(呼出側がページ生成前にSTOP=fail-closed)。items=items_from_record(確定レコード)
er_learning_highlight_01.items_from_record(record) / highlights_for_text(result, unit_key, text_index=0) / meanings_for_unit(result, unit_key)
er_learning_highlight_01.render_script_html / meaning_list_html / legend_html / HIGHLIGHT_CSS / contract_view(result)
er_user_listening_page_common_01.script_block(text, chunk_texts=None, audience="public", warnings=None, highlights=None)   # highlights=None/[]は現行とバイト同一
er128_kp_highlight_01.verify_highlights(level_section_html, expected)   # expected={"result":resolve結果,"script_texts":[...],"audience":"public"|"dev"} -> {"status":"PASS"|"FAIL"|"SKIPPED_DISABLED","problems":[...]}
er003.build_prompt / phrases_signature / generate_* / resolve_* / require_fresh_* / assemble_part1 / write_study_text / study_html_for_audio_dir  (全て level="b1b" 既定引数)
er128 reconsume --run --level --by --user-ref
X配線(C班): er019_family_x_audio_production_runner_01: x_display_spec / part1_enabled / part1_levels / x_display_units / resolve_x_highlights / x_script_cell_html /
            validate_part1_block_count / verify_x_level_page / generate_part1_all(level=) / assemble_part1_x(level=) / part1_study_html_for_player(level=)
            er019_family_x_audio_production_runner_01.PLAYER_CSS_WITH_HIGHLIGHT(=audio_review_player.PLAYER_STANDARD_CSS+HIGHLIGHT_CSS。共有moduleは無編集=Family A等の既存playerもバイト同一)
            er019_family_x_listening_page_01.build_page / er019_x_page_guard_01(旧per-article scriptのSTOP)
```
**表示範囲(Fable決定、委任_04C)**: DisplayUnit列=ページに表示される本文単位すべて。Xは Full Story Part 1-3 + In One Line(`parts.json` の `in_one_line`)。Full Story外の「In one line」節にのみ出現する語句(例 `year over year`)はISSUEにしない(分類B)。

## 3. Family別アダプタの責務(M1)
アダプタは「**候補生成に使った本文**」(Xは`{source_dir}/{lv}/article.md`、Zは`canonical_article_text(...)`変換後、Yは該当本文)とそのDisplayUnit列を渡す。`sha256_text(text) == cands["text_sha256"]`(`er119:1353,1406`)を必須とし、不一致は`HL_TEXT_SHA_MISMATCH`。`<run>/<lv>/article.md`の決め打ちは禁止。

## 4. 原因コード(委任_04C更新: A班の実装名が正。CONTRACT名はalias表`CONTRACT_CODE_ALIASES`/`contract_view()`で相互変換)
ISSUE(ページ生成前STOP): `HL_TEXT_SHA_MISMATCH` / `HL_SENTENCE_ID_UNKNOWN` / `HL_SENTENCE_MISMATCH`(`_norm_ws`正規化後の不一致のみ) / `HL_SPAN_NOT_IN_SENTENCE` /
`HL_CANDIDATE_UNKNOWN` / `HL_NOT_IN_DISPLAY`(=契約名`HL_SENTENCE_NOT_IN_DISPLAY`。範囲内出現0件の①②、LR書換え後に項目語句も消失) /
`HL_PARTIAL_OVERLAP`(=契約名`HL_OVERLAP_PARTIAL`。①②が関わる部分交差のみ) / `HL_SURFACE_MISMATCH`(描画時assert)
NOTICE(停止しない): `HL_OCCURRENCE_RELOCATED` / `HL_CONTAINED`(=契約名`HL_CONTAINED_SKIPPED`) / `HL_PARTIAL_OVERLAP_3`(=契約名`HL_OVERLAP_RANKED`、③同士の部分交差) /
`HL_NOT_IN_DISPLAY_MEANING_ONLY`(=契約名`HL_MEANING_ONLY`) / `HL_LR_REBOUND`
X配線のSTOPメッセージは A班名(契約名)の併記: `X_HIGHLIGHT_UNRESOLVED(<level>): <契約名>(A班名=<A班名>):<candidate_id>`。

## 5. HTML契約(委任_04C更新)
- 装飾要素は`class="lk1|lk2|lk3"`と`data-hl="<candidate_id>"`(①②=`<strong>`、③=`<span>`)。Zのクリップ分割は各片に同一`data-hl`。文字を増やす属性・疑似要素・`title`(③含む)禁止。
- ③訳リストは **`<ul class="lk-meaning">`**(旧記述の`hl-meaning`は廃止。G3は両方受理)。`div.script`/`table`/`h2`の外。各`<li>`=`<used_form> ＝ <japanese_gloss>`。`英語:`/`日本語:`/`EN:`/`JA:`の語を使わない。
- 凡例は`<p class="lk-legend">`(`legend_html()`)。`data-hl`を持たない=G3の集計対象外。
- CSSは`HIGHLIGHT_CSS`(単一定数)。common本体のCSSへは連結しない(既存ページのバイト不変)。ハイライトを出すページ/playerだけが連結する
  (標準builder=`</head>`直前に`<style>`、X player=runner内の`PLAYER_CSS_WITH_HIGHLIGHT`)。
- G3は`data-hl`のcandidate_id単位で数え、level節単位(`level_section_html` / X playerは`player_level_section`)で検査。X playerはESCAPE切替(M13): ハイライトのあるlevelだけ`render_script_html`(escape)、無いlevelは従来の未escape出力のまま。

## 6. G1不変条件
a2では`display_spec`と`std_part1`が一致する。`display_spec`付きなら`STD_CATEGORY2_NO_SLOT`が0件。vocab対象levelではPart 1がちょうど1個。③の`used_form`/`japanese_gloss`は`_cand_diffs`の照合対象。

## 7. `display_spec`継承規則
付与は`new_review`の1箇所。`_new_record`は前レコードの`display_spec`を継承。前レコードが無い新規時のみreviewの`std_part1`から導出。`std_part1`は存在時のみ`selection_signature`に含める。マーク発行は最後の1commit(M14)。

## 8. 遅延import
`er128_kp_confirmed_content_01.py`と`er128_kp_highlight_01.py`は互いに関数内importとする(モジュール先頭でのimport禁止)。

## 9. 所有ファイル表
| 班 | 所有 |
|---|---|
| A | `er_learning_highlight_01.py`、`er_user_listening_page_common_01.py`、`er128_kp_highlight_01.py`、各新規test |
| B | `er003_kp_general_explanation_01.py`、`er003_kp_source_sentence_ja_01.py`、`er119_kp_human_review_01.py`(マーク発行以外)、`er128_kp_confirmed_content_01.py`(S9-S12、`reconsume`、継承、`which="highlight"`分岐、`verify_outputs`委譲1行)、`er120_part2_wiring_01.py` |
| C | `er019_family_x_audio_production_runner_01.py`、`er019_family_x_listening_page_01.py`(新)、`er019_x_page_guard_01.py`(新。`display_spec`検出STOP。旧per-article script 14本へは1行importのみ)、`er019_nws2_final_page_01.py`、player CSS連結(`PLAYER_CSS_WITH_HIGHLIGHT`、runner内。`audio_review_player`は無編集)、X用test |
| D | `er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`、Y用test |
| E | `er026_family_z_fiction_production_runner_01.py`、`er063_family_z_audio_01.py`、Z用test |
| F | evidence、`ER-*_REPORT.md`、ブラウザ検証。**マーク発行の最後の1commit(`new_review`/`display_spec`導出)**はF直前にB班が実施 |
共通ファイルは所有班以外が編集しない(必要なら所有班へ依頼)。着手直前に`git status`/`git diff --stat`で他Agent未commit差分を確認し、pathspec付きcommit。
