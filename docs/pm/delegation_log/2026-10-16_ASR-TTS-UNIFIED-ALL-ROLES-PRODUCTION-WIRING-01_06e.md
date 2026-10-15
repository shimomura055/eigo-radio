# 委任_06e: AUW — 06dで判明した実run不整合F1〜F3の是正と再実run

場所: `C:\Users\tensh\eigo-radio`、branch `feat/auw-unified-asr-01`(HEAD faa82fdf5)。main禁止。禁止git操作: `add -A`/`-f`/`stash`/`reset --hard`/`checkout -f`/`clean`/`rebase`/`amend`/`force push`。**費用上限 JPY 10**(再実run tstop/kp4/dlg_cap2相当のみ、token実測記録、各run前stop_scope_check rc=0、隔離Lock/隔離queue、共有state md5不変を確認)。**有料runの再起動は不可**(失敗したらそのまま記録して報告)。test実行は通信遮断plugin付き、かつ本番`attempt_history`/`telemetry`へ副作用を出す既存testは並行実行しない(06dの逸脱(b)再発防止)。

## T-0
委任文を`docs/pm/delegation_log/2026-10-16_..._06e.md`へ全文保存、checker→`_check.json`(FAILでも継続)。

## 参照
`RUNTIME_EVIDENCE_06.md` §13-11〜13-13(F1〜F5、tstop traceback、kp4のTTS2/lock、dlg_cap2のlock=RESOLVED)、`IMPLEMENTATION_06c.md`((d)guard_generate/技術STOP entry、(h)`generate_with_a2_slowdown_outer_loop`)、`er063_family_z_audio_01.py`(:667-684 `kp_en` 2段呼出、:1023 `_evidence_row`)、`er003_v1_n3_01_tts_generate.py`(:372-411 外側ループ)、`er011_human_review_lock_01.py`(**ロジック無変更**。既存の`record_outcome`/`guarded_generate`を正しく呼ぶだけ)、ユーザー原文_01.md L58(両NGなら次のTTS再生成)、L39-49(3回NGでLR/HR)、DESIGN_01.md:73(KP英語phrase 4回構成=2026-09-01ユーザー決定)。

## やること
F2. **Z `run_tts_stage`のcircuit-open後KeyError**: 技術STOP entryを`build_entry`に通す(または`_evidence_row`を欠落key耐性に)。`run_tts_stage`レベルのcircuit-open test(技術STOP entryが結果JSONに書かれ、残りclipはTTS 0、`[TECHNICAL_STOP]`報告、異常終了しない)。
F1. **Z `kp_en`の2段呼出に外側guard**: legacy/X入口と同じ`@guarded_generate`相当の外側guardに揃え、KP英語4回構成(既存ユーザー決定)がZでも成立し、1段目STOPPEDでLockが先に立たないこと。mainにも同構造がある既存事象だが、AUWの「全Family統一」の範囲内として是正(Lockロジックは触らない)。test。
F3. **Dialogue/Voices A2外側ループの最終NG**: 通算3回目NGのとき、(i)entryの`asr_judgement`を減速後NGの判定に更新(減速前PASSのまま残さない。退避は`asr_judgement_pre_slowdown`)、(ii)既存`record_outcome`にSTOPPEDとして渡しLockが`HUMAN_REVIEW_REQUIRED`+HR queue 1行(最終slotのみ)になること、(iii)ENならLR経路へ(既存どおり)、を実装。narrator側の同構造も確認し同じ是正。test。
R. **再実run(実音声)**: `tstop`(F2)、`kp4`(F1、Z入口)、`dlg_cap2`(F3)を再実行し、期待どおりになることを`evidence_06e/`に記録(各1回のみ)。
D. `RUNTIME_EVIDENCE_06.md` §14に結果と15条件表の差分(変化があれば)。`IMPLEMENTATION_06c.md`末尾に§8「06e是正」。影響suite(AUW中核30 file+er063/er003 n3/er011関連)per-fileで新規失敗0(baseline=06c)。静的監査snapshot一致。
G. commit/push(branch、明示add、`secret_scan --staged` hits=0)。message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_06e: Z circuit-open KeyError是正+Z kp_en外側guard(KP4回構成統一)+A2外側ループ最終NGのHR末端・asr_judgement更新+再実run。main無変更、JPY <実額>`。

## 禁止/STOP
HR Lockロジック変更(`er011_human_review_lock_01.py`のdiffは0行であること)、U1/U2定数変更、Prompt/Voice/速度/閾値変更、有料run再起動、JPY10超過。F5(Secondary障害でもLRが走る)はU4と同根のため**変更しない**(記録のみ)。

## 報告様式(受入記録5項目)
(1)当初目的=原文L39-49/L58の逐語(ファイル:行) (2)成果物 (3)証拠(再実runの観測値・test数値・commit hash・費用実額) (4)F1/F2/F3/Rごとの一致/不一致 (5)判定材料。加えて逸脱・累計費用・委任_07申し送り。
