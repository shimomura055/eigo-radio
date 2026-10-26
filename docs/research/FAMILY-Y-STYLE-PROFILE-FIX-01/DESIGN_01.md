# DESIGN_01 — Family Y Style profile 是正設計(X方式 `resolve_run_profile` のYへの適用)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / 到達上限Status=DESIGN_READY / コード変更なし(設計のみ、実装は委任_02)。
性質: 承認済み仕様(`fx_20261017`継承=DESIGN_01[LAUNCH-01]:84・YL-A01・28-1運用7)と実装の乖離の是正(11-8 T1=不具合)。**新Style・新Prompt・新閾値・新方式の導入なし**。flagは作らない(新機能ではなく既存承認仕様の配線)。DefaultOffIsolation型testの対象外(Production挙動はY runが承認仕様どおりに変わることが目的)。ただしY Production挙動が変わるため、Fableが11-3条件C(重要変更のProduction採用前)に当たるか判断する(OPUS_REVIEW_REQUEST_01.md)。

## 1. 方式の選択: X方式(`resolve_run_profile`+固定記録+M3)
| 案 | 内容 | 判定 |
|---|---|---|
| **X方式(採用)** | `er019_family_x_style_profile_01.resolve_run_profile`(:458)で解決、`audit/style_profile.json`(:289)を固定記録、Gateは既存`m3_assembly_gate`(:685)+Y追加検査 | Yの音声moduleは既に`style_profile_mod.resolve_role_style/attach_segment_profile_record/m3_assembly_gate`を使用(`er121_family_y_audio_01.py:354-363,798`)。**profileの値の供給元だけが欠落**。差分最小、M2(新out_dir強制)・M5(backend検査)をそのまま継承 |
| Z方式(不採用) | 定数参照+drift test(`er063_family_z_audio_01.py:266-283,303`) | Y専用の定数表・Y用`resolve_role_style`相当を新設する必要があり差分が大きい。固定記録(runtime evidence)が残らない。DESIGN_01(LAUNCH):84の「Z方式」記述は、Yが既にXのprofile基盤を使っている現状と整合しない→本設計で訂正(OPEN-415は「エンジン化の要否」であり本件の配線はそれと独立に実装できる) |

## 2. 変更点(委任_02で実装。行番号は読取時HEAD)
### 2-1 `er121_family_y_runner_01.py`
1. `:37 STYLE_PROFILE = "default"` を**撤去**し、`Y_APPROVED_STYLE_PROFILE = "fx_20261017"`(リテラル。理由コメント+承認出典[`DESIGN_01.md:84`・A19・28-1運用7]を付す)を置く。X既定への自動追従はしない(Z同様、drift testで一致を固定=PREVENTION (d))。旧名`STYLE_PROFILE`は残さない(参照が残れば即AttributeErrorで検出)。
2. `YContext`に`style_profile: str = None`/`style_profile_source: str = None`を追加(:155-)。
3. 新関数`resolve_style_profile(ctx, cli_profile, write)`: `xr.style_profile_mod.resolve_run_profile(ctx.out_dir, cli_profile, write=..., tts_backend=ya.TTS_BACKEND)`→`assert_profile_backend`(Xと同順: write=Falseで検査→write=True。`er019_family_x_audio_production_runner_01.py:3352-3357`)。結果が`Y_APPROVED_STYLE_PROFILE`でなければ`YE2EStop("FAMILY_Y_STYLE_PROFILE_NOT_APPROVED")`(課金前)。例外は 2-1-5 のlegacy waiverのみ。
4. 呼出位置=`build_real_context`(:1280-)の`check_stop_sentinel`・`_launch_guard`の後、`load_dotenv`/client生成/予算生成の**前**(課金・ファイル作成前にSTOPするXの規約: `er019…runner:3347-3351`コメント)。mock/dry-runのcontext(:1300付近)はdry-runで`write=False`、mockで`write=True`(tmp)。
5. CLI: `--style-profile`(choices=`fx_20261017`,`default`、既定None)。`default`は**既存run stateがあり固定記録がないout_dirのlegacy resume**に限り受理し、`--legacy-style-waiver-ref <ユーザー承認の記録path>`が必須。受理時は`audit/style_profile_waiver.json`(profile・ref・時刻)を書く。Gate(2-2)はwaiverが無い`default`をBLOCK。**目的**: run_01/`run_voice_puck_ev_01`/E-3 run等の公開済み旧runの再pages等を失わず、かつ新規runが黙って`default`になる経路を作らない。
6. `:966 _tts_input_sha`の`STYLE_PROFILE`→`ctx.style_profile`(profile変更でstale判定。旧profileのstageはSTOP: 明示`--regenerate-stage`なしに再利用しない)。`:988,:990`(generate)・`:1016`(gate)・`:1034`(assemble)も`ctx.style_profile`。
7. `stage_gate`/`stage_assemble`の冒頭で`ctx.style_profile`の再検証(`read_record`と一致。resume時に別profileが紛れたらSTOP)。

### 2-2 `er121_family_y_audio_01.py`
1. `:544 generate_y_b1_segments`/`:632 generate_y_a2_segments`の`style_profile: str = "default"`既定引数を**必須キーワードに変更**(既定値撤去)。呼出し側がprofileを渡し忘れたら即TypeError(`assemble_level`は既に必須:1019)。
2. `y_style_gate`(:789-)の先頭に**fail-closed検査`y_style_profile_assert`**を追加(詳細=PREVENTION_01 (a)): (i)`read_record(theme_out_dir)`が`None`→BLOCK `Y_STYLE_PROFILE_RECORD_MISSING` (ii)`verify_record`(sha一致)失敗→BLOCK (iii)`record.profile_id != Y_APPROVED_STYLE_PROFILE`かつwaiverなし→BLOCK `Y_STYLE_PROFILE_NOT_APPROVED` (iv)`x_gate.checked`が空、または承認profileの全role(FULL_STORY[Y 8 segment]/SUPPORT_JA[a2]/PREVIEW[b1b]/KP_EN/KP_JA_MEANING[a2]/KP_EXPLANATION_EN[b1b])のうち当該levelに適用されるroleの検査対象が0件→BLOCK `Y_STYLE_COVERAGE_EMPTY(role)`。`gate_summary.json`と`y_style_profile_gate.json`に`profile_id`・`record_sha`・`checked_roles`を残す。
3. 既存の`if prof is not None:`分岐(:815)は、(2)により`prof`が`None`になる経路(default)をassertが先に落とすため、承認profileでは常に実行される。
4. **Voice本文のStyle合成**: 判断候補V1(PD06を全本文に適用=A19)では**追加実装なし**。現行loop(:590-605 Adv、:703-726 Std)が`_role_style("FULL_STORY")`を全本文segment(narrator・Voice 1〜3)に使うため、profile供給だけで承認仕様どおりになる。人物別Styleの結合(`style_prefix_override`へのVoice別連結)は未承認の新Styleになるため設計しない。V2(Voice本文のみdefault維持)が選ばれた場合のみ、Voice本文の`style_prefix_override`を`resolve_role_style("default","FULL_STORY",level,_base)`で解決し、Gateへ「Voice本文のdefault維持は承認済み例外」(例外ID+ユーザー承認ref)を記録する形で実装できる(新Promptは不要。承認後の別委任)。

### 2-3 影響範囲・既存機構との整合
| 機構 | 整合 | 根拠 |
|---|---|---|
| 初回生成(Std/Adv) | profile供給のみ変更。Std本文はPD06逐語+生成後6%減速(`std_append_slower_instruction=False`、減速は`n3_tts.generate_a2_segment_with_slowdown`=現行と同経路) | `er019_family_x_style_profile_01.py:_FULL_STORY_OVERRIDE`、`er121…audio:703-726` |
| chunk経路 | 親と同roleのStyleをchunkごとに記録(`attach_segment_profile_record`をchunk単位)。`y_style_gate`は全chunkを検査(:812付近の`targets`)。Std chunkも同。実記事は単一段落でchunk非発火(OPEN-527)。OPEN-527 CLOSEOUT委任の検証は`r.STYLE_PROFILE`参照を使うため、本設計の名称撤去と衝突する→委任_02は並行委任の完了後に開始 | `er121_family_y_audio_01.py:488-538,812` |
| retry/fallback | 変更なし。ただしprofile有効化でAdvの`minimal_fallback`(3回目)が`ADV_MINIMAL_FALLBACK`でBLOCK(人間承認なしでは組立不可)。これは承認済みX規則(`m3_assembly_gate`)で、Yに今まで効いていなかった分が効く。Stdのfallback検査は従来からdefaultでも有効 | `er019_family_x_style_profile_01.py:709-716` |
| Local Rewrite再TTS | `news_tail_fix`のLR再TTSは`style_prefix_override`を転送せず`<default:ENGLISH_STYLE_PREFIX>`で生成(共通核CC-F2)。LRに至った本文は`LOCAL_REWRITE_RECOVERY`でBLOCK→人間承認(従来どおり)。OPEN-540(TTS統一)の範囲。**本委任ではLR規則を変更しない** | `er003_v1_sing01_news_tail_fix.py:370-377`、Y_F01_STYLE_PROFILE_CHECK_01.md §4 |
| resume | 固定記録が正。CLI未指定=記録を採用、食い違いはSTOP(`er019_family_x_style_profile_01.py:458-` )。旧run(記録なし+run stateあり)は`default`明示+waiverなしではSTOP(M2)=Style混在を防止 | 同:440-456 |
| M2(新out_dir要否) | **必須**。`run_01`等は`tts_generation_results.json`等があり固定記録を新規作成できない(同:290-295)。→新run dir `run_style_fix_01`(REGEN_PLAN_01) | 同 |
| Master Audio Store | K2は2段key(`key_phrase_english_component_k2`)で旧MINIMAL keyと別id→新規生成(旧entry不変)。shell固定はStyle非対象で従来どおり再利用 | `er019_family_x_style_profile_01.py:163-` |
| HR承認(OPEN-535) | 新runへ`human_approved_segments.json`/`review_lock_state.json`を**複製しない**(Style/Voiceが変わった音声に旧承認を流用しない)。並行委任のguardとは独立に、runの作り方で担保 | REGEN_PLAN_01 §2 |
| er117 | chunk本体はprofileを読まない(`er117_chunk_tts_production_01.py`にstyle_profile言及0件)。「固定記録欠落STOP」(RESULT_PACKET_CHKW2.md:9、課金前rc=1)はX/Y run dir複製時に`audit/style_profile.json`を複製し忘れたM2側のSTOP。本設計では記録は複製せず新out_dirで`resolve_run_profile`が作る | `docs/pm/RESULT_PACKET_CHKW2.md:9` |

## 3. 撤去・残置の確認(委任_02でGrep)
- 撤去: `STYLE_PROFILE`(runner)、`generate_y_*`の`"default"`既定引数。
- 残置(意図): `er019_family_x_style_profile_01.PROFILE_DEFAULT`と`resolve_role_style`のdefault素通し(X/Z/legacy用)。Yの`y_style_gate(…,"default")`を直接呼ぶ既存test(`er121_family_y_audio_chunk_test_01.py:298,308`)は「default用の歴史的test」ではなくGate単体の振る舞いtestなので、承認profileへ書換え、defaultがBLOCKされるtestを追加。
- 期待Grep(実装後): `grep -n 'STYLE_PROFILE\b' er121_*.py`→`Y_APPROVED_STYLE_PROFILE`のみ。`grep -n '"default"' er121_family_y_*.py`→legacy waiver経路とtestのみ。

## 4. test(要件。PREVENTION_01 (c)(d)と共通)
1. runner: ctxのprofile==`Y_APPROVED_STYLE_PROFILE`、`audit/style_profile.json`が作られる、既存run state+記録なし+CLI未指定→課金前STOP(M2)、`--style-profile default`+waiverなし→STOP。
2. Gate: 記録欠落/不一致/`default`/`checked=[]`/全role未カバー→BLOCK(fail-closed)。承認profile+全roleのfake entryでPASS。
3. 生成: Std/Adv全本文segment(narrator+Voice 1〜3)の送信prefixがPD06(Stdは逐語+減速、Advは`startswith(PD06)`)、previewがE1/S3、KPがK2/P8-KP/P7(fake TTS経由、API 0)。
4. drift: `Y_APPROVED_STYLE_PROFILE == xprof.DEFAULT_NEW_RUN_PROFILE`、`STYLE_PROFILES[承認].overrides`の全roleがY側カバレッジ表(PREVENTION (c))にある。
5. 既存14 Y testの回帰: 5ファイル(`r.STYLE_PROFILE`参照: audio_chunk/multiparagraph_regression/runner_01/std_chunk/std_chunk_opus)+HR guard test。fx化でAdv Gate(`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`等)が有効化されるため、fake TTSの戻りentryに`style_prefix`/`style_profile`記録を持たせる修正が要る見込み(+約0.5h、委任_02で実測)。

## 5. 実装順・所要時間・並行衝突
並行委任(OPEN-535: `er121_family_y_audio_01.py`のHR承認照合部とtest、OPEN-527: test fixture)と同一ファイルを触る。**直列化の理由=同一ファイル競合(許される直列条件)**。OPEN-535 guardとOPEN-527のcommit後に委任_02を開始、または委任_02を「runner+Gate新規関数(別セクション)」に限定してmerge競合を避ける。見込み: 実装1h+test修正1h+Opus任意レビュー(ある場合)別。実run(REGEN_PLAN_01)は約0.5h。
