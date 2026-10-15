# 委任文保存(要約版): KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_03 (2026-10-15)
注: 受領した委任文は非常に長いため、実行に必要な要素を逐語に近い形で保存した要約版(全文の完全複写ではない。逸脱としてRESULT_PACKETに記録)。

## 管理ID・性質
KGCPW 委任_03: runtime evidence E1〜E10 + SSOT本文更新。到達上限Status=EVIDENCE_COMPLETE_PENDING_FABLE_JUDGMENT。PRODUCTION_WIREDは宣言しない(文案:「配線・evidence取得済み、Fable判定待ち」)。10条件(ユーザー§8)対応表を作る。
並行: Coffee監査CFSA(Read-only)、Day3。Coffee完成版dir(er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/、user_test/coffee_m2p0_n01_final_03/)は絶対に変更しない(copyのみ)。index.lock衝突は30秒待ち最大3回。
## 費用・禁止
費用Guardrail JPY60(到達でも自動STOPでなく、暴走疑い時のみSTOP)。E7はclip数x1.0円(E2E_TTS_CLIP_EST_JPY)+解説LLM費を事前見積し、JPY30超なら実行せずFable判断待ち。各runに--budget-jpy/--approved-budget-jpyを明示。TTS_EXECUTION_MODE=STANDARD明示(Batch不使用)。
禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。Productionコード・Prompt・schema・flag既定・test本体の変更禁止(不具合は修正せず記録)。Coffee完成版dir・Melos run_e2e_01/02原本変更禁止。HR queue/Lock・Batch TTS不使用。Agent起動禁止。
起動前STOP確認: tools/stop_scope_check_01.py --managed-id KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 --run-dir <run> --out <evidence>/stop_scope_<name>.json。再起動は各runにつき明示許可1回のみ。
## 実行計画
E1 X Std KP段(実LLM, budget 3) / E2 X Adv(b1b, budget 4) / E3 Z KP段(run_e2e_02 copy, --regenerate-stage kp_a2, kp_b1b, approved-budget 8) / E4 harness_kgcpw_01.py --synth-target --level a2|b1b --align-mode real --allow-paid / E5 失敗注入(fail2)+下流拒否 / E6 resolve_gloss→再開 / E7 E2E完成(見積JPY30超なら停止) / E8 Regression直列単独(er003/er019/er026) / E9 model_id・routing / E10 量産費・追加時間。.env kill switchはimport順観測のみ。
evidence出力先: er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/evidence/{E1_x_a2,E2_x_b1b,E3_z,E4_synth,E5_fail2,E6_resume,E7_e2e,E8_regression,E9_E10_summary.json}。Xのrun dir=er019_output/family_x_audio_production_wiring_01/kgcpw_evidence_01/<name>/、Z=er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_01/。
## 成果物
VALIDATION_WIRING_03.md(§0超サマリ/§1 E表/§2 10条件対応表/§3異常系/§4 QDC/§5 mock・注入・実LLM区別/§6残存リスク/§7未確認)、docs/pm/RESULT_PACKET_KGCPW3.md(15項目)。
## SSOT
CURRENT_SPEC L2635付近(既定OFF行を残し直後に追記)、OPEN_ITEMS(OPEN-356更新、OPEN-359追記、新規3件)、DECISION_LOG(1件)、REPORT_LEDGER 1行、USER_DECISION_REGISTER新規行、OPUS_FINDINGS_LEDGER遷移(EVIDENCED等。CLOSEOUT_CONFIRMEDはFable)。
## Git
明示addのみ(VALIDATION_WIRING_03.md、evidence配下の要約JSON/MD/stop_scope/cost集計、SSOT6本、本ファイル+_check.json)。wav/mp3・巨大ログ・共有state・Coffee完成版・user_test・Melos原本はadd不可。commit末尾にCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>、origin/mainへpush。
## ユーザー指示(原文)
委任_01保存ファイルの「ユーザー指示(原文)」節が全文(§5必須検証、§6 C追加量産単価、§7 SSOT・Git、§8 PRODUCTION_WIRED 10条件)。
