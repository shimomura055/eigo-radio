# READING-VALIDATION 配線 設計調査(read-only)

管理ID: NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3a
作成: Sonnet実行層(read-only recon、実装・API呼び出しなし)

本文書は事実(コード引用・実データ引用)と推測・提案を明確に分離する。
「【事実】」「【推測/提案】」の接頭辞で区別する。

---

## 1. 現行の日本語Audio Validationの流れ

### 1.1 呼び出しチェーン(A2 comment系、B1 charon系共通)

【事実】TTS呼び出し前ゲート(ER-009 Gate、READING_DICTIONARY分類ではブロックしない)→
標準TTS生成→ASR→Validator→(必要ならCascade)→(必要ならfallback再生成)→
(それでも尽きればHuman Review Lock)という一直線の流れ。関数・行番号:

1. `er003_v1_n3_01_tts_generate.py`
   - `generate_charon_japanese_with_reading_safety()` L293-328(B1)
   - `generate_a2_japanese_with_reading_safety()` L475-515(A2)
   両者とも同じ順序で: `tts_safe_ja()`→`detect_gloss_placeholder_notation()`→
   `safety.classify_foreign_tokens_in_japanese_text()`(L311-312/L497-498)→
   `foreign_token_gate_requires_stop()`(L313/L499、HUMAN_REVIEW分類のみ
   ブロック)→`to_tts_safe_japanese_fraction_reading()`→実TTS呼び出し
   (`voice01.generate_charon_japanese()`L322、または
   `generate_a2_japanese_with_fallback()`L508)。
2. `generate_a2_japanese_with_fallback()`(同ファイルL377-472): 標準経路
   `c.generate_narration_snippet_verified_strict(text,"ja",...)`
   (L402-403、`standard_attempts`=既定2回)→不合格なら
   `_generate_a2_japanese_minimal_instruction()`によるminimal instruction
   fallback(L418-419、TTS再生成あり)。
3. `c.generate_narration_snippet_verified_strict()`
   (`er003_v1_repro01_main_generate.py` L194-371)。日本語分岐(L291-300)で
   `ja_secondary.evaluate_attempt_ja_with_cascade(text, asr_text, out_path,
   cascade_enabled=...)`を呼ぶ。
4. `evaluate_attempt_ja_with_cascade()`(`er007_ja_secondary_asr_01.py`
   L196-206)→`evaluate_attempt_ja_with_cascade_detail()`(L104-193)。
   Primary#1判定を`javal.classify_ja_asr_match()`(L112)で行い、
   `is_entity_like_mismatch_ja()`(L58-59、L123)がTrueならTTSは
   再生成せず同一音声に対しPrimary#2(OpenAI)→Secondary#1(Azure)→
   Secondary#2(Azure)の順に**ASRだけ**を追加実行し、いずれかが
   `should_pass`ならその時点で即PASSを返す(L156-158/167-169/182-184)。
5. 照合ロジック本体は`er007_ja_asr_validator_01.py`の
   `classify_ja_asr_match()`(L243-405)。文字単位正規化
   (`normalize_ja()`L81-101、英字は小文字化・句読点除去・NFKC)後、
   `difflib.SequenceMatcher`のopcode単位で`protected_check_ja()`
   (L179-240)が数字/否定/固有名詞らしさ(`entity_like`
   =カタカナ列またはLatin acronym、L104-114)/濁点差だけの読みゆれ
   (`phonetic_uncertain`)を判定する。

### 1.2 なぜ「メタン」がOKになったか(実データで再現・確認済み)

【事実】実artifact: `er012_output/e_family_two_level_wiring_01/meta/a2/
audit/tts_generation_results.json` L357-431(comment_3)。
- `canonical_text`(L412、`tts_input_text_after_reading_safety`と同一
  L413、`reading_safety_changed_text: false`L414): 「...サービスを、
  **Meta**が準備していたという話です。」(辞書登録どおり英大文字表記の
  ままTTS入力へ渡っている。**辞書の読み「メタ」へ置換されることは
  一度もない**)
- `asr_text`(L378、attempt 1のPrimary ASR、L384と同一): 「...サービスを
  **メタン**が準備していたという話です。」
- `audio_classification`: `"PHONETIC_MATCH"`(L390/L404)、
  `verified: true`(L393)、`call_count: 1`・`retry_count: 0`(L364-365、
  TTS再生成は一度も発生していない)。
- `foreign_token_findings`(L415-431)には`"Meta"`が
  `READING_DICTIONARY`・`reason: "読み方辞書に登録済みの表記です
  (読み: メタ)"`として記録されているが、この情報はASR照合には
  一切渡されていない(下記1.3参照)。

【事実・ローカル再現】上記のcanonical_text/asr_textをそのまま
`er007_ja_asr_validator_01.classify_ja_asr_match()`へ直接渡すと(API
呼び出し不要、`.venv/Scripts/python.exe`でのローカル実行のみ)、
唯一の差分opcodeは`replace 'meta' -> 'メタン'`であり、
`entity_like=True`(`meta`はLatin acronym扱い、`メタン`はカタカナ100%)・
`phonetic_uncertain=False`・`cascade_eligible=True`、他に差分が無いため
`classification="ASR_VALIDATION_UNCERTAIN"`・`should_pass=False`となる
(Primary#1単体では**不合格**と判定される。artifact上の最終結果
PHONETIC_MATCHとは異なる)。

【推測(コード構造からの推論、追加ASR呼び出しの再現はしていない)】
Primary#1がASR_VALIDATION_UNCERTAIN(entity_like)のため、
`evaluate_attempt_ja_with_cascade_detail()`が同一音声への追加ASR
(Primary#2→Secondary#1→Secondary#2)を実行する(L150-189)。
`call_count: 1`(TTS再生成なし)と最終`audio_classification:
"PHONETIC_MATCH"`(entity_likeな差が完全に0になった場合のみ到達しうる
分類、L403-405)から、Cascadeのいずれかの追加ASR呼び出しが「メタン」
ではなく読みが完全一致する表記(例:「メタ」)を書き起こし、その回の
`classify_ja_asr_match()`が`content_diffs`ゼロ→即PASSを返したと
推測される(コード上、Cascadeが直接PHONETIC_MATCHへ到達できる唯一の
経路)。**この場合、`attempts_log`に記録される`asr_text`はPrimary#1の
ものに固定され(`er003_v1_repro01_main_generate.py` L301-303が
`attempts_log`へ書く`asr_text`はループ先頭で取得した1回目のASR結果)、
Cascade各ステップの実際の書き起こしはこの成果物JSONには残らない
(監査上のトレーサビリティ欠落、本タスクの主題ではないが記録する)。

**結論**: 「メタン」がOKになった直接原因は、(a) 辞書の読み「メタ」が
TTS入力にもASR照合にも一切使われず、canonical側は生のLatin表記
「Meta」のまま比較されていること、(b) その結果生じる
「Latin acronym風 vs カタカナ」という差はENTITY_LIKEヒューリスティック
に該当し、ASR Cascade(最大4回の追加ASR、TTS再生成なし)の対象になる
こと、(c) 4回のうちどれか1回でも「読みが完全一致する表記」が
偶然出れば即PASSになる、という**辞書の期待値を一切参照しない偶然一致
救済**である。TTSが実際に"methane"寄りの発音をしていたかどうかは
本調査だけでは判定できない(音声を聴取していない)。

### 1.3 findingsの現在の使われ方(配線ギャップの正体)

【事実】`classify_foreign_tokens_in_japanese_text()`
(`er003_audio_tts_asr_safety.py` L708-785)が返す`findings`は、
`foreign_token_gate_requires_stop()`(L788-791、HUMAN_REVIEW分類が
1件でもあればTTS呼び出し自体をブロック)の判定にのみ使われ、
`generate_charon_japanese_with_reading_safety()`/
`generate_a2_japanese_with_reading_safety()`では`r["foreign_token_
findings"]`として結果JSONへ記録される(L326-327/L513-514)だけで、
TTS本文にも、ASR照合(`classify_ja_asr_match()`)にも一切渡されていない
(grep確認: `classify_ja_asr_match`・`protected_check_ja`・
`evaluate_attempt_ja_with_cascade`のいずれのシグネチャにも
`reading`/`expected_reading`系の引数は存在しない)。

---

## 2. expected readingのデータフロー案

【推測/提案】最小差分の推奨案(案i、下記2.1)。案ii(下記2.2、不採用
理由付き)も検討した。

### 2.1 推奨案: `protected_check_ja()`のopcodeループへ直接照合を追加

既存の`_reading_equal()`判定(L212-215)の直後に、辞書登録トークン
専用の追加チェックを挿入する:

1. `classify_foreign_tokens_in_japanese_text()`(L708-785)の
   READING_DICTIONARY分類finding生成部(L771-775)へ、既存の`reason`
   文字列(パースは脆弱で不採用)とは別に**構造化フィールド
   `"reading": dictionary[token.lower()]`**を追加する(1エントリにつき
   1行追加、既存の`reason`/`token`/`category`を読むだけの既存呼び出し元
   には無影響)。
2. `generate_charon_japanese_with_reading_safety()`/
   `generate_a2_japanese_with_reading_safety()`で、既に計算済みの
   `foreign_token_findings`から
   `expected_readings = {f["token"].lower(): f["reading"] for f in
   foreign_token_findings if f["category"] ==
   safety.FOREIGN_TOKEN_READING_DICTIONARY}`を作り、TTS呼び出し
   (`voice01.generate_charon_japanese()`/
   `generate_a2_japanese_with_fallback()`)へ新規オプション引数として
   渡す(既定`None`、渡さない既存呼び出し元は無変更)。
3. 下記の各関数へ新規オプション引数`expected_readings: dict | None =
   None`を追加し、そのまま下流へ転送するだけの配線を行う:
   `generate_a2_japanese_with_fallback()`
   (`er003_v1_n3_01_tts_generate.py` L377-472)、
   `generate_charon_japanese()`(`er003_v1_sing01_voice01_generate.py`、
   B1経路)、`generate_narration_snippet_verified_strict()`
   (`er003_v1_repro01_main_generate.py` L194-371、ja分岐L291-300のみ)、
   `evaluate_attempt_ja_with_cascade()`/
   `evaluate_attempt_ja_with_cascade_detail()`
   (`er007_ja_secondary_asr_01.py` L104-206、Primary#1・Primary#2・
   Secondary#1・Secondary#2の**全呼び出し**へ転送、L112/L152/L163/L178)、
   `classify_ja_asr_match()`(`er007_ja_asr_validator_01.py`
   L243-405)→`protected_check_ja()`(L179-240)。
4. `protected_check_ja()`内、既存の`reading_equal = _reading_equal(
   c_padded, a_padded)`がFalse(L212-215で継続しない場合)のとき:
   - `c_span`(または`_LATIN_TOKEN_RE`で`c_span`内を再検索した
     Latin token)が`expected_readings`のキーに一致し、かつ
     `c_span`から該当Latin token文字列を除いた残りが空(=このopcode
     差分が辞書登録トークン単体である)場合のみ、新チェックへ入る。
   - 登録読み(カタカナ)を`a_span`(ASR側の表記)と、既存の
     `_reading_equal_allowing_voicing()`と同じ濁点許容ロジックで比較
     する(kakasi hepburn/hira変換を再利用、新規ライブラリ不要)。
   - 一致 → 「読みが確定どおり発話された」とみなし、既存の
     `continue`(許容差、L215相当)と同じ扱いにする(content_diffsへ
     計上しない、この差分は無条件PASS側)。
   - 不一致 → `entity_like=False`・`phonetic_uncertain=False`を
     強制し(=`cascade_eligible=False`)、`reading_dictionary_
     mismatch=True`という新フラグを持つdiffとして`content_diffs`へ
     追加する。これにより`classify_ja_asr_match()`の
     `non_cascade_diffs`(L298)が非空になり、既存の
     `TRUE_CONTENT_MISMATCH`系分岐(whole_text読み一致チェック→
     variant layer→A2 Reading Resolver(LLM)→最終TRUE_CONTENT_MISMATCH、
     L307-390)へ**そのまま**流れる(新しい分岐を作らない)。
   - `expected_readings`が`None`(未指定)の場合は一切分岐しない
     (完全後方互換)。

この案が最小差分である理由:
- 新しい判定ロジックは「辞書登録トークンのopcode差分1箇所」に限定され、
  既存の`entity_like`/`phonetic_uncertain`ヒューリスティック(辞書に
  登録の無い固有名詞・略語)の挙動は一切変更しない(DECIDED行
  「固有名詞のASR表記ゆれのみを理由とした繰り返しTTS再生成は行わない」
  ※CURRENT_SPEC.md L1288、との整合は保たれる。辞書未登録トークンは
  従来どおり許容側)。
- FAIL後の経路は既存の`TRUE_CONTENT_MISMATCH`→retry→Cascade→
  Human Review Lockをそのまま再利用し、新しいGate・新しい上限・新しい
  ログ経路を作らない。
- 引数はすべて`= None`既定のオプション追加であり、`expected_readings`
  を渡さない全既存呼び出し元(B1本文・非日本語経路・既存test)は
  ソース差分ゼロで従来どおり動く。

### 2.2 不採用案(案ii): 最終ASRテキストへの後付けパターンマッチ

`generate_a2_japanese_with_reading_safety()`側で、最終結果の
`r["asr_text"]`全体に対して「登録トークンの読み+余分な文字」を正規表現
等で検出する案。**不採用理由**: (a)`protected_check_ja()`が既に持つ
opcode位置情報(どの文字範囲が辞書登録トークンに対応するか)を持たず、
`SequenceMatcher`を重複して実行する必要がある(二重実装・将来の
挙動乖離リスク)。(b) Cascade各ステップの中間ASR結果(Primary#2/
Secondary#1/Secondary#2)にはアクセスできない(現状記録されていない、
1.2節参照)ため、後付けチェックは最終結果にしか適用できず、「4回中
どれか1回運よく一致すればPASS」という今回の根本原因を解消できない。

---

## 3. retry/fallback/regeneration経路との整合

【事実】案iはTRUE_CONTENT_MISMATCH化のみを行い、以降は完全に既存経路:

- `c.generate_narration_snippet_verified_strict()`のja分岐で
  `stop_retrying`(L365、`ja_secondary.evaluate_attempt_ja_with_cascade`
  が返す`stop_retrying`)がTrueなら即`status="ASR_VALIDATION_UNCERTAIN"`
  で打ち切り(L365-369)、Falseならループ先頭へ戻りTTSを再生成する
  (`max_attempts`回、A2は`standard_attempts`=2回に固定、
  `er003_v1_n3_01_tts_generate.py` L401参照の
  `review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`=3が絶対上限、
  `er011_human_review_lock_01.py` L80/L102)。
- 標準経路が尽きた後は`generate_a2_japanese_with_fallback()`の
  minimal instruction fallback(L418-472)が残り予算分だけ新規TTSを
  生成し、同じ`ja_secondary.evaluate_attempt_ja_with_cascade()`
  (辞書チェック込み)で再照合する(L427-428)。
- 最終的にHuman Review Lock(`er011_human_review_lock_01.py`)が
  累積TTS試行(既定上限15)・累積ASR呼び出し(既定上限60)を超えると
  強制的に`HUMAN_REVIEW_REQUIRED`へ固定し(CURRENT_SPEC.md L1248)、
  以降`approve_regenerate()`(L357-384)によるユーザー明示承認が無い
  限り0 API callで即ブロックする(`_blocked_result()`L387-410)。
  **無限retryにはならない**(既存の3層上限: standard 2回→fallback
  最大1回[合計3回]→Human Review Lockの累積上限)。
- TTSの発話揺れで解消するか: 「Meta」がTTSモデル側の発音ゆれで
  「メタン」寄りに聞こえる場合、fallback再生成(minimal instruction、
  声・モデルは同一)で改善する可能性はあるが保証はない。改善しなければ
  既存のHuman Review Lockで終端し、辞書エントリ自体の見直し
  (別の読み方表記への変更、または「メタ」ではなく直接カタカナ
  「メタ」表記へcanonical text自体を書き換える等)がユーザー判断で
  必要になる(実装Phase外の論点として明記のみ)。

---

## 4. 影響範囲

### 4.1 変更が必要なファイル・関数(見積り行数、すべて新規オプション
引数の追加+転送、または既存関数内への追加分岐)

| ファイル | 関数 | 変更内容 | 見積り行数 |
|---|---|---|---|
| `er003_audio_tts_asr_safety.py` | `classify_foreign_tokens_in_japanese_text()` | READING_DICTIONARY findingへ`"reading"`フィールド追加 | +2〜3 |
| `er003_v1_n3_01_tts_generate.py` | `generate_charon_japanese_with_reading_safety()` | `expected_readings`算出+転送 | +5〜8 |
| 同上 | `generate_a2_japanese_with_reading_safety()` | 同上 | +5〜8 |
| 同上 | `generate_a2_japanese_with_fallback()` | 引数追加+`c.generate_narration_snippet_verified_strict()`・fallbackループ内`evaluate_attempt_ja_with_cascade()`呼び出しへ転送 | +6〜10 |
| `er003_v1_sing01_voice01_generate.py` | `generate_charon_japanese()`(B1) | 引数追加+転送 | +5〜8 |
| `er003_v1_repro01_main_generate.py` | `generate_narration_snippet_verified_strict()` | 引数追加(ja分岐のみ使用)+転送 | +3〜5 |
| `er007_ja_secondary_asr_01.py` | `evaluate_attempt_ja_with_cascade()`/`_detail()` | 引数追加+Primary#1/#2・Secondary#1/#2の4呼び出しへ転送 | +8〜12 |
| `er007_ja_asr_validator_01.py` | `classify_ja_asr_match()` | 引数追加+`protected_check_ja()`へ転送 | +3〜5 |
| 同上 | `protected_check_ja()` | 新チェック本体(辞書トークン判定+読み比較+diff生成分岐) | +20〜30 |

**合計見積り: 約60〜100行(9ファイル)**、うち実質ロジックは
`protected_check_ja()`内の1ブロックのみで、他は全て引数の素通し配線
(この形の「オプション引数を末端まで素通しする」パターンは
`asr_prompt`/`enable_non_latin_cascade`/`enable_connected_speech_
equivalence_layer`等、`generate_narration_snippet_verified_strict()`
に既存の前例が複数ある、L217-231参照)。

### 4.2 英語TTS経路への影響

【事実】`expected_readings`は`classify_ja_asr_match()`
(日本語専用Validator)にのみ渡す設計であり、英語経路
(`secondary_asr.evaluate_attempt_with_cascade()`
=`er006_secondary_asr_01.py`、B1本文等)のシグネチャ・呼び出しには
一切触れない。`generate_narration_snippet_verified_strict()`の
`language=="en"`分岐(L272-290)は無変更。**影響なし**。

### 4.3 既存21+1語の実測(regressionリスク評価)

【事実】"AI"の実例(`er011_output/family_a_trend_ai_manufacturing_
prod_run_01/a2/audit/tts_generation_results.json`):
ASRは"AI"をLatin文字のまま書き起こす例が複数確認できた
(例: L24 `"asr_text": "Today's topic is The AI Factory Story..."`
は英語文、L81 `"asr_text": "AI工場の物語には..."`
=canonical文L115と`AI`部分が文字として直接一致、`audio_classification:
"NORMALIZED_MATCH"`L107)。この場合`classify_ja_asr_match()`の
**トップレベル**(`c_norm == a_norm`、L257-260)で即PASSし、
`protected_check_ja()`のopcodeループにすら到達しないため、案iの
新チェックは実行されない(**regressionなし**)。

"Meta"の実例は1.2節のとおりASR側がカタカナへ変換したため
opcode差分が発生するケース。案iを適用した場合、このcomment_3は
**再TTS/再ASRを行わない限り現在のartifact(status=OK)には影響しない**
(既存artifactの書き換えは行わない設計、次回このsegmentが再生成
[regenerate]される時にのみ新チェックが適用される)。もし将来の
再生成でASRが再び「メタン」相当を返せば、案iはこれをFAIL
(non_cascade_diff)として扱い、既存retry→fallback→Human Review Lock
へ回す(3節参照)。これは**仕様どおりの動作**であり、regressionでは
なく意図した挙動変化(ユーザー承認済みの背景どおり)。

"cm"/"kg"/"km"については、`er011_output`/`er012_output`配下の
sample済みaudit fileでは該当トークンの使用例が見つからなかった
(grep 0件、実測なし)。辞書内の他の略語についても、案iはトークンが
実際に「entity_likeなopcode差分」として現れた場合のみ発火するため
(4.3節の"AI"のように文字通りASRされるケースは対象外)、regression
リスクは辞書登録済みトークンかつASR側がカタカナ変換した場合に限定
される。**この母集団のサイズは本調査だけでは不明**であり、実装Phase
で辞書22語それぞれについて過去artifactの`foreign_token_findings`
category=READING_DICTIONARYな箇所を全数grepし、
`content_diffs`が発生していた件数(=opcodeループに到達していた件数)
を洗い出すことを推奨する(API呼び出し不要、¥0で実施可能)。

---

## 5. test計画(追加案)

### 5.1 Unit test(`er007_ja_asr_validator_01_test.py`への追加、
fixture形式は既存の`run_group()`パターンを踏襲)

- 「メタ」(canonical) vs 「メタ」(ASR、辞書読み完全一致) →
  PASS(既存のreading_equal相当、regressionでないことの確認)
- 「Meta」(canonical) vs 「メタン」(ASR、実際にNo.問題を再現) →
  `expected_readings={"meta":"メタ"}`ありの場合はFAIL
  (`TRUE_CONTENT_MISMATCH`または新フラグ付きdiff)、
  `expected_readings`なしの場合は従来どおり
  `ASR_VALIDATION_UNCERTAIN`(後方互換の確認)
- 「Meta」(canonical) vs 「メター」(ASR、長音差のみ)→濁点許容と同様の
  緩和が必要か、既存`_reading_equal_allowing_voicing`の長音扱いを
  確認した上でfixtureを追加(このタスクでは未検証、実装Phaseで確定)
- 辞書に無いLatin token(例: 未登録の"XYZ")での`entity_like`挙動が
  `expected_readings`指定時でも従来どおり(regressionなし)であること

### 5.2 Unit test(`er003_audio_tts_asr_safety.py`関連、
`classify_foreign_tokens_in_japanese_text`のtest = 実ファイルは
`er009_ja_foreign_token_gate_01_test_01.py`、既存`test_4`
[L56、reading_dictionary_term_classified]の拡張)

- READING_DICTIONARY findingに`"reading"`フィールドが追加され、値が
  `DEFAULT_JA_READING_DICTIONARY`の登録値と一致すること

### 5.3 Integration test(新規、findings→expected_readings→
classify_ja_asr_matchの配線確認)

- `generate_a2_japanese_with_reading_safety()`(またはより下位の
  `generate_a2_japanese_with_fallback()`)をTTS/ASRをモック化した状態で
  呼び、`expected_readings`が最終的に`classify_ja_asr_match()`へ
  正しい値で渡っていることをモックの呼び出し引数で確認する
  (`er007_ja_tts_retry_path_fix_test_01.py`等、既存のmock test
  パターンを踏襲)

---

## 6. runtime evidence計画(実行はしない、可能性のみ確認)

【推測/提案・未実行】最小evidence案: 「メタ」を含む短い日本語1
segment(例:「これはMetaのテストです」)を、
`generate_a2_japanese_with_reading_safety()`経由で専用out-dir
(例: `er0XX_output/reading_validation_wiring_recon_evidence_01/`)へ
1回TTS+ASRし、`expected_readings`を渡した場合と渡さない場合の
classification差を比較する。想定コスト: TTS1回(Gemini Batch)+
Primary ASR1回(OpenAI)、Cascade非発火なら追加コストなし、発火時は
Azure Secondary最大2回追加(既存の`CASCADE_CONFIG_JA`上限どおり)。
概算¥1〜2(既存の同種segment実測値から推定、本調査では未確定)。
`TTS_EXECUTION_MODE=STANDARD`で動作するかは、既存の
`batch_wiring.resolve_tts_execution_mode()`(`er003_v1_n3_01_tts_
generate.py`等で参照)が環境変数を見て自動判定するため、追加設定は
不要と推測されるが未確認。**このタスクでは実行しない**(ユーザー指示
どおりread-only)。

---

## 7. Dangling Reference Check

【事実】本設計が依存する3つの既存仕様は、いずれもCURRENT_SPEC.mdで
`DECIDED`(`PRODUCTION_WIRED`)/`WIRED(ON)`:

- ER-009 Gate(`classify_foreign_tokens_in_japanese_text`):
  CURRENT_SPEC.md L1244「`DECIDED`(`PRODUCTION_WIRED`)」
  (ER-009-JA-FOREIGN-TOKEN-GATE-01)。
- 日本語ASR Validator+Cascade(`classify_ja_asr_match`/
  `evaluate_attempt_ja_with_cascade`): CURRENT_SPEC.md L1283
  「Validator(日本語)」`DECIDED`(`PRODUCTION_WIRED`)、L1287
  「ASR-first Retry Policy」`DECIDED` / `WIRED(ON)`(Production call
  site 3箇所を明記: `er003_v1_repro01_main_generate.py`のJapanese分岐、
  `er003_v1_sing01_voice01_generate.py`、`er003_v1_n3_01_tts_
  generate.py`)。
- Human Review Lock(`er011_human_review_lock_01.py`): CURRENT_SPEC.md
  L1248「`DECIDED`(`PRODUCTION_WIRED`)」(ER-011-HUMAN-REVIEW-COST-
  GUARD-01)。

いずれもDEV/Trial専用実装ではなく、本設計はこの3つのProduction正式
経路の内部(引数追加+1関数内の追加分岐)のみを対象とする。新しいGate・
新しい保存先・新しいLock機構は作らない。

なお、CURRENT_SPEC.md L1288「TTS Retry条件(絞り込み)」
(`DECIDED`)は「固有名詞のASR表記ゆれのみを理由とした繰り返しTTS
再生成は行わない」と定めている。本設計は辞書**未登録**の固有名詞
表記ゆれの扱いには一切触れないため矛盾しない。辞書**登録済み**トークン
のみ、期待読みとの不一致を「表記ゆれの許容範囲」から除外する
(辞書へ読みを登録した以上、その読みが守られたかを確認する、という
今回のユーザー決定に沿った限定的な例外)。

---

## 8. STOP条件該当判断

【判断】**該当しない。最小差分で実装可**。根拠:

- 新しい仕様領域(新Gate・新Lock・新再生成上限・新ログ経路)を作らない。
  既存の3層(TTS Retry→Fallback→Human Review Lock)をそのまま使う。
- 新規LLM呼び出し・新規API呼び出しを追加しない(`protected_check_ja()`
  内の追加チェックはpykakasiのみ、既存依存)。
- 影響範囲は日本語Validator1系統(9ファイル、合計60〜100行見積り)に
  限定され、英語経路・非TTS経路には触れない。
- 依存する3仕様はいずれもCURRENT_SPEC.mdでPRODUCTION_WIRED済み
  (7節)。
- 唯一の副作用は、辞書登録トークンで過去に「Cascade運任せ」でPASSして
  いたケース(1.2節のMeta comment_3相当)が、**次回そのsegmentが
  再生成された場合のみ**FAIL側へ倒れうることだが、これはユーザーが
  明示的に意図した挙動変化であり(背景節「メタ」相当ならPASS、
  「メタン」等ならFAILと明記)、既存artifactを遡及的に書き換えるもの
  ではない。

実装Phaseへ進む場合の残作業(本調査の範囲外、実装Phase自体の見積り):
2.1節の9ファイル変更+5節のtest追加+(可能なら)6節のruntime evidence
1件。

---

## 9. まとめ(報告用の骨子)

- 「メタン」がOKになった直接原因: 辞書の読み「メタ」がTTS入力にも
  ASR照合にも使われておらず(1.3節)、Latin表記"Meta" vs カタカナ
  "メタン"の差が`entity_like`ヒューリスティックに該当してASR Cascade
  (最大4回の追加ASR、TTS再生成なし)へ回り、4回のうちどれか1回が
  偶然「読み完全一致」を返せば無条件PASSになる設計だったため
  (1.2節、実データ+ローカル再現で確認)。
- 推奨案: `protected_check_ja()`のopcodeループへ、辞書登録トークン限定
  の直接読み照合を追加し、`expected_readings`という新規オプション引数
  (既定None)を9ファイルへ素通し配線する(2.1節、既存前例パターンを
  踏襲、約60〜100行)。
- regressionリスク: "AI"等、ASRがLatin表記のまま書き起こすケースは
  opcodeループへ到達しないため影響なし(4.3節)。"Meta"のような
  カタカナ変換ケースのみ、次回再生成時に挙動が変わる(意図した変更)。
  辞書全22語のregression母集団サイズは未確定(実装Phaseでのgrep調査を
  推奨)。
- STOP条件: 非該当。最小差分で実装可(8節)。
