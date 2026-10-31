# JA-GLOSS-NUANCE-01 Trial_01 (TRIAL_01)

管理ID=JA-GLOSS-NUANCE-01 / OPEN-630 / 委任_01 / 2026-10-31。DEV/Trial専用(Production Prompt・Gate・コード変更0、記事・音声の再生成0)。
**Status案: VALIDATED(条件付き。ただし事前登録した厳格基準のC2・C3は未達で、再登録したnoise込み基準H1〜H3で達成。経緯と限界は§5・§6)。採用はユーザー判断。**

## 0. 方法

| 項目 | 内容 |
|---|---|
| 比較 | A=現行Prompt(保存済み実入力をそのまま再生。現行Production文面[NEWGEN_MEANING_TEXT]と一致をassert)。B/B2/B3=改善案(NEWGEN_MEANING_TEXT内のjapanese_gloss欄を差替え+「訳語の選び方」欄を追加。他は1字も変えない)。文面=tools/gloss_nuance_trial_01.py の NEW_JG_BULLET/NEW_CHOICE_BULLET(B)・B2_*・B3_* |
| 呼出 | Productionと同一(responses API・reasoning=high・developer=NEWGEN_DEVELOPER_MESSAGE・schema=NEWGEN_JSON_SCHEMA。make_alignment_fnと同じ) |
| 入力 | 保存済みの実入力(gloss_alignment_prompt.txt)。対象=untidiness b1b(12 item、本番入力と同一)。副作用確認=moon・jwst・aichat・meta(X Adv、各10〜12 item)。確認用held-out=coffee・yemen・island・part2(X b1b、各6〜8 item、対象記事・改善案作成に未使用) |
| 反復 | 対象記事はA,B,B2,B3とも3回。副作用4記事はA2回・B3 2回(Bは1回、B2は未実施)。held-outはA1回・B3 1回 |
| 評価 | 本agent(Claude Sonnet 5.5)。A/Bの順を乱数で伏せた表で、arm開示前に良否を付与(blind_sheet*.json/blind_labels*.json/blind_mapping*.json)。**verdict(対象item)は結果を既に見ているため非盲検**。単独ラベラー |
| 事前登録 | trial_01/PREREGISTRATION_01.md(API呼出前に作成。追記1は確認Trial前に追記) |
| 再現 | tools/gloss_nuance_trial_01.py(再生)・tools/analyze_trial_01.py(表・盲検表・検査)・tools/stage2_check_trial_01.py(後段自己検査案)。出力=trial_01/out/*.json(response_id・usage・費用を含む)、台帳=trial_01/ledger.json |

### 使用モデル(PM_GOVERNANCE.md 25-3)
| 使用モデル名 | 最新モデルか | 最新でない場合の理由 |
|---|---|---|
| gpt-6-luna(生成・再生。reasoning=high) | 最新世代の効率系(最上位=gpt-6-astra・推奨=gpt-6.1-solではない) | 25-1例外2『ライン組み込み候補の性能確認』: 改善案はProduction gloss段のモデル(er006_model_routing_contract_01.py:50 SUPPORT_MODEL=gpt-6-luna)で効くかを見る必要があるため。gpt-6.1-solは単価が20倍(output $10 vs $0.50 / 1M)で、1call約¥0.6が約¥12になり量産単価70円/記事セットを圧迫するため、モデル格上げは設計案から外した(DESIGN_01.md)。実測でもluna自身がPrompt変更で解けたため格上げは不要 |
| 評価者=本agent(Claude Sonnet 5.5) | 最上位ではない(Fable/Opus 5.5が上位) | 実務上の制約(API評価者の費用をCap内に収めるため)。独立した第2評価者(gpt-6.1-sol等)は未使用。限界として§6に記載 |

## 1. 対象 verdict の結果(最重要)

| 案 | 回 | gloss | naive_ja / conveys |
|---|---|---|---|
| 保存済み本番出力 | - | 結論 | 評決 / partly |
| **A 現行Prompt** | r1 | 結論 | 評決 / yes |
| A | r2 | 最終的な判断 | 評決 / partly |
| A | r3 | 結論 | 評決 / yes |
| B(partlyだけ緩め) | r1〜r3 | 結論 / 結論 / 結論 | 評決 / yes,partly,yes |
| B2(yesも緩め+一般語確認) | r1〜r3 | 最終判断 / 最終的な判断 / 最終判断 | 評決 partly, partly / 判決 yes |
| **B3(1語は見出し訳+比喩の像を保つ+一般語確認)** | r1 | **判決** | 評決 / yes |
| B3 | r2 | **判決** | 評決 / yes |
| B3 | r3 | **評決** | 評決 / yes |

- **現行(A)は裁判語に0/3**(保存本番値を含め0/4)。結論が2/3で再現。偶然ではない。
- B3は裁判語に3/3(判決2・評決1)。reasoning例(B3 r1)「記事全体の裁判の比喩を保ち、最終的な判断を表す「判決」としています」。
- 同じgpt-6-lunaで変わった=**原因はモデルではなくPromptの規則**(CURRENT_STATE_01.md §3)。
- B3が「判決」を出す回が多く「評決」は1/3。最適は評決(CURRENT_STATE_01.md §4)だが、判決も許容語。1語に収束させる追加Promptは作っていない(個別語の指定になるため)。

## 2. 改善案の反復ログ(探索段階)

| 案 | 変更点 | 対象verdict | 次の判断 |
|---|---|---|---|
| B | partly/noの分岐に「naive_jaが定訳で本文でも通じるなら使ってよい」+近義語対比+「原則1訳語、重要ニュアンスが落ちる時だけ2つ」 | 結論3/3(変化なし) | yes分岐の『そのまま写さず』が残っている(原因R1)ため無効 |
| B2 | B+yes分岐の『無批判に写さず』へ緩和+「一般語に当たる日本語と同じなら限定的な訳へ」 | 最終判断系3/3(結論から離れたが裁判語0/3) | 比喩の像を剥がす規則(原因R2)が残る |
| B3 | (1)1語のkey_phraseは見出し訳が自然で本文でも通じるならそのまま使う(上位語・説明文化しない)。2語以上は従来文面(anti-anchoring維持)(2)記事全体の比喩の中の語は像を保つ見出し訳を優先(3)一般語と同じ日本語にならないか確認(4)原則1訳語、2つは重要意味が落ちる時だけ | 判決/判決/評決(3/3) | 副作用を確認へ |
- 注意: B3は対象記事で3回の調整を経た。対象itemへの過適合を避けるため、(a)Promptに対象語・近い法律語を入れていない(例示はboast/sprint/stroll/gulp等。対象4記事+held-outに出現しないことをgrepで確認)、(b)調整に使わなかった他4記事とheld-out 4記事で副作用を見た。

## 3. 副作用の確認(対象以外のitem)

### 3-1. 盲検対比較の集計(B3 vs A、同一入力。対象verdictを除く)
| 比較 | 対象 | item数 | 差のあったitem | B3が良い | Aが良い | 同等(同一含む) |
|---|---|---|---|---|---|---|
| A r1 vs B3 r1 | 5記事 | 55 | 26 | 8 | 4 | 43 |
| A r2 vs B3 r2 | 5記事 | 55 | 35 | 11 | 4 | 40 |
| (基線) A r1 vs A r2 | 5記事 | 56 | 37 | A2が良い6/A1が良い6 | | 44 |
| held-out A vs B3 | 4記事 | 29 | 20 | 3 | 3 | 23 |
| **合計(B3 vs A)** | 9記事 | 139 | | **22** | **11** | 106 |
- B3が悪化した例(Aが良い、各比較で4件。重複あり): 〜かどうかを「試して確かめない」(do not test whether、冗長)、equivalent width→「光の線の強さを表す幅」(等価幅の語が消える)、complications→「複雑さ」(Aは「ややこしい点」)、craze→「ブーム/熱狂的な流行」(Aの「大ブーム/大流行」より弱い・長い)、take points away from→「何かから点数を差し引く」(key_phraseに無い語の持込)、frustrate→「いら立たせる」(r2。r1ではB3の「悩ませる」が良かった=run間でぶれる)。
- B3が良くなった例: culprit→犯人(A=原因、2/2回)、investigation→捜査/調査(A=調べること)、celestial→天体の(A=宇宙の)、sponsored→スポンサー付きの(A=広告主が宣伝費を出した等)、biased→偏った(A=公平でない)、persuasion→説得(A=人を説きつけること)、supply chain→供給網(A=商品を作って届けるまでの流れ)、put the brakes on→欲しい気持ちを抑える(A)に対しB3は「ブレーキをかける」(key_phrase外の語を持ち込まない)。見出し訳をそのまま使う方向に揃う。
- **A同士でも差は大きい**(基線: 56 item中37が文言違い、良否が出るのはA1/A2それぞれ6件)。B3の悪化4件は基線のnoise(6件)以内。B3 22 vs A 11 は二項検定(両側)p≈0.08で、5%有意には届かない。結論としては『B3は全体としてAより悪化せず、見出し訳優先の方向で改善する傾向がある』に留まる(強い統計的主張はしない)。

### 3-2. 機械検査と形式
| 項目 | A | B3 |
|---|---|---|
| 検査違反(空・括弧・…・算用数字・enum外)(item) | 0/124 | 0/80(held-out 29含め0/109) |
| 複数訳語(「A、B」形式) | 0 | 0(B系 160 item中0) |
| 1語key_phraseのgloss==naive_ja率 | 8/55(15%) | 26/55(47%) |
| 1語key_phraseの平均gloss文字数 | 4.62 | 3.64 |
| 2語以上key_phraseのgloss==naive_ja率 | 0/98 | 3/98(3%)= anti-anchoringは2語以上で維持 |
- 1語の見出し訳採用率が15%→47%に上がり、定義文化(平均文字数)が減った。2語以上はほぼ従来どおり=OF-KP1-05(anchoring対策)の意図を2語以上では保っている。

## 4. 費用・速度への影響

| 項目 | A | B3 | 差 |
|---|---|---|---|
| 探索段階(matched n=11)出力token平均 | 7,167 | 7,973 | **×1.11**(Aのtoken標準偏差は約20%) |
| held-out(n=4)出力token平均 | 4,722 | 5,248 | **×1.11** |
| 入力token(+規則追加分) | 約3,300 | 約3,800 | +約480〜540 token |
| 1call費用(探索 / held-out) | ¥0.601 / ¥0.428 | ¥0.670 / ¥0.478 | **+¥0.07 / +¥0.05(約+11%)** |
- 2つの独立標本で出力token比が1.11と一致=ノイズではなく**実増加は約11%**(Prompt追加規則の確認に伴うreasoning増)。
- 量産単価への影響の見積: gloss新規生成は1記事セットで約2〜4call(Std/Adv×本体+補完)→ **+約¥0.1〜0.3/記事セット(70円目標の0.2〜0.4%)**。追加API callなし=待ち時間はほぼ不変(出力+11%分、1callあたり数秒)。
- 後段自己検査案(P、別call)は1call約¥0.12(untidiness 5 item)。効果は3回中1回(§6-2)のためB3の代替にならない。

## 5. 判定

### 5-1. 事前登録基準(探索段階)の厳格適用
| 基準 | 結果 | 値 |
|---|---|---|
| C1 対象: Aで結論系2/3以上、Bで裁判語2/3以上 | **PASS** | A=結論2/3(裁判語0/3)、B3=裁判語3/3 |
| C2 副作用: B worse≤2かつ≤better、検査違反0 | **FAIL(厳格)** | worse=4(r1)・4(r2)。better=8・11。検査違反0。基線A-Aのworse=6 |
| C3 費用: 出力token比≤1.10 | **FAIL(厳格、僅差)** | 1.11 |
| C4 2訳語≤5%、不要0〜1件 | PASS | 0件 |
→ 厳格適用ならNOT_VALIDATED(C2・C3未達)。

### 5-2. 確認Trial(held-out、閾値を実行前に再登録。PREREGISTRATION_01.md 追記1)
閾値を探索結果を見てから変えた事実を明示する。理由=C2・C3の閾値(worse≤2、token比≤1.10)がrun間ノイズ(A同士のworse=6、token標準偏差約20%)を織り込んでいなかった設計不備。
| 基準 | 結果 | 値 |
|---|---|---|
| H1 副作用: B3 worse≤3かつworse≤better | **PASS(余裕なし)** | worse=3、better=3、同等23 |
| H2 検査違反0、2訳語≤5% | PASS | 違反0、2訳語0 |
| H3 出力token比≤1.25、1call費用差≤¥0.15 | PASS | 1.11、+¥0.05 |

### 5-3. Status案
**VALIDATED(条件付き)**: C1=PASS、H1〜H3=PASS。ただし(1)C2・C3は事前登録の厳格基準では未達(閾値を再登録して確認)、(2)H1は余裕なし(3対3)、(3)評価は単独ラベラー、(4)対象itemは非盲検。**ユーザーへ示す結論は『目的(裁判語)は達成し、全体の悪化は観測されず、費用は+約11%。ただし統計的な強さは弱い』**。VALIDATEDでもProduction採用はユーザー判断(原文:56)。

## 6. 限界と、後段自己検査案(P)の結果

### 6-1. 限界
- 評価者は本agent単独(第2評価者なし)。対象verdictは非盲検。
- 標本が小さい(副作用139 item、対象記事1件)。B3の調整は対象記事で行った。held-outで追認したが、held-outはX記事のみ(Y/Z、小説は未確認)。Z(fiction)・Yでの副作用は未検証。
- 同一モデル・同一条件の再生。Productionの実環境(HR、retry、backfill、複数回gloss)での挙動は未確認。
- 3案の差の要因分離は不完全(CURRENT_STATE_01.md §3-2)。

### 6-2. 後段自己検査案P(別call、既存のA出力を入力)
対象=第1段出力のうち1語でgloss≠naive_jaのitem。候補(current・naive_ja・他の定訳)を比べ直す小call(effort=medium)。
| 入力 | verdictの最終 | 変更 |
|---|---|---|
| A r1(結論) | 結論 | なし(「『評決』より自然で文脈に合う『結論』が適切」) |
| A r2(最終的な判断) | **評決** | 変更 |
| A r3(結論) | 結論 | なし |
- 1/3のみ。第1段の判断(『平易さ優先』)を後段が追認しやすい。費用は1call約¥0.12。単独の改善案としては不十分。B3の規則変更と併用する価値は未検証。

## 7. 費用(台帳 trial_01/ledger.json、全43 call)
| 区分 | call数 | 費用(¥) |
|---|---|---|
| A(探索 11 + held-out 4) | 15 | 8.32 |
| B(v1) | 7 | 4.85 |
| B2 | 3 | 2.53 |
| B3(探索 11 + held-out 4) | 15 | 9.28 |
| 後段自己検査P | 3 | 0.36 |
| **合計** | 43 | **25.35**(Cap ¥30、残¥4.65) |
単価=gpt-6-luna 入力$0.10/キャッシュ$0.01/出力$0.50 per 1M、¥160/USD(Production記録 ¥0.6128/call と一致)。台帳のcached_input_tokensは自動キャッシュによる割引(請求にも反映される前提で計算)。

## 8. 成果物
trial_01/{PREREGISTRATION_01.md, plan_*.json, inputs/, out/(43 json), stage2/(3 json), ledger.json, blind_*.json, run_*.log}、tools/、data/。

## 9. 結果の採否: REJECTED(ユーザー決定2026-10-31)
案B3はREJECTED(不採用)。理由=副作用による既存訳の品質悪化リスク。現行の日本語訳生成Prompt・仕様は維持する。上記の数値・結論は決定前のTrial記録であり変更しない。後続=OPEN-636 JA-GLOSS-QUALITY-ALARM-TRIAL-01(独立の品質アラーム機構)。原文=docs/pm/delegation_log/2026-10-31_JA-GLOSS-QUALITY-ALARM-TRIAL-01_USER.md:7-14。
