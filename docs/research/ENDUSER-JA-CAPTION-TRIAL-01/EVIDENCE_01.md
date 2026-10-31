# EVIDENCE_01 日本語キャプション Trial(2026-10-31、API 0・再生成0、ローカル実測+公開URL確認)

使用ブラウザ: Playwright Chromium(PC 1280幅 / スマホ390幅エミュレーション。実機iOS/Androidではない)。音声は既公開mp3(実再生)。

## 確認URL
Trial一覧: https://shimomura055.github.io/eigo-radio/user_test/enduser_caption_trial_01/index.html
X(Meta Waddle World)/Y(姓の選択)/Z(走れメロス): `.../enduser_caption_trial_01/{x,y,z}_{std,adv}/index.html`。現行(Production)は各ページ上部リンクまたは一覧から(`user_test/family_*/enduser/index.html?lv=`)。ON/OFFは`?caption=0|1`またはボタン。

## 既存チェック(er135_enduser_page_verify_01.py、Trial版app/style/indexを既公開dirの複製に重ねて実行)
X/Y/Z(std+adv, PC+mobile): TOTAL 270/268/250、NG 0(`verify_x|y|z.json`)。F `std/adv_sentence_click_does_not_play_or_seek` OK、J連動/G境界/K level_switch/console_errors_0/http_4xx_5xx_0 すべてOK。

## 観察(`shots/observe.json`、`shots/observe_extra.json`。6ページ×PC/スマホ)
- 英文クリック: 全文を順にクリックして再生開始/シークなし(`click_played_or_sought=false`、全12観察)。クリックで選択した文の対応日本語がキャプションに出る(例 X adv 45/49文、Y adv 48/49、Z adv 69/70、Std 34/54・51/63・53/62。残りはJA対応なし=空)。
- 再生中12秒サンプル(80ms間隔、約135点): キャプション文字列=本文側`.jhl.on`の文字列が全点一致(mismatch 0、全12観察)。文の切替回数は2〜8回で一回ずつ入れ替わり、ちらつき(同一文の点滅)なし。
- 一時停止: 内容維持。停止中シーク/±10秒/シークバー: mismatch 0(移動先の点灯文に追従、日本語なし区間は空)。
- KP再生・Vocabulary音声・「ここから再生」・再生中の英文クリック: mismatch 0、エラー0。KP/Vocab再生中はキャプション空(既存仕様で日本語は点灯しないため)。
- ON/OFF: ボタンでOFF時に枠が非表示、URLが`?caption=0`へ更新。現行リンクあり。
- 長文: 最長でもスマホで3行(約73px)に収まり`max-height`内(最長77字)。
- 固定バー高さ: PC約172px、スマホ約188px(ON時。OFF時は約112px)。画面高844pxのスマホで約22%。

## スクリーンショット
`shots/`: `{x_adv,y_std,z_adv}_{pc,mobile}_01_initial_stopped|02_click_selected|03_playing|04_no_ja_part|05_long_caption|06_paused|07_after_seek|08_kp_play|09_caption_off.png`。他3ページ(x_std,y_adv,z_std)は01〜05のみ。

## 良い点
- スマホで再生バーのすぐ下に対応日本語が常時見え、本文下方の訳へスクロールしなくても確認できる(主目的に合致)。
- 点灯ロジックを一切変更せず追加表示のみ。null・日本語なしは誤表示せず空。API 0・データ変更0。

## 気になる点(ユーザー判断材料)
- 固定バーが約60〜75px高くなり、スマホでは画面の約22%を占める(本文の可視領域が減る)。ON/OFFスイッチを正式版に付けるか、折りたたみ式にするかは採否時の論点。
- 本文側の日本語ハイライトとの二重表示になる(混乱は小さいと考えるが実機での体感はユーザー確認が必要)。
- 文が短く連続する箇所ではキャプションが数秒ごとに入れ替わる(読み切れない速度かは実聴での確認が必要)。
- エミュレーションでの確認のみ(実機iOS Safari/Androidは未確認)。
