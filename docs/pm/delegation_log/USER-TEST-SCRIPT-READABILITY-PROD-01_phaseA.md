## 管理ID

USER-TEST-SCRIPT-READABILITY-PROD-01 / Phase A(全3 Phaseの1つ目。Phase A=Production wrapper実装+translation asset規約+全20 levelのKey Phrase本文対応mapping+Personalized News既存翻訳の正式path移行+翻訳用source抽出。Phase B=残り18 levelの翻訳作成、Phase C=QA/E2E/Landing/TSV/SSOT/最終commit)。並行Agentなし(Fable確認済み)。音声stage(TTS/ASR/Ledger/Key Phrase生成)は一切実行しないためaudio_stage.lockは不要。`docs/pm/ACTIVE_TASK.md`を本委任内容の固定ヘッダ+要約で上書きしてから作業開始すること(固定ヘッダ書式は`docs/pm/PM_BRIEF.md` L157-172)。

## 性質/到達上限Status/禁止事項

- 性質: Production実装(ユーザー正式承認済み仕様の20 level展開)。前段Trial `USER-TEST-SCRIPT-READABILITY-TRIAL-01`はユーザー実物確認のうえ`APPROVED_FOR_PRODUCTION`(2026-09-18ユーザー承認、下記「ユーザー指示(原文)」参照)。
- Phase Aで到達してよい最大Status: `PHASE_A_DONE`(Production wrapper実装済み・mapping 20/20確定・未配線)。`PRODUCTION_WIRED`宣言はPhase C完了時のみ(Phase Aでは宣言しない)。Landing page(`user_test/articles_2026_0918.html`)とTSV(`docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`)はPhase Aでは変更しない。
- 禁止: canonical article本文・canonical player.html/index.html/user_test_simple.html・canonical audio・TTS・Key Phrase asset(`keywords_canonicalized.json`等)・Comment原文・タイトル・記事構成の変更禁止(sha256で無変更証明)。TTS/ASR/外部API呼び出し禁止(費用上限¥0。外部API支出が必要と判断した場合は実行せずSTOP)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。mp3/wav追加禁止。`user_test/trial/script_readability_01/`配下の変更禁止(履歴として残す)。Production wrapperからTrial path(`user_test/trial/...`)への参照・fallback禁止。
- STOP条件(該当時はそのKey Phrase/levelを`USER_DECISION_REQUIRED`として記録し、他の作業は継続して最後にまとめて報告。複数案を勝手に試さない): (1)Key Phraseの本文対応候補が2箇所以上あり一意に決められない、(2)活用差ではなく大きく言い換えられていて対応が不明、(3)Key Phrase asset自体が見つからない/表示中のKey Phrase一覧とassetが食い違う、(4)canonical scriptとKey Phrase assetの不整合、(5)article/level対応が不明、(6)wrapper共通化が安全にできない(player/audio側の変更が必要になる)、(7)新しいProduct仕様判断が必要。「ユーザー意図としてどちらか迷う」点は勝手に判断せず記録してSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseA.md`)

## ユーザー指示(原文)

ユーザー正式承認内容(USER-TEST-SCRIPT-READABILITY-PROD-01、2026-09-18):
1. Key Phrase該当箇所の本文ハイライト
2. Standard / Advancedともスクリプト下部に日本語訳を追加
3. Advancedは英語Commentも日本語訳する
4. Standardは既存日本語Commentを日本語訳セクション内で再掲する
5. Standard Comment再掲はグレー系で目立たなくする
6. Standard Comment再掲には「既存Comment再掲」であることが分かる表示を維持
7. Trialの黄色ハイライトは水色へ変更
8. Key Phraseは本文由来なので、本文中の対応箇所を必ず特定してハイライトする
9. 表層形が完全一致しなくても、活用形・時制・三単現・複数形等の差であれば対応箇所としてハイライトする
10. 無関係な類義語や意味の近い別表現まで勝手に広げない
11. 対応箇所の判断に迷う場合は、推測で実装せずユーザー判断を求める
12. その他Trial画面の仕様・レイアウトは承認済み

「Key Phraseが stay out of view で、本文が stays out of view なら、本文側のstays out of viewをハイライトする。Key Phrase自体がもともと本文から取られたPhraseなので、必ず本文に対応箇所がある前提。したがって、単純なexact matchだけで未ハイライトにする仕様は不採用。正式仕様は:『Key Phraseの元になった本文中の対応フレーズを特定し、その箇所をハイライトする』」

対応判定で許容する差(ユーザー指定): 三単現/過去形/過去分詞/現在分詞/単数・複数/be動詞の活用/助動詞・時制に伴う自然な形の変化/冠詞や軽微な機能語の差/大文字小文字/punctuation差/HTML entity・apostrophe等の表示差。「ただし、単なる文字列類似度だけで判断しない。重要なのは『この本文表現が、このKey Phraseを抽出した元の箇所である』と合理的に特定できること。」

禁止matching(ユーザー指定): 無関係な類義語/意味が近いだけの別Phrase/本文中の別の似た箇所を誤選択/edit distanceだけの機械判定/embedding similarityだけの自動決定/該当箇所不明なのに一番近い候補を勝手に採用。

水色仕様(ユーザー指定): 淡い水色、蛍光ペン程度、文字の可読性維持、リンクに見えない、選択状態に見えない、Standard/Advanced共通、PC/スマホで自然に折り返す。Trialレイアウトは維持し色のみ変更。

Production実装方針(ユーザー指定): Trial `user_test/trial/script_readability_01/unified_trial.html`をそのままProductionで参照しない。既存正式wrapper `user_test/unified.html`を基準にTrialでVALIDATEDされた表示仕様を実装する。変更は表示層・日本語訳asset・ハイライトのみ。translation assetは20 level共通で管理できる配置規約(例 `user_test/translations/<article_id>/<level>/translation_ja.json`)。Production側が`user_test/trial/...`を参照しない、Trial artifactへのfallbackも禁止。

## 事前指定Read一覧

1. `docs/pm/PM_BRIEF.md` L148-172(ACTIVE_TASK固定ヘッダ書式)
2. `docs/pm/PM_GOVERNANCE.md` L2049から18節末尾まで(Family横断共通化原則。Grep `^## 19\.` で終端特定)
3. `docs/pm/PM_GOVERNANCE.md` Gate 7(n)(Grep `Gate 7\(n\)` → 該当節全体、表示フォーマットルール: Key Phrase 2列・ラベル無し、Standard/Advanced表記、5点E2E)
4. `user_test/unified.html` 全文(構造変更対象のため全文Read可)
5. `user_test/trial/script_readability_01/unified_trial.html` 全文(移植元、読み取りのみ)
6. `user_test/trial/script_readability_01/personalized_news_a2/translation_ja.json` 全文、`.../personalized_news_a2/translation_qa.json` 全文、`.../personalized_news_b1/translation_ja.json` 全文、`.../personalized_news_b1/translation_qa.json` 全文(内容をProduction正式pathへ複製するため)
7. `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv` 全文(20 URLのsrc/level/en/jaの正)
8. `docs/pm/tools/user_test_page_e2e_check.py` 全文(既存5点checker。Phase Cで拡張する前提で構造把握)
9. `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_TRIAL_01.md` L42-48(共通化上の課題4点)
10. 各20 levelのcanonical player(TSVのsrc値のファイル、計19ファイル: Wake Before the AlarmはStandard/Advancedで同一src `player_std/index.html`)。各playerの script本文・Key Phrase一覧・Comment部分を把握するために必要範囲をRead(D-1: 巨大な場合はGrepで位置特定→範囲Read)。
11. 各levelのKey Phrase asset: playerと同ディレクトリ配下または親ディレクトリ配下を`Glob`で `**/keywords_canonicalized.json` 探索(Trial知見: A2は`key_phrases/`直下、B1は`b1b/key_phrases/`配下等、Familyで構成差あり)。見つからない場合はplayer HTML内のKey Phrase一覧DOMを正とし、asset不明としてRESULT_PACKETに記録(STOP条件(3)ではなく「asset未発見・DOM一覧を正とした」旨を記録。ただしDOM一覧すら無い場合はSTOP条件(3))。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `kp-hl|translation|trial` in `user_test/trial/script_readability_01/unified_trial.html` → Trialで追加したJS/CSSブロック位置を特定し、`user_test/unified.html`への移植範囲を決める。
- Grep `level|Standard|Advanced|rowData` in `user_test/unified.html` → 既存のlevel→Standard/Advanced表示・`rowData()`の`<br>`修正(commit 240e0723)を壊さない位置に追加する。
- Grep `Comment` in 各Standard player → 既存日本語Comment(再掲元)の位置とDOM構造を確認。
- Grep `Comment` in 各Advanced player → 英語Comment(翻訳元)の位置と件数を確認。
- Phase AではSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`)へ追記しない(Phase Cでまとめて実施)。

## 実行内容(設計要件、この順で)

### A-1. inventory(20 level)
`user_test/translations/index.json`を新規作成し、TSVの20 (src, level)ペアごとに以下を登録: `article_id`(snake_case、例 `young_travelers`/`wake_before_alarm`/`convenience_ai`/`tiny_bags`/`free_address`/`personalized_news`/`ai_hiring`/`home_robots`/`memory`/`digital_twins`)、`level`(A2/B1)、`src`(TSVのsrc値をURLデコードしたrepo相対path、完全一致で照合するキー)、`family`(News/Discovery/Voices/Future等、既存呼称に合わせる)、`player_sha256`、`key_phrase_asset_path`(相対path、未発見ならnull)、`comment_lang`(Standard=ja/Advanced=en、実物で確認。Standardなのに英語Comment、Advancedなのに日本語Commentの場合は記録してSTOP条件(7))。wrapperは(src, level)→article_idを`index.json`で解決する(src文字列のみに依存せず、Wake Before the Alarmのように同一srcで2 levelがある場合を正しく扱う)。

### A-2. translation asset規約
`user_test/translations/<article_id>/<level>/translation_ja.json`(Trialと同じschema: `level`/`article`/`note`/`sections[{section_id, heading_ja, source_en, text_ja, type: translation|reprint}]`)、同ディレクトリに`translation_qa.json`、`kp_mapping.json`、`source_sections.json`。Personalized News A2/B1については、Trialの`translation_ja.json`/`translation_qa.json`の**内容を複製**(ファイル参照ではなくコピー)して正式pathへ配置し、`note`を「Trial(USER-TEST-SCRIPT-READABILITY-TRIAL-01)でユーザー確認済み訳文をProduction pathへ複製」に更新。

### A-3. 翻訳用source抽出(Phase Bの入力)
残り18 levelについて、各playerから英語本文をsection単位で抽出し`source_sections.json`(`sections[{section_id, heading_en, structure_role(Hook/Story/Voice/Point/Tension/Closing/In One Line/Comment等、Familyの既存構造名), source_en, comment_lang, is_comment}]`)を作成。Standardの既存日本語Commentは`source_sections.json`に`is_comment=true, comment_lang=ja, text_ja_canonical=<DOMの日本語Comment原文そのまま>`として格納(Phase Bで再掲用に使う。翻訳しない)。Intro(「Welcome to English Your Way / Today's topic is ...」)とPreviewは翻訳対象外(TrialどおりFull Script本文のみ)。Familyごとの構造差は無理に同一化しない。

### A-4. Key Phrase本文対応mapping(20 level、本Phaseの中核)
各levelについて`kp_mapping.json`を作成: `key_phrases[{phrase(表示一覧と同一文字列), phrase_ja, matched_text(本文DOMに実際に現れる部分文字列そのまま), mapping_type(exact|inflection|tense|plural|function_word|case_punct|entity_apostrophe|UNRESOLVED), occurrences(本文中のmatched_text出現数), rationale(非exactの場合、なぜこの箇所が元Phraseと特定できるか1行), candidates(非exactで候補が複数あった場合は全候補列挙)}]`、`summary{total, mapped, exact, non_exact, unresolved}`。
ルール: (a)ハイライト対象のPhrase集合は、そのlevelページに表示されるKey Phrase一覧と**完全一致**させる(assetとDOMが食い違う場合はSTOP条件(3))。(b)exact(正規化: 大小文字・apostrophe種別・HTML entity・連続空白のみ吸収)が本文に1回以上あればexact採用、全出現をハイライト対象とする。(c)exactが0件なら、ユーザー許容差(活用形・時制・複数・機能語・be動詞等)の範囲でSonnetが**本文を読んで**元箇所を特定する。文字列類似度・edit distance・embeddingでの自動決定禁止。候補が1つに合理的に絞れる場合のみmatched_textを確定し`rationale`を書く。(d)候補が複数/大きな言い換え/不明の場合は`mapping_type=UNRESOLVED`、`candidates`に候補全部と迷う理由・推奨候補(あれば)を記録し、そのlevelを`USER_DECISION_REQUIRED`扱いとする(勝手に採用しない)。(e)mappingはオフラインで確定した`matched_text`をwrapperが決定論的に完全一致ハイライトする方式とし、wrapper runtimeにfuzzy matchingを実装しない。

### A-5. Production wrapper実装(`user_test/unified.html`)
Trialの表示仕様(ハイライト、日本語訳セクション、構造見出し、Standard Comment再掲のグレー表示+ラベル「既存Comment(再掲、翻訳ではありません)」、Advanced Comment訳)を`user_test/unified.html`へ移植。変更点: ハイライト色を水色(例 `background: #dff2fb` 前後の淡い水色、文字色変更なし、下線なし、`border-radius`小)。asset解決は`user_test/translations/index.json`→`<article_id>/<level>/`。Trial path参照・fallback禁止。`trial=`パラメータは使用しない(Production URLは`src/level/en/ja`のみ)。translation/mapping assetが無い(src,level)の場合は既存表示のまま(エラー表示なし、console.warnのみ)。既存機能(Play/Seek/Key Phrase 2列・ラベル無し/Standard・Advanced表記/`rowData()`の`<br>`処理)を壊さない。Trial機能と同様にtry/catchで分離。

### A-6. runtime確認(Phase A範囲)
Personalized News A2/B1(翻訳asset有り)についてローカルhttpサーバ(例 `.venv\Scripts\python.exe -m http.server 8765` をrepo rootで起動)+Playwright headless Chromiumで、`http://localhost:8765/user_test/unified.html?src=...&level=...&en=...&ja=...`を開き、(1)水色ハイライト要素数=mapping summary.mapped(A2は5/5、`stays out of view`を含む)、(2)日本語訳セクション存在、(3)Standard Comment再掲4件のグレーcomputed style、(4)Advanced Comment訳4件、(5)Key Phrase一覧2列・ラベル無し、(6)横スクロールなし、(7)Play進行・Seek、(8)JS errorなし、を機械確認しscreenshot(PC 1280×800/mobile 390×844)を`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/`へ保存。さらに残り18 levelについて、翻訳asset無しでも既存表示が壊れないこと(regression)と、`kp_mapping.json`のmatched_textが本文DOMに実在すること(mapped件数=DOM上のヒット数)を機械確認(`kp_mapping_dom_check.json`)。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseA.md --json-out docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseA.md_check.json`
- 開始時/終了時のcanonical無変更証明: `.venv\Scripts\python.exe -c "import hashlib,pathlib,json,sys; ..."` の形で、TSV 20 srcのplayerファイルとその同階層ディレクトリ配下全ファイル(mp3含む)+`user_test/articles_2026_0918.html`+TSVのsha256一覧を`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/sha256_before.json`/`sha256_after.json`へ出力し、diffゼロを確認(スクリプトは`docs/pm/tools/sha256_snapshot.py`として保存し、Phase Cでも再利用する。引数: `--paths-from docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv --extra user_test/articles_2026_0918.html --out <path>`のように実値で実装)。
- ローカルサーバ: `Start-Process -NoNewWindow .venv\Scripts\python.exe -ArgumentList "-m","http.server","8765"`(作業終了時に停止)。
- Playwright: `.venv\Scripts\python.exe docs\pm\tools\user_test_readability_check.py --base http://localhost:8765 --tsv docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --translations user_test\translations --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_a\e2e_result.json --screenshots docs\pm\closeout_136_e2e\script_readability_prod_01\phase_a`(新規checker。既存`user_test_page_e2e_check.py`の5点に加え、ハイライト数/翻訳section数/Comment再掲・訳件数/JS error/横スクロール/Play/Seekを判定。`--base`をrawcdn URLに差し替えればPhase Cの公開後確認にも使える設計にする)。
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test_*.py"`(既存テストへの影響確認、unified.html変更のみなので影響なし想定だが1回実行)。

## SSOT追記文

Phase AではSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`)へ追記しない(Phase Cでまとめて実施)。ただし`docs/pm/ACTIVE_TASK.md`(固定ヘッダ+Phase A要約)と`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`(新規、`## Phase A`節)は更新する。

## Git(明示add対象・コミットメッセージ・trailer)

作業完了・runtime確認PASS後に1 commit(push前に`git fetch origin`で衝突確認、push後`git fetch origin`でmain=origin/main確認):
- 明示add: `user_test/unified.html`、`user_test/translations/index.json`、`user_test/translations/**/translation_ja.json`、`**/translation_qa.json`、`**/kp_mapping.json`、`**/source_sections.json`、`docs/pm/tools/sha256_snapshot.py`、`docs/pm/tools/user_test_readability_check.py`、`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/*.json`、`*.png`、`docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseA.md`(+`_check.json`)、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`、`docs/pm/ACTIVE_TASK.md`。
- コミットメッセージ: `USER-TEST-SCRIPT-READABILITY-PROD-01 Phase A: Production wrapper(水色highlight+日本語訳)+translation asset規約+20 level KP mapping+PN訳文移行(Landing/TSV未更新・未配線)`
- trailer: `Task-ID: USER-TEST-SCRIPT-READABILITY-PROD-01`
- Landing page/TSV/SSOTはこのcommitに含めない。mp3/wavは含めない(`git status --porcelain`で確認)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`の`## Phase A`節に以下を記載:
1. Phase A Status(`PHASE_A_DONE` / `USER_DECISION_REQUIRED`(該当KP/levelあり))
2. index.json 20 level一覧表(article_id/level/family/src/key_phrase_asset_path/comment_lang)
3. Key Phrase asset未発見・DOM一覧を正としたlevel(あれば)
4. mapping集計: 20 levelの総KP数/mapped/exact/non_exact/UNRESOLVED
5. 非exact対応の全件一覧(article/level/phrase/matched_text/mapping_type/rationale)
6. UNRESOLVED全件(article/level/phrase/候補本文/迷う理由/推奨候補と理由)——0件なら「なし」
7. Standard Comment言語・Advanced Comment言語の実物確認結果(想定外があれば記載)
8. source_sections.json作成結果(18 level、各section数・Comment数)
9. wrapper実装の変更概要(unified.html差分行数、水色の実値、asset解決方式、Trial path参照なしの確認方法)
10. Personalized News A2/B1 runtime確認結果(8項目)+screenshot path
11. 残り18 levelのregression確認(既存表示無変更)とkp_mapping DOM実在確認結果
12. canonical無変更証拠(sha256 before/after diff 0)
13. 回帰テスト結果
14. Git commit SHA、main=origin/main確認
15. 一覧外Read(あれば理由1行)、check_delegation_prompt結果
16. Phase Bへの引き継ぎ事項(翻訳対象18 levelのsource_sections.json path一覧、注意点)
