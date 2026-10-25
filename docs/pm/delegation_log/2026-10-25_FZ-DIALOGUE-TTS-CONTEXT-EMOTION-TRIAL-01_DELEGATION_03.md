FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_03(Phase 1b: Fable感情レビュー反映→TTS生成(ctx_t1→base_t1→ctx_t2)→analyze→試聴ページ公開→評価資料→SSOT)。DEV専用、Production変更禁止、Trial上限30円(既消費0.0975円)。

## Fableの感情レビュー結果(2026-10-25、`er118_output/fz_dialogue_context_tts_trial_01/llm/emotion_review.json` の `fable_decision` に設定。`EMOTION_CANDIDATES_01.md`に判断と理由を追記)
- 8件すべて **accept**。理由: ACCEPTED 3件(part2_c7「a little worried」=whispered/kept returning to the mirrorに根拠、part3_c2「eager to explain and reassure」=rushed toward him/It'll grow again!に根拠、part3_c6「pleased」=Look! Isn't it perfect?に根拠)はいずれも原文から妥当に導ける穏当な表現で創作なし。NO_EXPLICIT_CUE 5件(part2_c2/c4/c5、part3_c4/c8)は仕様どおり状態行を出さず、scene・reaction・manner_words(例: smiling through tears、smiled gently、shut her eyes)と地の文引用で演出を伝える形を**そのまま採用**(結果を見た後の検査ルール変更・LLM再呼出はしない=事前登録遵守)。summary_ja(日本語要約)はFable確認済みとして`reviewer_note`を更新(内容は原文の範囲内であること、感情を盛らないことを確認し、必要なら表現を穏当化)。
- 記録: `emotion_review.json`の各件に `fable_decision: accept`、`fable_note`(上記理由の要約)、`reviewed_at`。

## 実施
1. 上記レビュー結果をファイルに反映(decision未設定が0であることを確認)。
2. 日次確認: `py docs/pm/tools/daily_dev_cost_01.py`(JST 2026-10-25)。累計+約20円が1,000円以内なら実行(Fable確認済み: 961.2円時点で可)。超える見込みならSTOPして報告(JST日付変更後に再開)。
3. `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 --run-dir er118_output/fz_dialogue_context_tts_trial_01 --out er118_output/fz_dialogue_context_tts_trial_01/stop_check_1b.json` rc0確認。
4. `.venv\Scripts\python.exe er118_fz_dialogue_context_tts_trial_01.py gen-session`(1起動、ctx_t1→base_t1→ctx_t2、cap 30円、GO済み)。実行ログ・実送信prompt全文・sha・request config・model名・before/after snapshot・repo mtime走査の結果を保存。再起動は行わない(失敗時は事実を報告)。
5. `analyze`(API 0): leakage(全attempt/final、needs_listen)、comparison_valid、本文逐語一致(ASR)、長さ・RMS(揃える前)・調音話速・F0(信頼性注記)、clip別主指標の完全分離判定(事前登録02)、逆向き分離、過剰監視(c2/c5)、安定監視(c4)、最終相当音声(atempo)生成、音量統一mp3、試聴ページ生成。
6. 試聴ページ公開: `user_test/fz_dialogue_context_trial_01/index.html`(noindex、8カード: 日本語場面説明/話者/英文/前後の会話(折りたたみ)/A=①現行方式(本番最終音声)/B=②改善方式 take1(最終相当)を同じ行にワンクリック、参考にA'=対照base新規take/B'=②take2(折りたたみ)、LLM状態の日本語要約(accept分)、音量注記「本番でも各セリフの音量は揃えられるため、音量の大小ではなく、声の柔らかさ・息づかい・速さ・抑揚で比べてください」。開発者情報は`dev_details.html`)。commit/push後にPages 200確認(index+全mp3、最大6回×120秒)。
7. `EVAL_01.md`(Sonnet所見: 機械指標表[clip×arm×take]、主指標の分離結果、leakage、comparison_valid、ASR正確性、発音悪化の有無、過剰演技の兆候、Fable評価欄は空欄)、`TRIAL_RESULT_01.md`(ユーザー閲覧用・報告9項目の順: 試聴URL/対象一覧と選定理由/①②の具体的Style Promptと文脈情報[①のstyle全文sha+②のCONTEXT 8件全文]/Fable比較評価(空欄)/発話正確性・生成条件・再利用分離の確認/実費と量産単価影響/Status候補(事前登録02: 提出時=USER_DECISION_REQUIRED(試聴判断待ち))とProduction採用に向けた判断事項/SSOT・Git)。`BUDGET_LOG_01.md`。
8. SSOT: `OPEN_ITEMS.md` OPEN-516・OPEN-511を各1行更新(Phase 1b完了・試聴ページURL・Status候補)。`DECISION_LOG.md`は変更しない(Trial)。`docs/pm/ACTIVE_TASK.md`。
9. 委任文逐語 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_03.md`(冒頭「FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_03」、index 568〜600を走査。`--index -1`不可)。
Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。対象pathのみ(`user_test/fz_dialogue_context_trial_01/`のhtml/mp3は追跡可。wav/raw_usage_log/STOP/lock/telemetry不追跡)`git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。

## 報告(`docs/pm/RESULT_PACKET_FZDC3.md`+返答)
試聴URL(200確認)/機械指標表と主指標の分離結果(効果あり・保留・なしの機械判定)/leakage・comparison_valid・ASR正確性/②のCONTEXT全文1例+残り7件は要点/実費(call別)・累計・日次/Status候補/commit hash・raw URL(TRIAL_RESULT_01.md)/RESULT_PACKET 4行。生成に失敗したclipがあれば事実と原因候補を記載(再試行は上限内の既定retryのみ)。