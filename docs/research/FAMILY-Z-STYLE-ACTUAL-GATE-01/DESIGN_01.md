# FAMILY-Z-STYLE-ACTUAL-GATE-01 DESIGN_01(OPEN-551是正、Y方式のZ展開)

管理ID: FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01 / 2026-10-27。到達上限=IMPLEMENTED(正式経路mock確認)。API 0。
根拠: 再発防止方針 `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/PREVENTION_01.md` (a)=全Familyの正式経路で承認profileと実測prefixをaudit必須化、未記録/不一致=BLOCK。出発点=`docs/research/PM-OPEN-548-551-INVESTIGATION-01/OPEN551_Z_STYLE_CHECK_01.md`。

## 1. 構造(Y `y_style_gate` と同じ)
| 項目 | Y(er121:814-990) | Z(本委任、er063「8-S」節) |
|---|---|---|
| 期待集合 | `Y_ROLE_COVERAGE`(role×level×segment) | `Z_ROLE_COVERAGE`(level→role→必須か) + 検査集合は**planの全TTS clip(role×clip_id)**。planの行数==照合表の行数を要求(`Z_STYLE_COVERAGE_MISMATCH`)、planにlevel外のroleが現れたら`Z_STYLE_COVERAGE_UNEXPECTED`、必須roleが0件なら`Z_STYLE_COVERAGE_EMPTY`、表と`FAMILY_Z_ROLE_STYLE`/`CROSS_FAMILY_COMMON_STYLE_MAP`のdrift=`Z_STYLE_ROLE_TABLE_DRIFT` |
| 承認値 | X profile(`fx_20261017`)を`resolve_run_profile`で解決 | Zは独自表`FAMILY_Z_ROLE_STYLE`+literal sha固定`_STYLE_SHA256`(Xのprofileに従属しない。Zの既存設計[er063:175-200]を維持) |
| 実測取得 | `final_style_record`(Adv top-level str / Std attempts_log末尾 dict)、日本語=top-level `style_prefix`(str) | **`build_entry`が`build_style_actual_record(spec,result)`で`entry["style_actual"]`へ記録**(leaf戻り値のみ使用、leaf非編集)。取得順=(1)採用attempt(fallback段→標準段の順で最後にstyle記録を持つattempt)(2)top-level `style_prefix`(str全文/dict)。両方あり不一致なら`secondary_top_level`に副次記録 |
| 取れない時 | M-4: `意図sha(実測なし)`ラベル、一致扱いにしない | 同じ。`kind=unmeasured`→`Z_STYLE_ACTUAL_UNMEASURED`=BLOCK(`measured_kind="意図sha(実測なし)"`, `match=False`) |
| fail-closed | checked空=FAIL | 未記録(`Z_STYLE_ACTUAL_UNRECORDED`)・未実測・不一致・checked空(`Z_STYLE_CHECKED_EMPTY`)=BLOCK(`FamilyZStyleActualGateStop`、照合表保存後に送出) |
| 出力 | `audit/style_actual_vs_approved.json` | 同名(`<run>/<level>/audit/style_actual_vs_approved.json`)。行=level/role/segment/承認sha/実測sha/len/source/match/check/violations/human_approved |

## 2. Z固有論点(Fable照合用)
### 2-1 hint追記(英語Style)
英語は発音hint(`pron_resolver_core`)がStyle末尾に追記され得る。判定=(a)実測sha==承認sha(exact)、または(b)`hint_applied=True`かつ`len>=承認長`かつ`head200`が承認原文の先頭で始まる(+全文が見える場合は`startswith_expected`が偽でない)。X(`evaluate_segment_evidence`)と同じ規則。日本語roleは追記が無くexactのみ。

### 2-2 セリフ(DIALOGUE_STD / DIALOGUE_ADV)
- 承認値=**既定Dialogue Style `p9a.ENGLISH_STYLE_PREFIX`**(`style_prefix_override=None`、ユーザー§2B/2026-10-19決定③。`CROSS_FAMILY_COMMON_STYLE_MAP`のEXCEPTION)。
- leaf `er012.generate_voice_body_wide_margin`は**送信prefixを返さない**(top-level `style_prefix`もattempts_logにも無い。er012:525-560)。leaf(er012/er003_v1_*)は編集禁止のため**実測は原則取れない**。→ `意図sha(実測なし・leaf非公開)`ラベルで`match=None`(一致扱いにしない)、行に`measurement_gap=true`を残す。
- ただし意図shaは検査する: `style.effective_style_prefix_sha256`が(既定Dialogue Style sha)または(文脈・感情付きTTS採用時のみ`dialogue_tts.ctx_style_sha256`)に一致しなければBLOCK(`Z_DIALOGUE_STYLE_INTENDED_MISMATCH`)。将来leafが実測を返せば`measured`として既定sha/ctx shaとの一致を要求(`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`)。
- 従来方式(3回目)への切替はDialogueの承認済み構成(ctx→ctx→180秒→従来)でありStyle落ちではない→fallback違反にしない。
- **判断候補(C: 現タスクと独立の改善)**: Dialogueの実測化はleaf(er012)側の`style_prefix`返却追加が必要。leaf編集は本委任の範囲外(Fable判断)。当面は上記の意図sha検査+`measurement_gap`明示で、Narrator Styleの誤混入(overrideを渡す配線ミス)は`style_text_for(dialogue)=None`のtest(既存)と`effective sha`で検知する。

### 2-3 例外role(CROSS_FAMILY_COMMON_STYLE_MAP "EXCEPTION")
| role | 期待値 | 理由(既存表のまま) |
|---|---|---|
| ADV_EN_COMMENT | E2_UPBEAT(`_STYLE_SHA256["E2_UPBEAT"]`) | ユーザー§2B表に記載なし・Coffee採用Styleを維持 |
| TOPIC_INTRO_EN | X_TOPIC_INTRO | X既存承認TOPIC_INTRO逐語コピー |
| JAPANESE_TITLE | X_J3 | X既存承認J3逐語コピー |
| DIALOGUE_ADV/STD | 上記2-2 | ユーザー§2B |
| SHELL | 対象外 | TTSなし(既存Master資産) |
共通role(NARRATOR ADV/STD=PD06、STD_JA_PREVIEW/COMMENT=S3、ADV_EN_PREVIEW=E1、KP_EN=K2、KP_JA=P8_KP、KP_EXPL_EN=P7)は`FAMILY_Z_ROLE_STYLE`の承認shaに対し完全一致。例外roleもtext保有roleは同じ「実測==承認」規則(`row.role_origin`で区別して記録)。

### 2-4 第3KP(KP_JA/KP_EXPL_EN)
planの形(`kp_explanations`の有無)はplan builderの責務のため、levelでの固定はしない: `KP_JA`/`KP_EXPL_EN`は個別には任意、**どちらか1種以上がplanに存在**(`KP_THIRD`、無ければ`Z_STYLE_COVERAGE_EMPTY`)かつ全clipが検査されることを要求。production Std=KP_JA、Adv=KP_EXPL_ENは既存plan builderが保証(er063:577-590)。

### 2-5 Style落ちfallback採用=人間承認必須
- 採用attempt(fallback段)または`instruction_type`に`minimal`を含む、または`result.fallback_used`で、かつ実測が承認と不一致/未実測 → 違反に`Z_STYLE_FALLBACK_ADOPTED`を併記。
- 承認=既存の`human_approved_segments.json`(`asm.record_human_approval`、canonical text shaが一致する場合のみ有効。X `_approved`と同じ関数を読み取り利用)。承認recordなし→BLOCK、承認あり→PASS(`human_approved=true`・違反IDを照合表に残す)。
- fallback段でも承認Styleのまま送られた場合(Style落ちなし)は違反にしない。
- 注意: 上記承認はX/Yと同じく「clipをHuman Reviewで聴いてPASS」の記録と共用。KP_EN(ENGLISH_LOCK段)のfallback採用も同規則(Zでは例外免除を置かない)。

## 3. 過去runの扱い(遡及BLOCKしない)
- 判定=マーカー`<run>/<level>/audit/style_actual_gate.json`の有無。`run_tts_stage`が**結果/checkpointが無い新規level開始時のみ**書く(`write_style_actual_marker_if_fresh`)。導入前に開始したrun(結果が既にある)には書かない=遡及しない。dry-runは書かない。
- マーカー有(strict): 未記録clip=BLOCK、カバレッジ強制。
- マーカー無かつ記録の無いclip: **「未記録」警告のみ**(`Z_STYLE_ACTUAL_UNRECORDED_LEGACY_RUN`、BLOCKしない)。attempts_logから導出できる範囲は`legacy_derived_*`として参考記録(例: 猿の手`full_story_part1_c10`の不一致は警告側に現れる)。
- マーカー無でも`style_actual`記録のあるclipは厳格に検査(進行中runの新規clipを守る)。記録済みclipが1つでもあればカバレッジも強制。
- 出力`mode`: `strict` / `legacy_run_recorded_clips_strict` / `legacy_run_warning_only`。

## 4. 影響範囲・非変更
- 変更: er063(`build_entry`にadditive `style_actual`、`run_tts_stage`にマーカー、`run_audio_gate`に検査、新節8-S)。reuse_key・既存entryキー・Style文面/Prompt/Voice/回数は不変。
- 非変更: `er019_family_x_style_profile_01.py`(X)、`er121`(Y Gate)、`er003_v1_*`(leaf)、過去run dir・公開ページ。
- 既存fixtureの是正(不整合mock): `fake_generators`/`Gens`/`mock_tts_generators`が`style_prefix.sha256="ab"*32`(承認Styleと無関係の値)を返していたため、実leaf同様に承認Styleを送った記録を返すよう修正(`er063_family_z_audio_01_test_01.py`・`er117_z_chunk_wiring_test_01.py`・`er026_family_z_fiction_production_runner_01.py` mock_tts_generators)。不整合値を期待値としてassertするtestではない(いずれも「通過すること」を見るfixture)。
- Production挙動の意味的変更: 「未記録/不一致のZ新規runをGateでBLOCKする」=承認済み再発防止方針(PREVENTION_01 (a))の実装であり新仕様ではない(Y展開と同種、Fable判断)。Gateは既存の承認済みStyleを変更しない。
