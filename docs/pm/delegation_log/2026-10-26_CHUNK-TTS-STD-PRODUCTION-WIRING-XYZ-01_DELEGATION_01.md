## 管理ID

CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(案件A Phase 0+1a: ユーザー正式承認の保存→設計(Std 6%減速×Chunk分割+0.2秒の合成)→Opus条件A依頼文→**X/Y側の実装+遮断下test**。Z側(`er063`)の実装は別委任=`er063_family_z_audio_01.py`を並行AgentがPhase 1実装中のため本委任では**編集禁止・読取のみ**)。並行Agent: (1)FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02(所有=`er063_family_z_audio_01.py`・`er012_b_family_voices_production_01.py`・`er003_v1_n3_01_tts_generate.py`・`er122_*`・`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`・SSOT[DECISION_LOG/OPEN_ITEMS/OPUS台帳]・`docs/pm/ACTIVE_TASK.md`) (2)KP-GATE-EXCLUSION-RESCUE-DESIGN-02(所有=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`、`er123_*`、KP系は読取のみ)。本委任の所有=`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/**`、`er117_chunk_tts_production_01.py`(共通規則のレベル条件のみ)、`er019_family_x_audio_production_runner_01.py`(X Std配線)、`er121_family_y_structure_01.py`/`er121_family_y_audio_01.py`/`er121_family_y_runner_01.py`(Y Std配線)、対応test(`er117_*_test_*`、`er019_*chunk*_test_*`、`er121_*chunk*_test_*`)、`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_*`、`docs/pm/RESULT_PACKET_CHKW1.md`。**SSOT・ACTIVE_TASKは編集しない**(文案のみ)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式承認(APPROVED_FOR_PRODUCTION、2026-10-26、下記原文)のProduction配線。目標PRODUCTION_WIRED(XYZ各レベル)。本委任の到達上限=X/Y Std: IMPLEMENTED_PENDING_EVIDENCE、Z Std: DESIGN_READY(実装は次委任)。**PRODUCTION_WIREDとは書かない**(runtime evidence後にFable判定)。
- ユーザー明示: 「Standardを除外することは認めない。」「今回の明示承認に従い、ユーザーへの再確認を求めず是正すること。」「コード配線済み・テストPASSだけで、実際には確認できていないruntime evidenceを取得済みと扱わないこと。」
- 禁止: 有料API 0(本委任。runtime evidenceは次委任)/新しい分割規則(文境界分割・語数閾値変更・Y本文契約変更)の追加禁止/X/Z Advの既存挙動を変えない(Advの分割計画・0.2秒・chunk数が既存runでバイト同一になるtest)/`er063`編集禁止/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。
- 修正範囲の線引き(11-8): 範囲内=承認済み規則(X: 段落境界B0.2/Z: 約70語目安の段落境界B_r1/Y: X方式、いずれも+0.2秒)をStandardへ同一条件で適用し、Std 6%減速との合成を既存の承認済み減速仕様(`verify_std_english_slowdown`・減速率6%・ASR再検証)を変えずに設計・実装すること。範囲外=分割規則・減速率・ポーズ長の変更、文境界分割、Y本文契約変更。
- Opus独立技術レビューGate(11-3): **条件A該当**(Std減速×Chunk分割の合成=新しい処理フロー)。本委任で`OPUS_REVIEW_REQUEST_01.md`を作成し、**設計(DESIGN_01)確定後・実装前にRESULT_PACKET(中間)で報告してFableのOpus起動を待たず、設計をそのまま実装してよいのは次の条件を満たす場合のみ**: 合成方式が「chunkごとに既存の減速処理をそのまま適用→0.2秒無音を挿入→連結」(=減速後のポーズ長を0.2秒に保つ、既存減速検証をchunk単位で通す)で、新規の後処理・閾値を導入しない場合。それ以外(連結後減速・ポーズ補正係数等)は実装せずSTOPしFableへ。Opusレビューは実装後でも内容が変わらなければ再利用可(11-3)。
- 時間見込み: 2.5〜3.5時間(承認保存+設計45分、X Std実装+test 60分、Y Std実装+test 45分、evidence計画・費用 20分)。並列化: 案件Bと並列。本委任内はX→Yの直列(共通規則er117の変更をXで固めてからY)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約214/残約786/本委任JPY0/承認区分: C。Phase 2(runtime evidence: X Std 1記事3 part・Y Std/Adv複数段落入力1 segmentずつ・Z Std長narrator 1〜2 clip)の見積はBUDGET_PLAN_01で算定(出典ある単価のみ: X Adv TTS 2.51〜2.64円/記事[CURRENT_SPEC.md:2946]、Y 約2.92円/take[FAMILY-Y-FEEDBACK BUDGET_LOG_01]、Z tell_tale全体16.67円上限目安)。Guardrail案100円(300円超なら報告)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。(本委任は実TTSなし。Phase 2コマンド案には明示)
T-3: 本委任はCapなし(JPY0)。有料API呼出が必要と判明したら実行せずSTOP。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 638 --out docs\pm\delegation_log\2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_DELEGATION_01.md`(先頭が「## 管理ID」+「CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01」でなければ634〜650を順に試す)→check実行。
ユーザー原文保存: 下記「ユーザー指示(原文)」の全文(「# 【正式指示】Chunk分割 XYZ Production Wiring ＋ …」から「…実際に機能する救済方式を完成させること。**」まで、案件Bの節も含む)を一字も変えず`docs\pm\delegation_log\2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`へ保存(先頭に`<!-- ユーザー正式指示原文(2026-10-26)。逐語。案件A/B共通原文。Fable委任_01同梱の写しから転記 -->`の1行可)。

## ユーザー指示(原文)

# 【正式指示】Chunk分割 XYZ Production Wiring ＋ Key Phrase Gate除外救済方式の再設計

## 1. 今回の決定・目的

以下の2案件を並列で進めてください。

**案件A：Family X/Y/Z Chunk分割のProduction Wiring完了**

ユーザーの承認意図と異なり、Standardが対象外になっていた問題を是正する。

**案件B：Key Phrase Gate除外救済方式の設計やり直し**

前回の「除外11件中4件救済可能」という報告では、除外原因を十分に解決できておらず、ユーザーが求めた設計成果に到達していない。

原因究明→設計→検証を自律的に繰り返し、救済可能な候補を最大限残せる方式を完成させる。

独立作業は並列化し、品質を守りながら最速で進めること。

---

## 2. 案件A｜Chunk分割の正式Production Wiring

### ユーザー正式承認仕様

| Family | 分割方式 | 追加ポーズ | 対象 |
|---|---|---|---|
| X | 段落境界分割（Trial B0.2） | 0.2秒 | Standard／Advanced |
| Y | Family Xと同じ | 0.2秒 | Standard／Advanced |
| Z | 約70語を目安とした段落境界分割（B_r1） | 0.2秒 | Standard／Advanced |

**Status：APPROVED_FOR_PRODUCTION**
**目標：PRODUCTION_WIRED（XYZ各レベル）**

Standardを除外することは認めない。

### 問題の位置づけ

ユーザーがStandardの除外を指示・承認していないにもかかわらず、Fable/Sonnet側の設計判断で対象外とし、その判断を明示せずProductionへ配線していた。

これは単なる技術的問題ではなく、PM Gate・承認管理の不備である。

今回の明示承認に従い、ユーザーへの再確認を求めず是正すること。

### 実施事項

1. 承認済みTrial B0.2／B_r1の規則を維持し、Standardにも正式適用する。
2. Standardの既存6%減速とChunk分割・0.2秒ポーズの合成を適切に設計する。
3. 初回Production生成、retry、fallback、regeneration、resumeへ一貫して反映する。
4. 各Family／各レベルの正式runtimeで、分割位置・Chunk数・追加ポーズの発火証拠を取得する。
5. 必須Validator・音声QA・統合テスト・Regressionを実施する。
6. Fable独立レビューを経て、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを更新する。
7. X/Zで既に確認済みのAdvanced動作を回帰させない。

実装方法を過度に固定せず、既存の正式モジュールを最大限再利用すること。

### Family Yの注意事項

Yの各Voice本文は現在1段落のため、段落境界分割が実際には発動しないことが確認されている。

今回の承認は**Family Xと同じ段落境界分割方式のStd/Adv共通採用**であり、文境界分割や本文契約の変更を追加承認したものではない。

したがって、Yで分割対象となる段落構造を持つ入力に対して正式経路が正しく発火することを検証し、実記事が1段落のため不発火ならその事実を記録する。

**コード配線済み・テストPASSだけで、実際には確認できていないruntime evidenceを取得済みと扱わないこと。** Gate 3の必須条件が欠ける場合は、未確認事項を明示する。

### 再発防止

Family共通仕様や対象レベルをAI側の判断で狭める場合は、今後必ずユーザー承認を得る。

「TrialではAdvancedのみだった」という事実だけで、正式Production採用の対象レベルまで限定しないこと。

---

## 3. 案件B｜Key Phrase Gate除外救済方式の再設計

**Status：USER_DECISION_REQUIRED（設計・検証段階）**
**今回の到達目標：完成した設計案と実証結果の提出**

Productionへの新規則採用は、ユーザー判断前に行わない。

### 根本目的

Key Phrase候補を抽出した後、Gate違反を理由に機械的に捨てるのではなく、**適切に修正できる候補は救済してHuman Reviewに残す。**

候補数8件を無理に埋めることが目的ではない。

また、学習価値の最終判断はユーザーが行う。AIが主観的な学習価値判断で救済可能な候補を過度に捨てないこと。

### ① 原因究明

前回の除外11件を、候補ごとに一件ずつ再調査する。

各候補について以下を確認する。

- 元の本文
- AIが提案した候補
- Gate除外の直接原因
- 原因となる規則・コード条件
- その条件のユーザー承認履歴
- 実際に品質上の問題があるのか、実装制約による過剰除外なのか
- 修正可能性

さらに同種の除外が他にないか確認し、パターンを整理する。

**「11件中4件救済可能、残り7件は不可」という分類を結論として固定しないこと。**

残り7件についても、原因を分析し、具体的な救済方法を検討する。

### ② パターン別の修正方式を設計

代表例：

**A. 語数超過**

`too soon to wave a flag`

例として `too soon to do` のような一般化が考えられる。

本文にない語を使う一般化については、現行規則との衝突・意味保持・品質リスクを検討し、具体的な救済方法を設計する。

単に「現行規則違反だから不可」で止めないこと。

**B. 原形への正規化**

`studied separately` → `study separately`

動詞直後が副詞であることを理由に原形化を禁止する内部条件について、その必要性・承認根拠・副作用を調査する。

適切な原形化を認める修正方式を設計・検証する。

誤った原形を作るリスクには必要十分な検査を設ける。

**C. 助動詞と一般動詞の誤判定**

`have a say`

一般動詞のhaveを助動詞と誤認して除外しているなら、文法的な役割に応じて区別できる方式を設計する。

**D. 本文との不一致・一般化・その他**

既存の過剰拡張、活用形、人称一般化、重複、発音辞書、Human Review NG等を区別し、それぞれについて救済可否を検討する。

品質や安全上、救済すべきでない候補を無理に復活させない。

### ③ 原因究明→設計→検証の自律ループ

単に修正案を列挙するだけでは不十分。

各パターンについて次を行う。

1. 除外原因を特定
2. 救済方法を設計
3. 既存の実例で修正候補を生成・再導出
4. 既存Gateで再検証
5. 本文対応・意味保持・自然な英語・重複・gloss整合を評価
6. 不合格なら原因を分析し、設計を改善
7. 効果が見込める範囲で再検証
8. 十分な品質に到達したら終了

同一方向の無益なTrial反復を避け、必要なら手法を変更すること。

既存データ・ローカル検証を優先し、追加API費用を最小化する。

### ④ ユーザー判断が本当に必要なものだけ抽出

各改善案を次の3区分に分ける。

**区分1：承認済み仕様への準拠修正**

既存ルールの意図に反する過剰除外や実装不具合を修正するもの。

仕様変更を伴わず、既存の委任・予算範囲内なら自律的に解決する。

ただし今回の新しい候補救済フロー全体を、正式採用前に無断でProductionへ配線しない。

**区分2：既存ルール変更が必要で、ユーザー判断を要するもの**

本文にない語への一般化、許容する形態変化の拡張など。

検証した修正例、メリット、品質リスク、代替案、QCD影響、推奨案を示して判断を求める。

**区分3：救済すべきでないもの**

意味が変わる、不自然な英語になる、出典との対応が失われる、明示的なHuman Review NGを覆す等。

除外する合理的理由を示す。

単にコードで対応が難しいという理由だけで区分3にしないこと。

### ⑤ 検証成果物

少なくとも、除外された11件すべてについて以下の表を完成させる。

| 元候補 | 除外原因 | 修正候補 | 検証結果 | 救済可否 | 規則変更の要否 |
|---|---|---|---|---|---|

加えて、パターン別の汎用修正方式、実装設計、品質リスク、追加コスト、期待救済率を提示する。

救済候補の修正履歴、gloss、QA、Human Reviewへの引渡しが一貫するよう設計する。

救済後の候補も既存の必須品質Gateを通過させる。

### ⑥ Fable・Opusレビュー

前回のOpusレビュー指摘を活用し、同じ論点のレビューを無駄に繰り返さない。

設計が実質的に変わった部分は、必要な独立レビューを行う。

Fableは、11件の原因分析・修正方法・検証結果・規則変更要否を独立照合する。

不十分ならユーザーへ未完成案を転送せず、委任範囲内で設計を改善すること。

---

## 4. QCD・承認境界

両案件とも品質 ＞ Delivery ＞ 量産単価。

- Family共通部分はX/Y/Zの整合を維持する。
- 承認済み品質基準を独断で緩和・厳格化しない。
- 不要な再生成・有料Trial・日付分割を避ける。
- 量産単価70円／記事セットへの影響を評価する。
- 開発費は既存の個別承認枠および原則1,000円／日（JST）の上限を遵守する。
- 仕様変更が必要な場合はユーザー承認を得る。
- 既存の重大なSTOP条件・安全条件を維持する。

## 5. 完了条件と最終報告

### 案件A

**目標：Family X/Y/ZのStandard／AdvancedすべてでPRODUCTION_WIRED。**

Family×レベル6行の表で、承認仕様・実装・正式runtime・必須テスト・最終Statusを報告する。

不発火と配線漏れを区別し、未確認のGate条件を隠さない。

### 案件B

**目標：再設計・実例検証・Fable受入まで完了し、真に必要なユーザー判断だけ提示する。**

除外11件すべての個別結果を省略せず報告する。

救済率だけを結論にせず、どの候補が、どう修正でき、なぜ救済できる／できないのかを示す。

**今回の最重要指示：案件Aはユーザー承認を正しくProductionへ反映して完了させること。案件Bは問題を分類して報告するだけでなく、原因究明→設計→検証の自律ループで、実際に機能する救済方式を完成させること。**

## KPI provenance欄

該当なし(本委任は実装+offline test。runtime evidenceは次委任でfresh/production_formal_pathとして取得)。

## Opus台帳更新

関連: 前回Chunk配線時のOpus指摘(`docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `CHUNK|chunk`→該当なしだった[監査結果]。`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md`に指摘があればM/R番号を引用し、Std適用で維持すべき点をDESIGN_01に記す)。台帳編集なし。

## Fableからの前提・既知事実(監査CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01の結果。再検証のうえ使用)

- X: `er117_chunk_tts_production_01.py:90-93`「段落2未満は分割しない」。X Std=chunk経路なし(`er019_family_x_audio_production_runner_01.py:1743`)、testでStd除外を固定(`er117_x_chunk_wiring_test_01.py:194-213`→この固定は撤去対象)。X Adv=`er019:1443-1547`配線済み・実発火(uk_train 10 chunk・0.2秒7箇所)。X Stdの3 partは123〜170語(複数段落)で分割対象が実在。
- Z: `er117:143-144`の`level != "b1b"`で除外。Z Adv=`er063:585-600,1402-1458`。Z Stdの100語超narratorが4 clip残存(tell_tale 129/139語、melos 134語、gift_of_the_magi 122語)。**Z側の実装(er063)は次委任**。本委任ではer117のレベル条件撤去がZにも効く場合の影響(er063の呼出がStdでも動くか、Z Std減速との合成)をDESIGN_01に設計として書き、er117変更がZ Advをバイト同一に保つtestを置く。er117のレベル条件をZ向けに撤去するとZ Stdが即時発火する場合は、Z側の減速合成が未実装の状態で発火させないため、**er117側はX/Y向けの条件撤去に限り、Z向け条件は次委任で撤去**(その旨を明記)。
- Y: `er121_family_y_structure_01.py:111`で`("b1b",)`に限定(Xから継承、`DESIGN_02.md:211`)、`er121_family_y_audio_01.py:264-310,363-390`。Y本文は各Voice 1段落→不発火(正常)。Yは「複数段落の入力に対して正式経路が発火する」ことをtest+次委任のruntime(複数段落のdev入力1 segment、公開物を上書きしない)で示す。
- Std 6%減速: `verify_std_english_slowdown`、減速後ASR再検証、reuse_key、Gate(Grepで実装箇所特定)。Std減速とchunkの合成は未Trial(Phase 0除外の理由)。**Fable設計方針(既定)**: chunkごとにTTS→chunkごとに既存の減速処理+減速後検証(既存関数をそのまま適用)→0.2秒無音を挿入→連結。ポーズ長は減速の影響を受けず0.2秒のまま。連結後減速(ポーズが0.212秒になる)は採らない。既存の減速検証がchunk単位でも成立するか(語数・尺の下限等)をコードで確認し、成立しない場合はSTOPしてFableへ。
- 承認原文: `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md`、`..._FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md`、`..._FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md`、`docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/{APPROVAL_TRACE_01,WIRING_CHECK_01,RUNTIME_EVIDENCE_01}.md`(全文Read推奨、監査結果の正本)。

## 事前指定Read一覧

1. `docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/{APPROVAL_TRACE_01,WIRING_CHECK_01,RUNTIME_EVIDENCE_01,FIX_01}.md` 全文。
2. `er117_chunk_tts_production_01.py` 全文(共通規則module、構造変更を伴うため許可)。
3. `er019_family_x_audio_production_runner_01.py` :1400-1560(Adv chunk経路)、:1700-1780(Std経路)、Grep `slowdown|verify_std|a2|reuse_key|resume|regenerate|retry`→該当範囲。
4. `er121_family_y_structure_01.py` :90-130、`er121_family_y_audio_01.py` :240-420、`er121_family_y_runner_01.py` Grep `chunk|slowdown|a2`。
5. `er063_family_z_audio_01.py` :570-610, :1395-1460(読取のみ、Z設計用)。
6. Std減速実装: Grep `verify_std_english_slowdown|SLOWDOWN|0\.94|atempo|slowdown` in `er019_*.py` `er121_*.py` `er063_*.py` `er003_*.py` `er020_*.py`→該当関数全体。
7. test: `er117_x_chunk_wiring_test_01.py` 全文、Glob `er117*_test_*.py` `er019*chunk*_test_*.py` `er121*chunk*_test_*.py`。
8. `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/{WIRING_DESIGN_01,OPUS_REVIEW_01}.md` 該当節(Grep `a2|Standard|減速|slowdown`)。
9. `CURRENT_SPEC.md` Grep `Chunk TTS`→該当節±30行(:2939付近)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- SSOT編集なし。CURRENT_SPEC Chunk TTS節の修正文案・DECISION_LOGエントリ文案・OPEN-532更新文案をRESULT_PACKETへ。
- Adv不変の基準: 実装前に`git rev-parse HEAD`を記録し、X Adv既存run(`er019_output/.../uk_train*`等のaudit/chunk_tts_decision.json・chunk_plan_b1b.json)に対して分割計画関数を再実行した結果をgolden fixtureとして`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/golden/`へ凍結→実装後にバイト一致test。

## 実行コマンド全文

- 回帰(遮断下、変更前後): `$env:PYTHONPATH="netblock_harness_01"; py run_project_regression.py --pattern "er117*_test_*.py"`、同`"er019*_test_*.py"`、`"er121*_test_*.py"`(`--help`で実引数確認。`google.genai`未導入でImportErrorになるtestは前後で同一であることを記録。必要なら遮断下でmock可能か確認)。
- 新規test: `$env:PYTHONPATH="netblock_harness_01"; py -m pytest er117_std_chunk_wiring_test_01.py er019_x_std_chunk_test_01.py er121_family_y_std_chunk_test_01.py -q`(実名に合わせる、`_test_`必須)。
- Z不変: `git diff --stat -- er063_family_z_audio_01.py`(本委任由来の差分0。並行Agentの差分が出る場合はその旨記録し触れない)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。
- Phase 2コマンド案(実行しない、実値で記載): 例 `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug uk_train_manners --run run_stdchunk_ev_01 --level a2 --stage tts --budget-jpy 20`(slug/runは実在名・新規run名で。公開物を上書きしない)。

## 成果物(`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/`)

1. `SPEC_LEDGER_01.md`: ユーザー原文§2を要求項目に分解(ID/逐語/実装先/検証/Status)。再発防止条項(対象レベル限定はユーザー承認必須)を記録。
2. `DESIGN_01.md`: (a)共通規則er117のレベル条件の扱い(X/Y向け撤去、Z向けは次委任) (b)Std減速×chunk合成(既定方針、既存関数の適用順、ポーズ0.2秒保持、減速後検証のchunk単位適用、reuse_key、retry/fallback/regeneration/resumeでの一貫性) (c)X Std配線設計(Adv経路の再利用) (d)Y Std配線設計(`("b1b",)`→両レベル、複数段落入力でのみ発火、実記事は不発火=正常) (e)Z Std設計(er063変更点の提示のみ、実装は次委任) (f)Adv不変保証(golden) (g)Phase 2 evidence計画(X Std 1記事・Y Std/Adv複数段落dev入力・Z Std 1〜2 clip。正式経路・新規run dir・公開物不変・発火証拠=chunk_tts_decision/chunk_plan/0.2秒位置/TTS call数) (h)CURRENT_SPEC/DECISION_LOG文案。
3. `OPUS_REVIEW_REQUEST_01.md`(条件A: 減速×chunk合成、retry/resume一貫性、Adv不変、Y不発火の扱い、Z次委任との整合)。
4. `BUDGET_PLAN_01.md`(Phase 2見積、Guardrail文言、300円判定)。
5. 実装: er117(X/Y向けレベル条件)・er019(X Std)・er121(Y Std)+test群。`FIX_01.md`に差分要約。
6. `docs/pm/RESULT_PACKET_CHKW1.md`。

## SSOT追記文

文案のみ(RESULT_PACKETへ): CURRENT_SPEC Chunk TTS節「Std対象外」記述の是正文、DECISION_LOG(ユーザー正式承認2026-10-26 APPROVED_FOR_PRODUCTION Std/Adv、Phase 1a実装)、OPEN-532更新。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。ACTIVE_TASK編集なし。
- commit 2分割: (1)設計+ユーザー原文+golden (2)実装+test。明示add(pathごと)。
- message例: (1)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: ユーザー正式承認(Std/Adv・APPROVED_FOR_PRODUCTION)保存+Std減速×Chunk合成設計+Opus依頼文+golden(API 0)` (2)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: X/Y StandardへChunk分割+0.2秒を配線(er117レベル条件撤去[X/Y]、Adv golden一致、test N PASS、API 0、IMPLEMENTED_PENDING_EVIDENCE)`。
- `git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(X/Y Std=IMPLEMENTED_PENDING_EVIDENCE/Z Std=DESIGN_READY、合成方式が既定方針どおりか・STOP有無) (2)6行表(承認仕様/実装/runtime/必須test/Status。runtime列は本委任時点「未取得」) (3)設計要点(減速×chunk合成・一貫性) (4)test結果(新規N、既存前後、Adv golden一致、接続試行0) (5)Z次委任への引継ぎ(er063変更点・er117 Z条件) (6)Phase 2計画・費用 (7)SSOT文案 (8)commit×2・raw URL (9)一覧外Read (10)Fable向け懸念(Opusに重点確認させたい点)。最終行に要約10行以内。