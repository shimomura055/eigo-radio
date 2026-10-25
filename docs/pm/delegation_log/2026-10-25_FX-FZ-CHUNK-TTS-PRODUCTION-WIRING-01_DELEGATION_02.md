FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02(実装: Opus条件A必須M1〜M4を設計へ反映→共通module+er020+testを先行→X/Z配線→runtime evidence→回帰→SSOT)。あなたはsonnet-worker。Fable(PM)からの委任。

## 0. 前提
- ユーザー正式決定: X=B0.2(Advanced本文3 part、段落分割+0.2秒)、Z=B_r1(Adv narrator 100語超、ceil(語数/100)、段落>文、最小25語、引用途中禁止、0.2秒)=APPROVED_FOR_PRODUCTION、目標PRODUCTION_WIRED。原文`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md`。追加Trial・保留禁止、方式/ポーズ/対象の変更禁止。
- Phase 0成果(委任_01、commit 98cc1a174): `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/{EXISTING_SPEC_CHECK_01,WIRING_DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`、`chunk_tts_core_draft_01.py`、`tests_draft_01.py`(24 passed/15 skipped)。Fable決定: 150語ルールは共存(Opusも妥当と判定)。
- Opus条件Aレビュー=「条件付き(実装前に設計修正M1〜M4)」(§1に逐語。`OPUS_REVIEW_01.md`として逐語保存、見出し「# OPUS_REVIEW_01(条件A: Chunk分割Production配線設計、2026-10-25、opus-consultant、read-only・API 0)」)。同内容の再レビュー不要(Fable照合済み)。
- 費用: evidence=X 約5〜10円(theme_out_dir全体を複製し正式runner CLIでAdv TTS→assemble→pages)、Z 約30〜40円(M3: `copy_reusable_run_assets`でテキスト系のみ複製した新runを作り`tts_a2,tts_b1b,provision_shell,gate,assemble,pages,page_verify`を1起動)。本委任上限60円(案件300円以下・承認範囲内)。**各有料起動前に当日(JST)累計を集計し、見積を足して1,000円超なら、実装・test・SSOTまで完了して起動は日次上限解除後に回す(その旨報告)**。公開差替えなし(完成候補として`user_test/`配下に置く)。同一run起動間隔150秒・RESTART_STORM・RUN_LOCK順守、他agentのZ TTSと直列化。
- 並行agent(重要): FAMILY-Z-STUDY Part 1配線(`er019_family_x_audio_production_runner_01.py`のKP/scaffold、`er026_*` stage_kp/pages、`er063_family_z_audio_01.py` build_pages付近を編集中)、FX-CORE-NUMERIC配線(er019 B3/Writer系、er053、Writer module)、Family Y音声化(er110)。**手順**: (1)共通module `er117_chunk_tts_production_01.py`(番号の空きを確認)+`er020_tts_retry_local_rewrite_01.py`のchunk ID形追加+test+設計書修正は、`git worktree add <scratchpad>/wt_chunk HEAD`で作ってmainへcommit(他agentの作業treeに触れない。worktreeはautocrlfに注意、終了後remove)。(2)X/Z配線(er019/er026/er063/er019_family_x_style_profile_01)は、**他agentの未commit差分が当該ファイルに無いことを`git status`で確認してから着手**。差分が残っていれば5分間隔で最大60分待ち、解消しなければ(1)までの成果とSSOTをcommitして報告終了(Fableが再委任)。編集は関数単位、commitは一時index方式。conflictが出たら停止して報告(ユーザー確認事項)。

## 1. Opus条件Aレビュー(逐語保存用)
---
## 判定: 条件付き(実装前に設計修正が4点必要)

骨格は妥当です。chunkを通常entryとして扱うこと、親wavを生chunkの連結にして組立時にchunk別gainをかけ直すこと、`resolve_narrative_role`への追加、150語ルールとの共存がこれに当たります。
ただし次の2点が設計書に入っていません。
- X Style profile M3 Gateの写像漏れ(このままだと、組立が常にBLOCKされるか、Gateが黙って効かなくなる)
- Z evidence案Aが既存の再利用禁止ルールに抵触している

いずれも採用済みの方式・ポーズ・対象の変更を要しないため、WIRING_DESIGNへ追記すれば実装委任へ進めます。

---

## 実装前に必須(設計修正)

**M1. X Style profile M3 Assembly Gateがchunkを見ていない(最重要)**
- 根拠:
  - `er019_family_x_style_profile_01.py:200-205` `ROLE_SEGMENTS["FULL_STORY"]=("full_story_part1","full_story_part2","full_story_part3")`
  - `:636-655 _gate_targets`は`segments.get(name)`の完全一致
  - `:681-687`は`style_prefix`がprofile原文で始まること、`instruction_type!="minimal_fallback"`、`:715 local_rewrite_recovery`を検査
  - 呼出は`er019:1963-1966`(`load_family_x_b1_sources`より前)
- 問題: 設計どおり親集約entryを`segments["full_story_partN"]`に置くと、M3 Gateは親を検査します。親には`style_prefix`/`style_profile`が無いので、常にBLOCKされます。実装者が回避のためchunk1の値を親へコピーすると、chunk2以降のminimal_fallbackやLocal Rewriteが**黙って通ります**。
- 修正:
  - chunk化したpartについては`_gate_targets`がchunk entryを列挙するようにする(親はM3の対象外)。
  - `attach_segment_profile_record`(`er019:1166-1171`)をchunkごとに呼ぶ。
  - C8の編集対象表に`er019_family_x_style_profile_01.py`を追加する。
  - testでは「chunk k2だけminimal_fallback→BLOCK」を固定する。

**M2. 親集約entryの生成・再構築の条件**
- (a) 親entryは失敗時も**常に書く**。statusはplanのchunk id一覧から導出し、entryが無いchunkは`_segment_gate_status(None)`=UNVALIDATED(`assemble:116-118`)として扱う。
  - 設計(X-b)は「全chunk OKなら親を書く」+「失敗chunkでループ停止」です。この組合せだと、失敗chunkが人間承認された後、Gateには承認済みchunkだけが見え、未生成chunkも親も存在しない状態になります。Gate(`assemble:485`)は存在するentryしか走査しないので、ここが穴になります。
- (b) `refresh_parent_status`は親**wavの再合成とshaの更新**も行う。STOPPED chunkの人間承認後は親wavが無い、または古いままで、X `load_family_x_b1_sources`とZ `run_assembly:1761`のtarget_rms計算が、存在しないwavや古いwavを読むことになるためです。
- (c) 呼ぶ位置:
  - X: `stage_assemble_family_x_b1`の`_style_profile_gate_blocked_summary`より前(`er019:1963`)
  - Z: `run_audio_gate`の冒頭(`er063:1647`)と`run_assembly`
  - `verify_parent_integrity`は音声を読む前に実行する。
- (d) 親に`human_approved_chunks`を記録する。statusがOKに丸められて人間承認の事実が見えなくなるのを防ぐためです。

**M3. Z evidence案A(run_sf_prod_02の複製+tts_b1bのみ)は不可**
- 根拠: `er063:659-671`の再利用許可リスト(委任_15、Opus R-C4)は「音声・tts結果・HR承認/Lock・audit・narration・assemblyは持ち込まない…取り込み機構は作らない」と明記しています。results/narrationの手動複製はこのルールの迂回になります。
- 技術的にも問題があります。複製したentryの`path`は旧runを指したままなので、共有Gateのstale検知(`assemble:212-222`)は**旧runのファイル**のハッシュを照合してしまいます。
- 代案:
  - `copy_reusable_run_assets`でテキスト系だけを複製して新runを作り、`tts_a2,tts_b1b,provision_shell,gate,assemble,pages,page_verify`を1起動で実行する。gate/assembleは`LEVELS`の両levelを回すため(`er026:1969-1988`)、Stdの生成も必要です。
  - 費用見積はb1b単独15〜20円から両level合計で**約30〜40円**に修正。案件300円以下・承認範囲内なのでFableの自律判断で実行できます。
  - 近日中にZの本番runがあるなら、それを正式初回経路の証拠にするのが最も安く、証拠としても最も強いです。
  - 補足: 他agentがer026のPart 1配線を並行編集中なので、起動はそれがcommitされた後にしてください。

**M4. X evidenceの複製範囲**
- b1b dirだけを複製すると、theme直下の`audit/style_profile.json`(`style_profile_01:288`)が欠けます。その場合、`resolve_run_profile`(`:457-`)はdefaultに解決されるかSTOPします。M3も`read_record`がNoneになって素通りになります(`er019:1887-1892`)。結果として、誤ったStyleでchunkが生成され、証拠として無効になります。
- 修正:
  - `theme_out_dir`全体(entry_point.json・audit含む)を複製する。
  - 起動前に、記録profileが現行Production profileと一致することを確認する。
  - evidenceに、M3の`checked`へchunk idが含まれていることを入れる。
- これらを満たせば、正式runner CLIで新out_dirに対しAdv TTS→assemble→pagesを実行する方式は「正式経路でchunkが初めて生成された証拠」として十分です。chunk idは旧cacheに無いので、構造的に初回生成になります。

---

## 実装時に必須

- **I1. Xのchunk reuseにplanner_version条件を入れる**: `_generate_or_reuse`(`er019:840-852`)はtextとstyle_versionしか見ていません。`CHUNK_PLANNER_VERSION`を上げると旧chunkが再利用され、その後`verify_parent_integrity`(draft:201)がSTOPし、手作業でしか抜けられなくなります。版が違えば再生成するようにしてください。
- **I2. gain式を1か所にまとめる**: draftの`compose_gained_parent:168-172`は`p9a.compute_gain_for_target_rms`(`p9a:459-471`)を再実装しています。関数を引数で渡して共通化し、式のずれを防いでください。
- **I3. planner一致testを強化する**: 現状は語数列の比較だけです(tests_draft:86-89)。chunk本文と`boundary_kind`まで比較し、ディスク上の全Z run・全clipと全X parts.jsonに広げてください。期待値はfixtureとして凍結し、Production testがDEVのer113/er114をimportしないようにします(commit 13c640bcのallow-list方針)。
- **I4. import時の自己検査**: `er019:80-88`と同型で`full_story_part1_k1`、Z側では`full_story_part1_c1_k1`がFULL_STORYに解決されることを検査し、C4の入れ忘れを即時に検出します。roleは`er006_secondary_asr_01.py:1024,1181`(judge role)でも使われるので、外れると影響は広範囲に及びます。
- **I5. `--only-segments`の正規表現**: `_k`は`full_story_part`の選択肢にだけ付け、`--level a2`での`_k`指定は拒否する(`er019:682-701`)。
- **I6. Z `run_assembly`へchunk planを渡す**: 現在は`story_clips`しか受け取りません(`er026:1984`)。`load_level_inputs`のplanを渡し、そこで`verify_parent_integrity`を実行してください。
- **I7. 親entryに表示用の項目を持たせる**: `voice`・`style.instruction_label`・`canonical_text`を持たせ、ページ行(`er063:1886-1899`)が「-」や「未取得」にならないようにします。chunkの`audio_text_deviation`(Local Rewrite)の注記もページに出してください。gain_reportの親keyに、実際には掛けていないgain値を書かないこと。
- **I8. 合成長検査**: draftの`verify_composed_duration`(:216-220)は秒換算で許容幅の単位が混乱しています。整数サンプル数の一致で判定してください。あわせて、組立時に「親wav == ディスク上のchunk wavを生連結したもの」を確認してから、親wavをtarget_rmsの基準に使ってください。
- **I9. Zのchunk本文の表記**: chunk本文は`normalize_for_tts`後の表記です。segment_planのclip.textが既に正規化済みかを確認してください(引用符の表記差が出ないこと)。語数定義は`er013:272`と一致しているので問題ありません。
- **I10. 回帰testはclean worktreeで取る**: 他agentの未commit差分による失敗と区別するためです。
- **I11. 固定名に依存する箇所の残り**: `er019_family_x_validation_inheritance_01.py:593`(`derive_expected_texts`、手動CLI)はchunk labelを導出できません。拡張するか、既知の制限として記録してください。

---

## 推奨(任意)

- **R1. Xでもchunk失敗時は後続chunkの生成を続ける**: 既存のX loop(`er019:1146-1171`)もZ(`er063:1349-1376`)も失敗後に続行します。停止しても、OK chunkは再利用されるので節約になりません(Xは段落単位なので、本文を修正しても変わるのは1 chunkだけ)。停止すると、未生成entryという余計な状態が生まれるだけです。
- **R2. `_CLIP_ID_RE`は全体を広げずに別の正規表現を追加する**: 使うのはGate箇所(1534/1570/1658/1660)だけにし、入力検証(:580)、`comment_after_segment_ids`(:1717)、`part_to_clip_id`(:1851)は厳密なまま残します。
- **R3.** pwwの警告をページ行へ紐付けるとき、`_k\d+`を親clipへ対応させる(`er063:2031`)。
- **R4.** role解決のスナップショットtestは手書きの一覧ではなく、既存`*_output`のresultsに出てくる全segment idを使う。

---

## 論点別の結論

1. **Gate写像**: M1・M2以外は妥当です。共有Gate、HR Lock(segment_id+text sha、`er011:318-333`、replan後の同じidも安全)、telemetry、stale検知は無変更でchunk単位に効きます。
2. **親集約entryのstatus導出・target_rms**: 二重構造は妥当で、式を無変更で使う主張も正しいです(Xのchunk合成はTrialの`join_chunks`と同一ロジック)。
   - Xの+0.5dBは、現行方式でもtakeごとに動く範囲です。
   - Zはrun_sf_prod_02の`story_clips[0]`(part1_c1)がchunk化されないので、target値自体がTrialと同じになります。
   - 0.2秒の無音を含めて計算するとRMSが約0.06dB下がる点は、仕様として明記してください。
   - peak cap(上限0.95での頭打ち)は記録するだけでよいです。
3. **Trialとの一致**: Xは一致、Zも実runで一致しています。I1・I3で担保を強めてください。
4. **retry/resume**: chunkごとの上限3回は回避になりません。最悪ケースの文字量は「3回×n本×1/n長」で従来と同等です。残る対応はI1・I5・I6です。
5. **欠落・重複・順序の防止**: 5層で十分です。chunk境界での語欠けはchunk単位ASR(tail fix込み)で既存と同じ水準で検出され、短いchunkは相対的に厳しくなる方向です。chunk間の重複はplannerのassertと順序検査で防げます。実行時のwhisper整列は不要です。
6. **150語ルールとの共存**: 妥当です。150語ルールは複数段落の場合に1回だけ2分割する規則で(`er013:263`)、新規則は単一段落の長いclipも扱えるので役割が重なりません。さらにTrialは150語ルール適用後のplan(82/79語)に対して実施されているので、共存こそがユーザーが試聴して承認した構成です。一本化すると承認範囲から外れます。
7. **非影響の担保**: 方法は十分です。R4とI5を追加してください。
8. **runtime evidence**: M3・M4のとおりです。
9. **role解決の追加**: 必須で、妥当です(I4を追加)。
10. **並行編集・費用**: 一時index方式は、同じ関数内で他agentの変更と隣接するhunkがあると分離に失敗します。共通module・er020・testは`git worktree`(HEAD起点)で先に作り、X/Zの配線は他agentがer019/er026/er063をcommitした後に着手するのが安全です。conflictが出たら既存ルールどおりユーザーに確認します。費用見積(X 0.43%・Z 0.3%未満)に誤りはありません。

## ユーザー判断が必要な事項

なし(上記の修正はすべて、承認済みの方式・ポーズ・対象の範囲内で収まります)。
---

## 2. 作業
### Step A(worktree、API 0): 設計修正+共通部
- `WIRING_DESIGN_01.md`へM1〜M4・I1〜I11・R1〜R4(R1〜R4は採用)を反映(§番号付き)。
- `er117_chunk_tts_production_01.py`(planner[Trial er114/er113と同一規則、`CHUNK_PLANNER_VERSION`]、親wav合成[生chunk+0.2秒無音、整数サンプル検査=I8]、gain共通化[I2: p9aの関数を引数渡し]、親集約entry[M2: 常に書く・statusはplanのchunk id一覧から導出・`human_approved_chunks`・表示用項目=I7]、`verify_parent_integrity`、resume再構成)、`er020_tts_retry_local_rewrite_01.py`のchunk ID形追加+import時自己検査(I4)、test(planner一致fixture凍結=I3、role解決スナップショット=R4、既存ID戻り値不変)。commit→push。
### Step B(他agentのer019/er026/er063未commit差分が無いことを確認後): X配線・Z配線
- X: `generate_family_x_b1_segments`本文ループ→chunk生成(失敗後も続行=R1)、`attach_segment_profile_record`をchunkごと(M1)、`er019_family_x_style_profile_01._gate_targets`をchunk列挙(M1、親は対象外)、`_generate_or_reuse`にplanner_version条件(I1)、`_VALID_ONLY_SEGMENT_RE`(I5)、`load_family_x_b1_sources`/`apply_family_x_b1_gain`/timeline/assemble、`refresh_parent_status`を`stage_assemble_family_x_b1`の`_style_profile_gate_blocked_summary`より前で(M2c)。M1 test「chunk k2だけminimal_fallback→BLOCK」。I11は拡張または既知制限として記録。
- Z: `build_level_plan`でchunk ClipSpec展開、Gate箇所限定の別正規表現(R2)、`build_reuse_key`(chunk specのみ追加、非chunkバイト不変test)、`_run_tts_stage_impl`末尾で親entry再構築、`run_audio_gate`冒頭と`run_assembly`で`refresh_parent_status`+`verify_parent_integrity`(M2c、I6: planを渡す)、`verify_z_speed_profile`、`build_z_sequence`、ページ行(I7、R3)、`er026 load_level_inputs`(段落構造供給)、I9確認。
- 対象外経路(X Std/Dialogue/短narrator/KP/Y)のバイト不変test。
- Production実装+testは X/Z それぞれ1 commit(revert単位)。
### Step C(有料、日次確認後): runtime evidence
- X: 『英国の電車マナー』theme_out_dir全体を新out_dirへ複製(M4、記録profile=現行Production profile一致を確認)→正式runner CLIでAdv TTS→assemble→pages。evidence: actual model_id/voice/style sha/分割位置と種別/chunk数/0.2秒実測offset/gain・RMS・peak(peak cap発火記録)/attempts・fallback・Local Rewrite/ASR判定/M3 `checked`にchunk id/費用/所要時間。
- Z: M3代案(`copy_reusable_run_assets`で新run→`tts_a2,tts_b1b,provision_shell,gate,assemble,pages,page_verify`を1起動)。対象=『告げ口心臓』(run_sf_prod_02本文)。他agentのZ TTS稼働なしを確認。evidence項目同上+speed v2 Gate結果。
- 両方とも公開差替えなし(`user_test/<trial name>/`に完成候補)。`RUNTIME_EVIDENCE_01.md`。
### Step D: 回帰(clean worktree=I10)、SSOT(CURRENT_SPEC新節: X/Z Chunk分割仕様・適用範囲・0.2秒・親wav定義[0.2秒無音を含むRMS約−0.06dBの明記]・runtime evidence項目・原価; OPEN-506/510=`WIRED_PENDING_FABLE`(X/Z別)、新規OPEN(将来判断候補: X Std適用は未検証・対象外)、DECISION_LOG、UDR #191実施記録)、`ADOPTION`相当の受入チェック表(要件1〜9)。`docs/pm/RESULT_PACKET_FXZC2.md`、ACTIVE_TASK自行。委任文逐語保存: `docs/pm/tools/extract_delegation_from_jsonl_01.py`(--index 545前後、冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02」で照合、±6; toolが無ければjsonlから先頭文字列一致で抽出)→`..._DELEGATION_02.md`。
- Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`(一時index方式)→`git push origin HEAD:main`。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡。

## 3. STOP条件
採用方式・ポーズ・対象の変更が必要/既存承認仕様と両立不可/上限60円・日次1,000円超過見込み(evidence延期で対応できない場合)/重大品質問題/他agentとのconflict解消不能(停止して報告)。

## 4. 報告(Fableへ、X/Z別)
(1)M1〜M4・I1〜I11・R1〜R4の反映対応表 (2)配線完了状況と要件1〜9の充足表 (3)runtime evidence要約(未実施なら理由と計画) (4)Trial方式との一致確認(planner fixture一致・音響同一性) (5)retry/fallback/regeneration/resume整合の根拠 (6)回帰結果(clean worktree)と他agent起因の分類 (7)量産原価・処理時間の実測 (8)SSOT・commit・raw URL (9)未解決Open (10)RESULT_PACKET 4行+「判定整合」1行。Status候補はX/Z別に`WIRED_PENDING_FABLE`まで(PRODUCTION_WIRED判定はFable)。