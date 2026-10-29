# DESIGN_NOTE_01(END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01b、2026-10-29)

## 読んだ正本
- 旧 `user_test/unified.html`(20,014B)・`user_test/articles_2026_0918.html`(一覧→unifiedへ`?src=&level=&en=&ja=`)
- 最近の完成ページ `user_test/family_x_ai_island_form_01/index.html`(主記事)・`family_x_moon_shrinking_reselect_01/index.html`(Grammar 1件)・`paycheck_personality_e2e_02/index.html`
- 選定=`ARTICLE_PICK_01.md`(01a)

## 継承した要素(unified)
| 要素 | unified | 試作 |
|---|---|---|
| 配色・字体 | `--bg #f6f7f9`/`--accent #315efb`/system font | そのまま(CSS変数名も同じ) |
| 見出し | 暗色グラデのhero(eyebrow=レベル、h1=日本語題、sub=英語題) | 同じ。eyebrowに「English Your Way · Standard/Advanced」 |
| カード構成 | Intro / Preview / Key Phrases / Full Script(Comment=枠付き) | 同順。+In One Line、Vocabulary & Expressions、Grammar |
| 「▶ ここから再生」ボタン | 各カード右上、全体audioをseek | 継承(「通しで ▶」)+パート別(「▶ このパート」) |
| 内部情報の非表示 | 効果音・ジングル・技術情報を出さない | 同じ(Intro SFX/Notification/定型案内/Outro/Local Rewrite注記/制作情報/事後試聴リストは非表示。通し音声には含まれる) |
| 単一ページ・静的 | 外部ライブラリなし | 同じ(html/css/js、fetchでJSON) |

## 変えた点(最小限・理由つき)
1. 再生UI: unified=sticky上部のネイティブ`<audio controls>`。スマホで親指が届く**固定フッター**(再生/停止・シークバー・時刻・±10秒・現在パート名)へ。ユーザー指示「スマホ重視・固定フッター等」。
2. Std/Adv切替: unifiedは別URL(`?level=`)。試作はタブ切替(同一記事のStd/Advが完成済みのため)。
3. 本文下線: unifiedの`mark.kp-hl`(水色)ではなく、**最新の承認済み表示**(AI島公開ページのlk1/lk2/lk3、`family_x_ai_island_form_01/index.html`のCSSと凡例)をそのまま使用。
4. 再生速度: 既存(unified・公開ページ)に無いため**未実装**(新機能の仕様追加に当たるため)。±10秒ボタンは「シーク操作」(原文§3)の範囲として追加(試作上の追加操作。Phase 3で要否判断)。

## 組み込んだ機能と出典(既存仕様どおり・内容は改変なし)
- タイトル・レベル: 公開ページのJapanese title/Topic intro、タブ。
- 全体再生=公開済み通しmp3、パート別=公開済みsegment mp3(`../family_x_ai_island_form_01/audio/`を相対参照。コピーなし。sha256を`data/*.json`の`audio_sha256`に記録)。
- Key Phrase: Std=英語+日本語の意味、Adv=英語+英語での解説(公開ページ同様)+各KP音声。本文ハイライト(lk1/2/3)+語の意味一覧(`lk-meaning`)。
- Word(Vocabulary & Expressions): 本文中の意味・本文の英文・日本語訳・解説(公開ページの`study`節を構造化)。
- Grammar & Sentence Structure: 採用件数に応じ表示(0件=コーナーごと非表示。AI島Std/Adv=0件確定、月Adv=1件)。※公開ページは0件でも「ありませんでした」の文を出す旧実装だが、承認済み仕様(0件は非表示)に従い非表示。
- Preview/Comment1-4/In One Line: 公開ページどおり(Std=日本語、Adv=英語)。
- 文単位ハイライトのフック: 各文`<span class="sent" data-sid>`+`data/sync_index.json`/`?sync=dummy`から`sentences:[{sid,start,end}]`(全編内秒)を読む(委任_02で01aの実同期を接続)。

## データ方式
公開ページHTML+`audit/timeline.json`から`tools/build_data_01.py`でJSON生成(正本の表示=公開ページと同一内容を保証、再利用優先)。表示上の除去は検証用注記(Chunk記号・Local Rewrite着色/注記・制作情報・事後試聴リスト)と、月の文法解説末尾に混入していた区切り文字列`=====`のみ(`data/_sanitized_log.json`に記録)。
