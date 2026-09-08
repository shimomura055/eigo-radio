# FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01 — Trend Synthesis Production化 残件棚卸し(読み取り専用)

**管理ID**: FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01(Lane A-1)
**性質**: 読み取り専用棚卸し・設計準備。SSOT編集・コード編集・API呼び出し・
Git操作は一切行っていない。

---

## 0. 前提・スコープ確認

Family A優先順位1位=Trend SynthesisのProduction化。現状(根拠:
`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`§3・§6、`OPEN_ITEMS.md` OPEN-112行):

- Theme 2「若者の旅」完成音声(A2 rerun_04・B1 rerun_04)は
  `APPROVED_FOR_PRODUCTION`(2026-09-08)。**ただしこれは一回限りの
  Trialスクリプトによる成果物への承認**であり、Trend Synthesis
  Writer/Focus Module自体はProduction Writerコードへ配線されていない。
- OPEN-112本体(Discovery 4-layer採否・Engagement根底指示採否・News
  Ledger自動Research化)は2026-09-08ユーザー決定により**DEFERRED**
  (追加Trial・Production変更なし)。
- 状態表現(OPEN_ITEMS.md OPEN-112行末尾): 「Theme 2音声: CLOSED /
  本体残件: DEFERRED」。

---

## 1. (a) すでにVALIDATED済みの仕様

| 項目 | Status | 管理ID | 根拠 |
|---|---|---|---|
| Trend Gate(6条件、質的Gate・数値閾値化せず) | `VALIDATED`(実記事1テーマで確認) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 | `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`§5(設計)。Trial-09でイラン・ホルムズ海峡テーマが全6条件PASS、`OPEN_ITEMS.md` OPEN-112行Trial-09追記 |
| Mode判定基準(単一起点質問/集約質問の2問、境界事例表つき) | `VALIDATED`(設計+具体例確認、実データ再確認1件) | OPEN-112-NEWS-MODE-DESIGN-08 | `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`§4。Trial-09で`TREND_SYNTHESIS`再確認 |
| 最小Focus Module Prompt(Trend Synthesis Layer3、最小版) | `VALIDATED`(実記事A2×2・B1B×1で生成成功) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 | Production Prompt/code変更なしのTrial実行。`er011_output/open112_trend_synthesis_minimal_prompt_trial_09/` |
| Engagement/Storytelling原則(施策1: 時系列列挙禁止+反転・対比構成) | `VALIDATED`(A/B比較、両パターン改善確認) | OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10 | 「A happened. Then B happened」型からの構成改善を2パターンで確認 |
| Point Overlap閾値(0.40固定)の扱い | `VALIDATED`寄り(再現性なし、閾値付近の不安定さと判定・仕様変更は不要と判断) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09/-10 | Trial-09で誤flag1回発生も再現生成で解消、Trial-10では0.08〜0.17と余裕を持ってPASS |
| Ledger Deviation Checkerのtrend overclaim検知(既存タグ流用) | `VALIDATED`寄り(既存タグがEXISTING_QA_SUFFICIENT寄りと評価、専用カテゴリ欠如は既知Gap) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 | `changed_causality`/`changed_certainty`/`unsupported_new_claim`が4件のMINOR trend overclaimを実際に検知(ただしseverity一律MINORでoverall_status非block、要検討) |
| Reference Digest(施策2、Fact source使用禁止) | `VALIDATED`(Fact漏洩0件)、効果自体は**不明瞭** | OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10 | 1回比較のみのため効果不明瞭。追加検証は`USER_DECISION_REQUIRED`候補として未登録 |
| A Family共通骨格(4slot: Main Story/Point One/Point Two/In One Line)がTrend Synthesisでも成立 | `VALIDATED` | OPEN-112-NEWS-MODE-DESIGN-08 | 構造拡張不要(Voicesと異なり見出し数変更なし)。§12 |
| Point Role Planning機構の流用可能性 | `VALIDATED`(設計確認、実記事でも機能) | OPEN-112-NEWS-MODE-DESIGN-08 | 既存の動的役割選択がTrend Synthesisでも新規Validatorなしで機能する設計 |

---

## 2. (b) USER_DECISION_REQUIRED一覧

| 項目 | 内容 | 管理ID | Status |
|---|---|---|---|
| Discovery 4-layer Focus Module Production採否 | Trend SynthesisはDiscoveryと同じ4層構造フレームを共有するため、この採否が前提として残る | PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01 | `USER_DECISION_REQUIRED`(defer扱いにせず個別判断すべき重要事項として維持) |
| Engagement根底指示の正式Production採用可否 | Trial-10の施策1(時系列列挙禁止)をWriter根底指示へ正式追加するか | 同上 | `USER_DECISION_REQUIRED` |
| News Ledger作成を既存自動Research経路へ寄せるか | Theme2で使ったLedgerは全てTrial手動作成(下記§4参照)。自動Researchパイプライン接続は**Trialなし** | 同上 | `USER_DECISION_REQUIRED` |
| Ledger Deviation Checker trend overclaim severity方針 | 現状MINOR一律でoverall_status非block。これで十分か専用重み付けが必要か | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 | `USER_DECISION_REQUIRED`(2026-09-05 PM-HANDOFF-CHATGPT-001で明示defer) |
| Point Overlap閾値(0.40)のNews/Trend向け調整要否 | News/Trend記事の共有語彙による誤flagリスク | 同上 | `USER_DECISION_REQUIRED`(defer) |
| Reference Digest追加検証要否 | 効果不明瞭のまま | OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10 | `USER_DECISION_REQUIRED`(defer) |
| Point長さ目安(25〜70語)超過傾向への対応要否 | Trial-09で81語のPoint超過事例あり(別件のRedundancy修正で解消したが構造的傾向として観測) | 同上 | `USER_DECISION_REQUIRED`(defer) |
| Diagnostic Full Retry診断語彙のNews/Trend拡張要否 | evidence listing/trend overclaim/weak counter-signal等の語彙が存在しない(Gap) | OPEN-112-NEWS-MODE-DESIGN-08§10 | `USER_DECISION_REQUIRED`(コード変更を伴うため今回スコープ外のまま) |

---

## 3. (c) deferred項目

2026-09-05(PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01)でユーザーが明示的に
`defer`(先送り、承認取消ではない)とした4件:

1. trend overclaim severity方針
2. News/Trend向けPoint Overlap閾値(0.40)見直し
3. Reference Digest追加検証要否
4. Point長さ目安(25〜70語)見直し

2026-09-08(PM-CLOSEOUT-CONSOLIDATION-08)でOPEN-112本体残件(Discovery
4-layer・Engagement根底指示・News Ledger自動Research化)も「追加Trial・
Production変更なし」で**DEFERRED**と決定(§2の3件と同一実体)。

---

## 4. (d) Production Writer未配線の具体箇所

### 4.1 現行Production Writerの構造

`er003_v1_n3_01_articles_generate.py::build_common_block()`
(348〜364行)は、`COMMON_BLOCK_TEMPLATE`をformatして返す共通関数で、
既に**後方互換な任意ブロック挿入パターン**の前例がある:

```python
def build_common_block(master_full_text, topic, verified_ledger_text,
                        shared_point_blueprint_block: str = "",
                        evidence_compression: bool = False) -> str:
```

`shared_point_blueprint_block`(既定`""`)は、A2/B1 Point Structure
Semantic Alignmentタスクで追加された既存の前例であり、**Trend
Synthesis Focus Moduleを同じパターンで追加する土台が既に存在する**
(例: `editorial_type_module_block: str = ""`)。

実際にProduction経路がこれを呼ぶ箇所は
`er006_pool_pilot_01_writer.py::run_writer_for_theme()`(61〜69行):

```python
common_block = gen.build_common_block(master_full_text, topic, verified_ledger_text,
                                       shared_point_blueprint_block=blueprint_block,
                                       evidence_compression=evidence_compression)
prompt = gen.build_prompt(common_block, instruction)
result = gen.run_one_pattern(client, theme_id, label, prompt, verified_ledger_text,
                              topic, level_out_dir, apply_evidence_compression=...)
```

この関数には現在、**Editorial Type/Modeを表す引数が一切存在しない**。
POOL_TOPIC_MASTER.md等の設計上No.10〜20に割り当てられている「Editorial
Type」概念は、OPEN-112本体診断(2026-09-03)の時点でコード実装0件と
確認済みで、この状態は今回の調査でも変化なし。

### 4.2 Theme 2 TrialスクリプトがProduction Writerを迂回した方法

`er011_open112_trend_synthesis_minimal_prompt_trial_09.py`は、
Production `COMMON_BLOCK_TEMPLATE`をmonkeypatchせず、以下の手順で
Focus Module挿入を模擬した(コード確認済み):

1. `gen.COMMON_BLOCK_TEMPLATE`(Productionモジュールのグローバル、
   無変更のまま読み取りのみ)内のアンカー文字列
   `"【Spoken-first原則(数字の扱い)】"`(Discovery Trial-05と同一
   Anchor)を`.replace()`でローカル変数へコピーし、Focus Module
   Blockを挿入した**ローカルな**candidate_templateを構築(149〜153行)。
2. `candidate_template.format(...)`でcommon_block文字列を生成し、
   `gen.build_prompt(common_block, instruction)`(無変更のProduction
   関数、`common_block`は単なる文字列引数)へ渡す。
3. `gen.run_one_pattern(client, theme_id, label, prompt, ...)`
   (無変更のProduction関数、`prompt`は文字列引数として公開設計済み)
   を直接呼び出す。

**結論**: monkeypatch・Production関数の書き換えは一切なし。既存の
公開引数(`prompt`文字列を直接渡せる`run_one_pattern`の設計)を利用した
合法的な外部呼び出しであり、Gate 4観点でのDangling Reference候補は
**発見されなかった**(詳細は§7)。ただし、この「アンカー文字列を
`.replace()`で置換する」手法は**Trial専用の簡易手法**であり、正式
Production配線では§4.1のような明示的パラメータ化が必要(文字列一致に
依存する現行手法は、`COMMON_BLOCK_TEMPLATE`側の文言変更で無警告のまま
壊れうる脆弱な結合)。

### 4.3 Mode判定ロジック自体の実装状況

Mode判定基準(§1参照、単一起点質問/集約質問)は**設計のみ**
(`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`§4)であり、コードとしての
実装は0件。Trial-09/10ではテーマ選定自体が人間(タスク実行者)による
判断であり、Mode判定を自動化するコードパスは存在しない。

### 4.4 Assembly/TTS層は既存Production関数を無変更利用

Theme 2完成音声はAssembly段(`stage_assemble_b1`/`stage_assemble_a2`、
`er003_v1_n3_01_assemble.py`)・TTS生成(`er003_v1_n3_01_tts_generate.py`)・
Key Phrase選定(`er006_audio_cost_pilot_02_shared_narration.py`)を
いずれも無変更のまま利用しており、**この層にはTrend Synthesis固有の
未配線箇所は存在しない**(記事テキストさえ生成されれば既存Audio
Production Pipelineがそのまま機能する)。

---

## 5. (e) Research / Ledger route

**Trial手動作成**(既存自動Researchパイプライン経由ではない)。

- Trial-09: `TREND_VERIFIED_LEDGER_TEXT`はTrialスクリプト内に直接
  埋め込まれたテキスト(2026年9月にWebSearchで実施者が手動収集)。
- Trial-12/13: Ledger精度誤り(F-005機雷個数の未確認具体数混入、
  F-009曜日/日付誤り)が発覚し、一次資料(観光庁公式PDF等)で手動修正
  したという記録があり、これも人手によるLedger作成・検証プロセスで
  あることを示す。
- 「News Ledger作成を既存自動Researcherパイプライン経由にすべきか」は
  §2に記載の通り**Trialなし・USER_DECISION_REQUIRED候補として報告のみ**
  (OPEN_ITEMSへの正式登録・実装は未実施)。

**結論**: Trend Synthesis Production化には、Ledger供給経路(自動 vs
手動)の決定と、自動化する場合はその実装(既存Research pipelineの
拡張または新規経路)が別途必要。現状のTrial実績だけでは「Production
runで毎回どうやってLedgerを作るか」という運用上の問いに答えられない。

---

## 6. (f) Focus Module

- 設計: `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`が、News全体を
  Major/Daily NewsとTrend Synthesisの2 variantとして設計(Discovery
  Moduleと同じ「Anchor 1箇所への単一Module挿入」方式)。
- Trend Synthesis Focus Module本体: 中心Question
  "What is changing, and what do several independent signals together
  suggest?"。Main Story=Evidence列挙せず変化を提示、Point
  One=driver/mechanism候補、Point Two=counter-signal/limitation優先
  検討(既定候補、無い場合は明示)、In One Line=方向感+留保。
- 実装: `er011_open112_trend_synthesis_minimal_prompt_trial_09.py`の
  `TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`(最小版、実記事Trialで動作確認
  済み)。ただしこれはTrial専用ファイルであり、Production側の正式定数
  としては未採用・未配線。

---

## 7. (g) Engagement・Storytelling原則

- 施策1(時系列列挙禁止+反転・対比構成をWriter根底指示へ追加)は
  Trial-10のA/B比較でVALIDATED(2/2パターンで構成改善)。ただし
  「Writer根底指示への正式追加」自体は§2の通り`USER_DECISION_REQUIRED`
  のまま未実装。
- 施策2(Reference Digest)は効果不明瞭(§1・§3参照)、追加検証も
  deferred。

---

## 8. (h) Trend Gate・Mode判定

§1・§4.3に集約。Gate自体は質的(qualitative)設計であり機械的な
Validatorコードは意図的に未実装(`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`
§5「Validator実装はせず、Writer/Reviewerが判断する定性的Gateとして」)。
Trial-09で実記事1件のみ6条件全PASSを確認したのみで、複数記事での
再現性は未検証。

---

## 9. (i) retry・fallback・validatorへの影響

既存の共通Production安全機構(Editorial Type非分岐、全テーマ共通、
`PRODUCTION_WIRED`確定済み)は、Trend Synthesis記事が実際にProduction
Writerへ配線された場合も**無変更のまま自動的に適用される**設計:

- Fact Checker(独立Web検索)/Ledger Deviation Checker(10種変化検知)/
  Directional Fact Precheck: 記事全文ベースの構造非依存設計であり
  Trend Synthesis固有の変更は不要(ただしtrend overclaim/source
  strength専用カテゴリの欠如は既知Gap、§2参照)。
- Point Overlap QA + Diagnostic Full Retry: 流用可能だが、News/Trend
  固有の失敗パターン(evidence listing・trend overclaim・weak
  counter-signal等)に対応する診断語彙が存在しない(Gap、§2参照)。
- TTS Repetition/False Start QA(OPEN-121、`PRODUCTION_WIRED`)・
  Connected Speech Equivalence Layer(OPEN-122、`PRODUCTION_WIRED`、
  A2/B1英語本文segment限定)・Transcript Style Normalization
  (OPEN-123、`PRODUCTION_WIRED`)・Numeric Precision共通原則
  (`PRODUCTION_WIRED`)は、いずれもEditorial Type非依存の共通経路で
  あり、Trend Synthesis記事も自動的にこの恩恵を受ける(Theme 2実績で
  実際に確認済み: rerun_02/03/04でKey Phrase gloss規約・Numeric
  Precision強化ブロック・repetition QA・Connected Speech Equivalence
  Layerがいずれも正しく機能した実データあり)。
- Key Phrase Validator(ASR数字保護ゲート・EN ASR false rejection
  cascade、OPEN-116/119、`PRODUCTION_WIRED`): Theme 2 Trial-13/17で
  実際に発見されたKey Phrase系の問題(助数詞表記ゆれ・数字保護ゲート・
  gloss規約不足)は、全てTrend Synthesis固有ではなく既存Key Phrase
  経路全体の問題として修正・配線済み。
- Audio Validation Gate: 位置ベース(`point_one_heading`等)の設計で
  あり、見出しブロックの中身の意味がPoint→Signal解釈に変わっても
  **コード変更不要**(構造は不変のため)。

**結論**: retry/fallback/validator層への追加変更は基本的に不要
(既存の共通安全機構がそのまま機能する)。唯一の明確なGapは
Diagnostic Full Retry診断語彙とLedger Deviation Checkerのtrend
overclaim/source strength専用カテゴリの2点で、いずれもコード変更を
伴う拡張の要否がUSER_DECISION_REQUIREDのまま。

---

## 10. 最小単位の判断項目リスト(APPROVED_FOR_PRODUCTIONへの経路)

各項目: 何を決めるか / 選択肢 / Trial根拠 / 推奨 / 依存関係。

1. **Trend Synthesis modeの正式採用可否**(そもそも量産化するか)
   - 選択肢: 採用する/しない/追加Trial待ち
   - 根拠: Trial-09/10で構造・Gate・Engagement原則はVALIDATED、Theme 2
     完成音声はユーザー承認済み
   - 推奨: 追加Trial不要、次項目群の判断へ進める(構造自体の妥当性は
     十分に確認されている)
   - 依存: なし(起点)

2. **Discovery 4-layer Focus Module全体の採否**(Trend Synthesisは
   同じ4層フレームを前提とする)
   - 選択肢: 採用/不採用/Trend Synthesisのみ先行採用(Discoveryと
     切り離す)
   - 根拠: PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01で個別判断事項として
     維持
   - 推奨: 不明(ユーザー判断)。ただし4層構造自体(Layer1/2は完全共有・
     Layer3のみ差し替え)はNews Mode Design-08でも同じ結論に達しており、
     Trend Synthesisだけを切り離して先行採用することは設計上可能
   - 依存: 項目1

3. **Focus Module実装方式**: `build_common_block()`への新規パラメータ
   追加(`shared_point_blueprint_block`と同型パターン) vs 現行Trialの
   アンカー文字列置換方式の踏襲
   - 選択肢: 新規パラメータ化(推奨) / 現状のTrial方式のまま
   - 根拠: §4.1〜4.2(コード確認済み)
   - 推奨: 新規パラメータ化(既存前例と一貫性があり、`COMMON_BLOCK_
     TEMPLATE`文言変更に対して脆弱でない)
   - 依存: 項目1・2

4. **Mode判定の自動化要否**: 記事化パイプライン内でMode判定を自動実行
   するコードを新設するか、当面は人間が選定するか
   - 選択肢: 自動化する/当面は人間選定のまま
   - 根拠: §4.3(現状コード実装0件、質的Gateとして意図的にValidator
     化していない設計)
   - 推奨: **追加Trial要**(自動Mode判定の精度検証が未実施。誤判定時の
     影響[Major/DailyをTrendとして書いてしまう等]も未検証)
   - 依存: 項目1・2

5. **News Ledger供給経路**: 既存自動Research pipelineへ統合するか、
   当面は手動作成を継続するか
   - 選択肢: 自動Research統合/手動継続/ハイブリッド
   - 根拠: §5(Trialなし、論点提起のみ)
   - 推奨: **追加Trial要**(自動Research pipeline側の対応可否が未調査)
   - 依存: 項目1

6. **Engagement根底指示(施策1)のWriter共通Prompt正式採用**
   - 選択肢: 採用/不採用/Trend Synthesisのみ限定採用
   - 根拠: Trial-10でVALIDATED(2/2改善)
   - 推奨: 採用に足る根拠はあるが、他Editorial Type(Discovery等)への
     波及効果は未検証のため、Trend Synthesis Module内限定での採用が
     低リスク
   - 依存: 項目2・3

7. **Reference Digest(施策2)の採否**
   - 選択肢: 採用/不採用/追加検証
   - 根拠: 効果不明瞭(1回比較のみ)
   - 推奨: **追加Trial要**(効果測定にはn数を増やす必要がある)
   - 依存: 項目6

8. **Ledger Deviation Checker trend overclaim severity方針**
   - 選択肢: 現状維持(MINOR一律)/専用重み付け追加/専用カテゴリ新設
   - 根拠: Trial-09で4件MINOR検知(overall_status非block)
   - 推奨: 不明(ユーザー判断、コード変更を伴う)
   - 依存: 項目1

9. **Point Overlap閾値(0.40)のNews/Trend向け調整要否**
   - 選択肢: 現状維持/News/Trend向け閾値緩和
   - 根拠: Trial-09で誤flag1回(再現性なし)、Trial-10では発生せず
   - 推奨: 現状維持(再現性が低く、閾値変更の必要性を裏付けるデータが
     不十分)
   - 依存: なし

10. **Point長さ目安(25〜70語)超過傾向への対応**
    - 選択肢: 現状維持/News/Trend向け目安緩和
    - 根拠: Trial-09で81語の超過事例(1件、別要因のRedundancy修正で解消)
    - 推奨: 現状維持(n数不足)
    - 依存: なし

11. **Diagnostic Full Retry診断語彙のNews/Trend拡張**
    - 選択肢: 拡張する/しない
    - 根拠: Gap確認済み(evidence listing/trend overclaim/weak
      counter-signal等の語彙が存在しない)
    - 推奨: **追加Trial要**(拡張後の診断精度・false positive率が未検証)
    - 依存: 項目1・2

---

## 11. Gate 4 Dangling Reference Check観点

**Theme 2 TrialスクリプトによるProduction関数直接置換・monkeypatchの
有無**: 確認した範囲(`er011_open112_trend_theme2_b_final_audio_rerun_01/
02.py`、`er011_open112_theme2_{a2,b1}_numeric_minimal_fix_rerun_04.py`、
`er011_open112_trend_synthesis_minimal_prompt_trial_09.py`、
`er011_open112_trend_engagement_reference_ab_trial_10.py`)で
`monkeypatch`/`setattr(gen...`/`patch(`等のパターンは**検出されなかった**
(grep確認)。全て`import er003_v1_n3_01_assemble as asm`のような通常の
import + `asm.stage_assemble_b1`等の無変更Production関数呼び出しで
完結している。

**確認できた依存関係**(いずれも実在・現存確認済み、Dangling Referenceなし):
- `er003_v1_n3_01_assemble.py`(`stage_assemble_a2`/`stage_assemble_b1`)
- `er003_v1_n3_01_scaffold_generate.py`
- `er003_v1_n3_01_tts_generate.py`
- `er006_audio_cost_pilot_02_shared_narration.py`
- `er003_v1_n3_01_articles_generate.py`(`COMMON_BLOCK_TEMPLATE`/
  `build_prompt`/`run_one_pattern`)
- `er003_v1_n3_01_evidence_compression_editor.py`(`run_lossless_editor`)

いずれもファイル存在・関数存在を確認済み(2026-09-08時点)。

**配線時に解消が必要な依存(将来の課題、現時点でDangling Referenceでは
ない)**:
- Trial-09が使用したアンカー文字列一致方式(`"【Spoken-first原則
  (数字の扱い)】"`の`.replace()`)は、正式Production配線時には
  §10項目3の通り明示的パラメータ化へ置き換える必要がある。文字列一致に
  依存したままだと、将来`COMMON_BLOCK_TEMPLATE`の文言が変わった際に
  Focus Module挿入が無警告で失敗しうる。
- rerun_03(`OPEN-112-THEME2-B1-REASSEMBLY-POST-WIRING-03`)を生成した
  スクリプトの実体(.pyファイル名)を本タスクでは特定できなかった
  (`er011_open112_trend_theme2_b_final_audio_rerun_03*.py`という
  ファイルが見当たらない)。レポート記述上はProduction関数
  `stage_assemble_b1`を無変更利用したと明記されているが、再現用スクリプト
  自体の所在は**不明**。

---

## 12. 配線設計メモ(実施した場合の想定スコープ、実装なし)

**変更ファイル候補**:
1. `er003_v1_n3_01_articles_generate.py`: `build_common_block()`へ
   `editorial_type_module_block: str = ""`相当の新規オプション引数を
   追加(既存`shared_point_blueprint_block`と同型パターン、既定値で
   後方互換維持)。`COMMON_BLOCK_TEMPLATE`側にも対応するf-string
   placeholderを追加。
2. Trend Synthesis Focus Module定数(`TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`
   相当)を、Trial専用ファイルから正式モジュールへ昇格(新規ファイル
   または既存モジュールへの追加、要判断)。
3. Mode判定ロジック(新規、現状コード0件)。自動化する場合
   (§10項目4)は新規モジュールが必要。
4. `er006_pool_pilot_01_writer.py::run_writer_for_theme()`: 
   `editorial_type`/`mode`引数を追加し、`build_common_block()`へ
   スレッド。
5. News Ledger供給経路(§10項目5の決定次第、既存Research pipeline
   モジュールへの接続または新規経路)。
6. (要否は§10項目11次第)Diagnostic Full Retry診断語彙モジュール
   (`er009_diagnostic_full_retry_modules_12.py`)への語彙拡張。
7. (要否は§10項目8次第)Ledger Deviation Checker
   (`er003_v1_en_direct_vfl_01_generate.py`)への新カテゴリ追加。

**回帰テスト対象**:
- `run_project_regression.py`全体(直近実測値はcollected 2110〜2157
  範囲、既知の無関係failure 3件を除き全PASSが通常のベースライン)。
- `build_common_block()`/`build_prompt()`/`run_one_pattern()`関連の
  既存単体テスト(後方互換確認、既定値""での旧来動作一致を必須)。
- Point Overlap QA/Point Value QA/Diagnostic Full Retry関連の既存
  fixture(News/Trend固有語彙を追加する場合は新規fixtureも必要)。
- Ledger Deviation Checker既存10種カテゴリのregression(新カテゴリ
  追加時は既存カテゴリへの影響がないことの確認必須)。

**runtime evidence取得方法**:
- Theme 2で使用済みの実テーマ(イラン・ホルムズ海峡、または新規収集
  テーマ)でProduction配線後のWriterを実際に呼び出し、A2/B1双方で
  Fact Checker/Ledger Deviation/Directional Precheck/Point Overlap・
  Value QAを実行、既存パターン(`er011_output/`配下への保存)を踏襲。
- 複数テーマ(最低2〜3件)でMode判定の自動化を試す場合は、境界事例
  (§1のMode判定基準表に近い際どい事例)を含めることを推奨。

**費用概算**(既存Trial実績からの類推、確定額ではない):
- Writer生成(A2×1・B1×1): Trial-09/10実績から数十円〜百円未満/テーマ
  程度(Evidence Compression・Fact Checker等の既存QA込み)。
- Reference Digest追加検証時: 約¥0.43/記事(Trial-10実績、既存pricing
  snapshot使用)。
- 完成音声化まで行う場合: Key Phrase・TTS・ASR込みでTheme 2実績
  (rerun_02実費約¥9.2、numeric precision fix分¥0.26〜¥4.73等)を
  参考に、1テーマ・A2/B1両レベル完成音声化で概算数十円〜¥20程度
  (cache hit率次第で変動)。
- 回帰テスト自体はAPI課金を伴わない(既存fixtureベース)。

---

## 「不明」とした項目

- rerun_03を生成した実際のスクリプトファイル名・所在(§11)。
- Diagnostic Full Retry診断語彙拡張・Ledger Deviation Checker新カテゴリ
  追加の技術的難易度・工数(コード変更を伴うため未着手、見積もり不可)。
- Mode判定自動化の精度(Trial実績なし)。
- News Ledger自動Research pipeline統合の技術的実現可能性(調査自体が
  未実施)。

---

## 参照した既存SSOT・Report(読み取りのみ)

- `OPEN_ITEMS.md`(OPEN-112〜116, 119, 121, 122, 126行)
- `DECISION_LOG.md`(該当エントリ、内容はOPEN_ITEMS.mdへの集約と重複する
  ため個別引用は省略)
- `CURRENT_SPEC.md`(冒頭changelog、QA/Human Review節)
- `FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`
- `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`
- `ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`(design reference
  only、Voices向けだが4層構造アーキテクチャ設計はTrend Synthesisにも
  同様に適用可能な内容)
- `er003_v1_n3_01_articles_generate.py`
- `er006_pool_pilot_01_writer.py`
- `er011_open112_trend_synthesis_minimal_prompt_trial_09.py`
- `er011_open112_trend_theme2_b_final_audio_rerun_01/02.py`
- `er011_open112_theme2_{a2,b1}_numeric_minimal_fix_rerun_04.py`
