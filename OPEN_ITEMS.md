# OPEN_ITEMS — 未確定事項・技術的負債

**管理ID: ER-PM-001**
**最終更新: 2026-08-09**

検討中・候補・未確定仕様・技術的負債を記録する。確定済み仕様は書かない
(→[CURRENT_SPEC.md](CURRENT_SPEC.md))。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-01 | CEFR-A2の正式仕様(語彙・文長・語数等、全20項目)が一切存在しない | `PROTOTYPE / UNDER_REVIEW`(ER-003-A2-01→A2-02→A2-03と3段階で暫定仕様を検証中) | 仕様未決 | Blocking(CURRENT_SPECへ正式反映するまでは音声化・量産着手不可) | ユーザーがA2-03の3記事テキストを確認し、DECIDEDとするかどうか判断する。[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)参照 |
| OPEN-17 | ER-003-A2-03の新規語彙ルール(A2超一般語を記事全体で最大5語)が、prompt指示だけでは安定して達成できなかった(3記事とも実測10〜16語、目標の2〜3倍)。正式CEFR-A2 wordlistが存在しないため判定はLLM semantic QA(補助的手法)による近似 | `UNDER_REVIEW` | 検証結果・未解決 | Blocking(この語彙ルールをCURRENT_SPECへ`DECIDED`として反映する前に要判断) | ユーザーが実測結果(語のリストと理由)を確認し、(a)上限を緩和する、(b)QA結果を用いた反復修正の仕組みを別途新設する、(c)目安・目標値として運用する、のいずれかを選ぶ。安易な追加実装は先行させない |
| OPEN-18 | ER-003-A2-03の1文1数字ルールは、3記事中2記事(A01・A02)で違反0件、ADD03で1件(日付"July 13, 2026"を2つの数字として検出)が残った。日付(月+日+年)を1つの数字表現として例外扱いすべきかは、ユーザー指定の例外リストに含まれておらず未決定 | `UNDER_REVIEW` | 仕様の曖昧点 | Non-blocking | ユーザーが日付形式を例外リストへ追加するか判断する |
| OPEN-02 | A2の生成元(Natural English Sourceから独立生成 vs B1/B2からの派生簡略化)が、ユーザー依頼文言と公式decision recordで矛盾 | `DECIDED`(ER-003-A2-01実行分については独立生成を採用、恒久方針としての確定はユーザー判断待ち) | 仕様矛盾 | Non-blocking(今回は独立生成で実施し、矛盾は解消せず併記) | ER-003-A2-01では独立生成方式を採用したことをユーザーへ明示。恒久的な方針決定はユーザーに委ねる |
| OPEN-13 | ER-003-A2-STRUCT-01: Full Storyブロック分割+日本語signpost挿入 | `CANDIDATE / NOT_ADOPTED` | 構造支援候補 | Non-blocking | A2本文評価後、必要と判断されれば実装検討(今回は未実装) |
| OPEN-14 | ER-003-A2-STRUCT-01: Full Story前の簡易Listening Questions(2問程度) | `CANDIDATE / NOT_ADOPTED` | 構造支援候補 | Non-blocking | 同上 |
| OPEN-15 | [訂正・ER-003-A2-02] B1承認済みKey Phraseの語そのものがA2本文に残るかは要件にしない。A2 Key PhraseはA2本文確定後に本文から改めて選定する(方針確定) | `DECIDED` | 方針整理 | Non-blocking | 対応不要。当初「B1 Key Phrase語の消失」を問題視していたが、これは誤った懸念設定だったと整理した。実際の問題は主要fact自体がFull StoryからPointsへ流出していたことであり、これはER-003-A2-02で解消(下記OPEN-16参照) |
| OPEN-16 | A2-01でFull Storyの情報比重が崩れていた(3記事ともFull Story語数シェアが12.5〜29%まで低下、B1は49〜62%)。ER-003-A2-02のprompt改訂(情報削減を目的化しない、Full Storyに主要factを必須化)で3記事ともFull Story比重をB1同等(52〜65%)まで回復したことを確認済み | `DECIDED`(A2-02として確定、ただしCURRENT_SPECへの正式反映はユーザー承認待ち) | 検証結果 | Non-blocking | ユーザーがA2-02本文を確認し、DECIDEDとしてCURRENT_SPECへ反映するか判断する |
| OPEN-03 | CEFR-B2の音声化(Preview/Key Phrase/Full Story/Podcast組み立て)が一度も実施されていない | `TBD` | 未着手 | Non-blocking(B1公開には影響しない) | 着手するかどうか・いつ着手するかをユーザーが判断 |
| OPEN-04 | `used_form`/`key_phrase`の100%重複 | `DECIDED`(整理しない方針は確定済み) | 技術的負債 | Non-blocking | 実際に分ける必要が生じるまで対応しない(意図的放置) |
| OPEN-05 | 短文TTS hallucinationの根本原因(モデル側の挙動)が未解明 | `UNDER_REVIEW` | 技術的負債 | Non-blocking(strict検証+fallbackで運用上は吸収済み) | 発生時にstrict検証+fallbackで対応を継続。原因調査は優先度低 |
| OPEN-06 | ASR homophone ambiguityを機械的に判別する手段が未実装(同音異義語リスト等) | `TBD` | 技術的負債 | Non-blocking(human reviewフローで運用上は吸収済み) | 次に同種の事象が実際に発生してから検討(先回り実装はしない) |
| OPEN-07 | 正式なLUFS masteringが未導入(現状はscalar RMS基準の簡易調整のみ) | `TBD` | 技術的負債 | Non-blocking | 音質改善の必要が生じた際に検討 |
| OPEN-08 | ADD03初回Full Story生成(1回目3試行不合格分)の詳細ログが失われている(`stage_a_generate_body_audio`のバグ、2回目実行分からは修正済み) | `HISTORICAL`(バグ自体は修正済み) | 記録欠落 | Non-blocking | 再発防止は完了。過去分の復元は行わない |
| OPEN-09 | Dynamics3不使用の決定について、比較検討の詳細記録(なぜscalar RMSを選んだかの根拠レポート)が見当たらない | `TBD` | 記録欠落 | Non-blocking | 発見時に追記。現時点では推測で埋めない |
| OPEN-10 | A01(CEFR-B1)の「エピソード全体の最終承認」が未取得(`publication_status: NOT_APPROVED`のまま) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking(A02・ADD03の作業には影響しない) | ユーザーがA01最終版(r2)を通しで試聴し、公開可否を判断 |
| OPEN-11 | A02・ADD03も`user_quality_status: PASS`だが`publication_status`は`NOT_APPROVED`のまま(品質OKと公開承認は別判断) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking | ユーザーが公開判断を行うタイミングで確定 |
| OPEN-12 | `ER-003-B1_HANDOFF.md`が旧運用のまま(仕様・経緯を大量に含む29KB超のファイル)で、新ルール(直近作業再開専用)に未準拠 | `TBD` | 運用移行未完了 | Non-blocking | 次回以降の更新時に新フォーマットへ段階的に移行(今回は大規模書き換えを行わない) |

## 参照元

[CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
