# PREREGISTRATION_01: Trial計画(事前登録案。結果を見る前に固定する。Phase 2はユーザー/Fable承認後)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01。本書はPhase 1成果物であり**Trialは未実施**。承認前に有料APIを呼ばない。結果を見てからの基準変更・Prompt修正・再Trialは禁止(変更が必要なら新たな事前登録+ユーザー承認)。

## 1. 比較する腕

| 腕 | 内容 | LLM call | 備考 |
|---|---|---|---|
| C0 Control-frozen | 既存の`brief_original.md`(g0_real_annotation_01、各テーマ1本) | 0 | 既出力の再解析 |
| C1 Control-fresh | **現行B3 Prompt(Production module未改変import)**で同一台帳から再生成、各テーマ2 rep | 18 | 「混入はB3のサンプリング次第でどの程度出入りするか」を測る=案の効果とサンプリング差を切り分ける |
| D | 決定論assemble(DESIGN_01 2節)。入力は**C0とC1の`selected_fact_ids`(27通り)**を再利用。D-min(claimのみ)とD-full(claim+scope+conditions)の2変種 | 0 | 追加費用なし。B3選定は変えない |
| A' | B3 Prompt/schemaの**Trialコピー**(Factのみ指示、Storyline再掲なし)+制約は決定論転記、各テーマ2 rep | 18 | Productionファイルは不変。Promptの差分を`PROMPT_DIFF.md`に保存しshaを記録 |

テーマ: 正式9テーマ=問題5(semiconductor_earnings / small_bag / space_weapons / hormuz / central_bank_mortgage)+正常系4(meta / byd_recall / openai_copyright / streaming_price)。台帳は凍結(`g0_real_annotation_01/<slug>/shared/ledger.txt`のsha256を実行時に照合)、topicは`shared/topic.txt`。Research/Ledger工程は再実行しない。

## 2. 評価項目(全て決定論スクリプト+差分一覧。LLM判定を使わない)

| ID | 項目 | 方法 | 事前登録の合格基準 |
|---|---|---|---|
| E1 | Selected FactsにFactだけが残るか | Facts節の文を命令形/禁止形パターンで検出(検出器は`trace_5themes.json`の手作業ラベル10件に対し再現率10/10を確認してから使う。ただしこのパターンは同10件を見て作ったため過学習の可能性があり、**A'の全Facts文(推定約100文)は人間(Fable/Claude)が全件目視**する) | D: 全27出力で0件。A': 18出力中17以上で0件、残1は内容が許容される事実の限定かを目視で判定 |
| E2 | 指示・制約が別欄へ正しく移ったか/Writerに必要な制約が消えていないか | 採用factごとの台帳`notes_for_writer`が制約ブロックに**文字列完全一致**で存在するか。C0/C1のbriefにそのnotesが届いていた件数(逐語級12字一致または目視)と比較 | D・A': 100%(転記は決定論) |
| E3 | Fact本文の欠落なし/数値の非破壊 | 採用factの`claim`中の数字・日付トークン(全角→半角正規化)がFacts節に全て存在し、Facts節に台帳に無い数字トークンが無い | D: 100%。A': 95%以上、欠落・新数字は全件列挙し重大度を目視判定 |
| E4 | 主体・対象・因果・時系列の非破壊 | (a)claimの固有名詞/組織名トークンの包含率 (b)因果接続語(ため/から/により/受け/原因/理由/ことで)の出現数がclaimから増えていないか (c)日付出現順がclaimと同じか。差分を一覧化し、問題5テーマは全差分を人間が目視 | D: (a)(b)(c)全て差0(逐語のため)。A': 差分は全件目視、意味を変える差分0 |
| E5 | 既存B3(C0/C1)との情報欠落比較 | C0/C1のFacts節に含まれ、新Facts+制約のどちらにも無い語句(3文字以上のn-gram差、固有名詞・数字優先)を一覧化 | 欠落が「B3の言い換え由来」か「台帳に無い追加」かを分類。台帳に根拠のあるFact情報の欠落=0 |
| E6 | Fact Lockが必要情報を受け取れるか(乾式) | (i)`parse_brief_md`成功 (ii)`dryrun_annotate`の`【事実N】`数==Fact行数 (iii)`jaw.build_original_prompt`+`fl.build_r0_block`でR0 Promptを組み立て(API無し)、R0テンプレートshaがProduction版と一致、制約ブロックがちょうど1回含まれ、各Fact行が`【事実N】`付与対象として現れる (iv)Fact行内に`【`が無い | 全項目PASS。1つでも不一致ならSTOP報告 |
| E7 | B3注記LLM不要化の可否(報告のみ、合否なし) | 注記仕様v2のうち決定論化できる範囲を表にする(【事実N】とledger_ids対応=Dで決定論か、数値印の種類/概念=残るか)。既存`b3_annotation_check_01`の期待値計算が使える範囲を確認 | 「可能/部分的/不可」とその理由、別管理ID候補の提案のみ |
| E8 | 追加コスト・処理時間・実装複雑性 | 実測¥(cost logger)、B3 latency(runtime_evidence)、assembler/テストのLOC、変更ファイル数 | 追加LLM call=0(A'・Dとも)。B3 1 callの¥が現行比+20%を超えない |

任意(既定OFF): **E9 Writer R0乾式の有料確認** 問題5テーマ×{C0 brief, D}×R0のみ1 rep=10 call。目的=Writerが制約行へ`【事実N】`を付けないか/制約文を記事に転記しないか/R0冒頭復唱の増加が無いかを`detect_r0_echo`・タグ検査で測る。費用見積¥3前後(推定。根拠: 過去のR0単価¥0.24〜0.26[`DECISION_LOG`のja_original]は旧モデル時の値で、gpt-6-luna実測は未取得のため**推定**)。実施にはFable/ユーザー判断が必要(原則なし)。

## 3. 判定ルール(事前登録)

- D「Trial限定のVALIDATED候補」: E1〜E6を全て満たし、人間目視で「台帳に根拠のあるFact情報の欠落0」「意味を変える差分0」、STOP条件(5.)に該当しないこと。
- A'「同候補」: E1(17/18)・E3・E4を満たし、E6 PASS。Promptに従わなかった場合は後段補正AIを足さずに**不採用**。
- DもA'も満たさない場合: `REJECTED`として原因を報告(Prompt修正・再Trialは新たな事前登録+承認が必要)。
- いずれの場合も**Production採用はユーザーだけが承認**(`USER_DECISION_REQUIRED`)。Trial結果は`VALIDATED`止まりで`APPROVED_FOR_PRODUCTION`と誤認しない。

## 4. 費用見積(根拠付き)と予算

| 項目 | 内訳 | 見積 |
|---|---|---|
| C1 Control-fresh | 9テーマ×2 rep=18 call × B3実測平均¥0.50(範囲¥0.38〜0.60。`stage_r/cost_by_theme.json`の10テーマ) | 約¥9(上限18×0.60=¥10.8) |
| A' | 9×2=18 call × 約¥0.50〜0.60(Prompt差分は短く入力は同程度、出力はbrief短縮でむしろ減る可能性。未測定のため上限側で見積) | 約¥9〜11 |
| D・評価・乾式 | 決定論・ローカル | ¥0 |
| **基本合計** | | **約¥18〜22** |
| 技術retry込みの最悪値 | 全36 callが各1回retry(B3の既存仕様は技術retry1回のみ) | 約¥43 |
| **予算ガード案** | Cap ¥40(超過見込みで即STOP)。到達しても単純な超過ではなくSTOP報告 | |
| 任意E9 | R0 10 call | 約¥3(推定、上記) |

使用モデル(最新モデル原則への記載): B3は本番ラインと同一の`gpt-6-luna`(`er006_model_routing_contract_01.py` L48 `WRITER_MODEL`、実測`model_id_actual=gpt-6-luna`)。gpt-6世代で最新世代だが、最上位系かは本委任では確認していない。例外理由=本Trialは「本番B3の挙動を変えずにPrompt/構造だけ変えたときの差」を見るため、本番と同じモデルで比較することが採用判断の前提になる(最上位系での評価は本番ライン選定の別判断)。Trial実行時に`requested/returned model`の不一致があればSTOP。

## 5. STOP候補判定(Phase 1時点)

| 条件 | 判定 | 根拠 |
|---|---|---|
| 混在が正式仕様で、分離が他の重要仕様を壊す | **非該当(ただし要注意)** | 混在を規定する正式仕様は見つからない(INVESTIGATION_01 3節)。一方でFact Lock R0規則4と注記仕様v2は混在を前提にした規則を持つ。制約ブロックを**ニュース欄に残す**設計(P-out)なら規則4は成立し、注記契約V1〜V10も不変 |
| Research/Ledger仕様変更が必要 | 非該当 | 台帳の既存欄をそのまま使用。案E(Researcher欄分割)は採らない |
| 新LLM工程の追加が必要 | 非該当 | D・A'とも追加call 0 |
| Production Promptの変更が必要 | **該当(採用時)** | A'はB3 Prompt変更。DもPrompt手順5/schemaの`selected_fact_brief`を不使用化。**Trialはコピー上で可、Production採用はユーザー判断** |
| W-1承認仕様との矛盾 | 条件付き非該当 | R0 Prompt不変(データ連結のみ)。P-inを選ぶと注記契約V4/V5/V10の拡張が必要になるため**P-outを前提**。Lane A(委任_07進行中)とrunner R0入力組立の編集箇所が競合しうるため調整が必要 |
| 有料Trialが大きい | 非該当 | 基本約¥18〜22、Cap ¥40 |
| 別の新仕様判断 | **該当** | (1)B3 briefを決定論生成に変えること(ユーザー確定事項(7)の読み方に依存) (2)制約ブロックをR0へ別連結すること (3)`ambiguity_note`と、notes内の記述的限定(central_bank F003等)の置き場所 (4)Storyline行内の書き方指示(space)を対象にするか (5)BYD型で従来Writerに届いていなかったnotesが新たに届く=Writer入力の増加(B3導入前の状態への回帰) |
| Opus独立技術レビュー | **必須(条件A: 新しい構造・処理フロー)** | Phase 2実装前にFableが手配 |

## 6. 並列化・直列化(PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01)

- クリティカルパス: assembler/evaluator実装(1〜1.5h) → B3 API実行(約6分) → 評価(約30分) → 人間目視+報告(約1h)。合計約3〜3.5h。
- 並列化: ①実装中に評価基準スクリプト・差分一覧生成・目視用テンプレートを先行作成 ②C1(18 call)とA'(18 call)は互いに独立で、台帳・topicが凍結のため条件同一性を保てる。6 process並列(各自の出力dirと費用台帳、共通Capは親が合算)で36 call×約50秒を直列約30分→約6分に短縮(約25分短縮) ③Dはreplayのため、C0・C1完了を待つ部分(C1の選定結果依存)だけが直列。
- 直列にする理由: D(C1選定依存)は前工程出力依存。費用Cap確認は各process開始前の予約方式で、同一state競合を避けるため費用台帳はprocess別ファイルにして最後に集計。

## 7. 成果物の保存先(新しい置き場所を作らない)

`er052_output/b3_fact_instruction_separation_trial_01/`(本ディレクトリ)配下: `armD_preview_01/`相当を`runs/<arm>/<theme>/rep<n>/`へ拡張、`eval/`に評価結果、`RESULT_01.md`。REPORTへの記載(§番号)はPhase 2完了時に追記。
