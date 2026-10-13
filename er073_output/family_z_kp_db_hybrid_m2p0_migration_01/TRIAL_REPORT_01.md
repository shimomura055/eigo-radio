# TRIAL_REPORT_01 (FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01)

性質: Trial。Production無変更・Production採用判断なし・Family Z記事再生成/音声化なし。**Status: USER_DECISION_REQUIRED**(品質劣化が3原稿で再現。案1のままのDB Hybrid+M2P0移行は推奨しない[REJECTED寄り])。
使用モデル: 選定/canonicalization/Redundancy QA すべて `gpt-6-luna`(model_id実測 run_summary.json.model_ids。Production同一[比較可能性の例外]、最新モデル原則の例外理由=Strategy Lとの比較条件を揃えるため)。
証跡: `runs/<text_id>/<arm>_run<N>/`(run_summary.json、key_phrases/*.json、cost_log.jsonl[add対象外])、`runs/aggregate.json`、`phase1/`、`state_before.json`/`state_after.json`。

## 0. 実施範囲・未達
- 計画: Melos Std/Adv/Lemon L11 × DB Hybrid+M2P0 × n=3 + Lemon Strategy L 1回(対照)。実施: DB Hybrid 7 run(Std **1**/Adv 3/Lemon 3) + Strategy L 1。
- **Melos Std は n=1 で終了**: run2開始前のbudget/STOP guardが `er026_output/family_z_production_e2e_01/STOP_ALL` を検出し当該processが自主停止した(新規API呼出なし、`melos_std/dbh_m2p0_run2/`はcost_logのみ)。確認時点(20:32)ではSTOP_ALLは既に存在しなかった(私は作成・削除していない)。委任文は再起動を許可していないため**再起動していない**。Std run2/3(約JPY1.9、約6分)の追加実施は要判断(Fable)。
- Strategy L対照: Melos Std/Advは既存 run_e2e_02 出力(再生成なし)、Lemonは1回実行。

## 1. 選定品質(目視ラベル。※Sonnet暫定ラベル、Fable/ユーザー確認要。基準: 慣用句・比喩・句動詞・学習価値)
ラベル: 正 / 粒度不良 / 誤 / 低価値(透明で学習価値が低い)

| 原稿 | Strategy L最終KP(対照) | DB Hybrid+M2P0最終KP | 評価 |
|---|---|---|---|
| Melos Std | pull someone under[正] / in someone's place[正] / lose trust in someone[正] / hold out[正] / far bank[正] | (run1のみ) order someone's death[粒度不良: 予約枠断片`ordered his death`、『sentence someone to death』ではない] / hold out[正] / for once[正] / walking stick[低価値] / come back[低価値] | 正 5/5 -> 2/5。比喩・句動詞(pull under, in your place, far bank)を全て失う |
| Melos Adv | sentence someone to death[正] / current[正] / hold out[正] / seize[正] / abandon[低〜正] | run1: hold out / ring through / rise above / to death / walking stick; run2: hold out / walking stick / rise above / ring through / come back; run3: hold out / ask for / rise above / walking stick / ring through | `hold out`は全run共通[正]、`rise above`[正]・`ring through`[正]は対照にない良質な追加。一方`to death`[断片: 粒度不良]、`walking stick`/`come back`/`ask for`[低価値]。`sentence someone to death`/`seize`/`current`を失う。混在(良2・低価値/断片2-3) |
| Lemon L11 | close around me[正] / catch one's breath[正] / tiny bomb[正: 比喩] / grow lighter[正] / short of money[正] | run1: catch one's breath[正] / bookshop[低価値] / fruit shop[低価値] / shopkeeper[低価値] / lean[低価値]; run3: catch one's breath[正] / bookshop / rise up[低価値] / fruit shop / walk out[低価値]; run2: DB Hybrid selection INVALID -> Strategy L fallback(tiny bomb等、DB Hybrid成功ではない) | 正 5/5 -> 1/5(DB成功2run)。比喩`tiny bomb`/`grow lighter`/`short of money`を失う |

- **直接原因はshortlist(抽出段)**: Strategy L対照の最終KP 15件(各原稿5件)のうち、DB Hybrid shortlist(25/25/24件、phase1/)に存在したのは各原稿1件のみ(Std `held out`、Adv `held out`、Lemon `catch my breath`[M2予約枠])。`pulled him under` `far bank` `in your place` `sentenced him to death` `tiny bomb` `grown lighter` `short of money` 等はshortlistに無く、選定LLMは選べない(構造的な取りこぼし)。shortlistはdictionary/Idiom DB/Wiktionary辞書ヒット由来で、物語の比喩・台詞由来表現や活用語は拾えない。
- M2予約枠(a)(b2)は、Fictionでは`ordered his death` `blocked his way` `remember its exact` `stained his feet` `see her wedding` `out his hands`のような断片を供給する(`catch my breath`のみ良質)。Melos Stdでは予約枠由来の断片が最終KPに入った(run1: order someone's death)。News向けに設計・検証された(a)(b2)ルールはFictionで低価値断片を混入させるリスクがある。
- Fiction固有: 台詞の口語表現(`come back` `for once`)は拾えるが、固有名詞は候補化されない(Melosを含む候補なし)。一人称原稿(Lemon)の所有格(`my breath`)は`catch one's breath`へ正規化されRule7に当たらなかった。

## 2. 既存Validator整合
- stage PASS 8/8(DB Hybrid 7 + Strategy L 1)。ただしDB Hybridの1/7(Lemon run2)は選定gate INVALID(`normalization_note`が空、`KEY_WORDS_STRUCTURE_INVALID`)でStrategy L fallback -> fallback発火率 1/7=14%(DB Hybrid成功としては6/7)。
- canonicalization INVALID: DB Hybrid 0件(Z外側retry 全run outer_attempts=1)。Rule7違反: 0件。対照(Melos Std Strategy L)は3 attempt中2回INVALID(OPEN-310型)。**DB Hybrid経路ではRule7 INVALIDが再現せず、OPEN-310を実質回避**(n=7で0件。母数小のため保証ではない)。
- Redundancy QA: 全run PASS。symbol gate: flagなし。Validatorの緩和・変更なし(同一module)。

## 3. コスト・処理時間
| 指標 | Strategy L(対照) | DB Hybrid+M2P0 |
|---|---|---|
| 1 run費用 | Lemon JPY0.77(1 attempt)。Melos kp段 Std+Adv=JPY5.31(Std 3 attempt[Rule7 INVALID 2回]+Adv 1)、explanation JPY0.03別 | JPY0.83-1.05(成功6 run平均0.94)。fallback発火run JPY1.46 |
| 処理時間/run | Lemon 82秒 | 165-199秒(M2供給[Wiktionary]65-68秒、LLM合計96-130秒) |
- 1 attempt同士の単価はDB Hybridがやや高い(約+JPY0.1-0.3、+85-115秒)。Rule7 INVALIDによる再試行が減る分、Stdでは総額が低くなる可能性があるが、Trial母数では確定できない。
- Phase 2実費 合計 **JPY7.90**(8 run、上限JPY50、soft JPY35に対し十分内)。計画見積約JPY16に対し、全run 1 attempt通過のため低かった。委任文の「Wiktionary約43秒/記事」は不正確(phase1単独185秒、並列時65-68秒)。

## 4. 品質劣化の有無
**あり**。Strategy Lで選ばれていた良質KP(比喩・句動詞・慣用的な名詞句: pull someone under / in someone's place / lose trust in someone / far bank / sentence someone to death / tiny bomb / grow lighter / short of money 等)がshortlist段で失われる。得られる良質KPは`hold out` `rise above` `ring through` `for once` `catch one's breath`などに限られ、低価値(`walking stick` `come back` `bookshop` `fruit shop` `shopkeeper`)が混入する。

## 5. 安定性(n=3のJaccard、final KP、小文字化)
- Melos Adv: 全ペア0.667(平均0.667、核`hold out` `rise above` `ring through` `walking stick`は安定)。
- Lemon: 平均0.143(ペア 0.0/0.429/0.0。fallback runを含む。DB Hybrid成功2 run同士のみでは0.429)。
- Melos Std: n=1のため算出不可(STOP_ALL)。

## 6. Status判定と根拠
**USER_DECISION_REQUIRED**。VALIDATEDとしない理由=品質劣化が3原稿で再現(第4節)。REJECTEDと断定しない理由=(a)Std n=1、(b)Rule7 INVALID回避という利点、(c)移行方式の最終判断はユーザー専権、(d)劣化の主因が「候補供給(shortlist)」でありFiction向け候補供給の設計(案2a、本委任範囲外=N01/M2P0以外の方式探索に該当)で改善余地がある可能性。Production採用は推奨しない(案1そのままでは品質劣化)。

## 7. Production実装に必要な変更一覧(**未実装・未承認**)
MIGRATION_DESIGN_01.md 第3節のとおり: (1)Z配線(`select_fn`差し替え、1-2箇所)、(2)(任意)`SUPPORTED_FAMILY_PROFILES`へfamily_z、(3)telemetry識別、(4)OPEN-310暫定外側retryの扱い。guidance差分は不要(新規Prompt作成なし)。

## 8. ユーザー判断事項(推奨付き。採用判断はしない)
1. Z KPの移行方式: **推奨=現時点ではStrategy L継続**(案1のDB Hybrid+M2P0はFictionで品質劣化。OPEN-344/UDR Z-1は「M2P0をZにも適用する正式決定」と衝突するため、その決定の解釈=「ZはM2P0適用不可(候補供給がFiction不適)」の整理が必要)。
2. Fiction向け候補供給の再設計Trial(案2a: 例えばLLM自由選定+DB補助、またはFiction向けshortlist拡張)を別Trialとして起こすか(N01/M2P0以外の方式探索のため新規承認が必要)。
3. Melos Std n=3化(追加約JPY1.9)を実施するか(結論は変わらない見込み、省略推奨)。
4. OPEN-310(Rule7)の扱い: DB Hybrid経路では再現せず。Strategy L継続の場合は暫定外側retryを維持。
5. 今回のSTOP_ALL出現(誰が/何の目的かは本task外)の確認。
