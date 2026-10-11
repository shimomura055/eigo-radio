# 委任_04C 報告(Trial C: 英語ASR比較 縮小版) 2026-10-12

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04C / Trial限定・Production変更なし
詳細: `er058_output/trial_c/TRIAL_C_EN_ASR_COMPARISON_01.md`、結果 `trial_c_results_01.json`、script `er058_trial_c_en_asr_compare_01.py`
使用モデル: Azure STT en-US / OpenAI Primary ASR は測定対象=Production同一の例外。参考にlocal faster-whisper small/medium。新規LLM/TTS呼出0。

## 実施
1. 対象選定(sha重複除外): Primary NG 18 + HR queue 6 + Primary PASS対照 8 = 32本・788.6秒。`COST_ESTIMATE_C_01.md`で見積35.05円(<=40円)を確認してから実行。
2. mock乾式(`dry`)でpipeline検証 -> real(`--approved-budget-jpy 40`)。実費 **約35.05円**(`cost_actual_C_01.json`、送信秒数ベース)。他課金0、新規TTS生成0、Production書込0。
3. 除外4本(HR 2本=wav上書き疑い、対照2本=原稿復元不一致)。評価対象 NG系22+対照6。

## 結果(要約)
- 統一案(安全条件付き)の救済 4/22(18%、Wilson約7〜39%)、合意誤読11件の誤PASS 0。Azure noPLは合意誤読11件すべてで原稿へ補正せず。
- 単純ORは繰返しQA NG音声(S13)等を通した(安全条件の必要性)。合成誤読188件(最悪ケース=Secondary原稿補正)で単純OR 144/144通過、安全条件案はブロック37(数値否定全件)+警告24+残存83(内容語・固有名詞)。
- Phrase List: 同一wav 5件でPLなしの厳格PASS 3対PL付き0。
- QCD射影: 完了率95.3〜97.4%(現行93.1%)だが主因は同一Prompt継続(外挿)で、Secondary救済実測は5.6%。追加ASR費用は約0.07 -> 約0.27〜0.30円/call(Azure 1回は再生成の約13倍の費用)。
- 例外: 数値否定不呼出・固有名詞(ASR共通限界)・Gate NG・最小対(警告)・Key Phrase。

## 限界
n小・代理ラベル(人間試聴なし)・標本はNG/HR偏り。提案のみ、採用は人間ユーザー判断。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は未編集(Fable判断)。
