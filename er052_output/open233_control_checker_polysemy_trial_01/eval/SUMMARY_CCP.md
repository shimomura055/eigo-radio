# SUMMARY_CCP: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_03 盲検評価の集計(¥0、2026-10-07)

到達Status: **EVALUATED(人間確認待ち)**。Trial(DEV)。Production変更なし。API費用 ¥0(既存成果物の集計のみ)。評価JSONは書換えていない。
**重大/Rollback判定は全て評価インスタンスの単独判定(人間確認前)=暫定**。確定は `HUMAN_REVIEW_PACK.md` のユーザー回答後(`preregistration_01.md` 6節)。

## MAP開封記録
- 開封時刻: 2026-10-07 20:21頃(最初に `eval/_private/MAP_ccp.json` を読込)。集計script `docs/pm/control_checker_polysemy_trial_01/tools/aggregate_eval_ccp.py` の実行時刻: 2026-10-07 20:27:12。
- 理由: 評価者A/B/C(各6記事=18記事JSON)+rollback_X(Meta10件)が全員分出揃い、Fableが委任_03で集計開始を指示した。評価JSONは読取専用。
- 検算: 記事JSON 18件(MAP解決不能 0)、rollback_X 10件、ng_items件数とstages値の不一致 0件、評価者A/B/Cの担当6記事ずつ割付どおり。

## 結論の要点(暫定)
- 重大あり記事 **0/18**(片側95%上限 15.3%)。Rollback JA R2 の誤読 **0/10**、累積 **0/22**(上限12.7%)。評価者とrollback_Xの3値ラベル不一致 **0件**(30判定中)。
- ただしRollbackの内訳は 正1/曖9/誤0(JA R2)で、**曖昧が9/10**(過去12本は曖昧9/12=75%)。固定最小Note(brief到達10/10)でも『正』は増えていない(JA R2 正1/10、過去 正3/12)。Noteの効果は曖昧→正の方向では確認できない。
- Gate STOP(1回目) 2/18(懸念なし)。原価 平均¥10.43・最大¥18.50・総額(失敗試行込み)¥195.5(合格)。Rewrite由来の新規重大 0。
- **要注意1点**: ④不要Rewrite率。事前登録文言(unclearは分子に含めず別掲)=**50.0%**(`>50%`に該当せず)、委任文の定義(before_was_ng=false+unclear)=**75.0%**(`>50%`で要注意)。事前登録の定義は変えず両方を併記し、裁定はFableに委ねる。
- 暫定の総合判定: 事前登録の文言を機械適用すると **PASS(暫定)**、委任文の不要定義を適用すると **CONDITIONAL(暫定)**。いずれも「N=18の範囲で検出されなかった」であり安全の証明ではない。

## ①〜⑦ 事前登録指標(数値)
### ① Rollback(Meta N=10、HC-012選択10/10、not_selected 0)
| 箇所 | 評価者 正/曖/誤 | rollback_X 正/曖/誤 |
|---|---|---|
| JA R2(主指標①a) | 1/9/0 | 1/9/0 |
| EN Checker前 | 2/8/0 | 2/8/0 |
| EN最終(Checker後) | 2/8/0 | 2/8/0 |
| 3箇所の悪い方(①b) | 1/9/0 | 1/9/0 |

- X判定と記事評価者判定の不一致: **0件**(10記事x3箇所=30判定すべて一致)。
- 『正』の記事: JA R2 は cz6g(rep4)のみ。ua6f(rep7)は JA が曖昧、EN(Checker前=最終)が『put on hold』で正(悪い方=曖昧)。
- **累積(過去12本+今回10本=N=22)**: 正4/曖18/誤0。誤読0/22、片側95%上限 **12.7%**(今回のみ 0/10=25.9%)。過去内訳は REPORT §91(5本: 正1/曖4/誤0)+§92(7本: 正2/曖5/誤0、rep9境界は曖昧扱いで固定)。
- EN Checker前→EN最終でラベル変化 0件(Checkerは Meta HC-012 文を変更していない)。
- 判定: ①a=**PASS**(暫定)。

### ② 重大NG(18本)
- 重大あり記事 **0/18**、重大NG件数 0(全工程)。pendingで leaning=major とされた件 0。片側95%上限 15.3%(0/18)。V0 0/55(5.3%)とは別条件(Checkerあり・Meta Note混入・N=18)であり同一条件比較ではない。
- 評価者が『重大寄りの境界』と書いたのは ai_control/jb9k item3(軽微に倒した)のみ明示。他の『境界』記述は軽微/Rollback関連。第2評価(重大記事の再評価)は重大0のため対象なし。判定: **PASS**(暫定)。

### ③ Gate STOP/生成不能
- 1回目Writer内部Gate STOP **2/18**(meta rep6、rep9。ともにphase2の JA_RECHECK_REQUIRED/JA_FACT_CHECK_STOP、同枠1回再実行で完走)。再実行後の生成不能 0。基準 ≤2/18=**懸念なし**。V5 4/12、V0 0/12、E2E_02 P2 1/10と比較。
- 参考(別掲): Checker final_state=STAGE4_ESCALATION が space_weapons/control rep1(4mjq) 1/18(blocking_confirmed_unlocatable_after_cap、cycle3)。これは Writer内部Gate STOPではなく③には含めない。評価対象のEN最終は重大0だが、Production経路ではStage4(人間確認)へ回る状態であり、**Fableへ要報告**(自己判断で扱いを変えない)。

### ④ 不要Rewrite率
- Checker Rewrite記録 run_facts=**10件**(6 run)。評価者が `checker_rewrites` に記録したのは **8件**(6記事)。**2件は評価者記録なし**(4mjq: records 2に対し評価1、kfuf: records 2に対し評価1。cycleをまたぐ同一箇所の重複/連続書換と推定、未確認)。分母は評価者記録の8件。
- before_was_ng: true 2 / false 4 / unclear 2。
- 不要率(false+unclear)=**6/8=75.0%**。事前登録文言(falseのみ)=4/8=50.0%。記事単位: Rewrite入り6記事のうち全件が不要(true無し)= meta/gj99,meta/jdmu,space_weapons/4mjq,space_weapons/kfuf(4/6)、falseのみ= space_weapons/4mjq,space_weapons/kfuf。
- 必要だったRewrite(true): ai_control/jb9k(『AISI事案』帰属補足)、meta/qvqc(情報共有可能性の拡張除去)の2件。不要寄り: gj99・jdmu(unclear)、qvqc タイトル・qvqc『sometimes a human』(false)、4mjq『four faces』文削除(false)、kfuf限定文削除(false)。
- 不要率>50%は『要注意』としてFable報告(事前登録④)。合否基準なし。

### ⑤ Rewrite由来の新規NG
- after_new_ng: **major 0** / minor 1(meta/qvqc タイトル変更『I Followed…』→『Meta Tested an AI Phone Agent and Found a Human』で主体が曖昧化)。Checker前ENに無く最終ENで新規に生じたNG(s2のみ)= 1件(同じqvqc-03)。基準 major=0 → **PASS**(暫定)。
- 逆に、Checkerが ENだけ解消したNGは jb9k-01(AISI帰属)・qvqc-02(情報共有の拡張)で、いずれもJAには残存(⑦参照)。

### ⑥ 原価(TTSなし)
- 平均 **¥10.43**・最大 **¥18.50**(meta rep2)・完了18本総額 ¥187.79・失敗試行込みディスク総額 **¥195.54**。基準 平均≤¥13.0・最大≤¥25・総額≤¥500 → **PASS**。参照 TRIAL-04 Control平均¥9.28、E2E_02 P2平均¥11.04/最大¥16.74。

### ⑦ JAのみ残存NG(OPEN-239関連、Checker書換はENのみ)
- 件数 **3件**(重大0/軽微3): ai_control/jb9k 01(scope)、meta/qvqc 02(added_fact)、meta/ua6f 02(scope)。いずれも軽微。

## 軽微NGの集計(HC-012 Rollback曖昧を分離)
定義: 全工程=ng_items全件(R0/JA R2/ENのいずれかに存在、同一誤り1件)、JA/EN最終=s1またはs2に残存。『Rollback曖昧』=fact_id=MUSE-HC-012 かつ kind=scope のng_items(Rollback 3値と二重計上になる)。
| 区分 | 軽微(全工程) | 軽微/記事 | 軽微(JA/EN最終) | 軽微/記事 |
|---|---|---|---|---|
| 含む(18記事) | 25 | 1.39 | 22 | 1.22 |
| うちRollback曖昧 | 9 | - | 9 | - |
| **Rollback曖昧を除く** | **16** | **0.89** | **13** | **0.72** |
| (参考)jb9k除く17記事、Rollback曖昧除く | 11 | 0.65 | 8 | 0.47 |

- 注: 件数25→うちRollback曖昧**9**→それ以外**16**(委任文の例示は10だが、cz6g(正)はRollback曖昧に該当せず、実数は9。Rollback 3値の曖昧=JA R2 9件と一致)。
- 比較(同一物差し、`SUMMARY_RCA.md`): B3 V0(Checker無)12記事 全工程0.58/最終0.58、重大0/12。E2E_02従来(Note無、Checkerあり)5記事 全工程1.40/最終0.60、重大0/5。
- 全工程の軽微/記事: 今回 含む1.39・除く0.89 ≷ V0 0.58 / E2E_02従来 1.40。JA/EN最終: 今回 含む1.22・除く0.72 ≷ V0 0.58 / E2E_02従来 0.60。
- 読み方: Rollback曖昧を除いてもV0(0.58)よりやや多いが、評価者間の差が大きく(下記)、N=18・単独評価のためこの差だけで悪化とは言えない。E2E_02従来(1.40)とは同水準以下。**jb9k(1記事で5件)が全体を押し上げている**(jb9k除く17記事・Rollback除く=0.65/記事)。
- 退行(R0→R2、軽微): 6件(meta 4、ai_control 2。jb9k 2件、meta 2xhw/cz6g/jdmu 2件)、重大0。V0 0.08/記事より多い(0.33/記事)。内訳にjdmuのHC-012(ロールバックのまま曖昧化)を含む。

## テーマ別(重大/軽微/保留/退行)
| テーマ | 記事 | 重大 | 軽微(全工程、含む) | 軽微(Rollback曖昧除く) | 軽微(最終) | 保留 | 退行 |
|---|---|---|---|---|---|---|---|
| meta | 10 | 0 | 16(1.60) | 7(0.70) | 14 | 2 | 4 |
| hormuz | 2 | 0 | 0(0.00) | 0(0.00) | 0 | 4 | 0 |
| space_weapons | 2 | 0 | 1(0.50) | 1(0.50) | 1 | 1 | 0 |
| sewer | 2 | 0 | 2(1.00) | 2(1.00) | 1 | 2 | 0 |
| ai_control | 2 | 0 | 6(3.00) | 6(3.00) | 6 | 1 | 2 |

- **ai_control/jb9k(評価C)**: 軽微5・退行2・保留1。内容=『AISI事案の封じ込め帰属が不明(JA)』『別の内部テストの一般化』『AIが外へ流れ出した事実も報告されていません(台帳の自己持ち出しなしを、直前の外部到達記述と矛盾して読める否定文にした。評価Cは重大寄りだが軽微に倒した)』『R2で現時点で人間が制御を失ったわけではないへ一般化』『防御策の対象取り違え』。Checkerは帰属補足1件(必要なRewrite)のみ。※ai_control s9dk は軽微1(認証情報流出元の限定)。
- hormuz 2記事は重大・軽微とも0(保留4: 出典帰属・Trump発言の強さ等)。space_weapons: 4mjq軽微1(counterspaceの連結)・kfuf 0、Checker STAGE4_ESCALATION 1件(4mjq)。sewer: 軽微2(うち1件はR0のみ)。

## 評価者別(評価者効果)
| 評価者 | 記事数 | 重大 | 軽微(全工程、含む) | 軽微/記事 | Rollback曖昧除く | 軽微/記事 | 保留 |
|---|---|---|---|---|---|---|---|
| A | 6 | 0 | 8 | 1.33 | 4 | 0.67 | 2 |
| B | 6 | 0 | 6 | 1.00 | 3 | 0.50 | 4 |
| C | 6 | 0 | 11 | 1.83 | 9 | 1.50 | 4 |
- 評価Cの軽微/記事が最大(担当にjb9k=軽微5を含む)。除外後も評価者間でC>A>B(1.50/0.67/0.50)。別TrialのRCA再採点でも評価者別に0.56〜1.22/記事と開きがあり(SUMMARY_RCA §4)、評価者効果は大きい。割付(どの記事が誰か)の偶然を含むため、V0/E2E_02との差は評価者を揃えた比較ではなく参考値。

## 事前登録の総合判定規則の機械適用(暫定、人間確認前)
| 指標 | 結果 | 判定 |
|---|---|---|
| ①a Rollback JA R2 誤読 | 0/10(累積0/22) | PASS |
| ② 重大あり記事 | 0/18 | PASS |
| ③ Gate STOP(1回目) | 2/18 | 懸念なし |
| ④ 不要Rewrite率 | 50.0%(false) / 75.0%(false+unclear) | 要注意判定が定義で分かれる(上記) |
| ⑤ Rewrite由来の新規重大 | 0 | PASS |
| ⑥ 原価 | 平均¥10.43/最大¥18.50/総額¥195.5 | PASS |
- **規則どおりの暫定判定**: 事前登録の文言(④分子=falseのみ、50.0%)=**PASS**。委任文の不要定義(unclear含む75%、`>50%`で要注意→CONDITIONAL条項)=**CONDITIONAL**。
- いずれも、(a)人間確認でRollback/重大の確定がなされるまで暫定、(b)『N=18の範囲で検出されなかった』であり安全の証明ではない、(c)Production採用は人間ユーザーのみ。
- 目的(1)Rollback N増し: 累積0/22(上限12.7%)達成。曖昧が22中18件(82%)残存=固定最小Noteで曖昧→正にはほぼ動かない。目的(2)本番経路のネガ: 重大・新規重大は見当たらず、要注意は④(不要Rewrite)とCheckerのSTAGE4_ESCALATION 1件、評価者C側のjb9k集中。

## plan §2(a): themeの渡し方の影響評価(事実)
- 今回18本は `--theme` に `topic.txt` の**内容**を渡した。TRIAL-04 Control(5本)・E2E_02(allfact_note_e2e_02、全run)の `entry_point.json` の `args.theme` は `er052_output/open233_polysemy_trial_02/ledgers/<slug>/topic.txt` という**パス文字列そのもの**だった(確認済み)。
- runner(er019)は `args.theme` を文字列のまま B3のstoryline/事実選択プロンプトの `{topic}` へ埋め込む(ファイルを読まない。コード上 `isfile/open` なし)。よって当時のStoryline/選定はテーマ文ではなくパス文字列を受けており、今回はテーマ文本体を受けた。台帳(`--ledger-txt`固定sha)は同一でresearchは0回のため、差が出るのは storyline_b3(brief)の入力のみ。
- 比較への影響: brief生成の入力条件が異なる(Control再確認の同一条件比較ではない)。方向と大きさは本データからは分離不能(未測定)。hormuzの内容テーマ文は『見出し行+代替採用の註記』を含む文字列だった点も同様に条件差(参考)。V0/E2E_02従来との対比は『参考値』扱いとする。

## Note位置(rep10 249j)
- rep10(249j)はNoteがHC-012 factの直後でなく冒頭Storyline行の直前(brief 8行目、HC-012は11行目)。249j のRollbackは JA/EN前/EN最終とも曖昧(評価者・X一致)、誤読ではない。位置不良が結果を変えた証拠はない(rep1〜9でNote隣接でも正は cz6g・ua6f(EN)のみ)。詳細は `HUMAN_REVIEW_PACK.md` の(d)。

## 付録: 生成物
- `eval/aggregate_ccp.json`(数値の正)、`docs/pm/control_checker_polysemy_trial_01/tools/aggregate_eval_ccp.py`・`build_summary_ccp.py`(再現script、API無し)。人間確認パック=`eval/HUMAN_REVIEW_PACK.md`。
