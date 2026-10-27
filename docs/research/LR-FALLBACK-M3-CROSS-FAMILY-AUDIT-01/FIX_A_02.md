# FIX_A_02: 人間承認で原文へ戻した音声のLR正解原稿解決(委任_06、2026-10-27、API 0)

根拠: W4_ROLE_COVERAGE_01.md §6・P1。承認済み仕様(CURRENT_SPEC.md:2925)どおりへの是正(11-8不具合)。Gate判定・HR Lock・音声・Prompt・閾値は不変。

## 変更
| 修正 | file:line | 内容 |
|---|---|---|
| フラグ名を定数化(単一ソース) | `er020_tts_retry_local_rewrite_01.py:852` `HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG` | 書込側・読取側が共有 |
| 解決関数の先頭分岐 | 同`:867-869` | entryにフラグ真なら、LR記録(1次`local_rewrite_recovery`/Z形2次`audio_text_deviation`)が残っていても`(canonical_text, "canonical_text")`を返す |
| 書込側を定数参照へ | `er121_e1_hr_adopt_r0_01.py:147`(import `:21`) | 文字列重複を撤去 |

`guard_entry`(er078)はLR記録を直接読まず、再利用/rejudge/減速後再検証/X継承(er019_validation_inheritance:277)/N3 L4(er003_v1_n3_01_tts_generate:231)はいずれも本関数経由のため、単一箇所で全て効く。

## X/Zにも同経路があるか
- フラグを立てる経路はY E-1 `er121_e1_hr_adopt_r0_01`のみ。X/Zの`record_human_approval`(er003_v1_n3_01_assemble:96)は承認sha記録のみで音声差替え・LR記録との併存を作らない。個別承認系one-off(er010_no9/er011_towels/er019_fx_moon/FAMILY-Y-STYLE-PROFILE-FIX-01 hr_adopt)はLR記録を扱わない(grepで`local_rewrite`/`superseded`参照0)。よって新経路は作らず、将来X/Zで同様に原文へ戻す運用が出ても、同フラグを立てれば自動で効く(Z形2次出典も対象)。

## test(追加5件、`er020_tts_retry_local_rewrite_01_test_01.py` `HumanApprovalSupersedesLrExpectedTextTest`)
(a)LR+フラグなし→LR文 (b)LR+フラグ真→原文 (c)Z形2次+フラグ真→原文 (d)書込側と定数の同一性 (e)Y E-1保存entry(redelivery_fee run_01 a2/b1b `y_voice_1`)を読み取り専用で読み原文が返ることを確認(保存データ書換えなし)。
実行: er020_tts_retry_local_rewrite_01_test_01 34 passed。
指定群(er121_e1_hr_adopt/er078_asr_unified_backcompat_07/er020_*/er127_*/er121_family_y_*): 655 passed / 1 failed / 1 skipped。失敗1件=`er020_tts_retry_local_rewrite_fullseg_test_01::test_recorded_candidates`(`er011_output/local_rewrite_recovery/...`保存データのgit上D=既存失敗、FIX_A_01記載と同一、本変更無関係)。OPEN-543系の差分増加なし。
注: 変更前baseline比較のため`git stash`で一時退避した実行は未コミット差分も外れて11 failedとなり比較に使えないため不採用(stashは即popで復元、作業ツリー復元確認済み)。

## 影響範囲(X/Y/Z 6経路)
| 経路 | 効き方 |
|---|---|
| X Std/Adv | フラグを持つentryが現存しないため出力不変。将来フラグ付きで効く |
| Y Std/Adv | 該当entry(E-1 y_voice_1 a2/b1b)の再判定・resume・減速後検証が原文基準になる(今回の是正対象) |
| Z Std/Adv | Z形entryでもフラグ真なら原文。現状フラグ付きentryなし=不変 |
| A/B/C(scope外) | フラグなし=不変 |

## Dangling/旧記述Grep
`local_rewrite_audio_superseded_by_human_approval`の文字列リテラルは定数定義(er020:852)のみ(コード側)。残りはtest assert(er121_e1_hr_adopt_r0_01_test_01:98、既存・値は同じ)と保存データ。

## 未観測
実runでの再判定(原文音声が原文で判定されること)は次回自然発生時に採取。純関数と保存entry fixtureまで確認。保存データ・音声は未変更。
