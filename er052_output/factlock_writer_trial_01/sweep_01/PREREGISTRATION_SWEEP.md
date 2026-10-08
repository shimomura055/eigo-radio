# PREREGISTRATION_SWEEP: Fact Lock Writer prompt 変種sweep(FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04b用、2026-10-08 委任_04aで確定)

性質: Trial(比較実験、Production経路ではない、`APPROVED_FOR_PRODUCTION`なし)。Status上限=`MEASURED`(委任_04b)。**合否しきい値なし**。生成・評価は委任_04b。設計の詳細・全変種のprompt全文は同ディレクトリの `DESIGN_SWEEP_01.md`(付録A)と `variants.json`。

## 1. 問い
ユーザー指示(2026-10-08)「禁止・誘導は最小、指定を多くすると1パターン化する、5でも10でもパターンを振って方向性を決める、一回の評価で広く知見を得る」に基づき、規則の量・置き場所・形(規則形/目標形)・段の分担・連鎖・回数・手段リストを振った9変種を、事実面(崩れ)と面白さ(S0基準の勝率)と多様性(1パターン化)の3面で**1回の評価**で並べ、次に進む方向を決める材料を得る。数値化と並置のみ。方向の決定はFable/ユーザー。

## 2. 生成セル(固定)
- 変種: **S1, S2, S3, S4, S6, S7, S8, S9, S10 の9変種**(新規生成)。参照 S0(6x現行)・S5(Fact Lock v1)は**既存runを使い再生成しない**(`variants.json`の`references`、space_weapons/b3のS0のみ all6 r1がphase2でSTOPのためr2を参照)。
- brief 3本(テーマ3種x数値あり/なし): **meta b2**(数値なし、中核0)、**hormuz b4**(数値あり、中核3・周辺5)、**space_weapons b3**(数値あり、中核3・周辺2、v1で不整合が最も集中したbrief)。
- 反復1。**生成 = 9変種 x 3 brief x 1 = 27本**。モデル=6-luna(all6構成)、reasoning effort=high、Checker ON(v1・all6と同一構成)、JA Fact Check(R0直後・R2直後、must-fix1回・STOP)現行どおり、EN phase2現行どおり。並列度4(自動降格4->2->1、v1の`tools/driver_fl.py`方式に準拠し、`cmd()`を下記コマンドに差し替える)。
- 台帳=`er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`(v1・all6と同一)。briefは`briefs/<slug>/b<i>/selected_brief_factlock.md`(注記版。印除去が必要な変種はharnessが`sweep_01/briefs_nomarks/`に複写を作る)。
- out_dir: `er052_output/factlock_writer_trial_01/sweep_01/runs/<slug>/control/b<i>__<VARIANT>__r1`(DEV runnerのout_dirガード=`<runs_root>/<slug>/control/`を満たすことをdry-runで3 brief分確認済)。
- 1枠の技術的失敗は再実行1回まで、全体5回まで(v1のdriver既定`MAXRERUN=5`)。JA Fact Check STOP・JA再確認STOPは観測結果として記録し再実行しない。

## 3. 実行コマンド(cwd=`C:\Users\tensh\eigo-radio`、python=`.venv\Scripts\python.exe -X utf8`)
1テンプレートx(変種9 x brief3)。例(S4 x hormuz b4):

```
.venv\Scripts\python.exe -X utf8 er052_factlock_sweep_01_run.py --variant S4 --slug hormuz --brief-md er052_output\factlock_writer_trial_01\briefs\hormuz\b4\selected_brief_factlock.md --core-numbers-json er052_output\factlock_writer_trial_01\briefs\hormuz\b4\core_numbers.json --ledger-txt er052_output\open233_polysemy_trial_02\ledgers\hormuz\control\research_ledger\verified_fact_ledger.txt --out-dir er052_output\factlock_writer_trial_01\sweep_01\runs\hormuz\control\b4__S4__r1 --budget-jpy 12 --yes-run-paid
```

brief組: `meta b2` / `hormuz b4` / `space_weapons b3`。事前の無課金確認: 上記に `--dry-run` を付ける(manifest全項目を出力、API呼び出しなし)。単体テスト: `.venv\Scripts\python.exe -X utf8 -m pytest er052_factlock_sweep_01_test_01.py -q`(29 passed)。

smoke: 本番の前に **S8(連鎖切り) x hormuz b4 と S9(R3) x hormuz b4 の2本**を先に流し、(a)S8の`manifest.json`の`chain_actual_cut_log`がR1・R2の2件あり、`ja_writer/revision1_untagged_raw.md`と`sweep_retag.json`が出る、(b)S9の`sweep_r3.json`が出て`adopted`/`rejected_reason`が記録される、(c)全変種共通で`factlock_summary.json`の`residual_brackets_total`=0・`manifest.residual_bracket_scan.unexpected`が空、(d)model_id実測=gpt-6-luna、を確認する。この2変種は本変更で初めて実機を通す部分(他の変種はprompt差のみで、v1実機通し済みの経路を再利用)。確認NGは設計を直して再smoke(最大1回)。

## 4. 評価設計(1回の評価で方向を決める)

### 4-1. 評価パック(盲検)
- 対象: 新規27本 + S0の既存3本 + S5の既存3本 = **33本**。各記事のJA R2(タグ除去後`ja_writer/revision2.md`。S9はR3採用時R3)・EN(`b1b/article.md`)・R0・R1。匿名コード化しMAPを`sweep_01/eval/_private/`へ隔離(v1の`tools/eval_fl.py`/`eval_ta_shared.py`を流用可)。**S0・S5・新規27本を同一パック・同一評価者(LLM2系統: gpt-5.6-luna / gpt-6-luna)で一緒に採点**する。評価者へ変種・セル・モデルは非開示。rubricは`docs/pm/b3_trial_01/eval_rubric.md`(v1と同一)。STOP記事も母数に含め、R0(と到達した最終段)を評価する。

### 4-2. 面白さ(S0基準の勝率)
- 各新規記事(27本)を**同briefのS0記事とpairwise**(位置入替2回、LLM判定、人間確認なし)= 27 x 2 = **54判定**。アンカーとして S5 対 S0 の3 x 2 = 6判定も行う(v1の再測)。変種同士の総当たりはしない。
- 判定プロンプトはv1の`pairwise`(`eval/pairwise.json`作成時の定型)を踏襲し、**理由を型に分類**して残す: (a)比喩の重なり・作り込み、(b)硬い表現(台帳表記の転記由来)、(c)流れ・順序の分かりやすさ、(d)結論の繰り返し、(e)窮屈さ、(f)その他。
- 出力: 変種x{S0に対する勝ち判定数/6(3 brief x 2順序)、brief対単位の一貫勝ち数/3}。

### 4-3. 事実面
- 盲検rubric: 重大件数、軽微NG/記事(JA R2・EN別、テーマ別)、保留/記事、R0->R2退行。
- 照合(測定のみ、harness内で自動): タグあり変種は (i)不整合率(文単位)・unsupported主張/記事・unknown_tags、(ii)タグなし文の`new_specific_claim`/`background_general`/`hedged_speculation`/記事、(iii)数値不一致(`hedge_changed+not_core`)/記事・`core_used_without_tag`・`marks_echoed`、(iv)R0->R2のタグ付き文の維持/改変/削除/added。**S8は(i)(iv)を参考値**(事後タグ再付与のため)で、主は盲検・(ii)(iii)。S1・S2・S7は数値規則を持たないため(iii)は「現行並みか」の観察で読む。
- 工程: JA Fact Check MAJOR率・must-fix率・STOP率、記号Gate must-fix率、EN再生成(JA再確認)率、Checker findings/Rewrite件数、S9はR3の採否(`sweep_r3.json`)。
- 基準値: v1(S5)の同指標(`eval/FACTLOCK_CHECK_SUMMARY.md`、24本)と、新規S5相当3本の値。

### 4-4. 多様性(1パターン化)
- 機械: 同変種3記事の ①冒頭1文の形(問いかけ/断定/場面描写/数字/その他)の異なり数 ②結びの形(問い/まとめ/余韻/その他)の異なり数 ③タイトル・本文の比喩語(舞台・映画・探偵・ゲーム等の頻出語リストの共通語数、char bigram Jaccardの最大値)。3テーマ(別話題)でも同じ型に寄るかを見る。S0・S5の3記事も同じ指標で並べる(基準)。
- LLM所見: 変種ごとに1 call「この3記事の構成・比喩・導入・結びの共通点」を所見で出力(11変種分)。**どの変種が1パターン化しているか**の記述所見(しきい値なし)。

### 4-5. 判定の出し方(しきい値なし)
1. **一覧表**(11行: S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10)x{面白さ(S0基準の勝ち判定数/6)、軽微NG/記事(JA R2)、重大件数、不整合率(タグあり変種のみ)、new_specific_claim/記事、数値不一致/記事、JA FC MAJOR・STOP、多様性(冒頭の異なり数/3、結びの異なり数/3)、R2文字数}。
2. **軸別の要約**(各1~3行、`DESIGN_SWEEP_01.md` §3の比較対応表に従う): ①タグの副作用はあるか(S0対S1) ②R0の1文禁止だけで事実は守れるか(S1対S2) ③数値規則の効果(S2対S3) ④R0だけ固めてReviseを自由にした増幅量(S3のR0->R2悪化) ⑤R1/R2の2文制約は面白さを落とすか(S3対S4) ⑥骨格->肉付けは成立するか(S4対S6) ⑦目標形は規則形より良いか(S7対S4、複合比較と注記) ⑧連鎖切りは効くか(S3対S8) ⑨R3は効くか(S4対S9) ⑩手段リストは1パターン化を招くか(S4対S10、多様性の列)。
3. 3brief中のそろい方: 各軸で3 briefが同方向か、割れたか(割れたら割れた事実のみ記載)。
4. 「言えないこと」: N=3本/変種のため有意性は主張しない。変種効果とテーマ効果の交絡。照合(i)(ii)は6-luna自己判定。S1/S2/S7はbrief印の有無が他変種と異なる。S6/S7は複数の差を同時に含む複合比較。S8の再付与は6-luna割当。盲検・pairwiseの評価者はLLMのみ(人間確認なし、重大候補は`HUMAN_CHECK`に列挙)。
5. **推奨は書かない**。次の方向(どの変種を残す・組み合わせる・Opusレビュー・Production採用提案)はFable/人間ユーザー。

## 5. KPI provenance
面白さpairwise・照合指標・JA FC/STOP・盲検rubric=**fresh**(Trial harness)。S0・S5の既存記事・既存値=**reuse**(進行中Trial・v1の既存run)。briefは注記版=reuse。E2E自己確認: No。

## 6. 費用見積(上限¥300)
- 生成27本: v1実測 ≈¥4.3/本(`MANIFEST.json`のcost_total、ライター+Checker)x27 ≈ ¥116。S8の事後タグ再付与(6-luna 2 call/本x3)・S9のR3+FC(約1.3倍の追加、3本)は数円。
- 照合(i)(ii): 1runあたり最大5~6 call、v1実績から ≈¥0.6/本x27 ≈ ¥17(上の¥4.3に含まれない場合の保守見積)。
- pairwise 60判定 ≈ ¥30、盲検採点33本 ≈ ¥40、多様性所見11 call ≈ ¥3。
- 合計 ≈ ¥206(積み上げ)~ ¥245(委任文の概算、27本x≈¥5を採用した場合)。**上限¥300(Guardrail)**。
- T-3定型文: 「上限¥300(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## 7. 時間見込み・並列化
- 生成60分(27本、4並列、v1実測 ≈6~7分/本 -> 7 wave ≈45~60分)+smoke 2本 ≈15分(先行)。評価40分、集計20分。計 ≈ 2時間。
- 並列化: 生成待ちの間に、盲検パック作成script・pairwise実行script・多様性の機械指標script・集計script・一覧表テンプレートを先行準備(前工程出力に依存する実行だけ直列)。盲検採点とpairwiseと多様性所見は、生成完了後に3つ並列で流せる(互いに独立)。

## 8. 開始条件
- `er052_output/factlock_writer_trial_01/RESULT.md` が存在すること(委任_02bの採点完了。**本委任の作業時点で既に存在を確認済**。ただし内容は未読)。
- メモリ/並列: 他の4並列生成が走っていないこと(進行中Trialの生成完了済み)。
- Fableが委任_04bの発行を判断。ユーザーの費用了承(上限¥300)。
- 診断(`v2_design/DIAGNOSIS_01.md`)が出ていれば、その内容による変種の追加・差替えをFableが判断してから開始(変種数は10まで可、現在9)。

## 9. 固定sha(2026-10-08、本委任の終了時点)
| 項目 | sha256 |
|---|---|
| er052_factlock_sweep_01_run.py | `1a48d1092ff6bcba41e76fded50dd506f9a44cbedd8b06e105a9f07420f66f90` |
| sweep_01/variants.json | `07cd5d4a121075aeada26e1dd49d2d9a5e961fe8c3062d8f34c45f87d74a8eda`(各runの`manifest.json`の`variants_json_sha256`にも記録) |
| production(無編集): er019_family_x_ja_writer_o_r1_r2_01.py | `b3b5b9ff0eb6e97241d50cd70b0443b43007fd32680f764911f69d70420b28e6`(v1事前登録と同一) |
| production(無編集): er003_v1_en_direct_vfl_01_generate.py | `63286c2b558cdcc3cd2def090bae6975ca48385e962dd53c9c70f7e116afde80`(v1事前登録の`0aac53ec...`とは異なる。別タスク[Production配線]の変更と見られるが、本委任では未確認) |
| reused(無編集): er052_factlock_writer_trial_01_run.py | `6a04e22d73e40d3becc83927959325a41fd90f4d892161a7ad5b14f869fa2a55`(v1事前登録の`0b20b3dd...`とは異なる。本委任では編集していない。委任_02b等による後続変更の可能性) |
| reused(無編集): er052_all6_writer_trial_01_run.py | `9412a19e43753f28d55e6915e5337a5053aa037b347fb8664e261c68f508d7d0`(v1事前登録と同一) |
各runの`manifest.json`に、実行時点のproduction・harnessのshaとpromptのshaを記録する(差異があれば委任_04bで検知できる)。

## 改訂履歴
- 2026-10-08 委任_04aで初版。
- 2026-10-08 委任_04b(生成側)改訂: ①変種S11(S4と同一で数値規則のみ「中核数値も原則書かない。記事の理解に本当に必要な場合だけ、台帳の表記のままで最大1つ」に差替え、診断の「数字2.6倍」の切り分け)とS12(DESIGN_02案A=v1規則維持+語り口規則、`v2_design/blocks_v2.json`のA.R0/A.R1_R2を逐語使用、ユーザー仮説「誘導は効かない」の検証端点)を追加し新規11変種x3 brief=33本、②共通修正T(「番号は【事実N】のNだけを使い、ニュース欄の事実の後ろに書かれているF-011やHF-002のような別の番号は、タグに使わないでください。」)を、S7以外の全タグ付き変種(S1~S4、S6、S8、S9、S10、S11、S12[S12は案AのR0規則1に同一文が既に入っている])のR0へ追加(S1~S10のR0がv1.0の事前登録時点から変わる点に注意)、③判定文の中立化(評価者へ誘導語を渡さない)と不戦勝(相手本文なし)の除外は委任_04c(LLM評価)で適用する。harnessにR0 mode `replace_all`(ブロックが固有名詞文を逐語で含むことを検査して全置換)を追加。固定sha(改訂後): run=`c8626f6c82e48663ca5f0be2b14d47aa2ee3e54788dcfffb9ee016cfae995b29` / test=`3a45d52b6da0fa36edd677e74e6287e4a732e919dbe9d0a01351768d85603457` / variants.json=`6519d798838b2504914a89b5710d54646da4e9889d058626b3430c70c8925c38`。生成は`sweep_01/tools/driver_sweep.py`(4並列)。

## 評価規則v2(評価前固定、Opus任意レビュー反映)(委任_04c、追記時刻 2026-10-08 12:24:24、評価実行前)

本節は評価実行前に追記・固定。全文は `sweep_01/eval/EVAL_RULES_V2.md`(Opus任意レビュー: `docs/pm/opus_l2_review_factlock_sweep_eval_01.md`)。上の§4-2〜§4-5(9変種・勝ち判定数/6・勝ち負け一致のみ)は以下で置換される。対象は11変種(S1〜S4,S6〜S12)+参照S0・S5=33本(S11=S4の数値規則差替え、S12=v1規則維持+語り口規則)。

### v2-1. 面白さ(M1,M3,M2,M4,M5,O1)
- 判定文(逐語): 「以下は同じニュースをもとにした、日本語ラジオで読み上げる記事AとBです。あなたが聞き手だとして、続きを聞きたい、誰かに話したくなるのはどちらですか。事実の正確さは別に評価するので考えなくてかまいません。winnerはA/B/tie。reasonは、そう感じた箇所を具体的に挙げて日本語2文以内で。」developer=「あなたはラジオ番組の聞き手です。」評価軸は1つ(総合選好)。reasonは事後に型分類(比喩の重なり/硬さ/流れ/繰り返し/窮屈さ/その他、機械の語彙分類)して読む。
- 比較: 各変種×3 brief を同briefのS0(space_weapons b3はall6 r2)とpairwise。入力=JA最終稿(`ja_writer/revision2.md`、タグ【事実N】除去)。2順序(A/B入替)。S5対S0もアンカーとして3 brief×2順序。
- 主judge=gpt-6-luna(reasoning medium)。併用=gpt-5.6-luna(O1、**一致度のみ報告**、スコアは主judgeを使う)。
- スコア化(M3): 1 brief あたり、2順序とも変種勝ち=1、割れ(片方勝ち片方負け、またはtieを含む)=0.5、2順序とも変種負け=0。変種ごとに brief別スコア(3つ)、合計(0〜3)、割れ率(割れbrief数/3)。
- 不戦勝(M2): judge前に両本文の存在・非空をassert。STOP等でR2がない記事はjudgeにかけず「不戦敗」列へ(スコアは0点で計上せず、合計は有効brief数で注記)。
- ノイズ基準(M4): S0 r1対r2(両本文がある全対、先に実施・`NOISE_BASELINE.md`)の「同条件の3 brief合計」分布の min〜max を「ノイズ幅」とし、変種の合計が幅の内側か外側かを列に出す。
- 読み規則(M5、事前固定): **明確に上** = 3 briefすべてで1.0かつ合計>=2.5 / **明確に下** = 3 briefすべてで0.0(合計<=0.5) / それ以外は**同等**(中位の序列はつけない)。metaは数値規則の軸(S2→S3、S11)では読まない(数値なし)。S9でR3が不採用になった本はS4同等として別記する。
- 推移性: S0基準の比較なので「S0より明確に上か下か」までを読む。変種どうしの順位は読まない。

### v2-2. 事実側(M6)
主指標(変種比較に使う):
1. **重大**: 軽量rubric call(B3 rubricの重大定義、JA R2+EN、1記事1 call、gpt-6-luna)で出た重大候補を**全件**`HUMAN_CHECK_SWEEP.md`へ(人間確認待ち)。変種の比較には件数を参考に載せるが確定値ではない。
2. **決定論の数値チェック**: 本文の数字(アラビア数字、漢数字+単位を正規化)のうち、brief(`storyline_b3/selected_brief.md`)と台帳(`research_ledger/verified_fact_ledger.txt`)の数値集合に無いものの個数/本。
3. **増幅(ii)**: 各runの`factlock_check_r0.json`/`r2.json`の`ii_untagged`のlabel=`new_specific_claim`件数の R0→R2 増加分(R2−R0)、/本。タグなし変種(S0)は計測できず n/a。
4. **JA Fact Check の MAJOR率・STOP率**(MANIFEST/各run由来)。
参考列: 軽微/記事(同call内で出させる。ENのみに出たもの=翻訳段由来は分離して変種比較から除く)。付録: 照合(i)不整合率、軽微/記事。
注記(必須): 「事実は変わらない」は「この規模(N=3)・この指標で検出できる差がない」の意味であり、事実が保たれていると証明するものではない。照合は6-luna自己判定。

### v2-3. 多様性(M7)
- 主指標: (a)比喩領域が3記事で一致した数(領域=舞台/ゲーム/探偵/料理/スポーツ/天気/旅/医療/その他の語彙表、各記事の最多領域が3記事で同じなら1、領域集合の全記事共通領域数も併記) (b)決まり文句(「もし…なら」「あなたなら」「かもしれません」「ではありません」「ではない」等の定型表現)が3記事すべてに出る種類数。
- 参考: 冒頭1文・結びの型の異なり数(最大3)、char bigram Jaccard(付録、話題差に支配される)。
- LLM所見: 変種名を伏せ、S0・S5を含む11組(3記事)をシャッフルして**1 call**で共通点の記述所見。

### v2-4. 文体(論点4、O2、O4)
- 6指標(です・ます文率、アラビア数字、比喩異なり、仮定語[推量]、問い、字数)を1000字あたりに正規化(です・ます率は比率のまま)。定義は`tools/style_metrics.py`(04b)と同じ。
- O2: 全pairwise対(変種×3 brief+S5)の「変種 − S0」指標差の符号を、**勝った側/負けた側別**に集計(勝者−敗者の符号。割れ・tie対は除外)。因果と読まない(文体は媒介の経路にすぎず「この文体を指定すれば面白くなる」とは読まない)。
- O4: 台帳との逐語n-gram率(転記度): 本文の字8-gramのうち台帳に含まれる割合。
- 11変種間の相関はとらない。

### v2-5. 出力表(SUMMARY_SWEEP)の列
変種 / brief別スコア×3 / 合計 / 割れ率 / ノイズ幅内外 / 不戦敗 / 決定論数値NG(/本) / 増幅(ii) / JA FC MAJOR・STOP / 比喩領域一致数 / 決まり文句共通数 / 文体6指標(1000字あたり) / 3段階の読み。付録: (i)不整合率、軽微/記事(JA由来・EN由来分離)、5.6併用の一致度。
軸別要約(各1〜3行、事実のみ)+「面白さが同等以上、かつ決定論指標(数値NG・増幅)が悪化していない変種」の一覧(事実の並べ替えであり推奨ではない)+言えること/言えないこと。

### v2-6. 限界(事前記載)
N=3 brief×1反復、LLM判定のみ(同系列モデル)、brief交絡(話題と数値有無)、判定文は総合選好1軸、割れ率が高いこと自体が「差がない」情報。
