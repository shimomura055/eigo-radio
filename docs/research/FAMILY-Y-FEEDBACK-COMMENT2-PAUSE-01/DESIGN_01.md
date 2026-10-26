# DESIGN_01: Family Y Advanced Comment 2削除の実装差分(委任_01 Lane A、2026-10-26)

承認: ユーザー正式承認(原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01_USER.md` §1-③)。範囲照合=`SPEC_CHECK_01.md`。到達上限=IMPLEMENTED_PENDING_EVIDENCE(runtime evidenceは委任_03のE-1再組立)。

## 1. 設計方針

level別のsupport構成を `er121_family_y_structure_01.py` の1か所(`Y_SUPPORT_NAMES`/`support_names(level)`/`body_comment_names(level)`/`Y_REMOVED_SUPPORT_NAMES`/`COMMENT2_REMOVED_SPEC`)に定義し、生成・検査・TTS・組立・ページ・manifestはそこから導出する。comment名の直書きtupleは撤去(testで固定)。flag・新設定なし(承認済み仕様の直接変更)。

## 2. 変更ファイル:行(変更後)

| ファイル | 内容 |
|---|---|
| `er121_family_y_structure_01.py` | `Y_COMMENT_2_ROLE`からb1b撤去(a2のみ。role文は無変更)。`Y_SUPPORT_NAMES`等の定義と `advanced_preview_role()` を追加(`Y_COMMENT_2_ROLE`直後〜`comment_contexts`直前) |
| `er121_family_y_runner_01.py` `stage_support` (L439-480付近) | b1bはComment 2を生成しない(LLM 1 call削減)。Advanced Previewは `advanced_preview_role` で派生したroleを使用。`_meta.removed_by_spec`を記録。`write_final_manifest`に `support_segments`/`removed_by_spec` |
| `er121_family_y_audio_01.py` | `YProvider.collect`(L146付近)・`write_level_inputs`(L174-190)・`generate_y_b1_segments`(L421付近)・`generate_y_a2_segments`(L538付近)・`load_y_sources`(L719/732付近)・`_body_seq`(level引数追加)・`build_y_timeline`の呼出 |
| `er121_family_y_comment2_removal_test_01.py`(新規) | 13 test(構成/role/Preview派生/write_level_inputs/_body_seq/support stage call構成/残存Grep) |
| `er121_family_y_runner_01_test_01.py` | timeline期待の更新(b1bはComment 2なし/a2は維持)+新規2 test(全成果物の不在、旧成果物の無視) |
| `er121_family_y_structure_match_test_01.py` | DEV Trial逐語一致をa2のみに更新(b1b撤去) |

## 3. 経路別の反映(ユーザー要求「初回生成・retry・resume・組立・公開ページ」)

| 経路 | 反映 |
|---|---|
| 初回生成(support) | b1bはComment 1/Comment 3/Previewの3 call(旧4)。Comment 2のrole文もb1bには存在しない |
| 検査 | 生成後のAIアナウンス検査は生成したtextのみ。Style/M3 Gateはb1bのcomment_2を元々対象としない(`er019_family_x_style_profile_01.py:204` ROLE_SUPPORT_JA=a2のみ)。ASR/Audio Validation Gateはresults駆動のため追従 |
| TTS(retry含む) | `generate_y_b1_segments`が`support_names("b1b")`のみ生成。retry/`--only`のsegment名正規表現(`_ONLY_OK_RE`)は共通のため`comment_2`をa2用に許可したまま。b1bで指定してもsupport辞書に無いため生成されない |
| resume | 旧runの`support/b1b_support.json`にcomment_2が残っていても `write_level_inputs`は書き出さず検査もしない(test固定)。`tts_b1b`のsha等は不変(旧Preview/Comment 1/3の本文は再利用可能、TTSも再利用) |
| 組立 | `load_y_sources`がb1bのcomment_2を読まない。`_body_seq(level)`がb1bでComment 2を挿入しない。旧narration/comment_2.wav・旧results entryが残っていても無視(test: `test_legacy_comment2_artifacts_are_ignored_on_reassemble`) |
| 公開ページ | `build_page_rows`はtimeline駆動のため追従(Advancedに『Comment 2』行なし、Standardに1行。test固定) |
| manifest | `final_manifest.json` に `support_segments` と `removed_by_spec` を追加。b1bの`parts.json`/`support_texts.json`/support jsonの`_meta`にも注記 |

## 4. 設計判断(開示)

1. **Lead→Voice 1リード文のpause**: Comment 2削除でLeadの直後にVoice 1リード文が来る。新しいpause値は作らず、Lead直後の既存`pause_story_to_comment`(Advanced=AOEDE_TO_CHARON_PAUSE_SECONDS 1.0秒、Standard側は無変更)をそのまま1つ残し、旧Comment 2後の`pause_comment_to_story`は削除。ナレーター同士(Lead→紹介1)の間隔は旧『Lead→Comment 2』間隔と同値。聴感で長短の指摘があれば別判断(新値は導入しない)。
2. **Previewの重複回避参照**: X共有`PREVIEW_ROLE`はComment 2への言及を持つため、Y側 `advanced_preview_role()` で該当3か所のみ機械的に除去(共有module無編集。Standardは共有roleそのまま)。共有roleの文面が変わると`ValueError`で停止し、黙って旧文面を出さない。Opus条件A(新構造)には該当しない(段の削除のみ)。
3. **Comment 3は維持**: ユーザー原文はComment 2の削除のみを指示。原文の新構成の『Tension＋Closing』は段落5(`y_closing`)に対応し、直前のComment 3(`comment_3`)は削除対象に含めない(SPEC_CHECK_01 §1)。
4. **DEV Trialモジュール(`er110_*`)**: 旧Comment 2定義(b1b含む)はDEV Trial専用で、Production(er121)はimportしない。旧run解析のため無変更で残置(Production経路ではない)。
5. **旧成果物の扱い**: E-1 `run_01`は本委任では変更しない。再組立手順は §5。

## 5. E-1 run_01への反映手順案(委任_03用、本委任では実行しない)

- 再TTS不要・API 0・費用0円見込み: Comment 2削除はAdvancedの組立順序のみの変更で、他のsegmentのTTS音声は不変。
- 手順: `er121_family_y_runner_01.py ... --stages provision_shell,gate,assemble,pages,page_verify` を**1起動**で(provision_shell欠落でgateがrc=2→再起動でRESTART_STORMの既知事象、OPEN-480)。assemble/pages/page_verifyはstageがsha非依存でその都度再実行されるため追加の`--regenerate-stage`は不要。事前に`stop_scope_check_01.py`でrc確認。
- 旧`b1b/support_texts.json`(comment_2入り)・`narration/comment_2.wav`・`tts_generation_results.json`のcomment_2 entryは無視される(削除しない)。気になる場合のみ`tts_b1b`を`--regenerate-stage`で再評価できるが、全segment再利用のはずで必須ではない(要確認、費用0円確認後)。
- 注意: Previewの本文は旧role(Comment 2を排除参照)で生成済み。本文にComment 2は含まれず再利用可。Preview再生成が必要か(重複回避の観点)はFable判断。
- 試聴ページは `pages` stageで再生成。新構成の再生順に切替わる(Lane Bの分割点表示は委任_03)。

## 6. 量産単価

Advanced Comment 2の削除分: LLM 1 call(E-1実測: support 8 call計0.421円→1 callあたり約0.05円)、TTS 1 segment(`gemini-3.8-flash-lite-tts` 入力29/出力219 token+ASR1 call。cost_jpyは記録なし、概算 <0.1円)。合計 約0.1〜0.2円/記事セット削減見込み(70円目標の約0.2%)。
