# FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01 — Discovery deferred項目の分類(読み取り専用)

管理ID: FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01(Lane A-2)
実施日: 2026-09-08
実施者: sonnet-worker(読み取り専用。新規実装・SSOT編集・API呼び出し・Git操作・
他Lane[A-1/A-3/B]参照はいずれも行っていない)

前提: Discovery(Family A内の1枝)のdeferred項目のみを対象とし、Trend Synthesis
とは別管理として扱う(共通化候補は「候補」として記録のみ、正式共通仕様化は
提案しない)。直近の事実確認は`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`
(2026-09-08、同日実施、7節「Discovery」参照)で、本タスクはその内容を
Discovery視点で再分解・不足分を補ったもの。新規のSSOT探索で追加発見した
事実（ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01の実行時系列、
OPEN-107のWITHDRAWN確認等）を含む。

---

## 1. 用語整理(根拠付き)

- **Discovery/Why**: ABC Family大枠(2026-09-04ユーザー決定、
  `OPEN-112-...-TOPIC-SSOT-AND-FAMILY-FRAME-02`)における「A=Discovery/Why
  +News/Trend Synthesis」の1枝。CURRENT_SPEC.mdに"Discovery"という語は
  存在しない(grep 0件、全620行)。
- **4-layer構造**: Layer1 Common Writing Contract / Layer2 A Family Common
  Skeleton / Layer3 Focus Module / Layer4 Article-specific Inputs。
  Discovery/Whyが最初にこの4層で設計・Trial実装された
  (`OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05`、2026-09-04、
  `er011_open112_a_family_4layer_prompt_trial_05.py`内
  `DISCOVERY_FOCUS_MODULE_BLOCK`)。News(Major/Daily・Trend Synthesis)は
  後日(2026-09-05、`OPEN-112-NEWS-MODE-DESIGN-08`)同じ4層フレームで
  設計されたが、read-only設計のみでコード実装・Trial実行は0件。
- **Layer3 Focus Module(Discovery)**: `DISCOVERY_FOCUS_MODULE_BLOCK`
  (Trial-05、単一Anchorへの1箇所挿入方式)。Phase A機械的再構成一致テスト
  (`clean_single_insert_confirmed=true`)で手続きの妥当性を確認済み。
  Production Writer(`er003_v1_n3_01_articles_generate.py`・
  `er006_pool_pilot_01_writer.py`)への配線は**行われていない**(grep監査
  0件、DECISION_LOG.md 1223-1238行台で「実装対象になり得る箇所は最小限、
  `run_writer_for_theme()`と`build_common_block()`/`COMMON_BLOCK_TEMPLATE`
  の間のみ」と特定済みだが未実装)。
- **Engagement根底指示**: Writer根底指示へのInteresting/Engaging/
  Entertaining原則+Storytelling原則(時系列列挙禁止)の追加案。
  **管理IDの帰属はTrend Synthesis側**(`OPEN-112-TREND-ENGAGEMENT-
  REFERENCE-AB-TRIAL-10`・`OPEN-112-ENGAGEMENT-REFERENCE-CROSS-TOPIC-
  AB-TRIAL-11`)。実際にA/B比較Trialが実施されたのはTrend Synthesis記事
  (Theme2「若者の旅行」等)のみで、Discovery記事(No.18等)でのEngagement
  A/B Trial実施記録は**見つからなかった**。したがってEngagement根底指示は
  「Discovery固有」ではなく「Trend Synthesis管理IDの下で検証されたが、
  Writer根底指示という性質上Discoveryを含む全A Familyへ影響しうる項目」
  という位置づけが正確。

---

## 2. Discovery関連の主要管理IDと到達点(時系列)

| 管理ID | 日付 | 内容 | 到達点 |
|---|---|---|---|
| `ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01` | 2026-09-02 | No.18「Why Is It So Hard to Ignore a Notification?」をDiscovery/Whyラベルで正式Production実行。**既存Production Wired仕様のみ使用**(4-layer Discovery Moduleは未使用、Trial-05より前の実行) | A2=完成音声`USER_FINAL_AUDIO_REVIEW_REQUIRED`。B1=記事・Support・Key Phrase完成、`in_one_line`が3attempt ASR不合格でAudio Validation GateがSTOP(新規OPEN-107) |
| `OPEN-107` | 2026-09-02発見 | No.18 B1 "opened"→"open"語尾脱落(新TTS失敗モード候補) | **`WITHDRAWN`**(2026-09-03、B1 Connected Speech Validatorへ置換済み。`FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`表(5)で確認) |
| `OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05` | 2026-09-04 | Discovery/Why Layer3 Focus Module設計・No.18 Article-only Trial | `VALIDATED`(手続き上の結論) |
| `OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07` | 2026-09-05 | Discovery 4層仕様のProduction Adoption Readiness整理。Fact Checker `REVIEW_REQUIRED`件数がBaseline比増加(A2: 0→3、B1: 3→5、いずれもblockingなし)する「解釈強化リスク」を発見 | `USER_DECISION_REQUIRED_WITH_RISK` |
| `PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01` | 2026-09-05 | OPEN-112行7論点のうち4件は明示defer、残り3件(Discovery採否/Engagement採否/News Ledger自動Research化)は個別ユーザー判断要と整理 | `USER_DECISION_REQUIRED`維持 |
| `PM-CLOSEOUT-CONSOLIDATION-08`(第4弾ユーザー決定6.) | 2026-09-08 | OPEN-119/122/118・OPEN-112本体残件(Discovery 4-layer Focus Module・Engagement根底指示・News Ledger自動Research経由)は追加Trial・Production変更を行わず据え置く、とユーザーが決定 | **`DEFERRED`**(現状の正式status) |
| `FAMILY-A-DESIGN-FIX-INVENTORY-01`/`FAMILY-A-BRANCH-FACT-CHECK-02` | 2026-09-08 | 読み取り専用棚卸し(本タスクと同日、Lane A-1相当の先行タスク) | Discovery=「共通配管はPRODUCTION_WIRED済み(Discovery固有ではない)、Layer3自体はVALIDATED止まりでDEFERRED」と整理済み |

---

## 3. OPEN-112残件のうちDiscoveryに属するもの

OPEN_ITEMS.md OPEN-112行は単一の巨大追記型エントリで、7論点(2026-09-05
PM-HANDOFF整理時点)+その後の追加論点を内包する。Discoveryに直接属するのは
以下の1論点のみ:

- **Discovery 4-layer Focus Module Production採用可否**
  (`OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-
  REGISTER-07`起点) — status: `DEFERRED`(2026-09-08、追加Trial・
  Production変更なしで据え置き)。

他の6論点(Trend overclaim severity方針・News/Trend向けPoint Overlap閾値・
Reference Digest追加検証要否・Point長さ目安・Engagement根底指示採否・News
Ledger自動Research化)はTrend Synthesis管理ID配下の論点であり、Discovery
固有ではない(Engagement根底指示のみ「Discoveryへも波及しうる候補」として
4節へ記載)。

---

## 4. 4分類

### (A) 既にVALIDATED済み

| 項目 | 管理ID | 根拠 | 最終更新 | 区分 |
|---|---|---|---|---|
| Discovery/Why Layer3 Focus Module(Trial手続き自体) | `OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05` | DECISION_LOG.md 1170-1187行、Phase A機械的再構成一致テスト`clean_single_insert_confirmed=true` | 2026-09-04 | Discovery固有 |
| Diagnostic Full Retry経路がDiscovery Moduleを保持し続ける設計(実装対象箇所の特定含む) | `OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-...-07` | DECISION_LOG.md 1223-1238行 | 2026-09-05 | Discovery固有 |
| Discovery記事一般構造(共通Production配管: Writer→Editor→Fact QA→Key Phrase→TTS retry cascade→Assembly) | OPEN-110/111/113/115/116/118/119/121/122/123/127/128等 | `FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`表(1) | 2026-09-08 | **全テーマ共通(Discovery固有ではない)** |
| Trend Synthesis Engagement/Storytelling原則(施策1)のA/B効果(時系列列挙→反転・対比構成) | `OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10` | DECISION_LOG.md 978行台 | 2026-09-05 | Trend Synthesis実施、**Discoveryへの共通化候補**(未検証) |

### (B) USER_DECISION_REQUIRED(≒DEFERRED、ユーザー判断待ち)

| 項目 | 管理ID | 根拠 | 最終更新 | 区分 |
|---|---|---|---|---|
| Discovery 4-layer Focus Module Production採用可否(解釈強化リスクとのtrade-off判断) | `OPEN-112`本体残件 | OPEN_ITEMS.md OPEN-112行末尾「本体残件: `DEFERRED`」、DECISION_LOG.md `PM-CLOSEOUT-CONSOLIDATION-08` | 2026-09-08 | Discovery固有 |
| Engagement根底指示のProduction採用可否 | `OPEN-112`本体残件 | 同上 | 2026-09-08 | Trend Synthesis管理・**Discovery共通化候補** |
| News Ledger自動Research経由化 | `OPEN-112`本体残件 | 同上 | 2026-09-08 | News全般(Discoveryは対象外、Ledgerの調達方式論点) |

### (C) 追加Trial必要(設計要点のみ、実行しない)

| 項目 | 目的 | 対象 | 成功基準 | 費用概算 |
|---|---|---|---|---|
| Discovery Layer3 Focus Module「解釈強化」リスクの緩和検証 | Fact Checker `REVIEW_REQUIRED`増加(A2 0→3, B1 3→5)の原因となる複数Evidence統合的解釈のPrompt制御可否を検証 | No.18相当のDiscovery記事1〜2件、A2/B1 | REVIEW_REQUIRED件数がBaseline相当まで低減、Ledger Deviation Checkerの検出範囲に変化なし(過検知/検知漏れなし) | No.18 4-layer Trial実測(¥90.9級)と同水準、¥100前後/記事と概算(実測なし、参考値) |
| Engagement根底指示のDiscovery記事への適用効果検証(共通化候補の実証) | Trend Synthesisで確認済みの「時系列列挙→反転・対比構成」改善効果がDiscovery/Why記事でも再現するか | Discovery記事1本(新規または既存テーマ再生成)、B1優先 | Point Overlap/Value QA PASS維持、Fact Safety blockingなし、構成改善が主観・機械的双方で確認 | ¥60〜165程度(Trial-07/Trial-10相当の過去実測を参考に概算、実測なし) |

### (D) 不要・obsolete

| 項目 | 理由 | 管理ID |
|---|---|---|
| OPEN-107(No.18 B1 "opened"→"open"新TTS失敗モード) | `WITHDRAWN`。B1 Connected Speech Validator(OPEN-110)へ置換済みで、個別対応の必要が構造的に解消 | OPEN-107 |
| ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02・ER-010-EDITORIAL-TYPE-WRITER-ARCH-01(未追跡設計文書) | ユーザーが「正式仕様として採用せず、参考資料(design reference only)」と明示位置づけ済み(2026-09-04)。deferred項目としての解消対象ではなく、参照専用のまま維持で足りる | OPEN-112行追記(2026-09-04) |

---

## 5. deferred解消に必要なユーザー判断項目(最小単位)

1. **Discovery 4-layer Focus Moduleを`APPROVED_FOR_PRODUCTION`とするか**
   - 選択肢: (a)解釈強化リスクを許容し採用へ進む、(b)Prompt側で解釈強化を
     抑制する追加Trialを先に依頼する(上記4(C)参照)、(c)採用を見送り
     現行の無区別Writer経路を維持する
   - 推奨: 明示なし(判断はユーザーに委ねる性質の項目のため、本タスクでは
     推奨を提示しない)
   - 依存関係: (b)を選ぶ場合、追加Trial実施後に再度この判断へ戻る

2. **Engagement根底指示をDiscoveryへも共通適用する検証を行うか**
   - 選択肢: (a)Trend Synthesisのみで維持しDiscoveryへは適用しない、
     (b)Discovery記事での効果検証Trialを依頼する(上記4(C)参照)、
     (c)Trend Synthesis側の採否判断が出るまで両方保留する
   - 依存関係: Trend Synthesis側のEngagement採否判断(Lane A-1/OPEN-112本体
     が扱う論点)と連動する可能性がある。本タスクではLane間の独立性維持の
     ため、Trend Synthesis側の判断状況には踏み込まない

3. **ER-010-EDITORIAL-TYPE-*設計文書2件を正式Decision化(git commit)するか**
   - 選択肢: (a)参考資料のまま維持(現状)、(b)正式Decisionへ昇格させ
     git追跡化する
   - 依存関係: 1.の採否判断と直接連動(Discovery Module採用が決まれば
     設計文書の正式化も併せて検討する流れが自然)

---

## 6. Gate 4観点: Dangling Reference Check(実施結果)

Production Writerコード(`er003_v1_n3_01_articles_generate.py`・
`er006_pool_pilot_01_writer.py`)を対象に以下をgrep実施:

```
grep -rn "DISCOVERY_FOCUS_MODULE\|editorial_type\|Editorial Type\|Discovery/Why\|Engagement" \
  er003_v1_n3_01_articles_generate.py er006_pool_pilot_01_writer.py
→ 0件
```

```
grep -rln "DISCOVERY_FOCUS_MODULE\|editorial_type" --include="er0*.py" .  (er011 Trial系・er012 Lane B系を除外)
→ 0件
```

**結果**: Discovery関連のTrial-only仕様・未承認Focus Moduleへの参照
(dangling reference)はProduction Prompt/コードに**発見されなかった**
(`FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`の先行監査結果と一致)。

---

## 「不明」とした項目

- Engagement根底指示のDiscovery記事への適用効果(実施記録なし、推測で
  補完していない)。
- ER-010-EDITORIAL-TYPE-*設計文書2件の内容そのものの技術的な出来栄え
  (本タスクでは開封していない、既存位置づけ[参考資料]の確認のみ行った)。
- Discovery 4-layer Focus Module採用時の具体的Prompt文言修正案(4(C)の
  追加Trialが必要という設計要点のみ記載し、文言案自体は作成していない)。
