# FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01 実行ログ (2026-10-12、実行層Sonnet)

## 結論
Production初回経路への配線(Comment4新Prompt、profile `coffee_final_v5`=P8+R2+P3、`--only-segments`)とStdのR2実TTS・Std v5組立までは完了。**Advanced KP英英解説P3の実TTSが5件中3件で中断(実行層が付けたshell timeout 540秒でrunnerが終了)。委任文が再起動を許可していないため再起動せず停止**。Adv組立・試聴ページ・Playwright evidence・最終Gateは未実施。`PRODUCTION_WIRED`は未達。

## 時系列(要点)
1. STOP_NOTICE確認: Melos用のみ(別案件)。Coffeeに停止指示なし。PRECHECK_V5_01.md作成(v4/Production原稿は別原稿=OPEN-326、IOL spec不一致=OPEN-299は変更なしのため続行)。
2. 実装: `er019_family_x_audio_plan_01.py`(Comment4 +2文)、`er019_family_x_style_profile_01.py`(profile拡張)、runner(R2/P3解決・記録・`--only-segments`)。test 49件OK。
3. v4原稿のsource_dir/out_dir用意(Tone sourceを`run_v5_ms_01`へ明示コピー、sha一致、scaffold明示コピー)。Comment4のみProduction Prompt定数で1 call再生成(gpt-6-luna)。dry-run planでstyle_profile.json作成。Adv KP解説text bundle(v4原稿)をM2後に事前配置(M2回避に近い手順として明示)。
4. Std tts(起動1回、rc=0、約11分): Preview/Comment1〜4をR2で生成、全attempt R2 sha一致、comment_1のみ1回ASR不合格→再生成。費用 約JPY2.5。
5. Adv tts(起動1回): kp1〜3生成後、`timeout 540`が約9分で終了(rc=124)。kp4生成中。results JSONは最後に書かれる設計のため結果record無し。**実行層の誤り**: BATCH方式でclip1件約2.5分かかるため5件で約13分必要なのに540秒timeoutを付けた。再起動はしていない。
6. 中断後の無料作業: Std v5組立(316.603s)・QA・異音検知(medium/high 0)、evidence集計、SSOT記録。

## Fableへの再開提案(いずれも未実施)
- 推奨: Adv tts段を**1回だけ**再起動(5件全て、`--only-segments kp1_explanation,kp2_explanation,kp3_explanation,kp4_explanation,kp5_explanation`、バックグラウンド実行・timeoutなし)。kp1〜3は結果recordが無いため再生成(重複費用約JPY0.9)。想定費用 約JPY1.5、所要約13分。
- その後: Adv組立→QA→異音→WPM→試聴ページ(v5)→push→Playwright→最終報告(スクリプトは用意済み: `er057_coffee_final_v5_build_01.py`、`_anomaly_01.py`、`_known_anomaly_01.py`、`_wpm_01.py`、`_page_01.py`、`_play_verify_01.py`)。
