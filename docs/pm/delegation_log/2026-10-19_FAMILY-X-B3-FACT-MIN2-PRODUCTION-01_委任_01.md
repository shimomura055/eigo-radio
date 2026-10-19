# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_01(ユーザー2026-10-19指示原文保存+Family X B3 Fact選定「下限2件」の現行経路調査・最小変更設計・Regression案・中東記事再生成計画・費用見積。**Phase 1=read-only調査+文書、JPY0、Production変更なし**。実装はOpus条件Aレビュー後の委任_02以降)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 調査・設計文書(Phase 1)。コード変更0、有料API呼出0、`er019_output/middle_east_yemen_saudi/run_mey_01/`配下の変更0(読取のみ)。
- 到達上限Status: `B3MIN2_DESIGN_READY_PENDING_OPUS_A`。
- 禁止: Production・Prompt・Gateの変更/有料実行/B3の別方式新設や新品質基準の「採用」(候補列挙は可)/RLCT(er082)方式の混入/Research再実行/`run_mey_01`配下の編集・移動/Family A/B/Cへの変更。
- 固定ブロック: **E-1**(既存仕様・過去Trial照合: CURRENT_SPEC「B3」「Fact選定」「Fact Lock」「Select-then-Verify」「決定論B3」関連行、OPEN_ITEMSのB3/Fact選定関連項目(OPEN-416含む)、`docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01/E2E_PLAN_01.md` §12〜§15の事実(B3がF11のみを2回選定)、RLCT Trial最終報告(`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_FINAL_REPORT_01.md`)のB3選定数に関する記述を必ずGrepし、A(既存仕様あり)/B(過去Trialあり未採用)/C(真に新規)に分類)/**D-1**(本Phaseは不適用。方式はOpus後に決定)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentなし(ただし`.git/index.lock`があれば待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP)。`docs/pm/ACTIVE_TASK.md`は先頭に固定ヘッダ(PM_BRIEF「ACTIVE_TASK固定ヘッダ」書式、`QDC:`行・`承認済み指示:`行・`未回答報告:`行・`報告単位Status:`行を含む)を追記し旧ヘッダは`--- 旧ヘッダ ---`で残す)/**F-1**(JPY0。見積は既存実測単価を出典に: `E2E_PLAN_01.md` §13の再生成実費23.260(B3 6.673/W-1 R0-R2 14.264/Adv 0.343+RF 0.92/Std 0.270+RF 1.03)および`run_mey_01`配下の`raw_usage_log.jsonl`/cost記録)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_委任_01.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_XB3M1.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_USER.md`へ以下「# Claude Code／Fableへの指示」から「音声化は今回の作業範囲外とする。」までを原文のまま(1文字も変えず)保存し、文字数とsha256を報告)

# Claude Code／Fableへの指示
## Family X｜B3 Fact選定下限2件のProduction採用・中東記事再生成

### 1. ユーザー正式決定

**B3が記事に採用するFact数の下限を2件に変更する。**

Status：**APPROVED_FOR_PRODUCTION**

現行B3方式の採用数実績を踏まえ、最低2件のFactを選ぶ仕様を正式Production経路に適用する。

今回の目的は、必要なFactが過度に絞られ、ニュースの具体的内容が失われることを防ぐことである。

対象はFamily XのB3 Fact選定仕様。Family固有か共通仕様かを確認し、既存の承認済み仕様との整合を取る。

### 2. B3の新仕様

- B3は原則として、**検証済みFactから最低2件を採用する**。
- 初回選定で1件以下になった場合は、中心テーマに関連するFactを再評価し、2件以上を選定する。
- **数合わせのために、関連性の低いFactや未検証Factを追加しない。**
- 既存のFact検証、帰属、因果関係、時点、AMBIGUOUS取扱い、Fact Lock、安全条件を維持する。
- 下限2件を満たせない場合は、原因を記録してSTOPする。無制限のretryや、事実性を損なう補完は行わない。
- 原則として、既存のB3選定方式への最小限の変更で実現する。新たな品質基準や別方式を独断で追加しない。

### 3. Production実装と検証

正式初回Production経路だけでなく、B3のretry／regeneration／resume／再利用経路にも新仕様を適用する。

既存のFact選定Prompt・決定論B3 producer・Validator・下流Writerとの整合を確認し、必要十分な修正を行う。

Regressionでは少なくとも以下を確認する。

- 検証済みFactが十分にある場合、採用数は2件以上になる。
- 1件しか採用しない旧挙動は検出される。
- 2件採用の既存正常例は不要に変更されない。
- 無関係なFact・未検証Factを下限達成目的で採用しない。
- 下限未達時のSTOPが機能する。
- 既存のFact Lock、Writer、安全Gateが維持される。

### 4. 中東記事の再生成

対象：

`er019_output/middle_east_yemen_saudi/run_mey_01/`

**既存の検証済みFact Ledger（11件）を再利用する。Researchは再実行しない。**

新B3仕様に基づき、B3 Fact選定から下流の記事生成・必要なテキストQAまで、正式Production経路で再実行する。

- 採用Factは最低2件。
- 中心テーマは「イエメン周辺での攻撃と、それがサウジ・地域全体に与える影響」。
- 既存の検証済み事実のみを使用する。
- 攻撃主体が未確認の場合は断定しない。
- 事実性・中立性・具体性を維持する。
- 改善した採用Factが記事本文で実際に使用されていることを照合する。

**B3が2件以上を選んだだけで成功とは判定しない。** 記事がユーザーの意図したテーマを具体的に扱えていることも確認する。

### 5. 今回のSTOP位置

**音声化には進まない。**

今回は、記事生成とテキストQAが完了した時点で停止し、以下をユーザーへ提示する。

1. 新B3で選ばれたFact数
2. 採用FactのIDと、それぞれの具体的内容
3. 不採用FactのID（理由は重要なもののみ）
4. 前回とのFact選定差分
5. 再生成された日本語記事の全文
6. Standard／Advanced英文へのリンクと必要な確認結果
7. 記事が当初の狙いを満たしているかについてのFable評価
8. 実費・残予算・Production配線状況

**ユーザーが記事内容とFact選定を確認し、音声化を明示承認するまで、有料TTS・Assembly・試聴ページ生成へ進まない。**

### 6. QCD・費用管理

前回実費はJPY79.9／個別上限JPY180。

既存Ledger・生成物・検証結果を最大限再利用し、不要なResearch・再生成・重複検証を避ける。

原則1,000円／日（JST）と本案件の個別Capを遵守する。費用は累計で管理し、上限超過見込み・承認範囲外変更・明示STOP条件に該当する場合のみユーザーへ判断を求める。

改善作業で問題が発生した場合は、承認範囲内で原因調査・修正・再検証を自律的に進める。効果のない同一Trialを反復しない。

### 7. CloseoutとFable受入

- 新B3仕様の正式経路への配線、retry／regeneration／resume、runtime evidence、Regressionを確認する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新する。
- 必要なGit commit／pushを完了する。
- Fableがユーザー承認内容と実動作を独立照合する。
- 必須条件をすべて満たした場合のみ、新B3仕様をPRODUCTION_WIREDと判定する。
- **中東記事自体はユーザーの内容確認待ちで停止**し、Production仕様の配線完了と記事の品質承認を混同しない。

### 最終到達目標

**B3の採用Fact下限2件をProductionに恒久反映したうえで、中東記事を既存Factから再生成し、採用Factと記事全文をユーザーが確認できる状態にする。**

音声化は今回の作業範囲外とする。

## Fable指示(調査・設計の要件)
1. **現行B3経路マップ**: Family XのB3 Fact選定の正式経路を関数名:行で列挙する。対象=`er019_family_x_storyline_b3_fact_selection_01.py`(Prompt、選定ロジック、決定論producer、Validator、出力`fact_selection_evidence.json`の構造)、runner `er019_family_x_entertainment_production_runner_01.py`の`storyline_b3` stage(初回/`--regenerate-stage storyline_b3`/resume/再利用[U-1 PROVENANCE_MISMATCH]経路)、下流Writerが採用Factをどう受け取るか(Fact Lock・`verified_fact_ledger.txt`との関係)。「採用Fact数」を現在どこで決めているか(Promptの指示文/コード側の上限・下限/fact_tests=excludedの判定)を特定し、現状の下限(0件/1件?)と上限を明記。Family Z/Yや共通moduleに同じB3選定が存在するか(Family固有か共通か)を確認。
2. **実績確認**: 既存run(`run_mey_01`の`storyline_b3/fact_selection_evidence.json`[現行と`_before_regen_01/`]、および他のFamily X Production run、例: `er019_output/family_x_audio_production_wiring_01/*`、BAPE「退屈と攻撃性」run)で、B3が採用したFact数の実績表(run名/採用数/Ledger件数)を作る(read-onlyで取得できる範囲、推定値禁止)。
3. **最小変更設計(2案以上、原則「既存方式への最小変更」)**: 例=(案I)Prompt指示に「原則最低2件」+選定結果のValidatorで採用数<2ならB3のみ1回再選定(再評価指示: 中心テーマに関連するFactを再評価。数合わせ・未検証Fact追加禁止)、再選定後も<2なら理由記録+STOP(`FamilyX...Stop`相当の既存STOP機構を使う)/(案II)コード側Validatorのみで下限2を強制し、Promptは不変で再選定1回/(案III)I+II等。各案: 変更箇所(ファイル:関数)、Prompt変更の有無(Prompt変更=Production Gate対象であることを明記)、retry/regeneration/resume/再利用経路への反映点(各経路で下限が必ず評価されること)、Fact Lock・帰属・因果・時点・AMBIGUOUS・安全条件の不変性、下流Writerへの影響(Fact 2件以上を本文で使うか=Writer側の採用Fact使用照合の有無)、副作用(関連性の低いFactの混入リスクとその防止=既存のfact_tests/relevance判定の再利用)、費用影響(再選定1回あたりのJPY、出典=B3 6.673)、Regression設計(ユーザー§3の6項目を各テストにどう対応させるか: 十分Factあり→≥2/旧挙動1件検出/既存2件例の不変/無関係・未検証Factの不採用/下限未達STOP/Fact Lock・Writer・安全Gate維持。モックLLM応答で決定論的に確認できる設計)。各案を「承認済み範囲内(ユーザー§2に合致)」/「新品質基準(USER_DECISION_REQUIRED候補)」に区分し、推奨案と理由。
4. **中東記事再生成計画**: `run_mey_01`で既存Ledger 11件を再利用しB3から下流(writer→advanced→standard+テキストQA)を正式経路で再実行する正確な手順(E2E_PLAN §12の段階別`--stage X --regenerate-stage X`手順を踏襲、各1回)、旧成果物の退避(`_before_regen_02/`等、PM_GOVERNANCE 2-3 Artifact supersession)、STOPセンチネル・STOP_NOTICE(`run_mey_01`に`STOP`があるか確認し、あれば解除手順はFable権限=委任_02以降で指示)、Research再実行が起動しないことの保証(ledger sha不変の確認方法)、費用見積(出典付き: 前回再生成23.260+B3再選定1回分)、累計管理(前回79.881/180)。
5. **ユーザー提示物の準備計画**: ユーザー§5の8項目(採用Fact数/ID+内容/不採用ID/前回差分/日本語記事全文/Std・Adv英文リンク/Fable評価/費用・配線状況)を、再生成後にどのartifactから取るかの対応表。日本語記事全文はどのファイルか(Family Xの日本語記事成果物の有無を確認。英文のみなら「日本語記事」に相当する成果物を特定し、無ければその旨を事実として記録=推測で作らない)。GitHub Pagesでの英文リンク提示方法(試聴ページ生成は禁止=音声なしのテキスト確認ページが既存仕組みにあるか、無ければraw/blob以外の提示方法候補を列挙し、Fable判断に回す)。
6. **Opusレビュー観点案(条件A)**: 5件以内。
7. 文書: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-FACT-MIN2-PRODUCTION-01\B3_MIN2_DESIGN_01.md`(§1経路マップ/§2実績表/§3設計案と推奨/§4中東記事再生成計画/§5提示物対応表/§6 Opus観点/§7 E-1分類/§8費用見積)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py`(全体)
- `C:\Users\tensh\eigo-radio\er019_family_x_b3_production_wiring_01_test_01.py`(既存テストの範囲)
- `C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py` L230-470(reuse/U-1、`storyline_b3`/writer/advanced/standardの再生成分岐)
- `C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\storyline_b3\fact_selection_evidence.json` と `..\_before_regen_01\`配下の同名ファイル、`..\research_ledger\verified_fact_ledger.txt`(11件)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01\E2E_PLAN_01.md` §12〜§15
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md` 2-3節(Artifact supersession)・26節(STOPセンチネル)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `B3|Fact選定|Fact Lock|fact_tests|Select-then-Verify`→該当行番号を§7に記録(編集しない。仕様文の追記は実装委任で行う)。
- `OPEN_ITEMS.md`: Grep `OPEN-416|B3|Fact選定`→関連項目を§7に列挙。新規起票: `OPEN-420 FAMILY-X-B3-FACT-MIN2-PRODUCTION-01`(番号は末尾最大+1をcommit直前に再Grepして確定、Status=PHASE1_DESIGN、APPROVED_FOR_PRODUCTION[ユーザー2026-10-19、原文sha]・未配線)。OPEN-416: Status行末尾に「2026-10-19 ユーザー決定: #112は選択肢(a)〜(d)ではなく新決定『B3下限2件のProduction採用+既存Ledgerで再生成(音声化は範囲外)』で解決。後続=OPEN-420」を追記。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ユーザー正式決定: Family X B3 Fact採用下限2件=APPROVED_FOR_PRODUCTION(未配線)。中東記事は既存Ledger 11件で再生成、音声化は範囲外、記事+Fact選定のユーザー確認でSTOP。#112は本決定で解決」。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #112を「判断済み(2026-10-19、本決定により解決)」へ更新し、本決定を次番号(#117。直前Grepで番号確定)で判断済み登録。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行(初回報告未)。
- `docs/pm/ACTIVE_TASK.md`: 先頭に固定ヘッダ(管理ID/Status/UDR-blocking=#116[FZQI HR Lock、別案件]/UDR-deferred=#114/APPROVED未配線=OPEN-420 B3下限2件/STOP条件/次アクション/QDC/承認済み指示/未回答報告=#116,#23/報告単位Status)。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_委任_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_委任_01.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 --run-dir C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01 --out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_XB3M1_stop_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er019_family_x_b3_production_wiring_01_test_01.py -q`(現行baseline、読み取り確認のみ)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`
- `certutil -hashfile C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-FACT-MIN2-PRODUCTION-01_USER.md SHA256`

## SSOT追記文(要点)
- OPEN-420(新規): 「ユーザー2026-10-19正式決定: Family X B3 Fact採用下限2件=APPROVED_FOR_PRODUCTION(原文sha)。初回選定≤1件なら中心テーマ関連Factを再評価して≥2、数合わせ・未検証Fact禁止、未達はSTOP、Fact Lock等不変、retry/regeneration/resume/再利用経路にも適用。Phase 1設計中、PRODUCTION_WIRED未。中東記事は既存Ledger 11件で再生成、音声化は範囲外」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 2件(+_check.json、stop_check.json)、`docs/research/FAMILY-X-B3-FACT-MIN2-PRODUCTION-01/B3_MIN2_DESIGN_01.md`、OPEN_ITEMS.md、DECISION_LOG.md、USER_DECISION_REGISTER_01.md、REPORT_LEDGER.md、ACTIVE_TASK.md(一時ファイルだが従来どおりcommit対象なら含める)。msg: `FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_01: ユーザー2026-10-19指示(B3 Fact採用下限2件APPROVED_FOR_PRODUCTION・中東記事再生成)原文保存+B3経路マップ・採用数実績・最小変更設計案・Regression案・再生成計画(Phase 1、JPY0、Opus条件A前)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_XB3M1.md`)
4行: (1)整合(E-1分類A/B/C、既存仕様行、Family固有/共通の結論)(2)Production到達経路=変更なし(3)成果物とcommit sha、現行の採用数決定箇所と下限の事実、採用数実績表の要約、設計案比較と推奨(承認範囲内/USER_DECISION候補の区分)、再生成計画の要点と見積(出典付き)、日本語記事成果物の有無、STOPセンチネル有無(4)撤去/残置候補。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/コード不変/run_mey_01不変)。原文保存の文字数とsha256を必ず記載。
