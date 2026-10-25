# EVIDENCE_01(KP Human Review + Part 2文法 統合 runtime evidence R1〜R4)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_04 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_04 / 実施日: 2026-10-25(JST 21:03〜23:15) / 実施者: Sonnet(Fable代行operator名`Fable-evidence-operator`でHuman操作を代行)
**PRODUCTION_WIRED判定はFableが行う(本書は判定を書かない)。** 本書は事実と証跡のみ。実費合計 **45.44円**(Cap 150円内)。モデルは全工程 `gpt-6-luna`(OpenAI最新世代の推奨系。旧/下位モデル使用なし。TTSは既存Production構成=gemini-3.8-flash-lite-tts[Aoede]/ASR=gpt-4o-mini-transcribe+Azure)。

## 0. 結果サマリ(正直な到達点)
| run | Family/モード | 到達点 | 完走 |
|---|---|---|---|
| **R1** | X・HRあり(`part2_hr_evidence_01` run_r1) | 候補生成→rc=4(1回)→CLI操作→再開→Part 1[5件]/Part 2 SELECTED/TTS/ASR/assemble/player.html/study_text再実行(API 0)まで | **完走**(18.13円) |
| **R2** | X・HRなし(`--kp-review auto`、run_r2) | 自動確定(KP TOP3/Part 1 TOP5/文法TOP1)・R1のNG skip・Part 1/2生成・a2のTTS/ASRまで | **未完走**: b1b `comment_4`が既存ER-011 Human Review Lockで停止(§6-4)。assemble/player未実施(18.32円) |
| **R3** | Z・HRあり(melos `run_p2_evidence_r3`) | rc=4(KP b1b+文法を1回)→select/NG/文法reselect/reextract/omit→再開→KP finalize→Adv解説→Part 1→Part 2(ZERO `human_rejected_all`)まで | **未完走**: 完成段(TTS〜page_verify)の起動を**私の起動間隔ミス**でRESTART_STORMにし`STOP`が自動作成された(§6-3)。STOPは未削除(2.90円) |
| **R4** | Z・HRなし(melos `run_p2_evidence_r4`、`--kp-review auto`) | 自動確定→TTS差分→gate→assemble→pages→page_verify | **完走**(5.72円)。evidence公開: `user_test/family_z_melos_kphr_evidence_r4/` |
| R0(補助) | Z the_tell_tale_heart(旧run複製) | Step A''が候補0件→待機なしで`NO_CANDIDATE_UNREVIEWED`(ZERO)に確定。旧run(KP HR導入前)は`_kp_legacy_run`で再利用されKP待機は発生しない | 0.37円(KP/文法HRの対象として不適と判断し以後の対象をmelosへ変更) |

対象記事の変更理由(EVIDENCE_PLAN §6どおり): the_tell_tale_heartは(1)旧run複製でKP HRが発動しない(`--regenerate-stage kp_b1b`が必要)(2)Step A''が22段落すべて「特徴なし」で候補0件、のため。the_gift_of_the_magi/the_monkeys_paw/after_twenty_yearsは複製元の`seed_sha256`が現行seedと不一致で起動前にSTOP(`FamilyZProvenanceMismatchStop`、API 0・費用0)。現行seedと一致し本文確定済みの`melos/run_e2e_06`を複製元とした。KP段は新方式(`--regenerate-stage kp_b1b`)で候補生成から再実行(a2は旧run再利用のまま。Zの正式初回run相当の「a2もHR対象」は本evidenceでは未実施=モック統合testで固定済み)。

## 1. 検証7点(ユーザー原文 §8)× 証跡
| # | 検証 | 結果 | 証跡 |
|---|---|---|---|
| 1 | KP TOP8/文法TOP2が保存される | **充足**(X・Z) | R1: `evidence_01/R1/{a2,b1b}/kp_candidates.json`(a2=7件、b1b=8件。≤8)、`R1/study_text/grammar_candidates.json`(候補4件・TOP1/TOP2)。R3: b1b 4件(3 KP+1単語)、文法1件(TOP2なし=候補1件のためTOP2非表示、R-4)。 |
| 2 | Human選定が最終出力へ反映 | **充足**(X完走、Zは確定JSON・Part 2まで) | R1: AI順位(1,2,3)と異なる a2=[4,6,7]、b1b=KP[6,7,8]+vocab[6,7,8,4,5]を`select`。`kp_selection_final.json`・`keywords_canonicalized.json`・TTS結果(`kp1_en.wav`=reach a record high 等)・Part 1・player.htmlの一致を `verify_selection_matches_outputs`がPASS(player stage rc=0)。文法=`grammar-select top2`(理由付き)→`part2_result.json` `selection.source=human_top2`、player.htmlのAdvanced節にだけ「Coffee may be bitter, but we want our detective work to be clear.」(Part 1ブロック直後、Standard節に0)。R3: b1b KP=[2,3,4]をselect(AI順位1,2,3と異なる)。完成段までのZページ反映は未実施(§6-3)。 |
| 3 | Human未レビュー時 KP TOP3/Part 1 TOP5/文法TOP1で継続 | **充足**(X部分、Z完走) | R2: a2/b1b とも `UNREVIEWED_AUTO_ADOPTED`、KP TOP3、b1b vocab TOP5、文法 `selection.source=auto_top1`(TOP1=`The first thing that comes to mind is tariffs.`)、`mode_declaration.source=cli_runner_arg`・`declared_by=Fable`・`user_ref`にユーザー原文§8検証項目3を参照。起動1回・待機なし(rc=4なし)でPart 2まで確定。R4: KP `UNREVIEWED_AUTO_ADOPTED`(TOP3/vocab TOP5)、文法は候補0件のため `NO_CANDIDATE_UNREVIEWED`(待たずに確定、auto宣言があっても自動ZEROではなく正規の0件経路)。`summarize_review_statuses`: R1=reviewed3/auto0、R2=reviewed0/**unreviewed_auto_adopted 3**、R3=reviewed2、R4=reviewed0/auto1/no_candidate1(**UNREVIEWED_AUTO_ADOPTEDとNO_CANDIDATE_UNREVIEWEDはreviewedに数えない**)。 |
| 4 | NGは自動採用されない | **充足**(KP: X・Z、文法: Z) | KP: R1でa2「put in place」・b1b「off the hook」をNG登録→**R2の別run(新support・新候補生成)で `dropped(stage=human_ng)`**(`R2/{a2,b1b}/kp_candidates.json`)。R3で b1b「sentenced him to death」をNG→**R4の新候補生成で `human_ng` として除外**(`R4/b1b/kp_candidates.json`)。文法: R3でTOP1(P11 `Melos struck the man…`)を`reselect`でNG→**同runの再抽出(Step A'' 再実行)でLLMが同じ文を再提案→`filtered_by_ng`に3方式(candidate_id/正規化文/範囲)ヒットして除外**(`R3/study_text/grammar_candidates.json` `filtered_by_ng`)。R4/R2の文法はLLMが当該文を再提案しなかったためR2/R4単独でのskipは未観測(LLM非決定)。 |
| 5 | 再生成・再開でも選定保持 | **充足** | R1再開(launch2): API呼出は`scaffold`3(確定集合のRedundancy QA×2+Adv解説1)・`kp_part1`1・`kp_part1_ja`1・`part2_final`1のみ。**support 0・KP選定(kp_prompt_2/2v) 0・Step A''(`part2_cand`) 0**(`call_counts_by_stage_01.json` R1 launch2_resume)。`--stage study_text`再実行(R1)=全工程`reused:true`・費用差分0(18.13円のまま)。R3: 再開(launch3)でも選定保持(キャッシュ済み候補を再利用、Redundancy QAのみ)。 |
| 6 | 各Familyの正式Production経路で機能 | X・Z=**充足**(runner main経由)、Y=**未配線** | X: `er019_family_x_audio_production_runner_01.py` main、Z: `er026_family_z_fiction_production_runner_01.py` main(いずれも本番の起動引数、モック/テスト用hook無し)。Y: 正式入口なし(別案件FAMILY-Y-PRODUCTION-LAUNCH-01、OPEN-484/520)=PRODUCTION_WIREDにしない。 |
| 7 | 既存Gate・音声構成に意図しない変更なし | **充足**(R1/R4)、R2/R3は途中 | R4: gate/assemble/pages/page_verify rc=0、`page_verify_local.json`は既存melos run_e2e_06と同一指標(plays_ok=全件・http_ge400=[]・console_errors=[]・seek_ok_all=Falseは既存runと同一)、`user_test_page_standard_check_01`(index.html)PASS。非KP clipは再利用(R4 b1b: 45 clip中 新規TTSはKP差分8 call、他はコピー元audio/Master Store再利用)。R1: Master Store再利用を含む(supply chain/play a partのKP clip)。Prompt/Gate/閾値のコード変更0(§5-1の1件の検証修正を除く)。 |

## 2. Part 2 受入条件10項目 × 証跡
| # | 条件 | 状態 | 証跡 |
|---|---|---|---|
| 1 | 承認済み仕様が正式初回Production経路に存在 | 充足 | X/Z runner main経由で実走(上記)。 |
| 2 | retry/fallback/regeneration/resumeと整合 | 充足(部分) | resume=R1/R3、`--stage study_text`再実行=reuse、`--regenerate-stage kp_b1b`→`kp_expl_b1b`(親sha不一致の安全STOP→明示再生成)を実走(R3/R4)。Part 2の`--regenerate-stage part2_b1b`は未実走(mock統合test固定済み)。 |
| 3 | HRの候補提示・操作・確定の反映 | 充足 | R1/R3の統合依頼書`review_request.md`にKP+文法が統合表示、CLI操作→確定JSON→出力。古いsha(短縮16桁)での`grammar-select`は拒否され状態不変(R3で偶発的に実証)。 |
| 4 | HR結果が後続の解説・音声・組立に反映 | X充足/Z部分 | R1: Step Bは確定したTOP2を解説(`part2_final`)、player.htmlへ反映。R4: ZERO固定文面がAdvancedにのみ。R3の音声・組立は未完。 |
| 5 | 必須Regression/Validator/Integration test PASS | 充足 | 本委任で`.venv`の`er119_kp_human_review_outputs_test_01.py`7 PASS(§5-1修正の回帰含む)。他は委任_03で実施済み。 |
| 6 | 正式runtime発火証拠 | X完走(R1)、Z完走(R4)。R2/R3は途中 | 本書。 |
| 7 | actual model_id/routing/Prompt等 | 充足 | §4。 |
| 8 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新 | **OPEN-518/519のみ更新**(CURRENT_SPEC/DECISION_LOGは本委任で変更しない) | OPEN_ITEMS.md。 |
| 9 | Git commit/push | 本委任末で実施 | commit hashは報告参照。 |
| 10 | Fableが独立照合 | Fable | 本書・`evidence_01/`を一次資料として提出。 |

## 3. stage順序・待機・費用タグ(Part 2固有)
- **P2-a stage順序**: X(R1)の`raw_usage_log`時系列(UTC): a2 support/KP候補 → b1b support → **`part2_cand`(12:06:19)** → b1b KP候補(12:06:22〜12:08:40)→ rc=4。TTS(12:12〜)・Part 1(`kp_part1`12:10:28)・`part2_final`(12:10:41)は確定後。Z(R4): `cost_log`時系列 `part2_cand`(12:20:00) → KP候補(12:20:12〜)→ 確定 → 解説(12:26:14)→ `kp_part1`/`kp_part1_ja`(12:26:31/36)→ TTS(12:27〜)。`writer/provenance.json` `downstream_stages`: `part2_cand_b1b`(12:20:00) < `kp_b1b`(12:23:03) < `kp_part1_b1b`(12:26:31) ≤ `part2_b1b`(12:26:36)。
- **P2-b 待機が1回**: R1初回起動はrc=4が1回、標準出力の`[KP_REVIEW_PENDING] … 文法(Part 2) + KP`が1回・`再開コマンド`1つ、統合依頼書`R1/review_request.md`にKP(a2/b1b)+文法。R3も同様(KP b1b+文法)。**R3は文法の再抽出(Human操作)後の再開で再度rc=4(文法のみ)**=仕様どおりの2回目待機(再抽出という追加Human操作の結果で、初回の待機が分裂したものではない)。
- **P2-c 再開で再生成しない**: 上記検証5。Step A'' 0 call(再開時)。
- **P2-d 費用タグ**: X・Zとも `part2_cand`/`part2_final`。Part 2原価(モデル`gpt-6-luna`): R1 = 抽出0.379+解説0.0596=**0.44円/セット**、R2 = 抽出0.8807(parse retry込み2 call)+解説0.0505=**0.93円/セット**、R3(Z)抽出0.31円(再抽出込み・ZERO確定でStep B 0 call)、R4(Z)0.16円(0件)。BUDGET_PLANの約0.4円/セット見積と整合(R2のみparse retryで約2倍)。

## 4. actual model_id / routing / Prompt sha
- `gpt-6-luna`(`response_model`=同。KP候補 call1=`kp_prompt_2`/call2=`kp_prompt_2v`、canonicalization、gloss alignment、Redundancy QA、Part 1、Part 2 Step A''/B すべて)。
- Prompt sha256: `kp_prompt_2`=`a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a`、`kp_prompt_2v`=`e1d5349ce2fda897b74f0350817ced0d7385842c170d066721eb3917f012f5ec`(R1・R4同一)、Step A''(`part2_stepA8`)テンプレート=`51912fe1e2428c347c09969f2f3e8831c73782d5669921e6508c15de8855e15c`、Step Bテンプレート=`59588b5961e88d1be052e9ae5045ed90ca243546d6996027b60336e3083b591c`。`git diff HEAD`でPrompt module(`er119_kp_candidates_01.py`/`er119_kp_prompt_2v_01.py`/`er120_part2_grammar_production_01.py`)の変更0。
- Redundancy QA: 確定集合に再適用(`kp_selection_final.json` `final_redundancy_qa`、再開時にレベルごと1 call)。

## 5. 不具合と最小修正
1. **[修正済み] `verify_selection_matches_outputs`がMaster Store再利用のKP英語recordを不一致と誤判定**(R1 player stageで`KP_SELECTION_OUTPUT_MISMATCH: TTSのKP英語text ['reach a record high', None, None]`、rc=3)。原因: 再利用recordは`text`を持たず、runnerが記録する`canonical_text`(再利用時に`expected_text`一致を検査済み、`er019…runner` L1164)だけを持つ。修正: `er119_kp_human_review_01.py` `verify_selection_matches_outputs`で`text`が無いとき`canonical_text`を比較に使う(両方無い/不一致=従来どおり不一致=fail-closed)。回帰test `test_master_store_reused_tts_record_uses_canonical_text`を`er119_kp_human_review_outputs_test_01.py`へ追加(7 PASS)。分類: 修正へ進む(同一委任で完了)。R1は修正後の`--stage player`でPASS。
2. [evidence設定ミス・製品不具合ではない] X入力copyに`ja_writer/`を含めず、A2の`japanese_title`がSTOPPED→assemble停止(rc=1)。R1/R2とも`ja_writer`をcopyして再実行。
3. [私の運用ミス] RESTART_STORM自行発動(§6-3)。
4. [既存Gate・今回の対象外] R2 b1b `comment_4`のHR Lock(§6-4)。

## 6. 未完了項目と原因(Fable判断材料)
3. **R3の完成段が未実施(RESTART_STORMで`STOP`自動作成)**: R3(melos)の起動は 21:13:52, 21:18:10, 21:23:24, 21:26:06(`kp_expl_b1b`再生成)、21:27:12(完成段)で、**最後の3件が300秒窓内**(21:23:24/21:26:06/21:27:12)。私が「>150秒間隔」を守らず前回起動から約66秒で起動した。`er026_output/.../melos/run_p2_evidence_r3/STOP`(`reason=RESTART_STORM`)は**削除していない**(外部停止ではなく自行発動)。再開に必要な作業: `--clear-stop --reason "..."`(Fable判断)後、(a)`--stage kp --regenerate-stage kp_b1b`(§6-5により再finalize)→(b)`--regenerate-stage kp_expl_b1b`→(c)完成段`--stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify --pages-dir …/run_p2_evidence_r3/pages_evidence`。各起動は150秒以上あける。見積追加費用: 約2〜4円。
4. **R2が既存ER-011 HR Lockで停止**: b1b `comment_4`(TTS)の3 attemptはすべて`ASR PASS/EXACT_MATCH`だが、`faster_whisper`の`disfluency`検査が本文自身の「…what is happening **now. Now,** let's…」を繰り返し(`repeats: now`)としてflaggedし最終STOPPED→`HUMAN_REVIEW_REQUIRED`ロック(`approve_regenerate()`の明示呼出まで0 API)。R1の同文面は通過(TTS音声の揺れ)。KP/Part 2とは無関係の既存音声品質Gate(false NG寄り)であり、私はGate・ロックを回避していない。R2を完走するには `approve_regenerate`(既存の人間承認経路)による`comment_4`再生成が必要。本日残り時間(TTS 1.5時間/run)では新run dirでの全再実行も不可。
5. **R3のKP確定署名が不一致になっている(私の後始末による副作用)**: evidence後に実記事melosのNG registryへ検証用NGを残さないため`unng`/`grammar-unng`を実行したところ、確定済み`kp_human_review.json`の署名が変わり`kp_selection_final.json`と不一致(`KP_FINAL_SIGNATURE_MISMATCH`)。registryは最終的にinactive(melos実記事に影響なし。`z__melos__b1b*.json`の全entry `active:false`)。R3を再開する際は(a)の再finalizeが必要(§6-3)。設計上は「確定後のNG変更→再finalize」であり意図どおりの動作。
6. 事象メモ: Zの`--regenerate-stage kp_b1b`後は親sha不一致で`kp_expl_b1b`が安全STOP(rc=2)し、明示的な`--regenerate-stage kp_expl_b1b`で続行する(R3/R4とも発生。OPERATIONS_01 §3記載どおり。新規の初回runでは発生しない想定)。

## 7. 機能 × Family Status表案(PRODUCTION_WIRED判定はFable)
| 機能 | X | Y | Z |
|---|---|---|---|
| KP Human Review(候補TOP8・select/NG・rc=4・不在宣言) | 実走確認(R1完走、R2途中)。**R2未完走・R1のKP/文法HRあり完走** | **未配線**(正式入口なし。FAMILY-Y-PRODUCTION-LAUNCH-01、OPEN-484/520) | 実走確認(R4完走=auto、R3=HR操作〜finalizeまで。完成段はSTOP中) |
| Part 2 文法 HR(TOP2・top2/reselect/omit/reextract・NG共有registry) | 実走確認(R1: top2→SELECTED完走、R2: auto_top1) | 未配線 | 実走確認(R3: reselect→reextract→omit→ZERO `human_rejected_all`、R4: 候補0件→`NO_CANDIDATE_UNREVIEWED`、ページ固定文面確認) |
| 判定材料の残り | R2のHR Lock解除後の完走(任意: R1がHRあり完走、R2はHRなしの完走が欲しい場合) | — | R3のSTOP解除後の完走(HRありのZ完成段) |

## 8. HR負担の実測(代行operatorの操作数と所要)
- R1: Human操作 = CLI **3コマンド**(a2 select+NG、b1b select+NG、文法top2)、所要は合計 約1秒(CLI実行)。依頼書の閲覧・判断時間はAI代行のため人間の所要時間は**未測定**(候補表は7〜8行/レベル、文法はTOP2の2件のみ。1画面分)。
- R3: Human操作 = CLI **5コマンド**(select+NG、文法reselect[古いsha短縮形で1回拒否→フルshaで成功]、reextract、omit)。
- 待機時間: R1 rc=4まで6分(support+KP候補生成の所要)、再開60秒。R3 rc=4まで約3.7分(旧run複製のためsupport生成なし。Step A''+KP候補生成)。

## 9. 量産単価増分(実測)
- Part 2の増分: **0.44〜0.93円/記事セット**(X: gpt-6-luna 2 call=抽出+解説、parse retryで+0.5円。Zの0件はStep Aのみ0.16〜0.31円)。目標70円/セットに対し約0.6〜1.3%。
- KP HRの増分: 候補生成(kp_prompt_2/2v)は従来の選定と同じ呼出に置換されたため新規増分なし。確定集合のRedundancy QA(1 call/レベル、約0.05〜0.1円)が再開時の追加呼出。基準runとの同条件比較が無く**KP HR単独の増分は未測定**(R1 scaffold 4.09円。比較基準runの実測値は本書では未照合)。
- 実費内訳: R1 18.13円(scaffold 4.09、TTS/ASR/Azure 14.04)、R2 18.32円、R3(melos)2.90円+R0(tell-tale)0.37円、R4 5.72円 = **45.44円**。

## 10. 残課題(新規OPEN候補)
1. R2のHR Lock(既存音声品質Gate、disfluency false positive[本文自身の「now. Now,」])。分類: 実害なし(既存Gateが仕様どおり停止。KP/Part 2とは独立)/ただし完走させるなら人間によるapprove_regenerate要。
2. Z小説でStep A''が0件になりやすい(tell-tale 22段落すべて「特徴なし」、melos R3=1件、R4=0件)。Part 2のZでの有用性に関わる仕様面の観察(分類: ユーザー判断要の可能性[Zへの文法解説の価値/抽出基準]。現時点は仕様どおり固定文面で完走するため実害なし)。
3. 新規の初回Zでa2のHR(KP)が対象になる経路は本evidenceでは未実走(a2は旧run再利用)。モック統合test固定のみ。分類: 修正へ進む場合は次委任でZ新規run相当(旧KPを削除したcopy)で実走。
