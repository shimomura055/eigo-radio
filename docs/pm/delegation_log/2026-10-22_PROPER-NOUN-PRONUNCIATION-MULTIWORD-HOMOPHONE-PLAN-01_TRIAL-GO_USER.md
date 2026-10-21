# PNMH Trial実行GO ユーザー原文(2026-10-22、逐語)
出典: Fable委任_04 §1。本文は無改変。

本文文字数=1497 / sha256(本文のみ,UTF-8)=55ac4069bcb036211ad5bca01a1058e717545e35ccc09aafb3a5a4d2b5386feb

---
## Claude Code指示：多語同音救済計画 — Trial実行GO

### 1. ユーザー決定

ASR 3方式比較Trialが完了し、以下を正式決定した。

- Primary：OpenAI `gpt-4o-mini-transcribe`（現行維持）
- Secondary：Azure Speech STT（現行維持）
- Azure Phrase List重み2.0（現行維持）
- ローカルWhisper：Production導入しない
- Primary／Secondaryの入替なし

これにより、**多語同音救済計画のASR構成確定待ちを解除する。**

### 2. 実行指示

先に検討・Opusレビューを経てFixした「#133 固有名詞英語発音供給＋多語同音救済計画」に基づき、Trialを実行すること。

実行前に、最新版のFix計画・レビュー結果・CURRENT_SPEC・関連する過去Trialとの整合を確認する。

計画がまだ正式にFixされていない場合、または未解決の重要なレビュー指摘がある場合は、Trialを開始せず、その事項だけ報告すること。

**Fix済みで実行条件が満たされていれば、追加承認を待たずTrialを開始する。**

### 3. Trialで確認すること

- `ByUs` ↔ `by us` / `buy us` のような1語対複数語の発音同等性を、正しく救済できるか。
- 原稿側の正しい英語発音を、信頼できる情報から取得・供給できるか。
- 既存の1語対1語の同音判定・各種救済機構を壊さないか。
- 発音が異なるものを誤ってPASSさせないか。
- Family X／Zの共通仕様との整合。
- 処理速度・量産原価への影響。

評価対象・判定基準・予算・STOP条件は、承認済みFix計画に従うこと。独断で変更しない。

### 4. 注意事項

- 既存ProductionのASRモデル構成・Azure重み2.0は変更しない。
- ローカルWhisperを新たなProduction依存として追加しない。
- Key PhraseのPrimary／Secondary両方PASS仕様は別指示系統で対応中。今回の作業と重複させない。
- Trial専用経路に限定し、未承認のValidator・Pronunciation Ledger・Production仕様を変更しない。
- 既存音声と過去Trial成果物を優先再利用し、不要なAPI呼出・TTS再生成を避ける。
- 独立した検証は並列化し、品質を守りながら最短で完了させる。

### 5. Trial Closeout

結果は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類する。

以下を簡潔に報告する。

1. Fix計画に対する実施結果
2. 救済できた具体例と救済できなかった具体例
3. 誤PASS・過剰NGの発生状況
4. 既存Validator・ASR Cascadeへの影響
5. QCD（品質・処理速度・量産原価・Trial費用）
6. Fable独立評価
7. Production採用に必要なユーザー判断

Trial結果と未決事項はSSOT／OPEN_ITEMS／Gitへ記録すること。

**Trial成功でもProduction採用・配線は行わない。ユーザー正式承認を必須とする。**

本指示はFix済み計画の実行許可であり、新たな仕様検討・計画変更の依頼ではない。
