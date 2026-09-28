# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT

管理ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(Trial、Production実装なし)

## 1. Existing Spec / Prior Trial確認

- 対象は`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01`と同じ10 phrase(EN 9+
  JA 1「ポイント解説」、`er006_audio_cost_pilot_02_shared_narration.
  FIXED_ENGLISH_TEXTS`/`FIXED_JAPANESE_TEXTS_A2_ONLY`)。
- 現行Production Master実測(read-only、`er006_output/master_audio_store_01/
  manifest.json`): EN 9件全て`style_instruction_version="v2_flash_lite_
  short_style"`、`tts_model_id="gemini-3.8-flash-lite-tts"`。styleは
  `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN_
  FALLBACK[0]`="natural, clear, conversational"を**9件全てに同一文言**で
  適用している(welcome〜num_fiveの区別なし)。JA(point_explanation)は
  style override無し(既定`voice01.p9a.JAPANESE_STYLE_PREFIX`、記事本文
  向けの長い既定style)。
- TRIAL-01実測: Candidate A(現行Master再利用)はOne〜Five 5/5OK・drift無し
  (duration幅0.33秒、RMS幅4.68dB)。Candidate B(Role style「brief, clear,
  neutral」)はnum_one/two/three 3attempt全滅(OPEN-222)。Candidate C
  (2.5 Pro系既定style)もnum_three全滅・num_two 2/3ドリフト。同一の極短
  数字語不安定性が、Flash-Lite固有ではなくモデル・style文言を変えても
  再現することが既に確認済み(OPEN-222)。

## 2. 実施内容

新規`er043_tts_fixed_shell_master_champion_trial_02.py`(生成、`er040_...
_trial_01.py`の`trial_master_audio_store`/`ensure_candidate_a_from_
production`/`trial_japanese_style_override`をimport/流用)+
`er043_..._page_01.py`(mp3変換・One→Five連結ページ生成、`er040_..._
page_01.py`の`wav_to_mp3`/`concat_wavs`をimport/流用、独自に簡易F0
[基本周波数]推定[自己相関ベース、librosa不使用の簡易proxy]を追加)+
`er043_..._test_01.py`(17 unit test、実API無し)。

実行はphrase group単位で分割実行した(前回インシデント再発防止、
delegation「実行安全」節):

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates A --phrases all --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates B,C --phrases welcome,preview_intro,key_phrases_intro --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates B,C --phrases full_story_intro --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates B,C --phrases num_one,num_two,num_three,num_four,num_five --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates B,C --phrases point_explanation --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40
.venv\Scripts\python.exe er043_tts_fixed_shell_master_champion_trial_02_page_01.py
```

累計費用(`raw_usage_log.jsonl`、`fx_runner.compute_cost_jpy_so_far`実測):
**¥1.54**(gemini ¥1.35 + openai_asr ¥0.19、Guardrail¥40の約3.9%)。
Candidate Aは新規TTS/ASR呼び出し無し(¥0、Production Master再利用)。
暴走・Guardrail超過なし。

テスト: `.venv\Scripts\python.exe -m unittest er043_tts_fixed_shell_master_
champion_trial_02_test_01`(pytest未インストールのため代替、TRIAL-01と
同じ判断)で**17/17 PASS**。`run_project_regression.py --pattern
"er043*_test_*.py"`でも**collected=17 passed=17 failed=0 errors=0
skipped=0**を確認。

## 3. num_fourの扱いについて(delegation内表記の矛盾を解消した実装判断)

delegation Fable補足の(i)は「指摘なしphrase」の例としてnum_fourを挙げるが、
(ii)は「num_one〜num_five=5個セットとして同一styleで一括生成」と明記しており、
num_fourの扱いについて両者は矛盾している。**ユーザー原文(「One.〜Five.
現行は...5個セットとして、テンション/抑揚/語尾/音量/テンポを安定させる」)を
最上位の根拠とし**、5-word setの一体性(num_fourだけ旧styleのままでは「揃い」
を安定させるという目的自体が達成できない)を優先して、num_fourもグループ3
(5個set style)の対象に含めることを実装判断とした(design doc §2-1に記録)。
この点はTrial内の解釈判断であり、Production仕様への無断変更ではない。

## 4. Candidate設計(グループ別、詳細は設計書§2)

| Group | 対象phrase | 方針 |
|---|---|---|
| 1(指摘なし) | welcome/preview_intro/key_phrases_intro | 仕様(style文言・model・voice)をAと同一のまま2回生成(ばらつき比較) |
| 2(full_story_intro) | full_story_intro | 「発音が速すぎる」への対応、pace指示を追加した style を2回生成 |
| 3(num_one〜five) | num_one/two/three/four/five | 「5個セットとして...安定させる、Fiveを疑問形にしない」への対応、B/Cで異なる2種のstyle |
| 4(point_explanation) | point_explanation(JA) | 「平板」への対応、B/Cで異なる2種のJA style |

Candidate Aは新規TTS/ASR呼び出しなし(Production既存Master再利用、
`er040_..._trial_01.ensure_candidate_a_from_production`をそのまま呼ぶ)。
B/CはいずれもFlash-Lite backend(`speech_metadata_flash_lite`)を使用し、
モデルはAと揃えてstyle文言のみを変える(理由: モデル比較が目的ではない、
Aとの公平な比較のためモデルを固定、Flash-LiteはOPEN-201実測で2.5 Pro系より
大幅に安価で¥40 Guardrail内に収めやすい。詳細design doc §4)。

## 5. 使用Prompt全文(逐語、phrase別)

### Group1(welcome/preview_intro/key_phrases_intro、B・C共通、versionのみ相違)

`"natural, clear, conversational"`(現行Production `FAMILY_X_ROLE_STYLE_EN_
FALLBACK[0]`と完全一致、新規文言ではない)

### Group2(full_story_intro、B・C共通)

`"natural, clear, conversational, unhurried pace, with a brief pause before continuing"`

### Group3(num_one〜num_five)

- Candidate B: `"calm, steady, declarative tone, even volume and pace across
  the set, ending each word with a clear falling pitch, stated plainly,
  never rising like a question"`
- Candidate C: `"measured, matter-of-fact delivery, consistent energy and
  tempo for every word, plain falling pitch at the end, spoken as a flat
  statement, not a question"`

(TRIAL-01の既知失敗文言「brief, clear, neutral」は再利用していない、
OPEN-222。unittest`test_group3_style_texts_do_not_reuse_known_failure_
wording`で回帰確認済み)

### Group4(point_explanation、JA)

- Candidate B: `"自然な抑揚をつけて、はっきりと落ち着いた調子で話す"`
- Candidate C: `"やわらかい自然な抑揚で、簡潔かつ丁寧に伝える"`

## 6. 結果(status/ASR)

### 6-1. 全体結果(10 phrase × 3 candidate)

| Candidate | OK | STOPPED |
|---|---|---|
| A(Production再利用) | 10/10 | 0 |
| B(新規生成) | 7/10 | 3(num_one/num_three/num_four) |
| C(新規生成) | 9/10 | 1(num_three) |

welcome/preview_intro/key_phrases_intro/full_story_intro/point_explanationは
A/B/C全て`asr_text`が原文と一致(drift無し)。num_one〜fiveのみ候補ごとに
個別のドリフトが発生した。

### 6-2. num_one〜five 個別結果とattempts_log

| phrase | A | B | C |
|---|---|---|---|
| num_one | OK(asr="One") | **STOPPED**(3attempt: "一"→"一"→"1") | OK(asr="one") |
| num_two | OK(asr="2") | OK(asr="2") | OK(asr="2") |
| num_three | OK(asr="3") | **STOPPED**(3attempt: "三"→"三"→"三") | **STOPPED**(3attempt: "三"→"三"→"三") |
| num_four | OK(asr="four") | **STOPPED**(3attempt: "四"→"四"→"四") | OK(asr="Four") |
| num_five | OK(asr="Five") | OK(asr="five") | OK(asr="Five") |

いずれのSTOPPEDもCJK(漢数字)への言語ドリフトであり、OPEN-222の既知パターン
(style文言によらず再現する極短数字語の不安定性)と一致する。**新しいstyle
文言でも根本原因は解消しなかった**が、Candidate C(4/5 OK)はCandidate B
(2/5 OK)より安定した。既存Human Review Lock(`review_lock.guarded_
generate`)がSTOPPEDを正しく検出・ブロックしており、独自retryの追加は行って
いない。

### 6-3. One〜Five揃いの定量比較(OK件数のみ、STOPPEDは欠落のまま連結)

| Candidate | OK件数 | duration幅(max-min) | RMS幅(max-min) |
|---|---|---|---|
| A | 5/5 | 0.33秒 | 4.68dB |
| B | 2/5(num_two/five) | 0.11秒 | 1.09dB |
| C | 4/5(num_one/two/four/five) | 0.10秒 | 5.58dB |

B/Cとも母数が5より少ないため直接比較は限定的だが、**Candidate Cのduration
揃いはAよりわずかに良い(0.10秒<0.33秒)一方、RMS(音量)揃いはAより悪い
(5.58dB>4.68dB)**。Aが唯一の5/5完全セット。

### 6-4. 簡易F0(語尾ピッチ)proxy指標(自己相関ベース、librosa不使用)

本環境にlibrosaが無いため、`er043_..._page_01.estimate_pitch_trend`で
自己相関ベースの簡易F0推定を実装した(語の前半1/3と後半1/3の平均F0を比較、
比率+8%超を「rising=疑問形っぽさの疑い」と判定する簡易proxy、厳密なピッチ
トラッキングではない旨をページ・JSONに明記)。

| phrase | A | B | C |
|---|---|---|---|
| num_one | falling | STOPPED | falling |
| num_two | flat | falling | falling |
| num_three | falling | STOPPED | STOPPED |
| num_four | **rising** | STOPPED | **rising** |
| num_five | **rising** | flat | **rising** |

**現行Production Baseline(Candidate A)は、この簡易指標でもnum_four/
num_fiveが「rising(疑問形っぽさの疑い)」と判定された**。ユーザー指摘
「Fiveが疑問形っぽい」と方向性が一致する。Candidate B(唯一成功したnum_five
の1サンプル)は"flat"だったが、num_one/three/fourがSTOPPEDのため5-word
全体としての改善検証はできていない。Candidate Cはnum_four/fiveともAと同じ
「rising」判定であり、この指標上は改善が確認できなかった(Candidate Cの
style文言は語尾下降を明示的に指示しているにもかかわらず改善が見られない
ため、この簡易proxy自体の精度限界の可能性も含め、ユーザー自身の試聴判断を
優先すべき機械判定である)。

## 7. 試聴ページ・Pages公開確認(7項目)

- 試聴ページ: `user_test/fixed_shell_champion_trial_02/index.html`
- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_champion_trial_02/index.html

7項目全て実測確認済み(§8)。

## 8. Pages公開確認ログ(逐語記録、commit `7f01bad1` push後に実施)

1. **URL 200確認**: `curl -sI .../fixed_shell_champion_trial_02/index.html`。
   push直後は404(Pages未反映)、10秒間隔でpolling後 約90秒後に
   `HTTP/1.1 200 OK`(Content-Length: 14660)を確認。
2. **実ブラウザ相当のDOM取得**: `"C:\...\msedge.exe" --headless --disable-gpu
   --dump-dom <URL>` で公開DOMを取得(14,793 byte)。exit code 0。
3. **placeholder不在確認**: 取得DOM中`(existing 6-role value, unchanged)`の
   出現回数=**0件**。
4. **Style Prompt全文の実表示確認**: 6種類のstyle文言(group1〜4のB/C、
   group1はA/B/C共通文言)全てが、DOM中に**省略なく完全一致で出現**する
   ことを`grep -o`(英語文言)/`grep -c`(日本語文言)で確認: group1
   "natural, clear, conversational"=6件(3phrase×B/C)、group2 pace文言=2件、
   group3 B文言=5件(5word分、STOPPED含む)、group3 C文言=5件、group4 JA
   B文言=1件、group4 JA C文言=1件。
5. **`<audio>`件数**: DOM中`<audio`出現数=**29件**(A=10 OK+B=7 OK+C=9 OK
   +One→Five連結3件=29、champion_trial_results.jsonのstatus集計と完全一致)。
6. **mp3個別確認(29件全て)**: `curl -sI`で全29件が`HTTP/1.1 200 OK`・
   `Content-Type: audio/mp3`・`Content-Length`非ゼロを確認(FAIL_COUNT=0)。
   代表4件(welcome_candA/num_three_candA/one_to_five_candC/point_
   explanation_candB)を実ダウンロードし、MP3フレーム同期バイト
   (`0xFF`+`0xEx`/`0xFx`)の検出によりデコード可能な構造であることを確認
   (lameenc encoder使用、全29件同一コード経路で生成のため代表確認とした)。
7. **ページ表示StyleとStyle metadata(json)の一致**: `champion_trial_
   results.json`の`style_prefix_used`値5サンプル(welcome/B, num_one/B,
   num_three/C, point_explanation/B, full_story_intro/C)全てが公開DOM内に
   文字列として完全一致で出現することを確認(page生成コードが同じ
   `style_prefix_used`フィールドから直接HTMLへ書き出しているため、
   構造的に一致が保証される設計)。

7項目全て満たしたため、試聴ページは完成状態にある。

## 9. Production無変更の証拠

- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/"
  "er006_output/master_audio_store_01/" | grep -v er043`は、本Trial作業
  開始前から既に存在していた他タスク(Task 1: `advanced_english_
  explanation_audio_style_trial_03*`、および`er006_output/master_audio_
  store_01/manifest.json`・`reuse_telemetry.jsonl`の既存差分)のみを含み、
  本Trialが新規に加えた差分は無い(`grep -c "trial_ch2"`でProduction
  manifest差分を検索した結果0件、本Trialのstyle keyは一切混入していない
  ことを確認)。
- Production Master Audio Store(`er006_output/master_audio_store_01/`)への
  書き込みは、Candidate A(read-only、`shutil.copyfile`のみ、`get_or_
  generate`を呼ばない設計)・Candidate B/C(`trial_master_audio_store`
  contextで`store.STORE_DIR`等をTrial専用pathへ一時的に差し替え、`finally`
  で必ず復元)のいずれからも発生しない。

## 10. 新規発見・既知課題

1. **num_three(3.）はA以外(B/C双方)で3attempt全滅**。TRIAL-01では
   Candidate C(既定2.5 Pro系)でも同型の失敗が確認されていたが、今回は
   Flash-Lite backend + 全く新しい2種のstyle文言でも同じ結果になった。
   num_threeの不安定性は、style文言やモデルの選択に依存しない、より
   根本的な限界(OPEN-222の考察を追加裏付け)である可能性が高い。
2. **Candidate B(5個set style)はnum_one/three/fourの3語が失敗し、5/5
   完全成功したのはCandidate A(現行Production Baseline)のみ**。「テンション/
   抑揚を安定させる」ことを狙った新style自体が、皮肉にも安定性
   (ASR合格率)の面ではAより悪化した。
3. 簡易F0指標では現行Production Baseline自体がnum_four/fiveで「rising」
   判定であり、ユーザー指摘(Fiveが疑問形っぽい)と整合する一方、Candidate C
   のstyle文言(語尾下降を明示指示)でも改善が確認できなかった。これは
   (a)この簡易proxy指標自体の精度限界、(b)Flash-Liteモデルが語尾ピッチを
   style指示通りに制御しきれていない可能性、のいずれかであり、最終判断は
   ユーザー試聴に委ねる。
4. `er011_output/attempt_history.jsonl`(共有固定path、OPEN-223と同型)へ
   本Trial実行分の追記が発生した可能性がある(commit対象外)。

## 11. SSOT追記案(文案のみ、RESULT_PACKETへ転記)

- REPORT_LEDGER新規行: 本REPORTへのリンク、Status=`USER_DECISION_REQUIRED`。
- DECISION_LOG追記案: 「TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02実施、
  A(Production Baseline)/B/C 3候補比較、ユーザー試聴によるChampion選定待ち」。
- OPEN-222追記案: 「2026-09-28追記(TTS-FIXED-SHELL-MASTER-CHAMPION-
  TRIAL-02): 全く新しい2種のstyle文言(Role style「brief, clear, neutral」
  を再利用しない)でもnum_three(3attempt全滅、B/C双方)・num_one/four
  (Candidate Bのみ全滅)が再現し、style文言に依存しない極短数字語の限界
  という既存考察をさらに裏付けた。」

## 12. Trial Status

`USER_DECISION_REQUIRED`(Championをユーザーが選ぶ前段階)。STOP要因なし
(Guardrail超過なし、暴走なし)。Sonnetは`VALIDATED`を自己宣言しない。

## 13. 修正1回目(未合格attemptの可視化、¥0、2026-09-28)

delegation本文は「REPORT §9に追記」と指定していたが、既存§9は既に
「Production無変更の証拠」として完結した内容であり、上書きすると証跡が
失われるため、本節を新規§13として末尾に追加した(delegationの意図=
「今回の追加作業の記録をREPORTへ追記する」ことは本節で満たしている)。

### 13-1. 追加内容

試聴ページ(`user_test/fixed_shell_champion_trial_02/index.html`)に、
既存section(legend/One→Five連続再生比較[OK音声のみ、既存のまま不変]/
Phraseごと比較表)を一切変更せず、`</body>`直前へ以下2つの新規sectionを
追加した(新規TTS/ASR呼び出しは無し、既存生成物の読み取り+mp3変換のみ)。

1. **「ASR 未合格 attempt(人間確認用・Production 登録不可のまま)」**:
   STOPPEDとなった4組(Candidate B: num_one/num_three/num_four、
   Candidate C: num_three)、計12 attemptについて、attemptごとに
   音声(mp3)・ASR認識結果・失敗分類(`audio_classification`)・
   duration・簡易F0 pitch_trend・verified状態を表形式で掲載。
   各ブロックにcanonical_text・Style Prompt全文・reasonも明記し、
   「合格でもProduction登録可でもない」旨を赤字で明示。
2. **「One→Five 参考連結(未検証attemptを含む、参考情報)」**: Candidate
   B/Cそれぞれについて、OK音声+STOPPED phraseは最初のattempt(attempt1)
   を組み合わせた参考連結mp3(`one_to_five_candB_ref.mp3`/
   `one_to_five_candC_ref.mp3`)を追加。構成(どのphraseがOKでどれが
   未検証attemptか)を明記し、Championの正式候補ではない旨を赤字で明示。
   Candidate Aの既存連結(`one_to_five_candA.mp3`)は変更していない。

### 13-2. attemptごとのASR結果一覧(全12 attempt、`champion_trial_results.
json`実測から転記)

| Phrase | Candidate | attempt | ASR結果 | 失敗分類 | duration | pitch_trend(簡易proxy) |
|---|---|---|---|---|---|---|
| num_one | B | 1 | "一" | TTS_FAILURE | 0.93s | rising(疑問形っぽさの疑い) |
| num_one | B | 2 | "一" | TTS_FAILURE | 0.95s | rising(疑問形っぽさの疑い) |
| num_one | B | 3 | "1" | TRUE_CONTENT_MISMATCH | 0.99s | flat(ほぼ平坦) |
| num_three | B | 1 | "三" | TRUE_CONTENT_MISMATCH | 1.04s | flat(ほぼ平坦) |
| num_three | B | 2 | "三" | TRUE_CONTENT_MISMATCH | 1.05s | falling(平叙文らしい語尾) |
| num_three | B | 3 | "三" | TRUE_CONTENT_MISMATCH | 1.00s | flat(ほぼ平坦) |
| num_three | C | 1 | "三" | TRUE_CONTENT_MISMATCH | 0.97s | rising(疑問形っぽさの疑い) |
| num_three | C | 2 | "三" | TRUE_CONTENT_MISMATCH | 0.92s | rising(疑問形っぽさの疑い) |
| num_three | C | 3 | "三" | TRUE_CONTENT_MISMATCH | 0.88s | flat(ほぼ平坦) |
| num_four | B | 1 | "四" | TRUE_CONTENT_MISMATCH | 0.98s | rising(疑問形っぽさの疑い) |
| num_four | B | 2 | "四" | TRUE_CONTENT_MISMATCH | 1.12s | rising(疑問形っぽさの疑い) |
| num_four | B | 3 | "四" | TRUE_CONTENT_MISMATCH | 0.94s | flat(ほぼ平坦) |

12 attempt全てwav保存済み(音声未保存attemptなし)、全件mp3変換済み。
全attemptともASR結果は原文(One/Three/Four)と不一致(CJK漢数字化または
数字・別語への誤認識)であり、OPEN-222の既知パターンと一致する。この
一覧だけでは「音声自体は正しく発話されているが単語1語の極短音声に対する
ASR側が誤認識している可能性」と「TTS自体が誤った音を生成した可能性」を
機械的に区別できないため、最終判断はユーザー試聴に委ねる(design方針通り)。

### 13-3. One〜Five「参考込み」揃い指標(既存§6-3のOK限定版との対比)

| Candidate | 構成 | 揃い5/5化 |
|---|---|---|
| A(既存、不変) | 5/5 OK | 対象外(既存§6-3の通り5/5完全OK) |
| B(参考連結) | OK=num_two/num_five、未検証attempt1=num_one/num_three/num_four | 5/5(うち3件は未検証) |
| C(参考連結) | OK=num_one/num_two/num_four/num_five、未検証attempt1=num_three | 5/5(うち1件は未検証) |

既存§6-4の簡易F0 proxyはSTOPPED attemptにも同一関数(`estimate_pitch_
trend`)で適用済み(§13-2表のpitch_trend列)。追加傾向: num_four(B)の
attempt1/2は「rising」、num_one(B)のattempt1/2も「rising」であり、
現行Production Baseline(Candidate A)でnum_four/fiveが「rising」だった
既存観察(§6-4)と方向性として近い。ただしこの簡易proxyの精度限界は
既存記載の通りであり、機械判定を最終結論として扱わない。

### 13-4. Production無変更・API支出の実測

- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/"
  "er006_output/master_audio_store_01/" | grep -v er043`は§9記載時点と
  差分無し(本追加作業はPhrase生成・ASR呼び出しを一切行っていないため)。
- 新規TTS/ASR呼び出し**0件**: `er043_output/tts_fixed_shell_master_
  champion_trial_02/raw_usage_log.jsonl`の行数は本追加作業の前後で
  **64行のまま不変**(`wc -l`実測)。`_page_01.py`はmp3変換
  (`page1.wav_to_mp3`)とwav単純連結(`page1.concat_wavs`)のみを行い、
  いずれも既存生成物のファイル読み取りのみでAPIを呼ばない設計。
- Production Master Audio Store(`er006_output/master_audio_store_01/`)
  への書き込みは発生していない(読み取りすら発生しない、本追加作業は
  `er043_output/`配下のTrial専用attempt wavのみを参照)。
- `run_project_regression.py --pattern "er043*_test_*.py"`:
  **collected=17 passed=17 failed=0 errors=0 skipped=0**(既存17件を
  維持、新規テスト追加なし、既存の`er043_..._page_01.py`公開関数
  シグネチャは変更していないため影響なし)。
- Pages公開確認7項目: commit push後に再実施し、全項目実測PASSを確認
  (詳細は本追加作業のdelegation報告[RESULT_PACKET_CH2B]およびcommit
  ログ参照)。
