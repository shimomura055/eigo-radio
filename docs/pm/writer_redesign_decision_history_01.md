# Writer仕様変更判断の経緯整理(FACTLOCK-ASTRA-E2E-TRIAL-01 付随調査 委任_18、2026-10-09、API支出¥0・read-only調査)

注意: 本書は決定ではなく、一次資料(SSOT・REPORT・delegation_log・docs/pm)から経緯を事実ベースで並べたもの。【確認】=該当ファイル・行で文言/数値を確認、【推測】=資料から読み取った解釈(根拠付き)。推測で数字・日付は書いていない。Rollback誤読の個別件数の再集計は行っていない(必要なら委任_17参照)。Production変更・SSOT編集なし。略称: DL=`DECISION_LOG.md`、REPORT=`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`。

## §1 結論(要約)

1. 【確認】「Writer由来の事実NG」を、SSOTが数値付きで最初に述べたのは、2026-10-07のOpus独立レビュー(「誤りが生まれる場所は全出所でWriter初稿(R0)が初出の過半、R2初出は0〜22%」)と、それを裏取りした既知NG140件の再分類(NG92件のR0初出66%、R2初出20%、EN初出13%)。Writer起因という見方は、10-07夜の時点で資料上すでにある。
2. 【確認】同じ10-07に、Writerを変えない選択肢が先に採られている。ユーザー決定1=(A)「Writerは単一パス自由生成のまま」(DL L20220付近)、翌朝の夜間ループ統合報告でもFableの推奨は(b)軽微許容+(c)台帳多義語正規化で、Writer側は「面白さリスク未測定」と書かれていた(`docs/pm/handoff/2026-10-08_night_loop_morning_report.md` L35)。
3. 【確認】10-07までにWriter以外の対策(Note/多義語注意、台帳明確化P'、B3 brief構造、precheck修正、Checker新仕様)が多数試され、結果は「Rollback誤読の予防は有効(0/22)だが軽微NGは残る」「B3 brief構造は差なし(NOT_SUPPORTED)」「Note介入は判定不能」「Checker側は夜間の範囲で頭打ち」。B3 TrialのFable判定は「残る誤読対策はWriter/Checker側で扱う」(REPORT §100-6)。
4. 【確認】Writer根本設計の要否を決める起点は、2026-10-08のユーザー判断(DL L20228、逐語は要旨のみ。逐語全文は`delegation_log/2026-10-08_ALL-6-LUNA-..._01.md` L21)。「現状の品質問題(Writer由来の事実NG)で全てが止まっているため時間優先」「決めたいのは『Writerの根本設計(Fact Lock等)をする必要があるか』」「6.0で改善するなら根本設計は不要」。この文言の前半「Writer由来の事実NG」はユーザーの認識として記録されており、その根拠となった個別Trial・件数の記録は、この判断エントリには付いていない。
5. 【確認】ALL-6-LUNA Trial(全工程6-luna、48本)の結果は、重大が改善せず(JA R2 重大0→1、EN 1→1)、軽微は微減(JA 10→7、EN 14→12)、評価者差が群間差より大きい、というもの。Fableの記録は「根本設計要否判断はユーザー」(DL L20231)。直後の10:12にユーザー判断7で全工程6-luna化(Production方針)が確定し、配線された(PRODUCTION_WIRED)。
6. 【確認】FACTLOCK-WRITER-REDESIGN-TRIAL-01は、ALL-6 Trialと並行して設計され(委任_01は「並行タスク」と明記)、ユーザー方針は「面白さはRevise1,2で確保、Factは従来どおりB3で絞る、数値・細かい情報はWrite時に規制、それ以外はWriter時点で嘘をかかないよう固める(貴殿idea基準)」。決定A(Writer不変)の「例外Trial」と位置付けられた(DESIGN_01 §0)。
7. 【確認】Fact Lock v1の事実指標は良化(軽微/記事 JA R2 0.55→0.21、EN 0.81→0.32、重大はFact Lockで0/0)したが、面白さpairwiseは9対35でNG(ユーザーが「全くNG」)。そこからsweep、ChatGPT再現(Step 1)、Astra Revise(R1→R2)へと、Writer側(R0/R1/R2とモデル)の再設計が連鎖した。ここで「事実を固めるR0 + 面白さを作るAstra Revise」という新Writer仕様(series X、R2止め)が形になった。
8. 【確認】新Writer仕様の10-09 E2E(FACTLOCK-ASTRA-E2E-TRIAL-01、n=9)のFable最終判定は「同等・混在。事実安全の良化は示されなかった(測定力不足を含む)。面白さは未測定。費用は約6倍」(REPORT §111)。Production採用は未宣言・未承認。
9. 【確認】「brief条件(P2 Note全転記)がNGを増やした」という知見は、10-07のRCAとB3 Trialで、(a)「前回NG多発は測定手順の差が最大」(H-A)、(b)「Note介入の実差は判定不能」(H-B)、(c)「B3 brief構造は重大・軽微に差なし」と整理されている。Writer原因説を否定した記録も、brief原因説で置き換えた記録もない。両方の仮説が併存したまま、判断はユーザーに委ねられている。
10. 【推測】ユーザーの「Writer変更が必要という認識を共有していた」と、資料上のFableの10-08朝時点の推奨(Writer以外を基本)は、10-08朝のユーザー判断(判断1〜6への回答)の記録が見つからないため、どこで一致したかを資料からは確定できない(§5)。

## §2 時系列表

| 日付 | 管理ID | 出来事/結果(Status・主要数値) | 誰の判断か | 出典 |
|---|---|---|---|---|
| 2026-10-06 | OPEN-233-LEDGER-CLARITY-DESIGN-01 / P-TRIAL-01 | 台帳明確化(P'方式)の設計→Trial。HC-012 Rollback型はAfter全段で復元型0(Before 5 runで3/5)、真の重大NG0、ただし断定強化1件+保留2。Status=USER_DECISION_REQUIRED(VALIDATEDでもREJECTEDでもない) | Fable判定、Opus条件A | DL L20102〜L20118、REPORT §87-§88 |
| 2026-10-06 | OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 / TRIAL-02/03 | 多義語Note設計。案N+B(B3 promptへ転記規則)は「Production Writer仕様変更=新Product判断」でSTOP条件該当と明記。自動Note生成は3ループで成立せず | Fable判定、Opus条件A | DL L20119〜L20146 |
| 2026-10-07 | META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02、ALLFACT-NOTE-ENT-01、E2E-02、NOTE-TRANSFER-MATRIX-01 | Note系Trial。Meta N=12で重大誤読0・曖昧9。P2(全fact Note)E2E N=10で重大3(OPEN-238/239起票)。MATRIX 36本で重大1、前回P2の多発は不再現(仮説: brief生成条件が主因、未検証) | Fable判定(USER_DECISION_REQUIRED) | DL L20147〜L20184 |
| 2026-10-07 | E2E-STAGEWISE-NG-AUDIT-01 | 従来5+P2 10=15本の工程別再評価。重大全6件(84件中、軽微78)、⑤b 重大: 従来0/P2 4。1記事⑤b 従来4.2/P2 6.1 | Fable | DL L20173〜L20179、`docs/pm/ng_root_cause_01/ng_origin_by_stage.md` L5 |
| 2026-10-07 | OPEN-233-B3-BRIEF-STRUCTURE-HYPOTHESIS-01 | ¥0の仮説書(未commit)。重大6件を「Writer起因」と分類し、うち5/6がbrief段階の主体・対象欠落または連結(a/c)と対応づけ。「仮説であり結論ではない」(N小) | Sonnet(委任_01)、判定は既存台帳に従う | `docs/pm/b3_brief_structure_hypothesis_01.md` L1-L3、L33-L43 |
| 2026-10-07 | OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01 / PRODUCTION-WIRING-01 | precheckの分数語偽陽性。案1をProduction採用(APPROVED_FOR_PRODUCTION)→PRODUCTION_WIRED。Rewrite由来の重大1件はこれが原因 | ユーザー決定+Fable判定 | DL L20185〜L20200 |
| 2026-10-07 | OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 | B3 brief構造Trial(V0〜V6)。Fable判定=**NOT_SUPPORTED**(H1〜H3支持されず)。55記事で重大0(床効果)、軽微0.4〜0.8/記事で評価者差と同程度。逆方向対照V6が悪化せず操作確認も不成立。「残る誤読対策はWriter/Checker側で扱う」 | Fable判定、ユーザー決定: 段階2再開YES(4並列) | DL L20201〜L20206、REPORT §100-6(L5514) |
| 2026-10-07 | OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 | RCA。同一15記事の元評価/再採点=約7.5倍(測定手順一式の差が最大の説明)。R0初出が過半、R2初出0〜22%(H-D「重大の増幅段階として示唆」、判定=部分支持)。Rewrite由来2/84(2.4%)。Note介入H-Bは判定不能。「前回が過大だった」とは結論しない | Fable判定(Opus任意レビューM1〜M4反映) | DL L20208〜L20212、REPORT §101、`docs/pm/ng_root_cause_01/root_cause_draft.md` §4(L45)、§9(L73) |
| 2026-10-07 | OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 | 本番経路Trial。事前登録判定=**CONDITIONAL**。Rollback誤読0/10(累積0/22)、重大あり記事1/18。重大1件は「Writer初稿由来の否定・不在型をCheckerが検知しながらStage2が格下げして見逃し」、別にChecker RewriteがタイトルTを置換して新規誤りを作成。Note系Trial群はSUPERSEDED/DEFERRED。次方向はユーザー判断待ち | ユーザー人間判定(jb9k重大、qvqcタイトル軽微)+Fable判定(a)〜(f) | DL L20213〜L20217、REPORT §102-6(L5601) |
| 2026-10-07 | OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_A、22:01 commit) | Opus独立レビュー(L2)の結論: 2段Writer・全文関係diffは非推奨。「Writerは単一パスの自由生成のまま」「Writerへの禁止事項追記は効果未証明」「誤りが生まれる場所は全出所でWriter初稿(R0)が初出の過半」。**ユーザー決定1=(A)** この経路採用(Fable当初案=2段Writerは撤回)。ユーザー決定2=段階0承認、約8時間不在、予算¥1000でFable主体の夜間自律ループ | ユーザー(決定1・2)、Opus(所見)、Fable(撤回) | DL L20219〜L20224、`docs/pm/opus_l2_review_stabilization_strategy_01.md` L7・L10・L13 |
| 2026-10-07〜08夜 | 同上 夜間ループ | 既知NG140件再分類: NG92のR0初出61(66%)/R2初出18(20%)/EN12(13%)/Rewrite1。Opus所見「R0初出が過半、R2は0〜22%」と同方向。①v3(構造要素Rewrite規則)は限定付き有効(21試行、違反0、STOP 7→1)。②Stage2 rubric追記は打ち止め。反転型検出・関係抽出中核化は不成立。狭い対判定は8/21でr3(11/21)を下回る。夜間実費約¥248/¥1000 | Fable主体の自律ループ+Opus総括レビュー4回 | `er052_output/open233_stage0_01/reclass/RECLASS.md` L28・L61、`docs/pm/handoff/2026-10-08_night_loop_morning_report.md` L10〜L20、`docs/pm/opus_l2_review_night_loop_summary_01.md` |
| 2026-10-08 朝 | 夜間ループ統合報告(06:52 commit)・ユーザー判断1〜6提示 | 判断4: 軽微の関係型の方針(a1)Writer最小禁止事項(決定Aに触れる・面白さリスク高)/(a2)Writerモデル・温度(決定Aに触れない・盲検読み比べ必須)/(b)軽微は許容し「重大+人間10%枠」/(c)台帳多義語正規化。**Fable推奨=(b)を基本に(c)を並行**。「根本設計見直しの条件(a)(b)(c)は未該当/判定不能のままで、現行の枠は維持」。Opus総括の順序は「(6)(a)選択時のみWriter Trial」 | Fable(推奨)、Opus(総括) | `docs/pm/handoff/2026-10-08_night_loop_morning_report.md` L35・L42、`docs/pm/opus_l2_review_night_loop_summary_01.md` L21 |
| 2026-10-08 | ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01 委任_01(08:05 harness commit) | **ユーザー判断(要旨)**: 現状の品質問題(Writer由来の事実NG)で全てが止まっているため時間優先。決めたいのは『Writerの根本設計(Fact Lock等)をする必要があるか』。gpt-5.6-luna工程(Checker含む)をgpt-6-lunaへTrial的に切替え、NG率・重大見逃しの改善代を数値化。6.0で改善するなら根本設計は不要。しきい値なし、予算¥500。逐語: 「決めたいのは根本設計(Wrtier)をする必要があるか。6.0で改善するならやる必要がない。」「今は時間優先」。背景: CURRENT_SPEC『Writerは不変(Opus#15 K7)』はユーザー決定ではなくOpus提案由来の設計制約 | **ユーザー** | DL L20226〜L20231、`delegation_log/2026-10-08_ALL-6-LUNA-..._01.md` L21 |
| 2026-10-08 | ALL-6-LUNA... 結果(09:31 commit) | MEASURED。48本(両群完走19/24)。JA R2 重大0対1・軽微10対7、EN 重大1対1・軽微14対12、EN Advanced must-fix 0/19対6/19、費用/本¥9.46対¥4.29。T-B(既知NG再判定n=2): 重大7件の検出 5.6=1/14(7%)対6=4/14(29%)。評価者差が群間差より大きい、重大は全体で2件(床効果)。Status「根本設計要否判断はユーザー」 | Fable(Status判定) | DL L20230〜L20231、REPORT §103(L5621〜L5629) |
| 2026-10-08 | PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 | ユーザー判断7: 全工程6-luna化(Production方針)。10:12記録、PRODUCTION_WIRED確定(受入a〜e)。Writerモデルも6-lunaに切替 | ユーザー(判断7)、Fable(受入判定) | DL L20233〜L20269、OPEN_ITEMS OPEN-241 |
| 2026-10-08 | FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_01〜02b | **ユーザー指示(要旨)**: 「やりたいのは、エンターテイメント性はRevise1,2(場合によっては3以降も)で確保。従来通りFactは絞る(B3)。また数値・細かい情報があると読者読みづらく、かつ、Reviseでも消えないので、そこはWriteするときに規制。それ以外は、上記貴殿ideaベースでWriterのタイミングで嘘をかかないように固める。」数値規則「CでOK。それ以外も貴殿提案ベースでよい」。**決定A(Writer単一パス自由生成・prompt不変)の例外Trial**(ユーザー指示)。Opus条件A: 修正後に進む(M1〜M9)。「Writer根本設計の要否を判断する材料として足りる」(Opus) | **ユーザー**(方針)、Fable(idea・設計)、Opus(条件A) | `delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_01.md` L18〜L24、`_02a.md` L17、`er052_output/factlock_writer_trial_01/DESIGN_01.md` §0、`docs/pm/opus_l2_review_factlock_writer_trial_01.md` |
| 2026-10-08 | FACTLOCK v1 結果(12:31 commit) | MEASURED。3セル(baseline 5.6現行/all6/factlock)×24本。軽微/記事 JA R2 0.55/0.32/0.21、EN 0.81/0.68/0.32。重大 JA R2 0/1/0、EN 1/1/0。面白さpairwise factlock 13対all6 35(実質9対35)。実費¥173.2/¥150。残NG突合: factlock全NG14項目、照合の検出は狭義1/9(11%)、EN軽微6件の半分は翻訳段由来。Status MEASURED、採用判断ユーザー | Fable | DL L20271〜L20285、REPORT §104(L5631〜L5664) |
| 2026-10-08 | FACTLOCK 委任_03〜05 | ユーザー: 「指摘の通りエンターテイメント性については全くNGです。これでは話になりません。一つはR0>R1>R2のPromptを変更して改善できないか、もう1つはそもそもWriterへのPromptを現状の品質重視をキープしながら、工夫できないか、変更して検討してください」。さらに「AIは禁止、誘導すると上手くいきません…5でも10でもパターンを振って方向性を決める」。さらに「改善はしたものの、軽微・重大が思ったより良くなってませんね。想定通りですか。」 | **ユーザー** | `delegation_log/..._FACTLOCK-WRITER-REDESIGN-TRIAL-01_03.md` L27、`_04a.md` L25、`_05.md` L15 |
| 2026-10-08 | FACTLOCK sweep(11変種×3brief、33本)・R3-MINIMAL・6-sol N=1 | sweep評価=EVALUATED。S0基準で明確に上は0、明確に下はS6のみ、他はノイズ幅内。位置バイアス大(B選択79%)。R3-MINIMAL(N=12): 6-lunaでは最小指示で事実逸脱が増える(fresh JA FC MAJOR 0→6、5本)。6-sol N=1はJA FC MAJOR 0。推奨なし | Fable(Status判定、推奨なし) | DL L20271〜L20285、REPORT §105、§104 |
| 2026-10-08 | FACTLOCK Step 1(ChatGPT再現) | ユーザー: 「Chatgptに『事実は変えずにエンターテイメント性をもっと上げた記事にReviseください』といったら、良くなりました。元の設計(Writerに自由に書かせる)よりもまだ一歩というところですが、だいぶましです。」→Step 1: 構成の組替えはgpt-6-astraのみで起き、luna/solは指示緩和でも変わらない。ユーザー盲検 C(F3_astra)>B(F2_astra)>A(F3_luna) | **ユーザー**(盲検評価)、Fable | `_06.md` L21、DL L20292〜L20299、REPORT §106 |
| 2026-10-08 | ASTRA-REVISE-MATRIX-01/02 | ユーザー確定設計(逐語): 「モデル Astra / ベース Fact Lock R0 / R0>R1>R2>R3 文字数800-1000ソフト / 日本語まで / 各段を人間がチェック+AI判定 / 軽微・重大カウント / META 1記事 / 2系列」。MATRIX-01: FC MAJOR 0/7。ユーザー人間判定: 「Xの方がよく、コストの兼ね合いもあるのでR2が落としどころ」(X=ユーザーPromptのみ)。MATRIX-02(ホルムズ+ミニバッグ): FC MAJOR/MINOR 全10本で0。ホルムズ・ミニバッグも系列X採用(Production採用ではない) | **ユーザー**(設計・判定) | DL L20306〜L20322、`_15.md` L38、`_16.md` L33 |
| 2026-10-08 | OPEN-243-TRANSLATION-NG-ANALYSIS-01 | 翻訳段NGの解析→Opus所見→ユーザー決定。EV-25はChecker Stage 1(r3)がchanged_actor=trueで検出していたが、再分類(`STAGE1_RECLASSIFY=True`)が除外した。ユーザー: 「1: OK / 2: OK。まずTrial、結果を見てProduction採否判断 / 3: 今回聞く必要なし」(S0監査実施、M1〜M3はTrial経路) | **ユーザー**、Opus | DL L20323〜L20331(OPEN-243項) |
| 2026-10-09 | FACTLOCK-ASTRA-E2E-TRIAL-01 委任_01〜16 | 新Writer仕様(Fact Lock R0[Luna]+Astra R1→R2[系列X])+翻訳段M1/M3 vs 旧仕様、n=9テーマ(旧4+新5)、予算¥1000、旧4テーマ+新6(うち2件ユーザー提案)。Opus条件A(OF-095〜102)、B3注記仕様v2(OF-103〜110)。**Fable最終判定=総合「同等・混在」**: 重大=判定不能(両腕0)、軽微JA/EN=同等、人手介入必要率=同等・混在(0.333対0.333、層別は逆向き)、費用 新約¥43.9対旧約¥7.1/記事。面白さ未測定。次の選択肢(a)〜(e)はユーザー方向判断待ち | ユーザー(設計決定1〜9)、Opus、Fable(最終判定) | DL L20341〜L20400、REPORT §111(L5913〜L5934) |

## §3 Writer以外の対策の試行と結果

| 管理ID | 対策内容 | 結果(Status・数値) | 「Writer変更が必要」への含意 |
|---|---|---|---|
| OPEN-233-LEDGER-CLARITY-P-TRIAL-01(2026-10-06) | 台帳明確化(Researcher/Verification拡張P'): 台帳側で多義・方向を明確化 | USER_DECISION_REQUIRED。HC-012 Rollback型After全段で復元型0(Before 3/5)。実費¥34.85。断定強化1件+保留2。n=1テーマ・1 seed | 【確認】台帳側対策はHC-012型の復元には効いたが、断定強化の別型が残った。軽微NGの全般解決とは言えない |
| OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 / TRIAL-02/03(10-06) | 多義語Note(自動生成)。案N(Researcher側規則)・案N+B(B3 prompt転記規則) | USER_DECISION_REQUIRED。自動Note生成は3ループで成立せず(捕捉最大10/14だが付与率NG、捏造リスク)。案N+Bは「Production Writer仕様変更に当たる」とSTOP条件 | 【確認】Noteを確実に届ける案はWriter(B3)側の変更を要する、と記録されている(DL L20119〜L20130) |
| OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02(10-07) | 最小Note注意喚起(Meta N=5→累積12) | USER_DECISION_REQUIRED。Note brief転記6/6、明示的復活型誤読0、R2は正1〜2/曖昧4〜7/重大誤読0 | 【確認】効果は限定(曖昧が残る) |
| OPEN-233-META-ALLFACT-NOTE-ENT-01 / E2E-02(10-07) | 全fact一律Note(P2) | ENT: P2は多義注意転記0/3。E2E-02(N=10): P2のFact誤りは従来を下回らず(hormuz 8/10 vs 2)、重大3件 | 【確認】P2でNGが増えたという測定は、後のRCAで測定手順差が主因と整理された(下記RCA) |
| OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01(10-07) | 転記形式×多義語注意の6条件(36本) | USER_DECISION_REQUIRED。条件間差が小さくN=2で採否不可。前回P2の多発は不再現(仮説: brief生成条件が主因、未検証) | 【確認】brief条件説は仮説のまま未検証 |
| OPEN-238-PRECHECK-FALSE-POSITIVE-FIX(10-07) | precheck分数語の偽陽性修正(Checker側) | VALIDATED(Trial)→ユーザー決定でAPPROVED_FOR_PRODUCTION→PRODUCTION_WIRED。26 run Regressionで発火2→0 | 【確認】Checker側の欠陥修正は完了したが、これはWriter由来NGの解決ではない(Checkerが作る誤りの除去) |
| OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01(10-07) | B3 brief構造(V1主体・対象保持/V3単一因果/V5未提示明記/V6最大簡潔)×3テーマ | **NOT_SUPPORTED**。55記事で重大0、軽微0.4〜0.8/記事で評価者差と同程度、操作確認も不成立。実費≈¥434.5/¥500。「B3 brief構造の変更はProduction採用候補にしない」 | 【確認】brief側の操作ではNG低減を示せなかった。「残る誤読対策はWriter/Checker側」と明記 |
| OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01(10-07) | 前回NG多発の原因系分析(¥0) | 順位: 測定手順一式の差(7.5倍)>評価範囲(JAのみ残存)>テーマ差>JA R2段階(部分支持)>Rewrite由来(2.4%)>Note介入(判定不能)>Gate STOP除外(不支持)。「V0の重大0はChecker不要の根拠にならない」 | 【確認】Writer原因説・brief原因説のどちらも「証拠不十分」として並存。R0初出が過半という事実のみ、Writer側の関与を示唆 |
| OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(10-07) | 本番経路に固定Note+旧引き継ぎ規則 | **CONDITIONAL**。Rollback誤読0/22、重大あり記事1/18、不要Rewrite率4/8(50%)。Checkerが検知した重大をStage2が格下げ、Checker Rewriteがタイトルを置換して新規誤りを作成 | 【確認】Rollback誤読は予防できるが、「Writer初稿由来」の重大が1/18残り、かつCheckerが自ら新規誤りを作る。両側に課題が残る |
| OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 夜間ループ(10-07〜08) | 構造要素Rewrite規則①v3、Stage2 rubric追記②、反転型検出、関係抽出中核化、狭い対判定 | ①v3: 限定付き有効(21試行、STOP 7→1)。②: 打ち止め(狙った誤判定12件中1件、BLOCKING +237%)。他は不成立。「Checker側は今夜の範囲で頭打ち」 | 【確認】Checker側の改善は頭打ちと報告されたが、Fable推奨はなお(b)+(c)で、Writer側は「面白さリスク未測定」(night report L35)。Writer変更を結論した記録はこの時点にない |
| ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(10-08、モデル切替のみ) | Writer/FC/EN/ほか工程を5.6→6-lunaへ | MEASURED。重大JA 0→1(EN 1→1)、軽微JA 10→7・EN 14→12、評価者差が群間差を超える。T-Bで重大7件の検出 5.6=7%→6=29%(n=2) | 【確認】「6.0で改善するなら根本設計は不要」という条件に対し、重大は改善せず軽微は微減で評価者差が大きい。Fableの記録は「根本設計要否判断はユーザー」。【推測】改善が明確に示されなかったことが、Fact Lock Trialの続行を妨げなかった、と読める(ユーザーの追加指示の記録はALL-6結果後のFact Lock以降に連続している)が、ALL-6結果を受けた明示的な「Writer変更で行く」というユーザー発言は資料に見つからない |
| FACTLOCK-WRITER-REDESIGN-TRIAL-01 v1(Writer側の対策) | Fact Lock(出典タグ・台帳外禁止・数値規則C)+R1/R2事実固定5則 | 軽微JA R2 0.55→0.21、EN 0.81→0.32。重大は0/0(baseline 0/1)。面白さpairwise 9対35でNG | 【確認】事実指標は良化(ただし重大はN極小で判断不能)、面白さは大幅悪化 → さらに再設計(sweep→ChatGPT再現→Astra Revise) |
| FACTLOCK-ASTRA-E2E-TRIAL-01(10-09) | 新Writer仕様(Fact Lock R0+Astra R1→R2)+翻訳M1/M3、n=9 | MEASURED。Fable最終判定「同等・混在」、事実安全の良化は示されなかった、費用約6倍、面白さ未測定 | 【確認】Writer変更の効果は、このE2Eでは事実安全面で「示されなかった」。判断は方向判断待ち |

## §4 Fableの直前報告との整合・矛盾(事実のみ、弁護も断罪もしない)

対象の記述(委任文の引用): 「過去の重大6件は旧Writerの問題というよりP2 brief条件で起きた」「Writer自体の改善ではない」。なお、この2文自体の文書化されたSSOT記録は見つかっていない(§5)。以下は関連する記録との照合。

### 整合する点
1. 【確認】「重大6件」は、E2E_02の15本(従来5+P2 10)に対する工程別再評価で出た84件のうち重大6件(従来0/P2 6)を指す数字と一致する(`ng_origin_by_stage.md` L5「84件(重大6/軽微78)」)。
2. 【確認】`b3_brief_structure_hypothesis_01.md` は重大6件を「Writer起因6件」と分類したうえで、5/6をbrief段階の主体・対象欠落(a)またはStoryline連結(c)と対応づけている(L33〜L43)。「brief条件が絡んだ」という読みはこの文書にある。
3. 【確認】RCAは「Note介入のP2が従来より多い」という元評価の方向を、同じ物差しの再採点では再現しなかった(従来1.40/P2 0.80、P2は従来の0.57倍)と記録している(`root_cause_draft.md` §2)。「P2のせいでNGが増えた」とは言えない、という整合はある。
4. 【確認】Writerを変えたFact Lock v1でもsweepでも、重大は床効果(0〜2件)で、重大件数の差は判断不能と事前登録されている(`opus_l2_review_factlock_writer_trial_01.md` 論点7)。「Writerを変えれば重大が減る」ことは測定されていない。

### 矛盾する点・記録と一致しない点
1. 【確認】brief条件(H1〜H3)を操作したB3 Trialは、Fable判定でNOT_SUPPORTED(重大・軽微とも事前登録ルールで判定できる差なし)。「briefの構造は誤読・創作の主要なレバーではない」(REPORT §100-6、DL L20202)。これは「P2 brief条件で起きた」という説明を裏付けず、むしろ弱める。
2. 【確認】`b3_brief_structure_hypothesis_01.md` は未commit・仮説段階(「仮説であり結論ではない」L2)で、SSOT(DECISION_LOG・REPORT・OPEN_ITEMS)に採否の記録がない。「brief条件で起きた」はSSOT上の確定事実ではない。
3. 【確認】RCAは「重大の出所としてJA R2・R0段階の関与を示唆(部分支持)」「R0初出が過半、R2初出0〜22%」と記録している(`root_cause_draft.md` L45〜L49, L73〜L85)。R0はWriter初稿であり、「旧Writerの問題というより」という言い方とは緊張関係がある。ただしRCAは同時に、H-Aを最大原因とし、Note介入は判定不能としている。
4. 【確認】10-07夜のOpus所見は「誤りが生まれる場所は全出所でWriter初稿(R0)が初出の過半」(`opus_l2_review_stabilization_strategy_01.md` L10)で、既知NG92件の再分類もR0初出66%(RECLASS.md L28)。Writer(R0)が初出の過半という記録と、「Writerの問題というより」は一致しない。ここでの「Writer起因」は工程位置(R0に初出)を指し、「brief条件」はR0への入力条件を指す、と読むことも可能(【推測】)だが、資料自体はこの両者の関係を明示していない。
5. 【確認】ユーザー判断(DL L20228)は「現状の品質問題(Writer由来の事実NG)」を前提に「Writerの根本設計の要否」を問うており、ユーザーの認識として「Writer由来」は記録に残っている。Fableの直前報告「Writer自体の改善ではない」は、この前提・Fact LockをWriter根本設計としたユーザー判断(DL L20271〜L20285)・DESIGN_01 §0(「Writerが台帳から誤った事実を書かないようにする」)と文言上衝突する。
6. 【確認】Fact Lock/Astra ReviseはいずれもWriter(R0/R1/R2)のprompt・モデル変更として定義され、決定A(Writer単一パス自由生成・prompt不変)の「例外Trial」としてユーザーが指示した(DESIGN_01 §0)。Writer変更が「Writer自体の改善ではない」という整理は、この位置付けと一致しない。
7. 【確認】一方で、Writer仕様変更を「必要」と結論した記録(Fableの判定やユーザーの結論)はSSOT上に見つからない。ALL-6結果のStatusは「根本設計要否判断はユーザー」(DL L20231)、E2E最終判定も「同等・混在」で、DL・REPORT・OPEN_ITEMSのいずれにも「Writer仕様変更が必要」という結論は記録されていない。ユーザーの「同じ認識で進めていたはず」の根拠となる合意の記録は、SSOTからは確認できない(§5)。
8. 【確認】10-08朝のFableの推奨は「(b)軽微は許容し重大+人間10%枠、(c)台帳多義語正規化を並行」で、Writer最小禁止事項は「決定Aに触れる・面白さリスク高」と評価されている(night report L35)。Writerを変えないと解決しないという推奨は、この時点のFable記録にはない。ユーザーが「同じ認識」と受け取る根拠となった会話(チャット)は、SSOT化されていない可能性がある(§5)。

## §5 未確認・データ欠落

1. 【確認】ユーザーの「Writerの仕様を変更しないと、今の品質問題の解決は難しい、というのは貴殿とも同じ認識で進めていた」の根拠となるFableの発言は、SSOT・delegation_log・docs/pmのGrepで見つからなかった(「Writer由来」「根本設計」「Writer起因」「Writerの仕様」等で検索)。チャット上の口頭・文章合意の可能性があり、資料外。
2. 【確認】10-08朝の夜間ループ報告の判断1〜6(判断4=Writer側を含む)に対するユーザーの回答は、DECISION_LOG・REPORT・delegation_logで見つからなかった。ユーザーが「(a1)(a2)を選んだ」のか「ALL-6で6-lunaを先に試す」と決めたのかは、ALL-6委任文の要旨(DL L20228、delegation L21)以外に記録がない。判断1〜6の回答が資料にないため、ALL-6への切り替えが夜間報告とどう接続するかは確定できない。
3. 【確認】DL L20228の「ユーザー判断(逐語要旨)」は要旨であり、全文逐語ではない。逐語は`delegation_log/2026-10-08_ALL-6-LUNA-..._01.md` L21に2文のみ。「Writer由来の事実NG」というユーザー発話が、どの記事・どの件数を指すかの記載はない。
4. 【確認】FACTLOCK-WRITER-REDESIGN-TRIAL-01の設計書(DESIGN_01.md)の最初のgit commitは10-08 12:31(v1結果と同一commit)で、設計が書かれた時刻とALL-6結果(09:31 commit)の前後関係はgitから確定できない(委任_01文面は「並行タスク」「生成は進行中Trial完了後」と記載)。
5. 【確認】「貴殿idea」(Fable提案のFact Lock案)の初出(Fableがいつ・どの資料でFact Lockを提案したか)は、委任_01の要約保存(「注: Fableからの委任文の要約保存。原文はセッション履歴」)以外に記録がない。
6. 【確認】Fableの直前報告(「重大6件はP2 brief条件で起きた」「Writer自体の改善ではない」)の全文は、資料内に保存されていない(委任文引用のみ)。比較対象はこの引用に限った。
7. 【推測】「重大6件」の数値は`ng_origin_by_stage.md`の84件(重大6/軽微78)の「重大6」と一致するが、Fableが使った母集団がこれと同一かは確認していない(記事別内訳は本書で再集計していない)。
8. 【確認】`docs/pm/b3_brief_structure_hypothesis_01.md` と `docs/pm/ng_root_cause_01/` 配下の一部は未commit(git status で`??`)。SSOTに採否の記録がなく、正式な位置付けは「仮説書」にとどまる。
9. 【確認】Opus所見「Writerへの禁止事項追記は効果未証明」(stabilization_strategy L13)は、Fact Lock(禁止・タグ規則を含む)の設計判断(「決定Aの例外」)とどう整合させたかを説明した記録は、DESIGN_01 §0の「ユーザー指示に基づく例外」以外に見つからない。
10. 【確認】Rollback誤読の個別件数(0/22、3/5等)は上記の既出SSOT引用にとどまり、再集計していない(委任_17参照)。
