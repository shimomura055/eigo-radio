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

## Stage 3c(2026-09-27): 見出しsegment分離の実装+Hormuz本文2再TTS+small_bag音声化

Stage 3bのSTOP 3件中2件(A2/B1B `full_story_part2`)は、見出し文と本文
冒頭の反復をrepetition QA/ASRが誤検知したことが原因と分析されていた。
本StageでCURRENT_SPEC「Family X音声構造」節の`DESIGN NOTE`(見出しを
本文segmentへ含める解釈)を、見出しsub-segment分離へ変更した(構造・
順序・効果音方針そのものは無変更、Fable技術判断としてユーザー既決仕様の
範囲内)。

### 1. 実装差分
- `er019_family_x_audio_plan_01.py`: `FAMILY_X_B1_SEGMENT_ORDER`/
  `FAMILY_X_A2_SEGMENT_ORDER`へ`full_story_part2_heading`/
  `full_story_part3_heading`(`plan_role=HEADING_READOUT`)を本文2/3の
  直前に追加。DESIGN NOTEを更新。
- `er019_family_x_audio_production_runner_01.py`:
  - `build_segment_plan()`: 見出し/本文の見積りテキストを`heading1`/
    `body2`/`heading2`/`body3`(語の二重計上なし)へ変更。
  - TTS生成: 見出しはB1B=`er003_v1_sing01_point_headings_aoede.generate()`
    (Family A`point_one_heading`と同一関数、Aoede)、A2=
    `er003_v1_n3_01_tts_generate.generate_a2_segment_with_slowdown()`
    (Family A A2の`point_one_heading`と同一関数、6%減速)を再利用(新規
    TTS経路は作らない)。本文2/3は見出しを含まない`body2`/`body3`のみを
    渡す。
  - Assembly: 見出し→本文間のpauseは新規値を追加せず、Family A既存の
    `er003_v1_n3_01_assemble.HEADING_TO_BODY_PAUSE_SECONDS_B1`(B1B)/
    `er003_v1_crosslevel_audio_02_common.POINT_EXPLANATION_PAUSE_SECONDS`
    (A2、いずれも0.7秒)を再利用。`_row_info_family_x()`をplayer.html行
    対応のため更新(見出しlabelを本文labelより先に判定、prefix一致の
    誤マッチを回避)。
  - **実装中に発見した既存コードの安全性ギャップ(自己発見・自己修正)**:
    旧`_generate_or_reuse()`はキャッシュのstatus=="OK"+wavファイル存在
    のみで再利用可否を判定しており、`full_story_part3`のようにsegment_id
    は同じでもcanonical textが変わった(見出し除去)場合、**旧audio
    (見出しを含んだまま)を誤って再利用し、見出しが二重に読まれる欠陥**
    があった。`expected_text`引数を追加し、キャッシュされた
    `canonical_text`と完全一致する場合のみ再利用するよう修正(全10箇所の
    既存呼び出し元を更新、`expected_text`省略時は既存呼び出し元の挙動を
    変えない後方互換)。実データで実際に発生することを確認: Hormuz A2/B1B
    とも旧`full_story_part3`の`canonical_text`は見出し+本文の結合済み
    テキストで`status=="OK"`(Stage 3b Local Rewriteで回復済み)、新設計の
    期待text(bodyのみ)と不一致のため両方とも正しく自動再生成された。
  - `run_theme_scaffold`のKey Phrase Gate(既存、無変更)がSTOPし
    `keywords_canonicalized.json`が書かれないケース(small_bag B1Bで実際に
    発生)で、tts/assemble stageが未処理`FileNotFoundError`でクラッシュ
    する問題を発見。Gate自体は回避せず、ファイル不在時にKey Phrase生成の
    みを明示的にスキップし他segmentの生成は継続する防御を追加
    (`generate_family_x_b1/a2_segments`)、assemble側も
    `status="BLOCKED_KP_SCAFFOLD_MISSING"`を返して`player.html`まで
    到達できるようにした(`stage_assemble_family_x_b1/a2`)。
  - unit test: 既存25件PASSを維持し、見出し順序・plan_role・`resolve_
    narrative_role`(新segment_idはer020未認識のためNone、実効値は
    Family Aの`point_one_heading`=HEADING_READOUTと同じFalseで挙動差なし)・
    `_generate_or_reuse`安全性回帰を7件追加、**計32/32 PASS**
    (`.venv/Scripts/python.exe -m unittest
    er019_family_x_audio_production_runner_01_test_01 -v`)。

### 2. 入力article.mdの不変性
- Hormuz: 実行前後で完全一致(sha256、Stage 3bと同一値)。
  `a2/article.md`=`e29b21c67f2140393001cbeefebe47db4fae3559979d6f0c7b17b20955106137`、
  `b1b/article.md`=`5290325c6c663aff67f762a0f0eae29dfe76451c5524cdfa457f856233fcf987`。
- small_bag: 実行前後で完全一致。
  `a2/article.md`=`131c783730d48d3f1fd6daf4aed277a8018c5e67d78fd7113eec64dcb5c65df2`、
  `b1b/article.md`=`eb5cea40c24d32883a1de7aa852d5ceb2a7102db4de5ee563ec9fd27b1ed0e10`。

### 3. Hormuz再TTS結果(見出し分離後)

| segment | A2 | B1B |
|---|---|---|
| full_story_part2_heading(新規) | OK(attempt1、NORMALIZED_MATCH) | OK(attempt1) |
| full_story_part2(body、旧STOPの再検証) | **HUMAN_REVIEW_LOCKED**(下記STOP参照) | **STOPPED**(下記STOP参照) |
| full_story_part3_heading(新規) | OK(attempt1、NORMALIZED_MATCH) | OK(attempt1) |
| full_story_part3(body、text変更のため再生成必須) | **OK(attempt1、NUMERIC_EQUIVALENCE_MATCH)** | **OK(attempt1、NORMALIZED_MATCH)** |
| full_story_part1/in_one_line/comment_1-4/preview/KP(kp2除く) | 再利用(canonical_text一致、0 API call) | 同左 |
| KP2(rank2)日本語gloss「海からの封鎖」 | (A2側は該当なし) | 変更なし(既存STOP継続、0 API call、本タスクでは触っていない) |

**重要な肯定的所見**: `full_story_part3`はStage 3bでB1BのみLocal
Rewrite(attempt4)を要したが、見出し分離後は**両levelとも1回の試行で
クリーンにOK**(cool-down/Local Rewrite発火0件)。見出し文分離が、
見出し句の反復をrepetition QAが誤検知していたStage 3bの故障モードを
解消したという直接的な証拠。

### 4. Hormuz `full_story_part2` STOP(新規、回避せず報告)
見出し分離後の`full_story_part2`(body、"About 24 hours and 48 minutes
later, at **11:04 a.m.** on July 14, ..."で始まる)は、**Stage 3bとは
別の既存Gate(Placeholder/Symbol Normalization Gate、
`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`、Stage 3bと
Stage 3cの間に別管理IDでProduction配線済み)がTTS呼び出し自体を実行せず
STOP**した(0 API call、既存Human Review Cost Guard機構により2回目以降の
再実行も自動的に0 API callでブロックされることを確認済み)。
- 検出理由: `RESIDUAL_PLACEHOLDER_OR_PAUSE_SYMBOL`カテゴリでtoken`:`
  (コロン)がNormalizer通過後も残存(`%`/`$`は`NUMERIC_SYMBOL_OBSERVE`
  カテゴリでblock対象外、観測のみ)。
- 原因: 本文中の**時刻表記"11:04 a.m."のコロン**が、既存Normalizer
  (`tts_safe_news_en`等、shared Production module)の変換パターンで
  カバーされていないため。同じコロンは旧(見出し込み)combined textにも
  存在しており、**本STOPは見出し分離が原因ではなく、Stage 3bとStage 3c
  の間に新しく配線された記号Gateが今回初めてこのtextに対して発火した**
  (Stage 3b時点ではこのGate自体が存在しなかった)。
- 対応: テキスト書き換え・Gate回避は一切行っていない。Fable/ユーザー
  判断が必要な選択肢(実装はしていない、Stage 3a/3bの(a)/(b)/(c)に準ずる):
  (a) 該当箇所を含むJA/EN本文を既存retry/regeneration経路で作り直す、
  (b) 時刻表記(`H:MM`パターン)の読み上げ安全な正規化ルールをNormalizer
  (shared Production module、承認要)へ追加する、(c) 人手でHuman Review
  Lockを承認する。

### 5. small_bag(run_02)実行結果

scaffold: A2 `key_phrases_status=CANONICALIZATION_PASS`。**B1B
`key_phrases_status=KEY_WORDS_STRUCTURE_INVALID`**(既存Key Phrase
構造Gate、rank1「have a big moment」の"have"が有限助動詞として検出され
STOP、リトライ機構なし[既存仕様どおり、選定からの再試行はRedundancy QA
段のみでStructure Gate段には無い]。Gateを回避・再試行の追加実装はしていない)。
scaffold費用¥4.54(openai)。

TTS(A2、full pipeline完走):

| segment | 結果 |
|---|---|
| topic_intro/japanese_title/preview/comment_1/comment_3/comment_4/full_story_part1/in_one_line | OK |
| full_story_part2_heading/full_story_part3_heading(新規) | OK |
| **comment_2** | **STOPPED**(2回試行、内容+長さ不一致) |
| **full_story_part2**(body) | **STOPPED**(2回試行後ASR不一致) |
| **full_story_part3**(body) | **ASR_VALIDATION_UNCERTAIN**(同一mismatch signature継続) |
| KP1-5(en/meaning) | 全OK |

TTS(B1B、Key Phrase以外):

| segment | 結果 |
|---|---|
| topic_intro/preview/comment_1-4/full_story_part1/in_one_line | OK |
| full_story_part2_heading/full_story_part3_heading(新規) | OK(見出し"ELLE's small-bag examples"はASRが"L's small bag examples"と転記したが、ELLEの発音上の同音性を既存Tier救済[verified=True]が採用しOK確定。既存機構、新規実装なし) |
| **full_story_part2**(body) | **STOPPED**(2回試行後ASR不一致) |
| **full_story_part3**(body) | **ASR_VALIDATION_UNCERTAIN**(固有名詞"Altuzarra"を"also Zara"とASR誤認識、救済不成立) |
| Key Phrase(5件) | 未生成(scaffold Gate STOPのため、上記防御によりKey Phrase以外のsegmentは正常に生成継続) |

**small_bag STOPの性質**: `comment_2`(Comment役割、本タスクの変更対象外)
も同様にSTOPPEDしており、`full_story_part2`/`full_story_part3`のSTOPは
見出し分離とは無関係な、記事固有の内容(フランス語/固有名詞由来の
ブランド名"Altuzarra"・"minaudière"等)に対するTTS/ASRの一般的な難易度に
起因すると判断する(Hormuzの`full_story_part3`が両levelともクリーンに
OKだった事実と対比すると、見出し分離自体は正しく機能している)。

### 6. Assembly / Gate確認
- Hormuz A2: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`
  (`['full_story_part2=UNVALIDATED']`)。
- Hormuz B1B: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`
  (`['full_story_part2=STOPPED', 'kp2_japanese=UNVALIDATED']`)。
- small_bag A2: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`
  (`['comment_2=UNVALIDATED', 'full_story_part2=UNVALIDATED',
  'full_story_part3=UNVALIDATED']`)。
- small_bag B1B: `BLOCKED_KP_SCAFFOLD_MISSING`(上記防御により
  `run_summary_assemble.json`へ明示記録、クラッシュなし)。
- 4件とも既存Gateが正しく発火し、Gateを回避・無効化する変更は一切
  行っていない。player.html(4記事×levelとも生成、Assembly未完了の
  levelは"status=..."を表示するのみで音声再生不可、既存Meta/Hormuz
  Stage 3a/3bと同じ挙動)。timeline.json/manifestは未完了levelでは
  生成されない(Gate通過前に停止、既存仕様どおり)。Point通知音・
  「ポイント解説」の不在はFAMILY_X_*_SEGMENT_ORDERにPoint系segment/SFXが
  一切含まれないことをコードで確認済み(Stage 3a/3bと同じ確認方法)。

### 7. ASR Phase B(semantic_equivalence)telemetry
`er021_output/en_asr_semantic_equivalence_production_wiring_01/
telemetry.jsonl`は他Agent並行実行と共有書き込みされる(Stage 3b注記と
同じ制約)。canonical text断片照合(Hormuz: `20% plan`/`Strait of
Hormuz`/`11:04`、small_bag: `minaudi`/`division of labor`/`stage
crew`/`ELLE`)による粗い件数: Hormuz 11件(Stage 3b時点の9件+本Stageの
+2件、内訳はA2 `full_story_part2`の旧Batch-mode誤設定run[§8参照]での
2回のTTS+ASR試行に対応)、small_bag 59件。ただしKP Trial(er023_*)等の
並行Agentが同じ記事語彙断片を扱っている可能性を排除できないため、この
件数は目安であり正式な件数根拠としては採用しない(Stage 3bと同じ限界)。
本タスクの正式な根拠は各`tts_generation_results.json`の`attempts_log`
実測値とする(§3/§5に反映済み)。

### 8. STOP(実装中の運用ミス、回避せず報告)
Hormuz実行の1回目試行で、`TTS_EXECUTION_MODE`環境変数を`STANDARD`へ
明示設定し忘れ、既定値`BATCH`のままrunnerを起動してしまった
(委任文で指定された`TTS_EXECUTION_MODE=STANDARD`との不整合)。A2
`full_story_part2`/`full_story_part2_heading`に対し計4回のBatch経路
TTS呼び出し(実コスト計約¥4.56、Gemini Batch API経由)が発生した時点で
気づき、プロセスをkillして`TTS_EXECUTION_MODE=STANDARD`を明示指定し
再実行した(以降は全てStandard経路)。Batch経由で生成された当該2
segmentの音声は、後続の再実行でcanonical text不一致検知(§1の自己修正
バグfix)により自動的に再生成されたため、最終成果物には混入していない。
既存retry/Gate機構への影響・Production module変更は無し。

### 9. Cost / Wall clock
- Hormuz(累計、Stage 3b分含む): ¥127.27
  (openai=17.30/gemini=102.91/openai_asr=7.05/azure=0.00)。
  本Stageの純増分: 約¥6.61(検出できたAPI課金分。§8のBatch経由4回分
  [約¥4.56、`gemini_batch`は現行cost集計ロジックの対象外プロバイダ名の
  ため合算されない既知の集計ギャップ]を含めた実質純増は約¥11)。
- small_bag: ¥148.47(openai=37.77/gemini=103.02/openai_asr=7.68/
  azure=0.00、Guardrail¥150に対し目安¥60〜100を上回った。理由:
  (1)OOM強制終了[システム側のメモリ不足によるプロセス強制終了、
  ¥ロス分は小さいが再試行が必要になった]、(2)`comment_2`/
  `full_story_part2`/`full_story_part3`(A2)3件が2回ずつ試行後にSTOP、
  (3)B1B見出し2件でTTS_FAILURE/ASR_VALIDATION_UNCERTAINの追加試行が
  発生、が主因。Cap¥150は超過していない)。
- 本Stage合計純増(Hormuz+small_bag): 約¥155(検出集計分)、Guardrail
  ¥250の範囲内・報告閾値¥200未到達。

### 10. Gate 3 checklist
| # | 項目 | 状態 |
|---|---|---|
| retry/fallback/regeneration整合 | 既存TTS/ASR retry・cool-down・Local Rewrite・Placeholder/Symbol Gate・Human Review Lock(Cost Guard含む)・Key Phrase構造Gate・Audio Validation Gateは無改変のまま動作(独自バイパスなし)。所有ファイル内の`_generate_or_reuse`拡張はGate判定ロジックそのものではなく、自ファイル内キャッシュ再利用の安全性強化 | 充足 |
| runtime evidence(実TTS/Assembly) | 本REPORT §3/§5/§6、実API呼び出し実測。Assembly完走は4記事×level全てGate STOPのため未達(理由は既存Gateの正常動作、§6) | 充足(完走未達の理由明記) |
| actual model/routing | TTS: Gemini(Charon/Aoede、STANDARD経路)。ASR: openai_asr+Azure(corroboration)。見出しsub-segment: 既存point_one_heading系関数を無変更のまま再利用 | 充足 |
| regression/validator/integration test | 対象runner unit test: 25→32件(7件追加)、32/32 PASS(実装後・実行後に再実行し再確認)。全体regression(`run_project_regression.py`)は他Agent並行実行中のため今回は未実行(Stage 3bと同じ判断、対象ファイル無変更部分は影響なしと推定されるが正式根拠にはunit testのみを採用) | 一部限定(理由明記) |
| SSOT記載案 | CURRENT_SPEC.md「Family X音声構造」節の`DESIGN NOTE`(現行「本文2/3の見出しは本文segment内で読み上げる」)を「見出しをsub-segment(`full_story_part2_heading`/`full_story_part3_heading`)として分離する(Family A point_one_heading同一機構)」へ更新する案。Fable/ユーザー判断待ち、本タスクではSSOT自体は編集していない | 提案のみ(未反映) |
| Git | 所有ファイル(plan/runner/test)+出力ディレクトリ配下のJSON/audit/raw_usage_log(wav除く)+REPORT追記のみpath指定add | 充足 |
| Dangling Reference Check | 既存関数(point_headings/generate_a2_segment_with_slowdown/asm定数/crosslevel_common定数)は無変更のままimport、新規参照のみ追加 | 充足 |

## Stage 3d(2026-09-27): 残STOP解消の試行とAssembly状況確認

管理ID: `NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`。委任文全文は
`docs/pm/delegation_log/2026-09-27_NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_05.md`
に保存済み。Guardrail¥300に対し、本Stageの実測純増costは**¥0**(全ての
実行がHuman Review Lockにより0 API callでブロックされたか、既存cache
再利用[0 API call]だったため)。

### 0. Lock棚卸し(実行前、¥0)

3記事×A2/B1Bの全segmentについて`review_lock_state.json`を走査した結果:

| 記事/level | HUMAN_REVIEW_REQUIRED(Locked)なsegment | 原因分類 |
|---|---|---|
| Meta A2 | `japanese_title`(final=STOPPED, attempts=2) | OPEN-199待ち(句読点ギャップ、本Stageでは触らない) |
| Meta B1B | (無し、全segment RESOLVED/OK) | — |
| Hormuz A2 | `full_story_part2`(final=STOPPED, attempts=0) | 時刻コロンGate STOP由来のLock(本Stage対象外、後述) |
| Hormuz B1B | `full_story_part2`(final=STOPPED, attempts=0)、`kp2_ja_charon`(final=STOPPED, attempts=3) | 前者=時刻コロンGate STOP由来のLock(本Stage対象)。後者=「海からの封鎖」ASR誤認識、既にPhase 2 JA-3で回復見込み確認済みだが**ユーザー承認待ちLock解除** |
| small_bag A2 | `comment_2`/`full_story_part2`(final=STOPPED, attempts=2)、`full_story_part3`(final=ASR_VALIDATION_UNCERTAIN, attempts=2) | ブランド名ASR失敗由来のLock(本Stage対象) |
| small_bag B1B | `full_story_part2`/`full_story_part3`(final=ASR_VALIDATION_UNCERTAIN, attempts=1) | ブランド名ASR失敗(EN resolverはA2英語経路のみ配線、B1B英語[`voice01.generate_charon_english`経由]は未配線のため対象外、Phase 2 REPORT §21既知の残課題) |
| small_bag B1B | Key Phrase 5件(未生成) | scaffold Key Phrase構造Gate STOP(後述、item 2) |

**「ユーザー承認待ち」としてLock解除を保留したsegment(本Stageでは
`approve_regenerate()`等の解除操作を一切行っていない)**:
`hormuz__run_02/b1b`の`kp2_ja_charon`(「海からの封鎖」、Phase 2 JA-3で
Candidate Eが正しく機能することを確認済み、ユーザーが承認すれば次回
再生成時にPASSする見込みが高い)。

**発見(本Stageで判明、既存の別ファイル間の不整合、修正はしていない)**:
small_bag A2の`meaning_5`(Key Phrase5 日本語gloss「目を引く」)は
`review_lock_state.json`上は`HUMAN_REVIEW_REQUIRED`/`STOPPED`
(attempts=2)のまま**更新されていない**が、実際の最終結果を保持する
`tts_generation_results.json`(`key_phrases["5"]["japanese_meaning"]`)
は`status="OK"`(fallback attempt3、`audio_classification=EXACT_MATCH`、
Stage 3c実行時の2026-09-27T16:21頃に確定済み)。原因: Key Phrase
Japanese meaning経路は標準2回分のみ内側の`generate_narration_snippet_
verified_strict`(`@review_lock.guarded_generate_with_language_arg`で
guard)で完結してrecord_outcome()が先に(不合格として)確定してしまい、
その後さらに実行されるfallback(minimal instruction)側の成功が、外側の
呼び出し元では別途guardされていないためLock storeへ反映されない、という
既存コードの構造的なギャップと判断する(Key Phrase英語Component
[`generate_key_phrase_component_verified`]はreentrancy guardで二重会計を
防いでいるが、Key Phrase Japanese meaning経路には同じ保護が無い可能性)。
本Stageではこの経路のコード自体は変更していない(Production module
修正はスコープ外、Fableへ報告のみ)。実害としては、Assembly Gate
(`verify_episode_audio_validation_gate`)は`tts_generation_results.json`
(正しい方の"OK")を参照するため、`meaning_5`がAssemblyを誤ってブロック
することは無いことを§5で確認した。

### 1. Hormuz B1B `full_story_part2`(時刻コロン修正後の再TTS)

実行コマンド(逐語):
```
set -a && source .env && set +a && TTS_EXECUTION_MODE=STANDARD ./.venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug family_x_b3_diversity_trial_01/hormuz --run run_02 --level b1b --stage tts --budget-jpy 160
```
結果: 累計cost=127.27円→127.27円(**変化なし、0 API call**)。
`full_story_part2`の結果は`status="HUMAN_REVIEW_LOCKED"`
(`human_review_lock_status="HUMAN_REVIEW_REQUIRED"`)。

**重要な発見(想定外、正直に報告)**: Symbol Normalization Gateの修正
(`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`修正1・2回目、
時刻コロンを`RESIDUAL_PLACEHOLDER_OR_PAUSE_SYMBOL`から除外)は既に
Production配線済みだが、**Human Review Lock(`er011_human_review_lock_01.
py`)は、canonical text(script本文)が変更されない限り、Gate側の修正が
入ったかどうかに関わらず、以前STOPPEDに到達したsegmentへの新規TTS/ASR
呼び出しを一律ブロックする**設計になっている
(`check_before_generation()`: `canonical_text_sha256`が前回Lock時と
一致する限りstate=`HUMAN_REVIEW_REQUIRED`のままproceed=Falseを返す、
`generate_english_segment_with_fallback`/相当のB1関数もこの返り値を見て
fallbackにも進まない設計)。本文自体は書き換えていない(article.md不変)
ため、canonical textは前回と完全一致し、この安全装置が正しく作動した。
コードを読んで検証し、実際に上記コマンドを実行して**0 API call・Lockの
まま**であることを実測で確認した(推測ではない)。

**結論・必要な判断**: Symbol Gateの修正自体は正しく機能する状態にあるが、
**このLockを解除しない限り、`full_story_part2`は再TTSされない**。
選択肢(実装はしていない):
  (a) ユーザーが`er011_human_review_lock_01.approve_regenerate()`を
  明示的に承認する(次回`--stage tts`実行1回に限り再挑戦を許可)、
  (b) 承認しない場合は現状のHuman Review Lockのまま維持する。
Sonnet単独ではLockを解除していない。Hormuz A2側の`full_story_part2`
(同じ時刻コロン原因、委任文では対象外のため本Stageでは触っていない)も
同一の理由で同じLock状態のまま残っている。

### 2. small_bag B1B Key Phrase構造Gate("have")

`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_
trial_01/small_bag__run_02/b1b/key_phrases/keywords_runtime_metadata.json`
を確認した。rank1候補`"have a big moment"`(source_span
`"having a big moment"`)が、`er003_key_words_production.py`の構造
validatorにより「有限助動詞(is/are/was/were/has/have/had/will/would/
can/could/should/may/might/must)が含まれている」で`KEY_WORDS_STRUCTURE_
INVALID`と判定されている(`attempts_detail`は1件のみ)。

既存コードを確認した結果、この構造Gate自体には内部retryが無い
(`er003_v1_n3_01_scaffold_generate.py`の`run_key_phrase_selection()`が
`prod.run_production_selection_gate(..., max_attempts=1)`で単発呼び出し
[190-215行付近])。呼び出し元`run_key_phrases()`(同ファイル322-341行
付近)が持つ`KEY_PHRASE_REDUNDANCY_RETRY_MAX`回の再選定ループは、
**Redundancy QA(5件相互の意味重複)がNGだった場合のみ**選定からやり直す
設計であり、`sel["status"] != "KEY_WORDS_STRUCTURE_PASS"`の場合は
即座に`return`してこのループへ入らない(340-341行)。すなわち
**Structure Gate段には既存仕様として自動再選定経路が存在しない**
(Fable委任文の想定どおり)。

Gateを回避・独自の再試行実装は行っていない。本Stageでの対応はSTOP
(コード読解による確認のみ、追加API呼び出し・追加cost無し)。Key Phrase
5件は引き続き未生成のまま(`kp_scaffold_status="KEY_WORDS_STRUCTURE_
INVALID"`)。

### 3. small_bag A2 `comment_2`/`full_story_part2`/`full_story_part3`(EN resolver経由の再TTS)

実行コマンド(逐語):
```
set -a && source .env && set +a && TTS_EXECUTION_MODE=STANDARD ./.venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug family_x_b3_diversity_trial_01/small_bag --run run_02 --level a2 --stage tts --budget-jpy 160
```
結果: 累計cost=148.47円→148.47円(**変化なし、0 API call**、
`perplexity`provider列も0.0のまま=EN resolverのweb lookup発火0件)。
3segmentとも`status="HUMAN_REVIEW_LOCKED"`
(`human_review_lock_status="HUMAN_REVIEW_REQUIRED"`)。

Stage 3d §1と同一の理由(Human Review Lockがcanonical text不変を検知し
即ブロック)により、**Phase 2で配線されたEN resolver
(`pron_resolver_core.resolve_and_augment_en_style_prefix`)は、
`generate_narration_snippet_verified_strict()`関数本体の冒頭
(288行付近)で呼ばれる設計だが、その手前にある`@review_lock.
guarded_generate_with_language_arg`デコレータのLockチェックが先に
ブロックするため、resolverのコード自体が実行される機会が無かった**
(0 lookup、0 hint注入、これも実測で確認した想定外の事実であり、
"EN resolverを通して再TTSする"という委任文item 3の前提が、Lock解除
無しでは成立しないことが判明した)。ブランド名(Altuzarra/minaudière等)
自体は既にPhase 2 EN-3 evidence(`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-
FAMILIES-PRODUCTION-01_REPORT.md`§17 EN-3)で「これらの語を含む本番文で
hits=0」と確認済みであり、そもそも現状のPronunciation Ledgerには
Altuzarra/minaudière自体の発音hintがまだ登録されていない(誤guessを
注入する誤動作の心配は無いが、資すべき有用なhintも無い)。

**結論・必要な判断**: item 3も同じくLock解除がなければ実行の余地が
無い。選択肢(実装はしていない): (a)ユーザーが`approve_regenerate()`を
承認する、(b)現状のHuman Review Lockのまま維持する(既存retry予算内で
不合格の最終結果として確定済み扱い)。Sonnet単独ではLockを解除していない。

### 4. Meta A2 `japanese_title`(Muse)

OPEN-199(JA ASR Validatorの句読点処理ギャップ、`PRONUNCIATION-
RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md`§17 JA-1/§22-1
既述)が未修正のため、委任文の指示どおり**再TTSを実行していない**
(0 API call、現状維持)。`review_lock_state.json`は
`state=HUMAN_REVIEW_REQUIRED`, `final_status=STOPPED`, `attempts=2`の
まま。

### 5. Assembly状況

| 記事/level | Assembly | 詳細 |
|---|---|---|
| **Meta B1B** | **完了(既存artifact確認)** | `b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_PRODUCTION_WIRING_01.wav`(duration=303.468s, peak=0.8456, clipping無し)・`run_summary_assemble.json`(`status="OK"`)・`player.html`が既に存在(mtime 2026-09-27 14:12〜14:13、`kp1_ja_charon`のLock更新[14:10:06]の直後)。**本Stageで新規に生成したものではない**(既存artifactを読み取り検証したのみ、生成主体は本Stage開始前の別プロセス[時刻から推定するとStage 3c完了後〜本Stage開始前の間]。生成し直してはいない)。全16 narration segment[見出し2件含む]がRESOLVED/OKであることをLock棚卸しで確認済み、`run_summary_assemble.json`のstatus="OK"と整合。 |
| Meta A2 | 未完(既存) | `run_summary_assemble.json`不在(=Gate遮断のためsummary書き込み前に中止、既存仕様どおり)。`player.html`は`status=NOT_ATTEMPTED_OR_GATE_BLOCKED_BEFORE_SUMMARY_WRITE`と表示。原因: `japanese_title`STOPPED(§4、OPEN-199待ち) |
| Hormuz A2 | 未完(再確認) | `--stage assemble`を実行し`RuntimeError: EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(`['full_story_part2=UNVALIDATED']`)を実測確認(既存Gate、無改変)。原因: §1のLock(ユーザー承認待ち) |
| Hormuz B1B | 未完(再確認) | 同上、`RuntimeError`(`['full_story_part2=UNVALIDATED', 'kp2_japanese=UNVALIDATED']`)。原因: §1のLock+`kp2_ja_charon`Lock(いずれもユーザー承認待ち) |
| small_bag A2 | 未完(再確認) | 同上、`RuntimeError`(`['comment_2=UNVALIDATED', 'full_story_part2=UNVALIDATED', 'full_story_part3=UNVALIDATED']`)。`meaning_5`はブロックリストに含まれない(§0の発見どおり、Assembly Gateは正しい方[tts_generation_results.json]を見ている証拠)。原因: §3のLock(ユーザー承認待ち) |
| small_bag B1B | 未完(再確認) | RuntimeErrorは発生せず`run_summary_assemble.json`に`status="BLOCKED_KP_SCAFFOLD_MISSING"`相当の防御的記録(Stage 3c実装のまま、既存挙動を再確認)。原因: Key Phrase未生成(§2)+`full_story_part2`/`full_story_part3`のASR_VALIDATION_UNCERTAIN |

4件の再確認assemble実行(Hormuz A2/B1B、small_bag A2/B1B)はいずれも
API呼び出しを伴わない(Gate判定のみ)ため、cost増分は0円。

### 6. CURRENT_SPEC「Family X音声構造」DESIGN NOTE追記

実行前に`git status -- CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md`を
確認し、未commit差分が無いことを確認した上で、`CURRENT_SPEC.md`
「Family X(Entertainment News)音声構造」節の解釈注記(旧:「本文2/3の
見出しは本文segment内で読み上げる」)へ、Stage 3cで実装したsub-segment
分離方式への更新を追記した(構造・順序・効果音方針は無変更、既存
`point_one_heading`機構の再利用である旨・unit test 25→32件・Meta run_01
B1BでのAssembly完走[§5]を根拠として明記)。`DECISION_LOG.md`/
`OPEN_ITEMS.md`への追加記載は行っていない(Fable/ユーザー判断に委ねる、
本Stageの委任範囲はCURRENT_SPECの当該箇所のみ)。

### 7. 費用まとめ

| 項目 | 費用 |
|---|---|
| Lock棚卸し(§0、read-only) | ¥0 |
| Hormuz B1B `full_story_part2`再TTS試行(§1) | ¥0(0 API call、Lockブロック) |
| small_bag B1B Key Phrase Gate確認(§2、コード読解のみ) | ¥0 |
| small_bag A2 3segment再TTS試行(§3) | ¥0(0 API call、Lockブロック) |
| Meta A2 `japanese_title`(§4、実行せず) | ¥0 |
| Assembly再確認4件(§5、Gate判定のみ) | ¥0 |
| **本Stage合計** | **¥0**(Guardrail¥300に対し十分小さい) |

### 8. Gate 3 checklist(本Stage分)

| # | 項目 | 状態 |
|---|---|---|
| retry/fallback/regeneration整合 | Human Review Lock・Audio Validation Gate・Key Phrase構造Gateはいずれも無改変。`approve_regenerate()`は一切呼んでいない | 充足 |
| runtime evidence | §1/§3で実際にコマンドを実行し、cost不変・`HUMAN_REVIEW_LOCKED`応答を実測確認(推測ではない) | 充足 |
| Production module変更 | 無し(本Stageはコード変更ゼロ、SSOT追記[§6]のみ) | 充足 |
| SSOT | `CURRENT_SPEC.md`Family X音声構造節へ追記(§6)。`DECISION_LOG.md`/`OPEN_ITEMS.md`は未編集(Fable判断待ち) | 一部(SSOT本体のみ反映) |
| Git | 変更ファイル(REPORT・CURRENT_SPEC・delegation_log・review_lock_state.json等の出力JSON)のみpath指定add | 充足 |
| Dangling Reference Check | コード変更ゼロのため対象なし | 該当なし |

### 9. 残STOP一覧(分類、Stage 3d時点)

| segment | 分類 | 次のアクション |
|---|---|---|
| Meta A2 `japanese_title` | OPEN-199待ち | OPEN-199修正後に再検討 |
| Hormuz A2 `full_story_part2` | ユーザー承認待ちLock解除 | `approve_regenerate()`承認後に`--stage tts --level a2`再実行 |
| Hormuz B1B `full_story_part2` | ユーザー承認待ちLock解除 | `approve_regenerate()`承認後に`--stage tts --level b1b`再実行 |
| Hormuz B1B `kp2_ja_charon` | ユーザー承認待ちLock解除(Phase 2 JA-3でPASS見込み確認済み) | 承認後に再実行 |
| small_bag A2 `comment_2`/`full_story_part2`/`full_story_part3` | ユーザー承認待ちLock解除 | 承認後に`--stage tts --level a2`再実行(EN resolverはLock解除後に初めて発火する) |
| small_bag B1B `full_story_part2`/`full_story_part3` | Human Review正常落ち(既存retry予算exhausted、EN resolver未配線[B1B英語経路]) | Fable/ユーザー判断待ち(resolver配線拡大の要否含む) |
| small_bag B1B Key Phrase 5件 | Human Review正常落ち(既存仕様上Structure Gateに自動retryなし) | 人手でのKey Phrase再選定またはGate仕様変更要否のユーザー判断待ち |

