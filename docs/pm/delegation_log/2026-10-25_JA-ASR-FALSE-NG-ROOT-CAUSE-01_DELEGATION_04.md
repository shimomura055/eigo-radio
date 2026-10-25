管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_04(Fable評価の転記+prototype v2再凍結+API 0再評価。**有料API 0・Production変更0**)。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{PREREGISTERED_CRITERIA_02,DESIGN_01,EVAL_01,EVAL_02,TRIAL_RESULT_01,OPUS_REVIEW_01}.md`、`proto_reading_compare_01.py`(v1 sha 8799aa60…凍結)、`eval_api0_v1_01.py`、`eval_phase3_02.py`、`phase3_run/usage_log.jsonl`(保存済み実転写)、`n3_clips_01.json`、OPEN-515/517。

## 1. Fable評価(逐語で`TRIAL_RESULT_01.md`の「Fable・Opus評価」欄と`EVAL_02.md`へ転記。「Fable(2026-10-25 委任_04転記)」と明記)
- 原因: 月題の誤NGは「ASR数詞崩れ(転写ごとに変わる)×同音異字(しわ→詩/死/氏)」の重なりで、Production側の正規化規則だけでは安定して直せないことが実測で確認された(Sonnet所見に同意)。Azureは値を正しく転写するが読みが合わず、既存仕様ではSecondaryの値一致だけで救済できない(R4)。
- 対策の評価: 案A(Primary層の値atom化+読み一致)は安全側(増分誤PASS 0/180、回帰0)だが、救済効果は月題12転写中1件にとどまり、月題の誤NGを安定解消する効果は未確認。A4(a)(Secondary値のみ一致)はN3-21「三日/さんにち」で増分誤PASS 1件=事前登録§1により**v1は不合格**。O1(書式prompt)・gpt-4o-transcribe切替は効果なし(採用提案しない)。
- Status: **v1=REJECTED(事前登録写像どおり。再凍結して再評価)**。案A Primary層のみは「安全性はVALIDATED(限定)・効果は限定的」と記録。Phase 4(Production適用)は提案段階にない。
- 重要な副次発見(Fable所見): N-3で既存Productionの誤PASS 16/30件が実音声で確認された。特にN3-02(音声89,000 vs 原稿8,900が`PHONETIC_MATCH`でPASS=値が10倍違うのに通る)とN3-07(しわ→すわがPASS)は、承認済み安全条件(CURRENT_SPEC/SCG「値・否定の最終確認」)との矛盾であり、本Trialの範囲外だが**優先度の高い不具合**としてOPEN-517で是正へ進める。
- 次の一手(Fable判断): v2=A4(a)から不規則読み値(三日・二十歳・一日・二日・七日等の数詞の特殊読み)を除外する厳格化。保存済み転写でAPI 0再評価。Melos「三日目」(Primary側PASS_WITH_WARNING)への副作用とN-3再評価を確認。
- ユーザー判断事項(27-3 D、後述の報告で提示): 月題の数詞崩れの安定解消にはB-light(Azure値+読み等価)やAzure併用が必要=UDR #136に関わる。Phase 4採用はv2が事前登録を満たしてから。

## 2. 作業
A. 上記転記。
B. `proto_reading_compare_02.py`(v2)を作成: v1からの差分は「A4(a)の値のみ一致PASS_WITH_WARNINGから、原稿側の値が不規則読み数詞(既存の不規則読み辞書/`JA_NUMERIC_IRREGULAR_READING`判定に該当)の場合を除外しNG維持」のみ。v1ファイルは変更しない(凍結)。v2 sha記録・再凍結。差分をunified diffで`DESIGN_02.md`(v1→v2差分・理由・事前登録§1の手順準拠)に記載。
C. API 0再評価`eval_api0_v2_01.py`: N-1 150+N-3 30の保存済み転写(`phase3_run/usage_log.jsonl`・EVAL_01の素材)で増分誤PASS・回帰(421件+Phase 3新規転写)・救済件数(月題12転写・Melos preview)を再計算。N3-21がNGに戻ること、Melos「三日目」の挙動変化の有無、他に失う救済がないかを表で示す。`PREREGISTERED_CRITERIA_03.md`(v2用。基準は02と同一、対象をv2へ)。`EVAL_03.md`。
D. OPEN-517: N3-02/N3-07等の既存誤PASS16件を「既存Productionの承認済み安全条件との矛盾(不具合)」として是正対象に整理(件数・型別・該当規則`PHONETIC_MATCH`の箇所・是正案の方向[値の最終確認を`PHONETIC_MATCH`より優先]・影響範囲・API 0で検証可能か)。**実装はしない**(別委任。ただし是正案はDESIGN_02に章として書く)。OPEN-515更新(v1 REJECTED→v2)。直前再Read・最小Edit・バックアップ(他agent並行編集中)。
E. test(API 0、`py`): v2のunit test(v1 testを継承+除外規則)、`eval_api0_v2_01.py`の決定論性。
F. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
G. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_04.md`(Nは585前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_04」を580〜610で走査)。

## 禁止
有料API 0。Production code(ASR cascade・normalize_ja・Variant Layer・`PHONETIC_MATCH`規則・閾値・Prompt)の変更禁止。v1変更禁止。B-light/Azure併用の実装禁止(ユーザー判断)。

## 報告(RESULT_PACKET_JAASR4.md+口頭要約)
v2差分、再評価結果(増分誤PASS/回帰/救済件数/Melos副作用)、v2のStatus候補(事前登録写像)、OPEN-517是正案の要点(件数・方向・検証方法・見積)、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。