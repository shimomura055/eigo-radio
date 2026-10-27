# TEST_PLAN_06 受入条件1〜12の検証計画(委任_06、設計。実装・実行は委任_07/GPG小委任/Fable受入)

試作の既実証: 往復66/66・改変9種検出・揺れ吸収5種・data更新2経路=`proto06_output_01.txt`(`py -X utf8 proto06_copy_restore_01.py --work <origin/mainのform_logic.jsとdata/を置いたdir>`)。下表は**本実装**での検証計画。

| # | 受入条件(ユーザー原文§6) | 検証手段(種別) | 担当/時期 |
|---|---|---|---|
| 1 | Standard/Advancedの選定結果が正しく扱える | node: 全データ×(a2,b1b)で`buildReadable`→Python`restore`→`buildStructured`と一致(T-C契約test)。headless: 実DOMで選択→コピー文を取得 | 委任_07 |
| 2 | 長い文法解説全文を含んでも欠落しない | node/py: 最長解説(実データ最大721字+)でコピー文に全文、復元payloadの`explanation_full`がer128の`explanation_md`と一致。URL長超過でも貼付経路で全文 | 委任_07 + GPG小委任 |
| 3 | 「ChatGPTへ送信」が想定どおり動作 | headless(CDP): `window.open`引数を捕捉(URL内蔵時は`?q=`にデコード後本文が一致、超過時は`https://chatgpt.com/`)。クリップボードへ書込まれたこと(権限付与したheadlessで`readText`)。**実ブラウザ(ユーザー実操作)**: `?q=`が入力欄に入るか・上限(SURVEY §5) | 委任_07 + ユーザー実操作 |
| 4 | 直接送信不可なら1クリックコピーへ正常切替 | headless: 超過データでstatus文言が「貼り付け方式」(警告色でない)、`window.open`は`q`なし。clipboard拒否時はtextarea表示・文言 | 委任_07 |
| 5 | コピー結果が自然な日本語・英語で読みやすい | COPY_FORMAT_01実例との差分0を自動testし、AI島Std/Adv実出力をFable/ユーザーが目視 | Fable受入 |
| 6 | 不要なJSON/内部コードが大量表示されない | test: コピー文に`{`/`"candidate_id"`/64桁hex/`candidates_all`が含まれない(許容=照合コード1行のみ)。文法なしコピー文の長さ上限(目安1.2k字) | 委任_07 |
| 7 | 確定内容がChatGPT/Claudeへ正確に引継ぎ | **往復検証(ChatGPT実アクセス不要)**: 生成本文をChatGPT返信を模した変換(コードブロック囲み・前置き・行末空白・CRLF・半角コロン)に通し`restore`→一致。**ChatGPT実機でのecho検証はユーザー実操作の任意項目** | Fable/Agent(模擬)+ユーザー(任意) |
| 8 | candidate_id・SHAの照合可能性維持 | py: 復元payloadの`candidate_id`/`kind`/`candidates_sha256`(全文)/`text_sha256`が`buildStructured`と一致。改変9種(訳書換え/項目欠落/区分入替え/解説省略・改変・末尾切れ/コメント改変/コード欠落・破損)が全てRestoreError。data更新(履歴あり/なし) | GPG小委任(tool実装) |
| 9 | 0件/1件の文法が正常 | node/py: 文法0件(`文法：選定なし`、`g10=0`)と1件(同名3件のAI島Std含む)。2件(旧上限)も後方互換で復元可 | 委任_07 + tool |
| 10 | ①②③選定上限を維持 | 既存フォームtest(`selection_form_logic_test_01.js`)全PASSのまま。コピー形式は上限を変更しない | 委任_07 |
| 11 | retry/fallback/resumeでも確定内容が変わらない | 復元payloadを`cmd_from_form`へ→`rev{N}_payload.json`/`rev{N}_readable.txt`保存、同じ入力の再送は冪等(従来仕様)。再取り込み/resume/LR/retry後のrecord shaが不変(GPG委任の既存evidence再利用) | GPG小委任 |
| 12 | 全Family正式Production経路・runtime evidence・Regression/Validator/Integration | GPG委任_05 evidence(6経路)に相乗り: 各経路で「フォーム→コピー文→`confirm --from-readable`→確定→後続」を実行(API 0)。Regression=既存`form1_selection_form_v3_test_01.py`+er128 testの全PASS | GPG小委任 + Fable受入 |

## 追加test(本設計固有)
- T-C 契約test: JSの`buildReadable`出力とPythonの`build_readable`出力がバイト一致(同じdata/stateで)。照合コードのsha256がJS/Pyで一致(`d6`はfetchした生バイトから)。
- T-D PREFACE: ChatGPT向け前置きが含まれ、選定結果ブロックと区別できる。
- T-E 状態保持: 送信/コピーの成功・失敗どちらでもlocalStorageの選定状態が不変。
- T-F DefaultOff: 新CLIオプション未指定時、既存`confirm --from-form`/`--from-review`の出力が不変。
- T-G 未確認事項の記録: `?q=`実上限・clipboard実機成功は「ユーザー実操作確認項目」として`SEND_CHECK_04.md`(委任_07)に未確認のまま記録。

## 実装順序(クリティカルパスと並列化)
1. (並列) A: フォーム(JS)実装[AI-ISLAND委任_02マージ後] / B: 復元tool+CLI[GPG委任_05A後]。契約=`COPY_FORMAT_01.md`のみで独立。
2. 契約test(T-C)→headless実DOM→(任意)ユーザー実操作(?q=上限・clipboard)。
3. GPG委任_05 evidence 6経路への相乗り→Fable独立受入→SSOT。
所要見込み(実装側): A約1.5h、B約1.5h(並列で約1.5h)、検証約1h。
