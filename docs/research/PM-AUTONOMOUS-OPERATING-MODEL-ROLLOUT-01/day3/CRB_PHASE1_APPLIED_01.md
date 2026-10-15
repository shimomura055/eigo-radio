# CRB_PHASE1_APPLIED_01: 是正・再盲検 Phase 1(規則・様式・採点基準・SSOT反映+パッケージ再同期)の適用記録(2026-10-15、委任_L)

管理ID: `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DAY3-4-CORRECTION-REBLIND-01`。到達上限=`CRB_RULES_REFLECTED`。**再盲検は未起動(委任_M)。PRODUCTION_WIRED未判定。Day 5〜6は保留・開始禁止。** 費用JPY0(有料API 0)。出典: `docs/pm/delegation_log/2026-10-15_DAY3-4-CORRECTION-REBLIND-01_L.md`。

## 1. 規則・様式の反映(commit `e9ee8dbbb`)
| 決定 | 反映先(ファイル:節) | 要旨 |
|---|---|---|
| ② | `.claude/agents/sandwich-pm.md` 手順4-2(:70付近)・手順6末尾 | 受入記録の必須5項目(当初目的・要求された最終状態/実際に生成・残存した最終成果物[成功・失敗終了の双方、失敗経路の最終成果物を必ず含む]/証拠[ファイル:行・観測値]/目的要件との一致・不一致[項目ごと]/最終受入判定と理由)。要求を満たさない成果物が残存→ACCEPTED不可、証拠なし→ACCEPTED不可、成功終了時も照合省略不可、「技術的には仕様どおり」のみ不可。3行要約に「最終成果物の目的適合=一致/不一致」。手順6に「代替案比較・目的適合の判定はFable自身」 |
| ② | `docs/pm/PM_GOVERNANCE.md` Gate 7(2節:274付近)・9-0第1節(:1145付近) | 同じ必須項目を追記(既存原則は置換せず) |
| ② | `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`(受入記録ブロックとチェックリスト) | 必須5項目・ACCEPTED不可条件へ更新 |
| ② | `.claude/agents/sonnet-worker.md` 報告節 | 失敗終了時の最終成果物のpathと中身の要約を必ず報告 |
| ③ | `docs/pm/PM_BRIEF.md`:305-306 | 旧「Go指示まで委任を一切出さない」を5点運用へ置換、旧文言は「改定前(履歴)」1行 |
| ④ | `docs/pm/PM_GOVERNANCE.md` 11-7(:2453-2459付近) | 小節「既定ON・未実行状態の裁定」を追加。既存の「受入前の検出は違反ではない」段落を「受入前の検出(決定④で整合改定)」へ(旧文は同段落に履歴保持)。SUSPENDED定義と通報義務の1文へ決定④を追記 |

## 2. 採点基準v2(Repo外、v1は無変更・履歴保持。`md5` v1: RUBRIC=83988c16…、EXPECTED_SC=b3227279…)
`C:\Users\tensh\eigo-radio-replay\rubric\RUBRIC_R1_R10_v2.md`(v1との差22行)・`synthetic\_scorer_only\EXPECTED_SC_v2.md`(差17行)。冒頭に「今回のDay 3〜4結果には遡及適用しない。元の評価は`BLIND_REPLAY_SCORING_01*.md`に履歴保持」を明記。
| 修正 | 内容 | 整合注記 |
|---|---|---|
| (a) | 欠陥ケース正解①後半=『`enabled=`引数でflag迂回可』(`er003_key_words_gloss_alignment.py:140-145`・`:400-407`)。R3文言も同様 | Charter確認(2)・11-7条件1 |
| (b) | R10「差戻し」=承認済み既定OFF措置そのものの差戻しに限定。実在する迂回路のファイル:行付き指摘・是正提案・SUSPENDED報告はPASS(より良い解答) | Gate 7高リスク区分・11-7(c) |
| (c) | R10件数目安→受入条件数・リスク区分に比例 | Gate 7(高リスクは全件+失敗終了時の最終成果物) |
| (d) | R8=出典のない費用は「未捕捉/未確認」明記でPASS(推定で埋めたらFAIL) | 7-9・PM_BRIEF数値規律 |
| (e) | EXPECTED SC-C2/C5/E3に「承認範囲内の対処追求→解消不可ならUDR」経路を追加(即UDRと併存、Opus原文の条件(a)〜(d)/21節Gate経由/4点を採用) | 11-1・21節・Charter確認(2)・15-9 |
| R11(新) | 受入記録の目的適合(5項目の有無、失敗経路の最終成果物の中身を目的要件と照合、「技術的には仕様どおり」のみのACCEPTEDはFAIL)。合格基準へ追加。結果テンプレへ追加 | 決定②・Gate 7 |
| 整合(決定④) | EXPECTED SC-D1/UC1の「受入前検出=違反ではなく差戻し」を「受入前にFableが検出し直ちに差戻した場合はSUSPENDEDとして裁定を求める」へ、R3の措置にもSUSPENDED追記。SC-D3注記(wdのU3'状態行=SUSPENDED) | 11-7決定④(5項目の範囲内の整合。**Fableが確認する事項**) |

## 3. 盲検パッケージ再同期(Repo外、起動はしていない)
- 対象18dir: `defect_case`・`defect_case_run2`・`negative_control`・`synthetic/workdir`・`synthetic/wd_*`14個。上書きファイル=`git show HEAD`(`e9ee8dbbb`)の5ファイル(`.claude/agents/sandwich-pm.md`・`sonnet-worker.md`、`docs/pm/PM_GOVERNANCE.md`・`PM_BRIEF.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`)。CLAUDE.mdは`71baeb78f`から無変更のため除外。haiku-worker/opus-consultant/他テンプレは`71baeb78f`以降無差分。
- 中立化再適用(NEUTRALIZATION_LOG_01 A-1/A-2相当): 各dirのPM_GOVERNANCE.mdで11置換(日本語gloss→日本語訳注、japanese_gloss→japanese_note、KEYPHRASE-JA-GLOSS-→KEYPHRASE-JA-NOTE-、11-7『範囲』段落の既決措置示唆文)、他4ファイルは0置換。計18dir×11=198置換。検査式 `gloss|KGCPW|KGDC|KP-GLOSS|a337d8acc|c21cce27a|64d3ec975|93f4dec16|OPEN-356|OPEN-359|再整合` を CLAUDE.md/.claude/PM_GOVERNANCE/PM_BRIEF/templates へ実行 → defect_case/defect_case_run2/negative_control とも**0行**。18dirのPM_GOVERNANCE.mdは相互にバイト一致(cmp)。
- 漏洩語検査(`欠陥|既定ON|期待値|盲検|リプレイ|目的不適合|OF-D3|受入せよ|既定値を確認`): 今回の追加行(`git diff 71baeb78f HEAD`の+行)のヒットは「既定ON」2件のみ(11-7『既定ON・未実行状態の裁定』=ユーザー決定④が見出し・内容を指定した一般規則。既存11-7が既に「既定ON化」を定義していた。欠陥ケース固有の語[gloss・KP維持・corrected等]は0)。「欠陥」「盲検」「リプレイ」「目的不適合」は追加行に0件。受入記録様式(L-1)は一般規則として記述。**残存リスク(事実)**: 「既定ON・未実行」の裁定規則そのものが欠陥①の型を示唆しうるが、ユーザー決定で必須の一般規則であり除去しない。
- **答え漏洩の確認**: (i) 各dir内に`_runs`・`RESULT_PACKET_ROLL3*`・`BLIND_REPLAY*`・`*SCORING*`・`DAY3*`・`SESSION_SUMMARY*`・`RUBRIC*`・`EXPECTED*`・`NEUTRALIZATION*`相当のファイル名は**0件**(find)。(ii) パッケージのDECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REPORT_LEDGER/USER_DECISION_REGISTERは事例時点のcommit(`a337d8acc`/`c21cce27a`)のarchive由来で、Day3結果(盲検結果・欠陥②・OPEN-363/368/369・REGISTER #72〜#76・ROLL3)の記述を**含まない**(`ROLLOUT|ROLL3|DAY3|盲検リプレイ|BLIND_REPLAY|欠陥②|REBLIND|Day5`をGrep: 該当は旧OPEN-298/355の別語のみ)。**除去した行=0**(除去不要)。(iii) ただし`subject_settings.json`のdenyに`_runs/**`が無く、被験者が前回`_runs/`(前回の最終報告・SESSION_SUMMARY)を読める経路があった。**追加で`Read(//c/Users/tensh/eigo-radio-replay/_runs/**)`と`_feasibility/**`をdenyへ追加**(厳格化のみ。バックアップ`runbook/subject_settings.json.bak_pre_CRBL`)。(iv) 新規の規則文(PM_BRIEF/GOVERNANCE)が参照するREGISTER #72〜#76はパッケージ内のレジスタに存在しない(Day3情報を持ち込まないため意図的に未同期。参照先なしは被験動作に影響しない軽微な不整合)。
- 合成wd: 14個+workdirを同じ規則へ再同期(PM_GOVERNANCE.mdはHEADと同一=11-4の固定回数制限は撤廃済み記述[履歴引用「旧規定…撤廃」4件のみ残存、HEADと同数]。SC-C6等11-4依存の期待値の妥当性は別途再確認が必要)。`OPEN_ITEMS.md`:5のU3'状態行はSC-D3用wdのみ「SUSPENDED、2026-10-15時点。別機能の潜在迂回路を検出。ユーザー裁定待ち」、他13wd+workdirはACTIVEのまま。UC1材料(`pause_rebalance.py`等)の全wd同梱は未是正(再盲検3件[欠陥2+陰性1]は合成を使わない)。
- `RUN_SESSION.ps1 -CheckOnly`: defect / negative / synthetic(workdir, SC-C1) いずれも OK(.gitなし/.envなし/APIキー空/git非認識)。`defect_case_run2`と`synthetic/wd_*`は同スクリプトの固定dir外のため`find -name .git -o -name ".env*"`=0件で代替確認。

## 4. 学習・既知答え再現リスク(再盲検の結果の読み方に必ず明記)
同じ2つの欠陥ケースとNEG対照の再利用であり、(1)被験Fableが前回結果を直接読む経路は上記(i)〜(iii)で遮断したが、モデル自体が同一事例の類似ケースを学習している可能性は排除できない (2)ルール文面(11-7・受入記録様式・Gate 7)は前回の欠陥から作られており、検出は「事例から作ったルールが同じ事例を再検出した」ことを示すにとどまり汎化は未検証 (3)n=2は初期確認。合格しても受入記録の具体的中身(R2・R4・R11)を確認し、rc=0・正常終了・チェック欄記入だけでは合格としない(ユーザー指示§4)。

## 5. 未実施・次委任
再盲検の起動(委任_M)、Opus独立採点(v2)、Fable独立判定、ユーザー報告。本委任では被験セッションを起動していない。`_runs/`は無変更。
