# Claude Codeへの指示:Family Z 会話速度改善 — 正式Production Wiring

## 1. ユーザー正式決定

Family Z会話速度A/B Trial(OPEN-462/UDR #159)について、ユーザーが『走れメロス』『開いた窓』のStandard/Advanced全4組を試聴し、**すべてTrial B版の正式採用を決定**しました。

**Status:APPROVED_FOR_PRODUCTION**

Trialの追加や再評価は不要です。正式Productionへの配線から、既存2作品の音声更新、検証、Fable独立受入まで進めてください。

対象は**Family Zのみ**です。

## 2. 正式採用する速度仕様

| 音声区分 | 採用仕様 |
|---|---|
| Standard Narrator | 従来どおり6%減速 |
| Standard Dialogue(登場人物の会話) | **生成後6%減速を撤去** |
| Advanced Narrator | 従来どおり速度変更なし |
| Advanced Dialogue | **生成後に約6%高速化** |

Advancedの高速化はTrial Bで検証済みの、音程を維持する機械処理を使用してください。

以下は変更しません。

- Voice割当
- TTSモデル・Prompt・Style
- 台詞・本文
- 音声の再生順序
- 効果音・BGM
- 承認済みの音声品質基準

## 3. Production Wiring

今回の速度仕様を、Family Zの正式Production経路へ実装してください。

**新規記事の初回制作だけでなく、retry/fallback/regeneration/resume/Store再利用でも同じ速度仕様が適用されることを必須条件とします。**

特に以下を確認してください。

1. StandardのDialogueに旧6%減速処理が残らない。
2. AdvancedのDialogueにTrial Bと同一の高速化処理が適用される。
3. NarratorとDialogueが正しく区別される。
4. 速度処理の二重適用や処理漏れが発生しない。
5. Storeの再利用キー・音声メタデータが新仕様と整合する。
6. 旧仕様の音声が誤って新仕様として再利用されない。
7. TTS再試行上限や既存のASR品質検査を維持する。

旧仕様の不要な分岐・設定・検査があれば、正式経路との整合を確認して適切に整理してください。

実装方法は既存構造を最大限再利用し、不要な新機構を増やさないこと。

## 4. 既存2作品への適用

以下の4組を、承認済みTrial B版の速度へ更新してください。

| 作品 | Standard | Advanced |
|---|---|---|
| 走れメロス | 会話6%減速撤去 | 会話約6%高速化 |
| 開いた窓 | 会話6%減速撤去 | 会話約6%高速化 |

既存のTrial成果物・原音を再利用し、原則としてTTS再生成なしで再組立してください。

『走れメロス』の既存Voice割当は維持します。新しいVoice割当規則に合わせた再生成は不要です。

既存完成音声は、QA合格・公開確認後に安全に差し替えてください。

### 『開いた窓』に関する注意

『開いた窓』では、原作の重要な結末欠落と固有名詞ルールに関する別作業が進行中です。

今回の速度改善では、その本文・台詞を変更しないでください。

ただし、後続の原作忠実性改善で本文・台詞が更新される場合、新速度仕様が確実に適用されるようにしてください。

**速度仕様のProduction Wiring完了と、『開いた窓』作品全体の完成判定を混同しないこと。**

『開いた窓』は引き続き本文品質の問題が未解決であり、作品全体をCLOSEDにしません。

## 5. 検証・受入条件

以下を完了してください。

- Family Z正式初回Production経路への配線確認。
- Standard/Advancedそれぞれの速度処理に関するruntime evidence。
- Trial B版との速度・音声処理の一致確認。
- Voice・本文・台詞・Narrator・BGM等の非対象部分が不変であること。
- retry/fallback/regeneration/resume/Store再利用との整合。
- 速度変更後のASR・音声QA。
- 必須Regression/Validator/Integration test PASS。
- 公開試聴ページの通し再生・個別再生確認。
- Dangling Referenceなし。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新。
- Git commit・push完了。
- Fable独立受入。

**正式Production経路での実動作証拠がない場合、PRODUCTION_WIREDとは判定しないでください。**

追加の有料TTS生成を伴う検証は、既存Trial音声や保存音声で代替できないか先に検討してください。

## 6. QCD・作業進行

優先順位:**品質 > 完了速度 > 量産単価**

- Trialは完了済み。追加の速度探索Trialを行わない。
- 既存音声・Trial B成果物を最大限再利用する。
- 2作品・2レベルの独立作業は並列化する。
- 不要な待機・日付分割をしない。
- 新たなTTS費用・ASR費用は必要最小限に抑える。
- 承認済み範囲内の実装不具合は自律的に原因究明・修正・検証する。
- 未承認の仕様変更や重大な品質リスクが必要になった場合のみSTOPして報告する。

## 7. Status・Closeout

今回の正式採用仕様について、Family Zで以下の状態まで到達してください。

**APPROVED_FOR_PRODUCTION → PRODUCTION_WIRED**

Fableは、コード実装だけでなく正式Production実経路、runtime evidence、試験結果、SSOT・Git反映を照合して受入判断すること。

OPEN-462/UDR #159はユーザー判断済みとして更新し、同じ採用判断を再度求めないでください。

既存2作品の公開音声更新状況も個別に記録してください。

## 8. 最終報告

以下を簡潔に報告してください。

1. **Production Wiring結果・Fable受入Status**
2. Standard/Advancedの新速度仕様とruntime evidence
3. 『走れメロス』『開いた窓』各4組の音声更新結果
4. 更新後の試聴URL
5. QA・回帰テスト結果
6. TTS再生成数・実費・量産単価への影響
7. SSOT/Git反映結果・残Open Item

**ユーザーが4組すべてのTrial B版を正式採用したことは確定済みです。**

新たなユーザー判断を不要に増やさず、承認された仕様を必要十分な品質でProduction Wiredまで完成させてください。
