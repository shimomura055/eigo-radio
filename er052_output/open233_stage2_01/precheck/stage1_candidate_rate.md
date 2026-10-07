# Stage1候補化率・Stage2判定(dev既知NG 100件、¥0・既存ログのみ)

委任: OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_01 作業4。生成: `stage1_candidate_rate.py`(同ディレクトリ)。詳細はstage1_candidate_rate.json。

## 分母
- dev項目 100件(split.json dev)。Checkerログあり=**47件**(ccp 26[18本中13記事]+rca 31のうちE2E_02由来21、22本のrun)。
- 対象外 53件: B3 Trial 39件(--no-checkerでChecker未通過)、RCA盲検再採点のB3 V0由来 10件(Checker無し)、過去重大(PAST-*) 4件(旧版runのログがログ集合に無い)。
- 版: 使用した33本(ccp 18+E2E_02の従来版5+P2版10)は全て stage1_coverage_v1、PROMPT_SHA256が現行と一致(replay_targets.json)。

## 方法と限界(重要)
- 項目はJA文(R0/R2由来)・評価者の説明、Stage1候補はEN文+日本語issue。**同一文かの対応付けはAPI無しの機械近似**。
  - `sentence_level`: (EN語/数値の共有3語以上)または(項目のfact_id一致 かつ 項目JA文とCheckerのissue+claimのJA3gram重なり>=0.4)。jb9k-n3のみRCA_jb9k_qvqc.md(S7.4候補化)で手動固定。人間確認なし。
  - `fact_level_only`: 同じfact_idの候補は在るが文までは確認できない(同factの別文を拾っただけの可能性を含む)。**候補化率の上限側を押し上げる**。
  - `indeterminate_fact_id_null`: 保留項目でfact_idが無く、機械では対応不能。
  - 目視で怪しい文レベル判定: hormuz-d5qr-p2、meta-7aqr-n1の2件(下限側は実質9件の可能性)。
- Stage1の「候補化」=当該runの初回Stage1 union_candidates(Rewrite後の再検出は含めない)。評価対象ENは採用版(Rewrite後の場合あり)で、初回Stage1が見た文と異なりうる。
- Stage2判定=対応候補のcycle1(初出)判定。`BLOCKING/QUALITY/ACCEPTABLE`は最終materiality。

## 全体
| 区分 | n | 文レベル | fact一致のみ | 候補なし | 判定不能 | 候補化率(下限=文/上限=文+fact) | Stage2最終 BLOCKING/QUALITY/ACCEPTABLE |
|---|---|---|---|---|---|---|---|
| 全体 | 47 | 11 | 18 | 1 | 17 | 0.234 / 0.617 | 3 / 8 / 18 |

## ガード対象型別(`sentence_type`をガード型へ写像)
ガード型の写像: 否定・不在=否定・不在 / 全称 / 多義語方向=方向・極性 / 主語新規出現・置換=主体 / 数値。その他は非ガード型(参考)。
| 型 | n | 文レベル | fact一致のみ | 候補なし | 判定不能 | 候補化率(下限/上限) | Stage2 BLOCKING/QUALITY/ACCEPTABLE |
|---|---|---|---|---|---|---|---|
| 主体 | 3 | 0 | 2 | 0 | 1 | 0.0 / 0.667 | 0 / 1 / 1 |
| 全称 | 2 | 0 | 1 | 1 | 0 | 0.0 / 0.5 | 0 / 0 / 1 |
| 否定・不在 | 4 | 1 | 2 | 0 | 1 | 0.25 / 0.75 | 0 / 2 / 1 |
| 数値 | 2 | 0 | 0 | 0 | 2 | 0.0 / 0.0 | 0 / 0 / 0 |
| 方向・極性 | 6 | 4 | 2 | 0 | 0 | 0.667 / 1.0 | 0 / 0 / 6 |
| 非ガード型(その他) | 16 | 2 | 3 | 0 | 11 | 0.125 / 0.312 | 1 / 1 / 3 |
| 非ガード型(因果・時間接続) | 8 | 3 | 3 | 0 | 2 | 0.375 / 0.75 | 0 / 3 / 3 |
| 非ガード型(限定語消失) | 6 | 1 | 5 | 0 | 0 | 0.167 / 1.0 | 2 / 1 / 3 |

## Stage2格下げ
- Stage1が(文/fact)対応候補にしたうちStage2のentryが見つかったのは29件。最終BLOCKING 3件、非BLOCKING(QUALITY/ACCEPTABLE) 26件 = **非BLOCKING率 0.897**。
- 初回のStage2 LLM判定(llm_materiality)がBLOCKINGで後から格下げされた例は0件(`llm_BLOCKING_then_downgraded`)。ほぼ全件がStage2 LLMの初回判定から非BLOCKING。
- 2nd opinion(`second_opinion.confirmed_downgrade=true`)は非BLOCKING判定のほぼ全てに付いている(下限を弱める方向の確認ではなく、2回目も非BLOCKINGで同意した記録)。2nd opinionが非BLOCKING→BLOCKINGへ引き上げた例は対象全記事で3件(別集計・本表の項目とは別)。
- 旧BLOCKING寄りの根拠(`s1_second_opinion_blocking`)等の詳細はjsonの`stage2`欄。

## 含意(事実のみ)
- ガード対象型(否定・不在/全称/方向・極性/主体/数値)のdev項目はeligible内でn=17。数値型は2件とも保留でfact_idが無く判定不能。
- Stage1の候補化は、fact_idが分かる項目の範囲では96.7%(fact一致を含む上限)だが、文レベル確証は23.4%に留まる。候補化後のStage2が非BLOCKINGとする点が主な取りこぼし経路。
- 文レベルの人間確認と、Stage1が文を直接拾ったかの確定にはr3 per-unit(support_fact_ids含む)の保存付きreplayが要る(作業5参照)。
