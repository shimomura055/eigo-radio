# ユーザー指示原文_03(2026-10-28、管理ID: FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 不具合調査・修正)

## Claudeへの指示｜『告げ口心臓』Narrator Voice変更の不具合調査・修正

『告げ口心臓』Fenrir版について、ユーザーが最終試聴した結果、**Standard／AdvancedともFull StoryのNarrator Voiceが従来のAoedeから変わっていない**との報告がありました。

対象：
https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_fenrir_01/index.html

### 1. 原因調査

以下を確認してください。

- 実際のTTS APIリクエストにFenrirが指定されていたか。
- 生成された音声ファイルが本当にFenrirによるものか。
- 正式組立・公開ページが新しい音声を参照しているか。
- キャッシュ、既存音声の誤再利用、Voice指定の上書きなどが起きていないか。
- Standard／Advancedの両方で確認すること。

**コード上のVoice設定やテストPASSだけで、実際の音声が変更されたと判断しないでください。**

### 2. 修正・再検証

既存承認範囲内で原因究明から修正・検証まで自律的に実施してください。

- Narrator＝Fenrir、老人＝Algieba、警官＝Schedarを維持。
- 本文・学習項目など、今回変更対象外の内容は維持。
- 正式Production経路、retry／fallback／resumeを確認。
- 公開ページが正しい音声ファイルを参照していることを検証。
- Standard／Advancedとも、実際の音声とTTS送信時のVoice指定の一致を証拠で示すこと。
- Fableによる独立受入評価を実施。

### 3. 完了報告

以下を簡潔に報告してください。

1. **真因**：なぜ変更されていなかったのか。
2. **修正内容**：何を直したか。
3. **検証証拠**：実際にFenrirで生成・公開されたことをどう確認したか。
4. **試聴URL**：Standard／Advancedとも確認できるページ。
5. **追加費用**：今回の修正費用。
6. **再発防止**：今回の誤った完了判定を防ぐための必要十分な対策。

CURRENT_SPEC／OPEN_ITEMS／DECISION_LOGおよび必要なGit反映まで実施してください。

なお、**ユーザー最終試聴PASSは未取得**です。修正完了後も、正式公開版への差替えはユーザー承認待ちとしてください。

今回の問題はVoice変更だけでなく、誤ったPRODUCTION_WIRED判定が出た点も重要です。Fableの受入判定に漏れがなかったかも調査してください。

作業中の詳細ログや逐次報告は不要です。修正・検証が完了した段階で、結果をまとめて報告してください。
