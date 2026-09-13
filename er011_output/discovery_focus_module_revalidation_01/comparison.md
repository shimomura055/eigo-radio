# FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01: 比較Artifact

テーマ: "Why do we sometimes wake up right before the alarm rings?"(目覚まし時計が鳴る直前に自然に目が覚めることがあるのはなぜか)
Ledger再利用元: `er011_output/discovery_generalization_wake_before_alarm_trial_12/research/verified_fact_ledger.txt`(ledger_deviation overall_status=LEDGER_COMPLIANT、CONFIRMED[VERIFIED]のみ)。新規Research/Ledger作成なし。
条件差: `editorial_type_module_block`(Discovery Focus Module Part A、`er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`一字一句不変)の有無のみ。他は現行Production経路(`er003_v1_n3_01_articles_generate.run_one_pattern`)無変更。

採点者注記: 以下の0〜2点の定性スコア(Discoveryらしさ/Main Story/Point One価値/Point Two価値/Point多様性)は本タスク(Sonnet実行層)による主観評価であり、統計的検定ではない。N=1×2レベルのみ。

## 比較表(必須)

| 指標 | Baseline | Focus | 差 |
|---|---|---|---|
| Discoveryらしさ(0-2、「へえ」+quiet takeaway) | 1 | 2 | +1 |
| Main Story(現象提示に留め「なぜ」を出し切らないか、0-2) | 1 | 2 | +1 |
| Point One価値(0-2、Full Storyの言い換えでなく新規理解か) | 1 | 2 | +1 |
| Point Two価値(0-2) | 2 | 2 | 0 |
| Point多様性(0-2、Point One・Twoが異なる角度か、記事内評価) | 2 | 2 | 0 |
| Fact Safety(Fact Checker verdict / Ledger最終status) | PASS / LEDGER_COMPLIANT(A2・B1とも) | PASS / LEDGER_COMPLIANT(A2・B1とも) | 差なし |
| REVIEW_REQUIRED件数(fact_verdict=REVIEW_REQUIRED相当) | 0/2 | 0/2 | 0 |
| Point Overlap記事全体retry回数 | A2=0, B1=0 | A2=0, B1=0 | 0 |
| Local Rewrite発火(cycle数/item数) | A2=0/0, B1=0/0 | A2=1cycle/1item(resolved, human_review不要), B1=0/0 | Focus A2のみ1件発火・自動解消 |
| 差分QA(Local Rewrite後、target-sentence-matching+Fact Checker A'+Ledger再確認) | 該当なし(Local Rewrite未発火) | Focus A2の1件でapplied=true、fact_check_verdict=PASS、ledger再確認COMPLIANT、blocks_acceptance=false | Focus A2で1回実施・PASS |
| コスト(実測、writer段階のみ、A2+B1合算) | A2 baseline+focus合算61.70円/B1合算52.20円の内訳は本文参照 | 同上 | 4本合計113.91円(上限320円の36%) |

補足: word_count(本文語数): A2 baseline=471 / A2 focus=363 / B1 baseline=507 / B1 focus=442。全4本で avg_sentence_length は11.9〜14.5語、Directional Fact Precheck は4本すべてDIRECTION_REVIEW_REQUIRED(baseline/focus差ではなく、本Precheck層が全arm一律で出す挙動として観察。non-blocking advisory、記事のstatusはOKのまま)。

## 論点A(書き分け)詳細

### Main Story

- Baseline(A2/B1とも)は、現象提示のすぐ後に、概日リズム同調・ACTH上昇・前頭前野活動・心拍上昇という複数の生理学的知見を**Main Story自体の中で**具体的に列挙して説明していた(例: A2 baseline「Researchers have seen signs of preparation. When people expected sleep to end at a set time, a body chemical in the blood called ACTH rose about an hour before waking. In one self-awakening study, brain activity changed about 30 minutes before waking...」)。これはFocus Moduleが禁止する「Main Storyだけで「なぜ」を説明しきる」パターンに近い。
- Focus(A2)は、Main Storyを現象提示と問いの提示に留め、具体的な生理学的知見(ACTH等)をPoint Oneへ明示的に繰り延べていた(「There may be another part. When the end of sleep is expected, the body may begin preparing before the person is fully awake. The question is not whether the body has a hidden alarm, but whether several quiet changes build up before waking.」)。Focus Moduleの指示(「Main Storyでは、まず「何が観察されたか」という現象そのものを伝えてください。「なぜそれが起こるのか」という答えをMain Storyだけで説明しきってしまわないでください」)への追従が明瞭。
- Focus(B1)はA2ほど徹底しておらず、ACTH等の具体値をMain Story内でも一部言及していた(「In a laboratory study, a body signal called ACTH rose about an hour before people woke. Researchers interpreted this as part of a process...」)。ただし「researchers interpreted」という著者解釈の明示化はFocus Moduleの断定回避指示に沿っている。B1はA2よりMain Story分量そのものが多い記事タイプ(直接B1生成)であるため、完全な繰り延べは両立しにくい可能性がある。

### Point One・Point Two価値/多様性

- Baseline: A2/B1とも Point One=「練習された起床習慣(chronotype/practice)」、Point Two=「睡眠段階(sleep architecture、深いNREMほど起きにくい)」という2つの異なる角度を持ち、Full Storyには無い新情報(11人中82%成功率、643人調査の10.3%等)を提供していた。角度の分化自体は明瞭(スコア2)。
- Focus: A2 Point One=「ACTH→前頭前野→心拍という段階的countdown」、Point Two=「self-awakening文献における練習・期待の役割」。B1 Point One=「概日ペースメーカーを限定された同調範囲を持つsynchronizerとして再定義」、Point Two=「学習されたスキルとしてのself-awakening」。Point One・Two間の角度分化はFocusでも明瞭(スコア2)。
- 観察(N=1のため確定的ではない): Baselineでは2本とも「睡眠段階(sleep architecture)」という角度がPoint Twoに登場したのに対し、Focus 2本ではどちらも「睡眠段階」角度が一切登場せず、代わりに「概日ペースメーカーの限定範囲」または「生理学的段階的countdown」という角度に収束していた。記事単体で見るとPoint One・Twoの分化は保たれているが、Focus条件下でA2とB1の間で採用される「角度の引き出し」がやや似通う(mechanism-limit系 + practice-skill系の2つに収束)可能性がある。N=1×2につき、これがFocus Module固有の効果か偶然かは本Trialだけでは判別できない。

### 「へえ」・throughline

- Focus arm はIn One Lineで比喩的な言い回し(A2: "a quiet countdown, not a perfect time reading"、B1: "a meeting point between a body clock, a familiar routine, and expectation")を使い、Main Story冒頭の「問い」からPoint One・Twoの内容へ戻る一貫したthroughlineを保っていた。
- Baseline arm のIn One Lineは要約寄り(A2: "Your body may prepare for a familiar wake-up time while sleep becomes easier to leave...")であり、悪くはないが、Main Storyが既に結論の大半を出しているため、In One Lineの「持ち帰り感」がFocus armよりやや弱い。

## 論点B(副作用)

- Fact Checker: 4本ともverdict=PASS、unsupported_specific_claims=0件。
- Ledger Deviation: 4本とも最終overall_status=LEDGER_COMPLIANT。A2 baselineはMINOR相当の逸脱1件(Local Rewrite不要、閾値未満)。A2 focusはMAJOR逸脱1件を検出、Local Rewrite cycle 1で解消(human_review_required=false)。
- Local Rewrite後の差分QA(2026-09-13配線、既定ON): A2 focusの1件で実施。target-sentence-matching使用、Fact Checker A'再実行(verdict=PASS)、Ledger Deviation Checker再確認(COMPLIANT)、Point Overlap再計算(該当、overlap_ratio=0.229・flagged該当なし)。blocks_acceptance=falseで受理。
- Point Overlap QA: 4本とも記事全体retry 0回(overlapなし、初回で解消)。cross_point_overlap比率はA2 baseline 0.03/0.029、A2 focus 0.15/0.171、B1 baseline 0.061/0.053、B1 focus 0.1/0.094 — いずれも閾値未満だが、Focus armの方がPoint One・Two間の字面共有語がやや多い(Point Role Planningが同じLedger断片[ACTH等]をPoint OneとMain Story双方の関連語彙として使うため語彙面での近さがわずかに増える可能性、内容的な重複ではない)。
- REVIEW_REQUIRED: 0/4(Trial-09 current_focus 0/6、Trial-10 current_focus 0/6と整合。Trial-07の「約17%/Focusあり約67%」水準は再現されず、旧Household Ledger FACT-03問題の影響を受けない現行Ledger下では観察されない)。
- word count / sentence length: Focus armの方がやや短め(A2: 471→363語、B1: 507→442語)。avg_sentence_lengthはA2 baseline 11.9語、A2 focus 12.4語、B1 baseline 14.5語、B1 focus 13.7語で大差なし。
- コスト: 4本合計113.91円(内訳 writer_a2ステージ61.70円、writer_b1ステージ52.20円、pricing_snapshot換算)。上限320円の36%。Local Rewrite 1cycle(A2 focus)を含めてもこの範囲。

## 論点C(Point Role PlanningがFocusを知らない構造)の観察

Gate 4静的確認で機械確認済み: `er011_point_role_value_planning_01.run_point_role_planning(client, topic, verified_ledger_text, model, reasoning_effort)` のシグネチャに `editorial_type_module_block` 引数は存在しない(4 armとも同一のtopic/ledgerがrole planningへ渡っており、Focus Moduleの有無はrole planning自体には伝わっていない)。

- 4 armの役割計画(role plan)を比較すると、Point One/Twoの割り当てる「角度」はarmごとに異なっていた(A2 baseline: 練習habit / 睡眠段階、A2 focus: 生理学的countdown / practice-expectation、B1 baseline: 睡眠段階 / practice、B1 focus: 概日限定範囲 / practice-skill)。同一入力(topic/ledger)にもかかわらずrole planが4通りとも異なるのは、主に**モデルの非決定性**によるものであり、Focus Moduleの有無による系統的な差ではない(role planningにFocusは渡っていないため)。
- WriterとRole Planの競合(役割指定を無視・矛盾する記述)の実例は4 armとも見つからなかった。Focus armのWriterはrole planが指定した角度(例: B1 focus Point Oneの"synchronizer, not a perfect stopwatch"という比喩)をそのまま採用しており、Focus Module本文(Main Story抑制・角度分化・断定回避)とrole planの内容が矛盾する箇所は観察されなかった。
- 一方で、Focus ModuleはMain Storyの記述方針(現象提示に留める)を直接指示するのに対し、role planningはMain Story側の記述方針を一切考慮せず(topic文字列とledgerのみを見てPoint One/Twoの役割を決めている)、結果的に「Main Storyで何を出し切るか」はWriter本体のみがFocus Moduleの指示に従って調整している。B1 focusでMain StoryにACTHの具体値が残っていた(A2ほど徹底されなかった)のは、この構造(role planがMain Story側の抑制を意識していない)が一因である可能性がある。**接続実装は行っていない。観察のみ。**

## Gate 1判定材料

- 差は明瞭か: Main Story抑制・In One Lineのthroughline/「へえ」の点でFocus armが一貫して優位(A2で最も明瞭、B1でも同方向)。Point Two価値・記事内Point多様性は両arm同水準(差が明瞭でない)。
- 品質問題の有無: 4本ともFact Checker PASS・Ledger最終COMPLIANT・REVIEW_REQUIRED 0件。Focus A2で1件のLedger MAJOR逸脱が発生したが、既存Local Rewrite+差分QA機構で自動解消し、human_review_required=falseで着地した(新しいfailure modeではなく、既存安全装置が想定通り機能した事例)。
- N増しの要否(材料、実行はしない): (1)Main Story抑制の効果はA2で明瞭・B1でやや弱く、レベル間差の再現性確認にはN増しが有用。(2)cross-article角度収束(睡眠段階角度の消失)がFocus固有の効果か偶然かはN=1×2では判別不可、追加テーマまたは追加runでの確認が望ましい。(3)Point One価値・Discoveryらしさの差自体はA2/B1とも同方向に出ており、大きな追加Nなしでも方向性の判断材料にはなり得る。

## 4記事本文比較

(Full Story / Point One / Point Two / In One Line / Point Role Planning出力の全文は `index.html` に並置。各記事全文は `<level>_<arm>/article.md` を参照。)
