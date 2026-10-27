# CURRENT_CONSUMERS_01 現行消費者の事実(read-only、API 0、2026-10-27)

## 1. ユーザー定義の区分(参照フォーム原文)
`docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`
- :6 「各候補は①②③のいずれか1つだけ。①単独で3件、①＋②で5件、①＋②＋③で12件まで。」
- :27(送信payload文面) 「① Key Phrase (n/3)」「② 追加解説 (①＋②=n/5)」「③ 本文意味表示 (累計=n/12)」
- AI島指示 `docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER.md:95-97`(上限)、`:133`「①②③の区分に応じた音声・解説・本文ハイライトを適用」。
- 注意: フォーム上の③の名称は「本文意味表示」(=ユーザー定義)。委任文の「本文ハイライト・短い日本語意味」は§7と初回フォーム指示の語の合成。区分②③の意味の細目(②=何の追加解説か、③の見せ方)は、参照フォームに説明文が無い(ラベルのみ)=**ユーザー定義は件数上限とラベルまで**。

## 2. 消費者の現状(X/Y/Z × Std/Adv)
| 区分 | Adv | Std | 根拠 |
|---|---|---|---|
| ① KP(音声+KP行) | 消費あり: KP音声(kp_en/kp_ja/解説)+台本表のKP行(英語/日本語の意味) | 同左 | Y `er121_family_y_audio_01.py:1484-1489`、Z `er063_family_z_audio_01.py:2473,2543-2546`、X KP行 `er019…:2922-2925`(KP-CONFIRMED CURRENT_FLOW_01 §8) |
| ② 追加解説 | **消費あり**: Part 1「Vocabulary & Expressions」は`vocab_confirmed.json`(最大5件、KP⊂vocab)が入力。1件ごとに 英語表現/本文中の意味(確定gloss)/本文引用英文/英文の日本語訳(T1)/解説 を表示 | **消費者なし**(`vocab`はAdvのみ。Stdで指定するとエラー) | X入力 `er019…:461-469`(`_part1_items`)、`er119_kp_human_review_01.py:63-64,524-530`(`a2 and vocab`→NG、Adv必須・KP⊂vocab)、`er003_kp_general_explanation_01.py:364-400`(assemble_part1)、`er120_part2_wiring_01.py:497-507` |
| ③ 本文ハイライト+短い日本語意味 | **消費者なし** | **消費者なし** | `unconsumed[]` reason=CATEGORY3_NO_CONSUMER/STD_CATEGORY2_NO_SLOT(KP-CONFIRMED DESIGN_02:38,96) |

- Adv「5件」: 現行の自動(HR AUTO)は`er119…:564-580`で「KP=先頭3、vocab=先頭5(KPを含む)」。フォーム確定後は確定レコードのvocab集合(①→②順)がミラーされる設計(DESIGN_02)。**①→②順がvocab_confirmedに反映される点は確定保護実装側の担保で、本委任では未確認**。Part 1のrows数は`MAX_PHRASES=5`(`er003…:68`)。
- Part 1の仕様(CURRENT_SPEC.md:2086)は「**Advancedのみ。Standard・A/B/C・Yへは拡張しない**」。Std向けは承認済み仕様の拡張に当たる。X Playerは`if "b1b" in levels:`でPart 1+2を連結し「Standard=a2には載せない」(GRAMMAR CURRENT_FLOW_01:33)。Y/ZもAdvのlevelにだけstudy_htmlを渡す(`er063…:2589-2593`、GRAMMAR CURRENT_FLOW_01:41)。
- Std学習ページ構成: 台本表(パート/音声/Script+KP行)→(Part 2文法 study_html、全6経路化はGRAMMAR-PREGEN進行中)。共通`render_standard_page`(`er_user_listening_page_common_01.py:138-163`)はlevel別`study_html`(任意)を節の後ろへ置く。

## 3. 本文表示のハイライト機構
- 共通builder: `script_block`(`er_user_listening_page_common_01.py:123-129`)は`esc(text)`のみ(⏸マーカーはdev限定)。`<mark>`/下線の経路は**無い**。
- X/Y/Z Production builderのKP下線/ハイライト: 該当0件(KP-CONFIRMED CURRENT_FLOW_01:58、LEARNING-ITEM-SELECTION-FORM-V3 SURVEY_01:16-17でZ advanced.htmlも0件)。
- 旧資産: `user_test/unified.html:227`の`applyKeyPhraseHighlight(mapping)`は`kp_mapping.json`(`phase_d_kp_mapping_regen.py`生成、`matched_text`でp.script内を検索)依存の旧ビューア用。X/Y/Z Productionからの参照0件(CURRENT_FLOW_01:59)=流用不可(Python builder側の静的HTMLで実装する方が整合)。
- 短い日本語意味の表示箇所: KP行(台本表)の「日本語の意味」と、AdvのPart 1「本文中の意味」のみ。いずれも①(+Adv②)だけ。

## 4. 確定レコードの利用可能項目
`vocab_confirmed.json`/確定item(例 `part2_hr_evidence_01__run_r2/b1b/key_phrases/vocab_confirmed.json`)のitemは`source_span`(本文表層形、例 "made its way through")・`source_sentence`/`source_sentence_id`(S27)・`used_form`(原形 "make its way through")・`japanese_gloss`・`occurrence_count`/`occurrence_sentence_ids`を持つ。=ハイライトは`source_span`を使えば活用形の問題なし(原形`used_form`は本文に無い場合がある)。
