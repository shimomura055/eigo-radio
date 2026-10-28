# TRIAGE_01: OPEN-581 由来46件の実態精査・分類(PM-OPEN-581-TRIAGE-46-01 委任_01B、API 0、SSOT/Production無編集)

## 0. 方法・限界
- 元記録=`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/PM_AUDIT_02_CROSSCHECK.md` §2(36件、CC:13-48)+§3(10件、CC:53-62)。OPEN-581=`OPEN_ITEMS.md:1097`。同書§1の限界(見出しだけの機械判定・偽陽性)どおり、各OPEN行の本文末尾の追記・UDR・DECISION_LOG/CURRENT_SPEC(Grepのみ)・該当コードで実態を再確認した。
- 同書の「UDR=無」判定は不正確だった(例: OPEN-263=UDR #20、OPEN-267/268=#21、OPEN-272=#22、OPEN-287=#12が実在。`docs/pm/USER_DECISION_REGISTER_01.md`)。「未登録」の多くは登録漏れではなく見出しの陳腐化。
- A/B/C定義=ユーザー原文§4-2(`docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md:155-181`)。推測でA/Cにしない。取れなかった根拠は「未確認」と明記。Family A/B/C該当は対象外Family扱い(本46件に主対象として該当なし。T21で言及の「9 runner」にはTrial/Family B・E runnerが含まれ、これらは対象外)。
- 行番号表記: `OI:Lnnn`=OPEN_ITEMS.md(2026-10-29時点)、`CC:nn`=PM_AUDIT_02_CROSSCHECK.md、`UDR:nn`=USER_DECISION_REGISTER_01.md、`CS:nn`=CURRENT_SPEC.md。

## 1. 集計(結論)
| 区分 | 件数 |
|---|---|
| A(重大・緊急) | 0(Production影響が現存する未解決の重大案件は確認されなかった。元A相当だが解決済み=T36) |
| B(重要・緊急でない) | 10(T08,T12,T15,T16,T22,T23,T24,T25,T31,T43) |
| C(軽微・管理整理) | 36 |
| うちClose提案(解決済み/吸収済み/ユーザー判断済み) | 24(T01,02,03,05,06,09,14,17,19,21,26,27,28,29,30,32,34,36,37,38,41,44,45,46) |
| うち継続管理(正式Deferred/進行中案件/記録のみ) | 11(T04,07,10,11,18,20,33,35,39,40,42) |
| うち軽微是正 | 1(T13) |
| 残るOpen Item(Close提案が全て受入れられた場合) | 22(B 10 + C継続管理 11 + 軽微是正 1) |
| 新規のユーザー判断(区分D) | なし。既にユーザー待ちで登録済みのもの=T12(UDR #21実読)、T35(AI島Std最終試聴)、T43(UDR #144試聴)、T10/T11(UDR #19実読) |
- 36件(§2)は「未決語が見出しにある」だけで、本文追記を読むと26件以上が解決済み・判断済み・吸収済み。10件(§3)は全件が登録済みで、trigger語が無いだけ。
- 未解決の重要問題は見つからなかったが、T23/T08/T15(JA-ASR誤NG/誤PASS系)は OPEN-515・JA-ASR v2 Beta Workstream A が現在処理中(関連コードは2026-10-28にR4/R3是正済み、`git log 930c31ff2`)。二重カウントせずOPEN-515へ統合とした。

## 2. 一覧(46件)
列: T | ID(元報告CC行 / OPEN行) | 内容(何が未登録・未確定か) | 重大度 | Production影響 | 現在の状態 | 対応 | 根拠 file:line | 次の条件 | 提案処理

|T|ID(元報告 / OPEN行)|内容|重大度|Prod影響|現在の状態|対応|根拠 file:line|次の条件|提案処理|
|---|---|---|---|---|---|---|---|---|---|
|T01|OPEN-224 (CC:13 / OI:L407)|T1(英語化抑制)追加検証の要否|C|なし|解決済み(Status=CLOSED、AN3-T0のみ採用・T1不採用)|是正済み|OI:L407(本文末尾『CLOSED』『T1はProductionへ混入していない』)|なし|Close(見出しが古いだけ)|
|T02|OPEN-229 (CC:14 / OI:L413)|JA Role Style(J3)の既定backendへの拡張が未決|C|なし|解決済み(X正式runnerの既定backend=flash-lite、J3は既定で有効)|是正済み|`er019_family_x_audio_production_runner_01.py:78`(承認backend=speech_metadata_flash_lite)、`:3492`(`--tts-backend`既定値=同)、`:2118-2121`(`_role_style_ja()`がflash-liteでJ3返却)|なし|Close(「既定backendへの拡張は別判断」の前提が消滅)|
|T03|OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 (CC:15 / OI:L732)|Stage1 Checker再検証Trial(USER_DECISION_REQUIRED表記)|C|なし|親OPEN-233がSUPERSEDED(2026-10-10ユーザー決定)、Production未配線|是正済み|OI:L416(『OPEN-233系Checkerは…SUPERSEDED』)。Production runner(`er019*`/`er053*`/`er012_e*`/`er026*`/`er121*`)に`er052_open233_self_recovery_precheck_01`のimport 0件(Grep実測)|子行(OPEN-233-COST-REDUCTION-01/OF018-SUBREASON-01等)は別行で本46件の対象外|Close(子行の扱いはFable確認)|
|T04|OPEN-237 (CC:16 / OI:L739)|Fact台帳明確化(P')設計、見出しUSER_DECISION_REQUIRED|C|なし|FXPW(2026-10-16)で分類済み: 台帳明確化・Note転記=B3 producerに吸収(OPEN-244 PRODUCTION_WIRED)、多義語Note自動生成=C(採否不能)。Researcher P'規則は未配線|継続管理|OI:L739末尾『closeしない』、OI:L746(OPEN-244 CLOSED/WIRED)、CS:1165|Researcher prompt側P'規則の配線をユーザーが求めたとき|継続管理(Deferred、P'規則のみ)|
|T05|OPEN-238 (CC:17 / OI:L740)|precheck数値偽陽性(案1)がPRODUCTION_WIREDだが見出しUSER_DECISION_REQUIRED|C|なし(Family X/Zの正式経路からPrecheckへ到達しない)|解決済み(案1 WIRED 2026-10-07)。Precheck本体はSUPERSEDED路線|是正済み|OI:L740(『Status=PRODUCTION_WIRED』『到達経路なし』注記)、T03と同じimport 0件Grep|なし|Close|
|T06|OPEN-248 (CC:18 / OI:L750)|B3 ROOTFIX Status『Production採用はUSER_DECISION_REQUIRED』|C|なし|解決済み(D-det v2 APPROVED→2026-10-11 PRODUCTION_WIRED)|是正済み|OI:L750(『2026-10-16注記』『見出しは陳腐化』)、OI:L746、CS:1165,1186|なし|Close|
|T07|OPEN-257 (CC:19 / OI:L759)|音韻衝突型固有名詞TTS/ASR失敗の包括対策|C|なし(固有名詞のみ不一致はPNAPでアラーム受理・HR停止なし)|ユーザー判断済み(2026-10-11『包括対策は見送り(保留)』)|継続管理|OI:L759(『保留継続(ユーザー 2026-10-11)』『新規OPENは立てない』)、OI:L963(OPEN-450 PNAP X=PRODUCTION_WIRED)|公開音声で音韻衝突が人間聴取で確認されたとき再提示|継続管理(正式Deferred)|
|T08|OPEN-263 (CC:20 / OI:L766)|SCG同形異音語の読み辞書欠落(行った等)|B|未確認(辞書外の同形異音語がSecondaryでPASSし得る既知の弱点。実発生した公開音声は確認できず)|UDR #20 Deferred、補強は未承認候補。JA ASR改善はOPEN-515で再評価中|継続管理|UDR:38(#20 Deferred)、OI:L766(『ASR出力は漢字表記で読みが落ちる…C2維持案』)|JA-ASR v2 Beta Workstream A完了後に実データ頻度を確認して再提示|継続管理(OPEN-515と一体)|
|T09|OPEN-264 (CC:21 / OI:L767)|Story品質の絶対閾値が未定義|C|なし|ユーザー判断済み(D主+C補助、絶対閾値は設定しない、2026-10-12)|是正済み|OI:L767(『ユーザー決定により…絶対閾値は設定しない』)|なし|Close|
|T10|OPEN-265 (CC:22 / OI:L768)|D/A低評価が英語再話失敗を予測するか未検証|C|なし(Z Story Pool研究)|ユーザー実読待ち(英語化Trial実施済み)|継続管理|OI:L768、UDR:37(#19)|ユーザー実読結果が出たとき|継続管理(UDR #19)|
|T11|OPEN-266 (CC:23 / OI:L769)|原語原作のAI理解品質|C|なし|同上|継続管理|OI:L769、UDR:39(#21関連)|同上|継続管理|
|T12|OPEN-267 (CC:24 / OI:L770)|L05『交尾』の扱い・底本の第三者権利が個別未確認|B|なし(L05は未制作。公開前に権利確認が必要)|UDR #21 Deferred(L05はユーザー実読待ち)|継続管理|UDR:39(#21)、OI:L770|L05を記事化候補にする時点で権利確認を実施|継続管理(再提示trigger=L05記事化時)|
|T13|OPEN-268 (CC:25 / OI:L771)|`er054_family_z_story_pool_trial_02_test_01::test_real_refused_without_budget`がcp932文字化けで失敗|C|なし(test環境起因)|再現確認済み: `PYTHONUTF8=1`でPASS、未設定でFAIL(本委任で実測)|軽微是正(test内subprocessのenv/encoding指定)|runtime: `py -3 -m pytest er054_family_z_story_pool_trial_02_test_01.py -k test_real_refused_without_budget` → PYTHONUTF8=1: 1 passed / 未設定: 1 failed|なし|軽微是正(委任_02Bで1行修正、またはFableが『環境起因・Trial専用』としてClose)|
|T14|OPEN-269 (CC:26 / OI:L772)|評価指標改善の相互参照のみ|C|なし|OPEN-264/265へ参照済み(新仕様なし)|是正済み|OI:L772(『相互参照のみ、新規仕様なし』)|なし|Close|
|T15|OPEN-272 (CC:27 / OI:L775)|固有名詞ヒューリスティックの粗さ(JA C1・EN capitalized)、EN偽NG(US↔U.S.等)|B|未確認(EN偽NGはFinal v3 Std Part2で再発記録あり=OI:L775末尾。頻度は未確認。`er021/er006/er078`に「U.S.」正規化コードはGrepで見つからず)|UDR #22 Deferred。JA側(C1)はOPEN-515が再評価中|継続管理|UDR:40(#22)、OI:L775|Workstream A完了後にEN表記差(US/U.S.、cost/costs)のattempt消費実績を集計して再提示|継続管理(JAはOPEN-515統合)|
|T16|OPEN-273 (CC:28 / OI:L776)|一時API失敗(5xx/429/timeout)が音声不良と区別されずattemptを消費|B|あり得る(実測: `er011_output/attempt_history.jsonl` 20,029行中classification=`TTS_FAILURE` 190件=0.95%。attempt消費の有無はコード未追跡のため「消費実績」は未確認)|未解決。統一仕様(CS:3155以降)は3回ブロックで、技術失敗の非消費規定なし(Grep)|継続管理|runtime: `wc -l`=20029、classification別集計(`TTS_FAILURE`=190)、CS:3155節に429/5xx規定なし|HR増/429多発が観測された時、または次のTTS統合改修委任に相乗り|継続管理(再提示trigger案=TTS_FAILURE率2%超)|
|T17|OPEN-274 (CC:29 / OI:L777)|LR再TTSがminimal fallbackに依存、LR span選択|C|なし(X/Y/Z)|部分解消(LR block 3回構成化=OPEN-540、PM-SSOT-SYNC-17)。残=minimal廃止は別判断(Family A/B系はscope外)|是正済み|OI:L777末尾『部分解消』、CS:3155(統一仕様)|なし|Close(minimal廃止の別判断は対象外Family)|
|T18|OPEN-278 (CC:30 / OI:L781)|異音検知の非ブロッキング警告Validator|C|なし|ユーザー決定済み: Production組込みDEFERRED、検知アルゴ追加開発なし(2026-10-12)|継続管理|OI:L781(『ユーザー決定: DEFERRED(保留)、追加開発なし』)|再開時は条件A(Opus)+ユーザーAPPROVED_FOR_PRODUCTION|継続管理(正式Deferred、再開条件記載済み)|
|T19|OPEN-279 (CC:31 / OI:L782)|Trial限定条件(発音hint省略・同期生成・正規化)で作った試聴音声の採用時再生成要否|C|なし|CoffeeはFinal v3でProduction runner経由に再整理(PRODUCTION_DIFF_V3_01.md)、以後のX承認仕様は正式runnerで生成|是正済み|OI:L782(『Final v3…再整理』)、CS:1265(Phase3 Coffee正式E2E runtime evidence)|新Trial候補を採用する都度、その委任で本番条件再生成を確認|Close提案(Fable照合推奨: 他Trial候補の採用実績は個別未確認)|
|T20|OPEN-282 (CC:32 / OI:L785)|`attempt_history.jsonl`が再利用segmentまで重複退避し肥大|C|軽微(実測27,705,372 bytes・20,029行、`er011_output/attempt_history.jsonl`。性能影響は未確認)|未解決(監視のみ)|継続管理|runtime: `ls -la`/`wc -l`|ファイル>100MBまたは読込時間問題が出たとき|継続管理(閾値案=100MB)|
|T21|OPEN-285 (CC:33 / OI:L788)|単価未登録モデルを0円扱い(9 runner)vs Azure停止の方針混在|C|なし(X/Y/Z)|解決済み(X/Y/Zは共通`er019`の`_load_pricing`がfail-closed、Y/Zはx_runnerを読取専用で呼ぶ)。9 runnerの大半はTrial/Family B・E runner=対象外|是正済み|`er019_family_x_audio_production_runner_01.py:3020-3035`(PricingNotFoundError)、`er026_family_z_fiction_production_runner_01.py:1277-1278`、`er121_family_y_runner_01.py:155-156`|なし|Close(対象外Family/Trial runnerは追跡しない)|
|T22|OPEN-286 (CC:34 / OI:L789)|統一フロー導入前提: PASS_WITH_WARNING試聴連動/A2 LR再TTS計数/累計ガード再計算|B|未確認|親AUW=OPEN-370 PRODUCTION_WIRED(2026-10-16)で設計吸収。(3)累計ガードは`MAX_CUMULATIVE_TTS_ATTEMPTS=15`のまま(統一仕様の最大ブロック数との整合は未確認)|継続管理|OI:L879(OPEN-370『親項目=OPEN-286〜291…設計は具体化済み』)、`er011_human_review_lock_01.py:68`(=15)、CS:3075(PASS_WITH_WARNING事後試聴リスト)|統一仕様のLR後ブロックで累計上限到達の実績を確認|継続管理(AUW実走データで確認)|
|T23|OPEN-287 (CC:35 / OI:L790)|JA S1(数値)の漢数字盲点・表記差誤発火|B|未確認(コードは2026-10-28にR4/R3是正済み`930c31ff2`。是正後の実態は未確認)|OPEN-515が追跡中(INVESTIGATING)。UDR #12|継続管理|UDR:30(#12)、OI:L1030(OPEN-515『R3桁区切り・R4 Secondary値等価層』)、`git log 930c31ff2`|JA-ASR v2 Beta Workstream A受入後に再評価|継続管理(OPEN-515統合。Workstream Aで処理中)|
|T24|OPEN-288 (CC:36 / OI:L791)|見出しが標準1+minimal2構成でPrimary単独PASSを見逃す|B|未確認(見出し音声は統一judgeを通る: `er003_v1_sing01_point_headings_aoede.py:132-133`。標準1+minimal2構成は`:79-81`に現存。X/Y/Zでの使用有無は未確認)|AUWで主要部分を吸収。minimal撤去(D-8)は別判断|継続管理|`er003_v1_sing01_point_headings_aoede.py:36-37,79-81,132-133`|point headingsをX/Y/Zが使う場合のみ再評価|継続管理(低)|
|T25|OPEN-289 (CC:37 / OI:L792)|KP 4→3回単一Promptの中身(P-a/b/c)とMaster Store 241件再利用|B|未確認(KPはその後KP3V(OPEN-451/UDR #152)で多数決方式がAPPROVED。trim policy `v2_margin030`は現存: `er006_audio_cost_pilot_02_shared_narration.py:58`)|UDR上は#8/#18の親括り。吸収先の詳細照合は未了|継続管理|OI:L792、UDR:26,36(#8,#18)、UDR(#152 KP3V APPROVED)|KP Prompt変更を検討する委任のときに照合|継続管理(Fableが吸収確認できればClose)|
|T26|OPEN-290 (CC:38 / OI:L793)|JA LRなし/EN LR発火条件/F-5先行修正|C|なし|LR仕様は統一仕様(OPEN-540、2026-10-26ユーザー決定)で置換済み。F-5部分はT15へ集約|是正済み|CS:3155(統一仕様 LR=最大1回)、OI:L777(OPEN-540統合)|なし|Close(F-5はT15)|
|T27|OPEN-291 (CC:39 / OI:L794)|言語別Secondary選択、D6二重Azure呼出|C|未確認(D6二重呼出費用=約2円/件は未再測)|AUW(OPEN-370)の統一judgeで確定(JA/EN=Azure、S+W規定)|是正済み|OI:L879、CS:3075-3076(統一ASR判定表)|なし|Close提案(D6は原価低減の話題。Fable照合推奨)|
|T28|OPEN-293 (CC:40 / OI:L796)|Advanced Full Story減速がPrompt文のみで不足|C|なし|PACE-TRIAL-02/Final v3でPD8採用(Coffee)、以後Family XのFull Story承認Style=PD06|是正済み|CS:1224(Full Story TTS=PD06)、OI:L796末尾(Final v3)|なし|Close|
|T29|OPEN-294 (CC:41 / OI:L797)|10秒窓WPM>250警告閾値の妥当性|C|なし(Production codeにWPM窓警告なし。`er*.py`でWPM窓警告を持つのは`er057_pace_trial_01_measure.py`/`er057_pace_trial_02_measure.py`のTrial計測のみ)|警告を採用していない|是正済み|Grep `window_wpm|WINDOW_WPM|wpm_warning` → Trial計測script2件のみ|警告を採用する判断が出たとき|Close|
|T30|OPEN-297 (CC:42 / OI:L800)|Melos 3方式比較の判断待ち|C|なし|ユーザー正式決定済み(2026-10-12 Sol採用/B3Z REJECTED/R0→R1→R2 APPROVED、2026-10-16 Sol統一)|是正済み|OI:L800(『ユーザー正式決定で更新』『本行は記録のみでcloseしない』)|なし|Close|
|T31|OPEN-331 (CC:43 / OI:L834)|HR採択takeを正規clipへ配置する汎用機構なし/RESTART_STORMが逐次stageを誤検知|B|未確認|Melos完成(2026-10-13、UDR #23判断済み)は個別手順で解決。汎用機構の有無は未確認。RESTART_STORM運用はOPEN-480(CLOSED)でstage一括指定を再発防止化|継続管理|OI:L834末尾(『量産向けに残る(1)(2)』)、OI:L995(OPEN-480 CLOSED)|量産でHR採択takeが発生した時|継続管理|
|T32|OPEN-353 (CC:44 / OI:L862)|KP供給段fragment対策C1〜C4|C|なし|ユーザー判断済み(2026-10-14 C4『当面変更なし・A′結果確認』、再提示しない)|是正済み|UDR:78(#58 判断済み)、OI:L862|A′結果確認(OPEN-349)|Close|
|T33|OPEN-369 (CC:45 / OI:L878)|受入記録へ目的要件照合を必須化(欠陥②対策)|C|なし(PM運用)|採用済み(#76/#77)、様式反映済み。有効性は再盲検待ち(是正3=#81 B1ユーザー承認待ち)|継続管理|OI:L878(『採用済み(2026-10-15)』『是正3は#81 B1』)、UDR:96(#76)|UDR #81 B1の判断が出たとき|継続管理(PM運用、低)|
|T34|OPEN-537 (CC:46 / OI:L1052)|Y Style profile乖離|C|なし|PRODUCTION_WIRED(Fable受入2026-10-27)、CLOSED相当|是正済み|OI:L1052末尾(SYNC-23『Status=PRODUCTION_WIRED』『WIRED_CHECK_02.md条件1〜7充足』)|なし|Close(OPEN-543分は別行)|
|T35|OPEN-561 (CC:47 / OI:L1077)|AI島Std/Adv V3フォーム実運用|C|なし(個別案件が進行中)|Adv=ユーザー承認済み、Std=Comment3 Z方式で再制作済み・最終試聴の再提出待ち(2026-10-28)|継続管理|OI:L1077末尾『2026-10-28追記』|Std最終試聴の承認|継続管理(進行中案件。管理漏れではない)|
|T36|OPEN-565 (CC:48 / OI:L1081)|LR・Fallback・M3横断監査(公開音声と本文の不一致3件を含む。元A相当)|C(解決済み)|なし(是正済み)|UD-1〜3ユーザー決定(2026-10-28)→OPEN-569でPRODUCTION_WIRED(X/Y/Z×Std/Adv、Fable受入)。Word Gacha Adv・猿の手Stdは候補版を正式公開(commit 0bff5a518)、AI島はユーザー試聴待ち(T35)|是正済み|OI:L1085(OPEN-569 SYNC-33『PRODUCTION_WIRED』『委任_16 正式公開』)、OI:L1081(SYNC-29)|なし|Close|
|T37|OPEN-306 (CC:53 / OI:L809)|Melos Voice承認(Algieba暫定)|C|なし|Melos Std/Adv試聴PASS・完成版run_e2e_06(UDR #23 判断済み2026-10-21)|是正済み|UDR:41(#23)。注: UDR:32(#14)は『判断保留』のまま陳腐化(参照漏れ)|UDR #14の注記更新のみ|Close(UDR #14注記更新案は委任_02B)|
|T38|OPEN-308 (CC:54 / OI:L811)|Syracuse未登録・Melos誤認識のLedger登録要否|C|なし(EN固有名詞のみ不一致はPNAPでアラーム受理、JA三日間はOPEN-319/515)|ASR原因はROOT_CAUSE_01で分類A是正済み+C/D=HR妥当。登録要否はPNAP方針(B階層=人承認登録)に包含|是正済み|OI:L811(ROOT_CAUSE_01追記)、OI:L963(OPEN-450)、UDR:25(#7)、UDR:28(#10 判断済み)|なし|Close|
|T39|OPEN-316 (CC:55 / OI:L819)|Comment4 Prompt: Std側配線済み、B1(Advanced)側展開が未決|C|なし(Std配線済み、Advは従前のまま)|ユーザー指示でdeferred(2026-10-16 §7、UDR #99)|継続管理|OI:L819末尾『2026-10-16 FXPW・分類A…deferred』、UDR:225(#99 判断済み=deferred)|IOL基本2文化の完了、またはAdv Comment4不具合発生時|継続管理(正式Deferred、trigger記載済み)|
|T40|OPEN-330 (CC:56 / OI:L833)|Pattern A語幹末s受理範囲/F1後続置換見逃し|C|なし(F1は是正済み)|ユーザー決定(2026-10-20): 選択肢A/A' REJECTED・現行維持・再提案は条件付き(UDR #119/#120)。F1はOPEN-340で実装(全差分点検)|継続管理|OI:L833末尾『[2026-10-20 ユーザー決定]』、UDR:286-287(#119,#120)、`er011_b1_connected_speech_validator_01.py:204-211`(F1全差分点検)、OI:L843(OPEN-340)|再提案は原因・他案・QCDが揃った場合のみ|継続管理(正式保留)|
|T41|OPEN-388 (CC:57 / OI:L897)|A3 length NGがPrimary由来で独立QAでない|C|なし|是正済み・Fable判定PRODUCTION_WIRED(2026-10-16)、AUWユーザー承認|是正済み|OI:L897末尾(委任_13/14『PRODUCTION_WIRED』『追加改修なし』)、`er003_v1_sing01_point_headings_aoede.py:132-133`(final_length_ok使用)|なし|Close|
|T42|OPEN-394 (CC:58 / OI:L903)|Primary層が誤文面でもPASSする弱点(仕様候補)|C|あり得る(既知の限界。誤読の実例は未確認=live負例は合成)|ユーザーが保留明示(2026-10-16 §1-A/§7『再発行しない、記録のみ』)|継続管理(記録のみ)|OI:L903末尾、UDR:201,231(#93 再発行しない)|ユーザーが再提案を求めたとき|継続管理(記録のみ。判断要求を新規に出さない)|
|T43|OPEN-432 (CC:59 / OI:L944)|Paycheck E2E: Std fallback takeは個別承認済み、記事全体の最終試聴PASS未取得|B|なし|e2e_01は完成候補、その後OPEN-442(run_pp_02)が記事A再制作。UDR #144『回答待ち』(2026-10-22〜)|継続管理|OI:L944(『PRODUCTION_TECH_COMPLETE_USER_LISTENING_PENDING』)、OI:L955(OPEN-442)、UDR:337(#144 回答待ち)|ユーザー試聴(e2e_02)の回答|継続管理(再提示trigger=UDR #144。7日経過のためFable報告でリマインド)|
|T44|OPEN-474 (CC:60 / OI:L989)|FX-KP汎化意味の配線状況|C|なし(X/Z=PRODUCTION_WIRED、Yは別行)|Fable受入(2026-10-24)でX/Z PRODUCTION_WIRED。Y=OPEN-484。監視指標新基準案=UDR #187(非blocking)|是正済み|OI:L989末尾『判定: X=PRODUCTION_WIRED・Z=PRODUCTION_WIRED(Fable受入2026-10-24)』、OI:L999(OPEN-484)|なし|Close(Y=OPEN-484、#187は別途)|
|T45|OPEN-497 (CC:61 / OI:L1012)|Z学習テキスト解説Trial(VALIDATED限定、Production未配線)|C|なし|ユーザーが2026-10-25にFamily X/Y/Z共通仕様としてAPPROVED_FOR_PRODUCTION。配線はOPEN-519でX/Z=PRODUCTION_WIRED|是正済み|OI:L1012末尾(『PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01』『配線はOPEN-519で追跡』)、OI:L1034(OPEN-519)|なし|Close(OPEN-519へ移管済み)|
|T46|OPEN-503 (CC:62 / OI:L1018)|告げ口心臓: ユーザー試聴待ち|C|なし|公開版=Fenrir版でユーザー正式承認・公開反映済み(2026-10-28)|是正済み|OI:L1018見出し『2026-10-28最新: 公開版=Fenrir版でユーザー正式承認』、OI:L1086(OPEN-570: 公開mp3 55本sha=候補、`voice_acceptance_check` ALL_MATCH)|なし|Close(OPEN-570は別行で完結)|

## 3. A判定の裏付け結果(Fable独立照合用)
- A=0。検索した「Production影響あり」候補の否定根拠:
  - 未承認仕様がProductionで動いている: T04/T05(Precheck/Checker)→Production runnerにimport 0(T03のGrep)。T42(Primary層の限界)→未承認の新仕様ではなく承認済みAUWの既知限界で、ユーザーが記録のみと明示。
  - 承認済み重要仕様が未配線: T02(J3)→既定backendで有効(`er019:78,3492,2118`)。T22/T25→AUWはOPEN-370でPRODUCTION_WIRED。T44/T45/T34/T36→Fable受入でPRODUCTION_WIRED。
  - 実動作と承認仕様の食い違い: T40のF1(承認前提『差は1か所』vs実装『最初の食い違いのみ』)は`er011_b1_connected_speech_validator_01.py:204-211`で全差分点検へ是正済み(OPEN-340)。JA ASRのR1〜R4(月Std題HR Lock)はOPEN-515・Workstream Aで処理中で、T23/T08/T15へ統合。
  - 重大STOP/HRが機能していない: T16(一時API失敗のattempt消費)は機能不全でなく設計の未規定(B)。T36は元A相当(公開音声と本文の不一致3件)だが2026-10-28にOPEN-569で是正済み。
- 未確認として残した点(推測でA/Cにしていない): T08/T15/T23の是正後の実態(OPEN-515・Workstream Aの結果待ち)、T16の消費実績、T22(3)の累計ガード整合、T24のX/Y/Z使用有無、T25の吸収確認、T31の汎用機構の現存、T27 D6費用。
- 実測した事実: `attempt_history.jsonl`=27,705,372 bytes/20,029行/TTS_FAILURE 190件。`er054`テストはPYTHONUTF8=1でPASS・未設定でFAIL。X/Y/Zのcost集計は共通fail-closed。

## 4. 提案する後続(本委任では実装しない。委任_02B以降はFable判断)
1. SSOT整合: Close提案24件の注記追記、見出し陳腐化の訂正、UDR #14の注記更新、OPEN-581自身のClose。新規Gate・検査は追加しない(原文§4-4)。
2. B10件は『継続管理+再提示trigger』をOPEN行に追記(T08/T15/T23はOPEN-515へ統合)。
3. 管理漏れを理由に46件分の新規開発タスクは作らない(原文§4-3)。軽微是正はT13のみ(任意)。
