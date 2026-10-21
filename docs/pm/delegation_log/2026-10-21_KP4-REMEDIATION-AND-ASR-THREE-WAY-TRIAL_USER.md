# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01 / ASR-THREE-WAY-COMPARISON-TRIAL-01

# Claude Code指示：KP4音声是正＋ASR 3方式総合比較Trial

## 目的

eigo-radioの音声品質検査について、品質を最優先に、処理速度・量産単価も含めた最適なASR構成を判断できる状態にする。

以下の2タスクを実施する。

- **Task A：記事B Standard KP4「take part」の問題音声是正**
- **Task B：OpenAI／Azure／ローカルWhisperの総合精度比較Trial**

Task Aはユーザーが実施承認済み。Task BはTrial実施承認済みだが、新しいASR構成のProduction採用は未承認。

両者を混同せず、独立して並列実行すること。

---

## Task A：KP4「take part」の問題音声是正

### Status・範囲

**既存の承認済み音声品質基準に基づく不具合修正。**

対象：
- Family X 記事B Standard
- Key Phrase 4「take part」
- 既存音声 `kp4_en.wav`

### 実施内容

1. 問題音声がMaster Storeから再利用されないよう、該当エントリを無効化する。正常な他エントリは変更しない。
2. 承認済みのProduction TTS仕様で音声を再生成する。
3. 既存のASR Validator・音声QAを実施する。
4. 「take part」が「take tart」「take heart」等に誤発音されていないことを確認する。
5. 正常な音声が得られたら、正式記事Bの該当箇所を差し替える。
6. Master Store、正式記事の音声、再生成・fallback・resume経路の整合を確認する。
7. 必要なRegression、SSOT、Git反映を完了させる。

**重要：**
- 現行ASR判定基準を勝手に変更してPASSさせない。
- Task Bの新方式を未承認のまま適用しない。
- 再生成だけで完成とせず、音声品質を確認する。
- 通常の品質検査で解決できない場合は、原因究明・修正を承認範囲内で自律的に進める。
- 発音の正誤を機械検査だけで確定できない場合は、試聴用音声と判断事項を報告する。

### 完了条件

問題音声が再利用されず、正しい音声への差し替えと既存品質検査が完了していること。

Production経路・runtime evidence・Regression・SSOT/Gitを照合してPRODUCTION_WIRED可否を報告する。記事全体のユーザー最終試聴PASSとは区別する。

---

## Task B：ASR 3方式 総合精度比較Trial

### Status

`TRIAL`。到達可能Statusは `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`。

**ASRのPrimary／Secondary変更、モデル切替、ValidatorのProduction仕様変更は禁止。**

### 1. 比較対象

| ASR | 現行の役割 |
|---|---|
| OpenAI `gpt-4o-mini-transcribe` | Primary |
| Azure Speech STT | Secondary |
| ローカル `faster-whisper small` | 独立検証 |

ローカルWhisperをPrimaryにする可能性も含め、先入観なく比較する。

必要性が実測で確認された場合は、Whisperの別モデルサイズもTrial内で比較してよい。ただし、無益なモデル探索は避ける。

### 2. 検証データの構成

**既存教材・過去Trial音声の再利用を優先する。**

少なくとも次の種類を含める。

**A. 正常音声**

- Key Phrase：短文、定型表現、固有名詞、造語、同音異綴り
- 本文：通常のニュース文章、長文、数字、固有名詞を含む文章、連結発音
- Standard／Advanced
- Family X／Z

原則として、過去に正しい発音が確認された音声を使用する。

**B. 問題音声**

- 既知の誤発音
- 子音・母音の取り違え
- 固有名詞の誤発音
- 単語の脱落・追加
- 数字・否定・意味を変える発音ミス
- 「take part」の既存NG音声

正常音声・誤発音音声の正解ラベルは、過去の人間試聴・信頼できる既存評価を優先する。ASR結果そのものを正解の根拠にしない。

過去教材だけでは十分な評価ができない場合は、必要な種類のTTSを新規生成してよい。ただし、正解発音・誤発音の確認方法を明確にし、追加音声数は必要十分に抑える。

正常音声と問題音声の構成比・選定理由を記録し、難例に偏った評価を避ける。評価用に意図的に作った音声は、通常量産の集計と区別する。

### 3. 比較方式

#### Phase 1：ASR単体の認識性能

同一音声を3方式に入力し、以下を比較する。

- 文字起こしの正確性
- 発音ミスの検出能力
- 正しい音声の過剰NG
- 固有名詞・同音異綴り・数字への対応
- 同一音声での認識安定性

単なる文字列一致率だけでは判断しない。

#### Phase 2：Production運用条件での比較

各方式の実際の補助機能を含めて評価する。

- OpenAI：Productionで使用しているPrompt等
- Azure：Phrase List、承認済み重み2.0
- Whisper：現行ローカル実行条件

Phrase Listが使えるケースと、今回の「take part」のように空になるケースを区別する。

Azure Phrase Listへ供給する発音情報の品質問題と、Azureモデル自体の認識性能を混同しない。

#### Phase 3：Validatorを含む最終品質

既存のValidator・救済機構・Cascadeを変更せず、候補構成ごとの最終判定を検証する。

候補：
1. OpenAI Primary → Azure Secondary（現行）
2. Azure Primary → OpenAI Secondary
3. Whisper Primary → OpenAI Secondary
4. Whisper Primary → Azure Secondary
5. その他、実測上有望な構成

Primary／Secondaryを入れ替えた場合に、現在の判定ルールや発動条件をそのまま使用できるとは限らない。

必要な変更と、その品質リスクを明示すること。

既存判定ロジックで比較できない構成についてはTrial専用の評価実装を使用し、正式Productionへ配線しない。

### 4. 主要評価指標

**品質（最優先）**

- 正常音声の正しいPASS率
- 誤発音音声の検出率
- 誤PASS率（誤発音の見逃し）
- 過剰NG率（正常音声の誤検出）
- 認識の安定性
- 固有名詞・同音異綴り・連結発音への対応

特に、誤PASSと過剰NGを混ぜず、それぞれ実例を提示する。

**Delivery**

- 1音声あたりの処理時間
- 1記事セットの想定検査時間
- 並列実行の可能性
- retry／fallbackによる時間増
- ローカルWhisperのCPU負荷・同時実行時の性能

**Cost**

- ASR API料金
- ローカルWhisperの計算資源・運用負荷
- 1記事セットの想定ASR原価
- 過剰NGに伴うTTS再生成費用
- Human Review増減による実質的な運用負荷

単純なASR呼出単価だけではなく、最終的な量産コストを比較する。

目標は70円／記事セット。品質を維持した原価削減を継続的に検討する。

### 5. Trial実施方針

事前にCURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・過去ASR関連Trialを確認する。

特に以下の既存結果を再利用する。

- `FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`
- Azure Phrase List重み1.0／1.5／2.0比較Trial
- byUs発音同等性の原因調査
- 過去のASR誤PASS／過剰NG検証
- 既存のHuman Review・再生成履歴

**品質上の重要な区別：**

今回のtake part Trialで確認されたのは「問題音声をAzureが検出したこと」であり、「Azureが正常音声も高精度に判定できること」ではない。

同様に、ローカルWhisperが同じNGを検出したことだけでPrimary採用に適すると判断しない。

試験対象数、音声の偏り、判定根拠、信頼性の限界を明示する。

同一音声の反復実行と、独立した複数音声での検証を区別する。

### 6. QCD・自律実行

- 既存の評価音声・正解ラベル・過去Trial結果を最大限再利用する。
- 独立する比較・集計作業は並列化する。
- 品質を守れる範囲で全体の完了時間を最小化する。
- API費用と残予算を管理する。
- 開発費は既存のJST日次予算1,000円および承認範囲を遵守する。
- 新規TTSが必要な場合も、Trial承認範囲内で必要十分な本数に限定する。
- 失敗が続く場合、同一条件の反復でなく原因・方法を見直す。
- 有効な結論が出た時点で追加検証を止める。

予算超過、新しい品質基準の必要性、重大な品質問題、またはTrial承認範囲を超える変更が必要な場合はSTOPし、ユーザー判断を求める。

---

## 7. Fable独立評価

FableはClaudeの試験結果を独立評価する。

特に以下を確認する。

1. 正解ラベルの信頼性
2. 通常音声と難例の偏り
3. 正常音声の過剰NGと誤発音の見逃し
4. ASR単体性能とValidator込み性能の区別
5. Primary／Secondary候補の品質・速度・原価
6. 既存Production仕様との整合
7. 追加検証の必要性と費用対効果

FableはProduction採用を代行しない。

---

## 8. 最終報告

Task AとTask Bを分けて報告する。

### Task A

- 問題音声の無効化結果
- 再生成音声の品質判定
- 差し替え結果
- Master Store・正式音声・retry/fallback/resumeの整合
- runtime evidence／Regression／SSOT／Git
- 完了Statusと未処理事項

### Task B

以下を経営・PM判断ができる形で報告する。

1. **結論：どのASR構成が最も有望か**
2. 正常音声のPASS率・誤発音検出率・誤PASS率・過剰NG率
3. Key Phrase／本文／固有名詞／数字等の種類別比較
4. 3方式の安定性と実例
5. 処理速度・原価比較（1記事セット換算）
6. Primary／Secondary入れ替えの利点・リスク
7. 現行Productionと候補構成の差分
8. Fable独立評価
9. 残存問題・必要な追加Trial
10. Production採用に関するユーザー判断事項

Trial結果は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類し、SSOT・OPEN_ITEMS・Gitへ記録する。

**重要：VALIDATEDはProduction採用を意味しない。ユーザーの正式承認があるまで、Primary／Secondary構成と既存ValidatorのProduction実装は変更しない。**

---

## 最終指示

**品質（Q）＞速度（D）＞量産単価（C）≫開発費用。**

Task Aは既存の品質基準に従って速やかに修正・完成させる。

Task Bは、ASRの単純なランキングではなく、eigo-radioの量産に最適なASR構成を判断できる客観的証拠を得ることをゴールとする。

十分な結論が得られたら過剰な検証を行わずTrialを終了し、ユーザーへ採用候補と判断材料を提示すること。
