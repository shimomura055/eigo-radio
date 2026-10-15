# 委任文 FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_02 (2026-10-15、全文保存)

## 管理ID

`FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01`(CFSA)委任_02(統合: 01A仕様側+01B成果物側→仕様反映マトリクス完成版・監査報告書)。並行: KGCPW 委任_03(コード・`er071_output/.../gloss_alignment_production_wiring_01/`・SSOT6本・ACTIVE_TASK・REPORT_LEDGER編集中)、Day3 委任_F2(`PM_GOVERNANCE.md`/`CLAUDE.md`/`PM_BRIEF.md`/`docs/research/.../day3/`)。本委任はRead-only監査で、これらに一切触れない。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: Read-only監査の統合・判定・報告書作成。Production実装・音声再生成・有料API・Trial・SSOT編集・Open Item起票は禁止(文案のみ)。到達上限Status: `AUDIT_COMPLETE`または`AUDIT_INCOMPLETE`(未確認項目が結論を左右する場合。理由明記)。音声成果物・Production仕様のStatusは変更しない。
- 禁止: 有料API 0(JPY0)。SSOT/`ACTIVE_TASK.md`/`REPORT_LEDGER.md`/`USER_DECISION_REGISTER_01.md`/コード/Prompt/profile/音声/`user_test/`の編集禁止。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。新Validator・新管理制度の提案禁止(既存機構・既存Gateの範囲での是正案のみ。Day 2運営モデル[F3独立受入・承認済み指示欄・Gate 7集約]との関係は「検討事項」として記述し、進行中の実装へ介入しない)。推測をPASS扱いしない。証拠がなければ「未確認」。費用・工数の数字は出典のある確認済みの値のみ(未確認は数字を出さず「未確認」)。
- Opus独立技術レビューGate: 非該当(監査)。
- 時間見込み: 約2h(マトリクス統合1.0h/原因分析0.4h/報告書0.6h)。並列化: 単一文書への統合のため直列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本、全文Readは構造変更時のみ。G-1: git出力は--porcelain/--stat/--short等で最小化。F-1: 自タスクのtranscript退避は不要。T-0: 受領した委任文を本ファイルへ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続、記録用)。T-2: TTSを伴う委任はSTANDARD明示(本委任はTTSなし)。T-3: 費用上限JPY0のためGuardrail文不要。

## ユーザー指示(原文)

委任_01A保存ファイル(`docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01A.md`「ユーザー指示(原文)」節)に全文(逐語)。本委任で直接効く逐語:
> 「### 4. 必須成果物：仕様反映マトリクス 各仕様について、少なくとも以下を記録する。仕様名・管理ID(Trial／承認／実装の出典)/対象(Standard／Advanced／両方)/Trial結果(VALIDATED／REJECTED／未検証)/ユーザー判断(採用／Coffee限定採用／保留／不採用)/完成版への適用要否(必須／今回対象／対象外／要判断)/期待動作(本来どうあるべきか)/実際の完成版(原稿・音声・Prompt等の観測結果)/判定(反映済み／未反映／部分反映／証拠不足)/原因(仕様管理・配線・再利用・受入等)/是正方針(必要な最小対応)。推測をPASS扱いしないこと。証拠がなければ「未確認」と記録する。」
> 「### 5. 原因分析・再発防止 反映漏れが見つかった場合、個別修正案だけでは不十分。以下を区別して根本原因を分析する。1. Trial成果が正式な採否判断へつながっていなかった。2. 採用済み仕様がProduction経路に反映されていなかった。3. Production側には存在するが、Coffee完成版では旧artifactやseedを再利用した。4. 完成条件に必要仕様の網羅性確認がなかった。5. Fableが実際の完成物を照合せず受入れた。6. CURRENT_SPEC／Decision Log／Open Itemsの情報が制作時に参照されなかった。今回のDay 2運営モデル刷新と関係する問題は、再発防止の検討事項として報告すること。ただし、進行中の運営モデル実装へ無断介入しないこと。」
> 「### 6. 監査後の修正で音声再生成が必要な場合は、変更対象segmentを特定し、全記事を無条件に再生成しない最小対応案を提示する。」
> 「### 8. 報告形式 最初に、非エンジニアPM向けの超サマリを提示すること。その後、次の順序で報告する。1. 結論：Coffee完成版は当初要求を満たしていたか 2. Standard／Advanced別の仕様反映一覧 3. 未反映・部分反映・証拠不足の項目 4. In One Lineが1文のままになった根本原因 5. Key Phrase／Voice Prompt等の実際の反映証拠 6. 必要な是正内容と最小限の再生成範囲 7. 今回の反映漏れを引き起こしたPM・制作工程の問題 8. QDC影響・費用見込み 9. 未解決事項・ユーザー判断が本当に必要な事項。」
> 「今回の最終Statusは監査完了または未完了とし、音声成果物やProduction仕様をPRODUCTION_WIREDへ変更しない。監査結果を提出したところでSTOPし、ユーザーの判断を待つこと。」
> 「最重要事項: 今回の本質は、In One Lineの1文だけではない。ユーザーが求めた『最新の改善成果を網羅したCoffee完成版』が本当に作られていたか、仕様・Prompt・音声・成果物の全体を確認すること。仕様が承認されていても完成品に反映されていなければ、完成とはいえない。また、VALIDATEDであっても未承認の仕様は、Production採用と区別して報告すること。根本原因と最小是正案を揃え、ユーザーが次の判断をできる状態で報告してください。」

## KPI provenance欄 / Opus台帳更新
該当なし(監査、全てreuse / 台帳は編集しない)。

## Fableが照合済みの事実(統合の前提。鵜呑みにせず原文で再確認してよい)
- `CURRENT_SPEC.md:583`: In One Lineの正式仕様(2026-08-09 DECIDED、ER-003-A2-STRUCT-05)=「中心1文(要約)+英語の短い補足2文程度」。final_03の両levelは1文15語(`a2/parts.json:10`、`b1b/parts.json:10`)=正式仕様にも未達。
- `a2/key_phrases/gloss_alignment_runtime_metadata.json:3-4`: version `ER-003-KP-GLOSS-ALIGN-01`(旧legacy)、`ALIGN_PASS`、targets=[4]。corrected(2026-10-15採用、配線中KGCPW)ではない。
- `er019_family_x_style_profile_01.py:16-18`: Phase 1=Full Storyのみ、K2/M2/A5/B5/E1/R2等は後続Phase、OPEN-298/299は範囲外。
- `DECISION_LOG.md:21007`: in_one_line Trial rawを`_replaced_02/`へ退避し検証済みtakeへ置換(COMPLETION-01 委任_02)。

## 事前指定Read一覧
1. `er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/`: A_COMPLETION_CRITERIA_RECONSTRUCTION_01.md / A_IN_ONE_LINE_TIMELINE_01.md / A_ROOT_CAUSE_CANDIDATES_01.md / B_ARTIFACT_OBSERVATION_01.md / B_SEGMENT_PROVENANCE_01.csv(68行) 全文
2. `docs/pm/RESULT_PACKET_CFSA1A.md`・`CFSA1B.md` 全文
3. `OPEN_ITEMS.md`: Grep `OPEN-298|OPEN-299|OPEN-313|OPEN-316|OPEN-321|OPEN-350`
4. `CURRENT_SPEC.md`:2615-2630(P2/R2二重記述)
5. `er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md` 全文
6. 費用出典: `docs/pm/REPORT_LEDGER.md`:256-275、`er057_output/coffee_final_listening_tone_trial_01/`配下のcost記録。1 segment TTS+ASRの単価が出典から確定できなければ「未確認」。

## 追記位置・手順
- 01Aのマトリクス(46行+7行)の各行に、01Bの観測を突合して「実際の完成版」「判定」「原因(6分類)」「是正方針」を埋める。01Bに観測が無い行は「証拠不足(未確認: 何が無いか)」。
- 区分(正式採用済み/Coffee限定/VALIDATED未採用/個別指示/不採用・保留/完成後承認)と判定の交差集計表(件数)を作る。
- 「完成版への適用要否=必須」で「未反映/部分反映」の行を最優先で列挙。
- 成果物は同ディレクトリに`AUDIT_REPORT_01.md`と`SPEC_REFLECTION_MATRIX_01.md`(+`.csv`)を新規作成。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_02.md --json-out docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_02_check.json`
- git: `git status --porcelain -- er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01 docs/pm/delegation_log`、`git log --oneline -3`
有料API・runner・TTS・音声処理は一切実行しない。

## 成果物
- `SPEC_REFLECTION_MATRIX_01.md`(+同内容の`.csv`): ユーザー§4の10列を全行で埋めた完成版。各判定に証拠。末尾に交差集計表。
- `AUDIT_REPORT_01.md`: §0超サマリ(10行以内)/§1結論(Std/Adv別、区分1・2・4の必須行で判定、区分3は区別)/§2 Std/Adv別反映一覧/§3未反映・部分反映・証拠不足(優先度付き)/§4 In One Line根本原因(時系列、誰が何を見落としたか、「正式仕様未達」と「2文方針未反映」を分ける)/§5 KP・Voice Prompt等の反映証拠/§6是正内容と最小再生成範囲(費用は出典のある値のみ)/§7 PM・制作工程の問題(6分類、Day 2運営モデルとの関係は検討事項)/§8 QDC影響・費用見込み/§9未解決事項・ユーザー判断事項(選択肢・影響・推奨・理由。技術的に自明なものは「開発側で是正(承認不要)」)/§10 SSOT追記文案(書かない)/§11確認できなかった事項。

## SSOT追記文 / Git
SSOT追記文なし(文案は報告書§10のみ)。SSOT編集権なし。明示add: AUDIT_REPORT_01.md、SPEC_REFLECTION_MATRIX_01.md、SPEC_REFLECTION_MATRIX_01.csv、本ファイル(+_check.json)。`docs/pm/RESULT_PACKET_CFSA2.md`はgitignore対象なら強制addしない。コミットメッセージ: 「FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_02: 仕様反映マトリクス完成版(区分×判定)+監査報告書(結論・In One Line根本原因・Style/KP反映証拠・最小再生成範囲・工程問題・ユーザー判断)。Read-only、SSOT/Production無変更、JPY0」。push to origin/main。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_CFSA2.md`へ: (1)T-0 (2)§0超サマリ転記 (3)§1結論(Std/Adv) (4)交差集計表 (5)「必須」かつ「未反映/部分反映」の行一覧 (6)In One Line根本原因の1段落 (7)最小再生成範囲と前提 (8)ユーザー判断事項(推奨付き)と「開発側で是正」事項 (9)commit hash・push・raw URL (10)確認できなかった事項 (11)逸脱。Fableは§1・§4・§9とマトリクスの「必須×未反映」行を自分で照合する(受領≠受入)。

(注: 本保存版は事前指定Read/コマンド節を要旨化したが、ユーザー指示原文・Fable照合済み事実・成果物要件は逐語。)
