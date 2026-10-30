# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 設計(委任_01、2026-10-30。実装は本設計のFable確認[+Opus条件A]後の委任_02)

前提=CURRENT_STATE_01.md。原則: 訳本文・英語本文は不変/誤ハイライトより非ハイライト/既存`highlight()`1点に追加/新規生成LLM呼出なし。

## D0. 判断が要る前提(判断候補。Fable確認事項)
1. **Z全作品とX/Yの非story部(Comment/Topic/Preview/In One Line)には日本語訳が存在せず、End Userページにも表示していない**(承認済み日本語原稿が無い=`none_approved_translation_hidden`)。ユーザー原文は「既存の本文クリック再生」と「対応する日本語訳」を前提にしている。本設計は **訳が表示されているブロックだけを連動対象**(X/Y story部)とし、訳の無いブロックは「対応先なし=ハイライトなし」とする。Zと非story部へ連動を広げるには**日本語訳の新規作成・承認・表示という別の新仕様**が要る(LLM翻訳=新規API・品質Gate・承認済み訳の位置づけ)。→ 分類=**D(真に新しい判断)**。推奨=本件はX/Y story部で先行PRODUCTION_WIRED、Z/非story部は「日本語訳の拡張」として別委任(Fable経由でユーザー判断)。Zを「未確認・未達」と明示し完了扱いにしない(原文§5)。
2. 意味的検証のための**埋め込みAPI**(文の意味類似度のみ。文章生成ではない)の使用可否: 費用は1記事あたり約¥0.1〜0.3(下記)。実測で「長さ・数字だけの決定論」は誤対応を出した(CURRENT_STATE_01 §5)ため、品質(誤ハイライト0)のために必要。→ 分類=**B(承認範囲内で自己解決。7-7: 承認済みScope内¥300以下・新仕様でない)**。ただし「新規LLM呼出は原則不可」の委任条件に触れるため理由・費用を明記しFable確認を求める。

## D1. データ設計
- `article.json`のstory part(`ja`を持つpart)へ**任意フィールド`ja_align`**を追加(`ja`と`paragraphs`は不変。schema id`enduser_article_v1`は加法的変更で維持、旧データ=フィールド無しはapp.jsが「連動なし」で従来表示):
  ```
  "ja_align": [ {"g": 0, "sids": ["std_14-s009","std_14-s010"], "ja": [paraIdx, start, end] | null, "conf": 0.93}, ... ]
  ```
  `ja`=`p.ja[paraIdx]`への**文字オフセット**(訳本文は書換えない。表示時にスライスして`<span class="jhl" data-jg>`で包むだけ)。対応不明=`ja:null`(非ハイライト)。1グループ=連続するEN文(1〜3)とJA連続区間(1〜3文)。1EN文は高々1グループ。順序は単調(ENもJAも前進)。
- `build_info.json`に`ja_align:{method,model,coverage:{story_parts,sentences_total,sentences_linked,groups_null},sha256}`(Family別・レベル別のcoverageをhandoff/完了報告に出す)。
- 検証(`validate_output`/`verify_consistency`): sidがその段落に実在・出現順/重複なし、オフセットが範囲内・非重複・単調、スライスが空でない、**`ja`全文のslice連結+未対応間隙==元文字列(不変条件)**、`ja_align`が有る part は`ja`有り、`conf`<閾値のグループは`ja:null`。

## D2. 対応づけアルゴリズム(`er135_enduser_align_01.py`新設。決定論+意味検証、新規LLM生成なし)
段落ペア(X=EN段落i↔JA段落i、Y=1:1)ごとに:
1. JA文分割: `。！？`で区切り、「」『』（）内の句点では切らない。連結==元段落(offset保持)。
2. 候補生成: 単調DP(§5プロトタイプ。許可move 1:1,1:2,2:1,2:2,1:3,3:1。EN/JA片側のみの欠落moveは非ハイライト扱い)。コスト=長さ比log差+群サイズペナルティ+λ×(1−cos類似度)。cos類似度=**OpenAI `text-embedding-3-large`(最新世代の推奨系。25節)でEN文・JA文を埋め込み、グループ平均**。埋め込みは`<run>/enduser_sync_cache`にテキストsha256キーで保存(resume/再実行でAPI 0)。
3. 採否(安全側): (a)グループcos≥τ1、(b)その決定が代替パスに対し余裕(次点とのコスト差≥δ)、(c)数字・固有名の一致(EN数字集合==JA数字集合、不一致=null)、(d)**段落全体の単調整合(総コストが閾値内)**。いずれか不成立のグループは`ja:null`。**段落全体が不成立なら全グループnull**(部分的に正しく見えて他が誤る事態を避ける)。
4. 文数一致(1:1)の段落も同じ検証を通す(順序対応だけを信用しない)。
5. 閾値(τ1/δ/λ)は**ゴールド(下記)で決め、決めた後は固定・testで固定**。ゴールド: 既公開3記事(X月/Y再配達/Y姓)×Std/Adv=215グループ全件を人手(Worker読取+別グループ目視)でラベル。受入基準=**emitしたグループの誤対応0**(precision=100%)。coverage(非null率)は目標≥85%(未達は安全側のnull=不具合でなく品質メトリクス。Fableに実測を報告)。
- 失敗系: 埋め込みAPI失敗→2回再試行→なお失敗なら**文数一致かつ長さ・数字検証を満たす段落だけ**を決定論で連動、他はnull+warning(build_info・完了報告に`degraded`表示。STOPにはしない=End Userページ本体の生成を表示拡張で止めない)。環境変数/設定でのON/OFFは設けない(正式採用済みのため既定ON。flag迂回なし)。
- 費用: X月Std+Adv相当で埋め込み対象約400短文(約1.2万token)×$0.13/M≈$0.0016≈**¥0.25/記事**。Y/Xとも<¥0.5。LLM生成呼出0・再生成0。70円/記事セット目標への影響<1%。

## D3. app.js / style.css(derive_assets EDITSのADDとして追加。DEV不変)
- 新build id=`rev01-f`(`enduser_page_assets/rev01-f/`、`ASSET_BUILD_ID`更新、`derive_assets_01.py`のOUT_DIRとEDITSに連動用ADD編集[J-L1..]を追加。旧`rev01-e`ディレクトリは凍結・残置)。
- `trHtml(p)`: `p.ja_align`があれば、各`p.ja[k]`をオフセットで切り出し、グループ範囲を`<span class="jhl" data-jg="<g>">escaped</span>`で包む(ja:nullグループと間隙は素のテキスト)。無ければ従来出力(旧データ互換)。
- `render()`末尾で`jgEls={gid:[el]}`と`sidToG={sid:gid}`を構築(`sentEls`構築と同じ場所、`app.js:112-113`の隣)。
- `highlight(sid)`(`app.js:223`): 先頭の`if (sid===activeSid) return`の後、EN`on`更新と同時に旧グループの`.jhl.on`を外し新グループへ付与(`sid`→`sidToG[sid]`)。`highlight(null)`・setLevel(`activeSid=null`+render再構築)・「文と文の間=null」でJAも消灯。`tick()`/click/seek/自動進行はすべて既存のまま`highlight`へ集約されるため**追加の呼出点なし**=既存の再生・一時停止・再開・連続再生・停止ボタンに無影響。
- 色・形: `style.css`に`.jhl{border-radius:4px;transition:background .12s}`/`.jhl.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}`のみ(`.sent.on`と同一変数=色統一、デザイン変更なし)。JA側の自動スクロールはしない(EN追従スクロールを維持。JAがモバイルで画面外のときは点灯のみ=許容。実測で確認しリスクとして報告)。
- 日本語クリックでのジャンプは**実装しない**(原文は英語クリック→日本語連動のみ。追加仕様を避ける)。
- モバイル/PC: 追加要素はinline spanのみ・幅/高さ不変。横スクロールなし(verify B)を維持。

## D4. 取込み経路(Family差分)
- 変更は`er135_enduser_page_01.py`の`build_enduser`(attach_translations直後に`align`呼出)と新`er135_enduser_align_01.py`、schema/validate/verify_consistency、`er135_enduser_page_verify_01.py`、assetのみ。**hook(X/Y/Z)は不変**(3経路とも`eu.hook_run`、CURRENT_STATE_01 §6)。X=承認済み日本語原稿、Y=devページの日本語の元原稿は既に`ja`として取り込み済みで追加入力なし。Zは`ja`無し→`ja_align`なし(N/A、D0-1)。
- retry/regeneration/resume: 対応づけは**最終のarticle.json(EN文+JA)の純関数**で、pages/page_verifyのたびに再計算(埋め込みはsha256キャッシュ)。LR/Fallback/regenerationでEN文が変われば自動的に再対応。`build_info.ja_align.sha256`=(EN文列+JA文字列)のhashで`verify_consistency`が陳腐化を検出(旧alignが新本文に残る事故を防止)。resumeはキャッシュ再利用でAPI 0。Gate/retry/fallbackは触らない。
- verify_consistencyは`build_info.asset_build`でasset dirを解決する(旧rev01-e dirも検証可能=既公開物の再現性を保つ)ように最小変更。

## D5. 検査追加(Playwright。`er135_enduser_page_verify_01.py`の新カテゴリJ)
J1 `.jhl`数==ja_align非nullグループ数・data-jgがdataと一致 / J2 `.tr`のtextContent==`ja`原文(不変) / J3 英語文クリック→その文がon、**mapped JA群のみon・他JAは非on**(null群は無点灯) / J4 自動進行サンプリング(F既存のn個)でEN onとJA onが常にdata通り / J5 シーク(#seek 50%・±10秒)後の同期 / J6 レベル切替・停止後の全消灯 / J7 既存F・G・H・Iが全PASS(回帰) / J8 console error 0・4xx 0 / PC・モバイルで`.jhl.on`が可視(色一致: computed backgroundが`.sent.on`と同値)、横スクロールなし。unit test(API 0): 文分割・DP・採否・不変条件・schema拒否・旧データ互換(`ja_align`無しで従来出力)・asset diff・実データ回帰(ゴールド固定)。

## D6. 既存記事・新規記事
- 既存(enduser有り5dir): 公開dir上のdev HTMLから`produce --dev-dir <公開dir> --cache-dir <run>/enduser_sync_cache`を再実行(ASR API 0・埋め込み約¥0.3/記事)。X月・Y再配達・Y姓=連動有り、Zメロス/藪の中=ja無しのためrev01-fへ更新のみ(連動N/A)。
- 新規: 以降のX/Y/Z新記事はpages段のhookで自動的にrev01-fで生成。X 4記事は音声完了後のpagesで自動適用(別Worker進行、完了後に1件実測)。雪女(Z)は連動N/A。
- 公開反映: publish-copy手順(PM_GOVERNANCE 9-8近傍/1772行)で`enduser/`のみ差替え、live検証。

## D7. runtime evidence計画(委任_02)
正式runner hookをコピーrun上で発火(EUP03前例): X月reselect / Y再配達 / Y姓(連動あり、Std+Adv)、Zメロス(N/A確認)、+X新記事1件(音声完了後)。各: ゴールド精度、Playwright J1-J8(PC+モバイル)、ローカル+live、スクリーンショット。End User確認URL=公開`…/<dir>/enduser/index.html`(X月/Y再配達/Y姓)。

## D8. Opus条件A向け論点
1. 文対応アルゴリズムの安全側設計: 採否基準(cos・余裕・数字・段落全体不成立→全null)が誤ハイライト0を担保するか。埋め込みで十分か、LLM検証の追加が要るか。
2. 意味検証にAPIを使う妥当性(決定論のみで誤対応を実測した事実との比較)と失敗時degradeの是非(STOP/degrade)。
3. 既公開物の再現性: rev01-f新設+旧rev01-e残置+verifyのasset解決変更の安全性。再produceによる既公開5dirの差替え(API 0)の影響。
4. Family差分: Z/非story部が連動N/Aである扱い(D0-1)と、ユーザーの「全Family」要件との整合。
5. データ契約: オフセット方式(訳不変)の堅牢性(JA文字列の正規化・サロゲート・改行)、`ja_align`の後方互換。
6. 検査の網羅(J1-J8)。
