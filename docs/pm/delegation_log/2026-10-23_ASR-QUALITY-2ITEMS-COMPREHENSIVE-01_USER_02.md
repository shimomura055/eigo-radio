

<pasted_content id="a638">
# 指示｜ASR品質改善2件のProduction Wiring・Family Z『開いた窓』完成・Perplexity調査

## 1. 目的・承認事項

ユーザーは以下を正式承認済み。

**A. ASR品質改善2件のProduction採用**
- ① 固有名詞の発音救済：Run Entity Table（RET）／OPEN-472
- ② 英米綴りの包括対策：6,361対の対応辞書／OPEN-471
- 対象：Family X/Z共通
- Status：`APPROVED_FOR_PRODUCTION`
- 到達目標：X/Z双方の`PRODUCTION_WIRED`

**B. Family Z『開いた窓』の制作再開**
- Bertie関連の停止音声4件を再生成。
- Advancedの`forte`を原稿本来の`speciality`へ復元し、該当音声を再生成。
- 正式品質検査後、試聴ページを更新。
- 完成版はユーザー最終試聴待ちとする。

**C. Perplexity API認証エラー（401）の調査**
- 調査・原因究明・承認済み仕様内での復旧を許可。
- OPEN-473として管理。

## 2. A：ASR品質改善2件のProduction Wiring

両Trialの成果・Opus指摘事項・Fable評価を引き継ぎ、必要なOpus条件Cレビューを実施する。

承認済み仕様を変更せず、正式Production経路に実装すること。

**必須受入条件**
1. Family X/Z双方の正式初回Production経路で有効。
2. retry／fallback／regeneration／resume／Store再利用／再判定との整合。
3. DEV／Trial専用コードへの暗黙依存がない。
4. 正式runtimeでの発火証拠を取得。
5. 必須Regression／Validator／integration test PASS。
6. 固有名詞の既存受理境界、一般語・数字・否定等の安全条件を維持。
7. 英米綴り対策による既存PASS→NGや意図しない誤PASSを防止。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新、必要なGit commit/push。
9. X/Zそれぞれについて実動作と承認仕様の一致を確認。

Fableは独立して受入評価を実施すること。

**コード配線やTrial成功だけでPRODUCTION_WIREDと判定しない。**

## 3. B：『開いた窓』の完成

AのProduction Wiring完了後、承認済みの修正を正式経路で実施する。

- 停止中の既存音声・成果物を保全。
- Bertie関連4clipを再生成し、新しい発音救済仕様で検証。
- Advancedの`forte`を`speciality`に戻し、原稿・音声の一致を確認。
- 既存の正式品質Gateを通過させ、Standard/Advancedの完成音声を組み立てる。
- 公開試聴ページを更新し、全体再生・個別再生・スクリプトの整合を確認。
- 完成版URLと品質検査結果を報告する。

不要な記事全文再生成や未承認の仕様変更は行わない。

既存の承認済み品質基準を満たした時点で完成とし、追加の磨き込みTrialは行わない。

## 4. C：Perplexity 401エラーの調査・復旧判断

以下4点を調査する。

1. **Production利用実態**：正式量産経路のどの工程・条件でPerplexity APIを使用しているか。実際のruntime証拠も確認。
2. **今回のエラー**：どの処理・対象語・呼び出し経路で401が発生したか。
3. **原因と復旧**：APIキー、設定、認証方法、利用権限等を切り分け、Claude側で解決可能か確認。
4. **代替手段**：Perplexityを利用できない場合、既存の代替経路で承認済みの発音品質と自動処理を維持できるか。

**対応原則**
- 調査・既存仕様内の不具合修正・検証は自律的に実施。
- APIキーなどの秘密情報はログや報告へ出力しない。
- 新規サービス導入や未承認の仕様変更は行わない。
- ユーザー自身の操作が不可欠な場合のみ、理由・必要な操作・放置した場合の影響を具体的に報告。
- 根本原因と影響範囲を明確にし、OPEN-473を適切に更新する。

Perplexity問題はA/Bから独立して進め、品質・安全上の依存関係がない限り、A/Bを停止させない。

## 5. 進行管理・QCD

優先順位は **品質（Q）＞完成速度（D）＞量産単価（C）≫開発費**。

- AとCの独立作業は原則並列実行。
- BはAの必要なProduction配線・検証が完了した段階で着手。
- 既存仕様・過去Trial・Production全体との整合を確認。
- 不具合は承認範囲内で原因究明から再検証まで自律解決。
- 同じ失敗の反復を避け、改善見込みに応じて方法を見直す。
- 開発費は既存承認枠および日次原則1,000円（JST）を遵守。
- 量産単価70円/記事セットを意識し、不要なAPI・再生成・待機を避ける。
- 重大な品質・安全問題、明示STOP、承認範囲超過、新仕様採用が必要な場合は停止・報告。

## 6. 完了報告

Fableの独立評価を含め、以下を簡潔に報告すること。

**A. ASR改善**
- ①②それぞれのX/Z別Production Wiring Status
- 正式runtime evidence、回帰検証結果
- QCD影響、残存リスク

**B. 『開いた窓』**
- 修正音声の検証結果
- Standard/Advanced完成状況
- 最終試聴URL
- ユーザー試聴待ち事項

**C. Perplexity**
- 現行Productionでの利用実態
- 401の原因・発生箇所
- 復旧結果または代替経路の品質評価
- ユーザー対応の必要性

**D. PM Closeout**
- OPEN-471／472／473、UDR #168の処理状況
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映状況
- 未解決事項・ユーザー判断が必要な事項

承認済み事項について再度ユーザー承認を求めず、可能な範囲で完成まで自律的に進めること。

**最終到達目標：ASR改善2件のX/Z PRODUCTION_WIRED、『開いた窓』完成版のユーザー試聴提出、Perplexity問題の原因・影響・対応方針の確定。**
</pasted_content id="a638">
