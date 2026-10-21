# Trial設計 TRIAL_DESIGN_01(有料実行前にcommit)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_01 / 2026-10-21 / 事前Gate=`PRIOR_TRIAL_GATE_01.md`(否定的結果なし)
性質: Trial(Trial専用経路)。Production Prompt・コード・routing・注記/契約/Writer/RF本体は**無改変**。VALIDATEDでも採用・配線なし。

## (a) 挿入位置と隔離
- 決定論producer(`er053_b3_deterministic_producer_01`)の注記完了後、Writer R0入力生成前。B3選定(LLM)も注記producerも**再実行しない**(既存`er019_output/paycheck_personality/run_pp_01/storyline_b3/`をそのままcopyして使用=B3選定結果・中核数値は構造的に固定)。
- 新機能は**別ファイル(overlay)**に出力。注記md/sidecar/manifestは無改変(契約V3/V9のsha検証を壊さない。PRIOR_TRIAL_GATE_01 §3-3)。
- 実装(Trial専用、`er090_b3_core_number_rounding_trial_01_*.py`): `overlay.py`(純関数: 判定Prompt生成・出力検証・overlay生成・Writer入力差込・構造diff)、`run.py`(API実行)、`test_01.py`。Writerへの差込は `w1.build_r0_prompt` を**Trial runner内でのみ**ラップ(monkeypatch、呼出元プロセス限定。`er053_family_x_factlock_ja_writer_01.py`のファイル自体は無改変、sha記録)。

## (b) 丸め判断(新機能)
- 呼出: 1記事1回(gpt-6.1-sol、B3と同一model、`routing.require_model("FAMILY_X_STORYLINE_B3", ...)`、effort=high、JSON schema出力)。入力=確定済み`storyline`・採用Fact本文・sidecarの数値リスト(surface/kind/class/concept/ledger_ids)・参照Ledger記録(numeric_value/scope/conditions/notes_for_writer)。**判断対象=sidecarで`class=core`のconceptのみ**(周辺数値は「値同士の区別」確認用の読取り専用文脈。件数・対象・順序はLLMが追加/削除/並べ替え不可=検証で強制)。
- 出力: concept毎に `EXACT_REQUIRED` / `APPROXIMATE_OK`、surface毎の概数表記(`approx_surface`、EXACT時null)、理由、根拠Fact ID、該当した承認済み条件。**不確実なら`EXACT_REQUIRED`**(Promptで指示+検証failは全てEXACT_REQUIREDへfail-closed)。
- 判断基準=承認済み原文を**逐語**Promptへ埋込(新基準なし): Spoken-first Number Treatment(CURRENT_SPEC.md:1730)、Listener-Friendly Numeric Precision(`er003_v1_n3_01_evidence_compression_editor.LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK`をimportして逐語)、Numeric Precision既定(`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`逐語)。追加するのは出力形式指示・Ledger改変禁止・fail-closedのみ。
- 決定論検証(LLM出力の安全網、独自品質基準ではなく承認済み「通常の四捨五入で得られる近似値」[DECISION_LOG.md:14388]の機械化): (V1) conceptの集合==sidecar core conceptの集合(追加・欠落・重複なし) (V2) 各surfaceがsidecarのsurfaceと完全一致 (V3) APPROXIMATE_OKのapprox数値が元の数値の「通常の四捨五入(有効数字k桁、2<=k<桁数)」と一致 (V4) 単位語(人/件/回/ドル等)・限定語(最大/以上/超/未満/少なくとも)を維持 (V5) 概数ヘッジ語(約/およそ/ほぼ/前後/ほど/近く)を含む。(V6)根拠Fact IDが当該conceptのledger_idsに含まれる。違反はEXACT_REQUIREDへ降格しreasonに記録。
- ジャッジ入力に期待ラベルは含めない(ブラインド)。

## (c) Writerへの伝達(最小変更)
- 伝達先は既存の「Writerへの注意(事実ではありません)」ブロック(`writer_constraints`相当、R0 `[ニュース]`欄末尾)。APPROXIMATE_OKのconcept毎に1行を**追記のみ**: `- 事実{n}について：【概数表記】「{exact}」は「{approx}」と書いてよい。書く場合はこの表記に限り、他の丸め方・別の数字にはしない。`(n=sidecar factsでledger_idsから対応づけ)。Fact本文・【中核数値】印・sidecarは不変。EXACT_REQUIREDは**何も追記しない**(=従来Promptとバイト一致)。
- Writer R0 Prompt: 末尾に1項のみ追加(Trial wrapper): `8. 「Writerへの注意」に【概数表記】として指定された数字は、規則5の例外として、指定された表記で書けます(書くかどうかは文脈次第)。指定のない数字は規則5のとおり、丸めたり「約」「およそ」を足したりしません。` 規則5本文は無変更(例外節の追加で矛盾を避ける)。APPROXIMATE_OKが0件ならこの項も追加しない(Default no-op)。
- 【概数表記】はprompt内のみ。R1/R2 Promptは無変更(R1/R2はR0本文だけを入力に取る=概数表記がそのまま維持されるかを測る)。出力への漏れ(`【概数`)はTrial側の検査で確認。

## (d) 比較設計(同一入力でBefore/After)
- Before=既存Production run(`run_pp_01`)のR0入力(`build_r0_prompt`で再構成し`r0_meta.json:r0_prompt_sha256`と一致すること=入力再現性を確認、APIなし)。After=Beforeと同一storyline・同一news_text+overlay差込のみ。
- 構造diff(test固定、API 0): (1)採用Fact ID・件数・順序 (2)sidecar numbers(surface/class/concept/順序)・件数 (3)storyline_b3全ファイルのsha不変 (4)After news_text == Before news_text + 追記行のみ(行集合diff) (5)After R0 prompt == Before R0 prompt + 追記行 + 規則8のみ (6)EXACT_REQUIRED only入力ではPromptがバイト一致。
- Writer自然言語出力: After JA R0→R1→R2→Advanced→Standard を1回再生成。**対照(Control)**として、概数情報なしの同一Prompt(=Production同等)をもう1回、JA(R0→R2)のみ再生成し、自然な再生成揺れの大きさを測る(単一サンプル比較ではLLM揺れと丸め効果が分離できないため。JPY約13追加、必要十分と判断)。意味差分判定は gpt-6.1-sol(ラベル伏せ: 文書をX/Yにランダム割付、数値表現差/それ以外の意味差/構成差を列挙)+Sonnet通読。使用モデルはProduction Writerと同一系列のため、judge用は「最新上位系=gpt-6.1-sol」(25節: 最新世代の最上位系、同モデル由来バイアスの可能性を残存課題に明記)。

## (e) Fact Safety
- After Advanced/Standard英語本文に対し、(1)Trial専用にLDC(`er003_v1_en_direct_vfl_01_generate.run_deviation_check(hook_aware=True)`、既存関数・Prompt無改変、旧Fact Checkerは2026-10-10にProductionから撤去済みのためLDCを使用)、(2)Production検査であるRisk Flagger 4条件(`rf.run_risk_flagger`、Trial out_dirのみ・Review Queue保存なし)を実行。Before既存記事にも同一検査を実行し基準線とする(Beforeは既存RF結果あり、LDCのみ追加実行)。
- 単なる文字列差分と意味が変わるFact差分の区別: LDC `changed_number`/`deviations[].severity`の内訳と、本文の数値表現diff(Ledger値との四捨五入関係検査=決定論)を併記。

## (f) 丸めないケース(判断のみ。Writer再生成なし)
過去Production runの実Ledger/注記sidecarから、事前登録ラベル(判断前に固定、LLMには渡さない):
| # | 出典 | 数値(surface) | 事前ラベル | 根拠(承認済み条件) |
|---|---|---|---|---|
| A1 | 記事A F04 | 最大134,515人/134,515人 | APPROXIMATE_OK | ユーザー指定。精度自体に意味なし。「最大」「解析ごとに異なる」維持 |
| A2 | 記事A F04 | 11件 | EXACT_REQUIRED | 研究件数(小さい整数・数え上げ、丸め不能) |
| A3 | 記事A F07 | 3回以上 | EXACT_REQUIRED | 適格条件の閾値(「以上」) |
| A4 | 記事A F08 | +0.0630 | EXACT_REQUIRED | 同Factの+0.0589と並ぶ比較。丸めると0.06で同一視(値同士の区別)・研究結果の精度 |
| X1 | coffee_prices run_fxpw_01 F02 | 4.30(米ドル超) | EXACT_REQUIRED | 史上最高値の閾値(「超」) |
| X2 | coffee_prices run_fxpw_01 F02 | 2025年2月 | EXACT_REQUIRED | 日付 |
| X3 | boredom_aggression run_bape_01 F06 | 1,332(N) | APPROXIMATE_OK | 標本数(A1と同型の対照) |
| X4 | semiconductor_earnings run_devconfirm_01 F2 | 295億9,100万ドル | APPROXIMATE_OK | 売上高の聞き取り用概数(境界ケースとして記録) |
| X5 | boredom_aggression run_bape_01 F05/F06 | 5分 / 最大50 | EXACT_REQUIRED | 実験条件の回数・金額上限(正確さが条件の意味に直結) |
(X4は境界、報告のみで合否に使わない。それ以外の不一致=要因分析対象。)
各ケースの判断は元runのsidecarとLedgerを使い、**当該runのB3/Writerは再実行しない**。判断callは出典記事ごとに1回(A / coffee / boredom / semiconductor = 4回)、記事Aのみ安定性確認のため追加1回(計5回)。

## 評価指標(ユーザー§6)
① 判断妥当性: 事前ラベルとの一致(A4/X1/X2/X5はEXACT、A1/X3はAPPROX)、検証V1〜V6のfail件数、approxが意味語(最大/解析ごとに異なる)を落としていないか
② 伝達: overlay→R0 Promptの行の欠落/重複/誤適用0、R0〜R2〜英語での出現(指定表記の使用有無・変形)、【概数】漏れ0
③ 範囲限定: (d)の構造diff全件PASS、JA/ENのOutput差分をControl差分と比較
④ Fact Safety: LDC MAJOR数・`changed_number`、RF flag数/内容(After vs Before)

## 費用・時間見積(実績単価: run_pp_01/cost.json)
判断LLM 5call(約JPY0.5〜1.5/call) + After JA R0〜R2(約12.9) + Control JA(約12.9) + Advanced/Standard(0.32+0.32) + LDC 3〜4call(約0.3〜0.6/call) + RF 8call(約1.8) + 意味差分judge(約1〜2) ≒ **JPY 35〜45**。Guardrail JPY100(累計、超過見込みでSTOP)。日次(S0実測): 306.37円(`docs/pm/tools/daily_dev_cost_01.py`)。TTS/ASR/Research/新規テーマなし。
