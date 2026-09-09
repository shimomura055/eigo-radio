# EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-03

管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-03(Lane B、B-3V-1=(b))。
**Trial(Production・Trial-07・registry・Contract・Prompt本体の編集禁止、SSOT・Git禁止)**。
並列稼働中: Reconciliation Gate(読取)、FACT-03再検証(`er003_output/`)、SSOT統合。いずれも
本ファイルとは無関係(`git status`確認済み、本Trialで変更したのは新規ファイルのみ)。

ユーザー決定(2026-09-09、Trial-02のUSER_DECISION_REQUIRED[497語/395.3秒、目標超過]を受け):
Trial-02最終版(`er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/
article.md`)の**Tensionだけを75〜90語へ短縮する再生成を1回だけ**実施する指示。

## 0. 実施内容の要約

新規`er012_editorial_b_voices_3v_person_voice_trial_03.py`(root)。Trial-02(無変更、モジュール
としてimport)の最終article.mdを入力とし、Tension本文のみをLLM 1回(retryなし)で圧縮再生成し、
Hook/Voice1-3/Closing(見出し含む)は単純文字列置換で温存した(byte一致を全段階で確認・記録)。

## 1. Tension圧縮結果

- **語数**: 132語(Trial-02)→ **圧縮直後90語**(目標75〜90語の上限ちょうど、1回のみで達成)。
  ただし、その後のLedger Deviation Checker→Local Rewrite(既存安全装置、下記§3)により2文が
  差し替えられ、**最終article.mdのTension語数は118語**(圧縮直後90語から28語増、Trial-02の
  132語よりは14語少ない)。目標75〜90語は最終的に未達。
- **4要素構造(共通前提→分岐点→非対称性→外部制約統合)**: 圧縮直後は維持していたが、Local
  Rewriteが「非対称性」文("Power differs: applicant cannot choose the system, recruiter
  operates it without deciding adoption, and owner may make the final call.")を、決定権の
  所在を明示しない曖昧な文("Their perspectives and roles can differ...and business-efficiency
  concerns may also inform organizational choices.")へ置き換え、"business-efficiency concerns"
  という、Focus Moduleが明示的に禁止していた抽象軸表現を再導入した。「外部制約統合」文
  (NYC Local Law 144)も、3人それぞれへの具体的な制約効果の説明から、一般的な法令解説文へ後退
  した。

## 2. Fact Checker A' / Analytical Leakage Check(全section)

- **Fact Checker A'**: verdict=**REVIEW_REQUIRED**(PASSでもFAILでもない中間判定、web_search
  11回)。unsupported_specific_claimsは4件、いずれも圧縮後のTension文(「NYC規制がrecruiter/
  owner/applicantの3人全員をconstrainする」という一般化、「applicant cannot control the
  score」の一般化等)を指しており、Voice本文(Hook/Voice1-3/Closing)は含まれない。
- **Analytical Leakage Check(全section、1回のみ)**: **any_flagged=True**。flagged項目は
  tensionの`leak_discovery_syntax`のみ(1件)。quoted_evidenceはLocal Rewrite後の上記2文
  そのもの。`leak_tension_constraint_integration`・`leak_binary_camp_split`は両方**PASS**
  (統合構造・非2対1構図自体はLLM判定上は保たれている)。Voice1-3・Closingはflagged項目なし。

## 3. Ledger Deviation Checker + Local Rewrite(既存安全装置、独自回避なし)

初回判定: LEDGER_DEVIATION(MAJOR 2件、いずれも圧縮によって生じた新規箇所)。既存Local Rewrite
(cycle 1/3、文単位、MAX_REWRITE_CYCLES=3を維持)を適用: item1(非対称性文)はattempt2で
resolved=True。item2(NYC規制の統合文)はattempt1〜3すべてLEDGER_DEVIATIONのまま
**resolved=False, human_review_required=True**(3回目のscope-safe fallbackを適用後も、記事
全体の再判定自体はLEDGER_COMPLIANT[deviations=0]だが、個別item安全フラグが立った状態)。
既存Local Rewriteの仕様どおり、この状態は`NG_REVIEW_REQUIRED`として扱い、追加のTension再生成
(禁止事項)は行っていない。

## 4. Distinctness / Overlap / 語数・尺

- Pairwise Voice Distinctness(一括[主]+有向[診断]、Voice本文はbyte不変): direction_agreement_
  rate=0.933、method_agreement_rate=0.867(Trial-02実測1.0/0.933よりやや低いが、入力Voice本文
  は完全に同一のためLLM判定のノイズと考えられる。5軸×3ペアで不一致は数件のみ)。
- Point Overlap QA monitoring(有向9値、記録のみ): any_flagged=False。
- 語数・尺見積り(既存monitoring専用関数、無変更): 総語数483語(Trial-02比14語減)、推定尺
  **388.3秒**(Trial-02実測395.3秒より7秒改善したが、目標325〜355秒の範囲外のまま、365秒の
  「近傍」許容にも入らない)。

## 5. Trial-02との差分表

| 項目 | Trial-02 | Trial-03(本Trial) |
|---|---|---|
| Tension語数 | 132語 | 118語(圧縮直後90語、Local Rewriteで+28語) |
| 全体語数(6区分合計) | 497語 | 483語 |
| 推定尺 | 395.3秒 | 388.3秒 |
| `leak_tension_constraint_integration` | PASS(2/2) | PASS |
| `leak_binary_camp_split` | PASS(FAILなし) | PASS |
| Analytical Leakage any_flagged | False | **True**(tension、leak_discovery_syntax) |
| Fact Checker A' | PASS(2/2) | **REVIEW_REQUIRED** |
| Ledger Deviation | LEDGER_COMPLIANT(最終) | LEDGER_COMPLIANT(最終値だがhuman_review_required=True) |
| Distinctness 方向/方式一致率 | 1.0 / 0.933 | 0.933 / 0.867 |
| 費用 | ¥20.57 | ¥19.49 |
| Gate 1分類 | USER_DECISION_REQUIRED | USER_DECISION_REQUIRED |

## 6. Gate 4

Production(`er012_b_family_voices_production_01.py`)・registry(`er012_b_family_editorial_
type_registry_01.py`)・Trial-07はいずれも読み取り専用importのみ、`git status`で無変更を確認
した。Ledger本文(`verified_fact_ledger.txt`)は無改変。SSOT・Git操作は実施していない。

## 7. Gate 1分類: USER_DECISION_REQUIRED

保持条件のうち、**崩れたもの**: Analytical Leakage(discovery-syntax再導入)、Fact Checker A'
(PASS→REVIEW_REQUIRED)、Ledger Deviation(human_review_required=True)、Voice3への抽象軸
("business-efficiency concerns")の部分的再導入(Tension内)。**維持されたもの**: 3 concrete
voices(Voice本文はbyte不変)、賛否2対1構図なし(`leak_binary_camp_split`PASS)、外部制約統合
の構造自体(`leak_tension_constraint_integration`PASS)、Distinctness(高水準維持)。

根本原因: 132語→75〜90語への圧縮そのものは1回のLLM呼び出しで達成できた(90語)が、圧縮により
断定的な短文表現("constrain all three"等)が生まれ、これがLedger Deviation Checkerに検出され、
既存Local Rewrite(文単位パッチ)が安全側に倒れて法令解説文的な表現・抽象軸表現へ後退させ、
Analytical Leakageを再導入する結果となった。Trial-01で観測された「Local Rewriteのhedgingが
narrator調Leakageを再導入する」相互作用と同型の失敗モードが、圧縮タスクでも再現した。

尺(388.3秒)は目標325〜355秒・365秒近傍のいずれにも未達のため、395秒許容案(a)を検討する場合も、
上記の品質崩れ(Fact/Ledger/Leakage)が未解消のまま残る。**無限retryはせず、本Reportをもって
ユーザー判断を仰ぐ**(2回目のTension再生成・他sectionの再生成はいずれも実施していない)。

## 8. 費用

¥19.49(上限¥40以内)。call_count=22、web_search 11回(Fact Checker A')。集計は既存pricing
snapshot(`er005_output/cost_baseline_01/pricing_snapshot.json`)を用いた実測(`compute_cost_
jpy()`、Trial-02 cost_compute補助スクリプトと同一price()パターン)。

## 9. 記事最終版・新規ファイル

記事最終版(NG状態、Production採用不可): `er012_output/editorial_b_voices_3v_person_voice_
trial_03/article.md`

新規ファイル:
- `er012_editorial_b_voices_3v_person_voice_trial_03.py`(root)
- `er012_output/editorial_b_voices_3v_person_voice_trial_03/`配下一式(article.md、
  tension_stage_result.json、fact_qa.json、ledger_deviation.json、
  analytical_leakage_check_3v_attempt1.json、byte_identity_check_*.json、summary.json、
  cost_compute_result.json、audit/、qa/)
- 本Report
