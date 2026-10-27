# 委任_04(W4): 本文以外のLR適用範囲と同種不具合の横断調査(ユーザー原文 §6)

共通事項: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_委任_00_COMMON.md`(必読・遵守)。
成果物: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W4_ROLE_COVERAGE_01.md`。読取専用・API 0。

## 1. 全音声Role一覧(X/Y/Z×Std/Adv)
`ROW_MAPPING_01.md`(49行)と`er127_tts_block_policy_01.PROFILES`、各runner(er019 X/er121 Y/er063・er117 Z)から、全音声Role(本文・Comment・Preview・Topic intro・In One Line・KP英語・KP解説・KP日本語意味・JA Support・Zセリフ・Z narrator・Shell・固定mp3等)を列挙し、LR適用あり/なし/TTSなしを表にする。なし/TTSなしのRoleは理由と正式仕様の`file:line`を記録。

## 2. LR適用Roleごとの確認(本文以外を重点)
各Roleについて:
- 音声に読ませる原稿と、ユーザー向け表示テキスト(公開ページ・スクリプト・字幕・KP表示)の対応(同一ソースか別ソースか、LR後にどちらが変わるか)
- LR後の書換え結果の伝搬先(record/Store/manifest/ページbuilder)
- ASR判定の正解原稿(`resolve_expected_text_after_local_rewrite`が経路で使われているか)
- 確定済み学習項目(KP/KW/文法/訳、`er128`保護)との整合(KP英語phraseがLR対象外である根拠)
- 後続の公開ページ・字幕・スクリプト・音声の一致
- Human Reviewへの移行条件
- 再利用(Master Audio Store/`reuse`)・resume時に旧原稿が復活しないか(key=原稿sha、LR後entryの継承)

## 3. 既存の本文/音声不一致の実在調査(API 0)
`er0*_output`/`er1*_output`配下の`tts_generation_results.json`およびZ形entry/Store manifestを`local_rewrite_recovery`(selection採用あり)で横断Grepし、**LRが採用された全entry**を一覧化(Family/run/level/segment/role/Before→After/日付/公開済みか)。公開済み(user_test配下や公開ページ)の記事で、表示本文と音声が食い違っているものを特定する(AI島以外にあるか)。X/Y/Zの正式Production run(Legacy A/B/Cは対象外、ただし検出されたら件数のみ記録)。

## 4. 分類と報告
所見をA/B/Cに分類。同じ原因が他経路で再発する条件(Role×Family)を明記。判断候補の区分、Fableへの要約10行。
