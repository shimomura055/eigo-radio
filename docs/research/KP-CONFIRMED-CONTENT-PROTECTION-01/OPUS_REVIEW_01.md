## KP-CONFIRMED-CONTENT-PROTECTION-01 独立技術レビュー(Opus 条件A、read-only、API 0)

(2026-10-27。Opusレビュー原文の逐語保存。Fable採否=M1〜M9全件採用。依頼文=`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/OPUS_REVIEW_REQUEST_01.md`。委任_02A文`2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_02A.md`の「Opusレビュー(逐語)」節から転記。ユーザー判断事項(a)=既出UDR-FORM-1と同一のため新規提示不要、(b)=CURRENT_SPEC:458-469「表示用`japanese_gloss`/TTS用`japanese_gloss_tts`、表示用フィールドはTTSへ渡らない」が承認済みのため、Y/Z Stdページが`canonical_text`(TTS用)を表示している現状は承認済み仕様との不一致=バグ是正としてFable判断で委任_02Bで修正)

**結論: 条件付きで実装に進んでよい。** 骨格は妥当です(確定レコード、消費者入口での fail-closed 検査、違反の2分類、AND追加のみで既存Gateを緩めない)。ただし、下記「必須修正 M1〜M9」を設計に反映してから委任_02へ進めてください。中でも M1・M2・M3・M4 は、そのまま実装すると「確定内容が黙って変わる穴が残る」か「誤BLOCKが多発する」ため必須です。

### O-1 正本性・置き場所・sha範囲・改ざん耐性 — 要修正
- 正本を kp_dir、ミラーを audit に置く構成自体は可です。ただしミラーで検出できるのは「片方だけの偶発的な改変」に限られます。レコードは自己sha方式なので、AIがファイルを書き換えてshaを再計算すれば素通りし、改ざん耐性はありません。
- **M5(改ざん耐性の錨)**
  - (a) フォームpayloadの受信原文を `confirmed_selection_source/rev<N>_payload.json` に逐語保存します(加えて delegation_log にも)。
  - (b) G1 は「レコード保護フィールド == 候補docの値」も毎回検証します。候補docは `require_final_consistent` の自己sha検査(`er119_kp_human_review_01.py:1060`)で既に保護されているので、正本は事実上「候補doc+review」になり、レコードは「ユーザーの確認行為の上乗せ情報(区分・③・文法全文・コメント)」と位置づけられます。これで二重の正本(dual truth)を避けられます。
  - (c) `history` の各エントリに直前エントリのhashを入れ、連鎖させます。
- sha範囲: AI理由を外す判断は正しいです。`comment` はユーザーが書いた内容なので、内容shaとは別の `user_note_sha256` で検証することを推奨します(パイプラインは消費しないが、改変は検出する)。正規化は sort_keys のみとし、値の Unicode 正規化は**禁止**してください(「～」と「〜」は別物として扱う必要がある。O-5参照)。`kind`(phrase/word)はレコードに保存し、候補docとの一致を検証します。
- 文法を KP レコード(b1b)の `grammar[]` に同居させる案は、KP と文法の2つの状態機械を結合してしまいます。G4(er120)が KP 側のパスを知る必要も出ます。`<study_dir>/confirmed_grammar.json` に分け、共通の `confirmation_id`(= payload sha)で束ねる方が局所的です(推奨、必須ではない)。

### O-2 Gate位置(G1)が全消費者の前に通るか — 要修正(見落としあり)
- X は網羅されています。`er019_family_x_audio_production_runner_01.py:3533-3544` が study_text/tts/assemble/player/all の全stage(`--only-segments` を含むtts)の前で `require_final_consistent` を呼びます。
- **M1(見落とし)**: Y と Z の `stage_kp` では、確定後に**G1を通らないまま有料の派生物生成**が走ります。
  - Z: `er026_family_z_fiction_production_runner_01.py:2055` `_gloss_person_gate`(gloss上書き)、`:2060` `_src_gate`(artifactへ書込)、`:2061` install、その後 `:2106` Adv KP解説LLM、`:2120-2123` Part 1解説・Part 1訳・Part 2 Step B。
  - Y: `er121_family_y_runner_01.py:614` install、その後 `:629` 解説LLM、`:640-644` Part 1/Part 2。
  - 最終的には TTS 前(Z `load_level_inputs:2273`、Y `stage_tts:1012`)で捕まりますが、それまでに改変済みの入力で派生物を生成して費用を消費し、キャッシュも汚します。
  - 修正: Y/Z の stage_kp で、全levelの install 直後・解説生成前に `_assert_kp_review_consistent(ctx, lv, "stage_kp_post_install")` を1行ずつ追加します。Z では `_gloss_person_gate` と `_src_gate` の**後**に置きます。
- その他の経路の確認結果:
  - Y/Z の assets copy: G1 に `assets_json` を渡す案で可です。
  - `er120_part2_wiring_01.py:187` `public_study_html` は G1 を通らずに `part1_items` を直接呼んでいます。現状の呼出元は test のみですが、公開builderとして使うなら G1 が必要です。
  - `docs/pm/tools/phase_d_kp_mapping_regen.py`(ハイライト用mapping)と `er019_*_page_*.py` 系の一回限りのページscriptは、artifact を直接読みます。これらは Production 外ですが、今後の消費者は「検証してから返す単一アクセサ」(例: `cc.load_verified_items(kp_dir)`)だけを使うことを契約に明記してください。
  - `--regenerate-stage kp_*` は確定済みreviewを再利用するので問題ありません。ただし **`--regenerate-stage part2_cand_b1b`(再抽出)は未カバー**です(O-8 の M6)。
- **M3(例外クラスの設計内矛盾)**: §3 は「全て `KpReviewInconsistent` のサブクラスで rc=3」、§3-1 は「ISSUE は rc=4 待機」と書いており、矛盾しています。`KpReviewNotConfirmed` は `KpReviewInconsistent` のサブクラスで(`er119_kp_human_review_01.py:97`)、X/Y/Z とも NotConfirmed を先に捕まえて rc=4 にしています(X `:3538`、Y `:521`、Z `:1520`)。そこで次のように分けます。
  - CONFIRMED_CONTENT_ISSUE は `KpReviewNotConfirmed` の派生にして rc=4(ユーザー待機)。依頼書 `request_md` の先頭に「確定内容の確認依頼」節を置く。
  - INTEGRITY_VIOLATION は `KpReviewInconsistent` の派生にして rc=3。
  - Z の `_gloss_person_gate` 内で送出する場合は `FamilyZKpReviewPending` に写像します。
- G2 の補足: Master Store を再利用した TTS record は `text` 等を持たないことがあります(`:1137` に既存の対処あり)。`display_gloss` の欠落は canonical_text 側で比較する形にして、誤BLOCKを避けてください。G3 の Part 1 行の検査は、ページにPart 1が描画されたとき(`:1168`)に限定します。

### O-3 confirm-restore を AI 単独で実行してよいか / STOPとの整合 — 条件付き妥当
- 「artifact をレコード値へ戻す」ことは確定内容を守る操作で、USER_02「黙って変更せず」と矛盾しません。AI が明示コマンドで実行するのは可です。ただし条件を付けます。
  - (i) 逸脱の原因が**人間の操作でないこと**を `history` / review history で確認する。例えば `resolve_gloss` や CLI `--by` による人間の編集が原因なら、ISSUE に格上げして「新しい値を採用するか復元するか」をユーザーに聞く。
  - (ii) 復元は完了報告に必ず列挙する(黙って直さない)。
  - (iii) 実装はフィールド単位のパッチではなく、「確定物を退避 → 候補docから決定論的に再finalize(API 0) → Z は SRC D1 を再実行」とする。`finalize_kp` は署名が同じなら再書込しないため(`:995`)、パッチ方式だと整合が崩れます。
  - 候補docそのものが変わっている場合(`origin.candidates_sha256` の不一致)は restore で直せないので、ISSUE か BLOCK にして次の一手を明記します。
- **M4(AIによる再選定の経路が残っている)**: 設計がガードしているのは `op_reselect` だけです。以下は、ユーザー確定レコード(actor=user)がある状態でも AI 操作者が実行でき、結果として選定を書き換えられます。
  - `op_select`(REVIEWED からの再select。`:601,612`)と `--accept-ai`(`:632-635`)
  - `declare-absent`。M-6 で失効するのは人間操作より前の宣言だけなので(`:432-434`)、確定**後**の宣言は有効です。Redundancy QA NG で PENDING に戻った後に `ensure_kp_review:1353-1368` の AUTO が発火し、AI の自動選定に置き換わります。
  - `ng` / `unng` / `resolve-gloss`
  - 修正: これらは全て、ユーザー確定レコードがあれば拒否し、`confirm-revise` / `revoke` を案内します。さらに `confirm-revise` / `revoke` には `--by` だけでなく `--user-ref`(ユーザー発言原文の delegation_log パス)を必須にします。declare-absent の `user_ref` と同じ方式です。`--by` は認証ではないためです。

### O-4 救済・補完・再選定・gloss再整合と pinned_items — 要修正
- 「確定後には呼ばれない」(R-12〜14)という前提は、コード上確認できました。救済・補完・人称整合は `_gate_chain` / `_run_backfill` の中だけで呼ばれます(`er119_kp_candidates_01.py:183-273,371-378`)。resume は `provenance_drift` のログ出力のみです(`er119_kp_human_review_01.py:1305-1311`)。
- **M8(STALE時の再バインド基準と対象)**
  - (a) 基準を「used_form が新本文に逐語で出現」から、「**各確定itemの `source_sentence` と、文法の選定文・段落が新本文に逐語で存在**」へ強めます。gloss は「本文中の意味」なので、文脈が変われば used_form が一致していても訳が合わなくなり得ます。満たさない場合は ISSUE とします。
  - (b) 再バインドの対象はレコードだけでは足りません。候補docの `text_sha256` を書き換えると `candidates_sha256` が変わり、review の署名も変わり、再finalize が必要になります。この連鎖を API 0 で決定論的に行う手順を明記してください。また `ensure_kp_review:1315-1329` の退避処理より**前**に分岐させます。Z の SRC D1 契約や Part 1 の引用は派生物として再計算されます。
- **M9(pinned_items は削除を推奨)**: STALE で全件成立なら再生成しない、一部不成立なら BLOCK、revoke 後はピン留めする確定がない。つまり pinned_items は**到達する経路がありません**。さらに外側retryは候補全体を置き換え(`:306-365`)、pinned item を Gate 連鎖の外へ出す必要があるため複雑です。削除(必要になったら別設計)とすれば、7+5 との同一ファイル競合(`er119_kp_candidates_01.py`)もほぼ解消します。

### O-5 日本語訳の保護層 — 要修正(重要)
- `japanese_gloss_tts` を protected にすると誤りになります。`convert_display_gloss_to_tts_text` の規則は実際に変更された実績があります(2026-09-27 に「～」の変換を全位置へ一般化。`er003_key_words_canonicalization.py:231-258`)。読み上げ規則の正当な改善が INTEGRITY_VIOLATION になってしまいます。
- **M2-a**: 保護するのは `japanese_gloss`(ユーザーが見て確定した表示値。フォームの `ja_gloss` と逐語一致)だけにします。`japanese_gloss_tts` は「派生物(契約つき)」とし、検査を `japanese_gloss_tts == convert(record.japanese_gloss)`(converter 版をレコードに記録)にします。Y の `canonical_text` も同様です。
- 「別訳への置換に当たらない境界」は次のように定義します。(1) 文字列を入力とする決定論的な読み変換で、(2) 音声(TTS)入力にだけ使い、(3) **表示面には出さない**もの。
- **M2-b(既存の不一致。設計で見落とされている)**: Y と Z の Standard 公開ページは、「日本語の意味」欄に TTS用テキストを表示しています。
  - Y: `er121_family_y_audio_01.py:1504`(`japanese_meaning.canonical_text` を優先)
  - Z: `er063_family_z_audio_01.py:2538`(`japanese_meaning.canonical_text`)
  - X は表示用gloss です(`:2924`)。
  - このため、gloss に「～」が含まれると、ページにはユーザーが確定した訳ではなく「なになに…」が出ます。設計の G3(Std ページに `japanese_gloss` があること)は Y/Z で誤BLOCKします。
  - 対応: Y/Z の Std ページ表示を `japanese_gloss` に修正し、G3 は表示用gloss で検査します(下の「ユーザー判断」(b) を参照)。

### O-6 LR / ハイライト — 警告のみで妥当
- KP segment は LR の対象外で(`er020:122-130`)、書面(canonical_text・ページ)は不変です。USER_02 の保護対象(表現・訳・区分・解説)は本文の読み上げ音声を含まないので、警告記録で範囲内です。
- 保護spanを LR の候補選定に追加すると、厳しくする方向(tighten-only)であっても承認済みの OPEN-540 統一仕様の変更になるため、今回は入れないでください。
- 推奨: 既存の LR 発火済みrunで、確定KPの出現位置との重なり件数を API 0 で集計します。実例があった場合だけ提案に上げます(原則5・6)。警告は完了報告に必ず表示します。
- 将来のハイライト(③)は、上記の単一アクセサ経由とし、本文に対応がない(unresolved)場合は BLOCK+修正案とする案で妥当です。

### O-7 resume/regenerate/retry/fallback と HR Lock — 妥当(M8 前提)
- resume は API 0 で読み戻すので問題ありません。G1 が TTS より前にあれば、HR Lock(`er011:333`)の「テキストが変われば新バージョン」による抜け道は上流で塞がれます。
- converter 変更による `japanese_gloss_tts` の変化は、派生物の正当な再生成として HR Lock の新バージョンになります。これは既存挙動のままでよいです。
- G0 と `finalize_kp` の idempotent 性の関係も整合しています。

### O-8 Part 2 の凍結 — 要修正
- **M6**: 凍結は Step B だけでは足りません。
  - `extract_signature` には Step A'' の prompt と `MODEL = routing.SUPPORT_MODEL` が入っています(`er120_part2_grammar_production_01.py:40,540-542`)。`require_fresh_part2:1239-1245` は、これが変わると Part2Stale にします。Z の `part2_cand` の input_sha(`:1181-1183`)も同様です。
  - つまり、モデルの経路変更(単価削減で現実に起き得る)だけで再抽出され、確定した文法が失われます。
  - 修正: 確定レコードがある場合、`require_fresh_part2` は extract/explain の両signatureの代わりに `frozen:<sha>` と「選定文が本文の逐語span、かつ candidate_id 一致」(`:1267-1270`)で判定します。`--regenerate-stage part2_cand_b1b` と reextract は revoke を必須にします。
- `ref_ja` 不一致を ISSUE にする案は修正します。Part 1訳(派生物)が再生成されるたびにユーザーへ確認を求めることになるためです。代わりに「新しい pool の値がレコードの `translation_ja` と異なる場合だけ ISSUE、一致または pool に無い場合は PASS」とします。
- `translation_ja` は v2 の payload に無いため、`explanation_full` の【日本語訳】節から決定論的に取り出します。

### O-9 A/B/C不変・flag既定ON・HR CLI互換・隔離test — 条件付き妥当
- 既定ON は、USER_02 ④の「Family別に PRODUCTION_WIRED の受入条件を満たす」と整合します。kill switch(OFF)は「ユーザー指示がある場合のみ、user_ref 付きで使う」ことを運用ルールに明記してください。
- **M7(旧run互換)**: 「G1 初回通過時にレコードを遅延生成する」案は採用しないでください。理由は2つです。(i) 検証関数が書込みを行うことになり、「runner は load と verify のみ」という契約に反する。(ii) 公開済みrunを再実行した際に、確定後の正当な修復履歴があると、ユーザーが関与しないまま即BLOCKになる。
  - 修正: 機能を有効にする前に確定した旧runでは、検証を read-only で行い、ずれは WARN と `confirmed_content_legacy_drift.json` に記録します。保護下に置くのは明示コマンド `confirm --adopt-existing`(差分を提示)からとします。
- `reselect` に `--revoke-confirmation` を必須にすると既存の CLI test が変わるので、T22 に識別子を列挙してください。

### O-10 evidence計画と 7+5 化との衝突回避 — 要追加
- 追加すべき evidence:
  - フォームpayload → `confirm --from-form` → 後続工程、の通しE2E を各Familyで最低1件(X だけでなく)。
  - **公開URL版のページ**に対する G3。
  - Y/Z の Std ページに「～」を含む gloss(M2-b の回帰確認)。
  - AI操作者ガードの拒否(M4)。
  - ISSUE が rc=4 になること(M3)。
  - Y/Z の stage_kp に追加した G1(M1)。
  - Part 2 で MODEL/routing を patch しても再抽出されないこと(M6)。
  - STALE は空白差では canonical 化で sha が変わらない可能性があります。確定item・文法の出典文**以外**の文を1語変える(再バインド成立)、出典文を変える(ISSUE)の2ケースにしてください。
- 見積の ≤¥10/Family は妥当です(大半が API 0)。
- 7+5 との順序: 委任_02-A(新module・G0/G1・CLIガード)は 7+5 と**並列で可**です。ただしレコードの schema に最初から `kind` を入れ、候補数・上限を定数で決め打ちしない(SLOT_RULES と候補doc から読む)ことが条件です。`er119_kp_human_review_01.py` のフック追加は、先に完了した方が merge し、もう一方が rebase する直列にします。M9 で pinned_items を削除すれば、`er119_kp_candidates_01.py` での競合はなくなります。
- **関連(フォーム側の契約不足)**: DATA_MODEL_02 の v2 には `candidate_id`・`kind`・`candidates_sha256` がなく、`term` しかありません。canonicalization 後は同じ used_form が複数候補にあり得るので、term での対応付けは曖昧です。これら3項目を v2 に追加してください(フォーム側の小さな変更)。`ja_gloss_status != official` の訳が確定された場合は、`op_select` が拒否する前に ISSUE(修正案を提示)へ回す流れを明記してください。

### 実装へ進んでよいか
**条件付きで可。** M1〜M9 を DESIGN_02 として反映し、Fable が照合した後に委任_02-A へ進めます。M1・M2・M3・M4 を欠いたまま実装するのは不可です。

### Fable がユーザー判断に上げるべき事項(分離)
- (a) **文法解説の「ユーザー確定」をどう扱うか**: 現行のフォームでは文法解説が全記事「未生成」で、Step B は確定後に生成されます。そのため USER_02 の「確定した解説全文」は、事実上ユーザーが見ていない文になります(設計では `stepB_generated_frozen`)。ユーザーに見せてから確定させるには、提示前に候補分の Step B を生成する必要があり(1記事あたり約¥0.3×候補数、工程順の変更)、新仕様になります。フォーム側の委任で既に判断候補に挙がっていれば重複不要です。
- (b) **Y/Z の Std 公開ページの「日本語の意味」欄**(M2-b): 表示を、確定した表示用gloss(`japanese_gloss`)に改めるのか、音声と同じ TTS用テキストを表示する現状を許容するのか。表示とTTSの分離仕様(KEYPHRASE-DISPLAY-TTS-SEPARATION)で「表示=japanese_gloss」と定義済みであれば、USER_02 の範囲内のバグ修正として Fable 判断で可です。定義がなければ、Production ページの表示変更としてユーザー判断です。
- これ以外(LR の保護span、③・Std の②③・文法2件目の消費者)はユーザー判断に上げる必要はありません。LR は、evidence で実例が出た場合のみ提案します。③等は前提どおり既に分離済みです。

(Opusレビュー原文ここまで)
