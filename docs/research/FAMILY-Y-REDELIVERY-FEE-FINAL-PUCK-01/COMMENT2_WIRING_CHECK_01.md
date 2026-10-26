# COMMENT2_WIRING_CHECK_01 — Advanced Comment 2削除の配線照合(FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01、read-only・API 0)

照合元: `CURRENT_SPEC.md:3080-3090`(「Family Y Advanced Comment 2削除」節)、コードはHEAD(`git show HEAD:…`)と作業木の両方(作業木差分は並行Agentの`Y_DIALOGUE_VOICE_POOL`/`FIXED_VOICE_SLOTS`のVoice表変更のみで、Comment 2経路に差分なし=`git diff -U1`で確認)、`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/{DESIGN_01,EVIDENCE_01}.md`、`run_01`の実成果物。

## 1. 結論

**Advanced Comment 2削除は、本記事(既存run_01=Comment 2ありで生成済み)をresume/再組立した場合に、音声・スクリプト・ページ・manifest・再生順序から除外される。実成果物で既に確認できる(下記)。新規の配線実装は不要(重複実装しない)。**

- 本記事で必要な作業は「resume/再組立」であり、限定事項「初回生成stage(導入文3 call)は次のY新規記事で確認」は**本記事に該当しない**(Voice 1再生成は`stage_support`を再実行しない。support文書は再利用。Comment 2はb1bで元々再生成されない設計)。
- **Preview再生成は不要**(自己判定。根拠は §4)。Fableが異論なければPuck再生成に加えない。

## 2. 経路別の確認(○=コード+実成果物で確認 / ◎=runtime成果物で実測)

| 経路 | 実装箇所(HEAD行) | 確認 |
|---|---|---|
| 定義(単一箇所) | `er121_family_y_structure_01.py:247-251` `Y_SUPPORT_NAMES`(b1b=preview/comment_1/comment_3、a2=4種)、`Y_REMOVED_SUPPORT_NAMES={"b1b":("comment_2",),"a2":()}`、`:254` `support_names`、`:260` `body_comment_names` | ○ |
| 初回生成(support) | `er121_family_y_runner_01.py:460`(`if "comment_2" in ys.support_names(lv)`)でb1bはComment 2生成なし、`:468` `advanced_preview_role`、`:477` `_meta.removed_by_spec`記録 | ○(コードのみ。実API確認は未=限定事項) |
| 入力書出し | `er121_family_y_audio_01.py:176` `names=ys.support_names(level)`、`:184-185` `parts["removed_by_spec"]`。旧support dictに`comment_2`が残っても書き出さない・検査しない | ◎ `run_01/b1b/parts.json`にcomment_2=0件 |
| TTS | `er121_family_y_audio_01.py:459` `for name in ys.support_names("b1b")`(ループにcomment_2が入らない)。再生成するとresultsは新規構築されb1bの`comment_2` entryは消える | ○ |
| 組立 | `:780` `body_comment_names("b1b")`、`:822-823` `_body_seq`(`"comment_2" in body_comment_names(level)`の時のみ挿入)。旧`narration/comment_2.wav`・旧results entryは**無視**(削除せず=`DESIGN_01.md:44`) | ◎ `b1b/audit/timeline.json` 43要素(Comment 2 8.61秒+直後pause 0.8秒のみ削除、`EVIDENCE_01.md:21`)。現timelineの再生順=…comment_1(4.33)→0.8→Lead(21.52)→0.8→intro_1(5.88)→0.8→Voice1(44.36)→0.8→intro_2(6.81)→Voice2(45.84)→intro_3(8.72)→Voice3(49.84)→comment_3(10.11)→Closing(37.56)→Outro |
| ページ | 同`_body_seq`/`build_y_timeline`(`:832`)から行を生成 | ◎ 公開済み`user_test/family_y_production_redelivery_fee_01/index.html`: `Comment 2`行はStandard節(`<h2 id='standard'>`以降、std_16.mp3)のみ。Advanced節(`<h2 id='advanced'>`以降)は0行。`run_01/pages/index.html`の`comment_2`grep=0件(ラベル`Comment 2`はStd節の1行のみ) |
| manifest | `er121_family_y_runner_01.py:1192-1193` `support_segments`、`removed_by_spec` | ◎ `run_01/final_manifest.json:294-297` `removed_by_spec.b1b.comment_2` |
| gate/page_verify | 現行Gate(§4 INVENTORY_01) | ◎ 現コードでA2/B1 audio validation gate PASS・y_style_gate PASS(scratch実測) |
| resume | `DESIGN_01.md:27` / test `test_legacy_comment2_artifacts_are_ignored_on_reassemble`、`er121_family_y_comment2_removal_test_01.py:81,89`(`test_advanced_ignores_legacy_comment2`/`test_advanced_does_not_require_comment2`) | ◎ run_01再組立で実測(`EVIDENCE_01.md:11-22`、Std byte同一) |

## 3. 「旧runのcomment_2成果物は無視」の実装位置

- 入力: `er121_family_y_audio_01.py:176-185`(`write_level_inputs`が`support_names(level)`だけを書く)。
- 検査/生成: `:459`(TTSループ)、`:146`(`for name in ys.support_names("b1b")`、検査系)。
- 組立: `:780`(`body_comment_names("b1b")`でsegsを読み、旧`comment_2.wav`を読まない)、`:822-823`。
- 既存の残存(無視されるだけで害なし。完全除外の証跡に使えるよう「残存箇所一覧」を記録): `b1b/support_texts.json`(1件)、`support/b1b_support.json`(2件)、`b1b/audit/tts_generation_results.json`(7件)、`…pre_ypl7_adopt_backup.json`、`b1b/audit/review_lock_state*.json`、`b1b/narration/comment_2.wav`・`attempts/comment_2_attempt1_*.json`、`b1b/run_summary_tts.json`(1件)、`final_manifest.json`(`removed_by_spec`の2件=意図的記録)。`b1b/parts.json`・`b1b/audit/timeline.json`・`pages/index.html`は0件。
- Voice 1再生成時のtts_b1b再実行で`write_level_inputs`が再走(`runner.stage_tts` `runner()`内)し`b1b/support_texts.json`はcomment_2なしに更新、`tts_generation_results.json`のb1b `comment_2` entryも消える見込み(コード読みの推論。委任_02で実測)。

## 4. Preview(Advanced)再生成の要否 — 不要

- `advanced_preview_role`(`er121_family_y_structure_01.py:265-286`)はPreview生成時の**プロンプト**から「Comment 2との重複回避参照」を除くだけで、既存のb1b Previewの**本文**はComment 2への言及を持たない: 「A missed package can affect more than the person waiting for it. In this episode, we look at the delivery process and what needs to be considered when trying to reduce missed deliveries.」(`b1b/audit/tts_generation_results.json` `preview.text`、sha e84f0cb8…)。a2 Previewは日本語でStd(Comment 2あり構成)に属し変更なし。
- 先行判断: `EVIDENCE_01.md:22`「Preview(重複回避参照の旧role生成)は再生成せず再利用(Fable判断)」、`DESIGN_01.md:45`。本委任でも新たな矛盾(Comment 2への言及・順序依存)は見つからない。
- Voice 1がPuckになってもPreviewの内容(Voice非依存)に影響しない。残る確認は最終試聴(Comment 1→Lead→Voice 1の接続)のみ。

## 5. 接続・流れ(Comment 2削除後)

- Comment 1(4.33秒、「Listen for what the 3 people think about charging for another delivery.」)→Lead→Voice 1リード文の順。Lead直後のpauseは既存`pause_story_to_comment`(0.8秒)を1つ残し新値なし(`CURRENT_SPEC.md`該当節、`_body_seq`)。Comment 2が担っていた役割(Lead Recovery+Bridge to the Three Voices)はLead(21.52秒)+各Voiceリード文で既に重複しているため削除された(ユーザー決定の理由)。音声ブリッジ上の文面上の参照切れ(「先ほどの…」等)をb1bのcomment_3/y_intro_1/Lead本文で目視確認: b1b comment_3「Why does the same issue look so different…」、y_intro_1「First to speak is a delivery driver who…」にComment 2を指す語は無い(`inventory_01.json`のtext_head)。最終の聴感確認は委任_02(ASRではなくユーザー試聴)。

## 6. 配線完了後に再確認する項目(委任_02)

1. 組立後`b1b/audit/timeline.json`の要素数(43のまま)・`b1b/parts.json`/`pages/index.html`のAdv節にcomment_2が無いこと。
2. `final_manifest.json`の`removed_by_spec.b1b.comment_2`が残ること、`support_segments.b1b`が[preview, comment_1, comment_3]であること。
3. Voice 1再生成後、Std側のcomment_2(std_16.mp3)が維持されていること(ユーザー指示「Standardに未承認の構成変更を加えない」)。

## 7. 起票候補

- なし(新規OPEN不要)。限定事項「初回生成stage未確認」は本記事に非該当であり、OPEN-527/次Y新規記事の既存追跡のまま。
