# 00d 評価表テンプレート(P' Trial、Before/After、空欄)
基準出典: docs/pm/ledger_clarity/05_trial_plan.md §1/§4。判定列はFable/ユーザー記入。diff材料=`er052_output/open233_ledger_clarity_p_trial_01/tools/ledger_diff_p01.py`・`fact_safety_p01.py`、Ent指標=`ent_metrics_p01.py`・`ja_copy_rate_p01.py`。
**n=1前提(M-e)**: After=1 chain。Beforeは「同topic meta 5 run(e2e_02)のHC-012型分布: 復元型3/5、うち重大ラベルY 1件」を参照値とする(chain数の分母比較はしない)。**本TrialのChecker結果をS1・precheck4種除外等の承認根拠に流用しない。**

## 品質① 重大Fact誤認(HC-012型)
| 測定項目 | Before値 | After値 | 判定基準 | 判定 | 備考 |
|---|---|---|---|---|---|
| HC-012型曖昧訳 発生(After 1 chain: 有/無) | 復元型3/5 run(重大Y 1件) | | After 1 chainで復元型・曖昧型が出ない。出なくても「再現率改善」とは言えず参考扱い | | After台帳にHC-012相当fact(人間コンシェルジュ機能の取り下げ/停止に関する記述)が無い場合=INCONCLUSIVE(評価不能、成功扱いにしない) |
| held-out(HF-012/HC-014/small_bag方向語fact)重大/run | | | Afterの重大/runがBefore以下(n=1、参考) | | |
| 決定論語彙判定(復元系語の有無) | | | 対象factで判定 | | |
| 重大件数(Fable/Sonnet二重ラベル) | | | labeling_guide準拠 | | |
HC-012型 段別3値ラベル(取り下げ系/復元系/曖昧):
| 段 | Before Fable | Before Sonnet | After Fable | After Sonnet | 備考 |
|---|---|---|---|---|---|
| B3 brief | | | | | |
| JA R0 | | | | | |
| JA R2 | | | | | |
| EN | | | | | |

## 品質② Checker精度
| 測定項目 | Before値 | After値 | 判定基準 | 判定 | 備考 |
|---|---|---|---|---|---|
| 重大件数 / 候補数 | | | 重大見逃し0維持 | | |
| Rewrite回数/run / human_review | | | A以下 | | |
| 不要NG(誤爆)件数(同列比較) | | | 誤爆増0件 | | |
| Phase1 既存SUPPORTED unit再判定(¥0) | | | 誤爆増0 | | |

## 品質③ 自然さ・面白さ(Entertainment)
| 測定項目 | Before値 | After値 | 判定基準 | 判定 | 備考 |
|---|---|---|---|---|---|
| 文数 / 平均文長 | | | 文長±20%以内 | | |
| type-token比 | | | ±20%以内 | | |
| 台帳逐語コピー率【主指標】JA側12文字連続(ja_writer/original.md または R2 vs 台帳txt、`ja_copy_rate_p01.py`) | 0.1518 | | +5pt以内 | | |
| 台帳逐語コピー率(EN 8語連続、参考) | 0.0(構造上無効) | | 参考のみ(台帳がJAのため) | | 合否に使わない |
| pairwise(順序入替2回)「劣る」率 | | | ≤25%かつ4軸いずれも過半数でない | | 判定割れ軸=引き分け |
| Fable抜粋確認 | | | 単独で合否にしない | | |
| 真の重大NG: Checkerが拾ったか | | | | | |
| 真の重大NG: 記事本文に存在するか(Fable) | | | | | |
| 真の重大NG: 記事本文に存在するか(Sonnet) | | | | | Fable/Sonnet不一致は併記 |

## 品質④ Fact安全性(必須条件)
材料=`fact_safety_p01.py`(接地・否定/因果語増減・改行・文字数・M4・順序/語義書き出し・書式)+`ledger_diff_p01.py`。ツールは合否を出さない。Before基準=`phase0/before_ledger_stats.json`(Before自身に適用)。
| 測定項目(ツール出力) | Before値 | After値 | 判定基準 | 判定 | 備考 |
|---|---|---|---|---|---|
| fact_id集合差 / fact数 | | | 追加・削除の理由が説明可能 | | ID不一致は類似候補併記のみ |
| 各fact内部の整合(claim/notes/conditions/date_or_periodの食い違い) | | | 食い違い0 | | Fable目視 |
| 原資料接地: 未接地の数値・日付・固有名(fact_safety (a)) | Before自身=14件(ベースライン、接地源がverification_notes中心のため) | | 新規の未接地0、またはBefore同等で全件説明可能 | | 接地源=draft構造化欄+verification_notes |
| 改行(`
`)件数(fact_safety (c)) | 0 | | 0 | | |
| 否定語・因果語の増加(fact_safety (b)、Before類似fact比) | | | 増加0 | | |
| claim行の新括弧/番号/否定/因果(M4、(e)) | | | 増0 | | |
| 日本語キー行・ブロック内空行(M4、(g)) | 0件 | | 0件 | | |
| notes_for_writer「順序:」「語義:」書き出し(f) | 0 | | 任意規則の遵守確認(材料) | | |
| claim平均文字数・Before比(d) | 92 | | 材料(長文化の程度) | | |
| 変更factの原資料照合(全件) | | | 変更factの全件 | 保留可 | URL再取得は別委任 |
| 新Fact/主体・因果・時系列/否定肯定反転/断定強化 | | | なし(必須) | | |

副作用観測: claim長文化により数字・日付がfactに増え、precheck(number_only)/再分類で「台帳一致」になりやすくなる可能性。候補数・重大数の変化を品質②の行と合わせて記録する。本TrialのChecker結果をS1・precheck4種除外等の承認根拠に流用しない。
