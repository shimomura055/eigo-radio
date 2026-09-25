# TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01 REPORT

Status: **STOP**(estimate段階、API課金0円。Luna/Sol/Terraいずれも未実行)

## §1 Trial条件・対象24時間
- 目的: 「検索→Candidate Pool→別callでrerank」ではなく、Search+Angle
  Discovery+追加検索+Topic Package化+Selectionを1つのResponses API
  call(web_searchツール付き、内部の複数tool callは許容)で行う新設計を
  Luna/Terra/Solで比較する。
- 対象24時間: 2026-09-18 00:00〜23:59 JST(第一候補どおり)。
- 同一条件: 同一Prompt(sha256記録)・同一json_schema(strict)・同一effort
  (medium)・同一search_context_size("low")・同一Teacher Data(57件+
  Positive/Negative例)・同一最終出力件数(10件)を設計。
- 3モデルとも**未実行**(下記§9のとおりestimate段階でSTOP)。

## §2 共通Prompt全文・schema
- `er016_topic_discovery_angle_integrated_3way_trial_01.py`の
  `DEVELOPER_MESSAGE`/`USER_MESSAGE_TEMPLATE`/`build_schema()`に実装
  (委任文の共通Promptブロックと逐語一致)。
- 実際に teacher データを差し込んだ最終Promptの sha256:
  `91b8206d80c7fdb1...`(全文は`cost_estimate.json.prompt_sha256`、
  developer+user合計6,997文字)。
- schema: OpenAI strict schemaの既存実績(`er016_topic_selection_chatgpt_
  repro_01._step_a_schema`等)に倣い、`minItems`/`maxItems`は使用せず
  件数固定はPrompt文言("exactly 10 topic packages"/"at least 5 dropped
  candidates")のみで行う設計(委任文の緩和条件に該当、schema自体を
  実際に投げていないため厳格化での失敗有無は未検証)。

## §3〜§8 各モデル実行結果・検索件数・最終10件・ブラインド一覧・
News/Social比率・window compliance
**未実施。** Luna/Sol/Terraいずれも1 callも実行していないため、
response.model実値・検索件数・Topic Package・ブラインド一覧・
News/Social比率・window complianceのいずれも生成されていない。

## §9 予算概算(estimateステップ実行結果)
`--step estimate --budget-jpy 200`を実行し、`cost_estimate.json`を生成
(`er016_output/topic_discovery_angle_integrated_3way_trial_01/
cost_estimate.json`)。

**算出方法**:
- Luna: `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`の実測データ
  (`cost.json`、web_search_call_countが1以上の20エントリ)から最小二乗法
  で線形回帰(`jpy = 0.2145 + 1.9678 * internal_search_count`、Sonnetが
  本タスク中に算出、算出コマンドは`docs/pm/delegation_log/TOPIC-
  DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md`に記録)し、internal
  search 20/25/30件で外挿。加えて、本Trialの実際のPrompt文字数
  (6,997文字)と基準プロンプト(同Trialのcompare_classify call、7,498
  文字/4,375 input tokens、較正比1.71文字/token)の差分から入力コスト
  補正を加算(今回は本Prompt側が基準より短いため補正はほぼ0)。
- Sol/Terra: `pricing_snapshot.json`の直接価格比はinput/output共に
  Sol/Luna=25.0x。ただし**実測2件**(`NEWS-HOOK-MODEL-COMPARISON-01`:
  Sol¥20.41/Luna¥0.74=27.58x、`TOPIC-SELECTION-USER-PREFERENCE-RERANK-
  TRIAL-01`:Sol¥25.2032/Luna(同一プロンプト相当)¥0.908=27.75x)の平均
  27.665xを採用した(**委任文記載の「Luna比≈6.6倍」は上記実測2件と一致
  しないため不採用**、この不一致自体をcost_estimate.jsonの
  `price_ratio_note`と本REPORTに明記する)。Terra単価は
  `pricing_snapshot.json`未収載(UNKNOWN)のため、委任文指定どおり
  Solと同額と仮置きして安全側に判定した。

**結果**(3シナリオ、`internal search count`=20/25/30):

| シナリオ | Luna(円) | Sol(円) | Terra(仮置き、円) | 3-way合計(円) | budget¥200以内 |
|---|---|---|---|---|---|
| low(n=20) | 39.57 | 1,094.70 | 1,094.70 | **2,228.97** | No |
| mid(n=25) | 49.41 | 1,366.93 | 1,366.93 | **2,783.27** | No |
| high(n=30) | 59.25 | 1,639.15 | 1,639.15 | **3,337.55** | No |

3シナリオすべてで予算¥200を大幅に超過(最小でも約11倍)。主因はSol/Terra
の価格がLunaの約25〜28倍であり、委任文が想定する内部search回数
(20〜30回)をこなす1 callの規模では、Sol/Terra単体だけで¥1,000超級に
なる見込みであるため。

**STOP判定**: 委任文STOP条件「¥200超過見込み」に該当。Luna実行前に
STOPし、`stop_condition.json`を保存した。API課金は0円。

## §10 モデル間重複
未実施(§3〜§8同様、実行データなし)。

## §11 評価方法(ユーザー評価後)
`er016_topic_discovery_eval_01.py`を作成し、`--dry-run`で動作確認した
(ダミーblind_map・ダミーuser_evalを自動生成、
`er016_output/topic_discovery_angle_integrated_3way_trial_01/
eval_result_DUMMY.json`)。集計ロジック(モデル別○率/○+△率/×率/統合
グループ件数/独自候補Hit率)はダミーデータで動作したが、**実データでは
未検証**(Luna/Sol/Terraが未実行のため)。

## §12 Fable参考評価
`[Fable記入]`

## §13 分類
`[Fable記入]`

## §14 USER_DECISION_REQUIRED
`[Fable記入]`

**Sonnetからの事実提示**(判断材料):
1. 本Trialの設計(1 call内でモデル自身に20〜30回程度のweb_search実行を
   促すTeacher 57件+詳細schemaのPrompt)は、Sol/Terraでは1 callあたり
   ¥1,000〜1,600円台になる見込みで、Luna単体の約25〜28倍という価格差が
   そのまま跳ね返る。¥200という暴走防止上限とは1桁以上の乖離がある。
2. 選択肢としては(a)予算上限の引き上げ、(b)Sol/Terraを除きLunaのみで
   先行実施、(c)internal search回数を制限するPrompt変更(ただし
   モデル自身の探索量比較という設計思想と衝突する可能性)、(d)Teacher
   57件のPrompt組み込みを圧縮する、等が考えられるが、いずれも委任文の
   想定範囲外の設計変更にあたるため、Sonnet単独では選択せず報告する。

## §15 新Open Item候補(事実列挙)
1. 「検索+Angle Discovery+Selectionを1 callで行う」設計は、web_search
   ツールを内部で多数回呼び出すことが前提となるため、Sol/Terraのような
   高単価モデルでは1 callのコストがLunaの実測25〜28倍になる(実測2件:
   27.58x、27.75x)。今後この種の「1 call・多数回web_search」設計を
   高単価モデルで検証する場合、予算設計は「1 search callあたりの単価」
   ではなく「1 call全体の予想コスト×モデル価格比」で先に見積もる必要が
   ある(旧Rerank設計の知見「表面的Candidateの後段Rerank単独では品質
   不足」とは別の、コスト設計上の新たな知見)。
2. 委任文記載の「RERANKのSol実績(Luna比≈6.6倍)」は、Sonnetが実際の
   `cost_estimate.json`(`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-
   01`)を確認した限り根拠が確認できず(実測は27.75x)、`NEWS-HOOK-
   MODEL-COMPARISON-01`の実測も27.58xで一致。今後同様の概算を行う際は
   実測値を都度再確認する必要がある。

## §16 Dangling Reference Check
`Grep "TOPIC-DISCOVERY" --include=er003_*.py --include=er012_*.py` = 0件
(実行結果、Production code側に本Trial由来の参照なし)。

## §17 Production変更なしの確認
- `er003_*.py`/`er012_*.py`等のProduction正式pathは一切変更していない。
- `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`は未編集。
- 旧`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`の成果物は削除・
  変更していない。
- API課金は0円(estimate段階でSTOPしたため)。
