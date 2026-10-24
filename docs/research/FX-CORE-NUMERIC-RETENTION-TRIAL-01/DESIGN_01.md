# DESIGN_01 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_01 Phase 0、2026-10-25、API 0円・Production変更0)

Status: TRIAL_APPROVED(ユーザー2026-10-25)/設計案(Opus条件Aレビュー待ち)/Production採用・配線: 未承認。根拠データ=`ROOT_CAUSE_02.md`、`er114_output/fx_numeric_trace_01/{TRACE_TABLE_01.md,trace_all_runs.json,trace_aggregate.json}`。

## 0. 推奨(1文)
**「B3のStorylineに主題への答えの数値(最大2個)を入れさせ、既存のderive_ranks(Storyline優先)でその数値だけを“必須集合E”として扱い、R0直後に決定論で保持を検査し、欠けたときだけR0を(記号QA再生成と同じ1回の枠で)再生成する」**。B3の中核数値選定・順位付けは変更せず(重複システムなし)、「全部必須」にもしない。範囲値の波ダッシュ矛盾は入力側の決定論正規化で除く。LLMの新規callは0(B3の既存1callのPrompt文言追加のみ)。

## 1. ユーザー要件の写像
| 原文 | 設計上の扱い |
|---|---|
| §2 全部入れるのは目的でない/必要十分 | 必須集合E≤2個。E以外の中核数値は従来どおり任意(検査しない)。周辺数値は従来どおり禁止 |
| §3 月: 約42〜46m必須 | E1。B3 Storylineに入る/入らない、Gateで欠ければR0再生成 |
| §3 約4億年からの推定は必要・条件を正確に | Eの2個目候補(Storylineの「前提」数値)+推定条件チェック(§5)。誤解(継続同速度)防止はFact制約ブロックと前提語チェックで担保。**必須ではなく“必要”=Phase 1の評価対象**(§6) |
| §3 約11cm/100万年・750m〜1.1kmは不要/追加しない | 周辺数値のまま。Gate対象外。不要掲載数に計上 |
| §4 重複システム禁止/B3を活かす | E=B3 Storylineの既存優先(derive_ranks `in_story`)。新しい重要度判定器は作らない |
| §4 全部必須は禁止 | 比較表のO1として却下 |
| §7 追加LLM処理は慎重/決定論優先 | 追加LLM call 0。検査は決定論(B3自身の抽出・照合関数を再利用) |

## 2. 方式比較
| 案 | 概要 | 品質(必須の保持) | 過剰掲載リスク | 追加LLM | 重複システム | 量産単価増分(期待/最悪) | 判定 |
|---|---|---|---|---|---|---|---|
| O1 | 【中核数値】全部必須 | 保持は確実 | **高**(3〜6個強制、不自然、AN3思想「必要な数字だけ」に反する) | 0 | なし | 再生成多発で高 | **禁止(ユーザー原文)・却下** |
| **O3(推奨)** | B3 Storylineに答えの数値(≤2)を入れる→E=core∩Storyline→R0の「テーマ：」行で搬送(+任意でR0規則9)→R0直後に決定論Gate | 高(実測: Storyline数値4/4残存、n小。Phase 1で再測) | 低(E≤2。非Eは増やさない) | 0(B3 Prompt文言追加のみ) | **なし**(既存StorylineとderiveRanksを使用) | +0.0〜2円/+8円(R0 1回再生成) | **採用候補** |
| O2 | Writer自己選定: 規則「中核数値のうち問いに答える1〜2個は必ず入れよ」+件数Gate(≥1) | 低〜中(Writerが8,900本超等を選べばGate通過=月で再現しうる=不合格) | 低 | 0 | なし | 同上 | 単独では却下。O3の補助(規則9)として一部採用 |
| O4 | R2後に追加LLMで必須数値を挿入 | 中(挿入が不自然化しやすい) | 中 | **+1 call**(≈4〜8円/記事、全記事に継続) | 実質あり | **+4〜8円/記事** | 却下(単価・不自然・R2の再検査が必要) |
| O5 | 決定論の語彙照合でStorylineと台帳subjectから必須数値を推定 | 低〜中(語彙一致は壊れやすい) | 中 | 0 | **あり**(新しい重要度判定器) | 0 | 却下(重複システム禁止) |
| O6 | R1/R2のPromptに保持条項を追加 | 効果は未測(R1/R2脱落0なので不要) | 中(文体影響) | 0 | なし | 0 | 却下(Production逐語USER_TMPL不変、脱落が出たら段限定再実行) |

## 3. 推奨方式O3の構成
(DEVモジュールはProductionファイルを編集せず、新規 `er115_fx_numeric_retention_trial_01.py` に置く。runは `er115_output/fx_numeric_retention_trial_01/<article>/<arm>/`。公開版・`er019_output/*`は読み取りのみ。)

### C1. B3 Storyline指示(DEV Prompt override)
`er019_family_x_storyline_b3_fact_selection_01.py` の `USER_PROMPT_TEMPLATE` に、DEVコピーで次の趣旨の1ブロックを足す(文言案。Phase 1で1回だけ調整可):
> 「Storylineの1行が答える中心的な問いに、台帳の数値(numeric_value欄にあるもの)で直接答えられる場合は、その数値を、台帳の表記のまま、Storylineの1行に含めてください(最大2個)。その数値の解釈に不可欠な前提(推定・仮定・期間・範囲)がある場合は、前提を示す言葉と、前提の数値(1個)を含めて構いません。中心的な問いが数値で答えるものでない場合や、入れると文が不自然になる場合は、数値を入れなくて構いません。数値を増やすために無関係な数値を入れないでください。」
- 4テスト・DEVELOPER_MESSAGE・JSON schema・採用Fact選定は不変。DEV用に `THEME_TAG` を別名にし、原Promptのshaと追記ブロックのshaを証跡に残す。
- なぜここか: Storyline文は既に「Writerへそのまま渡すテーマ文」(同ファイルPrompt項目2)。B3の既存機構を変えるのは文言1ブロックのみ。

### C2. 必須集合E(決定論、新しい選定器ではない)
`E = { 中核数値の概念 | その表記がStoryline文に現れる }`、上限2(超えたら出現順)。`derive_ranks(with_story=True)` が既に「Storylineに現れる概念を中核の最優先」にしているため、Eは既存`annotation.json`の中核数値とStorylineの照合で得る(`er114`の`in_story`と同じ関数)。年・序数・名称内番号は従来どおり対象外(never-core)。Storylineに数値が無ければE=∅(義務なし。観測値`story_numbers_empty_with_core_present`を証跡に出す)。
- 「約4億年」のような前提数値は、Storylineに前提として入った場合のみE2となる。E2を“必須”にするか“要注意”にとどめるかは§5。

### C3. 範囲値の表記正規化(C4原因の対処、決定論・費用0)
Writerへ渡す入力(ニュース欄・Storyline行)の範囲値で、数字と数字の間の「〜」「～」を「から」に置換する(例: 約42〜46 m→約42から46 m)。数値は不変。Gate・計測の照合は両表記を許容(`er114`の範囲規則と同じ)。置換は注記(印付け)の後、`rounding.news_field_for_writer`と同じ位置(DEVコピー)で行い、B3の注記・sha・契約検証は原本のまま。
- これは承認済み規則同士(規則5「表記のまま」×記号予防「〜禁止」×Normalizer「〜→なになに」)の矛盾の是正であり、11-8の不具合候補。ただし**Production適用は採用判断と同時**(Phase 0/Trialでは適用しない)。

### C4. R0規則9(任意の補助、アームBのみ)
`rounding.apply_rule8`と同型のDEV追記ブロック(Productionのprompt0へは入れない):
> 「9. 『テーマ：』の文に含まれる数字は、記事の中心的な問いに答える数字です。本文で必ず述べてください(表記はニュース欄のとおり。範囲は『AからB』と書き、波ダッシュは使わない)。推定や仮定が付いた数字は、『推定』『仮定』『としたら』など前提を示す言葉と同じ文で述べ、観測された事実のように書かないでください。それ以外の【中核数値】は使わなくて構いません。数字を増やすために文章を不自然にしないでください。」
- アームA(規則9なし)で足りればBは採用しない(最小変更原則)。

### C5. 決定論の保持Gate+段限定再生成
- 検査関数 `check_essential_retention(text, E, overlay)` : `er114`の`ja_present`と同一の照合(B3の`contains/extract_surfaces/main_numbers`再利用、範囲「から」許容、概数可は概数表記も許容)。
- 実行点: R0直後・R1直後・R2直後(ENはobserve-onlyで記録)。不足時の動作:
  - R0: 既存の記号QA再生成と**同じ1回の枠に合流**(記号findingsと保持findingsを1つの再生成Promptの注意書きにまとめる。R0 callは最大2回で、現行の記号QA再生成だけの場合と同数)。再生成後も不足/残存ならSTOP(`JANumericRetentionStopError`、記号QAのSTOPと同型。本文は手で直さず `ja_writer/audit/rejected_w1_r0_numeric.md` に残し既存のHR/STOP枠へ合流)。
  - R1: R0本文から1回だけR1再実行。R2: 同一R1生出力から1回だけ再実行(既存の記号QA再実行と同型)。残ればSTOP。
  - R1/R2は実測で脱落0のため期待費用0。
- 再生成Promptの追記文言: 「次の数字が本文にありません: {表記}。ニュース欄のとおりに含めて書き直してください。他の数字は増やさないでください。」(Trial専用の新規1文)。
- 安全側: **Gateは本文を自動書換えしない**(不自然な挿入を作らない)。誤判定時は本文を変えずSTOPして人が見る。

### C6. 計測器(`er114_fx_numeric_trace_01.py`)
Phase 1/2の評価はこの計測器の拡張(同一照合規則)を使う。4指標: 選定数(core)・必要数(Eまたはユーザー表)・最終掲載数(R2/ENに載ったcore)・不要掲載数(周辺+未分類)。

## 4. R0→R1→R2→Std/Advでの運用
| 段 | 変更 | 保持の担保 |
|---|---|---|
| B3 | Storyline指示1ブロック(DEV) | E生成 |
| 注記 | 変更なし(決定論producer) | in_story優先で自動中核化 |
| R0 | (A)入力の範囲値正規化 (B)+規則9 | Gate+再生成1回 |
| R1/R2 | **Prompt変更なし** | 検査のみ(脱落0の実績)。脱落時は段限定再実行 |
| 英訳Std/Adv | 変更なし | observe-only検査。欠けた場合はFableへ報告(Phase 1で観測) |

## 5. 「約4億年前からの推定」の扱い(数値保持×事実正確性)
- 事実: 台帳F06 notes=「観測された一定速度ではなく、開始時期と速度の一様性を仮定した見積もり。『現在も毎年この速さで縮んでいる』と言い換えない」(`research_ledger/verified_fact_ledger.txt`)。45m÷4億年≈11cm/百万年で、4億年は縮みの総量を割った前提期間。
- 設計: (1)前提数値が必要かはB3 Storylineが(C1の後半文言で)決める。(2)保持するときの文言規律は既存の制約ブロック(F06のnotes)がWriterに渡る。(3)決定論チェックを追加(ソフト=WARNのみ): 保持された時間単位数値(年/年前/万年/億年)が、台帳の `conditions/scope/notes` に「仮定・推定・見積」を含むFactに由来するとき、同一段落内に「仮定|推定|見積|としたら|なら|場合|可能性」のいずれかが無ければWARN。(4)最終判定はFable(本文読み)とRisk Flagger A3/A4(英語側)。**ブロッキング化はPhase 1でFP/FNを見てから**。
- 禁止表現(継続同速度の誤解)は Phase 1 の人手評価で「現在も続いている/一定速度で縮んでいる」と読める文が無いか確認する(§6の項目)。

## 6. Trial設計(Phase 1/2)・合否・撤退
### 6.1 判定基準の事前登録(結果を見る前に固定)
- 必要数の判定基準案: N1 中心的な問い(タイトル/Storyline)への答えそのもの / N2 欠くと主張が曖昧・誤解を招く(「ごくわずか」だけで規模が無い等) / N3 保持する数値の解釈に不可欠な前提・期間。どれにも当たらなければ「任意」(掲載可・必須でない)または「不要」。月はユーザー表(§3)で確定、過去記事は**B3 Storyline再生成の前に**Fableがledger・タイトルから`labels.json`を固定。
### 6.2 Phase 1(月)
- 手順: (1)B3 DEV 1call(ledger再利用、Web検索なし)→Storylineに42〜46m(±4億年)が入るか確認(入らなければ文言を1回だけ調整) (2)決定論注記→丸め判断(Luna low、約0.17円) (3)アームA(C1+C3+C5)、アームB(A+C4)をW-1フルチェーン→Std/Adv (4)R0のみの追加標本(各アーム+2)で保持率を推定 (5)人手評価(Fable)。
- 評価項目(原文§5): ①必須縮小量(約42〜46m)がR2・Std・Advに残る ②期間情報(約4億年+仮定)が正確 ③不要数値(約11cm、750m、1.1km)が入っていない ④文章が不自然でない(数字密度、読み上げ可能性) ⑤事実関係・単位・推定条件が台帳どおり ⑥既存丸め仕様と整合(EXACT_REQUIRED=表記どおり、概数可があれば【概数表記】のみ)。
- 合格: 必須(42〜46m)がR2・Std・Adv全てに残る(R0単独の保持率3/3以上)、不要数値の混入0、④⑤⑥NGなし、4億年は“前提語つき”で出るか“出ない場合は理由が妥当(Fable判定)”。最小変更アーム(A優先)を採用候補とする。
### 6.3 Phase 2(横展開)
- 対象(ledger再利用・Web検索なし): ig_nobel_2026/run_nws_02(中核0/3→R2で1)・coffee_prices/run_fxpw_01(1/5)・semiconductor_earnings/run_devconfirm_01(数値多数・Storyline数値5=過剰掲載リスクのstress)。予算次第で paycheck run_pp_02。
- 評価: 記事別の選定数・必要数・最終掲載数・不要掲載数(`er114`拡張)、Storyline数値の件数(上限2が効いているか)、過剰掲載(R2数値表記ユニーク数が基準run比+1以内、周辺数値0)、文章品質(Fable)。公開版は不変。
- 合格: 全記事で ①E⊆最終掲載 ②基準runに比べR2の数値表記が増えすぎない ③周辺数値混入0 ④文章不自然化なし ⑤追加の保持再生成率が許容内(R0再生成≤1/3記事で費用上限内)。
### 6.4 撤退条件(REJECTED/再設計)
- B3 Storyline指示でStorylineに数値が入らない/入っても不正確(前提を誤結合)が文言1回調整後も続く → O3不成立。台帳subject照合で必須を推定する案(O5)は重複システムに近いので採らず、**方針再提案(USER_DECISION_REQUIRED候補)**。
- Gateが誤判定(FP>1/10)/自然さ悪化/過剰掲載(周辺混入>0または基準比+2超) → 当該アーム REJECTED。
- 同じ方式の無意味な繰り返しはしない: 原因が文言なら文言1回、構造なら設計見直し(Opus再レビュー条件B)。

## 7. Production不変の保証(Trial中)
- Productionファイル(er053/er019/er095/er003系)・Prompt・閾値・flagの編集0。新規 `er115_*` のみ。Production関数はimportして**呼ぶだけ**で、Promptはsha固定の定数を文字列合成で拡張(原定数の書換えなし)。
- DefaultOffIsolation相当test: (a)フックOFF時にDEV版`build_r0_prompt`がProduction版と**バイト一致**(`er053.build_r0_prompt`) (b)Production module側にDEVのimport・参照が無いGrep (c)DEV runnerを起動しない限りProduction runnerは従来の入力・出力(env・起動scriptでONにしない)。
- 公開版・`er019_output/*/run_*`は読み取りのみ。DEVは `er115_output/` のみに書く。

## 8. QCD
- **量産単価(継続増分、出典=`er019_output/moon_shrinking/run_ms_02/cost.json`、`run_ms_01/cost.json`)**: 追加LLM call 0。(a)B3 Prompt約250字≈+0.0〜0.02円(B3全体12.07円=run_ms_01 storyline_b3)、(b)アームBの規則9≈+150入力token×1call≈+0.01円、(c)再生成: R0 1回=7.61円(run_ms_02 w1_r0)、記号QA再生成は6.23円(run_ms_01 w1_r0_symbol_regen)の実績。**期待増分=P(R0にEが無い)×約7円**。P=0.2なら+1.4円/記事(単価目標70円の約2%)、P=0.5なら+3.5円。R1/R2脱落は実測0。最悪(R0+R1+R2全て再実行)=7.6+3.9+4.2=15.8円(発生は想定せず、記事ごとに上限を持つ)。→ Phase 1で実測P_R0を出し、確定値は報告で更新。
- **生成時間**: 通常は+0秒(決定論Gateはミリ秒)。再生成時R0 72〜80秒追加(`raw_usage_log.jsonl` w1_r0 elapsed)。
- **開発費(Trial実費、見積)**: Phase 0=0円(実績)。Phase 1≈79円(B3 12.1+丸め0.2+フルチェーン2アーム36.0+R0追加標本4×7.6=30.4)。B3文言再調整が必要なら+12.1(最大約91円)。Phase 2≈113円(3記事×(B3 12.1+フルチェーン18.0)+追加R0標本7.6×3)。合計≤200円(Fable案件上限)。単一案件300円以下=自律枠。
- **品質**: 必須の保持、過剰掲載抑制、既存丸め仕様と整合。**残存リスク**: B3 LLMが前提を誤結合/Storylineを不自然に長くする、Gate誤判定、Writer variance(標本n小)、英訳での表記変化。

## 9. 使用モデル(最新原則 PM_GOVERNANCE 25節)
- Writer R0/R1/R2/B3: Production同一(`routing.PROCESS_MODEL_MAP`: FAMILY_X_FACTLOCK_R0/REVISE=gpt-6.1-sol、B3選定=gpt-6.1-sol[`run_ms_02/storyline_b3/runtime_evidence.json` model_id_actual]、丸め判断=gpt-6-luna low)=条件同一性。最新世代かの確認はPhase 1 evidenceに記録。
- 評価: 人手(Fable)中心でLLM評価call 0。LLM評価を使う必要が出たら最新世代(gpt-6.1-sol等)を使用し、名称と最新か否かを記載。

## 10. Production採用時の必要作業・影響範囲(参考。未承認)
- 変更候補ファイル: B3選定Prompt(`er019_family_x_storyline_b3_fact_selection_01.py`)、`er053_family_x_factlock_ja_writer_01.py`(Gate/再生成/規則9/範囲正規化)、`er095`同型の入力変換、runner、`CURRENT_SPEC.md`、test。Family Xのみ(Z/Yは到達しない=Isolation test)。
- 影響: X全記事のB3 Storylineが数値を含みうる(B3 Promptの意味的変更=ユーザー承認事項)、R0 callが再生成で増える可能性、既存公開記事は不変。

## 11. 判断候補(Opus条件Aレビュー後にFableが分類)
- J1 B3 Prompt(Storylineに数値を含める)のProduction適用: C(新規・採用判断時にユーザー承認)。Trial実施自体は承認済み。
- J2 範囲値表記の正規化: 11-8不具合候補(承認済み規則同士の矛盾)。Production適用タイミングは採用判断と同時を推奨。
- J3 保持Gate不足時のSTOP(vs 警告のみ)の既定: Trialでは記号QA同型のSTOP。Production既定は採用判断で。
