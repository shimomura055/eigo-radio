# EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01

管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01(Lane B)。**設計修正Trial**
(Production/Trial-07/registry/Contract編集禁止、SSOT・Git禁止)。並列稼働中: Lane A
Gap Audit(読取)、Ledger Deviation Checkerコスト調査(読取、本Trial出力の一部ログを
参照)、SSOT統合。いずれも本ファイルとは無関係。

テーマ固定: "Should companies use AI to screen job applicants?"。音声は生成していない
(テキストのみTrial)。

## 0. ユーザー決定(2026-09-09)の要点

4V Trial-01/02(Business/Legal VoiceのAnalytical Leakageが3 attemptで解消せず)を受け、
今回のテーマでは4 Voicesを3 Voicesへ変更する新しい設計Trial。原因仮説:
Business/EfficiencyとFairness/Legalが具体的人物ではなく抽象的分析軸だったため、
WriterがResearch/Evidenceを人物の経験・責任として語らず数値・解説へ戻った。
3 Voices=(1) 応募者(Algieba)/ (2) 採用担当者・Hiring Manager(Erinome)/
(3) 経営者(Schedar、採用コスト・速度・会社運営・結果に責任を持つ人物)。
Fairness/Legal/HR GovernanceはVoiceから外し、Tension/Closing側の統合・制約材料とする。

## 1. Step 0: Reconciliation・3人物版Perspective Map(要点)

- 4V Trial-02の経路(`er012_editorial_b_voices_4v_article_trial_02.py`)を土台に複製
  (Trial-02自体は無変更)。design.md B-1〜B-7(`er012_output/editorial_b_voices_
  phase1_5_3v_4v_integrated_trial_03/design.md`)のうち、B-1(Comment 2/3の3V案文言)・
  B-6(3V目標尺325〜355秒)・B-7(3V Tension=共通前提→分岐点→非対称性の3段構造)を
  そのまま引用・適用。本Trialの3 Voice構成(Applicant/Recruiter・HM/Business Owner)は
  design.mdの3V-a型(Legal落とし)に相当し、design.mdはこの構成を「Applicant 1 vs
  Recruiter+Business 2の2対1陣営化リスクが高い」として非推奨としていたが、ユーザー決定は
  この既知リスクを「外部制約(fairness/bias/accountability/law)をTensionへ統合する」ことで
  緩和する新しい設計として採用したもの(design.mdの懸念を無視したのではなく、異なる緩和策で
  対応する新設計)。
- Ledger: `er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt`を
  無改変で再利用。VOICE_1/2はそのまま、VOICE_3は「効率性の立場」→「採用コスト・速度・
  会社運営・結果に個人として責任を負う経営者」へ再フレーム、VOICE_4は独立Voiceとせず
  Tension統合用の制約evidenceとして扱う。Fact Checker A'のVoice帰属opt-in免除blockは
  Trial側でVOICE_4_EVIDENCEブロックを除去した断片のみをProduction関数
  (`registry.build_voice_attribution_block()`)へ渡し、Voice 1〜3限定とした
  (Ledger Deviation Checkerには全文[VOICE_4含む]を無改変で渡した)。
- 3人物版Perspective Map:
  `er012_output/editorial_b_voices_3v_person_voice_trial_01/research/perspective_map_3v.md`
  (新規作成)。Voice 3のVoice Cardを、「効率性」という分析軸ではなく、毎週ダッシュボードを
  見て採用継続を判断し、差別が公になれば自分が矢面に立つ、という一人の経営者の具体的な状況・
  賭け金・責任として書き直した(Ledgerのevidence自体は変更せず、解釈の再構成のみ)。

## 2. Step 1: 生成結果

新規`er012_editorial_b_voices_3v_person_voice_trial_01.py`(root)。見出し6区切り
(Hook/Voice 1〜3/Tension/Closing)。物理構造の内部キーはProduction 2V正式命名
`point_one`/`point_two`を`point_three`へ1段拡張(4Vが選んだ`voice_1..4`命名とは異なる
設計選択、§9参照)。QAスキーマ(Leakage・Distinctness)は`voice_1/2/3`キーを踏襲。

| attempt | 状態 | Fact Checker A' | Ledger Deviation | Leakage Check | 備考 |
|---|---|---|---|---|---|
| 1 | OK | PASS(unsupported 0) | MINOR×1(LR不発) | flagged(voice_2, tension) | voice_2: 91%統計の前景化。tension: discovery_syntax+**制約統合不足** |
| 2 | OK | REVIEW_REQUIRED(unsupported 2) | MINOR×1(LR不発) | flagged(voice_1, tension) | voice_1: 途中で第三者事例の外部報告文に切替。tension: 同上 |
| 3(最終) | **NG_REVIEW_REQUIRED** | REVIEW_REQUIRED(unsupported 5) | MAJOR×4→3サイクルでLEDGER_COMPLIANT(deviations=0)まで解消、ただし1件`resolved=false`/`human_review_required=true`が残存 | 未実施(Fact/Ledger段階で早期リターンのためpipeline側の正式Leakage評価はスキップ) | MAX_WRITER_ATTEMPTS(3)到達。既存の安全装置(Local Rewrite human_review_required flag)により最終確定を保留 |

attempt3は既存の安全装置(Ledger Deviation Checker + Local Rewrite、無変更のProduction
primitive)が正しく機能した結果としてNG_REVIEW_REQUIREDとなった。全体を通じて自動追加retry
は行わず(MAX_WRITER_ATTEMPTS=3は既存上限どおり）、既存Gateを独自判断で回避・無効化しては
いない。

補足診断(gate外、費用¥1.14): attempt3の最終article(Local Rewrite適用後の実テキスト)に対して
`run_analytical_leakage_check_3v()`を追加で1回実行(pipelineが早期リターンしたため正式には
未実施だった箇所を、記事全体の状態把握のために診断目的でのみ実行。ゲート判定・Contract判定には
使わない)。結果: voice_1/2/3すべてがFAIL(evidence_subject等5〜6項目)、tension は
`leak_tension_constraint_integration`のみFAIL。詳細は§4参照。

## 3. 評価1〜7

**1. 3 Voiceすべてが具体的人物として成立しているか**: Voice 1(応募者)・Voice 2
(採用担当者)は4V版から継続で人物として成立。Voice 3(経営者)は本Trialの再設計により、
「毎週ダッシュボードを見て採用継続を判断し、差別が公になれば自分が矢面に立つ」という一人の
経営者として書かれ(attempt1/2本文で確認)、Analytical Leakage Check(6項目)で
**attempt1・attempt2ともにvoice_3のFAILは0件**だった(後述の対比参照)。人物として成立して
いたと判断する。

**2. 一貫して本人Perspectiveで語られているか(参考値として一人称率、成功基準にはしない)**:
最終article(attempt3)の一人称"I"出現率はVoice 1=66.7%、Voice 2=71.4%、Voice 3=66.7%
(4V版33〜50%から改善)。ただしattempt2ではVoice 1に`leak_narrator_analysis`(本人の経験
から第三者事例への切替)がFAILとして検出されており、一人称率だけでは視点の一貫性を保証
しない(定性的にも一部視点のブレを検出できた)。

**3. Research is backstage / People are on stageか**: attempt1・attempt2では、Voice 3が
数値・分析主語の文を作らず成立していた(Leakage 0件)。一方、attempt1のVoice 2・attempt2の
Voice 1では統計・第三者報告が前景化するFAILが検出され、また補足診断(attempt3最終テキスト)
ではVoice 1〜3すべてにFAILが再出現した(§4で分析)。

**4. 仮説検証**: **支持された(ただし限定的)**。4V Trial-02ではvoice_3(旧Business/
Efficiency)がMAX_WRITER_ATTEMPTS(3)を通じて一貫してDiscovery型逆戻り
([leak_discovery_syntax]等)を起こしていたのに対し、本Trialのvoice_3(経営者)は、
公式にLeakage Checkが実施された2 attempts(attempt1・attempt2)いずれも**FAIL 0件**
だった。これは「Voiceを具体的人物として再設計するとAnalytical Leakageが改善する」という
仮説を直接支持する結果である。ただし、attempt3では別の既存機構(Ledger Deviation
Checker+Local Rewrite)が、Voice 3の個人化された主張(「自分の信用」「最終責任は自分に
返ってくる」等、Ledgerに直接の根拠がない具体化)をMAJOR deviationとして検出し、その是正
過程(Local Rewriteが不確実な主張を「The cited analysis suggests that...」という
ヘッジ表現で書き換える既存パターン)が、皮肉にもDiscovery/Narrator-analysis型の文を
Voice 3へ再導入する結果になった(補足診断で確認、§4)。**「人物化はLeakageを減らすが、
Ledger忠実性の負荷を増やし、その是正過程で別経路からLeakageが再流入しうる」という
新しい相互作用が見つかった**(§9未承認候補・新規知見として記録)。

**5. Fairness/LegalをTensionへ移した外部制約統合の成否**: **不成立**。新設した
`leak_tension_constraint_integration`基準は、attempt1・attempt2・attempt3補足診断の
**3回すべてでFAIL**だった(理由: 「ニューヨーク市やEUの規制は各人物の判断や行動への
統合が弱く、地域別の法制度を説明する列挙・付け足しになっている」)。最終article本文でも
Tension末尾に "A New York City recruiter may need a bias audit... The outside rules
limit all three." という付加的な一文として現れており、3者の物語構造そのものへ組み込まれた
というより、末尾に列挙された印象が残る。**2対1の陣営化(`leak_binary_camp_split`)は
3回とも検出されず**(設計目標のうち陣営化回避は達成)、3段構造(共通前提→分岐点→
非対称性)自体は本文で認識可能だが、外部制約の「足し算では答えにならない」という統合は
Focus Module Blockの現行文言だけでは実現できていない。

**6. 賛否2対1構図の有無**: 3 attempts(attempt1・attempt2・attempt3診断)いずれも
`leak_binary_camp_split`はFAILなし。Tension本文も「応募者は判断される側、採用担当は
運用するが決定しない、経営者は決定し結果を負う」という非対称性で描かれており、単純な
2対1構図にはなっていない。

**7. Perspective Map整合・Fact Checker A'・Ledger Deviation・Overlap・尺/語数・構造整合**:
- Perspective Map整合: 目視突合の結果、article本文(Voice 1〜3・Tension)と
  `perspective_map_3v.md`のVoice Card内容(camera/video評価、91%統計、weekly
  dashboard/30%コスト削減等)は対応しており、不一致は検出されなかった。
- Fact Checker A': attempt1=PASS(unsupported 0)、attempt2=REVIEW_REQUIRED(2件)、
  attempt3=REVIEW_REQUIRED(5件、うち3件はTensionの一般化表現、1件は経営者個人の信用への
  言及、1件はNY州とNYC市の混同)。3/3 PASSだった4V Trial-02より悪化。是正フィードバック
  ループがLeakage判定のみを対象としFact Checker指摘を反映しないという既存設計(4Vと共通)が
  この悪化を止められなかった一因。
- Ledger Deviation: attempt1・attempt2はMINOR 1件ずつ(Local Rewrite不発)。attempt3は
  MAJOR 4件検出、3 Local Rewriteサイクルを尽くして全体再判定はLEDGER_COMPLIANT
  (deviations=0)まで到達したが、個別item 1件(「差別が公になれば経営者個人の信用に
  及ぶ」という主張)は3 rewrite attemptsで解決せず`human_review_required=true`が残った
  ため、pipelineはこれをNG_REVIEW_REQUIREDとして正しく報告した(既存安全装置どおり)。
- Overlap(Point Overlap QA、16→9値へ縮小、有向6+vs Hook 3): 最終articleでany_flagged
  記録済み(`point_overlap_qa_monitoring_3v.json`参照、合否判定には未使用)。Overlap
  Controls(¥0): positive control 0.907(flagged、期待どおり検出)、deterministic
  control 0.711(flagged、指標の盲点の実証、4V同水準)、negative control(既存2V実採用
  ペア)0.14(未flagged、期待どおり)、theme_vocab_dummy 0.389(閾値0.40未満、未flagged、
  4V同水準、偽陽性リスク近接は継続観察事項)。
- 尺・語数: 最終article総語数530語(soft target約330語を大幅に超過、特にTension 142語
  [目標60〜75語]とVoice 3=95語[目標55〜70語]が主要因)。換算推定尺411.7秒
  (3V目標325〜355秒の範囲**外**、4V目標380〜430秒に近い水準)。attempt1(475語・
  推定約380秒相当)・attempt2(392語・推定約330秒相当、目標内寄り)と比べ、attempt3は
  Local Rewriteによる語数増加(ヘッジ表現の追加)も一因。
- 構造整合: 6見出し・`point_one/two/three`命名は全attemptで技術的に問題なく機能した
  (`split_six_voice_sections()`が全attemptで正しく6区切りを抽出、`required_structure_
  3v_trial_review.json`はsegment_count=16・各roleちょうど1回登場をVALIDATED)。Comment
  位置(Comment1=Hook直後、Comment2/3=3V手動ドラフト、Comment4=Tension/Closing間)は
  4V・2Vと同一パターンで問題なし。

## 4. Distinctness Check(Trial継続)

- 有向6ペア(directed): 47.9秒。一括判定(batch, 3ペア同時): 14.3秒。
- direction_agreement_rate=0.933(14/15)、method_agreement_rate(一括 vs 有向)=0.933
  (14/15)。いずれも4V Trial-02(0.933/0.933)と同一水準を再現した(voice数が4→3へ
  減っても判定の一貫性は維持)。
- False positive/negative候補: 人手による個別再判定は本Trialでは実施していない
  (時間・費用の制約、Trial継続の診断値として記録のみ)。

## 5. 4V Trial-02との差分表

| 項目 | 4V Trial-02 | 3V Person-Voice Trial-01 |
|---|---|---|
| 見出し数/内部命名 | 7区切り、`voice_1..4` | 6区切り、`point_one/two/three`(QAスキーマのみ`voice_1..3`) |
| 語数(final article) | 469語 | 530語(soft target約330語を超過) |
| 推定尺 | 385.0秒(目標380〜430秒内) | 411.7秒(目標325〜355秒**外**) |
| Voice 3(旧Business/新経営者)のLeakage | 3 attempts全てFAIL(discovery_syntax等が持続) | attempt1・2は**FAIL 0件**、補足診断(attempt3最終テキスト)ではFAIL再出現 |
| Tension Leakage | 4V専用`leak_binary_camp_split`はFAILなし | `leak_binary_camp_split`は3回ともFAILなし、新設`leak_tension_constraint_integration`は**3回ともFAIL** |
| Fact Checker A' | 3/3 PASS | 1/3 PASS、2/3 REVIEW_REQUIRED |
| Ledger Deviation(MAJOR) | attempt1:1件→LR解消、attempt3:1件→LR解消(いずれも完全解消) | attempt3:4件→3サイクルで全体はLEDGER_COMPLIANTだが1件human_review_required残存 |
| Distinctness direction/method agreement | 0.933/0.933 | 0.933/0.933(同水準) |
| Overlap Controls(positive/deterministic/negative/theme_dummy) | flagged/flagged/未flagged/0.389未flagged | flagged(0.907)/flagged(0.711)/未flagged(0.14)/0.389未flagged(同水準) |
| 費用 | ¥76.6 | ¥93.63(内訳: Writer ¥90.08、QA ¥2.40、補足診断 ¥1.14) |
| attempt数 | 3(MAX到達、Leakage起因) | 3(MAX到達、attempt1-2はLeakage起因の是正、attempt3はFact/Ledger起因で早期リターン) |

## 6. Ledger Deviation Checker検索ログ(並列コスト調査タスク向け)

詳細JSON: `er012_output/editorial_b_voices_3v_person_voice_trial_01/qa/
ledger_deviation_checker_search_log.json`。要点: コード現物確認
(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)の結果、この関数
(および Local Rewrite の再チェックコールバック)は`tools=`引数を一切持たず、Web Searchを
**使用しない**(web_search_call_count=常に0)。raw usage logの実測でもこれを裏付けた。
Web Searchを実際に使用していたのはFact Checker A'(`b1prod.run_fact_checker`→
`r3.make_fact_checker_fn`、`tools=[{"type": "web_search"}]`)のみで、attempt1=6回、
attempt2=11回、attempt3=10回(response_idの完全一致で確認済み)。4V Trial-02 Reportの
「Ledger Deviation Checkerがweb_search呼び出しを行い」という記載は、実際にはFact
Checker A'の挙動を指していた可能性が高いと考えられる(本Trialでは正確な帰属を記録した)。

## 7. コスト実測・量産概算

- Writer stage(47 call、うちFact Checker A' 3回・web_search計27回込み): ¥90.08
- QA stage(18 call、Comment 1・4・Distinctness 7+1件・Overlap Controls[¥0]・
  Duration/First-person[¥0]): ¥2.40
- 補足診断(attempt3最終article、Leakage Check 1回、gate外の診断目的): ¥1.14
- **合計 ¥93.63**(上限¥150に対し十分な余裕、4V Trial-02実績¥76.6よりやや高いが、
  同水準)。
- 量産時概算: MAX_WRITER_ATTEMPTS=3をフルに消費し、かつattempt3のようにLedger
  Deviation Checker+Local Rewriteが多数のitem×cycleを要する場合、記事あたり
  約¥90〜100/本。Local RewriteのCycle数・item数が増えるほど費用は増加する
  (本Trialのattempt3は29 API callのうち大半がLocal Rewrite関連)。

## 8. Gate 4・Gate 1分類

- **Gate 4**: Production(`er012_b_family_voices_production_01.py`・
  `er012_b_family_editorial_type_registry_01.py`)・Trial-07・4V Trial-01/02は
  いずれもimportのみ(読み取り専用)で、`git status`上も無変更を確認した。SSOT・Git
  操作は実施していない。Ledger本文(`verified_fact_ledger.txt`)・
  `perspective_map.md`(4V版)も無改変。
- **Gate 1分類**: **USER_DECISION_REQUIRED**。仮説(Voice 3の人物化がAnalytical
  Leakageを改善する)は明確に支持されたが(attempt1・2でvoice_3 FAIL 0件、4Vの
  持続的FAILからの明確な改善)、(a) その人物化がLedger Deviation・Fact Checker A'の
  負荷を増大させ、Local Rewriteの是正過程で別経路からLeakageが再流入するという
  新しい相互作用が見つかった、(b) 外部制約統合(`leak_tension_constraint_
  integration`)は3回とも未達成、(c) 最終attemptはNG_REVIEW_REQUIREDで完結して
  おり「副作用なし」とは言えない、という3点により、VALIDATEDとはしない。REJECTED
  でもない(2対1陣営化は一度も起きておらず、Voice設計自体の失敗ではない)。

## 9. 未承認仕様候補一覧

- 3V Comment 2/3文言(design.md B-1手動ドラフト、registry未反映)。
- Leakage Check 3V版スキーマ(`voice_1/2/3`+新設`leak_tension_constraint_
  integration`、Trial側新規、registry未反映)。
- Pairwise Voice Distinctness Check(一括方式主・有向方式併走、正式採用は別途)。
- required_structure 3V定義(`point_one/two/three`命名方式、Production 2V命名の
  1段拡張という設計選択。4Vが選んだ`voice_1..4`命名とは異なり、両命名方式の
  優劣比較は本Trial・4V Trial双方の実測をもって今後判断する材料とする)。
- Tension外部制約の扱い(fairness/bias/accountability/lawの統合方式そのもの、
  今回の設計変更の中心。統合は未達成のまま)。
- 3V目標尺(325〜355秒)・soft target語数(約330語)は、本Trialの実測(411.7秒・
  530語、いずれも超過)により**未検証のまま反証的材料が追加された**(設計目標の
  再検討が必要な可能性、Prompt側の圧縮指示強化は未承認のため未実施)。

## 10. STOP有無

**新規知見(§3-4・§9)を報告し、Prompt原則の追加は行っていない(未承認候補として記載
のみ)。** MAX_WRITER_ATTEMPTS(3)到達後の最終状態がNG_REVIEW_REQUIRED(Fact Checker
REVIEW_REQUIRED+Ledger Local Rewrite human_review_required)であることは、既存の
安全装置(Ledger Deviation Checker+Local Rewrite、無変更)が正しく機能した結果であり、
これを独自判断で回避・上書き・追加retryすることはしていない。2対1陣営化は発生しておらず、
見出し数6は全attemptで成立、費用は上限内。以上を踏まえ、追加のPrompt変更・再生成は
実施せず、本Reportをもって結果を提示する(§8のとおりUSER_DECISION_REQUIRED)。

## 11. 新規ファイル一覧

- `er012_editorial_b_voices_3v_person_voice_trial_01.py`(新規、root)
- `er012_output/editorial_b_voices_3v_person_voice_trial_01/research/
  perspective_map_3v.md`(3人物版Perspective Map、Step 0成果物)
- `er012_output/editorial_b_voices_3v_person_voice_trial_01/`配下一式
  (b1b_run01/、b1b_run01_attempt1〜3/、qa/、summary.json、
  required_structure_3v_trial_review.json、raw_usage_log_3v_writer.jsonl、
  raw_usage_log_3v_qa_stage.jsonl)
- `er012_output/editorial_b_voices_3v_person_voice_trial_01/qa/
  ledger_deviation_checker_search_log.json`(並列コスト調査タスク向け)
- 本Report(`EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01_REPORT.md`)

## 12. 記事最終版の絶対パス

`C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_3v_person_voice_trial_01\
b1b_run01_attempt3\article.md`

(注: このattemptは§2・§8のとおりNG_REVIEW_REQUIREDで完結しており、Production採用可能な
「合格」記事ではない。仮説検証・Voice設計そのものの評価材料としては、Leakage Checkが正式
実施されたattempt1[`b1b_run01_attempt1/article.md`]・attempt2
[`b1b_run01_attempt2/article.md`]も併せて参照すべきである。)
