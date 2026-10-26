# TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 ユーザー指示原文(逐語、2026-10-26)

# 【調査指示】Family XYZ共通｜TTS Retry・Fallback・Local Rewrite・Human Review仕様の全体棚卸し

**管理対象：Family X／Y／Z、Standard／Advanced**
**Scope：調査・比較・問題整理のみ。Production変更・新規Trial・有料API実行なし。**

## 1. 目的

Family Zの文脈・感情付きTTS Production Wiring報告で、3回NG後にLocal Rewriteを行わずHuman Review／STOPへ進むことが判明した。

一方、Family X等にはLocal Rewriteが存在しており、Family・音声部位によって処理が異なる。

今回、XYZ全体について以下を整理する。

1. どの音声部位にLocal Rewriteが適用されているか。
2. Rewriteがある場合、**何を契機に、どの条件で発動するのか**。
3. Rewriteがない場合、**なぜないのか。承認済みの意図的な差異なのか、未実装なのか**。
4. TTS Retry・Fallbackの仕様と、その発動順序・条件。
5. 最終的にHuman Review／STOPへ進む条件。
6. 承認済み仕様と正式Production実装の一致・不一致。

**推測による理由付けは禁止。根拠が見つからない場合は「理由不明・記録なし」と明記する。**

## 2. 対象範囲

Family X／Y／Zの正式Productionで音声化されるすべての部位を対象とする。

例：

- Family X：本文、Comment、In One Line、Key Phrase等
- Family Y：Lead、Voice 1〜3、Tension＋Closing、Key Phrase等
- Family Z：地の文、登場人物のセリフ、Key Phrase等

上記は例示であり、実際のProduction音声構成を確認して完全な一覧を作成すること。

Standard／Advancedで処理が異なる場合は分けて記載する。

特に、本文、セリフ、Key Phrase、短い定型音声等で共通生成関数が異なる場合、その差異を省略しない。

## 3. 星取表①：Family別・音声部位別の全体比較

以下の形式で一覧化する。

| Family | レベル | 音声部位 | 通常TTS上限 | Retry条件 | Fallback有無・種類 | Rewrite有無 | Rewrite発動条件 | 最終NG時 | 仕様・実装一致 |
|---|---|---|---|---|---|---|---|---|---|
| X | Std/Adv | 本文 | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |
| Y | Std/Adv | Voice | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |
| Z | Std/Adv | セリフ | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |

この表を全音声部位について埋めること。

**必ず確認する事項**

- TTS試行上限と、技術エラーによる再試行の扱い
- ASR NG、発音NG、内容不一致、無音・異常音声など、Retryを発動する具体的条件
- Primary／Secondary ASRの判定との関係
- 同じStyleで再試行するのか、Style・モデル・音声設定が切り替わるのか
- Fallbackが何回目に、どの条件で発動するのか
- Fallback後もNGの場合に何が起こるか
- Local Rewriteの発動条件
- Rewrite後の再TTS回数と検査内容
- Human Review／STOPへ進む条件
- Human Review Lock・retry・regeneration・resume時の扱い

「3回NG」と表現する場合も、通常TTSの3回なのか、Fallbackを含む3回なのか、Rewrite後の試行を含むのかを区別すること。

**Fallbackは単なる有無ではなく、何から何へ切り替える方式なのかを明記する。**

## 4. 星取表②：Local Rewriteの適用有無と理由

特にRewriteがない部位を重点的に調査する。

| Family | 音声部位 | Rewrite | 不適用・例外の理由 | ユーザー承認の有無 | 根拠資料 | 分類 |
|---|---|---|---|---|---|---|
| X | 部位名 | ○/× | 記録に基づく理由 | 有/無/不明 | 文書・該当箇所 | A/B/C |
| Y | 部位名 | ○/× | 同上 | 同上 | 同上 | 同上 |
| Z | 部位名 | ○/× | 同上 | 同上 | 同上 | 同上 |

理由は次のように区別する。

- ユーザーが明示的にRewriteを不採用とした。
- 品質保護などの理由で、承認済み仕様として対象外にしている。
- 実装当時の技術的制約から未対応となっている。
- 共通仕様の適用漏れ・Production配線漏れ。
- 設計・承認記録に理由が存在しない。

「セリフだから書き換えられない」「原作保護のため」といった説明は、**実際の設計・承認根拠が存在する場合だけ、既存の決定理由として記載すること**。

Claude/Fableの新たな解釈や技術的見解は、事実・承認済み仕様とは別欄に区別する。

## 5. 発動フローの明示

Family・音声部位ごとに、以下のような形式で実際の処理順序を示す。

**記載例（正式仕様を意味しない）**

通常TTS①
→ NGなら通常TTS②
→ NGならFallback TTS③
→ NGならLocal Rewrite
→ 書換え後TTS＋ASR
→ NGならHuman Review／STOP

実際には各Family・部位について、現行の正確なフローを記載すること。

共通するフローはまとめてよいが、差異がある箇所を省略しない。

また、同じ「Fallback」という名称でも、Style変更、モデル変更、技術エラー救済など目的や動作が異なる場合は区別する。

## 6. 承認済み仕様・過去経緯との照合

以下を確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- 過去のユーザー承認・不採用記録
- 過去のLocal Rewrite関連Trial・設計・Opus/Fableレビュー
- 正式Productionコード
- retry／fallback／regeneration／resume経路
- Production runtime evidence
- Git変更履歴

特に、2026-10-19のLocal Rewrite発動条件に関するユーザー決定、および今回のFamily Z文脈・感情付きTTSの正式採用内容と照合すること。

「共通仕様」と「Family・部位固有仕様」を分類し、後から追加した仕様によって古いルールが残存・矛盾していないかも確認する。

コードの存在だけでPRODUCTION_WIREDと判断しない。正式経路の到達性と既存runtime evidenceを確認し、実走証拠のないものは未検証と明記する。

## 7. 差異・問題の分類

発見した違いを次の3種類に分類する。

**A：承認済みの合理的な差異**

- ユーザー承認または正式仕様の根拠あり
- 実装が仕様と一致
- 原則として現状維持

**B：承認済み仕様との不一致**

- 配線漏れ、不具合、古いルールの残存等
- 修正の必要性と影響範囲を明示
- 今回は修正せず、原因と解決方針を報告

**C：未承認・根拠不明の差異**

- 実装上は異なるが、承認された理由が見つからない
- 意図的な例外かどうか判断できない
- 必要なユーザー判断事項を整理

問題の重要度・品質リスク・量産コスト・Deliveryへの影響も併記すること。

## 8. 調査・報告の進め方

- 追加の有料Trialや音声生成は実施しない。
- 既存コード・SSOT・Git・runtime evidenceを使ったread-only調査とする。
- 独立したFamily別調査は原則並列化する。
- 情報不足による曖昧さは残さず、確認できるところまで自主的に掘り下げる。
- ただし、新仕様の無断採用やProduction修正は行わない。
- OPEN_ITEMSへの反映が必要な未解決事項は提案し、既存記録との重複を確認する。

## 9. 最終報告の構成

以下の順番で報告すること。

1. **結論：XYZのRewrite／Fallback仕様は整合しているか**
2. 全Family・全音声部位の星取表①
3. Rewrite不適用理由と承認根拠の星取表②
4. Family・部位別の実際の処理フロー
5. 発見した仕様不一致・未配線・理由不明箇所
6. QCD影響と優先順位
7. Fable独立評価
8. 必要なユーザー判断事項（本当に判断が必要なものだけ）

**本調査の完成条件は、ユーザーが星取表を見れば、XYZそれぞれの音声部位について「何回失敗すると、何が起こり、なぜそうなっているのか」を理解できる状態にすること。**

単にRewriteの○×を列挙するだけで終了しないこと。

なお、今回の調査結果を踏まえた仕様統一やProduction改修は、別途ユーザー判断を経て実施する。

(原文ここまで)
