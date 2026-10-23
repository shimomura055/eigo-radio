# TRIAL_DESIGN_05: 課題① 字義訳の根本対策 Trial設計(案A=解釈先行+字義像判定 / 案B=文脈限定句の置換のみ / 参照=Cp)(委任_21、2026-10-24、API 0・設計のみ)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21 / 対策案=`DESIGN_07.md` / 原因=`ROOT_CAUSE_04.md` / 台帳(既存)=`TRIAL_04/BUDGET_LOG_01.md`・`TRIAL_04/POSS_REP2_01.md`
状態: 設計のみ(本委任では有料runを実行しない)。実装・実行は次委任(DEV/Trial専用、er112系)。使用モデル: 生成=gpt-6-luna(Production系列と同一=比較のため最新最上位ではない。25節の例外理由=評価対象がluna生成の品質そのもの、Trial_04と同じ)。判定=**Fable盲検**(API 0)。Sonnet参考Judge(1call約2.0円・Fableと乖離83/360セル)は**使わない**。

## 0. Trialの問いと最小構成

| 問い | arm | 何を分離するか |
|---|---|---|
| Q1 文脈限定句の置換だけで字義訳は減るか(H5) | **X1**(案B: M-base+制約句置換、schema変更なし) | 制約句の寄与 |
| Q2 解釈先行+字義像判定の欄を足すと更に減るか(H3/H4/H10)、通常表現は悪化しないか | **X2**(案A: X1+`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`→gloss) | 欄の寄与(X2−X1) |
| Q3 既存の最良実測(Cp)は再現するか | **Cp**(Trial_04既存、1 repの実測を参照。再実行は予算次第) | 既存最良との比較 |
| 対照 | **B0**(現行。**新規rep**。選択バイアスを避けるため既存2repは推定に使わない) | 現行 |

最小Trial = 2段(Stage 1で有効性の有無を安価に判定→Stage 2で通常表現の非劣化を確認)。Stage 1の結果で Stage 2の要否・対象を決める(憲章2: 不要な実行をしない)。

## 1. 比較対象セット(事前定義。出力を見る前に固定、結果に依らない)

層別の定義は`TRIAL_04/strata_04.json`(F層=比喩・慣用で字義読みが文法的に成立、N層=用語・コロケーション・句動詞等、N標本seed=11)をそのまま再利用し、新規生成を最小化する(`trial05_plan_counts.json`)。

| セット | 内容 | KP数 | call数(article単位、本番と同じ最大3KP/call相当) |
|---|---|---|---|
| **R(hard-core)** | 既知の字義訳NG 4KP: `draw a line`・`an unseen clock`・`question shaped like a trophy`・`greener grass`(Trial_02〜04のFable/gold確定でFAIL_LITが1出力以上出たKPの全数) | 4 | 同記事のco-KP(`come down`,`behind the scenes`,`sound no one asked for`)を含め **4 call/rep**(7KP) |
| **S(非対象)** | strata_04のtrial_setからRとco-KPを除く: F層35+N標本19(正常例=通常表現の非劣化確認) | 54 | **28 call** |
| co-KP(3) | Stage 1で同時に生成される非対象KP | 3 | (R callに含む) |

Rの注意: Rは『G0/B0でNGが出たために選ばれた』事後層別。そのためG0/B0の既存率(8/11)は過大評価で、**効果の判定には新規repの対照(B0)を使う**。Sは結果に依らない事前層別(Trial_04)。

## 2. 実施手順と測り方

### Stage 1(R、有効性。3 rep)
- arm: B0(新規3rep)・X1(3rep)・X2(3rep)。計 (4 call×3rep)×3arm=36 call。出力数 R 12/arm+co-KP 9/arm。
- 事前宣言の判定(Fable盲検):
  - **M1(主)**: R 12出力のFAIL_LIT数。B0の期待≥4/12(未満なら『検出力不足/regression to the mean』と記録し、repを追加する判断を報告)。
  - **有効(X2)**: FAIL_LIT ≤1/12 かつ 語義誤認FAIL(trophy C/rep2型)がB0以下。**解消**: FAIL_LIT 0/12(Fisher: 6/12対0/12でp=0.005)。
  - **X1の判定**: X1が有効ならH5が主因として確定、**案B採用候補**(最安)。X1が無効でX2が有効なら欄が必要。両方無効なら§3の再計画。
  - **M2(診断)**: X2の`naive_ja_conveys`が、R 12出力で`no`または`partly`を返す割合(期待≥10/12)。`yes`が多ければ『確証バイアスで形骸化』と判定。
- 費用の安全装置: 最初にX2を1記事分(rep1)だけ実行して**実測単価を確認**(6〜10 call相当)、上限0.20円/call超ならSTOPして報告(Trial_04の見積り超過[1call実測が想定の2〜6倍]の再発防止)。cap検査は**発行前累計+その call の見込み**で判定、workers≤2。

### Stage 2(S+co-KP、通常表現の非劣化。1 rep)
- 条件: Stage 1でX2またはX1が有効の場合のみ実施(有効でなければ原因再検討へ。無駄な費用を使わない)。有効だった方のarm(両方なら X1とX2。予算内ならX2優先、X1は安価なので追加)。
- 対象: S 54KP+co-KP 3(=57KP)を28 call。
- 比較: B0は**既存Trial_04のB0 2rep**(同一KP・同条件)を対照に使える(Sは事前層別で選択バイアスなし)。
- **M3(非劣化、事前宣言)**: Fable盲検ラベルで、B0(2repの悪い方)に対しX2/X1が PASS→THIN/FAILとなったKP数 ≤2/57、かつ **PASS→FAIL=0**。基準の根拠=Trial_04のB0 rep1-rep2間のKP単位ラベル変化(`pump one's fist` PASS→THIN の1/61)+許容1。THIN率が増えた場合は種類(説明文化/含意欠落/範囲狭小)を分類して報告。
- **M4**: `naive_ja_conveys`の`no/partly`率(S)。期待≤15%。>30%なら過剰発火(説明文化リスク)として是正。
- **M5(費用)**: X2/X1/B0の実測 円/call、1記事(2call)換算。見込み: X2 +0.1〜+0.24円/記事、X1 −0.05円/記事。
- **M6(動作)**: parse失敗・欄欠落・attempt数・既存validate互換(括弧禁止・数字・人称整合)。fail数0が目標。

### 判定書式(Fable盲検の継承)
- 盲検表: `TRIAL_04/fable_blind_04.md`と同書式(KP行×distinct日本語gloss列、arm伏せ、key分離)。ラベル=PASS/THIN(△)/FAIL_LIT/FAIL(語義誤認等)。既存B0・Cp文字列は`fable_labels_04.json`のラベルを継承し、新規文字列のみFableが判定(約75行見込み)。
- 集計: `er112_kp_gm_trial_04_report.py report --labels`を再利用(arm名追加)。**Before/After表**(KP×arm×rep、ラベル)、**残存NG一覧**、**新規悪化一覧**(B0がPASSでX2がTHIN/FAILのKP)を必ず出す。
- 成功例だけでなく、残存NG(どのKP・どの型)・新規悪化・費用を記録する(ユーザー§2-4)。

## 3. 結果別の次の一手(自己ループ。同じPrompt変更を繰り返さない)

| 結果 | 解釈 | 次の一手(方式を変える) |
|---|---|---|
| X1有効(FAIL_LIT≤1/12)・S悪化なし | H5(制約句)が主因。最安で解決 | **案B**を採用提案(原価が下がる)。VALIDATED候補→ユーザー採否 |
| X1無効・X2有効・S悪化なし | 解釈先行+字義像判定が必要 | **案A**を採用提案 |
| X2有効だがS悪化(説明文化) | 条件付き化が不足 | X2の`japanese_gloss`規則を修正(『yesでも定訳優先を厳格に』『長さ上限』)して再Trial(同じPromptの反復ではなく、悪化原因に特化) |
| X2も無効(R残存≥2/12) | 解釈をgloss callの中で行う方式が不足(H4/H10が不十分) | 方式変更: (a)案D-light(canonicalizationの既存`reasoning`をhintとして添付。API追加0、offline構成可)、(b)reasoning effortを下げず**解釈だけをluna別callにする**案は追加callのため最終手段、(c)案E(選定schema)はユーザー承認が前提 |
| `naive_ja_conveys`が常にyes(形骸化) | 確証バイアス | naive_jaを先にgloss入力へ**物理的に分離**(別欄でnaive_jaのみ先に出力させ、次項目で判定)する構造変更 |
| trophy型の語義誤認(C r2型)が残る | 本文の意味の読み違い | meaning_in_text_enのみ別途Sol(1call 1.1円×flag率)でなく、前文を明示する入力(隣接文window)を追加する案を検討 |

停止の条件: 上限到達・STOP・予算超過見込み(下記)。効果がない反復や品質水準を超える過剰な改善はしない(ユーザー§2-4)。

## 4. 費用見積と予算枠

**事実(台帳で再確認、`er112_output/kp_gm_trial_04/paid_calls.jsonl` 389行、合計76.672円)**:
- Trial_04 60円枠: 実費56.57円(`TRIAL_04/BUDGET_LOG_01.md`) → **残 3.43円**。
- rep2 25円枠: 実費20.10円(`TRIAL_04/POSS_REP2_01.md:4`) → **残 4.90円**。(76.672=56.57+20.10 で一致)
- 合計残 8.33円。**この残額は課題②のrep2枠を含む**。課題①のみで使えるのは Trial_04枠の3.43円。2枠をまたいで使うか(Fable判断)で実施可能範囲が変わる。
- 日次(JST 10-24): ACTIVE_TASK記載の10-24累計239.87円+本Trial約8円=約248円 <1,000円。案件累計: KP案件≈247円(`POSS_REP2_01.md:4`)+約8円=約255円 <300円(7-7)。

**単価(実測、ledger)**: B0 0.061〜0.070円/call(1〜3KP)、M 0.038、G2 0.107〜0.130、G3 0.094〜0.104、Cp 0.179、C再生成 0.072。X1≈M(0.038〜0.045)、X2はG2〜Cpの範囲(0.11〜0.18)と推定し**上限0.16円/callで計算**(Pilotで確定)。

| 区分 | call数 | 単価(円) | 小計(円) |
|---|---|---|---|
| Stage 1 B0 新規3rep | 12 | 0.07 | 0.84 |
| Stage 1 X1 3rep | 12 | 0.045 | 0.54 |
| Stage 1 X2 3rep | 12 | 0.16 | 1.92 |
| **Stage 1 小計** | 36 | | **3.30** |
| Stage 2 X2 (S+co-KP、1rep) | 28 | 0.16 | 4.48 |
| Stage 2 X1 (同、有効だった場合) | 28 | 0.045 | 1.26 |
| **Stage 2 小計(X2のみ / X1も)** | 28 / 56 | | **4.48 / 5.74** |
| Judge | 0(Fable盲検) | | 0 |
| **合計(X2のみStage 2)** | 64 | | **7.78**(残8.33内、余裕0.55=7%) |

- **最小Trial(Stage 1のみ)= 約3.3円** → Trial_04枠の残3.43円内に収まる(余裕0.13円=4%。cap guardで超過前に停止)。Stage 1で有効性が判定でき、Stage 2の要否を決められる。
- **Stage 2** は 4.48円(X2のみ)で rep2枠の残4.90円内(余裕0.42円=9%)。X1も走らせる場合は5.74円で超過するため、Stage 1でX1が有効ならX1だけを走らせる(X2との同時はX1の方が安価=Stage 2はX1優先に切替)。
- **追加予算案**: 初回ループは上記で収まる。2ループ目(例: 悪化原因に特化したX2改訂版でStage 1+Stage 2を再実行)を想定する場合、**追加12〜15円**(1ループ=Stage 1 3.3+Stage 2 4.5+再実行余裕を含め約8〜9円、安全率1.4で12〜15円)を提示案とする。根拠: 見積り超過(Trial_04: 計画3円→実測7円等)の実績を踏まえ、単価は上限で見て安全率を取る。案件累計は約255〜270円で7-7の300円内。
- 見積りの不確実性(開示): X2単価0.11〜0.18円の幅、Stage 1でのB0 repの実測、記事ごとのKP数。**Pilot(X2を1記事分、約0.5〜0.8円)で単価を確定してからStage 1の残りへ進む**。

## 5. 実行上の安全条件(実装委任への引継ぎ)
- DEV専用(er112系、新規 `er112_kp_gm_trial_05*.py`)。Production module(`er003_*`/`er019_*`/`er026_*`/`er105_*`)は**編集せずimportして呼ぶのみ**(Trial_04のproduction hash検査[start/end sha256一致]を踏襲)。X2/X1のPromptはDEV側でmessageを組み立てる(`build_m_message`と同様)。
- 有料run前に `tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>` を実行(rc=3なら新規API呼出なし)。再起動は委任文が許す回数のみ。監督ループ・自動再試行ラッパは作らない。
- 日次/案件累計の事前確認(`daily_dev_cost_01.py`)。台帳は既存構造 `er112_output/kp_gm_trial_05/paid_calls.jsonl`(Trial_01〜04と同じ命名)。
- 検証は盲検(arm伏せ・key分離)。判定前にkeyを開かない。ラベル保存後に集計。
- X/Z DEV注入E2E(text工程、TTSなし)は、案A/Bが有効と判定され採用提案へ進む場合に別途実施(Trial_04のe2e構成を再利用。本Trialの範囲外、費用約1.7円)。

## 6. 本設計の限界(推測で埋めない)
- Rは4KP。『hard-coreの型』が一般化するか(他の新造比喩・断片慣用)はStage 2のSでは直接測れない(Sに該当KPは少ない)。一般化の確認は採用提案前のE2Eで新規記事を2〜3本生成して観察する(別承認枠)。
- 判定基準値(M1 ≤1/12、M3 ≤2/57)は事前宣言の案。**ユーザー定義の品質水準ではない**。Fableがユーザー定義水準と照合して確定する。
- Cpの再現確認(参照arm)は予算上、本設計の標準構成に含まない(Trial_04のCp 1 repを参照)。Cpが案Aの実質的な対抗である場合は追加費用約2.2円(R 3rep)で実施可能。
- Fable盲検は新規文字列約75行。同一rep間のラベル雑音の基準はTrial_04のB0 rep1-rep2差(1/61)のみ。
