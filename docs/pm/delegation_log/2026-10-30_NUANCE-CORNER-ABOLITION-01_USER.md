# ユーザー指示原文(逐語、2026-10-30受領。①ニュアンス解説廃止・v3 REJECTED、②One Step Further最優先、③Family Y姓記事 完成保留)
<<<USER>>>
# Claude Codeへの追加指示｜One Step Further最優先・ニュアンス解説廃止・Family Y「姓」記事完成保留

## 1. ユーザー決定事項

以下の3点を正式に伝えます。

### ① 現行「ニュアンス解説」コーナーを廃止する

ユーザーは、現行ニュアンス解説について、説明のわかりにくさと学習価値の不足を理由に、**コーナーの廃止を決定しました。**

- 現行のニュアンス解説は今後の学習コンテンツから廃止する。
- 改善Prompt v3も正式採用しない（REJECTED）。
- 既存Production・Human Review・公開ページ・生成工程などへの影響を調査し、必要な撤去と整合確認を行う。
- 不要となる生成・品質検査・表示処理は整理し、量産費用・処理時間の削減につなげる。
- ニュアンス解説以外の承認済み仕様は維持する。

廃止に伴うProduction変更は、既存仕様との整合・回帰テスト・runtime evidence・SSOT/Git反映まで実施し、対象Family・全レベルでPRODUCTION_WIREDまで確認すること。

過去の完成記事の本文・音声は変更しない。過去の公開済み記事に遡って表示を撤去するかは、既存公開物の変更範囲を確認し、未承認の一括変更を行わないこと。

### ② One Step Furtherを最優先で進める

先に指示した新学習コーナー **「One Step Further｜もう一歩進んだ英語表現」** のTrialを、現在の最優先タスクとする。

目的は、日本人学習者が、

「聞いたことはあるが、自分では使えない」
「こんな英語表現があるのか。覚えて使ってみたい」

と感じる、実用的な英語表現を紹介すること。

先行指示の内容を維持する。

- 対象：Family Y「姓」記事＋Family X/Z各1記事
- Standard／Advancedの全6ケース
- 各ケース1〜2表現
- 本文の話題に関連する、実用的で自然な発展表現
- 基本表現／発展表現／日本語訳／簡潔な学習ポイントを提示
- 既存Key Phrase・文法解説との重複を回避
- 学習価値・自然さ・正確性・再現性・QCDを検証
- ユーザーが比較できるTrialページを作成

品質上の問題は承認済みTrial範囲・予算内で自律的に改善する。

**One Step FurtherはまだTrialであり、Production正式採用は未決定。**

Trial成功を理由にProductionへ無断配線しないこと。

Trial CloseoutはVALIDATED／REJECTED／USER_DECISION_REQUIREDとし、正式採否をユーザーに提示する。

### ③ Family Y「姓」記事はOne Step Furtherの完成を待つ

対象記事：

**「結婚するとき、男性が妻の姓を選ぶのはあり？」**

この記事については、One Step FurtherのTrial結果と今後の正式採用判断が確定するまで、**記事の最終完成承認を保留**します。

- 記事本文・音声など、既に完成・検証済みの成果は維持する。
- One Step Furtherを正式採用する場合は、採用仕様に従って本記事へ反映する。
- 不採用の場合は、One Step Furtherなしで最終完成候補を整理する。
- いずれの場合も、ユーザーの最終確認・承認なしに記事完成扱いにしない。

## 2. 作業優先順位

**最優先：One Step Further Trialの完成・ユーザーへの結果提示**

ニュアンス解説の廃止対応についても、独立して進められる調査・撤去・検証は並列化し、One Step FurtherのTrial完了を遅らせないこと。

Family Y「姓」記事は、追加の不要な本文・音声再生成を行わず、One Step Furtherの正式採否決定を待つ。

他の承認済みタスクについても、不要な全面停止はせず、競合や優先順位を管理する。

## 3. PM Gate・Closeout

以下を明確に区別すること。

| 項目 | Status |
|---|---|
| 現行ニュアンス解説 | 廃止決定・Production撤去待ち |
| ニュアンス改善Prompt v3 | REJECTED |
| One Step Further | Trial進行中・正式採否未決定 |
| Family Y「姓」記事 | 最終完成承認保留 |

現行ニュアンス解説の撤去と、One Step Furtherの追加は別の仕様変更として管理する。

特に、ニュアンス解説の撤去を理由に、未承認のOne Step FurtherをProductionへ配線しないこと。

廃止対応のProduction Wiring完了には、対象Family・レベルの正式初回経路、retry／fallback／regeneration／resume、品質検査、公開ページ、runtime evidence、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS、Git反映を確認すること。

重大な品質問題・承認範囲外の変更・予算超過はSTOPして報告する。

## 4. 最終報告

まずはOne Step FurtherのTrial結果を優先して提出してください。

その際、以下を明確に示すこと。

1. 3記事・全6ケースの比較ページURL
2. 学習価値と再現性の評価
3. QCDへの影響
4. Fable独立評価とTrial Closeout Status
5. ユーザーの正式採否判断に必要な事項

ニュアンス解説の廃止・Production撤去については、完了後に別途報告すること。

**最重要：One Step Furtherの品質検証を最優先で完成させ、Family Y「姓」記事の最終承認へつなげること。**
<<<END>>>
