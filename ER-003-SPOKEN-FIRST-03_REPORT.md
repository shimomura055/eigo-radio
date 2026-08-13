# ER-003-SPOKEN-FIRST-03 実行報告(A02 Point Balance Test)

**管理ID: ER-003-SPOKEN-FIRST-03**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**成功。** ER-003-SPOKEN-FIRST-02でA02のPoint One(144語)が本編
(166語)とほぼ同じ長さになり、「本文とは別の切り口を短く示す」という
Pointの役割から外れていた問題を是正した。

- Point One: 144語 → **47語**(目標30〜60語の範囲内)
- Point Two: 85語 → **44語**(目標30〜60語の範囲内)
- 本編(Intro/Full Story): **166語のまま完全維持**(0語差)
- In One Line: **28語のまま完全維持**(0語差)
- 総語数: 423語 → **285語**(観察用soft range 280〜420語の範囲内)
- Fact Checker: `PASS`(矛盾0件、Web検索6回)
- Ledger Deviation Check: `LEDGER_COMPLIANT`(逸脱0件)
- 技術的再試行: 0回(初回生成でSTRUCTURE_PASS)

Point One・Point Twoとも、ユーザー指定の核心メッセージ(下記D・E節)
を保持したまま、目標範囲内に収まった。本編は指示通り一切変更されず、
Point削減分を埋め合わせる形での本編延長も発生しなかった。

## B. Before / After 全文

全文は比較Artifact(H節)参照。以下は要点。

**Before(SPOKEN-FIRST-02 Listening-first版、423語)**: Point One・
Point Twoがそれぞれ144語・85語あり、Point Oneは特に本編(166語)と
ほぼ同等の分量で、試行の詳細(300世帯・80世帯・遵守内訳・介入群の
説明等)を本編同様の密度で再展開していた。

**After(Point Balance版、285語)**: Point One・Point Twoとも、
核心メッセージを1つの短い段落(3〜4文)に凝縮。試行の内訳数値
(300/80世帯等)や介入群の構成といった、核心メッセージの保持に
必須ではない詳細は削除した(これらはFact Ledger上に記録済みで
消失していない。単に記事本文からは削った)。

## C. Length Comparison

| Section | Before | After | Diff |
|---|---:|---:|---:|
| Intro / Full Story | 166 | 166 | 0 |
| Point One | 144 | 47 | −97 |
| Point Two | 85 | 44 | −41 |
| In One Line | 28 | 28 | 0 |
| **Total** | **423** | **285** | **−138** |

Point One・Point Twoとも目標30〜60語の範囲内に収まった(許容範囲
25〜70語よりさらに狭い範囲)。総語数はsoft range(280〜420語)の
下限に近いが範囲内。本編・In One Lineは指示通り完全無変更。

## D. Point One 圧縮の根拠

保持すべき核心(ユーザー指定): 「nighttime restrictionは実行し
やすく、睡眠改善の兆しもあった。ただし小規模・自己申告中心なので
proofではない」

**After全文(47語)**:
> In the pilot, participants described the night curfew as the
> easiest of the three interventions to manage, and reported the
> most consistent sleep improvements. But the study was small,
> self-selected, and based mainly on personal reports. The
> findings are promising signals—not proof of cause and effect.

削除した要素とその判断: 300世帯・80世帯という規模の数字、介入群の
構成(control/3介入群)、遵守内訳(most/some/a few)、9 p.m.–7 a.m.
という試行時点の制限時間帯。これらはいずれも「試行が実行しやすく
睡眠改善を示したが証明ではない」という核心メッセージそのものでは
なく、その周辺の方法論的詳細である。核心の4要素(easiest・most
consistent sleep improvements・small and self-selected・not proof
of cause and effect)はすべて保持した。

## E. Point Two 圧縮の根拠

保持すべき核心(ユーザー指定): 「restrictionはscreen timeそのもの
を消すのではなく、時間や媒体を移す可能性がある」

**After全文(44語)**:
> Participants often reported little change in daytime social
> media use. Some used it more before the restriction or after it
> ended; others switched to television or games. A nighttime
> setting may therefore shift screen use across hours or media,
> rather than make it disappear.

削除した要素とその判断: "That difference matters"という橋渡し文、
政策案が試行のアクセス遮断より緩やか(default protectionでopt-out
可能)という対比の再言及(本編で既に説明済みのため重複)、サービス
詳細が未定という一文(本編の主題ではなくPoint Twoの核心でもない)。
核心の2要素(日中利用はほぼ不変・時間や媒体への移動)はいずれも
保持した。

## F. Fact Safety

| Check | Result | Detail |
|---|---|---|
| Fact Checker | `PASS` | 矛盾0件・未裏付け具体的claim 0件(Web検索6回) |
| Ledger Deviation Check | `LEDGER_COMPLIANT` | 逸脱0件 |
| 技術的再試行 | 0回 | 初回生成でSTRUCTURE_PASS |

Fact Checkerは政府公式資料(gov.uk)・議会Hansard記録・AP通信記事と
照合し、圧縮後の記述(最も管理しやすい・最も一貫した睡眠改善・小規模
自己選択サンプル・日中利用の変化パターン)がいずれも一次情報と整合
することを確認した。なお、試行の夜間制限時間帯(午後9時〜午前7時)
と政策案の時間帯(午前0時〜午前6時)が異なる点を注記しているが、
記事はこれらを同一条件の実証実験だったとは記述していないため、
判定を変える矛盾ではないと結論している。

Ledger Deviation Checkは、圧縮後の記述がVerified Fact Ledgerの
範囲(fact_id単位)を超えていないか、数値のscopeを変更していないか
を確認し、逸脱0件だった。

## G. 11観点QA(Listening/Structure)

| 観点 | Before | After |
|---|---|---|
| 1. Listening ease | Point部が本編と同程度の情報密度で聞き手の負荷が高い | Point部が短く簡潔になり、本編との情報量の差が明確 |
| 2. Number density | Point Oneに300/80世帯等の数字が残る | Point部の数字を削減(Ledgerには保持) |
| 3. Cognitive load | Point部で新しい詳細を都度処理する必要がある | Point部は核心の再確認として機能し負荷が低い |
| 4. Narrative clarity | 本編とPointの役割の境界が曖昧 | 本編=事実経過、Point=意味づけという役割分担が明確 |
| 5. Editorial engagement | Point内の対比表現は維持 | 短縮後も対比の骨格("but"/"rather than")は維持 |
| 6. Master-style transfer | 短い断定文のリズムは部分的に本編に限定 | Point部でも短文リズムを保持 |
| 7. Information efficiency | Point部の情報密度は本編とほぼ同等で冗長 | Point部が「別の切り口の要約」として機能し効率的 |
| 8. **Point proportionality**(新規軸) | Point One(144語)が本編(166語)とほぼ同等で「第二の本編」化 | Point One(47語)・Point Two(44語)とも本編(166語)の3割弱に収まり、補足としての比重が適切 |
| 9. Fact accuracy | PASS(F節) | PASS(F節) |
| 10. Downstream suitability | Point部の音声化で本編と同等の尺を要する | Point部が短く、音声尺の面でも「補足」として自然 |
| 11. Fact Ledger整合性 | LEDGER_COMPLIANT | LEDGER_COMPLIANT |

新規追加した軸8「Point proportionality」により、SPOKEN-FIRST-02で
確認された「Point Oneが第二の本編になっている」問題が、After版では
解消されたことを確認した。

## H. Comparison Artifact

Before/After全文(先頭から読める配置)、語数比較表、Fact Safety表を
まとめた。

**URL**: https://claude.ai/code/artifact/098d66ea-c58d-4bf4-b52f-be0506eee90f

リポジトリ内の原本: `er003_output/spoken_first_03/comparison.html`

## I. Range Exception(範囲外事項の説明)

Point One・Point Two・本編・In One Line・総語数のすべてが目標/
tolerance/soft range内に収まったため、**範囲外事項は発生しなかった**。
数値に合わせるための不自然な追加・削除は行っていない(圧縮は核心
メッセージの保持を優先した結果として目標範囲に収まった)。

## Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL/spoken_first関連
  スクリプト**: 無変更。今回も新規の独立ファイル
  (`er003_v1_spoken_first_03_generate.py`)から、これらの関数を
  読み取り専用でimportした
- **A01・ADD03**: 再生成していない(A02のみが対象)
- **B1/A2/B2生成・TTS・audio assemble**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **新規Topic E2E**: 実施していない(既存Base記事とLedgerのみ使用)
- **「350語」のhard rule化**: 行っていない

## J. 次のDecision

以下から提案する。

1. 同じLength Policy(Point One/Two=30〜60語目標)をA01・ADD03にも
   適用し、横展開できるか確認する
2. 3ジャンルすべてで成立した場合、Spoken-first方式の仕様候補として
   CURRENT_SPEC.md等への統合を検討する
3. 完全新規Topic E2Eへ進む

**今回の結果を踏まえた所見**: A02について、Fact safety(Fact
Checker PASS・Ledger deviation 0件)を壊さずにPoint圧縮を達成でき、
新規軸「Point proportionality」で確認した通り、Point部が本編の
補足として適切な比重になった。ただしこれはA02(制度/SNS)1ジャンル
のみの結果であり、A01(スポーツ)・ADD03(経済)ではPointの元々の
長さ構成が異なる(SPOKEN-FIRST-02実測: A01 Point One=37語・
Point Two=60語、ADD03は個別に確認要)。他ジャンルで同様の
Point肥大化問題が発生しているとは限らないため、選択肢1の横展開検証
を経てから統合判断するのが妥当と考えるが、最終判断はユーザーに
委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_spoken_first_03_generate.py`(新規) | A02向けPoint圧縮パイプライン。VFL-01・spoken_first_01・spoken_first_01_r1のProduction関数を読み取り専用でimport |
| `er003_output/spoken_first_03/A02/`(新規) | version_after.md・length_report.json・fact_qa.json・ledger_deviation.json・run_summary.json・audit記録 |
| `er003_output/spoken_first_03/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
