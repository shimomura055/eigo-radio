# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 統合設計メモ(委任_03T、2026-10-30、API 0・未配線)

対象module=`er135_enduser_translate_01.py`(standalone、test=`er135_enduser_translate_test_01.py` 32件PASS)。`er135_enduser_page_01.py`/app.js/hookは本委任で未編集。統合は委任_02完了後の委任_03。

## 1. 公開I/F(確定)
`translate_part(part_id, sentences:[{sid,en[,para]}], *, level, family, cache_dir, llm=None, embed_fn=None) -> {"ja":{sid:ja|None}, "coverage":{sentences,translated,paragraphs,paragraphs_translated,ratio,complete}, "meta":{part_id,level,family,ja_source:"generated",model,prompt_sha256,generated_at,cache_hits,api_calls:{translate,verify},cost_jpy,failures:[{paragraph,sids,reason}]}}`
- fail-closed粒度=段落(`para`が連続する文の塊)。失敗段落の全文は`None`(呼出側は英語のみ表示、`.jhl`は作らない)。
- 流れ: キャッシュ命中判定(保存訳も決定論検査を再実施)→未命中段落を文脈付き1 call→件数/ID/重複検査→構造Gate(`check_ja`+結合疑い)+数値決定論→NG段落のみretry1回→対訳照合(LLM 1 call/part、応答不正は1回retry→全段落null)→成功分のみ`ja_generated.json`保存。translate最大2 call+verify最大2 call/part。

## 2. 組み込み差分(`er135_enduser_page_01.py`)
| 項目 | 差分 |
|---|---|
| 呼出点 | `build_enduser()`内、`attach_translations`(:628)直後・委任_02の`align`呼出の前。入力=訳が無いpart(下記対象判定)の`sentences`(EN文ID=既存`sid`、段落=`paragraphs`の区切り→`para`)。`cache_dir`=**公開dirの`enduser/`直下**(`ja_generated.json`が公開物に同梱され再build・resume・live再produceで再利用=M5)。hookは不変。 |
| 対象判定 | 生成対象=Z story(Std/Adv)/Adv Preview・Comment・In One Line(X/Y/Z、存在するパートのみ)/Std In One Line(X)。除外=承認済みJA有り(X/Y story)・Std日本語のPreview/Comment(M7: 英語を新設しない・N/A)。 |
| article.json | 該当`parts[]`に`ja`(段落配列。ENと同数の段落、各段落=文の訳を連結)、`ja_source:"generated"`、`ja_align`(文ID↔`[paraIdx,start,end]`、生成訳の文長から確定)。`R.JA_SOURCES`(:914,:1029,:1324)と`_S`スキーマのenumへ`generated`を**追加**(承認済み2値+generated)。失敗段落は`ja`から外し(部分`ja`は作らない)、partに`ja_partial:true`相当は設けずbuild_info側に計上。 |
| build_info | `translation_coverage.<part種別>={blocks,translated,source}`に`source:"generated"`。新規`generated_translation={model,prompt_sha256,api_calls,cost_jpy,coverage_by_part,failures[]}`。**カバー率<100%の記事はbuild_info.warningsとOPEN計上**し、完了判定から外す(M4)。 |
| verify追加(`verify_consistency` :1209) | (a)訳の陳腐化=各`parts[].ja_source=="generated"`のENをsha→`ja_generated.json`の鍵と照合、不一致=stale NG (b)カバー率=ratio<1.0は報告(NGではなく完了不可フラグ) (c)生成訳の表示=`ja_source=generated`のpartで`.tr`が出ること、失敗段落は`.tr`/`.jhl`が0であること (d)Std日本語onlyのpart(Preview/Comment)で`.jhl`0、英語が新設されていないこと (e)`ja_generated.json`のschema/sha整合。 |
| Std Preview/Comment N/A | articleに`ja`を付けず`link:"na_ja_only"`は設けない(表示変更0)。verifyのN/A件数のみbuild_infoに記録。 |
| trHtml | 受け渡し変更なし(`app.js:83/85/88`は`p.ja`を既に読む)。`ja_align`供給のみ(委任_02のasset rev01-f)。 |
| routing | `ENDUSER_JA_TRANSLATE`/`ENDUSER_JA_VERIFY`を`er006_model_routing_contract_01.py`へ追加済み(SUPPORT_MODEL=gpt-6-luna)。 |

## 3. 再produce対象
X月reselect/Y再配達_03/Y姓_01/Zメロスr3/Z藪の中_01(`produce --dev-dir <公開dir>`、ASR 0)→ X4新記事・雪女(pages段hookで自動適用、雪女は音声完了後)。初回導入時にFableがZ story各1レベルの訳を抜き取り確認(M6)。

## 4. 費用見込み(実測前の推定)
翻訳+照合 ≈¥1〜2/記事(Z storyは約120文/2レベル、1 call/part+照合1 call/part)。キャッシュ命中時API 0。70円/記事セット比 ≦約3%。

## 5. 既知の保守側挙動(実Z fixtureで委任_03にて較正)
- 数値の「JA側余剰」も不一致扱い(漢数字「三日月」等の数詞でない語もNGになり得る)→段落null(fail-closed側)。実測で誤NGが多ければ余剰側の判定を緩める案を委任_03で検討(緩和は品質基準変更ではなく検査の精緻化)。
- 英文3語以下の台詞は`check_ja`の最小長4字/かな必須を緩和(「走れ!」を通すため)。
- 埋め込みcosは任意補助(`embed_fn`注入時のみ、既定OFF)。要否は実Z較正後に判断。
