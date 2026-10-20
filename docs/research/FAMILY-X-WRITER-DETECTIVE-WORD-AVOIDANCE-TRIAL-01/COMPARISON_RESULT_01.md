# COMPARISON_RESULT_01: Writer Detective単語回避 Trial 比較結果

- 生成: `er086_output/writer_detective_avoidance_trial_01/{A,B,C}`、Baseline=`er019_output/middle_east_yemen_saudi/run_mey_02`(変更なし)。詳細=`eval/results.json`。
- 注: Pattern Aの初回生成(out-dir `A`)はProduction JA記号QA(R2再実行後も全角コロン残存)でSTOPし本文未完成のため、評価には再生成分(`A_rerun1`、同一条件)を使用。初回A費用JPY14.221は総費用に含む。
- 注: 各Pattern n=1。Production過去のFamily X JA R2 24件中の『探偵』出現は2件(約8%、Grep)であり、n=1でdetective=0でも追加指示の効果の証明にはならない(効果判定ではなく『単語を消しつつ品質を保てるか』の確認)。
- 評価LLM: gpt-6-luna(ラベル伏せ・ランダム順・2回)。

## 1. detective件数(工程別、大小文字不問substring/派生/JA探偵)

| 変種 | R0(JA) | R1(JA) | R2(JA) | Advanced | Standard |
|---|---|---|---|---|---|
| Baseline | 探偵0 | 探偵0 | 探偵2 | 2(派生0) | 2(派生0) |
| A | 探偵0 | 探偵0 | 探偵0 | 0(派生0) | 0(派生0) |
| B | 探偵0 | 探偵0 | 探偵0 | 0(派生0) | 0(派生0) |
| C | 探偵0 | 探偵0 | 探偵0 | 0(派生0) | 0(派生0) |

出現文(0件でないもののみ):
- Baseline/R2: 「…いのか」。今回は、その主語を追うニュース探偵の出番だ。  まずは発表を確認しよう。サ…」 / 「…撃しないって言いましたよね？」  ここで探偵、名札を拡大する。「攻撃しない」と説明さ…」
- Baseline/Adv: 「…rom the minutes: who won’t attack? This time, it’s the news detective’s turn to track down the subject.  First, let’s check the…」 / 「…t! You just said they wouldn’t attack, right?”  Here, the detective zooms in on the name tag. The phrase “won’t attack” refers …」
- Baseline/Std: 「…the meeting notes: who will not attack? This time, the news detective must find the subject.  First, let’s look at the announce…」 / 「…t! You just said they wouldn’t attack, right?”  Here, the detective looks closely at the name tag. “Won’t attack” means the Typ…」

## 2. 類似語観測(件数と文脈のみ。禁止リスト化しない)

| 変種 | R2(JA) | Advanced | Standard |
|---|---|---|---|
| Baseline | 2 | 1 | 1 |
| A | 0 | 0 | 0 |
| B | 0 | 0 | 0 |
| C | 0 | 0 | 0 |

- Baseline/R2: 「…給油支援の対象を見て「ならタイフーンも攻撃するんだ」と読むのも、証拠を飛び越えた推理になる。  ニュース読解の必携道具は、虫眼鏡より三つの質問。「誰が？」「どの任務…」 / 「…するんだ」と読むのも、証拠を飛び越えた推理になる。  ニュース読解の必携道具は、虫眼鏡より三つの質問。「誰が？」「どの任務で？」「何をする？」。「守るため」という大き…」
- Baseline/Adv: 「…e tools you need to read news are not a magnifying glass, but three questions: “Who?” “For which…」

## 3. Entertainment(LLM判定、5観点×2回の平均、1〜5)

### Adv

| 変種 | 平均 | hook | flow | surprise_structure | readability_pull | no_unnatural_staging | run1平均 | run2平均 | 順位(run1,run2) |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 2.7 | 3.0 | 3.0 | 3.0 | 3.0 | 1.5 | 2.8 | 2.6 | [4, 4] |
| A | 2.9 | 3.0 | 3.0 | 3.5 | 3.0 | 2.0 | 2.8 | 3.0 | [3, 3] |
| B | 3.7 | 4.0 | 4.0 | 3.5 | 4.0 | 3.0 | 3.8 | 3.6 | [2, 2] |
| C | 4.3 | 4.0 | 4.5 | 4.0 | 4.0 | 5.0 | 4.4 | 4.2 | [1, 1] |

### Std

| 変種 | 平均 | hook | flow | surprise_structure | readability_pull | no_unnatural_staging | run1平均 | run2平均 | 順位(run1,run2) |
|---|---|---|---|---|---|---|---|---|---|
| Baseline | 2.9 | 3.5 | 3.0 | 3.0 | 3.0 | 2.0 | 3.0 | 2.8 | [4, 4] |
| A | 3.4 | 4.0 | 3.5 | 4.0 | 3.5 | 2.0 | 3.6 | 3.2 | [3, 3] |
| B | 3.8 | 4.0 | 4.0 | 4.0 | 4.0 | 3.0 | 3.8 | 3.8 | [2, 1] |
| C | 3.9 | 3.5 | 4.0 | 3.5 | 3.5 | 5.0 | 4.4 | 3.4 | [1, 2] |

根拠引用(hook、run1/run2):
- Adv/Baseline: 「“Won’t attack.” At that one line, you were about to end the meeting in your head with the conclusion, “So Britain will only defend.”」 / 「“Won’t attack.” At that one line, you were about to end the meeting in your head with the conclusion, “So Britain will only defend.”」
- Adv/A: 「Fighter jets are coming. But they won’t attack.」 / 「Fighter jets are coming. But they won’t attack.」
- Adv/B: 「“We won’t attack.” If so, their role must be that of a “shield.”」 / 「“We won’t attack.” If so, their role must be that of a “shield.”」
- Adv/C: 「Britain is sending fighter jets, but not to attack the other side.」 / 「Britain is sending fighter jets, but not to attack the other side.」

## 4. 事実(決定論 + LLM事実検査)

| 変種 | レベル | LLM unsupported件数(MAJOR/MINOR) | new_major_error_count | Houthi launcher | 連合軍報道官帰属 | Ledger+briefに無い固有語/数字 |
|---|---|---|---|---|---|---|
| Baseline | Adv | 0(0/0) | 0 | True | True | About, According, Air, Arabia, Attack, Britain, British, But, Defence, Doing, Don, Even, First, Force, Here, Houthi, Houthis, Just, Meanwhile, Ministry, Mixing, Right, Riyadh, Royal, Saudi, Saudi-led, Says, Subject, Support, That, The, Then, They, This, Typhoon, Typhoons, Wait, Warning, What, Who, Won, Yemen, You |
| A | Adv | 2(1/1) | 1 | True | False | According, Also, Arabia, Attack, Before, Britain, But, Defence, Did, Didn, Even, Fighter, Forget, Houthi, Houthis, Ministry, Riyadh, Saudi, Saudi-led, Subject, The, Then, These, This, Typhoon, Typhoons, Wait, What, When, Whose, Won, Yemen, Yes, You |
| B | Adv | 1(1/0) | 1 | True | True | According, Air, And, Arabia, Attack, Before, But, Defense, Does, Even, Explanation, First, Force, Houthi, Houthis, Include, Let, Ministry, One, Refueling, Riyadh, Royal, Saudi, Saudi-led, That, The, They, This, Typhoon, Typhoons, Wait, Wasn, Who, Won, Yemen |
| C | Adv | 0(0/0) | 0 | True | True | According, Another, Arabia, Attack, Britain, British, But, Defence, Deploy, Even, Fighter, Has, Houthi, Houthis, Jets, Ministry, Riyadh, Saudi, Saudi-led, Seen, Set, Side, Support, That, The, They, This, Typhoon, Typhoons, Won, Yemen |
| Baseline | Std | 1(1/0) | 1 | True | False | About, Air, Arabia, Attack, Both, Britain, British, But, Defence, Doing, Don, First, Force, Here, Houthi, Houthis, Its, Look, Ministry, Mixing, Now, One, Putting, Right, Riyadh, Royal, Saudi, Saudi-led, Says, Support, The, Their, Then, They, This, Typhoon, Typhoons, Wait, Warning, When, Who, Won, Yemen, You |
| A | Std | 1(0/1) | 0 | True | True | According, Also, Arabia, Attack, Before, Britain, But, Check, Defence, Did, Didn, Even, Fighter, Forget, Houthi, Houthis, Ministry, Riyadh, Saudi, Saudi-led, Subject, The, Their, Then, These, This, Typhoon, Typhoons, Wait, What, When, Whose, Won, Yemen, Yes, You |
| B | Std | 2(2/0) | 2 | True | False | Air, Also, And, Arabia, Attack, Before, But, Defense, Didn, Does, Even, Force, Houthi, Houthis, Include, Its, Let, Ministry, One, Refueling, Riyadh, Royal, Saudi, Saudi-led, That, The, Their, They, This, Typhoons, Wait, What, Who, Won, Yemen |
| C | Std | 3(0/3) | 0 | True | True | Another, Arabia, Are, Attack, Britain, British, But, Defence, Fighter, Has, Houthi, Houthis, Jets, Ministry, Riyadh, Saudi, Saudi-led, Seen, Side, Support, That, The, These, They, This, Typhoon, Way, What, Won, Yemen |

### LLM指摘の詳細(unsupported_claims)

- A/Adv [MINOR] 「Fighter jets are coming.」: The ledger supports the UK’s announcement of a planned Typhoon air-defense mission, but does not establish that the jets are already coming or have been deployed. This is loose wording that makes the plan sound more immediate.
- A/Adv [MAJOR] 「The Houthis fired one ballistic missile toward Riyadh, Saudi Arabia.」: The ledger records this as the Saudi-led coalition spokesperson’s report, not as an independently verified fact. The article states the launch as fact and does not attribute that claim to the spokesperson.
- B/Adv [MAJOR] 「In response to these threats, the UK Ministry of Defense said that Royal Air Force Typhoons would carry out air defense missions.」: The ledger supports the Typhoon air-defense announcement and its purpose of protecting against aerial attacks, but does not establish that the announcement was made in response to the missile interception just described.
- Baseline/Std [MAJOR] 「The Houthis had fired it toward Riyadh.」: The ledger says the coalition spokesperson announced that the Houthis fired the missile. This sentence states the launch as fact without attributing it to the spokesperson, making the report sound independently established.
- A/Std [MINOR] 「Fighter jets are coming, but they will not attack.」: The ledger supports the UK’s announcement of a Typhoon air-defense mission, but does not establish that the jets are already on their way or when they will arrive. The article later clarifies that the UK announced plans, not completed actions.
- B/Std [MAJOR] 「The Houthis had fired it toward Riyadh.」: The ledger supports this only as part of the Saudi-led coalition spokesperson’s reported announcement. This sentence states the launch as fact without attributing it to the spokesperson, making the claim stronger than the ledger supports.
- B/Std [MAJOR] 「The UK Ministry of Defense responded to these threats.」: The ledger says the UK announced defensive support, but does not establish that the announcement was a response to the missile interception or to these specific threats.
- C/Std [MINOR] 「# “Fighter Jets That Won’t Attack” Are on the Way—Britain’s Support Has Another Side」: The ledger records the Ministry of Defence’s announcement of a future defensive mission, but does not establish that the jets are already on their way.
- C/Std [MINOR] 「Britain is sending fighter jets, but they will not attack the other side.」: The ledger supports an announced future Typhoon mission, not the claim that the jets have already been dispatched or are en route.
- C/Std [MINOR] 「This time, the story is not only about the fighter jets arriving.」: The ledger describes an announced future mission and does not establish that the jets have arrived.

### Houthi言及文(Advanced)

- Baseline: A spokesperson for the Saudi-led coalition forces in Yemen said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis.
- Baseline: The mission is limited to defense, and the jets will not attack the Houthis.
- Baseline: That support also covers operations to weaken Houthi military targets in Yemen.
- Baseline: Meanwhile, refueling support also backs operations to weaken Houthi military targets.
- Baseline: Britain said its Typhoon jets would defend Saudi cities and key facilities, not attack the Houthis, while its refueling support also backs operations to weaken Houthi military targets.
- A: The Houthis fired one ballistic missile toward Riyadh, Saudi Arabia.
- A: The UK says they will not attack the Houthis.
- A: This support also covers operations to weaken Houthi military targets in Yemen.
- A: It would be wrong to read this as, “Then will the Typhoons attack the Houthis too?” What the fighter jets do and what operations the refueling support backs are two separate things.
- A: Britain says its Typhoon jets will defend Saudi Arabia, not attack the Houthis; refueling support will also back operations against Houthi targets.
- B: A spokesperson for the Saudi-led coalition in Yemen announced that it had intercepted and destroyed a ballistic missile launched by the Houthis toward Riyadh.
- B: They would not attack the Houthis, it said.
- B: According to the announcement, this support also covers operations to weaken Houthi military targets inside Yemen.
- B: The UK says its Typhoons will only defend Saudi cities, while its refueling support also covers operations to weaken Houthi targets in Yemen.
- C: A spokesperson for the Saudi-led coalition said it had intercepted and destroyed one ballistic missile fired by the Houthis toward Riyadh.
- C: Britain also says it will limit the mission to defense and will not attack the Houthis.
- C: That support also covers operations to weaken Houthi military targets inside Yemen.
- C: The Typhoons themselves have a clear limit: they will not attack the Houthis.
- C: But if we take it to mean “British fighter jets will attack the Houthis,” we misunderstand the limits placed on the Typhoons.
- C: Britain says its Typhoon jets will defend Saudi cities and key sites, not attack the Houthis.
- C: But its extended refueling support also covers operations to weaken Houthi military targets in Yemen, so its support is not purely defensive.

## 5. QCD(Writer工程のみ。Research/B3/RF/音声は含まない)

| 変種 | Writer費用JPY | R0 | R1 | R2 | Advanced(英訳+IOL) | Standard | LLM呼出数 | 失敗呼出(success=False) | Adv/Std 段落retry | LLM呼出秒合計 / 壁時計秒(writer/adv/std/total) | 文字数(R2JA/Adv/Std) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 13.275 | 6.739 | 2.663 | 3.291 | 0.385 | 0.197 | 6 | 0 | False/False | 233.0 / None/None/None/None | 892/2727/2583 |
| A | 13.742 | 5.649 | 3.591 | 3.828 | 0.309 | 0.365 | 6 | 0 | False/False | 223.7 / 157.8/26.0/40.0/223.8 | 904/2695/2579 |
| B | 14.086 | 7.154 | 2.684 | 3.738 | 0.27 | 0.24 | 6 | 0 | False/False | 222.3 / 178.9/21.8/21.7/222.5 | 906/2773/2543 |
| C | 11.847 | 5.66 | 2.977 | 2.723 | 0.234 | 0.253 | 6 | 0 | False/False | 197.3 / 156.4/19.0/22.0/197.4 | 983/2868/2750 |

モデル: Baseline=['gpt-6-luna', 'gpt-6.1-sol']; A=['gpt-6-luna', 'gpt-6.1-sol']; B=['gpt-6-luna', 'gpt-6.1-sol']; C=['gpt-6-luna', 'gpt-6.1-sol']
評価LLM費用(判定): JPY 1.81

## 6. 機械判定(事前固定規則)

```json
{
  "A": {
    "detective_zero_adv_std": true,
    "llm_new_major_errors": 1,
    "manual_major_errors": 1,
    "fact_ok": false,
    "entertainment_adv_ok": true,
    "entertainment_std_ok": true,
    "status": "NOT_CANDIDATE"
  },
  "B": {
    "detective_zero_adv_std": true,
    "llm_new_major_errors": 3,
    "manual_major_errors": 1,
    "fact_ok": false,
    "entertainment_adv_ok": true,
    "entertainment_std_ok": true,
    "status": "NOT_CANDIDATE"
  },
  "C": {
    "detective_zero_adv_std": true,
    "llm_new_major_errors": 0,
    "manual_major_errors": 0,
    "fact_ok": true,
    "entertainment_adv_ok": true,
    "entertainment_std_ok": true,
    "status": "CANDIDATE"
  },
  "_overall": {
    "candidates": [
      "C"
    ],
    "pick_if_tie_shortest_instruction": "C",
    "label": "CANDIDATE_MACHINE:C"
  }
}
```
