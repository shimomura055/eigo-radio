# 委任_06: 分類A是正(W4 P1)=人間承認で原文へ戻した音声に対するLR正解原稿の解決不整合(実装+test、API 0)

管理ID: LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01(Fable→sonnet-worker、2026-10-27)。共通所在=`…_委任_00_COMMON.md`。本委任は実装委任(指定範囲のProductionコード・testの編集可)。SSOTは編集しない。
根拠: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W4_ROLE_COVERAGE_01.md` §6・修正案P1。Fable判定: 承認済み仕様(`CURRENT_SPEC.md:2925`「resume/再利用が書換え後の文を使えるのはLR記録を持つentryのみ」+人間承認で原文音声を採用した場合は原文が正)どおりへの是正=11-8不具合・ユーザー承認不要・API 0。前委任_05(commit 7dab92aba、er127/er003_v1_n3/er003_v1_crosslevel/er019 test)との整合を確認のうえ進める。

## 事象
Y E-1 `y_voice_1`: HR個別採用(`er121_e1_hr_adopt_r0_01.py`)で音声を原文版へ戻し、entryにフラグ`local_rewrite_audio_superseded_by_human_approval`(`:146`付近)を立てたが、`local_rewrite_recovery`記録は残る。`er020_tts_retry_local_rewrite_01.resolve_expected_text_after_local_rewrite`(`:850-880`)はこのフラグを参照せず、LR後の文を正解原稿として返す(a2/b1bで純関数実行により確認済み)。再利用・`rejudge_with_current_judge`・resume・減速後再検証で、原文音声をLR文で判定する誤判定リスク。

## 是正(範囲=この1件)
1. `resolve_expected_text_after_local_rewrite`(および同じLR記録を2次出典として読む`guard_entry`/Z形`audio_text_deviation.audio_text_after`読み取り箇所)で、entryに`local_rewrite_audio_superseded_by_human_approval`(真)がある場合は**元原稿(`canonical_text`/`canonical_text_before_local_rewrite`)を正解として返す**。`expected_text_source`も原文側の出典名にする。フラグ名・意味は`er121_e1_hr_adopt_r0_01.py`の既存定義を単一ソースとして参照(定数化して両所から読む。重複文字列を書かない)。
2. 同じ「人間承認で原文へ戻す」経路がX(`record_human_approval`経由で原文音声を採用する運用)・Zにも存在するか確認し、存在するなら同じフラグ(または既存の同等記録)を判定に含める。存在しない場合はその旨を記録(新しい経路は作らない)。
3. test: `er020_tts_retry_local_rewrite_01_test_01.py`(または適切なtest)に、(a)LR記録あり+フラグなし→LR文、(b)LR記録あり+フラグ真→原文、(c)Z形2次出典+フラグ真→原文、の3ケースを追加。既存のY E-1保存entry(a2/b1b)を読み取り専用fixtureとして再現確認(保存データは書き換えない)。`er121_e1_hr_adopt_r0_01_test_01.py`・`er078_asr_unified_backcompat_07_test_01.py`・`er020_*`・`er127_*`・`er121_family_y_*`のtestを実行し件数・失敗0を記録(既知失敗OPEN-543系は差分なしを示す)。
4. 影響範囲表(X/Y/Z 6経路のどこに効くか)、Dangling reference・旧記述Grep、未観測(実runでの再判定は次回自然発生時)を`FIX_A_02.md`に記録。

## 成果物・Git
- `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/FIX_A_02.md`。
- 変更ファイルのみ`git add`(`git add -A`禁止)、commit「LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 委任_06: 人間承認で原文採用した音声のLR正解原稿解決を是正(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、**`origin/main`へpush**(現在のブランチ`work/post-merge-01`はmainと同一。push先は`git push origin HEAD:main`で明示)。test失敗・競合時はcommitせず報告。
- 最終応答: FIX_A_02.mdのパス+要約10行(修正内容/file:line/test件数/影響表/未観測/commit hash/push先)。
