# EVIDENCE_01(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_03 WP-E/F、2026-10-29、API 0)

原データ=同dir `evidence_03/`(`formal_logs/`発火ログ・`run_results/`hook要約+ブラウザ結果・`wpe_evidence.json`再実行/stale/整合・`sync_gate_summary.json`同期gate・`live/`live検証json・`shots/`スクショ)。
**API呼出 0**(全工程ローカル。同期=faster-whisper medium int8 CPU。TTS/本文/解説の再生成 0。有料runなし)。stop_scope_check(`END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01`、各run-dir)rc=0。

## 0. 構成(正式経路hookと、公開済みdirへの後付け)
- hook: X=`er019_family_x_listening_page_01.py` `main`→`build_enduser_after_page`(rc=5=ENDUSER_*) / Y=`er121_family_y_runner_01.py` `stage_page_verify`(既存検査すべて通過後・`write_final_manifest`前、manifestに`enduser`のfile sha) / Z=`er026_family_z_fiction_production_runner_01.py` `stage_page_verify`末尾。共通入口=`er135_enduser_page_01.hook_run`(`produce_enduser`→`verify_consistency`→Playwright検証[PC1280+モバイル模擬390x844])。新stage名なし。
- **mock/dry-runはskip記録(偽TTS音声に発話がなくASR同期不成立)。real(正式Production)は必ず生成**(env/flag/引数でのskip不可。test固定)。
- 公開済みdirの後付け(backfill)=同じmoduleのCLI `produce --dev-dir <公開dir>`。理由=公開済みのdev index.htmlは公開後に手編集されており(X月=状態注記を正式公開へ差替え/Y=Voice説明文・制作情報リンク・候補版注記/Z=古いPart 2版)、現行builderの再実行結果と一致しない。End User pageは**公開dirのdev HTMLのsha**と整合(`ENDUSER_STALE_DEV_CHANGED`)するため、公開dev HTMLを入力にしてdev index.html・音声を1バイトも変えず`enduser/`だけ追加した。
- 正式runが現行コードで再実行できないdata state(下記§5)のため、**formal hook発火に使ったrunは公開記事と同一音声の別run**: X=月reselect(同一run)、Y fee=`run_gpg5_y_01`(音声52/52がfee_03公開と同sha)、Y姓=`run_02`(同一)、Z=`run_gpg5_z_01`(音声93/93がr3公開と同sha)。ASRキャッシュ(mp3 sha256)は共有できる。

## 1. 正式Production経路の発火証拠(Family別・レベル別)
| Family/記事 | 起動(formal_logs) | rc | 同期gate | tok一致(総/行min/行median) | rows・文 | low_conf行 | episode offset(最大lag/最小相関) | 全編長-timeline差 | KP英語窓(行/最小tok) | 訳 | glossary | hook所要 | browser(local) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X 月 Std | `er019_family_x_listening_page_01.py --slug moon_shrinking --run-name run_reselect_01 --web <scratch>`(`x_formal_stdout*.log`) | 0 | PASS | 0.980/0.882(std_02 17tok)/0.974 | 11・63 | 2 | 0.000s/0.9886 | 0.030s | 2/1.0 | story 3/3 承認済み日本語原稿(revision2.md) | applied | cold 205s(ASR 13 call、並列負荷下) | 168 NG 0 |
| X 月 Adv | 同上 | 0 | PASS | 0.992/0.947/0.997 | 10・49 | 1 | 0.000s/0.9885 | 0.030s | 3/1.0 | story 3/3 | applied | cold 362s | 同上 |
| Y 再配達料 Std | `er121_family_y_runner_01.py --run run_gpg5_y_01 --stages pages,page_verify`(`y_fee_formal_stdout4.log`) | 0 | PASS | 0.980/0.857(std_02 7tok)/0.982 | 14・60 | 3 | 0.000s/0.9898 | 0.038s | 3/1.0 | story 8/8(`approved_ja_original_in_dev_page`) | 対象外(display_spec無し) | 11.6s(dropout窓1+cache17) | 162 NG 0 |
| Y 再配達料 Adv | 同上 | 0 | PASS | 0.987/0.857(adv_02 7tok)/1.000 | 12・43 | 0 | 0.000s/0.9894 | 0.050s | 3/1.0 | story 8/8 | 対象外 | 187s(ASR 15 call) | 同上 |
| Y 姓 Std | `er121_family_y_runner_01.py --run run_02 --stages pages,page_verify`(`y_sn_formal_stdout5.log`) | 0 | PASS | 0.980/0.929/0.993 | 14・63 | 0 | 0.000s/0.9892 | 0.045s | 3/1.0 | story 8/8 | applied(level一覧poolを使用) | warm 0.9s | 170 NG 0 |
| Y 姓 Adv | 同上 | 0 | PASS | 0.992/0.972/1.000 | 12・49 | 0 | 0.000s/0.9899 | 0.040s | 3/1.0 | story 8/8 | applied | warm 0.7s | 同上 |
| Z 走れメロス Std | `er026_family_z_fiction_production_runner_01.py --run run_gpg5_z_01 --stages pages,page_verify --pages-dir <run>/pages_evidence`(`z_formal_stdout4.log`) | 0 | PASS | 0.987/0.939/0.985 | 9・62 | 0 | 0.000s/0.9964 | 0.045s | 5/1.0 | 承認済み訳なし=非表示(0/3) | 対象外 | warm 1.0s | 162 NG 0 |
| Z 走れメロス Adv | 同上 | 0 | PASS | 0.988/0.969/1.000 | 8・70 | 1 | 0.000s/0.9974 | 0.029s | 3/1.0 | 0/3 非表示 | 対象外 | warm 0.7s | 同上 |
- 閾値は02A確定値のまま緩和なし(行=一致率>=0.90 または短行[en<=20/ja<=30tok]で不一致<=2[ja3]かつ>=0.75、全補間文STOP、KP>=0.80/blocks>=4)。行0.90未満は短行3行のみ(X std_02 17tok・Y std_02/adv_02 7tok、内容は正常)。zero_match長文 0。
- 設計§6-2(4)episode_offset(1秒窓相互相関ずれ<=0.05s)・(5)全編音声長とrunのtimeline終端の差<=0.15sを本委任で実装(`episode_checks`)。**全6 level×4記事でlag 0.000s、相関>=0.9885、長さ差<=0.05s**。相関下限は実測(最小0.9885)から0.97(別音声検出用の健全性チェック。設計値でなく本委任の実装値)。
- 所要(cold): 他の3 ASRと並列(CPU 16core共有)の負荷下でXのASR 567s・Y fee adv 187s・Z cold launch 11m。**非並列の基準値(02A Phase-0)=約6.5分/セット**。warm(キャッシュ)=sync 約1秒+build 約5秒+browser検証 約90秒。

## 2. DEV仮データ・未承認データの分離(validator・静的test)
- `validate_output`・禁止語(`placeholder_for_layout_check`/`dev_translation_unapproved`/`DEV訳`/`未承認`/`[DEV]`/`phnote`/`⏸`/`rpt-`/`Traceback`/`confirmation_id`等)・schema(additionalProperties=false)・asset sha(DEV rev01-eからの許可リスト差分のみ)を4ページすべて通過(生成時・`verify_consistency`)。
- 訳: X Full Story=承認済み`ja_writer/revision2.md`の段落のみ、Y=dev page内の承認済み日本語原稿(`split_y_article`と一致検査)のみ、Z・各Comment/Preview/Topic/In One Line=承認済み訳なし=**非表示**(DEVの未承認11ブロックは持ち込まない。`build_info.translation_coverage`に種別ごとの{blocks,translated,source}を記録)。
- 文法・ニュアンス: dev HTMLの`section.study`をそのまま継承(0件/不採用は節ごと非表示、空枠0)。DEVのAI島流用仮データは不使用。

## 3. retry / resume / regeneration / stale(`wpe_evidence.json`、4記事)
| 記事 | pages(hook)再実行のASR | 再実行所要 | 再実行後に変化したfile | dev index.html | verify_consistency | dev変更を模した複製 |
|---|---|---|---|---|---|---|
| X月 | 0回(std/adv) | 6.1s | `enduser/build_info.json`のみ(cost秒数) | 不変 | ok | `ENDUSER_STALE_DEV_CHANGED` |
| Y fee03 | 0回 | 5.8s | 同上 | 不変 | ok | 同上 |
| Y姓 | 0回 | 5.7s | 同上 | 不変 | ok | 同上 |
| Zメロス | 0回 | 5.0s | 同上 | 不変 | ok | 同上 |
- 本文/audio/sync/asset=バイト同一(article.json・sync_*.json・app.js・style.css・index.html)。差分は`build_info.json`の`cost`の経過秒だけ。
- Local Rewrite/Fallback/TTS再生成でsegment mp3が変わる場合は、`pages`再実行で当該segmentだけ再ASR(sha256キー)。変わらなければ0。End User生成のためにTTS・本文・解説を再生成することは構造上ない。
- `publish-copy`(Y公開手順補助): pages→公開dirで`enduser/`だけcopy+copy先でverify。公開dirのdev index.htmlがpagesと異なる場合は**copy前に不合格・公開dir不変**(姓公開dirで実測=`copied:false`、既存enduser/保持)。copy後検査NGは元のenduser/へ戻す(test)。
- 失敗終了時: `ENDUSER_*`でSTOP、dev index.html・既存`enduser/`は不変(X rc=5・Y/Z StopのメッセージがENDUSER_*。testで固定)。

## 4. live検証(GitHub Pages、キャッシュ無効クエリ、commit 1b4b41afb push後)
| ページ | 開発者向けURL | End User向けURL | 検証(PC1280+モバイル模擬390x844、`verify-only --base-url`) |
|---|---|---|---|
| X月 | https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/enduser/index.html | 168チェック NG 0 |
| Y再配達料 | https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/enduser/index.html | 162 NG 0 |
| Y姓 | https://shimomura055.github.io/eigo-radio/user_test/family_y_production_surname_choice_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_y_production_surname_choice_01/enduser/index.html | 170 NG 0 |
| Zメロス | https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_kphr_evidence_r3/index.html | https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_kphr_evidence_r3/enduser/index.html | 162 NG 0 |
- 検査内容: console error 0・HTTP 4xx/5xx 0・音声参照200/206・文ハイライト追従・文クリック再生・シーク後追従・パート間連続再生・停止/再開・KP英語のみ区間・太字(引用英文)・0件コーナー非表示・Voice説明文(Y)・訳ブロック==承認済みデータ・glossaryリンク。live上のfile(dev index.html/enduser 8file)はローカルとバイト一致(8/8×4)。開発者向けページは`check_file`標準適合PASS×4、`git diff`で`user_test`の非enduser file変更0(dev index.html・音声は1バイトも変えていない)。
- **模擬と実機の区別: 上記は全てPlaywright Chromium(モバイルemulation)=模擬。実機iOS Safari/Android Chromeは未実施(実機検証済みとは扱わない)**。スクショ=`evidence_03/shots/`。

## 5. 本委任で見つけて是正した不具合(承認済み仕様内・API 0)
1. **ASR dropout**: Y再配達料Std Voice1(std_18, 40秒)でWhisperが発話済みの10語/4.2秒(25.76〜29.98s)を丸ごと欠落(窓ASRで語が存在すると確認)。行token一致0.883でgateがSTOP。→ sync moduleに「ASR語間の2秒超かつ無音でない(>=1.0s)区間を、同モデル同設定の窓として再ASR(キャッシュ)して統合」を追加(11語回復→一致0.98)。**閾値は不変**。回復できない欠落は従来どおりSTOP(test)。発動は4記事中この1行のみ。
2. **level節直後の③本文中の意味一覧**(Y等): 行内でなくlevel末にある`ul.lk-meaning`を共有poolとして下線に1回だけ対応づける(未使用が残ればSTOP)。人称/語形差(let my son go↔let one's son go等)は語幹列比で吸収。
3. **Zのdevページ**はIntro/Notification/Outro行を持たない→全編長の照合を行ではなくrunの完全なtimelineで行う。
4. 相対pathのpages_dirで音声pathが二重結合(`ENDUSER_SYNC_AUDIO_MISSING`)→絶対path化。
5. 検証script: 長いページでglossaryリンクのsmooth scrollが700msで終わらずNGになる計測の揺れ→スクロール静止まで待ってから判定(NG→0)。
6. **既存run dataの陳腐化(End User hookとは無関係、現行コードの`verify_outputs`が検出)**: X月run・Y fee `run_gpg5_y_01`・Z `run_gpg5_z_01`のstudy_text/part2 markdownに古い終端`=====`(OPEN-591)が残り、`pages/page_verify`の四者一致がSTOPした。`er120_part2_wiring_01.write_md`(決定論render、API 0)でresultからmdを再描画して解消(3 run×最大2 level。内容はresultと同一・終端のみ)。
- 発火に使えなかったrun(参考): Y `run_01`=Style profile導入前でM2 STOP(新しいout_dirのみ可)、Y `run_style_fix_01`・Z `run_p2_evidence_r3`=Part 2 artifactなし(`--regenerate-stage`は有料API)。Zの正式1起動(`provision_shell,gate,assemble,pages,page_verify`)は**未実施**: gate/assembleは既存の確定音声(timeline・wav)を書き換え、gateのAPI 0をcopy-runで事前確認できなかったため(hookは`page_verify`stage自体に入っており、`pages,page_verify`起動で発火経路は同一)。

## 6. 量産単価増分
- API費用 **0円/セット**。追加はローカルCPUのみ: 初回 約6.5分/セット(faster-whisper medium、02A実測。並列負荷下では約10〜14分)、再実行はキャッシュで約6秒(+browser検証約90秒)。`build_info.cost`={api_calls:0,model,asr_wall_s,build_wall_s,cached_segments}。70円/記事セット目標への増分=0円。
- 追加の実費=0円(本委任のAPI支出なし、各runの`e2e_stage_log.jsonl`の`spent_jpy_cumulative`は起動前後で不変[Y fee 1.5892・Y姓 48.7534・Z 0.7532]、各run`cost_log.jsonl`は未更新[mtimeが本作業より前]、hook内にAPI呼出なし。日次1,000円枠に影響なし)。
