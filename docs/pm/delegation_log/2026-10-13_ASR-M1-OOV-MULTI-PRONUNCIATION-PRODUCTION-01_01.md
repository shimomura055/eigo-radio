# 委任_01 ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 (2026-10-13)

## 範囲・制約(要点)
- 設計+offline評価(API 0 / JPY0)まで。Production py編集禁止(M1-F1委任_03・FAMILY-XZ-M2P0の並行領域は読取のみ)。到達上限Status: WIRING_DESIGN_DRAFT(Opus条件A待ち)。
- 出力: er077_output/m1_oov_multi_pronunciation_01/ 、script er077_m1_oov_multi_pronunciation_01_*.py 。SSOT編集権なし(SSOT_DRAFT_01.mdへ文案)。UDR-1更新は委任_02。
- 禁止: Ledger編集/confidence書換、ASR転写を見てから候補作成(後付け)、綴り類似のみPASS、候補無制限追加、Pattern拡張、Gate緩和、allow-list、Melos固有hardcode、git add -A/-f、amend/rebase/force push、stash/clean/reset --hard、共有ファイル追記test、外部プロセス再起動、監督ループ。
- STOP条件: 承認範囲超の発音許容基準/Gate緩和/合理的候補の定義不成立/誤PASS抑制不能/予算超過/既存仕様と重大矛盾。
- 設計固定: 候補集合C1(CMU全異読)・C2(Ledger全発音、confidence不問、英語のみ、IPA→ARPAbet決定論表)・C3(規則G2P)はFable既定=今回不採用、候補上限(例6)、candidates_fixed_before_asr記録、受理理由M1_MULTI_CANDIDATE_ACCEPT、F1残差点検の内側で動作、適用点(Primary#1/P2/S1/S2/forced-secondary L711/減速後rescue L146/dialogue/point_headings)、KPはFable既定=C1+C2のみで適用(両案影響記載)、Ledgerは読取のみ。
- offline評価: Melos12件(Before/F1のみ/本設計)、674ペア、合成8類型、unit test。報告: RESULT_PACKET_M1OOV.md。
- commit: 「ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_01: ...」+ Managed-ID trailer。

## ユーザー指示(原文)
(2026-10-13、管理ID ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01、全文)

# Claude Codeへの正式指示

**管理ID: ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01**

## 1. ユーザー正式決定

ASR M1のOOV(発音辞書未収録語)の扱いについて、ユーザーが以下を正式承認した。

**複数の合理的な発音候補が存在する場合、そのうち1つでも、連結発音・ASR転写・文章全体との音韻的整合性が成立すればPASSとしてよい。**

例: `Melos said`

- 「メロス」に近い読み方
- 「ミーラス」に近い読み方

この両方が合理的な候補であれば、双方を評価する。

どちらか1つで成立すればPASS。唯一の正しい読み方を人間が事前に指定する必要はない。

ただし、**任意の読み方を後付けで作り、ASR結果に合わせて合格させることは禁止**する。

Status: `APPROVED_FOR_PRODUCTION`

到達目標: `PRODUCTION_WIRED`

既存M1・F1の正式承認は維持する。

## 2. 判定原則

1. 辞書収録語は、信頼できる既存の発音情報を利用する。
2. 辞書未収録語は、既存Pronunciation Ledgerや利用可能な発音情報から合理的な候補を取得する。
3. 複数の合理的な読み方があれば、候補ごとに連結発音・音素同等性を評価する。
4. **1候補でも文章全体が整合すればPASS可能**とする。
5. 綴りが近いだけではPASSにしない。
6. 発音候補を無制限に追加しない。
7. 発音候補が成立しない場合は、既存の非PASS判定を維持する。

候補の出典・採用根拠・実際に一致した候補を追跡可能にすること。

ユーザーが毎回固有名詞の発音を指定する運用を前提にしない。

## 3. M1とF1の整合

M1は、合理的な発音候補と連結発音の同等性を判定する仕組み。

F1は、連結発音以外の内容差分を見逃さない仕組み。

**M1が成立しても、他の単語・時制・否定・数値等に不一致が残れば、文章全体を無条件にPASSしてはならない。**

以下を含めて整合を確認する。

- Pattern A/B/C
- Equivalence Layer
- Secondary ASR
- Standardの6%減速後再検証
- Advanced
- 初回・retry・fallback・regeneration
- KPを含む関連英語ASR経路

F1の既存承認済み是正内容と矛盾しないこと。

## 4. 実装方針

まず委任_02・Opusレビューで整理したOOV候補取得方式を、今回のユーザー追加承認に基づいて再評価する。

特に以下を区別すること。

- 外部または既存の信頼できる発音情報に基づく候補
- 綴りから規則的に推定される発音候補
- ASR結果に合わせて後付けで作られた候補

後者を無条件に許容してはならない。

**実装方法は既存機構の再利用を優先し、過度な仕組みを新設しない。**

既存Pronunciation Ledgerを利用できる場合は活用するが、低信頼の推測を高信頼の確定発音として登録しない。

新しい候補取得方式・信頼度基準に、今回の承認範囲を超える仕様判断が必要な場合のみSTOPして報告する。

## 5. 受入条件・Regression

### Melos 12音声

既存の同一12音声・同一ASR転写を再利用し、Before/Afterを比較する。

- 従来: 4/12 PASS
- Trial M1: 12/12 PASS

今回の正式実装でも12/12が得られるか確認する。

ただし、**12/12を達成するために判定基準を緩めてはならない**。

PASSしないものがあれば、候補の出典・不一致理由を明示する。

### 一般化・安全性

- 他の固有名詞・一般語でも成立すること
- 複数の発音候補のうち1つが一致するケース
- どの発音候補でも一致しないケース
- 綴りは近いが発音が異なるケース
- ASRが別の実在語へ誤転写したケース
- 正しい連結発音と、実際の語句欠落を区別すべきケース
- 文章後半に別の内容差分があるケース
- F1で是正した誤PASSの再発がないこと

Regressionで新たな誤PASSが出た場合、原因を調査し是正する。

## 6. 品質目標・QCD

ユーザーはゼロリスクを要求していない。

**最終的な品質目標は、1000本あたり不良1〜2本程度を許容する水準。**

これは目標値であり、今回の12音声によって達成が実証されたわけではない。

過剰に保守的な判定による不要なHuman Review、再生成、API費用も品質・運用上の問題として扱う。

品質とコスト・時間のバランスを評価し、誤PASSと誤NGの双方を確認すること。

ただし、安全性の未確認を「確率が低いはず」として無条件にPASS扱いしない。

## 7. Production Wiring Gate

以下をすべて満たすこと。

- 正式Production初回経路に実装
- retry / fallback / regenerationへの整合
- Secondary ASRへの適用
- Standard減速後・Advancedへの適用
- 必要Regression / Validator / integration test PASS
- 正式runtime evidence取得
- model_id / routing等の必要証跡
- CURRENT_SPEC更新
- DECISION_LOG更新
- OPEN_ITEMS更新
- USER_DECISION_REGISTER更新
- Git commit / push / merge確認
- Dangling Reference Check
- ユーザー承認内容とProduction挙動の一致

全項目が満たされるまで`PRODUCTION_WIRED`としない。

F1とM1はそれぞれ独立してStatusを管理してよいが、相互整合の検証を省略してはならない。

## 8. STOP条件

以下の場合のみ、ユーザー判断を求めてSTOPする。

- 承認範囲を超える新しい発音許容基準が必要
- 品質Gateの緩和が必要
- 合理的な発音候補の定義が成立せず、新しい仕様判断が必要
- 誤PASSを十分に抑制できない
- 予算・実行上限を超える
- 既存正式仕様との重大な矛盾が発生

単なる辞書未登録や実装上の問題だけを理由に、直ちにユーザーへ判断を差し戻さないこと。

まず既存仕様・発音情報・実装経路を調査し、承認済み範囲で自律的に解決する。

追加Trialや未承認仕様のProduction採用は行わない。

## 9. 最終報告

1. 複数発音候補の取得・判定方法
2. `Melos said` 12件のBefore/After
3. 他の固有名詞・一般語での一般化結果
4. F1との整合・誤PASS回帰
5. Standard減速前後・Advanced・retry・fallbackでの結果
6. 正式Production runtime evidence
7. 使用費用・QCD
8. SSOT・Decision Log・Open Items・Git反映
9. 未配線項目・残るユーザー判断事項

**ユーザーの目的は、現実的な品質水準で音声生成を自動運用できること。発音辞書の完全性や誤判定ゼロを追求すること自体を目的化しないこと。**

今回の追加承認に基づき、M1のProduction実装・検証を進めること。

(ユーザー指示 原文ここまで)
