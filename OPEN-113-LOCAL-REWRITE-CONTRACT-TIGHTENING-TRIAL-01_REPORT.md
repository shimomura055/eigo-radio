# OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01 報告

管理ID: OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01
実施日: 2026-09-04
対象: Local Rewrite Prompt契約の改善のみ(Trial専用、Production未変更)
コード: `er011_open113_local_rewrite_contract_tightening_trial_01.py`
生データ: `er011_output/open113_local_rewrite_contract_tightening_trial_01/`

## 1. 最終Status

**USER_DECISION_REQUIRED**

REJECTEDではない(狙った不具合は解消し、Fact安全性の劣化も確認されなかった)。VALIDATEDと言い切るには、regressionで新たに見つかった「過剰DELETE傾向」というtrade-offがあり、これはSTOP条件11節「ユーザー判断が必要なtrade-off発生」に該当するため、勝手に次工程へは進めない。

## 2. 原因仮説の妥当性

妥当だった。現行Local Rewrite(`er010_ledger_local_rewrite_09.py`)を確認したところ、2点の根本原因を確認した。

1. 契約の自由度: REWRITE_ATTEMPT2_TEMPLATEには「別のLedger Factへ逃げるな」という禁止がなく、Ledger準拠さえ満たせばどんな文でも許容していた。
2. 見落としていたより直接的な原因: **rewrite_ng_itemには、対象文の前後1文(before_ctx/after_ctx)はLedger再検証にしか使われず、書き換えを生成するモデル自身にはPointの他の部分が一切見えていなかった。** 既知ケースでモデルが選んだ代替文は、Verified Fact Ledgerの[F-010]をほぼそのまま言い換えたものであり、Point内に既に[F-010]相当の文("A majority felt a need to reply quickly.")があることを知らずに同じFactを再発見していた。

## 3. 新Local Rewrite契約

`REWRITE_SYSTEM_PROMPT_V2` + `ATTEMPT{1,2,3}_TEMPLATE_V2`(Trial専用、Production未反映)。既存の3段階escalation構造(attempt 1回につきgenerate 1回+check 1回)はそのまま維持し、変更したのは文言のみ。

- 優先順位を明示: (1)unsupportedな意味だけ除去 (2)Ledger範囲内へ縮退 (3)Pointが成立するならDELETE (4)別Factで穴埋め禁止 (5)既出Fact・意味の言い換え再提示禁止 (6)新Fact・因果・solution claim追加禁止
- 対象文の前後1文だけでなく、**その文が属するPoint全体**をcontextとして追加(新しいAPI callは増やさず、既存callへの入力を増やしただけ)
- 出力形式にDELETE_SENTENCEという固定tokenを追加し、削除を正式な選択肢にした

## 4. No.18 B1結果(既知ケース、Point Two)

- 対象: `"Clear response windows could ease it."`(既存文"A majority felt a need to reply quickly."と意味重複していたMAJOR逸脱文)
- 結果: **attempt 1回目でDELETE_SENTENCEを選択、そのままLEDGER_COMPLIANT**
- Point Two: 81語 → **69語**(目標「70語以内」達成)
- 削除後の文末: `"...A majority felt a need to reply quickly. Ignoring an alert may involve pressure, not just attention."` — 前後の接続は自然で違和感なし
- 記事全文でのLedger再判定: `LEDGER_COMPLIANT`(MAJOR 0件)

## 5. 現行Rewriteとの比較

| | A. 元の逸脱Point | B. 現行Local Rewrite | C. 新契約Local Rewrite |
|---|---|---|---|
| 対象文 | "Clear response windows could ease it." | "The survey found that a majority of teens reported feeling a need to respond immediately to texts, social media messages, and other notifications." | (削除) |
| 意味重複 | — | あり("A majority felt a need to reply quickly."と重複) | なし |
| Ledger | MAJOR | COMPLIANT | COMPLIANT |
| Point Two語数 | 75語 | 81語 | 69語 |
| 試行回数 | — | 2回 | 1回 |

## 6. DELETE / REWRITEどちらになったか

既知ケースは **DELETE**。unsupportedな「対策の効果」という主張は、Ledgerのどの範囲にも縮退させられず、かつPointは既存文だけで意味的に成立していたため、契約の優先順位どおりDELETEが選ばれた。

## 7. 重複解消

解消した。新しい代替文自体を生成しないため、既存文との言い換え重複が原理的に発生しない。

## 8. word count

Point Two: 81語 → 69語(目標「70語以内」達成、元の75語より若干短いが許容範囲)。

## 9. Ledger compliance

対象文単位(attempt時点のwindow check)・記事全文再判定のいずれも`LEDGER_COMPLIANT`。

## 10. 新Fact追加有無

なし。削除のみで、新しいFactや因果関係の追加は発生していない。

## 11. API call増減

増減なし。既知ケースはattempt 1回で解決したため、現行(2回)より**むしろ減少**(1 generate call + 1 check call + 記事全文recheck 1回 = 計3 call)。

## 12. Regression

過去の成功Local Rewrite事例3件(4文)を再実行し、**ここで新しい問題を発見した**。

| ケース | 元の逸脱文 | 現行結果(履歴) | 新契約結果 | 評価 |
|---|---|---|---|---|
| No.9 tip_screens A2 #1 | "...also fell, from 66 percent..."(範囲の一般化) | REWRITE(条件を明記) | REWRITE(条件を明記、item単位Ledger compliant) | 問題なし |
| No.9 tip_screens A2 #2 | "...tired of being guided by the screen."(未検証の心理解釈) | REWRITE(softening、重複なし・Ledger準拠) | **DELETE** | **過剰削除** |
| No.18 notifications A2 | "...does not always mean..."(1語のcertainty softening) | REWRITE("always"→"necessarily"のみ) | **DELETE(文末全体を削除)** | **過剰削除** |

4文中3文がDELETEとなり、そのうち2文(No.9 #2、No.18 notifications)は、**そもそも同じPoint内に重複する文が存在せず**、現行契約でも安全なREWRITEが既に成立していたケースだった。それにもかかわらず新契約はDELETEを選んだ。Ledger違反・Fact捏造・重複再発は起きていないが、「元文の役割・情報量をどこまで保存すべきか」で、現行より内容を削る方向に大きく振れている。

なお記事全文でのLedger再判定は、この2件で`LEDGER_DEVIATION`(MAJOR 1件)となったが、**いずれも今回のRewrite対象とは無関係な、別セクションの手つかずの文**("With a screen held by an employee..."/見出し"The habit begins before the first message")が原因だった。念のため、同じ記事の**編集前(元のまま、今回一切手を加えていないテキスト)**に対してもう一度Ledger Deviation Checkerを単独で走らせたところ、こちらは`LEDGER_COMPLIANT`(MAJOR 0件)だった。つまりこのMAJORは新契約のprompt内容が原因ではなく、Ledger Deviation Checker自体が同一記事に対して判定にばらつきを持つ(Production自身の記事全体再判定ステップにも起こり得る)既存の特性であり、Local Rewrite Rewrite対象文とは無関係と判断した。ただしこれはOPEN-113のスコープ外の別課題であり、今回は修正しない。

## 13. Promptだけで十分そうか

部分的に十分。狙った不具合(unrelated fact substitutionによる意味重複)はPrompt変更だけで解消できた。ただし「DELETEを許可する」という設計自体が、意図せず「安全なREWRITEがあってもDELETEを選ぶ」方向へモデルを寄せてしまっており、優先順位の文言だけでは制御しきれていない可能性がある。

## 14. 追加QAが必要そうか

現時点では不要と考える。今回見つかった過剰DELETE傾向は、新しいQA/Validatorを足すのではなく、Prompt内の優先順位(「非重複かつLedger準拠のREWRITEが成立するなら、DELETEより先にそちらを使う」という一文の追加など)の再調整で対応できる可能性が高い。ただしこれは次のTrialで検証すべき話であり、今回のTrial-01のスコープ(禁止事項10節: 新Validator追加禁止)には含めていない。

## 15. リスク

- 過剰DELETEにより、記事の情報量・話の厚みが現行より減る可能性がある(音声化した際の聞き応えに影響しうる)
- Ledger Deviation Checkerの記事全文再判定に、Rewrite対象と無関係な箇所でのばらつきがあることを確認した(OPEN-113範囲外の既存課題として要注意)

## 16. USER_DECISION_REQUIRED

以下のいずれかをユーザーに判断していただく必要がある。

- (a) 今回確認された過剰DELETE傾向を許容範囲と判断し、この契約のまま次段階(優先順位のさらなる調整、または限定的なProduction採用検討)へ進める
- (b) 「同じPoint内で重複せず、かつLedgerに準拠する安全なREWRITEが成立する場合は、DELETEより優先する」という一文をPromptへ追加する追加Trialを依頼する
- (c) 量産前必須修正とはせず、現状のまま`DEFERRED`として保留する

## 17. Production変更なし確認

確認済み。`er010_ledger_local_rewrite_09.py`・`er003_v1_n3_01_articles_generate.py`はいずれも一切編集していない(新規ファイル`er011_open113_local_rewrite_contract_tightening_trial_01.py`の追加のみ)。APPROVED_FOR_PRODUCTION・PRODUCTION_WIREDのいずれも実施していない。

## 18. 次アクション

ユーザーが16節の(a)/(b)/(c)のいずれかを選ぶまで、このTrialはこれ以上進めない。

---

今回Status: **USER_DECISION_REQUIRED**
OPEN-113: Open継続(closeせず、Trial-01の結果のみ`OPEN_ITEMS.md`へ追記済み)
Prompt-only対策: 有効(既知ケースの重複は解消)、ただし過剰DELETE傾向というtrade-off新発生
追加QA: 不要と判断(今回は追加していない)
Production変更: なし
次に進めてよい工程: なし(ユーザー判断待ち)
