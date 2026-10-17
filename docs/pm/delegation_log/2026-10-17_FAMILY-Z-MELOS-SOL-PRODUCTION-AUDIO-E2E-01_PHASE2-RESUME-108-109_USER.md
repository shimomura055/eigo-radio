# Claude Code／Fableへの回答・指示
## Family Z「走れメロス」Production E2E — Phase 2再開

**管理ID：FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01（継続）**

### 1. ユーザー正式判断

**#108：追加費用100円を承認**

- 「走れメロス」Production完成作業に、既存300円枠とは別枠で**JPY100**を承認する。
- 期待費用：約45円。
- 追加100円を超過する見込みが生じた場合はSTOP。
- 既存費用と今回の追加費用を分離して記録する。

**#109：SRCのD1方式を正式採用**

Family Zの既存KP選定方式（Strategy L）を維持し、選定結果をPythonで元英文と照合する方式を採用する。

具体的には、

1. 従来どおり、AIが本文からKPを選定する。
2. 選定されたKPについて、Pythonが元英文の該当箇所・文ID・位置を特定する。
3. 対応が一意に確認できれば、出典情報を決定論的に記録する。
4. 対応を確認できない場合は、推測で補完せずSTOPする。

**目的はKPの出典保証であり、KP選定品質や選定方針の変更ではない。**

Family Xの候補ID選定方式（M2P0等）をFamily Zへ導入しない。既存KP選定結果を最大限再利用する。

本方式をFamily ZにおけるSource Reference Contractの正式実装方式として`APPROVED_FOR_PRODUCTION`に記録する。

### 2. Phase 2の実施範囲

先のユーザー指示およびPhase 1棚卸し結果に従い、承認済みのProduction整備を再開すること。

対象：

- Family Z「走れメロス」
- Story 3分割＋Comment 3つ
- Sol R0→R1→R2、Advanced→Standard調整
- Family Xと共通化する音声仕様
- Dialogue別Voice
- Source Reference Contract（D1方式）
- 正式Production E2E、ASR、Assembly、試聴ページ

新しい記事・Prompt探索・追加Trialは行わない。

### 3. 既存成果の再利用

既存`run_e2e_02`の以下を原則再利用する。

- Advanced／Standard本文
- Story 3分割
- Preview／Comment
- KP選定結果

原稿から無条件に作り直さない。

正式Production経路のprovenance・Stage整合を確認したうえで、新規runへ引き継ぐ。

過去のHuman Review承認は、Style変更後の新規生成音声へ自動継承しない。

### 4. 音声Production配線

Family Xで正式採用された以下の音声仕様をFamily Zへ適用する。

| Role | 適用Style |
|---|---|
| Full Story Narrator | PD06 |
| Standard日本語Preview／Comment | S3 |
| Advanced英語Preview | E1 |
| KP英語 | K2 |
| Standard KP日本語意味 | P8-KP |
| Advanced KP英語解説 | P7 |
| Standard英語Full Story | 既存6%減速 |
| ASR／音声品質 | 承認済みAUW |

既に適用済みのE1・K2等は、不要に再実装・再生成しない。

**FictionのDialogueはFamily Z固有仕様として別Voiceを維持する。** NarratorのPD06をセリフに一律適用しない。

retry／fallback／regeneration／resumeを含め、承認済みStyleとVoice割当の整合性を確認する。

### 5. SRC D1方式の実装条件

D1は、Family Zの既存Strategy Lに適合させるための実装方式である。

- KP選定Prompt・優先順位・候補供給方式は原則変更しない。
- Pythonによる出典特定は決定論的に行う。
- 既存のSource Consistency Gate／canonicalization等の品質検証を弱めない。
- 同一表現が複数箇所にあるなど、一意に特定できない場合は勝手に採用箇所を決めない。
- 曖昧・不一致の場合は既存の安全なSTOP／再確認経路と整合させる。
- 初回生成だけでなくretry／fallback／再生成でもSRCが有効であることを確認する。

Opus独立レビューで承認方式に抵触する重大な問題が見つかった場合は、独断でD2等へ変更せずSTOP・報告すること。

### 6. Production Wiring Gate

今回の到達目標は、対象仕様の`PRODUCTION_WIRED`と、正式E2Eの技術的完走である。

以下をすべて確認すること。

1. 正式Production初回経路への実装
2. retry／fallback／regeneration／resumeとの整合
3. Trial／DEV専用経路ではないこと
4. 正式runtimeでの実発火証拠
5. actual model_id・Style SHA・Voice・routingの一致
6. 必要なRegression／Validator／integration testのPASS
7. AUW／ASR・6%減速・Dialogue切替・AssemblyのPASS
8. Dangling Reference Check
9. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
10. commit／push／mergeの確認

Phase 1で確認された既存テストFAIL 9件は、原因を切り分けること。今回の変更に起因するFAILや必須品質GateのFAILを放置して完了扱いにしない。

### 7. 費用・作業効率

- 今回の追加承認枠：**JPY100**
- 期待：約JPY45
- Web／LLM／TTS／ASR／再試行等を含めて実費記録
- 日次JPY1,000のsoft budget維持
- 既存成果を最大限再利用
- 不必要な再生成・再検索を避ける
- 独立して安全に実行できるread-only作業・検証は並列化してよい
- Git変更・commit作業の競合を避ける

費用上限超過見込み、重大品質問題、未承認仕様変更が必要になった場合はSTOP。

### 8. Cross-Family運用・既存判断

Cross-Family同時Production配線原則は、先に承認された上位ルールとしてPM_GOVERNANCE／CURRENT_SPEC等へ正式反映すること。

今回のFamily Zへの音声仕様展開とSRC配線を、Family別のStatus表で追跡する。

Family固有仕様や明示的な不採用仕様は維持する。

Preview／Comment 1については既存方式を維持し、新しいA/B方式は採用しない。追加Trialは不要。

Risk FlaggerはFamily X固有仕様のため、Family Zには追加しない。

### 9. 最終報告

作業終了時に以下を簡潔に提示すること。

1. 「走れメロス」正式Production E2Eの完走可否
2. Standard／Advanced試聴ページURL
3. SRC D1方式の適用結果と実際の出典照合結果
4. PD06・S3・P7・P8-KP等のruntime適用証拠
5. Dialogue別Voiceの確認結果
6. 既存成果の再利用範囲
7. 実測費用／100円上限との差額
8. Regression／AUW／ASR／Assembly結果
9. 各仕様の`PRODUCTION_WIRED`判定
10. 未解決Open Item・ユーザー判断事項

**E2E技術的完走とユーザー試聴PASSは区別すること。**

最終音声が完成した段階で試聴ページを提示し、ユーザー判断を求めてSTOPする。

今回承認した#108・#109について、重複してユーザー判断を求めないこと。
