# BUDGET_PLAN_02(Opus反映後のevidence run費用見積。いずれも**推定**。実測値で差替える)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02 / 日付: 2026-10-25 / **本委任(委任_02)の実費=0円(有料API呼出0・Production run 0)**。以下はevidence run(R1〜R4。翌日JST 10/26以降の別委任)の見積。
根拠データ・原単価は `BUDGET_PLAN_01.md` を踏襲(`docs/research/JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md:77-82`、`CURRENT_SPEC.md:2039-2052`)。新規部分は未測定=推定。

## 1. BUDGET_PLAN_01 からの差分
| 項目 | BUDGET_PLAN_01 | BUDGET_PLAN_02 | 理由 |
|---|---|---|---|
| E-0(Prompt 2-R上位3件の品質同等性確認 約1〜3円) | あり | **削除(0円)** | R-1採用でPrompt 2は無変更=上位3件は承認済み選定と同一。同等性確認が不要 |
| 選定call | 1 call(8件+理由) +0.01〜0.03円/レベル | **2 call**(Prompt 2無変更で3件+Prompt 2-Vで最大5件) | 2 call目が **+約0.05円/レベル**(Opus試算) |
| **M-7a** canonicalization INVALID時の残item再実行 | — | 発生時のみ1 call追加(約0.15〜0.4円/発生) | 発生率は未測定。通常は0 |
| **M-8** 確定集合Redundancy QA(KP集合、Advはvocab集合も) | — | **+0.02〜0.1円/レベル** | 候補全体(≤8)の1回は提示用の旗として維持 |
| 外側retry | item単位除外で減る見込み | M-7c(AUTO採用可能<3かつGate除外発生のときだけ)で発動条件を限定 | 減少〜同等 |
| **M-7a + M-8 + 2 call目の合計増分** | — | **+約0.1〜0.5円/セット**(BUDGET_PLAN_01の+0.9〜2.5円に加算。Opus妥当確認済み) | |
| セット合計(X: Std+Adv、Z: 同) | +0.9〜2.5円/セット | **+約1.0〜3.0円/セット(推定)**。70円比 約1.4〜4.3% | Charter 3(量産単価)の増額は避けられない部分(候補をHumanへ見せるGate)。最小化策はBUDGET_PLAN_01 §1のとおり |
| 文法(Part 2) | 本件では0 | 0 | 変更なし |

## 2. evidence run(R1〜R4。TEST_PLAN_02 §4。**本委任では実行しない**)
| run | 内容 | 推定費用 |
|---|---|---|
| R1 X HRあり | 既存記事(Std+Adv)でKP候補生成(2レベル)+`reselect` 1回(NG検証)+Part 1(Adv、5件)+TTSはKP segment差分のみ(Master Store再利用)+player/page | KP関連 約3〜6円+KP TTS差分 約1〜3円 ≒ **4〜9円** |
| R2 X HRなし(auto) | 同記事を別run、`--kp-review auto`(+ **「前のroundでNG → 不在宣言 → AUTOでNGがskipされる」シナリオを組み込む**: R1でNG登録した句が共有storeにあるため、R2のAUTO候補にその句が出ても採用されないことを確認) | **3〜6円** |
| R3 Z HRあり | 既存作品の複製run: kp stage(2レベル)+select+Part 1+`tts_b1b/tts_a2`のKP segment差分+gate/assemble/pages/page_verify | **8〜16円**(再利用できない場合最大約40円) |
| R4 Z HRなし(auto) | 同作品の別複製run、auto宣言 | **8〜16円**(同上) |
| 小計 | | **約23〜47円**(再利用できない最悪ケース約90円) |
- 付随: 再選定往復・失敗時の再実行(委任文が許す回数のみ)の予備20〜30%。
- 合計(予備込み): **約30〜60円(最悪約110円)**。BUDGET_PLAN_01から変わらない(E-0削除の−1〜3円が、M-7a/M-8の+0.1〜0.5円/セット×4 runと相殺)。

## 3. 案件Cap・承認
- **案件Cap = 150円**(再実行余裕込み。Fable確定)。
- 7-7(2026-10-19)の自律範囲: 承認済みScope(APPROVED_FOR_PRODUCTION)・個別Cap内で案件見積300円以下→都度承認不要。本見積は300円以下。(a)日次1,000円超過見込み(7-9)、(b)個別Cap超過、(c)新仕様/重要Scope変更は事前にFable報告。日付・stage分割で境界を回避しない。
- モデル(最新原則・25節): 選定/canonicalization/gloss/解説/T1 = routing契約の`SUPPORT_MODEL`(gpt-6-luna、現行Production。本番ラインのモデル選定は別判断)。evidenceの報告には使用モデル名・最新か・理由を記載する。

## 4. 時間見積(並列化可否)
- R1とR3(Family別・本文別・run別)は独立=並列起動可(同一run内の依存は直列: 候補→Human→再開)。R2はR1のHuman待ちと独立に開始可(auto宣言)。ただし**R2のNG skipシナリオはR1のNG登録(共有store)に依存**するため、その確認だけR1のreselect後。
- 各runの所要(推定): R1,R2 約30分 / R3,R4 約1〜1.5時間 / Human選択の介在待ちは別。
- 実行順序案: (1) R1 と R3 を並列起動(候補生成まで)→ (2) 候補確認・select/reselect → (3) 再開・完走 → (4) R2 と R4 を並列(auto)。RESTART_STORM(Z: 5分間に3起動)に注意し、再起動は間隔を空ける(OPERATIONS_01 §4)。
