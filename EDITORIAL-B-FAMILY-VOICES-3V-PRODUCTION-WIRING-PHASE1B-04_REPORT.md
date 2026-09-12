# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-AND-REGRESSION

実行者: sonnet-worker(2回目のinvocation、再開。1回目はcontext上限で途中終了し
`run1_ng_review_required`として結果を保存済み)。Git操作は本Sonnetでは未実施
(別Agentがpush中のため管理ID指示に従い禁止を遵守)。SSOT(CURRENT_SPEC.md等)は
未編集(判断はFableへ委ねる)。

## 1. 背景・目的(再掲)

`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-03_REPORT.md`で、
Trial-02の`B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK`(約330行)が「3V共通の構造
原則」と「AI採用選考テーマ固有の内容」を不可分に含んでおり、切り分け基準が
未確定なため新Writer原則STOP該当と判定された。本タスクはその切り分けを
`EDITORIAL-B-FAMILY-VOICES-3V-WRITER-GENERIC-VS-THEME-SPLIT-DESIGN-01_REPORT.md`
の行単位分解に基づき正式実装し、既存の承認済みAI採用選考記事(Trial-02)を
「汎用テンプレート+テーマ別Ledger/Voice Card」経路でRegression再生成して、
汎用化が既存記事の品質を壊していないかを確認するもの。

## 2. 実装差分(git未commit、全ファイルパス)

### 2-1. 新規ファイル(前回セッションで作成済み、今回セッションで内容確認・テスト実行のみ)

- `er012_b_family_voices_writer_generic_01.py`(1184行): B-Family Voices 3V用
  汎用Writerテンプレート+パイプライン。`COMMON_EXPERIENTIAL_CLAIM_GROUNDING_
  BLOCK`(体験claim根拠付け=恒常ルール、フラグ無しで常時適用)、
  `external_constraint`引数(既定None=OFF、Tensionでの外部制約統合=任意
  パターン)。Voice Card/ThemeConfigをplain dictスキーマで受け取り、テーマ
  固有内容(固有名詞・数字)を一切含まない。6区切りparserは既存Production
  正式関数`b1prod.split_six_voice_sections()`へ委譲(独自parser不使用)。
- `er012_b_family_voices_theme_ai_screening_01.py`(175行): テーマ固有データ
  モジュール(Writer原則ではない)。Trial-02のVerified Fact Ledger・Voice
  Card 1〜3・Tension素材・外部制約素材を**無変更で転記**(新しい主張・数字を
  加えていない。今回49%/91%/87%/57%/74%の数値をTrial-02原本と突合し一致を
  確認済み)。Ledgerファイルパスも同一(`er012_output/ai_screening_ledger_
  trial_01/research/verified_fact_ledger.txt`)。
- `er012_b_family_voices_writer_generic_01_test_01.py`(248行、20テスト):
  API呼出し無し(¥0)。テンプレート組立の決定性、Voice Card注入、
  external_constraint ON/OFF切替、Ledger fragment一般化、6区切りparserの
  Production委譲、旧Trialファイル非import、を検証。

### 2-2. 既存ファイルの変更

- `er012_b_family_production_runner_01.py`: `main_b1_3v()`冒頭に独立分岐
  `stage == "write_new_theme"`を追加(既存stage分岐の**前**でreturnするため、
  既存stage[prepare/voice_check/kp_reuse/scaffold/tts/assemble/player/all]の
  挙動には無影響)。呼び出し規約:
  `python er012_b_family_production_runner_01.py write_new_theme b1_3v
  <theme_module_name> <out_dir>`。Writerのみ実行しTTSは行わない
  (新テーマの記事本体を検証する用途に限定)。

## 3. テスト結果(今回実行、runtime evidence)

`.venv/Scripts/python.exe`で実行(system pythonには`python-dotenv`が無く
ImportErrorになったため、プロジェクト用venvを使用)。

- `er012_b_family_voices_writer_generic_01_test_01.py`: **20/20 PASS**(¥0)
- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  (既存Phase1テスト、回帰確認用): **56/56 PASS**(¥0)

両方ともAPI呼出しを含まないため、今回この検証自体による追加費用は¥0。

## 4. Regressionの実行結果(前回セッションで実行済み、今回は結果の読解・比較のみ)

対象: AI採用選考テーマ、新経路(`write_new_theme`相当のWriterパイプライン)。
出力: `er012_output/editorial_b_voices_3v_generalization_regression_01/`
(+`_attempt1`/`_attempt2`/`_attempt3`)。比較対象(旧・承認済み記事):
`er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/`
(Trial-02、3V成立確認済み、Fact PASS・Ledger 0件逸脱)。

### 4-0. 前提: run1(前回invocationの試行)はNGで正しく中断されていた

`er012_output/editorial_b_voices_3v_generalization_regression_01_run1_ng_review_
required/`は前回セッションの試行で、Local Rewriteが`human_review_required:
true`を出したため`status=NG_REVIEW_REQUIRED`となり、既存の安全装置どおり
自動続行せず停止していた(独自判断でのバイパスは無し)。今回のattempt1〜3は
この試行を破棄し、新たに実行した結果である(旧試行の内容を裏口で流用して
いない)。

### 4-1. Writer retry推移(既存承認済み上限 MAX_WRITER_ATTEMPTS=3、初回+是正2回)

Analytical Leakage Checkのflagged項目に基づき是正再実行する既存機構が、
バイパスされず正しく動作した。

| attempt | flagged section(s) | fail fields |
|---|---|---|
| 1 | voice_1 / voice_3 / tension | 計7項目FAIL(discovery_syntax・evidence_memorable・numbers_foreground・binary_camp_split等) |
| 2 | voice_2 | leak_evidence_subject, leak_discovery_syntax |
| 3(採用) | voice_1 | leak_evidence_subject(1項目のみ) |

attempt3は上限到達時点でflagged項目が1件残った状態のまま最終結果として
記録された(コード内コメントどおり「Report側でUSER_DECISION_REQUIRED候補
として扱う」)。該当箇所: Voice 1本文の
`"I am not alone: 49% of working U.S. job seekers say these tools seem more
biased than human recruiters."`(文の主語がevidence寄りと判定)。

旧記事(Trial-02 attempt2、採用版)は**Leakage Check any_flagged=False**
(flagged項目0件)だった。→ **この1点は新経路の方が旧記事より弱い
(劣化候補)**。ただし1件・1文のみ、かつ既存の安全装置(3回上限)の範囲内で
処理されており、暴走や無制限retryは発生していない。

### 4-2. Fact Checker / Ledger / Point Overlap / Directional Precheck比較表

| 項目 | 旧(Trial-02 attempt2) | 新(Regression attempt3) | 判定材料 |
|---|---|---|---|
| Fact Checker verdict | PASS | PASS | 同等 |
| Ledger status | LEDGER_COMPLIANT | LEDGER_COMPLIANT | 同等 |
| Ledger deviation件数 | 0 | 1(MINOR、changed_actor、Local Rewrite対象外の軽微逸脱として残存) | 新の方がわずかに逸脱多い(劣化候補、ただしMINORでLEDGER_COMPLIANT自体は維持) |
| Local Rewrite発動 | 無し | cycle1で1件(MAJOR)を自動是正・resolved=true | 新は是正機構が正しく機能した実例(既存機構どおり) |
| Point Overlap QA(9値、監視専用) | any_flagged=False | any_flagged=False(最大overlap比率0.158、閾値0.4未満) | 同等 |
| Analytical Leakage Check | any_flagged=False | any_flagged=True(1件、上記4-1) | 新の方が弱い(劣化候補) |
| Directional Fact Precheck(Layer2、rule-based、¥0) | PASS | DIRECTION_REVIEW_REQUIRED(1件) | 要注意(下記4-3) |

### 4-3. Directional Fact Precheckの1件の内容(判定材料、機械的限界の可能性あり)

新記事Voice3に「hiring costs fell by about 30 percent」という具体的数字
入りの記述があり、これはLedger原文(日本語、「IBMは採用コストを約30%削減
したと報告されている」)と数字(30)は一致し`conflicts: []`(矛盾は検出
されず)だが、ルールベースchecker側の英語方向語彙リストが日本語Ledger文に
一致せず`reference_signals: []`(参照側に方向シグナルが検出できない)と
なり、機械的に一致/不一致を判定できないという理由で`REVIEW_REQUIRED`に
分類された。旧記事は同じ主張を「I have seen reports of faster hiring and
lower costs after AI」という数字無しの曖昧な表現にとどめており、この
checkerを作動させていない。

解釈の分かれ目: 新記事の方が「体験claim根拠付け」原則(具体的な数字への
言及)により忠実だが、そのぶんrule-based checkerの言語間ギャップ(日本語
Ledger文とのマッチング限界)を露呈させた、とも読める。**これが真の
ファクト齟齬なのか、checker側の既知の限界(誤検知)なのかはFable/ユーザー
判断が必要**(Layer 3以降の人手確認、または今回はconflicts=0件・
shared_numbers一致という事実のみ報告する)。

### 4-4. 語数tolerance(section別、上限・PASS/FAIL表)

**注記**: 3V記事の正式な「section別」語数上限はSSOT中に見当たらず(設計上の
既承認値は`design.md B-6`由来の**総語数目安 約410〜450語**のみ、
`PHASE1B-03_REPORT.md`108行に記載)。旧記事(497語)・新記事(489語、いずれも
`gen.compute_metrics()`基準)は共にこの目安を上回っており、これは今回新たに
生じた問題ではなく既存承認済み記事(旧)でも同水準で超過していた
(**同等**、新規の劣化ではない)。以下はsection別の実測語数(参考、正式
上限が無いためPASS/FAIL列は「旧との差が15語以内=同等」という本Report限りの
簡易基準で暫定表示。正式な閾値化はFable/ユーザー判断が必要):

| section | 旧(語) | 新(語) | 差 | 簡易判定 |
|---|---|---|---|---|
| Hook | 59 | 51 | -8 | 同等 |
| Voice 1(Applicant) | 79 | 84 | +5 | 同等 |
| Voice 2(Recruiter) | 86 | 80 | -6 | 同等 |
| Voice 3(Owner) | 82 | 84 | +2 | 同等 |
| Tension | 132 | 132 | 0 | 同等(完全一致) |
| Closing | 53 | 60 | +7 | 同等 |
| **合計** | **491** | **491** | **0** | 同等(markdown記号除く簡易カウント) |

### 4-5. Near-duplicate最大ratio・記事間定型句類似(判定材料、簡易diff計測)

- 記事内文同士の最大類似度(difflib.SequenceMatcher、文字ベース): 旧=0.582
  (「But the work does not end with a score.」対「If hiring slows, the
  work does not wait.」)、新=0.471。**新の方がむしろ低い(内部反復が少ない、
  同等以上)**。
- 記事間(旧 vs 新)の全文類似度: 0.164(低い。逐語コピペではなく、Voice
  Card/Ledgerが同じでも文面は独立に生成されている)。
- Closing文のみの直接比較(0.039、低い)だが、**修辞的骨格は酷似**: 両記事
  とも「Xは単に〜かという問いではない。それは誰が〜し、誰が〜し、誰が〜を
  背負うかという問いだ。これは権力(power)についての問いでもある。」という
  型を踏襲している。これは旧記事(承認済み)に既に存在していたパターンであり
  **新経路が新たに持ち込んだ劣化ではない**が、B-Family Voices全体で
  Closingの定型化が進んでいる可能性があり、Fableへ参考情報として共有する
  (SSOT変更提案はしない)。

### 4-6. Caveat文(ヘッジ表現)手動カウント

"may"/"in some cases"/"one [reported] case"/"one company"等のヘッジ・
限定表現を含む文を手動でカウント(sentence単位、複数ヘッジ語を含む文は
1件として計上):

- 旧: 10文(Hook 1、Voice1 2、Voice2 1、Voice3 3、Tension 3)
- 新: 8文(Hook 1、Voice1 3、Voice2 **0**、Voice3 1、Tension 3)

Voice2(Recruiter)で新記事はヘッジ表現が0件になっている(旧は「I may
prepare...」等2件相当)。全体件数はわずかに少ないが、致命的な断定過多には
なっていない(Fact Checker PASS済み)。判定材料として記録。

### 4-7. 体験claimの根拠付け(今回のユーザー決定1点目)

新経路では`COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`により**全テーマ共通の
恒久原則として構造的に保証**される(Voice Cardの`concrete_scene`/
`supporting_evidence`内`[VOICE_n_EVIDENCE n-xx]`タグでLedgerとの
traceabilityを持たせ、Writerへ明示指示)。旧記事(Trial-02)にも同種の
grounding(具体的な女性求職者の実例等)は存在したが、これはTrial-02の
Focus Module個別の作り込みであり、恒久ルールとして他テーマへ自動継承
される保証はなかった。**新経路の方が構造的な保証という点で改善**
(内容面の質は今回両記事とも同水準)。

### 4-8. Comment 3(「どの声が正しいか」ではない旨の表現)・3V構造成立

**本Regressionの範囲外(N/A)**。`run_writer_stage_generic()`はWriterのみを
実行しTTSは行わない設計(`PHASE1B-03`のSTOP境界=記事生成[Writer]が対象、
Comment/TTS等の下流Production stageは`main_b1_3v()`の既存stage
[prepare以降]側にあり、今回の`write_new_theme`分岐からは呼ばれていない)。
3V構造(3つの声=Perspectives、賛否二元論ではない)自体はVoice Card
(Applicant/Recruiter/Owner)3枚+Tension+Closingの6区切り構造で新記事も
成立していることをsections抽出で確認済み(4-4のsection別語数表が根拠)。

## 5. 費用(5区分、PM_GOVERNANCE 15-5準拠)

対象は「1記事(Writerのみ、TTS抜き)」のOpenAI Responses API実測(全て
Standard同期、Batch未使用)。

1. **今回実測**: ¥110.1(内訳: 前回invocationのrun1[NG、human_review_
   required、既存安全装置により正しく中断]¥32.1 + 今回採用のRegression run
   [attempt1〜3+Phase A確認]¥78.0)。本管理ID累計上限¥150に対し残¥39.9。
   今回セッションでの追加API呼出しは0件(¥0、offlineテスト実行と既存結果の
   読解のみ)。
2. **Trial特有の追加コスト**: ¥110.1のほぼ全額(このRegression自体が
   「汎用テンプレートが機能するか」を検証するTrialであり、通常運用の
   ベースラインが別途存在しない)。うちrun1(¥32.1、NG破棄)+採用run
   attempt1・2(¥24.3+¥28.3=¥52.6、Leakage Check是正retryで破棄)の
   計¥84.7が「1回で通れば発生しなかった」Trial特有の上振れに相当。
3. **異常retry・Human Review由来の上振れ**: run1の¥32.1
   (human_review_required発動、既存機構どおりの安全側停止であり
   バイパスしていない)。採用run内のattempt1・2(¥52.6)は
   MAX_WRITER_ATTEMPTS=3の枠内の設計どおりのretryであり「異常」には
   分類しない。
4. **Standard同期での1記事あたりコスト**: 最終採用分のみ(Phase A確認
   ¥2.4+attempt3¥23.1)=**¥25.5**(retryが発生しなかった場合の見込み値)。
5. **Batch量産換算時のコスト**: gpt-5.6-luna(OpenAI Responses API)の
   Batch単価は`pricing_snapshot.json`に未収録(Batch tierは現状Gemini系
   TTS/text-genのみ記載、Standard比50%オフの前例あり)。**確認値ではなく
   参考値**として、一般的な50%割引を仮定すると¥25.5×0.5≈¥12.8程度。
   正式なBatch単価確認が必要な場合は別途調査が必要(本Reportでは未確認と
   明記する)。

## 6. Status(判定材料の要約、判定語自体はFableが確定)

- 実装・offlineテスト: **完了・全PASS**(20/20、56/56、¥0)。
- Regression: **status=OK**(Fact Checker PASS、Ledger LEDGER_COMPLIANT)
  だが、旧記事(承認済み)と比べて以下の弱化候補が残る:
  (a) Analytical Leakage Check flagged 1件が上限到達まで未解消のまま
      最終記録された(4-1)、
  (b) Ledger MINOR逸脱1件が残存(4-2)、
  (c) Directional Fact Precheckが1件REVIEW_REQUIRED(4-3、rule-based
      checkerの言語間ギャップの可能性あり、真の齟齬かは未確認)。
- 一方、体験claim根拠付けの恒久ルール化(4-7)・Point Overlap同等・
  内部文重複が旧より少ない(4-5)など改善/同等点もある。
- 上記(a)(b)(c)は「USER_DECISION_REQUIRED」候補としてコード側にも
  明示コメントがあり、Sonnet側では独自に合否判定をしない
  (既存Gate/安全装置の枠内での挙動であり、無効化・バイパスはしていない)。

## 7. CURRENT_SPEC.md 3V節への追記文案(Fable判断待ち、Sonnet側では編集していない)

> B-Family Voices 3V用Writerを「汎用テンプレート
> (`er012_b_family_voices_writer_generic_01.py`)+テーマ別データモジュール
> (`er012_b_family_voices_theme_*_01.py`)」へ正式分離した
> (PHASE1B-04、2026-09-12)。恒久Writer原則として「体験claimの根拠付け」を
> 追加(常時適用)。「Tensionでの外部制約統合」は任意パターン
> (`external_constraint`引数)として実装、恒久ルール化はしていない。
> 既存承認済みAI採用選考記事(Trial-02)によるRegressionでは、Fact
> Checker PASS・Ledger LEDGER_COMPLIANTを維持したが、Analytical Leakage
> Check・Directional Fact Precheckで旧記事には無かった軽微な指摘が残存
> (詳細`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04_
> REPORT.md`4節)。Production採用可否はユーザー承認待ち
> (`APPROVED_FOR_PRODUCTION`未取得)。

## 8. 変更ファイル一覧(すべて未commit、Git操作はSonnet側で未実施)

- 変更: `er012_b_family_production_runner_01.py`
- 新規(untracked): `er012_b_family_voices_writer_generic_01.py`、
  `er012_b_family_voices_theme_ai_screening_01.py`、
  `er012_b_family_voices_writer_generic_01_test_01.py`
- 新規artifact(untracked): `er012_output/editorial_b_voices_3v_
  generalization_regression_01/`(+`_attempt1`/`_attempt2`/`_attempt3`/
  `_attempt_history.json`/`_run1_ng_review_required/`)
- 一時ファイル: `docs/pm/ACTIVE_TASK_3V_1B04.md`、
  `docs/pm/RESULT_PACKET_3V_1B04.md`

他Agent成果物(`er011_open121_*`、`er003_audio_tts_asr_safety.py`、
`er011_output/discovery_*`、`er011_output/family_a_trend_*`、
`docs/pm/ACTIVE_TASK_ER009.md`等)には一切触れていない。

## 修正1回目(管理ID末尾-04-GENERALIZATION-AND-REGRESSION、Fable指示によるSonnet再委任)

実行者: sonnet-worker(Fable修正指示1回目)。Git操作は未実施(禁止指示遵守)。
SSOT(CURRENT_SPEC.md等)は未編集。追加API呼び出しは今回0件(¥0、既存artifact
の読解・diff・offlineテストのみ)。

### 9-1. (a) Analytical Leakage Check flagged 1件の原因切り分け

flagged実文(採用版=attempt3、Voice 1本文の一部):
> "I am not alone: 49% of working U.S. job seekers say these tools seem more
> biased than human recruiters."

判定: `leak_evidence_subject`(FAIL、文の主語が"49%..."という統計寄りになって
いる)。checkerのreasoningは「最後の文ではパーセンテージが文の主語になって
いる」。

**汎用テンプレートの差分が原因か**: 旧Trial-02の最終prompt(attempt2用、
是正メモ込み)と新Regressionの最終prompt(attempt3用、是正メモ込み)を全文diff
した結果(367行、うち構造的に意味のある差分は下記(i)〜(iii)):

- (i) 体験claim根拠付け原則の文言: 「3人全員に等しく適用してください」→
  「全Voiceに等しく適用してください」の言い換えのみ。原則の意味・強さに
  変更なし。根拠説明を誘発する要因なし。
- (ii) disputed 2ブロック(Tension 3a/3b構造)の扱い: 旧「3a. 非対称性」→
  新「3. 非対称性」への番号振り直しのみ(4要素→3+3bの表記変更)。3bの
  外部制約統合の本文指示は語一致で完全に同一(diffで無変更確認)。
- (iii) Voice Card 1の「Supporting evidence」文言はほぼ完全一致
  (49%統計の記述・「最大1つの具体的な数字だけを、人を主語にした自然な
  話し言葉で織り込んでください」という指示も同一)。**唯一の違いは参照先の
  言葉**: 旧「(詳細ルールは下記【Voice内の数字】参照)」→新「(詳細ルールは
  上記【Evidenceは脇役であること】参照)」。新版でも実際のセクション順序は
  旧と同じ(Voice Card群が先、当該詳細ルール節が後)なので、正しくは
  「下記」であるべきところ「上記」に誤記されている(コピー時の誤記、
  参照先ドキュメント自体は削除されていない)。この誤記が生成結果に影響した
  可能性は低いと判断する(LLMはプロンプト全文を読むため、方向語の誤りが
  実際の参照失敗を起こす根拠は無い)。

→ **該当なし。「run分散の可能性」と判定する。** 根拠:
Trial-02自身の**attempt1**(旧記事の最初の下書き、後にattempt2で自己是正済み)
でも、ほぼ同一の失敗が既に発生していた:

> Trial-02 attempt1、Voice 1 flagged(`leak_evidence_subject`):
> "Nearly half of working U.S. job seekers see AI hiring tools as more
> biased than people."

これは新記事のattempt3で検出された49%統計文と同じ「Voice 1の49%統計を
主語に使ってしまう」という、この特定のVoice Card(1つ目の49%統計)に対する
モデルの再現性のある傾向であり、汎用化によって新たに生まれた問題ではない。
違いは、旧Trial-02はMAX_WRITER_ATTEMPTS=3のうちattempt2(2回目)で解消
できたのに対し、新Regressionはattempt1(voice_1/voice_3/tension、7項目)→
attempt2(voice_2)→attempt3(voice_1、1項目)と、**全文書き直し
("ゼロから新しく書き直してください"、旧新で文言同一)**の性質上、
一度直った箇所が別のattemptで再発しうるという既存の(旧新共通の)retry
設計の挙動により、たまたま上限到達時点まで1件残った、という差(run分散)
である。既存の安全装置(3回上限)は無効化・回避されておらず、コード内
コメントどおりUSER_DECISION_REQUIRED候補として記録されている。

### 9-2. (b) Ledger MINOR逸脱(changed_actor)の原因切り分け

flagged実文(採用版=attempt3):
> "I prepare an audit summary and notice, as required under New York City
> rules."
> Ledger該当行(判定理由): 「Ledgerが確認しているのは、雇用主・人材紹介
> 会社が監査結果の要約を公開し応募者に通知すること、およびNBCUniversalの
> 企業運用例であり、個々の採用担当者が自ら作成することまでは確認して
> いない。」(severity=MINOR、changed_actor=true)

Voice Card 2の該当テキスト(旧新で完全一致、diffで無変更確認)は
「実際に大手雇用主(NBCUniversal)がニューヨーク市の法律に基づき...独立
監査を受け、その結果を公開している実例がある」であり、企業主体の実例を
一人称Voiceへ落とし込む際の主体のズレは、Voice Card文言そのものの差では
説明できない。

判定材料(run分散の裏付け): 新Regression run自体の**attempt2**でも、
同種のMINOR逸脱が2件発生していた(1件はまさに`changed_actor=true`、
Hiltonの採用期間短縮という特定企業事例を「I have seen hiring move from
weeks to days」という一人称の直接経験であるかのように表現したもの)。
一方、旧Trial-02はattempt1・attempt2とも`deviations: []`
(LEDGER_COMPLIANT、逸脱0件)だった。

**重要な訂正(9-3と合わせて本REPORT 4-2の記載を修正)**: 旧Trial-02の
採用版(attempt2)の`audit/local_rewrite_results.json`を実際に確認した
ところ、本REPORT4-2表の「Local Rewrite発動: 無し(旧)」という記載は
**誤りだった**。旧attempt2でも実際にはcycle1でLocal Rewriteが1件
(MAJOR、`changed_actor`含む5フラグ)発動し、自動是正・`resolved: true`に
なっていた(該当文: "The applicant cannot choose the system; the
recruiter runs it but cannot adopt it; the owner decides." →
"...the recruiter runs it and may also help decide whether to adopt it;
the owner may make the final call.")。これは新Regression run(attempt3)の
Local Rewrite該当文("Power is uneven: the applicant cannot choose, the
recruiter operates, and the owner decides." → "Power can be uneven: in
some cases...")と**ほぼ同一パターン(Tensionの権限構造断定→ヘッジ表現への
是正)**であり、Local Rewrite機構自体は旧新で対称的に機能している。

→ **判定: run分散の可能性が高い(汎用化由来と断定する根拠は無い)。**
Voice Card本文に差がなく、MAJOR相当の逸脱パターンはLocal Rewriteで
旧新とも同様に自動是正されている。新のみ残ったMINOR 1件(changed_actor)
は、Local Rewriteの対象外(MAJORのみ自動是正、MINORは記録のみで残存する
既存仕様)の範囲内の挙動であり、これも既存の安全装置の回避ではない。

### 9-3. (c) Directional Fact Precheck 1件の再判定

実文(採用版=attempt3、Voice 3):
> "I have seen one reported case where hiring costs fell by about 30
> percent."
Ledger該当文(日本語): 「IBMは採用コストを約30%削減したと報告されている。」

`directional_fact_precheck.json`の実際の値: `conflicts: []`
(矛盾は検出されず)、`shared_numbers: ["30"]`(数字は一致)、
`reference_signals: []`(Ledger側=日本語文から、checkerの英語方向語彙
リストが方向シグナルを検出できなかった)、`candidate_signals`は英語側の
"fell"(magnitude=low)のみ検出。`reason`: 「片方にのみ方向表現があり、
機械的に一致/不一致を判定できない」。

判定: **誤検知(checker側の言語間ギャップ)の可能性が高い、判定材料として
報告する。** 根拠: 数字(30)は一致し矛盾は0件。旧記事(Trial-02)は
同じLedger根拠を"I have seen reports of faster hiring and lower costs
after AI"という数字なしの曖昧な表現にとどめたため、このrule-based
checker自体が起動しなかった(`overall_status: PASS`, `results: []`、
=判定対象ゼロ件であり、旧記事が「正しく方向性を検証されてPASSした」
わけではない)。つまり旧新の差は、新記事が「体験claimの根拠付け」原則に
より忠実に具体的な数字を使ったことで、日本語Ledger原文との方向語彙
マッチングという既存checkerの技術的限界(英語方向語彙リストが日本語の
「削減した」を認識しない)を初めて露呈させた、という構図であり、汎用
テンプレートのWriter指示自体に起因する劣化ではない。checker側の改修は
本タスクの権限範囲外(Trial検証用の別コンポーネント)のため実装しない。
最終判定はFable/ユーザーへ委ねる。

### 9-4. failure mode一般化と最小修正(実装は転記漏れの復元のみ)

上記(a)(b)(c)はいずれも「汎用化由来」と断定できる根拠が見つからず、
「run分散(モデルの確率的挙動+全文書き直しretry設計の既存の性質)」と
判定する。ただし、prompt全文diffの過程で、汎用化時の**転記漏れ**を1件
発見した:

**転記漏れ内容**: 旧Trial-02の【禁止事項まとめ】には以下の1文があったが、
新汎用テンプレートの同セクションには存在しなかった(3bの本文指示自体は
両方に残っており、内容としての完全消失ではなく、チェックリストとしての
再掲が抜けていた):
> 旧: "Tensionで外部制約(fairness/bias/accountability/law)を列挙・解説の
> リストにすること(Tensionの自然な流れの中に1〜2件だけ、人を主語にした
> 話し言葉で織り込むこと)"

この項目は、直接は(a)(b)(c)いずれの原因でもない(採用版attempt3の
Tension leakage checkは`leak_tension_constraint_integration: PASS`済み)
が、「テーマ固有→汎用に分離する際に、本文中の指示は残っても、末尾の
禁止事項サマリーへの再掲が抜け落ちる」という一般化しやすい失敗の型として
記録する。**明らかな転記漏れ**と判断し、以下のとおり復元を実施した
(実装、diffで提示。Writer/Prompt原則そのものの変更ではなく、既存原則の
再掲を戻すのみ):

`er012_b_family_voices_writer_generic_01.py`:
- `TENSION_EXTERNAL_CONSTRAINT_PROHIBITION_BULLET`(新規定数)を追加し、
  `external_constraint`有効時のみ【禁止事項まとめ】へ
  `{tension_external_constraint_prohibition_block}`として注入
  (無効時は空文字列、既存の`tension_external_constraint_block`/
  `tension_self_check_block`と同じON/OFFパターンに揃えた)。
- 復元後の文言(theme固有の"fairness/bias/accountability/law"という
  例示語は、他の3b関連ブロックと同様にテーマ非依存の表現へ一般化):
  "- Tensionで外部制約(evidenceとして与えられた規制・監査・中止/提訴
  事例等)を列挙・解説のリストにすること(Tensionの自然な流れの中に
  1〜2件だけ、人を主語にした話し言葉で織り込むこと)"
- offlineテスト再実行: 20/20 PASS(新規)・56/56 PASS(既存Phase1)、
  いずれも¥0。既存の`test_off_omits_3b_and_self_check`
  (`external_constraint`無効時の非包含テスト)も無変更でPASS
  (今回の追加ブロックも無効時は空文字列のため抵触しない)。

「上記/下記」誤記(9-1(iii))は転記漏れ(内容の欠落)ではなく参照方向の
誤記のみのため、今回は復元(修正)の対象にしていない(必要であれば
別途ユーザー判断)。

### 9-5. N+1 Regression: 費用超過見込みのため未実行(STOP、見積り報告)

管理ID指示: 「1回のRegression再実行が残額に収まらない見込みなら実行せず
STOPし見積りを報告」に従い、**今回は実行していない**。

見積り根拠(実測値):
- 1attemptあたりの実測コスト: 新Regressionのattempt1=¥24.3、attempt2=
  ¥28.3、採用attempt3+Phase A確認=¥25.5(内訳¥2.4+¥23.1)。
- 過去2回のフルRegression実行はいずれも複数attemptを要した
  (旧Trial-02: 2/3、新Regression: 3/3上限到達)。1attemptで確定PASSした
  実績は無い(0/2)。
- そのため、N+1を1回実行した場合の費用見込みは**¥25.5(最良ケース、
  1attemptで確定)〜約¥78(直近実績、3attempt上限到達)**、単純平均でも
  約¥50超と見込まれる。
- 残額は**¥39.9**であり、最良ケース(¥25.5)なら収まるが、過去実績
  (2/2回とも複数attempt)を踏まえると「収まらない見込み」の方が高いと
  判断し、独自判断で実行しない。

**参考(追加費用なしで得られる代替エビデンス)**: 既に実データとして
新Regression run内のrun1(NG、discarded)+attempt1+attempt2+attempt3の
計4サンプルが存在し、(a)(b)ともに複数attemptにまたがってflagged箇所が
voice_1→voice_3→tension→voice_2→voice_1と分散して出現・解消・再発する
という「run分散」を示す挙動が既に観測できている(9-1・9-2参照)。追加の
N+1実行なしでも、上記9-1〜9-3の判定材料は成立すると考えるが、実際に
「4の復元適用後」のN+1で(a)(b)(c)が再現するかどうかまでは未確認であり、
これは追加予算が承認された場合にのみ実行可能。

### 9-6. 費用(5区分)

1. **今回実測**: ¥0(追加API呼び出し0件、既存artifactの読解・diff・
   offlineテストのみ)。本管理ID累計は前回までと変わらず¥110.1/上限¥150
   (残¥39.9)。
2. **Trial特有の追加コスト**: 変動なし(前回までの¥110.1のまま)。
3. **異常retry・Human Review由来の上振れ**: 変動なし。
4. **Standard同期での1記事あたりコスト**: 変動なし(¥25.5、前回同様)。
5. **Batch量産換算時のコスト**: 変動なし(未確認、参考値¥12.8程度)。

### 9-7. Status(判定材料の要約、判定語自体はFableが確定)

- (a)(b)(c)いずれも「汎用化由来」と断定できる根拠は見つからず、
  「run分散(既存のretry設計・モデルの確率的挙動)」との判定材料が
  優勢(9-1・9-2)。(c)はcheckerの言語間ギャップによる誤検知の可能性が
  高い(9-3)。
- 転記漏れ1件(禁止事項まとめの外部制約列挙禁止の再掲)を発見し復元済み
  (9-4、offlineテスト20/20+56/56 PASS、¥0)。これは(a)(b)(c)の直接原因
  ではない。
- 旧Trial-02自体にもLocal Rewrite発動(1件、MAJOR、changed_actor含む)が
  あったことが判明し、本REPORT4-2表の「旧: Local Rewrite発動無し」は
  誤りだったため9-2で訂正した。
- N+1 Regression(実際の再現確認)は費用見込みが残額¥39.9を超える可能性が
  高いため未実行。実行するには追加予算承認が必要。
- 最終的な合否判定・追加予算承認・4の復元を含めたN+1実行の要否は
  Fable/ユーザー判断。

### 9-8. 変更ファイル一覧(修正1回目、すべて未commit)

- 変更: `er012_b_family_voices_writer_generic_01.py`(9-4の転記漏れ復元、
  diff内容は9-4記載のとおり)
- 変更なし(読解・diffのみ): `er012_b_family_voices_theme_ai_screening_01.py`、
  `er012_output/editorial_b_voices_3v_generalization_regression_01*/`、
  `er012_output/editorial_b_voices_3v_person_voice_trial_02/`
- 一時ファイル: `docs/pm/ACTIVE_TASK_3V_1B04.md`、
  `docs/pm/RESULT_PACKET_3V_1B04.md`(追記)

他Agent成果物には今回も一切触れていない。Git操作は未実施(禁止指示遵守)。

## 修正2回目(N+1実行、Fable指示によるSonnet再委任、費用上限¥230への延長を承認済み)

実行者: sonnet-worker(Fable修正指示2回目)。Git操作は未実施(別Agentがpush中
のため禁止指示を遵守)。SSOT(CURRENT_SPEC.md等)は未編集。既存の
`MAX_WRITER_ATTEMPTS=3`・Local Rewrite上限・Directional Fact Precheck等の
既存安全装置はバイパスせず、既存の`write_new_theme`エントリポイント
(`python er012_b_family_production_runner_01.py write_new_theme b1_3v
er012_b_family_voices_theme_ai_screening_01 <out_dir>`)をそのまま1回実行した
(9-4で復元した`TENSION_EXTERNAL_CONSTRAINT_PROHIBITION_BULLET`を含む現行
コードのまま、人為介入なし)。出力先: `er012_output/editorial_b_voices_3v_
generalization_regression_01_n2/`(+`_n2_attempt1`/`_n2_attempt2`/
`_n2_attempt3`)。採用版=attempt3(上限到達)。

### 10-1. (a) Analytical Leakage Check: 再現あり(件数はむしろ悪化)

採用版(attempt3)で`any_flagged=True`、2件(旧=0件、新1回目=1件)。

- voice_1(fail: leak_evidence_subject, leak_numbers_foreground,
  leak_discovery_syntax)引用: "About half of working U.S. job seekers see
  these tools as more biased than human recruiters."
- voice_2(fail: leak_evidence_subject, leak_numbers_foreground,
  leak_discovery_syntax)引用: "About 90% of HR leaders say they use AI
  somewhere in hiring."

Attempt推移: attempt1 flagged=voice_2(3項目)→attempt2 flagged=voice_3(2項目)
→attempt3(採用、上限到達)flagged=voice_1+voice_2(各3項目)。新1回目
(voice_1→voice_2→voice_1)と同様、flagged箇所がattemptごとに異なるVoiceへ
分散する挙動が再度観測された。**(a)は3回中3回とも何らかの形でflagged項目が
残る**という点で一貫しているが、具体的にどのVoice・どの引用文がflagされるかは
run間で一致しない。

### 10-2. (b) Ledger MINOR逸脱: 再現なし

採用版(attempt3)の`ledger_deviation.json`は`deviations: []`・
`overall_status: LEDGER_COMPLIANT`(0件)。新1回目の1件(MINOR、changed_actor)
は再現しなかった。全3attemptを通じても逸脱0件(旧記事と同水準)。

### 10-3. (c) Directional Fact Precheck: 再現なし(全attempt PASS)

全3attemptで`overall_status: PASS`・`results: []`。新1回目の1件
(REVIEW_REQUIRED、30%数字)は再現しなかった。

### 10-4. 新規に観測された相違点: Fact Checker verdictがREVIEW_REQUIREDへ

旧記事・新1回目はいずれも`verdict: PASS`だったが、今回の採用版(attempt3)は
`verdict: REVIEW_REQUIRED`(`contradictions: []`、矛盾は0件)。指摘された
`unsupported_specific_claims`は3件すべてVoice本文ではなく地の文
(Tension/Closing)の一般化・解釈的主張:
1. "All three want the same result: the right person in the right job."
   (3者共通の目的の断定)
2. "Their power is uneven: the applicant is judged, the recruiter operates
   but does not choose the tool, and the owner chooses it and owns the
   result."(役割・権限関係の一律断定)
3. "AI has made hiring a shared decision with unequal power and risk"
   (記事全体からの解釈的結論)
`notes`欄には「Voice本文の具体的主張はLedgerと実質的に一致する範囲では
未裏付けとして計上していない。問題は主に地の文の普遍的な断定と解釈にある。
明確な事実矛盾は確認できないためFAILではない」と明記されている。**これは
今回指示された(a)(b)(c)のいずれとも異なる第4の指摘であり**、事前に
Fableから再現確認を求められた3項目とは別に、新たなrun分散の実例として
記録する(3個体すべてが異なる箇所でチェッカーに引っかかっている)。

### 10-5. Point Overlap QA・Directional・Local Rewrite・retry回数

- Point Overlap QA(監視専用、9値): `any_flagged=False`、最大overlap比率
  0.154(旧0.158、新1回目0.158と同等以下)。
- Local Rewrite発動: **0回**(全3attempt、`local_rewrite_cycles: []`)。
  新1回目は1回(MAJOR)発動していたが、今回は発動なし。旧記事(Trial-02)も
  実際には1回発動していた(9-2訂正済み)ため、3個体で「発動0/1/1」と
  ばらついており、これも一貫した傾向ではない。
- Writer retry回数: 3/3(上限到達、既存承認済み上限内、バイパスなし)。
  新1回目も3/3で同一。

### 10-6. Comment 3・Voice Card準拠・体験claim根拠付け・3V構造

新1回目と同じく`write_new_theme`はWriterのみでComment/TTS等の下流stageを
実行しないため、Comment 3表現の検証は**本Regressionの範囲外(N/A)**。3V
構造(Hook+Voice1〜3+Tension+Closingの6区切り)は今回もsection抽出で成立を
確認。Voice Card準拠は同一theme moduleを無変更で使用しているため構造的に
維持。体験claim根拠付け(`COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`)も
同一テンプレート機構のため新1回目と同様に常時適用(内容面の当たり外れは
10-1〜10-4のcheckerの指摘として現れている)。

### 10-7. 必須5項目

**(i) section別語数表**(本Report独自の簡易regexカウント、
`[A-Za-z']+`マッチ数。既存`gen.compute_metrics()`の総語数とは方式が異なる
別集計であることに注意。参考として`metrics.json`の総語数も併記):

| section | 旧Trial-02 | 新1回目(regression) | 新N+1 |
|---|---|---|---|
| Hook | 60 | 50 | 46 |
| Voice1(Applicant) | 81 | 84 | 87 |
| Voice2(Recruiter) | 91 | 81 | 79 |
| Voice3(Owner) | 82 | 83 | 74 |
| Tension | 132 | 133 | 129 |
| Closing | 54 | 60 | 57 |
| **簡易合計** | **500** | **491** | **472** |
| `metrics.json`総語数(参考、別方式) | 488 | 462 | 470 |

3個体とも410〜450語の設計目安(`design.md B-6`)を上回る点は共通(新規の
劣化ではない、PHASE1B-04本文4-4と同じ結論)。

**(ii) near-duplicate最大ratio**(記事内、difflib.SequenceMatcher文字ベース、
本Report独自計測): 新N+1=0.590(該当文: "I do not choose the system; it
chooses what part of me counts." 対 "I did not choose the final system, but
I face its questions."、いずれもVoice1・Voice2内の類似修辞)。旧=0.582、
新1回目=0.471。**新N+1が3個体中最も高い**(内部反復がやや増えているが、
致命的な逐語重複ではない)。

**(iii) caveat文(ヘッジ表現)手動カウント**("may"/"one company"等、文単位):
新N+1 = 6文(Hook 2、Voice1 2、Voice2 **0**、Voice3 **0**、Tension 2、
Closing 0)。旧=10文(Hook1/V1 2/V2 1/V3 3/Tension 3)、新1回目=8文
(Hook1/V1 3/V2 0/V3 1/Tension 3)。**Voice2(Recruiter)のヘッジ表現0件は
新1回目・新N+1の両方で再現**しており、これは単発のrun分散ではなく
Recruiter Voice Card/Ledger fragmentの内容そのものに起因する可能性がある
(判定はFable/ユーザー判断、Sonnet側では断定しない)。

**(iv) 記事間定型句類似(Trial-02 vs 新2本のHook/Closing)**: 文字ベース
ratioは全て低い(Closing: 旧vs新1回目=低、旧vs新N+1=0.034、新1回目vs新
N+1=0.067、Hook: 旧vs新N+1=0.022、新1回目vs新N+1=0.072)が、**Closingの
修辞的骨格(「Xは単に〜かという問いではない。それは誰が〜し、誰が〜し、
誰が〜を負うかという問いだ。これは権力についての問いでもある」という型)は
旧・新1回目・新N+1の**3個体すべて**で踏襲されている**(例: 新N+1
"The real question is not only whether a machine can sort applications. It
is who gets a fair chance, who can ask why, and who carries responsibility
when the process fails. AI has made hiring a shared decision with unequal
power and risk...")。Hookも「An application が処理される→Software
may/canが résumé/test/video を score/scan/judge→3人が同じ場面に立つ」という
型が3個体で共通。これらは文字レベルの逐語コピペではなく、Focus Module/
Closing・Hook生成指示に由来する**構造的なテンプレート再現**であり、
汎用化固有の劣化ではなく元々Trial-02設計時から存在するパターンと解される
(4-5と同じ結論、今回3個体目でも継続)。

**(v) 音声layer**: **未実施**(`write_new_theme`はWriterのみでTTSを呼ばない
設計、新1回目と同じ)。

### 10-8. 判定材料の整理(判定語自体はFableが確定)

- (a)Analytical Leakage: **3回中3回(旧含めれば実質的には新2本)で
  flagged項目が残る**という点では一貫するが、flagされる具体的なVoice・
  引用文はrunごとに異なる(voice_1→voice_1+voice_2など)。「新テンプレート
  だから常にvoice_Xが弱い」という固定パターンは確認できない→**run分散の
  裏付けが優勢**、ただし「新経路は旧より弱い」こと自体は2/2回で再現。
- (b)Ledger MINOR逸脱: 新1回目のみで発生、新N+1では0件(旧と同水準)。
  **再現なし→run分散の裏付け**。
- (c)Directional Fact Precheck: 新1回目のみREVIEW_REQUIRED、新N+1は
  全attempt PASS。**再現なし→run分散の裏付け**(9-3のcheckerの言語間
  ギャップ説と整合)。
- 新規: Fact Checker verdict自体が新N+1でREVIEW_REQUIRED化(旧・新1回目は
  PASS)。指示された3項目とは別だが、**「3個体すべてが毎回異なる箇所で
  何らかのcheckerに引っかかる」という意味では(a)と同じ「run分散」パターンの
  一部**と読める。
- Voice2(Recruiter)のcaveat文0件は新1回目・新N+1の2/2回で再現。これは
  他の項目と異なり**テンプレート/データ内容由来の可能性がある**候補として
  分けて記録する。

### 10-9. 費用(5区分、PM_GOVERNANCE 15-5準拠)

算出方法: `raw_usage_log_writer.jsonl`(15件、全attempt+Phase A確認含む)の
`input_tokens`/`output_tokens`/`cached_input_tokens`/`web_search_call_count`
実測値を`pricing_snapshot.json`記載単価(input$0.20/1M、cached$0.02/1M、
output$1.20/1M、web_search $10/1000件)で計算(USD建て、実測合計
input=274,991・output=84,740・cached=8,942・web_search=18件、
コスト$0.335)。JPY換算レートは本REPORT既存記載値(新1回目のregression実測
¥78.0÷同ロジックで算出したUSD$0.4874から逆算した約¥160/$)を継続適用した
**Sonnet側の再構成値**であり、公式のJPY自動計算ログが存在しないための
近似(注記: 為替レート自体はプロジェクト内に公式記録が見当たらず、前回
REPORTの¥表記との整合を取るための逆算)。

1. **今回実測**: 約¥53.6(内訳: token代$0.155相当+web_search実費$0.18相当、
   合計$0.335×約160)。本管理ID累計は¥110.1+¥53.6=**約¥163.7**、
   Fable承認済み上限¥230に対し残り約¥66.3。今回の目安上限¥80は
   超えていない。
2. **Trial特有の追加コスト**: 今回実測分のほぼ全額(このN+1自体が
   汎用テンプレート検証Trialであり、通常運用ベースラインが別途存在しない)。
3. **異常retry・Human Review由来の上振れ**: なし(3/3 attemptは
   MAX_WRITER_ATTEMPTS上限内の設計どおりのretryであり、human_review_
   required等の異常停止は発生していない)。
4. **Standard同期での1記事あたりコスト**: 今回のN+1実測がそのまま該当
   (約¥53.6、3attempt要した場合の実測値)。
5. **Batch量産換算時のコスト**: 前回同様、Batch単価未確認(参考値として
   50%割引想定なら約¥26.8程度、確認値ではない)。

### 10-10. 変更ファイル一覧(修正2回目、すべて未commit)

- 新規artifact(untracked): `er012_output/editorial_b_voices_3v_
  generalization_regression_01_n2/`(+`_n2_attempt1`/`_n2_attempt2`/
  `_n2_attempt3`、`raw_usage_log_writer.jsonl`含む)
- 変更なし(コード): `er012_b_family_voices_writer_generic_01.py`、
  `er012_b_family_voices_theme_ai_screening_01.py`、
  `er012_b_family_production_runner_01.py`(修正1回目からの変更なし、
  今回はコード変更を一切していない)
- 一時ファイル: `docs/pm/ACTIVE_TASK_3V_1B04.md`、
  `docs/pm/RESULT_PACKET_3V_1B04.md`(追記)

他Agent成果物には今回も一切触れていない。Git操作は未実施(禁止指示遵守)。

## 修正3回目(Fable指示、ablation Trial、原因切り分け・本管理ID最終)

実行者: sonnet-worker(Fable修正指示3回目)。Git操作は未実施(禁止指示)。
SSOT(CURRENT_SPEC.md等)は未編集。

### 11-1. Ablation設計とProductionファイル無変更の証跡

Fable仮説: N+1でAnalytical Leakage flagが2/2回再現しており、汎用化で新設した
「体験claimの根拠付け」原則(`COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`)の
文言(「統計の数字を文の主語にする」ような分析調を誘発している可能性)が
原因かどうかを切り分ける。

実装方法(Productionファイルは一切書き換えず、実行時monkeypatchのみ):
scratchpad(`ablation_no_grounding_block_01.py`、Production外)から
`er012_b_family_voices_writer_generic_01`をimportし、`COMMON_EXPERIENTIAL_
CLAIM_GROUNDING_BLOCK`モジュール属性を実行時に空文字へ上書きしたうえで、
既存の`run_writer_stage_generic(theme_mod.THEME_CONFIG, out_dir_base)`
(`write_new_theme`エントリポイントが呼ぶのと同一関数)をそのまま1回呼び出した
(既存retry/Local Rewrite/MAX_WRITER_ATTEMPTS等の安全装置は無変更・無回避、
人為介入なし)。

デフォルト挙動不変の実証: 本monkeypatchはプロセス内メモリ上でのみ有効で
あり、`er012_b_family_voices_writer_generic_01.py`ファイル自体への書き込みは
一切行っていない。実行前後で`git diff --stat`により同ファイルの差分が
0であることを確認済み(実行後も無変更を再確認)。実行直前にpatchなしの
`build_focus_module_block_3v()`が例外なく動作することも確認済み。

出力先: `er012_output/editorial_b_voices_3v_ablation_no_grounding_block_01/`
(+`_attempt1`、未commit)。theme_configは新1回目・N+1と同一
(`er012_b_family_voices_theme_ai_screening_01`、無変更)。

### 11-2. 結果概要(最重要: 検証対象のLeakage Checkに到達する前に別の既存安全装置で停止)

`total_attempts=1`(既存ロジックにより、`status != "OK"`の場合はMAX_WRITER_
ATTEMPTS=3まで再試行せず即座にbreakする仕様。今回もこの既存分岐どおり)。
最終`status=NG_REVIEW_REQUIRED`、`fact_verdict=PASS`、`ledger_status=
LEDGER_COMPLIANT`(ただし後述のとおりこの`ledger_status`は最終full-recheck
時点の値であり、履歴上human_review_required=Trueの項目が残ったことが
NG_REVIEW_REQUIREDの直接理由)。

**(a)Analytical Leakage Checkは今回未実施(N/A)**。理由: 既存コード
(`run_voices_pattern_3v`)は、Fact Checker FAILまたはLedger Local Rewrite
cycle上限到達後もMAJOR残存/human_review_required の場合、Leakage Check
実行前にNG_REVIEW_REQUIREDとして早期returnする設計(修正1・2回目から変更
なしの既存分岐)。今回はLedger側でこの早期停止条件に該当したため、検証
対象のAnalytical Leakage Checkそのものが実行されなかった。**Fableが想定した
2つの判定ケース(原則なしでleakage 0件 / 原則なしでもleakage再現)のいずれも
観測できず、当初の設問には未回答のまま**である。

### 11-3. Ledger逸脱・Local Rewrite(新たな主要観測、当初の設問とは別)

初回Ledger逸脱チェックで`overall_status=LEDGER_DEVIATION`・
`deviations=4`(旧=1件[MAJOR、resolved]、新1回目=1件[MINOR]、N+1=0件との
比較で、**4個体中最多**)。うち3件がMAJORとしてcycle 1のLocal Rewrite対象と
なった:

1. 採用担当者の「監査要約準備」を、Ledger上は条件付き・一部ケースの
   プレッシャーであるものを、一般的必須職務として断定(`changed_fact`,
   `changed_scope`, `changed_certainty`)→cycle1で解消(resolved=true)。
2. 経営者が「毎週ダッシュボードを確認する」という、Ledgerに存在しない
   具体的な習慣・頻度を新規に作出(`changed_fact`, `changed_time`,
   `unsupported_new_claim`)→cycle1で解消(resolved=true)。
3. Tension文「3者の権力は不均衡: 応募者は選べず、採用担当者は導入を選べず、
   所有者が結果を負う」という、Ledgerが示す複数の役割可能性を絶対的な
   固定権限構造へ拡張(`changed_fact`, `changed_scope`, `changed_certainty`,
   `changed_actor`, `changed_negation`, `unsupported_new_claim`)→**3回
   rewriteを試みても`ledger_status=LEDGER_DEVIATION`のまま解消せず、
   `resolved=false`・`human_review_required=true`のまま記録**。

cycle1のフルLedger再判定でさらに2件のMAJORが新規発見され(「採用担当者は
必ずシステムを使わなければならない」「応募者にはシステムへの発言権が
一切ない」、いずれも既存文中の未修正箇所)、cycle2でこの2件は解消
(resolved=true)。cycle2後のフル再判定は`overall_status=LEDGER_COMPLIANT`・
MAJOR=0件(item3の文言自体は最終的に全体再判定ではLedger逸脱と判定されなく
なった)。しかし既存コードの判定条件(`remaining_major_count`または`any_
human_review_required`のいずれかが真ならNG_REVIEW_REQUIRED)により、item3が
個別rewriteでは一度も`resolved=true`に到達しなかった履歴が残っているため、
最終`ledger_status`表示上はLEDGER_COMPLIANTでも**NG_REVIEW_REQUIREDとして
確定**した。これは既存の安全装置がそのとおりに機能した結果であり、今回の
ablationがこの分岐を回避・改変したことはない。

### 11-4. Fact Checker・Point Overlap QA・その他既存メトリクス

- Fact Checker(A'、fact_attribution_mode有効): `verdict=PASS`、
  `contradictions=[]`、`unsupported_specific_claims=[]`(旧・新1回目と同じ
  PASS。N+1のみREVIEW_REQUIREDだったため、これも4個体で0/1/0という
  run分散の範囲内)。
- Point Overlap QA(監視専用、9値): `any_flagged=False`。最大overlap比率
  **0.143**(voice_1_vs_hook。旧0.158、新1回目0.158、N+10.154よりむしろ
  低い=改善方向)。
- Directional Fact Precheck: **今回はN/A**(Ledger早期停止のため、この
  チェックに到達する前段でreturnしたため未実行)。
- Local Rewrite発動: cycle 1・2の計2サイクル、NG項目5件処理(旧1回・新1回目
  1回・N+1 0回との比較でも今回が最多)。

### 11-5. 必須5項目

(i) section別語数表(article.md、post local-rewrite最終稿、body文のみの
概算カウント。compute_metrics側の総語数[569語、見出し記号の扱いの差で
本表の合計565語と数語差]とは別集計):

| section | word_count(概算) | caveat語数(may/might/could/can/often/sometimes/in some cases) |
|---|---|---|
| Hook(The Question) | 65 | 2 |
| Voice1(Applicant) | 93 | 1 |
| Voice2(Recruiter) | 93 | 2 |
| Voice3(Owner) | 90 | 0 |
| Tension(Why They See It Differently) | 166 | 9 |
| Closing(What This Changes) | 58 | 1 |

(ii) near-duplicate最大ratio: **0.559**(SequenceMatcher記事内文ペア方式で
再計算。0.143はPoint Overlap値の取り違え、2026-09-12訂正)。
(iii) caveat文カウント: 上表参照。**Voice2(Recruiter)のcaveat=2**(旧・
新1回目・N+1で観測されていた「Voice2 caveat=0が2/2回再現」というパターンは
**今回は再現しなかった**。これはVoice2のcaveat=0がテンプレート由来の固定
挙動ではなく、run間で変動しうることを示す追加証拠)。Tensionのcaveat語数
(9)が今回最多で、Local Rewriteによる「may」多用のhedge追加が主因
(11-3の書き換え後文面を参照)。
(iv) 記事間定型句類似: Hookは「具体的場面描写→三人称の設問で終わる」形式
(旧・新1回目・N+1と同じ骨格)。Closingは「The deeper question is not
[表層]. It is [再定義]」という、旧・新1回目・N+1と共通の修辞パターンを
今回も維持(テンプレート由来、汎用化固有の劣化ではないとする既存解釈と
整合)。
(v) 音声layer: **未実施**(`write_new_theme`はWriterのみでTTSを呼ばない、
旧・新1回目・N+1と同じ制約)。

### 11-6. 判定材料の整理(判定語自体はFableが確定)

- **当初のFable仮説(「体験claimの根拠付け」原則の文言が分析調Analytical
  Leakageを誘発している)は、今回のablationでは検証できなかった**。
  Leakage Checkに到達する前に、Ledger Local Rewrite側の既存安全装置
  (human_review_required判定)がより早く・より強く反応してNG_REVIEW_
  REQUIREDとして停止したため。
- 観測された事実として、原則除去後は4個体中最多のLedger逸脱(4件、うち
  1件はhuman_review_required)が発生した。ただし**n=1のため、これが原則
  除去の系統的効果なのか、既存run分散(旧1件→新1回目1件→N+1 0件という
  幅が既に確認されている)の外れ値なのかは切り分けられない**。
- 除去後に生じた4件の逸脱の内容は、いずれもVoice本文の「体験claim」
  (原則が本来対象とする、数値・制度・他者の具体的行動を確定事実として
  断定する箇所)そのものではなく、(1)採用担当者の職務範囲の一般化、
  (2)経営者の習慣的行動の新規作出、(3)Tensionでの権力構造の絶対化、
  (4)採用担当者の使用義務の絶対化という、**Narrator文・役割定義文側の
  確信度上昇(certainty inflation)**だった。これは、除去した原則が
  (文言上の対象範囲を超えて)Voice本文以外の確信度も間接的に抑制していた
  副次効果を持っていた可能性を示唆する一方、直接の反証にも確証にもならない
  弱い状況証拠にとどまる。
- 参考として、Voice1本文中の「長期失業」「提訴」という第三者の具体的な
  事案(1-03/1-04)はいずれもLedgerに直接根拠があり、原則の有無にかかわらず
  Ledger逸脱としては検出されなかった(原則が実際に守ろうとしていた典型的な
  ケースでは、除去後も問題は生じていない)。

**文言修正案(参考、実装はしない・意味を変えない範囲・ユーザー判断待ち)**:
今回のablationでは原則文言とAnalytical Leakageとの直接の因果関係を示す
証拠は得られなかったため、以下は「仮に文言側に手を入れるとすれば」という
参考の書き分け案であり、優先度・要否ともに未確定:

1. 現状維持案: 今回の結果は原則文言の問題を示していないため、文言変更を
   保留し、N+2以降の追加ablation(予算確保後)またはLeakage Check単体での
   独立検証(Ledger側の早期停止を回避する実行経路の設計)で再検証する。
2. 「根拠付け」という語を、統計的・分析的な裏付け提示と誤読されないよう、
   「確定事実として断定しない(hedgeする)」という指示の方向性をより明確に
   する言い換え(例: 「〜を統計や調査結果を挙げて正当化するのではなく、
   その人が今感じている実感の強さとして留める」という否定形の明示を追加)。
3. 原則の適用範囲を、Voice本文だけでなくTension・Closingの役割定義文にも
   明示的に及ぼす一文を追加する案(11-3で観測されたNarrator文側の確信度
   上昇に対応する場合の案。ただし今回はn=1でありTension側の問題が原則除去と
   因果関係にあるかは未確認)。

### 11-7. 費用(5区分、PM_GOVERNANCE 15-5準拠)

算出方法: `raw_usage_log_writer.jsonl`(20件)の実測値を、修正2回目と同一の
`pricing_snapshot.json`記載単価(gpt-5.6-luna: input $0.20/1M、cached
$0.02/1M、output $1.20/1M、web_search $10/1000件)・同一算式
((input-cached)×$0.20/1M + cached×$0.02/1M + output×$1.20/1M +
web_search回数×$10/1000)・同一のJPY換算レート(約¥160/$、修正2回目実測値
から逆算した継続値)で計算。実測合計: input=227,397・output=49,152・
cached=4,471・web_search=6件、コスト$0.1637。

1. **今回実測**: 約¥26.2($0.1637×約160)。total_attempts=1(既存分岐で
   Leakage Check・Directional Precheckを含む後続処理が実行されなかった
   ため、新1回目・N+1[3attempt要、約¥53.6〜¥78.0]より大幅に低い)。
   本管理ID累計は¥163.7+¥26.2=**約¥189.9**、Fable承認済み上限¥230に対し
   残り約¥40.1。今回の目安上限¥66.3は超えていない。
2. **Trial特有の追加コスト**: 今回実測分のほぼ全額(ablation Trial自体が
   通常運用に存在しない検証経路のため)。
3. **異常retry・Human Review由来の上振れ**: あり(方向性が通常と逆)。
   今回はLocal Rewrite cycleが2回発動しhuman_review_required判定に
   至ったが、これは**費用の上振れではなくむしろ下振れ**要因になった
   (Writer再attempt[MAX_WRITER_ATTEMPTS=3回]・Leakage Check・Directional
   Precheckが実行されなかったため)。異常停止自体は発生したが、費用への
   影響は減少方向だった点を記録する。
4. **Standard同期での1記事あたりコスト**: 今回のように早期NG_REVIEW_
   REQUIREDで停止した場合の実測値としては約¥26.2が該当するが、これは
   「完走(3attempt到達またはOK確定)」の場合の目安(約¥53.6〜¥78.0、
   修正1・2回目実測)とは別物であり、量産時の代表値としては使えない
   (要human_reviewでの停止は量産では再実行・人手介入が必要になるため)。
5. **Batch量産換算時のコスト**: 未確認(参考値のみ、確認値ではない)。

### 11-8. 変更ファイル一覧(修正3回目、すべて未commit)

- 新規artifact(untracked): `er012_output/editorial_b_voices_3v_ablation_no_
  grounding_block_01/`(+`_attempt1`、`raw_usage_log_writer.jsonl`含む)
- scratchpad(Production外、リポジトリにも含まれない一時ファイル):
  `ablation_no_grounding_block_01.py`(monkeypatchによるablation実行専用、
  Claude Codeのセッション用一時ディレクトリに保存、リポジトリへは配置
  していない)
- 変更なし(コード): `er012_b_family_voices_writer_generic_01.py`
  (実行前後で`git diff`差分0を確認済み)、`er012_b_family_voices_theme_ai_
  screening_01.py`、`er012_b_family_production_runner_01.py`(いずれも
  今回コード変更なし)
- 一時ファイル: `docs/pm/ACTIVE_TASK_3V_1B04.md`、
  `docs/pm/RESULT_PACKET_3V_1B04.md`(追記)

他Agent成果物には今回も一切触れていない。Git操作は未実施(禁止指示遵守)。
本管理IDのSonnet委任ループはこれで3回目(合計4回)に到達しており、
PM_GOVERNANCE 11節の上限どおり、追加のSonnet再委任にはUSER_DECISION_
REQUIREDの手続きが必要になる。
