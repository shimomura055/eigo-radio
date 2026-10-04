## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_60)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定(2026-10-04、判断D=案1)の記録と実装: 比較・方向・時期の機械判定(floor)に限って「追加確認2回で2回とも重大でなければ軽微以下へ戻す」仕組みを検証用runnerへ実装し、判定原則文の矛盾を整合し、「動機」の整理を仕様・文書へ反映し、限定的な単体安全確認(有料)と再較正を行う。限定flow・29件横断は本委任では行わない(次の委任)。
- 到達上限Status: 案1=ユーザー正式判断済み(`APPROVED_FOR_PRODUCTION`)。本委任では検証用runnerへの実装・テスト・runtime evidence・SSOT反映まで。**自己修復機構本体がProduction未接続のため`PRODUCTION_WIRED`ではない**(明確に区別して記録)。次Trial(5記事×2レベル)は開始しない。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。
  - **主体(`changed_actor`)・数値(`changed_number`)・否定(`changed_negation`)のfloorは変更しない**(決定論のまま)。これらのフラグが1つでもtrueの指摘は、追加確認の対象にしない。
  - 自動解放(文字一致・台帳中の上昇/下落語の有無だけを根拠にした解放)を実装しない。解放は「追加確認2回とも非BLOCKING」のときだけ。
  - `dev`のフラグを書き換えない(解放理由は別フィールド)。確認のAPI失敗・schema不一致・曖昧(2回の判定が食い違う、BLOCKINGが1回でも出る)はBLOCKING固定。
  - 既存より厳しくする変更を追加しない。新しい仕様候補を勝手に追加しない。
  - 新スイッチは既定OFF。既存テスト・`HANDOFF_MODE=legacy`・固定fixtureが動き続けること。
  - 単体確認で**重大ラベルのケースを1件でも軽微以下へ解放したら、その時点で測定を止めて報告**(修正を重ねない)。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分に触れない。
- 費用上限: 上限¥45(Guardrail。内訳の目安: 単体安全確認¥10〜30[ユーザー承認済み]、V7文言整合の再較正¥8〜10)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥536.4930、上限¥900。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A該当だが、Opus独立レビュー#8(`docs/pm/opus_l2_review_open233_self_recovery_08.md`)で代替案F5として提示・レビュー済み。ユーザーが案1(F5を比較・方向・時期に限定、確認2回)として正式判断。本委任はその形で実装する。レビュー済みの形と異なる変更が必要になったら実装せず報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_60.md`。**委任文は全文そのまま保存(要旨化不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文)

次の全文を`DECISION_LOG.md`末尾へ一字一句そのまま引用する(作業1)。

````
OPEN-233について、判断Dは以下で確定です。

## 1. ユーザー判断

**案1を採用します。**

つまり、

**比較・方向・時期に関する機械判定だけ、追加確認で軽微へ戻せる仕組みを導入する。**

一方で、

- 主体の取り違え
- 数値改変
- 否定反転

は、これまでどおり決定論的な安全判定を維持してください。

主体については、役職の一般化のような過剰判定が一部残ることは現時点では受容します。

---

## 2. 実装方針

比較・方向・時期について、

- 決定論的に台帳との不一致を確認できたものは重大のまま
- それ以外で、機械判定と通常の判定役が食い違う場合だけ追加確認を行う
- Checkerの指摘内容を「検証すべき仮説」として確認する
- 追加確認を2回行い、**2回とも重大ではない場合だけ**軽微以下へ戻す
- 確認失敗・不一致・曖昧な場合は重大のまま

としてください。

単純な文字一致や、台帳中に上昇/下落語があることだけを根拠に自動解放しないでください。

---

## 3. 安全確認

実装後、まず限定的な単体確認を実施してください。

最低限、

- `prices began to fall` 型
- 「撤回後に原油価格が下落した」のような明確な方向反転
- 数値の付け替え
- 日付・時期の取り違え
- 継続中の出来事を「一度消えて戻った」とするケース
- その他既存の重大Safety対照

を使ってください。

受入条件は、

**重大ラベルのケースを1件でも軽微以下へ解放したらSTOP**

です。

この単体確認の費用目安¥10〜30は承認済み予算内です。

---

## 4. 判定原則文の整合

現在の、

- 「比較の差は明確に重大」
- `prices began to fall` は軽微

という矛盾を解消してください。

原則は、

**台帳と矛盾する重大な変更  
（数値改変、主体取り違え、否定反転、方向反転、時期取り違え）は重大**

に整理してください。

今回正式採用した「重大な誤解だけ止める」基準と矛盾しないことを確認してください。

---

## 5. 「動機」の件

既に整理済みの方針を反映してください。

- 確認済みの事象に理由づけを添える「動機の帰属」→軽微
- 台帳にない意図・仕組みを新事実として作る「動機の創作」→重大

これは追加のユーザー判断なしで仕様・実装・文書を整合させてください。

既存より厳しくする変更を追加しないこと。

---

## 6. その後の確認

単体確認がPASSした場合のみ、

1. 少数の実flow確認
2. 問題がなければ29件横断を1回

まで進めてください。

確認項目：

- 真の重大見逃し 0
- 解放した重大ケース 0
- 過剰Majorが減っている
- 不要Rewriteが減っている
- Human Reviewが増えていない
- 説明文混入対策が誤範囲を選ばない
- 句読点差対策が機能する
- 英語だけ修正する方針が維持される
- retry / recheckで仕様が崩れない

問題が出たら29件へ進まずSTOPしてください。

---

## 7. 次Trialは禁止

**5記事 × Standard / Advanced = 10本の次Trialはまだ開始しないでください。**

今回のSTOP地点は、

**少数flow確認＋必要なら29件横断まで**

です。

結果をユーザーへ報告し、次TrialのGO判断を待ってください。

---

## 8. Production / Status

今回の案1については、ユーザー正式判断済みです。

必要な仕様反映・テスト・runtime evidence・CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS / Git反映まで完了したものだけ `PRODUCTION_WIRED` としてください。

自己修復機構本体がまだProduction未接続であれば、その点を明確に区別してください。

既にAPPROVED_FOR_PRODUCTIONの、

- 新しい重大/軽微/問題なし基準
- 句読点差対策
- 説明文混入の後段分離
- 英語だけ修正する方針

も、Production接続時に抜けがないよう一体で追跡してください。
````

## 作業1: ユーザー決定の記録

`DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、ユーザー決定[4回目]: 判断D=案1[比較・方向・時期の機械判定だけ追加確認2回で解放、主体・数値・否定は決定論維持、役職の一般化の過剰判定は受容]/単体安全確認の受入条件/判定原則文の整合/動機の反映/その後の確認手順/次Trial禁止/Status区別)」を追記し、原文を全文逐語で引用。続けて「Fableの受け止めと分担」(委任_60=記録・実装・原則文整合・動機反映・単体確認・再較正・SSOT、委任_61=限定flow→29件横断、委任_62=Closeout確認)。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(判断D=案1の実装・単体確認中、次Trial開始禁止)」(addしない)。

## 作業2: 案1の実装(検証用runner、スイッチ既定OFF)

スイッチ `FLOOR_VERIFY_MODE`(既定`"off"`、`"comparison_time"`。CLI `--floor-verify-mode`)。

2-1. **対象の絞り込み**: Stage 2のLLM判定(`llm_materiality`)が非BLOCKINGで、floor(`apply_floor`)がBLOCKINGへ昇格させた指摘のうち、trueのfloorフラグが`changed_comparison`・`changed_time`のみ(`changed_actor`/`changed_number`/`changed_negation`が1つでもtrueなら対象外=従来どおりBLOCKING確定)のものだけを対象にする。precheck floor(`precheck_floor`、数値)は対象外。
2-2. **決定論の不一致確認(CONFIRMED、維持方向にのみ働く)**: 対象について、関連factブロック(`related_fact_id`のLedger本文。無ければ全文ではなく「確認不能」として確認経路へ)と照合し、(a)`changed_time`: claimに含まれる日付・時刻・期間のトークン(月日・年・時刻・「翌日」等の決定論で抽出できる形)がfactブロックに(日英の表記正規化後に)存在しないとき、(b)`changed_comparison`: claimに含まれる数値つきの比較(%、倍、以上/以下等)がfactブロックに存在しないとき、をCONFIRMEDとしBLOCKINGを維持(確認を呼ばない)。**CONFIRMED以外は「解放」ではなく確認経路へ進む。自動解放(CLEARED)は実装しない。** 抽出規則はコード定数にし、報告に逐語で載せる。
2-3. **追加確認(2回)**: Stage 2と同じモデル・設定で、対象claim 1件ごとに独立の呼び出しを2回行う(batchに混ぜない。既存の`run_stage2_batch_variant`は使わず、新関数`run_floor_verify_call`)。入力: claim文(確定範囲)、局所文脈、関連factブロック(Ledger逐語)、Checkerの`issue`を「検証すべき仮説」として明示(「Checkerは次の問題を指摘した: …。この指摘が正しいか、Ledgerの該当箇所を引用して検証せよ」)、フラグ名(comparison/time)。出力schema: `materiality`(BLOCKING/QUALITY/ACCEPTABLE)、`ledger_citation`(逐語)、`basis`、`explanation`。判定原則文は作業3で整合させたV7(改)を使い、「台帳と矛盾する重大な変更(方向の反転、時期の取り違え)は重大。方向・時期のニュアンスの差で事実関係の核心が保たれていれば軽微」の趣旨を含める。
2-4. **解放条件**: 2回とも非BLOCKINGのときだけ、最終`materiality`をLLM判定の値(QUALITY/ACCEPTABLE。2回の確認とStage 2の3つのうち最も重い非BLOCKING値)にする。1回でもBLOCKING、API失敗、schema不一致、`ledger_citation`が空、はBLOCKING固定。`dev`のフラグは書き換えない。解放情報は`floor_verify`フィールド(対象判定の理由、CONFIRMED判定と根拠トークン、各確認の`materiality`/`basis`/`ledger_citation`/`prompt_sha256`/費用、解放の有無と理由)に記録。
2-5. **相互作用(Opus#8の必須対策)**: (a)解放したclaimは`apply_stage2_two_of_two`の降格対象から外す(解放済みはそれ以上動かさない)。(b)`run_stage2`内の`apply_floor`再適用で上書きされないよう、確認経路は`llm_materiality`を基準にし、最終値を別途セットする。(c)cycleごとに再評価(解放状態を次周回へ引き継がない)。(d)Recheck由来の指摘にも同じ経路(Stage 1初回・Recheck・Rewrite周回で同一)。(e)既存のdisclosure_gap降格・hook降格のガード条件(`FLOOR_FLAGS`等)は変更しない。
2-6. **runtime evidence**: instance JSONに`floor_verify`の全件と、summaryに「対象件数/CONFIRMED件数/確認呼び出し件数/解放件数/BLOCKING固定の理由別件数/費用」。

## 作業3: 判定原則文の整合(V7→V7b等。再較正必須)

3-1. `er052_open233_self_recovery_stage2_calibration_01.py`のV7(3)「数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり明確にBLOCKING」を、既存の基底R3(e)に揃えて「数値・主体・否定・比較・時期について、Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は、この原則の対象外で、従来どおり明確にBLOCKING」へ修正(新版名で追加、旧版は定数として残す)。`er052_open233_self_recovery_stage2_production_01.py`の`_V7_NEW_TIEBREAK`も同じ修正(Production配線時用。現行flowで使われているかはGrepで確認し、使われていなければその旨を記録)。
3-2. 正式採用基準(重大な誤解だけ止める)と矛盾しないことを、3つの例(例1=QUALITY、例2=ACCEPTABLE、K19=QUALITY)と重大例(K16・K18・A2A3-0・B4-a)の期待値で確認(作業5の再較正)。
3-3. 動機(ユーザー指示§5、Opus#8の結論): (a)設計書§0-2の記述を「未確認の人物・行動・仕組み・数字の追加(Ledgerに根拠のない人物・組織の意図・動機の断定を含む。確認済みの事象に理由づけを添えるだけで新しい具体的事実を加えないものは含まない)」へ更新(文書)。(b)Stage 2 production rubricのQUALITY行(動機の帰属)は現行flowで未使用なら変更せず、Production配線時の整合項目として`OPEN-233-A1-PROD`に記録。(c)V7(1)(イ)への「仕組み・意図」追加は**しない**(Opus#8: 既存より厳しくなりうる)。(d)criteria docに「動機の帰属=軽微/動機の創作=重大」の整理を1節追加。

## 作業4: 単体安全確認(有料、¥10〜30)

新スクリプト`er052_open233_floor_verify_unit_check_01.py`(runnerの`run_floor_verify_call`等を使う。flowは回さない)。出力`er052_output/open233_floor_verify_unit_check_01/`(生の応答、`results_01.json`、`cases_01.csv`)。
- ケース(各ケースの期待ラベルを固定し、`expected`列に記録):
  - 解放期待(過剰判定): K19「Just after the charge plan disappeared, prices began to fall.」(HF-009、comparison)、B2「Trump’s proposed Hormuz fee vanished overnight.」(label=QUALITY、Grep `B2`で正解ラベルを確認し、ラベルが別ならそれに従う)、B4「Names, plans…」(comparison、正解ラベルを設計書で確認)。
  - 重大期待(解放したらSTOP): 明確な方向反転「After the plan was withdrawn, oil prices fell.」(HF-009に`changed_comparison`を付けた合成)、K16「The fee plan left the stage, but the events driving oil prices…」型(継続中の出来事を一度消えて戻ったとする、HF-009/HF-003、time)、日付の取り違え(7/13と7/14、HF-003系に`changed_time`を付けた合成)、数値の付け替え(20%を別の対象に付けた合成。`changed_number`が立つため対象外=決定論BLOCKINGのままであることの確認)、Safety12のうち比較・時期フラグのfixture、Safety-critical 5件のうちcomparison/timeが絡むもの(A5-0=時期・経過の創作、K18=A2A3-0は主体なので対象外確認)。
  - 各ケースで、2-1の対象判定→2-2のCONFIRMED→2-3の確認2回、を実行。回数: 重大期待はn=5(各n=2回の確認=10 call/ケース)、解放期待はn=3。最初に1ケース×1回で単価を確認し、全体が¥30を超える見込みならnを減らして報告。
- 受入条件: **重大期待のケースが1件でも解放(2回とも非BLOCKING)されたら測定を止めて報告。** 解放期待のケースの解放率は参考値(0でも不合格ではない。安全側)。
- 集計: ケース別の対象判定/CONFIRMED/確認結果の分布/解放数、費用、`ledger_citation`の妥当性(目視で逐語一致か)。

## 作業5: 再較正(V7b)と回帰

- 委任_55の`er052_open233_element_trial_safety_control_05.py`を新版rubricで再実行(較正セット(a)〜(f)+K16・K18、n=2)。出力`er052_output/open233_safety_control_04/`。合格: (a)Safety-critical 5件誤降格0、(b)Safety12 0/18、(c)Hormuz V6/V7と同じ、(d)例3件期待どおり、(e)K16・K20 BLOCKING、(f)false BLOCK 0。外れたら修正を重ねず報告。
- テスト: 新規(対象判定の絞り込み、CONFIRMED規則、2回確認の解放条件、失敗時BLOCKING固定、2-of-2除外、cycleごとの再評価、スイッチOFFで無変更、legacy無影響、V7b文言の存在、動機の文書整合)。runner単体・er052回帰・全体回帰(基準11件以外に新規なし。`budget_state_c233an_42_rep22.json`の書き換えは`git checkout`で戻す)。

## 作業6: SSOT

- `CURRENT_SPEC.md`: 委任_55が新設したOPEN-233節に「比較・方向・時期の機械判定の追加確認による解放(案1、2026-10-04ユーザー正式判断、`APPROVED_FOR_PRODUCTION`、自己修復機構本体がProduction未接続のため`PRODUCTION_WIRED`ではない)」を追記: 仕組みの要点(対象の絞り込み、CONFIRMED維持、確認2回、失敗時BLOCKING固定、主体・数値・否定は決定論維持)、判定原則文の整合(V7b)、動機の整理、単体確認の結果、再較正の結果。
- `OPEN_ITEMS.md` OPEN-233行Status: 「ユーザー決定[4回目]反映(2026-10-04、委任_60): 案1実装(既定OFF)【単体確認PASS/STOP】、V7b再較正【結果】。限定flow・29件横断(1回)は次工程。次Trial禁止。自己修復機構本体はProduction未接続(`PRODUCTION_WIRED`ではない)。」(旧Statusは「旧Status参考(委任_59)」として残す)。`OPEN-233-A1-PROD`行: 一体で追跡する構成要素に「案1の追加確認」「新しい線引き(V7b)」「動機の整理(production rubricのQUALITY行整合)」を追加。
- `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考。`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §42。設計書`docs/pm/design_open233_floor_alignment_01.md`末尾に「8. 実装・単体確認・再較正(委任_60)」。

## 事前指定Read一覧

- `docs/pm/design_open233_floor_alignment_01.md`: §2-4(F1/F5の定義)、§6(Opus#8後の採否)。
- `docs/pm/opus_l2_review_open233_self_recovery_08.md`: (3)Opus全文の論点1・2・5・6・8・10(Grep `論点`)。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `apply_floor`、`FLOOR_FLAGS`、`run_stage2`、`apply_stage2_two_of_two`、`llm_materiality`、`floor_reason`、`build_precheck_floor_claims`、`apply_disclosure_gap_downgrade`、`HOOK_AWARE_OTHER_FLAGS`、`stage2_results`、`switches` → 該当範囲。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `V7`、`R3`、`run_stage2_batch_variant`(620〜665行付近: Stage 2の入力) → 該当範囲。
- `er052_open233_self_recovery_stage2_production_01.py`: Grep `_V7_NEW_TIEBREAK`、`MATERIALITY_RUBRIC_V7`、`動機`。
- `er052_open233_element_trial_safety_control_05.py`: 全文(再利用)。`er052_output/open233_safety_control_03/results_01.json`: 集計キーのみ。
- 設計書`docs/pm/design_open233_self_recovery_flow_01.md`: Grep `0-2`、`B2`、`B4-a`、`Names`、`K16`、`A5-0`、`正解ラベル` → 該当範囲(全文Read禁止)。
- Ledger: `er019_output/.../verified_fact_ledger.txt`(HF-003・HF-009・該当factブロック。Grep)。
- `CURRENT_SPEC.md`: Grep `OPEN-233` → 委任_55の新設節だけ。`OPEN_ITEMS.md`: Grep `OPEN-233`。`DECISION_LOG.md`・`REPORT_LEDGER.md`・REPORT: 追記位置だけ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件を確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_60.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_60.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

単体安全確認(有料。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --stage probe
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --stage main --n-serious 5 --n-release 3 --budget-jpy 30
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --stage agg

再較正(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_05.py --rubric v7b --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_safety_control_04 --n 2 --budget-jpy 12
(引数名は`_05.py`の実装に合わせる。無ければ`_06.py`として追加し、同じ出力先に書く。)

順序: 作業1 → 2 → 3 → 5(テスト・回帰) → 1回目commit/push → 4(単体確認) → 5(再較正) → 6(SSOT) → 2回目commit/push。単体確認でSTOP条件に当たったら、その時点で2回目commit(結果とSSOT[STOPの記録])を行い報告。

## SSOT追記文

作業1・6のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、`CURRENT_SPEC.md`のOPEN-233節への追記)。`PM_GOVERNANCE.md`は編集しない。
- 1回目commit: `DECISION_LOG.md`、runner、runnerテスト、Stage 2 calibration/production、設計書(§0-2)、criteria doc、委任ログ`_60.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 判断D=案1(比較・方向・時期の機械判定の追加確認2回による解放、主体・数値・否定は決定論維持)を逐語記録し検証用runnerへ実装(既定OFF)、判定原則文をR3(e)へ整合(V7b)、動機の整理を文書反映(Production未変更)(委任_60)`
- 2回目commit: 単体確認スクリプトと結果、再較正結果、`CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、REPORT、設計doc。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 案1の単体安全確認【PASS/STOP】とV7b再較正【結果】を実施、CURRENT_SPEC等へ反映(自己修復機構本体はProduction未接続)(委任_60)`
- 各commit前に`git status --porcelain`で確認。競合・新規テスト失敗・再較正不合格は自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内、(2)実装の要点(対象判定・CONFIRMED規則の定数逐語・確認promptの要点・解放条件・相互作用対策)、(3)V7b差分逐語と動機の文書変更、(4)単体確認のケース別結果表(対象判定/CONFIRMED/確認2回の結果/解放/期待との一致)、費用、STOP条件への該当有無、(5)再較正の集計と合否、(6)テスト件数・回帰、(7)SSOT更新箇所、(8)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
