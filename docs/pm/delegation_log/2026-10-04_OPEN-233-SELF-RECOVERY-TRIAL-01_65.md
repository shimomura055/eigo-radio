## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_65)。並行タスクなし。¥0(API課金・Trial実行なし。既存ログの決定論replayのみ)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー指示(2026-10-04、6回目)に基づき、Checker返却spanの「途中切断」「`...`省略」を**Human Reviewなしで自動解決**する後段照合の設計と、既存ログによる¥0の決定論検証を行う。Primary KPI=Production運用でChecker起因のUSER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均+¥2/記事以内、を同時に満たす設計であること。実装は本委任では行わない(設計→Opus独立レビュー[条件A]→Fable照合→委任_66で実装)。
- 到達上限Status: 設計案+¥0検証結果(`docs/pm/design_open233_span_sentence_restore_01.md`)。次Trial(10本)は開始しない。
- 禁止事項:
  - コード(runner・Prompt・Production path)の変更禁止。replay用スクリプトは`er052_output/open233_span_restore_offline_01/`配下に新規作成する(runnerの既存関数をimportして使ってよい。runnerは変更しない)。
  - 「Human Reviewを残す」前提の案を推奨にしない。Human Reviewに回すのは「断片を含む完結文が記事内で一意に決まらない」場合だけ。
  - 類似度・単語重なりによる推測照合を使わない(決定論の部分文字列照合のみ)。範囲を縮小しない(断片→それを含む完結文へ拡張のみ)。
  - 新しいProduct判断が必要になったら、設計書にUSER_DECISION候補として明記(勝手に決めない)。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: ¥0。Phase累計¥572.8515、上限¥900。
- Opus独立技術レビューGate: 条件A(新しい処理フロー: 後段照合に文復元レベルを追加)に該当。本委任の設計書とOpus向けcontext packet(`docs/pm/opus_packet_open233_span_restore_01.md`、`docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`(a)〜(g)に従う。(g)の独立レビューブロックは`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`の`---`内を改変せず貼る。packet総量2〜3万字以内)を作成する。Opusへの依頼はFableが行う。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_65.md`。**委任文は全文そのまま保存(要旨化・要約保存は不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用`.md`をWriteツールが拒否する場合は、Pythonスクリプトからファイル出力する。

## ユーザー指示(原文)

次の全文を`DECISION_LOG.md`末尾へ一字一句そのまま引用する(作業0)。

````
OPEN-233のPrimary KPIは、Production運用におけるChecker起因のUSER_DECISION_REQUIRED / Human Review 0件です。
今回の2件について「件数が少ないのでHuman Review維持を推奨」という提案は、KPIと明確に矛盾しています。
今後、KPI未達を前提にした“ぬるい安全側提案”を推奨案として出さないでください。
今回の2件は、重大判断そのものではなく、Checker返却spanの途中切断・省略という技術問題です。まずHuman Reviewなしで解決する方法を詰めてください。
現在の方向性は以下です。
- Checkerは検出に専念する。
- 後段で記事原文に照合する。
- spanが途中切断・...省略でも、断片を含む意味の通る完結文が記事内で一意に特定できるなら、その文を対象範囲として復元する。
- 複数候補、本当に一意に決められない場合のみ例外扱い。
- 範囲拡張で不要Rewriteが入らないよう、最小Rewrite原則は維持する。
必ず以下のKPIを同時に満たす前提で設計・検証してください。
- Primary：USER_DECISION_REQUIRED / Human Review 0件
- Safety：重大Fact見逃し 0件
- Cost：平均 +¥2/記事以内
今回の29件横断で残ったHuman Review 2件は、このspan不完全の2件だけです。
したがって、ここを自動解決できれば今回セットではHuman Review 0件になります。
次の報告では「Human Reviewを残す理由」ではなく、0件にするためにどう自動解決したか／できなかったなら何が技術的に不可能だったかを示してください。
KPIを満たせない状態を安易に推奨案として持ってこないこと。
Production量産性を成立させるためのTrialであることを忘れないでください。
````

## 作業0: ユーザー指示の記録

`DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、ユーザー指示[6回目]: Primary KPI=Checker起因のUSER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均+¥2/記事以内。span途中切断・`...`省略はHuman Reviewなしで自動解決[断片を含む完結文が記事内で一意なら復元、一意でない場合のみ例外、最小Rewrite原則維持]。KPI未達前提の安全側提案を推奨にしない)」を追記し、原文を全文逐語で引用。続けて「Fableの受け止めと分担」(Fableの前回推奨(A)「現状維持」はKPIと矛盾していたため撤回。委任_65=設計+¥0検証+Opus packet、Opus独立レビュー(条件A)、委任_66=実装+単体テスト+影響instance再実行、その後29件横断の再確認でHuman Review 0件を実証)。`OPEN_ITEMS.md` OPEN-233行Statusの冒頭に「(2026-10-04、ユーザー指示[6回目])判断(A)は撤回され「span切断の自動復元を設計・検証」へ変更。Primary KPI=Human Review 0件。委任_65で設計中」を追記、次Action欄末尾に「(委任_65)設計+¥0検証→Opus条件A→委任_66実装→影響instance再実行→29件再確認(Human Review 0件の実証)」を追記(既存文は削除しない)。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(span切断の自動復元: 設計+¥0検証中、KPI=Human Review 0件)」(addしない)。

## 作業1: 現状の照合経路と失敗2件の正確な把握

- runnerの`resolve_violation_spans`→`_resolve_claim_string`→`_resolve_claim_string_base`(L0〜L4)、`VS_MATCH_EXT`(L5: edge punctuation strip+word boundary[EN]、`label_only`)、`VS_EXPLAIN_SPLIT`(P-strict-closed)、「確定=記事内でちょうど1回出現」、unresolvable→`violation_span_unverified`→STAGE4の流れを、該当行番号付きで設計書§1に整理(Grep: `_resolve_claim_string_base`、`VS_MATCH_EXT`、`word boundary`/`\\b`、`label_only`、`vs_explain_split_resolve`、`violation_span_unverified`、`claim_span_text`、`unresolvable`)。
- rep24の失敗2件(`er052_output/open233_self_recovery_flow_runner_01_rep24/`の`safety_A2A3` s2 cycle2と`bgroup_B3` s2 cycle2のinstance JSON)から、Checkerの`claim_in_article`原文・`issue`・記事本文中の該当完結文・各レベルでの失敗理由(`mismatch`/`fragment_not_in_article`/`no_quote`等)を逐語で設計書§2に転記。A2A3 s1/s2 cycle1の「`6 percent, because …`」型(別claimのRewriteでカバーされた2件)も同様に転記。
- 過去ログ(`er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`、rep22〜rep24のinstance JSON)から、unresolvableになった全claimを収集し、型分類する: (a)途中切断(先頭が語・数値の途中)、(b)末尾`...`/`…`省略、(c)中間`...`省略、(d)説明文混入、(e)記事にない語の混入(Checkerの言い換え)、(f)複数出現、(g)その他。件数と代表例を§3に表で。

## 作業2: 設計(L6「完結文復元」)

設計書§4に次を定義(Opus#5・#6の受け渡し基本線「Checkerの違反範囲を後段で再推測しない/類似度で縮小しない」との関係を明記: 本件はユーザー指示により、**縮小ではなく、断片を含む完結文への決定論的拡張**を認めるもの)。

- 発火条件: L0〜L5(+P-strict-closed)で確定しなかったclaimのうち、(i)断片の先頭または末尾が語・数値の途中で終わる(単語境界を満たさない)、または(ii)`...`/`…`/`・・・`を含む、または(iii)断片全体としては記事に一致しないが、`...`で分割した各部分(先頭部・末尾部)は記事に一致する、のいずれか。
- 復元手順(決定論): (1)記事を文に分割(既存の文分割関数があればそれを使う。Grep `split_sentences`/`sentence_split`/`find_sentence_context`)。(2)断片(または`...`分割後の先頭部と末尾部)を正規化(既存L2/L3/L5と同じ: 空白・引用符・大小・端の句読点)したうえで、**部分文字列として**含む文を探す。`...`型は「先頭部を含み、同じ文(または隣接する連続文)内でその後に末尾部が現れる」文を探す。(3)候補がちょうど1文(または隣接する連続文の1組)なら、その完結文(群)を対象範囲として確定し、`level="L6:sentence_restore"`、`restore_reason`(truncated_head/truncated_tail/ellipsis_tail/ellipsis_mid)、元断片・復元文を記録。(4)候補0または2以上なら従来どおりunresolvable(例外扱い。これが唯一のHuman Review経路)。
- ガード: 断片の最小長(例: 正規化後EN≥3語かつ≥12文字、JA≥8文字。短すぎる断片は復元しない。しきい値は既存ログで根拠を示す)/復元文の最大長(段落全体へ広がらないよう、連続文は最大2文まで。根拠を示す)/断片が複数の文にまたがる場合の扱い/引用符内の発話(“ ”)を含む文の扱い/`label_only`(In one line)との優先順位/P-strict-closedとの順序(P→L6かL6→Pか。P-strict-closedは「説明文を外す」、L6は「断片を文へ広げる」なので、P適用後の残りにL6を適用する案を基本とし、理由を書く)。
- 最小Rewrite原則の維持: 復元した完結文はRewriteの「対象範囲」であり、Rewrite promptには「Checkerの`issue`に該当する語句だけを最小限修正し、文の他の部分は変えない」を明示(既存のラダー①確定範囲→③文→④段落との関係: L6復元=①の範囲が文になるだけで、ラダーの段は進めない)。Recheckの`prior_issues`には復元文を渡す。
- Safety: 復元が失敗側(unresolvable)に倒れる条件を列挙。復元文がSafety-critical登録文と一致する場合の扱い(通常どおりBLOCKING→Rewrite)。復元によって「別の文」を選ぶリスク(断片が一般的な語句のとき)を最小長・一意性で封じる根拠。
- Cost: 追加API callなし(決定論のみ)。Rewrite対象が語句→文になることで増える費用の見積り(rep24実測のRewrite単価から)。平均+¥2/記事以内を満たすことを示す。
- Production配線時の対応箇所(er003のDeviation→Local Rewrite経路のどこに相当するか、`er010_ledger_local_rewrite_09.py`の`locate_target_sentence`との関係)を1節で。

## 作業3: ¥0検証(決定論replay)

`er052_output/open233_span_restore_offline_01/replay_01.py`(runnerの既存関数をimport、L6はreplayスクリプト内に試作実装。runner本体は変更しない)。
- 対象: 作業1で収集したunresolvable全claim+rep24の全claim(確定済みのものも含む。L6が確定済みclaimの結果を変えないことの確認)。
- 出力`results_01.json`/`results_01.md`: claimごとに、従来レベルの結果/L6発火の有無/候補数/復元文/`restore_reason`/判定(復元成功・候補0・候補複数・発火せず)。
- 必須確認: (1)rep24の失敗2件(A2A3 s2・B3 s2)が一意に復元されること(復元文を逐語で示し、Checkerの`issue`が実際にその文の問題を指していることを目視相当で確認)。(2)A2A3の「`6 percent, because …`」型2件も復元されること。(3)確定済みclaimの結果が1件も変わらないこと。(4)**誤復元0**: 復元文がChecker `issue`と無関係の文になったケースが0件であること(全復元件を列挙し、1件ずつ`issue`との対応を仮判定)。(5)過去unresolvable全体のうち、L6で復元できる割合・残る割合と、残るものの型(=技術的に不可能な残り)。
- 合成テストケース: 途中切断(先頭/末尾)・末尾`...`・中間`...`・短すぎる断片・同じ断片が2文に出現(候補複数→例外)・引用符内発話を含む文・2文またがり、各1件以上をrep24の記事本文で作り、期待どおりの判定になることを確認。

## 作業4: Opus向けcontext packet

`docs/pm/opus_packet_open233_span_restore_01.md`を雛形(a)〜(g)で作成。(a)論点: 1.L6の発火条件・一意性・最小長ガードは「別の文を誤って選ぶ」Failureを封じているか 2.受け渡し基本線(再推測しない・縮小しない)との整合 3.P-strict-closedとL6の順序 4.最小Rewrite原則が実際に守られる仕組み(promptと記録) 5.Human Reviewに残る例外(候補0/複数)を更に減らす決定論的手段はあるか 6.Production配線時の矛盾(er003/er010/retry/fallback/regeneration) 7.KPI(Human Review 0/重大見逃し0/+¥2以内)を同時に満たすか。(b)失敗2件の逐語・記事該当文・replay結果表・費用見積り。(c)runner行範囲(Grep確認列付き)。(d)Sonnet要約。(e)Progressive Disclosure指示文。(f)文字数自己計測。(g)発火条件=条件A、重複レビュー確認(既存Opus#5[受け渡し再設計]・#6[後段対策]との関係: 内容が変わる[拡張を認める]ため再レビュー)、独立レビューブロックを逐語貼付。

## 作業5: 記録

- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §47「span切断の自動復元(L6)設計と¥0検証(委任_65)」。`docs/pm/REPORT_LEDGER.md` OPEN-233行の備考。

## 事前指定Read一覧

- runner: Grep(上記)→該当範囲のみ。全文Read禁止。
- rep24 instance JSON: `safety_A2A3`(s1, s2)、`bgroup_B3`(s2)の`handoff`/`claims`/`stage4`該当フィールド(Grepで抽出)。`summary_01.json`。
- `er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`(unresolvable行のみ抽出)。
- `docs/pm/design_open233_violation_span_handoff_01.md`: Grep `基本線`/`縮小`/`再推測` → 該当節。`docs/pm/opus_l2_review_open233_self_recovery_05.md`・`_06.md`: Grep `縮小|1文|再推測|word overlap` → 該当行。
- `docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`: §P-strict-closedの4ガード部分(Grep `ガード`)。
- `er010_ledger_local_rewrite_09.py` L60〜90(`locate_target_sentence`)、`er003_v1_en_direct_vfl_01_generate.py` Grep `MINOR|location|claim_in_article` → 該当行のみ(read-only)。
- テンプレート: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`、`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`(全文)。
- `DECISION_LOG.md`/`OPEN_ITEMS.md`/REPORT/REPORT_LEDGER: 追記位置のみ(Grep `委任_64`)。

## 事前指定Grep一覧+追記位置

- 上記のとおり。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_65.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_65.md_check.json

replay(¥0):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_span_restore_offline_01\replay_01.py

テスト: runner未変更のため回帰不要。`git status --porcelain`で混入なしを確認。

順序: T-0 → 作業0 → 1 → 2 → 3(結果を設計書§5へ) → 4 → 5 → commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `DECISION_LOG.md`末尾、`OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない。
- add対象: `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、REPORT、`docs/pm/design_open233_span_sentence_restore_01.md`、`docs/pm/opus_packet_open233_span_restore_01.md`、`er052_output/open233_span_restore_offline_01/`配下、委任ログ`_65.md`・`_check.json`。
- メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: ユーザー指示(Primary KPI=Human Review 0件、span切断は自動復元)を逐語記録、L6完結文復元の設計と¥0決定論検証【復元X/Y・誤復元0】、Opus条件A向けpacketを作成(未実装、Production未変更)(委任_65)`
- commit前に`git status --porcelain`で混入なしを確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内(失敗2件は復元できたか/誤復元0か/残る不可能ケースは何か)、(2)unresolvable型分類表、(3)L6設計の要点(発火条件・手順・ガード・しきい値根拠・P-strict-closedとの順序・最小Rewrite維持)、(4)replay結果表(復元成功/候補0/候補複数/確定済み不変)、復元全件と`issue`対応の仮判定、(5)KPI見通し(Human Review/重大見逃し/費用)、(6)USER_DECISION候補(あれば)、(7)packet文字数、(8)SSOT更新箇所、(9)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
