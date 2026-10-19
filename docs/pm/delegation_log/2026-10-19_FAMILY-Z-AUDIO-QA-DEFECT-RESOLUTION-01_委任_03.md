# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03(Opusレビュー_G/_H逐語保存+Opus_H必須修正6条件の実装[M5 LR後凍結のanchor引継ぎ/Z形entryの原稿解決/HR queue行への元原稿記録/CURRENT_SPEC注記/全体suite再実行/Status注記]+P1判断材料の辞書census(API 0)+⑤残対策(sonnet-worker.md 1文、D-1定義整合)+SSOT統合。原則JPY0、新規TTS 0、HR Lock不変)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Production修正(共有ASR cascade/HR queue/LR経路の整合)+test+文書+SSOT。
- 到達上限Status: `ITEMS23_OPUS_H_CONDITIONS_MET_PENDING_FABLE_WIRED_JUDGMENT`(PRODUCTION_WIRED判定はFable)。①はP1=ユーザー判断待ちのため実装しない。
- 禁止: P1(M1 `_post_check`の受理面変更)の実装/entity保全Gate等の新仕様追加/品質基準・閾値の緩和/HR Lock・`review_lock_state.json`の変更/新規TTS/`er019_output`・`er083*`(並行agentのB3 Trial)への接触/`anchor`不在時に現在時刻やNoneで凍結する実装(安全側=M1不発)。
- 固定ブロック: **E-1**(Opus_H本文[本委任文末尾の要点+逐語保存後の原文]、`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md`、OF-179(OPUS_FINDINGS_LEDGER)、CURRENT_SPEC L2808/L2818、OPEN-371を照合)/**D-1**(修正範囲の線引き: 承認済み仕様(OF-179、ユーザー§4「書換え後原稿を正解に全後続検査」)との矛盾の是正=範囲内。受理面・閾値・方式の新設/拡大=範囲外。読込効率: 指定行範囲のみRead)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_01: er083_*/docs/research/FAMILY-X-B3-BACKGROUND-*とSSOT)**: 共有SSOT(OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER/CURRENT_SPEC)は「編集直前に`git status --porcelain <file>`でclean確認(dirtyなら60秒間隔最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASKは先頭に自ブロック追記(gitignore))/**F-1**(JPY0。census・testはAPI 0)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_03.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ3.md`)。

## Fable決定(Opus_G/_H照合結果)
- Opus_H=GO_WITH_CHANGES、ユーザー判断事項なし。Fableは条件1〜6を全て採用し、充足後に②③のPRODUCTION_WIRED判定を行う(本委任でSonnetが判定しない)。
- Opus_G=GO_WITH_CHANGES、P1は承認済み範囲外(CURRENT_SPEC L2798・OF-178改訂)→**ユーザー判断事項**。本委任ではOpus_Gの必須修正「辞書レベル上限census(API 0)」のみ実施して判断材料を作る。P1実装・test変更はしない。
- ⑤残対策: sonnet-worker.mdへの1文追記=採用(明確化)。U-2(READ_EFFICIENCY_BLOCKのD-1定義を「読込効率+修正範囲の線引き」に整合)=採用(明確化、`check_delegation_prompt.py`の判定が壊れないこと)。U-1(経過日数棚卸し義務)=不採用。

## 作業要件
1. **Opus逐語保存**: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-af5045186c52b1183.jsonl`→`C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\OPUS_REVIEW_G_01_VERBATIM.md`、`...\agent-a45e7eeccb4575743.jsonl`→`OPUS_REVIEW_H_01_VERBATIM.md`(文字数・sha256報告。`--index 0`が正、NOT_FOUNDなら-1も試す)。
2. **Opus_H条件1(論点2 M5)**: `er006_secondary_asr_01.py` `_m1_frozen_for(canonical_text, *, anchor_text=None)`を追加。anchor(元原稿)が凍結済みならその`segment_started_at`(とsnapshot)で書換え後文を凍結、anchor不在ならM1不発(frozen=None)。anchorは`attempt_ctx["m1_anchor_text"]`で受け渡し、4箇所に配線: crosslevel `_retts_fn`(`er003_v1_crosslevel_audio_02_common.py:415`付近)、voice01のLR再TTS、news_tail_fixのLR再TTS、`apply_a2_slowdown_postprocess`(出典=`local_rewrite_text`時)。test4件: (i)元segment開始より後にupsertされたLedgerエントリはLR再TTS・減速後再検証ともM1候補から除外 (ii)開始前エントリは候補のまま (iii)anchor無しはM1不発 (iv)LRなし経路はbyte-identical(出力dictの一致)。`_M1_FROZEN_CACHE`がプロセス内で保持される事実を文書に1行記録。
3. **条件2(論点1 1-a)**: `resolve_expected_text_after_local_rewrite`がZ形entry(`er063_family_z_audio_01.py:932-990` `build_entry`、`audio_text_deviation.audio_text_after`)も扱えるようにする(2次出典として読む案を基本。必要なら`build_entry`へ最小限のLR記録を追加の形で保存)。Z形entryの`guard_entry`/`rejudge` testを追加。
4. **条件3(論点3)**: HR queue行へ`lock_canonical_text`(元原稿)と`expected_text_source`を追加の形で記録(`_post_slowdown_unified_judge`へ元原稿を渡す。`er003_v1_n3_01_tts_generate.py:157-160`、`er006_secondary_asr_01.py:359-362`)。test1件。HR手順書(HRページ生成/承認手順の文書、Grep `record_human_approval`)に「承認キーは元の原稿」を明記。
5. **条件4(論点4・1-b)**: CURRENT_SPEC L2818付近: 「3NGにSecondary障害を含まない」に「未実装・OPEN-371(U4)ユーザー判断待ち」注記、「`lr_used==0`」に「構造的に満たす(明示判定なし)」注記、「減速後再検証・retry・fallback・resume・最終検証」を実態(最終HR遷移とLock keyは元原稿、resumeはLR記録のあるentryのみ[Z形対応後は`audio_text_deviation`も])に合わせる。rollback(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=False`)時の早期LRを「既知の逸脱(rollback時のみ、既定True)」としてOPEN_ITEMS(OPEN-422内)に1行記録(挙動変更はしない)。
6. **条件5**: 修正commit後に全体suiteを再実行し、baseline(委任_02報告: 8555 passed/155 failed+error、うち未commit差分guard2件)との差分0を`ITEMS23_...md` §7末尾に追記。関連suite(`-k "er020 or local_rewrite or er003_v1_n3 or crosslevel or er063 or slowdown or secondary_asr or m1_multi or human_review"`)も全PASS。
7. **条件6**: `ITEMS23_...md`のStatus節に「runtime evidence=offline正式経路(実wav・実ffmpeg・保存転写)。LRのlive発火は未観測。`post_slowdown_expected_text_source=local_rewrite_text`のlive観測は次回LR発火時に確認」を明記。
8. **P1判断材料census(Opus_G必須、API 0)**: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\p1_dictionary_census_01.py`: CMU収録のs/z終わり語(固有名詞+一般語)全件について、P1の4条件(ASR語wがCMU収録/wが期待綴りsとCMU同音/音素列がcanonical側drop/add_s形と一致/(c,s)がbenign単複対)で新たに受理され得る(c,w)ペアの上限一覧と件数(`Jones←Joan`型の別実在語の件数を分離集計、`Hayes←Hey`型が除外されることの確認)。結果`p1_dictionary_census_01_result.json`+要約表(件数・代表例20件)。**P1は実装しない**。
9. **⑤残対策**: `.claude/agents/sonnet-worker.md`に1文追記「承認済み仕様・設計原則との矛盾の是正は仕様候補ではなく不具合(PM_GOVERNANCE 11-8)であり、委任範囲内なら修正・検証まで行う」。`docs/pm/templates/`のREAD_EFFICIENCY_BLOCK(D-1定義、Grep `D-1`)を「読込効率+修正範囲の線引き(11-8の語で記述)」へ整合(`check_delegation_prompt.py`を既存委任文3件で再実行しPASS維持)。`check_defect_vs_spec_rule_01.py`を再実行(49項目維持または増加)。
10. **SSOT統合**: OPEN-422を①②③⑤の統合Status行に整理(①=P1 USER_DECISION_REQUIRED[REGISTER #120に紐付け]、②③=Opus_H条件充足・Fable判定待ち、⑤=対策反映済み)。OPEN-283=修正済み(Opus_H条件反映後のcommit追記)。DECISION_LOG末尾: Opus_G/_H結果とFable決定(P1はユーザー判断、Opus_H条件採用、U-1不採用、U-2採用)。REPORT_LEDGER 1行。ACTIVE_TASK先頭ヘッダ(UDR-blocking: #120 P1/#116 Lock、#119 中東記事[B3BG Trialで代替中])。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md`、`ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md` §5、`PRINCIPLE_NONCOMPLIANCE_ANALYSIS_01.md` §D
- `C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py` L198-211・L302-382・L716-743・L997-1012、`C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01.py` L229・L248-287、`C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py` L121-179・L182-274・L288-307、`C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py` L257-307・L409-442、`C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py` L708-803、`C:\Users\tensh\eigo-radio\er019_family_x_validation_inheritance_01.py` L233-254、`C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py` L718-741・L932-990、`C:\Users\tensh\eigo-radio\er011_human_review_lock_01.py` L179-190・L299-354、`C:\Users\tensh\eigo-radio\er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`
- `C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py` L634-651・L687-696(census用benign判定の再利用)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `rg -n "_m1_frozen_for|segment_started_at|m1_anchor_text" C:\Users\tensh\eigo-radio --glob "er0*.py"`(配線箇所の確認)。
- `rg -n "record_human_approval" C:\Users\tensh\eigo-radio --glob "*.md" --glob "*.py"`(HR手順書の特定)。
- `CURRENT_SPEC.md`: `3NG|Secondary障害|lr_used|減速後再検証・retry`(L2808-2820)→注記修正。
- `OPEN_ITEMS.md`: `OPEN-422|OPEN-283|OPEN-371`。`DECISION_LOG.md`末尾。`docs/pm/USER_DECISION_REGISTER_01.md`: `#120`にOpus_G結論・選択肢A/A'/B/C・census結果を追記。`docs/pm/REPORT_LEDGER.md` 1行。`docs/pm/templates/`: `D-1|READ_EFFICIENCY`。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_03.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_03.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-af5045186c52b1183.jsonl" --role assistant --index 0 --tool-use-name SubagentHandback --tool-input-field message --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\OPUS_REVIEW_G_01_VERBATIM.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a45e7eeccb4575743.jsonl" --role assistant --index 0 --tool-use-name SubagentHandback --tool-input-field message --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\OPUS_REVIEW_H_01_VERBATIM.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio -q -k "er020 or local_rewrite or er003_v1_n3 or crosslevel or er063 or slowdown or secondary_asr or m1_multi or human_review" --ignore=C:\Users\tensh\eigo-radio\er082_output --ignore=C:\Users\tensh\eigo-radio\er083_output`
- 全体suite(commit後): 委任_02と同じper-file runner方式(RESULT_PACKET_FZAQ2.md記載の実コマンドを踏襲し、実行した全文をRESULT_PACKETに記載)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\p1_dictionary_census_01.py --out C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01\p1_dictionary_census_01_result.json`(`-I`でimport不可なら`-I`なし、理由記録)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_defect_vs_spec_rule_01.py --json-out C:\Users\tensh\eigo-radio\docs\pm\tools\check_defect_vs_spec_rule_01_result.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_02.md --json-out C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\recheck_fzaq2.json`(D-1定義変更後のPASS維持確認。同様に委任_01・委任_04でも)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`

## SSOT追記文(要点)
- OPEN-422統合行(上記10)。CURRENT_SPEC L2818注記(上記5)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: Opus逐語2件、コード(er006_secondary_asr/er003_v1_n3/crosslevel/voice01/news_tail_fix/er020/er063の変更分)、test、HR手順書、census script+json、ITEMS23文書更新、delegation_log。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03: Opus_H必須修正(LR後M1凍結のanchor時刻引継ぎ[OF-179]・Z形entryの原稿解決・HR queue行へ元原稿記録)+Regression+全体suite再実行+P1判断材料の辞書census(API 0)+Opus_G/_H逐語保存(JPY0、新規TTS 0)`
- commit 2: sonnet-worker.md、templates(D-1定義)、check結果json。msg: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03: ⑤残対策(sonnet-worker.md 11-8参照1文、委任テンプレートD-1定義を読込効率+修正範囲の線引きへ整合)`
- commit 3: SSOT(CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG/REGISTER/REPORT_LEDGER)。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZAQ3.md`)
4行: (1)整合(Opus_H条件1〜6の充足表[条件/実装箇所:行/test名/結果]、OF-179整合)(2)Production到達経路(変更箇所一覧、runtime evidence種別とlive未観測の明記)(3)成果物とcommit sha 1〜3、関連suite・全体suite結果(baseline差分)、census要約(新規受理上限ペア数、別実在語型の件数、代表例)、⑤残対策のcheck結果(4)撤去/残置。`判定整合:`・`判断候補:`(なし想定。あれば11-8に照らした停止根拠IDを明記)・T-0 check・自己チェック(Lock sha不変/新規TTS 0/P1未実装/受理面・閾値不変)。
