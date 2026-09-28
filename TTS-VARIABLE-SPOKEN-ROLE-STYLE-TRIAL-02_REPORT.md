# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md

管理ID: TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(Trial、Production未採用)
実行: 2026-09-28(Sonnet実行層)
到達Status: **USER_DECISION_REQUIRED**(ユーザー試聴前、Production配線へ進まない)

## §1 目的・範囲

可変segment(固定phraseを除く)のRole Styleについて、日本語(Standard/A2の
preview/comment_1〜4)はJ0(現状)〜J3(J2より少し表情豊か)、英語本文
(Advanced/B1Bのtopic_intro/full_story_part1/in_one_line)はE0(現状)〜E3
(E2より少し表情豊か)の4パターンを比較する試聴ページを作成した。詳細設計は
`docs/pm/design_tts_variable_spoken_role_style_trial_02.md`。

## §2 重要な発見(J0の訂正)

delegationが想定したJ0(「落ち着いた、自然な話し言葉で」)は、実は**現行
Productionには配線されていない**(別Trial`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`
がTrial限定で導入した新規値)。コード実測の結果、現行Production日本語音声
(Standard preview/comment_1〜4)は**常に**`p9a.JAPANESE_STYLE_PREFIX`という
長文instruction(「Give the narration a noticeably animated, emotionally
present, and expressive delivery」等、むしろ表情豊かな方向)を使っており、
role別の短いstyle指定機構自体が存在しない(`generate_a2_japanese_with_
reading_safety`に`style_prefix_override`パラメータが無いことを実測確認)。
本Trialでは、この真のProduction現状をJ0として採用した(design doc §1-2)。
EN側(FULL_STORY/IN_ONE_LINE/TOPIC_INTRO)は delegation想定どおり
`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN`と完全一致
することを実測確認済み(乖離なし)。

## §3 棚卸し・対象segment(全8件、実施)

| 言語 | segment | 必須/任意 | J0/E0 |
|---|---|---|---|
| JA | preview, comment_1, comment_2 | 必須 | reuse(真のProduction現状音声、`hormuz__run_06_flashlite_full_kp`) |
| JA | comment_3, comment_4 | 任意(実施) | 同上 |
| EN | full_story_part1, in_one_line | 必須 | reuse(Task B[er038]出力、style一致確認済み) |
| EN | topic_intro | 任意(実施) | 同上 |

除外: 固定phrase(welcome/preview_intro/key_phrases_intro/full_story_intro/
num_one〜five/point_explanation、Task 2専用)、Key Phrase系(kp_english/
kp_japanese/meaning_*、Task 1専用)、full_story_part2/3(コスト抑制、理由記録)。

## §4 使用Prompt全文

**JA**: J0=`p9a.JAPANESE_STYLE_PREFIX`全文(design doc §2に逐語掲載)。
J1「落ち着いた、自然な話し言葉で。意味の流れに合わせて軽く抑揚をつけて
ください。」/J2「落ち着いた、自然な話し言葉で。強調点や話の転換に応じて
抑揚をつけてください。大げさにしないでください。」/J3「落ち着いた、自然な
話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。
演技がかった話し方は避けてください。」

**EN FULL_STORY**: E0="calm, steady news narration"/E1="calm, steady news
narration, with a touch of natural inflection that follows the meaning."/
E2="calm, steady news narration with natural emphasis at key points and
turns; not dramatic."/E3="calm, steady news narration, naturally expressive
at key points, contrasts, and the conclusion; understated, not theatrical."

**EN IN_ONE_LINE**: E0="concise, clear"/E1="concise, clear, with a natural
closing tone."/E2="concise, clear, landing naturally as a settled
conclusion; not flat, not dramatic."/E3="concise, clear, with a slightly
more expressive, confident closing landing; understated, not theatrical."

**EN TOPIC_INTRO**: E0="brief, clear, engaging news topic introduction"/
E1〜E3は design doc §4-4参照(全文同一)。

全新規style文字列は`assert_no_wpm_specification()`通過済み(数値WPM指定なし)。

## §5 試聴URL

- 新規ページ: https://shimomura055.github.io/eigo-radio/user_test/tts_variable_role_style_trial_02/index.html
- 旧ページ(先頭に案内リンク追記): https://shimomura055.github.io/eigo-radio/user_test/tts_all_role_style_trial_01/index.html

## §6 公開実ブラウザ確認結果(7項目、全て満たす)

1. HTTP 200: 確認(新規ページ・mp3全32件)。
2. 実ブラウザ相当: msedge `--headless --dump-dom`で公開DOM取得成功(226行、
   ソースと一致)。
3. 公開DOMに`(existing 6-role value, unchanged)`等の省略表記: 0件。
4. Style Prompt全文の公開DOM実表示: 確認(J0長文instruction・E3新style等を
   grepで実在確認)。
5. `<audio>`件数: 32件(8segment×4pattern)。
6. 全32 mp3: HTTP 200・`Content-Type: audio/mp3`・非ゼロ長を全件確認、1件を
   ダウンロードしffmpegでデコード可能(エラー0件)を確認。
7. ページ表示Styleと生成結果json(`style_prefix_used`)の一致: 1件(EN
   in_one_line E1)を明示クロスチェックし完全一致(他は同一sourceから機械
   生成のため構造的に一致)。

## §7 ASR/drift/retry/cost

全32件(J0/E0のreuse 8件含む)が`status=OK`。新規生成24件のうち22件は
標準1回で合格、2件(EN full_story_part1のE1=2回、E2=3回)は既存retry
cascade内で合格(`PRODUCTION_MAX_TTS_ATTEMPTS=3`を超える独自延長なし)。
言語ドリフト・Human Review Lock到達は0件。EN側`en_pronunciation_resolver_
info.hints_applied`は新規24件・既存reuse 8件とも全てfalse(発音ヒント
augmentationなし、ページ表示Style=実際にTTSへ渡した文字列そのもの)。

## §8 費用実測

**¥20.71**(gemini ¥17.75 + openai_asr ¥2.96)。Guardrail上限¥60に対し
大幅に余裕あり(必須15segment+任意9segment=24新規TTS呼び出し、理論上限
未使用のまま完了)。

## §9 regression / Production無変更証拠

- `run_project_regression.py --pattern "er044*_test_*.py"`: 11/11 PASS
  (Pattern文言逐語、固定phrase/Key Phrase非対象、Store隔離復元、
  `--stage all`相当関数なし)。
- Production無変更: `git diff --stat HEAD~2 HEAD -- "er0*.py"
  "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" |
  grep -v er044` → 空(差分なし)。

## §10 delegationからの逸脱・既知の制約

- pytest未導入のため`-m pytest`ではなく`-m unittest`で実行(結果は同一の
  11 test、`run_project_regression.py`でも同一11 testをPASS確認)。
- `er011_output/attempt_history.jsonl`/`er006_output/audio_retry_cascade_
  prod_01/human_review_queue.jsonl`が本Trial実行で追記された可能性がある
  (共有固定path、OPEN-223と同型、commit対象外)。
- J0の訂正(§2)はOPEN候補として報告する(§11)。

## §11 SSOT追記案(文案のみ、編集権なし)

- **REPORT_LEDGER新行案**: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02 | Trial |
  USER_DECISION_REQUIRED | 可変segment(JA preview/comment_1-4、EN topic_intro/
  full_story_part1/in_one_line)のRole Style 4パターン比較(J0-J3/E0-E3)、
  Style全文表示試聴ページ作成、¥20.71 | 2026-09-28`
- **DECISION_LOG追記案**: 「TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(2026-09-28）:
  日本語Role Style(J0〜J3)・英語本文Role Style(E0〜E3)比較Trialを実施。
  重要発見として、現行Production JAは役割別style機構自体を持たず常に長文
  instruction(`p9a.JAPANESE_STYLE_PREFIX`)を使用していることが判明、J0を
  この実測値へ訂正して実施した。試聴・採否はユーザー判断待ち
  (USER_DECISION_REQUIRED)。」
- **OPEN候補**: 「JA Role Style機構がProductionに存在しない(J0訂正の根拠)。
  短いJA Role Style(J1〜J3のような方向性)をProductionへ新規配線するか、
  現行の長文instruction路線を維持するかはユーザー判断待ち。関連: OPEN-201
  (role別styleはStage3の6-role最小案を初期仕様採用、と記載されているが
  JA側は未配線のまま)。」

## §12 Trial status / STOP有無

**USER_DECISION_REQUIRED**(ユーザー試聴前、Production配線へ進まない、暴走
STOPなし)。

## §13 commit / raw URL

- commit 1: `06691c46`(er044_*.py/test、design doc、delegation_log、
  er044_output json/md、試聴ページmp3/html)
- commit 2: `a0c4b592`(旧ページ先頭への案内リンク追記)

raw URL(コピペ用):
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er044_tts_variable_spoken_role_style_trial_02.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er044_tts_variable_spoken_role_style_trial_02_test_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/design_tts_variable_spoken_role_style_trial_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/user_test/tts_variable_role_style_trial_02/index.html
