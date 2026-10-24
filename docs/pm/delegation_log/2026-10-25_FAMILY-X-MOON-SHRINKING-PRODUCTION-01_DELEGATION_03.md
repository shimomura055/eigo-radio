管理ID: FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_03 — 本文から中核数値(半径約42〜46m・ここ数億年・推定)が全て脱落した問題の原因究明と是正。作品累計上限を**150円**に引上げ(既使用63.78円。7-7の300円以内でFable判断、70円目標との差は報告で開示)。

## Fable判断
- ユーザー指示(原文 `docs/pm/delegation_log/2026-10-24_FAMILY-XZ-MOON-TELLTALE-PRODUCTION-01_USER.md`)は「縮小量の対象期間・推定の根拠・不確実性を正確に扱う」を本作の品質条件として明示している。数値が0個の本文は、冒頭の問い「どれだけ縮んだか」に答えておらず、この条件を満たさない。**現状のまま完成候補とはしない**。UDR #189は「Fableが是正を試みたうえで必要なら再提示」に更新(選択肢Aを推奨しない)。
- 是正は承認済み仕様の範囲内で行う(Prompt・Gate・仕様の変更禁止)。B3が【中核数値】注記を付けているのにW-1 R0で落ちたのは、Writer出力のばらつきか既存不具合かを先に切り分ける。

## 作業
1. 本委任文を `docs/pm/delegation_log/2026-10-25_FAMILY-X-MOON-SHRINKING-PRODUCTION-01_DELEGATION_03.md` に逐語保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新(493以降。見つからなければjsonlをgrepしてindexを特定)> --out <path>`、先頭行一致確認)。
2. **原因究明(API 0)**: `er019_output/moon_shrinking/run_ms_01/` のB3出力(中核数値の選定と注記)→W-1入力→`ja_writer/original.md`(R0)→R1/R2の各段で数値がどこで消えたかを特定。W-1 PromptとCURRENT_SPECの中核数値規定(`CURRENT_SPEC.md:2875`付近「中核数値丸め」と周辺、B3→W-1の受け渡し仕様)を確認し、「Writerは中核数値を本文に含める」ことが仕様上期待されているか/明文化されていないかを根拠付きで記録。比較として直近X記事(『英単語ガチャ』run_wg_01、記事A ig_nobel_2026、記事B uk_train)のR0に中核数値が含まれていたかを確認(Writerのばらつきか、本作固有[科学記事で数値を"専門的"と判断して省いた可能性]かを判定)。結果を `NUMERIC_DROPOUT_ROOT_CAUSE_01.md` に保存。
3. **是正(有料、最小再生成)**: Ledger・B3の成果物を再利用し、**W-1以降だけ**を再実行できる正式経路(runnerのstage/resume/`--from-stage`等。CP_CHECK_01とrunnerの引数を確認)で、新run dir(`run_ms_02`等、run_ms_01は保全)に日本語W-1→忠実英訳→KP→audio→pagesを再実行する。W-1再実行の入力はrun_ms_01と同一(B3・注記・theme.txt。Prompt改変・本作固有Prompt新設禁止)。W-1以降の再実行が正式経路で不可能な場合のみtext全段再実行(その場合も上限150円内)。
   - 再生成後のR2/Std/Adv本文で、中核数値(縮小量42〜46m[丸め規定に従う]・対象期間[ここ数億年]・「推定」である旨)と不確実性(「今も続いているかは可能性」)が含まれ、禁止表現0件であることを `FACT_CHECK_03.md` で確認。**数値が再び脱落した場合は再々実行せず停止**し、原因(仕様上の必須化がないこと)と選択肢を報告(USER_DECISION_REQUIRED候補)。
   - audio段は正式経路1起動(`--stage all`)、HR Lock・Style Gate人間承認待ちは停止報告、TTS直列化flag尊重、起動間隔150秒以上、RESTART_STORM回避、cost logger install、`.venv\Scripts\python.exe`。日次はJST 10-25に切替済み(新日次1,000円)。
   - 公開ページ `user_test/family_x_moon_shrinking_01/` を新版へ差替え(旧版はrun dirに保全)、page_verify PASS。
4. `RUNTIME_EVIDENCE_02.md`(新run: 入口・stage・model_id・Gate結果・KP一覧と`meaning_stage`・ASR・HR・費用内訳[run_ms_01+02の累計と70円目標差]・所要・URL)。OPEN-505・UDR #189・DECISION_LOG・ACTIVE_TASKを更新(別agentとの並行編集はないが、直前再Read・最小Edit)。
5. Git: 自分の変更のみ(`git add <path>`→`git diff --cached --name-status`→`git commit --only -- <path…>`または前例のupdate-index方式)→`git push origin HEAD:main`。公開mp3は`user_test`配下のみ追跡、wav/raw_usage_log/sources不追跡。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret grep 0件。OPEN-490。
6. 報告 `docs/pm/RESULT_PACKET_FXMS3.md`: 原因究明結論/是正経路と再利用範囲/新本文の数値・期間・不確実性の所在(引用)/Gate結果/KP/費用累計/URL/残存事項。到達目標「正式完成候補・ユーザー最終試聴待ち」、PASS先取り禁止。