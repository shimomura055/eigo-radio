# 委任_01b 逐語保存(Fable→sonnet-worker、2026-10-29、管理ID END-USER-LISTENING-PAGE-PROTOTYPE-01)

Fableからの委任_01b(管理ID: END-USER-LISTENING-PAGE-PROTOTYPE-01。Phase 2: 記事視聴ページ試作(DEV隔離、静的HTML/CSS/JS)。API 0、Production変更なし)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PROTOTYPE-01_委任_01b.md` に逐語保存してから開始。`tools/stop_scope_check_01.py --managed-id END-USER-LISTENING-PAGE-PROTOTYPE-01 --run-dir docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01 --out docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/stop_check_01b.json`(rc=3で停止)。

## 正本
ユーザー原文=`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PROTOTYPE-01_USER.md`(並行Workerが数分内に保存。着手後に全文読み§1・§3・§4・§5に従う)。要点: 旧 `user_test/articles_2026_0918.html`・`user_test/unified.html` の**シンプルさを継承**(全面リニューアル禁止)。視聴ページのみ(Top/一覧/会員は作らない)。スマホ重視+PC対応。組み込む: 記事タイトル・レベル表示/全体再生+パート別再生/再生・停止・シーク/スクリプト表示/KP・Wordの意味と解説(英語解説・日本語意味・音声・本文ハイライト=既存仕様どおり)/Grammar & Sentence Structure(対象レベルのみ、採用件数に応じ表示)/その他承認済み表示仕様(Preview・Comment・In One Line等、既存完成ページにあるもの)。学習仕様・音声は変更しない。1文単位の音声連動ハイライト(§4)は委任_02で統合するため、本試作では**文単位のDOM構造(各文に`data-sid`付きspan)と、`sentences.json`を読んでハイライトするJSのフック**を用意しておく(同期データは並行01aが `docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/` に生成中。無い間はダミーで動作確認)。

## やること
1. 並行01aが `docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/ARTICLE_PICK_01.md` に選定記事(Family X、Std/Adv)とasset一覧をcommitする(〜15分)。読めるまで旧unified/articles_2026_0918と最近の完成ページ(`user_test/family_x_ai_island_form_01/`、`user_test/paycheck_personality_e2e_02/`)の構造を読み、継承する要素(レイアウト・配色・操作)と組み込む要素の設計メモ `DESIGN_NOTE_01.md` を書く。選定記事が決まったらそのassetを使う(**音声・本文・解説のコピーは参照(相対パス/同一リポジトリURL)で済ませ、改変しない**。必要ならDEVディレクトリ内へコピーしsha記録)。
2. 試作 `user_test/dev_enduser_page_01/index.html`(+css/js、外部ライブラリなし、静的)。見出しに「DEV試作・正式公開ページではありません」を明記。Std/Adv切替、全体再生(通しmp3)とパート別再生(segment mp3)、シークバー、再生速度(既存にあれば)、スクリプト(文単位span)、KP/Word(既存ページと同じデータ・同じ内容を再利用)、文法コーナー(採用件数に応じ表示/0件非表示)、Preview/Comment等。スマホ(360〜430px幅)で親指操作しやすい再生コントロール(固定フッター等、過剰演出なし)。
3. 検証(Playwright、ローカル): PC(1280px)とスマホ(390×844、iPhone相当UA)で、表示崩れなし・全音声再生開始可・コントロール操作・console error 0・4xx 0。スクリーンショットを `docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/shots/` に保存(PC/スマホ各3枚程度)。
4. push後 live URL(`https://shimomura055.github.io/eigo-radio/user_test/dev_enduser_page_01/index.html`)のHTTP 200を確認。正式公開ページ・Productionコードは一切変更しない(`git diff --stat`で確認)。
5. `docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/PHASE2_PROTOTYPE_01.md`(構成・継承した要素・組み込んだ要素・未実装・既知の制約・検証結果)。ACTIVE_TASK(Q)行更新(Re-Read)。commit(DEVディレクトリ・docs・委任文のみ明示`git add`)→push。
6. `docs/pm/RESULT_PACKET_EUP1b.md`(整合/未承認機能/成果物と目的適合/判断候補/費用0/commit、`判定整合:`行)。最終回答は短く(URL・組み込み機能一覧・検証結果・commit)。

## 範囲(11-8)
範囲内=DEV試作の制作・検証・記録。範囲外=Productionコード/公開ページ/音声/学習コンテンツの変更、新機能の仕様追加(承認済み表示仕様に無いもの)、Top/一覧/会員、Family A/B/C。
