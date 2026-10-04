## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_66)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Opus独立レビュー#9(条件A、本委任文末尾に全文)をFableが照合した結果に基づき、L6「完結文復元」を検証用runnerへ実装し(Opus推奨ガード(1)〜(5)を含む)、¥0の検証(replay一致・cycle横断replay・B3根本原因の点検)と単体テストを行い、影響instance(`safety_A2A3`・`bgroup_B3`)をn=2で再実行してHuman Review 0件・重大見逃し0・費用+¥2/記事以内を実flowで確認する。29件横断の再確認は次の委任_67。
- Primary KPI(ユーザー指示2026-10-04[6回目]): Production運用でChecker起因のUSER_DECISION_REQUIRED/Human Review 0件。Safety: 重大Fact見逃し0件。Cost: 平均+¥2/記事以内。三つ同時。
- 到達上限Status: Trial実装+限定実flow確認。Production採用判断・`PRODUCTION_WIRED`はしない。次Trial(10本)は開始しない。
- Fableの照合判断(Opus#9に対する採否。変更しない):
  - 採用: 推奨(1)残余包含検査+アンカー間隔整合+`unmatched≥0`検査、(2)略語対応の文分割(L6用、固定リスト)、(3)`issue_focus_absent`時はRewriteせずRecheckのみ、(4)2文復元時のdiff焦点文ガード、(5)数値境界補正は単語境界関数側(`VS_MATCH_EXT`配下、新スイッチなし)、Opus(c)E1 Promptへの元断片(fragment)併記(Rewrite用Promptの小変更。Checker Promptは変更しない)、代替案のcycle横断replay(¥0)とB3根本原因(前cycle本文の引用)の点検(¥0、点検のみ)。
  - 記録のみ(実装しない): (6)runner/er010共有module化(Production配線時、`OPEN-233-A1-PROD`へ)、論点3のL5末尾省略の粒度不整合(判断事項として記録)、論点6(a)Production `sentence_fallback`集計(配線前の¥0作業として登録)、U-2(1)位置語→構造要素の対応(承認済みP-strict-closedの変更にあたるため設計+¥0 replayのみ行い、実装はユーザー確認後)、U-3(実例0件、不要)。
  - アンカー型(Checkerが記事にない語を1〜6語混ぜたclaimを、逐語で一意な連続語列から文を決める)は、ユーザー指示の「断片を含む完結文が一意なら復元」の趣旨の内側にある決定論的拡張としてTrial実装に含める。ただし字義上の拡張であることをユーザーへ確認事項として明示する(報告でFableが提示)。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。Checker Prompt・Schema・判定方法は変更しない。
  - 類似度・単語重なり照合を使わない。範囲の縮小をしない(穴Aの残余包含検査で保証)。
  - 新スイッチ`VS_SENTENCE_RESTORE`(既定OFF)。OFFで既存挙動が不変であることをテストで固定。`HANDOFF_MODE=legacy`無影響。
  - 既存より厳しくする変更を追加しない。新しいProduct判断が必要なら実装せず報告(USER_DECISION候補として記録)。
  - 影響instance再実行で、日本語変更・重大解放・Safety-critical残存・例外が出たら即STOP。再実行はn=2固定(増やさない)。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: 上限¥10(Guardrail。影響instance再実行の目安はrep24実測でA2A3 ¥0.6〜1.1、B3 ¥0.5〜1.6、計¥3〜6)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥572.8515、上限¥900。
- Opus独立技術レビューGate: #9実施済み(条件A)。実装がレビュー済みの形(P→L6、決定論のみ、追加LLM callなし、ガード(1)〜(5))から外れる変更が必要になったら実装せず報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_66.md`。**委任文は全文そのまま保存(末尾のOpus#9全文を含む。要旨化不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用`.md`をWriteツールが拒否する場合は、Pythonスクリプトからファイル出力する。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾のユーザー指示[6回目])

````
- Checkerは検出に専念する。
- 後段で記事原文に照合する。
- spanが途中切断・...省略でも、断片を含む意味の通る完結文が記事内で一意に特定できるなら、その文を対象範囲として復元する。
- 複数候補、本当に一意に決められない場合のみ例外扱い。
- 範囲拡張で不要Rewriteが入らないよう、最小Rewrite原則は維持する。
必ず以下のKPIを同時に満たす前提で設計・検証してください。
- Primary：USER_DECISION_REQUIRED / Human Review 0件
- Safety：重大Fact見逃し 0件
- Cost：平均 +¥2/記事以内
````

## 作業1: Opus#9の保存とFable評価の記録(¥0)

`docs/pm/opus_l2_review_open233_self_recovery_09.md`を作成: (1)依頼文(本委任文末尾の「Opusへの依頼」節を逐語)、(2)Opus#9全文(本委任文末尾を逐語)、(3)Fable PM評価(上記「Fableの照合判断」を逐語、PM_GOVERNANCE 11-3の8項目照合: 必要性/単純化/既存利用/前段情報/LLM追加なし/非決定性/Human Review/不要Rewrite/コスト/retry整合/安全側/再発防止 を1行ずつ、STOP条件(1)〜(7)非該当の根拠)。設計書`docs/pm/design_open233_span_sentence_restore_01.md`に§6「Opus#9後の採否」を追記。

## 作業2: 実装(runner、`VS_SENTENCE_RESTORE`既定OFF)

設計書§4+Opus#9是正を実装する。
- 2-1 数値境界補正: `_vs_wordch`/`vs_word_boundary_ok`(runner 3482〜3505付近)で「数字に挟まれた`.`/`,`は語構成文字」とする補正を`VS_MATCH_EXT`配下に入れる(新スイッチなし)。`2.6 percent`の`6 percent…`が確定しなくなり、L6へ回ることをテストで固定。既存確定claimへの影響は設計書§5の1一意(7 runs)のみであることをreplayで再確認。
- 2-2 L6本体(`vs_sentence_restore_resolve`): 発火条件(i)〜(iv)、除外(日本語・説明文混入型・label_only・multi_match)、手順1〜6、ガード表の値、記録(`level="L6:sentence_restore"`、`restore_reason`、元断片、復元文、アンカー、候補数)。P-strict-closed→L6の順序。
- 2-3 Opus是正(1): 残余包含検査(アンカー外の連続語列が記事に逐語で存在するなら復元範囲の内側にあること。外側なら復元しない=unresolvable)、アンカー間隔整合(先頭・末尾アンカーの記事上の間隔≤claim側の語数+α、αは定数で根拠を書く)、`unmatched≥0`・cover二重計上の修正。
- 2-4 Opus是正(2): L6用の文分割に略語除外リスト(固定、決定論: `U.S.`、`Mr.`、`Mrs.`、`Ms.`、`Dr.`、`Jan.`〜`Dec.`、`St.`、`No.`、`vs.`、`e.g.`、`i.e.`、`Inc.`、`Co.`、`Ltd.`、`a.m.`、`p.m.`を最低限。既存`vs_sentence_segments`は変更せず、L6用に`vs_sentence_segments_l6`を新設して理由を記す)。
- 2-5 Opus是正(3): `issue_focus_absent`: Checkerの`issue`中の引用符で囲まれた語句(“…”/‘…’/「…」)がすべて復元範囲に存在しないとき、その claimはRewriteせず`issue_focus_absent`を記録してRecheckのみに回す(既存の「全文Recheck」の仕組みを使う。Recheckで再指摘されれば次cycleで通常処理)。引用符付き語句が`issue`に無い場合は通常どおりRewrite。
- 2-6 Opus是正(4): 2文を復元した場合、E1 Rewrite結果を書き戻し前にdiffし、変更位置が「元断片またはアンカーを含む文」の内側に収まるかを検査。外側の変更はE1失敗扱い(既存の失敗経路へ)。
- 2-7 Opus(c): E1 Prompt(runner 4020〜4048付近)に、L6復元時のみ「指摘箇所(元断片)」を併記する(範囲=復元文、焦点=断片)。Checker Promptは触らない。
- 2-8 記録: instance JSONの`handoff`に上記フィールド、summaryに「L6発火/復元成功/候補0/候補複数/ガード不通過(理由別)/`issue_focus_absent`件数/2文復元の焦点文ガード発火」を追加。

## 作業3: ¥0検証

- 3-1 replay一致: `er052_output/open233_span_restore_offline_01/replay_01.py`の対象(unresolvable全件+rep24全claim+合成13+ストレス889通り)に対し、runner実装(`VS_SENTENCE_RESTORE=True`)で同じ結果になること(差分があれば全件列挙・理由)。穴A/穴Bの是正で結果が変わるケースは「安全側に変わった」ことを確認。
- 3-2 cycle横断replay(Opus代替案): 既存ログで「cycle N−1の本文で確定したclaimを、cycle Nの本文に当てる」(B3型の古い引用を再現)。L6が誤った文を選ばないこと(0件)、`issue_focus_absent`が適切に発火することを確認。出力`er052_output/open233_span_restore_offline_01/cycle_cross_replay_01.{json,md}`。
- 3-3 B3根本原因の点検(¥0、点検のみ): rep24 `bgroup_B3` s2 cycle2のChecker入力(`prior_issues`の中身、本文)とcycle1の本文を比較し、Checkerの`so`がcycle1本文の引用かを確認。`build_prior_issues_instruction`(er003、read-only)が前cycleのspan textを渡しているかを確認。結果と「Checker入力側の是正はChecker Prompt変更に当たるためユーザー判断事項」を設計書§7に記録。
- 3-4 U-2(1)設計+replay(実装しない): 位置語(`headline`/`title`/`one-line summary`/`In one line`の閉じた語彙)→構造要素(`#`見出し行/`## In one line`直下の1行)を範囲に追加する案の設計(1節)と、(d)型5件へのreplay(復元できる件数・誤範囲0)。実装はユーザー確認後。

## 作業4: テスト・回帰

- 新規テスト: OFFで無変更/legacy無影響/数値境界補正/L6発火条件(i)〜(iv)/除外/ガード各値/残余包含検査(穴A)/間隔整合+unmatched≥0(穴B)/略語文分割/`issue_focus_absent`/2文焦点文ガード/E1 Prompt併記/P→L6順序/rep24失敗2件の復元(fixture化)/候補複数→unresolvable。
- runner単体・er052回帰・全体回帰(基準11件以外に新規なし。`budget_state_*.json`の書き換えは`git checkout`で戻す)。

## 作業5: 影響instance再実行(有料、rep25)

- スクリプト`er052_open233_self_recovery_flow_runner_01_rep25_affected_01.py`(rep24スクリプトを複製、instance=`safety_A2A3`・`bgroup_B3`、n=2、`VS_SENTENCE_RESTORE=True`+rep24と同じスイッチ)。出力`er052_output/open233_self_recovery_flow_runner_01_rep25/`。
- 確認: STAGE4 0件(KPI)/Safety-critical(A2A3-0、B3)検出・`residual_at_pass`残存0/L6発火と復元文の逐語(Checker `issue`との対応を目視相当で確認)/最小Rewrite(Rewrite前後diffで変更が焦点内か)/`issue_focus_absent`の発火有無/費用(rep24同instance比。+¥2/記事以内)/JA変更0。
- 即時STOP: JA変更・重大解放・Safety残存・例外。

## 作業6: SSOT

- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §48「L6実装・Opus#9是正・rep25(委任_66)」。`OPEN_ITEMS.md` OPEN-233行Status「L6実装(既定OFF)+rep25【STAGE4 X件、L6復元Y件】(委任_66)。29件再確認は委任_67」(旧Statusは「旧Status参考(委任_65)」で残す)、次Action末尾「(委任_66)Fable照合→委任_67=29件横断再確認(Human Review 0件の実証、¥17前後)→STOP報告(確認事項: アンカー型/U-2(1)/L5末尾省略の粒度/B3根本原因のChecker入力側是正)」。`OPEN-233-A1-PROD`行に「L6完結文復元(`VS_SENTENCE_RESTORE`)」「runner/er010共有module化」「Production `sentence_fallback`集計(配線前¥0)」を追加。`docs/pm/REPORT_LEDGER.md` OPEN-233行備考(Opus発火列に#9 A)。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(L6実装+rep25完了、Fable照合待ち)」(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は本委任では編集しない。

## 事前指定Read一覧

- `docs/pm/design_open233_span_sentence_restore_01.md`: §4・§5。`er052_output/open233_span_restore_offline_01/replay_01.py`: 全文(L6試作、runnerへ移植)。`results_01.md`: 復元6件・合成・ストレスの集計行。
- runner: Grep `_vs_wordch|vs_word_boundary_ok`(3482〜3505)、`vs_sentence_segments`、`vs_explain_split_resolve`(P→L6の挿入位置)、`_resolve_claim_string`/`resolve_violation_spans`(未確定の分岐)、`rewrite_ranges_ladder`(4155〜4264、E1空→③の分岐)、E1 Prompt(4020〜4048)、`full_recheck_required`、`claim_span_text`、`vs_replace_once`、`switches`、summary集計 → 該当範囲(全文Read禁止)。
- `er052_open233_self_recovery_flow_runner_01_rep24_full_01.py`(複製元)。rep24 `bgroup_B3` s2・`safety_A2A3` s2 instance JSONの`handoff`/cycle別本文/`prior_issues`(Grep抽出)。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `build_prior_issues_instruction` → 該当範囲のみ(read-only)。
- テンプレート不要。`OPEN_ITEMS.md`/REPORT/REPORT_LEDGER: Grep `委任_65` → 更新位置のみ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_66.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_66.md_check.json

¥0検証:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_span_restore_offline_01\replay_01.py --use-runner
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_span_restore_offline_01\cycle_cross_replay_01.py
(引数名は実装に合わせてよい。)

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

rep25(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep25_affected_01.py --stage main --n 2 --budget-jpy 8
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep25_affected_01.py --stage agg

順序: T-0 → 作業1 → 2 → 3 → 4 → 1回目commit/push → 5 → 6 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、REPORT。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。
- 1回目commit: Opus#9保存ファイル、設計書、runner、runnerテスト、replay関連、委任ログ`_66.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: Opus独立レビュー#9(L6完結文復元)を保存、L6をOpus是正ガード(残余包含・間隔整合・略語文分割・issue_focus_absent・2文焦点ガード・数値境界補正)付きで検証用runnerへ実装(既定OFF)、¥0 replay・cycle横断replay・B3根本原因点検(Production未変更)(委任_66)`
- 2回目commit: rep25スクリプトと出力、REPORT、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: L6有効で影響instance(A2A3・B3)を再実行rep25【STAGE4 X件、L6復元Y件、¥Z】、29件再確認は次委任(委任_66)`
- commit前に`git status --porcelain`で混入なしを確認。競合・新規テスト失敗は自動解決せず報告。

## 報告(RESULT_PACKET項目)

(1)結論10行以内(rep25でHuman Review 0件か/重大見逃し0か/費用)、(2)実装の要点とOpus是正の反映箇所(行番号)、(3)replay一致・cycle横断replay・B3根本原因点検の結果、(4)U-2(1)設計+replay結果(実装なし)、(5)rep25結果表(run別: STAGE4/L6発火・復元文逐語/`issue`対応/最小Rewrite diff/費用/rep24比)、(6)テスト件数・回帰、(7)SSOT更新箇所、(8)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(9)Fableへの論点・USER_DECISION候補。

---

## 参考(逐語): Opusへの依頼(レビュー#9)

[依頼文: 本委任を発行したFableがopus-consultantへ送った依頼。論点1〜8: 1.ガードは「別の文を誤って選ぶ」Failureを封じているか 2.アンカー型は基本線の範囲内か 3.P→L6の順序 4.最小Rewrite原則の仕組み 5.残る例外を決定論で減らせるか 6.Production配線時の矛盾 7.KPI 3つを同時に満たすか 8.数値境界補正はどこで直すか。packet: `docs/pm/opus_packet_open233_span_restore_01.md`、設計書: `docs/pm/design_open233_span_sentence_restore_01.md`。]

## 参考(逐語): Opus独立技術レビュー#9 全文

# Opus独立技術レビュー #9: OPEN-233 L6「完結文復元」設計(条件A)

結論: L6 を入れることは**必要**。全体の構造(P→L6、決定論のみ、追加 LLM call なし)にも**大筋で同意**する。ただし設計書の「誤復元0」「最小Rewrite維持」「ラダーの段を進めない」という主張には、それぞれ根拠が足りない箇所が1つずつある。実装前に決定論のガードを4点足すことを推奨する。採用可否と Production 採用は宣言しない(人間ユーザーのみが決める)。

## 12観点(独立評価)

1. **必要性**: 必要。rep24 で残った Human Review は2件ともこの型。Primary KPI(Human Review 0件)にも直結する。
2. **単純化**: 骨格は妥当。ただし数値境界の補正は L6 側ではなく単語境界関数側で直す方が単純で正しい(論点8)。
3. **既存処理の利用**: `vs_sentence_segments`、正規化、`vs_replace_once` を再利用しており良い。ただし Production(er010)は文分割が別実装(行を連結し、見出しを除外する方式)で、二重実装の問題が残る(論点6)。
4. **前段情報の喪失・再探索**: replay 実装では、アンカー外の語(最大6語)の行き先を検査していない。claim の一部を黙って捨てる「縮小」が起こりうる(論点1の穴A)。
5. **LLM 追加**: なし。良い。
6. **非決定性**: 照合部分は増えない。ただし範囲が文に広がると E1 の出力の振れ幅は増える(論点4)。
7. **Human Review**: 減る。ただし Production では逆に**増える**可能性がある(論点6の(a))。
8. **不要Rewrite**: 設計書の評価は楽観的。E1 が空を返すと③(文単位の汎用 Rewrite)へ進む。古い引用(stale)型ではここで不要Rewrite が起きる(論点4)。
9. **コスト**: 問題なし(平均+¥0.03/記事の見積りは妥当)。
10. **retry/fallback/regeneration**: Trial 内では矛盾なし。Production の fallback との関係が未解決(論点6)。
11. **Failure 時の安全側**: 候補0・複数・例外は従来経路へ戻るので良い。ただし穴A・穴B(論点1)は「安全側に倒れない」誤りの形。
12. **再発防止になっているか**: 半分。B3 の根本原因(Checker が前 cycle の本文を引用した可能性)には触れていない(論点7)。

## 論点別回答

**1. ガードは「別の文を誤って選ぶ」Failure を封じているか**
- 大筋では封じている。ただし根拠の置き方がずれている。n-gram 一意率(4語で98.3%)は「復元できる割合」の根拠であって、安全性の根拠ではない。安全性を支えているのは「アンカーが記事に逐語でちょうど1箇所ある(実装で確認済み)」+「Checker は記事から写した」という2点。ガード値の高さそのものは過剰でも不足でもない。
- **穴A(縮小)**: `anchor_scan` は先頭側か末尾側の一方のアンカーが複数箇所に出る(曖昧な)とき、それを無視してもう一方だけで位置を決める。アンカー外の語(6語以内)が記事の別の文に逐語で存在する場合(Checker が2文を混ぜた場合)でも、片方の文だけを復元して終わる。
  - 対策(決定論): 「アンカー外の語の連続部分が記事に逐語で存在するなら、その位置は復元範囲の内側にあること。外側にあれば復元しない」という残余包含検査を足す。
- **穴B(位置の整合)**: 先頭アンカーと末尾アンカーの両方があるとき、replay は順序だけを検査している。記事上の間隔と claim 上の間隔(アンカー外の語数)が対応しているかは見ていない。
  - さらに、2つのアンカーが重なると unmatched が負の値になり、そのまま通る(`replay_01.py` 260-261行)。cover も二重に数えられる。
  - 2文以内のガードがあるので実害は小さいが、「間隔が claim 側の語数+α以内」「unmatched≥0」の検査を足すべき。
- **文分割**: `_VS_SENT_END_RE` は `.`+空白で必ず文を切る。`U.S. officials`、`Mr. Trump`、`Jan. 5` で文が割れ、「完結文」が文の途中までになる。現 fixture は `US` 表記なので表面化していない。2文以内のガードと合わさると、不完全な範囲を復元するか、安全側の拒否(Human Review)が増えるかのどちらか。
  - 対策: 略語の除外リスト(固定、決定論)を L6 用の文分割に入れる。
- **検証の母数**: 実例10件と、閾値を決めたのと同じ fixture の機械的変形が中心で、過学習の余地がある。
  - ¥0 でできる、より実分布に近い検証: 既存ログで「cycle N−1 の本文で確定した claim を、cycle N の本文に当てる」。これは B3 型の古い引用そのものを再現する。

**2. アンカー型は基本線の範囲内か**
- 技術的見解: 「似ていることを根拠に範囲を選ぶ」再推測ではない。部分文字列の同一性だけで位置を決め、範囲は拡張のみ。この点で、基本線の**趣旨**の内側にある決定論的拡張と評価できる。
- ただし基本線の**字義**(「変換後の文字列が完全一致」)は明確に超えている。加えて、アンカー外の語を捨てる点は、穴A を塞がない限り「範囲を縮小しない」と緊張関係にある。
- ユーザー指示(6回目)の文言は「途中切断・...省略」で、語の**置換・混入**には明示的に触れていない。私の見解では、ユーザーへの1行確認(「Checker が記事にない語を1〜6語混ぜた場合も、逐語で一意な部分から文を決めてよいか」)を挟むのが筋。判断は Fable とユーザーに委ねる。

**3. 順序(P→L6)**
- 正しい。逆順にすると P の4ガードを迂回してしまう。統合は複雑化するだけ。
- 1点だけ不整合がある。末尾 `...` の claim で、前半が逐語なら現行 L5 が「断片」を範囲として確定し、語の混入があれば L6 が「完結文」を範囲にする。似た入力で範囲の粒度が変わる。
  - 実害は小さい(ラダー③で文へ広がる)が、ユーザー指示の文言に揃えるなら、L5 の末尾省略も完結文へ広げる方が一貫する。判断事項として記録しておくこと。

**4. 最小Rewrite の仕組み**
- **不十分**。設計書の「ラダーの段を進めない」は入口の段についてだけ正しい。runner の 4216-4229行では、E1(`allow_empty: False`)が空または失敗を返すと③ `3_sentence`(E2 の汎用 Rewrite)へ進む。L6 の復元文は既に文なので、③の対象は同じ文で、許される編集が大きくなるだけ。
- B3 型(issue が指す語 `so` が現本文に無い。既に `while` へ修正済み)では、E1 は空を返すか、無関係な編集をする可能性が高い。そうなると③の不要Rewrite へ進む。
- 推奨(決定論、LLM call 追加なし):
  - (a) issue 中で引用符に囲まれた語(例: “so”)が復元範囲に無いときは `issue_focus_absent` を記録する。その claim は Rewrite をせず、Recheck だけに回す(Recheck は既存の call で、費用はむしろ減る)。
  - (b) 2文を復元した場合は、Rewrite 結果を diff し、変更位置が「元の断片またはアンカーを含む文」の内側に収まるかを書き戻し前に検査する。外側の変更は不採用とし、E1 失敗として扱う。設計書では「最小Rewrite 違反率」を評価項目としているが、これはガードにすべき。
  - (c) E1 Prompt に、元の断片(fragment)を「指摘箇所」として併記する。範囲は文、焦点は断片という形。Prompt の変更は小さいが、Prompt 改変になるので扱いは Fable が判断する。

**5. 残る例外((d)型・候補0・複数)を決定論で減らせるか**
- U-2(1)の位置語→構造要素の機械的な対応(`headline`→`#` 見出し行、`one-line`→`## In one line` 直下の1行を範囲に追加)は決定論で可能で、LLM call も不要。対応表を閉じた語彙(headline / title / one-line summary / In one line)に限れば安全。範囲が広がるだけで縮小はしない。
- U-2(2)の `remainder_too_long` の緩和は Opus#7 の判断の再検討にあたる。引用断片を範囲にして説明文を捨てる案は、説明文が別の箇所を指していた場合に見逃しにつながる。(1)より慎重に扱うべき。
- 候補0・複数は実例が0件。U-3(span 再取得)は今は不要で、実例が出てから検討すれば足りる。
- 残りを0件にするには、決定論では原理的に届かない領域が残る(Checker が記事に無い文を完全に言い換えた場合)。

**6. Production 配線時の矛盾**
- (a) er010 の `locate_target_sentence` は exact 一致が無ければ単語重なり0.25以上で必ず何かを選ぶ。つまり Production は現状、span の問題を Human Review にせず、黙って推測して Rewrite している可能性がある。
  - L0〜L6 へ置き換えると、誤った対象への Rewrite(Safety 側)は減る。一方で、Production で見える Human Review は**増える**可能性がある。
  - 置き換え前に、Production ログで `sentence_fallback(overlap=...)` の発生件数と、その正誤を集計することを推奨する(¥0)。
- (b) er010 の exact 一致は単語境界も見ない(`in` による判定)。`2.6` の穴はより広く存在する。
- (c) er010 は行を連結して見出しを除外する独自の文分割を持ち、runner の `vs_sentence_segments` と文の単位が違う。Trial 専用の実装が2本並ぶことを避けるため、照合 L0〜L6 と文分割を純関数の共有 module に切り出し、runner と er010 の両方から呼ぶ構造を推奨する。er010 は元々「文」を対象にするモデルなので、L6 の出力とは相性が良い。
- retry・regeneration・Stage 4・floor との矛盾はない(L6 は未確定の件数を減らすだけ)。

**7. KPI 3つを同時に満たすか**
- 今回のセットについては見込みあり。Cost は余裕で満たし、Safety も悪化要因は小さい(穴A・穴B を塞げば)。
- Primary の残りは2種類。(d)型(過去 0.85%)は U-2(1)である程度、決定論で潰せる。完全言い換えによる候補0は決定論では不可能。
- 根本原因の仮説を確認してほしい。B3 は Checker が cycle1 の本文(`so`)を引用した可能性があり、cycle2 の Checker 入力(prior_issues に前 cycle の span text が渡っていないか)を確認すべき。もし前 cycle の text が入力に含まれていれば、Checker の入力側を直すことが再発防止になる。L6 だけでは対症療法にとどまる。
- 母数(10件)は小さい。実 flow の再実行と、論点1の cycle 横断 replay を併用すべき。

**8. 数値境界の補正はどこで直すか**
- **単語境界関数そのもの**(`_vs_wordch` / `vs_word_boundary_ok`、フラグで切替)を直すべき。
- 理由1: L6 側だけで補正しても、base(L0〜L5)が `6 percent…` を先に確定してしまい、L6 は呼ばれない。
- 理由2: `vs_replace_once` は一致1箇所なら書き戻すので、`2.` + 書き換え後の文、という数値の破壊を起こしうる潜在バグであり、L6 と独立した不具合。
- 既存の確定済み claim への影響はログ上1件(7 runs)のみで、すべて正しい方向への変化。
- er010 の exact 一致にも同じ穴がある。共有 module 化(論点6)の際に同時に直すこと。

## まとめ
- **必要/不要**: 必要。
- **推奨構造**: P→L6 を維持し、次を追加する。
  - (1) 残余包含検査とアンカー間隔の整合検査(穴A・穴B)
  - (2) 略語に対応した文分割
  - (3) `issue_focus_absent` の場合は Recheck だけに回す(Rewrite しない)
  - (4) 2文復元時の diff による焦点文ガード
  - (5) 単語境界の修正は関数側で行う
  - (6) runner と er010 で共有する照合 module
- **リスク**: アンカー外の語を捨てることによる縮小、E1 が空を返したときの③への進行による不要Rewrite、略語での文の割れ、Production の Human Review 件数が見かけ上増えること、閾値の過学習。
- **代替案**: cycle 横断 replay(¥0)による実分布検証を先に行う。Checker 入力に前 cycle の text が混入していないかを点検する(根本原因側の対策)。

## 追加で読んだファイル(宣言済み)
- `er052_open233_self_recovery_flow_runner_01.py` 3425-3509・3919-3998・4155-4264(約1.2万字)
- `er052_output\open233_span_restore_offline_01\replay_01.py` 60-349(約1.3万字)
- `er010_ledger_local_rewrite_09.py` 55-94(約2千字)
- 必須2点: `docs\pm\opus_packet_open233_span_restore_01.md`、`docs\pm\design_open233_span_sentence_restore_01.md`(合計約4万字)

## 今回の context で十分に答えられなかった論点
- B3 の古い引用の原因。cycle2 の Checker 入力(prior_issues の中身)と cycle1 B3 の本文を読んでいないため、仮説のまま。
- ラダーの各段の間に Recheck が入るか(runner 4264行以降は未読)。
- Production での `sentence_fallback` の実際の発生件数。
- `results_01.md` の合成テストとストレステストの個別ケース(未読。packet の要約を前提にした)。
