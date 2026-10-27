# B4_CLASSIFY_CORE_AND_DIFF_AUDIT_01: 採用take分類核 `classify_adopted_take`(未配線)+旧Gate/新Gate差分監査(委任_08 / Phase B B4、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。設計=W3_UD3_GATE_DESIGN_01(§1,§2,§5,§6,§9)・INTEGRATION_01(F-4/5/6/16)・OPUS_REVIEW_01((b)-1/(b)-5、M-5/M-8/M-9/M-10)。前提=`er129_lr_display_reflection_01.py`。

## 0. 結論
1. `er130_adopted_take_classifier_01.py`(未配線の純module)+`er130_adopted_take_classifier_01_test_01.py`(40件PASS、約6秒)を新設。X M3/Y gate/Z gateの呼出切替は**未実施**(統合配線commitで行う)。どのProductionコードからもimportされない(`test_13_not_imported_by_production`)。既存Productionコード・run dir・SSOT無編集(監査前後でX/Y/Z audit配下3,264ファイルのmanifest hash一致)。
2. 差分監査(M-9): 保存X/Y/Z run **289件**(X 134・Y 31・Z 124)・segment行5,518。**旧BLOCK→新PASS(解除)3件**(全て正常LR: AI島Std/Adv、Y tru_ev_y_adv_4b)、**旧PASS→新BLOCK(厳格化)8件**(全てZ旧run=Style実測照合Gate導入前で「遡及しない」legacy run。内訳§3。**偽BLOCK 0**)。X・Yの厳格化は0。
3. 告げ口心臓Adv `kp2_en`(ENGLISH_LOCK、M-10): 新核=PASS_WITH_WARNING(`FALLBACK_APPLIED`、ENGLISH_LOCK、attempt sha一致)=期待どおり。旧Zは誤同定(K2記録)でPASSしていた。
4. 偽BLOCKを0にするための規則修正: §4。

## 1. 契約と実装
`classify_adopted_take(ledger_clip, policy, allowlist, ctx) -> Classification{verdict: PASS|PASS_WITH_WARNING|BLOCK, reasons[], warnings[], notes[]}`。
- 入力: ledger_clip=`er129.build_lr_ledger`のclip(採用take・LR・parity・T1-T3は**受け取る**。再実装しない=(b)-5)、policy=er127 PROFILES(名前/Profile)、allowlist=`build_allowlist()`、ctx=`ctx_from_entry(entry, take=)`(ASR状態・LR 7 Gate結果・attempt instruction全文等)。
- allowlist(leaf定数をimportして導出): Fallback=EN Minimal(`er033.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`)/JA短文(`er003_v1_n3_01_tts_generate._A2_JA_MINIMAL_INSTRUCTION_PREFIX`)/ENGLISH_LOCK(`repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`、er129定数とも一致)/従来Dialogue(`p9a.ENGLISH_STYLE_PREFIX`)。role Style=X `STYLE_PROFILES`全override+Z `FAMILY_Z_ROLE_STYLE`+既定Dialogue。drift testで固定(`test_12`)。
- 通過(警告記録): Style実測がallowlist内・slotがpolicy許可(Fallbackは③/③'、KP_ENは3,4、policyがLR可なら6)・記録完全(UNKNOWN/RECORD_MISMATCH/NOT_ADOPTEDでない)・ASR PASS系・parity PASS・T1-T3非干渉。`FALLBACK_APPLIED`/`LR_APPLIED`(別種別、重複時は両方)。
- BLOCK理由コード: STYLE_NOT_APPROVED_OR_UNKNOWN / FALLBACK_NOT_ALLOWED_FOR_POLICY / FALLBACK_SLOT_INCONSISTENT / STYLE_RECORD_MISSING / ADOPTED_TAKE_RECORD_INCOMPLETE / RECORD_MISMATCH / NO_ADOPTED_TAKE / ASR_RECORD_MISSING / ADOPTED_TAKE_ASR_NOT_PASS / LR_ON_NON_LR_ROLE / LR_RECORD_INCOMPLETE / LR_NOT_ADOPTABLE / LR_TAKE_INCONSISTENT / TEXT_AUDIO_PARITY_MISMATCH(_UNLOCATABLE, _NOT_PASS=未評価も常にBLOCK) / LR_OVERLAPS_CONFIRMED_CONTENT / POLICY_UNRESOLVED / INPUT_INVALID / CLASSIFIER_EXCEPTION(fail-closed)。
- profile非依存(F-4)。**X M3の`PROFILE_DEFAULT`無条件PASS(`m3_assembly_gate`先頭)との関係**: defaultは現行どおりM3が何も検査しないため新核は呼ばれない(旧runの遡及なし)。非default profile(fx_20261016/17等)の対象role(`_gate_targets`)で新核を呼ぶ。parity(三者一致)はassemble入口Gate側(OPUS (b)-5)で、M3内側には置かない。
- 人間承認take(`human_approval`)はASR要求を既存の個別承認経路(X15 `_approved`)に委ね(注記`HUMAN_APPROVED_TAKE`)、Style照合は維持。
- Fable追加仕様(final_adoption、委任_06 commit d3775dae7): `source=="store_reuse"`はer129が優先順位②で処理し、BlockProgress verified(depth,ordinal)突合(③)に入らない(`er129 resolve_adopted_take`:593が③より前)。**er129は既に除外済みで、er130側の追加吸収は不要**。`test_m5_store_reuse_not_mismatch_and_wav_sha_irrelevant`で、ordinal=null・BlockProgressに対応attemptなし(未closeの②がverified:true)でもRECORD_MISMATCHにならないこと、wav sha変化でBLOCKしないことを固定。

## 2. test(40件)
W3 §6-2の新規15ケース(正常LR/Fallback各種・重複・未承認Style・許可外Fallback・証拠欠落・旧記録・ASR NG・parity・確定内容・非LR role・drift・未配線static grep・fail-closed・回帰)+Opus M-5(HR採用後・Store再利用・旧cache・Z build_entry形・wav sha)+実データ(AI島Std/Adv=PASS_WITH_WARNING、告げ口心臓kp2_en=ENGLISH_LOCK、run不変)。`pytest er130_adopted_take_classifier_01_test_01.py -q` → 40 passed。**er129の`test_u8_no_production_module_imports_er129`は許可リストにer130を追加(1行)。同時進行の委任_09(er131_*)・委任_10(er132_*)がer129をimportするため、同testは現在それらでFAIL(本委任の対象外。各委任側で許可リストへ追加が必要=Fableへ引継ぎ)**。

## 3. 差分監査(M-9)
再現: `.venv\Scripts\python.exe docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B4_diff_audit_01/audit_gate_diff_01.py <out.json> [--scope X,Y,Z]`(読取専用。Yのy_style_gateだけscratch複製上)。結果=同dirの`diff_{X,Y,Z}.json`(segment単位)。旧Gate=X `m3_assembly_gate`(profileは固定記録、無ければdefault=検査なし)/Y `y_style_gate`/Z `_z_row_for_clip`+採択条件(Z1維持)。新=旧違反のうちLR/Fallback/採用Style由来コード(`X_REPLACED`/`Z_REPLACED`)をイベントclip(LR・Fallback証跡あり)に限り分類核へ置換し、他の旧違反は維持。人間承認は新旧同一に効く。

| Family | run | segment行 | 旧Gate対象のイベントseg | 解除 | 厳格化 | 不変 | 旧Gate対象外(情報) |
|---|---|---|---|---|---|---|---|
| X | 134 | 1,397 | 12 | 2 | 0 | 1,355 | 40 |
| Y | 31 | 578 | 18 | 1 | 0 | 573 | 4 |
| Z | 124 | 3,543 | 49 | 0 | 8 | 3,534 | 1 |
| 計 | 289 | 5,518 | 79 | 3 | 8 | 5,462 | 45 |

- **解除3件(全て正常LR)**: X AI島Std(旧=`STD_FALLBACK_USED_OR_UNKNOWN`+`LOCAL_REWRITE_RECOVERY`→`LR_APPLIED`)・AI島Adv(旧=`LOCAL_REWRITE_RECOVERY`→`LR_APPLIED`。parityはer129のoverlay後表示で判定=PASS)・Y `run_tru_ev_y_adv_4b y_voice_1`。Fallback単独の解除は、保存run内で旧BLOCKだったFallback採用が維持項目(`STYLE_BASE_SHA_MISMATCH`等)と併発するか人間承認済みのため0件(単体testで解除を固定)。
- **厳格化8件(全てZ、全てlegacy run=`style_actual`マーカー無しで、旧Gateは「遡及しない」警告のみ。偽BLOCKではなく正当)**: (1)Melos Adv 7件(run_e2e_01×2・run_e2e_02・run_kga3_off_z_01・run_kgcpw_z_01・run_kgcpw_z_e5_a2_01・run_kgcpw_z_e5_b1b_01の`full_story_part*_c*`、LR)=採用StyleがPD8(現行PD06へ置換済みの旧Style)で`STYLE_NOT_APPROVED_OR_UNKNOWN`。run_e2e_01の2件は旧Z記録に`local_rewrite_revalidation`が無く`LR_RECORD_INCOMPLETE`も併発。現行承認Styleと不一致のため停止が従来どおり正しい(再組立する場合のみ影響。公開済みmelos_02はLR 0で対象外=F-10)。(2)Z猿の手Std `full_story_part1_c10`(run_sf_prod_01)=`ADOPTED_TAKE_RECORD_INCOMPLETE`(LR blockのattempt未記録=B2 §5(b)、記録欠落そのもの、区分C実害なし)。原因の内訳=旧Style世代7・記録欠落1。parity未配線・overlap干渉による厳格化は0(parityはer129 overlayで判定済み)。
- 個別: **AI島hr_02**: Std/AdvともBLOCK→PASS_WITH_WARNING(`LR_APPLIED`)。**告げ口心臓Adv kp2_en**: PASS_WITH_WARNING(ENGLISH_LOCK、M-10期待どおり)。**Y E-1(`redelivery_fee/run_01`)**: a2 y_voice_1=BLOCK維持(人間承認takeのStyle sha 9293e0c3「calm, steady news narration」が現行承認集合に無い=`STYLE_NOT_APPROVED_OR_UNKNOWN`。B2 §5(a)のとおり`STYLE_RECORD_CONFLICT`注記付き)、b1b y_voice_1=BLOCK維持(`STYLE_RECORD_MISSING`:人間採用attemptにinstruction非保存でrole Style記録なし)。いずれも旧Gateと同じBLOCK(個別承認X15で救済する従来運用のまま)。**Word Gacha Adv part3**(X `word_gacha__run_wg_01/b1b`): 旧=PASS(UDR #183(a)個別承認)→新=PASS_WITH_WARNING(`LR_APPLIED`、parity PASS=`you've→you have`をoverlay反映後に判定。overlay未反映の現行公開本文ではparity BLOCKになる=UD-1是正と同時配線が前提、F-5)。
- 「旧Gate対象外45」=旧Gateが検査しないrole(topic_intro・in_one_line・japanese_title等)。新核の適用対象を広げるかは配線時の設計判断(区分B)。分類結果は`diff_*.json`に記録(多くは旧trial runの記録欠落=`STYLE_RECORD_MISSING`/`NO_ADOPTED_TAKE`)。

## 4. 規則修正(偽BLOCKを0にした経緯、承認済み品質条件は不変)
| # | 初回の誤判定 | 原因(観測) | 修正 |
|---|---|---|---|
| a | Z厳格化の17件が`NO_ADOPTED_TAKE` | 監査側のZ旧Gate行判定にstatus採択条件(Z1維持項目)が無かった | 監査側z_oldへZ1を追加(比較条件の是正。核は無変更) |
| b | Z JA Fallback 4件(告げ口心臓`comment_2`含む)が`STYLE_RECORD_MISSING` | JA短文Fallbackのattempt記録はroute名`minimal_fallback`のみでshaを保存しない(leafは単一定数のみ送信、`er003_v1_n3_01_tts_generate.py:833,857`) | JA kindかつroute=`minimal_fallback`をStyle識別の直接記録として許可(W3 B-3の解決、**区分B=Fable判断**)。EN Minimalは別Styleが存在し得るためshaを要求(維持) |
| c | Z topic_intro_en等が`POLICY_UNRESOLVED` | `resolve_narrative_role`がZ clip idを解決できない | `policy_for_clip`にZ `clip_kind`対応を追加 |
| d | Z旧Style 7件の理由が`STYLE_RECORD_MISSING`(誤ラベル) | role Style routeだがfrom_style_shaが承認集合外 | `STYLE_NOT_APPROVED_OR_UNKNOWN`へ是正(判定はBLOCKのまま) |

## 5. 撤去予定(W3 §5、本委任では撤去しない。統合配線commitで実施)
`er019:742-743` `LOCAL_REWRITE_RECOVERY`無条件判定(コード名撤去→異常側`LR_*`)・Y `er121:928-929`同/`er019:714,717,720,724,741` `ADV_MINIMAL_FALLBACK`・`STD_FALLBACK_USED_OR_UNKNOWN`・`JA_FALLBACK_USED_OR_UNKNOWN`・`KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN`・`PREVIEW_MINIMAL_FALLBACK`(UNKNOWN側のみ記録欠落コードとして残す)・`er019:529-546` `_final_style_record`のtop-level優先(採用take優先へ)・`er121:905-929` Y本文重複実装(共通核へ置換)・`er063:2133-2140` `fb_phase`併記(`Z_STYLE_FALLBACK_ADOPTED`は許可リスト外のみに意味限定)。既存test更新対象=W3 §6-1(er019/er121/er127/er063の8ファイル)。`er020:836-846`/`er128:1264`「記録のみ」は残置(`confirmed_kp_lr_overlap.json`はGate入力にしない)。残存Grep(現状、本委任で撤去0): `LOCAL_REWRITE_RECOVERY`=`er019:743`/`er121:929`+test。

## 6. 判断候補(`USER_DECISION_REQUIRED`の付与はFable)
- B-3: JA短文Fallbackをroute名で識別(§4b)。**B**(記録形式への適合、leaf単一定数が根拠。品質条件の緩和ではない)。
- 新核の適用範囲(旧Gate対象外45件、topic_intro等の非profile role)。**B**。
- 旧Z Style(PD8等、置換済み)のrun再組立時はBLOCK。**C**(再組立予定なし)。
- er129 testの許可リストへer131/er132追加。**C**(各委任側の機械的修正)。
