## 管理ID

KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(evidenceの6経路化: ユーザー正式決定【全面修正版】§5「確定内容の保護を全6経路で検証する」に従い、委任_02B(commit 438ac1b22/93915b971)で不足したY(runner下流未実測)・X Adv(b1b下流)・Z Std/Adv双方の**現行runner**での確定→下流→改変BLOCKのevidenceを補完する。コード編集は不具合発見時の最小是正のみ。有料上限¥20(TTS再生成禁止、既存take/record再利用)。並行Agent: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(read-only)、LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_05(フォーム)。これらは編集しない。あなたの所有=`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{EVIDENCE_02,EVIDENCE_Y_02,EVIDENCE_X_02,EVIDENCE_Z_02,COST_02}.md`+`evidence_runs/`+`tools/`、必要時のみ`er128_kp_confirmed_content_01.py`+test、`docs/pm/delegation_log/2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_KCP3.md`。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み仕様のruntime evidence補完(6経路×Std/Adv)。到達上限=EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- 禁止: **TTS再生成(02Bの¥7.39の再発防止。`--stage tts`は既存recordが揃っていてAPI 0で通る場合のみ、事前にdry-run/録音数確認)**、公開済み/進行中Production runの改変(必ずコピーdir。コピーはrepo外 `C:\Users\tensh\kcp3_evidence_copies_20261027\`に置きjunction不使用で動くか確認、不可ならrepo内`er128_output/evidence_02/`に置いて完了時に退避)、**同一run dirの5分3回起動(RESTART_STORM)・起動間隔150秒未満**(02Bで自発動した。各起動前に`Start-Sleep 150`相当の待機を実行ログに残す)、STOP/lock解除、Gate緩和、禁止Git操作、所有外ファイル編集(必要なら報告のみ)。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2(有料run前): `py tools/stop_scope_check_01.py --managed-id KP-CONFIRMED-CONTENT-PROTECTION-01 --run-dir <run> --out <...>`。T-3: 費用はusage logから実測。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_03.md` をN=713から順に試し、先頭「## 管理ID」+「KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03」のものを採用。

## 実施事項

1. **Y(Std/Adv)**: コピー元を現行runner世代のrun `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(`audit/style_profile.json`あり、Std/Adv TTS record・assets・pages一式あり。HR Lock残あり=preview未承認。**HR Lockは解除しない**。影響する場合はHR対象segmentを除くstageで検証)に変更。(a)a2/b1bで`confirm --from-form --actor evidence`(payload v2はKP確定済みreviewから生成、文法は現行Adv Part 2の確定があればそれを含める)、(b)`gate`/`assemble`/`pages`/`page_verify`をコピーで実走(API 0見込み。HR Lock起因の停止は「保護とは別理由」と区別して記録)、(c)確定後に英語/訳/区分/解説を各1件改変→G1(stage_kp_post_install/`_assert_kp_review_consistent`)・G2(TTS record)・G3(pages)・G4(Part 2)でBLOCK、runner rcを記録、(d)resume・STALE(再バインド成立/ISSUE)、(e)操作ガード拒否、(f)Yの`--regenerate-stage`(KP系)がLOCKEDで拒否されAPI 0。
2. **X Adv(b1b)**: 02BはX a2下流中心。b1bで確定→`study_text`/`assemble`/`player`(API 0で通る範囲)→改変BLOCK(G1〜G4)。KP英語解説(P7)の扱いが確定英語と整合すること。
3. **Z(Std/Adv)**: 02Bの不足分(Stdのgate〜page_verify実走と改変BLOCK、Advの`--regenerate-stage kp_b1b`拒否=02Bで未実測。150秒規律遵守で1回だけ起動)。公開URL G3のBLOCK(melos kphr_evidence_r3の旧公開訳≠現doc)は「旧公開ページと現docの差」として事実記録し、保護の欠陥でないことの根拠(いつの公開か・docの改訂履歴)を添える。
4. **6経路一覧表(`EVIDENCE_02.md`)**: X-Std/X-Adv/Y-Std/Y-Adv/Z-Std/Z-Advごとに「確定→下流実走」「改変BLOCK G1/G2/G3/G4」「resume/STALE/ISSUE」「操作ガード」「regenerate拒否」「公開URL G3」「API費用」「未観測」を○/×/未観測で。02Bの結果と統合(02Bの結果は再実行しない)。
5. 発見した不具合は同一委任内で最小是正+test(所有内のみ)。所有外(runner等)なら是正案を報告。

## 事前指定Read一覧

- `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{EVIDENCE_01,EVIDENCE_Y_01,EVIDENCE_X_01,EVIDENCE_Z_01,COST_01,IMPLEMENTATION_02B,DESIGN_02}.md`、`tools/kcp2b_ev_*.py`(再利用)
- `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01/`の構成(`a2/`、`b1b/`、`audit/`、HR lock、`human_approved_segments.json`等、Grep不要・ls)、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/REGEN_RESULT_02.md` §3(runner引数先例)
- `er121_family_y_runner_01.py`: Grep `--stages|--stage|--only-segments|regenerate-stage|_assert_kp_review_consistent` ±5(HEAD版)
- `er128_kp_confirmed_content_01.py`: CLI引数(Grep `add_argument` ±2)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_03.md --json-out ...\_check.json`
- 有料/実runner起動前: `py tools/stop_scope_check_01.py --managed-id KP-CONFIRMED-CONTENT-PROTECTION-01 --run-dir <run> --out <run>/audit/stop_scope_check.json`、起動間隔150秒以上(ログに時刻)
- test(是正時のみ): `.venv\Scripts\python.exe run_project_regression.py --pattern "er128_*test*.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_KCP3.md`にOPEN-556追記文案(6経路表・Family別Status案)。

## Git

- commit message: `KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03: 6経路evidence補完(Y現行run・X Adv・Z Std/Adv、TTS再生成なし、実費¥NN)`。trailer: `Delegation: KP-CONFIRMED-CONTENT-PROTECTION-01/03`。push。wav/raw_usage_log/STOP/lock/コピーdir不追跡。

## 報告

`docs/pm/RESULT_PACKET_KCP3.md`: (0)T-0、(1)6経路一覧表、(2)経路別の実行ログ要点(rc、BLOCK箇所、API呼出数)、(3)是正した不具合、(4)費用・規律遵守記録(起動間隔)、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾10行要約。