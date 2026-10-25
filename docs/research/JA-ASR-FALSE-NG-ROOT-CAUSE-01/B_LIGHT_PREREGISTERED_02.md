# B_LIGHT_PREREGISTERED_02(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_08、2026-10-25。評価実行前に凍結。API 0・Production変更0)
Opus条件Aレビュー(`OPUS_REVIEW_01_BLIGHT.md`)のM-1〜M-3・R-1〜R-8を受けた事前登録。`B_LIGHT_PREREGISTERED_01.md`(v1)は変更しない(v1の基準は**緩めず全件引き継ぎ**、比較基準列の是正と負例の追加のみ)。
評価対象=`b_light_proto_02.py`(DEV専用、sha256 `d041b1ca439a878f88b85dd1e590c8371569c740e01e663b6fcaa6c542c1aead`。評価前に凍結。不合格なら**変更せず**v3として再凍結して再評価)。test=`b_light_proto_02_test_01.py`(100 passed)。設計=`B_LIGHT_DESIGN_02.md`。評価スクリプト=`eval_b_light_api0_02.py`(保存済み転写のみ・socket guard・LLM判定なし・2回実行で出力一致)。
比較基準のProduction=**pin commit `89b630bd1086a638b2fec1f00d69bfae8722b665` のtop-level `*.py`スナップショット**(07Aが`er078_*`/`er007_*`を並行編集中のため)。07A適用後の姿は`proto_value_gate_fix_04.apply_in_process`(v4=07Aが適用する元の凍結proto)で再現する。07Aがcommitされた時点で、Production関数での再現一致確認(同じ入力で列`base+F1F2`と一致するか)を別途行う(本評価時点では未着=`prod07a_committed_at_eval=false`を出力に記録)。

## 0. 評価する列(M-1是正。「+v2」を比較基準から外す)
| 列 | 内容 |
|---|---|
| base | pin時点のProduction(Primary層+SCG許容集合[EXACT/NORMALIZED]) |
| **base+F1F2 (`F12`)** | base + OPEN-517 F1+F2(v4)。**07A適用後のProductionの代表**。v2のPrimary層・A4(a)は**含まない**(v2はProduction未採用) |
| **base+F1F2+β (`F12B`)** | F12 + `composite_judge`(proto v2、案β既定: garble説明あり・読み規則v2・Secondary読み食い違い=警告+試聴必須)。Primary NG[`p1_value_diff`/`final_gate_value_diff`/`p1_protected_diff:number_mismatch`/`secondary_not_accepted`]かつSecondary転写がある対にだけ適用 |
| (参考)`F12B_strict` | F12B だが読み規則を`normalize_ja`完全一致のみ(v2読み規則に**依存しない**)。βがv2読み規則にどれだけ依存するかを測る |
| (参考)`F12B_veto` | F12B だが Secondary読み食い違い(R-1)をvetoにする |
| (参考)`v2F12` / `v2F12B` | 旧基準(v1評価の「+F」「+B」)。v1評価との連続性のみのために並記。**判定基準には使わない** |
回帰・増分は**すべて `F12` と `F12B` の差**で数える。救済数・露出・N-1最悪ケース・合成負例は`F12`基準。

## 1. 合格基準(厳格化のみ可・緩和禁止。v1の1a〜1d・2・4・5・6・7を継承+追加)
| # | 基準 | 合格 | 不合格時 |
|---|---|---|---|
| 1a | N-3 30clipで F12がNGなのにF12BがPASSになった件(増分誤PASS) | **0** | REJECTED |
| 1b | N-1確定負例(Secondary=原稿そのもの)でF12がNGなのにcompositeがPASSになる件(露出) | 露出は『Primaryの数値表記が位取り断片崩れ[観測形: 前断片d×10^k+後断片]で読みも一致』の型に**限る**。それ以外の型は**0**。型内は全件列挙・審査 | 型外があればREJECTED |
| 1c | 合成負例**3群**(V1=v1の55件、**M3=複数atom[M-3]**、**FB=F-B・Secondary表記・R-3・R-4負例**)でcomposite(β)がPASSにする件 | **0**(群ごと) | REJECTED |
| 1d | 実Production履歴のP-S対(Secondary記録あり43)でF12がNGのものを composite がPASSにする件 | 全件列挙して個別審査。誤PASS疑いでREJECTED | REJECTED |
| 2 | 回帰: F12がPASSでF12BがNG(月題・N-3・履歴・Melos) | **0** | REJECTED |
| 3 | 月題12転写の増分(F12→F12B)と、うち**strict読みでも成立する数**・**veto時に成立する数**(v2読み規則/Secondary読み食い違いへの依存度) | 報告。増分1以上で『効果あり』、0で『効果なし』。strict増分0なら『効果はv2読み規則の採用に完全に依存』と明記 | 効果なし→採用提案しない |
| 4 | Melos副作用(F12とF12Bの判定が同一) | 変化**0** | REJECTED |
| 5 | 評価不能の件数開示(P-4 562件・未知493件・N-1 150[Secondary実転写なし]) | 開示 | 開示漏れ=不合格 |
| 6 | 決定性・隔離: 2回実行で出力一致/Production file変更0/Productionが`b_light_proto_*`をimportしない(test) | 満たす | REJECTED |
| 7 | 追加Azure呼出の見積 | 件数と費用を開示(判定基準ではない) | — |
| 8 | **(新)R-5予備集計**: 保存転写でのF1+F2の新規NG(base PASS→F12 NG)と値差NG(β対象になりうるPrimary NG)の件数(P-4・未知・履歴・月題・N-3) | 開示(判定基準ではない。Productionでの本計測は`R5_MEASUREMENT_SPEC_01.md`) | — |
| 9 | **(新)M-3**: 複数atom負例(1個目EXPLAINED+2個目矛盾・順序入替・同助数詞反復・Secondaryの値過不足/順序違い・Primary順序入替/余剰数値)と **F-B/Secondary表記負例**(かなN数詞・全角数字・空白run[`8000 900本`]・万を含む形・R-3違反の前断片[`12000|300`]・3断片・R-4[Secondaryかな数詞atom])が全てNG | 全件NG(上記1c群M3・FBに含む) | REJECTED |

## 2. Status写像(機械的。最終Statusは Fable)
- 1a・1b・1c・1d・2・4・6・9のいずれか不合格 → **REJECTED**。
- 全て合格 かつ 基準3の増分≥1 → **VALIDATED(限定)候補**(**Opus所見(iii)**: 効果が狭ければVALIDATED(限定)で止め**低優先の採用候補**とする)。限定の中身=評価母集団の狭さ・同一データでの再評価・合成データの比率・**v2読み規則への依存・Secondary読み食い違い(R-1)の試聴必須化**を併記。**VALIDATEDを上限とする**(Production採用はユーザー専決)。
- 全て合格 かつ 増分0 → **NOT_EFFECTIVE**。
- **T1(別題材の有料Trial)は非実施**: Opus所見(型の発生率約0.2%で無作為40 clipでは0件の可能性が高い=T1は非推奨)をFableが採用。頻度の確認は**Production側の計測(R-5)**で行う(API 0。`R5_MEASUREMENT_SPEC_01.md`)。本委任の有料run・実Azure呼出は0。

## 3. 事前に開示する既知の限界(v1から継承+追加)
1. 月題の数詞崩れの型(8000句800=復号不能、千九百=桁欠落、8000900/8000九百=断片連結)のうち**断片連結型だけ**がcompositeの対象。2エンジンの値矛盾はγ(第3証拠)でないと決まらず、UDR #136に触れる。
2. 実データでの断片連結崩れは月題の2転写型のみ(n=2〜3)。汎化は未確認(合成の正例は自作で実頻度の証拠ではない)。
3. N-3のAzure台本値追従0/3は母数が小さい。
4. **(M-1)βの読み判定はv2の読み規則(助詞は→わ/へ→えの発音一致・c2_blocked)を使う**。base+F1F2上ではProductionのPrimary層はこの同音異字を受理しないため、βを採用することは『Secondary値の裏付けがある範囲に限って』v2読み規則も採用することと同じ。`F12B_strict`列でその依存度を測る。
5. **(R-4)** 原稿・Secondaryの値atomは数字・漢数字表記に限る(OPEN-523/524を引き継がない)。
6. **(R-6)** CURRENT_SPEC L2865と実装(R4)の不一致はβ承認に混ぜない別件(`B_LIGHT_DESIGN_02.md`§9)。
