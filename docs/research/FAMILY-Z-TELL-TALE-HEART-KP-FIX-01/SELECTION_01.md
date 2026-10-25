# SELECTION_01: 『告げ口心臓』Standard KP#2 差し替え候補比較(FAMILY-Z-TELL-TALE-HEART-KP-FIX-01 委任_01)

## 現状(Step 1、API 0)
- 公開版=Chunk版 `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01`(公開 `user_test/family_z_tell_tale_heart_01/`)。
- 旧KP(Standard=内部名a2のみ。key_phrases/a2/keywords_canonicalized.json): #1 `make one's blood turn cold`(S8) / **#2 `catch of one's lantern`「人のランタンの留め具」(S17、差替え対象)** / #3 `go on talking`(S43)。
- Advanced(b1b)のKPは `sharpen someone's senses` / `cloudy film` / `never stir`。旧KPは含まれない=Advanced・Part 1(Advancedのみ描画)・Part 1解説/T1訳は無影響。
- 不適切の理由: 本文の逐語は `the catch of my lantern`(ランタンの留め具)で、特定物の具体名詞句。汎用性・学習価値が低い。

## 候補(Std本文 writer/std.md 実在、5語以下、既存validate_and_resolveで機械検証済み)
| 候補 | 本文位置 | 語数 | 学習価値/汎用性/話への即応 | 既存Validator | 判定 |
|---|---|---|---|---|---|
| **louder and louder** | S44 "The sound kept growing louder and louder!" | 3 | 「比較級 and 比較級」(だんだん〜)の汎用パターン(better and better/more and more)。物語のクライマックス(心臓の音が大きくなる)に直結。単独で自然・語形変化なし | PASS(逐語1回出現、canonicalizationもPASS) | **採用** |
| growing louder and louder | S44 | 4 | 同上だが `grow louder and louder` への基本形化をRule7が拒否(実測: 外側retry3回INVALID、`outer_retry_log.json`)。上位集合として`louder and louder`が最小形 | 基本形化NG | 不採用(実測) |
| gave one scream | S27 | 3 | give a scream/cry の汎用コロケーション。ただし `give` への基本形化は同様に拒否されるリスク、`one`が数詞的で一般化しづらい | 本文一致PASS | 次点 |
| get free of it | S9 | 4 | `it`が文脈依存の指示語(汎用性が下がる)、"get rid of"が通常形 | PASS | 不採用 |
| stood completely still | S20 | 3 | stand still系は有用だが過去形(基本形化がRule7で拒否される型) | PASS(本文一致) | 不採用 |
| could not stand any more | S47 | 5 | 有益だが既存Validatorが『有限助動詞を含む』で機械的に拒否(実測) | NG | 不採用 |

## 選定: `louder and louder`
- 根拠: (1)本文逐語・3語(5語以下) (2)既存KP選定仕様(Prompt 2: 本文連続一致・5語以内・最短形・学習価値)の機械検証をそのまま通る (3)他2件(`make someone's blood turn cold`/`go on talking`)と意味・語彙が重複しない (4)汎用「X-er and X-er」パターンで自然 (5)正しい意味=「だんだん大きく」(gloss再整合 ALIGNED、used_form=`louder and louder`)。
- 注: 選定は既存正式経路(Luna選定を固定選定へ差し替えるdriver、`kp_fix_driver_01.py`)でcanonicalization・gloss再整合・Redundancy QA・SRC D1・CMU語彙gateをすべて通した。
