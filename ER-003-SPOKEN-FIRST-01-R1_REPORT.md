# ER-003-SPOKEN-FIRST-01-R1 実行報告(ADD03 Listening-first 長文化是正)

**管理ID: ER-003-SPOKEN-FIRST-01-R1**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(ADD03限定の実験系。Production仕様は変更していない。A01/A02への展開はユーザー判断待ち)**

## A. Executive Summary

**長文化は是正できた。** Version L(472語、Version Vより+13%)から
Version L2(355語)へ圧縮し、Version Vの418語を**下回った**。

- Fact Checker: **`PASS`**(矛盾・未確認主張ともに0件)
- Ledger Deviation Check: **`LEDGER_COMPLIANT`**(逸脱0件)
- word count: V=418語 → L=472語(+13.0%) → **L2=355語(V比−15.1%、L比−24.8%)**

ただし、L2はご指示のsoft target(375〜418語)の**下限をやや下回った**
(355語)。これは「数値合わせのために不自然な英文へ削ることは禁止」と
いうご指示を優先した結果であり、不自然な圧縮や意味の欠落は確認されて
いない(D・G節)。この点は成功条件10「375〜418語に収まることが望ましい」
を完全には満たしていないため、正直に報告する。

## B. Version L2全文

```
"Twenty Percent—Then Never Mind": Hormuz Fee Reversal Fails to Calm Oil

For just over a day, one number hung over the Strait of Hormuz: 20 percent.

On July 13, President Donald Trump said the United States would seek
reimbursement of 20 percent on "all cargo" moving through the strait,
as payment for providing safety and security. He said work on the
procedures would begin immediately.

The announcement sounded forceful, but the mechanism was almost
entirely blank. How the reimbursement would be calculated, collected,
or enforced remained unexplained—including what the 20 percent would
apply to. This was a proposal, not an implemented toll.

Still, the number was large enough to make markets imagine the bill.

One scenario assumed a tanker carrying about two million barrels, with
oil at about 85 dollars a barrel. If 20 percent were applied to the
cargo's value, the estimated charge would be about 34 million dollars
for one tanker. That was hypothetical, not an actual charge.

On July 13, Brent settled at about 83 dollars a barrel, up nearly 10
percent. Reuters linked the jump to a planned U.S. maritime blockade
of Iran and concerns over energy shipments through Hormuz—not to the
proposed fee alone.

Then came the reversal.

On July 14, Trump said the 20-percent plan would be replaced by Gulf
trade and investment deals with the United States. Later, he told
reporters that nobody should charge ships for passage through Hormuz
and that he disliked fees, while maintaining that America's protective
burden was unfair.

Oil briefly eased after the announcement, but the relief did not last.

Brent soon returned close to its earlier elevated level. It settled at
about 85 dollars a barrel, finishing higher as blockade, attacks, and
tanker-safety concerns persisted.

## What Matters Beyond the Headline

### A Dramatic Percentage Was Never a Complete Policy

The 20-percent figure dominated attention, but a rate was not a
policy. Without a defined calculation or collection framework, any
precise cost estimate remained hypothetical. The proposal sounded
immediate, yet it never became an implemented toll.

### The Market Was Pricing a Wider Danger

Removing the proposed fee did not remove the other risks surrounding
Hormuz. Blockade fears, attacks, and tanker-safety concerns remained.
That helps explain why the initial relief faded and Brent still
finished higher.

## In One Line

The 20 percent proposal vanished quickly, but the anxiety did not:
markets were watching the strait, not merely the fee.
```

## C. Length比較

| Version | Total words | vs V | vs L | Intro/Full Story | Point One | Point Two | In One Line |
|---|---:|---:|---:|---:|---:|---:|---:|
| V | 418 | baseline | — | 299 | 25 | 76 | 18 |
| L | 472 | +13.0% | baseline | 334 | 39 | 81 | 18 |
| **L2** | **355** | **−15.1%** | **−24.8%** | **268** | **36** | **32** | **19** |

**当初の想定への訂正**: ご指示ではPoint Twoでの長文化を主に想定して
いたが、実測ではVersion Lの語数増加(+54語)の内訳は、Intro/Full Story
部分が最大(+35語)、Point Oneが次(+14語)、Point Twoは最小(+5語)
だった。したがって今回のL2生成では、Intro/Full Story・Point One・
Point Twoの3箇所すべてを圧縮対象とした(結果的にPoint Twoが最も
大きく圧縮されたのは、法的背景・IMOの説明という、核心理解に不要な
一段落をまるごと省いたため)。

## D. 削除・圧縮内容

- **Intro/Full Story(299→268語)**: Version Lで追加されていた説明的な
  言い換え("It did not identify who would collect the money or who
  would pay. It did not explain how cargo would be valued, what
  currency would be used, or how exemptions and enforcement would
  work."という個別列挙)を、「具体的な仕組みはほぼ示されていなかった」
  という核心1文("How the reimbursement would be calculated,
  collected, or enforced remained unexplained")へ統合した
- **Point One(25→36語)**: Version Vでは25語と簡潔すぎたため若干増加。
  「20%という数字は明確だったが、具体的制度はほぼ示されなかった」と
  いう核心を保ったまま、Version Lの表現を維持
- **Point Two(76→32語)**: 最も大きく圧縮した箇所。Version V/Lにあった
  「IMO理事会が国際法上の原則を再確認した」という法的・外交的背景の
  段落を丸ごと省略した。**この情報はVerified Fact Ledger(HF-001)に
  引き続き保持されており、失われてはいない**。Point Twoの核心
  (「料金案が消えても、他のリスクは残った」という切り口)は維持した
- **In One Line(18→19語)**: ほぼ変更なし

いずれもFact Ledger外の新規情報を追加しておらず、Ledger Deviation
Checkで確認済み(F節)。

## E. Number Treatment

前回Version Lの数字処理方針(丸め・方向化・重複排除)を維持し、新たに
増やしていない。

- "20 percent"はANCHORとして維持
- "about 83 dollars"/"nearly 10 percent"、"about 85 dollars a barrel"/
  "finishing higher"という丸め・方向化はVersion Lのまま
- "34 million dollars"はSUPPORTING・仮説である旨を維持("That was
  hypothetical, not an actual charge.")
- Version Lにあった$32M近似値・時刻(10:16am/11:04am)・IMO会合番号
  (137th)は、前回同様L2でも登場しない

## F. Fact Safety

- **独立Fact Checker**: `PASS`(Web検索7回、矛盾・未確認主張ともに0件)。
  丸めた数値・$34M scenarioの位置付けはいずれも正確と確認された
- **Ledger Deviation Check**: `LEDGER_COMPLIANT`(逸脱0件)。IMO関連の
  段落を本文から省いたことは、Ledger外への逸脱ではなく、Ledgerに
  保持されたまま本文で選択しなかっただけであることを確認
- **技術的再試行**: Rewrite呼び出しは1回で構造(###見出し2つ)に合格

## G. Listening QA(9観点、V/L/L2比較)

| 観点 | V | L | L2 |
|---|---|---|---|
| 1. Listening ease | 数値の重複処理が必要 | 改善(重複排除済み) | L同水準を維持 |
| 2. Number density | 15個の数値 | 約8個相当 | Lと同水準(増やしていない) |
| 3. Cognitive load | 高い(3点セットを2回記憶) | 改善 | L同水準を維持 |
| 4. Narrative clarity | 明確 | 明確 | より簡潔に、核心が前に出る |
| 5. Editorial engagement | 強いフック | 維持 | 維持("The announcement sounded forceful, but the mechanism was almost entirely blank."等) |
| 6. Master-style transfer | 短い断定文 | 維持 | 維持、むしろ引き締まった分リズムが良い |
| 7. **Information efficiency(新規)** | 情報量に対し語数はやや冗長 | Version Vより情報量は増えず語数だけ増加(効率低下) | **改善**: 同じ核心情報をより少ない語数で伝達 |
| 8. Fact accuracy | PASS | PASS | PASS、Ledger deviation 0 |
| 9. Downstream suitability | 良好 | 数字面は良好、語数はやや長い | 数字・語数とも音声ナレーション向け |

**Information efficiency**については、L2が最も高いと判断する。IMOの
法的背景など、Point Twoの核心理解に必須ではない情報を削ったことで、
「1語あたりに伝える必要な意味」の密度が上がった。

## H. 比較Artifact

Version V・L・L2の全文(先頭から読める配置)、全体・セクション別語数、
Fact QA・Ledger deviation結果をまとめた。

**URL**: https://claude.ai/code/artifact/d83d5828-5fe2-4969-b81c-9c4d01fa5778

リポジトリ内の原本: `er003_output/spoken_first_01_r1/ADD03/comparison.html`

## Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL関連スクリプト・spoken_first_01スクリプト**: 無変更。今回も新規の独立ファイル(`er003_v1_spoken_first_01_r1_generate.py`)から、これらの関数を読み取り専用でimportした
- **A01・A02**: 変更していない
- **B1/A2/B2生成・TTS・audio assemble**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **新規Web Research**: 実施していない(既存のVerified Fact Ledgerのみ使用)

## I. 次のDecision

成功条件12項目中、11項目は満たしている。10番目(375〜418語のsoft
target)のみ、355語とやや下回る形になった。

| # | 条件 | 結果 |
|---|---|---|
| 1 | L2のFact CheckerがFAILではない | PASS |
| 2 | Ledger deviationなし | PASS |
| 3 | 数字密度がL以下 | PASS |
| 4 | 7/13→7/14時系列維持 | PASS |
| 5 | 20% proposalの意味維持 | PASS |
| 6 | scenario/actualを混同しない | PASS |
| 7 | Editorial engagementを維持 | PASS |
| 8 | Listening easeをLと同等以上に維持 | PASS |
| 9 | L2が原則418語以下 | PASS(355語) |
| 10 | 目標375〜418語に収まることが望ましい | **未達(355語、下限を17語下回る)** |
| 11 | Point Twoを含め、無関係な説明膨張が抑制されている | PASS |
| 12 | ユーザーが聞く記事として適切と判断できるか | ユーザー判断待ち |

技術的な成功条件(1〜9、11)はすべて満たしており、Fact safetyも確保
されている。10番目の未達は、自然さを優先した結果としての「やや
コンパクトすぎる」という程度であり、不自然な省略や意味の欠落は
確認されていない。

**提案**: 上記を踏まえ、A01・A02への展開(次のDecisionの選択肢)を
妨げる技術的な問題はないと考える。ただし、soft targetの下限をやや
下回った点について、A01/A02展開時にsoft targetの運用(「以上」ではなく
「範囲」として厳密に扱うか、下限超過は許容するか)を明確にしておくと
今後の判断がしやすいと考える。最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_spoken_first_01_r1_generate.py`(新規) | L2生成パイプライン(Rewrite→Fact Checker→Ledger Deviation Check、セクション別語数集計含む)。VFL-01・R4・spoken_first_01のProduction関数を読み取り専用でimport |
| `er003_output/spoken_first_01_r1/ADD03/version_l2.md`(新規) | Version L2本文 |
| `er003_output/spoken_first_01_r1/ADD03/length_report.json`(新規) | V/L/L2の全体・セクション別語数比較 |
| `er003_output/spoken_first_01_r1/ADD03/fact_qa.json`(新規) | Version L2の独立Fact Checker結果 |
| `er003_output/spoken_first_01_r1/ADD03/ledger_deviation.json`(新規) | Ledger Deviation Check結果 |
| `er003_output/spoken_first_01_r1/ADD03/run_summary.json`(新規) | 実行要約 |
| `er003_output/spoken_first_01_r1/ADD03/comparison.html`(新規) | 比較Artifact原本 |
| `er003_output/spoken_first_01_r1/ADD03/audit/`(新規) | prompt全文・API応答詳細等の監査証跡 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
