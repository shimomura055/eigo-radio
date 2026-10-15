## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_08(main merge+merge後検証+SSOT Status更新+ユーザー指示原文保存)。並行タスク: 同時刻に3つの**read-only調査委任**(AUW 委任_09[U1/U2/Section計画]、`FAMILY-C-JA-TTS-PRODUCTION-FIX-01` 委任_01、`DECISION-QUALITY-IMPROVEMENT-01` 委任_01)が`C:\Users\tensh\eigo-radio`(main dir)で新規ファイルを作るのみで、Git操作・SSOT編集・既存ファイル編集はしない。**Git操作・SSOT編集・`docs/pm/ACTIVE_TASK.md`更新は本委任だけが行う。** 衝突なし。

## 前委任(07b)の受入記録(Gate 7、sandwich-pm.md 4-2)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md` L204): 「4. Primary／Secondary両NGなら最大3回のTTS生成フローが成立。」L217「1項目でも未確認であればPRODUCTION_WIREDと報告しない。」
- 最終成果物: `evidence_07b/narr_cap3/`(narrator A2外側ループ通算3回→NG_BOTH→Lock HUMAN_REVIEW_REQUIRED、HR queue 1行、cool-down 600.004秒)、commit `614958796`。
- 証拠: `RUNTIME_EVIDENCE_06.md` §15-5、`runner_execute.json`、Secondary重複0(Azure 1回)、JPY 0.72。
- 一致・不一致: 条件4のnarrator経路は一致。条件1・2・9はFamily C JA(F4=OPEN-372)とB A2 narrator見出し系が未確認のまま(不一致=未充足として明示済み)。条件12 merge未。
- 判定: 07b単体はACCEPTED。AUW全体は`PRODUCTION_WIRED`未宣言のまま。
- 前委任QDC: 目的=条件4実音声/試行=07(timeout 590で途中終了)→07b(timeout 1200で完走)/原因=既存600秒cool-downとtimeoutの競合/結果=完走/費用=JPY 0.57+0.72/次の一手=ユーザーGo後にmerge(本委任)。

## 性質/到達上限Status/禁止事項

- 性質: Production反映(mainへのmerge)。ユーザー正式決定済み(REGISTER #87=Go、下記ユーザー指示原文 A-1)。到達上限Status: `MERGED_PENDING_PRODUCTION_WIRED`(merge済み・`PRODUCTION_WIRED`は未宣言。宣言はFable/ユーザー)。**本委任では`PRODUCTION_WIRED`と書かない。**
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、squash merge、競合の自己解決(競合・エラー時は中止してRESULT_PACKETに報告)、STOPセンチネル削除・回避、HR Lock迂回、有料API実行(本委任はAPI 0。TTS/ASR/LLM呼出を伴うコマンドは実行しない)、`er078_asr_unified_judge_01.py:65-66`のU1/U2定数変更(別委任で扱う)、Production code変更。
- Opus独立技術レビューGate(11-3): 非該当(設計変更なし。条件A/Cレビューは委任_02b/06cで実施済みで内容不変)。
- 時間見込み: 全体60〜90分(事前予行10・merge5・merge後test/監査/smoke 30〜45・SSOT/REGISTER更新15・報告10)。並列化: 本委任は直列(merge→検証→SSOTの順序依存)。他3委任は並列実行中(read-only)。
- 費用/日次: 当日(2026-10-16 JST)既使用=AUW 07/07b 約JPY 1.3は確認済み(出典 `RUNTIME_EVIDENCE_06.md` §15)、06〜06eの日別内訳は未確認/本委任見積 JPY0/改善見込み 高/承認区分: C(承認済みscope内。ユーザーGo #87)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任は費用上限[Cap]を伴わない(API 0)。

T-0の保存先: 本委任文全文を`docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_08.md`へ**全文**(要旨化禁止)保存。加えて、下記「ユーザー指示(原文)」節の本文を**一字一句そのまま**`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`へ保存する(冒頭1行に「2026-10-16 ユーザー指示原文(ChatGPT経由の実行指示。A=AUW / B=Family C JA TTS / C=DQI)。Fableが受領。」を付す)。この2ファイルは他の3委任から参照される。

## ユーザー指示(原文)

以下は2026-10-16にユーザーから受領した指示の全文である(ChatGPTが作成しユーザーが提示)。

# Claude Code／Fableへの指示
## AUW Production完成・Family C不具合是正・Fable PM判断改善

### 0. 今回の指示の位置づけ

本指示は、これまでのユーザー正式決定に基づく実行指示である。

以下の3案件を明確に分離して管理する。

- **A：AUW統一ASR判定のProduction完成**
- **B：Family C日本語TTSの既存Production不具合是正**
- **C：Fable自律PMの判断品質改善**

A・B・Cを一つの仕様変更として混在させない。

各案件のStatus・受入条件・Open Item・証拠を独立して管理する。

**共通原則：ユーザーがすでに決定した事項を、理由なくUSER_DECISION_REQUIREDに戻さない。**

承認済み仕様の実現に必要な技術調査・修正・テストは、自律的に進める。

新しい仕様判断、承認範囲を超える変更、重大な安全・品質・予算問題が発生した場合のみSTOPする。

---

# A. AUW統一ASR判定のProduction完成

**管理ID：ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01**

**現在Status：APPROVED_FOR_PRODUCTION**

**到達目標：PRODUCTION_WIRED**

## A-1. ユーザー正式決定

mainへのmergeを正式に許可する（REGISTER #87：Go）。

既存branch `feat/auw-unified-asr-01` の実装・テスト・証拠を確認し、最新mainとの整合を取ったうえで、既存Git運用規則に従ってmergeする。

merge後も、必要な是正・Regression・runtime evidence・SSOT反映まで継続する。

**mergeだけでタスク完了としない。**

## A-2. 統一ASR判定の正本

英語・日本語、全Family・全Production Sectionについて以下を基本とする。

1. Primary ASRがPASSなら採用。
2. Primary NGなら、不一致の種類・大きさにかかわらず原則Secondary ASRを実行。
3. Secondary PASSならPASS_WITH_WARNINGとして採用。
4. WARNINGは事後試聴リストに自動登録。事前Human Reviewは不要。
5. 両方NGなら既定のTTS再生成へ進む。
6. 通算3回のTTS生成で不合格なら、承認済みのLocal Rewrite／Human Review経路へ進む。
7. 数値・否定などの明確な重大内容差、独立音声品質QAは維持する。

Melos saidのConnected Speech／M1の合格実績を維持する。

**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**

## A-3. 日本語固有名詞・低類似度の除外を是正

現在のU1（REGISTER #83）は、ユーザー正式承認済み統一仕様との不整合として扱う。

現在の固有名詞差・類似度0.4未満等によるSecondary事前除外を調査し、承認済み共通ルールに合わせて是正する。

実行要件：

- 固有名詞差でもPrimary NGならSecondary確認。
- 低類似度でもPrimary NGならSecondary確認。
- Secondaryが原稿を正当に支持すればWARNING付き採用。
- 数値・否定等の保護差、独立QAは例外として維持。
- 既存日本語ASR Validator・Pronunciation Ledgerとの整合確認。
- 過剰救済・誤受理がないことをRegressionで確認。

これは新仕様Trialではなく、**承認済み仕様への実装修正**である。

新たな仕様判断が本当に必要な場合を除き、同じ採否をユーザーへ問い直さない。

## A-4. Local Rewrite後のforce_secondaryを確認

U2（REGISTER #84）について、A2_ONLYの既存例外の意味・成立経緯・品質上の必要性を確認する。

注意：

- A2は従来のStandard相当の処理経路。
- B1系はAdvanced相当。
- Primary NG→Secondaryは両レベル共通の正式仕様。
- `force_secondary`はPrimary PASS時にもSecondary確認を要求する特殊経路であり、通常のSecondary利用とは別。

実施事項：

1. 既存仕様・承認履歴・Production codeを照合する。
2. なぜA2だけに限定されているのか、品質・安全上の根拠を確認する。
3. 今回の統一仕様と矛盾しないか判定する。
4. 不要な旧例外なら、承認済み共通仕様へ整理する。
5. 例外維持が本当に必要なら、理由・適用範囲・影響を報告する。

**Primary PASS時のSecondary強制照合を、根拠なく全レベルへ拡大してはならない。**

## A-5. 残Sectionの実証

43行マトリクスを次の区分で再整理する。

- 実音声で検証済み
- 新規生成が必要だが未検証
- 既存音声の再利用・複製が仕様どおりで、追加ASR不要
- 正式仕様上のN/A
- 別Production不具合で検証不能

特にFamily B A2 narratorの見出し・Hook・Tension・Closingの必要な実音声確認を実施する。

Family C日本語の既存TTS不具合はB案件で扱い、AUWの実装漏れと混同しない。

ただし、全SectionのProduction Wiring受入条件から未確認項目を黙って除外しない。依存関係・未充足条件を明示する。

## A-6. Secondary障害時の処理

U4（REGISTER #86）については、**現行挙動を当面許容する**。

技術障害でHuman Review Lock／Local Rewriteへ進む非効率は、既知の独立Open Itemとして管理する。

今回、ユーザー承認なしにLock挙動を変更しない。

## A-7. AUW完了条件

- 正式Production初回経路に統一判定を適用
- retry／fallback／regeneration／Local Rewrite後の整合
- 日本語U1不整合の是正
- U2の必要性確認・承認範囲内の整理
- 必要な全Section実音声・runtime evidence
- 数値／否定／Connected Speech／M1／F1のRegression PASS
- WARNING試聴リストが実際に機能
- 二重Secondary呼出・無限retryなし
- actual model_id／routing確認
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- main merge／push／必要なmerge後test
- Dangling Reference Check
- Fableによるユーザー承認内容との独立照合

すべて満たした場合のみPRODUCTION_WIRED。

未充足があれば、達成済み事項と未達事項を区別して報告する。

---

# B. Family C日本語TTSの既存Production不具合是正

**管理ID：FAMILY-C-JA-TTS-PRODUCTION-FIX-01**

**現在Status：既存Production不具合の是正承認**

**到達目標：正式Production経路で日本語音声生成・検証・再利用整合が正常動作すること**

## B-1. 確認済みの不具合

Family CのProduction runner `er013_family_c_production_runner_01.py`で、日本語Comment生成時にも共通のnarrator処理を呼んでおり、その内部でTTSの言語が`"en"`に固定されている。

このため日本語Commentの新規音声生成が失敗した。

また、既存音声のreuse_fromで、原稿変更後にも旧音声が紐づくリスクが確認されている。

**AUWの統一ASRとは別のProduction不具合である。**

## B-2. 是正方針

最初に既存のFamily C正式仕様とProduction経路を確認する。

そのうえで、承認済み仕様の範囲内で必要な修正を実施する。

最低限：

- 日本語Commentを日本語としてTTS生成する。
- 日本語タイトル等、同じ問題が及ぶSectionを調査する。
- 適切な日本語Voice・言語設定・ASR Validatorを使用する。
- 英語Sectionの従来動作を壊さない。
- 日本語の長さ・音声品質・Segment構造を検証する。
- 原稿と音声の対応を保証する。
- reuse_from／metadata／hash等の整合を確認し、変更後の原稿に旧音声が誤って紐づく問題を防ぐ。
- retry／fallback／regenerationとの整合を確認する。
- 必要な実音声をProduction正式経路から生成し、runtime evidenceを取得する。

単なる`"en"`→`"ja"`の置換だけで安全に解決できるなら、過度な改修はしない。

ただし、単一行の修正だけで品質・再利用整合を確認せず完了としない。

## B-3. 自律是正原則

既存仕様に沿った言語設定・配線・metadata等の技術的不具合修正であれば、ユーザーへ再承認を求めず実施する。

新しいVoiceの正式採用、音声品質基準の変更、日本語Commentの内容仕様変更など、新たな仕様判断が必要になった場合のみSTOPする。

不具合がAUW検証中に発見されたことを理由に、AUW仕様と混同しない。

## B-4. 完了条件

- Family C日本語Commentの新規TTS成功
- 必要な日本語Sectionの生成・ASR確認
- 英語Sectionの回帰なし
- 原稿変更時の誤音声再利用なし
- Production実行でruntime evidence取得
- Validator／Regression／integration test PASS
- SSOT／Open Item／Git反映
- Dangling Reference Check
- 実成果物が既存Family C仕様を満たすこと

条件未充足ならPRODUCTION_WIREDとしない。

---

# C. Fable PM判断品質の改善

**管理ID：PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DECISION-QUALITY-IMPROVEMENT-01**

**現在Status：既存改善は実装済みだが、目的達成は未検証・未達**

**今回の到達範囲：改善方式の検討・既存規則との整合確認・具体案の提示**

**Day 5〜6：引き続き保留**

## C-1. 解決すべき問題

Fableはこれまでの改善で、ユーザー原文・最終成果物・受入条件の照合を行うようになった。

しかし、次の問題が残る。

1. 承認済み仕様を再びユーザー判断へ戻す。
2. 自己解決可能な技術的不具合をユーザーへ転送する。
3. 発見済みの重大品質NGを最終判定へ正しく反映できない。
4. 本来のタスクと、新規発見した独立問題を混在させる。
5. 検出した不適合に対する是正・STOP・ユーザー提示制限が不適切。

単なる報告形式の問題ではなく、PMの意思決定品質の問題として扱う。

## C-2. 改善案の検討

以下はChatGPTからの参考提案であり、実装方式の指定ではない。

Fable自身が検討し、必要に応じてOpus独立レビューを受けること。

### 提案①：重大品質NGと最終受入の整合強制

成果物に重大な意味反転、Fact欠落、学習内容の不一致等がある場合、別のテストPASSや形式的問題による差戻しで相殺できない仕組みを検討する。

### 提案②：不適合成果物の提示制限

目的を満たしていない成果物を、完成品としてユーザーへ試聴・選定依頼することを防ぐ。

ただし、不完全な候補を比較すること自体が正式目的のTrialは区別する。

### 提案③：最終判定の矛盾検出

受入記録の詳細では重大NGなのに、総合判定ではACCEPTEDとなるなどの矛盾を、Validator・構造化判定・独立レビュー等で防ぐ方式を比較する。

### 提案④：ユーザー判断Gateの適正化

必ず以下を区別する。

- ユーザー承認済みで実施すべき事項
- 承認範囲内で技術的に自己解決可能な事項
- 新たに発見された独立問題
- 本当にユーザー判断が必要な事項

承認済み事項を再びUSER_DECISION_REQUIREDに戻さない。

独立問題はOpen Itemに分離し、重大な依存・阻害関係がない限り、本タスクを不要に停止させない。

## C-3. Fable／Opusに求める検討

以下を比較評価する。

- 現行Prompt／運用規則の改善だけで足りるか
- 構造化した受入判定が必要か
- Validator等の機械的な矛盾チェックが必要か
- Fable自身による独立判断とOpusレビューの適切な役割分担
- 誤STOP・過剰なUSER_DECISION_REQUIREDのリスク
- 実装・運用コスト
- 他Family／案件への再利用性
- 既存Governanceとの重複・競合
- 再発防止効果

Fableは単にOpusの提案を転記するのではなく、自分自身の推奨案・理由・代替案・QDC評価を示す。

## C-4. 今回のSTOP条件

本指示では、新規の大規模改修・追加盲検・Day 5〜6開始は承認していない。

改善案の比較と推奨がまとまった段階でSTOPし、ユーザーへ提示する。

新しい運用仕様を独自にProduction採用してはならない。

---

# D. 横断的なPM運用ルール

今回のA・B作業とCの検討では、以下を徹底する。

1. **正式承認済みの仕様は実装して完了させる。** Trialで止めない。
2. USER_DECISION_REQUIREDは、真に新しいユーザー判断が必要な場合だけ発行する。
3. 技術的な原因調査・是正方法の選定は原則Claude／Fableが担う。
4. 別問題の発見時は、重要度・依存関係・Production影響を確認し、Open Itemへ分離する。
5. 未承認の新仕様をProductionへ反映しない。
6. 既存のHuman Review Lock・費用上限・STOP指示を尊重する。
7. 実装後は、技術的テストだけでなく、ユーザー目的との一致を検証する。
8. retry／fallback／regeneration等の後続経路まで整合する。
9. 重大品質NGを検出した成果物を、無条件にACCEPTEDとしない。
10. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／USER_DECISION_REGISTERを実態に合わせて更新する。

既存の関連Open Item・承認済み未配線事項を確認し、作業範囲外のものは明示して引き継ぐ。

**最終報告では、A・B・Cそれぞれについて「達成・未達・理由・証拠・残る判断事項」を独立して示すこと。**

AとBはProduction実装・実証まで、Cは改善方針の検討までが今回の承認範囲である。

A・Bを無条件に完了扱いせず、Cの改善案をユーザー判断なしにProduction採用しない。

(ユーザー指示原文ここまで)

## KPI provenance欄

該当なし(本委任はmerge・既存testの再実行のみ。test結果は`reuse`[既存test]、新KPIなし)。

## Opus台帳更新

該当なし(状態遷移なし)。

## 事前指定Read一覧

- `er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md` §1(L9-21、merge計画)・§6(L90-93)。
- `er058_output/unified_all_roles_production_wiring_01/REVERT_REHEARSAL_07.md` 冒頭〜30行(予行の前提確認用)。
- `docs/pm/USER_DECISION_REGISTER_01.md` L160-170(#83〜#87の既存行)。
- `docs/pm/ACTIVE_TASK.md` L1-12(固定ヘッダ現状)。
- `docs/pm/PM_BRIEF.md` L236-267(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. `CURRENT_SPEC.md`: Grep `統一ASR判定仕様` → 節のStatus行を特定。既存行は書換えず、Status行の直後に追記: 「Status追記(2026-10-16 委任_08): ユーザーGo(REGISTER #87、2026-10-16指示A-1)により`feat/auw-unified-asr-01`をmainへmerge(merge commit `<hash>`)。`PRODUCTION_WIRED`は未宣言(残=U1是正[A-3]・U2確認[A-4]・残Section実音声[A-5]・Fable独立照合)。U4(#86)は現行挙動を当面許容(OPEN-371で管理、Lock挙動変更なし)。」
2. `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#87(新規` / `#86(新規` / `#83(新規` / `#84(新規` → 各行は不変とし、L169付近(「本追記後:」行)の直後に新ブロックを追加: 「- 2026-10-16 ユーザー指示(原文=`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`)による更新: #87=**判断済み(Go)**、merge commit `<hash>`。#86 U4=**判断済み(現行挙動を当面許容。Lock変更なし。OPEN-371で独立管理)**。#83 U1=**判断済み(方針): 除外は承認済み統一仕様との不整合として是正する[固有名詞差・類似度<0.4でもPrimary NGならSecondary確認、数値・否定保護と独立QAは維持]。実装は委任_09以降**。#84 U2=**調査中(A2_ONLY例外の成立経緯・必要性を確認し承認範囲内で整理。根拠なく全レベルへ拡大しない)**。#85 U3=据え置き(今回指示に言及なし。UDRのまま)。」
3. `OPEN_ITEMS.md`: Grep `OPEN-371 ` → 当該行は不変。行末尾に追記(同一行内、`| 区分:`より前の説明セル末尾): 「【2026-10-16更新】ユーザー指示A-6: 現行挙動を当面許容。Lock挙動はユーザー承認なしに変更しない。独立Open Itemとして継続。」
4. `docs/pm/REPORT_LEDGER.md`: Grep `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` → 既存行の末尾に「委任_08 merge済み(`<hash>`)」を追記(行の構造を崩さない)。
5. `DECISION_LOG.md`: Grep `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` の末尾節 → 節末尾に追記: 「- 2026-10-16 委任_08: ユーザーGo(#87)によりmain merge(`<hash>`、`--no-ff`、squashなし)。merge後 中核12 file <N> passed/後方互換<N>/静的監査<N>/flag OFF経路<N>/smoke dry-run結果。U4は現行許容(A-6)。U1是正方針・U2調査はユーザー指示A-3/A-4に従い後続委任。`PRODUCTION_WIRED`未宣言。」索引行があれば1行追加。
6. `docs/pm/ACTIVE_TASK.md`: 全体を上書き(固定ヘッダ書式、PM_BRIEF L252-267)。管理ID行に3案件(AUW 委任_08〜/FCJ 委任_01/DQI 委任_01)を併記。Status: AUW=MERGED_PENDING_PRODUCTION_WIRED / FCJ=調査中 / DQI=検討中(Day5〜6保留)。UDR-blocking: なし。UDR-deferred: #85 U3、#80〜#82(OAR-02)、#70、#69、#68、#63他。STOP条件固定行を維持。QDC行: 当日費用=2026-10-16 既確認分 約JPY1.3(06〜06e日別は未確認)/1,000。承認済み指示: 2026-10-16ユーザー指示原文ファイルパス。

## 実行コマンド全文

作業ディレクトリは**main checkout済みworktree** `C:\Users\tensh\eigo-radio-crbn`(存在しなければ `git -C C:\Users\tensh\eigo-radio worktree list --porcelain` で確認し、無い場合はRESULT_PACKETに記録して `git -C C:\Users\tensh\eigo-radio worktree add C:\Users\tensh\eigo-radio-crbn main` を試す。失敗時は中止報告)。

手順0(STOP確認): `cd C:\Users\tensh\eigo-radio; .venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` → rc=0を確認(rc≠0ならmergeせず中止報告)。

手順1(事前予行): `cd C:\Users\tensh\eigo-radio-crbn; git fetch origin; git status --porcelain --branch; git log --oneline -3 origin/main; git log --oneline origin/main..feat/auw-unified-asr-01 | Measure-Object -Line; git log --oneline feat/auw-unified-asr-01..origin/main` → origin/mainにbranch未取込のcommitがあれば `git merge --no-commit --no-ff feat/auw-unified-asr-01` → 競合0確認(`git diff --name-only --diff-filter=U`が空)→ `git merge --abort`。競合があればabortして中止報告。

手順2(merge): `git checkout main; git pull --ff-only origin main; git merge --no-ff feat/auw-unified-asr-01 -m "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01: 統一ASR判定・全Section Production Wiring(main merge、ユーザーGo #87)"; git log --oneline -1; git push origin main`。(crbn worktreeに未commitの変更があってもmergeに関係しないファイルなら続行可。関係すれば中止報告。)

手順3(main dirの追随): `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main`(main dirは`feat/auw-unified-asr-01`上にあり、ff可能なはず。不可なら理由を記録して手順4をcrbn側で実施)。ff成功後 `git checkout main`(同一commitなので未commit変更があっても通る想定。拒否されたら無理に進めず、feat branch上のまま手順4へ。`checkout -f`禁止)。`git branch --show-current; git status --porcelain | Measure-Object -Line` を記録。

手順4(merge後検証、API 0、main dirで`.venv`使用。CLOSEOUT_PLAN_07 §1-3どおり):
- `cd C:\Users\tensh\eigo-radio; .venv\Scripts\python.exe -m pytest -p er078_netguard_pytest_plugin_01 er058_asr_tts_prodfix_01_test_01.py er063_family_z_audio_01_n01_test_01.py er063_family_z_audio_01_test_01.py er078_asr_unified_en_wiring_test_01.py er078_asr_unified_ja_wiring_test_01.py er078_asr_unified_judge_01_test_01.py er078_asr_unified_wiring_05_test_01.py er078_asr_unified_wiring_06c_test_01.py er078_asr_unified_wiring_06d_test_01.py er078_asr_unified_wiring_06e_test_01.py er078_asr_value_guard_01_test_01.py er078_pass_with_warning_registry_01_test_01.py -q -p no:cacheprovider` (期待411 passed。netguard pluginの正式名が異なる場合は `Get-ChildItem er078*netguard*` で実名を確認して置換し、置換をRESULT_PACKETに記録。ファイル名が存在しないものは`Get-ChildItem er078_*_test_01.py`で実名を確認して置換)。
- `.venv\Scripts\python.exe -m pytest -p <netguard> er078_asr_unified_backcompat_07_test_01.py -q -p no:cacheprovider` (期待53 passed)。
- `.venv\Scripts\python.exe -m pytest -p <netguard> er078_asr_unified_wiring_static_audit_01.py -q -p no:cacheprovider` (期待15 passed) と `.venv\Scripts\python.exe er078_asr_unified_wiring_static_audit_01.py` (出力の`unlisted_new_calls`/`vanished`/`count_changed`がすべて空)。
- `.venv\Scripts\python.exe -m pytest -p <netguard> er078_asr_unified_wiring_06c_test_01.py -k test_g -q -p no:cacheprovider` (期待3 passed)。
- smoke(dry-run、`--execute`なし): `.venv\Scripts\python.exe er078_auw_runtime_evidence_06e.py tstop`、同`kp4`、同`dlg_cap2`、`.venv\Scripts\python.exe er078_auw_runtime_evidence_07.py narr_cap3` → 各出力の`stop_files_present: []`・`shared_state_unchanged: true`を記録(script引数形式が異なる場合は`--help`で確認し、`--execute`を付けないこと)。
- `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` rc=0。
- 影響suite per-file(06e `patch_06e/summary_06e.json`と同形式)は時間が許せば実施、省略時はRESULT_PACKETに「未実施」と明記(次委任で実施)。
- test実行で本番state file(`er011_output/attempt_history.jsonl`等、OPEN-374)が変化しても**addしない**。

手順5(SSOT・REGISTER・LEDGER・ACTIVE_TASK更新): 上記Grep手順1〜6。main dirが`main`に切替済みならmain dirで、そうでなければcrbn worktreeで編集・commit(どちらで行ったかを記録)。

手順6(commit/push): `.venv\Scripts\python.exe tools\secret_scan.py --staged`相当(既存のsecret scan手順。実名は`Get-ChildItem tools\*secret*`で確認)hits=0確認後、
`git add CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/REPORT_LEDGER.md docs/pm/ACTIVE_TASK.md docs/pm/RESULT_PACKET_AUW8.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_08.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_08_check.json docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`
`git commit -m "AUW 委任_08: main merge後のSSOT Status更新(merge commit <hash>、PRODUCTION_WIRED未宣言)+REGISTER #83/#84/#86/#87更新+2026-10-16ユーザー指示原文保存"`
`git push origin main`。

## SSOT追記文

上記「事前指定Grep一覧」1〜5の文面をそのまま使う(`<hash>`・`<N>`は実値に置換)。

## Git(明示add対象・コミットメッセージ・trailer)

- 本Agentは`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`の編集権を**持つ**(追記のみ・既存行の書換え・削除禁止)。`docs/pm/PM_GOVERNANCE.md`は編集しない。
- merge commit: 手順2のメッセージ。SSOT commit: 手順6のメッセージ。trailer不要。
- add対象は手順6の明示リストのみ。test副作用で変化した`er0XX_output/*`・`*.jsonl`は**addしない**。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_AUW8.md`に記載(`docs/pm/RESULT_PACKET.md`は上書きしない):
1. T-0結果(check PASS/FAIL)、ユーザー指示原文ファイルの保存確認(sha256)。
2. 事前予行の結果(origin/main側の未取込commit有無、競合0)。
3. merge commit hash、push結果、`git log --oneline -3 main`。
4. main dirの状態(branch、ff結果、checkout main可否と理由、未commit変更件数)。
5. merge後検証の実測(各test件数、静的監査出力、smokeの`stop_files_present`/`shared_state_unchanged`、stop_scope rc)。期待値との差があれば原因。
6. SSOT/REGISTER/LEDGER/ACTIVE_TASKの更新箇所(ファイル:行)。
7. commit hash(SSOT)・push結果・secret scan hits。
8. 逸脱・未実施事項(per-file suite省略等)・新規発見の独立問題(あればOPEN候補として記載のみ、OPEN_ITEMSへの新規起票はしない)。
9. 費用: JPY0(API 0)。所要時間。
10. 受入記録5項目(当初目的=ユーザー指示A-1原文逐語「mainへのmergeを正式に許可する(REGISTER #87:Go)。…mergeだけでタスク完了としない。」/最終成果物/証拠/一致・不一致/判定)。`PRODUCTION_WIRED`は宣言しない。
