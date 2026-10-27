# VERIFY_07 — `_03`公開ページの凡例⏸残存1行の撤去と不変確認(委任_09、API 0・JPY0・ページ再生成なし)
対象: `user_test/family_y_production_redelivery_fee_03/index.html`(commit 29d1a79d7)。VERIFY_06が指摘した「凡例に記号⏸が1件残る」不整合の是正。静的ページへの後処理(バイト列置換)のみで、builder/pages stageは再実行していない。

## 変更
撤去した文字列(1か所、index.htmlは改行なし1行ファイルのため行単位でなく部分文字列として削除): `<br>⏸=実際のTTS Chunk分割境界(開発確認用表示)。今回の記事にChunk分割境界はなく、表示はありません。`
バイト同一確認: 修正前(scratch保存)から上記文字列を除去したものと修正後が**完全一致**(50529→50391バイト、差138バイト=当該文字列のみ)。`git diff --numstat`は1行変更(1ファイル全体が1行のため)。
`tools/build_page_05.py`: 当該凡例の生成元`NEW_LEGEND`を`"</div>"`へ変更(凡例行を生成しない)。docstringも追従。`_03`の再ビルドはしていない。他に⏸文字列を含むProduction/生成元は無い(Grep `⏸=実際のTTS`: build_page_05.pyのみだった→撤去済み)。

## 検証
| 項目 | 結果 |
|---|---|
| `⏸`/`&#9208;`残存(index.html) | 0/0(修正前 `⏸`1)。`preview_segments_01.html`も0 |
| 承認文言「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」 | 逐語**2件**(上部`y-ai-notice`+制作情報節。VERIFY_06の記録どおり、修正前後で同数。委任文の「1件」は上部のみの想定と解釈。減っていない) |
| `audio/std_full.mp3` sha256 | `7c037f49d9c0d6454919ed4702a5014bbbe52ce4d52d57b9306e8112174a268c`(修正前後・公開URL配信とも同一) |
| `audio/adv_full.mp3` sha256 | `f2c7d26fa2a100c0ac0f3f6cc43524baeca70bfbd967a1a069bcdfd5e24cb5fc`(同上) |
| KP表(`<table class='kp'>`) | 6=6(修正前後同数) |
| 音声src(`src='audio/…'`) | 52=52 |
| 台本ブロック(`<div class='script'>`) | 26=26 |
| index.html sha256 | 修正前 `e69dd7c8…0e93c2d` → 修正後 `87f93366738d869bc49bdce6e0c77e37e8623fce8bb333acbad19ebb836f124a` |
| 公開URL headless(playwright/chromium、push後・Pages反映確認後) | `https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html`: HTTP200、配信size 50391・sha=修正後と一致、Console error 0・pageerror 0・HTTP>=400 0、body表示テキストの⏸=0、`<audio>`52・台本26・table 9(KP6+他3) |
音声・台本・KP表・説明文・学習内容は変更していない。Pages反映に約2〜3分かかった(反映前はサイズ50529の旧版配信)。
