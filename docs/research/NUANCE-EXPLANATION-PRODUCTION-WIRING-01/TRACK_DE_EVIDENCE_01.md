# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C: Track D(runner配線)・Track E(runtime evidence)

作成: 2026-10-29(Sonnet 実行層)。Status: **PRODUCTION_WIRED_PENDING_FABLE**(X/Y/Z runner配線済み・runtime evidence取得済み・Fable受入待ち。`PRODUCTION_WIRED`とは書かない)。
ユーザー正式採用(APPROVED_FOR_PRODUCTION、2026-10-29)原文=`docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md`。設計=`WIRING_DESIGN_01.md`、Track A+C=`TRACK_AC_EVIDENCE_01.md`。

## 1. 結論(目的との適合)

- X・Y・Zの3 runnerが**同一の共有関数**(`er134_nuance_explanation_01`の`n1_stage`/`finalize_stage`/`pool_identity_sha_of`ほか)を呼ぶ形で配線済み。新規flag・既定動作の変更なし。
- 実runのcopy-run(公開済み・本番runは不変)で N0 → N1 → HR(CLI `nuance-select`) → finalize → pages を **X(月)・Y(再配達料)・Z(走れメロス)の3 Family** で実走。採用したlevelの節だけにコーナーが出て、不採用・0件・生成API失敗のlevelは**見出しも空枠も出ない**ことを機械集計で確認。
- 失敗2経路を実run各1回: (M-5)生成API失敗でもページは「ニュアンス無し」で完成(X・Y・Z各で確認)、(R-4)HR未了のままページ入口へ入ると rc=4(X・Y・Z各で確認)。
- 既存run(ニュアンス仕様なし=LEGACY)は生成0・待機0・表示0。Y・Xは実runで**元ページとbyte一致**(Xはpath正規化後)。Zは下記§6。
- 生成API費用(N1の実費)=**合計1.674円**(上限3円以内)。TTS=0円。

## 2. 方式(copy-run)

- 元の完了runを repo外 `C:\Users\tensh\eigo-radio-evidence\NXW02C\` へ複製し(`tools/copy_run_01.py`が`EVIDENCE_COPY_RUN.json`を書く)、runnerが要求する`er0XX_output/`配下へNTFS junction(`tools/junction_01.py`)で接続。元run・公開ページは読み取りのみ(無変更)。
- 既存runはN0(spec発行)の対象外(LEGACY)なので、copy-runにだけ明示コマンド `er119_kp_human_review_cli_01.py nuance-issue-spec`(マーカー必須・実運用runには拒否=Opus M-2)で仕様マークを付与。user-ref=`evidence/user_ref_02C.md`。
- HR(採否)は **KP HR CLIの `nuance-select`**(V3フォームと同じ検証・同じsidecarを書く。testで同一性確認済み)で、評価用の代理確定(`--by sonnet-02C-evidence-human-sim`)。実ユーザーの採否ではない。
- 元run: X=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`(月・公開済み)、Y=`er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f`、Z=`er026_output/family_z_production_e2e_01/melos/run_kcp4_ev_z_01_s23f`(両levelにKP reviewがある完了run)。Zのpagesは元と同じく`pages_s23f`へ出力。
- 抽出ツール(API 0): `tools/extract_nuance_fragment_02c.py`(level節ごとのコーナー個数・空枠・HTML断片sha)、`tools/cmp_html_path_norm_02c.py`(path正規化比較)、`tools/select_via_cli_02c.py`。

## 3. 結果表(X/Y/Z × Std/Adv × 採用/不採用/0件)

HTML断片・集計JSON=`evidence/<label>__summary.json`、`evidence/<label>__<level>__nuance_fragment.html`。状態ファイル(spec/candidate/failed/result/sidecar)=`evidence/state/<run>/<level>/`、要約=`evidence/state_summary.json`、実行ログ=`evidence/logs/`。

| ケース(label) | Std(A2) / Adv(B1)の表示 | ページ全体sha256(先頭16) | 空枠数 |
|---|---|---|---|
| Y_y1(Adv採用・Std不採用) | Std: コーナー無し(見出し0) / Adv: コーナー1個(断片sha 918d1b2fc80d2429、"must have a hard time") | `68a915a1b2a6372c` | 0 |
| Y_y2(Adv不採用・Std採用) | Std: コーナー1個(断片sha 10275ae0107c337e、"maybe that's just my view") / Adv: 無し | `0b5e597750f03c02` | 0 |
| X_nxm1(Std採用・Adv不採用) | Std: 1個(断片sha d1dd72d28ac91dcf、"rock coat") / Adv: 無し | `958ce4ceeb182d5b` | 0 |
| X_nxm2(Std不採用・Adv採用) | Std: 無し / Adv: 1個(断片sha b6c89696d6b4e80f、"Still") | `7f472b58a4cd5886` | 0 |
| Z_nxz3(Std採用・Adv=0件) | Std: 1個(断片sha 84d13d590d051342、"almost") / Adv: 無し(modelが`none`を返却=NO_CANDIDATE) | `709703fb7c4b8be1` | 0 |
| Z_nxz2(Adv不採用・Std=0件) | Std: 無し(NO_CANDIDATE) / Adv: 無し(不採用) | `4a39157c29888620` | 0 |

- 実run(real)で「0件」が自然に発生(Z Std・Z Adv、modelが`none`を返却)。0件levelは見出し・空枠とも出ず、HR待機itemも作られない(`nuance_result.json`=NONE/`model_returned_none`)。
- **不採用(REJECTED)のページ = 生成失敗(NONE)のページ = byte一致**: Z_nxz2(Adv不採用)のページ sha `4a39157c29888620…` は、同じ元から作った失敗状態ページ(Z_nxz1、`failed_technical:api_error`)と完全一致(path正規化比較True)。つまり「採用されなかったlevelはニュアンス機能が無い場合と同一のページ」。
- 重複禁止・文法0件非表示・検証: Y/X/Zいずれも`page_verify`(Y/Z)/player生成が完走。コーナーの個数は節単位(採用した節だけ)。Zは`_verify_part2_outputs`のニュアンス節単位一致も実行済み。
- Zの「Adv採用」は実runでは出なかった(N1の標本でAdvが0件/不採用側)。Z Adv採用は mock E2E(`er134_nuance_z_mock_e2e_test_01.py` T1、Zの実stage経路)で確認。実runでのAdv採用はY・Xで取得。

## 4. 失敗2経路(実run各1回、X/Y/Z各で確認)

- **M-5 生成API失敗 → ページは「ニュアンス無し」で完成**: 不正なAPIキー(`OPENAI_API_KEY=sk-invalid-evidence`、費用0円)で N1 を起動 → 各levelが`FAILED_TECHNICAL`(401 AuthenticationError、`nuance_failed.json`)。その状態で pages を実行 → rc=0で完成し、`nuance_result.json`=`NONE`/`failed_technical:api_error`、コーナー0。Y=元ページとbyte一致(sha `23ad577310ec8043`)、X=player.htmlが元と一致(path正規化後)、Z=Z_nxz1(上記のとおり不採用ページとbyte一致)。ログ=`evidence/logs/{y1_kp_fail,y1_pages_after_fail,x2_scaffold_fail,x2_player_fail,z1_kp_fail,z1_pages_fail}.log`。
- 技術失敗の再試行は明示CLI `nuance-retry`(FAILED_TECHNICAL候補docだけを`nuance_candidate.REGEN_<sha8>.json`へ退避。人手採否の上書き不可)→ 次の制作コマンドでN1が再生成(Y・X・Zとも実走で成功)。
- **R-4 HR未了のままページ入口 → ISSUE rc=4**: N1でCANDIDATEが出た状態(採否未確定)でpagesを実行 → rc=4、`[KP_REVIEW_PENDING] Human Review待ちです: ニュアンス解説`、pagesは未生成(既存ページ不変)。Y: `y1_pages_rc4.log`(rc=4後もページsha `23ad577310ec8043`のまま=不変を確認)、X: `x2_player_rc4.log`、Z: `z3_pages_rc4.log`(X・Zはrc=4とバナーを確認。ページ生成前に停止)。自動で不採用にはならない(SUPPRESSED廃止=人間を上書きしない)。

## 5. 費用

| run | 内容 | 生成API費用 |
|---|---|---|
| Y_y1(→y2はcopy) | N1(Adv 0.2324 + Std 0.1877) | 0.4201円(runner報告 7.9955→8.4156と一致) |
| X_nxm1(→nxm2はcopy) | N1(Adv 0.1947 + Std 0.2602) | 0.4549円(予算ガードcap=累計+3円で通過) |
| Z_nxz1(→nxz2はcopy) | N1(Adv 0.2289 + Std 0.1592) | 0.3881円(13.9498→14.3379と一致) |
| Z_nxz3 | N1(Adv 0.1364 + Std 0.2745) | 0.4109円 |
| 失敗経路(不正キー) | 401で課金0 | 0円 |
| LEGACY/pages/page_verify | LLM呼出なし | 0円 |
| **合計** | | **1.674円(上限3円以内)**。TTS=0円 |

予算ガードが生成呼出の直前に効くことも実走で確認(X: 上限3円で起動 → `[BUDGET_GUARD] cost so far 37.24 > cap 3.0`でSTOP、生成0。cap=累計+3で再実行)。

## 6. LEGACY(ニュアンス仕様なし)は変更なし

- Y: 元runのcopyで`pages,page_verify`を再実行 → ページ sha `23ad577310ec8043…`(55,721 bytes)=元とbyte一致、コーナー0・API 0。
- X: 元(月)のcopyで`--stage player` → path正規化後に元の`player.html`とbyte一致(`cmp_html_path_norm_02c.py`: equal_after_path_norm True、38,039 chars)。
- Z: 元run(2026-10-27生成)のpagesと、現コードで再生成したpagesは**LEGACY/失敗状態でも**差が出る(chunkマーク・文法0件表示の描画差。ニュアンス実装前から存在するHEADまでの別変更に由来)。差がニュアンス実装由来でないことの確認として、**HEAD(ニュアンス実装なし)のコードで同じ元runのcopyを再生成したページ**と本実装のLEGACY相当ページを比較した結果は§7。
- 自動test: 既存run(KP review先行)にhooksが後から有っても生成0・副作用ファイル0・コーナー0(Y/Z mock E2E、`er134_nuance_runner_wiring_test_01.py` DefaultOffIsolation)。

## 7. Z LEGACY: HEADコードとの比較(同一の元runのcopy)

- 手順: HEAD(ニュアンス実装前、commit `0902f3f08`)のdetached worktreeで、同じ元run(`run_kcp4_ev_z_01_s23f`)のcopy `run_nxz0b` を `--stages provision_shell,gate,assemble,pages,page_verify --pages-dir …/pages_s23f` で再生成(1起動、rc=0、費用0。ログ=`evidence/logs/z_baseline_head_pages.log`)。
- 結果: HEADコードのページ sha256 = `4a39157c29888620879df7ac2fc365b89d935d9bb3da164d65cd6b1a4307c323` = 本実装での「生成失敗(NONE)」ページ(Z_nxz1) = 「不採用(REJECTED)+0件」ページ(Z_nxz2)。**byte一致**(path正規化比較True、35,776 chars)。よって元pagesとの差(chunkマーク等)はニュアンス実装由来ではなく、元run生成後に既に入っていた別変更の描画差。ニュアンス機能が出さない場合のページはHEADと同一。
- (参考)HEAD worktreeの実行にはignored dataの`narration` 36 wavを環境差分としてコピーした(本実装の差分ではない)。

## 8. 注意・限界(正直報告)

- HR採否は評価用の代理確定(`sonnet-02C-evidence-human-sim`)。実ユーザーの採否ではない。copy-runは公開・本番ではない。
- 自己起因のRESTART_STORM sentinel 3件(いずれも証跡用copy-run内、本番runではない): (a)Y copy `run_nxw_a`(`pages`を3回短時間に起動)、(b)Z copy `run_nxz1`(kp実生成・rc=4確認・最終pagesを300秒内に3回)。いずれも新規API呼出前に停止(費用0)。STOPは解除・削除せず、元の完了runから**新しいcopy-run(`run_nxw_y1`・`run_nxz3`等)を作り直して**起動間隔を空けて再実施(起動はrun単位に1回ずつ、150秒以上空ける)。copy-run `run_nxw_a`・`run_nxz1`のSTOPは `C:\Users\tensh\eigo-radio-evidence\NXW02C\` 配下に残置(未解除)。
- 元run(Y・X・Z)のcopyで、Y/Z実行には`THEME_DATA_02.json`のsha(LF)がrepoのCRLF checkoutとずれるため、Yの`--theme-package`はmain作業ツリーのLF版を読み取りで参照(書込なし)。環境差でありProduction挙動の変更ではない。
- Xの元run(ai_island_temple/run_form_prod_01)は旧形式でplayerが`BLOCKED_STYLE_PROFILE_GATE`だったため、LEGACY比較に適さず、公開済みの月(moon_shrinking/run_reselect_01)へ切替えた(ai_island側のFAILED_TECHNICAL実走ログは`evidence/logs/x1_scaffold_fail.log`)。

## 9. 公開済み0件ページ

既に公開済みの0件ページ15本(委任文の記載どおり)は**再生成しない**。既存run(本機能導入前にKP reviewが作られたrun)はLEGACYのまま遡及しない(M-2)。今後の新規run(KP review新規作成)からN0が自動発行される。

## 10. テスト結果(origin/main統合後に再実行。pytest -p no:cacheprovider)

- 新規: `er134_nuance_runner_wiring_test_01.py` 29 PASS(N0/N1/finalize/resume/LEGACY/採否保持/重複規則[KP・Word重複NG・文法重複は警告]/0件非表示/CLI=フォームと同結果/runner契約X・Y・Z/既定OFF隔離)、`er134_nuance_y_mock_e2e_test_01.py` 4 PASS(Y実stage経路)、`er134_nuance_z_mock_e2e_test_01.py` 4 PASS(Z実stage経路、約14分)。
- 既存(02A 45・02B 49を含む g4群 535中): 全PASS。関連回帰の失敗は **既知の旧失敗7件のみ**(HEAD `0902f3f08` でも同一集合): `er121_y_highlight_wiring…test_golden_existing_run_without_mark_pages_html_byte_identical`、`er019_x_highlight_wiring…test_golden_existing_run_player_byte_identical_to_before_change`、`er003_kp_general_explanation…ZPart1Tests::test_kp_expression_change_needs_two_step_regeneration_with_hints`、`er119_grammar_review…TestStaticBoundaries::test_public_builder_and_standard_never_call_part2`、`er119_isolation…test_only_x_z_runners_import_er119`、`er128_kp_confirmed_content…TestIsolation::test_abc_and_shared_functions_do_not_import_er128`(OPEN-588系の構造testの陳腐化: er121/er123/er124/er129が許可リスト外)、`er119_z_wiring…test_part1_items_follow_vocab_confirmed_five`(`_part1_items_b1b`属性不在)。
- 群別(通過数): Y g1=147 / X g3=181 / core g4=534 / Z g5=283 / mock E2E 8。環境依存の旧失敗(seedの改行コード・ignoredデータ欠落)は、Windows worktreeのseedをLF化・narration 36 wavをコピーして解消(コミット対象外)。

## 11. 委任_02C-V(Fable受入のための独立検証、2026-10-29、Sonnet)

- **Fable判定(RESTART_STORM sentinel 2件)**: copy-run `run_nxw_a`(Y)・`run_nxz1`(Z)のsentinelは、証跡用の使い捨てcopy-run内で自己起因。API呼出前に停止・費用0(nxz1: cost_log最終12:51:46、STOP作成12:52:34。nxw_a: cost_logは10-27のまま)、sentinelは削除せず残置。本番run・他agentへの影響なし。STOP回避ではないとFableが判定。
- **Z Adv「採用」実run evidence(新copy-run `run_nxz4`、元=`run_kcp4_ev_z_01_s23f`、保存先=`C:\Users\tensh\eigo-radio-evidence\NXW02C\z\run_nxz4`)**: N1でAdv(b1b)=CANDIDATE(0.1842円)・Std(a2)=CANDIDATE(0.2518円)、HR代理確定(`--by sonnet-02CV-evidence-human-sim`)でAdv=adopt・Std=reject → finalize → pages/page_verify rc=0。N1再試行は不要(1回目でAdv候補あり)。
  | ケース | Std/Adv表示 | ページsha256(先頭16) | 断片sha(先頭16) | 空枠数(`count_empty_study_sections`) | N1費用 |
  |---|---|---|---|---|---|
  | Z_nxz4(Adv採用・Std不採用) | Std: 無し / Adv: 1個("even") | `c5275e63b9fa3187` | `1ce3e2e2df3ef4fb` | 0 | 0.4360円(runner ledger 13.9498→14.3859と一致) |
  断片・集計=`evidence/Z_nxz4_adv_adopt_std_reject__*`、状態=`evidence/state/Z_nxz4/`、ログ=`evidence/logs/z4_{kp_real,pages_final}.log`。起動はkp(13:50:25)→pages(13:53:09、間隔164秒)の各1回。TTS=0円。
- 本検証の追加費用=0.4360円(累計N1実費: 1.674+0.436=2.110円)。
- **作業ツリー再実行(origin/main bffc1cb3bをmerge後のメイン作業ツリー、`pytest -p no:cacheprovider`)**: 新規 `er134_nuance_runner_wiring_test_01.py`+`y_mock_e2e` = 33 PASS(29+4)、`z_mock_e2e` = 4 PASS(841秒)、02A `er134_nuance_explanation_01_test_01.py` = 45 PASS、02B系 `er120_nuance_display_test_01.py` 11 + `er128_nuance_hr_test_01.py` 37 = 48 PASS(報告の49との1件差は対象file特定不能、失敗0)。`er121_y_highlight`/`er019_x_highlight`のgolden(byte一致)4件=PASS(02C報告の「既存失敗2件」はworktree seedのCRLF環境差で、メイン作業ツリーでは失敗しない)。構造系の既存失敗(`er119_isolation::test_only_x_z_runners_import_er119`・`er119_z_wiring::test_part1_items_follow_vocab_confirmed_five`・`er119_grammar_review::…never_call_part2`・環境起因`…not_tracked_dirs`)はTRACK_AC_EVIDENCE_01.md:70-76に02C以前から「HEADで同様に失敗」と記録済み。
