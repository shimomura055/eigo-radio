[受領日2026-10-22 / 受領者Fable→Sonnet(委任_02 D-1が保存) / 管理ID: FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01(KP英語phrase Primary・Secondary両方PASS必須のX/Z Production採用) / 本文3081文字 / sha256[本文のみ]=55830753ba0c9f19e0f459592be559fbf912614a51e21961638aa9f1911cc2c0 / 出典=委任_02 §1(ユーザー原文逐語)]

# Claude Code指示：ASR PASS条件の正式採用・Family X/Z Production配線

## 1. ユーザー正式決定

以下のASR判定仕様を**Family X/Z共通仕様として正式採用**する。

Status：`APPROVED_FOR_PRODUCTION`

| 対象 | 正式PASS条件 |
|---|---|
| ① Key Phraseの英語フレーズ | **Primary（OpenAI）とSecondary（Azure）の両方PASSが必須** |
| ② Key Phraseの英語解説文 | 現行維持。Primary PASSで合格、Secondary不要 |
| ③ その他すべての音声 | 現行維持。Primary PASSで合格、Secondary不要 |

②③についても、Primary NG時のSecondary判定、承認済み例外、retry／fallback等の既存仕様を維持する。

①は、Primary単独PASSやSecondary単独PASSでは最終合格としない。同音・表記揺れの救済を行う場合も、両Providerそれぞれが承認済み判定基準を満たすこと。

**対象Family：X/Z両方。片方だけの実装完了をもってCloseしない。**

## 2. 実装方針

既存調査 `FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01` を起点とし、既存の共通ASR判定関数および `force_secondary` 等を最大限再利用する。

- Key Phraseの英語フレーズに限り、PrimaryがPASSしてもAzure判定を実行する。
- 両方PASSした場合のみ、そのtakeを採用可能とする。
- どちらかがNGの場合は既存の次slot／再生成処理へ進める。
- 最大試行回数、Human Review Lock、安全STOP条件は承認済み仕様を維持する。
- Azure障害・タイムアウト時にPrimary単独PASSへ自動降格させない。
- Key Phraseの英語解説文、その他の音声には新たなAzure必須条件を適用しない。
- 既存のA2本文minimal fallback等の例外を壊さない。

適用対象の識別は、音声role・正式実行経路に基づいて確実に行うこと。誤って対象を広げたり狭めたりしない。

## 3. 既存実装との整合

並行して進んでいる**多語同音救済**とASR共通判定関数が重なるため、変更競合・仕様矛盾・二重検証を避ける。

可能な範囲でRegressionとruntime evidence取得を統合し、全体のDeliveryと費用を最小化する。

なお、多語同音救済については既存のユーザー承認内容・作業範囲を守り、本指示を理由に仕様を変更しない。

既存のASR重み2.0、Provider routing、数値・否定語の厳格判定、発音救済等も維持する。

## 4. 必須検証

少なくとも次のケースを検証する。

1. Key Phrase：Primary PASS／Secondary PASS → 合格
2. Key Phrase：Primary PASS／Secondary NG → 不合格、次slotへ
3. Key Phrase：Primary NG／Secondary PASS → 不合格、次slotへ
4. Key Phrase：Primary NG／Secondary NG → 不合格、次slotへ
5. Key Phrase：Azure障害・タイムアウト → Primary単独合格にしない
6. Key Phraseの英語解説文：Primary PASS → Azure不要
7. その他の音声：Primary PASS → Azure不要
8. その他の音声：Primary NG → 既存Secondary判定が機能
9. 既存例外、retry／fallback／regeneration／resume、Store再利用時の既存品質保証との整合

**Family X/Zそれぞれで、正式Production初回経路からの実行を確認すること。**

DEV／Trial経路でのPASSやunit testだけでは完了としない。

runtime evidenceには、音声role、両Providerの実際の判定、呼出有無、採否結果、使用model_id／routing、retry／fallbackの動作を残す。

過去の「take part」のように、PrimaryがPASSしてもSecondaryがNGとなるケースが確実に拒否されることを確認する。

## 5. QCD・自律実行

品質（Q）＞速度（D）＞量産単価（C）≫開発費用を厳守する。

- 品質基準を引き下げず、既存機構の再利用と必要最小限の変更で実装する。
- 独立作業は並列化し、不要な日付分割・待機をしない。
- 既存データや保存済み音声を再利用し、API実走は必要十分な範囲に抑える。
- 実測で追加Azure費用、retry・Human Review増分、記事セットあたりの原価影響を評価する。
- 既存承認範囲・日次開発費1,000円（JST）を遵守する。
- 承認範囲内の不具合は原因究明→修正→検証まで自律的に進める。

新仕様の追加、品質基準変更、重要なQCDトレードオフ、予算超過、解決不能なblockerが生じた場合のみSTOPして報告する。

## 6. SSOT・完了条件

- CURRENT_SPECにFamily X/Z共通の新PASS条件を正式記載する。
- 旧文言「同音救済はSecondary側も一致したときのみPASS」と現行仕様との関係を整理し、矛盾を解消する。
- DECISION_LOG／OPEN_ITEMS／PM管理記録を更新する。
- Productionの後続経路に未承認仕様やTrial専用実装へのDangling Referenceがないことを確認する。
- 必須unit／Regression／Validator／integration testをPASSする。
- 必要なcommit・pushを完了する。

**Family XとFamily Zの双方について、正式Production経路で実際に発火した証拠が確認できた場合にのみ `PRODUCTION_WIRED` と判定する。**

## 7. 最終報告

報告は以下に絞る。

1. Family X/ZそれぞれのProduction配線・runtime evidence・最終Status
2. Key Phrase／英語解説文／その他のPASS条件が仕様どおり動いた証拠
3. Primary PASS・Secondary NG時にKey Phraseが確実に拒否された結果
4. retry／fallback／Store再利用への影響
5. 回帰テスト結果
6. 量産追加原価・処理時間・Human Reviewへの影響
7. SSOT・Git反映状況と残存Open Item

**ユーザーは正式採用を承認済み。仕様どおりの実装・検証について追加承認を求めず、Family X/Z両方の `PRODUCTION_WIRED` まで自律的に完了させること。**
