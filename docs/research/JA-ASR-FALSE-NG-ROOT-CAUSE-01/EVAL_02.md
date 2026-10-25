# EVAL_02(Phase 3 有料検証の評価、委任_03、2026-10-25)
評価対象=プロトタイプ v1(凍結。sha256 `8799aa60fed66e2d78eea00bb263e99ebf069db83c6fe1d3191d1d96870c1733`、実行前後で不変を確認)。事前登録=`PREREGISTERED_CRITERIA_02.md`。評価は`eval_phase3_02.py`(API 0・LLM不使用・socket guard。再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_phase3_02.py`)。生データ=`phase3_run/usage_log.jsonl`(転写)・`eval_phase3_02.out.json`(判定全件)。
使用モデル: ASR=OpenAI `gpt-4o-mini-transcribe`(Production Primary、比較基準のため最新でない旧世代を使う例外)+Azure ja-JP(Production Secondary)/O1のみ`gpt-4o-transcribe`(最新世代)/TTS=Production JA Std経路(`gemini-3.8-flash-lite`系、batches.create)。判定は決定的ルール(LLM判定なし)。
判定の定義: base=現行Production判定、v1=案A(Primary層差替え)+A4(a)(Secondary値のみ一致)、v1+A4(b)=さらに発音一致も(新仕様候補)。

## 1. 事前登録の主要指標
| 指標 | 結果 | 基準 | 判定 |
|---|---|---|---|
| 増分誤PASS(N-3 30 clip、案A=Primary層のみ) | **0** | 0 | 合格 |
| 増分誤PASS(N-3、A4(a)=Secondary値のみ一致を含む) | **1(N3-21)** | 0 | **不合格(事前登録§1: 1件でも出たら不合格→v2再凍結→再評価)** |
| 増分誤PASS(N-1 150、API 0、EVAL_01) | 0 | 0 | 合格 |
| 非回帰(P-4 421ユニーク) | 回帰0(EVAL_01) | 0 | 合格 |
| 非回帰(今回の新規転写でのbase PASS→v1 NG) | 0(月題A2 9本・N-3 30 clip・O1 6本) | 0 | 合格 |
| 既存誤PASS(報告のみ) | N-3で16/30(下記§3) | 報告 | 報告 |
| 最終ANDゲート/警告継承 | v1経路で`JA_PRON_EQUIVALENT`/`JA_NUMERIC_IRREGULAR_READING`が付与(Melos preview・N3-21) | 維持 | 合格 |
→ 厳密適用では**合格基準1が不合格(1/30、A4(a)側)**。Primary側の案Aは0/30で合格。事前登録は厳格化可・緩和禁止のため、A4(a)の1件を「構造的同一」等で除外しない。

### N3-21の詳細(増分誤PASS)
原稿`三日待った`(正しい読み=みっか)、TTS入力`さんにち待った`→音声は誤読。Primary=`三日間待った。`(NG: 間が混入)、Azure=`3日待った。`。base=NG。v1=A4(a)(Azure `3日`が値のみ一致、kind=VALUE_ONLY、cause=A1_value_notation)で**PASS_WITH_WARNING(`JA_NUMERIC_IRREGULAR_READING`)**。機序=ASR転写(漢数字/算用数字)からは読み(みっか/さんにち)を判別できない**既存の盲点**(N-1の`三日→さんにち`既存誤PASS、N3-22 `二十歳→20歳`のPrimary既存PASSと同型)がSecondary側の表記違いにまで及んだ。Productionは警告付与+事後試聴リスト対象で、PASSは「試聴リスト送り」の扱い。
v2案(厳格化方向・API 0で再評価可): A4(a)で`JA_NUMERIC_IRREGULAR_READING`該当の値(三日・二十歳・一日等の不規則読み語)は救済しない。月題・Melosの正例には不規則読み警告が付かない場合は影響無し(Melos previewは`三日目`でPrimary側案Aが救済しており警告付きのため要扱い判断)。**v1凍結につき今回は変更せず、Fable判断**。

## 2. 月題・Melos(実API)
| 項目 | 転写 | base | v1 | 備考 |
|---|---|---|---|---|
| A1 Azure attempt1 | 月野市は8900本越え | NG | NG | 値は8900で正しい(OpenAIは8000句800/8000900と崩れた)。読み`月野市`≠`月のしわ`で発音不一致。B-light保留のため救済せず |
| A1 Azure attempt3 | 杉野氏は8900本超 | NG | NG | 同上 |
| A3 Azure attempt2 | 月の詩は8900本超 | NG | NG(A4(a))/PASS(A4(b)のみ) | Primary側で案Aが通るので不要。A4(b)=新仕様候補 |
| A2 attempt1 OpenAI×3 | 月野詩は8,900本超え×2/好きの詩は8000900本超え | NG | NG | 値は8,900でも`月野詩`≠`月のしわ`(TRUE_CONTENT_MISMATCH)。**案Aでも救えない**(読み`つきのうたは`≠`つきのしわ`) |
| A2 attempt2 OpenAI×3 | 月の島は千九百本超 ×3 | NG | NG | **今回は3/3とも`千九百`(八が欠落)**。保存時の転写は`八千九百`でPASS。同一音声でも転写が時点で変わる(ASR再現性なし) |
| A2 attempt3 OpenAI×3 | 月野氏は八千九百本超/月の詩は八千九百本長/月のシワ、8000九百本超 | NG/PASS/PASS | **PASS/PASS/PASS** | 案Aで1/3救済(`JA_PRON_VALUE_EQUIVALENT_MATCH`)。他2は現行でもPHONETIC_MATCHで通る |
| A3 Melos preview Azure | 3日目…道をふさぐ | (Primary 3日目はbaseでNG_SECONDARY_UNAVAILABLE) | Primary案AでPASS_WITH_WARNING(`JA_NUMERIC_IRREGULAR_READING`+`JA_PRON_EQUIVALENT`) | **Azure転写も`3日目`/`ふさぐ`で原稿`三日目`と読み・値一致**。Secondary単体のA4(a)は不受理(理由は未調査。Primary案Aで通るため影響なし)。推定正例の裏付け。試聴素材=`er0*`のMelos previewのattempt2 wav(後述パス) |
集計: 月題12転写(A2 9+A1 2+A3 1)のうち案A(Primary)で救済=**1件(attempt3#0)**。attempt2は今回の転写では値が欠落して救えず、attempt1は読み不一致。**案Aの効果は「月題の誤NGを安定して解消する」ものではなく、「Primaryが漢数字を書き読みが同音のときの救済」に限定される**(EVAL_01の想定より狭い)。OpenAIの数詞崩れ(8000句800、8000900、千九百)はASR側の揺らぎで、案Aでは救えない。
## 3. N-3 30 clip(実TTS→実ASR OpenAI+Azure)
- 増分誤PASS: 案A(Primary)0 / A4(a)込み1(N3-21)/ A4(b)込みでも1。誤PASSの新規型は無し。
- 既存誤PASS(現行でも通る、v1と無関係)16件: 桁違い`89,000`(N3-02、`PHONETIC_MATCH`で値ゲートskip)、`しわ→すわ`(N3-07、同)、同形異音(今日/市場/行った/一日/人気)、連濁(三本/六百)、`二十歳`、助詞(月は/町へ/私は)、N3-26/27。**N3-02(値が10倍違うのにPASS)・N3-07は`PHONETIC_MATCH`が値ゲート・近音を見ない既存不具合**(OPEN-517と同系統・重要)。
- N3-26/27の物理的前提確認: N3-26の音声はAzureが`月のしわが多い`と転写=TTSは`は`をwaで読んだ可能性が高い(OpenAIは`手話`)。N3-27はAzureが`屁を書く`=`へ`と読んだ可能性(原稿`絵を描く`と別語。**しかしOpenAIが`絵を描く`と原稿一致で転写→現行PASS**)。いずれも現行で通る既存の盲点で、v1の増分ではない。
- 型別: 値違い(N3-01)/助数詞違い(05,29)/否定反転(06,28)/へ→に(04)/一分→粉末(19)/長音差(30)/近音しば(08)/わ脱落(03)はv1もNG維持(正しい)。
## 4. O1(数値フォーマットPrompt、月題3 wav)
汎用書式prompt(`数字は算用数字で書いてください。`)付きmini: attempt1 `8,900`(promptなしA2でも既に8,900が2/3)、attempt2 `千九百`(改善なし)、attempt3 `800年本朝`(悪化)。`gpt-4o-transcribe`: attempt1 8,900/attempt2 八千九百(値は正)/attempt3 8000900(崩れ)。どれも読み部分(`月の枝`・`隙の師`・`杉の枝`)が原稿`月のしわ`と不一致でNG。**O1は誤NGを減らす効果なし**(n=6、探索的。採用提案しない)。ASRの数詞崩れは書式promptでは安定化しない。
## 5. 結論(機械的写像)
- 合格基準1(増分誤PASS 0): A4(a)込みで1/30 → 不合格。基準2(非回帰)合格・基準3(誤NG削減)は限定的(月題で安定救済できない)・基準4合格・基準6(費用)合格。
- Status候補: **v1はVALIDATED不可**。事前登録§1に従い「原因修正→v2再凍結→再評価」(案: A4(a)から不規則読み値を除外、または案A(Primary層)のみに範囲を絞る)。案A(Primary)単体はN-1 150+N-3 30で増分誤PASS 0・回帰0だが、効果は月題で限定的。
- 最終Statusは Fable。
## 6. 試聴素材
Melos preview attempt2 wav(推定正例の確認用): `er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_e2e_01/a2/narration/attempts/preview_attempt2_custom99dc82e9.wav`(リポジトリ内ローカルpath。公開不要)。N-3の誤読wav 30本=`phase3_run/n3/N3-*.wav`(ローカルのみ・不追跡)。

## 7. Fable評価(2026-10-25 委任_04転記。逐語)
**Fable(2026-10-25 委任_04転記)**
- 原因: 月題の誤NGは「ASR数詞崩れ(転写ごとに変わる)×同音異字(しわ→詩/死/氏)」の重なりで、Production側の正規化規則だけでは安定して直せないことが実測で確認された(Sonnet所見に同意)。Azureは値を正しく転写するが読みが合わず、既存仕様ではSecondaryの値一致だけで救済できない(R4)。
- 対策の評価: 案A(Primary層の値atom化+読み一致)は安全側(増分誤PASS 0/180、回帰0)だが、救済効果は月題12転写中1件にとどまり、月題の誤NGを安定解消する効果は未確認。A4(a)(Secondary値のみ一致)はN3-21「三日/さんにち」で増分誤PASS 1件=事前登録§1により**v1は不合格**。O1(書式prompt)・gpt-4o-transcribe切替は効果なし(採用提案しない)。
- Status: **v1=REJECTED(事前登録写像どおり。再凍結して再評価)**。案A Primary層のみは「安全性はVALIDATED(限定)・効果は限定的」と記録。Phase 4(Production適用)は提案段階にない。
- 重要な副次発見(Fable所見): N-3で既存Productionの誤PASS 16/30件が実音声で確認された。特にN3-02(音声89,000 vs 原稿8,900が`PHONETIC_MATCH`でPASS=値が10倍違うのに通る)とN3-07(しわ→すわがPASS)は、承認済み安全条件(CURRENT_SPEC/SCG「値・否定の最終確認」)との矛盾であり、本Trialの範囲外だが**優先度の高い不具合**としてOPEN-517で是正へ進める。
- 次の一手(Fable判断): v2=A4(a)から不規則読み値(三日・二十歳・一日・二日・七日等の数詞の特殊読み)を除外する厳格化。保存済み転写でAPI 0再評価。Melos「三日目」(Primary側PASS_WITH_WARNING)への副作用とN-3再評価を確認。
- ユーザー判断事項(27-3 D、後述の報告で提示): 月題の数詞崩れの安定解消にはB-light(Azure値+読み等価)やAzure併用が必要=UDR #136に関わる。Phase 4採用はv2が事前登録を満たしてから。

v2再評価=`EVAL_03.md`。
