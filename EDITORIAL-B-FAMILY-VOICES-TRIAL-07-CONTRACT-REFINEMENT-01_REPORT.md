# EDITORIAL-B-FAMILY-VOICES-TRIAL-07-CONTRACT-REFINEMENT-01 Report

Lane: Lane B / Voices-Perspective。Trial(隔離)。Production未採用。
書き込み: `er012_editorial_b_voices_trial_07.py`(root、Trial-06 scriptを
コピー、Trial-06本体は無変更)、`er012_output/editorial_b_voices_trial_07/`。
Git操作なし(Fableが統合)。

---

## 0. Closeout分類案

**VALIDATED(仕様候補として有効性を確認、Production採用は別途USER_DECISION_REQUIRED)**。

理由: Contractへ織り込んだ3点(Tensionの役割・Closingの役割・Compactness)の
うち、Tension/Closingの2点は実記事(attempt1・attempt2とも)で狙いどおり
機能したことをAnalytical Leakage Check(本Trialで拡張)・原文引用で確認した。
Compactness(約350語soft target)は、最終採用attempt(453語)ではTrial-06
(419語)より**長くなり**、狙いどおりには機能しなかった。これは仕様自体の
欠陥というより、Leakage是正の再生成ループが語数目標を再強化しない設計上の
穴(§7・§11で開示)によるものと判定するが、「Compactnessは常に効く」という
主張はできないため、REJECTEDではなくVALIDATED(条件付き・改善余地あり)と
する。Production採用可否は人間ユーザー判断(USER_DECISION_REQUIRED、§12)。

---

## 1. 更新後Trial用Voices Editorial Contract全文(統合形、差分付き)

`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`全文は
`er012_output/editorial_b_voices_trial_07/audit/phase_a_b_family_voices_focus_module_block.txt`
(19,112字のcandidate_template中に単一ANCHOR挿入で組み込み済み、
`phase_a_result.json`で`clean_single_insert_confirmed: true`を確認)。
Trial-06版との全文diffは
`er012_output/editorial_b_voices_trial_06/audit/phase_a_b_family_voices_focus_module_block.txt`
との`diff`で再現可能。要旨(3点、既存原則と統合する形で追記。単独ルール化
していない):

**A. Tensionの役割(既存原則"Research is backstage. People are on stage."を
Tensionにも明示適用)**: 「Tensionの中心は、あくまでVoice Cardに描かれている
2人の人物であり、Evidence(survey/research/data/percentage)ではありません」
「"A survey found...", "The data show..."のような…調査・データそのものを
主語にした文で始めたり、その説明へ立ち戻ったりしないでください」を追加。
掘り下げ軸を「経験/優先するもの・守るもの/問題の定義/「良い状態」の定義」の
4種として明示。EvidenceはFact Safety用の裏付けとして保持するが本文の主語に
しない、と明記。

**B. Closingの役割**: 「「固定席派にも自由席派にも良い点がある」「人によって
違う」というだけの結び方で終わらせないでください」「目指すのは、この問題が
実は何についての問題なのかを一段深く見せることです」を追加。表面的対立軸の
組み替えは「可能であれば」「Voice CardとTensionの内容から自然に導かれる」
形とし、**どの抽象軸に組み替えるべきかを先に決め打ちしない**ことを明記
(タスク指示通り)。解決策提案の禁止をClosingにも明示拡張。

**C. Compactness**: 「約350語をsoft targetとしてください(hard capでは
ありません)」「短くすること自体を目的にしないでください」と明記し、削る
対象を「重複説明・Narrator分析・余分なResearch説明・同義の言い換え・不要な
導入文」に限定。禁止事項リストへ「350語ちょうどへ合わせるために…質を犠牲に
した短縮は禁止」を追加(旧Trial-06の「350〜420語」レンジ目安をsoft target
350語へ変更)。

---

## 2. Perspective/Voice Card(再利用分と変更点)

Perspective(固定席を好む社員 vs 自由席を好む社員、主要意見優先の選定基準)・
Voice Card 1/2・Diversity Check根拠は、`research/perspective_map.md`・
`research/verified_fact_ledger.txt`ともTrial-06資産をファイル単位でそのまま
コピーし、**無変更で再利用**した(本Trialのスコープは生成仕様[Focus Module
Block]のみで、Perspective選定ロジック自体は対象外)。

---

## 3. 最終記事全文(原文・無編集)+ pre_editor_article.md差分

採用: `er012_output/editorial_b_voices_trial_07/b1b_run01_attempt2/article.md`
(Analytical Leakage Check flagged項目なし、2 attempts目で確定)。

```markdown
# The Office Desk Divide: A Home Base or a Choice?

## The Question

Every morning, one employee enters the office and looks for an empty desk. Another scans the room for a quiet corner or a place near other people. They may share the same office, yet the desk system can feel very different to each of them. As some companies bring back assigned seats while others keep shared desks, what makes a workplace feel workable?

### One Voice: The search for a home base

Every morning, I get to the office and look for an empty desk. I may sit at a keyboard someone else used yesterday. Before work begins, I am already thinking about cleanliness, my bag, and where to put my papers.

A familiar fixed seat can provide a consistent place to begin work. That routine let me start without searching. Now the people beside me and the desk may change each day. I keep thinking, "I have no personal seat, so I cannot settle down."

A fixed seat is not just ownership. It is a quiet home base. It gives me a familiar place to begin work and a feeling that I belong there.

### Another Voice: The freedom to move

One day, I choose a quiet corner. Another day, I want a livelier place where I can talk with people from another team. If I need distance from an awkward relationship, moving to another desk gives me room.

I like choosing a place that fits my mood and task. Working from home has already given me a personal place to focus, so the office does not need to feel the same every day.

A different seat can bring a new conversation or a new pace. I want choice, not another problem to solve. Staying in one place all day can feel more limiting than freeing.

## Why They See It Differently

These two workers are not really answering the same question. The first asks, "Where can I return to each morning?" The second asks, "What kind of place do I need today?"

One feels secure when the surroundings stay familiar. The other feels secure when movement remains possible. Even for the second worker, choice must be easy and useful. If finding a desk becomes the first problem each morning, freedom can start to feel like work.

The same office can therefore look like a home base to one person and a set of useful choices to another.

## What This Tells Us

The desk debate is not only about where furniture goes. It is about how people find a workable place in a shared office.

For some, that place is built through continuity: the same desk, drawer, and view. For others, it is built through choice: the freedom to move toward focus, conversation, or distance. The deeper question is not simply fixed or free. It is what makes a worker feel ready to work and able to belong.
```

**pre_editor_article.mdとの差分**(Evidence Compression Editor、Production
無変更): 語数456→453(3語減)。実質的な変更は語句レベルのみ("A familiar
fixed seat can provide"←"I used to have"、"One day"←"On one day"等)で、
主語の入れ替え・削除・意味変化はない。全差分:
`er012_output/editorial_b_voices_trial_07/b1b_run01_attempt2/audit/pre_editor_article.md`
と`article.md`の`diff`(6箇所、いずれも軽微な言い回し調整)。Trial-06 Phase B/C
の結論(Editorは劣化させていない)と整合。

---

## 4. Trial-06から何を削ったか(削除・圧縮した要素の一覧)

- Tension段落からsurvey/percentageの直接紹介文を削除。Trial-06最終版
  ("A 2024 workplace survey found that about 37 percent of people…")に
  相当する文はTrial-07最終版のTensionに一切登場しない(§5で原文比較)。
- Closingの結び方を、Trial-06の「A desk may be a small anchor…It may
  also be a tool for changing…」(2つの機能を並記する形)から、Trial-07は
  「continuity/choiceという2つの"built through"の軸→"what makes a worker
  feel ready to work and able to belong"という一段抽象化した問いの再定義」
  へ変更(§5で原文引用)。
- attempt1→attempt2間でも、Voice A/Bの中の外部報告文("In one Japanese
  survey, roughly one in three hot-desk users described…"、"Workers in
  one Japanese workplace said that moving seats made it easier to talk
  with people from other departments.")を、Analytical Leakage Check
  是正メモに基づき全文書き直しで削除。数字そのものを使わない一人称の実感
  表現へ置換した(§7で詳細)。
- 一方、語数そのものは**削れていない**(Trial-06 419語→Trial-07最終453語、
  §8参照)。これは意図した削減とは逆方向の結果であり、正直に開示する。

---

## 5. Tension・Closingの仕様適合(引用)

**Tension(最終article.md)**:
> "These two workers are not really answering the same question. The
> first asks, "Where can I return to each morning?" The second asks,
> "What kind of place do I need today?" One feels secure when the
> surroundings stay familiar. The other feels secure when movement
> remains possible."

survey/research/dataを主語にした文・数字の比較は一切登場しない。Analytical
Leakage Check(拡張版、§7)は`leak_evidence_subject`・`leak_numbers_
foreground`・`leak_discovery_syntax`・`leak_evidence_memorable`・
`leak_tension_reverts_to_research`の5項目すべてPASS、reasoning:「2人の
問いの違いを、継続性による安心と移動可能性による安心という価値観の対比
として掘り下げている。研究結果や数字の紹介には戻らず…」。

**Closing(最終article.md)**:
> "The desk debate is not only about where furniture goes. It is about
> how people find a workable place in a shared office. For some, that
> place is built through continuity… For others, it is built through
> choice… The deeper question is not simply fixed or free. It is what
> makes a worker feel ready to work and able to belong."

「fixed or free」という表面的対立軸を、「built through continuity / built
through choice」→「what makes a worker feel ready to work and able to
belong」という一段抽象的な軸へ組み替えており、「両方に良い点がある」で
終わらせていない。解決策提案(半固定席・ゾーン制等)も無い。Leakage Check
`leak_closing_simple_summary`はPASS、reasoning:「単に両論を要約するのでは
なく、共有オフィスで働く準備と所属感を何が生むのかという問いに広げて
締めている。具体的な制度や妥協案をWriterが提案しているわけでもない」。

---

## 6. 一人称/三人称の選択結果と理由(Writer出力の観察)

Contractは一人称/三人称を指定していない(タスク指示どおり)。実測では、
attempt1・attempt2とも**Voice A・Voice Bをどちらも一貫して一人称("I")**で
書いた("Every morning, I look for a desk nobody is using."等)。Hook・
Tension・Closingは一貫して三人称の語り手視点のまま(既存Hookルール「三人称で
書き始める」の対象は元々Hookのみ)。Trial-06最終版も同じく一人称だった
(§8比較表参照)ため、本Trialでは新しい選択パターンの発見はなく、
「一人称がこのテーマ・Voice Cardの組み合わせでは安定して選ばれる」という
既存観察を再確認した形。Production採用可否はユーザー判断(§12)。

---

## 7. Analytical Leakage Check結果(attempt別・引用・再実行回数)

タスク指示「検出対象…TensionでResearch説明に戻る構成、Closingが単純要約」に
対応するため、Trial-06までのVoice A/B限定6基準に加え、**Tension用5基準
(既存4基準の流用+`leak_tension_reverts_to_research`新規)・Closing用1基準
(`leak_closing_simple_summary`新規)を追加**した(voice_a/voice_bの6基準は
Trial-06から無変更)。詳細実装は`er012_editorial_b_voices_trial_07.py`の
`VOICE_LEAKAGE_FIELDS`/`TENSION_LEAKAGE_FIELDS`/`CLOSING_LEAKAGE_FIELDS`。

| attempt | voice_a | voice_b | tension | closing | any_flagged |
|---|---|---|---|---|---|
| 1 | FAIL(leak_evidence_subject, leak_discovery_syntax) | FAIL(leak_discovery_syntax) | PASS(全5項目) | PASS | **true** |
| 2 | PASS(全6項目) | PASS(全6項目) | PASS(全5項目) | PASS | **false**(確定) |

attempt1のFAIL引用: Voice A「In one Japanese survey, roughly one in
three hot-desk users described returning to the same seat.」、Voice B
「Workers in one Japanese workplace said that moving seats made it
easier to talk with people from other departments.」— いずれもVoice
本文の中でsurvey/研究結果の紹介文がDiscovery型構文へ戻る、Trial-06までにも
繰り返し確認されているパターンで、**Tension/Closingではなく、拡張前から
あったVoice側の基準で検出された**。Tension/Closing自体は両attemptともPASS
であり、A/B(Tension/Closing)の新Contract条項は、少なくとも本Trial実行の
範囲では2 attemptsとも一度も破られなかった。

再実行回数: 1回(初回attempt1がflagged→是正メモ付きでattempt2を実行、
attempt2でany_flagged=false、MAX_WRITER_ATTEMPTS=3のうち2回で確定、
上限未到達)。

全raw記録: `er012_output/editorial_b_voices_trial_07/b1b_run01_attempt1/
analytical_leakage_check_attempt1.json`、`.../b1b_run01_attempt2/
analytical_leakage_check_attempt2.json`、
`er012_output/editorial_b_voices_trial_07/b1b_run01_attempt_history.json`。

---

## 8. Trial-06との比較表

| 項目 | Trial-06最終(attempt3) | Trial-07最終(attempt2) |
|---|---|---|
| 総語数(5区切り合計) | 419語 | **453語**(soft target 350語に対し未達、Trial-06より+34語) |
| 内訳(Hook/VoiceA/VoiceB/Tension/Closing) | 73/92/98/93/63 | 63/113/105/96/76 |
| Tensionにsurvey/percentage主語の文 | あり("A 2024 workplace survey found that about 37 percent…") | **なし** |
| Closingの型 | 2機能の並記("may be…It may also be…") | 対立軸の組み替え("built through continuity"/"built through choice"→"ready to work and able to belong") |
| Evidenceの前面度(Tension) | 高(数字を軸に段落展開) | 低(2人の問いの違いを軸に展開、数字ゼロ) |
| 一人称/三人称(Voice) | 一人称 | 一人称(同じ) |
| Analytical Leakage Check対象 | Voice A/B(6基準)のみ | Voice A/B(6基準)+Tension(5基準)+Closing(1基準) |
| Analytical Leakage Check最終結果 | any_flagged=false(3attempt目) | any_flagged=false(2attempt目) |
| Fact Checker verdict | REVIEW_REQUIRED(FAILなし) | REVIEW_REQUIRED(FAILなし、同一既知パターン) |
| Ledger Deviation | LEDGER_COMPLIANT(MINOR 1件) | LEDGER_COMPLIANT(**MINOR 0件**) |
| Directional Fact Precheck | PASS | PASS |
| cost(概算) | 約$1.09(¥165前後、Phase A+B+C合算) | 約$0.25(¥38前後、Phase A相当のみ) |

「短くなった」だけで評価しない、という指示に対する結論: **短くはなっていない
(むしろ+34語)**。一方でTension/Closingの質的な仕様適合(Evidence前面度低下・
対立軸の組み替え)は明確に改善しており、Ledger Deviationも改善(1件→0件)。
「Compactnessだけが未達で、A/Bは達成」という非対称な結果を正直に報告する。

---

## 9. Reference Example比較

Trial-05/06と同じ制約が残る:リポジトリ内でReference Example 1(カフェ)・
Reference Example 2(リモートワーク)の記事全文は見つからず、
`EDITORIAL-B-FAMILY-VOICES-DESIGN-02_REPORT.md`に記録された設計原則との
比較にとどまる。同Reportが指摘する**判断基準の転換**("Example 2「remote
versus officeが間違った問い」")は、本Trial最終版のClosing("built through
continuity"/"built through choice"→"what makes a worker feel ready to
work and able to belong")と同型のEditorial mechanism(表面的対立軸を、
より深い判断基準へ組み替える)であり、Family similarityは維持されている
と判断する。ただし全文比較ができないため確度は限定的(Trial-05/06と同じ
留保)。

---

## 10. 技術結果(Fact Safety/Precheck/Point QA monitoring/語数/cost)

| 項目 | attempt1(不採用) | attempt2(採用) |
|---|---|---|
| Fact Checker verdict | REVIEW_REQUIRED | REVIEW_REQUIRED |
| unsupported_specific_claims | 3件(一人称体験の出典不明・因果の一般化・2026年9月時点動向の定量根拠不足、Trial-04〜06と同一の既知パターン) | 5件(同種のパターン、詳細は`b1b_run01_attempt2/fact_qa.json`) |
| contradictions | 0件 | 0件 |
| Ledger Deviation overall_status | (attempt1、記録は`b1b_run01_attempt1/ledger_deviation.json`参照) | LEDGER_COMPLIANT、MAJOR/MINORとも0件 |
| Directional Fact Precheck | (未到達、Leakage是正で再実行のため) | PASS |
| Point Overlap QA(monitoring) | lexical_flagged=False | lexical_flagged=False |
| Point Value QA(monitoring) | PASS | PASS |
| 語数(5区切り合計) | 400語(Hook 88/VoiceA 99/VoiceB 107/Tension 113/Closing 54)※old数値注記below | 453語(Hook 63/VoiceA 113/VoiceB 105/Tension 96/Closing 76) |
| Analytical Leakage Check | any_flagged=true(Voice A/B) | any_flagged=false |

※attempt1の実測は`b1b_run01_attempt1/five_section_length_report.json`
(hook 88/voice_a 99/voice_b 107/tension 113/closing 54、total 400)を正とする。

**Cost**: `raw_usage_log_trial07_writer.jsonl`(19コール、attempt1+attempt2
合算、新規Perplexity呼び出しゼロ)実測: input 231,461 tokens・output 54,380
tokens・cached_input 20,384 tokens・web_search 14回。pricing(input
$0.20/1M、output $1.20/1M、cached $0.02/1M、web_search $10/1,000 call、
Trial-06報告と同一単価)で概算**約$0.25(¥38前後、¥500を大幅に下回る)**。
TTSは実行していない。Cost超過によるSTOPには該当しない。

---

## 11. 受入条件12項目セルフチェック(根拠引用、最終判定はFable)

1. **約350語目標にコンパクト化**: **未達**。最終453語(attempt1は400語で
   目標に近かったが、Leakage是正でattempt2は453語に増加、§7・§8参照)。
2. **hard cap化していない**: 達成。Contract本文に「hard capではありません」
   「350語ちょうどに合わせる必要はなく」と明記、実際にpipelineも語数を
   ゲートにしていない(word_countはmonitoring専用フィールド)。
3. **主要意見優先**: 達成(Trial-06から無変更のPerspective選定、
   `research/perspective_map.md`参照)。
4. **Voiceの主人公が人**: 達成(§7 Analytical Leakage Check、voice_a/
   voice_bの`leak_evidence_memorable`は両attemptともPASS)。
5. **Evidenceが前面に出ていない**: attempt1のVoice A/Bで一部未達
   (survey文検出、是正済み)、attempt2は全項目PASS。最終採用版としては
   達成。
6. **Tensionにsurvey/percentageが主役として入らない**: 達成(§5・§7、
   `leak_tension_reverts_to_research`両attemptともPASS)。
7. **Tensionが「なぜ違う答えになるか」を掘る**: 達成(§5引用参照、
   "The first asks…The second asks…"の対比構造)。
8. **Closingが問いの再定義へ進む**: 達成(§5・§8、対立軸の組み替えを確認)。
9. **Narrator分析が前面に出ない**: 達成(`leak_narrator_analysis`・
   `leak_unknowable_analysis`両attemptとも全PASS)。
10. **Reference Example 2本と同じEditorial mechanism**: 部分的に達成
    (§9、全文比較不可のため確度は限定的、Trial-06から変化なし)。
11. **Fact Safety/Ledger/provenance維持**: 達成(Fact Checker FAILなし・
    contradictions 0件、Ledger Deviation MAJOR 0件、Directional Precheck
    PASS)。
12. **Trial-06より短くてもVoice/Tension/Closingの質が落ちていない**:
    **「短くても」の前提が成立せず**(§8、453語>419語)。Voice/Tension/
    Closingの質自体はTrial-06より向上または同等と判断する(§5・§8の
    質的比較)が、項目文言どおりの「短くて質が落ちていない」という組み合わせ
    条件は満たしていない。

**12項目中: 完全達成8、部分達成2(5・10)、未達2(1・12)**。未達2件は
いずれもCompactness関連であり、Tension/Closingの質的仕様(6・7・8)とは
独立して評価できる。

---

## 12. USER_DECISION_REQUIRED・Production採用判断が必要な仕様候補

1. **Tensionの役割定義(Evidence backstage化)・Closingの役割定義(対立軸の
   組み替え)**: 本Trialで2/2 attemptsとも安定して機能した。Production
   Voices/Perspective型記事のEditorial Contractへ正式採用するかは、
   人間ユーザーの`APPROVED_FOR_PRODUCTION`判断が必要(Production Prompt/
   Editor変更はSTOP条件、本Trialでは実施していない)。
2. **Compactness soft target(約350語)**: 本Trial1回の実行では意図どおり
   機能しなかった(453語)。原因は§7で述べたとおり、Analytical Leakage
   Check是正メモ(`build_leakage_corrective_note()`)が語数目標を再言及
   しないため、是正時に語数が伸びる余地が残ることだと判定する。改善案候補
   (未実装、実装するにはさらなるTrialまたはユーザー承認が必要):
   是正メモの中にも「約350語soft target」を明記して再送する、または
   是正後に語数だけを独立してmonitoring・報告する仕組みを追加する。
   これはPromptロジックの改修であり、本Trialのスコープ(Focus Module
   Block内の3節の書き換えのみ)を超えるため、実装せず提案にとどめる。
3. **Analytical Leakage Checkの4-section拡張
   (voice_a/voice_b/tension/closing)**: Trial-06までのVoice A/B限定6基準
   では「TensionでResearch説明に戻る構成」「Closingが単純要約」を検出
   できないことが判明したため、本Trialで`TENSION_LEAKAGE_FIELDS`
   (5基準、既存4基準の流用+新規1)・`CLOSING_LEAKAGE_FIELDS`(新規1基準)
   を追加した。この拡張自体もTrial限定の新規実装であり、Production
   Analytical Leakage Check相当の仕組みは現時点でProductionに存在しない
   (B Family自体が未採用のため)。将来B Family Voices型がProduction採用
   される場合、この4-section拡張版を土台とするかはユーザー判断。
4. **一人称Voice記述**: Contractが一人称/三人称を指定していないにも
   かかわらず、Trial-06・Trial-07とも2/2 attemptsが一貫して一人称を選択
   した。これを「Writerの自然な選択として尊重し続ける」か「Reference
   Exampleとの整合のため明示的に指定する」かは、Production採用時に
   ユーザー判断が必要(本Trialでは指定を追加せず、観察のみ)。

---

## 13. SSOT登録案(未実施)

本Trialは`docs/pm/*`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`
への正式登録を行っていない(タスク範囲外、SSOT・Fable領域は触れない指示の
ため)。Fable判断でSSOT反映が必要な場合、以下を登録候補として提示する:
- `OPEN_ITEMS.md`: 「B Family Voices/Perspective型 Editorial Contract
  (Tension/Closing/Compactness 3条項)のProduction採用可否」
  「Analytical Leakage Checkの4-section拡張の要否」を
  `USER_DECISION_REQUIRED`として追加登録する候補。
- `DECISION_LOG.md`: 未登録(ユーザー承認が確定した時点で追記する候補)。

---

## 技術的付記(透明性のための開示)

Phase A(write stage)を最初に一度実行した後、Analytical Leakage Checkが
Trial-06から無変更のVoice A/B限定6基準のままだったことに気づき(タスク
指示の検出対象リストに「TensionでResearch説明に戻る構成」「Closingが
単純要約」が明記されていたにもかかわらず未実装だった)、実行中の
プロセスを停止し、`er012_editorial_b_voices_trial_07.py`の
`run_analytical_leakage_check()`をTension/Closing対応へ拡張したうえで、
research/writer出力を含めクリーンな状態から再実行した。最初の不完全な
実行(attempt1のみ、Fact Checker完了直前で停止)はコストが記録される前に
停止しており(`raw_usage_log_trial07_writer.jsonl`は削除して再作成)、
§10のcostには含まれていない。

---

## 14. 往復1回目(run02): Contract是正メモ改修・Compactness節強化と再生成結果

Fableレビュー(run01最終453語、要旨は本Reportの往復依頼冒頭に記録)を受け、
`er012_editorial_b_voices_trial_07.py`のContract/Trial機構のみを修正し、
Perspective・Voice Card・Research・記事本文は一切手で書き換えず、run02として
Writerを再生成した。

### 14.1 修正内容(スクリプト差分、原文)

**(A) `build_leakage_corrective_note()`**: run01では、flagged項目の指摘のみで
Contract全体の優先事項を再言及しなかった(これがrun01でattempt1 400語→
attempt2 453語に増えた原因とFableが特定)。run02では、flagged項目リストの後に
以下を毎回のattemptで必ず追記するよう変更した:
```
【この記事全体で必ず守るContractの優先事項(是正のたびに毎回再掲。上記の
flagged箇所を直すことだけに集中して、以下を見失わないでください)】
- Compactness: 記事全体の総語数は約350語がsoft targetです(hard capではありません、
多少前後してかまいません)。上記の問題箇所を削るときは、**削った分だけ短くなることを
基本とし(replace-with-nothing)、削った直後に別の言い回し・別の具体例・新しい説明文で
同じ内容を書き足さないでください**。書き直す場合も、重複説明・Narrator(語り手)による
外側からの分析・余分なResearch説明・同義の言い換え・不要な導入文は入れないでください。
同じ経験・同じ感覚を2回描写しないでください。
- Tensionの役割: Tensionの中心はVoice Cardの2人の人物であり、Evidence
(survey/research/data/percentage)ではありません。survey・data・researchを主語に
した文で始めたり、その説明へ立ち戻ったりしないでください。
- Closingの役割: 単なる要約(「両方に良い点がある」「人による」)で終わらせず、また
Voice A・Voice B・Tensionの内容を並べ直してから結論に入るのでもなく、この問題が実は
何についての問題なのかという再定義そのものから書き始めてください。解決策の提案は
しないでください。
```
実装は`er012_editorial_b_voices_trial_07.py`の`build_leakage_corrective_note()`
(該当箇所)。

**(B) Contract Compactness節の強化**: `B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`の
「【記事全体の長さについて】」節へ以下3点を追記した(hard cap化はしていない、
既存soft targetの記述はそのまま維持):
1. 「各Voiceは同じ意味を2回言わないでください」(1つの経験は1回だけ描写)
2. 「Closingは、前段(Voice A・Voice B・Tension)の内容の要約から書き始めない
   でください。…再定義そのものから書き始めてください」
3. 配分の目安(soft guidance): Hook 60〜70語 / 各Voice 90〜100語 / Tension
   60〜70語 / Closing 40〜50語、合計約350語程度
禁止事項まとめへも「削るときは、基本的に何も足さない="replace-with-nothing"」
の1文を追加した。Contract全文diff(run01保存版 vs run02実行時版、27行、上記3点
以外の差分なし)は
`er012_output/editorial_b_voices_trial_07/audit/phase_a_b_family_voices_focus_module_block.txt`
と
`er012_output/editorial_b_voices_trial_07/b1b_run02/audit/phase_a_b_family_voices_focus_module_block.txt`
の`diff`で再現可能(run01版ファイルは無変更のまま保持)。

**(C) RUN_ID変更・出力先分離**: `RUN_ID = "run01"` → `"run02"`。Trial-04
run02の方式を踏襲し、`run_phase_a()`の監査出力・`cl.install()`のcost log・
`audit_candidate_prompt_base.txt`・`trial07_summary.json`をすべて
`LEVEL_OUT_DIR`(`b1b_run02/`)配下または`run02`専用ファイル名へ変更し、
run01のtracked出力(`OUT_DIR/audit/`・`audit_candidate_prompt_base.txt`・
`raw_usage_log_trial07_writer.jsonl`・`trial07_summary.json`)を一切上書き
していない(実行後にファイルタイムスタンプ・サイズで無変更を確認済み)。

Research(`research/perspective_map.md`・`verified_fact_ledger.txt`)は
run01からファイル単位で無変更のまま再利用した(research stageは再実行して
いない、`run_writer_stage()`のみ実行)。

### 14.2 run02実行結果: attempt別語数・Leakage

| attempt | 総語数(5区切り) | 内訳(Hook/VoiceA/VoiceB/Tension/Closing) | any_flagged | flagged詳細 |
|---|---|---|---|---|
| 1 | 390語 | 65/105/89/72/59 | **true** | voice_aのみ: `leak_evidence_subject`, `leak_numbers_foreground`, `leak_narrator_analysis`, `leak_unknowable_analysis`, `leak_discovery_syntax`(5/6項目FAIL)。原因は挿入された1文"For about 37 percent of people using hot desks, the seat they choose becomes their regular place."(voice_b/tension/closingは全PASS) |
| 2 | **388語** | 51/99/101/81/56 | **false**(確定) | 該当なし。voice_a/voice_b/tension/closingとも全項目PASS |

再実行回数: 1回(初回attempt1がflagged→是正メモ付きでattempt2を実行、
attempt2でany_flagged=false、MAX_WRITER_ATTEMPTS=3のうち2回で確定、上限未到達)。
run01と同じ「2 attemptsで確定」だが、**attempt1→attempt2間で語数がほぼ変化
しなかった(390語→388語、-2語)**。run01ではこの是正1回で400語→453語
(+53語)に増加していたため、build_leakage_corrective_note()の改修は狙いどおり
機能したと判断する。

全raw記録: `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt1/
analytical_leakage_check_attempt1.json`、`.../b1b_run02_attempt2/
analytical_leakage_check_attempt2.json`、
`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt_history.json`、
`er012_output/editorial_b_voices_trial_07/b1b_run02/trial07_summary_run02.json`。

### 14.3 最終記事全文(run02 attempt2、原文・無編集)

採用: `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`

```markdown
# One Office, Two Ideas of a Place to Work

## The Question

Every morning, one employee enters the office and looks for an empty desk. Another chooses a quiet corner or a lively place near other teams. Some companies are bringing back assigned desks, while others continue shared seating. Why can the same office feel secure to one person and liberating to another?

### One Voice: The desk that lets work begin

Every morning, I look for an empty desk. Someone else may have used it yesterday, and someone new may sit there tomorrow. I cannot leave papers in a drawer, and I sometimes worry about using a desk or keyboard after someone else. Before work begins, I have already spent time finding a place. I miss the same desk, drawer, and view. They helped me start without searching and gave me a quiet sense of belonging. Now the office can feel borrowed. I want my work and things to have a place, even when I cannot choose the seating policy.

### Another Voice: The freedom to move

Some mornings, I choose a quiet corner because I need to think. On other days, I sit where conversation is easy. A different desk can bring me closer to people from another department. It can also give me distance when a workplace relationship feels uncomfortable or when I simply need room. Since working from home gave me a place of my own, I do not need one fixed spot at the office. I value being able to change my surroundings and choose a place that fits my mood, my task, and the people I need—or do not need—around me.

## Where the Difference Comes From

The disagreement is not really about movement. It is about where stability comes from. One employee finds it in a desk that stays put, with papers and a familiar start. The other finds it in the power to change social distance and the kind of space needed that day. A shared-seat system can even create unofficial regular desks. So a rule that looks flexible on paper may feel like friction to one person, while the same system feels useful to another.

## What the Seat Really Means

The real question is not fixed desks or shared desks. It is what makes a place workable: a stable point that removes daily searching, or enough control to change one's social and working surroundings. The seat is only the visible part of a deeper question: what makes an employee feel, "This is my place at work"?
```

**pre_editor_article.mdとの差分**(Evidence Compression Editor、Production
無変更): 4箇所いずれも語句レベルの軽微な言い回し調整のみ(例: "Yesterday,
someone else may have used it, and tomorrow someone new may sit there."←
"Someone else may have used it yesterday, and someone new may sit there
tomorrow."の語順入れ替え、"the same drawer, and the same view"←"drawer,
and view"のような重複語の整理)。主語の入れ替え・削除・意味変化はない。全差分:
`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/audit/pre_editor_article.md`
と`article.md`の`diff`。

### 14.4 選定理由(「機械的にPASSかつ350語最近傍」を選ばない、の実践)

run02では、Leakage Check全4-section PASSとなったattemptはattempt2のみ
(attempt1はvoice_aで5/6項目FAIL)。したがって「Contract順守(Tension/
Closing/Voice質)を満たすattemptのうち最短のもの」はattempt2が唯一の候補で
あり、機械的な「PASSかつ350語最近傍」の複数候補からの選択は発生しなかった。
それでも、機械判定(Leakage PASS)だけに頼らず、Tension・Closingの原文を人手で
再確認した:
- Tension(§14.3引用)は"The disagreement is not really about movement. It
  is about where stability comes from."から始まり、2人がそれぞれ何に安定を
  見出すかの違いを掘り下げており、survey/data主語の文は無い。
- Closingは、run01最終版で見られた「Voice A・Bの要約を再掲してから再定義に
  入る」という構造(§8で指摘済み)を回避し、要約段落を経ずに"The real
  question is not fixed desks or shared desks."から直接再定義へ入っている。
  「desk, drawer, view」「focus, conversation, or distance」のような前段の
  具体的語彙の再掲は無い。
- Voice A・Voice Bとも、run01で指摘された同義反復(例: 「familiar place to
  begin work」の2回描写、「choice」の2回強調)に相当する重複は見当たらない
  (§14.5でrun01との対比を記録)。
この確認により、attempt2はContract順守(Tension/Closing/Voice質)を満たす
としてそのまま採用した。

### 14.5 run01・Trial-06との比較表

| 項目 | Trial-06最終(attempt3) | Trial-07 run01最終(attempt2) | Trial-07 run02最終(attempt2) |
|---|---|---|---|
| 総語数(5区切り合計) | 419語 | 453語 | **388語**(soft target 350語との差-38語、run01比-65語) |
| 内訳(Hook/VoiceA/VoiceB/Tension/Closing) | 73/92/98/93/63 | 63/113/105/96/76 | 51/99/101/81/56 |
| Voice内の同義反復 | (未評価) | あり(§14.4参照、「familiar place to begin work」等2回描写) | **確認されず**(原文再読、§14.4) |
| Closingが前段要約を経てから再定義に入るか | (未評価) | **経る**("the same desk, drawer, and view"等を再掲してから再定義) | **経ない**(要約段落なしで直接再定義) |
| Tensionにsurvey/percentage主語の文 | あり | なし | なし |
| Evidenceの前面度(Voice/Tension) | 高(Tensionで数字を軸に展開) | 低 | 低(attempt1で数字1つ挿入されたが是正で削除、attempt2は0個) |
| 一人称/三人称(Voice) | 一人称 | 一人称 | 一人称(同じ) |
| Analytical Leakage Check最終結果 | any_flagged=false(3attempt目) | any_flagged=false(2attempt目) | any_flagged=false(2attempt目) |
| attempt1→是正後の語数変化 | (該当データ無し) | +53語(400→453) | **-2語(390→388)** |
| Fact Checker verdict | REVIEW_REQUIRED | REVIEW_REQUIRED | REVIEW_REQUIRED(同一既知パターン、§14.6) |
| Ledger Deviation | LEDGER_COMPLIANT(MINOR 1件) | LEDGER_COMPLIANT(MINOR 0件) | LEDGER_COMPLIANT(**MINOR 2件、MAJOR 0件**) |
| Directional Fact Precheck | PASS | PASS | PASS |
| Point Overlap/Value QA(monitoring) | (§8参照) | lexical_flagged=False、PASS | lexical_flagged=False、value_qa PASS |
| cost(概算、writer stageのみ) | 約$1.09 | 約$0.25(¥38前後) | 約$0.17(¥25前後) |

結論: Compactness(受入条件1)は**run02で達成**(388語、350語soft targetに
対し-38語のみ、Trial-06の419語より短い)。この達成は「単に短くなった」の
ではなく、Tension/Closingの質的仕様(受入条件6〜8)を維持したまま、かつ
同義反復・要約再掲という具体的な冗長要素を排除した結果であることを、原文の
再読で確認した(§14.4)。

### 14.6 技術結果(Fact Safety/Precheck/QA/cost、run02 attempt2)

| 項目 | attempt1(不採用) | attempt2(採用) |
|---|---|---|
| Fact Checker verdict | (未取得、Leakage是正で再実行のため) | REVIEW_REQUIRED(unsupported_specific_claims 5件、Trial-04〜run01と同一の既知パターン=一人称体験の出典不明・企業名/時期不明の業界動向・Tensionの解釈の断定性) |
| contradictions | (未取得) | 0件 |
| Ledger Deviation overall_status | (未取得) | LEDGER_COMPLIANT、MINOR 2件("Every morning"という頻度の断定がLedgerの裏付けを超える、Hook側1件・Voice A側1件)、MAJOR 0件 |
| Directional Fact Precheck | (未到達) | PASS |
| Point Overlap QA(monitoring) | (未取得) | lexical_flagged=False(4方向とも overlap_ratio 0.14〜0.2、閾値0.4未満) |
| Point Value QA(monitoring) | (未取得) | PASS(6項目×2 Point全PASS) |
| 語数(5区切り合計) | 390語 | 388語 |
| Analytical Leakage Check | any_flagged=true(voice_a) | any_flagged=false |

**Cost**(`b1b_run02/raw_usage_log_trial07_writer_run02.jsonl`、14コール、
attempt1+attempt2合算、run01のcost logとは別ファイルで計測): 実測 input
161,286 tokens(うちcached 20,384 tokens)・output 39,830 tokens・web_search
9回。run01と同一単価(input $0.20/1M、output $1.20/1M、cached $0.02/1M、
web_search $10/1,000call)で概算**約$0.17(¥25前後、¥500を大幅に下回る)**。
TTSは実行していない。Cost超過によるSTOPには該当しない。

### 14.7 受入条件12項目セルフチェック(run02時点、根拠引用、最終判定はFable)

1. **約350語目標にコンパクト化**: **達成**(388語、-38語差)。
2. **hard cap化していない**: 達成(Contract本文・是正メモとも「soft target」
   「hard capではない」を維持、変更なし)。
3. **主要意見優先**: 達成(run01から無変更のPerspective選定)。
4. **Voiceの主人公が人**: 達成(§14.2、voice_a/voice_bとも6項目全PASS)。
5. **Evidenceが前面に出ていない**: attempt1のVoice Aで一部未達(37%の挿入文、
   是正済み)、attempt2は全項目PASS。最終採用版としては達成。
6. **Tensionにsurvey/percentageが主役として入らない**: 達成(両attemptとも
   `leak_tension_reverts_to_research`PASS)。
7. **Tensionが「なぜ違う答えになるか」を掘る**: 達成(§14.3引用、"where
   stability comes from"の対比)。
8. **Closingが問いの再定義へ進む**: 達成(§14.3・§14.4、要約段落を経ずに
   直接再定義)。
9. **Narrator分析が前面に出ない**: 達成(`leak_narrator_analysis`両attempt
   とも全PASS)。
10. **Reference Example 2本と同じEditorial mechanism**: 部分的に達成
    (run01と同じ留保、全文比較不可)。
11. **Fact Safety/Ledger/provenance維持**: 達成(Fact Checker FAILなし・
    contradictions 0件、Ledger Deviation MAJOR 0件、Directional Precheck
    PASS)。
12. **Trial-06より短くてもVoice/Tension/Closingの質が落ちていない**:
    **達成**(388語<419語、かつ§14.4・§14.5でTension/Closingの質は同等以上
    と判断)。run01で未達だったこの項目が、run02で達成に転じた。

**12項目中: 完全達成10、部分達成2(5・10)、未達0**。run01の未達2件
(Compactness・「短くても質が落ちない」)がいずれもrun02で達成に転じた。

### 14.8 一人称/三人称の選択結果

run02もattempt1・attempt2とも、Voice A・Voice Bをどちらも一貫して一人称
("I")で書いた。Hook・Tension・Closingは一貫して三人称の語り手視点のまま。
run01・Trial-06と同じ結果であり、新しい選択パターンの発見はない
(Contractは引き続き一人称/三人称を指定していない)。

### 14.9 Closeout分類案(run02時点、§0を更新)

**VALIDATED(仕様候補として有効性を確認、Production採用は別途
USER_DECISION_REQUIRED)**。

run01でFableが指摘した唯一の未達項目(Compactness、受入条件1・12)が、
build_leakage_corrective_note()へのContract優先事項再掲・Contract
Compactness節への同義反復禁止/Closing再定義先行/配分soft guidanceの3点
追記という、**Trial機構側の修正のみ**(記事本文の手作業書き換えなし)で
run02において達成された(388語、attempt1→attempt2間の語数増加も
+53語→-2語へ改善)。Tension/Closingの役割(run01で既に達成済みの2点)は
run02でも引き続き2/2 attemptsとも安定して機能した。3点(Tension/Closing/
Compactness)すべてが実記事生成で再現された状態であり、run01時点より
確度の高いVALIDATEDと判断する。Production採用可否は引き続き人間ユーザー
判断(§12のUSER_DECISION_REQUIRED項目は無変更、追加で「run02のCompactness
改善[是正メモへのContract優先事項再掲・配分soft guidance]をProduction相当
の仕組みへ含めるか」も同種の判断対象に加わる)。

### 14.10 参照ファイル一覧(run02分、証跡)

- Trial script(該当箇所): `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_trial_07.py`
  (`build_leakage_corrective_note()`・`B_FAMILY_VOICES_FOCUS_MODULE_BLOCK`の
  Compactness節・`RUN_ID`・`run_writer_stage()`の出力先分離)
- Contract全文(run02実行時): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02\audit\phase_a_b_family_voices_focus_module_block.txt`
- Contract全文diff元(run01保存版、無変更): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\audit\phase_a_b_family_voices_focus_module_block.txt`
- 最終記事(run02採用): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02_attempt2\article.md`
- attempt1記事(不採用、参考): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02_attempt1\article.md`
- Leakage Check詳細: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02_attempt_history.json`、`b1b_run02\trial07_summary_run02.json`
- Fact Safety: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02_attempt2\fact_qa.json`、`ledger_deviation.json`、`audit\directional_fact_precheck.json`
- Cost log: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run02\raw_usage_log_trial07_writer_run02.jsonl`
- Research(run01から無変更・再利用): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\research\perspective_map.md`、`verified_fact_ledger.txt`

---

## 参照ファイル一覧(証跡)

- Trial script: `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_trial_07.py`
- Contract全文: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\audit\phase_a_b_family_voices_focus_module_block.txt`
- 最終記事: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run01_attempt2\article.md`
- attempt1記事(不採用、参考): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run01_attempt1\article.md`
- Leakage Check詳細: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run01_attempt_history.json`
- Fact Safety: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\b1b_run01_attempt2\fact_qa.json`、`ledger_deviation.json`、`audit\directional_fact_precheck.json`
- Cost log: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\raw_usage_log_trial07_writer.jsonl`
- Research(再利用): `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_07\research\perspective_map.md`、`verified_fact_ledger.txt`
- (run02分は§14.10を参照)
