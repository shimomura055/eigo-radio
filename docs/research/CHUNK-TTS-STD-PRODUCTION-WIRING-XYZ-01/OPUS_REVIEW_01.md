# OPUS_REVIEW_01(条件A・実装後レビュー、2026-10-26、read-only、JPY0。以下Opus所見の逐語)

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
