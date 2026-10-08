## 管理ID

FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_04a: Prompt変種sweep[8〜10変種]の設計・harness・事前登録。**¥0・API課金なし・git操作なし**)。並行タスクあり: (1)同管理IDの委任_02b agent(盲検採点・集計中、書込先`er052_output/factlock_writer_trial_01/eval/`・`RESULT.md`・`MANIFEST.json`・`docs/pm/RESULT_PACKET_FACTLOCK.md`)、(2)同管理IDの委任_03 agent(診断、書込先`er052_output/factlock_writer_trial_01/v2_design/`・`docs/pm/RESULT_PACKET_FACTLOCK_V2.md`)、(3)`PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01`委任_03(Production配線・git commit中)。本委任はいずれのファイルにも書き込まない。

## 性質/到達上限Status/禁止事項

- 性質: Trial準備(sweep設計・harness・事前登録)。到達上限Status: `SWEEP_READY`(生成は委任_04bで、委任_02bの採点完了[`er052_output/factlock_writer_trial_01/RESULT.md`存在]後に開始)。
- 隔離規則(必須): 書込は `er052_output/factlock_writer_trial_01/sweep_01/` 配下、新規 `er052_factlock_sweep_01_run.py`・`er052_factlock_sweep_01_test_01.py`、`docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md`(新規)、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04a.md`(+`_check.json`)のみ。既存harness `er052_factlock_writer_trial_01_run.py` は**編集せずimportして再利用**(prompt注入点・タグ照合・タグ除去・6-luna差し替え)。SSOT・他のRESULT_PACKET・ACTIVE_TASK編集禁止。git禁止。有料API禁止(テストはmock)。Production code編集禁止。
- 費用: 本委任¥0。委任_04b見積は事前登録に記載(上限¥300、T-3定型文)。
- Opus独立技術レビューGate: 構造(タグ・照合・除去)は条件A済み。本sweepはprompt文言の探索でFableは任意レビュー(¥0)を並行で入れる予定。
- 時間見込み: ≈60〜75分(設計30分/harness+テスト30分/事前登録10分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は使わない(本委任ではgit操作禁止)。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ**全文**保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は課金なし。委任_04b向け定型文: 「上限¥300(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## ユーザー指示(原文)

「AIは禁止、誘導すると上手くいきません(特にエンターテイメント性については)。また指定を多くすると1パターン化します。これと1つに決め打ちせず、それこそ5でも10でもパターンを振って方向性を決めるのが良いと思います。やってみないとわからない世界です。時間重視で一回の評価で広く知見がえられる、方向性が決めれる、そのような評価を考えてください。」(2026-10-08)。前段: 「エンターテイメント性については全くNG」「事実固定(Fact Lock)は維持」「R0>R1>R2のPrompt変更」「Writerへのpromptを品質重視をキープしながら工夫」。

## KPI provenance欄

本委任は測定なし。委任_04bの指標: 面白さpairwise・照合指標・JA FC/STOP・盲検rubric=**fresh**(Trial harness)。比較対象「6×現行」「6×Fact Lock v1」=**reuse**(既存run)。E2E自己確認: No。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `er052_factlock_writer_trial_01_run.py` 全文(構造再利用のため全文Read可: prompt注入点[`CONCRETENESS_CONTROL_AN3_BLOCK`差し替え・`REVISION_INSTRUCTIONS`更新]、6-luna差し替え、タグ照合(i)〜(iv)、タグ除去、manifest)
- `er019_family_x_ja_writer_o_r1_r2_01.py` Grep `R0_PROMPT|REVISION_INSTRUCTIONS|CONCRETENESS_CONTROL_AN3_BLOCK|previous_response_id` →該当範囲Read(現行prompt原文と連鎖の仕組み。R1/R2へ渡す本文を差し替えられるか[連鎖を切って新規contextで渡す変種のため]を確認)
- `er052_output/factlock_writer_trial_01/DESIGN_01.md` §1〜§3(v1規則とv1の追記ブロック)
- `er052_output/factlock_writer_trial_01/eval/SUMMARY_FL.md` §3(pairwise負け理由)
- `er052_output/factlock_writer_trial_01/eval/FACTLOCK_CHECK_SUMMARY.md` 全文(v1の照合基準値)
- `er052_output/factlock_writer_trial_01/v2_design/DIAGNOSIS_01.md`(委任_03が作成中。**存在すれば**読み、負け理由分類・失われた要素を変種設計に反映。存在しなければ読まずに進め、その旨を記録)
- `er052_output/factlock_writer_trial_01/briefs/<slug>/b<i>/selected_brief_factlock.md` と `core_numbers.json`(対象brief 3本: meta b2、hormuz b4、space_weapons b3)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `def run_ja_writer_o_r1_r2|previous_response_id|input=` in `er019_family_x_ja_writer_o_r1_r2_01.py` → R1/R2の入力が「直前応答への連鎖」固定か、本文を明示的に渡す経路があるかを確定(変種「タグ除去済み本文をR1/R2へ新規contextで渡す」の実装可否)。不可なら当該変種はharness側で連鎖を切り、`input`にタグ除去済みR0本文+現行Revision指示を渡す形で実装(Production不変)。
- 追記位置: 新規 `sweep_01/DESIGN_SWEEP_01.md`、`sweep_01/variants.json`(変種ID→R0/R1/R2 promptブロック全文・連鎖方式・タグ有無)、`sweep_01/PREREGISTRATION_SWEEP.md`。

## 実行コマンド全文

cwd=`C:\Users\tensh\eigo-radio`、python=`.venv\Scripts\python.exe -X utf8`。

0. 委任文全文保存+検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04a.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04a.md_check.json`

1. 設計 `sweep_01/DESIGN_SWEEP_01.md`: **設計原則**(ユーザー指示に基づく): 禁止・誘導は最小、変種ごとに「変える軸」を1つに絞る(効いた軸を特定できるように)、規則の多い変種と少ない変種を両端に置く、「規則」ではなく「目標」で書く変種を含める、タグそのものの副作用を分離する変種を含める。**変種案(8〜10。以下をたたき台にし、Opus/診断を踏まえ調整可。各変種はR0/R1/R2ブロック全文を逐語で書く)**:
   - S0 参照=6×現行(既存24本から同brief、再生成しない)。
   - S1 現行+R0に出典タグ付与のみ(規則文なし。「事実を述べる文の末尾に【事実N】を付ける」の1文だけ)。→タグ自体の副作用を測る。
   - S2 S1+「ニュース欄にないことは書かない」1文のみ(R0のみ)。
   - S3 S2+数値規則(c)(R0のみ、短文化版)。R1/R2は現行のまま(無制約)。→R0だけ固めてReviseを自由にしたときの増幅量を測る。
   - S4 S3+R1/R2に「タグ付き文の事実は変えない。新しい事実文は足さない」の2文のみ。
   - S5 参照=Fact Lock v1(既存24本、再生成しない。規則最大の端)。
   - S6 R0を**事実の骨格**(タグ付き短文のみ、面白さを求めない、文字数上限小)にし、R1/R2は現行Entertainment指示そのまま+S4の2文。→「骨格→肉付け」構成。
   - S7 **目標形**: 規則を一切書かず、R0/R1/R2に目標文のみ(例: R0「読者がニュース欄の事実を正確に受け取れる記事」、R1/R2「友人に『これ、ちょっと面白くない?』と話すような読み物に。ニュース欄の事実はそのまま」)。タグはR0に付与。
   - S8 **連鎖切り**: R0はS3、R1/R2は直前応答への連鎖ではなく、タグ除去済みR0本文を新規contextで渡し現行Entertainment指示のみ(台帳もタグも見せない)。→タグ・規則が視界にない状態でReviseさせ、事後にタグ再付与(照合は(i)の文×主張分解で代替)。
   - S9 S4+R3追加(Entertainment Revisionを3回)。→回数の効果。
   - S10(任意) S4のR1/R2に「面白さの手段リスト」(禁止ではなく選択肢の列挙: 生活場面の仮定/対比/問いかけ/意外性のある導入/テンポ)を添える。→指定が1パターン化を招くかを測る。
   各変種に「仮説(何を学べるか)」「事実固定への影響見込み」「面白さへの影響見込み」を1行ずつ。
2. harness `er052_factlock_sweep_01_run.py`: `--variant <ID> --slug --brief-md --core-numbers-json --ledger-txt --out-dir --budget-jpy --yes-run-paid`。`variants.json`からR0/R1/R2ブロックと方式(連鎖/連鎖切り、タグ有無、R3有無)を読み、既存harnessの関数を再利用して注入。タグ無し変種では照合(i)(iv)を省略し(ii)(iii)のみ。S8は事後タグ再付与(LLM 1 call、6-luna)。manifestにvariant・prompt sha・方式を記録。単体テスト(mock): 全変種でprompt注入が意図どおり/連鎖切りの入力構成/Production module sha不変/dry-runでAPI呼び出しなし。`.venv\Scripts\python.exe -X utf8 -m pytest er052_factlock_sweep_01_test_01.py -q` PASS。
3. 事前登録 `sweep_01/PREREGISTRATION_SWEEP.md`(委任_04b用): 生成=8〜9変種(S0/S5は既存を参照)× brief 3本(meta b2、hormuz b4、space_weapons b3。テーマ3種×数値あり/なし)× 1反復 = 24〜27本、6-luna、Checker ON同構成、4並列。**1回の評価で方向を決めるための評価設計**: (a)面白さ=各変種記事を同briefの**S0(現行)とpairwise**(順序入替2回)+**変種同士の総当たりではなくS0基準の勝率**で並べる、加えて評価者LLMに「どの変種が1パターン化しているか(3記事間の構成・比喩・導入の類似度)」の所見を出させる、(b)事実=照合指標(タグあり変種: 不整合率・unsupported/記事、全変種: タグなし断定文(ii)・数値一致(iii))+JA FC must-fix/EN再生成/STOP+盲検rubric(重大/軽微、S0・S5の既存記事と同一パック・同一評価者で24〜27+6本)、(c)多様性=同変種3記事の導入文・比喩系統・結び方の異なり数(機械+LLM所見)。**判定の出し方(しきい値なし)**: 変種×{面白さ勝率, 軽微NG/記事, 不整合率, 多様性}の一覧表と、軸別の要約(タグの副作用はあるか/R0規則だけで事実は守れるか/R1/R2の2文制約は面白さを落とすか/骨格→肉付けは成立するか/目標形は規則形より良いか/連鎖切りは効くか/R3は効くか/手段リストは1パターン化を招くか)。費用見積(27本×≈¥5=¥135+pairwise≈¥30+照合≈¥40+盲検≈¥40 ≈¥245、上限¥300)。時間見込み(生成60分・評価40分・集計20分)。開始条件=`er052_output/factlock_writer_trial_01/RESULT.md`存在。

## SSOT追記文

本委任ではSSOT編集なし。RESULT_PACKET_FACTLOCK_SWEEPにDECISION_LOG追記文案(ユーザー指示: 禁止・誘導最小、変種sweepで方向決定、1回評価)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

**本委任ではgit操作禁止**。commit候補一覧(後続): `er052_factlock_sweep_01_run.py`、`er052_factlock_sweep_01_test_01.py`、`er052_output/factlock_writer_trial_01/sweep_01/**`、`docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md`、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04a.md`(+`_check.json`)。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md`を新規作成(ヘッダ: 管理ID・Status=SWEEP_READY・¥0・Production変更なし・git未操作)。本文: 1. 変種一覧表(ID・変える軸・仮説・R0/R1/R2ブロックの要約)と全文の所在。2. 連鎖切り(S8)の実装方式と制約。3. テスト結果。4. 評価設計の要点(1回で方向を決めるための表の形)。5. 委任_04bの開始条件・費用・時間。6. 診断(DIAGNOSIS_01)を反映できたか。7. 問題・残作業(blockingか明示)。8. check_delegation_prompt結果1行、一覧外Readの理由。推奨は書かず事実のみ。
