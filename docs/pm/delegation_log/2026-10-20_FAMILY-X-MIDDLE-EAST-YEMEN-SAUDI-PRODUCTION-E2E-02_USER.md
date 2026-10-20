# ユーザー指示原文(2026-10-20)
管理ID: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 / 関連: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04

# Family X Research Trial Closeout・中東記事Production再生成

## 1. ユーザー正式決定

以下3点を確定する。

### ① Researcher改善Trial：全5方式REJECTED

- A〜Eの5方式はすべて不採用。
- 現行Researcher／検証仕様を維持する。
- 追加Trialは実施しない。
- Trial CloseoutとSSOTを正式決定に合わせて更新する。

### ② 背景Fact欠落：現行維持・Open Item管理不要

- 背景Fact欠落について、現時点では新たな改善策を導入しない。
- この問題を理由に新規Open Itemを作成しない。
- 既存Open Itemに残っている同課題も、今回の決定と整合するよう整理・Closeする。
- 今後、実際に問題が再発した場合、対策に着手するかどうかはユーザーが判断する。
- Claude／Fableの独断で改善Trialを再開しない。

### ③ 中東記事：Researchから再実行し、音声完成まで進める

**現行Production仕様のまま、Researchから再実行する。**

重要な受入条件は、**攻撃主体（Ansar Allah／フーシ派）がB3の採用Factに含まれること**。

- B3が攻撃主体を採用した場合：そのままWriter → TTS → Audio QA → Assemblyまで進め、完成音声と試聴ページを作成する。
- B3が採用しなかった場合：その試行の音声化は行わず、Researchから再実行する。
- Research再実行は、**初回1回＋再試行最大2回＝合計最大3回**。
- 3回ともB3で攻撃主体が採用されなければSTOPし、原因・各試行の結果を報告する。
- 未承認のPrompt・仕様変更、手動Fact挿入、B3の採用Factの強制変更によって条件を満たしたことにしてはならない。

## 2. 実行時の留意点

- Research → Fact Ledger → B3 → Writer → 音声化の正式Production経路を使用する。
- 各試行で、Researcherが攻撃主体をFact化したか、Ledgerに登録されたか、B3が採用したかを区別して記録する。
- B3で攻撃主体が採用された時点で、Researchの追加試行は不要。
- 既存の品質Gateはすべて維持する。攻撃主体の採用だけで記事全体を無条件PASSにしない。
- Writer本文にも攻撃主体が正確に反映されていることを確認する。
- 既存の承認済みTTS仕様、retry／fallback／regeneration／resumeを維持する。
- 原稿のユーザー事前確認待ちは設けず、条件を満たせば音声完成まで連続実行する。
- 独立作業を並列化し、不要な待機・日付分割をしない。
- 予算は既存の個別承認枠と日次1,000円（JST）を遵守する。最大3回のResearchを含め費用を管理し、上限超過が見込まれる場合は超過前にSTOPする。

## 3. 完成条件・PM Gate

- 攻撃主体がB3の正式採用Factに含まれる。
- Writer本文にも正確に反映される。
- 全必須品質GateをPASSする。
- Standard／Advancedの対象音声が完成する。
- 完成音声・全文原稿・Key Phrasesを確認できる試聴ページを公開する。
- 正式Production経路のruntime evidenceを記録する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを整合させる。
- Fableが実行証拠を確認し、独立評価する。

## 4. 最終報告

以下を簡潔に報告する。

1. **中東記事は完成したか／試聴URL**
2. Research試行回数（最大3回）と各回の結果
3. 攻撃主体のFact化 → Ledger登録 → B3採用 → Writer反映の証拠
4. Standard／Advancedの音声品質Gate結果
5. 実費、量産単価への影響、所要時間
6. Production経路・SSOT・Git反映状況
7. 未解決事項と必要なユーザー判断（ある場合のみ）

**今回の目的は、新しいResearch仕様を探索することではなく、現行の承認済みProduction仕様で、攻撃主体を正しく含んだ中東記事を完成させること。**

品質を守りながら、完成まで最短で進めること。
