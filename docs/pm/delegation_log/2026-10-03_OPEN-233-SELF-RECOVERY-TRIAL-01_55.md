## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_55)。並行タスク: 委任_56(説明文混入12件の原因深掘りと複数対策案、read-only+新規doc+¥0再生。runner・SSOTを編集しない)。**SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`REPORT_LEDGER.md`/`CURRENT_SPEC.md`)と、runner・Stage 2モジュール・テストを編集するのは本委任だけ。**

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定(2026-10-03、2回目)の記録、「重大/軽微/問題なし」の線引きの正式採用(`APPROVED_FOR_PRODUCTION`)に伴う判定ルール・正解ラベル・Safety-critical登録・降格ルールの修正(検証用モジュール内)、再較正(有料・小規模)、runtime evidence、SSOT更新。
- 到達上限Status: 線引き=`APPROVED_FOR_PRODUCTION`(ユーザー決定)。**`PRODUCTION_WIRED`ではない**(Self-Recovery Flow自体がProduction未接続)。句読点差対策=`APPROVED_FOR_PRODUCTION`としてProduction配線時の必須構成要素の追跡(`OPEN-233-A1-PROD`)。次Trial(5記事×2レベル)・29件横断は開始しない。
- 禁止事項:
  - Production正式path(`er003*`、`er009*`、`er010*`、`er012*`、`er019*`)の変更禁止。編集対象は`er052_open233_*`(Trial/検証用)のみ。編集前に、編集するモジュールがProduction pathからimportされていないことを`git grep`で確認して報告する。
  - **数値・主体・否定・比較・時期の機械的な安全装置(`FLOOR_FLAGS`によるfloor、precheck、主体置換ガード)を緩めない。**
  - 「迷ったら重大」を外す代わりに判定を緩める方向へ原則文を広げすぎない(ユーザー基準の文言と3つの例に忠実に)。
  - 新しい仕様候補を勝手に追加しない。説明文混入12件の対策(委任_56の範囲)には触れない。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分に触れない。
- 費用上限: 上限¥15(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥530.0107、上限¥900。有料なのは作業4(再較正)だけ。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(ユーザー決定に基づく判定基準の文言・ラベル・降格条件の修正であり、新しい構造・処理フロー・検出方式・Safety処理の追加ではない。Fable判定。Production配線時に条件Cで併せてレビューする旨をSSOTに記す)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55.md`。**委任文は全文そのまま保存(要旨化・参照形式は不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文)

次の全文を`DECISION_LOG.md`末尾へ一字一句そのまま引用する(作業1)。

````
OPEN-233について、今回のユーザー判断を反映して残課題を処理してください。

重要：
**5記事 × Standard / Advanced = 計10本の次Trialはまだ開始しないでください。**
今見えている問題を先にすべて整理・対策し、その結果をユーザーが確認してから次Trialへ進みます。

## 1. `prices began to fall` の扱い

以下はユーザー判断確定です。

`Just after the charge plan disappeared, prices began to fall.`

→ **軽微な品質問題として許容。重大ではない。**

この判断を正式記録へ反映してください。

---

## 2. 「重大 / 軽微 / 問題なし」の新しい線引きは正式採用

今回、例1・例2を基準に作成した一般ルール案を、ユーザーは正式採用します。

正式な基準は以下です。

- **重大**
  - 英語学習者に事実関係の重大な誤解を与えるもの
- **軽微**
  - 事実関係の核心は保たれているが、表現の精度が少し落ちるもの
- **問題なし**
  - 確認済みFactから自然に導ける描写・推論で、新しい具体的事実を追加しないもの

例として、すでにユーザー判断済みの以下を必ず基準にしてください。

- `Also, some calls needed user information to continue.`
  → 軽微
- `They enjoyed AI's convenience, but a human was on the other end. They did not realize it.`
  → 問題なし
- `Just after the charge plan disappeared, prices began to fall.`
  → 軽微

この線引きを正式仕様として扱い、現在の判定ルール・正解ラベル・Safety-critical登録・降格ルール等と食い違う箇所を修正してください。

特に、

- 条件付き→断定を一律Majorにしない
- 自然な推論は否定形だけでなく肯定形も許容
- 「迷ったら重大」に機械的に寄せず、重大な誤解になるかで判断

という方向へ合わせてください。

ただし、数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に勝手に緩めないでください。

この項目のStatusは、
**APPROVED_FOR_PRODUCTION**
です。

必要な再較正・テスト・runtime evidence・SSOT更新等が終わるまでは`PRODUCTION_WIRED`ではありません。

---

## 3. 句読点差22件の対策

この件について前提を明確にします。

句読点差対策を、現在の既存Productionへ単独で差し込む話ではありません。

今回開発している、

**Checkerの指摘箇所を記事本文へ照合し、その場所だけを最小Rewriteする自己修復機構**

をProductionへ接続するときに、

**その照合処理の一部として句読点差対策も必ず一緒に入れる**

という方針です。

つまり、

Checker指摘
→ 記事本文で該当箇所を特定
→ 末尾の句読点差を吸収して照合
→ 最小範囲Rewrite

です。

既存検証では、

- 346件再生
- 22件解消
- 悪化0

まで確認済みです。

したがって、この句読点差対策は
**自己修復機構のProduction配線時の必須構成要素**
として正式に追跡してください。

Production接続時にこの対策が抜けていた場合は`PRODUCTION_WIRED`としないでください。

---

## 4. Checker説明文混入12件は見送らない

今回の分離形式Trialでは、

- 原文位置の特定は改善
- しかしCheckerの重大事実検出が低下
- false PASSが増加

したため、その方式自体は不採用で問題ありません。

ただし、

**「1案試してうまくいかなかったので、この問題自体を見送る」**
という結論にはしないでください。

この問題は原因がかなり見えているため、引き続き対策を検討してください。

---

## 5. 説明文混入12件について、原因を改めて深掘りする

今回の結果を前提に、もう一度原因を掘り下げてください。

最低限、以下を切り分けてください。

- なぜ10件は出力形式起因だったのか
- なぜ2件はPrompt起因だったのか
- Checkerが「違反箇所」と「理由」を混ぜて出す具体的なパターン
- 初回CheckerとRecheckで混入の仕方が違うか
- どの処理段階で記事原文と説明文を安全に分離できるか
- 分離に必要な情報はすでにChecker出力内に存在しているか
- CheckerのPromptやSchemaを変えずに解決できる可能性
- 後段で決定論的に処理できる範囲
- 一意に確定できない場合のfail-safe

単に「別方式を試す」ではなく、
**なぜ前回方式で検出性能まで落ちたのか**
を、Prompt差・Schema差・実際の出力差から具体的に説明してください。

---

## 6. 対策案は複数案を出すこと

こちらから一つの候補案を提示しますが、これをそのまま採用しないでください。

### 候補案
**Checker自体の検出Prompt・判定方法・出力Schemaは変えず、後段で記事原文部分と違反理由を分離する。**

例えば、

- Checkerは今までどおり問題箇所・問題内容・理由を出す
- 後段で記事本文に完全一致する引用部分を抽出
- 句読点差だけなら承認済みの句読点吸収を使う
- 記事内で一意に1箇所確定できる場合だけ採用
- 似ている文をAIで再推測しない
- 一意に確定できなければ勝手に近い文を選ばない

という方向です。

ただし、これは**あくまで一つの候補案**です。

Claude側でも今回の原因分析から、
より単純・安全・低コスト・再現性の高い対策がないか、別案を必ず検討してください。

比較軸は最低限、

- Checkerの検出性能を落とさないか
- false PASSを増やさないか
- Human Reviewを増やさないか
- 不要Rewriteを増やさないか
- 再推測による誤範囲選択を起こさないか
- 実装が複雑化しすぎないか
- 初回 / Recheck / retry / fallbackで整合するか
- コスト
- 非決定性

です。

---

## 7. この件は必ずOpusレビューを入れる

Checker説明文混入12件の対策については、
**必ずOpusの独立技術レビューを実施してください。**

レビュー対象は、

- 原因分析が十分か
- 前回失敗方式の原因説明が妥当か
- 候補案の比較が十分か
- より単純な代替案がないか
- Checkerの検出性能を変えずに解決できないか
- 後段で安全に分離できる範囲はどこまでか
- fail-safeが妥当か
- 初回 / Recheck / retry / fallbackで矛盾しないか
- QCD上の妥当性
- Production wiring時のリスク

です。

**Opusレビュー後、Claude自身がレビュー内容を再評価してください。**

Opusの意見をそのまま採用せず、

- ユーザー判断
- OPEN-233の目的
- 新しい重大/軽微/問題なし基準
- 最小Rewrite原則
- Human Reviewを非常口にする方針
- QCD

と照合して再検討してください。

---

## 8. ユーザー提示前に必ず再検討する

Checker説明文混入12件については、

原因分析
→ 複数対策案
→ Claude比較
→ Opusレビュー
→ Claude再評価

まで実施してください。

その後、

**ユーザーへ最終候補を提示する直前に、もう一度「本当に見送り以外の合理的な手段を十分検討したか」を自己点検してください。**

1案失敗だけを理由に見送りを提案しないでください。

見送りを提案してよいのは、

- 原因が依然として特定不能
- 妥当な複数案を比較しても安全性・品質が改善しない
- 副作用が大きい
- QCD上、追加対策が合理性を失う

等の根拠がそろった場合のみです。

---

## 9. 英語だけ修正する方針

既存ユーザー方針を維持します。

Ledgerとの差異が英語側にあるなら、原則として英語だけ修正してください。

- 日本語本文へ遡って同時修正しない
- 日英整合のためだけに処理を複雑化しない
- 日本語タイトルは変更なし前提

ただし、古い日本語から英語を再生成するProduction経路については、再生成後のCheckerで必ず再検査されることを接続仕様へ明記してください。

---

## 10. 次Trialはまだ開始禁止

将来の次Trialは、

**5記事 × Standard / Advanced = 計10本**

を予定しています。

ただし、まだ開始しないでください。

以下をすべて整理・対策し、ユーザー確認後に開始します。

- 新しい線引きへの判定ルール再較正
- `prices began to fall`の軽微反映
- 説明文混入12件の原因再分析
- 複数対策案比較
- Opusレビュー
- Claude再評価
- 必要な限定確認
- 句読点差22件を含む自己修復機構の整合
- 英語だけ修正する構造の確認
- 未解決USER_DECISION_REQUIREDの整理

**29件横断も勝手に開始しないでください。**

今回の作業が終わったら、
何が解決したか、何が未解決か、次Trialへ進める状態かを報告してSTOPしてください。

## 11. Status / Gate

今回到達してよいのは、

- 線引き：APPROVED_FOR_PRODUCTIONの実装・再較正準備
- 句読点差対策：APPROVED_FOR_PRODUCTIONとしてProduction配線対象の追跡
- 説明文混入対策：Trial / USER_DECISION_REQUIREDまで

です。

ユーザー承認なしに、
説明文混入対策をProduction採用しないでください。

また、次Trialへも進まないでください。
````

## 作業1: ユーザー決定の記録

1-1. `DECISION_LOG.md`末尾に新エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-03、ユーザー決定[2回目]: `prices began to fall`は軽微/線引きの正式採用=`APPROVED_FOR_PRODUCTION`/句読点差対策は自己修復機構のProduction配線時の必須構成要素/説明文混入12件は見送らない・原因深掘りと複数案・Opusレビュー必須/英語だけ修正を維持・再生成経路は再検査を接続仕様に明記/次Trial・29件横断は開始禁止)」を追記し、上の原文を全文逐語で引用する。続けて「Fableの受け止めと分担」: 委任_55(本委任)=線引きの反映・再較正・A1-PROD追跡の更新・英語だけ修正の接続仕様メモ、委任_56=説明文混入の原因深掘りと複数案(その後Opusレビュー→Fable再評価→ユーザー提示)。
1-2. `docs/pm/ACTIVE_TASK.md`固定ヘッダのStatusを「IN_PROGRESS(ユーザー決定反映中、次Trial・29件横断は開始禁止)」に更新(addしない)。

## 作業2: 正解ラベル・Safety-critical登録・線引き文書の更新(¥0)

2-1. `docs/pm/open233_materiality_criteria_2026-10-03.md`に「正式採用(2026-10-03、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)」の節を追加し、ユーザー原文の正式基準(重大/軽微/問題なし の3定義と3つの例)を逐語で載せ、Fable案との対応(Fable案はこの3定義の具体化として維持。ただし「迷えば実害で決める」はユーザーの「『迷ったら重大』に機械的に寄せず、重大な誤解になるかで判断」で置き換える。機械的な安全装置は不変)を書く。委任_51の指摘7点それぞれに「正式採用後の扱い」を1〜2行で付ける。
2-2. `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`のK19の新判定を「軽微(ユーザー決定2026-10-03)」に改め、集計を更新する(真の重大見逃し0/23、軽微9/23。20種類換算も更新)。既存の判定文は消さず「旧: 重大(境界)」として残す。
2-3. 設計書`docs/pm/design_open233_self_recovery_flow_01.md`の正解ラベル表(Grep `正解ラベル`、`Meta-1`、`A2A3`、`B4-a`、`7-1`)を更新: Meta-1/Meta-2(MUSE-HC-010)=QUALITY(ユーザー決定)、MUSE-HC-012「They enjoyed…」=ACCEPTABLE(ユーザー決定)、HF-009「prices began to fall」=QUALITY(ユーザー決定)、その他は再分類docの新判定に合わせる(K05〜K07=QUALITY、K11〜K13=ACCEPTABLE/QUALITY等。再分類docの表を正とする)。旧ラベルは「旧: …(〜2026-10-02)」として残す。更新箇所の行番号を報告。
2-4. runnerの`SAFETY_CRITICAL_CLAIM_DEFS`: Meta-1/Meta-2を「Safety-critical」から外す。削除ではなく、期待ラベル(`expected: "QUALITY"`等)を持たせて「過剰品質の監視用」として残す形が既存構造で可能ならそうする(不可なら削除し理由を報告)。`detect_safety_critical_misdowngrades`と`residual_at_pass`(委任_49)の対象から外れることを確認し、テストを更新。

## 作業3: 判定ルールの修正(検証用Stage 2モジュール、最小変更)

対象はStage 2(`er052_open233_self_recovery_stage2_production_01.py`の`MATERIALITY_RUBRIC` 37〜46行付近、`er052_open233_self_recovery_stage2_calibration_01.py`の`MISCONCEPTION_PRINCIPLE_TEXT_V4`[V5・V6に含まれる]、runnerの`apply_disclosure_gap_downgrade`[2141行付近]と`DISCLOSURE_GAP_NEGATION_RE`)。**編集前に、これらがProduction path(`er003*`〜`er019*`)からimportされていないことを`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`で確認する。**

委任_51が特定した不整合4箇所を、次の方針で直す(新しい原則文の版名は既存の命名規則に従い`V7`等とし、旧版は定数として残す。Stage 2のPromptに使う版を切り替える):
3-1. **条件つき→断定(V4原則文)**: 「一律BLOCKING」をやめ、「Ledgerが条件つき・可能性・懸念として書く内容を記事が発生したこととして書く場合、**被害・結果にあたる核心の主張**まで断定している、またはLedgerに無い新しい具体的事実(人物・出来事・発言・数値)を加えている、またはLedgerの`notes_for_writer`が明示的に禁じる断定をしている場合はBLOCKING。核心の主張に留保が残り帰属が保たれている場合はQUALITY(例: 『some calls needed user information to continue』は、共有が『might』で留保され、懸念の主体がMeta従業員のままなのでQUALITY)」とする。
3-2. **自然な推論の肯定形**: 決定論的な降格(`DISCLOSURE_GAP_NEGATION_RE`、否定形限定)は**変更しない**(正規表現を肯定形へ広げると範囲が定まらないため)。代わりにrubric本文へ「開示がなかった等の確認済み事実から自然に導かれる利用者の状態・認識・反応の描写(否定形『気づかなかった』も肯定形『AIだと思っていた』『楽しんでいた』も)は、新しい具体的事実を加えなければACCEPTABLE」を追加する(例: 『They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.』=ACCEPTABLE)。
3-3. **「迷えばBLOCKING」**: 「判断に迷う場合は、読者(英語学習者)がこの文を信じたときに事実関係の重大な誤解につながるかで決める。つながるならBLOCKING、つながらないならQUALITY。数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり機械的にBLOCKINGとする」に置き換える。
3-4. **「動機の帰属=QUALITY」**: 変更しない(新しい基準の「新しい具体的事実の追加」に当たる動機の創作は3-1の文で拾える。食い違いの残りは報告に記す)。
3-5. 3つの例(例1=QUALITY、例2=ACCEPTABLE、K19=QUALITY)を、rubricの例示として最小限(各1行)で載せる。委任_16 B-2のprompt primingの前例(例示リストの追記でSafety-critical誤降格)があるため、例示は3行までに留め、作業4で誤降格0件を確認する。
3-6. Hook専用rubric(V3)は変更しない。`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`は変更しない。
3-7. 変更前後の原則文・rubric文の差分(逐語)を報告とruntime evidence(作業4の出力ディレクトリ内`rubric_diff.md`)に残す。

## 作業4: 再較正(有料、Guardrail ¥15)

既存の較正スクリプト(`er052_open233_element_trial_safety_control_02.py`、設計書§4-21・§7-0-iter29の方式。Grep `safety_control`で所在確認)を踏襲した新スクリプト`er052_open233_element_trial_safety_control_03.py`で、新しいrubric(V7等)をStage 2単体に当てる。
- 較正セット: (a)Safety-critical claim(更新後の定義。A5-1・Meta-1/2除外後)全件=期待BLOCKING、(b)Safety12(er009の9フラグ)=期待BLOCKING、(c)Hormuz許容5/NG5=期待どおり、(d)新しい例3件=例1 QUALITY・例2 ACCEPTABLE・K19 QUALITY、(e)再分類docで重大(見逃し0)とした種類(A2A3-0の支払い主体、B4-aの動機創作、K16)=期待BLOCKING、(f)負例(neg1_meta_b3prod_a2のACCEPTABLE期待claim)から3件。入力は既存の較正セットの保存済みclaim・Ledger・記事文脈をそのまま使う(新しいChecker呼び出しはしない)。
- n=2。Stage 2単価は既存実測(設計書§4-21: 8claim+Safety12+Hormuz10でn=2が¥4.94)から見積もり、先に(d)の3件×n=1を実行して単価を確認し、全体が¥15を超える見込みならn=1に落として報告する。
- 合否(Fableが判定するための基準): (a)(b)(e)でmisdowngrade 0件、(c)で従来と同じ、(d)が期待どおり(n=2の両方)、(f)でfalse BLOCKが従来より増えない。1件でも外れたら、原因と原則文のどの文が効いたかを示し、**修正を重ねずに報告して止まる**(修正はFable判断)。
- runtime evidence: `er052_output/open233_safety_control_03/`に、各claimの入力・出力・判定・費用、`rubric_diff.md`、集計`results_01.json`を保存。

## 作業5: テスト・回帰

- runnerとStage 2のテストを更新(ラベル変更、rubric版の切り替え、例3件の期待値、既存のSafety-critical検出テストが新定義で通ること)。
- `python -m unittest er052_open233_self_recovery_flow_runner_01_test_01`、Stage 2関連のテスト(Grep `stage2`で`*_test_*.py`を特定)、er052回帰、プロジェクト全体回帰(既存の失敗11件以外に新規なし。回帰後に`budget_state_c233an_42_rep22.json`等の書き換えがあれば`git checkout`で戻す)。

## 作業6: SSOT更新

6-1. `CURRENT_SPEC.md`: OPEN-233関連の節(Grep `OPEN-233`、`Self-Recovery`)に「重大/軽微/問題なしの線引き(2026-10-03ユーザー正式採用、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)」として、ユーザー原文の3定義と3例を逐語で、適用先(Stage 2判定・正解ラベル・Safety-critical登録)、機械的な安全装置は不変であること、再較正の結果(作業4の数値)、Production配線時に条件Cレビューで併せて確認することを追記する。既存節の末尾に追加し、既存文は編集しない。該当節が無ければ、`OPEN-233-A1-PROD`の案文(`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md` A-3の(5))が指す位置の次に新設する。
6-2. `OPEN_ITEMS.md`: OPEN-233行のStatusを「ユーザー決定反映中(2026-10-03、委任_55): 線引き`APPROVED_FOR_PRODUCTION`(再較正【結果】)、K19=軽微、真の重大見逃し0/23。説明文混入12件は委任_56で原因深掘り・複数案→Opusレビュー予定。次Trial・29件横断は開始禁止。`PRODUCTION_WIRED`ではない。」に更新(旧Statusは「旧Status参考(委任_54)」として残す)。`OPEN-233-A1-PROD`行: 本文を「自己修復機構(Checker指摘→記事本文で該当箇所を特定→末尾の句読点差を吸収して照合→最小範囲Rewrite)のProduction配線時の必須構成要素。抜けていた場合は`PRODUCTION_WIRED`としない(ユーザー決定2026-10-03)」に合わせて更新し、「既存Productionへ単独で差し込む話ではない」を明記。次Actionセルに「英語だけ修正の接続仕様: 古い日本語から英語を再生成するProduction経路(er012_e L361・365・403〜404/er019 entertainment runner L358〜397)は、再生成後のChecker(`run_deviation_check`)で必ず再検査されることを接続仕様に明記(ユーザー決定2026-10-03)」を追記。
6-3. `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考: 「2026-10-03 委任_55: 線引き正式採用(`APPROVED_FOR_PRODUCTION`)の反映・再較正【結果】。」
6-4. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §39: 作業1〜6の内容(rubric差分の要点、再較正の集計表、ラベル更新一覧、Production未変更の確認結果)。
6-5. 設計書`docs/pm/design_open233_self_recovery_flow_01.md`に§4-23「線引きの正式採用に伴うrubric V7(2026-10-03)」を追記(§4-21・§4-22の次。差分と再較正結果)。

## 事前指定Read一覧

- `docs/pm/open233_materiality_criteria_2026-10-03.md`: 全文(自分が更新する対象。前回作成分)。
- `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`: K19の節と集計節(Grep `K19`、`集計`)。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `正解ラベル`、`Meta-1`、`4-21`、`4-22`、`7-0-iter29`、`safety_control` → 該当範囲だけ(全文Read禁止)。
- `er052_open233_self_recovery_stage2_production_01.py`: 28〜90行、Grep `MATERIALITY_RUBRIC`、`MISCONCEPTION_PRINCIPLE`。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `MISCONCEPTION_PRINCIPLE_TEXT_V4`、`V5`、`V6`、`RUBRIC_` → 定数定義の範囲。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS`、`detect_safety_critical_misdowngrades`、`residual_at_pass`、`apply_disclosure_gap_downgrade`、`DISCLOSURE_GAP_NEGATION_RE`、Stage 2のrubric版を選ぶ箇所(Grep `RUBRIC_R3`または`rubric_version`)。
- `er052_open233_element_trial_safety_control_02.py`: 全文(踏襲元。構造把握目的)。
- `CURRENT_SPEC.md`: Grep `OPEN-233`、`Self-Recovery` → 該当節の範囲だけ(全文Read禁止)。
- `OPEN_ITEMS.md`: Grep `OPEN-233` → 該当行。`DECISION_LOG.md`・`REPORT_LEDGER.md`・REPORT: 追記位置だけ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。
- `git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件を確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55.md_check.json

テスト:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

再較正(有料。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_03.py --stage probe
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_03.py --stage main --n 2 --budget-jpy 15
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_03.py --stage agg

順序: 作業1 → 2 → 3 → 5(テスト・回帰)→ 1回目commit/push → 4(再較正)→ 6(SSOT)→ 2回目commit/push。

## SSOT追記文

作業1・6のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md` OPEN-233行・OPEN-233-A1-PROD行、`REPORT_LEDGER.md` OPEN-233行、`CURRENT_SPEC.md`の指定節への追記のみ)。`PM_GOVERNANCE.md`は編集しない。
- 1回目commit: `DECISION_LOG.md`、runner、runnerテスト、Stage 2モジュール2点、Stage 2テスト、`docs/pm/open233_materiality_criteria_2026-10-03.md`、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`、設計書、委任ログ`_55.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 2026-10-03ユーザー決定(2回目)を逐語記録、重大/軽微/問題なしの線引きを正式採用(APPROVED_FOR_PRODUCTION、未配線)として正解ラベル・Safety-critical登録・Stage 2 rubricへ反映(機械的な安全装置は不変、Production未変更)(委任_55)`
- 2回目commit: `er052_open233_element_trial_safety_control_03.py`、`er052_output/open233_safety_control_03/`配下、`CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、REPORT。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 線引き正式採用後のStage 2再較正を実施しruntime evidenceとSSOTへ反映、A1-PRODを自己修復機構配線時の必須構成要素として更新(委任_55)`
- 各commit前に`git status --porcelain`で確認。並行の委任_56はcommitしないので競合は想定しないが、`git push`が拒否されたら`git fetch`→fast-forward mergeのみ。競合・新規テスト失敗・再較正の不合格があれば自動解決せず報告して止まる。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内、(2)Production非依存の確認結果(`git grep`)、(3)ラベル更新一覧(旧→新)、(4)rubric差分の逐語、(5)再較正の集計表と合否基準への当てはめ(判定はFable)、費用(今回・累計・残)、(6)テスト件数・回帰、(7)SSOT更新箇所(行番号)、(8)ユーザーへ戻す条件(機械的安全装置の変更が必要になった/再較正で外れた/Production変更が必要)に当たる事実の有無、(9)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
