# EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02

管理ID: EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02(Lane B、
OPEN-131、Sonnet委任、Trial専用)。
最大Status: **VALIDATED(Trial範囲内)**。Production採用は`USER_DECISION_
REQUIRED`(ユーザー決定2026-09-09により、本Trialでも今回到達可能な最大
Statusは`VALIDATED`までで、A'をProductionへ実装しない)。

対象: Trial-01でVALIDATEDだった候補A'(Voice別evidenceタグ+「Voice本文は
出典明記不要」の明示ルール)の量産再現性を、拡張claim集合(14件)・N=5
再現性・A-Family誤爆stress test・3V/4V拡張性designで検証した。

新規生成物: `er012_multi_voice_fact_attribution_trial_02.py`(root、Trial
専用スクリプト、Trial-01を読み取りimportして拡張)、`er012_output/
multi_voice_fact_attribution_trial_02/`(実行結果、17ファイル)。本番
Fact Checker(`er002_ja_web_research_r3.py`)・Ledger Deviation Checker
(`er003_v1_en_direct_vfl_01_generate.py`)・`fact_checker_prompt_template_
r3.txt`・model routing(`er006_model_routing_contract_01.py`)・
`er010_ledger_local_rewrite_09.py`・`er012_b_family_editorial_type_
registry_01.py`は**読み取りのみ**で一切変更していない。`a2_production_
wiring_01`は参照していない(`a2_free_address_04`のarticle/fact_check.json
は読み取りのみ、claim抽出のためだけに使用)。

---

## 1. N=5再現性

同一入力(CORE 6claim+EXT 8claim=計14claim、共通Ledger evidenceブロック)
で候補A'を5回実行(`run_01`〜`run_05`)。

- false_accept: **5回とも0件**(70判定中0件)。
- false_reject: 各run 1〜2件(`run_01`〜`run_04`=1件、`run_05`=2件)、
  5回合計6件/70判定。
- REVIEW_REQUIRED(`should_still_require_review=true`)率: run毎に3/14
  〜4/14(21%〜29%)。
- claim単位の試行間一致率(5回中の多数派と一致した回数の割合): 14 claim
  平均**98.6%**(`should_still_require_review`・`classification`とも同値)。
  完全一致(5/5)は12/14 claim、4/5一致が2 claim
  (`tension_repeated_desk_use`は5/5で"要レビュー"に一致=安定して保守的、
  `control_negative_generic_opinion`は4/5一致、1回のみ"要レビュー"へ揺れた)。
- 詳細: `er012_output/multi_voice_fact_attribution_trial_02/run_summary_
  n5.json`(`agreement_report`)。Trial-01で観測された候補A/Bの大きな
  非決定性(false_reject 1件↔4-5件で揺れる)と比べ、候補A'は5回中4回まで
  同一FA/FR件数(1件)で、揺れは最小限だった。

## 2. false accept / false reject(事実誤り vs 帰属曖昧の分離)

Trial-01の6claim(A2/B1実データ+control 2件)に加え、本Trialで新規8claim
を追加(B1[trial_07]・A2[free_address_04、読み取りのみ]から抽出した実claim
+意図的に事実を改変したclaim+A-Family実claim)。

- **数値改変(`ext_fact_error_digit_voiceA`)**: Ledger実evidence(Gensler
  87%/74%)を97%/40%へ改変してVoice A一人称文に埋め込んだもの。5/5回とも
  `should_still_require_review=true`で正しく検出(false_accept 0)。
- **主体改変(`ext_fact_error_subject_change`)**: 実在しない架空調査主体・
  数値をVoice B一人称文に埋め込んだもの。5/5回とも正しく検出。
- 結論: **「Voice本文だから出典明記不要」という免除ルールを与えても、
  内容そのものが改変・捏造されている場合はUNSUPPORTED_OR_UNVERIFIEDへ
  分類され、免除の対象にならなかった**(N=5全ラン、false_accept 0件)。
  「事実が間違っている」と「帰属表現(一人称合成persona)が曖昧」という
  2軸は、この規模のTrialでは機械的に分離できていた。ただし14claim×5回
  という小規模Trialであり、より大きなclaim集合での検証は未実施(不明)。

## 3. Voice A/B/Tension/Closingの帰属(section別判定表、5run多数決)

| Section | claim | 多数決判定 | 一致率 | 正解(ground truth)と一致 |
|---|---|---|---|---|
| Hook | (Trial-01同様、対応claimなし) | - | - | - |
| Voice A(One Voice) | voiceA_desk_experience | ATTRIBUTION_ONLY_SUPPORTED / 要レビュー不要 | 100% | 一致 |
| Voice A(数値改変) | ext_fact_error_digit_voiceA | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| Voice A(実在人物引用) | ext_real_named_individual_in_voice_body | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| Voice B(Another Voice) | voiceB_seat_choice_experience, voiceB_wfh_reason | ATTRIBUTION_ONLY_SUPPORTED / 要レビュー不要 | 100% | 一致 |
| Voice B(主体改変) | ext_fact_error_subject_change | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| Voice B(negative control) | control_negative_generic_opinion | 主に要レビュー不要 | 80%(4/5) | 多数決は一致、1回のみ揺れ |
| Tension | tension_repeated_desk_use | 要レビュー(保守的維持) | 100% | ground truth(False)とは不一致だが、Trial-01と同じ「引用不足を残すべき」ケースとして意図通り |
| Tension(実在人物誤引用) | ext_real_named_individual_misquote_tension | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| Tension(positive control捏造) | control_positive_fabricated | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| Closing | (対応claimなし) | - | - | - |
| A-Family非Voice本文 | ext_afamily_uc_davis_humidity, ext_afamily_iowa_state_room_temp | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致 |
| A-Family誤ラベル(voice_a_bodyとして偽装) | ext_mislabeled_afamily_as_voice | UNSUPPORTED_OR_UNVERIFIED / 要レビュー | 100% | 一致(誤爆せず) |
| Voice 3(synthetic 3V設計テスト) | ext_synthetic_3v_voice_c | ATTRIBUTION_ONLY_SUPPORTED / 要レビュー不要 | 100% | 一致 |

## 4. Ledger evidenceとの機械的対応付け

`matched_evidence_ids`は5回とも同一のevidence ID集合(例:
`voiceA_desk_experience`→`["1-01","1-02","1-05","1-07"]`)を返し、対応
しないclaim(捏造・改変・A-Family非関連claim)には5回とも空配列を返した。
対応しないclaimの扱いは一貫して`UNSUPPORTED_OR_UNVERIFIED`。詳細:
`run_0X_result.json`。

## 5. persona一人称と実在人物claimの分離(FAリスク検証)

Trial-01では未検証だった、**実在の名前付き人物の発言を「Voice本文」の
中に埋め込んだ場合**を新規に検証した(`ext_real_named_individual_in_
voice_body`、Ledger fact_006のナイジェル・オセランド博士のコメントを
誇張・Voice A文中へ挿入)。5/5回とも正しく`UNSUPPORTED_OR_UNVERIFIED`/
要レビューへ分類され、「Voice本文=出典明記不要」というA'の免除ルールが
実在人物への具体的帰属主張まで免除してしまう、というFAリスクは**この
Trialでは発現しなかった**。同様に地の文(Tension)での実在人物(Amazon
CEO)の発言範囲誇張(`ext_real_named_individual_misquote_tension`)も
5/5回で正しく検出。ただし、この結果はプロンプト文言(「Voice本文の
一人称の語りは実在する単一個人の発言ではなく、Ledger上の複数の実evidence
を合成したもの」という前提説明)がモデルに「合成persona」と「実在人物
への具体的帰属」を区別する十分な手がかりを与えていたためと考えられ、
より曖昧な事例(実在人物名を出さずに実在の権威を仄めかす等)は未検証
(不明)。

## 6. A-Familyへ誤爆しないopt-in scope設計(非影響/誤爆stress test)

- **gating条件の実体確認**: `er012_b_family_editorial_type_registry_01.py`
  の`EDITORIAL_TYPES["b_family_voices"]["family"] == "B"`
  (`physical_structure == "five_section"`も併用可)が、既存registryに
  既に存在する。Production配線する場合、この`family`判定をA'有効化条件
  にする設計は既存構造と自然に整合する(新規追加ではなく既存フィールド
  の参照のみで済む)。
- **誤爆stress test(実測)**: A-Family実記事(`er003_output/n3_01/
  household/b1b/article.md`、単一ナレーター・第三者視点、実際の本番
  verdict=REVIEW_REQUIRED)から実際にflagされた2claim
  (`ext_afamily_uc_davis_humidity`、`ext_afamily_iowa_state_room_temp`)
  を、無関係なB-Family用Voice evidenceブロックと**同一のprompt呼び出し**
  に混在させて実行(=gatingを実装し忘れた場合の最悪ケースを模擬)。
  5/5回とも正しく`UNSUPPORTED_OR_UNVERIFIED`/要レビューへ分類され、
  無関係なVoice evidenceへの誤マッチ(false accept)は発生しなかった。
- **ラベルのみのrobustness test**: 上記household claimの一方に、section
  ラベルだけを意図的に`voice_a_body`へ偽装した版(`ext_mislabeled_
  afamily_as_voice`)でも、5/5回とも正しく`UNSUPPORTED_OR_UNVERIFIED`へ
  分類された。A'のロジックが「section名のラベル」だけでなく
  `matched_evidence_ids`(内容の対応)を要求している設計が、この5回の
  試行では機能していた。
- **限界**: これはモデルの意味理解に依存した結果であり、決定的
  (deterministic)なコードレベルの安全装置ではない。5回の試行では誤爆
  しなかったが、より多くの試行・より紛らわしい入力(座席運用と部分的に
  類似する内容等)では異なる結果になる可能性があり、**正式採用する場合は
  gatingをprompt側の意味理解だけに依存させず、`editorial_type`による
  コードレベルのオプトインを必須とすべき**という設計上の結論を支持する
  実測データが得られた(未実装、設計のみ)。

## 7. 2Vでの安定性

1節参照。5回中4回はFA/FR件数が完全に同一(0/1)で、揺れは1 claim
(negative control)のみ。Trial-01で観測された候補A/Bの大きな非決定性
(false_reject 1↔4-5件)と比べ、候補A'は明確に安定していた。

## 8. 3V/4Vへの適用可能性

- `build_candidate_a2_prompt`のprompt文言自体には「2」「二つ」等の
  Voice数を固定するハードコードは存在しない(既存確認、コード読了)。
  ため、Ledger evidenceブロックへ`VOICE_3_EVIDENCE`タグを追加するだけで
  prompt文言の変更なしに3V/4Vへ拡張できる設計と確認できた。
- synthetic design test(`ext_synthetic_3v_voice_c`、本Trialで作成した
  架空evidence1件、実データではない)を1件追加し5回実行した結果、5/5回
  とも`ATTRIBUTION_ONLY_SUPPORTED`/要レビュー不要へ分類され、Voice数への
  依存なく動作した。
- **限界**: 実データでの3V/4V検証ではなく、synthetic 1件のみの設計確認
  である(`EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-
  TRIAL-03_REPORT.md`のB-1〜B-7詳細設計ファイルは本Trialでは読んでいない、
  不明)。3V/4V実記事が生成された後の再検証が必要(未実施)。

## 9. retry/regeneration後の帰属維持

- コード確認(再確認、Trial-01と同一結論): `er010_ledger_local_rewrite_
  09.py`の`apply_rewrites()`は対象文字列を`str.replace(...,1)`で1回だけ
  置換するのみで、section見出し構造・記事全体は保持される
  (`extract_section()`が見出し行で区切る実装、Trial-01の分析と一致)。
  `er003_v1_n3_01_articles_generate.py`のFact Checker呼び出し部分
  (999〜1013行)を再確認し、`verdict="REVIEW_REQUIRED"`は引き続き
  non-blocking advisoryであり、retryを発火させないことを確認した
  (この点は無変更)。
- **retry-simulation実測(新規)**: voiceA_desk_experienceのclaim文を、
  Local Rewriteが行うような文単位の言い換え(内容不変、表現のみ変更)を
  模擬した版を作成し、原文と並べて同一Ledger evidenceブロックで1回
  分類させた。結果、両方とも`ATTRIBUTION_ONLY_SUPPORTED`/`matched_
  evidence_ids=["1-01","1-02","1-05","1-07"]`/要レビュー不要で完全一致
  (`retry_simulation_result.json`)。ただしこれは実際のLocal Rewrite出力
  ではなく本Trialで作成した模擬文であり、実際のRewrite後テキストでの
  検証ではない(不明、要追加検証)。

## 10. Cost / latency / maintainability

- N=5本実験(14claim/回): 5回合計 input 16,135 token・output 8,304
  token(内訳は各`run_0X_result.json`の`usage`)。reasoning_effort=low・
  web_search tool不使用。
- retry-simulation実験: 追加でinput 1,841 token・output 476 token。
- 合計token(14claim×5回+retry-sim 2件×1回)から`gpt-5.6-luna`単価
  (`ER-005-LLM-COST-STRUCTURE-AUDIT-01-R1_report.md`記載: Input
  $0.20/1M、Output $1.20/1M)で概算すると、本Trial-02のLLM費用は
  **約$0.017(約¥2.6、1ドル150円換算の概算)**。上限¥60に対し十分に
  収まっている。
- maintainability: Trial-01と同結論。`build_fact_check_prompt(topic,
  article_text, writer_sources)`への第4引数(Voice別evidenceブロック、
  既定None/未指定でA-Family既定挙動不変)という最小変更設計は今回も
  変える理由がなかった。追加のmaintainanceコストは、Ledgerタグ命名規約
  (`VOICE_N_EVIDENCE`)を書き手側・Ledger作成側で一貫させ続けることと、
  6節のgating(`editorial_type["family"]=="B"`)をコードレベルで強制する
  実装が必要という点(未実装)。

## 11. 既存Fact Checkerへのregression

- `er002_ja_web_research_r3.py`の`build_fact_check_prompt()`・
  `er003_v1_n3_01_articles_generate.py`の呼び出し行(978行目、
  `r3.build_fact_check_prompt(topic, article_text, [])`)を再確認し、
  Trial-01時点から一切変更されていないことを確認した(grep実測、diffなし)。
  本Trialのスクリプトはこれらの関数を一切import/呼び出ししておらず、
  Trial専用の別prompt(`build_candidate_a2_prompt`)のみを使用している
  ため、A-Family/B-Family問わずProduction経路への実行時の影響はゼロ
  (コード変更なし、かつ別関数)。
- 「A' OFF時に既存出力と同一」という回帰確認は、Production関数を無変更で
  参照したことにより自明に成立する(byte比較の実行は不要、コード上
  変更箇所がないため)。

---

## Gate 1分類

**Trial(Production変更なし)**。本番Fact Checker/Ledger Deviation
Checker/Validator/Prompt/model routing/registryを一切変更していない。
TTS・音声生成なし。`a2_production_wiring_01`は参照していない。

## USER_DECISION_REQUIRED候補

1. Trial-01・Trial-02を通じ候補A'型設計(Voice別evidenceタグ+Voice本文
   出典明記免除ルール)がN=5・14claimの規模で安定した結果(false_accept
   0/70、試行間一致率98.6%)を示したが、これをProduction採用する方向性
   自体を進めるか。
2. 採用する場合、6節で確認した「gatingをprompt側の意味理解だけに依存
   させず`editorial_type`によるコードレベルのオプトインを必須とする」
   という設計方針を、正式な実装要件とするか。
3. 8節(3V/4V拡張性)はsynthetic 1件の設計確認に留まる。3V/4V実記事が
   生成された段階で本Trialと同様の検証を再実施することを、3V/4V本体の
   USER_DECISION_REQUIREDと合わせて条件とするか。
4. 9節のretry-simulationは模擬文であり実際のLocal Rewrite出力ではない。
   正式採用前に実際のLedger Deviation Rewriteが発生した実記事での再検証
   を前提条件とするか。
5. より大規模なclaim集合(本Trialの14件を超える規模)・複数記事での
   反復検証を、正式採用の前提条件とするか。

## 費用

本Trialの新規有料LLM呼び出しは、N=5本実験(5回)+retry-simulation(1回)
の計6回。すべてweb_search tool不使用・reasoning_effort=low。合計token
使用量は10節に記載の通りで、`gpt-5.6-luna`単価から概算した費用は約
$0.017(約¥2.6)であり、上限¥60以内に十分収まっている(正確な円換算は
ダッシュボード未確認、token usageは各`run_0X_result.json`/
`retry_simulation_result.json`に記録)。TTS・ASR等の追加コストは発生
していない。

## 新規ファイル一覧

- `EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02_REPORT.md`(本ファイル、root)
- `er012_multi_voice_fact_attribution_trial_02.py`(root、Trial専用スクリプト)
- `er012_output/multi_voice_fact_attribution_trial_02/claims_all_input.json`
- `er012_output/multi_voice_fact_attribution_trial_02/combined_ledger_block.txt`
- `er012_output/multi_voice_fact_attribution_trial_02/candidate_a2_prompt_used.txt`
- `er012_output/multi_voice_fact_attribution_trial_02/run_01_result.json`〜`run_05_result.json`
- `er012_output/multi_voice_fact_attribution_trial_02/run_01_score.json`〜`run_05_score.json`
- `er012_output/multi_voice_fact_attribution_trial_02/run_summary_n5.json`
- `er012_output/multi_voice_fact_attribution_trial_02/retry_simulation_result.json`
- `er012_output/multi_voice_fact_attribution_trial_02/retry_simulation_score.json`
- `er012_output/multi_voice_fact_attribution_trial_02/retry_simulation_claims.json`

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp
