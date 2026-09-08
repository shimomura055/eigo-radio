# EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01

管理ID: EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01(Lane B、Sonnet委任、Trial専用)
最大Status: **VALIDATED(Trial範囲内)**。Production採用は`USER_DECISION_REQUIRED`。

対象: B-Family(複数Voice)構成でFact Checkerが`REVIEW_REQUIRED`を返した事例
(`er012_output/editorial_b_voices_a2_free_address_03/`、
`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/`、元Ledgerは
`er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt`)。

新規生成物: `er012_multi_voice_fact_attribution_trial_01.py`(root、Trial専用
スクリプト)、`er012_output/multi_voice_fact_attribution_trial_01/`(実行結果)。
Production Fact Checker(`er002_ja_web_research_r3.py`)・Ledger Deviation
Checker(`er003_v1_en_direct_vfl_01_generate.py`)・fact_checker_prompt_
template_r3.txt・model routing (`er006_model_routing_contract_01.py`)は
**読み取りのみ**で一切変更していない。

---

## 1. 今回なぜREVIEW_REQUIREDになったか

`er012_output/editorial_b_voices_a2_free_address_03/a2/audit/fact_check.json`
(A2)と`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/audit/
fact_check_attempts.json`(元B1)の`unsupported_specific_claims`は、B1/A2の
双方でほぼ同一内容だった。原因はB1/A2共通で構造的:

- 記事のOne Voice/Another Voice本文は、`verified_fact_ledger.txt`の
  `[VOICE_1_EVIDENCE]`/`[VOICE_2_EVIDENCE]`(複数の実調査・実報道・実
  インタビューのfact、それぞれ`verification: CONFIRMED`)を、単一の一人称
  「私」の語りへ**意図的に合成・翻案**したもの(Ledger冒頭のPerspective
  選定記述、Writer prompt `audit/writer_prompt.txt`のOne Voice/Another
  Voice指示より確認)。
- 一方、独立Web検証を行うFact Checker(`fact_checker_prompt_template_r3.txt`)
  は、記事テキスト全体を単一の対象として与えられ、「実在の当事者発言・
  調査・事例として確認できるか」を判定する。合成personaの一人称文は
  「発言者・企業・調査名が示されず実在確認できない」として機械的に
  `unsupported_specific_claims`に該当してしまう。
- これはB1(trial_07)・A2(free_address_03、B1のA2翻案)の双方、かつ
  複数回の生成attemptで再現しており、個別のランダムな失敗ではなく、
  「複合Voice設計」と「単一テキストに対する独立Web検証」という2つの
  既存機構の**設計上のミスマッチ**である。
- 例外1件(Tensionの「同じ机を頻繁に使う」)のみ性質が異なり、Ledgerには
  対応fact(1-06、MONOist 36.8%)があるが本文中に出典明示がないという、
  複合persona問題とは別の「地の文の引用不足」ケース。
- 例外1件(Hookの「パンデミックが唯一の起点」という単純化)は、複合Voice
  とは無関係な、記事前提のニュアンス上の指摘。
- 矛盾(`contradictions`)は0件であり、既存`ledger_deviation.json`も両方
  `LEDGER_COMPLIANT`。事実そのものの誤りではなく、**帰属表現**の問題である
  ことは既存出力からも確認できる。

## 2. Section別事実帰属表(要約)

| Section | 主な内容 | 対応Ledger evidence | 分類 |
|---|---|---|---|
| Hook (`hook_body`) | 座席運用の対比という前提設定 | CROSS_REFERENCE相当(明示IDなし) | 前提の単純化(軽微、attribution問題ではない) |
| Voice A (`voice_a_body`, One Voice) | 固定席への安心感・私物管理の不安等、一人称 | VOICE_1_EVIDENCE 1-01/1-02/1-03/1-05等 | 事実主張ではなく複合persona化された一人称体験。内容はLedger支持 |
| Voice B (`voice_b_body`, Another Voice) | 気分・関係性に応じた席選び、在宅勤務経験、一人称 | VOICE_2_EVIDENCE 2-01/2-02/2-03/2-04 | 同上 |
| Tension (`tension_body`) | 安定の源の違い、「同じ机の頻繁利用」への言及 | VOICE_1_EVIDENCE 1-06(地の文、出典明示なし)+ 編集的一般化 | 一部は引用不足、一部はLedgerの`role`/`why_it_matters`に基づく編集的解釈(単一factに一対一対応しない) |
| Closing (`closing_body`) | 「本当に必要なもの」への収斂 | 直接対応するevidence IDなし(Tensionの解釈の延長) | 編集的統合、fact主張ではなく解釈 |

## 3. section単位provenance利用可否

- Ledger自体(`verified_fact_ledger.txt`)は`[VOICE_1_EVIDENCE]`/
  `[VOICE_2_EVIDENCE]`/`[CROSS_REFERENCE]`というVoice別タグを既に持つ。
- ただし、この機構が実際にWriterへ渡され、section→evidence対応として
  記録されているのは**Point One/Point Two(Key Phrase系)のみ**
  (`b1b_run02_attempt2/audit/point_role_planning_initial.json`の
  `evidence_anchor`フィールド)。
- 記事本文5-section(Hook/Voice A/Voice B/Tension/Closing)の
  `writer_result.json`・`article.md`には、section→evidence idの対応を
  示す構造化フィールドは**存在しない**(プレーンテキストのみ)。
  `scaffold_summary.json`にはsection別の語数・文長統計はあるが、evidence
  IDとの対応はない。
- 結論: 「Voice別にどのevidenceを使うか」という設計上のprovenanceは
  Ledgerレベルでは既にあるが、Writer出力・Fact Checker入力としては
  **配線されていない**。これが1節の構造的原因の技術的実体である。

## 4. Ledger evidenceとの機械的対応付け(既存Fact Checkerの限界)

`er003_v1_n3_01_articles_generate.py`(B-Family呼び出し元)から
`er002_ja_web_research_r3.build_fact_check_prompt(topic, article_text, [])`
を確認。`fact_checker_prompt_template_r3.txt`は記事全文を単一textとして
渡し、独立Web検索で「具体的主張」の真偽を判定するのみで、Ledgerそのもの
(`verified_fact_ledger.txt`)も、Voice別evidenceタグも、section境界も
一切受け取らない。判定単位は「記事全体中の個々の具体的主張」であり、
section・Voice・持ち主(誰の発言か)という帰属軸は最初から評価対象外。
B-Familyの複合persona設計は、この既存アルゴリズムの前提(記事中の一人称
発言は実在の当事者発言であるはず)に反する入力を作っている。

## 5. factの正誤と「誰の主張か(帰属)」の分離可否

Trial実験(6節)の結果、分離は**部分的に可能**と分かった。Ledgerの
Voice別evidenceタグと「Voice本文は仕様上ナレーションであり逐語引用では
ない」という明示ルールを分類器へ与えると、「内容はLedgerに対応するか」
(fact軸)と「本文中に出典が明記されているか」(帰属・引用表記軸)を
概ね分けて判定できた(6節Candidate A')。既存Fact Checkerの語彙
(`PASS`/`REVIEW_REQUIRED`/`FAIL`)には元々この2軸の区別がなく、
`unsupported_specific_claims`ひとつに両方が混在している。

## 6. false accept / false reject(Trial実験)

`er012_multi_voice_fact_attribution_trial_01.py`で、A2の実`fact_check.json`
から抽出した4件の実claim + positive control(捏造した「2030年法律義務化」
主張)+ negative control(検証不能な純粋主観意見)、計6件を分類させた
(web_search toolなし、model=`routing.WRITER_FACT_CHECK_MODEL`
=gpt-5.6-luna、reasoning_effort=low、既存fact_checker_prompt_template_r3.txt
とは別のTrial専用prompt)。

- **Candidate B(主観/客観二値のみ、Ledger evidence不使用)**: ディスク
  永続化された実行(`candidate_b_result.json`)ではfalse_accept=0、
  false_reject=4/6(Voice A/B系3件を含む)。別の実行では
  false_reject=1/6と、同一promptでも試行間で結果が安定しなかった
  (`rerun_variability_note.md`参照、非決定性あり)。
- **Candidate A(Voice別evidenceタグを付与、ただしVoice本文の出典明記
  免除ルールなし)**: false_accept=0、false_reject=4/6。
  matched_evidence_idsの対応付け自体は概ね正しかったが、「本文中に出典が
  ない」ことを理由に大半をレビュー要求のままにした。
- **Candidate A'(Voice別evidenceタグ+「Voice本文は仕様上出典明記
  不要」という明示ルールを追加)**: false_accept=0、
  false_reject=1/6(残る1件はTensionの地の文における未引用の統計主張で、
  これは正しく残すべきもの)。3設計中で最良、かつfalse_accept(捏造
  claimの見逃し)は3設計とも0件。
- 詳細JSON: `er012_output/multi_voice_fact_attribution_trial_01/`
  (`candidate_{a,a2,b}_{prompt.txt,result.json,score.json}`、
  `claims_input.json`、`run_summary.json`、`rerun_variability_note.md`)。
- 限界: claim数6件・1回〜2回試行のみの小規模Trialであり、Candidate A/Bの
  非決定性が示す通り、**単発の良好な結果を安定した性能と断定できない**。
  正式採用にはより大きなclaim集合・複数回試行での再現性検証が必要
  (未実施、不明)。

## 7. 3V/4Vでも成立するか

`EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03_REPORT.md`
は既存2 Voices Productionを変更せず、3V/4V構成を追加設計する方針
(`VALIDATED(Trial範囲内)`、採用は`USER_DECISION_REQUIRED`)。同報告書
本体は詳細設計をB-1〜B-7の別ファイルへ委譲しており、本Trialの範囲では
それらを読んでいない(不明)。ただし、既存Ledgerの`VOICE_1_EVIDENCE`/
`VOICE_2_EVIDENCE`というタグ命名規則が既に番号付きである点から、
`VOICE_3_EVIDENCE`/`VOICE_4_EVIDENCE`への拡張はタグ体系上は自然に見える。
Candidate A'の分類器も、Voice数に依存したロジックを持たない(タグ→Voice
本文の対応を都度渡すだけ)ため、設計としては3V/4Vへ拡張可能と見込まれる
が、**3V/4Vの実データでの検証は本Trialでは実施していない(不明)**。

## 8. retry/regeneration後も帰属が維持されるか

`er003_v1_n3_01_articles_generate.py`を読む限り、現行のRetry機構は2種類:

- Ledger Deviation MAJOR時の局所Rewrite(`er010_ledger_local_rewrite_09.py`
  `MAX_REWRITE_CYCLES`まで): 文単位で対象文を特定・置換するのみで、
  article_text全体・section構造は保持される。Voice本文がどのevidenceに
  対応するかというLedger側の設計(taggingそのもの)は変更されない。
- Point overlap NG時の記事全体retry: `point_role_planning`を含め記事全体を
  再生成する。ただしこれはPoint One/Two(Key Phrase)用の`evidence_anchor`
  であり、Hook/Voice A/Voice B/Tension/Closingの5-section本体とは別枠。
- 重要な点: 現行実装では**Fact Checkerの`REVIEW_REQUIRED`自体はリトライを
  発火させない**(11節参照、既存ユーザーDecisionによりnon-blocking
  advisory)。したがって「retry後も帰属が維持されるか」という問いは、
  Fact Checker起因のretryには現状該当しない。Ledger Deviation由来の
  局所Rewriteに関しては、Writer側の出力に文単位の書き換えが起きても
  Ledger側のVoice別evidenceタグとの対応関係(Candidate A'方式が前提とする
  「Voice本文全体とVOICE_N_EVIDENCEの対応」)は生成単位・Voice単位である
  ため、文単位の局所修正では原則維持されると考えられる(ただし実測は
  未実施、不明)。

## 9. Cost / latency / maintainability

- 6節のTrial実験は、web_search tool不使用・reasoning_effort=low・
  6claim/1回あたり入力最大2,084 token・出力最大951 tokenで完了(詳細usage
  は各`candidate_*_result.json`の`usage`フィールド)。既存Fact Checker
  (web_search tool使用、4回のクエリ)と比べ、追加のLLM呼び出しを本番
  Fact Checkerの**前段**または**同一呼び出し内のprompt拡張**として置く
  場合、web_search回数を増やさずに済む設計が可能と見込まれる
  (Candidate A'はweb_search不使用でも機能した)。
- 実装形態としては、既存`build_fact_check_prompt(topic, article_text,
  writer_sources)`に、第4引数としてVoice別evidence blockを**オプション**
  で追加する形が最小変更になり得る(A-Familyでは空/未指定のまま呼び出せば
  既定挙動不変)。ただし、これはTrialでの設計評価であり、実装は行っていない。
- maintainability上の懸念: Candidate A'のprompt文言自体が「Voice本文は
  出典明記不要」という**新しい免除ルール**を導入するため、B-Family以外
  (単一語り手のA-Family)へ誤って適用されると、既存の検証水準を下げる
  リスクがある(11節・10節参照)。

## 10. 既存Fact Checkerを壊さないか

- 本Trialでは`er002_ja_web_research_r3.py`・`fact_checker_prompt_
  template_r3.txt`・`er006_model_routing_contract_01.py`を一切変更して
  いない(読み取りのみ)。A-Family経路への実行時の影響はゼロ(未実行の
  コード変更のため)。
- 将来Production実装する場合の非破壊案(設計のみ、未実装): Voice別
  evidence blockが空/未指定の場合は既存prompt・既存挙動と完全一致させる
  (opt-inパラメータ化)。A-Familyは元々複数Voice構造を持たないため、
  この引数が渡らない限り現行動作から変化しない、という設計方針が
  妥当と考えられる。
- 回帰テスト案(未実施): (1) 既存A-Family PASS事例に対しCandidate A'
  prompt拡張を適用し、判定がPASSのまま変化しないことを確認、(2) 既存
  A-Family REVIEW_REQUIRED/FAIL事例に対しても判定区分が変化しないことを
  確認。今回は時間・予算の都合上、Trial範囲(B-Family 6 claimの分類実験)
  に限定し、A-Family側の回帰確認は行っていない(不明、要追加検証)。

---

## Gate 1 分類

**Trial(Production変更なし)**。Production Fact Checker/Ledger Deviation
Checker/Validator/Prompt/model routingを一切変更していない。TTS・音声生成
なし。`a2_free_address_04`(並列Lane B再生成タスク)には触れていない。

## USER_DECISION_REQUIRED候補

1. 複数Voice構成のFact Checker帰属判定を機械化する方向性そのものを
   採用するか(採用する場合、どの候補設計をベースにするか)。
2. 採用する場合、Candidate A'型(Voice本文=出典明記不要というルールを
   Fact Checkerへ明示的に追加)の免除ルールを、B-Family限定でどう安全に
   スコープするか(A-Family誤爆防止の実装方式・回帰テスト範囲)。
3. 6節で観測したCandidate A/Bの非決定性(同一prompt・同一条件でも結果が
   変わった)をどう扱うか。追加検証(複数回試行での再現性測定)を正式
   採用の前提条件とするか。
4. 3V/4V拡張時の検証(7節、未実施)を、3V/4V本体のUSER_DECISION_REQUIRED
   と合わせていつ・どの単位で行うか。

## 費用

本Trialで発生した新規有料LLM呼び出しは、`er012_multi_voice_fact_attribution_
trial_01.py`による分類実験のみ(5回、うち2回は`main()`実行トリガーの
重複により意図せぬ再実行、詳細は`rerun_variability_note.md`)。すべて
web_search tool不使用・reasoning_effort=low・入力最大2,084 token/出力
最大951 tokenの小規模呼び出しで、上限¥50以内に収まっている(正確な円
換算はダッシュボード未確認、不明。usage tokenは各`candidate_*_result.json`
に記録)。TTS・ASR等の追加コストは発生していない。

## 新規ファイル一覧

- `EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01_REPORT.md`(本ファイル、root)
- `er012_multi_voice_fact_attribution_trial_01.py`(root、Trial専用スクリプト)
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a_prompt.txt`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a_result.json`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a_score.json`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a2_prompt.txt`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a2_result.json`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_a2_score.json`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_b_prompt.txt`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_b_result.json`
- `er012_output/multi_voice_fact_attribution_trial_01/candidate_b_score.json`
- `er012_output/multi_voice_fact_attribution_trial_01/claims_input.json`
- `er012_output/multi_voice_fact_attribution_trial_01/run_summary.json`
- `er012_output/multi_voice_fact_attribution_trial_01/rerun_variability_note.md`
