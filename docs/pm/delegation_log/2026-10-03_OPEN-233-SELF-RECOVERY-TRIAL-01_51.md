## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_51)。並行タスク: 委任_52(句読点差対策のProduction反映準備・日本語本文の実害整理、read-only+新規doc)と委任_53(説明文混入12件の対策とTrial Prompt実装・限定確認、runner編集+有料)が同時に動く。**SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`REPORT_LEDGER.md`)を編集するのは本委任だけ**(他2つは編集しない)。本委任はrunner・テスト・Promptを編集しない。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定(2026-10-03)の記録と、「重大/軽微/問題なし」の線引きの補正、見逃し候補の再分類(read-only分析+文書作成)。
- 到達上限Status: なし(OPEN-233の`USER_DECISION_REQUIRED`は解除され「ユーザー判断反映・次工程進行中(次Trial開始禁止)」になる。`VALIDATED`ではない。Production採用ではない)。
- 禁止事項: コード・Prompt・テストの編集禁止。LLM/TTS/ASR呼び出し禁止(¥0)。Production正式pathの変更禁止。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`の編集禁止。`git add -A`/`stash`/`amend`禁止。既存の未commit差分に触れない。線引きの文言(下記)を黙って変えない(無理・矛盾があれば「Fable案への指摘」節に書く)。
- 費用上限: ¥0(API呼び出しなしのためT-3は対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(ラベル基準の文書化と再分類。構造変更なし)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51.md`。委任文は全文そのまま保存(圧縮・参照形式不可)。一時ファイルはリポジトリ外(`%TEMP%`配下に作業用フォルダを作る)。

## ユーザー指示(原文)

次の全文を、`DECISION_LOG.md`末尾へ**一字一句そのまま**(見出し・強調記号・改行を含めて)引用して記録する(作業1)。

```
OPEN-233について、今回のユーザー判断を反映して次工程へ進んでください。

重要：
**5記事 × Standard / Advanced = 計10本の次Trialは、まだ開始しないでください。**
今見えている問題を先にすべて潰し、その結果をユーザーが確認してから次Trialへ進みます。

## 1. 重大 / 軽微 / 問題なし の線引きを更新する

以下2件について、ユーザー判断が確定しました。

### 例1
`Also, some calls needed user information to continue.`

→ **重大ではない。軽微な品質問題として許容。**

### 例2
`They enjoyed AI's convenience, but a human was on the other end. They did not realize it.`

→ **問題なしとして許容。**

この2件だけを例外扱いしないでください。

この2件を具体的な基準例として、
**「重大 / 軽微 / 問題なし」の線引き自体を補正**してください。

その上で、これまで「見逃し候補」とされていた残り18種類を、改めて再分類してください。

最低限、各種類について、

- 原文
- Ledger上の事実
- 旧判定
- 新判定
- 新判定の理由
- 本当に重大な誤解になるか

を示してください。

再分類後、

- 過剰品質：x/20
- 真の重大見逃し：a/20
- 軽微：b/20
- 問題なし：c/20

のように全体を数値で出してください。

**真のMajor見逃しだけが、その後の対策対象です。**

## 2. 真のMajor見逃しが残った場合だけ、原因分析＋対策

再分類の結果、本当に重大なのに後の周回まで拾えていないものが残った場合のみ、原因を切り分けてください。

最低限、

- 1周目で完全に見逃したのか
- Minorとして拾ったが後でMajorになったのか
- Rewriteによって新たに問題が発生したのか
- Checkerと判定役で基準が食い違っているのか

を確認してください。

そして原因ごとに、

**原因分析だけで終わらず、対策設計 → 必要な検証用実装 → 限定確認まで**
進めてください。

ただし、Safety原則の変更や新しいProduct原則が必要ならSTOPしてUSER_DECISION_REQUIREDです。

## 3. 日本語本文は原則修正しない方向で整理する

ユーザー方針：

**LedgerとのDeviationが英語側にあるなら、英語だけ修正する。**

日本語本文は、エンターテイメント性のある英語記事を作るための手段です。

したがって、

- 英語のDeviation修正のために日本語本文へ遡らない
- 日本語側の対応箇所を推測して同時Rewriteしない
- 日英整合を取るためだけに処理を複雑化しない

方向で設計を整理してください。

日本語タイトルも、
**英語本文の最小修正で変更する前提にはしません。タイトル変更なし前提**です。

確認すべきなのは、

**日本語本文を直さないことで後続処理に実害があるか**

だけです。

実害がある場合は具体的なProduction経路を示してください。
単に「整合を保ちたい」だけなら対策不要です。

## 4. Checker引用の特定不能35件について

既存調査では、

- 22件：末尾の句読点差
- 12件：Checker自身の説明文が違反箇所に混入
- 言い換え：0件

でした。

### 4-1. 末尾の句読点差22件

検証では、

- 既存346件で再生
- 22件解消
- 悪化0

を確認済みです。

この対策は、ユーザーとして**正式採用してよい意向**です。

したがって、Trial/DEV専用に残さず、Production正式経路への反映対象として追跡してください。

ただし、`PRODUCTION_WIRED`と判断するのは、既存Gateどおり、

- Production初回経路への実装
- retry / fallback / regenerationとの整合
- runtime evidence
- 必要test PASS
- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Git反映

まで完了してからです。

**「Trialでは直っていたがProductionへ入れ忘れた」状態を禁止します。**

### 4-2. Checker説明文混入12件

次工程で、

**原因調査だけでなく、対策検討・必要なら実施・確認まで**
行ってください。

最低限、

- 12件それぞれで何が混入したか
- なぜ違反箇所フィールドへ説明文が入ったか
- Prompt起因か
- 出力形式起因か
- 後段処理起因か

を分類してください。

有力案として、

**違反箇所フィールドには記事原文だけを入れ、説明・理由は別フィールドに分離する**

方式を検討してください。

必要なら検証用Prompt/出力形式で限定確認して構いません。

確認項目：

- 特定不能率が下がるか
- 検出漏れが増えないか
- false PASSが増えないか
- Human Reviewが増えないか
- コストが悪化しないか

## 5. 受け渡し修正

すでに実施した、

- Checkerが示した範囲を後段で再推測しない
- 複数文なら複数文のまま渡す
- 範囲を勝手に縮小しない
- 最小修正優先

という方針は維持してください。

Rewrite範囲は既存ルールどおり、

**語句だけで直せるなら語句だけ**
→
文が不自然 / 違反未解消なら文全体
→
それでも足りない場合のみさらに広げる

です。

最初から文全体Rewriteへ広げないでください。

## 6. 次Trialはまだ開始禁止

将来の次Trialは、

**5記事 × Standard / Advanced = 計10本**

程度で行う予定です。

ただし、これは**まだGOではありません。**

以下がすべて整理されてから、ユーザー確認を挟んで開始します。

- 残り18種類の再分類完了
- 真のMajor見逃しがあれば対策完了
- 日本語本文を直さない設計整理完了
- Checker説明文混入12件の対策整理・必要な確認完了
- 句読点差22件のProduction反映計画/追跡明確化
- その他の未解決USER_DECISION_REQUIREDなし

勝手に10本Trialへ進まないでください。

## 7. 予算

ユーザー判断：

Trial予算を**+¥300**追加します。

従来上限¥600
→ **新上限¥900**

ただし、予算は使い切る目標ではありません。

不要な、

- 再測定
- 全文Recheck
- 不要Rewrite
- 同じEvidence取得
- 惰性的retry

は禁止です。

## 8. Opusレビュー

今回の対策で新しい構造変更が発生する場合は、正式採用済みのOpus独立技術レビューGateに従ってください。

すでにレビュー済みで内容が変わっていない部分は、重複レビュー不要です。

ただし、

- Checker出力構造の変更
- 新しい検出方式
- 新しいSafety処理
- 新しいProduction経路

などを追加する場合は、必要条件に該当するか必ず判定してください。

## 9. 今回のSTOP地点

今回進めてよいのは、

- 18種類再分類
- 真のMajorが残れば対策＋限定確認
- 日本語本文を直さない設計整理
- 説明文混入12件の対策検討・必要な検証
- 句読点差22件の正式反映準備・Gate追跡

までです。

**5記事×2レベルの次Trialは開始しないでください。**

この段階で、

- 何が解決したか
- 何がまだ残るか
- USER_DECISION_REQUIREDが残るか
- 次Trialへ進める状態か

を報告してSTOPしてください。
```

## 作業1: ユーザー決定の記録(SSOT)

1-1. `DECISION_LOG.md`末尾に新エントリ「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-03、ユーザー決定: 線引きの補正・日本語本文は原則修正しない・句読点差対策の正式採用意向・説明文混入12件の対策・予算+¥300[上限¥900]・次Trial開始禁止)」を追記し、上の原文を全文逐語で引用する。続けて「Fableの受け止め」として: (a)`USER_DECISION_REQUIRED`は解除、(b)判断1=例1は軽微、判断2=例2は問題なし、判断3=予算上限¥900(Phase累計¥515.0181、残¥384.9819)、(c)次Trial(5記事×2レベル)は開始しない、(d)本委任_51〜53の分担、を記す。
1-2. `OPEN_ITEMS.md` OPEN-233行: Statusセルを「ユーザー判断反映・次工程進行中(2026-10-03、委任_51)。例1=軽微・例2=問題なしで線引きを補正、残りの見逃し候補を再分類中。予算上限¥900。次Trial(5記事×2レベル)は開始禁止(ユーザー確認後)。`VALIDATED`ではない。Production未接続。」に更新し、直前のStatusは「旧Status参考(委任_50)」として行内に残す。
1-3. `docs/pm/ACTIVE_TASK.md`の固定ヘッダのStatusを「IN_PROGRESS(ユーザー判断反映、次Trial開始禁止)」に更新(addしない)。

## 作業2: 線引きの補正(Fable案を文書化し、無理があれば指摘)

新規doc `docs/pm/open233_materiality_criteria_2026-10-03.md` に、次のFable案を書く。既存の原則(設計書`docs/pm/design_open233_self_recovery_flow_01.md` §0-2「重大誤解原則」、§4-21 V4原則[条件つき→断定]、§7-0-iter27[Brent→oil pricesの一般化は許容候補、2026-10-01ユーザー指示]、§7-0-iter29[A5-1 役職の一般化はQUALITY]、1228〜1246行[disclosure_gap降格]、Stage 2の`MATERIALITY_RUBRIC`[`er052_open233_self_recovery_stage2_production_01.py` 37〜46行])を各Grepで確認し、Fable案との**整合・不整合を表にする**。不整合は「Fable案への指摘」節に書く(勝手に直さない)。

**Fable案(線引き)**:

- **重大(BLOCKING)= 読者に事実関係の重大な誤解を与える**。該当: (1)数値・数量・規模の変更や創作、(2)主体・当事者の取り違え、(3)否定の反転、(4)因果・比較・時期の変更や創作、(5)Ledgerの`notes_for_writer`が明示的に禁じる断定(例: 「実際の大規模な情報漏えいが発生した」と断定)、(6)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値)の追加、(7)**被害・結果にあたる核心の主張**を、Ledgerが条件つき・可能性としか書いていないのに発生したと断定すること。
- **軽微(QUALITY)= 事実関係の核心は保たれているが、言い回しの精度が落ちている**。該当: (a)条件つき・可能性の内容を発生として書いているが、**被害・結果にあたる核心の主張には留保が残り、主体の帰属も保たれている**(例1: 「some calls needed user information」は断定だが、共有は「might」で留保、懸念の主体はMeta従業員のまま)、(b)対象の一般化で核心の主張が変わらないもの(Brent原油先物→oil prices、副社長→executive)、(c)語句の粗さ(肩書きの補い等、er003 533〜534行のMINOR規定に相当)。
- **問題なし(ACCEPTABLE)= Ledgerの事実から自然に導かれる描写・推論・物語的な導入で、新しい具体的事実を加えない**。該当: (i)開示がなかった等のLedger事実から導かれる利用者の状態・認識の推論(例2: 「They enjoyed AI’s convenience … They did not realize it.」。否定形・肯定形を問わない)、(ii)場面描写・導入(hook)で具体的な事実を加えないもの、(iii)同義の言い換え。
- **判定の順序**: まず重大の(1)〜(7)に当たるかを見る(1つでも当たれば重大)。当たらなければ軽微の(a)〜(c)。どれにも当たらなければ問題なし。迷う場合は、「読者がこの文を信じたとき、実害のある誤った行動・認識につながるか」で決め、つながるなら重大、つながらないなら軽微。
- **例1・例2から一般化した点**: 例1は(7)と(a)の境界を定める(核心の主張=「情報が共有された」。それが留保されていれば軽微)。例2は(i)を定める(既存の降格ルールは否定形に限定していたが、ユーザー決定により肯定形の推論[「驚いた」等]も、新しい具体的事実を加えなければ問題なし)。
- **既存の機械的な安全装置(数値・主体・否定・比較・時期のfloor、precheck)は変更しない。**

## 作業3: 見逃し候補の再分類

対象: 委任_46の見逃し型23種類(K01〜K23、`er052_output/open233_missed_detection_truth_check_01/cases_01.csv`・`results_01.json`、報告本文は`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46_result.md` §3)。ユーザーは「残り18種類」「/20」と書いているが、Fableの把握では、23種類のうち例1=K04、例2=K10、委任_46で判定済み=K02・K03・K11・K12・K13。**23種類すべてを新しい線引きで再分類**し、(a)全23種類の集計と、(b)ユーザーの「20」に対応づけた集計(例1・例2を含み、どの種類を数えたかを明記)の両方を出す。対応づけが一意に決まらなければ、その旨と候補を示す。

各種類について次を表にする(Ledger原文はCheckerが実際に見たLedger[監査JSONの`prompt`内、委任_46 A-1と同じ所在]から逐語で):
- 原文(英語記事の該当文、逐語)
- Ledger上の事実(該当factの本文・conditions・notes_for_writer、逐語)
- 旧判定(flow内でBLOCKINGになった根拠: LLM判定か、floorか、列挙の波及か。委任_44の`cases_detail_01.csv`の該当行)
- 新判定(重大/軽微/問題なし)と、線引きのどの項目に当たるか
- 新判定の理由(2〜4行)
- 本当に重大な誤解になるか(読者が信じたときの実害を1〜2行で)
- 見逃しの有無(新判定が重大の場合のみ: その文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終わった実行数、委任_46 B-2の値)

集計:
- 過剰品質(旧判定BLOCKINGだが新判定が軽微または問題なし)の種類数
- 真の重大見逃し(新判定が重大で、かつ見逃しが1実行以上)の種類数
- 軽微の種類数、問題なしの種類数
- 新判定が重大だが見逃し0の種類数(あれば)

**真の重大見逃しが1種類でもあれば**、その種類について次を記録から確認する(ユーザー指示§2): 1周目で完全に見逃したのか/MINORとして拾ったが後でMAJORになったのか(委任_49以降のrunはMINORを記録しているが、それ以前の記録にはMINORが無いので「確認不能」と書く)/Rewriteによって新たに発生したのか/Checkerと判定役で基準が食い違っているのか。対策の設計はしない(Fableが別途判断する)。

## 作業4: Stage 2の判定・既存ラベルへの影響の洗い出し(変更はしない)

新しい線引きと現在の実装・ラベルが食い違う箇所を列挙する(読むだけ): (1)設計書の正解ラベル表でMeta-1/Meta-2(MUSE-HC-010)がSafety-critical、runnerの`SAFETY_CRITICAL_CLAIM_DEFS`(Grep)にも登録、(2)Stage 2 calibrationの`MISCONCEPTION_PRINCIPLE_TEXT_V4`(`er052_open233_self_recovery_stage2_calibration_01.py`、Grep)が条件つき→断定をBLOCKING候補とする文言、(3)disclosure_gap降格が否定形に限定、(4)その他Grepで見つかるもの。各箇所について「新しい線引きとの差」「変更した場合に必要になる再較正(過去の較正セットと費用、設計書§4-21の¥4.94等)」を書く。**変更は行わない**(ユーザー指示は「真のMajor見逃しだけが対策対象」)。

## 事前指定Read一覧

- `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46_result.md`: §2〜§3(見逃し候補の表、Ledger所在)。
- `er052_output/open233_missed_detection_truth_check_01/cases_01.csv`・`results_01.json`: Pythonで必要行・キーだけ。
- `er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`: P2a/P2b行をPythonで抽出。
- 各記事のLedger: `er019_output/.../audit/deviation_checks/*.json`の`prompt`内(委任_46と同じ方法。所在は`check_01.py`を参照)。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `0-2`、`4-21`、`7-0-iter27`、`7-0-iter29`、`disclosure_gap`、`正解ラベル` → 該当範囲だけ(全文Read禁止)。
- `er052_open233_self_recovery_stage2_production_01.py`: 28〜86行。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `V4` → 該当範囲。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS`、`DISCLOSURE_GAP_NEGATION_RE` → 該当範囲だけ。
- `er003_v1_en_direct_vfl_01_generate.py`: 525〜541行(MINOR規定、読むだけ)。
- `OPEN_ITEMS.md`: Grep `OPEN-233` で該当行だけ。`DECISION_LOG.md`: 末尾の追記位置だけ。`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。
- `DECISION_LOG.md`末尾に追記。`OPEN_ITEMS.md` OPEN-233行のStatusセル更新(次Actionセルは触らない。委任_52・53の結果を受けてFableが後で更新する)。
- 新規doc 2点: `docs/pm/open233_materiality_criteria_2026-10-03.md`(作業2・作業4)、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`(作業3)。

## 実行コマンド全文

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51.md_check.json

テスト・回帰は不要(コード変更なし)。

## SSOT追記文

作業1に記載のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md` OPEN-233行Statusセルのみ)。
- 明示add対象: `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/open233_materiality_criteria_2026-10-03.md`、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`、`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51.md`、同`_check.json`。`ACTIVE_TASK.md`はaddしない。並行タスクのファイル(委任_52・53が作るもの、runner等)はaddしない。
- commit前に`git status --porcelain`で確認。コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 2026-10-03ユーザー決定(線引き補正・日本語本文は原則修正しない・句読点差対策の正式採用意向・予算上限¥900・次Trial開始禁止)を逐語記録、重大/軽微/問題なしの線引きを文書化し見逃し候補23種類を再分類(委任_51)`。`git push origin main`まで。並行タスクが先にpushしていた場合は`git pull --rebase`を使わず、`git fetch`後に`git merge origin/main`(fast-forwardのみ)を試み、競合やfast-forward不可なら報告して止まる。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内(集計の数値、真の重大見逃しの有無とその種類)、(2)Fable案への指摘(線引きの無理・矛盾、既存原則との不整合)、(3)再分類の表の要約(全23種類の新判定一覧と、「20」への対応づけ)、(4)真の重大見逃しがあればその原因切り分け、(5)作業4の一覧、(6)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
