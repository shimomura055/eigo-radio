# POSS_REP2_01 (委任_17、課題② possessor_role写像 rep2再現性確認、DEV/Trial専用・Production変更0)

使用モデル: luna(Production系列比較のため最新最上位ではない。理由=評価対象がluna生成そのもの、BUDGET_LOG_01と同じ)。
費用: rep2実費 20.10円(a1_c 9.83 + a1r_c 10.27、上限25円内)。KP案件累計≈227→≈247円(7-7の300円内)。案件台帳 `er112_output/kp_gm_trial_04/paid_calls.jsonl`、Trial_04累計 56.57→76.67円。
当日(JST 10-23)累計: 開始時 955.0円(daily_dev_cost_01 adopted) + 20.1 = 約975円。他案件予約 Family Y Phase B 180 + Family Z 100 を足しても約1,255円 < 上限1,400円。
STOP確認: stop_scope_check rc=0(`er112_output/kp_gm_trial_04/stop_check_17.json`)。Production module hash 不変(start/end一致 True、a1_c・a1r_c両方)。
注記: 委任_16の委任文ファイルがrepo上に存在せず、委任_17本文+既存runner仕様で実行。cap検査は既存の「発行前累計」方式(並列3、超過なし)。
実行: `py er112_kp_gm_trial_04_poss.py run --arms a1_c --reps 2 --cap 69.5 --workers 3` → `--arms a1r_c --reps 2 --cap 81.0 --workers 3`(別process)→ score。出力 `er112_output/kp_gm_trial_04/poss_runs/{a1_c,a1r_c}/rep2/`、集計 `poss_score_rep12.txt`。

## 1. arm x rep(所有格を含む目視gold付きitem、keyあり)
| arm | rep | CORRECT_GENERALIZED | KEPT | WRONG(誤り) | canon: PASS/INVALID/REVIEW |
|---|---|---|---|---|---|
| C0A(a1_c 現行系) | 1 | 28 | 5 | **9** | 33/2/1 |
| C0A | 2 | 27 | 6 | **5** | 32/3/1 |
| C1A(a1r_c role写像) | 1 | 29 | 14 | **0** | 35/1/0 |
| C1A | 2 | 29 | 13 | **1** | 35/1/0 |

(公式score集計=C0A/C1A両方keyのあるitemのみ n=80: C0A WRONG14・C1A WRONG0。上表はarm別にkeyのあるitemを全数えしたため、C1A rep2のWRONG1=`out of our hands -> out of someone's hands`[gold=self]は、C0A rep2側がINVALIDで公式scoreの対象外。)
- C1A rep2の唯一の誤り: `out of our hands`(R_df02db5b40)。roleは「self」と判定せず(roles上は誤り扱い)key=someone's。再現性は完全ではない。
- 修復(revert/repair)発火: role mode status 80件すべて NO_CHANGE(修復発火0)。raw=final=revert、すなわち改善はPrompt/role写像そのもので、事後修復は効いていない。
- role判定 vs gold: 80中 76一致、4不一致(いずれも gold=self を non_person と判定[rep1・rep2で各2、同一itemの繰り返し])。不一致でも出力keyはKEPT(its/their維持)側に倒れ、誤置換にはならない。
- INVALID/REVIEW_REQUIRED: C0A rep1 INVALID2+REVIEW1、rep2 INVALID3+REVIEW1(R_e6e80c11f1がREVIEW、R_63ec43c18cがINVALID、両rep共通)。C1A rep1/rep2とも INVALID1(R_63ec43c18c、C0Aと共通の別要因)。C1AがC0Aより悪化した箇所なし。

## 2. 非所有格(対照)item
- C0A vs C1A key同一: rep1 99/102(97.1%)、rep2 100/102(98.0%)、公式合算 199/204(97.5%)。所有格以外への副作用は、rep間で再現する差分は無く小さい。
- rep間(rep1 vs rep2)一致率(同一arm内、全item): C0A 129/135(95.6%)、C1A 143/149(96.0%)。非所有格のみ: C0A 95/98(96.9%)、C1A 104/106(98.1%)。所有格item: C0A 34/37(91.9%)、C1A 39/43(90.7%)。

## 3. ノイズ基準(C0A rep1 vs rep2)
- 同一promptでもC0Aの誤りは9->5と変動(±4)。しかしC0A誤りは両repとも5以上、C1Aは0->1。差(C0A合計14 vs C1A合計1[公式範囲では0])はrep間変動幅(4)を明確に超える。
- 再現した個別誤り: C0Aで両repとも誤り=`enforce their rules`(->someone's)、`find its way back`(->one's)、`occupy their thoughts`(->someone's)、`apply its findings`(->one's)、`questioned its methods`(->one's)。C1Aは両repでこれらをits/their維持またはone's(自己)へ正しく修正。

## 4. `pumps its fist`型・`close around me`の扱い
- `pumps its fist` / `pump its fist`(gold=self、元の本文は擬人化的な用例): C0Aは両repとも `pump one's fist`(CORRECT_GENERALIZED相当)。C1Aは rep1=`pump its fist`(KEPT)、rep2=`pumps its fist`は`pump one's fist`/`pump its fist`が割れ(pumps側 rep1 one's→rep2 its、pump側 rep1 its→rep2 one's)。= このtypeはrep間で不安定(KEPTと汎化が入れ替わる)だが、誤置換(someone's等)にはならない。
- `close around me`(gold未付与、非所有格扱い): 両arm・両repとも `close around someone`で同一。C0A=C1A。評価対象外(gold無し)として据え置き、劣化なし。

## 5. 所見
- C1A(role写像)は2rep合計で、C0Aの所有格誤り14(rep1:9, rep2:5)に対し、誤りは公式範囲で0、arm別全数えで1(`out of our hands`、rep2のみ)。rep1の「誤り9->0」はrep2でも再現(5->1)。誤りの質も維持(誤りはC0A側のone's/someone'sへの誤置換が主で、C1AはKEPT=its/their維持に倒れる)。
- 非所有格への影響は rep1/rep2 とも約97〜98%同一で、再現する悪化なし。canon INVALID/REVIEWはC1Aで増えていない(むしろ減少)。
- 残課題: (a)C1A rep2に誤り1(`out of our hands`、self->someone's)、(b)role判定のself->non_person誤り4/80(誤置換にならずKEPT側に倒れる)、(c)`pumps its fist`型のrep間不安定。いずれもrep2だけで致命的とは言えないが、完全な安定ではない。
- 結論: 本rep2は「VALIDATED候補を支持する」(rep1結果を再現。ただし完全ゼロではなく、2repの誤り計1/80、C0Aは14/80)。判定・採否はFable/ユーザー。サンプル(gold付き所有格item約40件x2rep)は限定的で、REAL記事への汎化はX/Z DEV注入E2E(委任_14)の範囲に留まる。
