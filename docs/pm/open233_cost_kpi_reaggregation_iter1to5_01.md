# OPEN-233 コストKPI 5分割再集計(iteration 1〜5、既存usageデータからの再計算)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_15、2026-09-30、read-only調査)
入力: `er052_output/open233_self_recovery_flow_runner_01{,_iter2,_iter3,_iter4,_iter5}/summary_flow_runner.json`
(instance別`total_cost_jpy`/`stage1_call_used`/`final_state`)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`
(既存の`今回¥X・Phase累計¥Y`記述)、`docs/pm/design_open233_self_recovery_flow_01.md`§13(単価根拠)。
**API呼び出しなし、費用¥0、新規実行なし(既存artifactの再計算のみ)。**

---

## 0. 前提・定義

- **記事の定義**: Standard(A2)+Advanced(B1B)の2 instanceを1記事として合算(`hormuz_run03`・
  `meta_run03`の2ペアのみ対応が取れる)。対応が取れないfixture(`hormuz_run01_advanced`・
  `hormuz_run02_advanced`・negative群7件)はinstance単位のまま「記事相当単位」として扱う
  (instance＝該当levelのみの単一記事)。**合成Safety群(`safety_er009_*`9件+`safety_A2A3`/
  `A4`/`A5`3件、計12件)とB群(`bgroup_B1〜B4`4件、claim単位検証用改竄fixture)は「記事」
  集計から分離**(いずれも意図的に事実を改竄/構成した診断用fixtureであり、実記事のコスト
  分布を代表しない)。
- **「記事」母集団(n=11)** = real_run 4件(`hormuz_run01`/`hormuz_run02`/`hormuz_run03`
  [ペア]/`meta_run03`[ペア]) + negative 7件(実記事のfalse-positive検証用、単一level)。
  「real_runのみ」(n=4、ペア2+単一2)も参考として併記する。
- **追加コスト(baseline控除後)の定義**: instance単位で`stage1_call_used=true`(Stage1を
  このTrialで新規call、既存Production相当の1 call/記事/levelを含む)の場合のみ、
  Stage1 1 call分の単価を控除する。`stage1_call_used=false`(既存Stage1 artifactを再利用、
  このTrialでの追加支出¥0)の場合は控除しない(controlしても相殺されるため。理由は§1末尾
  「reuse/fresh換算の扱い」参照)。
  - **LOW(gpt-6-luna、Trialモデル)**: 実測平均¥0.2043/call(design書§13-1、固定fixture
    84 call実測)。2 call/記事(Advanced+Standard)ベースライン ≈ **¥0.41/記事**
    (委任文表記「gpt-6-lunaで¥0.5〜0.6」の元になった概算値をより精密な実測値で採用)。
  - **HIGH(gpt-5.6-luna、現行Production実モデル)**: 実測平均¥0.4911/call。2 call/記事
    ベースライン ≈ **¥0.98/記事**(design書§13-2の既存確定値と一致)。
- 既存REPORT.md§14-6の「記事単位コスト」(baseline控除なし、Safety/B群も同一枠で平均)とは
  **定義が異なる**ため数値は一致しない。両者の関係は§1末尾に注記。

---

## 1. 5分割コスト表(iteration別、「記事」母集団n=11、baseline控除後)

| iteration | Rewriteなし平均/記事 | Rewriteあり平均/記事 | Rewrite率 | 全記事平均/記事 | worst(記事単位) |
|---|---|---|---|---|---|
| iter1(委任_09、baseline flow) | LOW ¥0.42 / HIGH ¥0.32 | LOW ¥0.41 / HIGH ¥0.41 | 2/11=18.2% | **LOW ¥0.42 / HIGH ¥0.34** | ¥0.94(meta_run03、LOW) |
| iter3(委任_11、S1-U導入+Opus是正) | LOW ¥0.53 / HIGH ¥0.38 | LOW ¥1.86 / HIGH ¥1.82 | 7/11=63.6% | **LOW ¥1.37 / HIGH ¥1.30** | ¥3.08(hormuz_run03) |
| iter4(委任_12、R3/R3'較正+S1-U有効) | LOW ¥0.70 / HIGH ¥0.70 | LOW ¥1.36 / HIGH ¥1.22 | 6/11=54.5% | **LOW ¥1.06 / HIGH ¥0.99** | ¥2.72(meta_run03、LOW) |
| iter5(委任_13、R3'''+2-of-2+品質v2、n=2結合平均) | LOW ¥0.67 / HIGH ¥0.67 | LOW ¥1.32 / HIGH ¥1.27 | 9/11=81.8% | **LOW ¥1.20 / HIGH ¥1.16** | ¥2.66(meta_run03、LOW、sample内最大) |

**判定**: 4 iteration全てで**全記事平均 ≤ +¥2/記事のKPIを達成**(iter1 ¥0.34〜0.42、
iter3 ¥1.30〜1.37、iter4 ¥0.99〜1.06、iter5 ¥1.16〜1.20)。ただしiter1→iter3で
Safety強化機構(S1-U・2-of-2・cite-or-release等)追加に伴いRewrite率・平均コストが
明確に上昇するトレンドがあり、iter5時点でも+¥2の58〜60%水準まで来ている(余裕は
残るが縮小傾向)。**worst(記事単位)はiter3で一度旧+¥3 Capを超過**(¥3.08、
`hormuz_run03`、HF-009 changed_scope型)、iter4/iter5は¥2.7台で+¥3 Cap内に戻った。
worstは委任文の方針どおり監視指標であり主KPI判定には使わない。

### 1-1. real_runのみ(n=4、negativeを除いた狭義「記事」、参考)

| iteration | Rewriteなし平均 | Rewriteあり平均 | Rewrite率 | 全体平均 | worst |
|---|---|---|---|---|---|
| iter1 | LOW ¥0.52 | ―(0件) | 0/4=0% | **¥0.52** | ¥0.94 |
| iter3 | LOW ¥0.32 | LOW ¥2.98 | 2/4=50% | **¥1.65** | ¥3.08 |
| iter4 | ―(0件) | LOW ¥1.48 | 4/4=100% | **¥1.48** | ¥2.72 |
| iter5(sample1/sample2) | ―/― | LOW ¥1.97/¥1.57 | 3/4=75%・4/4=100% | **¥1.62/¥1.57** | ¥2.66/¥2.19 |

real_runのみに絞るとiter4以降Rewrite率100%近くまで上昇しており(4記事中3〜4記事が
Rewrite発火)、全体平均もnegative込みより高め(¥1.5〜1.65)。nが4と小さく統計的信頼度は
低い(区間推定はREPORT.md§14-2のWilson CI参照)。

### 1-2. 参考: 合成群(Safety・B群、「記事」ではない、監視専用)

| iteration | Safety群 全体平均/worst | B群 全体平均/worst |
|---|---|---|
| iter1 | ¥0.60 / ¥2.27(safety_A4) | ¥1.10 / ¥1.94(bgroup_B4) |
| iter3 | ¥1.19 / ¥6.24(safety_A4) | ¥1.75 / ¥2.54(bgroup_B1) |
| iter4 | ¥0.91 / ¥4.30(safety_A4) | ¥1.34 / ¥2.87(bgroup_B4) |
| iter5(n=2結合) | ¥0.96 / ¥5.36(safety_A4) | ¥1.38 / ¥4.04(bgroup_B4) |

既存REPORT.md§14-6の「記事単位worst cost ¥5.3592(safety_A4)」「¥4.0387(bgroup_B4)」は
この合成群由来であり、**実記事のコスト分布を表すものではない**(改竄fixtureが意図的に
複雑なclaim構造を持つため、cycle上限近くまでRewriteが繰り返される)。

### 1-3. 不要Rewrite(誤った過剰Rewrite)が押し上げている分

- iter4→iter5で「正常記事の不要Rewrite率」(design書測定項目、negative候補7件+Normal2件
  [`hormuz_run03_advanced`/`meta_run03_advanced`]の計9件が母集団)が**44.4%(4/9)→
  77.78%/66.67%(sample1/sample2)へ悪化**(REPORT.md§14-2)。これは§1表の「Rewriteあり
  平均」を構成するinstance数がiter5で増えたことに直結しており、iter5の「Rewriteあり
  平均¥1.27〜1.32」のうち相当割合が**発火しなくてよかったはずのRewrite**である。
- 具体的にはREPORT.md§14-3が原因を2系統に分類済み: (a) floor起因(3件、item7として
  ユーザー判断待ちで未修正のまま凍結)、(b) Stage2(R3''')自体の較正セット外claimへの
  汎化未確認(4件、新規知見、独断修正はしていない)。
- **iteration5全体はStatus=`ITER5_DONE_IMPROVEMENT_NEEDED`のまま**であり(全記事平均
  KPI自体はギリギリ達成しているが)、不要Rewrite率とreal_run Escalation率とworstが
  いずれもiter4比で悪化している。この是正は別worker(委任_14/iteration6、本委任と
  同時並行、docs/pm/design_open233_self_recovery_flow_01.md・REPORT.md・er052_output/
  …_iter6/を編集中)が対応中であり、**本委任ではiter6の内容には一切触れていない**。

---

## 2. ¥223(正確には¥222.9756)のEvidence整理

REPORT.mdの`今回¥X・Phase累計¥Y`記述(§5〜§14、各行末尾)から復元した委任単位の
内訳(本Phaseのみ、前Phase¥45.68とは別枠)。

| 委任 | 内容 | 費用 | 得られたEvidence(再利用価値) | 無駄/再実行要否 |
|---|---|---|---|---|
| _01〜_04(設計+Opus L2#1) | Self-Recovery Flow設計・Opus初回レビュー | ¥0 | 設計書全体(§1〜§13)、Second Judge/Rewrite設計 | 設計SSOTとして継続再利用、再実行不要 |
| _05/_06 | hormuz Stage2独立診断3call+precheck測定 | ¥0.6285 | **Stage1 recall欠落をStage2独立診断が3/3で埋められる実証**(HF-009)、precheck FP率・Safety検出率(¥0、fixture再計算) | 再実行不要。ただしfixture母集団拡張時は再測定余地あり |
| _07 | Stage1 V0/V4-A/S1-D比較(76call)+Stage2 unitcost/batch/caching(12call) | ¥14.6598 | **V4-A最終確定**(S1-D不採用の根拠データ)、changed_actor n=15有意差(p=0.00220)、Stage2実単価¥0.087〜0.112/call、batch化(call-55%/cost-29%)・caching(63〜64%削減)実測 | V4-A確定・Stage2 unit price確定済みにつき**再測定不要**。S1-D実装自体は不採用だが「なぜ不採用か」の比較データとして保持価値あり(無駄ではなく必要な否定結果) |
| _08 | Stage2 rubric R1/R2/R3較正(作業A)+Stage3 delete/replace型Rewrite成功率(作業B、E-1/E-2・J-1/J-2) | ¥6.208 | R1(緩すぎ)/R2(過剰補正)の比較データがR3系列較正の出発点、Stage3局所Rewrite実単価 | R1/R2自体はR3'''に置き換わったが**過程データとして保持**(較正の理由付けに必要)。単体では再実行不要 |
| _09(iteration1) | 29 instance flow_runner初回実行(baseline flow) | ¥16.7806 | Self-Recovery Flow初回全体動作確認、Initial BLOCK 23件→Rewrite進捗22件 | baseline比較点として保持、再実行不要 |
| _10(iteration2) | R2'較正(¥3.3977)+rewrite_hint実装検証(Safety群12 instanceのみ、¥26.0302) | ¥29.4279 | rewrite_hint機構がSafety群での重大recall miss3件を解消した実証 | **Safety群12件の個別コスト数値はiter3の全29 instance再測定で上書き済み**(rewrite_hint込みでの再測定)。rewrite_hintという機構の有効性自体は確定済みで再実行不要だが、iter2固有のコスト内訳は以後参照されていない(部分run、real_run/negative群は未測定のまま) |
| _11(iteration3) | S1-U比較(¥5.136)+29 instance主run(¥36.9585)+n=2追加3 instance(¥5.8944) | ¥47.9886 | 29 instance全体でのS1-U効果測定、fresh-mode 3 instanceのn=2安定性データ | 再実行不要(iter4以降の比較基準として保持) |
| _12(iteration4) | R3/R3'自然文較正(¥7.8974、R3の¥3.7785含む累計) | ¥28.5644(29 instance主run) 計¥36.4618 | S1-U有効化後の29 instance測定、**real_run Escalation 0%(n=1)** | **「real_run Escalation 0%」はiter5のn=2実測で「n=1点推定は楽観的すぎた」と訂正済み**(実際は8.33%)。この特定の主張は無効化されたが、生データ(各instanceのcost/final_state)自体はn=2結合計算の一方の標本として現在も使用中であり無駄ではない |
| _13(iteration5) | R3''/R3'''較正(¥8.4443)+29 instance×n=2(¥62.3761) | ¥70.8204 | R3'''確定(93.48%一致、既存最高)、n=2非決定性の定量化(72.41%一致率)、2-of-2効果(46%がdowngrade)、cite-or-release検証(誤release0件)、品質劣化v2測定 | **成果と問題が同時に出た**: safety_A4が初解消(前進)。一方、不要Rewrite率悪化(44.4%→66.7/77.8%)・worst cost超過(¥4.04〜5.36、ただし合成群由来)・real_run Escalation実測値訂正、という「当初目的(不要Rewrite削減)は未達成」の結果も含む。**Status=ITER5_DONE_IMPROVEMENT_NEEDED**につき、この一部(特にR3'''自体のさらなる較正、品質劣化v2の再生成ロジック)はiteration6で見直される可能性がある(iteration6は別worker委任_14が作業中、本委任は一切未確認)。n=2の生データ(29 instance×2 sample)自体は再利用可能(次のiterationのbefore/after比較に使える) |
| **合計** | | **¥222.9756**(REPORT.md§14-10、Phase累計) | | |

### 今後再取得不要な既存Evidence(重複課金を避けるため明記)

- Stage1 variant確定(V4-A、S1-D不採用)の根拠データ一式(_07)。
- changed_actor n=15のFisher検定結果(p=0.00220、有意)。
- Stage2実単価(per-claim¥0.087〜0.112/call)・batch化/caching効果の実測値(_07)。
- hormuz HF-009に対するStage2独立診断3/3成功(_05/_06)。
- R3'''ルーブリック文言そのもの(現在採用中の較正セット、design書§4-9または該当箇所)。
- iter1〜iter5の29 instance×各run分の生JSON(`instances`/`instances_s1`/
  `instances_s2`配下)。次の代表ケースTrialで同一fixtureを使う場合はここから
  Stage1出力・cost内訳を再利用できる(下記§3参照)。

---

## 3. 代表ケースTrial向け再利用資産(パス・sha256)

次の代表ケース候補(Meta Hook/B3丸め/B3因果/Hormuz scope/既知Safety)に対応する、
既存Stage1出力(固定artifact、iteration5時点で再利用元として使われている
`instances_s1/`配下)。

| 代表ケース | instance_id | ファイル | sha256(64桁、`sha256sum`実測) |
|---|---|---|---|
| Meta Hook | `meta_run03_advanced` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/meta_run03_advanced.json` | `0b7eb72e78741643e68c0ec0d4a47a3830cd750d429c0f4053da72c4045cec60` |
| Meta Hook(Standard対) | `meta_run03_standard` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/meta_run03_standard.json` | `c58fbc930223b1a377a68286c349e9ae0dae0ee2708c0a20dfaa5eff9579832a` |
| Hormuz scope(HF-009) | `hormuz_run03_advanced` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/hormuz_run03_advanced.json` | `443f99fcc1dbea961c7d1e8140f3693f78f826bd3a12d79813ee377b31253733` |
| Hormuz scope(Standard対) | `hormuz_run03_standard` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/hormuz_run03_standard.json` | `73e69da89d7dd7f9e3173813cfbf14a527976a24dd2fb3751b6cd72d84ba1df0` |
| B3(丸め/因果) | `bgroup_B3` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/bgroup_B3.json` | `f14ffec987b364ab096e82b58aa284216fd9caa24bcaed33848f221479a56669` |
| 既知Safety(er009系9種) | `safety_er009_*` | `er052_output/open233_self_recovery_flow_runner_01_iter5/instances_s1/safety_er009_*.json`(9ファイル) | 個別未算出(時間予算により省略、必要なら次委任で算出) |

これらは`sha256sum`で実測した64桁の値(改竄検知用フィンガープリントとして利用可)。

これらの`instances_s1/*.json`は各instanceの`call_log`(Stage1〜Recheckまでの
call別usage/cost内訳)を含むため、代表ケースTrialでStage1を再利用する場合は
このJSONの`stage1_call_used=false`パスを踏襲すれば追加課金なしで再現できる。
本文・Ledgerそのものの所在(article本文ファイル)はdesign書のfixture inventory
(`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`等)を参照のこと
(本委任では新たに特定していない)。

---

## 4. 出力ファイル(未commit)

- `docs/pm/open233_cost_kpi_reaggregation_iter1to5_01.md`(本ファイル、新規)
- `docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_15.md`(新規)

**git add/commit/pushは実施していない**(委任文指示どおり、次の委任でcommit予定)。
