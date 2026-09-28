# FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT

管理ID: FAMILY-Y-VOICE-STRUCTURE-TRIAL-01(ユーザー承認済みTrial、Production配線なし)。
実行日: 2026-09-28。Sonnet実行(初回、委任1回目)。

## 0. T-0結果

delegation_log保存: `docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_01.md`。
check script結果: `status: FAIL`(理由: 単体test実行コマンド行が「引数実値/絶対パス」形式チェックに
非該当。委任文は受領内容を逐語保存したため書き換えていない)。TTS警告はfalse positive
(本文中の"TTSなし"という記述自体が検知されたもの、T-2の通り実際にはTTS実行なし)。
詳細: `docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_01.md_check.json`。

## 1. 使用した記事・レベル

`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2`(Family B、3V、A2レベル、
"When AI Sits Between a Job and a Person")。B1レベル出力は存在しないためA2のみで実施
(委任文の指定どおり)。Before = この既存A2記事(`article.md`/`parts.json`)。
入力Fact材料 = `er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt`
(Family B 4V Trial用Verified Fact Ledger、41 fact中CONFIRMED 39件、うちVoice1-3+
CROSS_REFERENCE可視分17件)。

## 2. Family Xから流用した正式名称・仕組み(対応表)

| Family X正式名称 | 出典 | 本Trialでの使用 |
|---|---|---|
| Storyline決定+B3 Fact選定(LLM 1 call、Selected Fact Brief目安3〜5件) | `er019_family_x_storyline_b3_fact_selection_01.py::run_storyline_b3_selection()` | Step 1(無変更import)。入力Ledgerの形式差(`[VOICE_N_EVIDENCE]`形式→Family X期待の`[VERIFIED]`形式)はTrialスクリプト内のデータアダプタで橋渡し(Family B既存`build_ledger_fragment_visible_voices_only()`でVoice4除外→CONFIRMEDのみ`[VERIFIED] fact_id: text`へ変換)。実行結果: 5件選定(6件未満のためrecheck_note不要) |
| R1→R2 Entertainment性向上Revision | `er019_family_x_ja_writer_o_r1_r2_01.py::REVISION_INSTRUCTIONS["r1"]/["r2"]` + `call_fresh`/`call_with_previous_response_id`(previous_response_id連鎖) | Step 7(逐語・無変更import)。JA専用Fact Check/音声化禁止記号チェックは適用せず(設計書§1分類B、JA Full Ledger形式必須のため技術的に不可、TTSも本Trial対象外)。**この判断はSonnetの解釈であり、Fable/ユーザー確認事項** |

英語本文向けの独立したR1→R2実装はFamily Xに存在しない(Advanced/Standardはentertainment
revision型ではなくAdaptation/簡略化型)。詳細は`docs/pm/design_family_y_voice_structure_trial_01.md`§1。

## 3. Family Bから流用した既存Voice重複対策

既存あり(新規重複実装はしていない)。`er012_b_family_voices_writer_generic_01.py`
(Production、read-only import)の以下2つを無変更で使用:
- `run_overlap_monitoring_3v`(lexical overlap/paraphrase検知、monitoring専用): Before/R1/R2
  いずれも`any_flagged=False`(Voice間の字句流用は検出されず)。
- `run_analytical_leakage_check_3v`(LLM 1 call、`leak_position_blur`含む7項目Voice+6項目
  Tension+1項目Closing、2026-09-17ユーザー正式承認[B-FAMILY-VOICES-POSITION-AND-EVIDENCE-
  SPEC-01]で追加済みのcross-voice項目含む): Before=2件、R1=2件(fail-field数3)、R2=4件
  (fail-field数11)。詳細は§6。

## 4. 前段の割当結果(Step 1/2)

Selected Storyline(要約): 「企業は採用の速度・コストを下げるためAI選考を広げているが、
運用する人事には公平性説明責任、応募者には不透明判定の不利益、経営者には効率化と
法的・reputationalリスクの両方の判断が生じる」。Selected fact_ids(5件):
`R2_fact_004`/`R2_fact_006`/`R1_recruiter_industry_pressure_to_document_ai_fairness`/
`R2_fact_011`/`R1_business_risk_of_discrimination_and_reputation_nature`。

| Voice | Stakeholder | Angle | fact_ids |
|---|---|---|---|
| voice_1 | Applicant | AI評価が採用機会に与える影響、判定基準の不透明さ、opt-out・異議申立不能への懸念 | R2_fact_004(1件) |
| voice_2 | Recruiter / Hiring Manager | 日々の採用業務でAIを使いつつ公平性を説明する責任、候補者の不信への透明性対応 | R2_fact_006, R1_recruiter_industry_pressure_to_document_ai_fairness(2件) |
| voice_3 | Business Owner | AIが速度・コスト面で意味ある効果を生むか、差別訴訟・法的責任・reputation毀損リスクとの比較 | R2_fact_011, R1_business_risk_of_discrimination_and_reputation_nature(2件) |

Validation(`validate_voice_assignment`): エラー0件(1〜2件/Voice、全Voice同一fact_id集合の
禁止条件を満たす、fact_id overlap between voices = `any_shared: false`)。

## 5. R1/R2全文・R1→R2で何が変わったか

- R1全文: `er036_output/family_y_voice_structure_trial_01/ai_hiring_3v/r1_article.md`
- R2全文: `er036_output/family_y_voice_structure_trial_01/ai_hiring_3v/r2_article.md`

R1→R2 diff要約: 見出し・冒頭表現がより具体的・情景的になった(例: Hook見出し
"A Faster Door That May Be Harder to Open"→"The Score Appears Before the Interview"、
Tension見出しが疑問形から比喩表現へ)。語数はVoice毎に約25〜35%増加(§6表参照)。
**同時に、R2はVoiceごとに割り当てたFactの元テキスト(fact_by_idとしてcontext提供した
全文)から、より詳細な固有名詞・数字を掘り出して前景化した**(fabrication ではなく、
CONFIRMED済みFactの範囲内。例: voice_1はR2_fact_004の元テキストにある「CVS Health」
「HireVue」「Affectiva」「集団訴訟の暫定和解」を新たに明示、voice_2はR2_fact_006の
元テキストにある「91%のHRリーダーが...使用」という数字を新たに前景化、voice_3は
R2_fact_011の元テキストにある「Hilton」「IBM」の社名付き効果数値を新たに前景化)。
これはFamily XのEntertainment revision指示(「もっと/さらにエンターテインメント性の
高い記事に修正してください」)が、具体的な固有名詞・数字による臨場感を志向するために
起きたと考えられる。

## 6. 4課題それぞれの改善状況(決定論指標+Family B QA+LLM評価)

### 6.1 決定論的指標

| 指標 | Before | R1 | R2 |
|---|---|---|---|
| Fact紹介型冒頭文(参考指標、本サンプルでは検出0件) | 0/3 voices | 0/3 voices | 0/3 voices |
| 抽象語(society/trust等)出現 | 0件 | trust×2(voice_1/3、相対位置0.47/0.51) | trust×3(voice_1/3、相対位置0.28/0.57/0.59) |
| Voice平均語数 | 約89語 | 約206語 | 約261語 |
| Voice間fact_id重複 | (対象外、Before未生成) | 0件(any_shared=false) | 0件(any_shared=false) |

### 6.2 Family B既存Leakage Check(analytical_leakage_check_3v、any_flagged section数/fail-field数)

| | Before | R1 | R2 |
|---|---|---|---|
| flagged sections | 2 (voice_3, tension) | 2 (voice_1, voice_3) | 4 (voice_1, voice_2, voice_3, tension) |
| 合計fail-field数 | 2 | 3 | **11** |
| overlap_monitoring_3v(any_flagged) | False | False | False |

**この既存QA機構が示す結論はLLM rubricと逆方向**: R2はvoice_2で
`leak_evidence_subject/leak_numbers_foreground/leak_narrator_analysis/leak_discovery_syntax/
leak_evidence_memorable`の5項目全FAIL、voice_3で4項目FAIL(理由: 「91%のHRリーダーが...」
「HiltonとIBMの報告値が具体的な比較データとして前面に出ている」)。

### 6.3 LLM rubric(1〜5点、1=課題深刻、5=課題解消)

| 課題 | Before | R1 | R2 |
|---|---|---|---|
| 1. Fact言い直し | 2 | 3 | 4 |
| 2. Voice間の差 | 4 | 5 | 5 |
| 3. 抽象論化 | 2 | 3 | 4 |
| 4. 人の発言に聞こえるか | 3 | 4 | 5 |

**観察(重要)**: LLM rubricはBefore→R1→R2で単調に改善したと判定したが、rubricが「改善」の
根拠として引用したR2のevidence_quote自体("Hilton has reported that its average hiring
time fell from about six weeks to five days after using AI.")は、既存Family B Leakage
Checkが同じ箇所を`leak_numbers_foreground`/`leak_discovery_syntax`でFAILと判定した箇所と
一致する。単一のLLM rubric callだけに依存すると、具体的な数字・固有名詞による「読み応え」
を誤って「課題解消」と評価しうることが実測された。既存Family B QA機構(field単位の
厳格な判定基準)を併用したことで、この乖離を検出できた。

## 7. 8確認項目の結果表

| # | 確認項目 | 結果 |
|---|---|---|
| 1 | Fact言い直しが減ったか | 混在。rubric上は改善傾向だが、既存Leakage Checkでは R2 で悪化(fail-field 2→3→11) |
| 2 | Voice同士の差が明確になったか | 改善傾向(rubric 4→5→5、overlap_monitoring常にFalse=字句流用なし)。ただしBeforeも既に4点と高く、本サンプルでは当初から深刻な問題ではなかった可能性 |
| 3 | 後半の抽象論化が減ったか | 部分的悪化。抽象語(trust)の出現がBefore0件→R1/R2で複数件(参考指標、位置は前半〜中盤寄り)。rubric上は改善(2→3→4)、指標間で不一致 |
| 4 | 人の発言に聞こえるか | rubric上は改善(3→4→5)。ただしLeakage Checkの`leak_narrator_analysis`はR2のvoice_2でFAIL(語り手的分析文が混入) |
| 5 | Factを絞ったことで情報不足になっていないか | 情報不足の兆候なし(語数はBefore比R1で約2.3倍、R2で約2.9倍。Voiceは割当Fact数が少なくても自分の推論・経験則で語れている) |
| 6 | Fact Assignment+Angle先決めがWriterの自然さを損ねていないか | 損ねている兆候なし(validation error 0件、fact_id重複0件、rubric上の自然さ関連スコアも高い) |
| 7 | Family XのR1→R2がFamily Yにも有効か | **要検討**。Entertainment revision指示は、割当Fact本文からより具体的な数字・固有名詞を掘り出す方向へ働き、既存Leakage Checkの観点では逆効果(§5/§6.2)。JA専用Fact Check相当の安全機構なしにR1→R2単体を適用するのはリスクがある |
| 8 | 既存Family BのVoice diversity仕様との重複/競合なし | 競合なし(既存`run_overlap_monitoring_3v`/`run_analytical_leakage_check_3v`をそのまま呼び出せた。新規重複実装は行っていない) |

## 8. 新しく発見した問題(実装せず報告のみ)

1. **R1→R2 Entertainment revisionとVoice Fact抑制方針の構造的緊張**: Family Xの
   Entertainment revision指示("エンターテインメント性の高い記事に修正")は、既に
   contextとして渡した検証済みFactの原文から、より具体的な数字・固有名詞を掘り出して
   前景化する方向に働きやすい。これは「Fact is context, not script」というFamily Yの
   基本思想と逆方向であり、単純併用は推奨できない。改善候補(未実装、Fable/ユーザー
   判断待ち): (a) Revision指示へ「新しい固有名詞・数字を新たに前景化しない」という
   制約文を追加する、(b) R1→R2後に既存Leakage Checkをmust-fix retryのゲートとして
   接続する、のいずれもFamily Y専用の新仕様となるため、本Trialでは提案のみに留める。
2. **LLM rubric 1 callの評価バイアス**: 具体的な固有名詞・数字を含む文を「人間らしい/
   面白い」と評価しやすく、既存Leakage Checkが検出するFact-restating問題を過小評価する
   傾向が実測された(§6.3)。単独評価には使わず、既存Family B Leakage Check等の
   field単位QAとの併用が必須と考えられる。
3. **抽象語検出器の限界**: 本サンプルでは`society/the future`等は出現せず`trust`のみ
   検出された。1語のマッチでは「抽象論化」の実質を捉えきれておらず、参考指標以上の
   役割を持たせるべきではない(委任文の設計通り、gateにはしていない)。
4. **Fact Ledger形式の非統一**: Family Xの`extract_fact_ids_from_ledger()`は
   `[VERIFIED] fact_id:`形式専用であり、Family B系Verified Fact Ledger(`[VOICE_N_
   EVIDENCE] N-NN(fact_id):`形式)とは非互換。今後Family X関数をFamily B系データへ
   適用する場面が増えるなら、恒久的なアダプタ関数(Production化)の要否をFable/
   ユーザー判断待ちの候補として記録する(本Trialでは使い捨てのTrial内関数のみ実装)。

## 9. QCD上の懸念

- 費用実測: 合計¥5.90(2回実行分の累積、うち1回目はディレクトリ未作成バグで
  Step1-7完了後に中断[¥2.19相当]、2回目で完走)。予算上限¥40に対し十分な余裕。
- call数: Step1(1) + Step2(1) + Step3-5 Voice Writer(1) + Step7 R1→R2(2、previous_
  response_id連鎖) + Family B QA(Before/R1/R2 各1、計3) + LLM rubric(1) = 合計9 call
  (1記事あたり)。
- 所要時間: 実測ログ上、2回目実行はStep1〜評価完了まで概算数分(reasoning_effort=
  "medium"のため、Production既定"high"より短い)。
- Production化時の追加call数(仮に配線する場合の見積り、実装はしていない): 上記9 call
  に加え、既存Family B Writer品質Gate相当(attempt retry機構、`MAX_WRITER_ATTEMPTS`等)を
  組み込む場合は1記事あたりさらに数call増える可能性がある。また、問題8-1のmust-fix
  retryをR1→R2後に追加する場合、追加で1〜2 call/記事が必要になる見込み。

## 10. Trial終了status案

**`USER_DECISION_REQUIRED`**(SonnetはVALIDATEDを自己宣言しない)。根拠:
- 良かった点: Fact Selection(Family X既存流用)→Voice Fact Assignment→Angle先決めの
  前段は技術的に機能し(validation error 0件、Voice間fact_id重複0件、情報不足の兆候なし)、
  Family B既存Voice diversity機構(overlap monitoring/leakage check)ともバイト単位で
  無変更のまま連携できた(課題5/6/8は前向きな結果)。
- 未解決点: 中核の懸念(課題1 Fact言い直し、課題3 抽象論化)について、LLM rubric単独では
  改善したように見えるが、既存Family B Leakage Check(より厳格・field単位)では
  R1→R2適用後にむしろ悪化した(fail-field 2→3→11)。この乖離自体が、Family Xの
  R1→R2 Entertainment revisionをFamily Y(Voice)文脈へ無条件に流用してよいかについて、
  Fable/ユーザーの判断を要する具体的な技術的根拠である。
- 判断を要する具体的論点: (a) R1→R2適用は行うが後段にmust-fixゲートを追加する
  改善案を追加Trialとして検討するか(現時点では未実装・未承認)、(b) R1→R2適用自体を
  Family Y文脈では見送るか、(c) 評価方法として今後はLLM rubric単独ではなく既存
  Family B Leakage Check必須併用とするか。

## 11. 新仕様候補・追加改善案(実装せず列挙、§8と重複する項目は§8参照)

- Revision指示への制約文追加(未実装)
- R1→R2後のmust-fix retryゲート接続(未実装、Family Y専用仕様の新設に該当するため
  ユーザー承認が必要)
- Fact Ledger形式アダプタのProduction化(未実装、候補のみ)

## 12. 実行証跡

- `.venv\Scripts\python.exe er036_family_y_voice_structure_trial_01.py --source-dir "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2" --level a2 --out-dir "er036_output/family_y_voice_structure_trial_01/ai_hiring_3v" --budget-jpy 40`
- 単体test: `.venv\Scripts\python.exe -m unittest er036_family_y_voice_structure_trial_01_test_01 -v` → 13/13 PASS
- Scoped regression: `.venv\Scripts\python.exe run_project_regression.py --pattern "er036*_test_*.py"` → collected=13 passed=13 failed=0 errors=0
- 出力先: `er036_output/family_y_voice_structure_trial_01/ai_hiring_3v/`
  (`step1_fact_selection.json`/`step2_voice_fact_assignment.json`/
  `step34_voice_writer_r1_raw.json`/`step7_r1_to_r2.json`/`r1_sections.json`/
  `r2_sections.json`/`before_sections.json`/`ledger_adapter_output.json`/
  `deterministic_metrics.json`/`qa_before/`/`qa_r1/`/`qa_r2/`/`rubric_eval.json`/
  `summary.json`/`r1_article.md`/`r2_article.md`/`audit/raw_usage_log.jsonl`)

## 13. Git

commit: (RESULT_PACKET_FY1.md参照、push後にhashを追記)
