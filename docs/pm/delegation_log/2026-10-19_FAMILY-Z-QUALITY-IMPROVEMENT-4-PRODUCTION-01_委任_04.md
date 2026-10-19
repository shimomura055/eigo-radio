# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_04(③Standard Dialogue=Advanced同一Style+後処理6%減速、④本文語数400±70 のProduction実装+test。**JPY0、有料実行なし**。再生成はPhase 3(別委任))。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 承認済み仕様(ユーザー2026-10-19 APPROVED_FOR_PRODUCTION ③④)の正式Production配線(コード・test・文書)。Opus条件Aレビュー_Eが並行中(③④は低リスクで先行実装を許可。レビュー結果で修正が出れば後続委任で反映)。
- 到達上限Status: `ITEMS34_CODE_WIRED_TESTED_PENDING_PHASE3`(runtime evidenceはPhase 3後。PRODUCTION_WIREDはFableが判定)。
- 禁止: 有料実行/音声・原稿の再生成/③でWPM数値基準・追加品質Gateの新設/③でVoice割当・narrator PD06・Std本文6%減速の変更/`FAMILY_Z_ROLE_STYLE_VERSION`のbump(全clip再生成になるため)/他Familyが使う共有定数`n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER`の削除/④でハードキャップ・自動再生成・STOPの導入/`seed.json`の編集/②①の実装(別委任)/`er062_family_z_writer_01.py`の`run_support_std`周辺の変更(②用に残す。④は定数・Prompt文言・Guardrail文言のみ)。
- 固定ブロック: **E-1**(ITEMS234_DESIGN_01 §3(③)・§4(④)・§7に従う。設計と異なる実装が必要なら理由を報告)/**D-1**(不適用=承認済み仕様の正式配線、既定ON)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentなし(Opusはread-only)だが、SSOTは自分の変更行のみstaged blob、`.git/index.lock`待ち再試行)/**F-1**(JPY0)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_04.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI4.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\ITEMS234_DESIGN_01.md` §3・§4・§5・§7
- `C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py` L690-810(`style_text_for`、`dialogue()`、reuse_key)
- `C:\Users\tensh\eigo-radio\er012_b*`の該当箇所(設計書記載の`:519` override受渡し)
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py` 語数定数・Prompt文言・WARN(L120-135、L385-399、Prompt文言4箇所)
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L620-630(`ACCEPT_WORD_RANGE`)
- 既存test: `er063_family_z_audio_01_test_01.py`(L600-620)、`er078_*_05_test`/`_06c_test`該当行、`er063_family_z_common_style_wiring_01_test_01.py`、`er062_family_z_writer_01_test*.py`、`er026_family_z_e2e_integration_test_01.py`

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `A2_ENGLISH_STYLE_PREFIX_SLOWER` in `er063_family_z_audio_01.py`→該当2箇所(`style_text_for`のa2分岐・`dialogue()`のoverride)を撤去し、Std/AdvともDialogueは既定`ENGLISH_STYLE_PREFIX`(Advと同一)になるようにする。撤去後のGrep残存=0(er063内)を報告。
- Grep `350|280|420|TARGET_WORDS|WORD_RANGE|ACCEPT_WORD_RANGE` in `er062_family_z_writer_01.py`・`er026_family_z_fiction_production_runner_01.py`・関連test→400/330/470へ。Prompt文言4箇所の更新(語数の数値と「目安・WARNのみ」の意味は維持)。
- `CURRENT_SPEC.md`: Grep `A2_ENGLISH_STYLE_PREFIX_SLOWER|Dialogue`(Family Z節 L1600/1611/1674付近)→③の仕様文へ更新(「StdのDialogueはAdvと同一Style、生成後6%減速のみ。Voice割当維持」)。Grep `280〜420|350語`(L1606付近)→「目標400語、目安330〜470(400±70)、WARNのみ、語数理由の自動再生成・STOPなし」へ。「Family X共通目標」の不正確な括弧は削除(設計書§7)。共通Status表(L1664-1682)は変更しない。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→③④「コード配線・test済み、runtime evidence待ち」を追記。
- `DECISION_LOG.md`: 末尾に委任_04エントリ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 作業(順序)
A. T-0。B. ③実装: `er063`の2箇所撤去+`er012_b…:519`経由の一貫性確認(primary/minimal fallback/外側ループ/resumeが全て同一箇所でStyleを決めることをコードで示す)+`style_record.json`のDialogue記録・`CROSS_FAMILY_COMMON_STYLE_MAP`・drift testへの影響確認(Dialogueは共通Style対象外のまま)。test更新3件+新規3件(Std/Advとも`style_text_for`=None(またはAdvと同一)/Std Dialogue以外のreuse_key golden不変/er063内SLOWER残存0のGrep test)。
C. ④実装: 定数・Prompt文言・`ACCEPT_WORD_RANGE`・WARN文言・test(更新約6件+新規約3件: 400±70の境界、WARNのみでraiseしない、Promptに400が含まれる)。`seed.json`不変。`*_prompt.txt`退避手順(Phase 3前)を`ITEMS234_DESIGN_01.md`§4に明記済みなら、Phase 3委任用に実行コマンドを追記。
D. 回帰: er063系3 module、er062 writer test、er026 integration、er078 05/06c、`er019_family_x_fx_20261016_wiring_01_test_01`(X側不変確認)。PASS数報告。
E. メロス本文語数の実測(Std/Adv、既存の語数関数で)→新範囲内であることを記録(再生成不要の根拠)。
F. SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_04.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_04.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_common_style_wiring_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_pd06_run_style_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_fx_20261016_wiring_01_test_01.py -q`(+er062 writer test・er078 05/06c testの実在file名を追加)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC(Family Z節): 「③ Std Dialogue: Advと同一Dialogue Style(生成時減速指示なし)+生成後6%減速。Voice割当維持。2026-10-19ユーザー決定、コード配線済み(commit)、runtime evidence待ち」「④ 本文語数: 目標400、目安330〜470(400±70)、WARNのみ、語数理由の自動再生成・STOPなし。2026-10-19ユーザー決定」。
- OPEN-419: ③④の進捗。
- DECISION_LOG: 「2026-10-19 FZQI 委任_04: ③④コード配線+test(JPY0)。runtime evidenceはPhase 3」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_04+_check.json、`er063_family_z_audio_01.py`、`er062_family_z_writer_01.py`、`er026_family_z_fiction_production_runner_01.py`(ACCEPT_WORD_RANGEのみ)、更新/新規test、ITEMS234_DESIGN_01.md(追記分)、CURRENT_SPEC.md、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_04: ③Std Dialogue=Adv同一Style(生成時減速指示撤去、後処理6%減速維持、Voice不変、version非bump)+④本文語数400±70(WARNのみ)をProduction配線+test(JPY0、runtime evidenceはPhase 3)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI4.md`)
4行: (1)整合(設計書§3/§4との一致、差異があれば理由)(2)Production到達経路(③: Style決定の単一箇所とfallback/resume経路、reuse_key変化がStd Dialogue 10clipに限られる根拠/④: WARNのみの根拠)(3)成果物とcommit sha、test PASS数、SLOWER残存Grep(er063=0、他Family=残置件数)、メロス語数実測(4)撤去/残置。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/version非bump/Voice不変/seed.json不変/②①未着手)。
