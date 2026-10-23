FABLE-DELEGATION-MARKER: FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01-CLOSEOUT-委任_02-20261023

# 委任_02(小): Family Z会話速度仕様v2のFable受入(PRODUCTION_WIRED)をSSOTへ反映(費用0・Production変更なし)

## T-0
- 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01_委任_02.md`(N≈334〜344、先頭行MARKER一致確認)。
- 別agent(FAMILY-Z-SOURCE-FIDELITY 委任_03 U1 Trial)が並行中。共有SSOTは編集直前`git status`→再Grep→自分の行のみ→即commit。ACTIVE_TASKはOPEN-462行のみ更新(CLOSED/受入済み)。

## Fable受入判定(2026-10-23、そのまま記録)
FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01: **PRODUCTION_WIRED(Family Z)**。根拠(受入条件照合): (1)正式初回経路への配線=`er063_family_z_audio_01.py` level×kind速度表・dialogue generator・`speed_profile`記録・reuse_key version・Gate `verify_z_speed_profile`(commit b37804d2d) (2)runtime evidence=Production runner正式経路での2作品4組再処理(会話clipはTrial B wavとsha一致 57/57、非対象clip sha不変 113/113、gate PASS 4/4)+新規生成経路(`melos/run_dsw_evidence_01`、Std会話後処理なし・Adv会話tempo1.06・長さ比0.9485) (3)retry/fallback/regen/resume/Store=reuse_keyに`speed_profile=z_speed_v2:*`、旧entry非再利用test、中断復帰の二重適用なし、ASR NG時原音復元 (4)速度変更後ASR=Adv会話29clip統一judge PASS 28+PASS_WITH_WARNING 1(Trial時と同一clip) (5)回帰=collected 6,925/passed 6,915/failed 0/errors 0、pytest別枠984 PASS、新規test 24 (6)公開4ページ更新・HTTP200・実再生302/302 (7)Dangling/撤去=Std会話の減速呼出とGate要求を撤去、`+post6%` style_labelは記録照合のため意図的残置(コメント明記) (8)SSOT・commit b37804d2d/a52e99f76/fa474da63/b3defe8f8/ad949a05a push済み (9)費用約2.3円。
付随事実(記録のみ): メロスAdv KP1英語`sentence someone to death`が既存KP3V reuse gate(fail-closed)により正規retryで再生成(TTS 2call、PASS_DUAL、+0.16秒)=仕様どおりの動作。『開いた窓』は本文未変更・`USER_LISTENING_PENDING`+OPEN-465未解決のままCLOSEDにしない。ユーザー後続指示(『開いた窓』最終組立は全仕様が揃ってから)より前に本配線の4組更新が完了していたため、速度適用済み版が公開中。原作忠実性配線後に再組立が1回発生する(TTS再生成なし見込み)。X側`A2_SLOWDOWN_TARGET_SEGMENTS`の検知ガード穴はOPEN-466で別途。

## 作業
1. CURRENT_SPEC 会話速度v2のStatus行→`PRODUCTION_WIRED(Family Z、Fable受入2026-10-23)`。OPEN-462→PRODUCTION_WIRED(公開4組の更新状況を個別記載: メロスStd/Adv・開いた窓Std/Adv=更新済み・再生検証OK)。DECISION_LOG受入エントリ。UDR #159に配線完了追記。REPORT_LEDGER 1行。
2. commit(明示add、secret_scan `--staged` hits=0)、`git push origin HEAD:main`。報告: 変更ファイル・raw URL・commit hash+「判定整合: 重大NG=あり/なし」。