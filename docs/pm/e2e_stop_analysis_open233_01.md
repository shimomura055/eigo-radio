# OPEN-233 E2E-ACCEPTANCE-01 E2E停止の¥0原因分析(委任_20、2026-10-05)

provenance: 既存E2E 2 run(fresh Stage 1、E2E途中、20 run未完)の再集計。VALIDATED不可。API費用¥0、コード変更なし。集計スクリプト/出力: `er052_output/open233_kpi_recovery_02_offline_01/e2e_stop_analysis_01.py` / `.json`。

## 1. 結論
- 停止原因: A2A3の1 run費用が¥6.21で閾値¥6(Fable設定、ユーザーKPIではない)に到達。主因は(a)見積誤り+(b)SC fixtureの性質。(c)構造的Wasteは確認できず(証拠は3節。ただし一部は推測)。
- 見積対比: B3 ¥4.55(見積mid ¥3.26の1.40倍)、A2A3 ¥6.21はabort時点(出口3'-R未到達、完走時¥6.8〜7.0=推測、見積mid ¥3.18の約2.1倍)。
- 20 run再予測(モデル): low ¥62.1 / mid ¥98.6 / high ¥122.8(元見積 47.3/66.5/86.0)。残19 runで mid ¥94.0 は残予算¥87.53を¥6.5超過。14 run案(残13 run) mid ¥55.3、8 run案 mid ¥21.1。

## 2. call種別の内訳(実測、円/件数、tokensはin/out/reasoning)
| 種別 | B3 | A2A3(abort時) | 見積(mid/記事) |
|---|---|---|---|
| Stage 1 r3(medium) | 0.557 / 1 (5.1k/6.1k/1.7k) | 0.565 / 1 (5.0k/6.2k/2.0k) | Stage 1計1.23(est.json個別 B3 1.38/A2A3 1.30) |
| Stage 1 r5(high) | 0.938 / 1 (4.7k/11.0k/8.3k) | 1.206 / 1 (4.7k/14.4k/11.5k) | 同上 |
| Stage 2 body・hook(1st) | 0.731 / 3 | 1.006 / 3 | Stage 2計1.50 |
| Stage 2 s1(2nd opinion) | 0.317 / 3 | 0.660 / 3 | (同上に含む) |
| floor_verify | 0.128 / 1 | 0.776 / 5 | 見積に項目なし |
| Rewrite | 0.328 / 3 | 0.605 / 6 | Rewrite+Recheck計0.17(high 0.35) |
| Recheck r3 | 0.296 / 1 | 0.668 / 2 | (同上) |
| Recheck r5v(high) | 0.637 / 1 (4.8k/7.2k/6.0k) | 0.724 / 2 | (同上) |
| 出口3'-R(r3) | 0.618 / 1 (5.1k/6.9k/1.8k) | 未到達 | 0.22(high 0.45) |
| 計 | 4.549 / 15 call | 6.209 / 23 call | 3.1前後 |
- Stage 1実測は見積の1.08倍(B3)・1.36倍(A2A3)。Stage 2(+floor_verify)はB3で見積(1.50)を下回った(1.18)。差は主にRecheckと出口。

## 3. 乖離の分類(a/b/c)
(a)見積誤り(確認): 見積の「Rewrite+Recheck 0.17」は旧1 callのRecheck(rep30実測0.17〜0.45)ベース。新Recheck仕様はr3+r5vの2 callで、B3 ¥0.93・A2A3 c1 ¥0.92・c2 ¥0.47。r5vはreasoning 4〜6k tokensが主因。出口3'-R全文もB3で¥0.62(見積0.22の2.8倍)。B3の見積超過+¥1.29のうち、Recheck+出口の見積差は約+¥1.1(Stage 2は−¥0.32で相殺)。floor_verifyは見積に項目なし(A2A3で¥0.78)。
(b)SC fixtureの性質(確認+推測): A2A3はc1でRewrite 5 call、Recheck後にcycle 2へ進み、c2だけで¥1.55(stage2 0.45+floor_verify 0.56+Rewrite 0.07+Recheck 0.47)=run費用の25%。B3のc2は¥0.22。SCは意図的に重大逸脱を埋め込むため仕様どおりの上振れ。SC 12 runはmodelでmid総額の約79%。
(c)構造的Waste: 確認できず。証拠: ①Rewrite全体がB3 ¥0.33/3 call、A2A3 ¥0.61/6 call(run費用の7〜10%)で、仮に全てWasteでも¥6超の原因ではない。②B3のHF-007は2回だがrewrite_records上は別span(タイトル下見出し「### The 20% plan changes overnight」とLedger長文1文、rewrite_kindもreplace_with_ledger_valueとnarrow_scopeで別)、各々e1で1回成功(確認)。③call数15/23(上限80)、API失敗0、cycle 2〜3、HARD_MAX_CYCLES内。④A2A3のHF-009(c1で4 call): ラベル順e2_paragraph→e1→e2_rewrite→(HF-003)→e1は、1回のrewriteの局所ラダー順(e1→e3→e4)と一致しないため、別deviation(別span)の複数Rewriteと推測。ただしA2A3のabort記録にcycles/rewrite_recordsが残らず、同一spanか別spanかの断定は不可(未確認)。⑤同一入力の再実行: floor_verifyは同一claim indexで2 call(c0_15/c0_16、c2_17/c2_18、2本目はcached 99.9%)、Stage 2 s1も同入力の2nd opinion。設計上の二重確認(推測、コード定義は未精査)で、不要callとは断定しないが原価削減のレバー候補(Safety影響あり、実装しない)。

## 4. rep30(Stage 1凍結、同一instance)との比較(後段のみ、Stage 1除く)
| | rep30 B3 | E2E B3 | rep30 A2A3 | E2E A2A3(abort) |
|---|---|---|---|---|
| 後段計 | 0.828 / 6 call / 1 cycle | 3.054 / 13 call / 2 cycle+出口再入 | 1.429 / 7 call / 1 cycle | 4.438 / 21 call / 2 cycle |
| Stage 2(c1) | 0.573 | 0.832 (1.45倍) | 0.821 | 1.215 (1.48倍) |
| Rewrite | 0.081 / 1 call | 0.328 / 3 call | 0.162 / 2 call | 0.605 / 6 call |
| Recheck | 0.174 / 1 call | 0.933 / 2 call | 0.445 / 1 call | 1.392 / 4 call |
- 増分分解(B3 +2.23): (i)候補増=Stage 2 c1 +0.26/floor_verify +0.13/Rewrite +0.25=+0.63(28%)、追加cycle(c2 Stage 2)+0.22(10%)、(ii)新Recheck +0.76(34%)、(iii)出口全文 +0.62(28%)。
- 増分分解(A2A3 +3.01、出口未到達): (i)=Stage 2 c1 +0.39/floor_verify +0.78/Rewrite +0.44=+1.61(54%)、追加cycle +0.45(15%)、(ii)Recheck +0.95(31%)、(iii)未到達(完走で約+0.6、推測)。
- Stage 1自体(rep30は凍結で0)がB3 1.495・A2A3 1.771を追加。

## 5. 20 run費用の再予測(モデル、推測を含む)
式: 1 run=Stage 1(est.json個別mid×(1.0/1.22/1.36))+Stage 2(rep30同instance×(1.0/1.45/1.7)、候補ゼロのinstanceはrep30 downgrade型平均0.27)+floor_verify(SC 0.1/0.45/0.8、非SC 0.05/0.15/0.4=推測)+Rewrite(rep30×1.5/3.7/4.0)+Recheck(rep30 recheck回数×0.47/0.8/0.93)+出口(Rewrite有で0.5/0.62/0.75)+SC追加cycle(0/0.75/1.5)。校正: モデルB3 mid 5.43(実測4.55、+19%)、A2A3 mid 6.00(実測>=6.21)。
| run種別 | 1 run low/mid/high | 本数 |
|---|---|---|
| SC(B3 3.1/5.4/7.2、A2A3 3.4/6.0/7.8、A4 6.2/10.5/12.2、A5 3.2/5.6/7.3、B4 3.7/5.3/6.4、neg5 3.4/5.8/7.6) | 平均 3.9/6.5/8.1 | 12 |
| 対(hormuz/meta Std・Adv) | 1.7〜2.0/2.2〜2.6/2.7〜3.1 | 4 |
| 負例(neg1,2,3,7) | 1.9〜3.1/2.3〜4.5/3.0〜5.4 | 4 |
| 20 run合計 | 62.1 / 98.6 / 122.8 | 20 |
| 残19 run(B3 s1実測4.55済) | 57.5 / 94.0 / 118.2(残予算87.53との差 +30.0/−6.5/−30.7) | 19 |
| 14 run案(SC n=1)残13 run | 34.4 / 55.3 / 69.7(差 +53.1/+32.2/+17.9) | 13 |
| 8 run案(対+負例のみ) | 15.8 / 21.1 / 25.7(差 +71.7/+66.4/+61.8) | 8 |
- 最大の不確実性: A4はrep30の1サンプル(3 cycle・20 call、後段のみ4.14)でmid 10.5。A4をA2A3並み(6.0)とすれば20 run mid約89.5。
- Safety evidenceへの影響: 14 run案はSC 6 fixtureを各1回のみで、A4-0揺らぎ・Recheck安定性・同一fixture再現性を検出しにくい(n=1)。8 run案はSCを含まず重大逸脱見逃しの測定が不能(Safety evidenceなし、Cost/Human Reviewのみ)。

## 6. 1 run閾値 ¥6→¥10
- モデルmidで¥6超: A4(10.5)・A2A3(6.0)、high: SC全6 fixture(6.4〜12.2)。¥10に上げると止まらなくなるのは、midではA2A3、highではA4以外のSC 5 fixture(いずれも7.8以下)。¥10超はA4のみ(mid 10.5、high 12.2、根拠はrep30の1サンプル=推測)。
- 残るWaste検知の捕捉力: cycle>5はHARD_MAX_CYCLES=3のため実質発火しない。call>80は平均¥0.16/callで約¥13相当(¥10閾値より緩い)。API失敗>3は課金されないエラーの検知。同一候補反復(`SAME_CANDIDATE_REWRITE_MAX=3`)は完走後の事後検査(`post_run_waste_flags`、確認)で、rewrite_records件数ベースのためラダー内call(例: HF-009の4 call)は数えず、abortされたrunでは評価されない。runtime中に同一入力・同一claimの反復を止めるフックはない。
- 評価: ¥10に上げても、数十call規模の構造的Waste(同一判定の数回反復、約¥1〜3)は¥10・call>80のどちらにも届かず捕捉されない。¥10閾値の捕捉対象は「1 run >¥10の暴走」のみで、構造的Wasteの検知は事前に決まった反復上限(同一claim_identityのcall数、同一prompt_sha256の反復数)をrun中フックにするのが本筋(コード変更はFable判断、本委任では実装しない)。

## 7. 純増の暫定値(参考、SC 2 runのみ、推測)
- B3 ¥4.55を上振れ側1記事として両記事同額なら、セット=2×4.55−差し引き0.83=+¥8.27(事前見込み mid +5.4/high +6.7、Fable暫定基準 >+8.4を僅差で下回る)。A2A3を完走見込み¥6.8とすれば+¥12.8。
- ただしSCは意図的に逸脱を埋め込む記事で、通常記事・Std/Adv対の代表ではない。非SC 8 runのモデル平均は1記事 low 1.98/mid 2.64/high 3.21(未実測の推測)で、セット換算 +3.1/+4.5/+5.6。Cost KPIの判定は対・負例の実測が揃うまで不可。

## 8. 確認/推測の区別と制約
- 確認: 内訳・費用・tokens・call数・B3のrewrite_records・rep30実測・Waste判定コード。推測: A2A3完走費用、モデル係数(非SC・floor_verify・追加cycle・A4)、floor_verify/s1の二重呼出の設計意図、HF-009の同一/別span。
- 制約: A2A3のabort recordにcall_log/cycles/stage2_resultsが無く、HF-009の素性を確認できない(再開時はabort時に部分call_logを保存すべき)。
- 本分析はE2E再開・コード変更・Production採用を伴わない。再開可否・閾値・run数・予算追加はユーザー判断(USER_DECISION_REQUIRED)。
