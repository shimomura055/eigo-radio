## 管理ID

KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01(ユーザー正式採用 APPROVED_FOR_PRODUCTION 2026-10-26: Key Phrase Gate除外救済方式のProduction実装設計の確定+DEV実装+test。Production配線とruntime evidenceはOpusレビュー後の委任_02)。並行タスク衝突確認: 並行Agent 1件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02[read-only統合])。直後にFAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_02(`er121_*`・`er121_output/`・`user_test/`)が走る可能性あり=あなたはそれらに触れない。あなたの所有=`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/**`、`er123_kp_rescue_dev_01.py`(DEV module、拡張可)、`er123_kp_rescue_dev_test_01.py`(存在すれば拡張)、新規`er125_kp_rescue_production_01.py`(Production用module。**本委任ではProductionファイルからimportしない**=未配線)、`er125_kp_rescue_production_test_01.py`、vendoring辞書データ(`data/kp_idiom_lexicon_01/`等、新規dir)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_KPRW1.md`。**本委任で編集禁止**: `er119_kp_candidates_01.py`、`er105_kp_fulltext_selector_01.py`、`er003_key_words_canonicalization.py`、`er003_key_words_min_unit.py`、`er119_kp_human_review_01.py`、`er119_kp_human_review_cli_01.py`、`er119_kp_prompt_2v_01.py`(配線は委任_02)。例外: 「既存仕様に反する実装条件4件」の残り1件(量化詞限定詞guard `no/each/every`、`accepts no responsibility`)は区分1(承認済み規則への準拠修正)として**`er105_kp_fulltext_selector_01.py`の該当guardのみ**編集可(先例=845cfcb0a、test+A/B/C golden不変+敵対的85件を同梱)。SSOT編集権なし。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: Production実装設計の確定+DEV実装+test(承認済み仕様の実装)。到達上限Status=DESIGN_FINAL+DEV_IMPLEMENTED(Production配線は委任_02、PRODUCTION_WIRED判定はFable)。
- **Opus独立技術レビューGate(11-3): 条件A該当**(Production経路へ「違反検出→修正→再検査→候補登録」の新フローを加える)。既存レビュー`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/OPUS_REVIEW_01.md`(M1〜M6/R1〜R4)と`…DESIGN-02/OPUS_REVIEW_02.md`で設計の大半はレビュー済み。本委任では**変更部**(①慣用句の一般機構[27件閉表→辞書/規則ベースの汎用判定]、②HRなし経路での救済候補の扱い、③既定ON化と対象経路、④retry/resume一貫性)を`OPUS_REVIEW_REQUEST_03.md`として抽出し、Fableが委任_02前にOpusへ依頼する。あなたはOpusへ依頼しない。
- 禁止: Production配線(上記ファイルのimport追加・既定挙動変更)、有料Trial(本委任はAPI 0。gloss再整合・QA再判定の実コストは委任_02のevidenceで計測)、承認済み品質規則の緩和、Human NG候補の復活、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用/日次: JPY0(本委任)。当日既使用約552円/残約448円。委任_02見積(evidence X/Y/Z各1 level-run×2レベル+gloss/QA再整合)=約20〜30円。
- 修正範囲の線引き(11-8): 範囲内=ユーザー採用表の実装(時制・活用形救済/慣用句救済の一般機構/既存仕様違反4件の是正[残り1件])とそのtest・golden。範囲外=5語超の短縮救済・本文にない語の追加・CMU分解救済・Gate緩和・新しい品質閾値。
- 時間見込み: 全体約3h(設計確定60分/慣用句機構の実装・辞書整備60分/DEV→Production module化+test 45分/敵対的・golden・315種回帰15分)。並列化: 辞書データ整備と救済フロー実装は独立→先に辞書の出典・ライセンス・件数を確定し、並行して実装。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_DELEGATION_01.md` をN=662から順に試し、先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01」で始まるものを採用(`--index -1`不可)。ユーザー指示原文(下記全文)を`..._USER.md`へ逐語保存。

## ユーザー指示(原文)

# Claude Codeへの指示｜Key Phrase救済方式のProduction完成・候補生成TrialのCloseout

## 1. 目的・到達目標

Family XYZ共通のKey Phrase品質改善を、ユーザー承認済みの方針に従って進める。

**今回の到達目標は2つ。**

1. **Gate除外救済方式：PRODUCTION_WIREDまで完了**
2. **候補生成Trial（フレーズ7件＋単語3件）：検証・Fable評価・結果報告まで完了**

候補生成Trialの結果を、無断でProduction採用しない。

最優先順位は **品質（Q）＞Delivery（D）＞量産単価（C）** とする。

## 2. Gate除外救済方式｜正式採用内容

**Status：APPROVED_FOR_PRODUCTION**
**対象：Family X／Y／Z共通、Standard／Advanced**

以下を正式Productionへ適用する。

| 項目 | ユーザー決定 |
|---|---|
| 時制・活用形 | 本文との対応を確認でき、正しく原形化できる場合は救済 |
| 慣用句 | 助動詞等の機械的判定で不当に除外される自然な慣用表現を救済 |
| 5語以下 | 制限維持。6語以上を意味のない短縮で救済しない |
| 本文にない語の追加 | 不採用 |
| 発音辞書未登録語の分解救済 | 不採用 |
| 既存仕様に反する実装条件4件 | 承認済み仕様に合わせて是正 |

**個別の5表現だけを例外登録するのではなく、同じ原因を持つ候補を救済できる一般的な仕組みとすること。**

品質Gateを緩和して不適切な候補を通すのではなく、本文との照合、適切な正規化、自然な慣用表現の判定によって救済する。

Humanが明示的にNGとした候補は、救済処理によって復活させない。

### 慣用句の実装方式

過去に提案された「27件の固定例外リスト」は、実装方式として正式承認されたものではない。

Claude/Fableが汎用性・品質・費用・保守性を評価し、承認済み範囲内で必要十分な方法を自律的に選ぶこと。

リストのライセンス確認、技術的な実装方法、軽微な品質検証などを個別にユーザー判断へ回さない。

ただし、品質基準の実質的な変更や新たな重要トレードオフが必要な場合は、理由と影響を明示してユーザー判断を求める。

## 3. Production Wiring・検証

既存の検証成果・救済設計・Opusレビュー・敵対的テストを最大限再利用する。

以下を満たすこと。

- Family XYZそれぞれの正式初回Production経路へ適用
- Standard／Advancedへの適用
- Human Reviewあり／なしの両経路との整合
- retry／fallback／regeneration／resumeでの救済結果の一貫性
- 本文一致・5語以下・自然さ・意味の保持などの既存品質条件を維持
- 不当な候補の誤受理を防ぐRegression／Validator／integration test PASS
- 既存の敵対的テスト85件・実データ315種類の回帰確認
- 各Familyの正式runtime evidence
- actual model_id・routing・Prompt等の必要な証拠
- Fable独立受入
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新、Git反映
- Dangling Referenceがないこと

**コード配線やDEVテストのみでPRODUCTION_WIREDと判断しない。**

Family別に未検証項目がある場合は、そのFamilyを未完了として明示する。

承認済み品質に到達したら追加の磨き込みを行わず完成させる。

## 4. 候補生成Trial｜フレーズ7件＋単語3件

**Status：Trial進行中。Production変更禁止。**

既に委任済みのTrialを継続・完了する。

対象：

- Family X「AIの仮想の島」
- Family X「英国の電車マナー」
- Family Z「猿の手」
- 各Standard／Advanced、計6レベル

試験方式：

- フレーズ・表現・Idiom：7件要求
- 単語：3件要求
- 合計10件要求
- 各レベル2回実行して生成ばらつきを確認

**10件すべてを採用することが目的ではない。**

返答不足やGate除外を見越して多めに要求し、品質を維持した最終候補6〜7件程度を確保できるかを検証する。

追加補充は原則行わず、低品質候補による数合わせは禁止する。

検証内容：

- AI要求数・返答数・Gate除外数・最終候補数
- フレーズと単語の内訳
- 各候補の本文出典・意味・順位・学習価値
- 現行Production方式との比較
- 生成ばらつき・量産原価への影響
- Fable独立評価

Trial終了時にREJECTED／VALIDATED／USER_DECISION_REQUIREDを明確にし、**Production採用はユーザーの正式判断を待つこと。**

AI島の既存Human Review候補は保全し、Trial結果によって無断変更しない。

## 5. Claude/Fableの自律判断【重要】

**承認済みの仕様・品質・予算・Scope・PM Gateの範囲内なら、技術的な問題をユーザーへ逐一転送せず、自律的に解決すること。**

- 不具合は原因究明→修正→検証まで実施する。
- 複数の実装手段はQCDで比較し、自ら最適なものを選ぶ。
- 既存のTrial結果・コード・テストを再利用する。
- 独立作業は原則並列化する。
- 少額の費用や技術的な細部について都度承認を求めない。
- 失敗時は同じ対策を無益に反復せず、必要に応じて方法を見直す。
- ユーザーが定義した品質基準を勝手に引き上げたり引き下げたりしない。
- 必要十分な品質を満たした時点で完了する。

ユーザー判断が必要なのは、**新仕様の正式採用、承認済み仕様・品質の変更、重要なQCDトレードオフ、予算・Scope変更、重大なblocker**などに限定する。

AI側で自律解決可能な事項は、質問ではなく解決結果として報告する。

なお、日次開発予算は原則1,000円（JST）。既存の案件別上限・STOP条件も遵守する。

## 6. 最終報告

次の2案件を分けて報告すること。

**A. Key Phrase救済方式**

- Family X/Y/Z別のProduction Wiring Status
- 実際に救済できたパターンと品質検証結果
- runtime evidence・回帰結果
- 追加費用・量産原価影響
- Fable受入結果
- 未完了事項

**B. 候補生成Trial**

- 3記事×2レベルの結果比較
- 全候補・順位・本文出典・意味・選定理由
- フレーズ／単語の件数・品質比較
- 原価・生成ばらつき
- Fable評価とProduction採用推奨案

**到達点を混同しないこと。救済方式はPRODUCTION_WIREDまで、候補生成方式はTrial Closeoutまで。**

承認済みの範囲内で自律的に最後まで進め、ユーザーに不要な技術判断を求めないこと。

(原文ここまで。本委任の対象は§2・§3のうち設計確定+DEV実装+test。§4の候補生成TrialはKP-CANDIDATE-PHRASE7-WORD3-TRIAL-01で完了済み・報告済み)

## Fableの解釈・設計指示(承認表の適用)

1. **採用する救済(Production化)**: (a)時制・活用形=区分2「救済フロー本体」のうち **revert(表層形維持)+M1限定再導出(display窓内でLLM提案語/display語のみ、`rose above→rise above`・`held out→hold out`型)+D1再アンカー(`catch their interest`→本文`catches their interest`へ戻して正規canonicalization)**。(b)慣用句=`can't be helped`型(先頭/内部に法助動詞・有限助動詞を含む自然な慣用表現)を**一般機構**で救済(下記3)。(c)既存仕様違反4件の是正=区分1の3件(適用済み845cfcb0a)+**量化詞限定詞guard(`no/each/every`等、`accepts no responsibility`)**を本委任で是正(Production `er105`該当guardのみ、test・A/B/C golden不変・敵対的85件同梱)。
2. **採用しない(Fable解釈。報告で明示)**: A1短縮救済(`too soon to wave a flag`→`too soon`)は、ユーザー表「6語以上を意味のない短縮で救済しない」と「5語以下 制限維持」に基づき**不採用**(意味が狭まる短縮も含めて不採用。6語以上は従来どおり除外し、外側retryで別候補を得る)。A2スロット一般化(`too soon to do`)・本文にない語の追加・CMU分解=不採用(ユーザー表どおり)。Human NG(`match_ng`)は救済経路でも迂回不可。
3. **慣用句の一般機構(Fable裁量=あなたがQCDで決めるが、次の要件を満たす)**: 27件閉表は使わない。候補案=(i)辞書見出し照合: Wiktionary英語の慣用句(Category: English idioms)+句動詞(English phrasal verbs)の見出し語リストをvendoring(件数・取得日・ライセンスCC BY-SA 4.0の帰属ファイル`ATTRIBUTION.md`同梱、sha256固定、読込失敗はfail-closed=救済しない)。候補句(主語除去・縮約形正規化`can't`/`can’t`両対応・所有格スロット`one's/someone's`の置換)が見出しに一致し、かつ本文の連続部分列(1〜5語)に対応する場合に限り、有限助動詞guardの例外を適用。(ii)規則ベース(辞書なし): 「法助動詞+be+過去分詞/法助動詞+動詞原形」の固定句で本文連続一致…は誤受理リスクが高いため**単独では不採用**。(iii)LLM判定: 追加費用・非決定性のため**不採用**(決定論Gateの原則)。→ 既定は(i)。辞書サイズが大きければ、慣用句カテゴリに限定(句動詞は既存の原形化経路で足りる)してよい。`data/kp_idiom_lexicon_01/{idioms.txt, meta.json, ATTRIBUTION.md}`。取得はWeb(Wiktionaryのカテゴリダンプ/API)でよいが、**本委任では取得スクリプト+取得結果のsha固定まで**。取得にAPI費用はかからない。ネットワーク不可なら、リポ内に既存の辞書資産があるかGlobし、無ければ取得手順を文書化して委任_02へ。
4. **HRあり/なし両経路との整合**: 救済候補は(α)HR経路では`RESCUED`旗+元句+救済理由コードを候補表に表示し、人間が選ぶ。(β)HRなし(自動採用)経路では、救済候補が**既存の最終Gate(同一引数)+gloss再整合+QA 12項目の再判定**(救済後keyに対して。LLM call 1回/件、約0.5〜1円/件)を通過した場合のみ`auto_eligible=True`とし、通常候補と同じ順位規則(元の`raw_rank`位置)に入れる。QA再判定を省く場合は`auto_eligible=False`(HRなし経路では採用されない)。どちらをProduction既定にするかは、あなたがQCDで決めて理由を書く(推奨: βでQA再判定あり=品質優先。費用は候補1件あたり約1円・level-runあたり該当0.4件程度)。
5. **retry/fallback/regeneration/resume一貫性**: 救済結果は候補ファイル(`kp_candidates.json`等)に`rescue`メタ(元句・救済形・理由コード・validator引数のsha)として永続化し、resume時は再計算せず読み戻す(再計算しても同一結果になる決定論性もtestで固定)。外側retry(`n_auto<3 and gate_dropped`)では救済成功句を`gate_dropped`に数えない(=救済成功で候補が足りればretryしない)。OPEN-456 F1累積除外リストには救済失敗のみ累積。`candidates_sha256`の算出に救済形を含める(HR候補の不変性保証)。**AI島`run_ai_01`の既存HR候補ファイルは不変**(新フローは今後の生成runにのみ適用。既存runのresumeで候補が変わらないこと=testで固定)。
6. **適用経路**: `run_canonicalization_gate(postprocess=)`の`fulltext_p2`経路(X/Y/Z共通の`generate_candidates`)に**既定ON**で配線する設計(委任_02で実施)。A/B/C旧経路(`_is_ft=False`)は無影響(golden 1002件不変)。Z限定のSRC D1・人称整合は救済後itemにも通常どおり適用。Yは`er121_family_y_runner_01.py:540-569`が同一`generate_candidates`を呼ぶため同時に適用(OPEN-484との関係を記す)。
7. **Production module化**: DEV `er123_kp_rescue_dev_01.py`の検証済みロジック(RulePatch方式・三重検査・have役割・過去形表)はすでにProductionへ移植済み(845cfcb0a)。本委任では救済フロー本体(revert/M1/D1/慣用句例外/gloss再整合hook/QA再判定hook/永続化)を`er125_kp_rescue_production_01.py`として**Production品質で**実装(型注釈・fail-closed・決定論・ログ)。委任_02で`er119_kp_candidates_01.py`/`er105`から1箇所ずつimportする前提のインターフェースを`DESIGN_03.md`に明記。
8. **test**: `er125_kp_rescue_production_test_01.py`=(a)11件の除外事例の期待結果(採用表に従い: 救済可=#2/#3/#4/#5/#6/#7/#9/#10/#11、不採用=#1[短縮]/#8[CMU]。#2/#3/#6/#10は区分1是正で通常フロー通過を確認)、(b)敵対的85件(`…DESIGN-02/adversarial_01.json`)で誤受理0、(c)実データ315種(`…DESIGN-02`の該当json。所在をGrep)で区分1是正の誤受理0、(d)A/B/C golden 1002件(`abc_golden_01.json`)バイト一致、(e)Human NG迂回不可、(f)決定論(同入力2回で同一出力)、(g)resume読み戻し一致、(h)辞書fail-closed、(i)縮約形・所有格スロットの正規化、(j)量化詞限定詞guard是正の正負例。既存`er123`154 test・`er105_kp_rule_compliance_test_01.py` 19 test・er105/er119回帰(HEAD既存失敗2件は既知)も実行。
9. **成果物**: `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/{SPEC_LEDGER_01(採用表→実装項目の対応、Fable解釈を含む),DESIGN_03(確定設計・インターフェース・HRあり/なし・resume・既定ON),IDIOM_LEXICON_01(出典・件数・ライセンス・sha・取得手順),OPUS_REVIEW_REQUEST_03(変更部のみ: 慣用句一般機構/HRなし経路の扱い/既定ON/一貫性),TEST_PLAN_01,BUDGET_PLAN_02(委任_02 evidence見積: X/Y/Z各2レベル)}.md`、`rescue_eval_prod_01.json`。

## KPI provenance欄

該当: test結果=synthetic/frozen(既存json)。runtime evidenceは委任_02(fresh、production_formal_path)。E2E自己確認: No(本委任)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-KPRS-M1〜M6/R1〜R4(DESIGN-01)とOF-KPRS2(DESIGN-02)の状態を`SPEC_LEDGER_01.md`に「本設計での反映状況」として転記(台帳自体は編集しない=Fable sync)。

## 事前指定Read一覧

- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/{DESIGN_02,RESCUE_TABLE_01,PATTERN_DESIGN_01,OPUS_REVIEW_02,IDIOM_CLOSED_TABLE_01,PROD_APPLY_01}.md` 全文
- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/{DESIGN_02,OPUS_REVIEW_01}.md` 全文(M1〜M6/R1〜R4の内容)
- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/adversarial_01.json`・`abc_golden_01.json`・`rescue_eval_0*.json`(構造のみ確認、全件Readは不要)、Glob `…DESIGN-02/*315*|*realdata*|*inventory*` → 315種データの所在
- `er123_kp_rescue_dev_01.py`: Grep `^def |^class ` → 構造把握、救済フロー部(Grep `revert|rederive|reanchor|idiom|M1|D1`) ±40
- `er105_kp_fulltext_selector_01.py`: Grep `def run_canonicalization_gate|postprocess|_GUARD_DET|def _guard_ok|no |each|every|quantif` → ±30(量化詞guardの是正箇所特定)、`:689-700`
- `er119_kp_candidates_01.py`: Grep `def generate_candidates|gate_dropped|n_auto|candidates_sha256|auto_eligible|match_ng|align_glosses|qa_` → ±25(配線予定点とresume/HRの既存構造)
- `er119_kp_human_review_01.py`: Grep `RESCUED|auto_eligible|KP_CANDIDATE_MAX|candidates_sha256` → ±10
- `docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_USER.md`(存在すれば): Grep `区分|救済` → ±5
- `CURRENT_SPEC.md`: Grep `先頭またはto直後|Key Phrase候補|CMU|Human Review.*NG|最大8` → 該当行±10のみ(全文読込禁止)
- `OPEN_ITEMS.md`: Grep `OPEN-529|OPEN-530|OPEN-152|OPEN-456|OPEN-484|OPEN-526` → 該当行のみ

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `data/**/*idiom*`、`**/*wiktionary*` → 既存辞書資産の有無
- Grep `_containment|raw_rank|finalize` in `er119_kp_candidates_01.py`,`er105_kp_fulltext_selector_01.py` → 順位・包含処理の位置(設計のインターフェース記述用)
- 成果物は`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/`に新規作成、辞書は`data/kp_idiom_lexicon_01/`に新規作成

## 実行コマンド全文

- test(遮断harness・`.venv`): `.venv\Scripts\python.exe run_project_regression.py --pattern "er125*_test_*.py"`、`--pattern "er123*_test_*.py"`、`--pattern "er105*_test_*.py"`、`--pattern "er119*_test_*.py"`(harness起動方法はCHUNK委任_03 `regression_z/`記録に合わせ全文記録)
- A/B/C golden再生成比較: `.venv\Scripts\python.exe docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\tools\gen_abc_golden_01.py --out C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\abc_golden_check.json` → `abc_golden_01.json`とバイト比較(引数は`--help`で実値確認)
- 辞書取得(ネットワーク可の場合): 取得スクリプト`data/kp_idiom_lexicon_01/fetch_wiktionary_idioms_01.py`を作成し実行(Wiktionary API `categorymembers`、User-Agent明記、rate制限順守)。結果sha256を`meta.json`へ
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KPRW1.md`(9)にCURRENT_SPEC新節案「Key Phrase Gate除外救済方式(APPROVED_FOR_PRODUCTION 2026-10-26)」・OPEN-529更新案・DECISION_LOG案を記載(Fableが委任_02後に転記)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/`配下、`er125_kp_rescue_production_01.py`、`er125_kp_rescue_production_test_01.py`、`er123_*`(変更があれば)、`er105_kp_fulltext_selector_01.py`(量化詞guard是正のみ)、`er105_kp_rule_compliance_test_01.py`(追加test)、`data/kp_idiom_lexicon_01/`(txt/json/md/py。巨大ファイルは5MB以下に抑える=必要なら慣用句カテゴリ限定)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01_{USER,DELEGATION_01}.md`(+check.json)。pathspec付きcommit。RESULT_PACKETはaddしない。
- commit(2回可): ①`KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01: 量化詞限定詞guard是正(区分1、Production fulltext限定、A/B/C不変、敵対的85件)` ②`… 救済方式のProduction実装設計確定+er125 module+test+慣用句辞書vendoring(未配線、API 0)`
- trailer: `Delegation: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPRW1.md`: (0)T-0、(1)採用表→実装項目の対応(SPEC_LEDGER)とFable解釈の確認(短縮不採用の影響=#1は除外のまま)、(2)確定設計の要点(慣用句機構の選定理由・QCD比較、HRあり/なし既定、resume・retry一貫性、既定ON、インターフェース)、(3)量化詞guard是正(差分:行・正負例・A/B/C不変・敵対的85件)、(4)test結果(件数・接続試行0・HEAD既存失敗)、(5)11件の最終期待結果表(救済形・経路・理由コード)、(6)辞書(出典・件数・ライセンス・sha・サイズ・fail-closed)、(7)Opusレビュー依頼文案(変更部のみ)、(8)委任_02の実施計画(配線箇所:行、evidence run計画X/Y/Z・費用見積)、(9)SSOT文案、(10)判断候補(品質基準の実質変更が必要と判明した場合のみ)、(11)必須4行+「判定整合: 重大NG=<なし|あり>」、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。