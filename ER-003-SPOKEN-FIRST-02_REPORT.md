# ER-003-SPOKEN-FIRST-02 実行報告(A01・A02 Listening-first 横展開検証)

**管理ID: ER-003-SPOKEN-FIRST-02**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**A01・A02とも成功。** ADD03で成立したListening-first方式(Number
Classification→Rewrite、Information Budget原則、今回は語数目標を
与えず自然な収束を観察)を展開した結果:

- **A01**: Fact Checker `PASS`、Ledger Deviation `LEDGER_COMPLIANT`。
  語数は354語→**275語(−22%)**
- **A02**: Fact Checker `PASS`、Ledger Deviation `LEDGER_COMPLIANT`。
  語数は409語→**423語(+3%)**
- 技術的再試行は両記事とも0回

ジャンルによって語数の収束方向が明確に異なった(スポーツは大きく圧縮、
制度は微増)。3ジャンル(スポーツ・制度・経済)を並べると、
Listening-first適用後の語数は275〜423語の範囲に分布しており、
「350語」のような単一の値へ収束するわけではないことが確認できた
(G節)。

## B. A01 Before / After

**Base(VFL、354語)→Listening-first(275語)**

主な変更点:
- xG(1.47対0.46)・ポゼッション(56.5%/35.2%/8.2%)・パス成功数
  (549/610対293/353)という3種類の追加統計をすべて削除し、
  「シュート15本対5本」という1つの数字だけに絞った
  (focus_instructionsで明示的に依頼した「1〜2個程度」の範囲内)
- 得点時刻(55分・85分・90+2分)、キックオフ日、Messiの年齢(39歳21日)
  など、試合展開・切り口に直結する数字はすべて維持
- Match 102(試合番号)・15:00 local time(キックオフ時刻)は
  Listening-first版で省略(前回のADD03と同種の「識別番号・時刻の
  精密値は不要」という判断)

全文は比較Artifact(H節)参照。

## C. A02 Before / After

**Base(VFL Run-1、409語)→Listening-first(423語)**

Baseの選定理由: ER-003-EN-DIRECT-VFL-01でRun-1・Run-2の2版が存在し、
両方ともFact Check PASS・Ledger deviation 0件で優劣を判断する材料が
なかったため、**生成順が早いRun-1を機械的に採用**した(内容を比較して
選ぶbest-of選択ではない)。

主な変更点:
- 309→"about 300 households overall"、81→"roughly 80 households"と
  丸めたが、**両方とも維持**した(309が母集団全体、81が夜間制限群、
  という区別自体が記事の理解に必要と判断されたため)
- 遵守内訳(53/23/5)を"most reported... some made minor changes...
  a few did not comply"と方向化
- autoplay/personalised feedsの「常時適用」という区別(旧ERROR-1の
  該当箇所)は維持
- 語数がわずかに増えた主因: 対比構造("Two points worth watching"の
  導入、"That difference matters"等の橋渡し文)を保った結果。ADD03の
  ケース(法的背景を丸ごと削除できた)と異なり、A02は2つの介入群
  比較・対比自体が記事の主張(初期設定の効果)を支える構造だったため、
  大きく削れる「余剰な説明」が少なかった

全文は比較Artifact(H節)参照。

## D. Number Treatment

代表的な処理例(全件は各記事の`number_classification.json`参照)。

**A01**:

| Original | Classification | Treatment |
|---|---|---|
| 15 shots to England's five | SUPPORTING/EXACT_REQUIRED | 唯一残す統計として維持 |
| xG 1.47 against 0.46 | SUPPORTING/DIRECTION_ONLY | 削除(方向のみなら"also favored Argentina"程度に統合可能だったが、今回は省略) |
| 56.5%/35.2%/8.2% possession | SUPPORTING/DIRECTION_ONLY | 削除 |
| 549/610 vs 293/353 passes | SUPPORTING/DIRECTION_ONLY | 削除 |
| Match 102 | DISPENSABLE/EXACT_REQUIRED | 削除 |
| 90+2 minutes | ANCHOR/EXACT_REQUIRED | 維持(劇的な決勝点の核心) |

**A02**:

| Original | Classification | Treatment |
|---|---|---|
| 309 households | SUPPORTING/APPROXIMATE_OK | "about 300 households overall"に丸めて維持 |
| 81 households | SUPPORTING/APPROXIMATE_OK | "roughly 80 households"に丸めて維持 |
| 53/23/5 compliance | SUPPORTING/APPROXIMATE_OK | "most/some/a few"に方向化 |
| midnight–6 a.m. | ANCHOR/EXACT_REQUIRED | 維持 |
| throughout the day(autoplay等) | ANCHOR/EXACT_REQUIRED | 維持(制度理解の核心区別) |

## E. Fact Safety

| 記事 | Fact Checker | Web検索回数 | Ledger Deviation | 技術的再試行 |
|---|---|---|---|---|
| A01 | `PASS`(矛盾0件) | 15回 | `LEDGER_COMPLIANT`(0件) | 0回 |
| A02 | `PASS`(矛盾0件) | 6回 | `LEDGER_COMPLIANT`(0件) | 0回 |

A01のfact checkerは、シュート数15対5をFIFA公式Post Match Statistics
Reportと照合し正確と確認。A02のfact checkerは、丸めた数値(約300/約80)
・方向化した遵守内訳がいずれも公平な丸めであることを確認した。

## F. Listening QA(9観点)

| 観点 | A01 | A02 |
|---|---|---|
| 1. Listening ease | 統計の重複処理が不要になり大幅改善 | 数字は残るが丸め・対比構造で処理しやすい |
| 2. Number density | 大幅低下(4統計→1統計) | Baseと同水準(意図的に維持) |
| 3. Cognitive load | 大幅低下 | Baseと同程度、ただし丸めにより多少軽減 |
| 4. Narrative clarity | 明確、得点経過に集中 | 明確、2つの発見の対比が保たれている |
| 5. Editorial engagement | 維持("The score stayed close. The shot count did not.") | 維持("Midnight arrives. A phone lights up."の導入含む) |
| 6. Master-style transfer | 短い断定文のリズムを維持 | 維持 |
| 7. Information efficiency | 高い(1統計で「圧倒的優勢」を十分伝達) | 中程度(対比の性質上、圧縮の余地は限定的) |
| 8. Fact accuracy | PASS(E節) | PASS(E節) |
| 9. Downstream suitability | 良好、数字面の負荷が大きく軽減 | 良好、Baseとほぼ同等 |

## G. Length Analysis

| Article | Genre | Base words | Listening-first words | Difference |
|---|---|---:|---:|---:|
| A01 | Sports | 354 | 275 | −79(−22%) |
| A02 | Policy/SNS | 409 | 423 | +14(+3%) |
| ADD03 | Economy | 418 | 355(L2) | −63(−15%) |

**観察**: 「350語前後へ自然に収束する」という単純な仮説は**支持されな
かった**。3記事の結果は275〜423語まで分布しており、ジャンル・記事
構造(統計の重複度、対比構造の有無)によって収束点が大きく異なる。
A01は元々統計の重複が多く削減余地が大きかったため大きく圧縮された
一方、A02は対比構造そのものが記事の主張を支えており、圧縮の余地が
限定的だった。

**Review triggerとの照合**(observation用soft guardrail):
- A01(275語)は300語を下回るため「核心情報が不足していないか」の
  確認が必要だったが、Fact Checker PASS・得点経過/決定的場面/切り口
  (Messiの無得点支配)はすべて維持されており、**不足は確認されな
  かった**
- A02(423語)は400語をやや超えるが、超過はわずか(+23語)で、
  対比構造を保つための必然的な語数と判断する
- ADD03(355語)は300〜400語の範囲内

## H. Comparison Artifact

A01・A02それぞれのBase/Listening-first全文(先頭から読める配置)、
Fact QA結果、3記事の語数比較表をまとめた。

**URL**: https://claude.ai/code/artifact/082dff4e-6509-4bdf-868e-a847efeb2b60

リポジトリ内の原本: `er003_output/spoken_first_02/comparison.html`

## Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL/spoken_first関連
  スクリプト**: 無変更。今回も新規の独立ファイル
  (`er003_v1_spoken_first_02_generate.py`)から、これらの関数を
  読み取り専用でimportした
- **B1/A2/B2生成・TTS・audio assemble**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **新規Topic E2E**: 実施していない(既存Base記事とLedgerのみ使用)
- **「350語」のhard rule化**: 行っていない

## I. 次のDecision

以下から提案する。

1. Listening-first方式をProduction候補として仕様化する
2. 350語前後をhard capではなくsoft target候補として整理する
3. 完全新規Topic E2Eへ進む

**今回の結果を踏まえた所見**: A01・A02・ADD03の3記事とも、Fact
safety(Fact Checker PASS・Ledger deviation 0件)を壊さずに
Listening-first化できた。一方、G節の観察により「350語」という単一の
soft target値は3ジャンルの実態に合わない(275〜423語まで分布)ため、
選択肢2をそのまま採用するなら、**単一の語数目標ではなく「ジャンル・
記事構造に応じて自然に収束する語数を許容する」という運用方針**が
より実態に即すると考える。技術的な成功条件(1〜7、8前半)はすべて
満たしており、選択肢1(仕様化)・3(新規Topic検証)へ進む条件は
揃っていると考えるが、最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_spoken_first_02_generate.py`(新規) | A01・A02向けListening-firstパイプライン(語数目標なし)。VFL-01・R4・spoken_first_01・spoken_first_01_r1のProduction関数を読み取り専用でimport |
| `er003_output/spoken_first_02/A01/`(新規) | A01のNumber Classification・Version L・Fact QA・Ledger Deviation・audit記録 |
| `er003_output/spoken_first_02/A02/`(新規) | A02の同上 |
| `er003_output/spoken_first_02/run_summary.json`(新規) | 実行要約 |
| `er003_output/spoken_first_02/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
