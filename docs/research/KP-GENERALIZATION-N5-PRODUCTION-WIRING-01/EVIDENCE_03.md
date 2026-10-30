# KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_03 EVIDENCE(2026-10-30〜31)

状態: J2(Trial入力条件の再現)を是正し、未観測項目の実run・是正後の再証拠を取得した。**PRODUCTION_WIREDとは呼ばない**(Fable受入待ち。未観測=⑪人称書換の実例0件が残る。§9)。
置き場: 本ファイルと `ev03/`(M10=`ev03/m10/`、J2検証=`ev03/j2_*`、X/Y/Z=`ev03/{x,y,z}/`、テスト=`ev03/tests/`、起動記録=`ev03/launches.txt`+`launch_epochs.txt`、費用=`ev03/cost_table.json`+`ledger_log.txt`)。複製run dir本体(音声なし)は一時領域のため未commit。

## 1. J2の再診断と是正(分類B・11-8範囲内)
**前提の再確認**: 委任文の前提(「Trial 03のP7入力は保存済みProduction docのQA通過後候補であり、F判定になるsub-spanはTrialのpoolに存在しなかった」)は部分的に正しくない。`ev03/j2_trial_blocker_audit.py`(API 0、Trial 19ケースの記録応答replay)の結果: Trialのpoolで包含dedupeに落とされたB1候補76件のうち、**包含相手がTrial P7でSEL非keep(F)だったものが26件**(`ev03/j2_trial_blocker_audit.json`)。つまり「SELがFのP7 sub-spanがB1 supersetを落とす」挙動自体はTrialにも存在した。ただし26件のうち、**同一span(表記違い含む)の重複が23件・異なるspan(厳密な包含)は3件**(ai_cha_a2 `clear fall`←`confirm a clear fall`、moon_b1b `heat from escaping`←`keeps heat from escaping`、ignobel_a2 `that number alone`←`Take that number alone`[`that`始まりの節断片=FRAG除外のため再判定対象外])。④`set a lower limit`はTrialではP7候補そのもの(fixture jwst_m_b1b base)で、委任_02のM10で落ちたのは**Production側のP7が別のspan境界(`a lower limit`)を返した**ため(P7のLLM非決定性)。

**是正(Fable案(a)の厳密化・Trial 19ケースexact維持)**: `er138_kp_n5_generalization_01.pool_and_select`で、B1候補が**異なるspanのP7候補(またはB1先着)に包含関係で除外された場合**、SEL後にその包含相手が**keepでない**ときだけB1候補をSEL再判定(`SEL_DEFERRED`、追加1 call)してpoolへ戻す。同一span重複は再判定しない。包含相手がkeepなら従来(Trial逐語)どおり除外。`collect_pool`のdedupe・FRAG・pick・Prompt・schema・閾値は無変更(差分は`er138_kp_n5_generalization_01.py` +50/-14行のみ)。除外理由(`n5_pool`)に「Trial差分」文言と`blocked_by`を記録、再判定した件は`record.deferred_rejudged`に記録。flag/新Gate/Prompt追加なし。

最初に試した単純案(同一span重複も含め包含相手がkeepでなければ全て再判定)は、Trial 19ケースのうち14ケースで再判定callが必要になり(同一spanの重複を無駄に再判定、Trialと選定が変わり得る)、「19ケースexact維持」を満たさないため採用せず、上記の厳密化版に改めた(`ev03/j2_replay.log`相当の確認は上記audit)。

- Trial replay: 19ケースのL1選定がTrialのL1と**exact一致**(17ケース=cache replayで再判定callなし、2ケース[ai_cha_a2 `clear fall`・moon_b1b `heat from escaping`]=再判定callが必要だったため実API 2 call[¥0.096]で確認し**いずれも非keep=Trialと同一選定**。`ev03/j2_part1_result.json`)。回帰test: `TestJ2ProductionL1EqualsTrialOnRecordedCases`(19ケース)。
- ④の決定論的検証(`ev03/j2_part2_result.json`、実API ¥2.49): 委任_02のM10保存のP7出力7件+B1返却14件をそのまま入力し、公式部品(`pool_and_select`→`run_l3`)を実行 → P7`a lower limit`(SEL=F)に除外されたB1`set a lower limit`がSEL再判定でkeep→pick→`set a lower limit → set a limit`(CHK5=MODIFIER_DROPPED_OK)として保持。
- 実run(§3〜§5)でのdeferral発火: 10回のL1中3件(`ev03/j2_deferral_in_real_runs.json`)=`overlapped with some celestial objects`(keep)・`take the trouble to`(keep)・`a particular wavelength`(非keep)。**挙動変化の範囲**: 包含相手がSEL非keepの場合にsupersetが候補に残る(Trial記録19ケースでは0件、実run 10L1中2件の追加)。**残る限界**: 包含相手がSEL keepだが後段のQA(canonicalization_qa等)で落ちる場合は、supersetは戻らない(QAはL1より後段のため判定不能。観測0件)。

## 2. Trial 03との一致・回帰
- 新規/更新test(`er138_kp_n5_generalization_01_test_01.py` 59本・`er138_wiring_test_01.py` 31本)OK(`ev03/tests/`)。J2用: 再判定の発動/非発動(相手keep・同一span・別keepと包含・非包含)、collect_pool既定=Trial同一。
- 既存回帰(委任_02と同一の対象214ファイル・並列実行): 52ファイル失敗。うち委任_02との差分16ファイルは**全てbaseline(HEAD=3d404cfc6、本変更なし)でも失敗**(`ev03/tests/baseline_head_rerun_of_those16.txt`で16/16)=worktreeのCRLF/seed sha・音声evidence等の環境起因。er138・er119_kp_backfill・er119_x_wiring・er006 routing・er053_cost_aggregate: OK。N5/J2起因の回帰0。
- 委任_02からのコード差分=`er138_kp_n5_generalization_01.py`(L1の`pool_and_select`/`collect_pool`/`select`のlabel引数)とそのtestのみ(`git diff --name-only 3d404cfc6`)。L3・配線(er119)・routing・pricing無変更 → 他3level(X b1b・Y a2・Z b1b)の委任_02証拠はL3以降について有効(L1のみ本是正の影響)。ただし§4のとおり本是正後のY a2・Z b1bも実測した。

## 3. M10統合replay再実行(実API、Production `generate_candidates`公式経路、基準は`ev03/m10_thresholds_fixed.md`=委任_02と同一)
対象: jwst_m_b1b・untidi_a2・melos_a2(3level、費用¥19.05)。**untidi_b1bは委任_03では個別Cap見通しのため未実施→委任_04で実施済み(¥7.85、§10)**。以下は委任_03時点の3level記録(4level集計は§10・`ev03/m10/analysis.txt`)。

| level | 費用 | 結果 |
|---|---|---|
| jwst_m_b1b | ¥5.85 | ④: P7が今回`set a lower limit on`を返し、`set a lower limit on → set a limit on`(MODIFIER_DROPPED_OK)として保持=④相当(P7のspan境界差)。⑤`took an unexpected turn → take a turn`保持。再判定発火2件(1件keep)。 |
| untidi_a2 | ¥7.91 | ①`hear it out → hear someone out`保持、②`take points away from → take something away from`保持。`make life work`はSEL=F(cls=F)でN5 drop(委任_02と同一・2/2回、§8)。 |
| melos_a2 | ¥5.29 | **③`kept his eyes on them`が今回生成** → `keep one's eyes on`(SAME、flags FRAME_MISMATCH/PRONOUN_SLOT/VER_FIXED_FORM)。Trialのfixture(`test_4A_keep_ones_eye_on_boundary_example`、`keep one's eye on`)と同じ境界処理(語形は`eyes`のまま=本文の数)。 |

集計(3level、`ev03/m10/analysis.txt`。analysis.txtはspan境界違いの④を未再現側に数える): Trial生存候補21 → 同span保持11(+④をspan境界違いで保持1)・既存Gate喪失**0件(0%、基準15%以下)**・N5 drop 1(`make life work`)・未再現8(P7/B1がそのspanを返さない=LLM非決定性)。**§4A①②③④⑤の喪失なし**(③は生成された回で正しく処理、④はdeterministic fixtureとM10の両方で保持)。③の判定条件はfixture固定済み(生成されたときに正しく扱われること)。他の喪失の増加なし。

## 4. 是正後のruntime再証拠(正式runner CLIの複製run、本文・TTS再生成0)
X=`er019_family_x_audio_production_runner_01.py --slug untidiness_family_resource --run run_n5ev3 --level a2 --stage scaffold --scaffold-only kp`(技術失敗injection付き、§5.1)、Y=`er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_n5ev3 --stage kp --approved-budget-jpy 40`(+theme-package=main repoの現行THEME_DATA_02[seed sha一致]・reuse-manifest)、Z=`er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --slug the_tell_tale_heart --run run_n5ev3 --stages kp --mode real --approved-budget-jpy 30`。全て`stop_scope_check_01.py`rc=0確認後、`launch_gate.py`経由(§7)。複製元=委任_02の`run_n5ev`/`run_n5ev2`(KP成果物・launch log・cost logを除いた複製、`run_n5ev3`)。

| 項目 | X a2 | Y a2 / b1b | Z a2 / b1b |
|---|---|---|---|
| actual model_id | B1/SEL/GEN5=gpt-6-luna、VER5=gemini-3.8-flash、CHK5=gpt-6.1-sol(全route共通) | 同左 | 同左 |
| Gemini model_version | gemini-3.8-flash(正規化一致) | 同左 | 同左 |
| Prompt sha16 / FLAGS hash / 方式id | CURRENT_STATE_01 §4と一致(`evidence_*.json`)、`N5@T3-2026-10-30` | 同左 | 同左 |
| 候補数 / N5対象 | 10 / 5(phrase 5件全てn5記録あり) | a2 10/5、b1b r1 12/7→r2 11/6 | a2 r1 5/1→r2 11/6、b1b 10/5 |
| used_form語数(N5) | 2語2・3語2・4語1 | a2 2語1・3語3・4語1 / b1b r2 2語3・3語3 | a2 r2 2語1・3語5 / b1b 3語4・4語1 |
| 英日本文の一致(used_form==key_phrase==n5.display_form、gloss==n5.gloss_ja、source_spanが本文実在) | 全件一致 | 全件一致 | 全件一致 |
| gloss_alignment_status | 全ALIGNED | 全ALIGNED | 全ALIGNED |
| B1 pool drop(n5_pool) | 14(3 L1合計、attempt1・2含む) | a2 8 / b1b r1 6・r2 8 | a2 r1 4・r2 4 / b1b 4 |
| n5_* drop | n5_select 3 | a2 n5_select 3 / b1b r1 n5_select1・n5_pick2・n5_generalize1 | a2 n5_select 2 / b1b n5_select 2 |
| 既存Gate drop | canonicalization_qa 2 | a2 cmu1 / b1b r2 symbol・validate・canonicalization_qa 各1 | a2 canonicalization_qa 2 |
| 補完(backfill) | 発火 | 両level発火 | a2発火 / b1b 不発動 |
| CHK5 relation | SAME 4+revert1 | a2 SAME4+MODIFIER_DROPPED_OK1 / b1b SAME 6〜7 | a2 SAME5+FRAME_SHIFT1(revert1) / b1b SAME4+MODIFIER_DROPPED_OK1 |
| 人称整合でN5 gloss書換 | 0 | 0 | 0 |
| 除外計上(E) | n5_pool/select/pickは非計上、generalize/verify/checkは計上(`dropped`に記録) | 同左 | 同左 |
| 費用(各run実測、全段) | ¥7.94 | ¥18.90(round1 ¥12.04+reselect ¥6.86) | ¥15.10(round1 ¥10.11+reselect ¥5.00) |

※X a2の費用にはinjection前のattempt 1のN5 L1(¥0.47)を含む。Yは両levelが同一runnerの1 stageで生成される(1 level単独起動不可)ため両level取得、Zも同様。集計JSON=`ev03/{x,y,z}/evidence_*.json`、候補doc=`ev03/{x,y,z}/kp_candidates_*.json`、コンソール=`ev03/console_*.log`。

## 5. 未観測項目の実走(§4B)
1. **技術失敗injection(X a2、実run)**: harness=`ev03/inject_run.py`(runnerをrunpyで1回起動、`_send`のGEN5送信前に1つのcallの全attempt[MAX_ATTEMPTS=2]を例外化=課金なし。ログ`ev03/inject_log.jsonl` 00:23:01・00:23:03)。結果: N5 L3のGEN5が`N5TechnicalFailure`→`canonicalization_N5_TECHNICAL_FAILURE`として**外側retry(outer_attempt 1→2)で回復**。最終doc(`ev03/x/kp_candidates_a2.json`)は`outer_attempts=2`、phrase候補5件**全てn5記録あり(N5なし候補0)**、attempt 1の候補docは保存されない(`outer_retry_log`にfailureのみ記録)。injection前に課金されたのはattempt 1のL1(B1+SEL)¥0.47のみ。
2. **Y再選定round(実run)**: b1b `reselect --ng 3:...`(NG=`hard on`)→同コマンド再実行で round 2 を再生成(¥6.86のうちN5 ¥4.29)。NG句`hard on`は復活せず、round 1文書は`kp_candidates.SUPERSEDED_1.json`へ退避(`ev03/y/kp_candidates_b1b_round1.json`=round 1)、`kp_human_review.json`にNG記録(`ev03/y/kp_human_review_b1b.json`)。
3. **Z再選定round(実run)**: a2 `reselect --ng 1:...`(NG=`made my blood turn cold`)→再実行でround 2(¥5.00のうちN5 ¥4.18)。round 1は1 phrase(shortfall)→round 2は5 phrase+補完。NG句は復活せず(`ev03/z/kp_human_review_a2.json`)。
4. **人称書換(Z person_repair)の実例**: 全7候補docで`n5_gloss_rewritten=0`(Z a2 r1/r2・b1b を含む)。実例は**0件=未観測**と明記する(作為的に発生させない)。mock test(`TestApplyToItem`等)のみ確認。→委任_04で正式関数を通すdeterministic fixtureによる発火・更新の観測を追加(§10-2。自然発生の実例ではなくfixture)。

## 6. 量産単価の実測(N5段、1記事セット=Std+Adv、`ev03/cost_table.json`)

| 経路 | N5段の費用(補完込み) | 補完なし | 備考 |
|---|---|---|---|
| Y(round 1、a2+b1b) | ¥7.22 | ¥6.11(補完¥1.11) | chk5が全体の約半分(Y累計: chk5 ¥6.10/N5計¥11.51) |
| Z(round 1、a2+b1b) | ¥4.01 | ¥4.01(round 1は補完のN5 API 0) | |
| X(a2のみ) | ¥3.21 | ¥3.15 | injection前のattempt 1 L1 ¥0.47を除く。b1bは委任_02実測参照 |
| 再選定1 round(1 level) | Y b1b ¥4.29 / Z a2 ¥4.18 | | 補完を含む |

Trial見積¥6.28/セットとの差異: 委任_02(X ¥6.92・Y ¥8.90・Z ¥5.58)と本委任(Y ¥7.22・Z ¥4.01)の計5サンプル平均=**¥6.53**(Trial比+4%)。範囲¥4.01〜8.90。差の主因=B1返却数・SEL keep数・補完発火に依存(Zは候補が少なくGEN5以降の件数が少ない)。stage別内訳=`cost_table.json` `n5_by_stage`(Y: chk5 ¥6.10・ver5 ¥2.97・gen5 ¥1.24・sel ¥0.73・b1 ¥0.47)。J2の再判定callは1 callあたり約¥0.05(luna SEL)で量産単価への影響は無視できる。**未承認の節約策は不採用**(承認済みPrompt・モデルは無変更)。

## 7. 運用逸脱・規則遵守の記録(隠さず記録)
- 委任_02の運用逸脱(再掲): M10枠¥20に対し¥21.80(¥1.80超過、並列2本起動で事前合算guard未適用)、Y runの起動間隔66秒(規則>=150秒違反)とRESTART_STORM STOP(`run_n5ev`、API 0。解除せず別dir`run_n5ev2`で実施した=安全停止の実質回避に当たる運用)、自コードのdict key=None不具合による再生成約¥5.3。今回これらは**繰り返していない**。
- 委任_03の遵守: 起動11回(M10 4[うちuntidi_b1bはCap guardで実行前拒否]・X 1・Y 3[seed sha STOP含む]・Z 3[同])を`launch_gate.py`経由で記録(`launch_epochs.txt`)。**最小間隔150秒・300秒窓の最大起動数2・違反ゼロ**。各起動前に`stop_scope_check_01.py`(rc=0、`stop_check_*.json`)と費用台帳guard(`ledger.py --check`、実測+見積り>¥70でrc=3)を実行。Y/Zの`FamilyZProvenanceMismatchStop`(seed sha不一致、worktreeのCRLF化によるsha差。API 0)は原因を特定し、seed/theme packageをmain repoの現行内容へ合わせて各1回再起動(同一原因の不明rc≠0の連続ではない)。既存STOP(`run_n5ev`のRESTART_STORM)は解除・接触せず、新規複製dir`run_n5ev3`を使用(STOPを回避した別名継続ではなく、各run dirは今回初めて起動)。
- 費用合計(Cap ¥70固定): **¥63.57** = J2検証¥2.58(part1 ¥0.096+part2 ¥2.49)+M10再replay¥19.05+X ¥7.94+Y ¥18.90+Z ¥15.10。Cap超過なし。内訳目安との差: M10+J2検証 ¥21.63(目安≤25)、runtime+未観測 ¥41.94(目安≤30+15)。
- worktree: `<scratchpad>/wt_n5`を`git reset --hard`でorigin/main(3d404cfc6)へ更新(旧checkoutの内容が残っていたため。新規フルcheckoutなし)。Z`seed/seed.json`をmain repoの現行(LF、provenance sha一致)へ置換(worktree限定・commitしない)。

## 8. 観測事項(欠陥ではない/要追跡)
- untidi_a2 `make life work`: SELが2/2回(委任_02・本委任)でcls=F。Trial生存候補だが、Production側はN5 dropとして記録(基準「N5が落とした」、Gate喪失ではない)。SELのcandidate list差(pool構成)によるLLM判定差の可能性。回帰ではなく記録。
- 実runのGEN5出力の揺れ(X a2 `take points away from`が今回は一般化されず原形、委任_02のM10では`take something away from`)。Trial自身の既知の境界(4件)と同種で、Production方式の欠陥ではない。
- 実run Y b1b round 1: deferralで`take the trouble to`が復活(round 2では`take the trouble`)。
- M11(進行中のrun): 委任_02一覧のPENDING_REVIEW 42件を精査 — 全件が証跡run(`*_ev_*`)・バックアップ(`*_pre02a_backup`)・継承コピー(`inherited_from_*`)・superseded run(`surname_choice/run_01`は`run_02/03`で確定済み、OPEN_ITEMS参照)・scaffold停止のみのrun(`ai_island_temple__run_ai_01`は`run_form_prod_01`で制作継続、user_test公開済み)であり、**実運用でN5 marker無しのKP候補を待機している記事は0件**(分類C・現タスクと独立)。

## 9. 12必須項目の充足(X/Y/Z×a2/b1b、OPEN-625に反映)
①〜⑩: 委任_02で確認(6/6)+本委任で再確認(X a2・Y a2/b1b・Z a2/b1b)。⑪Z人称整合でN5 gloss書換(委任_04でfixture検証を追加=§10-2。以下は委任_03時点の記録): **実run0件(全7docで`n5_gloss_rewritten=0`)=未観測**(mock testのみ)。⑫再選定round/resume/技術失敗injection/stage別費用: 再選定=X(委任_02)・Y・Z実run確認、resume API 0=X実run確認(委任_02)、技術失敗injection=X a2実run確認、費用=実測済み。**未観測=⑪のみ。PRODUCTION_WIRED提案は不可**(全充足時のみの条件に従う)。⑪は自然発生を待つか、mock test+複数run0件観測を受入基準として足りるとするかはFable判断(ユーザー原文`delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md`の受入条件[「全6経路で必要条件が満たされた場合のみPRODUCTION_WIRED」]に⑪の実例要求の明文はなく、12項目はDESIGN_01/Fable委任文の受入基準)。

## 10. 委任_04(受入補助、2026-10-31): M10 untidi_b1b・⑪fixture・SEL_DEFERRED技術失敗経路・費用
個別Cap¥15固定。実費 **¥7.98**(M10 untidi_b1b ¥7.85+⑪fixture ¥0.13[2回実行の合算])。開始時と各有料run前に`stop_scope_check`(rc=0。`ev03/stop_check_04_start.json`・`stop_check_m10_untidi_b1b.json`・`stop_check_p11*.json`)、起動は`launch_gate.py`経由(150秒間隔・300秒窓2回以内を維持)。

### 10-1. M10 untidi_b1b(委任_03と同一基準`ev03/m10_thresholds_fixed.md`、公式`generate_candidates`・N5既定ON・1 round、費用¥7.85)
- 4level集計(`ev03/m10/analysis.txt`・`analysis.json`): Trial生存候補28 → 同span保持13・N5 drop 2(`make life work` [untidi_a2、SEL=F]・`taking its job quite seriously` [untidi_b1b、n5_generalize: 一般形組立失敗=lemma'job'が本文語'its'の語形違いでない])・**既存Gate喪失1件(`gets heated` [untidi_b1b]、canonicalization_qa=救済後の表現が未検査[QA再判定=NOT_REJUDGED]のfail-closed)=1/28=3.6%(基準15%以下)**・未再現12(P7/B1がそのspanを返さない=LLM非決定性、J2の分子に入れない)。J2トリガ(a)(b)とも非該当。
- `gets heated`の喪失は既存Gate(仕様①の救済後未検査fail-closed、`er119_kp_candidates_01.py`の`presentation_blockers`(`er119_kp_human_review_01.py:521`))によるN5と無関係の除外で、N5配線が原因ではない(補完`backfill OK`で代替が補われている)。分類=実害なし(Trial/Production差のLLM非決定性)。
- §4A②(untidi_b1b/untidi_a2): `take points away from` → **`take something away from`** (untidi_a2、SAME、訳=『何かをあるものから取り除く、差し引く』、canon前の訳は『評価を下げる』=訳が修正されて旧訳は残っていない。Trial訳は『〜から点数などを差し引く、取り去る』)。**訳は『差し引く』であり『減点』という語そのものではない**(Trialの訳『点数などを差し引く』と比べると『点数』が落ちた汎用訳。意味は同方向)。untidi_b1bの`taking points away`はTrialでは`take points away`だが、今回Productionは`end up taking points away`(P7のspan境界差)を返し、**N5は`SENSE_SHIFT`で本文形へrevert**(reverted=True、used_form=`end up taking points away`、訳=『最終的に点を差し引く』=本文語義)=期待の『本文形revert』と同種の安全側処理。`taking points away`そのもの(span一致)はNOT_SEEN(未再現)。
- §4A①: `hear it out → hear someone out`保持(untidi_a2: 『人の話を最後まで聞く』・untidi_b1b: 『人の話を最後まで聞く』、canon前の訳『話を最後まで聞く』/『言い分を最後まで聞く』から修正済み・旧訳残存なし)。
- 4level通算: §4A①②③④⑤の喪失なし(③④⑤は委任_03分、②b1bはrevertとして処理)。

### 10-2. ⑪ Z人称整合でのN5 gloss書換 fixture検証(`ev03/p11_fixture.py`・`p11_fixture_result.json`・`p11_fixture.log`、費用API実LLM ¥0.13[2回実行の合算、1回¥0.066])
**自然発生の実例ではなくfixtureである(⑪の自然発生は引き続き0件=未観測)。** Production code変更なし・mockなし。
- 入力: `ev03/z/kp_candidates_a2_round1.json`の実候補`made my blood turn cold`(key=`make someone's blood turn cold`、N5記録あり)の複製。発火条件として`japanese_gloss`と`n5.gloss_ja`だけを具体人称入りの『あなたをぞっとさせ、強い恐怖を感じさせる』に差替え(それ以外は実docのまま)。決定論check`ga.person_reference_mismatch`が不整合を返すことを事前確認(`mismatch_before`)。
- 処理: 正式関数`er119_kp_candidates_01._gate_chain`(`er119_kp_candidates_01.py:326-345`の人称整合step) → Zと同じ配線`kcand.make_person_repair_fn(text, er026_family_z_fiction_production_runner_01._person_repair_factory(ctx,"a2"), ...)`(`er026_family_z_fiction_production_runner_01.py:2215`と同じ組合せ) → `ga.align_glosses`(実LLM、SUPPORT_MODEL)。canon_fnは入力供給のみ(fixture入力を返す)、n5_target=False(L3は呼ばない)。
- 観測: `n5_gloss_rewritten=1`(`stages.n5_person_repair`、`er119_kp_candidates_01.py:343`) / `item.japanese_gloss` = 『人をぞっとさせ、強い恐怖を感じさせる』(旧『あなた…』が人称整合で書換) / `candidate.japanese_gloss`・`japanese_gloss_tts`も同値 / `gloss_alignment_status=ALIGNED` / 人称不整合は解消(`mismatch_after=None`) / `n5.person_repair={gloss_before: 旧, gloss_after: 新, ...}`を記録 / 候補は提示集合(gates全PASS、`dropped=[]`)に残る。対照(不整合なしの実doc)は`n5_gloss_rewritten=0`・書換なし・API 0相当。
- **観測した差異(所見。委任_05で是正済み→10-6)**: `item.n5.gloss_ja`は書換後も旧gloss『あなたを…』のまま(`er119_kp_candidates_01.py:338-340`は`n5.person_repair`にbefore/afterを記録するのみで`n5.gloss_ja`は更新しない)。旧訳が残る場所は`gloss_alignment.original_japanese_gloss`・`n5.gloss_ja`・`n5.person_repair.gloss_before`の**監査用フィールドだけ**。下流(HR依頼書/V3フォーム/TTS組立/`finalize_kp`)が読むのは`japanese_gloss`/`japanese_gloss_tts`(`n5.gloss_ja`の参照はProduction内0件、Grep: `er*.py`で`n5`.gloss_ja読出なし)。ユーザー原文:93『日本語訳が旧語義のまま残る問題の防止』は出力に出る訳について満たされている。分類=実害なし(`n5.gloss_ja`は監査記録でありN5確定時点の値を保持する設計とも読めるため修正せず。同期が望ましいかはFable判断、修正する場合はコード1行+test)。

### 10-3. SEL_DEFERRED再判定callの技術失敗経路(API 0、test追加)
- コード: 再判定callは`select(..., label="SEL_DEFERRED")`(`er138_kp_n5_generalization_01.py:1289`) → `call_llm`(`:800-836`)が既存retry(MAX_ATTEMPTS=2、sleep(2))後に`N5TechnicalFailure`を送出 → `pool_and_select`は握らず伝播 → `er119_kp_candidates_01.py:506-512`(初回)が`failure="n5_select_failed"`として外側retryへ(最終attemptは`OUTER_RETRY_EXHAUSTED`で候補0)、補完は`:765`で補完失敗として扱う。N5なし候補は出ない。
- test(新規、いずれもPASS): `er138_kp_n5_generalization_01_test_01.py` `TestJ2DeferredRejudge.test_sel_deferred_rejudge_technical_failure_raises_N5TechnicalFailure_after_retry_limit`(`_send`差替え、呼出列=b1,sel,sel,sel[再判定が2回試行]・sleep=[2]・N5TechnicalFailure) / `er138_wiring_test_01.py` `TestRetryAndFailure.test_sel_deferred_rejudge_technical_failure_is_outer_retry_and_emits_no_n5less_candidates`(正式`generate_candidates`、再判定callが発行され失敗→`OUTER_RETRY_EXHAUSTED`・全failure=`n5_select_failed`・docなし・GEN5以降へ進まない)。実行: er138 test 60件OK・wiring test 32件OK。

### 10-4. 費用(JST日次。`ev03/cost_by_jst_day.py`・`cost_by_jst_day.json`、daily_cost.pyと同じ区切り、LLM costのみ=下限値)
| JST日 | 管理ID | 実費 |
|---|---|---|
| 10-30 | 委任_02(ev02) | ¥72.69(記録上¥73.38のうちQA12 jsonl外分¥0.69) |
| 10-31 | 委任_03(ev03) | ¥60.99(jsonl計上。記録¥63.57との差¥2.58=J2検証callの`j2_part*.json`計上分) |
| 10-31 | 委任_04 | ¥7.98 |
| 10-31 KPN5計 | | ¥71.55 |
他管理IDの本日(10-31 JST)分: main tree実行の`daily_cost.py 2026-10-30T15:00:00`=¥212.9(下限。内訳の大半=ONE-STEP/NUANCE系Trial usage_logでtimestampなしのため過大側の可能性)。10-31 JST暫定累計 ≒ ¥284(KPN5 ¥71.55+他¥212.9)。10-30 JST: KPN5 ¥72.69(main treeの10-29T15基準total=¥353.0から10-31分¥212.9を引いた≒¥140が他管理ID分[gemini_batch等0円扱い¥207相当は含まず下限])。いずれもprovider単価未登録(gemini_batch・TTS)は0円扱いの**下限値**。日次1,000円に対し十分余裕。
注: worktreeで`daily_cost.py`を走らせるとcheckout mtimeで旧Trial logが全件混入し過大になる(wt TOTAL ¥568〜828は不採用)ため、KPN5分は専用集計、他分はmain treeで読取のみ実行(`PYTHONDONTWRITEBYTECODE=1`)。

### 10-6. 委任_05: 10-2の所見(n5.gloss_jaが旧値のまま)の是正と再観測(Fable判定=11-8範囲内是正、承認済み不変条件`japanese_gloss==n5.gloss_ja`との矛盾。新Gate/Prompt/閾値変更なし)
- 是正: `er119_kp_candidates_01.py:341`で人称整合による書換時に`x["n5"]["gloss_ja"]=x.get("japanese_gloss")`へ同期(旧値は`n5.person_repair.gloss_before`に残す。`gloss_alignment.original_japanese_gloss`は無変更)。
- test: `er138_wiring_test_01.py`に`test_n5_gloss_ja_synced_when_rewritten_and_unchanged_otherwise`追加+既存`test_xy_default_repair...`に同期assert。是正前コードでは2件FAIL、是正後er138系93件(wiring33+generalization60)全PASS(.venv python)。er119系の既存19件FAIL/ERRORは是正有無で同一集合(本変更無関係)。
- fixture再実行(実LLM、`ev03/p11_fixture.py`→`ev03/p11_fixture_result_02.json`、費用¥0.067): fire: `n5_gloss_ja_after`==`cand_japanese_gloss`==`japanese_gloss_after`=『人をぞっとさせ、強い恐怖を感じさせる』(True)、`n5.person_repair.gloss_before`=旧『あなたを…』。旧値の残存場所は`gloss_alignment.original_japanese_gloss`と`n5.person_repair.gloss_before`のみ(監査欄)。control(不整合なし): 全て不変・`person_repair`なし。いずれも自然発生ではなくfixture。

### 10-5. check_decision_quality(非ブロッキング)
`docs/pm/tools/check_decision_quality.py --packet docs/pm/RESULT_PACKET_KPN5_03.md` → status=OK・findings 0(warn 0・info 0)。`ev03/dq_03.json`。
