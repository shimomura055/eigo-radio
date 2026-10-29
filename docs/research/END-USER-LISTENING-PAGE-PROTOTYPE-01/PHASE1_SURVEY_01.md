# PHASE1_SURVEY_01(END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01a、2026-10-29、API 0)

凡例: **[仕様]**=CURRENT_SPEC/ユーザー正式決定に記載の承認済み仕様 / **[実装]**=repo上の稼働コード・生成済みページ / **[未配線]**=承認済みだが実装中・未配線、または未承認。file:lineは調査時点(HEAD e8219e9fc)。
原文=`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PROTOTYPE-01_USER.md` §2の8項目に対応。

## 0. 総括(再利用方針)
- 旧unified/articles_2026_0918の「単一の全体プレイヤー(画面上部固定)+セクションごとの『▶ここから再生』+カード型」というシンプルさは、最新の公開試聴ページ(`er_user_listening_page_common_01.py`=表形式・各segmentごとに`<audio>`が並ぶ制作者向けの試聴ページ)には引き継がれていない。End User向け試作は**旧unifiedの構造を骨格**にし、**中身(本文・KP/Word・Grammar・Comment)は最新公開ページのデータ(run_dirのartifact)をそのまま再利用**する(新規生成なし)。
- **1文単位の同期データは既存にない**(下記(7)。ASR auditは転写テキストのみでtimestampなし)。ただしsegment境界(`timeline.json`)とChunk境界(`chunk_tts_assembly_*.json`の`gap_offsets_in_part_s`)は正確に既存。文境界は本委任でAPI 0(ローカルASR+無音スナップ)により生成(`SYNC_METHOD_01.md`)。

## (1) 旧unifiedプレイヤーの画面構造・機能・スマホ対応
| 項目 | 内容 | 根拠 |
|---|---|---|
| 区分 | **[実装]**(user_test用の旧End User向け試験ページ。Production公開ページではない) | `user_test/unified.html` |
| 起動 | 記事選択ページ(`articles_2026_0918.html`)のボタン→`unified.html?src=<元player.html>&level=A2/B1B&en=..&ja=..`。unifiedは`src`のplayer.htmlを`fetch`してDOMをスクレイピングし再描画(`timelineRender`/`simpleRender`/`renderVoicesFull`/`renderFamilyCFull`) | unified.html:175(timelineRender)・:200(simpleRender)・:216-221(translations/index.json解決) |
| 構造 | hero(ja/enタイトル・レベル表示)→**画面上部固定プレイヤー**(`.player{position:sticky;top:0}`、`<audio id=episode controls>`1つ=全編通し)→カード(`section.card`)の縦積み(Preview/KP/Comment/Full Story/In One Line…)→日本語訳セクション | unified.html:12・:31 |
| 操作 | 各カードの「▶ ここから再生」ボタン=`jump(sec)`で全編audioの`currentTime`をセクション開始秒へ設定して再生。**パート別の個別audioはない**(単一audio+シーク) | unified.html:67-70 |
| KP/本文ハイライト | `kp_mapping.json`を読み`mark.kp-hl`(背景#dff2fb)で本文のKPを強調(旧仕様。最新の①②③下線仕様とは別) | unified.html:19・:227-249 |
| 日本語訳 | `user_test/translations/index.json`→`translation_ja.json`を「日本語訳」カードで表示 | unified.html:254-271 |
| スマホ | `<meta viewport width=device-width,initial-scale=1>`あり。`@media(max-width:640px)`でh1縮小・カードpadding縮小・KPグリッド1列化。固定プレイヤーで親指が届きやすい。**1文ハイライト・再生速度・パート別再生はなし** | unified.html:5・:17 |
| 記事選択 | `articles_2026_0918.html`: card grid(`minmax(300px,1fr)`)、Std/Advボタン(min-height 44px)。viewport・@media(max-width:600px)あり | articles_2026_0918.html:5・:30 |

再利用: 構造(固定プレイヤー+カード縦積み+Std/Adv切替)・配色(`--accent:#315efb`等)・スマホbreakpoint。非再利用: `fetch`でplayer.htmlをスクレイピングする方式(脆い。試作は`sync/*/index.json`+run artifactの静的JSONを読む)。

## (2) 最近の完成記事ページの表示機能
| 系統 | 実装 | 表示機能 | 根拠 |
|---|---|---|---|
| X(AI島=公開済み) | **[実装]**標準公開builder `er019_family_x_listening_page_01.py`(新規記事の正式入口、API 0)。共通描画`er_user_listening_page_common_01.render_standard_page`+学習ブロック`er120_part2_wiring_01.public_study_html`+`compose_page_html` | Std/Advのnav、レベルごとの「▶全編を通し再生」ボタン+全編`<audio>`、**segmentごとの表(パート名・開始秒・個別`<audio>`・台本/KP表)**、KP表(Std=英語+日本語の意味/Adv=英語+英語での解説)、台本の①②③下線、Part 1「Vocabulary & Expressions」・Part 2「Grammar & Sentence Structure」、`制作情報`details、事後試聴リスト | er019_family_x_listening_page_01.py:69-136(level_data)・:138(build_page); er_user_listening_page_common_01.py:218(render_standard_page)・:234(playall)・:240(viewport) |
| Y | **[実装]**`er121_family_y_audio_01.render_y_page`(:1589)・`build_page_rows`(:1493)、runner`stage_pages`(er121_family_y_runner_01.py:1282)→`compose_page_html`(:1302) | 同型の表+Voice 1〜3・Narrator導入・Closing | 同左 |
| Z | **[実装]**`er063_family_z_audio_01.build_listening_page_html`(:2440)・`build_pages`(:2696)、runner`stage_pages`(er026_family_z_fiction_production_runner_01.py:2619)→`compose_page_html`(:2644-2645) | 同型+Part別長尺audio(`a2_p1.mp3`等) | 同左 |
| 共通の注意 | 台本は`<div class='script'>`内に**プレーンテキスト+装飾タグ(①②③)**のみ。開発専用の⏸(Chunk境界)・赤/濃青(LR/Fallback)は`audience=dev`/報告用表示で、publicでは出さない(`script_block`) | er_user_listening_page_common_01.py:187-206 |
| 現状のCSS | `body max-width:1100px`の表(`table{width:100%}`)、`td.play{min-width:340px}`=スマホでは横スクロールが出やすい**制作者向けレイアウト**。viewportはあり、スマホ最適化の@mediaは実質なし | user_test/family_x_ai_island_form_01/index.html `<style>`(1行目) |

公開URL(AI島): https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/index.html

## (3) Standard/Advancedの最新学習コンテンツ仕様
| 項目 | 区分 | 内容 | 根拠 |
|---|---|---|---|
| 構成 | **[仕様]/[実装]** | Intro→Welcome→Topic intro→Japanese title→Preview(Std=日本語/Adv=英語)→Key Phrase×3→Full Story Part1〜3(Comment1〜4をPart間に挟む=Z方式C3)→In One Line→Outro。Part内は段落単位のChunk TTS | AI島`timeline.json`、CURRENT_SPEC:1268-1273(Std日本語Preview/Comment=S3)・2860付近(Comment4/In One Line) |
| Part 1「Vocabulary & Expressions」 | **[仕様]PRODUCTION_WIRED** | 案α+T1訳。Std/Advとも(Stdは2026-10-27 SYNC-26で`display_spec`付き新規記事から)。項目=見出し(used_form)/本文中の意味/本文の英文/日本語訳/日本語の詳細解説 | CURRENT_SPEC:2088-2094・3226-3253(学習項目①②③ 表示仕様、SYNC-26/27) |
| Part 2「Grammar & Sentence Structure」 | **[仕様]PRODUCTION_WIRED** | AI評価Top1/Top2のみ提示→ユーザー原則1件(0件可)選択→finalize(LLM 0)。Std/Adv共通 | CURRENT_SPEC:2110-2112(SYNC-20〜25) |
| 学習項目の本文表示 | **[仕様]PRODUCTION_WIRED** | ①Key Phrase=太字+二重下線 / ②追加解説=太字+通常下線 / ③本文意味表示=通常下線のみ(直下に「英語=訳」)。色・背景マーカー不使用、本文textContent不変 | CURRENT_SPEC:3226-3235 |
| ニュアンス解説 | **[未配線]**(2026-10-29ユーザー正式採用`APPROVED_FOR_PRODUCTION`、到達目標PRODUCTION_WIRED、実装中。OPEN-586/NUANCE-EXPLANATION-PRODUCTION-WIRING-01) | 記事・level最大1件、HR採用時のみ独立コーナー表示、不採用/なしは見出し・空枠含め非表示。共通module`er134`は委任_02Aで追加済み・**未配線**(`compose_page_html`の`nuance=`引数は受け口あり。`nuance_for_display`は`nuance_result.json`が無ければNone) | docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md:1-75; er120_part2_wiring_01.py:611-621・:442-454 |
| 文法0件時の表示 | **[未配線]**(同ユーザー正式採用 §2-C): 0件ならコーナー全体を非表示(見出しのみ禁止・プレースホルダー禁止) | 現行の既公開ページ(AI島)は旧表示=「今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。」(`er120_part2_grammar_production_01.py:163 _LEGACY_ZERO_GRAMMAR_BODY`) | 同USER:51・:103 |

→ 試作は**0件=非表示**を採用済み仕様(実装中)として扱う。既公開ページの旧メッセージは再現しない。ニュアンス解説は本記事に確定データが無いため表示対象なし(未配線として注記)。

## (4) Key Phrase/Wordの表示仕様(英語・日本語意味・英語解説・音声・本文ハイライト)
- **KP表(segmentの行内)[実装]**: Std=`英語|日本語の意味`、Adv=`英語|英語での解説`(`er019_family_x_listening_page_01.py:104-112` kp_block)。audio=「番号+KP英語+日本語の意味(Std)/英語での解説(Adv)」で1 segment(AI島Std KP1=6.9秒)。
- **Part 1詳細解説[実装/仕様]**: 上記(3)。①は解説コーナーで音声化対象、②は音声なし、③は短い日本語訳のみ(CURRENT_SPEC「SYNC-26 正式仕様表」)。
- **本文ハイライト[実装]**: `<strong class="lk1" data-hl="p_xxx">`(①)/`lk2`(②)/`lk3`(③)。CSS: lk1=太字+二重下線、lk2=太字+実線、lk3=下線のみ(AI島ページ内`<style>`、`ul.lk-meaning`=③の訳リスト、`p.lk-legend`=凡例)。`data-hl`で候補IDと対応。生成=`er_learning_highlight_01.render_script_html`/`er128_kp_highlight_01.py`。
- 1文ハイライト導入時の注意(01bへ引継ぎ): 本文は「textContent不変・余計な記号なし」が仕様(CURRENT_SPEC:3229)。文ハイライトは**CSSクラスで背景/左ボーダーを付ける方式**にし、①②③の下線装飾(色・背景なし)と属性を分離する(KP下線を壊さない)。

## (5) Grammar & Sentence Structureの表示仕様
- 既存ページ[実装]: `section.study > h3 Grammar & Sentence Structure > div.study-item > dl(対象となる本文英文 / 日本語訳 / 文法・構文の仕組み…)`。月reselect Advは1件(疑似分裂文: `what matters is not its weight; it is how well it keeps heat in`)。
- 配置: Adv=Part 1直後、Std=Stdの節に文法ブロック(CURRENT_SPEC:2108)。
- 0件: 旧表示=メッセージ文 / 新仕様=**コーナー全体非表示**([未配線]・実装中、上記(3))。AI島は両level 0件確定(ユーザー決定2026-10-27 USER_03 §1-A)。
- 試作での扱い: 採用件数>0のみ表示。AI島=0件→非表示、月Adv=1件→表示(補助記事)。

## (6) Family X/Y/Zの再生・記事構成・表示仕様の差
| Family | segment構成(再生単位) | Chunk | 話者 | 備考 |
|---|---|---|---|---|
| X | Preview/KP×3/Comment1〜4/Full Story Part1〜3/In One Line | Part内に段落Chunk(k1〜k3、gap 0.2秒)。`chunk_plan_*.json`+`chunk_tts_assembly_*.json` | Aoede(本編)+Charon(Support)等 | Std=日本語Preview/Comment、Adv=英語。1 segment=1 mp3(エピソードwavをtimelineで切り出し) |
| Y | Lead(Narrator)/Voice1〜3の各Introduction(Narrator)+Voice本文/Closing(Narrator)/Comment1〜3/KP×3 | 各segment「TTS 1回/分割なし(段落=1)」と表示 | 3 Voice+Narrator | segment=話者単位なので同期データはsegmentごとに独立生成できる |
| Z | Preview/KP×3/Comment1〜3/Full Story Part1〜3(長尺57〜71秒、`a2_p1.mp3`等) | Part長尺audio | Fenrir/Algieba/Aoede等(物語内の話者切替) | 台本の話者ラベル/紹介文の扱いに文分割ルール追加が必要 |

根拠: `user_test/family_y_production_redelivery_fee_03/index.html`・`user_test/family_z_tell_tale_heart_fenrir_01/index.html`のsegment表、`er121_family_y_runner_01.py:34`(STAGES)、`er026_family_z_fiction_production_runner_01.py:1183`(E2E_STAGES)。

## (7) 再生位置↔スクリプトを対応付ける既存データ・機能の有無(最重要)
| データ | 有無 | 粒度 | 場所 | 評価 |
|---|---|---|---|---|
| episode内のsegment開始秒 | **あり[実装]** | segment(Intro/Preview/…)、小数3桁 | `<run>/{a2,b1b}/audit/timeline.json`(part/start_seconds/duration_seconds)。公開builderはこれでエピソードwavを切ってsegment mp3を作る(er019_family_x_listening_page_01.py:106-108) | **正確**(同一wavからの切出し)。segment内の文位置は不明 |
| Chunk境界 | **あり[実装]** | Part内の段落Chunk間ギャップ(0.2秒) | `audit/chunk_tts_assembly_{a2,b1b}.json` の `parents.<part>.gap_offsets_in_part_s`・`gap_offsets_in_episode_s`・`chunk_samples` | **正確**(組立時に確定)。Chunkは約3〜5文のまとまり |
| TTS segment/clip時間 | あり | clip単位`duration_seconds` | `audit/tts_generation_results.json`(各`segments[*].duration_seconds`・`trim_info`) | clip単位のみ |
| ASR audit | **テキストのみ。timestampなし** | clip全体の転写 | 同上 `segments[*].asr_text`・`attempts_log[*].cascade_steps[*].text`(provider=openai_asr等) | **文/単語のタイムスタンプは保存されていない**(`timestamp|offset|words`のgrepはTTS語数・実行日時のみ) |
| Store manifest | 無関係 | 再利用clipの識別 | `er006_output/master_audio_store_01/manifest.json` | 時間情報なし |
| assembled wav | あり | エピソード全体 | `<run>/{a2,b1b}/assembled/*.wav`、`run_summary_assemble.json`(`duration_seconds`・`chunk_tts.parents`) | 文境界なし |
| 旧unified | あり(部分) | セクション開始秒のシーク | unified.html:67 | 文単位でない |

**結論: 文単位のタイムスタンプは既存に無い。** 一方、segment・Chunk境界は正確な既存データがあるため、文境界の生成はsegment内の補間で済む。ASR再実行が最小費用(本委任でローカルASRにより実施、費用¥0)。

## (8) Production初回経路・retry/regeneration/resumeと公開ページの関係
- **ページ生成のstage[実装]**: X=runnerの`--stage player`以降(assemble完了後)+標準公開builder`er019_family_x_listening_page_01.py`(**API 0**、assemble/Gate通過済みrunを入力。全検査PASS後にだけ`index.html`出力=fail-closed、同.py:1-12) / Y=`pages`→`page_verify`(er121_family_y_runner_01.py:34) / Z=`pages`→`page_verify`(er026…:1183)。
- **音声とページの関係**: 公開builderは**assembled wav**を読み(`summ["out_path"]`)、全編mp3(128k)と各segment mp3(96k)をtimeline通りに切り出す(同.py:104-108)。**ページ上のmp3はassemble済みwavの派生物**で、segment再生成(retry/regeneration)・LR/Fallbackがあると、assemble→timelineが更新され、ページ再ビルド(API 0)でmp3が差し替わる。
- **同期データへの影響**: 文の秒はmp3の内容に依存するため、(a)segment/chunkを再生成した場合、(b)Local Rewrite(LR)で本文が変わった場合、(c)Style/ゲイン処理が変わった場合は同期データを**再計算が必要**。再計算を`pages`stage内(API 0、ローカルASR)に組み込めば、再生成・resumeで自動追従できる。再利用キー=segment mp3のsha256+台本sha256(一致なら再利用=resume時ASR 0)。
- 公開済み記事の遡及更新は承認済み仕様上「遡及なし」(CURRENT_SPEC:3232)。試作は既公開ページを変更しない(`user_test/dev_enduser_page_01/`に隔離。本委任は編集しない)。
