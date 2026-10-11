# PHASE3_PREP_01: coffee_prices / hormuz へのA/C/D/E展開 課金前準備(無課金・read-only)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_04 / 2026-10-11。API・生成・Production変更・SSOT編集なし(費用0円)。為替160円/USD、単価はpricing_snapshot(luna 0.10/0.50、astra 10/50、sol(6.1) 2/10 USD/M)。

## 1. artifact表
| 項目 | coffee_prices | hormuz |
|---|---|---|
| A案(現行Production条件=W-1+決定論producer) | **既存あり**: `er019_output/coffee_prices/run_l3_01`(2026-10-10、B3 Luna→producer→R0 Luna→R1/R2 Astra)。**再利用可(新規0円)** | **存在しない**。refresh_e2e_01/hormuz/run_01〜03は旧writer(chain、ja_original/check/must_fix等)、b3_diversity_trial_01はTrial。`er052_output/factlock_astra_e2e_trial_01/runs/hormuz/new/new_writer`(2026-10-09)はFact Checker付き・旧手動注記B3入力でA案とは入力契約が異なる(META B案と同類、参考止まり)。**A案は新規生成が必要** |
| Ledger path(推奨) | `er019_output/coffee_prices/run_l3_01/research_ledger/verified_fact_ledger.txt` | `er019_output/family_x_refresh_e2e_01/hormuz/run_03/research_ledger/verified_fact_ledger.txt`(最新run、2026-09-29 14:32) |
| Ledger sha256 | e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b | 9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6 |
| Fact数/文字数 | 18件(全[VERIFIED])/8,266字(16,927 bytes) | 12件(全[VERIFIED])/4,949字(9,916 bytes) |
| 検証状態 | verified(verdict_counts.json、2026-10-10) | verified |
| R2(A案) | `ja_writer/revision2.md` sha 48fc4aea…、954字 | なし(A新規生成で作成) |
| B3(C案で再利用) | `storyline_b3/`にfull_ledger.json/selected_brief.md/fact_selection_evidence.json/runtime_evidence.json/annotation系/selected_brief_annotated.md/writer_constraints.txtが揃う(driverのprepare_inputs対象4ファイルすべて存在)。選択Fact数はfact_selection_evidence参照(driver実行時に記録) | A案新規生成時のB3(Luna)出力を再利用 |
| B3〜R2実測円 | 39.065円(B3 0.696/R0 0.543/R1 18.162/R2 19.664) | 実測なし(下記は見積) |
| token(in/out(reasoning)) | B3 6,241/7,456(4,558)、R0 2,437/6,296(5,588)、R1 696/2,131(1,405)、R2 765/2,305(1,550) | 実測なし |

hormuz Ledger候補はsha 9bd6834e…の同一内容(b3_diversity run_01/02、refresh_e2e run_01〜03、an3_t0_wiring_regression、all6_writer_redesign全てsha一致)=Ledger版は1つのみ。最新の検証済みコピー=refresh_e2e_01/hormuz/run_03を推奨(2026-09-29配置、Production経路に最も近いrunのartifact、byte一致のため差は無い)。原本Research実行は2026-09-26(b3_diversity run_01)。
hormuz topic文字列(B3入力): 「ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応」(run_03 storyline_b3/full_ledger.json)。coffeeは長い英語theme(run_l3_01 full_ledger.json topic、A案B3と同一文を使うこと)。

## 5相当. hormuz Ledgerの鮮度注意
Ledgerは2026-09-26取得(2026-10-11時点で約15日前)。内容は7月13〜14日のBrent・トランプ氏発言撤回の事象で、以後の続報は反映されない。Research再実行は禁止のためそのまま使用し、評価ページ/報告に「Ledger取得日2026-09-26、事実鮮度は当時」と注記。記事の比較目的(モデル配置差)には影響しないが、本文は最新状況を示さない。

## 2. 工程別費用見積(円、登録単価)
方法: input tokenはA実測(coffee=実測、hormuz=META/coffee実測からLedger長比で補正、B3入力3,130/R0 1,800/R1 600/R2 750)。output tokenはA実測(coffee=実測、hormuz=META・coffee実測平均 B3 5,855/R0 4,932/R1 2,184/R2 2,098、reasoning込み)に、**META Phase2実測のモデル別出力比**を掛ける(B3: Astra x1.262/Sol x0.852、R0: Astra x1.202/Sol x1.359、R1(対Astra): Luna x0.436/Sol x0.549、R2(対Astra): Luna x0.955/Sol x1.200)。保守=点x1.5。cached=0前提。

| 記事 | 案 | B3 | R0 | R1 | R2 | 点見積 | 保守(x1.5) |
|---|---|---|---|---|---|---|---|
| coffee | A | 既存 | 既存 | 既存 | 既存 | 0(実測39.07) | 0 |
| coffee | C | A再利用0 | 64.46 | 0.09 | 0.19 | 64.74 | 97.10 |
| coffee | D | 85.25 | 0.54 | 0.09 | 0.19 | 86.07 | 129.11 |
| coffee | E | 12.17 | 14.47 | 2.10 | 4.67 | 33.40 | 50.10 |
| hormuz | A(新規) | 0.52 | 0.42 | 18.43 | 17.98 | 37.36 | 56.04 |
| hormuz | C | A新規B3再利用0 | 50.32 | 0.09 | 0.17 | 50.58 | 75.87 |
| hormuz | D | 64.11 | 0.42 | 0.09 | 0.17 | 64.80 | 97.19 |
| hormuz | E | 8.99 | 11.30 | 2.11 | 4.27 | 26.66 | 40.00 |
| **coffee計(C/D/E)** | | | | | | 184.21 | 276.31 |
| **hormuz計(A/C/D/E)** | | | | | | 179.40 | 269.10 |
| **合計** | | | | | | **363.60** | **545.40** |

残予算 ¥140.89(上限250−既消費109.11)に対し: 点見積で **約222.7円超過**、保守で約404.5円超過。さらに上限250は累計(既消費+今回)で見るため、全案実施は約472.7円(点)に達する。
見積の不確実性: coffeeのA実測tokenはMETAの約1.75倍(長いLedgerで出力が増える)ため、META実測(C37.4/D50.2/E21.6)より高く出る。hormuzはLedgerが最小(12件/4,949字)で、旧writerの実測でもR0出力がMETAより少なく、実際は上記点見積より低い可能性がある(下限側の根拠は薄く、点見積をそのまま採用)。モデルの出力比はMETAの1サンプル(N=1)由来で不確実(Luna R0はreasoning 4,896の例あり)。

### 残予算内に収まる組合せ(点見積/保守、参考)
| 組合せ | 点 | 保守 | 残¥140.89に対し |
|---|---|---|---|
| coffee E + hormuz A,E | 97.42 | 146.13 | 点OK/保守超過(+5.2) |
| coffee C,E | 98.14 | 147.20 | 点OK/保守超過 |
| coffee E のみ | 33.40 | 50.10 | OK |
| coffee C + hormuz A,E | 128.76 | 193.14 | 点OK/保守超過 |
| coffee C,E + hormuz A,E | 162.16 | 243.24 | 点超過 |
| 全案(上表) | 363.60 | 545.40 | 超過 |
Dはどちらの記事でもAstra B3が重く最大(coffee 86/hormuz 65)。ユーザー判断事項: 記事数・案の絞り込み、または上限引上げ(Fable→ユーザー)。本委任では決めない。

## 3. driver / ページの準備状況
`maq_driver_01.py`は**META固定**で、slug/out_dir/Ledgerを引数で切り替えられない。必要な最小変更点(実装はしていない):
1. 定数 `TOPIC`、`LEDGER_SHA`、`A_RUN`、`RUNS`(出力先)を `--slug {coffee_prices,hormuz}` から引く記事設定dict(`ARTICLES[slug] = {topic, ledger_src, ledger_sha, a_run or None, out_root}`)へ。出力先は `er052_output/ja_article_quality_model_allocation_trial_01/runs_02/<slug>/<arm>/`(既存trialディレクトリ配下、runs_01=META とは分離)。
2. `prepare_inputs`(L368-)のLedger元を `A_RUN/research_ledger` 固定→`ledger_src`引数化、sha assertをslug別に。
3. `run_arm`のassert(`arm in ("C","D","E")`)を、hormuzのみ`A`も許可(A新規生成: b3=Luna、Production同一条件、capはA用に別途設定=保守見積約56円)。coffeeのAは`prepare_a`(既存複製)を`A_RUN`引数化して使う。hormuz C案はhormuz A新規生成のstoryline_b3を`copy_b3_from`に指定(A→Cの順序依存あり、直列)。
4. `ARMS`のcapと`EST_TOKENS`(META基準)は記事別化が必須。現状のまま使うとcoffeeはEST(META基準x1.5)がcoffee実績の約1.75倍の出力を過小評価するため、(a)cap超過をガードが検知できない、またはC cap55<coffee C点見積64.7で正当な実行がSTOPする。記事別cap/EST_TOKENSをこの文書の表から設定。
5. `prepare_a`内のraw_usage_log集計は`stage`フィルタ済みのためcoffeeの余分stage(research/ledger/advanced等)は無視される(確認済み)。ただしキー名(`model_id`/`response_id`/`elapsed_seconds`)がcoffeeのraw_usage_logにもあるかは実行前に無課金で確認要(委任_03のstub testで検証可能)。
6. テスト`maq_driver_01_test_01.py`はD.TOPIC/D.A_RUNを参照する。記事設定化に合わせてslug引数でALL_PASSを再取得(無課金stub)。
7. 全体予算guard: 現行のTOTAL_CAP(250)は案cap合計のみ。**既消費109.11を差し引いた残予算(140.89)**を実行前ゲートとして追加する必要がある。

### Blind割当(記事ごと独立seed)
`blind_page_01.py`はSEED固定(20261011)。記事別に `seed = int(sha256(("MAQ02:"+slug).encode()).hexdigest()[:8],16)` を使い、`random.Random(seed).shuffle(arms)`(coffee_prices=3330374777、hormuz=4088314252)。対応表は`BLIND_MAP_02_<slug>.json`としてtrialディレクトリに別保存(記事間でラベルに相関が出ない)。出力先を`user_test/ja_quality_model_allocation_02/{coffee,hormuz}/index.html`に引数化。
ページ構成: METAと同等(h1「記事比較」、注記、タブ(記事①〜、案数に応じて3〜4本)、各タブ=R2全文。モデル名・案名・文字数なし、noindex、音声なし)。漏洩検査(gpt/luna/astra/sol/案/model/モデル/文字/字数の骨格・本文検出)をそのまま流用。hormuzはLedger取得日(2026-09-26)の注記を評価者向けでなくメモ側(trial md)に置く(ページにはモデル推測情報を出さない)。

## 4. 未決・ユーザー判断
- 予算: 全案は不可。絞り込み(上表)または上限引上げ。
- hormuz A案の新規生成(約37円点/56円保守)を含めるか。
- hormuz B3 topic文字列は旧run_03のものを流用(Production現行のtopic指定はentry設定と一致するか実行前確認要)。
