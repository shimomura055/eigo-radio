レビュー日: 2026-10-25 / レビュー者モデル: claude-opus-5-5
Fable採否: 必須M1〜M7=全採用、推奨R1〜R7=採用、任意O1=採用(約1円、採用判断は別)、O2=採用(記録のみ)、O3=採用(記録)。全体判定「必須修正反映後にPhase 3へ」に従う。Cap=60円(Fable自律範囲)。

# OPUS_REVIEW_01(JA-ASR-FALSE-NG-ROOT-CAUSE-01 / 条件A 独立技術レビュー / 読み取り専用・API 0)

レビュー者: Opus(claude-opus-5-5)。対象: `ROOT_CAUSE_01.md`、`DESIGN_01.md`、`PREREGISTERED_CRITERIA_01.md`、`BUDGET_PLAN_01.md`、`proto_reading_compare_01.py`(v0)、再現出力3件、実装(`er007_ja_asr_validator_01.py:333-505`、`er007_ja_secondary_asr_01.py:83,427,494-660`、`er078_asr_unified_judge_01.py:60-84,505-582`、`er078_asr_value_guard_01.py:48,208-220,376-450`)、`CURRENT_SPEC.md` L2179/L2852-2867。
Production採用の可否は判断しない(人間ユーザーのみが判断する)。

## 全体判定
**必須修正を反映すればPhase 3へ進んでよい(設計の全面見直しは不要)。**
原因分析R1〜R4は、コードと再現結果に照らして妥当。案Aの骨格(値atom化+残り発音一致+値ガードEQUAL必須)も筋が良い。ただし次の3点は、Phase 3の結果の意味を変えるか、承認境界に関わるため、凍結前の是正が必須。
(1) 凍結済みプロトタイプv0が、設計書で「維持する」と書いた除外(C2同形異音・A7登録読み・P1保護差)を実装していない。
(2) 案A4(b)(Secondary転写での発音一致による受理)は不具合是正ではない。2026-10-11承認時に**明示的に未採用とされた安全条件**にあたる。
(3) 誤PASS基準「0/136」の測り方が、現行の誤PASS(ASRの既存盲点)と、新しい層が増やす誤PASSを区別していない。

## 観点1 案Aの誤PASS経路 — 修正推奨(一部は必須)
前提: 発音一致が成り立つ転写は、ASRから見れば「同じ音」と言える。新たな誤PASSが生じうるのは、主に次の3つ。(a) 読みエンジンが、ASR出力の漢字に「ASRが実際に聞いた読み」とは別の読みを与える場合。(b) 値atom化によって、数詞・助数詞の読みが比較対象から消える場合。(c) 既存の除外・保護を迂回する場合。
| 経路 | 現行でも同じ盲点か / 案Aで新たに開くか | 判定・防止策 |
|---|---|---|
| 同形異音(今日 きょう/こんにち、市場、一日、上手、人気、行った) | 数値を含まない文では現行PHONETIC_MATCHも同じ盲点。**数値を含む文では新たに開く** | 反例: canonical`3人できょう話した` / ASR`三人で今日話した`(実音声「こんにち」)→ v0はPASSする。**必須M1**: A3経路でも`_scg_heterophone_candidate`(C2、`reading_is_candidate`)を適用し、該当spanがあれば救済しない |
| 登録読み(expected_readings)の迂回 | **新たに開く**。v0は`expected_readings`を受け取らず`reading_dictionary_mismatch`も見ていない | **必須M1**: A7の差分が1つでもあれば救済しない(L2856) |
| 数字差があるのに値ガードがNO_VALUES/UNKNOWN | **新たに開く**。v0はNO_VALUESでも通す。A3がPrimaryを先にPASSさせると`protected_diff`のsignals計算が飛ぶ | **必須M3**: `number_mismatches`が空でないときは値ガードEQUALのみ許可。NO_VALUESは数字差が無いTCMの場合だけ |
| 数詞の不規則読み(三日、一人、二十歳) | 既存の値等価層と同じ残余リスク | 既存警告`WARN_IRREGULAR_READING`がA3経路でもPASS_WITH_WARNINGとして残ることをtestで固定(推奨R2) |
| 助数詞の連濁誤読(三本 さんほん等) | 既存の盲点 | 負例に含める |
| 助詞へ→エ/は→ワ | 新たに開く範囲は「原稿側が非助詞のワ/エ音語で、実音声がha/he、ASRが助詞は/へ」に限られる | 負例に数件。現行PHONETIC経路は助詞「は」をhaと読むためTTSが「月は」をtsuki-haと誤読しASRが`月派`と書いた場合でも現行はPASS(既存盲点、任意O3) |
| 長音・促音・拗音・送り仮名(超/超え) | v0は厳格 | 問題なし。超/超えの表は入れない(推奨R7) |
| 読みエンジン差(pykakasi vs unidic) | **新たに開く** | 推奨R4: flipを原因別(A1/A2/合成/エンジン差)に集計、エンジン差flipは個別に正当化 |
設計書の誤PASS表は、新たに開く3経路(C2・A7・NO_VALUES)が抜けている。

## 観点2 値ガード・P1・v4/J2との整合 — 修正推奨(1点は必須)
- 値ガードEQUAL必須化、否定差ガード、AMBIGUOUS/UNKNOWN対象外、範囲値(J2)対象外はP1と矛盾しない。v4・J2はWriter段で判定経路と干渉しない。**P1の値DIFF即NGは維持**。
- **必須M2**: adapterは分類`PHONETIC_MATCH`なら`basis="READING_MATCH"`を付け(`er007_ja_secondary_asr_01.py:427,603`)、承認済み根拠として最終ANDゲートがskipされる(`er078:526-530`)。新しい分類名(例`JA_PRON_VALUE_EQUIVALENT_MATCH`)を使い`_READING_MATCH_CLASSIFICATIONS`に入れない。「最終ゲートapplied=True」testを追加。
- 推奨R3: `extract_atoms_ja`が桁区切りを正しくatom化するなら、A1(カンマstrip)は不要かもしれない。adversarial panelの`売上は1,200円です`のNGがclassifyのみか値等価層込みかを確認。残す場合は値ガード入力にも同じstrip。
- 推奨R5(別OPEN): panel L8 `三日間の猶予`/`三日目の猶予`(内容が違う負例)が現行で`PHONETIC_MATCH`=PASS、かつREADING_MATCHは最終値ゲートをskip。別管理IDとして登録(本タスクで直さない)。

## 観点3 案B-light — 重大(現時点ではユーザーへ提示しない)
- 誤PASS機序: TTSが数字を誤読しPrimaryは正しく書いたがAzureが偶然原稿の値を書く場合。Azureの言語モデル補完の危険。Phase 3の10〜12件では有意な上限を出せない。
- KP3V(3票目Whisper要求)より弱い。承認済みP1の意味変更。この強度では推奨できない。
- 効果小(P1発火は1,217件中2件、月題は案Aだけで回避)。A-1実測(約0.6円)は情報取得のみ、`B-light 保留`と記録。再検討時はKP3Vと同等の強度で設計し直す(Whisper第3票はUDR #136・SCG未採用条件L2179に触れユーザー判断)。
- ローカルWhisper第3票の除外は妥当。

## 観点4 別方式 — 概ね問題なし
- Azure primary化: UDR #136で判断済み、再提案しない。Azure単独判定は副次データとして記録(任意O2)。
- 位取り復号: 却下に同意。辞書読み照合: A2が実質それ。
- 原稿prompt投入の却下は妥当。ただし**原稿内容を含まない汎用書式指示**(「数字は算用数字で」)や`gpt-4o-transcribe`でのJA数詞整形安定性は約1円で並置計測の価値(任意O1、採用はユーザー判断、使用モデルを記載)。

## 観点5 R4の扱い — A4(a)問題なし / A4(b)重大(分類の誤り)
- A4(a)(Secondary転写への値等価のみ)はL2865明記のため**不具合是正として妥当**(test: 三人/3人 mockが`PASS_WITH_WARNING`)。
- **必須M4**: A4(b)(Secondary転写での発音一致による受理、助詞読み含む)はSCG承認仕様L2179「未採用(安全条件): PHONETIC_MATCH自動PASS、助詞差・漢数字の追加除外、Whisper 2-of-3」とL2856「読みでの受理禁止」に該当。PASS_WITH_WARNINGでも承認済み安全条件の変更。**新仕様の候補(ユーザー判断)**と明記。Phase 3ではDEVで評価してよいが指標は(a)と分ける。
- Primary側A3は承認済み2機構の組合せとして説明できるが、「助詞差」が2026-10-11未採用リストに含まれるため、採否提示で明示開示。

## 観点6 Phase 3の評価設計 — 重大(必須2点)
- **必須M5**: 誤PASS基準を2本に分ける。1.**増分誤PASS**=負例のうち「現行NG・案APASS(含WARNING)」=**0件**(合否)。2.**既存誤PASS**=現行でもPASSする負例=報告のみ(必要なら別OPEN)。
- **必須M6**: N-3は「原稿は正しい漢字、TTS入力だけ誤読のかな」で次を追加: 同形異音(今日→こんにち、市場→しじょう、行った→おこなった、一日→いちにち/ついたち 各1〜2)/数値を含む文での同形異音(`3人できょう…`型、M1検証用)3/助数詞の連濁・音便(三本→さんほん、一分→いちふん、六百→ろくひゃく)3/不規則読み(三日→さんにち、二十歳→にじゅっさい)2/助詞の誤読(「月は」→つきハ、「町へ」→まちヘ)2〜4/非助詞わ/え語×助詞読み 2。既存16 clipは半数程度に減らしてよい。全体約30 clip。
- rule of three: 母集団全体の上限のみ。N-3は型ごとの機構testとして扱うと事前登録に明記。
- N-2のflipは試聴確認で妥当。P-1 attempt1の`超え`は実音声が「こえ」の可能性、発音一致層で救えないのは正しい挙動として事前登録。
- P-3 flip全件の個別審査は妥当。R4の原因別集計を追加。
- 凍結: v0にM1〜M3が欠けている。評価開始前・N-3作成前なので**v1として修正・再凍結すれば逸脱ではない**。**必須M7**: 評価対象コードと配線予定コードを同一に(v0 `value_form`は「atomが無いと原文」、Production `_ja_value_form`は「None」等の差)。trial moduleを配線候補コードそのものにするかparity test。

## 観点7 X/Z共通化と配線形 — 修正推奨
- 判定経路はX/Z/A/B/C共有(`er078`)。新scope機構は作らず、既存`er109_xz_scope_01.is_active_for_run()`+単一flag読取関数(既定OFF)を再利用。全JAへの拡大は採用時判断。
- 配線時test(推奨R6): HR Lock済みsegmentが新判定で自動解除されない/reuse・resume・継承で新ラベルが読める・旧readerが壊れない/試聴リスト再導出で新warning(`JA_PRON_EQUIVALENT`、`JA_NUMERIC_IRREGULAR_READING`)が拾われる/flag OFFで従来挙動。
- SecondaryCacheキー、retry3回、fallback、Master Audio Storeキーは影響なし。
- 推奨R2: Primary側A3救済にも非ブロッキングwarning`JA_PRON_EQUIVALENT`を付け試聴リスト対象に。

## 観点8 費用・単価 — 問題なし
- 案Aの追加API 0は正しい。M6でN-3約30 clipに増やすと+約10〜20円、中央値約30〜35円。Cap 60円を提案。量産単価70円への影響±0.01円未満。

## 修正一覧
### 必須(Phase 3開始前。v1として再凍結)
- M1: A3経路(Primary・Secondaryとも)でC2同形異音候補とA7登録読み不一致が1つでもあれば救済しない。`expected_readings`も渡す。
- M2: 新しい分類名を使い、READING_MATCH根拠にしない。最終ANDゲート適用をtestで固定。
- M3: `number_mismatches`があるときは値ガードEQUALのみ許可。`protected_diff`を迂回しない。
- M4: A4(b)を「新仕様候補(ユーザー判断)」と再分類。A4(a)と指標を分ける。
- M5: 誤PASS基準を「増分誤PASS 0件(合否)」と「既存誤PASS(報告)」に分ける。
- M6: N-3にTTSの実際の誤読モードを追加。
- M7: 評価コードと配線予定コードを同一に(またはparity test)。
### 推奨
- R1: B-lightは保留、A-1の実測だけ。R2: 不規則読み警告の残存をtest固定、`JA_PRON_EQUIVALENT`警告。R3: A1の要否確認。R4: flipの原因別集計。R5: `三日間/三日目`のPHONETIC_MATCH PASSとREADING_MATCHの最終ゲートskipを別OPEN登録。R6: 配線形=er109_xz_scope再利用+既定OFF、HR Lock・reuse・試聴リスト・flag OFFのtest。R7: 超/超え表は入れない。
### 任意
- O1: 書式prompt/`gpt-4o-transcribe`のJA数詞安定性を約1円で並置計測。O2: Azure単独判定を副次データ記録。O3: 現行PHONETIC経路の助詞「は」=ha読み盲点を既知の制約として記録。

## 追加で事前登録すべき項目
1. v1の凍結shaとv0からの差分(M1〜M3)。2. 増分誤PASS・既存誤PASSの定義と集計表形式。3. N-3の型別件数・TTS入力文(かな誤読)・各型の「NGになるべき理由」。4. flipの原因別分類の定義。5. A4(a)/(b)の指標分離、B-lightは「情報取得のみ・提示判断保留」。6. 最終ANDゲート適用testと警告ラベル継承test。7. 到達上限VALIDATED、Production無変更、配線はユーザー正式採用後。
