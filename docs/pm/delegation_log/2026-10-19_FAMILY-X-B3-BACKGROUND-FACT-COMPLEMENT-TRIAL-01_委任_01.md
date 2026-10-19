# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_01(ユーザー2026-10-19指示原文保存+Phase A: 「選んだストーリーの最低限の理解に不可欠な背景Factが欠けていれば、その場合に限り最小限追加する」B3補助仕様候補の設計・比較表+Trial専用harness実装(Production非変更)+モックdry-run+評価rubric+費用見積。**JPY0(有料API 0)。実走はOpusレビュー後の委任_02**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: Trial設計+Trial専用コード(er083名前空間)+文書。到達可能Status上限は案件全体で`VALIDATED`(Production採用・配線は範囲外)。
- 到達上限Status(本委任): `B3BG_PHASE_A_DESIGN_AND_HARNESS_READY_PENDING_OPUS`。
- 禁止: Production module(`er019_family_x_storyline_b3_fact_selection_01.py`、runner、producer、契約、Writer)の変更/flag新設/既定値変更/既存の「採用Fact下限2件」仕様・実装の変更/Research再実行・Ledger変更/`run_mey_01`配下の書込み(読取のみ。Trial出力は`er083_output/`)/仕様文への固有事例(「フーシ派」「サウジ」等)の埋め込み/特定Fact IDの採用を誘導する文言/候補の無駄な増殖(3候補以内)/有料API呼出。
- 固定ブロック: **E-1**(CURRENT_SPEC B3節[L1157-1171付近、下限2件bullet]、`docs/research/FAMILY-X-B3-FACT-MIN2-PRODUCTION-01/{B3_MIN2_DESIGN_01.md,OPUS_REVIEW_F_01_VERBATIM.md,MEY_REGEN_02_REPORT_01.md}`、`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_FINAL_REPORT_01.md`(REJECTEDのSelect-then-Verify/再選定方式=再導入しない)、OPEN-420、B3の4テスト(module L38-42)・DEVELOPER_MESSAGE・再評価note・schema、`er053_b3_deterministic_producer_01.py`の入力契約(Storyline一致検査L732等)、過去Trialで「背景」「文脈」「理解に必要」等のFact選定補助を扱ったもの(Grep `背景Fact|background|文脈Fact|理解に不可欠`)をGrepし、A/B/Cに分類)/**D-1**(Trial専用経路: `er083_b3_background_fact_trial_01_{lib,run,eval}.py`を新設し、Production moduleから定数・関数をimportして再利用(複製は最小)。Prompt候補は「既存DEVELOPER_MESSAGE+4テスト+下限2件」を不変のまま、背景補完の補助指示を**追加**する形。Production呼出元(runner)は一切触らない。読込効率: 大ファイルは該当範囲のみRead)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02: er020/er003_v1_n3/crosslevel/er063とCURRENT_SPEC LR節)**: 共有SSOT(OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER)は「編集直前に`git status --porcelain <file>`でclean確認(dirtyなら60秒間隔最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」、`.git/index.lock`待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASKは先頭に自ブロック追記(gitignore))/**F-1**(本委任JPY0。Trial全体のFable枠=JPY150(7-7: 承認済みScope内・300円以下=Fable自律配分。中東記事E2EのCap180とは別勘定で記録)。見積は実測単価(B3 1回≈7.6、W-1 R0-R2≈14.6、`run_mey_01/cost.json`)を出典に)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_01.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_B3BG1.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_USER.md`へ以下「# B3背景Fact補完 Trial」から「過去テーマへの展開は行わない。」までを原文のまま(1文字も変えず)保存し、文字数とsha256を報告)

# B3背景Fact補完 Trial — 中東記事での検証

## 1. 目的・位置づけ

B3の既存機能である「面白く、一貫性のあるストーリーを構成するためのFact選定」は維持する。

今回、以下の補助的な判断を追加する仕様候補について、Trialを行う。

> 選んだストーリーを最低限理解するために不可欠な背景情報が欠けていないかを確認し、不足している場合に限ってFactを追加する。

**最優先条件は、既存のストーリー性・エンターテイメント性を損なわないこと。**

以下は求めない。

- ニュース全体の網羅
- 背景事情の詳細な解説
- Fact数を増やすこと自体
- 関連Factの網羅的な探索
- 中東記事に特化した個別ルール

目指すのは、読者がストーリーを楽しみ、理解するために欠かせない背景情報だけを、必要最小限補う仕組みである。

**Status：新B3背景Fact補完ルールはTrial承認。Production採用は未承認。到達可能Statusは最大 `VALIDATED`。**

## 2. 既存仕様の維持

既存の「採用Fact下限2件」は維持する。

本仕様は、直近報告では `PRODUCTION_WIRED` と判定されている。ただし、Factが1件以下となった場合の再評価経路については、モックテストのみで正式runtime evidenceが未取得であることを未完了の検証事項として管理する。

今回のTrialでは下限2件の仕様・実装を変更しない。

既存のB3選定基準、ストーリー性の評価、Writerへの入力契約、その他の承認済み仕様は維持する。新しい背景Fact補完条件は、既存の選定を補助するものとしてTrial専用経路で検証する。

Trialに着手する前に、CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・既存B3 Prompt・過去Trialとの整合を必要範囲で確認すること。

## 3. Trial対象と検証目的

対象：現在の中東記事。

既存のFact Ledger 11件を再利用する。Researchの再実行は行わない。

現行B3による採用Factは以下の2件。

- F04：リヤド空港攻撃による死傷者数
- F11：国連特使による攻撃への非難と和平への悪影響の警告

今回の検証では、**「誰が、なぜサウジを攻撃するのか」という背景が、ストーリーの理解に不可欠なものとして適切に選定されるか**を確認する。

ただし、特定のFact IDの採用を強制しない。

まず既存Ledger内に必要な背景を裏付けるFactが存在するかを確認する。不足している場合は、不足を明示し、存在しない事実を推測・創作・補完しない。

また、攻撃主体の帰属、攻撃の動機、紛争の背景は区別する。一般的な紛争背景から個別の攻撃主体や動機を断定してはならない。

今回の対象記事への狙いは評価条件として扱い、B3の一般化された仕様文そのものに「フーシ派」「サウジ」等の固有事例を埋め込まないこと。

## 4. Trialの進め方

### Phase A：仕様候補の設計と比較

既存B3のストーリー選定機能を維持したまま、背景Factの最小限補完について複数のPrompt／仕様文候補を作成する。

候補間では「最低限」「不可欠」「欠落時のみ追加」という条件の表現や判断方法を比較する。

候補数や試行順序はFableが検証効率・QCDに基づいて合理的に決める。必要以上に候補を増やさない。

比較条件は統一し、既存B3をBaselineとして保持する。

各候補について、選定Fact・不採用Fact・選定理由・追加された背景Factとその必要性を記録する。

### Phase B：評価と改善ループ

評価軸は以下とする。

1. **ストーリー性・エンターテイメント性**：既存B3の魅力や焦点が損なわれていないか。
2. **最低限の背景理解**：選んだストーリーを理解するために不可欠な情報の欠落が補われたか。
3. **Fact選定の節度**：不要な背景Factの追加や、ニュース全体の網羅に向かっていないか。
4. **事実性・中立性**：Ledgerの根拠を超える推測や、攻撃主体・動機の不適切な断定がないか。
5. **汎用性の見込み**：中東記事に特化したルールや、特定Factを拾うためだけの誘導になっていないか。

Fact選定結果だけでは記事の面白さを確定できないため、有望候補については、既存Writerを使った最小限の下流テキスト検証も行い、Baselineと比較する。

音声化・試聴ページ作成は今回のTrial範囲外とする。

うまくいかない場合は、失敗原因を分析し、仕様文を改善して再Trialする。単なる言い換えの無益な反復は避け、必要に応じてアプローチを再検討する。

承認済み範囲・予算・安全条件内で自律的に進める。Trial回数のみを理由に停止しない。

既存の品質水準を満たす有望候補が見つかれば、追加の磨き込みを行わずTrialをCloseoutする。

### Phase C：Trial Closeout

有望な仕様が得られた場合、または合理的な改善見込みがなくなった場合に、ユーザーへ報告する。

成功した場合でも、新しいB3仕様の正式Production採用や既存記事群への追加Trialへ自動移行しないこと。

## 5. 報告内容

以下を、ユーザーの判断に必要な順番で報告する。

1. **結論**：有望候補の有無、Trial Status（`VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`）。
2. **仕様の差分**：既存B3に対し、背景Fact補完条件として何を追加したか。候補間の違い。
3. **採用FactのBefore／After**：Fact ID・内容・採用／不採用理由。特に「誰が、なぜサウジを攻撃するのか」に関係するFactの扱い。
4. **ストーリー性への影響**：記事の面白さ、一貫性、読みやすさ、余計な説明の増減をBaselineと比較する。
5. **実際の記事テキスト**：有望候補による日本語記事を、Baselineと比較してユーザーが確認できる形で提示する。
6. **QCD**：品質への影響、実費、量産時の追加コスト見込み、処理時間への影響。
7. **未解決事項・リスク**：必要FactのLedger欠落、過剰補完、他テーマへの副作用など。

Fableは既存の必須レビュー条件に従い、必要な独立レビューを実施すること。

## 6. ユーザー確認後の次段階

今回の中東記事で有望候補が得られた場合でも、**ここで一旦STOPし、ユーザーの確認を受ける。**

ユーザーが次段階の検証を承認した場合に限り、これまで扱ったテーマへ新B3仕様を適用し、以下を調べる。

- 既存B3と比較して、採用Factが変わる記事の割合
- Fact数の増減、採用・不採用Factの具体的な差分
- 背景理解が改善したケース
- 不必要なFactが追加されたケース
- ストーリー性・エンターテイメント性が低下したケース
- 量産単価・処理時間への影響

この過去テーマへの影響検証は、今回の委任範囲には含めない。

その結果を踏まえてユーザーがProduction採否を判断する。

## 7. QCD・STOP条件

全作業に共通Charterの8原則を適用する。

優先順位：**品質（Q）＞納期・速度（D）＞量産単価（C）≫開発費用**

独立作業は原則並列化し、既存成果物・Ledger・テスト基盤を再利用する。

既存の案件別承認枠、日次開発費上限、PM Gate、安全STOP、Opusレビュー条件を遵守する。未承認の仕様変更・Production配線は行わない。

特に以下ではSTOPしてユーザー判断を求める。

- Trialの前提となる重大な品質・安全問題が発見された場合
- 承認されたScopeや費用上限を超える場合
- Production仕様の変更が必要となる場合
- 有望候補のTrial Closeoutが完了した場合
- 合理的な改善見込みが失われた場合

**今回の完了条件：中東記事を題材に、ストーリー性を維持しながら不可欠な背景Factのみを補う一般化されたB3仕様候補を検証し、結果と根拠をユーザーが判断できる状態で報告すること。**

正式Productionへの配線、過去テーマへの展開は行わない。

## Fable指示(Phase Aの要件)
1. **Ledger前提確認**(ユーザー§3): `run_mey_01/research_ledger/verified_fact_ledger.txt`の11件について「誰が(攻撃主体の帰属)」「なぜ(動機)」「紛争の背景」の3区分で、Ledgerに裏付けがある/ない/部分的(帰属のみ: F09・F10はフーシ派の発射をイエメン側当局の発表として帰属)を表にする。動機を直接述べるFactが無ければ「Ledger欠落」と明示(推測で補わない)。この表は評価条件であり仕様文には入れない。
2. **仕様候補の設計(3候補以内、一般化された文言のみ)**: 既存B3 Prompt(DEVELOPER_MESSAGE・4テスト・下限2件・再評価note)を不変とし、背景補完の補助指示を追加する。例=(C1「二段階・欠落時のみ」)ストーリー選定を従来どおり完了した後に「このStorylineを初見の読者が最低限理解するために、採用Factだけでは欠ける不可欠な前提(誰が関与しているか/何の出来事の一部か 等)があるか」を自問し、欠ける場合のみLedger内のFactを最小限(原則1件、最大2件)追加。欠けなければ追加しない(既定=追加なし)。追加Factごとに「無いと何が理解できないか」を1文で記録/(C2「第5テスト統合」)既存4テストに「Test5: このFactが無いと、選んだStorylineを初見の読者が理解できないか(背景の不可欠性)」を加え、Test5=YESのFactは採用候補に含める(ただし網羅・解説にならないよう上限と「ストーリーの焦点を変えない」条件)/(C3)C1の変形で「不可欠」の判定方法を変える(例: 「読者が最初に抱く『誰が/なぜ』の問いに、Ledger内で答えられる場合のみ」等。固有事例を書かない)。各候補について: 追加文言(全文)、Storyline一致検査(producer L732)・schema・Writer入力契約への影響(追加Factの位置づけ=`selected_fact_ids`に含めるのか、別フィールドか→Writer契約を変えないため`selected_fact_ids`に含め理由欄で区別する案を基本)、過剰補完の抑止条件、汎用性(他テーマで何が起こるかの思考実験2例: 経済ニュース/科学ニュース)、Baselineとの比較条件統一(同モデル・同Ledger・同theme・温度等)。推奨順序とその理由。
3. **Trial専用harness**: `C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_lib.py`(候補定義・Prompt組立[Production moduleのDEVELOPER_MESSAGE/FACT_TEST定義/schema/validatorをimport]・LLM呼出[Production と同じclient・model_id・設定]・evidence保存)、`..._run.py`(`--article middle_east_yemen_saudi --ledger <path> --theme <現行theme> --candidate baseline|C1|C2|C3 --out-root C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01 --budget-jpy N`、1候補1 call、再評価は既存下限2件ロジックに委ね、費用をcost_log.jsonlに記録)、`..._eval.py`(候補横断の比較表: 採用ID/不採用ID/理由/追加Factと必要性/下限2件充足/Storyline要約/固有事例混入チェック[仕様文に固有名詞が無いことの機械確認])、下流検証用に既存W-1 JA Writerを一時out-dirで呼ぶ最小wrapper(`..._writer_probe.py`、Production Writerをimportし、入力=候補のannotated brief、出力=`ja_writer/revision2.md`相当。Production runnerは使わず、run_mey_01には書かない)。producer(`produce_annotated_b3`)はそのまま再利用(Production不変)。**モックLLMでdry-run**し、Baselineが現行Production選定(F04+F11)を再現する構成であること(同Prompt sha)をassertするtest `er083_b3_background_fact_trial_01_test_01.py`を作る。
4. **評価rubric**: ユーザー§4 Phase Bの5軸を各3段階(維持/軽微低下/低下 等)で定義し、評価者(Sonnet)がBaselineと候補を盲検で比較できる形式(記事テキストの候補名を伏せた比較)にする。「有望候補」の定義=軸1が維持かつ軸2が改善かつ軸3・4・5に問題なし。
5. **費用見積**: Phase B実走=Baseline(再利用、0円)+候補3×B3(各≈7.6)+有望候補の下流JA Writer(各≈14.6、最大2候補)+改善ループ1周(候補1〜2本再走)→期待/上限をJPY枠150と照合。処理時間見込み。
6. **Opusレビュー観点案(条件A)**: 5件以内(例: 補完指示がストーリー選定を侵食しないか/「不可欠」の操作的定義/過剰補完の抑止/Writer契約・producer検査との整合/汎用性)。
7. 文書: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01\TRIAL_DESIGN_01.md`(§1 Ledger前提表/§2候補C1〜C3全文と比較表/§3 harness設計とProduction非変更の証拠/§4 rubric/§5費用・時間/§6 Opus観点/§7 E-1)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py`(全体。Prompt定数・schema・validator・`run_storyline_b3_selection`の署名)
- `C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\{research_ledger\verified_fact_ledger.txt, storyline_b3\fact_selection_evidence.json, entry_point.json, ja_writer\revision2.md}`
- `C:\Users\tensh\eigo-radio\er053_b3_deterministic_producer_01.py` L700-760(入力検査)、`C:\Users\tensh\eigo-radio\er053_family_x_factlock_ja_writer_01.py`(エントリ関数の署名・入力ファイル)
- `C:\Users\tensh\eigo-radio\er082_rlct_trial_01_lib.py`(Trial harnessの構成・cost log・evidence形式の参考。方式は再利用しない)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-X-B3-FACT-MIN2-PRODUCTION-01\MEY_REGEN_02_REPORT_01.md`

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: `B3|Fact選定|下限2件`→§7 E-1に行番号記録(編集しない)。
- `OPEN_ITEMS.md`: `OPEN-420|OPEN-42[0-9]`→新規`OPEN-423 FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01`(番号は直前Grepで末尾+1。Status=TRIAL_PHASE_A_DESIGN、到達上限VALIDATED、Fable枠JPY150)。OPEN-420に「再評価経路の正式runtime evidence未取得=未完了検証事項(ユーザー2026-10-19指示§2)」を追記。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ユーザー指示: B3背景Fact補完Trial承認(上限VALIDATED、Production採用未承認)。原文sha」。`docs/pm/USER_DECISION_REGISTER_01.md`: 判断済み(次番号)、#119(中東記事の扱い)に「本Trial指示で(b)/(d)に代わる方針が示された。音声化判断は保留のまま」を追記。`docs/pm/REPORT_LEDGER.md`: 1行。`docs/pm/ACTIVE_TASK.md`: 先頭固定ヘッダ。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_委任_01.md_check.json`
- `certutil -hashfile C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01_USER.md SHA256`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_b3_min2_test_01.py C:\Users\tensh\eigo-radio\er019_family_x_b3_production_wiring_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er083_b3_background_fact_trial_01_run.py --article middle_east_yemen_saudi --ledger C:\Users\tensh\eigo-radio\er019_output\middle_east_yemen_saudi\run_mey_01\research_ledger\verified_fact_ledger.txt --theme "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く" --candidate baseline --out-root C:\Users\tensh\eigo-radio\er083_output\b3_background_fact_trial_01 --budget-jpy 0 --dry-run`(モック。API 0であることをcost_logで確認)
- `git diff --stat HEAD -- C:\Users\tensh\eigo-radio\er019_family_x_storyline_b3_fact_selection_01.py C:\Users\tensh\eigo-radio\er019_family_x_entertainment_production_runner_01.py C:\Users\tensh\eigo-radio\er053_b3_deterministic_producer_01.py C:\Users\tensh\eigo-radio\er053_family_x_factlock_ja_writer_01.py`(0行であることの証拠)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`

## SSOT追記文(要点)
- OPEN-423(新規): 「ユーザー2026-10-19指示(原文sha): B3背景Fact補完の補助仕様候補をTrial(中東記事、Ledger 11件再利用、上限VALIDATED、Production採用未承認、過去テーマ展開は範囲外)。Phase A設計中。Fable枠JPY150(7-7、300円以下自律)」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 2件(+check)、TRIAL_DESIGN_01.md、er083_*.py(lib/run/eval/writer_probe/test)、SSOT(OPEN_ITEMS/DECISION_LOG/REGISTER/REPORT_LEDGER)。msg: `FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01 委任_01: ユーザー2026-10-19指示(背景Fact補完Trial、上限VALIDATED)原文保存+Ledger前提表・仕様候補C1〜C3・Trial専用harness(er083、Production非変更)・モックdry-run・rubric・費用見積(Phase A、JPY0、Opus条件A前)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_B3BG1.md`)
4行: (1)整合(E-1 A/B/C、RLCTのREJECTED方式を再導入していないこと、下限2件不変)(2)Production到達経路=変更なし(git diff 0行の証拠)(3)成果物とcommit sha、Ledger前提表の結論(「なぜ」の動機FactはLedgerにあるか)、候補C1〜C3の要約と推奨順序、harness dry-run結果(Baseline Prompt sha=Production一致)、rubric、費用・時間見積(4)撤去/残置。`判定整合:`・`判断候補:`・T-0 check・自己チェック(有料0/Production不変/固有事例の仕様文混入0/原文sha256)。
