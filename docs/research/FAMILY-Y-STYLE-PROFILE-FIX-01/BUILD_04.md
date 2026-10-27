# BUILD_04 — 完成版組立・公開(委任_06)
## 1. 起動表(環境`TTS_EXECUTION_MODE=STANDARD`、API 0)
| 起動 | JST | 引数 | rc | 結果 |
|---|---|---|---|---|
| STOP確認 | 09:0x | `stop_scope_check_01.py`(`run/audit/stop_scope_check_06.json`) | 0 | 非停止 |
| 起動A | 09:05 | `--stages provision_shell,gate,assemble,pages,page_verify` | 2 | 引数検証で拒否(`provision_shell`はZ runner専用、Y runnerのstage名に無い)。プロセス未起動(run_launch_logにLAUNCH無し)・副作用0 |
| 起動B | 09:05 | `--stages gate,assemble,pages,page_verify --approved-budget-jpy 41`(他は委任_04 L5と同一) | 0 | gate/assemble/pages/page_verify完走、`spent_jpy` 32.0908不変 |
委任文の`provision_shell`指定はY runnerに存在せず(Z完成段の規則の過剰適用)。起動は実質1回(RESTART_STORM・5分3回なし)。
## 2. 公開物の構成(`user_test/family_y_production_redelivery_fee_03/`)
- `index.html` = 通常の最終試聴ページ(runner `pages/index.html` + 末尾に制作情報節[`tools/build_page_04.py`])。Std/Adv各「通し再生」(`audio/std_full.mp3` / `adv_full.mp3`)、パート別再生(Std 26 / Adv 24)、日本語元原稿、Vocabulary & Expressions / Grammar等の学習内容、制作情報(Voice表・Style `fx_20261017`・model_id)。旧Style比較・Voice別S9・Take比較の節なし。
- 先行版を退避: 旧`index.html`→`preview_segments_01.html`(参照audioは`audio/`→`preview_audio_01/`へ`git mv`+パス置換)。`hr_preview_01.html`・`std_hr/`・`std_ok/`・`compare_old/`は残置。`_02`は不変。
- 新`index.html`のsrc 52件はすべて存在。`evaluate_page_verify` = 違反0(`_03`上で再実行)。
## 3. 確認事項
- 確定内容保護G1: gate/assemble/pages/page_verifyでlegacy WARN・STOPなし(console_launch8.logにWARN文字列なし、page_verify `kp_selection_verified.legacy=false`)。`EIGO_KP_CONFIRMED_PROTECTION`は触っていない。
- HR Lock整合: preview=RESOLVED/HUMAN_APPROVED、y_voice_1=RESOLVED/OK。
