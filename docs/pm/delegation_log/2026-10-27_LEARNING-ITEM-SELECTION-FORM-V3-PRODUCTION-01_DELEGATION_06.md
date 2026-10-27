## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_06(ユーザー正式決定2026-10-27「V3フォーム送信・コピー改善の優先実装」APPROVED_FOR_PRODUCTION: (1)「ChatGPTへ送信」のURL長制限を踏まえ、公開フォーム→ChatGPTへの受渡しで実際に利用可能な方式を調査し最も簡単で安定した方式を採用(長いJSONをURLに載せる方式に固執しない。ChatGPT側で取得できない方式は不可。直接送信が困難なら1クリック全文コピーを正式代替=エラーではなく正常動作として案内)、(2)「選定結果をコピー」を人間可読形式(記事名/①②③ごとに「英語：訳」/文法名+解説全文/コメント)へ、JSON・SHA・candidate_id等の内部情報は表示から分離しつつ**データとして消失させず**Claudeが正確に復元・照合できること(照合不能な設計は不合格、ユーザーにJSON手編集を求めない)。本委任=**調査+設計+Claude側復元・照合toolの仕様(read-only、フォーム実装は委任_07=並行AgentのAI-ISLAND委任_02がフォーム編集中のため)**。API 0・JPY0)。ユーザー原文(下記)を`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_03.md`へ逐語保存。並行Agent: AI-ISLAND 委任_02(`user_test/selection_form_v3/**`編集中=読むのは`git show origin/main:<path>`)、GPG 05A(er128/CLI/exporter)、YSP 08、SYNC-21。あなたの所有=`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{HANDOFF_SURVEY_01,HANDOFF_DESIGN_01,COPY_FORMAT_01,RESTORE_TOOL_SPEC_01,TEST_PLAN_06,OPUS_REVIEW_REQUEST_02(必要時)}.md`、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_{USER_03,DELEGATION_06}.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM6.md`(gitignore、`-f`禁止)。コード/SSOT編集なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み改善の設計(新しい受渡し方式=Opus条件A該当の可能性: 新規バックエンド/外部サービス/識別子方式を採る場合は依頼文を用意。コピー形式の改善のみなら不要)。到達上限=DESIGN_READY。
- 禁止: 新たな有料外部サービス・複雑なバックエンドの前提(必要性が示せない限り)、ブラウザ保存データのみ参照する方式、照合情報(candidate_id/本文SHA/候補集合SHA)を失う設計、ユーザーへのJSON手編集要求、コード編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約1.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_06.md` をN=728から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_06」のものを採用。

## ユーザー指示(原文・逐語)

# Claude Code指示｜V3フォーム送信・コピー改善の優先実装＋AI島文法選定確定

## 1. ユーザー正式決定

以下を受領してください。

### A. AI島の文法再選定は不要

Family X「AIの仮想の島」について、Standard／Advancedともに文法0件を正式確定します。

- Key Phrase／Key Wordは、先に送付した両レベル各10件の選定結果を維持。
- 文法：Standard 0件、Advanced 0件。
- 文法の再選定・再提出を求めない。
- 旧フォームで選択した0件を、今回のユーザー明示判断によって最終確定とする。
- 文法0件を理由に記事完成工程を停止しない。

今回の判断はAI島個別の確定内容であり、全Family共通の文法選定仕様は「AI評価Top 1・Top 2を提示、原則1件、適切な候補がなければ0件」のまま維持します。

### B. V3フォームの送信・コピー方式を改善

現在、V3フォームで「ChatGPTへ送信」を押すと、送信内容がURLの長さ制限を超え、選定結果のコピーに切り替わります。

また、コピー結果にJSONなどの内部データが大量に含まれており、ユーザーの操作性が悪くなっています。

**これらを正式な改善対象とし、現在進行中のV3フォームProduction Wiring作業へ優先的に組み込んでください。**

Status：APPROVED_FOR_PRODUCTION  
到達目標：PRODUCTION_WIRED（X/Y/Z、Standard/Advanced）

## 2. 改善の目的

ユーザーがフォームで学習項目を選んだ後、できる限り**1回の操作でChatGPTへ選定結果を渡せること**を目標とします。

必要なデータを落とさず、JSON・SHA・candidate_idなどの技術情報をユーザーが読んだり編集したりする必要のない操作体験にしてください。

単なる表示の修正ではなく、「フォーム選定→ChatGPT→Claude→完成記事」の一連の工程で確定内容が正しく引き継がれることを受入条件とします。

## 3. 「ChatGPTへ送信」の改善

現在のURL方式の文字数制限と、公開フォームからChatGPTへの受渡しで利用可能な方式を調査し、最も簡単で安定した方法を採用してください。

優先する条件は以下です。

1. ユーザー操作が少ないこと。
2. 選定結果が欠落しないこと。
3. 英語、日本語訳、①②③区分、文法名・解説全文が正確に引き継がれること。
4. 候補ID・本文SHA・候補集合SHAなどの照合情報を維持すること。
5. 送信途中で意図せず内容が変更されないこと。
6. 新たな有料外部サービスや複雑なバックエンドを、必要なく追加しないこと。

**URLに長いJSONを載せる方式に固執しないでください。**

短い識別情報を送る方式なども検討できますが、ChatGPTがその識別情報から確定内容を安全かつ確実に取得できる仕組みがなければ採用しないこと。

ブラウザ上の保存データだけを参照するなど、実際にはChatGPT側で内容を取得できない方式は不可です。

### 直接送信が技術的に難しい場合

ChatGPTへの直接送信を装った不完全な実装は行わない。

その場合は、ユーザー操作を最小限にしたコピー方式を正式な代替手段として実装する。

- 1クリックで全文コピー。
- コピー成功を明確に表示。
- 操作方法を短く表示。
- エラー表示ではなく、正常な代替動作として案内。
- 送信失敗時にも選定状態を失わない。

実際に実現可能な範囲を確認したうえで最適な方式を選択してください。

## 4. 「選定結果をコピー」の改善

通常のコピー内容は、人間が読んで理解できる形式に変更する。

例：

記事：AIの仮想の島｜Standard

① Key Phrase
- carry over：持ち越す
- take a detour：寄り道をする
- card to play：使える手

② 追加解説
- worth paying attention to：注目する価値がある
- obstacle：障害物

③ 本文意味表示
- make a difference：影響を与える
- separately：個別に
- feature：性質
- Strategy：作戦
- setup：設定

文法：選定なし  
自由コメント：なし

実際のコピーでは、選択された文法がある場合、その文法名と解説全文も省略せず含めること。

### 内部情報の扱い

JSON、SHA、candidate_id、内部schemaなどは、通常のユーザー向けコピー表示から分離してください。

ただし、これらの情報は正式制作工程で必要なため、**表示から除外してもデータとして消失させないこと。**

以下を両立する実装とする。

- ユーザーにとって読みやすい選定結果
- Claudeが正確に復元・検証できる確定データ

たとえば、内部データの保存・識別・別途取得などを活用してよいが、ChatGPT／Claude間で実際に利用可能であることを確認する。

**読みやすくした結果、candidate_idやSHAとの照合ができなくなる設計は不合格。**

ユーザーにJSONの手作業による編集・補完を求めないこと。

## 5. 既存Production Wiringとの統合

現在進行中の以下の作業と整合させる。

- V3フォームの正式Production Wiring
- 文法Top 1／Top 2提示、最大1件選定仕様
- 文法解説全文の事前生成
- ユーザー確定内容の保護
- KP／KWの①②③分類
- Family X/Y/Zの共通フォーム仕様

**今回の改善を現在のフォーム実装に優先して取り込み、後から別修正としてやり直すことを避けてください。**

既存実装の担当作業と競合する場合は、作業分担・変更範囲を調整し、全体のDeliveryを最小化する。

並列に進められる作業は並列化する。

未承認の仕様変更や、別案件のProduction配線を無断で変更しない。

## 6. 必須検証・受入条件

次の条件を満たすこと。

1. Standard／Advancedの選定結果が正しく扱える。
2. 長い文法解説全文を含んでも欠落しない。
3. 「ChatGPTへ送信」操作が想定どおり動作する。
4. 直接送信が不可能な場合、1クリックコピーへ正常に切り替わる。
5. コピー結果が自然な日本語・英語で読みやすい。
6. コピー内容に不要なJSONや内部コードが大量表示されない。
7. 確定内容がChatGPT／Claudeへ正確に引き継がれる。
8. candidate_id・SHAなどの照合可能性が維持される。
9. 0件／1件の文法選定が正常に機能する。
10. 既存の①②③選定上限を維持する。
11. ユーザー確定内容がretry／fallback／resumeでも変更されない。
12. 全Familyの正式Production経路への接続・runtime evidence・Regression／Validator／Integration Testを確認する。

Fable独立受入を実施し、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitへ反映する。

全6経路の根拠が揃うまでPRODUCTION_WIREDと誤判定しない。

## 7. AI島完成工程

Standard／AdvancedともにKP／KW計10件ずつ、文法0件で確定済みです。

この確定内容を後続工程へ反映し、承認済み本文を再利用して完成記事の制作を進めてください。

- 文法再選定待ちは解除する。
- 確定内容は変更しない。
- 不要な本文・KP再生成をしない。
- 必要な音声・品質検査・公開作業を進める。
- Standard／Advancedの最終試聴ページを提出する。
- 最終試聴PASSまでは記事の受入完了としない。

フォーム改善と記事完成は、相互に妨げない範囲で並列に進めてください。

## 8. QCD・STOP条件

優先順位：品質 ＞ Delivery ＞量産単価 ≫ 開発費用。

- 既存成果を最大限再利用する。
- 不要なAPI実行・Trial・再生成をしない。
- 量産単価70円／記事セットを継続目標とする。
- 日次開発費1,000円（JST）と既存の個別承認枠を遵守する。
- 承認済み範囲の不具合は自律的に解決する。
- 新たな外部サービス・重要なアーキテクチャ変更・追加費用枠・重大品質リスクを伴う変更は、ユーザー判断を求める。

## 9. 次の報告

以下を優先順位順に報告してください。

1. V3フォームの送信・コピー改善方針と実装結果
2. 実際のブラウザ操作・ChatGPT受渡し検証結果
3. X/Y/Z全6経路へのProduction Wiring状況
4. AI島Std/Advの文法0件・KP/KW各10件の確定反映状況
5. AI島完成版の最終試聴URL（準備できた時点）
6. Fable受入、SSOT／Git、費用、残Open Item

**最優先は、V3フォームの使い勝手改善を進行中のProduction Wiringへ組み込み、確定内容を安全に渡せる実用的な仕組みを完成させることです。**

(原文ここまで)

## 実施事項

1. **受渡し方式の調査(`HANDOFF_SURVEY_01.md`)**: 現行(`?q=`URL、上限6000字の保守値、JSON同梱→text-only→null降格、`SEND_CHECK_0{1,2,3}.md`)の事実。候補方式を比較表で: (a)`chatgpt.com/?q=`/`?prompt=`の実上限(公開情報・既知の実測。本委任ではブラウザ実測不要=事実不明なら「未確認」)、(b)人間可読本文のみをURLに載せ、照合情報は短い「照合コード」(例: `AIF-a2-<候補集合sha先頭8>-<選択candidate_id群のhash先頭8>`+選択順序)として1行添付し、Claude側が**公開済みフォームデータJSON(GitHub Pages上の`data/<slug>__<level>.json`=既に公開・固定sha)**から選択を再構成・照合する方式(ChatGPTは中継のみ、復元はClaude。「ChatGPT側で取得できない方式は不可」との関係=ChatGPTが受け取るのは人間可読の確定内容そのもの+照合コードであり内容は欠落しないことを論証)、(c)1クリック全文コピー(人間可読+末尾に折りたたみ的な「技術情報」ブロック=短縮形)を正式代替、(d)GitHub Pages上に選定結果を保存する方式(バックエンド不要で書込み不可=不採用理由)、(e)Custom GPT Actions/外部API(新バックエンド=原則不採用、必要性なし)。各方式を優先条件1〜6で採点し推奨を決める(推奨案は(b)+(c)の組合せが有力だが、事実で判断)。
2. **コピー形式(`COPY_FORMAT_01.md`)**: ユーザー例示どおりの人間可読形式(記事名｜レベル、①②③ごとに「- 英語：訳」、文法=「文法名」+解説全文(省略禁止)または「選定なし」、自由コメント)。末尾に1〜2行の照合情報(`照合コード: …`、`データ: <公開JSONのURL or slug__level>`)。ChatGPT向け前置き指示文(構造化出力`eigo_radio_selection_result_v2`を返させる既存方式を維持するか、ChatGPTは人間可読のまま中継しClaudeが解釈する方式に簡素化するか=推奨付き)。
3. **Claude側復元・照合tool(`RESTORE_TOOL_SPEC_01.md`)**: 入力=ユーザーが貼り付けた人間可読テキスト(+照合コード)。処理=公開データJSON(ローカルrepoの同一ファイル、sha一致確認)から英語+訳+区分→candidate_idへ逐語一致で解決(同一termが複数候補ならcandidate_idの曖昧さを照合コードのhashで解消、解決不能はfail-closed)、`candidates_sha256`/本文shaを再構成、payload v2(`schema_minor:1`、`grammar[]`≤1)を生成して`er128 confirm --from-form`へ渡す。既存`DATA_MODEL_02.md`との整合、曖昧ケース(同名候補、訳の揺れ、全角/半角、文法名重複)の扱い。toolの置き場(例: `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/tools/restore_selection_01.py`またはer128 CLIサブコマンド`confirm --from-readable`)。
4. **test計画(`TEST_PLAN_06.md`)**: 受入条件1〜12の対応表(フォームnode/py/headless、復元toolのunit、ChatGPT中継の往復検証=ユーザー実操作またはFable/Agentが模擬[ChatGPTへの実アクセスは不要、貼付テキストの往復で検証]、6経路への接続はGPG委任_05 evidenceに相乗り)。
5. 新規バックエンド/外部サービス/識別子方式を推奨する場合のみ`OPUS_REVIEW_REQUEST_02.md`。コピー形式+照合コード+公開JSON参照の範囲なら「Opus不要(既存公開資産の参照のみ)」と明記。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_02,SEND_CHECK_01,SEND_CHECK_02,SEND_CHECK_03,VERIFY_05}.md`、`user_test/selection_form_v3/form_logic.js`(origin/main: Grep `buildText|buildStructured|chatgpt|q=|6000|copy|clipboard` ±8)、`docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`(送信部: Grep `chatgpt|copy` ±5)
- `er128_kp_confirmed_content_01.py`(origin/main: Grep `cmd_from_form|payload|candidate_id|candidates_sha256` ±5)、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/USER_GUIDE_01.md`(現行操作)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_06.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_FORM6.md`にOPEN-545更新文案(送信・コピー改善=APPROVED_FOR_PRODUCTION、設計)、DECISION_LOG文案(ユーザー決定A: AI島文法0件確定/B: 送信・コピー改善)。

## Git

- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_06: 送信・コピー改善の調査・設計(受渡し方式比較・人間可読コピー形式・Claude側復元/照合tool仕様、read-only、API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/06`。push。

## 報告

`docs/pm/RESULT_PACKET_FORM6.md`: (0)T-0、(1)方式比較と推奨(優先条件1〜6の採点)、(2)コピー形式(AI島Stdの実例を生成して掲載)、(3)復元toolの仕様要点、(4)test計画、(5)Opus要否、(6)判断候補(新たな仕様判断が必要な場合のみ)、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾5行要約。