# ROOT_CAUSE_01: 既存Trial(school_phone_ban)の品質不足の根本原因(FAMILY-Y-VOICES-DESIGN-01 委任_07 Phase A)

Status: 調査のみ(API 0・LLM呼出0・Production変更0・`er110_*`変更0)。ユーザー原文=`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_03.md`(全文読了)。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。
読取対象(基準dir `er110_output/family_y_trial_01/school_phone_ban/`、以下Y): `y_cast/{cast_candidates,voice_cards}.json`、`y_writer/gate_r0|gate_r2/{article_before_judgement1,article_final,leak_check_1}`、`y_writer/ablation_a0_light/r0_final.md`、`research_ledger/verified_fact_ledger.txt`(15件)、`storyline_b3/selected_brief.md`、コード`er110_family_y_text_trial_01.py`(以下`er110`)。
定量baseline: `persona_metrics_probe_01.py`(同dir、API 0)→`baseline_gate_r0.json`・`baseline_gate_r2.json`。

## 0. 結論(1段落)
不足の主因は「Personaより先に主張とResearchが決まる設計」と「Prompt/書き換え規則が安全で丁寧な語りだけを通す設計」の組合せ。Cast段階が`中心となる見方`(Research由来のstoryline)と`F番号の事実`を入力に`viewpoint_oneline`(=主張)を同時に作り(後付け)、Card段階で賛否の色を禁止し、Writerは約190字・冒頭は場面・解決策/提案なしで書かされ、Gateの局所書き換えは「調査・統計・制度の説明をしない」で事実を消した。R1/R2は比喩を足しただけで人物差・主観・主張の明確さは変わっていない。最終パートは抽象名詞を連ねた。いずれもコード/Promptの固定文言とTrial実データで裏付けられる(下表)。

## 1. 原因(a)〜(e)+追加(f)〜(h)と証拠
| ID | 原因 | 証拠(ファイル:行・実データ) |
|---|---|---|
| (a) | **Voice Cardが「属性リスト」で、経験・感情・価値観・話し方が主張に接続されていない。さらに主張(見方)が人物より先/同時にResearchから作られた(後付け)** | `er110:225-248`(`build_cast_prompt`)は入力に`中心となる見方: {storyline}`と`F番号の事実`を渡し、同じ1回のcallで`viewpoint_oneline`(主張)と職業ラベルを同時生成させる。実出力`y_cast/cast_candidates.json`: voice_2の`viewpoint_oneline`は「平均のテスト得点がほぼ変わらないという結果も踏まえて、ほかの学習支援より優先する理由を確かめたい」=Research(F2)の言い換えがそのまま主張。voice_1も「点数が上がるかどうかとは分けて」=F1/F2の対置。Card(`er110:250-279`)の7項目は`situation_and_scene/concern/stake/constraint`のみ=年齢以外の経験歴・性格・話し方・感情の癖・価値観の由来が無い。旧Bでも同種の所見: 「Voice Cardが人手作成で品質がCard次第」(`INVENTORY_OLD_B_VOICES_01.md:227`)、「人物でなく抽象的な軸だった」(同:202 F3)。 |
| (a2) | **主張が意図的に「対立しない別論点」にされ、賛否・要求が消えた** | `er110:240`「賛成・反対・中立を機械的に…必要はありません。…実質的に別の論点を中心に」+`:278`Card禁止「賛成・反対の陣営に寄せた書き方をしない」。結果3人の主張は「優先順位」「根拠の説明責任」「ルールづくりへの参加」=いずれも手続き的・慎重で、聞けば一文で言える強い主張(例: 「学校でしまってくれ」「一律禁止は困る」)が無い。ユーザー原文§2「主張が曖昧」と一致。USER_02(§3)の「機械的な賛否割当を避ける」は“割当の機械性”の否定であり、主張の賛否色そのものの禁止ではない。 |
| (b) | **Prompt制約が「安全で丁寧な語り」を誘導する** | `er110:366-367`: Voice「各約190字」(主張+具体論+感情を入れるには短い。実測 voice_1 176/voice_2 202/voice_3 184字、`baseline_gate_r0.json`)、「冒頭の1文で、誰がどんな状況か…具体的な場面から始める」「解決策や提案は語りません」「迷いや複雑な気持ちは書いてかまいません」(迷い許容のみ明示、断言・要求・怒り等の許容は無し)。`:377`数字禁止。`:568`(書き換えPrompt)「調査・統計・制度の説明をしない…解決策・提案は語らない」。実データ: 3Voiceの冒頭が同型「[場所]で、[職業]の私は、[書類/ノート]を[広げ/出し]…」(`gate_r0/article_final.md` 2〜4段落)、「手が止まる」がV2(R0)・V1/V2(R2)に反復、V1/V2/V3が全て「〜んだ」「責任」「余地」で収束。`baseline_gate_r0.json`: 3Voiceの平均文長範囲3.8字(25.1/28.9/26.3)・感情語0〜1/Voice・「だろうか/と思う」型の推量が各段落に存在。 |
| (c) | **Leakage判定+書き換えが事実を消す(M1衝突、OPEN-470)。ただし判定自体は正当で、本質は「事実の入れ方」と「選んだ事実の不自然さ」** | `gate_r0/article_before_judgement1.md`: V1「米国でスマホを鍵のかかる袋にしまう方式を取り入れた学校の研究では、…大きく減ったという」、V2「米国の同じ方式を調べたワーキングペーパーでは、…効果は平均ではほぼなく…という」=**研究が文の主語の報告文**。`leak_check_1.json`: V1 `leak_evidence_subject`+`leak_discovery_syntax` FAIL、V2 4項目FAIL(判定は`er110:454-488`の定義どおり正当)。`er110:568`の書き換え規則「調査・統計・制度の説明をしない」により最終稿(`gate_r0/article_final.md`)では両文が削除され、台帳Factの具体件数=0。さらに**人物と事実が不整合**: 日本の中学国語教員・自治体職員が「米国の…ワーキングペーパー」を語る(`leak_unknowable_analysis`の趣旨に反する)のは、B3が米国NBER論文を中心storylineに選び(`storyline_b3/selected_brief.md`)、Castがそれを背景factに割り当てたため。台帳には日本の事情に接続できる事実がある(JP-01〜03: 文科省2020年通知[高校=校内使用の制限]、OECD-02: 禁止校でも使う生徒がいる、等=`verified_fact_ledger.txt` 13 VERIFIED)が選ばれていない。つまり「Gateが自然な主観発言への事実織込みを妨げた」のではなく、「報告文形式でしか事実が書かれず(Prompt `:360-377`の出典タグ規則が『〜という』の報道文を誘導)、適合しない事実を選び、書き換えが消した」。ただしM1(Voice段落に世界スコープ事実1件まで許容)と書き換え規則(`:568`)とGate定義(`:434-441`)の3者に**設計上の矛盾が実在**(M1は許容、他2つは事実を許さない)。 |
| (d) | **R0→R1→R2が面白さの表層(比喩・導入)だけを足した** | `gate_r2/article_final.md`: リード「カチリと鍵をかける」、V2「財布は打ち出の小づちじゃない」、最終「袋を閉じる、その前に」=比喩の追加。人物の主張は不変(V2は『判断がつかない』、V3は『余地がほしい』)。`baseline_gate_r2.json`: 3Voice平均文長範囲は3.8字でR0と同一、感情語0〜1/Voiceでほぼ変化なし、「手が止まる」が増加。`WRITER_COMPARISON_01.md`/`TRIAL_SUMMARY_01.md §1`の自己評価も「導入・比喩・独白の面白さ」。USER_03 §7が「課題はエンタメ表現の追加ではなくPersona設計と主観的Voice生成」と述べるとおり。 |
| (e) | **最終パートの抽象化(一度聞いて理解しづらい)** | `gate_r0/article_final.md` 5段落「お金の行き先を決める力と、教室を動かす力と、自分の暮らしを保つ責任は、同じものじゃない。しかも、自分で決められる範囲が狭くても、決定の重さを軽くできるとは限らない。守りたいものが切実なほど、決定に関われるわけでもない。誰の納得が、まだ言葉になるのを待っているんだろう。」=抽象名詞(力・責任・決定・納得)の連鎖+二重否定(「〜とは限らない」「〜わけでもない」)。`baseline_gate_r0.json` final: 抽象語率4.13/100字(Voice段落1.1〜2.5)。過去のユーザー実検証でも「Voicesは概ね好評だが、引用後の抽象的なまとめを分かりやすくする余地あり」「数字・複数調査・抽象論の多い記事は音声だけでは理解しづらい」(`docs/pm/delegation_log/PM-USER-VALIDATION-DIRECTION-RECORD-01.md:39,43`、隣接論点の整理=同:80、該当segment=Tension/Closing)。USER_03 §6も同趣旨。DP02の最終パート規則「各人物の再要約・発言の再掲をしない」(`DESIGN_PROPOSAL_02.md:196`)が、具体的に名指しで違いを整理することを妨げ、抽象化に向かわせた疑い。 |
| (f) | **生徒(未成年)当事者が構造的に排除された** | `er110:242`「子ども・未成年の本人は避け、20代以上の人物」(声がAlgieba/Zephyr/Schedar=成人TTSのための設計者判断。ユーザー決定ではない)。結果、主要当事者の生徒・保護者が消え「30代の定時制生徒」「予算査定職員」が残った(`voice_cards.json`)。USER_03 §3「教師・親・生徒などの主要当事者を検討」を満たさない。親は候補にも上がらなかった(`TRIAL_SUMMARY_01.md §2`の所見)。 |
| (g) | **同型の場面テンプレートが人物差を消した** | Cardの`situation_and_scene`が3人とも「机/教卓/ノートに資料を広げ印・付箋を付ける」(`voice_cards.json`)。TRIAL_SUMMARY §2も「書類を前に手を止めて考える大人の同型」と自己所見。人物の差が職業名だけになり、生活・感情・口調の差がPromptにもCardにも無い。 |
| (h) | **対策弱化アーム(A0)でも優等生化は解消せず、別の問題(解説者化・創作)が出た** | `ablation_a0_light/r0_final.md`: 冒頭リードに米国論文の説明が入り、3人とも「この結果を、三人が別々の机で読んでいる」と研究結果への反応を語る(Research起点の人物=原因(a)の再現)。つまり「Gateを弱めれば人物が自由になる」わけではなく、**人物がResearchに従属した設計のまま**だと、制約を外しても解説者になる。→ 対策は「制約の緩和」ではなく「Persona起点への工程反転」と「事実の人物内での扱い方の設計」。 |

## 2. 因果の要約(Persona→Voice が逆になっていた箇所)
旧工程: Research → B3(storyline=研究結果) → Cast(立場+主張+事実割当を同時生成) → Card(属性7項目) → Writer(5段落契約・約190字) → Leakage/書き換え(事実を削除) → R1/R2(比喩追加)。
問題点: 主張の起点がResearchとstorylineで、Personaは「異なる論点を運ぶ器」になっている(後付け)。新工程は DESIGN_PROPOSAL_03 §1。

## 3. 設計の旧規則と今回の改善の関係(撤去・変更対象の洗い出し。詳細はSPEC_MAPPING_01.md)
`er110:240,242,278,366-367,377,568`の固定文言と`:434-441`のGate定義が改善対象。いずれも未承認のTrial設計(DESIGN_PROPOSAL_02由来)で、承認済みProduction仕様(X/Z/B)ではない。旧Bの承認済みAnalytical Leakage Check項目(7+6項目)は維持する(DESIGN_PROPOSAL_03 §5)。

## 4. 限界(事実と所見の区別)
- n=1テーマ・1回のR0/R1/R2。上記は実測の事実と、コード/データから読める因果の所見であり、統計的な確証ではない。
- 指標(抽象語率・感情語)は素案の語彙リストによる簡易値で判定器ではない(`persona_metrics_probe_01.py`)。
- Phase Aでは再現のための再実行は行っていない(API 0)。反証の機会はPhase Bの新設計R0で得る(DESIGN_PROPOSAL_03 §7)。
