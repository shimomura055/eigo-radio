# IMPLEMENTATION_DESIGN_02(FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_03、2026-10-12)

`IMPLEMENTATION_DESIGN_01.md`(v01、残置)に対し、Opus独立レビュー(条件A、2026-10-12)の必須修正M1〜M8・推奨・Fable判断を反映した版。v01と同じ節は要約し、差分は本書の各節に明記する。**本書の範囲は設計+課金0の先行実装(routing key・er020正規表現・Seed複製・先行test)まで。er061/er062/er063本体は後続並列委任(04A/04B/04C)。** 行番号は2026-10-12時点main。ユーザー正式決定①〜⑤(`DECISION_LOG.md`)は不変。

## 0. 状態
| 項目 | 状態 |
|---|---|
| 先行実装(routing key 7件、er020正規表現1箇所、Seed複製、test) | **完了**(委任_03、`er060_family_z_foundation_test_01.py` 9件PASS、関連suite新規failure 0) |
| er061 Validator / er062 Writer / er063 Audio / er026統合 | 未着手(04A/04B/04C、本書の契約に従う) |
| `PRODUCTION_WIRED` | 未達 |
| OPEN-297保留 | **Z範囲のみ解除**(Fable判断、DECISION_LOGに明記)。OPEN-276/279/281(X音声既知穴)はZへ持ち込まず、M1の検査関数で自衛 |

## 1. Opus必須修正M1〜M8の反映

### M1 Std英語6%減速のGate穴(担当04C: er063)
- 事実: `er003_v1_n3_01_assemble.py` L268のGate減速チェックは `A2_SLOWDOWN_TARGET_SEGMENTS`(`er003_v1_n3_01_tts_generate.py` L111-114: full_story_part1/2・point_*・in_one_line)外は即False。part3と`_cN`は未検査(共有moduleは**不変**)。
- 設計: `er063.verify_std_english_slowdown(out_dir, required_clip_entries, narration_dir)` を追加(Gate呼出の**前**に必ず実行、fail-closed)。対象=Std英語Story clip全て(`full_story_part{1-3}_c{k}`のNarrator・Dialogue両方)+Human Review経由で採択されたclip。各clipについて、`tts_generation_results.json`のentryが`slowdown_applied is True`、**または** `narration/{clip}_original.wav`と`{clip}.wav`の再生時間比(original/current ≈ 1.06、判定範囲 **[1.03, 1.09]**)を満たす。どちらも満たさないclipが1つでもあればGate前にSTOP(`FamilyZSlowdownGateStop`)。例外なし。
- test: part3相当ID・`_cN`ID・Human Review採択clip(entryにslowdown記録なし+`_original.wav`なし=FAIL、あり比1.06=PASS、比1.00=FAIL)。
- 参考(Z範囲外): X Stdのpart3にも同じ穴 → OPEN-304として記録。

### M2 Gate前のファイル存在assert(04C)
- 事実: `verify_episode_audio_validation_gate`(L471-473)は`audit/tts_generation_results.json`が無いと黙って`return`。
- 設計: `er063.assert_tts_results_complete(out_dir, required_clip_ids)` を**Gate呼出の直前**に実行。(i)ファイル存在、(ii)JSONとして読める、(iii)required clip(Part1-3の全clip、Comment1-3、Preview、KP全asset、shell)の**全entryが存在**し`status`が採択済み。欠落・不在はSTOP(fail-closed)。Gateの`return`を黙認経路にしない。test: ファイル不在/entry欠落/空dict。

### M3 ファイル配置の統一(04C、凍結)
- 事実: segment_id・Review Lock・Local Rewrite・Tier3は、パス `.../<theme>/<level>/narration/<segment>.wav` から導出(`er011` L119-152、`news_tail_fix` L199-201、`crosslevel_common` L340-342/L387-389)。Family Cのassembleは`audio_dir/<name>`規約でXと異なる。
- **Zの正本配置**: `er026_output/family_z_production_e2e_01/<slug>/<run>/{a2|b1b}/narration/<segment>.wav`(`a2`=Standard、`b1b`=Advanced。**<run>の下に<level>**。パス内に`narration`ディレクトリ1つ、その直下にwavを置く)。`audit/`は`<run>/<level>/audit/`。
- `_has_valid_narration_layout`(`crosslevel_common`)がTrueになることをtestで固定(Z配置のtmpdirで、`<slug>`=`melos`、level=`a2`/`b1b`)。
- **Family C `build_family_c_episode_sequence` の asset名対応表**(`audio_dir`=`<run>/<level>/narration`として呼ぶ。Zがshell/supportも同じnarrationディレクトリに置く):

| Family Cが読む名前(`audio_dir/<name>`) | 内容 | segment_id(role/gain key) |
|---|---|---|
| `welcome.wav` | Welcome(Charon、shell再利用) | welcome |
| `topic_intro_en.wav` | Topic intro | topic_intro_en(`resolve_narrative_role`は`topic_intro`のみTOPIC_INTRO。既存C/Xと同じ扱いとし、04Cはevidenceに実際のrole表を出す) |
| `japanese_title.wav` | 日本語タイトル | japanese_title |
| `preview_intro.wav` | Preview intro | preview_intro |
| `preview_asset_name`引数(Z=`preview.wav`) | Preview本体 | preview(Std=日本語R2、Adv=英語E1) |
| `key_phrases_intro.wav` | KP intro | key_phrases_intro |
| `full_story_intro.wav` | Full story intro | full_story_intro |
| `kp_blocks`引数のパス3点 | `kp{n}_number.wav`/`kp{n}_en.wav`/`kp{n}_ja.wav` | kp{n}_number / kp{n}_en / kp{n}_ja |
| `comment_wavs`引数のパス | `comment_{n}.wav`(**`_ja`は付けない**。Family C旧運用の`comment_{n}_ja.wav`と異なる) | comment_1/2/3 |
| `story_segments[].audio_path` | `full_story_part{p}_c{k}.wav` | full_story_part{p}_c{k}(er020新正規表現でFULL_STORY) |
| 参考(減速) | `full_story_part{p}_c{k}_original.wav` | **role対象外**(fullmatch不一致=testで固定) |

### M4 Z専用 `_generate_or_reuse` helper(04C)
- 事実: Xの`_generate_or_reuse`(`er019_family_x_audio_production_runner_01.py` L423)は`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`をハードコード。
- 設計: er063に`generate_or_reuse_z(...)`(Xの関数は呼ばない・不変)。再利用判定キー= **{canonical_text, `FAMILY_Z_ROLE_STYLE_VERSION`, voice名, style prefix sha256, tts_backend}** の全一致。1つでも異なれば再生成。キーはentryの`reuse_key`に保存。test: 各要素を変えると再生成、全一致で再利用、`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`のみ変えても影響を受けない。

### M5 Dialogue話者判定(04C)
- 事実: keyword窓判定(`er013_family_c_production_01.py` L66-95)は「言及」を拾い、`"I will return," Melos told the king.` が王に誤割当される。
- 設計: **全引用**(Melos・王・友を含む)について、(i)決定論判定(`classify_quote_voice_window`+`voice_keywords`)と、(ii)LLM話者判定(routing `FAMILY_Z_DIALOGUE_ATTRIBUTION`=gpt-6-luna、各レベル1 call、約¥0.3/レベル、全引用を1 callでJSON返却)を求め、**不一致が1件でもあればSTOP**(`dialogue_override.json`に両案・周辺文・引用IDを記録し人間判断。自動採用しない)。一致した場合のみ確定。
- Fableのスコープ決定: 登場人物の台詞(Melos・王・友を含む全引用)は**Dialogue clip**(既存Dialogue Voice割当)とし、narrator=PD8は**地の文のみ**(決定④に忠実)。Melos台詞用に別Voiceを割り当てる既存機構が無ければ**実装せずSTOP報告**(新Voice仕様は作らない。04Cは着手時に`STORY_REGISTRY["melos"]["voice_tts_names_plan"]`にMelos用キーが無いことを確認し、無ければ即STOP報告)。
- fixture(必須): 「`"I will return," Melos told the king.`」→Melos台詞(王ではない)、「`"I am here," he said to his friend.`」、言及だけの語(王の名前が地の文にあるが話者ではない)。誤割当をmockで再現し、LLM判定との不一致でSTOPすることをtest。

### M6 Local Rewrite差分記録(04C)
- 事実: er020正規表現追加によりZ narrator clipはconnected speech=Trueとなり、10分cool-down(`crosslevel_common` L182-183/L261-297、`er020` L63-87)とLocal Rewriteが発火しうる。
- 設計: 適用自体は既存承認cascade(標準2→fallback1→cool-down→Local Rewrite→human review)を無改変で利用してよい。**必須記録**: Local Rewrite採択時、provenance(clip entry)に `audio_text_deviation = {"canonical_text_before_local_rewrite": ..., "audio_text_after": ..., "diff_summary": ..., "clip_id": ...}` を記録。**書換後全文でValidator第1層を再実行**(FAIL→STOP)。KP source gateへ渡す`article_text`は**原稿(canonical)のまま**とし(音声の書換テキストは渡さない)、`audio_text_deviation`有無をgate入力のevidenceに明記。時間見込みにcool-down(**最大10分/clip**)を追加。
- test: LR採択clipで`audio_text_deviation`が記録される、書換後全文Validator第1層が呼ばれる、`article_text`が原稿のまま。

### M7 routing key(**完了**、先行実装)
追加済み(`er006_model_routing_contract_01.py`、既存key不変、リテラル固定):

| key | model | 用途 |
|---|---|---|
| `FAMILY_Z_WRITER_ADV_R0` / `_R1` / `_R2` | gpt-6.1-sol | Advanced Writer各段(v01のREVISEをR1/R2に分離) |
| `FAMILY_Z_STD_ADJUST` | gpt-6.1-sol | Std調整 |
| `FAMILY_Z_SEMANTIC_JUDGE` | gpt-6-luna | Validator第2層 |
| `FAMILY_Z_STORY_SPLIT` | gpt-6-luna | 分割境界選択(判定用keyと**共用しない**) |
| `FAMILY_Z_DIALOGUE_ATTRIBUTION` | gpt-6-luna | 全引用の話者判定(同上) |

`FAMILY_Z_TRIAL_*`は不変。`er006_model_routing_gpt6_wiring_test_01.py`のluna固定許可リストへSol 4キーを明示追加(判定は緩和せず、judge/split/attributionはluna固定判定のまま)。

### M8 閾値・calibration(04A)
- Std「同一本文」判定: **一致文率 >= 50% でFAIL**(案)。一致文率=Std文のうちAdvの正規化済み文と完全一致する文の割合(Fable判断で暫定採用、試聴時に妥当性確認)。
- **Validator第2層の実呼出calibrationは必須**(約¥2〜6): F1〜F6を実呼出。F4〜F6は正しいcategory(F4=role_relation/event、F5=ending、F6=causality)でFAIL、F1〜F3はPASS、**FAIL系(F4〜F6)はN=2で2回とも一致**すること。不合格 → **STOP**(Production配線しない)。保存先`er060_output/melos_production_e2e_01/validator_calibration_01.json`。

## 2. Opus推奨の反映

### 分割境界(04B: er062)
1. 各段落の語数から、(Part1, Part2, Part3)が各 **20〜45%** となる段落境界ペア(b1<b2)を**決定論で全列挙**。
2. 候補が空 → STOP(固定語数フォールバックしない。決定①)。
3. LLM(routing `FAMILY_Z_STORY_SPLIT`)は列挙された候補IDの**選択のみ**(候補外の値を返したら1回再提案→STOP)。理由は日本語で`segment_plan.json`に記録。
4. 分割後、planner(`plan_story_segments`)は**全文1回**を `force_split_before_paragraphs={b1,b2}` で呼び(L306-321)、後でclip idを `full_story_part{n}_c{k}` に改名。Part境界をclipが跨がない(force splitで担保、test)。
5. Std: 段落数・順序をAdvと**揃える契約**(Std Promptに明記、検証=段落数一致)。Std側の境界はAdvの段落index(b1,b2)をそのまま写像。

### er020正規表現(**完了**)
`_FAMILY_Z_STORY_CLIP_PATTERN = r"full_story_part[1-3]_c[0-9]+"`を`fullmatch`でFULL_STORYに(既存ID不変)。`\d`でなく`[0-9]`(Unicode数字を不許可)。negative test: `_original`/`_heading`/`part4`/`part0`/`foo_c1`/`_c`/`_cx`/`_c1x`/末尾改行/Unicode数字/`_c1_c2`など。`CONNECTED_SPEECH_SEGMENT_IDS`(未参照)に注記を追加(frozenset自体は不変)。

### Validator(04A)
- 第1層hard FAILは**高精度項目のみ**: 禁止結末family、名前ルール、主要アンカー全欠落。その他の曖昧項目は第2層。
- 順序は第2層schemaの`sequence` categoryで判定(v01の第1層order hardを降格)。
- `evidence_quote`は英語稿に**逐語存在する**ことを決定論検証(不在 → その判定項目を無効=NEEDS_REVIEW)。
- 第2層FAIL時は**再判定1回**し、2回一致でFAIL(不一致=NEEDS_REVIEW)。
- `validator_anchors`は**原作・Seedのみから作成**(新稿を見る前)、作成後sha256を凍結(`SEED_PROVENANCE.json`の`validator_anchors_status`を更新)。
- Seed: **Trial dirからProduction seed置き場へsha付き複製(完了)**。Trial成果物は編集しない。
- Std Commentの`content_facts`は、**該当Partに実在する事実**から作る(Part外の事実を入れない)。

### Writer(04B)
Std Promptに「Advと段落数・順序一致」追加。平均文長 <= Adv x 0.85 のsoft gate(WARN+試聴、FAILにしない)。

### Style(04C)
- fallback経路は`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`(既存承認挙動)。clipごとに`instruction_label`/`style_prefix`(のsha)をevidenceへ。
- Dialogue clipへPD8が混入しないことをtestで固定。
- 原典sha照合は実装時1回、runtimeはZ定数自身のshaをassert。Std narrator=`generate_a2_segment_with_slowdown`経路。

### TTS/Assembly(04C)
- Adv narratorの入口はX B1と同じ`news_tail_fix.generate_news_narration_wide_margin`(`er019 audio` L655-673)。
- **リスク明記**: Family C B1 assemblyは未実行(`B1_FULL_ASSEMBLY_NOT_EXERCISED` L767)=Z Advancedが初実行(新規OPEN-305)。
- X B1の`COMMENT_1/2_ROLE`/`PREVIEW_ROLE`はnews前提文言 → **出力にnews/In One Line/Point/構造ラベルが含まれないか決定論lint**。NG → retry(1回) → STOP。
- runtime evidence追加: out_path->segment_id導出結果、Local Rewrite差分(M6)、cool-down発生有無、fallback時のstyle。

### Dangling追加
`CONNECTED_SPEECH_SEGMENT_IDS`注記(完了)。`er026_family_z_fiction_production_runner_01_test.py` L93-99(`known_gap`前提のtest)は、er026統合時に`known_gap`文言と共に更新(現時点ではtestは通る)。

## 3. Fable判断の反映
- **OPEN-302語数(未承認Guardrail、試聴時にユーザー確認)**: Adv **400〜560語**、Std **300〜500語かつAdv比85〜110%**、各Part **20〜45%**。
- 全引用はDialogue clip、narrator=PD8は地の文のみ(M5参照)。
- Std Dialogue clipの6%減速は既存A2仕様(Full Story全体)どおり**一律適用**、試聴で確認。
- OPEN-303: 決定どおりR2。Coffee最終音声がP2でR2本文と異なる場合のみ報告。
- calibration不合格 → STOP。
- OPEN-297保留はZ範囲のみ解除(OPEN-276/279/281は持ち込まず、M1で自衛)。

## 4. データ契約(凍結、JSON schema相当)
全ファイルは`er026_output/family_z_production_e2e_01/<slug>/<run>/`配下。shaはsha256(UTF-8 bytes)小文字hex。

### 4-1 seed(`<slug>/seed/seed.json`、凍結済み・複製元と同一sha)
```json
{"type":"object","required":["original_summary","seed_elements"],
 "properties":{"original_summary":{"type":"string"},
  "seed_elements":{"type":"array","minItems":1,"items":{"type":"string"}}}}
```
(既存Trial seedは追加フィールド可。`SEED_PROVENANCE.json`: `files{name:{sha256}}`、`source_dir`、`validator_anchors_status`)。
`validator_anchors.json`(04A作成): `{"seed_sha256":str,"anchors":[{"id":str,"seed_element_index":int,"concept_family":[str],"order":int,"required":bool}],"forbidden_endings":[{"id":str,"patterns":[str]}],"created_before_candidate":true,"sha256_self":str}`。

### 4-2 segment_plan(`<run>/segment_plan_{a2|b1b}.json`)
```json
{"type":"object","required":["story_key","level","parts","boundaries","split_method","clips"],
 "properties":{
  "story_key":{"type":"string"},"level":{"enum":["a2","b1b"]},
  "split_method":{"const":"deterministic_candidates_llm_select"},
  "candidate_boundaries":{"type":"array","items":{"type":"array","items":{"type":"integer"},"minItems":2,"maxItems":2}},
  "boundaries":{"type":"array","items":{"type":"integer"},"minItems":2,"maxItems":2},
  "split_reason_ja":{"type":"string"},"split_model_id":{"type":"string"},
  "parts":{"type":"array","minItems":3,"maxItems":3,
   "items":{"type":"object","required":["part","paragraph_range","word_count","ratio"],
    "properties":{"part":{"enum":[1,2,3]},"paragraph_range":{"type":"array","items":{"type":"integer"}},
     "word_count":{"type":"integer"},"ratio":{"type":"number","minimum":0.20,"maximum":0.45}}}},
  "clips":{"type":"array","items":{"type":"object","required":["id","part","voice","paragraph_index","text_sha256","narration_path"],
   "properties":{"id":{"pattern":"^full_story_part[1-3]_c[0-9]+$"},"part":{"enum":[1,2,3]},
    "voice":{"type":"string"},"paragraph_index":{"type":"integer"},"text_sha256":{"type":"string"},
    "narration_path":{"pattern":"/(a2|b1b)/narration/full_story_part[1-3]_c[0-9]+\\.wav$"}}}},
  "std_adv_paragraph_count_match":{"type":"boolean"},
  "comment_after_segment_id":{"type":"object","required":["2","3"]}}}
```

### 4-3 provenance(`<run>/writer/provenance.json`)
```json
{"type":"object","required":["story_key","seed_sha256","chain","downstream_stale"],
 "properties":{"story_key":{"type":"string"},"seed_sha256":{"type":"string"},
  "chain":{"type":"array","items":{"type":"object",
   "required":["stage","routing_key","requested_model","actual_model_id","effort","response_id","attempts","cost_jpy","input_sha256","output_sha256","prompt_sha256"],
   "properties":{"stage":{"enum":["r0","r1","r2","std_adjust"]}}}},
  "adv_final_sha256":{"type":"string"},"std_sha256":{"type":"string"},
  "reference_only":{"type":"object"},"downstream_stale":{"type":"array","items":{"type":"string"}},
  "audio_text_deviations":{"type":"array","items":{"type":"object",
   "required":["clip_id","canonical_text_before_local_rewrite","audio_text_after"]}}}}
```
鎖: `seed_sha256 -> r0_prompt_sha -> r0_sha -> r1_sha -> r2_sha(=adv_final_sha) -> std_prompt_sha -> std_sha`。再開時、各ファイルshaを再計算し一致時のみ再利用、不一致は`FamilyZProvenanceMismatchStop`。

### 4-4 tts_generation_results entry(`<run>/<level>/audit/tts_generation_results.json`、既存形式の拡張。キー=clip名)
```json
{"type":"object","additionalProperties":{"type":"object",
 "required":["status","segment_id","narration_path","role","connected_speech_enabled","tts_backend","voice","style","reuse_key","attempts"],
 "properties":{
  "status":{"enum":["adopted","human_review_adopted","failed"]},
  "segment_id":{"type":"string"},"narration_path":{"type":"string"},
  "role":{"type":["string","null"]},"connected_speech_enabled":{"type":"boolean"},
  "tts_backend":{"type":"string"},"voice":{"type":"string"},
  "style":{"type":"object","required":["instruction_label","style_prefix_sha256"],
   "properties":{"fallback_used":{"type":"boolean"}}},
  "reuse_key":{"type":"object","required":["canonical_text_sha256","role_style_version","voice","style_prefix_sha256","tts_backend"]},
  "slowdown_applied":{"type":["boolean","null"]},
  "slowdown_ratio":{"type":["number","null"]},
  "attempts":{"type":"array"},
  "cooldown_occurred":{"type":"boolean"},
  "audio_text_deviation":{"type":["object","null"]}}}}
```

## 5. ファイル配置規約
上記M3のとおり。`<run>`直下: `writer/`、`segment_plan_{a2|b1b}.json`、`support/`(Comment/Preview本文)、`key_phrases/`、`{a2|b1b}/narration/`、`{a2|b1b}/audit/`、`{a2|b1b}/assembly/`。`<slug>/seed/`は複製済みSeed(sha凍結)。

## 6. 並列実装の分担(04A/04B/04C)
| 担当 | 対象 | 入力 | 出力 | 禁止領域 |
|---|---|---|---|---|
| 04A | `er061_family_z_semantic_validator_01.py`+`_test_01.py`+fixtures F1〜F8+`validator_anchors.json`+calibration(実呼出、約¥2〜6) | 4-1 seed、F1〜F8元(Trial dir read-only)、routing `FAMILY_Z_SEMANTIC_JUDGE` | `verdict`(第1層/第2層/統合)、`validator_calibration_01.json` | er062/er063/er026の編集、Writer Prompt、TTS。旧`check_character_name_rule`等は削除せず`superseded`注記 |
| 04B | `er062_family_z_writer_01.py`+test: Writer Adv R0->R1->R2、Std調整、分割候補列挙+LLM選択、Preview/Comment(Std JA/Adv EN)・KP選定、構造ラベルlint、provenance(4-3)、segment_plan(4-2) | seed、routing keys、`validate_semantic_preservation`(04A成果物のinterfaceのみ) | `writer/provenance.json`、`segment_plan_*.json`、support text | er061/er063の編集、TTS、assembly、Style定数 |
| 04C | `er063_family_z_audio_01.py`+test: Role Style表(PD8/R2/E1/E2_UPBEAT/K2/M2 sha照合、Dialogueへ非混入)、`generate_or_reuse_z`(M4)、TTS(narrator/dialogue/support/KP)、assemble(M3対応表)、`verify_std_english_slowdown`(M1)、`assert_tts_results_complete`(M2)、Dialogue override(M5)、LR差分(M6)、runtime evidence、試聴ページ | segment_plan、writer成果物、4-4 | `tts_generation_results.json`(4-4)、assembly、player | er061/er062の編集、共有module(er003/er011/er013/er019/er020/news_tail_fix/crosslevel_common)の編集 |
| 統合(後) | `er026`: stage順序・CLI・budget¥300・dry-run副作用ゼロ・`known_gap`更新 | 04A〜04Cのinterface | E2E runner | 04A〜Cの内部変更 |

共有: routing key・er020正規表現は本委任_03で完了済み(以降編集しない)。

## 7. テスト追加一覧(後続委任で実装)
M1(part3/`_cN`/Human Review採択clip)、M2(ファイル不在/entry欠落)、M3(`_has_valid_narration_layout`True)、M4(reuse key各要素)、M5(話者誤割当fixture「Melos told the king」「said to his friend」+LLM不一致STOP)、M6(`audio_text_deviation`・第1層再実行・`article_text`原稿維持)、M8(calibration F1〜F6、N=2、Std同一本文50%)、分割候補列挙(空->STOP、範囲外値->再提案->STOP)、Std段落整列、`evidence_quote`逐語、構造ラベルlint、新stage dry-run副作用ゼロ。**完了済み**: routing key存在・値、er020 positive/negative/既存ID不変、Seed sha、`CONNECTED_SPEECH_SEGMENT_IDS`不変(`er060_family_z_foundation_test_01.py`)。

## 8. 費用・時間見込みの差分(v01比)
- 費用: v01(約¥125〜175、上限¥300)に、話者判定LLM(2レベル各1 call、約¥0.6)と、Validator第2層再判定(FAIL時1回)・calibration N=2化(約¥4〜6)を加算。中央〜上側 **約¥130〜185**、上振れ約¥220〜255。上限¥300・¥200警告は不変。
- 時間: **TTSのcool-down(Connected Speech=True化により、clipが3回目attemptに入った場合最大10分/clip)** を追加。NGが数clipあれば+10〜30分。`--only-clips`再実行手順とSTOP条件(human review queue)で制御。

## 9. 追加OPEN・リスク
- **OPEN-304**(新規): X StdのStory part3(および`_cN`)が6%減速Gateで未検査(`A2_SLOWDOWN_TARGET_SEGMENTS`外)。Z範囲外、OPEN候補。
- **OPEN-305**(新規): Family C B1 assemblyが未実行(`B1_FULL_ASSEMBLY_NOT_EXERCISED`)で、Z Advancedが初実行。
- OPEN-302: Opus対案値で更新(未承認Guardrail)。
