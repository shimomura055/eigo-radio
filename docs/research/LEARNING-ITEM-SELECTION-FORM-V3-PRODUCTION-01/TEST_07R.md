# TEST_07R 復元・照合toolのtest結果(委任_07R、2026-10-27、API 0・JPY0)

実行: `.venv\Scripts\python.exe run_project_regression.py --pattern "er128_form_readable_restore_test_01.py"` -> collected=52 passed=52 failed=0 errors=0 skipped=0。
`--pattern "er128_*_test_*.py"` -> collected=198 passed=198 failed=0。`form1_selection_form_v3_test_01.py` -> 22 passed。

| # | 検証 | 結果 |
|---|---|---|
| 1 | 全公開データ11件(live) x 乱択6状態 = 66件: 人間可読コピー -> 復元payload が 既存`FormLogic.buildStructured`(node正本)の`article/selection/comment/grammar_status/grammar_decision/kp_confirmed`と**完全一致** | 66/66 |
| 2 | 共有fixture 27ケース(`fixtures/readable_cases_01/`): Python出力がfixtureとバイト一致、復元がnode正本のexpectedと一致 | 27/27 |
| 3 | 改変9種(訳書換え/項目欠落/区分入替え/解説省略/解説改変/解説末尾切れ/コメント改変/コード欠落/コード1字改変)= RestoreError | 9/9検出 |
| 4 | 追加の拒否(未知版AIF2/他区分への項目追加/未知term/文法名置換/提示範囲外文法/記事見出し不一致/データ版不一致+履歴なし/訳注記の矛盾) | 8/8 |
| 5 | 揺れ吸収(コードブロック+前置き/半角コロン/箇条書き3種/CRLF+行末空白/先頭大文字化/全角空白/複数行コメント+行末空白) | 全て復元+`buildStructured`一致。「なし」のみのコメントは拒否 |
| 6 | データ更新: 履歴あり(古い版を取得して復元)/履歴なし(拒否)/実gitの履歴からの取得 | OK |
| 7 | 同一termが複数候補(訳と`s10`で解決、区分入替えは拒否) / 同名文法(解説全文で一意化) | OK |
| 8 | 照合コード契約: COPY_FORMAT_01の実例(AI島Std 10語)の照合コード・本文とバイト一致(d6=915481指定)、部品(c8/t8/m8)の定義固定、d6のCRLF不変性 | OK |
| 9 | AI島Std/Advのユーザー確定payload(`AI-ISLAND-FORM-PRODUCTION-01/payloads/*.json`)を人間可読化->復元: `key_phrase/extra_explanation/meaning_display`・候補集合sha・本文shaが逐語一致。文法1件+コメントを足した版も復元可 | Std/Adv共にOK |
| 10 | 実`cmd_from_form`への結線(mock候補doc。er128のtest基盤): 確定成功+`rev1_readable.txt`が貼付原文と逐語一致+`rev1_payload.json`対 / 改変貼付は何も確定されない / データの候補集合shaが現在docと違えば`cmd_from_form`がISSUE(復元側は緩めない) / 再送は従来どおり拒否 | OK |
| 11 | 委譲: `cmd_from_form`へ`actor/grammar_pending`を透過、dry-runは副作用0、level不一致拒否、復元失敗時は`cmd_from_form`を呼ばない | OK |
| 12 | **T-C契約(JS==Python)**: 委任_07のフォームJS `FormLogic.buildReadable` を fixture 27ケースで実行し、出力(照合コードのsha含む)が Python参照実装/fixture と**バイト一致**(`fixtures/readable_cases_01/node_readable_batch.js`) | 27/27 |
| 13 | isolation: 本moduleは`er119_`をimportしない・`os.environ`/`getenv`/HTTP/openaiを含まない | OK |

関連回帰(本委任で新規に壊していないことの確認): `er128_*_test_*.py` 198/198。`er119_*_test_*.py`は255件中252 passed、失敗3件は本委任と無関係の既存事象(`er119_isolation_test_01`: `er121_family_y_runner_01.py`/`er123_kp_rescue_dev_01.py`/`er124_kp_phrase_word_trial_01.py`が`er119_`をimport、`er119_grammar_review_test_01`: `er119_output/`ディレクトリ(2026-10-25生成)の存在と`compose_page_html(`出現数2!=1)。いずれも本委任のファイルを含まない)。
