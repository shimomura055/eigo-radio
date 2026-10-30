# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A 統合メモ(2026-10-30。INTEGRATION_03_01.mdの実装結果と03Bへの申し送り)

## 1. 実装した統合(コード+mock試験。実生成は未実行=API 0)
- `er135_enduser_page_01.py`: `generate_missing_translations`(訳が無い英語partだけを文ID単位で生成→`ja`/`ja_source=generated`/`ja_align`[1文=1群・how=gen])、`make_translator(cache_dir, llm)`、`translation_coverage_of`、`build_link_targets`(build_info.link_targets=Family x level x partの訳の状態・連動数)、`build_enduser(..., translate_llm=None, translate_cache_dir=None)`、`build_enduser_data(..., translate_fn=None)`。`verify_consistency`に生成訳の陳腐化(EN/JAのsha)・link_targets再計算の検査を追加。schemaに`how`・`ja_source=generated`・`link_targets`・`generated_translation`・cost(`translate_*`)。
- `er135_enduser_translate_01.py`: `build_ja_fields`(翻訳結果→段落配列のja+UTF-16オフセットのja_align。1文でも欠ければNone=部分jaを作らない)。
- `er135_enduser_align_01.py`: 生成訳partは再整列せず(埋め込み0)、`check_generated_part`(1文=1群・訳の末尾まで隙間なく覆う)で改竄/陳腐化を検出。
- `er135_enduser_page_verify_01.py`: story以外(Preview/Comment/In One Line)で訳が生成された部分もクリック点灯を検査(J3b)。

## 2. 既定で生成が走らない理由(flagではない)
生成は「`translate_llm`(llm callable)が渡されたときだけ」実行する。`build_enduser`の既定は`None`、`hook_run`/`produce_enduser`は渡さない(test: `test_build_enduser_and_hook_do_not_enable_generation_by_default`)。`make_translator`はllm無しをValueError(translate_partの既定`DefaultLLM`=実APIへ黙って落ちない)。つまり正式経路(X/Y/Z hook)は03A時点で出力不変(diff Gate OK)で、`訳が無い部分だけ生成する`設計そのものは変えていない。03Bで`hook_run`が`translate_llm=DefaultLLM()`を渡す1箇所を足せば、全Family・全Levelで『訳が無いpartだけ』生成される(承認済みのX/Y storyは再生成0)。

## 3. 03Bの前提(asset更新)
現行asset rev01-fは**Previewカードに日本語訳を描画しない**(`app.js:81` `card('Preview', ...)`が`trHtml(p)`を呼ばない。Comment=`:100`、In One Line=`:105`、Story=`:102`は呼ぶ)。Adv Preview訳を表示するには asset rev01-g=derive EDIT **J26**(`out += card('Preview', ja ? ... : sentHtml(p), {...})` を `(ja ? ... : sentHtml(p)) + trHtml(p)` へ。訳が無いPreviewは空文字=表示不変)が要る。assetを更新すると全End Userページ(公開済み+制作中の⑨⑭を含む)が`ENDUSER_ASSET_MISMATCH`でstaleになり再produceが必要なため、03Aでは更新せず(他Worker稼働中の⑨⑭に波及させない)、`R.ASSET_TRANSLATION_KINDS`で現行assetが描画できる種別(story/comment/oneline)に生成を限定した(Previewは03Bでasset更新と同時に`GENERATE_KINDS`へ追加。test `test_preview_is_not_generated_until_the_asset_can_render_it`)。
03B作業: (1)derive EDIT J26追加+ASSET_BUILD_ID=rev01-g+`ASSET_TRANSLATION_KINDS`追加 (2)`hook_run`へ`translate_llm`受け渡し (3)全公開dirと制作中⑨⑭を再produce(実LLM: 1 call/part+照合1 call/part、見込み記事あたり¥1〜2) (4)Zストーリー各1レベルの抜取確認(M6)・実LLM較正(数値『余剰側』判定、短台詞緩和)。

## 4. 点灯率の改善(整列アルゴリズム、method=`tiered_dp_embed_v2`)
- 構造確定(how=det): EN1文またはJA1文の段落は段落全体を1群にし、**埋め込みを呼ばない**(数字・固有名・文字数比[1.2〜6.0]の安全検査に通ったときのみ。不通過は埋め込み経路)。
- 順序対応(how=order): EN文数==JA文数でDP経路が全て1:1のとき順序対応を既定とし、埋め込みは『明確な矛盾の検出』(cos<0.30、または同行/同列の他候補に0.03以上負ける)にだけ使う。
- DP周辺確率(how=soft): 従来の境界ずらし検査で棄却された群のうち、全経路の周辺確率(温度0.20)が0.95以上のものを追加採用(cos・数字・固有名・段落整合は従来どおり必須)。
- M8(LLM判定)は本委任では実装しない(Fable指示: 呼出は03Bで判断。コードも未実装。Std残り取りこぼしの主因は『文数不一致+境界ずらし余裕不足』で、埋め込みだけでは曖昧な群)。
- 撤去した旧規則: `PARAMS.eq_delta_ja/eq_delta_en`(文数一致modeの隣接ずらし余裕。上記orderの`eq_margin`へ置換)。
