# EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02

管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02(Lane B、Trial-01の継続改善)。
**設計修正Trialの継続改善**(Production/Trial-07/registry/Contract編集禁止、SSOT・Git禁止)。
並列稼働中: Lane A 3件(A2 B1B継続/A3 Trial-06/D2 Trial-07)、SSOT統合。いずれも本ファイルとは
無関係(`git status`確認済み、本タスクで変更したのは新規ファイルのみ)。

テーマ固定: "Should companies use AI to screen job applicants?"。音声は生成していない
(テキストのみTrial)。

## 0. Reconciliation(冒頭、Fableが「承認済み設計の適用」と判定した3点の根拠確認)

1. **Tension構造**: design.md B-7「3V: 別途最適構造」の「共通前提→分岐点→非対称性」3段構造
   (`er012_output/editorial_b_voices_phase1_5_3v_4v_integrated_trial_03/design.md` L471-500)、
   および外部制約統合の文言はユーザー決定(2026-09-09、`DECISION_LOG.md`
   PM-CLOSEOUT-CONSOLIDATION-37(2)「Fairness/Legal/HR GovernanceはVoiceから外し、
   Tension/Closing側の統合・制約材料(fairness/bias/accountability/law/compliance=外部制約、
   3者の合理性は単純加算で答えにならない)として扱う」)に一致。Trial-01でも採用済みの原則を、
   語り口指示ではなく検証可能な構造(4要素+自己チェック)として明示し直したのみで、範囲内。
2. **語数**: design.md B-6「3V目標尺(325〜355秒)」(L416-458)は承認済みmonitoring値。
   Fableが指定した逆算基準(2V実測305秒/388語≒1.27語/秒)を用いた合計約410〜450語への
   換算、およびHook/Voice×3/Tension/Closingへの配分はdesign.md B-6の区分別秒数配分表
   (L447-458)への比例配分であり、新しい上限仕様の追加ではなく承認済み目標尺の適用。範囲内。
3. **体験claimの根拠付け**: 既存のVerified Fact Ledger(Fact Safety機構)・
   design.md B-7「Research is backstage. People are on stage.」原則(L497-500)の適用。
   Ledgerに直接根拠のない事実主張を禁じ、体験・感情・判断としての表現に限定するのみで、
   Ledger・Fact Checker・Local Rewriteの挙動自体(hedging表現含む)は一切変更していない。範囲内。

3点とも範囲外と判断した項目はない。実装した改善はこの3点のみ(Voice Card内容・6区切り構造・
QAスキーマ・retry上限・Fact/Ledger呼び出しチェーンはTrial-01から無変更)。

## 1. 生成結果

新規`er012_editorial_b_voices_3v_person_voice_trial_02.py`(root、Trial-01を複製し上記3点の
みFocus Module Block内へ適用。Trial-01ファイル自体は無変更)。

| attempt | 状態 | Fact Checker A' | Ledger Deviation | Leakage Check | 備考 |
|---|---|---|---|---|---|
| 1 | OK | PASS(web_search 4回) | LEDGER_COMPLIANT(deviations=0) | flagged(voice_1, voice_2, voice_3) | voice_1/2: 統計主語文1件ずつ。voice_3: 数字前景化+discovery_syntax。**tensionは6項目中`leak_tension_constraint_integration`含め全PASS** |
| 2(最終) | **OK** | PASS(web_search 7回) | LEDGER_DEVIATION(MAJOR1件)→Local Rewrite 1 cycle(1件resolved=true, human_review=false)→**LEDGER_COMPLIANT(deviations=0)** | **flagged項目なし(0件、tension含む全項目PASS)** | MAX_WRITER_ATTEMPTS(3)のうち2回で確定。既存の安全装置(Local Rewrite)が構造修正のみで解消、hedging表現の追加は発生せず |

Trial-01(3 attempts全消化、attempt3がNG_REVIEW_REQUIRED)と異なり、本Trialは2 attemptsで
Leakage 0件・Fact Checker PASS・Ledger COMPLIANTのOK状態に到達した。既存Gate(Ledger Deviation
Checker+Local Rewrite、Analytical Leakage feedback loop、MAX_WRITER_ATTEMPTS=3)はいずれも
無変更のまま機能し、自動追加retryや独自判断でのGate回避は行っていない。

## 2. Tension外部制約統合基準の結果(改善1の直接評価)

`leak_tension_constraint_integration`は**attempt1・attempt2の2回とも(2/2)PASS**。Trial-01の
3/3 FAILから完全に転換した。attempt2 reasoning(判定モデルによる要約):「ニューヨーク市の監査・
通知義務や女性を低く評価したツールの停止も、各人物の行動を制約する力として物語に統合されて
いる」。実際のTension本文(最終article、抜粋):"In New York City, an employer needs a recent
fairness check, a public summary, and notice before using an automated hiring tool. The
recruiter cannot use it silently, the owner cannot rely on speed alone, and the applicant
still cannot control the score. [...] Their views cannot simply make one answer." のように、
規制の紹介文の直後に3人それぞれへの具体的な制約効果を接続する構造になっており、Trial-01で
指摘された「地域規制の列挙で終わる」パターンは再発しなかった。`leak_binary_camp_split`も
2/2 PASS(2対1陣営化なし、design.mdが懸念した既知リスクは今回も顕在化せず)。

## 3. 語数・尺

| 区分 | 新soft target(改善2) | attempt1実績 | attempt2(最終)実績 |
|---|---|---|---|
| Hook | 45〜55語 | 50語 | 60語(やや超過) |
| Voice 1 | 70〜85語 | 91語(超過) | 79語(範囲内) |
| Voice 2 | 70〜85語 | 96語(超過) | 90語(やや超過) |
| Voice 3 | 70〜85語 | 84語(範囲内) | 82語(範囲内) |
| Tension | 75〜90語 | 126語(超過) | 132語(超過、主因) |
| Closing | 45〜55語 | 53語(範囲内) | 54語(範囲内) |
| **合計** | **410〜450語** | **500語** | **497語** |

最終article(497語)はTrial-01の最終article(530語、NG)より33語(約6%)少なく、旧soft
target(330語)からの逆算の甘さは解消したが、新target上限(450語)は約47語(約10%)超過して
おり、超過の大半(42語)はTensionが占める(4要素[共通前提/分岐点/非対称性/外部制約統合+説明]
を保ちながら75〜90語へ圧縮するのは達成できなかった)。`build_word_count_and_duration_
estimate()`(Trial-01から無変更、2V実測の別比率[TWO_V_VARIABLE_PARTS_SECONDS基準、約2.0語/秒]
を用いるmonitoring専用関数)による推定尺は**395.3秒**(3V目標325〜355秒の範囲外だが、
Trial-01の411.7秒より改善)。この関数はFableが改善2で用いた逆算比率(1.27語/秒)とは別の
既存ロジックであり、本Trialでは変更していない(prompt側のsoft target算出にのみFableの比率を
新規適用し、QA側の尺推定関数自体は据え置いて前後比較の一貫性を保った)。

## 4. Leakage(Voice別・Local Rewrite後)

- attempt1(参考、最終不採用): voice_1(leak_evidence_subject FAIL、統計主語文1件)、
  voice_2(leak_evidence_subject FAIL、統計主語文1件)、voice_3(leak_numbers_foreground+
  leak_discovery_syntax FAIL、企業事例比較・削減率が前景化)。tension/closingはFAILなし。
- attempt2(最終、Local Rewrite後に確定): **全section・全項目PASS(0 flagged)**。Local
  Rewriteが修正した対象はTension内の1文(意思決定権の帰属範囲の誤り、Voice本文ではない)のみで、
  修正後の文("the recruiter runs it and may also help decide whether to adopt it; the owner
  may make the final call")はhedging表現("The cited analysis suggests..."等)を含まず、
  Leakage再導入は発生しなかった。**Trial-01で発見された「人物化→Ledger負荷増→Local
  Rewriteのhedging→narrator調Leakage再導入」という相互作用は、本Trialでは再現しなかった**
  (経営者Voice[voice_3]は改善3[体験claim根拠付け]の効果もあり、attempt2でLedger MAJORの
  対象にすらならなかった)。

## 5. Distinctness Check

- 有向6ペア: 36.5秒。一括判定(batch): 14.1秒。
- direction_agreement_rate=**1.0**(15/15、Trial-01の0.933から改善)、method_agreement_rate
  (一括 vs 有向)=0.933(14/15、Trial-01と同水準)。唯一の不一致はbatch判定のvoice_2_voice_3
  reasoning軸(batch=SIMILAR、有向=DIFFERENT)。
- 5軸すべて(stakeholder_position/constraint/responsibility/what_they_protect/reasoning)で、
  3ペア全てDIFFERENTと判定された(voice_2_voice_3のbatch reasoning軸を除く)。

## 6. Overlap Controls(¥0、合否判定には使わず記録のみ)

positive control 0.864(flagged、期待どおり)、deterministic control 0.711(flagged、指標の
盲点、Trial-01と同水準)、negative control(既存2V実採用ペア)0.14(未flagged、期待どおり)、
theme_vocab_dummy 0.389(閾値0.40未満、未flagged、Trial-01と同水準、偽陽性リスク近接は継続
観察事項)。Point Overlap QA monitoring(9値、有向6+vs Hook 3)もany_flagged=Falseで確定。

## 7. Fact Checker A'・Ledger Deviation詳細

Fact Checker A'は**attempt1・attempt2とも(2/2)PASS**(unsupported claims 0件、Trial-01の
1/3 PASSから改善)。web_search呼び出しはattempt1=4回、attempt2=7回(合計11回、Trial-01の
27回より大幅減、attempt数減少と1回あたり検索数の減少の両方が寄与)。Ledger Deviationは
attempt1がLEDGER_COMPLIANT(deviations=0、Local Rewrite不要)、attempt2は
MAJOR 1件検出(Tension内の意思決定権帰属の誤り、Voice本文ではない)→Local Rewrite 1 cycle
(1/1 resolved、human_review_required=false)→全体再判定LEDGER_COMPLIANT(deviations=0)。
Trial-01のattempt3(MAJOR4件、3 cycle消化後も1件human_review_required残存)より大幅に改善。

## 8. Trial-01 / 4V Trial-02との差分表(要約)

| 項目 | 4V Trial-02 | 3V Trial-01 | **3V Trial-02(本Trial)** |
|---|---|---|---|
| attempt数(MAX3) | 3(MAX到達) | 3(MAX到達、NG) | **2(早期OK確定)** |
| Fact Checker A' | 3/3 PASS | 1/3 PASS | **2/2 PASS** |
| Ledger Deviation(MAJOR→最終) | 完全解消×2 | 4件→human_review 1件残存 | **1件→完全解消(human_review 0件)** |
| Leakage(最終判定) | 3 attempts全FAIL(voice_3) | flagged継続(最終attemptは未実施) | **0 flagged(全section)** |
| `leak_tension_constraint_integration` | (基準なし) | 3/3 FAIL | **2/2 PASS** |
| `leak_binary_camp_split` | FAILなし | FAILなし | **FAILなし** |
| 最終語数/推定尺 | 469語/385.0秒(目標内) | 530語/411.7秒(目標外) | **497語/395.3秒(目標外、改善)** |
| Distinctness 方向/方式一致率 | 0.933/0.933 | 0.933/0.933 | **1.0/0.933** |
| 最終status | (Trial-01/02参照) | NG_REVIEW_REQUIRED | **OK** |
| 費用 | ¥76.6 | ¥93.63 | **¥20.57** |

## 9. コスト実測

- Writer stage(13 call、Fact Checker A' 2回・web_search計11回込み): ¥19.42
- QA stage(9 call、Comment 1・4・Distinctness 7件・Overlap Controls[¥0]・
  Duration/First-person[¥0]): ¥1.16
- **合計 ¥20.57**(上限¥150に対し大幅な余裕。Trial-01実績¥93.63の約1/4、attempt数減少と
  Local Rewrite cycle数減少が主因)。集計は既存pricing snapshot(`er005_output/cost_
  baseline_01/pricing_snapshot.json`)を用いた新規補助スクリプト
  (`er012_editorial_b_voices_3v_person_voice_trial_02_cost_compute.py`、他Trialと同一の
  price()パターンを踏襲)で実測。
- 量産概算: 本Trialの実績(2 attempts、Local Rewrite 1 cycle)がベースラインとして再現すれば
  記事あたり約¥20〜25/本(Trial-01の¥90〜100/本より大幅改善の可能性)。ただしN=1のため、
  再現性は今後の複数テーマ実測が必要。

## 10. Gate 4・Gate 1分類

- **Gate 4**: Production(`er012_b_family_voices_production_01.py`・
  `er012_b_family_editorial_type_registry_01.py`)・Trial-07・4V Trial-01/02・3V Trial-01は
  いずれもimportまたは読み取り専用参照のみで、`git status`上も無変更を確認した。SSOT・Git
  操作は実施していない。Ledger本文・perspective_map(4V/3V版とも)は無改変。
- **Gate 1分類**: **USER_DECISION_REQUIRED**。Fable指定の分類基準(VALIDATED=Tension統合
  成立・尺目標内・blocking 0・Leakage解消・副作用なし)のうち、Tension統合成立(§2、2/2
  PASS)・blocking 0(NG_REVIEW_REQUIRED発生せず)・Leakage解消(0 flagged)・副作用なし
  (Local Rewrite hedging→Leakage再導入は不再現、§4)の4点は満たしたが、**尺目標内は未達**
  (497語/395.3秒、目標410〜450語/325〜355秒の範囲外、§3)。REJECTEDでもない(Trial-01が
  残した3つの未達点[Tension統合・語数超過・相互作用効果]のうち2つ[Tension統合・相互作用
  効果]は解消し、残る1つ[語数・尺]も超過幅は縮小[530→497語、411.7→395.3秒]した)。

## 11. 未承認仕様候補一覧

- 3V Comment 2/3文言(design.md B-1手動ドラフト、Trial-01から無変更、registry未反映)。
- Leakage Check 3V版スキーマ(`voice_1/2/3`+`leak_tension_constraint_integration`、
  Trial-01から無変更、registry未反映)。
- Pairwise Voice Distinctness Check(一括方式主・有向方式併走、正式採用は別途)。
- required_structure 3V定義(`point_one/two/three`命名方式)。
- Tension外部制約統合の具体的構造(改善1、本Trialで初めて2/2 PASSを達成した4要素+自己
  チェック方式そのもの。「語り口指示ではなく構造として明示する」という手法自体は、他の
  未達成基準への横展開可能性がある未承認候補として記録する)。
- 3V目標尺・語数配分の逆算方法(改善2、Fable指定の1.27語/秒ベース。今回も目標を達成できな
  かったため、design.md B-6の3V区分別目安表自体の再検討[特にTensionの目安秒数]が必要な
  可能性がある未承認候補として記録する)。
- 体験claim根拠付けの文言(改善3、Ledger MAJOR発生率低下[4件→1件]に寄与した可能性がある
  未承認候補)。

## 12. STOP有無

**新規failure modeは検出していない。** MAX_WRITER_ATTEMPTS(3)未消費(2で確定)、見出し数6は
全attemptで成立、賛否2対1構図は発生せず、費用は上限内(¥20.57/¥150)。Production・Trial-07・
registry・Ledger本文・SSOT・Gitへの書き込みは行っていない。既存の安全装置(Leakage feedback
loop、Ledger Deviation Checker+Local Rewrite、MAX_WRITER_ATTEMPTS)を独自判断で回避・追加
retry・無効化したことはない。上記1〜3の適用で解消しなかった点(尺目標)は新原則の追加ではなく
既存目標値の再検討候補として§11に記載のみとした(実装はしていない)。以上を踏まえ、追加の
Prompt変更・再生成は実施せず、本Reportをもって結果を提示する(§10のとおり
USER_DECISION_REQUIRED)。

## 13. 記事最終版の絶対パス・新規ファイル一覧

記事最終版(OK確定、Production採用可否は別途ユーザー判断):
`C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_3v_person_voice_trial_02\
b1b_run01_attempt2\article.md`

新規ファイル:
- `er012_editorial_b_voices_3v_person_voice_trial_02.py`(新規、root)
- `er012_editorial_b_voices_3v_person_voice_trial_02_cost_compute.py`(新規、root、補助)
- `er012_output/editorial_b_voices_3v_person_voice_trial_02/`配下一式(b1b_run01/、
  b1b_run01_attempt1〜2/、qa/、summary.json、cost_compute_result.json、
  required_structure_3v_trial_review.json、raw_usage_log_3v_writer.jsonl、
  raw_usage_log_3v_qa_stage.jsonl)
- 本Report(`EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02_REPORT.md`)

(注: `er012_output/editorial_b_voices_3v_person_voice_trial_01/research/perspective_map_3v.md`
はTrial-01成果物を読み取り専用で再利用したのみで、本Trialでは新規作成・変更していない。)
