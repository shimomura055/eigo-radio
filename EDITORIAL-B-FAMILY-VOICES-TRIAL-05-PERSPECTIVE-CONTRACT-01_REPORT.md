# EDITORIAL-B-FAMILY-VOICES-TRIAL-05-PERSPECTIVE-CONTRACT-01 報告書

Lane: Lane B / Voices-Perspective(新管理ID)。Lane A(OPEN-112/OPEN-117/ER-011系、
docs/pm/*、er011_*、er006_*、er003_*Production等)には一切触れていない。
書き込みは `er012_editorial_b_voices_trial_05.py`(新規、Trial-04スクリプトを
土台にコピー、Trial-04本体は無変更)、`er012_output/editorial_b_voices_trial_05/`、
本Reportのみ。Production Prompt/コード変更なし。3+ Voices・A2/TTS/Assembly・
11-part対応・B Family Production正式採用は一切行っていない。

## 0. Closeout分類案

**USER_DECISION_REQUIRED**(REJECTEDでもVALIDATEDでもない)。

理由の要旨(詳細は§7・§11):
- 新しい生成方式(Perspective Map→Voice Cards→Diversity Check→Writer→
  Analytical Leakage Check)は、Trial-04で最も深刻だった失敗モード
  (複数の数字が調査報告調で連続する"reported"/"showed the same pattern"
  文)を、Voice B(ワークプレイス戦略責任者)については**3 attempts全てで
  完全に回避**した(leak_evidence_subject・leak_numbers_foregroundが
  3/3 PASS)。これは新方式(Supporting evidenceの隔離)が機能した明確な
  証拠である。
- 一方、Analytical Leakage Checkは**3 attempts全てでflagged**のまま
  MAX_WRITER_ATTEMPTS(3)に到達した。残った問題は主にleak_narrator_
  analysis/leak_unknowable_analysis(語り手がVoiceの人物を外側から要約・
  解釈する文)であり、これは6 Voice-instance中6件(2 Voice×3 attempts)で
  一貫して検出された、最も頑健な残存失敗モードである。
- **新規発見(§9・§11)**: Production既存機構のEvidence Compression
  Editor(無変更のまま適用)が、少なくとも2/3 attemptsで、Writerの生の
  出力(`pre_editor_article.md`)には無かった分析的な語り手要約文
  ("she must reckon with a broader workplace reality")を**新たに挿入**、
  および実在の人物名(Linda Foggie)を匿名化して受動態("The change was
  described as...")へ変換する編集を行っており、これがLeakage Checkの
  flagged判定に直接寄与していた可能性が高い。Evidence Compression Editor
  はProduction既存機構でありこのTrialの変更対象外のため、対策は提案の
  みに留める(§11)。
このように、Perspective選定・Voice Card設計・Evidence隔離という新方式の
中核要素は部分的に強く検証された一方、Analytical Leakage Checkが完全な
PASSへ到達しておらず、かつ原因の一部が本Trial範囲外のProduction機構との
相互作用にあるため、単純なVALIDATED/REJECTEDでは判定を誤らせると考え、
USER_DECISION_REQUIREDとする。最終判定はFableに委ねる。

---

## 1. Voices Editorial Contract(原文)

タスク文書(ACTIVE_TASK.md相当の指示)で与えられたセクションAをそのまま
Contractとして採用した(本Trialでの新規文章化ではなく、指示文書の原文を
正本として扱う)。要旨:

- **真似するもの**: 人から始まる/同じIssueを異なる人の内側から見る/Voice
  sectionではその人が何を見て・何に困り・何を守りたいかを書く/Research・
  EvidenceはそのPerspectiveが実在することを裏で支える/Evidenceを主人公に
  しない/Tensionで初めて複数Voiceを並べ、違いの意味を考える/Closingは
  単純要約でなく一段深い理解/Narratorが早い段階で結論・分析を説明しすぎ
  ない/Light・conversational・human-centered/「分析レポート」でなく
  「人の見方を知る記事」。中心原則: **"Research is backstage. People are
  on stage."**
- **真似しないもの**: Voice数/文数/語数/固定フレーズ/"Imagine"等のHook
  表現/Café・Remote Work固有の展開/見出しの完全固定/Reference記事の文章
  模倣。

**注記(調査の限界)**: リポジトリ内を検索したが、Reference Example 1
(カフェ)・Reference Example 2(リモートワーク)の記事全文は見つからなかった
(`EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`に、両記事の構造・一部の
引用フレーズ("コーヒー1杯の対価に何が含まれるか"「remote versus office
が間違った出発点かもしれない」等)のみが分析結果として記録されている)。
本Trialは、この既存分析結果とタスク文書自身のContract記述を正本として
用いており、Reference Example全文との直接比較(§11相当の詳細比較)は行って
いない。これは新規のUSER_DECISION_REQUIRED事項ではなく、既存資料の制約
として記録するのみである。

---

## 2. Research(再利用/追加)

新規Perplexity呼び出しは行っていない。EDITORIAL-B-FAMILY-VOICES-TRIAL-04で
実施済みのStage 1B/2B追加Research(14 fact、13件CONFIRMED・1件PARTIALLY_
CONFIRMED)を、`er012_output/editorial_b_voices_trial_04/research/`配下
(無変更のTrial-04資産)からそのまま再利用した。Trial-04の
`perspective_candidates.json`(候補A〜E)を土台に、本Trial側で
`er012_output/editorial_b_voices_trial_05/research/perspective_map.md`
として作業記録を作り直した。

---

## 3. Perspective Map(候補全件)

候補A(週の大半をオフィスで働き自分の場所を必要とする社員)、候補B(気分・
業務に応じて座席を自由に選びたい社員)、候補C(ワークプレイス戦略責任者、
実名の発言例Linda Foggie氏)、候補D(新人教育マネージャー、Evidence不足で
不採用、Trial-04から変更なし)、候補E(ファシリティ担当者、候補Cへ統合、
Trial-04から変更なし)。各候補についてWho/Situation/Protect/Difficulty/
Notice/Responsibility/Concrete scene/Research evidenceを整理した全文は
`er012_output/editorial_b_voices_trial_05/research/perspective_map.md`
参照。想像で埋めた項目はなく、根拠なしの項目は「(根拠なし)」と明記した
(候補A・Bの responsibility 欄等)。

---

## 4. Diversity Check(判定と根拠)

判定基準: "Are these two people different only because they prefer
different outcomes?"

- **候補A vs 候補B(Trial-04の組み合わせ)**: 双方とも座席運用の意思決定権
  を持たない個人であり、responsibility欄は双方とも根拠なし。差は「一貫性・
  所属感を求める」か「自由・変化を求める」かという、同一次元(個人の心理的
  好み)内の対称的な違いに近い。**YESに近いと判定し、Trial-05では不採用**。
- **候補A vs 候補C(Trial-05で採用)**: 候補Aは個人としての日々の感覚
  (所属感・集中)。候補Cは、経営層へのコスト説明責任と全社員への責任を
  組織全体の立場から負う。(1)責任の有無、(2)リスクの種類(個人の快適さ vs
  コスト超過・組織的信頼)、(3)「良い座席運用」の定義そのもの(個人の
  日々の感覚 vs 全社的な持続可能性)、の3点で構造的に異なる。**YESと
  判定し、VOICE_A=候補A、VOICE_B=候補C を採用**。

判定の全文・不採用理由は `research/perspective_map.md` §Perspective
Diversity Check、および `research/verified_fact_ledger.txt` 冒頭に記録。

---

## 5. Voice Cards(採用2件、Supporting evidence別枠)

Voice Cardの正本は `er012_editorial_b_voices_trial_05.py` の
`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK` 内(Writerへ実際に渡した内容)。
要旨:

**Voice Card 1(VOICE_A、社員)**: Person=週の大半をオフィスで働く社員。
Situation=毎朝、空いている机を探す。Need=探さずに座れる決まった居場所。
Concern=衛生面の不安・私物の置き場・居場所の欠如。Protect=所属感と集中。
Constraint=座席運用の決定権なし。Concrete scene=毎朝机を探して座る(A-02/
A-05根拠)。Supporting evidence(別枠)=Gensler 87/74%・80/67%[A-01]、
Forbes"impersonal/disorienting"[A-03]、Oselandコメント[A-04]、ITmedia
36.8%[A-06]。

**Voice Card 2(VOICE_B、ワークプレイス戦略責任者)**: Person=会社全体の
座席運用を決める職務(実名例Linda Foggie氏、Scotiabank Global Head of
Real Estate & Corporate Services)。Situation=ハイブリッド勤務で多くの席
が空く一方、社員は所属感を求める。Need=コストと所属感の両立。Concern=
フレックス席拡大による所属感の毀損 vs 固定席拡大によるコスト増、どちらへ
寄せても責任を問われる。Protect=組織全体の持続可能性と社員の所属感の両立。
Constraint=経営層への説明責任、全社員への責任。Concrete scene="静かに、
固定席が増えフレックス席が減る方向へのシフトが起きている"という発言
[B-01/fact_005]。Supporting evidence(別枠)=CBRE 83%→55%[B-02/fact_011]、
Desking.appコンサルタントの中間解提案[B-03/fact_010]。

---

## 6. Writer入力の構成(Voice Cardをどう渡したか、Ledgerの位置)

Production Writer本体(`er003_v1_n3_01_articles_generate.py`の
`COMMON_BLOCK_TEMPLATE`)は無変更。既存のANCHOR挿入方式(Trial-04と同一
手法)で `B_FAMILY_VOICES_FOCUS_MODULE_BLOCK` をANCHOR(`【Spoken-first
原則(数字の扱い)】`)の直前へ挿入した。`COMMON_BLOCK_TEMPLATE`内では
`{verified_ledger_text}`(Verified Fact Ledger本体)はANCHORより**後**に
配置されているため、ANCHOR位置へVoice Cardを挿入するだけで、Writerが
読む順序として「Voice Card(人物本体)→(その後にVerified Fact Ledger
本体)」を実現できた。挿入位置の変更・Production側テンプレートの並び替え
は一切行っていない(`run_phase_a()`の`clean_single_insert_confirmed=True`
で実測確認済み、`er012_output/editorial_b_voices_trial_05/audit/
phase_a_result.json`)。Voice Card内では、各Voiceについて
「Supporting evidence(裏付け専用、Voice本文の主役にしない)」という節を
明示的に分離し、「Voice Cardの内容を経由せず、Verified Fact Ledgerの
記述(出典名・数字の列挙)から直接Voiceの文章を組み立てること」を禁止
事項として明記した。

---

## 7. Analytical Leakage Check結果(検出・rewrite回数・引用)

MAX_WRITER_ATTEMPTS=3(初回+是正再実行最大2回)。**3 attempts全てで
any_flagged=True**、上限に到達し、attempt3を最終結果として採用した
(`er012_output/editorial_b_voices_trial_05/trial05_summary.json`
`attempt_history`)。

| attempt | Voice A fail_fields | Voice B fail_fields |
|---|---|---|
| 1 | narrator_analysis, unknowable_analysis, discovery_syntax | narrator_analysis, unknowable_analysis |
| 2 | evidence_subject, narrator_analysis, unknowable_analysis, discovery_syntax, evidence_memorable | narrator_analysis, unknowable_analysis |
| 3 | evidence_subject, numbers_foreground, narrator_analysis, unknowable_analysis, discovery_syntax | narrator_analysis, unknowable_analysis, discovery_syntax |

**重要な観察**: Voice B(ワークプレイス戦略責任者)は、`leak_evidence_
subject`と`leak_numbers_foreground`について**3/3 attempts全てPASS**
だった(調査主語文・複数数字の前面化が一度も発生しなかった)。これは
Supporting evidence隔離の効果が最も明確に出た箇所である。一方Voice A
(社員)は、attempt2・3で`leak_evidence_subject`が再発した(例:
attempt3 "For about 37 percent of people using hot desks, the seat
tended to become fixed anyway."、原資料はA-06/fact_009の36.8%)。
Voice AのSupporting evidence欄には4件の数字付きfactがあり、Voice Bの
Supporting evidence欄には数字付きfactが1件(fact_011)のみだったことが、
この差の一因である可能性がある(§11で考察)。

`leak_narrator_analysis`/`leak_unknowable_analysis`は、**6 Voice-instance
中6件全てでFAIL**した最も頑健な残存失敗モードである。典型的な検出文:
"The need is a stable start, with enough continuity to focus and feel
included."(attempt1 Voice A)、"She is protecting company resources and
people's sense of place."(attempt1 Voice B)、"This person must explain
space costs to senior leaders..."(attempt3 Voice B)。

is_flagged後、記事本文は手で書き換えず、`build_leakage_corrective_note()`
が生成した引用付き是正メモをprompt末尾へ追加してWriterをフル再実行した
(Fact Checker/Ledger Deviation Checker/Local Rewrite/Directional Fact
Precheckを含む完全なパイプラインを毎回やり直した)。詳細は各attemptの
`analytical_leakage_check_attempt{N}.json`、是正メモは
`b1b_run01_attempt{2,3}/audit/candidate_prompt_used.txt`末尾を参照。

---

## 8. 最終記事全文(原文・無編集)と`pre_editor_article.md`との差分

最終結果(attempt3、`er012_output/editorial_b_voices_trial_05/
b1b_run01_attempt3/article.md`)全文:

```markdown
# Who Owns a Seat at Work?

## The Question

Each morning, an employee walks into the office and looks for an empty desk. The chair may be different from yesterday, and the keyboard may have been used by someone else. Papers and personal things have nowhere to stay.

Some companies are bringing back assigned desks. Others are keeping shared seating. The question is not simply which system is better. It is why the same office can feel completely different, depending on who is looking at it.

### One Voice: The employee looking for a place

Every morning, the first job is to find an empty desk. Yesterday, someone else may have used the keyboard. There is no drawer or corner for papers and personal things. The worker has to choose a place before starting work.

A familiar desk would offer the same view, the same setup, and a calmer start. The need is not simply a love of furniture. It is a wish to keep personal space, focus, and a sense of belonging.

For about 37 percent of people using hot desks, the seat tended to become fixed anyway. So even when every desk is open, some workers may keep returning to the same workable place.

### Another Voice: The person responsible for the whole office

On another part of the office floor, a workplace leader has to look at the whole space. On some days, many desks are empty. At the same time, people who come in still want to feel that they have a place with their team.

This person must explain space costs to senior leaders while also taking seriously the need for continuity and connection. The change was described as "a slow, quiet shift" toward more assigned seats and fewer flex seats.

But this is not a simple return to the past. The decision must cover people who come in often, people who come in sometimes, and teams that work in different ways. Too much unused space raises one problem. Too much flexibility may weaken belonging. The responsibility is to protect both.

## Why They See It Differently

The two views sound different because they measure success in different ways. The employee feels the policy in minutes: Can I sit down, put my things somewhere, and focus? The workplace strategist sees a larger map: How much space is being paid for, how often is it used, and can people with different schedules still feel connected?

The share of companies using assigned seating fell from 83 percent to 55 percent by 2024, while workplace staff still faced many empty desks. A useful test is not only how many desks are available, but whether people keep recreating the same seat and carrying the daily work of organizing their workspace. This helps explain interest in team-based middle grounds.

## What This Tells Us

Before these voices, fixed seating and hot desking can look like a battle over personal preference. After them, the question changes. An office must work for the employee who needs a dependable place to begin and for the person responsible for making the whole space sustainable. The real disagreement is about what the office should provide—and for whom.
```

**`pre_editor_article.md`(Evidence Compression Editor適用前、Writer生の
出力)との差分**(`diff pre_editor_article.md article.md`実測):

1. `36.8 percent` → `about 37 percent`(丸め。Evidence Compression Block
   の既定ルールの範囲内)。
2. `Linda Foggie has to look at the whole space` → `a workplace leader
   has to look at the whole space`(**実在の人物名を匿名化**)。
3. `She must explain space costs... Foggie described the change as
   "a slow, quiet shift"...`(能動態、人物が主語)→ `This person must
   explain space costs... The change was described as "a slow, quiet
   shift"...`(**受動態化・"This person"への置換**)。
4. `Her decision must cover...Her responsibility is to protect both.`
   → `The decision must cover...The responsibility is to protect
   both.`(**所有格代名詞の除去、抽象名詞化**)。

この4点のうち2〜4は、Analytical Leakage Checkが検出した
`leak_narrator_analysis`/`leak_unknowable_analysis`の該当引用
("This person must explain...", "The responsibility is to protect
both.")と直接一致する。すなわち、**Writerが生成した時点(pre_editor)
ではLinda Foggieという実在の人物が主語のまま能動態で書かれていたのに、
Evidence Compression Editor(Production既存機構、無変更で適用)が
匿名化・受動態化する編集を行った結果として、語り手が人物を外側から
要約する文体が強まった**可能性が高い(§9で他attemptとの比較を含めて
詳述)。

---

## 9. 技術結果(Fact Safety/Precheck/Point QA monitoring/語数/cost)

- **Fact Checker**(attempt3): verdict=**REVIEW_REQUIRED**(non-blocking、
  既存policy通り)。contradictions=0件。unsupported_specific_claims 5件、
  うち3件は「独立web検索では原資料と完全一致する数値を再発見できなかった」
  という既知のパターン(例: 36.8%[A-06/fact_009]について、Fact Checkerの
  独立検索は別の調査[42%/63%等]を発見し、記事の"37 percent"と直接一致
  しないと指摘。Ledger自体には36.8%としてCONFIRMED記録済み)。1件は
  Linda Foggie氏の責任範囲に関する記述がinterpretiveと指摘(Voice Card
  のconstraint欄からの妥当な敷衍だが直接引用ではない)。attempt1・2も
  同様にREVIEW_REQUIRED(いずれもFAILなし)。
- **Ledger Deviation Checker**: 3 attempts全て**overall_status=
  LEDGER_COMPLIANT**。attempt2でMINOR 2件(Hook/導入部の頻度表現に関する
  軽微な指摘)、attempt1・3は0件。Local Rewrite発火なし(MAJORなし)。
- **Directional Fact Precheck**(attempt3): overall_status=
  **DIRECTION_REVIEW_REQUIRED**(non-blocking)。2件中1件はconflictsなし
  のMATCH(83%→55%の低下方向は一致)、もう1件は「Ledger側の文が断片化
  されており機械的に方向判定できない」という既知の限界によるレビュー要求
  (矛盾を検出したわけではない)。
- **Point Overlap QA(monitoring、5区切り専用parser経由)**: 3 attempts
  全てlexical_flagged=False。
- **Point Value QA(monitoring)**: 3 attempts全てvalue_qa_flagged=False。
- **語数**(5区切り実測、`five_section_length_report.json`): attempt1=
  454語、attempt2=442語、attempt3(最終)=490語(Hook 77・Voice A 110・
  Voice B 130・Tension 114・Closing 59)。目安350〜420語をやや超過して
  いるが、hard/soft gateなしのため許容。
- **Cost**: OpenAI(gpt-5.6-luna、Point Role Planning・Writer・Evidence
  Compression・Point Value QA・Analytical Leakage Check・Fact Checker
  [web_search計27回、3 attempts合算]・Ledger Deviation Check、計24 call、
  `raw_usage_log_trial05_writer.jsonl`実測)input 367,435 tokens・output
  74,604 tokens・cached 20,334 tokens、pricing_snapshot.json単価(input
  $0.20/1M、output $1.20/1M、cached $0.02/1M、web_search $10/1,000call)
  で概算**約$0.43(¥500を大幅に下回る)**。新規Perplexity呼び出しは
  ゼロ(Research再利用のため)。TTSは実行していない。Cost超過による
  STOPには該当しない。

---

## 10. 受入条件12項目セルフチェック(根拠引用、最終判定はFable)

1. **2 Voicesが単なるPreference A/Bでなく意味の異なるPerspective**:
   達成。VOICE_A(個人の日々の感覚)とVOICE_B(組織的責任)は、
   responsibility・risk・definition of what mattersの3点で構造的に
   異なる(§4)。
2. **PerspectiveがResearchから選ばれている**: 達成。全てTrial-04の
   CONFIRMED fact(fact_005・fact_011・fact_010・fact_001・fact_003・
   fact_004・fact_006・fact_007・fact_009)に根拠を持つ(§3・§5)。
3. **Voice sectionの主人公が人**: 部分的に達成。Voice Bはattempt3で
   実在の人物名が匿名化される編集を受けたが(§8)、それでも文法上の
   主語は一貫して人(the worker/she/this person)であり、
   survey/company/dataが主語になった文は稀(§7参照、Voice Bは3/3
   attempts leak_evidence_subject PASS)。
4. **survey/data/percentageが主人公になっていない**: Voice Bは
   3/3 attempts達成。Voice Aは1/3 attempts(attempt1)で達成、
   attempt2・3で1文だけ再発(§7)。
5. **Discovery型の調査結果説明へ戻っていない**: 部分的。
   leak_discovery_syntaxはVoice Aで3/3、Voice Bで1/3(attempt3)FAIL。
   ただしTrial-04で問題視された「複数数字の連続比較」("87%/74%・
   80%/67%・37%"のような)は今回一度も再現しなかった(各Voice最大1つの
   数字ルールは実測上守られていた)。
6. **Evidenceは裏付けとして保持され前面に出すぎない**: Voice Bは達成、
   Voice Aは一部未達(§7)。
7. **HookがTrend summaryでなく人・場面・問いから入る**: 達成。3
   attempts全てのHookが「Each morning, an employee/office worker...」
   という具体的情景描写から始まり、企業名・統計・パーセントを含まない
   (§8本文参照)。
8. **Tensionが独立しPerspective差の根本理由を説明**: 達成。3 attempts
   全てで独立した`## Why They See It Differently`セクションを持ち、
   「個人が毎日感じるものさし」対「組織全体を測るものさし」という
   構造的な違いを言語化している(§8)。
9. **Closingが一段深い理解**: 達成。「Before these voices...After
   them...」という形式で、単純要約でなく視点の変化を描いている(§8)。
10. **Light/conversational/human-centered**: 概ね達成。ただし
    leak_narrator_analysisが指摘する通り、一部で語り手による要約文が
    トーンをやや硬くしている(§7)。
11. **Reference Example 2本と並べて表面コピーでなく同じEditorial
    mechanismを感じる**: **判定保留**。§1の通り、Reference Example
    全文がリポジトリ内に見つからず、既存分析結果(構造・一部引用)との
    比較にとどまる。5区切り構造・Tension/Closingの役割は
    `EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`の分析と整合的だが、
    厳密な並置比較はできていない。
12. **Fact Safety/Ledger/provenanceを崩していない**: 達成。3 attempts
    全てLEDGER_COMPLIANT、Fact CheckerもFAILなし(§9)。

---

## 11. Trial-04 run04との比較表

| 観点 | Trial-04 run04 | Trial-05(最終、attempt3) |
|---|---|---|
| Discovery感(調査報告調文の有無) | Voice Aで複数数字が連続("87%/74%・80%/67%・37%"、"reported"/"showed the same pattern") | Voice Bは3/3で完全回避。Voice Aは1/3のみ完全回避、残りは1文単位の再発(複数数字の連続は再現せず) |
| 人の存在感 | Voice B(自由に選びたい社員)は個人の好みとして描かれるにとどまる | Voice B(ワークプレイス戦略責任者)は組織的責任を負う人物として描かれるが、attempt3でEvidence Compression Editorにより実名が匿名化され受動態化(§8) |
| Evidenceの前面度 | Voice Aで数字が前面化 | Voice Bで大幅改善(3/3 PASS)、Voice Aは一部改善(1/3 PASS) |
| Perspective diversity | 個人の好み対個人の好み(所属感 vs 自由) | 個人の経験対組織的責任(§4のDiversity Check根拠あり) |
| Narrator分析量 | 明示的なチェック機構なし(目視評価のみ) | Analytical Leakage Checkで定量的に検出。leak_narrator_analysis/unknowable_analysisが6/6 Voice-instanceでFAIL(新たに発見された残存課題) |
| Tensionの深さ | 「良い座席運用とは何かの測定基準の違い」を扱うが個人対個人 | 「個人が毎日感じるものさし」対「組織全体を測るものさし」という、より構造的な対比 |
| Reference ExampleとのFamily similarity | 5区切り構造はFableにより強い方向性と評価済み | 同じ5区切り構造を維持、adapter・parserはTrial-04から無変更で再利用 |

**総合**: 新記事単体を「良くなった」と単純評価はしない。Trial-04で最も
深刻だった「複数数字が調査報告調で連続する」失敗モードは、特にVoice B
で構造的に解消された。一方、Trial-04では言語化されていなかった、より
微妙な失敗モード(語り手による人物の外側からの要約)が、Analytical
Leakage Checkという新しい検出機構によって初めて可視化された。これは
「後退」ではなく「これまで見えていなかった問題が見えるようになった」
と解釈する方が正確である。

---

## 12. 未処理のUSER_DECISION_REQUIRED・新規仕様候補・APPROVED未配線項目の一覧(Lane B分)

- **新規発見(このTrialで判明)**: Evidence Compression Editor(Production
  既存機構、`er003_v1_n3_01_evidence_compression_editor.py`、無変更)が、
  Voices型記事において実在の人物名を匿名化・受動態化する編集を行い、
  Analytical Leakage Checkの`leak_narrator_analysis`判定に影響している
  可能性がある(§8・§9)。**対策は提案のみ**(実装はこのTrialの範囲外):
  Voices型記事では「実在の人物として特定されている固有名詞(組織名では
  なく人物名)は匿名化対象から除外する」という例外ルールをEvidence
  Compression Block(またはVoices専用の派生ブロック)へ追加することを
  今後検討候補として記録する。ユーザー承認なしに実装しない。
- Analytical Leakage Checkの許容基準(何件までのFAILならVALIDATED
  相当とするか)は、本Trialでは定義しておらず、**ユーザー判断が必要**。
- 5区切り構造自体は、Trial-04に続き本Trialでも安定して機能したが、
  Production正式採用は引き続き未決定(§13)。
- Voice Card + Evidence隔離という生成方式そのものの正式採用も未決定。
- Trial-03/04から継続するUSER_DECISION_REQUIRED(B Family Production
  設計、Voice数3以上への拡張要否等)は、本Trailでは一切変更していない。

---

## 13. SSOT登録案

以下は、後続タスクでのSSOT反映(`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`等)を目的とした登録案テキストであり、本Trialでは登録
していない(Lane A作業として別途行う)。

> **EDITORIAL-B-FAMILY-VOICES-TRIAL-05-PERSPECTIVE-CONTRACT-01**
> (2026-09-06): Trial-04で指摘された「Voice sectionがDiscovery型の
> 調査報告調に戻る」問題に対し、生成方式自体を再設計するTrial
> (Perspective Map→Voice Cards→Diversity Check→Writer→Analytical
> Leakage Check)を実施した。Status: **USER_DECISION_REQUIRED**
> (VALIDATEDでもREJECTEDでもない)。Perspective Diversity Check・
> Voice Card + Evidence隔離という中核設計は、特にEvidenceが数字に
> 富むVoice(ワークプレイス戦略責任者)で数値前面化を完全に防ぐという
> 明確な効果を示したが、Analytical Leakage Check(新規Trial限定機構)
> は3 attempts全てでflaggedのまま上限に到達し、語り手による人物の
> 外側からの要約(leak_narrator_analysis/unknowable_analysis)という
> 新しい失敗モードを可視化した。この一部はProduction既存のEvidence
> Compression Editorが実在人物名を匿名化・受動態化する編集と相関して
> いる可能性がある(未確認の仮説、対策は提案のみ、実装なし)。5-part
> structure(Hook/One Voice/Another Voice/Tension/Closing)は
> Trial-04に続き本Trialでも安定動作し、引き続き強い方向性の候補。
> Voices Editorial Design全体・Voice Card生成方式・B Family Production
> 採用は、いずれもAPPROVED_FOR_PRODUCTIONではない。次の判断が必要:
> (1) Analytical Leakage Checkの許容基準の定義、(2) Evidence
> Compression Editorの匿名化ルールにVoices向け例外を設けるかの検討、
> (3) 生成方式(Voice Card+Leakage Check)自体を次のTrialで継続改善
> するか、現状で一定の限界を認めてstopするか。
