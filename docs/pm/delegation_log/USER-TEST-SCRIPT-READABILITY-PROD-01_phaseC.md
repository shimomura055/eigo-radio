## 管理ID

USER-TEST-SCRIPT-READABILITY-PROD-01 / Phase C(翻訳asset正式配置+mapping最終化+全20 level E2E+Landing/TSV 20 URL更新+公開runtime確認)。並行Agentなし(Phase A/B1/B2/Dは全て完了、Fable確認済み)。音声stageなし(TTS/ASR/Ledger/Key Phrase生成を実行しない)のためaudio_stage.lockは不要(存在していたらSTOPして報告)。`docs/pm/ACTIVE_TASK.md`の固定ヘッダ+要約をPhase C内容で更新してから開始。

## 性質/到達上限Status/禁止事項

- 性質: Production wiring(ユーザー正式承認済み仕様の20 level展開、URL更新はユーザー許可済み)。
- Phase Cで到達する最大Status: `PHASE_C_DONE`(全20 level配線・Landing/TSV更新・公開E2E PASS)。**`PRODUCTION_WIRED`は宣言しない**(Free-Address A2のKey Phrase 2件[人称一般化によりqa_overall_status=REVIEW_REQUIRED]のユーザー確認がFable経由で別途進行中のため。確認後にPhase EでSSOT反映+最終Status確定を行う)。
- SSOT本体(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`)はPhase Cでは編集しない(Phase Eで実施)。ただしPhase Eが転記できるよう、RESULT_PACKETにSSOT追記文案を用意する。
- 禁止: canonical article本文・player・audio・Key Phrase asset(Phase Dの新`kp_fix_01`含む)の変更禁止。`user_test/articles_2026_0918.html`はStandard/Advancedの`href`20本以外(タイトル・概要・カテゴリー・順番・CSS・ボタン構成)変更禁止。TSVはURL列2本以外(category/title_en/title_ja/summary_ja・行順)変更禁止。`user_test/unified.html`の変更はPhase Cで発見した表示不具合の修正に限る(変更した場合は差分と理由を報告)。Trial path(`user_test/trial/...`)参照禁止。外部API支出禁止(¥0)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。mp3/wav追加禁止。
- STOP条件: (1)翻訳assetのreprint(Standard Comment再掲)が現行player DOMのComment原文と一致しない、(2)Landing/TSV/個別URLの整合が取れない、(3)公開URLでのBrowser E2Eが機械判定でFAILし原因が本タスク側にある、(4)wrapper共通化が安全にできない、(5)新しいProduct仕様判断が必要。該当時はRESULT_PACKETに記録して終了(推測で進めない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md`)

## ユーザー指示(原文)

「必要であれば各記事の固定SHA URLは変更してよい。ただし、変更後URLを必ず正式Web一覧ページへ反映する。TSVの20 URLも同時に更新する。Web一覧ページとTSVのURLを一致させる。古いリンクをWeb一覧ページに残さない。ユーザーが実際に共有する10記事一覧ページから、常に最新の正式記事へ到達できること。」「Landing page href = TSV URL = 実際にBrowser E2EしたProduction URL を一致させる。」「Landing pageの内容・デザインは今回変更しない。変更対象: Standard/Advancedリンク先のみ。」「TSV: 10記事/3カテゴリー/順番維持/タイトル維持/概要維持/Standard・Advanced対応維持/URLのみ必要箇所更新。」「Browser E2E: 全20 URLについて機械確認(HTTP正常/src正しい/level正しい/Key Phrase asset load/translation asset load/highlight mapping完了/JS errorなし/日本語訳表示あり)。代表Browser E2E: Standard News系1・Voices系1・Future系1、Advanced News系1・Voices系1・Future系1、追加 Personalized News A2/B1、修正対象2 Standard(Free-Address A2、AI Hiring A2)。PC/Mobileで確認。」「Key Phrase mapping最終要件: 20 level・全Key Phraseについて article/level/Key Phrase/mapped source text/mapping type/highlighted/unresolved を記録。unresolved=0。」「Regression: 本文無変更/本文音声無変更/Play/Seek/Key Phrase一覧/Standard・Advanced表記/日本語訳/Comment表示/Landingレイアウト無変更/カテゴリー・順番無変更。」「Dangling Reference Check: Production unified.htmlがTrial path参照なし/translation asset正式path/20 levelすべて正しいasset参照/修正済みKey Phrase asset参照/古いKey Phrase assetが正式経路に残っていない/Landing pageが旧SHA記事を参照していない/TSVが旧SHA URLを保持していない/Personalized News B1 FIX-01維持/AI Hiring A2は修正後canonicalを参照。」

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md` L1-157(Phase A節: wrapper実装・asset解決方式・checker仕様)、L158-387(Phase D節: 新src 2件、seek FAILの環境要因記録[item 10]、Phase C引き継ぎ[item 17])
2. `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01_phaseB1.md` L45-50、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01_phaseB2.md` L60-65(Phase Cへの注意点)
3. `user_test/translations/index.json` 全文(20 level、Phase Dで2行更新済み)
4. `user_test/unified.html`: Grep `translations/|kp_mapping|translation_ja|reprint|source_ja|heading_ja|kp-hl` → 該当範囲Read(asset読込・翻訳section描画・reprint描画の実装確認。全文Readは修正が必要と判明した場合のみ)
5. `docs/pm/tools/user_test_readability_check.py` 全文(拡張対象)、`docs/pm/tools/phase_d_e2e_check.py` Grep `def |argparse|add_argument` → 該当範囲
6. `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/e2e_result_all20.json`: Grep `Range|server|base` → Phase Aで使ったRange対応ローカルサーバの方式を特定(Phase Dの`python -m http.server`はRange非対応でseekがFAILした。Phase Cのローカル確認はRange対応サーバを使うか、公開rawcdn URLでseekを判定する)
7. `docs/pm/tools/user_test_page_e2e_check.py`: Grep `githack|External Content|interstitial` → githack interstitial自動通過処理の流用元
8. `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv` 全文、`user_test/articles_2026_0918.html`: Grep `href=` → 20本の位置
9. `user_test/translations_wip/**/translation_ja.json`(18件)は移動対象。内容確認はreprint照合スクリプトで機械的に行い、全文Readはしない
10. `user_test/translations/free_address/A2/kp_mapping.json`、`user_test/translations/ai_hiring/A2/kp_mapping.json` 全文(mapping_type再判定対象)

## 事前指定Grep一覧+追記位置・更新位置の手順

- C-1 翻訳asset正式配置: `user_test/translations_wip/<article_id>/<level>/{translation_ja.json,translation_qa.json}`(18 level)を`user_test/translations/<article_id>/<level>/`へ移動(`git mv`不可[未追跡]、通常moveの後`translations_wip`ディレクトリを削除し空であることを確認)。Personalized News 2 levelはPhase A配置済み(そのまま)。
- C-2 reprint照合: 全10 Standard levelについて、`translation_ja.json`の`type=reprint`各sectionの`text_ja`が、**現行canonical player DOM**(`index.json`のsrcが指すファイル。Free-Address A2/AI Hiring A2は`kp_fix_01/a2/player.html`)のComment原文と完全一致することをスクリプトで確認し`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/reprint_check.json`に記録(1件でも不一致ならSTOP条件(1))。Advanced 10 levelは`type=translation`のComment数=DOMの英語Comment数を確認。
- C-3 mapping_type再判定: Phase Dの`kp_mapping.json`2件は`source_span`一致を全て`exact`と表記しているが、Phase Aの分類規約(exact=表示phraseと本文が正規化後に完全一致、それ以外は`inflection`/`tense`/`plural`/`function_word`等)に合わせて再判定する。具体的に free_address/A2: `belong there`→"belonged there"=`tense`、`a place of one's own`→"a place of my own"=`function_word`(人称一般化one's→my)、`change one's surroundings`→"changing my surroundings"=`inflection`(+人称一般化)、`source of stability`/`on paper`=exact。ai_hiring/A2は5件とも表示phraseと本文が同一文字列であることを確認のうえexact維持。`rationale`に1行根拠を記す。`matched_text`/`occurrences`は変更しない。
- C-4 全100 Key Phrase mapping一覧: 20 levelの`kp_mapping.json`を集約し`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/kp_mapping_all100.json`と同`.md`(表: article/level/phrase/matched_text/mapping_type/occurrences/highlighted[E2E実測]/unresolved)を生成。集計: total/mapped/exact/non_exact(種別内訳)/unresolved(=0であること)。
- C-5 wrapper表示確認(ローカル、Range対応サーバ): 20 level×PC(1280×800)/mobile(390×844)で`user_test_readability_check.py`を実行(必要なら`--index user_test/translations/index.json`を正としてsrcを解決するオプションを追加。TSVはまだ旧srcのため)。判定項目: header Standard/Advanced表記、Key Phrase 2列・ラベル無し、水色ハイライト数=`kp_mapping.json`のoccurrences合計、日本語訳section存在、section数=`translation_ja.json`のsections数、Standard reprint件数=Comment数かつグレーcomputed style(color rgb(91,100,114)/background rgb(242,243,245))+ラベル「既存Comment(再掲、翻訳ではありません)」表示、Advanced Comment訳件数=Comment数、`heading_ja`が見出しとして表示(Family C: Scene見出し、Voices: Voice見出し、News: Full Story/Point見出し)、横スクロールなし、Play進行、Seek(Range対応サーバ時)、JS errorなし。AI Hiring A2は新標準player(`kp_fix_01/a2/player.html`)でComment DOMが`.comment`classを持つ想定。もし持たない場合はcheckerのComment数取得を翻訳asset側基準に変える(表示自体はassetで担保)。screenshotは全40通り保存(`phase_c/local/`)。
- C-6 commit 1(asset+mapping+checker+wrapper修正があれば)→push→SHA1取得。
- C-7 20 URL生成: `https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA1>/user_test/unified.html?src=<index.jsonのsrcをURLエンコード>&level=<A2|B1>&en=<TSV現行値>&ja=<TSV現行値>`。en/jaはTSV現行URLのパラメータ値をそのまま引き継ぐ(変更しない)。Personalized News B1はsrc=`er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01/player.html`(FIX-01)維持。Free-Address A2/AI Hiring A2はPhase Dの新src。
- C-8 TSV更新: `standard_url`/`advanced_url`の20セルのみ置換(他列・行順・ヘッダー無変更をdiffで確認)。Landing更新: `user_test/articles_2026_0918.html`の20 `href`のみ置換(diffが`href`行のみであることを確認)。`href_match.json`(Landing href=TSV URL 20/20完全一致)を生成。
- C-9 commit 2(TSV+Landing+href_match)→push→SHA2取得。Landing公開URL=`https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA2>/user_test/articles_2026_0918.html`。
- C-10 公開runtime確認(rawcdn実物、githack interstitial自動通過): (a)全20 URL機械確認(HTTP 200/src/level/index.json解決/kp_mapping load/translation load/ハイライト数/JS error/日本語訳section)、(b)代表10 URL(Standard: Tiny Bags A2[News]・Free-Address A2[Voices・修正対象]・Home Robots A2[Future]・Personalized News A2・AI Hiring A2[修正対象] / Advanced: Convenience AI B1[News]・Personalized News B1[Voices]・Memory B1[Future]、計8+PN両方は既出のため代表は上記8=Standard5+Advanced3。不足分としてAdvanced Voices=Free-Address B1、Advanced News=Young Travelers B1を追加し計10)でPC/mobileフルチェック(Play進行・Seek含む)、(c)Landing SHA2ページ: 20 href=TSV一致、3列/1列レイアウト・ボタン1行収まり(FIX-01基準)・タイトル/概要/カテゴリー/順番がTSVと一致、代表4クリックで遷移URL一致・Play進行。screenshot `phase_c/public/`。
- C-11 canonical無変更: `docs/pm/tools/sha256_snapshot.py`でPhase Aの`sha256_before.json`と同じ対象(旧19 player配下+Landing+TSV)を再取得し、差分が「Landing/TSV(意図した20 URL置換)」のみであることを確認。Phase Dの新`kp_fix_01`配下は新規のため別途一覧(`phase_c/kp_fix_01_inventory.json`)。
- C-12 Dangling Reference Check(ユーザー指示の9項目)を`phase_c/dangling_reference_check.json`に項目別PASS/FAILで記録。特に: `unified.html`にGrep `trial`該当なし、`index.json`の20 srcが全て存在しTSV srcと一致、Landing/TSVに旧SHA(`240e0723`/`7ea8bd7a`/`bf5c1e3b`)が残っていない、`translations_wip`が存在しない。
- 更新位置: `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`末尾に`## Phase C`節追記(Phase A/D節は残す)。`docs/pm/ACTIVE_TASK.md`更新。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md --json-out docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md_check.json`
- reprint照合: `.venv\Scripts\python.exe docs\pm\tools\translation_reprint_check.py --index user_test\translations\index.json --translations user_test\translations --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\reprint_check.json`(新規、Phase B1/B2が使った照合ロジックを共通化)
- mapping集約: `.venv\Scripts\python.exe docs\pm\tools\kp_mapping_aggregate.py --translations user_test\translations --out-json docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\kp_mapping_all100.json --out-md docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\kp_mapping_all100.md`(新規)
- ローカルE2E: Phase Aと同じRange対応サーバ起動方法(Read一覧6で特定した方法。不明な場合は`docs/pm/tools/range_http_server.py`を新規作成[`http.server`ベース+Rangeヘッダ対応]し`Start-Process -NoNewWindow .venv\Scripts\python.exe -ArgumentList "docs\pm\tools\range_http_server.py","--port","8765"`で起動)→ `.venv\Scripts\python.exe docs\pm\tools\user_test_readability_check.py --base http://localhost:8765 --index user_test\translations\index.json --tsv docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --translations user_test\translations --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\local\e2e_result_local20.json --screenshots docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\local`
- 公開E2E(commit 2後): `.venv\Scripts\python.exe docs\pm\tools\user_test_readability_check.py --urls-from docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --translations user_test\translations --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\public\e2e_result_public20.json --screenshots docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\public --full-check "tiny_bags:A2,free_address:A2,home_robots:A2,personalized_news:A2,ai_hiring:A2,convenience_ai:B1,personalized_news:B1,memory:B1,free_address:B1,young_travelers:B1"`(`--urls-from`/`--full-check`は新規オプション、仕様をRESULT_PACKETに記す)
- Landing確認: `.venv\Scripts\python.exe docs\pm\tools\landing_page_e2e_check.py --url https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA2>/user_test/articles_2026_0918.html --tsv docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\public\landing_e2e.json --screenshots docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\public`(`docs/pm/closeout_136_e2e/landing_10_01/`で使った検証スクリプトが残っていればそれを流用、無ければ新規作成。`<SHA2>`はcommit 2の実SHAに置換して実行)
- sha256: `.venv\Scripts\python.exe docs\pm\tools\sha256_snapshot.py --paths-from docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --extra user_test\articles_2026_0918.html --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_c\sha256_after_phase_c.json`(TSVは更新後のため新src 2件を含む。Phase A `sha256_before.json`との比較は旧19 player配下について行い、差分ゼロを確認)
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test_*.py"`(既知3件以外の新規失敗なし)

## SSOT追記文

Phase CではSSOT本体を編集しない。RESULT_PACKET `## Phase C`節末尾に、Phase Eが転記する以下の文案を用意する: (a)`CURRENT_SPEC.md`「ユーザーテスト表示仕様」追記案(Key Phrase本文対応箇所ハイライト/表層差対応/不整合時はKey Phrase sourceを本文へ追従/水色/日本語訳表示/Standard Comment再掲/Advanced Comment翻訳)、(b)`DECISION_LOG.md`エントリ案(Trial VALIDATED→ユーザー正式承認→exact-only解釈撤回→2 A2不整合発見→ユーザー判断[本文に合わせてKey Phrase修正]→URL変更許可→Landing/TSV完全反映→Phase A/B/D/C結果→費用)、(c)`ARTIFACT_REGISTRY.md`行案(Production wrapper/translation assets/kp_fix_01 2件[旧SUPERSEDED]/Landing新URL)、(d)`OPEN_ITEMS.md`: OPEN-169 close文案+再発防止新規Open Item案(Phase D item 15の(a)(b))。

## Git(明示add対象・コミットメッセージ・trailer)

- commit 1: 明示add `user_test/translations/**/translation_ja.json`・`**/translation_qa.json`(18 level新規)、`user_test/translations/free_address/A2/kp_mapping.json`、`user_test/translations/ai_hiring/A2/kp_mapping.json`、`docs/pm/tools/translation_reprint_check.py`、`docs/pm/tools/kp_mapping_aggregate.py`、`docs/pm/tools/user_test_readability_check.py`、`docs/pm/tools/range_http_server.py`(作成時)、`docs/pm/tools/landing_page_e2e_check.py`(作成時)、`user_test/unified.html`(修正時のみ)、`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/reprint_check.json`・`kp_mapping_all100.{json,md}`・`local/*.json`・`local/*.png`。メッセージ: `USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-1: 翻訳asset18 level正式配置+reprint照合+mapping_type再判定+全100 KP一覧+ローカルE2E`。
- commit 2: 明示add `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`、`user_test/articles_2026_0918.html`、`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/href_match.json`。メッセージ: `USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-2: 20記事URLを新Production SHAへ更新(Landing href=TSV)`。
- commit 3: 明示add `docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/public/*`、`.../phase_c/dangling_reference_check.json`、`.../phase_c/sha256_after_phase_c.json`、`.../phase_c/kp_fix_01_inventory.json`、`docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseC.md`(+`_check.json`)、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`、`docs/pm/ACTIVE_TASK.md`。メッセージ: `USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-3: 公開runtime E2E(20 URL+Landing)+Dangling Reference Check+報告`。
- 各commitのpush前後で`git fetch origin`、最終main=origin/main確認。trailer各commit: `Task-ID: USER-TEST-SCRIPT-READABILITY-PROD-01`。`git status --porcelain`で他タスクの未追跡ファイル・wavの混入なしを確認。

## 報告(RESULT_PACKET項目)

`## Phase C`節に:
1. Phase C Status(`PHASE_C_DONE`/STOP理由)
2. 翻訳asset配置結果(20/20 path一覧、translations_wip削除確認)
3. reprint照合結果(10 Standard、各true)・Advanced Comment数一致(10)
4. mapping_type再判定結果(変更した項目と根拠)
5. 全100 Key Phrase集計(total/mapped/exact/non_exact種別内訳/unresolved=0)+`kp_mapping_all100.md`のpath
6. ローカルE2E結果(40通り、項目別、FAILがあれば原因と対処)
7. wrapper修正の有無と差分理由
8. commit 1 SHA1、20 URL一覧(TSV更新後の全文)
9. TSV diff要約(URL列2本のみ)・Landing diff要約(href 20行のみ)・href_match 20/20
10. commit 2 SHA2、Landing公開URL
11. 公開E2E結果: 20 URL機械確認(項目別)、代表10のPC/mobile(Play/Seek含む)、Landingページ(href一致・レイアウト・代表クリック)
12. Play/Seek regression(公開URLでの実測値)
13. canonical無変更証拠(sha256比較結果)、kp_fix_01 inventory
14. Dangling Reference Check 9項目結果
15. Personalized News B1 FIX-01維持・AI Hiring A2新canonical参照の確認
16. 回帰テスト結果
17. commit 3 SHA、main=origin/main
18. 一覧外Read(理由1行)、check_delegation_prompt結果
19. Phase E向けSSOT追記文案(a)〜(d)
20. 未解決事項・注意点(Phase D seek環境要因の公開URLでの再判定結果を含む)
