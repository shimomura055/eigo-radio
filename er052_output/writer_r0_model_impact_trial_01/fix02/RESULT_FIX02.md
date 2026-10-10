# RESULT_FIX02: 前回R0 + 今回R0 3モデル の12本 Risk Flagger(D0+D2記事モード、完全台帳、2026-10-10)

性質: Trial/DEV。Production変更なし、採用判断なし、優劣は書かない。Flagの有用/誤検知の確定はユーザー(人間確認)。数値は実測(usage x 登録単価 gpt-6.1-sol 入力$2/出力$10 per 1M、USD/JPY=160)。事前登録: `PREREGISTRATION_FIX02.md`。

**注意(事実の注記)**: 前回R0(FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 `new_writer/r0.md`、gpt-6-luna、Fact Lock付き)と今回Luna R0は、同じFact Lock構成・同じモデルの別生成物であり、両者の差は生成ごとのばらつきを含む。old腕の `ja_writer/original.md`(旧Writer構成・Fact Lockなし)も保存されている(streaming 1cc983b6 / space f29bb0e9 / byd 129cfc9a)が、Fable判断により本比較には含めていない。Flagは{D0rb ∪ D2}の文単位ユニーク件数(FIX01-A/RESULT_01と同定義)。confidenceは絶対評価に使わない。

## 1. 12行表(Flag件数 = D0rb∪D2、confidence閾値別)

| テーマ | R0 | >=0.10 | >=0.20 | >=0.30 | >=0.50 | 最大confidence |
|---|---|---|---|---|---|---|
| Disney+ | 前回R0(new腕 r0.md、Luna) | 0 | 0 | 0 | 0 | - |
| Disney+ | 今回Luna | 0 | 0 | 0 | 0 | - |
| Disney+ | 今回Sol | 0 | 0 | 0 | 0 | - |
| Disney+ | 今回Astra | 0 | 0 | 0 | 0 | - |
| 宇宙兵器 | 前回R0(new腕 r0.md、Luna) | 1 | 1 | 1 | 0 | 0.30 |
| 宇宙兵器 | 今回Luna | 0 | 0 | 0 | 0 | - |
| 宇宙兵器 | 今回Sol | 0 | 0 | 0 | 0 | - |
| 宇宙兵器 | 今回Astra | 0 | 0 | 0 | 0 | - |
| BYD | 前回R0(new腕 r0.md、Luna) | 0 | 0 | 0 | 0 | - |
| BYD | 今回Luna | 0 | 0 | 0 | 0 | - |
| BYD | 今回Sol | 0 | 0 | 0 | 0 | - |
| BYD | 今回Astra | 0 | 0 | 0 | 0 | - |

## 2. R0源別合計(行方向: 閾値別)

| R0 | >=0.10 | >=0.20 | >=0.30 | >=0.50 | 最大confidence |
|---|---|---|---|---|---|
| 前回R0(new腕 r0.md、Luna) | 1 | 1 | 1 | 0 | 0.30 |
| 今回Luna | 0 | 0 | 0 | 0 | - |
| 今回Sol | 0 | 0 | 0 | 0 | - |
| 今回Astra | 0 | 0 | 0 | 0 | - |
| **全12本** | 1 | 1 | 1 | 0 | 0.30 |

## 3. 全Flag一覧(confidence降順、全件。理由=Flaggerのquestion欄原文)

| # | conf | テーマ | R0 | 文 | 種類 | 対応Fact | 検出元 | 該当文 | 理由(Flagger question) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.30 | space_weapons | prev_r0 | s6 | 不在断定 | F-001 | d2 | 具体的なシステム名や攻撃能力は示されていないからだ。 | 文の「具体的なシステム名や攻撃能力は示されていない」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意を、情報が示されていないという不在の断定に広げているのではありませんか。 |

(全Flagの全フィールドは `flags/<theme>/<source>.json` の `union_flags` / `d2_flags` / `d0_flags` に保存。)

## 4. D0参考件数(総数に含めない gate_only=不在断定/数量時系列/増減・許可反転 と、D0本体)と D2件数

| テーマ | R0 | D2 | D0rb(総数に入る) | D0 gate_only(参考) | 総数(D0rb∪D2) |
|---|---|---|---|---|---|
| Disney+ | 前回R0(new腕 r0.md、Luna) | 0 | 0 | 0 | 0 |
| Disney+ | 今回Luna | 0 | 0 | 0 | 0 |
| Disney+ | 今回Sol | 0 | 0 | 0 | 0 |
| Disney+ | 今回Astra | 0 | 0 | 0 | 0 |
| 宇宙兵器 | 前回R0(new腕 r0.md、Luna) | 1 | 0 | 4 | 1 |
| 宇宙兵器 | 今回Luna | 0 | 0 | 2 | 0 |
| 宇宙兵器 | 今回Sol | 0 | 0 | 2 | 0 |
| 宇宙兵器 | 今回Astra | 0 | 0 | 3 | 0 |
| BYD | 前回R0(new腕 r0.md、Luna) | 0 | 0 | 0 | 0 |
| BYD | 今回Luna | 0 | 0 | 0 | 0 |
| BYD | 今回Sol | 0 | 0 | 0 | 0 |
| BYD | 今回Astra | 0 | 0 | 0 | 0 |

## 5. FIX01-A Disney+結果との一致

| R0 | FIX01-A Flag数 | FIX02 Flag数 | 記事sha一致 | 一致 |
|---|---|---|---|---|
| 今回Luna | 0 | 0 | True | True |
| 今回Sol | 0 | 0 | True | True |
| 今回Astra | 0 | 0 | True | True |

(前回R0のDisney+はFIX01-Aに対応セルが無いため照合対象外。Disney+の今回3本は同一記事・同一条件の再実行で、Flag0件が再現した。)

## 6. 条件同一性の機械確認(12セル)

| セル | 記事sha一致(事前登録) | 台帳sha一致 | Fact数/見出し数 | 文数 | D2 system prompt sha | Flagger model_id | effort | attempts | valid_json |
|---|---|---|---|---|---|---|---|---|---|
| streaming_price/prev_r0 | True | True | 7/7 | 20 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| streaming_price/gpt-6-luna | True | True | 7/7 | 19 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| streaming_price/gpt-6.1-sol | True | True | 7/7 | 22 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| streaming_price/gpt-6-astra | True | True | 7/7 | 24 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| space_weapons/prev_r0 | True | True | 22/22 | 21 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| space_weapons/gpt-6-luna | True | True | 22/22 | 21 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| space_weapons/gpt-6.1-sol | True | True | 22/22 | 20 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| space_weapons/gpt-6-astra | True | True | 22/22 | 22 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| byd_recall/prev_r0 | True | True | 11/11 | 18 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| byd_recall/gpt-6-luna | True | True | 11/11 | 21 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| byd_recall/gpt-6.1-sol | True | True | 11/11 | 23 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |
| byd_recall/gpt-6-astra | True | True | 11/11 | 22 | b8dacc147009a13b | gpt-6.1-sol | medium | 1 | True |

D2 system prompt sha(先頭16桁)の種類: ['b8dacc147009a13b'](FIX01-A/事前登録 b8dacc147009a13b と一致)。
台帳sha: テーマ内4源で同一(manifest由来)。Fact数==見出し数は driver内assertで強制(全12セル通過)。detectors配下5ファイルshaは実行後に再計算し事前登録値と一致(prompts_flagger 730bc55f / run_flagger 0962b6e4 / flagger_lib 4cb071ff / d0_directional 972634b4 / ledger_restore 7e465e5b)、detectors配下の追跡ファイル差分0件。

## 7. 費用(実測)

| セル | in tok | out tok(reasoning) | 費用円 |
|---|---|---|---|
| streaming_price/prev_r0 | 3217 | 8(0) | 1.0422 |
| streaming_price/gpt-6-luna | 3176 | 91(81) | 1.1619 |
| streaming_price/gpt-6.1-sol | 3333 | 8(0) | 1.0794 |
| streaming_price/gpt-6-astra | 3386 | 8(0) | 1.0963 |
| space_weapons/prev_r0 | 7373 | 383(264) | 2.9722 |
| space_weapons/gpt-6-luna | 7383 | 62(52) | 2.4618 |
| space_weapons/gpt-6.1-sol | 7259 | 52(42) | 2.4061 |
| space_weapons/gpt-6-astra | 7337 | 53(43) | 2.4326 |
| byd_recall/prev_r0 | 3922 | 30(20) | 1.3030 |
| byd_recall/gpt-6-luna | 3985 | 45(35) | 1.3472 |
| byd_recall/gpt-6.1-sol | 4125 | 32(22) | 1.3712 |
| byd_recall/gpt-6-astra | 4053 | 34(24) | 1.3514 |
| **合計** | | | **20.03** |

FIX02費用 JPY 20.03(上限30内)。API呼び出し: D2 12回(各セル1回、再試行0)。R0生成は0回(再生成なし)。

## 8. 失敗・再試行

12セルとも valid_json=True、attempts=1、形式再呼び出し0、再試行0、失敗0(上表の attempts 列)。

## 9. 使用モデル

- Risk Flagger: gpt-6.1-sol(最新世代最上位系)、effort=medium。
- R0生成モデル: 前回R0=gpt-6-luna(FACTLOCK-ASTRA-E2E-TRIAL-01 new腕)、今回=gpt-6-luna / gpt-6.1-sol / gpt-6-astra(WRITER-R0-MODEL-IMPACT-TRIAL-01、再生成なし)。Flaggerは最新でない旧モデルを使っていない。

