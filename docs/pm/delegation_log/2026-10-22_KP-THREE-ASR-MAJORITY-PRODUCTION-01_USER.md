[受領日2026-10-22 / 受領者Fable→Sonnet(委任_01 KP3V-DESIGNが保存) / 管理ID: KP-THREE-ASR-MAJORITY-PRODUCTION-01(KP英語フレーズ3-ASR多数決のX/Z Production正式採用 APPROVED_FOR_PRODUCTION)。本文は逐語・無改変、本文2692文字・sha256=631a9561fb39de8c2e7adf61c534bfb541071686082af1f9468a81caa3d9aa85(本文=下記見出し行から末尾まで、先頭の本ヘッダ行は含まない)]

# Claude Code指示：Key Phrase 3-ASR多数決方式 — Family X/Z Production正式反映

## 1. 目的・正式承認

Key Phrase英語フレーズの発音判定について、**OpenAI・Azure・Whisperの3-ASR多数決方式を正式採用する。**

対象はFamily X/Z共通。既存の「OpenAI・Azure両方PASS必須」を置き換え、Production配線・テスト・runtime evidence・SSOT/Git反映まで完了させる。

- Status：`APPROVED_FOR_PRODUCTION`
- 到達目標：Family X/Z双方で`PRODUCTION_WIRED`
- Key Phrase英語解説文、その他の音声は現行判定ルールを維持する。

## 2. 正式判定仕様

| Primary（OpenAI） | Secondary（Azure） | Whisper | 最終判定 |
|---|---|---|---|
| PASS | PASS | 不要 | PASS |
| PASS | NG | PASS | PASS |
| PASS | NG | NG | NG |
| NG | PASS | PASS | PASS |
| NG | PASS | NG | NG |
| NG | NG | 不要 | NG |

**基本原則：3-ASR中、2つ以上がPASSなら最終PASS。**

処理効率のため、両方PASSならWhisperを呼ばない。両方NGの場合も、Whisperだけでは多数決PASSにならないため呼ばない。

片方だけNGの場合に限りWhisperを実行する。

既存の再生成回数上限、retry/fallback、安全STOP条件は維持する。

## 3. 既存検証の再評価

今回の実測結果：

- `think up`：OpenAI PASS／Azure NG／Whisper PASS → 新方式PASS
- `blurt`：OpenAI NG／Azure PASS／Whisper PASS → 新方式PASS
- `take part`旧問題音声：OpenAI・Azure・WhisperともNG → 新方式NG
- `take part`合格音声：3系統ともPASS → 新方式PASS

これまでの検証で品質改善の合理性は十分示されていると判断している。

**大規模な追加Trialを行わず、既存証拠・保存音声・テストを再利用すること。**

ただし、明確な誤発音の新規誤PASS、または既存品質条件との重大な衝突がないことを確認する。

## 4. Whisper導入・速度・費用

Whisperは既存検証で使用したローカル実行方式を基本とする。

- Whisper API利用料：0円
- 実際のCPU処理時間・実行環境・必要な依存ライブラリを確認
- 正式Production環境で利用できることを確認
- 既存検証で使用したsmall/mediumの結果と費用・速度を踏まえ、必要十分な構成を採用する
- 不要なモデル比較や再検証は行わない
- Whisper実行は片側NGのケースだけに限定
- 不要なTTS再生成の削減効果も評価する

既存Production環境でローカルWhisperが利用できない場合は、品質とQCDを満たす実現方法を検討し、重大な制約がある場合のみ報告する。

## 5. Family X/Z Production配線

両Familyの正式初回Production経路に適用する。

特に以下を確認する。

1. Primary・Secondaryの結果が分かれた場合のみWhisperが発動する。
2. 2/3 PASSで正常終了する。
3. 2/3 NGは従来どおりNGとして処理する。
4. Whisper実行エラーや未利用の場合に、勝手にPASSへ変更しない。
5. retry／fallback／regeneration／resumeに新判定が一貫して適用される。
6. Storeの既存音声再利用時にも新判定が反映される。
7. Key Phrase英語解説文とその他の音声には影響しない。
8. 既存の固有名詞アラーム方式との適用範囲の整合を確認する。
9. 両Familyで正式runtime evidenceを取得する。

従来の両PASS必須ルールが後続経路に残って新方式と矛盾しないことを確認し、不要な旧判定を整理する。

## 6. 受入条件・STOP

- Family X/Zで正式Production経路の判定が期待どおり動作
- 既存の正常音声・問題音声でRegression PASS
- 明確な誤発音を新たに自動PASSさせない
- 追加API費用0円
- 量産速度に重大な悪影響がない
- 必須Validator・integration test PASS
- 実際のmodel ID・Whisper実行環境・判定記録を確認可能
- SSOT・Git反映済み

重大な品質リスク、実行環境上の解決困難な制約、承認範囲・予算上限超過がある場合はSTOPして報告する。

軽微な問題は委任範囲内で自律解決する。

## 7. QCD・Closeout

品質（Q）＞速度（D）＞量産単価（C）。

開発費の日次原則1,000円（JST）を遵守し、既存の検証資産を再利用して最短で完成させる。

Fable独立評価を実施し、以下を簡潔に報告する。

1. Family X/ZのProduction配線Status
2. `think up`・`blurt`・`take part`の新旧判定結果
3. Whisperの正式runtimeでの発火証拠
4. 重大な誤PASSが発生していないことの検証結果
5. 追加コスト・処理時間・再生成削減効果
6. retry／fallback／Store再利用との整合
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映
8. Fable受入判定と残存Open Item

**すべてのGateを満たした場合のみ`PRODUCTION_WIRED`とする。**

既に正式承認された仕様について、重大な問題がない限り、追加のユーザー承認を求めずProduction配線まで進めること。