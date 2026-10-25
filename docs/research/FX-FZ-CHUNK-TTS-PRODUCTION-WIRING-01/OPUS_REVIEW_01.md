# OPUS_REVIEW_01(条件A: Chunk分割Production配線設計、2026-10-25、opus-consultant、read-only・API 0)

(委任_02の委任文§1より逐語保存。Fable照合済み。同内容の再レビューは不要。)

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
  設計(X-b)は「全chunk OKなら親を書く」+「失敗chunkでループ停止」です。この組合せだと、失敗chunkが人間承認された後、Gateには承認済みchunkだけが見え、未生成chunkも親も存在しない状態になります。Gate(`assemble:485`)は存在するentryしか走査しないので、ここが穴になります。
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
