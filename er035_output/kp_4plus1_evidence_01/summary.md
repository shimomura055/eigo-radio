# KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 Phase B 検証evidence summary

生成元: `er035_kp_4plus1_topic_phrase_evidence_01_run.py`(実行コマンド:
`.venv\Scripts\python.exe er035_kp_4plus1_topic_phrase_evidence_01_run.py
--out-dir er035_output/kp_4plus1_evidence_01 --budget-jpy 80`)。
melos_a2のみ、初回バッチ内で2回失敗(1回目: 既存source_sentence整合性
チェック起因・4+1と無関係、2回目: role構成不成立[topic=2件]で4+1
validatorが正しく機能した実例)したため、`er003_v1_n3_01_scaffold_generate.
run_key_phrases`を直接呼ぶ3回目の独立呼び出しでPASSを取得し直した
(詳細は`melos_a2/evidence_summary.json`の`note`フィールド)。

対象9件(Family X News 4件×DB Hybrid、Family Z/legacy Family B・C 4件×
Strategy L、forced_fallback 1件)、実測selection cost合計 ¥4.8383
(Guardrail¥80の約6%)。

## 10観点表

### 観点1: 構造PASS(4 important + 1 topic)

全9件が最終的に`KEY_WORDS_STRUCTURE_PASS`かつ`role_counts`={important:4,
topic:1}を達成(melos_a2は上記のとおり3回目で到達)。5件経路
(`expected_item_count==PRODUCTION_ITEM_COUNT_UNCHANGED`)でのみ4+1集計
検証が働くという設計どおりの挙動を実データで確認。

### 観点2: Topic Phrase該当性の主観判定(選定理由を逐語転記)

| 記事 | Topic Phrase | 選定理由(逐語) |
|---|---|---|
| meta_a2 | contract workers | 「AIの裏側で実際に電話をしていた人々を指し、記事中で繰り返される中心語である。構成語から大意は推測しやすいが、事前に分かっていると人間の関与を示す各場面を追いやすい。」 |
| meta_b1b | contract workers | 「AIの代わりに実際の会話を担当した人々を指し、記事の中心的な事実を支える表現。三回登場するため、先に分かると本文全体を追いやすい。」 |
| hormuz_a2 | be taken back | 「記事のタイトルと中心的な出来事を示し、20%案が撤回されたという全体の流れを最初に決める表現。」 |
| hormuz_b1b | sea blockade | 「原油上昇の背景と終盤の懸念をつなぐ、この記事の中心的な地政学表現である。」 |
| melos_a2 | execution | 「冒頭の処刑の脅しと終盤の処刑場面をつなぐ、この記事の題材理解に不可欠な語。」 |
| twins_a2 | digital twin | 「記事の中心設定を示す表現で、本文全体の出来事を追うために事前理解の価値が高い。digital と twin だけからAI上の分身という意味を瞬時に取るのは難しい。」 |
| twins_b1 | digital twin | 「記事全体の前提となる存在を指し、Echoが単なる音声アシスタントではなくMaraの分身であることを理解するために不可欠。」 |
| ai_hiring_a2 | fairness check | 「後半の規制、公開通知、偏りの確認の話を追うための題材固有の中心語である。」 |
| forced_fallback | fly away | 「短文の動物行動の中で、鳥がどう動くかを決める中心表現であり、最後の内容を取り違えると理解が止まりやすい。」 |

主観評価(Sonnet所見): 全件が中心質問「事前に理解していると本文を明確に
追いやすくなるか」に整合する理由付けになっている。特にNews記事(Meta/
Hormuz)では記事全体で繰り返される中心語("contract workers"3回、
"sea blockade"2回)、Fiction(twins/Melos)では物語前提そのもの
("digital twin"、"execution")が選ばれており、ユーザー定義のTopic概念
(汎用性は必ずしも高くないが記事特有で理解の前提となる語)と整合する。
"fairness check"(ai_hiring)は記事後半の専門的な話題の核であり同様に妥当。

### 観点3: 固有名詞への偏り

9件のTopic Phraseはいずれも人名・企業名・ブランド名・地名ではない
(普通名詞・句動詞・専門用語のみ: contract workers/be taken back/
sea blockade/execution/digital twin/fairness check/fly away)。
「固有名詞枠ではない」というユーザー方針への抵触は観測されなかった。

### 観点4: Important 4件の品質比較(同記事の既存Production KP 5件との差分)

比較対象: `er030_output/family_x_kp_source_reference_contract_evidence_01/
{key}/key_phrases/keywords_canonicalized.json`(4+1適用前、Source
Reference Contract PRODUCTION_WIRED時点の5件、同一本文・同一backend)。

| 記事 | 旧5件 | 新4 important+1 topic | 重複度 |
|---|---|---|---|
| meta_a2 | concierge/contract workers/take off/take over/speak for | important: speak for/concierge/pull back/take over, topic: contract workers | 概念重複4/5(take offのみ非継続、pull back新規) |
| meta_b1b | roll back/concierge/contract workers/stand behind/speak for | important: turn out/be rolled back/concierge/take over, topic: contract workers | 概念重複3/5(roll back≒be rolled back、concierge、contract workers) |
| hormuz_a2 | take back/Brent crude/center stage/give back/sea blockade | important: give back/Brent crude/sea blockade/center stage, topic: be taken back | 概念重複5/5(take back≒be taken back含め全概念が継続、roleラベルのみ変化) |
| hormuz_b1b | sea blockade/Brent crude/give back/center stage/flashy | important: give back/the Strait/center stage/pass through, topic: sea blockade | 概念重複3/5(sea blockade/give back/center stage継続、Brent crude・flashyが非継続) |
| melos_a2 | execution/one's word/stay on/fair trial/fall into | important: give one's word/in one's place/speak against someone/fall to one's knees, topic: execution | 概念重複3/5(execution/one's word≒give one's word/fall into≒fall to one's knees) |

Sonnet所見: 5記事中とくにhormuz_a2は旧5件と新4+1が概念的にほぼ完全一致
(Topic役割になった項目も含め)。他記事も3〜4/5の概念重複があり、
Important枠が1つ減ったことによる品質劣化の兆候(専門性の低い一般語への
質的低下等)は観測されなかった。新規に入った項目(pull back/turn out/
the Strait/pass through/in one's place/speak against someone)も、
記事内の重要な事実・展開に関わる表現であり、Listening Blocker Ranking
の既存優先順位と整合する。

### 観点5: Redundancy QA発火率

9件中3件(meta_a2・hormuz_a2・hormuz_b1b、すべてDB Hybrid Family X)で
1回のRedundancy QA NG retry(4+1構造+Redundancy双方を満たす選定への
やり直し)が発火し、いずれも1回のretryでREDUNDANCY_PASSに到達
(NG_REVIEW_REQUIREDへ到達した記事なし)。発火率33%(3/9)。

### 観点6: canonicalization QA PASS率

9/9件が`CANONICALIZATION_PASS`(REVIEW_REQUIRED到達なし)。100%。

### 観点7: Stage 1候補にTopic該当語が存在したか(DB Hybridのみ)

候補ID方式Source Reference Contractのschema enum制約により、選定
itemのsource_candidate_idは必ずStage1 shortlistの候補から選ばれる
(構造的に「存在しない候補」を選ぶことが不可能)。実データでは4件の
DB Hybrid成功例すべてで、Topic該当語は既存の「重要な単語・単語群候補」
区分(important_noun_candidates、3件)または「phrase/idiom/phrasal
verb候補」区分(phrase_survivors、1件[hormuz_a2のbe taken back])
から選ばれており、Topic専用の新しい候補区分は存在しない(Phase A設計書
B-4の予測どおり)。forced_fallback(意図的に候補プールを枯渇させた
記事)では、db_hybrid_stage1_debug.jsonにTopic該当語("fly away")が
0件で存在せず、DB Hybrid自体がSHORTLIST_TOO_SMALLでStrategy Lへ
fallbackしたため、Topic Phraseは全文自由選択のStrategy L側で得られた
(F-1で懸念された「候補プールにTopic該当語が存在しない」ケースの、
候補プール自体が薄い記事における具体例)。

### 観点8: retry発火率・追加コスト

- DB Hybrid選定costは1件あたり¥0.9574〜¥1.6032(4件合計¥4.8383)。
  Redundancy QA retryが発生した3件はretry無しの1件(meta_b1b
  ¥1.2566)より高コストになる傾向(hormuz_b1b ¥1.6032が最大)だが、
  4+1化による追加LLM callは新設していない(既存selector call内で
  処理、設計どおり)。
- Strategy L選定(melos/twins/ai_hiring/forced_fallback)のcost_jpyは
  既存Productionが元々計測していない(OPEN-206既知の限界、本タスク
  による新規劣化ではない)。
- melos_a2は評価作業中に計3回の独立呼び出しを要した(cost_jpy計測
  対象外のStrategy L呼び出しのため合計費用への計上はできないが、
  Guardrail¥80に対し無視できる規模)。

### 観点9: fallback発火時の4+1維持

forced_fallback(SHORTLIST_TOO_SMALL→Strategy Lへfallback)でも
`role_counts`={topic:1, important:4}を維持したまま
`KEY_WORDS_STRUCTURE_PASS`に到達。DB Hybrid→Strategy Lへのfallback後も
4+1構造が壊れないことを実データで確認。

### 観点10: 補助候補データ(auxiliary_candidates)の有無・件数

DB Hybrid経路4件は`kp_auxiliary_candidates.json`を生成、件数は
meta_a2=17件、meta_b1b=19件、hormuz_a2=15件、hormuz_b1b=15件
(いずれも「未検証・参考候補」フラグ付き、件数上限なし・shortlist
出現順)。Strategy L経路(melos/twins/ai_hiring/forced_fallback)は
`auxiliary_candidates: null`+`auxiliary_candidates_reason:
"not_available_strategy_l"`を記録(表示件数・UI配置は未定のまま、
ユーザー判断待ち)。

## 補足: STOP候補/USER_DECISION候補(観測ベース)

- F-1関連の実観測: forced_fallbackのように候補プール自体が薄い記事
  では、Topic該当語がStage1候補に存在しないままStrategy Lへ委ねられる
  ケースを実際に観測した(本ケースはDB Hybrid全体がfallbackしたため
  Topic枠だけの問題ではないが、F-1が懸念した状況の具体例)。DB Hybridの
  4件成功例では、shortlistが十分な記事であればTopic該当語は既存の
  important_noun/phrase候補区分から機械的に見つかる状況だったが、
  「一度しか出現しない一般語だが記事のTopic理解に必須」という
  Phase A設計書が懸念した狭いケースは、今回の9件では観測されなかった
  (対処案は実装せず、追加のUSER_DECISION対象とはしない範囲の所見)。
- Strategy L経路(max_attempts=1固定、本タスク以前からの既存挙動)で
  role構成不成立(melos_a2の2回目試行、topic=2件)が発生すると、
  `run_key_phrases`は即座に失敗を返し自動retryしない(既存の
  redundancy retryループは選定status不合格時には作動しない設計のため)。
  これは4+1導入前から存在する構造(max_attempts=1)であり本タスクの
  新しい分岐ではないが、4+1という追加の構造的制約により、Strategy L
  経路での初回選定失敗率がわずかに上がりうることは事実として報告する
  (対処[max_attempts変更等]は実装せず、Fable/ユーザー判断待ち)。
