# OPEN-233 Stage 1 recall / rep30 Closeout PM運営Failure RCA(委任_02、2026-10-05)

管理ID: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(PM RCA軸)。費用¥0・read-only(本文書以外を編集していない)。責任追及ではなく再発防止のプロセスRCA。ユーザー§10(8問)・§11(再発防止A〜E)の原文は委任ログ`docs/pm/delegation_log/2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_02.md`。
凡例: 【確認】=記録・コードで直接確認、【推測】=記録からの推測。行番号は2026-10-05時点。

## 1. 事実の時系列

| # | 時点 | 事実 | Evidence |
|---|---|---|---|
| 1 | 委任_09 | runnerに`substitute_baseline_on_stage1_miss`(B2_hormuz・B3のStage 1非検出時、現行Production V0記録へ差替え)が入る。`git log -S`の最古ヒット=5e8ff545(「Phase 1 ⑥ 統合dry-run、recall miss発見」)【確認】 | runner L7686・L8192〜8199。commit名 |
| 2 | Opus#10(委任_68前) | 「支配的なリスクはStage 2ではなくStage 1のrecall」「S1で『Safetyは解決』と報告してはならない」。論点8で「Safety KPIを代替投入ありの条件付き値と代替なしの通し値に分けて報告」「S1とは別の管理事項として明示的に残す」を要求【確認】 | `opus_l2_review_open233_self_recovery_10.md` L22・L45・L104〜109 |
| 3 | 委任_68 Fable採否 | #10の3修正を採用、うち(iii)=KPI分離報告。Stage 1 recall欠落は「S1と別の管理事項」。ユーザー判断候補に(2)「Stage 1 recall別管理」・(7)「Stage 1 recall対策の方向」を列挙【確認】 | `DECISION_LOG.md` L18498〜18513、設計書`design_open233_stage2_safety_downgrade_01.md` L207〜216 |
| 4 | KPI-RECOVERY-02(10-04) | ユーザー指示「必須作業6: Stage 1 Checker見逃しは第二段階」「まず(後段を)直す。その後Stage 1を別途改善」【確認】 | `DECISION_LOG.md` L18637〜18640 |
| 5 | KPI-RECOVERY-02 Fable評価・委任_03 | 「採用: Stage 1 recallは第二段階」「本委任では着手しない(Step 6の結果で未検出があれば次ループ)」。¥0評価手順は設計書§9-6に記載のみ【確認】 | `DECISION_LOG.md` L19062・L19076、`design_open233_kpi_recovery_02.md` L227〜231・L268、委任ログ_03 L19 |
| 6 | rep30(委任_12) | 重大見逃し0(旧・新・text_pattern)。38 run中、Stage 1 fresh 3 call(4 run)・frozen 31・V0差替え3【確認、provenance文書は事後作成】 | REPORT §62 L4458〜4466、`rep30_stage1_provenance_01.md` §3 |
| 7 | Closeout(委任_01c) | Trial `VALIDATED`・Production採用。最終数値に差替え/frozenの記載なし。未解決3件にStage 1 recallなし。「未処理USER_DECISION: なし」【確認】 | REPORT §63 L4481・L4495〜4496 |
| 8 | 採用後(委任_04c〜) | Gap棚卸しでrep30のStage 1が主にfrozen+V0差替えと判明、CORRECTION-01(委任_06/_07)・02(委任_08/_10): A構成fresh確認FAIL【確認】 | `rep30_stage1_provenance_01.md`、commit b5371bd0・1f50655d・bd22696b・a03a186d |

## 2. §10の8問への回答

### 問1 なぜrep30 Closeoutでblocking issueにならなかったか
- 事実: Opus#10の警告は「S1とは別管理」とされ、評価対象(rep30のKPI Gate)の合格条件に変換されなかった。Gate条件はHuman Review 0・重大見逃し0・費用基準で、Stage 1 recallを測る項目が無い【確認: REPORT §62 L4458〜4460】。
- 判断の所在: Opus(警告)→Fable(L18504「別管理」)→ユーザー(第二段階、L18637)。blocking化を検討・却下した記録は無い(明示判断なし)。
- 補足: Fableの採否はOpus警告を「ユーザー判断候補(7)」へ回したのみで、blockingか否かの分類語を持たなかった【確認】。

### 問2 「条件付き/代替なし」分離は実際どう処理されたか
- 事実: 採否で(iii)採用(L18499)。しかしrep30集計は2値分離を作らず、per-rowに`stage1_recall_miss_substituted`を残しただけ(`summary_kpi_01.json` L31〜318の8行、うち2行true=B3 s1/s2)。fresh/frozenの区分キー(`stage1_mode`)は出力に無い【確認】。
- 結論: 採用した方針が「報告フォーマット」へ落ちず、データ列としてだけ存在した。報告§62/§63に「差替え/frozen」語は無い(Grep: 差替えはL4433・L4532のみ、§62/§63外)【確認】。

### 問3 Fableが採用したのに最終KPI報告へ反映されなかった理由
- 事実: 経路記録の指示自体は存在した。KPI-RECOVERY-02の委任_01 L44は記録項目に「Stage 1の経路(fresh/reuse/代替投入)」、委任_04 L62はSafety-critical 6件の検出に「経路(Stage 1 fresh/reuse/代替投入を明記)」を要求【確認】。
- ところがrep30 Closeoutの§62 L4467「Safety-critical 6件: 全て検出」には経路の明記が無い(委任_12の報告で履行されず、Fable照合でも未検出)【確認: REPORT L4467、委任ログ_12/_01cの該当Grep=条件付き/代替投入語の受入条件なし】。
- 要因【推測】: 経路記録が「記録項目」止まりで、Closeoutの合否文言(KPI表記)へ紐づく規則が無く、後続委任文(_08〜_12)が新しいRCA・是正課題へ置換されるたびに受入条件として継承されなかった。履行確認の主体が不在。

### 問4 どこで管理され、どこで脱落したか
- OPEN_ITEMS: 独立行が無く、OPEN-233の巨大1行(L662)の「次Action」履歴に「Stage 1 recall別管理」があるのみ【確認: Grepで662行のみヒット】。
- ACTIVE_TASK: 一時ファイル。現行版の言及はCORRECTION-02の1行のみ【確認】。当時版の有無はgit履歴未調査【未確認】。
- KPI Gate: 項目なし(問1)。
- 脱落点: (a)独立Open Item化されなかった (b)Closeout時の「未解決」「UDR残」の棚卸しがOPEN_ITEMSの行頭ID単位で、行内の履歴語を拾わない(`open233_closeout_check_2026-10-04.md` §1はOPEN-233行の行頭IDのみ確認)【確認】。

### 問5 誰がnon-blocking / deferredと判断したか
- 全件Grep結果(DECISION_LOG・OPEN_ITEMS・REPORT・設計書・委任ログ2026-10-02〜05、`Stage 1.{0,40}(non-blocking|deferred|後回し|着手しない|次ループ|別管理|範囲外)`): ヒットは「別管理」(DECISION_LOG L18513、設計書L216、OPEN_ITEMS L662、REPORT L4278、委任ログ_68)と「着手しない」(DECISION_LOG L19076、設計書L268、委任ログ_03 L19)と、ユーザー今回指示(L19565)のみ。**Stage 1 recallを「non-blocking」「deferred」「後回し」とした記録は0件**【確認】。
- 実在する明示判断は3つ: (1)ユーザー「第二段階」=順序指定(L18637、blockingでないとは言っていない) (2)Fable「本委任では着手しない」=その委任範囲のみ。再開条件は「Step 6で未検出があれば次ループ」 (3)Opus「別管理」=設計レビュー範囲の分離。
- 自然消滅の経路【推測を含む】: 再開条件(2)は「後段で未検出が出たら」だが、Stage 1の取りこぼしは後段から見えない(差替え/frozenで検出済み扱いになる)ため、条件が構造的に発火しない。かつCloseoutのUDR棚卸し(§63 L4496「なし」)は未解決項目の一覧にStage 1を持たなかった。ある文書の更新で消されたのではなく、**どの文書にも「Open Item」として載らないまま、Closeoutの一覧が作られた**(OPEN_ITEMS独立行なし=問4)。

### 問6 なぜ「重大見逃し0」で条件付き評価と検出できなかったか
- 集計スクリプト`er052_open233_self_recovery_flow_runner_01_rep30_agg_01.py`: `Stage 1|代替投入|frozen|reuse|residual_at_pass|substitut`のGrep=2行(いずれもS1第2意見の判定、L63・L65)。fresh/frozen/差替えの区分・集計は**含まれない**【確認】。per-row値は`summary_kpi_01.json`にあるが分母・分子には使われない。
- `residual_at_pass`は「PASS時に本文に残った重大」の指標。Stage 1が非検出のclaimはStage 2/Rewriteに入らず、残存を測る対象にならない。B3は差替えにより検出済みとして数えられる(REPORT L4328)。`rep30_stage1_provenance_01.md` §4: A2A3 HF-009は「rep30でも非検出」だが、KPIの分母はSafety-critical登録分のため0の外にあった【推測: 分母定義は未再確認】。
- 結論: 指標の定義が「Stage 1通過後の残存」で、Stage 1自体の評価が分母から外れていた。条件付き値であることを機械的に検出する経路(provenance列の集計)が無かった。

### 問7 Production初回pathを通したかをなぜ確認できなかったか
- `PM_GOVERNANCE.md` 3節 Closeout Mandatory Check(L473〜540、項目1〜26)を確認: 「KPI provenance」「Production初回path通過」に当たる項目は**無い**。`provenance`のGrepは0件【確認】。近い項目は4(`PRODUCTION_WIRED`宣言条件)・5(initial/retry/fallback整合)・6(runtime evidence)で、いずれも「配線後の経路」か「Evidenceの有無」を問い、測定入力の出所は問わない【確認】。
- `open233_closeout_check_2026-10-04.md`の8項目も、Production側コードの有無(`git grep er052_open233`=0件)の確認で、「Trialが測った入力がProduction初回pathの出力か」は対象外【確認: 同ファイル L35】。
- Gate 1(2節 L166〜168)は`VALIDATED`≠採用としか定めず、`VALIDATED`の根拠が「何で測った値か」の表記を要求しない【確認】。用語面では、`VALIDATED`が「条件付きで仕様通り」と「E2Eで達成」を区別しない(後述§3)。
- 補足: reuse/frozenはコスト・再現性のため意図的に導入された(委任ログ・REPORT参照)。導入自体は問題ではなく、Closeout表記で条件付きと明示しなかったことが問題。

### 問8 Opus警告を「レビュー済み」で終わらせずCloseoutまで追跡する仕組みがなぜ働かなかったか
- 11-3(L1973〜)はOpusレビューの発火条件・観点・「Fableが照合して次工程へ」を定めるが、指摘単位の台帳(指摘→採否→実装→検証→Closeout確認)の規定は無い【確認: 11-3冒頭〜L1992を読み、Grep `Opus指摘|指摘.{0,10}追跡|トレーサ|警告.{0,10}追跡`=0件。11-3の後半[L1993以降]は条件B〜D・STOP条件の細部で、指摘台帳規定の有無は全文未精読=一部未確認】。
- Closeoutの§63 L4486〜4493は「Opus#8〜#14の指摘と対応」を**Closeout時に事後的に1行ずつ**作成した表で、#10行(L4489)は3修正の採否のみ。「Stage 1 recall支配的リスク」と「KPI分離」の履行状況の欄が無い【確認】。
- Closeout Mandatory Checkの項目3(正式採用項目の追跡)は「正式採用された項目」が対象で、Opusの未採用/別管理警告は対象外。項目20(UDR・VALIDATED・APPROVED・未報告・未登録Open Item)は「登録済み」を前提にするため、未登録のものは構造的に拾えない【確認】。
- 結論: 追跡は「採否の記録」で完結し、「Closeoutでの再確認」を行う仕組みと担当が無かった。

## 3. 根本原因(プロセス)の分類

| 区分 | 寄与因子 | 対応する問 |
|---|---|---|
| 仕組みの欠落 | (1) Opus警告の指摘単位台帳が無い(採否で完結)。(2) Closeout Mandatory Checkに「測定入力の出所」「Production初回path通過」が無い。(3) 未解決Safety項目が独立Open Itemにならない構造(巨大1行・行頭ID単位の棚卸し)。(4) 再開条件が構造的に発火しない設計(後段の未検出=Stage 1非検出は後段から見えない) | 1,4,7,8 |
| 判断の省略 | (5) Fableの採否が「ユーザー判断候補」止まりで、blocking/非blockingの分類を付けなかった。(6) Closeout時に「第二段階」「別管理」「着手しない」を、未解決一覧へ移す照合を行わなかった。(7) 事後作成した§63のOpus対応表が採否のみで履行状況を問わなかった | 1,3,5,8 |
| 用語の曖昧さ | (8) `VALIDATED`が「合格基準を満たした」と「E2Eで達成した」を区別しない。(9)「重大見逃し0」が「Stage 1通過後の残存0」を指すのに、読み手には「Fact見逃し0」と読める。(10)「別管理」「第二段階」がdeferと別語で、`PM_GOVERNANCE.md` 5節(明示defer成立条件)・項目9(無断defer)の語彙に引っかからない | 5,6 |
| 報告フォーマットの欠落 | (11) KPI表記にprovenance(fresh/frozen/差替え)欄が無い。(12) 最終数値に「条件」「分母」の併記が無い。(13) ユーザー向け報告(9節)が、決定材料となる数値の測定条件を必須としない | 2,3,6 |
| 委任文テンプレートの欠落 | (14)「経路を明記」指示(KPI-RECOVERY-02 委任_01・_04)が、後続委任の受入条件として継承される定型が無い。(15) Closeout委任(_01c)の確認項目が`open233_closeout_check`の8項目固定で、KPI測定条件の確認が入らない | 2,3,7 |

要点: 個々の人・モデルの見落としではなく、「測定条件を数値とセットで運ぶ」「警告を台帳で運ぶ」「未解決Safetyを独立登録する」の3経路が、Closeoutの確認項目と報告書式の双方に存在しなかった。

## 4. 再発防止のPM_GOVERNANCE反映案(案文のみ。本委任ではPM_GOVERNANCEを編集していない)

既存構造(Grep `^## `): 1責任分担/2 Gate1〜7/3 Closeout Mandatory Check(項目1〜26)/5 defer成立条件/6 安全≠成功/9 ユーザー向け報告/11 Fable↔Sonnet往復(11-3 Opus独立Gate、11-4 改善ループ)/20 Open Item区分/21 Existing Spec Check/22 ユーザー指示優先/23 上位目的レビュー/変更履歴。
配置案: A・B・D・F=新設**24節**「KPI provenance・E2E表記・Closeout自己確認」、C=新設**11-5**、E=**5節拡張**+20節追記、Closeout Check=**項目27〜30**追加。重複回避のため、各案は既存条文の参照を主とし再掲しない。

### 案A KPI provenance(24-1)
- 条文案: 「Trial/Closeout/Production採用提案で報告するKPI・合否数値は、数値ごとに測定経路を次の6区分から1つ以上明記する: `fresh`(当該構成を新規API実行) / `frozen`(過去出力の読み込み) / `reuse`(同一run内・run間キャッシュ) / `manual_substitution`(差替え・手動投入・fixture置換) / `synthetic`(合成fixture) / `production_formal_path`(正式量産経路を通過)。複数区分が混在する場合は件数内訳(例: fresh 4 / frozen 31 / manual_substitution 3)を併記する。」
- 適用範囲: KPI・Gate判定・Production採用判断の根拠となる数値すべて。探索的な内部診断は対象外。
- 追加項目: 委任文テンプレートに「KPI provenance欄(必須)」、RESULT_PACKET/REPORTのKPI表に「経路」列、集計スクリプトにrun単位の`provenance`キー出力(runnerの`stage1_mode`等を機械的に出す)。
- 整合: 既存に測定経路を問う規則は無い(Grep `provenance`=0件)ため新設。9節(ユーザー向け報告)・15節(コスト報告)の報告書式へ列追加する形で、書式の重複定義を避ける(15節は本委任で未精読=整合は要Fable確認)。

### 案B 条件付きKPIとE2E KPIの分離(24-2)
- 条文案: 「測定に`frozen`・`manual_substitution`・`synthetic`が1件でも含まれるKPIは『E2E Safety KPI』『E2E達成』と呼ばない。『条件付きKPI(条件: ○○)』と呼び、条件を値の隣に書く。E2E KPIは、同一Gate基準を満たす入力のみ(`fresh`かつ`production_formal_path`)で別途算出し、両値を併記する。E2E値が未測定なら『E2E未測定』と明記する。」
- 追加項目: Closeout報告の表題・結論文、`DECISION_LOG`のStatus文、ユーザー向け報告(9節)で同ルールを適用。
- 整合: 6節(安全≠成功)は品質の観点、本案は測定条件の観点で独立。

### 案C Opus指摘トレーサビリティ(新設11-5)
- 条文案: 「重要なOpus警告(BLOCKER/MAJOR/Safety警告、および『支配的リスク』『報告してはならない』等の制約表現を含む指摘)は、指摘単位の台帳行を作り、状態を `RAISED → ADOPTED/REJECTED/MANAGED_SEPARATELY → IMPLEMENTED/REFLECTED_IN_TRIAL → VERIFIED(Evidence path) → CLOSEOUT_CONFIRMED` で追跡する。`ADOPTED`は実装・報告書式への反映先を、`REJECTED`は理由とFable判断を、`MANAGED_SEPARATELY`は独立Open ID(案E)を必須とする。未解決のBLOCKER/MAJOR/Safety警告(`VERIFIED`未達かつ`REJECTED`理由なし)が残る状態のCloseout・Production採用提案を禁止し、STOPして`USER_DECISION_REQUIRED`とする。」
- 配置: 台帳は新規ファイルを作らず、各`opus_l2_review_*`ごとの末尾「追跡表」+REPORTのOpus対応節に同一表を置く案(新ファイルの要否はFable判断)。
- 追加項目: 委任文テンプレートに「関連Opus指摘ID・本委任での状態遷移」、Closeout Check項目27。
- 整合: 11-3は発火条件・観点・採否後の進行を定める。11-5は「採否後の追跡」を追加するのみ。Opusレビュー自体をユーザーGateにしない方針(CLAUDE.md・11-3)は維持。11-4(改善ループ回数上限)とは別カウント。Gate 1・項目3(正式採用項目の追跡)の対象外領域(未採用・別管理の警告)を補う。

### 案D Closeout自己確認(24-3)
- 条文案: 「Trial終了時(Gate 1)に、KPIごとに次を明示してYes/Noで判定する: 『このKPIはfresh・Production初回pathを含むE2E値か』。判定欄には根拠として案Aの経路内訳を書く。Noの場合、『E2E達成』『Production級の検証済み』と表記しない(条件付きと表記、案B)。Production採用提案には、Noのまま提出する場合に『何が未検証か』の1行を必須とする。」
- 追加項目: Closeout Mandatory Check項目28。委任文(Closeout委任)の固定ブロックへ「KPI E2E自己確認」欄を追加。
- 整合: 項目4(`PRODUCTION_WIRED`宣言条件)は配線後、本案はTrial終了時の測定条件を問う別時点。項目5・6と目的が近いが、問う対象(入力の出所)が異なるため重複しない。

### 案E Open Item消失防止(5節拡張+20節追記)
- 既存規則の確認: 5節は「deferはユーザーの明示承認のみ」「記録が無いdeferは無断defer=項目9抵触」と既に定める。今回の事故は、Stage 1 recallが「別管理」「第二段階」「本委任では着手しない」という**defer以外の語**で扱われ、5節・項目9の対象語彙に入らなかった点にある(問5)。
- 条文案(5節末尾へ追記): 「『別管理』『第二段階』『着手しない』『範囲外』『次ループ』『後回し』は、Safety・Fact・Production採用判断に関わる未解決項目に用いた場合、deferと同等に扱う。これらの語を使うとき、(1)独立したOpen ID(`OPEN_ITEMS.md`に独立行、巨大行内の履歴記載は不可)、(2)再開条件(観測可能・発火可能であること。後段から観測できない事象を条件にしない)、(3)ユーザーの明示承認(『第二段階』等の順序指定は、blocking/non-blockingの別をユーザーが明示した記録がある場合に限り『承認済み』とする)を必須とする。ユーザー合意なく`non-blocking`/`deferred`/`UDR-deferred`にしない。」
- 20節追記: Safety未解決項目は区分に加え`safety_unresolved: Y/N`を持たせ、Closeout時の棚卸しは行頭ID単位+本語彙のGrep(上記語)の両方で行う。
- 追加項目: Closeout Mandatory Check項目9を拡張(「無断deferが無い」→「defer同等語(上記)の使用箇所が全て5節の3条件を満たす」)、項目29として「Safety未解決項目の独立Open ID有無」。
- 整合: 項目20(e)「未登録のOpen Item」と目的が重なる。本案は(e)の前段として「登録を要する語彙・条件」を定義し、重複でなく具体化する(統合要否はFable判断)。

### 案F 条件付き`VALIDATED`をProduction採用判断の材料にする際の表記(24-4)
- 背景: 2026-10-05の採用決定の入力(REPORT §63 L4481)は、rep30の条件付き値(frozen 31+差替え3+fresh 3 call/4 run、【確認】`rep30_stage1_provenance_01.md` §3)だったが、その条件が決定材料に載らなかった。Gate 1は`VALIDATED`≠採用と定めるが、`VALIDATED`の根拠の種類は問わない。
- 条文案: 「Production採用提案(Gate 2)には、`VALIDATED`の根拠KPIについて(1)案Aの経路内訳、(2)案Dの自己確認結果、(3)E2E未測定部分のリスク(何が未検証で、採用すると何が起こり得るか)を、ユーザー向け報告冒頭に必ず記載する。Noを含む場合、Status表記は`VALIDATED(条件付き: <条件>)`とし、`VALIDATED`単独表記を禁じる。ユーザー承認の記録(Gate 2、原文転記)にも同じ条件を残し、承認がどの条件下の数値を根拠にしたかを後から確認できるようにする。」
- 追加項目: Closeout Mandatory Check項目30(採用提案に上記3点があること)。用語整合: 既存の`VALIDATED`定義(Gate 1)は変更せず、修飾子の追加のみ(既存Status語彙の破壊的変更を避ける)。

### Closeout Mandatory Check追加項目案(3節、項目27〜30)
27. 重要Opus警告が全て`CLOSEOUT_CONFIRMED`または`REJECTED(理由あり)`か(案C)
28. 各KPIにE2E自己確認(Yes/No)と経路内訳があるか(案A・D)
29. Safety未解決項目が独立Open ID・再開条件・ユーザー承認つきか(案E)
30. 採用提案の`VALIDATED`に条件修飾と未検証リスクが付いているか(案F)

## 5. Fable評価用チェックリスト

1. 追加先: 24節新設+11-5新設+5節拡張の3箇所分散で良いか。既存節(2節 Gate 1)へ集約する方が参照しやすいか。
2. 案A: 6区分の定義は十分か(`reuse`と`frozen`の境界、`fresh-cache`の扱い、`production_formal_path`と`fresh`の同時指定)。探索診断を除外する線引きは明確か。
3. 案B: 「1件でも含まれればE2Eと呼ばない」は厳しすぎないか(例: 単体のfixture再生が1件だけの場合)。ユーザー文言どおり採用か、修正するか。
4. 案C: 台帳の置き場(新規ファイル禁止との整合)。「重要警告」の機械的判定基準(語彙・重大度)をどう固定するか。11-3のSTOP条件との重複。
5. 案D: Yes/No判定の責任者(Fable/Sonnet)。Noのまま採用提案を許す条件の有無(ユーザーが承知の上なら可、とするか)。
6. 案E: defer同等語の範囲(広すぎて通常運用を止めないか)。「第二段階」というユーザー自身の順序指示を、どこまで承認済みdeferと見なすか(今回はblocking/non-blockingの別が未確認)。項目20(e)との統合要否。
7. 案F: `VALIDATED(条件付き)`という修飾子方式で良いか、新Status(例: `VALIDATED_CONDITIONAL`)を設けるか。既存Status体系への影響。
8. 遡及適用: 今回のrep30/Closeout(§63)へ案A〜Fを遡及適用し、`VALIDATED`の再表記(条件付き)をSSOTへ反映するか(別委任・ユーザー判断事項)。
9. 実装コスト: runnerの`provenance`キー出力、委任文テンプレート、`check_delegation_prompt.py`の必須キーワード追加(`KPI provenance`等)の要否と範囲。
10. 本委任の範囲外で発見した懸念: `check_delegation_prompt.py`の必須語(`事前指定Grep一覧`・`SSOT追記先`)が委任文に無いとFAILになる(本委任のT-0もFAIL、委任文は逐語保存のため未修正)。

## 6. 確認/推測の区別と範囲外Read

- 確認: 本文の【確認】付き記述(指定ファイル・Grep結果・行番号)。
- 推測: 問3の要因・問5の自然消滅の経路・問6の分母定義の一部。【推測】と明記。
- 未確認: ACTIVE_TASKの当時版(git履歴未調査)、11-3後半の全文、15節との整合、委任ログ_12/_01cの全文(Grepのみ)。
- 事前指定一覧外のRead: `PM_GOVERNANCE.md` 5節(L564〜576)・20節(L2800〜2837)・11-4(L2165〜2174)、`rep30_stage1_provenance_01.md`(全文)、`design_open233_kpi_recovery_02.md` L17〜20・L225〜232、`er052_output/open233_self_recovery_flow_runner_01_rep30/summary_kpi_01.json`(Grepのみ)、rep30/rep29の集計スクリプト(Grepのみ)。いずれもread-only。
