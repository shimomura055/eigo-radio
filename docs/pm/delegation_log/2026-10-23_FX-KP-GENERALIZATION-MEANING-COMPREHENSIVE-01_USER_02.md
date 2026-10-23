

<pasted_content id="a638">
# 指示｜Family X/Z Key Phrase品質改善・追加Trial・Open Items整理

## 1. ユーザー決定

| 項目 | 決定 | Status |
|---|---|---|
| A-1：Key Phrase一般化 | 正式採用。X/Z両方でProduction Wiringまで実施 | APPROVED_FOR_PRODUCTION |
| A-3 v3：Advanced英語説明 | 追加検証後に採用判断 | VALIDATED_LIMITED／USER_DECISION_REQUIRED |
| OPEN-476：bound→bind | 対応保留。Open Itemとして維持 | DEFERRED |
| OPEN-477：Python一括終了 | 再発防止を承認。正常解決時は報告不要 | 対応承認済み |

**重要：A-1のProduction Wiringは、A-3の追加検証結果と採否判断を待ち、可能であればまとめて実施する。**

ただし、A-1の配線準備・既存仕様との整合確認など、先行できる作業は並列で進め、不要な待機を発生させないこと。

## 2. A-1：正式Production採用

承認済みのA-1仕様をFamily X/Z共通で実装する。

- `this/that → a/an`等の参照語の不定化
- `him/her/me/us → someone`
- 本文存在ルール、5語以下ルール、既存の安全条件を維持
- 過剰な一般化を防ぐ既存・Trial検証条件を維持

A-3判断後、必要な実装をまとめ、以下を確認すること。

1. Family X/Z双方の正式初回Production経路への反映。
2. retry／fallback／regeneration／resumeとの整合。
3. Trial専用経路への依存・Dangling Referenceがないこと。
4. Validator・Regression・integration test PASS。
5. 正式runtimeでの発火証拠。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映。

両Familyとも証拠がそろうまで`PRODUCTION_WIRED`と判定しない。

## 3. A-3：Advanced英語説明の追加検証

### 目的

A-3 v3が特定の`draw a line`だけでなく、**幅広いKey Phraseに対して汎用的で正確な中心義の説明を安定して生成できるか**確認する。

### 検証方針

- 既存Trialデータ・結果を最大限再利用する。
- 意味や用途が異なる複数種類のKey Phraseを対象にする。
- 現行Production PromptとA-3 v3を同条件で比較。
- 本文中の意味との一致、記事固有条件の混入、過度な語義の限定、説明の自然さを確認。
- 改善例だけでなく悪化例・判断が分かれる例を明示。
- 既存の承認済み品質基準を変更しない。
- 新たな対策案の探索やPromptの際限ない調整は行わない。

検証規模・比較方法はFableが必要十分な範囲で設計すること。**追加費用は原則10円程度、上限20円。** 上限内で目的を達成できない場合は、その理由を報告する。

### Trial Closeout

結果を以下のいずれかで整理する。

- VALIDATED：正式採用に十分な根拠が得られた
- REJECTED：採用しない
- USER_DECISION_REQUIRED：追加のユーザー判断が必要

VALIDATEDでもA-3を無断でProduction採用しない。

**A-3の結果とFableの推奨を報告し、ユーザーの正式採否判断を受けてからProduction Wiringへ進む。**

## 4. OPEN-476：bound→bind

- 現時点では対応保留。
- OPEN-476を維持し、ユーザー判断によるdeferred項目として記録。
- 本件を理由にA-1/A-3の作業を不必要に停止しない。
- 未承認の仕様変更・追加Trial・修正を行わない。
- 将来の対応時に、原形化の既存仕様との整合を確認する。

## 5. OPEN-477：プロセス一括終了の再発防止

以下を実施する。

- `taskkill /F /IM python.exe`など、イメージ名による一括強制終了を禁止。
- 原則として自分が起動・管理するPIDのみを終了対象とする。
- PM_GOVERNANCEおよび該当agent定義に反映。
- 必要十分な確認を行い、Git・SSOTを更新。

**正常に対策・検証が完了した場合：**
- OPEN-477をCloseし、未解決Open Items一覧から除外。
- ユーザーへの個別完了報告は不要。

**問題が発生した場合のみ：**
- 原因、影響、未解決事項、必要な判断を報告する。

## 6. QCD・進行原則

- 品質 ＞ 完成速度 ＞ 量産単価 ＞ 開発費。
- A-3検証とA-1配線準備、OPEN-477対応は独立して並列化。
- 既存Trialを再利用し、不要なAPI費用・再生成を避ける。
- 不具合は承認範囲内で自律的に原因究明・修正・再検証する。
- OPEN-476は明示的な保留を尊重する。
- A-3追加検証は承認されたScope・費用上限を遵守。
- 承認済み品質基準に達した時点で完成とし、過剰な追加Trialを行わない。

## 7. 次回報告

**次回はA-3追加検証の結果を中心に報告すること。**

報告内容：
1. A-3の改善・悪化・維持の実績と代表例。
2. 既存Productionとの品質比較。
3. Fableによる採用推奨と残存リスク。
4. Trial費用。
5. ユーザーに必要なA-3正式採否判断。
6. A-1のProduction Wiring準備状況。

A-3採否判断後、A-1と合わせてX/Z双方のProduction Wiringを進める。

なお、OPEN-477が正常解決した場合、その完了報告は不要。

**ユーザー判断事項を最小化し、品質を守りながら最速でProduction完成まで進めること。**
</pasted_content id="a638">
