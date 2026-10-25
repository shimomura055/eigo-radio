# BUDGET_PLAN_01(evidence run費用見積。いずれも**推定**。実測値で差替える)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_01 / 日付: 2026-10-25 / 本委任の実費=0円(API 0)。以下は実装委任でのevidence run見積。
根拠データ: `docs/research/JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md:77-82`(X coffee scaffold 1.97+tts 22.24=24.2円/KP関連2.45円、X small_bag 20.8円/KP関連2.17円、Z melos 26.1円/KP関連3.71円[失敗retry込み])、`CURRENT_SPEC.md:2039-2052`(Part 1解説0.088〜0.137円/set+T1訳0.031〜0.039円/set)、gloss再整合約0.06円/call(`er026…:E2E_PERSON_REPAIR_EST_JPY`コメント)。新規部分(8件canonicalization等)は未測定=下記は推定。

## 1. 1セット(1記事)あたりの追加原価(量産単価、推定)
| 項目 | 現行 | 新仕様 | 増分(推定) |
|---|---|---|---|
| 選定call(Luna、Prompt 2-R) | 3件出力 | 最大8件+理由 | +0.01〜0.03円/レベル |
| canonicalization(Luna) | 3件 | 最大8件(1 call、構造INVALID時は現行retry) | +0.15〜0.4円/レベル(入出力トークン約2.5倍の推定) |
| gloss再整合 | 対象のみ | 最大8件中の対象のみ | +0.06〜0.3円/レベル(対象数に比例) |
| Redundancy QA | 3件 | 最大8件(1回) | +0.02〜0.1円/レベル |
| 外側retry頻度 | 現行 | item単位除外で減る見込み(未測定) | −〜+ |
| Part 1解説+T1訳(Advのみ) | 3件 0.119〜0.176円 | 5件 | +0.05〜0.08円 |
| 文法(Part 2) | — | **本件では0**(Part 2採用確認後に別見積) | — |
| **セット合計(X: Std+Adv、Z: 同)** | KP関連2.2〜3.7円 | **+0.9〜2.5円/セット(推定)** | 70円比 約1.3〜3.6% |
- Charter 3(量産単価の継続最適化): 増額は避けられない部分(候補をHumanに見せるための8件Gate)。最小化策=(1)item単位除外でattempt全体の再選定を減らす (2)canonicalizationの遅延方式(AUTO宣言済みrunは先頭5+予備)=切替複雑化のためv1は全8件一括、実測で改善余地があれば第2段 (3)Redundancy QAを候補全体1回のみ (4)gloss対象は既存どおり必要item限定。
- **HR運用のコスト**: Human待ちはAPI費用0。担当者の時間(約30〜55分/日、推定、DESIGN §k)は開発費に含まれない運用コストとして開示。

## 2. 事前確認(E-0): Prompt 2-R の上位3件品質同等性
- 内容: 保存済みの既存run記事(X/Zの各Std/Adv、約12記事レベル)に新Prompt 2-Rを適用し、旧Prompt 2の3件と新TOP3を比較(既存Validator通過率・Sonnet所見・Fable確認)。
- 費用: 選定call 12本×約0.05円≒0.6円(+比較用canonicalizationを行う場合は+約2円)。**合計約1〜3円**。
- 実施時期: 実装委任の最初(Opus条件Aレビュー後)。

## 3. evidence run(R1〜R4。TEST_PLAN_01 §4)
| run | 内容 | 推定費用 |
|---|---|---|
| R1 X HRあり | 既存記事(Std+Adv)でKP候補生成(2レベル)+reselect 1回(NG検証)+Part 1(Adv、5件)+TTSはKP segment差分のみ(Master Store再利用)+player/page | scaffold KP関連 約3〜6円(reselect分含む)+KP TTS差分 約1〜3円 ≒ **4〜9円** |
| R2 X HRなし(auto) | 同記事、`--kp-review auto`(候補はR1のキャッシュ再利用不可=別run。同本文で再生成) | **3〜6円** |
| R3 Z HRあり | 既存作品の複製run: kp stage(2レベル)+select+Part 1+`tts_b1b/tts_a2`のKP segment差分+gate/assemble/pages/page_verify | 実測`run_e2e_03`=36.4円(`CURRENT_SPEC.md:1709`、全stage実走)。writer/support/非KP音声を複製run(provenance付き再利用)で省くと KP関連 約4〜8円+差分TTS 約3〜8円 ≒ **8〜16円**(再利用できない場合は最大約40円) |
| R4 Z HRなし(auto) | 同作品の別複製run | **8〜16円**(同上、最大約40円) |
| 小計 | | **約23〜47円**(再利用できない最悪ケース約90円) |
- 付随: 再選定往復・失敗時の再実行(委任文が許す回数のみ。無断再起動0)の予備を20〜30%見込む。

## 4. 合計と承認枠
- 実装委任の見積合計: **約30〜60円(最悪約110円)**。案件Cap案=**150円**(再実行余裕込み)。
- 7-7(2026-10-19)の自律範囲: 承認済みScope(APPROVED_FOR_PRODUCTION)・個別Cap内で**案件見積300円以下**→都度承認不要。本見積は300円以下。ただし(a)日次1,000円超過見込み(7-9)、(b)個別Cap超過、(c)新仕様/重要Scope変更(Part 2採用、Std単語解説拡張等)は事前にFable報告。
- 日付分割・stage分割で境界を回避しない(7-7)。
- モデル(最新原則・25節): 選定/canonicalization/gloss/解説/T1 = routing契約の`SUPPORT_MODEL`(gpt-6-luna、現行Production。本番ライン選定は別判断)。評価Trialで旧モデルは使わない。報告に使用モデル名・最新か・理由を記載。

## 5. 時間見積(並列化可否)
- 並列化: R1とR3(Family別・本文別・run別)は独立=並列起動可(同一run内の依存は直列: 候補→Human→再開)。R2はR1のHuman待ちと独立に開始可(auto宣言)。E-0は実装のtest整備と並行。
- 所要(推定): E-0 約0.5〜1時間 / R1,R2 各約30分 / R3,R4 各約1〜1.5時間 / Human選択の介在待ちは別。
