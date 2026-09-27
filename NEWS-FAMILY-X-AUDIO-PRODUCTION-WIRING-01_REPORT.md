# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT

## Stage 3a(2026-09-27): Meta記事(Entertainment News)のruntime実行

Stage 1(commit `32430691`、runner/plan実装+dry-run、¥0)の続き。実TTS/ASR/
Assembly APIを実行し、runtime evidenceを取得した。入力はユーザー確認済みの
Meta run_01(`er019_output/family_x_b3_production_wiring_01/run_01`)。

### 1. 実行前に判明したbug(所有ファイル内、最小修正)
Stage 1では`--stage scaffold/tts/assemble`が未実行だったため顕在化しな
かった、`er019_family_x_audio_production_runner_01.py`内の2件の実装bugを
本Stageで修正した(既存Production module=`er003_*`/`er006_*`/`er020_*`等は
無編集):
1. `main()`のA2 `japanese_title`受け渡しが、`a2/article.md`の英語title
   をそのまま渡すStage 1時点のplaceholderのままだった。正式path
   (NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01)が生成した
   `ja_writer/runtime_evidence.json["title"]`から日本語titleを取得する
   `derive_japanese_title()`を追加し、これを使うよう修正。
2. `run_plan_stage()`の`article_sha256`が常に`None`固定だった。実際の
   sha256を計算するよう修正(`sha256_text()`追加)。

あわせて、要求されていた成果物(player.html、cost budget guard、cost
logger install)を本ファイル内に追加実装した(`build_player_html`/
`assert_budget_ok`/`compute_cost_jpy_so_far`/`cl.install()`呼び出し)。
Unit test 25/25 PASSを維持(dry-runの¥0・副作用ゼロ契約も回帰確認済み)。

### 2. 入力article.mdの不変性
- `a2/article.md` sha256(raw bytes、`sha256sum`): 
  `5fed4170a97251f1e679bb179139177da4ca32e41b2b127f20117facdd8806a2`
- `b1b/article.md` sha256(raw bytes、`sha256sum`):
  `d60ec9241e9b83974e5bc9e9da5d5a341438abd7e85e25fccb0645bbd4a8f50a`
- 実行前後で再計算し、完全一致(不変)を確認済み。

### 3. 実行結果サマリ
- scaffold(Comment1-4+Preview+Key Phrase選定、A2/B1B): 完了。両levelとも
  Key Phrase `canonicalization status=CANONICALIZATION_PASS`。
- tts(全segment、A2/B1B): ほぼ全segment`status=OK`。**例外2件が
  既存Placeholder Notation Gate(`er003_v1_n3_01_tts_generate.py`、
  ER-006-KP5-CANONICAL-BUG-01由来、Key Phrase以外の日本語TTS経路にも
  適用済み)によりSTOPPED**:
  - A2 `japanese_title`: canonical text中の"…"(三点リーダー)を
    未発話placeholder記号と判定しTTS呼び出し自体を実行せずSTOP。
  - B1B `key_phrases`の`kp1`(rank1)日本語gloss: canonical text中の
    "〜"を同様に検出しSTOP。
- assemble(A2/B1B): **両levelとも既存Audio Validation Gate
  (`asm.verify_episode_audio_validation_gate`)が正しく発火し、
  `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`でepisode assemblyを中止**
  (A2: `japanese_title=STOPPED`起因、B1B: `kp1_japanese=STOPPED`起因)。
  Gateを回避・無効化する変更は一切行っていない。

### 4. STOP(回避せず報告)
上記2件は、いずれもcanonical text(A2日本語titleはja_writer正式path由来、
B1B KP1 glossはscaffold LLM生成物)に、既存Gateが「読み上げ不可な記法」と
判定する記号("…"/"〜")が含まれていたために生じた。本委任範囲では
Production module編集・記事本文/Key Phrase内容の書き換えは行っていない。
Fable/ユーザー判断が必要な選択肢(実装はしていない):
  (a) 該当箇所を含むgloss/titleをKey Phrase再選定・ja_writer再生成
      経路で作り直す(既存retry/regeneration機構の範囲内)。
  (b) "…"/"〜"を読み上げ可能な形へ機械的に正規化するルールをGate側へ
      追加する(既存Production module=`er003_v1_n3_01_tts_generate.py`/
      `er009_ja_foreign_token_gate_01.py`系の変更が必要、ユーザー承認要)。
  (c) 当該2箇所のみ人手でテキストを差し替える。
どちらも本Sonnet単独では選択・実装しない。

### 5. 詳細
runtime evidence全文・segment表・cost・regression結果は
`docs/pm/RESULT_PACKET_FXA2.md`参照。

## Stage 3b(2026-09-27): Hormuz記事(News)のruntime実行

Stage 3aと同じrunnerで、別記事(`er019_output/family_x_b3_diversity_trial_01/
hormuz/run_02`、サブパスを含むslug`family_x_b3_diversity_trial_01/hormuz`)を
実行した。`derive_out_dir()`は既存実装のまま(単純文字列結合)でスラッシュ入り
slugからネスト出力先(`.../family_x_b3_diversity_trial_01/hormuz__run_02`)を
問題なく生成でき、所有ファイルの改修は不要だった(`--dry-run --stage plan`で
事前確認済み)。

### 1. 入力article.mdの不変性
- `a2/article.md` sha256(raw bytes): `e29b21c67f2140393001cbeefebe47db4fae3559979d6f0c7b17b20955106137`
- `b1b/article.md` sha256(raw bytes): `5290325c6c663aff67f762a0f0eae29dfe76451c5524cdfa457f856233fcf987`
- 実行前後で再計算し完全一致(不変)を確認済み。

### 2. 実行結果サマリ
- scaffold: 完了(¥8.89、A2/B1Bとも`key_phrases_status=CANONICALIZATION_PASS`。
  A2 Key Phrase Redundancy QAはretry 1/2で解消)。
- tts: 累計¥120.66(openai=17.30/gemini=97.24/openai_asr=6.11/azure=0.00、
  Guardrail¥150以内)。**Placeholder Notation Gate該当文字("…"/"〜")は
  今回のtitle/gloss群に一切含まれず0件発火**(Meta run固有の事象だった
  ことを確認)。一方、**既存のConnected Speech cool-down(10分固定)・
  Local Rewrite回復機構(TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-
  WIRING-01)が本記事で複数回実測発火**:
  - A2 `full_story_part2`: 標準2回exhausted(attempt2は`$83.30`→`$83.37`
    の数値誤認識でTRUE_CONTENT_MISMATCH)→10分cool-down→fallback
    (attempt3)も見出し境界読み上げの問題でTRUE_CONTENT_MISMATCH→
    **全3回exhaustedのままSTOPPED→HUMAN_REVIEW_REQUIRED**(回復せず)。
  - B1B `full_story_part1`: 標準2回とも`sub_reason=protected_number`
    ("Act One"をASRが"Act 1"と表記)でTRUE_CONTENT_MISMATCH→cool-down→
    fallback(attempt3)でNORMALIZED_MATCH回復(OK)。
  - B1B `full_story_part2`: 標準2回失敗(見出し句"The 20% plan"の近接
    反復をrepetition QAが検知)→cool-down→fallback(length超過)→
    Local Rewrite 2回(attempt4/5)も同種のrepetition/length再発で失敗。
    **全5回exhaustedのままSTOPPED→HUMAN_REVIEW_REQUIRED**(回復せず)。
  - B1B `full_story_part3`: 標準2回TRUE_CONTENT_MISMATCH→cool-down→
    fallback失敗→Local Rewrite(attempt4)でNORMALIZED_MATCH回復(OK)。
  - B1B `comment_4`: 標準2回ASR_VALIDATION_UNCERTAIN("point"→"points"
    複数形誤認識、Azure corroborationも不一致=救済不成立)→cool-down→
    fallback(attempt3)も同様→Local Rewrite(attempt4)でNORMALIZED_MATCH
    回復(OK)。
  - B1B `key_phrases`の`kp2`(rank2)日本語gloss:「海からの封鎖」を
    3回ともASRが「海からの風さ」等に誤認識しTRUE_CONTENT_MISMATCH→
    **STOPPED→HUMAN_REVIEW_REQUIRED**(Key Phrase日本語roleはConnected
    Speech対象外のためcool-down/Local Rewriteは適用されない、既存仕様
    どおり)。
  - B1B `comment_1`は`NUMERIC_EQUIVALENCE_MATCH`(Tier1数値救済)が
    attempt1から直接成立(OK)。
  - 上記以外の全segment(A2側は`full_story_part2`以外全て、B1B側は
    `full_story_part2`/`kp2_japanese`以外全て)はattempt1(一部2)でOK。
- assemble(A2/B1B個別実行): **両levelとも既存Audio Validation Gateが
  正しく発火しRuntimeErrorでepisode assemblyを中止**
  (A2: `['full_story_part2=STOPPED']`、
  B1B: `['full_story_part2=STOPPED', 'kp2_japanese=STOPPED']`)。
  Gateを回避・無効化する変更は一切行っていない。player.html/timeline.json/
  manifestは生成されていない(Meta run同様、Point Notification音・
  「ポイント解説」はFAMILY_X_A2_SEGMENT_ORDER/FAMILY_X_B1_SEGMENT_ORDER
  に一切含まれないため機械確認不要)。

### 3. ASR Phase B(semantic_equivalence)telemetry
`er021_output/en_asr_semantic_equivalence_production_wiring_01/
telemetry.jsonl`は他Agentの並行実行と共有されるため単純な行数差分は
使えず、本記事の canonical text断片(`Strait of Hormuz`/`20% plan`/
`center stage`)で内容照合した。本記事由来の新規記録9件、全て
`FULL_STORY` role: `TRUE_CONTENT_MISMATCH`(`sub_reason`:
`content_word`×4、`protected_number`×3)/`ASR_VALIDATION_UNCERTAIN`
(`sub_reason`: `entity_only`×2)。`SECONDARY_ASR_CORROBORATED_MATCH`
(Tier3救済)/`NUMERIC_EQUIVALENCE_MATCH`(Tier1救済、ただし前述の
`comment_1`はこのTelemetryとは別経路でTier1救済がattempt時点で直接
成立したため本telemetryには現れない)発火は本9件中0件。

### 4. STOP(回避せず報告、3件)
- A2 `full_story_part2`(HUMAN_REVIEW_REQUIRED): 3回(標準2+fallback1)
  全てTRUE_CONTENT_MISMATCH。attempt2/3は数値`$83.30`→`$83.37`の
  誤認識、attempt3(内容自体は数値一致)は見出し"The 20% plan changes
  overnight"が後続文と読点で連結され独立文として読まれなかった可能性。
- B1B `full_story_part2`(HUMAN_REVIEW_REQUIRED): 5回(標準2+fallback1+
  Local Rewrite2)全て失敗。見出し句"The 20% plan"が本文冒頭付近で近接
  反復するテキスト構造をrepetition QAが繰り返し検知(intentional=false
  判定)、Local Rewriteで別span("20%"の読み方等)を修正しても同じ
  反復パターンは解消しなかった。
- B1B `key_phrases` `kp2`(rank2)日本語gloss(HUMAN_REVIEW_REQUIRED):
  「海からの封鎖」の TTS読み上げをASRが3回とも誤認識(例:「海からの
  風さ」)。
いずれもテキスト書き換え・Gate回避は行っていない。Fable/ユーザー判断が
必要な選択肢(実装はしていない、Stage 3aの(a)/(b)/(c)に準ずる別種の
STOPのため個別に列挙):
  full_story系2件は(a)該当span[見出し文または数値文]をLocal
  Rewrite以外の経路[記事本文自体の軽微な言い回し変更・別テイクの
  人手選定]で再生成、または(b)人手でHuman Review Lockを承認、のいずれか。
  kp2は(a)「海からの封鎖」をKey Phrase再選定・gloss再生成、または
  (b)人手でHuman Review Lockを承認、のいずれか。
Sonnet単独では選択・実装しない。

### 5. 詳細
runtime evidence全文・segment表・cost内訳・cool-down/Local Rewrite
発生件数・regression結果は`docs/pm/RESULT_PACKET_FXA3.md`参照。
