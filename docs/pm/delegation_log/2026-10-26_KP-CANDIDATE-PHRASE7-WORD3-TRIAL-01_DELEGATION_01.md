## 管理ID

KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01(Trial: Key Phrase候補要求を「フレーズ・表現・Idiom 7件」+「単語単体 3件」に分けて要求する方式の検証。3記事×2レベル=6 level)。並行タスク衝突確認: 並行Agent 2件あり。(a) CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03(Z Std chunk実装。`er117_chunk_tts_production_01.py`/`er063_family_z_audio_01.py`/`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/`を編集中。あなたはこれらに触れない)、(b) SSOT同期Agent(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/ACTIVE_TASK.md`を編集。あなたはSSOT編集権なし)。あなたの所有ファイル=`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/**`、新規DEV module `er124_kp_phrase_word_trial_01.py`(+ `er124_kp_phrase_word_trial_test_01.py`)、`docs/pm/delegation_log/2026-10-26_KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_KPT1.md`(gitignored、commitしない)。git index.lockが並行Agentと競合して失敗したら10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: **Trial(候補抽出・評価まで)**。到達上限Status=**VALIDATED / REJECTED / 判断候補(USER_DECISION_REQUIREDラベルはFableのみ)**。VALIDATEDでもProduction実装へ移行しない(ユーザー明示判断必須)。
- **禁止**: ProductionのPrompt・選定ルール・Gate・Human Review・候補数仕様の変更(`er119_kp_candidates_01.py`/`er119_kp_human_review_01.py`/`er119_kp_human_review_cli_01.py`/`er105_kp_fulltext_selector_01.py`/`er003_key_words_canonicalization.py`/`er003_key_words_min_unit.py`はRead/Import onlyで**1文字も編集しない**。Promptのsha固定を壊さない)。記事本文の修正・再生成禁止。本文生成・TTS・公開記事の変更禁止。既存run dir(`er019_output/**`、`er026_output/**`、`er063_output/**`等)への書込み禁止(読むだけ。AI島のHuman Review候補ファイル・`candidates_sha256`は**不変のまま保全**。HR CLIの`select`等は実行しない)。Web検索不要。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`禁止。
- 費用: 上限¥80(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日(JST 2026-10-26)既使用約JPY500(出典: RESULT_PACKET_YM7 276.13+RESULT_PACKET_CHKW2 9.48+午前分約214)/残約JPY500(別途Chunk Z委任Cap60進行中)/本委任見積JPY20〜40(根拠: 6 level×[フレーズ7 call+単語3 call]×反復2回=24 call+LLM判定6〜12 call、既存KP候補生成callの実績単価×件数で算出し実行前にBUDGET_PLAN_01へ記す。上限=Guardrail 80)/改善見込み高/承認区分: C(承認済みTrial範囲=ユーザー本日指示、案件300円以下、日次1,000円以内)。
- Opus独立技術レビューGate(11-3): **非該当**(Trial。Production構造・フローの変更なし。採用提案時にFableが別途判定)。
- 修正範囲の線引き(11-8): 本委任は不具合修正ではなくTrial。Production受理面・閾値・方式の新設/拡大はDEV module内の「要求数・要求区分(フレーズ/単語)の分離」に限り、Gate(5語・本文対応・正規化・CMU・有限助動詞・Human NG復活禁止・重複/包含)は**Production関数をそのままimportして同一引数で適用**する。
- 最新モデル原則(PM_GOVERNANCE 25節): 候補生成はProduction候補生成(call1/call2)と同じモデルを既定とする(比較可能性のため。Productionモデルが最新でない場合はその旨と理由「現行方式との比較条件統一」を記録)。評価判定(LLM judge)を使う場合は最新最上位系(gpt-6-luna等、`er119_kp_candidates_01.py`で使用中のモデル名をGrepで確認し記載)。使用モデル名/最新か/最新でない理由を報告に必ず書く。
- 時間見込み: 全体約2.5〜3.5h(設計・既存成果物の棚卸し40分/DEV module+test 60分/6 level実行+Gate 30分/比較表・評価60分/commit 10分)。並列化: 6 levelの生成callはrate limitの範囲で並列(ThreadPool等)。現行方式候補の棚卸し(API 0)はDEV module実装と並行して先に行う。直列化するのは「現行Gate関数の呼出し方の確認→DEV module実装」のみ(前工程依存)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足(委任文の逐語保存): `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01_DELEGATION_01.md` をN=649から順に試し、先頭が「## 管理ID」+「KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01」で始まるものを採用(`--index -1`不可。同時刻に別委任文(SSOT同期委任)も送られているため先頭一致を必ず確認)。ユーザー指示原文(下記「ユーザー指示(原文)」の全文)を`docs/pm/delegation_log/2026-10-26_KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01_USER.md`へ逐語保存。

## ユーザー指示(原文)

# 【Trial指示】Key Phrase候補選定｜フレーズ7件＋単語3件の抽出比較

## 1. 目的・Status

Key Phrase候補選定について、現行方式ではフレーズ・表現に偏り、単語単体の候補がほとんど提示されない問題がある。

今回、AIへの候補要求を次の2種類に分けてTrialする。

- **フレーズ・表現・Idiom：7件**
- **単語単体：3件**
- **要求合計：10件／レベル**

重要なのは、**10件を必ず返させることではない。**

10件と多めに要求する理由は、AIが要求数を返さない場合や、既存Gateで候補が除外された場合でも、最終的に学習価値のある候補を6〜7件程度確保するためである。

候補数を埋める目的で、質の低い単語や不自然なフレーズを採用してはならない。

**Status：Trial。到達可能Status＝VALIDATED／REJECTED／USER_DECISION_REQUIRED。**

ProductionのPrompt・選定ルール・Gate・Human Review・候補数仕様は変更しない。Productionへの正式採用はユーザーの別途判断を必要とする。

## 2. Trial対象記事

以下の3記事を使用する。

| Family | 記事 |
|---|---|
| X | AIの仮想の島 |
| X | 英国の電車マナー |
| Z | 猿の手 |

各記事のStandard／Advancedを対象とし、**合計6レベル**で検証する。

既存の確定済み本文を使用し、記事本文の修正・再生成は行わない。

Family Z『猿の手』についても、実際の対象レベル・本文を既存成果物から確認し、現行正式仕様と同じ本文を用いること。

## 3. Trial方式

### A. フレーズ・表現・Idiom 7件

既存のKey Phrase選定仕様を基本とし、本文中の学習価値が高いフレーズ・慣用表現・自然な定型表現を、最大7件、順位付きで抽出する。

- 本文との対応が明確であること
- 原則5語以下
- 自然で汎用性があること
- Standard／Advancedそれぞれの難易度に適合すること
- 既存の一般化・正規化ルールと整合すること
- 類似候補や重複による数合わせをしないこと

### B. 単語単体 3件

**フレーズ抽出とは別枠で、単語単体を最大3件、順位付きで抽出する。**

例えば『AIの仮想の島』では、`cathedral` や `feature` のような語も、本文に実在し、そのレベルで学習価値があるなら選定対象となる。

ただし、これらの語を必須選定語として指定するものではない。

- 本文に実在する単語を対象とする
- 学習者にとっての有用性・汎用性・難易度を評価する
- 単語単体で学ぶ価値があるものを選ぶ
- すでにフレーズ候補に含まれる語についても、学習価値の重複を評価する
- 単語を3件埋めるために簡単すぎる語や不自然な候補を選ばない

既存の承認済み品質基準は維持する。

### C. Prompt・候補生成

今回のTrialでは、**フレーズ7件と単語3件を明確に区別して要求する。**

AI呼び出しの回数・Prompt分割・モデルの選択は、既存方式との比較可能性とQCDを踏まえて最適化してよい。

ただし、実際に要求した件数、返答件数、API呼び出し回数、費用を必ず記録すること。

現行方式との比較では、候補生成方法の違いが結果に与えた影響を説明できるようにする。

## 4. 検証項目

各記事・各レベルについて、以下を確認する。

1. フレーズ7件要求に対して実際に何件返ったか
2. 単語3件要求に対して実際に何件返ったか
3. 既存Gateで何件除外され、なぜ除外されたか
4. Gate通過後に何件残ったか
5. フレーズと単語の内訳
6. 現行方式では拾えていなかった有用な候補が増えたか
7. 候補の学習価値・自然さ・汎用性・難易度
8. 類似候補や重複、数合わせによる品質低下の有無
9. 追加生成費用・制作時間への影響

特に、**最終的に6〜7件程度の有用な候補を安定して確保できるか**を評価すること。

6〜7件は目標であり、品質を満たさない候補まで無理に残す義務ではない。

単に候補数が増えたことだけで成功としない。

## 5. 現行Production方式との比較

同じ本文に対して、現行方式の候補一覧と今回のTrial結果を比較する。

可能な限り既存の候補生成結果を再利用し、不要な有料再実行を避ける。

各レベルについて次の比較表を作成する。

| 項目 | 現行方式 | Trial方式 |
|---|---|---|
| 要求件数 | 最大8件 | フレーズ7＋単語3 |
| AI返答件数 | 実績 | 実績 |
| Gate除外件数 | 実績 | 実績 |
| 最終候補件数 | 実績 | 実績 |
| フレーズ件数 | 実績 | 実績 |
| 単語件数 | 実績 | 実績 |
| 学習価値・多様性 | 評価 | 評価 |
| 生成コスト | 実績または推計 | 実績 |

候補は単なる件数だけでなく、**英語表現・日本語意味・本文中の出典・選定理由・順位**を省略せず掲載すること。

『AIの仮想の島』については、現行Standardの5候補、Advancedの7候補との違いが分かるようにする。

## 6. Fable独立評価

Trial完了後、Fableが以下を独立評価すること。

- 単語候補が適切に増えたか
- フレーズ候補の品質が下がっていないか
- 最終6〜7件程度を安定して確保できる見込みがあるか
- 既存Gateとの整合
- Family X/Zに共通して使える方式か
- Family Yへの将来適用上の問題
- QCDへの影響

特に、**候補数の確保と品質維持を両立できるか**を評価すること。

3記事×2レベルの結果から一般化できる範囲と、まだ未確認の事項を区別する。

必要十分な品質が確認できれば、不要な追加Trialは行わない。

## 7. QCD・予算・進め方

品質 ＞ Delivery ＞ 量産単価。

既存データを再利用し、独立作業は並列化する。

今回のTrialは候補抽出・評価までとし、本文生成・TTS・公開記事の変更は行わない。

承認済みの案件予算・日次1,000円（JST）を遵守する。案件見積が事前費用承認を要する場合は、実行前に報告する。

失敗時は、原因究明→修正→検証の自律ループで解決する。ただし、未承認のProduction仕様変更、新規Trial範囲の追加、重大な品質基準変更、予算超過は行わない。

## 8. 最終報告・Closeout

報告は以下の順序とする。

1. **結論：10件要求方式で、実際に何件の有用候補を確保できたか**
2. 3記事×2レベルの件数比較
3. フレーズ・単語それぞれの候補全文リスト
4. 現行方式との学習価値・品質比較
5. Gate除外の内容と理由
6. 費用・量産単価への影響
7. Fable独立評価
8. Production採用の推奨／非推奨と残る判断事項

Trial終了時にVALIDATED／REJECTED／USER_DECISION_REQUIREDを確定する。

**VALIDATEDでもProduction実装へ自動移行しない。** 採用にはユーザーの明示判断を必要とする。

---

**今回の核心：フレーズ7件＋単語3件と多めに要求することで、数合わせによる品質低下を起こさず、最終的に質の高い候補を6〜7件程度確保できる方式かどうかを検証すること。**

(原文ここまで)

## Fableからの設計指示(ユーザー原文を狭めない範囲)

1. **現行方式の実績(API 0)**: 3記事×2レベルの現行候補生成結果(call1 Prompt 2=3件+call2 Prompt 2-V=max5、Gate除外記録、HR候補表)を既存成果物から棚卸しする。AI島=`docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/HR_REVIEW_REQUEST_01.md`+run dir `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/`(Std 5候補・Adv 7候補、Gate除外=`too soon to wave a flag`/`studied separately`)。英国電車マナー=`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_*`(HR候補ファイル・kp candidates json・除外記録をGlobで特定。複数runがある場合は正式採用runを優先し、どれを使ったか明記)。猿の手=`er026_output/family_z_production_e2e_01/`配下またはZの正式run(`docs/research/FZ-*`/`er063_output/`)から**実際の対象レベル・正式本文**を特定(Zのレベル構成が`a2/b1b`か別かを既存成果物で確認し、ユーザー原文「現行正式仕様と同じ本文」を満たすrunを使う。`run_fzcw_e1_01`はSTOP残置runなので使わない)。現行方式の要求件数・返答件数・Gate除外件数・最終候補件数・フレーズ/単語内訳を`CURRENT_BASELINE_01.md`+json化。現行候補が「単語」か「フレーズ」かの判定基準を事前に固定(例: 空白を含まない1語=単語。句動詞・複合語の扱いを明記)。
2. **DEV module `er124_kp_phrase_word_trial_01.py`**: Productionを変更せず、(a)本文(Production候補生成が受け取るのと同じ本文テキスト。`er119_kp_candidates_01.py`がどの入力[全文/Part別]を渡しているかをGrepで確認し同一にする)、(b)Prompt 2-Vの文面を基に**フレーズ7件用Prompt(P7)**と**単語3件用Prompt(W3)**をDEV側に新設(Production Promptの文字列定数は参照のみ。P7は既存規則[5語以下・本文対応・レベル適合・正規化整合・数合わせ禁止]をそのまま、要求数7・順位・選定理由・日本語意味・出典文を出力させる。W3は「本文に実在する単語単体・そのレベルで学習価値・汎用性・難易度・フレーズ候補との重複評価・簡単すぎる語を埋め合わせに使わない」を明示し、フレーズ候補一覧を入力に与えて重複評価させる[=P7→W3の2 call直列]。1 callで両方出す変種(P7W3合体)も比較可能性・費用の観点で検討し、採用した方式と理由を記す)、(c)既存Gateを**Production関数のimport**で同一引数適用(選定gate: 本文連続一致・1〜5語・有限助動詞・数値、canonicalization validator `allow_inflection_normalization=True`等=`er123_kp_rescue_dev_01.py`/`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/tools/prod_vs_dev_parity_01.py`で確立済みの呼出し方を再利用、CMU、Human NG照合、既存候補との包含/重複`_containment`相当、最大8の上限は**Trialでは適用せず**「通過件数」をそのまま記録し、8超の場合は別途注記)。単語候補についてはGateのうち適用されるもの/されないもの(例: 原形化・CMU・本文実在・Human NG)を事前に明記し、単語に適用すべき追加確認(本文実在・レベル適合)を同一基準で行う。Gate除外は理由コード付きで全件記録(除外は**捨てずに記録**。救済フローは本Trialの範囲外=適用しない)。
3. **反復**: 生成ばらつき評価のため各levelを**2回**実行(同一Prompt・同一モデル・temperature既定。1回目/2回目の候補差分・通過件数差を記録)。費用がGuardrailに収まらない見込みなら1回に落として理由を記録。
4. **LLM評価(任意、Cap内)**: 候補の学習価値・自然さ・汎用性・難易度・重複を、現行候補とTrial候補を**匿名化・順序シャッフル**して同一ルーブリックで判定させるjudge callを各level 1回(最新最上位モデル)。あなた自身のルーブリック評価も併記し、judgeと食い違う点を明示。judge結果を単独の合否根拠にしない。
5. **比較表**: ユーザー原文§5の8行表を6 level分+総括。候補一覧は英語表現・日本語意味・本文中の出典文・選定理由・順位・区分(フレーズ/単語)・Gate結果を全件掲載(`RESULT_01.md`)。AI島はユーザー原文どおり現行Std 5候補/Adv 7候補との差分を明示。
6. **安定性評価**: 「最終6〜7件の有用候補を安定して確保できるか」を、6 level×2回=12 runでの通過件数分布(最小/中央/最大)と、品質基準を満たす件数(あなたのルーブリック+judge一致分)で示す。件数増だけで成功にしない。
7. **Trial Status案**: VALIDATED/REJECTED/判断候補のいずれかと根拠。Production採用時の変更点(Prompt・call数・HR表示・候補数仕様・単価影響)を「採用提案の素案」として分離して書く(採用提案そのものはFable/ユーザー)。Family Yへの将来適用上の問題(Y正式KP経路未存在=OPEN-484)とZ特有(SRC D1・人称整合)の整合は机上で確認。
8. **実行前のSTOP確認**: `py tools/stop_scope_check_01.py`をAPI実行前に1回(rc=0を記録)。有料callは`.venv\Scripts\python.exe`。

## KPI provenance欄

該当: 現行方式の件数=reuse(既存成果物)/Trial方式の件数=fresh(本委任のDEV call)/Gate判定=Production関数のimport(production_formal_path相当だがDEV入口。混在件数を明記)。E2E自己確認: No(候補抽出のみ、Production初回pathではない)。

## Opus台帳更新

該当なし(本委任ではOpus指摘なし)。

## 事前指定Read一覧

- `er119_kp_candidates_01.py`: Grep `Prompt 2|PROMPT_2|max5|n_auto|gate_dropped|model=|MODEL` → 該当行±30(call1/call2のPrompt本文・モデル名・入力本文の渡し方・Gate呼出し順・費用記録の仕組み[usage log]を把握)
- `er119_kp_human_review_01.py:40-60`(KP_CANDIDATE_MAX=8周辺、HR候補表の構造)
- `er105_kp_fulltext_selector_01.py`: Grep `def _guard_ok|def run_canonicalization_gate|def _containment|_GUARD_DET` → 各def ±40
- `er123_kp_rescue_dev_01.py`: Grep `import|validate_canonicalization_item|selection_gate|cmu` → Gate呼出し部 ±30(Production関数の再利用方法の先例)
- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/tools/prod_vs_dev_parity_01.py` 全文(短いはず。長ければGate呼出し部のみ)
- `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/HR_REVIEW_REQUEST_01.md` 全文
- `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/ARTICLE_EN_STD_01.md`・`ARTICLE_EN_ADV_01.md` 全文(本文確認用。ただし生成入力はrun dirの正式本文ファイルを使う)
- `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/RESCUE_TABLE_01.md:1-20`(除外理由の語彙・Gate構成の参照)
- `CURRENT_SPEC.md`: Grep `Key Phrase候補|KP_CANDIDATE_MAX|Prompt 2-V|最大8|先頭またはto直後` → 該当行±15のみ(全文読込禁止)
- `docs/pm/PM_GOVERNANCE.md`: Grep `^## 25|25節|最新モデル` → 該当節のみ

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_*/**/kp*candidates*.json`・`**/human_review*.json`・`**/HR_REVIEW*` → 英国電車マナーの現行候補・除外記録を特定
- Glob `er026_output/family_z_production_e2e_01/**/kp*`・`er063_output/**/kp*`・`docs/research/FZ-*MONKEY*/**`・`docs/research/*SARU*/**`(猿の手の正式run・本文・KP候補) → 対象レベルと本文を確定し`CURRENT_BASELINE_01.md`冒頭に「使用run/本文ファイル/sha256」を記す
- Grep `gpt-6|model_name|OPENAI_MODEL` in `er119_kp_candidates_01.py`,`er105_kp_fulltext_selector_01.py` → モデル名の確定
- Grep `human_ng|match_ng|HUMAN_NG` in `er119_*.py`,`er105_*.py` → Human NG照合関数の特定(Trial候補にも同一適用)
- 成果物の追記位置: 全て`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/`配下に新規作成(`DESIGN_01.md`[方式・Prompt全文・Gate適用表・単語/フレーズ判定基準・反復設計・事前固定の評価ルーブリック=**API実行前に作成しsha256を`DESIGN_01.sha256`へ記録**]、`BUDGET_PLAN_01.md`、`CURRENT_BASELINE_01.md`+`current_baseline_01.json`、`trial_runs_01.json`[全call入出力・usage・費用]、`gate_results_01.json`、`RESULT_01.md`[§5比較表6 level+候補全文]、`COMPARISON_01.md`[学習価値・品質比較、judge結果]、`STATUS_01.md`[VALIDATED/REJECTED/判断候補と根拠、採用提案素案])

## 実行コマンド全文

- STOP確認: `py tools\stop_scope_check_01.py`
- DEV test(無料・遮断harness): `.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'C:\Users\tensh\eigo-radio\netblock_harness_01'); import sitecustomize; import pytest; sys.exit(pytest.main([r'C:\Users\tensh\eigo-radio\er124_kp_phrase_word_trial_test_01.py', '-q']))"`(harnessの正しい起動方法が異なる場合は`netblock_harness_01/`内のREADME/先例test(`er123_kp_rescue_dev_test_01.py`の実行記録)に合わせ、使ったコマンドを全文記録)
- 現行baseline棚卸し: `.venv\Scripts\python.exe er124_kp_phrase_word_trial_01.py baseline --out docs\research\KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01\current_baseline_01.json`(サブコマンド設計は自由。実値で記録)
- Trial実行(有料): `.venv\Scripts\python.exe er124_kp_phrase_word_trial_01.py run --levels ai_island_temple:a2,ai_island_temple:b1b,uk_train_speaker_playback:a2,uk_train_speaker_playback:b1b,monkeys_paw:<level1>,monkeys_paw:<level2> --repeats 2 --budget-jpy 80 --out docs\research\KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01\trial_runs_01.json`(猿の手のslug・levelは棚卸し後に実値へ置換して記録)
- 回帰(Production不変の確認): `.venv\Scripts\python.exe run_project_regression.py --pattern "er105*_test_*.py"` と `--pattern "er119*_test_*.py"`(HEAD既存失敗=er119 isolation 2件・er109 5件は既知。新規失敗0を確認)。`git diff --stat -- er119_kp_candidates_01.py er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py er003_key_words_min_unit.py er119_kp_human_review_01.py` が空であることを記録
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件確認(委任文内のパターン文字列は偽陽性として記録)

## SSOT追記文

SSOT編集権なし。以下の文案を`docs/pm/RESULT_PACKET_KPT1.md`の(9)に記載するのみ(Fableが転記):
- OPEN_ITEMS新規(11-8分類は「Trial結果の採否判断=ユーザー判断候補」): `OPEN-5xx | KP候補要求のフレーズ7+単語3分離方式Trial | Status=<VALIDATED|REJECTED>_PENDING_USER_DECISION | 2026-10-26 | 概要: 3記事×2レベル×2回、現行方式比の最終候補件数<min/median/max>、単語候補<件数>、費用<実費>円、採用時の単価影響<+x円/セット> | Production不変`
- DECISION_LOG: `2026-10-26 | KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 | Trial完了(<Status>)。方式=<P7→W3 2 call|合体1 call>、モデル=<名>、Gate=Production関数import同一引数、結果<要約1行>。Production採用はユーザー判断。`

## Git(明示add対象・コミットメッセージ・trailer)

- add対象(明示pathのみ): `docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/`配下の生成物(md/json/sha256、wavなし)、`er124_kp_phrase_word_trial_01.py`、`er124_kp_phrase_word_trial_test_01.py`、`docs/pm/delegation_log/2026-10-26_KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01_USER.md`、`..._DELEGATION_01.md`、`..._DELEGATION_01.md_check.json`。`docs/pm/RESULT_PACKET_KPT1.md`はgitignoredのためaddしない(`-f`禁止)。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/PM_GOVERNANCE/UDR/Opus台帳)の編集権なし=編集・addしない。
- commit message: `KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01: KP候補要求のフレーズ7+単語3分離Trial(3記事×2レベル×2回、現行方式比較、Gate=Production関数同一適用、実費<x>円、Production不変、Status案<...>)`
- trailer: `Delegation: KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。branch `work/post-merge-01`のまま。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPT1.md`に以下を書き、同内容を最終報告として返す(ユーザー原文§8の順序1〜8。7「Fable独立評価」はあなたの評価材料[ルーブリック表・judge一致表・一般化できる範囲/未確認事項]を書き、Fable評価欄は空けておく):
(0) T-0結果(PASS/FAIL・reasons1行)、委任文保存index
(1) 結論: 10件要求方式で確保できた有用候補件数(6 level×2回の min/median/max、品質基準充足分)と現行方式比
(2) 3記事×2レベル件数比較(§5の8行表×6+総括1表)
(3) 候補全文リスト(フレーズ/単語別、英語表現・日本語意味・出典文・選定理由・順位・Gate結果)、AI島は現行Std5/Adv7との差分
(4) 現行方式との学習価値・品質比較(ルーブリック+judge、食い違い)
(5) Gate除外の内容と理由(全件、理由コード)。単語候補へのGate適用表
(6) 費用: call数・要求件数・返答件数・モデル名(最新か/理由)・実費(usage log出典)・Production採用時の単価影響推計(現行KP生成費との差)
(7) Fable独立評価用材料(一般化できる範囲/未確認事項/Y・Z整合)
(8) Status案(VALIDATED/REJECTED/判断候補)と採用提案素案、残る判断候補
(9) SSOT文案(上記)
(10) RESULT_PACKET必須4行: 既存仕様整合(照合ファイル:行)/未承認機能の既定値(Production経路に入っていないことの証拠=git diff空)/失敗終了時の最終成果物と目的適合(ユーザー原文「核心」文との対応)/撤去・残置(なし想定)。直後に「判定整合: 重大NG=<なし|あり:主因/是正対象/STOP理由>」1行
(11) 一覧外Read(理由1行ずつ)、commit hash、raw URL(主要5件まで)
最終報告は10行以内の要約を末尾に付ける。ユーザー判断の候補は`判断候補`表記(USER_DECISION_REQUIREDラベルはFableのみ)。