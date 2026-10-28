# 委任_02(逐語): FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 「Opus条件A反映(M-1〜M-5/R-1〜R-7)+Production配線+runtime evidence+AI島Standard再制作(Comment 3のみ)+SSOT同期」

(注: 委任文中のOpus全文コードブロックは同内容を`docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/OPUS_REVIEW_01.md`へ逐語保存済みのため、本ファイルでは該当箇所を参照に置換した。それ以外は委任文のとおり。)

管理ID FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 委任_02「Opus条件A反映(M-1〜M-5/R-1〜R-7)+Production配線+runtime evidence+AI島Standard再制作(Comment 3のみ)+SSOT同期」。前提=委任_01成果(`docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/WIRING_DESIGN_01.md`、`er019_family_x_std_comment3_z_method_01.py`(+test)、ユーザー原文`docs/pm/delegation_log/2026-10-28_FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01_USER.md`)。Fable判断: Opusレビュー=条件付きGO、**M-1〜M-5を全て採用、R-1〜R-7を採用**(R-2は7記事表でfallbackが4/7超になるなら語を絞り理由記録)。ユーザー承認済み(APPROVED_FOR_PRODUCTION)のため配線可。到達目標=PRODUCTION_WIRED(Fable受入後)+AI島Std完成候補のユーザー最終試聴提出(独断で承認済みにしない)。

並行worker: JA-ASR 委任_03(SSOT・ACTIVE_TASKを編集中の可能性)、Z『藪の中』委任_01(er026_seeds/・STORY_REGISTRY)、Family Y Deep Research×2(docs/research/FAMILY-Y-*)。**SSOT編集は直前に再Read・最小Edit・衝突時は再Read再試行**。他workerのファイルをaddしない。Family A/B/C不可。X Advanced・Y/Zのコード挙動は変更しない。
**ファイル範囲**: 新module+test、`er019_family_x_audio_production_runner_01.py`(Comment3呼出・fail-closed停止・C3再生成経路・TTS入口検査の最小変更)、関連test、`docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/`、AI島Std run dir(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/`配下)、候補ページ`user_test/family_x_ai_island_form_01_candidate_b7_01/`(Std側の更新のみ。Advは不変)、SSOT(§6)、`docs/pm/RESULT_PACKET_FXC3P2.md`、`docs/pm/delegation_log/2026-10-28_FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01_委任_02.md`(本文逐語)。
開始時と有料前に `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 --run-dir docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 --out docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/stop_check_02.json`(rc=3で停止)。費用上限¥30(見積: 初回経路evidence LLM5回≈¥0.5、AI島C3再生成≈¥0.1、TTS comment_3 1clip+ASR≈¥1、再試行込み)。cost logger install。TTS直列化flag尊重(他agentのTTS中は待つ)。

## 0. Opusレビュー全文を `OPUS_REVIEW_01.md` へ逐語保存(最初に)
(全文=`docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/OPUS_REVIEW_01.md`)

## 1. 実装(M-1/M-2/M-3/M-5、R-1/R-2/R-3/R-4/R-7)+test
- M-1 regex追加→7記事表再生成(`WIRING_DESIGN_02.md`にfallback件数の前後)。R-2は結果を見て適用範囲を決め理由記録。fallbackが4/7超なら実装を止めず、報告で「ユーザー進言事項」として提示(Fableが判断)。
- M-2 (a)〜(e)。M-3 `--regenerate-support comment_3`経路(共通helper、他4キーsha assert、audit追記マージ、KP/Part/study不変)。M-5 監査項目。R-1 疑問文除外。R-3 未公開X Std runの列挙(該当あればFable判断用に一覧のみ)。R-4 旧定数撤去+test。R-5 非blocking 4-gram重複メモをauditへ。R-7 test群。既存関連test全PASS。
- 配線commit(SSOT前)。

## 2. runtime evidence(M-4)
- 初回経路: `run_family_x_a2_scaffold`をscratch out_dir(`docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/evidence_first_path/`、または%TEMP%配下→証拠jsonのみresearchへ)で実API 1回(AI島partsでよい。公開物に使わない)。prompt全文・response_id・model・comment3_z_audit を保存。
- 再生成経路(AI島Std、公開候補): R-6のparts確定(公開本文「AI agents sent」と一致するpartsを使用、sha記録)→`--regenerate-support comment_3`→C3新文面→lint→他4キーsha不変assert→TTS `--only-segments comment_3`(JA Std、既存ASR Gate適用。**HR Lockになったら停止して報告**、approve_regenerateはFable権限)→validation_inheritanceで他音声引継ぎ→正式assemble→候補ページ`user_test/family_x_ai_island_form_01_candidate_b7_01/`のStd側更新(index/standard.html・audio_standard/comment_3等。Advは不変=sha照合)→page_verify→Pages反映後の実測(200・sha)。
- 証拠を`RUNTIME_EVIDENCE_01.md`に: 両経路のprompt/response_id/model/audit、C3 Before/After全文、他4キーsha、comment_3.wav TTS送信パラメータ・ASR結果、assemble・page_verify結果、Pages URL、費用内訳。

## 3. SSOT同期(追記のみ)
- `CURRENT_SPEC.md`: Family X Std Comment節(Grep「Comment 3」「FAMILY_X_A2_COMMENT_3_ROLE」)に「2026-10-28ユーザー正式決定: X Std Comment 3=Z方式(COMMENT_2_ROLE流用+Part3冒頭の内容基準切り出し+先取りlint+fail-closed、`er019_family_x_std_comment3_z_method_01.py`、Status=PRODUCTION_WIRED(Fable受入後)/旧役割文は撤去、履歴はDECISION_LOG)」を2〜4行。
- `DECISION_LOG.md`末尾1件(採用・Opus条件A反映・配線・AI島Std再制作・Adv承認記録)。
- `OPEN_ITEMS.md`: 新規OPEN(本案件、Status=WIRED_PENDING_FABLE→AI島Std=COMPLETE_USER_LISTENING_PENDING、分類)。AI島関連OPEN(LR系OPEN-57x/UDR #200)に「Adv=ユーザー承認済み(2026-10-28)、Std=Comment 3再制作後に再提出」を追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #200を「Adv=承認済み、Std=再提出待ち」に更新、Trial(FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01)の採否=判断済み(採用)を1行。
- `docs/pm/ACTIVE_TASK.md`: (G)行を更新(Trial→正式採用・配線・AI島Std再制作、試聴待ち)。再Read後に最小Edit。
- `docs/pm/RESULT_PACKET_FXC3P2.md`(≤20行、ユーザー§6の7項目順+4行+判定整合行)。

## 4. Git
段階commit可(配線/evidence/SSOT)。各commitは`git diff --cached --name-only`空確認→自分のファイルのみ明示`git add … && git commit -m "FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 委任_02: …"`を1コマンド。wav/mp3/raw_usage_log不追跡(前例に従う。候補ページのmp3は前例どおり追跡可否確認)。`git add -A`禁止。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 配線点、M-1後のfallback件数、両経路evidence要点(prompt先頭・response_id)、C3 Before/After全文、他4キーsha不変、TTS/ASR/assemble/page_verify/Pages結果、試聴URL、実費、commit sha、判断候補。
