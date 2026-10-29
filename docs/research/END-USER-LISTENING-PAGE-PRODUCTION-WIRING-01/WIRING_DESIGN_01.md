# WIRING_DESIGN_01(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_01、2026-10-29。設計のみ・コード実装なし・API 0。Opus条件Aレビュー待ち)

前提: ユーザー正式採用(APPROVED_FOR_PRODUCTION)済みのため11-7限定例外(flag隔離)は使わず、承認済み仕様として直接配線する。ただし**配線完了(PRODUCTION_WIRED)までは未配線**と表記する。根拠=`CURRENT_STATE_01.md`(以下CS)、原文=`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01_USER.md`(以下U)。

## 1. 全体構成(最小変更)
```
[既存] pages stage(X: er019_family_x_listening_page_01.build_page / Y: stage_pages / Z: stage_pages)
          -> 開発者向け <pages_dir>/index.html (+audio) ... 不変・同一データ源
[新規] er135_enduser_page_01.build_enduser(pages_dir, family, ...)   (同一stage内の末尾で1回呼ぶ)
          -> <pages_dir>/enduser/index.html, app.js, style.css, data/article.json, data/sync_std.json, data/sync_adv.json, build_info.json
[新規] verify: stage_page_verify(Y/Z) / X は build_page内の構造検査 + 共通verify CLI(Playwright)
```
- 新規共通モジュール**`er135_enduser_page_01.py`**(Production code・flagなし)。内部=(a)アダプタ `extract_article()`、(b)同期 `build_sync()`、(c)訳 `attach_translations()`、(d)validator `validate()`、(e)出力 `write_enduser_dir()`、(f)整合検査 `verify_consistency()`。CLI(`--pages-dir --family [x|y|z] [--ja-manuscript] [--verify-only]`)も持ち、公開済みdirへの後付け生成・再生成を同一コードで行う(手作業ゼロ化・backfill兼用)。
- 共通asset `enduser_page_assets/rev01-e/{index.html,app.js,style.css}`: DEV rev01-eの**機械的派生**(CS §A末尾の除去リストのみ)。DEV本体`user_test/dev_enduser_page_01`は不変(参照実装として残置)。派生差分が許可リスト内であることをtestで固定(動作差の担保)。
- **新stage名は追加しない**: Y/Zの`stage_pages`末尾とX `build_page`末尾に呼出し1行、`stage_page_verify`末尾に検証呼出し1行。理由=Z完成段`--stages provision_shell,gate,assemble,pages,page_verify`の1起動運用とRESTART_STORM回避(CS §B-3)を壊さない。`pages`を走らせれば自動で両ページ、という「追加の手作業なし」(U§10)を満たす。

## 2. フック位置(runner変更は各3-4行、競合回避)
| Family | pages生成フック | 検証フック | 備考 |
|---|---|---|---|
| X | `er019_family_x_listening_page_01.py` `build_page`の`index.html`書出し直後(CS §B-1。:245-246) | 同関数内のvalidate+共通verify CLI | X runnerにpages stageは無い。公式入口=この関数のためここが唯一の接続点 |
| Y | `er121_family_y_runner_01.py` `stage_pages`末尾(:1346付近)。**audience==publicのみ**(devは`index_dev.html`でenduser対象外) | `stage_page_verify`(:1415)末尾 | HR選定フローWorkerが同ファイルを編集中→hookはそのWorkerのcommit後に最小hunkで入れる |
| Z | `er026_family_z_fiction_production_runner_01.py` `stage_pages`の`build_pages`戻り直後(:2684付近) | `stage_page_verify`(:2743)末尾 | 藪の中Workerのrun中。runner変更は後回し、er135本体・test・assetを先行 |
- 競合回避: `er135_*`新規file・asset・test・verify CLIは既存fileを触らない(並列開始可)。runner hookは3 file各1 hunk、`git fetch`→Re-Read→その1 hunkだけEdit→`git diff`でhunk以外が混ざらないことを確認→自分のfileのみ`git add`。他Workerの未commit差分がある間はhook着手を待つ(待機上限は既存規則)。

## 3. 出力先・URL(比較表)
| 案 | URL | 長所 | 短所 |
|---|---|---|---|
| **A(推奨)** `<既存dir>/enduser/index.html` | `…/user_test/<dir>/enduser/index.html` | 既存dev URLと互換(dev不変)。audioは`../`の既存mp3を参照=**mp3の複製0**。1回のcopy/pushで両ページ。dir単位で整合 | Y/Zのpages_dirを公開dirへcopyする手順に`enduser/`を含める必要(dangling riskとして手順化)。dev dirの削除でEndUserも消える(依存は意図通り) |
| B 兄弟dir `<dir>_enduser/` | `…/user_test/<dir>_enduser/` | dev dirに触れない | audioを相対参照(DEV同様`../<dir>/audio`)=2dirが整合しないと音声欠落。公開手順が2dir。両URLの対応が名前規約依存 |
| C 同一index.htmlにquery(`?view=enduser`) | 同一URL | URL1本 | dev pageの改変が必須=「不変」違反。不採用 |
→A推奨。理由=変更範囲が最小・音声重複0・既存URL不変(U§4)。**最終は Fableが決める**。

## 4. データアダプタ(最終dev HTML→End User JSON)
入力: `<pages_dir>/index.html`(書出し済み最終版)+family別補助(X: `ja_writer`手原稿path)。**dev HTML自体が本文=音声=表示の四者一致検査済みの最終成果物**なので、End Userはそこから読むだけ(別データ源を作らない=二重管理・不整合なし。LR/Fallback overlay、strip_trailing_delim、ニュアンス採否、文法0件を自動継承)。
- 抽出: h2 id(std|adv|standard|advanced)を`std/adv`に正規化→`<tr><td><b>label`行を順に(data-t、`<audio src>`、`div.script`群、`ul.lk-meaning`、KP表、`details>div.ja`)→`section.study`(h3 = Vocabulary & Expressions / Grammar & Sentence Structure / ニュアンス解説 を**見出し文字列で厳密判定**。新規はニュアンス解説を追加。h3が未知ならSTOP)。
- kind分類(label正規表現。Family別profile): X=DEV既存、Y=`Full Story: *`→story(Lead/Voice N Introduction/Voice N/Closing)・Comment・Preview・Topic intro・Japanese title・KP・定型(Intro/Welcome/Notification/Preview intro/Key phrases intro/Full story intro/Outro)、Z=`Full Story Part N (…)`→story。未知labelはSTOP(黙って捨てない)。
- 文単位: 1行内の`div.script`が複数(Z)なら各divを独立単位に、単一divなら段落(空行)単位に、HTML対応の決定論分割(DEV `split_sentences`/`find_cuts`、build_data_01.py:62-96を移植。引用符閉じ・略語・小文字継続を考慮。日本語は。！？)。sidは`<lv>_<行idx>-s<連番>`。
- **除去(開発者向け専用要素)**: 制作情報/aux/#pww/#production、⏸(chunk-mark)、LR赤/Fallback青(`rpt-*`)、凡例、`note`(Y注記を除く)、audience marker。除去後に残存0をvalidatorで確認(CURRENT_SPEC:3203のエンドユーザー非表示要件)。本文テキストは書換えない。
- Y「Voice説明文」: dev HTMLにPAGE_NOTICE_CLASSの注記がある場合のみ、`er121_family_y_structure_01.PAGE_NOTICE_JA`と**文言一致**でEndUserページ冒頭(hero直下)へ複写。dev側にある⇔EndUser側にある、をvalidatorで検査(判断候補3)。
- KP: 各KP clip(`kp`行)の英語区間=silencedetect -40dB d=0.2 の「2番目の発話ブロック」(DEV方式、ブロック数>=4)。**ASR(同モデル)で当該区間を転写しKP表現とトークン一致を確認**し、不一致はSTOP(Z Adv KP2の5ブロックの実測を踏まえDEVの`==4`は採らない。CS §D-3)。
- glossary(覚えておきたい表現): DEV build_rev_01.py:104-154の規則を移植。display_spec付きlevel(本文にlk1/lk2/lk3 spanあり)でのみ生成し、**assert(全KP/全Vocabが載る・重複なし)はdisplay_spec付きlevelでは必須(違反=STOP)、無しlevel(旧run)ではglossary自体を出さない**(「適用対象外」をbuild_infoに記録し黙ったskipにしない)。
- 出力JSON `enduser_article_v1`: DEVのschemaからplaceholder/`*_source`/dev系field・`audio_base`固定を除き、`build_info`(後述)を追加。

## 5. 日本語訳(承認済みデータのみ)
- X: story行にのみ`ja_writer/revision2.md`(無ければrevision1、original。`derive_japanese_title`と同じ優先順)の段落を、story行の段落数に従って順に割当(先頭=日本語タイトル行は除外)。**段落総数不一致=STOP**(`ENDUSER_JA_PARAGRAPH_MISMATCH`。DEVのassertと同じ。承認済み2成果物の不整合は黙って落とさない)。ja manuscriptファイル自体が存在しない旧run=訳なし(非表示)、`translation_coverage`に記録。`ja_source=approved_ja_manuscript`+sha256を保持。
- Y: dev HTMLの`details>div.ja`(承認済み日本語原稿の該当segment)を採用。`ja_source=approved_ja_original_in_dev_page`。
- Z: 承認済み訳なし→訳ブロックを出さない。
- Comment/In One Line/Preview/Topic intro(英語): 承認済み訳なし→**非表示**。DEV_TR・機械翻訳・LLM訳を一切持たない。validatorは`ja_source`が上記2値以外ならSTOP。
- 新翻訳仕様(判断候補2、未採用): 上記非表示の英語ブロックを訳す工程を新設する場合は、既存T1訳(CURRENT_SPEC:2100)と同型の独立1 call/level(SUPPORT_MODEL gpt-6-luna)案。概算 X/Y Adv: Comment+In One Line 約250語/level=約¥0.1-0.3/level、Z全Part約700-900語/level=約¥0.3-1/level(いずれも**未実測の概算**)。1記事Std+Adv約¥0.5-2(70円/セットの0.7-3%)。訳品質の承認基準(ユーザー定義)が要るため現時点では提案のみ。
- `build_info.translation_coverage`: 種別(story/comment/oneline…)ごとの{blocks, translated, source}を記録し、完成報告に「訳なしの種別」を転記できるようにする(U§3「必要な訳が無い場合は承認済み仕様の範囲で解決」)。

## 6. 音声同期(faster-whisperをローカル正式stage化・API 0)
### 6-1 方式(DEV rev01-eと同一モデル・設定、整列対象のみ簡素化)
- ASR: faster-whisper **medium・int8・CPU・word_timestamps・beam_size=5・condition_on_previous_text=False・vad_filter=False**(DEVと同一、T/asr_raw_01.py:22-25)。日本語行は`language=ja`、他はen(DEV通り)。対象=各行の**既存segment mp3**(新規音声生成なし)。
- 整列: DEVは「TTS入力台本を分割→ASR整列→dev表示文へ二段目の文字整列(split 8/155)」の2層(build_sync_index_02.py)。Productionは**dev表示文を直接ASR語列へ整列**(同じ`align`/`fill_gaps`/無音スナップ=T/sync_build_01.py:60-196を移植)に簡素化。理由=X専用の`tts_generation_results.json`/`chunk_plan`/`chunk_tts_assembly`に依存しないためY/Zでも成立し、二段整列由来のsplit 8/155が消える。
- **DEVとの動作差の担保**: 同じ3記事(AI島Std/Adv・月Adv、151文)で(a)直接整列の境界とDEV最終sync(sync_*.json)の差の分布(中央値/最大)、(b)DEV検証指標(単調・Chunk既知ギャップ16件・無音スナップ不能0)を再計算し、DEV並みを回帰基準にする(TEST_PLAN T-SYNC-REG)。基準未達なら二層方式の移植に切替(設計内の逃げ道、ユーザー判断不要)。
- 時刻: 各行の`data-t`(episode開始)+segment内秒。`episode_offset_check`(segmentが全編mp3内`data-t`位置に一致、1秒窓の相互相関ずれ<=0.05s、DEVは0.000s/相関>=0.998)を全行で実施。
- キャッシュ: `<run>/enduser_sync_cache/<mp3 sha256>_<model>_<params>.json`(ASR生出力)。**segment mp3の内容が不変なら再ASR 0**(resume/再実行時は変更segmentのみ再計算。T/PRODUCTION_IMPACT_01.md §3)。キャッシュは公開dirに置かない。

### 6-2 失敗時の扱い(未承認仕様を追加しない)
- 同期に失敗/不合格(下記ゲート違反、ASR例外、モデル不在)=**`EnduserPageStop`でenduser生成を停止**: dev `index.html`は既に確定済みで不変、`enduser/`は書かない(部分生成なし。X builderの『落ちたらindex.htmlを書かない』、Y/Zの`*E2EStop`と同じ既存fail-closed規約。CS §D-4)。完成報告では**End User URLを提出せず**原因付きで報告(再実行/修正はFable・Worker)。
- 『ハイライトなしでEnd Userページを公開する』縮退は**実装しない**(DEV試作の前提だったが、公開可否の新トレードオフ=判断候補1。承認が出るまで作らない)。
- ゲート(構造不変条件=ハード): (1)各行で`0<=start<end<=音声長`、文間単調・重なりなし (2)全sidが時刻を持つ(欠落/unmatchedなし) (3)行ごとトークン一致率>=閾値T (4)episode_offset_check合格 (5)全編音声長とtimeline合計差<=0.15s(DEV実測の許容)。閾値T=DEV実測最小96%を踏まえ**初期値0.90**とし、Phase-0(Y/Z実測)で確定。低信頼度境界(短ポーズ/広窓スナップ)は**警告として記録のみ**(DEV同様。件数をbuild_infoへ)。閾値は『DEV検証済み範囲を超えるものを通さない』ための工学的受入基準であり、緩和する場合はユーザー判断(自動緩和なし)。

## 7. validator(DEV仮データ・未承認データの混入検出。`validate()`、生成の最終ゲート)
1. JSON/HTML内に禁止語0: `placeholder_for_layout_check`・`dev_translation_unapproved`・`DEV訳`・`仮データ`・`未承認`・`[DEV]`・`phnote`・`=====`・`⏸`・`chunk-mark`・`rpt-`・`sha256`(表示文として)・`Traceback`・`confirmation_id`・run/絶対path。
2. `ja_source`∈{approved_ja_manuscript, approved_ja_original_in_dev_page}のみ。`*_source`系field/`placeholder`系fieldの存在自体を禁止(schema拒否)。
3. 学習コーナー: SELECTED/ADOPTED由来のみ。文法・ニュアンスが0件/不採用のlevelは`levels[lv].grammar`/`nuance`キー自体が空→UI非表示。dev HTMLの`section.study`数と一致(ニュアンス解説h3は最大1、`count_empty_study_sections`相当=0)。
4. 本文一致: End User各文の連結テキスト==dev HTMLの当該行`div.script`プレーンテキスト(正規化後バイト一致)。太字(`<b>/<strong>`の対象語)の有無も一致。
5. 音声一致: JSON内の全audio参照がdev dirの実在mp3を指し、sha256がbuild_infoと一致(音声欠落0)。
6. Y注記⇔dev注記一致、KP数・Vocab数・語順がdev HTMLと一致。
7. 負例fixtureを注入するtestで各ルールが実際にSTOPすることを確認(TEST_PLAN T-VAL-NEG)。

## 8. retry / fallback / regeneration / resume との整合
| イベント | 既存の挙動 | End Userの挙動 |
|---|---|---|
| pages再実行(Y/Z `--stages …pages,page_verify`、X listening page再実行) | dev pageを上書き(API 0) | 同一stage内で再生成。`build_info`のdev index.html sha・全mp3 shaが一致するsegmentは同期キャッシュ再利用(ASR 0) |
| Local Rewrite / Fallback / TTS再生成でsegment mp3が変わる | assemble→pages再実行(既存運用) | 当該segmentのみ再ASR。他segmentはキャッシュ。LR後英文はdev表示本文に反映済み→End Userも自動追従 |
| 本文/学習テキスト(KP・文法・ニュアンス)が確定し直る | pages入口の確定確認(_assert_*)がrc=4/STOP | pagesが通った後にだけenduser生成。確定待ち中は何も出さない |
| 失敗・STOP(`EnduserPageStop`) | - | dev pageは残る、`enduser/`は書かない(古いenduser/が残る場合は**削除**=古い不整合ページを公開しない) |
| resume / RESTART_STORM | 起動回数を計上 | 新stageなし=起動回数は増えない。ASR時間(medium約4分/セット)で`pages`が長くなる点のみ |
| 公開copy後にdev pageだけ更新 | - | `verify_consistency`(dev index.html shaとbuild_info照合)でstale検出→page_verify/公開前チェックで落とす |
| TTS/本文/解説の再生成 | - | **End User生成のために再生成することは一切ない**(U§4) |

## 9. 検証(取得するruntime evidence)
- 構造検証=`validate()`+`verify_consistency()`(上記)。ブラウザ検証=DEV `verify_rev_e_01.py`(T/tools、Playwright)を**記事/パラメータ化した共通CLI** `er135_enduser_page_verify_01.py`として継承: 342チェック相当(1文ハイライト追従・文クリック再生・シーク・パート間連続再生・停止/再開・KP英語のみ・太字共存・学習コーナー色/順序・console error/HTTP 4xx/リンク切れ/音声欠落0・PC/390x844スマホ)+DEV既存`verify_rev_d_01`系の全継承。local(http)+live(GitHub Pages)。
- 実機iOS Safari/Android Chrome: 本環境では実施不可。Playwright Chromium(モバイルemulation)と(インストール済みなら)WebKit(Safariエンジン近似)で**模擬**と明記し、実機は「未実施・ユーザーまたは実機手順(`MOBILE_CHECK_STEPS`)で確認」として報告(実機検証済みとは書かない)。
- Regression: 開発者向けページのバイト不変(hook前後でindex.htmlとaudio全mp3のsha256一致)、既存test集合(er120_nuance_display/er128_nuance_hr/er121 runner/er026 runner/er019 page系)が旧失敗集合(OPEN-588)と同一。
- 6組合せ: X/Y/Z × Std/Adv を **既存完成記事のpages再実行**(TTS・本文・解説の再生成0・API 0)で: X=月reselect(公開済 88df63bb0。ニュアンス=NXW02C `x/nxm1,nxm2` copy-run)、Y=再配達料fee_03+NXW02C `y/nxw_y1,y2`、Z=melos_02+NXW02C `z/nxz2,nxz3,nxz4`。藪の中(in_a_grove)は別Workerが修正中のため触れない。evidence出力は`C:\Users\tensh\eigo-radio-evidence\ENDUSER-WIRING\`(repo外)+公開3記事は**既存dirへ`enduser/`を追加するのみ**(既存ファイル0変更、判断候補4)。
- 量産単価増分の計測: `build_info.cost`={api_calls:0, asr_wall_s, build_wall_s, cached_segments, model}。pages stage前後で`cost_log`/usage logの行数・合計円が不変であることをtestで検査。増分=0円/セット(CPU時間のみ、small約85秒・medium約4分/セット、T/PRODUCTION_IMPACT_01.md)。

## 10. 作業分割(並列)と見込み
| WP | 内容 | 依存 | 見込み(Sonnet作業) |
|---|---|---|---|
| WP-A | asset派生(app.js/style.css/index.html: 除去リスト適用、data path汎用化、動作差test) | なし | 半日 |
| WP-B | アダプタ+訳+validator+unit test(既存完成3記事+負例fixture) | なし | 1日 |
| WP-C | 同期module(移植+直接整列)+DEV回帰(T-SYNC-REG)+**Phase-0: Y/Z実音声の同期品質実測(ローカル・API 0、各数分)** | なし。Phase-0結果でT確定 | 1日 |
| WP-D | 共通verify CLI(DEV verify継承)+consistency check | A,B,Cの出力形式(固定済み) | 半日 |
| WP-E | runner hook(X/Y/Z)+copy-run/公開3記事のruntime evidence+live検証 | A-D、HR/藪の中Workerのcommit | 1日 |
| WP-F | SSOT(CURRENT_SPEC新節・DECISION_LOG・OPEN-597・OPEN-590)、PM完成報告テンプレ(両URL欄)、sonnet-worker/sandwich-pm受入基準、公開手順(enduser含むcopy) | E | 半日 |
- 並列: A/B/C は同時着手可(別file)。クリティカルパス=C(Phase-0実測)→E。A-Dは約1日で並走、E-Fで約1.5日。直列理由=hookは他Workerの未commit差分解消待ち(競合file)、evidenceは全WP完了後。

## 11. 判断候補(Fable仕分け用。A既判断/B承認範囲内で自己解決/C現タスクと独立/D真に新しい判断 の自己評価付き)
| # | 内容 | 根拠(file:line) | 自己評価 | 推奨 |
|---|---|---|---|---|
| 1 | **同期データ生成失敗時の扱い** | 承認済み記述なし(CS §D-4。T/PRODUCTION_IMPACT_01.md:20「仕様判断(ユーザー)」)。既存stageは fail-closed(`er019_family_x_listening_page_01.py:5-9,245`、Y `er121…:1415-1431`、Z `er026…:2743-2788`)。U§6「既存承認仕様で処理可能ならそれに従い、公開可否など新たな品質トレードオフが必要ならユーザー判断」 | 『失敗でenduser生成をSTOP(再実行/修正)』=**B**(既存fail-closed準拠・新トレードオフなし)。『ハイライトなしでEnd Userページを公開』=**D**(公開可否のトレードオフ)で**未実装** | 本設計はBのみ実装。D案は実際に特定記事で解消不能になった時点でUDR化(今は不要) |
| 2 | 訳が無い英語ブロック(Comment/In One Line/Preview/Topic intro、Z全Part)の訳 | 承認済み訳なし(CS §C-2)。U§3「未承認の翻訳方式を独断で導入しない」 | 現行は『非表示』で完遂可能=**B**。訳工程の新設は**D**(新仕様+訳品質基準)で任意の将来提案 | 非表示で完了。D案は費用概算付きで提案のみ(WD §5)。ユーザー判断は不要(完了を止めない) |
| 3 | Family Y「Voice説明文」をEnd Userページにも表示 | CURRENT_SPEC:3202(正式文言・Family Y共通・将来アプリ表示も同一文言)・3206(適用条件)、`er121_family_y_structure_01.py:110` | **B**(承認済み仕様の継続適用。置き場所=hero直下はdev pageの冒頭位置を踏襲) | 実装する。表示位置のみFable確認 |
| 4 | 既存公開3記事(X月・Y再配達料・Z走れメロス)へ`enduser/`をadditive追加して両URLのlive evidenceを取る | U§7・§10(正式Productionで生成した両URL)。dev既存ファイル0変更をsha一致で確認 | **B**(Git公開操作を含むためFable許可確認推奨) | 実施。許可がなければ公開前のcopy-run+ローカルevidenceに限定し、liveはE段の新規記事で取得 |
| 5 | 同期ゲート閾値T(トークン一致率) | DEV実測最小96%(T/SYNC_METHOD_01.md「token match 96-100%」)。U§6 | **B**(DEV検証済み範囲を超えて通さない工学基準。緩和はUDR) | 初期0.90、Phase-0で確定しWD追記 |
| 6 | ASRモデル medium(DEV同一) vs small | DEV: medium/small最終境界差0.00s・small約85秒 vs medium約4分(T/PRODUCTION_IMPACT_01.md §1、T/SYNC_METHOD_01.md:36) | **B**(Charter2速度 vs 同一性。Y/Z未検証) | 初回はmedium(DEV同一)。Phase-0でY/Zもmedium=small同一ならsmallへ切替提案 |
| 7 | DEV URL(`user_test/dev_enduser_page_01`)の残置/廃止 | OPEN-590 | **C** | 残置(参照実装・動作差test基準)。廃止は別判断 |
| 8 | X pagesはrunner stageでなくlisting page builderにhook | CS §B-1 | **B** | `build_page`末尾にhook。X runner stage新設は不要 |
- ユーザー判断が必須となりうる(D)のは、現時点で**なし**。1のD案・2のD案は『今は不要・将来任意』。

## 12. Opus条件Aレビューで見てほしい点
1. 「最終dev HTMLをスクレイピングして単一アダプタ」vs「各builderの中間構造(levels/rows)を直接受ける」の脆さ比較(HTML形式変更への耐性、Y/Z初適用の妥当性)。
2. 同期整列を「dev表示文へ直接」にした簡素化の妥当性と動作差担保(T-SYNC-REG)、ゲート閾値と失敗時STOP方針の妥当性。
3. pages/page_verify内へ内包(新stage名なし)した場合の失敗波及(enduser失敗でpages stageが失敗扱いになり後続が走らない)と代替(devページ保持+rc区別)。
4. Zの話者別複数div・引用符跨ぎ文、Yの短ポーズ(Chunk pad無し)への同期適用リスク。
5. validator禁止語・schema拒否の抜け(DEV仮データ混入防止)。
6. 公開copy手順での`enduser/`漏れ、完成報告テンプレへの両URL欄追加の確実性。

## 13. 既知の未確認・リスク
- Y/Z実音声での文単位同期品質は未測定(Phase-0で実測)。Yは文間ポーズが短い可能性(T/PRODUCTION_IMPACT_01.md §4)。
- 実機iOS/Android未確認(模擬のみ)。聴感照合(ユーザー評価)はDEV同様未実施。
- Y/Zの学習解説・ニュアンス・glossaryのEnd User表示は未試験(Xのみ342チェック)。
- 旧run(display_spec無し)ではglossary/本文意味が出ない(適用対象外として記録)。
- HR選定フロー/藪の中Workerのrunner未commit差分が解消するまでhook着手不可。
