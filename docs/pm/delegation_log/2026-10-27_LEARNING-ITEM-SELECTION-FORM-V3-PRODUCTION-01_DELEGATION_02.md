## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02(ユーザー追加指示①③④: 全Key Phrase/Key Word候補にエンドユーザー提供予定の日本語訳とAI選定理由を表示[既存gloss/`reason_ja`等を再利用、未生成・未確定は明示し仮訳を正式扱いしない]、送信データに日本語訳・選定区分・文法解説全文・自由コメントを欠落なく含め、AI選定理由は「確認用」として区別。承認済みUI仕様は維持。API 0・JPY0)。並行Agent: KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01(②確定内容保護の調査・設計、read-only。あなたの`DATA_MODEL`/出力schemaを参照する)。あなたの所有=`user_test/selection_form_v3/**`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{PORT_02,DATA_MODEL_02,SEND_CHECK_02,VERIFY_02,TEST_02,JA_SOURCE_SURVEY_01}.md`+`build_data_01.py`拡張+test、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(日本語訳・理由の出力項目追加のみ)、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_{USER_02,DELEGATION_02}.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM2.md`。Production Python経路編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み仕様(フォームv3)への追加指示の実装(承認範囲内)。到達上限=IMPLEMENTED+公開+自己検証(ユーザー実操作確認待ち)。
- 禁止: 日本語訳・理由のAI再生成(既存成果物の再利用のみ。無い場合は「未生成」表示)、仮訳の正式扱い、UI仕様(①②③累積上限・文法独立・コメント)の変更、Production経路の変更、禁止Git操作。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER_02.md`へ逐語保存(並行Agentも参照)。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_02.md` をN=699から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02」のものを採用(同時刻に別委任あり、先頭一致必須)。

## ユーザー指示(原文・逐語)

【追加指示｜学習項目選定フォームの日本語訳・選定理由表示と確定内容の保護】

対象：Family X/Y/Z、Standard/Advanced共通。

現在実装中の学習項目選定フォームv3に、次の内容を追加してください。

**① 日本語訳・選定理由の表示**

- 全Key Phrase・Key Word候補に、エンドユーザーへ実際に提供する予定の日本語訳を表示する。
- AIが生成した日本語の選定理由も併記する。
- 既存の候補生成結果・gloss・`reason_ja`等を調査して再利用し、不要なAI再生成をしない。
- 日本語訳と選定理由が未生成・未確定の場合は、その状態を明示し、仮訳を正式訳として扱わない。
- ①②③のチェック方式、累積上限、文法独立枠、自由コメント等の承認済みUI仕様は維持する。

**② ユーザー確定内容の保護（重要）**

ユーザーがフォーム上で選定・確定した次の情報は、以降の生成・組立・公開工程で勝手に変更しない。

- Key Phrase／Key Wordの英語表現
- 各英語表現に対応する日本語訳
- ①②③の選定区分
- 採用した文法事項と、エンドユーザー向け文法解説全文

選定確定後、AIによる自動書換え・再選定・別訳への置換は禁止する。

既存のHuman Review Lock・retry／fallback／resume・本文ハイライト・公開ページまで、同じ確定内容が一貫して引き継がれる設計とする。

既存の品質Gateは維持する。確定内容に品質上の問題が見つかった場合は、黙って変更せず、修正案を提示して再確認を求める。

**③ フォーム送信データ**

英語表現だけでなく、日本語訳、選定区分、選定した文法解説全文、自由コメントを欠落なくChatGPTへ渡す。

AIの選定理由は確認用情報として保持し、ユーザーが確定した英語・日本語訳・解説本文と区別する。

**④ 検証・Status**

フォームの公開ページで表示・選定・送信を確認する。

特に、選定確定後の英語・日本語訳・文法解説が勝手に変化しないことを、既存Production経路と後続工程を含めて検証する。

既存の承認済み品質基準・Gateを変更しない。

必要なテスト、runtime evidence、SSOT/Git反映を完了し、Family別にPRODUCTION_WIREDの受入条件を満たすこと。

既存委任の承認範囲内で対応し、新たな仕様判断が必要な場合のみ報告してください。

(原文ここまで。本委任=①③④のフォーム側。②は並行委任)

## 実施事項

1. **日本語訳・理由の出所調査(`JA_SOURCE_SURVEY_01.md`)**: `kp_candidates.json`の候補schemaで「エンドユーザー提供予定の日本語訳」に当たる項目(gloss/`meaning_ja`/`gloss_ja`等。gloss再整合・救済後のglossの扱い、HR gloss pending旗)と「AI選定理由」(`reason_ja`/`reason`。call1 Prompt 2は理由を出さない事実)を、`er119_kp_human_review_01.py`/`er119_kp_candidates_01.py`/`DATA_CONTRACT_01.md`から特定。公開ページで実際に表示される日本語訳の生成元(KP日本語意味=P8-KP音声・ページ表示)との同一性を確認(同じ項目を使う)。Trial-02由来データ(猿の手Adv)は`RESULT_02.md`の「日本語意味」「選定理由」列。文法はPart 2候補(解説全文は選定後生成=現状「未生成」表示)。
2. **フォーム実装**: 各候補行に日本語訳(正式/仮/未生成のラベル付き)とAI選定理由(「AI理由・確認用」ラベル、折りたたみ可)を表示。未生成・未確定は明示(`status: official|provisional|missing`)。UI仕様不変。データJSON schema拡張(`ja_gloss`, `ja_gloss_status`, `reason_ja`, `reason_source`)。`export_form_data_01.py`/`build_data_01.py`を拡張して既存6+1件のデータを再生成(AI再生成なし)。
3. **送信データ**: 構造化JSON(schema v2: 記事・レベル・候補ごとに英語表現・日本語訳・区分・AI理由[`for_reference_only`]、文法=選択した文法名+解説全文[未生成なら`missing`]、自由コメント、timestamp)と人間可読テキストに全項目を含める。ChatGPT URL長の上限(前回2985字)を再確認し、超える場合はコピー誘導。
4. **test**: schema検証、表示ロジック、送信データの欠落なし(全項目の有無をassert)、既存25+6件の維持。headless検証(表示・選定・送信テキスト内容)。
5. **公開・検証(`VERIFY_02.md`)**: push後HTTP 200、Console error 0。実操作確認チェックリストを更新(日本語訳・理由表示、送信テキストの内容確認を追加)。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_01,SEND_CHECK_01,DIFF_01}.md`、`user_test/selection_form_v3/{index.html,form_logic.js,data/articles.json,data/monkeys_paw__b1b.json}`
- `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/DATA_CONTRACT_01.md`、`tools/export_form_data_01.py`
- `er119_kp_human_review_01.py`: Grep `gloss|reason|meaning_ja|render_request_md` ±10、`er119_kp_candidates_01.py`: Grep `gloss|reason_ja` ±10
- 公開ページのKP日本語意味の生成元: Grep `kp_ja_meaning|KP_JA|japanese_meaning` in `er019_family_x_audio_production_runner_01.py`/`er121_family_y_audio_01.py`/`er063_family_z_audio_01.py` ±5

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_02.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+node test
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_FORM2.md`にOPEN-545更新文案、判断候補(新たな仕様判断が必要な場合のみ)。

## Git

- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02: 候補の日本語訳・AI選定理由表示(既存gloss/reason再利用、未生成明示)+送信データschema v2(日本語訳・区分・文法解説全文・コメント)+検証(API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/02`。push。

## 報告

`docs/pm/RESULT_PACKET_FORM2.md`: (0)T-0、(1)日本語訳・理由の出所と採否、(2)実装差分、(3)送信データ検証、(4)test・公開検証・チェックリスト、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾5行要約。