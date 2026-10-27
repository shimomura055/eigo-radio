# VERIFY_05 — `_03` 表示修正の検証(委任_07、API 0・JPY0)
修正tool: `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_05.py`(`_03/index.html`と`preview_segments_01.html`への後処理。冪等)。
生成元の区別: `_03/index.html`はrunnerのpages stage(Production builder `er121_family_y_audio_01.py`)出力を`tools/build_page_04.py`が複製+制作情報節追記したもの。Production builderは編集していない(委任_08)。本修正は出力済みの静的ページへの表示追従のみ。

## 変更内容
1. Voice説明文: `y-ai-notice`(上部)と制作情報節の2か所を承認文言へ。`preview_segments_01.html`の同notice1か所も同文言へ。
2. 実測ポーズ表示 `&#9208;N.NNs@m:ss.s` を19個撤去(本文18+凡例の見本1)。`_03`の実Chunk分割境界は0件(a2/b1b全8 segment chunked=false、`chunk_tts_decision.json`)なので`⏸`は置かない。
3. 凡例noteの『実測停止』『▼』説明を1行「⏸=実際のTTS Chunk分割境界(開発確認用表示)。今回の記事にChunk分割境界はなく、表示はありません。」へ。

## 検証結果
| 項目 | 結果 |
|---|---|
| index.html: `&#9208;`/`⏸`残存 | 0/0(修正後) |
| 旧文言残存(`参考に、AIが編集・構成`/`ではなく、AIが編集した意見`) | 0(index/preview両方) |
| 承認文言の出現 | index.html 2、preview_segments_01.html 1 |
| 本文・KP・学習内容のdiff | 許容領域(上部notice・凡例note・ポーズspan・制作情報のVoice文)を除去して比較: **一致**(`$TEMP/v.py`、元41768字→38759字) |
| 音声sha(不変) | std_full.mp3 `7c037f49…8a268c`、adv_full.mp3 `f2c7d26f…cb5fc` 修正前後同一。`git status`でaudio/配下の変更0 |
| 冪等 | 2回目実行で変更0 |
| index.html sha | 修正前 `4b67a0b50a56aaa64421bcc5d391938d0b95d9ac39e28dbe4dcac74d9b8d06c2` → 修正後 `e69dd7c8c8251186fdbb3d0510b6cc72c3b81254a0096034ac833c09a0e93c2d` |
| 公開HTTP 200 | push後に確認(RESULT_PACKET参照) |

制約: 本ページは静的修正のため、Production builderが今後`pages` stageを再実行すると旧表示が再生成される(委任_08で是正するまで)。`_03`の再生成は不要・禁止(承認済み音声)。
