# ANALYSIS_REPORT_01(FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 委任_01、2026-10-16、read-only・JPY0・実装/Trialなし。本文は委任_01 sonnet-workerの最終報告を無改変で転記。採用判断はユーザー)

RLCO 委任_01 完了報告。Status=ANALYSIS_COMPLETE_PROPOSAL_READY。費用JPY0、API呼出なし、git書込みなし。

重要: ANALYSIS_REPORT_01.md と RESULT_PACKET_RLCO1.md は書けなかった。Writeツールが「サブエージェントはレポート.mdを書かず本文で返せ」と拒否した。Bashのheredocで迂回すると制限の回避になるため行っていない。提案書の全内容は以下の本文にある。ファイル化が必要なら、Fableが自分で保存するか、権限を明示した再委任をしてほしい。

# 0. T-0結果と成果物状況

- 委任文: 全文を保存した。
  - `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md`
  - check結果は FAIL（記録のみ）。理由は「実行コマンド節の『有料コマンド・runner実行は一切しない。』行に引数実値が無い」の1件。
  - warningsは2件。TTS予算の言及なし（本委任はTTSなし）と、QDC記録なし（新規委任のため）。
  - 結果JSON: 上記ファイル名の末尾に `_check.json` を付けたもの。
- ユーザー原文: `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_USER.md`
  - 3,149文字、6,503バイト（UTF-8、LF）。
  - sha256=`1a58d4d72c19f1edb243f0a76491128e1d3a32ca8107f50ed8807d4de402d42b`
  - 指定の約2,600〜3,000字を超えている。原文は欠落なく保存した。表やMarkdown記号の分で超えたとみられる。
- 開始時に stop_scope_check を実行した（rc=0、非停止）。
- 作成物は次の3つ。
  - `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/aggregate_usage_01.py`
  - `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/usage_breakdown_01.json`
  - delegation_log の3ファイル（上記の委任文・check JSON・ユーザー原文）
- 集計scriptの実行は、委任文の指定コマンドに `--compare-run` を3つ追加して実行した。比較対象は run_l3_01、family_x_b3_production_wiring_01/run_01、meta/run_sol61_01。

# 1. Research ¥19.85 / Ledger ¥25.14 の費用発生原因（ユーザー§9の項目1）

- **費用の88.9%（¥40.00 / ¥44.98）はWeb検索ツールの呼出手数料。** 1回¥1.6（$10/1,000回×¥160）で25回分。トークン代は ¥4.98（11%）しかない。
- Ledgerの方が高い原因は3点。
  1. 検索回数が14回対11回で、+3回＝+¥4.80。差額¥5.29の91%を占める。input token は +¥0.62、output token は -¥0.13。
  2. Ledgerは24クエリのうち11クエリ（46%）を、記事に使われなかった F16 / F17 の確認に使っていた。
     - F16 / F17 はどちらもUSDA 2026年7月版の文書。
     - Ledgerが持つURL（`.../circulars/coffee.pdf`）は最新版を指す別名で、検索すると2025年12月版が返った。
     - 結果は両方とも AMBIGUOUS。
     - 証拠: `er019_output/coffee_prices/run_fxpw_01/research_ledger/audit/verification_full_record.json` のqueries 12,13,14,16〜23、および F16 / F17 の verification_notes。
  3. LedgerのPromptに下書き全文（15,815文字）を埋め込んでいる。Researchは1,855文字。これは input token で数円未満の差で、主因ではない。

# 2. 費用表（項目2）

`raw_usage_log.jsonl` の stage=research / ledger 各1行を再計算した。両工程とも成功、attempt_number=1、retry/fallback/再生成=0回。cached_input_tokens=0。

| 項目 | Research | Ledger | 合計 |
|---|---:|---:|---:|
| model_id | gpt-6-luna | gpt-6-luna | — |
| API呼出 | 1 | 1 | 2 |
| web_search呼出 | 11 | 14 | 25 |
| input token | 92,865 | 131,645 | 224,510 |
| output token（うちreasoning） | 9,518（2,924） | 7,857（5,728） | 17,375 |
| cached token | 0 | 0 | 0 |
| 所要時間 | 141.8秒 | 115.9秒 | — |
| 検索手数料 | ¥17.60 | ¥22.40 | ¥40.00 |
| input token代 | ¥1.486 | ¥2.106 | ¥3.592 |
| output token代 | ¥0.761 | ¥0.629 | ¥1.390 |
| 再計算合計 | ¥19.8473 | ¥25.1349 | ¥44.9822 |
| cost.json | 19.847 | 25.135 | 差 +0.0003 / -0.0001（丸めのみ） |

- 単価は `er005_output/cost_baseline_01/pricing_snapshot.json` から。gpt-6-luna は input 0.1 / cached 0.01 / output 0.5（USD per 1M）、web_search は $10 per 1,000 calls。
- 為替は `er012_e_family_entertainment_two_level_runner_01.py:68` の USD_JPY=160.0。
- 課金コードは `er019_family_x_entertainment_production_runner_01.py:308-345` と `er012_e_family_entertainment_two_level_runner_01.py:126-135`。検算と同じ式。未集計行はない。

過去runとの比較（同経路）:

| run | model | Research | Ledger | 検索回数 R/L | 選定Fact |
|---|---|---:|---:|---|---|
| fxpw_01（今回、Coffee） | gpt-6-luna | 19.85 | 25.14 | 11/14 | 4/17 |
| l3_01（Coffee） | gpt-6-luna | 21.96 | 24.88 | 12/14 | 5/19 |
| family_x_b3_production_wiring_01/run_01（Meta） | gpt-5.6-luna | 14.47 | 14.27 | 7/7 | 3/15 |

- Ledgerの検索ログを持つFamily Xのrunは上の3つだけ（n=3）。一般化はしない。
- `run_l3_01_stdregen` はl3_01のログの複製なので別計上していない。

# 3. 無駄・重複・過剰処理と、品質上の役割（項目3）

- **使われないFactの検証。** B3（Fact選定）が採用するFactは全runで20〜27%（4/17、5/19、3/15）。検証済みFactの約3/4は記事に入らない。役割は要確認で、案2の対象（要Trial）。
  - B3は全Factを材料に物語を選ぶ。
  - Risk Flaggerは完全なLedgerと記事を照合する（`er053_risk_flagger_production_01.py:5`）。
- **同じ文書への言い換え検索の反復。** 今回はUSDA 11クエリ。L3でも `359.25` 系4クエリ＋USDA系で同様。
  - 現行仕様でも、確認できなければ AMBIGUOUS が安全側の標準出力（`er003_v1_en_direct_vfl_01_generate.py:282-292`）。
  - 案1の対象（要Trial）。
- **Researchでの類似クエリ。** ICO 2026年9月版を3〜4回言い換えている。一次資料探索の失敗リカバリの可能性があり、**算出不可**。削減案に入れない。
- **Promptの埋込量とキャッシュ。** 効果は上限でも数十銭〜¥0.25、キャッシュは最大¥0.23。対象外。
- **retry / fallback / 再生成。** 0回。

# 4. 品質上削れない処理（項目4）

- **Ledgerの独立Web再照合。**
  - Family Xは旧Fact Checkerを撤去済み（`CURRENT_SPEC.md:1186,1346`）。W-1 Writer と Risk Flagger には web_search が無い（`er053_risk_flagger_production_01.py`、`er053_family_x_factlock_ja_writer_01.py` でGrep 0件）。
  - つまり、Webに対する独立確認はLedgerだけ。
  - 今回の検出実績:
    - F07: Reuters記事にVietnamへの懸念の記載がなく AMBIGUOUS。**F07は記事に採用された。**
    - F12: BLSの -0.3% は季節調整済みなのに、下書きは未調整と誤記していた。
    - F16: 輸出量は生豆のみの数字。
    - F17: 「低地」限定が出典で未確認。
    - F02: 4.30超は3月限spotの日中高値で、主要限月の終値は4.211。
  - L3でも COFFEE-004（販売済み割合が記事内で 70〜80% と 80〜90% に食い違う）を検出した。
- **Researcherの一次資料優先と、scope / causal_strength の構造化。** WriterのFact Lockの入力になる。Prompt は `er003_v1_en_direct_vfl_01_generate.py:137-170`。
- **AMBIGUOUSの保持と「断定禁止」タグ。**
- **B3が全Factを見て物語を選ぶこと。** 過去のNews Trial-12では、Fact 5件でNG率83%、12件で33%だった（`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md` 3-4）。Fact数の単純削減は推奨しない。

# 5. 効かない、または既決の方向（重複新設しない）

- **モデル変更**
  - 検索手数料は全モデル共通（`pricing_snapshot.json` の `N/A (tool, all models)`）。
  - トークン代は全体で ¥4.98 のため、仮に0円のモデルでも削減上限は -¥4.98。
  - gpt-6-luna は登録済みOpenAIモデルで最安。
  - 低性能化は精度リスクがあり、採用しない。
- **Prompt短縮**: 上限でも約¥0.25。
- **キャッシュ**: 最大約¥0.23。B-FC-1(b)（`DECISION_LOG.md:1506,6422-6430`）で「cacheは現時点でProduction実装しない」と既決。
- **同一run内のLedger再利用**: 実装済み（runner:98-102）。
- **reasoning effort**: 出力トークン代は合計¥1.39で、検索回数への影響は算出不可。

# 6. 推奨改善案（最大3案、項目5・6）

共通前提:
- 試算は `manual_substitution`（机上計算）。実測ではない。
- 検索1回＝¥1.6＋検索本文token（約8.3〜9.4千token＝¥0.13〜0.15）で計算。
- クエリ→呼出の換算は 14/24=0.583。ログにクエリ別の呼出数が無いための近似。

## 案1: Ledger検証の「Fact単位の探索上限」＋Researcherの出典ロケータ引継ぎ【順位1】

| 項目 | 内容 |
|---|---|
| 原因 | 1件のFactが確認できないとき、言い換え検索を無制限に反復する。LedgerのURLが最新版を指す別名で、版違いに当たる |
| 証拠 | fxpw のqueries 12〜14,16〜23（11/24）、F16 / F17 の verification_notes、l3_01 のqueries（`359.25` 系4件＋USDA系） |
| 対策 | (a) Ledger Promptで、Factあたりの探索がN回（案3回）で確認できなければ AMBIGUOUS＋理由で終了させる。全Factの独立Web再照合は維持する。(b) Researcher出力に版・発行月・出典内の該当箇所を追加する |
| 削減額 | Ledger 約¥5.1〜7.2（上限3回で5クエリ＝2.9呼出、上限2回で7クエリ＝4.1呼出）。Research ¥0 |
| 削減率 | Ledger -20〜28%、Research+Ledger -11〜16%、Text工程 -7〜10% |
| 品質リスク | 低〜中。本来確認できたFactが AMBIGUOUS に落ち、使えるVERIFIED Factが減る恐れ。誤ってVERIFIEDにするリスクは増えない設計。検索回数の制限は、T-3評価で11節STOP必須条件（QA相当）と判定されており、ユーザー判断が必要 |
| 実装負荷 | 小（Promptとschemaの追加。検索実行コードは不変） |
| 検証方法 | 保存済み下書きでLedger検証だけを再実行し、現行verdictと比較（§9） |

## 案2: 採用候補に絞って検証（Select-then-Verify）【順位2、最大効果、構造変更】

| 項目 | 内容 |
|---|---|
| 原因 | 全Factを検証してからB3が選ぶため、検証の約3/4が記事に入らない |
| 証拠 | `fact_selection_evidence.json`（3runで 4/17、5/19、3/15）。runnerは全Factを検証する（runner:97-141）。クエリ内訳では、選定4Fact（F02 / F07 / F09 / F11）に関係するのは6/24＝25%で、Fact比 4/17＝24% と整合 |
| 対策 | Researcher下書き → B3が選定 → 選定Factだけ独立Web再照合 → W-1。B3入力は検証前の下書きになり、Risk Flaggerの参照台帳は「選定Factの検証済みLedger」になる |
| 削減額 | Ledger呼出 14 → 約3.3〜6回。Ledger新費用 ¥5.9〜10.8。削減（総額）¥14.4〜19.2。REJECTEDで再選定になる場合、B3 1回 ¥10.94 が追加で発生する。REJECTED実測は 0/51 で、95%上限（5.7%/Fact）ならその期待値は +¥2.3。**純削減 約¥12.1〜19.2** |
| 削減率 | Ledger -57〜76%、Research+Ledger -27〜43%、Text工程 -17〜26% |
| 品質リスク | 中。(1) B3が未検証Factで物語を選ぶ（今回もF07は AMBIGUOUS のまま採用された）。(2) Risk Flaggerの参照台帳が縮小し、選定外Factに触れたときの検知力が変わり得る（要Regression）。(3) B3の入力形式変更はProduction仕様変更。記事に出るFactの検証は維持される |
| 実装負荷 | 大（runnerの段階順、resume/再利用経路、RF契約、B3 Prompt、test）。Opus条件A対象と見込む |
| 検証方法 | 保存済み下書き3件で、B3 → 選定Factのみ検証を実行し、現行と比較（§9） |

## 案3: 検索基盤の置換（Evidence Pack / 別Search API）【参考、推奨せず】

- 既存資産は `ER-005-RESEARCH-LAYER-REDESIGN-01_report.md`（検索21回→0回、約$0.022）。Perplexity Search APIは $5/1,000 request（`ER-005-SEARCH-LAYER-OPT-01_report.md` L12）。
- ただし検証は**単一のOpen Access論文1件のみ**。Reuters/AP/BLS/USDAなどへの適用は未検証。
- 削減額は**算出不可**。確認には調査範囲の拡大と有料Trialが要るため、STOP理由として記録するにとどめる。

## 組合せ（二重計上なし）

| 条件 | Research | Ledger | Research+Ledger | Text工程（現行¥72.64） |
|---|---:|---:|---:|---:|
| 現行実測 | 19.85 | 25.14 | 44.98 | 72.64 |
| 案1のみ | 19.85 | 17.9〜20.0 | 37.8〜39.9 | 65.5〜67.5 |
| 案2のみ（純額） | 19.85 | 5.9〜13.0 | 25.8〜32.9 | 53.4〜60.5 |
| 案1+案2 | 19.85 | 案2とほぼ同じ | 案2とほぼ同じ | 53.4〜60.5（案1の追加分は算出不可、0〜約¥1） |

- 案1と案2は足し算しない。案1が削る反復（F16 / F17の11クエリ）は、案2では検証対象外になって既に消えるため。
- Research（¥19.85）は不変。Researcherの重複検索は、クエリ→Fact対応が無く算出不可。Fact数削減は物語選択の幅を損なうため推奨しない。

# 7. 組合せ後の量産原価（項目7）と70円目標への影響（項目8）

- Text工程の実測は ¥72.64。
  - Research 19.85
  - Ledger 25.14
  - B3 10.94
  - W-1（w1_r0 + r1 + r2）13.85
  - Advanced / Standard / RF 約3.2
- 案2適用後のText工程は約¥53.4〜60.5（推定）。
- 音声工程は**未実測**。委任_06の値は入れていない。
- 70円は、Research/Ledger・Writer・TTS等を含む1生成セット総原価が対象（PM_GOVERNANCE.md 15-9、3036行付近）。Text工程だけで既に70円を超えている。
- 案2適用後でも、音声・KP等に使える残りは約¥9.5〜16.6。
  - 計画書 `COFFEE_E2E_PLAN_01.md:69-80` の audio+scaffold 小計は ¥27.8。これは計画見積で、未実測。
  - 仮にこの見積通りなら合計は約¥81〜88となり、Research/Ledger改善だけでは70円に届かない。他工程でさらに約¥11〜18の削減が必要。
  - 判定は実測音声費用が出てから行う。
- 70円のために品質を下げる案（Fact削減・検証省略・低性能モデル）は推奨しない。

# 8. Existing Spec / Prior Trial Check（項目7の補足）

| 既存事項 | 本件との関係 | 区分 |
|---|---|---|
| T-3: Ledger検索の回数上限（`DECISION_LOG.md:2477-2490`、`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md` 3章）。「現状維持（保留）」で、Verification段階は削減対象から除外、上限検討はResearcher段階に限定、という推奨 | 案1は総回数上限ではなく「Fact単位の探索上限＋AMBIGUOUS退避」で性質が違う。ただし今回の実測では、無駄はResearcherでなくVerifierの反復に出ており、当時の推奨と異なる所見 | C/D |
| OPEN-149（`OPEN_ITEMS.md:325`）: A-Family限定のResearch/Verification/Final Web Fact Check最適化。DEFERRED、単純削除禁止 | Family X対象外。本提案は削除でなく順序・探索規律 | C |
| OPEN-143（`OPEN_ITEMS.md:318`）: 量産API費用最適化。ユーザー実検証後に着手のDEFERRED | 今回ユーザーが本調査を明示依頼＝調査の着手指示済み | B |
| B-FC-1(b)（`DECISION_LOG.md:1506`）: cacheは実装しない | 案に含めない | A |
| ER-005-RESEARCH-LAYER-REDESIGN-01: Evidence Pack | 案3の既存資産。新設しない | C |
| OPEN-366 / 15-9: 70円は目標でありSTOPではない | §7 | B |
| OPEN-395: JA Latin語web lookup 1回¥21.5 | 別系統。重複計上しない | C |

# 9. 次に検証する場合の必要費用・受入条件（項目9）

費用は既存実測を流用した見積で、本調査では実行していない。

| 検証 | 内容 | 見積 | 根拠 |
|---|---|---:|---|
| 案1 Trial | 保存済みResearcher下書き（Coffee fxpw / L3 / Meta）に対し、Ledger検証だけを改変Promptで再実行。反復3回 | 約¥150〜200 | Ledger実測 25.14 / 24.88 / 14.27。現行runnerは分割再実行非対応（runner:60-66）のため、検証用harnessの新規作成が必要 |
| 案2 Trial | 同3下書きで「B3 → 選定Factのみ検証」を実行し、現行と比較（Research再実行なし） | 約¥55〜60 | B3実測 ¥10.94 ＋案2のLedger試算（約6〜11）×3 |
| 案2 実装 | runner・RF契約・B3入力・test | 別途 | Opus条件Aレビューが必要 |

受入条件案:
1. 現行のVERIFIED Factは、VERIFIED維持か理由付きAMBIGUOUSのみ。現行のAMBIGUOUS / REJECTEDがVERIFIEDに昇格しない。
2. 記事採用Factの誤りの見逃しが0。F07型（部分欠落）やF12型（ラベル誤り）を検出し続ける。
3. 検索呼出の削減が試算の下限以上。案1はLedger -2.9回以上、案2は -8回以上。
4. 案2では、B3選定結果が現行と大きく乖離しないこと（人間確認）。既存のRF / Fact Lock回帰テストがPASSすること。REJECTED化による再選定の発生率を記録すること。
5. 3テーマ（Coffee、Meta、新テーマ1件）で成立すること。

# 10. 判断候補（項目10）

| 判断候補 | 区分 | 根拠 |
|---|---|---|
| 案1を検証Trialへ進めてよいか | D（真に新しい） | 検索回数制限はT-3評価でSTOP必須条件扱い（`DECISION_LOG.md:2483`）。既判断なし |
| 案2を検証Trial・実装設計へ進めてよいか | D | Production処理順とB3入力の変更。承認済みFamily X仕様（`CURRENT_SPEC.md:1157` 以降）の意味変更に当たる |

案3、モデル変更、Prompt短縮、cacheは推奨なしで、判断不要。

# 11. STOP理由（証拠の限界）。提案書は完成させた

- 検索ログはクエリ文字列のみ。各呼出の種別（検索かページ閲覧か）と、クエリ別の呼出数は未保存。削減額は比例仮定で、実測誤差がある。
- 公式の課金単位（複数クエリやページ閲覧を何回と数えるか）は、ネット調査禁止のため再確認していない。プロジェクトの課金式（呼出数×$10/1,000）に従った。
- 比較対象はFamily XのLedgerログを持つ3runのみ。
- 以上から、削減額は範囲で示し、§9のTrialで実測確認する前提とした。

# 12. RESULT_PACKET 4行と判定整合

1. 既存仕様整合: 照合したのは次のファイル:行。
   - `CURRENT_SPEC.md:1157,1186,1346`
   - `er019_family_x_entertainment_production_runner_01.py:60-66,97-141,308-345`
   - `er012_e_family_entertainment_two_level_runner_01.py:68,126-135,183-236`
   - `er003_v1_en_direct_vfl_01_generate.py:137-170,228-250,282-292`
   - `er053_risk_flagger_production_01.py:5,169-194`
   - `PM_GOVERNANCE.md` の 15-8 / 15-9 / 21節
   - `DECISION_LOG.md:1506,2477-2490`
   - `OPEN_ITEMS.md:318,325`
2. Production到達経路の未承認機能の既定値: 変更なし。コード・Prompt・設定は未編集で、新機能の追加もない。
3. 最終成果物: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/usage_breakdown_01.json` と、上記の本文。調査が目的の要件（原因特定・削減試算・採用判断材料）に対し、案1・案2・組合せ・70円影響まで揃っている。ただし提案書.mdファイルは未作成（§0）。削減額は机上試算で、実測確認は未了。
4. 撤去・残置: なし。旧ルール・検査・testの撤去も残置もない。
- 判定整合: 重大NG=なし / 主因=web_search手数料（呼出25回＝¥40.00）およびLedgerのF16/F17反復検索 / 是正対象=なし（提案のみ） / STOP理由=クエリ別呼出数と呼出種別が未保存、課金単位が未確認（提案書は完成）/ 提示=可（採用判断はD区分でユーザー）

# 13. commit対象ファイル一覧（git書込みは未実施）

- `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md`
- `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md_check.json`
- `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_USER.md`
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/aggregate_usage_01.py`
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/usage_breakdown_01.json`
- 提案書本体は未作成。Fableが保存する場合の保存先は `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/ANALYSIS_REPORT_01.md`。
- commit message案: 「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 委任_01: Research/Verified Fact Ledger費用構造のread-only分析+削減案提案書(JPY0、実装・Trialなし)」

SSOT追記文案（編集していない）:
- DECISION_LOG: 「2026-10-16 FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 委任_01。Coffee fxpw_01のResearch/Ledger費用の89%がweb_search手数料と判明（25呼出×¥1.6）。案1（Fact単位探索上限、削減¥5〜7）・案2（Select-then-Verify、純削減¥12〜19）を提案。採用はユーザー判断待ち、実装・Trialなし。」
- OPEN_ITEMS（新規候補）: 「RLCO-PROPOSAL-01、Status=PROPOSAL_READY_USER_DECISION、区分=POST_USER_VALIDATION。案1・案2の検証Trial可否」。
- REPORT_LEDGER行とACTIVE_TASK追記行: 上記要約から作成可能。

# 14. 一覧外Readの理由

- `PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`、`ER-005-RESEARCH-LAYER-REDESIGN-01_report.md`、`ER-005-SEARCH-LAYER-OPT-01_report.md`: 過去のコスト対策（検索回数上限・Evidence Pack・Perplexity）との重複新設を防ぐための必須確認。
- `er003_v1_en_direct_vfl_01_generate.py`、`er002_ja_web_research_r3.py`、`er053_risk_flagger_production_01.py`、`er053_b3_deterministic_producer_01.py`、`er053_family_x_factlock_ja_writer_01.py`、`er019_family_x_storyline_b3_fact_selection_01.py`: Research/Ledgerの実体（Prompt・モデル・web_search計数）と、下流でLedgerが何に使われるか・Webが他に無いことの確認。
- 他run（`run_l3_01`、`family_x_b3_production_wiring_01/run_01`、`meta/run_sol61_01`）の `raw_usage_log.jsonl`、`research_ledger/audit/*`、`fact_selection_evidence.json`: 委任文「過去run比較」の範囲。`family_x_audio_production_wiring_01` と `user_test` は読んでいない。