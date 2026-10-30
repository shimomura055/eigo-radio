# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 設計差分メモ(委任_03A、2026-10-30。実装は委任_03)

基準=DESIGN_01.md(委任_02が実装中: X/Y story、Opus M1〜M10)。根拠=FACT_CHECK_Z_AND_PARTS_01.md。コード変更0。

## 1. 要点(DESIGN_01からの差分)
1. 適用範囲: story(X/Y) → **story(X/Y/Z)+Comment+Preview+In One Line(X/Y/Z、Std/Adv、存在するパートのみ)**。D0-1(「Z・非storyは連動N/A」)は撤回。
2. 日本語が**既にあるもの**: X/Y story(承認済みJA原稿、段落/ブロック単位)のみ。Std Preview/CommentはStd用の独立した日本語文(英語対なし)=現行の文単位ハイライトで足りる(新規作業なし。英語は作らない)。
3. 日本語が**無いもの→新規生成**: Adv Preview/Comment/In One Line(X/Y/Z)、Std In One Line(X)、Z story(Std/Adv)。生成は**文ID付き**=ENとJAが構成上1:1 → **埋め込みAPI不要**(決定論)。
4. 埋め込みAPIが要るのは**X/Y storyの文数不一致段落のみ**(DESIGN_01 D2のまま。EN1×JA1・文数一致で安全検査通過の段落は決定論。原文§3.2「既存データで正確に分かる場合は埋め込みを使わない」に適合)。

## 2. データ構造(part別 ja_align、D1の拡張)
- `ja_align`をstory以外のpart(`preview`/`comment`/`oneline`)にも許可(同一schema、加法的変更)。生成訳の`ja`は**EN段落と同数の段落配列**(EN文を改行区切りでなく、文ID順に連結した1段落=1段落)、`ja_align`の`ja:[paraIdx,start,end]`は生成時に確定(文ごとの訳の長さから算出)=位置ずれなし。
- 由来表示: `ja_source`=`approved_ja_manuscript` / `approved_ja_original_in_dev_page`(既存) / **`generated_ja_translation`(新規。`trtag`は「日本語訳」のまま)**。build_infoの`translation_coverage`にparts別・source別件数と`generated`のmodel/prompt_sha/費用を追記。
- app.js: `trHtml`は既にcomment(`app.js:83`)/oneline(`:88`)/preview(`:85`)で呼ばれている → **表示側の追加は不要**。`highlight(sid)`と`sidToG`はpart横断で効くため、story以外へ拡張は`ja_align`データ供給のみ(asset変更はDESIGN_01のrev01-fのまま。追加変更なし)。Std Preview/Commentは日本語sentが唯一の言語=現行ハイライトのまま。
- verify追加: 全part種別×Family×Levelの`.jhl`数==非nullグループ数、Std日本語onlyのpartで`.jhl`が0であること(誤補完しない)、Y AdvのComment 2不在の扱い。

## 3. 新規モジュール `er135_enduser_translate_01.py`(End User build内、DEV/Trial経路ではない)
- 入力=最終article.jsonの未訳の英語part(文ID付き)。出力=`ja`と`ja_align`。呼出位置=`build_enduser`の`attach_translations`直後(委任_02の`align`呼出の前)。hook(X `er019:262`、Y `er121:1388`、Z `er026:2777`)は不変(3経路とも`eu.hook_run`)=正式Production初回経路・retry/regeneration/resume(pages/page_verify再実行)で自動適用。
- 翻訳Prompt/Gate: `er003_kp_source_sentence_ja_01.py`のPROMPT/`check_ja`(構造Gate)/技術retry1回→fail-closedを再利用(`_collect`等の流用は同moduleを直接import、複製しない)。model=SUPPORT_MODEL(gpt-6-luna、routingに処理名`ENDUSER_JA_TRANSLATE`を追加)。追加検査: 文数一致・数字集合一致・(推奨)EN↔JAの埋め込みcos下限(不通過=その文を非表示にせず再翻訳1回→なお不通過は当該partの訳を出さず`warning`、End Userページは英語のみで継続。STOPにしない=DESIGN_01の方針と同じ)。
- キャッシュ=`<run>/enduser_sync_cache/ja_<sha>.json`(キー=EN文+Prompt sha+model)。EN文が変わった文だけ再翻訳(LR/Fallback/regeneration/resume対応)。既存の承認済み日本語(X/Y story、Std日本語part)は**翻訳対象から除外**(再生成0)。
- 新規テスト: 翻訳対象判定(既存JAのあるpartは除外)/文ID↔訳1:1/Gate失敗系/cache hit時API 0/Y・X・Z fixture/Std日本語partが対象外であること。

## 4. 再produce対象と費用見込み
| 対象 | 内容 | 追加API |
|---|---|---|
| 公開済5dir(X月reselect、Y再配達_03、Y姓_01、Zメロスr3、Z藪の中_01) | 公開dir上のdev HTMLから`produce --dev-dir <公開dir> --cache-dir <run>/enduser_sync_cache`(ASR API 0) | X/Y: 埋め込み約¥0.25(story)+翻訳約¥0.1(Adv Preview/Comment/OneLine+Std OneLine)。Z: 翻訳約¥0.5〜1.0(story+Adv Preview/Comment) |
| X新4記事・雪女(制作中別Worker) | pages段のhookで自動適用(コード統合後)。雪女は組立段Style Gate BLOCK停止中のため音声完了後 | 同上 |
| 告げ口心臓(Z) | enduser未生成のため対象外(必要ならproduceで新規。ユーザー指示なし) | - |

追加量産原価の見込み: X/Y 約+¥0.35/記事、Z 約+¥0.6〜1.1/記事(70円/記事セット目標比 ≦約1.6%)。

## 5. 委任_03の作業分割・見積
| # | 作業 | 依存 | 並列 |
|---|---|---|---|
| 1 | 委任_02の成果(align module/rev01-f)統合確認 | 委任_02完了 | - |
| 2 | translateモジュール+routing+test | なし | 1と並列(先行可) |
| 3 | schema/validate/verify拡張(part別ja_align、Std日本語only) | 1 | 2と並列 |
| 4 | Playwright J系の全part×全Family拡張(PC+モバイル) | 1,2,3 | - |
| 5 | 5dir再produce+live反映+X新4記事の自動適用実測 | 2,3,4 | - |
| 6 | 回帰(retry/regeneration/resume、Y Adv Comment 2不在)・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN-618)・commit/push | 5 | - |
見積: 実装・test 1委任(大)+運用実測は音声完了待ち(X4/雪女)。Opus条件A: 委任_02のM1〜M10が整列アルゴリズム、本差分は**新規翻訳経路の追加(新しい処理フロー)**なので、条件Aの対象に含めるのが妥当(translateのGate設計・埋め込みcos下限の要否)。

## 6. 判断候補(分類)
- A(既判断): 埋め込みAPI使用(原文§3.2)/Adv Preview日本語訳の生成(§1,§4)/Z日本語訳の新規作成(§2末尾)/全Family×4パートへの拡大。
- B(承認範囲内で自己解決): Adv Comment・In One Lineの訳を新規生成しStd日本語を流用しない(原文§4「実際に不足している部分のみ補う」。ユーザーが見たComment 2はStd/Advの別文の並置だった事実を完了報告で明記)。Std日本語のPreview/Commentに英語を新設しない(原文は“存在するパートに適用”)。
- C(独立): 雪女・X4記事の制作・Style Gate。
- D(真に新しい判断): なし。ただし「翻訳の誤訳検知に埋め込みcos下限を追加するか」は新しい品質基準にはあたらない見込み(既存構造Gateの拡張)だが、Fable/Opus条件Aで要否確認を推奨。
