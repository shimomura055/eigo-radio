# B9 Z chunk本文overlay(⏸欠落)修正(委任_14、API 0)

## 原因
B7で直したX(er019_family_x_listening_page_01.py:127)と同型。Zは`er063_family_z_audio_01.py`の2箇所(build_page_rows内row["chunk_texts"]、_user_page_rowsのFull Story script_block)で、chunk planの原文(TTS入力前)をそのまま⏸位置決めへ渡していた。LRで英文が変わったchunkは表示本文(overlay後)に見つからず、直後の⏸が欠落する。

## 修正
両箇所を`er132_lr_overlay_pages_01.chunk_texts_overlaid(ledger, plan)`へ(_user_page_rowsにはlevel_ledgerを追加)。LR 0=従来とバイト同一(`chunk_texts_of_plan`と同一)。plan・parts・run dirは不変。

## test
- er132_lr_overlay_pages_01_test_01.py: 新規2件(Z source: overlaid呼出2か所・生plan直渡しの撤去 / ⏸数=plan境界数(LRあり)・LRなし同一)。
- `test_public_page_scan_flags_exactly_the_known_publication_mismatches`: 未公開の声候補dir(`*_fenrir_01`・`*_reselect_01`)を走査対象外に(`_UNPUBLISHED_CANDIDATE_SUFFIXES`)。既知2件の網羅assertは不変。
- 結果: er132 53 PASS。er133/er063系(audio/speed_v2/std_chunk/common_style/narrator_voice_override)141 PASS、1 FAIL=`er063_family_z_audio_01_test_01.py::WiringTest::test_preview_comment_kp_styles`(K2 style assert)。本変更前(stash)でも同じく失敗=既存不具合(本件と無関係、未着手)。

## 影響run一覧(chunk planあり×level全20件を実ledgerで検証、script=一時scratchpad)
chunk_texts_overlaidとchunk_texts_of_planの差分が出たrun=0件。LRありでchunk plan有: melos run_fzcw_e2_b1b_01/e4_b1b_01(各1)、tell_tale_heart run_reselect_01 b1b(1)・run_voice_fenrir_01 a2(7)/b1b(8)・run_voice_schedar_01 b1b(8)も、LR対象clipがchunk idと一致せず差分なし=現時点で⏸欠落の実害run 0、候補ページ(reselect_01/fenrir_01)のpages段再実行は不要。
