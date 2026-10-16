# ユーザー指示原文(2026-10-16受領、Fable転記)
# Claude Code／Fableへの指示
## Coffee正式E2E実走・原価実測・DQI効果観察

**管理ID：FAMILY-X-COFFEE-E2E-COST-AND-DQI-FOLLOWUP-01**

### 1. 現在の状態・目的

- AUW：`PRODUCTION_WIRED`。ユーザー正式承認済み。
- DQIパッケージP：PM運用へのProduction実装完了。効果評価は未完了。
- Family X：承認済み最新仕様のProduction配線・テスト完了。Coffee正式実走によるruntime evidence待ち。
- Coffee E2E：**最大205円までユーザー承認済み**。
- Family X・Zが現在の開発対象。Family Yは将来対象。
- Family A・B・Cは開発停止。

今回の目的は、新しい仕様を探索することではなく、**既に承認・実装された仕組みを正式経路で動かし、品質と原価を実測すること**。

### 2. Coffee全面新規制作

既存管理ID：

`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`

既存の`SPEC_WIRING_MATRIX_01.md`および`COFFEE_E2E_PLAN_01.md`に従う。

- Coffeeはテーマだけを維持。
- Research、Fact Ledger、B3、Writer R0→R1→R2、英語化、Standard調整、KP、TTS、Assemblyを新規実行する。
- Standard／Advancedの試聴ページを完成させる。
- 工程ごとに正式仕様反映マトリクスと照合する。
- 必須Human Review／品質Gateを迂回しない。
- B3／R0／R1／R2のactual model_idと実送信Prompt SHAを記録する。
- retry／fallback／regenerationにおける承認済み仕様との整合を確認する。
- AUWは既存Production配線を利用し、再実装しない。

**Coffeeが完成しただけでFamily Xを`PRODUCTION_WIRED`としない。** 正式初回経路・後続経路・runtime evidence・test・SSOT・Git反映まで確認して判定する。

### 3. 費用管理・量産原価

**今回のユーザー承認上限：205円。**

この金額はCoffee E2Eに限定し、追加Trialや他案件へ流用しない。

費用について、以下を必ず計測する。

1. Research
2. Verified Fact Ledger
3. B3
4. Writer R0／R1／R2
5. Advanced英語化・Standard調整
6. KP生成・選定・解説
7. TTS・ASR
8. retry／fallback等の追加費用
9. 記事セット全体の実費

併せて、正式リリース後のBatch TTS適用を想定した**量産1記事セット（Standard＋Advanced）の原価**を算出する。

既存目標は**70円／記事セット**。

報告では以下を区別する。

- 今回の実測開発・検証費
- 通常の新規Production生成で反復する費用
- 今回だけの検証・異常対応費
- Batch適用による推定削減額
- 量産想定原価と70円目標との差額

Batch単価は正式な既存価格記録に基づいて計算し、未測定部分を実測値として扱わない。

70円超過の場合は、主因と改善余地を説明する。ただし、**今回は原価削減の追加Trial・モデル変更・品質仕様変更を行わない。**

日次開発費の原則1,000円／日（JST）も継続適用する。

205円を超える見込みが生じた場合は既存費用Gateに従いSTOPする。上限を超えないよう品質Gateを省略してはならない。

### 4. K2代替音声：Open Item登録のみ

K2はFamily XのStandard／AdvancedのKey Phrase英語フレーズ用正式TTS Style。

現行実装ではK2が不合格の場合、別Styleによる代替音声が使用される可能性がある。

今回のユーザー判断：

**この問題はCoffee制作から切り分け、Open Itemとして管理する。**

実施事項：

- 既存Open Itemとの重複を確認し、重複させず登録・更新する。
- K2代替音声の利用時、内部警告だけではユーザー報告が保証されない点を記録する。
- Coffee実走では代替音声の有無、件数、対象フレーズを記録する。
- 代替使用があれば完成報告に明示し、正式K2との不一致として扱う。

**今回、K2 fallbackの改修や追加Trialは行わない。**

Open Itemを登録したことだけを理由にCoffee制作を止めない。ただし、既存の必須品質Gateや受入条件を緩和しない。

### 5. DQI：今後10件の前向き効果観察

DQIパッケージPは既にPM運用へ実装済みである。

実装のやり直しは不要。

**今後の実際の受入案件10件について、DQIの効果を測定する。**

評価指標：

| 指標 | 目標 |
|---|---|
| 重大NGの被覆漏れ | 0件 |
| 承認済み事項の再質問 | 0件 |
| 機械Validatorの誤警告率 | 10%以下 |

各案件で以下を記録する。

- P1：受入判定と重大NGの整合
- P2：ユーザー判断前の4区分仕分け
- P3：不要なユーザー判断の提示抑制
- P4：機械Validatorの所見と妥当性

**10件分を集計し、まとめてPM向けに報告する。**

ユーザーの主観評価だけに依存せず、判定記録とValidator結果を用いて評価する。

一方、通常運用の観察では未知の重大NGを確実に発見できるとは限らないため、測定できなかった項目は「未検証」と明示する。

追加の有料盲検Trialは実施しない。

既知正解による机上評価と、今後の未知ケース観察を混同しない。

観察のためだけに不要な受入案件や追加タスクを作成しない。通常業務の進行に合わせて測定する。

### 6. Day 5・6

**PM自律運営モデルのDay 5・6は保留を維持する。**

DQIの10件観察をDay 5・6の代わりに完了扱いしない。

Day 5・6の詳細な実施項目を推測で補完したり、今回勝手に開始したりしない。

### 7. 作業範囲と禁止事項

実施対象：

- Family X Coffee正式E2E
- 工程別費用実測と量産想定原価計算
- K2代替音声Open Item登録
- DQI実運用10件の観察

禁止事項：

- Family A／B／Cの調査・Trial・改修
- Family Zの予防的追加改修
- Family Yの先行開発
- 新規の音声Style探索
- コスト削減を目的とした追加Trial
- 依頼されていないOpen Itemの全件棚卸し
- 不要なユーザー判断の発行
- Day 5・6の無断再開

新しい問題を発見しても、今回の依頼を逸脱して独立開発を始めない。

### 8. PM Gate・STOP条件

次の場合はSTOPし、事実・影響・必要な判断だけを報告する。

- Coffee費用205円の超過見込み
- Mandatory Human Review／品質Gate到達
- 承認済み仕様との重大な不一致
- 正式Production経路を使えない
- 新たな仕様採用・追加Trialが不可欠
- 既存の安全・品質・費用STOP条件に抵触

ただし、ユーザーが明示的に後回しにした非Blocking Open Itemを理由に、勝手に作業を止めない。

### 9. 報告事項

Coffee実走後、以下を報告する。

1. Standard／Advanced試聴ページ
2. 全工程の仕様照合結果
3. B3→R2のactual model_id・Prompt SHA
4. K2代替音声の有無と件数
5. 工程別の実測費用
6. Batch適用時の量産想定原価・70円目標との差
7. Production Wiring受入条件の達成状況
8. 未解決のBlocking事項のみ

DQIについては、**通常の受入10件が蓄積した時点で効果評価をまとめて報告**する。

FableはClaude Codeの完了報告をそのまま採用せず、CURRENT_SPEC・承認済み仕様・runtime evidence・テスト結果・QCDと照合して受入判定すること。

**ユーザーに不要な判断を求めないこと自体が、今回のDQIの重要な評価対象である。**
