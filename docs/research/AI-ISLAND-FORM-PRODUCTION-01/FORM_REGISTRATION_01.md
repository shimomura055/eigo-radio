# FORM_REGISTRATION_01 V3フォームへの登録・検証(AI-ISLAND-FORM-PRODUCTION-01 委任_01)

公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (記事選択の先頭2枠=『1. AIの仮想の島｜Standard』『2. AIの仮想の島｜Advanced』)

## 変更点(最小)
1. `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`: `--grammar-bundle <form_grammar_bundle.json>`(+`--grammar-source-json`)を追加。`grammar_from_bundle()`が`form_grammar_bundle`(SCHEMA_CONTRACT_01 §5)の各itemを、フォームUI項目(`id/title/body/example`)+契約項目(`candidate_id/explanation_full/explanation_status=provided/explanation_sha256/level/rank/ai_recommended/para/feature_class`)で書く。解説が空/`provided`でないitemは例外(fail-closed、仮データを入れない)。文法0件のbundle(`no_candidates_found`)は「文法候補なし(事前生成は実施済み)」注記+`grammar_status`を出力。bundle無しは従来どおり(後方互換)。
2. `user_test/selection_form_v3/form_logic.js`: 送信payloadの文法record(`grammarRecord`)に`candidate_id/explanation_sha256/level`をデータにある場合のみ併記、`grammar_status`が`no_candidates_found`なら正しく出力(従来は未生成扱い)。**UI・選定上限・他の記事データは不変**。
3. `data/ai_island_temple__{a2,b1b}__prod.json`: run_kp75_ev_01のKP doc(再利用)+文法bundleで再出力(同名ファイルを置換=既存test/参照の互換維持、`name='AIの仮想の島'`/`slug=ai_island_temple`)。`data/articles.json`: 先頭2枠のdataをこの2ファイルへ、重複していた『AIの仮想の島｜Production候補・7+5 evidence』2枠を削除(17枠)。旧3+5版`data/legacy/`は不変・非表示。
4. 旧Trial/旧Production候補が最新として出ないこと: AI島に該当する記事枠は2つのみ(headless確認)。他記事(英国の電車/再配達/メロス/猿の手)のデータは不変。

## データ照合(元データとの逐語diff。`tools/verify_form_data_aif1.py`、出力=`VERIFY_DATA_output.txt` 24項目 bad=0)
- 英語(`used_form`)・日本語訳(`japanese_gloss`=official 10/10×2)・AI理由(`reason_ja`)・例文(`source_sentence`)・`kind`・`ai_rank`・`candidate_id`が`kp_candidates.json`と逐語一致、`candidates_sha256`一致、全例文が承認済み`article.md`に存在(引用符字種差のみ正規化)。
- 文法: id/名称(`construct_ja`)/解説全文(`explanation_md`)/例文/`explanation_sha256`が`grammar_candidates.json`・`grammar_explanations.json`と逐語一致、`sha256(explanation_md)`再計算一致、全`source=pregen`。

## 表示・操作検証(`tools/browser_check_aif1.mjs`、headless Chrome。出力=`BROWSER_CHECK_local_output.txt`/`BROWSER_CHECK_public_output.txt`)
- 41項目: 記事枠(AI島はStd/Advの2枠のみ・先頭)、候補10件の順序・日本語訳・AI理由(全件≤40字)、文法(Std4/Adv3)の名称+解説全文+例文がデータと一致、上限(①≤3/①+②≤5/全候補/文法≤2・3件目以降disabled)、送信payload(文法の解説全文・`candidate_id`・sha、KPの`candidate_id/kind/ja_gloss(official)`、3/2/残りの区分、`candidates_sha256`/`text_sha256`/`grammar_status`/自由コメント)、コピー本文に解説全文が欠落なく入りJSONが再パース可能、コンソールエラー0。
- 送信経路の事実: 文法2件を選ぶとコピー本文は約1.3万字(Std 13,018/Adv 12,517)で、`ChatGPTへ送信`のURL上限(6000字)を超えるため**自動的に全文コピーに切替**(黙って切り詰めない既存設計・「送信文が長くURLに載せられないため、選定結果をコピーしました」表示)。ユーザーはコピーされた全文をChatGPTへ貼る(USER_GUIDE_01)。
- Node/Python test: `selection_form_logic_test_01.js` ALL PASS 41 / `form1_selection_form_v3_test_01.py` 17 tests OK(既存testを無修正で通過)。

## 正式訳・未確定訳
- 日本語訳は20/20が`official`(gloss Gate=ALIGNED)。未確定訳(provisional/missing)0件。

## 未実施(第2報側・委任_02)
- 確定内容保護`confirm --from-form`(payload v2取込)は第1報では使用しない。ユーザー選定後に、保存・前後照合を必須で実行する。
