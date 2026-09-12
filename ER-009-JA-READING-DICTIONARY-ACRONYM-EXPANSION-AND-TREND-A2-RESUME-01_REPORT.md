# ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01_REPORT

管理ID: ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01
作業者: sonnet-worker(Git操作禁止・SSOT編集禁止で委任)
日付: 2026-09-12
ユーザー承認: 「NFTを含む以下15語を登録して構いません。AI / IT / EV / IoT / DX / GPS /
SNS / PC / GDP / EU / NASA / AR / VR / ESG / NFT。Gateロジック自体は変更せず、
辞書拡張のみで進めてください。」→`APPROVED_FOR_PRODUCTION`(辞書エントリ追加のみ)。

## 1. 何が問題だったか(日本語での簡単な説明)

Trend記事「AI Manufacturing」のA2(中級者向け)音声のうち、日本語の説明部分
(タイトル/プレビュー/コメント4本/Key Phrase5番の意味説明、計7か所)に
「AI」という英字の略語がそのまま含まれていた。安全のための仕組み(Gate、
「意味の分からない英字が混ざっていたら人が確認するまで音声化を止める」
というルール)が、辞書に「AI」の読み方が登録されていなかったため作動し、
この7か所だけ音声化がSTOP(停止)していた。

## 2. 何を変更したか

- `er003_audio_tts_asr_safety.py`の読み方辞書(`DEFAULT_JA_READING_DICTIONARY`)へ、
  ユーザー承認済みの15語(AI/IT/EV/IoT/DX/GPS/SNS/PC/GDP/EU/NASA/AR/VR/ESG/NFT)の
  読み仮名を追加した(既存7語は変更なし)。Gateの判定ロジック自体は一切変更していない
  (辞書に載っている語は「読み方辞書登録済み」として通す、載っていない語は
  引き続き人による確認待ちにする、という既存の仕組みのまま)。
  ※この辞書追加自体は前回セッション(前回タスクが上限到達で中断した時点)で
  既に実装済みだった。今回はその内容を検証し、後続作業(3〜6)を実施した。
- 上記7か所の音声を、辞書追加後に実際に音声合成(TTS)+音声認識による検証(ASR)を
  行い、全て成功させた。
- 音声7本を1つのエピソード音声にまとめる処理(Assembly)と、音声の完全性を
  確認する仕組み(Audio Validation Gate)を実行し、両方合格した。
- 完成したA2音声を、ブラウザで聞きながら台本を確認できる標準フォーマットの
  ページ(player)として新規作成した。

## 3. 何が改善されるか

- 停止していたTrend記事のA2音声7segmentが完成し、A2エピソード全体
  (14 segment+Key Phrase5件、合計361.075秒)が完成した。
- 今後同じ記事群で「AI」「IT」「EV」など今回登録した15の略語が出てきても、
  同じ理由でSTOPすることはなくなる(ただし辞書に無い未知の略語は、これまで
  通り安全のため人の確認待ちになる。安全装置は弱めていない)。

## 4. リスクや注意点

- 辞書に登録した読み方(例: AI→エーアイ、NASA→ナサ)は機械的な音声変換用の
  読みであり、内容の正しさ(事実関係)には影響しない。
- Gateのロジック自体は変更していないため、今回登録していない略語は
  引き続き人の確認が必要になる(想定通りの動作)。
- 本タスクはGit操作禁止(commit/push未実施)。反映はFableの統合タスクで行う。

---

## 5. 再開手順で確認した前回到達点

`git diff --stat er003_audio_tts_asr_safety.py`で、辞書15語追加が既に完了して
いたことを確認した(前回セッションが上限到達で中断した時点で、この差分は
既に完了していた)。既存7語(cm/kg/km/kcal/ceo/wi-fi/cafe)は不変。

`er009_ja_foreign_token_gate_01_test_01.py`にも、前回セッションで新規テスト
クラス`AcronymDictionaryExpansionTests`(4テスト)が既に追加済みであることを
確認した。今回はこのテストを実行してPASSを確認した(下記6節)。Gate再判定
スクリプト・A2 TTS再開・Assembly・player作成は今回新規に実施した(前回は
これらに未着手のまま中断していた)。

## 6. テスト結果(コード変更は今回無し、実行・検証のみ)

`.venv/Scripts/python.exe -m unittest er009_ja_foreign_token_gate_01_test_01 -v`

- 全17テストPASS(既存13テスト+新規4テスト)。
- 新規4テストの内容:
  - `test_11_all_15_added_acronyms_classified_as_reading_dictionary`: 15語全てが
    `READING_DICTIONARY`分類になり、Gateがブロックしないことを確認。
  - `test_12_mixed_case_and_slash_joined_tokens_still_match_dictionary`:
    「AR/VR」のようなスラッシュ連結表記が、トークン分割の正規表現
    (`_LATIN_TOKEN_RE = r"[A-Za-z][A-Za-z0-9\-\.']*"`、`/`を含まない)により
    自動的に「AR」「VR」の2トークンへ分かれ、それぞれ独立に辞書照合される
    ことを確認(`"AR/VR技術について話します。"` → `[("AR", READING_DICT),
    ("VR", READING_DICT)]`)。「IoT」のような大小混在表記も、辞書照合が
    `token.lower() in dictionary`(既存ロジック、無変更)であるため正しく
    「iot」キーへ一致することをコードで確認済み。
  - `test_13_unregistered_acronym_still_human_review_gate_not_weakened`:
    未登録語「XYZ」は引き続き`HUMAN_REVIEW`となり、Gateがブロックすることを
    確認(安全装置が弱まっていないことの回帰確認)。
  - `test_14_original_7_entries_unchanged`: 既存7語の読みが変更されていないこと
    を確認。

ロジック変更は不要だった(照合されないケースは発生しなかった)。

## 7. ¥0再判定(Trend A2停止7segment、ローカル関数実行のみ)

対象: `er011_output/family_a_trend_ai_manufacturing_prod_run_01/a2/audit/
tts_generation_results.json`内の`segments.japanese_title`/`preview`/
`comment_1`〜`4`(status=STOPPED)、`key_phrases["5"].japanese_meaning`
(status=STOPPED)。各canonical_textに対し`classify_foreign_tokens_in_
japanese_text()`をローカル(API呼び出し無し、¥0)で再実行した。

| segment | 旧判定(登録前) | 新判定(15語追加後) | Gate再要求 |
|---|---|---|---|
| japanese_title | AI→HUMAN_REVIEW | AI→READING_DICTIONARY(エーアイ) | 不要 |
| preview | AI→HUMAN_REVIEW ×2 | AI→READING_DICTIONARY ×2 | 不要 |
| comment_1 | AI→HUMAN_REVIEW | AI→READING_DICTIONARY | 不要 |
| comment_2 | AI→HUMAN_REVIEW | AI→READING_DICTIONARY | 不要 |
| comment_3 | AI→HUMAN_REVIEW | AI→READING_DICTIONARY | 不要 |
| comment_4 | AI→HUMAN_REVIEW | AI→READING_DICTIONARY | 不要 |
| key_phrases.5.japanese_meaning(「AIで動く工場」) | AI→HUMAN_REVIEW | AI→READING_DICTIONARY | 不要 |

7件全てが`foreign_token_gate_requires_stop() == False`(HUMAN_REVIEW以外)に
変化したことを確認した。残存HUMAN_REVIEWは0件のため、次段階(TTS再開)へ
進んだ。

## 8. A2 TTS再開(既存Production関数、無改変)

### 8-1. 方式判断(重要な設計上の発見)

指示された既存経路`er011_family_a_trend_synthesis_ai_manufacturing_production_
run_01_audio.py`をそのまま(`main()`ごと)実行すると、内部で呼ばれる
`run_scaffold()`(A2 Comment/Preview生成、LLM再呼び出し)・`run_key_phrases()`
(Key Phrase再生成)まで再実行され、既に合格済みの記事文言が意図せず変わって
しまう可能性、および`tts_gen.generate_a2_segments()`自体が「未完了segmentのみ
再開する」設計ではなく、呼び出す度に全14segment+Key Phrase5件すべてに対して
TTS/ASRを再実行する設計(状態を見て未処理分だけ動かすresume機構が無い)である
ことをコードで確認した。そのまま`main()`を呼ぶと、既に`OK`だった残り7segment
分も再課金・再TTSされ、「7segmentのみ」「上限¥100」という指示範囲を超える
おそれがあった。

このため、`generate_a2_segments()`内部で各segmentに対して呼ばれているのと
**全く同じ既存Production関数**(`generate_a2_japanese_with_reading_safety()`/
`resolve_key_phrase_ja_gloss_tts()`/`expected_substring_ja()`、いずれも
無改変)を、STOPPEDだった7segmentのみに対して直接呼び出す方式を採用した
(Gate自体は無変更、呼び出しコードもgenerate_a2_segments内の該当箇所を
そのまま踏襲)。Production関数のコード自体は一切変更していない。

### 8-2. 実行結果

7segment全てが1回目の試行(retry無し、Human Review Lock新規発動無し)で
`status=OK`となった。

| segment | 状態 | TTS attempt | ASR attempt | asr_verified |
|---|---|---|---|---|
| japanese_title | OK | 1 | 1 | true |
| preview | OK | 1 | 1 | true |
| comment_1 | OK | 1 | 1 | true |
| comment_2 | OK | 1 | 1 | true |
| comment_3 | OK | 1 | 1 | true |
| comment_4 | OK | 1 | 1 | true |
| key_phrases.5.japanese_meaning | OK | 1 | 1 | true |

`git show HEAD:...tts_generation_results.json`との差分確認により、上記7件
以外の既存14件中7件(`topic_intro`/`point_one_heading`/`point_two_heading`/
`full_story_part1`/`full_story_part2`/`point_one`/`point_two`)およびKey
Phrase 1〜4は完全にbyte一致(無変更)であることを確認した(この方式選択が
正しく機能した証跡)。既存Human Review Lock機構(`review_lock_state.json`)にも
7件分`state=RESOLVED, final_status=OK`が正しく記録された。

## 9. Assembly(既存Production関数、無改変)

`er003_v1_n3_01_assemble.stage_assemble_a2()`・`verify_episode_audio_
validation_gate()`(いずれも無改変)を呼び出した。

- Assembly: `status=OK`、`duration_seconds=361.075`、`peak=0.95202`、
  `clipping_detected=False`、`headroom_safety_valve.applied=False`
  (閾値0.98未満のため非発動)。
- 出力: `er011_output/family_a_trend_ai_manufacturing_prod_run_01/a2/assembled/
  English_Your_Way_A2_FAMILY_A_TREND_AI_MANUFACTURING_PROD_RUN_01.wav`
- Audio Validation Gate(既定OFF経路): PASS。
- Audio Validation Gate(opt-in ON経路、OPEN-129 required_structure): PASS。

## 10. 費用(5区分、JPY、実測)

| 区分 | 金額 | 内訳 |
|---|---|---|
| ①今回実測(Standard同期、7segment TTS+ASRのみ) | ¥9.70 | gemini(TTS)¥9.25(`gemini-3.1-flash-tts-preview`、7回)+openai_asr¥0.45(`gpt-4o-mini-transcribe`、7回)。Assembly/Gate判定はローカル処理のみで課金無し。Gate再判定(7節)も¥0(ローカルpure-Python) |
| ②Trial特有の追加コスト | ¥0 | 本タスクはTrialではなく既存Production記事の完成作業のため該当なし |
| ③異常retry・Human Review由来の上振れ | ¥0 | 7segment全てTTS/ASR各1回で成功(retry無し)。今回はHuman Review Lockの新規発動も無し |
| ④Standard同期でのコスト(1記事あたり、累積) | B1B(完成、前回実測)=¥70.80。A2(今回完成)=¥51.18(前回部分実測)+¥9.70(今回)=¥60.88。**記事全体(B1B+A2)合計=¥121.98(前回)+¥9.70(今回)=¥131.68** | 前回`FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01_REPORT.md`§6実測値に今回分を加算 |
| ⑤Batch量産換算時のコスト | 今回分TTS(¥9.25)のみ半額(`pricing_snapshot.json`Gemini Batch tier=Standardの50%)→約¥4.62。ASR(¥0.45)にBatch tierは存在しないため不変。今回分Batch換算合計≈¥5.07。記事全体Batch換算(参考)≈前回Batch換算(tts_b1b¥17.50+tts_a2部分¥11.32)+今回¥5.07 | 同上`pricing_snapshot.json`参照 |

為替レート: プロジェクト既存値`USD_JPY = 160.0`
(`er006_pool_pilot_01_cost_time_compute.py`)を使用。単価は
`er005_output/cost_baseline_01/pricing_snapshot.json`(OFFICIAL_SOURCE)。

## 11. Gate 3充足状況(SSOT反映・Git commit/pushは統合タスク側で実施)

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Production正式path経由(Trial非import) | 充足 | §8-1。呼び出したのは全て既存`er003_v1_n3_01_tts_generate.py`/`er003_v1_n3_01_assemble.py`の既存関数(無改変)。新規driverスクリプトは一時実行用(scratchpad配置、リポジトリへコミット対象外) |
| 2 | retry/fallback/regeneration整合 | 充足 | §8-2。既存Human Review Lock/retry予算を独自判断で回避していない(7segment全て通常のOK経路) |
| 3 | Gateロジック無改変 | 充足 | §2・6。辞書エントリ追加のみ、`classify_foreign_tokens_in_japanese_text`/`foreign_token_gate_requires_stop`のコード自体は無変更(diff確認済み) |
| 4 | runtime発火(実TTS/ASR/Assembly/Gate) | 充足 | §8・9 |
| 5 | 回帰テスト | 充足 | §6(既存13+新規4、計17件PASS) |
| 6 | model_id/routing | 充足 | TTS=`gemini-3.1-flash-tts-preview`、ASR=`gpt-4o-mini-transcribe`(既存routing、無変更) |
| 7 | 辞書diff | 充足 | §2・§13(diff全文) |
| 8 | OPEN-129整合 | 充足 | §9。Audio Validation Gate opt-in ON(required_structure)PASS |
| 9 | 既存artifact不変性 | 充足 | §8-2。他7segment+KP1-4がbyte一致(diff確認済み) |
| 10-12 | SSOT反映(CURRENT_SPEC/OPEN_ITEMS/DECISION_LOG) | **統合タスク側で実施**(本SonnetはSSOT編集禁止のため未実施、追記文案は§14) | — |
| 13 | Git(commit/push) | **統合タスク側で実施**(本SonnetはGit操作禁止) | — |
| 14 | 承認内容とProduction挙動一致 | 充足 | ユーザー承認(冒頭記載)通り「辞書エントリ追加のみ、Gateロジック不変」で実装。追加語も承認された15語と完全一致(diff確認済み) |
| 15 | Gate 4 Dangling Reference Check | 充足 | 新規追加ファイルはplayer(読み取り専用、mp3変換のみ)とREPORT本体のみ。既存ファイルへの参照切れ無し |

## 12. OPEN-145/146/121発火有無(runtime evidence)

7segmentの`attempts_log[0]`を確認した結果:

- **OPEN-121(TTS Repetition QA)**: `repetition_qa_checked=false`(全7件)。
  そもそも本Production配線ではrepetition QAは`full_story_part1/2`・
  `point_one`・`point_two`の英語本文4segmentのみが対象(ユーザー承認済み範囲)
  であり、今回対象の7segment(日本語)は元々対象外のため不発火は想定通り。
- **OPEN-145(日本語ASR表記ゆれ対策、Reading Resolver)**: `reading_resolver_
  info=null`(全7件)。1回目のASR照合で正常一致したため、Reading Resolverの
  フォールバック自体が起動しなかった(想定通り、異常ではない)。
- **OPEN-146(英語記事中の日本人名ローマ字表記事前確認)**: 該当無し。本記事
  (AI Manufacturing)の英語本文に日本人名は登場しないため、そもそも対象外。

いずれも安全に「不発火」であり、Gateの誤動作や想定外の分岐は確認されなかった。

## 13. 辞書エントリのdiff全文(参考、実装は前回セッションで完了済み)

```diff
 DEFAULT_JA_READING_DICTIONARY = {
     "cm": "センチ", "kg": "キログラム", "km": "キロメートル", "kcal": "キロカロリー",
     "ceo": "シーイーオー", "wi-fi": "ワイファイ", "cafe": "カフェ",
+    # ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01
+    # (2026-09-12、ユーザー承認=APPROVED_FOR_PRODUCTION、辞書エントリ追加の
+    # みでGateロジック自体は不変)。Trend/News editorial modeで技術トレンド系
+    # テーマを扱う際に高頻度で出現し得る略語15語を予防的に追加登録する
+    # (根拠: FAMILY-A-TREND-AI-MANUFACTURING-A2-JA-FOREIGN-TOKEN-GATE-
+    # RECONCILE-01_REPORT.md 候補案A)。
+    "ai": "エーアイ", "it": "アイティー", "ev": "イーブイ", "iot": "アイオーティー",
+    "dx": "ディーエックス", "gps": "ジーピーエス", "sns": "エスエヌエス", "pc": "ピーシー",
+    "gdp": "ジーディーピー", "eu": "イーユー", "nasa": "ナサ", "ar": "エーアール",
+    "vr": "ブイアール", "esg": "イーエスジー", "nft": "エヌエフティー",
 }
```

## 14. SSOT追記文案(統合タスク側での反映用、本Sonnetは編集していない)

### CURRENT_SPEC.md追記案

「日本語canonical text向け読み方辞書(`DEFAULT_JA_READING_DICTIONARY`)へ、
2026-09-12ユーザー承認によりAI/IT/EV/IoT/DX/GPS/SNS/PC/GDP/EU/NASA/AR/VR/
ESG/NFTの15略語を追加登録した(ER-009-JA-READING-DICTIONARY-ACRONYM-
EXPANSION-AND-TREND-A2-RESUME-01)。Gate判定ロジック自体(`classify_foreign_
tokens_in_japanese_text`/`foreign_token_gate_requires_stop`)は無変更。」

### OPEN_ITEMS.md ER-009行への追記案

「2026-09-12、ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-
RESUME-01でユーザー承認済み15略語を辞書登録し、Trend記事(family_a_trend_ai_
manufacturing_prod_run_01)A2で停止していた7segment(japanese_title/preview/
comment_1〜4/kp5日本語gloss)のHUMAN_REVIEWを解消、TTS再開+Assembly完成+
Audio Validation Gate(既定/opt-in両方)PASSまで完了した。標準player新規
作成(`player_std/a2_index.html`)。追加費用¥9.70(記事全体累計¥131.68)。
詳細は`ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-
01_REPORT.md`参照。」

### DECISION_LOG.md追記案

「2026-09-12: Trend/News editorial modeの日本語Foreign Token Gate用
読み方辞書へ、ユーザー承認済み15略語(AI/IT/EV/IoT/DX/GPS/SNS/PC/GDP/EU/
NASA/AR/VR/ESG/NFT)を追加登録することを承認。Gateロジック自体は変更しない
辞書拡張のみの対応とする。承認範囲: ER-009-JA-READING-DICTIONARY-ACRONYM-
EXPANSION-AND-TREND-A2-RESUME-01。」

## 15. 変更・新規作成ファイル一覧(絶対パス、Git操作は本タスクで未実施)

### 前回セッションで既に変更済み(今回は検証のみ、内容変更無し)
- `C:\Users\tensh\eigo-radio\er003_audio_tts_asr_safety.py`
- `C:\Users\tensh\eigo-radio\er009_ja_foreign_token_gate_01_test_01.py`

### 今回のセッションで変更(既存追跡ファイル、`git diff`で確認済み)
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\tts_generation_results.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\review_lock_state.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\run_summary_tts.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\raw_usage_log_audio.jsonl`(既存ファイルへ追記)

### 今回のセッションで新規作成
- `C:\Users\tensh\eigo-radio\er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_a2_player.py`(A2標準player生成スクリプト、B1B版を雛形)
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\timeline.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\gain_report.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\audit\headroom_report.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\run_summary_assemble.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\narration\japanese_title.wav`/`preview.wav`/`comment_1.wav`〜`comment_4.wav`/`meaning_5.wav`(gitignore対象`*.wav`)
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\narration\attempts\{comment_1,comment_2,comment_3,comment_4,japanese_title,meaning_5,preview}_attempt1_standard.wav`および対応`.json`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\a2\assembled\English_Your_Way_A2_FAMILY_A_TREND_AI_MANUFACTURING_PROD_RUN_01.wav`(gitignore対象)
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\a2_index.html`
- `C:\Users\tensh\eigo-radio\er011_output\family_a_trend_ai_manufacturing_prod_run_01\player_std\audio_mp3\a2\`配下30ファイル(mp3変換、gitignore対象)

### 触れていないこと(スコープ外、確認済み)
- `er012_*`、`er011_open121_*`、`er011_output\discovery_generalization_wake_before_alarm_trial_12\`には一切アクセス・変更していない。
- 上記以外の`git status`上の既存差分(`CURRENT_SPEC.md`/`er006_output\master_audio_store_01\*`/`er011_output\attempt_history.jsonl`/`er011_output\family_a_completion_a2_trend_end_to_end_01\*`/`er011_open121_*`/`er012_b_family_production_runner_01.py`/`er011_output\discovery_generalization_wake_before_alarm_trial_12\*`/`er006_output\audio_retry_cascade_prod_01\human_review_queue.jsonl`/`er006_output\pronunciation_ledger_01\ledger.json`)は本タスク開始前から存在した他Agent/他タスクの差分であり、本タスクでは一切編集・stageしていない。

## 16. Status

`APPROVED_FOR_PRODUCTION`(辞書エントリ追加、ユーザー承認済み)+配線実装済み
(Gate再判定・TTS再開・Assembly・Gate opt-in全てruntime実行済みでPASS)。
`PRODUCTION_WIRED`という正式宣言はSonnetからは行わない(Fable/ユーザー
受入判定待ち)。SSOT反映・Git commit/pushは統合タスク側で実施。
