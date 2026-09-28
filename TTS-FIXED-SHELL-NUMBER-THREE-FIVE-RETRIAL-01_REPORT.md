# TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md

管理ID: TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(Trial、ユーザー承認済み)

## 1. 左/中/右 → A/B/C 対応表(冒頭必須項目)

`user_test/fixed_shell_champion_trial_02/index.html`の比較表ヘッダー行
(`<th>Phrase</th><th>A</th><th>B</th><th>C</th>`)より、**列順どおり
左=A、中=B、右=C**であることを実データ突き合わせで確認した(詳細根拠は
`docs/pm/design_tts_fixed_shell_number_three_five_retrial_01.md`§2)。

| phrase | 位置(delegation) | candidate | model | voice | Style Prompt全文 |
|---|---|---|---|---|---|
| welcome | 左 | A | gemini-3.8-flash-lite-tts | Charon | "既存Production v2_flash_lite_short_style(FALLBACK[0])" |
| preview_intro | 右 | C | gemini-3.8-flash-lite-tts | Charon | "natural, clear, conversational" |
| key_phrases_intro | 右 | C | gemini-3.8-flash-lite-tts | Charon | "natural, clear, conversational" |
| full_story_intro | 右 | C | gemini-3.8-flash-lite-tts | Charon | "natural, clear, conversational, unhurried pace, with a brief pause before continuing" |
| num_one | 右 | C | gemini-3.8-flash-lite-tts | Charon | "measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question" |
| num_two | 中 | B | gemini-3.8-flash-lite-tts | Charon | "calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question" |
| num_four | 右 | C | gemini-3.8-flash-lite-tts | Charon | (num_oneと同一C系統文言) |
| point_explanation | 中 | B | gemini-3.8-flash-lite-tts | Charon(JA) | "自然な抑揚をつけて、はっきりと落ち着いた調子で話す" |

## 2. 実施内容

num_one/num_two/num_fourの中にB系統・C系統の両方が採用されていたため、
delegation指示どおり両系統で再Trialした。num_three/num_five × B系統/C系統
× 4 take = 16 take。style文言は`er043_tts_fixed_shell_master_champion_
trial_02.py`の既存定数(`STYLE_TEXT_GROUP3_B`/`STYLE_TEXT_GROUP3_C`)を
そのままimportし、新規文言は一切考案していない。model/voiceも無変更
(gemini-3.8-flash-lite-tts / Charon)。

## 3. 既存Spec確認結果

`er011_human_review_lock_01.py`(`PRODUCTION_MAX_TTS_ATTEMPTS=3`、
`guarded_generate`decorator)をそのまま`voice01.generate_charon_english`
経由で使用(独自retry追加なし)。Master Audio Storeは
`er040...trial_master_audio_store()`で`er047_output/.../master_store/`
へ隔離(Production Store非書込、実測確認済み、§7参照)。

## 4. 実行コマンド全文(逐語)

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er047_tts_fixed_shell_number_three_five_retrial_01.py --phrases num_three,num_five --styles B,C --takes 4 --out-dir "er047_output/tts_fixed_shell_number_three_five_retrial_01" --trial-store "er047_output/tts_fixed_shell_number_three_five_retrial_01/master_store" --budget-jpy 20
```
exit code 0。

## 5. ASR/take合否内訳

| phrase | style系統 | take1 | take2 | take3 | take4 |
|---|---|---|---|---|---|
| num_three | B | OK(3attempt目) | STOPPED | STOPPED | OK(1attempt目) |
| num_three | C | STOPPED | OK(3attempt目) | STOPPED | STOPPED |
| num_five | B | OK(3attempt目) | STOPPED | STOPPED | STOPPED |
| num_five | C | STOPPED | OK(2attempt目) | OK(1attempt目) | OK(2attempt目) |

合計: OK 7/16、STOPPED 9/16(3attempt全滅、既存Human Review Lock、
OPEN-222既知の極短数字語ASRドリフトと同型)。全STOPPED takeの全attempt
音声(計27 attempt音声)を試聴ページへ「Production登録不可(人間確認用)」
として掲載済み。独自retry追加は一切していない。

## 6. 費用

`raw_usage_log.jsonl`実測(`fx_runner.compute_cost_jpy_so_far`):
**¥1.69**(gemini ¥1.51 + openai_asr ¥0.18、上限¥20の約8.5%)。budget到達・
超過なし。

## 7. Production非影響の確認

- `git diff --stat HEAD -- "er0*.py" ...` で本タスク関連ファイル
  (`er047_*`)以外に、他並行Agentによる既存差分(`er003_b1_p9a_audio.py`
  等、`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`起因、本タスク開始前
  から存在)を確認したが、本タスクでは一切編集・stageしていない。
- Production Master Store manifest(`er006_output/master_audio_store_01/
  manifest.json`)を実行前後でsha256比較し、本タスクの生成entryが含まれて
  いないことを確認(diff中に`num_three`/`num_five`/`retrial01_take`文字列
  が0件、Trial Store側manifestに7件[OK take数と一致]を確認)。
- `er011_output/attempt_history.jsonl`・`er006_output/audio_retry_
  cascade_prod_01/human_review_queue.jsonl`は共有append-onlyログのため
  本タスク実行分も追記された(OPEN-223既知の同型事象、Gate判定・
  Production音声出力に影響なし)。

## 8. Regression

`.venv/Scripts/python.exe -m unittest er047_tts_fixed_shell_number_three_five_retrial_01_test_01 -v`
19/19 PASS。`run_project_regression.py --pattern "er047*_test_*.py"`
collected=19 passed=19 failed=0 errors=0 skipped=0。

## 9. 公開試聴URL

https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_three_five_retrial_01/index.html

## 10. 公開確認(7項目、実測)

1. HTTP 200(`curl -sI`、push後約80秒でPages反映、Content-Length: 18154)。
2. headless Edge DOM取得: `msedge.exe --headless --disable-gpu --dump-dom
   <URL>` exit code 0、18,336byte取得。
3. 省略表記0件: DOM中に置換文字・省略マーカー0件を確認。
4. Style全文表示: B系統文言(158字)/C系統文言(153字)とも定義済み文字列と
   完全一致する長さで検出(切り詰めなし)、4箇所(num_three/num_five ×
   B/C)全てで確認。
5. `<audio>`件数: 45件(採用reuse3 + OKtake7 + 全attempt27[STOPPED9takeの
   一部OKtakeの成功前attempt含む] + 連結参考8)。
6. mp3全件200・Content-Type audio/mp3・非ゼロ長(45/45、FAIL 0件)。
   代表4件(adopted_num_one/num_five_styleC_take2/
   num_three_styleC_take1_attempt1/seq_styleB_take1)を実ダウンロードし
   MP3フレーム同期バイト(`0xFF`+`0xFx`)を確認(lameenc encoder使用、
   全45件同一コード経路のため代表確認とした)。
7. 表示StyleとStyle metadata(`retrial_results.json`/`champion_trial_
   results.json`)一致: 4サンプル(num_three/B take1、num_five/C take2、
   採用num_two、採用num_one)全て一致。

## 11. Production変更有無

なし(Production正式path・Production Master Store・正式Prompt・
CURRENT_SPECは一切変更していない、§7参照)。

## 12. Trial Status

`USER_DECISION_REQUIRED`。num_three/num_fiveそれぞれ、B系統/C系統の
OK take(num_three: B×2/C×1、num_five: B×1/C×3)の中からユーザーが
良いtakeを選定する必要がある。STOPPED takeの音声も人間確認用として
掲載済みのため、あわせて参考にできる。

## 13. USER_DECISION_REQUIRED事項

- num_three: どのtake(B-take1/B-take4/C-take2)を採用するか。
- num_five: どのtake(B-take1/C-take2/C-take3/C-take4)を採用するか。
- 採用後のMaster Audio Store登録・Production配線は別管理IDで実施予定
  (本Trialでは実施していない)。

## 14. 未配線APPROVED項目

採用済み8 phrase(welcome/preview_intro/key_phrases_intro/
full_story_intro/num_one/num_two/num_four/point_explanation、TRIAL-02で
ユーザー決定済み)のMaster Audio Store登録・Production配線は、いずれも
まだ未実施(別管理IDでの対応が必要)。

## 15. SSOT追記案(文案のみ、編集権なし)

### DECISION_LOG.md追記案
```
TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(2026-09-28): TRIAL-02で
採用済みのnum_one(Candidate C系統)/num_two(Candidate B系統)/num_four
(Candidate C系統)と同一model(gemini-3.8-flash-lite-tts)・同一voice
(Charon)・同一style文言で、num_three/num_fiveのみB系統・C系統それぞれ
4 takeずつ新規生成した(計16 take、OK7/STOPPED9)。ASR不合格(STOPPED)
takeも音声が保存されていれば人間確認用として試聴ページへ全attempt公開。
費用¥1.69(上限¥20)。試聴: https://shimomura055.github.io/eigo-radio/
user_test/fixed_shell_three_five_retrial_01/index.html
Status: USER_DECISION_REQUIRED(ユーザーがnum_three/num_fiveの採用take
を選定するまで)。commit fa37cd85。
```

### OPEN-222追記案(既存行への追記文)
```
**追記(2026-09-28、TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01)**:
num_three/num_fiveをB系統・C系統それぞれ4 takeずつ再Trialした結果、
16take中9takeが3attempt全滅(STOPPED)、7takeがOKとなった(1回目成功
7件中、3attempt目まで要した成功が4件)。同一style・同一model・同一voice
でも成否が非決定的であることを再確認し、極短数字語のFlash-Lite ASR厳格
一致限界という既存所見(OPEN-222)をさらに裏付けた。
```

### REPORT_LEDGER新行(該当SSOT側に追記予定、Fable/Claude編集権なし)
```
| TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01 | 2026-09-28 | Trial |
USER_DECISION_REQUIRED | ¥1.69 | num_three/num_five複数take生成、
7OK/9STOPPED、試聴ページ公開 | 本REPORT |
```

## 16. Commit / URL

commit: `fa37cd85`

Raw URL(代表):
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er047_tts_fixed_shell_number_three_five_retrial_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er047_tts_fixed_shell_number_three_five_retrial_01_page_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/design_tts_fixed_shell_number_three_five_retrial_01.md

## 17. STOP有無

STOPなし(暴走疑い・費用上限到達・スコープ拡大のいずれも発生していない)。
