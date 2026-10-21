# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01(記事A) / FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01(記事B)

# Family X 新規2記事・並列Production E2E制作

## 1. ユーザー正式決定

以下の2記事をFamily Xで制作する。

**記事A：給料が上がると、性格も変わる？**

- Source：PsyPost（2026-10-20）
- https://www.psypost.org/a-bigger-paycheck-tends-to-come-with-personality-changes-according-to-a-large-scale-analysis-of-psychology-research/
- テーマ：収入の変化と性格特性の関係

**記事B：漫画のキャラクターとAIで会話。物語の楽しみ方が変わる？**

- Source：ITmedia NEWS（2026-10-20）
- https://www.itmedia.co.jp/news/article/2610/20/2000002432/
- テーマ：LINEマンガのAIチャットサービス「byUs」

**2記事を独立したProduction runとして並列制作する。**

既存の正式Family X仕様を使用し、Research → Fact Ledger → B3 → Writer → Standard／Advanced → TTS → Audio QA → Assembly → 試聴ページ公開まで進める。

## 2. 記事Aの重点品質条件

研究結果を「収入増加が性格変化を引き起こした」と断定しない。

元記事では、収入と性格の関係に双方向の関連が示され、効果も小さいと報告されている。

以下を守る。

- 相関・時間的な先行関係・因果関係を区別する。
- 性格変化の方向や大きさを誇張しない。
- 研究対象・手法・限界を一次研究で確認する。
- 「給料が上がると冷たい人間になる」などの過度な一般化を避ける。
- 研究の意外性を生かしながら、読者自身の仕事や生活と結び付ける。

## 3. 記事Bの重点品質条件

発表内容と、実際に確認できたサービスの動作を区別する。

特に以下を確認する。

- 「byUs」と既存の「キャラチャット」を混同しない。
- 2026年10月19日の発表内容と提供状況。
- Official Storyとファンストーリーの違い。
- 原作者が承認した作品を対象とするという条件。
- サービス提供者が公表した利用実績と、独立に確認された事実の区別。

単なるAI機能紹介で終わらせず、**「物語を読む人が、その物語に参加する人になる」**という変化を中心的なAngle候補として検討する。

ただし、このAngleを採用するために、実際には提供されていない機能や利用者の反応を創作しない。

## 4. Writer・Entertainment品質

両記事ともCURRENT_SPECの正式Production Writer仕様を維持する。

- 既存のResearch／Fact Ledger／B3構造を使用する。
- Ledger外の事実・因果関係を創作しない。
- 重要なFactの帰属を保つ。
- エンターテインメント性は高めるが、事実性を犠牲にしない。
- 不自然な比喩、冗長な説明、同内容の反復を避ける。

**直近のDetective改善TrialのPattern A／B／CはすべてProduction不採用。今回のWriterには適用しない。**

## 5. 並列化・QCD

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 2記事のResearch・原稿生成・音声生成を、依存関係と安全条件が許す範囲で並列実行する。
- 同じProduction共有資源を使用する場合は、競合やRUN_LOCKを尊重する。
- 一方の記事の軽微な不具合で、独立したもう一方の進行を止めない。
- 承認済みの品質Gate・retry／fallback／regeneration／resumeを維持する。
- 不要なTrial、Prompt探索、モデル変更、追加機構の開発を行わない。
- 量産単価70円／記事セットを目標とし、記事別に費用を計測する。
- 日次開発予算1,000円（JST）と既存の個別承認枠を遵守する。2記事合計の費用見積を事前確認し、承認枠超過見込み時は超過前にSTOPする。

既存の承認済み仕様内で解決できる不具合は、自律的に原因究明・修正・検証する。

## 6. 完成条件

記事A／Bそれぞれについて以下を満たす。

1. 原典・一次情報と重要Factの確認。
2. Fact Ledger／B3／Writerの整合。
3. Standard／Advancedの原稿完成。
4. 現行Production TTS・Audio QA・Style Gate・必須Validator PASS。
5. Standardの承認済み6%減速の確認。
6. 完成音声・全文スクリプト・Key Phrasesを掲載した試聴ページ公開。
7. 正式runtime evidence、SSOT／Git反映。
8. Fable独立受入判定。

**Production技術完成とユーザー試聴PASSは区別する。**

両記事の完成後は `USER_LISTENING_PENDING` とし、ユーザーの試聴結果を待つ。

## 7. 報告形式

2記事を横並びで、以下を簡潔に報告する。

| 報告項目 | 記事A：収入と性格 | 記事B：漫画AI |
|---|---|---|
| 完成状態 | | |
| 試聴URL | | |
| 重点Fact品質 | | |
| Standard／Advanced音声QA | | |
| 実費・量産単価 | | |
| 所要時間 | | |
| Fable受入判定 | | |
| 未解決事項 | | |

ユーザー判断が必要な重大な問題が生じた場合のみ、該当記事・理由・推奨対応を明示する。

**目的は、既存の承認済みFamily X Production経路を再利用して、2記事を高品質・最短・低原価で完成させること。**
