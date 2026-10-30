# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 DESIGN_01(設計・実装計画、2026-10-30。実装前。Fable確認+Opus条件Aレビュー後に着手)
調査=CURRENT_STATE_01.md。API 0。

## 0. 解釈の確定(原文との照合)
- 「フレーズ・単語を合計ちょうど3件必須」=**区分①(Key Phrase)の件数**を「最大3→ちょうど3」に変更(原文§4「現在、最大3件として扱われている」=LIMITS[0]=3のみが該当、§2「①の既存選定数は変更しない」と整合)。②(<=2)・③は不変。kp_confirmed記事は固定3件でPASS。
- 「残りをすべて選択」=現在未選択の提示候補を**③(本文意味表示)へ**まとめて割当(②は<=2のため追加不可、①は3固定)。累積<=12は候補総数<=12(phrases<=7+words<=5)なので常に満たされ、実質は「全候補を何かの区分に入れる」。ただし関数は上限判定`allowed()`を必ず通し(上限超過候補があればそこで止める=防御)、kp_confirmedでは無効。候補なし=ボタン無効。
- 5件Vocab=①3+②2(②が0〜1件の記事は掲載件数全て)。②を2件必須にする変更は原文に無く行わない。

## 1. A: 一括選定画面(推奨=V3を拡張、新V4ディレクトリは作らない)
| 案 | 利点 | 欠点 |
|---|---|---|
| V3拡張(同じ`user_test/selection_form_v3/`・同じdata/・同じ`?a=`) | 公開URL・export_form_data・既存test(node/py)・fixturesが連続、form_logic.jsの二重化なし(Dangling回避) | 既存index.htmlの大幅書換え |
| 新V4(コピー) | 既存を壊さない | ロジック二重管理・旧URL残置・データ配布二箇所 |

→ V3拡張。旧単体UIの`?a=<slug>__<lvl>`は「選択セットを開く」導線として互換維持(1セット編集部がそのまま下部フォーム)。ユーザー提示URLは従来と同じ`.../user_test/selection_form_v3/index.html`(公開前に実URL確認)。
- 画面: 上部=進捗(対象記事数・セット数・Done数・バー)/中央=記事行リスト(1記事1行、Std/Advチップ[未完了・Done・要再確認]、クリックで下部フォームを該当セットに切替、「次の未完了へ」ボタン)/下部=選択中1セットの既存フォーム(①②③・文法)+Doneボタン。記事数はarticles.jsonの**対象バッチ**から動的生成(固定9にしない)。モバイル=一覧は折畳み可・チップ44px以上、下部フォームは全幅。
- 対象セットの定義: articles.jsonに任意キー`batch:{id,date,members:[stem...]}`を追加(無ければdata有りの全セットからダミー/slot/legacyを除外)。Fableが日々の対象を書出し時に指定(ユーザーはURLを開くだけ)。既存`articles[]`は触れない。
- Done: booleanは保存せず**署名方式**=`st.done={sig,at}`、`sig=sha256(選択内容+文法+合成コメント+data d6)`。表示時に`sig===現在sig`ならDone、不一致=自動解除(「内容変更のため未完了に戻りました」表示)。変更で自動解除が署名比較により自然に成立しテスト容易。データ更新(d6変化)でもsigが変わりDone無効=陳腐化検出。
- Done条件(`doneErrors(d,st)`、具体的エラー配列): ①ちょうど3件(kp_confirmedは免除)、文法decision!=undecided(既存`grammarBlocked`)、validateArticle OK、提示候補>=3。コメントは任意。
- 保存: localStorageキー`eigo-kp-form-v3`を**継続**(旧stateは読込時にnormalize、未知フィールド保持=下位互換)。新フィールド: `comment_phrase, comment_word, done`。旧`comment`は「追加指示(全体)」として保持(既存コメントの用途を失わない)。リロード・切替で保持(都度save)。「全リセット」は確認ダイアログ付き別ボタン。
- 一括コピー: 全Done時のみ成功。未完了で押された場合はコピーせず未完了の記事名・レベルを列挙(各行クリックでジャンプ)。コピー直前に全セットを再検証(`doneErrors`、3件条件含む)。成功時=緑バナー「N件をコピーしました」、クリップボード失敗時は既存フォールバックtextarea。
- ChatGPT送信・技術情報付きコピーは一括画面では出さない(自動送信対象外)。単体「選定結果をコピー」は選択中1セットに残す。

## 2. コピー形式(受入互換)
**各セットは現行のAIF1 readableを一字も変えず**に使い、一括ヘッダと区切りで連結:

    以下はeigo-radioの学習項目選定結果(一括)です。…(各ブロックを変更せずそのまま)
    一括ヘッダ: 件数=N / 生成=ISO時刻 / バッチ=<id>
    ════ SET 1/N ｜ <slug>__<level> ════
    <buildReadable出力(記事：…｜Standard、①②③、文法、自由コメント、照合コード)>
    ════ SET 2/N ｜ … ════
    …
    ════ END 合計N件 / BATCH1-<N>-<全照合コード連結のsha10> ════

- 各セットの照合コードはer128が現行どおり検証可能。新設`restore_batch(text)`(er128に**追加**のみ・既存`restore`/`cmd_from_readable`無変更): `════ SET i/N`でブロック分割→各ブロックを既存`restore()`へ→**全件PASS時のみ**全payload返却(1件でも不一致なら全体拒否し原因セットを明示、何も書かない)。N一致・BATCH1コード一致・重複セット検出も検査。CLI`--from-readable-batch`新設。
- コメント(AIF1のm8互換のため単一合成文字列): 【フレーズ】…／【単語】…／【追加指示(全体)】…の行(空区分は行ごと省略、全空=`なし`=従来と同一)。ラベルでClaudeが区分識別。m8=合成文字列のsha8。**AIF1コード構造・restoreの既存ロジックは無変更**。受入側でラベルから分解して`comment_by_section`を加法追加する案は任意(Fable判断)。
- ちょうど3件の検査位置: フォーム(Done/一括コピー再検証)+`restore_batch`(受入側でも再検証)。単体`restore`(旧AIF1回答)は互換のため<3件を警告ノートのみ(拒否しない)。

## 3. B: コメント欄・3件必須・残り全選択
- コメント: 「フレーズ選定欄」「単語選定欄」の直下にそれぞれtextarea。候補をkind(phrase/word)別セクション見出しで2グループ化(候補順は既存維持)。
- ①表示「① 2/3 ※ちょうど3件必要」、0〜2件=Done不可+赤文言、4件目は選択不可(既存`allowed`)。
- 「残りをすべて選択」: form_logicに純関数`selectRemaining(d,st,tl)`追加(nodeテスト可)。未選択候補を表示順に③へ。①②は触らない。`allowed()`が拒否する候補があれば停止して「N件は上限のため選べません」表示。選択後はDone署名が変わり自動解除。無効条件=未選択0/kp_confirmed/データ不正。
- 候補不足: 提示候補<3のセットはDone不可+「候補不足(K件)のためKey Phraseを3件選べません。品質基準を下げず停止。候補補充が必要」と原因表示(一括コピーも拒否)。

## 4. C: Vocabulary 5表現の音声化
**方針**: 追加2表現(②)のみ新規TTS。KP3表現は既存KP英語区間(`en_audio`)の再生に再利用(新規生成0)。
- 生成段: X/Y/Z共通の新関数`generate_vocab_extra_audio(...)`(新module `er137_vocab_extra_audio_01.py`想定)。各②表現=`_kp_english_generate_fn`相当(KP3V 3-ASR多数決+Master Audio Store key)で`vocab_extraN_en.wav`を生成。同一表現でStoreに正式KP英語音声(同key)があれば**Store hit=生成0**(「KP音声再利用優先・重複回避」の実体)。`_generate_or_reuse_kp`のrole=`vocab_extra_english`で再利用ガード・値ガード・KP vote再利用ゲート・resumeキャッシュ(tts_generation_results.json)に載せる。retry/fallbackはKP englishと同一(上限・安全装置は独自変更しない)。
- 配線位置: ②確定(vocab_confirmed/Part1)後・End Userページ生成(`pages`段、build_enduser)前。X=er019 runner、Y=er121_family_y_audio_01(xr._generate_key_phrase_segments_*経由で共有)、Z=er026 runnerのKP音声段の直後に同一関数を1呼出追加。**新stageは作らず既存kp系stageへ内包**(`--stages`列挙・RESTART_STORM規則への影響を避け、resumeはcachedで担保)。
- 成果物: 公開mp3を記事`enduser/audio/`へ、`article.json`の`levels[lv].vocab[i]`に**加法的フィールド**`audio:{kind:kp_clip|standalone,ref|file,start?,end?,dur,sha256}`。KP項目=`kp_clip`(`parts[].kp[].en_audio`参照)、②=`standalone`。`enduser_article_v1`のschema/validate/整合検査に追加(5件すべてaudio有を必須=欠落でpages生成STOP、fail-closed)。Dangling防止=audio fileの存在・sha・長さ>0を`verify_consistency`で検査。
- End Userカード: `summary`内の見出し横に▶ボタン(`button.vplay`、aria-label「英語を聞く」、44px)。clickで`preventDefault()+stopPropagation()`し`<details>`開閉と非競合。再生は共有Audio要素`A`で`playVocab(vi)`: KP=seg mp3+区間(`playKp`と同形、終端停止)、②=standalone。他表現/本文再生を押せば直ちに切替(単一Audio=排他)、`mode`に`vocab`を追加し終端で本文位置へ復帰(`endKp`と同形)。既存の本文再生・KPボタン・同期ハイライトは分岐1つの追加のみ。
- 既存公開記事: 公開済みenduser有り=Y再配達・Y姓・X月reselect・Z melos(+藪の中=お蔵入りのため対象外)=4記事×2レベル×②最大2=最大16clip。`backfill`CLI(TTS+ASR、Cap付き)で追加し`pages`再生成(本文・音声不変)で公開dir更新。制作中(X4記事+雪女)は新経路で自動(X4はpagesでバックフィル)。
- 原価: 追加=②2表現×2レベル=4clip/記事セット。概算0.1〜1円/記事セット(70円目標の1.5%以下、確定値は検証runの実測)。Store hit=0円。保存・配信=mp3数KB×4でPages無料枠内=増分0円。
- 検証run費用: 16clipで概算2〜15円(Cap 50円で十分、7-7の300円以下枠内)。

## 5. 並行Workerとの衝突回避
| 衝突点 | 相手 | 回避策 |
|---|---|---|
| `enduser_page_assets/rev01-f`・`derive_assets_01.py` EDITS・`ASSET_BUILD_ID`・`app.js` | 英日ハイライトWorker(rev01-f新設中) | **順序付け**: 相手のcommit完了を待ち、その上に`rev01-g`(=f+vocab再生)を派生。実装は先行して**別ファイル断片**(ADDキー`V-*`)でEDITSを書き、f側EDITSと独立にテスト。同一build idへ相乗りしない(相手の凍結・検証を壊さない) |
| `er135_enduser_page_01.py` build_enduser・schema・validate | 同上 | vocab audioの処理は新module`er137`に集約。er135への変更は(a)schemaのvocab audio(b)validate/verify項目(c)build時の1呼出のみ。着手時にgit logで最新を再確認 |
| `user_test/selection_form_v3/*` | X 4記事・雪女Worker(data追加) | form_logic.js/index.htmlを触るのは本タスクのみ(相手はdata/*.jsonとarticles.json追記のみ)。articles.jsonは`batch`キー追加のみ |
| er128 / er119 | 確定済み(読取のみ) | `restore_batch`は新関数追加のみ、既存無変更(差分grep確認) |
| runner KP段(er019/er121/er026) | X4記事・雪女の実走 | 実走中は編集せず、実走停止/完了後に1呼出追加(resumeで旧新コード混在を防ぐ) |

## 6. Opus条件A論点
1. 新UI状態管理: Done署名方式の妥当性、localStorage後方互換、データ更新の陳腐化検出、複数タブ同時編集(後勝ち)。
2. コピー形式互換: 現行AIF1連結+区切り+一括コード、コメントを単一合成文字列にする判断(m8互換)、`restore_batch`のatomic性とちょうど3件の検査位置(フォーム+受入の二重)。
3. 新TTS配線: ②音声のgenerate_or_reuse契約(Store key共有でKP音声再利用、KP3V/再利用ガード/resume整合)、新stageを作らずkp段へ内包する是非、article.json加法スキーマ+fail-closed検査、`mode=vocab`追加によるapp.js状態機械の回帰リスク、rev01-f/g順序。
4. バックフィルの冪等性(既存公開dirの安全な差替え、旧dirのbackupは既存publish手順に準拠)。

## 7. 実装計画(委任分割・見積)
依存: 設計承認(Fable+Opus条件A)→並列3本。
- 委任_02A(Sonnet): form_logic拡張(exact3/selectRemaining/doneErrors/署名/合成コメント/buildBatch)+nodeテスト+index.html一括画面+Playwright(1/4/9/10記事×2レベル、Done/解除/リロード、未完了コピー拒否・成功、2件Done拒否、残り全選択、PC/スマホ)。実装3〜4h+検証1h。API 0。
- 委任_02B(Sonnet): er128`restore_batch`+CLI+ちょうど3件検査+test(既存fixtures流用+batch異常系)+export側`batch`キー出力。1.5〜2h。API 0。(02Aとは形式仕様のみ共有、fixtureで契約)
- 委任_02C(Sonnet): `er137`(②TTS・再利用・ASR・resume)+3 runner配線+article.json schema/validate/verify+mockテスト。3h。続く02C-2: app.js `rev01-g`再生UI(英日ハイライト完了後)+Playwright(5表現再生・開閉非競合・本文再生回帰)2h。
- 委任_03(Sonnet、有料): 実TTS/ASR runtime evidence=新規1記事×2レベル+既存公開記事バックフィル(最大16clip、Cap 50円)、3 Family×Std/Advで実再生確認。2h。
- 委任_04: Fable受入+SSOT(CURRENT_SPEC/OPEN/DECISION_LOG)+公開+最終URL提示。
クリティカルパス: 設計承認(~0.5h)→02A/02B/02C並列(~4h)→02C-2(f完了待ち)→03→04。同日完遂可(日付分割なし)。並列化で直列約12h→約6〜7h。
開発費: TTS/ASR実費は概算<=50円。LLM判断コールなし。

## 8. 撤去・整合
- 変更: V3単体「ChatGPTへ送信」は一括画面で非表示(`buildChatGptUrl`の残置/撤去はFable判断。残置時は呼出元をGrep管理)。LIMITS文言「最大3」→「ちょうど3」。旧test期待値「①0件でもコピー可」はDone不可へ修正(不整合出力を期待値にしない)。
- 現行仕様整合: AIF1/文法1件/ニュアンス廃止/KP3V/Master Audio Store契約/enduser_article_v1(加法)を維持。
