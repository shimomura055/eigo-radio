# RESULT_PACKET: USER-TEST-FINAL-AUDIO-BATCH-06(委任D)

管理ID: USER-TEST-FINAL-AUDIO-BATCH-06(委任D: Discovery B1 part2分割TTS→Discovery A2 NG 2 segment個別retry)+FOLLOWUP-01項目4・5

## 1) T-0結果

`docs/pm/delegation_log/USER-TEST-FINAL-AUDIO-BATCH-06_D_check.json`: status=FAIL(reason: 実行コマンドセクションのコードフェンス行```を「引数/絶対パスを含まない行」と機械的に誤検出。必須キーワード8/8 PASS、固定ブロックE-1/D-1/G-1/F-1全PASS)。記録のみ、作業は継続。

## 2) Part 1 B1: full_story_part2の2segment分割TTS

- 分割点: canonical parts.json part2の**既存の`\n\n`段落境界**(P1「At the same time, silence can also bring calm...」+P2「Research on the body shows...」=2a、P3「People also differ across studies and cultures. In a study of about 2,500 college students in 11 countries...phone use...」=2b)。`SPLIT_CONCAT_EQUAL=True`(2a+2b連結が元part2と完全一致)、`TRANSFORMED_SPLIT_CONCAT_EQUAL=True`(読み整形後テキストも同様)。
- Lock解除: `approve_regenerate(full_story_part2a, ...)`/`approve_regenerate(full_story_part2b, ...)`各1回、state=REGENERATE_APPROVED。
- 2a: attempt1でHIGH_SIMILARITY_SAFE、verified=True(PASS、1回で成功)。**長segment後半のdelete block[段落丸ごと欠落]問題は分割により解消を確認**。
- 2b: 3回とも「a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed more than thinking for pleasure. This was true in every country tested. Still, differences...phone use. In one Japan-United States survey...」の内容を**全文含む**(delete block=0)。差分は3回とも「Japan–United」(canonical、enダッシュ)対「Japan-United」(ASR実音声、ハイフン)の1箇所のみ(attempt1/2はさらに軽微な句読点差異あり)。audio_classification=TRUE_CONTENT_MISMATCH、verified=Falseのままcascade(標準2+fallback1)上限到達でSTOPPED。
- 判定: **STOP**(委任STOP条件の追加自動retry禁止・Gate緩和禁止に従う。delete blockは解消したがGate FAILが別要因で継続)。
- Assembly/Audio Validation/player: 未実施(2b未確定のためfull_story_part2.wavは更新せず、既存の6attempt目の音声のまま)。
- 費用: ¥13.55(TTS+ASR、`raw_usage_log_audio_completion.jsonl`実測、upper¥25以内)。再生成回数: 2a=1回、2b=3回(cascade1周分)。
- 個別対応候補(実装なし、3件以内):
  1. 「Japan–United」(enダッシュ)と「Japan-United」(ハイフン)を同一表記として扱うよう、Gateの表記正規化ルールへenダッシュ→ハイフン変換を追加する(既存Gate仕様変更、要ユーザー判断)。
  2. attempt3(句読点差異のみ)の実音声を人間が試聴し、内容的に問題ないと判断できればHuman Approval経路で採用する(既存Human Review運用)。
  3. tts_reading_transforms.jsonへ「Japan–United」→「Japan-United」の読み整形エントリを追加し、TTS入力自体をハイフン表記に統一する(既存の数字読み整形と同型の追加、要ユーザー判断)。

## 3) Part 2 A2: NG 2segment個別retry(full_story_part1のみ実施、point_two未着手)

- full_story_part1: `approve_regenerate`後、標準2+fallback1(計3回、通番attempt5/6/7)を実施。3回とも「brief,」「10-minute」等の軽微差異に加え、**「silence」(canonical)対「pause」(実音声)の語置換**が残存(attempt5/7は「silence」、attempt6は「pause」で不安定)。delete block・数字誤りはなし。audio_classification=TRUE_CONTENT_MISMATCH、verified=Falseでcascade上限到達。
- point_two: **未着手**。full_story_part1の1segmentのみでPart 2予算(¥15)を超過(実費¥21.01)したため、委任STOP条件(3)費用上限超過に該当し、そのままSTOP。
- 他14 content segment+kp/meaning計10segmentのwav sha256: 22/22件不変(再TTS・再ASrなし、`audio/a2/audit/ut06d_a2_targeted_retry_result.json`に記録)。
- 判定: **STOP**(full_story_part1=cascade上限到達でSTOP、point_two=予算超過で未着手)。
- Assembly/Audio Validation/player: 未実施。**既存`audio/a2/player.html`は2026-09-14時点の604語版由来のまま未更新**(530語版を反映していない、参照時に注意)。
- 費用: ¥21.01(full_story_part1のみ、上限¥15を超過)。word_count=530(WORD_COUNT_GE_500該当、ただし本Partでは公開せず)。
- Discovery Production 1生成セット総原価: ¥840.74(直前値)+¥13.55(B1)+¥21.01(A2)=**¥875.30**(`production_set_cost.json`更新済み)。
- 個別対応候補(実装なし、3件以内):
  1. point_two個別retryのための追加予算(¥15超過分、実測ベースで¥20〜25程度を目安)をユーザーに確認する。
  2. full_story_part1の「silence」対「pause」置換について、人間試聴でどちらの発話が実際に生成されているか確認し(attempt間で不安定)、Human Approval可否を判断する。
  3. A2の`generate_a2_segment_with_slowdown`はslowdown post-process分の追加ASR呼び出しがあり、単一segment(270語規模)のretryでも¥20超のコストがかかることが判明。今後の予算設定時にこの単価を反映する(恒久対策はdefer)。

## 4) ユーザー指示原文項目6(恒久課題の扱い)Closeout

- B1: 長segment後半block omissionは**2segment分割で解消を確認**(良い結果)。ただし新たに判明したenダッシュ/ハイフン表記のGate正規化Gapは今回対策せず、OPEN-153へ事実追記のみ。
- A2: TTSの同義語置換傾向(silence/pause)・ASR表記揺れ・A2 slowdown経路の想定コスト過小は今回対策せず、OPEN-135へ事実追記のみ。Production-wide対策・Validator新設・Gate緩和は一切実施していない。

## 5) Token節約報告

- Sonnet委任回数: 1(本委任のみ、Opus不使用)。
- 既存asset再利用: B1の他13完成segment、A2の他14 content+10 kp/meaning segment(sha256不変で確認)、run_discovery_audio_completion.pyのAssembly/Gate/Consistency/Web player関数を無変更で再利用(B1は未到達、A2も未到達のため実行はしていないが呼び出し口は流用設計)。
- 回避した再生成: B1の他13segment・A2の他14+10segmentへのTTS/ASR呼び出しをゼロ件に抑制(全16 segment再TTSする既存`generate_a2_segments`を直接使わず、targeted retry用の`--only-segments`引数を追加した個別呼び出しに変更)。

## 6) Web到達確認

Part 1・Part 2ともAssembly未完了のため、B1の`player.html`は依然として**未生成**、A2の`player.html`は**2026-09-14時点(604語版由来)のまま更新されていない**。委任文に列挙されたURL到達確認(4件)は、本タスクで生成/更新したcontentが存在しないため実施を見送った(既存URLへのGETは新規性がなく、確認する意味がないため)。

## 7) commit・push・残差分

- commit(D-B1): `eabc3ffb`(push済み)。
- commit(D-A2): 本RESULT_PACKET保存後にcommit予定、hashは下記追記または次回参照。
- 残差分: `er014_output/four_type_observation_01/discovery/audio/a2/narration/full_story_part1.wav`と関連attempt wav(gitignore対象、コミット外)、review_lock_state.json/tts_generation_results.json等の監査jsonのみ変更。本タスクに無関係な既存差分(er006_output/er011_output配下等)は触っていない。

## 8) unresolved issue(恒久defer事項)

- OPEN-153(B1): enダッシュ/ハイフン表記のGate正規化Gap。
- OPEN-135(A2): TTS同義語置換傾向・ASR表記揺れ・A2 slowdown経路のコスト見積り。
- 両方ともUSER_DECISION_REQUIRED。追加対応(個別対応候補の実施可否・追加予算)はユーザー判断待ち。

## 9) 事前指定外Read(理由付き)

- `er011_human_review_lock_01.py`の`check_before_generation`/`record_outcome`本体(199-330行付近)を事前指定のシグネチャ範囲より広く読んだ: 新segment名(2a/2b)に対するLockの実際の挙動(新規entry扱いでproceed=True)を正確に確認するために必要だった。
- `er003_v1_n3_01_assemble.py`のbuild_b1_timeline関数(583-639行): Assembly側がfull_story_part2をnarration wavパス経由でどう読むかを確認し、「音声レベル連結+既存Assembly無変更」というPart1の設計判断の妥当性を検証するために読んだ(事前指定外だが設計の安全性確認に必須と判断)。
- `er003_v1_n3_01_tts_generate.py`のgenerate_a2_segments全体・generate_a2_segment_with_slowdown・generate_english_segment_with_fallback(er003_v1_crosslevel_audio_02_common.py): Part 2の`--only-segments`実装のため、A2個別segment retryに使うべき既存Production関数を正確に特定する必要があった(事前指定ではrun_tts経由の言及のみだったが、run_ttsは全16segment一括のため個別呼び出し関数の特定が必須だった)。
