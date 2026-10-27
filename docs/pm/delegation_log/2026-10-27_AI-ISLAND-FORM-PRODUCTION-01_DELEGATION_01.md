## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_01(ユーザー指示2026-10-27「Family X『AIの仮想の島』V3フォーム実運用・完成記事制作」の**第1報(ユーザー選定待ち)まで**: 既存成果の照合→KP 7+5候補(既存正式生成結果の再利用)→文法候補の事前準備(Std/Adv、承認済みStep A''/Step B品質を無変更で今回記事限りの暫定事前生成=正式配線とは区別)→V3フォームへ登録→選定可能状態。**完成記事制作はユーザー選定前に進めない**。有料上限¥15(文法Step A''×2 level+Step B×候補数、KP再生成は原則不要))。並行Agent: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02(`er120_*`/`er119_grammar_review_01.py`を作業ツリーで編集中=**Production関数は`git show origin/main:<path>`で固定版をimportして使う**(委任_02Sの`tools/std_candidate_rate_01.py`の方式を流用)。Production Pythonは編集しない。あなたの所有=`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{SURVEY_01,GRAMMAR_PREP_01,FORM_REGISTRATION_01,COST_01,USER_GUIDE_01}.md`+`tools/`+`grammar_prep_out/`(raw_usage_log不追跡)、`user_test/selection_form_v3/**`(AI島Std/Advのデータ更新・`articles.json`)、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(文法items取込の最小拡張のみ=`form_grammar_items`契約`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_01.md`が既にcommit済みならそれに従う。未commitなら`DATA_MODEL_02.md`のgrammar schemaで)、`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF1.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit(`git commit <pathspec>`を必ず使い、indexの他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み仕様(フォームv3・7+5・事前生成の暫定運用)の実運用準備。到達上限=フォーム登録完了・第1報材料。
- 禁止: 記事本文の再生成、ユーザー選定の代行、旧HRでユーザーが明示確定した内容の破棄・上書き、公開済み/進行中runの改変(新しい選定結果は新run/新dirで追跡)、Prompt/品質基準変更、旧Trial/旧Production候補の最新版としての表示、Gate緩和、¥15超過、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER.md`へ逐語保存。T-2(有料前): `py tools/stop_scope_check_01.py --managed-id AI-ISLAND-FORM-PRODUCTION-01 --run-dir <対象> --out <...>`。T-3: 費用実測。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_01.md` をN=720から順に試し、先頭「## 管理ID」+「AI-ISLAND-FORM-PRODUCTION-01 委任_01」のものを採用。

## ユーザー指示(原文・逐語)

# Claude Code指示｜Family X「AIの仮想の島」V3フォーム実運用・完成記事制作

## 1. 目的・作業範囲

Family X「AIの仮想の島」について、既存の記事本文を再利用し、学習項目選定フォームv3を使ってKey Phrase／Key Word・文法をユーザーが選定するところから、Standard／Advancedの完成記事制作・最終試聴ページ公開まで進めてください。

今回の目的は次の2点です。

1. 「AIの仮想の島」を正式な完成記事にする。
2. V3フォームによる選定から記事完成までの実運用を検証する。

**対象：Family X「AIの仮想の島」Standard／Advanced**

今回の実運用は、全Family共通のフォームProduction Wiring作業とは区別して管理する。

## 2. 既存成果の再利用

最初にRepo・既存run・CURRENT_SPEC・OPEN_ITEMSを確認する。

特に以下を照合する。

- 既存Standard／Advanced本文の最新版と承認状態
- OPEN-526（AI島Human Review関連）
- 既存Key Phrase候補・Human Review結果
- Key Phrase 7件＋Key Word 5件の正式Production仕様
- Part 2文法解説・Trial-08選定方式
- 選定フォームv3
- ユーザー確定内容の保護機能の実装状況

**記事本文は原則として再生成しない。**

既存の承認済み本文・音声・その他の制作成果を再利用する。

既存runを破壊せず、新しい選定結果と旧結果の区別・追跡ができるようにする。

ただし、旧Human Reviewでユーザーが既に明示的に確定した内容については、無断で破棄・上書きしない。今回の選び直しと競合する場合は承認履歴を照合し、必要な判断のみ報告する。

## 3. Key Phrase／Key Word候補の準備

正式採用済みの最新方式を使用する。

- Key Phrase：最大7件
- Key Word：最大5件
- 合計最大12件
- 学習価値順に順位付け
- 数合わせは不要
- 全候補にAI選定理由（日本語1文・40字以内）
- エンドユーザー向け日本語訳を付与

Key Wordの5条件・補足規則・出力規則、フレーズ包含単語の除外を維持する。

Gate除外候補補完・KP救済方式を含め、正式Productionの承認済み処理を利用する。

**既存の7＋5方式の正式生成結果が、その本文に対して既に利用可能であれば、不要な再生成を行わない。**

再生成が必要な場合も、対象は原則としてKP候補生成工程に限り、記事本文を再生成しない。

## 4. 文法候補の準備

今回正式採用された事前生成方式を使用する。

- 文法候補ごとに文法名とエンドユーザー向け解説全文を準備する。
- Standard／Advanced双方を対象とする。
- 既存Part 2文法解説・Trial-08方式と整合させる。
- ユーザーが解説全文を読んで選定できるようにする。
- 選定後に解説を再生成しない。

事前生成方式の正式Production配線が未完成の場合、承認済みの品質仕様を保ったまま、今回の記事に限って選定前に解説を準備することは認める。

ただし、その実運用上の暫定対応を正式Production配線完了と混同しない。

品質上必要なHuman Reviewは省略しない。

## 5. V3フォームへの登録・ユーザー提出

公開フォーム：

https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/

Family X「AIの仮想の島」Standard／Advancedの最新候補を登録し、ユーザーがすぐに選定できる状態にする。

表示内容：

- Key Phrase／Key Wordの英語
- エンドユーザー向け日本語訳
- AI選定理由
- ①②③の選択欄
- 文法候補の名称と解説全文
- 自由コメント欄

上限：

- ① Key Phrase：最大3件
- ①＋②：最大5件
- ①＋②＋③：最大12件
- 文法：独立枠で最大2件

候補の英語・日本語訳・選定理由・文法解説の対応関係を確認すること。

旧Trial候補・旧Production候補を誤って最新版として表示しない。

**準備ができたら、AI島Standard／Advancedを選定できるフォームURLと、必要最小限の操作説明だけを提出してください。**

この段階ではユーザーの選定結果を待つ。選定内容をClaude/Fableが代行決定しない。

## 6. ユーザー選定後の処理

ユーザーがフォームで選定し、ChatGPTに送信した確定内容を、正式制作工程に反映する。

送信内容のうち、以下を正確に引き継ぐ。

1. 選定されたKey Phrase／Key Wordの英語表現
2. それぞれの日本語訳
3. ①②③の選定区分
4. 採用された文法名・文法解説全文
5. 自由コメントと、そこから生じた明示的な修正判断

**ユーザー確定内容の無断変更は禁止。**

ChatGPTからClaudeへの受渡しは、現行の承認済み手順を使用する。未実装の直接連携を前提にしない。

確定内容保護機能の全体実装が進行中の場合も、今回の実運用では確定内容の保存と前後照合を必須とする。

本文との不整合などが発生した場合、黙って別候補・別訳・別解説へ変更しない。

## 7. 完成記事の制作

ユーザーによる選定後、Standard／Advancedを完成させる。

- 選定したKey Phrase／Key Wordを学習コンテンツに反映。
- ①②③の区分に応じた音声・解説・本文ハイライトを適用。
- 文法解説を両レベルの公開ページに反映。
- 既存の承認済みTTS Style・Voice・速度・Chunk仕様を維持。
- 必要な音声のみ生成・再利用し、不要なTTS再生成をしない。
- 正式組立・音声品質検査・公開検査を完了。

Human Reviewが必要な場合は、該当箇所のみ「原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価」の形式で提出する。

複数Takeの不要な比較や技術的判断をユーザーへ委ねない。

**完成後は、Standard／Advancedを通し再生できる通常の最終試聴ページを提出する。**

ユーザーの最終試聴承認までは、完成記事の受入完了としない。

## 8. V3フォーム実運用の検証

今回の記事制作を通じて、次の点を確認する。

- 候補の表示内容と元データが一致する。
- 日本語訳・AI選定理由が正しく表示される。
- 文法解説全文を選定前に確認できる。
- ①②③・文法の選定上限が正常に働く。
- フォームからChatGPTへの送信で情報が欠落しない。
- ユーザー確定内容が後続工程で変化しない。
- 最終公開ページに選定結果が正しく反映される。

今回の実運用で発見した不具合は、承認済み仕様・予算内で原因究明から修正・検証まで自律的に対応する。

新たな仕様変更が必要な場合だけユーザー判断を求める。

この1記事の成功だけで、全FamilyのPRODUCTION_WIREDを宣言しない。

## 9. QCD・進行管理

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 記事本文の再生成を原則禁止。
- 既存成果を最大限再利用。
- 独立作業は並列化。
- 不要なTrial・検査の重複を避ける。
- 品質Gateを緩和・省略しない。
- 量産単価70円／記事セットを目標とし、追加費用を最小化する。
- 開発費1,000円／日（JST）および個別承認枠を遵守する。
- STOP条件、Human Review Lock、承認境界を維持する。

## 10. 報告・Gate

### 第1報：ユーザー選定待ち

以下のみ簡潔に報告する。

1. AI島Standard／AdvancedのV3フォームURL
2. 候補数・文法候補数
3. 正式訳・未確定訳の有無
4. フォーム上の選定・送信準備が完了したか
5. ユーザーが行う操作

**第1報の段階では、完成記事の制作をユーザー選定前に進めないこと。**

### 第2報：完成記事提出

1. Standard／Advanced完成版の試聴URL
2. ユーザー確定内容との一致結果
3. 必須品質検査・Human Review結果
4. V3フォーム実運用で確認した事項
5. QCD・SSOT/Git・残Open Item

必要なGate・SSOT更新を完了し、Fable独立受入を実施する。

**最終目標は、AI島の完成記事をユーザーが通常どおり試聴・承認できる状態にすることです。フォームのために記事制作全体をやり直さないでください。**

(原文ここまで)

## 既知の前提(Fable把握分。コードと記録で再確認)

- AI島(`ai_island_temple`)のX production run群は`er019_output/family_x_audio_production_wiring_01/`配下。7+5のevidence doc=`ai_island_temple__run_kp75_ev_01`(a2 5+5=10件、b1b 5+5=10件、`kp_candidates.json`、HR待ちrc=4、全候補`reason_ja`、gloss official)。このdocは**どの本文(run/sha)から生成したか**を`text_sha256`/provenanceで特定し、最新の承認済み本文と一致することを確認(一致しなければ、承認済み本文に対してKP候補生成(7+5)のみを新run dirで実行=約¥2/level、本文再生成禁止)。
- OPEN-526: AI島の旧3+5候補でHR候補選択+案A/B/Cがユーザー判断待ちだった(Fable推奨A)。今回のユーザー指示(フォームで選び直し)により実質上書きされるが、「旧HRでユーザーが明示確定した内容」があるかをHR記録(`kp_human_review.json`の`approved_by=user`/`op_select --by user`等)で照合し、あれば報告(無ければ「明示確定なし」と記録)。
- フォームには既に`ai_island_temple__a2/b1b`(kp75 doc由来、FORM委任_04で登録)が載っている。最新本文との対応・旧3+5版(`data/legacy/`)が非表示であることを確認。
- 文法: 現行Production Part 2はAdvのみ・選定後生成。今回は**今回記事限りの暫定事前生成**(Step A''でStd/Adv候補抽出→候補ごとにStep B解説生成。Production関数の固定版をimport、Prompt sha不変、model=routing.SUPPORT_MODEL、`ref_ja=None`、出力は`docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out/<level>/`+`SCHEMA_CONTRACT_01.md`の`grammar_explanations.json`形式があればそれで保存)。Std候補率実測ではX Std平均1.25件(AI島Stdは1→3件と揺れ)。候補0件なら「文法候補なし」として登録。
- 確定内容保護(er128): `confirm --from-form`でpayload v2(`candidate_id`/`kind`/`candidates_sha256`/文法items)を取り込める。第1報では使わない(選定後の委任_02で使用)。

## 実施事項

1. **照合(`SURVEY_01.md`)**: 最新承認済み本文(Std/Adv)のrun・sha・承認記録、既存音声の再利用可否、OPEN-526のHR記録とユーザー明示確定の有無、kp75 docの本文一致、フォーム登録済みデータの出所。
2. **KP候補**: kp75 docが最新本文と一致なら再利用(再生成しない)。不一致なら承認済み本文に対し正式経路(`er119_kp_wiring.run_kp_with_review`相当=X runnerのkp stageを新run dir `ai_island_temple__run_form_prod_01`で実行、本文は既存runからコピー、TTSは実行しない)で7+5生成。
3. **文法暫定事前生成(`GRAMMAR_PREP_01.md`)**: Std/Adv各本文でStep A''→全候補Step B(PREGEN_MAX=8)。出力に`candidate_id`/level/title(文法名)/explanation_md(解説全文)/translation_ja/explanation_sha256/model_id/prompt sha/費用。品質HR: 解説文の既存Validator(あれば)を通す。「暫定(正式配線前)」と明記。
4. **フォーム登録(`FORM_REGISTRATION_01.md`)**: `export_form_data_01.py`で最新KP docを再出力(`candidate_id`/`kind`/`candidates_sha256`/`ja_gloss_status`/`reason_ja`)、文法itemsをデータJSONに追加(`grammar: [{id, name, explanation_full, level, sha}]`、UIは既存の「文法名+解説全文」表示を使う)。`articles.json`でAI島Std/Advを最新版として先頭付近に(旧版が表示されないこと)。node/py test、公開headless(AI島Std/Advの候補数・訳・理由・文法解説全文の表示、上限動作)。英語・訳・理由・文法解説の対応関係を元データとdiffで確認。
5. **操作説明(`USER_GUIDE_01.md`)**: 必要最小限(URL→記事「AIの仮想の島」Std/Advを選ぶ→①②③と文法を選ぶ→コメント→「ChatGPTへ送信」または「全文コピー」→ChatGPTに貼り、ChatGPTの出力(構造化JSON+本文)をClaude Codeへ貼り付け)。
6. 第1報材料(5項目: URL/候補数・文法候補数/正式訳・未確定訳の有無/準備完了/ユーザー操作)。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_02,VERIFY_05}.md`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/build_data_01.py`
- `docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/EVIDENCE_01.md`(AI島doc)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_01(あれば),STD_CANDIDATE_RATE_01,tools/std_candidate_rate_01.py}`、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md`(from-form節)
- `OPEN_ITEMS.md` Grep `OPEN-526|ai_island|AI島` ±3、`CURRENT_SPEC.md` Grep `AI島|ai_island` ±3
- `er019_output/family_x_audio_production_wiring_01/`配下のai_island run一覧(dir名・更新日・`article.md` sha・`kp_human_review.json`の有無)
- `er120_part2_grammar_production_01.py`(origin/main固定版: Grep `def extract|def generate_explanation|STEPB|MODEL` ±10)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_01.md --json-out ...\_check.json`
- 文法暫定生成: `.venv\Scripts\python.exe docs\research\AI-ISLAND-FORM-PRODUCTION-01\tools\grammar_prep_01.py --article <a2/b1b article.md> --level a2|b1b --out ...\grammar_prep_out\ --budget-jpy 6`
- test: node test+`.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+headless(公開URL)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_AIF1.md`にOPEN新規起票文案(AI-ISLAND-FORM-PRODUCTION-01=実運用、暫定事前生成の区別、OPEN-526との関係)。

## Git

- commit message: `AI-ISLAND-FORM-PRODUCTION-01 委任_01: AI島Std/AdvをV3フォームへ登録(7+5候補再利用+文法解説の暫定事前生成、実費¥N)+照合・操作説明`。trailer: `Delegation: AI-ISLAND-FORM-PRODUCTION-01/01`。push。

## 報告

`docs/pm/RESULT_PACKET_AIF1.md`: (0)T-0、(1)照合結果(本文・OPEN-526・kp75 doc一致)、(2)KP候補(再利用/再生成の別)、(3)文法暫定事前生成(候補数・例・費用)、(4)フォーム登録・検証、(5)第1報材料5項目、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・公開URL・raw URL。末尾5行要約。