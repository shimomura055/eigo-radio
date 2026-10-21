# Trial設計 TRIAL_DESIGN_02(委任_03: 判断LLMのLuna化 + Ledger整合性N増し検証。有料実行前にcommit)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 / 2026-10-22
ユーザー原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_LUNA-NINC_USER.md`(本文3,588字、sha256[本文のみ]=4bb9d283...e7330)
前提(整合確認済み): `PRIOR_TRIAL_GATE_01.md`(否定的結果なし)、`TRIAL_RESULT_01.md`(Sol判断・記事A)。性質=Trial(Trial専用経路、Production無改変、VALIDATEDでも採用/配線なし)。

## 0. 現行Production Fact経路の実態(照合: コード直読)
| 段 | 実体(ファイル:行) | 停止/非停止 |
|---|---|---|
| 中核数値の機械選定 | `er053_b3_deterministic_producer_01.py` `produce_annotated_b3`(:843) | 契約違反=課金前STOP。本Trialは無改変でそのまま実行(API 0) |
| Writer 規則(5) | `er053_family_x_factlock_ja_writer_01.py:86-93`(丸め・約追加禁止) | Promptのみ。**出力の数値を機械的に拒否する検査はWriter内に無い**(grep: number検査関数なし) |
| Writer停止条件 | 同:54 `JASymbolCheckStopError`(記号QA、R0/R2各1回再生成後STOP)、:50 `TagLeak`、:46 `ProvenanceViolation` | **STOP**。丸め追加で新規発火しうる箇所=`【概数表記】`の漏れ(`TAG_LEAK_RE`:102は`概数表記`を含まない=漏れても検知されない。Trial_01 S5) |
| 英語記事のFact検査 | `er053_risk_flagger_production_01.py` Risk Flagger(Luna×2+Gemini×2の4条件)。**非Blocking**: 合否判定せず、結果はReview Queue(Human Review)へ(同:7、runner:305-345) | **STOPしない**。丸めの影響は「Human Review対象flag数」として現れる |
| 旧Ledger Deviation Checker | `er003_v1_en_direct_vfl_01_generate.run_deviation_check` は2026-10-10にFamily X Productionから撤去済み。**Trial専用の追加参考検査としてのみ併用**(それだけで運用可と判断しない) | Trial限定 |
=> 「Productionの最終判定・停止」= (a)Writer STOP(記号QA/TagLeak/Provenance)と再生成retry、(b)Risk Flagger flag→Human Review増分。数値の機械Gateは存在しないため、**Trial専用の決定論数値監査(下記)を追加してRiskの見逃し有無を測る**(Productionへは入れない)。

## 1. データセット(ユーザー§3、API 0。`er090_b3_core_number_rounding_trial_02_dataset.py`)
既存B3出力(research_ledger+storyline_b3)を `er090_output/b3_core_number_rounding_trial_02/dataset/<art>/` へcopyし、Production決定論producer(無改変)で中核数値を機械選定。同一Ledger sha=同一記事として重複除去、同一Ledger内は中核数値が最多のbrief。同テーマの別Ledger重複(hormuz/sewer/space_weapons)はmanifestに残すが対象外。
- 独立記事(distinct Ledger)=**18**、テーマ=**15**(coffee×2・ai_control×2・mey×2が同テーマ別Ledger)、Fact(採用)=**75**、中核concept=**71**(表記75)。**人工fixture 0**(7カテゴリが実中核数値で充足)。
- 7カテゴリ充足(`evidence/coverage.json`、表記の機械分類。重複該当あり): C1大きな人数/金額=16、C2小数/割合/精度=28、C3閾値・限定語・近接比較=14、C4日付/回数/小数量=23、C5同一Factの複数数値=54、C6既に「約」=9、C7同形・文脈で適否が分かれる対=5組。
- **偏り(正直な記載)**: 事前ラベル A(概数化可)=5・E(厳密維持)=58・B(境界、合否除外)=8。機械選定の中核数値は大半が厳密維持側で、「丸めるべき」正解の母数は小さい(Aの正解率は粗い推定)。Eの母数が大きいため「丸めてはいけない」側の安全性(過剰丸めなし)は比較的よく測れる。ユーザー定義が「丸めない」寄りの運用であることとは整合。
- ラベル(`er090_b3_core_number_rounding_trial_02_labels.py`): **判断LLM実行前にcommit**。基準=承認済みSpoken-first/Listener-Friendly条件の人間読み替え(A=精度に意味が薄い大きな数量で四捨五入が意味・閾値・比較を変えない/E=日付・小整数・閾値/限定語付き・価格/金利/率・近接/合算関係・既に概数/B=人間でも割れる境界)。LLMへ非開示。

## 2. Phase 1: Sol対Luna(9件評価セット再使用)
- 評価セット=Trial_01の4記事(A paycheck / coffee / boredom / semi)の判断。Luna(`gpt-6-luna`、正式routing `er006_model_routing_contract_01.py:45-51`のLuna、単価USD0.1/0.5 per MTok[`pricing_snapshot.json`]、Sol 6.1=USD2/10 per MTok)に**Trial_01と同一Prompt**(`build_judge_user_prompt` byte一致をtest/`evidence/prompt_manifest.json`で確認。semiのSol基準のみv1 Prompt版→公平比較のため**Sol v2を1回再実行**)・同一JSON schema・同一effort=high・同一V1〜V7を適用。実response.modelとusage/料金を記録。
- 追加比較: Luna effort=medium/low(出力項目/token最適化の候補。Prompt・判定基準の意味は変えない)。品質が十分(事前ラベル一致が劣化しない)になった最安設定で探索停止(ユーザー§8)。不足時のみ原因分析→最小改善(1〜2回、基準引下げ禁止)。
- モデル例外理由(25節): ユーザー指示による原価低減Trial(`require_model_or_override`のoverride_reason記録)。

## 3. Phase 1b: 全dataset(18記事・71concept)でLuna判断(Writer未実行)
正解率(A/E、B除外)、過剰丸め(EをAと判断)=安全側誤り、丸め漏れ(AをEと判断)=品質側、V1〜V7降格件数、粒度、反復安定性(同条件を最大3回)。

## 4. Phase 2: Writer→R0/R1/R2→Advanced/Standard(text経路のみ、TTSなし)
- 対象記事: Phase 1bで最終APPROXが1件以上の記事から最大4本(カテゴリ多様性優先)。APPROXが0件の記事はWriter Promptが従来とbyte一致(Trial_01 test)=Control同一のため再生成しない(決定論で証明)。
- Control(現行)とLuna丸め版を**同一入力(同一コピー)・同一モデル・同一条件**で各1回(Trial_01と同じoverlay方式=`w1.build_r0_prompt`をTrial runner内のみラップ、Production file無改変)。既存Before出力があれば参考として併記。
- 現行Production Fact経路の最終判定: Writer STOP/再生成retry回数(Controlとの差)、Risk Flagger flag数と丸め文の関与(Human Review増分)。旧LDCはTrial専用追加参考検査。
- **Trial専用の決定論数値監査(新規、Productionへ入れない)**: JA R2/Advanced/Standardの全数値トークンを抽出し、(i)中核数値の厳密値 (ii)指定概数 (iii)それ以外 に分類。(iii)=規則(5)違反(指定外丸め・周辺数値・新規数値)。EN側は表示精度で厳密値・概数と照合し、JA R2に無い数字(翻訳段の逸脱)も検出。指定概数に付随する限定語(最大/以上/超等)の保持もsurface逐語一致で確認。
- NG分類(ユーザー§5): ①丸めによる真のFact変化 ②Checker誤NG(丸めは正しいがflag) ③丸め以外のWriter揺れ ④見逃し。④は**既知NGの注入テスト**(Luna丸め版Advanced記事の指定概数を意図的に誤丸め/限定語落とし/閾値反転した合成記事)を現行RFへ流し検出率を測る(Controlが検出できる範囲の把握)。
- 再現性: RFは確率的のため同一記事のRF反復は費用内で最小限(各記事×level 1回+注入テスト)。サンプル数の限界は結果文書に明記。

## 5. 費用・時間見積(出典付き。実測単価はTrial_01の `evidence/cost_by_stage.json`、単価は `pricing_snapshot.json`)
| 工程 | 数量 | 単価の出典 | 見積JPY |
|---|---|---|---|
| Luna判断(Phase1: 4記事×3設定+Phase1b: 18記事×最大3rep) | 約66call | Sol記事A=4.30/call(Trial_01実測)×Luna/Sol単価比1/20(入力1/20・出力1/20)=約0.2〜0.3/call | 約15〜20 |
| Sol v2 semi再実行(公平比較) | 1call | Trial_01 A_rep1実測の同規模 | 約4〜5 |
| Writer R0〜R2(Control+Luna版) | 4記事×2arm | Trial_01 実測 After 11.2/Control 13.5(R0 6.1-8.0,R1 2.3-3.5,R2 2.0-2.1) | 約100 |
| Advanced/Standard英訳 | 4記事×2arm | Trial_01実測 0.77/arm | 約6 |
| Risk Flagger 4条件×2level | 4記事×2arm | Trial_01実測 約1.7/arm | 約14 |
| 旧LDC(参考) | 4記事×2arm×3文書 | Trial_01実測 0.2〜0.35/call | 約7 |
| 既知NG注入テスト(RF) | 約6合成記事 | 同RF実測 | 約6〜8 |
| 合計(予備1.3倍込み) | | | **約210〜230**(JPY300以内。Phase1〜2合計がJPY300を超える見込みが出たら有料工程前にSTOP) |
日次(JST、`daily_dev_cost_01.py --date 2026-10-22`): 開始時6.32円 + 上記 < 1,000円。時間: Luna判断はLuna 1call約10〜60秒、Writer R0〜R2は約4分/arm(並列可)、全体を並列化(articleごとに独立process、同一log汚染なし)。

## 6. 禁止/不変(ユーザー§7)
B3本体Fact選定・構成判断、機械的中核数値選定/上限/優先順位、Ledger数値、Production Writer Prompt/Validator/Risk Flagger、Family X/Z正式経路は無改変(Production .pyのgit diff 0をtestとgit statusで確認)。CheckerがNGを出すことを理由とした判定緩和はしない。新基準/Validator緩和/Fact Lock仕様変更が要る場合はProductionへ適用せず、原因・対策候補・誤PASSリスク・QCD影響を整理して提案のみ。
