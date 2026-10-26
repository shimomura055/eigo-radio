## 管理ID

KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01(案件B: 除外11件の一件ずつ再調査→パターン別救済方式の設計→既存実例での再導出・既存Gate再検証→不合格なら設計改善、の自律ループ。DEV実装(Production非配線)で実証し、区分1/2/3へ分類。到達目標=完成した設計案と実証結果)。並行Agent: (1)FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02(所有=er063/er012_b/er003_n3/er122_*/SSOT/ACTIVE_TASK) (2)CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01(所有=er117/er019/er121 chunk、`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/**`)。本委任の所有=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`、新規DEV module `er123_kp_rescue_dev_01.py`(+test)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_*`、`docs/pm/RESULT_PACKET_KPRS3.md`。**KP Production code(`er105_kp_fulltext_selector_01.py`、`er003_key_words_canonicalization.py`、`er003_key_words_min_unit.py`、`er119_*`、`er003_v1_n3_01_scaffold_generate.py`)は編集禁止(読取・import・DEVでの呼出のみ)。SSOT・ACTIVE_TASKは編集しない。**

## 性質/到達上限Status/禁止事項

- 性質: 設計・検証(DEV)。前回KP-GATE-EXCLUSION-RESCUE-DESIGN-01(DESIGN_02、Opus M1〜M6/R1〜R4反映済み)のやり直し。ユーザー原文: 「前回の『除外11件中4件救済可能』という報告では、除外原因を十分に解決できておらず」「『11件中4件救済可能、残り7件は不可』という分類を結論として固定しないこと」「単に『現行規則違反だから不可』で止めないこと」「単にコードで対応が難しいという理由だけで区分3にしないこと」。
- 到達上限Status: 設計=COMPLETED_PENDING_FABLE_ACCEPTANCE→Fable受入後USER_DECISION_REQUIRED(区分2のみ提示)。**Productionへの新規則採用・救済フロー配線は行わない。** 区分1(承認済み仕様への準拠修正)に該当するものも、本委任ではDEV実証+修正差分案まで(Production適用はFable判断・別委任)。
- 禁止: Production code編集禁止/AI島run_ai_01のHR候補を確定・変更しない(`status`のみ)/`er0XX_output/`書込禁止/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。
- 費用: 原則API 0(既存データ・ローカル検証優先)。**自然さ・意味保持・gloss整合の判定でLLM判定が必要な場合のみ**、`.venv\Scripts\python.exe`で最小限の呼出を許可: 「上限¥30(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」呼出前に`py tools/stop_scope_check_01.py`、モデルは最新世代推奨系(PM_GOVERNANCE 25節、使用モデル名を記録)、費用は`raw_usage_log`相当に記録。LLM判定は「評価」にのみ使い、救済候補の生成自体は決定論を優先(LLM生成が必要なパターン[語数超過の一般化等]はそれ自体を設計の一部として明示)。
- 修正範囲の線引き(11-8): 区分1=承認済み規則の意図に反する過剰除外・実装不具合の是正(例: 規則文に無い内部条件、閉表の網羅漏れ、助動詞誤判定)。区分2=受理面の拡大(本文に無い語への一般化、許容形態変化の拡張)。本委任は分類と実証まで。
- Opus独立技術レビューGate(11-3): 前回Opusレビュー(`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md` M1〜M6/R1〜R4)を前提として設計に組み込み、**設計が実質的に変わった部分**(新規: 副詞前原形化の検査設計、lexical have判定、語数超過の一般化方式、cmu_post_canon/構造違反へのトリガー拡張)だけを対象に`OPUS_REVIEW_REQUEST_02.md`を作成(Fableが起動)。
- 時間見込み: 3〜4時間(11件再調査60分、パターン設計+DEV実装90分、検証ループ60分、文書30分)。並列化: 案件Aと並列。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約214/残約786/本委任見積JPY0〜30/承認区分: A(Fable判断可)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。上記定型文に従う。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 639 --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_DELEGATION_01.md`(先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01」でなければ634〜650を順に試す)→check実行。
ユーザー原文: 全文は並行Agent(案件A)が`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`へ保存する。本委任は下記「ユーザー指示(原文)」節(案件B関連の§1・§3・§4・§5案件Bの逐語)を一字も変えず`docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_USER.md`へ保存(先頭に`<!-- ユーザー正式指示原文(2026-10-26)のうち案件B関連節の逐語抜粋。全文は 2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md -->`の1行可)。

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

### 案件B

**目標：再設計・実例検証・Fable受入まで完了し、真に必要なユーザー判断だけ提示する。**

除外11件すべての個別結果を省略せず報告する。

救済率だけを結論にせず、どの候補が、どう修正でき、なぜ救済できる／できないのかを示す。

**今回の最重要指示：案件Aはユーザー承認を正しくProductionへ反映して完了させること。案件Bは問題を分類して報告するだけでなく、原因究明→設計→検証の自律ループで、実際に機能する救済方式を完成させること。**

## KPI provenance欄

救済率・再検証結果=reuse(既存ログ)+synthetic(DEV再導出)。LLM評価を使う場合はfreshとして件数・費用を分離。E2E自己確認=No。

## Opus台帳更新

該当なし(編集はFable側のSSOT委任で)。前回OF-KPRS-M1〜M6/R1〜R4は設計に組み込み、DESIGN_01 §0に「前回Opus指摘の反映状況」表を置く。

## Fableからの前提(前回成果。再検証のうえ使用。前回の分類に縛られない)

- 前回成果物: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/{SPEC_CHECK_01,EXCLUSION_PATTERNS_01,RESCUE_ANALYSIS_01,DESIGN_01,DESIGN_02,OPUS_REVIEW_01}.md`、`inventory_01.json`、`recheck_01.json`、`rescue_candidates_01.json`、`tools/kp_exclusion_inventory_01.py`(再利用可)。
- 11件(HR導入後、Human NG 3件除く): X `too soon to wave a flag`(6語)、X `studied separately`(guard: 直後が副詞)、X `had our eye on`(有限助動詞リスト=lexical have)、Z `rose above`→LLM`rise above the other voices`(範囲拡張)、Z `held out`→`hold out one's hands`(同)、Z `rang through`(過去形専用表に`rang`無し)、Y `it can't be helped`/`can't be helped`(助動詞リスト)、Y `redelivery fee`(CMU未登録)、Y `have a say`(lexical have)、Y `catch their interest`(本文に連続一致しない)。
- 重要な事実: 「動詞直後が副詞なら原形化しない」guard(`er105_kp_fulltext_selector_01.py:662 _guard_ok`、`_GUARD_DET:614`)はCURRENT_SPEC.md:1997の承認文(「先頭またはto直後の動詞・最終語の複数形、除外表あり」)にもOpus P-04原文にも無い実装判断(コードコメント:570-575「V+名詞等は基本形化しない」)。承認済み規則=Rule7(source_spanに無い別の辞書形を勝手に生成しない)、人称一般化例外(閉表1対1)、活用形→基本形例外(X/Z限定、1対1トークン置換、CMU実在)、5語以下、本文連続一致、有限助動詞拒否(`er003_key_words_min_unit.py:260` `_FINITE_AUX_WORDS`、承認経緯を調べる)、CMU代替合格禁止(CURRENT_SPEC.md:2001)、数合わせ禁止・最大8、NG復活禁止。
- 前回Opus M1: 機械的再導出はLLM提案語の部分集合に限定(hoped→hopのような非提案語形を作らない)。今回「副詞前の原形化を認める」場合、原形はLLMが提案した`study`であること+CMU実在+活用表(規則/不規則)での逆引き一致、の三重検査を基本とし、必要十分な検査を設計する。
- 語数超過`too soon to wave a flag`→`too soon to do`: 本文に無い`do`を生成し`wave a flag`を削る。現行Rule7と衝突。設計では(a)「本文連続部分列への短縮」(決定論・現行規則内、意味反転リスク=`too`削除禁止等の決定論禁止表で歯止め)、(b)「スロット一般化(目的語句→do/something/someone)」(新規則=区分2。生成はLLM提案+決定論検査[元句の冒頭連続部分列+一般化スロット1個以内、否定・程度語の削除禁止、CMU実在]、HR表に元句と本文文を併記)、の両方をDEVで実証し、区分2としてユーザーに判断材料を出す。「現行規則違反だから不可」で止めない。
- lexical have: `have a say`/`had our eye on`/`have a big moment`。設計案: 直後トークンが限定詞・所有格・数量詞・名詞句ならlexical(受理)、直後が過去分詞/`been`/`to`なら助動詞(拒否)等の決定論判定+LLM提案との一致。既存の`_FINITE_AUX_WORDS`の承認経緯(なぜhaveを含めたか)を確認し、区分1(誤判定の是正)か区分2(受理面拡大)かを判定根拠付きで分類。
- `can't be helped`: 法助動詞+受動の慣用句。承認済み「有限助動詞拒否」の意図(「文の一部を切り出した不自然な学習単位を避ける」等)を調べ、慣用句として成立するものを区別できるか(例: 辞書形`can't be helped`は慣用表現として自立)を検討。区分2候補か区分3か、根拠を示す。
- `redelivery fee`: CMU未登録語の扱いは承認済み(代替合格禁止)。ただし「`redelivery`=`re`+`delivery`の派生語で発音は合成可能」等の救済余地があるかを調べ、承認規則の意図(TTS発音の安全)に照らして区分2か区分3か判定。
- `catch their interest`: 本文の実表現を特定し(Y SNS年齢制限記事)、「本文の近傍表現へ戻す」決定論(編集距離・語順・活用の範囲内で本文の連続スパンを探索)で救えるかDEV検証。
- `rose above`/`held out`: LLMが範囲拡張。前回S1(再導出)。M1制限(display窓内でdisplay語かLLM提案語から選ぶ)で`rise above`/`hold out`が実際に通るかをDEVで実証(前回は机上)。
- `rang through`: 過去形専用表の網羅漏れ→区分1候補(表の補完)。不規則動詞表の網羅性を確認し、同種の漏れを列挙。
- 検証データ: `er019_output/.../ai_island_temple__run_ai_01/{a2,b1b}/key_phrases/`、Y `er121_output/family_y_production_01/{redelivery_fee,sns_age_limit}/run_01/*/key_phrases/`、Z `er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r{3,4}/`等(前回inventoryのpathを使う)。保存済みのparsed LLM応答(`kp_candidates.json`/`canonicalization_runtime_metadata.json`等)を入力に、DEV moduleで救済→既存validator関数(`validate_canonicalization_*`、CMU、`_containment`、Redundancy QA判定関数)を**同一引数**(前回Opus M6)で再適用。

## 事前指定Read一覧

1. 前回成果物(上記)全文: DESIGN_02、RESCUE_ANALYSIS_01、OPUS_REVIEW_01、EXCLUSION_PATTERNS_01 §1〜§4。
2. `er105_kp_fulltext_selector_01.py`: Grep `_guard_ok|_GUARD_DET|_verb_base_candidates|_token_pair_ok|postprocess_possessor_roles|run_canonicalization_gate|IRREGULAR|past|_PAST`→該当関数全体(:560-700, :800-840, :900-1000)。
3. `er003_key_words_canonicalization.py` :520-720(validator本体)。`er003_key_words_min_unit.py` :240-290(`_FINITE_AUX_WORDS`とその使用箇所)。
4. `er119_kp_candidates_01.py` :80-110, :250-360。`er003_v1_n3_01_scaffold_generate.py` :500-560(canonicalization hook・gloss)。
5. 承認履歴: `CURRENT_SPEC.md` :1990-2003、Grep `有限助動詞|finite|助動詞`、`DECISION_LOG.md` Grep `有限助動詞|_FINITE_AUX|Rule7|P-04`→該当行、`docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/OPUS_REVIEW_COND_A_01.md:100-130`、delegation_log Grep `助動詞|原形|辞書形` in `docs/pm/delegation_log/*_USER*.md`。
6. 実データ: 11件の各run `kp_candidates.json`(`dropped[]`・`raw`応答)、`canonicalization_runtime_metadata.json`、本文(`article.md`/`segment_plan`)。
7. `tools/stop_scope_check_01.py --help`(LLM評価を使う場合)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- SSOT編集なし。OPEN-529更新文案・DECISION_LOG文案をRESULT_PACKETへ。
- 新規OPEN番号は発番しない(OPEN-529を継続使用)。

## 実行コマンド全文

- 保全確認(前後): `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`。
- DEV検証(API 0、`py`。既存validator importでopenai moduleが連鎖読込されるため、前回と同様script冒頭で`socket.connect`を例外化): `py er123_kp_rescue_dev_01.py --inventory docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\inventory_01.json --out docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\rescue_eval_01.json --md docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\RESCUE_TABLE_01.md`(ループ各回で`rescue_eval_0N`と改訂履歴を残す)。
- DEV test(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py -m pytest er123_kp_rescue_dev_01_test_01.py -q`(非提案語形を作らない・否定/程度語削除禁止・同一引数再検証・X/Y/Z区別・NG復活禁止)。
- LLM評価(使う場合のみ、各回前に`py tools/stop_scope_check_01.py`): `.venv\Scripts\python.exe er123_kp_rescue_dev_01.py --judge docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\rescue_eval_0N.json --budget-jpy 30 --out docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\judge_01.json`。
- Production不変: `git status --short -- er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py er003_key_words_min_unit.py er119_kp_candidates_01.py er119_kp_human_review_01.py er003_v1_n3_01_scaffold_generate.py`(差分なし)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。

## 成果物(`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/`)

1. `CASE_ANALYSIS_01.md`: 11件を一件ずつ(元本文の該当文/AI提案/除外の直接原因/規則・コード条件[ファイル:行]/その条件のユーザー承認履歴[出典行、または「承認文なし=実装判断」]/品質上の実問題か過剰除外か/修正可能性)。同種除外の他例(前回inventoryのpreHR 29句から)。
2. `PATTERN_DESIGN_01.md`: パターンA(語数超過: 連続部分列短縮[現行内]+スロット一般化[区分2])/B(副詞前原形化: guardの必要性・承認根拠・副作用、三重検査設計、誤原形リスクの検査[CMU実在+活用逆引き+LLM提案一致+POS文脈])/C(lexical have判定)/D(範囲拡張の再導出[M1制限]、人称一般化、過去形表補完、本文近傍探索、CMU派生語、法助動詞慣用句、Human NG=復活しない)。各々: 決定論/LLM区別、再検査(既存Gate同一引数)、gloss/QA/HR引渡し(前回M3/M4)、HR経路限定(前回M2)、外側retry現行維持(前回M5)。
3. `er123_kp_rescue_dev_01.py`(+test): 上記パターンの救済をDEV実装し、11件+同種例に適用→既存validator再検証→本文対応・重複・gloss整合(gloss不一致は`gloss_hr_pending`)・自然さ(決定論チェック+必要ならLLM判定≤30円)を記録。ループ: 不合格→原因→設計改善→再実行(各回の結果と変更点を`LOOP_LOG_01.md`に)。終了条件=「各パターンで救済可能な候補が既存Gateを通過し、区分3の理由が品質・安全根拠で書けた」。同一方向の無益な反復禁止。
4. `RESCUE_TABLE_01.md`: ユーザー指定6列×11行(+同種例)。各行に「なぜ救済できる/できないか」。
5. `DESIGN_01.md`: 汎用修正方式・実装設計(Production配線時の差分案、前回DESIGN_02との差分)・品質リスク・追加コスト(出典ある単価のみ)・期待救済率(11件および一意句29での再計算)・区分1/2/3一覧(区分2は検証済み修正例・メリット・リスク・代替案・QCD・推奨付き)。
6. `OPUS_REVIEW_REQUEST_02.md`(設計が実質変わった部分のみ)。
7. `docs/pm/RESULT_PACKET_KPRS3.md`。

## SSOT追記文

文案のみ: OPEN-529更新(DESIGN-02成果、区分1/2/3)、DECISION_LOG(Fable受入後)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- 明示add: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`、`er123_kp_rescue_dev_01.py`、`er123_kp_rescue_dev_01_test_01.py`、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_{USER,DELEGATION_01}.md`+`_check.json`。
- commit: `git commit --only <paths…> -m "KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01: 除外11件の個別再調査+パターン別救済方式のDEV実証(副詞前原形化/lexical have/語数超過一般化/本文近傍探索ほか、既存Gate同一引数再検証、Production非配線、API <X>円)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(11件の最終分類: 救済可[区分1/区分2]件数と区分3件数、根拠) (2)RESCUE_TABLE転記(11行全て) (3)パターン別方式の要点と検証ループの回数・改善内容 (4)guard(副詞前原形化禁止)の必要性・承認根拠・副作用の結論 (5)lexical have判定の設計と区分 (6)語数超過の2方式の実証結果(連続部分列/スロット一般化)と意味反転の歯止め (7)区分2の判断材料(各案: 修正例・メリット・リスク・代替・QCD・推奨) (8)費用(LLM判定の有無・実費・モデル) (9)保全・Production不変証拠 (10)commit/push・raw URL (11)一覧外Read (12)Fable向け懸念(未解決・Opusに確認させたい点)。最終行に要約10行以内。