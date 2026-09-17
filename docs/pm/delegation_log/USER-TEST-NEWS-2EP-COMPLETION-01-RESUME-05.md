# 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`。前段RESUME-03 `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md`[既読扱い可])。現在main=`1cceb843`以降。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md`(新規)へ。

**並行タスクあり(衝突回避ルール)**: (a)`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`(AI Control A2是正→B1→音声→player→URL、`er014_output/user_test_news_2ep_01/ai_control/`配下+`build_web_player_common.py`利用+最後にDECISION_LOG編集・commit)、(b)`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`(er012 B-Family実装+音声生成+SSOT編集・commit)が実行中。ルール: (1)本タスクが触ってよいのは`er014_output/user_test_news_2ep_01/space_weapons/{a2,b1b}/web/`配下、`er014_output/user_test_news_2ep_01/build_web_player_common.py`(共通不具合の場合)、`user_test/unified.html`(低riskな既存plumbing修正に限る)、docs/pm配下の自タスクファイル、SSOT。`ai_control/`配下・er012・root `er0*.py`には触れない。(2)SSOT編集(PM_GOVERNANCE/OPEN_ITEMS/DECISION_LOG)は最後にまとめ、編集前に`git status --porcelain docs/pm/PM_GOVERNANCE.md DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待ち、超過時はSSOT編集をスキップして報告)。(3)commit前に`git fetch origin`→進んでいれば`git merge origin/main --no-edit`(rebase/force push禁止、競合時はSTOP)。明示add、全文Write禁止(Editで局所修正。player.htmlは生成物なので生成スクリプト経由の再生成は可)。(4)`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダ形式で上書き(他タスクの状態行を保持)。(5)TTS/Writer/Research等のAPI実行は禁止(本タスクはplayer plumbingのみ、API 0)。

## 性質/到達Status/禁止事項

- 性質: **最優先blocker**。ユーザー実試聴で「Space Weapons A2/B1のrawcdn unified.html URLはページ到達・再生ボタン表示までできるが、Playしても音声再生が始まらない(A2/B1同症状)」。原因をread/debugで特定し、既存player/unified plumbingの低riskな不具合で既存仕様から一意に修正可能なら**ユーザー確認なしで修正**し、実際にPlayで再生が始まることをruntime evidenceとして残したうえで新URLを再提示する。**Assembly/Gate PASSやHTTP 200/206だけで「ユーザー試聴可能」と判定してはならない。**
- 到達Status: Space Weapons=「技術的player再生確認済み/ユーザー試聴・品質確認待ち」まで。`USER_TEST_READY`最終確定・記事完成扱いにしない。
- STOP(修正せず原因と選択肢を整理して報告): UI/UX仕様変更が必要/player構造を大きく変える/他Familyへ広範な影響/新しい配信基盤が必要/GitHub Pages等の新インフラ導入が必要/セキュリティ・CORS制約で現行方式そのものが成立しない。闇雲に代替player方式を試さない。
- 禁止: API実行、`ai_control/`・er012・root moduleの変更、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wav/大容量のcommit。

## A. 原因特定(確認対象、すべて記録)

`user_test/unified.html`(fetch方式・`src`パラメータの解決・埋め込み方法[innerHTML/iframe/DOM移植]・audio要素の生成・イベントハンドラ・base URL解決)、埋め込み先`.../space_weapons/{a2,b1b}/web/player.html`(audio要素のsrc・relative path・`table.timeline`・seek JS)、`episode.mp3`(存在・サイズ・Content-Type・Range応答)、HTML/JS内のsrc参照とrelative path(player.html基準か、unified.html基準[`user_test/`]か)、rawcdn.githack.com経由のURL解決(commit SHA固定URL・`src`のquery parameter・リダイレクト)、browser autoplay/CORS/MIME/Range、raw.githubusercontent.com/rawcdn経路の差、consoleで起こりうるエラー。**Sheetで正常に再生できている既存記事**(例: `er011_output/household_unified_final_candidate_01/`のplayer.html+`web/episode_a2.mp3`、`build_player.py`生成物、または`er012_output/*/web/`配下の既存player)と、Space Weapons player.html(`build_web_player_common.py`生成)のaudio src指定・path形式・JS構造を**差分比較**し、相違点から原因を特定する。有力仮説(検証のこと): unified.htmlがplayer.htmlをfetchしてDOMへ注入する方式の場合、player.html内の相対audio src(例`episode.mp3`/`web/episode.mp3`)が`user_test/`基準に解決されて404になる。正常動作している既存playerが絶対URLまたはunified.html側で書き換えられる形式になっているかを確認。

## B. 修正方針

原因が既存plumbingの低risk不具合(相対path/URL解決/属性名/生成スクリプトの出力差)で既存仕様から一意に直せる場合は修正(共通不具合なら`build_web_player_common.py`を修正しSpace Weapons A2/B1 playerを再生成。unified.html側の修正が必要な場合は、既存記事のplayerを壊さない後方互換な最小修正に限り可。既存記事のURLで回帰しないことをA同様の手順で1件確認)。

## C. 修正後の受入(A2/B1それぞれ)

ページ表示/Playボタン操作/**実音声再生開始**/seek可能/音声全体再生可能/script表示/Key Phrase表示。**ブラウザ実操作または同等のE2E evidence**: `.venv\Scripts\python.exe -c "import playwright"`または`npx playwright --version`でPlaywright有無を確認。無ければ`.venv\Scripts\python.exe -m pip install playwright`+`.venv\Scripts\python.exe -m playwright install chromium`を実行してよい(dev tooling、Production非依存、repoへcommitしない)。Playwright(headless Chromium)で新URL(最終commit SHAのrawcdn URL)を開き、Play操作→`audio.currentTime`が進む/`audio.paused==false`/`audio.readyState>=3`/`audio.error==null`を一定時間後に確認、seek操作後の`currentTime`変化、`table.timeline`・Key Phrase・script要素の表示をDOMで確認し、結果JSONとスクリーンショットを`er014_output/user_test_news_2ep_01/space_weapons/{a2,b1b}/web/e2e_playback_evidence.json`/`.png`へ保存(commit可、png小サイズ)。console errorsも記録。Playwrightが導入できない場合は、unified.htmlのJSロジックを静的に追跡し、実際にブラウザが要求するaudio URLを導出→GET(Range)で206+`Content-Type: audio/mpeg`を確認し、「静的追跡による確認であり実操作ではない」と明記(その場合Statusは「技術的再生確認(静的)」とし、実操作確認は未達と報告)。修正前のURLでも同手順を実行し、不具合が再現する(currentTimeが進まない/エラー)ことを先に記録してから修正する(原因証跡)。

## D. 修正後のユーザー提示
最終commit SHAで新URL 2本(形式: `https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA>/user_test/unified.html?src=<PLAYER_PATH>&level=<A2|B1>&en=<URL_ENCODED_EN>&ja=<URL_ENCODED_JA>`)。CDN反映遅延時は60秒×最大5回待つ。

## SSOT記録(最後に)

- `docs/pm/PM_GOVERNANCE.md`: 9-1「ユーザー判断」欄および9-8の定義を更新(9-1の4「ユーザー判断」の直後または9-8末尾に「2026-09-17ユーザー再指示」として追記): 「ユーザー判断」欄は **A. 仕様・Product・実装判断待ち** と **B. ユーザー試聴・品質確認待ち(対象記事/音声/URL、何を確認してほしいか)** の2区分を必ず分けて記載し、どちらか一方でも存在する場合「ユーザー判断なし」と書かない(各区分が空なら「なし」)。開発段階では技術的完成(Assembly/Gate PASS、HTTP到達)でもユーザー試聴OK未取得なら「ユーザー判断あり(B)」として扱い、記事の最終OK扱いにしない。あわせて「HTTP 200/206・Gate PASSだけで『ユーザー試聴可能』と判定しない。Playで実再生が始まるE2E evidenceを要する」をGate 7 player要件の補足として追記(節番号を報告)。
- `OPEN_ITEMS.md`: 新規Open Item(OPEN-162想定、書式はOPEN-159〜161に合わせる): 「Fact/Ledger Checkerが厳格すぎることで、意味的に妥当な一般化・背景説明・概念整理・読者理解のための非事実的bridgeまで`unsupported_new_claim`/`changed_scope`として過剰に止める可能性(AI Control A2でsuperintelligence/intelligence explosion/singularityの概念名を含む一文がMAJOR停止した事例、2026-09-17)。優先度=低。期限=量産開始までに改善方針を検討・必要なら実装。改善観点=本当のFact逸脱・Ledgerにない新しい具体的主張と、意味的に妥当な一般化・背景説明・概念整理・非事実的bridgeをより適切に区別。今回Validator/Prompt/Gateは変更せず、AI Control完成をブロックしない」。Status=`OPEN / DEFERRED(量産開始前)`。
- `DECISION_LOG.md`: 本IDエントリ(ユーザー方針3点[報告欄定義修正/Checker厳格さOpen Item/player再生blocker]+原因+修正内容+E2E evidence+Status)。`CURRENT_SPEC.md`: 無変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read(unified.html/player.html/build_web_player_common.pyは全文Read可)。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録。T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果を1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧
- `user_test/unified.html`全文、`er014_output/user_test_news_2ep_01/space_weapons/a2/web/player.html`(audio/src/script部分)、`build_web_player_common.py`全文
- 正常動作例: `er011_output/household_unified_final_candidate_01/build_player.py`(audio src生成部)+生成player.html(Grep `<audio|src=|episode`)、`docs/pm/RESULT_PACKET_LEGACY_WEB_AUDIO_EXPORT.md`/`RESULT_PACKET_WEB_AUDIO_EXPORT.md`(web/episode.mp3配置規約)
- `docs/pm/PM_GOVERNANCE.md`: L689-730(9-1候補セクション)、L953-990(9-8)、Grep `Gate 7`→player要件行
- `OPEN_ITEMS.md` L304-308、`DECISION_LOG.md`: Grep `^## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03`
- `docs/pm/PM_BRIEF.md` L135-159

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME5.md`)
0. T-0 1. 原因(証跡付き: 実際にブラウザが要求したaudio URLと応答、正常例との差分) 2. 修正内容(ファイル・差分要旨、unified.html変更の有無と後方互換確認) 3. A2再生runtime evidence(修正前再現→修正後: currentTime進行/paused/readyState/error/seek/表示要素/console、evidence path、方法=Playwright実操作か静的追跡か) 4. B1同上 5. 新A2 URL 6. 新B1 URL 7. 既存記事playerの回帰確認(1件) 8. AI Control進捗(RESUME-04の`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md`が存在すれば要旨1行、無ければ「進行中」) 9. OPEN-162登録内容 10. PM_GOVERNANCE更新(節番号・行) 11. DECISION_LOG行 12. cost(API 0の証跡) 13. Git SHA/push 14. 現在Status(Space Weapons=技術的再生確認済み/ユーザー試聴・品質確認待ち) 15. 未決事項 16. 無変更証跡(`git status --porcelain er0*.py CURRENT_SPEC.md`が空)/事前指定外Read(理由付き)。ユーザー向け表記は「B1」に統一。
