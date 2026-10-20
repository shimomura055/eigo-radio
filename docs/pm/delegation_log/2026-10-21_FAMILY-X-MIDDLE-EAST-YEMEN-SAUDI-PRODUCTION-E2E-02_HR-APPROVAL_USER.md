# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_04 / REGISTER #128

# 中東記事 E2E-02 — Human Review承認・音声完成指示

## 1. ユーザー正式判断

**Standard Comment 2のHuman Reviewを承認（PASS）する。**

ユーザーが実際に試聴し、「タイフーン機」と正しく発音されていることを確認済み。

- ASRの「台風機／台風期」は今回の特殊な認識誤りとして扱う。
- 発音判定仕様・Variant Layer・ASR許容条件は変更しない。
- 追加Trial・再発防止策・新規Open Itemは不要。
- 同種問題が頻発した場合のみ、ユーザーが対策の要否を判断する。

## 2. 実施作業

1. ユーザーの明示承認を記録し、Comment 2のHR Lockを既存の正式手順で解除する。
2. 承認済みの既存takeを採用する。不要なTTS再生成は行わない。
3. Standardの差分resumeを実行する。
4. 音声組立・Audio QA・必須Validator／Regressionを完了する。
5. Standard／Advanced両レベルの完成音声、全スクリプト、Key Phrasesを確認できる正式試聴ページを公開する。
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／必要なGit反映を整合させる。

**既存の承認済みProduction経路を使用し、新たな仕様変更や記事本文の再生成は行わないこと。**

## 3. 受入条件

- Comment 2の承認が正式記録されている。
- Standard／Advancedの音声が完成している。
- 既存の必須品質GateがPASSしている。
- retry／fallback／resumeの整合が確認できる。
- 正式Production runtime evidenceが残っている。
- Fableが実行結果を照合し、完了可否を独立判定している。

既存仕様・承認範囲内の不具合は自律的に修正・検証する。

重大な品質問題、予算超過、未承認仕様変更が必要な場合のみSTOPする。

## 4. QCD

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 不要なTTS再生成・LLM呼出・検索を行わない。
- 既存成果物を再利用して差分処理する。
- 独立作業は並列化し、不要な待機を避ける。
- 承認済み予算枠と日次1,000円（JST）を遵守する。

## 5. 完了報告

以下を簡潔に報告する。

1. **中東記事完成の可否と正式試聴URL**
2. Standard／AdvancedのAudio QA結果
3. HR Lock解除・差分resume・正式runtime evidence
4. 実費、所要時間、追加再生成の有無
5. SSOT／Git反映状況とFable最終受入判定
6. 残るユーザー判断（ある場合のみ）

**今回の目的は、ユーザー承認済みの音声を使い、最短・最小費用で中東記事を完成させること。追加の改善Trialや仕様変更は行わない。**
