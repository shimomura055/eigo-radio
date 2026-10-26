# SPEC_CHECK_01: Family Y Advanced Comment 2削除の仕様照合(委任_01 Lane A、2026-10-26)

出典(ユーザー承認原文): `docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_USER.md` §1-③。

## 1. 現行構成(実装名)と新構成の差分(Advanced=b1b)

再生順の実装: `er121_family_y_audio_01.py` `_body_seq`(旧: 同:751-765)、`build_y_timeline`。

| 順 | 現行(HEAD) | 実装名(segment/timeline part) | 新構成 | 備考 |
|---|---|---|---|---|
| 1 | Comment 1 | `comment_1` / "Comment 1" | 維持(=ユーザー用語の『導入』の一部) | 削除対象外 |
| 2 | Lead(導入段落) | `y_lead` / ys.PAGE_LABEL[Y_LEAD] | 維持(=『導入』) | |
| 3 | **Comment 2** | `comment_2` / "Comment 2" | **削除** | 唯一の削除対象 |
| 4-6 | Voice 1リード文→Voice 1 | `y_intro_1`→`y_voice_1` | 維持 | |
| 7-9 | Voice 2リード文→Voice 2 | `y_intro_2`→`y_voice_2` | 維持 | |
| 10-12 | Voice 3リード文→Voice 3 | `y_intro_3`→`y_voice_3` | 維持 | |
| 13 | Comment 3 | `comment_3` | 維持(ユーザー原文は削除を指示していない。原文の「Tension＋Closing」は段落5=`y_closing`) | 判断候補ではなく『Comment 2のみ削除』の字義通り |
| 14 | Closing(Tension+Closing) | `y_closing` | 維持 | |

Standard(a2、日本語側)・日本語原稿・Preview以外のsupport: 無変更(`comment_2`含む4種を維持)。

## 2. 照合した既存仕様

- 構成の設計記述: `docs/research/FAMILY-Y-VOICES-DESIGN-01/REDESIGN_01/DESIGN_PROPOSAL_03.md:8`(Comment 1→Comment 2→[見出し→Voice]x3→Tension+Closing)。Comment 2は設計案段階の構成要素で、ユーザー承認(本件)で除外。
- 実装: `er121_family_y_structure_01.py` `Y_COMMENT_2_ROLE`(b1b/a2)、`comment_contexts`、`er121_family_y_runner_01.py` `stage_support`(HEAD 439-475)、`er121_family_y_audio_01.py` 7か所(YProvider.collect / write_level_inputs / generate_y_b1_segments / generate_y_a2_segments / load_y_sources(b1b,a2) / `_body_seq`)。
- CURRENT_SPECにはY構成の独立した正本行が無かったため、本委任で新節を追加(出典=USER.md §1-③)。

## 3. Comment 2の他段入力有無(影響範囲調査)

Comment 2のテキストを入力として使う段を全grepで確認(`er121_*.py`、`er121_prompts/`):
- Tension/Closing/Lead/Part 1/Part 2/KP選定/ページ: **使わない**(text core `er121_family_y_text_core_01.py` に `comment` の参照0件。Comment 2生成は記事確定後の `stage_support` のみ)。
- **Previewのみ**: `gen.PREVIEW_ROLE.format(comment_1=c1, comment_2=c2)`(`stage_support`)。共有のX用PREVIEW_ROLE(`er003_v1_b1_scaffold_01_generate.py:193-221`)は『後で流れるComment 1・Comment 2と内容が重複しない』ための**重複回避の参照**として両commentを受ける。これは入力文脈ではなく排除対象の参照。
  - 対処(最小・Y側のみ): Y専用の派生関数 `ys.advanced_preview_role(base)` が共有roleから**Comment 2への言及3か所だけ**を機械的に除く(他の文は不変、置換対象が変わればValueErrorで停止)。共有module(X)は編集しない。Standard(a2)のPreviewは共有roleをそのまま使う(無変更)。
  - 影響: 既存run(E-1)の `support/b1b_support.json` のPreview本文は旧role由来だが、本文自体にComment 2は含まれないため再利用可能(Fable判断に委ねる。DESIGN_01 §5)。
- 判定: 条件A(新構造)非該当のまま。Previewは『入力』ではなく重複回避参照のため停止対象外と判断(`etc.`の解釈。Fableが再判定可)。

## 4. 結論

削除対象=`comment_2`(b1bのみ)で確定。Comment 1・Lead・Comment 3・Closing・Standardは残す。不明点なし(STOPなし)。
