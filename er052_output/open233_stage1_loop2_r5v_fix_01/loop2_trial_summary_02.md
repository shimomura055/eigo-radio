# ループ2 実装是正+再測定 集計(委任_13、Step 2 G armは未実施=STOP)
provenance=fresh Stage 1限定(r3は段階A保存出力の再利用、r5-Vのみfresh)/E2Eではない。Trial(DEV)、Production未変更。
(注: G arm未実施のため`..._garm_01`は作成せず、本書はStep 1出力dirに置く。)

## Step 0 是正内容(¥0、単体テスト75件PASS)
- `r5v_target_units`: 対象=r3の**モデル判定**SUPPORTED(D適用前、`SUPPORTED->CANDIDATE(D理由/group)`も含む)+関係単位。r3 CANDIDATE/重複矛盾/coverage_gap欠落は対象外。fresh r3は`model_verdict`を保存、保存r3はstatus文字列から復元。
- `--reuse-r3-from`+`--negation-mode a`: 保存r3へ否定案aを再適用(D理由が否定のみの単位をSUPPORTEDへ戻し、group_inconsistentを再計算。近似=related_fact_ids先頭1件で再判定。42 runで140単位を復帰)。
- 不具合修正: モデルが単位IDを`[S2.1]`と角括弧付きで返すとorphan(unit_id不明)扱いになりM集計から落ちていた。`_norm_uid`で正規化+集計`is_model_cand`を`source_of`(unknown_unit_idもM)に整合。旧集計値は`*_idvalid_only`欄に併記。
- Step 1b用: `--plan cap`(SC18+hold-out 9=27 run)、`--r5v-force-targets gold`(Trial専用・測定用、SC=定義一致単位、hold-out=全判定単位を強制対象に追加。既定無効)。

## Step 1(保存r3 42 run、否定案a再適用、r5-V)
| 項目 | 基準 | low | medium |
|---|---|---|---|
| r3 M(再利用) | 16/18 | 16/18 | 16/18 |
| r5-V M(SC 18) | - | 0/18 | 3/18(A4-0 2、neg5 1) |
| ∪M | 18/18 | 16/18 | 18/18 |
| A4-0 s1/s2救済(r5-V M) | 2/2 | 0/2 | 2/2(s1=単位ID一致、s2=`[S2.1]`角括弧=orphan経由、いずれもS2.1を逐語引用) |
| hold-out M | 9/9 | 9/9(r3) | 9/9(r3) |
| neg5 ∪M | 3/3 | 3/3 | 3/3 |
| r5-V対象単位/run | - | 11.5(SC 15.0、NORMAL 12.3) | 同左 |
| NORMAL候補∪/記事 | 24.0 | 19.58 | 20.00 |
| r5-V費用/run・総額 | - | ¥0.164・¥6.87 | ¥0.285・¥11.97 |
| worst run・>¥3 | - | ¥0.31・0 | ¥0.65・0 |
| API失敗・欠落ID | - | 0・0% | 0・0% |
- 判定(基準1〜4): low=未達(A4-0 0/2)、medium=達成(∪M 18/18、A4救済2/2、hold-out 9/9、neg5 3/3)。ただしA4救済の1件は角括弧ID(修正前コードではorphan)経由で、厳密(ID一致のみ)集計では∪M 17/18・救済1/2。
- 否定案a再適用でNORMAL候補∪は24.0→約20(r3単独19.42)。D単独候補は0.3〜0.4/記事。
- 見積(script mid): low ¥15.45/medium ¥21.77に対し実績 ¥6.87/¥11.97(+30%超なし)。

## Step 1b(r5-V検出能力テスト: gold単位を強制対象、SC 18+hold-out 9=27 run、基準(5)=M>=17/18)
| 項目 | low | medium |
|---|---|---|
| r5-V M(SC 18) | 10/18(B3 2/3、A2A3 2/3、A4-0 1/3、A5 2/3、B4-a 3/3、neg5 0/3) | 12/18(B3 3/3、A2A3 3/3、A4-0 0/3、A5 3/3、B4-a 3/3、neg5 0/3) |
| 基準(5) 17/18 | 未達 | 未達 |
| hold-out(全単位強制)で候補を返した | 9/9 | 9/9 |
| 費用・worst・>¥3・API失敗 | ¥4.94(¥0.183/run)・0・0 | ¥8.01(¥0.297/run)・0・0 |
- 参考: 段階A r5(5-lite full、high)は17/18。A4-0とneg5でr5-Vは強制対象でも検出が不安定(medium 0/3、0/3)。
- 判定: low・medium とも基準(5)未達 → STOP。Step 2(G arm)へ進まない(効果:r5側のeffort引下げでは5-lite high同等の検出力に届かない所見)。

## Step 2(G arm)/(iii)見込み
未実施(STOP)。(iii)見込みは更新不能。参考(推測・未検証): Stage 1費用 = r3(high、段階A実測¥0.651/run)+r5-V medium ¥0.285 = 約¥0.94/run(段階A r3+r5=¥1.51)。NORMAL候補∪ 24.0→20.0で、Stage 2 fit ¥0.064/件なら約-¥0.26/記事。Rewrite費用・BLOCKING率はE2Eでないと不明。Human Review 0はE2Eでのみ判定可。
## 費用
本委任 ¥31.78(Step 1 low 6.87+medium 11.97、1b low 4.94+medium 8.01、Guardrail¥50内)、本管理ID累計 ¥111.91/枠¥238。
## 出力dir
`er052_output/open233_stage1_loop2_r5v_fix_01/`(low)、`..._r5v_fix_medium_01/`、`..._r5v_cap_01/`(low)、`..._r5v_cap_medium_01/`。既存dirは読取のみ(stageA_01等はgit差分なし)。
