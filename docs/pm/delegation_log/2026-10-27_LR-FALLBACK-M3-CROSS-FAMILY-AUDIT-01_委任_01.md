# 委任_01(W1): AI島 真因確定+LRデータフロー+本文反映の仕様上の扱い(ユーザー原文 §2・§3)

共通事項: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_委任_00_COMMON.md`(必読・遵守)。
成果物: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W1_LR_DATAFLOW_01.md`。読取専用・API 0。

## 1. AI島事象の確定(§2)
ユーザー原文§2の表を、保存evidence(tts_generation_results.json・attempts_log・telemetry・hr_packet_data_01.json)で1項目ずつ照合し、「一致/不一致/補正」を表にする。特に: (a)AI島runは統一仕様(①②同Style→180秒→③短文Style→LR→①'②'③')で動いたのか、旧フロー(標準2+minimal 1)なのか(policy名・attempt列・待機の実測値・`tts_block_progress`で判定)。(b)LR後のTTS試行回数とStyle(元role Styleか)。(c)Stdの減速後再検証の実際。(d)最終停止がM3 `LOCAL_REWRITE_RECOVERY`(+Std `STD_FALLBACK_USED_OR_UNKNOWN`)であることの確認。既存結論(HR_ROOT_CAUSE_01)を鵜呑みにせず再照合する。

## 2. なぜLR後に本文が更新されないのか(§3、最優先)
1. LRが「TTS送信用の英文だけ」を変える設計か: コード(er020/er127/各経路)とdocs(DESIGN_01/02、2026-09-26・10-19原文)から確定。
2. その設計のユーザー承認履歴: 承認原文の`file:line`で、「本文は変えない」が(i)明示承認/(ii)暗黙(言及なし)/(iii)実装欠落のどれかを判定。先例OPEN-499(Word Gacha「you've felt」→「you have felt」)での扱いも確認(本文が更新されたか、公開ページの表示はどちらか)。
3. LR後の英文の保存先(全キー・全ファイル)と後続への伝搬経路: `local_rewrite_recovery.selection.selected.rewritten_segment`/`text`/`canonical_text_before_local_rewrite`/`BlockProgress.lr`/Z形`audio_text_deviation.audio_text_after`/Master Audio Store entry/manifest等。消費者(resume・再利用・減速後再検証・HR queue・assemble・公開ページbuilder)を列挙。
4. 参照先一覧表(X/Y/Z×Std/Adv): 記事本文(article.md/parts.json)・公開スクリプト表示・表示ハイライト(①②③表示仕様、SLOT-23)・KP出現箇所照合(G3)・文法解説・TTS入力・ASR正解原稿(`resolve_expected_text_after_local_rewrite`)・HR Lock key/承認記録(`record_human_approval`のsha対象)が、それぞれ「元原稿」か「LR後」かを明記。
5. 本文をLR後に更新した場合の影響: `confirmed_selection.json`の`article.text_sha256`、KP確定保護G0〜G4(`er128`)、`scaffold_article_sha256.json`、文法(Part 2/pregen)、Fact check/Ledger deviation、QA(repetition等)、日本語訳・JA Support、選定ロック(フォームv3照合コード`t8`=本文sha)、公開ページ照合、resume時の原稿sha stale検知(`BlockProgress` key)。影響を「壊れる/再実行が必要/影響なし」で表にする。

## 3. 分類と提案
所見をA/B/Cに分類。本文と音声の一致を満たす方式候補(例: (i)LR後本文を記事本文へ反映[確定内容保護との関係]、(ii)LRを採用せずHRで原稿側を人間が修正、(iii)音声側のみで表示に注記、(iv)Writer/発音供給側でLR誘発を減らす[OPEN-563])を、品質・速度・量産単価・必要承認・既存仕様との衝突で比較し推奨を書く。**実装しない**。

## 4. 報告
重要度順: 真因/本文反映の仕様上の扱い(承認済みか否か)/影響表/分類/判断候補/Fableへの要約10行。
