# W3_UD3_GATE_DESIGN_01 UD-3「M3/Style Gateの正常LR・Fallback停止解除」設計(LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_03 / Phase A、2026-10-28)

設計のみ。コード・test・SSOT編集0、API 0、JPY 0。ユーザー原文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §5(UD-3)・§7(TTS仕様不変)・§10(受入)。Opus条件A(新構造)レビュー対象。
根拠区分: [配線]=コード読み / [実]=保存データ実測(読取のみ) / [test]=既存test存在確認(再実行せず)。前提資料=`docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W3_M3_LR_HR_01.md`(以下「前回W3」)。

## 0. 結論(先頭)
1. **現行Gateは「正常なLR/Fallback」と「異常なStyle逸脱」を同じ違反コードに混在させている項目が多い**。`LOCAL_REWRITE_RECOVERY`等を消すだけでは、(a)未承認Style・許可外Fallbackの検知が緩む、(b)LRと本文・確定KPの食い違い検知が消える(M3のLR項が事実上唯一の停止点だった)、の2点で原文§5「従来どおり停止」を破る。よって**「項目の削除」ではなく「採用take単位の正常/異常判定核を1つ新設し、X/Y/Zが同じ核を呼ぶ」**設計とする(§2)。
2. **判定核の中心は「最終採用takeのStyle実測値が、承認済みStyle(role Style または 承認済みFallback Style)の許可リストに含まれるか」**。許可リストはleaf側の既存定数から単一箇所で導出する(新Style・新Promptなし。§2-3)。未承認Style・許可外Fallback・記録欠落・記録不一致は従来どおり停止、正常なLR/Fallbackは「警告記録(WARNING)」へ降格して通す。
3. **LRの解除は「本文=TTS入力=ASR正解の一致検査(UD-1/W1の伝搬)」と同時配線が必須**(§8)。現状は本文が旧原稿のままなので(AI島の`AIs`)、一致検査なしでLR項だけ外すと「本文と音声の不一致」(原文§5の停止対象)が無検知で公開される。AI島は新Gate+UD-1/2適用前=停止(TEXT_AUDIO_PARITY)、適用後=通過、という形で「異常→停止/正常→通過」を同一runで実証できる(§7)。
4. **確定KPとLRの重なり(`confirmed_kp_lr_overlap.json`)は現状「記録のみ」**(`er128_kp_confirmed_content_01.py:1264`、`er020_tts_retry_local_rewrite_01.py:836-846`)。M3のLR項が外れると停止点が消えるため、新Gateは当該記録を読み、重なり1件以上を**停止**にする(原文§3・§5の「確定内容干渉=STOP」の実装。Zでは新規の検知追加=UD-1由来、§4)。
5. **発見(委任文の前提の修正)**: 委任文は「Zで新たに停止を増やさない」としたが、**Zは現に③/Style落ちFallback採用で停止している**(`er063_family_z_audio_01.py:2138-2140` `Z_STYLE_ACTUAL_MISMATCH`+`Z_STYLE_FALLBACK_ADOPTED`、test `er063_family_z_style_actual_gate_test_01.py:225-257`)。ZにLR項は無いが、Fallback停止はXと同じ構造で存在する。UD-3(「Family Zや他Familyの相当する品質確認経路も対象」)の解除対象にZ_STYLE_FALLBACK_ADOPTEDが入る。一方Zへ追加される検知はLRのKP重なり・本文音声一致のみ(UD-1由来)。
6. **既存SSOTとの衝突1点**: `CURRENT_SPEC.md:2857`(2026-10-21ユーザー決定「fallback takeの採用はM3 Gateの正規承認記録による個別判断。共通の自動採用ルールは設けない」)は、2026-10-28のUD-3(正常Fallbackの組立停止解除)で**後決定により置換**される。ユーザー原文§5が明示するため再質問不要(区分A)、実装後にSSOT改訂(§5)。

## 1. 現行Gate判定項目の分類表(file:line)
凡例: **維持**=従来どおり停止 / **解除**=正常LR・Fallbackのみを理由とする停止(WARNING記録へ降格) / **分割**=正常と異常が混在、異常側だけ残す。
「採用take」=最終的に音声として採用されたattempt(§2-1の解決関数で決める)。

### 1-1 X `m3_assembly_gate`(`er019_family_x_style_profile_01.py:685-760`)と`evaluate_segment_evidence`(:551-593)、`kp_en_store_key_check`(:598-624)
| # | 違反コード(行) | 現行条件 | 分類 | 新規則(異常側として残すもの) |
|---|---|---|---|---|
| X1 | `NO_SEGMENT_RECORD`(:701) | entry無し | 維持 | 変更なし |
| X2 | `KP_EXPLANATION_STATUS_NOT_OK`(:705)/`KP_JA_MEANING_STATUS_NOT_OK`(:726)/`KP_EN_STATUS_NOT_OK`(:730) | status≠OK | 維持 | 変更なし(音声品質NG) |
| X3 | `STYLE_BASE_SHA_MISMATCH_OR_MISSING`(:563) | `style_profile.style_base_sha256`≠承認sha | 維持 | 変更なし(runnerが渡したbase Styleの記録=Fallbackでも不変。承認Style照合の根幹) |
| X4 | `FINAL_STYLE_RECORD_MISSING`(:583) | 採用Style記録なし | 維持(+解決先変更) | 記録欠落=停止のまま。ただし「記録を探す先」を採用take基準へ(§2-1)。現行`_final_style_record`(:529-546)はtop-level `style_prefix`を優先するため、**Std ③採用時にtop-levelが旧Style(PD06)のままだと③のStyleを見ずに通る**(AI島a2のtop-level=PD06、`fallback_attempts_log`側にFallback sha`dba23e66…`、[実])。採用take基準に直すのは緩和でなく厳格化 |
| X5 | `FINAL_STYLE_SHA_MISMATCH_NO_HINT`(:592)/`FINAL_STYLE_HEAD200_MISMATCH_WITH_HINT`(:588) | 採用Styleがrole Styleと不一致 | **分割** | 採用takeのStyleが「role Style(sha一致/hint付与時はhead200一致)」または「承認済みFallback Style許可リスト(§2-3、hint付与時はstartswith)」→**通過**。どちらにも属さない→`STYLE_NOT_APPROVED_OR_UNKNOWN`で**停止**(未承認・不明Styleへの切替) |
| X6 | `ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`(:712) | Adv top-level `style_prefix`が承認文で始まらない | **分割** | X5と同じ。③採用時はtop-level `style_prefix`がFallback recordになる(`er003_v1_sing01_news_tail_fix.py:210-228`の`_sp_top`)。LR①'採用時はrole Styleのまま[実:AI島b1b] |
| X7 | `ADV_MINIMAL_FALLBACK`(:714) | `instruction_type=="minimal_fallback"` | **分割(解除)** | 正常条件(§2-2)を満たす③/③'は解除し`FALLBACK_APPLIED`警告。`minimal_fallback`だが採用StyleがMinimal許可リスト外・slot不整合・ASR非PASS・記録不完全→`FALLBACK_*`異常で停止 |
| X8 | `STD_FALLBACK_USED_OR_UNKNOWN`(:717) | `fallback_used is not False`(=True/None/欠落) | **分割(解除)** | `fallback_used is True`かつ記録完全かつ正常条件→解除。`None`/欠落(UNKNOWN)は**停止のまま**(記録欠落)。True+許可リスト外→停止 |
| X9 | `JA_FALLBACK_USED_OR_UNKNOWN`(:720)/`KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN`(:724) | 同上(日本語) | **分割(解除)** | X8と同形。許可リスト=JA短文Fallback(`er003_v1_n3_01_tts_generate.py:683` `_A2_JA_MINIMAL_INSTRUCTION_PREFIX`系。Production backendの実送信文は実装時に実測確認=§9 B-3) |
| X10 | `PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED`(:739)/`PREVIEW_MINIMAL_FALLBACK`(:741) | Adv Preview E1 | **分割** | X5/X7と同形 |
| X11 | `KP_EN_STORE_KEY_MISSING/ID_MISMATCH/VERSION_MISMATCH/PATH_INVALID`(:608-619) | Master Audio Store key | 維持 | 変更なし(Style記録・証拠の不一致) |
| X12 | `KP_EN_FALLBACK_USED_BUT_KEY_NOT_FALLBACK_PATH`(:622) | fallback_used=Trueなのにkeyがfallback pathでない | 維持 | 記録不一致=停止 |
| X13 | warning `KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2`(:617) | ENGLISH_LOCK採用 | 既に非ブロッキング | 記録維持。最終Human資料(濃い青)への伝搬は別委任。**KP_ENは現行でENGLISH_LOCKを通している=正常Fallbackの先例** |
| X14 | **`LOCAL_REWRITE_RECOVERY`(:742-743)** | `local_rewrite_recovery`が真なら無条件 | **分割(解除)** | 正常LR(§2-2)→解除し`LR_APPLIED`警告。異常LR→`LR_*`異常コードで停止(§2-2) |
| X15 | 人間承認による解除(:754-757 `_approved`) | `record_human_approval`のcanonical sha一致 | 維持 | 異常側の最終救済として残す(個別承認運用=REGISTER #132/#183は不変)。正常LR/Fallbackは承認不要になる |

### 1-2 Y `y_style_gate`(`er121_family_y_audio_01.py:874-1000`)
| # | 項目(行) | 分類 | 内容 |
|---|---|---|---|
| Y1 | `_y_profile_assert`(:~830-850、`Y_STYLE_PROFILE_*`) | 維持 | 承認profile以外/記録欠落/不一致=BLOCK |
| Y2 | X gate呼出+X専用segment除外(:892-893 `m3_assembly_gate`+`_X_ONLY_SEGMENTS`) | 維持(X核の変更が自動波及) | X1〜X15の変更はYのprofile対象role(Std SUPPORT_JA/Adv PREVIEW/KP)へ自動で効く |
| Y3 | Y本文8segの**重複実装**(:905-929: `evaluate_segment_evidence`+`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`+`ADV_MINIMAL_FALLBACK`+`STD_FALLBACK_USED_OR_UNKNOWN`+`LOCAL_REWRITE_RECOVERY`) | **分割(解除)+共通化** | X5〜X8・X14と同じ分割をYにも書くと二重実装でdrift危険。**Y本文も§2の共通判定核を呼ぶ形へ置換**(Yのchunk展開・coverage・`NO_SEGMENT_RECORD`は維持) |
| Y4 | 日本語role `JA_STYLE_ACTUAL_MISMATCH`/`JA_STYLE_ACTUAL_UNMEASURED`(:950-956) | **分割** | JA ③採用時のtop-level `style_prefix`が短文Styleなら現行は`JA_STYLE_ACTUAL_MISMATCH`でBLOCK(推定[配線]、実測はB-3)。採用takeがJA短文Fallback許可リストなら通過、リスト外/未実測は維持 |
| Y5 | `Y_STYLE_COVERAGE_EMPTY/UNEXPECTED`(:977-978) | 維持 | 検査網羅性。変更なし |
| Y6 | `check_std_slowdown`(:777) | 維持 | 音声品質(減速) |
| Y7 | `reconcile_hr_approvals_for_request`(:~896) | 維持 | 旧HR承認の無効化(Voice/Style不一致) |

### 1-3 Z `run_audio_gate`(`er063_family_z_audio_01.py:1908-1950`)と`z_style_actual_gate`(:2149-2212)・`_z_row_for_clip`(:2071-2146)
| # | 項目(行) | 分類 | 内容 |
|---|---|---|---|
| Z1 | `assert_tts_results_complete`(:1720-1752) | 維持 | 欠落/未採択=STOP。LR採用clipは`audio_text_deviation`を**記録のみ**(:1735-1750)=Zは既にLRで止まらない |
| Z2 | `verify_z_speed_profile`(:1821)/`verify_std_english_slowdown`(:1782)/`check_clip_audio_quality`(:1883-1903 peak/clipping/無音/長さ異常) | 維持 | 音声品質NG |
| Z3 | `Z_STYLE_ENTRY_MISSING`(:2086)/`Z_STYLE_ACTUAL_UNRECORDED`(:2103)/`Z_STYLE_ACTUAL_UNMEASURED`(:2132)/`Z_STYLE_COVERAGE_*`(:2170-2193)/`Z_STYLE_ROLE_TABLE_DRIFT`(:2063-2065)/`Z_STYLE_CHECKED_EMPTY`(:2193) | 維持 | 記録・証拠の欠落 |
| Z4 | **`Z_STYLE_ACTUAL_MISMATCH`(:2138)+`Z_STYLE_FALLBACK_ADOPTED`(:2140)** | **分割(解除)** | 採用takeのStyleが承認Fallback許可リスト(Z narrator=Minimal EN、Z KP_EN=ENGLISH_LOCK、Z JA=JA短文)→解除(`FALLBACK_APPLIED`警告)。リスト外/未実測→停止。現行はFallback採用そのものを`fb_phase`(:2133-2134)で検知して**承認を要求**(test:225-257) |
| Z5 | Dialogue `Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`(:2122)/`Z_DIALOGUE_STYLE_INTENDED_MISMATCH`(:2128) | 維持 | 3回目の従来Dialogue Styleへの切替は**既に許可集合`allowed`に入っている**(:2111-2118)。UD-3で変更なし(Z_DLG_CTXの③=LEGACY_DIALOGUE) |
| Z6 | 共有Gate`asm.verify_episode_audio_validation_gate`(:1946) | 維持(UD-1と連動) | `article_text`は「原稿のまま(canonical)」(:1909-1911)。UD-1で表示本文がLR後になるため、本文=TTS入力=ASR正解の一致検査との接続はW1(委任_01)の設計に従う。本設計は接続点だけ要求(§8) |

### 1-4 HR Lock投入条件・Human Review要求・`pass_with_warning`
| # | 項目(行) | 現状 | 分類 | 内容 |
|---|---|---|---|---|
| H1 | HR queue投入=最終slot NGのみ(`er078_asr_unified_attempt_ctx_01.py:5-12`、`is_last_slot`) | LR/Fallback**成功**では投入されない | 維持(変更不要) | 正常LR/Fallbackが理由のHR Lock・HRQ登録は**既に存在しない**。AI島は`review_lock_state.json`=RESOLVED、HRQ該当0(前回W3 §7)。止めていたのはM3のみ |
| H2 | `register_terminal_hr`(`er127_tts_block_policy_01.py:~570-590`、呼出:~700-708) | LR非RESOLVED(終端NG)で1行 | 維持 | 品質NG・終端NG・LR block最終NGは従来どおりLock+HRQ→Gate BLOCK |
| H3 | M3/Y gateの「人間承認(`record_human_approval`)待ち」=実質のHR要求(AI島OPEN-561) | LR/Fallback採用でBLOCK→人承認待ち | **解除**(正常のみ) | 本設計の主対象。異常側は従来どおり承認待ち |
| H4 | `LR_REWRITTEN`警告(`er078_asr_unified_judge_01.py:63,556-559`、`script_version=="v1"`かつPASS系でPASS_WITH_WARNINGへ) | 採用LR音声に必ず付与 | 維持(記録)・HR非要求 | 非ブロッキング。HRを要求しない扱いは**現状どおり**(H1)。変更不要 |
| H5 | `pass_with_warning_listening_list`(`er078_pass_with_warning_registry_01.py:94-110 derive_listening_list`) | `asr_judgement.state==PASS_WITH_WARNING`の採用音声を事後試聴リストへ(非ブロッキング) | 維持 | 影響なし。**LRは従来どおり載る**(LR_REWRITTEN警告経由)。**Fallback採用はASR判定上の警告が無いため載らない**(現状も同じ)。Fallbackの可視化は新Gateの`FALLBACK_APPLIED`警告(`style_profile_gate.json`/`y_style_profile_gate.json`/Z `style_actual_vs_approved.json`)から最終Human報告資料(別委任)が取る |
| H6 | HR採用経路(`er121_e1_hr_adopt_r0_01.py:146`、`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG` `er020:852-880`) | 人間が原文音声へ戻した場合のフラグ | 維持 | 該当entryは正常LR扱いにしない(音声が原文=LR前提のparity判定対象外、§2-2のLR判定から除外) |

## 2. 設計の核: 採用take単位の「正常/異常」判定(共通核)

### 2-1 構造(新コード経路。leaf・TTS・ASR・Voice・速度は不変)
新規純関数`classify_adopted_take(entry, role, level, profile_id, policy) -> {normal_lr, normal_fallback, adopted_style:{sha,len,head200,source}, abnormal:[理由コード], warnings:[{kind:"LR_APPLIED"|"FALLBACK_APPLIED",...}]}`を`er019_family_x_style_profile_01.py`(承認Style・`evaluate_segment_evidence`の所在)へ1つ置き、X `m3_assembly_gate`・Y `y_style_gate`(本文・JA・Preview・KP)・Z `_z_row_for_clip`が**同じ関数**を呼ぶ。API 0・副作用0・entryは読むだけ。
- **採用takeの解決順(最重要)**: (1)LR採用entry(`local_rewrite_recovery.status=="RESOLVED_BY_LOCAL_REWRITE"`)は`local_rewrite_recovery.retts_result`(LR block採用take)、(2)LRなしでFallback採用は`fallback_attempts_log`の最後の`status=OK`/verified take、(3)それ以外は標準段の最後のtake。Z形entryは既存`build_style_actual_record`(`er063:~1277-1320`)の「採用attempt優先→top-level」順を踏襲し、**同じ順序をX/Y側にも適用**(top-levelの`fallback_used`/`style_prefix`は補助情報に降格。理由=§1 X4・前回W3§4: Stdのtop-level `fallback_used`は旧記録でLR①'採用でもTrue[OPEN-564。記録は`er003_v1_crosslevel_audio_02_common.py:473-481`で修正済みだが保存済みAI島は旧記録]。
- 読取キーはすべて既存(新規記録キーの追加なし、AI島で実測済み[実]): `asr_judgement.state/slot/script_version/warnings`、`attempts_log[*].style_prefix(record{sha256,len,head200})/instruction_type/instruction_label`、`fallback_attempts_log[*]`、`local_rewrite_recovery.selection.selected.{all_seven_gates_pass,adoptable,changed_span_before/after,rewritten_segment}`、`local_rewrite_recovery.retts_result.{fallback_used,asr_judgement.slot}`。

### 2-2 「正常なLR」「正常なFallback」の定義
**正常Fallback**(すべて真):
1. policyがFallback可能(`er127 PROFILES`の`third_style` in {FALLBACK_MINIMAL_EN, FALLBACK_MINIMAL_JA, ENGLISH_LOCK, LEGACY_DIALOGUE}=`EN_LR_STD/ADV, JA_STD, KP_EN, KP_EXPL, Z_DLG_CTX`、`er127:108-123`)。`SHELL_EN/Z_DLG_LEGACY`(third_style=SAME)・`NO_TTS`でFallback採用が現れたら**異常**(許可されていないFallback方式)。
2. 採用takeの実測Style(sha/head200)が、そのpolicyの`third_style`に対応する**承認済みFallback Style許可リスト**(§2-3)に属する(hint付与時はstartswith+len)。
3. 採用takeが許可slotのFallback位置: 元block=ordinal 3、LR block=ordinal 6(KP_ENはENGLISH_LOCK段=3,4)。`asr_judgement.slot`で確認(slot・attempt記録欠落→異常=記録欠落)。**Styleが変わらない再試行はFallbackと判定/表示しない**(原文§6B。slot1,2でStyle=role StyleならFallbackではない)。
4. 記録が完全: Style名(`instruction_label`/sha)・attempt番号・採用フラグ(`fallback_used`)・`asr_judgement`が存在し互いに矛盾しない。
5. 採用takeのASR判定が`PASS`/`PASS_WITH_WARNING`(`status==OK`)。それ以外=音声品質NG=停止。
6. 既存の音声品質Gate(減速・duration・clipping等、X/Y/Z側の各検査)がPASS(本Gateでは緩めず並走して維持)。

**正常LR**(すべて真):
1. policyが`lr=True`(`EN_LR_STD/ADV`のみ、`er127:108-123`。LR範囲不変)。**LR記録が`lr=False`のrole(JA/KP/Zセリフ)に現れたら異常**(`LR_ON_NON_LR_ROLE`)。
2. `local_rewrite_recovery.status=="RESOLVED_BY_LOCAL_REWRITE"`、`selection.selected.all_seven_gates_pass==true`かつ`adoptable==true`(LR 7 Gate+Natural English QA、`er020:625-628,746-749`)、LR block再入なし(slot 4〜6のみ)。
3. LR採用takeのStyleが**元のrole Style(①'②')または承認Fallback Style(③')**(正常Fallbackの2.と同じ許可判定)。
4. `local_rewrite_recovery.retts_result.asr_judgement.state`が`PASS`/`PASS_WITH_WARNING`、`script_version=="v1"`(ASR正解=LR後の送信文、`resolve_expected_text_after_local_rewrite` `er020:855-885`)。
5. **本文=TTS入力=ASR正解の一致(UD-1)**: 表示本文(最終)の該当区間 == entry送信文(`text`/`selected.rewritten_segment`) == ASR期待文。LR前後・変更語句・理由・対象区間が記録されている(`canonical_text_before_local_rewrite`、`changed_span_before/after`)。W1(委任_01)の「最終表示本文」記録をキーに照合(インターフェースだけ本設計で要求=§8)。
6. **確定内容非干渉**: `confirmed_kp_lr_overlap.json`に当該segmentの重なりイベントが無い(確定KP・KW・文法・訳・Fact・原作保持=`er128` G0-G4、`lr_overlap` `er128:1236`)。重なり1件以上→`LR_OVERLAPS_CONFIRMED_CONTENT`で停止(`USER_DECISION_REQUIRED`扱い、原文§3)。確定レコードが無い記事は検査対象外。
7. 人間承認でLR音声が原文へ戻されたentry(`local_rewrite_audio_superseded_by_human_approval`)は正常LR判定の対象外(音声=原文、既存の承認経路)。

**異常コード(停止、新設)**: `STYLE_NOT_APPROVED_OR_UNKNOWN`(未承認・不明Style)/`FALLBACK_NOT_ALLOWED_FOR_POLICY`(許可されていないFallback方式)/`FALLBACK_STYLE_RECORD_INCOMPLETE`/`FALLBACK_SLOT_INCONSISTENT`/`LR_RECORD_INCOMPLETE`/`LR_NOT_ADOPTABLE`/`LR_ON_NON_LR_ROLE`/`LR_OVERLAPS_CONFIRMED_CONTENT`/`TEXT_AUDIO_PARITY_MISMATCH`/`ADOPTED_TAKE_ASR_NOT_PASS`。既存コード(§1の維持項目)は名前を変えず残す。
**安全側の原則**: 上記のいずれかを検証できない(キー欠落・解決不能)ときは必ず異常側(現行どおりBLOCK)。**判定核が例外を投げたら通さずBLOCK**(fail-closed)。

### 2-3 「未承認・不明Style」「許可されていないFallback方式」を検知し続ける所在
- **承認済みStyle許可リストの単一ソース**: `APPROVED_STYLE_REGISTRY`(新規、`er019_family_x_style_profile_01.py`)。(a)role Style=既存`get_profile(profile_id)["overrides"][role]`(sha)、(b)Fallback Style=leaf定数を**importして導出**(コピー禁止): EN Minimal=`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`("natural, clear, conversational"、30字、sha先頭`dba23e66`[実:AI島a2 `fallback_attempts_log`・paycheck run_pp_01])、JA短文=`er003_v1_n3_01_tts_generate._A2_JA_MINIMAL_INSTRUCTION_PREFIX`系、ENGLISH_LOCK=`er003_v1_repro01_main_generate.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(KP_ENはStore key`instruction_path=="english_lock_fallback"`でも二重確認、`er019:598-620`)、LEGACY_DIALOGUE=`p9a.ENGLISH_STYLE_PREFIX`(Zの既存`default_dialogue_sha`と同値)。
- 検知の本体=「採用takeのStyle実測shaが、(policy.third_style×slotで決まる許可集合)に含まれるか」。含まれない=`STYLE_NOT_APPROVED_OR_UNKNOWN`。**照合対象は意図値ではなく送信Styleの実測**(Y/Zが既にやっている方式、`er121:950-956`・`er063:2132`)。
- **driftガード**: Y/Zが既に使う方式(`Y_APPROVED_STYLE_PROFILE`のdrift test `er121:804`、`_z_role_table_drift` `er063:2063`)に倣い、`APPROVED_STYLE_REGISTRY`と`er127.PROFILES.third_style`・leaf定数の完全一致test(いずれかが変わればGateが落ちる=Style変更時に承認判断を強制)。
- 不変であるもの(原文§5末尾・§7): TTS試行回数・待機・Fallback Style・LR範囲・ASR判定基準・Voice/速度・確定内容保護。本設計はこれらを読むだけで書換えない。

## 3. HR Lock/Human Review要求の変更点(まとめ)
| 事象 | 現行 | 新 |
|---|---|---|
| 正常LRのみ(ASR PASS系・正常条件) | M3/Y gate BLOCK→人承認待ち(AI島=HR待ち) | **通過**。`LR_APPLIED`警告を記録(gate json+stdout `[WARN]`)。HR Lock・HRQ登録は元々なし(H1) |
| 正常Fallbackのみ | X Std/Adv/JA/Previewは BLOCK、ZもBLOCK(承認要)、X/Y KP ENGLISH_LOCKだけ通過 | **通過**。`FALLBACK_APPLIED`警告(Style名・slot・本文範囲=最終Human資料の入力) |
| 正常LR+正常Fallback重複 | BLOCK | 通過。両警告を**別種別**で記録(原文§6C。実行履歴=attempts、最終採用状態=adopted_styleを別フィールドに) |
| 未承認Style/許可外Fallback/記録欠落・不一致 | BLOCK | **BLOCK(不変)**。人間承認(`record_human_approval`)で個別救済は従来どおり |
| ASR NG・終端NG・三者不一致 | Lock+HRQ+BLOCK | 不変 |
| LR×確定KP重なり・本文音声不一致・LR非LRrole | (X/Y: LR項で一律BLOCK、Z: 未検知) | **BLOCK**(新コード、X/Y/Z共通) |
- `LR_REWRITTEN`(PASS_WITH_WARNING)は記録として維持しHRを要求しない(現状どおり。H4)。`pass_with_warning_listening_list`は無改修(H5)。
- 警告の出力先: 既存`m3_assembly_gate`の`warnings`(:759、runnerの`[WARN][STYLE-PROFILE][M3]`stdout、`er019_family_x_audio_production_runner_01.py:~2470`)を構造化(`{segment, warning, style_label, slot, role, changed_span?}`)。Yは`y_style_profile_gate.json`に`y_body_warnings`を追加、Zは`style_actual_vs_approved.json`の`warnings`へ。**警告は隠蔽でなく可視化**(原文§12末尾)。

## 4. Family X/Y/Z整合表と他Familyの扱い
| 判定 | X(M3) | Y(`y_style_gate`) | Z(`z_style_actual_gate`+`run_audio_gate`) | 同じ基準か |
|---|---|---|---|---|
| 採用takeStyle照合 | 共通核 | 共通核(本文8を重複実装から置換) | 共通核(`_z_row_for_clip`が呼ぶ) | **同一に統一** |
| 正常Fallback | 通過 | 通過 | 通過(**現行は停止**=Z4) | 同一(Zが緩む側) |
| 正常LR | 通過(現行停止) | 通過(現行停止) | 通過(現行も通過) | 同一 |
| 未承認Style/許可外Fallback | 停止 | 停止 | 停止 | 同一 |
| ENGLISH_LOCK(KP_EN) | 通過(現行から) | 通過(現行から) | 通過(**現行は推定停止**、実測はB-3) | 同一 |
| LR×確定KP重なり | 停止(新規。従来はLR項で一律停止) | 停止(同) | 停止(**新規の検知追加**、UD-1/§5由来) | 同一 |
| 本文=TTS=ASR一致 | 検査(UD-1) | 検査 | 検査(`article_text`の扱い=W1連動) | 同一 |
| 原作保持違反 | LR 7 Gate・locality | 同 | **Validator撤廃済(2026-10-12ユーザー決定③、`CURRENT_SPEC.md:1622`)。専用の機械検知は従来から無い** | 下記注 |
- 注(Zの原作保持): 原文§5は「LRによる原作保持違反」を停止対象とするが、Zの専用検査は2026-10-12のユーザー決定で撤廃済み。**引下げではなく従来からの状態**。新Validatorは作らない(新仕様=承認事項)。Zは(i)LR 7 Gate(meaning/role/fact/context/natural、`er020:625-628`)全PASS、(ii)局所性(`locality_check`)、(iii)確定KP非干渉、(iv)最終Human資料の赤色表示で人が把握、を現行の防御線とする旨をSSOTへ明記(区分A、既判断=1622)。
- **Family A/B/C**: 方式置換禁止=本Gate変更の**対象外**。根拠: `m3_assembly_gate`はXの`stage_assemble`(`er019_family_x_audio_production_runner_01.py:2473`)、Yの`y_style_gate`、Z`run_audio_gate`からのみ呼ばれ、A/B/Cのrunner(`er012_b_family_production_runner_01.py`・`er013_family_c_production_runner_01.py`)は呼ばない。`er127.unified_flow_active()`(scope X/Y/Zのみ、`er127:~124`)=A/B/Cは常にFalse。A/B/Cへ適用されるのは最終Human報告仕様(表示のみ、別委任)。
- **適用profile範囲**(B-2): `m3_assembly_gate`は`coffee_p8`/`n01`/`fx_20261016`/`fx_20261017`等の全非defaultで共通。判定核はprofile非依存(許可リスト=leaf定数)のため**全profileで有効にする**案を推奨。旧profileのLR採用はStyle脱落記録(OPEN-312時代)が許可リスト外となり従来どおり停止する(後退なし)。`er057_*`/`er071_*`のoffline evidence scriptは凍結扱い(再実行しない)。

## 5. 撤去・残置(Charter 8原則「旧ルール・旧検査の撤去要否」)
| 対象 | 方針 |
|---|---|
| `er019:742-743` `LOCAL_REWRITE_RECOVERY`の無条件判定 | **置換**(分割)。コード名`LOCAL_REWRITE_RECOVERY`は撤去、異常側は`LR_*`へ。Y`er121:928-929`も同様 |
| `er019:714,717,720,724,741` `ADV_MINIMAL_FALLBACK`/`STD_FALLBACK_USED_OR_UNKNOWN`/`JA_FALLBACK_USED_OR_UNKNOWN`/`KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN`/`PREVIEW_MINIMAL_FALLBACK` | **分割置換**。UNKNOWN(None/欠落)側のみ`FALLBACK_STYLE_RECORD_INCOMPLETE`として残す |
| `er019:529-546` `_final_style_record`のtop-level優先 | 採用take優先へ変更(厳格化) |
| `er121:905-929`のY本文重複実装 | 共通核へ置換(撤去) |
| `er063:2133-2140` `fb_phase`による`Z_STYLE_FALLBACK_ADOPTED`併記 | 許可リスト判定へ置換(`Z_STYLE_FALLBACK_ADOPTED`は「許可リスト外のFallback採用」のみに意味を限定) |
| `er020:836-846` `_note_confirmed_kp_overlap`/`er128:1264` `note_lr_fired`「記録のみ」 | **残置+読取Gate追加**。LR自体は止めない(docstring不変)。Gateが停止判断をする旨をコメント追記 |
| SSOT記述 | `CURRENT_SPEC.md:2857`(個別承認のみ・共通自動採用なし)・`:3168`(Gate無変更)・`:3170`(③/LR採用はBLOCK対象)・`:3178`(M3 LR項の注記)、`OPEN_ITEMS.md` OPEN-312(M3 LR項の根拠)・OPEN-561/563(AI島HR待ち)・OPEN-564(Std記録)の整合改訂と、DECISION_LOGへのUD-3追記。**Phase Bの実装受入後にFableが実施**(本Phaseは編集しない) |
| test | §6。旧コードを前提とするassertは更新対象(Dangling防止) |
| 実装後Grep確認 | `LOCAL_REWRITE_RECOVERY`・`STD_FALLBACK_USED_OR_UNKNOWN`・`ADV_MINIMAL_FALLBACK`・`Z_STYLE_FALLBACK_ADOPTED`の残存0または新意味のみ、を全`*.py`/docs/SSOTでGrep |

## 6. test計画(既存の更新+新規)
### 6-1 既存で変更が必要なケース(旧コード・旧挙動をassert)
- `er019_family_x_style_profile_01_test_01.py:410,412,414,415,424-431,794-806`(`ADV_MINIMAL_FALLBACK`/`LOCAL_REWRITE_RECOVERY`/`STD_FALLBACK_USED_OR_UNKNOWN`/`JA_FALLBACK_USED_OR_UNKNOWN`)。**ポイント**: 既存は`local_rewrite_recovery={"x":1}`・`fallback_used=True`の**最小合成entry**でBLOCKを検証。新核では合成entryは「記録不完全」=異常のままBLOCKだが理由コードが変わる→assertする理由コードを更新。`:424` `test_lr_adoption_blocks_even_when_fallback_used_false_open564`は「LR採用=BLOCK」を明示assertしており、**正常LR完全記録の入力では期待値反転(PASS)**が必要。
- `er019_family_x_s3_wiring_01_test_01.py:222,227,234`、`er019_family_x_fx_20261016_wiring_01_test_01.py:379`、`er019_family_x_style_profile_migration_01_test_01.py:88`(`PREVIEW_MINIMAL_FALLBACK`)、`er117_x_chunk_wiring_test_01.py:276`(chunk ADV_MINIMAL_FALLBACK)。
- `er121_family_y_style_profile_test_01.py:369,371,397`。
- `er127_tts_block_policy_01_test_01.py:1157,1166,1170,1185-1186`(L1〜L4実generate+合成judge→`m3_assembly_gate`。`test_lr_adoption_is_detected`/`test_std_third_and_lr_are_detected`は正常採用=PASSへ反転、`test_first_pass_std_has_no_...`は維持)。
- `er063_family_z_style_actual_gate_test_01.py:225-257`(`test_style_dropping_fallback_adopted_requires_human_approval`: 許可リスト内Fallbackは承認不要でPASS、許可リスト外sha(別文字列)は`Z_STYLE_ACTUAL_MISMATCH`のまま人間承認要、の2ケースへ分割)。`:259`(fallback_phase+approved Style不変=PASS)は維持。
### 6-2 新規ケース(X Std/X Adv/Y/Zで同一形式。判定核の単体+各gate結合)
1. 正常LR(role Style①'採用・7Gate PASS・ASR PASS_WITH_WARNING・parity OK・KP重なり0)→**PASS**+`LR_APPLIED`警告(AI島の実entryコピーをfixture)。
2. 正常Fallback ③(EN Minimal許可リスト内、slot3)→PASS+`FALLBACK_APPLIED`。JA ③、KP ENGLISH_LOCK、Z Dialogue ctx→従来Dialogue、LR block内③'(slot6)も各1件。
3. 正常LR+正常Fallback(LR block③')重複→PASS+2警告(種別が別)。
4. **未承認Style切替**(採用takeのStyle shaを許可外へ改変/Minimalが非Fallback slot1,2で出現)→BLOCK `STYLE_NOT_APPROVED_OR_UNKNOWN`/`FALLBACK_SLOT_INCONSISTENT`。
5. **許可されていないFallback方式**(`SHELL_EN`/`Z_DLG_LEGACY`/JA roleにEN Minimal)→BLOCK `FALLBACK_NOT_ALLOWED_FOR_POLICY`。
6. **証拠欠落**(`asr_judgement`・Style record・`instruction_label`・`fallback_attempts_log`の各欠落)→BLOCK(各1ケース)。top-level `fallback_used`が`None`→BLOCK。
7. **記録不一致**(top-level `fallback_used=True`だが採用takeはrole Style=OPEN-564旧記録)→B-4で方針確定後にtest化(推奨: 採用take記録が完全なら警告化、不完全ならBLOCK)。
8. **ASR NG**(採用takeのstate=NG、status≠OK)→BLOCK。
9. **本文音声不一致**(表示本文のLR区間が旧文のまま)→BLOCK `TEXT_AUDIO_PARITY_MISMATCH`。UD-1配線前は常にこの結果になることをtest化(§8の順序保証)。
10. **LR×確定KP重なり**(`confirmed_kp_lr_overlap.json`に1イベント)→BLOCK。確定レコードなし→対象外でPASS。
11. LRが`lr=False` role(JA/KP/Zセリフ)に出現→BLOCK `LR_ON_NON_LR_ROLE`。
12. drift test: `APPROVED_STYLE_REGISTRY`が`PROFILES.third_style`・leaf定数と一致。
13. 新flagは設けない(本件はAPPROVED_FOR_PRODUCTION・既存Gateの分割)ためDefaultOffIsolation不要。代わりに**A/B/C runnerから判定核の呼出が0**であることのstatic grep test。
14. 判定核が例外を投げる/entryが想定外型のとき通さない(fail-closed)。
15. 回帰: 既存の維持項目(X1〜X3,X11,X12、Y1,Y5,Y6、Z1〜Z3,Z5)は変更前と同じ入力で同じ結果。

## 7. runtime evidence計画(有料0、保存済みrunの読取専用再評価)
1. **AI島(X、`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/{a2,b1b}`、M3 BLOCK実績=OPEN-561/563)**: `tts_generation_results.json`を**読むだけ**(コピーはscratchpad、書込0)で新Gateを評価。期待: (i)UD-1/2適用前=`TEXT_AUDIO_PARITY_MISMATCH`でBLOCK(本文`AIs`≠音声`AI agents`/`AI systems`。LR自体は正常だがparity不成立=「異常→停止」の実証)、(ii)記録上の本文をUD-2後の英文に置換した模擬(in-memory)=PASS+`LR_APPLIED`(Std・Adv各1警告、`full_story_part1_k2`)。前回W3 §5の模擬(LR項除去でAdvはPASS・Stdは旧`_merge`偽陽性)との差=採用take基準でStdも偽陽性なし(retts_result.fallback_used=False、slot4 [実])。
2. **Y E-1(`er121_output/family_y_production_01/redelivery_fee/run_01` a2/b1b `y_voice_1`、Y gate BLOCK実績)**: 同様。個別承認済みLRは`HUMAN_APPROVAL_SUPERSEDES`フラグ有(`ypl7_user_approval_record_y_voice_1.json`)=正常LR判定の対象外/既存承認経路の維持を確認。
3. **X Word Gacha Adv part3(`word_gacha__run_wg_01/b1b`)**: LR採用+UDR #183(a)個別承認。新Gateで正常LR判定+parity(本文`you've`≠音声`you have`はUD-1/W4是正の対象)=承認前提の挙動を確認。
4. **異常ケースの実証**: 上記保存データの**in-memory変異**(Style sha改変・`asr_judgement`削除・`fallback_used=None`・`confirmed_kp_lr_overlap`イベント付与・JA roleにLR記録)で各々BLOCKを確認(§6-2の4〜11と同一fixtureを流用)。
5. **Z**: 保存run内に「Z narrator LR成功→Gate PASS」の実発火は未観測(前回W3 §2)。`er063_family_z_style_actual_gate_test_01.py`のfixtureで評価し、**実発火のruntime evidenceは別途**(Phase C、ZのFallback強制NG等=有料。費用は7-7により案件見積300円以下なら承認済みScope内で自律、Fable判断=B-5)。
6. 証跡の保存先は本管理IDの`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/`配下(Fableが指定)。原文§10-11は「コード配線のみ・DEV動作のみ・単体のみではPRODUCTION_WIREDにしない」ため、**1件以上の正式Production run(Z含む)での発火確認**をPhase B/Cの受入条件とする。

## 8. 実装順序・依存(Opus条件A論点)
- **依存1(必須・順序)**: 判定核のLR解除は、W1(委任_01)の「最終表示本文=TTS入力=ASR正解」記録と`TEXT_AUDIO_PARITY`検査が同一リリース内で配線済みであること。**UD-3のLR解除だけ先行リリースしてはならない**(原文§5「本文と音声の不一致」停止要件を満たせなくなる)。parity検査の入力が未配線の間は常に異常(BLOCK)側に倒れる設計(fail-closed)のため、順序を誤ってもAI島等が無検知公開されることはなく、ただ止まるだけで安全。
- **依存2**: Fallback部は表示仕様(委任_02等)と独立。先行配線しても`FALLBACK_APPLIED`警告が最終Human資料へ伝わるまで人が見えない期間が生じるため、**Fallback解除も最終Human報告配線と同時リリースを推奨**(原文§12「隠さない」)。
- **並列化**: 判定核(純関数)+単体testは単独で先行実装可。Y/Zのgate差替・runnerの警告出力・SSOT改訂は核の完成後に並列。

## 9. 判断候補(区分付き。`USER_DECISION_REQUIRED`ラベルはFableが付与)
| ID | 内容 | 区分 | 根拠 |
|---|---|---|---|
| A-1 | `CURRENT_SPEC.md:2857`(Fallback採用=個別承認のみ)がUD-3で置換される | **A** 既判断(原文§5(2)、2026-10-28が後決定) | 再質問不要。SSOT改訂のみ |
| A-2 | Zは現にFallback採用で停止している(`er063:2140`)。UD-3は「Z相当経路も対象」(原文§5)なので解除対象 | **A** | 原文§5本文 |
| A-3 | LR×確定KP重なりを停止にする(従来は記録のみ) | **A** 既判断(原文§3「確定内容に干渉する場合は無断で変更せず適切なSTOP/USER_DECISION_REQUIRED」・§5「LRによる…確定内容…違反は従来どおり停止」) | Zでは新規の検知追加だが原文由来 |
| A-4 | Y本文のGate重複実装を共通核へ統合 | **A**(承認済みGateの内部構造整理、品質条件は同一以上) | `er121:905-929` |
| A-5 | Zの原作保持検知はValidator撤廃済(既判断`CURRENT_SPEC.md:1622`)につき新設しない | **A**(既判断)。**Fableが「検知手段不在は§5違反」と解する場合のみD** | §4注 |
| B-1 | UD-3(LR/Fallback解除)をUD-1(parity検査)・最終Human報告と同一リリースで配線する順序 | **B**(Fable判断) | §8。順序を誤ってもfail-closedで止まるだけ |
| B-2 | 判定核を全profile(coffee_p8/n01/fx_20261016等)に適用するか、現行既定`fx_20261017`のみか | **B** | §4。全profile推奨(許可リストはprofile非依存) |
| B-3 | JA短文Fallback・ENGLISH_LOCK・Z JA/KP_ENの「採用take Styleが実際にどのキーで記録されるか」の実測確認(推定の箇所: Y4・Z KP_EN・JA ③) | **B**(Phase B冒頭の0円確認。記録キーが無ければleaf側の記録追加が承認済みGate整合の範囲内かFableが判断) | 保存run走査で、旧runのFallback entryはStyle記録なし・新run(paycheck run_pp_01)はtop-level `style_prefix`=dba23e66+`instruction_label`あり[実]。JA/KP_ENは未確認 |
| B-4 | OPEN-564以前の旧記録(Stdのtop-level `fallback_used=True`だが採用takeはrole Style)の扱い=記録完全なら警告・不完全なら停止 | **B** | AI島a2が該当。品質引下げではなく記録の正確化(採用take記録で担保) |
| B-5 | 有料runtime evidence(Z narrator/Fallback強制NG等)の費用=7-7の300円以下か | **B**(Fable見積) | §7-5 |
| C-1 | `LR_REWRITTEN`警告・`pass_with_warning_listening_list`は変更なし(Fallbackは載らない現状のまま、可視化は新警告で代替) | **C** 実害なし | H4/H5 |
| D | **品質基準の引下げに当たる懸念: なし(ユーザー決定済み範囲内)**。残る実質リスク2点を明記: (1)X/Y本文LRは正常条件を満たせば人の試聴なしで採用される(従来は常に人承認)。防御線=LR 7 Gate+Natural English QA+ASR PASS+parity+KP非干渉+最終Human資料の赤表示(ユーザー決定のとおり)。(2)Fallback採用が「正常」化する結果、Adv本文でrole Styleが落ちたtake(Minimal)も無承認で通る。これは原文§5(2)・§6Bが明示決定した内容で、許可リストが限定する(未承認Styleは停止) | (該当なし) | 原文§5・§6 |

## 10. RESULT_PACKET用4行+判定整合
1. 既存仕様整合(照合したfile:line): `er019_family_x_style_profile_01.py:529-624,629-760`、`er121_family_y_audio_01.py:774,804,874-1000`、`er063_family_z_audio_01.py:1720-1752,1908-1950,2063-2212`、`er127_tts_block_policy_01.py:108-123`、`er020_tts_retry_local_rewrite_01.py:625-628,746-749,836-885`、`er128_kp_confirmed_content_01.py:1236,1264`、`er078_asr_unified_judge_01.py:63,556-559`、`er078_pass_with_warning_registry_01.py:94-110`、`er003_v1_sing01_news_tail_fix.py:210-228`、`er003_v1_crosslevel_audio_02_common.py:473-481`、`CURRENT_SPEC.md:1622,2857,3168,3170,3178`、前回W3、ユーザー原文§3・§5〜§7・§10。
2. Production到達経路に入る未承認機能: なし(設計のみ、コード変更0)。
3. 失敗終了時の最終成果物: 該当なし(完走)。成果物=本ファイルのみ。原文UD-3の各項(照合維持/Fallback記録維持・解除/LR記録維持・解除/従来停止項目/品質検査不弱化)に対応する設計を記載。
4. 撤去・残置: 撤去0(設計のみ)。撤去予定と残置は§5。残存Grep(現状): `LOCAL_REWRITE_RECOVERY`=`er019:743`/`er121:929`+test(前回W3§7+本書§6-1)。
5. 判定整合: 重大NG=なし

## 付録: 実行した確認(読取・API 0)
- コード読取(上記file:line)。保存データ読取: AI島`{a2,b1b}/audit/tts_generation_results.json`(`full_story_part1_k2`のキー・attempts・LR記録・asr_judgement形)、告げ口心臓`b1b/audit/style_actual_vs_approved.json`(PASS・違反0)、`er019_output/**`・`er121_output/**`のFallback採用entryのStyle記録有無の走査(scratchpad内scriptのみ・書込0)。
- 未確認: JA/KP_EN/Z JAのFallback採用takeのStyle記録キー(B-3)、Z narrator LR成功の正式run実発火、W1のparity記録の最終スキーマ(委任_01の成果物待ち)。
