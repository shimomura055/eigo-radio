# phase2_plan_02: Phase 2 改訂計画(未実行・JPY0・Fable確認後の委任_03で実行)

01版(`../phase1_b/phase2_plan_01.md`)を、Opusレビュー必須修正M1〜M4とFable判断で改訂したもの。使用モデル(Phase 2予定): gpt-6-luna(Production同一。最新モデル原則の例外理由=比較可能性。本Phase 1修正ではLLM呼出なし)。reasoning effort等はProduction既定。

## 1. 条件
| 条件 | Prompt | shortlist | 対象 |
|---|---|---|---|
| C0 | 現行(Production) | `current`(Production現行構成の再生) | Coffee/meta/hormuz x Std/Adv |
| C1 | 現行 | **`alt_precision_guarded`**(主対照) | **Coffee Advのみ**(Std v5本文に`time lag`が無いため) |
| C2 | 改善(`prompt_after_02.txt`、短縮版) | `alt_precision_guarded` | Coffee/meta/hormuz x Std/Adv |
| C2' | 改善(同上) | 方式2のV2 shortlist(Phase D成果物を再利用、新規抽出callなし) | **Coffee Advのみ**(3 job) |
| C0' | 現行 | 方式2のV2 shortlist | ABC-A既存18 jobの結果を再利用(新規費用0) |

- 主対照shortlist = **`alt_precision_guarded`**(Fable判断の基本)。R1適用版`alt_precision_guarded_r1`は、「R1で希少単語の押し出しが減るなら主対照にする」という条件を**満たさなかった**(押し出し6件→6件、減らない)ため主対照にしない。R1はnoise除去のみ(`want to`/`close to`/`call it`の重要語行を6行除去、候補行token平均-18)で、Fable判断の対象として`shortlists_fixed_02.json`に残す。`improved`(拡大+U2+U3+U4、平均+247token)はPhase 2で使わない。
- Phase 2から`established_or_article_specific`欄を外した(schemaはProduction同一)。例示「take careよりtake care of」も削除済み。
- C0(Prompt+shortlist)の候補行は、Coffee Std/Adv・meta Std/AdvでProduction実run(`keywords_selector_prompt.txt`)の候補行とバイト一致を確認済み(`c0_byte_match_02.json`)。**hormuz run_02のProduction実runは候補一覧方式導入前の旧方式で候補行が存在せず、hormuzのC0は照合不能**(現行構成の再生であり、Production実runとの一致は未確認)。

## 2. 注意(M1・M4)
1. **C1の注釈**: 現行Promptは`contains: Cn`/`contained_in: Cn`注釈の意味を説明しない。C1(現行Prompt+guarded)では、Coffee Adv等の一部の行末にこの注釈が説明なしで渡る。C1とC0の差は「shortlistの差」と「説明のない注釈の影響」の合算。C2はPromptが注釈を説明する(ラベル統一=M1)。meta/hormuzのrowsには注釈が出ない(0件)ため、meta/hormuzではこの点は影響しない。
2. **方式1のshortlistでは測定不能な項目(M4)**: 下記は`current`/`improved`/`alt_precision_guarded`/`alt_precision_guarded_r1`のいずれにも**候補として存在しない**(test M4で全記事・全構成を確認)。
   - Coffee: `push prices up`、`be behind price increases`、`in the ring`、`its own hidden clock`、`pump one's fist`(`pumps`というword候補はあるが、`pump one's fist`のphraseは存在しない)
   - hormuz: `give back gains`、`take a sharp turn`(加えて`strait of hormuz`もword `strait`のみで存在しない=3語上限100の外)
   - したがって**受入2(記事独自比喩のImportant混入率)・受入4のnever_fragment・R8は、方式1のshortlist(C0/C1/C2)では測定不能**。これらを測れるのは方式2のV2 shortlist(C0'/C2')のみ。方式1の結果をこれらの観点で「改善した/しなかった」と解釈しない。
   - 期待ラベルの存在状況(30以上のラベル候補が各構成に在るか)は`phase2_label_coverage_02.json`。比較(C0 vs C2/C1)は**両条件のshortlistに共に存在する候補に限る**。`time lag`はC0に無くguardedにのみ存在(C0対比不可、C1/C2間では測定可)、`of a`はC0のみ(U3で消える)なので比較から除外する。
3. **Coffee v5のStdには`time lag`がない**(Std v5本文に無い)ため、`time lag`の受入1はCoffee Advのみ。

## 3. 評価の層(gate前とgate後を分ける)
- **選定指標(受入2〜6)は、gate前のselector生出力(5件+backup_item)で全jobを採点する**。gate(canonicalization/Redundancy QA)の失敗でjobが評価から落ちないようにする。
- gate結果は別層で集計: canonicalization(Rule7 INVALIDは`phase1_a/rule7_predicted_invalid_01.json`の35組と自動照合し、予測内=Rule7起因、予測外=選定能力/その他に分類)、Redundancy QA。
- **実挙動(コードで確認)**: `er064_kp_idiom_trial_01_select.run_canonicalization_and_qa`は、canonicalizationの状態が`CANONICALIZATION_PASS`/`CANONICALIZATION_REVIEW_REQUIRED`のどちらでもないとき(INVALID等)は、**Redundancy QAを実行せずに返る**(同じ分岐はProductionの`er003_v1_b1_scaffold_01_generate.py:307`等と同じ)。つまりINVALID jobにはRedundancy QA結果が無く、Redundancy NG率の分母はcanonicalizationを通ったjobに限る(INVALIDを理由にQA NGが隠れる/生じることはない)。自動retryはしない。
- jobごとに**usage(入力/出力/reasoning token)を必ず記録**(量産時のコスト試算用。ABCのcost_01.json形式に加えreasoning tokenを分離)。
- ja_gloss機械検査(括弧・算用数字・「…」・数値穴埋め形)で、グロス段落統合(D12)の副作用を確認。
- 副指標: Jaccard安定性(n=3)、費用/出力token/所要時間。`established_or_article_specific`の集計は行わない(欄を削除)。
- 判定の注意: n=3の小標本のため方向性の確認とする。「改善」はC2がC0に対して受入2/4/5/6のいずれかで改善し、かつRule7起因を除いた選定品質層が低下しない場合のみ(ただし上記のとおり受入2/4は方式1では測定不能な部分が大きい)。

## 4. 費用見積(`phase2_cost_estimate_02.json`、未実行の推定。単価=ABC実測 Std 1.1854 / Adv 0.9377 JPY/job、C0以外は+3%)
| Stage | 内容 | job数 | 費用 | 累計 |
|---|---|---|---|---|
| 1 | Coffee C0/C2 両Level(12) + C1 Adv(3) + C2' Adv(3) | 18 | 18.72 | 18.72 |
| 2 | meta C0/C2 両Level | 12 | 12.93 | 31.65 |
| 3 | hormuz C0/C2 両Level | 12 | 12.93 | 44.58 |

合計 **42 job / 約JPY44.58 / 上限JPY50**(停止規則JPY48まで残3.42、上限まで残5.42。+3%を載せない場合は43.84)。C0'は既存結果の再利用で0円。停止規則: 累計JPY48到達で新規job停止し報告、1 job > JPY2.5で即停止、自動retryなし、STOPセンチネル(`docs/pm/delegation_log/*STOP_NOTICE*`、`<run>/STOP`)を開始前に確認、再起動は委任文が許可した回数のみ。
- Std/Adv両方のC2'を入れると約JPY48の停止規則に掛かるためAdvのみ(Fable判断)。C2' Advの約JPY2.8(3 job)は上表に含まれる。
- 収まらない比較(未検証): meta/hormuzのC1、Coffee StdのC1、C3(新Prompt+現行shortlist)。

## 5. Phase 2実行前にFableが確認する事項
1. 期待ラベルDRAFT(`../phase1_b/phase2_expected_labels_draft_01.json`)の凍結。`established_or_article_specific`関連の副指標は削除。meta/hormuzの`avoid`はユーザー確認待ち。`pumps its fist`は方式1では測定不能(維持確認は方式2のみ)。
2. R1適用版を使うか(押し出し減少の条件は未達。noise除去のみ)。
3. V2 shortlistのrows書式が`contains: Cn`注釈を含むか(C2'のPromptが注釈を説明するため、含まない場合は説明が不要な文となる。実行前に確認)。
4. 並行実行とrate limit/APIキー競合、STOP通知の確認。
