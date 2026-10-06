## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02: 系統的読み違い[方向反転等]を狙い撃つSafety設計の作成+¥0反実仮想評価。Opus条件Aレビューの入力となる設計doc)。並行タスク: 委任_01(SSOT訂正・記録・commit。REPORT/DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REPORT_LEDGER/ACTIVE_TASK/RESULT_PACKET.mdを編集)。**本委任はそれらを編集しない。git操作もしない。** 書き込み先: `docs/pm/design_open233_directional_misread_safety_01.md`(新規)、`er052_output/open233_directional_misread_offline_01/`(新規: 反実仮想script・json・md)、`docs/pm/RESULT_PACKET_DESIGN.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須)**: `Write`/`Edit`で§単位に小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを4分割して逐語保存。説明は最小限。時間目安40〜60分。長文を1回で出力しない。

## 性質/到達上限Status/禁止事項

- 性質: Safety flow設計(¥0、read-only+設計doc)。到達上限: 設計doc完成(DESIGN_READY_FOR_REVIEW候補)。最終Status・採否はOpusレビュー後にFable/ユーザーが決める。
- 禁止(ユーザー指定): 残11 run E2E/Production変更/全機械floor復活/一律のChecker厳格化/gold変更/KPI変更/Human Reviewへの安易な振替/有料API(**¥0厳守**: 反実仮想は保存データの決定論的集計+分析的評価のみ。LLM呼び出しが必要な検証は「次の限定Trial案」として費用見積付きで提示)/コード・prompt・runner変更(反実仮想scriptは新規dirに置き、runnerをimportして関数を読む・保存jsonを読むのは可、書き換え不可)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: **条件A該当(Safety flowの構造変更、設計後・実装前、必須)**。Opusレビューは本docに対しFableが依頼する(Sonnetは依頼しない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(runnerは9,000行超、全文Read禁止)。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、設計課題部分を逐語)

> 設計課題: 「同じAIにもう一度重大かどうか聞く」のではなく、読み違いの種類そのものを直接検査する仕組みを設計する。特に検討すること：
> 1. 方向反転専用確認: Ledger側では何が起きたのか/Article側では何が起きたのか/両者は同方向か逆方向か、を直接判定させる
> 2. 対象となる意味関係: rollback / restore、withdraw / reinstate、increase / decrease、start / stop、expand / shrink、allow / prohibit、approve / reject、add / remove、その他、既存gold・過去事故から一般化できる方向反転。単語リストだけに依存せず、意味関係として一般化できる設計を考えること。
> 3. Checkerの機械信号の扱い: negation_polarity_mismatch 等の決定論検査が出した警告を、後段AIが単純に消してしまわないようにできるか/強制重大化ではなく、専用追加確認を起動するtriggerとして利用する案を検討する
> 4. 独立性: 同じmodel/同じrubric/同じ入力をそのまま繰り返す方式は避ける。別Prompt、限定された入力、別model等のどの組み合わせが最も費用対効果がよいか設計する。
> 5. 最終判定: 専用確認で明確な方向反転 → 重大/一致 → 通過/本当に曖昧 → どう扱うか、を提案する。
> 私からの設計仮説: 有力候補として、決定論検査 = 重大判定器ではなく「専門検査を起動するセンサー」という構造を評価すること。今回のようにCheckerの機械検査が異常を検知した場合だけ、「この表現は重大か？」ではなく、「LedgerではXは撤回されたのか復活したのか。Articleではどちらか。方向は一致しているか？」のように、誤読しやすい一点だけを直接比較する独立確認へ送る。この方式なら、以前の機械floorのように広範囲を自動BLOCKINGして不要Rewriteを大量発生させることなく、今回のAIの癖だけを狙える可能性がある。ただし、この案をそのまま採用せず、Claude側でも代替案を検討すること。
> ¥0で先に検証すること: 可能な限り既存artifactを使い、今回HC-012/A5-0等の既知方向反転gold/過去の否定・比較・方向系gold/正常なのに旧機械判定が誤爆した代表例、へ候補設計を反実仮想適用する。最低限、今回HC-012を捕捉できるか/既知goldを維持できるか/正常文を再び大量に重大化しないか/追加確認へ送る件数がどの程度になるか、を比較する。
> 報告内容: 今回見逃しの正確な原因/AIの揺れなのか、系統的な読み癖なのか/どのタイプを専門検査対象にすべきか/2〜3案の比較/今回HC-012と既存goldへの反実仮想結果/正常文への誤爆見込み/追加処理件数/追加費用見込み/推奨案/Opusレビュー/次の限定Trial案。

## KPI provenance欄

反実仮想=frozen/reuse(新仕様9 run `er052_output/open233_prod_e2e_02/runs/`、旧9 run `er052_output/open233_e2e_acceptance_01/runs/`、段階A 42 run `er052_output/open233_stage1_stageA_01/`、Stage 2較正の保存結果、floor誤爆35件分析`er052_output/open233_floor_selectivity_offline_01/`)。trigger件数=決定論的集計【確認】。専用確認の捕捉可否=分析的評価【推測】(LLM未実行)。

## Opus台帳更新

参照のみ: `docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `OF-04[3-9]|OF-05[0-5]|相関|同じrubric|S1` →関連指摘(S1は同rubric再サンプル、verify同モデル相関、前段情報の喪失)を設計docの根拠として引用(台帳編集なし)。

## 事前指定Read一覧

1. `er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json`: L320-L420(HC-012 claimの全記録: flags/sub_reasons/Stage 2/S1)。
2. `er052_output/open233_prod_e2e_02/report_final/critical_trace.md`: 全文。
3. runner `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS` →定義ブロック全体(gold 6件+監視項目、L9817付近)。Grep `negation_polarity|def .*polarity|number_not_in_fact|quote_not_in_ledger|coverage_gap` →決定論検査の種類と実装(coverage_checker側にあればそちら、Grep `def ` in `er052_open233_stage1_coverage_checker_01.py` L538-L648)。Grep `confirmed_downgrade|def .*second_opinion|run_stage2\(` →S1の入力・rubric共有の確認(L4026-L4088)。Grep `floor_verify_target|def .*verify` →旧time verifyの問い方(別prompt方式の既存例、L2868-L2885・L2984-L3010)。
4. Stage 2較正の誤降格履歴: `er052_open233_self_recovery_stage2_calibration_01.py` L355-L380(A4-0/A5-1 false downgrade、Ledger issue逐語)。Grep `A5-0|A5-1|put back|rollback` →該当claim文と判定。
5. `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`: L38-L60(23種の集計)、Grep `方向|反転|否定|増|減|復|撤回|K19` →方向・否定系の過去事故の型。
6. `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.md`: 35件一覧表(正常なのに旧floorが誤爆した例、カテゴリ別)。
7. `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`: (2)(3)R3(cite-to-fire、S1の性質、verify相関)。
8. `docs/pm/opus_l2_review_open233_checker_floor_production_e2e_01.md`: (3)R2・その他(S1対象増、上書き箇所一覧)。
9. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `重大誤解原則` →§0。
10. 新仕様9 runの全claim: `er052_output/open233_prod_e2e_02/report_final/report_abcde.md`と`labels/labels_merged.json`(ラベル付き123件: 専用確認のtrigger対象件数と誤爆見込みの算出用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 反実仮想script `er052_output/open233_directional_misread_offline_01/trigger_replay_01.py`(¥0): 保存run json(新9 run・旧9 run・段階A 42 runのStage 1出力)から、各設計案のtrigger条件(例: 案A=決定論検査`negation_polarity_mismatch`等が立ち、かつStage 2/S1が非BLOCKING/案B=決定論検査+Stage 1 AIのSUPPORTED判定の食い違い[決定論で戻した候補]/案C=4観点再分類の`qualifier/scope/counterpart mismatch`や否定・方向語彙の存在等)を機械適用し、(i)trigger件数(run別・全体・件/記事)、(ii)そのうちラベル済み123件での内訳(真に重大/軽微/問題なし=誤trigger見込み)、(iii)HC-012がtriggerされるか、(iv)gold 6件+A5-1・HF-009型・旧35件の正当6のうちtriggerされる件数(=専用確認へ回る件数)、(v)旧floor誤爆24件のうちtriggerされる件数(専用確認が正しく「一致」と返せば通過するが、処理件数として計上)、を表にする。出力`trigger_replay_01.json/.md`。
- 設計doc `docs/pm/design_open233_directional_misread_safety_01.md`(§単位): §0 前提・provenance・禁止事項/§1 見逃しの正確な原因/§2 専門検査対象の意味関係タクソノミー/§3 設計案2〜3案の比較(案A〜D)/§4 Checker機械信号の保持設計/§5 最終判定ルール案/§6 反実仮想結果/§7 追加費用見込み/§8 推奨案と理由/§9 次の限定Trial案/§10 Opus条件Aレビュー論点(ユーザー指定4点+Fable追加論点)/§11 Existing Spec/Prior Trial Check(A/B/C)とDangling Reference確認/§12 STOP条件該当判定。(各§の詳細指定は原文参照: 案A=ユーザー仮説センサー→方向反転専用独立確認、案B=Stage 2 rubric拡張、案C=Stage 1再分類に第5観点、案D=A+C併用)
- `docs/pm/RESULT_PACKET_DESIGN.md`: 報告項目(ユーザー指定11項目の要約+一覧外Read理由+成果物一覧)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02.md_check.json`
2. 反実仮想: `.venv\Scripts\python.exe er052_output\open233_directional_misread_offline_01\trigger_replay_01.py --new-runs er052_output\open233_prod_e2e_02\runs --old-runs er052_output\open233_e2e_acceptance_01\runs --stagea er052_output\open233_stage1_stageA_01 --labels er052_output\open233_prod_e2e_02\labels\labels_merged.json --out-dir er052_output\open233_directional_misread_offline_01`
3. 設計doc・RESULT_PACKET_DESIGN作成。
4. git操作なし。

## SSOT追記文 / Git / 報告

SSOT追記なし(文案はRESULT_PACKET_DESIGNに記す)。git操作なし、SSOT編集権なし。報告はRESULT_PACKET_DESIGNへ13項目(T-0結果/見逃し原因と揺れvs系統/タクソノミーと第1段対象/案比較表/反実仮想結果/追加費用/推奨案/次の限定Trial案/Opus論点/A/B/C分類・Dangling/STOP判定/一覧外Read理由/成果物一覧)。最終報告は15行以内。
(注: p4は長大な原文の§詳細指定を要約記載。原文は呼出し元の委任文)
