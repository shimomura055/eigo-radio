## 管理ID

CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02(Opus条件Aレビュー反映: X/Y側の是正M1・R1〜R5+X Std/Y Std・Advのruntime evidence取得。Z側(M2/M3/R6/R7)は`er063`がZ文脈TTS evidence取得中のため**次委任**=本委任ではer063を編集しない)。並行Agent: FZ Phase 2 evidence(er063使用・有料)、Y男性7Voice Trial(有料・`er121_*`読取)、KP再実証(KP系)。本委任の所有=`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/**`、`er117_chunk_tts_production_01.py`、`er019_family_x_audio_production_runner_01.py`、`er121_family_y_{structure,audio}_01.py`(chunk関連部分)、対応test、evidence run dir(`er019_output/family_x_audio_production_wiring_01/<slug>__run_stdchunk_ev_01/`、`er121_output/family_y_std_chunk_evidence_01/`)、`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_{DELEGATION_02,OPUS_REQUEST_01}*`、`docs/pm/RESULT_PACKET_CHKW2.md`。SSOT・ACTIVE_TASKは編集しない。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(APPROVED_FOR_PRODUCTION、Std/Adv)の配線是正+runtime evidence。到達上限=X Std/Y Std・Adv: EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。Z Std: 次委任。
- Fable照合: Opus所見は承認済み仕様内の不具合修正・設計反映でユーザー判断事項なし→**M1・R1〜R5を全件採用、実装へ進む**。M2/M3/R6/R7はZ次委任へ引継ぎ(DESIGN_02 §6へ反映のみ)。
- 禁止: `er063`編集禁止/公開済み音声・manifest・公開ページの上書き禁止(evidenceは新規run dir。X Stdは既存記事を**新規run名**で再生成し、公開物へは反映しない)/新しい分割規則・減速率・ポーズ長の変更禁止/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)/wav・raw_usage_log・STOP・lock・RUN_LOCKはcommitしない。
- 有料run規律: `.venv\Scripts\python.exe`、`TTS_EXECUTION_MODE=STANDARD`、各起動前`py tools/stop_scope_check_01.py`(rc=0)、起動間隔150秒以上(`Get-Date`記録)、同一run 5分以内3回起動禁止。**並行2案件が同一TTS backendを使用中**: 429/5xx等の技術失敗はevidenceとして扱わず記録し、150秒以上空けて再実行。連続3件でSTOP報告。T-2追記4点(差分再生成可否・cache有無・`--budget-jpy`明示・想定外全再生成はSTOP)。
- 費用上限: 「上限¥100(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」見積=BUDGET_PLAN_01(X Std 1記事3 part+Y dev入力Std/Adv各1 segment≒約25〜30円、Z分は次委任)。
- 修正範囲(11-8): 範囲内=Opus M1(旧方式Std結果への部分指定retryで本文が失われる不具合)、R1(検査位置)、R2(欠損素通し)、R3(test)、R4(Adv不変補強)、R5(固定文言)。範囲外=分割規則・閾値・方式の変更。
- Opus独立技術レビューGate: 条件A実施済み(本委任は反映)。
- 時間見込み: 2.5〜3時間(M1+R1〜R5 60〜80分、evidence run 60分[起動間隔含む]、集計・報告30分)。並列化: 他案件と並列。本委任内は是正→test→evidenceの直列(是正後のコードでevidenceを取る)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約216+進行中(Y Trial Cap 250・Z Phase 2 Cap 200・KP ≤15)/本委任見積JPY約25〜30/承認区分: C。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。上記定型文に従う。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 645 --out docs\pm\delegation_log\2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_DELEGATION_02.md`(先頭が「## 管理ID」+「CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02」でなければ641〜656を順に試す)。Opus依頼文(prompt先頭「## 管理ID\nCHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 Opus独立技術レビュー」、index 643付近)も`..._OPUS_REQUEST_01.md`へ保存。check実行は委任_02分。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md` §2(保存済み)。要点: 「初回Production生成、retry、fallback、regeneration、resumeへ一貫して反映する。」「各Family／各レベルの正式runtimeで、分割位置・Chunk数・追加ポーズの発火証拠を取得する。」「X/Zで既に確認済みのAdvanced動作を回帰させない。」「Yで分割対象となる段落構造を持つ入力に対して正式経路が正しく発火することを検証し、実記事が1段落のため不発火ならその事実を記録する。」「コード配線済み・テストPASSだけで、実際には確認できていないruntime evidenceを取得済みと扱わないこと。」

## Opusレビュー原文(逐語。`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/OPUS_REVIEW_01.md`へ一字も変えず保存。先頭に`# OPUS_REVIEW_01(条件A・実装後レビュー、2026-10-26、read-only、JPY0。以下Opus所見の逐語)`の1行を付ける)

## CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 Opus独立技術レビュー(条件A・実装後レビュー、read-only、0円)

**判定: 条件付き承認。** 合成方式は妥当です。X/Yには実装後に直す点が1件(M1)、Zには実装前に反映すべき点が2件(M2・M3)あります。どれも承認済み仕様の範囲内の不具合修正・設計反映であり、ユーザー判断が必要な事項はありません。

### 論点別の判定

**1. 合成方式: 問題なし**
- 「chunkごとに減速→減速後に4800サンプルの無音→連結」は、既存関数をそのまま使っています(`er003_v1_n3_01_tts_generate.py:331-432`、`er008_a2_postprocess_slowdown_01.py:32-58`)。
- 連結後に減速しない理由は十分です。次の4点です。
  - ポーズが減速されて固定値0.2秒が変わる(WSOLAで縁がぼやけ、無音の連続長は4569サンプルになる)。これは承認値の改変にあたる。
  - 合成長検査(`er117:265-269`)が成り立たない。
  - 減速後のASR再検証と取り直しの単位が親全体になり、chunk単位の部分再生成ができなくなる。
  - 親wav全体を減速する新しい後処理経路が必要になる(承認されていない)。
- margin(chunk前後に残す無音)が6%伸びる件は、承認範囲内です。Stdは「TTSが出した音声全体を6%減速」が既存仕様で、非chunkのStdでも段落間の間は6%伸びています。chunk化しても、追加ポーズが正確に0.2秒であることは変わりません。補正は入れないのが正解です。
- Phase 2で実測・報告(Gateにはしない)してほしい項目:
  - 境界ごとの可聴無音(前chunk末尾の無音+0.2秒+次chunk先頭の無音)。Std実測と、`_original.wav`から求めたmargin×1.06を並べる。
  - 同じ記事のAdv実測(`RUNTIME_EVIDENCE_01.md:10`)との差。
  - pad端に段差・クリックが無いこと(peak確認)。

**2. 共有Gateの穴と補い方: 問題なし(R1・R2を推奨)**
- 親の集約値は抜け道になりません。根拠は次の4つが連鎖していることです。
  - 集約値はchunk entryに明示記録された`slowdown_applied is True`と比率だけから導出される(`er117:335-367`)。
  - chunk wavのshaは共有Gateの`_segment_asset_hash_stale`で照合される(`er003_v1_n3_01_assemble.py:494`)。
  - 親wavがchunk wavの生連結であることを、音声を読む前に`verify_raw_parent`が整数サンプルで確認する(`er019:2545-2547`)。
  - 親には明示的なTrue/Falseが入るため、古い`full_story_partN_original.wav`を弱い証拠とする経路(`er003_v1_n3_01_assemble.py:278-294`)には落ちない。
- 共有moduleを変えなかった判断は妥当です。Family A/B/Cへ波及し、並行Agentの領域でもあり、Zも同じ部品を使うためです。

**3. retry/fallback/regeneration/resume: 要修正(M1)**
- 一部chunkだけ減速済みの途中状態からの再開、`_k`の直接指定、HR Lock後の親entry、失敗後の後続chunk続行は、いずれも安全側に止まります(`er117:408-471`、`er019:963-972,1094-1118`、継承entryは深いcopyで減速記録を保持=`er019_family_x_validation_inheritance_01.py:126`)。
- 穴は1つです。旧方式で生成したStd結果に`--only-segments`で本文以外だけを指定すると、検証済みの本文が失われ、組立が止まります(詳細はM1)。

**4. Adv不変: 概ね十分(R4を推奨)**
- golden・`CHUNK_PLANNER_VERSION`・`attach_chunk_meta`/`evidence_record`の検査で、planとmetaの不変は担保されています。
- 音声経路とaudit出力の不変までは直接証明できていません。Yの`chunk_tts_decision.json`(b1b)とページ凡例の文言は変わっています(表示・監査のみで、音声には影響しません)。

**5. Z Std設計: 要修正(実装前、M2・M3)**
- 一番大きい穴は速度Gateです。速度Gateの対象idはplanのclip id=chunk idで、親は含まれません(`er063:1672-1673`)。このため、§6の撤去作業と速度Gateの拡張を同時に入れないと、Stdのchunk化narratorが減速検査ゼロで通ります(fail-open。詳細はM2)。
- 文脈TTSとの干渉はありません。文脈抽出前の畳み戻しadapter `story_clips_from_plan`(`er122_fz_ctx_notes_01.py:170-188`)はレベルに依存しないため、Stdでchunk展開しても文脈入力とdialogueのreuse_keyは変わりません。
- 「約70語を目安」について: 承認済みの規則はB_r1そのものです(閾値100語・k=ceil(語数/100)・等分割・最小25語)。対象のStd clip(122〜139語)では約61〜70語×2になり、Adv実績(58/62、65/61、74/50語)とも合います。ユーザーへの再確認は不要です。Phase 2で実際のchunk語数を記録してください。71〜100語のclipを分割しないのはAdvのB_r1と同じ扱いです。

**6. Y: 承認範囲内**
- 新しい規則は追加していません。
- 報告で正確に書くべき点があります。Yの記事parser(`er121_family_y_structure_01.py:152-183`)は、各segmentを1段落または1行として作ります。つまり「今の記事が1段落だから不発火」ではなく、**現行の本文契約では、正式な記事から作ったparts.jsonはchunk化の条件を構造的に満たせません**。Y StdのPRODUCTION_WIREDは「配線済み・現行契約では発火経路に到達しない」と明記してください。
- 複数段落のdev入力で正式runnerの`tts→gate→assemble`を通せば、「正式経路が発火すること」の検証になります。dev入力は、実在するY runのparts.jsonに、文の境界で空行だけを挿入したものを推奨します。本文の文字列が空白差以外は同一なので、KP source gate(本文中にKey Phraseが実在するかの検査)やarticle.mdとの整合は保たれます。
- 実記事の不発火は、既存runの`chunk_tts_decision.json`(`chunked:false, paragraphs:1`)で記録できます(追加費用0)。

**7. 試聴ページ「Standardは分割対象外」表示の同一委任内是正: 妥当**
- 利用者に見える文言が承認済み仕様と食い違っていたため、11-8の「仕様文と実装の乖離の是正」にあたります。旧記録を「旧記録」と明示した分岐も適切です。
- 1か所だけ残りがあります(R5)。

### M(必須修正)/R(推奨)一覧

**X/Y(実装後の是正)**

- **M1(X Std。同じ潜在不具合が10-25配線のX Advにもある)**
  - 症状: 旧方式のStd結果(親entryのみ)に`--stage tts --only-segments comment_2`のような本文以外の指定をすると、次の順で組立が止まります。
    1. 本文chunkは前回cacheに無いため`SKIPPED_NOT_SELECTED`になる(`er019:1094-1104`)。
    2. 親は`CHUNKS_NOT_ALL_VALIDATED`の集約entryで上書きされる(`er019:1995`、`er117:457-470`)。
    3. 組立時は親に`chunk_tts`が付くため旧方式と判定されず(`er117:554-563`)、組立がBLOCKになる。
  - 復旧するには本文の再TTSが必要になり、費用がかかり、公開済み本文の音声も変わります。
  - 修正案: 生成時に、親もそのchunk idも`_ONLY_SEGMENTS`に含まれず、かつ前回cacheが`is_legacy_unchunked`である親は、従来経路(親名で`_generate_or_reuse`による引継ぎ)を通す。
  - test: 旧方式Std結果に本文以外を指定→本文のTTSは0回、旧方式経路で組立がPASS。
  - 本文を含む通常のresumeはchunk化して再生成する、という現行挙動は承認文の「resumeへ一貫」に合っています。そのまま維持し、SSOTに既知事項として記録してください。
- **R1**: `std_chunk_slowdown_violations`を、`load_family_x_a2_sources`(`er019:2545`の直後)と`_load_y_body_chunks`(a2のとき)にも置く。現状はstage関数の中にしか無く、`er019_coffee_s3_support_regen_01.py:190`のような直接呼び出しでは検査を通りません。共有Gateがload関数の中にある構造と揃えるためです。
- **R2**: chunk entryで`slowdown_info`の`src_duration_seconds`/`dst_duration_seconds`が欠けていたら違反にする(`er117:353-356`は現状、欠けていると素通しになる)。新しいchunkは必ずこの両方を記録するので(`er003_v1_n3_01_tts_generate.py:248-249`)、誤ってブロックすることはありません。
- **R3**: testを3つ追加する。
  - (a) 集約値Falseの親が、古い親`_original.wav`の弱い証拠で救済されないこと。
  - (b) 減速後NG→HR承認済みのchunkで、親がOK・集約値True・組立PASSになること。
  - (c) planに存在しないchunk id(例 `full_story_part1_k9`)を指定したら拒否または警告すること。現状は何も起きずに素通りします。
- **R4**: Adv不変の補強。
  - `git diff bb578265c`の各差分箇所(hunk)が、a2専用関数か、既定値がAdvの共通helperの中にしか無いことを機械的に確認する。
  - mockの生成器でAdvのgenerate+assembleを新旧両方のcommitで実行し、results jsonと合成wavのバイト一致を取る。
  - b1bの`chunk_tts_decision.json`をgoldenにする(差分は注記文言だけと明示)。
- **R5**: `er121_family_y_audio_01.py:1100`の「(今回はありません)」が固定文言になっている。`n_chunked>0`なら出し分ける。

**Z(実装前に反映)**

- **M2**: `_CLIP_ID_RE`の絞り込みは**2か所**あります。関数内の`er063:1731`と、呼出側の`er063:1865`です。両方を広げたうえで、chunk idについては次を満たすこと。
  - `chunk_tts.std_chunk_slowdown_violations(chunk_plans_from_specs(plan), segments)`で`slowdown_applied is True`と比率を厳格に要求する。
  - `_original.wav`による弱い証拠の救済は使わない。
  - §6の「親は集約値で判定」はこのGateには届きません(親が対象idに入っていないため)。
  - test: 減速の無いStd chunkで`FamilyZSlowdownGateStop`が出ること。
- **M3**: 次の変更を同一commitで入れること。
  - `er117:156-157`のレベル条件の撤去と`er063:598`の撤去。
  - `er063:1561`の`attach_chunk_meta(..., level=spec.level)`。
  - `_z_chunk_parent_display`(`er063:636`)をa2のときだけ集約にする。b1bは`None`のまま=バイト不変と、`er063:1805`の検査を維持する。
  - `drop_cached_std_chunks_without_slowdown`を、`load_results`の直後(`er063:1525-1528`の並び)に置く。理由は、`--only-clips`で選ばれなかったclipの再利用(`er063:1540-1545`)が`generate_or_reuse_z`を通らないためです。
- **R6**: Stdでchunk展開したplanに`story_clips_from_plan`を掛けると、非chunk時と同一になることを確認するtestを追加する(猿の手Std15・メロスStd10のTrialとの一致が維持されること、dialogueのTTSは0回)。Z Stdの実装は、並行Agent(FZ)のcommitの後に行うこと。FZのStd evidence runは、後でTTSをresumeすると100語超のnarratorがchunkで再生成されます。その旨を記録してください。
- **R7**: Std chunkでLocal Rewrite(`er063:1553-1555`)を経た出力に減速が掛かっていることをtestで固定する(漏れてもM2の厳格Gateで止まりますが、止まる前に確認できるように)。

### PRODUCTION_WIRED判定に必要なruntime evidenceの過不足

- **X Std(1記事3 part)**: 概ね十分です。次を足してください。
  - 同じ引数でtts stageをもう一度起動し、新規TTSが0回(chunkの再利用)であること。
  - 各chunkの`_original.wav`と減速後wavの比率一覧。
  - 論点1の境界無音の実測。
  - Gate通過の記録と費用(旧方式Std runとのJPY比較)。
  - M1修正後の旧方式経路はoffline testで足ります。
- **Y Std/Adv(複数段落のdev入力)**: 「発火」の証拠としては十分です。上記の空行挿入版の入力を推奨します。実記事の不発火は既存のdecision fileで記録し、構造的に発火経路へ到達しない旨を明記してください。
- **Z Std(1〜2 clip)**: 量は十分ですが、DESIGN §7のstage列(`provision_shell,gate,assemble,pages,page_verify`)には**tts stageが入っていません**。`--only-clips <親id>`付きのTTS実行が必要なので、起動計画を確認してください。chunkの語数、厳格Gateの判定、dialogueのTTSが0回であることを記録してください。

### 要約
- 合成方式(chunkごとの既存6%減速→減速されない0.2秒→連結)は妥当です。marginが伸びる件も承認範囲内で、補正は不要です。
- X/YのGate補完は抜け道になっていません。ただし、旧方式Std runへの部分指定retryで本文が失われる不具合(M1)を直す必要があります。
- Zは、速度Gateの`_CLIP_ID_RE`を2か所とも広げて厳格化することと、撤去作業の同時実施(M2・M3)が無いと、Stdのchunkが無検査で通ります。
- Yは承認範囲内ですが、現行の本文契約では構造的に発火しないことを明記してください。
- ユーザー判断が必要な事項はありません。Z StdのPhase 2起動計画にtts stageが入っていない点は確認してください。

(Opus原文ここまで)

## 実施事項

1. **M1**(X Std。X Advにも同潜在不具合=同時に是正): 親もそのchunk idも`--only-segments`に含まれず、前回cacheが`is_legacy_unchunked`の親は従来経路(親名で`_generate_or_reuse`引継ぎ)。test: 旧方式Std結果に本文以外指定→本文TTS 0回・旧方式経路で組立PASS。Adv側も同test。通常resume(本文含む)はchunk化再生成=現行維持(SSOT既知事項文案)。
2. **R1**: `std_chunk_slowdown_violations`を`load_family_x_a2_sources`直後と`_load_y_body_chunks`(a2)にも配置。**R2**: `slowdown_info`の`src/dst_duration_seconds`欠損を違反に。**R3**: test (a)(b)(c)。**R4**: `git diff bb578265c`の各hunkがa2専用/既定値Advの共通helper内のみであることの機械確認script+mock生成器で新旧commitのAdv generate+assembleのresults json・合成wavバイト一致+b1b `chunk_tts_decision.json` golden(差分=注記文言のみ)。**R5**: Y `er121_family_y_audio_01.py:1100`付近の固定文言を出し分け。
3. 回帰(遮断下、`.venv`でのtest実行は前委任と同条件): er117/er019/er121全PASS(前委任の件数以上)。
4. **Runtime evidence(有料)**: 
   - X Std: 既存記事1本(例 uk_train_manners。実在slugをGlobで確認)を新規run名`run_stdchunk_ev_01`で`--level a2 --stage tts,gate,assemble`(公開pagesなし)。記録: `chunk_tts_decision.json`、chunk plan(分割位置・語数・chunk数)、各chunkの`_original.wav`/減速後wav比率、0.2秒無音の位置・サンプル数、TTS call数、Gate通過、費用(旧方式Std runのJPYと対比)、境界ごとの可聴無音実測(前chunk末尾無音+0.2秒+次chunk先頭無音)とmargin×1.06の並記、同記事Adv実測との差、pad端のpeak/段差。**同じ引数で再起動し新規TTS 0回(chunk再利用)**を確認(150秒以上空ける)。
   - Y Std/Adv: 実在Y run(`er121_output/family_y_production_01/redelivery_fee/run_01`)のparts.jsonに**文境界で空行を挿入しただけ**のdev入力(本文文字列は空白差以外同一)を`er121_output/family_y_std_chunk_evidence_01/`配下に作り、正式runnerの`tts→gate→assemble`(pagesなし)を各レベル1 segment(`--only-segments`相当で本文1つ)で実行。記録項目はXと同じ。実記事の不発火は既存run_01の`chunk_tts_decision.json`(`chunked:false, paragraphs:1`)を証拠として転記し、「現行の本文契約(parser `er121_family_y_structure_01.py:152-183`が各segmentを1段落/1行で作る)ではchunk化条件を構造的に満たせない」旨を明記。
5. `EVIDENCE_01.md`(Family×レベル表: X Std/Y Std/Y Adv取得分、X Adv/Z Adv既存、Z Std次委任)、`COST_01.md`、`DESIGN_02.md`(Opus M/R対応表、Z側M2/M3/R6/R7の実装指示を§6へ統合、Z Phase 2 stage列に`tts`を追加し`--only-clips <親id>`を明記)、`FIX_02.md`、`docs/pm/RESULT_PACKET_CHKW2.md`。

## 事前指定Read一覧

1. `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{DESIGN_01,FIX_01,BUDGET_PLAN_01}.md`、`docs/pm/RESULT_PACKET_CHKW1.md`。
2. Opus引用行: `er019_family_x_audio_production_runner_01.py` :940-980, :1085-1125, :1985-2000, :2535-2555、`er117_chunk_tts_production_01.py` :330-370, :400-475, :550-570、`er019_family_x_validation_inheritance_01.py` :115-135、`er121_family_y_audio_01.py` :1090-1110と`_load_y_body_chunks`、`er121_family_y_structure_01.py` :150-185、`er003_v1_n3_01_assemble.py` :270-300, :485-500、`er019_coffee_s3_support_regen_01.py` :180-200。
3. 既存X Adv run(`uk_train`等)の`audit/chunk_tts_decision.json`・`chunk_plan_b1b.json`(境界無音比較用)。
4. `tools/stop_scope_check_01.py --help`。

## 実行コマンド全文

- test: `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe run_project_regression.py --pattern "er117*_test_*.py"`、同`"er019*_test_*.py"`、`"er121*_test_*.py"`(前委任と同条件。接続試行0または前後同数)。
- X Std evidence(例、実値で): `py tools\stop_scope_check_01.py`→`Get-Date`→`$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <実在slug> --run run_stdchunk_ev_01 --level a2 --stage tts,gate,assemble --budget-jpy 20`(stage指定の実引数は`--help`で確認)。150秒後に同コマンド再実行(再利用確認)。
- Y evidence(例): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er121_family_y_runner_01.py --theme-dir er121_output\family_y_std_chunk_evidence_01\redelivery_fee_multipara --run run_01 --levels a2 --stages tts_a2,gate,assemble --approved-budget-jpy 20`(実引数・stage名は`--help`とrunner定数[`APPROVED_BUDGET_MAX_JPY=170`]で確認。dev入力の作り方はrunnerの入力仕様に合わせ、公開dirへ書かない)。
- 計測script: `py docs\research\CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01\tools\chunk_evidence_measure_01.py --run <run dir> --out …\measure\<name>.json`(0.2秒無音位置・サンプル数、境界無音、比率、peak)。
- Production不変(er063): `git diff --stat -- er063_family_z_audio_01.py`(本委任由来0)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`。

## SSOT追記文

文案のみ: CURRENT_SPEC Chunk TTS節(Std/Adv両対象、合成方式、Y=現行契約では構造的に不発火、M1既知事項)、DECISION_LOG(Opus M/R採用・X/Y Std evidence)、OPEN-532更新、OPUS台帳OF-CHKW-M1〜M3/R1〜R7文案。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- commit 2分割: (1)Opus原文+DESIGN_02+是正実装+test (2)evidence(研究dir内のmd/json/measure、wav不可)。
- message例: (1)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: Opus M1/R1〜R5反映(旧方式Std部分指定retryの本文喪失是正、検査位置・欠損違反・Adv不変補強、test追加)` (2)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: X Std/Y Std・Adv runtime evidence(chunk発火・0.2秒・減速比率・再利用0回、実費<X>円、Z Stdは次委任)`。
- `git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(M/R反映表、X Std/Y Std・Adv evidence取得状況、PRODUCTION_WIRED判定材料の充足/不足) (2)6行表更新(runtime列に実測値) (3)evidence詳細(分割位置・語数・chunk数・0.2秒位置・比率・TTS call数・再利用0回・Gate・境界無音実測とAdv比較・peak) (4)Y: 発火証拠(dev入力)と不発火記録(実記事)、構造的理由 (5)test結果・Adv不変(R4) (6)費用(起動時刻・実費・累計/Cap 100、技術失敗の有無) (7)Z次委任の実装指示(M2/M3/R6/R7、tts stage・`--only-clips`) (8)SSOT文案 (9)commit×2・raw URL (10)一覧外Read (11)Fable向け懸念。最終行に要約10行以内。