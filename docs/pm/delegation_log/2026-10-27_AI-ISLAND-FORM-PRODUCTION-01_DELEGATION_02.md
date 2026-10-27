## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_02(ユーザー正式決定2026-10-27: AI島Std/AdvのKey Phrase/Key Word各10件=USER_CONFIRMED(保存・保護・後続反映対象)、文法=新仕様(Top1/Top2のみ提示・1件選択・0件可・2件禁止)で**再選定待ち**(0件確定にしない)。本委任=(1)ユーザー確定20件の元データ照合(candidate_id/本文SHA/候補集合SHA、不一致はfail-closed)、(2)KP先行確定(`--grammar-pending`、並行委任_05Aの実装到着後)、(3)V3フォームのAI島Std/Advを「KP20件は確定済み表示(再選定不可)+文法Top1/Top2のみ選定(0/1件)」へ、(4)第1報材料(両レベルの文法Top1/Top2=文法名+解説全文)。API 0・JPY0(解説は既存暫定事前生成物を再利用、再生成禁止))。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A(核/er128/CLI/exporterの仕様変更=**これらは編集しない**。`--grammar-pending`と`presented_ids`/`grammar_max_select=1`は05Aが実装中。着手前と確定実行前に`git log origin/main -3 -- er128_kp_confirmed_content_01.py`で到着を確認。未到着なら(1)(3)(4)を先に進め、(2)は05A到着後に実行。本委任終了時点で未到着なら(2)は委任_03へ引継ぎ)、(b)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03(runner/ページ)。あなたの所有=`user_test/selection_form_v3/**`(UI: 文法枠の新仕様化=Top1/Top2・rank表示・最大1件・2件禁止・0件可、確定済み記事のKP欄ロック表示モード)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{build_data_01.py,DATA_MODEL_03.md,TEST_06.md,VERIFY_06.md}`+node/py test、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{CONFIRMATION_CHECK_01,KP_CONFIRM_01,GRAMMAR_TOP2_01,FORM_RESELECT_01,USER_GUIDE_02}.md`+`payloads/`(ユーザー確定payload v2をJSONで逐語保存)、`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_{USER_02,DELEGATION_02}.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF2.md`(gitignore、`-f`禁止)。Production Python編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: ユーザー確定内容の保存・保護+承認済みフォーム仕様変更(文法枠)の実装。到達上限=KP確定保存(05A到着時)+フォーム再提出可能状態+第1報材料。
- 禁止: 英語表現・日本語訳・区分・candidate_idの変更、KP/KW 20件の再選定要求、文法0件での確定、解説の再生成、SHA不一致時の続行(fail-closed=原因を報告)、本文再生成、Production Python編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER_02.md`へ逐語保存(委任_05Aも参照)。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_02.md` をN=724から順に試し、先頭「## 管理ID」+「AI-ISLAND-FORM-PRODUCTION-01 委任_02」のものを採用(同時刻にGPG 委任_05Aあり)。

## ユーザー指示(原文・逐語)

# Claude Code指示｜Family X「AIの仮想の島」Std/Adv選定確定＋文法選定仕様変更・Production Wiring

## 1. 目的とユーザー正式決定

今回の指示は、次の3件を一体で進めるものです。

1. 「AIの仮想の島」StandardのKey Phrase／Key Word選定10件を正式確定する。
2. 同記事AdvancedのKey Phrase／Key Word選定10件を正式確定する。
3. 文法の新しい選定仕様をFamily X/Y/Zの全6経路に正式採用し、Production Wiringまで完了する。

**記事本文は既存の承認済み本文を再利用し、再生成しない。**

両レベルの文法は、新仕様のフォームで再選定するため、現時点では未確定として管理する。

### Status

- Std/AdvのKey Phrase／Key Word：USER_CONFIRMED。後続工程への正式反映対象。
- 文法新仕様：APPROVED_FOR_PRODUCTION。
- 文法のユーザー選定：Std/AdvともUSER_DECISION_REQUIRED。
- 文法新仕様の到達目標：PRODUCTION_WIRED（全6経路）。
- AI島完成記事：ユーザー最終試聴待ちまで進め、最終承認を受けてCloseout。

## 2. Standard｜確定内容

記事：`ai_island_temple`  
Level：`a2`  
本文SHA256：`76f80f62120b57835150b1fc35d590c0b848926ce219ecb27105f2414d376599`  
候補集合SHA256：`25a7bce9357cdaaaf58207e179fd187e97f77e0c5f30c4b511ec933bd51d028a`

候補元：
`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/a2/key_phrases/kp_candidates.json`

### ① Key Phrase（3件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| carry over | 持ち越す | p_1a2370a6af |
| take a detour | 寄り道をする | p_1473453d19 |
| card to play | 使える手 | p_289a665236 |

### ② 追加解説（2件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| worth paying attention to | 注目する価値がある | p_1cf1329364 |
| obstacle | 障害物 | p_d17f8079e3 |

### ③ 本文意味表示（5件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| make a difference | 影響を与える | p_801113c17d |
| separately | 個別に | p_dc8803926c |
| feature | 性質 | p_4b7615dce5 |
| Strategy | 作戦 | p_31e10e6357 |
| setup | 設定 | p_80437a44a6 |

本文表層形の対応を維持する。

- carry over → carried over
- take a detour → taken a detour
- make a difference → made a difference

文法：旧フォームで0件選択。ただし今回の仕様変更により**文法のみ再選定待ち**。0件として最終確定しない。

自由コメントなし。

## 3. Advanced｜確定内容【今回追加】

記事：`ai_island_temple`  
Level：`b1b`  
本文SHA256：`00f14092c072d9aa208778dbc1aa1b5d715262cc77b4e5420acae6c0bffca324`  
候補集合SHA256：`5d8c1b12f01b0de9265721152da508e7f8f7afb1f7f126d5d461a835457d87f9`

候補元：
`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json`

### ① Key Phrase（3件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| carry over | 次に持ち越す | p_1a2370a6af |
| call on | 頼む | p_ad091fb295 |
| take a detour | 遠回りをする | p_1473453d19 |

### ② 追加解説（2件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| card to play | 打てる手 | p_289a665236 |
| obstacle | 障害物 | p_d17f8079e3 |

### ③ 本文意味表示（5件）

| 英語 | 確定日本語訳 | candidate_id |
|---|---|---|
| look at separately | 別々に検討する | p_8f3df24cb8 |
| exploration | いろいろ探ること | p_0d5feb1964 |
| technique | やり方 | p_b41c6aff6d |
| overlook | 見過ごす | p_1b8ee344f0 |
| erase | 消し去る | p_4513a423ab |

本文表層形の対応を維持する。

- carry over → carried over
- call on → called on
- take a detour → taken a detour
- look at separately → looked at separately
- erase → erased

文法：旧フォームで0件選択。ただし今回の仕様変更により**文法のみ再選定待ち**。0件として最終確定しない。

自由コメントなし。

## 4. ユーザー確定内容の保存・保護

両レベルとも以下が確定している。

- ① Key Phrase：3件
- ② 追加解説：2件
- ③ 本文意味表示：5件
- 合計10件
- 日本語訳：全件official

**英語表現、日本語訳、①②③区分、candidate_idを変更しない。**

StandardとAdvancedで同じ英語表現の日本語訳が異なる場合も、今回確定したレベル別の訳をそのまま保持する。

候補ID、本文SHA、候補集合SHAを元データと照合し、不一致があればfail-closedとする。

今回のフォーム結果で送付された `production_connected: false` は、ユーザーの選定結果がまだProductionに接続されていないことを示す。保存だけで正式反映完了と誤認しない。

AI選定理由は参考情報であり、ユーザー確定コンテンツには含めない。

既存のHuman Review記録との整合を確認する。OPEN-526の旧PENDING結果は、確定済みデータを破壊しない方法で引き継ぎ・整理する。

後続のretry／fallback／regeneration／resumeで、確定内容を再生成・変更・上書きしない。

## 5. 文法選定仕様の正式変更【全Family共通】

対象：Family X/Y/Z × Standard/Advanced。

新仕様：

1. AIが文法候補を評価して順位付けする。
2. **ユーザーにはTop 1・Top 2の最大2件のみ提示する。**
3. 表示順はAI評価の順位順（Top 1 → Top 2）。
4. 各候補の文法名と、エンドユーザー向け解説全文を選定前に表示する。
5. **ユーザーは原則1件を選ぶ。**
6. 適切な候補がない場合、0件も選択できる。
7. 2件同時選択は禁止。
8. 確定した文法名・解説全文は後続工程で変更しない。

候補が1件しかない場合は1件、0件の場合は0件を提示する。数合わせのための候補追加は行わない。

既存のTrial-08選定方式・品質基準を尊重し、今回承認された選定数・表示数の変更以外を独断で変更しない。

### 事前生成との整合

別途正式承認済みの「選定前に文法解説全文を生成する」方式を維持する。

AI評価Top 1・Top 2が特定できた後に、その2候補の解説全文だけを生成する方式が合理的であれば採用し、不要なAPI費用を削減する。ただし既存の品質仕様・Trial-08選定方式との整合を必須とする。

ユーザーが選んだ解説全文を後から生成し直すことは禁止。

### 旧仕様の整理

旧「文法最大2件を選定可能」という制約を新仕様に置換する。

対象には以下を含める。

- V3フォームのUI・選定状態・件数表示
- フォーム送信内容・schema・Validator
- 文法Human Review
- 確定保存データ
- 文法finalize
- 組立・公開表示
- retry／fallback／regeneration／resume
- CURRENT_SPEC・関連テスト・既存の旧規則参照

文法解説の公開対象は、承認済みどおり**X/Y/ZのStandard／Advancedすべて**とする。

## 6. AI島の文法再選定

現在のV3フォーム：

https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/

Standardは旧フォームで文法4候補、Advancedは3候補が提示されていた。

新仕様では、各レベルのAI評価Top 1・Top 2だけを提示する。

### 必須対応

- Standardの①②③確定済み10件を保持。
- Advancedの①②③確定済み10件を保持。
- **両レベルとも文法のみ再選定**できる状態にする。
- 文法名＋解説全文を表示する。
- Top 1・Top 2の順位を明示する。
- 0件／1件の選定のみ許可。
- 旧フォームで文法0件だったことを、新フォームでの確定0件として引き継がない。
- 新フォームからの送信内容が、既存の確定済み10件と矛盾しないようにする。

**ユーザーにKey Phrase／Key Wordの20件を再選定させないこと。**

修正したフォームで、Standard／Advancedの文法をまとめて選定できる状態にする。

再提出時は、両レベルのTop 1・Top 2を文法名・解説全文付きで提示し、ユーザーには文法選定だけを依頼する。

## 7. AI島の完成記事制作

Standard／Advancedの文法選定をユーザーから受領したら、確定内容をそのまま正式制作工程へ反映する。

- 既存本文を再利用する。
- Key Phrase／Key Wordの①②③を正確に反映する。
- 文法0件なら追加しない。1件なら確定解説全文をそのまま公開する。
- 必要な音声だけ生成し、既存の有効な音声を再利用する。
- 承認済みTTS Style、Voice、Chunk、ASR品質Gateを維持する。
- Human Reviewが必要な場合は承認済み手順で処理する。
- 通常のStandard／Advanced最終試聴ページを公開する。

ユーザーの最終試聴PASSまでは完成記事の最終受入としない。

## 8. Production Wiringの受入条件

文法の新仕様を全6経路で検証する。

- 正式初回Production経路でTop 1・Top 2のみ提示。
- AI評価順位と表示順が一致。
- 解説全文の事前生成と表示が正常。
- 0件／1件の選定が可能で、2件選定を拒否。
- 確定内容が後続工程で完全一致。
- Standard／Advanced双方の公開ページに正しく反映。
- retry／fallback／regeneration／resumeとの整合。
- 必須Regression／Validator／Integration Test PASS。
- 実runtimeでの発火証拠。
- actual model_id、routing、Prompt／Style等の証拠。
- Fable独立受入。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新。
- Git反映。

Family別・レベル別にStatusを判定し、証拠のない経路をPRODUCTION_WIREDとしない。

既に完了している別案件の文法事前生成・確定内容保護との実装競合を避け、重複作業をしない。

## 9. QCD・進行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 不要な本文再生成・KP再選定・重複API呼出しを行わない。
- 確定済み20件を再利用。
- 文法の新仕様への変更と全Family配線を、既存作業との依存関係を考慮して並列化。
- ユーザーが文法選定を行える状態を優先的に準備する。
- 文法の選定待ち中も、確定済み内容の保存・非競合作業は進める。
- 開発費1,000円／日（JST）および個別承認枠内で実施。
- 不具合は承認済み範囲で自律解決。
- 未承認仕様変更、重大な品質問題、blocker、予算超過はSTOPして報告。

## 10. 次の報告

### 第1報｜文法選定待ち

1. Standardの文法Top 1・Top 2（文法名＋解説全文）
2. Advancedの文法Top 1・Top 2（文法名＋解説全文）
3. 修正後V3フォームURL
4. 両レベルのKP／KW計20件が確定保存され、変更されていないこと
5. ユーザーが文法だけを選定する方法

### 第2報｜完成記事提出

1. Standard／Advanced最終試聴URL
2. KP／KW計20件と文法確定内容の一致結果
3. 音声・公開品質Gate結果
4. 実費・作業時間・量産単価への影響
5. Fable受入・Git／SSOT・残Open Item
6. 文法新仕様のX/Y/Z全6経路Production Wiring Status

**最優先の到達点は、両レベルの確定済みKP／KWを保持したまま、文法だけ新仕様でユーザーに選んでもらえる状態にすること。その後、AI島の記事完成と、全Familyへの文法新仕様Production Wiringを確実に完了することです。**

(原文ここまで)

## 実施事項

1. **照合(`CONFIRMATION_CHECK_01.md`、fail-closed)**: ユーザー提示の本文SHA(a2 `76f80f62…`/b1b `00f14092…`)と候補集合SHA(a2 `25a7bce9…`/b1b `5d8c1b12…`)を、候補doc(`run_kp75_ev_01/<lv>/key_phrases/kp_candidates.json`の`text_sha256`/`candidates_sha256`)、フォームデータJSON(`article.candidates_sha256`/本文sha項目)、`run_ai_01/<lv>/article.md`のsha(委任_01報告ではa2=`90c66293…`/b1b=`a2951b9b…`=**ユーザー値と異なる**)と突き合わせ、**どの算出基準の値か**(article.md生bytes/正規化本文/候補docの`text_sha256`等)を特定して一致を証明する。全20件のcandidate_id・英語・訳(レベル別)・区分が候補doc/フォームデータの値と逐語一致することを表で示す(訳はユーザー提示の「確定日本語訳」=候補docの`japanese_gloss`と一致するか。異なる場合はユーザー確定値を正とし、その事実を明記=ただし変更せず報告)。不一致があれば続行せず原因と判断材料を報告。
2. **payload保存**: Std/Advそれぞれのpayload v2(`schema_minor:1`、`selection[]`10件+`article`sha+`grammar:[]`+`grammar_status:"pending_reselection"`)を`payloads/ai_island_temple__{a2,b1b}__user_confirmed_01.json`に作成(ユーザー原文から逐語)。
3. **KP先行確定(`KP_CONFIRM_01.md`)**: 05Aの`--grammar-pending`が到着していれば、新run dir(既存runを破壊しない: `run_ai_01`をコピーした`ai_island_temple__run_form_prod_01`。候補docは`run_kp75_ev_01`から、本文は`run_ai_01`から。KP review=フォーム確定として`op_select`相当)で`er128 confirm --from-form <payload> --run <run> --level <lv> --by user --user-ref docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md --grammar-pending`をa2/b1bで実行。`confirmed_selection.json`のsha・`actor=user`・文法`pending`を確認。OPEN-526旧PENDING review(7件)は新runに持ち込まない(旧runに残置=破壊しない)。未到着なら手順と準備済みコマンドを記載し委任_03へ。
4. **フォーム(`FORM_RESELECT_01.md`/`DATA_MODEL_03.md`)**: (a)文法枠の新仕様: Top1/Top2のみ表示(rank明示「Top 1」「Top 2」)、ラジオ/排他で最大1件、「適切な候補なし(0件)」を明示選択、2件不可、文法名+解説全文表示。(b)確定済み記事モード: AI島Std/Advのデータに`kp_confirmed:{status:"USER_CONFIRMED", selection:[…10件…], confirmed_at, user_ref}`を持たせ、KP/KW欄は確定内容を表示のみ(チェック不可・区分バッジ付き)、送信payloadにはその確定10件を**そのまま**含め(再選定不可)、文法のみ選択可。(c)AI島の文法データ: 既存暫定事前生成物(`docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out/<lv>/study_text/`)からTrial-08順位のTop1/Top2を特定(順位は候補docの既存rank/Tier=核のロジックと同じ基準。05Aの`presented_ids`が使えればそれで、未到着なら候補doc内の順位情報で同一結果になることを確認)し、Std 4候補→Top2、Adv 3候補→Top2を登録(3位以降は非表示)。旧「文法0件」の選択状態を引き継がない。(d)他記事の文法枠も新仕様UIに統一(データが旧形式のものは表示のみ)。(e)test(node/py: 排他・0件・2件拒否・確定済みKP不変・payload)、公開headless。
5. **第1報材料(`GRAMMAR_TOP2_01.md`/`USER_GUIDE_02.md`)**: Std/AdvのTop1/Top2(文法名+解説全文=逐語)、フォームURL、20件確定保存の証明(sha)、文法だけを選ぶ操作手順。

## 事前指定Read一覧

- `docs/research/AI-ISLAND-FORM-PRODUCTION-01/{SURVEY_01,GRAMMAR_PREP_01,FORM_REGISTRATION_01}.md`、`grammar_prep_out/{a2,b1b}/study_text/`(候補doc・explanations)、`user_test/selection_form_v3/{form_logic.js,index.html,data/ai_island_temple__{a2,b1b}__prod.json,data/articles.json}`
- `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/{a2,b1b}/key_phrases/kp_candidates.json`(sha項目・rank)、`er019_output/.../ai_island_temple/run_ai_01/{a2,b1b}/article.md`
- `er128_kp_confirmed_content_01.py`(origin/main最新: Grep `cmd_from_form|grammar_pending|add_argument` ±5)、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md`(from-form節)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_0{1,2}.md`
- `er120_part2_grammar_production_01.py`(origin/main: Grep `TOP_N|rank|Tier|presented` ±5)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_02.md --json-out ...\_check.json`
- 確定(05A到着後): 上記3のコマンド(実行前に`--help`)
- test: node test+`.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+headless(公開URL)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_AIF2.md`にOPEN(AI島実運用)更新文案、OPEN-526整理文案(旧PENDINGは旧runに残置・新runはフォーム確定)、OPEN-545(フォーム文法枠新仕様)文案。

## Git

- commit message: `AI-ISLAND-FORM-PRODUCTION-01 委任_02: AI島Std/Adv KP/KW各10件のユーザー確定を照合・保存(grammar-pending)+V3フォーム文法枠を新仕様(Top1/Top2・1件・0件可)へ+確定済みKPロック表示(API 0)`。trailer: `Delegation: AI-ISLAND-FORM-PRODUCTION-01/02`。push。

## 報告

`docs/pm/RESULT_PACKET_AIF2.md`: (0)T-0、(1)照合結果(SHA基準の特定、20件一致表、不一致の有無)、(2)KP先行確定の結果(または引継ぎ)、(3)フォーム変更・検証、(4)第1報材料5項目(Top1/Top2の文法名+解説全文を逐語)、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・公開URL・raw URL。末尾10行要約。