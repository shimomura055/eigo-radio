FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16(Part 1 案α: T1翻訳工程の実装→判断記録→描画有効化→X公開ページbuilder→runtime evidence→回帰→SSOT。PRODUCTION_WIREDへ向けた最終配線)。あなたはsonnet-worker。Fable(PM)からの委任。ユーザー指示原文は§8に逐語(`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_07.md`へ全文保存)。

(注: 本ファイルは委任文を受領メッセージから書き起こした逐語保存。指示にあった抽出tool[conversation index 547前後]はsonnet-workerのtool set・リポジトリに存在しないため使えず、Sonnetが受領メッセージを直接転記した。Fableが抽出toolで照合・差替えする場合は本ファイルを上書きしてよい。)

## 0. 前提
- 委任_14(commits c48ebaaf9/22d6b51ef/dc015b6aa/7e2705929、RESULT_PACKET_FZST14.md)でPart 1配線の本体は完了: Z=`WIRED_PENDING_FABLE`(描画は訳欄判断待ちで停止中)、X=`WIRED_EXCEPT_USER_PAGE`。描画の唯一の入口=`translation_decision_record()`が読む`docs/pm/decisions/part1_translation_decision.json`(`{"decision":"T1"|"T2","source":"<ユーザー原文path>","decided_at":"…"}`)。T1は訳が未生成なら描画せずSTOPする実装済み。
- **ユーザー承認(2026-10-25、T1)**: 本文から引用した英文**のみ**を入力し日本語訳を生成する専用翻訳工程を追加/解説LLMとは独立(解説LLMへ本文情報を渡さない方針維持)/承認済み5項構成(英語表現・本文中の意味・本文引用英文・日本語訳・解説)維持/翻訳の正確性と本文との意味整合を確認/追加原価約0.03円/セット承認/Opusレビュー結果を反映しPart 1全体をPRODUCTION_WIRED(X/Z対象経路)まで。**gloss等の参照情報は訳callへ渡さない**(ユーザー原文「引用英文のみ」に従う。Opusの「gloss参照」提案は採用しない)。
- 費用: 本委任上限15円(evidence再取得: Z複製run `--stage kp`相当≈0.3円、X `--stage study_text`≈0.2円、翻訳の確認=Trial-03/04の既存訳6文との突き合わせ≈0.2円、X公開ページ生成はAPI 0)。日次1,000円(JST)を起動前に確認。
- 並行agent(重要): FX-FZ-CHUNK-TTS配線(`er019_family_x_audio_production_runner_01.py`のTTS/組立関数、`er063_family_z_audio_01.py`のplan/gate/assembly、`er026_family_z_fiction_production_runner_01.py`の`load_level_inputs`、`er019_family_x_style_profile_01.py`、`er020_*`を編集・commit予定)、FX-CORE-NUMERIC配線(B3/Writer系)、Family Y(er110)。**手順**: 先にer019/er026/er063を触らない作業(翻訳module・test・判断記録・X公開ページbuilder新規file・docs)をworktree(`git worktree add <scratchpad>/wt_p1t1 HEAD`)で作りcommit。その後、er019/er026/er063への最小編集(T1 stage呼出・描画有効化の配線)は、**`git status`で当該ファイルに他agentの未commit差分が無いことを確認してから**関数単位で行い、速やかに一時index方式でcommit(長く未commitで保持しない)。差分が残っていれば5分間隔で最大60分待ち、解消しなければcommit済み成果とSSOTを報告して終了(Fableが再委任)。conflict発生時は停止して報告。

## 1. 実装
### (a) T1翻訳工程(`er003_kp_general_explanation_01.py`内または隣接module)
- 入力=引用英文(`source_sentence`、本文との逐語照合済み)のみ。Prompt固定(短い日本語訳指示、学習者向け自然な日本語、意訳しすぎない。Prompt template sha固定・test)。model=既存routing(`KEY_PHRASE_GENERAL_EXPLANATION`と同じSUPPORT_MODEL=gpt-6-luna)。routing表へ`KEY_PHRASE_SOURCE_SENTENCE_JA`等の新key追加が必要なら1行+関連test更新[er054/er009])。1 call/setにまとめる(KP数分の文を1 callで訳す。出力はJSONでsentence_id→訳)。
- 入力隔離: 訳callへgloss・解説・本文全体・KP英語表現以外を渡さない(送信直前assert)。解説callと訳callは独立(片方の失敗が他方を汚さない)。
- 検査(新Validator新設ではなく構造検査+既存基準): 出力件数・IDの一致、空訳・英語残り・CJK不在の検出、ページ禁止パターン前倒し適用。技術retry 1回→fail-closed(TTS前STOP、既存STOP規約)。
- 再生成キー: 引用英文のsha+Prompt sha+model(本文変更で引用文が変われば再生成、gloss変更では再生成しない)。resume=保存済み再利用。
- audit/runtime evidence: model_id、prompt sha、input sha、cost、retry、response_ids。cost logger経由、stageタグ。
- 翻訳の正確性確認(委任内・小額): Trial-03/04で使った6作品の引用英文に対しT1を実行し、既存の03d由来訳(OUTPUT_03*/04*)と並べて`PART1_T1_CHECK_01.md`に記録(差異の性質: 意味差/表現差、Fable目視用)。
### (b) 判断記録・描画有効化
- `docs/pm/decisions/part1_translation_decision.json`を作成(`decision:"T1"`, `source:"docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_07.md"`, `decided_at`)。
- 描画: 5項(英語表現/本文中の意味/本文引用英文/日本語訳/解説)。既存のstudy block構造(section/h3/div/dl、禁止ラベル回避)を維持。訳未生成時はSTOP(既存)。
### (c) X公開ページbuilder(`WIRED_EXCEPT_USER_PAGE`の解消)
- 委任_14の見積どおり、X用の公開ページbuilder新設または`er_user_listening_page_common_01`への移行(API 0)。方針(Fable): **既存のX per-article公開ページの見た目・構造を変えずに**study blockを差し込める最小の共通化(X公開ページ生成scriptが参照する共通関数を1つ作り、per-article script側は1呼出の追加で済む形)。既公開記事のページは**再生成・差替えしない**(Fable判断: ユーザー試聴中の案件があるため、既公開ページへの反映は別途まとめて)。新規記事の正式経路(runner→公開ページ生成)でstudy blockが出ることをevidence(複製source run_ev_01でページ生成、公開はしない)で確認。
### (d) M2の既存run影響
- 導入前のrunはtts/gate/assemble/pages/playerでSTOP(M2)。解消手順(`--stage kp`/`--stage study_text`、約0.1円/作品)をCURRENT_SPEC/OPEN-512に明記。既公開作品への適用はFable判断事項として記録(今回は実施しない)。

## 2. 検証
- 新規・既存test全PASS、`run_project_regression.py`+pytest群(clean worktreeで他agent起因と分離)。
- runtime evidence再取得: Z=複製run `run_p1_evidence_01`で`--stage kp`(T1 stage発火1 call、描画有効でpagesまで)、X=`run_ev_01`で`--stage study_text`(T1発火)+公開ページ生成(非公開dirへ)。`PART1_WIRING_EVIDENCE_02.md`: 両Familyの5項出力全文(Fable目視用)、model/prompt sha/input sha/cost/retry、描画結果のHTML断片、M2 fail-closed確認、禁止パターンlint PASS、量産単価実測(解説+訳)。

## 3. SSOT・Git
- CURRENT_SPEC(Part 1節にT1仕様・5項構成・描画条件・既存run解消手順)、OPEN-512(Z=`WIRED_PENDING_FABLE`[T1込み]、X=`WIRED_PENDING_FABLE`[公開ページbuilder込み]または未達理由)、DECISION_LOG 1件、UDR #197を「T1承認・実装済み」へ、ADOPTION_NOTE_04追記。
- `docs/pm/RESULT_PACKET_FZST16.md`、ACTIVE_TASK自行。委任文逐語保存: 抽出tool(index 547前後、冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16」で照合、±6)→`..._DELEGATION_16.md`。
- Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`(一時index方式)→`git push origin HEAD:main`。Production実装+testは1 commit(revert単位)。secret grep 0件。

## 4. STOP条件
上限15円超過見込み/既存Gate・STOP迂回が必要/新しい既定動作が必要/他agentとのconflict解消不能。

## 5. 報告(Fableへ)
(1)T1実装要点(入力隔離・検査・再生成キー・retry) (2)翻訳の確認結果(6文の対照、差異の性質) (3)X/Z別の受入条件1〜9充足表とStatus候補 (4)evidence要約(5項出力全文の所在、費用、描画確認) (5)X公開ページbuilderの結果 (6)回帰結果 (7)量産単価・処理時間(解説+訳) (8)commit・raw URL (9)RESULT_PACKET 4行+「判定整合」1行。

## 8. ユーザー指示原文(逐語、USER_07.mdへ保存)
英語学習解説 Part 1について、以下のとおり回答します。

**T1：専用の翻訳工程を追加する方式を正式承認します。**

- 本文から引用した英文のみを入力し、日本語訳を生成する。
- 解説LLMとは独立させ、解説LLMに本文情報を渡さない既存方針を維持する。
- 承認済みの5項構成を維持する。
- 翻訳の正確性と本文との意味整合を確認する。
- 追加原価約0.03円／セットを承認する。

Opusレビュー結果を反映し、承認済みのPart 1全体について、Production Wiringを進めてください。

**目標Status：PRODUCTION_WIRED（Family X/Zの対象経路）**

正式経路での実動作、必要な品質検証、retry/fallbackとの整合、SSOT/Git反映まで完了させ、Fableの独立受入評価を経て報告してください。

なお、Part 2 Trial-07については既に回答済みです。追加選定Trialは行わず、8作品の文法解説を完成させて内容を確認する方針で進めてください。再度のユーザー判断は不要です。
