## 管理ID

FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(修正=ユーザー決定の反映、委任 _04、本管理IDの Sonnet 最終回)。対象はローカル Python パイプラインの prompt 定数削除(最小 diff)。一時ファイル `docs/pm/ACTIVE_TASK_AN3D.md` / `docs/pm/RESULT_PACKET_AN3D.md`(commitしない)。並行: 別Sonnet 3件(Task 1 `er045_*`、Task 3 `er047_*`、Task 4 Phase B `er019_family_x_audio_production_runner_01.py`/`er033_*`/`er003_b1_p9a_audio.py`/`er003_v1_n3_01_tts_generate.py`/SSOT 4点[編集中])→ これらに触れない。**SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ RESULT_PACKET へ)**。本タスクの所有: `er019_family_x_ja_writer_o_r1_r2_01.py`、`er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`、`FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`(§16 追記)、設計書 `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md`(§9 追記)、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。API 支出 **上限¥0**(LLM 呼び出し禁止。runtime 再生成は行わない=理由は下記)。APIキー本文表示禁止。

## ユーザー正式決定(2026-09-28、逐語要旨)

「R1/R2 reminder: 不要。削除する。理由: AN3-T0 を評価した Trial-02 では、この Reminder は入っていなかった。Trial-02 の実際の構成は、Original 生成時に AN3(A3+N2)を追加/R1・R2 は既存 Revision 指示のみ。したがって Production Wiring Phase で追加した『この修正で、すでに減らした細かい数字・時刻や固有名詞を、記事理解に必要でない限り再び増やさないでください。』は未 Trial 追加仕様。Production 正式経路から外すこと。対応: R1/R2 通常経路から削除/Fact Check must-fix 経路から削除/Symbol must-fix 経路から削除/fallback 経路でも同 Reminder を残さない/runtime evidence・SHA・test・CURRENT_SPEC・DECISION_LOG 等で Reminder を正式仕様扱いしている箇所を是正/Trial-02 と同じ条件、すなわち AN3 は Original 側のみ に戻す。AN3-T0 Production Wiring は、Trial で検証済みの仕様に合わせること。」

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定の反映(仕様縮小)。Status は `APPROVED_FOR_PRODUCTION`(Gate 3 保留、OPEN-228 順序はユーザー決定済み)のまま。
- 禁止: `CONCRETENESS_CONTROL_AN3_BLOCK`(Original 側)の変更/R0_PROMPT・REVISION_INSTRUCTIONS 本体の変更/OPEN-228 関連(split/Gate/retry)への変更/Advanced 化 Prompt の変更/リファクタリング/runtime 再生成(¥0)。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(SSOT は Grep のみ、編集禁止)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_04.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_04.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_04.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 手順

1. `er019_family_x_ja_writer_o_r1_r2_01.py`: `CONCRETENESS_CONTROL_AN3_REMINDER_JA` 定数と、R1/R2 の 3 箇所(通常 r1/r2 ループ・R2 Fact Check must-fix・R2 音声記号 must-fix)の append を削除し、各箇所を **Phase B 以前(commit `b814f241` 時点)の逐語**に戻す(`git show b814f241:er019_family_x_ja_writer_o_r1_r2_01.py` と該当行を diff で照合し、Original 側の `CONCRETENESS_CONTROL_AN3_BLOCK` 追記(1 行)と `verbatim_shas()` の `concreteness_an3_block_sha256` のみが残ることを確認)。`verbatim_shas()` から `concreteness_an3_reminder_sha256` を削除。fallback_full_text 経路にも reminder 文言が残っていないことを Grep で確認(`再び増やさない` が 0 件)。
2. テスト `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`: reminder 関連ケース(3 経路含有、sha キー)を「**含まれないこと**」の assert に置換(R1/R2 の 3 経路の instruction が Phase B 以前の逐語=`REVISION_INSTRUCTIONS[...]`(+既存 SYMBOL_PREVENTION_BLOCK_JA/must-fix block)のみ、`再び増やさない` 不在、`verbatim_shas()` に reminder キー不在)。Original 側のケース(BLOCK 含有、er037 逐語一致、T1 不在、Advanced Prompt sha 一致)は維持。`run_project_regression.py --pattern "er019*_test_*.py"`、`"er037*_test_*.py"`、`"er039*_test_*.py"` 全 PASS。
3. runtime evidence: 既存の `an3_t0_wiring_regression_01/{hormuz,meta}/runtime_evidence.json` は Phase B 時点(reminder あり)の記録のため、そのまま残し(削除禁止)、REPORT に「Phase B 時点の証拠。reminder 削除後の R1/R2 は Trial-02(`er039`、AN3-T0 セル)と同一条件であり、Original 側の BLOCK と sha は不変」と明記。**再生成は行わない**(¥0。Trial-02 の AN3-T0 実測が reminder なし構成の証拠)。
4. REPORT §16「ユーザー決定による R1/R2 reminder 削除(2026-09-28)」: 削除箇所(ファイル・行)、Phase B 以前との逐語一致の diff 結果、テスト結果、runtime evidence の扱い、Checklist 項目「R1/R2 で再前景化しない既存方針との整合」は「Trial-02 と同一条件(R1/R2 は既存 Revision 指示のみ)」として充足と再記載。設計書 §9 に同旨。
5. SSOT 文案(RESULT_PACKET へ、編集せず): CURRENT_SPEC の「Family X Writer — Concreteness Control(AN3-T0)」小節から reminder 記述を削除し「AN3 は Original 側のみ(Trial-02 と同一条件)」に是正する文案/DECISION_LOG 新エントリ文案(ユーザー決定・削除内容・commit)/OPEN-227 の文言調整案(reminder 付与への言及を削除、非対称性の記録は維持)/REPORT_LEDGER 備考更新案。

## 事前指定Read一覧

- `er019_family_x_ja_writer_o_r1_r2_01.py`: Grep `CONCRETENESS_CONTROL_AN3|再び増やさない|verbatim_shas` → 該当範囲
- `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`(全文)
- `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`: Grep `REMINDER|reminder|## ` → 見出しと該当箇所

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記+`CURRENT_SPEC.md`(`REMINDER|再び増やさない`、文案作成のため read-only)。
- 更新位置: `er019_family_x_ja_writer_o_r1_r2_01.py` の該当 4 箇所、テスト、REPORT 末尾 §16、設計書末尾 §9。

## 実行コマンド全文

- `git show b814f241:er019_family_x_ja_writer_o_r1_r2_01.py > "%TEMP%\jaw_b814f241.py"` 相当(scratchpad へ出力)→ `git diff --no-index` で現行との差分が Original 1 行+sha 1 キーのみであることを確認(出力を REPORT に転記)
- `.venv\Scripts\python.exe -m unittest er019_family_x_concreteness_an3_t0_production_wiring_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er037/er039)
- `grep -n "再び増やさない" er0*.py`(0 件)

## SSOT追記文

RESULT_PACKET へ文案のみ(上記 5)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er019_family_x_ja_writer_o_r1_r2_01.py`、テスト、REPORT、設計書、delegation_log+`_check.json`。SSOT 編集権なし。他Agent差分(er045/047、Task 4 Phase B の 4 ファイル、SSOT)は add しない。
- メッセージ: `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01: ユーザー決定によりR1/R2 reminderを削除(AN3はOriginal側のみ=Trial-02と同一条件)、テスト・REPORT是正`、trailer `Management-ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_AN3D + handback、目安20行)

削除箇所/Phase B 以前との diff 結果(残差=Original 1 行+sha 1 キー)/`再び増やさない` 0 件/テスト結果/runtime evidence の扱い/SSOT 文案の所在/commit hash・push・raw URL/禁止操作未実施/STOP有無。
