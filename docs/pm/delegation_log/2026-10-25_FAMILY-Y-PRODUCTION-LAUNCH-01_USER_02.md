<pasted_content id="a638">
# Claude Codeへの追加指示
## Family Y Production正式立ち上げ｜追加仕様決定・実装継続

**対象：FAMILY-Y-PRODUCTION-LAUNCH-01**  
**現状：Phase 0完了、Opus設計レビュー中**  
**目標：Family Y PRODUCTION_WIRED**

### 1. 今回のユーザー決定

Phase 0報告の判断事項について、以下を正式決定する。

#### ① Family Y Chunk分割

**Family X方式（段落分割＋0.2秒ポーズ）をFamily Yに正式採用する。**

- Status：APPROVED_FOR_PRODUCTION
- Family Yの正式Production経路に組み込む。
- 既存のX方式を最大限再利用する。
- Yの5パート構成・3 Voice・話者切替との整合を確保する。
- セリフや話者の切替を不自然に結合・分割しない。
- 事前の追加Trial・ユーザー試聴承認は不要。
- 正式Production実走時に音声品質・分割位置・ポーズを検証する。

今回の承認はX方式のY適用であり、ZのB_r1方式は採用しない。

#### ② Closing Prompt／Gate

**現行Prompt 02・既存Gateを変更せずにProduction立ち上げを進める。**

- Prompt 02＋GPT-6.1 Sol（high）を維持する。
- 既存の承認済みGate品質基準を維持する。
- 既存の局所修正・再判定機構を利用する。
- Gate FAILが解消しない場合は公開しない。
- PromptとGateの不整合は既存OPEN_ITEMSで継続管理する。
- Prompt 03への変更やGate条件の緩和は行わない。

将来の改善案は、実績を踏まえて必要十分な形で整理する。

#### ③ Family Y Voice生成方式

**既存Family Y設計に基づく3 Voice生成方式を正式Production採用する。**

- Status：APPROVED_FOR_PRODUCTION
- 実在する意見を素材にする。
- 明確な人物像を持つ3人のVoiceを生成する。
- 各Voiceは一人称で主観的に語る。
- 3人の立場・価値観・経験の違いを明確にする。
- 既存の5パート構成を維持する。
- 新たな意見収集の自動化は今回のScope外とする。

過去のTrialでVALIDATED（限定）だった方式について、今回ユーザーが明示的に正式採用したものとして扱う。

ただし、公開前の出典・利用許諾に関する既存課題は継続管理し、必要な公開条件を省略しない。

### 2. 既存のClosing採用判断も維持

以下は変更しない。

**今後のFamily Y記事**
- Closing一般化Prompt 02
- GPT-6.1 Sol
- reasoning effort：high

**『宅配の再配達は有料にすべきか？』**
- 人手設計案B「料金は何を動かせるか」を個別採用
- 当該記事のみの例外
- 今後の一般記事へ案B固定方式を拡張しない

### 3. XYZ共通仕様の継承・配線漏れ防止【最重要】

Phase 0で作成した55項目の仕様差分台帳を正本として更新し、今回の3項目を反映する。

特に以下を徹底する。

**A. 承認済み仕様**

Family Yへの適用が必要なものは、今回のProduction立ち上げで組み込む。

Key Phrase・文法Human Review、英語解説、Part 1／Part 2、ASR・TTS共通品質対策等を確認する。

他案件で現在実装・検証中のものは、正式な接続仕様が確定した時点でYへ接続する。

**B. 現在進行中・未承認仕様**

未承認のTrial結果をProductionへ先行採用しない。

ただし、将来正式採用された際にFamily Yへの配線が漏れないよう、仕様ごとに以下を追跡する。

- 現在のStatus
- 適用対象Family
- Family Yへの適用要否
- 配線状況
- 残作業
- 完了条件
- OPEN_ITEMSの追跡先

**「Family Y立ち上げ時に未完成だったため、後日正式採用されてもYには未反映」という状態を防止すること。**

既存PM Closeout Mandatory Checkに、共通仕様のX/Y/Z配線状況を確認する項目を必要十分な形で追加する。

この追加は、今回承認済みのFamily間仕様乖離防止方針の実装として扱う。

### 4. Opusレビューと実装の進め方

現在進行中のOpus設計レビュー結果を反映する。

- 既存Phase 0調査を不要にやり直さない。
- 承認済み範囲内の修正は自律的に実施する。
- 仕様変更が必要な指摘はユーザー判断へ回す。
- 独立した作業は並列化する。
- 品質・安全・承認上の理由がない限り、日付を分けず最速で進める。
- Family Y固有仕様と共通仕様の整合を守る。

Family Xのコードを機械的にコピーせず、Family Yの構成に適した形で再利用する。

### 5. 費用・予算

Phase 0の概算を現時点の予算計画として維持する。

| 項目 | 見積 |
|---|---:|
| 『宅配』正式完成 | 27〜35円 |
| 通常Y記事 | 69〜93円 |
| 立ち上げ検証総額 | 73〜113円 |
| 案件費用枠の提案 | 150円 |

今回のChunk分割採用によって費用見積や必要な検証範囲が変わる場合は、合理的な精度で再計算する。

**150円は提案された案件枠であり、この指示によって新規承認された予算ではない。**

既存の承認済み予算・日次上限内の作業は継続する。

有料実走前に予算充足を確認し、不足する場合は、必要な追加額と用途をユーザーへ提示する。

費用のかからない調査・設計・実装・テストは不要に停止しない。

量産単価70円／記事セットを継続目標とし、通常Y記事の見積が目標を超える点は改善課題として残す。ただし、品質を下げて目標に合わせない。

### 6. Production Wiring受入条件

正式初回Production経路について、少なくとも以下を確認する。

1. Family Yの5パート・3 Voice構造が正しく動作する。
2. 実在意見を素材とした承認済みVoice生成方式が使われる。
3. 通常Y記事でPrompt 02＋GPT-6.1 Sol highが発火する。
4. 『宅配』のみ案B Closingが使用される。
5. X方式Chunk分割＋0.2秒ポーズがYで機能する。
6. Key Phrase・文法Human Reviewあり／なしが機能する。
7. 承認済みXYZ共通仕様が適用される。
8. retry／fallback／regeneration／resumeで仕様が維持される。
9. 品質Gate・必須Regression・integration testがPASSする。
10. 正式runtime evidenceに実際のmodel_id、routing、Prompt／Style等が記録される。
11. CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・仕様差分台帳が更新される。
12. 必要なGit commit／pushが完了する。
13. Fableが独立受入評価を実施する。

**DEV／Trial経路の動作、コード実装のみ、単体テストのみではPRODUCTION_WIREDとしない。**

ユーザーによる完成記事の最終試聴PASSは、Production Wiringとは別管理とする。

### 7. STOP条件

既存仕様・承認Scope・予算内の問題は、自律的に原因究明・修正・検証する。

以下の場合のみ、該当作業をSTOPしてユーザー判断を求める。

- 承認済み仕様・品質基準の変更が必要
- Family Y固有仕様と共通仕様が重大に衝突する
- 適用可否が判断できない重要仕様がある
- Closing Prompt／Gateの意味的変更が必要
- 承認予算の超過
- 公開条件・権利関係の未解決によって公開できない
- 重大な品質・安全問題
- 正式Production経路の構築を妨げるblocker

独立して進められる作業は継続する。

### 8. 報告

まず、Opusレビュー結果と今回の追加決定を反映し、更新した実装計画・費用見積・未解決事項を簡潔に報告する。

その後、承認済み範囲内でProduction実装・検証を進める。

最終報告では以下を明示する。

- Family Y ProductionのStatus
- 今回承認した3項目の配線・検証結果
- Closing Prompt 02と案Bの使い分け
- XYZ共通仕様の適用状況
- 将来適用待ち仕様の追跡状況
- 正式runtime evidence
- 品質検査結果
- 実費・量産単価見込み
- Fable独立受入評価
- SSOT・Git反映
- 残Open Item
- ユーザー試聴用の完成記事URL

**最終目標は、Family Yを承認済み共通仕様に整合した正式Productionとして完成させ、今後の仕様変更でもFamily Yが取り残されない状態を実現すること。**

品質を守りながら、不要な待機や逐次処理を避け、最速でPRODUCTION_WIREDまで進めてください。
</pasted_content id="a638">
