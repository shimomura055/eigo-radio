## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01`(以下AUW)委任_01(Phase 1〜2: 既存仕様・Production経路の確認、承認範囲と変更箇所の特定、全Family×全Section適用マトリクス、実装設計書、競合一覧、test/evidence計画)。**本委任はRead-only+設計文書作成のみ**(Productionコード・SSOT・Prompt無変更、有料API 0)。設計はOpus独立技術レビュー(11-3条件A: 新しい処理フロー)を経てから実装委任へ進む。現在Status `APPROVED_FOR_PRODUCTION`(ユーザー正式決定2026-10-15)。到達目標は本管理ID全体で`PRODUCTION_WIRED`だが、本委任の到達上限は`DESIGN_READY_FOR_OPUS_A`。並行委任なし。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: 調査・設計(Read-only)。費用JPY0。時間見込み: 約2.5h(調査1.2h/マトリクス0.5h/設計0.8h)。並列化: 本委任内で調査項目A〜Eは独立(順不同で可)。
- 禁止: コード・Prompt・flag・test・SSOT・`user_test/`の変更。有料API(TTS/ASR/LLM)の実行。新規Trial。承認済み仕様の勝手な拡張・緩和(競合は「競合一覧」に挙げ、Fable/ユーザー判断へ)。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
- 既決事項を再質問しない: 本日ユーザーが決定した内容(下記原文§2〜§7)は決定済み。調査報告`docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md`で「既決」とされた項目(日本語SCG 10/11承認・否定保護・英語Tier1数値等価・警告ラベル/audit・M1/F1)も既決。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(全文Readは設計書・仕様書の該当節のみ)。G-1: git出力最小化。F-1: transcript退避不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。保存先: `docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`(**本委任文とユーザー指示原文を全文逐語保存。要旨化禁止**)。
T-2: 本委任はTTSなし(実装段で適用)。T-3: 費用0のためGuardrail文不要。

## ユーザー指示(原文・逐語。delegation_logへこのまま保存)

# Claude Code／Fable 実装指示
## ASR/TTS統一判定・数値保護是正・全Section Production Wiring

**管理ID：ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01**

**現在Status：APPROVED_FOR_PRODUCTION**  
**今回の到達目標：PRODUCTION_WIRED**

### 1. 目的

2026年10月12日の `ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01` で作成した統一設計を基礎として、今回ユーザーが正式決定した仕様をProductionへ反映する。

**英語・日本語、全Family・全Sectionで、ASRの誤認に起因する不要なTTS再生成を減らし、数値・否定などの重要な内容を保護しながら、自動量産できる統一音声検証基盤を完成させる。**

既存技術を最大限再利用し、重複実装・無用なTrial・無益なAPI消費を避ける。

### 2. ユーザー承認済みの基本フロー

各音声Sectionで以下を共通化する。

**TTS生成① → Primary ASR → NGならSecondary ASR**

両方NGの場合：

**TTS再生成② → Primary ASR → NGならSecondary ASR**

両方NGの場合：

**TTS再生成③ → Primary ASR → NGならSecondary ASR**

3回とも不合格の場合、既存の安全条件に従いLocal RewriteまたはHuman Reviewへ進む。

必須条件：

- Primary PASSなら、その時点でASR合格。Secondaryは不要。
- Primary NGなら、不一致の種類によらず原則Secondaryを実行する。
- Primary NG・Secondary PASSなら、**PASS_WITH_WARNINGとして採用**する。
- PASS_WITH_WARNINGはユーザーの事前承認を求めず、自動採用する。
- WARNING音声はユーザーが事後試聴できるリストへ自動登録する。
- Primary・Secondary両方NGなら次のTTS再生成へ進む。
- Secondaryが障害・利用不能の場合、PASS扱いせず、既存の安全な障害処理へ進む。
- 同じ音声に対するSecondaryの重複API呼び出しを防ぐ。
- 各TTS再生成では、原則として原稿・Prompt・モデル・Voice・速度を維持する。
- 既存の無音・反復・言語違い・異常長・発音品質等の独立QAは維持する。
- 既存のHuman Review Lock、承認・停止・予算上限は維持する。

### 3. 数値保護の設計是正

10月12日設計のS1には、漢数字の見逃しと表記差の誤検出が残っている。

**表記ではなく、数値の値と単位で比較できる仕組みに是正する。**

必須の正例・負例：

| 原稿 | ASR | 期待判定 |
|---|---|---|
| 三人 | 3人 | 同値として許容 |
| 三人 | 四人 | 異値として不許容 |
| 三十人 | 30人 | 同値として許容 |
| 三十人 | 40人 | 異値として不許容 |
| 十分（10分の意味） | 10分 | 文脈上同値の場合のみ許容 |
| 100円 | 百円 | 同値として許容 |
| 20% | 20 percent | 同値として許容 |
| 20% | 30% | 異値として不許容 |
| 25% | 26% | 異値として不許容 |

既存の英語Tier1数値等価・日本語表記ゆれ正規化・数値Validatorを優先的に再利用する。

**重要な安全条件：**

- 数値の異値を単純なSecondary文字起こし一致だけで誤PASSさせない。
- 否定の有無・意味の反転に対する既存の保護は維持する。
- 漢数字・算用数字・数詞・助数詞・単位・割合の値を比較する。
- 曖昧な読みの数値表現は、文脈を無視して機械的に同値化しない。
- 数値を含むだけでSecondaryを一律禁止する旧来の過剰制限は撤廃する。
- 既存の正規化仕様と競合・重複させない。
- 対象の初回・retry・fallback・regeneration経路で同じ判定を使用する。

この安全条件と「Secondary PASSなら採用」の原則が競合する場合は、**数値・否定などの明確な重大内容差を誤採用しないことを優先**する。保護すべき差異を警告だけで無条件に解放する仕様にはしない。

### 4. Connected Speech・M1の再利用

音の連結による自然な発音を、文字列不一致だけでNGにしてはならない。

既存の以下の仕組みを再利用する。

- B1 Connected Speech Validator
- Connected Speech Equivalence Layer
- M1 OOV Multi-Pronunciation
- F1残差検査
- Pronunciation Ledger
- 既存の音韻・同音語判定

`Melos said.` の2026年10月14日の実音声検証は重要なRegression基準とする。

- Full Story相当：12/12 PASS
- Dialogue・見出し相当：12/12 PASS
- M1新規救済：21観測
- M1起因の誤受理：0件

既存判定の安全条件を維持し、必要なRoleへ共有機構として適用する。

**自然な発音を許容することと、別の語・意味変更を無条件に許容することを混同しない。**

### 5. 適用範囲

**英語・日本語の全Family、Productionで生成する全音声Sectionを対象とする。**

最低限、次を含む。

- Full Story各Part
- Point本文・見出し
- Comment
- Preview
- Topic Intro
- In One Line
- Key Phrase英語
- Key Phrase日本語意味
- Key Phrase英語解説
- Dialogue／複数Voice音声
- その他Production生成対象の音声Section

Role一覧をProductionの実装・SSOTから洗い出し、適用漏れがないことを確認する。

**Section固有の既存例外は維持する。**

特に：

1. **Key Phrase**：学習対象の英語表現は変更しない。既存Minimal Prompt／English Language Lockとの整合を確認。全体のTTS3回仕様との競合は整理する。
2. **日本語Local Rewrite**：現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める。
3. **見出し・短文**：独立したQA・意味保護を維持する。
4. **A2の6%減速**：減速前後のASR検証・再生成回数・音声品質が整合すること。
5. **Dialogue**：複数Voiceの区分・話者帰属・既存Segment構造を維持する。

新しいSection固有の例外を実装都合で勝手に増やさない。

### 6. Local Rewrite・Human Review

TTS3回の不合格後は、既存のLocal Rewrite回復機構を利用する。

- 英語：意味・Fact・role・前後文脈・局所性・全文性を保持できる場合のみLocal Rewriteを許容。
- 日本語：現時点では原則Human Review。
- Key Phrase：学習対象の表現を別表現に置き換えない。
- 原稿の問題ではなくASR誤認と推定される場合は、安易に原稿を書き換えない。
- Rewrite後は同じ統一ASR判定を適用。
- Rewriteの発火・再TTS回数を正しく計数し、累積上限を守る。

既存のHuman Review承認を回避・解除してはならない。

### 7. 実装上の重点事項

- Primary／Secondary判定を共通化し、Role別の重複実装を避ける。
- 既存Cascadeと新統一フローを整理し、同一音声へのAzure二重呼び出しを防ぐ。
- ASR結果・判定理由・WARNING・コスト・所要時間を監査可能にする。
- PASS_WITH_WARNINGの最終試聴リストへの自動連動を完成させる。
- Production初回だけでなく、retry／fallback／regeneration／Local Rewrite後の経路まで整合させる。
- DEV／Trial専用スクリプトへの実装で終わらせない。
- 既存の正常な動作を壊さず、ロールバック可能性を確保する。

### 8. 実行方針・QCD

今回は新たな設計探索Trialではなく、**APPROVED_FOR_PRODUCTION仕様のProduction実装タスク**。

以下の順で進める。

1. Existing Spec／Decision／Production Pathを確認し、承認範囲と変更箇所を特定。
2. 全Family・全Sectionの適用マトリクスを作成。
3. 既存資産を再利用して数値S1・ASR判定・警告連動・経路整合を実装。
4. Unit／Validator／Integration／Regressionテスト。
5. 正式Production経路でruntime evidence取得。
6. 必要な不具合を是正して再検証。
7. SSOT・Git反映。
8. FableによるGate 3／Gate 4／Gate 7受入評価。

独立して進められる調査・テストは並列化し、無駄なAPI実行を避ける。既存の試験データ・音声・テストを最大限再利用する。

**既知の問題を同じTrialで再検証し直すことを目的にしない。**

### 9. 必須受入条件

以下すべてを満たすこと。

1. ユーザー承認済みのASR判定仕様と実際のProduction動作が一致。
2. 日本語・英語、すべてのProduction音声Sectionに適用。
3. Primary NG→Secondary PASSがWARNING付きで採用される。
4. Primary／Secondary両NGなら最大3回のTTS生成フローが成立。
5. 数値の同値・異値を適切に判定し、否定保護を維持。
6. Connected Speech／M1／F1の既存Regressionに悪化なし。
7. 試聴リストへのWARNING連動が動作。
8. Secondary二重呼び出し・予算超過・無限retryがない。
9. Production正式pathのruntime evidenceがある。
10. 必要なUnit／Regression／Integration testがPASS。
11. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSに実態を反映。
12. 必要なcommit／push／mergeを確認。
13. Dangling Reference Checkで問題なし。
14. 未解決USER_DECISION_REQUIRED・未配線APPROVED項目を明示。
15. Fableがユーザー承認内容・実装・証跡を独立照合。

**1項目でも未確認であればPRODUCTION_WIREDと報告しない。**

### 10. STOP条件と判断権限

既に承認済みの範囲では、実装・テスト・必要な技術的是正を継続してよい。

ただし、次の場合はSTOPして報告する。

- 新たなユーザー仕様判断が必要。
- 承認済み仕様との重大な競合が判明。
- 数値・否定などの重大な誤PASSが発生。
- 既存Production品質を大きく悪化させる。
- 予算・安全・権限・Human Review Lockに抵触。
- 全Section共通化に際して、承認済み範囲を超える例外が必要。

Trial結果からClaude/Fableが独自に新仕様を正式採用してはならない。

新たなTrialが必要と判断した場合も、承認なしに開始しない。

### 11. 最終報告

非エンジニアのPMが判断できるよう、以下を明示する。

- 全体の完了／未完了
- Family・言語・Section別のProduction適用状況
- 数値保護の是正結果
- ASR誤PASS／誤NGの検証結果
- WARNINGS・ユーザー試聴リスト
- TTS再生成回数・Secondary API回数・費用・時間
- Regression／Integration／runtime evidence
- commit・merge・SSOT更新
- 残るOpen Items・USER_DECISION_REQUIRED
- Fableの独立受入判定

**最終Statusは、すべての必須条件を満たした場合のみ`PRODUCTION_WIRED`。**

今回の作業はTrial成功やProductionへの一部配線で終了しない。ユーザー承認済み仕様を正式Production全経路で利用できる状態にし、その実証・ドキュメント・Git反映まで完了させること。

(ユーザー指示原文ここまで)

## KPI provenance欄 / Opus台帳更新

provenance: 該当なし(設計)。Opus台帳: 本体編集なし(条件Aレビューは次段でFableが委任。設計書にOpusへ渡す論点一覧を含める)。

## 事前指定Read一覧

1. `docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md` 全文(本日の既決/未決整理。資産マップの起点)
2. `er058_output/design/UNIFIED_FLOW_SPEC_V04.md` 全文(10/12統一設計。S1〜S7・D-1〜D-19の定義)、`er058_output/RECONCILIATION_FINAL_REPORT_01.md`:140-180(D一覧)
3. 日本語SCG: `er007_ja_secondary_asr_01.py`(Grep `def |EXACT_MATCH|NORMALIZED|exclude|数字|否定|C1|C2|similar|length`→判定関数・除外条件の所在)、`er007_ja_asr_validator_01.py`:60-70(`_DIGIT_RE`)・:255-270(否定)、`CURRENT_SPEC.md`:2000-2030(日本語SCG仕様)
4. 英語: `er006_preprod_hardening_01_validation.py`(Grep `def validate|PASS_WITH_WARNING|CONNECTED_SPEECH|NUMERIC_EQUIVALENCE|negation|percent|isdigit|TRUE_CONTENT_MISMATCH|ASR_VALIDATION_UNCERTAIN|secondary|SECONDARY`)、`er021_*`(Grep `-l "semantic_equivalence|secondary|PASS_WITH_WARNING"` → 英語ASR意味等価・Secondary経路の実装と配線先)、M1/F1: `rg -l "M1|OOV_MULTI|F1|residual" --type py | head`→該当モジュールの判定関数と呼出元
5. Cascade/retry: `er006_audio_retry_cascade*`(Grep `def |attempt|secondary|azure|HUMAN_REVIEW|LOCAL_REWRITE|max_attempts|budget`)、`er011_human_review_lock_01.py`:1-60、`er011_local_rewrite*`(Grep `def |英語|日本語|ja|en|role`)、`er011_output/attempt_history.jsonl`のフィールド名(先頭1行のキーのみ)
6. Role/Section一覧: `CURRENT_SPEC.md`(Grep `Full Story|Point|Comment|Preview|Topic Intro|In One Line|Key Phrase|Dialogue|解説|日本語意味|role`で見出し・表)、Production runner群(`er019_family_x_audio_production_runner_01.py`、`er026_family_z_fiction_production_runner_01.py`、News/Trend/Discovery/VoicesのProduction runner: `rg -l "TTS_EXECUTION_MODE|def stage_tts|tts_generation_results" --type py`で特定)のTTS呼出箇所とrole名・ASR検証呼出箇所(Grep `role=|segment_id|validate_asr|asr_validate|run_asr`)
7. 試聴リスト: `user_test/`の既存final pageの生成コード(Grep `warning|WARNING|試聴|review_list|human_review_queue`)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`のキー、既存「事後試聴リスト」相当の機構の有無
8. 数値資産: `rg -n "kanji|漢数字|kansuji|to_arabic|normalize_number|NUMERIC_EQUIVALENCE|percent" --type py -l` → 既存の漢数字/数値正規化の所在(10/13 JA Trialの値署名実装 `er0XX_*`含む)、既存test(`rg -l "NUMERIC|漢数字|percent" *test*.py`)
9. A2 6%減速: `rg -n "0\.94|6%|slowdown|SLOWDOWN|rate=" --type py` → 減速経路とASR検証の順序
10. SSOT: `OPEN_ITEMS.md` Grep `OPEN-28[6-9]|OPEN-29[0-1]|OPEN-287|OPEN-334|OPEN-333` / `docs/pm/USER_DECISION_REGISTER_01.md` Grep `#18|#24` / `DECISION_LOG.md` Grep `JA-ASR-ORTHOGRAPHIC|ASR-PHONETIC-EQUIVALENCE-M1-F1|ASR-M1-OOV|CONNECTED-SPEECH` → 既決仕様の原文(安全条件の文言)
11. `docs/pm/PM_GOVERNANCE.md` Grep `^### 11-3|^### 2-0|Gate 3|Gate 4|Gate 7` → 受入Gateの定義(設計書の受入計画に反映)

## 成果物(`er058_output/unified_all_roles_production_wiring_01/`配下、新規dir)

1. `DESIGN_01.md`:
   - §1 承認仕様の要約(ユーザー原文§2〜§7を逐語で引用し、各項目に「既存で充足/変更要/新規」を付す)
   - §2 既存資産マップ(モジュール・関数・配線先・test・評価記録。英語/日本語別。Primary/Secondary/数値/否定/Connected Speech/M1/F1/Cascade/HR Lock/LR/試聴)
   - §3 **全Family×言語×Section適用マトリクス**(行=Family[News/Trend/Discovery/Voices/X/Z…実在するもの全部]×Section、列=言語/現行Primary/現行Secondary有無/現行retry回数/現行数値・否定保護/Section固有例外/統一フロー適用後の挙動/変更箇所[ファイル:関数]/evidence取得方法)。**Role漏れがないことをProduction runnerのTTS呼出箇所で裏取り**
   - §4 統一判定の設計: 共通関数(例: `unified_asr_judge(role, lang, script, primary_result, secondary_fn)`)の入出力・状態機械(PASS/PASS_WITH_WARNING/NG→次TTS/3回NG→LR or HR/Secondary障害→既存障害処理)、Secondary重複呼出防止(同一音声hashのキャッシュ)、監査record項目(ASR結果・判定理由・WARNING・費用・所要時間)、既存Cascadeとの統合方法(Azure二重呼出排除)
   - §5 数値S1是正の設計: 値と単位で比較(漢数字⇄算用数字、%⇄percent、助数詞・単位、文脈依存「十分」は同値化しない方針)、ユーザー提示9例を**test caseとして固定**、既存Tier1/表記ゆれ正規化/Validatorとの統合(重複排除)、Primary/Secondary両方で適用、否定保護の維持
   - §6 **競合一覧(STOP候補)**: 承認仕様と既存承認済み仕様の競合を列挙し、各々「承認範囲内で解消可能(案)/ユーザー判断が必要」を判定。最低限検討: (a)日本語SCGの既存除外条件(C1固有名詞・類似度0.4未満・length NG・C2同形異音)と「不一致の種類によらず原則Secondary」「Secondary PASS→採用」の関係(数値・否定以外の除外をどう扱うか) (b)Key Phrase英語のMinimal Prompt/English Language Lock・既存retry仕様とTTS3回の関係 (c)現行Cascadeの試行回数・LR発火条件との整合 (d)D-5〜D-19のうち本指示で実質決定されたもの/未決のまま残るもの (e)日本語LRが現状どう動いているか(原則HRへ)
   - §7 変更箇所一覧(ファイル:関数、変更種別、ロールバック方法[flag不要: 承認済みのためProduction直配線だが、既存挙動へ戻せるcommit単位を設計])
   - §8 test計画(Unit: 9例+否定+Secondary障害+重複防止/Integration: 各Family runnerの初回・retry・fallback・regeneration・LR後/Regression: Melos said. 12/12・M1 21観測・誤受理0の再現方法[既存データ再利用、API不要か]) 
   - §9 runtime evidence計画(Production正式pathで、Primary NG→Secondary PASS→WARNING→試聴リスト、両NG×3→LR/HR、数値異値の不採用。**既存音声・既存失敗事例の再利用を優先、新規TTS/ASRの見積[call数×単価、JPY]**を明記。見積合計と内訳)
   - §10 実装分割案(委任_02以降の段階: 共通判定+数値S1+Unit → 各runner配線+Integration → evidence → SSOT。各段の受入条件と費用)
   - §11 Opus条件Aレビューへ渡す論点(5〜8点)
2. `APPLICABILITY_MATRIX_01.csv`(§3と同内容)
3. `docs/pm/RESULT_PACKET_AUW1.md`: (1)T-0 (2)既存資産マップ要旨 (3)マトリクスの行数とRole漏れ裏取り方法 (4)競合一覧(STOP候補)と各判定 (5)evidence費用見積 (6)実装分割案 (7)確認できなかった事項 (8)commit hash・raw URL(DESIGN_01)。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01_check.json`
- 上記Grep群(rg)。`git log --oneline --since=2026-10-10 -- er006_preprod_hardening_01_validation.py er007_ja_secondary_asr_01.py er007_ja_asr_validator_01.py | head -20`
- git: `git status --porcelain -- er058_output/unified_all_roles_production_wiring_01 docs/pm/delegation_log`、`git log --oneline -3`

## SSOT追記文

なし(設計段。SSOTはOpus条件A後の実装段で)。

## Git

明示add: `er058_output/unified_all_roles_production_wiring_01/DESIGN_01.md`、`APPLICABILITY_MATRIX_01.csv`、delegation_log(+`_check.json`)。コミットメッセージ: 「ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_01: 既存資産マップ+全Family×Section適用マトリクス+統一判定/数値S1是正の実装設計書+競合一覧+test/evidence計画(Opus条件A前)。Read-only、Production/SSOT無変更、JPY0」。push origin/main。

Fableは(3)(4)(5)を照合する(受領≠受入)。
