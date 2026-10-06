## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02c: 設計docの後半§6〜§12の執筆+RESULT_PACKET_DESIGN統合。前半§0〜§5[委任_02b]と反実仮想[委任_02a]は完了済み)。並行タスク: Opus前段スキャン(read-only、ファイル書込なし)。**git操作・SSOT編集・コード変更をしない。** 書き込み先: `docs/pm/design_open233_directional_misread_safety_01.md`(末尾へ§6〜§12追記)、`docs/pm/RESULT_PACKET_DESIGN.md`(新規、A/B統合)、`docs/pm/delegation_log/`。

**作業方式(必須・最重要)**: §ごとに別々のEditで追記(1回30行以内、箇条書き中心)。Bash heredoc不使用。思考・説明文は最小限。T-0の委任文保存はWriteを3分割して逐語保存。時間目安25分。

## 性質/到達上限Status/禁止事項

- 性質: Safety flow設計(¥0)。到達上限: 設計doc完成(DESIGN_READY_FOR_REVIEW候補)。採否はOpus条件Aレビュー(Part 2)後にFable/ユーザー。
- 禁止(ユーザー指定): 残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold変更/KPI変更/Human Reviewへの安易な振替/有料API/コード・prompt・runner変更/新Safety原則を「決定」として書くこと。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当(必須)。Part 1(信号喪失箇所・同型誤読)は並行実施中、Part 2(設計案評価)はFableが本doc完成後に依頼。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、要点)

> 報告内容: 今回見逃しの正確な原因/AIの揺れなのか、系統的な読み癖なのか/どのタイプを専門検査対象にすべきか/2〜3案の比較/今回HC-012と既存goldへの反実仮想結果/正常文への誤爆見込み/追加処理件数/追加費用見込み/推奨案/Opusレビュー/次の限定Trial案。
> ¥0で先に検証すること: 今回HC-012を捕捉できるか/既知goldを維持できるか/正常文を再び大量に重大化しないか/追加確認へ送る件数がどの程度になるか、を比較する。
> Opusレビュー: 同一モデルの相関誤りを本当に減らせるか/方向反転以外にも同型のsystematic misreadがないか/過剰Safetyへ逆戻りしないか/既存Checker信号を捨てている他の箇所がないか。
> Status: 到達してよいのは DESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED まで。

## 反実仮想の確定数値(§6へ転記、再集計不要)

新9 run(16 cycle・123件): T-A 43件(4.78/run)、T-B 43、T-C 55(6.11/run)。ラベル内訳(重大/軽微/問題なし/UNDECIDABLE): T-A・T-B=1/0/42/0、T-C=1/3/51/0。HC-012は3案ともtrigger(`sub_reasons=negation_polarity_mismatch`、llm/final=ACCEPTABLE)。新9 runの重大4件中triggerはHC-012のみ(B3/HC-011/HF-009はAIがBLOCKING済み・`sub_reasons=model`で非trigger=影響なし)。旧9 run(25 cycle・326件): T-A 52(5.78/run)、T-B 52、T-C 105(11.67/run)。旧35件の正当6件のtrigger 0。旧floor誤爆24件のtrigger: T-A 0/T-B 0/T-C 8、判断不能5件はT-Cで3。段階A(42 run・候補658): T-C語彙該当183、決定論由来候補155。段階A SC gold: T-C該当はB3とA5-0(各3 run)、A2A3-0/A4-0/B4-a/B3-same@neg5は0。決定論由来候補はA4-0のみ2 run。近似: T-Bは「`sub_reasons`に`model`が無い」で近似(T-Aと同数)、T-CはLedger本文がjsonに無いためclaim_textのみ適用。

## KPI provenance欄

反実仮想=frozen/reuse、決定論的集計【確認】(`er052_output/open233_directional_misread_offline_01/trigger_replay_01.md`)。専用確認の捕捉可否=分析的評価【推測】(LLM未実行)。費用見込み=Stage 2単価と入力token概算からの推計【推測】。

## Opus台帳更新

該当なし(Part 2後にFableが記録)。

## 事前指定Read一覧

1. `docs/pm/design_open233_directional_misread_safety_01.md`: 全文(140行、§0〜§5。整合させる)。
2. `docs/pm/RESULT_PACKET_DESIGN_A.md`・`docs/pm/RESULT_PACKET_DESIGN_B.md`: 全文(統合用)。
3. `er052_output/open233_directional_misread_offline_01/trigger_replay_01.md`: 全文(表の転記元)。
4. Stage 2単価の根拠: `er052_output/open233_prod_e2e_02/report_final/report_abcde.md` Grep `後段判定|¥|cost` →後段判定費用(¥7.29/9 run、123判定)から1判定あたり単価を算出。
5. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `重大誤解原則` →§0段落本文(委任_02bが未Readのため、§0要約との逐語照合を本委任で行い、相違があれば§1を訂正)。

## 事前指定Grep一覧+追記位置・更新位置の手順

設計doc末尾へ§ごとにEdit追記(各30行以内):
- §6 反実仮想結果: 上記確定数値を表(案別trigger件数/run、ラベル内訳、HC-012捕捉、gold影響、旧誤爆24件のtrigger、段階A)。所見: trigger精度(真に重大/trigger)は約2%だが、専用確認は軽量call・強制重大化なしのため不要Rewriteは増えない(専用確認が正しく「一致」と返す前提)。T-CはT-Aより対象広く誤爆24件のうち8件もtrigger(処理増)。近似の限界(T-B近似、Ledger本文なし)を明記。
- §7 追加費用見込み: 専用確認1 call=入力(該当fact+notes+該当文+前後1文≒400〜800 tok)+出力(schema固定≒100 tok)、Stage 2単価(§4の算出値)比で1/3〜1/2と仮定→T-Aで約4.8 call/run×単価=¥/run、9 runで¥、low/mid/high。別model(例: Stage 2と別系統)を使う場合の単価差は「未測定、Trialで実測」。
- §8 推奨案(Sonnet所見、決定ではない): §3比較と§6/§7から1案(案D=前段で信号保持[案C]+決定論センサーtrigger[T-A/T-B]→方向反転専用の独立確認[案A]、曖昧は別model再確認→なお曖昧ならQUALITY)。理由(Safety: HC-012捕捉・gold非影響/独立性: 別prompt+限定入力(+別model)/誤爆: 強制重大化なし/費用: 約5 call/run)。採用しない案の理由。
- §9 次の限定Trial案: 段階0(¥0、完了=本replay)→段階1(有料): 保存候補に専用確認を実測。対象: HC-012(1)、段階AのA5-0候補(3)、新9 runのT-A trigger 43件(真に重大1・問題なし42=誤反転判定率の測定)、旧floor誤爆24件のうちT-C該当8件、委任_61の方向反転再現ケース。費用概算(件数×単価、low/mid/high)、測定項目案(HC-012捕捉/A5-0 3/3/問題なし42件の「一致」率/曖昧率、新KPIではない)、STOP条件案(HC-012非捕捉/問題なしの逆転誤判定が多数/曖昧多数)。段階2=Production配線設計(条件A・C)。
- §10 Opus条件Aレビュー論点: ユーザー指定4点+Fable追加(S1との関係[置換か併用か]、決定論検査の粗さ[英語否定語×日本語否定マーカー近似]をセンサーとして使う妥当性と偽陰性、trigger精度2%の処理負荷、Recheck/出口/retry/regenでの専用確認の再実行要否、専用確認の失敗時fail-closed)。
- §11 Existing Spec/Prior Trial Check(A/B/C): 旧time verify(別prompt・2回確認方式の前例、委任_61で比較の方向反転を誤解放=B)、cite-to-fire(反実仮想記録あり=B)、S1(Stage 2承認構成の一部=A)、Stage 2 V3 rubric修正(A)、決定論検査(A)。本設計=C(新規: センサー→専用独立確認)。Dangling Reference: 参照する関数・フィールド名(`sub_reasons`、`negation_polarity_mismatch`、`cycle_record`、`second_opinion`等)の実在をGrep確認(行番号)。
- §12 STOP条件該当判定: 新Safety原則の追加(=「決定論検査をセンサーとして専用確認を起動」は新構造だが重大誤解原則の運用手段であり原則追加ではない【推測】、ユーザー確認事項)/gold変更(不要)/有料Trial(段階1で必要→ユーザー承認事項)/Production変更(段階2で必要→承認事項)。到達Status案: DESIGN_READY_FOR_REVIEW(Opus Part 2後にFable判定)。
- `docs/pm/RESULT_PACKET_DESIGN.md`: A/Bの内容を統合し、ユーザー指定11項目(原因/揺れvs系統/対象タイプ/案比較/反実仮想/誤爆見込み/追加処理件数/追加費用/推奨/Opus[Part 1・2はFableが追記]/限定Trial案)を各3行以内で要約+SSOT追記文案(OPEN_ITEMS進捗・REPORT §82案・DECISION_LOG案)+成果物一覧(commit対象)+一覧外Read理由。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02c.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02c.md_check.json`
2. 設計doc §6〜§12を順にEdit追記。
3. RESULT_PACKET_DESIGN作成。
4. git操作なし。

## SSOT追記文

なし(文案のみRESULT_PACKET_DESIGNへ)。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DESIGN.md`へ上記。最終報告は10行以内。

