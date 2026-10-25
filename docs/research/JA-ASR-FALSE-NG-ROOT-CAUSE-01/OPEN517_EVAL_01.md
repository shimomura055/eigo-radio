# OPEN517_EVAL_01(OPEN-517是正案のAPI 0再評価。委任_05、2026-10-25)
事前登録=`OPEN517_PREREGISTERED_01.md`(§0〜§6)。評価=`eval_open517_api0_03.py`(proto v3 `proto_value_gate_fix_03.py` sha `00c8c133a760a3e620e07e3b0d77c2d174cab70c29f1cf72d348b0004c9ef631`)。API 0(socket guard)・LLM/ASR/TTS呼出0・費用0円・Production file変更0(`git status`で`er078_*`/`er007_*`無変更を確認)。使用モデル: なし(保存済み転写のみ。転写の元はEVAL_02記載のOpenAI `gpt-4o-mini-transcribe`/Azure ja-JP)。再現: リポジトリrootで`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open517_api0_03.py`。2回実行で標準出力が完全一致(`cmp`)=決定的。出力JSON(全771件の現行/是正後判定)=`open517_api0_eval_03.out.json`(sha `a7168756…`)。
評価方式: Productionのadapter(`evaluate_attempt_ja_with_cascade_detail`→`unified_judge`)を実際に通し、in-process差替え(`apply_in_process`、Production file無変更)で現行と是正後を比較。Secondary(Azure)はstub(呼出0。DEMOTE時は`NG_SECONDARY_UNAVAILABLE`と表示されるがこれはstubの表示で、実運用ではSecondary 1回の結果次第)。
## 1. 結果(基準別)
| 基準 | 結果 | 合否 |
|---|---|---|
| 1 増分誤NG=0(P4実attempt 133+正例対照10の現行READING_MATCH PASS 143件) | NG化/降格 **0**。`comment_4_attempt1`の`いちばん低い`↔`一番低い`はPASSのまま | 合格 |
| 2 既知負例9件がPASS以外 | **9/9**(NG_PROTECTED 8、`一分`↔`いちふん`=DEMOTE[AMBIGUOUS→Secondary]) | 合格 |
| 3 非回帰: 全771件で変化はF1由来のみ | 変化13件=F1(PASS→NG) 10件+F2の警告追加3件(PASS→PASS_WITH_WARNING、非ブロッキング)。**非READING_MATCH PASSの変化0・NG→PASS 0・警告喪失0** | 合格(警告追加3件を個別提示) |
| 4 決定性 | 2回実行で完全一致 | 合格 |
| 5 API 0・費用0円・Production変更0 | 確認済み | 合格 |
## 2. 判定が変わった全件(現行→是正後。771件中13件)
| 出所 | ID | 原稿 | 転写 | 現行 | 是正後 | 区分 |
|---|---|---|---|---|---|---|
| N1 | N1-er066a-028 | 三日間 | 三日目 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-er066b-020 | 三日目 | 3日間 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-er066b-022 | 三日目 | 三日間 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-prodbug-006 | 3~5日待つ | 35日待つ | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-prodbug-007 | 3～5日待つ | 35日待つ | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-new-042 | 一分待つ | いちふん待つ | PASS (PHONETIC_MATCH) | NG_SECONDARY_UNAVAILABLE / secondary_unavailable | 既知負例 |
| N1 | N1-new-044 | 三日待った | さんにち待った | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| N1 | N1-new-057 | 三日間の猶予 | 三日目の猶予 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| MOON | japanese_title_attempt3_minimalfallback.wav#2 | 月のしわ、8,900本超！その奥に潜む「岩の上着」の | 月のシワ、8000九百本超。その奥に潜む岩の上着の秘 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 月題実転写 |
| N3 | N3-02 | 月のしわ、8,900本超 | 月野氏は八万九千本町。 | PASS (PHONETIC_MATCH) | NG_PROTECTED / final_gate_value_diff | 既知負例 |
| POS | pos-022 | 三日間の旅 | みっかかんの旅 | PASS (PHONETIC_MATCH) | PASS_WITH_WARNING / primary_pass | 正例対照 |
| POS | pos-024 | 四月に会う | しがつに会う | PASS (PHONETIC_MATCH) | PASS_WITH_WARNING / primary_pass | 正例対照 |
| POS | pos-032 | 七月に行く | しちがつに行く | PASS (PHONETIC_MATCH) | PASS_WITH_WARNING / primary_pass | 正例対照 |
- 月題実転写1件(`japanese_title_attempt3…wav#2`、転写`8000九百本超`)は事前登録の既知負例9件に含まれない追加の発見(現行Productionで`READING_MATCH`のPASS=値が8,900と異なる転写を通していた)。
- F2警告追加3件(pos-022/024/032): 正しい不規則読みを『かな書き』したASR転写(`みっかかん`/`しがつ`/`しちがつ`)。値は同一でPASS。非ブロッキング警告(試聴リスト)が付く。不要ならF2の警告付与(1行)を外す案(この3件は現行と同一のPASSに戻る見込み。未検証)=Fable判断。
## 3. F1/F2の版履歴(開示)
| 版 | 結果 |
|---|---|
| F1+F2 v1(閉集合{番,度}書換え、`proto_value_gate_fix_01.py`、`open517_api0_eval_01.out.json`) | 基準1不合格(正例対照6件を誤NG化)。P4の`いちばん`は解消 |
| F2 v2(期待読み表の汎用規則、`proto_value_gate_fix_02.py`、`open517_api0_eval_02.out.json`) | 基準1・2合格。基準3で副作用: 警告喪失8件・Primary NGのP1解除6件 |
| F2 v3(警告保全+適用範囲限定、`proto_value_gate_fix_03.py`、`open517_api0_eval_03.out.json`) | 基準1〜5合格。**最終** |
同一コーパスで不合格を見てから再設計した点が限界(未知データの汎化は未確認)。
## 4. 取りこぼし(是正後もPASSする現行READING_MATCH PASS 163件の内訳)
P4実attempt 133(正常)・正例対照10・P3 NG pool再評価6・月題1・N1 11・N3 2。N1/N3の11+2件は全て値ガードで原理的に検出不能な既存誤PASS型: 同形異音(今日/市場/一日/上手)+数 7、助詞誤読(月は/町へ)3、同音異義`七晩`↔`七番`(`晩`が助数詞表に無くUNKNOWN素通し)1、N3-07(Candidate E近音`しわ`→`すわ`)、N3-24(町へ→待ちへ)。これらはOPEN-517の範囲外(ASRの限界O3・OPEN-333)。
## 5. 結論
事前登録基準1〜5を全て満たす → **是正案(F1+F2 v3)=API 0検証PASS(DEV/proto)**。Production適用はOpus軽量レビュー+ユーザー報告後。Candidate E(N3-07)は別件(OPEN-333)。
