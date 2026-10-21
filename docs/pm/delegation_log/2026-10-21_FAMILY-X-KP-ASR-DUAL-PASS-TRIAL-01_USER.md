# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01

# Claude Code／Fableへの指示
## Family X Key Phrase音声QA — Primary／Secondary両方PASS方式のTrial-01

### 1. 目的・背景

Family X「漫画のキャラクターとAIで会話（byUs）」のStandard Key Phrase 4「take part」に、ユーザーから「take tart」と聞こえるとの指摘があった。

既存調査では以下を確認済み。

- Primary ASR：`Take part.` → PASS
- ローカルWhisper：`Take Tarte.` → 不一致（判定に未使用）
- Secondary Azure：Primary PASSのため未実行
- TTS再生成：なし
- 最終音声：誤発音の疑いが強いが、音声学的な確定は未了

Key Phraseは学習者が発音に注目するセクションであり、通常本文よりも誤発音の影響が重大。

**ユーザーは、Key PhraseについてPrimary／Secondaryの両方を必須とし、両方が既存の同音等価判定を含む品質基準でPASSした場合のみOKとする方式を、検証する方針に同意した。**

ただし、Production正式採用はTrial結果確認後に別途判断する。

### 2. Trial対象・条件

対象は既存のStandard Key Phrase 4「take part」の採用音声。

- Production run：`run_byus_01`
- 音声：`kp4_en.wav`（実際に採用されたTake 1）
- 既存音声をそのまま使用
- 同一音声・同一台本・同一判定条件を固定
- Primary／Secondary／ローカルWhisperで各10回の認識を実施
- 既存の同音等価判定・発音照合仕様を変更しない
- Azure Phrase Listは既存Production設定（重み2.0）を維持し、実際に使用したPhrase Listも記録する

キャッシュされた文字起こし結果を10回表示するのではなく、各回の認識処理を独立して実行すること。

ただし、外部API呼び出しの重複防止機構などが存在する場合は、その動作を確認し、実行回数を正確に記録する。

### 3. 実施方法

以下を10セット実施する。

| Trial | Primary | Secondary | ローカルWhisper |
|---|---|---|---|
| 1 | 実行 | 実行 | 実行 |
| 2 | 実行 | 実行 | 実行 |
| 3 | 実行 | 実行 | 実行 |
| 4 | 実行 | 実行 | 実行 |
| 5 | 実行 | 実行 | 実行 |
| 6 | 実行 | 実行 | 実行 |
| 7 | 実行 | 実行 | 実行 |
| 8 | 実行 | 実行 | 実行 |
| 9 | 実行 | 実行 | 実行 |
| 10 | 実行 | 実行 | 実行 |

各回で必ず以下を保存する。

- Primary ASRの文字起こし原文とPASS／NG
- Secondary Azureの文字起こし原文とPASS／NG
- ローカルWhisperの文字起こし原文とPASS／NG相当の評価
- Primary＋Secondaryの両方PASS方式による総合判定
- 判定理由（完全一致・同音等価・不一致等）
- API実費・実行時間

Whisperは今回の比較用とし、総合判定の条件には加えない。

### 4. 評価すること

**① 検出能力**

今回の疑わしい音声が、Primary＋Secondary両方PASS方式によって何回NGになるか。

**② 認識の安定性**

同一音声を10回認識させたとき、Primary・Secondaryそれぞれの転写がどの程度変動するか。

**③ 誤PASSの可能性**

両方PASSとなった場合でも、それを発音の正しさの証明とはしない。

同じ発音不良を両ASRが見逃す可能性を評価する。

**④ 原価・速度**

- 追加Secondaryの実測費用
- Key Phrase 5件×Standard／Advancedの10音声に適用した場合の費用見込み
- 追加処理時間
- NG増加に伴うTTS再生成・Human Reviewリスク

今回の音声1件だけで一般的な検出率・誤NG率を断定しない。

### 5. Fable独立評価

Fableは次を確認する。

- 実際に各ASRを10回実行した証拠
- 同一音声・同一設定で比較したこと
- 同音等価判定を既存仕様どおり適用したこと
- Primary／Secondary両方PASSの判定結果
- 誤PASS・過剰NGのリスク
- Production採用に向けて残る未検証事項

結果が期待どおりでなくても、Trial途中でPrompt・認識条件・判定基準を変更して再試行しない。

### 6. 費用・STOP条件

- 今回は承認済みの限定Trialとして実行する。
- TTS新規生成は禁止。
- 既存記事・音声・Master Audio Storeは変更しない。
- Productionコード・Prompt・Validator・ASR routingは変更しない。
- 日次開発予算1,000円（JST）と既存の個別予算枠を遵守する。
- 想定を超える費用や重大な技術的問題が判明した場合は停止して報告する。

試行間に不要な10分Cooldown等を設けない。独立実行・並列化が安全に可能な範囲で、品質と正確な計測を維持しながら最短で完了する。

### 7. Trial終了報告

10回分の結果を、次の形式で一覧表示する。

| 回 | Primary転写／判定 | Azure転写／判定 | Whisper転写／判定 | 両方PASS方式 |
|---|---|---|---|---|
| 1〜10 | | | | |

さらに以下を簡潔に報告する。

1. Primary PASS回数（10回中）
2. Secondary PASS回数（10回中）
3. Primary＋Secondary両方PASS回数（10回中）
4. 今回の疑わしい音声を何回NGとして検出できたか
5. 実費と量産時の追加費用見込み
6. Fableの独立評価と推奨

**Trial終了Statusは `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` のいずれかとする。**

今回の結果からProduction採用を自動的に決定しない。未承認の追加Trial・Production実装へ進まない。

### 8. 最重要事項

今回知りたいのは、**「take tart」のように聞こえる音声を、Primary＋Secondary両方PASS方式で検出できるのか**という一点。

対策を先に作るのではなく、まず既存音声で事実を確認すること。
