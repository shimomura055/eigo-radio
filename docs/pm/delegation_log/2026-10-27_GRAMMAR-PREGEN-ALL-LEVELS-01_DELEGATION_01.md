## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(ユーザー正式決定【全面修正版】2026-10-27、APPROVED_FOR_PRODUCTION: ①フォームv3正式採用 ②**文法解説の事前生成(全6経路=X/Y/Z×Std/Adv)** ③全候補AI選定理由 ④確定内容保護(全6経路)。本委任=②を中心に、調査・旧Advanced限定仕様の棚卸し・設計・実装計画・Opus条件A依頼文。**read-only、コード/SSOT編集なし**。API 0・JPY0)。並行Agent: (a)KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B(`er119_kp_human_review_01.py`/`er120_*`/`er121_family_y_audio_01.py`/`er063_*`/`er026`runner/`er020`/`er128`編集中)、(b)LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04(フォーム側)。これらは編集しない(読むのは可。編集中のため`git show origin/main:<path>`のHEAD版を基準に読む)。あなたの所有=`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{CURRENT_FLOW_01,ADV_ONLY_INVENTORY_01,DESIGN_01,IMPL_PLAN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,COST_ESTIMATE_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG1.md`。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み新仕様(工程順変更+Standardへの文法解説拡張+公開ページ表示)の設計=**Opus条件A必須(実装前)**。到達上限=DESIGN_READY。
- 禁止: コード/SSOT編集、対象範囲をAdvancedに狭めるAI独自判断、承認済みの解説品質・文章量・学習内容(Part 2解説Prompt)の変更、フォームUI変更、禁止Git操作。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER.md`へ逐語保存。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_01.md` をN=711から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01」のものを採用。

## ユーザー指示(原文・逐語)

# Claude Code指示｜学習項目選定フォームv3・文法解説事前生成・確定内容保護｜全Family Production Wiring【全面修正版】

## 1. ユーザー正式決定【最優先】

以下4項目を、Family X/Y/Z × Standard/Advancedの**全6経路**に正式採用する。

**Status：APPROVED_FOR_PRODUCTION**

**到達目標：PRODUCTION_WIRED（全6経路）**

正式採用項目：

1. **学習項目選定フォームv3**
2. **文法解説の事前生成**
3. **全Key Phrase／Key Word候補へのAI選定理由の付与・表示**
4. **ユーザー確定内容の保護**

**重要：この4項目はすべてStandard／Advancedの両方に適用する。**

文法解説も例外ではない。

- Standard：文法候補の事前生成、ユーザー選定、確定内容の保護、公開表示まで対象。
- Advanced：同上。
- Family X/Y/Z：すべて同じ適用方針。

既存CURRENT_SPECに「Part 2文法解説はAdvancedのみ」など、今回のユーザー意思に反する記述が存在する場合は、**今回の正式承認によって変更された旧仕様として整理・修正すること。**

旧仕様を根拠にStandardを対象から外してはならない。

対象範囲を狭めるAI独自判断は禁止する。

## 2. フォームv3の正式仕様

公開URL：
https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/

参照HTML：
`docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`

現在のフォームv3を正式採用する。以下の仕様を維持する。

- 最大9記事・レベル別に選定可能。
- Key Phrase／Key Wordを一覧表示。
- 候補の英語表現、日本語訳、AI選定理由を表示。
- 日本語訳は「正式訳／仮訳・未確定／未生成」を区別。
- ①Key Phrase：最大3件。
- ①＋②追加解説：最大5件。
- ①＋②＋③本文ハイライト・短い日本語意味：最大12件。
- ①②③は同一候補で重複選択不可。
- 文法は独立枠で最大2件。
- 文法候補には文法名・解説全文を表示。
- 自由コメント欄を維持。
- 選定上限超過を防ぎ、選択解除・変更は可能。
- 英語、日本語訳、区分、文法名・解説全文、コメントなどを欠落なくChatGPTへ渡す。
- 当面はChatGPTへの送信方式を維持し、Claudeへの直接送信機能は新設しない。

Family X/Y/ZのStandard/Advancedすべてについて、候補の取込・表示・選定・送信を可能にする。

フォーム仕様は今回FIX済み。不要な追加UI Trialや仕様変更は行わない。

## 3. 文法解説の事前生成【全6経路】

以下をStandard／Advanced共通仕様として実装する。

1. 文法候補ごとに、エンドユーザー向けの「文法名＋解説全文」を選定前に生成する。
2. ユーザーがフォームで解説全文を確認して採否を決める。
3. 採用した文法名・解説全文を確定データとして保存する。
4. 確定後は同じ内容を再生成・書換えしない。
5. 採用した文法解説は、そのFamily・レベルの正式な公開ページに表示する。

**Family X/Y/Z × Standard/Advancedの全6経路で、文法解説の生成・選定・確定・公開までを対象とする。**

既存のPart 2文法解説、Trial-08選定方式、文法Human Reviewと整合させる。

承認済みの解説品質・文章量・学習内容を独断で変更しない。

工程順の変更に伴い、旧「選定後に解説を生成する」処理の重複実行を防止する。

追加費用の事前見込みは約0.3円×候補数／記事。実際の費用を計測し、量産単価への影響を報告する。

## 4. AI選定理由【全候補】

正式採用済みのKey Phrase最大7件＋Key Word最大5件の候補生成方式と連携する。

- 全候補に、日本語1文・40字以内のAI選定理由を生成する。
- フォームに英語表現・エンドユーザー向け日本語訳・AI選定理由を表示する。
- AI選定理由はユーザーの確認・選定のための情報とし、エンドユーザー向け公開コンテンツには含めない。
- 従来方式など、理由が実際に存在しない候補は「AI理由なし」等を表示せず、理由欄を非表示にする。
- 正式7＋5方式に移行後は、理由の欠落を正常状態として扱わない。

Key Phrase／Key Wordの候補生成Prompt、データ保存、Gate、Human Review、フォームへの受渡しまで理由が失われないことを確認する。

## 5. ユーザー確定内容の保護【全6経路】

ユーザーが選定・確定した以下の内容を、正式Productionの後続工程で無断変更しない。

- Key Phrase／Key Wordの英語表現
- 対応する日本語訳
- ①②③の選定区分
- 採用した文法名と解説全文

Family Zで確認された日本語訳の再生成・上書きや、本文変更時の確定内容の退避・再生成といった既知の問題を是正する。

確定内容は、Human Review・本文表示・音声生成・組立・公開まで一貫して保持する。

retry／fallback／regeneration／resumeでも内容が不当に変化しないようにする。

本文変更などで確定内容と整合しなくなった場合、黙って書き換えず既存の品質Gateに従って停止・確認する。

既存のOpus独立レビュー結果を反映し、必要十分な保存・照合・fail-closed機構を実装する。

確定内容の保護を全6経路で検証する。

## 6. 既存仕様との整合・不整合是正【重要】

実装に際して、次を確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- 既存Part 2文法解説仕様
- Trial-08選定方式
- KP／文法Human Review
- Family X/Y/ZのProduction runner
- retry／fallback／regeneration／resume
- 公開ページ生成・表示処理

**今回のユーザー承認が既存仕様より優先する。**

特に以下を調査・是正する。

1. 文法解説をAdvancedに限定する旧記述・コード条件・表示条件。
2. Standardで文法候補の生成やHuman Reviewを実行しない旧経路。
3. 文法解説を選定後に生成する旧処理。
4. ユーザー確定後に英語・日本語訳・解説が再生成・上書きされる経路。
5. Family間でフォーム連携・文法公開処理が異なる部分。
6. 旧仕様を参照するretry／fallback／Validator／テスト。

ユーザー承認と矛盾する制限は撤去または更新する。

古い記録は履歴として残してよいが、**現行の承認済み仕様として参照されないようにすること。**

Dangling Referenceを解消し、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSに今回の正式決定を記録する。

既存仕様と今回の承認に矛盾がない部分は維持する。今回の4項目以外の仕様を独断で変更しない。

## 7. 既存7＋5方式・Gateとの整合

別途APPROVED_FOR_PRODUCTIONの以下の仕様と整合させる。

- Key Phrase最大7件
- Key Word最大5件
- Key Word抽出の正式採用済み5条件・補足・出力規則
- 選定済みフレーズに含まれる単語の候補除外
- Gateで実際に除外された候補数だけの補完
- KP救済方式

既存の品質Gate・Human Review Lockを維持する。

候補生成・フォーム実装・文法事前生成は独立部分を並列化し、相互の接続時に整合検証する。

7＋5方式自体のPRODUCTION_WIRED判定と、フォーム／文法解説の判定は区別する。

## 8. 必須検証・Production Wiring受入条件

対象6経路：

| Family | Standard | Advanced |
|---|---|---|
| X | 必須 | 必須 |
| Y | 必須 | 必須 |
| Z | 必須 | 必須 |

各経路で以下を確認する。

1. 正式初回Productionで候補データが選定フォームへ渡る。
2. 英語・日本語訳・AI選定理由が表示される。
3. ①②③の上限・排他選定が守られる。
4. 文法候補と事前生成した解説全文がフォームに表示される。
5. ユーザー確定内容が正しく保存される。
6. 確定した文法解説がStandard／Advanced双方の公開ページに反映される。
7. ユーザー確定内容がretry／fallback／regeneration／resumeで維持される。
8. KP救済・Gate除外補完・Human Reviewとの整合が保たれる。
9. 必須Regression／Validator／Integration TestがPASSする。
10. actual model_id、routing、Prompt、正式runtimeの生成・確定・公開証拠を取得する。
11. SSOT更新・Git反映を完了し、Fable独立受入を得る。

DEV/Trial経路だけの成功をProduction Wiringの証拠としない。

一部Family・レベルだけの検証をもって全体完了としない。

ユーザー実操作確認が未完了の場合は、その事実を明示し、受入Statusを混同しない。ただし、独立した実装・検証は継続する。

## 9. QCD・STOP条件

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 承認済み品質を維持し、最速で全6経路を完成させる。
- 独立作業は並列化する。
- 既存のTrial、生成結果、テスト資産を再利用する。
- 不要な本文・音声の再生成を避ける。
- 重複する文法生成・検査・API呼出しを撤去する。
- 量産単価70円／記事セットを目標とし、増分費用を最小化する。
- 開発費は原則1,000円／日（JST）、個別承認枠内で管理する。
- 既存承認範囲の不具合は原因究明・修正・検証まで自律対応する。

未承認の新仕様・品質基準変更、重大な品質／安全問題、予算超過、解決不能なblockerはSTOPして報告する。

## 10. 最終報告

以下の順序で報告する。

1. **全6経路のProduction Wiring Status**
2. フォームv3の正式採用仕様・公開URL
3. Standard／Advancedそれぞれの文法解説事前生成・公開結果
4. Key Phrase／Key Wordの選定理由付与状況
5. ユーザー確定内容の保護・後続工程一致
6. 旧Advanced限定仕様・旧コード条件・SSOT不整合の是正結果
7. Gate／Human Review／retry／fallback／resumeの検証結果
8. QCD実績
9. Fable受入・SSOT/Git・残Open Item

**完了条件：全6経路で、ユーザーが正式承認した仕様とProduction実動作の一致を証明すること。**

未完了・未観測の経路は明示して追跡し、全6経路が揃うまで一括してPRODUCTION_WIREDと判定しないこと。

(原文ここまで)

## 既知の前提(Fable把握分。コードで再確認)

- Part 2文法=`er120_part2_grammar_production_01.py`/`er120_part2_wiring_01.py`: Step A''(候補抽出、`extract_signature`にprompt sha/MODEL)→HR(英文1つ選択、最大1)→Step B(解説生成、`explain_signature`)。現行はAdvanced(b1b)のみ、Std(a2)にはPart 2なし。文法HR=`er119_grammar_review_01.py`、統合依頼書=`er119_kp_wiring_01.py:99`。Trial-08選定方式はCURRENT_SPEC Grep `Trial-08`。
- 確定内容保護(KCP、並行実装中): 文法sidecar `<study_dir>/confirmed_grammar.json`(`confirmation_id`)、Part 2凍結(M6: `frozen:<sha>`+選定文逐語span+candidate_id、revoke必須)。フォームpayload v2(`DATA_MODEL_02.md`): grammar=`{name, explanation_full, ...}`最大2件。
- フォームv3は文法「文法名+解説全文・最大2件」、現行Productionの確定は1件(型不一致=旧UDR-FORM-1、今回ユーザー決定で「文法は独立枠で最大2件」「採用した文法解説を公開ページに表示」が正式仕様=2件採用時の公開表示も設計対象)。
- 7+5(PRODUCTION_WIRED、b5de6ee5b): 全候補`reason_ja`。旧Prompt 2 docは理由なし→フォームは理由欄非表示へ(FORM側で対応)。

## 実施事項

1. **現行フロー(`CURRENT_FLOW_01.md`)**: X/Y/Z runnerのPart 2呼出(stage・level条件・HR・Step B・ページ描画・retry/regenerate/resume)をファイル:行で。Std(a2)の学習ページ構成(Part 1/Part 2相当の有無、ページbuilderのlevel分岐)。Y/Zの差(Z `part2_cand` input_sha等)。
2. **Advanced限定の棚卸し(`ADV_ONLY_INVENTORY_01.md`)**: ユーザー§6の1〜6を、SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/PM_GOVERNANCE Grep `Part 2|文法|grammar|b1b.*のみ|Advanced.*のみ|Trial-08`)・コード(Grep `b1b|level == |is_advanced|part2` in er120/er119_grammar/er019/er121/er026/er063/page builders)・test・Validatorで列挙し、「撤去/更新/履歴化/維持」を判定(今回のユーザー承認が優先。範囲を狭めない)。
3. **設計(`DESIGN_01.md`)**: (a)工程順: 候補抽出(Step A''、Std/Adv共通。Std本文への適用可否=Prompt/閾値は無変更で入力levelだけ変える。Std本文で候補が出ない場合の扱い=空候補を正常として記録)→**候補ごとにStep B解説を事前生成**(承認済み解説Prompt・文章量を無変更、候補数×約¥0.3)→フォーム/HRへ「文法名+解説全文」→ユーザー確定(最大2件)→確定レコード(KCPの`confirmed_grammar.json`、凍結)→公開ページ表示(Std/Adv双方。2件採用時の表示順・構成。Std学習ページに文法節を新設する場合の最小構成=Advと同一テンプレート再利用)。(b)旧「選定後Step B」の重複防止(事前生成済み解説の再利用、signature/freezeとの整合、`--regenerate-stage part2_*`の扱い)。(c)文法HR(`er119_grammar_review_01.py`)とフォーム確定の関係(HR CLI経路でも解説全文を見せる)。(d)X/Y/Z共通核への配線点(Family間差の解消)。(e)KCP M6凍結との接続(事前生成解説のsha固定、確定後再生成禁止)。(f)Trial-08選定方式との整合(選定基準は無変更、提示物に解説全文が加わるだけ)。(g)費用: 候補数実測(既存run docの`part2_cand`件数、Std想定)×Step B単価(usage log実測)で/記事・/レベル・量産単価影響。(h)旧仕様参照のretry/fallback/Validator/test一覧と更新方針。
4. **実装計画・test計画・evidence計画(6経路、見積≤¥40)**、Opus論点(工程順変更の副作用/Std本文への候補抽出の妥当性/事前生成とM6凍結の整合/重複防止/2件採用の公開表示/Family差解消/費用)。

## 事前指定Read一覧

- `er120_part2_grammar_production_01.py`(構造+Grep `def |b1b|level|signature|Step` ±5)、`er120_part2_wiring_01.py`(全体)、`er119_grammar_review_01.py`(構造)、`er119_kp_wiring_01.py:80-120`
- runner: `er019_family_x_audio_production_runner_01.py`/`er121_family_y_runner_01.py`/`er026_family_z_fiction_production_runner_01.py` Grep `part2|grammar|b1b` ±8(HEAD版=`git show origin/main:<path>`)
- page builders: Grep `part2|grammar|文法` in `er019_*page*.py`/`er121_family_y_audio_01.py`/`er063_family_z_audio_01.py` ±8
- `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md`(文法sidecar・M6)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_02.md`(grammar schema)
- SSOT Grep: `CURRENT_SPEC.md` `Part 2|Trial-08|文法解説|grammar` ±5、`OPEN_ITEMS.md` `文法|Part 2|UDR-FORM-1` ±2、`DECISION_LOG.md` `Part 2|Trial-08` ±2

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG1.md`にOPEN新規起票文案(APPROVED_FOR_PRODUCTION 2026-10-27、DESIGN_READY)、CURRENT_SPEC旧記述の履歴化文案、UDR-FORM-1解消文案。

## Git

- commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01: 文法解説事前生成(全6経路・Std/Adv)の現行フロー・Advanced限定棚卸し・設計・実装計画・Opus依頼(read-only、API 0)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/01`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG1.md`: (0)T-0、(1)現行フロー要点、(2)Advanced限定棚卸し(撤去/更新/履歴化/維持)、(3)設計要点(a)〜(h)+Fable設計判断事項(推奨付き)、(4)実装/test/evidence計画・費用見積、(5)Opus論点、(6)判断候補(新たな仕様判断が必要な場合のみ)、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。