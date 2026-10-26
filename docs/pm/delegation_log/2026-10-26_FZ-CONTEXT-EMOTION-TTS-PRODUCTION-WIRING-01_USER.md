<!-- ユーザー正式決定原文(2026-10-26)。逐語。Fable委任_01同梱の写しから転記 -->
# Family Z｜文脈・感情付きTTS＋Fallback 正式Production Wiring

## 1. ユーザー正式決定

Family Zの「文脈・感情付きTTS」を正式採用する。

**Status：APPROVED_FOR_PRODUCTION**
**目標：PRODUCTION_WIRED**

対象はFamily Zのセリフ音声、Standard／Advanced両方。

Family X/Yには適用しない。既存のナレーション、Key Phrase、その他のTTS仕様も変更しない。

## 2. 正式採用するRetry／Fallback仕様

セリフ単位で以下を実行する。

**1回目：文脈・感情付きTTS**
- PASS → 採用
- NG → 即時Retry

**2回目：文脈・感情付きTTS**
- PASS → 採用
- NG → 10分クールダウン

**3回目：従来方式TTSへFallback**
- 文脈・感情情報を付加しない、従来の承認済みTTS指示・Styleを使用
- PASS → 採用
- NG → 既存のLocal Rewrite処理へ

Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う。

**TTS総試行回数は初回を含め最大3回。** Fallbackを追加の4回目として扱わない。

Local Rewriteも既存の回数上限・安全条件を維持し、無制限な再生成を発生させない。

## 3. Production実装の必須条件

### ① Trial方式の正確な移植

今回の『猿の手』『走れメロス』全編Trialで使用した文脈・感情情報生成方式とTTS指示を、承認済み仕様として正式Productionへ移植する。

未承認のPrompt改変、感情分類方式の変更、品質基準の追加・緩和は行わない。

Trialの一時コードを単に呼び出すのではなく、正式初回Production経路として機能させる。

### ② Retry／Fallbackの一貫性

以下の経路すべてで同一仕様を保証する。

- 初回Production生成
- retry
- fallback
- regeneration
- resume
- 中断後の再開
- Local Rewrite
- Human Review Lock

失敗が発生した場合も、残りの試行回数・状態・生成方式を正しく引き継ぐこと。

特に、再開によって1〜2回目の文脈・感情付きTTSを不必要に再実行したり、3回の上限を超えたりしないこと。

### ③ 従来方式への正確な復帰

3回目のFallbackでは、今回の文脈・感情情報をTTS指示から完全に除外する。

従来方式のVoice、Style、速度、発音制御、品質検査を維持する。

文脈・感情付き方式の一部設定が残り、従来方式と異なる音声になることを防ぐ。

### ④ 既存の品質・安全仕様

以下を維持する。

- ASR Primary／Secondaryの承認済み判定規則
- 発音・内容一致検査
- ASR表記揺れへの救済
- Local Rewrite／Natural English QA
- Human Review Lock
- STOP条件
- 音声の組立・音量・速度に関する承認済み仕様

特に、ASRの表記違いだけを理由に不要なTTS再生成を行わないこと。

## 4. Trialで判明した問題の扱い

全編Trialでは、次の問題が観測された。

- 一部セリフの不自然な話速
- 長いポーズ
- 地の文とセリフの音量差
- 一部の声の高さの不安定さ
- 『走れメロス』Standardの比較音量条件不一致
- 53件中1件のASR／QA不合格

これらを隠さず、Production品質への影響を確認する。

既存の承認済みValidator・組立・品質条件に反する問題は、承認範囲内で是正する。

ただし、Trial結果を理由に独自の新しい品質基準を設けたり、承認した文脈・感情方式を変更したりしない。

実質的な仕様変更が必要なら、理由とQCD影響を示してUSER_DECISION_REQUIREDで報告する。

## 5. 量産単価・QCD

**Family Z専用のコスト増として管理する。Family X/Yは変更しない。**

全編Trial報告の追加原価推計は＋1.8〜3.3円／記事セットだったが、これは今回のFallback仕様を反映した確定値ではない。

Production実装時に、以下を分けて算定すること。

1. 文脈・感情情報生成の追加費用
2. 文脈・感情付きTTSの費用差
3. Retry／Fallbackの発生率と期待費用
4. Local Rewrite・ASR追加費用
5. Family Zの記事セットあたり総量産単価
6. 制作時間への影響

70円／記事セットの目標を継続する。品質を維持できる範囲で、情報生成の再利用・キャッシュ・不要な再生成防止によって原価を最適化する。

**品質 ＞ Delivery ＞ 量産単価。**

費用削減のために承認済み品質を下げないこと。

## 6. 検証・受入条件

少なくとも次の動作を確認する。

| ケース | 期待動作 |
|---|---|
| 1回目PASS | 文脈・感情付き音声を採用 |
| 1回目NG、2回目PASS | 即時Retry後に採用 |
| 1・2回目NG、3回目PASS | 10分クールダウン後、従来方式で採用 |
| 3回ともNG | Local Rewrite／Human Review／STOPへ正しく移行 |
| retry途中で中断・再開 | 回数・方式を維持 |
| X/Yの通常TTS | 一切変更なし |

Mockテストに加え、正式Production runtimeで文脈・感情付き方式が実際に発火した証拠を取得すること。

Fallbackは3回目まで偶発的に失敗するのを待たず、強制NGによるテストで遷移を検証してよい。ただし、Mockだけで通常経路全体をPRODUCTION_WIREDと判定しないこと。

実際の正常経路・Fallback経路を区別して証拠を記録する。

Fableは独立して設計、コード、正式実行経路、回帰テスト、runtime evidenceを照合する。

## 7. SSOT・Git・Closeout

以下を更新する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- 必要な設計・runtime evidence
- Git commit／push

今回の正式採用をFamily Z専用仕様として記録する。

旧方式は3回目のFallbackとして利用できるよう維持し、新方式が後続経路で参照されない等のDangling Referenceを防ぐ。

完了報告では、Family Z Standard／Advancedそれぞれについて、正式初回生成・retry・fallback・resume・QA・実音声・コストを明示すること。

**すべてのGate条件を満たして初めてPRODUCTION_WIREDと判定する。**

未確認事項がある場合は、完了とせず残るOpen Itemと解消条件を報告すること。

## 8. 実行方針・STOP

既存の承認済み作業・日次予算内で、独立作業を並列化して速やかに進める。

不要な追加Trialや磨き込みは行わない。

重大な品質・安全問題、予算超過見込み、承認範囲外の仕様変更が必要な場合はSTOPし、判断事項を整理する。

**今回の最重要目的は、Family Zで文脈・感情付きTTSを標準方式とし、2回失敗した場合だけ、10分クールダウン後の3回目に従来方式へ戻すこと。そして、その動作を正式Productionの全経路で保証することです。**
