## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01(ユーザー正式採用[APPROVED_FOR_PRODUCTION]の「学習項目選定フォームv3」をWebへ移植・公開し、『猿の手』Advancedに候補を入力した試作フォームでユーザー実操作確認に供する。参照コード=`docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`[UI・操作仕様の基準、Git保全]。API 0・JPY0)。並行Agent: KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01(補完機構の設計、read-only+docs)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・leaf)。あなたの所有=`docs/pm/Phrase_Form/**`(参照HTMLは**無改変**でGit追加)、フォーム公開先(既存Family X記事選定フォームの公開方式を調査のうえ決定。候補: `user_test/selection_form_v3/`または既存フォームと同じdir配下)、フォームの実装(静的HTML/JS、候補データJSON)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{SURVEY_01,PORT_01,DIFF_01,DATA_MODEL_01,SEND_CHECK_01,VERIFY_01,TEST_01}.md`+test、`docs/pm/delegation_log/2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM1.md`。Production Python経路(`er119_*`/`er105_*`/`er003_*`/`er125_*`/Family runner)は**編集禁止**(候補の読み出しは既存のkp_candidates.json/HR依頼書/Trial成果物から)。SSOT編集権なし。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様のProduction実装(フォーム=ユーザー操作面)。到達上限Status=**IMPLEMENTED+公開+自己検証済み(ユーザー実操作確認待ち)**。PRODUCTION_WIRED判定は受入条件11項目(ユーザー原文§6)が全て揃ってからFableが行う(フォームと補完機構を一括でWIREDと報告しない)。
- 禁止: 文章仕様からのUI再設計(参照HTMLの画面構成・操作・累積制約を維持。技術的に必要な移植・保存方式調整のみ許容し、差異は`DIFF_01.md`に全件記録)、7+5候補生成PromptのProduction採用・配線、本文への新表示機構(①②③ハイライト)のProduction配線(公開ページ仕様との照合結果を記録するのみ)、参照HTML内の文法仮データの正式記事への流用、未検証の送信機能を「動作確認済み」と報告すること、禁止Git操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`)。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): フォーム単体は条件A非該当(UI移植)。データモデル・送信方式に新規構造が出た場合は`OPUS_REVIEW_REQUEST_01.md`に論点を用意(Fableが任意レビュー要否判断)。
- 修正範囲の線引き(11-8): 範囲内=参照HTMLの忠実移植、9記事対応データ構造、記事切替の状態分離、自由コメント、送信(ChatGPT)検証+ワンクリックコピー、公開・検証。範囲外=候補生成Prompt、Gate、公開ページの表示変更、Claude Code直接送信(将来拡張)。
- 時間見込み: 約4h(調査0.5h/移植2h/試作データ+送信検証0.5h/検証・文書1h)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行Read、全文Readは構造把握時のみ(参照HTMLは全文Read可)。G-1: git出力最小化。F-1: transcript退避不要。T-0(全委任常時有効): 委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSなし。T-3: 費用なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_01.md` をN=685から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01」のものを採用(同時刻に別委任1件あり、先頭一致必須)。ユーザー原文2通(下記)を`..._USER.md`へ逐語保存(**あなたが作成**。並行の補完機構Agentはこれを参照)。

## ユーザー指示(原文・逐語、2通)

### 原文1

# 【正式Production採用・実装指示】学習項目選定フォーム＋Key Phrase候補ドロップ補完｜Family XYZ共通

## 1. 承認内容・目的

ユーザーは以下の2機能を正式採用した。

**Status：APPROVED_FOR_PRODUCTION**

対象：Family X／Y／Z、Standard／Advanced。

1. 学習項目選定フォームv3
2. GateでNG除外されたフレーズ・単語候補の不足分補完

今回の目標は、実装・正式経路接続・テスト・runtime evidence・SSOT/Git反映まで完了し、PRODUCTION_WIREDに到達すること。

ただし、技術的な配線だけで完了扱いにせず、実際に1記事でユーザーが操作確認する工程を設ける。

既存Production仕様、Human Review、Key Phrase救済方式、文法解説仕様との整合を必須とする。

## 2. 学習項目選定フォーム

### 2-1. コードを基準に実装

添付の `eigo_radio_selection_form_reference.html` を参照実装とする。

これはChatGPT上でユーザーが操作・承認したフォームv3を、通常のWebブラウザ向けに移したコードである。

**文章仕様からUIを作り直さず、このコードの画面構成・操作・累積制約を維持すること。**

既存のFamily X記事選定フォームのRepo構成・公開方式を調査し、可能な限り再利用する。

技術的に必要な移植・保存方式の調整は許容するが、ユーザー承認済みのUI動作を独断で変更しない。

### 2-2. 選定仕様

フレーズ最大7件、単語最大5件を候補として表示する。

各候補の右側に①②③のチェック列を設け、同一候補は1区分だけ選べる。

上限は累積管理する。

- ① Key Phrase：①単独で最大3件
- ② 追加解説：①＋②で最大5件
- ③ 本文意味表示：①＋②＋③で最大12件

上限到達時は背景色・表示を変更し、それ以上の選択を防ぐ。選択解除・変更は常に可能とする。

①②③はいずれも本文中でレベルに応じてハイライトする対象。③は簡潔な意味表示を目的とし、追加の詳細解説・TTS生成は要求しない。

ただし、本文への新しい表示機構のProduction配線は、既存の公開ページ仕様と照合し、未承認の表示変更を先行実施しないこと。

### 2-3. 文法選定

文法はフレーズ・単語と完全に独立して管理する。

- 最大2件
- チェック方式
- 文法名とエンドユーザー向け解説本文を全文表示
- 既存のPart 2文法解説生成・選定仕様と整合

参照フォーム内の文法例は仮データであり、正式記事への流用禁止。

### 2-4. 記事管理・コメント・送信

- 9記事に対応できる構造とする。
- 各記事・レベルの候補、選択状態、文法、コメントを区別する。
- 記事切替時に選定結果が混在・消失しないようにする。
- 候補の部分修正・追加要求を書ける自由コメント欄を設ける。
- 選定結果は構造化データとして保持し、将来のClaude直接送信に利用可能とする。

今回の送信方式は、

**フォーム → ChatGPT → Claude Code**

とする。

「ChatGPTへ送信」を備え、実際に選定結果がChatGPTへ渡るか検証する。

直接受渡しが環境上できない場合は、ワンクリックコピーを必須の代替機能とする。

未検証の送信機能を「動作確認済み」と報告しないこと。

Claude Codeへの直接送信は将来の量産拡張であり、今回の実装対象外。

### 2-5. 公開と検証

既存のFamily X記事選定フォーム同様にRepoへ保存し、ユーザーが開けるURLを公開する。

Claudeが今後、フレーズ・単語・文法の判断をユーザーに依頼するときは、候補を入力済みの対象記事フォームURLを報告に掲載する。

まず『猿の手』Advancedを試作確認対象とする。

9記事すべてを制作する必要はないが、9記事に拡張できることを構造・テストで確認する。

## 3. Gate除外候補の補完機能

### 3-1. 発動条件（最重要）

**補完は、AIが一度選定した候補が後続GateでNG除外された場合に限る。**

単に初回選定件数が上限未満という理由で発動させないこと。

具体例：

| 初回AI選定 | Gate除外 | 補完 |
|---|---|---|
| フレーズ5件／最大7件 | 0件 | なし |
| フレーズ7件／最大7件 | 2件 | 最大2件 |
| 単語4件／最大5件 | 0件 | なし |
| 単語5件／最大5件 | 1件 | 最大1件 |

**補完件数＝実際にGateで除外された件数。**

対象はフレーズ・単語の両方。

初回に合格した候補は保持し、再生成・入れ替えをしない。

### 3-2. 補完処理

- 除外件数だけ追加候補を探索する。
- 初回候補・既存合格候補を踏まえ、重複や同じNGの繰り返しを防ぐ。
- 補完候補にも承認済みの品質基準・Gateを適用する。
- 補完候補が不合格でも品質基準を緩和しない。
- 見込みのない同一処理の反復を避ける。
- 補完後も上限未達なら、その結果を許容する。

既存のKP救済方式と処理順序を確認すること。

救済によって正式な候補として残ったものを、誤って「Gate除外」と数えて補完しないこと。

Human Review限定候補、Human NG、retry、fallback、resume、再生成との整合を確認する。

既存の正式な候補生成経路だけでなく、必要な後続経路にも矛盾なく組み込む。

### 3-3. 単語抽出の優先順位

単語の初回抽出・補完抽出とも、ユーザー指定の優先順位を厳守する。

1. 本文一致（絶対条件）
2. 1語（絶対条件）
3. 上級者向けの学習価値
4. 易しい語の除外
5. 単語単体の学習価値（必須条件ではない）

過去の7＋3 Trialで発生した、条件⑤の必須化・優先順位逆転を再発させないこと。

フレーズに含まれる単語の重複扱いについては、既存Production Gateと承認済み仕様の整合を確認する。未承認のGate緩和を行わない。

## 4. 既存仕様との整合

着手前に、以下を確認する。

- CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS
- KP候補生成7＋5 Trialと既存Production方式の関係
- KP救済方式の最新Production Wiring
- KP Human Review・文法Human Review
- Part 1／Part 2文法解説と公開ページ
- Family別正式初回経路、retry／fallback／resume
- Family X既存記事選定フォームの実装・公開方法

なお、今回承認されたのは「7＋5方式の候補上限を前提とする選定フォーム」と「Gate除外分の補完」である。

過去の7＋5 Trialで判明した数合わせ品質問題を無視して、7＋5候補生成Prompt自体のProduction採用を自動確定してはならない。

新しい候補生成Prompt、採用枠、Gate変更が必要になった場合は、既存承認の範囲と区別して報告すること。

## 5. 実施・QCD

品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用。

フォームのWeb移植と候補補完機構は、競合しない範囲で並列に進める。

既存コード・データ・テストを再利用する。

開発費は日次1,000円（JST）と既存個別承認枠を守り、費用の内訳・量産単価への影響を計測する。

承認済み仕様内の不具合は自律的に原因究明・修正・検証する。

仕様変更・品質基準変更・新規Trial範囲・承認外費用が必要ならSTOPして判断を求める。

## 6. Production Wiring受入条件

Family X／Y／Zの各Standard／Advancedについて、次を確認する。

1. 承認済みのフォーム仕様・選定制約との一致
2. 正式候補生成経路におけるGate除外・補完の動作証拠
3. Gate除外0件では補完が発動しないこと
4. 初回選定が上限未満でも補完が発動しないこと
5. 補完後のGate再検査と重複防止
6. retry／fallback／resume／Human Review／KP救済との整合
7. 必須Regression／Validator／Integration Test PASS
8. actual model_id、Prompt、routing等のruntime evidence
9. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
10. Git反映
11. 公開フォームURLからの実操作確認

特に、実際のユーザー操作で試作フォームが承認仕様どおり機能することを確認する。

**APPROVED_FOR_PRODUCTIONからPRODUCTION_WIREDへの変更は、すべての必要なGate条件が揃ってから行う。**

一部Familyでの成功やDEV経路での成功だけをもって、全Family完了としない。

## 7. 最終報告

次の順序で簡潔に報告すること。

1. 結論・機能別Status
2. 選定フォーム公開URLと実操作確認状況
3. 参照コードとの一致・差異
4. Gate除外補完の実測結果・具体例
5. Family X／Y／Z別Production Wiring証拠
6. QCD（処理時間・量産単価・開発実費）
7. 残存Open Item・ユーザー判断事項
8. Git commit・SSOT更新結果

フォーム・補完機構のいずれかが未完成の場合、両方を一括してPRODUCTION_WIREDと報告しない。

未承認の関連仕様は自動採用せず、USER_DECISION_REQUIREDとして切り分けること。

### 原文2

【追加指示｜選定フォーム参照コードの保存先】

先ほどの「学習項目選定フォーム＋Key Phrase候補ドロップ補完」の指示について、フォーム参照コードの保存先を連絡します。

**保存先（ローカルRepo内）：**
`C:\Users\tensh\eigo-radio\docs\pm\Phrase_Form\eigo_radio_selection_form_reference.html`

このファイルを、ユーザーが正式承認したフォームの**UI・操作仕様の基準コード**として使用してください。

- 文章から独自にUIを再設計せず、当該HTMLを基準にWebフォームを実装する。
- チェック方式、①②③の累積上限、文法の独立管理、自由コメント、9記事対応など、承認済みの操作仕様を維持する。
- 既存のFamily X記事選定フォームの公開方式を可能な限り再利用する。
- 参照HTMLはRepoにGit反映し、正式な参照コードとして保全する。
- 実装後、公開URLと動作確認結果を報告する。

**その他の指示内容・承認範囲・Production Wiring受入条件に変更はありません。**

フォーム実装とGate除外候補の補完機能は、引き続き並列で進めてください。

(原文ここまで)

## Fableの実施指示

1. **調査(`SURVEY_01.md`)**: 既存「Family X記事選定フォーム」の実装・公開方式(Grep `選定フォーム|selection_form|theme_selection|記事選定` 全repo・`user_test/`・`docs/`、GitHub Pagesの公開path規約=`user_test/<name>/index.html`)、Part 2文法解説の候補データ形式(Grep `grammar_candidates|part2|Part 2` in `er119_*`/`er003_*`、HR依頼書`HR_REVIEW_REQUEST_01.md`の文法節)、KP HR候補データ形式(`kp_candidates.json`、`er119_kp_human_review_01.py`の候補schema)、公開ページの①②③ハイライト相当の既存表示(KP下線・単語解説・本文意味表示の有無)を事実で整理。
2. **移植(`PORT_01.md`+実装)**: 参照HTMLを全文読み、画面構成・操作・累積制約(①≤3、①+②≤5、①+②+③≤12、同一候補1区分、上限到達時の背景色・無効化、解除常時可)・文法独立(最大2、チェック、文法名+解説全文)・自由コメント・9記事対応・記事切替の状態分離を**そのまま**維持。候補データは外部JSON(`data/<article_slug>__<level>.json`: フレーズ最大7・単語最大5・文法候補・本文抜粋・意味)から読み込む方式に調整(参照HTMLの埋め込みデータ→JSON化は許容される保存方式調整。`DIFF_01.md`に全差異を列挙: 理由・UI影響なしの根拠)。選択状態は`localStorage`に記事×レベル単位で保存(消失・混在防止)。構造化出力JSON(記事・レベル・①②③選択・文法選択・コメント・timestamp・schema version)を生成。
3. **送信(`SEND_CHECK_01.md`)**: 「ChatGPTへ送信」=構造化JSON+人間可読テキストを生成し、(a)`https://chatgpt.com/?q=<encoded>`型のURL起動が選定結果を渡せるかを実際にブラウザで確認できる形にする(あなたは実ブラウザ検証ができない場合、「未検証」と明記し、ユーザー実操作確認の項目に入れる)、(b)**ワンクリックコピー**(clipboard API+フォールバックのtextarea選択)を必須実装。「動作確認済み」と書けるのはあなたが実際に検証できた範囲のみ。
4. **試作データ(猿の手 Advanced)**: 候補=`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/RESULT_02.md`の猿の手 b1b(フレーズ7+単語4、Gate通過分。救済済み句`pulled free`は旗付きで表示)を入力。**明記**: この候補はDEV Trial-02由来(Production候補生成Promptは現行3+最大5・単語0件のまま。7+5 Promptは未採用)。文法候補=猿の手Advの正式Part 2候補(存在すれば実データ、無ければ「候補なし・要生成」と表示し仮データは入れない)。本文=確定本文(`er0XX_output`の猿の手 b1b article)。9記事対応はデータdirに`articles.json`(index)を置き、テストで9件のダミーindex(本文なし・slugのみ)で切替・状態分離を確認。
5. **test(`TEST_01.md`)**: ブラウザなしで検証できる部分=JSON schema検証、累積制約ロジック(JSを関数化しnodeまたはpythonで単体test。node不在なら`.venv`のpythonでロジック同等実装をtest+JSとの対応表)、9記事切替の状態分離、出力JSONの構造。
6. **公開・検証(`VERIFY_01.md`)**: 既存フォームと同じ方式(`user_test/<name>/index.html`+`data/`)。push後HTTP 200、リンク、JSON読込、Console errorなし(可能な範囲)。公開URLを報告。
7. **ユーザー実操作確認手順**: 報告に「確認項目チェックリスト」(①②③上限の挙動、文法2件、記事切替、コメント、送信/コピー)を付ける。

## 事前指定Read一覧

- `docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html` 全文
- `docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/RESULT_02.md` 猿の手 b1b節
- `docs/research/FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01/HR_REVIEW_REQUEST_01.md`(HR依頼書の候補・文法の形式)
- `er119_kp_human_review_01.py`: Grep `KP_CANDIDATE_MAX|grammar|candidate|schema` → ±10
- 既存フォーム(調査で判明したpath)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_01.md_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "<新規test名>"`(接続0)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_FORM1.md`(9)にOPEN新規起票文案(11-8分類: フォーム=APPROVED_FOR_PRODUCTION・IMPLEMENTED・ユーザー実操作確認待ち)、CURRENT_SPEC新節案(選定フォームv3仕様)、判断候補(候補ソース: 現行Prompt[単語0]か7+5 Promptか=ユーザー判断事項として切り分け)。

## Git

- add対象: `docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`(無改変)、フォーム公開dir、test、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/`、delegation_log。pathspec付きcommit。
- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01: 学習項目選定フォームv3 Web移植(参照HTML保全、①②③累積上限・文法独立・9記事・コメント・送信/コピー)+猿の手Adv試作公開(API 0)`
- trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/01`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_FORM1.md`: (0)T-0、(1)調査結果(既存フォーム方式・再利用点)、(2)公開URL+実操作確認チェックリスト、(3)参照コードとの差異全件、(4)送信検証の事実(検証済み/未検証)、(5)試作データの出所と注記、(6)test・検証結果、(7)判断候補(候補ソース等)、(8)必須4行+「判定整合: 重大NG=<なし|あり>」、(9)SSOT文案、(10)一覧外Read、commit hash、raw URL。末尾10行要約。