# OPEN-233 negative claim候補表(委任_04、gold確定はしない)

管理ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01
日付: 2026-09-29
種別: read-only抽出作業(¥0、API呼び出しなし)。Opus L2レビュー#1論点5推奨1
「既存Production実行でretryを経て最終的にLEDGER_COMPLIANTになった記事本文
からnegative claimを無料で抽出する」に基づく。

## 前提・抽出方法

- `er019_output/**/deviation_checks/*.json` 43件を走査し、`parsed.overall_status
  == "LEDGER_COMPLIANT"` かつ `parsed.deviations` が空(=Checker自身が一切の
  逸脱を検出せずPASSさせた)の28件を対象にした(MINORとして通過した記録は
  0件、Checkerが検出した場合はdeviations非空でMAJORへ収束するため、
  「通した」記録は常に空配列)。
- このうち、話題・Family(Hormuz/Meta/small_bag)・段階(a2=Standard/
  b1b=Advanced)で多様性を確保できる7ファイルを選び、`er050_gpt6_checker_
  comparison_trial_01.extract_inputs_from_prompt()`(既存read-only関数、
  変更なし)でarticle_text/ledger_textを逆展開し(`verify_reconstruction()`
  で全件一致確認済み)、Ledgerに明示されていない「一般常識レベルの背景
  説明・条件付き一般論・心理一般論」に該当するclaimを手動で特定した。
- 各候補について、出典run/段階・claim本文・関連Ledger fact_id(あれば)・
  Checkerが通した根拠・Opus分類案(ACCEPTABLE/QUALITY)・出典fileのsha256を
  記す。**gold確定はしない**(本表はユーザー確認待ちの候補表)。
- 特筆すべき対応関係: 候補1〜3は `family_x_b3_production_wiring_01/run_01`
  の **a2(Standard)** から抽出したが、**同一runのb1b(Advanced)**
  (`advanced_attempt1.json`、gold=LEDGER_DEVIATION MAJORx4、design書のB4
  fixtureそのもの)には、ほぼ同内容のclaimが**より断定的な表現**で含まれ、
  そちらはBLOCKING判定されている。同一Ledger・同一取材内容でも、
  Standard(ヘッジ表現)は通り、Advanced(断定表現)は止まるという表現差が
  観測された(Opus論点2のB4-b/c評価と直接対応)。

## negative claim候補(16件)

| # | 出典run/段階 | claim本文 | 関連fact_id | Checkerが通した根拠 | Opus分類案 |
|---|---|---|---|---|---|
| 1 | `family_x_b3_production_wiring_01/run_01/a2/standard_attempt1.json`(Meta Standard、LEDGER_COMPLIANT) | "Having a person take over is not always a bad thing. A human can handle situations that AI alone finds difficult. As a system, this may even be useful." | MUSE-HC-006(文脈) | `parsed.deviations=[]`(全逸脱ゼロで通過)。同一runのb1b/advanced_attempt1.jsonでは類似claim「A person can take over when AI alone has trouble」がMAJOR検出(design書B4-a、Opus分類=BLOCKING) | ACCEPTABLE(「may even be」のヘッジにより具体的なフォールバック機構の断定を避けている) |
| 2 | 同上 | "As AI becomes able to make calls or reservations for us, this question will become more familiar. The more useful the feature, the more people will want to know who is on the other side. They will want to know if it is AI or human." | なし(一般的未来予測) | `parsed.deviations=[]` | ACCEPTABLE〜QUALITY(design書B4-c「useful features make people want to know whether AI or a person is on the other end」に対応するOpus分類=ACCEPTABLE〜QUALITYと同型) |
| 3 | 同上 | "It is one thing to speak because you think a machine is listening. It is another when you know a person is listening. When people share their names, plans, or personal situations, it matters who listens." | なし(一般心理論) | `parsed.deviations=[]` | ACCEPTABLE(design書B4-b「People feel differently when...」「Names, plans, and private matters are easier to share...」に対応するOpus分類=ACCEPTABLE〜QUALITYと同型) |
| 4 | `family_x_refresh_e2e_01/meta/run_03/a2/standard_attempt2.json`(Meta Standard、LEDGER_COMPLIANT) | "The real challenge for AI phone calls is not only how they speak. It is also whether they can honestly tell people who is on the other end. The more useful a service is, the less it should hide the people working behind the scenes." | なし(一般倫理論) | `parsed.deviations=[]` | ACCEPTABLE〜QUALITY(B4-cパターンと同型の一般論) |
| 5 | 同上 | "However, this is only one report. It would be wrong to say this about all contract workers." | なし(過度な一般化への注意喚起) | `parsed.deviations=[]` | ACCEPTABLE(明示的な過度一般化の否定、安全側のヘッジ) |
| 6 | 同上 | "If AI can handle difficult phone calls, it seems very useful." | なし(条件付き一般論) | `parsed.deviations=[]` | ACCEPTABLE(仮定+ヘッジ「seems」) |
| 7 | `family_x_entertainment_production_runner_01/.../hormuz/b1b/advanced_attempt2.json`(Hormuz Advanced、LEDGER_COMPLIANT) | "Normally, removing the fee plan would seem likely to calm oil prices." | HF-009/HF-011(文脈、対比の前提) | `parsed.deviations=[]` | ACCEPTABLE(一般的市場期待の記述、「would seem」でヘッジ、実際に何が起きたかの断定はしていない) |
| 8 | 同上 | "The lesson is that changing the words in an announcement does not always change the price in the same way." | なし(一般的市場原理) | `parsed.deviations=[]` | ACCEPTABLE(条件付き一般論、「does not always」で断定を避ける) |
| 9 | 同上 | "The fee plan may be replaced, but events continuing at the same time do not simply disappear backstage because of one announcement." | HF-008/HF-009(文脈、継続緊張) | `parsed.deviations=[]` | QUALITY(境界)。design書B2「他の要因が残った。So価格は一度反応し高水準へ戻った」と類似の因果隣接だが、明示的な因果接続詞「so」を使わず「do not simply disappear」と婉曲表現にしている点でB2よりヘッジが強い |
| 10 | `family_x_b3_diversity_trial_01/small_bag/run_02/a2/standard_attempt1.json`(小物Ledger F001-F018、LEDGER_COMPLIANT) | "In 2026 fashion, mini bags are having a big moment." | F001(文脈) | `parsed.deviations=[]` | ACCEPTABLE(一般トレンド導入文、具体的固有名詞・数値なし) |
| 11 | 同上 | "This list matters. Large bags had not disappeared. Small and large bags appeared in the same season." | F007〜F013(引用済みfactの要約) | `parsed.deviations=[]` | ACCEPTABLE(Ledger引用済みfactの直接的要約、新規具体情報の追加なし) |
| 12 | 同上 | "In 2026, the two sizes seem to have different jobs. One carries what we need. The other helps create the look." | なし(解釈的フレーミング) | `parsed.deviations=[]` | ACCEPTABLE(美的解釈のフレーミング、事実性の主張ではない) |
| 13 | `family_x_b3_diversity_trial_01/hormuz/run_02/a2/standard_attempt1.json`(Hormuz Standard、LEDGER_COMPLIANT) | "This news feels like a short play in three acts. Act One was '20%.' Act Two brought a surprise. Act Three was an unexpected move in oil prices." | なし(編集上のフレーミング) | `parsed.deviations=[]` | ACCEPTABLE(純粋な物語的フレーミング、事実内容を含まない) |
| 14 | `family_x_b3_diversity_trial_01/small_bag/run_02/b1b/advanced_attempt1.json`(小物Advanced、LEDGER_COMPLIANT) | "Even so, the way trends look has changed. Bags are no longer in a game where one size alone sits on the throne." | なし(比喩) | `parsed.deviations=[]` | ACCEPTABLE(比喩表現、事実主張なし) |
| 15 | `family_x_entertainment_production_runner_01/.../meta/b1b/advanced_attempt1.json`(Meta Advanced、LEDGER_COMPLIANT) | "Even in an age when AI does our work, a human may still need to help. But that person should not appear secretly. If they step onto the stage, they should give their name first." | なし(一般的倫理原則・意見) | `parsed.deviations=[]` | ACCEPTABLE(一般的な意見・規範表明、Metaに関する事実主張ではない) |
| 16 | `family_x_refresh_e2e_01/meta/run_03/a2/standard_attempt2.json`(前掲、Meta Standard) | "Muse can call businesses and stores in the United States. It can book haircuts, check if items are in stock, and ask for price estimates." | MUSE-HC-001系(製品仕様、Ledger本体に一致) | `parsed.deviations=[]` | ACCEPTABLE(Ledger本体fact範囲内の製品仕様記述、新規性なし。参考: 純粋なledger_fact一致の例として他候補との対比用) |

## 出典fileのsha256(読み取り時点)

| 出典file | sha256 |
|---|---|
| `family_x_b3_production_wiring_01/run_01/a2/audit/deviation_checks/standard_attempt1.json` | `452557024763421eb2176fff6a427b2528c40e1eade7e3a3d0d263db101f843c` |
| `family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/standard_attempt2.json` | `644c3124dd5bc009cfa974d80c07a980d63a09efd350d3926a9072e423f804f0` |
| `family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/hormuz/b1b/audit/deviation_checks/advanced_attempt2.json` | `1f3ee0a06fa93d3aeda63a55a3b61a5b2c429658d01b3f294d8c966e5e9aafc3` |
| `family_x_b3_diversity_trial_01/small_bag/run_02/a2/audit/deviation_checks/standard_attempt1.json` | `ef6c46db7326ee43ebd8c1c0a53f0e8dcac1276d8891645a6f538c80805433ef` |
| `family_x_b3_diversity_trial_01/hormuz/run_02/a2/audit/deviation_checks/standard_attempt1.json` | `6fcbd800732573df4ae06c8aa5c8eddcc14fce4be4c468f1183a7e8c639924f7` |
| `family_x_b3_diversity_trial_01/small_bag/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` | `882984ed1d49e6392f2df6e98d803893dba55b921329f58a4bff5b498d182f65` |
| `family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/meta/b1b/audit/deviation_checks/advanced_attempt1.json` | `e087ea6d88b637eada54338974334ddff1c758001015f2355d7af83474158ae7` |

## 注記

- 本表はregression fixture化(freeze)を行っていない(委任文により「fixture化はせず」と明示指定)。将来のTrialでnegative
  regression fixtureとして凍結する場合は、上記sha256を基準に別途Fable/ユーザー判断を得ること。
- 候補1〜3と候補15の対比(同一Ledger・同一取材内容でStandard/Advancedの表現の断定度によって判定が分かれる)は、
  Opus L2レビュー#1論点4(recall/stability)とは別の観点(過剰BLOCKの表現依存性)として、次回設計判断の参考情報になる。
- 全16件ともAPIコスト¥0(既存保存済みJSON読込+read-only関数の再利用のみ)。
