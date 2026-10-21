# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03(Fallback調査)
# 緊急：Family X Full Story Fallbackの仕様・承認・Production実動作調査

## 目的

記事A「収入と性格」のStandard Full Story第2部で発動したFallbackについて、承認済み仕様と実装・実行結果が一致しているか確認する。

**調査が完了するまで当該Fallback音声の採用は保留。新たなTTS生成は行わない。**

## 1. 既存仕様と承認履歴

ChatGPTによるRepo確認では、CURRENT_SPECに以下の記載が存在する。

- N01は正式承認されたFull Story通常Style。
- Fallback takeはN01ではない。
- 2026-09-28のFAMILY-X-02では、Fallbackのminimal instructionに関して `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` を使う記載がある。

以下を照合する。

1. 当該Fallbackを承認したユーザー判断の日時・内容・適用範囲。
2. N01採用時に旧Fallbackを維持する判断があったか。
3. 現在のCURRENT_SPECとDECISION_LOGで、Fallbackの条件・Style・Human Review要件が整合しているか。
4. 未承認仕様や、廃止すべき旧経路へのDangling Referenceがないか。

## 2. 記事Aの実行証拠

Std Full Story第2部について、実際のログから次を確認する。

- 通常Take 1／2とFallback Takeの使用モデル・Voice・Prompt／Style全文またはSHA
- 各TakeのASR結果と不合格理由
- Fallbackが発動した正確な条件
- Fallbackで合格した検査と、人間承認が必要になった理由
- 減速処理・再検証の結果
- 通常Takeが本当に発音不良だったのか、ASRの誤認識・表記揺れだったのか

コード上の想定ではなく、今回のrunの証拠を提示する。

## 3. Fable独立評価

以下のいずれかに分類する。

**A：承認済み仕様どおり**

Fallbackは適法な既存Production経路であり、今回のHuman Reviewも仕様どおり。

**B：仕様・記録の不整合**

過去に承認された処理だが、CURRENT_SPECやN01との関係が不明確。仕様を勝手に変えず、事実関係と記録上の不足を整理する。

**C：未承認・不正な経路**

ユーザー承認のないFallback仕様がProductionで発動。影響範囲・再発防止策を報告し、ユーザー判断前に仕様変更・正式採用しない。

既存承認範囲内の明確な実装不具合は自律的に修正・無課金テストする。ただし、新仕様・新Styleの採用は禁止。

## 4. 報告

最優先で、次の4点を簡潔に報告する。

1. **Fallbackの実際のStyle／モデルは何か。**
2. **誰が、いつ、何を承認したのか。**
3. **なぜN01ではない音声がProduction候補になったのか。**
4. **今回の音声は承認候補として有効か、それとも仕様上の問題があるか。**

調査完了までは、記事AのHuman Review判断を求め直さない。記事B等の独立した完成作業は妨げない。

Fableの独立確認を必須とし、SSOT／Git更新が必要なら適切に反映する。新しい有料Trialは実施しない。
