# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_06(Trial-03追補: Part 2「基礎文法を選ぶくらいなら0個」の指示強化を1回だけ検証[上限3円]→Fable評価用整理)+ 併記タスク: FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Fable受入記録(API 0)
前提: 委任_05(RESULT_PACKET_FZST5.md、PROMPT_03.md[03c]、EVAL_03.md、commit 71ca6dc99)。Fable独立評価(『賢者』03c): Part 1=hand down(技能・後任者)/catch one's breath(忙しさから一息)とも参考例の要点を満たしPASS、Part 2=倒置の仕組み・通常語順・焦点・foolish↔wisest効果まで説明され、Trial-02のwhose解説から明確に改善=PASS(深さ中程度、文末焦点の説明は薄い)。残存=『開いた窓』Part 2の選定不安定(基礎文を選ぶ/0個が標本間で揺れる)とX Part 2への基礎項目混入(2/4)。

## A. Trial-03追補(有料、上限3円、Luna同一条件)
1. `PROMPT_03.md` のPart 2指示のみを改訂して03dを作る(Part 1は03cのまま、Part 3/4不変)。改訂内容=「候補を検討した結果、Advancedの学習者にとって理解が難しい文が本文にない場合は、Part 2は0個とし、その旨を1文で記す。基礎的な文法項目を埋め草として選ばない(2項目目としても選ばない)。選ぶのは理解の助けになる構文に限る」の趣旨を、作品名・特定文を含めず汎用に指示化。`PROMPT_DIFF_03d.md` に差分と理由。
2. 生成: 『開いた窓』×2、『イグ・ノーベル賞2026』×2、『賢者の贈り物』×1(回帰確認)=5 call(≈1.5円)。無編集保存 `OUTPUT_03d_*_RAW.md`、`usage_03d_*.json`、引用逐語照合(`check_quotes_03.py`流用)。
3. 評価 `EVAL_03.md` §追補: 『開いた窓』が「0個+その旨」または学習価値のある構文(例: 倒置 `Across the quiet garden came a young voice:` を選ぶなら§3の深さで説明)に安定したか、X の基礎項目混入が消えたか、『賢者』が倒置選定・深さを維持したか。改善しなければ原因を記し、これ以上の反復はしない(作品側の天井と結論)。
4. 最終Prompt版(03cまたは03d)の推奨と理由、量産費用(円/記事セット)を `EVAL_03.md` に追記。`BUDGET_LOG_01.md` 更新。STOP確認(`tools/stop_scope_check_01.py`)を有料launch前に実行。
5. Fable盲検用に `COMPARISON_03.md`: 3作品のBefore(Trial-02/02B)/最終版のPart 1・Part 2を並べる(無編集引用)。

## B. FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Fable受入記録(API 0、記録のみ)
以下をそのまま `docs/research/FX-PARAGRAPH-CHUNK-TTS-TRIAL-01/FABLE_EVAL_01.md` に保存し、OPEN-506 Statusを `TRIAL_DONE_FABLE_EVAL_USER_DECISION_REQUIRED(試聴判断)` に更新、`docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(件名=段落単位Chunk方式の採否[試聴判断]、選択肢(a)B0採用方向で設計へ/(b)B採用方向で設計へ/(c)不採用、Fable推奨=(a)B0[声質の一貫性に違和感がなければ]、試聴URL https://shimomura055.github.io/eigo-radio/user_test/fx_paragraph_chunk_trial_01/index.html 、非blocking)、`DECISION_LOG.md` 1件。
```
# FABLE_EVAL_01 — FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Fable独立評価(2026-10-25、委任_02成果、API 0)
- 客観面: 全Gate PASS(ASR一致・Repetition QA)、HR Lock 0、条件差異chunk 0、mp3 22本の公開確認、Production store/承認済み音声/公開ページのsha256不変、Opus条件A必須修正M1〜M4反映済み。
- 速度: 実発話が約7%遅い(A→B_r1 全長+10.1秒のうち発話区間+7.7秒、段落境界gap+2.6秒。B0は+6.6秒で境界gapはAと同等)。段落10対×4組すべて同方向・art300同方向のため断定可。見かけの減速ではない。
- 接続・音量: 境界音量差はB最大5.8dB(承認済みAのpart境界7.8〜8.3dBより小)、peak頭打ち0、語欠け・二重なし。
- 音質改善・声質の一貫性(過去P6B不合格理由)は機械指標で代替せず、ユーザー試聴で判断。
- 費用: Trial実費13.89円/上限50円。採用時Advanced本文あたり約+0.30円(+7.5%)、所要+約6秒。
- Status(Fable): USER_DECISION_REQUIRED(試聴判断)。VALIDATED/REJECTEDはユーザー試聴後に確定。Production採用は含まない。
- 推奨: 声質の一貫性に違和感がなければB0(追加ポーズなし)を採用方向で設計(ポーズ構造をAと同等に保ったまま実発話の減速を得られ、コスト増が小さい)。違和感があれば不採用。採用時は配線設計→Opus条件C→ユーザー承認。
- 限界: 標本A 2take/B 2take、word timestamp精度限界、mtime走査が並行agentの書込みで誤検知(実害なし)。
```

## C. 共通
- SSOT: OPEN-497(Trial-03追補結果・最終Prompt版・Status候補)、OPEN-506(上記)、`DECISION_LOG.md`(2件)、`docs/pm/ACTIVE_TASK.md` 自行のみ(並行agent: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_02、FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02 が同時編集中。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認(OPEN_ITEMS.mdはCRLF/LF混在、USER_DECISION_REGISTERはCRLF化事故の前例あり)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 507 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_06.md`。冒頭が「管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_06」と一致するか確認、不一致なら index 505〜510 を順に試す(`--index -1`不可)。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。
- 報告 `docs/pm/RESULT_PACKET_FZST6.md`: ①03d差分、②追補結果(作品×標本の選定と判定)、③最終Prompt推奨版と理由、④実費(委任_05累計+追補)/量産費用、⑤Status候補、⑥B記録の完了(UDR番号)、⑦変更ファイル・commit、⑧`check_delegation_prompt.py`結果、⑨問題点。raw URL(COMPARISON_03.md、EVAL_03.md、OUTPUT_03d_*)。

## D. 禁止
Production code/Prompt/flag変更、KP追加選定、音声生成、Web検索、出力の編集、Part 1/3/4 Promptの変更(Part 2のみ)、上限3円超過、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction配線へ進まない。