# 委任_13(B8) 正式runtime evidence(Family×Level×Role別): 保存run読取再評価(API 0)+承認済みdriverによる最小有料実走(実費¥39.92)

HEAD=統合配線 commit 4475cebf8 の上。Python=`.venv\Scripts\python.exe`。**PRODUCTION_WIREDの判定はFableが行う(本書は判定材料)**。Production code・SSOTは未変更(driver実行と読取のみ)。
証跡dir=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B8_evidence_01/`(下記 `B8/` と略)。

## 0. 結論(先頭)
- **発火と挙動は実走で確認**。承認済みdriver(`tru_ev_run_01.run_case`、正式runner関数・既定profile fx_20261017・STANDARD)の初回Production経路で、X/Y/Z・Std/Adv・LR/Fallbackの発火→`final_adoption`記録→ledger→Gate(警告通過)→三者一致→最終Human報告(赤/青)→混入0を確認(§3)。
- **ただし受入に影響する不具合3件+軽微2件を実走・実Gate照合で発見**(§5)。(D1)(D2)=「正常なFallbackがGateで停止」=UD-3違反、(D3)=「実Chunk境界の⏸が欠落」=USER_02 §4違反。**修正せずFableへ報告**(分類=修正へ進む。次委任案=§5)。
- 未確認(PRODUCTION_WIREDにしない): A/B/C試聴ページの⏸/赤/青(未配線・27-7でA/B/C開発対象外)、X/Yの実LR/Fallback記録を持つ全体ページの赤・青(該当する保存full runが無い/Part2欠落)、Y Std本文Fallback採用・Y chunk(§6)。
- 実費 **¥39.92**(`cost.jpy`実測合計、見積≤¥40内、本委任Cap¥60内)。全起動前に`stop_scope_check` rc=0(`B8/stop_check_*.json`、stop=false)。自動再起動なし(resume1回=委任指示)。

## 1. 読取再評価(API 0、配線後HEADの実関数)
`B8/read_reeval_01.py`→`B8/read_reeval_01.json`(sha 17f3f849)。保存X/Y/Z run×level **295件**(superseded/aborted/smoke除外)に対し実関数を実行: X `m3_assembly_gate(level_dir=)`・Y `y_style_gate`・Z `_z_row_for_clip(ledger_clips=)`(`BWIRE_audit_01/audit_wired_gate_01.py`を再利用)、`er129.build_lr_ledger`、`er132.evaluate_text_parity`(三者一致)、`er131.build_model/render_report`(最終Human報告)、`er131.scan_run_contamination`。エラー0。全体差分監査(`B8/audit_diff_{X,Y,Z}.json`、HEAD再実行、API 0): **旧PASS→新BLOCK(厳格化)=X0/Y0/Z0**、旧BLOCK→新PASS(解除)=X3・Y3・Z1(全て正常LR/Fallbackのevent clip。AI島a2/b1b・B8 X-Adv-14b・Y-Adv-4b(B8+保存)・B8 Y-Std-4c相当・B8 Z-Adv-6)。

| Family | Lv | 正常LR→通過 | 正常Fallback→通過 | 異常/記録欠落/品質NG→停止(実例) | 発動なし |
|---|---|---|---|---|---|
| X | Std | topic_intro(B8 X-Std-2b) | JA title(B8 X-Std-6)・KP_EN `FALLBACK_APPLIED`(B8 X-Std-8)・保存9件 | LR全NG/再TTS失敗→HRQ終端(B8 X-Std-2/5、最終報告に「採用なし」表示)・旧run STYLE_BASE等BLOCK維持 | 旧新UNCHANGED(1510行) |
| X | Adv | comment_1(B8 X-Adv-2)・in_one_line LR+Fallback同居(B8 X-Adv-16)・AI島 `LR_APPLIED`(旧BLOCK→PASS) | preview `FALLBACK_APPLIED`(B8 X-Adv-14b、旧run=BLOCK→新PASS) | KP解説Fallback(B8 X-Adv-7)=**BLOCK(D1、本来は通過すべき)** | 同上 |
| Y | Std | topic_intro LR(B8 Y-Std-1lr)・y_voice LR(B8 Y-Std-4c、Y Gate `LR_APPLIED`) | topic_intro(B8 Y-Std-1fb)・JA title(B8 Y-Std-2b) | 全NG→HRQ終端(B8 Y-Std-1/4b)・旧run y_std_4b記録欠落=BLOCK維持 | 旧新UNCHANGED(693行) |
| Y | Adv | y_voice LR(B8 Y-Adv-4b、Y Gate `LR_APPLIED`、旧BLOCK→新PASS) | (Y Adv単独Fallback実走なし=未観測) | — | 同上 |
| Z | Std | topic_intro_en LR(B8 Z-Std-6、`LR_APPLIED`) | 会話ctx→legacy Fallback(B8 Z-Std-2)=**BLOCK(D2、本来は通過すべき)** | — | 旧新UNCHANGED |
| Z | Adv | topic_intro_en LR(B8 Z-Adv-4)・メロス/猿の手(保存) | KP_EN `FALLBACK_APPLIED`(B8 Z-Adv-6、旧BLOCK→新PASS)・告げ口心臓reselect kp2_en | — | 旧新UNCHANGED(3631行) |

- 集計: `B8/family_level_summary_01.txt`。event clipのGate結果=PASS(警告あり/Gate行なし)が大多数、BLOCKは X Adv KP解説1(D1)・Z Std会話1(D2)・保存の旧run記録欠落2(fail-closed維持)のみ。
- X Gateの対象roleは本文chunk・preview・KP・JA。comment/in_one_line/topic_intro(X)はGate行を持たず、LRはledger・最終Human報告で赤表示される(設計どおり。警告なし通過)。

## 2. 最小有料実走(承認済みdriver、`B8/run_b8_01.py`)
`run_b8_01.py`=case idに`B8-`を付けて新run dirで`tru_ev_run_01.run_case`を呼ぶだけの薄いselector(1 group=1起動。driver・Production code無変更。既存evidence run dirを壊さないため)。追加case(Y-Std-1fb/1lr/4c・X-Std-2b)は既存caseと同一leaf・policyで、planのみ(ng/sub)・title_overrideを既存パターンと同じにした派生。
見積(実走前記録): 波1 ¥25.7・波2 ¥6.2・波3 ¥2.4・波4 ¥6.5(`COST_01.md`実績値ベース)。`--approved-budget-jpy`明示、波ごとに`stop_scope_check` rc=0。
実費(`evidence_runs/B8-*.json` `cost.jpy`): X-Std-2 1.05 / 2b 1.06 / 5 1.89 / 6 0.24 / 8 0.38 / 12 1.19、X-Adv-2 1.15 / 7 0.66 / 14b 1.59 / 16 1.73(kill前1.30+resume分)、Y-Std-1 1.40 / 1fb 0.58 / 1lr 0.86 / 2b 0.25 / 4b 6.37 / 4c 6.53、Y-Adv-4b 9.89、Z-Std-2 1.34 / 6 0.64、Z-Adv-4 0.66 / 6 0.46。**合計39.92**。
実ASRの自然な逸脱で想定外にHRQ終端/LR経路になった実走: X-Std-2(topic→market)・Y-Std-4b(slot1/3自然NG)・Y-Std-4c(slot3自然NG→LR成功)。X-Std-5・Y-Std-1・X-Std-12はcase設計上の終端(LR全NG=E-S2b)/evidence専用chunk gate。

## 3. 実走の確認(a)final_adoption (b)ledger (c)Gate (d)overlay/三者一致 (e)最終Human報告 (f)注記混入
| case(Family/Lv/leaf) | 発火 | (a) | (b) | (c) | (d) | (e) | (f) |
|---|---|---|---|---|---|---|---|
| X-Std-2b(X Std topic_intro) | LR | 記録 | LR採用 | 通過(Gate行なし) | parity OK | 赤(lr=1) | 0 |
| X-Std-6(X Std JA title) | Fallback | 記録 | FB USED | 通過 | OK(not_rendered) | 青 | 0 |
| X-Std-8(X Std KP_EN) | Fallback(ENGLISH_LOCK) | 記録 | FB USED | `FALLBACK_APPLIED` | OK | 青 | 0 |
| X-Adv-2(X Adv comment_1) | LR | 記録 | LR(根拠付き) | 通過(Gate行なし) | OK | 赤 | 0 |
| X-Adv-14b(X Adv preview) | Fallback | 記録 | FB USED | 旧BLOCK→`FALLBACK_APPLIED` | OK | 青 | 0 |
| X-Adv-16(X Adv in_one_line, kill→resume) | LR+Fallback同居 | 記録(depth1,③') | LR+FB | 通過 | OK | 赤+青 | 0 |
| X-Adv-7(X Adv KP解説) | Fallback | 記録 | FB USED | **BLOCK(D1)** | OK | 青 | 0 |
| Y-Std-1lr / Y-Std-4c(topic / y_voice) | LR | 記録 | LR | 4c: Y Gate `LR_APPLIED` | OK | 赤 | 0 |
| Y-Std-1fb / 2b(topic EN / JA title) | Fallback | 記録 | FB USED | 通過 | OK | 青 | 0 |
| Y-Adv-4b(y_voice) | LR | 記録 | LR | 旧BLOCK→`LR_APPLIED` | OK | 赤 | 0 |
| Z-Std-6 / Z-Adv-4(topic_intro_en) | LR(audio_text_deviation) | 記録 | LR | `LR_APPLIED` | OK | 赤 | 0 |
| Z-Adv-6(KP_EN) | Fallback | 記録 | FB USED | 旧BLOCK→`FALLBACK_APPLIED` | OK | 青 | 0 |
| Z-Std-2(会話ctx→legacy) | Fallback | 記録 | FB USED(LEGACY_DIALOGUE) | **BLOCK(D2)** | OK | 青 | 0 |

- (f) 全B8 run×level の`scan_run_contamination`(TTS入力・ASR正解・Style prompt・KP/study・scripts)hit=0。三者一致=全run `OK`。正常LR/Fallbackの`hrq_rows`=0(Human Reviewに入らない)。最終Human報告の赤/青HTML件数=ledgerと一致(`consistent=True`、全run)。
- **resume(実kill→再開)=B8-X-Adv-16**: LR block内のcooldown中に自己kill(`evidence_runs/B8-X-Adv-16.partial_before_kill.json`: sleep 254.97s)→`--resume`: 再TTS1回・LR LLM再実行0(`lr_calls=0`)・追加待機0s(経過521s>180s)・`final_adoption` depth1/ordinal3/③'一貫。LR根拠は`BlockProgress lr.audit`と`recovery.lr_selection_audit_restored`に保存(M-4の保存は実走確認)。**ただしledgerがこの復元根拠を読まず「理由: 記録なし」表示(D4)**。mock側: `er127_tts_block_policy_01_test_01 -k "resume or lr"` 37 PASS。
- test(#10): er129/er130(+mock E2E)/er131/er132/er133/er127_final_adoption=205件中204 PASS+1件(`er132 …known_publication_mismatches`)は並行workerの`user_test`書込中に1回失敗、単独・ファイル全体再実行ともPASS(53件PASS)=環境要因。

## 4. 試聴ページの⏸/赤/青(Family×Level、保存run、`B8/pages_01.py`→`B8/pages_01.json`、scratch出力・run dir/user_test不変)
| Family/Lv | 実run | ⏸(ページ) vs 実chunk plan境界 | 赤 | 濃青 | 判定 |
|---|---|---|---|---|---|
| X Std/Adv | AI島 run_form_prod_01 | **4 vs 5(各Lv、D3)** | 2span+注記1(LR1clip)一致 | 0(Fallbackなし) | ⏸**不一致**・赤一致 |
| X Adv | part2 gpg5_x_01 | 6=6一致(Std planなし0=0) | 0 | 0 | ⏸一致 |
| X(他) | word_gacha・pp_01(Fallback)・part2 r1 | ページ生成不可(Part2 artifact欠落=Part2Stale、旧run由来) | — | — | **未確認** |
| Y Std/Adv | redelivery_fee_stdchunk_ev(scratch複製、wav1本に絞って) | 2=2一致(各Lv) | 0 | 0 | ⏸一致(Y実chunk境界) |
| Y | run_01・gpg5_y_01 | plan chunk<2で0=0 | 0(HR採用で音声=原文) | 0 | 一致。Yの赤/青の全体ページ=**未確認**(LR/Fallback採用のY保存full runなし) |
| Z Std/Adv | 告げ口心臓 reselect_01 | 2=2一致 | 0 | Adv kp2_en 1span+注記1(ledger FB=1一致) | 一致 |
| Z Std | 猿の手 run_sf_prod_01 | plan無し(0) | 2span+注記1(c10 LR)一致 | 0 | 赤一致 |
| Z Adv | メロス run_e2e_02 | plan無し(0) | 2span+注記1(part3_c1 LR)一致 | 0 | 赤一致 |
| A/B/C | er003/er012/er013/er014 保存52 results | 試聴ページ生成器にer133未配線 | — | — | **未確認/未配線**。最終Human報告(er131 legacy)は52件全て生成可・「記録なし」警告帯表示・Fallback有無のみ(adopted fb 1件を青、LR/Styleは「記録なし」)=`B8/abc_legacy_report_01.json` |
- 旧注記: `user_test/family_z_melos_01/advanced.html`・`family_z_monkeys_paw_01/standard.html`に旧「Local Rewrite採用」注記が既公開のまま残存(再生成対象外の旧公開ページ。コード側は撤去済み、ページ再生成時に新注記へ置換される)。

## 5. 発見事項(不具合・旧ルール残存。修正していない。全て「修正へ進む」)
| ID | 内容 | 根拠 | 影響 | 修正案 |
|---|---|---|---|---|
| **D1** | 正常なKP解説Fallback(Adv X/Y/Z共通の`_kp_explanation_unified`③)が`STYLE_NOT_APPROVED_OR_UNKNOWN`でBLOCK | B8-X-Adv-7: 採用take style_sha=b66d3a74(=`repro01.MINIMAL_INSTRUCTION_PREFIX`、`er019_family_x_audio_production_runner_01.py:1316`)。`er130_adopted_take_classifier_01.py:68-70`のallowlist `FALLBACK_MINIMAL_EN`は`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`(dba23e66)のみ | UD-3違反(正常FallbackでBLOCK)。Adv KP解説Fallback発動時に組立停止 | `build_allowlist`の`FALLBACK_MINIMAL_EN`へKP解説③専用のMINIMAL_INSTRUCTION_PREFIX shaを追加+KP_EXPL policy test追加 |
| **D2** | 正常なZ会話ctx→legacy_fallback(③)がBLOCK(`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`+`STYLE_RECORD_MISSING`) | B8-Z-Std-2: take kind=LEGACY_DIALOGUE・style_sha=null・how=final_adoption。`er130:38`の`_DIRECT_KIND_RECORD_HOWS`は`dialogue_tts.final_mode`のみ、`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`(`er063_family_z_audio_01.py:2174`)は`Z_REPLACED`(`er130:441`)に含まれない | UD-3違反。Z Std/Adv会話Fallback発動時にZ組立停止 | Z dialogueの`final_adoption`にstyle_shaまたは直接kind記録を持たせる(または分類核がhow=final_adoption+kind=LEGACY_DIALOGUE+policy third=LEGACY_DIALOGUEを直接kind記録として扱う)+`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`を正常Fallback時に置換対象へ |
| **D3** | LR採用chunkを含む本文で、実Chunk境界の⏸が欠落 | AI島run_form_prod_01 part1: chunk plan本文はLR前(AIs)、表示本文はUD-1 overlay後(AI agents)のため`_find_chunk`が失敗(`CHUNK_TEXT_NOT_FOUND_IN_SCRIPT` boundary 2/2。`er_user_listening_page_common_01.py:125-139`、`er019_family_x_listening_page_01.py:122-125`)。ページ⏸4 vs plan5 | USER_02 §4「実際のChunk境界に⏸」違反(LRを含むchunkの境界が欠落)。Y/Zも同構造(plan付きLR保存runが無く未実証) | chunk本文を表示本文と同じoverlay(LR前/後の両方)で照合する。一致しない場合は⏸を落とさず警告 |
| D4 | resume後のLR「理由」がledgerで「記録なし」 | B8-X-Adv-16: `lr_selection_audit_restored.selected.rationale`は保存済みだが`er129_lr_display_reflection_01.py:683-688`の`_lr_info`が`selection.selected.rationale`/candidate_genのみ参照 | 軽微(Gate停止なし・`LR_REASON_UNAVAILABLE`警告のみ) | `_lr_info`が`lr_selection_audit_restored`を読む |
| D5 | 旧検査残存: `er131.check_page_fhr_contamination`が試聴ページの赤+濃青(`fhr_color_pair`、`er131_final_human_report_01.py:434`)・「切替元Style:」をFHR混入と判定 | scratchページ7件・`user_test`の新候補ページ5件がhit(`scan_public_html`) | 実害なし(er131の検査は未配線)。USER_02で「試聴ページ=報告資料に⏸/赤/青を表示」と決定済みのため旧仕様。配線時に偽STOPの恐れ | 試聴ページ用部品(er133 class `rpt-lr/rpt-fb/rpt-notes`)を除外して検査、「Local Rewrite採用」旧注記の検知は維持 |

- 新規OPEN分類: D1・D2・D3=修正へ進む(UD-3/§4違反、PRODUCTION_WIRED前に必須)/D4・D5=修正へ進む(軽微)。実害なし分類=なし。**判断候補(ユーザー)=なし**(承認済み仕様内の不具合=11-8)。
- 次委任案「委任_14(B8-fix)」: D1〜D5を同一委任で修正(`er130` allowlist・直接kind、`er063`/`er130` Z会話、ページchunk照合、`er129._lr_info`、`er131`検査)+各unit/mock test+該当経路のdriver実走再確認(B8-X-Adv-7・B8-Z-Std-2相当は各¥1.3〜1.5、Cap内)。

## 6. 未観測(実証済みとは書かない)
- Y本文chunk(Y-S-07・Y-B-06)・Y Std本文(y_voice)Fallback採用(実ASRが③で自然NG。B8-Y-Std-4b/4cとも③未採用)・Y Adv単独Fallback・Z legacy会話(Z_DLG_LEGACY)・shell日本語2・shell固定英語3(表外・生成なし)・固定mp3(生成なし)。¥40内に収めるため追加実走なし。
- X Std本文(full_story chunk)のLR/Fallback実走(B8-X-Std-12はchunk gate(evidence専用)のみでevent無し)。
- 試聴ページ: X/Yの実LR/Fallback記録を持つ全体ページの赤/青(Xの該当保存runはPart2欠落でページ生成不可、Yは該当保存full runなし)、A/B/C試聴ページ全て、Z Std Fallbackページ。
- resume: 実kill→再開はX Adv 1件。Y/Zのresumeは実走せずmock。

## 7. 受入12条件(原文§10)×証拠(判定材料。判定はFable)
| # | 条件 | 証拠 | 状態 |
|---|---|---|---|
| 1 | 正式初回Production経路 | B8全case=正式runner関数+承認driver、配線点=BWIRE_INTEGRATED_WIRING_01 §1(`er019 runner:2581,2841`・`er121:1206`・`er026:2552`)。`B8/evidence_runs/B8-*.json`(例 B8-X-Adv-2 sha 8ea656a1) | X/Y/Z実走確認。D1/D2で一部Fallback経路はGate停止 |
| 2 | retry/fallback/regen/resume | B8-X-Adv-16(kill→resume)・X-Adv-14b/Z-Adv-6等 | X Advのresumeのみ実走。他はmock |
| 3 | LR後 本文/TTS/ASR整合 | 全run parity `OK`(`read_reeval_01.json` `parity`) | 確認(D3は⏸のみ。本文一致は成立) |
| 4 | KP/KW/文法/Fact確定内容保護 | AI島k2 overlap T1/T2/T3=PASS(ledger)。B8 runはconfirmed_selection無し=SKIPPED | 実走では**未観測**(unit/er128で担保) |
| 5 | 正常LR/FallbackでHR非入室 | B8正常eventの`hrq_rows`=0、Gate警告通過 | X Std/Adv(KP解説除く)・Y・Z(会話除く)で確認。D1/D2は不成立 |
| 6 | 異常は従来どおり停止 | 旧runのSTYLE_BASE等BLOCK維持・B8 HRQ終端の「採用なし」表示・差分監査 tightened0 | 確認 |
| 7 | 全Role発動記録が最終Human報告へ | B8 全event clipでreport lr/fb=ledger一致。Role=X topic/comment/in_one_line/preview/JA/KP_EN/KP解説・Y topic/y_voice/JA・Z topic_en/会話/KP_EN | 実走済み範囲で確認(§6未観測を除く) |
| 8 | 赤・濃青・注記・区間 | §4(X/Y/Z)。注記=`rpt-notes`。区間=chunk id/範囲 | X/Y/Z一部確認、D3で⏸欠落、A/B/C未 |
| 9 | 注記が本文/TTS/ASR/公開表示に混入しない | scan hit=0(全run)。ページでは`div.script`外に注記 | 確認(旧公開ページに旧注記残存=§4注記) |
| 10 | 必須Regression | §3 test 204/205(+1は再実行PASS) | 本委任範囲では確認 |
| 11 | 正式runtime evidence | 本書§2〜4 | 実施(未観測=§6) |
| 12 | Fable受入・SSOT/Git | 本委任外(Fable) | — |
