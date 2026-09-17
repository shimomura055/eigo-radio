## 管理ID

`USER-TEST-ARTICLE-LANDING-10-01`(RESUME、SSOT確定後の実装)。報告は`docs/pm/RESULT_PACKET_LANDING_10_01.md`(新規、★★★★報告ここから/ここまで)。一時ファイル`docs/pm/ACTIVE_TASK_LANDING_10_01.md`。現在main=origin/main=`56aa528d`(要fetch確認)。**並行Agentなし。API/LLM呼び出し0、記事・音声・既存player・`user_test/unified.html`・`user_test/human_review.html`は変更禁止。** 目安30〜45分。不要な調査・追加Trial・追加機能なし。

## SSOT(唯一の正)

`C:\Users\tensh\eigo-radio\docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv`(列: category/title_en/title_ja/summary_ja/standard_url/advanced_url、ヘッダー+10行)。**最初に実際に読み**、10記事・20 URL全て`https://`・記事順・3カテゴリー(TSV表記のまま: 「News系の記事」4件/「様々な意見をまとめた記事」3件/「未来をテーマにした小説」3件)を確認し報告に記載。Fable確認済み事項: Personalized News Advanced=FIX-01 canonical(SHA `7ea8bd7a`)と一致、AI HiringはStandard(`src=...ai_hiring_3v_a2/user_test_simple.html`)/Advanced両方あり(ユーザー確認済み、「—」にしない)。過去の一覧・Repo内旧URL・記憶をSSOTに使わない。TSVの本文(タイトル・概要・カテゴリー名・URL)は**一切改変しない**(概要末尾の半角「.」もそのまま)。軽微な文字コード/BOM/parse対応のみ可。STOP: TSVを読めない/10記事でない/URL欠損/canonical不一致/SSOT矛盾。

## 目的・承認済み方針(`APPROVED_FOR_PRODUCTION`)

ユーザーテスト対象10記事の**正式なWeb一覧ページ**(1つのレスポンシブHTML)。ユーザーがタイトル・概要を見て自由に選べ、3カテゴリーが視覚的に明確。到達可能最大Status=`PRODUCTION_WIRED`(下記Gate 3全充足時のみ)。

## ページ仕様

- **配置**: `user_test/`配下(例 `user_test/articles_2026_0918.html`。既存ファイルを壊さない。命名は既存構成に合わせ報告)。静的HTML/CSS中心、JS最小(不要ならゼロ)。外部フォント/CDN依存なし(githack配信で完結)。
- **上部案内(短く、強制しない)**: 趣旨「気になる記事を自由に選んでください。迷ったら、3つのカテゴリーから1つずつ選んでみてください。」禁止表現: 「必ず」「すべて必須」「各カテゴリー1本必須」等。加えてレベル説明を1〜2行: Standard=日本語サポートあり / Advanced=英語のみ(初見で分かる文言)。
- **構成**: カテゴリー見出し→そのカテゴリーの記事カード群、をTSV順で3ブロック。カテゴリーごとに落ち着いた色分け(見出し帯・カード左ボーダー等、派手にしない)。カテゴリー名・記事順・所属はTSVどおり(再分類・並べ替え・追加・削除禁止)。
- **カード**: 日本語タイトル(主)/English title(副)/日本語概要/**Standardボタン(「Standard｜日本語サポートあり」等)**/**Advancedボタン(「Advanced｜英語のみ」)**。hrefはTSVのURL文字列をそのまま(推測・再生成・短縮・エンコード変更禁止)。`target="_blank" rel="noopener"`可。ボタンは最小タップ高44px、幅は狭い画面で全幅。
- **レスポンシブ**: PC(≥900px程度)=2〜3列カードグリッド、横スクロールなし。スマホ(≤600px)=1列、横スクロールなし、テキスト切れなし(長いEnglish titleは折り返し)、カテゴリー区切りが一目で分かる。
- **デザイン**: 既存`user_test/unified.html`の配色・フォント感(English Your Way · User Test)と大きく乖離しない。検索/ソート/フィルター/アニメーション/お気に入り/ログイン/過度な装飾は不要。ページタイトル・見出しに「User Test」文脈を明示。日本語表示は`lang="ja"`、`<meta viewport>`必須。

## リンク照合(全20本、機械確認)

TSVをパースし、HTML内の各カード(記事順)のStandard/Advanced hrefとTSVのstandard_url/advanced_urlが**完全一致**(文字列比較)することをスクリプトで確認しJSON化(`docs/pm/closeout_136_e2e/landing_10_01/href_match.json`)。取り違え(level=A2/B1とボタン種別の整合)・別記事混入なし。各URLへHTTP GET(githack)で200を確認(200だけでPASSにしない)。

## Browser E2E(Playwright headless Chromium、rawcdn.githack公開URL=commit/push後のSHA)

- **PC viewport 1280×800**: 10記事カード全表示(タイトルtextContentがTSVと一致)、3カテゴリー見出し表示(TSV表記一致)、カード崩れなし(各カードのbounding boxが重ならない・画面内)、`document.documentElement.scrollWidth <= window.innerWidth`(横スクロールなし)、Standard/Advancedボタン各10個表示、**代表リンク実クリック**: 各カテゴリー1本+AI Hiring Standard(srcが`user_test_simple.html`で他と形式が異なるため必ず含める)=計4本以上を新タブで開き、遷移先URLがhrefと一致し、既存チェッカー`docs/pm/tools/user_test_page_e2e_check.py`相当でPlay進行(currentTime>0、error=null)を確認。
- **スマホviewport 390×844(モバイルUA/touch)**: 1列(カードのx座標が全て同一)、横スクロールなし、テキスト切れなし(overflow検出: 各テキスト要素のscrollWidth<=clientWidth)、ボタン高さ≥44px・幅が画面内、カテゴリー見出し表示、代表リンク2本以上をタップ相当(click)で遷移確認。
- screenshot: PC全体/スマホ全体(フルページ)を`docs/pm/closeout_136_e2e/landing_10_01/`へ保存。結果JSON `e2e_result.json`。
- githack初回の「External Content Notice」中継ページは既存チェッカーの通過処理を再利用。

## Dangling Reference Check

user_test wrapper(`unified.html`)・配信方式(commit→rawcdn.githack)・Standard/Advanced表記・20本の遷移先(全て正式`USER_TEST_READY`記事のcanonical URL、DEV/Trial-only artifactへの参照なし。AI Hiring StandardはユーザーがRepo実体を確認済み)・Personalized News FIX-01を確認して報告。既存視聴ページは改変しない。

## SSOT/Git

- TSVをRepo管理対象に含める(commit)。
- `DECISION_LOG.md`: `## USER-TEST-ARTICLE-LANDING-10-01`(索引+本体): SSOT path、10記事・3カテゴリー、ページpath、公開URL、E2E結果、Gate 3チェック、Status。
- `ARTIFACT_REGISTRY.md`: 「ユーザーテスト一覧ページ(10記事、2026-09-18)」行を追加(path/URL/SSOT/evidence)。
- `OPEN_ITEMS.md`: 新規問題がある場合のみ。`CURRENT_SPEC.md`: 変更しない(証跡)。
- Git: 明示add(HTML/TSV/evidence/SSOT/RESULT_PACKET/delegation_log)、`git add -A`禁止、fetch→merge、commit分割可(HTML→push→E2E→SSOT)、trailer `Task-ID: USER-TEST-ARTICLE-LANDING-10-01`。公開URL=`https://rawcdn.githack.com/shimomura055/eigo-radio/<最終SHA>/user_test/<file>.html`(E2Eはこの最終URLで実施。SSOT commitでSHAが進む場合は、HTMLを含むcommitのSHAで固定したURLを正式URLとし、その旨明記)。

## Gate 3(全て○で`PRODUCTION_WIRED`、1つでも×なら`PARTIAL`で報告)

正式user-test page実装/PC responsive runtime確認/スマホresponsive runtime確認/全20リンクSSOT一致/Browser E2E PASS/公開runtime URL確認/Git反映/SSOT・DECISION_LOG更新/ユーザー承認内容と実装一致/DEV・Trial-onlyではない。

## STOP条件
TSV不整合/URL欠損/canonical不一致/配信経路との重大衝突/新Product・UX判断が必要(例: TSV本文の変更が必要、AI Hiring Standardのsrcがunified.htmlで再生できない)/既存記事修正が必要/git conflict。CSS・余白・font-size・breakpoint・card幅・button幅の調整は自律で可。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-ARTICLE-LANDING-10-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: TSV、`user_test/unified.html`(デザイン参照・読み取りのみ)、`user_test/`配下一覧、`docs/pm/tools/user_test_page_e2e_check.py`、`docs/pm/closeout_136_e2e/format_rule_01/`(E2E型)、PM_GOVERNANCE Gate 7(n)・9-7(配信)。事前指定外Readは理由付き報告。

## 報告(★ブロック、簡潔に、19項目)
1.最終Status 2.TSV読取結果 3.使用SSOT path 4.対象10記事(順) 5.3カテゴリー(TSV表記) 6.作成ページpath 7.公開URL 8.PC表示runtime確認 9.スマホ表示runtime確認 10.全20リンク一致 11.Personalized News Advanced FIX-01一致 12.Browser E2E結果(evidenceパス) 13.Git commit 14.main=origin/main 15.SSOT/Decision Log更新内容 16.未解決事項 17.USER_DECISION_REQUIRED残存有無 18.APPROVED_FOR_PRODUCTION未配線項目の有無 19.Dangling Reference Check結果(+Closeout Mandatory Check 21項目の○/×、無変更証跡)。
