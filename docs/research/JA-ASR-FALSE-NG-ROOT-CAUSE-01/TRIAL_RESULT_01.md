# TRIAL_RESULT_01(JA-ASR-FALSE-NG-ROOT-CAUSE-01 Phase 3 結果、2026-10-25、ユーザー閲覧用)
## 原因
月題の誤NGは「ASRが数詞を崩す(8000句800/8000900/千九百)」「`しわ`を`詩/死/氏`等の同音異字で書く」の組合せ。Productionは(1)値ガードがDIFFで止める (2)読み一致の救済は`8,900`のような値表記差を通さない、が重なって正常音声をNGにしていた。今回の実測で、**OpenAIの数詞崩れは同一音声でも時点で変わる(attempt2は保存時`八千九百`、今回`千九百`×3)**=ASR側の揺らぎで、Production側の判定規則だけでは安定して直せないことが分かった。Azureは同じ音声で`8900`と値を正しく転写する(attempt1/3とも)。
## 対策
案A(Primary層で「値atom化後に読み一致」なら`JA_PRON_VALUE_EQUIVALENT_MATCH`でPASS_WITH_WARNING)+A4(a)(Secondaryの値のみ一致=仕様L2865の是正)。prototype v1(凍結)。Production変更0・新flag 0。
## 検証(実API、実費約5.6円/保守側29.65円、Cap60円内)
- 増分誤PASS: 案A(Primary)は N-1 150+N-3 30 で**0**。A4(a)込みで N-3 の**1件(N3-21 `三日待った`→音声`さんにち`、Azure `3日`が値のみ一致で通る。警告付き)**=事前登録基準(0)不合格。
- 非回帰: 回帰0(P-4 421 + 新規転写)。
- 月題: 12転写中、案Aの救済は1件のみ(attempt3の1回)。attempt2は今回の転写で値が欠落、attempt1は`月野詩`で読み不一致。**月題の安定解消にはならない**(誤NG解消には数詞転写の安定化=Azure併用等が別途必要=B-light保留)。
- Melos preview(推定正例): 案AでPASS_WITH_WARNING(`三日目`は不規則読み警告付き)。Azureも`3日目`で一致。試聴確認はPhase 4前に依頼。
- N-3 30 clip: 型別機構は想定通り(値違い/助数詞違い/否定/へ→に/近音はNG維持)。**既存の誤PASS16件を新発見**: 特に`PHONETIC_MATCH`が値ガード・近音を見ず、値10倍違い(89,000)や`しわ→すわ`までPASSする(OPEN-517と同系統、本案と無関係の既存盲点)。
- O1(書式prompt/gpt-4o-transcribe): 誤NG減少効果なし(n=6、採用提案なし)。
## QCD
Q: 案Aの安全性は0/180(N-1+N-3)だが、A4(a)側1件で基準未達。効果(誤NG削減)は想定より狭い。C: API追加0、量産単価影響±0.01円/セット未満。D: 実行は約1.5時間(TTS 35分が律速)。
## Fable・Opus評価
**Fable(2026-10-25 委任_04転記)**
- 原因: 月題の誤NGは「ASR数詞崩れ(転写ごとに変わる)×同音異字(しわ→詩/死/氏)」の重なりで、Production側の正規化規則だけでは安定して直せないことが実測で確認された(Sonnet所見に同意)。Azureは値を正しく転写するが読みが合わず、既存仕様ではSecondaryの値一致だけで救済できない(R4)。
- 対策の評価: 案A(Primary層の値atom化+読み一致)は安全側(増分誤PASS 0/180、回帰0)だが、救済効果は月題12転写中1件にとどまり、月題の誤NGを安定解消する効果は未確認。A4(a)(Secondary値のみ一致)はN3-21「三日/さんにち」で増分誤PASS 1件=事前登録§1により**v1は不合格**。O1(書式prompt)・gpt-4o-transcribe切替は効果なし(採用提案しない)。
- Status: **v1=REJECTED(事前登録写像どおり。再凍結して再評価)**。案A Primary層のみは「安全性はVALIDATED(限定)・効果は限定的」と記録。Phase 4(Production適用)は提案段階にない。
- 重要な副次発見(Fable所見): N-3で既存Productionの誤PASS 16/30件が実音声で確認された。特にN3-02(音声89,000 vs 原稿8,900が`PHONETIC_MATCH`でPASS=値が10倍違うのに通る)とN3-07(しわ→すわがPASS)は、承認済み安全条件(CURRENT_SPEC/SCG「値・否定の最終確認」)との矛盾であり、本Trialの範囲外だが**優先度の高い不具合**としてOPEN-517で是正へ進める。
- 次の一手(Fable判断): v2=A4(a)から不規則読み値(三日・二十歳・一日・二日・七日等の数詞の特殊読み)を除外する厳格化。保存済み転写でAPI 0再評価。Melos「三日目」(Primary側PASS_WITH_WARNING)への副作用とN-3再評価を確認。
- ユーザー判断事項(27-3 D、後述の報告で提示): 月題の数詞崩れの安定解消にはB-light(Azure値+読み等価)やAzure併用が必要=UDR #136に関わる。Phase 4採用はv2が事前登録を満たしてから。
## Status
v1は**VALIDATED不可**(事前登録§1: 増分誤PASS 1件→v2再凍結→再評価)。案A(Primary)単体は誤PASS0・回帰0。最終Statusは Fable。
**委任_04追記**: Fable評価転記済み(上記)。v1=REJECTED。v2(`proto_reading_compare_02.py`)のAPI 0再評価結果=`EVAL_03.md`(Status候補=事前登録写像でVALIDATED(限定)候補、最終はFable)。
## 判断
- 判断候補(分類B 承認範囲内): v2(A4(a)から不規則読み値を除外=厳格化、API 0で既存転写を再評価可)を次委任で実施。
- 判断候補(分類D 新規): Phase 4=Production適用は事前登録が満たされてから。月題の数詞崩れ解消にはB-light/Azure併用(UDR #136に触れる)=ユーザー判断。
- 別OPEN: OPEN-517(PHONETIC_MATCHの値ガードskip)に本件N3-02/N3-07を追記。
詳細: `EVAL_02.md`・`BUDGET_LOG_01.md`・`eval_phase3_02.out.json`。
