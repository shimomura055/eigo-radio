# RESTORE_TOOL_IMPL_01 人間可読選定結果の復元・照合tool 実装と運用手順(委任_07R、2026-10-27、API 0)

設計=`RESTORE_TOOL_SPEC_01.md`/`COPY_FORMAT_01.md`(委任_06)。実装=`er128_form_readable_restore_01.py`(新規)。到達=IMPLEMENTED+test PASS(Production既定動作は不変。明示実行時のみ動作)。

## 1. 何ができるか
ユーザーがChatGPT経由で貼り付けた人間可読テキスト(+末尾の照合コード1行)から、公開データJSONを参照して`candidate_id`・候補集合sha・本文sha・文法解説全文を復元し、payload v2(`schema_version:2, schema_minor:1`)を作る。確定は既存`er128 cmd_from_form`へ委譲(検証は緩めない)。照合できなければfail-closed(何も確定・保存しない)。

## 2. 受け取ってから確定までのコマンド列(Fable/Agent用)
1. ユーザー(またはChatGPT)の返信全体を `paste.txt` に保存(UTF-8。コードブロック囲み・前置き文があってもよい)。
2. **dry-run**(確定しない。復元内容を確認): 
   `py er119_kp_human_review_cli_01.py confirm --from-readable paste.txt --run <run> --level a2|b1b --by <名> --user-ref <delegation_log path> --dry-run`
   (同等: `py er128_form_readable_restore_01.py confirm --from-readable ... --dry-run`。復元payloadだけ欲しい場合は `py er128_form_readable_restore_01.py restore --text paste.txt --out payload.json`)
   出力: 英語表現・日本語訳・candidate_id・区分・文法名と解説長・コメント・照合コード・notes(正規化・履歴復元の記録)。
3. **確定**: `--dry-run`を外して同じコマンド。`--grammar-pending`(KP/KWだけ先行確定)・`--actor evidence`(runtime evidence)は`cmd_from_form`へそのまま透過。
   成功時: `source/rev{N}_payload.json`(既存)と`source/rev{N}_readable.txt`(貼付原文を逐語保存、sha記録は出力の`readable_sha256`)が対で残る。
4. その後は従来どおり(制作コマンドを同じまま再実行 -> finalize -> 後続)。確定後の変更は`confirm-revise`/`revoke`のみ(従来仕様)。

終了コード: 0=成功 / 2=拒否(復元不一致=`[READABLE_RESTORE][REFUSED]`、または`cmd_from_form`のCliError) / 4=ISSUE(`cmd_from_form`が候補doc不一致等を記録。従来仕様)。

## 3. fail-closed(拒否する場合。ユーザーへはJSON編集を求めず「フォームの『選定結果をコピー』を押し直して全文を貼り付け」を案内)
照合コード欠落/破損(k4)/未知版(AIF2等) / データ版(d6)が現在と異なり履歴にも無い / 記事見出し・候補集合sha・本文shaの不一致 / 英語表現が候補に無い / 日本語訳が候補データと不一致(意訳の検出。黙って置換しない) / 区分の入替え・項目の欠落や追加(s10) / 文法解説の省略・改変・追記・末尾切れ・提示範囲(Top1/Top2)外 / 文法名が候補に無い・同名同文で一意不可 / コメントの変更(m8)。コメントが文字列「なし」のみの場合は「コメントなし」と区別できないため拒否。

## 4. 吸収する揺れ(復元でき、既存`buildStructured`と一致することをtest済み)
コードブロック囲み・前置き・後書き / 半角コロン / 箇条書き記号(`-`・`・`・`•`・`1.`) / CRLF・行末空白(コメントは行末空白を除いたshaが`m8`と一致する場合のみ) / 英語表現の先頭大文字化(NFKC+casefoldで一意の場合のみ、notesに記録) / 日本語訳の全角半角・空白。

## 5. 実装メモ(Fable/レビュー用)
- 所有ファイル: `er128_form_readable_restore_01.py`(新)、`er119_kp_human_review_cli_01.py`(`confirm --from-readable`サブコマンドの薄い委譲のみ、+15行。CRLF維持)、`er128_kp_confirmed_content_01.py`は**無変更**。
- **現状との差異(委任文・仕様書の前提)**: `confirm`サブコマンドの実体は`er128_kp_confirmed_content_01.py`のCLIにあり、`er119_kp_human_review_cli_01.py`には`confirm`が無かった。委任文に従い`er119`側へ`confirm --from-readable`のみを追加し、本体moduleにも同等のCLI(`restore`/`confirm`)を持たせた。er128側CLIは無変更。
- 照合コード: `AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>`。**d6はデータJSONバイト列の`CRLF->LF`正規化後sha256先頭6桁**(作業ツリーがCRLFになるWindowsと公開Pages=LFの差を吸収。JS側も同じ定義)。
- 新データ形式への追従(試作から追加): `kp_confirmed`(確定済みKP/KWの記事: payloadの`selection`は確定レコードの逐語、貼付の項目集合が一致しなければ拒否)・`grammar_spec`(Top1/Top2提示・1件・0件可: 提示外は拒否、`grammar_decision`/`grammar_status`を`buildStructured`と同形で出力)・文法record の`rank`/`rank_label`。
- payloadは決定論的(時刻なし)。`restore_meta.collation_code`に照合コードを記録(`cmd_from_form`は無視)。
- `--verify-public`(公開Pagesとの同一性GET、任意)は未実装。外部HTTPは0。
- 変更なし/撤去なし: 既存`confirm --from-form`/`--from-review`の出力・挙動、`cmd_from_form`の検査(`candidates_sha256`・`text_sha256`・正式訳・文法逐語照合)は不変。
- 副次変更: `er128_kp_confirmed_content_test_01.py`の`TestIsolation`許可リストに、本toolと`er119`CLI入口を追加(A/B/C共有関数からのer128 importを禁じる既存testが、遅延importにも反応するため)。
- 既知の限界: 同一コメントが「なし」のみ / 項目名がMarkdown装飾(`**term**`)された返信は拒否(fail-closed。再コピー案内)。KP/KWと文法を別時点で確定する`--grammar-from-form`の人間可読版は未実装(必要なら次委任)。
