# CONTRACT_03 A/B/C/D/E/F班の境界契約(DESIGN_03の実装契約。班はこの契約に対して先行着手し、変更は契約改訂commitで行う)

## 1. 型
```
DisplayUnit = {key: str, texts: list[str], joiner: str}   # 表示順の台本単位。Xはparts.jsonのPart、Yはsegment、Zはクリップ群をPart単位に連結(texts=クリップ台本、joiner=クリップ間の連結文字列)
Highlight   = {candidate_id, kind: 1|2|3, surface, unit_key, start, end, gloss_short, used_form}
   # start/endは当該unit(joiner込み連結テキスト)内の文字オフセット。描画時に text[start:end] == surface をassert
Notice      = {code, candidate_id, detail}
```

## 2. 関数
```
er128.load_verified_items(kp_dir, *, level, which="highlight") -> list[dict]        # display_spec無し→[]。表示有効化はflag非経由(F-4)
er_learning_highlight_01.resolve_highlights(specs, source_text, text_sha256, display_units) -> {"highlights":{unit_key:[Highlight]},"meanings":{unit_key:[{used_form,gloss}]},"notices":[Notice]}
      # 特定不能は HighlightIssue(code) を送出。純関数。er128とは遅延importで相互参照
er_user_listening_page_common_01.script_block(text, chunk_texts=None, audience="public", warnings=None, highlights=None)
er_user_listening_page_common_01.render_script_html / script_blocks_for_part / meaning_list_html / HIGHLIGHT_CSS
er128_kp_highlight_01.verify_highlight_outputs(kp_dir, level, page_texts, display_units)
er003.build_prompt / phrases_signature / generate_* / resolve_* / require_fresh_* / assemble_part1 / write_study_text / study_html_for_audio_dir  (全て level="b1b" 既定引数を追加)
er128 reconsume --run --level --by --user-ref
```

## 3. Family別アダプタの責務(M1)
アダプタは「**候補生成に使った本文**」(Xは`{source_dir}/{lv}/article.md`、Zは`canonical_article_text(...)`変換後、Yは該当本文)とそのDisplayUnit列を渡す。`sha256_text(text) == cands["text_sha256"]`(`er119:1353,1406`)を必須とし、不一致は`HL_TEXT_SHA_MISMATCH`。`<run>/<lv>/article.md`の決め打ちは禁止。

## 4. 原因コード(`HL_*`)
`HL_TEXT_SHA_MISMATCH` / `HL_SENTENCE_ID_UNKNOWN` / `HL_SENTENCE_MISMATCH`(`_norm_ws`正規化後の不一致のみ) / `HL_SPAN_NOT_IN_SENTENCE` / `HL_SENTENCE_NOT_IN_DISPLAY`(範囲内出現0件の①②、LR書換え後に項目語句も消失) / `HL_OVERLAP_PARTIAL`(①②が関わる部分交差のみ) / `HL_SURFACE_MISMATCH`(描画時assert) 
NOTICE(停止しない): `HL_OCCURRENCE_RELOCATED`(範囲外出現→範囲内最初の出現へ。`occurrence_sentence_ids`は番号順) / `HL_CONTAINED_SKIPPED`(包含で低優先を非装飾) / `HL_OVERLAP_RANKED`(③同士の部分交差) / `HL_MEANING_ONLY`(範囲内0件の③は訳リストのみ)

## 5. HTML契約
- 装飾要素は`class="lk1|lk2|lk3"`と`data-hl="<candidate_id>"`。Zのクリップ分割は各片に同一`data-hl`。文字を増やす属性・疑似要素・`title`(③含む)禁止。
- ③訳リスト`<ul class="hl-meaning">`は`div.script`/`table`/`h2`の外。英語表示は`used_form`。`英語:`/`日本語:`/`EN:`/`JA:`の語を使わない。
- G3は`data-hl`のcandidate_id単位で数え、level節単位(`level_section_html`)で検査。

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
| C | `er019_family_x_audio_production_runner_01.py`、`er019_family_x_listening_page_01.py`(新)、`er019_pp_page_01`(`display_spec`検出STOP)、`audio_review_player`(`PLAYER_STANDARD_CSS`)、X用test |
| D | `er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`、Y用test |
| E | `er026_family_z_fiction_production_runner_01.py`、`er063_family_z_audio_01.py`、Z用test |
| F | evidence、`ER-*_REPORT.md`、ブラウザ検証。**マーク発行の最後の1commit(`new_review`/`display_spec`導出)**はF直前にB班が実施 |
共通ファイルは所有班以外が編集しない(必要なら所有班へ依頼)。着手直前に`git status`/`git diff --stat`で他Agent未commit差分を確認し、pathspec付きcommit。
