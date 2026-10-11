# RESULT_02: JA記事品質 工程別モデル配置Trial(委任_05、Phase 3 coffee_prices / hormuz)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_05 / 2026-10-11 / DEV/Trial専用(Production code・Prompt・Routing・CURRENT_SPEC不変、Research/Ledger再実行なし、英訳・RF・TTS・Audioなし)
Status案: **MEASURED(N=1)**。hormuz=A/C/D/E 4案すべて完了。coffee_prices=A(既存再利用)/C/E完了、**D=R2記号QA STOP(R2再実行1回後も括弧残存、仕様どおり停止)**。B案は保留(対象外)。VALIDATED/採用はユーザーBlind評価後。
モデル: 全案 gpt-6-luna / gpt-6-astra / gpt-6.1-sol(各世代の現行。effort high)。

## 1. 比較表(再掲、B案は保留・今回対象外)
| 案 | B3 | R0 | R1 | R2 |
|---|---|---|---|---|
| A | Luna(coffeeは既存run_l3_01再利用¥0、hormuzは新規) | Luna | Astra | Astra |
| B | 保留(旧仕様再現不可。本Phase対象外) | - | - | - |
| C | A再利用 | Astra | Luna | Luna |
| D | Astra | Luna | Luna | Luna |
| E | Sol 6.1 | Sol | Sol | Sol |
決定論producer・契約・Prompt・effort high・developerはR0のみ・R2入力=R1 raw・記号QA(R2再実行1回)はMETA Phase 2と同一(無課金stub検査で両slug ALL_PASS、5ケースのrequest列/出力ファイル完全一致)。

## 2. 入力
- coffee_prices: Ledger=er019_output/coffee_prices/run_l3_01/research_ledger/verified_fact_ledger.txt(sha e94a50c1…、18件)。B3 topic=run_l3_01 full_ledger.jsonの英語theme(A既存と同一)。
- hormuz: Ledger=er019_output/family_x_refresh_e2e_01/hormuz/run_03/research_ledger/verified_fact_ledger.txt(sha 9bd6834e…、12件、2026-09-26取得。**事実鮮度は当時**)。B3 topic「ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応」=旧run_03 full_ledger.json記録と一致、かつProduction runnerは`--theme`でtopicを自由文字列指定する方式(er019_family_x_entertainment_production_runner_01.py L30/L386)でrun_03の記録topicと同じ文字列(ER-002 ADD03以来の正式topic)。不一致なし。

## 3. 実測円(記事×案×stage、円=USD×160、pricing_snapshot単価)
| 記事 | 案 | B3 | R0 | R1 | R2 | R2再実行 | 新規実測 | 点見積 | 保守cap | 状態 |
|---|---|---|---|---|---|---|---|---|---|---|
| coffee | A | 0.696(既存) | 0.543(既存) | 18.162(既存) | 19.664(既存) | - | 0(既存実測39.065) | 0 | - | 既存再利用 |
| coffee | C | 0(A再利用) | 42.499 | 0.080 | 0.080 | - | 42.659 | 64.72 | 97 | OK |
| coffee | D | 75.514 | 0.681 | 0.101 | 0.106 | 0.106 | 76.508 | 86.08 | 129 | **STOP(R2記号QA)** |
| coffee | E | 11.533 | 6.741 | 4.184 | 4.482 | - | 26.940 | 33.40 | 50 | OK |
| hormuz | A(新規) | 0.410 | 0.325 | 15.270 | 13.939 | - | 29.945 | 37.36 | 56 | OK |
| hormuz | C | 0(A再利用) | 46.126 | 0.092 | 0.104 | - | 46.323 | 50.58 | 76 | OK |
| hormuz | D | 51.731 | 0.496 | 0.087 | 0.088 | - | 52.403 | 64.80 | 97 | OK |
| hormuz | E | 7.209 | 7.332 | 2.284 | 2.590 | - | 19.415 | 26.66 | 40 | OK |
見積との差: 全案で点見積以下(点見積-実測: coffee C -22.1、D -9.6、E -6.5、hormuz A -7.4、C -4.3、D -12.4、E -7.2。点見積はMETA比出力・A実測由来のため全体にやや過大)。capを超えた案なし。
**Phase 3 新規課金合計 JPY294.19**(coffee 146.11[C42.66+D76.51+E26.94]+hormuz 148.09[A29.94+C46.32+D52.40+E19.42])。**Trial累計 JPY403.30 / 上限550(残146.70)**。全体残予算ゲート(既消費109.11+Phase3累計+他process予約+当該call見積≤550)は全callで通過。

## 4. 実行結果(actual model_id、受理)
- 全call: 返却model_idが要求モデルで始まる(gpt-6-luna / gpt-6-astra / gpt-6.1-sol)。モデル/effort/json_schemaの非受理(400系)なし。
- coffee D: R0/R1/R2は完了。R2(Luna、`w1_astra_r2`)出力に全角括弧「USDA（米農務省）」が残り、R2再実行1回(同一R1 raw入力)でも括弧が残存→`JASymbolCheckStopError`で停止(既存の記号QA機構どおり、上限回数を変更・回避せず)。rejected本文は`runs_02/coffee_prices/D/ja_writer/audit/rejected_w1_r2_symbol.md`(Blindページには使用しない)。各案1回のみの方針のため再生成していない。coffee DのR2は未受理=Blind比較に含められない。
- 他の6案(coffee A/C/E、hormuz A/C/D/E)は記号QA 初回/再実行とも発火なし(R0再生成・R2再実行ゼロ)。
- hormuz C は hormuz A のB3(Luna)をバイト再利用(注記済みB3/writer_constraintsの一致assert通過)。

## 5. 補助QA(人間判断の代替ではない。詳細 `AUX_METRICS_02_<slug>.md/.json`)
- 制約文混入grep・タグ残存・記号QA findings・R0 echo: 全受理記事で検出なし。
- 数値・英字固有名詞のLedger外: 全受理記事で「Ledger外の数値/英字」なし(カタカナ語は翻字ゆれ・比喩語で目視対象のみ、fact上の問題とは判断していない)。
- Fact忠実性の重大問題: **なし**(hormuz 4本・coffee A/C/E を Ledger の notes_for_writer と照合: 「提案した」表現、7/13と7/14の時系列、Brent 83.30/約2.6%/85ドル超、約9か月の見積り帰属、CPI 6.1%/8.7%の対象の区別は維持)。軽微: hormuz C本文・題に「通行料」「料金」(Ledgerは償還料/通航料。提案段階の表現として許容範囲)、coffee C本文に「、？」の句読点崩れ(postprocess由来の可能性、要目視)、E題冒頭の「！、」(同)。
- 選択Fact: hormuz A/C=HF-002,006,007,009、D/E=HF-002,007,009(Dは3件)。coffee A/C=COFFEE-003,009,010,014,015、E=COFFEE-001,010,014,015,018。D(STOP)=COFFEE-009,010,014,015,019。

## 6. Blind比較ページ
- hormuz: `user_test/ja_quality_model_allocation_02/hormuz/index.html`(4タブ、記事ごと独立seed=int(sha256("MAQ02:hormuz")[:8],16)=4088314252、対応表 `BLIND_MAP_02_hormuz.json`、漏洩検査OK、Pages 200+Playwright tab4/全文表示/leakなし/audioなし: `pages_playwright_evidence_02_hormuz.json`)。
- coffee: **未作成**(D欠落のため。選択肢: (i)A/C/Eの3本で作成、(ii)Dの扱いをFable/ユーザー判断)。seedは`int(sha256("MAQ02:coffee_prices")[:8],16)`=3330374777(4本でも3本でも同一seed、割当は本数で変わる)。

## 7. 未解決・判断事項
1. coffee D: 再生成(追加課金約76円)かD欠落(3本評価)かの判断。Luna R2が出典括弧を出しやすい傾向の可能性(N=1、断定しない)。
2. hormuz Ledgerは2026-09-26取得(鮮度は当時、比較目的には影響なし)。
3. B案は保留のまま。

## 8. 委任_06: Coffee D追加とコーヒーBlind比較ページ(課金0、2026-10-11)
- ユーザー指示により、coffee D案は記号QA STOPした R2(`runs_02/coffee_prices/D/ja_writer/audit/rejected_w1_r2_symbol.md`、「USDA(米農務省)」を含む)を**逐語のまま**評価対象R2として採用(`D/export/r2.md`は同ファイルのcmp一致コピー、sha256=7883dc289ee0f296958f201001a1ea161d49e3ab7a4fc49eb8ab088c184e310f)。
- **評価専用の扱い**: `D/TRIAL_EVAL_ONLY.md`に「記号QA不合格(全角括弧残存、R2再実行1回でも残存、JASymbolCheckStopError)・Trial評価専用・正式完成品ではない・Production経路ではSTOPとなる」を記録。Blindページには判定情報を表示しない。実際の残存は括弧「（」「）」(USDA（米農務省）1箇所)と波ダッシュ「〜」(約2〜3か月 2箇所)。
- コーヒーBlindページ: `user_test/ja_quality_model_allocation_02/coffee/index.html`(A/C/D/Eの4タブ、記事①〜④、独立seed=int(sha256("MAQ02:coffee_prices")[:8],16)=3330374777、対応表`BLIND_MAP_02_coffee_prices.json`(Blind評価後に開示)。漏洩検査OK、Pages 200+Playwright(tab4/各全文表示/leakなし/audioなし)=`pages_playwright_evidence_02_coffee.json`。
- D(評価専用)の補助指標(Fable内部): タイトル20字、本文849字(空白除く)、26文。Dは記号QA未通過のため、品質比較時はD案の括弧・波ダッシュ残存が評価にどう影響したかを別途Fableが整理する(Productionでは音声化へ進まない)。
- 追加課金0。Production・Prompt・Routing不変。

## 9. 全角括弧「（）」発生原因と予防策の整理(read-only調査、修正なし、2026-10-11 委任_06)
### 9-1. 現行の仕組み(確認した事実)
- **R0**(Luna)のuser promptには`SYMBOL_PREVENTION_BLOCK_JA`(`er019_family_x_ja_writer_o_r1_r2_01.py`、括弧「()」「（）」「[]」・波ダッシュ・三点リーダー・コロン・スラッシュの禁止、鉤括弧は対象外)が付く(`er053_family_x_factlock_ja_writer_01.py::build_r0_prompt`)。
- **W-1のR1/R2**(`astra_stage`)のuser promptは`USER_TMPL`(「以下の記事:…事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。」、系列X逐語・変更禁止)のみで、`SYMBOL_PREVENTION_BLOCK_JA`も禁止記号の指示も**含まれない**(確認: build_r0_prompt以外に同ブロックの付加箇所なし)。旧Writer(er019 ja_writer r1/r2)は`REVISION_INSTRUCTIONS+SYMBOL_PREVENTION_BLOCK_JA`を付けていたが、W-1(2026-10-10正式採用)の移植時にR1/R2側は`USER_TMPL`のみとなっている。
- 記号QA: R0はタグ付き本文で判定し、違反ならviolation note付きで1回再生成、残ればSTOP。R1出力には記号QAなし。R2は案A(判定は最終文、禁止記号が残ればR2のみ同一R1生出力で1回再実行、残ればSTOP、本文は手で直さない)。判定は`er003_audio_tts_asr_safety.detect_prohibited_symbols`: 括弧=`[()（）\[\]]`、スラッシュ、URL/メール、絵文字(Unicode So)、残存placeholder=`[〜～]|…+|\.{3,}|[:;：；]`(時刻H:MMコロンは許容)。STOP対象は括弧/スラッシュ/URLメール/絵文字/placeholderの5カテゴリ。
### 9-2. 履歴(DECISION_LOG)
- TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(2026-09-27)でLayer1(Prompt予防)/Layer2(Validator)/Layer4(TTS直前Gate)を導入。FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(2026-09-28)でOPEN-227「R2 must-fix経路のSYMBOL_PREVENTION_BLOCK_JA非対称性」を起票。W-1採用: RISK-FLAGGER-PRODUCTION-WIRING-01 委任_04(2026-10-10)。
### 9-3. Production経路での発生実績(runtime_evidence.jsonのsymbol_qa)
- 走査可能な16 run(Production coffee run_l3_01/stdregen、meta regen、semiconductor devconfirm、Trial A/C/D/E各run含む)で、R0/R2 first attemptの記号finding=0件、再実行発動=0件。モデル別: Astra R1/R2=7 run(0件)、Luna R1/R2(C・D案)=5 run(0件)、Sol(E案)=3 run(0件)。**今回のcoffee D=Luna R1/R2で初の記号QA不合格(1件、R2再実行でも残存)**。`rejected_w1_r2_symbol.md`はリポジトリ全体でこの1件のみ。N=1の観測でありLunaの傾向とは断定できない。旧Writer経路の過去実績はDECISION_LOGの個別記録(Meta STOP実例A2 japanese_title「…」等)に限られ、全数集計は未実施。
### 9-4. 今回D案(R2=Luna)の発生箇所と経路
- R0(Luna)出力は括弧0・「〜」0(「USDAの…」「約2か月から3か月」)。**R1(Luna)出力で初めて**「USDA（米農務省）のブラジル現地報告」「約2〜3か月」が出現(=Luna R1がUSDAに説明括弧を付け、範囲表現を〜に変えた)。R2初回・R2再実行はR1生出力を入力とするため両方で引き継がれ、再実行でも消えなかった。
- Fact側: selected_brief.mdに全角括弧・「〜」なし(COFFEE-009/010は「USDA」「約2か月から3か月」等の表記)。writer_constraints.txtに半角括弧「(事実ではありません)」が含まれるが、R0出力・R1出力への混入は確認されず(R0は括弧0)。つまり括弧・〜はFact由来ではなくR1でモデルが追加したもの。
- 文脈: 「USDA（米農務省）」=組織略称の初出時の説明括弧。
### 9-5. 原因仮説(確認できた範囲と未確認)
1. (確認)括弧・〜はR1段で初出。R1/R2のpromptには禁止記号指示がない(W-1のUSER_TMPLは逐語固定)ため、モデルは「新聞記事風の略称説明括弧」「範囲の〜」を自然に出す。R0は予防ブロックがあるため0件。
2. (仮説・N=1)Luna R1が略称に説明括弧を付ける傾向。Astra/Solでの発生0件(15 run)との差は、モデル差かprompt/記事内容差か切り分け不能。
3. (確認)再実行は同一R1生出力を入力にするため、R1に括弧があるとR2再実行でも消えにくい(案Aの構造上の限界)。D案では再実行でも括弧・〜が両方残った。
### 9-6. 予防策候補(生成段階で出さない。Rewriteによる事後修正は優先しない。いずれもユーザー承認までTrial/Production実施なし)
| 候補 | 内容 | 影響範囲・リスク | 費用 |
|---|---|---|---|
| P1 | R1/R2のuser promptへ`SYMBOL_PREVENTION_BLOCK_JA`を追記(旧Writerと同型) | `USER_TMPL`逐語固定の変更=W-1 Prompt変更(Opus独立レビュー条件対象の可能性、事実忠実性・記事品質への影響をTrialで測る必要)。R1/R2出力の長さ・語調が変わるリスク | Trial数記事×R1/R2分(Astra既存実績で数十円/記事) |
| P2 | 略称・固有名詞の表記ルールを明示(「USDAは米農務省と言い換えるか、略称だけ使い、括弧で説明しない。『USDA、すなわち米農務省』と書く」「範囲は『2か月から3か月』」) | P1に併用可。Fact Lock表記一致(ledger逐語)との整合確認が必要 | P1と同じ(追記のみ) |
| P3 | R1直後にも記号QAを入れ、違反ならR1のみ再実行(再実行をR2でなくR1で行う) | 新しい処理フロー=Opus独立レビュー必須(条件A)。再実行回数が増える=既存安全装置の拡張(上限回数・予算の再設計) | 発生時のみR1再実行分(約18円/回、Astra実績) |
| P4 | Structured Output/出力schemaで禁止文字をpattern制約 | APIがpattern制約に対応するか未確認。タイトル/本文の自由生成品質への影響不明 | 要調査(技術確認のみ無課金可) |
| P5 | R0のLuna段階のみ予防ブロックがある現状を、全段(R0/R1/R2)で一貫させる設計整理(P1/P2を含む上位案) | OPEN-227(R2 must-fix経路の非対称性)と同根。整合の再点検が必要 | 設計のみ無課金 |
- 事後修正(Local Rewrite等)は優先しない(ユーザー方針)。まずP1〜P5の設計比較(無課金)をユーザーに提示し、承認後に新規Trial(OPEN-261)を行う。
