## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_03(ユーザー正式決定2026-10-27(USER_03=「V3フォーム送信・コピー改善の優先実装+AI島文法選定確定」§1-A・§7): AI島Std/Adv=KP/KW各10件USER_CONFIRMED+**文法0件を最終確定**(再選定不要、0件を理由に停止しない)。本委任=確定内容の正式反映(新run・KP確定・文法0件確定)→承認済み本文を再利用した完成記事制作(Std/Adv: support texts・TTS・Gate・assemble・player/pages・page_verify)→通常の最終試聴ページ公開→受入材料。有料上限¥150(案件見積300円以下=AI自律。X記事1セットの先例費用を`COST_01`に記録し超過見込みなら停止報告))。ユーザー原文=`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_03.md`(FORM委任_06が保存。未作成なら本委任文引用§1-A/§7で足りる)。payload=`docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/ai_island_temple__{a2,b1b}__user_confirmed_01.json`(委任_02、照合一致済み。`grammar_status`を`pending_reselection`→ユーザー決定により`[]`=0件確定へ。payload自体は改変せず、文法0件確定は`USER_03`を`--user-ref`にして別途確定)。
並行Agent: (a)GPG 委任_05B(`er120_part2_wiring_01.py`・integration test。**05Bのcommitがorigin/mainに載るまで(`git log origin/main -1 -- er120_part2_wiring_01.py`で`a1bb5fa71`以降の05B commitを確認)KP確定・制作を開始しない**。待ち時間は照合・コマンド準備・公開ページ雛形に充てる)、(b)YSP 委任_08(`er019_family_x_audio_production_runner_01.py`の`audience`受け口を編集中の可能性=runnerは**実行のみ**、編集しない)、(c)FORM 委任_06(設計)、(d)SLOT-23-CONSUMER-DESIGN-01(②③消費者の設計、read-only)。あなたの所有=新run dir `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/`(既存`run_ai_01`/`run_kp75_ev_01`は改変しない)、`user_test/family_x_ai_island_form_01/`(最終試聴ページ)、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{KP_CONFIRM_02,GRAMMAR_ZERO_CONFIRM_01,BUILD_01,VERIFY_01,COST_02,HR_*}.md`+`tools/`、`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF3.md`(gitignore、`-f`禁止)。Production Python編集禁止(不具合は報告)。SSOT編集権なし。pathspec付きcommit(wav/raw_usage_log/STOP/lock不追跡、公開mp3は`user_test/`のみ)。

## 性質/禁止

- 性質: ユーザー確定内容の正式反映+完成記事制作(承認済み経路)。到達上限=完成版公開・Fable受入待ち(記事の最終受入はユーザー試聴PASS後)。
- 禁止: 本文再生成、KP再選定・再生成、確定内容(英語・訳・区分・candidate_id)の変更、文法の再選定依頼、Gate緩和・HR Lock解除、同一run 5分3回起動・150秒未満再起動、¥150超過、Production Python編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- ①②③の扱い(Fable指示): 現行X Productionの消費者=①(KP 3件: KP音声+日本語意味)、Adv Part 1単語解説=**①+②の5件**(Advのみ)。Std ②(追加解説)と③(本文ハイライト・短い日本語意味)は現行Productionに消費者がなく、並行設計(d)で共通機構を設計中。本委任では**確定レコードの`unconsumed[]`に③(Std/Adv)とStd ②を保持**し(黙って捨てない)、Adv Part 1は確定①+②の5件(順序=①→②、ユーザー確定順)で生成、現行構成で完成版を制作する。③/Std②の表示は共通機構配線後に**ページ再ビルド(API 0)**で追加する前提(音声再生成なし)。完成版ページには「③本文ハイライト・Std②は後続反映予定」の注記を1行入れる。
- 時間見込み: 約3h(05B待ち含む)。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2(有料前): `py tools/stop_scope_check_01.py --managed-id AI-ISLAND-FORM-PRODUCTION-01 --run-dir <run> --out <run>/audit/stop_scope_check.json`、起動間隔150秒以上(ログに時刻)、同一run 5分3回禁止、`.venv\Scripts\python.exe`+`TTS_EXECUTION_MODE=STANDARD`、有料stage実行前に「そのstageがなぜ必要か」を1行記録。T-3: 費用はusage log実測(`COST_02.md`、Std/Adv・stage別、量産単価¥70比)。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_03.md` をN=730から順に試し、先頭「## 管理ID」+「AI-ISLAND-FORM-PRODUCTION-01 委任_03」のものを採用(NOT_FOUNDなら数分待って再試行、不可なら「抽出不可」明記)。

## ユーザー決定(USER_03 §1-A/§7 逐語)

### A. AI島の文法再選定は不要

Family X「AIの仮想の島」について、Standard／Advancedともに文法0件を正式確定します。

- Key Phrase／Key Wordは、先に送付した両レベル各10件の選定結果を維持。
- 文法：Standard 0件、Advanced 0件。
- 文法の再選定・再提出を求めない。
- 旧フォームで選択した0件を、今回のユーザー明示判断によって最終確定とする。
- 文法0件を理由に記事完成工程を停止しない。

今回の判断はAI島個別の確定内容であり、全Family共通の文法選定仕様は「AI評価Top 1・Top 2を提示、原則1件、適切な候補がなければ0件」のまま維持します。

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

(引用ここまで)

## 実施事項

1. **新run準備**: `run_ai_01`をコピーして`ai_island_temple__run_form_prod_01`(本文・meta・既存成果物。旧HR PENDING 7件のreview/lockは持ち込まない)、`run_kp75_ev_01/<lv>/key_phrases/kp_candidates.json`(候補集合sha一致)を配置。KP review=フォーム確定(`er128 confirm --from-form <payload> --run <run> --level <lv> --by user --user-ref <USER_02 path> --grammar-pending`、`KP_CONFIRM_01.md`の手順)。`confirmed_selection.json`のsha・`actor=user`・10件・区分を確認(`KP_CONFIRM_02.md`)。
2. **文法0件確定(`GRAMMAR_ZERO_CONFIRM_01.md`)**: X runnerの`study_text`(両level: Step A''→Top1/Top2事前生成=約¥0.3〜0.6。Production経路の初回runtime evidenceにもなる)を実行後、`er128 confirm --grammar-from-form <payload_grammar_zero.json(grammar:[])> --run <run> --level <lv> --by user --user-ref <USER_03 path>`で0件omit確定(`zero_reason=human_omit`)。pendingのまま進めない。`grammar-pregen`/exporterの出力(Top1/Top2・sha)を証跡として保存。
3. **制作**: X runnerの残stage(`--help`で確認: support/KP音声/Adv Part 1(①+②5件)/tts a2・b1b/gate/assemble/player/page_verify)を順に1起動ずつ(150秒規律)。承認済みStyle/Voice/Chunk/ASR Gate維持。HR停止時は新形式(原稿・ASR全文・相違点・NG理由・推奨音声1つ・AI評価、質問1つ)で`HR_<segment>_01.md`+公開HTMLを作り、停止・報告(Take比較を求めない)。
4. **公開(`user_test/family_x_ai_island_form_01/index.html`)**: Std/Adv通し再生+パート別+原稿+学習内容(①KP+Adv Part 1=①+②、Std②/③は「後続反映予定」注記)+制作情報。HTTP 200。
5. **受入材料(`VERIFY_01.md`)**: 確定20件とページ/音声/KP docの逐語一致(英語・訳・区分、`unconsumed[]`に③とStd②)、本文sha=承認済み、Gate結果、G1〜G4通過記録、費用(`COST_02.md`、量産単価比)、所要時間。

## 事前指定Read一覧

- `docs/research/AI-ISLAND-FORM-PRODUCTION-01/{SURVEY_01,CONFIRMATION_CHECK_01,KP_CONFIRM_01,GRAMMAR_TOP2_01}.md`+`payloads/`
- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{IMPLEMENTATION_05A,IMPLEMENTATION_03}.md`(X stage列・CLI)、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{IMPLEMENTATION_02B,EVIDENCE_X_02}.md`(X確定→下流の先例コマンド)
- `er019_family_x_audio_production_runner_01.py`(origin/main: `--help`出力、Grep `--stage|--run|--out-dir|approved-budget|study_text|player` ±5)、`er128_kp_confirmed_content_01.py`(origin/main: Grep `grammar-pending|grammar-from-form|add_argument` ±3)
- 先例の完成版ページ構成: `user_test/family_y_production_redelivery_fee_03/index.html`(構成のみ)、X公開記事の`user_test/`配下1件(Grep不要・構成確認)
- X記事1セットの費用先例: `docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/COST_01.md`、`er005_output/cost_baseline_01/cost_summary.json`(Grep `family_x|ai_island` ±3)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_DELEGATION_03.md --json-out ...\_check.json`
- 上記1〜3のコマンド(実行前に`--help`/dry-run)、有料前stop_scope_check
- 公開確認: `Invoke-WebRequest <公開URL>` → 200
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_AIF3.md`にOPEN-561更新文案(KP確定・文法0件確定・完成版公開・費用)、OPEN-545/556関連、X Std/Advの文法新仕様runtime evidence(0件経路)としての記録文案。

## Git

- commit(複数可): `AI-ISLAND-FORM-PRODUCTION-01 委任_03: AI島Std/Adv ユーザー確定(KP/KW各10件・文法0件)を新runへ反映→完成記事制作・公開(実費¥NN)`。trailer: `Delegation: AI-ISLAND-FORM-PRODUCTION-01/03`。push(`git push origin HEAD:main`)。

## 報告

`docs/pm/RESULT_PACKET_AIF3.md`: (0)T-0+05B到着確認、(1)KP確定・文法0件確定の記録、(2)制作stage別結果(Gate/HR)、(3)公開URL・ページ構成、(4)受入材料(VERIFY要点、③/Std②のunconsumed保持)、(5)費用・所要・量産単価比、(6)判断候補、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)SSOT文案、commit hash・raw URL。末尾10行要約。